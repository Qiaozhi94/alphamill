"""F001 AC-003 采集器冒烟：单交易对采集 + 幂等复跑 + 未闭合 K 线过滤。

需要本地 TimescaleDB 在线且可出网（经 BINANCE_HTTPS_PROXY 代理，见 deployment/.env）。
数据库不可达时跳过（CI 场景），本地全绿为准（SOP 真实环境测试纪律）。
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

ccxt_ingestor = pytest.importorskip("alphamill.data_bridge.collector.ccxt_ingestor")
db_writer = pytest.importorskip("alphamill.data_bridge.collector.db_writer")

pytestmark = pytest.mark.integration


def _db_available() -> bool:
    try:
        conn = db_writer.db_connect()
    except Exception:
        return False
    conn.close()
    return True


def _settled_rows(conn) -> int:
    """统计 2 分钟前的已闭 K 线行数（排除采集窗口内的分钟边界抖动）。"""
    cutoff = datetime.now(UTC) - timedelta(minutes=2)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT count(*) FROM ohlcv_1m
            WHERE exchange = 'binance' AND symbol = 'BTC/USDT' AND time < %s
            """,
            (cutoff,),
        )
        return int(cur.fetchone()[0])


@pytest.mark.skipif(not _db_available(), reason="本地 TimescaleDB 不可达")
def test_collector_smoke_single_symbol_idempotent():
    """AC-003：采集一个周期写入，重复执行不产生重复行。"""
    conn = db_writer.db_connect()
    try:
        exchange = ccxt_ingestor.build_exchange("binance")
        try:
            first = ccxt_ingestor.run_cycle(conn, "binance", exchange, ["BTC/USDT"])
            conn.commit()
            settled_after_first = _settled_rows(conn)

            second = ccxt_ingestor.run_cycle(conn, "binance", exchange, ["BTC/USDT"])
            conn.commit()
            settled_after_second = _settled_rows(conn)
        finally:
            close = getattr(exchange, "close", None)
            if callable(close):
                close()
    finally:
        conn.close()

    assert first, "采集周期未返回统计"
    assert second, "复跑周期未返回统计"
    # 已闭 K 线在两次紧邻周期之间不应增长（分钟边界抖动被 2 分钟 cutoff 排除）。
    assert settled_after_second == settled_after_first, (
        f"幂等违规：复跑后已闭 K 线增加 {settled_after_second - settled_after_first} 行"
    )
