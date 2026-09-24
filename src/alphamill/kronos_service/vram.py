"""设备侧显存探测（F009 FR-007 / NFR-005）。

口径是**整卡已用字节**，与架构 §7.1 决策表第三行的回落探测同源。顺序为
`torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used` → 不可得；
**不查 GPU 进程列表**——WSL2 下 `nvidia-smi` 不列出 GPU 进程，按进程求和会恒为 0。

读数不可得不是错误：调用方以 `readable=false` + `used_bytes=None` 如实表达，
status 仍是成功响应（spec FR-001）。
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import dataclass

MIB = 1024 * 1024
NVIDIA_SMI_CMD = [
    "nvidia-smi",
    "--query-gpu=memory.used",
    "--format=csv,noheader,nounits",
]

UNREADABLE_REASON_NO_BUDGET = "budget_exhausted"


@dataclass(frozen=True)
class VramReading:
    used_bytes: int | None
    readable: bool
    source: str  # torch | nvidia_smi | cpu | unavailable


def _from_torch(torch_module) -> VramReading | None:
    try:
        free, total = torch_module.cuda.mem_get_info()
        return VramReading(used_bytes=int(total) - int(free), readable=True, source="torch")
    except Exception:
        return None


def _from_nvidia_smi(runner: Callable, timeout_s: float) -> VramReading | None:
    try:
        proc = runner(NVIDIA_SMI_CMD, capture_output=True, text=True, timeout=timeout_s)
    except Exception:  # 包含 TimeoutExpired 与「找不到可执行文件」
        return None
    if getattr(proc, "returncode", 1) != 0:
        return None
    try:
        used_mib = int(str(proc.stdout).strip().splitlines()[0].strip())
    except (ValueError, IndexError):
        return None
    return VramReading(used_bytes=used_mib * MIB, readable=True, source="nvidia_smi")


def _import_torch():
    try:  # 惰性导入：mock 镜像不含 torch，控制面不得因此不可达（NFR-001）
        import torch

        return torch
    except Exception:
        return None


def probe(
    *,
    device: str,
    mode: str,
    probe_timeout_s: float,
    budget_s: float,
    torch_module=None,
    smi_runner: Callable = subprocess.run,
) -> VramReading:
    """探测设备侧已用显存。

    `budget_s` 是调用方（status）剩余的处理预算：子进程超时取它与 `probe_timeout_s`
    的较小者，预算耗尽则直接判不可得——status 的 deadline 优先于拿到读数。
    """
    if device == "cpu" or device.startswith("cpu:"):
        # 无 CUDA 实例：语义完整，读数是确定的 0 而非"不可得"（spec §3 边界场景 /
        # NFR-005：device=cpu 时 vram_bytes=0、vram_readable=true）。
        return VramReading(used_bytes=0, readable=True, source="cpu")

    if not device.startswith("cuda"):
        # 既不是 cuda 也不是 cpu（空串、unknown、mps…）：**不得**假装是 CPU 实例报 0，
        # 那是编造读数——"读不到"与"确实是 0"在编排侧的处置完全不同（R2-003）。
        return VramReading(used_bytes=None, readable=False, source="unknown_device")

    if budget_s <= 0:
        return VramReading(used_bytes=None, readable=False, source="unavailable")

    if mode in ("auto", "torch"):
        torch_module = torch_module if torch_module is not None else _import_torch()
        reading = _from_torch(torch_module) if torch_module is not None else None
        if reading is not None:
            return reading
        if mode == "torch":  # 单一来源模式不跨源回退（FR-007）
            return VramReading(used_bytes=None, readable=False, source="unavailable")

    if mode in ("auto", "nvidia_smi"):
        reading = _from_nvidia_smi(smi_runner, min(probe_timeout_s, budget_s))
        if reading is not None:
            return reading

    return VramReading(used_bytes=None, readable=False, source="unavailable")
