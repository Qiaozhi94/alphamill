"""F004 编排静态契约（unit，CI 常绿）。

对应 spec FR-001 / NFR-001、design §2：
- Dockerfile 拆 mock（保持现状、不含 torch）与 real（锁定 design §2 依赖 pin）两个构建目标；
- compose 增 kronos-signal-real 服务（profiles: [kronos-real]）：real 目标、只读挂载、
  8002:8001、KRONOS_* 与 DB_* 环境、healthy 依赖、alphamill 网络、失败不重启、
  healthcheck 以 model_loaded=true 为通过条件；kronos-signal 显式 target: mock；
- 默认隔离：未启用 profile 时默认编排不启动也不构建 real 服务。

断言逻辑抽成纯函数（assert_*），供本文件内的变异验证复用：对 compose/Dockerfile
文本做变异（改 target、删 pin、放开 :ro、删 DB 依赖）后重跑，必须判红。
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = ROOT / "deployment/kronos-service.Dockerfile"
COMPOSE_PATH = ROOT / "deployment/docker-compose.yml"

# design §2 锁定的 real 目标依赖 pin（与宿主 AC-006 实测集一致）
REAL_PIN_LINES = (
    "torch==2.14.0",
    "--index-url https://download.pytorch.org/whl/cpu",
    "einops==0.8.2",
    "safetensors==0.8.0",
    "huggingface_hub==1.31.0",
    "tqdm==4.70.0",
)

SERVICE_KEY_RE = re.compile(r"^  ([a-z][a-z0-9-]*):\n", re.M)


def _service_block(compose: str, service: str) -> str:
    """截取某服务的 compose 块：从服务键到下一个同级键（或文件尾）。"""
    start = compose.index(f"\n  {service}:\n") + 1
    nxt = SERVICE_KEY_RE.search(compose[start + len(service) + 3 :])
    end = start + len(service) + 3 + nxt.start() if nxt else len(compose)
    return compose[start:end]


def _strip_comments(text: str) -> str:
    return re.sub(r"(?m)#.*$", "", text)


def assert_real_dockerfile_contract(dockerfile: str) -> None:
    """real 构建目标契约：mock 基座不含 torch；real 从 mock 派生并锁定依赖 pin。"""
    assert re.search(r"^FROM python:3\.11-slim AS mock$", dockerfile, re.M), (
        "Dockerfile 必须有 python:3.11-slim 基座的 mock 目标"
    )
    assert "FROM mock AS real" in dockerfile, "real 目标必须从 mock 派生（默认镜像行为不变）"
    mock_stage, _, real_stage = (
        _strip_comments(part) for part in dockerfile.partition("FROM mock AS real")
    )
    assert "torch" not in mock_stage, "mock 目标（默认镜像）不得安装 torch（NFR-001）"
    for pin in REAL_PIN_LINES:
        assert pin in real_stage, f"real 目标缺少依赖 pin: {pin}"


def test_dockerfile_targets_pin_real_dependencies() -> None:
    assert_real_dockerfile_contract(DOCKERFILE_PATH.read_text(encoding="utf-8"))
