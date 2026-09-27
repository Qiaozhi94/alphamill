"""F012 代码检视回归：候选流水线（R-B3 起）。"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime

from _f012_pipeline_support import GOOD, PARAMS, _lines, _registry, _tensor

from alphamill.factor_factory.generators.candidate_pipeline import CandidatePipeline
from alphamill.factor_factory.generators.objective import CostModel, ObjectiveParams
from alphamill.factor_factory.registry.event_writer import RunEventWriter
from alphamill.factor_factory.registry.factor_store import feature_map_digest


def test_funding_channel_reaches_the_prefilter_cost(tmp_path) -> None:
    """R-B3：面板带 funding 通道且 funding_8h_bps>0 时，预筛成本后收益须扣资金费。"""
    base = _tensor()
    funding = "derivatives_funding_rates.funding_rate@1h"
    base.panel[funding] = 0.0001
    feature_map = {**base.feature_map, funding: len(base.feature_map)}
    panel = replace(
        base, feature_map=feature_map, feature_map_digest=feature_map_digest(feature_map)
    )
    returns = {}
    for bps in (0.0, 50.0):
        cost = CostModel(taker_fee_bps=0.0, maker_fee_bps=0.0, slippage_bps=0.0, funding_8h_bps=bps)
        params = ObjectiveParams(**{**vars(PARAMS), "cost_model": cost})
        writer = RunEventWriter(tmp_path / str(bps), run_id="alphagen_test")
        CandidatePipeline(
            panel=panel,
            objective_params=params,
            run_id="alphagen_test",
            writer=writer,
            compilers=_registry(),
            quota=5,
            generator_version="vendor-test",
            created_at=datetime(2026, 9, 27, tzinfo=UTC),
        ).offer(GOOD)
        writer.close()
        [row] = _lines(tmp_path / str(bps) / "prefilter.jsonl")
        returns[bps] = row["after_cost_return"]

    assert returns[50.0] < returns[0.0]
