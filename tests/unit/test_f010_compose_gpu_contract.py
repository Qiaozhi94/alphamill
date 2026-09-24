"""F010 GPU 叠加层编排契约（unit，CI 常绿，纯文本断言，不依赖 docker 二进制）。

对应 spec FR-002 / FR-003 / NFR-001 / NFR-003 与 AC-002 / AC-003 / AC-005、design §4
override 文件契约表：
- GPU 面（独立镜像标签、CUDA 构建参数、`KRONOS_DEVICE: cuda`、nvidia × 1 设备预留、
  `startswith('cuda')` healthcheck）只出现在 `deployment/docker-compose.gpu.yml`；
- override 只覆盖 `kronos-signal-real`，不碰端口/卷/`restart`/`depends_on`，不用特权容器；
- 默认 compose 对 GPU 一无所知：`KRONOS_DEVICE: cpu`、无设备预留、无 GPU 变量插值、
  不设 `image:`（与 GPU 标签互不覆盖）。

断言抽成纯函数，供本文件的变异验证复用（沿用 F004 做法）。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = ROOT / "deployment/docker-compose.yml"
GPU_OVERRIDE_PATH = ROOT / "deployment/docker-compose.gpu.yml"

GPU_IMAGE = "alphamill/kronos-signal-real:gpu"
GPU_TORCH_INDEX_URL = "https://download.pytorch.org/whl/cu130"
SERVICE_KEY_RE = re.compile(r"^  ([a-z][a-z0-9-]*):\n", re.M)
# override **只许**出现的键（白名单，R1-002）：GPU 面就这几项，其余一律由默认文件唯一定义。
# 用白名单而不是黑名单——黑名单只拦得住想到的那几个（network_mode / cap_add / command /
# build.target 都曾整队绕过），而"只加 GPU 面"这件事可以正面枚举。
ALLOWED_SERVICE_KEYS = {"image", "build", "environment", "deploy", "healthcheck"}
ALLOWED_BUILD_KEYS = {"args"}
ALLOWED_ENV_KEYS = {"KRONOS_DEVICE"}
SERVICE_SUBKEY_RE = re.compile(r"(?m)^    ([A-Za-z_][\w.-]*):")
BUILD_SUBKEY_RE = re.compile(r"(?m)^      ([A-Za-z_][\w.-]*):")


def _strip_comments(text: str) -> str:
    """剥离整行注释（与 F004 同口径：不处理行尾注释，免误伤引号内 #）。"""
    return re.sub(r"(?m)^[ \t]*#.*$", "", text)


def _service_block(compose: str, service: str) -> str:
    stripped = _strip_comments(compose)
    start = stripped.index(f"\n  {service}:\n") + 1
    nxt = SERVICE_KEY_RE.search(stripped[start + len(service) + 3 :])
    end = start + len(service) + 3 + nxt.start() if nxt else len(stripped)
    return stripped[start:end]


def assert_default_compose_gpu_free(compose: str) -> None:
    """默认文件不含任何 GPU 面（FR-002 / NFR-001）。"""
    stripped = _strip_comments(compose)
    assert "driver: nvidia" not in stripped, "默认 compose 不得出现 nvidia 设备预留"
    assert "reservations:" not in stripped, "默认 compose 不得出现设备预留块"
    real_block = _service_block(compose, "kronos-signal-real")
    assert "KRONOS_DEVICE: cpu" in real_block, "默认 real 服务必须钉死 KRONOS_DEVICE: cpu"
    assert "devices:" not in real_block
    assert "${KRONOS_DEVICE" not in real_block, "默认文件不得以变量插值开关设备"
    assert "${KRONOS_GPU" not in stripped, "默认文件不得出现 GPU 变量插值"
    assert not re.search(r"(?m)^    image:", real_block), (
        "默认 real 服务不得设 image:（否则与 GPU 标签互相覆盖）"
    )


def assert_gpu_override_contract(override: str) -> None:
    """override 文件契约（design §4 表逐项）。"""
    stripped = _strip_comments(override)
    services = SERVICE_KEY_RE.findall(stripped.split("services:\n", 1)[-1])
    assert services == ["kronos-signal-real"], f"override 只允许覆盖 kronos-signal-real: {services}"
    block = _service_block(override, "kronos-signal-real")

    assert f"image: {GPU_IMAGE}" in block, "GPU 构建必须使用独立镜像标签"
    assert f"TORCH_INDEX_URL: {GPU_TORCH_INDEX_URL}" in block, "CUDA 构建参数必须是 cu130 索引"
    assert "TORCH_VERSION" not in block, "GPU 构建不得覆盖 torch 版本"
    assert "KRONOS_DEVICE: cuda" in block, "override 必须显式 KRONOS_DEVICE: cuda（触发严格分支）"
    assert "driver: nvidia" in block
    assert re.search(r"(?m)^\s+count: 1$", block), "设备预留必须 count: 1（缺省即全部 GPU）"
    assert "capabilities: [gpu]" in block
    assert "privileged" not in block, "设备预留不得借道特权容器"
    assert_override_keys_whitelisted(block)
    assert_gpu_healthcheck(block)


def assert_override_keys_whitelisted(block: str) -> None:
    """服务块的键面是白名单：GPU 面之外的键一律判红（R1-002）。"""
    keys = set(SERVICE_SUBKEY_RE.findall(block))
    extra = keys - ALLOWED_SERVICE_KEYS
    assert not extra, (
        f"override 出现 GPU 面之外的键: {sorted(extra)}（白名单 {sorted(ALLOWED_SERVICE_KEYS)}）"
    )

    build_block = block[block.index("    build:") :] if "    build:" in block else ""
    if build_block:
        nxt = SERVICE_SUBKEY_RE.search(build_block[len("    build:") :])
        build_block = build_block[: len("    build:") + nxt.start()] if nxt else build_block
        build_keys = set(BUILD_SUBKEY_RE.findall(build_block))
        extra_build = build_keys - ALLOWED_BUILD_KEYS
        assert not extra_build, (
            f"build 下只许 {sorted(ALLOWED_BUILD_KEYS)}，实际多出 {sorted(extra_build)}"
        )

    env_block = block[block.index("    environment:") :] if "    environment:" in block else ""
    if env_block:
        nxt = SERVICE_SUBKEY_RE.search(env_block[len("    environment:") :])
        env_block = env_block[: len("    environment:") + nxt.start()] if nxt else env_block
        env_keys = set(BUILD_SUBKEY_RE.findall(env_block))
        extra_env = env_keys - ALLOWED_ENV_KEYS
        assert not extra_env, (
            f"environment 下只许 {sorted(ALLOWED_ENV_KEYS)}（其余由默认文件唯一定义），"
            f"实际多出 {sorted(extra_env)}"
        )


def assert_gpu_healthcheck(block: str) -> None:
    """healthcheck 判据：model_loaded=true 且 device 以 cuda 开头（FR-003）。"""
    assert "healthcheck:" in block
    assert "model_loaded') is True" in block, "GPU healthcheck 必须要求 model_loaded=true"
    assert "startswith('cuda')" in block, "GPU healthcheck 必须以 device 以 cuda 开头为判据"
    assert "== 'cpu'" not in block, "GPU healthcheck 不得沿用 cpu 判据"


def test_default_compose_has_no_gpu_surface() -> None:
    assert_default_compose_gpu_free(COMPOSE_PATH.read_text(encoding="utf-8"))


def test_gpu_override_contract() -> None:
    assert_gpu_override_contract(GPU_OVERRIDE_PATH.read_text(encoding="utf-8"))


def _mutate(text: str, old: str, new: str) -> str:
    assert old in text, f"变异基准串不存在（上游改动后需同步变异用例）: {old}"
    return text.replace(old, new, 1)


DEVICE_BLOCK = (
    "    deploy:\n      resources:\n        reservations:\n          devices:\n"
    "            - driver: nvidia\n              count: 1\n              capabilities: [gpu]\n"
)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        # 往默认 real 服务加设备预留
        ("    healthcheck:\n", DEVICE_BLOCK + "    healthcheck:\n"),
        # 默认设备改为变量开关
        ("KRONOS_DEVICE: cpu", "KRONOS_DEVICE: ${KRONOS_DEVICE:-cpu}"),
        # 默认 real 服务设 image（与 GPU 标签互相覆盖）
        (
            "    container_name: quant-kronos-signal-real\n",
            "    image: alphamill/kronos-signal-real:gpu\n"
            "    container_name: quant-kronos-signal-real\n",
        ),
    ],
)
def test_default_compose_mutations_fail_the_gate(old: str, new: str) -> None:
    mutated = _mutate(COMPOSE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_default_compose_gpu_free(mutated)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("              count: 1\n", ""),  # 删 count（语义变为全部 GPU）
        (f"    image: {GPU_IMAGE}\n", ""),  # 删独立镜像标签
        ("KRONOS_DEVICE: cuda", "KRONOS_DEVICE: cpu"),  # 设备写回 cpu
        (GPU_TORCH_INDEX_URL, "https://download.pytorch.org/whl/cpu"),  # 构建参数写回 CPU
        ("driver: nvidia", "driver: amd"),  # 设备驱动错配
        (".startswith('cuda')", " == 'cpu'"),  # healthcheck 判据写回 cpu（AC-003）
        ("h.get('model_loaded') is True and ", ""),  # 删 model_loaded 条件（AC-003）
        ("    environment:\n", "    privileged: true\n    environment:\n"),  # 特权容器
        ("    environment:\n", '    ports:\n      - "8003:8001"\n    environment:\n'),
        ("    environment:\n", "    restart: unless-stopped\n    environment:\n"),
        ("    environment:\n", "    volumes:\n      - ../models:/app/models\n    environment:\n"),
        ("    environment:\n", "    depends_on: []\n    environment:\n"),
        ("    image:", "    # image:"),  # 注释掉镜像标签：门禁读语义不读裸文本
    ],
)
def test_gpu_override_mutations_fail_the_gate(old: str, new: str) -> None:
    mutated = _mutate(GPU_OVERRIDE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_gpu_override_contract(mutated)


def test_override_touching_another_service_fails_the_gate() -> None:
    """override 只允许覆盖 kronos-signal-real：顺手改 mock 服务即判红。"""
    override = GPU_OVERRIDE_PATH.read_text(encoding="utf-8")
    mutated = override + "\n  kronos-signal:\n    environment:\n      KRONOS_DEVICE: cuda\n"
    with pytest.raises(AssertionError):
        assert_gpu_override_contract(mutated)


# R1-002：门禁原为黑名单（只拦 6 个键），下列越界写法全部能过门禁。改白名单后逐条判红。
OUT_OF_SCOPE_MUTATIONS = [
    # 控制面被暴露到所有网卡，违反 F009 NFR-003「只在回环可达」与 F010 NFR-003
    ("    environment:\n", "    network_mode: host\n    environment:\n"),
    # 容器名被改 → F009/F003 客户端找错实例
    ("    environment:\n", "    container_name: something-else\n    environment:\n"),
    # GPU 镜像退回 mock 目标 → 镜像里根本没有 torch
    ("      args:\n", "      target: mock\n      args:\n"),
    # 越界覆盖运行时环境（模型路径由默认文件唯一定义）
    ("      KRONOS_DEVICE: cuda\n", "      KRONOS_DEVICE: cuda\n      KRONOS_MODEL_PATH: /tmp/x\n"),
    # 悄悄加能力位
    ("    environment:\n", "    cap_add:\n      - SYS_ADMIN\n    environment:\n"),
    # 越界覆盖 entrypoint/command
    ("    environment:\n", '    command: ["sleep", "infinity"]\n    environment:\n'),
]


@pytest.mark.parametrize(("old", "new"), OUT_OF_SCOPE_MUTATIONS)
def test_out_of_scope_override_keys_fail_the_gate(old: str, new: str) -> None:
    """override 的键面必须是**白名单**：GPU 面之外的任何键都判红。

    黑名单只能拦住想到的那几个——`network_mode`、`cap_add`、`command`、`build.target`
    这些都能绕过（代码检视 R1-002 实测 6/6 过门禁）。GPU override 的职责是"只加 GPU 面"，
    这一点可以正面枚举，所以该用白名单。
    """
    mutated = _mutate(GPU_OVERRIDE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_gpu_override_contract(mutated)
