"""F009 显存探测与配置契约（unit，CI 常绿，不需要 GPU）。

对应 spec FR-007 / NFR-005 与 AC-007、design §4/§7：
- 探测顺序 `torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used` → 不可得，
  **不查 GPU 进程列表**（WSL2 下 nvidia-smi 不列出进程）；
- `KRONOS_VRAM_PROBE_MODE` 的三个合法值逐个生效，单一来源模式失败即不可得、不跨源回退；
- 探测受 `KRONOS_VRAM_PROBE_TIMEOUT_S` 与调用方剩余预算的**较小者**约束，超时按读数不可得；
- 无 CUDA 实例（device=cpu）：`vram_bytes=0` + `vram_readable=true`；
- 五个环境变量的非法值一律启动期判红，不静默回退默认值。
"""

from __future__ import annotations

import subprocess
import types

import pytest

from alphamill.kronos_service import lifecycle_config, vram

MIB = 1024 * 1024


def _torch(*, free=None, total=None, raises=False, has_cuda=True):
    """假 torch：mem_get_info 返回 (free, total) 或抛错。"""

    def mem_get_info():
        if raises:
            raise RuntimeError("cuda unavailable")
        return (free, total)

    return types.SimpleNamespace(
        cuda=types.SimpleNamespace(mem_get_info=mem_get_info, is_available=lambda: has_cuda)
    )


def _smi(stdout="", returncode=0, timeout=False):
    """假 nvidia-smi 执行器：记录调用参数，供"不得查进程列表"断言复用。"""
    calls: list[list[str]] = []

    def runner(cmd, **kwargs):
        calls.append(list(cmd))
        if timeout:
            raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout", 0))
        return subprocess.CompletedProcess(cmd, returncode, stdout, "")

    runner.calls = calls  # type: ignore[attr-defined]
    return runner


def test_cpu_instance_reports_zero_and_readable() -> None:
    """无 CUDA 实例：读数是 0 且可读，不是"不可得"（spec §3 边界场景）。"""
    reading = vram.probe(device="cpu", mode="auto", probe_timeout_s=2.0, budget_s=5.0)

    assert reading.readable is True
    assert reading.used_bytes == 0


def test_auto_prefers_torch_mem_get_info() -> None:
    reading = vram.probe(
        device="cuda:0",
        mode="auto",
        probe_timeout_s=2.0,
        budget_s=5.0,
        torch_module=_torch(free=2 * MIB, total=8 * MIB),
        smi_runner=_smi(stdout="4096\n"),
    )

    assert reading.readable is True
    assert reading.used_bytes == 6 * MIB, "已用 = total - free（设备侧整卡口径）"


def test_auto_falls_back_to_nvidia_smi() -> None:
    runner = _smi(stdout="4096\n")
    reading = vram.probe(
        device="cuda:0",
        mode="auto",
        probe_timeout_s=2.0,
        budget_s=5.0,
        torch_module=_torch(raises=True),
        smi_runner=runner,
    )

    assert reading.readable is True
    assert reading.used_bytes == 4096 * MIB
    cmd = " ".join(runner.calls[0])  # type: ignore[attr-defined]
    assert "--query-gpu=memory.used" in cmd
    assert "--query-compute-apps" not in cmd, "不得依赖 GPU 进程列表（NFR-005）"


def test_auto_unreadable_when_both_sources_fail() -> None:
    reading = vram.probe(
        device="cuda:0",
        mode="auto",
        probe_timeout_s=2.0,
        budget_s=5.0,
        torch_module=_torch(raises=True),
        smi_runner=_smi(returncode=9),
    )

    assert reading.readable is False
    assert reading.used_bytes is None


@pytest.mark.parametrize(
    ("mode", "expect_smi_called"),
    [("torch", False), ("nvidia_smi", True)],
)
def test_single_source_mode_never_crosses_over(mode: str, expect_smi_called: bool) -> None:
    """单一来源模式：该来源失败即不可得，不跨源回退（FR-007）。"""
    runner = _smi(returncode=9)
    reading = vram.probe(
        device="cuda:0",
        mode=mode,
        probe_timeout_s=2.0,
        budget_s=5.0,
        torch_module=_torch(raises=True),
        smi_runner=runner,
    )

    assert reading.readable is False
    assert reading.used_bytes is None
    assert bool(runner.calls) is expect_smi_called  # type: ignore[attr-defined]


def test_nvidia_smi_mode_reads_value() -> None:
    reading = vram.probe(
        device="cuda:0",
        mode="nvidia_smi",
        probe_timeout_s=2.0,
        budget_s=5.0,
        torch_module=_torch(free=1, total=2),
        smi_runner=_smi(stdout="1024\n"),
    )

    assert (reading.readable, reading.used_bytes) == (True, 1024 * MIB)


def test_probe_timeout_is_min_of_budget_and_configured() -> None:
    """子进程超时取「配置值」与「调用方剩余预算」的较小者，status 不被探测拖过 deadline。"""
    seen: list[float] = []

    def runner(cmd, **kwargs):
        seen.append(kwargs["timeout"])
        return subprocess.CompletedProcess(cmd, 0, "1024\n", "")

    vram.probe(
        device="cuda:0",
        mode="nvidia_smi",
        probe_timeout_s=2.0,
        budget_s=0.5,
        smi_runner=runner,
    )
    vram.probe(
        device="cuda:0",
        mode="nvidia_smi",
        probe_timeout_s=2.0,
        budget_s=30.0,
        smi_runner=runner,
    )

    assert seen == [0.5, 2.0]


def test_probe_timeout_is_unreadable_not_error() -> None:
    reading = vram.probe(
        device="cuda:0",
        mode="nvidia_smi",
        probe_timeout_s=2.0,
        budget_s=5.0,
        smi_runner=_smi(timeout=True),
    )

    assert (reading.readable, reading.used_bytes) == (False, None)


def test_exhausted_budget_skips_probe_entirely() -> None:
    """剩余预算已耗尽：直接判读数不可得，不再发起探测（status 的 deadline 优先）。"""
    runner = _smi(stdout="1024\n")
    reading = vram.probe(
        device="cuda:0", mode="auto", probe_timeout_s=2.0, budget_s=0.0, smi_runner=runner
    )

    assert (reading.readable, reading.used_bytes) == (False, None)
    assert runner.calls == []  # type: ignore[attr-defined]


# --- 配置契约（FR-007 表逐行） -------------------------------------------------


def test_defaults_match_contract_table() -> None:
    cfg = lifecycle_config.load_config({})

    assert cfg.probe_mode == "auto"
    assert cfg.probe_timeout_s == 2.0
    assert cfg.status_timeout_s == 5.0
    assert cfg.stop_timeout_s == 60.0
    assert cfg.restore_timeout_s == 120.0


def test_env_overrides_are_honored() -> None:
    cfg = lifecycle_config.load_config(
        {
            "KRONOS_VRAM_PROBE_MODE": "nvidia_smi",
            "KRONOS_VRAM_PROBE_TIMEOUT_S": "1.5",
            "KRONOS_LIFECYCLE_STATUS_TIMEOUT_S": "9",
            "KRONOS_LIFECYCLE_STOP_TIMEOUT_S": "30",
            "KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S": "90",
        }
    )

    assert cfg.probe_mode == "nvidia_smi"
    assert (cfg.probe_timeout_s, cfg.status_timeout_s) == (1.5, 9.0)
    assert (cfg.stop_timeout_s, cfg.restore_timeout_s) == (30.0, 90.0)


@pytest.mark.parametrize(
    ("env", "culprit"),
    [
        ({"KRONOS_VRAM_PROBE_MODE": "gpu"}, "KRONOS_VRAM_PROBE_MODE"),
        ({"KRONOS_VRAM_PROBE_TIMEOUT_S": "0"}, "KRONOS_VRAM_PROBE_TIMEOUT_S"),
        ({"KRONOS_VRAM_PROBE_TIMEOUT_S": "abc"}, "KRONOS_VRAM_PROBE_TIMEOUT_S"),
        ({"KRONOS_LIFECYCLE_STATUS_TIMEOUT_S": "-1"}, "KRONOS_LIFECYCLE_STATUS_TIMEOUT_S"),
        ({"KRONOS_LIFECYCLE_STOP_TIMEOUT_S": "0"}, "KRONOS_LIFECYCLE_STOP_TIMEOUT_S"),
        ({"KRONOS_LIFECYCLE_STOP_TIMEOUT_S": "n/a"}, "KRONOS_LIFECYCLE_STOP_TIMEOUT_S"),
        ({"KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S": ""}, "KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S"),
        # 探测超时必须 ≤ status deadline（FR-007 值域），否则 status 会被探测拖过 deadline
        (
            {"KRONOS_VRAM_PROBE_TIMEOUT_S": "9", "KRONOS_LIFECYCLE_STATUS_TIMEOUT_S": "5"},
            "KRONOS_VRAM_PROBE_TIMEOUT_S",
        ),
    ],
)
def test_invalid_values_fail_at_startup_naming_the_variable(env: dict, culprit: str) -> None:
    """非法值一律判红并点名变量，不静默回退默认值（FR-007）。"""
    with pytest.raises(lifecycle_config.ConfigError) as excinfo:
        lifecycle_config.load_config(env)

    assert culprit in str(excinfo.value)


def test_unrelated_env_keys_are_ignored() -> None:
    cfg = lifecycle_config.load_config({"KRONOS_DEVICE": "cuda", "PATH": "/nope"})

    assert cfg.probe_mode == "auto"
