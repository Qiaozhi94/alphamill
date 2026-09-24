"""F009 部署面（mock 边界 + 暴露面），对应 spec AC-009 / IR-005 / NFR-001 / NFR-003。

三件事：
- **mock 不注册控制面**：`kronos-signal`（`KRONOS_USE_REAL_MODEL=false`）上 `/lifecycle/*`
  返回 404，客户端据此命中架构 §7.1 决策表第三行的回落探测；
- **默认镜像不含 torch**：F004 NFR-001 的否证断言保持绿——控制面的引入不得给默认镜像
  带进 torch 依赖（torch 相关导入一律惰性化）；
- **控制面不对外**：compose 把 real 实例端口绑 `127.0.0.1`，不发布到 `0.0.0.0`
  （NFR-003 以网络边界代替鉴权）。

前两项的 compose/镜像证据需 docker（`ALPHAMILL_INTEGRATION=1`，执行机取证）；
端口绑定是纯文本契约，CI 常绿。
"""

from __future__ import annotations

import os
import re
import socket
import subprocess
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = ROOT / "deployment/docker-compose.yml"
COMPOSE_BASE = ["docker", "compose", "-f", "deployment/docker-compose.yml"]
MOCK_BASE_URL = os.getenv("KRONOS_MOCK_URL", "http://127.0.0.1:8001")

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}

# 探测不走环境代理：代理会替失败连接返回响应，让 404/不可达断言假绿。
SESSION = requests.Session()
SESSION.trust_env = False


def _require_integration(reason: str | None = None) -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("部署集成需 ALPHAMILL_INTEGRATION=1 并在执行机取证（SOP §3）")
    if reason:
        pytest.fail(reason)


def _run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)


def _service_block(compose: str, service: str) -> str:
    stripped = re.sub(r"(?m)^[ \t]*#.*$", "", compose)
    start = stripped.index(f"\n  {service}:\n") + 1
    nxt = re.compile(r"^  ([a-z][a-z0-9-]*):\n", re.M).search(stripped[start + len(service) + 3 :])
    end = start + len(service) + 3 + nxt.start() if nxt else len(stripped)
    return stripped[start:end]


def assert_control_plane_not_published(compose: str) -> None:
    """控制面端口只在回环可达（NFR-003）；容器口仍是 8001，host 口仍是 8002。"""
    real_block = _service_block(compose, "kronos-signal-real")
    assert '- "127.0.0.1:8002:8001"' in real_block, (
        "real 实例必须绑 127.0.0.1（控制面能改变生产状态，不得发布到 0.0.0.0）"
    )
    assert not re.search(r'(?m)^\s+- "8002:8001"', real_block), "不得保留未绑定地址的发布形式"
    assert not re.search(r'(?m)^\s+- "0\.0\.0\.0:', real_block)
    mock_block = _service_block(compose, "kronos-signal")
    assert '- "8001:8001"' in mock_block, "mock 的 host 8001 不变（real 的 8002 不顶替它）"


def test_control_plane_port_is_loopback_only() -> None:
    assert_control_plane_not_published(COMPOSE_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('- "127.0.0.1:8002:8001"', '- "8002:8001"'),  # 退回未绑定地址
        ('- "127.0.0.1:8002:8001"', '- "0.0.0.0:8002:8001"'),  # 显式对外发布
        ('- "127.0.0.1:8002:8001"', '- "127.0.0.1:8001:8001"'),  # 顶替 mock 的 host 口
    ],
)
def test_port_mutations_fail_the_gate(old: str, new: str) -> None:
    compose = COMPOSE_PATH.read_text(encoding="utf-8")
    assert old in compose
    with pytest.raises(AssertionError):
        assert_control_plane_not_published(compose.replace(old, new, 1))


def test_env_example_documents_lifecycle_variables() -> None:
    """FR-007 五个变量在 .env.example 有名有值：迁移执行机只改配置。"""
    env_example = (ROOT / "deployment/.env.example").read_text(encoding="utf-8")
    for name in (
        "KRONOS_VRAM_PROBE_MODE",
        "KRONOS_VRAM_PROBE_TIMEOUT_S",
        "KRONOS_LIFECYCLE_STATUS_TIMEOUT_S",
        "KRONOS_LIFECYCLE_STOP_TIMEOUT_S",
        "KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S",
    ):
        assert re.search(rf"(?m)^{name}=", env_example), f".env.example 缺 {name}"


@pytest.mark.parametrize("path", ["status", "stop", "restore"])
def test_mock_instance_has_no_lifecycle_routes(path: str) -> None:
    """mock 上 /lifecycle/* 必须 404——契约明确 mock 不在范围（IR-005）。"""
    _require_integration()
    try:
        health = SESSION.get(f"{MOCK_BASE_URL}/health", timeout=5)
    except requests.RequestException as exc:
        _require_integration(f"mock 实例不可达（{MOCK_BASE_URL}）: {exc}")
    assert health.json()["model_enabled"] is False, "该实例不是 mock，取证目标选错了"

    method = SESSION.get if path == "status" else SESSION.post
    resp = method(
        f"{MOCK_BASE_URL}/lifecycle/{path}", headers={"X-Contract-Version": "1"}, timeout=5
    )

    assert resp.status_code == 404, f"mock 竟注册了控制面路由: {resp.status_code} {resp.text[:200]}"
    print(f"\n[evidence] hostname={socket.gethostname()} mock /lifecycle/{path} -> 404")


def test_default_image_still_has_no_torch() -> None:
    """NFR-001 否证：控制面的引入不得让默认（mock 目标）镜像带进 torch。"""
    _require_integration()
    built = _run([*COMPOSE_BASE, "build", "kronos-signal"], timeout=1800)
    assert built.returncode == 0, f"mock 镜像构建失败: {built.stderr[-2000:]}"
    cfg = _run([*COMPOSE_BASE, "config", "--format", "json"], timeout=60)
    assert cfg.returncode == 0, cfg.stderr
    import json

    image = f"{json.loads(cfg.stdout)['name']}-kronos-signal:latest"

    proc = _run(["docker", "run", "--rm", "--entrypoint", "python", image, "-c", "import torch"])

    assert proc.returncode != 0, "默认镜像竟能 import torch——NFR-001 被破坏"
    print(f"\n[evidence] hostname={socket.gethostname()} {image} import torch -> exit≠0")


def test_compose_config_keeps_loopback_binding() -> None:
    """compose CLI 实际解析的结果也必须是回环绑定（文本契约的双重覆盖）。"""
    _require_integration()
    cfg = _run([*COMPOSE_BASE, "--profile", "kronos-real", "config", "--format", "json"], 60)
    assert cfg.returncode == 0, cfg.stderr
    import json

    ports = json.loads(cfg.stdout)["services"]["kronos-signal-real"]["ports"]
    published = [(p.get("host_ip"), str(p.get("published"))) for p in ports]

    assert ("127.0.0.1", "8002") in published, published
