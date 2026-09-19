"""T008 / `FR-002`·`FR-007`·`AC-002`·`AC-009`：方法论门能力/守卫配对与三层无前视状态。

覆盖：L1 静态纯度（未来算子/负向 shift/空表达式）fail-closed、能力覆盖默认拒绝、四类运行时守卫
（label endpoint 跨折、embargo、train-only fit、as-of join 方向与陈旧度）加 forward-fill 与
跨 pair/算子登记、三层状态逐层显式记录（L2/L3 `not_yet_available` 且带 owner）、非 PASS 即阻断晋级。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.validation import methodology_gate as mg
from alphamill.validation.no_lookahead import (
    LAYER_L1,
    LAYER_L2,
    LAYER_L3,
    OWNER_F006_M3,
    OWNER_F007,
    STATUS_FAIL,
    STATUS_NOT_YET_AVAILABLE,
    STATUS_PASS,
    NoLookahead,
    NoLookaheadError,
    NoLookaheadLayer,
    build_no_lookahead,
)

BASE = datetime(2026, 9, 1, tzinfo=UTC)


def _context(**overrides) -> mg.GuardContext:
    base = {
        "max_label_horizon": 24,
        "embargo": 24,
    }
    base.update(overrides)
    return mg.GuardContext(**base)


# ---------- L1 静态纯度 ----------


def test_clean_expression_passes_l1():
    verdict = mg.evaluate_methodology(
        expression="rank(close / delay(close, 1))",
        declared_capabilities=[mg.CAPABILITY_OPERATOR],
        context=_context(
            used_operators=("rank", "delay"), registered_operators=frozenset({"rank", "delay"})
        ),
        l1_evidence_refs=("sha256:" + "a" * 64,),
    )
    assert verdict.passed is True
    assert verdict.no_lookahead.get(LAYER_L1).status == STATUS_PASS


@pytest.mark.parametrize(
    "expression",
    [
        "future_return",
        "lookahead_close",
        "shift(close, -1)",
        "shift(close,-2)",
        "peek(x)",
        "lead(x)",
    ],
)
def test_lookahead_expressions_are_rejected(expression: str):
    verdict = mg.evaluate_methodology(
        expression=expression,
        declared_capabilities=[],
        context=_context(),
    )
    assert verdict.passed is False
    assert verdict.l1_failed is True
    assert verdict.failure_mechanism == "lookahead"
    assert verdict.no_lookahead.blocks_promotion is True


def test_empty_expression_is_rejected():
    with pytest.raises(mg.GuardViolation, match="为空"):
        mg.assert_no_lookahead_expression("   ")


# ---------- 能力/守卫配对 ----------


def test_every_declared_capability_has_a_guard():
    payload = mg.guard_registry_payload()
    guarded = {spec["capability"] for spec in payload["guards"]}
    assert guarded == set(mg.CAPABILITIES)
    for capability in mg.CAPABILITIES:
        assert mg.guards_for(capability)


def test_unknown_capability_is_denied_by_default():
    verdict = mg.evaluate_methodology(
        expression="close", declared_capabilities=["teleport"], context=_context()
    )
    assert verdict.passed is False
    assert verdict.failure_mechanism == "capability_unguarded"
    assert any("未知能力" in violation.message for violation in verdict.violations)


# ---------- 运行时守卫 ----------


def test_label_endpoint_crossing_fold_is_rejected():
    fold_bounds = (
        (BASE, BASE + timedelta(hours=24)),
        (BASE + timedelta(hours=24), BASE + timedelta(hours=48)),
    )
    context = _context(
        signal_times=(BASE + timedelta(hours=23),),
        label_endpoints=(BASE + timedelta(hours=25),),
        fold_bounds=fold_bounds,
    )
    violations = mg.run_guards("close", context)
    assert any("跨越切分边界" in violation.message for violation in violations)


def test_label_endpoint_inside_fold_is_accepted():
    fold_bounds = (
        (BASE, BASE + timedelta(hours=24)),
        (BASE + timedelta(hours=24), BASE + timedelta(hours=48)),
    )
    context = _context(
        signal_times=(BASE + timedelta(hours=1),),
        label_endpoints=(BASE + timedelta(hours=5),),
        fold_bounds=fold_bounds,
    )
    assert mg.run_guards("close", context) == ()


def test_embargo_smaller_than_max_horizon_is_rejected():
    violations = mg.run_guards("close", _context(max_label_horizon=48, embargo=24))
    assert any("embargo" in violation.message for violation in violations)


def test_fit_indices_outside_train_fold_are_rejected():
    violations = mg.run_guards(
        "zscore(close)", _context(train_indices=frozenset({0, 1}), fit_indices=frozenset({0, 1, 9}))
    )
    assert any("拟合索引越出训练折" in violation.message for violation in violations)


def test_asof_join_direction_and_staleness_are_enforced():
    forward = mg.run_guards("join(a, b)", _context(join_direction="forward"))
    assert any("方向必须为 backward" in violation.message for violation in forward)
    stale = mg.run_guards(
        "join(a, b)",
        _context(join_staleness_seconds=120.0, join_max_staleness_seconds=60.0),
    )
    assert any("陈旧度" in violation.message for violation in stale)


def test_forward_fill_and_registration_guards():
    fill = mg.run_guards(
        "ffill(close)", _context(forward_fill_seconds=90.0, forward_fill_max_seconds=30.0)
    )
    assert any("forward-fill" in violation.message for violation in fill)
    operators = mg.run_guards(
        "rank(close)",
        _context(used_operators=("rank", "future_op"), registered_operators=frozenset({"rank"})),
    )
    assert any("算子未登记" in violation.message for violation in operators)
    cross = mg.run_guards(
        "corr(btc, eth)", _context(cross_pair_operators=("corr",), registered_operators=frozenset())
    )
    assert any("跨 pair 算子未登记" in violation.message for violation in cross)


def test_violations_are_collected_not_short_circuited():
    violations = mg.run_guards(
        "ffill(join(a,b))", _context(join_direction="forward", forward_fill_seconds=90.0)
    )
    assert len(violations) >= 2


# ---------- 三层无前视 ----------


def test_default_layers_mark_l2_l3_not_yet_available_with_owner():
    layers = build_no_lookahead(l1_status=STATUS_PASS, l1_evidence_refs=("sha256:" + "b" * 64,))
    payload = layers.to_payload()
    assert [entry["layer"] for entry in payload["layers"]] == [LAYER_L1, LAYER_L2, LAYER_L3]
    assert payload["layers"][0]["owner"] == OWNER_F007
    assert payload["layers"][1]["owner"] == OWNER_F006_M3
    assert payload["layers"][1]["status"] == STATUS_NOT_YET_AVAILABLE
    assert payload["layers"][2]["status"] == STATUS_NOT_YET_AVAILABLE
    assert payload["blocks_promotion"] is True


def test_layer_recorded_as_pass_requires_evidence():
    with pytest.raises(NoLookaheadError, match="必须携带证据引用"):
        NoLookaheadLayer(LAYER_L1, STATUS_PASS)


def test_omitting_a_layer_is_rejected():
    with pytest.raises(NoLookaheadError, match="不得静默省略"):
        NoLookahead(layers=(NoLookaheadLayer(LAYER_L1, STATUS_FAIL),))


@pytest.mark.parametrize(
    ("layer", "status", "message"),
    [("L4", STATUS_PASS, "未登记的无前视层"), (LAYER_L1, "OK", "未登记的无前视层状态")],
)
def test_unknown_layer_or_status_is_rejected(layer: str, status: str, message: str):
    with pytest.raises(NoLookaheadError, match=message):
        NoLookaheadLayer(layer, status)


def test_all_layers_pass_lifts_promotion_block():
    layers = NoLookahead(
        layers=(
            NoLookaheadLayer(LAYER_L1, STATUS_PASS, ("sha256:" + "c" * 64,)),
            NoLookaheadLayer(LAYER_L2, STATUS_PASS, ("reports/replay.json",)),
            NoLookaheadLayer(LAYER_L3, STATUS_PASS, ("reports/cache_align.json",)),
        )
    )
    assert layers.non_pass_layers == ()
    assert layers.blocks_promotion is False
