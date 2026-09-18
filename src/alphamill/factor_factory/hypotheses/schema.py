from dataclasses import dataclass
from typing import Final, Literal, TypeAlias

from alphamill.factor_factory.errors import SchemaValidationError

CostSensitivity: TypeAlias = Literal["low", "medium", "high", "unknown"]

_COST_SENSITIVITIES: Final = frozenset({"low", "medium", "high", "unknown"})


@dataclass(frozen=True, kw_only=True)
class HypothesisDef:
    """Validated economic hypothesis metadata."""

    hypothesis_id: str
    mechanism: str
    data_columns: tuple[str, ...]
    expected_holding_period: str
    cost_sensitivity: CostSensitivity
    source: str
    generation: int
    applicable_state: str = "unspecified"

    def __post_init__(self) -> None:
        string_fields = (
            ("hypothesis_id", self.hypothesis_id),
            ("mechanism", self.mechanism),
            ("expected_holding_period", self.expected_holding_period),
            ("source", self.source),
            ("applicable_state", self.applicable_state),
        )
        for field_name, value in string_fields:
            if not value.strip():
                raise SchemaValidationError(f"HypothesisDef.{field_name} must be non-empty")

        if any(not column.strip() for column in self.data_columns):
            raise SchemaValidationError("HypothesisDef.data_columns must contain non-empty names")
        if len(set(self.data_columns)) != len(self.data_columns):
            raise SchemaValidationError("HypothesisDef.data_columns must be unique")
        if self.generation < 0:
            raise SchemaValidationError("HypothesisDef.generation must be non-negative")
        if self.cost_sensitivity not in _COST_SENSITIVITIES:
            raise SchemaValidationError(
                "HypothesisDef.cost_sensitivity must be low, medium, high, or unknown"
            )
