"""Private lake, artifact, and provenance checks for F003 snapshot bindings."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn, assert_never

from alphamill.data_bridge import manifest, reader, registry, symbol_map
from alphamill.data_bridge import paths as lake_paths
from alphamill.data_bridge.errors import DataBridgeError, InvalidVersionError
from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    parse_utc,
    sha256_prefixed_bytes,
)
from alphamill.factor_factory.errors import (
    BindingValidationError,
    SchemaValidationError,
    SnapshotResolverUnavailableError,
)
from alphamill.factor_factory.generators.universe import UniverseLedger, load_explicit_universe

if TYPE_CHECKING:
    from alphamill.factor_factory.generators.binding import (
        ArtifactRef,
        DatasetBinding,
        ExplicitSnapshotBinding,
        SnapshotBinding,
        SnapshotResolver,
        UniverseLoader,
        ValidatedBinding,
    )

_CALENDAR_KEYS = frozenset({"schema_version", "kind", "timezone"})


def _fail(field: str, detail: str) -> NoReturn:
    raise BindingValidationError(f"{field}: {detail}")


def _obj(value: object, field: str, keys: frozenset[str] | None = None) -> dict[str, object]:
    if not isinstance(value, Mapping) or any(not isinstance(key, str) for key in value):
        _fail(field, "必须是 JSON object，且键必须是 string")
    result = dict(value)
    if keys is not None and set(result) != keys:
        _fail(
            field,
            f"keys invalid; missing={sorted(keys - set(result))}, "
            f"unknown={sorted(set(result) - keys)}",
        )
    return result


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(field, "必须是非空 string")
    return value


def _integer(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _fail(field, "必须是 integer")
    return value


def _time(value: object, field: str) -> datetime:
    try:
        return parse_utc(_text(value, field), field=field)
    except SchemaValidationError as exc:
        raise BindingValidationError(str(exc)) from exc


def _same(actual: object, expected: object, field: str) -> None:
    if actual != expected:
        _fail(field, f"mismatch: expected {expected!r}, got {actual!r}")


def _member_check(
    name: str,
    member: DatasetBinding,
    binding: ExplicitSnapshotBinding,
    lake_root: Path | None,
    root: Path,
) -> None:
    try:
        spec = registry.require_dataset(name)
        result = reader.read(
            spec.name,
            data_version=member.data_version,
            start=binding.cutoff_time,
            end=binding.cutoff_time,
            pairs=[],
            as_of=binding.cutoff_time,
            allow_event_time_only=member.as_of_fidelity == "event_time_only",
            lake_root=lake_root,
        )
    except InvalidVersionError as exc:
        raise BindingValidationError(f"{name}: data_version invalid") from exc
    except (DataBridgeError, ValueError) as exc:
        raise BindingValidationError(f"{name}: F002 reader rejected binding") from exc
    _same(result.data_version, member.data_version, f"members.{name}.data_version")
    _same(result.value_digest, member.value_digest, f"members.{name}.value_digest")
    _same(result.as_of_fidelity, member.as_of_fidelity, f"members.{name}.as_of_fidelity")
    _same(result.symbol_map_digest, binding.symbol_map_digest, "symbol_map_digest")
    try:
        parts = manifest.load_manifest(root, spec.name, member.data_version).get("partitions")
        if not isinstance(parts, list) or not parts:
            _fail(f"members.{name}", "manifest 没有 declared coverage")
        lows = [parse_utc(part["time_min"], field=f"{name}.time_min") for part in parts]
        highs = [parse_utc(part["time_max"], field=f"{name}.time_max") for part in parts]
    except DataBridgeError as exc:
        raise BindingValidationError(f"{name}: manifest 无法读取") from exc
    except (KeyError, TypeError, SchemaValidationError) as exc:
        raise BindingValidationError(f"{name}: manifest coverage 非法") from exc
    if min(lows) > member.event_time_min or max(highs) < member.event_time_max:
        _fail(f"members.{name}", "manifest coverage does not cover declared range")


def _calendar_check(ref: ArtifactRef) -> None:
    _same(ref.schema_version, 1, "calendar.schema_version")
    try:
        body = _obj(json.loads(ref.path.read_text(encoding="utf-8")), "calendar", _CALENDAR_KEYS)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BindingValidationError(f"calendar artifact 无法读取: {ref.path}") from exc
    _same(_integer(body["schema_version"], "calendar.schema_version"), 1, "calendar.schema_version")
    _same(body["kind"], "continuous_24_7", "calendar.kind")
    _same(body["timezone"], "UTC", "calendar.timezone")
    _same(
        sha256_prefixed_bytes(canonical_json_bytes(body)),
        ref.digest,
        "calendar.digest",
    )


def _universe_check(ref: ArtifactRef, loader: UniverseLoader) -> UniverseLedger:
    _same(ref.schema_version, 1, "universe.schema_version")
    try:
        if loader is load_explicit_universe:
            ledger = loader(
                ref.path,
                expected_digest=ref.digest,
                expected_schema_version=ref.schema_version,
            )
        else:
            ledger = loader(ref.path, ref.digest, ref.schema_version)
    except BindingValidationError:
        raise
    except (DataBridgeError, OSError, SchemaValidationError, TypeError, ValueError) as exc:
        raise BindingValidationError(f"universe artifact 无法读取: {ref.path}") from exc
    if not isinstance(ledger, UniverseLedger):
        _fail("universe", "loader must return UniverseLedger")
    _same(ledger.digest, ref.digest, "universe.digest")
    _same(ledger.schema_version, ref.schema_version, "universe.schema_version")
    return ledger


def _immutable(path: Path, field: str, identity: str) -> Path:
    if any(part.lower() in {"current", "latest"} for part in path.parts):
        _fail(field, "mutable current/latest path is forbidden")
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise BindingValidationError(f"{field}: path 不存在") from exc
    if not resolved.is_file() or identity not in resolved.as_posix():
        _fail(field, "path is not an immutable digest-named artifact")
    return resolved


def _provenance_check(binding: ExplicitSnapshotBinding, root: Path) -> None:
    provenance = binding.provenance
    _immutable(
        provenance.artifact_path,
        "provenance.artifact_path",
        binding.universe_calendar_digest,
    )
    for name, member in sorted(binding.members.items()):
        actual = _immutable(
            provenance.member_manifest_paths[name],
            f"provenance.member_manifest_paths.{name}",
            member.data_version,
        )
        _same(
            actual,
            lake_paths.manifest_path(root, name, member.data_version).resolve(),
            f"provenance.member_manifest_paths.{name}",
        )
    _same(
        _immutable(
            provenance.symbol_map_path,
            "provenance.symbol_map_path",
            binding.symbol_map_digest,
        ),
        (lake_paths.symbol_maps_dir(root) / f"{binding.symbol_map_digest}.csv").resolve(),
        "provenance.symbol_map_path",
    )
    _same(
        _immutable(provenance.universe_path, "provenance.universe_path", binding.universe.digest),
        binding.universe.path.resolve(),
        "provenance.universe_path",
    )
    _same(
        _immutable(provenance.calendar_path, "provenance.calendar_path", binding.calendar.digest),
        binding.calendar.path.resolve(),
        "provenance.calendar_path",
    )


def _validate(
    binding: SnapshotBinding,
    *,
    lake_root: Path | None,
    snapshot_resolver: SnapshotResolver | None,
    universe_loader: UniverseLoader,
) -> ValidatedBinding:
    from alphamill.factor_factory.generators.binding import (
        ExplicitSnapshotBinding,
        SnapshotRefBinding,
        ValidatedBinding,
        binding_to_dict,
        parse_binding,
    )

    source = parse_binding(binding_to_dict(binding))
    match source:
        case ExplicitSnapshotBinding() as resolved:
            pass
        case SnapshotRefBinding(research_snapshot_id=identifier):
            if snapshot_resolver is None:
                raise SnapshotResolverUnavailableError(
                    "snapshot 绑定需要 SnapshotResolver，但调用方未提供"
                )
            candidate = snapshot_resolver(identifier)
            if not isinstance(candidate, ExplicitSnapshotBinding):
                _fail("snapshot_resolver", "必须返回 ExplicitSnapshotBinding")
            parsed = parse_binding(binding_to_dict(candidate))
            match parsed:
                case ExplicitSnapshotBinding() as resolved:
                    pass
                case SnapshotRefBinding():
                    _fail("snapshot_resolver", "必须返回 explicit_tuples binding")
                case unreachable:
                    assert_never(unreachable)
        case unreachable:
            assert_never(unreachable)
    root = Path(lake_root) if lake_root is not None else lake_paths.lake_root()
    for name in sorted(resolved.members):
        _member_check(name, resolved.members[name], resolved, lake_root, root)
    try:
        symbol_map.load_symbol_map(digest=resolved.symbol_map_digest, lake_root=lake_root)
    except DataBridgeError as exc:
        raise BindingValidationError("symbol_map artifact 校验失败") from exc
    ledger = _universe_check(resolved.universe, universe_loader)
    _calendar_check(resolved.calendar)
    payload: JSONValue = {
        "universe": resolved.universe.digest,
        "calendar": resolved.calendar.digest,
    }
    expected = "sha256:" + hashlib.sha256(canonical_json_bytes(payload)).hexdigest()
    _same(expected, resolved.universe_calendar_digest, "universe_calendar_digest")
    _provenance_check(resolved, root)
    return ValidatedBinding(source=source, resolved=resolved, universe_ledger=ledger)
