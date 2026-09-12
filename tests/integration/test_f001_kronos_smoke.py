"""F001 AC-002 Kronos 推理冒烟：/health 200 且 /predict 返回 source=kronos。

目标服务地址用 KRONOS_BASE_URL 覆盖（默认 http://127.0.0.1:8001，compose mock 模式）；
真实模型 CPU 推理冒烟时以 KRONOS_BASE_URL 指向本机 uvicorn 实例。服务不可达时跳过
（CI 场景），本地全绿为准（SOP 真实环境测试纪律）。
"""

import os

import pytest
import requests

BASE_URL = os.getenv("KRONOS_BASE_URL", "http://127.0.0.1:8001")

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}


def _require_or_skip(available: bool, reason: str) -> None:
    if available:
        return
    if INTEGRATION_REQUIRED:
        pytest.fail(reason)
    pytest.skip(reason)


def _service_up() -> bool:
    try:
        return requests.get(f"{BASE_URL}/health", timeout=5).status_code == 200
    except requests.RequestException:
        return False


def test_kronos_health():
    _require_or_skip(_service_up(), f"Kronos 服务不可达 {BASE_URL}")
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200


def test_kronos_predict_returns_kronos_source():
    _require_or_skip(_service_up(), f"Kronos 服务不可达 {BASE_URL}")
    # AC-002 要求 source=kronos（真实模型）。compose 默认实例为 mock 模式
    # （KRONOS_USE_REAL_MODEL=false，source=placeholder），此时跳过而非判红；
    # 真实模型实例见 tasks T008 记录（KRONOS_BASE_URL 指向 8002）。
    health = requests.get(f"{BASE_URL}/health", timeout=10).json()
    if not health.get("model_enabled"):
        _require_or_skip(
            False, "当前实例为 mock 模式（model_enabled=false），AC-002 需真实模型实例"
        )
    # 服务契约即 GET /predict/{symbol:path}，符号为 ccxt 斜杠格式 BTC/USDT（旧仓现
    # 行为，design §4）；exchange 参数指向数据实际落库的交易所（F001 回填源
    # binance，见 deployment/.env EXCHANGES）。
    resp = requests.get(f"{BASE_URL}/predict/BTC/USDT", params={"exchange": "binance"}, timeout=120)
    assert resp.status_code == 200, resp.text[:300]
    payload = resp.json()
    assert payload.get("source") == "kronos", payload
