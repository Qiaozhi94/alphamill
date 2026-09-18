"""代码/构建摘要与工作树洁净度（`IR-001`/`NFR-002`；任务 T006）。

canonical 的 `--code-build-digest` 只作**期望值**：真实摘要由 runner 自行计算，不一致即
`E_INPUT_INVALID`（design §4）。摘要按**内容**计算，且用包内相对路径作键，因此同一份代码在不同
检出路径、不同 Parquet codec 下得到同一摘要（`NFR-002`）；绝对路径、主机与时间不入摘要。
版本控制工作树脏时 canonical 必须拒绝，`worktree_dirty()` 无法判定时返回 `None`（fail-closed）。
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from alphamill.data_bridge import paths
from alphamill.evaluation.contract_common import DIGEST_PREFIX

PACKAGE_SUBDIR = "src/alphamill"
BUILD_FILES = ("pyproject.toml", "uv.lock")


def repo_root() -> Path:
    return Path(paths.REPO_ROOT)


def _package_files(root: Path) -> list[Path]:
    package = root / PACKAGE_SUBDIR
    if not package.is_dir():
        return []
    return sorted(path for path in package.rglob("*.py") if "__pycache__" not in path.parts)


def code_build_digest(root: Path | None = None) -> str:
    """包内容 + 构建/锁文件的内容寻址摘要；与检出路径无关。"""
    base = Path(root) if root is not None else repo_root()
    entries: list[str] = []
    for path in _package_files(base):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        entries.append(f"{path.relative_to(base).as_posix()}:{digest}")
    if not entries:
        raise FileNotFoundError(f"找不到包源码: {base / PACKAGE_SUBDIR}")
    for name in BUILD_FILES:
        candidate = base / name
        if candidate.is_file():
            entries.append(f"{name}:{hashlib.sha256(candidate.read_bytes()).hexdigest()}")
    return DIGEST_PREFIX + hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


def worktree_dirty(root: Path | None = None) -> bool | None:
    """True=有未提交改动；False=干净；None=无法判定（非 git 或 git 不可用，fail-closed）。"""
    base = Path(root) if root is not None else repo_root()
    try:
        proc = subprocess.run(
            ["git", "-C", str(base), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return bool(proc.stdout.strip())


def assert_expected_code_build_digest(expected: str | None, actual: str) -> None:
    """`--code-build-digest` 只作期望值：不一致即拒绝，不接受调用方自报值（`IR-001`）。"""
    if expected is None:
        return
    if expected != actual:
        raise CodeBuildMismatchError(
            f"code_build_digest 期望值与实际计算不符（expected={expected}, actual={actual}）"
        )


class CodeBuildMismatchError(Exception):
    """`--code-build-digest` 期望值与 runner 计算结果不一致。"""

    code = "E_INPUT_INVALID"


def assert_worktree_clean_for_canonical(root: Path | None = None) -> None:
    dirty = worktree_dirty(root)
    if dirty is None:
        raise CodeBuildMismatchError(
            "无法判定版本控制工作树是否洁净，canonical 拒绝（fail-closed）"
        )
    if dirty:
        raise CodeBuildMismatchError("版本控制工作树存在未提交改动，canonical 拒绝（IR-001）")
