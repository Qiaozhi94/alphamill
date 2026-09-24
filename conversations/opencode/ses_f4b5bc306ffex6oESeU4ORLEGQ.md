---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4b5bc306ffex6oESeU4ORLEGQ"
title: "F002 reader API + snapshot identity (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-18T13:10:57Z"
updated_at: "2026-09-18T13:12:33Z"
tokens_input: 85290
tokens_output: 8484
cost: 0.022
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# F002 reader API + snapshot identity (@explore subagent)

## user · 2026-09-18T13:10:57Z

[CONTEXT] I am implementing F003 (AlphaGen vendor + pluggable generator plane) in the alphamill repo at /home/georg/projects/alphamill-F003 (a git worktree of /home/georg/projects/alphamill). F003 needs to read immutable Parquet-lake snapshots through the F002 data_bridge read-only reader, and to validate per-dataset `(data_version, value_digest)` identity. I need the exact F002 public API so my binding/tensor layer calls it correctly instead of inventing a parallel path.

[GOAL] Produce the precise, verbatim API contract of the F002 reader layer and the snapshot/dataset identity model, so I can implement `generators/binding.py` and `generators/lake_tensor.py` against it.

[DOWNSTREAM] I will write binding validation (per-dataset value_digest comparison, invalid/absent version rejection) and tensor construction calling reader.read(); I also need to know how to discover valid data_versions and their value_digests for a dataset, and the shape/fields of symbol_map.

[REQUEST] Investigate `src/alphamill/data_bridge/` (reader.py, registry.py, manifest.py, symbol_map.py, digest.py, paths.py, partitions.py, export_summary.py) and `tests/` for F002 usage examples. Report, with file:line references and verbatim signatures:
1. The public read API: exact function/class names, parameters, return types, and how you select `(dataset, data_version)` (is version explicit? is there a `latest` resolution I must avoid?).
2. How `value_digest` is defined per dataset/version and where it is stored (manifest? registry?), and verbatim the function to fetch it.
3. How to enumerate valid (non-invalid) data_versions for a dataset, and how invalidity is represented.
4. The `symbol_map` structure and its digest.
5. The on-disk lake layout (partition paths, Parquet schema/columns, timestamp/timeframe semantics) and the manifest fields for a dataset version.
6. Any existing test fixtures/helpers that build a fake or real lake for tests (path + how used), especially in tests/unit and tests/integration.
Skip: F002 collector code, TimescaleDB writers, and any F001 migration detail. Return concrete code excerpts, not prose summaries.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T13:10:57Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill-F003 2>/dev/null && echo \"---SRC---\" && ls -la /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/ 2>/dev/null && echo \"---MAIN---\" && ls -la /home/georg/projects/alphamill/src/alphamill/data_bridge/ 2>/dev/null"})`
- **tool**: `glob({"pattern": "**/data_bridge/*.py", "path": "/home/georg/projects/alphamill-F003"})`
- **tool**: `glob({"pattern": "**/data_bridge/*.py", "path": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "git -C /home/georg/projects/alphamill-F003 worktree list 2>/dev/null; git -C /home/georg/projects/alphamill-F003 rev-parse --abbrev-ref HEAD 2>/dev/null; git -C /home/georg/projects/alphamill-F003 log --oneline -5 2>/dev/null"})`


> [reasoning] Let me start by exploring the repository structure. Note the worktree is at /home/georg/projects/alphamill-F003, but the working directory is /home/georg/projects/alphamill. Let me check both. The request says investigate src/alphamill/data_bridge/. Let me look in the worktree and main repo.

Let me launch parallel searches.
<analysis>
**Literal Request**: Extract verbatim F002 data_bridge reader API, identity/digest model, symbol_map structure, lake layout, and test fixtures.
**Actual Need**: A precise call contract so F003 `generators/binding.py` and `generators/lake_tensor.py` call the existing F002 reader rather than reimplementing it.
**Success Looks Like**: Exact file:line references, verbatim signatures, digest-fetch function, version enumeration/invalidity representation, symbol_map schema, Parquet columns/timestamp semantics, and reusable test lake fixtures.
</analysis>

Let me locate the F002 code in both the worktree and main repo.

  <details><summary>tool output</summary>

  ```text
total 536
drwxr-xr-x 16 georg georg   4096 Sep 18 21:10 .
drwxr-xr-x 15 georg georg   4096 Sep 18 21:10 ..
-rw-r--r--  1 georg georg    312 Sep 18 21:10 .dockerignore
-rw-r--r--  1 georg georg     69 Sep 18 21:10 .git
drwxr-xr-x  3 georg georg   4096 Sep 18 21:10 .github
-rw-r--r--  1 georg georg   1222 Sep 18 21:10 .gitignore
drwxr-xr-x  3 georg georg   4096 Sep 18 21:10 .pytest_cache
-rw-r--r--  1 georg georg    343 Sep 18 21:10 .sdd.json
-rw-r--r--  1 georg georg     99 Sep 18 21:10 AGENTS.md
-rw-r--r--  1 georg georg   2896 Sep 18 21:10 BACKLOG.md
-rw-r--r--  1 georg georg   4890 Sep 18 21:10 CLAUDE.md
-rw-r--r--  1 georg georg   3700 Sep 18 21:10 README.md
drwxr-xr-x  4 georg georg   4096 Sep 18 21:10 conversations
drwxr-xr-x  3 georg georg   4096 Sep 18 21:10 db
drwxr-xr-x  2 georg g
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 15 file(s)

/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest_validation.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/partitions.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reader.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/symbol_map.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/paths.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reconcile.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/registry.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/cli.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/digest.py
/home/georg/projects/alphamill-F003/sr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 15 file(s)

/home/georg/projects/alphamill/src/alphamill/data_bridge/partitions.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/reader.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/symbol_map.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/paths.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/reconcile.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/registry.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest_validation.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/digest.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/exporter.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/export_policy.py
/home/geo
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill      e06f4fa [main]
/home/georg/projects/alphamill-F003 e06f4fa [feat/F003-alphagen-vendor]
feat/F003-alphagen-vendor
e06f4fa chore(sdd): F003 ready-for-development → developing——最终验收 PASS 后开工
1d18e8d fix(sdd): 状态词表迁移 v4.2——门禁接受 doc-reviewing/developing/code-reviewing
d4b400d feat(f007): 流转 ready-for-development——检视闭环后状态推进（spec/BACKLOG/CLAUDE 三处同步）
612e03a docs(sdd): F003 派生索引同步 ready-for-development（BACKLOG / CLAUDE 活跃表）
7776b1f docs(reviews): F007 规格文档检视闭环——循环 14 完整 issue 表（47 条）与模式教训入库


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-18T13:11:04Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reader.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/__init__.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/registry.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/digest.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/paths.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/errors.py"})`


> [reasoning] The worktree at F003 has the same code as main. Let me read all the key files in parallel. Let me read reader.py, registry.py, manifest.py, symbol_map.py, digest.py, paths.py, partitions.py, export_summary.py, __init__.py, errors.py.
Both trees identical at F002. Reading the core files in parallel.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reader.py</path>
<type>file</type>
<content>
1: """DuckDB 研究只读取数入口（FR-003，NFR-001 零写路径）。
2: 
3: - 只按 manifest `partitions` 清单构造输入路径，**从不扫描目录**（F002-R2-02）；
4: - 返回数据前先跑清单完整性校验（存在/字节数/sha256）与 `value_digest` 重算，
5:   任一不符抛 `ManifestIntegrityError`（fail-closed，NFR-002 的技术保证）；
6: - `as_of=T` 同时施加 `event_time <= T` **与** `available_at <= T`（双时间轴，
7:   design §3）；`as_of_fidelity=event_time_only` 的 dataset 默认抛
8:   `InsufficientAsOfFidelityError`，显式 `allow_event_time_only=True` 才放行；
9: - 事后回填标签（`realized_return_60m`）在其可用时间（`evaluated_at`）晚于 T
10:   时**置 NULL 而非丢行**——丢行会让样本集随 T 变化；
11: - 带未解决质量旗的分区默认拒绝，`allow_flagged=True` 显式豁免并随附清单；
12: - 时间过滤语义：`start` 含、`end` 不含（半开区间 [start, end)）。
13: """
14: 
15: from __future__ import annot
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/__init__.py</path>
<type>file</type>
<content>
1: """Data ingestion and lake bridge components."""

(End of file - total 1 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/registry.py</path>
<type>file</type>
<content>
1: """Dataset registry——F002-D007 / R2-04 冻结的只读白名单（design §3）。
2: 
3: `export_dataset()` 与 `read()` 的 `dataset` 参数只接受 `DATASETS` 中的键，
4: 其余一律抛 `UnknownDatasetError`。投影列逐一枚举、顺序即编码顺序——摘要的
5: 稳定性取决于输入是否被完全规范化，禁止用「等」占位。
6: 
7: 类型只有五种：`timestamptz` / `text` / `double` / `jsonb` / NULL（NULL 的
8: 哨兵编码见 digest.py）。
9: """
10: 
11: from __future__ import annotations
12: 
13: from dataclasses import dataclass, field
14: from types import MappingProxyType
15: 
16: from alphamill.data_bridge.errors import UnknownDatasetError
17: 
18: TIMESTAMPTZ = "timestamptz"
19: TEXT = "text"
20: DOUBLE = "double"
21: JSONB = "jsonb"
22: 
23: AS_OF_BITEMPORAL = "bitemporal"
24: AS_OF_EVENT_TIME_ONLY = 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/digest.py</path>
<type>file</type>
<content>
1: """规范编码与 row_digest——对账口径的唯一权威实现（design §3，F002-D003/R2-04）。
2: 
3: 源侧（psycopg2 游标产出的 Python 值序列）与湖侧（PyArrow `to_pylist()` 的
4: 值序列）由**同一个函数** `canonical_row_bytes()` 编码——不让 PG 与 DuckDB 各算
5: 一次（`hashtext` 无跨引擎等价物，`sum(numeric)` 不抗抵消）。SHA-256 与聚合
6: 顺序无关且抗抵消；本模块不提供降级出口，性能不可接受走 spec 修订。
7: 
8: 编码规则（逐列，顺序 = registry 投影列顺序，无损）：
9: - `timestamptz`：UTC 微秒 int64，8 字节大端；
10: - `double`：IEEE-754 binary64 原始位模式 8 字节大端（**不得 Decimal 定标**），
11:   `-0.0` 归一为 `+0.0`，NaN 归一为单一静默 NaN 位型；
12: - `text`：UTF-8 字节，前置 uint32 大端长度；
13: - `jsonb`：规范 JSON（键按 Unicode 码点排序、无空白）后按 `text` 编码；
14: - NULL：单字节哨兵 `0x00`；非 NULL 前置 `0x01`，哨兵不与任何值碰撞。
15: 
16: 排序键 = 该行的规范编码字节串本身（字典序），不是逻辑主键——`signals_log`
17: 无主
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/paths.py</path>
<type>file</type>
<content>
1: """湖根路径与目录布局约定（design §3）。
2: 
3: 唯一入口 `lake_root()`：默认仓库根 `lake/`，可用环境变量 `ALPHAMILL_LAKE_DIR`
4: 覆盖（测试与多环境部署用）。所有模块经此处取湖路径，不各自硬编码。
5: """
6: 
7: from __future__ import annotations
8: 
9: import os
10: from pathlib import Path, PureWindowsPath
11: 
12: from alphamill.data_bridge.errors import DataBridgeError
13: 
14: REPO_ROOT = Path(__file__).resolve().parents[3]
15: 
16: 
17: def lake_root() -> Path:
18:     override = os.getenv("ALPHAMILL_LAKE_DIR", "").strip()
19:     if override:
20:         return Path(override).expanduser().resolve()
21:     return (REPO_ROOT / "lake").resolve()
22: 
23: 
24: def manifests_dir(root: Path, dataset: str) -> Path:
25:     return root / "_m
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/errors.py</path>
<type>file</type>
<content>
1: """F002 数据桥异常契约（design §4）。
2: 
3: 取数与导出对以下任一情形一律抛错，不降级为警告（D4 数据红线；本 feature
4: 无 SOP 所述的「安全校验降级声明」出口）。
5: """
6: 
7: 
8: class DataBridgeError(Exception):
9:     """数据桥异常基类。"""
10: 
11: 
12: class UnknownDatasetError(DataBridgeError):
13:     """dataset 不在 registry 白名单中。"""
14: 
15: 
16: class VersionNotFoundError(DataBridgeError):
17:     """请求的 data_version manifest 不存在，或不存在任何 valid 版本。"""
18: 
19: 
20: class InvalidVersionError(DataBridgeError):
21:     """请求的 data_version 已被标记 invalid，消费端拒绝读取。"""
22: 
23: 
24: class ManifestIntegrityError(DataBridgeError):
25:     """manifest 清单内文件缺失、字节数或 sha256 不符，或 value_digest 缺失/重算不符。
26: 
27:     不含「目录里存在本版本未引用的文件」——`.rN` 共享模型下那是其他版
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:08Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/symbol_map.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/partitions.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/export_summary.py"})`


> [reasoning] Now let me read manifest.py, symbol_map.py, partitions.py, export_summary.py, manifest_validation.py. Also registry reference. Let me do these in parallel.
Now the identity/manifest/symbol_map/partition layers.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py</path>
<type>file</type>
<content>
1: """manifest 契约读写、data_version 排序、完整性与增量合成（design §3/§4，架构 §4.4）。
2: 
3: 关键不变量：
4: - `partitions` 是必填的版本身份；reader 只按清单构造输入路径，从不扫描目录
5:   （F002-R2-02）——完整性校验逐项验存在/字节数/sha256，任一不符即
6:   `ManifestIntegrityError`，不要求目录全集相等（`.rN` 共享模型）。
7: - `value_digest` 是 DatasetVersion 的语义根摘要：只含 dataset、registry 投影与
8:   分区级 (key, rows, bounds, row_digest)，不含物理 path/codec/bytes/sha256/
9:   exported_at（F002-D011）。
10: - manifest 合成是**累计完整快照**而非一日 delta：增量从上一 valid 清单继承基线，
11:   full 用基线复用未变文件但按当前源库组成版本；本轮分区按逻辑分区键替换/追加，
12:   `rows`/`pairs`/quality 重算，`skipped` 走同样的继承/替换（F002-R2-03/R3-03）。
13: """
14: 
15: from __future__ import annotations
16: 
17: import errno
18: import hashlib
19: import j
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/symbol_map.py</path>
<type>file</type>
<content>
1: """symbol_map：湖内 pair ↔ Freqtrade pair 的映射与内容寻址发布（design §4）。
2: 
3: 映射键冻结为 **(exchange, market_type, db_symbol)**（F002-D010）——库内
4: `DISTINCT symbol` 不足以无损推导（spot 与 perp 的 `BTC/USDT` 是不同标的）。
5: 输出格式冻结：spot `BTC/USDT → BTC-USDT`（Freqtrade `BTC/USDT`）、perp
6: `BTC/USDT[:USDT] → BTC-USDT-PERP`（Freqtrade `BTC/USDT:USDT`）。任意两行推导
7: 出相同 lake_pair 即为碰撞，导出直接失败（`SymbolCollisionError`）。
8: 
9: current 副本位于湖元数据目录，不改写源码树；它不是可复现身份：canonical CSV
10: （五列排序、UTF-8、LF、固定表头）原子发布到
11: `lake/_metadata/symbol_maps/<digest>.csv`，digest 为 canonical bytes 的
12: SHA-256；已有同 digest 文件必须逐字节一致。ResearchSnapshot 只引用显式 digest。
13: """
14: 
15: from __future__ import annotations
16: 
17: import csv
18: 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/partitions.py</path>
<type>file</type>
<content>
1: """分区文件层操作：单元格发现、`.rN` 写入、空单元格判定、质量标记（design §3）。
2: 
3: 本模块只做「源行集 → 湖分区文件」的机械转换与窗口内的网格判定；导出编排
4: （事务、基线继承、manifest 合成与发布）在 exporter.py。分区写入永不覆盖：
5: 内容变化写 `.rN+1`，序号由盘上现有最大值推导，孤儿文件不阻塞重跑。
6: """
7: 
8: from __future__ import annotations
9: 
10: import datetime as dt
11: import re
12: from collections import defaultdict
13: from pathlib import Path
14: from typing import Any
15: 
16: import pyarrow as pa
17: import pyarrow.parquet as pq
18: 
19: from alphamill.data_bridge import manifest as mf
20: from alphamill.data_bridge import paths, reconcile, registry, symbol_map
21: from alphamill.data_bridge.digest import canonical_json_text, canonical_row_bytes, row_digest
22: from
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/export_summary.py</path>
<type>file</type>
<content>
1: """导出摘要构造；与数据库/湖文件编排解耦。"""
2: 
3: from __future__ import annotations
4: 
5: import time
6: from typing import Any
7: 
8: from alphamill.data_bridge import registry
9: 
10: 
11: def build_summary(
12:     spec: registry.DatasetSpec,
13:     mode: str,
14:     data_version: str | None,
15:     baseline_version: str | None,
16:     merged: list[dict[str, Any]],
17:     failures: list[dict[str, Any]],
18:     skipped: list[dict[str, str]],
19:     reconcile_field: dict[str, Any],
20:     *,
21:     excluded: int,
22:     started: float,
23:     no_op: bool,
24:     reason: str | None,
25:     revision_diff: list[dict[str, Any]],
26: ) -> dict[str, Any]:
27:     return {
2
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:13Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest_validation.py"})`
- **tool**: `bash({"command": "find /home/georg/projects/alphamill-F003/tests -type f -name '*.py' | sort"})`
- **tool**: `grep({"pattern": "data_bridge|lake_root|write_partition|load_manifest|read\\(|symbol_map|value_digest", "path": "/home/georg/projects/alphamill-F003/tests", "output_mode": "files_with_matches"})`


> [reasoning] Now let me read manifest_validation.py to understand manifest shape and status values, and look at tests for F002. Also need to see the manifest fields, especially status "invalid"/"valid"/"no-op"? Note export_summary sets status to "valid"/"invalid"/"no-op". But reader checks `manifest["status"] == "invalid"`, and latest_valid_version checks `== "valid"`. Interesting: "no-op" status would not be valid. Let me check manifest_validation.py.

Also need tests. Let me search tests for data_bridge.
Now manifest shape validation and the F002 test fixtures.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest_validation.py</path>
<type>file</type>
<content>
1: """manifest 结构、版本绑定与分区路径的 fail-closed 校验。"""
2: 
3: from __future__ import annotations
4: 
5: import json
6: import re
7: from datetime import date
8: from pathlib import Path, PureWindowsPath
9: from typing import Any
10: 
11: from alphamill.data_bridge import paths
12: from alphamill.data_bridge.errors import (
13:     DataBridgeError,
14:     ManifestIntegrityError,
15:     UnknownDatasetError,
16: )
17: from alphamill.data_bridge.registry import require_dataset
18: 
19: DATA_VERSION_RE = re.compile(r"^v(\d{4})\.(\d{2})\.(\d{2})(?:-r([1-9]\d*))?$")
20: PARTITION_FILE_RE = re.compile(r"^date=(\d{4}-\d{2}-\d{2})\.r([1-9]\d*)\.parquet$")
21: SHA256_DIGEST_RE = re
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/tests/integration/conftest.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_dryrun_monitoring.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_kronos_smoke.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_row_reconciliation.py
/home/georg/projects/alphamill-F003/tests/integration/test_f002_export_reconcile.py
/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py
/home/georg/projects/alphamill-F003/tests/integration/test_f002_revision.py
/home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py
/home/georg/projects/alphamill-F003/tests/integration/test_f003_kronos_lifecycle.py
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 22 match(es) in 22 file(s)

/home/georg/projects/alphamill-F003/tests/unit/test_f002_timer_contract.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_symbol_map.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_registry.py

/home/georg/projects/alphamill-F003/tests/unit/test_symbol_manager.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_paths.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_manifest.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_exporter.py

/home/georg/projects/alphamill-F003/tests/unit/test_f002_digest.py

/home/georg/projects/alphamill-F003/tests/unit/test_historical_backfill_review_fixes.py

/home/georg/projects/alphamill-F003/tests/unit/test_f004_kronos_runtime_contract.py

/home/georg/projects/alphami
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:18Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/conftest.py"})`


> [reasoning] Now let me read the key test files: test_f002_reader_contract.py, test_f002_manifest.py, test_f002_partitions.py, test_f002_symbol_map.py, tests/integration/test_f002_reader.py, tests/integration/conftest.py, and test_f002_exporter.py to find fixtures. Let me read them in parallel.
Reading the F002 tests and fixtures.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py</path>
<type>file</type>
<content>
1: """F002 reader 的本地湖边界测试（不依赖 TimescaleDB）。"""
2: 
3: from datetime import UTC, datetime
4: 
5: import pyarrow.parquet as pq
6: 
7: from alphamill.data_bridge import digest, manifest, partitions, symbol_map
8: from alphamill.data_bridge.reader import read
9: from alphamill.data_bridge.registry import require_dataset
10: 
11: 
12: def test_pair_filter_uses_manifest_mapping_and_requested_lake(tmp_path, monkeypatch):
13:     spec = require_dataset("signals_log")
14:     event_time = datetime(2026, 9, 11, 9, tzinfo=UTC)
15:     rows = [
16:         [
17:             event_time,
18:             "binance",
19:             "BTC/USDT",
20:             "placeholder",
21:            
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py</path>
<type>file</type>
<content>
1: """F002 DuckDB 取数入口集成测试（AC-003/008/009/013）。
2: 
3: 复用 conftest 的一次性 f002_integration 库与种子数据；真实 TimescaleDB
4: 在线时运行，否则按 SOP 约定跳过（ALPHAMILL_INTEGRATION=1 下判红）。
5: """
6: 
7: from __future__ import annotations
8: 
9: import datetime as dt
10: 
11: import pytest
12: from conftest import D1, D3, D4, seed_f002_data
13: 
14: from alphamill.data_bridge import manifest as mf
15: from alphamill.data_bridge.errors import (
16:     FlaggedPartitionError,
17:     InsufficientAsOfFidelityError,
18:     ManifestIntegrityError,
19: )
20: from alphamill.data_bridge.exporter import export_dataset
21: from alphamill.data_bridge.reader import read
22: 
23: pytestmark = pytest.mark.integratio
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/integration/conftest.py</path>
<type>file</type>
<content>
1: """Load the local deployment environment for host-side integration tests."""
2: 
3: from __future__ import annotations
4: 
5: import os
6: import subprocess
7: from pathlib import Path
8: 
9: import psycopg2
10: import pytest
11: 
12: CONTAINER = "quant-timescaledb"
13: F002_DB = "f002_integration"
14: REPO = Path(__file__).resolve().parents[2]
15: 
16: # F002 种子日（过去日期，与真实数据窗口无冲突）
17: D1, D2, D3, D4 = "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04"
18: 
19: 
20: def pytest_configure() -> None:
21:     dotenv = REPO / "deployment/.env"
22:     if dotenv.is_file():
23:         for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
24:             line = raw_line.stri
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:22Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_exporter.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_symbol_map.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_manifest.py"})`
- **tool**: `grep({"pattern": "class .*(Snapshot|ResearchSnapshot|DatasetVersion|Identity|LakeRef|SnapshotRef)|def (open_snapshot|snapshot|resolve_snapshot|dataset_identity)", "path": "/home/georg/projects/alphamill-F003/src", "output_mode": "content"})`


> [reasoning] Now I have a lot. Let me read the remaining test files for fixtures: test_f002_manifest.py (synthesize / value_digest), test_f002_partitions.py, test_f002_symbol_map.py, test_f002_exporter.py, and maybe test_f002_registry.py. Also check the exporter.py public API (export_dataset signature) since F003 might need to build a lake in tests. And check if there's a Reader class / research snapshot elsewhere. The request mentions "snapshot/dataset identity model" and symbol_map. Let me also check docs for F002 design reference and search for a ResearchSnapshot / Snapshot class. Let me grep for "snapshot" in src.

Let me read test_f002_exporter.py, test_f002_manifest.py, test_f002_symbol_map.py, and grep for snapshot / ResearchSnapshot / DataVersion.
Now exporter API + remaining fixtures, and any snapshot/identity classes elsewhere.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_exporter.py</path>
<type>file</type>
<content>
1: """F002 导出窗口边界测试。"""
2: 
3: import datetime as dt
4: 
5: import psycopg2
6: import pytest
7: 
8: from alphamill.data_bridge import export_policy, exporter, registry
9: from alphamill.data_bridge import manifest as mf
10: from alphamill.data_bridge.errors import DataBridgeError
11: 
12: 
13: def _partition(pair: str) -> dict:
14:     return {
15:         "logical_partition_key": {"exchange": "binance", "pair": pair, "date": "2026-09-14"},
16:         "path": f"ohlcv_1m/exchange=binance/pair={pair}/date=2026-09-14.r1.parquet",
17:         "rows": 1,
18:         "time_min": "2026-09-14T00:00:00Z",
19:         "time_max": "2026-09-14T00:00:00Z",
20:         "row_digest": "sha256:" +
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_symbol_map.py</path>
<type>file</type>
<content>
1: """T005 / AC-004：symbol_map 生成、双向解析、内容寻址发布与可重放。"""
2: 
3: import pandas as pd
4: import pytest
5: 
6: from alphamill.data_bridge import symbol_map as sm
7: from alphamill.data_bridge.errors import (
8:     DataBridgeError,
9:     SymbolCollisionError,
10:     SymbolNotFoundError,
11: )
12: 
13: ROWS = [
14:     sm.SymbolRow("binance", "spot", "BTC/USDT"),
15:     sm.SymbolRow("binance", "spot", "ETH/USDT"),
16:     sm.SymbolRow("binanceusdm", "perp", "BTC/USDT"),
17: ]
18: 
19: 
20: class _FakeCursor:
21:     def __init__(self, rows_by_table: dict[str, list[tuple]], executed: list[str]):
22:         self._rows = rows_by_table
23:         self._executed = executed
24: 
25:     
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_manifest.py</path>
<type>file</type>
<content>
1: """T002 / AC-011·AC-015（单测部分）：manifest 契约读写、版本排序、完整性、
2: 增量合成与 value_digest 的正反两面测试。"""
3: 
4: import json
5: from dataclasses import replace
6: from datetime import UTC, date, datetime
7: 
8: import pytest
9: 
10: from alphamill.data_bridge import manifest as mf
11: from alphamill.data_bridge import paths
12: from alphamill.data_bridge.errors import (
13:     ManifestIntegrityError,
14:     UnknownDatasetError,
15:     VersionNotFoundError,
16: )
17: from alphamill.data_bridge.registry import DOUBLE, Column, require_dataset
18: 
19: SPEC = require_dataset("ohlcv_1m")
20: 
21: 
22: def _partition(pair: str, day: str, rows: int, digest_hex: str, **overrides) -> dict:
23:     entr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No matches found
  ```
  </details>

## assistant · 2026-09-18T13:11:27Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/exporter.py"})`
- **tool**: `grep({"pattern": "data_bridge|reader\\.read|latest_valid_version|value_digest|symbol_map|binding|lake_tensor", "path": "/home/georg/projects/alphamill-F003/docs", "output_mode": "files_with_matches"})`


> [reasoning] No ResearchSnapshot in src yet (that's likely F003/F006). Now I need the exporter.py public API for `export_dataset`, and the export_policy. Let me read exporter.py signature and cli.py to see CLI entry points. Also check docs for F003 spec referencing data_bridge. Let me also read the __init__ etc. Let me get exporter signature and export_policy briefly.

Also the request mentions `export_summary.py` — done. Let me read exporter.py at least the export_dataset signature and the manifest fields it writes. Let me grep for the manifest assembly in exporter.py.
Reading exporter public API and manifest assembly, plus F003 spec references.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/exporter.py</path>
<type>file</type>
<content>
1: """TimescaleDB → Parquet 导出编排：快照读取、分区写入、对账与 manifest 发布。
2: 
3: 增量版本继承未变分区；full 版本以当前源库全量结果为组成，但仍复用未变文件。
4: 文件与 manifest 的发布均不可变；对账失败保留 invalid 审计版本。CLI 入口见底部 `main()`。
5: """
6: 
7: from __future__ import annotations
8: 
9: import datetime as dt
10: import logging
11: import time
12: from pathlib import Path
13: from typing import Any
14: 
15: from alphamill.data_bridge import manifest as mf
16: from alphamill.data_bridge import partitions, paths, reconcile, registry, symbol_map
17: from alphamill.data_bridge.collector.db_writer import db_connect
18: from alphamill.data_bridge.errors import DataBridgeError, VersionNotFoundError
19: from alphamill.data_bridge.export_policy 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 23 match(es) in 23 file(s)

/home/georg/projects/alphamill-F003/docs/alphamill-integration.md

/home/georg/projects/alphamill-F003/docs/alphamill-prd.md

/home/georg/projects/alphamill-F003/docs/alphamill-architecture.md

/home/georg/projects/alphamill-F003/docs/README.md

/home/georg/projects/alphamill-F003/docs/SOP.md

/home/georg/projects/alphamill-F003/docs/features/0.1/F001-quant-crypto-migration/design.md

/home/georg/projects/alphamill-F003/docs/features/0.1/F001-quant-crypto-migration/migration-plan.md

/home/georg/projects/alphamill-F003/docs/features/0.1/F001-quant-crypto-migration/tasks.md

/home/georg/projects/alphamill-F003/docs/features/0.1/F001-quant-crypto-migration/spec.md

/home/georg/projects/alphamill-F003/docs/design/ui-mockup/app.js

/home/georg/projects/alphami
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:31Z

- **tool**: `bash({"command": "wc -l /home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/spec.md /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/tasks.md /home/georg/projects/alphamill-F003/docs/decisions/0007-research-snapshot-binding.md"})`
- **tool**: `grep({"pattern": "read\\(|ReadResult|latest_valid_version|value_digest|symbol_map_digest|binding|lake_tensor|data_version|ALPHAMILL_LAKE_DIR", "path": "/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md", "output_mode": "content", "head_limit": 120})`


> [reasoning] The F003 design/spec likely references the F002 reader API. Let me read the F003 design and spec for binding.py/lake_tensor.py and the F002 design for §3 and reader contract. Also ADR-0007 research-snapshot-binding. This will help confirm the intended API contract for F003.

Let me read F003 design.md, F003 spec.md, F002 design.md (maybe large), and ADR-0007. Let me check sizes first, then read. Actually let me just read them.
Reading F002 design §3/§4 and the F003 binding spec to confirm intended usage.

  <details><summary>tool output</summary>

  ```text
431 /home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md
   277 /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md
   355 /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/spec.md
   129 /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/tasks.md
   114 /home/georg/projects/alphamill-F003/docs/decisions/0007-research-snapshot-binding.md
  1306 total


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 21 match(es) in 1 file(s)

/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md
  24: - **ADR / 上游 Contract**：ADR-0001（选型、冒烟闸门、降级判据）、ADR-0002（vendor 卫生规则、pin 纪律、永不 fork）、ADR-0003（门禁不降级）、ADR-0007（快照绑定）；F002 的 `alphamill.data_bridge.reader.read()` 与 `(dataset, data_version, value_digest)` 身份
  42: - 并行依赖：`F008` 宇宙扩容会把 `ohlcv_1m` 的 pair 数从 6 抬到 30~50——数据面代码不需要改（`lake_tensor` 本就按绑定解析 pair 集合），但显存占用与横截面 reward 信噪比随之变化，故 `universe` 必须进运行记录
  54: │   ├── binding.py            # SnapshotBinding：research_snapshot_id | 显式元组（FR-003, Q-002）
  55: │   ├── lake_tensor.py        # 快照绑定 → (T×P×F) 张量 + PIT 掩码 + feature_map（FR-003；掩码消费 F008 `universe_at(T)`）
  78: | 生成器 → 数据 | 只经 `data_bridge.reader.read()`；`lake_tensor` 是唯一取数入口，其他模块不得自行读湖 |
  82: | PIT 宇宙 → F008 | `lak
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:37Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md", "offset": 100, "limit": 140})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/decisions/0007-research-snapshot-binding.md"})`
- **tool**: `grep({"pattern": "value_digest|data_version|symbol_map|manifest|partition|read\\(|latest_valid|invalid", "path": "/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/spec.md", "output_mode": "content", "head_limit": 80})`


> [reasoning] The F003 design/spec has the exact binding model. Let me read the F003 design.md fully around the binding/ResearchSnapshot section, and F002 design §3/§4. Let me read F003 design lines 110-230 and F002 design fully or relevant sections. Also ADR-0007.

The request specifically asks: "Report, with file:line references and verbatim signatures: 1. public read API ... 2. value_digest ... 3. enumerate valid non-invalid data_versions ... 4. symbol_map structure and digest ... 5. on-disk lake layout ... 6. test fixtures."

I have most. Need to check F002 design for the dataset version manifest fields and reader contract. But the code is authoritative. Let me read F003 design 110-230 and ADR-0007 for the binding semantics (the user is implementing binding.py). And F002 design §3 relevant sections.

Let me read F003 design 100-230 and ADR-0007, and F002 spec read API section. Also check tasks.md for F003 to see task names. Let me be efficient.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md</path>
<type>file</type>
<content>
100: └── checkpoints/              # 训练 checkpoint（可清理，不属于证据）
101: ```
102: 
103: **终态与可消费性**：`run.json` 是唯一运行事实，四种终态 `completed` / `rejected` / `failed` / `partial` 都必须写出，字段至少含 `status`、`termination`、`reason`、`started_at`/`finished_at`；写出之前目录一律视为未完成（与 F002「manifest 最后写」同构）。若终态 manifest 自身写出失败，目录同样视为未完成（fail-safe），不得凭残留物推断终态。**只有 `status=completed` 的运行可被下游消费**：`rejected`/`failed` 不产出候选；`partial` 的 `factors/` 仅作 `show` 诊断残留、不得被下游入册，且不产出 `pool.json`。
104: 
105: **FactorDef（`schema_version: 1`）**：`factor_id` / `definition_digest` / `hypothesis_id` / `name` / `generator` / `generator_version` / `scope` / `expression` / `params` / `data_columns` / `feature_map_digest` / 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/decisions/0007-research-snapshot-binding.md</path>
<type>file</type>
<content>
1: # ADR-0007：研究快照绑定 —— 独立 DatasetVersion 的不可变组合
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted（2026-09-18 修订：universe/calendar 拆为两个独立 artifact 引用并冻结 `universe_calendar_digest` 组合公式，见文末「修订记录」）
5: - 决策人：Georg
6: - 背景：PRD FR1/FR7；F002 dataset 独立版本；F007 多数据集评测与实验身份；ADR-0006
7: 
8: ## 背景
9: 
10: F002 已决定 `data_version` 按 dataset 独立递增，因为 OHLCV、funding、basis、OI 与 signals
11: 具有不同采集节奏和失败域。这个决定对数据桥是正确的，但不能直接充当多数据集实验身份：
12: 若 F007 在运行时分别解析各 dataset 的 “latest valid”，相同命令在不同时间会绑定到不同版本，
13: 还可能把不同 source snapshot、不同覆盖范围的数据临时拼成一个不可复现的输入。
14: 
15: 用各 manifest 的 `exported_at` 临时聚合也不足以解决问题。`exported_at` 是写出 provenance，
16: 不是跨 dataset 的一致性边界；它既不固定 point-in-time universe/symbol map，也不证明各成员
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 69 match(es) in 1 file(s)

/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/spec.md
  21: - **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
  22: - **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/宇宙扩容)、§2.2(symbol_map.csv M1 出口标准)
  28: - **一句话意图**:把 TimescaleDB 的修订态数据按日导出为带 manifest 的不可变 Parquet 快照,并提供拒绝失效版本的 DuckDB 研究取数入口,使挖掘/评测/回测从同一版数据算出同一版结果。
  38: - `lake/` 内出现分区化 Parquet 快照(ohlcv_1m、衍生品三表、signals_log),每次导出附 manifest(dataset/rows/data_version/value_digest/对账状态);
  39: - 导出与 TimescaleDB 逐 dataset 对账(行数 + 时间边界 + `row_digest`,口径见 design §3 唯一权威定义),不一致的 data_version 被标记 `invalid`;
  40: - 提供统一 DuckDB 取数模块:按 dataset+data_version 查询,**拒绝读取 inv
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:42Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_partitions.py"})`
- **tool**: `grep({"pattern": "value_digest|symbol_map_digest|data_version|as_of_fidelity|partitions|skipped|quality|source_snapshot|_manifests|date=", "path": "/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md", "output_mode": "content", "head_limit": 100})`


> [reasoning] I now have essentially everything. Let me check the F002 design §3 for the on-disk layout and manifest JSON fields, to give exact manifest field list. But the code shows the manifest fields. Let me also verify the timestamp/timeframe semantics — reader returns UTC timestamps from parquet; `event_time` for each dataset. time is stored as timestamptz (UTC micros). timeframe column in OI/basis. For ohlcv no timeframe column (1m implicit). Let me double check partitions `_ARROW_TYPES` and registry projections: done.

Also check `tests/unit/test_f002_partitions.py` for a fake lake builder helper and `tests/unit/test_f002_manifest.py` has `_write_partition_file` helper. Let me quickly check test_f002_partitions.py and test_f002_paths.py for fixtures/helpers. And search for a reusable helper named something like "build_lake" across tests.

Let me grep for helper functions building manifests in tests: `publish_manifest`, `rows_to_table`, `write_partition`, `_write_partition_file`. Already saw several. Let me read test_f002_partitions.py quickly to confirm any lake-building helper.

Also, the question 3 asks how to enumerate valid versions and how invalidity is represented. `manifest.list_versions(root, dataset)` returns all versions sorted; `latest_valid_version` returns latest status=="valid". Invalid is `manifest["status"] == "invalid"`; there's no public "list_valid_versions", but one can iterate list_versions + load_manifest. Important: `read()` raises InvalidVersionError for invalid explicit version, and latest_valid_version skips invalid. But note: a `status` of "invalid" or "valid" only — manifest_validation rejects anything else; export_summary can produce "no-op" but those aren't published (no_op returns before publish). So status is only valid|invalid.

Also note `latest_valid_version` exists in two places: `reader.latest_valid_version(dataset, lake_root)` (public convenience returning str) and `manifest.latest_valid_version(root, dataset)`.

For question 2: value_digest stored in manifest JSON under `value_digest`, computed by `manifest.compute_value_digest(spec, partitions)` (manifest.py:168), verified by `manifest.verify_value_digest(spec, manifest)` (manifest.py:191). `ReadResult.value_digest` returns it (reader.py:117,163). There's no per-dataset-version registry; it's in the manifest. symbol_map_digest in manifest.

Question 4: symbol_map structure: COLUMNS tuple, SymbolRow dataclass, SymbolMapRef, load_symbol_map, export_symbol_map, digest = content_digest(canonical_csv_bytes(frame)) = "sha256:"+hex. Stored at lake/_metadata/symbol_maps/<digest>.csv; current at lake/_metadata/symbol_map.csv.

Question 5: lake layout: paths.partition_dir, partition_filename `date=<date>.r<rev>.parquet`; manifests at lake/_manifests/<dataset>/<data_version>.json; staging at _staging/<dataset>/<version>. Parquet schema = projection columns. timestamp semantics UTC. timeframe: partition key for OI/basis; ohlcv only 1m implicitly (no timeframe column). reader SQL `read_parquet(?::VARCHAR[], hive_partitioning=false)` — note hive_partitioning=false, so partition dirs are NOT exposed as columns; only columns inside the parquet file. Since file only stores projection columns and not exchange/pair/timeframe partition dims... wait, let's check: the parquet written by `write_partition` uses `rows_to_table(sorted_rows, spec)` where spec.projection includes exchange & symbol but NOT pair. The partition dir contains exchange=, pair=, timeframe=. But hive_partitioning=false means those dir values are not added; the file itself has exchange and symbol columns (from projection). pair isn't in projection, symbol is. So filtering by pair uses symbol_map.to_db_symbols. Good, important detail: pair is NOT a column in the parquet; symbol is the column. timeframe IS a column in OI/basis projection. For ohlcv there is no timeframe column.

Let me verify by reading the F002 design §3 quickly for the manifest JSON contract and partition/timestamp semantics, plus check test_f002_partitions for helper. Let me read design.md relevant lines (~150-300). Actually I have enough. But to be thorough on question 5, let me read the design doc's data model section. Let me grep in F002 design for the manifest example JSON.

Let me also read test_f002_partitions.py and test_f002_paths.py to answer Q6 fully.
Checking the F002 design manifest contract and partition test helpers.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_partitions.py</path>
<type>file</type>
<content>
1: """F002 分区辅助函数边界测试。"""
2: 
3: import datetime as dt
4: 
5: import pytest
6: 
7: from alphamill.data_bridge import partitions, registry
8: from alphamill.data_bridge.errors import DataBridgeError
9: from alphamill.data_bridge.partitions import as_date
10: 
11: 
12: def test_naive_datetime_is_interpreted_as_utc():
13:     assert as_date(dt.datetime(2026, 9, 14, 0, 30)) == dt.date(2026, 9, 14)
14: 
15: 
16: class _Cursor:
17:     def __init__(self):
18:         self.sql = ""
19: 
20:     def __enter__(self):
21:         return self
22: 
23:     def __exit__(self, *exc):
24:         return False
25: 
26:     def execute(self, sql, params):
27:         self.sql = sql
28: 
29:     d
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 65 match(es) in 1 file(s)

/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md
  32: - Event / Evidence:`lake/_manifests/<dataset>/<data_version>.json` 与内容寻址 symbol-map artifact
  42: ├── manifest.py       # 新增:manifest 契约读写、data_version 排序、invalid 标记
  79: **写进 manifest 的 `as_of_fidelity: "event_time_only"`**,并由 `read()` 默认拒绝(见 §4);要做真正的
  90: ├── ohlcv_1m/exchange=binance/pair=BTC-USDT/date=2026-09-11.r1.parquet
  91: │                                           date=2026-09-11.r2.parquet   # 修订产生新文件
  92: ├── derivatives_funding_rates/exchange=binance/pair=.../date=....r1.parquet
  95: ├── signals_log/date=....r1.parquet        # 无 exchange 维度,按事件日
  96: └── _manifests/<dataset>/<data_version>.json
  99: 旧文件原样留存。版本与文件的绑定**不靠路径推导,靠 manifest 的 `partitions
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:52Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_paths.py"})`
- **tool**: `bash({"command": "find /home/georg/projects/alphamill-F003/tests -name 'conftest.py' -o -name 'pytest.ini' -o -name 'pyproject.toml' | sort; echo '---'; ls -la /home/georg/projects/alphamill-F003/tests /home/georg/projects/alphamill-F003/tests/unit /home/georg/projects/alphamill-F003/tests/integration | head -60"})`
- **tool**: `grep({"pattern": "def (rows_to_table|write_partition|publish_manifest|read|export_dataset|load_symbol_map|build_symbol_map|compute_value_digest|verify_value_digest|list_versions|load_manifest|latest_valid_version)", "path": "/home/georg/projects/alphamill-F003/src/alphamill/data_bridge", "output_mode": "content"})`


> [reasoning] I now have the full picture. Let me also confirm the exact reader signature from design §4 (lines ~294-334) to give verbatim. Already have from code. Let me read design lines 290-360 for the exact read signature and symbol_map section to cross-check. Actually I have code, which is authoritative. But the design gives a documented contract; the request wants verbatim signatures with file:line. I have all file:line.

Let me also check test_f002_paths.py for the layout assertions, and test_f002_registry.py perhaps. Also check if there's a helper to build a real/fake lake. The best reusable helpers:
- `partitions.rows_to_table(rows, spec)` + `pq.write_table`
- `partitions.write_partition(root, spec, key, rows)` - writes real partition + returns manifest entry
- `manifest.publish_manifest(root, manifest)`
- tests/unit/test_f002_reader_contract.py builds a full fake lake inline.
- tests/integration/conftest.py f002_lake fixture + seed_f002_data + export_dataset.

Let me check test_f002_paths.py quickly for exact path layout assertions, and check whether there's a conftest at tests/ root or unit. Let me glob conftest.
Checking path layout assertions and conftest availability.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_paths.py</path>
<type>file</type>
<content>
1: """F002 湖路径边界测试。"""
2: 
3: import pytest
4: 
5: from alphamill.data_bridge import paths
6: from alphamill.data_bridge.errors import DataBridgeError
7: 
8: 
9: @pytest.mark.parametrize("value", ["../escape", "nested/value", r"nested\\value", ""])
10: def test_partition_dimension_cannot_escape_lake(tmp_path, value):
11:     with pytest.raises(DataBridgeError, match="非法分区路径组件"):
12:         paths.partition_dir(tmp_path, "ohlcv_1m", {"exchange": value})

(End of file - total 12 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/tests/integration/conftest.py
---
/home/georg/projects/alphamill-F003/tests:
total 28
drwxr-xr-x  7 georg georg 4096 Sep 18 21:11 .
drwxr-xr-x 17 georg georg 4096 Sep 18 21:11 ..
drwxr-xr-x  3 georg georg 4096 Sep 18 21:11 .pytest_cache
drwxr-xr-x  3 georg georg 4096 Sep 18 21:10 integration
drwxr-xr-x  2 georg georg 4096 Sep 18 21:10 property
drwxr-xr-x  2 georg georg 4096 Sep 18 21:10 simulation
drwxr-xr-x  3 georg georg 4096 Sep 18 21:10 unit

/home/georg/projects/alphamill-F003/tests/integration:
total 92
drwxr-xr-x 3 georg georg  4096 Sep 18 21:10 .
drwxr-xr-x 7 georg georg  4096 Sep 18 21:11 ..
-rw-r--r-- 1 georg georg     0 Sep 18 21:10 .gitkeep
drwxr-xr-x 2 georg georg  4096 Sep 18 21:11 __pycache__
-rw-r--r-- 1 georg georg  8056 Sep 18 21:10 con
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 13 match(es) in 5 file(s)

/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/partitions.py
  93: def rows_to_table(rows: list[list[Any]], spec: registry.DatasetSpec) -> pa.Table:
  158: def write_partition(

/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/exporter.py
  110: def export_dataset(

/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py
  86: def list_versions(root: Path, dataset: str) -> list[str]:
  95: def load_manifest(root: Path, dataset: str, data_version: str) -> dict[str, Any]:
  120: def latest_valid_version(root: Path, dataset: str) -> str:
  168: def compute_value_digest(spec: DatasetSpec, partitions: list[dict[str, Any]]) -> str:
  191: def verify_value_digest(spec: DatasetSpec, manifest: dict[str, Any]) -> str:
  2
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:59Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md", "offset": 285, "limit": 75})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_registry.py"})`


> [reasoning] I have everything. Let me verify the design's read signature lines 290-360 to confirm documented parameters (the design might show more/additional). Let me read design lines 285-360. This matters because the request wants "exact public API ... parameters". Code is authoritative, but design may note the intended. Let me read that block quickly, plus check `tests/unit/test_f002_registry.py` for projection/timeframe semantics. Actually, let me read design 285-360 and registry test.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/features/0.2/F002-data-bridge/design.md</path>
<type>file</type>
<content>
285: DATASETS: Mapping[str, DatasetSpec]          # 只读;未登记的名字 → UnknownDatasetError
286: 
287: # exporter.py
288: def export_dataset(dataset: str, mode: Literal["incremental", "full"],
289:                    window_end: datetime | None = None) -> dict   # 返回 manifest 摘要
290: # reader.py —— start/end 切 registry 声明的 event_time;as_of 另加 available_at 约束
291: @dataclass(frozen=True)
292: class ReadResult:
293:     frame: pd.DataFrame
294:     dataset: str
295:     data_version: str              # 即使调用方传 None,也回报实际解析版本
296:     value_digest: str              # 来自已校验 manifest 的 canonical row/value digest
297:     as_of: datetime | None          # None = 纯历史切片,不得用于回测/门禁判定
298:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f002_registry.py</path>
<type>file</type>
<content>
1: """T015：dataset registry 白名单契约（design §3 表逐一核对）。"""
2: 
3: import pytest
4: 
5: from alphamill.data_bridge import registry
6: from alphamill.data_bridge.errors import UnknownDatasetError
7: 
8: EXPECTED_PROJECTIONS = {
9:     "ohlcv_1m": ["time", "exchange", "symbol", "open", "high", "low", "close", "volume"],
10:     "derivatives_funding_rates": [
11:         "time",
12:         "exchange",
13:         "symbol",
14:         "funding_rate",
15:         "next_funding_time",
16:         "mark_price",
17:         "index_price",
18:         "metadata",
19:         "ingested_at",
20:     ],
21:     "derivatives_open_interest": [
22:         "time",
23:         "exchange",
24:        
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:12:04Z


> [reasoning] I now have comprehensive info. Let me compile the final answer with file:line refs and verbatim excerpts. The request explicitly wants concrete code excerpts, not prose summaries. I'll structure by their 5 questions.

Key gotchas to surface:
1. `read()` has `lake_root` param (design doc omits it but code has it) — must be used for F003 to point at configured lake.
2. `data_version=None` resolves latest valid via `mf.latest_valid_version` — ADR-0007 says canonical must NOT use implicit latest; F003 must pass explicit version from binding.
3. `pairs` are lake pairs (e.g. "BTC-USDT"), and reader maps to db symbols via symbol_map using the manifest's `symbol_map_digest`. So binding's pairs must be lake pairs.
4. `read()` re-verifies `value_digest` on every call (`mf.verify_value_digest`) and raises InvalidVersionError for invalid; returns actual value_digest in ReadResult. So binding's per-dataset validation = load manifest + verify digests, or call read and compare `result.value_digest`.
5. Value digest is computed from manifest partitions + registry projection; not stored elsewhere.
6. symbol_map_digest from ReadResult / manifest; load_symbol_map(digest).
7. On-disk: partition dirs include pair= dir but parquet does NOT contain pair column, only symbol. hive_partitioning=false in SQL. So tensor layer must use `symbol` column (db symbol) and map pairs itself, or pass `pairs` to read().
8. `end` is exclusive (half-open [start,end)). `_partition_covers`.
9. `as_of_fidelity`: ohlcv_1m is event_time_only → passing as_of raises unless allow_event_time_only=True.
10. Invalid enumeration: `list_versions` + `load_manifest`; status ∈ {"valid","invalid"}. No "list_valid_versions" helper. `latest_valid_version` skips invalid. `read` raises InvalidVersionError.
11. Test fixtures: tests/integration/conftest.py f002_lake + seed_f002_data + export_symbol_map_for + real export_dataset. tests/unit/test_f002_reader_contract.py builds a synthetic lake inline with `partitions.rows_to_table`, `pq.write_table`, `manifest.compute_value_digest`, `manifest.publish_manifest`, plus symbol map. `partitions.write_partition` writes real parquet and returns manifest entry.

Let me also mention `paths.lake_root()` env var ALPHAMILL_LAKE_DIR and `symbol_map.current_csv_path` env.

I should provide verbatim signatures. Let me be precise with line numbers.

Let me construct the answer now. The answer should be thorough with code excerpts (the request explicitly wants code, skip prose). I'll keep it structured.

For question 5, manifest fields: from exporter.py:252-279. Let me list them:
- dataset, source, source_snapshot {backend_xmin, taken_at}, symbol_map_digest, shrink_confirmed, as_of_fidelity, exported_at, rows, pairs, caliber {close, adjclose}, data_version, value_digest, status, partitions, reconcile, quality {flagged_partitions, unresolved_total}, skipped, excluded_null_event_time, revision_diff.
Required fields (`_REQUIRED_FIELDS`): dataset, data_version, status, rows, value_digest, partitions.
Partition entry required: logical_partition_key, path, rows, time_min, time_max, row_digest, bytes, sha256.

Timestamp semantics: all timestamptz stored as Arrow timestamp("us", tz="UTC"); parquet file has actual column `time` (or `latest_candle` for signals). Partition date = UTC date of event_time. `time_min`/`time_max` are ISO Z strings of event_time min/max. Timeframe: column in OI & basis; partition key; ohlcv is 1m implicit, no timeframe column.

The reader SQL: SELECT * FROM read_parquet(['file1',...], hive_partitioning=false) WHERE ... ORDER BY. So returned frame columns = projection columns only, no partition dims. For ohlcv, columns: time, exchange, symbol, open, high, low, close, volume. No pair, no timeframe.

Let me write final.

One more: the `FilterValue = Any` alias and `_utc` accepts str/datetime/pd.Timestamp, naive→UTC. Good to mention.

Let me also confirm `read` return frame dtype — pandas from duckdb `con.execute(...).df()`. Fine.

Now, for the binding implementation specifically: enrichment. The ReadResult fields map exactly to ADR-0007 member tuple: data_version, value_digest, as_of_fidelity. event_time_min/event_time_max are not on ReadResult — they're per-partition in manifest. So F003 binding must read manifest partitions to compute event_time_min/max (or use min/max over time_min/time_max). The user asked "how to discover valid data_versions and their value_digests for a dataset" — answer: `manifest.list_versions` + `load_manifest` + read `status`/`value_digest`; or `verify_value_digest` to re-verify.

Let me write it all out with line references. Use absolute paths.

I'll produce the results block at end.

Let me double check the ReadResult line numbers: 35-44. read signature 97-107. latest_valid_version reader 47-50. _utc 53. _partition_covers 68.

manifest: list_versions 86, load_manifest 95, latest 120, verify 191, compute 168, publish 278. _REQUIRED_FIELDS 41. parse_data_version 44.

symbol_map: COLUMNS 35, SymbolRow 64-68, SymbolMapRef 58-61, build 87, canonical_csv_bytes 114, content_digest 124, export 182, load 210, resolve 234, to_db_symbols 266, derive_pairs 71.

paths: lake_root 17, manifests_dir 24, manifest_path 28, symbol_maps_dir 36, partition_dir 40, partition_filename 69.

partitions: _ARROW_TYPES 27-32, arrow_schema 89, rows_to_table 93, write_partition 158, discover_cells 105, row_digest_of_rows 154.

registry: Column 27, DatasetSpec 33, DATASETS 193, require_dataset 199, pair_partitioned 208, timeframe_partitioned 212. Projections.

digest: row_digest 111, canonical_row_bytes 88.

errors: all.

exporter: export_dataset 110-118, manifest assembly 252-279.

Tests: integration conftest lines 95-101 (f002_lake), 104-189 (seed), 192-196 (export_symbol_map_for); unit test_f002_reader_contract 12-87.

Let me write the final response. Since the user wants concrete code excerpts, I'll include the relevant signatures verbatim.

I need to make sure all paths absolute. Use /home/georg/projects/alphamill-F003/... (their worktree). Mention main repo identical at e06f4fa.

Let me write.
<analysis>
**Literal Request**: Verbatim F002 data_bridge API, identity/digest model, symbol_map schema, lake layout, test fixtures.
**Actual Need**: Callable contract for F003 `generators/binding.py` + `generators/lake_tensor.py` so they reuse `reader.read()` and validate `(data_version, value_digest)`.
**Success Looks Like**: Exact signatures + line refs, digest fetch/verify functions, version enumeration + invalid handling, symbol_map columns/digest, Parquet columns/timestamp semantics, reusable lake builders.
</analysis>

Worktree `/home/georg/projects/alphamill-F003` is at `e06f4fa` (branch `feat/F003-alphagen-vendor`); `src/alphamill/data_bridge/` is byte-identical to main. All refs below are worktree paths.

# 1. Public read API

Verbatim, `/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reader.py:35-50`:

```python
@dataclass(frozen=True)
class ReadResult:
    frame: pd.DataFrame
    dataset: str
    data_version: str  # 即使调用方传 None，也回报实际解析版本
    value_digest: str  # 来自已校验 manifest 的语义根摘要
    as_of: dt.datetime | None  # None = 纯历史切片，不得用于回测/门禁判定
    as_of_fidelity: str | None  # "bitemporal" | "event_time_only"；as_of=None 时为 None
    flagged: list[str]  # 被显式豁免放行的带旗分区
    symbol_map_digest: str | None  # 该版本绑定的不可变映射（旧 manifest 可能为空）

def latest_valid_version(dataset: str, lake_root: Path | None = None) -> str:
    spec = registry.require_dataset(dataset)
    root = lake_root or paths.lake_root()
    return mf.latest_valid_version(root, spec.name)
```

Verbatim `reader.py:97-107` (note: `lake_root` IS in code; the design doc at `F002-data-bridge/design.md:302` omits it):

```python
def read(
    dataset: str,
    data_version: str | None = None,
    start: FilterValue | None = None,
    end: FilterValue | None = None,
    pairs: list[str] | None = None,
    as_of: FilterValue | None = None,
    allow_flagged: bool = False,
    allow_event_time_only: bool = False,
    lake_root: Path | None = None,
) -> ReadResult:
```

`FilterValue = Any` (`reader.py:32`). `start`/`end`/`as_of` accept `str | datetime | pd.Timestamp`; naive strings/datetimes are treated as UTC (`_utc`, `reader.py:53-65`). **`start` inclusive, `end` exclusive** (`reader.py:12`, `_partition_covers` `reader.py:68-78`, SQL `<` at `reader.py:191-193`).

Version selection, `reader.py:111-117`:
```python
version = mf.latest_valid_version(root, spec.name) if data_version is None else data_version
manifest = mf.load_manifest(root, spec.name, version)
if manifest["status"] == "invalid":
    raise InvalidVersionError(...)
value_digest = mf.verify_value_digest(spec, manifest)
```

**Answer to "must I avoid latest":** Yes. `data_version=None` silently resolves latest-valid. ADR-0007 decision 5 (`docs/decisions/0007-research-snapshot-binding.md:63-65`) forbids canonical consumers from doing this; F003 must pass the explicit `data_version` from the binding. The reader itself re-verifies integrity + `value_digest` on every call and returns the resolved `(data_version, value_digest)`.

`pairs` are **lake pairs** (`"BTC-USDT"`), mapped to db symbols inside `_query` via `symbol_map.to_db_symbols(..., digest=manifest["symbol_map_digest"])` (`reader.py:200-206`). The reader reads Parquet with `hive_partitioning=false` (`reader.py:214`), so partition dirs (`pair=`, `exchange=`, `timeframe=`) are NOT exposed as columns.

# 2. Where `value_digest` lives + fetch function

No registry of digests — it is a field in the dataset-version manifest JSON. Stored under `lake/_manifests/<dataset>/<data_version>.json`, key `"value_digest"`. The only authoritative fetch/verify is `manifest.verify_value_digest` (`/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py:191-201`):

```python
def verify_value_digest(spec: DatasetSpec, manifest: dict[str, Any]) -> str:
    declared = manifest.get("value_digest")
    if not declared:
        raise ManifestIntegrityError(f"{manifest.get('data_version')}: value_digest 缺失")
    recomputed = compute_value_digest(spec, manifest.get("partitions", []))
    if declared != recomputed:
        raise ManifestIntegrityError(
            f"{manifest['data_version']}: value_digest 重算不符"
            f"（manifest {declared}，重算 {recomputed}）"
        )
    return declared
```

Computed by `manifest.compute_value_digest` (`manifest.py:168-188`): canonical JSON of `dataset` + registry `projection` (name, logical_type in order) + partitions sorted by canonical logical key, each contributing only `logical_partition_key, rows, time_min, time_max, row_digest`; SHA-256 returns `"sha256:<hex>"`. Physical `path/bytes/sha256/exported_at` do NOT affect it.

Simplest binding flow: read `manifest["value_digest"]`, call `mf.verify_value_digest(spec, manifest)`, compare to the binding tuple; or call `read(...)` and compare `result.value_digest`. `ReadResult.value_digest` is set at `reader.py:163`.

# 3. Enumerating valid versions / invalidity

`manifest.py:86-92` and `120-125`:

```python
def list_versions(root: Path, dataset: str) -> list[str]:
    require_dataset(dataset)
    directory = paths.manifests_dir(root, dataset)
    if not directory.is_dir():
        return []
    versions = [p.stem for p in directory.glob("*.json")]
    return sorted(versions, key=data_version_sort_key)

def latest_valid_version(root: Path, dataset: str) -> str:
    for version in reversed(list_versions(root, dataset)):
        manifest = load_manifest(root, dataset, version)
        if manifest["status"] == "valid":
            return version
    raise VersionNotFoundError(f"{dataset} 无 valid 版本")
```

There is **no** `list_valid_versions`. F003 must iterate `list_versions` + `load_manifest` and filter `manifest["status"] == "valid"`. Invalidity representation: `manifest["status"] ∈ {"valid","invalid"}` only (`manifest_validation.py:92-95`). `read()` raises `InvalidVersionError` on explicit invalid (`reader.py:113-116`); `latest_valid_version` skips invalid. There is **no valid→invalid reversal** and invalid version numbers are never reused (`manifest.next_data_version`, `manifest.py:128-135`).

Version format `vYYYY.MM.DD` / `vYYYY.MM.DD-rN`, sorted by `(date, revision)` (`manifest.parse_data_version`, `manifest.py:44-65`; regex `manifest_validation.py:19`).

# 4. `symbol_map` structure + digest

`/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/symbol_map.py:35`, `58-68`, `87-125`, `182-231`:

```python
COLUMNS = ("exchange", "market_type", "db_symbol", "lake_pair", "freqtrade_pair")
MARKET_TYPES = ("spot", "perp")

@dataclass(frozen=True)
class SymbolMapRef:
    digest: str
    path: Path  # digest 命名的不可变 artifact，不是 current 副本

@dataclass(frozen=True)
class SymbolRow:
    exchange: str
    market_type: str
    db_symbol: str

def build_symbol_map(rows: list[SymbolRow]) -> pd.DataFrame:
    ...
    return frame.sort_values(list(COLUMNS), kind="stable").reset_index(drop=True)

def canonical_csv_bytes(frame: pd.DataFrame) -> bytes: ...   # fixed header + LF, 5 cols sorted
def content_digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()

def load_symbol_map(digest: str | None = None, lake_root: Path | None = None) -> pd.DataFrame
def to_db_symbols(pairs: list[str], market_type: str, lake_root: Path | None = None,
                  digest: str | None = None) -> list[str]
```

- Row shape: `exchange, market_type, db_symbol, lake_pair, freqtrade_pair`, e.g. `("binance","spot","BTC/USDT","BTC-USDT","BTC/USDT")`; perp: lake `BTC-USDT-PERP`, freqtrade `BTC/USDT:USDT` (`derive_pairs`, `symbol_map.py:71-84`).
- Digest = `sha256(canonical_csv_bytes)` prefixed `"sha256:"`; immutable artifact at `lake/_metadata/symbol_maps/<digest>.csv` (`paths.symbol_maps_dir`, `paths.py:36-37`); mutable copy at `lake/_metadata/symbol_map.csv` (`symbol_map.current_csv_path`, `symbol_map.py:46-55`, overridable by env `ALPHAMILL_SYMBOL_MAP_CURRENT`).
- `load_symbol_map(digest=...)` verifies digest AND re-canonicalizes the bytes (`symbol_map.py:221,229`). Use explicit digest from the binding/manifest for reproducibility; `digest=None` reads the mutable current copy.
- `ReadResult.symbol_map_digest` comes straight from `manifest.get("symbol_map_digest")` (`reader.py:167`).

# 5. On-disk layout, Parquet schema, timestamp/timeframe semantics, manifest fields

**Paths** (`paths.py:17-70`):
```
ALPHAMILL_LAKE_DIR → root (default <repo>/lake)        # lake_root()
root/_manifests/<dataset>/<data_version>.json          # manifest_path
root/_metadata/symbol_maps/<digest>.csv                # symbol_maps_dir
root/_staging/<dataset>/<version>/                     # staging_dir
root/<dataset>/exchange=<ex>/[pair=<pair>/][timeframe=<tf>/]date=<date>.r<rev>.parquet
```
`partition_filename = f"date={key['date']}.r{revision}.parquet"` (`paths.py:69-70`). Files are never overwritten; revisions add `.rN`. `data_version` is NOT in the path; version composition is defined solely by manifest `partitions`.

**Parquet schema** (`partitions.py:27-32`, `89-102`): exact `spec.projection` columns, no partition dims.
- `timestamptz` → `pa.timestamp("us", tz="UTC")`; `text/jsonb` → `pa.string()` (jsonb = canonical JSON text); `double` → `pa.float64()`.
- ohlcv_1m columns: `time, exchange, symbol, open, high, low, close, volume` (NO `pair`, NO `timeframe`; 1m is implicit).
- derivatives_open_interest/mark_index_basis include `timeframe` plus `ingested_at`.
- signals_log event time column is `latest_candle` (not `time`); see registry.

**Partition keys** (`registry.py:133-191`, test `test_f002_registry.py:68-74`):
```
ohlcv_1m / derivatives_funding_rates: (exchange, pair, date)
derivatives_open_interest / mark_index_basis: (exchange, pair, timeframe, date)
signals_log: (date,)
```
`partition_dir` builds `exchange=`→`pair=`→`timeframe=` and `date=` is only in the filename (`paths.py:40-50`, `69`). The `pair` directory value is a lake pair; the in-file column is `symbol` (db symbol).

**Dual time axis / fidelity** (`registry.py:133-191`):
- `ohlcv_1m`: `event_time="time"`, `available_at=None`, `as_of_fidelity="event_time_only"` → `read(as_of=...)` raises `InsufficientAsOfFidelityError` unless `allow_event_time_only=True` (`reader.py:126-130`).
- others: `event_time="time"`, `available_at="ingested_at"`, `bitemporal`.
- `signals_log`: `event_time="latest_candle"`, `available_at="time"`, deferred label `realized_return_60m`→`evaluated_at`, nullified if `evaluated_at > as_of` (`reader.py:224-233`).
- `start/end` filter `spec.event_time`; `as_of` additionally filters `available_at` when present (`reader.py:188-199`).

**Manifest fields** assembled in `exporter.py:252-279` (required minimum `_REQUIRED_FIELDS`, `manifest.py:41` = `dataset, data_version, status, rows, value_digest, partitions`):
```
dataset, source, source_snapshot{backend_xmin,taken_at}, symbol_map_digest,
shrink_confirmed, as_of_fidelity, exported_at, rows, pairs[], caliber{close,adjclose},
data_version, value_digest, status, partitions[], reconcile{}, 
quality{flagged_partitions[],unresolved_total}, skipped[], excluded_null_event_time, revision_diff[]
```
Each partition entry (`partitions.py:188-197`, validated `manifest_validation.py:115-124`):
```
{logical_partition_key:{...}, path:"<dataset>/exchange=.../date=....rN.parquet", rows,
 time_min:"...Z", time_max:"...Z", row_digest:"sha256:...", bytes, sha256}
```
`time_min/time_max` = min/max of `spec.event_time` ISO-8601 Z (`partitions.py:192-193`, `manifest.iso_utc`). For binding `event_time_min/max` per dataset, derive min(time_min)/max(time_max) across `manifest["partitions"]` (not directly on `ReadResult`).

**Other public API** (`exporter.py:110-118`): `export_dataset(dataset, mode="incremental", window_end=None, conn=None, lake_root=None, post_export_hook=None, allow_shrink=False) -> dict[str, Any]`. `rows_to_table` (`partitions.py:93`), `write_partition` (`partitions.py:158`).

# 6. Test fixtures / fake-lake builders

- **Synthetic real lake, no DB** — the canonical template: `/home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py:12-87`. Uses `partitions.rows_to_table` + `pq.write_table` for a partition file (lines 32-35), `symbol_map.build_symbol_map`+`canonical_csv_bytes`+`content_digest` into `symbol_map.paths.symbol_maps_dir(tmp_path)` (37-42), builds a manifest entry with `digest.row_digest(rows, spec.projection)` + `manifest.file_sha256` (44-53), then `manifest.compute_value_digest(spec, [...])` + `manifest.publish_manifest(tmp_path, lake_manifest)` (70-74), then `read("signals_log", data_version="v2026.09.11", pairs=["BTC-USDT"], ..., lake_root=tmp_path)`. This is the exact shape F003's `test_f003_lake_tensor.py` should mimic.
- **Unit helper** `_write_partition_file(root, partition, content)` at `/home/georg/projects/alphamill-F003/tests/unit/test_f002_manifest.py:37-44`; `_partition(...)` entry builder at `:22-34`.
- **Real export via DB** — `/home/georg/projects/alphamill-F003/tests/integration/conftest.py`: `f002_lake` fixture (`:95-101`, sets `ALPHAMILL_LAKE_DIR` + `ALPHAMILL_SYMBOL_MAP_CURRENT`), `seed_f002_data(conn)` (`:104-189`), `export_symbol_map_for(conn, lake) -> digest` (`:192-196`). Used in `tests/integration/test_f002_reader.py:27-35` which calls `export_symbol_map_for` then `export_dataset(dataset, mode="full", window_end=f"{D4}T00:00:00Z", conn=f002_conn)`. Constants `D1..D4 = 2026-09-01..04` (`conftest.py:17`).
- **No unit `conftest.py`** exists (only `tests/integration/conftest.py`); unit tests build lakes inline.

<results>
<files>
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/reader.py - `read()`, `ReadResult`, `latest_valid_version`; the single sanctioned data entry point
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py - `list_versions`, `load_manifest`, `verify_value_digest`, `compute_value_digest`, `latest_valid_version`, `publish_manifest`, manifest field contract
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/symbol_map.py - 5-column map, `SymbolMapRef`, `load_symbol_map(digest)`, `to_db_symbols`, canonical digest
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/registry.py - 5 frozen `DatasetSpec`s, projections, event/available time, partition keys, fidelity
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/partitions.py - Parquet schema, `rows_to_table`, `write_partition`, partition entry shape
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/paths.py - lake root, manifest/symbol-map/partition paths
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/digest.py - `row_digest`, canonical encoding (identity leaf)
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest_validation.py - manifest shape, status enum, path safety
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/errors.py - exception hierarchy (InvalidVersionError, ManifestIntegrityError, etc.)
- /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/exporter.py - `export_dataset`; manifest field assembly at lines 252-279
- /home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py - fake-lake builder template (no DB)
- /home/georg/projects/alphamill-F003/tests/integration/conftest.py - `f002_lake`, `seed_f002_data`, `export_symbol_map_for`
- /home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py - end-to-end F002 usage examples
- /home/georg/projects/alphamill-F003/docs/decisions/0007-research-snapshot-binding.md - binding member tuple + "no dynamic latest" rule
- /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md - binding/explicit_tuples shape (lines 119-122)
</files>

<answer>
Call contract for F003:

1. For each dataset, load the manifest with `manifest.load_manifest(root, dataset, data_version)` (explicit version from the binding; never `None`), reject if `manifest["status"] == "invalid"`, then `manifest.verify_value_digest(registry.require_dataset(dataset), manifest)` and compare the returned `"sha256:..."` against the binding tuple.
2. Construct tensors exclusively via `reader.read(dataset, data_version=<explicit>, start=..., end=..., pairs=<lake pairs like "BTC-USDT">, as_of=..., lake_root=<resolved>, allow_flagged=..., allow_event_time_only=...)`. It re-verifies integrity + value_digest internally and returns `ReadResult` with resolved `data_version`, `value_digest`, `as_of_fidelity`, `flagged`, `symbol_map_digest`.
3. `pairs` are lake pairs; the returned frame contains the `symbol` (db symbol) column and no `pair`/`exchange` partition columns (`hive_partitioning=false`). Map pairs/channels via `symbol_map.load_symbol_map(digest=result.symbol_map_digest, lake_root=...)`, whose columns are `exchange, market_type, db_symbol, lake_pair, freqtrade_pair`.
4. Discover valid versions by iterating `manifest.list_versions(root, dataset)` + `load_manifest` and filtering `status == "valid"` (no list-valid helper exists). `latest_valid_version` is for preview/exploration only and must not back a canonical binding.
5. To get per-dataset `event_time_min/max` for the binding, take min(`time_min`)/max(`time_max`) across `manifest["partitions"]`; they are not fields on `ReadResult`.

Key traps: `end` is exclusive; `ohlcv_1m` + `as_of` raises unless `allow_event_time_only=True`; jsonb is stored as canonical JSON text; timestamps are UTC microseconds; the lake root is `ALPHAMILL_LAKE_DIR` or `<repo>/lake`.
</answer>

<next_steps>
Implement `generators/binding.py` against `manifest.load_manifest` + `verify_value_digest` (explicit version/digest compare), and `generators/lake_tensor.py` against `reader.read(...)` + `symbol_map.load_symbol_map(digest=result.symbol_map_digest)`. Copy the fake-lake pattern from tests/unit/test_f002_reader_contract.py:12-87 into `tests/unit/test_f003_lake_tensor.py` for a DB-free reader test; point `lake_root` at `paths.lake_root()` in production.
</next_steps>
</results>
