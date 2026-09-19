"""Phase-1 expression operator capabilities for F003 and downstream consumers.

``feature:<column>`` is a feature reference resolved by the expression compiler,
not an operator, so it is intentionally absent from this registry.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Literal, TypeAlias

from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    sha256_prefixed_bytes,
)
from alphamill.factor_factory.errors import SchemaValidationError

REGISTRY_SCHEMA_VERSION: Final[int] = 1
OperatorKind: TypeAlias = Literal["time_series", "cross_sectional"]
DELTAS: Final[tuple[int, ...]] = (1, 5, 10, 20, 40)


@dataclass(frozen=True, slots=True, kw_only=True)
class OperatorSpec:
    """Describe one enabled operator and its minimum window requirement."""

    name: str
    kind: OperatorKind
    window_bars: int | None
    window_parameter: str | None
    description: str


_VENDOR_OPERATOR_ROWS: Final[tuple[tuple[str, OperatorKind, int | None, str | None, str], ...]] = (
    ("abs", "time_series", None, None, "Take the element-wise absolute value."),
    ("add", "time_series", None, None, "Add two operands element by element."),
    (
        "corr",
        "cross_sectional",
        1,
        "bars",
        "Compute rolling pair correlation within each cross-sectional panel.",
    ),
    (
        "cov",
        "cross_sectional",
        1,
        "bars",
        "Compute rolling pair covariance within each cross-sectional panel.",
    ),
    (
        "delta",
        "time_series",
        1,
        "bars",
        "Subtract the value lagged by the requested number of bars.",
    ),
    ("div", "time_series", None, None, "Divide two operands element by element."),
    (
        "ema",
        "time_series",
        1,
        "bars",
        "Compute the vendor's finite trailing weighted exponential mean.",
    ),
    ("greater", "time_series", None, None, "Take the element-wise maximum of two operands."),
    ("less", "time_series", None, None, "Take the element-wise minimum of two operands."),
    ("log", "time_series", None, None, "Take the element-wise natural logarithm."),
    ("mad", "time_series", 1, "bars", "Compute mean absolute deviation over a trailing window."),
    ("max", "time_series", 1, "bars", "Compute the maximum over a trailing window."),
    ("mean", "time_series", 1, "bars", "Compute the mean over a trailing window."),
    ("med", "time_series", 1, "bars", "Compute the median over a trailing window."),
    ("min", "time_series", 1, "bars", "Compute the minimum over a trailing window."),
    ("mul", "time_series", None, None, "Multiply two operands element by element."),
    ("ref", "time_series", 1, "bars", "Reference the value at the requested lag."),
    ("std", "time_series", 1, "bars", "Compute sample standard deviation over a trailing window."),
    ("sub", "time_series", None, None, "Subtract two operands element by element."),
    ("sum", "time_series", 1, "bars", "Compute the sum over a trailing window."),
    ("var", "time_series", 1, "bars", "Compute sample variance over a trailing window."),
    ("wma", "time_series", 1, "bars", "Compute the vendor's finite trailing weighted mean."),
)

_VENDOR_OPERATOR_SPECS: Final[tuple[OperatorSpec, ...]] = tuple(
    OperatorSpec(
        name=name,
        kind=kind,
        window_bars=window_bars,
        window_parameter=window_parameter,
        description=description,
    )
    for name, kind, window_bars, window_parameter, description in _VENDOR_OPERATOR_ROWS
)


_OPERATOR_SPECS: Final[tuple[OperatorSpec, ...]] = (
    OperatorSpec(
        name="cs_rank",
        kind="cross_sectional",
        window_bars=None,
        window_parameter=None,
        description="Rank values within each timestamp's point-in-time universe.",
    ),
    OperatorSpec(
        name="neg",
        kind="time_series",
        window_bars=None,
        window_parameter=None,
        description="Negate each value without changing the observation window.",
    ),
    OperatorSpec(
        name="pct_change",
        kind="time_series",
        window_bars=1,
        window_parameter="bars",
        description="Compute percentage change over a caller-supplied window of at least one bar.",
    ),
    OperatorSpec(
        name="return",
        kind="time_series",
        window_bars=1,
        window_parameter="bars",
        description="Compute return over a caller-supplied window of at least one bar.",
    ),
    OperatorSpec(
        name="rolling_std",
        kind="time_series",
        window_bars=1,
        window_parameter="bars",
        description="Compute rolling standard deviation over a window of at least one bar.",
    ),
    *_VENDOR_OPERATOR_SPECS,
)

OPERATOR_REGISTRY: Final[Mapping[str, OperatorSpec]] = MappingProxyType(
    {spec.name: spec for spec in _OPERATOR_SPECS}
)

OPERATOR_ARITIES: Final[Mapping[str, int]] = MappingProxyType(
    {
        **{name: 1 for name in ("cs_rank", "neg", "pct_change", "return", "rolling_std")},
        **{
            name: 1
            for name in (
                "abs",
                "delta",
                "ema",
                "log",
                "mad",
                "max",
                "mean",
                "med",
                "min",
                "ref",
                "std",
                "sum",
                "var",
                "wma",
            )
        },
        **{name: 2 for name in ("add", "corr", "cov", "div", "greater", "less", "mul", "sub")},
    }
)

_RESAMPLE_MINUTES: Final[Mapping[str, int]] = MappingProxyType(
    {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1d": 1_440,
    }
)


def require_operator(name: str) -> OperatorSpec:
    """Return an enabled operator or reject the unknown capability name."""
    spec = OPERATOR_REGISTRY.get(name)
    if spec is None:
        raise SchemaValidationError(f"operator is not registered: {name!r}")
    return spec


def enabled_operators() -> tuple[OperatorSpec, ...]:
    """Return enabled operators in stable declaration order."""
    return _OPERATOR_SPECS


def window_to_duration(bars: int, resample: str) -> str:
    """Convert crypto bars exactly, using hours when integral and minutes otherwise."""
    if bars < 1:
        raise SchemaValidationError(f"bars must be at least 1, got {bars!r}")
    minutes_per_bar = _RESAMPLE_MINUTES.get(resample)
    if minutes_per_bar is None:
        raise SchemaValidationError(f"unsupported resample: {resample!r}")

    total_minutes = bars * minutes_per_bar
    hours, remaining_minutes = divmod(total_minutes, 60)
    if remaining_minutes == 0:
        return f"{hours}h"
    return f"{total_minutes}m"


def capability_manifest() -> dict[str, JSONValue]:
    """Build the deterministic, versioned operator capability manifest for F007."""
    operators: list[JSONValue] = [
        {
            "name": spec.name,
            "kind": spec.kind,
            "window_bars": spec.window_bars,
            "window_parameter": spec.window_parameter,
            "description": spec.description,
        }
        for spec in enabled_operators()
    ]
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "operators": operators,
    }


def manifest_digest() -> str:
    """Return the canonical ``sha256:`` digest of the current capability manifest."""
    return sha256_prefixed_bytes(canonical_json_bytes(capability_manifest()))
