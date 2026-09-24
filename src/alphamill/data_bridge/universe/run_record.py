"""回填运行记录的读写与校验（`DR-003` / T013）：`run.json` 的路径解析、载入与原子落盘。

从 `backfill_runner` 拆出（行数治理 + 职责单一）：运行记录是**可更新的运行态**（不是内容寻址
artifact），逐 pair 落盘以保留断点，因此两条硬要求都落在这里：

- **原子替换**：截断式原地写一遇中断（机器重启 / Ctrl-C / 容器重建）就留下半截 JSON，而分片
  脚本固定带 `--resume-run-id`，一次损坏就再也续不上（2026-09-24 检视 R1-027）。
- **fail-closed 载入**：缺失 / 损坏 / `schema_version` 不符一律给明确错误，而不是让裸
  `JSONDecodeError` 逃成 traceback + 退出 1（那会被分片脚本当成可重试瞬时故障），也不静默按
  新契约解读旧记录（检视 R1-014）。

本模块不 import `backfill_runner`：`BackfillRun` 的构造留在调用方，避免循环依赖。
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from alphamill.data_bridge import paths
from alphamill.data_bridge.universe.errors import BackfillIncompleteError
from alphamill.data_bridge.universe.storage import atomic_create

__all__ = ["RUN_FILE", "SCHEMA_VERSION", "read_run_document", "run_dir", "write_run_document"]

RUN_FILE = "run.json"
#: 运行记录 schema 版本（`AC-013`）；漂移必须拒载而不是静默按新契约解读（检视 R1-014）
SCHEMA_VERSION = 1


def run_dir(run_id: str, reports_dir: Path | None = None) -> Path:
    """运行记录目录：显式 `reports_dir` 优先，否则 `<repo>/reports/backfill/<run_id>`。"""
    root = (
        Path(reports_dir) if reports_dir is not None else paths.REPO_ROOT / "reports" / "backfill"
    )
    return root / run_id


def read_run_document(run_id: str, reports_dir: Path | None = None) -> dict:
    """载入并校验运行记录文档：缺失/损坏/版本不符都判红（fail-closed）。"""
    path = run_dir(run_id, reports_dir) / RUN_FILE
    if not path.is_file():
        raise BackfillIncompleteError(f"运行记录不存在: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BackfillIncompleteError(f"运行记录损坏（JSON 无法解析）: {path}") from exc
    if not isinstance(document, dict):
        raise BackfillIncompleteError(f"运行记录结构非法（顶层应为对象）: {path}")
    missing = sorted({"run_id", "universe_id", "window", "pairs"} - set(document))
    if missing:
        raise BackfillIncompleteError(f"运行记录缺必需键 {missing}: {path}")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise BackfillIncompleteError(
            f"运行记录 schema_version 不符: {document.get('schema_version')!r} != {SCHEMA_VERSION}"
            f"（{path}）"
        )
    return document


def write_run_document(run_id: str, document: dict, reports_dir: Path | None = None) -> None:
    """首次写入用 `atomic_create`（写一次），更新走「同目录临时文件 + `os.replace`」原子替换。"""
    target = run_dir(run_id, reports_dir) / RUN_FILE
    payload = json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False).encode()
    if not target.is_file():
        atomic_create(target, payload)
        return
    tmp = target.with_name(f".{target.name}.tmp")
    tmp.write_bytes(payload)
    os.replace(tmp, target)
