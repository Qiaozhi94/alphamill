"""F009 生命周期日志行（unit，CI 常绿）。

对应 spec TR-001/TR-002/TR-003 与 AC-008、design §4 Event/Trace：
- stop / restore 各写一行 logfmt，字段集为白名单且含 `operation_id`；
- 超时返回后的迟到完成补写**同 operation_id** 的 `result=late_complete` 收尾行；
- 行内不得出现主机路径（模型路径除外）、凭据或数据库连接串。

运维价值：`docker logs kronos-signal-real | grep 'action='` 能还原当晚是否真的卸载、
显存降了多少、有没有迟到完成。
"""

from __future__ import annotations

import pytest
from _f009_fakes import FakeSignal

from alphamill.kronos_service import lifecycle
from alphamill.kronos_service.lifecycle_config import LifecycleConfig

EXPECTED_KEYS = [
    "action",
    "operation_id",
    "result",
    "state_before",
    "state_after",
    "desired",
    "vram_bytes_before",
    "vram_bytes_after",
    "vram_readable",
    "contract_version",
    "elapsed_ms",
]


def _parse(line: str) -> dict:
    return dict(part.split("=", 1) for part in line.split(" "))


def _controller(signal=None, **cfg):
    lines: list[str] = []
    controller = lifecycle.LifecycleController(
        signal or FakeSignal(),
        LifecycleConfig(**{"probe_mode": "torch", **cfg}),
        emit=lines.append,
    )
    return controller, lines


def test_stop_writes_one_logfmt_line_with_whitelisted_fields() -> None:
    controller, lines = _controller()

    controller.stop()

    assert len(lines) == 1
    fields = _parse(lines[0])
    assert list(fields) == EXPECTED_KEYS, "字段集是白名单且顺序固定，便于 grep 与对齐"
    assert fields["action"] == "stop"
    assert fields["result"] == "ok"
    assert fields["state_before"] == "running"
    assert fields["state_after"] == "stopped"
    assert fields["desired"] == "stopped"
    assert fields["contract_version"] == lifecycle.CONTRACT_VERSION
    assert fields["operation_id"] and len(fields["operation_id"]) == 8
    assert int(fields["elapsed_ms"]) >= 0


def test_restore_writes_its_own_line() -> None:
    signal = FakeSignal(loaded=False)
    controller, lines = _controller(signal)
    controller.stop()

    controller.restore()

    assert len(lines) == 2
    fields = _parse(lines[1])
    assert (fields["action"], fields["result"]) == ("restore", "ok")
    assert (fields["state_before"], fields["state_after"]) == ("stopped", "running")


def test_failed_action_logs_error_code_as_result() -> None:
    signal = FakeSignal()
    signal.unload_error = lifecycle.UnloadFailed("boom", discarded=True)
    controller, lines = _controller(signal)

    with pytest.raises(lifecycle.LifecycleError):
        controller.stop()

    fields = _parse(lines[0])
    assert fields["result"] == lifecycle.E_UNLOAD_FAILED
    assert fields["state_after"] == "stopped", "失败也要如实记录落点"


def test_late_completion_writes_late_complete_line_with_same_id() -> None:
    """超时返回后动作最终完成：补写同 operation_id 的收尾行（TR-002）。"""
    signal = FakeSignal()
    signal.unload_delay = 0.3
    controller, lines = _controller(signal, stop_timeout_s=0.05)

    with pytest.raises(lifecycle.LifecycleError) as excinfo:
        controller.stop()
    assert excinfo.value.code == lifecycle.E_TIMEOUT

    operation_id = controller.status()["operation"]["id"]
    controller.wait_idle(timeout=5)

    assert len(lines) == 1, "超时本身不写行——行由动作的真实落点写"
    fields = _parse(lines[0])
    assert fields["result"] == "late_complete"
    assert fields["operation_id"] == operation_id, "收尾行必须能与超时的那次动作对上"
    assert fields["state_after"] == "stopped"


def test_log_line_carries_no_host_paths_or_credentials() -> None:
    """TR-003：行内不得出现主机路径、凭据或连接串。"""
    signal = FakeSignal(device="cuda:0")
    controller, lines = _controller(signal)

    controller.stop()

    line = lines[0]
    for forbidden in ("/home/", "/app/models", "password", "postgres://", "DB_PASSWORD", "@"):
        assert forbidden not in line, f"日志行泄露了 {forbidden!r}: {line}"


def test_vram_readable_reflects_probe_outcome(monkeypatch) -> None:
    """读数不可得时 vram_readable=false——事后归因要分得清"没降"与"读不到"。

    显式注入不可得读数：本机是否有 GPU 不得影响结论（开发机/执行机同样判定）。
    """
    from alphamill.kronos_service import vram

    monkeypatch.setattr(
        vram,
        "probe",
        lambda **_: vram.VramReading(used_bytes=None, readable=False, source="unavailable"),
    )
    signal = FakeSignal(device="cuda:0")
    controller, lines = _controller(signal)

    controller.stop()

    fields = _parse(lines[0])
    assert fields["vram_readable"] == "False"
    assert fields["vram_bytes_after"] == "None"
