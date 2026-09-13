"""门禁命令契约回归测试（D046 回归门）。

规范声明的唯一验证入口是 `python3 tools/verify.py`（当前真实环境无 `python`
命令，D046 已全仓统一）。本测试扫描 tracked 文本文件，禁止再出现裸
`python tools/verify.py` 引用，并断言 python3 在本机可用。变异验证已做过：
任一 tracked 文档改回 `python tools/verify.py` 时本测试必须变红。
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# 扫描器必须跳过自身：本文档字符串引用了被禁止的裸命令作规则说明（同 ruff 自含违例样本）。
_SELF = pathlib.Path(__file__).resolve()

# 历史档案（检视复盘 / 会话归档）原样保留，不参与当前规范扫描。
# 必须按目录前缀（posix 形式）比对：早期写法 `part in _SCAN_EXEMPT_PARTS for part in p.parts`
# 对 "docs/reviews" 这种多段前缀永不命中，豁免形同虚设——`conversations` 恰好是单段路径
# 所以一直生效，掩盖了缺陷，直到 RETROSPECTIVE 首次出现裸命令才暴露（ADR5-R4-01）。
_SCAN_EXEMPT_DIRS = ("docs/reviews/", "conversations/")
_TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".toml", ".cfg", ".txt"}
_BARE_COMMAND = re.compile(r"\bpython tools/verify\.py")


def _tracked_files() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.splitlines()


def _tracked_text_files() -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for rel in _tracked_files():
        p = pathlib.Path(rel)
        if p.suffix not in _TEXT_SUFFIXES:
            continue
        if p.as_posix().startswith(_SCAN_EXEMPT_DIRS):
            continue
        if (REPO_ROOT / p).resolve() == _SELF:
            continue
        files.append(REPO_ROOT / p)
    return files


def test_no_bare_python_gate_command_in_tracked_sources() -> None:
    offenders: list[str] = []
    for p in _tracked_text_files():
        if not p.is_file():
            continue
        match = _BARE_COMMAND.search(p.read_text(encoding="utf-8"))
        if match:
            offenders.append(f"{p}: {match.group(0)}")
    assert offenders == [], f"门禁命令必须统一为 python3 tools/verify.py：{offenders}"


def test_exempt_dirs_are_actually_skipped() -> None:
    """豁免目录必须真的被跳过（ADR5-R4-01 回归门）。

    先断言豁免目录下确实有被跟踪的文本文件，否则下面的"未泄漏"断言会在空集上
    恒真——测试自证而非证伪。
    """
    exempt_tracked = [
        rel
        for rel in _tracked_files()
        if rel.startswith(_SCAN_EXEMPT_DIRS) and pathlib.Path(rel).suffix in _TEXT_SUFFIXES
    ]
    assert exempt_tracked, "豁免目录下没有被跟踪的文本文件，本断言将空转，需重新选取样本"

    scanned = {p.relative_to(REPO_ROOT).as_posix() for p in _tracked_text_files()}
    leaked = sorted(rel for rel in exempt_tracked if rel in scanned)
    assert leaked == [], f"豁免目录仍被扫描，豁免判定未按目录前缀生效：{leaked}"


def test_python3_is_available() -> None:
    assert shutil.which("python3") is not None
