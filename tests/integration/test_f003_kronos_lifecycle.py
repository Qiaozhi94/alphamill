"""F003 契约测试：Kronos 服务生命周期控制面（架构 §7.1，客户端可见行为）。

**契约目标是真实推理服务 `kronos-signal-real`（执行机 GPU 实例）**——夜槽卸载为的是
释放 GPU 显存，mock 服务（`kronos-signal`，8001，无 torch）无显存可释放，不是本契约的
对象，也不是合法的测试目标（R4-002）。服务端端点（`GET /lifecycle/status`、
`POST /lifecycle/stop`、`POST /lifecycle/restore`）属待分配 feature（BACKLOG「Kronos
服务生命周期端点」）——本文件以 `xfail(strict=True)` 显式声明当前「服务端未实现」的
先红态：端点落地后 XPASS 即红，落地 feature 必须移除本标记并补 `E_BUSY` / `E_TIMEOUT`
错误路径用例（F004 tasks §5）。

开关纪律（双保险，缺一即 skip）：
- 未设 `ALPHAMILL_INTEGRATION` → skip（与 F004 容器套件同纪律）；
- 未设 `KRONOS_CONTROL_URL` → skip（**无默认地址**：契约目标必须显式指定，避免默认
  打到 mock 的 404 上制造假红/假绿；T033 的 verify 命令给出执行机取值）。
设了以后失败就是失败（当前被 strict xfail 吸收为 xfailed，即预期红）。**404 / 连接
拒绝不构成契约通过**：「端点未实现」正是先红态本身，任何用例不得把它解释成服务端
行为合法。

断言对象是架构 §7.1 的客户端可见契约：字段面（含 `device`）、幂等性、显存确认与版本
协商。F003 客户端（`gpu_slot` 生命周期客户端，tasks T025）自身的行为——`offload_not_needed`
与 fail-closed 的观测归类（架构 §7.1 观测→处置决策表）、FIFO 等待——由其单元测试覆盖，
不在此文件。
"""

from __future__ import annotations

import os

import pytest
import requests

CONTRACT_VERSION = "1"

# 客户端超时取契约默认值：status 5s / stop 60s / restore 120s（可配项的缺省档）。
TIMEOUT_STATUS, TIMEOUT_STOP, TIMEOUT_RESTORE = 5, 60, 120

pytestmark = [
    pytest.mark.integration,
    pytest.mark.xfail(
        strict=True,
        reason="服务端控制面端点属待分配 feature（BACKLOG「Kronos 服务生命周期端点」）；"
        "端点落地后 XPASS 即红，须移除本标记（F004 tasks §5）",
    ),
]

INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}
CONTROL_URL = os.getenv("KRONOS_CONTROL_URL", "").strip().rstrip("/")


def _require_ready() -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("生命周期契约测试需 ALPHAMILL_INTEGRATION=1 并在执行机取证（SOP §3）")
    if not CONTROL_URL:
        pytest.skip(
            "未设 KRONOS_CONTROL_URL：契约目标是 kronos-signal-real（执行机 GPU 实例），"
            "必须显式指定，不打 mock（架构 §7.1）"
        )


def _headers(version: str = CONTRACT_VERSION) -> dict[str, str]:
    return {"X-Contract-Version": version}


def _status() -> dict:
    resp = requests.get(
        f"{CONTROL_URL}/lifecycle/status", headers=_headers(), timeout=TIMEOUT_STATUS
    )
    resp.raise_for_status()
    return resp.json()


def test_stop_restore_contract() -> None:
    """字段面 + 停止/恢复往返 + 显存确认（架构 §7.1 动作表）。"""
    _require_ready()
    before = _status()
    assert before["state"] in {"running", "stopped"}
    for field in ("contract_version", "model_loaded", "vram_bytes", "device"):
        assert field in before, f"status 响应缺字段 {field}"

    stop = requests.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    stop.raise_for_status()
    stopped = stop.json()
    assert stopped["state"] == "stopped"
    assert isinstance(stopped["vram_bytes"], int)

    # 显存确认：编排必须经 status 的 vram_bytes 确认释放后才能取锁训练。
    after = _status()
    assert after["state"] == "stopped"
    assert isinstance(after["vram_bytes"], int) and after["vram_bytes"] >= 0

    restore = requests.post(
        f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
    )
    restore.raise_for_status()
    assert restore.json()["state"] == "running"
    assert _status()["state"] == "running"


def test_stop_restore_idempotent() -> None:
    """重复 stop 返回 state=stopped 不报错；重复 restore 返回 state=running。"""
    _require_ready()
    first = requests.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    first.raise_for_status()
    second = requests.post(
        f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP
    )
    second.raise_for_status()
    assert second.json()["state"] == "stopped"

    requests.post(f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE)
    again = requests.post(
        f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
    )
    again.raise_for_status()
    assert again.json()["state"] == "running"


def test_unsupported_contract_version_rejected() -> None:
    """版本不匹配 → 错误信封 `{"error": "E_UNSUPPORTED_VERSION"}`（契约 §7.1）。

    只认错误码信封，不认 HTTP 状态码：把 404 当「拒绝」会让端点未实现的现状
    假性通过（实测 mock 404 → XPASS strict 红），门禁等于没牙。
    """
    _require_ready()
    resp = requests.get(
        f"{CONTROL_URL}/lifecycle/status", headers=_headers("999"), timeout=TIMEOUT_STATUS
    )
    assert resp.json().get("error") == "E_UNSUPPORTED_VERSION", (
        f"不支持的契约版本未被按契约拒绝：{resp.status_code} {resp.text[:200]}"
    )
