"""Build, persist, and restore executable collaborative-pool factors."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from pathlib import Path
from typing import Final

import pandas as pd

from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.errors import (
    FactorDependencyError,
    FactorFactoryError,
    SchemaValidationError,
)
from alphamill.factor_factory.factor import FactorCompute, FactorDef, FactorResolver
from alphamill.factor_factory.generators.expression_compiler import _validate_frame
from alphamill.factor_factory.hypotheses.catalog import (
    DEFAULT_CATALOG,
    MECHANISM_UNKNOWN_ID,
    HypothesisCatalog,
)
from alphamill.factor_factory.registry import factor_store
from alphamill.factor_factory.registry.compiler_registry import (
    DEFAULT_COMPILERS,
    CompileContext,
    CompilerRegistry,
)
from alphamill.factor_factory.registry.factor_store import FactorDefDTO

__all__ = (
    "POOL_GENERATOR",
    "PoolMember",
    "build_pool",
    "load_pool",
    "read_pool",
    "write_pool",
)

POOL_GENERATOR: Final = "pool"
_POOL_NAME: Final = "alpha_pool"
_POOL_PARAM_FIELDS: Final = frozenset({"members", "pool_version"})
_POOL_MEMBER_FIELDS: Final = frozenset({"factor_id", "weight"})


@dataclass(frozen=True, kw_only=True)
class PoolMember:
    """A factor reference and its exact, non-normalized linear weight."""

    factor_id: str
    weight: float


def build_pool(
    members: Sequence[PoolMember],
    *,
    run_id: str,
    created_at: datetime,
    resolver: FactorResolver,
    feature_map: Mapping[str, int],
    pool_version: str,
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
) -> FactorDef:
    """Build a content-addressed composite bound to ``mechanism_unknown``.

    A pool combines factors from potentially different hypotheses, so it does not assert a
    single mechanism. Weights are persisted exactly as supplied and are never normalized here.
    """
    validated = _validate_members(members)
    version = _validate_pool_version(pool_version)
    params: dict[str, JSONValue] = {
        "members": _member_payload(validated),
        "pool_version": version,
    }
    factor = factor_store.build_factor(
        hypothesis=DEFAULT_CATALOG.require(MECHANISM_UNKNOWN_ID),
        name=_POOL_NAME,
        generator=POOL_GENERATOR,
        generator_version=version,
        scope="cross_sectional",
        expression=(),
        params=params,
        feature_map=feature_map,
        run_id=run_id,
        created_at=created_at,
        compilers=compilers,
        resolver=resolver,
    )
    return _with_pool_meta(factor, validated, version)


def write_pool(run_dir: Path, pool: FactorDef) -> Path:
    """Persist an executable pool DTO at ``run_dir/pool.json`` without overwriting conflicts."""
    dto = factor_store.factor_to_dto(pool)
    _validate_pool_dto(dto)
    path = run_dir / "pool.json"
    factor_store._write_json(path, factor_store._factor_dto_payload(dto))
    return path


def read_pool(path: Path) -> FactorDefDTO:
    """Read and strictly validate a persisted pool definition without compiling it."""
    dto = factor_store.read(path)
    _validate_pool_dto(dto)
    return dto


def load_pool(
    path: Path,
    *,
    resolver: FactorResolver,
    feature_map: Mapping[str, int],
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
    catalog: HypothesisCatalog = DEFAULT_CATALOG,
) -> FactorDef:
    """Restore a pool whose compute resolves and combines its persisted members."""
    dto = read_pool(path)
    members, version = _pool_definition(dto.params)
    factor = factor_store.factor_from_dto(
        dto,
        feature_map=feature_map,
        compiler=compilers.require(POOL_GENERATOR),
        hypothesis=catalog.require(dto.hypothesis_id),
        resolver=resolver,
    )
    return _with_pool_meta(factor, members, version)


def _compile_pool(context: CompileContext) -> FactorCompute:
    members, _ = _pool_definition(context.params)
    resolver = context.resolver
    if resolver is None:
        raise FactorDependencyError("pool compiler requires a factor resolver")

    def compute(frame: pd.DataFrame) -> pd.Series:
        _validate_frame(frame, context)
        result = pd.Series(0.0, index=frame.index, dtype=float)
        for member in members:
            try:
                factor = resolver(member.factor_id)
            except (FactorFactoryError, LookupError) as exc:
                raise FactorDependencyError(
                    f"pool member cannot be resolved: {member.factor_id!r}"
                ) from exc
            if factor.scope != "cross_sectional":
                raise FactorDependencyError(
                    f"pool member must be cross_sectional: {member.factor_id!r}"
                )
            values = factor.compute(frame)
            if not values.index.equals(frame.index):
                raise FactorDependencyError(
                    f"pool member changed the input index: {member.factor_id!r}"
                )
            result = result + member.weight * values.astype(float)
        return result.where(frame["__in_universe__"])

    return compute


def _validate_members(members: Sequence[PoolMember]) -> tuple[PoolMember, ...]:
    validated = tuple(members)
    if not validated:
        raise SchemaValidationError("pool members must not be empty")
    if any(not member.factor_id.strip() for member in validated):
        raise SchemaValidationError("pool member factor_id must not be empty")
    if any(
        not isinstance(member.weight, float) or not math.isfinite(member.weight)
        for member in validated
    ):
        raise SchemaValidationError("pool weights must be finite floats")
    factor_ids = tuple(member.factor_id for member in validated)
    if len(set(factor_ids)) != len(factor_ids):
        raise SchemaValidationError("pool member factor_ids must be unique")
    if sum(abs(member.weight) for member in validated) <= 0.0:
        raise SchemaValidationError("pool total weight magnitude must be positive")
    return validated


def _validate_pool_version(pool_version: str) -> str:
    if not pool_version.strip():
        raise SchemaValidationError("pool_version must not be empty")
    return pool_version


def _member_payload(members: Sequence[PoolMember]) -> list[JSONValue]:
    return [{"factor_id": member.factor_id, "weight": member.weight} for member in members]


def _pool_definition(
    params: Mapping[str, JSONValue],
) -> tuple[tuple[PoolMember, ...], str]:
    if set(params) != _POOL_PARAM_FIELDS:
        raise SchemaValidationError("pool params must contain only members and pool_version")
    raw_members = params["members"]
    raw_version = params["pool_version"]
    if not isinstance(raw_members, list):
        raise SchemaValidationError("pool members must be a list")
    if not isinstance(raw_version, str):
        raise SchemaValidationError("pool_version must be a string")
    members: list[PoolMember] = []
    for raw_member in raw_members:
        if not isinstance(raw_member, dict) or set(raw_member) != _POOL_MEMBER_FIELDS:
            raise SchemaValidationError("pool member fields must be factor_id and weight")
        factor_id = raw_member["factor_id"]
        weight = raw_member["weight"]
        if not isinstance(factor_id, str) or not isinstance(weight, float):
            raise SchemaValidationError("pool member factor_id and weight types are invalid")
        members.append(PoolMember(factor_id=factor_id, weight=weight))
    return _validate_members(members), _validate_pool_version(raw_version)


def _validate_pool_dto(dto: FactorDefDTO) -> None:
    if dto.generator != POOL_GENERATOR or dto.scope != "cross_sectional":
        raise SchemaValidationError("pool DTO must be a cross_sectional pool factor")
    if dto.hypothesis_id != MECHANISM_UNKNOWN_ID:
        raise SchemaValidationError("pool DTO must use the mechanism_unknown hypothesis")
    if dto.expression or dto.data_columns:
        raise SchemaValidationError("pool DTO must encode dependencies in params")
    _, version = _pool_definition(dto.params)
    if dto.generator_version != version:
        raise SchemaValidationError("pool_version must match generator_version")


def _with_pool_meta(
    factor: FactorDef,
    members: Sequence[PoolMember],
    pool_version: str,
) -> FactorDef:
    meta = dict(factor.meta)
    meta.update(members=_member_payload(members), pool_version=pool_version)
    return replace(factor, meta=meta)


DEFAULT_COMPILERS.register(POOL_GENERATOR, _compile_pool)
