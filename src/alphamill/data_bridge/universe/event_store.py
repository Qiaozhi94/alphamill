"""F008 事件流的契约与读侧：强类型 schema、严格校验、路径解析与按条件查询。

写入口在 `events.py`（构造、幂等去重、`flock` 原子追加）；本模块承载**读侧与契约**——事件
dataclass、canonical JSONL 行解析、键集合/`schema_version`/枚举的严格校验、事件文件路径与
查询。依赖方向单向：`events` → `event_store`，本模块不 import `events`。

fail-closed（策略全文见 `events.py` docstring）：缺字段、未知字段、未知事件类型、
`schema_version` 不是整数 1、时间戳不是 canonical UTC `...Z`、行不是 canonical JSON、文件末行
缺换行——一律抛 `EventsError`，没有任何「跳行继续读」的宽松路径。
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Final

from alphamill.data_bridge import paths
from alphamill.data_bridge.universe.canonical import canonical_json_text, parse_utc, utc_iso
from alphamill.data_bridge.universe.errors import UniverseArtifactError, UniverseError
from alphamill.data_bridge.universe.membership import REASONS as TRADABILITY_REASONS

SCHEMA_VERSION: Final[int] = 1
EVENT_MEMBER_CHANGED: Final[str] = "universe.member_changed"
EVENT_BACKFILL_PROGRESS: Final[str] = "backfill.progress"
EVENT_BACKFILL_FAILED: Final[str] = "backfill.failed"
EVENT_TYPES: Final[tuple[str, ...]] = (
    EVENT_MEMBER_CHANGED,
    EVENT_BACKFILL_PROGRESS,
    EVENT_BACKFILL_FAILED,
)
DIRECTIONS: Final[tuple[str, ...]] = ("in", "out")
LINES: Final[tuple[str, ...]] = ("tradability", "admission")
SUFFIX: Final[str] = ".jsonl"
ENV_EVENTS_DIR: Final[str] = "ALPHAMILL_EVENTS_DIR"
_COMMON_FIELDS: Final[tuple[str, ...]] = ("event_type", "schema_version", "recorded_at")
PAYLOAD_FIELDS: Final[dict[str, tuple[str, ...]]] = {
    EVENT_MEMBER_CHANGED: (
        "lake_pair",
        "direction",
        "effective_at",
        "reason",
        "universe_id",
        "line",
    ),
    EVENT_BACKFILL_PROGRESS: ("run_id", "lake_pair", "rows", "cursor", "elapsed"),
    EVENT_BACKFILL_FAILED: ("run_id", "lake_pair", "error_class", "retries", "last_cursor"),
}
KEY_SETS: Final[dict[str, frozenset[str]]] = {
    kind: frozenset(_COMMON_FIELDS + fields) for kind, fields in PAYLOAD_FIELDS.items()
}
TIMESTAMP_FIELDS: Final[frozenset[str]] = frozenset({"recorded_at", "effective_at"})
_MEMBER_REASONS: Final[frozenset[str]] = frozenset(TRADABILITY_REASONS)


class EventsError(UniverseError):
    """事件行非法、版本/键集合/枚举不符，或过滤条件与事件类型不匹配。"""

    code = "E_UNIVERSE_EVENTS"


@dataclass(frozen=True, slots=True, kw_only=True)
class MemberChangedEvent:
    """成员进出：`line=tradability` 记台账可交易期，`line=admission` 记准入状态（`TR-001`）。"""

    event_type: ClassVar[str] = EVENT_MEMBER_CHANGED
    lake_pair: str
    direction: str
    effective_at: datetime
    reason: str
    universe_id: str
    line: str
    recorded_at: datetime
    schema_version: int = SCHEMA_VERSION

    def idempotency_key(self) -> tuple[str, str, str, str]:
        return (self.lake_pair, utc_iso(self.effective_at), self.direction, self.line)


@dataclass(frozen=True, slots=True, kw_only=True)
class BackfillProgressEvent:
    """回填进度：`cursor` 是该 pair 的续跑断点（`TR-002`）。"""

    event_type: ClassVar[str] = EVENT_BACKFILL_PROGRESS
    run_id: str
    lake_pair: str
    rows: int
    cursor: str
    elapsed: float
    recorded_at: datetime
    schema_version: int = SCHEMA_VERSION

    def idempotency_key(self) -> tuple[str, str, str]:
        return (self.run_id, self.lake_pair, self.cursor)


@dataclass(frozen=True, slots=True, kw_only=True)
class BackfillFailedEvent:
    """回填失败：保留 `last_cursor` 供单独重跑，不因失败提速（`TR-002`）。"""

    event_type: ClassVar[str] = EVENT_BACKFILL_FAILED
    run_id: str
    lake_pair: str
    error_class: str
    retries: int
    last_cursor: str | None
    recorded_at: datetime
    schema_version: int = SCHEMA_VERSION

    def idempotency_key(self) -> tuple[str, str, str | None]:
        return (self.run_id, self.lake_pair, self.last_cursor)


Event = MemberChangedEvent | BackfillProgressEvent | BackfillFailedEvent

CLASSES: Final[dict[str, type[Any]]] = {
    EVENT_MEMBER_CHANGED: MemberChangedEvent,
    EVENT_BACKFILL_PROGRESS: BackfillProgressEvent,
    EVENT_BACKFILL_FAILED: BackfillFailedEvent,
}
_TEXT_FIELDS: Final[frozenset[str]] = frozenset(
    {"lake_pair", "run_id", "cursor", "error_class", "universe_id"}
)
_INT_FIELDS: Final[frozenset[str]] = frozenset({"rows", "retries"})
_ENUM_FIELDS: Final[dict[str, tuple[str, ...]]] = {"direction": DIRECTIONS, "line": LINES}


def default_events_dir() -> Path:
    """事件根目录：`ALPHAMILL_EVENTS_DIR` 优先，否则 `<repo>/reports/universe/events/`。"""
    override = os.getenv(ENV_EVENTS_DIR, "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (paths.REPO_ROOT / "reports" / "universe" / "events").resolve()


def event_path(event_type: str, *, events_dir: Path | None = None) -> Path:
    """事件文件路径 `<root>/<event_type>.jsonl`；显式目录 > 环境变量 > 默认根。"""
    if event_type not in CLASSES:
        raise EventsError(f"未知事件类型: {event_type!r}（已知：{', '.join(EVENT_TYPES)}）")
    root = default_events_dir() if events_dir is None else Path(events_dir).expanduser().resolve()
    return root / f"{event_type}{SUFFIX}"


def require_text(value: Any, field: str) -> str:
    """无首尾空白与控制字符的非空字符串。"""
    if not isinstance(value, str) or not value or value != value.strip():
        raise EventsError(f"{field} 必须是无首尾空白的非空字符串: {value!r}")
    if any(char < " " or char == "\x7f" for char in value):
        raise EventsError(f"{field} 不得含控制字符: {value!r}")
    return value


def require_choice(value: Any, allowed: tuple[str, ...], field: str) -> str:
    text = require_text(value, field)
    if text not in allowed:
        raise EventsError(f"{field} 必须是 {allowed} 之一: {text!r}")
    return text


def require_count(value: Any, field: str) -> int:
    """非负整数（bool 不算整数）。"""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise EventsError(f"{field} 必须是非负整数: {value!r}")
    return value


def require_elapsed(value: Any, field: str) -> float:
    """非负有限数值（秒）；bool / NaN / Inf / 负数 / 非数值判红。"""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EventsError(f"{field} 必须是非负有限数值（秒）: {value!r}")
    try:
        number = float(value)
    except OverflowError as exc:
        raise EventsError(f"{field} 超出可表示范围: {value!r}") from exc
    if not math.isfinite(number) or number < 0:
        raise EventsError(f"{field} 必须是非负有限数值（秒）: {value!r}")
    return number


def _utc_text(value: datetime, field: str) -> str:
    try:
        return utc_iso(value)
    except UniverseArtifactError as exc:
        raise EventsError(f"{field}: {exc}") from exc


def parse_timestamp(value: Any, field: str) -> datetime:
    """canonical UTC ISO-8601 文本（`...Z`）→ aware datetime；偏移写法判红。"""
    if not isinstance(value, str):
        raise EventsError(f"{field} 必须是 ISO-8601 字符串: {value!r}")
    try:
        parsed = parse_utc(value, field=field)
    except UniverseArtifactError as exc:
        raise EventsError(str(exc)) from exc
    if _utc_text(parsed, field) != value:
        raise EventsError(f"{field} 不是 canonical UTC ISO-8601: {value!r}")
    return parsed


def timestamp_text(value: Any, field: str) -> str:
    """写入侧：带时区 `datetime` 或 ISO-8601 字符串 → canonical UTC `...Z` 文本。"""
    if isinstance(value, datetime):
        return _utc_text(value, field)
    return _utc_text(parse_timestamp(value, field), field)


def require_reason(value: Any, line: str) -> str:
    """`tradability` 只认台账原因码；`admission` 只认质量门原因码/`universe_reselect`。"""
    reason = require_text(value, "reason")
    if line == "tradability":
        if reason not in _MEMBER_REASONS:
            raise EventsError(
                f"tradability 的 reason 必须是 {sorted(_MEMBER_REASONS)} 之一: {reason!r}"
            )
        return reason
    if reason in _MEMBER_REASONS:
        raise EventsError(
            f"admission 的 reason 不得复用台账原因 {reason!r}"
            "（应为质量门原因码或 universe_reselect）"
        )
    return reason


def field_value(name: str, value: Any, line: str | None) -> Any:
    """按字段名分派的严格校验；未知字段名直接判红，不做宽松传递。"""
    if name in _TEXT_FIELDS:
        return require_text(value, name)
    if name in _INT_FIELDS:
        return require_count(value, name)
    if name in _ENUM_FIELDS:
        return require_choice(value, _ENUM_FIELDS[name], name)
    if name in TIMESTAMP_FIELDS:
        return parse_timestamp(value, name)
    if name == "elapsed":
        return require_elapsed(value, name)
    if name == "reason":
        return require_reason(value, line or "")
    if name == "last_cursor":
        return None if value is None else require_text(value, "last_cursor")
    raise EventsError(f"未知字段: {name}")


def validate_document(document: Any) -> Event:
    """已解析文档 → 强类型事件；键集合、版本、类型、枚举任一不符即 `EventsError`。"""
    if not isinstance(document, dict):
        raise EventsError("事件行顶层必须是 JSON object")
    kind = document.get("event_type")
    if kind not in CLASSES:
        raise EventsError(f"未知事件类型: {kind!r}（已知：{', '.join(EVENT_TYPES)}）")
    keyset = KEY_SETS[kind]
    unknown, missing = sorted(set(document) - keyset), sorted(keyset - set(document))
    if unknown or missing:
        raise EventsError(f"{kind} 键集合非法: missing={missing}, unknown={unknown}")
    version = document["schema_version"]
    if isinstance(version, bool) or not isinstance(version, int) or version != SCHEMA_VERSION:
        raise EventsError(f"{kind} schema_version 必须是整数 {SCHEMA_VERSION}: {version!r}")
    line = require_choice(document["line"], LINES, "line") if kind == EVENT_MEMBER_CHANGED else None
    fields: dict[str, Any] = {
        "recorded_at": parse_timestamp(document["recorded_at"], "recorded_at"),
        "schema_version": version,
    }
    if line is not None:
        fields["line"] = line
    fields.update((name, field_value(name, document[name], line)) for name in PAYLOAD_FIELDS[kind])
    return CLASSES[kind](**fields)


def parse_line(text: str) -> Event:
    """严格解析一行 canonical JSONL：键集合/版本/类型/枚举/canonical 形式任一不符即判红。"""
    body = text[:-1] if isinstance(text, str) and text.endswith("\n") else text
    if not isinstance(body, str) or not body or body != body.strip() or "\n" in body:
        raise EventsError(f"事件行必须是单行且无首尾空白的 JSON: {text!r}")
    try:
        document = json.loads(body)
    except json.JSONDecodeError as exc:
        raise EventsError(f"事件行不是合法 JSON: {body!r}") from exc
    event = validate_document(document)
    try:
        canonical = canonical_json_text(document)
    except UniverseArtifactError as exc:  # pragma: no cover - 校验已限定取值
        raise EventsError(f"事件无法规范化为 canonical JSON: {exc}") from exc
    if canonical != body:
        raise EventsError(f"事件行不是 canonical JSON（键排序/紧凑分隔/无多余空白）: {body!r}")
    return event


def read_lines(path: Path) -> tuple[str, ...]:
    """整文件行视图；文件不存在或为空返回空元组，非 UTF-8/缺行尾换行判红。"""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ()
    except (OSError, UnicodeDecodeError) as exc:
        raise EventsError(f"事件文件不可读或不是 UTF-8: {path}: {exc}") from exc
    if not text:
        return ()
    if not text.endswith("\n"):
        raise EventsError(f"事件文件最后一行未以换行结尾（canonical JSONL 要求）: {path}")
    return tuple(text[:-1].split("\n"))


def read_events(
    event_type: str,
    *,
    run_id: str | None = None,
    lake_pair: str | None = None,
    line: str | None = None,
    events_dir: Path | None = None,
) -> tuple[Event, ...]:
    """按事件类型 + 过滤条件读取（文件顺序 = 追加顺序）；文件不存在返回空元组。

    `run_id` / `lake_pair` / `line` 只在该类型确有该字段时可用：给了不存在的过滤条件判红，
    不做「静默忽略、返回全部」的宽松处理。
    """
    path = event_path(event_type, events_dir=events_dir)
    fields = PAYLOAD_FIELDS[event_type]
    filters = {"run_id": run_id, "lake_pair": lake_pair, "line": line}
    for name, value in filters.items():
        if value is None:
            continue
        if name not in fields:
            raise EventsError(f"{event_type} 没有 {name} 字段，不能按 {name} 过滤")
        field_value(name, value, value if name == "line" else None)
    events: list[Event] = []
    for text in read_lines(path):
        event = parse_line(text)
        if event.event_type != event_type:
            raise EventsError(f"{path.name} 中出现 {event.event_type} 事件行（文件与类型不符）")
        matched = all(
            getattr(event, name) == value for name, value in filters.items() if value is not None
        )
        if matched:
            events.append(event)
    return tuple(events)
