"""canonical 登记与恢复支持（`R1-003`；从 `canonical.py` 拆出以守住单文件上限）。

- `stage_results_from_manifest` / `registered_events`：canonical 正常路径与复用路径共用的
  manifest 读取与登记事件构造；
- `ensure_member_registered`：复用已发布批次前**幂等补登记**——崩溃窗口只丢失登记时，
  cohort 不会永久挂在 OPEN。
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import (
    EVENT_REGISTERED,
    EVENTS_FILENAME,
    RunEvent,
    build_event,
    read_events,
)
from alphamill.evaluation.run_state import (
    STATE_EVIDENCE_READY,
    STATE_REGISTERED,
    STATE_REJECTED,
)
from alphamill.experiment_store import population
from alphamill.experiment_store.promotion import PromotionInputs, derive_promotion_verdict
from alphamill.validation.no_lookahead import (
    STATUS_NOT_YET_AVAILABLE,
    build_no_lookahead,
)

CANONICAL_STATE_MANIFEST = "manifest.json"


def stage_results_from_manifest(manifest: Mapping[str, Any]) -> Any:
    from alphamill.factor_factory.bench.stage_model import StageResults

    return StageResults.from_payload(manifest.get("stage_results", []))


def registered_events(
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


def ensure_member_registered(
    *,
    reports: Path,
    cohort_id: str,
    candidate_id: str,
    experiment_id: str,
    target: Path,
    config: Any,
) -> None:
    """复用已发布批次前幂等补登记，修复「已发布但未登记」的崩溃窗口。"""
    if any(
        entry.candidate_id == candidate_id for entry in population.registrations(reports, cohort_id)
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
                stage_results=stage_results_from_manifest(manifest),
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
