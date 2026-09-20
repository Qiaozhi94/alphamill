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


class _AvailableVram:
    free_gb = 8.0


def _prepare_mine_runtime(
    monkeypatch: pytest.MonkeyPatch,
    *,
    window_open: bool = True,
    vram: _AvailableVram | None = None,
) -> list[bool]:
    from alphamill.factor_factory import cli as cli_module

    capability_calls: list[bool] = []

    def require_capabilities(*, require_cuda: bool) -> None:
        capability_calls.append(require_cuda)

    monkeypatch.setattr(cli_module, "require_mining_capabilities", require_capabilities)
    monkeypatch.setattr(
        cli_module.gpu_slot,
        "in_training_window",
        lambda _now, *, window_start, window_end, window_tz: window_open,
    )
    monkeypatch.setattr(cli_module.gpu_slot, "query_vram", lambda: vram)
    return capability_calls


def _read_mine_run(
    reports_root: Path,
) -> tuple[Path, dict[str, JSONValue], list[dict[str, JSONValue]]]:
    [run_path] = sorted((reports_root / "generation").glob("*/run.json"))
    run = json.loads(run_path.read_text(encoding="utf-8"))
    events_path = run_path.parent / "events.jsonl"
    events = (
        [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines()]
        if events_path.exists()
        else []
    )
    return run_path, run, events


def _assert_mine_rejected(
    reports_root: Path, exit_code: int, *, termination: str
) -> dict[str, JSONValue]:
    run_path, run, events = _read_mine_run(reports_root)
    assert exit_code == EXIT_REJECTED
    assert run["status"] == "rejected"
    assert run["termination"] == termination
    assert run["reason"]
    assert run["started_at"]
    assert run["finished_at"]
    assert not list((run_path.parent / "factors").glob("*.json"))
    assert "generation.run_completed" not in [event["event_type"] for event in events]
    return run


def test_mine_manual_allow_cpu_completes_and_writes_factors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    capability_calls = _prepare_mine_runtime(monkeypatch)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--allow-cpu",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    run_path, run, events = _read_mine_run(reports_root)
    assert exit_code == EXIT_OK
    assert run["status"] == "completed"
    assert run["device"] == "cpu"
    assert list((run_path.parent / "factors").glob("*.json"))
    assert [event["event_type"] for event in events] == ["generation.run_completed"]
    assert capability_calls == [False]


def test_mine_missing_binding_writes_rejected_terminal_run(tmp_path: Path) -> None:
    reports_root = tmp_path / "reports"

    exit_code = main(
        ["mine", "--generator", "manual", "--seed", "17", "--allow-cpu"],
        reports_root=reports_root,
        lake_root=tmp_path / "lake",
    )

    _assert_mine_rejected(reports_root, exit_code, termination="missing_binding")


def test_mine_invalid_binding_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    payload = json.loads(binding_path.read_text(encoding="utf-8"))
    payload["members"]["signals_log"]["value_digest"] = "sha256:" + "f" * 64
    binding_path.write_text(json.dumps(payload), encoding="utf-8")
    _prepare_mine_runtime(monkeypatch)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--allow-cpu",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    run = _assert_mine_rejected(reports_root, exit_code, termination="invalid_binding")
    assert "value_digest" in str(run["reason"])


def test_mine_unknown_tier_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    config_path = tmp_path / "unknown-tier.json"
    config_path.write_text('{"tier_level":"unknown"}', encoding="utf-8")
    _prepare_mine_runtime(monkeypatch)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--config",
            str(config_path),
            "--allow-cpu",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="unknown_tier")


def test_mine_outside_training_window_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    capability_calls = _prepare_mine_runtime(monkeypatch, window_open=False)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="outside_training_window")
    assert capability_calls == [True]


def test_mine_without_cuda_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    capability_calls = _prepare_mine_runtime(monkeypatch)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="cuda_unavailable")
    assert capability_calls == [True]


def test_mine_capability_failure_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from alphamill.factor_factory import cli as cli_module

    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)

    def reject_capabilities(*, require_cuda: bool) -> None:
        raise cli_module.errors.MiningCapabilityError(f"capability unavailable: {require_cuda}")

    monkeypatch.setattr(cli_module, "require_mining_capabilities", reject_capabilities)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--allow-cpu",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="capability_unavailable")


def test_mine_allow_offhours_and_cpu_bypasses_resource_refusals(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch, window_open=False)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--allow-cpu",
            "--allow-offhours",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _, run, events = _read_mine_run(reports_root)
    assert exit_code == EXIT_OK
    assert run["status"] == "completed"
    assert [event["event_type"] for event in events] == ["generation.run_completed"]


def test_mine_defaults_are_expanded_in_canonical_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--allow-cpu",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    run_path, _, _ = _read_mine_run(reports_root)
    config = json.loads((run_path.parent / "config.json").read_text(encoding="utf-8"))
    assert exit_code == EXIT_OK
    assert config["tier_level"] == "manual"
    assert config["quota"] > 0
    assert config["window"]["preset"] == DEFAULT_WINDOW_PRESET
    assert config["window"]["start"]
    assert config["window"]["end"]
    assert config["window"]["resample"] == "1h"


def _patch_offload(monkeypatch: pytest.MonkeyPatch, action: str, reason: str) -> list[str | None]:
    from alphamill.factor_factory import cli as cli_module
    from alphamill.factor_factory.generators.gpu_slot import KronosOffloadOutcome

    seen: list[str | None] = []

    def offload(*, control_url: str | None, **_kwargs) -> KronosOffloadOutcome:
        seen.append(control_url)
        return KronosOffloadOutcome(
            action=action, reason=reason, vram_before_gb=3.0, vram_after_gb=0.2
        )

    monkeypatch.setattr(cli_module.gpu_slot, "offload_kronos", offload)
    return seen


def test_mine_fail_closed_offload_rejects_before_taking_the_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R003 判红点：夜槽卸载判 fail_closed 时必须拒绝，且不得取锁。"""
    from alphamill.factor_factory import cli as cli_module

    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch, vram=_AvailableVram())
    _patch_offload(monkeypatch, "fail_closed", "vram_not_released")
    acquired: list[str] = []
    monkeypatch.setattr(
        cli_module.gpu_slot.GpuSlot,
        "acquire",
        lambda _self, run_id, **_kwargs: acquired.append(run_id),
    )

    exit_code = main(
        ["mine", "--generator", "manual", "--binding", str(binding_path), "--seed", "17"],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    run = _assert_mine_rejected(reports_root, exit_code, termination="kronos_offload_failed")
    assert acquired == [], "卸载失败仍取锁 = 与 Kronos 抢同一张卡"
    assert run["kronos_offload"]["action"] == "fail_closed"


def test_mine_records_kronos_offload_outcome_in_run_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-010：运行记录须持久化 kronos_offload（含前后显存读数）。"""
    from alphamill.factor_factory import cli as cli_module

    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch, vram=_AvailableVram())
    seen = _patch_offload(monkeypatch, "stopped", "vram_released")
    monkeypatch.setattr(
        cli_module.gpu_slot.GpuSlot, "acquire", lambda _self, run_id, **_kwargs: None
    )
    monkeypatch.setattr(
        cli_module.gpu_slot.GpuSlot, "release", lambda _self, run_id, **_kwargs: None
    )
    config_path = tmp_path / "mine.json"
    config_path.write_text(
        json.dumps({"tier_level": "manual", "kronos_control_url": "http://127.0.0.1:8002"}),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--config",
            str(config_path),
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _, run, _ = _read_mine_run(reports_root)
    assert exit_code == EXIT_OK
    assert seen == ["http://127.0.0.1:8002"], "控制面地址必须来自配置，不得写死"
    assert run["kronos_offload"] == {
        "action": "stopped",
        "reason": "vram_released",
        "vram_before_gb": 3.0,
        "vram_after_gb": 0.2,
    }


def test_mine_restores_kronos_after_stopping_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R012 判红点：停了 Kronos 就必须恢复，否则白天 dry-run 一直没有实时信号。

    取锁失败这条路径尤其容易漏——卡没拿到，Kronos 却已经被停了。
    """
    from alphamill.factor_factory import cli as cli_module

    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch, vram=_AvailableVram())
    _patch_offload(monkeypatch, "stopped", "vram_released")
    restored: list[str | None] = []
    monkeypatch.setattr(
        cli_module.gpu_slot,
        "restore_kronos",
        lambda *, control_url, contract_version: restored.append(control_url) or True,
    )

    def refuse(_self, run_id: str, **_kwargs) -> None:
        raise cli_module.gpu_slot.GpuQueueTimeoutError(
            record=cli_module.gpu_slot.QueueRecord(
                queue_seq=1,
                run_id=run_id,
                event="timeout",
                ts=datetime(2026, 9, 19, 23, tzinfo=UTC),
                vram_free_gb=8.0,
            )
        )

    monkeypatch.setattr(cli_module.gpu_slot.GpuSlot, "acquire", refuse)
    config_path = tmp_path / "mine.json"
    config_path.write_text(
        json.dumps({"tier_level": "manual", "kronos_control_url": "http://127.0.0.1:8002"}),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
            "--config",
            str(config_path),
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="queue_timeout")
    assert restored == ["http://127.0.0.1:8002"], "取锁失败也必须把 Kronos 恢复回去"


def test_mine_queue_timeout_writes_rejected_terminal_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from alphamill.factor_factory import cli as cli_module
    from alphamill.factor_factory.generators.gpu_slot import QueueRecord

    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    _prepare_mine_runtime(monkeypatch, vram=_AvailableVram())
    _patch_offload(monkeypatch, "not_needed", "cpu_instance")

    def timeout(
        _slot, run_id: str, *, now: datetime | None = None, ignore_window: bool = False
    ) -> None:
        raise cli_module.gpu_slot.GpuQueueTimeoutError(
            record=QueueRecord(
                queue_seq=1,
                run_id=run_id,
                event="timeout",
                ts=datetime(2026, 9, 19, 23, tzinfo=UTC),
                vram_free_gb=8.0,
            )
        )

    monkeypatch.setattr(cli_module.gpu_slot.GpuSlot, "acquire", timeout)

    exit_code = main(
        [
            "mine",
            "--generator",
            "manual",
            "--binding",
            str(binding_path),
            "--seed",
            "17",
        ],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    _assert_mine_rejected(reports_root, exit_code, termination="queue_timeout")
