"""F009 错误面、单飞与超时（unit，CI 常绿，FastAPI TestClient + 假 signal）。

对应 spec FR-005/FR-006 与 AC-005/AC-006、design §4/§5/§7：
- 版本协商：缺头与版本不匹配都以**恰为单键**的 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝；
- 请求体：空体与 `{}` 放行，含额外键以 `E_BAD_REQUEST` 拒绝且**不执行动作**，两码不代用；
- 单飞：动作进行中冲突动作立即 `E_BUSY`，原动作不受影响，`status` 不受阻；
- 超时：`E_TIMEOUT` 不中断后台、`operation` 仍非空；完成后转 `null` 且与 `desired` 一致。
"""

from __future__ import annotations

import threading
import time

import pytest
from _f009_fakes import FakeSignal
from fastapi import FastAPI
from fastapi.testclient import TestClient

from alphamill.kronos_service import lifecycle
from alphamill.kronos_service.lifecycle_api import build_lifecycle_router
from alphamill.kronos_service.lifecycle_config import LifecycleConfig

HEADERS = {lifecycle.CONTRACT_VERSION_HEADER: lifecycle.CONTRACT_VERSION}


def _client(signal=None, **cfg) -> tuple[TestClient, lifecycle.LifecycleController]:
    controller = lifecycle.LifecycleController(
        signal or FakeSignal(), LifecycleConfig(**{"probe_mode": "torch", **cfg})
    )
    app = FastAPI()
    app.include_router(build_lifecycle_router(controller))
    return TestClient(app), controller


@pytest.mark.parametrize("path", ["/lifecycle/status", "/lifecycle/stop", "/lifecycle/restore"])
@pytest.mark.parametrize("headers", [{}, {lifecycle.CONTRACT_VERSION_HEADER: "999"}])
def test_version_negotiation_rejects_with_single_key(path: str, headers: dict) -> None:
    client, controller = _client()
    method = client.get if path.endswith("status") else client.post

    resp = method(path, headers=headers)

    assert resp.status_code == 200, "错误也走 200 + 信封：非 2xx 可能被中间件改写"
    assert resp.json() == {"error": lifecycle.E_UNSUPPORTED_VERSION}
    assert controller.status()["desired"] == "running", "被拒请求不得改变期望态"


def test_success_response_has_no_error_key() -> None:
    client, _ = _client()

    payload = client.get("/lifecycle/status", headers=HEADERS).json()

    assert "error" not in payload
    assert payload["state"] == "running"


@pytest.mark.parametrize("body", [None, {}])
def test_empty_or_empty_object_body_is_accepted(body) -> None:
    signal = FakeSignal()
    client, _ = _client(signal)

    resp = client.post("/lifecycle/stop", headers=HEADERS, json=body)

    assert resp.json() == {"state": "stopped", "vram_bytes": 0}
    assert signal.unload_calls == 1


@pytest.mark.parametrize("body", [{"force": True}, {"state": "stopped"}, [1, 2], "x"])
def test_extra_parameters_are_bad_request_and_do_nothing(body) -> None:
    """额外参数一律 E_BAD_REQUEST，**不得**复用 E_UNSUPPORTED_VERSION，且不执行动作。"""
    signal = FakeSignal()
    client, controller = _client(signal)

    resp = client.post("/lifecycle/stop", headers=HEADERS, json=body)

    assert resp.json() == {"error": lifecycle.E_BAD_REQUEST}
    assert signal.unload_calls == 0
    assert controller.status()["state"] == "running"


def test_conflicting_action_is_busy_and_leaves_original_alone() -> None:
    signal = FakeSignal()
    signal.unload_delay = 0.5
    client, controller = _client(signal, stop_timeout_s=5)
    outcome: dict = {}

    def _stop():
        outcome["stop"] = client.post("/lifecycle/stop", headers=HEADERS).json()

    worker = threading.Thread(target=_stop)
    worker.start()
    time.sleep(0.1)

    busy = client.post("/lifecycle/restore", headers=HEADERS).json()
    during = client.get("/lifecycle/status", headers=HEADERS).json()
    worker.join(timeout=5)

    assert busy == {"error": lifecycle.E_BUSY}, "不排队、不叠加"
    assert during["state"] == "transitional" and during["operation"]["action"] == "stop"
    assert outcome["stop"] == {"state": "stopped", "vram_bytes": 0}, "原动作不受影响"
    assert signal.load_calls == 0, "被拒的 restore 不得执行"


def test_timeout_keeps_background_running_then_operation_clears() -> None:
    """E_TIMEOUT 不是失败终态：后台不被中断，完成后 operation 转 null 且与 desired 一致。"""
    signal = FakeSignal()
    signal.unload_delay = 0.4
    client, controller = _client(signal, stop_timeout_s=0.05)

    resp = client.post("/lifecycle/stop", headers=HEADERS).json()
    during = client.get("/lifecycle/status", headers=HEADERS).json()

    assert resp == {"error": lifecycle.E_TIMEOUT}
    assert during["operation"] is not None, "超时后动作仍在进行"
    assert during["state"] == "transitional"

    controller.wait_idle(timeout=5)
    after = client.get("/lifecycle/status", headers=HEADERS).json()
    assert after["operation"] is None
    assert after["state"] == "stopped" and after["desired"] == "stopped"
    assert signal.unload_calls == 1, "后台动作未被中断，也未被重复执行"


@pytest.mark.parametrize(
    ("discarded", "expect_state", "expect_loaded"),
    [(False, "running", True), (True, "stopped", False)],
)
def test_unload_failure_envelope_and_landing(
    discarded: bool, expect_state: str, expect_loaded: bool
) -> None:
    """三个注入点分别断言响应、desired、model_loaded、operation（AC-006）。"""
    signal = FakeSignal()
    signal.unload_error = lifecycle.UnloadFailed("inject", discarded=discarded)
    client, _ = _client(signal)

    resp = client.post("/lifecycle/stop", headers=HEADERS).json()
    after = client.get("/lifecycle/status", headers=HEADERS).json()

    assert resp == {"error": lifecycle.E_UNLOAD_FAILED}
    assert after["state"] == expect_state
    assert after["model_loaded"] is expect_loaded
    assert after["operation"] is None, "返回错误前 operation 必须已清空"


def test_restore_failure_envelope_is_unavailable() -> None:
    signal = FakeSignal(loaded=False)
    signal.load_error = RuntimeError("weights missing")
    client, _ = _client(signal)

    resp = client.post("/lifecycle/restore", headers=HEADERS).json()
    after = client.get("/lifecycle/status", headers=HEADERS).json()

    assert resp == {"error": lifecycle.E_UNAVAILABLE}
    assert after["state"] == "stopped" and after["operation"] is None


def test_error_codes_are_limited_to_contract(monkeypatch) -> None:
    """错误码取值限于契约表（IR-004）：实现不得发明新码。"""
    allowed = {
        lifecycle.E_UNSUPPORTED_VERSION,
        lifecycle.E_BAD_REQUEST,
        lifecycle.E_BUSY,
        lifecycle.E_TIMEOUT,
        lifecycle.E_UNLOAD_FAILED,
        lifecycle.E_UNAVAILABLE,
    }

    assert set(lifecycle.ERROR_CODES) == allowed
