"""生成运行记录的 schema 常量（叶子模块，F012 `DR-001`）。

事件信封的版本号与 run.json 的 schema 版本解耦（文档检视 D20/D40）：run.json 升 v2 不改变
events.jsonl 的格式。本模块不导入 run_store，run_store 与 event_writer 都从这里取常量。
"""

from __future__ import annotations

from typing import Final

RUN_SCHEMA_VERSION: Final = 1  # T009 升 v2（run.json 当前写入版本）
EVENT_SCHEMA_VERSION: Final = 1
