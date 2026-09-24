"""F009 控制面契约与状态机（unit，CI 常绿，假 predictor，不需要 GPU）。

对应 spec FR-001/FR-002/FR-004 与 AC-001/AC-002/AC-004、design §4/§5：
- `status` 返回八字段；动作窗口内 `state=transitional` 且 `operation` 非空；
- `stop` 卸载并置 `desired=stopped`、幂等、不终止进程；卸载失败按注入点落点（§5 表）；
- `restore` 重载并置 `desired=running`、幂等；加载失败 `E_UNAVAILABLE` 且进程不退出。

状态由 `(desired, model_loaded)` 派生，不存第二份——测试因此只断言这两者与 wire 输出。
"""

from __future__ import annotations

import threading
import time

import pytest
from _f009_fakes import FakeSignal

from alphamill.kronos_service import lifecycle
from alphamill.kronos_service.lifecycle_config import LifecycleConfig


def _controller(signal=None, **cfg_kwargs) -> lifecycle.LifecycleController:
    config = LifecycleConfig(**{"probe_mode": "torch", **cfg_kwargs})
    return lifecycle.LifecycleController(signal or FakeSignal(), config)


def test_status_returns_eight_fields_when_running() -> None:
    payload = _controller().status()

    assert set(payload) == {
        "state",
        "desired",
        "contract_version",
        "model_loaded",
        "vram_bytes",
        "vram_readable",
        "device",
        "operation",
    }
    assert payload["state"] == "running"
    assert payload["desired"] == "running"
    assert payload["model_loaded"] is True
    assert payload["operation"] is None
    assert payload["contract_version"] == lifecycle.CONTRACT_VERSION
    assert "error" not in payload


def test_status_on_cpu_instance_reports_zero_readable() -> None:
    payload = _controller(FakeSignal(device="cpu")).status()

    assert (payload["device"], payload["vram_bytes"], payload["vram_readable"]) == ("cpu", 0, True)


def test_status_is_reachable_after_load_failure() -> None:
    """模型加载失败后控制面仍可达——可达性不依赖模型可用性（§5 不变量）。"""
    signal = FakeSignal(loaded=False)
    signal.load_error = RuntimeError("assets missing")
    controller = _controller(signal)

    with pytest.raises(lifecycle.LifecycleError) as excinfo:
        controller.restore()

    assert excinfo.value.code == lifecycle.E_UNAVAILABLE
    payload = controller.status()
    assert payload["state"] == "stopped"
    assert payload["model_loaded"] is False
    assert payload["operation"] is None


def test_status_during_action_is_transitional_with_operation() -> None:
    """动作窗口内：desired 已改、model_loaded 未跟上 → transitional 且 operation 非空。"""
    signal = FakeSignal()
    signal.unload_delay = 1.0
    controller = _controller(signal, stop_timeout_s=0.05)

    with pytest.raises(lifecycle.LifecycleError) as excinfo:
        controller.stop()
    assert excinfo.value.code == lifecycle.E_TIMEOUT

    payload = controller.status()
    assert payload["state"] == "transitional", payload
    assert payload["desired"] == "stopped"
    assert payload["model_loaded"] is True
    assert set(payload["operation"]) == {"id", "action", "started_at"}
    assert payload["operation"]["action"] == "stop"

    controller.wait_idle(timeout=5)


def test_stop_unloads_and_reports_stopped() -> None:
    signal = FakeSignal()
    controller = _controller(signal)

    payload = controller.stop()

    assert payload == {"state": "stopped", "vram_bytes": 0}
    assert signal.unload_calls == 1
    assert controller.status()["state"] == "stopped"
    assert controller.status()["operation"] is None


def test_stop_is_idempotent_and_keeps_process_alive() -> None:
    signal = FakeSignal()
    controller = _controller(signal)

    controller.stop()
    payload = controller.stop()

    assert payload["state"] == "stopped"
    # 进程存活：status 与 restore 随后都可达
    assert controller.status()["state"] == "stopped"
    assert controller.restore()["state"] == "running"


@pytest.mark.parametrize(
    ("discarded", "expect_desired", "expect_loaded"),
    [(False, "running", True), (True, "stopped", False)],
)
def test_unload_failure_lands_per_injection_point(
    discarded: bool, expect_desired: str, expect_loaded: bool
) -> None:
    """§5 表：丢引用前失败回落 running，丢引用后（含 empty_cache）保持 stopped。"""
    signal = FakeSignal()
    signal.unload_error = lifecycle.UnloadFailed("boom", discarded=discarded)
    controller = _controller(signal)

    with pytest.raises(lifecycle.LifecycleError) as excinfo:
        controller.stop()

    assert excinfo.value.code == lifecycle.E_UNLOAD_FAILED
    payload = controller.status()
    assert payload["desired"] == expect_desired
    assert payload["model_loaded"] is expect_loaded
    assert payload["operation"] is None, "返回错误前 operation 必须已清空（§5 不变量）"
    assert payload["state"] in ("running", "stopped"), "错误返回前状态必须落在稳定态"


def test_restore_reloads_and_reports_running() -> None:
    signal = FakeSignal(loaded=False)
    controller = _controller(signal)
    controller.stop()

    payload = controller.restore()

    assert payload == {"state": "running"}
    assert signal.load_calls == 1
    assert controller.status()["model_loaded"] is True


def test_restore_is_idempotent_without_reloading() -> None:
    signal = FakeSignal(loaded=True)
    controller = _controller(signal)

    first = controller.restore()
    second = controller.restore()

    assert first == second == {"state": "running"}
    assert signal.load_calls <= 1, "已加载时不得重复加载（复用 _load_predictor 早返回）"


def test_restore_failure_does_not_lie_or_exit() -> None:
    signal = FakeSignal(loaded=False)
    signal.load_error = RuntimeError("weights missing")
    controller = _controller(signal)
    controller.stop()

    with pytest.raises(lifecycle.LifecycleError) as excinfo:
        controller.restore()

    assert excinfo.value.code == lifecycle.E_UNAVAILABLE
    payload = controller.status()
    assert payload["state"] == "stopped", "不得伪报 running"
    assert payload["desired"] == "stopped", "加载失败 desired 回落 stopped（design §5）"
    assert payload["model_loaded"] is False


def test_allow_load_follows_desired() -> None:
    """停机准入的开关：desired=stopped 期间不允许加载（FR-003 的机制来源）。"""
    controller = _controller()

    assert controller.allow_load() is True
    controller.stop()
    assert controller.allow_load() is False
    controller.restore()
    assert controller.allow_load() is True


def test_status_not_blocked_by_running_action() -> None:
    """status 不进单飞执行器：动作进行中照样可达（design §4 R1-008）。"""
    signal = FakeSignal()
    signal.unload_delay = 0.4
    controller = _controller(signal, stop_timeout_s=5)
    done = threading.Event()

    def _stop():
        controller.stop()
        done.set()

    worker = threading.Thread(target=_stop)
    worker.start()
    time.sleep(0.05)
    started = time.monotonic()
    payload = controller.status()
    elapsed = time.monotonic() - started
    worker.join(timeout=5)

    assert elapsed < 0.3, f"status 被动作阻塞了 {elapsed:.2f}s"
    assert payload["operation"] is not None
    assert done.is_set()
