import logging
import os
import time
from datetime import UTC, datetime, timedelta

try:  # Support both package imports and the legacy standalone container entrypoint.
    from .db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from .symbol_manager import parse_symbols
except ImportError:  # pragma: no cover - exercised only by direct script execution.
    from db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from symbol_manager import parse_symbols


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
TIMEFRAME = "1m"
TIMEFRAME_MS = 60_000
DEFAULT_DAYS = int(os.getenv("BACKFILL_DAYS", "1"))
FETCH_LIMIT = int(os.getenv("BACKFILL_FETCH_LIMIT", "100"))
FETCH_RETRIES = int(os.getenv("BACKFILL_RETRIES", "3"))
REFRESH_AGGREGATES = os.getenv("BACKFILL_REFRESH_AGGREGATES", "true").lower() in {
    "1",
    "true",
    "yes",
}
RESUME_BACKFILL = os.getenv("BACKFILL_RESUME", "true").lower() in {"1", "true", "yes"}

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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS backfill_progress (
                exchange      TEXT NOT NULL,
                symbol        TEXT NOT NULL,
                timeframe     TEXT NOT NULL,
                target_start  TIMESTAMPTZ NOT NULL,
                target_end    TIMESTAMPTZ NOT NULL,
                next_since    TIMESTAMPTZ NOT NULL,
                status        TEXT NOT NULL DEFAULT 'running',
                rows_upserted BIGINT NOT NULL DEFAULT 0,
                last_error    TEXT,
                started_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                completed_at  TIMESTAMPTZ,
                PRIMARY KEY (exchange, symbol, timeframe, target_start, target_end)
            )
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_backfill_progress_status
                ON backfill_progress (status, updated_at DESC)
            """
        )
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
              AND status <> 'complete'
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
                    CASE WHEN %s = 'complete' THEN NOW() ELSE NULL END)
            ON CONFLICT (exchange, symbol, timeframe, target_start, target_end)
            DO UPDATE SET
                next_since = EXCLUDED.next_since,
                status = EXCLUDED.status,
                rows_upserted = EXCLUDED.rows_upserted,
                last_error = EXCLUDED.last_error,
                updated_at = NOW(),
                completed_at = CASE
                    WHEN EXCLUDED.status = 'complete' THEN NOW()
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
    resume_start, total = load_progress(conn, exchange_id, symbol, start, end)
    save_progress(conn, exchange_id, symbol, start, end, resume_start, "running", total)

    since_ms = int(resume_start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

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

        rows = [row for row in rows if row[0] < end_ms]
        if not rows:
            break

        total += upsert_ohlcv(conn, normalize_ohlcv_rows(exchange_id, symbol, rows))
        last_ts = rows[-1][0]
        next_since = last_ts + TIMEFRAME_MS
        if next_since <= since_ms:
            break
        since_ms = next_since
        next_since_dt = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
        save_progress(conn, exchange_id, symbol, start, end, next_since_dt, "running", total)

        logger.info(
            "backfilled exchange=%s symbol=%s last=%s rows_total=%s target_end=%s",
            exchange_id,
            symbol,
            datetime.fromtimestamp(last_ts / 1000, tz=UTC).isoformat(),
            total,
            end.isoformat(),
        )
        time.sleep(exchange.rateLimit / 1000 if exchange.rateLimit else 0.2)

    save_progress(conn, exchange_id, symbol, start, end, end, "complete", total)
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


def main():
    exchanges = csv_env("EXCHANGES", "okx")
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
            finally:
                close = getattr(exchange, "close", None)
                if callable(close):
                    close()
        refresh_aggregates(conn, start, end)
        logger.info("backfill complete rows_upserted=%s", grand_total)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
