"""T002 / `FR-004`·`FR-005`：预注册配置与控制夹具的自检。

锁定 `tests/fixtures/f007/` 的 schema 与统计性质，防止夹具在后续任务中悄悄漂移：
样本量三级半开区间、五阶段/失败三维枚举、查重阈值、四个控制的方向性与"故意泄漏"性质、
以及 `expected-outcomes-v1.json` 与磁盘文件集合的双向一致。
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "f007"
CONTROLS = FIXTURES / "controls"

METHOD = json.loads((FIXTURES / "method-v1.json").read_text(encoding="utf-8"))
COHORT = json.loads((FIXTURES / "cohort-template-v1.json").read_text(encoding="utf-8"))
OUTCOMES = json.loads((FIXTURES / "expected-outcomes-v1.json").read_text(encoding="utf-8"))

STAGE_IDS = [
    "signal_quality",
    "portfolio_transform",
    "cost_capacity",
    "temporal_stability",
    "execution_implementation",
]
OWNERS = ["data", "signal", "method", "statistics", "cost", "execution", "infra"]
MECHANISMS = [
    "missing_input",
    "invalid_input",
    "capability_unguarded",
    "lookahead",
    "estimator_failure",
    "publish_failure",
    "underpowered",
    "cost_negative",
]


def load(control: dict) -> pd.DataFrame:
    return pd.read_csv(FIXTURES / control["path"])


def test_method_config_ids_and_schema_version():
    assert METHOD["schema_version"] == 1
    assert METHOD["method_config"]["id"] == "method-v1"
    assert METHOD["cost_model"]["id"] == "cm-v1"
    assert METHOD["method_config"]["normalized"]["required_statistics_fail_closed"] is True


def test_sample_tier_bounds_are_half_open_and_frozen():
    bounds = METHOD["sample_tier"]["bounds"]
    assert [(b["tier"], b["min_inclusive"], b["max_exclusive"]) for b in bounds] == [
        ("underpowered", 0, 30),
        ("provisional", 30, 69),
        ("trustworthy", 69, None),
    ]
    assert METHOD["sample_tier"]["unit"] == "round_trips"


@pytest.mark.parametrize(
    ("bound", "tier"),
    [(29, "underpowered"), (30, "provisional"), (68, "provisional"), (69, "trustworthy")],
)
def test_sample_tier_boundary_examples(bound: int, tier: str):
    matched = [
        b["tier"]
        for b in METHOD["sample_tier"]["bounds"]
        if bound >= b["min_inclusive"]
        and (b["max_exclusive"] is None or bound < b["max_exclusive"])
    ]
    assert matched == [tier]


def test_stage_and_failure_taxonomy_match_frozen_enums():
    assert METHOD["stage_ids"] == STAGE_IDS
    assert METHOD["failure_taxonomy"]["stage"] == STAGE_IDS
    assert METHOD["failure_taxonomy"]["owner"] == OWNERS
    assert METHOD["failure_taxonomy"]["mechanism"] == MECHANISMS


def test_dedup_thresholds_are_frozen():
    dedup = METHOD["method_config"]["normalized"]["dedup"]
    assert dedup["reject_above"] == 0.99
    assert dedup["variant_above"] == 0.90
    assert dedup["aggregate"] == "max_abs_rho"
    assert set(dedup["metrics"]) == {"oos_pnl", "rolling_ic"}


def test_no_lookahead_layer_ownership():
    layers = METHOD["no_lookahead_layers"]
    assert layers["L1"]["owner"] == "F007"
    assert layers["L2"]["owner"] == "F006/M3"
    assert layers["L3"]["owner"] == "F006/M3"


def test_cohort_template_carries_preregistered_invariants():
    schema = COHORT["cohort_schema"]
    for field in (
        "hypothesis_family",
        "selection_stage",
        "commitments",
        "window",
        "universe_digest",
        "calendar_digest",
        "frozen_at",
    ):
        assert field in schema, field
    assert "commitments 数组顺序" in COHORT["invariants"]["commitment_order_rule"]
    assert "REGISTERED" in COHORT["invariants"]["finalize_rule"]


def test_outcomes_cover_every_control_file_exactly():
    declared = {Path(c["path"]).name for c in OUTCOMES["controls"]}
    on_disk = {p.name for p in CONTROLS.glob("*.csv")}
    assert declared == on_disk
    assert len(OUTCOMES["controls"]) == 4


def test_every_control_uses_the_unified_column_set():
    columns = OUTCOMES["unified_columns"]
    for control in OUTCOMES["controls"]:
        assert list(load(control).columns) == columns, control["name"]


def test_positive_controls_have_predictive_signal():
    for name in ("funding_carry", "eth_btc_momentum"):
        control = next(c for c in OUTCOMES["controls"] if c["name"] == name)
        frame = load(control)
        assert control["kind"] == "positive"
        assert frame["signal"].corr(frame["forward_return"]) > 0.5


def test_white_noise_is_independent_of_the_label():
    control = next(c for c in OUTCOMES["controls"] if c["name"] == "white_noise")
    frame = load(control)
    assert control["expected"]["statistics"] == "not_significant_after_multiplicity_correction"
    assert abs(frame["signal"].corr(frame["forward_return"])) < 0.15


def test_leakage_control_is_future_filled_and_gate_rejected():
    control = next(c for c in OUTCOMES["controls"] if c["name"] == "future_fill_leakage")
    frame = load(control)
    assert (frame["signal"] == frame["forward_return"]).all()
    assert "shift(close, -1)" in control["factor"]["expression"]
    assert control["expected"]["methodology_gate"] == "FAIL"
    assert control["expected"]["mechanism"] == "lookahead"
    assert control["expected"]["run_state"] == "REJECTED"
    assert control["expected"]["still_registered"] is True


def test_control_member_verdicts_follow_the_frozen_priority_table():
    for control in OUTCOMES["controls"]:
        expected = control["expected"]
        if control["kind"] == "positive":
            assert expected["sample_tier"] == "underpowered"
            assert expected["promotion_verdict"] == "underpowered"
        else:
            assert expected["promotion_verdict"] in {"dead", "rejected"}
