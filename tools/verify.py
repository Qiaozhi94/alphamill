#!/usr/bin/env python3
"""本地统一验证入口（公开验证唯一入口）。

按固定顺序运行：规格生命周期校验 → pytest → ruff check → ruff format check。
任一步失败即返回非零。

各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
统一指向本入口。

用法：
    python tools/verify.py
退出码 0 表示全部通过；非 0 时打印失败步骤。
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n== {label} ==")
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        print(f"FAILED: {label}")
        return False
    return True


def main() -> int:
    steps = [
        ([sys.executable, "tools/validate_spec_lifecycle.py"], "规格生命周期校验"),
        ([sys.executable, "-m", "pytest", "-q"], "pytest"),
        (["ruff", "check", "."], "ruff check"),
        (["ruff", "format", "--check", "."], "ruff format check"),
    ]
    failed = []
    for cmd, label in steps:
        if not _run(cmd, label):
            failed.append(label)
    if failed:
        print(f"\nverify.py 失败步骤：{failed}")
        return 1
    print("\nverify.py 全部通过：生命周期 / pytest / ruff")
    return 0


if __name__ == "__main__":
    sys.exit(main())
