"""T012 / `DR-003`·`DR-004`·`TR-003`·`AC-003`·`AC-013`：canonical 登记、查重、裁决与留出台账。

覆盖：cohort 内容寻址冻结与幂等、成员终态登记（只认 `evaluation.registered` + `REGISTERED`）、
收齐校验（未收齐 `E_COHORT_FROZEN` 且不留部分 verdict）、official population 确定性投影与计数
自洽、`promotion_verdict` 冻结优先级表逐级取值、`|ρ|` 查重（0.99/0.90 阈值、cohort 内承诺顺序
保留在先者、注册表既有记录）、留出预算台账的 capability 边界与 v0.2 零行不变量。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from alphamill.evaluation import canonical_ops
from alphamill.evaluation.capabilities import CapabilityError, context_for
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    EVENT_REGISTERED,
    build_event,
    read_events,
)
from alphamill.evaluation.run_state import STATE_EVIDENCE_READY, STATE_REGISTERED
from alphamill.experiment_store import population as pop
from alphamill.experiment_store.dedup import (
    DedupCandidate,
    DedupError,
    DedupRecord,
    decide_dedup,
    decide_verdict,
    max_abs_rho,
    pearson,
    resolve_cohort_dedup,
)
from alphamill.experiment_store.holdout_budget import (
    HoldoutBudgetEntry,
    HoldoutBudgetError,
    append_entry,
    iso_week_of,
    ledger_path,
    read_ledger,
    rejection_event,
    rejections_path,
)
from alphamill.experiment_store.promotion import (
    DEDUP_REJECTED,
    PromotionError,
    PromotionInputs,
    derive_promotion_verdict,
)
from alphamill.factor_factory.bench.curves import build_equity_curves, write_curves
from alphamill.factor_factory.bench.stage_model import (
    COST_NEGATIVE,
    COST_POSITIVE,
    PROMOTION_VERDICTS,
    STAGE_COST_CAPACITY,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_SIGNAL_QUALITY,
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_INCOMPLETE,
    STATUS_PASS,
    STATUS_UNDERPOWERED,
    FailureRecord,
    StageResult,
    StageResults,
    not_applicable,
)
from alphamill.validation.no_lookahead import (
    LAYER_L1,
    LAYER_L2,
    LAYER_L3,
    NoLookahead,
    NoLookaheadLayer,
    build_no_lookahead,
)
from alphamill.validation.no_lookahead import (
    STATUS_PASS as LAYER_PASS,
)

CANDIDATE_A = "factor_sha256:" + "a" * 64
CANDIDATE_B = "factor_sha256:" + "b" * 64
EXPERIMENT_A = "sha256:" + "1" * 64
EXPERIMENT_B = "sha256:" + "2" * 64
COHORT = "cohort_sha256:" + "c" * 64
FROZEN_AT = "2026-09-01T00:00:00Z"


# ---------- promotion_verdict 优先级表 ----------


def _stages(
    *,
    signal: str = STATUS_PASS,
    cost: str = STATUS_PASS,
    stability: str = STATUS_PASS,
    signal_failures: tuple = (),
    cost_failures: tuple = (),
    stability_failures: tuple = (),
) -> StageResults:
    return StageResults(
        results=(
            StageResult(
                stage_id=STAGE_SIGNAL_QUALITY, status=signal, failures=tuple(signal_failures)
            ),
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合"),
            StageResult(stage_id=STAGE_COST_CAPACITY, status=cost, failures=tuple(cost_failures)),
            StageResult(
                stage_id=STAGE_TEMPORAL_STABILITY,
                status=stability,
                failures=tuple(stability_failures),
            ),
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, "无执行实现"),
        )
    )


def _all_lookahead_layers() -> NoLookahead:
    return NoLookahead(
        layers=(
            NoLookaheadLayer(LAYER_L1, LAYER_PASS, ("sha256:" + "e" * 64,)),
            NoLookaheadLayer(LAYER_L2, LAYER_PASS, ("reports/replay.json",)),
            NoLookaheadLayer(LAYER_L3, LAYER_PASS, ("reports/cache_align.json",)),
        )
    )


def _verdict(**overrides) -> str:
    base = {
        "run_state": STATE_EVIDENCE_READY,
        "stage_results": _stages(),
        "sample_tier": "trustworthy",
        "cost_verdict": COST_POSITIVE,
        "no_lookahead": build_no_lookahead(
            l1_status=LAYER_PASS, l1_evidence_refs=("sha256:" + "d" * 64,)
        ),
    }
    base.update(overrides)
    return derive_promotion_verdict(PromotionInputs(**base))


def test_rejected_wins_over_everything():
    assert _verdict(run_state="REJECTED") == "rejected"
    assert _verdict(dedup_verdict=DEDUP_REJECTED) == "rejected"


def test_evidence_failure_maps_to_incomplete():
    assert _verdict(stage_results=_stages(stability=STATUS_INCOMPLETE)) == "incomplete"
    failure = FailureRecord(
        stage=STAGE_SIGNAL_QUALITY,
        owner="signal",
        mechanism="estimator_failure",
        error_code="E_REQUIRED_METRIC_FAILED",
        first_seen=FROZEN_AT,
    )
    verdict = _verdict(stage_results=_stages(signal=STATUS_FAIL, signal_failures=(failure,)))
    assert verdict == "incomplete"


def test_underpowered_precedes_dead():
    assert _verdict(sample_tier="underpowered") == "underpowered"
    assert _verdict(stage_results=_stages(stability=STATUS_UNDERPOWERED)) == "underpowered"


def test_cost_negative_maps_to_dead_not_incomplete():
    failure = FailureRecord(
        stage=STAGE_COST_CAPACITY,
        owner="cost",
        mechanism="cost_negative",
        error_code="E_REQUIRED_METRIC_FAILED",
        first_seen=FROZEN_AT,
    )
    verdict = _verdict(
        stage_results=_stages(cost=STATUS_FAIL, cost_failures=(failure,)),
        cost_verdict=COST_NEGATIVE,
    )
    assert verdict == "dead"
    assert verdict != "incomplete"


def test_missing_lookahead_layer_blocks_promotion():
    assert _verdict() == "blocked_pending_audit"


def test_provisional_and_promising_are_the_last_two_levels():
    layers = _all_lookahead_layers()
    assert _verdict(sample_tier="provisional", no_lookahead=layers) == "provisional"
    promising = _verdict(no_lookahead=layers)
    assert promising == "promising"
    assert promising in PROMOTION_VERDICTS


def test_priority_table_rejects_unknown_dedup_and_tier():
    with pytest.raises(PromotionError, match="dedup 取值"):
        PromotionInputs(
            run_state=STATE_EVIDENCE_READY,
            stage_results=_stages(),
            sample_tier="trustworthy",
            cost_verdict=COST_POSITIVE,
            no_lookahead=build_no_lookahead(l1_status=LAYER_PASS, l1_evidence_refs=("x",)),
            dedup_verdict="mystery",
        )


# ---------- |ρ| 查重 ----------


def test_pearson_and_max_abs_rho_pick_the_larger_metric():
    left = DedupCandidate("a", oos_pnl=(1.0, 2.0, 3.0, 4.0), rolling_ic=(0.1, -0.1, 0.2, -0.2))
    right = DedupCandidate("b", oos_pnl=(2.0, 4.0, 6.0, 8.0), rolling_ic=(0.1, -0.1, 0.2, -0.2))
    assert pearson(left.oos_pnl, right.oos_pnl) == pytest.approx(1.0)
    assert max_abs_rho(left, right) == pytest.approx(1.0)
    with pytest.raises(DedupError, match="常数"):
        pearson((1.0, 1.0), (1.0, 2.0))
    with pytest.raises(DedupError, match="长度不一致"):
        pearson((1.0, 2.0), (1.0,))
    with pytest.raises(DedupError, match="不可比"):
        max_abs_rho(DedupCandidate("a"), DedupCandidate("b"))
    equal_oos_mismatched_ic_left = DedupCandidate(
        "a", oos_pnl=(1.0, 2.0, 3.0), rolling_ic=(1.0, 2.0)
    )
    equal_oos_mismatched_ic_right = DedupCandidate(
        "b", oos_pnl=(1.0, 2.0, 3.0), rolling_ic=(1.0, 2.0, 3.0, 4.0)
    )
    assert max_abs_rho(
        equal_oos_mismatched_ic_left, equal_oos_mismatched_ic_right
    ) == pytest.approx(1.0)


@pytest.mark.parametrize(
    ("rho", "verdict"),
    [
        (0.995, "rejected"),
        (0.9901, "rejected"),
        (0.99, "variant"),
        (0.95, "variant"),
        (0.90, "variant"),
        (0.8999, "none"),
    ],
)
def test_dedup_thresholds_are_frozen(rho: float, verdict: str):
    assert decide_verdict(rho) == verdict


def test_cohort_internal_duplicate_keeps_the_earlier_commitment():
    series = (1.0, 2.0, 3.0, 4.0, 5.0)
    early = DedupCandidate(CANDIDATE_A, oos_pnl=series, rolling_ic=series)
    late = DedupCandidate(CANDIDATE_B, oos_pnl=series, rolling_ic=series)
    outcomes = resolve_cohort_dedup([early, late])
    assert outcomes[CANDIDATE_A].verdict == "none"
    assert outcomes[CANDIDATE_A].against_factor_id is None
    assert outcomes[CANDIDATE_B].verdict == "rejected"
    assert outcomes[CANDIDATE_B].against_factor_id == CANDIDATE_A


def test_registry_records_participate_but_rejected_ones_do_not():
    series = (1.0, 2.0, 3.0, 4.0, 5.0)
    candidate = DedupCandidate("new", oos_pnl=series, rolling_ic=series)
    existing = DedupCandidate("old", oos_pnl=series, rolling_ic=series)
    hit = decide_dedup(
        candidate, registry_records=[DedupRecord("old")], registry_candidates={"old": existing}
    )
    assert hit.verdict == "rejected"
    assert hit.against_factor_id == "old"
    ignored = decide_dedup(
        candidate,
        registry_records=[DedupRecord("old", verdict="rejected")],
        registry_candidates={"old": existing},
    )
    assert ignored.verdict == "none"


def test_dedup_outcome_payload_shape():
    outcome = decide_dedup(DedupCandidate("solo", oos_pnl=(1.0, 2.0), rolling_ic=(1.0, 2.0)))
    assert outcome.to_payload() == {
        "max_abs_rho": 0.0,
        "verdict": "none",
        "against_factor_id": None,
    }


# ---------- 留出预算台账 ----------


def _entry(**overrides) -> HoldoutBudgetEntry:
    base = {
        "candidate_id": CANDIDATE_A,
        "iso_week": iso_week_of(datetime(2026, 9, 1, tzinfo=UTC)),
        "experiment_id": EXPERIMENT_A,
        "cohort_id": COHORT,
        "verdict": "promising",
        "recorded_at": FROZEN_AT,
    }
    base.update(overrides)
    return HoldoutBudgetEntry(**base)


def test_preview_cannot_append_to_holdout_ledger(tmp_path):
    preview = context_for("preview", tmp_path)
    with pytest.raises(CapabilityError, match="holdout_budget_writer"):
        append_entry(preview, tmp_path, _entry())
    assert read_ledger(tmp_path) == ()
    assert not ledger_path(tmp_path).exists()


def test_preview_overreach_on_ledger_leaves_gate_rejected_event(tmp_path):
    """R1-006 回归：越权写留出台账先留 gate_rejected 证据再失败关闭；台账保持零行。"""
    preview = context_for("preview", tmp_path)
    entry = _entry()
    with pytest.raises(CapabilityError, match="holdout_budget_writer"):
        append_entry(preview, tmp_path, entry)
    assert read_ledger(tmp_path) == ()
    assert not ledger_path(tmp_path).exists()
    events = read_events(rejections_path(tmp_path))
    assert len(events) == 1
    assert events[0].type == EVENT_GATE_REJECTED
    assert events[0].reason_code == "E_CANONICAL_FORBIDDEN"
    assert events[0].experiment_id == entry.experiment_id
    assert events[0].cohort_id == entry.cohort_id


def test_canonical_can_append_and_read_back(tmp_path):
    canonical = context_for("canonical", tmp_path)
    path = append_entry(
        canonical,
        tmp_path,
        _entry(holdout_window=("2026-09-01T00:00:00Z", "2026-10-01T00:00:00Z"), regime="bull"),
    )
    entries = read_ledger(tmp_path)
    assert path == ledger_path(tmp_path)
    assert len(entries) == 1
    assert entries[0].holdout_window == ("2026-09-01T00:00:00Z", "2026-10-01T00:00:00Z")
    assert entries[0].regime == "bull"


def test_ledger_rejects_non_canonical_entries():
    with pytest.raises(HoldoutBudgetError, match="只记录 canonical"):
        _entry(execution_tier="preview")
    with pytest.raises(HoldoutBudgetError, match="缺 verdict"):
        _entry(verdict="")


def test_ledger_invalid_recorded_at_is_mapped_to_holdout_error(tmp_path):
    """R1-120 回归：非法 recorded_at 必须抛 HoldoutBudgetError，read_ledger 能接住。"""
    path = ledger_path(tmp_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "candidate_id": "c",
                "iso_week": "2026-W36",
                "experiment_id": "e",
                "cohort_id": "k",
                "verdict": "promising",
                "recorded_at": "not-a-date",
                "execution_tier": "canonical",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(HoldoutBudgetError, match="非法"):
        read_ledger(tmp_path)


def test_preview_overreach_leaves_a_gate_rejected_event():
    event = rejection_event(
        experiment_id=EXPERIMENT_A,
        cohort_id=COHORT,
        execution_tier="preview",
        stage="cost_capacity",
    )
    assert event.type == EVENT_GATE_REJECTED
    assert event.reason_code == "E_CANONICAL_FORBIDDEN"
    assert "holdout_budget/ledger.jsonl" in event.evidence_refs


# ---------- cohort 冻结、登记与 finalize ----------


def _definition(*candidates: str) -> dict:
    return {
        "schema_version": 1,
        "hypothesis_family": "momentum-v1",
        "selection_stage": "cross_sectional",
        "method_config_ref": "method-v1",
        "cost_model_ref": "cm-v1",
        "inclusion_rules": "全部承诺成员计入分母",
        "commitments": [
            {"candidate_id": candidate, "generator": "alphagen", "registered_at": FROZEN_AT}
            for candidate in candidates
        ],
        "window": {
            "selection": ["2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"],
            "label_horizons": [1, 4, 24],
        },
        "universe_digest": "sha256:" + "f" * 64,
        "calendar_digest": "sha256:" + "0" * 64,
        "frozen_at": FROZEN_AT,
        "frozen_by": "Georg",
    }


def _registration(
    candidate: str, experiment: str, *, verdict: str = "promising"
) -> pop.MemberRegistration:
    return pop.MemberRegistration(
        candidate_id=candidate,
        experiment_id=experiment,
        run_state=STATE_REGISTERED,
        promotion_verdict=verdict,
        sample_tier="trustworthy",
        cost_model_version="cm-v1",
        evidence_ref=f"reports/bench/{candidate}/{experiment}/curves.parquet",
    )


def _registered_event(experiment: str, cohort_id: str):
    return build_event(
        experiment_id=experiment,
        execution_tier="canonical",
        cohort_id=cohort_id,
        from_state=STATE_EVIDENCE_READY,
        to_state=STATE_REGISTERED,
        event_type=EVENT_REGISTERED,
        sequence=0,
    )


def test_cohort_id_excludes_provenance_fields():
    first = pop.cohort_id_for(_definition(CANDIDATE_A))
    changed = {
        **_definition(CANDIDATE_A),
        "frozen_at": "2027-01-01T00:00:00Z",
        "frozen_by": "someone",
    }
    assert pop.cohort_id_for(changed) == first
    assert pop.cohort_id_for(_definition(CANDIDATE_A, CANDIDATE_B)) != first
    assert first.startswith("cohort_sha256:")


def test_freeze_cohort_is_idempotent_and_rejects_conflicts(tmp_path):
    cohort_id, path = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    assert path.is_file()
    assert pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))[0] == cohort_id
    tampered = _definition(CANDIDATE_A)
    tampered["frozen_by"] = "other"
    with pytest.raises(pop.RegistryIntegrityError, match="不一致"):
        pop.freeze_cohort(tmp_path, tampered)


def test_duplicate_commitments_are_rejected():
    with pytest.raises(pop.CohortError, match="重复"):
        pop.commitment_ids(_definition(CANDIDATE_A, CANDIDATE_A))


def test_missing_definition_fields_are_rejected():
    broken = _definition(CANDIDATE_A)
    del broken["window"]
    with pytest.raises(pop.CohortError, match="缺字段"):
        pop.cohort_id_for(broken)


def test_registration_must_be_a_terminal_registered_event(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    wrong_type = build_event(
        experiment_id=EXPERIMENT_A,
        execution_tier="canonical",
        cohort_id=cohort_id,
        from_state=STATE_EVIDENCE_READY,
        to_state=STATE_REGISTERED,
        sequence=0,
    )
    with pytest.raises(pop.CohortError, match="成员登记必须用"):
        pop.register_member(
            tmp_path, cohort_id, _registration(CANDIDATE_A, EXPERIMENT_A), wrong_type
        )
    not_terminal = pop.MemberRegistration(
        candidate_id=CANDIDATE_A,
        experiment_id=EXPERIMENT_A,
        run_state="RUNNING",
        promotion_verdict="promising",
    )
    with pytest.raises(pop.CohortError, match="成员终态"):
        pop.register_member(
            tmp_path, cohort_id, not_terminal, _registered_event(EXPERIMENT_A, cohort_id)
        )
    unknown = _registration("factor_sha256:" + "9" * 64, EXPERIMENT_A)
    with pytest.raises(pop.CohortError, match="不在 cohort 承诺内"):
        pop.register_member(
            tmp_path, cohort_id, unknown, _registered_event(EXPERIMENT_A, cohort_id)
        )


def test_registration_is_idempotent_by_event_id(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    event = _registered_event(EXPERIMENT_A, cohort_id)
    path = pop.register_member(tmp_path, cohort_id, _registration(CANDIDATE_A, EXPERIMENT_A), event)
    assert (
        pop.register_member(tmp_path, cohort_id, _registration(CANDIDATE_A, EXPERIMENT_A), event)
        == path
    )
    altered = _registration(CANDIDATE_A, EXPERIMENT_A, verdict="dead")
    with pytest.raises(pop.RegistryIntegrityError, match="内容不一致"):
        pop.register_member(tmp_path, cohort_id, altered, event)


def test_conflicting_duplicate_registration_is_rejected(tmp_path):
    """R1-007 回归：同一承诺用两个 event_id 登记且载荷不同时必须拒绝，不得静默 last-wins。"""
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    first_event = _registered_event(EXPERIMENT_A, cohort_id)
    second_event = build_event(
        experiment_id=EXPERIMENT_A,
        execution_tier="canonical",
        cohort_id=cohort_id,
        from_state=STATE_EVIDENCE_READY,
        to_state=STATE_REGISTERED,
        event_type=EVENT_REGISTERED,
        sequence=1,
    )
    pop.register_member(tmp_path, cohort_id, _registration(CANDIDATE_A, EXPERIMENT_A), first_event)
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_A, EXPERIMENT_A, verdict="dead"),
        second_event,
    )
    with pytest.raises(pop.RegistryIntegrityError, match="不一致"):
        pop.registrations(tmp_path, cohort_id)


def test_finalize_requires_every_commitment_and_writes_no_partial_verdict(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A, CANDIDATE_B))
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_A, EXPERIMENT_A),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    assert pop.missing_commitments(tmp_path, cohort_id) == (CANDIDATE_B,)
    with pytest.raises(pop.CohortError) as excinfo:
        pop.finalize_cohort(
            tmp_path, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=FROZEN_AT
        )
    assert excinfo.value.code == "E_COHORT_FROZEN"
    assert pop.load_verdict(tmp_path, cohort_id) is None


def test_finalize_records_counts_and_projection_rebuilds(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A, CANDIDATE_B))
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_A, EXPERIMENT_A),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_B, EXPERIMENT_B, verdict="rejected"),
        _registered_event(EXPERIMENT_B, cohort_id),
    )
    pop.assert_cohort_complete(tmp_path, cohort_id)
    pop.finalize_cohort(
        tmp_path, cohort_id, verdict={"fdr_alpha": 0.05, "dsr": 0.98}, finalized_at=FROZEN_AT
    )
    verdict = pop.load_verdict(tmp_path, cohort_id)
    assert verdict["status"] == "FINALIZED"
    assert verdict["trial_count"] == 2
    assert verdict["member_count"] == 2
    assert verdict["rejected_count"] == 1
    assert [entry.candidate_id for entry in pop.registrations(tmp_path, cohort_id)] == [
        CANDIDATE_A,
        CANDIDATE_B,
    ]
    derived = pop.cohort_dir(tmp_path, cohort_id) / "index"
    derived.mkdir(parents=True, exist_ok=True)
    (derived / "stale.json").write_text("{}", encoding="utf-8")
    pop.assert_projection_rebuilds(tmp_path, cohort_id)
    assert not derived.exists()


def test_finalize_is_idempotent_across_finalized_at_values(tmp_path):
    """R1-008 回归：重复 finalize 不因墙钟不同而报错，也不改写已写 verdict；语义冲突仍拒绝。"""
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_A, EXPERIMENT_A),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    path = pop.finalize_cohort(
        tmp_path, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=FROZEN_AT
    )
    before = path.read_bytes()
    again = pop.finalize_cohort(
        tmp_path,
        cohort_id,
        verdict={"fdr_alpha": 0.05},
        finalized_at="2030-01-01T00:00:00Z",
    )
    assert again == path
    assert path.read_bytes() == before
    with pytest.raises(pop.RegistryIntegrityError, match="不一致"):
        pop.finalize_cohort(
            tmp_path, cohort_id, verdict={"fdr_alpha": 0.99}, finalized_at=FROZEN_AT
        )


def _write_member_evidence(
    reports,
    candidate: str,
    experiment: str,
    returns,
    *,
    p_value: float = 0.01,
    with_report: bool = True,
    alpha: float = 0.05,
) -> str:
    directory = reports / "bench" / candidate / "snapshot" / experiment
    directory.mkdir(parents=True, exist_ok=True)
    times = tuple(
        datetime(2026, 9, 1, tzinfo=UTC) + timedelta(hours=index) for index in range(len(returns))
    )
    write_curves(directory / "curves.parquet", build_equity_curves(returns, times=times))
    if with_report:
        (directory / "report.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "required_statistics": {
                        "status": "PASS",
                        "p_value": p_value,
                        "method": {"fdr_alpha": alpha},
                    },
                }
            ),
            encoding="utf-8",
        )
    return f"bench/{candidate}/snapshot/{experiment}/curves.parquet"


def test_finalize_wires_cohort_dedup_and_overrides_verdict(tmp_path, monkeypatch):
    """R1-002 回归：finalize 内按承诺顺序查重，并据此重导 promotion_verdict（同一次原子写）。

    起点用生产可达的 `blocked_pending_audit`（`R1-116`），避免夹具手工注入不可达的 `promising`；
    删除 finalize 里的 `resolve_cohort_dedup` 调用后 B 不会变 `rejected`，本断言变红。
    """
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = pop.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    series = (0.05, 0.04, 0.06, 0.05, 0.055, 0.045)
    for candidate, experiment in ((CANDIDATE_A, EXPERIMENT_A), (CANDIDATE_B, EXPERIMENT_B)):
        pop.register_member(
            reports,
            cohort_id,
            pop.MemberRegistration(
                candidate_id=candidate,
                experiment_id=experiment,
                run_state=STATE_REGISTERED,
                promotion_verdict="blocked_pending_audit",
                sample_tier="trustworthy",
                cost_model_version="cm-v1",
                evidence_ref=_write_member_evidence(reports, candidate, experiment, series),
            ),
            _registered_event(experiment, cohort_id),
        )
    path = canonical_ops.finalize_cohort(cohort_id, finalized_at=FROZEN_AT)
    verdict = json.loads(path.read_text(encoding="utf-8"))
    dedup = verdict["cohort_statistics"]["dedup"]
    assert dedup[CANDIDATE_B]["verdict"] == "rejected"
    assert dedup[CANDIDATE_B]["against_factor_id"] == CANDIDATE_A
    assert dedup[CANDIDATE_A]["verdict"] == "none"
    members = {entry["candidate_id"]: entry for entry in verdict["members"]}
    assert members[CANDIDATE_A]["promotion_verdict"] == "blocked_pending_audit"
    assert members[CANDIDATE_B]["promotion_verdict"] == "rejected"
    assert verdict["rejected_count"] == 1
    from alphamill.evaluation.registry_writeback import read_evaluation_face

    assert {row["factor_id"] for row in read_evaluation_face(reports)} == {
        CANDIDATE_A,
        CANDIDATE_B,
    }


def test_finalize_downgrades_evidence_adequate_when_stats_incomplete(tmp_path, monkeypatch):
    """R1-101 回归：cohort 统计非 PASS 时证据达标类 verdict 必须降为 `incomplete`。

    只有 `promising` 会被降级是 v0.2 的失效点（`promising` 生产不可达）；本用例锁住
    `blocked_pending_audit` 也会被统计门降级。
    """
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = pop.freeze_cohort(reports, _definition(CANDIDATE_A))
    series = (0.05, 0.04, 0.06, 0.05, 0.055, 0.045)
    pop.register_member(
        reports,
        cohort_id,
        pop.MemberRegistration(
            candidate_id=CANDIDATE_A,
            experiment_id=EXPERIMENT_A,
            run_state=STATE_REGISTERED,
            promotion_verdict="blocked_pending_audit",
            sample_tier="trustworthy",
            cost_model_version="cm-v1",
            evidence_ref=_write_member_evidence(
                reports, CANDIDATE_A, EXPERIMENT_A, series, with_report=False
            ),
        ),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    path = canonical_ops.finalize_cohort(cohort_id, finalized_at=FROZEN_AT)
    verdict = json.loads(path.read_text(encoding="utf-8"))
    assert verdict["cohort_statistics"]["cohort_statistics"]["status"] == "INCOMPLETE"
    members = {entry["candidate_id"]: entry for entry in verdict["members"]}
    assert members[CANDIDATE_A]["promotion_verdict"] == "incomplete"


def test_statistically_insignificant_member_becomes_dead(tmp_path, monkeypatch):
    """R1-101 回归：cohort 统计 PASS 时 BH-FDR 未显著成员由证据达标降为 `dead`。"""
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = pop.freeze_cohort(reports, _definition(CANDIDATE_A))
    series = (0.05, 0.04, 0.06, 0.05, 0.055, 0.045)
    pop.register_member(
        reports,
        cohort_id,
        pop.MemberRegistration(
            candidate_id=CANDIDATE_A,
            experiment_id=EXPERIMENT_A,
            run_state=STATE_REGISTERED,
            promotion_verdict="blocked_pending_audit",
            sample_tier="trustworthy",
            cost_model_version="cm-v1",
            evidence_ref=_write_member_evidence(
                reports, CANDIDATE_A, EXPERIMENT_A, series, p_value=0.9
            ),
        ),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    path = canonical_ops.finalize_cohort(cohort_id, finalized_at=FROZEN_AT)
    verdict = json.loads(path.read_text(encoding="utf-8"))
    stats = verdict["cohort_statistics"]["cohort_statistics"]
    assert stats["status"] == "PASS"
    assert stats["bh_rejected"][CANDIDATE_A] is False
    members = {entry["candidate_id"]: entry for entry in verdict["members"]}
    assert members[CANDIDATE_A]["promotion_verdict"] == "dead"


def test_finalize_rejects_conflicting_member_fdr_alpha(tmp_path, monkeypatch):
    """R1-111 回归：成员间 `fdr_alpha` 不一致必须拒绝，不得静默 last-wins。"""
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = pop.freeze_cohort(reports, _definition(CANDIDATE_A, CANDIDATE_B))
    series = (0.05, 0.04, 0.06, 0.05, 0.055, 0.045)
    for candidate, experiment, alpha in (
        (CANDIDATE_A, EXPERIMENT_A, 0.05),
        (CANDIDATE_B, EXPERIMENT_B, 0.10),
    ):
        pop.register_member(
            reports,
            cohort_id,
            pop.MemberRegistration(
                candidate_id=candidate,
                experiment_id=experiment,
                run_state=STATE_REGISTERED,
                promotion_verdict="blocked_pending_audit",
                evidence_ref=_write_member_evidence(
                    reports, candidate, experiment, series, alpha=alpha
                ),
            ),
            _registered_event(experiment, cohort_id),
        )
    with pytest.raises(canonical_ops.CanonicalOpError, match="fdr_alpha 不一致"):
        canonical_ops.finalize_cohort(cohort_id, finalized_at=FROZEN_AT)


def test_unreadable_evidence_marks_cohort_incomplete_and_records_rejection(tmp_path, monkeypatch):
    """R1-112 回归：曲线/报告不可读不得静默剔除成员；必须写 gate_rejected 并标 INCOMPLETE。"""
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = pop.freeze_cohort(reports, _definition(CANDIDATE_A))
    pop.register_member(
        reports,
        cohort_id,
        pop.MemberRegistration(
            candidate_id=CANDIDATE_A,
            experiment_id=EXPERIMENT_A,
            run_state=STATE_REGISTERED,
            promotion_verdict="blocked_pending_audit",
            evidence_ref="bench/missing/snapshot/curves.parquet",
        ),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    path = canonical_ops.finalize_cohort(cohort_id, finalized_at=FROZEN_AT)
    verdict = json.loads(path.read_text(encoding="utf-8"))
    assert verdict["cohort_statistics"]["cohort_statistics"]["status"] == "INCOMPLETE"
    events = read_events(pop.cohort_dir(reports, cohort_id) / "gate_rejections.jsonl")
    assert len(events) == 1
    assert events[0].type == EVENT_GATE_REJECTED
    assert CANDIDATE_A in events[0].evidence_refs


def test_registrations_return_in_commitment_order(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_B, CANDIDATE_A))
    for candidate, experiment in ((CANDIDATE_A, EXPERIMENT_A), (CANDIDATE_B, EXPERIMENT_B)):
        pop.register_member(
            tmp_path,
            cohort_id,
            _registration(candidate, experiment),
            _registered_event(experiment, cohort_id),
        )
    assert [entry.candidate_id for entry in pop.registrations(tmp_path, cohort_id)] == [
        CANDIDATE_B,
        CANDIDATE_A,
    ]


def test_official_population_contains_no_canonical_leak_markers(tmp_path):
    cohort_id, _ = pop.freeze_cohort(tmp_path, _definition(CANDIDATE_A))
    pop.register_member(
        tmp_path,
        cohort_id,
        _registration(CANDIDATE_A, EXPERIMENT_A),
        _registered_event(EXPERIMENT_A, cohort_id),
    )
    project = pop.official_population(tmp_path, cohort_id)
    assert set(project) == {"cohort", "cohort_id", "registrations", "verdict"}
    assert project["verdict"] is None
    assert "lifecycle" not in json.dumps(project["registrations"])
