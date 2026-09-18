"""F003 T008 运行存储契约：DR-001 / TR-001 / TR-002 / AC-009 / AC-012。"""

from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.factor_factory.canonical import JSONValue, canonical_json_bytes, utc_iso
from alphamill.factor_factory.errors import (
    RunStoreError,
    SchemaValidationError,
    UnknownSchemaVersionError,
)
from alphamill.factor_factory.generators.base import (
    GenerationCounts,
    RejectionCounts,
    Window,
)
from alphamill.factor_factory.generators.binding import SnapshotRefBinding
from alphamill.factor_factory.registry.run_store import (
    RUN_SCHEMA_VERSION,
    EngineInfo,
    GenerationRun,
    ObjectiveInfo,
    RunStatus,
    UniverseSummary,
    append_candidate_rejected,
    finalize_run,
    generation_run_dir,
    load_run,
    new_run_id,
    write_config,
)

STARTED_AT = datetime(2026, 9, 19, 1, 2, 3, tzinfo=UTC)
FINISHED_AT = STARTED_AT + timedelta(minutes=7)


def _completed_run() -> GenerationRun:
    return GenerationRun(
        schema_version=RUN_SCHEMA_VERSION,
        run_id="manual-20260919T010203000000Z-1234abcd",
        generator="manual",
        engine=EngineInfo(
            vendor_commit=None,
            code_digest="sha256:" + "a" * 64,
            dependencies={"alphamill": "0.1.0", "python": "3.11"},
        ),
        binding=SnapshotRefBinding(mode="snapshot", research_snapshot_id="snapshot-001"),
        seed=17,
        config_digest="sha256:" + "b" * 64,
        device="cpu",
        hostname="unit-host",
        vram_limit_gb=None,
        universe=UniverseSummary(
            pair_count=6,
            symbol_map_digest="sha256:" + "c" * 64,
            universe_digest="sha256:" + "d" * 64,
            source="explicit",
        ),
        tier_level="manual",
        window=Window(
            start=datetime(2024, 9, 19, tzinfo=UTC),
            end=datetime(2026, 9, 19, tzinfo=UTC),
            resample="1h",
        ),
        objective=ObjectiveInfo(
            turnover_penalty_lambda=0.05,
            reachability_min_trades_90d=30,
            cost_model={"maker_bps": 1.0, "taker_bps": 4.0},
            min_after_cost_return=0.001,
        ),
        counts=GenerationCounts(
            proposed=2,
            rejected=RejectionCounts(reachability=1),
            registered=1,
        ),
        pool="pool_deadbeefdead",
        started_at=STARTED_AT,
        finished_at=FINISHED_AT,
        status="completed",
        termination="normal",
        reason=None,
    )


def _events(run_dir: Path) -> list[dict[str, JSONValue]]:
    path = run_dir / "events.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_new_run_id_is_safe_unique_and_creates_expected_directory(tmp_path: Path) -> None:
    ids = {new_run_id("manual", now=STARTED_AT) for _ in range(100)}

    assert len(ids) == 100
    assert all(re.fullmatch(r"[A-Za-z0-9._-]+", run_id) for run_id in ids)
    assert all(".." not in run_id and Path(run_id).parts == (run_id,) for run_id in ids)
    run_id = next(iter(ids))
    run_dir = generation_run_dir(run_id, reports_root=tmp_path)
    assert run_dir == tmp_path / "generation" / run_id
    assert run_dir.is_dir()


def test_write_config_is_canonical_and_ignores_only_runtime_keys(tmp_path: Path) -> None:
    first: dict[str, JSONValue] = {
        "quota": 5,
        "model": {"depth": 2, "kind": "manual"},
        "created_at": "old",
        "hostname": "host-a",
        "device": "cpu",
    }
    reordered_runtime_only: dict[str, JSONValue] = {
        "device": "cuda:0",
        "hostname": "host-b",
        "created_at": "new",
        "model": {"kind": "manual", "depth": 2},
        "quota": 5,
    }
    semantic_change: dict[str, JSONValue] = {"quota": 6, "model": first["model"]}
    stable_dir = tmp_path / "stable"

    first_digest = write_config(stable_dir, first)
    second_digest = write_config(stable_dir, reordered_runtime_only)
    changed_digest = write_config(tmp_path / "changed", semantic_change)

    expected: JSONValue = {"model": {"depth": 2, "kind": "manual"}, "quota": 5}
    content = (stable_dir / "config.json").read_bytes()
    assert first_digest.startswith("sha256:")
    assert first_digest == second_digest
    assert changed_digest != first_digest
    assert content == canonical_json_bytes(expected)
    assert json.loads(content) == expected


def test_append_candidate_rejected_writes_sequential_canonical_json_lines(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    first = append_candidate_rejected(
        run_dir,
        run_id="run-001",
        expression=("feature:close", "future:1"),
        reason_code="lookahead",
        detail="future offset",
        ts=STARTED_AT,
    )
    second = append_candidate_rejected(
        run_dir,
        run_id="run-001",
        expression=("feature:close", "unknown"),
        reason_code="unregistered_op",
        detail="unknown operator",
        ts=FINISHED_AT,
    )

    records = _events(run_dir)
    assert (first.event_seq, second.event_seq) == (1, 2)
    assert [record["event_seq"] for record in records] == [1, 2]
    assert all(record["event_type"] == "generation.candidate_rejected" for record in records)
    assert records[0]["payload"] == {
        "detail": "future offset",
        "expression": ["feature:close", "future:1"],
        "reason_code": "lookahead",
    }
    assert (run_dir / "events.jsonl").read_bytes().endswith(b"\n")


def test_finalize_completed_writes_manifest_once_and_one_completed_event(tmp_path: Path) -> None:
    run_dir = tmp_path / "completed"
    run = _completed_run()

    path = finalize_run(run_dir, run)

    payload = json.loads(path.read_text(encoding="utf-8"))
    records = _events(run_dir)
    assert path == run_dir / "run.json"
    assert payload["schema_version"] == RUN_SCHEMA_VERSION
    assert payload["status"] == "completed"
    assert payload["termination"] == "normal"
    assert payload["started_at"] == utc_iso(STARTED_AT)
    assert payload["finished_at"] == utc_iso(FINISHED_AT)
    assert [record["event_type"] for record in records] == ["generation.run_completed"]
    with pytest.raises(RunStoreError):
        finalize_run(run_dir, run)
    assert len(_events(run_dir)) == 1


@pytest.mark.parametrize(
    ("status", "termination", "reason", "pool"),
    (
        ("rejected", "invalid_binding", "digest mismatch", "pool_deadbeefdead"),
        ("failed", "RuntimeError", "training failed", "pool_deadbeefdead"),
        ("partial", "early", "SIGTERM", None),
    ),
)
def test_finalize_noncompleted_status_writes_no_completed_event(
    tmp_path: Path,
    status: RunStatus,
    termination: str,
    reason: str,
    pool: str | None,
) -> None:
    run_dir = tmp_path / status
    run = replace(
        _completed_run(),
        status=status,
        termination=termination,
        reason=reason,
        pool=pool,
    )

    path = finalize_run(run_dir, run)

    assert json.loads(path.read_text(encoding="utf-8"))["status"] == status
    assert not (run_dir / "events.jsonl").exists()


@pytest.mark.parametrize("status", ("rejected", "failed", "partial"))
def test_finalize_requires_reason_for_noncompleted_terminal_status(
    tmp_path: Path, status: RunStatus
) -> None:
    run = replace(_completed_run(), status=status, reason=None, pool=None)

    with pytest.raises(SchemaValidationError, match="reason"):
        finalize_run(tmp_path / status, run)


def test_finalize_rejects_partial_run_with_pool(tmp_path: Path) -> None:
    run = replace(_completed_run(), status="partial", reason="SIGTERM")

    with pytest.raises(SchemaValidationError, match="pool"):
        finalize_run(tmp_path / "partial", run)


def test_finalize_rejects_reverse_terminal_timestamps(tmp_path: Path) -> None:
    run = replace(_completed_run(), finished_at=STARTED_AT - timedelta(seconds=1))

    with pytest.raises(SchemaValidationError, match="finished_at"):
        finalize_run(tmp_path / "reverse-time", run)


def test_finalize_then_load_round_trip_preserves_all_fields(tmp_path: Path) -> None:
    run = _completed_run()
    path = finalize_run(tmp_path / "round-trip", run)

    assert load_run(path) == run


def test_load_run_rejects_unknown_schema_version(tmp_path: Path) -> None:
    path = finalize_run(tmp_path / "unknown-version", _completed_run())
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema_version"] = RUN_SCHEMA_VERSION + 1
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(UnknownSchemaVersionError):
        load_run(path)


@pytest.mark.parametrize(("mutation", "field"), (("extra", "verdict"), ("missing", "generator")))
def test_load_run_rejects_tampered_field_set(tmp_path: Path, mutation: str, field: str) -> None:
    path = finalize_run(tmp_path / mutation, _completed_run())
    payload = json.loads(path.read_text(encoding="utf-8"))
    if mutation == "extra":
        payload[field] = "pass"
    else:
        del payload[field]
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SchemaValidationError):
        load_run(path)


def test_finalize_retry_after_event_before_manifest_does_not_duplicate_event(
    tmp_path: Path,
) -> None:
    run_dir = tmp_path / "retry"
    run = _completed_run()
    write_config(run_dir, {"quota": 5})
    first_path = finalize_run(run_dir, run)
    first_path.unlink()

    retried_path = finalize_run(run_dir, run)

    assert retried_path.is_file()
    assert (run_dir / "config.json").is_file()
    assert [record["event_type"] for record in _events(run_dir)] == ["generation.run_completed"]
