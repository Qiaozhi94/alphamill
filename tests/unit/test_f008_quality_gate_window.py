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
        if "FROM backfill_progress" in text:
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
