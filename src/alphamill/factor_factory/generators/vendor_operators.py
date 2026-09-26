from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from alphamill.factor_factory.errors import FactorCompilationError
from alphamill.factor_factory.factor import FactorScope


def apply_unary(operand: pd.Series, operator: str) -> pd.Series:
    match operator:
        case "abs":
            return operand.abs()
        case "log":
            return pd.Series(np.log(operand), index=operand.index)
        case unreachable:
            raise FactorCompilationError(f"unknown unary operator: {unreachable!r}")


def apply_binary(lhs: pd.Series, rhs: pd.Series, operator: str) -> pd.Series:
    match operator:
        case "add":
            return lhs + rhs
        case "sub":
            return lhs - rhs
        case "mul":
            return lhs * rhs
        case "div":
            return lhs / rhs
        case "greater":
            return pd.Series(np.maximum(lhs, rhs), index=lhs.index)
        case "less":
            return pd.Series(np.minimum(lhs, rhs), index=lhs.index)
        case unreachable:
            raise FactorCompilationError(f"unknown binary operator: {unreachable!r}")


def apply_window(
    operand: pd.Series,
    operator: str,
    periods: int,
    scope: FactorScope,
) -> pd.Series:
    def apply(values: pd.Series) -> pd.Series:
        match operator:
            case "pct_change" | "return":
                return values.pct_change(periods=periods, fill_method=None)
            case "rolling_std" | "std":
                return values.rolling(window=periods, min_periods=periods).std()
            case "delta":
                return values.diff(periods)
            case "ref":
                return values.shift(periods)
            case "ema":
                return values.rolling(window=periods, min_periods=periods).apply(
                    _ema_value, raw=True
                )
            case "mad":
                return values.rolling(window=periods, min_periods=periods).apply(
                    _mad_value, raw=True
                )
            case "max":
                return values.rolling(window=periods, min_periods=periods).max()
            case "mean":
                return values.rolling(window=periods, min_periods=periods).mean()
            case "med":
                return values.rolling(window=periods, min_periods=periods).apply(
                    _med_value, raw=True
                )
            case "min":
                return values.rolling(window=periods, min_periods=periods).min()
            case "sum":
                return values.rolling(window=periods, min_periods=periods).sum()
            case "var":
                return values.rolling(window=periods, min_periods=periods).var()
            case "wma":
                return values.rolling(window=periods, min_periods=periods).apply(
                    _wma_value, raw=True
                )
            case unreachable:
                raise FactorCompilationError(f"unknown window operator: {unreachable!r}")

    return _groupwise(operand, apply, scope)


def apply_pair_window(
    lhs: pd.Series,
    rhs: pd.Series,
    operator: str,
    periods: int,
    scope: FactorScope,
) -> pd.Series:
    if scope != "cross_sectional":
        raise FactorCompilationError(f"{operator} requires cross_sectional scope")

    pieces: list[pd.Series] = []
    for _, left_values in lhs.groupby(level="pair", sort=False):
        right_values = rhs.loc[left_values.index]
        match operator:
            case "corr":
                result = _rolling_corr(left_values, right_values, periods)
            case "cov":
                result = left_values.rolling(window=periods, min_periods=periods).cov(right_values)
            case unreachable:
                raise FactorCompilationError(f"unknown pair operator: {unreachable!r}")
        pieces.append(result)
    return pd.concat(pieces).reindex(lhs.index)


def _groupwise(
    operand: pd.Series,
    function: Callable[[pd.Series], pd.Series],
    scope: FactorScope,
) -> pd.Series:
    match scope:
        case "time_series":
            return function(operand)
        case "cross_sectional":
            return operand.groupby(level="pair", sort=False, group_keys=False).transform(function)
        case unreachable:
            raise FactorCompilationError(f"unknown factor scope: {unreachable!r}")


def _mad_value(values: np.ndarray) -> float:
    return float(np.abs(values - values.mean()).mean())


def _med_value(values: np.ndarray) -> float:
    return float(np.sort(values)[(len(values) - 1) // 2])


def _rolling_corr(left: pd.Series, right: pd.Series, periods: int) -> pd.Series:
    result = np.full(len(left), np.nan, dtype=float)
    left_values = left.to_numpy(dtype=float)
    right_values = right.to_numpy(dtype=float)
    for end in range(periods - 1, len(left_values)):
        left_window = left_values[end - periods + 1 : end + 1]
        right_window = right_values[end - periods + 1 : end + 1]
        if not np.isfinite(left_window).all() or not np.isfinite(right_window).all():
            continue
        centered_left = left_window - left_window.mean()
        centered_right = right_window - right_window.mean()
        numerator = float(np.dot(centered_left, centered_right))
        left_variance = float(np.dot(centered_left, centered_left))
        right_variance = float(np.dot(centered_right, centered_right))
        denominator = float(np.sqrt(left_variance * right_variance))
        has_variance = left_variance >= 1e-6 and right_variance >= 1e-6
        result[end] = numerator / denominator if has_variance else numerator
    return pd.Series(result, index=left.index, name=left.name)


def _ema_value(values: np.ndarray) -> float:
    periods = len(values)
    alpha = 1.0 - 2.0 / (1.0 + periods)
    weights = alpha ** np.arange(periods, 0, -1, dtype=float)
    total = weights.sum()
    return float(np.dot(weights, values) / total) if total else float("nan")


def _wma_value(values: np.ndarray) -> float:
    weights = np.arange(len(values), dtype=float)
    total = weights.sum()
    return float(np.dot(weights, values) / total) if total else float("nan")
