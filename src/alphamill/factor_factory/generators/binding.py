"""Frozen research-snapshot binding types and public file-boundary operations."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal, Protocol, TypeAlias

from alphamill.factor_factory.canonical import JSONValue, parse_utc, utc_iso
from alphamill.factor_factory.errors import BindingValidationError, SchemaValidationError
from alphamill.factor_factory.generators.universe import UniverseLedger, load_explicit_universe

BindingMode: TypeAlias = Literal["snapshot", "explicit_tuples"]
"""The two persisted binding representations."""

AsOfFidelity: TypeAlias = Literal["bitemporal", "event_time_only"]
"""The F002 as-of fidelity declared by a dataset member."""


@dataclass(frozen=True, kw_only=True)
class DatasetBinding:
    """Immutable identity and event-time coverage for one dataset member."""

    data_version: str
    value_digest: str
    as_of_fidelity: AsOfFidelity
    event_time_min: datetime
    event_time_max: datetime


@dataclass(frozen=True, kw_only=True)
class ArtifactRef:
    """Content-addressed artifact identity and location."""

    digest: str
    path: Path
    schema_version: int


@dataclass(frozen=True, kw_only=True)
class BindingProvenance:
    """Immutable filesystem references used to audit a binding."""

    created_at: datetime
    artifact_path: Path
    member_manifest_paths: dict[str, Path]
    symbol_map_path: Path
    universe_path: Path
    calendar_path: Path


@dataclass(frozen=True, kw_only=True)
class SnapshotRefBinding:
    """Reference form resolved through a ResearchSnapshot resolver."""

    mode: Literal["snapshot"]
    research_snapshot_id: str


@dataclass(frozen=True, kw_only=True)
class ExplicitSnapshotBinding:
    """Fully materialized binding whose members can be checked against F002."""

    mode: Literal["explicit_tuples"]
    schema_version: int
    cutoff_time: datetime
    members: dict[str, DatasetBinding]
    symbol_map_digest: str
    universe: ArtifactRef
    calendar: ArtifactRef
    universe_calendar_digest: str
    provenance: BindingProvenance


SnapshotBinding: TypeAlias = SnapshotRefBinding | ExplicitSnapshotBinding
"""Union accepted by generation requests and binding files."""


class SnapshotResolver(Protocol):
    """Resolve a persisted ResearchSnapshot identifier to explicit inputs."""

    def __call__(self, research_snapshot_id: str) -> ExplicitSnapshotBinding: ...


UniverseLoader: TypeAlias = Callable[[Path, str, int], UniverseLedger]
"""Load and validate an explicit universe artifact."""


@dataclass(frozen=True, kw_only=True)
class ValidatedBinding:
    """Resolved binding plus the validated point-in-time universe ledger."""

    source: SnapshotBinding
    resolved: ExplicitSnapshotBinding
    universe_ledger: UniverseLedger


def parse_binding(payload: Mapping[str, object]) -> SnapshotBinding:
    """Parse the frozen JSON binding schema without compatibility guesses."""
    member_keys = frozenset(
        {"data_version", "value_digest", "as_of_fidelity", "event_time_min", "event_time_max"}
    )
    artifact_keys = frozenset({"digest", "path", "schema_version"})
    provenance_keys = frozenset(
        {
            "created_at",
            "artifact_path",
            "member_manifest_paths",
            "symbol_map_path",
            "universe_path",
            "calendar_path",
        }
    )
    explicit_keys = frozenset(
        {
            "mode",
            "schema_version",
            "cutoff_time",
            "members",
            "symbol_map_digest",
            "universe",
            "calendar",
            "universe_calendar_digest",
            "provenance",
        }
    )

    def obj(value: object, field: str, keys: frozenset[str] | None = None) -> dict[str, object]:
        if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
            raise BindingValidationError(f"{field}: must be a JSON object with string keys")
        result = dict(value)
        if keys is not None and set(result) != keys:
            raise BindingValidationError(
                f"{field}: keys invalid; missing={sorted(keys - set(result))}, "
                f"unknown={sorted(set(result) - keys)}"
            )
        return result

    def text(value: object, field: str) -> str:
        if not isinstance(value, str) or not value:
            raise BindingValidationError(f"{field}: must be a non-empty string")
        return value

    def integer(value: object, field: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise BindingValidationError(f"{field}: must be an integer")
        return value

    def timestamp(value: object, field: str) -> datetime:
        try:
            return parse_utc(text(value, field), field=field)
        except SchemaValidationError as exc:
            raise BindingValidationError(str(exc)) from exc

    def member(value: object, name: str) -> DatasetBinding:
        body = obj(value, f"members.{name}", member_keys)
        fidelity = text(body["as_of_fidelity"], f"members.{name}.as_of_fidelity")
        if fidelity not in {"bitemporal", "event_time_only"}:
            raise BindingValidationError(f"members.{name}.as_of_fidelity: unknown fidelity")
        low = timestamp(body["event_time_min"], f"members.{name}.event_time_min")
        high = timestamp(body["event_time_max"], f"members.{name}.event_time_max")
        if low > high:
            raise BindingValidationError(f"members.{name}: event_time_min exceeds event_time_max")
        return DatasetBinding(
            data_version=text(body["data_version"], f"members.{name}.data_version"),
            value_digest=text(body["value_digest"], f"members.{name}.value_digest"),
            as_of_fidelity=fidelity,
            event_time_min=low,
            event_time_max=high,
        )

    def artifact(value: object, field: str) -> ArtifactRef:
        body = obj(value, field, artifact_keys)
        return ArtifactRef(
            digest=text(body["digest"], f"{field}.digest"),
            path=Path(text(body["path"], f"{field}.path")),
            schema_version=integer(body["schema_version"], f"{field}.schema_version"),
        )

    def provenance(value: object, datasets: frozenset[str]) -> BindingProvenance:
        body = obj(value, "provenance", provenance_keys)
        paths = obj(body["member_manifest_paths"], "provenance.member_manifest_paths", datasets)
        return BindingProvenance(
            created_at=timestamp(body["created_at"], "provenance.created_at"),
            artifact_path=Path(text(body["artifact_path"], "provenance.artifact_path")),
            member_manifest_paths={
                name: Path(text(paths[name], f"provenance.member_manifest_paths.{name}"))
                for name in sorted(datasets)
            },
            symbol_map_path=Path(text(body["symbol_map_path"], "provenance.symbol_map_path")),
            universe_path=Path(text(body["universe_path"], "provenance.universe_path")),
            calendar_path=Path(text(body["calendar_path"], "provenance.calendar_path")),
        )

    body = obj(payload, "binding")
    match text(body.get("mode"), "mode"):
        case "snapshot":
            body = obj(body, "binding", frozenset({"mode", "research_snapshot_id"}))
            return SnapshotRefBinding(
                mode="snapshot",
                research_snapshot_id=text(body["research_snapshot_id"], "research_snapshot_id"),
            )
        case "explicit_tuples":
            body = obj(body, "binding", explicit_keys)
            version = integer(body["schema_version"], "schema_version")
            if version != 1:
                raise BindingValidationError(f"schema_version: unsupported value {version}")
            raw_members = obj(body["members"], "members")
            if not raw_members:
                raise BindingValidationError("members: at least one dataset is required")
            members = {name: member(raw_members[name], name) for name in sorted(raw_members)}
            return ExplicitSnapshotBinding(
                mode="explicit_tuples",
                schema_version=version,
                cutoff_time=timestamp(body["cutoff_time"], "cutoff_time"),
                members=members,
                symbol_map_digest=text(body["symbol_map_digest"], "symbol_map_digest"),
                universe=artifact(body["universe"], "universe"),
                calendar=artifact(body["calendar"], "calendar"),
                universe_calendar_digest=text(
                    body["universe_calendar_digest"], "universe_calendar_digest"
                ),
                provenance=provenance(body["provenance"], frozenset(members)),
            )
        case unknown:
            raise BindingValidationError(f"mode: unknown value {unknown!r}")


def load_binding_file(path: Path) -> SnapshotBinding:
    """Read and parse one binding file, rejecting malformed input."""
    try:
        return parse_binding(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BindingValidationError(f"binding file cannot be read: {path}") from exc


def binding_to_dict(binding: SnapshotBinding) -> dict[str, JSONValue]:
    """Serialize a binding into the exact JSON-compatible frozen schema."""

    def default(value: object) -> str:
        if isinstance(value, datetime):
            return utc_iso(value)
        if isinstance(value, Path):
            return value.as_posix()
        raise TypeError(type(value).__name__)

    try:
        return json.loads(json.dumps(asdict(binding), default=default))
    except (TypeError, ValueError, SchemaValidationError) as exc:
        raise BindingValidationError("binding contains a non-JSON value") from exc


def validate_binding(
    binding: SnapshotBinding,
    *,
    lake_root: Path | None = None,
    snapshot_resolver: SnapshotResolver | None = None,
    universe_loader: UniverseLoader = load_explicit_universe,
) -> ValidatedBinding:
    """Resolve and fail-closed validate every immutable input in a binding."""
    from alphamill.factor_factory.generators.binding_checks import _validate

    return _validate(
        binding,
        lake_root=lake_root,
        snapshot_resolver=snapshot_resolver,
        universe_loader=universe_loader,
    )
