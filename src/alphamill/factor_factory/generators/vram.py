"""设备侧显存探测（不查 GPU 进程列表——WSL2 下 nvidia-smi 不列出进程）。"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class VramReading:
    total_gb: float
    free_gb: float


def query_vram() -> VramReading | None:
    """Read the first NVIDIA GPU without consulting process listings."""
    try:
        output = subprocess.run(
            (
                "nvidia-smi",
                "--query-gpu=memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ),
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        total, free = output.splitlines()[0].split(",", maxsplit=1)
        return VramReading(total_gb=float(total) / 1024, free_gb=float(free) / 1024)
    except (IndexError, OSError, subprocess.SubprocessError, ValueError):
        return None


def vram_is_sufficient(reading: VramReading | None, *, limit_gb: float) -> bool:
    """读数缺失不是"够用"的证据——architecture §7.1 队列赢，绝不并行赌 OOM。"""
    return reading is not None and reading.free_gb >= limit_gb
