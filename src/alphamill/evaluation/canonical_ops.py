"""canonical 后续操作：abandon 与 finalize-cohort（`IR-001`/`TR-003`/`AC-003`；任务 T013）。

- `abandon` 只接受 canonical 下处于 `INCOMPLETE` 的 experiment（其他状态返回 `E_INPUT_INVALID`），
  要求非空 reason，写 `evaluation.run_state_changed`（`to=REGISTERED`）后按终态不完整结论登记，
  使耗不尽重试的成员不会把 cohort 永久挂在 `OPEN`；
- `finalize-cohort` 在承诺成员未收齐时非零拒绝（`E_COHORT_FROZEN`）且**不产生部分 verdict**，
  收齐后原子写 `cohort_verdict.json`。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
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
from alphamill.evaluation.registry_writeback import read_evaluation_face
from alphamill.evaluation.required_statistics import cohort_statistics
from alphamill.evaluation.run_state import STATE_INCOMPLETE, STATE_REGISTERED
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.dedup import (
    DedupCandidate,
    DedupError,
    DedupRecord,
    resolve_cohort_dedup,
)
from alphamill.factor_factory.bench.curves import CurvesError, read_curves

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
        evidence_ref=f"{path.parent.relative_to(reports).as_posix()}/curves.parquet",
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


def _resolve_reference(root: Path, reference: str | None) -> Path | None:
    if not reference:
        return None
    path = Path(reference)
    if path.is_absolute():
        return path
    candidate = root / path
    if candidate.exists():
        return candidate
    if path.parts and path.parts[0] == "reports":
        return root / Path(*path.parts[1:])
    return candidate


def _load_member_curves(root: Path, entry: population.MemberRegistration) -> Any:
    path = _resolve_reference(root, entry.evidence_ref)
    if path is None:
        return None
    try:
        return read_curves(path)
    except CurvesError:
        return None


def _load_member_report(root: Path, entry: population.MemberRegistration) -> dict[str, Any] | None:
    path = _resolve_reference(root, entry.evidence_ref)
    if path is None:
        return None
    report_path = path.parent / "report.json"
    if not report_path.is_file():
        return None
    return json.loads(report_path.read_text(encoding="utf-8"))


def _load_registry(
    root: Path, horizon: int
) -> tuple[tuple[DedupRecord, ...], dict[str, DedupCandidate]]:
    records: list[DedupRecord] = []
    candidates: dict[str, DedupCandidate] = {}
    for row in read_evaluation_face(root):
        dedup = row.get("dedup") or {}
        verdict = str(dedup.get("verdict", "none"))
        factor_id = str(row["factor_id"])
        records.append(DedupRecord(factor_id=factor_id, verdict=verdict))
        if verdict == "rejected":
            continue
        path = _resolve_reference(root, row.get("evidence_ref"))
        if path is None:
            continue
        try:
            curves = read_curves(path)
        except CurvesError:
            continue
        candidates[factor_id] = DedupCandidate.from_curves(
            factor_id, curves, horizon, evidence_ref=row.get("evidence_ref")
        )
    return tuple(records), candidates


def _horizon_of(definition: Mapping[str, Any]) -> int:
    horizons = (definition.get("window") or {}).get("label_horizons") or [1]
    return max(int(horizon) for horizon in horizons)


def finalize_cohort(cohort_id: str, *, finalized_at: str | None = None) -> Path:
    """finalize 内先 `|ρ|` 查重、再导出 verdict，最后原子写 `cohort_verdict.json`。

    查重与 verdict 导出在同一次原子写内完成（`FR-008`/`AC-013`），不存在「先发布 verdict、
    后补查重」的窗口；cohort 级 BH-FDR/DSR/MinTRL 由成员必需统计与成对相关性导出，任一估计器
    异常把 cohort 统计标为 `INCOMPLETE` 并阻断 `promising`（`FR-003`/`R1-001`/`R1-002`）。
    """
    reports = rs.reports_root()
    population.assert_cohort_complete(reports, cohort_id)
    definition = population.load_cohort(reports, cohort_id)
    entries = population.registrations(reports, cohort_id)
    horizon = _horizon_of(definition)

    curves_by_candidate: dict[str, Any] = {}
    for entry in entries:
        curves = _load_member_curves(reports, entry)
        if curves is not None:
            curves_by_candidate[entry.candidate_id] = curves

    members_in_order = [
        DedupCandidate.from_curves(
            entry.candidate_id,
            curves_by_candidate[entry.candidate_id],
            horizon,
            evidence_ref=entry.evidence_ref,
        )
        for entry in entries
        if entry.candidate_id in curves_by_candidate and entry.promotion_verdict != "rejected"
    ]
    registry_records, registry_candidates = _load_registry(reports, horizon)
    dedup_reason: str | None = None
    outcomes: dict[str, Any] = {}
    try:
        outcomes = resolve_cohort_dedup(
            members_in_order,
            registry_records=registry_records,
            registry_candidates=registry_candidates,
        )
    except DedupError as exc:
        dedup_reason = f"查重不可判定: {exc}"

    p_values: list[float] = []
    member_returns: list[tuple[float, ...]] = []
    alpha = 0.05
    for entry in entries:
        report = _load_member_report(reports, entry)
        statistics = (report or {}).get("required_statistics") or {}
        if statistics.get("p_value") is not None:
            p_values.append(float(statistics["p_value"]))
        method = statistics.get("method") or {}
        if method.get("fdr_alpha") is not None:
            alpha = float(method["fdr_alpha"])
        curves = curves_by_candidate.get(entry.candidate_id)
        if curves is not None:
            member_returns.append(tuple(curves.long_short))

    ordered = [member.factor_id for member in members_in_order]
    correlations = [
        outcomes[candidate].max_abs_rho for candidate in ordered[1:] if candidate in outcomes
    ]
    statistics_payload = cohort_statistics(
        p_values=p_values,
        correlations=correlations,
        member_returns=member_returns,
        alpha=alpha,
    )
    if dedup_reason is not None:
        statistics_payload = {
            **statistics_payload,
            "status": "INCOMPLETE",
            "dedup_status": "INCOMPLETE",
            "reason": statistics_payload.get("reason", dedup_reason),
        }

    promotion_verdicts: dict[str, str] = {}
    dedup_payloads: dict[str, Any] = {}
    for entry in entries:
        candidate = entry.candidate_id
        candidate_dedup = entry.dedup or (
            outcomes[candidate].to_payload() if candidate in outcomes else None
        )
        if candidate_dedup is not None:
            dedup_payloads[candidate] = candidate_dedup
        verdict = entry.promotion_verdict
        if candidate_dedup is not None and candidate_dedup.get("verdict") == "rejected":
            verdict = "rejected"
        if statistics_payload.get("status") != "PASS" and verdict == "promising":
            verdict = STATE_INCOMPLETE
        promotion_verdicts[candidate] = verdict

    verdict = {
        "fdr_alpha": alpha,
        "basis": "member_evidence",
        "cohort_statistics": statistics_payload,
        "dedup": dedup_payloads,
        "promotion_verdicts": promotion_verdicts,
    }
    return population.finalize_cohort(
        reports,
        cohort_id,
        verdict=verdict,
        finalized_at=finalized_at or datetime.now(UTC).isoformat(),
    )
