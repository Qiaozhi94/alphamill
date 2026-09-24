"""F009 AC-012 / F010 AC-009：显存真实下降（**先红态已由 F010 解除**）。

判据（架构 §7.1 显存确认条，逐字同源）：`stop` 后设备侧读数**真实下降**，
**且**卸载后整卡可用显存达到训练预算（`vram_limit_gb`，与单槽取锁同一阈值）。
只检查 `vram_bytes` 是合法整数的断言弱于成功声明——端点完全不释放显存也能通过。

**历史与所有权**：本载体由 F009 交付并以 `xfail(strict=True)` 标注先红态——当时仓内没有
任何 GPU Kronos 实例，判据不可能成立。F010 交付 GPU 基座后于 **2026-09-24** 在执行机
`qiaozhi-lt` 取到真实证据并解除该标记（F010 T011 / AC-009）：

    device=cuda:0  vram_before=1601699840  vram_after=1144520704
    free_after=7.53GB  budget=6.0GB      # RTX 4060 Laptop / 驱动 616.64

**为什么独立成文件**：放进 `test_f003_kronos_lifecycle.py` 会与 F003 T033 的
「该文件在 `--runxfail` 下 0 xfailed」门禁互相拆台（先红态按真失败计）。解除后本文件
仍独立——它需要 GPU 实例，与只需控制面语义的那批用例前置条件不同。

执行机取证：
    ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 \
      pytest -q tests/integration/test_f009_vram_release.py
"""

from __future__ import annotations

import os
import socket
import subprocess

import pytest
import requests

CONTRACT_VERSION = "1"
TIMEOUT_STATUS, TIMEOUT_STOP, TIMEOUT_RESTORE = 5, 60, 120

# 训练预算与单槽取锁同源（F003 `vram_limit_gb` 缺省 6.0）：不新增第二份配置，
# 未声明时不猜缺省值——猜出来的阈值会让"腾够了"这个结论不可追。
TRAINING_BUDGET_GB = float(os.getenv("KRONOS_TRAINING_BUDGET_GB", "6.0"))
GIB = 1024**3

pytestmark = pytest.mark.integration

SESSION = requests.Session()
SESSION.trust_env = False  # 代理会替失败连接返回响应，让显存断言假绿

INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}
CONTROL_URL = os.getenv("KRONOS_CONTROL_URL", "").strip().rstrip("/")


def _require_ready() -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("显存取证需 ALPHAMILL_INTEGRATION=1 并在执行机（SOP §3）")
    if not CONTROL_URL:
        pytest.skip("未设 KRONOS_CONTROL_URL：契约目标是 kronos-signal-real，不打 mock")


def _headers() -> dict[str, str]:
    return {"X-Contract-Version": CONTRACT_VERSION}


def _status() -> dict:
    resp = SESSION.get(
        f"{CONTROL_URL}/lifecycle/status", headers=_headers(), timeout=TIMEOUT_STATUS
    )
    resp.raise_for_status()
    return resp.json()


def _free_bytes() -> int | None:
    """整卡可用显存。不依赖 GPU 进程列表（WSL2 下不列出进程，NFR-005）。"""
    try:
        proc = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return None
    if proc.returncode != 0:
        return None
    return int(proc.stdout.strip().splitlines()[0]) * 1024 * 1024


def test_stop_releases_vram_to_training_budget() -> None:
    """判据：读数真实下降 **且** 卸载后整卡可用显存 ≥ 训练预算。"""
    _require_ready()
    before = _status()
    assert before["vram_readable"] is True, (
        "读数不可得时无法判定释放——这与'确实没释放'是两回事，须分别记账（FR-009）"
    )
    assert before["state"] == "running" and before["model_loaded"] is True
    vram_before = before["vram_bytes"]

    stop = SESSION.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    stop.raise_for_status()
    assert stop.json()["state"] == "stopped"

    try:
        after = _status()
        assert after["vram_readable"] is True
        vram_after = after["vram_bytes"]
        free_after = _free_bytes()

        assert vram_after < vram_before, (
            f"显存未真实下降：{vram_before} -> {vram_after}（端点声称已卸载）"
        )
        assert free_after is not None, "卸载后可用显存读不到，无法确认是否腾够训练预算"
        assert free_after >= TRAINING_BUDGET_GB * GIB, (
            f"降了但腾不出训练预算：可用 {free_after / GIB:.2f}GB < {TRAINING_BUDGET_GB}GB"
        )
        print(
            f"\n[evidence] hostname={socket.gethostname()} device={after['device']} "
            f"vram_before={vram_before} vram_after={vram_after} "
            f"free_after_gb={free_after / GIB:.2f} budget_gb={TRAINING_BUDGET_GB}"
        )
    finally:
        SESSION.post(
            f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
        )
