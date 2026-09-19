"""T025 / `SC-002`·`NFR-001`·`AC-001`·`AC-003`：并发、lease 接管与 finalize 原子性故障注入。

覆盖 SC-002 的四条：同 ID 并发 claim 只有一个成功；崩溃后只有 lease 过期 ∧ 无活进程 ∧ temp 未发布
才可接管（正常路径不能偷锁）；finalize 失败不产生部分 `cohort_verdict`（失败后可重试）；registration
幂等重试不重复计数。
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta

import pytest

from alphamill.evaluation.claim import (
    ClaimBusyError,
    acquire,
    assert_takeover_allowed,
    claim_file_exists,
    claim_path,
    is_process_alive,
    read_claim,
    recover,
    release,
)
from alphamill.evaluation.events import EVENT_REGISTERED, build_event
from alphamill.evaluation.run_state import STATE_EVIDENCE_READY, STATE_REGISTERED
from alphamill.experiment_store import population

pytestmark = pytest.mark.integration

EXPERIMENT = "sha256:" + "1" * 64
CANDIDATE = "factor_sha256:" + "a" * 64
NOW = datetime(2026, 9, 1, tzinfo=UTC)
FROZEN_AT = "2026-09-01T00:00:00Z"


def _definition(candidate: str) -> dict:
    return {
        "schema_version": 1,
        "hypothesis_family": "momentum-v1",
        "selection_stage": "cross_sectional",
        "method_config_ref": "method-v1",
        "cost_model_ref": "cm-v1",
        "inclusion_rules": "全部承诺成员计入分母",
        "commitments": [
            {"candidate_id": candidate, "generator": "manual", "registered_at": FROZEN_AT}
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


# ---------- 并发 claim ----------


def test_concurrent_claim_single_winner(tmp_path):
    first = acquire(tmp_path, EXPERIMENT, owner_token="runner-a", now=NOW)
    assert first.owner_token == "runner-a"
    assert read_claim(tmp_path, EXPERIMENT) == first
    with pytest.raises(ClaimBusyError, match="已被 runner-a 持有"):
        acquire(tmp_path, EXPERIMENT, owner_token="runner-b", now=NOW)
    assert claim_path(tmp_path, EXPERIMENT).is_file()


def test_release_requires_the_owner_token(tmp_path):
    acquire(tmp_path, EXPERIMENT, owner_token="runner-a", now=NOW)
    with pytest.raises(ClaimBusyError, match="不得释放他人 claim"):
        release(tmp_path, EXPERIMENT, owner_token="runner-b")
    release(tmp_path, EXPERIMENT, owner_token="runner-a")
    assert read_claim(tmp_path, EXPERIMENT) is None
    acquire(tmp_path, EXPERIMENT, owner_token="runner-b", now=NOW)


# ---------- lease 接管 ----------


def test_takeover_requires_expired_lease_and_dead_process(tmp_path):
    claim = acquire(tmp_path, EXPERIMENT, owner_token="runner-a", lease_seconds=60, now=NOW)
    assert claim.is_expired(NOW + timedelta(seconds=30)) is False
    assert claim.is_expired(NOW + timedelta(seconds=61)) is True
    with pytest.raises(ClaimBusyError, match="lease 未过期"):
        assert_takeover_allowed(claim, now=NOW + timedelta(seconds=30), process_alive=False)
    with pytest.raises(ClaimBusyError, match="持有进程仍存活"):
        assert_takeover_allowed(claim, now=NOW + timedelta(seconds=61), process_alive=True)
    with pytest.raises(ClaimBusyError, match="temp artifact 已发布"):
        assert_takeover_allowed(
            claim, now=NOW + timedelta(seconds=61), process_alive=False, temp_published=True
        )
    assert_takeover_allowed(
        claim, now=NOW + timedelta(seconds=61), process_alive=False, temp_published=False
    )


def test_recover_is_refused_while_lease_is_live(tmp_path):
    acquire(tmp_path, EXPERIMENT, owner_token="runner-a", lease_seconds=600, now=NOW)
    with pytest.raises(ClaimBusyError, match="不得接管"):
        recover(
            tmp_path,
            EXPERIMENT,
            owner_token="recovery",
            now=NOW + timedelta(seconds=10),
            process_alive=False,
        )
    assert read_claim(tmp_path, EXPERIMENT).owner_token == "runner-a"


def test_recover_takes_over_only_after_crash(tmp_path):
    acquire(tmp_path, EXPERIMENT, owner_token="runner-a", lease_seconds=60, now=NOW)
    taken = recover(
        tmp_path,
        EXPERIMENT,
        owner_token="recovery",
        lease_seconds=60,
        now=NOW + timedelta(seconds=120),
        process_alive=False,
    )
    assert taken.owner_token == "recovery"
    assert read_claim(tmp_path, EXPERIMENT).owner_token == "recovery"


def test_recover_on_free_claim_just_acquires(tmp_path):
    claim = recover(tmp_path, EXPERIMENT, owner_token="runner-a", now=NOW)
    assert claim.owner_token == "runner-a"


def test_corrupt_claim_is_treated_as_stale_and_recoverable(tmp_path):
    """R1-105 回归：空/损坏 claim 不再抛 JSONDecodeError，acquire 报 busy、recover 可接管。"""
    claim_path(tmp_path, EXPERIMENT).write_text("", encoding="utf-8")
    assert read_claim(tmp_path, EXPERIMENT) is None
    assert claim_file_exists(tmp_path, EXPERIMENT) is True
    with pytest.raises(ClaimBusyError, match="corrupt"):
        acquire(tmp_path, EXPERIMENT, owner_token="runner-b", now=NOW)
    taken = recover(tmp_path, EXPERIMENT, owner_token="recovery", now=NOW)
    assert taken.owner_token == "recovery"
    assert read_claim(tmp_path, EXPERIMENT).owner_token == "recovery"


def test_takeover_guard_serializes_and_preserves_single_writer(tmp_path):
    """R2-202 回归：接管临界区串行——他人持接管锁时本进程接管必须失败，任一时刻至多一个持有者。"""
    import alphamill.evaluation.claim as claim_module

    acquire(tmp_path, EXPERIMENT, owner_token="dead", lease_seconds=1, now=NOW)
    now = NOW + timedelta(seconds=120)
    claim_file = claim_path(tmp_path, EXPERIMENT)
    guard = claim_file.with_name(f"{claim_file.name}{claim_module.TAKEOVER_SUFFIX}")
    guard.write_text(json.dumps({"pid": os.getpid()}), encoding="utf-8")
    try:
        with pytest.raises(ClaimBusyError, match="接管"):
            recover(tmp_path, EXPERIMENT, owner_token="A", now=now, process_alive=False)
    finally:
        guard.unlink(missing_ok=True)
    taken = recover(tmp_path, EXPERIMENT, owner_token="B", now=now, process_alive=False)
    assert taken.owner_token == "B"
    with pytest.raises(ClaimBusyError):
        recover(tmp_path, EXPERIMENT, owner_token="C", now=now, process_alive=False)
    assert read_claim(tmp_path, EXPERIMENT).owner_token == "B"


def test_stale_takeover_guard_is_reclaimed(tmp_path):
    """R2-202：残留接管锁（持有进程已死）可被回收，不永久堵死 experiment_id。"""
    import alphamill.evaluation.claim as claim_module

    acquire(tmp_path, EXPERIMENT, owner_token="dead", lease_seconds=1, now=NOW)
    now = NOW + timedelta(seconds=120)
    claim_file = claim_path(tmp_path, EXPERIMENT)
    guard = claim_file.with_name(f"{claim_file.name}{claim_module.TAKEOVER_SUFFIX}")
    guard.write_text(json.dumps({"pid": 999999}), encoding="utf-8")
    taken = recover(tmp_path, EXPERIMENT, owner_token="recovery", now=now, process_alive=False)
    assert taken.owner_token == "recovery"


def test_release_refuses_corrupt_claim(tmp_path):
    claim_path(tmp_path, EXPERIMENT).write_text("{not json", encoding="utf-8")
    with pytest.raises(ClaimBusyError, match="不可识别"):
        release(tmp_path, EXPERIMENT, owner_token="runner-a")


def test_process_liveness_probe_is_conservative():
    assert is_process_alive(0) is False
    assert is_process_alive(-1) is False
    assert is_process_alive(os.getpid()) is True


# ---------- finalize 原子性 ----------


def test_finalize_failure_leaves_no_partial_verdict_and_is_retryable(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE))
    population.register_member(
        reports,
        cohort_id,
        population.MemberRegistration(
            candidate_id=CANDIDATE,
            experiment_id=EXPERIMENT,
            run_state=STATE_REGISTERED,
            promotion_verdict="promising",
        ),
        _registered_event(EXPERIMENT, cohort_id),
    )
    assert population.load_verdict(reports, cohort_id) is None

    original_replace = os.replace

    def failing_replace(source, target, *args, **kwargs):
        raise OSError("simulated crash before rename")

    monkeypatch.setattr("os.replace", failing_replace)
    with pytest.raises(OSError, match="simulated crash"):
        population.finalize_cohort(
            reports, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=FROZEN_AT
        )
    monkeypatch.setattr("os.replace", original_replace)
    assert population.load_verdict(reports, cohort_id) is None

    path = population.finalize_cohort(
        reports, cohort_id, verdict={"fdr_alpha": 0.05}, finalized_at=FROZEN_AT
    )
    assert path.is_file()
    assert population.load_verdict(reports, cohort_id)["status"] == "FINALIZED"


# ---------- registration 幂等 ----------


def test_registration_retry_does_not_double_count(tmp_path, monkeypatch):
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    cohort_id, _ = population.freeze_cohort(reports, _definition(CANDIDATE))
    event = _registered_event(EXPERIMENT, cohort_id)
    registration = population.MemberRegistration(
        candidate_id=CANDIDATE,
        experiment_id=EXPERIMENT,
        run_state=STATE_REGISTERED,
        promotion_verdict="promising",
    )
    for _attempt in range(3):
        population.register_member(reports, cohort_id, registration, event)
    entries = population.registrations(reports, cohort_id)
    assert len(entries) == 1
    assert population.load_verdict(reports, cohort_id) is None
