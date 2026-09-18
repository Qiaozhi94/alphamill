"""preview 运行编排（`FR-001`/`UX-001`；任务 T006）。

一次 preview 的确定性流程：装载预注册配置 → 冻结/解析 ResearchSnapshot（latest 先冻结）→
构造语义上下文与 `experiment_id` → 计算代码/构建摘要 → 信号来源 provenance 与近似标注 →
跑最小阶段集（信号质量、成本/容量、时序稳定；组合与执行阶段显式 `NOT_APPLICABLE`）→
产出结构化结果与首屏。

边界：preview **只**写 `reports/preview/` 命名空间；Agent/preview 可读产物不得含最终确认窗或
留出字段（`NFR-003`）；preview 永不产生 `promotion_verdict`（cohort 级 verdict 只在 canonical
finalize 产出）。

design §4 的 preview CLI 没有 `--cohort` 参数，但上下文与身份需要 cohort 引用、首屏也要求显示
cohort：未显式给出时由 `run_config.preview_cohort_id` 派生一个**确定性 preview 专属引用**
（永不登记进 official population），使同一组语义输入的 preview 身份稳定且与 canonical 不混淆。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation.capabilities import assert_no_canonical_leak
from alphamill.evaluation.code_build import code_build_digest as compute_code_build_digest
from alphamill.evaluation.contract_common import TIER_PREVIEW
from alphamill.evaluation.run_config import (
    LABEL_COLUMN,
    SIGNAL_COLUMN,
    load_run_config,
    load_unified_frame,
    preview_cohort_id,
    resolve_snapshot,
)
from alphamill.evaluation.run_state import STATE_INCOMPLETE, STATE_PREVIEW_DONE
from alphamill.evaluation.signal_adapter import adapt_signal_records
from alphamill.experiment_store.experiment_context import (
    CONTEXT_SCHEMA_VERSION,
    ExperimentContext,
)
from alphamill.factor_factory.bench.cost import evaluate_cost, load_cost_model
from alphamill.factor_factory.bench.minimal_backtest import summarize
from alphamill.factor_factory.bench.signal_quality import (
    evaluate_signal_quality,
    signal_source_payload,
)
from alphamill.factor_factory.bench.stability import evaluate_temporal_stability
from alphamill.factor_factory.bench.stage_model import (
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_UNDERPOWERED,
    StageResults,
    not_applicable,
    sample_tier,
)

ADAPTER_VERSION = "f007-adapter-v1"
SIGNALS_DATASET = "signals_file"
DEFAULT_SIGNAL_SOURCE = "real"
PORTFOLIO_REASON = "FactorDef 运行不构建 PortfolioDef（组合构建属 FR4/M3）"
EXECUTION_REASON = "FactorDef 运行不含执行实现（执行链属 F006/M3）"


@dataclass(frozen=True)
class PreviewResult:
    execution_tier: str
    experiment_id: str
    cohort_id: str
    snapshot_id: str
    code_build_digest: str
    state: str
    cost_verdict: str
    sample_tier: str | None
    stage_results: StageResults
    approximation: Mapping[str, Any]
    signal_provenance: Mapping[str, Any]
    first_failure: Mapping[str, Any] | None

    @property
    def promotion_verdict(self) -> None:
        """preview 永不产生可晋级结论。"""
        return None

    def to_payload(self) -> dict[str, Any]:
        return {
            "execution_tier": self.execution_tier,
            "experiment_id": self.experiment_id,
            "cohort_id": self.cohort_id,
            "research_snapshot_id": self.snapshot_id,
            "code_build_digest": self.code_build_digest,
            "state": self.state,
            "cost_verdict": self.cost_verdict,
            "sample_tier": self.sample_tier,
            "promotion_verdict": self.promotion_verdict,
            "stages": self.stage_results.to_payload(),
            "approximation": dict(self.approximation),
            "signal_provenance": dict(self.signal_provenance),
            "first_failure": self.first_failure,
        }

    def first_screen(self) -> tuple[str, ...]:
        """CLI 首屏固定字段；顺序与内容被快照测试锁定（`UX-001`）。"""
        stages = " ".join(
            f"{entry['stage']}:{entry['status']}" for entry in self.stage_results.to_payload()
        )
        return (
            f"tier={self.execution_tier} cohort={self.cohort_id}",
            f"experiment_id={self.experiment_id}",
            f"data={self.snapshot_id}",
            f"code={self.code_build_digest}",
            f"state={self.state}",
            f"cost_verdict={self.cost_verdict} sample_tier={self.sample_tier}",
            f"promotion_verdict={self.promotion_verdict}",
            f"stages={stages}",
            f"approximation={self.approximation['is_approximate']}",
            f"first_failure={failure_text(self.first_failure)}",
        )


def failure_text(failure: Mapping[str, Any] | None) -> str:
    if not failure:
        return "none"
    stage = failure.get("stage") or "?"
    detail = failure.get("reason") or failure.get("mechanism") or failure.get("error_code") or ""
    return f"{stage}:{detail}" if detail else str(stage)


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


def run_preview(
    *,
    config_path: Path,
    factor_ref: str,
    seed: int,
    signals_path: Path,
    snapshot_id: str | None = None,
    latest: Sequence[str] | None = None,
    cutoff: str | None = None,
    symbol_map_digest: str | None = None,
    universe_digest: str | None = None,
    calendar_path: Path | None = None,
    cohort_id: str | None = None,
    signal_source: str = DEFAULT_SIGNAL_SOURCE,
    upstream_kind: str = "factor",
    observed_at: str | None = None,
) -> PreviewResult:
    config = load_run_config(config_path)
    snapshot = resolve_snapshot(
        snapshot_id=snapshot_id,
        latest=latest,
        cutoff=cutoff,
        symbol_map_digest=symbol_map_digest,
        universe_digest=universe_digest,
        calendar_path=calendar_path,
    )
    code_digest = compute_code_build_digest()
    cohort = cohort_id or preview_cohort_id(factor_ref, snapshot.snapshot_id)
    context = ExperimentContext(
        schema_version=CONTEXT_SCHEMA_VERSION,
        execution_tier=TIER_PREVIEW,
        upstream={"kind": upstream_kind, "id": factor_ref},
        cohort_id=cohort,
        method_config=config.method_config,
        window=config.window,
        cost_model=config.cost_model,
        research_snapshot_id=snapshot.snapshot_id,
        code_build_digest=code_digest,
        seed=seed,
    )

    times, signals, labels = load_unified_frame(signals_path)
    moment = observed_at or datetime.now(UTC).isoformat()
    records = [
        {
            "time": time,
            "symbol": "fixture",
            "source": signal_source,
            SIGNAL_COLUMN: signal,
            LABEL_COLUMN: label,
        }
        for time, signal, label in zip(times, signals, labels, strict=True)
    ]
    provenance = adapt_signal_records(
        records,
        dataset=SIGNALS_DATASET,
        adapter_version=ADAPTER_VERSION,
        signal_column=SIGNAL_COLUMN,
        label_column=LABEL_COLUMN,
        horizons={signal_source: config.max_label_horizon},
    )[1]
    source_payload = signal_source_payload(provenance, TIER_PREVIEW)

    _quality_metrics, quality_stage = evaluate_signal_quality(
        signals, labels, observed_at=moment, min_observations=config.min_observations
    )
    trades = summarize(signals, labels, times)
    cost_result, cost_stage = evaluate_cost(
        gross_return=trades.gross_return,
        turnover_value=trades.turnover,
        round_trips=trades.round_trips,
        holding_period_hours_value=trades.holding_period_hours,
        cost_model=load_cost_model(config.cost_model.get("normalized", {})),
        observed_at=moment,
    )
    _stability, stability_stage = evaluate_temporal_stability(signals, labels, observed_at=moment)

    stage_results = StageResults(
        results=(
            quality_stage,
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, PORTFOLIO_REASON),
            cost_stage,
            stability_stage,
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, EXECUTION_REASON),
        )
    )
    result = PreviewResult(
        execution_tier=TIER_PREVIEW,
        experiment_id=context.experiment_id,
        cohort_id=cohort,
        snapshot_id=snapshot.snapshot_id,
        code_build_digest=code_digest,
        state=STATE_PREVIEW_DONE if stage_results.evidence_complete else STATE_INCOMPLETE,
        cost_verdict=cost_result.verdict,
        sample_tier=sample_tier(trades.trade_count, sample_unit=trades.sample_unit),
        stage_results=stage_results,
        approximation=source_payload["approximation"],
        signal_provenance=source_payload["signal_provenance"],
        first_failure=first_failure(stage_results),
    )
    assert_no_canonical_leak(
        {"experiment_id": result.experiment_id, "sample_tier": result.sample_tier},
        agent_readable=True,
    )
    return result
