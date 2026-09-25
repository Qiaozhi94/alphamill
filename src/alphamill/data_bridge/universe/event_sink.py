"""F008 事件写入的生产接线：严格载荷形状 + sink 工厂 + 成员变更写入口（T013/T017）。

契约与读写原语在 `event_store.py` / `events.py`（冻结，只许消费）：事件键集合由
`event_store.PAYLOAD_FIELDS` 逐个精确命中，未知或缺失键一律 `EventsError`。本模块是
**唯一**把运行态数据翻译成该形状的地方——形状散落在编排与准入两处必然漂移：

- `backfill_event()`：逐 pair 结果 → `(事件类型, 载荷)`，字段严格等于契约（`elapsed`
  取 run 起点到现在的秒数，`retries` 取真实尝试次数减首次）；
- `backfill_sink()`：`(kind, payload) -> None` 的 sink 工厂，按 kind 分派到
  `backfill_progress_event` / `backfill_failed_event` 后 `append_event()` 原子追加；
- `emit_member_changed()`：`universe.member_changed` 的直接写入口（准入的台账线与判定线）。

`events_dir=None` 时每次调用解析 `ALPHAMILL_EVENTS_DIR` / 默认根（`default_events_dir()`），
测试改环境变量或传显式目录即可改道。**不吞异常**（门禁不降级）：构造或追加失败
（`EventsError` / `OSError`）一律向上抛，让 `backfill` / `gate` 以非零退出暴露，
而不是「跑完一行证据都没有」的静默降级。
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

from alphamill.data_bridge.universe import events
from alphamill.data_bridge.universe.canonical import parse_utc
from alphamill.data_bridge.universe.event_store import EventsError

#: 回填事件出口：`(事件类型, 严格载荷)`；实现方负责构造与落盘。
EventSink = Callable[[str, dict[str, Any]], None]

__all__ = ["EventSink", "backfill_event", "backfill_sink", "emit_member_changed"]

_BUILDERS: Final[dict[str, Callable[..., events.Event]]] = {
    events.EVENT_BACKFILL_PROGRESS: events.backfill_progress_event,
    events.EVENT_BACKFILL_FAILED: events.backfill_failed_event,
}


def backfill_event(
    *, run_id: str, started_at: str, payload: dict[str, Any], failed: bool
) -> tuple[str, dict[str, Any]]:
    """逐 pair 结果 → `(事件类型, 载荷)`；载荷键集合逐个精确命中契约（多/少一个都判红）。"""
    if failed:
        return (
            events.EVENT_BACKFILL_FAILED,
            {
                "run_id": run_id,
                "lake_pair": payload.get("lake_pair"),
                "error_class": payload.get("error_class"),
                "retries": _attempts(payload) - 1,  # 首次之外的真实重试次数
                "last_cursor": payload.get("last_cursor"),
            },
        )
    elapsed = datetime.now(UTC) - parse_utc(started_at, field="started_at")
    return (
        events.EVENT_BACKFILL_PROGRESS,
        {
            "run_id": run_id,
            "lake_pair": payload.get("lake_pair"),
            "rows": int(payload.get("rows") or 0),
            "cursor": payload.get("last_cursor"),
            # run 起点（续跑时即原始 run 的起点）到现在的秒数；时钟回拨取 0（不得为负）
            "elapsed": max(0.0, elapsed.total_seconds()),
        },
    )


def backfill_sink(events_dir: Path | None = None) -> EventSink:
    """回填事件 sink 工厂：按 kind 分派到严格构造器后原子追加（目录缺省走环境变量/默认根）。"""

    def sink(kind: str, payload: dict[str, Any]) -> None:
        build = _BUILDERS.get(kind)
        if build is None:
            raise EventsError(f"未知回填事件类型: {kind!r}（已知：{sorted(_BUILDERS)}）")
        events.append_event(build(**payload), events_dir=events_dir)

    return sink


def emit_member_changed(
    *,
    lake_pair: str,
    direction: str,
    effective_at: datetime,
    reason: str,
    universe_id: str,
    line: str,
    events_dir: Path | None = None,
) -> bool:
    """写一条 `universe.member_changed`；`True` = 新写入，`False` = 同幂等键已存在被去重。"""
    return events.append_event(
        events.member_changed_event(
            lake_pair=lake_pair,
            direction=direction,
            effective_at=effective_at,
            reason=reason,
            universe_id=universe_id,
            line=line,
        ),
        events_dir=events_dir,
    )


def _attempts(payload: dict[str, Any]) -> int:
    """失败事件必须带真实尝试次数（`SymbolOutcome.attempts`）；缺失/非法即判红，不回落成假 0。"""
    value = payload.get("attempts")
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise EventsError(f"backfill.failed 缺少真实尝试次数 attempts: {value!r}")
    return value
