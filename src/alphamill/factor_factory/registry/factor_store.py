"""Build, persist, and restore executable factors from strict content-addressed DTOs."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from alphamill.factor_factory.canonical import JSONValue, canonical_json_bytes, parse_utc, utc_iso
from alphamill.factor_factory.errors import (
    FactorCompilationError,
    FactorStoreError,
    FeatureMapIntegrityError,
    SchemaValidationError,
)
from alphamill.factor_factory.factor import FactorCompute, FactorDef, FactorResolver, FactorScope
from alphamill.factor_factory.generators.expression_compiler import referenced_features
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG, HypothesisCatalog
from alphamill.factor_factory.hypotheses.schema import HypothesisDef
from alphamill.factor_factory.registry.compiler_registry import (
    DEFAULT_COMPILERS,
    CompileContext,
    CompilerRegistry,
    FactorCompiler,
)
from alphamill.factor_factory.registry.factor_dto import (
    FACTOR_DTO_FIELDS,
    FACTOR_IDENTITY_EXCLUDED_FIELDS,
    FACTOR_SCHEMA_VERSION,
    FactorDefDTO,
    FeatureMapDTO,
    _digest_hex,
    _factor_dto_payload,
    _parse_factor_dto,
    _parse_feature_map,
    _validate_factor_dto,
    definition_digest,
    feature_map_digest,
)

__all__ = (
    "FACTOR_SCHEMA_VERSION",
    "FACTOR_DTO_FIELDS",
    "FACTOR_IDENTITY_EXCLUDED_FIELDS",
    "FeatureMapDTO",
    "FactorDefDTO",
    "feature_map_digest",
    "definition_digest",
    "build_factor",
    "factor_to_dto",
    "factor_from_dto",
    "write",
    "read",
    "load",
)


def build_factor(
    *,
    hypothesis: HypothesisDef,
    name: str,
    generator: str,
    generator_version: str,
    scope: FactorScope,
    expression: Sequence[str],
    params: Mapping[str, JSONValue],
    feature_map: Mapping[str, int],
    run_id: str,
    created_at: datetime,
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
    resolver: FactorResolver | None = None,
) -> FactorDef:
    """Compile an expression and construct its content-addressed executable factor."""
    tokens = tuple(expression)
    if any(not isinstance(token, str) for token in tokens):
        raise FactorCompilationError("expression tokens must be strings")
    features = dict(feature_map)
    columns = referenced_features(tokens)
    if missing := tuple(column for column in columns if column not in features):
        raise FeatureMapIntegrityError(f"expression features absent from feature_map: {missing!r}")
    dto = FactorDefDTO(
        schema_version=FACTOR_SCHEMA_VERSION,
        factor_id="pending",
        definition_digest="pending",
        hypothesis_id=hypothesis.hypothesis_id,
        name=name,
        generator=generator,
        generator_version=generator_version,
        scope=scope,
        expression=tokens,
        params=dict(params),
        data_columns=columns,
        feature_map_digest=feature_map_digest(features),
        run_id=run_id,
        created_at=parse_utc(utc_iso(created_at), field="created_at"),
    )
    context = _compile_context(dto, features, resolver)
    digest = definition_digest(dto)
    final = replace(dto, factor_id=f"{generator}_{digest[:12]}", definition_digest=digest)
    _validate_factor_dto(final)
    return _factor(final, compilers.compile(context), features, hypothesis.source)


def factor_to_dto(factor: FactorDef) -> FactorDefDTO:
    """Convert an executable factor to its strict persistence DTO."""
    dto = FactorDefDTO(
        schema_version=FACTOR_SCHEMA_VERSION,
        factor_id=factor.factor_id,
        definition_digest=factor.meta["definition_digest"],
        hypothesis_id=factor.hypothesis_id,
        name=factor.name,
        generator=factor.generator,
        generator_version=factor.meta["generator_version"],
        scope=factor.scope,
        expression=tuple(factor.meta["expression"]),
        params=dict(factor.params),
        data_columns=tuple(factor.data_columns),
        feature_map_digest=factor.meta["feature_map_digest"],
        run_id=factor.meta["run_id"],
        created_at=parse_utc(factor.meta["created_at"], field="created_at"),
    )
    _validate_factor_dto(dto)
    if feature_map_digest(dict(factor.meta["feature_map"])) != dto.feature_map_digest:
        raise FeatureMapIntegrityError("FactorDef feature_map does not match its digest")
    return dto


def factor_from_dto(
    dto: FactorDefDTO,
    *,
    feature_map: Mapping[str, int],
    compiler: FactorCompiler,
    hypothesis: HypothesisDef,
    resolver: FactorResolver | None = None,
) -> FactorDef:
    """Compile a validated DTO and restore its executable factor shape."""
    _validate_factor_dto(dto)
    features = dict(feature_map)
    if feature_map_digest(features) != dto.feature_map_digest:
        raise FeatureMapIntegrityError("feature_map digest does not match FactorDefDTO")
    if dto.data_columns != referenced_features(dto.expression):
        raise FeatureMapIntegrityError("FactorDefDTO data_columns do not match expression features")
    if hypothesis.hypothesis_id != dto.hypothesis_id:
        raise SchemaValidationError("hypothesis does not match FactorDefDTO")
    compute = compiler(_compile_context(dto, features, resolver))
    return _factor(dto, compute, features, hypothesis.source)


def write(run_dir: Path, factor: FactorDef) -> Path:
    """Persist the feature map before the factor DTO, rejecting path conflicts."""
    dto = factor_to_dto(factor)
    feature_path = run_dir / "feature_maps" / f"{_digest_hex(dto.feature_map_digest)}.json"
    factor_path = run_dir / "factors" / f"{dto.factor_id}.json"
    _write_json(
        feature_path,
        {"schema_version": FACTOR_SCHEMA_VERSION, "features": factor.meta["feature_map"]},
    )
    _write_json(factor_path, _factor_dto_payload(dto))
    return factor_path


def read(path: Path) -> FactorDefDTO:
    """Parse a factor DTO strictly without compiling it."""
    return _parse_factor_dto(_read_json(path))


def load(
    path: Path,
    *,
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
    catalog: HypothesisCatalog = DEFAULT_CATALOG,
    resolver: FactorResolver | None = None,
    require_completed: bool = True,
) -> FactorDef:
    """Verify persisted dependencies and restore an executable factor."""
    run_dir = path.parent.parent
    if require_completed:
        manifest = run_dir / "run.json"
        if not manifest.is_file():
            raise FactorStoreError(f"completed run manifest is missing: {manifest}")
        run = _read_json(manifest)
        if run.get("schema_version") != FACTOR_SCHEMA_VERSION or run.get("status") != "completed":
            raise FactorStoreError("run.json must have schema_version=1 and status='completed'")
    dto = read(path)
    feature_path = run_dir / "feature_maps" / f"{_digest_hex(dto.feature_map_digest)}.json"
    feature_map = _parse_feature_map(_read_json(feature_path))
    if feature_map_digest(feature_map.features) != dto.feature_map_digest:
        raise FeatureMapIntegrityError("persisted feature map digest does not match FactorDefDTO")
    return factor_from_dto(
        dto,
        feature_map=feature_map.features,
        compiler=compilers.require(dto.generator),
        hypothesis=catalog.require(dto.hypothesis_id),
        resolver=resolver,
    )


def _factor(
    dto: FactorDefDTO,
    compute: FactorCompute,
    features: Mapping[str, int],
    hypothesis_source: str,
) -> FactorDef:
    meta: dict[str, JSONValue] = {
        "schema_version": FACTOR_SCHEMA_VERSION,
        "expression": list(dto.expression),
        "definition_digest": dto.definition_digest,
        "generator_version": dto.generator_version,
        "feature_map": dict(features),
        "feature_map_digest": dto.feature_map_digest,
        "run_id": dto.run_id,
        "created_at": utc_iso(dto.created_at),
        "hypothesis_source": hypothesis_source,
    }
    return FactorDef(
        factor_id=dto.factor_id,
        hypothesis_id=dto.hypothesis_id,
        name=dto.name,
        generator=dto.generator,
        scope=dto.scope,
        params=dict(dto.params),
        compute=compute,
        data_columns=list(dto.data_columns),
        meta=meta,
    )


def _compile_context(
    dto: FactorDefDTO,
    features: Mapping[str, int],
    resolver: FactorResolver | None,
) -> CompileContext:
    return CompileContext(
        generator=dto.generator,
        expression=dto.expression,
        scope=dto.scope,
        params=dto.params,
        data_columns=dto.data_columns,
        feature_map=features,
        resolver=resolver,
    )


def _write_json(path: Path, payload: Mapping[str, JSONValue]) -> None:
    content = canonical_json_bytes(dict(payload))
    if path.exists():
        if path.read_bytes() != content:
            raise FactorStoreError(f"conflicting artifact at {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _read_json(path: Path) -> dict[str, JSONValue]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise FactorStoreError(f"cannot read artifact: {path}") from exc
    except (json.JSONDecodeError, ValueError) as exc:
        raise SchemaValidationError(f"invalid JSON artifact: {path}") from exc
    if not isinstance(payload, dict):
        raise SchemaValidationError(f"JSON artifact must be an object: {path}")
    return payload
