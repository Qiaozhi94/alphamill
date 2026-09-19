"""综合报告：只读 canonical 证据的合成（`FR-006`/`AC-007`/`AC-012`；任务 T014）。

**只消费 canonical**：输入是已冻结 cohort、终态登记与 `cohort_verdict.json`；**从不读取 preview**
产物。若只有 preview 产物（cohort 台账不存在），输出**空 canonical 结果**（计数为零、成员为空），
不混入任何 preview 指标（`US-003` 场景 2）。

聚合与三栏输出见 `synthesis_analysis`（五阶段漏斗、失败三维、事实/推断/建议）。漏斗第一级只读
摄取 F003 的 `generation.run_completed`（仅 `status=completed`）与 `generation.candidate_rejected`
（按原因码），拒绝者仍计入分母（`FR-004`）。`synthesis_id` 是语义内容摘要，`generated_at` 是墙钟、
不参与身份——同一 canonical 台账必须确定性重建出同一报告（`SC-004`）。
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation.contract_common import content_digest
from alphamill.evaluation.generation_ingest import ingest_generation_events
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as rs
from alphamill.experiment_store.identity import canonical_json
from alphamill.experiment_store.synthesis_analysis import (
    FailureBucket,
    SynthesisError,
    build_columns,
    empty_funnel,
    empty_stage_funnel,
    failure_buckets,
    generation_funnel,
    stage_funnel,
)

__all__ = [
    "FailureBucket",
    "SynthesisError",
    "SynthesisReport",
    "SCHEMA_VERSION",
    "SYNTHESIS_FILENAME",
    "STATUS_EMPTY",
    "STATUS_FINALIZED",
    "STATUS_OPEN",
    "build_synthesis",
    "compute_synthesis_id",
    "load_synthesis",
    "publish_synthesis",
    "synthesis_dir",
]

SCHEMA_VERSION = 1
SYNTHESIS_SUBDIR = "synthesis"
SYNTHESIS_FILENAME = "synthesis_report.json"
STATUS_EMPTY = "EMPTY"
STATUS_FINALIZED = "FINALIZED"
STATUS_OPEN = "OPEN"


@dataclass(frozen=True)
class SynthesisReport:
    schema_version: int
    synthesis_id: str
    cohort_id: str
    status: str
    funnel: Mapping[str, Any]
    stage_funnel: Mapping[str, Mapping[str, int]]
    failures: tuple[FailureBucket, ...]
    facts: tuple[Mapping[str, Any], ...]
    inferences: tuple[Mapping[str, Any], ...]
    recommendations: tuple[Mapping[str, Any], ...]
    effective_trials: float | None = None
    generated_at: str = field(default="")

    def semantic_payload(self) -> dict[str, Any]:
        """身份输入：不含 `generated_at`（墙钟不参与身份）。"""
        return {
            "schema_version": self.schema_version,
            "cohort_id": self.cohort_id,
            "status": self.status,
            "funnel": dict(self.funnel),
            "stage_funnel": {key: dict(value) for key, value in self.stage_funnel.items()},
            "failures": [bucket.to_payload() for bucket in self.failures],
            "facts": [dict(item) for item in self.facts],
            "inferences": [dict(item) for item in self.inferences],
            "recommendations": [dict(item) for item in self.recommendations],
            "effective_trials": self.effective_trials,
        }

    def to_payload(self) -> dict[str, Any]:
        return {
            "synthesis_id": self.synthesis_id,
            "generated_at": self.generated_at,
            **self.semantic_payload(),
        }


def compute_synthesis_id(payload: Mapping[str, Any]) -> str:
    return content_digest(canonical_json(dict(payload)).encode("utf-8"))


def _member_reports(root: Path, cohort_id: str) -> tuple[tuple[str, dict[str, Any]], ...]:
    """读取终态成员的已发布 report.json（只认 canonical 证据目录）。"""
    reports = []
    for entry in population.registrations(root, cohort_id):
        if not entry.evidence_ref:
            continue
        reference = Path(entry.evidence_ref)
        resolved = reference if reference.is_absolute() else root / reference
        report_path = resolved.parent / "report.json"
        if not report_path.is_file():
            continue
        reports.append((entry.candidate_id, json.loads(report_path.read_text(encoding="utf-8"))))
    return tuple(reports)


def _assemble(
    *,
    cohort_id: str,
    status: str,
    funnel: Mapping[str, Any],
    stage_counts: Mapping[str, Mapping[str, int]],
    failures: tuple[FailureBucket, ...],
    generated_at: str | None,
) -> SynthesisReport:
    facts, inferences, recommendations = build_columns(
        status=status, funnel=funnel, stage_counts=stage_counts, failures=failures
    )
    effective_trials = funnel.get("cohort", {}).get("effective_trials")
    report = SynthesisReport(
        schema_version=SCHEMA_VERSION,
        synthesis_id="",
        cohort_id=cohort_id,
        status=status,
        funnel=funnel,
        stage_funnel=stage_counts,
        failures=failures,
        facts=facts,
        inferences=inferences,
        recommendations=recommendations,
        effective_trials=effective_trials,
        generated_at=generated_at or datetime.now(UTC).isoformat(),
    )
    return replace(report, synthesis_id=compute_synthesis_id(report.semantic_payload()))


def build_synthesis(
    *,
    cohort_id: str,
    generation_events: Iterable[Mapping[str, Any]] = (),
    generated_at: str | None = None,
) -> SynthesisReport:
    """从 canonical 台账重建综合报告；只有 preview 产物时返回空 canonical 结果。"""
    root = rs.reports_root()
    generation = ingest_generation_events(generation_events)
    if not (root / population.COHORTS_SUBDIR / cohort_id).is_dir():
        funnel = empty_funnel()
        funnel["generation"] = generation_funnel(generation)
        return _assemble(
            cohort_id=cohort_id,
            status=STATUS_EMPTY,
            funnel=funnel,
            stage_counts=empty_stage_funnel(),
            failures=(),
            generated_at=generated_at,
        )

    definition = population.load_cohort(root, cohort_id)
    entries = population.registrations(root, cohort_id)
    verdict = population.load_verdict(root, cohort_id)
    reports = _member_reports(root, cohort_id)
    funnel = empty_funnel()
    funnel["generation"] = generation_funnel(generation)
    final_verdicts = {entry.candidate_id: entry.promotion_verdict for entry in entries}
    effective_trials = None
    if verdict is not None:
        statistics = (verdict.get("cohort_statistics") or {}).get("cohort_statistics") or {}
        effective_trials = statistics.get("effective_trials")
        for member in verdict.get("members") or ():
            final_verdicts[str(member["candidate_id"])] = str(member["promotion_verdict"])
    funnel["cohort"] = {
        "trial_count": len(population.commitment_ids(definition)),
        "member_count": len(entries),
        "rejected_count": sum(1 for value in final_verdicts.values() if value == "rejected"),
        "promotion_verdicts": final_verdicts,
        "effective_trials": effective_trials,
    }
    return _assemble(
        cohort_id=cohort_id,
        status=STATUS_FINALIZED if verdict is not None else STATUS_OPEN,
        funnel=funnel,
        stage_counts=stage_funnel(reports),
        failures=failure_buckets(reports),
        generated_at=generated_at,
    )


def synthesis_dir(root: Path, cohort_id: str, synthesis_id: str) -> Path:
    return root / population.COHORTS_SUBDIR / cohort_id / SYNTHESIS_SUBDIR / synthesis_id


def publish_synthesis(report: SynthesisReport, *, root: Path | None = None) -> Path:
    """原子发布；同 synthesis_id 幂等（语义一致即成功，先写者胜）。"""
    base = root or rs.reports_root()
    directory = synthesis_dir(base, report.cohort_id, report.synthesis_id)
    final = directory / SYNTHESIS_FILENAME
    payload = (
        json.dumps(report.to_payload(), ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    ).encode("utf-8")
    if final.is_file():
        existing = json.loads(final.read_text(encoding="utf-8"))
        candidate = report.to_payload()
        for item in (existing, candidate):
            item.pop("generated_at", None)
        if existing != candidate:
            raise SynthesisError(f"同 synthesis_id 语义不一致，拒绝覆盖: {final}")
        return final
    final.parent.mkdir(parents=True, exist_ok=True)
    temp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    temp.write_bytes(payload)
    os.replace(temp, final)
    return final


def load_synthesis(root: Path, cohort_id: str, synthesis_id: str) -> SynthesisReport:
    final = synthesis_dir(root, cohort_id, synthesis_id) / SYNTHESIS_FILENAME
    if not final.is_file():
        raise SynthesisError(f"synthesis 不存在: {final}")
    payload = json.loads(final.read_text(encoding="utf-8"))
    semantic = {
        key: value for key, value in payload.items() if key not in ("synthesis_id", "generated_at")
    }
    if compute_synthesis_id(semantic) != synthesis_id:
        raise SynthesisError(f"synthesis 内容与 ID 不符: {synthesis_id}")
    return SynthesisReport(
        schema_version=payload["schema_version"],
        synthesis_id=synthesis_id,
        cohort_id=payload["cohort_id"],
        status=payload["status"],
        funnel=payload["funnel"],
        stage_funnel=payload["stage_funnel"],
        failures=tuple(
            FailureBucket(
                stage=bucket["stage"],
                owner=bucket["owner"],
                mechanism=bucket["mechanism"],
                count=bucket["count"],
                error_codes=tuple(bucket.get("error_codes", ())),
                evidence_refs=tuple(bucket.get("evidence_refs", ())),
            )
            for bucket in payload["failures"]
        ),
        facts=tuple(payload["facts"]),
        inferences=tuple(payload["inferences"]),
        recommendations=tuple(payload["recommendations"]),
        effective_trials=payload.get("effective_trials"),
        generated_at=payload.get("generated_at", ""),
    )


def assert_no_preview_contamination(report: SynthesisReport) -> None:
    """综合报告不得出现 preview 层级指标（`UX-002`/`US-003` 场景 2）。"""
    if report.status != STATUS_EMPTY and "preview" in canonical_json(report.to_payload()):
        raise SynthesisError("综合报告混入 preview 指标")
