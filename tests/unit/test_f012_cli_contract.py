"""F012 CLI 契约（AC-006 / AC-007 / AC-005 CLI 侧）：生成器分发、manual 等价、run.json v2、partial。

alphagen 生成器本体（T014）以替身驱动：本文件只验 CLI 编排——config 合成、先建张量后卸载 Kronos、
层级与空宇宙拒绝、写者先于 finalize 关闭、partial 收尾。manual 等价的基准取自改动前 main
（84ab505）在同一夹具上的实跑产物（`tests/fixtures/f012/manual_baseline.json`）。
"""

from __future__ import annotations

import json
import os
import signal
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from test_f003_cli_contract import _build_cli_fixture, _prepare_mine_runtime, _read_mine_run

from alphamill.factor_factory import cli as cli_module
from alphamill.factor_factory import mine_dispatch
from alphamill.factor_factory.cli import EXIT_OK, EXIT_REJECTED, main
from alphamill.factor_factory.errors import FactorStoreError, SchemaValidationError
from alphamill.factor_factory.generators import base
from alphamill.factor_factory.generators.gpu_slot import AcquireCancelled, QueueRecord
from alphamill.factor_factory.generators.lake_tensor import TensorPanel
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry import factor_store
from alphamill.factor_factory.registry.factor_store import feature_map_digest

BASELINE = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures/f012/manual_baseline.json").read_text(
        encoding="utf-8"
    )
)
V2_FIELDS = ("budget", "stop_reason", "evaluations")
CLOSE, VOLUME = "ohlcv_1m.close@1h", "ohlcv_1m.volume@1h"


def _mine(tmp_path: Path, *extra: str, generator: str = "alphagen", allow_cpu: bool = True):
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    argv = ["mine", "--generator", generator, "--binding", str(binding_path), "--seed", "17"]
    argv += ["--allow-cpu"] if allow_cpu else []
    if generator == "alphagen" and "--config" not in extra:
        # F003 夹具的绑定只含 signals_log；张量本身由替身提供
        extra = (*extra, "--config", str(_config(tmp_path, {})))
    code = main([*argv, *extra], reports_root=reports_root, lake_root=lake_root)
    return code, reports_root


def _config(tmp_path: Path, body: dict) -> Path:
    path = tmp_path / "alphagen-config.json"
    path.write_text(json.dumps({"datasets": ["signals_log"], **body}), encoding="utf-8")
    return path


def _panel(*, masks: dict[str, bool] | None = None, extra_close: bool = False) -> TensorPanel:
    pairs = ("BTC-USDT", "ETH-USDT", "SOL-USDT")
    timestamps = pd.date_range("2026-08-01", periods=48, freq="1h", tz=UTC)
    index = pd.MultiIndex.from_product([timestamps, list(pairs)], names=["timestamp", "pair"])
    masks = masks or {"BTC-USDT": True, "ETH-USDT": True, "SOL-USDT": False}
    frame = pd.DataFrame(
        {
            CLOSE: np.linspace(100, 120, len(index)),
            VOLUME: np.linspace(1, 2, len(index)),
            "__in_universe__": [masks[pair] for _ in timestamps for pair in pairs],
        },
        index=index,
    )
    feature_map = {CLOSE: 0, VOLUME: 1}
    if extra_close:
        frame["other.close@1h"] = frame[CLOSE]
        feature_map["other.close@1h"] = 2
    return TensorPanel(
        datasets=("ohlcv_1m",),
        resample="1h",
        pairs=pairs,
        timestamps=timestamps,
        panel=frame,
        feature_map=feature_map,
        feature_map_digest=feature_map_digest(feature_map),
        universe_source="explicit:test",
    )


@dataclass
class _Calls:
    offload: int = 0
    restore: int = 0
    build_tensor: int = 0


@pytest.fixture()
def alphagen_runtime(monkeypatch):
    """替身：合成张量 + 替身生成器（写一条拒绝事件、入册一个真实 alphagen 因子）。"""
    calls = _Calls()
    state: dict = {"panel": _panel(), "stop_reason": "quota_reached", "tensor_error": None}
    _prepare_mine_runtime(monkeypatch)

    def fake_build_tensor(validated, **kwargs):
        calls.build_tensor += 1
        state["tensor_kwargs"] = kwargs
        if state["tensor_error"] is not None:
            raise state["tensor_error"]
        if state.get("on_build"):
            state["on_build"]()
        return state["panel"]

    class _StubGenerator:
        name = "alphagen"

        def __init__(self, ctx) -> None:
            self._ctx = ctx

        def produce(self, request: base.GenerationRequest) -> base.GenerationResult:
            assert request.panel is state["panel"]
            self._ctx.writer.rejected(("feature:close", "mean"), "lookahead", "no window")
            factor = factor_store.build_factor(
                hypothesis=DEFAULT_CATALOG.require("mechanism_unknown"),
                name="alphagen",
                generator="alphagen",
                generator_version="vendor-test",
                scope="cross_sectional",
                expression=(f"feature:{CLOSE}", "delta:5"),
                params={},
                feature_map=request.panel.feature_map,
                run_id=self._ctx.run_id,
                created_at=datetime(2026, 9, 27, tzinfo=UTC),
            )
            counts = base.GenerationCounts(
                proposed=2, rejected=base.RejectionCounts(lookahead=1), registered=1
            )
            return base.GenerationResult(
                run_id=self._ctx.run_id,
                factors=[factor],
                pool=None,
                counts=counts,
                device="cpu",
                tier_level="L0",
                stop_reason=state["stop_reason"],
                evaluations=37,
                budget={"quota": request.quota, "total_timesteps": 64, "pool_capacity": 10},
            )

    def offload(config):
        calls.offload += 1
        return cli_module.gpu_slot.KronosOffloadOutcome(
            action="stopped",
            reason="vram_released",
            vram_before_gb=3.0,
            vram_after_gb=1.0,
            restore_required=True,
        )

    def restore(config, outcome):
        calls.restore += 1
        return True

    monkeypatch.setattr(mine_dispatch, "build_tensor", fake_build_tensor)
    monkeypatch.setattr(mine_dispatch, "_build_alphagen", _StubGenerator)
    monkeypatch.setattr(cli_module, "resolve_kronos_offload", offload)
    monkeypatch.setattr(cli_module, "restore_kronos_if_needed", restore)
    return calls, state


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
