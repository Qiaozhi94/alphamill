"""F008 事件与 trace 的写入口：append-only JSONL、严格构造与幂等去重（`TR-001`/`TR-002`）。

契约与读侧在 `event_store.py`（dataclass、canonical 行解析、严格校验、路径与查询），本模块
只负责**写入**：`build_event()` 严格构造、`event_document()` / `canonical_line()` 序列化、
`append_event()` 幂等去重 + 原子追加。依赖方向单向（`events` → `event_store`），下方 import
同时把读侧公开 API 重新导出，调用方只 import 本模块即可完成写与读。

**落盘布局**：每种事件一个文件，根目录默认 `<repo>/reports/universe/events/`，环境变量
`ALPHAMILL_EVENTS_DIR` 优先（`default_events_dir()` 每次调用读环境变量，测试用 `tmp_path` +
`monkeypatch.setenv` 改道）；文件名即事件类型——`universe.member_changed.jsonl` /
`backfill.progress.jsonl` / `backfill.failed.jsonl`。**只追加**：无删除/改写/截断/重排接口，
一行一个 canonical JSON 对象（键排序、紧凑分隔、UTF-8、无首尾空白、以 `\\n` 结尾，同
`canonical.py` 规则），`elapsed` 归一为 JSON number，行内不得有 NaN/Inf；历史行落盘后不再被
触碰，读取按文件顺序返回全部历史。

**schema_version / 未知字段（fail-closed，不做宽松忽略）**：写入侧严格构造——类型、枚举、非空
字符串、非负计数不符即 `EventsError`，`schema_version` 固定为 `SCHEMA_VERSION`（1），调用方
不可覆写；读取侧要求各类型键集合**逐个精确命中**——缺字段、未知字段、未知事件类型、
`schema_version` 不是整数 1、时间戳不是 canonical UTC `...Z`（如 `+08:00`）、行不是 canonical
JSON、文件末行缺换行，全部判红，没有「跳过不认识的行继续读」的路径。因此**新增字段/事件类型
是破坏性变更**：必须同时改 `event_store.PAYLOAD_FIELDS` 并把 `SCHEMA_VERSION` +1（T014 的
hostname 若要进事件流照此办理；design §4 目前把 hostname 归在 `BackfillRun` 运行记录里）。

**幂等键**（`idempotency_key()`，design §4）：同键重复追加被去重——不报错、不写第二行，
`append_event` 返回 `False`，先写入者为准（append-only 没有 UPDATE 语义，`retries` 变化不产生
新行）。成员事件 `(lake_pair, effective_at, direction, line)`；回填事件 `(run_id, lake_pair,
cursor)`，其中 `backfill.failed` 用该事件的游标字段 `last_cursor`（游标未建立时为 `None`）。
键由**扫描文件**得出（无内存缓存），故跨进程、跨重启同样生效。

**并发与原子性**：追加在 `flock(LOCK_EX)` 临界区内完成——先扫已有键，再以 `O_APPEND` 的
`os.write` 单次写入整行，写入字节数异常则 `ftruncate` 回滚到写入前长度再报错，故并发追加既不
互相截断也不产生半行；读取方无需加锁（整行单次写入 + 行级严格校验），文件永不删除或改名。
不逐行 `fsync`：崩溃最多丢掉未落盘的行尾，不会改写历史行。

**原因码（`TR-001`）**：`line=tradability` 的 `reason` 必须是台账原因（`listed`/`delisted`/
`initial_seed`，与 `membership.REASONS` 同源）；`line=admission` 的 `reason` 是质量门原因码或
`universe_reselect`（原因码集合归质量门 T015 所有，本模块只拒绝空值与台账专用原因码）——两条
线共用一个事件流但必须可区分，不允许互相复用原因。
"""

from __future__ import annotations

import contextlib
import fcntl
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from alphamill.data_bridge.universe.canonical import canonical_json_text
from alphamill.data_bridge.universe.errors import UniverseArtifactError
from alphamill.data_bridge.universe.event_store import (
    CLASSES,
    DIRECTIONS,
    ENV_EVENTS_DIR,
    EVENT_BACKFILL_FAILED,
    EVENT_BACKFILL_PROGRESS,
    EVENT_MEMBER_CHANGED,
    EVENT_TYPES,
    KEY_SETS,
    LINES,
    PAYLOAD_FIELDS,
    SCHEMA_VERSION,
    SUFFIX,
    TIMESTAMP_FIELDS,
    BackfillFailedEvent,
    BackfillProgressEvent,
    Event,
    EventsError,
    MemberChangedEvent,
    default_events_dir,
    event_path,
    parse_line,
    read_events,
    read_lines,
    require_elapsed,
    timestamp_text,
    validate_document,
)

__all__ = [
    "CLASSES",
    "DIRECTIONS",
    "ENV_EVENTS_DIR",
    "EVENT_BACKFILL_FAILED",
    "EVENT_BACKFILL_PROGRESS",
    "EVENT_MEMBER_CHANGED",
    "EVENT_TYPES",
    "KEY_SETS",
    "LINES",
    "PAYLOAD_FIELDS",
    "SCHEMA_VERSION",
    "SUFFIX",
    "BackfillFailedEvent",
    "BackfillProgressEvent",
    "Event",
    "EventsError",
    "MemberChangedEvent",
    "append_event",
    "backfill_failed_event",
    "backfill_progress_event",
    "build_event",
    "canonical_line",
    "default_events_dir",
    "event_document",
    "event_path",
    "idempotency_key",
    "member_changed_event",
    "parse_line",
    "read_events",
]


def idempotency_key(event: Event) -> tuple[Any, ...]:
    """幂等键（design §4）：先写入者为准；未知事件对象类型判红。"""
    if not isinstance(event, (MemberChangedEvent, BackfillProgressEvent, BackfillFailedEvent)):
        raise EventsError(f"未知事件对象类型: {type(event).__name__}")
    return event.idempotency_key()


def build_event(event_type: str, **payload: Any) -> Event:
    """写入侧唯一构造入口：缺字段/未知字段/枚举/类型不符在落盘前判红（`EventsError`）。"""
    recorded_at = payload.pop("recorded_at", None)
    stamp = timestamp_text(datetime.now(UTC) if recorded_at is None else recorded_at, "recorded_at")
    payload.update(event_type=event_type, schema_version=SCHEMA_VERSION, recorded_at=stamp)
    for name in list(payload):
        if name in TIMESTAMP_FIELDS and name != "recorded_at":
            payload[name] = timestamp_text(payload[name], name)
    return validate_document(payload)


def member_changed_event(**payload: Any) -> MemberChangedEvent:
    """`build_event(EVENT_MEMBER_CHANGED, ...)` 的强类型别名。"""
    return cast(MemberChangedEvent, build_event(EVENT_MEMBER_CHANGED, **payload))


def backfill_progress_event(**payload: Any) -> BackfillProgressEvent:
    """`build_event(EVENT_BACKFILL_PROGRESS, ...)` 的强类型别名。"""
    return cast(BackfillProgressEvent, build_event(EVENT_BACKFILL_PROGRESS, **payload))


def backfill_failed_event(**payload: Any) -> BackfillFailedEvent:
    """`build_event(EVENT_BACKFILL_FAILED, ...)` 的强类型别名。"""
    return cast(BackfillFailedEvent, build_event(EVENT_BACKFILL_FAILED, **payload))


def event_document(event: Event) -> dict[str, Any]:
    """事件 → canonical 文档；手搓 dataclass 也在这里被判红（写入前的最后一道校验）。"""
    if not isinstance(event, (MemberChangedEvent, BackfillProgressEvent, BackfillFailedEvent)):
        raise EventsError(f"未知事件对象类型: {type(event).__name__}")
    document: dict[str, Any] = {
        "event_type": event.event_type,
        "schema_version": event.schema_version,
        "recorded_at": timestamp_text(event.recorded_at, "recorded_at"),
    }
    for name in PAYLOAD_FIELDS[event.event_type]:
        value = getattr(event, name)
        if name in TIMESTAMP_FIELDS:
            value = timestamp_text(value, name)
        elif name == "elapsed":
            value = require_elapsed(value, name)
        document[name] = value
    validate_document(document)
    return document


def canonical_line(event: Event) -> str:
    """事件 → canonical JSONL 行（含结尾换行）；非法事件在此判红。"""
    try:
        return canonical_json_text(event_document(event)) + "\n"
    except UniverseArtifactError as exc:
        raise EventsError(f"事件无法规范化为 canonical JSON: {exc}") from exc


def append_event(event: Event, *, events_dir: Path | None = None) -> bool:
    """追加一条事件：`True` = 新写入，`False` = 同幂等键已存在被去重（不报错、不写第二行）。"""
    payload = canonical_line(event).encode("utf-8")
    key = idempotency_key(event)
    path = event_path(event.event_type, events_dir=events_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = os.open(path, os.O_RDWR | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
        # 全量解析（不用 any 短路）：文件里任何一行非法都判红，不因命中同键就跳过校验
        if key in [parse_line(line).idempotency_key() for line in read_lines(path)]:
            return False
        size = os.fstat(handle).st_size
        written = os.write(handle, payload)
        if written != len(payload):
            os.ftruncate(handle, size)
            raise EventsError(f"事件行写入不完整（{written}/{len(payload)} 字节），已回滚: {path}")
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(handle, fcntl.LOCK_UN)
        os.close(handle)
    return True
