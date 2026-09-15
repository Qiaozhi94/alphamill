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

import pytest

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
    """截取某服务的 compose 块：从服务键到下一个同级键（或文件尾）。

    先剥离整行注释再切块：整行注释掉关键行后断言不得再从注释文本读到子串，且
    下一服务的前置注释不并入上一块（F004 检视 T001/Q002 回归——门禁读语义，
    不读裸文本）。
    """
    stripped = _strip_comments(compose)
    start = stripped.index(f"\n  {service}:\n") + 1
    nxt = SERVICE_KEY_RE.search(stripped[start + len(service) + 3 :])
    end = start + len(service) + 3 + nxt.start() if nxt else len(stripped)
    return stripped[start:end]


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


def assert_compose_real_service_contract(compose: str) -> None:
    """compose 双服务契约：kronos-signal 显式 mock；kronos-signal-real 全量接线。"""
    mock_block = _service_block(compose, "kronos-signal")
    assert "target: mock" in mock_block, (
        "kronos-signal 必须显式 target: mock（无 target 的默认构建会取最后一个 stage=real）"
    )
    # mock 的 real 开关必须钉死（C001）：保留 ${KRONOS_USE_REAL_MODEL} 覆盖时，
    # .env 误置 true 会让默认服务预检失败、再被 unless-stopped 拉成无限重启。
    assert 'KRONOS_USE_REAL_MODEL: "false"' in mock_block
    assert "${KRONOS_USE_REAL_MODEL" not in mock_block

    real_block = _service_block(compose, "kronos-signal-real")
    # profile 与构建目标
    assert "profiles: [kronos-real]" in real_block, "real 服务必须挂在 kronos-real profile 下"
    assert "target: real" in real_block
    # 只读挂载（vendor clone + 权重，容器不写宿主资产）
    assert "../vendor/Kronos:/app/vendor/Kronos:ro" in real_block
    assert "../models:/app/models:ro" in real_block
    # KRONOS_* 运行时环境（design §2）
    assert 'KRONOS_USE_REAL_MODEL: "true"' in real_block
    assert "KRONOS_REPO_PATH: /app/vendor/Kronos" in real_block
    assert "KRONOS_MODEL_PATH: /app/models/Kronos-base" in real_block
    assert "KRONOS_TOKENIZER_PATH: /app/models/Kronos-Tokenizer-base" in real_block
    assert "KRONOS_DEVICE: cpu" in real_block
    # DB 接线与 mock 服务同约定
    assert "DB_HOST: timescaledb" in real_block
    assert "DB_PORT: 5432" in real_block
    assert "DB_USER: ${DB_USER:-quant}" in real_block
    assert "DB_PASSWORD: ${DB_PASSWORD:-change-me}" in real_block
    assert "DB_NAME: ${DB_NAME:-quant}" in real_block
    # 依赖、网络、端口、失败语义与 readiness
    assert "timescaledb: {condition: service_healthy}" in real_block
    assert "networks: [alphamill]" in real_block
    assert '- "8002:8001"' in real_block
    assert 'restart: "no"' in real_block, "real 服务失败不得自动重启（失败态保持可见）"
    assert "model_loaded') is True" in real_block and "device') == 'cpu'" in real_block, (
        "healthcheck 必须以 /health 的 model_loaded=true（且 device=cpu）为通过条件"
    )


def test_compose_real_service_contract() -> None:
    assert_compose_real_service_contract(COMPOSE_PATH.read_text(encoding="utf-8"))


def test_default_compose_stays_mock_only() -> None:
    """默认隔离（NFR-001）：real 服务必须挂 profile，mock 服务不得背权重挂载。"""
    compose = COMPOSE_PATH.read_text(encoding="utf-8")
    real_block = _service_block(compose, "kronos-signal-real")
    assert "profiles: [kronos-real]" in real_block, "real 服务必须挂 kronos-real profile"
    mock_block = _service_block(compose, "kronos-signal")
    assert "profiles" not in mock_block
    assert "/app/vendor/Kronos" not in mock_block, "默认服务不得挂载权重/vendor"


def test_service_block_never_reads_next_service_comments() -> None:
    """F004-Q002 回归：下一服务的前置注释不得并入上一块参与断言。

    kronos-signal-real 的前置注释叙述里含 `--profile kronos-real`、`restart: "no"`
    等文本；若切块把注释算进来，默认隔离断言实际核对的是注释而非配置。
    """
    compose = COMPOSE_PATH.read_text(encoding="utf-8")
    mock_block = _service_block(compose, "kronos-signal")
    assert "--profile kronos-real" not in mock_block
    assert 'restart: "no"' not in mock_block


def _mutate(text: str, old: str, new: str) -> str:
    assert old in text, f"变异基准串不存在（上游改动后需同步变异用例）: {old}"
    return text.replace(old, new)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("FROM mock AS real", "FROM python:3.11-slim AS real"),  # 改派生关系
        ("torch==2.14.0", "torch==9.9.9"),  # 改 torch pin
        ("--index-url https://download.pytorch.org/whl/cpu", ""),  # 删 CPU wheel index
        ("einops==0.8.2", ""),  # 删 einops pin
        ("huggingface_hub==1.31.0", ""),  # 删 huggingface_hub pin
    ],
)
def test_dockerfile_mutations_fail_the_gate(old: str, new: str) -> None:
    """变异验证：Dockerfile 契约被破坏时门禁必须判红（design §8）。"""
    mutated = _mutate(DOCKERFILE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_real_dockerfile_contract(mutated)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("      target: real\n", "      target: mock\n"),  # 改 real 服务的构建目标
        ("../vendor/Kronos:/app/vendor/Kronos:ro", "../vendor/Kronos:/app/vendor/Kronos"),
        ("../models:/app/models:ro", "../models:/app/models"),  # 放开 models 只读
        ("DB_HOST: timescaledb", "DB_HOST: localhost"),  # 破坏 DB 接线
        ("timescaledb: {condition: service_healthy}", "timescaledb"),  # 删 healthy 依赖
        ("profiles: [kronos-real]\n", ""),  # 删 profile（real 变默认启动，破坏 NFR-001）
        ('restart: "no"', "restart: unless-stopped"),  # 破坏失败可见语义
        ('- "8002:8001"', '- "8001:8001"'),  # 端口顶替默认实例
        # F004-T001 回归：整行注释掉关键行必须判红——门禁读语义文本，不读裸子串
        ("profiles: [kronos-real]\n", "# profiles: [kronos-real]\n"),  # 注释掉 profile
        ("target: real\n", "# target: real\n"),  # 注释掉构建目标
        (
            "- ../vendor/Kronos:/app/vendor/Kronos:ro",
            "# - ../vendor/Kronos:/app/vendor/Kronos:ro",
        ),  # 注释掉只读挂载
        ('restart: "no"', '# restart: "no"'),  # 注释掉失败不重启
        # F004-C001 回归：mock 服务恢复 .env 覆盖开关必须判红
        (
            'KRONOS_USE_REAL_MODEL: "false"',
            "KRONOS_USE_REAL_MODEL: ${KRONOS_USE_REAL_MODEL:-false}",
        ),
    ],
)
def test_compose_mutations_fail_the_gate(old: str, new: str) -> None:
    """变异验证：compose 契约被破坏时门禁必须判红（design §8）。"""
    mutated = _mutate(COMPOSE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_compose_real_service_contract(mutated)
