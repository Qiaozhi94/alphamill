"""calendar artifact 契约（F007 `DR-006`；任务 T001）。

universe 与 calendar 是两个**独立** artifact：universe 归 F008 内容寻址台账（F007 只读），
calendar 由本 Feature 拥有——调用方给出 calendar JSON，本模块校验其 v1 schema、规范化后按
内容寻址保存到 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`
（该目录只承载 calendar，universe 不合并进来）。ADR-0007 的 `universe_calendar_digest`
由两者 digest 按冻结公式组合导出（见 `identity.universe_calendar_digest`）。

v1 calendar schema（本 Feature 拥有）：

```json
{"schema_version": 1, "timezone": "UTC",
 "windows": [{"start": "2026-01-01T00:00:00Z", "end": "2026-04-01T00:00:00Z"}]}
```
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from alphamill.experiment_store.errors import SnapshotInputError, SnapshotIntegrityError
from alphamill.experiment_store.identity import canonical_json, content_digest, parse_utc
from alphamill.experiment_store.paths import (
    CALENDAR_SUBDIR,
    SNAPSHOTS_SUBDIR,
    atomic_create,
    calendar_artifact_path,
)

CALENDAR_SCHEMA_VERSION = 1


def validate_calendar(calendar: Any) -> None:
    """校验 v1 calendar schema；任何缺失/越界字段一律 fail-closed。"""
    if not isinstance(calendar, Mapping):
        raise SnapshotInputError("calendar 必须是 JSON object")
    if calendar.get("schema_version") != CALENDAR_SCHEMA_VERSION:
        raise SnapshotInputError(
            f"calendar schema_version 需为 {CALENDAR_SCHEMA_VERSION}，"
            f"收到 {calendar.get('schema_version')!r}"
        )
    if not isinstance(calendar.get("timezone"), str) or not calendar["timezone"]:
        raise SnapshotInputError("calendar.timezone 必须是非空字符串")
    windows = calendar.get("windows")
    if not isinstance(windows, list) or not windows:
        raise SnapshotInputError("calendar.windows 必须是非空数组")
    for index, window in enumerate(windows):
        if not isinstance(window, Mapping):
            raise SnapshotInputError(f"calendar.windows[{index}] 必须是 object")
        start = parse_utc(window.get("start", ""), f"windows[{index}].start")
        end = parse_utc(window.get("end", ""), f"windows[{index}].end")
        if start >= end:
            raise SnapshotInputError(f"calendar.windows[{index}] 区间必须 start < end")


def freeze_calendar(root: Path, calendar: Mapping[str, Any]) -> tuple[str, str]:
    """校验并内容寻址保存 calendar；返回 `(digest, 逻辑 POSIX 路径)`。"""
    validate_calendar(calendar)
    payload = canonical_json(dict(calendar)).encode("utf-8")
    digest = content_digest(payload)
    artifact = calendar_artifact_path(root, digest)
    if artifact.is_file():
        if artifact.read_bytes() != payload:
            raise SnapshotIntegrityError(f"同 digest calendar artifact 内容不一致: {artifact}")
    else:
        atomic_create(artifact, payload)
    logical = f"reports/{SNAPSHOTS_SUBDIR}/{CALENDAR_SUBDIR}/{digest}.json"
    return digest, logical


def calendar_covers(calendar: Mapping[str, Any], moment: datetime) -> bool:
    """moment 是否落在任一 window 的半开区间 `[start, end)` 内。"""
    when = moment.astimezone(UTC)
    return any(
        parse_utc(window["start"], "start") <= when < parse_utc(window["end"], "end")
        for window in calendar["windows"]
    )
