---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4b5bba2dffeIQsH2j7oUN2BLl"
title: "Test conventions + FactorDef usage (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-18T13:10:59Z"
updated_at: "2026-09-18T13:12:44Z"
tokens_input: 59341
tokens_output: 7235
cost: 0.0159
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# Test conventions + FactorDef usage (@explore subagent)

## user · 2026-09-18T13:10:59Z

[CONTEXT] I am implementing F003 in the alphamill repo worktree /home/georg/projects/alphamill-F003. Before writing new tests I must match the repo's existing test conventions exactly, and I need to know whether any FactorDef-like executable object already exists in the codebase (F001 migrated factor_factory/bench scripts) so I extend it rather than invent a duplicate.

[GOAL] (a) Document the repo's unit/integration test conventions; (b) locate every existing in-code FactorDef / HypothesisDef / factor-evaluation structure and its exact shape.

[DOWNSTREAM] I will write tests/unit/test_f003_generator_contract.py, test_f003_factor_store.py, test_f003_run_store.py, test_f003_hypotheses.py and match existing style; and I will implement FactorDef to be compatible with architecture §4.1 rather than duplicating an existing definition.

[REQUEST] Investigate and report with file:line references and verbatim excerpts:
1. Test conventions in tests/unit and tests/integration: how tests are structured (plain functions vs classes), use of pytest fixtures/tmp_path, markers (`integration`), env-var gating (e.g. ALPHAMILL_INTEGRATION, ALPHAMILL_REAL_LAKE_DIR), any shared conftest.py helpers, how tests avoid touching the real lake, and how skips are justified.
2. Any existing helper for building temp dirs/fixtures for data_bridge.
3. Every occurrence of a factor definition object: search for `FactorDef`, `HypothesisDef`, `compute`, `data_columns`, `scope`, `factor_id`, `definition_digest`, `meta` across src/ and tests/ (excluding src/alphamill/factor_factory/bench/ internals unless they define such a type). For each hit, give the verbatim class/dataclass/function definition and its fields, and note which module owns it.
4. src/alphamill/factor_factory/__init__.py and any existing exports.
5. The 350-line hard limit enforcement: which tool/test enforces it (name + how), so new files stay compliant.
Skip: unrelated freqtrade_bridge risk code, kronos_service internals. Return concrete excerpts.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T13:10:59Z

- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill-F003 2>&1 | head -40; echo \"---GITWORKTREE---\"; git -C /home/georg/projects/alphamill worktree list 2>&1"})`
- **tool**: `bash({"command": "find /home/georg/projects/alphamill-F003/tests -type f 2>/dev/null | sort; echo \"---CONFTEST---\"; find /home/georg/projects/alphamill-F003 -name \"conftest.py\" -not -path \"*/.venv/*\" -not -path \"*/node_modules/*\" 2>/dev/null"})`
- **tool**: `glob({"pattern": "**/*.py", "path": "/home/georg/projects/alphamill-F003/tests"})`
- **tool**: `bash({"command": "grep -rn \"FactorDef\\|HypothesisDef\" /home/georg/projects/alphamill-F003 --include=\"*.py\" --include=\"*.md\" -l 2>/dev/null | grep -v \".venv\" | head -50"})`


> [reasoning] Let me start investigating. I need to be careful: the working directory is /home/georg/projects/alphamill but the target worktree is /home/georg/projects/alphamill-F003. The user wants investigation of the repo (probably the F003 worktree). Let me explore both. The context says "the alphamill repo worktree /home/georg/projects/alphamill-F003". Let me check if that exists.

Let me launch parallel searches.
<analysis>
**Literal Request**: Document test conventions in tests/unit and tests/integration, locate every existing FactorDef/HypothesisDef/factor-evaluation structure with shape, find factor_factory exports, and identify the 350-line limit enforcer.
**Actual Need**: Match existing test style before writing F003 tests, and know whether to extend or create the FactorDef type per architecture §4.1.
**Success Looks Like**: Concrete file:line excerpts for conftest helpers, fixture patterns, any existing factor-definition dataclasses/classes, and the line-limit tool.
</analysis>

I'll investigate the F003 worktree (and cross-check the main worktree). Launching parallel reconnaissance.

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
/home/georg/projects/alphamill-F003/tests/integration/.gitkeep
/home/georg/projects/alphamill-F003/tests/integration/__pycache__/conftest.cpython-314-pytest-9.1.1.pyc
/home/georg/projects/alphamill-F003/tests/integration/__pycache__/test_f003_kronos_lifecycle.cpython-314-pytest-9.1.1.pyc
/home/georg/projects/alphamill-F003/tests/integration/__pycache__/test_f003_kronos_lifecycle.cpython-314.pyc
/home/georg/projects/alphamill-F003/tests/integration/conftest.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_dryrun_monitoring.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_kronos_smoke.py
/home/georg/projects/alphamill-F003/tests/integration/test_f001_row_reconciliation.py
/h
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 52 file(s)

/home/georg/projects/alphamill-F003/tests/unit/test_risk_guards.py
/home/georg/projects/alphamill-F003/tests/unit/test_check_task_dag.py
/home/georg/projects/alphamill-F003/tests/unit/test_review_artifacts_gitignore.py
/home/georg/projects/alphamill-F003/tests/unit/test_f002_timer_contract.py
/home/georg/projects/alphamill-F003/tests/unit/test_verify_env_contract.py
/home/georg/projects/alphamill-F003/tests/unit/test_f004_compose_profile_contract.py
/home/georg/projects/alphamill-F003/tests/unit/test_check_dep_pins.py
/home/georg/projects/alphamill-F003/tests/unit/test_f002_registry.py
/home/georg/projects/alphamill-F003/tests/unit/test_symbol_manager.py
/home/georg/projects/alphamill-F003/tests/unit/test_historical_backfill_review_fixes.py
/home/georg/projects/alphamill-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/conversations/codex/rollout-2026-09-14T22-22-43-01a0a04c-8001-7150-bb57-d36fa88f802c.md
/home/georg/projects/alphamill-F003/conversations/codex/rollout-2026-09-13T16-06-26-01a099cd-a51a-74b1-9c0a-0902fe40b473.md
/home/georg/projects/alphamill-F003/conversations/codex/rollout-2026-09-13T16-06-23-01a099cd-9a06-7fe3-b3e8-2ef1b010066b.md
/home/georg/projects/alphamill-F003/conversations/opencode/ses_f6664247effe4SLb37r5OF4RZ9.md
/home/georg/projects/alphamill-F003/conversations/opencode/ses_f5f9a1cf7ffemPxb4yILEhSmY0.md
/home/georg/projects/alphamill-F003/conversations/opencode/ses_f5f9c9f13ffeUndV8k28QEtsfZ.md
/home/georg/projects/alphamill-F003/conversations/opencode/ses_f66eaac26ffe9ePoIIWcPIcJlS.md
/home/georg/projects/alphamill-F003/conversations/timeli
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:04Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/conftest.py"})`
- **tool**: `bash({"command": "find /home/georg/projects/alphamill-F003/src -type f -name \"*.py\" | sort"})`
- **tool**: `bash({"command": "find /home/georg/projects/alphamill-F003/src/alphamill/factor_factory -type f 2>/dev/null | sort; echo \"---INIT---\"; cat /home/georg/projects/alphamill-F003/src/alphamill/factor_factory/__init__.py 2>&1"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f001_line_limit_exemptions.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/pyproject.toml"})`


> [reasoning] Interesting: the .py file search for FactorDef/HypothesisDef returned nothing in src/tests — only docs/conversations. Wait, the grep was with --include="*.py" --include="*.md" and -l. No .py hits? That's surprising given conversations. Let me redo more carefully. Actually the output only shows .md files. So there's no FactorDef in .py currently. But there might be a FactorDef in the F003 design doc. Let me examine.

Let me read the integration conftest, key test files, factor_factory dir, and search for factor-evaluation structures. Also check the line limit enforcement (test_f001_line_limit_exemptions.py likely).

Let me launch a wide batch.
Key finding already: no `FactorDef`/`HypothesisDef` in any `.py` — only docs. Let me gather the conventions and the factor_factory module.

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

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/__init__.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/__init__.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/cli.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/__init__.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/backfill_boundaries.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/ccxt_ingestor.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/db_writer.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/derivatives_market_backfill.py
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/collector/historical_backfill.py
/home/georg/projects/alphamill-F003/src/alph
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/__init__.py
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/__init__.py
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/kronos_ic_decay_eval.py
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/kronos_rankic_eval.py
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/train_low_frequency_walk_forward_baselines.py
---INIT---
"""Factor generation and evaluation components."""


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f001_line_limit_exemptions.py</path>
<type>file</type>
<content>
1: """F001 file-limit exemption register regression test."""
2: 
3: import re
4: from pathlib import Path
5: 
6: ROOT = Path(__file__).resolve().parents[2]
7: 
8: 
9: def test_all_f001_over_limit_files_are_registered_with_an_expiry() -> None:
10:     sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
11:     section = sop.split("### F001 原样迁移文件豁免", 1)[1].split("\n## ", 1)[0]
12:     registered = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.MULTILINE))
13:     actual = {
14:         str(path.relative_to(ROOT))
15:         for root in (ROOT / "src", ROOT / "freqtrade", ROOT / "deployment")
16:         for path in root.rglob("*")
17:         if path.is_file
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/pyproject.toml</path>
<type>file</type>
<content>
1: [build-system]
2: requires = ["hatchling"]
3: build-backend = "hatchling.build"
4: 
5: [project]
6: name = "alphamill"
7: version = "0.1.0"
8: description = "以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行"
9: readme = "README.md"
10: requires-python = ">=3.11"
11: dependencies = [
12:   "ccxt>=4.4,<5",
13:   # F002 数据桥：Parquet 湖（写 PyArrow / 读 DuckDB）。运行时依赖同样锁范围，
14:   # 是否在范围内由 check_dep_pins 门禁强制（F002 spec 决策表：版本漂移显式改动）。
15:   "duckdb>=1.5,<2",
16:   "fastapi>=0.115,<1",
17:   "pandas>=2.2,<3",
18:   "psycopg2-binary>=2.9,<3",
19:   "pyarrow>=25,<26",
20:   "pydantic>=2.10,<3",
21:   "uvicorn>=0.34,<1",
22: ]
23: 
24: [project.optional-dependencies]
25: dev = [
26:   # 固定到范围：CI 每次 `pip
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:09Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f003_lifecycle_contract_config.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/unit/test_f002_exporter.py"})`
- **tool**: `bash({"command": "grep -rn \"FactorDef\\|HypothesisDef\\|definition_digest\\|factor_id\\|data_columns\" /home/georg/projects/alphamill-F003/src /home/georg/projects/alphamill-F003/tests /home/georg/projects/alphamill-F003/tools /home/georg/projects/alphamill-F003/scripts 2>/dev/null | grep -v \".venv\" | head -80"})`
- **tool**: `bash({"command": "grep -rn \"ALPHAMILL_INTEGRATION\\|ALPHAMILL_REAL_LAKE_DIR\\|pytest.mark.integration\\|pytest.skip\\|pytest.fail\" /home/georg/projects/alphamill-F003/tests 2>/dev/null | grep -v \".pyc\" | head -80"})`


> [reasoning] Now let me look at representative unit tests to document conventions, especially F002 tests that likely use tmp_path and data_bridge fixtures. Also test_f003_lifecycle_contract_config.py (existing F003 unit test). And search for factor-definition structures: `data_columns`, `scope`, `factor_id`, `definition_digest`, `meta`, `compute`. Let me grep.

Also read architecture §4.1 for FactorDef. And F003 design.md. Let me do a big parallel batch.
Now the conventions deep-dive plus factor-definition structures.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/unit/test_f003_lifecycle_contract_config.py</path>
<type>file</type>
<content>
1: """F003-R4-002 锁：生命周期契约测试模块不得有 mock 默认地址。
2: 
3: 契约目标是 `kronos-signal-real`（执行机 GPU 实例）；`KRONOS_CONTROL_URL` 未设时
4: 模块级 `CONTROL_URL` 必须为空串并使用例 skip——绝不回落到 mock 的 8001（XPASS
5: 转正警报因此只可能打在真实实例上）。直接以文件位置加载被测模块，避免受本进程
6: 已导入副本或收集期环境的影响。
7: """
8: 
9: from __future__ import annotations
10: 
11: import importlib.util
12: import pathlib
13: 
14: import pytest
15: 
16: MODULE = (
17:     pathlib.Path(__file__).resolve().parents[1] / "integration" / "test_f003_kronos_lifecycle.py"
18: )
19: 
20: 
21: def _load_fresh():
22:     spec = importlib.util.spec_from_file_location("_f003_lifecycle_under_test", MODULE)
23:     mod = importlib.util.module_from_spec(spec)
24:     
…[truncated]
  ```
  </details>

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
/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py:71:        "factor_id_no_run_seq",
/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py:74:            (DESIGN, "factor_id = <generator>_<definition_digest[:12]>"),


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:62:    （ALPHAMILL_INTEGRATION=1 下判红）。quant 角色为超级用户，可自建库。
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:67:        if os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}:
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:68:            pytest.fail(f"ALPHAMILL_INTEGRATION=1 但 docker/DB 不可达: {exc}")
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:69:        pytest.skip(f"docker 或 quant-timescaledb 不可达: {exc}")
/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py:4:在线时运行，否则按 SOP 约定跳过（ALPHAMILL_INTEGRATION=1 下判红）。
/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py:23:pytestmark = pytest.mark.integration
/home/georg
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:14Z

- **tool**: `bash({"command": "grep -rn \"4\\.1\\|FactorDef\\|HypothesisDef\\|factor_id\\|definition_digest\\|data_columns\" /home/georg/projects/alphamill-F003/docs/alphamill-architecture.md | head -60"})`
- **tool**: `bash({"command": "grep -rn \"@dataclass\\|^class \\|NamedTuple\\|BaseModel\" /home/georg/projects/alphamill-F003/src /home/georg/projects/alphamill-F003/tools /home/georg/projects/alphamill-F003/scripts 2>/dev/null | grep -v \".venv\" | head -80"})`
- **tool**: `bash({"command": "cat /home/georg/projects/alphamill-F003/src/alphamill/data_bridge/__init__.py; echo \"===CONFTEST ROOT===\"; find /home/georg/projects/alphamill-F003 -maxdepth 2 -name \"conftest.py\" -o -maxdepth 2 -name \"pytest.ini\" 2>/dev/null"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md"})`


> [reasoning] Now let me look at architecture §4.1 for FactorDef shape, the design.md for F003, and tasks.md. Also examine the data_bridge module for a helper building temp dirs/fixtures. And look at test_f002_run? Actually test files. Let me read architecture around §4.1 and F003 design.md.

Also, I should check the src/alphamill/data_bridge/__init__.py to see exports and any temp-dir helper. And check `compute`, `scope`, `meta` grep.

Let me search for "class .*Def" and "dataclass" in src. And "compute" definitions.

  <details><summary>tool output</summary>

  ```text
45:               │ HypothesisDef / FactorDef                    │ 报告与事件
135:    A[HypothesisDef] --> B[FactorDef / meta-factor]
191:    │   ├── hypotheses/          # HypothesisDef 注册、人审队列与 generation
193:    │   │   ├── base.py          #   生成器接口：produce() -> list[FactorDef]
194:    │   │   ├── alphagen_adapter.py  # 表达式树/张量 ↔ FactorDef 适配层（§4.1.1；放 vendor 外，见集成文档卫生规则）
240:ResearchSnapshot + HypothesisDef → FactorDef → factor ExperimentRun
241:FactorDef(s) → PortfolioDef → portfolio ExperimentRun → DeploymentCandidate
242:→ DeploymentRun → RunRecord → AttributionReport →（人审通过）新 HypothesisDef
245:- `HypothesisDef` 拥有经济动机、来源、generation、数据依赖、预期持有期和成本敏感性；
246:- `FactorDef` 拥有可执行定义和版本，不承载评测结论；
254:### 4.1 因子定义（FactorDef）
258:class FactorDef:
259:    factor_id: str            # 如 "alphagen_gen
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/drawdown_guard.py:8:@dataclass(frozen=True)
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/drawdown_guard.py:9:class DrawdownGuardState:
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/drawdown_guard.py:19:class DrawdownGuard:
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/correlation_guard.py:9:@dataclass(frozen=True)
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/correlation_guard.py:10:class CorrelationGuardState:
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/correlation_guard.py:17:class CorrelationGuard:
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/circuit_breaker.
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
"""Data ingestion and lake bridge components."""
===CONFTEST ROOT===


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: related_features: [F001, F002, F007, F008]
6: topics: [factor-factory, alphagen, vendor, generators, m2]
7: doc_kind: design
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F003：AlphaGen vendor 与可插拔生成器平面 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
17: > 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
18: > 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。
19: 
20: ## 0. 输入与约束
21: 
22: - **行为契约**：`spec.md`
23: - **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR2.1~FR2.6；`docs/alphamill-architecture.md` §三（`factor_fact
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:20Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/alphamill-architecture.md", "offset": 240, "limit": 100})`
- **tool**: `bash({"command": "grep -rn \"def compute\\|scope\\b\\|data_columns\\|meta\\[\" /home/georg/projects/alphamill-F003/src --include=\"*.py\" | grep -v \".venv\" | head -60"})`
- **tool**: `bash({"command": "grep -rn \"350\\|line.limit\\|line_limit\\|splitlines()\" /home/georg/projects/alphamill-F003/tools /home/georg/projects/alphamill-F003/docs/SOP.md /home/georg/projects/alphamill-F003/scripts 2>/dev/null | head -50"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tools/verify.py"})`


> [reasoning] Excellent. Now I need the exact architecture §4.1 FactorDef definition (lines ~254-278). Let me read that. Also read tools/verify.py to see how tests collected and line limit. And read the F001 bench scripts for any factor-def-like objects (the user said src/alphamill/factor_factory/bench/ internals unless they define such a type). The grep for FactorDef found nothing in .py, but let me check for structural factor objects in bench. Also read the F003 spec/tasks for the planned test files and keys.

Let me read architecture lines 40-60, 130-150, 240-300. And search for `compute` and `scope` in src.

Also check data_bridge test helper for temp dirs - I saw conftest f002_lake. Also maybe there's a module-level helper in tests/unit. Let me search for "tmp_path" usage and any helper functions named make_/build_.

Let me batch.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
240: ResearchSnapshot + HypothesisDef → FactorDef → factor ExperimentRun
241: FactorDef(s) → PortfolioDef → portfolio ExperimentRun → DeploymentCandidate
242: → DeploymentRun → RunRecord → AttributionReport →（人审通过）新 HypothesisDef
243: ```
244: 
245: - `HypothesisDef` 拥有经济动机、来源、generation、数据依赖、预期持有期和成本敏感性；
246: - `FactorDef` 拥有可执行定义和版本，不承载评测结论；
247: - `PortfolioDef` 拥有成员、权重、估计窗口、约束和组合门报告；
248: - `ExperimentRun` 拥有显式 execution tier、cohort、冻结规则和内容寻址 ID；
249: - `DeploymentRun` 固定引用 portfolio、信号缓存和审批版本；
250: - `RunRecord` 保存 intended/attempted/accepted/failed 四桶及执行事实；
251: - `AttributionReport` 区分事实、推断与建议，经规则或人审才触发生命周期/新假设动作；
252: - `ExperimentManifest` 是各对象和所有证据之间的不可变索引，不把结果复制回定义对象。
253:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/drawdown_guard.py:39:        trades = self._closed_trades_in_scope(closed_trades, current_time)
/home/georg/projects/alphamill-F003/src/alphamill/freqtrade_bridge/risk/drawdown_guard.py:95:    def _closed_trades_in_scope(
/home/georg/projects/alphamill-F003/src/alphamill/validation/validate_low_frequency_candidate_holdout.py:94:    center = {"train_days": 180, "test_days": 45, "quantile": 0.95, "scope": "filtered_no_btc_xrp"}
/home/georg/projects/alphamill-F003/src/alphamill/validation/validate_low_frequency_candidate_holdout.py:215:                    "train_start": meta["train_start"],
/home/georg/projects/alphamill-F003/src/alphamill/validation/validate_low_frequency_candidate_holdout.py:216:                    "tra
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/tools/check_secrets.py:69:        for lineno, line in enumerate(text.splitlines(), start=1):
/home/georg/projects/alphamill-F003/tools/f001_backfill_report.py:389:    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py:954:    for line in text[idx:].splitlines()[1:]:
/home/georg/projects/alphamill-F003/tools/f001_backfill_config.py:29:    for raw_line in WINDOW_FILE.read_text(encoding="utf-8").splitlines():
/home/georg/projects/alphamill-F003/tools/f001_backfill_config.py:42:    for raw_line in DOTENV_FILE.read_text(encoding="utf-8").splitlines():
/home/georg/projects/alphamill-F003/tools/apply_migrations.py:40:    for raw_line in path.read_text(encoding="utf-8").splitli
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tools/verify.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """本地统一验证入口（公开验证唯一入口）。
3: 
4: 按固定顺序运行：规格生命周期校验 → 文档相对链接检查 → 任务 DAG 检查
5: → 文档一致性检查 → dev 依赖 pin 范围检查 → 密钥模式扫描 → pytest
6: → ruff check → ruff format check。任一步失败即记录，全部跑完后汇总返回非零
7: （不短路）。
8: 
9: 各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
10: 统一指向本入口。
11: 
12: 用法：
13:     python3 tools/verify.py
14: 退出码 0 表示全部通过；非 0 时打印失败步骤。
15: """
16: 
17: from __future__ import annotations
18: 
19: import pathlib
20: import subprocess
21: import sys
22: 
23: ROOT = pathlib.Path(__file__).resolve().parent.parent
24: 
25: 
26: def _run(cmd: list[str], label: str) -> bool:
27:     print(f"\n== {label} ==")
28:     proc = subprocess.run(cmd, cwd=ROOT)
29:     if proc.returncode != 0:
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:25Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/docs/SOP.md", "offset": 85, "limit": 40})`
- **tool**: `bash({"command": "grep -rn \"^class Test\\|^def test_\\|^    def test_\\|@pytest.fixture\\|@pytest.mark\" /home/georg/projects/alphamill-F003/tests/unit /home/georg/projects/alphamill-F003/tests/integration 2>/dev/null | grep -v \".pyc\" | grep \"class Test\" | head; echo \"=== fixtures in unit ===\"; grep -rn \"@pytest.fixture\" /home/georg/projects/alphamill-F003/tests --include=\"*.py\" | head -30"})`
- **tool**: `bash({"command": "grep -rn \"^def \\|^class \\|factor\\|Factor\\|signal\\|alpha\" /home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/*.py | grep -i \"factor\\|class \\|def .*signal\\|def .*alpha\" | head -60"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py", "offset": 1, "limit": 60})`
- **tool**: `bash({"command": "grep -rn \"def _.*tmp\\|def make_\\|def build_\\|def write_\\|def seed_\\|def _lake\\|def _write\\|tmp_path\" /home/georg/projects/alphamill-F003/tests --include=\"*.py\" | head -50"})`


> [reasoning] Now I have most of what's needed. Key finding: no FactorDef exists in code — only architecture docs. The 350-line limit is enforced by test_f001_line_limit_exemptions.py (unit test) which reads docs/SOP.md exemption table and compares against actual files >350 lines. Note it only scans src, freqtrade, deployment (NOT tests). And verify.py runs pytest. Also ruff doesn't enforce line count. Let me confirm whether there's a `check_line_limit` in verify. No.

Wait — the test scans ROOT/src, ROOT/freqtrade, ROOT/deployment. It does NOT scan tools/ or tests/. But SOP §Code Quality says 350 hard limit. Let me read SOP section 91-110 to give exact wording.

Also, need to check factor_factory/bench for factor-def-like objects. The user asked to locate every occurrence of factor definition object. Let me look at the bench scripts for any dataclass/function resembling FactorDef. The grep for FactorDef found none. Let me check bench scripts for classes. independent_cross_backtest has Position dataclass. Let me search for "factor" symbols in bench and `def ` compute-ish. Let me grep for "def .*signal\|factor\|alpha" in bench.

Also, the user asked about helper for building temp dirs/fixtures for data_bridge. The conftest f002_lake and f002_db/f002_conn, plus seed_f002_data, export_symbol_map_for. Are there unit-level helpers? test_f002_reader_contract builds lake manually with tmp_path. Let me search tests for helper functions like `_build`, `write_`, `seed_`.

Also check the F003 tasks.md for the test plan / expected APIs to inform. And spec.md. Let me read tasks.md relevant sections.

Let me also confirm there is no tests/__init__.py and that tests are plain functions (no classes). Let me grep for "class Test" in tests.

And check how skips are justified - read one integration test's gate function e.g., test_f002_reader.py lines 1-40.

Let me batch these.
Now the remaining pieces: SOP line-limit wording, bench factor-like objects, skip-gate pattern, and test style (classes vs functions).

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/docs/SOP.md</path>
<type>file</type>
<content>
85: | 1 | 建分支/worktree 做隔离开发 |
86: | 2 | 严格按 `tasks.md` 里的顺序逐项实现，每完成一项立即勾掉；`[P]` 任务可并行；顺序过时先改 `tasks.md` 再继续 |
87: | 3 | 自检：对照 spec / acceptance criteria 过一遍，跑 `python3 tools/verify.py` |
88: | 4 | （可选）让 AI agent 扮演 reviewer 角色审一遍 diff，输出 findings |
89: | 5 | 合并 + 清理分支 |
90: 
91: ## Code Quality
92: 
93: - File limits: 200 行建议拆分 / 350 行硬上限。
94: - 分层与命名约定：node 见 `docs/decisions/` 目录结构 ADR；python 采用单一布局
95:   `src/alphamill/<module>/`（子包：data_bridge、factor_factory、validation、
96:   kronos_service 等）；非 Python 资产（docker-compose、deployment/、docs/）留仓库根。
97: 
98: ### F001 原样迁移文件豁免
99: 
100: 以下文件是 F001 从旧仓原样迁入、且尚未进入 F002 泛化范围的历史脚本，暂不按 350 行
101: 硬上限拆分。豁免截止 `F002` 完成对应模块泛化时，由 owner 复核并删除或续期；豁免不
102: 放宽运行时验证和质量门
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== fixtures in unit ===
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:57:@pytest.fixture(scope="module")
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:86:@pytest.fixture()
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:95:@pytest.fixture()
/home/georg/projects/alphamill-F003/tests/integration/test_f002_reader.py:26:@pytest.fixture()
/home/georg/projects/alphamill-F003/tests/integration/test_f004_real_profile.py:92:@pytest.fixture(scope="module")
/home/georg/projects/alphamill-F003/tests/integration/test_f002_export_reconcile.py:40:@pytest.fixture()
/home/georg/projects/alphamill-F003/tests/integration/test_f002_revision.py:24:@pytest.fixture()


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:14:class Position:
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:22:def main() -> int:
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:24:        description="Independent candle-by-candle replay for KronosFusionStrategy signal logic."
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:46:        pair: add_signals(frame, kronos_mode=args.kronos_mode) for pair, frame in frames.items()
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:149:                "KronosFusionStrategy currently fe
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
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:96:def f002_lake(tmp_path, monkeypatch):
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:98:    lake = tmp_path / "lake"
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:100:    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "symbol_map.csv"))
/home/georg/projects/alphamill-F003/tests/integration/conftest.py:104:def seed_f002_data(conn) -> None:
/home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py:27:def test_cli_incremental_run_exit_zero_and_artifacts(f002_conn, f002_lake, tmp_path):
/home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py:37:            "ALPHAMILL_SYMBOL_MAP_CURRENT": str(tmp_path / "symbol_map.csv
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:33Z

- **tool**: `bash({"command": "grep -rn \"FactorDef\\|HypothesisDef\\|definition_digest\\|factor_id\\|data_columns\\|FactorInput\\|FactorOutput\\|PanelFrame\\|compute\" /home/georg/projects/alphamill-F003/src /home/georg/projects/alphamill-F003/tests 2>/dev/null | grep -v \".pyc\" | grep -v \"compute_value_digest\\|_compute\\|computing\" | head -60; echo \"=== EXIT $? ===\""})`
- **tool**: `bash({"command": "grep -n \"test_f003_\\|tests/unit\\|tests/integration\\|FactorDef\\|HypothesisDef\\|factor_store\\|run_store\" /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/tasks.md | head -60"})`
- **tool**: `bash({"command": "grep -rn \"compute\\b\\|compute=\\|compute:\" /home/georg/projects/alphamill-F003/src/alphamill/kronos_service/generator.py | head; echo \"=== kronos generator head ===\"; sed -n '1,60p' /home/georg/projects/alphamill-F003/src/alphamill/kronos_service/generator.py 2>/dev/null"})`


> [reasoning] I now have a clear picture. Let me also confirm the F003 tasks.md test plan for test names and expected module paths (helps downstream). And check whether data_bridge has a helper for temp dirs / fixture. Also check how tests avoid touching real lake: monkeypatch ALPHAMILL_LAKE_DIR to tmp_path. There's `f002_lake`.

Let me quickly read the F003 tasks.md test section and check for existing factor-related modules. Also check the `.sdd.json` maybe. And verify no FactorDef in tools besides doc consistency.

Let me also check the F003 tasks.md for the four test files the user mentions (test_f003_generator_contract.py etc.) to align. And check whether there is a `tests/unit/conftest.py` (there isn't). 

Let me read tasks.md.

Also important: the user asked "Every occurrence of a factor definition object: search for FactorDef, HypothesisDef, compute, data_columns, scope, factor_id, definition_digest, meta across src/ and tests/". I've done the grep. Let me do a comprehensive grep across src/tests to be safe and get exact hits with context. I found only tools/check_doc_consistency.py references and docs. Let me run one final grep for the bare terms across src/tests.

Let me batch: read tasks.md, final grep, and check for any `PanelFrame`/`FactorInput` definitions.
Final gap-check: tasks.md test plan, exhaustive term grep in src/tests, and FactorInput/PanelFrame types.

  <details><summary>tool output</summary>

  ```text
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py:196:    if declared != recomputed:
/home/georg/projects/alphamill-F003/src/alphamill/data_bridge/manifest.py:199:            f"（manifest {declared}，重算 {recomputed}）"
/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/bench/independent_cross_backtest.py:151:                "precomputed timestamped Kronos signals are supplied."
/home/georg/projects/alphamill-F003/tests/unit/test_check_doc_consistency.py:415:def test_f007_dedup_goes_red_when_writeback_recomputes(tmp_path: pathlib.Path) -> None:
=== EXIT 0 ===


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
21:- 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
29:- [ ] T001 (`FR-003`, `AC-003`): 冻结并校验 F008 宇宙台账 artifact 的消费契约（按 digest 加载、`universe_at(T)` 与 `schema_version` 可读），产出 T020 的输入夹具；F008 未落地时以显式 universe 配置作为等价夹具 — verify: `tests/unit/test_f003_binding.py`
30:- [ ] T002 (`FR-003`, `DR-001`): 固定绑定文件格式并验证目标 dataset 的 valid 版本与 `value_digest` 可由 F002 reader 解析 — verify: `tests/unit/test_f003_binding.py`
32:- [ ] T004 (`NFR-002`, `NFR-005`): 打通并标定执行机 `qiaozhi-lt`——**先恢复 shell 接入**（env-manager 台账记录 2026-09-14 全端口复测 22/2222/2200/8022/3389/5985 全闭，当前无 shell 路径，按 `references/access-methods.md` §4 启用 Windows OpenSSH）；再在其 WSL2 内实测 CUDA 可用性与可用显存，按 §7.1 标定显存上限写进配置（不写死代码）；确认该机 F002 湖可读且通过完整性校验 — verify: `tests/unit/test_f003_gpu_slot.py`（能力探测纯函数）+ 在 `qiaozhi-lt` 上用 `alpham
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== kronos generator head ===
from statistics import mean


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def generate_placeholder_signal(rows: list[dict]) -> dict:
    if len(rows) < 30:
        return {
            "signal_type": "neutral",
            "confidence": 0.0,
            "expected_return": 0.0,
            "volatility": 0.0,
            "direction_prob": 0.5,
            "reason": "not_enough_data",
        }

    closes = [float(row["close"]) for row in rows]
    returns = [
        (closes[idx] / closes[idx - 1]) - 1 for idx in range(1, len(closes)) if closes[idx - 1] != 0
    ]
    short_return = (closes[-1] / closes[-12]) - 1 if closes[-12] else 0.0
    avg_return = mean(returns[-30:]) if returns else 
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:38Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py", "offset": 55, "limit": 30})`


> [reasoning] I have everything. Let me compose the report. The term grep confirms: NO FactorDef/HypothesisDef/compute/data_columns/factor_id/definition_digest in src/ or tests/. Only docs and tools/check_doc_consistency.py. So FactorDef must be created new.

Let me also verify the line-limit enforcement detail: test_f001_line_limit_exemptions.py scans src, freqtrade, deployment for .py/.ps1 >350 lines and requires exact match with SOP exemption table. It doesn't scan tests/ or tools/. But SOP says 350 hard limit generally. Design.md says factor_factory code subject to 350 limit. Note: new files in tests/ aren't scanned by that particular test, but verify.py's ruff (E501 at 100) applies to tests too. Actually careful: the test only checks src/freqtrade/deployment, not tests. But SOP line limit is a repo convention.

Also note: new F003 files must stay under 350; the exemption table currently has 9 files, and adding any >350 file in src would break test_f001_line_limit_exemptions.py unless registered.

Now, test conventions:
- Plain module-level functions `def test_*` — no test classes anywhere (grep for class Test returned nothing).
- Module docstrings in Chinese, prefixed with feature id / AC ids.
- `from __future__ import annotations` often (integration conftest, some tests). Not universal in unit tests.
- pytest fixtures defined in tests/integration/conftest.py (module scope f002_db, function scope f002_conn, f002_lake). No tests/unit/conftest.py. No root conftest.
- Integration tests use `pytestmark = pytest.mark.integration`.
- Env gating: `INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION","").lower() in {"1","true","yes"}`; helper `_require_integration`-style that pytest.fail if required but unavailable, else pytest.skip. Unset → skip.
- ALPHAMILL_REAL_LAKE_DIR specific to test_f002_schedule_backup.py.
- Avoid real lake: tmp_path + monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(tmp_path/"lake")), and delete env vars so read uses explicit lake_root.
- pyproject pytest config: addopts `-ra --strict-markers`, testpaths tests, pythonpath [".","src"], marker integration.
- Integration tests import conftest helpers directly: `from conftest import D1, D3, D4, seed_f002_data` — because rootdir/confcutdir tests and pythonpath.

- `--confcutdir=tests --rootdir=tests tests/unit tests/integration` in verify.

Let me give exact excerpts. I have them.

For helper for building temp dirs/fixtures for data_bridge: the conftest f002_lake fixture is the canonical one; seed_f002_data and export_symbol_map_for helpers. Also unit-level manual construction in test_f002_reader_contract.py (writes parquet + manifest with tmp_path). No dedicated "data_bridge fixture builder" beyond that.

Now the FactorDef shape: architecture §4.1 lines 254-277. Design §3 line 105 gives disk DTO fields. The executable FactorDef fields per architecture: factor_id, hypothesis_id, name, generator, scope, params, compute, data_columns, meta. Plus design says feature_map_digest and run_id/created_at are DTO-level.

Also note architecture says `scope: Literal["time_series","cross_sectional"]`, `params: dict`, `compute: Callable[[FactorInput], FactorOutput]`, `data_columns: list[str]`, `meta: dict`. Dataclass frozen.

Also note absence of FactorInput/FactorOutput definitions anywhere — need to define.

Also `tools/check_doc_consistency.py` lines 71-74 check the design doc string `factor_id = <generator>_<definition_digest[:12]>`. Let me read that snippet for exactness. Let me grab lines 60-90.

Let me quickly read that to report accurately.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py</path>
<type>file</type>
<content>
55: 
56: TEXT_CHECKS: tuple[TextCheck, ...] = (
57:     TextCheck(
58:         "architecture_universe_calendar_split_aligned",
59:         "F007-D045",
60:         requires=(
61:             (ARCH, '"universe_digest"'),
62:             (ARCH, '"calendar_digest"'),
63:             (ARCH, "lake/_metadata/universes/<digest>.csv"),
64:             (ARCH, 'sha256(canonical_json({"universe": <universe_digest>,'),
65:             (ARCH, '"calendar": <calendar_digest>}))'),
66:             (ARCH, "`universe_path` / `calendar_path`"),
67:         ),
68:         forbids=((ARCH, "显式 universe/calendar JSON 由构造器规范化后保存于"),),
69:     ),
70:     TextCheck(
71:         "factor_id_no_run_seq",
72:    
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:47Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py", "offset": 1, "limit": 95})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py", "offset": 1, "limit": 32})`


> [reasoning] I have all needed. Now compose the final structured report with file:line refs and verbatim excerpts. Keep it actionable, lead with answer.

Key headline: No executable FactorDef exists anywhere in src/ or tests/. You must create it. Follow architecture §4.1 exactly.

Let me structure per the 5 requests.

I should include absolute paths.

Let me write it.

For test conventions, give the essential patterns with file:line.

Line limit: test_f001_line_limit_exemptions.py enforces >350 for src/freqtrade/deployment; SOP §93. Note tests/ not scanned, tools/ not scanned.

Let me now produce. Keep within cap-of-5 lists where possible but this is an explain task. I'll use grouping.

Provide verbatim excerpts:
- conftest.py lines 57-101 (f002_db, f002_conn, f002_lake), 104-196 helpers.
- pyproject lines 42-50.
- integration gate pattern test_f002_reader.py lines 12-23 and the gate helper from another file. Let me include test_f003_kronos_lifecycle.py lines 38-54 maybe. I have grep but not exact text. Let me just quote from test_f002_reader.py and reference. Actually I can quote the gate pattern from test_f004_real_profile.py lines 35-45 based on grep. But I don't have verbatim full. Better to read one small gate block. Let me just quote what I have from grep plus test_f002_reader.py. Actually I should provide verbatim. Let me read test_f001_collector_smoke.py lines 19-30 and test_f002_schedule_backup.py 78-90. Quick read.

Let me do that to ensure verbatim accuracy.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py</path>
<type>file</type>
<content>
1: """F002 调度与灾备接入集成测试（AC-006）。
2: 
3: - CLI 子进程按 timer 同款调用方式增量导出 → 退出码 0、manifest/分区齐备；
4: - systemd unit 契约（02:00/周日 04:00、重试与退出码锁定）由
5:   tests/unit/test_f002_timer_contract.py 覆盖；
6: - backup-nas.sh 的 lake/ 同步行由 tests/unit/test_backup_nas_contract.py 覆盖；
7:   NAS 端产物齐全的真实传输验证在 T010 手工执行并记入验收证据（SOP 真实环境
8:   测试纪律：外部 NAS 凭据/网络不在 pytest 自动化范围内，须显式记录）。
9: """
10: 
11: from __future__ import annotations
12: 
13: import os
14: import subprocess
15: import sys
16: from pathlib import Path
17: 
18: import pytest
19: from conftest import D4, F002_DB, seed_f002_data
20: 
21: from alphamill.data_bridge import manifest as mf
22: from alphamill.data_bridge import registry
23:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py</path>
<type>file</type>
<content>
1: """F001 AC-003 采集器冒烟：单交易对采集 + 幂等复跑 + 未闭合 K 线过滤。
2: 
3: 需要本地 TimescaleDB 在线且可出网（经 BINANCE_HTTPS_PROXY 代理，见 deployment/.env）。
4: 数据库不可达时跳过（CI 场景），本地全绿为准（SOP 真实环境测试纪律）。
5: """
6: 
7: import os
8: import sys
9: from datetime import UTC, datetime, timedelta
10: from pathlib import Path
11: 
12: import pytest
13: 
14: sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
15: 
16: ccxt_ingestor = pytest.importorskip("alphamill.data_bridge.collector.ccxt_ingestor")
17: db_writer = pytest.importorskip("alphamill.data_bridge.collector.db_writer")
18: 
19: pytestmark = pytest.mark.integration
20: INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").low
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:11:53Z


> [reasoning] I have everything. Compose the report now.

Note the grep result for FactorDef in src/tests produced nothing — confirmed. Also `compute` only appears in unrelated contexts (recomputed). So no executable factor object exists.

Let me write final answer with file:line refs and verbatim snippets.
## Headline

**No executable `FactorDef` / `HypothesisDef` exists anywhere in `src/` or `tests/`.** Grep for all seven terms (`FactorDef`, `HypothesisDef`, `compute`, `data_columns`, `scope`, `factor_id`, `definition_digest`, `meta`) across `src/` + `tests/` returns zero type definitions — only docs and two doc-consistency string checks. You must create `FactorDef` fresh from architecture §4.1; there is nothing to extend or duplicate. `factor_factory/__init__.py` is empty of exports.

---

### 1. Test conventions

**Structure: plain module-level functions only.** No `class Test*` anywhere in the repo. `tests/unit` has **no `conftest.py`**; the only conftest is `/home/georg/projects/alphamill-F003/tests/integration/conftest.py`. There is no root conftest.

**pytest config** — `/home/georg/projects/alphamill-F003/pyproject.toml:42-50`:
```toml
[tool.pytest.ini_options]
addopts = "-ra --strict-markers"
testpaths = ["tests"]
pythonpath = [".", "src"]
markers = [
  "integration: 需要本地服务（TimescaleDB 等）在线的集成测试",
]
```
`--strict-markers` means any `@pytest.mark.x` not registered fails.

**verify.py collection** — `/home/georg/projects/alphamill-F003/tools/verify.py:45-57` runs exactly:
```
pytest -q --confcutdir=tests --rootdir=tests tests/unit tests/integration
```
Only those two dirs are gated (design.md:27 restates this). `tests/property`, `tests/simulation` are `.gitkeep`-only.

**Integration gating pattern** (env-var, justify-skip-vs-fail). Canonical form at `/home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py:19-28`:
```python
pytestmark = pytest.mark.integration
INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}

def _require_or_skip(available: bool, reason: str) -> None:
    if available:
        return
    if INTEGRATION_REQUIRED:
        pytest.fail(reason)
    pytest.skip(reason)
```
Semantics: **unset → skip; set but capability absent → `pytest.fail`**. Same in `conftest.py:67-69`, `test_f002_export_reconcile.py:21-37`, `test_f003_kronos_lifecycle.py:46-54`, `test_f004_real_profile.py:35-45`.

**Module docstring convention**: Chinese docstring naming feature + AC IDs, e.g. `test_f002_reader.py:1-5`:
```python
"""F002 DuckDB 取数入口集成测试（AC-003/008/009/013）。

复用 conftest 的一次性 f002_integration 库与种子数据；真实 TimescaleDB
在线时运行，否则按 SOP 约定跳过（ALPHAMILL_INTEGRATION=1 下判红）。
"""
```
Individual tests also carry a one-line `"""AC-xxx：..."""` docstring (`test_f002_reader.py:39`).

**`from __future__ import annotations`** is used in integration conftest and most newer tests, but not universally (unit tests like `test_f002_exporter.py` omit it).

**Fixtures** — all in `tests/integration/conftest.py`; unit tests use `tmp_path` + `monkeypatch` directly, no fixtures. Verbatim `conftest.py:57-101`:
```python
@pytest.fixture(scope="module")
def f002_db():
    """一次性模块级集成库：真实 schema（db/init.sql + 003 migration），测后销毁。

    需要本机 docker 与 quant-timescaledb 容器在线；不可用时按 SOP 约定跳过
    （ALPHAMILL_INTEGRATION=1 下判红）。quant 角色为超级用户，可自建库。
    """
    try:
        _docker_psql("postgres", command="SELECT 1")
    except Exception as exc:  # docker/容器不可达
        if os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}:
            pytest.fail(f"ALPHAMILL_INTEGRATION=1 但 docker/DB 不可达: {exc}")
        pytest.skip(f"docker 或 quant-timescaledb 不可达: {exc}")
    ...
    yield creds
    _docker_psql("postgres", command=f"DROP DATABASE IF EXISTS {F002_DB}")

@pytest.fixture()
def f002_conn(f002_db):
    conn = psycopg2.connect(**f002_db)
    try:
        yield conn
    finally:
        conn.close()

@pytest.fixture()
def f002_lake(tmp_path, monkeypatch):
    """每个测试独立的临时湖 + current symbol_map，绝不触碰真实 lake/。"""
    lake = tmp_path / "lake"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(lake))
    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "symbol_map.csv"))
    return lake
```

**How tests avoid the real lake**: `tmp_path` + `monkeypatch.setenv("ALPHAMILL_LAKE_DIR", ...)`, or explicitly pass `lake_root=tmp_path` and `monkeypatch.delenv(...)` (`test_f002_reader_contract.py:75-84`). The real-lake path is opt-in and double-gated — `test_f002_schedule_backup.py:80-87`:
```python
configured = os.environ.get("ALPHAMILL_REAL_LAKE_DIR", "").strip()
if not configured:
    if os.environ.get("ALPHAMILL_INTEGRATION") == "1":
        pytest.fail("ALPHAMILL_INTEGRATION=1 时必须设置 ALPHAMILL_REAL_LAKE_DIR")
    pytest.skip("未设置 ALPHAMILL_REAL_LAKE_DIR（本用例仅在有真实湖时运行）")
real_lake = Path(configured).expanduser().resolve()
if not real_lake.is_dir():
    pytest.fail(f"真实 lake/ 不存在: {real_lake}")
```

Integration tests import conftest helpers as a top-level module (`test_f002_reader.py:12`): `from conftest import D1, D3, D4, seed_f002_data` (works because `--rootdir=tests` / `pythonpath=["."]`).

### 2. data_bridge temp-dir helpers

There is **no dedicated data_bridge fixture factory** beyond the integration conftest. The reusable helpers are: `f002_lake` (above), `seed_f002_data(conn)` at `conftest.py:104-189`, and `export_symbol_map_for(conn, lake)` at `conftest.py:192-196`:
```python
def export_symbol_map_for(conn, lake) -> str:
    """测试辅助：为 scratch 库刷新 symbol map，返回 digest。"""
    from alphamill.data_bridge import symbol_map
    return symbol_map.export_symbol_map(conn=conn, lake_root=lake).digest
```
Unit-level lake construction is done inline by hand: `test_f002_reader_contract.py:33-74` writes a parquet partition with `pq.write_table`, builds a symbol map, and calls `manifest.publish_manifest(tmp_path, ...)`. For F003 factor/run store tests you can use bare `tmp_path` passed as the store root (matches this pattern) — no shared helper needed.

### 3. Factor-definition objects — none exist

Exhaustive result: **zero `.py` hits for `FactorDef`, `HypothesisDef`, `definition_digest`, `factor_id`, `data_columns`, `FactorInput`, `FactorOutput`, `PanelFrame` in `src/` and `tests/`.** The only code references are doc-string checks in `/home/georg/projects/alphamill-F003/tools/check_doc_consistency.py:70-77`:
```python
TextCheck(
    "factor_id_no_run_seq",
    "F003-D001",
    requires=(
        (DESIGN, "factor_id = <generator>_<definition_digest[:12]>"),
        (SPEC, "不含 run 序号"),
    ),
    forbids=((DESIGN, "run_seq"), (DESIGN, "_r<run_seq>")),
),
```
`bench/` defines no factor type either — only `Position` (`independent_cross_backtest.py:13-14`) and pandas signal helpers (`add_signals`, `should_exit`). Not reusable as a `FactorDef`. (Skip confirmed.)

**The authoritative shape is architecture §4.1**, `/home/georg/projects/alphamill-F003/docs/alphamill-architecture.md:256-270`:
```python
@dataclass(frozen=True)
class FactorDef:
    factor_id: str            # 如 "alphagen_gen042_f003"
    hypothesis_id: str        # 指向 HypothesisDef；自动公式可指向 mechanism_unknown 假设
    name: str
    generator: str            # alphagen / genetic / expression / manual / kronos / pool（协同池 meta-factor）
    scope: Literal["time_series", "cross_sectional"]
    params: dict
    # 可调用：输入单 pair Frame 或 point-in-time 多 pair PanelFrame，输出同粒度信号；
    # t 时刻值只允许使用 ≤t 的数据和 t 时刻真实可用的宇宙成员。
    compute: Callable[[FactorInput], FactorOutput]
    data_columns: list[str]   # 依赖的数据列（用于数据可用性检查）
    meta: dict                # LaTeX 定义、假设来源、生成器版本等
```
`FactorInput`/`FactorOutput` are referenced but **undefined anywhere** — you define them. Line 276-277: `expression` does **not** go on the executable object; it lives in `meta["expression"]`.

**`HypothesisDef`** shape is only in the F003 design, `/home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md:113`:
> `hypothesis_id` / `mechanism` / `data_columns` / `applicable_state` / `expected_holding_period` / `cost_sensitivity` / `source` / `generation`. 内置 `mechanism_unknown` 条目…

**On-disk DTO (different field set from executable object)** — design.md:105-111. Disk `schema_version:1`: `factor_id` / `definition_digest` / `hypothesis_id` / `name` / `generator` / `generator_version` / `scope` / `expression` / `params` / `data_columns` / `feature_map_digest` / `run_id` / `created_at`. Digest excludes `factor_id`/`run_id`/`created_at`; `factor_id = <generator>_<definition_digest[:12]>`. Design.md:110 states the load contract: `factor_store.load()` must return an executable object with `compute` rebuilt and `meta` restored.

### 4. `factor_factory` exports

`/home/georg/projects/alphamill-F003/src/alphamill/factor_factory/__init__.py` is one line:
```python
"""Factor generation and evaluation components."""
```
No `__all__`, no imports. `bench/__init__.py` likewise. Plan (not built): `generators/`, `hypotheses/{schema,catalog}.py`, `registry/{factor_store,pool_store,run_store}.py`, `cli.py` — design.md:47-71.

### 5. 350-line enforcement

Enforced by a **unit test**, not ruff: `/home/georg/projects/alphamill-F003/tests/unit/test_f001_line_limit_exemptions.py:9-24`:
```python
def test_all_f001_over_limit_files_are_registered_with_an_expiry() -> None:
    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
    section = sop.split("### F001 原样迁移文件豁免", 1)[1].split("\n## ", 1)[0]
    registered = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.MULTILINE))
    actual = {
        str(path.relative_to(ROOT))
        for root in (ROOT / "src", ROOT / "freqtrade", ROOT / "deployment")
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".ps1"}
        and len(path.read_text(encoding="utf-8").splitlines()) > 350
    }
    assert actual == registered
    assert "解除期限" in section
    assert "F002" in section
```
Scope: `src/`, `freqtrade/`, `deployment/` only (`.py`/`.ps1`) — **`tests/` and `tools/` are NOT scanned by this test**, but SOP §Code Quality (`docs/SOP.md:93`) states "350 行硬上限" repo-wide, and design.md:26 binds `factor_factory` code to it. The exemption table is `docs/SOP.md:104-114` (9 files, all F001-migrated). **Practical rule for F003: any new `src/alphamill/factor_factory/**` file >350 lines will fail this test unless you also add it to the SOP table — don't; split instead.** Ruff line-length is 100 (`pyproject.toml:53`), and F003 vendor dir will be `extend-exclude`d per design.md:233.

<results>
<files>
- /home/georg/projects/alphamill-F003/tests/integration/conftest.py - only conftest; f002_db/f002_conn/f002_lake fixtures + seed_f002_data/export_symbol_map_for helpers (lines 57-196)
- /home/georg/projects/alphamill-F003/pyproject.toml - pytest config, integration marker, pythonpath, ruff excludes (lines 42-65)
- /home/georg/projects/alphamill-F003/tools/verify.py - public gate; pytest collects only tests/unit + tests/integration (lines 45-57)
- /home/georg/projects/alphamill-F003/tests/unit/test_f001_line_limit_exemptions.py - the 350-line enforcement test
- /home/georg/projects/alphamill-F003/docs/SOP.md - 350-line rule (line 93) + F001 exemption table (lines 98-114)
- /home/georg/projects/alphamill-F003/docs/alphamill-architecture.md - authoritative FactorDef definition §4.1 (lines 254-277)
- /home/georg/projects/alphamill-F003/docs/features/0.2/F003-alphagen-vendor/design.md - disk DTO, HypothesisDef, module layout, test plan (lines 47-125, 236-253)
- /home/georg/projects/alphamill-F003/src/alphamill/factor_factory/__init__.py - empty of exports (1 docstring line)
- /home/georg/projects/alphamill-F003/tools/check_doc_consistency.py - only code refs to factor_id/definition_digest, as doc-string checks (lines 70-77)
- /home/georg/projects/alphamill-F003/tests/integration/test_f001_collector_smoke.py - canonical env-gate pattern `_require_or_skip` (lines 19-28)
- /home/georg/projects/alphamill-F003/tests/integration/test_f002_schedule_backup.py - ALPHAMILL_REAL_LAKE_DIR gating (lines 80-87)
- /home/georg/projects/alphamill-F003/tests/unit/test_f002_reader_contract.py - unit-level tmp_path lake construction pattern (lines 12-87)
</files>

<answer>
There is no existing FactorDef/HypothesisDef to extend — create them in `src/alphamill/factor_factory/` per architecture §4.1. FactorDef is a frozen dataclass with exactly: factor_id, hypothesis_id, name, generator, scope (Literal["time_series","cross_sectional"]), params, compute (Callable[[FactorInput], FactorOutput]), data_columns, meta. FactorInput/FactorOutput are undefined and yours to introduce. The on-disk JSON DTO has a different field set (adds definition_digest, expression, feature_map_digest, run_id, created_at; drops compute/meta-as-expression), and factor_store.load() must rebuild compute and restore meta. Match test style: plain functions, no classes, unit tests use tmp_path/monkeypatch directly with no fixtures, integration tests carry pytestmark = pytest.mark.integration and the unset→skip / set-but-missing→fail gate. Keep every new src file ≤350 lines because test_f001_line_limit_exemptions.py fails if any src/freqtrade/deployment .py exceeds 350 without a SOP table entry.
</answer>

<next_steps>
1. Implement `src/alphamill/factor_factory/generators/base.py` with frozen `FactorDef` matching architecture lines 258-269 verbatim, plus your `FactorInput`/`FactorOutput`.
2. Write `tests/unit/test_f003_factor_store.py` as plain functions using bare `tmp_path` (the f002_reader_contract.py pattern) — no new conftest needed; it belongs in tests/unit where there is no conftest.
3. Run `python3 tools/verify.py` (or at minimum `pytest -q tests/unit/test_f003_factor_store.py` plus the line-limit test) after each file to confirm ≤350 lines and green.
</next_steps>
</results>
