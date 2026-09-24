"""检视修复回归：`_emit` 的载荷严格命中冻结事件契约（`TR-001` / `TR-002` / `AC-010`）。

这是「契约漂移」的直接锁：旧实现发 `{run_id, lake_pair, hostname, rows, cursor, status}`
与 `{..., retries: None, error, hostname}`——既有未知键（`hostname`/`status`/`error`）、又缺
`elapsed`，`retries=None` 非法；一旦接上真 sink 即 `EventsError`，而 `on_outcome` 在回填
循环里没有 try，整轮就此中断（exit 2）。这里把 `_emit` 的**实际输出**喂回
`events.build_event(...)`：多一个键、少一个键、`retries=None` 都当场判红。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe import events
from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.event_sink import backfill_sink, emit_member_changed

STARTED_AT = "2026-09-01T00:00:00Z"
CURSOR = "2026-09-01T02:30:00Z"


def _run(started_at: str = STARTED_AT) -> runner.BackfillRun:
    return runner.BackfillRun(
        run_id="abc123-b1-20260901T000000Z",
        universe_id="sha256:" + "a" * 64,
        batch=1,
        window_start=STARTED_AT,
        window_end=CURSOR,
        rate_limit={"max_retries": 3},
        hostname="qiaozhi-lt",
        started_at=started_at,
        pairs=(),
    )


def _emit_payload(payload: dict, *, started_at: str = STARTED_AT) -> tuple[str, dict]:
    captured: list[tuple[str, dict]] = []
    runner._emit(lambda kind, body: captured.append((kind, body)), _run(started_at), payload)
    [item] = captured
    return item


def test_emit_progress_payload_is_accepted_by_contract_builder() -> None:
    """progress 载荷严格等于 `PAYLOAD_FIELDS`（旧实现的 `hostname`/`status` 会在这里判红）。"""
    kind, payload = _emit_payload(
        {"lake_pair": "BTC-USDT", "rows": 150, "last_cursor": CURSOR, "status": "completed"}
    )
    assert kind == events.EVENT_BACKFILL_PROGRESS
    assert set(payload) == set(events.PAYLOAD_FIELDS[kind])
    event = events.build_event(kind, **payload)
    assert (event.run_id, event.lake_pair, event.rows, event.cursor) == (
        "abc123-b1-20260901T000000Z",
        "BTC-USDT",
        150,
        CURSOR,
    )
    assert event.elapsed >= 0.0


def test_emit_progress_elapsed_comes_from_run_started_at() -> None:
    """`elapsed` 是 run 起点到现在的秒数（非 0、非负），不是常量也不是 0 占位。"""
    started = utc_iso(datetime.now(UTC) - timedelta(seconds=30))
    _, payload = _emit_payload(
        {"lake_pair": "BTC-USDT", "rows": 1, "last_cursor": CURSOR, "status": "completed"},
        started_at=started,
    )
    assert isinstance(payload["elapsed"], float)
    assert 25.0 <= payload["elapsed"] <= 120.0

    future = utc_iso(datetime.now(UTC) + timedelta(hours=1))
    _, clamped = _emit_payload(
        {"lake_pair": "BTC-USDT", "rows": 1, "last_cursor": CURSOR, "status": "completed"},
        started_at=future,
    )
    assert clamped["elapsed"] == 0.0  # 时钟回拨也不得产生负数（require_elapsed 判红）


def test_emit_failed_payload_is_accepted_by_contract_builder() -> None:
    """failed 载荷严格等于契约，且 `retries` = 真实尝试次数 − 首次（不是 None / 假 0）。"""
    kind, payload = _emit_payload(
        {
            "lake_pair": "ETH-USDT",
            "rows": 0,
            "last_cursor": CURSOR,
            "status": "failed",
            "error": "boom",
            "error_class": "RateLimitExhaustedError",
            "attempts": 3,
        }
    )
    assert kind == events.EVENT_BACKFILL_FAILED
    assert set(payload) == set(events.PAYLOAD_FIELDS[kind])
    event = events.build_event(kind, **payload)
    assert event.retries == 2
    assert event.error_class == "RateLimitExhaustedError"
    assert event.last_cursor == CURSOR


def test_failed_event_without_real_attempts_is_refused() -> None:
    """取不到真实尝试次数时判红，而不是回落成假 0（TR-002 的 retries 不得失义）。"""
    with pytest.raises(events.EventsError, match="attempts"):
        _emit_payload(
            {"lake_pair": "ETH-USDT", "status": "failed", "error_class": "X", "last_cursor": None}
        )


def test_legacy_payload_shape_is_rejected_by_the_frozen_contract() -> None:
    """变异对照：旧载荷（未知键 / 缺字段 / `retries=None`）在契约层必须判红。"""
    with pytest.raises(events.EventsError, match="unknown"):
        events.build_event(
            events.EVENT_BACKFILL_PROGRESS,
            run_id="r1",
            lake_pair="BTC-USDT",
            hostname="qiaozhi-lt",
            rows=1,
            cursor=CURSOR,
            status="completed",
        )
    with pytest.raises(events.EventsError):
        events.build_event(
            events.EVENT_BACKFILL_FAILED,
            run_id="r1",
            lake_pair="BTC-USDT",
            hostname="qiaozhi-lt",
            error_class="X",
            retries=None,
            last_cursor=None,
            error="boom",
        )


def test_backfill_sink_appends_strict_events_and_dedups(tmp_path: Path) -> None:
    """sink 工厂按 kind 分派到严格构造器：同幂等键去重，未知键判红。"""
    sink = backfill_sink(tmp_path)
    body = {
        "run_id": "r1",
        "lake_pair": "BTC-USDT",
        "rows": 150,
        "cursor": CURSOR,
        "elapsed": 1.5,
    }
    sink(events.EVENT_BACKFILL_PROGRESS, dict(body))
    sink(events.EVENT_BACKFILL_PROGRESS, dict(body))
    [stored] = events.read_events(events.EVENT_BACKFILL_PROGRESS, events_dir=tmp_path)
    assert (stored.rows, stored.cursor, stored.elapsed) == (150, CURSOR, 1.5)
    with pytest.raises(events.EventsError, match="unknown"):
        sink(events.EVENT_BACKFILL_PROGRESS, {**body, "hostname": "qiaozhi-lt"})
    with pytest.raises(events.EventsError, match="未知回填事件类型"):
        sink("backfill.renamed", dict(body))


def test_member_changed_lines_are_distinguishable_in_one_stream(tmp_path: Path) -> None:
    """`TR-001`：同一 pair 同一时刻的台账线与判定线是两个事件（幂等键含 `line`）。"""
    moment = datetime(2026, 9, 1, tzinfo=UTC)
    common = {
        "lake_pair": "BTC-USDT",
        "direction": "in",
        "effective_at": moment,
        "universe_id": "sha256:" + "b" * 64,
        "events_dir": tmp_path,
    }
    assert emit_member_changed(**common, reason="listed", line="tradability") is True
    assert emit_member_changed(**common, reason="ACTIVE", line="admission") is True
    assert emit_member_changed(**common, reason="listed", line="tradability") is False
    tradability = events.read_events(
        events.EVENT_MEMBER_CHANGED, line="tradability", events_dir=tmp_path
    )
    admission = events.read_events(
        events.EVENT_MEMBER_CHANGED, line="admission", events_dir=tmp_path
    )
    assert [item.reason for item in tradability] == ["listed"]
    assert [item.reason for item in admission] == ["ACTIVE"]
