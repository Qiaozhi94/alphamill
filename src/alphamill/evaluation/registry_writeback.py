"""F003 注册表**评测面**回写适配器（`FR-008`/`DR-008`/`AC-013`；任务 T018）。

F007 是注册表**评测面**的唯一写入 owner，规则是**只搬运、不重算**：

- cohort `FINALIZED` 后才回写（否则 `E_COHORT_FROZEN`）；载荷严格取 `DR-008` 字段集，其中
  `promotion_verdict` / `sample_tier` / `dedup` 全部来自 T012 finalize 已产出的结论；
- 载荷**不含任何 lifecycle 状态字段**（衰减/下线判定后移 M3/F006）——出现即拒绝；
- **定义面不可写**：`FactorDef` 表达式/定义摘要/定义版本任何写入尝试即 `E_CANONICAL_FORBIDDEN`
  （`AC-013` 场景「定义面越权写入」）；
- 追加是 append-only 且按 `(cohort_id, factor_id)` 幂等：重复回写同一条目不产生第二行，也不
  重复计数（`FR-004` 的「诊断性重算不重复计数」在回写面同样成立）。
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphamill.evaluation.capabilities import CAP_CANONICAL_WRITER, CapabilityError, TierContext
from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    append_events,
    build_event,
)
from alphamill.evaluation.run_state import STATE_CREATED, STATE_INCOMPLETE
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs

SCHEMA_VERSION = 1
REGISTRY_SUBDIR = "factor_registry"
EVALUATION_FACE_NAME = "evaluation_face.jsonl"
DR008_FIELDS = (
    "schema_version",
    "factor_id",
    "cohort_id",
    "experiment_id",
    "promotion_verdict",
    "sample_tier",
    "cost_model_version",
    "dedup",
    "evidence_ref",
    "finalized_at",
)
DEDUP_FIELDS = ("max_abs_rho", "verdict", "against_factor_id")
DEFINITION_FACE_FIELDS = ("expression", "definition_digest", "definition_version")
LIFECYCLE_TOKENS = ("lifecycle", "decay", "retired", "state")


class WritebackError(ValueError):
    """载荷字段越界（含 lifecycle 字段）或 cohort 未 finalize。"""


@dataclass(frozen=True)
class EvaluationSummary:
    factor_id: str
    cohort_id: str
    experiment_id: str
    promotion_verdict: str
    sample_tier: str | None = None
    cost_model_version: str | None = None
    dedup: Mapping[str, Any] | None = None
    evidence_ref: str | None = None
    finalized_at: str = ""
    schema_version: int = SCHEMA_VERSION

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "factor_id": self.factor_id,
            "cohort_id": self.cohort_id,
            "experiment_id": self.experiment_id,
            "promotion_verdict": self.promotion_verdict,
            "sample_tier": self.sample_tier,
            "cost_model_version": self.cost_model_version,
            "dedup": dict(self.dedup) if self.dedup else None,
            "evidence_ref": self.evidence_ref,
            "finalized_at": self.finalized_at,
        }


def evaluation_face_path(root: Path) -> Path:
    return root / REGISTRY_SUBDIR / EVALUATION_FACE_NAME


def assert_payload_is_dr008(payload: Mapping[str, Any]) -> None:
    """载荷只能含 `DR-008` 字段；定义面字段或任何 lifecycle 字段即拒绝。"""
    extra = sorted(set(payload) - set(DR008_FIELDS))
    if extra:
        raise WritebackError(f"评测面载荷含 DR-008 之外的字段: {extra}")
    missing = [field for field in DR008_FIELDS if field not in payload]
    if missing:
        raise WritebackError(f"评测面载荷缺 DR-008 字段: {missing}")
    for key in payload:
        if any(token in str(key).lower() for token in LIFECYCLE_TOKENS):
            raise WritebackError(f"评测面载荷不得含 lifecycle 状态字段: {key}")
    dedup = payload.get("dedup")
    if dedup is not None:
        unknown = sorted(set(dedup) - set(DEDUP_FIELDS))
        if unknown:
            raise WritebackError(f"dedup 载荷含未知字段: {unknown}")


def build_summaries(
    cohort_id: str, *, finalized_at: str | None = None
) -> tuple[EvaluationSummary, ...]:
    """从已 finalize 的登记搬运结论；**不重算**查重与 verdict。"""
    root = rs.reports_root()
    verdict = population.load_verdict(root, cohort_id)
    if verdict is None:
        raise population.CohortError(f"cohort {cohort_id} 尚未 FINALIZED，评测面回写被拒绝")
    moment = finalized_at or str(verdict.get("finalized_at", ""))
    members = verdict.get("members") or [
        entry.to_payload() for entry in population.registrations(root, cohort_id)
    ]
    summaries = []
    for member in members:
        summaries.append(
            EvaluationSummary(
                factor_id=str(member["candidate_id"]),
                cohort_id=cohort_id,
                experiment_id=str(member["experiment_id"]),
                promotion_verdict=str(member["promotion_verdict"]),
                sample_tier=member.get("sample_tier"),
                cost_model_version=member.get("cost_model_version"),
                dedup=member.get("dedup"),
                evidence_ref=member.get("evidence_ref"),
                finalized_at=moment,
            )
        )
    return tuple(summaries)


def read_evaluation_face(root: Path) -> tuple[dict[str, Any], ...]:
    path = evaluation_face_path(root)
    if not path.is_file():
        return ()
    return tuple(
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )


def writeback_evaluation_face(
    context: TierContext,
    root: Path,
    summaries: Iterable[EvaluationSummary],
) -> Path:
    """append-only 追加评测摘要；同 `(cohort_id, factor_id)` 幂等，不产生第二行。"""
    context.require(CAP_CANONICAL_WRITER)
    existing = read_evaluation_face(root)
    known = {(row["cohort_id"], row["factor_id"]) for row in existing}
    appended: list[dict[str, Any]] = []
    for summary in summaries:
        payload = summary.to_payload()
        assert_payload_is_dr008(payload)
        key = (summary.cohort_id, summary.factor_id)
        if key in known:
            continue
        known.add(key)
        appended.append(payload)
    if not appended:
        return evaluation_face_path(root)
    path = evaluation_face_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for payload in appended:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
    return path


def definition_face_rejections_path(root: Path) -> Path:
    """定义面越权写入时留下的 `evaluation.gate_rejected` 事件（`TR-002`；`R1-006`）。"""
    return root / REGISTRY_SUBDIR / "rejections.jsonl"


def write_definition_face(
    *,
    root: Path,
    experiment_id: str,
    cohort_id: str,
    execution_tier: str = TIER_CANONICAL,
    stage: str = "",
    **fields: Any,
) -> None:
    """`FactorDef` 定义面归 F003；F007 任何写入尝试都是越权（`E_CANONICAL_FORBIDDEN`）。

    越权时先原子追加 `evaluation.gate_rejected` 再抛错（`R1-006`），定义面内容零变化。
    """
    append_events(
        definition_face_rejections_path(root),
        (
            build_event(
                experiment_id=experiment_id,
                execution_tier=execution_tier,
                cohort_id=cohort_id,
                from_state=STATE_CREATED,
                to_state=STATE_INCOMPLETE,
                event_type=EVENT_GATE_REJECTED,
                stage=stage,
                reason_code="E_CANONICAL_FORBIDDEN",
                evidence_refs=(f"{REGISTRY_SUBDIR}/definitions",),
            ),
        ),
    )
    raise CapabilityError(
        f"定义面字段 {list(DEFINITION_FACE_FIELDS)} 归 F003，F007 评测面回写不得写入"
    )


def assert_no_lifecycle_fields(summaries: Sequence[Mapping[str, Any]]) -> None:
    """回写载荷不得携带 lifecycle 状态（判定后移 M3/F006）。"""
    for summary in summaries:
        assert_payload_is_dr008(summary)
