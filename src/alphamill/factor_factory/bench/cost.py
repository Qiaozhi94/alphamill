"""三档成本、breakeven 与成本裁决（`FR-005`；任务 T007）。

三档成本（zero / maker / taker）由预注册 `cost_model` 持有，不得硬编码；`cost_model.id`
对外即 `cost_model_version`（design §3.1）。裁决档位默认取**最保守的 taker**：`taker` 档成本后
不为正即 `cost_negative`，对应 `dead` 结论（`FR-005` 场景「高 IC 但成本不存活」）。换手与持有期
一并输出（`AC-004`）；输入不足以计算时 `cost_undetermined`，绝不把缺失当零。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.factor_factory.bench.stage_model import (
    COST_NEGATIVE,
    COST_POSITIVE,
    COST_UNDETERMINED,
    STAGE_COST_CAPACITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_PASS,
    FailureRecord,
    StageModelError,
    StageResult,
)

COST_TIERS = ("zero", "maker", "taker")
DECIDING_TIER = "taker"
BPS = 1e-4
ERROR_CODE = "E_REQUIRED_METRIC_FAILED"


@dataclass(frozen=True)
class CostTier:
    name: str
    fee_bps: float
    slippage_bps: float

    def __post_init__(self) -> None:
        if self.name not in COST_TIERS:
            raise StageModelError(f"未登记的成本档位: {self.name!r}（合法: {list(COST_TIERS)}）")
        if self.fee_bps < 0 or self.slippage_bps < 0:
            raise StageModelError(f"成本参数不得为负: {self}")

    @property
    def total_bps(self) -> float:
        return self.fee_bps + self.slippage_bps

    def to_payload(self) -> dict[str, float]:
        return {"fee_bps": self.fee_bps, "slippage_bps": self.slippage_bps}


def load_cost_model(normalized: Mapping[str, Any]) -> dict[str, CostTier]:
    """从预注册 `cost_model.normalized` 装载三档成本；缺档或非法即拒绝。"""
    tiers = normalized.get("tiers")
    if not isinstance(tiers, Mapping):
        raise StageModelError("cost_model.normalized.tiers 必须是 object")
    missing = [name for name in COST_TIERS if name not in tiers]
    if missing:
        raise StageModelError(f"成本模型缺档位: {missing}")
    loaded: dict[str, CostTier] = {}
    for name in COST_TIERS:
        body = tiers[name]
        if not isinstance(body, Mapping):
            raise StageModelError(f"成本档位 {name} 必须是 object")
        loaded[name] = CostTier(
            name=name,
            fee_bps=float(body.get("fee_bps", 0.0)),
            slippage_bps=float(body.get("slippage_bps", 0.0)),
        )
    return loaded


def cost_drag(turnover: float, tier: CostTier) -> float:
    """成本拖累（收益分数口径）：换手 × 每单位成交成本。"""
    if turnover < 0:
        raise StageModelError(f"换手不得为负: {turnover!r}")
    return turnover * tier.total_bps * BPS


def net_return(gross_return: float, turnover: float, tier: CostTier) -> float:
    return gross_return - cost_drag(turnover, tier)


def breakeven_cost_bps(gross_return: float, turnover: float) -> float | None:
    """使净收益归零的每单位成交成本（bps）；无换手时不存在有限 breakeven。"""
    if turnover < 0:
        raise StageModelError(f"换手不得为负: {turnover!r}")
    if turnover == 0:
        return None
    if gross_return <= 0:
        return 0.0
    return (gross_return / turnover) / BPS


def turnover(notional_traded: float, capital: float) -> float:
    if capital <= 0:
        raise StageModelError(f"资金必须为正: {capital!r}")
    if notional_traded < 0:
        raise StageModelError(f"成交名义不得为负: {notional_traded!r}")
    return notional_traded / capital


def holding_period_hours(total_holding_hours: float, round_trips: int) -> float:
    if round_trips <= 0:
        raise StageModelError("持有期需要正的往返笔数")
    return total_holding_hours / round_trips


def cost_verdict(net_returns: Mapping[str, float], *, deciding_tier: str = DECIDING_TIER) -> str:
    if deciding_tier not in COST_TIERS:
        raise StageModelError(f"未登记的裁决档位: {deciding_tier!r}")
    value = net_returns.get(deciding_tier)
    if value is None:
        return COST_UNDETERMINED
    return COST_POSITIVE if value > 0 else COST_NEGATIVE


@dataclass(frozen=True)
class CostResult:
    gross_return: float
    turnover: float
    holding_period_hours: float
    round_trips: int
    net_returns: Mapping[str, float]
    breakeven_bps: float | None
    deciding_tier: str
    verdict: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "gross_return": self.gross_return,
            "turnover": self.turnover,
            "holding_period_hours": self.holding_period_hours,
            "round_trips": self.round_trips,
            "net_returns": dict(self.net_returns),
            "breakeven_bps": self.breakeven_bps,
            "deciding_tier": self.deciding_tier,
            "verdict": self.verdict,
        }


def evaluate_cost(
    *,
    gross_return: float,
    turnover_value: float,
    round_trips: int,
    holding_period_hours_value: float,
    cost_model: Mapping[str, CostTier],
    observed_at: str,
    deciding_tier: str = DECIDING_TIER,
) -> tuple[CostResult, StageResult]:
    """算三档净收益、breakeven 与成本裁决，并给出 `cost_capacity` 阶段状态。"""
    if round_trips < 0 or turnover_value < 0:
        return _incomplete(
            gross_return,
            turnover_value,
            holding_period_hours_value,
            round_trips,
            cost_model,
            observed_at,
            deciding_tier,
            reason="成本输入为负值（invalid_input）",
            mechanism="invalid_input",
        )
    if round_trips == 0 or turnover_value == 0:
        return _incomplete(
            gross_return,
            turnover_value,
            holding_period_hours_value,
            round_trips,
            cost_model,
            observed_at,
            deciding_tier,
            reason="无模拟成交且无独立信号观测，成本无法裁决（missing_input）",
            mechanism="missing_input",
        )
    missing_tiers = [name for name in COST_TIERS if name not in cost_model]
    if missing_tiers:
        return _incomplete(
            gross_return,
            turnover_value,
            holding_period_hours_value,
            round_trips,
            cost_model,
            observed_at,
            deciding_tier,
            reason=f"成本模型缺档位: {missing_tiers}",
            mechanism="missing_input",
        )

    net = {name: net_return(gross_return, turnover_value, cost_model[name]) for name in COST_TIERS}
    verdict = cost_verdict(net, deciding_tier=deciding_tier)
    result = CostResult(
        gross_return=gross_return,
        turnover=turnover_value,
        holding_period_hours=holding_period_hours_value,
        round_trips=round_trips,
        net_returns=net,
        breakeven_bps=breakeven_cost_bps(gross_return, turnover_value),
        deciding_tier=deciding_tier,
        verdict=verdict,
    )
    if verdict == COST_POSITIVE:
        return result, StageResult(stage_id=STAGE_COST_CAPACITY, status=STATUS_PASS)
    failure = FailureRecord(
        stage=STAGE_COST_CAPACITY,
        owner="cost",
        mechanism="cost_negative",
        error_code=ERROR_CODE,
        first_seen=observed_at,
    )
    return result, StageResult(
        stage_id=STAGE_COST_CAPACITY, status=STATUS_FAIL, failures=(failure,)
    )


def _incomplete(
    gross_return: float,
    turnover_value: float,
    holding_period_hours_value: float,
    round_trips: int,
    cost_model: Mapping[str, CostTier],
    observed_at: str,
    deciding_tier: str,
    *,
    reason: str,
    mechanism: str,
) -> tuple[CostResult, StageResult]:
    failure = FailureRecord(
        stage=STAGE_COST_CAPACITY,
        owner="cost",
        mechanism=mechanism,
        error_code=ERROR_CODE,
        first_seen=observed_at,
    )
    result = CostResult(
        gross_return=gross_return,
        turnover=turnover_value,
        holding_period_hours=holding_period_hours_value,
        round_trips=round_trips,
        net_returns={},
        breakeven_bps=(
            breakeven_cost_bps(gross_return, turnover_value) if turnover_value > 0 else None
        ),
        deciding_tier=deciding_tier,
        verdict=COST_UNDETERMINED,
    )
    return result, StageResult(
        stage_id=STAGE_COST_CAPACITY, status=STATUS_INCOMPLETE, reason=reason, failures=(failure,)
    )
