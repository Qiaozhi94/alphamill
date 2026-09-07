#!/usr/bin/env python3
"""密钥模式扫描门禁（2026-09-07 对话归档泄露事件回归门）。

事件：conversations/ 归档提交把会话转录中带 Bearer 凭证的 curl 命令原样入库。
本门禁扫描仓库文本文件中的常见密钥形态：UUID 形态 Bearer/apiKey（火山 Ark key
即此格式）、GitHub token、OpenAI 风格 sk- key、AWS AKIA、PEM 私钥块。形态匹配
一票否决（宁误报不漏报），命中即非零退出。

已知边界：
- 扫描的是"形态"而非"真伪"，假 key 同样拦截；
- 仓库树内（含测试源码）不得出现任何命中形态的连续字符串——测试 fixture 一律
  写在 tmp_path 下，且源码中的样例密钥用字符串拼接切开，避免门禁拦下自己的
  测试（test_check_secrets.py 即此写法）；
- 转录/归档类内容（conversations/ 等）同样在扫描范围内——这正是事件根因。

用法：python tools/check_secrets.py
退出码 0 = 无命中；1 = 存在命中形态。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

UUID = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("uuid-bearer", re.compile(rf"bearer\s+{UUID}", re.IGNORECASE)),
    ("uuid-apikey", re.compile(rf"api[_-]?key\s*[\"']?\s*[:=]\s*[\"']?\s*{UUID}", re.IGNORECASE)),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}")),
    ("openai-style", re.compile(r"\bsk-[A-Za-z0-9]{20,}")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    ".omo",
    ".sisyphus",
    ".history",
    ".code-review-graph",
    ".codegraph",
}


def check(root: pathlib.Path = ROOT) -> list[str]:
    """返回命中列表，元素为 'path:line [pattern] 摘要'。"""
    findings: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for name, pattern in PATTERNS:
                if pattern.search(line):
                    rel = path.relative_to(root)
                    snippet = line.strip()[:80]
                    findings.append(f"{rel}:{lineno} [{name}] {snippet}")
    return findings


def main() -> int:
    findings = check()
    if not findings:
        print("check_secrets: 无密钥形态命中")
        return 0
    print("check_secrets: 命中密钥形态", file=sys.stderr)
    for f in findings:
        print(f"  - {f}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
