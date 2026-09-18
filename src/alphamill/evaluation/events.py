"""运行事件契约（`TR-001`/`TR-002`/`TR-003`；任务 T011）。

事件类型冻结为三类：`evaluation.run_state_changed`（运行状态迁移）、`evaluation.gate_rejected`
（越权/方法论/必需指标拒绝）、`evaluation.registered`（canonical population 登记，以 `experiment_id`
为幂等键）。

`event_id` 由「类型 + experiment ID + 状态迁移序号 + payload digest」导出（design §4）：重复登记
同一事件是**幂等成功**，同一 ID 不同 payload 是**完整性错误**。`events.jsonl` 只追加，不更新、
不删除。
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from alphamill.evaluation.contract_common import (
    EXECUTION_TIERS,
    content_digest,
)
from alphamill.evaluation.run_state import RUN_STATES

SCHEMA_VERSION = 1
EVENT_RUN_STATE_CHANGED = "evaluation.run_state_changed"
EVENT_GATE_REJECTED = "evaluation.gate_rejected"
EVENT_REGISTERED = "evaluation.registered"
EVENT_TYPES = (EVENT_RUN_STATE_CHANGED, EVENT_GATE_REJECTED, EVENT_REGISTERED)
EVENTS_FILENAME = "events.jsonl"


class EventError(Exception):
    """事件未登记、payload 与已存 ID 冲突或文件损坏。"""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass(frozen=True)
class RunEvent:
    schema_version: int
    event_id: str
    type: str
    experiment_id: str
    execution_tier: str
    cohort_id: str
    stage: str
    from_state: str
    to_state: str
    reason_code: str | None = None
    evidence_refs: tuple[str, ...] = ()
    sequence: int = field(default=0)

    def __post_init__(self) -> None:
        if self.type not in EVENT_TYPES:
            raise EventError(f"未登记的事件类型: {self.type!r}（合法: {list(EVENT_TYPES)}）")
        if self.execution_tier not in EXECUTION_TIERS:
            raise EventError(f"未登记的执行层级: {self.execution_tier!r}")
        if self.from_state not in RUN_STATES or self.to_state not in RUN_STATES:
            raise EventError(f"未登记的运行状态: {self.from_state!r} -> {self.to_state!r}")
        if self.schema_version != SCHEMA_VERSION:
            raise EventError(f"不支持的事件 schema_version: {self.schema_version!r}")

    @property
    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "type": self.type,
            "experiment_id": self.experiment_id,
            "execution_tier": self.execution_tier,
            "cohort_id": self.cohort_id,
            "stage": self.stage,
            "from": self.from_state,
            "to": self.to_state,
            "reason_code": self.reason_code,
            "evidence_refs": list(self.evidence_refs),
        }

    def to_payload(self) -> dict[str, Any]:
        return {"event_id": self.event_id, "sequence": self.sequence, **self.payload}

    def payload_digest(self) -> str:
        return content_digest(_canonical(self.payload).encode("utf-8"))


def derive_event_id(event_payload: Mapping[str, Any], sequence: int) -> str:
    material = {
        "type": event_payload["type"],
        "experiment_id": event_payload["experiment_id"],
        "sequence": sequence,
        "payload_digest": content_digest(_canonical(dict(event_payload)).encode("utf-8")),
    }
    return content_digest(_canonical(material).encode("utf-8"))


def build_event(
    *,
    experiment_id: str,
    execution_tier: str,
    cohort_id: str,
    from_state: str,
    to_state: str,
    event_type: str = EVENT_RUN_STATE_CHANGED,
    stage: str = "",
    reason_code: str | None = None,
    evidence_refs: Iterable[str] = (),
    sequence: int = 0,
) -> RunEvent:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "type": event_type,
        "experiment_id": experiment_id,
        "execution_tier": execution_tier,
        "cohort_id": cohort_id,
        "stage": stage,
        "from": from_state,
        "to": to_state,
        "reason_code": reason_code,
        "evidence_refs": list(evidence_refs),
    }
    event_id = derive_event_id(payload, sequence)
    return RunEvent(
        schema_version=SCHEMA_VERSION,
        event_id=event_id,
        type=event_type,
        experiment_id=experiment_id,
        execution_tier=execution_tier,
        cohort_id=cohort_id,
        stage=stage,
        from_state=from_state,
        to_state=to_state,
        reason_code=reason_code,
        evidence_refs=tuple(evidence_refs),
        sequence=sequence,
    )


def read_events(path: Path) -> tuple[RunEvent, ...]:
    if not path.is_file():
        return ()
    events = []
    for index, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise EventError(f"events.jsonl 第 {index} 行不是合法 JSON: {exc}") from exc
        events.append(
            RunEvent(
                schema_version=payload["schema_version"],
                event_id=payload["event_id"],
                type=payload["type"],
                experiment_id=payload["experiment_id"],
                execution_tier=payload["execution_tier"],
                cohort_id=payload["cohort_id"],
                stage=payload["stage"],
                from_state=payload["from"],
                to_state=payload["to"],
                reason_code=payload.get("reason_code"),
                evidence_refs=tuple(payload.get("evidence_refs", ())),
                sequence=payload.get("sequence", 0),
            )
        )
    return tuple(events)


def append_events(path: Path, events: Iterable[RunEvent]) -> tuple[RunEvent, ...]:
    """追加事件；同 ID 同 payload 幂等忽略，同 ID 不同 payload 抛完整性错误。"""
    existing = read_events(path)
    known = {event.event_id: event.payload_digest() for event in existing}
    appended = list(existing)
    for event in events:
        if event.event_id in known:
            if known[event.event_id] != event.payload_digest():
                raise EventError(f"事件 {event.event_id} 已存在但 payload 不同（完整性错误）")
            continue
        known[event.event_id] = event.payload_digest()
        appended.append(event)
    if appended != list(existing):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for event in appended[len(existing) :]:
                handle.write(_canonical(event.to_payload()) + "\n")
    return tuple(appended)


def query_events(
    events: Iterable[RunEvent],
    *,
    cohort_id: str | None = None,
    object_id: str | None = None,
    stage: str | None = None,
    experiment_id: str | None = None,
    event_type: str | None = None,
) -> tuple[RunEvent, ...]:
    """按 cohort/object/stage/experiment/类型查询（`TR-002`）。"""
    selected = []
    for event in events:
        if cohort_id is not None and event.cohort_id != cohort_id:
            continue
        if experiment_id is not None and event.experiment_id != experiment_id:
            continue
        if stage is not None and event.stage != stage:
            continue
        if event_type is not None and event.type != event_type:
            continue
        if object_id is not None and object_id not in event.evidence_refs:
            continue
        selected.append(event)
    return tuple(selected)


def events_digest(events: Iterable[RunEvent]) -> str:
    """事件批次的内容摘要（写入 manifest，供恢复时比对）。"""
    hasher = hashlib.sha256()
    for event in events:
        hasher.update(event.event_id.encode("utf-8"))
    return "sha256:" + hasher.hexdigest()
