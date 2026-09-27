"""Persist generation run manifests, canonical configs, and append-only events."""

from __future__ import annotations

import fcntl
import json
import os
import re
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.generators import base
from alphamill.factor_factory.registry.run_schema import (  # 再导出：导入方零改动（D22/D29）
    EVENT_SCHEMA_VERSION,
    RUN_SCHEMA_VERSION,
    RUN_SCHEMA_VERSIONS,
    BudgetInfo,
    EngineInfo,
    GenerationRun,
    ObjectiveInfo,
    RunStatus,
    StopReason,
    TierLevel,
    UniverseSummary,
    _mapping,
    _payload,
    _utc,
    _validate_terminal,
    load_run,
)

_R = frozenset(
    ("created_at", "started_at", "finished_at", "hostname", "device", "vram_limit_gb")
    + ("kronos_offload",)
)
_C = frozenset(
    ("run_id", "generator", "engine", "binding", "seed")
    + ("device", "tier_level", "counts", "pool")
)
_SAFE_COMPONENT = re.compile(r"[A-Za-z0-9._-]+")


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
            schema_version=EVENT_SCHEMA_VERSION,
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
                schema_version=EVENT_SCHEMA_VERSION,
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


def _require_component(value: str, field: str) -> None:
    if _SAFE_COMPONENT.fullmatch(value) is None or value in {".", ".."} or ".." in value:
        raise errors.SchemaValidationError(f"{field} must be one safe path component")


__all__ = (
    "EVENT_SCHEMA_VERSION",
    "RUN_SCHEMA_VERSION",
    "RUN_SCHEMA_VERSIONS",
    "BudgetInfo",
    "EngineInfo",
    "GenerationEvent",
    "GenerationRun",
    "ObjectiveInfo",
    "RunStatus",
    "StopReason",
    "TierLevel",
    "UniverseSummary",
    "append_candidate_rejected",
    "finalize_run",
    "generation_run_dir",
    "load_run",
    "new_run_id",
    "write_config",
)
