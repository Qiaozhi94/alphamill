"""F012 CLI 契约（AC-006 / AC-007 / AC-005 CLI 侧）：生成器分发、manual 等价、run.json v2、partial。

alphagen 生成器本体（T014）以替身驱动：本文件只验 CLI 编排——config 合成、先建张量后卸载 Kronos、
层级与空宇宙拒绝、写者先于 finalize 关闭、partial 收尾。manual 等价的基准取自改动前 main
（84ab505）在同一夹具上的实跑产物（`tests/fixtures/f012/manual_baseline.json`）。
"""

from __future__ import annotations

import json
import os
import signal
from datetime import UTC, datetime
from pathlib import Path

import pytest
from _f012_cli_support import _config, _mine, _panel, install_alphagen_runtime
from test_f003_cli_contract import _prepare_mine_runtime, _read_mine_run

from alphamill.factor_factory import cli as cli_module
from alphamill.factor_factory.cli import EXIT_OK, EXIT_REJECTED, main
from alphamill.factor_factory.errors import FactorStoreError, SchemaValidationError
from alphamill.factor_factory.generators.gpu_slot import AcquireCancelled, QueueRecord
from alphamill.factor_factory.registry import factor_store

BASELINE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures/f012/manual_baseline.json").read_text(
        encoding="utf-8"
    )
)
V2_FIELDS = ("budget", "stop_reason", "evaluations")


@pytest.fixture()
def alphagen_runtime(monkeypatch):
    return install_alphagen_runtime(monkeypatch)


# ------------------------------------------------------------------ manual 等价（FR-006）


def _strip(body: dict, keys) -> dict:
    return {k: v for k, v in body.items() if k not in keys}


def test_manual_mine_is_observably_equivalent_to_pre_f012_baseline(tmp_path, monkeypatch) -> None:
    """检视 D13/D26：因子去易变字段后逐字节一致，config_digest 不变，run.json 去易变字段后相等。"""
    _prepare_mine_runtime(monkeypatch)
    code, reports_root = _mine(tmp_path, generator="manual")

    run_path, run, events = _read_mine_run(reports_root)
    assert code == EXIT_OK
    factors = {}
    for path in sorted((run_path.parent / "factors").glob("*.json")):
        body = json.loads(path.read_text(encoding="utf-8"))
        factors[path.name] = _strip(body, {"run_id", "created_at"})
    assert factors == BASELINE["factors"]
    assert run["config_digest"] == BASELINE["config_digest"]
    volatile = {"run_id", "started_at", "finished_at", "hostname", "schema_version", *V2_FIELDS}
    stable = json.loads(json.dumps(_strip(run, volatile)).replace(str(tmp_path), "<TMP>"))
    stable["objective"] = _strip(stable["objective"], {"position_rule"})
    assert stable == BASELINE["run"]
    assert run["schema_version"] == 2
    assert run["budget"] == {"quota": 5, "total_timesteps": None, "pool_capacity": None}
    assert (run["stop_reason"], run["evaluations"]) == (None, None)
    assert run["objective"]["position_rule"] == "sign"
    assert [e["event_type"] for e in events] == BASELINE["event_types"]


def test_unknown_generator_is_rejected_by_argument_parsing(tmp_path) -> None:
    with pytest.raises(SystemExit) as info:
        main(["mine", "--generator", "gp", "--seed", "1"], reports_root=tmp_path)
    assert info.value.code == 2


# ------------------------------------------------------------------ alphagen 分发（FR-006/007/008）


def test_alphagen_mine_writes_truthful_v2_manifest(tmp_path, alphagen_runtime, capsys) -> None:
    calls, state = alphagen_runtime

    code, reports_root = _mine(tmp_path, "--quota", "3")

    run_path, run, events = _read_mine_run(reports_root)
    assert code == EXIT_OK, run
    assert run["status"] == "completed" and run["stop_reason"] == "quota_reached"
    assert run["generator"] == "alphagen" and run["tier_level"] == "L0"
    assert run["budget"] == {"quota": 3, "total_timesteps": 64, "pool_capacity": 10}
    assert run["evaluations"] == 37
    assert run["universe"]["pair_count"] == 2, "窗口内曾在宇宙的 pair 数（SOL 从未入宇宙）"
    assert run["objective"]["position_rule"] == "cs_median"
    assert run["engine"]["code_digest"] != run["config_digest"]
    assert run["pool"] is None
    assert [e["event_seq"] for e in events] == list(range(1, len(events) + 1))
    assert [e["event_type"] for e in events] == [
        "generation.candidate_rejected",
        "generation.run_completed",
    ]
    kwargs = state["tensor_kwargs"]
    assert kwargs["start"] < kwargs["end"] and kwargs["resample"] == "1h"
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert summary["status"] == "completed" and summary["stop_reason"] == "quota_reached"
    assert summary["counts"] == run["counts"] and summary["vram_peak_gb"] is None  # cpu


def test_partial_objective_config_is_deep_merged(tmp_path, alphagen_runtime) -> None:
    """检视 D44：用户只给部分 objective 键时 position_rule 仍为 cs_median。"""
    config = _config(tmp_path, {"objective": {"reachability_min_trades_90d": 10}})

    code, reports_root = _mine(tmp_path, "--config", str(config))

    run_path, run, _ = _read_mine_run(reports_root)
    stored = json.loads((run_path.parent / "config.json").read_text(encoding="utf-8"))
    assert code == EXIT_OK, run
    assert stored["objective"]["reachability_min_trades_90d"] == 10
    assert stored["objective"]["position_rule"] == "cs_median"
    assert run["objective"]["reachability_min_trades_90d"] == 10


def test_alphagen_rejects_a_non_l0_tier(tmp_path, alphagen_runtime) -> None:
    config = _config(tmp_path, {"tier_level": "L1"})

    code, reports_root = _mine(tmp_path, "--config", str(config))

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_REJECTED and run["termination"] == "unknown_tier"


@pytest.mark.parametrize(
    ("setup", "termination"),
    [
        ("empty_universe", "invalid_binding"),
        ("zero_rows", "invalid_binding"),
        ("channel_conflict", "invalid_config"),
    ],
)
def test_bad_tensor_is_rejected_before_kronos_offload(
    tmp_path, alphagen_runtime, monkeypatch, setup, termination
) -> None:
    """检视 D21/D34/D35：张量先于 Kronos 卸载构建，坏张量不白卸载 Kronos。"""
    calls, state = alphagen_runtime
    monkeypatch.setattr(
        cli_module.gpu_slot, "query_vram", lambda: type("V", (), {"free_gb": 8.0})()
    )
    if setup == "empty_universe":
        state["panel"] = _panel(masks=dict.fromkeys(("BTC-USDT", "ETH-USDT", "SOL-USDT"), False))
    elif setup == "zero_rows":
        state["tensor_error"] = SchemaValidationError("tensor dataset returned zero rows")
    else:
        state["panel"] = _panel(extra_close=True)

    code, reports_root = _mine(tmp_path, allow_cpu=False)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_REJECTED and run["termination"] == termination, run
    assert calls.offload == 0


# --------------------------------------------------------- partial（FR-005 / AC-005 CLI 侧）


def test_generator_stopping_for_window_writes_partial(tmp_path, alphagen_runtime) -> None:
    _, state = alphagen_runtime
    state["stop_reason"] = "window_closed"

    code, reports_root = _mine(tmp_path)

    run_path, run, events = _read_mine_run(reports_root)
    assert code == EXIT_OK
    assert run["status"] == "partial" and run["termination"] == "window_closed"
    assert "已入册 1/" in run["reason"] and run["pool"] is None
    [factor_path] = sorted((run_path.parent / "factors").glob("*.json"))
    with pytest.raises(FactorStoreError):
        factor_store.load(factor_path)
    assert "generation.run_completed" not in [e["event_type"] for e in events]


def test_interrupt_while_queueing_is_partial_and_restores_kronos(
    tmp_path, alphagen_runtime, monkeypatch
) -> None:
    calls, _ = alphagen_runtime
    monkeypatch.setattr(
        cli_module.gpu_slot, "query_vram", lambda: type("V", (), {"free_gb": 8.0})()
    )

    def cancelled(self, run_id, **kwargs):
        # 排队中收到 SIGTERM；只有 CLI 把信号标志作为 cancel 传进来，等待循环才会出队（检视 R-C3）
        os.kill(os.getpid(), signal.SIGTERM)
        cancel = kwargs.get("cancel")
        assert cancel is not None and cancel(), "cancel 须反映信号标志"
        record = QueueRecord(
            queue_seq=1, run_id=run_id, event="cancelled", ts=datetime.now(UTC), vram_free_gb=None
        )
        raise AcquireCancelled(record=record)

    monkeypatch.setattr(cli_module.gpu_slot.GpuSlot, "acquire", cancelled)

    code, reports_root = _mine(tmp_path, allow_cpu=False)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_OK
    assert run["status"] == "partial" and run["stop_reason"] == "interrupted"
    assert run["counts"]["registered"] == 0
    assert calls.offload == 1 and calls.restore == 1


def test_sigterm_before_training_is_partial(tmp_path, alphagen_runtime) -> None:
    _, state = alphagen_runtime
    state["on_build"] = lambda: os.kill(os.getpid(), signal.SIGTERM)
    previous = signal.getsignal(signal.SIGTERM)

    code, reports_root = _mine(tmp_path)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_OK
    assert run["status"] == "partial" and run["stop_reason"] == "interrupted"
    assert signal.getsignal(signal.SIGTERM) == previous


@pytest.mark.parametrize("stop_reason", ["window_closed", "interrupted"])
def test_training_stop_on_gpu_path_is_partial_releases_slot_and_restores_kronos(
    tmp_path, alphagen_runtime, monkeypatch, stop_reason
) -> None:
    """AC-005：训练中夜槽结束 / SIGTERM → partial；已入册落盘但不可加载；槽释放、Kronos 恢复。"""
    calls, state = alphagen_runtime
    state["stop_reason"] = stop_reason
    monkeypatch.setattr(
        cli_module.gpu_slot, "query_vram", lambda: type("V", (), {"free_gb": 8.0})()
    )
    slot_events: list[str] = []

    def acquire(self, run_id, **kwargs):
        slot_events.append("acquire")
        return QueueRecord(
            queue_seq=1, run_id=run_id, event="acquired", ts=datetime.now(UTC), vram_free_gb=8.0
        )

    monkeypatch.setattr(cli_module.gpu_slot.GpuSlot, "acquire", acquire)
    monkeypatch.setattr(
        cli_module.gpu_slot.GpuSlot,
        "release",
        lambda self, run_id, **kw: slot_events.append("release"),
    )

    code, reports_root = _mine(tmp_path, allow_cpu=False)

    run_path, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_OK
    assert (run["status"], run["stop_reason"], run["termination"]) == (
        "partial",
        stop_reason,
        stop_reason,
    )
    assert run["reason"].startswith("已入册 1/") and run["pool"] is None
    assert run["device"] == "cuda" and run["vram_limit_gb"] is not None
    assert run["kronos_offload"]["action"] == "stopped"
    assert run["universe"]["source"] and run["universe"]["pair_count"] == 2
    [factor_path] = sorted((run_path.parent / "factors").glob("*.json"))
    with pytest.raises(FactorStoreError):
        factor_store.load(factor_path)
    assert slot_events == ["acquire", "release"]
    assert calls.offload == 1 and calls.restore == 1
