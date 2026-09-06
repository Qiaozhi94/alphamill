#!/usr/bin/env python3
"""文档相对链接存在性检查（doc review D011 回归门）。

扫描 docs/**/*.md 与 README.md、CLAUDE.md（排除 conversations/、docs/research/、
.sisyphus/），解析 `[text](target)` 形式的相对链接，按所在文件目录解析目标路径，
目标（文件或目录）不存在即报告。跳过 http(s)、mailto、纯锚点（#...）链接，
代码围栏（``` / ~~~）内的内容整体忽略。

用法：python tools/check_doc_links.py
退出码 0 = 相对链接全部可解析；1 = 存在死链。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")
EXCLUDED_PARTS = {"conversations", ".sisyphus"}
EXCLUDED_REL_PREFIXES = ("docs/research/",)


def iter_markdown(root: pathlib.Path) -> list[pathlib.Path]:
    candidates: list[pathlib.Path] = []
    for name in ("README.md", "CLAUDE.md"):
        p = root / name
        if p.is_file():
            candidates.append(p)
    docs = root / "docs"
    if docs.is_dir():
        candidates.extend(p for p in sorted(docs.rglob("*.md")) if p.is_file())
    result = []
    for p in candidates:
        rel = p.relative_to(root).as_posix()
        if any(part in EXCLUDED_PARTS for part in p.relative_to(root).parts):
            continue
        if any(rel.startswith(prefix) for prefix in EXCLUDED_REL_PREFIXES):
            continue
        result.append(p)
    return result


def strip_fences(text: str) -> str:
    out_lines: list[str] = []
    fence: str | None = None
    for line in text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            out_lines.append("")
            continue
        if fence is not None and stripped.startswith(fence):
            fence = None
            out_lines.append("")
            continue
        out_lines.append("" if fence is not None else line)
    return "\n".join(out_lines)


def _is_broken(base: pathlib.Path, target: str) -> bool:
    path_part = target.split("#", 1)[0].strip()
    if not path_part:
        return False
    return not (base / path_part).exists()


def check_links(root: pathlib.Path = ROOT) -> list[str]:
    errors: list[str] = []
    for md in iter_markdown(root):
        rel = md.relative_to(root).as_posix()
        for lineno, line in enumerate(strip_fences(md.read_text(encoding="utf-8")).split("\n"), 1):
            for m in LINK_RE.finditer(line):
                target = m.group(2).strip()
                if target.startswith(SKIP_PREFIXES):
                    continue
                if _is_broken(md.parent, target):
                    errors.append(f"{rel}:{lineno}: 相对链接目标不存在: {target}")
    return errors


def main() -> int:
    errors = check_links()
    if not errors:
        print("check_doc_links: 相对链接全部可解析")
        return 0
    print("check_doc_links: 失败", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
