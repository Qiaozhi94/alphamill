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


class _RaisingAfterUnload(FakeSignal):
    """卸载成功，但随后读状态时抛出未预期异常。

    R1-001 复现载体：worker 自己的 try 只包住 unload/eager_load，其后的
    `status().device` 与显存探测在 try 之外，那里抛的异常原本会漏成 HTTP 500。
    """

    def __init__(self):
        super().__init__()
        self._broken = False

    def unload(self) -> None:
        super().unload()
        self._broken = True  # 卸载成功，但此后查询设备状态就会抛错

    def status(self):
        if self._broken:
            raise RuntimeError("driver query failed")
        return type("S", (), {"loaded": self.loaded, "device": self.device})()


class _UnprobeableDevice(FakeSignal):
    """设备名是意外类型：探测层会抛错，但控制面必须照样可达（读数记为不可得）。"""

    def status(self):
        return type("S", (), {"loaded": self.loaded, "device": None})()


def test_unexpected_exception_still_returns_contract_envelope() -> None:
    """R1-001：任何未预期异常都必须落在契约信封里，不得漏成 HTTP 500。

    500 不带 `error` 字段，客户端会把它读成"端点不存在"并转入回落探测
    （架构 §7.1 错误码各司其职），把一次服务端内部故障误判成契约缺失。
    """
    client, _ = _client(_RaisingAfterUnload())

    resp = client.post("/lifecycle/stop", headers=HEADERS)

    assert resp.status_code == 200, f"未预期异常漏成非契约响应: {resp.status_code}"
    assert resp.json() == {"error": lifecycle.E_UNLOAD_FAILED}, resp.text[:200]


def test_status_stays_reachable_when_probe_raises() -> None:
    """R1-001：显存探测抛错不得让 status 不可达——可达性不依赖探测成功（AC-001）。"""
    client, _ = _client(_UnprobeableDevice())

    resp = client.get("/lifecycle/status", headers=HEADERS)

    assert resp.status_code == 200, f"status 被探测异常打挂: {resp.status_code}"
    payload = resp.json()
    assert payload["vram_readable"] is False
    assert payload["vram_bytes"] is None
    assert "error" not in payload


def test_unexpected_restore_failure_maps_to_unavailable() -> None:
    """restore 侧的未预期异常映射为 E_UNAVAILABLE，并把 desired 收敛到 stopped。"""
    signal = FakeSignal(loaded=False)
    signal.load_error = MemoryError("device side blew up")
    client, controller = _client(signal)

    resp = client.post("/lifecycle/restore", headers=HEADERS)

    assert resp.json() == {"error": lifecycle.E_UNAVAILABLE}
    after = controller.status()
    assert after["state"] == "stopped" and after["operation"] is None


def test_busy_is_immediate_and_does_not_touch_the_device() -> None:
    """R1-002：`E_BUSY` 必须立即返回，受理失败的路径不得先做显存探测。

    FR-006 写的是"立即返回 E_BUSY"。探测卡住正是 FR-007 明说要防的情形
    （`KRONOS_VRAM_PROBE_TIMEOUT_S` 就是为它设的），若判忙排在探测之后，
    冲突动作会被拖到 probe_timeout 才拿到拒绝——编排的单飞重试节奏随之失真。
    """
    from alphamill.kronos_service import vram

    signal = FakeSignal(device="cuda:0")
    signal.unload_delay = 0.5
    controller = lifecycle.LifecycleController(
        signal,
        LifecycleConfig(probe_mode="nvidia_smi", probe_timeout_s=2.0, stop_timeout_s=5.0),
    )
    probes: list[float] = []

    def _stalling_probe(**kwargs):
        probes.append(kwargs["budget_s"])
        time.sleep(min(kwargs["probe_timeout_s"], kwargs["budget_s"]))  # 探测卡住到超时
        return vram.VramReading(used_bytes=None, readable=False, source="unavailable")

    worker = threading.Thread(target=controller.stop)
    worker.start()
    time.sleep(0.15)
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(vram, "probe", _stalling_probe)
        probes.clear()
        started = time.monotonic()
        with pytest.raises(lifecycle.LifecycleError) as excinfo:
            controller.restore()
        elapsed = time.monotonic() - started
    worker.join(timeout=10)

    assert excinfo.value.code == lifecycle.E_BUSY
    assert probes == [], "被拒的动作不得触碰设备"
    assert elapsed < 0.2, f"E_BUSY 被探测拖慢到 {elapsed:.2f}s"
