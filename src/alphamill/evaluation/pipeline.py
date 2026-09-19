"""夹具信号的最小评测流水线（preview 与 canonical 共用；任务 T006/T013）。

把「信号 + 前瞻收益」夹具跑成五阶段结果与成本/样本量裁决。canonical 与 preview 的差别只在
`execution_tier`（决定 `approximation` 与信号来源分层），阶段口径完全一致——因此两处共用同一
实现，避免出现两套口径（`FR-003` 的失败语义、`FR-005` 的成本裁决）。

阶段适用性：因子运行的 `portfolio_transform` 与 `execution_implementation` 显式记
`NOT_APPLICABLE`（组合构建属 FR4/M3、执行链属 F006/M3），**不得记为 PASS**。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.required_statistics import member_statistics
from alphamill.evaluation.run_config import RunConfig
from alphamill.evaluation.signal_adapter import adapt_signal_records
from alphamill.factor_factory.bench.cost import evaluate_cost, load_cost_model
from alphamill.factor_factory.bench.minimal_backtest import TradeSummary, summarize
from alphamill.factor_factory.bench.signal_quality import (
    evaluate_signal_quality,
    signal_source_payload,
)
from alphamill.factor_factory.bench.stability import evaluate_temporal_stability
from alphamill.factor_factory.bench.stage_model import (
    SAMPLE_UNIT_OBSERVATIONS,
    SAMPLE_UNIT_ROUND_TRIPS,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_PASS,
    STATUS_UNDERPOWERED,
    StageResult,
    StageResults,
    not_applicable,
    sample_tier,
)

ADAPTER_VERSION = "f007-adapter-v1"
SIGNALS_DATASET = "signals_file"
PORTFOLIO_REASON = "FactorDef 运行不构建 PortfolioDef（组合构建属 FR4/M3）"
EXECUTION_REASON = "FactorDef 运行不含执行实现（执行链属 F006/M3）"


@dataclass(frozen=True)
class FixtureEvaluation:
    stage_results: StageResults
    cost_verdict: str
    sample_tier: str
    approximation: Mapping[str, Any]
    signal_provenance: Mapping[str, Any]
    trade_summary: Mapping[str, Any]
    cost_payload: Mapping[str, Any]
    period_returns: tuple[float, ...] = ()
    curve_times: tuple[str, ...] = ()
    required_statistics: Mapping[str, Any] | None = None


def _aggregate_panel(
    times: Sequence[str],
    symbols: Sequence[str],
    signals: Sequence[float],
    labels: Sequence[float],
) -> tuple[tuple[str, ...], tuple[float, ...], tuple[float, ...]]:
    """多标的面板按 timestamp 聚合成等权组合序列：消除跨标的虚假换手与时间戳回跳。"""
    grouped: dict[str, list[tuple[float, float]]] = {}
    for time, _symbol, signal, label in zip(times, symbols, signals, labels, strict=True):
        grouped.setdefault(str(time), []).append((float(signal), float(label)))
    ordered = sorted(grouped)
    return (
        tuple(ordered),
        tuple(sum(item[0] for item in grouped[time]) / len(grouped[time]) for time in ordered),
        tuple(sum(item[1] for item in grouped[time]) / len(grouped[time]) for time in ordered),
    )


def _panel_trade_summary(
    times: Sequence[str],
    symbols: Sequence[str],
    signals: Sequence[float],
    labels: Sequence[float],
) -> TradeSummary:
    """多标的面板：逐标的分组计算交易摘要后汇总，避免跨标的边界产生虚假换手。"""
    groups: dict[str, list[int]] = {}
    for index, symbol in enumerate(symbols):
        groups.setdefault(str(symbol), []).append(index)
    summaries = [
        summarize(
            [signals[index] for index in indices],
            [labels[index] for index in indices],
            [times[index] for index in indices],
        )
        for indices in groups.values()
    ]
    round_trips = sum(summary.round_trips for summary in summaries)
    n_observations = sum(summary.n_observations for summary in summaries)
    if round_trips > 0:
        sample_unit = SAMPLE_UNIT_ROUND_TRIPS
        trade_count = round_trips
    else:
        sample_unit = SAMPLE_UNIT_OBSERVATIONS
        trade_count = n_observations
    count = len(summaries)
    return TradeSummary(
        gross_return=sum(summary.gross_return for summary in summaries) / count,
        turnover=sum(summary.turnover for summary in summaries) / count,
        round_trips=round_trips,
        holding_period_hours=sum(summary.holding_period_hours for summary in summaries) / count,
        sample_unit=sample_unit,
        trade_count=trade_count,
        n_observations=n_observations,
    )


def evaluate_fixture(
    *,
    config: RunConfig,
    times: Sequence[str],
    signals: Sequence[float],
    labels: Sequence[float],
    execution_tier: str,
    observed_at: str,
    signal_source: str = "real",
    signal_column: str = "signal",
    label_column: str = "forward_return",
    symbols: Sequence[str] | None = None,
) -> FixtureEvaluation:
    """跑信号质量 + 成本/容量 + 时序稳定三阶段，并给出近似与来源标注。

    多标的面板先按 timestamp 聚合成等权组合序列再做成本/稳定性/曲线（避免把面板当单条序列），
    成员级必需统计仍用原始（含横截面）数据。
    """
    if symbols is not None and len({str(symbol) for symbol in symbols}) > 1:
        evaluation_times, evaluation_signals, evaluation_labels = _aggregate_panel(
            times, symbols, signals, labels
        )
    else:
        evaluation_times = tuple(str(stamp) for stamp in times)
        evaluation_signals = tuple(float(value) for value in signals)
        evaluation_labels = tuple(float(value) for value in labels)

    records = [
        {
            "time": time,
            "symbol": "fixture",
            "source": signal_source,
            signal_column: signal,
            label_column: label,
        }
        for time, signal, label in zip(times, signals, labels, strict=True)
    ]
    provenance = adapt_signal_records(
        records,
        dataset=SIGNALS_DATASET,
        adapter_version=ADAPTER_VERSION,
        signal_column=signal_column,
        label_column=label_column,
        horizons={signal_source: config.max_label_horizon},
    )[1]
    source_payload = signal_source_payload(provenance, execution_tier)

    _quality, quality_stage = evaluate_signal_quality(
        evaluation_signals,
        evaluation_labels,
        observed_at=observed_at,
        min_observations=config.min_observations,
    )
    if symbols is not None and len({str(symbol) for symbol in symbols}) > 1:
        trades = _panel_trade_summary(times, symbols, signals, labels)
    else:
        trades = summarize(evaluation_signals, evaluation_labels, evaluation_times)
    cost_result, cost_stage = evaluate_cost(
        gross_return=trades.gross_return,
        turnover_value=trades.turnover,
        round_trips=trades.round_trips,
        holding_period_hours_value=trades.holding_period_hours,
        cost_model=load_cost_model(config.cost_model.get("normalized", {})),
        observed_at=observed_at,
    )
    _stability, stability_stage = evaluate_temporal_stability(
        evaluation_signals, evaluation_labels, observed_at=observed_at
    )
    required_statistics, stats_stage = member_statistics(
        times=times,
        signals=signals,
        labels=labels,
        method_config=config.method_config,
        observed_at=observed_at,
        symbols=symbols,
    )
    stability_stage = _merge_statistics_stage(stability_stage, stats_stage)
    stage_results = StageResults(
        results=(
            quality_stage,
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, PORTFOLIO_REASON),
            cost_stage,
            stability_stage,
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, EXECUTION_REASON),
        )
    )
    return FixtureEvaluation(
        stage_results=stage_results,
        cost_verdict=cost_result.verdict,
        sample_tier=sample_tier(trades.trade_count, sample_unit=trades.sample_unit),
        approximation=source_payload["approximation"],
        signal_provenance=source_payload["signal_provenance"],
        trade_summary=trades.to_payload(),
        cost_payload=cost_result.to_payload(),
        period_returns=_net_period_returns(
            evaluation_signals,
            evaluation_labels,
            cost_model=load_cost_model(config.cost_model.get("normalized", {})),
            deciding_tier=cost_result.deciding_tier,
        ),
        curve_times=evaluation_times,
        required_statistics=required_statistics,
    )


def _merge_statistics_stage(stability_stage: StageResult, stats_stage: StageResult) -> StageResult:
    """成员级必需统计失败时，时序稳定阶段记 `INCOMPLETE`（不得为 PASS，`FR-003`）。"""
    if stats_stage.status == STATUS_PASS:
        return stability_stage
    reasons = [value for value in (stability_stage.reason, stats_stage.reason) if value]
    return StageResult(
        stage_id=STAGE_TEMPORAL_STABILITY,
        status=STATUS_INCOMPLETE,
        reason="; ".join(dict.fromkeys(reasons)) or None,
        failures=tuple(stability_stage.failures) + tuple(stats_stage.failures),
    )


def _net_period_returns(
    signals: Sequence[float],
    labels: Sequence[float],
    *,
    cost_model: Mapping[str, Any],
    deciding_tier: str,
) -> tuple[float, ...]:
    """逐期成本后收益：方向仓位 × 前瞻收益 − 该期换手成本（与成本裁决同口径同档位）。"""
    positions = [1.0 if value > 0 else (-1.0 if value < 0 else 0.0) for value in signals]
    total_bps = getattr(cost_model[deciding_tier], "total_bps", 0.0)
    previous = 0.0
    returns = []
    for position, label in zip(positions, labels, strict=True):
        drag = abs(position - previous) * total_bps * 1e-4
        returns.append(position * label - drag)
        previous = position
    return tuple(returns)


def first_failure(stage_results: StageResults) -> Mapping[str, Any] | None:
    """首个失败记录优先；无记录时回落到首个「不通过」阶段（`NOT_APPLICABLE` 不算失败）。"""
    ordered = stage_results.to_payload()
    for entry in ordered:
        if entry["failures"]:
            return {**entry["failures"][0], "stage": entry["stage"]}
    for entry in ordered:
        if entry["status"] in (STATUS_FAIL, STATUS_UNDERPOWERED, STATUS_INCOMPLETE):
            return {
                "stage": entry["stage"],
                "status": entry["status"],
                "reason": entry.get("reason"),
            }
    return None


def failure_text(failure: Mapping[str, Any] | None) -> str:
    if not failure:
        return "none"
    stage = failure.get("stage") or "?"
    detail = failure.get("reason") or failure.get("mechanism") or failure.get("error_code") or ""
    return f"{stage}:{detail}" if detail else str(stage)
