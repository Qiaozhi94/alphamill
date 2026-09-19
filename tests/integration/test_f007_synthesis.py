"""T014 / `FR-006`·`AC-007`·`AC-012`·`SC-004`：综合报告只读 canonical、五阶段/三维聚合与三栏输出。

覆盖：只有 preview 产物时空 canonical 结果（不混入 preview 指标）、五阶段漏斗与失败三维聚合、
枚举外取值失败关闭、拒绝者仍入分母、事实/推断/建议分栏、同台账确定性重建同一 `synthesis_id`、
发布幂等与冲突拒绝、F003 生成侧漏斗第一级只消费 completed 运行。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import EVENT_REGISTERED, build_event
from alphamill.evaluation.run_state import STATE_EVIDENCE_READY, STATE_REGISTERED
from alphamill.experiment_store import population
from alphamill.experiment_store.synthesis import (
    STATUS_EMPTY,
    STATUS_FINALIZED,
    STATUS_OPEN,
    SynthesisError,
    assert_no_preview_contamination,
    build_synthesis,
    compute_synthesis_id,
    load_synthesis,
    publish_synthesis,
    synthesis_dir,
)
from alphamill.factor_factory.bench.stage_model import (
    STAGE_COST_CAPACITY,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_SIGNAL_QUALITY,
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_PASS,
    FailureRecord,
    StageResult,
    StageResults,
    not_applicable,
)

CANDIDATE_A = "factor_sha256:" + "a" * 64
CANDIDATE_B = "factor_sha256:" + "b" * 64
EXPERIMENT_A = "sha256:" + "1" * 64
EXPERIMENT_B = "sha256:" + "2" * 64
COHORT = "cohort_sha256:" + "c" * 64
NOW = "2026-09-01T00:00:00Z"
OBJECT = "factor_sha256:" + "o" * 64
SNAPSHOT = "sha256:" + "s" * 64


@pytest.fixture()
def reports(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(tmp_path / "reports"))
    return tmp_path / "reports"


def _definition(*candidates: str) -> dict:
    return {
        "schema_version": 1,
        "hypothesis_family": "momentum-v1",
        "selection_stage": "cross_sectional",
        "method_config_ref": "method-v1",
        "cost_model_ref": "cm-v1",
        "inclusion_rules": "全部承诺成员计入分母",
        "commitments": [
            {"candidate_id": c, "generator": "manual", "registered_at": NOW} for c in candidates
        ],
        "window": {
            "selection": ["2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"],
            "label_horizons": [1, 4, 24],
        },
        "universe_digest": "sha256:" + "f" * 64,
        "calendar_digest": "sha256:" + "0" * 64,
        "frozen_at": NOW,
        "frozen_by": "Georg",
    }


def _stages(*, cost_fail: bool = False) -> StageResults:
    failures = ()
    if cost_fail:
        failures = (
            FailureRecord(
                stage=STAGE_COST_CAPACITY,
                owner="cost",
                mechanism="cost_negative",
                error_code="E_REQUIRED_METRIC_FAILED",
                first_seen=NOW,
                evidence_refs=("reports/bench/x/curves.parquet",),
            ),
        )
    return StageResults(
        results=(
            StageResult(STAGE_SIGNAL_QUALITY, STATUS_PASS),
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合"),
            StageResult(
                STAGE_COST_CAPACITY, STATUS_FAIL if cost_fail else STATUS_PASS, failures=failures
            ),
            StageResult(STAGE_TEMPORAL_STABILITY, STATUS_PASS),
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, "无执行实现"),
        )
    )


def _publish_member(
    reports: Path, candidate: str, experiment: str, stages: StageResults, verdict: str
) -> None:
    directory = reports / "bench" / OBJECT / SNAPSHOT / experiment
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "execution_tier": TIER_CANONICAL,
                "experiment_id": experiment,
                "state": STATE_EVIDENCE_READY,
                "events_digest": "sha256:" + "d" * 64,
                "research_snapshot_id": SNAPSHOT,
                "object_id": OBJECT,
            }
        ),
        encoding="utf-8",
    )
    (directory / "report.json").write_text(
        json.dumps({"schema_version": 1, "stage_results": stages.to_payload()}), encoding="utf-8"
    )
    (directory / "curves.parquet").write_bytes(b"")
    (directory / "registration.json").write_text(
        json.dumps({"schema_version": 1}), encoding="utf-8"
    )


def _register(reports: Path, cohort_id: str, candidate: str, experiment: str, verdict: str) -> None:
    event = build_event(
        experiment_id=experiment,
        execution_tier=TIER_CANONICAL,
        cohort_id=cohort_id,
        from_state=STATE_EVIDENCE_READY,
        to_state=STATE_REGISTERED,
        event_type=EVENT_REGISTERED,
        sequence=0,
    )
    population.register_member(
        reports,
        cohort_id,
        population.MemberRegistration(
            candidate_id=candidate,
            experiment_id=experiment,
            run_state=STATE_REGISTERED,
            promotion_verdict=verdict,
            sample_tier="trustworthy",
            evidence_ref=f"{reports.as_posix()}/bench/{OBJECT}/{SNAPSHOT}/{experiment}/curves.parquet",
        ),
        event,
    )


# ---------- 只消费 canonical ----------


def test_only_preview_artifacts_yields_empty_canonical_result(reports):
    (reports / "preview" / EXPERIMENT_A / "attempt-1").mkdir(parents=True)
    report = build_synthesis(cohort_id=COHORT)
    assert report.status == STATUS_EMPTY
    assert report.funnel["cohort"]["trial_count"] == 0
    assert report.funnel["cohort"]["member_count"] == 0
    assert report.failures == ()
    assert report.stage_funnel[STAGE_SIGNAL_QUALITY][STATUS_PASS] == 0
    assert_no_preview_contamination(report)


def test_finalized_cohort_produces_funnel_and_failure_buckets(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _publish_member(reports, CANDIDATE_B, EXPERIMENT_B, _stages(cost_fail=True), "dead")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    _register(reports, cohort_id, CANDIDATE_B, EXPERIMENT_B, "dead")
    assert build_synthesis(cohort_id=cohort_id).status == STATUS_OPEN

    population.finalize_cohort(reports, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=NOW)
    report = build_synthesis(cohort_id=cohort_id)
    assert report.status == STATUS_FINALIZED
    assert report.funnel["cohort"] == {
        "trial_count": 2,
        "member_count": 2,
        "rejected_count": 0,
        "promotion_verdicts": {CANDIDATE_A: "promising", CANDIDATE_B: "dead"},
        "effective_trials": None,
    }
    assert report.stage_funnel[STAGE_COST_CAPACITY] == {
        "PASS": 1,
        "FAIL": 1,
        "UNDERPOWERED": 0,
        "INCOMPLETE": 0,
        "NOT_APPLICABLE": 0,
    }
    assert len(report.failures) == 1
    bucket = report.failures[0]
    assert (bucket.stage, bucket.owner, bucket.mechanism, bucket.count) == (
        STAGE_COST_CAPACITY,
        "cost",
        "cost_negative",
        1,
    )
    assert bucket.error_codes == ("E_REQUIRED_METRIC_FAILED",)
    assert "cost_negative" in [item["constraint"] for item in report.inferences]


def test_three_columns_are_separated_and_traceable(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_B))
    _publish_member(reports, CANDIDATE_B, EXPERIMENT_B, _stages(cost_fail=True), "dead")
    _register(reports, cohort_id, CANDIDATE_B, EXPERIMENT_B, "dead")
    report = build_synthesis(cohort_id=cohort_id)
    kinds = {item["kind"] for item in report.facts}
    assert {"cohort_status", "cohort_trials", "stage"} <= kinds
    assert all("basis" in item for item in report.inferences)
    assert all(
        item["owner"] in {"cost", "data", "method", "statistics", "infra"}
        for item in report.recommendations
    )
    assert any(item["action"] for item in report.recommendations)


def test_rejected_members_stay_in_the_denominator(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _publish_member(reports, CANDIDATE_B, EXPERIMENT_B, _stages(), "rejected")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    _register(reports, cohort_id, CANDIDATE_B, EXPERIMENT_B, "rejected")
    report = build_synthesis(cohort_id=cohort_id)
    assert report.funnel["cohort"]["trial_count"] == 2
    assert report.funnel["cohort"]["rejected_count"] == 1
    assert report.funnel["cohort"]["member_count"] == 2


def test_generation_first_level_only_consumes_completed_runs(reports):
    events = [
        {
            "type": "generation.run_completed",
            "status": "completed",
            "run_id": "r1",
            "counts": {"registered": 50},
        },
        {
            "type": "generation.run_completed",
            "status": "partial",
            "run_id": "r2",
            "counts": {"registered": 5},
        },
        {
            "type": "generation.candidate_rejected",
            "run_id": "r1",
            "expression": "x",
            "reason_code": "lookahead",
        },
    ]
    report = build_synthesis(cohort_id=COHORT, generation_events=events)
    assert report.funnel["generation"] == {
        "completed_runs": 1,
        "registered_candidates": 50,
        "rejected_by_reason": {"lookahead": 1},
        "rejected_total": 1,
        "denominator": 51,
    }


def test_unknown_enumeration_in_member_report_fails_closed(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    report_path = reports / "bench" / OBJECT / SNAPSHOT / EXPERIMENT_A / "report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    payload["stage_results"][0]["status"] = "OK"
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SynthesisError, match="未登记阶段状态"):
        build_synthesis(cohort_id=cohort_id)
    payload["stage_results"][0]["status"] = STATUS_PASS
    payload["stage_results"][0]["stage"] = "unknown_stage"
    report_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SynthesisError, match="未登记阶段"):
        build_synthesis(cohort_id=cohort_id)


def test_failure_bucket_rejects_unknown_mechanism():
    from alphamill.experiment_store.synthesis import FailureBucket

    with pytest.raises(SynthesisError, match="mechanism 未登记"):
        FailureBucket(stage=STAGE_COST_CAPACITY, owner="cost", mechanism="vibes", count=1)


# ---------- 确定性与发布 ----------


def test_rebuild_is_deterministic_and_generated_at_is_not_identity(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    first = build_synthesis(cohort_id=cohort_id, generated_at="2026-09-01T00:00:00Z")
    second = build_synthesis(cohort_id=cohort_id, generated_at="2027-01-01T00:00:00Z")
    assert first.synthesis_id == second.synthesis_id
    assert first.generated_at != second.generated_at
    assert compute_synthesis_id(first.semantic_payload()) == first.synthesis_id


def test_publish_is_idempotent_and_load_roundtrips(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    report = build_synthesis(cohort_id=cohort_id)
    path = publish_synthesis(report, root=reports)
    assert publish_synthesis(report, root=reports) == path
    assert path == synthesis_dir(reports, cohort_id, report.synthesis_id) / "synthesis_report.json"
    loaded = load_synthesis(reports, cohort_id, report.synthesis_id)
    assert loaded.synthesis_id == report.synthesis_id
    assert loaded.funnel == report.funnel
    assert loaded.facts == report.facts


def test_conflicting_synthesis_publish_is_rejected(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    report = build_synthesis(cohort_id=cohort_id)
    path = publish_synthesis(report, root=reports)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["facts"] = [{"kind": "cohort_status", "value": "TAMPERED"}]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SynthesisError, match="语义不一致"):
        publish_synthesis(report, root=reports)


# ---------- T031 [TEST] 层 2 旅程验收：US-003 跨实验综合诊断 ----------


def test_us003_synthesis_rebuilds_deterministically_from_finalized_ledger(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    _publish_member(reports, CANDIDATE_A, EXPERIMENT_A, _stages(), "promising")
    _publish_member(reports, CANDIDATE_B, EXPERIMENT_B, _stages(cost_fail=True), "dead")
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    _register(reports, cohort_id, CANDIDATE_B, EXPERIMENT_B, "dead")
    population.finalize_cohort(reports, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=NOW)
    first = build_synthesis(cohort_id=cohort_id, generated_at="2026-09-01T00:00:00Z")
    second = build_synthesis(cohort_id=cohort_id, generated_at="2027-01-01T00:00:00Z")
    assert first.synthesis_id == second.synthesis_id
    assert first.status == STATUS_FINALIZED
    assert first.funnel["cohort"]["trial_count"] == 2
    assert len(first.facts) >= 5
    assert first.inferences and first.recommendations
    bucket = first.failures[0]
    assert (bucket.stage, bucket.owner, bucket.mechanism) == (
        STAGE_COST_CAPACITY,
        "cost",
        "cost_negative",
    )


def test_us003_preview_only_yields_empty_canonical_result(reports):
    (reports / "preview" / EXPERIMENT_A / "attempt-1").mkdir(parents=True)
    report = build_synthesis(cohort_id=COHORT, generated_at=NOW)
    assert report.status == STATUS_EMPTY
    assert report.funnel["cohort"]["member_count"] == 0
    assert report.failures == ()


def test_us003_report_and_curves_scalars_recompute_within_tolerance(tmp_path):
    from datetime import UTC, datetime, timedelta

    from alphamill.factor_factory.bench.artifact_schema import read_artifact_dir
    from alphamill.factor_factory.bench.curves import build_equity_curves, write_curves

    start = datetime(2026, 9, 1, tzinfo=UTC)
    periods = tuple(0.01 if index % 2 else -0.004 for index in range(12))
    curves = build_equity_curves(
        periods, times=tuple(start + timedelta(hours=index) for index in range(12))
    )
    directory = tmp_path / "bundle"
    directory.mkdir()
    write_curves(directory / "curves.parquet", curves)
    (directory / "report.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "experiment_id": EXPERIMENT_A,
                "approximation": {
                    "is_approximate": False,
                    "reduced_dimensions": [],
                    "signal_source": "real",
                },
                "curves_summary": curves.scalar_summary(),
                "stage_results": _stages().to_payload(),
            }
        ),
        encoding="utf-8",
    )
    bundle = read_artifact_dir(directory, canonical=True)
    assert bundle.report["curves_summary"] == bundle.curves.scalar_summary()
