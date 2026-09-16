#!/usr/bin/env python3
"""本地统一验证入口（公开验证唯一入口）。

按固定顺序运行：规格生命周期校验 → 文档相对链接检查 → 任务 DAG 检查
→ 文档一致性检查 → dev 依赖 pin 范围检查 → 密钥模式扫描 → pytest
→ ruff check → ruff format check。任一步失败即记录，全部跑完后汇总返回非零
（不短路）。

各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
统一指向本入口。

用法：
    python3 tools/verify.py
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
        ([sys.executable, "tools/check_doc_links.py"], "文档相对链接检查"),
        ([sys.executable, "tools/check_task_dag.py"], "任务 DAG 检查"),
        ([sys.executable, "tools/check_doc_consistency.py"], "文档一致性检查"),
        ([sys.executable, "tools/check_dep_pins.py"], "dev 依赖版本在 pin 范围内"),
        ([sys.executable, "tools/check_secrets.py"], "密钥模式扫描"),
        # 显式限定两个测试目录和 collection root，避免仓库内工具生成的不可读
        # symlink（如 .codegraph）被 pytest 当作 collection root 探查。
        (
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--confcutdir=tests",
                "--rootdir=tests",
                "tests/unit",
                "tests/integration",
            ],
            "pytest",
        ),
        ([sys.executable, "-m", "ruff", "check", "."], "ruff check"),
        ([sys.executable, "-m", "ruff", "format", "--check", "."], "ruff format check"),
    ]
    failed = []
    for cmd, label in steps:
        if not _run(cmd, label):
            failed.append(label)
    if failed:
        print(f"\nverify.py 失败步骤：{failed}")
        return 1
    print(
        "\nverify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / "
        "依赖 pin / 密钥扫描 / pytest / ruff"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
