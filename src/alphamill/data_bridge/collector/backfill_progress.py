"""回填进度账本（`backfill_progress` 表）的读写面。

从 `historical_backfill.py` 拆出（T011）：进度账本是「断点续跑」的存储契约，交易所交互
是另一件事；拆开后两者都在 SOP 350 行硬上限内，且账本可以被回填编排独立复用。
表结构由 `db/init.sql` 建立（`ensure_progress_table` 只做存在性校验，不建表）。
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime

TIMEFRAME = "1m"
RESUME_BACKFILL = os.getenv("BACKFILL_RESUME", "true").lower() in {"1", "true", "yes"}

logger = logging.getLogger("historical-backfill")


def ensure_progress_table(conn) -> None:
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.backfill_progress')")
        if cur.fetchone()[0] is None:
            raise RuntimeError("backfill_progress is missing; initialize db/init.sql first")
    conn.commit()


def load_progress(
    conn, exchange_id: str, symbol: str, start: datetime, end: datetime
) -> tuple[datetime, int]:
    """断点续跑：返回 (next_since, rows_upserted)；无记录或有终态记录则从头开始。"""
    if not RESUME_BACKFILL:
        return start, 0

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT next_since, rows_upserted
            FROM backfill_progress
            WHERE exchange = %s
              AND symbol = %s
              AND timeframe = %s
              AND target_start = %s
              AND target_end = %s
              AND status NOT IN ('complete', 'unavailable')
            """,
            (exchange_id, symbol, TIMEFRAME, start, end),
        )
        row = cur.fetchone()

    if not row:
        return start, 0

    next_since, rows_upserted = row
    next_since = max(next_since.astimezone(UTC), start)
    logger.info(
        "resuming backfill exchange=%s symbol=%s next_since=%s rows_upserted=%s",
        exchange_id,
        symbol,
        next_since,
        rows_upserted,
    )
    return next_since, int(rows_upserted or 0)


def save_progress(
    conn,
    exchange_id: str,
    symbol: str,
    start: datetime,
    end: datetime,
    next_since: datetime,
    status: str,
    rows_upserted: int,
    last_error: str | None = None,
):
    """幂等 upsert：同一 (exchange, symbol, timeframe, target 窗口) 只有一行进度。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO backfill_progress (
                exchange, symbol, timeframe, target_start, target_end,
                next_since, status, rows_upserted, last_error, updated_at,
                completed_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(),
                    CASE WHEN %s IN ('complete', 'unavailable') THEN NOW() ELSE NULL END)
            ON CONFLICT (exchange, symbol, timeframe, target_start, target_end)
            DO UPDATE SET
                next_since = EXCLUDED.next_since,
                status = EXCLUDED.status,
                rows_upserted = EXCLUDED.rows_upserted,
                last_error = EXCLUDED.last_error,
                updated_at = NOW(),
                completed_at = CASE
                    WHEN EXCLUDED.status IN ('complete', 'unavailable') THEN NOW()
                    ELSE backfill_progress.completed_at
                END
            """,
            (
                exchange_id,
                symbol,
                TIMEFRAME,
                start,
                end,
                next_since,
                status,
                rows_upserted,
                last_error,
                status,
            ),
        )
    conn.commit()


def current_cursor(
    conn, exchange_id: str, symbol: str, start: datetime, end: datetime
) -> tuple[datetime | None, str | None, int]:
    """读断点位置与状态（回填编排记 `BackfillRun` 用）；无记录返回 (None, None, 0)。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT next_since, status, rows_upserted
            FROM backfill_progress
            WHERE exchange = %s AND symbol = %s AND timeframe = %s
              AND target_start = %s AND target_end = %s
            """,
            (exchange_id, symbol, TIMEFRAME, start, end),
        )
        row = cur.fetchone()
    if not row:
        return None, None, 0
    cursor = row[0]
    return (
        None if cursor is None else cursor.astimezone(UTC),
        None if row[1] is None else str(row[1]),
        int(row[2] or 0),
    )
