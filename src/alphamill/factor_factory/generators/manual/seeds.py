from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from types import MappingProxyType
from typing import Final

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.factor import FactorScope
from alphamill.factor_factory.generators.base import (
    GenerationCounts,
    GenerationRequest,
    GenerationResult,
    RejectionCounts,
)
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG, HypothesisCatalog
from alphamill.factor_factory.registry.compiler_registry import DEFAULT_COMPILERS, CompilerRegistry
from alphamill.factor_factory.registry.factor_store import build_factor

MANUAL_GENERATOR_VERSION = "manual-v1"
MANUAL_FACTOR_ORDER: tuple[str, ...] = (
    "funding_carry",
    "basis_reversion",
    "open_interest_change",
    "cross_sectional_momentum",
    "realized_volatility",
)


@dataclass(frozen=True, slots=True)
class _ManualSeed:
    expression: tuple[str, ...]
    scope: FactorScope


_FEATURE_MAP: Final[Mapping[str, int]] = MappingProxyType(
    {"close": 0, "funding_rate": 1, "basis_pct": 2, "open_interest": 3}
)
_SEEDS: Final[Mapping[str, _ManualSeed]] = MappingProxyType(
    {
        "funding_carry": _ManualSeed(
            expression=("feature:funding_rate", "neg"),
            scope="time_series",
        ),
        "basis_reversion": _ManualSeed(
            expression=("feature:basis_pct", "neg"),
            scope="time_series",
        ),
        "open_interest_change": _ManualSeed(
            expression=("feature:open_interest", "pct_change:24"),
            scope="time_series",
        ),
        "cross_sectional_momentum": _ManualSeed(
            expression=("feature:close", "return:168", "cs_rank"),
            scope="cross_sectional",
        ),
        "realized_volatility": _ManualSeed(
            expression=("feature:close", "return:1", "rolling_std:168", "neg"),
            scope="time_series",
        ),
    }
)


class ManualGenerator:
    """Produce fixed crypto-native seeds without data-dependent selection.

    Cross-sectional momentum alone uses ``cross_sectional`` scope because ``cs_rank``
    ranks within each timestamp's PIT universe. The remaining expressions contain only
    per-pair time-series operations, so they use ``time_series`` scope.
    """

    name = "manual"

    def __init__(
        self,
        *,
        run_id: str,
        catalog: HypothesisCatalog = DEFAULT_CATALOG,
        clock: Callable[[], datetime] | None = None,
        compilers: CompilerRegistry = DEFAULT_COMPILERS,
    ) -> None:
        """Configure run provenance and injectable catalog/compiler dependencies."""
        self._run_id = run_id
        self._catalog = catalog
        self._clock = clock or (lambda: datetime.now(UTC))
        self._compilers = compilers

    def produce(self, request: GenerationRequest) -> GenerationResult:
        """Build the quota-limited prefix of the fixed manual seed definitions."""
        if request.generator != self.name:
            raise SchemaValidationError(
                f"ManualGenerator requires generator={self.name!r}, got {request.generator!r}"
            )

        created_at = self._clock()
        factors = [
            build_factor(
                hypothesis=self._catalog.require(hypothesis_id),
                name=hypothesis_id,
                generator=self.name,
                generator_version=MANUAL_GENERATOR_VERSION,
                scope=_SEEDS[hypothesis_id].scope,
                expression=_SEEDS[hypothesis_id].expression,
                params={},
                feature_map=_FEATURE_MAP,
                run_id=self._run_id,
                created_at=created_at,
                compilers=self._compilers,
            )
            for hypothesis_id in MANUAL_FACTOR_ORDER[: request.quota]
        ]
        count = len(factors)
        return GenerationResult(
            run_id=self._run_id,
            factors=factors,
            pool=None,
            counts=GenerationCounts(
                proposed=count,
                rejected=RejectionCounts(),
                registered=count,
            ),
            device="cpu",
            tier_level="manual",
        )
