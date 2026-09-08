import os
import subprocess
from contextlib import contextmanager
from io import StringIO

import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor


def database_url() -> str | None:
    return os.getenv("DB_URL")


@contextmanager
def connect():
    db_url = database_url()
    if db_url:
        conn = psycopg2.connect(db_url)
    else:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "timescaledb"),
            port=int(os.getenv("DB_PORT", "5432")),
            dbname=os.getenv("DB_NAME", "quant"),
            user=os.getenv("DB_USER", "quant"),
            password=os.getenv("DB_PASSWORD", "changeme"),
        )

    try:
        yield conn
    finally:
        conn.close()


def healthcheck() -> dict:
    try:
        with connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                    SELECT
                        COUNT(*) AS total_rows,
                        MAX(time) AS latest_candle,
                        EXTRACT(EPOCH FROM (NOW() - MAX(time))) AS latest_lag_seconds
                    FROM ohlcv_1m
                    """
            )
            return dict(cur.fetchone())
    except Exception:
        if os.getenv("KRONOS_DB_DOCKER_FALLBACK", "false").lower() not in {"1", "true", "yes"}:
            raise
        return healthcheck_via_docker()


def healthcheck_via_docker() -> dict:
    sql = """
COPY (
    SELECT
        COUNT(*) AS total_rows,
        MAX(time) AS latest_candle,
        EXTRACT(EPOCH FROM (NOW() - MAX(time))) AS latest_lag_seconds
    FROM ohlcv_1m
) TO STDOUT WITH CSV HEADER
"""
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "timescaledb",
            "psql",
            "-U",
            os.getenv("DB_USER", "quant"),
            "-d",
            os.getenv("DB_NAME", "quant"),
            "-c",
            sql,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = pd.read_csv(StringIO(result.stdout)).to_dict(orient="records")
    return rows[0] if rows else {"total_rows": 0, "latest_candle": None, "latest_lag_seconds": None}


def latest_ohlcv(symbol: str, exchange: str = "okx", limit: int = 120) -> list[dict]:
    try:
        with connect() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                    SELECT time, exchange, symbol, open, high, low, close, volume
                    FROM ohlcv_1m
                    WHERE exchange = %s
                      AND symbol = %s
                    ORDER BY time DESC
                    LIMIT %s
                    """,
                (exchange, symbol, limit),
            )
            rows = [dict(row) for row in cur.fetchall()]
    except Exception:
        if os.getenv("KRONOS_DB_DOCKER_FALLBACK", "false").lower() not in {"1", "true", "yes"}:
            raise
        rows = latest_ohlcv_via_docker(symbol=symbol, exchange=exchange, limit=limit)

    rows.reverse()
    return rows


def latest_ohlcv_via_docker(symbol: str, exchange: str, limit: int) -> list[dict]:
    safe_exchange = exchange.replace("'", "''")
    safe_symbol = symbol.replace("'", "''")
    sql = f"""
COPY (
    SELECT time, exchange, symbol, open, high, low, close, volume
    FROM ohlcv_1m
    WHERE exchange = '{safe_exchange}'
      AND symbol = '{safe_symbol}'
    ORDER BY time DESC
    LIMIT {int(limit)}
) TO STDOUT WITH CSV HEADER
"""
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "timescaledb",
            "psql",
            "-U",
            os.getenv("DB_USER", "quant"),
            "-d",
            os.getenv("DB_NAME", "quant"),
            "-c",
            sql,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    df = pd.read_csv(StringIO(result.stdout))
    if df.empty:
        return []

    df["time"] = pd.to_datetime(df["time"], utc=True)
    return df.to_dict(orient="records")
