"""F012 候选流水线单元测试的共享面板、参数与流水线工厂。"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import numpy as np
import pandas as pd

from alphamill.factor_factory.generators.alphagen_adapter import register_alphagen_compiler
from alphamill.factor_factory.generators.candidate_pipeline import CandidatePipeline
from alphamill.factor_factory.generators.expression_compiler import compile_postfix
from alphamill.factor_factory.generators.lake_tensor import TensorPanel
from alphamill.factor_factory.generators.objective import CostModel, ObjectiveParams
from alphamill.factor_factory.registry.compiler_registry import CompilerRegistry
from alphamill.factor_factory.registry.event_writer import RunEventWriter
from alphamill.factor_factory.registry.factor_store import feature_map_digest

FEATURES = {"ohlcv_1m.close@1h": 0, "ohlcv_1m.volume@1h": 1}
PARAMS = ObjectiveParams(
    turnover_penalty_lambda=0.0,
    reachability_min_trades_90d=1,
    cost_model=CostModel(taker_fee_bps=0.0, maker_fee_bps=0.0, slippage_bps=0.0),
    min_after_cost_return=-1.0,
)
CLOSE, VOLUME = "ohlcv_1m.close@1h", "ohlcv_1m.volume@1h"
GOOD = ("feature:close", "delta:5")
GOOD_2 = ("feature:volume", "delta:5")


def _panel(
    values: np.ndarray, *, pairs=("AAA", "BBB", "CCC"), hours: int = 24 * 100
) -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=hours, freq="1h", tz=UTC)
    index = pd.MultiIndex.from_product([timestamps, pairs], names=["timestamp", "pair"])
    rng = np.random.default_rng(7)
    close = 100 + rng.standard_normal(len(index)).cumsum() * 0.01
    return pd.DataFrame(
        {"close": np.abs(close) + 1.0, "__in_universe__": True, "signal": values.reshape(-1)},
        index=index,
    )


def _lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _tensor(*, hours: int = 24 * 120, pairs=("AAA", "BBB", "CCC", "DDD")) -> TensorPanel:
    timestamps = pd.date_range("2026-01-01", periods=hours, freq="1h", tz=UTC)
    index = pd.MultiIndex.from_product([timestamps, list(pairs)], names=["timestamp", "pair"])
    rng = np.random.default_rng(11)
    walk = rng.standard_normal((hours, len(pairs))).cumsum(axis=0) * 0.5 + 100.0
    frame = pd.DataFrame(
        {
            CLOSE: walk.reshape(-1),
            VOLUME: rng.uniform(10, 20, hours * len(pairs)),
            "__in_universe__": True,
        },
        index=index,
    )
    feature_map = {CLOSE: 0, VOLUME: 1}
    return TensorPanel(
        datasets=("ohlcv_1m",),
        resample="1h",
        pairs=tuple(pairs),
        timestamps=timestamps,
        panel=frame,
        feature_map=feature_map,
        feature_map_digest=feature_map_digest(feature_map),
        universe_source="explicit",
    )


def _registry() -> CompilerRegistry:
    registry = CompilerRegistry({"manual": compile_postfix})
    register_alphagen_compiler(registry)
    return registry


def make_pipeline_factory(tmp_path):
    made = {}

    def make(*, quota: int = 50, panel: TensorPanel | None = None, on_quota=None, params=PARAMS):
        writer = RunEventWriter(tmp_path, run_id="alphagen_test")
        pipeline = CandidatePipeline(
            panel=panel or _tensor(),
            objective_params=params,
            run_id="alphagen_test",
            writer=writer,
            compilers=_registry(),
            quota=quota,
            generator_version="vendor-test",
            created_at=datetime(2026, 9, 27, tzinfo=UTC),
            on_quota=on_quota,
        )
        made["writer"] = writer
        return pipeline

    make.tmp_path = tmp_path
    make.made = made
    return make
