"""ResearchSnapshot 身份：规范化编码、内容 ID 与两级摘要组合（ADR-0007；F007 `DR-001`）。

这是身份规则的**唯一实现点**，`snapshot_id` 只哈希语义字段：

```text
snapshot_id = sha256(canonical_json({
  schema_version, cutoff_time,
  members: [<按 dataset 名排序的成员六元组>],
  symbol_map_digest, universe_calendar_digest,
}))
```

创建时间、路径、Parquet codec、文件 SHA 与主机只进 `provenance`；相同语义必须得到相同 ID
（`NFR-002`/`SC-003`）。`universe_calendar_digest` 由 universe 与 calendar 两个独立 artifact 的
digest 按 ADR-0007 冻结公式组合导出，不回退为「单一 JSON 文件摘要」（`DR-006`）。

任务 T004 在同一模块上追加 `ExperimentContext` 的规范化与两级内容 ID。
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge.digest import DIGEST_PREFIX, canonical_json_text
from alphamill.experiment_store.errors import SnapshotInputError, SnapshotIntegrityError

SCHEMA_VERSION = 1
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MEMBER_FIELDS = (
    "data_version",
    "value_digest",
    "as_of_fidelity",
    "event_time_min",
    "event_time_max",
)


def canonical_json(value: Any) -> str:
    """规范化 JSON 文本：键排序、无空白、非 ASCII 原样（与 F002 jsonb 编码同一规则）。"""
    return canonical_json_text(value, parse_text=False)


def content_digest(payload: bytes) -> str:
    return DIGEST_PREFIX + hashlib.sha256(payload).hexdigest()


def parse_utc(value: Any, field: str) -> datetime:
    """ISO-8601 字符串/datetime → aware UTC；无时区视为 UTC，非法即 `SnapshotInputError`。"""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value:
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise SnapshotInputError(f"{field} 不是合法 ISO-8601 时间: {value!r}") from exc
    else:
        raise SnapshotInputError(f"{field} 必须是 ISO-8601 字符串或 datetime")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def universe_calendar_digest(universe_digest: str, calendar_digest: str) -> str:
    """ADR-0007 冻结的组合公式；两个 digest 必须是合法内容摘要。"""
    for name, value in (("universe", universe_digest), ("calendar", calendar_digest)):
        if not isinstance(value, str) or not DIGEST_RE.fullmatch(value):
            raise SnapshotInputError(f"{name} digest 缺失或格式非法: {value!r}")
    payload = canonical_json({"universe": universe_digest, "calendar": calendar_digest})
    return content_digest(payload.encode("utf-8"))


@dataclass(frozen=True)
class SnapshotMember:
    """单个 dataset 的不可变成员引用（ADR-0007 决策 2）。"""

    dataset: str
    data_version: str
    value_digest: str
    as_of_fidelity: str
    event_time_min: str
    event_time_max: str

    def to_dict(self) -> dict[str, str]:
        return {"dataset": self.dataset, **{f: getattr(self, f) for f in MEMBER_FIELDS}}

    @classmethod
    def from_dict(cls, dataset: str, payload: Mapping[str, Any]) -> SnapshotMember:
        missing = [f for f in MEMBER_FIELDS if not isinstance(payload.get(f), str)]
        if missing:
            raise SnapshotIntegrityError(f"成员 {dataset} 缺少字段: {missing}")
        return cls(dataset=dataset, **{f: str(payload[f]) for f in MEMBER_FIELDS})


def members_payload(members: Mapping[str, SnapshotMember]) -> list[dict[str, str]]:
    """按 dataset 名排序的规范成员列表——身份排序键。"""
    return [members[name].to_dict() for name in sorted(members)]


def compute_snapshot_id(
    *,
    schema_version: int,
    cutoff_time: str,
    members: Mapping[str, SnapshotMember],
    symbol_map_digest: str,
    combined_digest: str,
) -> str:
    payload = {
        "schema_version": schema_version,
        "cutoff_time": cutoff_time,
        "members": members_payload(members),
        "symbol_map_digest": symbol_map_digest,
        "universe_calendar_digest": combined_digest,
    }
    return content_digest(canonical_json(payload).encode("utf-8"))


@dataclass(frozen=True)
class ResearchSnapshot:
    schema_version: int
    snapshot_id: str
    cutoff_time: str
    members: Mapping[str, SnapshotMember]
    symbol_map_digest: str
    universe_digest: str
    calendar_digest: str
    universe_calendar_digest: str
    provenance: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "snapshot_id": self.snapshot_id,
            "cutoff_time": self.cutoff_time,
            "members": {name: self.members[name].to_dict() for name in sorted(self.members)},
            "symbol_map_digest": self.symbol_map_digest,
            "universe_digest": self.universe_digest,
            "calendar_digest": self.calendar_digest,
            "universe_calendar_digest": self.universe_calendar_digest,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> ResearchSnapshot:
        if payload.get("schema_version") != SCHEMA_VERSION:
            raise SnapshotIntegrityError(
                f"不支持的 snapshot schema_version: {payload.get('schema_version')!r}"
            )
        raw_members = payload.get("members")
        if not isinstance(raw_members, Mapping) or not raw_members:
            raise SnapshotIntegrityError("snapshot members 缺失或为空")
        members = {
            str(name): SnapshotMember.from_dict(str(name), body)
            for name, body in raw_members.items()
            if isinstance(body, Mapping)
        }
        if len(members) != len(raw_members):
            raise SnapshotIntegrityError("snapshot members 含非 object 条目")
        return cls(
            schema_version=SCHEMA_VERSION,
            snapshot_id=str(payload.get("snapshot_id", "")),
            cutoff_time=str(payload.get("cutoff_time", "")),
            members=members,
            symbol_map_digest=str(payload.get("symbol_map_digest", "")),
            universe_digest=str(payload.get("universe_digest", "")),
            calendar_digest=str(payload.get("calendar_digest", "")),
            universe_calendar_digest=str(payload.get("universe_calendar_digest", "")),
            provenance=payload.get("provenance") or {},
        )
