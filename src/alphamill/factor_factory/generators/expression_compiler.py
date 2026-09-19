from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC
from typing import Literal, Protocol, assert_never

import pandas as pd
from pandas.api.types import is_bool_dtype

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import FactorCompilationError
from alphamill.factor_factory.factor import FactorCompute, FactorResolver, FactorScope
from alphamill.factor_factory.generators.operator_registry import (
    OPERATOR_ARITIES,
    OPERATOR_REGISTRY,
)
from alphamill.factor_factory.generators.vendor_operators import (
    apply_binary,
    apply_pair_window,
    apply_unary,
    apply_window,
)

_FEATURE_PREFIX = "feature:"
_CONSTANT_PREFIX = "constant:"
_WINDOW_OPERATORS = frozenset(
    {
        "delta",
        "ema",
        "mad",
        "max",
        "mean",
        "med",
        "min",
        "pct_change",
        "ref",
        "return",
        "rolling_std",
        "std",
        "sum",
        "var",
        "wma",
    }
)
_UNARY_OPERATORS = frozenset({"abs", "log"})
_BINARY_OPERATORS = frozenset({"add", "div", "greater", "less", "mul", "sub"})
_PAIR_OPERATORS = frozenset({"corr", "cov"})


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
class _Constant:
    value: float


@dataclass(frozen=True, slots=True)
class _Neg:
    pass


@dataclass(frozen=True, slots=True)
class _Unary:
    operator: str


@dataclass(frozen=True, slots=True)
class _Binary:
    operator: str


@dataclass(frozen=True, slots=True)
class _Window:
    operator: str
    periods: int


@dataclass(frozen=True, slots=True)
class _PairWindow:
    operator: Literal["corr", "cov"]
    periods: int


@dataclass(frozen=True, slots=True)
class _CrossSectionalRank:
    pass


_Operation = (
    _Feature | _Constant | _Neg | _Unary | _Binary | _Window | _PairWindow | _CrossSectionalRank
)


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
                case _Constant(value=value):
                    stack.append(pd.Series(value, index=frame.index, dtype=float))
                case _Neg():
                    stack.append(-stack.pop())
                case _Unary(operator=operator):
                    stack.append(apply_unary(stack.pop(), operator))
                case _Binary(operator=operator):
                    rhs = stack.pop()
                    lhs = stack.pop()
                    stack.append(apply_binary(lhs, rhs, operator))
                case _Window(operator=operator, periods=periods):
                    stack.append(apply_window(stack.pop(), operator, periods, context.scope))
                case _PairWindow(operator=operator, periods=periods):
                    rhs = stack.pop()
                    lhs = stack.pop()
                    if universe is not None:
                        lhs = lhs.where(universe)
                        rhs = rhs.where(universe)
                    stack.append(apply_pair_window(lhs, rhs, operator, periods, context.scope))
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
        if token == _CONSTANT_PREFIX[:-1] or token.startswith(_CONSTANT_PREFIX):
            operations.append(_Constant(_parse_constant(token)))
            depth += 1
            continue
        operator, separator, argument = token.partition(":")
        if operator == "constant":
            raise FactorCompilationError(f"malformed constant token: {token!r}")
        if operator not in OPERATOR_REGISTRY:
            raise FactorCompilationError(f"unknown expression token: {token!r}")
        arity = OPERATOR_ARITIES[operator]
        if depth < arity:
            raise FactorCompilationError(f"postfix stack underflow at token: {token!r}")
        if operator == "neg":
            if separator:
                raise FactorCompilationError(f"operator does not accept a window: {token!r}")
            operations.append(_Neg())
        elif operator == "cs_rank":
            if separator:
                raise FactorCompilationError(f"operator does not accept a window: {token!r}")
            if context.scope != "cross_sectional":
                raise FactorCompilationError("cs_rank requires cross_sectional scope")
            operations.append(_CrossSectionalRank())
        elif operator in _UNARY_OPERATORS:
            if separator:
                raise FactorCompilationError(f"operator does not accept a window: {token!r}")
            operations.append(_Unary(operator))
        elif operator in _BINARY_OPERATORS:
            if separator:
                raise FactorCompilationError(f"operator does not accept a window: {token!r}")
            operations.append(_Binary(operator))
        elif operator in _WINDOW_OPERATORS or operator in _PAIR_OPERATORS:
            periods = _parse_periods(token, argument if separator else None)
            if operator in _PAIR_OPERATORS:
                if context.scope != "cross_sectional":
                    raise FactorCompilationError(f"{operator} requires cross_sectional scope")
                operations.append(_PairWindow(operator=operator, periods=periods))
            else:
                operations.append(_Window(operator=operator, periods=periods))
        else:
            raise FactorCompilationError(f"unsupported registered operator: {operator!r}")
        depth = depth - arity + 1
    if depth != 1:
        raise FactorCompilationError(f"postfix expression leaves {depth} stack values")
    return tuple(operations)


def _parse_constant(token: str) -> float:
    value = token.removeprefix(_CONSTANT_PREFIX)
    if not value or ":" in value:
        raise FactorCompilationError(f"malformed constant token: {token!r}")
    try:
        parsed = float(value)
    except ValueError as error:
        raise FactorCompilationError(f"malformed constant token: {token!r}") from error
    if not math.isfinite(parsed):
        raise FactorCompilationError(f"malformed constant token: {token!r}")
    return parsed


def _parse_periods(token: str, argument: str | None) -> int:
    if argument is None or not argument.isascii() or not argument.isdecimal():
        raise FactorCompilationError(f"malformed window token: {token!r}")
    periods = int(argument)
    if periods < 1:
        raise FactorCompilationError(f"malformed window token: {token!r}")
    return periods


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
