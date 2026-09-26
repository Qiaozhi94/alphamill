"""Strict FactorDef persistence schema, canonical identity, and JSON boundary parsing."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Final

from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    parse_utc,
    sha256_hex,
    sha256_prefixed_bytes,
    utc_iso,
)
from alphamill.factor_factory.errors import (
    FeatureMapIntegrityError,
    SchemaValidationError,
    UnknownSchemaVersionError,
)
from alphamill.factor_factory.factor import FactorScope
from alphamill.factor_factory.generators.expression_compiler import referenced_features

FACTOR_SCHEMA_VERSION: Final = 1
FACTOR_IDENTITY_EXCLUDED_FIELDS: Final[frozenset[str]] = frozenset(
    {"factor_id", "definition_digest", "run_id", "created_at"}
)


@dataclass(frozen=True, kw_only=True)
class FeatureMapDTO:
    """Versioned feature-name to channel mapping stored by content digest."""

    schema_version: int
    features: dict[str, int]


@dataclass(frozen=True, kw_only=True)
class FactorDefDTO:
    """Strict persisted representation of an executable FactorDef."""

    schema_version: int
    factor_id: str
    definition_digest: str
    hypothesis_id: str
    name: str
    generator: str
    generator_version: str
    scope: FactorScope
    expression: tuple[str, ...]
    params: dict[str, JSONValue]
    data_columns: tuple[str, ...]
    feature_map_digest: str
    run_id: str
    created_at: datetime


FACTOR_DTO_FIELDS: Final[frozenset[str]] = frozenset(FactorDefDTO.__annotations__)


def feature_map_digest(feature_map: Mapping[str, int]) -> str:
    """Return the canonical digest of a contiguous, unique feature map."""
    features = dict(feature_map)
    channels = tuple(features.values())
    if (
        any(not isinstance(name, str) or not name.strip() for name in features)
        or any(not isinstance(channel, int) or isinstance(channel, bool) for channel in channels)
        or len(set(channels)) != len(channels)
        or set(channels) != set(range(len(channels)))
    ):
        raise FeatureMapIntegrityError("feature_map names and channels are invalid")
    payload: JSONValue = {
        "schema_version": FACTOR_SCHEMA_VERSION,
        "features": dict(sorted(features.items())),
    }
    return sha256_prefixed_bytes(canonical_json_bytes(payload))


def definition_digest(dto: FactorDefDTO) -> str:
    """Hash the canonical DTO identity projection."""
    payload = _factor_dto_payload(dto)
    return sha256_hex(
        {key: value for key, value in payload.items() if key not in FACTOR_IDENTITY_EXCLUDED_FIELDS}
    )


def _factor_dto_payload(dto: FactorDefDTO) -> dict[str, JSONValue]:
    payload = asdict(dto)
    payload.update(expression=list(dto.expression), data_columns=list(dto.data_columns))
    payload["created_at"] = utc_iso(dto.created_at)
    return payload


def _parse_factor_dto(payload: dict[str, JSONValue]) -> FactorDefDTO:
    if set(payload) != FACTOR_DTO_FIELDS:
        raise SchemaValidationError("FactorDefDTO fields must match the exact schema")
    if not isinstance(payload["expression"], list) or not isinstance(payload["params"], dict):
        raise SchemaValidationError("expression must be a list and params must be an object")
    if not isinstance(payload["data_columns"], list):
        raise SchemaValidationError("data_columns must be a list")
    created_at = payload["created_at"] if isinstance(payload["created_at"], str) else ""
    values = dict(payload)
    values.update(
        schema_version=_schema_version(payload["schema_version"]),
        expression=tuple(payload["expression"]),
        params=dict(payload["params"]),
        data_columns=tuple(payload["data_columns"]),
        created_at=parse_utc(created_at, field="created_at"),
    )
    dto = FactorDefDTO(**values)
    _validate_factor_dto(dto)
    return dto


def _parse_feature_map(payload: dict[str, JSONValue]) -> FeatureMapDTO:
    if set(payload) != {"schema_version", "features"}:
        raise SchemaValidationError("FeatureMapDTO fields must match the exact schema")
    if not isinstance(payload["features"], dict):
        raise FeatureMapIntegrityError("FeatureMapDTO.features must be an object")
    dto = FeatureMapDTO(
        schema_version=_schema_version(payload["schema_version"]),
        features=dict(payload["features"]),
    )
    feature_map_digest(dto.features)
    return dto


def _validate_factor_dto(dto: FactorDefDTO) -> None:
    _schema_version(dto.schema_version)
    if dto.scope not in ("time_series", "cross_sectional"):
        raise SchemaValidationError("FactorDefDTO scope is invalid")
    _digest_hex(dto.feature_map_digest)
    if dto.definition_digest != definition_digest(dto):
        raise SchemaValidationError("definition_digest does not match the identity payload")
    if dto.factor_id != f"{dto.generator}_{dto.definition_digest[:12]}":
        raise SchemaValidationError("factor_id is inconsistent with generator and digest")
    if dto.data_columns != referenced_features(dto.expression):
        raise SchemaValidationError("data_columns must follow expression feature order")


def _schema_version(value: JSONValue | int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise SchemaValidationError("schema_version must be an integer")
    if value != FACTOR_SCHEMA_VERSION:
        raise UnknownSchemaVersionError(f"unknown schema_version: {value!r}")
    return FACTOR_SCHEMA_VERSION


def _digest_hex(value: str) -> str:
    result = value[7:]
    if (
        not value.startswith("sha256:")
        or len(result) != 64
        or any(character not in "0123456789abcdef" for character in result)
    ):
        raise FeatureMapIntegrityError(f"invalid sha256 digest: {value!r}")
    return result
