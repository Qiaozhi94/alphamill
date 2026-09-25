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
import yaml

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
    assert_override_keys_whitelisted(override)
    assert_gpu_healthcheck(override)


def assert_override_keys_whitelisted(override: str) -> None:
    """服务块的键面是白名单，且按 **YAML 语义**取键（R1-002 定白名单、R2-002 改语义解析）。

    不按文本缩进取键：flow 写法（`build: {target: mock}`）、`healthcheck: disable`、
    `deploy.replicas` 都能从正则下面溜过去——第 1 轮的白名单就是这么被绕的。
    """
    doc = yaml.safe_load(override) or {}
    services = doc.get("services") or {}
    assert list(services) == ["kronos-signal-real"], (
        f"override 只允许覆盖 kronos-signal-real: {list(services)}"
    )
    svc = services["kronos-signal-real"] or {}
    extra = set(svc) - ALLOWED_SERVICE_KEYS
    assert not extra, (
        f"override 出现 GPU 面之外的键: {sorted(extra)}（白名单 {sorted(ALLOWED_SERVICE_KEYS)}）"
    )

    build = svc.get("build")
    assert isinstance(build, dict), f"build 必须是映射，实际 {type(build).__name__}"
    extra_build = set(build) - ALLOWED_BUILD_KEYS
    assert not extra_build, f"build 下只许 {sorted(ALLOWED_BUILD_KEYS)}，多出 {sorted(extra_build)}"

    env = svc.get("environment")
    assert isinstance(env, dict), f"environment 必须是映射（键值写法），实际 {type(env).__name__}"
    extra_env = set(env) - ALLOWED_ENV_KEYS
    assert not extra_env, (
        f"environment 下只许 {sorted(ALLOWED_ENV_KEYS)}（其余由默认文件唯一定义），"
        f"多出 {sorted(extra_env)}"
    )

    deploy = svc.get("deploy")
    assert isinstance(deploy, dict) and set(deploy) == {"resources"}, (
        f"deploy 下只许 resources（不得有 replicas 等——单卡单实例，架构 §7.1）: {deploy}"
    )
    resources = deploy["resources"] or {}
    assert set(resources) == {"reservations"}, (
        f"deploy.resources 下只许 reservations: {list(resources)}"
    )
    reservations = resources["reservations"] or {}
    assert set(reservations) == {"devices"}, f"reservations 下只许 devices: {list(reservations)}"

    healthcheck = svc.get("healthcheck")
    assert isinstance(healthcheck, dict) and set(healthcheck) == {"test"}, (
        f"healthcheck 只许覆盖 test（interval 等继承默认文件，也不得 disable）: {healthcheck}"
    )


def assert_gpu_healthcheck(override: str) -> None:
    """healthcheck 判据：`model_loaded=true` 且 `device` 以 cuda 开头（FR-003）。

    按 **assert 语句的实际条件**校验，不按子串——`assert True or h.get('model_loaded') …`
    含有全部关键子串却恒真（R3-002），子串匹配拦不住它。
    """
    doc = yaml.safe_load(override) or {}
    test = ((doc.get("services") or {}).get("kronos-signal-real") or {}).get("healthcheck", {})
    assert isinstance(test, dict), f"healthcheck 必须是映射（不得 disable）: {test!r}"
    command = test.get("test")
    assert isinstance(command, list) and command[:1] == ["CMD-SHELL"], (
        f"healthcheck.test 必须是 CMD-SHELL 形式: {command!r}"
    )
    shell = " ".join(command[1:])

    asserted = re.search(r"assert\s+(?P<cond>.+?),", shell)
    assert asserted, f"healthcheck 命令里找不到 assert 条件: {shell!r}"
    condition = asserted.group("cond")

    # 条件必须是「两个判据以 and 相连」，且不含恒真短路
    parts = [p.strip() for p in re.split(r"\band\b", condition)]
    assert len(parts) == 2, f"判据应为两项以 and 相连（model_loaded 与 device）: {condition!r}"
    # 只拦"独立的恒真项"与 or 短路：`is True` 是合法判据的一部分，不能一律禁 True
    assert not re.search(r"\bor\b", condition), f"判据不得用 or 短路: {condition!r}"
    for part in parts:
        assert not re.fullmatch(r"(True|1|1\s*==\s*1)", part.strip()), (
            f"判据项不得恒真: {part!r}（完整条件 {condition!r}）"
        )
    assert any("model_loaded" in p and "is True" in p for p in parts), (
        f"缺 model_loaded is True 判据: {condition!r}"
    )
    assert any("startswith('cuda')" in p for p in parts), (
        f"缺 device 以 cuda 开头判据: {condition!r}"
    )
    assert "== 'cpu'" not in condition, "GPU healthcheck 不得沿用 cpu 判据"


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


def test_integration_suite_scopes_project_name_to_image_build_only() -> None:
    """R2-001：`-p <项目名>` 只许用在「产镜像」的命令上，不许套到碰容器的命令上。

    第 1 轮为解决镜像名被并行会话覆盖（R1-001）而给整个 COMPOSE_BASE 加了 `-p`，结果
    非复用路径的 rm/up 走到另一个 compose 项目：与运营容器 `quant-kronos-signal-real`
    重名冲突，还会新建一套空的 TimescaleDB 卷（DB 依赖被一起拉起）。这条门禁把
    「项目名只服务构建」固化下来。
    """
    suite = (ROOT / "tests/integration/test_f010_gpu_runtime.py").read_text(encoding="utf-8")
    base = re.search(r"(?m)^COMPOSE_BASE = (.+)$", suite)
    assert base and '"-p"' not in base.group(1), "COMPOSE_BASE 不得带 -p（会污染容器路径）"

    gpu_block = suite[suite.index("COMPOSE_GPU = [") : suite.index("REAL_CONTAINER")]
    assert '"-p"' not in gpu_block, "GPU 路径（rm/up/build）不得带 -p"

    build_block = suite[suite.index("COMPOSE_CPU_BUILD = [") : suite.index("REAL_CONTAINER")]
    assert '"-p"' in build_block, "CPU 镜像构建应带 -p，避免镜像名被并行 worktree 覆盖"

    # 带 -p 的命令列表只允许出现在 build 上下文里
    for line in suite.splitlines():
        if "COMPOSE_CPU_BUILD" in line and "=" not in line:
            assert "build" in line or "_compose_image" in line, (
                f"带 -p 的项目名只许用于构建/解析镜像名，实际出现在: {line.strip()}"
            )


# R2-002：正则取键会被这些写法绕过——flow 写法把键写在一行、`healthcheck: disable` 直接
# 关掉健康检查、deploy 下塞 replicas。改用 YAML 语义解析后逐条判红。
YAML_EVASION_MUTATIONS = [
    # healthcheck 整体关掉：判据没了，报 cpu 的实例也会被判就绪
    (
        "    healthcheck:\n      test:\n",
        "    healthcheck: disable\n    _unused:\n      test:\n",
    ),
    # build 用 flow 写法：正则按缩进取键时看不见 target
    (
        "    build:\n      args:\n",
        "    build: {target: mock, args: \n",
    ),
    # deploy 下塞 replicas：多副本违反单卡单实例（架构 §7.1）
    (
        "    deploy:\n      resources:\n",
        "    deploy:\n      replicas: 3\n      resources:\n",
    ),
]


@pytest.mark.parametrize(("old", "new"), YAML_EVASION_MUTATIONS)
def test_yaml_level_evasions_fail_the_gate(old: str, new: str) -> None:
    """门禁必须按 **YAML 语义**取键，不能按文本缩进正则取键（R2-002）。"""
    mutated = _mutate(GPU_OVERRIDE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises((AssertionError, Exception)):
        assert_gpu_override_contract(mutated)


def test_feature_does_not_touch_default_env_example() -> None:
    """默认面红线（spec NFR-001 / tasks §0）：本 feature 不改 `deployment/.env.example`。

    R2-003：第 1 轮为 R1-004 把 `TORCH_EXTRA_INDEX_URL` 的说明写进了 .env.example，
    那是**默认面**，红线明写不动它——构建机各自的绕行配置属运维动作，说明位置在
    `docs/alphamill-integration.md` §七。红线不因一次方便而改；要改得先改 spec。
    """
    env_example = (ROOT / "deployment/.env.example").read_text(encoding="utf-8")

    assert "TORCH_EXTRA_INDEX_URL" not in env_example, (
        "GPU 构建的额外索引不得写进默认 .env.example（默认面红线）"
    )
    assert "cu130" not in env_example and "tuna.tsinghua" not in env_example, (
        "默认 .env.example 不得出现 GPU/镜像相关配置"
    )


def test_short_circuited_healthcheck_fails_the_gate() -> None:
    """R3-002：判据被短路（`assert True or 原判据`）必须判红。

    原门禁按子串匹配"含 model_loaded / startswith('cuda')"——把整个条件短路掉之后，
    这些子串**依然都在**，于是一个恒真的 healthcheck 能过门禁：容器永远 healthy，
    报 cpu 的实例也会被判就绪，FR-003 的第二道网形同虚设。
    """
    override = GPU_OVERRIDE_PATH.read_text(encoding="utf-8")
    mutated = override.replace(
        "assert h.get('model_loaded')", "assert True or h.get('model_loaded')"
    )
    assert mutated != override, "变异基准串不存在（healthcheck 命令改过？需同步本用例）"

    with pytest.raises(AssertionError):
        assert_gpu_override_contract(mutated)


def test_healthcheck_whitelist_rule_is_covered_by_a_mutation() -> None:
    """R3-002 的另一半：healthcheck 的白名单规则本身要有变异锁住。

    检视实测「删掉 healthcheck 白名单规则 → 30 passed」——规则没有任何用例依赖它。
    这里正面构造它该拦的两种写法：多加 interval（应由默认文件继承）、整体 disable。
    """
    override = GPU_OVERRIDE_PATH.read_text(encoding="utf-8")

    with_interval = override.replace(
        "    healthcheck:\n      test:", "    healthcheck:\n      interval: 3s\n      test:"
    )
    assert with_interval != override
    with pytest.raises(AssertionError, match="healthcheck"):
        assert_gpu_override_contract(with_interval)

    disabled = re.sub(
        r"(?ms)^    healthcheck:\n.*?\n(?=\Z)", "    healthcheck: disable\n", override
    )
    assert disabled != override
    with pytest.raises((AssertionError, TypeError)):
        assert_gpu_override_contract(disabled)
