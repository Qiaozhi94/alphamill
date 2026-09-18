"""方法论/纯度门拒绝后的终态登记（`spec.md` §5；任务 T016）。

`spec.md` §5 与 §5 不变量要求：方法论/纯度门入口失败是 `VALIDATING -> REJECTED` 的**终态结论**——
必须照常发布 `evaluation.registered` 终态登记并计入 cohort 漏斗分母，**不得因失败而缺席登记**，
也不得携带任何 PASS-like 结论。因此拒绝路径不是「抛错退出」，而是「跑出一个 REJECTED 结论」。

被拒运行的五阶段记录：拒绝阶段记 `FAIL` + 三维失败记录（`mechanism=lookahead`）；下游两个必需
阶段（成本/容量、时序稳定）因入口即被拒而**未执行**，记 `INCOMPLETE` 并给出原因——不得记为
`PASS`，也不得伪装成 `NOT_APPLICABLE`（必需阶段不允许 NOT_APPLICABLE）。曲线侧车为中性单点，
并在 report 中显式标注 `evaluation=not_run_after_methodology_rejection`。
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation import publisher
from alphamill.evaluation.canonical_result import CanonicalResult
from alphamill.evaluation.capabilities import TierContext
from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    EVENT_REGISTERED,
    EVENT_RUN_STATE_CHANGED,
    RunEvent,
    build_event,
    events_digest,
)
from alphamill.evaluation.run_state import (
    STATE_CREATED,
    STATE_REGISTERED,
    STATE_REJECTED,
    STATE_VALIDATING,
)
from alphamill.experiment_store import population
from alphamill.factor_factory.bench.curves import build_equity_curves
from alphamill.factor_factory.bench.stage_model import (
    STAGE_COST_CAPACITY,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_SIGNAL_QUALITY,
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    FailureRecord,
    StageResult,
    StageResults,
    not_applicable,
)
from alphamill.validation.methodology_gate import ERROR_CODE

NOT_EVALUATED = "方法论门拒绝后未执行"
NOT_RUN_MARKER = "not_run_after_methodology_rejection"
NEUTRAL_CURVE = (0.0,)
REAL_SOURCE_ANNOTATION: dict[str, Any] = {
    "is_approximate": False,
    "reduced_dimensions": [],
    "signal_source": "real",
}


def rejected_stage_results(*, stage_id: str, expression: str, observed_at: str) -> StageResults:
    failure = FailureRecord(
        stage=stage_id,
        owner="method",
        mechanism="lookahead",
        error_code=ERROR_CODE,
        first_seen=observed_at,
        evidence_refs=(f"expression_sha256:{expression}",),
    )
    return StageResults(
        results=(
            StageResult(stage_id=stage_id, status=STATUS_FAIL, failures=(failure,)),
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合"),
            StageResult(STAGE_COST_CAPACITY, STATUS_INCOMPLETE, reason=NOT_EVALUATED),
            StageResult(STAGE_TEMPORAL_STABILITY, STATUS_INCOMPLETE, reason=NOT_EVALUATED),
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, "无执行实现"),
        )
    )


def rejected_events(*, experiment_id: str, cohort_id: str, stage_id: str) -> tuple[RunEvent, ...]:
    return (
        build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=STATE_CREATED,
            to_state=STATE_VALIDATING,
            event_type=EVENT_RUN_STATE_CHANGED,
            sequence=0,
        ),
        build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=STATE_VALIDATING,
            to_state=STATE_REJECTED,
            event_type=EVENT_RUN_STATE_CHANGED,
            stage=stage_id,
            reason_code=ERROR_CODE,
            sequence=1,
        ),
        build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=STATE_VALIDATING,
            to_state=STATE_REJECTED,
            event_type=EVENT_GATE_REJECTED,
            stage=stage_id,
            reason_code=ERROR_CODE,
            sequence=2,
        ),
    )


def register_rejection(
    *,
    tier_context: TierContext,
    reports: Path,
    cohort_id: str,
    candidate_id: str,
    experiment_id: str,
    snapshot_id: str,
    object_id: str,
    expression: str,
    observed_at: str,
    violation_message: str,
    code_build_digest: str = "",
    stage_id: str = STAGE_SIGNAL_QUALITY,
) -> CanonicalResult:
    """发布并登记一个 REJECTED 终态成员；返回已发布目录。"""
    stages = rejected_stage_results(
        stage_id=stage_id, expression=expression, observed_at=observed_at
    )
    events = rejected_events(experiment_id=experiment_id, cohort_id=cohort_id, stage_id=stage_id)
    curves = build_equity_curves(
        NEUTRAL_CURVE,
        times=(datetime.fromisoformat(observed_at.replace("Z", "+00:00")),),
    )
    request = publisher.PublishRequest(
        experiment_id=experiment_id,
        manifest={
            "schema_version": 1,
            "execution_tier": TIER_CANONICAL,
            "experiment_id": experiment_id,
            "state": STATE_REJECTED,
            "events_digest": events_digest(events),
            "research_snapshot_id": snapshot_id,
            "object_id": object_id,
            "cohort_id": cohort_id,
            "candidate_id": candidate_id,
            "sample_tier": "underpowered",
            "cost_verdict": "cost_undetermined",
            "approximation": dict(REAL_SOURCE_ANNOTATION),
            "stage_results": stages.to_payload(),
        },
        report={
            "schema_version": 1,
            "experiment_id": experiment_id,
            "evaluation": NOT_RUN_MARKER,
            "violation": violation_message,
            "approximation": dict(REAL_SOURCE_ANNOTATION),
            "curves_summary": curves.scalar_summary(),
            "stage_results": stages.to_payload(),
        },
        curves=curves,
        events=events,
        registration={
            "schema_version": 1,
            "experiment_id": experiment_id,
            "cohort_id": cohort_id,
            "candidate_id": candidate_id,
            "registered_at": observed_at,
            "rejected": True,
        },
        object_id=object_id,
        snapshot_id=snapshot_id,
    )
    published = publisher.publish(tier_context, request)
    population.register_member(
        reports,
        cohort_id,
        population.MemberRegistration(
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            run_state=STATE_REGISTERED,
            promotion_verdict="rejected",
            sample_tier="underpowered",
            evidence_ref=f"{published.relative_to(reports).as_posix()}/curves.parquet",
        ),
        build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=STATE_REJECTED,
            to_state=STATE_REGISTERED,
            event_type=EVENT_REGISTERED,
            reason_code=ERROR_CODE,
            evidence_refs=(candidate_id,),
            sequence=0,
        ),
    )
    return published
