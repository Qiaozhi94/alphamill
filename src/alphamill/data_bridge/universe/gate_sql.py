"""质量门的 SQL 取数助手（从 `quality_gate.py` 拆出，行数治理）。

四项检查各自的真实查询都在这里：行数与时间边界、重复主键、连续聚合按桶对账、
回填进度状态。拆开是为了让判定逻辑与 SQL 细节各自可读、各自在 350 行内。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from alphamill.data_bridge.universe.canonical import utc_iso

AGGREGATES = {
    "ohlcv_5m": "5 minutes",
    "ohlcv_15m": "15 minutes",
    "ohlcv_1h": "1 hour",
    "ohlcv_4h": "4 hours",
    "ohlcv_1d": "1 day",
}


def backfill_status(
    conn, exchange: str, db_symbol: str, window_start: datetime, window_end: datetime
) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT status FROM backfill_progress
            WHERE exchange = %s AND symbol = %s AND timeframe = '1m'
              AND target_start = %s AND target_end = %s
            """,
            (exchange, db_symbol, window_start, window_end),
        )
        row = cur.fetchone()
    return None if not row else str(row[0])


def row_bounds(conn, table: str, exchange: str, db_symbol: str, start: datetime, end: datetime):
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT count(*), min(time), max(time) FROM {table}"  # noqa: S608 - 表名来自受控参数
            " WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s",
            (exchange, db_symbol, start, end),
        )
        row = cur.fetchone()
    return int(row[0]), row[1], row[2]


def duplicate_keys(
    conn, table: str, exchange: str, db_symbol: str, start: datetime, end: datetime
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT count(*) FROM (
                SELECT exchange, symbol, time FROM {table}
                WHERE exchange = %s AND symbol = %s AND time >= %s AND time < %s
                GROUP BY exchange, symbol, time HAVING count(*) > 1
            ) dup
            """,  # noqa: S608 - 表名来自受控参数
            (exchange, db_symbol, start, end),
        )
        return int(cur.fetchone()[0])


def aggregate_mismatch(conn, exchange: str, start: datetime, end: datetime) -> dict[str, Any]:
    """连续聚合与 1m 基表按桶重算精确一致（差得不多也不放行）。

    窗口起点先按**该聚合的桶宽向下对齐**，再用同一个对齐值查两侧：基表侧按「桶与窗口有
    重叠」计入（`time >= start` 分组后，跨窗口起点那个不完整的桶也在内），聚合侧若按
    `bucket >= start` 过滤就会漏掉它——两侧口径不一致会让「上市时间不落在桶边界」的 pair
    恒判不一致（2026-09-24 实测：DEXE `listed_at=2024-12-24T11:30`，1h/4h/1d 各差 25，
    恰好等于在 11:30–12:00 有数据的 symbol 数；5m/15m 因 11:30 对齐而全等）。
    """
    out: dict[str, Any] = {}
    with conn.cursor() as cur:
        for view, bucket in AGGREGATES.items():
            cur.execute("SELECT time_bucket(%s::interval, %s::timestamptz)", (bucket, start))
            aligned_start = cur.fetchone()[0]
            cur.execute(
                f"SELECT count(*) FROM {view}"  # noqa: S608 - 视图名来自模块常量
                " WHERE exchange = %s AND bucket >= %s AND bucket < %s",
                (exchange, aligned_start, end),
            )
            view_rows = int(cur.fetchone()[0])
            cur.execute(
                f"""
                SELECT count(*) FROM (
                    SELECT symbol, time_bucket('{bucket}', time) AS b
                    FROM ohlcv_1m
                    WHERE exchange = %s AND time >= %s AND time < %s
                    GROUP BY symbol, b
                ) t
                """,  # noqa: S608 - 桶宽来自模块常量
                (exchange, aligned_start, end),
            )
            base_buckets = int(cur.fetchone()[0])
            out[view] = {
                "rows": view_rows,
                "base_buckets": base_buckets,
                "aligned_start": utc_iso(aligned_start),
                "match": view_rows == base_buckets,
            }
    return out
