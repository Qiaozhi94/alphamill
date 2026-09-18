"""综合报告的聚合层：五阶段漏斗、失败三维与三栏输出（`AC-012`；任务 T014）。

聚合口径来自 `design.md` §3.3 的冻结枚举：`stage ∈ STAGE_IDS`、`owner ∈ FAILURE_OWNERS`、
`mechanism ∈ FAILURE_MECHANISMS`，出现枚举外取值即失败关闭。三栏输出把**事实**（可核计数与分布）、
**推断**（最大约束与其依据）与**建议**（按 owner 归属的动作）分开，避免把推断当事实读。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.generation_ingest import FunnelFirstLevel
from alphamill.factor_factory.bench.stage_model import (
    FAILURE_MECHANISMS,
    FAILURE_OWNERS,
    STAGE_IDS,
    STAGE_STATUSES,
    FailureRecord,
)


class SynthesisError(ValueError):
    """输入含冻结枚举外的取值，或已发布产物与请求不一致。"""


MECHANISM_OWNER = {
    "missing_input": "data",
    "invalid_input": "data",
    "capability_unguarded": "method",
    "lookahead": "method",
    "estimator_failure": "statistics",
    "publish_failure": "infra",
    "underpowered": "data",
    "cost_negative": "cost",
}
MECHANISM_ACTION = {
    "missing_input": "补齐必需输入后重跑（不要用空值继续）",
    "invalid_input": "修输入引用与摘要一致性后重跑",
    "capability_unguarded": "为该能力登记守卫，或从因子定义中移除",
    "lookahead": "移除未来算子后重跑（L1 fail-closed）",
    "estimator_failure": "修复统计估计器并补回归测试后重跑",
    "publish_failure": "修复发布/磁盘问题后按同一 experiment_id 重试",
    "underpowered": "扩宇宙或延长窗口以提升样本量",
    "cost_negative": "降低成本敏感度（降换手/改执行）或淘汰该信号",
}


@dataclass(frozen=True)
class FailureBucket:
    stage: str
    owner: str
    mechanism: str
    count: int
    error_codes: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.stage not in STAGE_IDS:
            raise SynthesisError(f"失败聚合 stage 未登记: {self.stage!r}")
        if self.owner not in FAILURE_OWNERS:
            raise SynthesisError(f"失败聚合 owner 未登记: {self.owner!r}")
        if self.mechanism not in FAILURE_MECHANISMS:
            raise SynthesisError(f"失败聚合 mechanism 未登记: {self.mechanism!r}")

    def to_payload(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "owner": self.owner,
            "mechanism": self.mechanism,
            "count": self.count,
            "error_codes": list(self.error_codes),
            "evidence_refs": list(self.evidence_refs),
        }


def empty_stage_funnel() -> dict[str, dict[str, int]]:
    return {stage: {status: 0 for status in STAGE_STATUSES} for stage in STAGE_IDS}


def stage_funnel(reports: Iterable[tuple[str, Mapping[str, Any]]]) -> dict[str, dict[str, int]]:
    """五阶段 × 五状态计数；未登记阶段或状态即失败关闭。"""
    funnel = empty_stage_funnel()
    for _candidate, report in reports:
        for entry in report.get("stage_results", ()):
            stage = str(entry.get("stage"))
            status = str(entry.get("status"))
            if stage not in STAGE_IDS:
                raise SynthesisError(f"报告含未登记阶段: {stage!r}")
            if status not in STAGE_STATUSES:
                raise SynthesisError(f"报告含未登记阶段状态: {status!r}")
            funnel[stage][status] += 1
    return funnel


def failure_buckets(
    reports: Iterable[tuple[str, Mapping[str, Any]]],
) -> tuple[FailureBucket, ...]:
    """按 `(stage, owner, mechanism)` 三维聚合，保留 error_code 与证据引用。"""
    aggregated: dict[tuple[str, str, str], dict[str, Any]] = {}
    for _candidate, report in reports:
        for entry in report.get("stage_results", ()):
            for failure in entry.get("failures", ()):
                record = FailureRecord(
                    stage=str(failure["stage"]),
                    owner=str(failure["owner"]),
                    mechanism=str(failure["mechanism"]),
                    error_code=str(failure["error_code"]),
                    first_seen=str(failure["first_seen"]),
                    evidence_refs=tuple(str(ref) for ref in failure.get("evidence_refs", ())),
                )
                key = (record.stage, record.owner, record.mechanism)
                bucket = aggregated.setdefault(
                    key, {"count": 0, "error_codes": set(), "evidence_refs": set()}
                )
                bucket["count"] += 1
                bucket["error_codes"].add(record.error_code)
                bucket["evidence_refs"].update(record.evidence_refs)
    return tuple(
        FailureBucket(
            stage=stage,
            owner=owner,
            mechanism=mechanism,
            count=payload["count"],
            error_codes=tuple(sorted(payload["error_codes"])),
            evidence_refs=tuple(sorted(payload["evidence_refs"])),
        )
        for (stage, owner, mechanism), payload in sorted(aggregated.items())
    )


def empty_funnel() -> dict[str, Any]:
    return {
        "generation": {
            "completed_runs": 0,
            "registered_candidates": 0,
            "rejected_by_reason": {},
            "rejected_total": 0,
            "denominator": 0,
        },
        "cohort": {
            "trial_count": 0,
            "member_count": 0,
            "rejected_count": 0,
            "promotion_verdicts": {},
        },
    }


def generation_funnel(funnel: FunnelFirstLevel) -> dict[str, Any]:
    return {
        "completed_runs": len(funnel.completed_runs),
        "registered_candidates": funnel.registered_candidates,
        "rejected_by_reason": {
            reason: count for reason, count in funnel.rejected_by_reason.items() if count
        },
        "rejected_total": funnel.rejected_total,
        "denominator": funnel.denominator,
    }


def build_columns(
    *,
    status: str,
    funnel: Mapping[str, Any],
    stage_counts: Mapping[str, Mapping[str, int]],
    failures: tuple[FailureBucket, ...],
) -> tuple[tuple[dict[str, Any], ...], tuple[dict[str, Any], ...], tuple[dict[str, Any], ...]]:
    """事实 / 推断 / 建议三栏；推断带 basis，建议带 owner。"""
    facts: list[dict[str, Any]] = [
        {"kind": "cohort_status", "value": status},
        {"kind": "cohort_trials", "value": funnel["cohort"]["trial_count"]},
        {"kind": "cohort_members", "value": funnel["cohort"]["member_count"]},
        {"kind": "cohort_rejected", "value": funnel["cohort"]["rejected_count"]},
        {"kind": "generation_denominator", "value": funnel["generation"]["denominator"]},
    ]
    for stage in STAGE_IDS:
        for stage_status, count in stage_counts[stage].items():
            if count:
                facts.append(
                    {"kind": "stage", "stage": stage, "status": stage_status, "count": count}
                )
    inferences: list[dict[str, Any]] = []
    recommendations: list[dict[str, Any]] = []
    if not failures:
        inferences.append({"constraint": "none", "statement": "未记录结构化失败", "basis": []})
    for bucket in failures:
        inferences.append(
            {
                "constraint": bucket.mechanism,
                "stage": bucket.stage,
                "statement": f"{bucket.stage}/{bucket.mechanism} 共 {bucket.count} 次",
                "basis": list(bucket.error_codes),
            }
        )
        recommendations.append(
            {
                "owner": MECHANISM_OWNER.get(bucket.mechanism, bucket.owner),
                "mechanism": bucket.mechanism,
                "action": MECHANISM_ACTION.get(bucket.mechanism, "人工复核该失败机制"),
            }
        )
    return tuple(facts), tuple(inferences), tuple(recommendations)
