"""F001 Kronos 推理冒烟：AC-002（编排内契约）+ AC-006（真实推理证据）。

AC-002 —— 编排内常绿：`/health` 200，`/predict` 返回结构合法的信号，且 `source`
与 `/health` 的 `model_enabled` **一致**（mock→placeholder，real→kronos）。声明真实
模型却回 placeholder 一律判红，不是放水的降级判据。

AC-006 —— 真实推理证据：需要 391MB 权重与 vendor clone，不在默认编排内，因此由独立
命令验证（前置条件见 spec §7 / vendor/VENDORED.md）：

    set -a; . ./deployment/.env; set +a   # DB_HOST 默认是 compose 服务名，宿主上不可解析
    DB_HOST=127.0.0.1 KRONOS_USE_REAL_MODEL=true KRONOS_REPO_PATH=vendor/Kronos \
      .venv/bin/python -m uvicorn alphamill.kronos_service.server:app --port 8002 &
    ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 \
      KRONOS_BASE_URL=http://127.0.0.1:8002 \
      .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py -q

未设 `KRONOS_REQUIRE_REAL_MODEL` 时 AC-006 跳过（默认编排是 mock，不让它污染常绿
门禁）；一旦设了该开关，mock 实例必须判红。
"""

import os

import pytest
import requests

BASE_URL = os.getenv("KRONOS_BASE_URL", "http://127.0.0.1:8001")

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}
REAL_MODEL_REQUIRED = os.getenv("KRONOS_REQUIRE_REAL_MODEL", "").lower() in {"1", "true", "yes"}

SIGNAL_FIELDS = ("signal_type", "confidence", "expected_return", "volatility", "direction_prob")


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


def _predict() -> dict:
    # 服务契约即 GET /predict/{symbol:path}，符号为 ccxt 斜杠格式（design §4）；
    # exchange 参数指向数据实际落库的交易所（F001 回填源 binance）。
    resp = requests.get(f"{BASE_URL}/predict/BTC/USDT", params={"exchange": "binance"}, timeout=120)
    assert resp.status_code == 200, resp.text[:300]
    return resp.json()


def test_kronos_health():
    """AC-002：健康端点可达。"""
    _require_or_skip(_service_up(), f"Kronos 服务不可达 {BASE_URL}")
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200


def test_kronos_predict_source_matches_declared_mode():
    """AC-002：/predict 结构合法，且 source 与部署模式自洽（两个方向都判红）。"""
    _require_or_skip(_service_up(), f"Kronos 服务不可达 {BASE_URL}")
    health = requests.get(f"{BASE_URL}/health", timeout=10).json()
    payload = _predict()

    missing = [field for field in SIGNAL_FIELDS if field not in payload]
    assert not missing, f"/predict 响应缺字段 {missing}: {payload}"
    assert payload["signal_type"] in {"buy", "sell", "neutral"}, payload
    assert payload["rows_used"] >= 30, payload

    expected_source = "kronos" if health.get("model_enabled") else "placeholder"
    assert payload.get("source") == expected_source, (
        f"部署模式与信号来源不一致：model_enabled={health.get('model_enabled')} "
        f"期望 source={expected_source}，实得 {payload.get('source')}"
    )


def test_kronos_predict_returns_kronos_source():
    """AC-006：真实模型实例必须返回 source=kronos（由 KRONOS_REQUIRE_REAL_MODEL 显式启用）。"""
    if not REAL_MODEL_REQUIRED:
        pytest.skip(
            "AC-006 需真实模型实例：设 KRONOS_REQUIRE_REAL_MODEL=1 并把 KRONOS_BASE_URL "
            "指向真实实例（命令见本文件 docstring / spec §6 AC-006）"
        )
    if not _service_up():
        pytest.fail(f"Kronos 服务不可达 {BASE_URL}")
    health = requests.get(f"{BASE_URL}/health", timeout=10).json()
    if not health.get("model_enabled"):
        pytest.fail(
            f"KRONOS_REQUIRE_REAL_MODEL=1 但 {BASE_URL} 是 mock 实例"
            "（model_enabled=false）——AC-006 需真实模型实例"
        )
    payload = _predict()
    assert payload.get("source") == "kronos", payload
    assert payload.get("model"), f"真实模型实例必须回报权重路径: {payload}"
