"""F003 可插拔生成器的共享类型与边界校验。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Literal, Protocol, TypeAlias

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import ConclusionFieldError, SchemaValidationError
from alphamill.factor_factory.factor import FactorDef

if TYPE_CHECKING:
    from alphamill.factor_factory.generators.binding import SnapshotBinding

Expression: TypeAlias = tuple[str, ...]
RejectionReason: TypeAlias = Literal[
    "unregistered_op", "lookahead", "reachability", "duplicate_definition"
]

CONCLUSION_FIELDS: frozenset[str] = frozenset(
    {
        "ic",
        "rank_ic",
        "pnl",
        "verdict",
        "promoted",
        "cost_verdict",
        "promotion_verdict",
    }
)
DEFAULT_WINDOW_PRESET = "default_1h_2y"
DEFAULT_SEED_QUOTA = 5


@dataclass(frozen=True)
class Window:
    """UTC generation window with an inclusive start and exclusive end."""

    start: datetime
    end: datetime
    resample: str

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.start.utcoffset() != UTC.utcoffset(self.start):
            raise SchemaValidationError("Window.start must be timezone-aware UTC")
        if self.end.tzinfo is None or self.end.utcoffset() != UTC.utcoffset(self.end):
            raise SchemaValidationError("Window.end must be timezone-aware UTC")
        if self.start >= self.end:
            raise SchemaValidationError("Window.start must be earlier than Window.end")
        if self.resample != "1h":
            raise SchemaValidationError("Window.resample must be '1h' in Phase 1")

    @classmethod
    def from_preset(cls, name: str, *, cutoff_time: datetime) -> Window:
        if name != DEFAULT_WINDOW_PRESET:
            raise SchemaValidationError(f"Window preset is unknown: {name!r}")
        return cls(
            start=cutoff_time - timedelta(days=730),
            end=cutoff_time,
            resample="1h",
        )


@dataclass(frozen=True)
class RejectionCounts:
    unregistered_op: int = 0
    lookahead: int = 0
    reachability: int = 0
    duplicate_definition: int = 0


@dataclass(frozen=True)
class GenerationCounts:
    proposed: int
    rejected: RejectionCounts
    registered: int

    def __post_init__(self) -> None:
        values = (
            self.proposed,
            self.rejected.unregistered_op,
            self.rejected.lookahead,
            self.rejected.reachability,
            self.rejected.duplicate_definition,
            self.registered,
        )
        if any(
            not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values
        ):
            raise SchemaValidationError("GenerationCounts values must be non-negative integers")

        rejected_total = sum(
            (
                self.rejected.unregistered_op,
                self.rejected.lookahead,
                self.rejected.reachability,
                self.rejected.duplicate_definition,
            )
        )
        if self.proposed != self.registered + rejected_total:
            raise SchemaValidationError(
                "GenerationCounts.proposed must equal registered plus rejected counts"
            )


@dataclass(frozen=True)
class GenerationRequest:
    generator: str
    binding: SnapshotBinding
    seed: int
    window: Window
    config: Mapping[str, JSONValue]
    quota: int

    def __post_init__(self) -> None:
        if self.quota < 1:
            raise SchemaValidationError("GenerationRequest.quota must be at least 1")


@dataclass(frozen=True)
class GenerationResult:
    run_id: str
    factors: list[FactorDef]
    pool: FactorDef | None
    counts: GenerationCounts
    device: str
    tier_level: str

    def __post_init__(self) -> None:
        for index, factor in enumerate(self.factors):
            reject_conclusion_fields(
                vars(factor),
                context=f"GenerationResult.factors[{index}]",
            )
        if self.pool is not None:
            reject_conclusion_fields(vars(self.pool), context="GenerationResult.pool")
            if self.pool.generator != "pool":
                raise SchemaValidationError("GenerationResult.pool must use generator='pool'")


class Generator(Protocol):
    """Structural contract implemented by every generation backend."""

    name: str

    def produce(self, request: GenerationRequest) -> GenerationResult: ...


def reject_conclusion_fields(payload: Mapping[str, object], *, context: str) -> None:
    """Reject evaluation conclusions anywhere inside a payload, at any depth.

    Top-level-only screening cannot fire on a real backend result: both
    ``GenerationResult`` and ``FactorDef`` are frozen dataclasses whose field
    names are fixed, so no backend can add an ``ic`` attribute to them. The only
    surfaces that can carry a conclusion are the free-form ``params`` and
    ``meta`` mappings — which is exactly what this walk covers (FR-001, AC-001;
    evaluation authority is F007 alone, ADR-0003).
    """
    offending = sorted(_conclusion_keys(payload))
    if offending:
        fields = ", ".join(offending)
        raise ConclusionFieldError(f"{context}: conclusion fields are forbidden: {fields}")


def _conclusion_keys(value: object) -> set[str]:
    """Collect forbidden keys from nested JSON-shaped mappings and sequences."""
    if isinstance(value, Mapping):
        found = set(CONCLUSION_FIELDS.intersection(value))
        for item in value.values():
            found |= _conclusion_keys(item)
        return found
    if isinstance(value, (list, tuple)):
        return set().union(*(_conclusion_keys(item) for item in value)) if value else set()
    return set()
