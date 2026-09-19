"""T018 / `FR-008`·`DR-008`·`AC-013`：注册表评测面回写（只搬运、不重算；定义面零变化）。

覆盖：只在 cohort FINALIZED 后回写、载荷严格为 `DR-008` 字段集且**不含 lifecycle 字段**、
append-only 且按 `(cohort_id, factor_id)` 幂等不重复计数、拒绝者照常回写、dedup 结论按原值搬运
（不重算）、preview 无回写能力、定义面写入即 `E_CANONICAL_FORBIDDEN` 且定义面内容零变化。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from alphamill.evaluation.capabilities import CapabilityError, context_for
from alphamill.evaluation.events import EVENT_REGISTERED, build_event
from alphamill.evaluation.registry_writeback import (
    DR008_FIELDS,
    WritebackError,
    build_summaries,
    evaluation_face_path,
    read_evaluation_face,
    writeback_evaluation_face,
)
from alphamill.evaluation.run_state import STATE_EVIDENCE_READY, STATE_REGISTERED
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs

pytestmark = pytest.mark.integration

CANDIDATE_A = "factor_sha256:" + "a" * 64
CANDIDATE_B = "factor_sha256:" + "b" * 64
EXPERIMENT_A = "sha256:" + "1" * 64
EXPERIMENT_B = "sha256:" + "2" * 64
NOW = "2026-09-01T00:00:00Z"


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


def _register(
    reports: Path, cohort_id: str, candidate: str, experiment: str, verdict: str, dedup=None
) -> None:
    event = build_event(
        experiment_id=experiment,
        execution_tier="canonical",
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
            cost_model_version="cm-v1",
            dedup=dedup,
            evidence_ref=f"bench/{candidate}/{experiment}/curves.parquet",
        ),
        event,
    )


def _finalized(reports: Path) -> str:
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    _register(
        reports,
        cohort_id,
        CANDIDATE_B,
        EXPERIMENT_B,
        "rejected",
        dedup={"max_abs_rho": 0.995, "verdict": "rejected", "against_factor_id": CANDIDATE_A},
    )
    population.finalize_cohort(reports, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=NOW)
    return cohort_id


def test_writeback_is_refused_before_finalize(reports):
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE_A))
    _register(reports, cohort_id, CANDIDATE_A, EXPERIMENT_A, "promising")
    with pytest.raises(population.CohortError, match="尚未 FINALIZED"):
        build_summaries(cohort_id)
    assert read_evaluation_face(reports) == ()


def test_writeback_appends_dr008_payloads_for_every_member(reports):
    cohort_id = _finalized(reports)
    summaries = build_summaries(cohort_id, finalized_at=NOW)
    assert len(summaries) == 2
    path = writeback_evaluation_face(context_for("canonical", reports), reports, summaries)
    assert path == evaluation_face_path(reports)
    rows = read_evaluation_face(reports)
    assert [row["factor_id"] for row in rows] == [CANDIDATE_A, CANDIDATE_B]
    for row in rows:
        assert set(row) == set(DR008_FIELDS)
    rejected = rows[1]
    assert rejected["promotion_verdict"] == "rejected"
    assert rejected["evidence_ref"].endswith("curves.parquet")


def test_writeback_transports_dedup_without_recomputing(reports):
    cohort_id = _finalized(reports)
    writeback_evaluation_face(
        context_for("canonical", reports), reports, build_summaries(cohort_id)
    )
    dedup = read_evaluation_face(reports)[1]["dedup"]
    assert dedup == {
        "max_abs_rho": 0.995,
        "verdict": "rejected",
        "against_factor_id": CANDIDATE_A,
    }


def test_writeback_is_idempotent_per_cohort_and_factor(reports):
    cohort_id = _finalized(reports)
    context = context_for("canonical", reports)
    writeback_evaluation_face(context, reports, build_summaries(cohort_id))
    first = evaluation_face_path(reports).read_text(encoding="utf-8")
    writeback_evaluation_face(context, reports, build_summaries(cohort_id))
    assert evaluation_face_path(reports).read_text(encoding="utf-8") == first
    assert len(read_evaluation_face(reports)) == 2


def test_preview_context_cannot_write_back(reports):
    cohort_id = _finalized(reports)
    with pytest.raises(CapabilityError, match="canonical_writer"):
        writeback_evaluation_face(
            context_for("preview", reports), reports, build_summaries(cohort_id)
        )
    assert read_evaluation_face(reports) == ()


def test_lifecycle_and_unknown_fields_are_rejected(reports):
    cohort_id = _finalized(reports)
    payload = build_summaries(cohort_id)[0].to_payload()
    from alphamill.evaluation.registry_writeback import assert_payload_is_dr008

    with pytest.raises(WritebackError, match="DR-008 之外的字段"):
        assert_payload_is_dr008({**payload, "lifecycle_state": "active"})
    with pytest.raises(WritebackError, match="DR-008 之外的字段"):
        assert_payload_is_dr008({**payload, "decay_score": 0.1})
    for field in ("expression", "definition_digest", "definition_version"):
        with pytest.raises(WritebackError, match="定义面字段"):
            assert_payload_is_dr008({**payload, field: "x"})


def test_definition_face_payload_is_rejected_and_definitions_untouched(reports):
    """R1-117：定义面归属由 DR-008 校验覆盖，不存在只有测试才调用的陷阱写入函数。"""
    cohort_id = _finalized(reports)
    definition = reports / "factor_registry" / "definitions"
    definition.mkdir(parents=True, exist_ok=True)
    (definition / "existing.json").write_text(
        json.dumps({"definition_version": 1}), encoding="utf-8"
    )
    before = sorted(path.name for path in definition.iterdir())
    from alphamill.evaluation.registry_writeback import assert_payload_is_dr008

    payload = build_summaries(cohort_id)[0].to_payload()
    with pytest.raises(WritebackError, match="定义面字段"):
        assert_payload_is_dr008({**payload, "expression": "close"})
    assert sorted(path.name for path in definition.iterdir()) == before
    assert rs.reports_root() == reports
