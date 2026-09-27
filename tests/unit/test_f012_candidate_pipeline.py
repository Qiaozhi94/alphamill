"""F012 候选流水线（单元层）：通道绑定、截面仓位、事件线性写出、流水线拒绝路径（AC-003/004）。"""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime

import numpy as np
import pytest
from _f012_pipeline_support import (
    CLOSE,
    FEATURES,
    GOOD,
    GOOD_2,
    PARAMS,
    VOLUME,
    _lines,
    _panel,
    _registry,
    _tensor,
    make_pipeline_factory,
)

from alphamill.factor_factory.errors import ChannelConflictError, MissingChannelError
from alphamill.factor_factory.generators.candidate_pipeline import (
    CandidatePipeline,
    Registered,
    Rejected,
)
from alphamill.factor_factory.generators.channel_binding import bind_feature_tokens, channel_index
from alphamill.factor_factory.generators.objective import (
    ObjectiveParams,
    evaluate_objective,
)
from alphamill.factor_factory.registry import run_schema
from alphamill.factor_factory.registry.event_writer import RunEventWriter

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


# ------------------------------------------------------------------ 候选流水线（T007）


@pytest.fixture()
def pipeline_factory(tmp_path):
    return make_pipeline_factory(tmp_path)


def test_tradable_expression_is_registered_as_alphagen_factor(pipeline_factory) -> None:
    pipeline = pipeline_factory()

    outcome = pipeline.offer(GOOD)

    assert isinstance(outcome, Registered), outcome
    factor = outcome.factor
    assert factor.generator == "alphagen"
    assert factor.hypothesis_id == "mechanism_unknown"
    assert factor.meta["expression"] == [f"feature:{CLOSE}", "delta:5"]
    assert pipeline.counts().registered == 1


@pytest.mark.parametrize(
    ("tokens", "code", "detail"),
    [
        (("feature:vwap", "mean:10"), "unregistered_op", "missing_channel:vwap"),
        (("feature:close", "mean"), "lookahead", "requires a strictly positive integer window"),
        (("feature:close", "ts_rank:20"), "unregistered_op", "not registered: 'ts_rank'"),
        (("feature:close", "constant:0", "mul"), "reachability", "trades_90d=0"),
        (("feature:close", "constant:0", "div"), "reachability", "degenerate_signal"),
    ],
)
def test_rejection_paths_map_to_funnel_reason_codes(pipeline_factory, tokens, code, detail) -> None:
    pipeline = pipeline_factory()

    outcome = pipeline.offer(tokens)

    assert isinstance(outcome, Rejected), outcome
    assert outcome.reason_code == code
    assert detail in outcome.detail


def test_duplicate_definition_is_rejected_by_digest(pipeline_factory) -> None:
    pipeline = pipeline_factory()

    assert isinstance(pipeline.offer(GOOD), Registered)
    second = pipeline.offer(GOOD)

    assert isinstance(second, Rejected) and second.reason_code == "duplicate_definition"


def test_degenerate_candidate_seen_twice_is_a_duplicate(pipeline_factory) -> None:
    """检视 D45：编译成功即入 seen，被拒的退化表达式再次出现判 duplicate，不重算信号。"""
    pipeline = pipeline_factory()
    tokens = ("feature:close", "constant:0", "div")

    pipeline.offer(tokens)
    again = pipeline.offer(tokens)

    assert isinstance(again, Rejected) and again.reason_code == "duplicate_definition"


def test_counts_are_conserved_and_match_rejection_events(pipeline_factory) -> None:
    pipeline = pipeline_factory()
    offers = [GOOD, GOOD, ("feature:vwap", "mean:10"), ("feature:close", "mean"), GOOD_2]
    for tokens in offers:
        pipeline.offer(tokens)
    pipeline_factory.made["writer"].close()

    counts = pipeline.counts()
    rejected = counts.rejected
    total_rejected = (
        rejected.unregistered_op
        + rejected.lookahead
        + rejected.reachability
        + rejected.duplicate_definition
    )
    assert counts.proposed == len(offers) == counts.registered + total_rejected
    events = _lines(pipeline_factory.tmp_path / "events.jsonl")
    by_code: dict[str, int] = {}
    for event in events:
        code = event["payload"]["reason_code"]
        by_code[code] = by_code.get(code, 0) + 1
    assert by_code == {
        code: n for code, n in vars(rejected).items() if n
    }  # 含 reachability（R-C9）
    prefilter = _lines(pipeline_factory.tmp_path / "prefilter.jsonl")
    assert {row["outcome"] for row in prefilter} <= {"registered", "rejected"}
    assert len(prefilter) == counts.registered + rejected.reachability


def test_quota_stops_counting_further_candidates(pipeline_factory) -> None:
    calls = []
    pipeline = pipeline_factory(quota=1, on_quota=lambda: calls.append(1))

    assert isinstance(pipeline.offer(GOOD), Registered)
    assert pipeline.offer(GOOD_2) is None

    assert calls == [1]
    assert pipeline.counts().proposed == 1
    assert pipeline.stopped


def test_missing_close_bars_are_masked_not_fatal(pipeline_factory) -> None:
    """检视 D32/D41：重采样缺口的 close 缺失视为未观测，不使运行失败，计数留痕。"""
    panel = _tensor()
    panel.panel.iloc[::7, panel.panel.columns.get_loc(CLOSE)] = np.nan
    pipeline = pipeline_factory(panel=panel)

    outcome = pipeline.offer(("feature:volume", "delta:5"))

    assert isinstance(outcome, (Registered, Rejected))
    rows = _lines(pipeline_factory.tmp_path / "prefilter.jsonl")
    assert rows and rows[-1]["masked_bars"] > 0


# ------------------------------------------------------------------ AC-003 / AC-004 补足（T015）


@pytest.mark.parametrize(
    "tokens", [("feature:close", "constant:x", "add"), ("unrenderable:TypeError",)]
)
def test_malformed_token_is_a_candidate_rejection_not_a_run_failure(
    pipeline_factory, tokens
) -> None:
    pipeline = pipeline_factory()

    outcome = pipeline.offer(tokens)

    assert isinstance(outcome, Rejected) and outcome.reason_code == "unregistered_op"
    assert outcome.detail.startswith("malformed:")
    assert isinstance(pipeline.offer(GOOD), Registered), "拒绝后运行继续"


def test_all_nan_signal_is_rejected_as_degenerate(pipeline_factory) -> None:
    panel = _tensor()
    panel.panel[VOLUME] = np.nan
    pipeline = pipeline_factory(panel=panel)

    outcome = pipeline.offer(("feature:volume", "delta:5"))

    assert isinstance(outcome, Rejected) and outcome.reason_code == "reachability"
    assert outcome.detail == "degenerate_signal:no_observation"


@pytest.mark.parametrize(
    "overrides",
    [{"reachability_min_trades_90d": 10**6}, {"min_after_cost_return": 1.0e9}],
    ids=["too_few_trades", "after_cost_below_threshold"],
)
def test_candidates_below_the_prefilter_thresholds_are_rejected(
    pipeline_factory, overrides
) -> None:
    params = ObjectiveParams(**{**vars(PARAMS), **overrides})
    pipeline = pipeline_factory(params=params)

    outcome = pipeline.offer(GOOD)

    assert isinstance(outcome, Rejected) and outcome.reason_code == "reachability"
    [row] = _lines(pipeline_factory.tmp_path / "prefilter.jsonl")
    assert row["outcome"] == "rejected" and row["trades_90d"] > 0


def test_prefilter_metrics_stay_out_of_factor_identity(tmp_path, pipeline_factory) -> None:
    """预筛指标只进 prefilter.jsonl：换一套阈值，同一表达式的 definition_digest 不变。"""
    from alphamill.factor_factory.registry import factor_store

    first = pipeline_factory().offer(GOOD)
    lenient = ObjectiveParams(**{**vars(PARAMS), "min_after_cost_return": -5.0})
    writer = RunEventWriter(tmp_path / "other", run_id="alphagen_test")
    second = CandidatePipeline(
        panel=_tensor(),
        objective_params=lenient,
        run_id="alphagen_test",
        writer=writer,
        compilers=_registry(),
        quota=5,
        generator_version="vendor-test",
        created_at=datetime(2026, 9, 27, tzinfo=UTC),
    ).offer(GOOD)
    writer.close()

    dto = factor_store.factor_to_dto(first.factor)
    assert dto.definition_digest == factor_store.factor_to_dto(second.factor).definition_digest
    body = factor_store.write(tmp_path / "written", first.factor).read_text(encoding="utf-8")
    for metric in ("turnover", "trades_90d", "after_cost_return", "masked_bars"):
        assert metric not in body
