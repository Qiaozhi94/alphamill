"""T015 与 `AC-005`：质量门四类失败 fixture、准入记录与导出准入集合。

真实库上的四类 fixture：缺失率超限、边界未闭合、重复主键（无主键 scratch 表承载，
否则参考表的主键让重复根本构造不出来，只能写成恒真的空转断言）、连续聚合对不上。
全项通过者写 ACTIVE 准入记录并进入导出准入集合；回填未完成判 INCOMPLETE 而不是 PASS。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.data_bridge.universe.errors import QualityGateError
from alphamill.data_bridge.universe.membership import MembershipRow, append_membership
from alphamill.data_bridge.universe.quality_gate import (
    AGGREGATES,
    REASON_AGGREGATE,
    REASON_BOUNDARY,
    REASON_DUPLICATE,
    REASON_INCOMPLETE,
    REASON_MISSING_RATIO,
    VERDICT_ACTIVE,
    VERDICT_INCOMPLETE,
    VERDICT_QUARANTINED,
    admitted_pairs,
    check_pair,
    current_verdicts,
    export_admitted,
    record_verdicts,
)

pytestmark = pytest.mark.integration

WINDOW_START = datetime(2026, 9, 1, 0, 0, tzinfo=UTC)
WINDOW_END = datetime(2026, 9, 1, 10, 0, tzinfo=UTC)  # 600 分钟
UNIVERSE_ID = "sha256:" + "c" * 64
SCRATCH_TABLE = "f008_scratch_ohlcv"


def _insert(conn, symbol: str, minutes: list[int], *, table: str = "ohlcv_1m") -> None:
    with conn.cursor() as cur:
        for minute in minutes:
            cur.execute(
                f"INSERT INTO {table} (time, exchange, symbol, open, high, low, close, volume)"  # noqa: S608
                " VALUES (%s, 'binance', %s, 100, 101, 99, 100, 1)",
                (WINDOW_START + timedelta(minutes=minute), symbol),
            )
    conn.commit()


def _refresh_aggregates(conn) -> None:
    """物化连续聚合（该 Timescale 版本不开启实时聚合，未刷新时视图为空）。"""
    previous = conn.autocommit
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for view in AGGREGATES:
                # 刷新窗口要覆盖每个视图至少两个桶（1d 视图需要 ≥2 天）
                cur.execute(
                    "CALL refresh_continuous_aggregate(%s, %s, %s)",
                    (view, WINDOW_START - timedelta(days=2), WINDOW_END + timedelta(days=2)),
                )
    finally:
        conn.autocommit = previous


def _mark_backfill_complete(conn, symbol: str, *, status: str = "complete") -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO backfill_progress (exchange, symbol, timeframe, target_start, target_end,
                                           next_since, status, rows_upserted)
            VALUES ('binance', %s, '1m', %s, %s, %s, %s, 0)
            """,
            (symbol, WINDOW_START, WINDOW_END, WINDOW_END, status),
        )
    conn.commit()


def _check(conn, symbol: str, *, table: str = "ohlcv_1m", lake_pair: str = "AAA-USDT-PERP"):
    return check_pair(
        conn,
        exchange="binance",
        market_type="perp",
        db_symbol=symbol,
        lake_pair=lake_pair,
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        source_table=table,
    )


def test_fully_passing_pair_becomes_active_and_admitted(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(600)))
    _refresh_aggregates(f008_conn)
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT")
    assert result.verdict == VERDICT_ACTIVE, result.metrics
    assert result.reason_code is None
    assert result.metrics["rows"] == 600
    assert result.metrics["boundary_ok"] is True
    assert all(item["match"] for item in result.metrics["aggregates"].values())

    assert record_verdicts(f008_conn, [result], universe_id=UNIVERSE_ID, hostname="qiaozhi-gp") == 1
    stored = current_verdicts(f008_conn, universe_id=UNIVERSE_ID)
    assert stored["AAA-USDT-PERP"].verdict == VERDICT_ACTIVE
    assert admitted_pairs(f008_conn) == frozenset({"AAA-USDT-PERP"})

    append_membership(
        f008_conn,
        [
            MembershipRow(
                exchange="binance",
                market_type="perp",
                db_symbol="AAA/USDT",
                lake_pair="AAA-USDT-PERP",
                valid_from=WINDOW_START,
                reason="initial_seed",
                universe_id=UNIVERSE_ID,
            )
        ],
    )
    assert export_admitted(f008_conn, WINDOW_START + timedelta(minutes=1)) == frozenset(
        {"AAA-USDT-PERP"}
    )


def test_missing_ratio_fixture_is_quarantined(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(0, 300)))  # 只有一半
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT")
    assert result.verdict == VERDICT_QUARANTINED
    assert result.reason_code == REASON_MISSING_RATIO
    assert result.metrics["missing_ratio"] == 0.5


def test_boundary_fixture_is_quarantined(f008_conn) -> None:
    # 只缺最后一根 K 线：缺失率 0.5% 仍过 1% 阈值，但边界未闭合必须拦下
    _insert(f008_conn, "AAA/USDT", list(range(0, 599)))
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT")
    assert result.verdict == VERDICT_QUARANTINED
    assert result.reason_code == REASON_BOUNDARY
    assert result.metrics["missing_ratio"] < 0.01
    assert result.metrics["boundary_ok"] is False


def test_duplicate_primary_key_fixture_is_quarantined(f008_conn) -> None:
    """重复主键用无主键 scratch 表承载：参考表主键让重复结构性不可发生。"""
    with f008_conn.cursor() as cur:
        cur.execute(
            f"CREATE TABLE {SCRATCH_TABLE} ("
            "time TIMESTAMPTZ NOT NULL, exchange TEXT NOT NULL, symbol TEXT NOT NULL,"
            "open DOUBLE PRECISION, high DOUBLE PRECISION, low DOUBLE PRECISION,"
            "close DOUBLE PRECISION, volume DOUBLE PRECISION)"
        )
        cur.execute(
            f"INSERT INTO {SCRATCH_TABLE}"
            " SELECT time, exchange, symbol, open, high, low, close, volume"
            " FROM ohlcv_1m WHERE false"
        )
    f008_conn.commit()
    _insert(f008_conn, "AAA/USDT", list(range(600)), table=SCRATCH_TABLE)
    # 同一 (exchange, symbol, time) 再来一行：只有无主键表能造出这种重复
    _insert(f008_conn, "AAA/USDT", [300], table=SCRATCH_TABLE)
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT", table=SCRATCH_TABLE)
    assert result.verdict == VERDICT_QUARANTINED
    assert result.reason_code == REASON_DUPLICATE
    assert result.metrics["duplicate_keys"] == 1


def test_aggregate_mismatch_fixture_is_quarantined(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(600)))
    _refresh_aggregates(f008_conn)
    # 刷完聚合后抽掉中间**一整桶**（5 分钟）：缺失率 5/600 ≈ 0.83% 仍过 1% 阈值、边界仍闭合，
    # 但基表的 5m 桶数比物化视图少一个 —— 跨周期对账必须判红
    with f008_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM ohlcv_1m WHERE time >= %s AND time < %s",
            (WINDOW_START + timedelta(minutes=300), WINDOW_START + timedelta(minutes=305)),
        )
    f008_conn.commit()
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT")
    assert result.verdict == VERDICT_QUARANTINED
    assert result.reason_code == REASON_AGGREGATE, result.metrics
    assert any(not item["match"] for item in result.metrics["aggregates"].values())


def test_incomplete_backfill_is_not_pass(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(600)))
    _mark_backfill_complete(f008_conn, "AAA/USDT", status="running")
    result = _check(f008_conn, "AAA/USDT")
    assert result.verdict == VERDICT_INCOMPLETE
    assert result.reason_code == REASON_INCOMPLETE

    with f008_conn.cursor() as cur:
        cur.execute("DELETE FROM backfill_progress")
    f008_conn.commit()
    assert _check(f008_conn, "AAA/USDT").verdict == VERDICT_INCOMPLETE


def test_quarantined_pair_is_not_admitted(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(0, 300)))
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    result = _check(f008_conn, "AAA/USDT")
    record_verdicts(f008_conn, [result], universe_id=UNIVERSE_ID)
    assert admitted_pairs(f008_conn) == frozenset()
    stored = current_verdicts(f008_conn)["AAA-USDT-PERP"]
    assert stored.reason_code == REASON_MISSING_RATIO


def test_verdict_records_are_append_only_and_latest_wins(f008_conn) -> None:
    _insert(f008_conn, "AAA/USDT", list(range(0, 300)))
    _mark_backfill_complete(f008_conn, "AAA/USDT")
    record_verdicts(
        f008_conn,
        [_check(f008_conn, "AAA/USDT")],
        universe_id=UNIVERSE_ID,
        judged_at=datetime(2026, 9, 2, tzinfo=UTC),
    )
    _insert(f008_conn, "AAA/USDT", list(range(300, 600)))
    _refresh_aggregates(f008_conn)
    record_verdicts(
        f008_conn,
        [_check(f008_conn, "AAA/USDT")],
        universe_id=UNIVERSE_ID,
        judged_at=datetime(2026, 9, 3, tzinfo=UTC),
    )
    stored = current_verdicts(f008_conn)["AAA-USDT-PERP"]
    assert stored.verdict == VERDICT_ACTIVE  # 最新一条生效

    with f008_conn.cursor() as cur, pytest.raises(Exception, match="只追加"):
        cur.execute("UPDATE universe_quality_verdicts SET verdict = 'ACTIVE'")
    f008_conn.rollback()


def test_gate_refuses_invalid_thresholds() -> None:
    with pytest.raises(QualityGateError):
        from alphamill.data_bridge.universe.quality_gate import GateThresholds

        GateThresholds(missing_ratio=2.0)
