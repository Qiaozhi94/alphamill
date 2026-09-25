---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f54f5084bffeUdodRf65AOC54U"
title: "Audit new document gates (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T16:26:57Z"
updated_at: "2026-09-16T16:43:34Z"
tokens_input: 275897
tokens_output: 5540
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Audit new document gates (@Sisyphus-Junior subagent)

## user · 2026-09-16T16:26:57Z

TASK: Review the newly added F003 document-consistency and task-DAG gates plus their tests for false-green/false-red behavior and coverage of the claimed fixes. EXPECTED OUTCOME: Findings with exact tool/test/doc line evidence, severity, root cause, origin, and concrete fix. REQUIRED TOOLS: Read-only; inspect tools/check_doc_consistency.py, tools/check_task_dag.py, tools/validate_spec_lifecycle.py, tests/unit/test_check_doc_consistency.py, tests/unit/test_check_task_dag.py, tests/unit/test_validate_spec_lifecycle.py, verify.py, and F003 tasks. MUST DO: Verify the gates are actually wired into verify.py, test both positive and mutation cases, check parser assumptions for edge cases (T039/T036 references, [TEST], deprecated text, active indexes), and identify any new gate that can pass while the violated contract remains. MUST NOT DO: No edits or commits; no broad unrelated code review. CONTEXT: Repo /home/georg/projects/alphamill, current HEAD d659db7, Round 2 doc review. Output Chinese.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T16:26:58Z

- **tool**: `skill({"name": "review-convergence", "user_message": "对 F003 新增文档一致性、任务 DAG gate 及测试做 Round 2 代码检视；只读，不编辑不提交；输出中文 findings，严格检查 false-green/false-red、verify.py 接线、正向和 mutation 测试、parser 边界及 F003 tasks。基线 HEAD d659db7。"})`


> [reasoning] **Preparing code review and graph generation**

  <details><summary>tool output</summary>

  ```text
## Skill: review-convergence

**Base directory**: /home/georg/.config/opencode/skills/review-convergence

Base directory for this skill: /home/georg/.config/opencode/skills/review-convergence/
File references (@path) in this skill are relative to this directory.

# Review Convergence

> 优先级:本 skill 优先于任何一次性的 code-review skill(包括 `review-changes`、
> `code-review-agent` 之类)。那些只是报告生成器,没有停止条件——正是本 skill 要修的
> 失效模式。真正一次性、无后续的小审查,可按第 0 节缩减轮次,但仍走本流程。
> 项目 CLAUDE.md 要求优先用 code-review-graph MCP 工具时,把它当作本流程的**取证手段**,
> 而不是替代本流程。

十轮审查还能挑出中等问题、修复还大概率引入新问题——这不是审查不够仔细,是流程没有
收敛条件。"审到审查者没意见为止"不是良定义的停止条件:只要投入足够注意力,任何代码
都能挑出新问题。本skill的目的是让审查在有限轮次内收敛,而不是无限发散。

## 0. 项目适配(每次先做,不要跳过)

在开始之前,读取当前仓库的 `CLAUDE.md` / `AGENTS.md`(如果存在),提取:
- 该项目自己的测试/回归规范(例如"每次修复必须补充回归测试"这类硬性要求)
- 已知的历史教训(例如"assert 被悄悄降级成 warning"这
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:27:18Z

- **tool**: `todowrite({"todos": [{"content": "指定 gate/test/verify.py/F003 tasks：读取实现与契约边界 - 建立 Round 2 审查证据", "status": "in_progress", "priority": "high"}, {"content": "文档一致性与 task-DAG：执行现有测试并构造只读 mutation/边界检查 - 判定 false-green/false-red", "status": "pending", "priority": "high"}, {"content": "verify.py 与生命周期联动：确认真实接线及旁路 - 核对 T039/T036、[TEST]、deprecated、active indexes", "status": "pending", "priority": "high"}, {"content": "整理 findings：按严重度输出精确文件行、根因、来源与修复建议 - 形成中文 Round 2 报告", "status": "pending", "priority": "high"
…[truncated])`


> [reasoning] **Planning baseline codegraph and status checks**
基线：`d659db7`，本轮只读审查，范围限定为 F003 gate、指定测试、`verify.py` 与 F003 tasks。先核对项目约定和变更范围，再做 gate 接线、正反例与 mutation 证据检查。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "指定 gate/test/verify.py/F003 tasks：读取实现与契约边界 - 建立 Round 2 审查证据",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "文档一致性与 task-DAG：执行现有测试并构造只读 mutation/边界检查 - 判定 false-green/false-red",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "verify.py 与生命周期联动：确认真实接线及旁路 - 核对 T039/T036、[TEST]、deprecated、active indexes",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "整理 findings：按严重度输出精确文件行、根因、来源与修复建议 - 形成中文 Round 2 报告",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T16:28:48Z

- **tool**: `codegraph_codegraph_explore({"query": "tools/check_doc_consistency.py tools/check_task_dag.py tools/validate_spec_lifecycle.py tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py verify.py F003 tasks T039 T036 [TEST] deprecated active indexes", "maxFiles": 12})`

  <details><summary>tool output</summary>

  ```text
**Exploration: tools/check_doc_consistency.py tools/check_task_dag.py tools/validate_spec_lifecycle.py tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py verify.py F003 tasks T039 T036 [TEST] deprecated active indexes**

Found 46 symbols across 5 files.

**Blast radius — what depends on these (update/verify before editing)**

- `validate_spec_lifecycle` (MarketGameSim/tools/spec_validation.py:1269) — 1 caller in `MarketGameSim/tools/validate_spec_lifecycle.py`; ⚠️ no covering tests found
- `check` (alphamill/tools/check_secrets.py:57) — 12 callers in `alphamill/tools/check_secrets.py`; tests: `alphamill/tests/unit/test_check_secrets.py`, `alphamill/tests/unit/test_f001_credentials.py`
- `check` (MarketGameSim/tools/check_se
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:29:21Z

- **tool**: `bash({"command": "git status --short --branch && git rev-parse --short HEAD", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/*F003*"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "tools/check_*.py"})`


> [reasoning] **Assessing git status and files**

  <details><summary>tool output</summary>

  ```text
## main...origin/main [ahead 29]
 M docs/features/0.2/F007-evaluation-gates/tasks.md
36b6564


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/CLAUDE.md</path>
<type>file</type>
<content>
1: # AlphaMill
2: 
3: AI 原生的加密量化研究与交易管线：以 AI 因子工厂为核心，贯通数据治理 → 假设与因子 →
4: 证据评测 → 组合与策略 → Freqtrade 执行 → 监控归因与复盘（中文别名：淘沙）。
5: 
6: ## 当前结构
7: 
8: - `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
9: - `docs/alphamill-architecture.md`：四平面架构与接口契约（架构真相源），随实现迭代。
10: - `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
11: - `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
12: - `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射） / 0005 呈现与观测架构 / 0006 证据边界与实验身份 / 0007 研究快照绑定（dataset 独立版本 + ResearchSnapshot） / 0008 北极星改为在跑组合持续盈利（产能降级为分母与能力标定）。
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-cry
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they run in background
// System will notify you when each completes
```

WHY:
- Agents can perform deeper, more thorough searches
- Background tasks run in parallel, saving time
- Specialized agents have domain expertise
- Reduces context window
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 5 file(s)

/home/georg/projects/alphamill/tools/check_doc_consistency.py
/home/georg/projects/alphamill/tools/check_task_dag.py
/home/georg/projects/alphamill/tools/check_dep_pins.py
/home/georg/projects/alphamill/tools/check_secrets.py
/home/georg/projects/alphamill/tools/check_doc_links.py
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:31:10Z

- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "docs/features/0.2/F003-alphagen-vendor/**"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "tests/unit/test_{check_doc_consistency,check_task_dag,validate_spec_lifecycle}.py"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "tools/validate_spec_lifecycle.py"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "tools/verify.py"})`


> [reasoning] **Inspecting exact files for rebaseline**
发现基线漂移：用户给定 `d659db7`，工作树当前 `HEAD=36b6564`；且已有未由本轮产生的 `F007/tasks.md` 修改。我不会把它纳入审查或改动。下面按当前实际 HEAD 做只读复核，并在报告中明确 re-baseline。

  <details><summary>tool output</summary>

  ```text
Found 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they ru
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 3 file(s)

/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py
/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py
/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/verify.py
  ```
  </details>

## assistant · 2026-09-16T16:32:09Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_task_dag.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/verify.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py"})`

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_doc_consistency.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """文档一致性门禁（doc review F003 契约断言回归门）。
3: 
4: 把 F003 检视闭环中被修复的每一处契约写成**可红的断言**：要求项缺失、或旧矛盾
5: 文本回归时即判红。每条 check 对应一个 finding id，便于检视方逐条独立核对。
6: 
7: 覆盖范围：
8:   - 声明式文本断言（`TEXT_CHECKS`）：要求/禁止的字面量，按 finding 分组；
9:   - 解析式断言：F007 是否声明 F003 上游（D014）、AC 断言是否覆盖其引用的子句
10:     （D017）、活跃 feature 索引三处是否一致（D022）。
11: 
12: 用法：python tools/check_doc_consistency.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15: 
16: from __future__ import annotations
17: 
18: import dataclasses
19: import pathlib
20: import re
21: import sys
22: 
23: ROOT = pathlib.Path(__file__).resolve().parent.parent
24: 
25: SPEC = "docs/features/0.2/F003-alphagen-vendor/spec.md"
26: DESIGN = "docs/features/0.2/F00
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_task_dag.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """任务依赖 DAG 校验（doc review F003-D012 回归门）。
3: 
4: 对进入开发流转的 Feature（spec status ∈ {ready-for-development, in-progress,
5: review}）校验 `docs/features/<version>/Fxxx-*/tasks.md`：
6: 
7:   - §4「依赖与并行关系」里所有边端点都是已定义的任务 ID；
8:   - 边一律「向前」：源 ID < 目标 ID（任务编号即执行顺序，禁止依赖后序任务）；
9:   - 最高编号任务（收口任务）必须有至少一条入边；
10:   - `[P]` 任务不得同时声明前置边（tasks 模板规定）。
11: 
12: **作用域说明**：不收 `done`（F001/F004 等历史 Feature 已收口，纳入会立刻破坏
13: 既有文档）与 `draft`（尚未进入流转）。这与 `validate_spec_lifecycle.py` 的
14: status 作用域模式一致。
15: 
16: 用法：python tools/check_task_dag.py
17: 退出码 0 = 全部通过；1 = 存在违规。
18: """
19: 
20: from __future__ import annotations
21: 
22: import pathlib
23: import re
24: import sys
25: 
26: ROOT = pathlib
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/verify.py</path>
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
30: 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: related_features: [F001, F002, F007, F008]
6: topics: [factor-factory, alphagen, vendor, generators, m2]
7: doc_kind: tasks
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F003：AlphaGen vendor 与可插拔生成器平面 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
20: - `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
21: - 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
22: - **机器边界**（架构 §7.1、`docs/SOP.md` §3）：编码、单元测试与门禁在开发机 `qiaozhi-gp`；挖掘训练与全部 GPU/产能证据在执行机 `qiaozhi-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py</path>
<type>file</type>
<content>
1: """check_doc_consistency 回归测试（修复方证据：每条断言必须可红）。
2: 
3: 两组断言：
4:   - 真实仓库上 `run_checks` 全绿；
5:   - 逐条 `TEXT_CHECKS` 做变异：删掉要求文本（或写回废弃文本）后，该 check 必须报错。
6:     变异在 tmp_path 的副本上做，不触碰仓库文件。
7: """
8: 
9: from __future__ import annotations
10: 
11: import pathlib
12: import shutil
13: 
14: import pytest
15: 
16: from tools import check_doc_consistency as cdc
17: 
18: REPO = cdc.ROOT
19: TEXT_CHECK_IDS = [c.check_id for c in cdc.TEXT_CHECKS]
20: ALL_DOC_FILES = {
21:     cdc.SPEC,
22:     cdc.DESIGN,
23:     cdc.TASKS,
24:     cdc.F007_SPEC,
25:     cdc.F007_DESIGN,
26:     cdc.F007_TASKS,
27: }
28: 
29: 
30: def _materialize(tmp_path: pathlib.Path, rels: set[str]) -> None:
31:     #
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py</path>
<type>file</type>
<content>
1: """check_task_dag 回归测试（修复方证据：DAG 门禁可红，且作用域正确）。
2: 
3: 用 tmp_path 下的合成 Feature 覆盖五类违规，并验证 `draft` 不在作用域内
4: （否则会把尚未进入流转的 Feature 一并判红）。
5: """
6: 
7: from __future__ import annotations
8: 
9: import pathlib
10: 
11: from tools import check_task_dag as dag
12: 
13: FEATURE_DIR = pathlib.Path("docs") / "features" / "0.2" / "F001-demo"
14: 
15: 
16: def write_feature(root: pathlib.Path, status: str, tasks: str) -> None:
17:     d = root / FEATURE_DIR
18:     d.mkdir(parents=True, exist_ok=True)
19:     (d / "spec.md").write_text(
20:         "---\n"
21:         "kind: feature\n"
22:         "id: F001\n"
23:         'version: "0.2"\n'
24:         f"status: {status}\n"
25:         "gate_v
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: """validate_spec_lifecycle 回归测试（CURRENT-code.md C002）。
2: 
3: 三组真实校验：frontmatter 解析与 status 必填、AC tests 路径逃逸检查、
4: BACKLOG 双向一致性。全部走 verify_repo(root=tmp_path) 端到端断言。
5: """
6: 
7: from __future__ import annotations
8: 
9: import pathlib
10: 
11: from tools import validate_spec_lifecycle as vsl
12: 
13: SPEC_GATE0_DRAFT = """---
14: kind: feature
15: id: F001
16: version: "0.1"
17: status: draft
18: gate_version: 0
19: ---
20: 
21: # F001-demo
22: 
23: 正文占位。
24: """
25: DESIGN_MIN = "# F001-demo design\n"
26: TASKS_MIN = "# F001-demo tasks\n"
27: BACKLOG_HEADER = "# BACKLOG\n\n| Feature | 版本 | 状态 | 链接 |\n|---|---|---|---|\n"
28: 
29: 
30: def write_feature(tmp_path: pathlib
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。
3: 
4: 校验 docs/features/<version>/Fddd-*/ 三件套：
5:   - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
6:   - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
7:   - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
8:     review/done 的 tests 路径真实存在
9:   - 进入开发流转（ready-for-development / in-progress / review）的 tasks.md
10:     必须含 `### [TEST] 组`（层 2 旅程验收轨）
11:   - BACKLOG.md 与所有非 done Feature 双向集合一致
12: 
13: 纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
14: 并补了变异测试。用法：python tools/validate_spec_lifecycle.py
15: 退出码 0 = 全部通过；1 = 存在违规。
16: """
17: 
18: from __future__ import annotations
19: 
20: import
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:32:40Z

- **tool**: `bash({"command": "python3 -m pytest -q tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 35})`
- **tool**: `bash({"command": "python3 tools/check_task_dag.py; python3 tools/check_doc_consistency.py; python3 tools/validate_spec_lifecycle.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`
- **tool**: `bash({"command": "git diff --stat d659db7..HEAD -- tools/check_doc_consistency.py tools/check_task_dag.py tools/validate_spec_lifecycle.py tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py tools/verify.py docs/features/0.2/F003-alphagen-vendor/tasks.md && git diff --unified=3 d659db7..HEAD -- tools/check_doc_consistency.py tools/check_task_dag.py tests/unit/test_check_task_dag.py tools/verify.py", "workdir": "/home/georg/projects/alp
…[truncated])`


> [reasoning] **Verifying F003 spec enforcement and parser behavior**

> [reasoning] **Identifying parsing bugs and refining F003 regex checks**

> [reasoning] **Detecting missing duplicate task ID checks in DAG**

> [reasoning] **Inspecting task ID uniqueness and lifecycle validation**
实现已确认：`verify.py` 第 37–40 行确实串联生命周期、DAG、文档一致性三道 gate；但 F003 的任务 DAG 是否真正受检取决于 `spec.md` status。当前测试主要是合成 tmp tree，尚未证明真实 F003 在入口中被覆盖。我继续用现有测试和临时副本做 mutation，不写仓库文件。

  <details><summary>tool output</summary>

  ```text
/home/georg/miniconda3/bin/python3: No module named pytest


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002, F007, F008]
8: topics: [factor-factory, alphagen, vendor, generators, m2]
9: doc_kind: spec
10: created: 2026-09-14
11: updated: 2026-09-14
12: ---
13: 
14: # F003：AlphaGen vendor 与可插拔生成器平面
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册）、FR2.2（可插拔生成器）、FR2.3（目标对齐）、FR2.4（纯度与能力边界）、FR2.6（探索组合）；目标 G3；里程碑 M2
21: - **架构来源**：`docs/alphamill-architecture.md` §三（`factor_factory/` 目录分工）、§4.0（闭环核心对象）、§4.1（FactorDef 契约）、§4.1.1（AlphaGen 适配契约与截面边界）、§7.1（机器边界与 GPU 槽位）
22: - **系统设计 / Research / Co
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
check_task_dag: 全部通过
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
tests/unit/test_check_doc_consistency.py |   9 ++-
 tools/check_doc_consistency.py           | 121 +++++++++++++++++++++++++++++++
 2 files changed, 129 insertions(+), 1 deletion(-)
diff --git a/tools/check_doc_consistency.py b/tools/check_doc_consistency.py
index ca62046..e736d69 100644
--- a/tools/check_doc_consistency.py
+++ b/tools/check_doc_consistency.py
@@ -26,6 +26,8 @@ SPEC = "docs/features/0.2/F003-alphagen-vendor/spec.md"
 DESIGN = "docs/features/0.2/F003-alphagen-vendor/design.md"
 TASKS = "docs/features/0.2/F003-alphagen-vendor/tasks.md"
 F007_SPEC = "docs/features/0.2/F007-evaluation-gates/spec.md"
+F007_DESIGN = "docs/features/0.2/F007-evaluation-gates/design.md"
+F007_TASKS = "docs/features/0.2/F007-evaluation-gates/tasks.md"
 
 
 @dataclasses.dataclass(frozen=True)
@@ -163
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:34:06Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "offset": 1, "limit": 85})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "offset": 75, "limit": 65})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md", "limit": 60})`
- **tool**: `bash({"command": "python3 - <<'PY'\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom tools import check_task_dag as d\nfrom tools import check_doc_consistency as c\nfrom tools import validate_spec_lifecycle as v\nimport shutil\n\n# DAG: remove one required F003 test prerequisite while leaving a structurally valid DAG.\nbase = Path('docs/features/0.2/F003-alphagen-vendor')\nwith TemporaryDirectory() as td:\n    root=Path(td); feat=root/'docs/features/0.2/F003-alphagen-vendor'; f
…[truncated])`


> [reasoning] **Planning mutation testing with temporary scripts**

> [reasoning] **Analyzing regex and mutation test limitations**

> [reasoning] **Refining task DAG parsing and edge detection**

> [reasoning] **Analyzing section 5 task lines**

> [reasoning] **Validating task DAG and regex logic**

> [reasoning] **Inspecting frontmatter and section parsing**

> [reasoning] **Planning test mutation via temporary script**

> [reasoning] **Testing DAG edge handling and parser quirks**

> [reasoning] **Identifying DAG parsing and AC check gaps**

> [reasoning] **Inspecting F007 lines for contract inconsistencies**

> [reasoning] **Identifying false-green DAG edge coverage gap**

> [reasoning] **Planning precise document line reading**
现有三门禁命令均返回 0，但 pytest 无法启动：当前解释器缺少 `pytest`，因此不能把“测试通过”作为证据。静态与临时副本探针显示两个重点风险方向：DAG 只验证结构、不验证 F003 声明的必需边；文档索引比较使用集合，重复/部分解析异常可能被吞掉。现在补做可复现的只读 mutation 探针并固定行号证据。

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F002, F003, F004, F008]
8: topics: [evaluation, validation, evidence, experiments]
9: doc_kind: spec
10: created: 2026-09-13
11: updated: 2026-09-17
12: ---
13: 
14: # F007：统一评测台与证据门禁
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
21: - **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
22: - **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级数据源，只有 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
75: - [ ] T030: 回写 spec 的真实 tests/验收证据、BACKLOG 和 feature 状态 — verify: `python3 tools/verify.py`
76: 
77: ## 4. 依赖与并行关系
78: 
79: - `T001,T002,T003 -> T004~T017`：先冻结上游、方法与权限夹具。
80: - `T004,T005 -> T006,T011,T012,T013`：CLI、发布和登记依赖身份与隔离。
81: - `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。
82: - `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。
83: - `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。
84: - `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。
85: - `T009/T016 -> T025`：第二实现对照以成员级统计实现与全链控制证据为
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/BACKLOG.md</path>
<type>file</type>
<content>
1: # BACKLOG —— 活跃 Feature 索引
2: 
3: 本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
4: frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。
5: 
6: | Feature | 版本 | 状态 | 链接 |
7: |---|---|---|---|
8: | F003-alphagen-vendor | 0.2 | draft | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
9: | F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
10: | F008-universe-expansion | 0.2 | draft | [spec](docs/features/0.2/F008-universe-expansion/spec.md) |
11: 
12: > 规则：feature 状态变更（spec frontmatter）时必须同步本表；`done` 的 Feature 移出本表，
13: > 交付记录进入 `docs/features/releases/<version>.md`。
14: > 示例行（复制后替换，链接必须指向真实 spec.md）：
15: > `| F001-<name> | 0.1 | 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
DAG missing T036 edge: []
duplicate active row: []
Q parser malformed: []


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:47Z

- **tool**: `grep({"pattern": "T036/T037/T038|T039|四条判据|四个判据|run_seq|deprecated|废弃|status=completed|termination=early", "path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor", "include": "*.md", "output_mode": "content"})`
- **tool**: `grep({"pattern": "active_feature_indexes|related_features|AC_BODY|TEXT_CHECKS|parse_edges|TASK_RE|TEST_GROUP", "path": "/home/georg/projects/alphamill/tools /home/georg/projects/alphamill/tests", "output_mode": "content"})`
- **tool**: `bash({"command": "python3 - <<'PY'\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom tools import check_doc_consistency as c\nimport shutil\nwith TemporaryDirectory() as td:\n r=Path(td); shutil.copytree('docs/features',r/'docs/features');\n for p in ['BACKLOG.md','CLAUDE.md','docs/README.md']:\n  (r/p).parent.mkdir(parents=True,exist_ok=True); shutil.copy(p,r/p)\n # remove F008 from CLAUDE bullet but leave a second unrelated F008 bullet after active section\n cl=r/'CLAUDE.md';
…[truncated])`


> [reasoning] **Investigating parser assumptions in DAG tests**

> [reasoning] **Analyzing parser edge cases and regex accuracy**

> [reasoning] **Identifying false green text checks**

> [reasoning] **Searching documentation for criteria terms**

  <details><summary>tool output</summary>

  ```text
Found 10 match(es) in 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  97: ├── factors/<factor_id>.json  # FactorDef 定义（只含定义，无结论；仅 status=completed 的运行可被下游入册）
  98: ├── pool.json                 # 协同池 meta-factor（可选；仅 status=completed 的运行产出）
  103: **终态与可消费性**：`run.json` 是唯一运行事实，四种终态 `completed` / `rejected` / `failed` / `partial` 都必须写出，字段至少含 `status`、`termination`、`reason`、`started_at`/`finished_at`；写出之前目录一律视为未完成（与 F002「manifest 最后写」同构）。若终态 manifest 自身写出失败，目录同样视为未完成（fail-safe），不得凭残留物推断终态。**只有 `status=completed` 的运行可被下游消费**：`rejected`/`failed` 不产出候选；`partial` 的 `factors/` 仅作 `show` 诊断残留、不得被下游入册，且不产出 `pool.json`。
  173: - `generation.run_completed`（TR-001，**仅 `status=completed` 的运行发出**）：`generator`、`engine`、`binding`、`seed`、`device`、`tier_level`、`
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No matches found
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
[('active_feature_indexes_aligned', "CLAUDE 活跃集合 ['F003', 'F007'] != 非 done 集合 ['F003', 'F007', 'F008']")]


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:38:02Z

- **tool**: `bash({"command": "python3 - <<'PY'\nfrom pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom tools import validate_spec_lifecycle as v\nfrom tools import check_doc_consistency as c\nimport shutil\n# [TEST] heading in wrong section still accepted by lifecycle check\nwith TemporaryDirectory() as td:\n r=Path(td); d=r/'docs/features/0.1/F001-demo'; d.mkdir(parents=True)\n spec='---\\nkind: feature\\nid: F001\\nversion: \"0.1\"\\nstatus: review\\ngate_version: 1\\n---\\n\\n' + '\\n'.join('
…[truncated])`
- **tool**: `bash({"command": "nl -ba tools/check_task_dag.py | sed -n '68,124p'; nl -ba tools/check_doc_consistency.py | sed -n '334,407p'; nl -ba tools/validate_spec_lifecycle.py | sed -n '201,255p'; nl -ba tests/unit/test_check_task_dag.py | sed -n '44,84p'", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] **Assessing DAG parser limitations and edge cases**

> [reasoning] **Examining regex weaknesses and false positives**

> [reasoning] **Validating parsing scope and deprecated text handling**

> [reasoning] **Planning custom probes for test validation**
已复现至少三类“违规仍绿”：删除 F003 的 `T036 -> T039` 前置边仍被 DAG 接受；BACKLOG 重复 active 行被集合比较吞掉；生命周期 gate 将位于错误章节的 `[TEST]` 标题视为合法。另发现 F007 上游声明和 AC 覆盖均是宽松字面量/单行解析，存在可通过的旁路。整理前再做最小探针确认这些结论与精确行号。

  <details><summary>tool output</summary>

  ```text
TEST wrong section: (True, [])
upstream fake mention: []


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
68	def parse_task_lines(text: str) -> list[tuple[str, bool]]:
    69	    """返回 [(task_id, is_parallel)]，保持文件顺序。"""
    70	    out: list[tuple[str, bool]] = []
    71	    for line in strip_code_blocks(text).split("\n"):
    72	        m = TASK_RE.match(line.strip())
    73	        if m:
    74	            out.append((m.group(1), "[P]" in line))
    75	    return out
    76	
    77	
    78	def parse_edges(text: str) -> list[tuple[str, str]]:
    79	    """解析 §4 的 `A -> B` 链；`A/B -> C/D` 展开为笛卡尔积。
    80	
    81	    非 T 开头的端点（如跨 feature 的 `F008.IR-002`）不参与本次校验。
    82	    """
    83	    edges: list[tuple[str, str]] = []
    84	    for seg in EDGE_SEGMENT_RE.findall(section_body(text, SECTION4)):
    85	        if "->" not in seg:
    86	            continue
    87	        hops = [h.strip() for
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:39:15Z

- **tool**: `todowrite({"todos": [{"content": "指定 gate/test/verify.py/F003 tasks：读取实现与契约边界 - 建立 Round 2 审查证据", "status": "completed", "priority": "high"}, {"content": "文档一致性与 task-DAG：执行现有测试并构造只读 mutation/边界检查 - 判定 false-green/false-red", "status": "completed", "priority": "high"}, {"content": "verify.py 与生命周期联动：确认真实接线及旁路 - 核对 T039/T036、[TEST]、deprecated、active indexes", "status": "completed", "priority": "high"}, {"content": "整理 findings：按严重度输出精确文件行、根因、来源与修复建议 - 形成中文 Round 2 报告", "status": "completed", "priority": "h
…[truncated])`


> [reasoning] **Identifying false green and red edges in DAG**

> [reasoning] **Verifying false red phrase variants**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "指定 gate/test/verify.py/F003 tasks：读取实现与契约边界 - 建立 Round 2 审查证据",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "文档一致性与 task-DAG：执行现有测试并构造只读 mutation/边界检查 - 判定 false-green/false-red",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "verify.py 与生命周期联动：确认真实接线及旁路 - 核对 T039/T036、[TEST]、deprecated、active indexes",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "整理 findings：按严重度输出精确文件行、根因、来源与修复建议 - 形成中文 Round 2 报告",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T16:39:36Z

**Round 2 代码检视结论：不通过**

基线发生漂移：用户给定 `d659db7`，当前实际 `HEAD=36b6564`。工作树另有未由本轮产生的修改：`docs/features/0.2/F007-evaluation-gates/tasks.md`。以下按当前 HEAD 只读审查，未编辑、未提交。

**发现**

| ID | 严重度 | 分类 | 根因 | 来源 | 证据 |
|---|---|---|---|---|---|
| `dag-does-not-enforce-declared-f003-edges` | High | correctness / false-green | DAG gate 只检查 tasks.md 中“写出来的边”是否结构合法，不验证 F003 声明的关键前置边必须存在 | original-coding | F003 明确要求 `T036/T037/T038 -> T039`（[tasks.md:100](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:100)）。只读 mutation 删除 `T036` 后，`check_task_dag.run_checks()` 仍返回 `[]`。实现仅遍历解析出的边（[check_task_dag.py:106-123](/home/georg/projects/alphamill/tools/check_task_dag.py:106)）。现有测试只覆盖未知端点、反向边、最高任务无入边和展开，不覆盖“删除既有契约边”([test_check_task_dag.py:44-84](/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py:44))。 | 
| `test-group-location-not-validated` | Medium | correctness / false-green | `[TEST]` 组用全文正则匹配，没有限定必须位于 tasks.md 第 3 节“验证与验收任务” | original-coding | `validate_spec_lifecycle.py:63` 的 `TEST_GROUP_RE` 是 `^###\s+\[TEST\]` 全文匹配，使用处为 [lines 210-211](/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py:210)。只读合成文档把伪造的 `### [TEST]` 放入第 5 节，`verify_repo()` 仍返回 `(True, [])`。这允许验收组写在错误章节而通过 gate。现有测试只覆盖完全缺少该标题及 draft 豁免([test_validate_spec_lifecycle.py:172-195](/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py:172))。 |
| `active-index-duplicates-are-silent` | Medium | correctness / false-green | active index 使用 set 比较，丢失重复行信息；重复 BACKLOG active 行仍可通过 | original-coding | [check_doc_consistency.py:368-375](/home/georg/projects/alphamill/tools/check_doc_consistency.py:368) 将 BACKLOG 行收集到 `set`，重复 F003 行的只读 mutation 返回 `[]`。而 `validate_spec_lifecycle.py` 同样使用 `row_names = {r[0] for r in rows}`([lines 274-278](/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py:274))，因此统一入口也无法捕获重复索引。现有测试只测删除 F008 行，不测重复行([test_check_doc_consistency.py:107-118](/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:107))。 |
| `f007-upstream-contract-check-allows-unrelated-mention` | Medium | correctness / false-green | F007 upstream 检查只要求全文出现 `**F003**`，不验证该标记位于“上游 Contract”及其具体事件/能力契约上下文 | original-coding | [check_doc_consistency.py:334-343](/home/georg/projects/alphamill/tools/check_doc_consistency.py:334) 只检查 `related_features` 含 F003 和全文 `**F003**`。只读 mutation 将真实 Contract 内容替换成历史说明 `**F003** is mentioned in a historical note`，检查仍返回 `[]`。现有测试只删除 frontmatter 中 F003，不测试正文旁路([test_check_doc_consistency.py:121-132](/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:121))。 |
| `ac-clause-check-is-single-line-and-literal` | Low | test-coverage / false-green | D017 只解析严格单行 AC，且仅检查字面字符串；换行、同义结构或嵌套格式可能绕过检查 | original-coding | AC 解析器为 [check_doc_consistency.py:367, 346-361](/home/georg/projects/alphamill/tools/check_doc_consistency.py:346)，要求整行匹配。现有 mutation 只删除 `DR-001 运行字段` 字面量([test_check_doc_consistency.py:134-142](/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:134))，没有测试 AC 换行、重复 AC、或引用子句出现在描述而非验收断言中的情况。该项当前更像覆盖缺口，未确认必然产品绕过，严重度为 Low。 |

**已确认项**

- `verify.py` 已接线：
  - lifecycle：`tools/verify.py:37`
  - doc links：`tools/verify.py:38`
  - task DAG：`tools/verify.py:39`
  - doc consistency：`tools/verify.py:40`
- 真实命令均返回 0：
  - `python3 tools/check_task_dag.py`
  - `python3 tools/check_doc_consistency.py`
  - `python3 tools/validate_spec_lifecycle.py`
- F003 当前 `status: draft`（[spec.md:5](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:5)），因此当前实际 DAG gate 不会检查 F003；只有进入 `ready-for-development`、`in-progress` 或 `review` 才进入作用域([check_task_dag.py:27,147-153](/home/georg/projects/alphamill/tools/check_task_dag.py:27))。这符合脚本声明的 draft 豁免，但意味着 F003 任务边目前没有真实入口覆盖。
- T039/T036 引用存在，但没有被 gate 作为特定契约验证：
  - T036/T037/T038 → T039：[tasks.md:100](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:100)
  - T039：[tasks.md:88](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:88)
- deprecated 文本 mutation 对 `TEXT_CHECKS` 本身有覆盖，但仅覆盖每条 forbidden 列表的第一个条目([test_check_doc_consistency.py:59-66](/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:59))，没有验证同一契约中其余 forbidden 条目。
- pytest 未能执行：当前解释器报 `/home/georg/miniconda3/bin/python3: No module named pytest`。因此不能声称指定单测通过。

**建议修复**

1. 为 F003/F007 固化“必需边集合”断言，至少锁定 `T036/T037/T038 -> T039`；mutation 删除任一边必须失败。
2. 将 `[TEST]` 检查改为先提取第 3 节正文，再在该节内检查标题；增加“错误章节伪造标题”的红灯测试。
3. active index 同时检查列表长度与集合，或直接对重复 feature ID 报错；补充 BACKLOG、CLAUDE、`docs/README.md` 各自重复项测试。
4. F007 upstream 检查改为验证具体 Contract 片段，例如事件名、`status=completed` 约束和算子登记表必须共同存在于指定章节；增加“无关 F003 mention”mutation。
5. 为 AC 解析增加多行/格式边界测试，并明确 AC 的结构化解析契约，避免仅靠字面包含。

**门槛状态**

- Critical/High：1 个未清零，不能闭环。
- 测试：无法运行，pytest 缺失。
- 未编辑仓库，未生成或修改 review 文档。
