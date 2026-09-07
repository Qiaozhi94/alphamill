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

# 历史档案（检视复盘 / 会话归档）原样保留，不参与当前规范扫描。
_SCAN_EXEMPT_PARTS = {"docs/reviews", "conversations"}
_BARE_COMMAND = re.compile(r"\bpython tools/verify\.py")


def _tracked_text_files() -> list[pathlib.Path]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    files: list[pathlib.Path] = []
    for rel in proc.stdout.splitlines():
        p = pathlib.Path(rel)
        if p.suffix not in {".md", ".py", ".yml", ".yaml", ".toml", ".cfg", ".txt"}:
            continue
        if any(part in _SCAN_EXEMPT_PARTS for part in p.parts):
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


def test_python3_is_available() -> None:
    assert shutil.which("python3") is not None
