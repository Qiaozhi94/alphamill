"""F001 AC-001 回填完整性集成测试。

需要本地 TimescaleDB 在线（docker compose 起 quant-timescaledb）且回填已完成；
数据库不可达时跳过（CI 无 DB 场景），本地全绿为准（见 SOP 真实环境测试纪律）。
"""

import os
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).resolve().parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

f001_backfill_report = pytest.importorskip("f001_backfill_report")

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
        conn = f001_backfill_report.db_connect()
    except Exception:
        return False
    conn.close()
    return True


def test_f001_backfill_completeness_passes():
    """AC-001：回填完整性校验按 design §3 口径通过。"""
    _require_or_skip(_db_available(), "本地 TimescaleDB 不可达")
    conn = f001_backfill_report.db_connect()
    try:
        if _backfill_incomplete(conn):
            _require_or_skip(False, "回填尚未完成（backfill_progress 存在非 complete 目标行）")
        report = f001_backfill_report.build_report(conn, "binance", _symbols(conn))
    finally:
        conn.close()

    assert report["ohlcv_1m"], "ohlcv_1m 无任何回填行"
    for symbol, stats in report["ohlcv_1m"].items():
        assert stats["verdict"] == "PASS", f"{symbol}: {stats}"
    for view, stats in report["continuous_aggregates"].items():
        assert stats["verdict"] == "PASS", f"{view}: 连续聚合与基表重算不一致 {stats}"


def _backfill_incomplete(conn) -> bool:
    # 权威窗口 = supervisor/首跑钉死的 BACKFILL_START/END（跨进程 resume 的主键）。
    # 早期失败行（其他 target_end）已被权威窗口的重跑取代，不参与判据。
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT count(DISTINCT symbol) FROM backfill_progress
            WHERE exchange = 'binance' AND timeframe = '1m'
              AND status = 'complete'
              AND target_start = '2024-09-10 00:00:00+00:00'
              AND target_end = '2026-09-10 15:52:00+00:00'
            """
        )
        done = int(cur.fetchone()[0])
    # 6 个交易对全部在权威窗口 complete 才算回填完成，否则跳过（回填进行中）。
    return done < 6


def _symbols(conn) -> list[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT symbol FROM ohlcv_1m WHERE exchange = 'binance' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]
