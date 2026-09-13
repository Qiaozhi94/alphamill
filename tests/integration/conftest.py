"""Load the local deployment environment for host-side integration tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import psycopg2
import pytest

CONTAINER = "quant-timescaledb"
F002_DB = "f002_integration"
REPO = Path(__file__).resolve().parents[2]

# F002 种子日（过去日期，与真实数据窗口无冲突）
D1, D2, D3, D4 = "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"


def pytest_configure() -> None:
    dotenv = REPO / "deployment/.env"
    if dotenv.is_file():
        for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    # Compose uses the service DNS name; these tests run on the host.
    if os.environ.get("DB_HOST") == "timescaledb":
        os.environ["DB_HOST"] = "127.0.0.1"


def _docker_psql(db: str, sql_file: Path | None = None, command: str | None = None) -> None:
    cmd = ["docker", "exec", "-i", CONTAINER, "psql", "-U", "quant", "-d", db,
           "-v", "ON_ERROR_STOP=1", "-q"]
    if sql_file is not None:
        with sql_file.open("rb") as fh:
            subprocess.run(cmd, input=fh.read(), check=True)
    else:
        subprocess.run([*cmd, "-c", command], check=True, stdout=subprocess.DEVNULL)


@pytest.fixture(scope="module")
def f002_db():
    """一次性模块级集成库：真实 schema（db/init.sql + 003 migration），测后销毁。

    需要本机 docker 与 quant-timescaledb 容器在线；不可用时按 SOP 约定跳过
    （ALPHAMILL_INTEGRATION=1 下判红）。quant 角色为超级用户，可自建库。
    """
    try:
        _docker_psql("postgres", command=f"SELECT 1")
    except Exception as exc:  # docker/容器不可达
        if os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}:
            pytest.fail(f"ALPHAMILL_INTEGRATION=1 但 docker/DB 不可达: {exc}")
        pytest.skip(f"docker 或 quant-timescaledb 不可达: {exc}")

    _docker_psql("postgres", command=f"DROP DATABASE IF EXISTS {F002_DB}")
    _docker_psql("postgres", command=f"CREATE DATABASE {F002_DB}")
    _docker_psql(F002_DB, sql_file=REPO / "db/init.sql")
    _docker_psql(F002_DB, sql_file=REPO / "db/migrations/003_derivatives_market_data.sql")
    creds = {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": F002_DB,
        "user": os.getenv("DB_USER", "quant"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    yield creds
    _docker_psql("postgres", command=f"DROP DATABASE IF EXISTS {F002_DB}")


@pytest.fixture()
def f002_conn(f002_db):
    conn = psycopg2.connect(**f002_db)
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture()
def f002_lake(tmp_path, monkeypatch):
    """每个测试独立的临时湖 + current symbol_map，绝不触碰真实 lake/。"""
    lake = tmp_path / "lake"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(lake))
    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "symbol_map.csv"))
    return lake


def seed_f002_data(conn) -> None:
    """确定性种子：BTC(D1×5, D3×1)、ETH(D1×5) 1m（D2 起步为空，供增量用例插入）；
    funding D1×3；OI D1×2；basis 空表；signals s1..s3（as-of 双时间轴用）；
    BTC D1 一条未解决质量标记。"""
    import datetime as dt

    def ts(day: str, minute: int) -> dt.datetime:
        return dt.datetime.fromisoformat(f"{day}T00:{minute:02d}:00").replace(tzinfo=dt.UTC)

    def at(day: str, hour: int, minute: int = 0) -> dt.datetime:
        return dt.datetime.fromisoformat(f"{day}T{hour:02d}:{minute:02d}:00").replace(tzinfo=dt.UTC)

    with conn.cursor() as cur:
        # 模块级库在测试间复用：先清场再播种
        for table in ("ohlcv_1m", "signals_log", "derivatives_funding_rates",
                      "derivatives_open_interest", "derivatives_mark_index_basis",
                      "ohlcv_quality_flags"):
            cur.execute(f"DELETE FROM {table}")
        # ohlcv_1m: close 基准 100.0，便于 AC-010 修订对照
        for minute in range(5):
            for symbol in ("BTC/USDT", "ETH/USDT"):
                cur.execute(
                    "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
                    " VALUES (%s,'binance',%s,100,101,99,100,1)",
                    (ts(D1, minute), symbol),
                )
        cur.execute(
            "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
            " VALUES (%s,'binance','BTC/USDT',100,101,99,100,1)",
            (ts(D3, 0),),
        )
        # derivatives_funding_rates: binanceusdm BTC/USDT D1 三档
        for hour in (0, 8, 16):
            cur.execute(
                "INSERT INTO derivatives_funding_rates (time, exchange, symbol, funding_rate,"
                " next_funding_time, mark_price, index_price, metadata, ingested_at)"
                " VALUES (%s,'binanceusdm','BTC/USDT',0.0001,%s,100,100,'{}'::jsonb, %s)",
                (at(D1, hour), at(D2, 0) if hour == 16 else at(D1, hour + 8), at(D4, 0)),
            )
        # derivatives_open_interest: (BTC/USDT, 1h) D1 两档
        for hour in (0, 1):
            cur.execute(
                "INSERT INTO derivatives_open_interest (time, exchange, symbol, timeframe,"
                " open_interest, open_interest_value, base_volume, quote_volume, metadata, ingested_at)"
                " VALUES (%s,'binanceusdm','BTC/USDT','1h',10,1000,1,100,'{}'::jsonb,%s)",
                (ts(D1, hour), ts(D4, 0)),
            )
        # signals_log: s1/s2 同事件不同可见性；s3 次日
        cur.execute(
            "INSERT INTO signals_log (time, exchange, symbol, source, signal_type, confidence,"
            " metadata, latest_candle, expected_return, volatility, direction_prob,"
            " realized_return_60m, evaluated_at)"
            " VALUES (%s,'binance','BTC/USDT','placeholder','buy',0.9,'{}'::jsonb,"
            " %s, 0.01, 0.2, 0.6, NULL, NULL)",  # s1: time=D1 12:00, 无评估
            (at(D1, 12), at(D1, 9)),
        )
        cur.execute(
            "INSERT INTO signals_log (time, exchange, symbol, source, signal_type, confidence,"
            " metadata, latest_candle, expected_return, volatility, direction_prob,"
            " realized_return_60m, evaluated_at)"
            " VALUES (%s,'binance','BTC/USDT','placeholder','buy',0.9,'{}'::jsonb,"
            " %s, 0.01, 0.2, 0.6, 0.05, %s)",  # s2: time=D1 12:00, 13:00 评估出 +5%
            (at(D1, 12), at(D1, 9), at(D1, 13)),
        )
        cur.execute(
            "INSERT INTO signals_log (time, exchange, symbol, source, signal_type, confidence,"
            " metadata, latest_candle, expected_return, volatility, direction_prob,"
            " realized_return_60m, evaluated_at)"
            " VALUES (%s,'binance','ETH/USDT','placeholder','sell',0.8,'{}'::jsonb,"
            " %s, -0.01, 0.3, 0.4, -0.02, %s)",  # s3: D2
            (at(D2, 10, 30), at(D2, 10), at(D2, 11)),
        )
        # ohlcv_quality_flags: BTC D1 未解决
        cur.execute(
            "INSERT INTO ohlcv_quality_flags (time, exchange, symbol, timeframe, flag_type,"
            " severity, metadata) VALUES (%s,'binance','BTC/USDT','1m','missing_candle',"
            "'warning','{}'::jsonb)",
            (ts(D1, 0),),
        )
    conn.commit()


def export_symbol_map_for(conn, lake) -> str:
    """测试辅助：为 scratch 库刷新 symbol map，返回 digest。"""
    from alphamill.data_bridge import symbol_map

    return symbol_map.export_symbol_map(conn=conn, lake_root=lake).digest
