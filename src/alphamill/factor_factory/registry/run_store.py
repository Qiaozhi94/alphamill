"""Persist generation run manifests, canonical configs, and append-only events."""

from __future__ import annotations

import fcntl
import json
import os
import re
import tempfile
import types
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TypeAlias, TypeVar, get_args, get_origin, get_type_hints
from uuid import uuid4

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.generators import base, binding

RUN_SCHEMA_VERSION = 1
RunStatus: TypeAlias = Literal["completed", "rejected", "failed", "partial"]
TierLevel: TypeAlias = Literal["L0", "L1", "L2", "manual"]
_R = frozenset(("created_at", "started_at", "finished_at", "hostname", "device", "vram_limit_gb"))
_C = frozenset(
    ("run_id", "generator", "engine", "binding", "seed")
    + ("device", "tier_level", "counts", "pool")
)
_SAFE_COMPONENT = re.compile(r"[A-Za-z0-9._-]+")
_T = TypeVar("_T")


@dataclass(frozen=True, kw_only=True)
class EngineInfo:
    vendor_commit: str | None
    code_digest: str
    dependencies: dict[str, str]


@dataclass(frozen=True, kw_only=True)
class UniverseSummary:
    pair_count: int
    symbol_map_digest: str
    universe_digest: str
    source: str


@dataclass(frozen=True, kw_only=True)
class ObjectiveInfo:
    turnover_penalty_lambda: float
    reachability_min_trades_90d: int
    cost_model: dict[str, JSONValue]
    min_after_cost_return: float


@dataclass(frozen=True, kw_only=True)
class GenerationRun:
    schema_version: int
    run_id: str
    generator: str
    engine: EngineInfo
    binding: binding.SnapshotBinding | None
    seed: int | None
    config_digest: str
    device: str
    hostname: str
    vram_limit_gb: float | None
    universe: UniverseSummary | None
    tier_level: TierLevel
    window: base.Window | None
    objective: ObjectiveInfo
    counts: base.GenerationCounts
    pool: str | None
    started_at: datetime
    finished_at: datetime
    status: RunStatus
    termination: str
    reason: str | None


@dataclass(frozen=True, kw_only=True)
class GenerationEvent:
    schema_version: int
    event_seq: int
    event_type: Literal["generation.run_completed", "generation.candidate_rejected"]
    ts: datetime
    run_id: str
    payload: dict[str, JSONValue]


def new_run_id(generator: str, *, now: datetime | None = None) -> str:
    """Create a unique, path-safe run identifier containing a compact UTC timestamp."""
    _require_component(generator, "generator")
    timestamp = now if now is not None else datetime.now(UTC)
    compact = canonical.parse_utc(canonical.utc_iso(timestamp), field="now").strftime(
        "%Y%m%dT%H%M%S%fZ"
    )
    return f"{generator}-{compact}-{uuid4().hex[:8]}"


def generation_run_dir(run_id: str, *, reports_root: Path | None = None) -> Path:
    """Create and return ``reports/generation/<run_id>``."""
    _require_component(run_id, "run_id")
    root = Path(__file__).resolve().parents[4] / "reports" if reports_root is None else reports_root
    run_dir = root / "generation" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_config(run_dir: Path, config: Mapping[str, JSONValue]) -> str:
    """Persist the canonical semantic config and return its prefixed digest."""
    cleaned = {key: value for key, value in config.items() if key not in _R}
    content = canonical.canonical_json_bytes(cleaned)
    digest = canonical.sha256_prefixed_bytes(content)
    path = run_dir / "config.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise errors.RunStoreError(f"conflicting config artifact at {path}")
        return digest
    path.write_bytes(content)
    return digest


def append_candidate_rejected(
    run_dir: Path,
    *,
    run_id: str,
    expression: Sequence[str],
    reason_code: base.RejectionReason,
    detail: str,
    ts: datetime | None = None,
) -> GenerationEvent:
    """Append one candidate rejection event under an exclusive file lock."""
    return _append_event(
        run_dir,
        GenerationEvent(
            schema_version=RUN_SCHEMA_VERSION,
            event_seq=0,
            event_type="generation.candidate_rejected",
            ts=_utc(ts if ts is not None else datetime.now(UTC), "ts"),
            run_id=run_id,
            payload={"expression": list(expression), "reason_code": reason_code, "detail": detail},
        ),
        unique=False,
    )


def finalize_run(run_dir: Path, run: GenerationRun) -> Path:
    """Validate and atomically publish the terminal run manifest."""
    _validate_terminal(run)
    path = run_dir / "run.json"
    run_dir.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise errors.RunStoreError(f"run manifest already exists: {path}")
    payload = _payload(run)
    if run.status == "completed":
        _append_event(
            run_dir,
            GenerationEvent(
                schema_version=RUN_SCHEMA_VERSION,
                event_seq=0,
                event_type="generation.run_completed",
                ts=_utc(run.finished_at, "finished_at"),
                run_id=run.run_id,
                payload={key: payload[key] for key in _C},
            ),
            unique=True,
        )
    _atomic_write(path, canonical.canonical_json_bytes(payload))
    return path


def load_run(path: Path) -> GenerationRun:
    """Strictly parse a persisted generation run manifest."""
    try:
        content = path.read_bytes()
        payload: JSONValue = json.loads(content)
    except OSError as exc:
        raise errors.RunStoreError(f"cannot read run manifest: {path}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise errors.SchemaValidationError(f"invalid run manifest JSON: {path}") from exc
    body = _mapping(payload, "run")
    version = body.get("schema_version")
    if isinstance(version, bool) or not isinstance(version, int):
        raise errors.SchemaValidationError("schema_version must be an integer")
    if version != RUN_SCHEMA_VERSION:
        raise errors.UnknownSchemaVersionError(f"unsupported run schema_version: {version}")
    run = _parse_model(payload, GenerationRun, "run")
    _validate_terminal(run)
    return run


def _append_event(run_dir: Path, event: GenerationEvent, *, unique: bool) -> GenerationEvent:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "events.jsonl"
    try:
        descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_RDWR, 0o644)
        with os.fdopen(descriptor, "rb+", buffering=0) as stream:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            try:
                stream.seek(0)
                content = stream.read()
                if content and (not content.endswith(b"\n") or b"\n\n" in content):
                    raise errors.RunStoreError("events.jsonl contains an incomplete line")
                lines = content.splitlines()
                for sequence, line in enumerate(lines, start=1):
                    record = _mapping(json.loads(line), f"events[{sequence}]")
                    if unique and record.get("event_type") == event.event_type:
                        return replace(event, event_seq=sequence)
                stored = replace(event, event_seq=len(lines) + 1)
                encoded = canonical.canonical_json_bytes(_payload(stored)) + b"\n"
                if os.write(descriptor, encoded) != len(encoded):
                    raise errors.RunStoreError(f"short event write: {path}")
                os.fsync(descriptor)
                return stored
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise errors.RunStoreError(f"cannot append event: {path}") from exc


def _atomic_write(path: Path, content: bytes) -> None:
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        descriptor = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise errors.RunStoreError(f"cannot publish run manifest: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _validate_terminal(run: GenerationRun) -> None:
    if run.schema_version != RUN_SCHEMA_VERSION or run.tier_level not in get_args(TierLevel):
        raise errors.SchemaValidationError("GenerationRun schema_version or tier_level is unknown")
    if _utc(run.finished_at, "finished_at") < _utc(run.started_at, "started_at"):
        raise errors.SchemaValidationError("finished_at must not precede started_at")
    match run.status:
        case "completed":
            if any(value is None for value in (run.binding, run.window, run.universe, run.seed)):
                raise errors.SchemaValidationError("completed run lacks required inputs")
            if run.reason is not None:
                raise errors.SchemaValidationError("completed run reason must be None")
        case "rejected" | "failed":
            if run.reason is None:
                raise errors.SchemaValidationError(f"{run.status} run requires reason")
        case "partial":
            if run.reason is None or run.pool is not None:
                raise errors.SchemaValidationError("partial run requires reason and forbids pool")
        case unknown:
            raise errors.SchemaValidationError(f"unknown run status: {unknown!r}")


def _payload(value) -> dict[str, JSONValue]:
    payload: JSONValue = json.loads(
        json.dumps(
            asdict(value),
            default=lambda item: (
                canonical.utc_iso(item) if isinstance(item, datetime) else item.as_posix()
            ),
            allow_nan=False,
        )
    )
    return _mapping(payload, "payload")


def _parse_model(value: JSONValue, model: type[_T], field: str) -> _T:
    body = _mapping(value, field, _field_names(model))
    annotations = get_type_hints(model)
    return model(
        **{
            item.name: _decode(body[item.name], annotations[item.name], f"{field}.{item.name}")
            for item in fields(model)
        }
    )


def _decode(value: JSONValue, annotation, field: str):
    if annotation is datetime:
        return canonical.parse_utc(_decode(value, str, field), field=field)
    if annotation in (str, int, float):
        accepted = (int, float) if annotation is float else (annotation,)
        if type(value) not in accepted:
            raise errors.SchemaValidationError(f"{field} has the wrong primitive type")
        return annotation(value)
    origin, arguments = get_origin(annotation), get_args(annotation)
    if origin is Literal:
        if value not in arguments:
            raise errors.SchemaValidationError(f"{field} has an unknown literal value")
        return value
    if origin is dict:
        return {
            key: _decode(item, arguments[1], f"{field}.{key}")
            for key, item in _mapping(value, field).items()
        }
    if origin is types.UnionType:
        if {str, int, float, bool, type(None)}.issubset(arguments):
            return value
        if value is None and type(None) in arguments:
            return None
        if {binding.SnapshotRefBinding, binding.ExplicitSnapshotBinding}.issubset(arguments):
            try:
                return binding.parse_binding(_mapping(value, field))
            except errors.BindingValidationError as exc:
                raise errors.SchemaValidationError(f"{field}: {exc}") from exc
        candidates = tuple(item for item in arguments if item is not type(None))
        if len(candidates) == 1:
            return _decode(value, candidates[0], field)
    if isinstance(annotation, type) and is_dataclass(annotation):
        return _parse_model(value, annotation, field)
    raise errors.SchemaValidationError(f"{field} has an unsupported schema type")


def _mapping(
    value: JSONValue, field: str, expected: frozenset[str] | None = None
) -> dict[str, JSONValue]:
    if not isinstance(value, dict):
        raise errors.SchemaValidationError(f"{field} must be a JSON object")
    if expected is not None and set(value) != expected:
        raise errors.SchemaValidationError(f"{field} fields do not match the schema")
    return value


def _field_names(model) -> frozenset[str]:
    return frozenset(item.name for item in fields(model))


def _utc(value: datetime, field: str) -> datetime:
    return canonical.parse_utc(canonical.utc_iso(value), field=field)


def _require_component(value: str, field: str) -> None:
    if _SAFE_COMPONENT.fullmatch(value) is None or value in {".", ".."} or ".." in value:
        raise errors.SchemaValidationError(f"{field} must be one safe path component")
