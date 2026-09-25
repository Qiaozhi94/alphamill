"""F003 FR-006/AC-007：IC 口径对齐（张量世界 vs pandas 世界，仅数值回归）。"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from alphamill.factor_factory.generators import ic_parity as icp

FEATURE_MAP = {"close": 0}
VERDICT_FIELDS = {"ic", "rank_ic", "pnl", "verdict", "promoted", "cost_verdict", "rankic"}


def _hand_series(level_values: list[float]) -> pd.Series:
    index = pd.MultiIndex.from_product(
        [pd.to_datetime(["2026-09-01T00:00Z"]), ["A", "B", "C"]], names=("timestamp", "pair")
    )
    return pd.Series(level_values, index=index, dtype=float)


def test_hand_computed_ic_anchor_is_exact() -> None:
    values = np.array([[1.0, 2.0, 3.0]])
    same_order = np.array([[0.1, 0.2, 0.3]])
    reverse_order = np.array([[0.3, 0.2, 0.1]])

    assert icp.tensor_ic(values, same_order) == pytest.approx(1.0)
    assert icp.tensor_ic(values, reverse_order) == pytest.approx(-1.0)
    assert icp.pandas_ic(
        _hand_series([1.0, 2.0, 3.0]), _hand_series([0.1, 0.2, 0.3])
    ) == pytest.approx(1.0)


def _panel_and_returns() -> tuple[pd.DataFrame, pd.Series]:
    timestamps = pd.to_datetime(
        [
            "2026-09-01T00:00Z",
            "2026-09-01T01:00Z",
            "2026-09-01T02:00Z",
            "2026-09-01T03:00Z",
            "2026-09-01T04:00Z",
        ]
    )
    pairs = ["A-USDT", "B-USDT", "C-USDT", "D-USDT"]
    index = pd.MultiIndex.from_product([timestamps, pairs], names=("timestamp", "pair"))
    close = [
        10,
        20,
        30,
        40,
        11,
        19,
        33,
        38,
        13,
        21,
        31,
        41,
        12,
        22,
        34,
        39,
        14,
        18,
        35,
        42,
    ]
    panel = pd.DataFrame({"close": close, "__in_universe__": True}, index=index)
    forward = panel["close"].groupby(level="pair").pct_change().shift(-1).dropna()
    return panel, forward


def test_tensor_and_pandas_ic_agree_for_several_expressions() -> None:
    panel, forward = _panel_and_returns()
    for expression in [
        ("feature:close", "return:1", "cs_rank"),
        ("feature:close", "neg"),
        ("feature:close", "pct_change:1"),
    ]:
        result = icp.compare_ic(expression, panel, forward, feature_map=FEATURE_MAP)
        assert result.matched, f"{expression}: {result.detail}"
        assert result.points > 0


def test_masking_is_applied_identically_on_both_sides() -> None:
    panel, forward = _panel_and_returns()
    masked = panel.copy()
    masked.loc[(slice(None), ["C-USDT", "D-USDT"]), "__in_universe__"] = False

    result = icp.compare_ic(
        ("feature:close", "return:1", "cs_rank"), masked, forward, feature_map=FEATURE_MAP
    )
    assert result.matched, result.detail


def test_parity_check_detects_convention_drift() -> None:
    """若一侧误用 Pearson 而非 Spearman，差异必须远超容差——证明该检查并非空转。"""
    values = np.array([[1.0, 2.0, 3.0, 100.0]])
    returns = np.array([[1.0, 2.0, 3.0, 4.0]])

    spearman = icp.tensor_ic(values, returns)
    pearson = float(np.corrcoef(values[0], returns[0])[0, 1])

    assert spearman == pytest.approx(1.0)
    assert abs(spearman - pearson) > icp.IC_PARITY_TOLERANCE


def test_degenerate_inputs_are_documented_not_silent() -> None:
    assert icp.tensor_ic(np.array([[1.0]]), np.array([[0.1]])) == 0.0
    assert icp.tensor_ic(np.zeros((1, 3)), np.array([[1.0, 2.0, 3.0]])) == 0.0


def test_result_surface_exposes_no_verdict_fields() -> None:
    assert not VERDICT_FIELDS & set(icp.IcParityResult.__dataclass_fields__)
