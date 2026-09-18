from collections.abc import Iterable

from alphamill.factor_factory.errors import SchemaValidationError, UnknownHypothesisError
from alphamill.factor_factory.hypotheses.schema import HypothesisDef

MECHANISM_UNKNOWN_ID = "mechanism_unknown"


class HypothesisCatalog:
    def __init__(self, entries: Iterable[HypothesisDef] = ()) -> None:
        self._entries: dict[str, HypothesisDef] = {}
        for entry in entries:
            self.register(entry)

    def register(self, hypothesis: HypothesisDef) -> None:
        hypothesis_id = hypothesis.hypothesis_id
        if hypothesis_id in self._entries:
            raise SchemaValidationError(f"duplicate hypothesis_id: {hypothesis_id!r}")
        self._entries[hypothesis_id] = hypothesis

    def require(self, hypothesis_id: str) -> HypothesisDef:
        if hypothesis_id not in self._entries:
            raise UnknownHypothesisError(f"unknown hypothesis_id: {hypothesis_id!r}")
        return self._entries[hypothesis_id]

    def all(self) -> tuple[HypothesisDef, ...]:
        return tuple(self._entries.values())


def builtin_catalog() -> HypothesisCatalog:
    return HypothesisCatalog(
        (
            HypothesisDef(
                hypothesis_id=MECHANISM_UNKNOWN_ID,
                mechanism=(
                    "Mechanism not yet articulated for an automatically-proposed candidate."
                ),
                data_columns=(),
                expected_holding_period="unspecified",
                cost_sensitivity="unknown",
                source="system",
                generation=0,
                applicable_state="unspecified",
            ),
            HypothesisDef(
                hypothesis_id="funding_carry",
                mechanism=(
                    "Persistent funding payments transfer value between crowded perpetual "
                    "positions and their counterparties."
                ),
                data_columns=("funding_rate",),
                expected_holding_period="8 hours to 3 days",
                cost_sensitivity="medium",
                source="manual_seed",
                generation=1,
                applicable_state="active perpetual funding market",
            ),
            HypothesisDef(
                hypothesis_id="basis_reversion",
                mechanism=(
                    "Large perpetual-to-spot basis dislocations attract arbitrage capital and "
                    "revert toward carrying cost."
                ),
                data_columns=("basis_pct",),
                expected_holding_period="1 to 7 days",
                cost_sensitivity="medium",
                source="manual_seed",
                generation=1,
                applicable_state="liquid spot and perpetual markets",
            ),
            HypothesisDef(
                hypothesis_id="open_interest_change",
                mechanism=(
                    "Changes in open interest reveal leverage entering or leaving the market and "
                    "foreshadow position unwinds."
                ),
                data_columns=("open_interest",),
                expected_holding_period="4 hours to 2 days",
                cost_sensitivity="high",
                source="manual_seed",
                generation=1,
                applicable_state="active derivatives positioning",
            ),
            HypothesisDef(
                hypothesis_id="cross_sectional_momentum",
                mechanism=(
                    "Relative crypto returns persist while information and capital diffuse "
                    "unevenly across assets."
                ),
                data_columns=("close",),
                expected_holding_period="1 to 7 days",
                cost_sensitivity="high",
                source="manual_seed",
                generation=1,
                applicable_state="broad liquid cross-section",
            ),
            HypothesisDef(
                hypothesis_id="realized_volatility",
                mechanism=(
                    "Volatility clusters because leverage adjustments and liquidations propagate "
                    "across consecutive trading intervals."
                ),
                data_columns=("close",),
                expected_holding_period="1 to 5 days",
                cost_sensitivity="low",
                source="manual_seed",
                generation=1,
                applicable_state="continuous liquid trading",
            ),
        )
    )


DEFAULT_CATALOG: HypothesisCatalog = builtin_catalog()
