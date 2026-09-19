"""留出预算台账（`DR-005`/`AC-001`；任务 T012）。

`reports/holdout_budget/ledger.jsonl` 是 **append-only** 追加台账：每行一次留出评估，只有
canonical capability 持有 append 句柄；preview/Agent 构造器没有该句柄，越权写入即失败关闭并写
`evaluation.gate_rejected`。台账**不提供** UPDATE/DELETE 路径。

v0.2 边界（`DR-005`）：FactorDef 评测流程不访问最终留出（留出评估属 FR4/M3 的 PortfolioDef 留出
门），因此 v0.2 **没有追加写入者**——台账零行是锁定「不存在旁路写入者」的预期不变量，不是功能
缺失。`holdout_window` 与 `regime` 是为留出门预留的字段。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.evaluation.capabilities import (
    CAP_HOLDOUT_BUDGET_WRITER,
    CapabilityError,
    TierContext,
)
from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    RunEvent,
    append_events,
    build_event,
)
from alphamill.evaluation.run_state import STATE_CREATED, STATE_INCOMPLETE
from alphamill.factor_factory.bench.stage_model import STAGE_COST_CAPACITY

LEDGER_SUBDIR = "holdout_budget"
LEDGER_FILENAME = "ledger.jsonl"
REJECTIONS_FILENAME = "rejections.jsonl"
REQUIRED_FIELDS = (
    "candidate_id",
    "iso_week",
    "experiment_id",
    "cohort_id",
    "verdict",
    "recorded_at",
    "execution_tier",
)
RESERVED_FIELDS = ("holdout_window", "regime")


class HoldoutBudgetError(Exception):
    """台账条目非法或写入被拒。"""


def ledger_path(root: Path) -> Path:
    return root / LEDGER_SUBDIR / LEDGER_FILENAME


def rejections_path(root: Path) -> Path:
    """越权写入留出台账时留下的 `evaluation.gate_rejected` 事件（`TR-002`；`R1-006`）。"""
    return root / LEDGER_SUBDIR / REJECTIONS_FILENAME


@dataclass(frozen=True)
class HoldoutBudgetEntry:
    candidate_id: str
    iso_week: str
    experiment_id: str
    cohort_id: str
    verdict: str
    recorded_at: str
    execution_tier: str = TIER_CANONICAL
    holdout_window: tuple[str, str] | None = None
    regime: str | None = None

    def __post_init__(self) -> None:
        if self.execution_tier != TIER_CANONICAL:
            raise HoldoutBudgetError(f"留出台账只记录 canonical 评估，收到 {self.execution_tier!r}")
        for name in ("candidate_id", "iso_week", "experiment_id", "cohort_id", "verdict"):
            if not getattr(self, name):
                raise HoldoutBudgetError(f"留出台账条目缺 {name}")
        datetime.fromisoformat(self.recorded_at)

    def to_payload(self) -> dict[str, Any]:
        payload = {
            "candidate_id": self.candidate_id,
            "iso_week": self.iso_week,
            "experiment_id": self.experiment_id,
            "cohort_id": self.cohort_id,
            "verdict": self.verdict,
            "recorded_at": self.recorded_at,
            "execution_tier": self.execution_tier,
            "holdout_window": list(self.holdout_window) if self.holdout_window else None,
            "regime": self.regime,
        }
        return payload

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> HoldoutBudgetEntry:
        missing = [name for name in REQUIRED_FIELDS if name not in payload]
        if missing:
            raise HoldoutBudgetError(f"留出台账条目缺字段: {missing}")
        window = payload.get("holdout_window")
        return cls(
            candidate_id=payload["candidate_id"],
            iso_week=payload["iso_week"],
            experiment_id=payload["experiment_id"],
            cohort_id=payload["cohort_id"],
            verdict=payload["verdict"],
            recorded_at=payload["recorded_at"],
            execution_tier=payload["execution_tier"],
            holdout_window=tuple(window) if window else None,
            regime=payload.get("regime"),
        )


def read_ledger(root: Path) -> tuple[HoldoutBudgetEntry, ...]:
    path = ledger_path(root)
    if not path.is_file():
        return ()
    entries = []
    for index, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            entries.append(HoldoutBudgetEntry.from_payload(json.loads(raw)))
        except (json.JSONDecodeError, HoldoutBudgetError) as exc:
            raise HoldoutBudgetError(f"留出台账第 {index} 行非法: {exc}") from exc
    return tuple(entries)


def append_entry(context: TierContext, root: Path, entry: HoldoutBudgetEntry) -> Path:
    """追加一行；调用方必须持有 canonical 的留出预算台账能力，否则 fail-closed。

    越权时**先**原子追加 `evaluation.gate_rejected`（`TR-002`/`R1-006`）再抛错——失败关闭
    必须留下可定位证据，而不是只抛异常；台账本身保持零行（不落任何越权写入）。
    """
    try:
        context.require(CAP_HOLDOUT_BUDGET_WRITER)
    except CapabilityError:
        append_events(
            rejections_path(root),
            (
                rejection_event(
                    experiment_id=entry.experiment_id,
                    cohort_id=entry.cohort_id,
                    execution_tier=context.execution_tier,
                    stage=STAGE_COST_CAPACITY,
                ),
            ),
        )
        raise
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry.to_payload(), ensure_ascii=False, sort_keys=True) + "\n")
    return path


def rejection_event(
    *,
    experiment_id: str,
    cohort_id: str,
    execution_tier: str,
    stage: str,
    reason_code: str = "E_CANONICAL_FORBIDDEN",
) -> RunEvent:
    """越权写入留出台账时留下的拒绝事件（`TR-002`）。"""
    return build_event(
        experiment_id=experiment_id,
        execution_tier=execution_tier,
        cohort_id=cohort_id,
        from_state=STATE_CREATED,
        to_state=STATE_INCOMPLETE,
        event_type=EVENT_GATE_REJECTED,
        stage=stage,
        reason_code=reason_code,
        evidence_refs=(f"holdout_budget/{LEDGER_FILENAME}",),
    )


def iso_week_of(moment: datetime) -> str:
    year, week, _ = moment.astimezone(UTC).isocalendar()
    return f"{year}-W{week:02d}"
