"""F001 AC-003 采集器冒烟：单交易对采集 + 幂等复跑 + 未闭合 K 线过滤。

需要本地 TimescaleDB 在线且可出网（经 BINANCE_HTTPS_PROXY 代理，见 deployment/.env）。
数据库不可达时跳过（CI 场景），本地全绿为准（SOP 真实环境测试纪律）。
"""

import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

ccxt_ingestor = pytest.importorskip("alphamill.data_bridge.collector.ccxt_ingestor")
db_writer = pytest.importorskip("alphamill.data_bridge.collector.db_writer")

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}


def _require_or_skip(available: bool, reason: str) -> None:
    if available:
        return
    if INTEGRATION_REQUIRED:
        pytest.fail(reason)
    pytest.skip(reason)


def _db_available() -> bool:
    try:
        conn = db_writer.db_connect()
    except Exception:
        return False
    conn.close()
    return True


def _settled_rows(conn, cutoff: datetime) -> int:
    """统计 cutoff 之前的已闭 K 线行数；两次统计须共用同一 cutoff，否则跨分钟会多数一根。"""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT count(*) FROM ohlcv_1m
            WHERE exchange = 'binance' AND symbol = 'BTC/USDT' AND time < %s
            """,
            (cutoff,),
        )
        return int(cur.fetchone()[0])


def test_collector_smoke_single_symbol_idempotent():
    """AC-003：采集一个周期写入，重复执行不产生重复行。"""
    _require_or_skip(_db_available(), "本地 TimescaleDB 不可达")
    conn = db_writer.db_connect()
    try:
        exchange = ccxt_ingestor.build_exchange("binance")
        try:
            first = ccxt_ingestor.run_cycle(conn, "binance", exchange, ["BTC/USDT"])
            conn.commit()
            cutoff = datetime.now(UTC) - timedelta(minutes=2)
            settled_after_first = _settled_rows(conn, cutoff)

            second = ccxt_ingestor.run_cycle(conn, "binance", exchange, ["BTC/USDT"])
            conn.commit()
            settled_after_second = _settled_rows(conn, cutoff)
        finally:
            close = getattr(exchange, "close", None)
            if callable(close):
                close()
    finally:
        conn.close()

    assert first, "采集周期未返回统计"
    assert second, "复跑周期未返回统计"
    # 已闭 K 线在两次紧邻周期之间不应增长（固定 cutoff 排除分钟边界与在跑采集器的新 K 线）。
    assert settled_after_second == settled_after_first, (
        f"幂等违规：复跑后已闭 K 线增加 {settled_after_second - settled_after_first} 行"
    )
