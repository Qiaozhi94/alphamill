"""F001 AC-001 回填完整性集成测试。

需要本地 TimescaleDB 在线（docker compose 起 quant-timescaledb）且回填已完成；
数据库不可达时跳过（CI 无 DB 场景），本地全绿为准（见 SOP 真实环境测试纪律）。
"""

import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

f001_backfill_report = pytest.importorskip("f001_backfill_report")

pytestmark = pytest.mark.integration


def _db_available() -> bool:
    try:
        conn = f001_backfill_report.db_connect()
    except Exception:
        return False
    conn.close()
    return True


@pytest.mark.skipif(not _db_available(), reason="本地 TimescaleDB 不可达")
def test_f001_backfill_completeness_passes():
    """AC-001：回填完整性校验按 design §3 口径通过。"""
    conn = f001_backfill_report.db_connect()
    try:
        report = f001_backfill_report.build_report(conn, "binance", _symbols(conn))
    finally:
        conn.close()

    assert report["ohlcv_1m"], "ohlcv_1m 无任何回填行"
    for symbol, stats in report["ohlcv_1m"].items():
        assert stats["verdict"] == "PASS", f"{symbol}: {stats}"
    for view, stats in report["continuous_aggregates"].items():
        assert stats["verdict"] == "PASS", f"{view}: 连续聚合与基表重算不一致 {stats}"


def _symbols(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT symbol FROM ohlcv_1m WHERE exchange = 'binance' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]
