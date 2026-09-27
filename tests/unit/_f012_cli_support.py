"""F012 CLI 契约测试的共享夹具：F003 夹具上的 mine 调用、合成张量与替身生成器。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from test_f003_cli_contract import _build_cli_fixture, _prepare_mine_runtime

from alphamill.factor_factory import cli as cli_module
from alphamill.factor_factory import mine_dispatch
from alphamill.factor_factory.cli import main
from alphamill.factor_factory.generators import base
from alphamill.factor_factory.generators.lake_tensor import TensorPanel
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG
from alphamill.factor_factory.registry import factor_store
from alphamill.factor_factory.registry.factor_store import feature_map_digest

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


def install_alphagen_runtime(monkeypatch):
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
            if state.get("produce_error") is not None:  # 训练期异常注入（检视 R-A1/R-A2）
                raise state["produce_error"]
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
    monkeypatch.setattr(mine_dispatch, "warm_training_runtime", lambda: None)
    monkeypatch.setattr(cli_module, "resolve_kronos_offload", offload)
    monkeypatch.setattr(cli_module, "restore_kronos_if_needed", restore)
    return calls, state
