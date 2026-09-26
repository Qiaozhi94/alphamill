"""Generation-side objective pre-filter signals for F003.

This module never produces an IC, rank-IC, PnL-significance, cost verdict, or
promotion decision. ADR-0003 assigns those conclusions, the three-tier cost
decision, and ``cost_model_version`` to F007. ``accepted`` only means that this
generation-side pre-filter passed; the fixed rejection vocabulary requires both
the trade-count and after-cost-return failures to use ``reachability``.

The input must contain ``signal``, ``__in_universe__``, and one close-like column:
either ``close`` or one unambiguous ``*.close@<resample>`` feature. A sign position
at bar t earns the close return from t to the next consecutive bar. ``gross_return``
is the arithmetic sum of equal-weight per-bar signed returns. ``turnover`` is the
sum across bars of the mean absolute sign-position change for pairs with valid,
consecutive, in-universe signals at both bars; universe entry and exit are not
treated as flat positions. ``trades_90d`` is the total direct nonzero sign changes
across pairs in the final 90 calendar days, compared directly with the configured
minimum.

Execution cost is turnover times taker fee + maker fee + slippage in basis points.
Modeled funding is charged by absolute held exposure in 8-hour equivalents only
when one funding-like feature is present; otherwise funding is not applied.
``turnover_penalty_lambda`` is persisted for generator reward shaping while this
function returns the unpenalized turnover separately, preserving the required
zero-cost identity ``after_cost_return == gross_return``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import pandas as pd
from pandas.tseries.frequencies import to_offset

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.base import RejectionReason
from alphamill.factor_factory.registry.run_store import ObjectiveInfo

_SIGNAL_COLUMN: Final = "signal"
_UNIVERSE_COLUMN: Final = "__in_universe__"
_BPS_DENOMINATOR: Final = 10_000.0
_FUNDING_PERIOD: Final = pd.Timedelta("8h")
_REACHABILITY_WINDOW: Final = pd.Timedelta("90d")


@dataclass(frozen=True, kw_only=True)
class CostModel:
    taker_fee_bps: float
    maker_fee_bps: float
    slippage_bps: float
    funding_8h_bps: float = 0.0


@dataclass(frozen=True, kw_only=True)
class ObjectiveParams:
    turnover_penalty_lambda: float
    reachability_min_trades_90d: int
    cost_model: CostModel
    min_after_cost_return: float


@dataclass(frozen=True, kw_only=True)
class ObjectiveResult:
    accepted: bool
    reason_code: RejectionReason | None
    turnover: float
    trades_90d: int
    gross_return: float
    after_cost_return: float
    detail: str


def _feature_columns(
    columns: tuple[str, ...],
    *,
    base_names: tuple[str, ...],
    resample: str,
) -> tuple[str, ...]:
    exact = tuple(column for column in columns if column in base_names)
    if exact:
        return exact
    suffixes = tuple(f".{name}@{resample}" for name in base_names)
    return tuple(column for column in columns if column.endswith(suffixes))


def _prepare_panel(
    signal: pd.DataFrame,
    *,
    resample: str,
) -> tuple[pd.DataFrame, pd.Timedelta, str | None]:
    if not isinstance(signal.index, pd.MultiIndex):
        raise SchemaValidationError("objective signal index must be a MultiIndex")
    if signal.empty:
        raise SchemaValidationError("objective signal panel must not be empty")
    if signal.index.nlevels != 2 or tuple(signal.index.names) != ("timestamp", "pair"):
        raise SchemaValidationError(
            "objective signal index must have levels named ('timestamp', 'pair')"
        )
    if signal.index.has_duplicates:
        raise SchemaValidationError("objective signal index must not contain duplicates")
    if _UNIVERSE_COLUMN not in signal.columns:
        raise SchemaValidationError("objective signal lacks __in_universe__")
    if _SIGNAL_COLUMN not in signal.columns:
        raise SchemaValidationError("objective signal lacks signal values")

    string_columns = tuple(column for column in signal.columns if isinstance(column, str))
    if len(string_columns) != len(signal.columns):
        raise SchemaValidationError("objective signal columns must be strings")
    close_columns = _feature_columns(
        string_columns,
        base_names=("close",),
        resample=resample,
    )
    if len(close_columns) != 1:
        raise SchemaValidationError(
            "objective signal requires one close or *.close@<resample> column"
        )
    funding_columns = _feature_columns(
        string_columns,
        base_names=("funding", "funding_rate"),
        resample=resample,
    )
    if len(funding_columns) > 1:
        raise SchemaValidationError("objective signal has ambiguous funding columns")

    try:
        interval = pd.Timedelta(to_offset(resample).nanos, unit="ns")
        signal_values = signal[_SIGNAL_COLUMN].astype(float)
        close_values = signal[close_columns[0]].astype(float)
    except (TypeError, ValueError) as exc:
        raise SchemaValidationError(
            "objective signal has invalid resample or numeric values"
        ) from exc
    if interval <= pd.Timedelta(0):
        raise SchemaValidationError("objective resample must be a positive fixed frequency")

    mask = signal[_UNIVERSE_COLUMN]
    if mask.isna().any() or not mask.isin((True, False)).all():
        raise SchemaValidationError("__in_universe__ must contain only booleans")
    in_universe = mask.astype(bool)
    observed = in_universe & signal_values.notna()
    if not observed.any():
        raise SchemaValidationError("objective signal has no in-universe signal values")
    if close_values.loc[observed].isna().any() or (close_values.loc[observed] <= 0.0).any():
        raise SchemaValidationError("in-universe signal rows require positive close values")
    if signal_values.loc[observed].isin((float("inf"), float("-inf"))).any():
        raise SchemaValidationError("objective signal values must be finite")
    if close_values.loc[observed].isin((float("inf"), float("-inf"))).any():
        raise SchemaValidationError("objective close values must be finite")

    timestamps = signal.index.get_level_values("timestamp")
    if not isinstance(timestamps, pd.DatetimeIndex) or timestamps.tz is None:
        raise SchemaValidationError("objective timestamps must be timezone-aware datetimes")
    funding_column = funding_columns[0] if funding_columns else None
    work = pd.DataFrame(
        {
            "timestamp": timestamps,
            "pair": signal.index.get_level_values("pair"),
            "position": (signal_values > 0.0).astype(float) - (signal_values < 0.0).astype(float),
            "close": close_values,
            "in_universe": in_universe,
            "observed": observed,
            "funding_available": (
                signal[funding_column].notna() if funding_column is not None else False
            ),
        }
    ).reset_index(drop=True)
    return work.sort_values(["pair", "timestamp"], kind="stable"), interval, funding_column


def evaluate_objective(
    signal: pd.DataFrame,
    *,
    params: ObjectiveParams,
    resample: str = "1h",
) -> ObjectiveResult:
    """Calculate deterministic objective pre-filter metrics for one signal panel."""
    work, interval, funding_column = _prepare_panel(signal, resample=resample)
    grouped = work.groupby("pair", sort=False)

    previous_position = grouped["position"].shift(1)
    previous_observed = grouped["observed"].shift(1).eq(True)
    previous_timestamp = grouped["timestamp"].shift(1)
    backward_consecutive = work["timestamp"].sub(previous_timestamp).eq(interval)
    transition = work["observed"] & previous_observed & backward_consecutive
    position_change = work["position"].sub(previous_position).abs().where(transition)
    turnover = float(position_change.groupby(work["timestamp"]).mean().sum())

    cutoff = work["timestamp"].max() - _REACHABILITY_WINDOW
    sign_change = work["position"].mul(previous_position).lt(0.0)
    trades_90d = int((transition & sign_change & work["timestamp"].ge(cutoff)).sum())

    next_close = grouped["close"].shift(-1)
    next_in_universe = grouped["in_universe"].shift(-1).eq(True)
    next_timestamp = grouped["timestamp"].shift(-1)
    forward_consecutive = next_timestamp.sub(work["timestamp"]).eq(interval)
    held_interval = work["observed"] & next_in_universe & forward_consecutive
    signed_return = work["position"].mul(next_close.div(work["close"]).sub(1.0))
    gross_return = float(signed_return.where(held_interval).groupby(work["timestamp"]).mean().sum())

    execution_bps = (
        params.cost_model.taker_fee_bps
        + params.cost_model.maker_fee_bps
        + params.cost_model.slippage_bps
    )
    execution_cost = turnover * execution_bps / _BPS_DENOMINATOR
    funding_cost = 0.0
    if funding_column is not None:
        funded_exposure = (
            work["position"]
            .abs()
            .where(held_interval & work["funding_available"])
            .groupby(work["timestamp"])
            .mean()
            .sum()
        )
        funding_periods = interval / _FUNDING_PERIOD
        funding_cost = (
            float(funded_exposure)
            * float(funding_periods)
            * params.cost_model.funding_8h_bps
            / _BPS_DENOMINATOR
        )
    after_cost_return = gross_return - execution_cost - funding_cost

    if trades_90d < params.reachability_min_trades_90d:
        detail = (
            f"trades_90d={trades_90d} is below configured minimum "
            f"{params.reachability_min_trades_90d}"
        )
        accepted = False
    elif after_cost_return < params.min_after_cost_return:
        detail = (
            f"after_cost_return={after_cost_return:.12g} is below configured minimum "
            f"{params.min_after_cost_return:.12g}; fixed rejection code is reachability"
        )
        accepted = False
    else:
        detail = ""
        accepted = True
    return ObjectiveResult(
        accepted=accepted,
        reason_code=None if accepted else "reachability",
        turnover=turnover,
        trades_90d=trades_90d,
        gross_return=gross_return,
        after_cost_return=after_cost_return,
        detail=detail,
    )


def objective_to_run_info(params: ObjectiveParams) -> ObjectiveInfo:
    """Project objective parameters into the GenerationRun manifest schema."""
    cost_model: dict[str, JSONValue] = {
        "taker_fee_bps": params.cost_model.taker_fee_bps,
        "maker_fee_bps": params.cost_model.maker_fee_bps,
        "slippage_bps": params.cost_model.slippage_bps,
        "funding_8h_bps": params.cost_model.funding_8h_bps,
    }
    return ObjectiveInfo(
        turnover_penalty_lambda=params.turnover_penalty_lambda,
        reachability_min_trades_90d=params.reachability_min_trades_90d,
        cost_model=cost_model,
        min_after_cost_return=params.min_after_cost_return,
    )
