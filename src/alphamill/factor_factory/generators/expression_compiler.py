from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from typing import Literal, Protocol, assert_never

import pandas as pd
from pandas.api.types import is_bool_dtype

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import FactorCompilationError
from alphamill.factor_factory.factor import FactorCompute, FactorResolver, FactorScope

_FEATURE_PREFIX = "feature:"
_WINDOW_OPERATORS = frozenset({"pct_change", "return", "rolling_std"})


class CompileContext(Protocol):
    generator: str
    expression: tuple[str, ...]
    scope: FactorScope
    params: Mapping[str, JSONValue]
    data_columns: tuple[str, ...]
    feature_map: Mapping[str, int]
    resolver: FactorResolver | None


@dataclass(frozen=True, slots=True)
class _Feature:
    name: str


@dataclass(frozen=True, slots=True)
class _Neg:
    pass


@dataclass(frozen=True, slots=True)
class _Window:
    operator: Literal["pct_change", "return", "rolling_std"]
    periods: int


@dataclass(frozen=True, slots=True)
class _CrossSectionalRank:
    pass


_Operation = _Feature | _Neg | _Window | _CrossSectionalRank


def referenced_features(expression: tuple[str, ...]) -> tuple[str, ...]:
    """Return feature names in first-appearance order."""
    features: list[str] = []
    for token in expression:
        if not isinstance(token, str):
            raise FactorCompilationError(f"expression token must be a string: {token!r}")
        if token.startswith(_FEATURE_PREFIX):
            feature = token.removeprefix(_FEATURE_PREFIX)
            if not feature.strip():
                raise FactorCompilationError(f"malformed feature token: {token!r}")
            if feature not in features:
                features.append(feature)
    return tuple(features)


def compile_postfix(context: CompileContext) -> FactorCompute:
    """Compile a validated postfix token sequence without executing arbitrary code."""
    operations = _parse_operations(context)

    def compute(frame: pd.DataFrame) -> pd.Series:
        _validate_frame(frame, context)
        stack: list[pd.Series] = []
        universe = _universe_mask(frame, context.scope)
        for operation in operations:
            match operation:
                case _Feature(name=name):
                    stack.append(frame[name].astype(float))
                case _Neg():
                    stack.append(-stack.pop())
                case _Window(operator=operator, periods=periods):
                    operand = stack.pop()
                    stack.append(_apply_window(operand, operator, periods, context.scope))
                case _CrossSectionalRank():
                    operand = stack.pop().where(universe)
                    stack.append(operand.groupby(level="timestamp", sort=False).rank(pct=True))
                case unreachable:
                    assert_never(unreachable)
        result = stack[0].astype(float)
        return result.where(universe) if universe is not None else result

    return compute


def _parse_operations(context: CompileContext) -> tuple[_Operation, ...]:
    features = referenced_features(context.expression)
    missing = tuple(feature for feature in features if feature not in context.feature_map)
    if missing:
        raise FactorCompilationError(f"features absent from feature_map: {missing!r}")

    operations: list[_Operation] = []
    depth = 0
    for token in context.expression:
        if token.startswith(_FEATURE_PREFIX):
            operations.append(_Feature(token.removeprefix(_FEATURE_PREFIX)))
            depth += 1
            continue
        if depth < 1:
            raise FactorCompilationError(f"postfix stack underflow at token: {token!r}")
        if token == "neg":
            operations.append(_Neg())
            continue
        if token == "cs_rank":
            if context.scope != "cross_sectional":
                raise FactorCompilationError("cs_rank requires cross_sectional scope")
            operations.append(_CrossSectionalRank())
            continue
        operator, separator, argument = token.partition(":")
        if separator and operator in _WINDOW_OPERATORS:
            if not argument.isdecimal() or int(argument) < 1:
                raise FactorCompilationError(f"malformed window token: {token!r}")
            operations.append(_Window(operator=operator, periods=int(argument)))
            continue
        raise FactorCompilationError(f"unknown expression token: {token!r}")
    if depth != 1:
        raise FactorCompilationError(f"postfix expression leaves {depth} stack values")
    return tuple(operations)


def _validate_frame(frame: pd.DataFrame, context: CompileContext) -> None:
    missing = tuple(column for column in context.data_columns if column not in frame.columns)
    if missing:
        raise FactorCompilationError(f"input frame is missing columns: {missing!r}")
    match context.scope:
        case "time_series":
            if not isinstance(frame.index, pd.DatetimeIndex) or frame.index.tz != UTC:
                raise FactorCompilationError("time_series input requires a UTC DatetimeIndex")
        case "cross_sectional":
            valid_index = isinstance(frame.index, pd.MultiIndex) and tuple(frame.index.names) == (
                "timestamp",
                "pair",
            )
            if not valid_index:
                raise FactorCompilationError(
                    "cross_sectional input requires MultiIndex names ('timestamp', 'pair')"
                )
            timestamps = frame.index.get_level_values("timestamp")
            if not isinstance(timestamps, pd.DatetimeIndex) or timestamps.tz != UTC:
                raise FactorCompilationError("cross_sectional timestamp level must be UTC")
            if "__in_universe__" not in frame or not is_bool_dtype(frame["__in_universe__"]):
                raise FactorCompilationError(
                    "cross_sectional input requires boolean __in_universe__ column"
                )
        case unreachable:
            assert_never(unreachable)


def _universe_mask(frame: pd.DataFrame, scope: FactorScope) -> pd.Series | None:
    match scope:
        case "time_series":
            return None
        case "cross_sectional":
            return frame["__in_universe__"]
        case unreachable:
            assert_never(unreachable)


def _apply_window(
    operand: pd.Series,
    operator: Literal["pct_change", "return", "rolling_std"],
    periods: int,
    scope: FactorScope,
) -> pd.Series:
    def apply(values: pd.Series) -> pd.Series:
        match operator:
            case "pct_change" | "return":
                return values.pct_change(periods=periods, fill_method=None)
            case "rolling_std":
                return values.rolling(window=periods, min_periods=periods).std()
            case unreachable:
                assert_never(unreachable)

    match scope:
        case "time_series":
            return apply(operand)
        case "cross_sectional":
            return operand.groupby(level="pair", sort=False).transform(apply)
        case unreachable:
            assert_never(unreachable)
