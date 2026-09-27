"""F012 候选流水线（单元层）：通道绑定、截面仓位、事件线性写出、流水线拒绝路径（AC-003/004）。"""

from __future__ import annotations

import json
import time
from datetime import UTC

import numpy as np
import pandas as pd
import pytest

from alphamill.factor_factory.errors import ChannelConflictError, MissingChannelError
from alphamill.factor_factory.generators.channel_binding import bind_feature_tokens, channel_index
from alphamill.factor_factory.generators.objective import (
    CostModel,
    ObjectiveParams,
    evaluate_objective,
)
from alphamill.factor_factory.registry import run_schema
from alphamill.factor_factory.registry.event_writer import RunEventWriter

FEATURES = {"ohlcv_1m.close@1h": 0, "ohlcv_1m.volume@1h": 1}
PARAMS = ObjectiveParams(
    turnover_penalty_lambda=0.0,
    reachability_min_trades_90d=1,
    cost_model=CostModel(taker_fee_bps=0.0, maker_fee_bps=0.0, slippage_bps=0.0),
    min_after_cost_return=-1.0,
)


# ------------------------------------------------------------------ 通道绑定（T004）


def test_vendor_feature_tokens_bind_to_lake_channels() -> None:
    channels = channel_index(FEATURES)

    bound = bind_feature_tokens(("feature:close", "feature:volume", "corr:10"), channels)

    assert bound == ("feature:ohlcv_1m.close@1h", "feature:ohlcv_1m.volume@1h", "corr:10")


def test_token_without_lake_channel_raises_missing_channel() -> None:
    with pytest.raises(MissingChannelError, match="vwap"):
        bind_feature_tokens(("feature:vwap", "mean:10"), channel_index(FEATURES))


def test_duplicate_basename_across_datasets_is_a_conflict() -> None:
    with pytest.raises(ChannelConflictError, match="close"):
        channel_index({"ohlcv_1m.close@1h": 0, "other.close@1h": 1})


# ------------------------------------------------------------------ 截面仓位规则（T005）


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


def test_cs_median_turns_an_always_positive_rank_into_long_short_positions() -> None:
    """截面排名取值恒在 (0,1]：sign 规则下永远满仓做多、零交易；cs_median 下有多有空、有交易。"""
    hours, pairs = 24 * 100, 3
    rng = np.random.default_rng(3)
    ranks = np.argsort(rng.random((hours, pairs)), axis=1).argsort(axis=1) + 1.0
    frame = _panel(ranks / pairs)

    by_sign = evaluate_objective(frame, params=PARAMS)
    by_median = evaluate_objective(frame, params=PARAMS, position_rule="cs_median")

    assert by_sign.trades_90d == 0
    assert by_median.trades_90d > 0
    assert by_median.turnover > 0


def test_unknown_position_rule_is_rejected() -> None:
    from alphamill.factor_factory.errors import SchemaValidationError

    frame = _panel(np.ones(24 * 100 * 3))
    with pytest.raises(SchemaValidationError, match="position_rule"):
        evaluate_objective(frame, params=PARAMS, position_rule="rank")


# ------------------------------------------------------------------ 事件写者（T006）


def _lines(path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_writer_appends_rejections_with_versioned_envelope_and_sequence(tmp_path) -> None:
    (tmp_path / "events.jsonl").write_text(
        json.dumps({"event_seq": 1, "event_type": "generation.candidate_rejected"}) + "\n",
        encoding="utf-8",
    )
    writer = RunEventWriter(tmp_path, run_id="alphagen_x")

    first = writer.rejected(("feature:close", "mean"), "lookahead", "no window")
    second = writer.rejected(
        ("feature:close",), "duplicate_definition", "dup", definition_digest="sha256:" + "a" * 64
    )
    writer.prefilter({"definition_digest": "sha256:" + "a" * 64, "outcome": "registered"})
    writer.close()

    events = _lines(tmp_path / "events.jsonl")
    assert [e["event_seq"] for e in events] == [1, 2, 3]
    assert (first.event_seq, second.event_seq) == (2, 3)
    assert events[1]["schema_version"] == run_schema.EVENT_SCHEMA_VERSION
    assert events[1]["payload"] == {
        "expression": ["feature:close", "mean"],
        "reason_code": "lookahead",
        "detail": "no window",
    }
    assert events[2]["payload"]["definition_digest"] == "sha256:" + "a" * 64
    assert _lines(tmp_path / "prefilter.jsonl") == [
        {"definition_digest": "sha256:" + "a" * 64, "outcome": "registered"}
    ]


def test_writer_rejects_unknown_reason_code(tmp_path) -> None:
    from alphamill.factor_factory.errors import SchemaValidationError

    writer = RunEventWriter(tmp_path, run_id="alphagen_x")
    with pytest.raises(SchemaValidationError):
        writer.rejected(("feature:close",), "bogus", "")
    writer.close()


def test_writer_cost_grows_linearly_with_event_count(tmp_path) -> None:
    """AC-004 / NFR-005：事件写出不回读文件，万级事件耗时近似线性。"""

    def cost(n: int, sub: str) -> float:
        writer = RunEventWriter(tmp_path / sub, run_id="alphagen_x")
        started = time.perf_counter()
        for _ in range(n):
            writer.rejected(("feature:close", "mean:10"), "reachability", "zero trades")
        writer.close()
        return time.perf_counter() - started

    small, large = cost(2_000, "small"), cost(10_000, "large")

    assert large < 10.0
    assert large / max(small, 1e-6) < 10.0, (small, large)
    assert len(_lines(tmp_path / "large" / "events.jsonl")) == 10_000


def test_events_written_before_run_json_keep_a_continuous_sequence(tmp_path) -> None:
    """close() 先于 finalize：finalize 内 _append_event 读到的行数与写者写出的一致。"""
    writer = RunEventWriter(tmp_path, run_id="alphagen_x", fsync_every=10_000)
    for _ in range(3):
        writer.rejected(("feature:close",), "unregistered_op", "x")
    writer.close()
    assert [e["event_seq"] for e in _lines(tmp_path / "events.jsonl")] == [1, 2, 3]
