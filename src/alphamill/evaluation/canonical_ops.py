"""canonical 后续操作：abandon 与 finalize-cohort（`IR-001`/`TR-003`/`AC-003`；任务 T013）。

- `abandon` 只接受 canonical 下处于 `INCOMPLETE` 的 experiment（其他状态返回 `E_INPUT_INVALID`），
  要求非空 reason，写 `evaluation.run_state_changed`（`to=REGISTERED`）后按终态不完整结论登记，
  使耗不尽重试的成员不会把 cohort 永久挂在 `OPEN`；
- `finalize-cohort` 在承诺成员未收齐时非零拒绝（`E_COHORT_FROZEN`）且**不产生部分 verdict**，
  收齐后原子写 `cohort_verdict.json`。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation.contract_common import TIER_CANONICAL, UpstreamContractError
from alphamill.evaluation.events import (
    EVENT_REGISTERED,
    EVENT_RUN_STATE_CHANGED,
    append_events,
    build_event,
)
from alphamill.evaluation.run_state import STATE_INCOMPLETE, STATE_REGISTERED
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs

MANIFEST_NAME = "manifest.json"
BENCH_SUBDIR = "bench"


class CanonicalOpError(UpstreamContractError):
    """canonical 后续操作前置条件不满足；`E_INPUT_INVALID`。"""

    code = "E_INPUT_INVALID"


def find_canonical_manifest(root: Path, experiment_id: str) -> tuple[Path, dict[str, Any]] | None:
    bench = root / BENCH_SUBDIR
    if not bench.is_dir():
        return None
    for path in sorted(bench.rglob(MANIFEST_NAME)):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("experiment_id") == experiment_id:
            return path, payload
    return None


def abandon_experiment(
    *,
    experiment_id: str,
    reason: str,
    cohort_id: str,
    candidate_id: str,
    observed_at: str | None = None,
) -> Path:
    if not reason or not reason.strip():
        raise CanonicalOpError("abandon 需要非空 --reason")
    reports = rs.reports_root()
    found = find_canonical_manifest(reports, experiment_id)
    if found is None:
        raise CanonicalOpError(f"找不到 canonical experiment: {experiment_id}")
    path, manifest = found
    if manifest.get("state") != STATE_INCOMPLETE:
        raise CanonicalOpError(
            f"abandon 只接受 {STATE_INCOMPLETE} 状态的 experiment，当前 {manifest.get('state')!r}"
        )
    moment = observed_at or datetime.now(UTC).isoformat()
    transition = build_event(
        experiment_id=experiment_id,
        execution_tier=TIER_CANONICAL,
        cohort_id=cohort_id,
        from_state=STATE_INCOMPLETE,
        to_state=STATE_REGISTERED,
        event_type=EVENT_RUN_STATE_CHANGED,
        reason_code=reason,
        sequence=0,
    )
    append_events(path.parent / "events.jsonl", (transition,))
    registration = population.MemberRegistration(
        candidate_id=candidate_id,
        experiment_id=experiment_id,
        run_state=STATE_REGISTERED,
        promotion_verdict="incomplete",
        evidence_ref=f"{path.parent.as_posix()}/curves.parquet",
    )
    registered = build_event(
        experiment_id=experiment_id,
        execution_tier=TIER_CANONICAL,
        cohort_id=cohort_id,
        from_state=STATE_INCOMPLETE,
        to_state=STATE_REGISTERED,
        event_type=EVENT_REGISTERED,
        reason_code=reason,
        sequence=0,
    )
    assert moment
    return population.register_member(reports, cohort_id, registration, registered)


def finalize_cohort(cohort_id: str, *, finalized_at: str | None = None) -> Path:
    """收齐后原子写 `cohort_verdict.json`；未收齐即 `E_COHORT_FROZEN`（不留部分 verdict）。"""
    reports = rs.reports_root()
    population.assert_cohort_complete(reports, cohort_id)
    entries = population.registrations(reports, cohort_id)
    verdict = {
        "fdr_alpha": 0.05,
        "basis": "member_evidence",
        "rejected_count": sum(1 for entry in entries if entry.promotion_verdict == "rejected"),
        "promotion_verdicts": {entry.candidate_id: entry.promotion_verdict for entry in entries},
    }
    return population.finalize_cohort(
        reports,
        cohort_id,
        verdict=verdict,
        finalized_at=finalized_at or datetime.now(UTC).isoformat(),
    )
