"""F010 torch 安装源参数化契约（unit，CI 常绿）。

对应 spec FR-001 / NFR-001 / AC-001、design §4 构建参数表：
- Dockerfile `real` 段以 `ARG TORCH_VERSION` / `ARG TORCH_INDEX_URL` 驱动 torch 安装，
  缺省值等于落地前字面量（`torch==2.14.0` + CPU wheel 索引）；
- 不带构建参数时解析出的 torch 安装命令（版本 + 索引）与落地前等价（NFR-001）；
- GPU override 只覆盖索引为 `cu130`，不覆盖版本（CPU/GPU 同版本，design §9）。

断言按"解析后的安装命令"判定，而不是只看子串：`ARG` 写在 `FROM mock AS real`
之前（全局作用域，stage 内不可见）或 `pip install` 不引用参数，都会让参数失效。
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE_PATH = ROOT / "deployment/kronos-service.Dockerfile"
GPU_OVERRIDE_PATH = ROOT / "deployment/docker-compose.gpu.yml"

# 落地前 real 目标的 torch 安装字面量（F004 design §2）。
LEGACY_TORCH_VERSION = "2.14.0"
LEGACY_TORCH_INDEX_URL = "https://download.pytorch.org/whl/cpu"
GPU_TORCH_INDEX_URL = "https://download.pytorch.org/whl/cu130"

ARG_RE = re.compile(r"^ARG ([A-Z_]+)(?:=(\S*))?$", re.M)
TORCH_INSTALL_RE = re.compile(
    r"pip install --no-cache-dir(?: --\S+ \S+)* torch==(\S+) \\\n\s*--index-url (\S+)"
    r"(?: \\\n\s*(\$\{TORCH_EXTRA_INDEX_URL[^\n]*))?",
    re.M,
)
REF_RE = re.compile(r"\$\{([A-Z_]+)\}|\$([A-Z_]+)")


def _real_stage(dockerfile: str) -> str:
    _, sep, real_stage = dockerfile.partition("FROM mock AS real")
    assert sep, "real 目标必须从 mock 派生"
    return re.sub(r"(?m)^[ \t]*#.*$", "", real_stage)


def resolve_torch_install(dockerfile: str, build_args: dict[str, str] | None = None):
    """按 Docker 语义解析 real 段 torch 安装命令，返回 (版本, 索引)。

    只认 real stage 内声明的 `ARG`（stage 作用域）；未声明的引用视为空串——
    与 docker build 行为一致，也正是"参数失效"类变异要被抓住的情形。
    """
    stage = _real_stage(dockerfile)
    declared = {name: default or "" for name, default in ARG_RE.findall(stage)}
    for name, value in (build_args or {}).items():
        if name in declared:
            declared[name] = value

    match = TORCH_INSTALL_RE.search(stage)
    assert match, "real 段缺少 torch 安装命令（pip install torch==… --index-url …）"

    def _expand(token: str) -> str:
        return REF_RE.sub(lambda m: declared.get(m.group(1) or m.group(2), ""), token)

    return _expand(match.group(1)), _expand(match.group(2))


def assert_build_args_contract(dockerfile: str) -> None:
    stage = _real_stage(dockerfile)
    declared = dict(ARG_RE.findall(stage))
    assert declared.get("TORCH_VERSION") == LEGACY_TORCH_VERSION, (
        "ARG TORCH_VERSION 缺省值必须等于落地前 pin"
    )
    assert declared.get("TORCH_INDEX_URL") == LEGACY_TORCH_INDEX_URL, (
        "ARG TORCH_INDEX_URL 缺省值必须是 CPU wheel 索引"
    )
    match = TORCH_INSTALL_RE.search(stage)
    assert match, "real 段缺少 torch 安装命令"
    assert match.group(1) == "${TORCH_VERSION}", "torch 版本必须引用 TORCH_VERSION 参数"
    assert match.group(2) == "${TORCH_INDEX_URL}", "wheel 索引必须引用 TORCH_INDEX_URL 参数"
    assert declared.get("TORCH_EXTRA_INDEX_URL") == "", (
        "ARG TORCH_EXTRA_INDEX_URL 缺省值必须是空串（默认构建不额外加索引）"
    )
    assert match.group(3) and "TORCH_EXTRA_INDEX_URL" in match.group(3), (
        "安装命令必须以 ${TORCH_EXTRA_INDEX_URL:+…} 条件展开引用额外索引参数"
    )
    assert resolve_torch_install(dockerfile) == (LEGACY_TORCH_VERSION, LEGACY_TORCH_INDEX_URL), (
        "不带构建参数时 torch 安装命令必须与落地前等价（NFR-001）"
    )


def test_build_args_default_to_legacy_cpu_install() -> None:
    assert_build_args_contract(DOCKERFILE_PATH.read_text(encoding="utf-8"))


def test_gpu_build_args_resolve_to_cu130_same_version() -> None:
    """GPU 构建参数：只换索引到 cu130，版本不变（CPU/GPU 同版本）。"""
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
    resolved = resolve_torch_install(dockerfile, {"TORCH_INDEX_URL": GPU_TORCH_INDEX_URL})
    assert resolved == (LEGACY_TORCH_VERSION, GPU_TORCH_INDEX_URL)


def test_gpu_override_passes_only_the_index_args() -> None:
    """override 只钉 cu130 索引；额外索引改为**引用环境变量且缺省为空**，不写死某台机器的镜像。

    R1-004：把 `pypi.tuna.tsinghua.edu.cn` 写死在 GPU 面唯一配置处，等于把 qiaozhi-lt 的
    网络绕行固化成契约——任何机器构建都会从第三方镜像解析 torch 的全部依赖，也让
    NFR-002「迁移只改参数」不成立。构建机自己在 deployment/.env 里给该变量。
    """
    override = re.sub(r"(?m)^[ \t]*#.*$", "", GPU_OVERRIDE_PATH.read_text(encoding="utf-8"))
    assert f"TORCH_INDEX_URL: {GPU_TORCH_INDEX_URL}" in override
    assert "TORCH_EXTRA_INDEX_URL: ${TORCH_EXTRA_INDEX_URL:-}" in override, (
        "额外索引必须引用环境变量且缺省为空"
    )
    assert "tuna.tsinghua" not in override and "aliyun" not in override, (
        "不得把具体镜像地址写进 GPU override（单机绕行不是契约）"
    )
    assert "TORCH_VERSION" not in override, "GPU 构建不得覆盖 torch 版本（CPU/GPU 同版本）"


def _mutate(text: str, old: str, new: str) -> str:
    assert old in text, f"变异基准串不存在（上游改动后需同步变异用例）: {old}"
    return text.replace(old, new, 1)


@pytest.mark.parametrize(
    ("old", "new"),
    [
        # 改缺省值
        ("ARG TORCH_VERSION=2.14.0", "ARG TORCH_VERSION=2.11.0"),
        (
            "ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu",
            "ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cu130",
        ),
        # 删缺省值（缺参构建时解析为空 → 安装命令不再等价）
        ("ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu", "ARG TORCH_INDEX_URL"),
        # 安装命令不再引用参数（写回字面量 = 参数失效）
        ("torch==${TORCH_VERSION}", "torch==2.14.0"),
        ("--index-url ${TORCH_INDEX_URL}", "--index-url https://download.pytorch.org/whl/cpu"),
        # 注释掉 ARG 声明
        ("ARG TORCH_VERSION=2.14.0", "# ARG TORCH_VERSION=2.14.0"),
        # 额外索引参数改为无条件展开（缺省空串时 pip 会拿到空的 --extra-index-url）
        (
            "${TORCH_EXTRA_INDEX_URL:+--extra-index-url ${TORCH_EXTRA_INDEX_URL}}",
            "--extra-index-url ${TORCH_EXTRA_INDEX_URL}",
        ),
        # 额外索引缺省值不再为空（默认构建被拽到第二索引）
        ("ARG TORCH_EXTRA_INDEX_URL=\n", "ARG TORCH_EXTRA_INDEX_URL=https://pypi.org/simple\n"),
    ],
)
def test_build_args_mutations_fail_the_gate(old: str, new: str) -> None:
    mutated = _mutate(DOCKERFILE_PATH.read_text(encoding="utf-8"), old, new)
    with pytest.raises(AssertionError):
        assert_build_args_contract(mutated)


def test_arg_declared_before_real_stage_is_not_visible() -> None:
    """ARG 挪到 `FROM mock AS real` 之前（全局作用域）即判红：stage 内引用解析为空。"""
    dockerfile = DOCKERFILE_PATH.read_text(encoding="utf-8")
    block = "ARG TORCH_VERSION=2.14.0\nARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu\n"
    assert block in dockerfile
    mutated = block + dockerfile.replace(block, "")
    with pytest.raises(AssertionError):
        assert_build_args_contract(mutated)
