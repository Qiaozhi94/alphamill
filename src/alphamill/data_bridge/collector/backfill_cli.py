"""回填脚本的环境层：supervisor 的 `python -m ...historical_backfill` 入口。

从 `historical_backfill.py` 拆出（T011 行数治理）：环境变量解析、窗口推导与退出码
与抓取/编排逻辑无关，搬家后两者都在 SOP 350 行硬上限内。
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime, timedelta

from .backfill_orchestrator import run_backfill
from .db_writer import db_connect
from .historical_backfill import (
    STATUS_FAILED,
    logger,
    refresh_aggregates,
)
from .symbol_manager import parse_symbols

DEFAULT_DAYS = int(os.getenv("BACKFILL_DAYS", "1"))


def csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_utc(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def date_range() -> tuple[datetime, datetime]:
    end = parse_utc(os.getenv("BACKFILL_END")) if os.getenv("BACKFILL_END") else datetime.now(UTC)
    start = (
        parse_utc(os.getenv("BACKFILL_START"))
        if os.getenv("BACKFILL_START")
        else end - timedelta(days=DEFAULT_DAYS)
    )
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    if start >= end:
        raise ValueError("BACKFILL_START must be before BACKFILL_END")
    return start, end


def run_from_env() -> int:
    """按环境变量跑一轮回填；退出码 0 = 全部 pair 完成，1 = 有 pair 失败。"""
    exchanges = csv_env("EXCHANGES", "binance")
    symbols = parse_symbols(os.getenv("SYMBOLS"))
    start, end = date_range()
    logger.info(
        "starting historical backfill exchanges=%s symbols=%s start=%s end=%s",
        exchanges,
        symbols,
        start,
        end,
    )

    conn = db_connect()
    try:
        failed = False
        grand_total = 0
        for exchange_id in exchanges:
            outcomes = run_backfill(
                exchange_id=exchange_id,
                symbols=symbols,
                start=start,
                end=end,
                conn=conn,
            )
            for outcome in outcomes:
                if outcome.status == STATUS_FAILED:
                    failed = True
                else:
                    grand_total += outcome.rows
        if failed:
            logging.getLogger("historical-backfill").error(
                "backfill stopped with failed symbols; aggregates were not refreshed"
            )
            return 1
        refresh_aggregates(conn, start, end)
        logger.info("backfill complete rows_upserted=%s", grand_total)
        return 0
    finally:
        conn.close()
