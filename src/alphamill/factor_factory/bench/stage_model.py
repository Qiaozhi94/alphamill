"""阶段状态与裁决枚举（design §3.3 术语表；`FR-003`/`FR-005`，任务 T007）。

术语表是**冻结**的单一真相源：五阶段 ID、阶段状态、成本裁决、样本量三级、晋升裁决与失败三维
都只在这里定义，其他模块引用而不另立枚举。阶段状态与晋升/成本 verdict 是**两层独立枚举**，
不得互相替代：`PASS` 只描述单阶段结果，**不是**晋级结论（`FR-003`）。

半开区间的样本量三级取自 `design.md` §3.3 / `spec.md` `FR-005`：
`[0,30)` underpowered（不判 PASS 也不判 FAIL）· `[30,69)` provisional（最多临时 PASS，仅缩减
仓位 paper）· `[69,∞)` trustworthy（才允许完整成本后 PASS/FAIL 判定）。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

STAGE_SIGNAL_QUALITY = "signal_quality"
STAGE_PORTFOLIO_TRANSFORM = "portfolio_transform"
STAGE_COST_CAPACITY = "cost_capacity"
STAGE_TEMPORAL_STABILITY = "temporal_stability"
STAGE_EXECUTION_IMPLEMENTATION = "execution_implementation"

STAGE_IDS = (
    STAGE_SIGNAL_QUALITY,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_COST_CAPACITY,
    STAGE_TEMPORAL_STABILITY,
    STAGE_EXECUTION_IMPLEMENTATION,
)
STAGE_OWNERS = {
    STAGE_SIGNAL_QUALITY: "signal",
    STAGE_PORTFOLIO_TRANSFORM: "portfolio",
    STAGE_COST_CAPACITY: "cost",
    STAGE_TEMPORAL_STABILITY: "statistics",
    STAGE_EXECUTION_IMPLEMENTATION: "execution",
}
OPTIONAL_STAGES = (STAGE_PORTFOLIO_TRANSFORM, STAGE_EXECUTION_IMPLEMENTATION)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"
STATUS_UNDERPOWERED = "UNDERPOWERED"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_NOT_APPLICABLE = "NOT_APPLICABLE"
STAGE_STATUSES = (
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_UNDERPOWERED,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
)

COST_POSITIVE = "cost_positive"
COST_NEGATIVE = "cost_negative"
COST_UNDETERMINED = "cost_undetermined"
COST_VERDICTS = (COST_POSITIVE, COST_NEGATIVE, COST_UNDETERMINED)

TIER_UNDERPOWERED = "underpowered"
TIER_PROVISIONAL = "provisional"
TIER_TRUSTWORTHY = "trustworthy"
SAMPLE_TIERS = (TIER_UNDERPOWERED, TIER_PROVISIONAL, TIER_TRUSTWORTHY)
SAMPLE_TIER_BOUNDS = (
    (TIER_UNDERPOWERED, 0, 30),
    (TIER_PROVISIONAL, 30, 69),
    (TIER_TRUSTWORTHY, 69, None),
)
SAMPLE_UNIT_ROUND_TRIPS = "round_trips"
SAMPLE_UNIT_OBSERVATIONS = "signal_observations"
SAMPLE_UNITS = (SAMPLE_UNIT_ROUND_TRIPS, SAMPLE_UNIT_OBSERVATIONS)

PROMOTION_VERDICTS = (
    "promising",
    TIER_PROVISIONAL,
    "blocked_pending_audit",
    "dead",
    TIER_UNDERPOWERED,
    "incomplete",
    "rejected",
)

FAILURE_OWNERS = ("data", "signal", "method", "statistics", "cost", "execution", "infra")
FAILURE_MECHANISMS = (
    "missing_input",
    "invalid_input",
    "capability_unguarded",
    "lookahead",
    "estimator_failure",
    "publish_failure",
    "underpowered",
    "cost_negative",
)


class StageModelError(ValueError):
    """违反冻结术语表的取值或组合。"""


def sample_tier(trade_count: int, *, sample_unit: str = SAMPLE_UNIT_ROUND_TRIPS) -> str:
    """按半开区间裁决样本量三级；`sample_unit` 显式记录计数口径（`FR-005`）。"""
    if not isinstance(trade_count, int) or isinstance(trade_count, bool) or trade_count < 0:
        raise StageModelError(f"样本量必须是非负整数: {trade_count!r}")
    if sample_unit not in SAMPLE_UNITS:
        raise StageModelError(f"未知 sample_unit: {sample_unit!r}（合法: {list(SAMPLE_UNITS)}）")
    for tier, lower, upper in SAMPLE_TIER_BOUNDS:
        if trade_count >= lower and (upper is None or trade_count < upper):
            return tier
    raise StageModelError(f"样本量 {trade_count} 没有匹配的样本量档位")


@dataclass(frozen=True)
class FailureRecord:
    """失败三维记录（`design.md` §3.3）：`stage × owner × mechanism`，枚举外取值即拒绝。"""

    stage: str
    owner: str
    mechanism: str
    error_code: str
    first_seen: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.stage not in STAGE_IDS:
            raise StageModelError(f"失败记录 stage 未登记: {self.stage!r}")
        if self.owner not in FAILURE_OWNERS:
            raise StageModelError(f"失败记录 owner 未登记: {self.owner!r}")
        if self.mechanism not in FAILURE_MECHANISMS:
            raise StageModelError(f"失败记录 mechanism 未登记: {self.mechanism!r}")
        if not self.error_code:
            raise StageModelError("失败记录必须有 error_code")

    def to_payload(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "owner": self.owner,
            "mechanism": self.mechanism,
            "error_code": self.error_code,
            "first_seen": self.first_seen,
            "evidence_refs": list(self.evidence_refs),
        }


@dataclass(frozen=True)
class StageResult:
    stage_id: str
    status: str
    reason: str | None = None
    failures: tuple[FailureRecord, ...] = ()

    def __post_init__(self) -> None:
        if self.stage_id not in STAGE_IDS:
            raise StageModelError(f"阶段 ID 未登记: {self.stage_id!r}")
        if self.status not in STAGE_STATUSES:
            raise StageModelError(f"阶段状态未登记: {self.status!r}")
        if self.status == STATUS_NOT_APPLICABLE and not self.reason:
            raise StageModelError(f"{self.stage_id} 记为 NOT_APPLICABLE 必须给出原因")
        for failure in self.failures:
            if failure.stage != self.stage_id:
                raise StageModelError(
                    f"失败记录的 stage={failure.stage!r} 与所属阶段 {self.stage_id!r} 不一致"
                )
        if self.status == STATUS_PASS and self.failures:
            raise StageModelError(f"{self.stage_id} 记为 PASS 时不得携带失败记录")

    @property
    def owner(self) -> str:
        return STAGE_OWNERS[self.stage_id]

    @property
    def counts_as_pass(self) -> bool:
        return self.status == STATUS_PASS

    def to_payload(self) -> dict[str, Any]:
        return {
            "stage": self.stage_id,
            "owner": self.owner,
            "status": self.status,
            "reason": self.reason,
            "failures": [failure.to_payload() for failure in self.failures],
        }


@dataclass(frozen=True)
class StageResults:
    """五阶段结果集合；`NOT_APPLICABLE` 不参与通过计数。"""

    results: tuple[StageResult, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        seen = [result.stage_id for result in self.results]
        if len(set(seen)) != len(seen):
            raise StageModelError(f"同一阶段不得重复记录: {seen}")

    def get(self, stage_id: str) -> StageResult | None:
        return next((result for result in self.results if result.stage_id == stage_id), None)

    def with_status(self, status: str) -> tuple[str, ...]:
        return tuple(result.stage_id for result in self.results if result.status == status)

    @property
    def failed_stages(self) -> tuple[str, ...]:
        return self.with_status(STATUS_FAIL)

    @property
    def underpowered_stages(self) -> tuple[str, ...]:
        return self.with_status(STATUS_UNDERPOWERED)

    @property
    def incomplete_stages(self) -> tuple[str, ...]:
        return self.with_status(STATUS_INCOMPLETE)

    @property
    def passed_stages(self) -> tuple[str, ...]:
        return self.with_status(STATUS_PASS)

    @property
    def evidence_complete(self) -> bool:
        """证据是否完整（可进 `EVIDENCE_READY`）：`INCOMPLETE` 是唯一未完状态。"""
        return not self.incomplete_stages

    @property
    def blocks_promotion(self) -> bool:
        """存在未通过/未达功效的阶段时不得产生可晋级结论。"""
        return bool(self.failed_stages or self.underpowered_stages or self.incomplete_stages)

    def failures(self) -> tuple[FailureRecord, ...]:
        return tuple(failure for result in self.results for failure in result.failures)

    def to_payload(self) -> list[dict[str, Any]]:
        ordered = sorted(self.results, key=lambda result: STAGE_IDS.index(result.stage_id))
        return [result.to_payload() for result in ordered]

    @classmethod
    def from_payload(cls, payload: Iterable[Mapping[str, Any]]) -> StageResults:
        results = []
        for entry in payload:
            failures = tuple(
                FailureRecord(
                    stage=str(item["stage"]),
                    owner=str(item["owner"]),
                    mechanism=str(item["mechanism"]),
                    error_code=str(item["error_code"]),
                    first_seen=str(item["first_seen"]),
                    evidence_refs=tuple(str(ref) for ref in item.get("evidence_refs", ())),
                )
                for item in entry.get("failures", ())
            )
            results.append(
                StageResult(
                    stage_id=str(entry["stage"]),
                    status=str(entry["status"]),
                    reason=entry.get("reason"),
                    failures=failures,
                )
            )
        return cls(results=tuple(results))


def not_applicable(stage_id: str, reason: str) -> StageResult:
    """把尚不适用的阶段显式记为 `NOT_APPLICABLE`（不得记为 `PASS`）。"""
    if stage_id not in OPTIONAL_STAGES:
        raise StageModelError(f"{stage_id} 是必需阶段，不得记为 NOT_APPLICABLE")
    return StageResult(stage_id=stage_id, status=STATUS_NOT_APPLICABLE, reason=reason)


def pass_through_optional(stage_id: str, *, reason: str, applicable: bool) -> StageResult:
    """可选阶段的二选一入口：不适用即显式 NOT_APPLICABLE，适用则交由调用方判 PASS/FAIL。"""
    if not applicable:
        return not_applicable(stage_id, reason)
    raise StageModelError(f"{stage_id} 适用时必须由评测器给出 PASS/FAIL，不能走此入口")


def stage_for_evidence(
    stage_id: str,
    *,
    complete: bool,
    passed: bool | None,
    failure: FailureRecord | None = None,
) -> StageResult:
    """由「证据是否完整 / 是否通过」推导阶段状态，避免各处自行拼状态字符串。"""
    if not complete:
        return StageResult(
            stage_id=stage_id, status=STATUS_INCOMPLETE, failures=tuple(filter(None, (failure,)))
        )
    if passed is None:
        return StageResult(
            stage_id=stage_id, status=STATUS_UNDERPOWERED, failures=tuple(filter(None, (failure,)))
        )
    status = STATUS_PASS if passed else STATUS_FAIL
    return StageResult(stage_id=stage_id, status=status, failures=tuple(filter(None, (failure,))))
