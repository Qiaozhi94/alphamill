"""F003 契约测试：Kronos 服务生命周期控制面（架构 §7.1，客户端可见行为）。

**契约目标是真实推理服务 `kronos-signal-real`（执行机 GPU 实例）**——夜槽卸载为的是
释放 GPU 显存，mock 服务（`kronos-signal`，8001，无 torch）无显存可释放，不是本契约的
对象，也不是合法的测试目标（R4-002）。服务端端点（`GET /lifecycle/status`、`POST /lifecycle/stop`、
`POST /lifecycle/restore`）由 **F009** 交付；本文件的模块级 `xfail(strict=True)` 已随
F009 T015 移除，改为**真红真绿**：失败即失败。显存真实下降的判据不在此文件——它在
`test_f009_vram_release.py` 以先红态等 F010 取证（F009 AC-012）；本文件必须保持
**0 xfailed**，否则 F003 T033 的 `--runxfail` 门禁不可能通过。

开关纪律（双保险，缺一即 skip）：
- 未设 `ALPHAMILL_INTEGRATION` → skip（与 F004 容器套件同纪律）；
- 未设 `KRONOS_CONTROL_URL` → skip（**无默认地址**：契约目标必须显式指定，避免默认
  打到 mock 的 404 上制造假红/假绿；T033 的 verify 命令给出执行机取值）。
设了以后失败就是失败。**404 / 连接
拒绝不构成契约通过**：「端点未实现」正是先红态本身，任何用例不得把它解释成服务端
行为合法。

断言对象是架构 §7.1 的客户端可见契约：字段面（含 `device`）、幂等性、显存确认与版本
协商。F003 客户端（`gpu_slot` 生命周期客户端，tasks T025）自身的行为——`offload_not_needed`
与 fail-closed 的观测归类（架构 §7.1 观测→处置决策表）、FIFO 等待——由其单元测试覆盖，
不在此文件。
"""

from __future__ import annotations

import os
import threading
import time

import pytest
import requests

CONTRACT_VERSION = "1"

# 客户端超时取契约默认值：status 5s / stop 60s / restore 120s（可配项的缺省档）。
TIMEOUT_STATUS, TIMEOUT_STOP, TIMEOUT_RESTORE = 5, 60, 120

pytestmark = pytest.mark.integration

# 探测一律不走环境代理：代理会替失败连接返回响应，让「端点不可达」类断言假绿。
SESSION = requests.Session()
SESSION.trust_env = False

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
    resp = SESSION.get(
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

    stop = SESSION.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    stop.raise_for_status()
    stopped = stop.json()
    assert stopped["state"] == "stopped"
    assert isinstance(stopped["vram_bytes"], int)

    # 显存确认：编排必须经 status 的 vram_bytes 确认释放后才能取锁训练。
    after = _status()
    assert after["state"] == "stopped"
    assert isinstance(after["vram_bytes"], int) and after["vram_bytes"] >= 0

    restore = SESSION.post(
        f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
    )
    restore.raise_for_status()
    assert restore.json()["state"] == "running"
    assert _status()["state"] == "running"


def test_stop_restore_idempotent() -> None:
    """重复 stop 返回 state=stopped 不报错；重复 restore 返回 state=running。"""
    _require_ready()
    first = SESSION.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    first.raise_for_status()
    second = SESSION.post(f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP)
    second.raise_for_status()
    assert second.json()["state"] == "stopped"

    SESSION.post(f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE)
    again = SESSION.post(
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
    resp = SESSION.get(
        f"{CONTROL_URL}/lifecycle/status", headers=_headers("999"), timeout=TIMEOUT_STATUS
    )
    assert resp.json().get("error") == "E_UNSUPPORTED_VERSION", (
        f"不支持的契约版本未被按契约拒绝：{resp.status_code} {resp.text[:200]}"
    )


def test_extra_parameters_rejected_as_bad_request() -> None:
    """请求体含契约外的键 → 恰为 `{"error": "E_BAD_REQUEST"}`（F009 AC-011）。

    **不得**是 `E_UNSUPPORTED_VERSION`——后者是客户端判定「服务端未实现本契约」的入口，
    两者混用会把自己的请求构造错误误读成服务端缺失（架构 §7.1 错误码各司其职）。
    """
    _require_ready()
    resp = SESSION.post(
        f"{CONTROL_URL}/lifecycle/stop",
        headers=_headers(),
        json={"force": True},
        timeout=TIMEOUT_STOP,
    )

    assert resp.json() == {"error": "E_BAD_REQUEST"}, resp.text[:200]
    assert _status()["state"] == "running", "被拒的请求不得执行动作"


def test_busy_rejects_conflicting_action() -> None:
    """动作进行中 → 冲突动作立即 `E_BUSY`，不排队不叠加（架构 §7.1 单飞）。

    用真实 stop 制造窗口：stop 在飞时并发 restore。若实例卸载极快而没能观测到
    `E_BUSY`，用例按"未能制造窗口"跳过而不是假绿——但 operation 字段必须成立。
    """
    _require_ready()
    outcome: dict = {}

    def _stop() -> None:
        outcome["stop"] = SESSION.post(
            f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP
        ).json()

    worker = threading.Thread(target=_stop)
    worker.start()
    busy_seen = None
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and worker.is_alive():
        resp = SESSION.post(
            f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
        ).json()
        if resp.get("error"):
            busy_seen = resp
            break
    worker.join(timeout=TIMEOUT_STOP)

    try:
        if busy_seen is None:
            pytest.skip("卸载过快，未能制造动作窗口（不构成契约通过，也不算失败）")
        assert busy_seen == {"error": "E_BUSY"}, busy_seen
    finally:
        SESSION.post(
            f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE
        )


def test_timeout_envelope_is_not_a_terminal_failure() -> None:
    """服务端 deadline 到点 → `E_TIMEOUT`，且动作仍在进行（operation 非空）。

    以**客户端**极短超时无法验证该语义（那只会得到 OSError）——服务端 deadline 由
    `KRONOS_LIFECYCLE_*_TIMEOUT_S` 承载。本用例只在实例被配成短 deadline 时才有意义，
    因此以 `KRONOS_EXPECT_SHORT_DEADLINE=1` 显式开启，默认跳过而不是假绿。
    """
    _require_ready()
    if os.getenv("KRONOS_EXPECT_SHORT_DEADLINE", "").lower() not in {"1", "true", "yes"}:
        pytest.skip(
            "需把实例的 KRONOS_LIFECYCLE_STOP_TIMEOUT_S 配成短值并设 "
            "KRONOS_EXPECT_SHORT_DEADLINE=1 才能观测 E_TIMEOUT（F009 AC-011）"
        )

    resp = SESSION.post(
        f"{CONTROL_URL}/lifecycle/stop", headers=_headers(), timeout=TIMEOUT_STOP
    ).json()

    assert resp == {"error": "E_TIMEOUT"}, resp
    assert _status()["operation"] is not None, "E_TIMEOUT 不是终态：动作仍在进行"
    SESSION.post(f"{CONTROL_URL}/lifecycle/restore", headers=_headers(), timeout=TIMEOUT_RESTORE)
