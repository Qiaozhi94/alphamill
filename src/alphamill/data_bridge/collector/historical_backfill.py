"""F001 历史回填：可被编排调用（T011），同时保留容器内的脚本入口。

拆分为三层：

- **环境层**：`main()` 从环境变量读窗口/交易对（supervisor 沿用 `python -m` 同款调用）；
- **编排层**：`run_backfill()` 逐 pair 执行、失败隔离、逐 pair 回调，供 `universe.backfill_runner`
  在共享限速预算下驱动；
- **抓取层**：`fetch_symbol()` 单 pair 断点续跑抓取（幂等 upsert、缺口即 stalled 而不是快进）。

限速：`limiter` 为空时沿用 F001 的内建退避（`FETCH_RETRIES`）；传入 `RateLimiter` 时
退避与节奏由限速器统一负责（pair 间共享预算），本模块不再自己 sleep。
"""

import logging
import os
import time
from datetime import UTC, datetime

from .backfill_boundaries import (
    delisting_end_for,
    listing_start_for,
    parse_unavailable_symbols,
)
from .backfill_progress import (
    TIMEFRAME,
    load_progress,
    save_progress,
)
from .db_writer import normalize_ohlcv_rows, upsert_ohlcv

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
TIMEFRAME_MS = 60_000
FETCH_LIMIT = int(os.getenv("BACKFILL_FETCH_LIMIT", "100"))


def retry_count(value: str | int) -> int:
    return max(1, int(value))


FETCH_RETRIES = retry_count(os.getenv("BACKFILL_RETRIES", "3"))
REFRESH_AGGREGATES = os.getenv("BACKFILL_REFRESH_AGGREGATES", "true").lower() in {
    "1",
    "true",
    "yes",
}
LISTING_STARTS = os.getenv("BACKFILL_SYMBOL_LISTING_STARTS", "")
DELISTING_ENDS = os.getenv("BACKFILL_SYMBOL_DELISTING_ENDS", "")
UNAVAILABLE_SYMBOLS = parse_unavailable_symbols(os.getenv("BACKFILL_UNAVAILABLE_SYMBOLS", ""))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("historical-backfill")

STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"
STATUS_UNAVAILABLE = "unavailable"
STATUS_DEFERRED = "deferred"


class BackfillDeadlineReached(Exception):
    """分段时间片到点：保存断点后停下，**不算失败**（下一片从 next_since 继续）。"""


def fetch_symbol(
    exchange_id: str,
    exchange,
    conn,
    symbol: str,
    start: datetime,
    end: datetime,
    *,
    limiter=None,
    should_stop=None,
) -> int:
    """抓取单个 pair 的窗口；返回本次累计 upsert 行数（幂等，可续跑）。

    `should_stop` 为时间片判据：到点即把当前断点写成 `running` 并抛
    `BackfillDeadlineReached`，让长跑可以按 ~30 分钟一片循环执行（单片失败只损失一片）。
    """
    if symbol in UNAVAILABLE_SYMBOLS:
        save_progress(
            conn,
            exchange_id,
            symbol,
            start,
            end,
            end,
            "unavailable",
            0,
            "symbol explicitly configured as unavailable for the target window",
        )
        return 0

    availability_start = listing_start_for(symbol, start, LISTING_STARTS)
    availability_end = delisting_end_for(symbol, end, DELISTING_ENDS)
    if availability_start >= availability_end:
        save_progress(
            conn,
            exchange_id,
            symbol,
            start,
            end,
            end,
            "unavailable",
            0,
            "symbol has no available candles inside the target window",
        )
        return 0

    resume_start, total = load_progress(conn, exchange_id, symbol, start, end)
    resume_start = max(resume_start, availability_start)
    save_progress(conn, exchange_id, symbol, start, end, resume_start, "running", total)

    since_ms = int(resume_start.timestamp() * 1000)
    end_ms = int(availability_end.timestamp() * 1000)
    attempts = 1 if limiter is not None else FETCH_RETRIES

    while since_ms < end_ms:
        if should_stop is not None and should_stop():
            cursor = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
            save_progress(
                conn,
                exchange_id,
                symbol,
                start,
                end,
                cursor,
                "running",
                total,
                "deferred to next chunk",
            )
            raise BackfillDeadlineReached(f"{symbol} 时间片到点，断点 {cursor.isoformat()}")
        rows = None
        for attempt in range(1, attempts + 1):
            try:
                rows = _fetch_once(limiter, exchange, symbol, since_ms)
                break
            except Exception as exc:
                if attempt >= attempts:
                    save_progress(
                        conn,
                        exchange_id,
                        symbol,
                        start,
                        end,
                        datetime.fromtimestamp(since_ms / 1000, tz=UTC),
                        "failed",
                        total,
                        str(exc),
                    )
                    raise
                sleep_for = min(2**attempt, 10)
                logger.warning(
                    "fetch failed exchange=%s symbol=%s attempt=%s/%s retry_in=%ss",
                    exchange_id,
                    symbol,
                    attempt,
                    attempts,
                    sleep_for,
                )
                time.sleep(sleep_for)

        availability_start_ms = int(availability_start.timestamp() * 1000)
        rows = [row for row in rows if availability_start_ms <= row[0] < end_ms]
        if not rows:
            if since_ms >= end_ms:
                save_progress(conn, exchange_id, symbol, start, end, end, "complete", total)
                break
            next_since_dt = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
            save_progress(
                conn,
                exchange_id,
                symbol,
                start,
                end,
                next_since_dt,
                "stalled",
                total,
                "exchange returned an empty batch before configured availability boundary",
            )
            raise RuntimeError(
                "empty OHLCV batch before configured availability boundary "
                f"for {exchange_id} {symbol} at {next_since_dt}"
            )

        total += upsert_ohlcv(conn, normalize_ohlcv_rows(exchange_id, symbol, rows))
        last_ts = rows[-1][0]
        next_since = last_ts + TIMEFRAME_MS
        if next_since <= since_ms:
            next_since_dt = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
            save_progress(
                conn,
                exchange_id,
                symbol,
                start,
                end,
                next_since_dt,
                "stalled",
                total,
                "exchange batch did not advance the cursor",
            )
            raise RuntimeError(
                f"OHLCV cursor stalled for {exchange_id} {symbol} at {next_since_dt}"
            )
        since_ms = next_since
        next_since_dt = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
        save_progress(conn, exchange_id, symbol, start, end, next_since_dt, "running", total)

        logger.info(
            "backfilled exchange=%s symbol=%s last=%s rows_total=%s target_end=%s",
            exchange_id,
            symbol,
            datetime.fromtimestamp(last_ts / 1000, tz=UTC).isoformat(),
            total,
            availability_end.isoformat(),
        )
        if limiter is None:
            time.sleep(exchange.rateLimit / 1000 if exchange.rateLimit else 0.2)

    completion_note = (
        "completed at configured delisting boundary" if availability_end < end else None
    )
    save_progress(conn, exchange_id, symbol, start, end, end, "complete", total, completion_note)
    return total


def _fetch_once(limiter, exchange, symbol: str, since_ms: int):
    if limiter is not None:
        return limiter.call(
            exchange.fetch_ohlcv,
            symbol,
            timeframe=TIMEFRAME,
            since=since_ms,
            limit=FETCH_LIMIT,
        )
    return exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, since=since_ms, limit=FETCH_LIMIT)


def refresh_aggregates(conn, start: datetime, end: datetime):
    if not REFRESH_AGGREGATES:
        return

    aggregates = ["ohlcv_5m", "ohlcv_15m", "ohlcv_1h", "ohlcv_4h", "ohlcv_1d"]
    previous_autocommit = conn.autocommit
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for aggregate in aggregates:
                logger.info("refreshing aggregate=%s start=%s end=%s", aggregate, start, end)
                cur.execute(
                    "CALL refresh_continuous_aggregate(%s, %s, %s)", (aggregate, start, end)
                )
    finally:
        conn.autocommit = previous_autocommit


def main() -> int:
    """环境层入口（`python -m alphamill.data_bridge.collector.historical_backfill`）。"""
    from .backfill_cli import run_from_env

    return run_from_env()


if __name__ == "__main__":
    raise SystemExit(main())
