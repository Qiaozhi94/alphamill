#!/usr/bin/env python3
"""任务依赖 DAG 校验（doc review F003-D012 回归门）。

对进入开发流转的 Feature（spec status ∈ {ready-for-development, in-progress,
review}）校验 `docs/features/<version>/Fxxx-*/tasks.md`：

  - §4「依赖与并行关系」里所有边端点都是已定义的任务 ID；
  - 边一律「向前」：源 ID < 目标 ID（任务编号即执行顺序，禁止依赖后序任务）；
  - 最高编号任务（收口任务）必须有至少一条入边；
  - `[P]` 任务不得同时声明前置边（tasks 模板规定）。

**作用域说明**：不收 `done`（F001/F004 等历史 Feature 已收口，纳入会立刻破坏
既有文档）与 `draft`（尚未进入流转）。这与 `validate_spec_lifecycle.py` 的
status 作用域模式一致。

用法：python tools/check_task_dag.py
退出码 0 = 全部通过；1 = 存在违规。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ENFORCED_STATUSES = {"ready-for-development", "in-progress", "review"}
TASK_RE = re.compile(r"^-\s+\[[ xX]\]\s+(T\d{3})")
EDGE_SEGMENT_RE = re.compile(r"`([^`]*->[^`]*)`")
SECTION4 = "4. 依赖与并行关系"


def strip_code_blocks(text: str) -> str:
    return re.sub(r"```[\s\S]*?```", "\n", text.replace("\r\n", "\n"))


def parse_frontmatter(text: str) -> dict:
    norm = text.replace("\r\n", "\n")
    m = re.match(r"^---\n([\s\S]*?)\n---", norm)
    if not m:
        return {}
    fm: dict = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fm


def section_body(text: str, title: str) -> str:
    lines = strip_code_blocks(text).split("\n")
    start = None
    for i, line in enumerate(lines):
        m = re.match(r"^##\s+(.+)$", line)
        if m and m.group(1).strip() == title:
            start = i + 1
            break
    if start is None:
        return ""
    body = []
    for line in lines[start:]:
        if re.match(r"^##\s", line):
            break
        body.append(line)
    return "\n".join(body)


def parse_task_lines(text: str) -> list[tuple[str, bool]]:
    """返回 [(task_id, is_parallel)]，保持文件顺序。"""
    out: list[tuple[str, bool]] = []
    for line in strip_code_blocks(text).split("\n"):
        m = TASK_RE.match(line.strip())
        if m:
            out.append((m.group(1), "[P]" in line))
    return out


def parse_edges(text: str) -> list[tuple[str, str]]:
    """解析 §4 的 `A -> B` 链；`A/B -> C/D` 展开为笛卡尔积。

    非 T 开头的端点（如跨 feature 的 `F008.IR-002`）不参与本次校验。
    """
    edges: list[tuple[str, str]] = []
    for seg in EDGE_SEGMENT_RE.findall(section_body(text, SECTION4)):
        if "->" not in seg:
            continue
        hops = [h.strip() for h in seg.split("->")]
        for left_raw, right_raw in zip(hops, hops[1:], strict=False):
            left = [x.strip() for x in left_raw.split("/")]
            right = [x.strip() for x in right_raw.split("/")]
            for a in left:
                for b in right:
                    if re.fullmatch(r"T\d{3}", a) and re.fullmatch(r"T\d{3}", b):
                        edges.append((a, b))
    return edges


def check_tasks(text: str) -> list[str]:
    task_lines = parse_task_lines(text)
    ids = [t for t, _ in task_lines]
    parallel = {t for t, is_p in task_lines if is_p}
    errors: list[str] = []
    if not ids:
        return ["tasks.md 未解析到任何任务行"]

    edges = parse_edges(text)
    for src, dst in edges:
        if src not in ids:
            errors.append(f"§4 边端点未定义: {src} -> {dst}")
        if dst not in ids:
            errors.append(f"§4 边端点未定义: {src} -> {dst}")
    errors = list(dict.fromkeys(errors))

    for src, dst in edges:
        if src in ids and dst in ids and src >= dst:
            errors.append(f"§4 存在向后边（依赖后序任务）: {src} -> {dst}")
    for src, dst in edges:
        if dst in parallel:
            errors.append(f"`[P]` 任务不得有前置边: {dst} 被 {src} 依赖")

    last = max(ids)
    if not any(dst == last for _, dst in edges):
        errors.append(f"最高编号任务 {last} 无入边（收口任务必须有前置依赖）")
    return list(dict.fromkeys(errors))


def discover_features(root: pathlib.Path) -> list[tuple[str, str, str]]:
    """返回 [(dir_name, status, tasks_text)]。"""
    out: list[tuple[str, str, str]] = []
    features_dir = root / "docs" / "features"
    if not features_dir.is_dir():
        return out
    for ver in sorted(features_dir.iterdir()):
        if not ver.is_dir() or ver.name in ("TEMPLATE", "releases"):
            continue
        for f in sorted(ver.iterdir()):
            if not f.is_dir() or not re.match(r"^F\d{3}-", f.name):
                continue
            spec, tasks = f / "spec.md", f / "tasks.md"
            if not spec.is_file() or not tasks.is_file():
                continue
            status = parse_frontmatter(spec.read_text(encoding="utf-8")).get("status", "")
            out.append((f.name, status, tasks.read_text(encoding="utf-8")))
    return out


def run_checks(root: pathlib.Path = ROOT) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    for name, status, tasks_text in discover_features(root):
        if status not in ENFORCED_STATUSES:
            continue
        for msg in check_tasks(tasks_text):
            errors.append((name, msg))
    return errors


def main() -> int:
    errors = run_checks()
    if not errors:
        print("check_task_dag: 全部通过")
        return 0
    print("check_task_dag: 失败", file=sys.stderr)
    for feature, msg in errors:
        print(f"  - {feature}: {msg}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
