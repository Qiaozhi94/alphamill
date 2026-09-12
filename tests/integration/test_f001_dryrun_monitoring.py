"""F001 AC-004 dry-run 监控集成测试：风控钩子前置 + 监控面板数据非空。

需要本地服务在线：TimescaleDB（quant-timescaledb）、Freqtrade dry-run（8080）、
Kronos 薄壳（8001）；任一不可达时跳过（CI 场景），本地全绿为准（SOP 真实环境纪律）。
风控钩子（confirm_trade_entry 三件套 + Kronos 方向守卫）的行为证据见 tasks T017
forceenter 双路径实测；本测试守护面板数据链路的持续可用。
"""

import os

import pytest
import requests

FREQTRADE_URL = os.getenv("FREQTRADE_URL", "http://127.0.0.1:8080")
FREQTRADE_AUTH = ("admin", "quant2026")

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}


def _require_or_skip(available: bool, reason: str) -> None:
    if available:
        return
    if INTEGRATION_REQUIRED:
        pytest.fail(reason)
    pytest.skip(reason)


def _db():
    sys_path_setup()
    from alphamill.data_bridge.collector.db_writer import db_connect

    return db_connect()


def sys_path_setup():
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))


def _ft_available() -> bool:
    try:
        return (
            requests.get(f"{FREQTRADE_URL}/api/v1/ping", timeout=5).json().get("status") == "pong"
        )
    except Exception:
        return False


def _db_available() -> bool:
    try:
        conn = _db()
    except Exception:
        return False
    conn.close()
    return True


def _db_count(conn, table: str) -> int:
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {table}")  # noqa: S608 固定表名清单
        return int(cur.fetchone()[0])


def _kronos_available() -> bool:
    try:
        resp = requests.get(
            f"{os.getenv('KRONOS_BASE_URL', 'http://127.0.0.1:8001')}/health", timeout=5
        )
        return resp.status_code == 200
    except Exception:
        return False


def test_freqtrade_dryrun_alive():
    """dry-run bot 存活且 state=RUNNING。"""
    _require_or_skip(_ft_available(), "Freqtrade dry-run 不可达")
    resp = requests.get(f"{FREQTRADE_URL}/api/v1/show_config", auth=FREQTRADE_AUTH, timeout=10)
    assert resp.status_code == 200
    assert resp.json()["dry_run"] is True
    assert resp.json()["state"] == "running"


def test_kronos_signal_source_reachable():
    """风控钩子的信号前置：Kronos 服务可出信号。"""
    _require_or_skip(_kronos_available(), "Kronos 薄壳不可达")
    resp = requests.get(
        f"{os.getenv('KRONOS_BASE_URL', 'http://127.0.0.1:8001')}/predict/BTC/USDT",
        params={"exchange": "binance"},
        timeout=30,
    )
    assert resp.status_code == 200
    assert resp.json()["signal_type"] in {"buy", "sell", "neutral"}


def test_monitoring_panels_have_data():
    """AC-004 面板数据源非空：K 线延迟(ohlcv_1m)/信号质量(signals_log)/交易健康(snapshots)。"""
    _require_or_skip(_ft_available() and _db_available(), "Freqtrade dry-run 或 TimescaleDB 不可达")
    conn = _db()
    try:
        assert _db_count(conn, "ohlcv_1m") > 0, "ohlcv_1m 无数据（K 线延迟面板空）"
        assert _db_count(conn, "signals_log") > 0, "signals_log 无数据（信号质量面板空）"
        assert _db_count(conn, "dryrun_runtime_snapshots") > 0, (
            "dryrun_runtime_snapshots 无数据（交易健康面板空）"
        )
    finally:
        conn.close()
