"""F003 CLI 契约：IR-001、IR-003、AC-011、AC-012。"""

from __future__ import annotations

import json
import socket
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from alphamill.data_bridge import digest as lake_digest
from alphamill.data_bridge import manifest, partitions, symbol_map
from alphamill.data_bridge import paths as lake_paths
from alphamill.data_bridge.registry import require_dataset
from alphamill.factor_factory.canonical import (
    JSONValue,
    canonical_json_bytes,
    sha256_prefixed_bytes,
)
from alphamill.factor_factory.cli import EXIT_OK, EXIT_REJECTED, main
from alphamill.factor_factory.generators.base import DEFAULT_SEED_QUOTA, DEFAULT_WINDOW_PRESET


def _artifact_digest(payload: JSONValue) -> str:
    return sha256_prefixed_bytes(canonical_json_bytes(payload))


def _build_cli_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    lake_root = tmp_path / "lake"
    reports_root = tmp_path / "reports"
    spec = require_dataset("signals_log")
    event_time = datetime(2026, 9, 11, 9, tzinfo=UTC)
    rows = [
        [
            event_time,
            "binance",
            "BTC/USDT",
            "placeholder",
            "buy",
            0.9,
            {},
            event_time,
            0.01,
            0.2,
            0.6,
            None,
            None,
        ]
    ]
    partition_path = lake_root / "signals_log/date=2026-09-11.r1.parquet"
    partition_path.parent.mkdir(parents=True)
    pq.write_table(partitions.rows_to_table(rows, spec), partition_path)

    mapping = symbol_map.build_symbol_map([symbol_map.SymbolRow("binance", "spot", "BTC/USDT")])
    mapping_payload = symbol_map.canonical_csv_bytes(mapping)
    symbol_digest = symbol_map.content_digest(mapping_payload)
    symbol_path = lake_paths.symbol_maps_dir(lake_root) / f"{symbol_digest}.csv"
    symbol_path.parent.mkdir(parents=True)
    symbol_path.write_bytes(mapping_payload)

    partition_entry = {
        "logical_partition_key": {"date": "2026-09-11"},
        "path": partition_path.relative_to(lake_root).as_posix(),
        "rows": 1,
        "time_min": "2026-09-11T09:00:00Z",
        "time_max": "2026-09-11T09:00:00Z",
        "row_digest": lake_digest.row_digest(rows, spec.projection),
        "bytes": partition_path.stat().st_size,
        "sha256": manifest.file_sha256(partition_path),
    }
    value_digest = manifest.compute_value_digest(spec, [partition_entry])
    manifest_path = manifest.publish_manifest(
        lake_root,
        {
            "dataset": "signals_log",
            "source": manifest.SOURCE_TAG,
            "data_version": "v2026.09.11",
            "status": "valid",
            "rows": 1,
            "value_digest": value_digest,
            "symbol_map_digest": symbol_digest,
            "partitions": [partition_entry],
        },
    )

    universe_payload: JSONValue = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": None,
            }
        ],
    }
    universe_digest = _artifact_digest(universe_payload)
    universe_path = tmp_path / "artifacts/universe" / f"{universe_digest}.json"
    universe_path.parent.mkdir(parents=True)
    universe_path.write_bytes(canonical_json_bytes(universe_payload))

    calendar_payload: JSONValue = {
        "schema_version": 1,
        "kind": "continuous_24_7",
        "timezone": "UTC",
    }
    calendar_digest = _artifact_digest(calendar_payload)
    calendar_path = tmp_path / "artifacts/calendar" / f"{calendar_digest}.json"
    calendar_path.parent.mkdir(parents=True)
    calendar_path.write_bytes(canonical_json_bytes(calendar_payload))

    combined_digest = _artifact_digest({"universe": universe_digest, "calendar": calendar_digest})
    artifact_path = tmp_path / "artifacts/bindings" / f"{combined_digest}.json"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_text("{}", encoding="utf-8")
    binding_path = tmp_path / "binding.json"
    binding_path.write_bytes(
        canonical_json_bytes(
            {
                "mode": "explicit_tuples",
                "schema_version": 1,
                "cutoff_time": "2026-09-12T00:00:00Z",
                "members": {
                    "signals_log": {
                        "data_version": "v2026.09.11",
                        "value_digest": value_digest,
                        "as_of_fidelity": "bitemporal",
                        "event_time_min": "2026-09-11T09:00:00Z",
                        "event_time_max": "2026-09-11T09:00:00Z",
                    }
                },
                "symbol_map_digest": symbol_digest,
                "universe": {
                    "digest": universe_digest,
                    "path": universe_path.as_posix(),
                    "schema_version": 1,
                },
                "calendar": {
                    "digest": calendar_digest,
                    "path": calendar_path.as_posix(),
                    "schema_version": 1,
                },
                "universe_calendar_digest": combined_digest,
                "provenance": {
                    "created_at": "2026-09-12T01:00:00Z",
                    "artifact_path": artifact_path.as_posix(),
                    "member_manifest_paths": {"signals_log": manifest_path.as_posix()},
                    "symbol_map_path": symbol_path.as_posix(),
                    "universe_path": universe_path.as_posix(),
                    "calendar_path": calendar_path.as_posix(),
                },
            }
        )
    )
    return lake_root, reports_root, binding_path


def _run_completed_seed(tmp_path: Path) -> tuple[Path, Path, Path]:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    exit_code = main(
        ["seed", "--generator", "manual", "--binding", str(binding_path), "--seed", "17"],
        reports_root=reports_root,
        lake_root=lake_root,
    )
    assert exit_code == EXIT_OK
    [run_path] = sorted((reports_root / "generation").glob("*/run.json"))
    return reports_root, binding_path, run_path


def test_seed_completes_five_factors_and_restores_guards(tmp_path: Path) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    original_socket = socket.socket

    exit_code = main(
        ["seed", "--generator", "manual", "--binding", str(binding_path), "--seed", "17"],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    [run_path] = sorted((reports_root / "generation").glob("*/run.json"))
    run_dir = run_path.parent
    run = json.loads(run_path.read_text(encoding="utf-8"))
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    events = [
        json.loads(line)
        for line in (run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert exit_code == EXIT_OK
    assert run["status"] == "completed"
    assert len(list((run_dir / "factors").glob("*.json"))) == 5
    assert [event["event_type"] for event in events] == ["generation.run_completed"]
    assert config["quota"] == DEFAULT_SEED_QUOTA
    assert config["window"]["preset"] == DEFAULT_WINDOW_PRESET
    assert socket.socket is original_socket


def test_missing_binding_writes_rejected_terminal_run(tmp_path: Path) -> None:
    reports_root = tmp_path / "reports"

    exit_code = main(
        ["seed", "--generator", "manual", "--seed", "17"],
        reports_root=reports_root,
        lake_root=tmp_path / "lake",
    )

    [run_path] = sorted((reports_root / "generation").glob("*/run.json"))
    run = json.loads(run_path.read_text(encoding="utf-8"))
    assert exit_code == EXIT_REJECTED
    assert run["status"] == "rejected"
    assert run["termination"] == "missing_binding"
    assert run["reason"] == "--binding is required"
    assert not (run_path.parent / "events.jsonl").exists()


def test_invalid_binding_writes_rejected_terminal_run(tmp_path: Path) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    payload = json.loads(binding_path.read_text(encoding="utf-8"))
    payload["members"]["signals_log"]["value_digest"] = "sha256:" + "f" * 64
    binding_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(
        ["seed", "--generator", "manual", "--binding", str(binding_path), "--seed", "17"],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    [run_path] = sorted((reports_root / "generation").glob("*/run.json"))
    run = json.loads(run_path.read_text(encoding="utf-8"))
    assert exit_code == EXIT_REJECTED
    assert run["status"] == "rejected"
    assert run["termination"] == "invalid_binding"
    assert "value_digest" in run["reason"]


def test_show_run_prints_completed_manifest(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reports_root, _, run_path = _run_completed_seed(tmp_path)
    capsys.readouterr()

    exit_code = main(["show", "--run", run_path.parent.name], reports_root=reports_root)

    output = capsys.readouterr().out
    assert exit_code == EXIT_OK
    assert run_path.parent.name in output
    assert '"status": "completed"' in output


def test_show_factor_prints_definition_and_occurrences(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    reports_root, _, run_path = _run_completed_seed(tmp_path)
    [factor_path, *_] = sorted((run_path.parent / "factors").glob("*.json"))
    factor = json.loads(factor_path.read_text(encoding="utf-8"))
    capsys.readouterr()

    exit_code = main(["show", "--factor", factor["factor_id"]], reports_root=reports_root)

    output = json.loads(capsys.readouterr().out)
    assert exit_code == EXIT_OK
    assert output["definition_digest"] == factor["definition_digest"]
    assert output["occurrences"] == [
        {
            "finished_at": json.loads(run_path.read_text(encoding="utf-8"))["finished_at"],
            "run_id": run_path.parent.name,
            "status": "completed",
        }
    ]


@pytest.mark.parametrize(
    ("flag", "identifier"), (("--run", "missing-run"), ("--factor", "missing"))
)
def test_show_unknown_artifact_is_rejected(
    tmp_path: Path,
    flag: str,
    identifier: str,
) -> None:
    exit_code = main(["show", flag, identifier], reports_root=tmp_path / "reports")

    assert exit_code == EXIT_REJECTED


def test_show_rejects_unknown_run_schema_version(tmp_path: Path) -> None:
    reports_root, _, run_path = _run_completed_seed(tmp_path)
    payload = json.loads(run_path.read_text(encoding="utf-8"))
    payload["schema_version"] = 999
    run_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = main(["show", "--run", run_path.parent.name], reports_root=reports_root)

    assert exit_code == EXIT_REJECTED
