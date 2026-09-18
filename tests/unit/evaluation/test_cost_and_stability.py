"""T007 / `FR-003`·`FR-005`·`AC-004`：阶段状态模型、三档成本/breakeven 与最小信号质量。

覆盖：术语表枚举的 fail-closed 校验、样本量三级半开区间边界、阶段状态推导与失败三维记录、
三档成本单调性与成本裁决（`cost_positive`/`cost_negative`/`cost_undetermined`）、breakeven 与
换手/持有期、Rank IC 的真实夹具对照、`approximation` 与 `source=placeholder` 分层。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphamill.evaluation.contract_common import (
    SIGNAL_SOURCE_PLACEHOLDER,
    TIER_CANONICAL,
    TIER_PREVIEW,
    UpstreamContractError,
)
from alphamill.evaluation.signal_adapter import adapt_signal_records
from alphamill.factor_factory.bench.cost import (
    COST_TIERS,
    CostTier,
    breakeven_cost_bps,
    cost_drag,
    cost_verdict,
    evaluate_cost,
    holding_period_hours,
    load_cost_model,
    net_return,
    turnover,
)
from alphamill.factor_factory.bench.signal_quality import (
    Approximation,
    approximation_for,
    evaluate_signal_quality,
    rank_ic,
    signal_source_payload,
)
from alphamill.factor_factory.bench.stage_model import (
    COST_NEGATIVE,
    COST_POSITIVE,
    COST_UNDETERMINED,
    STAGE_COST_CAPACITY,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_IDS,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_SIGNAL_QUALITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_NOT_APPLICABLE,
    STATUS_PASS,
    STATUS_UNDERPOWERED,
    FailureRecord,
    StageModelError,
    StageResult,
    StageResults,
    not_applicable,
    pass_through_optional,
    sample_tier,
    stage_for_evidence,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "f007"
METHOD = json.loads((FIXTURES / "method-v1.json").read_text(encoding="utf-8"))
COST_MODEL = load_cost_model(METHOD["cost_model"]["normalized"])
NOW = "2026-09-01T00:00:00Z"


def fixture_frame(name: str):
    import pandas as pd

    return pd.read_csv(FIXTURES / "controls" / f"{name}.csv")


# ---------- 术语表与阶段模型 ----------


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (0, "underpowered"),
        (29, "underpowered"),
        (30, "provisional"),
        (68, "provisional"),
        (69, "trustworthy"),
        (500, "trustworthy"),
    ],
)
def test_sample_tier_half_open_boundaries(count: int, expected: str):
    assert sample_tier(count) == expected


def test_sample_tier_records_counting_unit_and_rejects_garbage():
    assert sample_tier(70, sample_unit="signal_observations") == "trustworthy"
    with pytest.raises(StageModelError, match="sample_unit"):
        sample_tier(70, sample_unit="bars")
    with pytest.raises(StageModelError, match="非负整数"):
        sample_tier(-1)


def test_not_applicable_requires_reason_and_only_for_optional_stages():
    with pytest.raises(StageModelError, match="必须给出原因"):
        StageResult(stage_id=STAGE_PORTFOLIO_TRANSFORM, status=STATUS_NOT_APPLICABLE)
    assert not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合").reason
    with pytest.raises(StageModelError, match="必需阶段"):
        not_applicable(STAGE_SIGNAL_QUALITY, "想跳过")


def test_optional_stage_must_not_fake_pass_via_not_applicable():
    with pytest.raises(StageModelError, match="不能走此入口"):
        pass_through_optional(STAGE_EXECUTION_IMPLEMENTATION, reason="x", applicable=True)


def test_pass_cannot_carry_failures_and_failure_stage_must_match():
    failure = FailureRecord(
        stage=STAGE_COST_CAPACITY,
        owner="cost",
        mechanism="cost_negative",
        error_code="E_REQUIRED_METRIC_FAILED",
        first_seen=NOW,
    )
    with pytest.raises(StageModelError, match="不得携带失败记录"):
        StageResult(stage_id=STAGE_COST_CAPACITY, status=STATUS_PASS, failures=(failure,))
    with pytest.raises(StageModelError, match="不一致"):
        StageResult(stage_id=STAGE_SIGNAL_QUALITY, status=STATUS_FAIL, failures=(failure,))


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"stage_id": "unknown_stage", "status": STATUS_PASS}, "阶段 ID"),
        ({"stage_id": STAGE_SIGNAL_QUALITY, "status": "OK"}, "阶段状态"),
    ],
)
def test_unknown_enum_values_are_rejected(kwargs: dict, message: str):
    with pytest.raises(StageModelError, match=message):
        StageResult(**kwargs)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("stage", "nope", "stage"),
        ("owner", "wizard", "owner"),
        ("mechanism", "vibes", "mechanism"),
    ],
)
def test_failure_taxonomy_is_fail_closed(field: str, value: str, message: str):
    base = {
        "stage": STAGE_COST_CAPACITY,
        "owner": "cost",
        "mechanism": "cost_negative",
        "error_code": "E_REQUIRED_METRIC_FAILED",
        "first_seen": NOW,
    }
    with pytest.raises(StageModelError, match=message):
        FailureRecord(**{**base, field: value})


def test_stage_results_summarize_and_roundtrip():
    results = StageResults(
        results=(
            StageResult(stage_id=STAGE_SIGNAL_QUALITY, status=STATUS_PASS),
            StageResult(stage_id=STAGE_COST_CAPACITY, status=STATUS_INCOMPLETE),
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合"),
        )
    )
    assert results.evidence_complete is False
    assert results.incomplete_stages == (STAGE_COST_CAPACITY,)
    assert results.passed_stages == (STAGE_SIGNAL_QUALITY,)
    assert results.blocks_promotion is True
    assert results.to_payload()[0]["stage"] == STAGE_SIGNAL_QUALITY
    assert StageResults.from_payload(results.to_payload()).to_payload() == results.to_payload()
    with pytest.raises(StageModelError, match="重复"):
        StageResults(
            results=(
                StageResult(stage_id=STAGE_SIGNAL_QUALITY, status=STATUS_PASS),
                StageResult(stage_id=STAGE_SIGNAL_QUALITY, status=STATUS_PASS),
            )
        )


def test_stage_for_evidence_maps_incomplete_underpowered_and_verdicts():
    assert (
        stage_for_evidence(STAGE_SIGNAL_QUALITY, complete=False, passed=None).status
        == STATUS_INCOMPLETE
    )
    assert (
        stage_for_evidence(STAGE_SIGNAL_QUALITY, complete=True, passed=None).status
        == STATUS_UNDERPOWERED
    )
    assert (
        stage_for_evidence(STAGE_SIGNAL_QUALITY, complete=True, passed=True).status == STATUS_PASS
    )
    assert (
        stage_for_evidence(STAGE_SIGNAL_QUALITY, complete=True, passed=False).status == STATUS_FAIL
    )


def test_stage_ids_are_the_frozen_five():
    assert STAGE_IDS == (
        "signal_quality",
        "portfolio_transform",
        "cost_capacity",
        "temporal_stability",
        "execution_implementation",
    )


# ---------- 三档成本与 breakeven ----------


def test_cost_model_loads_three_tiers_from_preregistration():
    assert set(COST_MODEL) == {"zero", "maker", "taker"}
    assert COST_MODEL["zero"].total_bps == 0
    assert COST_MODEL["taker"].total_bps > COST_MODEL["maker"].total_bps > 0
    with pytest.raises(StageModelError, match="缺档位"):
        load_cost_model({"tiers": {"zero": {"fee_bps": 0, "slippage_bps": 0}}})


def test_net_return_is_monotonic_across_tiers():
    nets = [net_return(0.05, 4.0, COST_MODEL[name]) for name in COST_TIERS]
    assert nets == sorted(nets, reverse=True)
    assert nets[0] == pytest.approx(0.05)


def test_cost_drag_and_breakeven_are_consistent():
    tier = CostTier(name="taker", fee_bps=5, slippage_bps=2)
    assert cost_drag(4.0, tier) == pytest.approx(4.0 * 7 * 1e-4)
    breakeven = breakeven_cost_bps(0.05, 4.0)
    assert breakeven == pytest.approx((0.05 / 4.0) / 1e-4)
    assert net_return(0.05, 4.0, CostTier("taker", breakeven, 0.0)) == pytest.approx(0.0)
    assert breakeven_cost_bps(0.05, 0.0) is None
    assert breakeven_cost_bps(-0.01, 4.0) == 0.0


def test_turnover_and_holding_period_helpers():
    assert turnover(400.0, 100.0) == pytest.approx(4.0)
    assert holding_period_hours(240.0, 24) == pytest.approx(10.0)
    with pytest.raises(StageModelError, match="资金"):
        turnover(10.0, 0.0)
    with pytest.raises(StageModelError, match="往返笔数"):
        holding_period_hours(10.0, 0)


def test_cost_verdict_uses_deciding_tier_and_flags_undetermined():
    assert cost_verdict({"zero": 0.01, "maker": -0.01, "taker": -0.02}) == COST_NEGATIVE
    assert cost_verdict({"zero": 0.02, "maker": 0.01, "taker": 0.005}) == COST_POSITIVE
    assert cost_verdict({"zero": 0.02}) == COST_UNDETERMINED
    with pytest.raises(StageModelError, match="裁决档位"):
        cost_verdict({}, deciding_tier="vip")


def test_evaluate_cost_surviving_candidate_is_pass():
    result, stage = evaluate_cost(
        gross_return=0.05,
        turnover_value=2.0,
        round_trips=100,
        holding_period_hours_value=4.0,
        cost_model=COST_MODEL,
        observed_at=NOW,
    )
    assert result.verdict == COST_POSITIVE
    assert stage.status == STATUS_PASS
    assert set(result.net_returns) == set(COST_TIERS)
    assert result.to_payload()["turnover"] == 2.0


def test_evaluate_cost_dead_candidate_fails_with_taxonomy_record():
    result, stage = evaluate_cost(
        gross_return=0.001,
        turnover_value=40.0,
        round_trips=100,
        holding_period_hours_value=4.0,
        cost_model=COST_MODEL,
        observed_at=NOW,
    )
    assert result.verdict == COST_NEGATIVE
    assert stage.status == STATUS_FAIL
    assert stage.failures[0].mechanism == "cost_negative"
    assert stage.failures[0].owner == "cost"


@pytest.mark.parametrize(
    ("kwargs", "mechanism"),
    [
        ({"round_trips": 0}, "missing_input"),
        ({"turnover_value": 0.0}, "missing_input"),
        ({"turnover_value": -1.0}, "invalid_input"),
    ],
)
def test_evaluate_cost_incomplete_paths(kwargs: dict, mechanism: str):
    base = {
        "gross_return": 0.05,
        "turnover_value": 2.0,
        "round_trips": 100,
        "holding_period_hours_value": 4.0,
        "cost_model": COST_MODEL,
        "observed_at": NOW,
    }
    result, stage = evaluate_cost(**{**base, **kwargs})
    assert result.verdict == COST_UNDETERMINED
    assert stage.status == STATUS_INCOMPLETE
    assert stage.failures[0].mechanism == mechanism


# ---------- 信号质量 ----------


def test_rank_ic_on_real_control_fixtures():
    carry = fixture_frame("funding_carry")
    noise = fixture_frame("white_noise")
    assert rank_ic(carry["signal"], carry["forward_return"]) > 0.8
    assert abs(rank_ic(noise["signal"], noise["forward_return"])) < 0.2


@pytest.mark.parametrize(
    ("signal", "label", "message"),
    [
        ([1.0, 2.0], [1.0], "长度不一致"),
        ([1.0, float("nan"), 3.0], [1.0, 2.0, 3.0], "缺失值"),
        ([1.0, 1.0, 1.0], [1.0, 2.0, 3.0], "常数"),
        ([1.0], [1.0], "至少需要 2 个观测"),
    ],
)
def test_rank_ic_rejects_degenerate_inputs(signal, label, message: str):
    with pytest.raises(StageModelError, match=message):
        rank_ic(signal, label)


def test_evaluate_signal_quality_status_ladder():
    empty = evaluate_signal_quality([], [], observed_at=NOW)
    assert empty[1].status == STATUS_INCOMPLETE
    assert empty[0].rank_ic is None

    small = evaluate_signal_quality(list(range(5)), list(range(5)), observed_at=NOW)
    assert small[1].status == STATUS_UNDERPOWERED
    assert small[0].rank_ic is None

    carry = fixture_frame("funding_carry")
    good = evaluate_signal_quality(carry["signal"], carry["forward_return"], observed_at=NOW)
    assert good[1].status == STATUS_PASS
    assert good[0].n_observations == 40
    assert good[0].rank_ic is not None


# ---------- 近似与信号来源 ----------


def test_approximation_is_rejected_for_canonical():
    with pytest.raises(StageModelError, match="canonical 不得近似"):
        approximation_for(TIER_CANONICAL, reduced_dimensions=["symbols"])
    with pytest.raises(StageModelError, match="canonical 不得近似"):
        approximation_for(TIER_CANONICAL, signal_source=SIGNAL_SOURCE_PLACEHOLDER)
    payload = approximation_for(TIER_CANONICAL).to_payload()
    assert payload == {"is_approximate": False, "reduced_dimensions": [], "signal_source": "real"}


def test_preview_approximation_is_explicit():
    payload = approximation_for(TIER_PREVIEW, reduced_dimensions=["window", "symbols"]).to_payload()
    assert payload["is_approximate"] is True
    assert payload["reduced_dimensions"] == ["symbols", "window"]
    assert approximation_for(TIER_PREVIEW).is_approximate is False


def test_approximation_dataclass_guards_misuse():
    with pytest.raises(StageModelError, match="非近似结果"):
        Approximation(is_approximate=False, reduced_dimensions=("window",))
    with pytest.raises(StageModelError, match="placeholder"):
        Approximation(is_approximate=False, signal_source=SIGNAL_SOURCE_PLACEHOLDER)


def _provenance(source: str):
    records = [{"time": NOW, "symbol": "BTC/USDT", "source": source, "signal": 1.0}]
    return adapt_signal_records(
        records,
        dataset="signals_log",
        adapter_version="f007-adapter-v1",
        signal_column="signal",
    )[1]


def test_placeholder_signal_source_fails_closed_for_canonical():
    with pytest.raises(UpstreamContractError) as excinfo:
        signal_source_payload(_provenance(SIGNAL_SOURCE_PLACEHOLDER), TIER_CANONICAL)
    assert excinfo.value.code == "E_INPUT_INVALID"


def test_placeholder_signal_source_is_annotated_for_preview():
    payload = signal_source_payload(_provenance(SIGNAL_SOURCE_PLACEHOLDER), TIER_PREVIEW)
    assert payload["approximation"] == {
        "is_approximate": True,
        "reduced_dimensions": [],
        "signal_source": "placeholder",
    }
    assert payload["signal_provenance"]["source_distribution"] == {"placeholder": 1}
