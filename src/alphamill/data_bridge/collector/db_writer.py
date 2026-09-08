import os
from collections.abc import Iterable
from datetime import UTC, datetime

import psycopg2
from psycopg2.extras import execute_values


def db_connect():
    db_url = os.getenv("DB_URL")
    if db_url:
        return psycopg2.connect(db_url)

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "timescaledb"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "quant"),
        user=os.getenv("DB_USER", "quant"),
        password=os.getenv("DB_PASSWORD", "changeme"),
    )


def normalize_ohlcv_rows(exchange_id: str, symbol: str, rows: Iterable[list]) -> list[tuple]:
    normalized = []
    for ts_ms, open_, high, low, close, volume in rows:
        normalized.append(
            (
                datetime.fromtimestamp(ts_ms / 1000, tz=UTC),
                exchange_id,
                symbol,
                float(open_),
                float(high),
                float(low),
                float(close),
                float(volume),
            )
        )
    return normalized


def upsert_ohlcv(conn, rows: list[tuple]) -> int:
    if not rows:
        return 0

    sql = """
        INSERT INTO ohlcv_1m
            (time, exchange, symbol, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (exchange, symbol, time) DO UPDATE SET
            open = EXCLUDED.open,
            high = EXCLUDED.high,
            low = EXCLUDED.low,
            close = EXCLUDED.close,
            volume = EXCLUDED.volume
    """
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()
    return len(rows)
