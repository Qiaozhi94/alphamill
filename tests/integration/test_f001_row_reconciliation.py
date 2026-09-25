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

import f001_backfill_config  # noqa: E402

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


def _f001_baseline_symbols() -> list[str]:
    """F001 的判据宇宙 = **入库 window.env** 的 `SYMBOLS`，不是运行时 `.env` 的扩容清单。

    `SYMBOLS` 属运行量（优先级：显式环境变量 > 本机 `deployment/.env` > 入库 window.env），
    F008 扩容后运行时是 35 对。F001 的 completeness 口径要求**满窗**，对窗口中途上市的
    pair（2026-09-24 实测 DEXE/PENGU/PROM/HEI，上市于 2024-12-17 ~ 2025-02-13）必然判
    FAIL——它把上市前的空白计成缺失，属口径与事实的结构性不匹配，而非数据缺陷（这 4 对
    `gap_jumps_gt_1m=0`、获批区间内无跳变）。F008 正是为此立 `AC-006`（缺失率按**实际
    可得窗口**计算）并由 `tests/integration/test_f008_quality_gate.py` 对扩容后的 pair
    单独设门；此处若跟着运行量走，等于用 F001 口径否定 F008 的裁决。
    """
    for line in f001_backfill_config.WINDOW_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("SYMBOLS="):
            return [s for s in line.split("=", 1)[1].strip().split(",") if s]
    raise AssertionError("入库 window.env 未声明 SYMBOLS 默认值")


def test_f001_backfill_completeness_passes():
    """AC-001：F001 基线 6 对按 design §3 口径通过。"""
    _require_or_skip(_db_available(), "本地 TimescaleDB 不可达")
    exchange = f001_backfill_config.configured_exchanges()[0]
    symbols = _f001_baseline_symbols()
    assert set(symbols) <= set(f001_backfill_config.configured_symbols()), (
        "运行时 universe 必须覆盖 F001 基线（扩容不得丢掉基线 pair）"
    )
    conn = f001_backfill_report.db_connect()
    try:
        if _backfill_incomplete(conn, exchange, symbols):
            _require_or_skip(False, "回填尚未完成（backfill_progress 存在非 complete 目标行）")
        report = f001_backfill_report.build_report(conn, exchange, symbols)
    finally:
        conn.close()

    assert report["ohlcv_1m"], "ohlcv_1m 无任何回填行"
    for symbol, stats in report["ohlcv_1m"].items():
        assert stats["verdict"] == "PASS", f"{symbol}: {stats}"
    for view, stats in report["continuous_aggregates"].items():
        assert stats["verdict"] == "PASS", f"{view}: 连续聚合与基表重算不一致 {stats}"


def _backfill_incomplete(conn, exchange: str, symbols: list[str]) -> bool:
    # 权威窗口 = supervisor/首跑钉死的 BACKFILL_START/END（跨进程 resume 的主键）。
    # 早期失败行（其他 target_end）已被权威窗口的重跑取代，不参与判据。
    window_start, window_end = f001_backfill_config.window_datetimes()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT count(DISTINCT symbol) FROM backfill_progress
            WHERE exchange = %s AND timeframe = '1m'
              AND status IN ('complete', 'unavailable')
              AND target_start = %s
              AND target_end = %s
            """,
            (exchange, window_start, window_end),
        )
        done = int(cur.fetchone()[0])
    return done < len(symbols)
