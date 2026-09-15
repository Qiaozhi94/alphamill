"""F004 容器集成：`--profile kronos-real` 拉起真实推理实例（执行机取证）。

对应 spec AC-001 / AC-002 容器集成层（design §8）：
- 容器身份：compose 托管 + real 构建目标（容器内 torch 可导入）+ 只读挂载 + 8002:8001；
- 完整运行链（模型 + TimescaleDB）：/health 的 database 可达、model_enabled=true、
  /predict 返回 source=kronos；
- 失败关闭：缺资产实例非零退出并在日志保留缺失路径，不产生可服务的 mock 降级实例；
- 默认镜像否证：mock 目标镜像 `import torch` 判红（NFR-001）。

开关语义与 F001 冒烟一致：未设 `ALPHAMILL_INTEGRATION` 时 skip；设了而 docker/栈
不可达判红，不得以 skip 代替证据。前置：vendor/Kronos 与 models/ 就位（F001 流程）、
DB 已迁移且目标 exchange/symbol ≥30 根已闭合 1m K 线。

取证纪律：容器与集成证据必须在执行机采集（SOP §3 / 架构 §7.1）；开发机 skip 不算
证据。验收时记录本机 hostname 与 /health 的 device=cpu。
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from collections.abc import Iterator

import pytest
import requests

COMPOSE_BASE = ["docker", "compose", "-f", "deployment/docker-compose.yml"]
COMPOSE_PROFILE = [*COMPOSE_BASE, "--profile", "kronos-real"]
REAL_CONTAINER = "quant-kronos-signal-real"
BASE_URL = "http://127.0.0.1:8002"

pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}

POLL_SECONDS = 300  # CPU 上 torch 导入 + 391MB 权重加载的首启窗口


def _require_integration(reason_unavailable: str | None = None) -> None:
    if not INTEGRATION_REQUIRED:
        pytest.skip("容器集成需 ALPHAMILL_INTEGRATION=1 并在执行机取证（SOP §3）")
    if reason_unavailable:
        pytest.fail(reason_unavailable)


def _run(cmd: list[str], timeout: int | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _inspect(container: str) -> dict:
    proc = _run(["docker", "inspect", container])
    assert proc.returncode == 0, f"容器不存在或 docker 不可达: {proc.stderr}"
    return json.loads(proc.stdout)[0]


def _wait_for_real_model() -> dict:
    """轮询 /health 直到模型加载完成（uvicorn 在 lifespan 完成前不监听端口）。

    截止时刻用 time.monotonic() 计算：请求耗时不得挤掉轮询窗口——固定步长递减
    会把实际等待拉到最多约 2×POLL_SECONDS（F004-Q003）。
    """
    deadline = time.monotonic() + POLL_SECONDS
    last_error: str | None = None
    while time.monotonic() < deadline:
        try:
            resp = requests.get(f"{BASE_URL}/health", timeout=5)
            if resp.status_code == 200:
                health = resp.json()
                if health.get("model_loaded"):
                    return health
                last_error = f"model_loaded=false: {health.get('model_error')}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(5)
    pytest.fail(f"real 实例 {POLL_SECONDS}s 内未就绪: {last_error}")


def _compose_image(compose_cmd: list[str], service: str) -> str:
    """按 compose 默认命名（<project>-<service>:latest）解析镜像名。

    不能用容器 .Image / compose images -q 的镜像 ID：buildkit 每次构建都会生成
    新的 manifest list（ID 随变），重建后旧 ID 被取消标签，docker run 不认。
    """
    cfg = _run([*compose_cmd, "config", "--format", "json"], timeout=60)
    assert cfg.returncode == 0, cfg.stderr
    project = json.loads(cfg.stdout)["name"]
    return f"{project}-{service}:latest"


@pytest.fixture(scope="module")
def real_profile() -> Iterator[dict]:
    """构建 real 目标并拉起 profile 实例；teardown 只清 real 容器，不动共享栈。"""
    _require_integration()
    info = _run(["docker", "info"], timeout=30)
    if info.returncode != 0:
        _require_integration(f"ALPHAMILL_INTEGRATION=1 但 docker 不可达: {info.stderr}")

    built = _run([*COMPOSE_PROFILE, "build", "kronos-signal-real"], timeout=1800)
    assert built.returncode == 0, f"real 镜像构建失败: {built.stderr[-2000:]}"

    up = _run([*COMPOSE_PROFILE, "up", "-d", "kronos-signal-real"], timeout=300)
    assert up.returncode == 0, f"profile 拉起失败: {up.stderr[-2000:]}"

    yield {}

    _run([*COMPOSE_PROFILE, "rm", "-sf", "kronos-signal-real"], timeout=120)


def test_real_profile_container_identity_and_full_chain(real_profile) -> None:
    """AC-001：容器身份成立，且完整运行链（模型 + TimescaleDB）可用。"""
    info = _inspect(REAL_CONTAINER)
    labels = info["Config"]["Labels"]
    assert labels.get("com.docker.compose.service") == "kronos-signal-real"
    assert labels.get("com.docker.compose.project"), "实例必须由 compose 托管"

    mounts = {(m["Destination"], m["RW"]): m["Source"] for m in info["Mounts"]}
    assert mounts.get(("/app/vendor/Kronos", False), "").endswith("/vendor/Kronos")
    assert mounts.get(("/app/models", False), "").endswith("/models")

    port_map = info["NetworkSettings"]["Ports"]["8001/tcp"]
    assert any(binding["HostPort"] == "8002" for binding in port_map), port_map

    env = "\n".join(info["Config"]["Env"])
    assert "KRONOS_USE_REAL_MODEL=true" in env
    assert "KRONOS_REPO_PATH=/app/vendor/Kronos" in env
    assert "KRONOS_DEVICE=cpu" in env

    # real 目标身份：容器内 torch 可导入（mock 目标做不到，见默认镜像否证用例）
    torch_import = _run(
        [
            "docker",
            "exec",
            REAL_CONTAINER,
            "python",
            "-c",
            "import torch; print(torch.__version__)",
        ],
        timeout=120,
    )
    assert torch_import.returncode == 0, torch_import.stderr
    print(f"\n[evidence] hostname={socket.gethostname()} torch={torch_import.stdout.strip()}")

    health = _wait_for_real_model()
    assert health["model_enabled"] is True
    assert health["device"] == "cpu"
    assert health["database"]["total_rows"] > 0, f"DB 运行链不可用: {health['database']}"

    predict = requests.get(
        f"{BASE_URL}/predict/BTC/USDT", params={"exchange": "binance"}, timeout=120
    )
    assert predict.status_code == 200, predict.text[:300]
    payload = predict.json()
    assert payload["source"] == "kronos", payload
    assert payload["model"] == "/app/models/Kronos-base", payload
    assert payload["rows_used"] >= 30, payload
    print(f"[evidence] /predict source={payload['source']} reason={payload['reason']}")


def test_missing_assets_fail_closed(real_profile) -> None:
    """AC-002：缺资产实例启动即非零退出并打印缺失路径；不产生可服务的 mock 降级。"""
    _require_integration()
    image = _compose_image(COMPOSE_PROFILE, "kronos-signal-real")
    container = "f004-missing-assets"

    # 与 compose real 服务同一运行语义（KRONOS_USE_REAL_MODEL=true），仅把资产路径
    # 指向不存在处——等价于「新 clone 缺 vendor/models 就启用 profile」的失败关闭。
    # 不用 --rm：保留容器以便 inspect 失败态（exited + 非零退出码）而非只看日志；
    # 若发生 mock 降级，docker run 会挂着不退（TimeoutExpired）——同样判红（F004-Q004）。
    try:
        proc = _run(
            [
                "docker",
                "run",
                "--name",
                container,
                "-e",
                "KRONOS_USE_REAL_MODEL=true",
                "-e",
                "KRONOS_REPO_PATH=/nonexistent/vendor/Kronos",
                "-e",
                "KRONOS_MODEL_PATH=/nonexistent/models/Kronos-base",
                "-e",
                "KRONOS_TOKENIZER_PATH=/nonexistent/models/Kronos-Tokenizer-base",
                image,
            ],
            timeout=300,
        )
        output = proc.stdout + proc.stderr
        assert proc.returncode != 0, f"缺资产实例未失败关闭: returncode={proc.returncode}"
        assert "/nonexistent/vendor/Kronos" in output
        assert "refusing to start" in output

        state = _run(
            ["docker", "inspect", "-f", "{{.State.Status}}|{{.State.ExitCode}}", container]
        )
        assert state.returncode == 0, state.stderr
        status_name, _, exit_code = state.stdout.strip().partition("|")
        assert status_name == "exited", f"失败关闭实例必须 exited（非 running）: {state.stdout}"
        assert int(exit_code) != 0, f"失败关闭实例退出码必须非零: {state.stdout}"
    finally:
        _run(["docker", "rm", "-f", container], timeout=60)


def test_default_mock_image_has_no_torch(real_profile) -> None:
    """AC-001/NFR-001 否证：默认（mock 目标）镜像 import torch 必须失败。"""
    _require_integration()
    built = _run([*COMPOSE_BASE, "build", "kronos-signal"], timeout=1800)
    assert built.returncode == 0, f"mock 镜像构建失败: {built.stderr[-2000:]}"
    image_id = _compose_image(COMPOSE_BASE, "kronos-signal")

    proc = _run(
        ["docker", "run", "--rm", "--entrypoint", "python", image_id, "-c", "import torch"],
        timeout=120,
    )
    assert proc.returncode != 0, "默认镜像竟能 import torch——NFR-001 被破坏"


def test_default_compose_excludes_real_service() -> None:
    """F004-T004 回归：默认编排不含 kronos-signal-real（NFR-001）；带 profile 才含。

    静态门禁读文本；这里用 compose CLI 实际解析，双重覆盖（config 无需 daemon）。
    """
    _require_integration()
    default = _run([*COMPOSE_BASE, "config", "--services"], timeout=60)
    assert default.returncode == 0, default.stderr
    default_services = set(default.stdout.split())
    assert "kronos-signal-real" not in default_services, default_services
    assert "kronos-signal" in default_services, default_services

    profiled = _run([*COMPOSE_PROFILE, "config", "--services"], timeout=60)
    assert profiled.returncode == 0, profiled.stderr
    assert "kronos-signal-real" in set(profiled.stdout.split()), profiled.stdout
