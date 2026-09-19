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

from alphamill.evaluation.capabilities import context_for
from alphamill.evaluation.contract_common import TIER_CANONICAL, UpstreamContractError
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    EVENT_REGISTERED,
    EVENT_RUN_STATE_CHANGED,
    append_events,
    build_event,
)
from alphamill.evaluation.registry_writeback import (
    build_summaries,
    read_evaluation_face,
    writeback_evaluation_face,
)
from alphamill.evaluation.required_statistics import cohort_statistics
from alphamill.evaluation.run_state import STATE_CREATED, STATE_INCOMPLETE, STATE_REGISTERED
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.dedup import (
    DedupCandidate,
    DedupError,
    DedupRecord,
    max_abs_rho,
    resolve_cohort_dedup,
)
from alphamill.experiment_store.promotion import VERDICT_INCOMPLETE
from alphamill.factor_factory.bench.curves import CurvesError, read_curves

MANIFEST_NAME = "manifest.json"
BENCH_SUBDIR = "bench"
EVIDENCE_ADEQUATE_VERDICTS = ("promising", "provisional", "blocked_pending_audit")


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


def _record_unreadable_evidence(
    reports: Path, cohort_id: str, entry: population.MemberRegistration
) -> None:
    append_events(
        population.cohort_dir(reports, cohort_id) / "gate_rejections.jsonl",
        (
            build_event(
                experiment_id=entry.experiment_id,
                execution_tier=TIER_CANONICAL,
                cohort_id=cohort_id,
                from_state=STATE_CREATED,
                to_state=STATE_INCOMPLETE,
                event_type=EVENT_GATE_REJECTED,
                reason_code="E_PUBLISH_INCOMPLETE",
                evidence_refs=(entry.candidate_id, entry.evidence_ref or ""),
            ),
        ),
    )


def finalize_cohort(cohort_id: str, *, finalized_at: str | None = None) -> Path:
    """finalize 内先 `|ρ|` 查重、再导出 verdict，最后原子写 `cohort_verdict.json`。

    查重与 verdict 导出在同一次原子写内完成（`FR-008`/`AC-013`），不存在「先发布 verdict、
    后补查重」的窗口。cohort 级 BH-FDR/DSR/MinTRL 由成员必需统计与两两相关性导出：
    统计 `INCOMPLETE` 时把证据达标类 verdict 降为 `incomplete`；统计 `PASS` 时把 BH-FDR 未
    显著或 DSR 不达标的 EVIDENCE_ADEQUATE 成员判 `dead`。任一估计器缺失/异常即失败关闭。
    """
    reports = rs.reports_root()
    population.assert_cohort_complete(reports, cohort_id)
    definition = population.load_cohort(reports, cohort_id)
    entries = population.registrations(reports, cohort_id)
    horizon = _horizon_of(definition)

    curves_by_candidate: dict[str, Any] = {}
    reports_by_candidate: dict[str, dict[str, Any]] = {}
    for entry in entries:
        curves = _load_member_curves(reports, entry)
        report = _load_member_report(reports, entry)
        if curves is None or report is None:
            _record_unreadable_evidence(reports, cohort_id, entry)
            continue
        curves_by_candidate[entry.candidate_id] = curves
        reports_by_candidate[entry.candidate_id] = report

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

    member_p_values: dict[str, float] = {}
    member_returns: dict[str, tuple[float, ...]] = {}
    alphas: set[float] = set()
    for entry in entries:
        statistics = (reports_by_candidate.get(entry.candidate_id) or {}).get(
            "required_statistics"
        ) or {}
        if statistics.get("p_value") is not None:
            member_p_values[entry.candidate_id] = float(statistics["p_value"])
        method = statistics.get("method") or {}
        if method.get("fdr_alpha") is not None:
            alphas.add(float(method["fdr_alpha"]))
        curves = curves_by_candidate.get(entry.candidate_id)
        if curves is not None:
            member_returns[entry.candidate_id] = tuple(curves.long_short)
    if len(alphas) > 1:
        raise CanonicalOpError(f"成员间 fdr_alpha 不一致: {sorted(alphas)}")
    alpha = next(iter(alphas), 0.05)

    correlations: list[float] = []
    for index, member in enumerate(members_in_order):
        if index == 0:
            continue
        pair_rhos = []
        for earlier in members_in_order[:index]:
            try:
                pair_rhos.append(max_abs_rho(member, earlier))
            except DedupError:
                continue
        if pair_rhos:
            correlations.append(sum(pair_rhos) / len(pair_rhos))

    statistics_payload = cohort_statistics(
        member_p_values=member_p_values,
        member_returns=member_returns,
        correlations=correlations,
        alpha=alpha,
    )
    if len(reports_by_candidate) != len(entries):
        statistics_payload = {
            **statistics_payload,
            "status": "INCOMPLETE",
            "reason": statistics_payload.get("reason") or "存在不可读成员证据（曲线/报告）",
        }
    if dedup_reason is not None:
        statistics_payload = {
            **statistics_payload,
            "status": "INCOMPLETE",
            "dedup_status": "INCOMPLETE",
            "reason": statistics_payload.get("reason", dedup_reason),
        }

    bh_rejected = statistics_payload.get("bh_rejected") or {}
    dsr_map = statistics_payload.get("dsr") or {}
    dead_threshold = 1.0 - alpha

    def statistically_dead(candidate: str) -> bool:
        if candidate in bh_rejected and not bh_rejected[candidate]:
            return True
        value = dsr_map.get(candidate)
        return value is not None and value < dead_threshold

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
        elif verdict in EVIDENCE_ADEQUATE_VERDICTS:
            if statistics_payload.get("status") != "PASS":
                verdict = VERDICT_INCOMPLETE
            elif statistically_dead(candidate):
                verdict = "dead"
        promotion_verdicts[candidate] = verdict

    moment = finalized_at or datetime.now(UTC).isoformat()
    verdict = {
        "fdr_alpha": alpha,
        "basis": "member_evidence",
        "cohort_statistics": statistics_payload,
        "dedup": dedup_payloads,
        "promotion_verdicts": promotion_verdicts,
    }
    path = population.finalize_cohort(
        reports,
        cohort_id,
        verdict=verdict,
        finalized_at=moment,
    )
    writeback_evaluation_face(
        context_for(TIER_CANONICAL, reports),
        reports,
        build_summaries(cohort_id, finalized_at=moment),
    )
    return path
