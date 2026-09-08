import logging
import os
import signal
import time
from collections.abc import Iterable
from math import floor

try:  # Support both package imports and the legacy standalone container entrypoint.
    from .db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from .symbol_manager import parse_symbols
except ImportError:  # pragma: no cover - exercised only by direct script execution.
    from db_writer import db_connect, normalize_ohlcv_rows, upsert_ohlcv
    from symbol_manager import parse_symbols


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "30"))
FETCH_LIMIT = int(os.getenv("FETCH_LIMIT", "5"))
SUPPORTED_TIMEFRAME = "1m"

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger("ccxt-ingestor")

shutdown_requested = False


def request_shutdown(signum, _frame):
    global shutdown_requested
    shutdown_requested = True
    logger.info("received signal %s, shutting down after current cycle", signum)


signal.signal(signal.SIGTERM, request_shutdown)
signal.signal(signal.SIGINT, request_shutdown)


def csv_env(name: str, default: str = "") -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def build_exchange(exchange_id: str):
    import ccxt

    exchange_class = getattr(ccxt, exchange_id)
    api_key = os.getenv(f"{exchange_id.upper()}_API_KEY", "")
    secret = os.getenv(f"{exchange_id.upper()}_SECRET", "")
    password = os.getenv(f"{exchange_id.upper()}_PASSPHRASE", "")

    config = {
        "enableRateLimit": True,
        "timeout": 30_000,
    }
    if api_key and secret:
        config["apiKey"] = api_key
        config["secret"] = secret
    if password:
        config["password"] = password

    return exchange_class(config)


def is_closed_candle(ts_ms: int, timeframe_seconds: int = 60) -> bool:
    now_ms = int(time.time() * 1000)
    candle_close_ms = ts_ms + timeframe_seconds * 1000
    return candle_close_ms <= now_ms


def normalize_rows(exchange_id: str, symbol: str, rows: Iterable[list]) -> list[tuple]:
    closed_rows = [row for row in rows if is_closed_candle(row[0])]
    return normalize_ohlcv_rows(exchange_id, symbol, closed_rows)


def run_cycle(conn, exchange_id: str, exchange, symbols: list[str]) -> dict:
    written = 0
    succeeded = 0
    failed = 0
    for symbol in symbols:
        try:
            rows = exchange.fetch_ohlcv(symbol, timeframe=SUPPORTED_TIMEFRAME, limit=FETCH_LIMIT)
            closed_rows = normalize_rows(exchange_id, symbol, rows)
            rows_written = upsert_ohlcv(conn, closed_rows)
            written += rows_written
            succeeded += 1
            logger.info(
                "stored exchange=%s symbol=%s timeframe=%s fetched=%s closed=%s upserted=%s",
                exchange_id,
                symbol,
                SUPPORTED_TIMEFRAME,
                len(rows),
                len(closed_rows),
                rows_written,
            )
        except Exception:
            failed += 1
            logger.warning(
                "failed exchange=%s symbol=%s",
                exchange_id,
                symbol,
                exc_info=logger.isEnabledFor(logging.DEBUG),
            )
            conn.rollback()
    return {"written": written, "succeeded": succeeded, "failed": failed}


def main():
    exchanges = csv_env("EXCHANGES", "binance")
    symbols = parse_symbols(os.getenv("SYMBOLS"))
    requested_timeframes = csv_env("TIMEFRAMES", SUPPORTED_TIMEFRAME)

    unsupported = [tf for tf in requested_timeframes if tf != SUPPORTED_TIMEFRAME]
    if unsupported:
        logger.warning(
            "ignoring unsupported raw timeframes %s; collect 1m and use Timescale "
            "continuous aggregates",
            ",".join(unsupported),
        )

    clients = {exchange_id: build_exchange(exchange_id) for exchange_id in exchanges}
    logger.info(
        "starting collector exchanges=%s symbols=%s poll_seconds=%s",
        exchanges,
        symbols,
        POLL_SECONDS,
    )

    backoff = 1
    conn = None
    while not shutdown_requested:
        try:
            if conn is None or conn.closed:
                conn = db_connect()
                backoff = 1
                logger.info("connected to database")

            cycle_written = 0
            cycle_succeeded = 0
            cycle_failed = 0
            started_at = time.monotonic()
            for exchange_id, exchange in clients.items():
                result = run_cycle(conn, exchange_id, exchange, symbols)
                cycle_written += result["written"]
                cycle_succeeded += result["succeeded"]
                cycle_failed += result["failed"]

            elapsed = time.monotonic() - started_at
            sleep_for = max(POLL_SECONDS - floor(elapsed), 1)
            logger.info(
                "cycle complete rows_upserted=%s symbols_ok=%s symbols_failed=%s "
                "elapsed=%.2fs next_cycle_in=%ss",
                cycle_written,
                cycle_succeeded,
                cycle_failed,
                elapsed,
                sleep_for,
            )
            time.sleep(sleep_for)
        except Exception:
            logger.exception("collector cycle failed")
            if conn is not None:
                conn.close()
            sleep_for = min(backoff, 60)
            logger.info("retrying in %s seconds", sleep_for)
            time.sleep(sleep_for)
            backoff *= 2

    if conn is not None and not conn.closed:
        conn.close()
    for exchange in clients.values():
        close = getattr(exchange, "close", None)
        if callable(close):
            close()
    logger.info("collector stopped")


if __name__ == "__main__":
    main()
