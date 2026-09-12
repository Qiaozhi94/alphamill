import logging
import os
import time
from datetime import UTC, datetime, timedelta

try:  # Support both package imports and the legacy standalone container entrypoint.
    from .backfill_boundaries import (
        delisting_end_for,
        listing_start_for,
        parse_unavailable_symbols,
    )
    from .db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from .symbol_manager import parse_symbols
except ImportError:  # pragma: no cover - exercised only by direct script execution.
    from backfill_boundaries import delisting_end_for, listing_start_for, parse_unavailable_symbols
    from db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from symbol_manager import parse_symbols


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
TIMEFRAME = "1m"
TIMEFRAME_MS = 60_000
DEFAULT_DAYS = int(os.getenv("BACKFILL_DAYS", "1"))
FETCH_LIMIT = int(os.getenv("BACKFILL_FETCH_LIMIT", "100"))


def retry_count(value: str | int) -> int:
    return max(1, int(value))


FETCH_RETRIES = retry_count(os.getenv("BACKFILL_RETRIES", "3"))
REFRESH_AGGREGATES = os.getenv("BACKFILL_REFRESH_AGGREGATES", "true").lower() in {
    "1",
    "true",
    "yes",
}
RESUME_BACKFILL = os.getenv("BACKFILL_RESUME", "true").lower() in {"1", "true", "yes"}
LISTING_STARTS = os.getenv("BACKFILL_SYMBOL_LISTING_STARTS", "")
DELISTING_ENDS = os.getenv("BACKFILL_SYMBOL_DELISTING_ENDS", "")
UNAVAILABLE_SYMBOLS = parse_unavailable_symbols(os.getenv("BACKFILL_UNAVAILABLE_SYMBOLS", ""))

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("historical-backfill")


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


def build_exchange(exchange_id: str):
    import ccxt

    exchange_class = getattr(ccxt, exchange_id)
    config = {
        "enableRateLimit": True,
        "timeout": 30_000,
    }
    api_key = os.getenv(f"{exchange_id.upper()}_API_KEY", "")
    secret = os.getenv(f"{exchange_id.upper()}_SECRET", "")
    password = os.getenv(f"{exchange_id.upper()}_PASSPHRASE", "")
    if api_key and secret:
        config["apiKey"] = api_key
        config["secret"] = secret
    if password:
        config["password"] = password
    # 本机 DNS 对部分交易所域名存在污染时，经内网代理出网（默认关闭，不影响直连行为）。
    exchange_proxy = os.getenv(f"{exchange_id.upper()}_HTTPS_PROXY", "")
    if exchange_proxy:
        config["httpsProxy"] = exchange_proxy
    return exchange_class(config)


def ensure_progress_table(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.backfill_progress')")
        if cur.fetchone()[0] is None:
            raise RuntimeError("backfill_progress is missing; initialize db/init.sql first")
    conn.commit()


def load_progress(
    conn, exchange_id: str, symbol: str, start: datetime, end: datetime
) -> tuple[datetime, int]:
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


def fetch_symbol(
    exchange_id: str, exchange, conn, symbol: str, start: datetime, end: datetime
) -> int:
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

    while since_ms < end_ms:
        rows = None
        for attempt in range(1, FETCH_RETRIES + 1):
            try:
                rows = exchange.fetch_ohlcv(
                    symbol, timeframe=TIMEFRAME, since=since_ms, limit=FETCH_LIMIT
                )
                break
            except Exception as exc:
                if attempt >= FETCH_RETRIES:
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
                    FETCH_RETRIES,
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
        time.sleep(exchange.rateLimit / 1000 if exchange.rateLimit else 0.2)

    completion_note = (
        "completed at configured delisting boundary" if availability_end < end else None
    )
    save_progress(conn, exchange_id, symbol, start, end, end, "complete", total, completion_note)
    return total


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
        ensure_progress_table(conn)
        grand_total = 0
        failed = False
        for exchange_id in exchanges:
            exchange = build_exchange(exchange_id)
            try:
                for symbol in symbols:
                    try:
                        total = fetch_symbol(exchange_id, exchange, conn, symbol, start, end)
                        grand_total += total
                        logger.info(
                            "symbol complete exchange=%s symbol=%s rows_upserted=%s",
                            exchange_id,
                            symbol,
                            total,
                        )
                    except Exception:
                        logger.exception("symbol failed exchange=%s symbol=%s", exchange_id, symbol)
                        conn.rollback()
                        failed = True
            finally:
                close = getattr(exchange, "close", None)
                if callable(close):
                    close()
        if failed:
            logger.error("backfill stopped with failed symbols; aggregates were not refreshed")
            return 1
        refresh_aggregates(conn, start, end)
        logger.info("backfill complete rows_upserted=%s", grand_total)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
