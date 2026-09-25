"""F003 目标对齐测试：FR-005、NFR-001、AC-006。"""

from __future__ import annotations

import json
from dataclasses import asdict, fields, replace
from typing import Final

import pandas as pd
import pytest

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.objective import (
    CostModel,
    ObjectiveParams,
    ObjectiveResult,
    evaluate_objective,
    objective_to_run_info,
)

_ZERO_COST: Final = CostModel(
    taker_fee_bps=0.0,
    maker_fee_bps=0.0,
    slippage_bps=0.0,
)
_BASE_PARAMS: Final = ObjectiveParams(
    turnover_penalty_lambda=0.05,
    reachability_min_trades_90d=1,
    cost_model=_ZERO_COST,
    min_after_cost_return=-1.0,
)


def _panel(
    signals: list[float],
    *,
    closes: list[float] | None = None,
    in_universe: list[bool] | None = None,
) -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=len(signals), freq="1h", tz="UTC")
    index = pd.MultiIndex.from_arrays(
        [timestamps, ["BTC/USDT"] * len(signals)],
        names=["timestamp", "pair"],
    )
    return pd.DataFrame(
        {
            "signal": signals,
            "close": closes if closes is not None else [100.0] * len(signals),
            "__in_universe__": (in_universe if in_universe is not None else [True] * len(signals)),
        },
        index=index,
    )


def test_never_changing_signal_is_rejected_as_zero_trade() -> None:
    # Given
    panel = _panel([1.0, 1.0, 1.0, 1.0], closes=[100.0, 101.0, 102.0, 103.0])

    # When
    result = evaluate_objective(panel, params=_BASE_PARAMS)

    # Then
    assert not result.accepted
    assert result.reason_code == "reachability"
    assert result.trades_90d == 0


def test_frequently_flipping_signal_is_accepted() -> None:
    # Given
    panel = _panel([1.0, -1.0, 1.0, -1.0])
    params = replace(_BASE_PARAMS, reachability_min_trades_90d=3)

    # When
    result = evaluate_objective(panel, params=params)

    # Then
    assert result.accepted
    assert result.reason_code is None
    assert result.trades_90d >= params.reachability_min_trades_90d


def test_more_sign_flips_raise_turnover_and_lower_after_cost_return() -> None:
    # Given
    low_turnover = _panel([1.0, 1.0, -1.0, -1.0])
    high_turnover = _panel([1.0, -1.0, 1.0, -1.0])
    cost = CostModel(taker_fee_bps=4.0, maker_fee_bps=1.0, slippage_bps=2.0)
    params = replace(_BASE_PARAMS, cost_model=cost)

    # When
    low_result = evaluate_objective(low_turnover, params=params)
    high_result = evaluate_objective(high_turnover, params=params)

    # Then
    assert high_result.turnover > low_result.turnover
    assert high_result.after_cost_return < low_result.after_cost_return


def test_higher_taker_and_slippage_costs_lower_after_cost_return() -> None:
    # Given
    panel = _panel([1.0, -1.0, 1.0, -1.0], closes=[100.0, 102.0, 101.0, 103.0])
    expensive = CostModel(taker_fee_bps=8.0, maker_fee_bps=0.0, slippage_bps=5.0)

    # When
    zero_cost = evaluate_objective(panel, params=_BASE_PARAMS)
    costly = evaluate_objective(panel, params=replace(_BASE_PARAMS, cost_model=expensive))

    # Then
    assert zero_cost.after_cost_return == pytest.approx(zero_cost.gross_return)
    assert costly.after_cost_return < zero_cost.after_cost_return


def test_reachability_threshold_is_inclusive_at_exact_boundary() -> None:
    # Given
    panel = _panel([1.0, -1.0, 1.0])

    # When
    at_boundary = evaluate_objective(
        panel,
        params=replace(_BASE_PARAMS, reachability_min_trades_90d=2),
    )
    one_short = evaluate_objective(
        panel,
        params=replace(_BASE_PARAMS, reachability_min_trades_90d=3),
    )

    # Then
    assert at_boundary.trades_90d == 2
    assert at_boundary.accepted
    assert one_short.trades_90d == 2
    assert not one_short.accepted
    assert one_short.reason_code == "reachability"


def test_rows_outside_universe_do_not_contribute_or_bridge_sign_changes() -> None:
    # Given
    fully_tradable = _panel([1.0, -1.0, 1.0])
    masked_middle = _panel(
        [1.0, -1.0, 1.0],
        in_universe=[True, False, True],
    )

    # When
    full_result = evaluate_objective(fully_tradable, params=_BASE_PARAMS)
    masked_result = evaluate_objective(masked_middle, params=_BASE_PARAMS)

    # Then
    assert full_result.trades_90d == 2
    assert full_result.turnover > 0.0
    assert masked_result.trades_90d == 0
    assert masked_result.turnover == 0.0


def test_objective_to_run_info_preserves_all_configurable_fields() -> None:
    # Given
    params = ObjectiveParams(
        turnover_penalty_lambda=0.125,
        reachability_min_trades_90d=17,
        cost_model=CostModel(
            taker_fee_bps=7.0,
            maker_fee_bps=-1.0,
            slippage_bps=3.5,
            funding_8h_bps=0.75,
        ),
        min_after_cost_return=0.002,
    )

    # When
    info = objective_to_run_info(params)
    payload = asdict(info)

    # Then
    assert info.turnover_penalty_lambda == params.turnover_penalty_lambda
    assert info.reachability_min_trades_90d == params.reachability_min_trades_90d
    assert info.cost_model == asdict(params.cost_model)
    assert info.min_after_cost_return == params.min_after_cost_return
    assert json.loads(json.dumps(payload)) == payload


def test_public_models_expose_no_conclusion_fields() -> None:
    # Given
    forbidden = {"ic", "rank_ic", "pnl", "verdict", "promoted", "cost_model_version"}

    # When
    model_fields = {
        model.__name__: {field.name for field in fields(model)}
        for model in (CostModel, ObjectiveParams, ObjectiveResult)
    }

    # Then
    assert all(names.isdisjoint(forbidden) for names in model_fields.values())
    assert model_fields["ObjectiveResult"] == {
        "accepted",
        "reason_code",
        "turnover",
        "trades_90d",
        "gross_return",
        "after_cost_return",
        "detail",
    }


def test_empty_panel_raises_schema_error() -> None:
    # Given
    index = pd.MultiIndex.from_arrays([[], []], names=["timestamp", "pair"])
    panel = pd.DataFrame(columns=["signal", "close", "__in_universe__"], index=index)

    # When / Then
    with pytest.raises(SchemaValidationError):
        evaluate_objective(panel, params=_BASE_PARAMS)


def test_all_nan_signal_raises_schema_error() -> None:
    # Given
    panel = _panel([float("nan"), float("nan")])

    # When / Then
    with pytest.raises(SchemaValidationError):
        evaluate_objective(panel, params=_BASE_PARAMS)


def test_missing_universe_mask_raises_schema_error() -> None:
    # Given
    panel = _panel([1.0, -1.0]).drop(columns="__in_universe__")

    # When / Then
    with pytest.raises(SchemaValidationError):
        evaluate_objective(panel, params=_BASE_PARAMS)


def test_non_multi_index_raises_schema_error() -> None:
    # Given
    panel = pd.DataFrame(
        {"signal": [1.0, -1.0], "close": [100.0, 101.0], "__in_universe__": [True, True]}
    )

    # When / Then
    with pytest.raises(SchemaValidationError):
        evaluate_objective(panel, params=_BASE_PARAMS)
