"""canonical 运行与 abandon（`FR-001`/`IR-001`/`IR-002`/`TR-003`；任务 T013）。

canonical 与 preview 的差别是**门禁强度**，不是流程分支：

- 必须显式给出冻结 cohort、已发布 ResearchSnapshot、规则版本与 `--code-build-digest` 期望值；
  digest 由 runner 自行计算（不接受调用方自报），工作树脏或无法判定即拒绝（`IR-001`）；
- 入口先跑方法论门 L1 静态纯度 fail-closed（`FR-002`/`FR-007`）；canonical 恒为非近似
  （`NFR-004`），`source=placeholder` 一律拒绝（`DR-007`）；
- 产物发布到 `reports/bench/`，必须带 `registration.json`，随后写 `evaluation.registered`；
- 同语义重跑**幂等返回既有实验**（同一 `experiment_id`，不重复计数）。

v0.2 的因子输入经由 `--signals` + `--expression` 夹具接缝；F003 注册表接线后由 `--factor` 解析
替换该接缝，门禁与产物契约不变。abandon / finalize-cohort 见 `canonical_ops`。
"""

from __future__ import annotations

import json
import os
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation import claim, publisher
from alphamill.evaluation.canonical_result import CanonicalResult
from alphamill.evaluation.capabilities import TierContext, context_for
from alphamill.evaluation.code_build import (
    assert_expected_code_build_digest,
    assert_worktree_clean_for_canonical,
)
from alphamill.evaluation.code_build import code_build_digest as compute_code_build_digest
from alphamill.evaluation.contract_common import TIER_CANONICAL, UpstreamContractError
from alphamill.evaluation.events import (
    EVENT_REGISTERED,
    EVENT_RUN_STATE_CHANGED,
    EVENTS_FILENAME,
    RunEvent,
    build_event,
    events_digest,
    read_events,
)
from alphamill.evaluation.pipeline import evaluate_fixture
from alphamill.evaluation.rejection import (
    REAL_SOURCE_ANNOTATION,
    register_rejection,
    rejected_stage_results,
)
from alphamill.evaluation.run_config import RunConfig, load_run_config, load_unified_frame
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
from alphamill.experiment_store.experiment_context import (
    CONTEXT_SCHEMA_VERSION,
    ExperimentContext,
)
from alphamill.experiment_store.promotion import PromotionInputs, derive_promotion_verdict
from alphamill.factor_factory.bench.curves import build_equity_curves
from alphamill.factor_factory.bench.stage_model import STAGE_SIGNAL_QUALITY
from alphamill.validation.methodology_gate import GuardContext, evaluate_methodology
from alphamill.validation.no_lookahead import (
    STATUS_NOT_YET_AVAILABLE,
    STATUS_PASS,
    build_no_lookahead,
)

CANONICAL_STATE_MANIFEST = "manifest.json"
CLAIMS_SUBDIR = "_claims"


class CanonicalError(UpstreamContractError):
    """canonical 前置条件不满足或输入不可解析；`E_INPUT_INVALID`。"""

    code = "E_INPUT_INVALID"


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


def run_canonical(
    *,
    config_path: Path,
    factor_ref: str,
    candidate_id: str,
    cohort_id: str,
    seed: int,
    signals_path: Path,
    snapshot_id: str,
    expression: str,
    object_id: str | None = None,
    expected_code_build_digest: str | None = None,
    observed_at: str | None = None,
    require_clean_worktree: bool = True,
) -> CanonicalResult:
    config = load_run_config(config_path)
    if require_clean_worktree:
        assert_worktree_clean_for_canonical()
    code_digest = compute_code_build_digest()
    assert_expected_code_build_digest(expected_code_build_digest, code_digest)

    reports = rs.reports_root()
    definition = population.load_cohort(reports, cohort_id)
    if candidate_id not in population.commitment_ids(definition):
        raise CanonicalError(f"候选 {candidate_id} 不在 cohort {cohort_id} 的承诺内")
    snapshot = rs.load_snapshot(reports, snapshot_id)
    context = ExperimentContext(
        schema_version=CONTEXT_SCHEMA_VERSION,
        execution_tier=TIER_CANONICAL,
        upstream={"kind": "factor", "id": factor_ref},
        cohort_id=cohort_id,
        method_config=config.method_config,
        window=config.window,
        cost_model=config.cost_model,
        research_snapshot_id=snapshot.snapshot_id,
        code_build_digest=code_digest,
        seed=seed,
    )
    experiment_id = context.experiment_id
    tier_context = context_for(TIER_CANONICAL, reports)
    target = tier_context.bench_dir(object_id or factor_ref, snapshot.snapshot_id, experiment_id)
    if publisher.is_published(target, canonical=True):
        manifest = json.loads((target / CANONICAL_STATE_MANIFEST).read_text(encoding="utf-8"))
        _ensure_member_registered(
            reports=reports,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            target=target,
            config=config,
        )
        return CanonicalResult(
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            snapshot_id=snapshot.snapshot_id,
            code_build_digest=code_digest,
            state=str(manifest.get("state", STATE_EVIDENCE_READY)),
            cost_verdict=str(manifest.get("cost_verdict", "cost_undetermined")),
            sample_tier=str(manifest.get("sample_tier", "underpowered")),
            stage_results=_stage_results_from_manifest(manifest),
            approximation=manifest.get("approximation", {}),
            promotion_verdict=None,
            artifact_dir=str(target),
            reused=True,
        )

    claim_token = f"canonical-{os.getpid()}-{uuid.uuid4().hex}"
    claim.acquire(reports / CLAIMS_SUBDIR, experiment_id, owner_token=claim_token)
    try:
        return _execute_canonical(
            reports=reports,
            tier_context=tier_context,
            config=config,
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            factor_ref=factor_ref,
            object_id=object_id,
            signals_path=signals_path,
            snapshot=snapshot,
            expression=expression,
            code_digest=code_digest,
            observed_at=observed_at,
        )
    finally:
        claim.release(reports / CLAIMS_SUBDIR, experiment_id, owner_token=claim_token)


def _execute_canonical(
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

    times, signals, labels = load_unified_frame(signals_path)
    evaluation = evaluate_fixture(
        config=config,
        times=times,
        signals=signals,
        labels=labels,
        execution_tier=TIER_CANONICAL,
        observed_at=moment,
    )
    terminal_state = (
        STATE_EVIDENCE_READY if evaluation.stage_results.evidence_complete else STATE_INCOMPLETE
    )
    registered_events = _registered_events(experiment_id, cohort_id, candidate_id)
    events = _run_events(experiment_id, cohort_id, terminal_state) + registered_events
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
        registered_events[0],
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


def _stage_results_from_manifest(manifest: Mapping[str, Any]) -> Any:
    from alphamill.factor_factory.bench.stage_model import StageResults

    return StageResults.from_payload(manifest.get("stage_results", []))


def _registered_events(
    experiment_id: str, cohort_id: str, candidate_id: str
) -> tuple[RunEvent, ...]:
    return (
        build_event(
            experiment_id=experiment_id,
            execution_tier=TIER_CANONICAL,
            cohort_id=cohort_id,
            from_state=STATE_EVIDENCE_READY,
            to_state=STATE_REGISTERED,
            event_type=EVENT_REGISTERED,
            evidence_refs=(candidate_id,),
            sequence=0,
        ),
    )


def _no_lookahead_from_manifest(manifest: Mapping[str, Any]):
    """从已发布 manifest 重建三层无前视状态（复用分支重导 `promotion_verdict` 用）。"""

    payload = manifest.get("no_lookahead") or {}
    layers = {entry["layer"]: entry for entry in payload.get("layers", [])}

    def layer(name: str) -> Mapping[str, Any]:
        return layers.get(name, {})

    return build_no_lookahead(
        l1_status=str(layer("L1").get("status", STATUS_NOT_YET_AVAILABLE)),
        l1_evidence_refs=tuple(layer("L1").get("evidence_refs", ())),
        l2_status=str(layer("L2").get("status", STATUS_NOT_YET_AVAILABLE)),
        l2_evidence_refs=tuple(layer("L2").get("evidence_refs", ())),
        l3_status=str(layer("L3").get("status", STATUS_NOT_YET_AVAILABLE)),
        l3_evidence_refs=tuple(layer("L3").get("evidence_refs", ())),
    )


def _published_registered_event(
    target: Path, *, experiment_id: str, cohort_id: str, candidate_id: str, state: str
) -> RunEvent:
    """取已发布批次里**实际**的 `evaluation.registered` 事件，保证复用补登记幂等键一致。"""
    for event in read_events(target / EVENTS_FILENAME):
        if event.type == EVENT_REGISTERED:
            return event
    from_state = STATE_REJECTED if state == STATE_REJECTED else STATE_EVIDENCE_READY
    return build_event(
        experiment_id=experiment_id,
        execution_tier=TIER_CANONICAL,
        cohort_id=cohort_id,
        from_state=from_state,
        to_state=STATE_REGISTERED,
        event_type=EVENT_REGISTERED,
        evidence_refs=(candidate_id,),
        sequence=0,
    )


def _ensure_member_registered(
    *,
    reports: Path,
    cohort_id: str,
    candidate_id: str,
    experiment_id: str,
    target: Path,
    config: Any,
) -> None:
    """复用已发布批次前**幂等补登记**（`R1-003`）：崩溃窗口只丢失登记时 cohort 不会永挂 OPEN。"""
    if any(
        entry.candidate_id == candidate_id
        for entry in population.registrations(reports, cohort_id)
    ):
        return
    manifest = json.loads((target / CANONICAL_STATE_MANIFEST).read_text(encoding="utf-8"))
    state = str(manifest.get("state", STATE_EVIDENCE_READY))
    sample_tier = str(manifest.get("sample_tier", "underpowered"))
    cost_verdict = str(manifest.get("cost_verdict", "cost_undetermined"))
    if state == STATE_REJECTED:
        promotion = "rejected"
    else:
        promotion = derive_promotion_verdict(
            PromotionInputs(
                run_state=state,
                stage_results=_stage_results_from_manifest(manifest),
                sample_tier=sample_tier,
                cost_verdict=cost_verdict,
                no_lookahead=_no_lookahead_from_manifest(manifest),
            )
        )
    population.register_member(
        reports,
        cohort_id,
        population.MemberRegistration(
            candidate_id=candidate_id,
            experiment_id=experiment_id,
            run_state=STATE_REGISTERED,
            promotion_verdict=promotion,
            sample_tier=sample_tier,
            cost_model_version=str(config.cost_model.get("id", "")),
            evidence_ref=f"{target.relative_to(reports).as_posix()}/curves.parquet",
        ),
        _published_registered_event(
            target,
            experiment_id=experiment_id,
            cohort_id=cohort_id,
            candidate_id=candidate_id,
            state=state,
        ),
    )
