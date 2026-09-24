"""T016 与 `AC-006`：缺失率按 pair 的**实际可得窗口**计算（上线晚不算缺失）。

单元层用「只回放窗口后半段」的假连接证明：同一份数据在错误口径（按全局窗口）下会被判
缺失率超限，在正确口径（按 `max(窗口起点, 真实上市时间)`）下判 ACTIVE。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.data_bridge.universe.errors import QualityGateError
from alphamill.data_bridge.universe.quality_gate import (
    REASON_MISSING_RATIO,
    VERDICT_ACTIVE,
    VERDICT_INCOMPLETE,
    VERDICT_QUARANTINED,
    GateThresholds,
    check_pair,
    effective_window,
    expected_minutes,
)

WINDOW_START = datetime(2024, 9, 10, tzinfo=UTC)
WINDOW_END = datetime(2024, 9, 20, tzinfo=UTC)
LISTED_LATE = datetime(2024, 9, 15, tzinfo=UTC)


class _FakeCursor:
    def __init__(self, conn):
        self._conn = conn
        self._result: tuple = (0,)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql: str, params=()):
        text = " ".join(sql.split())
        if "time_bucket(%s::interval" in text:
            # 桶对齐查询（2026-09-24 新增）：夹具里原样返回起点，两侧计数因此用同一个值
            self._result = (params[1],)
        elif "FROM backfill_progress" in text:
            self._result = (self._conn.backfill_status,)
        elif "min(time), max(time)" in text:
            start, end = params[2], params[3]
            rows = self._conn.rows_between(start, end)
            self._result = (rows, self._conn.first, self._conn.last)
        elif "HAVING count(*) > 1" in text:
            self._result = (0,)
        elif "time_bucket" in text or text.startswith("SELECT count(*) FROM ohlcv_"):
            self._result = (self._conn.aggregate_rows,)
        else:  # pragma: no cover - 未知查询即暴露测试夹具缺口
            raise AssertionError(f"未预期的查询: {text}")

    def fetchone(self):
        return self._result


class _FakeConn:
    """按「数据只从真实上市时间开始」的语义回放行数。"""

    def __init__(self, *, listed_at: datetime, backfill_status: str = "complete") -> None:
        self.listed_at = listed_at
        self.backfill_status = backfill_status
        self.first = listed_at
        self.last = WINDOW_END - timedelta(minutes=1)
        self.aggregate_rows = 0

    def cursor(self):
        return _FakeCursor(self)

    def rows_between(self, start: datetime, end: datetime) -> int:
        begin = max(start, self.listed_at)
        if begin >= end:
            return 0
        return int((end - begin).total_seconds() // 60)


def _check(conn, **overrides):
    params = {
        "exchange": "binance",
        "market_type": "perp",
        "db_symbol": "LATE/USDT",
        "lake_pair": "LATE-USDT-PERP",
        "window_start": WINDOW_START,
        "window_end": WINDOW_END,
    }
    params.update(overrides)
    return check_pair(conn, **params)


def test_effective_window_uses_listing_time() -> None:
    start, end = effective_window(
        window_start=WINDOW_START, window_end=WINDOW_END, listed_at=LISTED_LATE
    )
    assert start == LISTED_LATE
    assert end == WINDOW_END
    assert expected_minutes(start, end) == 5 * 24 * 60


def test_effective_window_keeps_global_start_when_listed_earlier() -> None:
    start, _ = effective_window(
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        listed_at=datetime(2023, 1, 1, tzinfo=UTC),
    )
    assert start == WINDOW_START


def test_effective_window_respects_delisting() -> None:
    delisted = datetime(2024, 9, 12, tzinfo=UTC)
    _start, end = effective_window(
        window_start=WINDOW_START, window_end=WINDOW_END, delisting_end=delisted
    )
    assert end == delisted


def test_late_listed_pair_is_not_flagged_as_missing() -> None:
    """AC-006：晚上线 pair 按实际可得窗口算缺失率 → 不误判。"""
    result = _check(_FakeConn(listed_at=LISTED_LATE), listed_at=LISTED_LATE)
    assert result.verdict == VERDICT_ACTIVE
    assert result.reason_code is None
    assert result.metrics["missing_rows"] == 0
    assert result.metrics["expected_minutes"] == 5 * 24 * 60
    assert result.metrics["window_start"] == "2024-09-15T00:00:00Z"


def test_same_data_under_global_window_would_fail() -> None:
    """反证：不给 listed_at（按全局窗口）时，同一份数据判缺失率超限。"""
    result = _check(_FakeConn(listed_at=LISTED_LATE))
    assert result.verdict == VERDICT_QUARANTINED
    assert result.reason_code == REASON_MISSING_RATIO


def test_incomplete_backfill_is_not_pass() -> None:
    conn = _FakeConn(listed_at=LISTED_LATE, backfill_status="running")
    result = _check(conn, listed_at=LISTED_LATE)
    assert result.verdict == VERDICT_INCOMPLETE
    assert result.reason_code == "backfill_incomplete"


def test_thresholds_reject_out_of_range_values() -> None:
    with pytest.raises(QualityGateError):
        GateThresholds(missing_ratio=1.5)
    with pytest.raises(QualityGateError):
        GateThresholds(missing_ratio=-0.1)
    assert GateThresholds().missing_ratio == 0.01


def test_stricter_threshold_quarantines_small_gap() -> None:
    conn = _FakeConn(listed_at=LISTED_LATE)
    original = conn.rows_between

    def short_by_one(start, end):
        return original(start, end) - 1

    conn.rows_between = short_by_one  # type: ignore[method-assign]
    loose = _check(conn, listed_at=LISTED_LATE, thresholds=GateThresholds(missing_ratio=0.01))
    strict = _check(conn, listed_at=LISTED_LATE, thresholds=GateThresholds(missing_ratio=0.0))
    assert loose.verdict == VERDICT_ACTIVE  # 1/7200 ≈ 0.014% ≤ 1%
    assert strict.verdict == VERDICT_QUARANTINED
    assert strict.reason_code == REASON_MISSING_RATIO


def test_aggregate_check_uses_same_aligned_start_on_both_sides() -> None:
    """回归（2026-09-24）：聚合对账两侧必须同 `exchange + symbol`、同一个「按桶对齐后」的起点。

    DEXE 的 `listed_at=2024-12-24T11:30` 不落在 1h/4h/1d 的桶边界上：基表侧按「桶与窗口
    重叠」计入 11:00 那个不完整桶，聚合侧若按 `bucket >= 11:30` 过滤就会漏掉它 → 该 pair
    恒判 `aggregate_mismatch`（实测 1h/4h/1d 各差 25，恰等于 11:30–12:00 有数据的 symbol 数；
    5m/15m 因 11:30 对齐而全等）。

    `symbol` 过滤是 2026-09-24 检视 R1-003 的修复：作用域必须是**该 pair**（`FR-004`），
    否则跨 pair 相消能放行坏 pair。
    """
    from alphamill.data_bridge.universe import gate_sql

    aligned = datetime(2024, 12, 24, 11, 0, tzinfo=UTC)
    executed: list[tuple[str, tuple | None]] = []

    class _Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def execute(self, sql, params=None):
            executed.append((sql, params))

        def fetchone(self):
            if "time_bucket(%s::interval" in executed[-1][0]:
                return (aligned,)
            return (7,)

    class _Conn:
        def cursor(self):
            return _Cursor()

    out = gate_sql.aggregate_mismatch(
        _Conn(),
        "binance",
        "DEXE/USDT",
        datetime(2024, 12, 24, 11, 30, tzinfo=UTC),
        datetime(2026, 9, 10, 15, 52, tzinfo=UTC),
    )

    counted = [params for _sql, params in executed if params is not None and len(params) == 4]
    assert counted, "应发出聚合侧与基表侧两条计数查询"
    assert all(params[:2] == ("binance", "DEXE/USDT") for params in counted), (
        "两侧必须同 exchange + 同 symbol（作用域＝该 pair）"
    )
    assert all(params[2] == aligned for params in counted), "两侧必须传同一个对齐起点"
    assert list(out) == list(gate_sql.AGGREGATES)
    assert all(item["aligned_start"] == "2024-12-24T11:00:00Z" for item in out.values())
    assert all(item["match"] for item in out.values())


def test_aggregate_check_reports_mismatch_when_counts_differ() -> None:
    """两侧计数不等必须判 `match=False`——否则「对不上」这条检查没有牙。

    原用例的假游标对任何计数查询都回 `(7,)`，两侧恒等 → `match` 断言在任何实现下都真
    （2026-09-24 检视 R1-007）。这里让视图侧与基表侧返回不同计数，断言检查真的能变红。
    """
    from alphamill.data_bridge.universe import gate_sql

    aligned = datetime(2024, 12, 24, 11, 0, tzinfo=UTC)
    executed: list[str] = []

    class _Cursor:
        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def execute(self, sql, params=None):
            executed.append(sql)

        def fetchone(self):
            if "time_bucket(%s::interval" in executed[-1]:
                return (aligned,)
            # 基表侧少一个桶（视图侧 7 行 vs 基表 6 桶）
            return (6,) if "FROM ohlcv_1m" in executed[-1] else (7,)

    class _Conn:
        def cursor(self):
            return _Cursor()

    out = gate_sql.aggregate_mismatch(
        _Conn(),
        "binance",
        "BBB/USDT",
        datetime(2024, 12, 24, 11, 30, tzinfo=UTC),
        datetime(2026, 9, 10, 15, 52, tzinfo=UTC),
    )

    assert out, "应产出各聚合的对账结果"
    assert all(item["rows"] == 7 and item["base_buckets"] == 6 for item in out.values())
    assert not any(item["match"] for item in out.values()), "计数不等必须判不一致"
