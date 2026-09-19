"""canonical 事务执行体（从 `canonical.py` 拆出以守住单文件上限）。

`run_canonical` 负责前置校验、claim 与复用分支；本模块承载取得单写权后真正执行的
「方法论入口门禁 → 分阶段评测 → 原子发布 → 终态登记」流程。
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from alphamill.evaluation import publisher
from alphamill.evaluation.canonical_registration import registered_events
from alphamill.evaluation.canonical_result import CanonicalResult
from alphamill.evaluation.capabilities import TierContext
from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import (
    EVENT_RUN_STATE_CHANGED,
    RunEvent,
    build_event,
    events_digest,
)
from alphamill.evaluation.pipeline import evaluate_fixture
from alphamill.evaluation.rejection import (
    REAL_SOURCE_ANNOTATION,
    register_rejection,
    rejected_stage_results,
)
from alphamill.evaluation.run_config import RunConfig, load_unified_panel
from alphamill.evaluation.run_state import (
    STATE_CREATED,
    STATE_EVIDENCE_READY,
    STATE_INCOMPLETE,
    STATE_REGISTERED,
    STATE_REJECTED,
    STATE_RUNNING,
    STATE_VALIDATING,
)
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.promotion import PromotionInputs, derive_promotion_verdict
from alphamill.factor_factory.bench.curves import build_equity_curves
from alphamill.factor_factory.bench.stage_model import STAGE_SIGNAL_QUALITY
from alphamill.validation.methodology_gate import GuardContext, evaluate_methodology
from alphamill.validation.no_lookahead import (
    STATUS_NOT_YET_AVAILABLE,
    STATUS_PASS,
    build_no_lookahead,
)


def _run_events(experiment_id: str, cohort_id: str, terminal_state: str) -> tuple[RunEvent, ...]:
    def event(source: str, target: str, sequence: int, stage: str = "") -> RunEvent:
        return build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=source,
            to_state=target,
            event_type=EVENT_RUN_STATE_CHANGED,
            stage=stage,
            sequence=sequence,
        )

    return (
        event(STATE_CREATED, STATE_VALIDATING, 0),
        event(STATE_VALIDATING, STATE_RUNNING, 1, "signal_quality"),
        event(STATE_RUNNING, terminal_state, 2, "temporal_stability"),
    )


def execute_canonical(
    *,
    reports: Path,
    tier_context: TierContext,
    config: RunConfig,
    experiment_id: str,
    cohort_id: str,
    candidate_id: str,
    factor_ref: str,
    object_id: str | None,
    signals_path: Path,
    snapshot: rs.ResearchSnapshot,
    expression: str,
    code_digest: str,
    observed_at: str | None,
) -> CanonicalResult:
    verdict = evaluate_methodology(
        expression=expression,
        declared_capabilities=("operator",),
        context=GuardContext(
            max_label_horizon=config.max_label_horizon, embargo=config.max_label_horizon
        ),
    )
    moment = observed_at or datetime.now(UTC).isoformat()
    if not verdict.passed:
        published = register_rejection(
            tier_context=tier_context,
            reports=reports,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            snapshot_id=snapshot.snapshot_id,
            object_id=object_id or factor_ref,
            expression=expression,
            observed_at=moment,
            violation_message="; ".join(item.message for item in verdict.violations),
            code_build_digest=code_digest,
        )
        return CanonicalResult(
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            snapshot_id=snapshot.snapshot_id,
            code_build_digest=code_digest,
            state=STATE_REJECTED,
            cost_verdict="cost_undetermined",
            sample_tier="underpowered",
            stage_results=rejected_stage_results(
                stage_id=STAGE_SIGNAL_QUALITY, expression=expression, observed_at=moment
            ),
            approximation=dict(REAL_SOURCE_ANNOTATION),
            promotion_verdict="rejected",
            artifact_dir=str(published),
            reused=False,
        )

    times, symbols, signals, labels = load_unified_panel(signals_path)
    evaluation = evaluate_fixture(
        config=config,
        times=times,
        signals=signals,
        labels=labels,
        execution_tier=TIER_CANONICAL,
        observed_at=moment,
        symbols=symbols,
    )
    terminal_state = (
        STATE_EVIDENCE_READY if evaluation.stage_results.evidence_complete else STATE_INCOMPLETE
    )
    member_events = registered_events(experiment_id, cohort_id, candidate_id)
    events = _run_events(experiment_id, cohort_id, terminal_state) + member_events
    curves = build_equity_curves(
        evaluation.period_returns, times=[datetime.fromisoformat(stamp) for stamp in times]
    )
    promotion = derive_promotion_verdict(
        PromotionInputs(
            run_state=terminal_state,
            stage_results=evaluation.stage_results,
            sample_tier=evaluation.sample_tier,
            cost_verdict=evaluation.cost_verdict,
            no_lookahead=build_no_lookahead(
                l1_status=STATUS_PASS,
                l1_evidence_refs=(f"expression_sha256:{expression}",),
                l2_status=STATUS_NOT_YET_AVAILABLE,
                l3_status=STATUS_NOT_YET_AVAILABLE,
            ),
        )
    )
    registration = {
        "schema_version": 1,
        "experiment_id": experiment_id,
        "cohort_id": cohort_id,
        "candidate_id": candidate_id,
        "registered_at": moment,
    }
    request = publisher.PublishRequest(
        experiment_id=experiment_id,
        manifest={
            "schema_version": 1,
            "execution_tier": TIER_CANONICAL,
            "experiment_id": experiment_id,
            "state": terminal_state,
            "events_digest": events_digest(events),
            "research_snapshot_id": snapshot.snapshot_id,
            "object_id": object_id or factor_ref,
            "cohort_id": cohort_id,
            "candidate_id": candidate_id,
            "sample_tier": evaluation.sample_tier,
            "cost_verdict": evaluation.cost_verdict,
            "approximation": dict(evaluation.approximation),
            "no_lookahead": build_no_lookahead(
                l1_status=STATUS_PASS,
                l1_evidence_refs=(f"expression_sha256:{expression}",),
                l2_status=STATUS_NOT_YET_AVAILABLE,
                l3_status=STATUS_NOT_YET_AVAILABLE,
            ).to_payload(),
            "stage_results": evaluation.stage_results.to_payload(),
        },
        report={
            "schema_version": 1,
            "experiment_id": experiment_id,
            "approximation": dict(evaluation.approximation),
            "signal_provenance": dict(evaluation.signal_provenance),
            "cost": dict(evaluation.cost_payload),
            "trade_summary": dict(evaluation.trade_summary),
            "curves_summary": curves.scalar_summary(),
            "stage_results": evaluation.stage_results.to_payload(),
            "required_statistics": evaluation.required_statistics,
        },
        curves=curves,
        events=events,
        registration=registration,
        object_id=object_id or factor_ref,
        snapshot_id=snapshot.snapshot_id,
    )
    published = publisher.publish(tier_context, request)
    population.register_member(
        reports,
        cohort_id,
        population.MemberRegistration(
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            run_state=STATE_REGISTERED,
            promotion_verdict=promotion,
            sample_tier=evaluation.sample_tier,
            cost_model_version=str(config.cost_model.get("id", "")),
            evidence_ref=f"{published.relative_to(reports).as_posix()}/curves.parquet",
        ),
        member_events[0],
    )
    return CanonicalResult(
        experiment_id=experiment_id,
        cohort_id=cohort_id,
        candidate_id=candidate_id,
        snapshot_id=snapshot.snapshot_id,
        code_build_digest=code_digest,
        state=terminal_state,
        cost_verdict=evaluation.cost_verdict,
        sample_tier=evaluation.sample_tier,
        stage_results=evaluation.stage_results,
        approximation=evaluation.approximation,
        promotion_verdict=None,
        artifact_dir=str(published),
        reused=False,
    )
