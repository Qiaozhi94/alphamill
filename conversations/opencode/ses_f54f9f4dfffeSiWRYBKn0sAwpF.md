---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f54f9f4dfffeSiWRYBKn0sAwpF"
title: "修复 f007 设计文档检视问题"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T16:21:35Z"
updated_at: "2026-09-16T17:27:00Z"
tokens_input: 182663
tokens_output: 62787
cost: 0.1965
---

# 修复 f007 设计文档检视问题

## user · 2026-09-16T16:21:35Z

<system-reminder>Note: The user opened the file "/home/georg/projects/alphamill/docs/alphamill-prd.md". This may or may not be relevant to the current task.</system-reminder>

当前项目的f007需求的设计文档已经进行了第一轮的检视，请站在修复者的视角按照skill要求对检视问题进行审视和修复

## assistant · 2026-09-16T16:21:35Z

- **tool**: `skill({"name": "review-convergence", "user_message": "f007 设计文档第一轮检视后的修复者视角修复"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill/docs/ 2>/dev/null; echo \"---FEATURES---\"; ls -la /home/georg/projects/alphamill/docs/features/ 2>/dev/null"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline -15 && echo \"---STATUS---\" && git status --short | head -30"})`


> [reasoning] The user wants me to fix review issues for feature f007 design docs. Let me first understand the project and the review.

I should look at the project structure, find f007 docs, and the review report. Let me use the review-convergence skill since it's the default protocol for reviews, and it also covers fix-verify loops ("站在修复者的视角" = as the fixer).

Let me load the skill and explore in parallel.
I detect **fix intent** — f007 design docs passed round-1 review, and I'm to act as the fixer. My approach: load `review-convergence` (fixer-side protocol), locate the f007 review report + docs, then repair the issues.

  <details><summary>tool output</summary>

  ```text
## Skill: review-convergence

**Base directory**: /home/georg/projects/skills-manager-backup/review-convergence

Base directory for this skill: /home/georg/projects/skills-manager-backup/review-convergence/
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
- 已知的历史教训(例如"assert 被悄
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 152
drwxr-xr-x  7 georg georg  4096 Sep 15 01:58 .
drwxr-xr-x 23 georg georg  4096 Sep 15 22:00 ..
-rw-r--r--  1 georg georg  4550 Sep 16 23:02 README.md
-rw-r--r--  1 georg georg  8223 Sep 14 21:48 SOP.md
-rw-r--r--  1 georg georg 34939 Sep 16 23:36 alphamill-architecture.md
-rw-r--r--  1 georg georg 13267 Sep 14 21:48 alphamill-integration.md
-rw-r--r--  1 georg georg 27142 Sep 15 01:58 alphamill-prd.md
-rw-r--r--  1 georg georg 20663 Sep 10 00:25 alphamill-research-factor-mining.md
drwxr-xr-x  2 georg georg  4096 Sep 15 01:58 decisions
drwxr-xr-x  3 georg georg  4096 Sep 13 02:25 design
drwxr-xr-x  6 georg georg  4096 Sep 12 01:27 features
drwxr-xr-x  2 georg georg  4096 Sep 13 15:30 research
drwxr-xr-x  2 georg georg  4096 Sep 16 23:41 reviews
---FEATURES---
total 36
drwxr-xr-x 6
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
d659db7 test(f003): 新增任务 DAG/文档一致性/[TEST] 组门禁 + 变异单测（D011/D012 及各 finding 回归锁定）
fcc14ad fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
ab30da9 fix(f003): D002/D007/D010 术语归一——终态小写、池版本键改 factor_id、egress 措辞
32f4942 fix(f003): D011+D012 tasks 补 [TEST] 旅程验收组并修正任务图顺序
07e6649 fix(f003): D021 vendor 卫生补冻结上游基线，使逐行比对可复现
da4df56 fix(f003): D019 CLI 可构造完整 GenerationRequest + 默认值随运行留痕
60a51e8 fix(f003): D017+D018 AC 子句覆盖与可复现性 config digest/确定性契约
10866c4 fix(f003): D010 协同池持久化为可执行 FactorDef，AlphaPoolDef 降为内部视图
f12dfba fix(f003): D009 目标对齐补成本后收益预筛（PRD FR2.3，不越 ADR-0003）
0651afe fix(f003): D007 egress 断言收敛为进程级护栏并如实声明非内核隔离
b2414bb fix(f003): D004 纳入 ADR-0001 两条 M2 冒烟义务并显式占位下游漏斗级
4d5bdba fix(f003): D003 2 日 time-box 只裁 L0 锁定/L1 降级，L2 按 ADR-0001 连续 2 周触发
cb132c5 fix(f003): D002+D008 终态 run.j
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:06Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls -la docs/reviews/ && echo \"===F007===\" && find docs/features -ipath '*f007*' -o -ipath '*F007*' | sort"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls docs/features/0.2/ && echo \"===\" && cat .gitignore | head -40"})`


> [reasoning] The docs/reviews dir exists. Let me look at it. f007 is under features/0.2 presumably. Let me find.

  <details><summary>tool output</summary>

  ```text
total 220
drwxr-xr-x 2 georg georg   4096 Sep 16 23:41 .
drwxr-xr-x 7 georg georg   4096 Sep 15 01:58 ..
-rw-r--r-- 1 georg georg  43064 Sep 17 00:16 CURRENT-doc-F007.md
-rw-r--r-- 1 georg georg  35300 Sep 16 22:26 CURRENT-doc.md
-rw-r--r-- 1 georg georg  13434 Sep 17 00:07 FIX-log.md
-rw-r--r-- 1 georg georg 117606 Sep 16 02:11 RETROSPECTIVE.md
===F007===
docs/features/0.2/F007-evaluation-gates
docs/features/0.2/F007-evaluation-gates/design.md
docs/features/0.2/F007-evaluation-gates/spec.md
docs/features/0.2/F007-evaluation-gates/tasks.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
F002-data-bridge
F003-alphagen-vendor
F004-kronos-inference-runtime
F007-evaluation-gates
F008-universe-expansion
===
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
.venv/
venv/
dist/
build/
*.egg-info/
.idea/
.vscode/
.DS_Store

# 本机 AI 工具本地授权配置：含本机用户名路径与本地授权，不可移植
.claude/settings.local.json

# 编辑器本地历史
.history/

# 本机代理运行续接状态
.sisyphus/

# 本机 OpenCode 运行状态（含会话转录，严禁入库——密钥扫描门禁的原因之一）
.omo/

# 仿真/实验产生的数据与输出
data/raw/
data/processed/
results/
artifacts/
*.parquet
*.feather

# 本地-only 文档（保留在磁盘，不纳入 git）
docs/research/
docs/reviews/*
# ...例外：curated 摘要入库


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:22:10Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md"})`


> [reasoning] There's `docs/reviews/CURRENT-doc-F007.md` (43KB) — the round-1 review report for F007. And FIX-log.md. Let me read the review report and FIX-log.

Also let me read project CLAUDE.md for conventions.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: feature: F007
4: round: 1
5: date: 2026-09-16
6: prior_report: none
7: scope: full-scan
8: stop_condition_met: false
9: severity_counts: {critical: 0, high: 8, medium: 13, low: 4}
10: issues:
11:   - id: F007-D001
12:     title: "tasks 缺 design.md:16-18 强制的 [TEST] 旅程验收组"
13:     severity: high
14:     category: test-coverage
15:     root_cause: root-cause
16:     origin: process-gap
17:     pattern_tag: "test-group-missing"
18:     status: open
19:     tracked_task: ""
20:     fix_summary: ""
21:     regression_test: "proposed:tools/validate_spec_lifecycle.py::test_test_group_required"
22:     suggested_fix: "tasks 第 3 节增补 `### [TEST] 组：层 2 旅程验收轨`，从 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/FIX-log.md</path>
<type>file</type>
<content>
1: # FIX-log — 修复方声明（append-only）
2: 
3: > 本文件是修复方独占的发声通道（review-convergence skill §8）：只按轮追加，不修改/删除历史条目。
4: > 检视报告 `CURRENT-doc.md` 的写权归检视方，修复方对它的合法动作是**零写入**。
5: > 本文件与 `CURRENT-doc.md` 同为 gitignored 本地过程稿，闭环时由检视方一并删除。
6: 
7: ---
8: 
9: ## Round 1 · 2026-09-16 · report_type: doc-review
10: 
11: ### 基线与范围
12: 
13: - 基线：`main@a333394`（工作树干净），与本轮检视报告声明的基线一致。
14: - 被检对象：`docs/features/0.2/F003-alphagen-vendor/{spec,design,tasks}.md` 及相邻契约。
15: - 本轮处理范围：`CURRENT-doc.md` Round 1 全量扫描的全部 22 条 finding（high 14 / medium 7 / low 1）。
16: - 说明：F003 仍为 `status: draft`（无实现代码），本轮为**文档修复**；证据类型按 skill §3「文档检视靠文档被改 + 链接/格式检查通过」执行。
17: 
18: ### findings
19: 
20: 本轮处理 `F003-D001` … `F003-D022`，共 22 条，全部 `fixed`，无 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:13Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git rev-parse --short HEAD && git status --porcelain && echo \"---branch---\" && git branch --show-current && echo \"---ahead---\" && git rev-list --count origin/main..HEAD 2>/dev/null"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`


> [reasoning] Now I understand the setup. This is F007 doc-review round 1 with 25 findings. As the fixer, I need to:

1. Read F007 spec.md, design.md, tasks.md
2. Read the upstream references (PRD, SOP, ADR-0003, F003 spec, F004 spec, F008 spec/design/tasks, features/README)
3. Fix all 25 findings
4. Add regression tests / gate checks (the prior F003 round created `tools/check_doc_consistency.py` with TEXT_CHECKS + `tools/check_task_dag.py` + mutation tests)
5. Write FIX-log.md Round 2 (F007)
6. Run full gate

This is a big task. Let me first check baseline and read the docs. Note: git status was clean (no output from `git status --short`). HEAD is d659db7.

Wait, the review says baseline is d659db7. Let me verify HEAD and check whether F007 files were modified.

Let me read the F007 three files and the tools.

Let me plan carefully:
- This is a documentation fix task, not code. But it requires careful cross-doc contract alignment.
- The existing infrastructure: `tools/check_doc_consistency.py` with TEXT_CHECKS, `tools/check_task_dag.py`, mutation tests in `tests/unit/test_check_doc_consistency.py`.

Let me read all the relevant files. Start with F007 spec/design/tasks.

I should be efficient with context. Let me read them.

Actually, given the volume (25 findings, 3 F007 docs, ~10 upstream docs, 2 tools + tests), this is a large task. I'll consider delegating. But the fix quality depends on deep understanding across docs. Let me do the analysis myself first (reading), then possibly delegate parallel workstreams.

Hmm. The guidance says delegate. But doc fixes needing global consistency across 25 findings are risky to parallelize (conflicting edits). I'll do it myself with careful sequencing, possibly using subagents for verification (momus/oracle) and for gate/test writing.

Actually let me reconsider: the workloads:
- Workstream A: F007 spec.md fixes (D003, D004, D005, D006, D010, D011, D014, D017, D021, D022, D024...)
- Workstream B: F007 design.md fixes
- Workstream C: F007 tasks.md fixes
- Workstream D: tools/check_doc_consistency.py TEXT_CHECKS + tests

These all touch different files but need consistent vocabulary. Parallel agents would conflict on decisions. I think a single coherent author (me) is better for spec/design/tasks, then delegate the gate tooling to a subagent once the doc text is frozen.

Let me read the files now. First, all three F007 docs.
Baseline check + reading F007 三件套.

  <details><summary>tool output</summary>

  ```text
d659db7
---branch---
main
---ahead---
23


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

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
7: related_features: [F002, F003, F004]
8: topics: [evaluation, validation, evidence, experiments]
9: doc_kind: spec
10: created: 2026-09-13
11: updated: 2026-09-13
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
22: - **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级数据源，只有 `statu
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:21Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md"})`


> [reasoning] Now read design.md and tasks.md.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F004]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: design
8: created: 2026-09-13
9: updated: 2026-09-13
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
17: > 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
18: > 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。
19: 
20: ## 0. 输入与约束
21: 
22: - **行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003
23: - **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
24: - **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-000
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F004]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: tasks
8: created: 2026-09-13
9: updated: 2026-09-13
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`。
19: - 技术方案与边界：`design.md`。
20: - 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。
21: - canonical writer、留出访问、统计失败语义与 artifact 发布属于高风险路径，必须变异验证。
22: 
23: ## 1. 前置条件
24: 
25: - [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot builder/read
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:24Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_task_dag.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md"})`


> [reasoning] Now I have a good picture of F007 三件套. I need to read the upstream references for the cross-doc findings:
- PRD FR3.6/FR3.7 (lines 179-186), FR3 lines
- SOP lines 22-24, 64-75
- ADR-0003 lines 22-24, 42-56, 63-71, 82
- ADR-0007 lines 72-74
- ADR-0005 lines 40-52
- F003 spec lines 251-258, 328-330
- F004 spec lines 32, 71-72
- F008 spec lines 7, 243-244, 313, 326; F008 design line 100; F008 tasks line 90
- features/README line 103
- tools/check_doc_consistency.py, tools/check_task_dag.py, tests

Let me read these in parallel. That's a lot of reading. Let me do it.

Also line 103 of features/README - the design/tasks responsibility boundary. I read the README above; line 103 probably "design 只描述结构、契约、状态、失败和技术取舍，不写逐步编码任务。" Yes.

Let me read the tool files first (most important for the gate part), and the upstream docs.

Let me batch: 
1. tools/check_doc_consistency.py
2. tools/check_task_dag.py
3. ADR-0003
4. F008 spec
5. F003 spec (the relevant parts - it's large, maybe read all)
6. F004 spec
7. PRD relevant part

Let me use grep/read selectively but read whole files where needed. Since ADRs are small, read fully. F003/F004/F008 specs large — read specific ranges.

Let me do it.

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
<path>/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md</path>
<type>file</type>
<content>
1: # ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：quant-crypto 仓库 Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
7:   PRD G4 / FR3
8: 
9: ## 背景
10: 
11: quant-crypto 的最终 90 天留出门连续拦下全部候选（低频 Ridge/HGB、regime 增强、成本感知、
12: 衍生品 basis），看起来是"失败"，实际是验证协议在正确工作——它拦下的是会亏钱的东西。
13: 真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
14: 判定统计上不可信；regime filter 方向正确但 27 笔欠功效）。
15: 
16: 该门禁的价值来自它**从不放水**。任何"先上盘再观察"的妥协都会摧毁整个系统的可信度。
17: 
18: ## 决策
19: 
20: 1. **证据门不降级**：FactorDef 在选择期筛选后先构建并冻结 PortfolioDef，再由完整组合依次
21:    通过最终 90 天留出和永久隔离最终确认；不得先看留出再组装策略，效率提升也不得来自放宽门禁。
22: 2. **样本量门槛**：留出期 <30 笔输出 `UNDERPOWERED`（不判 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:29Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 150, "limit": 60})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md", "offset": 0, "limit": 30})`


> [reasoning] Now I need PRD lines 170-190, SOP lines 15-80, F008 spec relevant lines, F003 spec 240-340, F004 spec, ADR-0005 35-60, ADR-0007 60-90, and the tests/test_check_doc_consistency.py and test_check_task_dag.py to follow patterns.

Let me read in parallel.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
150: 
151: ### FR2 AI 因子工厂
152: 
153: - **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
154:   generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。
155: - **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
156:   生成器只产出 FactorDef/协同池定义，不拥有最终评测权。
157: - **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
158:   禁止只优化 RankIC。
159: - **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；前视、网络访问、隐式全样本统计和未支持的跨 pair
160:   算子直接拒绝，不得静默降级。
161: - **FR2.5 因子注册表**：保存定义、参数、数据依赖、来源、版本、评测摘要和生命周期；IC/OOS PnL
162:   高相关候选查重，`|ρ|>0.99` 拒绝，`0.90~0.99` 标记变体。
163: - **FR2.6 探索组合**：AlphaGen 协同池作为可部署 meta-factor 注册；名义产量、有效独立数、来源多样性
164:   与资源消耗并列记录，禁止只用公式数量汇报产能。
165: 
166: ### FR3 证据评测与验证
167: 
168: - **FR3.1 统一评测台**：输入 Facto
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/SOP.md</path>
<type>file</type>
<content>
1: ---
2: topics: [sop, workflow]
3: doc_kind: note
4: created: 2026-09-06
5: updated: 2026-09-07
6: ---
7: 
8: # 开发流程（AlphaMill）
9: 
10: 本文是项目的**原则入口与质量门**唯一真源：汇总「项目不可违反原则」的短摘要与各自
11: 唯一拥有者链接，规定开发纪律、验证流程、状态转换与复核协议。
12: 
13: ## 0. 项目不可违反原则（入口）
14: 
15: 以下原则是**阻断性**的：违反其中任何一条的规格/实现不得进入实现或收口阶段。规范
16: 正文在各自的唯一拥有者中，本文只给摘要与入口。**每条原则的规范正文只放一个唯一
17: 拥有者**，本文只写短摘要与链接，不重复 PRD、architecture、decisions 的完整定义。
18: 
19: | # | 原则 | 短摘要 | 规范正文唯一拥有者 |
20: |---|---|---|---|
21: | 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |
22: | 2 | 证据门不降级 | 候选按样本功效分级并经过留出与最终确认；效率提升不得来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |
23: | 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F008
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002, F003, F007]
8: topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
9: doc_kind: spec
10: created: 2026-09-14
11: updated: 2026-09-14
12: ---
13: 
14: # F008：宇宙扩容与 point-in-time 宇宙台账
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR1.5（数据质量与扩容、point-in-time 宇宙成员关系）、FR1.1（联机采集与质量标记）、FR1.4（pair/symbol 显式映射）、FR1.7（ResearchSnapshot 的 universe 摘要）；里程碑 M2
21: - **架构来源**：`docs/alphamill-architecture.md` §三（`data_bridge/` 与 `collector/` 分工）、§4.1.1（横截面只允许在同一 timestamp 的 point
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:33Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md", "limit": 150, "offset": 190})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 110, "offset": 240})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md"})`


> [reasoning] Now read F008 spec 190-260 and 300-338, F008 design around 100, F008 tasks around 90, F003 spec 240-340, F004 spec 20-80, ADR-0005 30-60, ADR-0007 60-90.

Let me batch reads.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md</path>
<type>file</type>
<content>
190: - THEN 按退避策略重试且不超过上限，绝不提高请求速率
191: 
192: ### Requirement: 新 pair 质量门（`FR-004`）
193: 
194: 系统应当对每个新 pair 执行完整性校验——缺失率（按该 pair 实际可得窗口计算）、时间边界闭合、重复主键、1m 基表与连续聚合按桶重算一致——全部通过才允许进入导出清单；任一项失败即隔离并记录原因码，不得静默放行或放宽阈值。
195: 
196: #### Scenario: 跨周期对不上
197: 
198: - GIVEN 某 pair 的连续聚合行数与 1m 基表按桶重算不一致
199: - WHEN 执行质量门
200: - THEN 判定失败，该 pair 不进导出清单
201: 
202: ### Requirement: point-in-time 宇宙成员台账（`FR-005`）
203: 
204: 系统应当维护只追加的宇宙成员台账，每条记录带生效区间与进出原因；系统应当提供 `universe_at(T)` 查询，返回 T 时刻的成员集合。历史区间一经发布不得修改。
205: 
206: #### Scenario: 历史时点还原
207: 
208: - GIVEN 某 pair 于 T1 进入宇宙、T2 退出
209: - WHEN 查询 T0(<T1)、T1.5、T3(>T2) 的宇宙成员
210: - THEN 该 pair 只出现在 T1.5 的结果中
211: 
212: #### Scenario: 台账不
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md</path>
<type>file</type>
<content>
240: - THEN 结果与训练期记录在容差内一致
241: 
242: ### 数据 / 实体需求
243: 
244: - **DR-001**：`GenerationRun` 应当持久化快照绑定（`research_snapshot_id`，或过渡期的显式元组：`schema_version`、`cutoff_time`、逐 dataset 成员映射 `{<dataset>: (data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)}`、`symbol_map_digest`、`universe_calendar_digest` 与不可变 artifact 的 `provenance` 引用——字段与身份语义与 ADR-0007 一致）、seed、生成器与引擎版本、配置摘要（canonical config artifact 与 `config_digest`）、device、hostname、宇宙规模（pair 数与 `symbol_map_digest`）、档位与逐级计数；**宇宙规模是候选质量结论的前提条件，必须随运行留痕**。
245: - **DR-002**：`FactorDef` 应当以规范化 JSON 内容寻址持久化，`factor_id = <generator>_<definition_digest[:12]>`（**不含 run 序号**；运行归属由 `run_id` 承载，跨 run 重跑同一表达式得到同一 `fa
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md</path>
<type>file</type>
<content>
1: # ADR-0007：研究快照绑定 —— 独立 DatasetVersion 的不可变组合
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted
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
16: 不是跨 dataset 的一致性边界；它既不固定 point-in-time universe/symbol map，也不证明各成员满足
17: 同一个信息截止时刻和评测窗口。另一方面，把所有 dataset 强绑成一个全湖版本会让单个低频
18: dataset 的延迟或失败阻塞全湖发布，反转 F002 已确立的独立失败域。
19:
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:37Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md", "limit": 50, "offset": 80})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md", "limit": 40, "offset": 80})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "limit": 100, "offset": 1})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0005-presentation-observability.md", "limit": 40, "offset": 30})`


> [reasoning] This is a lot of context. Now I need F008 design line 100, F008 tasks line 90, F004 spec 20-80, ADR-0005 30-60, and tests test_check_doc_consistency.py / test_check_task_dag.py.

Let me be efficient. I need:

For D003/D004: F008 design.md around line 100 (universe artifact paths) and tasks.md line 90.
For D017: F004 spec lines 32, 71-72.
For D018: ADR-0005 lines 40-52.
For D020: design §8 mapping table vs tasks test files.
For D005: PRD FR3.6 (read), SOP:22-24 (read), architecture — the no-lookahead three layers owner. Let me check architecture for 无前视.

Let me read those.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md</path>
<type>file</type>
<content>
80: | `ingested_at` | 采集时间，支撑 bitemporal 语义与"何时知道的"审计 |
81: 
82: 约束：区间不重叠（同一 pair 的 `valid_from` 严格递增）；**没有 UPDATE 路径**——退出用写 `valid_to` 的追加记录表达，历史行不可改写（数据库层用触发器或应用层单写封装，落地任务里择一并写明）。
83: 
84: **Migration**：一个前向迁移建表 + 索引 `(lake_pair, valid_from)`；无回滚数据（新表）。首次迁移后必须立即执行"现有 6 对补台账"（`reason=initial_seed`，`valid_from` 取各自实际数据起点），否则老 pair 在 PIT 查询里会凭空全程存在。
85: 
86: **`UniverseDef`（内容寻址 JSON）**：`universe_id` / `criteria` / `snapshot_at`（交易所数据快照时间）/ `candidates[]`（含逐候选筛选指标与排除者的排除原因）/ `frozen_at` / `frozen_by`。`universe_id = sha256(canonical_json(criteria + snapshot_at + candidates))`——同口径同快照必然同 id。
87: 
88: `criteria` 字段（Q-001 裁决值）：
89: 
90: | 字段 | 值 | 说明 |
91: |---|---|---|
9
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md</path>
<type>file</type>
<content>
80: - `T015 -> T017 -> T022`：质量门是导出清单的唯一准入通道。
81: - `T020 -> T022`、`T021 -> T022`：每批回填完成后各跑一次质量门；批 2 不阻塞批 1 的准入。
82: - `T022 -> T023`：两批都过门后才做容量实测（实测对象是最终的 40 对）。
83: - `T003 [P]`：只产接口 fixture，与定义/台账实现无共享状态。
84: - 与 `F003` 的关系：**批 1 过门（T022 的第一次执行）即满足 `F003` T035 的 ≥30 对前提**，不必等批 2 或 T023；在此之前 F003 的一切工作不被阻塞。
85: 
86: ## 5. 明确后移
87: 
88: - 多交易所聚合与跨所 symbol 归一 → 后续 Feature：当前数据路线只有 Binance（F001 裁决）。
89: - 实时上下架监听与自动扩缩容 → 后续 Feature：M2 只需批处理周期发现成员变化。
90: - calendar artifact（交易日历/停机窗口）→ `F007` 或后续 Feature：ADR-0007 把它与 universe 并列，但 crypto 24/7 下优先级低于宇宙台账。
91: - 扩容到 40 对以上（含 50 对方案）与分片导出优化 → 视 T024 的实测余量再决定：50 对的全量导出约 32min、NAS 约 73,500 个分区文件，噪声改善仅 11%，当前不做；台账支持增量加 pair，需要
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: status: done
6: gate_version: 1
7: related_features: [F001, F002]
8: topics: [kronos, inference, deployment]
9: doc_kind: spec
10: created: 2026-09-12
11: updated: 2026-09-16
12: ---
13: 
14: # F004：Kronos 真实推理运行时（编排内可复现）
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身
21: - **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）、§7.1（机器边界）
22: - **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）
2
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0005-presentation-observability.md</path>
<type>file</type>
<content>
30: | 层 | 内容 | 变更纪律 |
31: |---|---|---|
32: | 真相源 | 研究=不可变报告文件 + manifest；运营=TimescaleDB 原始表；执行=Freqtrade（自身库 + REST） | 不可变或版本化；任何展示数字必须可追溯至此 |
33: | 投影 | 版本化 SQL 视图（TSDB，入 `db/migrations/`）+ 统一只读 API | 必须可从真相源确定性重放/重建，禁止手工改投影 |
34: | 展示 | Grafana 板、自建 SPA、FreqUI | 薄渲染器，可随时替换，不承载口径 |
35: 
36: 2. **口径唯一居所是 SQL 视图**：指标口径一律定义为视图并入 `db/migrations/`；Grafana
37:    面板只允许 `SELECT ... FROM 视图 + 过滤参数`，禁止承载口径；自建页面消费同一批视图。
38:    任何新旧呈现并存期，**对数 diff=0 是迁移验收标准**（旧看板即新页面的 golden master）。
39: 
40: 3. **统一只读 API 是永久人类界面后端**：`src/alphamill/api/`，端点按领域对象组织
41:    （hypotheses / factors / portfolios / deployments / manifests / runs / ops-metrics /
42:    trades）；执行明细**代理 Freqtrade REST**（
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:22:42Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -rn \"无前视\\|重放\\|signal cache\\|信号缓存\" docs/alphamill-architecture.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls tests/unit/ && echo \"---\" && sed -n '1,80p' tests/unit/test_check_doc_consistency.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"TEST\\|test_group\" tools/validate_spec_lifecycle.py | head -40"})`


> [reasoning] Now I have decent context. Let me check the F004 spec lines about signals, and the architecture for no-lookahead ownership, plus F002 spec for signals_log / placeholder. Actually for D017 I mainly need F004 spec:32,71-72 (read above: line 32 says signals_log content all `source=placeholder`; lines 71-72: consumer routing not in scope, signals_log content auto-upgrade not in scope).

Let me also check the tests dir for test_check_doc_consistency.py.

And check `tools/validate_spec_lifecycle.py` for the [TEST] group requirement.

Let me also grep architecture for 无前视 layers to know where to point ownership (D005).

Let me batch.

  <details><summary>tool output</summary>

  ```text
153:    R --> S[版本化信号缓存]
249:- `DeploymentRun` 固定引用 portfolio、信号缓存和审批版本；
273:`factor_id` 与权重放在 `params`/`meta`，`compute` 由成员 `FactorDef` 与权重重算，加载即可执行；
347:  `research_snapshot_id`、`cost_model_version` 并列，保证曲线可从真相源确定性重放；
377:### 4.3 信号缓存契约（与 kronos_cache 兼容）
385:三条补充规则（与集成文档 §3.2 无前视对齐规则配套）：
391:3. **审计覆盖 join 步骤**：无前视审计的范围显式包含 merge/join 步骤本身，不只因子计算——逐 K 线重放时对每个决策 bar 校验（信号时间戳 ≤ t 收盘）∧（陈旧度 ≤ 界），两项任一不满足即审计失败。
438:重放，current 文件或调用方原路径不充当证据。
481:| `independent_cross_backtest.py`（独立重放器） | **迁入**为无前视审计器（FR3.6） |
493:主链路。不可用时，第二意见退化为本仓独立重放器或手工第二实现，复盘退化为其他只读 Agent


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
__pycache__
test_apply_migrations.py
test_backup_nas_contract.py
test_check_dep_pins.py
test_check_doc_consistency.py
test_check_doc_links.py
test_check_secrets.py
test_check_task_dag.py
test_doc_gate_command.py
test_f001_backfill_report.py
test_f001_backfill_window_source.py
test_f001_compose_contract.py
test_f001_credentials.py
test_f001_exchange_defaults.py
test_f001_line_limit_exemptions.py
test_f001_supervisor_contract.py
test_f002_cli_contract.py
test_f002_digest.py
test_f002_exporter.py
test_f002_manifest.py
test_f002_partitions.py
test_f002_paths.py
test_f002_reader_contract.py
test_f002_reconcile.py
test_f002_registry.py
test_f002_symbol_map.py
test_f002_timer_contract.py
test_f004_compose_profile_contract.py
test_f004_kronos_runtime_contract.py
test_historical_backfill_review_fix
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
10:    必须含 `### [TEST] 组`（层 2 旅程验收轨）
60:# [TEST] 组是「进入代码开发前」的硬性要求：不含 done（历史 Feature 豁免，纳入会
62:TEST_GROUP_STATUSES = {"ready-for-development", "in-progress", "review"}
63:TEST_GROUP_RE = re.compile(r"^###\s+\[TEST\]", re.M)
210:    if spec_fm.get("status") in TEST_GROUP_STATUSES and not TEST_GROUP_RE.search(tasks_clean):
211:        tag("tasks.md 缺少必需的 [TEST] 组（层 2 旅程验收轨）")


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:22:48Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "limit": 60, "offset": 375})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "limit": 40, "offset": 470})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -rn \"placeholder\\|signals_log\" docs/features/0.2/F002-data-bridge/*.md | head -20 && echo \"===CLAUDE===\" && sed -n '1,60p' CLAUDE.md"})`


> [reasoning] Now I understand the gate infrastructure. Important: `TEST_GROUP_STATUSES = {"ready-for-development", "in-progress", "review"}` — F007 is `draft`, so D001's `[TEST]` group is NOT enforced yet by the gate. But the finding is high severity. The finding says design.md:16-18 requires it before dev, and SDD Flow T3 will reject. So fixing means adding the [TEST] group to tasks.md. That's a documentation fix that also aligns with the gate (which will enforce when status becomes ready-for-development).

Now, D007/D008 task DAG: check_task_dag only enforces for non-draft. F007 is draft, so gate passes. But findings still need fixing (add edges).

Let me now plan the fix work. There are 25 findings. Let me enumerate the fixes needed:

**D001** (High, test-coverage): tasks.md add `### [TEST] 组：层 2 旅程验收轨` in §3, deriving ≥1 executable assertion per journey step of US-001/002/003.

**D002** (High, correctness): design.md/tasks.md frontmatter related_features add F003; design §2/§4 add ingestion points for `generation.*` events, operator capability registry, collaborative pool; tasks add implementation/contract tasks.

**D003** (High): spec.md:7 related_features + §0 add F008; IR-002 explicitly reference F008 universe artifact digest and `universe_at(T)`; design/tasks frontmatter sync.

**D004** (High): split universe and calendar artifacts. universe consumed per F008 IR-002 (CSV digest + universe_at(T)); calendar owner declared (F008 explicitly defers calendar artifact to F007 per F008 tasks §5:90 "calendar artifact → F007 或后续 Feature"). So F007 should own calendar artifact. Fix design.md:145,157-159,193 and spec IR-002/DR-001 to have two separate artifacts/refs, CLI separate `--universe` and `--calendar` refs.

**D005** (High): three-layer no-lookahead: F007 must declare ownership for AST purity, independent bar-by-bar replay, signal-cache timestamp alignment. PRD FR3.6, SOP:23. Need to explicitly assign executor/evidence/fail-closed gate for each layer, or defer with owner + blocking point.

**D006** (High): sample size three tiers: <30 UNDERPOWERED; 30~69 temporary PASS with reduced paper only; ≥69 trustworthy. Add to spec FR-005 and design §3.3/§7, AC-004 three-tier assertions, tasks T010 verify three-tier cases.

**D007** (Medium): tasks §4 add `T009 -> T012`, `T012 -> T013`.

**D008** (Medium): tasks §4 add `T007 -> T010,T011`, `T012 -> T016`, `T014 -> T016`.

Note: check_task_dag forbids backward edges (src < dst required) and requires highest task to have incoming edge. T024 has incoming? Currently §4 doesn't mention T024. Wait the gate passed on the repo... because F007 is draft (not enforced). For F003 it's enforced and passes.

If I add edges for F007, when status later becomes ready-for-development the DAG gate will run. Careful: edges must be forward only. T009->T012 ✓, T012->T013 ✓, T007->T010 ✓, T007->T011 ✓, T012->T016 ✓, T014->T016 ✓. Also highest task T024 must have an incoming edge — I should add something like `T016,T017,T022,T023 -> T024` or similar. Hmm, but careful: the gate requires the last task (max id = T024) to have at least one incoming edge. Let me check whether the current tasks has any edge to T024 — no. Since F007 is draft, it's not enforced. But to be safe and consistent (and because D001 makes the doc dev-ready), I should add incoming edges to T024. Actually if I add edges, the gate will be enforced only at ready-for-development. Being forward-thinking, add proper edges including to T024.

Wait — careful about `[P]` rule: "`[P]` 任务不得同时声明前置边". T005 is [P]. So no edge may have dst=T005. Fine.

Also the edge format: `EDGE_SEGMENT_RE = r"`([^`]*->[^`]*)`"` — backticked segments containing `->`. Current format: `` `T001,T002,T003 -> T004~T017` `` — the `~` range is not T\d{3} so it's skipped for those. Let me check parse: hops = ["T001,T002,T003", "T004~T017"]. left split by "/" → ["T001,T002,T003"] — not fullmatch T\d{3}, so skipped. So that edge produces no edges. OK.

I'll write new edges in explicit comma-separated form that the parser handles: the parser splits hops by "->" and each hop by "/" then requires fullmatch T\d{3}. So "T009 -> T012" works. For multiple: `T012/T014 -> T016` expands cartesian. And `T007 -> T010/T011` expands cartesian.

So I'll add lines like:
- `` - `T009 -> T012`：cohort 级校正依赖成员级估计器。 ``
- `` - `T012 -> T013`：finalize CLI 依赖登记实现。 ``
- `` - `T007 -> T010/T011`：阶段模型是 rolling split 与事件/发布的输入。 ``
- `` - `T012/T014 -> T016`：全链控制需 registry 与 synthesis。 ``
- `` - `T016/T017/T022/T023 -> T024`：收口回写。 ``

**D009** (High): T022 must be a real-env task distinct from T016: bind immutable crypto snapshot ref + digest, record hostname, use `ALPHAMILL_INTEGRATION=1` independent command; sync design §8 and spec:275.

**D010** (High): holdout budget ledger entity + DR, append-only, fields candidate/week/verdict/time; AC-001 "ledger zero rows" assertion; preview overreach negative case.

**D011** (Medium): verdict vocabulary conflict: freeze two-layer enum: stage status (PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE) and promotion/cost verdict (promising/dead). spec FR-003/FR-005 and design §3.3 share same glossary; AC-003/AC-004 consistent.

**D012** (Medium): SC-002 concurrency/fault injection task+test.

**D013** (Medium): AC-003 denominator multi-member batch fixture.

**D014** (Medium): NFR-004 preview approximation covered in design §3.3 report schema + tasks + AC.

**D015** (Medium): mutation targets vs AC labels aligned; T017 covers more than T021 declares; add kill artifact/tool pin.

**D016** (Medium): statistical second-implementation spot check decision no task carrier → add task or explicitly defer with owner.

**D017** (Medium): F004 Kronos signals → FactorDef adaptation/source contract.

**D018** (Low): F005 file reader inside API or not — clarify design §6.

**D019** (Medium): final confirmation window stats excluded from Agent-readable report/manifest/synthesis, fail-closed; AC assertion.

**D020** (Medium): design §8 test mapping missing several test files used by tasks.

**D021** (Medium): five-stage IDs and failure dimensions frozen; design §3.3/§4 schema; spec FR-003 reference; T014 implement.

**D022** (Medium): NFR-005 path portability + UX-001 CLI first screen traceability → AC refs + tasks verify.

**D023** (Low, quality): design.md:16-18 embedded tasks action instructions → move to tasks.md.

**D024** (Low): state vocabulary + canonical=bench mapping/event registration alignment; `evaluation.registered` into spec TR-003.

**D025** (Low): property test strategy lacking explicit execution task/tool-constraints.

Plus regression tests: each finding needs a check in tools/check_doc_consistency.py (TEXT_CHECKS or custom), and mutation tests must be added to test_check_doc_consistency.py. That's the "regression_test" evidence. The review's `regression_test` field says "proposed:tools/check_doc_consistency.py::test_xxx".

Note: the existing test file's `_materialize` uses `ALL_DOC_FILES = {SPEC, DESIGN, TASKS, F007_SPEC}` — if I add checks referencing F008/F004 spec files, I must update ALL_DOC_FILES to include them.

This is a substantial amount of work: ~25 findings, each needing doc changes + a gate check + mutation test.

Given the scale, and per the skill: "一个 finding 一个 commit" (one finding per commit). The F003 round did 22 findings with individual commits. I should follow the same discipline. That's 25 commits... That's heavy but it's the protocol. Hmm, but the F003 FIX-log shows commits per finding. The skill §6 says "一个 finding 一个 commit：本地提交,保 bisect/revert 能力".

I'm on branch main with 23 commits ahead. Committing 25 more commits locally is what the protocol demands. Should I commit? The skill says local commits with bisect/revert capability, then round-end full gate + push once (by reviewer). Actually §6: "每个修复先跑它的目标回归测试（秒级）再进下一个;全量门禁 + CI 每轮只在轮末跑一次,push 一次". And §8 闭环执行序列 says the reviewer pushes. But the fixer does local commits. F003 FIX-log says "未推送 / 未取 CI" — fixer made local commits, didn't push.

Hmm, but "Only commit, amend, push, or create PRs when explicitly requested" from my system prompt. The user asked to fix per the skill requirements. The skill requires one-finding-one-commit. The prior round (F003) did commits. So committing is implied by "按照skill要求". I think yes — the skill explicitly requires per-finding commits as the fixer's deliverable (FIX-log references commit hashes). Without commits, FIX-log can't have the commit column.

Hmm, but that's a big decision. Let me consider: the user says "请站在修复者的视角按照skill要求对检视问题进行审视和修复" — act as fixer per skill requirements. The skill's fixer deliverables include per-finding commits with hashes. So I should commit locally (not push).

OK. Also: "审视" = review/scrutinize the findings. That includes the accept/reject decision (第4条), and possibly rejecting some findings if evidence doesn't hold. As fixer, I should check each finding's validity. Some may be invalid... Let me assess as I go.

Let me now think about which findings might legitimately be rejected. Looking at them:

- D005 (three-layer no-lookahead): The finding says F007 only covers methodology guard layer; replay and signal-cache alignment not explicitly undertaken. Per PRD FR3.6 and SOP principle 3 (owner: alphamill-integration.md), the three layers: AST purity (factor definition layer), independent bar-by-bar replay audit (strategy layer), signal cache timestamp alignment (data layer). F007 is the evaluation platform. Is F007 obliged to own all three? Architecture line 481: `independent_cross_backtest.py` (独立重放器) → 迁入 as 无前视审计器 (FR3.6). Where does that land? Let me check architecture §... The finding's suggested fix: "F007 spec/design 明确三层归属：为 AST 纯度、独立逐 K 线重放与信号缓存时间戳对齐分别声明执行者、证据与晋级前 fail-closed 门；现有 FR-002 方法论守卫仅作为补充层。若后移 F006，需写明晋级前阻断点与 owner". So a valid fix is: declare ownership split with owner + blocking point. Not necessarily implement all in F007. Hmm — but is it in F007's scope? F007 is "统一评测台与证据门禁" scoped at M1 for factor evidence; the strategy-layer replay and signal-cache join alignment belong to F006/M3 (offline→decision parity). F007's spec §3 范围外 says "离线到决策时 parity、run_record、kill-switch 与启动对账 → F006/M3". So the finding can be satisfied by an explicit three-layer ownership table declaring which layer is F007's (AST purity via FR-002 methodology gate... actually AST purity is FR2.4 of F003/generator) and which are F006's, with the promotion blocking point. That's an acceptable fix without scope creep. I'll accept and fix by declaring explicit ownership + blocking point in spec/design (and it must not contradict 范围外).

- D017 (F004→F007 FactorDef adaptation): F004 is `done`; its spec says signals go into `signals_log` dataset with `source=placeholder` for F002 exports; F004 provides real signal source but consumer routing is out of scope. The finding wants F007 to define how Kronos signals adapt to an evaluatable FactorDef, provenance, and placeholder rules. That's a real gap: F007 spec §0 says upstream contract includes "F004/Kronos 与人工因子产出的 FactorDef". So the spec claims F004 provides FactorDef. Does it? F004 provides a signal service. The adapter Kronos signal → FactorDef is... hmm. F007 §3 范围内 includes "funding carry、BTC/ETH 截面动量正控制与白噪声/故意泄漏负控制". The Kronos signal factor would be a FactorDef whose compute reads signals_log from F002 dataset. So the placeholder boundary: F002 signals_log may have source=placeholder → is that allowed to be evaluated? Per ADR-0003 non-degradation and F004's completion, real source required for canonical. So F007 should specify: canonical requires real source (or is it F002's duty?). This is a legitimate finding. Accept and fix: add a contract section for signal-derived FactorDef / provenance, and placeholder policy (preview may allow placeholder with explicit labeling; canonical must reject placeholder / require source=kronos or declare it explicitly). Careful about not overstepping F004 (done) and F002. Let me check F002 spec for signals_log source field.

- D018 (low): clarify F005 front-end can only read via API; file reader may be internal adapter. Accept, fix design §6.

- D024 (low): state vocabulary + canonical=bench mapping + `evaluation.registered` into TR-003. Accept.

- D023 (low): design.md:16-18 dev precondition — is it "行动指令"? The `docs/features/README.md:103` rule: "design 只描述结构、契约、状态、失败和技术取舍，不写逐步编码任务". design.md:16-18 says "进入代码开发前，tasks.md 必须补齐 [TEST] 组——从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。开工门禁（SDD Flow T3）会拒绝缺失该组的流转。" Is that a step-by-step coding task? It's a precondition note, arguably a process constraint not a coding task. Hmm. The finding is Low quality-channel. The suggested fix: move to tasks.md as [TEST] group description/§0 rule, design keeps only the constraint or one line pointing to tasks. I think it's reasonable to partially accept: move the action instruction to tasks.md §0/§3 and leave design with a constraint line. Simpler: accept fully. I'll accept — it's cheap, keeps channels clean.

Now let me also check: does the review have any factually wrong findings? Let me verify a few claims:

D007: "T012 finalize 计算 BH-FDR/DSR 但依赖图缺 T009→T012；T013 缺 T012→T013". tasks T012 verify is `tests/integration/test_f007_canonical_registry.py`, T009 is statistics. §4 has `T008,T009,T010 -> T011,T016,T017` and `T011,T012 -> T014,T015`. Indeed no T009->T012. True.

D008: T016 needs registry/synthesis; §4 has T011,T012 -> T014,T015 but no T012->T016. True.

D020: design §8 table lists files: execution_tiers, methodology_gate, required_statistics, cost_and_stability, atomic_publish, research_snapshot/identity, synthesis, cli. tasks uses additionally: test_f007_upstream_contracts.py (T001), test_f007_canonical_registry.py (T012), test_f007_artifact_schemas.py (T015), test_f007_controls.py (T016), test_f007_gate_mutations.py (T017). True, those 5 are missing.

D021: "五阶段 ID 与失败维度未冻结，tasks 只说「三维失败汇总」无 schema". spec FR-003 names stages in Chinese: 信号质量、组合转换、成本/容量、时序稳定、执行实现. design §2 mentions stage "signal_quality". tasks T014 says "五阶段/三维失败汇总". So stage IDs aren't frozen as an enum. True.

D022: NFR-005 and UX-001 have no AC reference. Check AC list: AC-001..AC-008; does any reference NFR-005 or UX-001? AC-008 references IR-001, IR-002, IR-003. None references UX-001 or NFR-005. True.

D019: 最终确认窗 — spec NFR-003 says "Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力". Hmm, "留出读取" covers holdout. But the 最终确认窗 (final confirmation window) is separate from holdout per ADR-0003 §留出期使用预算 3. NFR-003 doesn't explicitly exclude the final confirmation window from Agent-readable report/manifest/synthesis. ADR-0003 复盘循环窥探防护 3: "agent 的输入（manifest + 报告）不得包含最终确认窗上的任何统计量". F007 produces the report/manifest. So F007 should assert it. True finding.

D013: AC-003 "拒绝者仍进入试验分母" — multi-member batch case. tasks T016 runs golden with controls; design §8 AC-003 maps to required_statistics. Need multi-member cohort fixture. True.

D015: T017 covers FR-001,FR-002,NFR-003 with mutation on future-fill, embargo, guard registry, preview writer, exception swallowing, publish integrity. T021 declares AC-002, AC-005. So coverage mismatch: T017 covers more (FR-001/preview writer → AC-001, publish → AC-005, exception swallowing → AC-003?). True.

D014: NFR-004 preview approximation — spec says preview may sample/window but must explicitly annotate approximation. design report.json fields don't include approximation. True.

D016: PRD FR3.7 second implementation review; spec §7 决策与风险 row "统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查"; design §9 "第二实现只做对照". No task. True.

D002: F003 spec says F007 consumes `generation.*` events, operator registry, collaborative pool; F007 spec:22 does declare. design/tasks frontmatter related_features = [F002, F004] — missing F003. True.

D003: F008 related_features includes F007; F008 spec IR-003 says artifact consumed by F007. F007 spec related_features = [F002,F003,F004] missing F008. True.

D004: design:145 CLI `--universe-calendar <path>` single JSON; design:157-159 `universe_calendars/<digest>.json`. F008 publishes universe as CSV artifact `lake/_metadata/universes/<digest>.csv` with `universe_at(T)`; and F008 tasks §5:90 defers calendar artifact to F007. ADR-0007:72-74 says symbol map from F002, universe/calendar JSON provided by caller & saved by experiment_store. Hmm — ADR-0007 says "调用方提供的 universe/calendar JSON" singular path. So there's a tension. The finding says split into two artifacts: universe per F008 (CSV digest + universe_at(T)), calendar owner F007 or separate. Given F008 now owns PIT universe as CSV, and calendar is deferred to F007, F007 should: consume universe artifact by digest (CSV, F008-IR-002 `universe_at(T)`) and own the calendar artifact (JSON, canonicalize & content-address) — updating ADR-0007's expectation accordingly? Careful: ADR-0007 is Accepted, owns universe_calendar_digest in ResearchSnapshot. Modifying an ADR is heavy. But F007 can declare: `universe_calendar_digest` = digest of a manifest that references both the F008 universe artifact digest and the F007 calendar artifact digest. Hmm, that's a clean way: keep ADR-0007's single field but define it as the digest of a combined canonical binding record. Actually simpler and honest: declare two sub-digests consumed within ResearchSnapshot: `universe_digest` (from F008, CSV artifact) and `calendar_digest` (F007-owned), and `universe_calendar_digest` = sha256(canonical(universe_digest, calendar_digest)) so ADR-0007's single field remains valid and identity semantics unchanged. That resolves the conflict without editing the ADR. And CLI splits into `--universe <digest|ref>` and `--calendar <path>`.

Hmm, but is that over-engineering? The finding says "拆分两个 artifact 契约：universe 按 F008 IR-002 的 digest + universe_at(T)（CSV）消费，calendar 明确 owner 与 schema（F007 或另立并登记）；CLI 与 builder 分别接收两个 ref；DR-001/IR-002 与 design.md:157-159 的 universe_calendars/*.json 命名同步". So yes: two refs, and the naming/PIT query fixed. My composite-digest approach satisfies "DR-001/IR-002 同步" and keeps ADR-0007 valid. I'll document it explicitly.

D006: sample size three tiers. True — spec §3 边界场景 says "指标样本不足：输出 UNDERPOWERED" and FR-005 says cost-negative → dead; sample-size裁决 not three-tier. design:124-126 stage states include UNDERPOWERED. Need three-tier with promotion verdict. Note: for factor preview, the "69 trades" metric is about trade counts; F007 evaluates factors — the tier should apply to the trade-count/effective sample. OK.

D010: holdout budget ledger. spec:40 "preview 快速诊断但不能污染 canonical cohort、留出预算和 official population"; spec:55 非目标... AC-001 says "正式台账与留出预算零变化". But no ledger entity. ADR-0003 §留出期使用预算 defines the ledger (append-only, candidate ID, date, verdict). F007 owns? ADR-0003 says "只有 execution_tier=canonical 的预注册运行可以写上述预算台账". The ledger is defined in ADR-0003 but F007 must implement/own it since F007 owns holdout access. Hmm — is this "产品缺陷 vs 上游任务未执行"? The ledger entity is F007's to implement (it's the gate owner). Accept; add DR-005 (holdout budget ledger) + design schema/dir + tasks + AC-001 assertion.

Wait, careful: adding a new DR to spec requires AC reference? DR-005 must be referenced by an AC. AC-001 references FR-001, DR-004, NFR-003 — I'd add DR-005 to AC-001.

D011: verdict vocabulary. spec FR-005 scenario: `cost_verdict=cost_negative` 且最终 verdict 为 `dead`. spec §4 FR-003 says "verdict 不得为 PASS/promising". design §3.3: stage states PASS|FAIL|UNDERPOWERED|INCOMPLETE|NOT_APPLICABLE; cohort verdict has `promotion_verdict`. Need frozen glossary. True.

D012: SC-002 concurrency/fault injection. True.

D005 details: need architecture reference/ownership. Let me check architecture for where 逐 K 线重放 lands and whether F007 owns. Let me grep architecture around 470-500 for migration table.

Let me read architecture lines 370-500 to understand signal cache and audit ownership.

Also need F002 spec for signals_log + `source` field and reader contract. And CLAUDE.md for active features.

Let me read a few more things, then start editing.

Actually, let me be pragmatic about context. I have a lot. Let me read architecture 370-500, and grep F002 spec for placeholder/signals_log.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
375: 新 ID，并从头消耗门禁预算。
376: 
377: ### 4.3 信号缓存契约（与 kronos_cache 兼容）
378: 
379: ```text
380: 路径：signal_cache/<portfolio_or_factor_id>/<research_snapshot_id>/<code_version+params_hash>/<pair>/<YYYY-MM-DD>.feather
381: 列：  timestamp(信号确认时刻, UTC), pair, signal_value, confidence*, stale
382: 约束：t 行只含 ≤t 信息；留出门审计按行校验时间戳对齐
383: ```
384: 
385: 三条补充规则（与集成文档 §3.2 无前视对齐规则配套）：
386: 
387: 1. **缓存键带版本维度**：缓存键 = (portfolio_or_factor_id, research_snapshot_id, code_version,
388:    params_hash, pair)，不是仅 timestamp+pair。任一输入 dataset 修订或代码/参数变化后写新版本目录，旧版本
389:    只读不覆盖。
390: 2. **混合频率陈旧策略**（4h 因子进 1h 决策）：merge_asof（backward）对齐后允许前向填充，但仅在最大陈旧度界内——因子值有效至下一个因子 K 线收盘，硬过期 = N 根决策 K 线（默认 N = 1 个因子周期，4h→1h 即 N=4）。越过
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
470: 
471: ---
472: 
473: ## 五、quant-crypto 资产清算迁移表
474: 
475: > 逐项操作步骤与验收标准见 [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md)。
476: 
477: | quant-crypto 资产 | AlphaMill 处置 |
478: |---|---|
479: | TimescaleDB 湖 + 质量标记 | **迁入本仓**，新增导出桥（FR1） |
480: | `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` | **泛化为统一评测台**（FR3.1），Kronos 信号作为第一批入库因子 |
481: | `independent_cross_backtest.py`（独立重放器） | **迁入**为无前视审计器（FR3.6） |
482: | `validate_low_frequency_*_holdout.py` 门禁脚本 | **参数化迁移**到 `src/alphamill/validation/`，落实 FR3.4/FR3.5 |
483: | 风控三件套 + Freqtrade dry-run | **迁入**（FR5），策略模板化 |
484: | Grafana / Prometheus / 日报 | **迁入**；实验谱系与评测浏览归自建研究控制台（ADR-0005），Grafana 逐步退守平台观测与
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
docs/features/0.2/F002-data-bridge/design.md:26:三步走:① 导出器核心——ohlcv_1m 一个 dataset 端到端(查询 → 分区 Parquet → manifest/value digest → 对账);② 扩展——衍生品三表与 signals_log、DuckDB 取数模块、不可变 symbol-map artifact;③ 运维化——每日/周日调度与 NAS `lake/` 激活,修订检测(全量校验模式)。
docs/features/0.2/F002-data-bridge/design.md:63:  | `signals_log` | time,exchange,symbol,source,signal_type,confidence,metadata,latest_candle,expected_return,volatility,direction_prob,realized_return_60m,evaluated_at | (date) | `latest_candle` | `time` |
docs/features/0.2/F002-data-bridge/design.md:82:  **标签列的可用性单独处理**:`signals_log.realized_return_60m` 是事后回填的结果列,
docs/features/0.2/F002-data-bridge/design.md:95:  ├── signals_log/date=....r1.parquet        # 无 exchange 维度,按事件日
docs/features/0.2/F002-data-bridge/design.md:204:  **排序键 = 该行的规范编码字节串本身**,不是逻辑主键。理由
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:23:35Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"\\[TEST\\]\" -A 14 docs/features/0.2/F003-alphagen-vendor/tasks.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '1,60p' tools/validate_spec_lifecycle.py && echo \"=====\" && sed -n '150,230p' tools/validate_spec_lifecycle.py"})`


> [reasoning] Now I have enough context. Let me now plan the fixes concretely and make the todo list.

Key design decisions I need to make (as fixer):

**Anchor decisions (must be consistent across spec/design/tasks):**

1. **Verdict vocabulary** (D011): two layers.
   - Stage result enum: `PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE`.
   - Promotion/cost verdict enum: `promising | dead | cost_negative`? Hmm. The finding says: stage 状态（PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE）与晋升/成本 verdict（promising/dead 等）.
   - spec FR-005 scenario uses `cost_verdict=cost_negative` and final verdict `dead`. spec FR-003 scenario says verdict 不得为 PASS/promising.
   - I'll freeze: `stage_verdict` ∈ {PASS, FAIL, UNDERPOWERED, INCOMPLETE, NOT_APPLICABLE}; `promotion_verdict` ∈ {promising, dead, underpowered, incomplete} for member; cohort verdict ∈ {promising, dead, open, incomplete}? Careful with spec §5 lifecycle FINALIZED and AC-003 "cohort 保持 OPEN".
   
   Let me simplify but be consistent:
   - Stage: `PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE` (already in design).
   - Member `promotion_verdict`: `promising`(可进入 cohort 级裁决/临时 PASS 带) | `dead` | `underpowered` | `incomplete`. Hmm, spec says "verdict 不得为 PASS/promising" for required-estimator failure, implying promotion verdict values include PASS/promising? Confusing. Let me define clearly:
     - Member report carries `stage_results[]` + `promotion_verdict ∈ {PROMISING, DEAD, UNDERPOWERED, INCOMPLETE}` (uppercase, matching stage enum style), plus `cost_verdict ∈ {COST_POSITIVE, COST_NEGATIVE, COST_INSUFFICIENT_DATA}`.
     - Wait spec FR-005 scenario says `cost_verdict=cost_negative` lowercase. To minimize churn while removing ambiguity, I could freeze lowercase for verdicts and uppercase for stage states. Hmm, that's subtle. Better: one glossary table in design §3.3 that both spec and design reference, defining exact tokens.

   Let me choose: **uppercase snake for stage states** (PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE) and **lowercase snake for verdicts** (`promising` / `dead` / `cost_negative` ... ). And explicitly say: `PASS` is a **stage state only**; `promising` is a **promotion verdict only**; they are never interchangeable; a run cannot have `promotion_verdict=promising` unless all required stages are `PASS` and cohort is FINALIZED. That resolves spec FR-003's "verdict 不得为 PASS/promising" — I'll rewrite that clause to say "stage 不得为 PASS 且 promotion_verdict 不得为 promising".

   Glossary table (design §3.3, referenced by spec FR-003/FR-005):
   | 层 | 字段 | 枚举 |
   | 阶段状态 | `stage_results[].status` | `PASS \| FAIL \| UNDERPOWERED \| INCOMPLETE \| NOT_APPLICABLE` |
   | 成本裁决 | `cost_verdict` | `cost_positive \| cost_negative \| cost_undetermined` |
   | 样本量裁决 | `sample_tier` | `underpowered \| provisional \| trustworthy` |
   | 成员晋升裁决 | `promotion_verdict` | `promising \| dead \| underpowered \| incomplete`（仅 cohort FINALIZED 后） |
   | cohort 状态 | `cohort_verdict.status` | `OPEN \| FINALIZED` |

2. **Sample tiers** (D006): `underpowered` (<30), `provisional` (30~69, temporary PASS limited to reduced-size paper), `trustworthy` (≥69). AC-004 asserts three tiers.

3. **Five stages** (D021): freeze IDs:
   - `signal_quality`（信号质量）
   - `portfolio_transform`（组合转换）
   - `cost_capacity`（成本/容量）
   - `temporal_stability`（时序稳定）
   - `execution_implementation`（执行实现）
   Failure dimensions ("三维"): tasks T014 says 五阶段/三维失败汇总. Freeze failure dimension schema: `{stage, owner, mechanism, error_code, evidence_ref}`? The finding says "冻结五阶段 ID 枚举与失败维度 schema（枚举、owner、必填字段）". I'll define `failure_taxonomy` with three dimensions: `owner`（责任方：data/signal/portfolio/cost/execution/method）、`mechanism`（机制：missing_input/invalid_input/estimator_error/leakage/violation/infra）、`disposition`（处置：block/stage_reject/retry/not_applicable）? Hmm. Let me define:
     - 三维 = `stage`（哪一级）× `owner`（谁负责）× `mechanism`（为什么）。
     - Schema: `{stage, owner, mechanism, error_code, first_seen, evidence_ref}`, required fields all; owner enum {`data`, `signal`, `method`, `statistics`, `cost`, `execution`, `infra`}; mechanism enum {`missing_input`, `invalid_input`, `capability_unguarded`, `lookahead`, `estimator_failure`, `publish_failure`, `underpowered`, `cost_negative`}.
   - synthesis report contains `failure_taxonomy` aggregation by these three dims.

4. **No-lookahead three layers** (D005): declare ownership:
   - L1 AST 纯度门 (factor definition layer) — owner F003 FR2.4/FR-002 of F003 (generator side) + F007 FR-002 consumes as 方法论守卫 at evaluation time. Evidence: F003 AC / F007 methodology gate tests.
   - L2 独立逐 K 线重放审计 (strategy layer) — per architecture migration table, `independent_cross_backtest.py` → 无前视审计器 (FR3.6). Who owns? This is部署前 strategic-layer audit which is M3/F006. But F007 is where 晋级 (promotion) happens. The finding requires: declare executor/evidence/fail-closed gate before promotion, or if deferred, state blocking point + owner.
   - L3 信号缓存时间戳对齐检查 (data layer) — architecture §4.3 rule 3; signal cache is produced by ... F006/M3? signal cache contract in architecture §4.3. F007's curves/report consume... Actually F007 evaluates FactorDef on snapshots, not signal cache. Signal cache is for deployment (F006). So L2/L3 belong to M3/F006.
   
   Fix: F007 spec/design add an explicit 三层归属表:
   | 层 | 执行者/owner | 证据 | F007 的角色 |
   | L1 AST 纯度 | F003（生成）+ F007 FR-002 方法论守卫复检 | F007 `tests/unit/validation/test_methodology_gate.py` | 评测前 fail-closed 拒绝 |
   | L2 独立逐 K 线重放 | F006/M3（架构迁移表 `independent_cross_backtest.py` → 无前视审计器） | 审计器报告 | F007 只对 canonical 因子证据负责；**晋级 paper 前**由 F006 提供审计通过证明，缺失即阻断晋级 |
   | L3 信号缓存时间戳对齐 | F006/M3（架构 §4.3，审计覆盖 merge/join） | 逐 bar 校验报告 | 同上 |
   And declare F007 is not the owner of L2/L3 (they are strategy/deployment-layer) but must not claim 无前视完成 without them: F007's `promotion_verdict` cannot be `promising` unless L2/L3 audit references present for portfolio-level promotion; for factor-level canonical evidence, F007 records `no_lookahead_levels` in manifest with L1=PASS and L2/L3=not_yet_available (owner F006) — and **no paper promotion** happens at F007 anyway (F007 registration ≠ promotion; promotion to paper is F006). That's honest and closes the finding.

   Careful: spec §3 范围外 line 109 says "离线到决策时 parity、run_record、kill-switch 与启动对账 → F006/M3". Add L2/L3 there too with explicit blocking point.

   Hmm, but the reviewer's suggested fix said "若后移 F006，需写明晋级前阻断点与 owner，不能只在范围外一行带过". So I must write it explicitly in the requirements/invariants, not just 范围外. I'll add it to design §7 权限/失败 + spec 不变量, and add an AC clause? Adding to an existing AC: AC-002 covers FR-002. I could add a new AC-009 for no-lookahead three-layer ownership. Hmm, adding ACs is allowed? The finding doesn't require new AC, but traceability is better. Adding AC-009 and AC-010 etc. increases gate surface (`validate_spec_lifecycle` checks AC references exist). Let me be careful: adding ACs requires `tests:` optional at draft. Fine.

   I'll add AC-009 (三层无前视归属与阻断点) and AC-010 (留出预算台账), AC-011 (样本量三级), AC-012 (五阶段/失败维度 schema), AC-013 (最终确认窗隔离), AC-014 (NFR-004/NFR-005/UX-001 可追踪). Hmm, that's a lot. Maybe better to fold new clauses into existing ACs to limit sprawl:
   - D005 → new AC-009 (三层无前视归属) — needs its own since it's cross-layer.
   - D010 → AC-001 add DR-005 + "台账零行" clause. Already AC-001 references DR-004,NFR-003,FR-001. Add DR-005.
   - D006 → AC-004 add sample tier three-level clause. AC-004 currently (`FR-005`). Add DR-006? No, sample tier is FR-005 clause.
   - D019 → AC-006? or new. 最终确认窗 relates to NFR-003/IR-003. Add clause to AC-001? Hmm AC-001 is about preview越权 + 留出预算零变化. 最终确认窗 isolation fits AC-001's spirit. But cleaner: add AC-010.
   - D014 (NFR-004 approximation) → add clause to AC-008? AC-008 is CLI/schema. Better new AC-011 or fold into AC-003? Let me add AC-010 for 报告标注与不可见性 (NFR-003 最终确认窗 + NFR-004 近似标注)。Hmm mixing. 
   
   Let me just add a small number of new ACs, each with clear requirement refs:
   - AC-009 (`FR-002`, `NFR-003`): 三层无前视归属——L1 由 F007 方法论守卫执行 fail-closed；L2/L3 owner=F006 且在 paper 晋级前阻断；manifest 记录三层状态，缺失不得声称无前视通过。
   - AC-010 (`NFR-003`, `IR-003`): 最终确认窗数据不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取 fail-closed。
   - AC-011 (`NFR-004`, `NFR-005`, `UX-001`): preview 近似在报告显式标注；产物路径为 POSIX 逻辑路径；CLI 首屏含 tier/cohort/digest/首个失败原因。
   - AC-012 (`FR-003`): 五阶段 ID 与失败维度 schema 冻结并可校验（stage/owner/mechanism 三键聚合）。
   
   And modify AC-001 (add DR-005), AC-004 (three tiers), AC-003 (multi-member batch denominator).

   Hmm, "AC-003 分母语义缺多成员批量用例" → just add a clause + tests to AC-003 (draft so tests optional; I'll write the requirement).

5. **Holdout budget ledger** (D010): new DR-005: `HoldoutBudgetLedger` append-only, fields: `candidate_id`, `week`（ISO 周）, `verdict`, `recorded_at`, `execution_tier=canonical`, `experiment_id`, `cohort_id`; only canonical writer may append; preview overreach → reject event `evaluation.gate_rejected`. Path `reports/holdout_budget/ledger.jsonl` (append-only). design §3.2 adds dir; tasks add implementation task; AC-001 adds "台账零行" assertion + negative test.

   Wait: who consumes holdout? F007 evaluates factors on ResearchSnapshot; holdout is part of the snapshot window. FR3.4's holdout is for PortfolioDef (组合) final 90 days. Hmm! PRD FR3.4: "FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef → PortfolioDef 最终 90 天留出". So the 90-day holdout applies to PortfolioDef, not to single factors. And ADR-0003 decision 1 similar. But F007 spec claims "preview 不能污染 ... 留出预算" and AC-001 "留出预算零变化". So F007 must at least own the budget ledger entity and enforce preview has no write/read access. Fine — F007 owns the ledger as the gate owner, even if holdout evaluation of PortfolioDef lands in M3. But careful about scope: F007 §3 范围外 includes PortfolioDef building. The ledger can be owned by F007 with writes only from canonical tier. I'll keep it as "预留 + preview 无写权限" and declare the F007-owned ledger artifact with schema, consistent with ADR-0003 §留出期使用预算 2.

   Hmm — is D010 possibly "上游任务未执行"? The ledger is defined in ADR-0003 (a decision), not a task. F007 is the implementation carrier (it owns 留出预算 isolation). So it's a genuine spec gap. Accept.

6. **D009 real-env task**: T022 → split/differentiate: T022 uses `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration/test_f007_controls_real.py` on immutable crypto snapshot with `--snapshot <id>` + digest recorded, and writes evidence with hostname + `device=cpu`; spec:275 测试策略 + design §8 updated. Add `tests/integration/test_f007_controls_real.py` (real env) distinct from T016's `test_f007_controls.py` (fixture). And a T025? No, modify T022 and add to §8 mapping.

7. **D015 mutation alignment**: T017 covers mutations incl. preview writer/publish; T021 declares AC-002, AC-005 only. Fix: T017 labels add AC-001, AC-003, AC-005 (already has FR-001, FR-002, NFR-003; AC-001 missing). Actually T017 currently: `(FR-001, FR-002, NFR-003)` — no AC tags at all! And T021: `(AC-002, AC-005)`. Fix: T017 → `(FR-001, FR-002, NFR-003, AC-001, AC-002, AC-003, AC-005)`; T021 → same AC set; add mutation tooling pin + mutant-killed artifact (e.g. `reports/mutation/f007/mutation_report.json`) as verify output.

8. **D012 concurrency**: add task T025 (concurrent claim/fault injection: same-ID concurrent claim, crash lease takeover, finalize atomicity) with verify `tests/integration/test_f007_concurrency.py`; design §8 maps SC-002; T023 (or new) references. Careful: adding T025 changes max task id → T025 needs incoming edge for DAG gate. I'll add edges to T025 in §4 or make T024 remain last with T025... no, ids sorted by number, max becomes T025. So need `T0xx -> T025` edge. I'll add `` `T012/T013 -> T025` `` and `` `T016/T017/T022/T023/T025 -> T024` ``. Hmm if T025 > T024 then edge T025->T024 is backward → gate error. So T024 (回写/收口) must be renumbered to be last. Ugh. Options: insert new tasks before T024 with ids T025+? Then T024 is no longer max... Actually max(ids) = T025 then, and T024 has no incoming edge required? Gate requires only the max id to have an incoming edge. If max = T025 and we add an edge into T025, fine. But then T024 (收口回写) sits before T025 numerically while logically last → ordering inconsistency (task numbers = execution order per gate comment). Bad.

   Cleaner: renumber T024 → T026 and add T024/T025 before it. But renumbering T024 changes references? §3 T023 references... T024 referenced in §4? Currently §4 doesn't reference T024. §3 has T023, T024. So I can renumber: make new tasks T024 (concurrency) and T025 (real-env controls)... but T022 is real-env. Let me restructure §3:
   - T018, T019, T020, T021, T022 (real env), T023 (project gate), then new T024 (concurrency/fault-injection integration), T025 (回写 spec/BACKLOG/status).
   
   That means: existing T024 (回写) → becomes T025; new concurrency task = T024. Then max = T025, need edge into T025. Good, and T024 gets edges from T012/T013.
   
   Also D016 (second implementation spot check) needs a task → add T026? That again shifts max. Alternatively put second-implementation task in §5 明确后移 with owner + target feature (the finding allows "或在 tasks 第 5 节明确后移目标 Feature 与 owner"). Simpler: §5 add "统计第二实现对照 → F007.1/独立研究 Feature（owner=Georg，入口：`tests/unit/evaluation/test_second_implementation.py`，time-box）". Hmm, but PRD FR3.7 says the second implementation is for 高价值候选/评测差异/系统升级, and spec:290 decision row says "自研最小协议 + 正/负控制 + 第二实现抽查". The finding wants a carrier. I'll add a task in §3 as T026 → then max=T026, need edge into T026. Fine, just add edges.
   
   Hmm, this is getting complex but manageable. Let me decide final task numbering:
   - T001–T017 unchanged (Phase 1–3)
   - §3: T018–T023 unchanged
   - New: T024 并发/故障注入集成（D012）, T025 统计第二实现对照抽查（D016）, T026 回写 spec/tests/BACKLOG/状态（原 T024）
   
   Wait but T022 real-env controls and T024 concurrency both integration. Fine.
   
   Actually, D016's suggested fix: "新增第二实现对照任务（明确 time-box、对照对象、容差与证据路径），或在 tasks 第 5 节明确后移目标 Feature 与 owner". A task is better because the PRD FR3.7 obligation is真. But is second implementation in F007's v0.2 scope? spec §7 decision says "第二实现抽查" as part of statistics risk mitigation. PRD FR3.7 says do it on high-value candidates or system upgrades, within 1-week time-box via Vibe-Trading. For F007 v0.2, a lightweight carrier: T025 (time-box 1 week, only for 高价值候选; compare BH-FDR/bootstrap against independent implementation via Vibe-Trading `quantlib_call` or hand-rolled; tolerance; evidence path `reports/second_impl/<experiment_id>/`). Good.

   Also `[TEST]` group (D001) must come in §3 as `### [TEST] 组：层 2 旅程验收轨` — it's a third-level heading inside §2 or §3? The gate `TEST_GROUP_RE = ^###\s+\[TEST\]` anywhere; the finding says "tasks 第 3 节增补 `### [TEST] 组：层 2 旅程验收轨`". Wait, §3 is 验证与验收任务 (a `##` section). Adding `### [TEST] 组` under §3 is fine. Let me check F003's implementation for the pattern. Let me look at F003 tasks §3.

Let me check that quickly to match the established pattern.

9. **D002**: design/tasks frontmatter add F003; design §2 add ingestion points (upstream contract adapter module `src/alphamill/evaluation/upstream_contracts.py`?) and §4 contract section for F003 events/capability registry/pool; tasks add T001 extension or new contract task. I'll:
   - design frontmatter related_features: [F002, F003, F004, F008]
   - design §2 模块放置 add: `src/alphamill/evaluation/upstream/` — F003 `generation.*` 事件读取、算子能力清单装载、协同池 FactorDef 摄入.
   - design §4 add contract block: `generation.run_completed` / `generation.candidate_rejected` 只读摄入为漏斗第一级（只消费 `status=completed`）；算子能力登记表 → 方法论门 guard 覆盖清单；协同池 `generator="pool"` FactorDef 与普通 FactorDef 同路径评测.
   - design §0 add F003 upstream contract line.
   - tasks: T001 add F003 contracts? Better add a new task T027? No—more renumbering. Instead extend T001's verify to `tests/contract/test_f007_upstream_contracts.py` (already there!) and add a clause. Actually T001 already verifies `tests/contract/test_f007_upstream_contracts.py` — good carrier. I'll extend T001 text to include F003/F008 ingestion contract and add a dedicated task in Phase 2: hmm. The finding says "tasks 增对应实现与契约任务（T001 上游契约或新任务）". So extending T001 is explicitly allowed. I'll extend T001 and also add funnel-level ingestion into T012 or T014 (漏斗第一级 = F003 rejected events; funnel is in synthesis T014). Let me: T014 text add "漏斗第一级摄取 F003 `generation.*`（仅 completed）/`candidate_rejected`". Good.

10. **D003**: spec frontmatter related_features add F008; §0 upstream contract add F008 `universe_at(T)` + digest; IR-002 reference; design/tasks frontmatter add F008; design §0 add F008.

11. **D004**: universe/calendar split as discussed.

12. **D014**: design §3.3 report schema add `approximation` field; spec FR-006/NFR-004; tasks T015 (schema reader) add assertion; AC-011.

13. **D017**: F007 spec/design add Kronos/F004 signal factor contract: 
    - Provenance: FactorDef derived from F002 `signals_log` dataset records `source` (kronos|placeholder) in its definition meta / run provenance; manifest records per-dataset `source` distribution.
    - Rules: `source=placeholder` → preview 允许（报告显式标注 `signal_source=placeholder`）；canonical **拒绝**（fail-closed, `E_INPUT_INVALID`）unless the cohort's pre-registration explicitly declares a placeholder-control purpose? Hmm. Better: canonical forbids placeholder for 候选评测; placeholder 只允许用于负控制/管线测试并显式标注, 记 `NOT_APPLICABLE`? Let me be careful: F002's signals_log is 100% placeholder currently; F007's positive controls (funding carry, BTC/ETH momentum) don't need Kronos. So canonical can forbid placeholder sources — clean fail-closed rule consistent with ADR-0003. I'll write:
      - canonical 只接受经显式适配的 `FactorDef`，且其数据来源 dataset 的 `source` 分布必须为真实源（`source != placeholder`）；`signals_log` 全为 placeholder 时 canonical 拒绝对应因子（`E_INPUT_INVALID`），preview 可运行但报告必须标注 `signal_source=placeholder` 与 `approximation=true`。
      - F004 只交付真实信号源与 `/predict` 契约，不升级 signals_log 内容；F007 不实现 F004 的消费者路由切换，只定义摄入契约。
    - Add AC clause to AC-008? Or AC-011. I'll add to AC-008 (输入契约) hmm AC-008 is CLI/schema. Let me put in AC-002? AC-002 is FR-002 methodology. The finding is about 来源契约 → IR-002 输入契约. Add clause to AC-008 (`IR-002` already). Good: AC-008 add "以及 placeholder 来源在 canonical 被拒、preview 显式标注".

14. **D018**: design §6 clarify F005 must consume via `src/alphamill/api/`; file reader is API/backend-internal adapter only; no frontend direct read.

15. **D019**: spec NFR-003 + IR-003 + design §3.3/§7 declare final confirmation window data never in Agent/preview-readable artifacts, fail-closed; AC-010.

16. **D020**: design §8 add the 5 missing test files.

17. **D022**: AC-011 covers NFR-005/UX-001; tasks T015/T006 verify additions (CLI 首屏 snapshot test `tests/integration/test_f007_cli.py`).

18. **D023**: move design.md:16-18 note → tasks.md §0 rule + [TEST] group; design keeps one-line constraint pointing at tasks.

19. **D024**: unify state vocab: design:35 says `reports/bench/` for canonical; spec:205-207 lifecycle states; map `PREVIEW_DONE`/`REGISTERED`/`FINALIZED`; add `evaluation.registered` to TR-003. Fix TR-003 to name event `evaluation.registered` and add "canonical 物理落 `reports/bench/`" note in spec DR/IR? Better in design §3.2/§1 and spec NFR/IR. I'll add to spec TR-003 explicit event name + design §3.2 note that canonical = `reports/bench/` 物理根，`REGISTERED` 对应 `evaluation.registered`.

20. **D025**: add property-test execution task + seed/generator constraints in design §8. Task: T026? I have T026 for 回写. Add property test as part of T004 (identity properties) / T019 (runs identity property tests). The finding wants "为身份稳定、ResearchSnapshot 变化敏感性等属性测试补显式执行任务，并在 design 第 8 节约束输入生成方式与可复现 seed". So: design §8 add a row/notes: property tests use fixed seed + explicit generator (`tests/property/`?), reproducible. And add task T018-T020 already run them. Hmm "显式执行任务" — I'll add T026 (property test track) and move 回写 to T027. Let me recount:
    - T018–T023 (unchanged)
    - T024: 并发/故障注入集成 (D012)
    - T025: 统计第二实现对照抽查 (D016)
    - T026: 属性测试轨（身份稳定/快照敏感性, seed 固定, 生成器约束）(D025)
    - T027: 回写 spec tests/AC 证据、BACKLOG 与状态 (原 T024)
    Max = T027; add edges into T027.

Hmm wait — also D015 wants "变异工具依赖 pin 与 mutant-killed 证据产物". That's T017 + T021 text changes, plus design §8 note. OK.

Now the **gate/regression tests**. For each finding I need a `check_id` in `tools/check_doc_consistency.py` (TEXT_CHECKS entry with finding id F007-Dxxx, requires/forbids) and mutation tests come free via the parametrized tests (since they iterate over TEXT_CHECKS). Plus F007-specific custom checks where parsing is needed (task DAG edges → check_task_dag already covers generic; but D007/D008 are "missing edges" — a text check can require the literal edge text `` `T009 -> T012` `` etc. That's simple and mutation-testable).

Careful: the existing TEXT_CHECKS use F003 file constants. I'll add F007 constants: F007_SPEC, F007_DESIGN, F007_TASKS, plus F008_SPEC? For D003 (F008 declared) I need to read F007_SPEC only. For D004 maybe check F007 design contains the split refs. Keep checks anchored on F007 files primarily to limit blast radius. But note: `_materialize` in the test copies `ALL_DOC_FILES` = {SPEC, DESIGN, TASKS, F007_SPEC} — I must extend that set to include F007_DESIGN, F007_TASKS. And any other files used in requires/forbids (e.g., if I check F008 spec, must add).

Let me define ALL_DOC_FILES dynamically in the test: `{rel for chk in TEXT_CHECKS for rel,_ in chk.requires+chk.forbids} | custom check files`. Better: refactor test to compute. I'll update the test file accordingly (it's a repo test, allowed to modify).

Also `test_repo_passes_all_checks` must stay green.

Now the deliverable is large. Let me think about parallelization. The doc edits must be coherent — I'll do them myself, sequentially by finding, committing per finding. The gate script + tests I can delegate after freezing the required text... but the required text IS determined by my doc edits. Actually the cleanest order:

1. First write the doc fixes (spec/design/tasks) — 25 findings.
2. Then write the gate checks matching the fixed text + run mutation verification.
3. Then run full verify.

But protocol says one finding per commit. I'll do: edit finding → add its check to check_doc_consistency → run the targeted test (fast: `pytest tests/unit/test_check_doc_consistency.py -q`) → commit. That's 25 iterations. Heavy but doable? Each iteration involves edits across up to 4 files. Hmm, 25 commits × (edit + test + commit) is a lot of tool calls but it's the protocol. Estimated: maybe 60-100 tool calls. That's a lot but let's go — though I should be pragmatic. 

Alternative reading of §6: "一个 finding 一个 commit" — mandatory for bisect/revert. I'll comply but batch tightly: group findings that touch the same check into separate commits still.

Hmm. Actually, let me reconsider: with 25 findings and each requiring multi-file doc edits, doing this fully solo will consume enormous context. Let me delegate a portion to subagents with very precise instructions? Risk: inconsistency. Given the anchor decisions are now made by me, I could produce a precise "edit spec" per finding and delegate execution. But subagent doc edits are error-prone and verification cost is high.

Middle path: I do all doc edits myself (they're the semantic core), and delegate the gate-tool + test extension to a `deep`/`unspecified-high` subagent after docs are frozen, with exact check_id list and needles. Actually the mutation tests are auto-generated by parametrize, so the subagent work is: add N TextCheck entries with exact literals + update ALL_DOC_FILES + add custom checks. That's mechanical but must match literals exactly — risky if delegated; but I can verify by running.

Given "one finding one commit" and the need for evidence, I'll do it myself but reduce commit granularity risk by committing per finding in a single git command after edits. Let me aim for efficiency: for each finding, use `edit` (1-3 calls) + then batch commits at the end? No — commit per finding requires commits interleaved. I can do edits for several findings then commit them separately with `git add <paths> && git commit`? Problem: same files touched by multiple findings → can't separate by path. Would need `git add -p` (interactive, not available). Hmm.

So per-finding commits require: edit → commit → edit → commit. That's fine: I can chain edit+commit in one bash call? No, edit tool is separate. But I can do: edit tool call, then bash `git add ... && git commit -m ...`. Two calls per finding minimum, plus test runs.

Practical approach: I'll do doc edits finding-by-finding, and commit per finding, running the targeted gate check at the end of each commit via the cheap direct script (`python tools/check_doc_consistency.py`) — but the check for that finding must exist. So order per finding: (a) edit docs, (b) add check to tool, (c) run `python tools/check_doc_consistency.py` expecting "全部通过", (d) commit docs+tool. And add tests once (parametrized auto-covers). Then run pytest test_check_doc_consistency.py at intervals.

Hmm, but the mutation test for a new check requires the needle removal to go red — auto test covers it. I'll run the full test file once at the end (or a couple of times).

Given the size, maybe I should reduce to fewer commits by grouping related findings? The skill is explicit: one finding one commit. I'll comply. Actually... let me reconsider the cost/benefit and the risk of running out of context. 

I think the pragmatic and still-compliant approach: implement all doc fixes + checks, committing per finding. To keep context manageable, I'll be terse in edits (use precise `edit` calls).

Let me also decide: do NOT modify CURRENT-doc-F007.md (reviewer's file). Write FIX-log.md Round 2 (append). FIX-log Round 1 exists for F003; I append a new section for F007 Round 1 (fix round). Per template: `## Round <N> · <date>`. Since this is F007's fixer declaration for review round 1 → I'll label `## F007 · Round 1 修复声明` to avoid confusion with F003's Round 1 in the same file. Hmm, the file is shared. The F003 entry is titled "## Round 1 · 2026-09-16 · report_type: doc-review". For F007 I'll title "## F007 Round 1 修复声明 · 2026-09-17 · report_type: doc-review".

Now, before writing, let me check F003's tasks.md §3 [TEST] group format and the validate_spec_lifecycle rules to make sure my additions pass gates.

Let me look at F003 tasks §3 and the validate_spec_lifecycle checks (AC format, structure, etc.).

Also need to check `check_doc_links.py` (relative links resolvable) and `check_dep_pins`.

Let me read F003 tasks §3 and validate_spec_lifecycle relevant parts.

  <details><summary>tool output</summary>

  ```text
82:### [TEST] 组：层 2 旅程验收轨（必填）
83-
84:- [ ] T036 [TEST] (`US-001`, `AC-001`, `AC-003`, `AC-004`): 旅程 US-001 端到端验收——固定快照绑定与 seed 经 `produce()` 连跑两次得到同一 `factor_id` 集合、落盘后加载的 FactorDef 可直接执行、invalid 绑定被拒并留 `rejected` 终态；夹具在 Phase 1 先以红灯立起，收尾全量执行 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/unit/test_f003_generator_contract.py tests/unit/test_f003_factor_store.py tests/unit/test_f003_alphagen_adapter.py tests/integration/test_f003_lake_tensor.py`
85:- [ ] T037 [TEST] (`US-002`, `AC-007`): 旅程 US-002 端到端验收——在执行机按 `smoke --day 1`、`--day 2` 走完 time-box：逐条 L1 判据 pass/fail、两条 M2 义务入 manifest、判据未达标即输出 L1 降级、回切请求被拒；收尾全量执行 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f003_smoke_gate.py` + 当日 manifest
86:- [ ] T038 [TEST] (`US-003`, `AC-006`, `AC-008`, `AC-009`): 旅程 US-003 端
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
#!/usr/bin/env python3
"""规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。

校验 docs/features/<version>/Fddd-*/ 三件套：
  - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
  - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
  - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
    review/done 的 tests 路径真实存在
  - 进入开发流转（ready-for-development / in-progress / review）的 tasks.md
    必须含 `### [TEST] 组`（层 2 旅程验收轨）
  - BACKLOG.md 与所有非 done Feature 双向集合一致

纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
并补了变异测试。用法：python tools/validate_spec_lifecycle.py
退出码 0 = 全部通过；1 = 存在违规。
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALLOWED_STATUS = {"draft", "ready-for-development", "in-progress", "review", "done"}
ALLOWE
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:24:17Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '60,150p' tools/validate_spec_lifecycle.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '230,300p' tools/validate_spec_lifecycle.py"})`


> [reasoning] Good. Now I know:
- `[TEST]` group pattern: `- [ ] T0NN [TEST] (...)` under `### [TEST] 组：层 2 旅程验收轨（必填）`.
- The gate requires `[TEST]` tasks to be `- [ ] Tnnn [TEST] (...)`.
- AC_RE format matters. Let me check AC_RE and requirement_ids.

Also note the check_task_dag `TASK_RE = ^-\s+\[[ xX]\]\s+(T\d{3})` — `[TEST]` appears after T036: `- [ ] T036 [TEST] (...)` — matches T036 then `[P]`? parse_task_lines checks `"[P]" in line` for parallel. OK.

Let me check AC_RE and requirement_ids quickly, plus the AC-line format requirement.

  <details><summary>tool output</summary>

  ```text
# [TEST] 组是「进入代码开发前」的硬性要求：不含 done（历史 Feature 豁免，纳入会
# 立刻破坏 F001/F004）与 draft（尚未进入流转）。
TEST_GROUP_STATUSES = {"ready-for-development", "in-progress", "review"}
TEST_GROUP_RE = re.compile(r"^###\s+\[TEST\]", re.M)
REQ_RE = re.compile(r"\b(?:FR|DR|TR|IR|UX|NFR)-\d+\b")
AC_RE = re.compile(r"^-\s+\[([ xX])\]\s+\*\*AC-(\d+)\*\*\s*\(([^)]*)\)\s*:\s*(.*)$")
Q_RE = re.compile(r"^-\s+\[([ xX])\]\s+[QD]Q?-\d+")


def parse_frontmatter(text: str) -> dict | None:
    norm = text.replace("\r\n", "\n")
    m = re.match(r"^---\n([\s\S]*?)\n---", norm)
    if not m:
        return None
    fm: dict = {}
    for line in m.group(1).split("\n"):
        kv = re.match(r"^([A-Za-z_]\w*):\s*(.*)$", line)
        if kv:
            fm[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fm


def st
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
ac = AC_RE.match(line)
        if not ac:
            continue
        if ac.group(2) in seen:
            tag(f"AC-{ac.group(2)} 重复")
        seen.add(ac.group(2))
        refs = set(REQ_RE.findall(ac.group(3)))
        bad = [r for r in refs if r not in req_ids]
        if bad:
            tag(f"AC-{ac.group(2)} 引用不存在的需求: {', '.join(sorted(bad))}")
        tests = [t for t in re.findall(r"`([^`]+)`", ac.group(4)) if not t.startswith("http")]
        if spec_fm.get("status") in ("review", "done") and not tests:
            tag(f"AC-{ac.group(2)} 在 {spec_fm.get('status')} 状态缺少 tests: 路径")
        # tests 路径存在性只在 review/done 强制；路径格式任何状态都校验。
        if spec_fm.get("status") not in ("review", "done"):
            continue
        for t in tests:
            if t.startswith("/") or ".." in t:

…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:24:22Z

- **tool**: `todowrite({"todos": [{"content": "tasks.md: 增 ### [TEST] 组 T027-T029 并重编号回写任务 (D001) - expect [TEST] 门在 ready-for-development 下可过", "status": "in_progress", "priority": "high"}, {"content": "design.md + tasks.md: 补 F003 摄入点/算子登记表/协同池契约 (D002) - expect design 有 F003 且 check 可红", "status": "pending", "priority": "high"}, {"content": "spec.md + design/tasks frontmatter: 声明 F008 上游与 universe_at(T) (D003) - expect F007_D003 check 绿", "status": "pending", "priority": "high"}, {"content": "spec/design: universe 
…[truncated])`


> [reasoning] Now I have full understanding of the gates. Let me set up the todo list and start.

Given the enormous scope, I'll organize into a tracked plan. Let me create todos.

Actually, one important consideration: the user asked me to "审视和修复" (scrutinize and fix). Per the skill, I should be honest about which findings I accept/reject. Let me finalize my accept/reject decisions:

- Accept all 25? Let me consider whether any is "上游任务未执行" → tracked instead of fixed. D010 (holdout ledger) — it's F007's to implement. D016 (second impl) — PRD FR3.7 obligation, carrier needed → task. D005 (L2/L3 layers) — owner F006/M3 → the fix is declaring ownership+blocking point; not "tracked task" since it's cross-feature. Hmm, the skill says `tracked` = "已落到任务条目的未执行任务". For D005, part of it (L2/L3 audit implementation) belongs to F006, so I could mark the F007-side as fixed (declaration) and... but statuses are the reviewer's to flip. As fixer I just declare. I'll declare all as fixed with evidence, except possibly none rejected.

Wait — should I reject any? "审视" means I should assess. Let me look for a genuinely wrong finding... 

D023: design.md:16-18 is a process precondition, arguably legitimately belongs in design as a "开发前置约束" since design is the artifact that carries constraints. `docs/features/README.md:103` says design 不写逐步编码任务 — this note isn't a coding task. I could reject it with evidence (README:103 says "design 只描述结构、契约、状态、失败和技术取舍，不写逐步编码任务" — the note is a process gate constraint, not a coding task). But the reviewer's proposed fix (move action instruction to tasks) is cheap and improves channel hygiene. Partial accept: move the actionable part to tasks §0, keep design with a one-line constraint. That's "partial" → but partial requires the rejected part to have a carrier. Hmm, "partial" complicates. Simpler: accept (fix by moving). It's Low/quality, non-blocking. I'll accept fully.

D018 (Low): F005 frontend/API — the finding says design:217 has ambiguity. Fix by clarifying. Accept.

D024 (Low): accept.

Are there findings that are factually wrong? Let me double check D004's claim about calendar ownership: F008 tasks:90 explicitly defers calendar to F007. F007 design:145 uses `--universe-calendar <path>` single flag. So yes conflict. Accept.

D014: NFR-004 requires preview approximation annotation. design doesn't have it. Accept.

D006: check spec:118 "指标样本不足：输出 UNDERPOWERED" — that's a single-tier. PRD FR3.5 three tiers. Accept.

D011: Accept.

D015: Accept.

D021: Accept.

D022: Accept.

D025: Accept.

D002, D003, D005, D007, D008, D009, D010, D012, D013, D016, D017, D019, D020, D023, D001: accept.

So all 25 fixed, no rejected. Hmm — the skill warns "全接纳说明检视在凑数". But some findings genuinely need a judgment. I'll accept all but note in FIX-log why no rejections (each was verified against source docs). Actually, let me reconsider D023 more carefully as a possible partial/reject to show genuine scrutiny... The reviewer itself classified it Low quality and non-blocking. Its evidence (README:103) exists. I'll fix it — cheap.

Hmm, one more: D001 — the [TEST] group. Note the gate `TEST_GROUP_STATUSES` excludes draft. And design:16-18 says the [TEST] group is required before dev. Since D023 says design shouldn't carry that instruction and I'm moving it to tasks §0, D001 and D023 interlock. Fine: move instruction to tasks §0 + add the [TEST] group (D001). Consistent.

Now let me plan the concrete text edits. I'll write them carefully. Let me draft each file's full new content mentally, then apply edits.

### spec.md changes

frontmatter: `related_features: [F002, F003, F004, F008]`, updated: 2026-09-17.

§0:
- 上游 Contract 来源: add F008 line. Current line 22 mixes F003. I'll add a new bullet:
  - **上游 Contract 来源（续）**：F008 的 point-in-time 宇宙台账 artifact（`IR-002` 内容寻址 digest 与 `universe_at(T)` 查询、`IR-003` 的 `schema_version`）；calendar artifact 由本 Feature 拥有（F008 §5 明确后移）。
  Also add D005 three-layer note? Put ownership in §4/§5.
- 上游决策: add nothing.
- Maybe add 「三层无前视归属」 pointer.

§1 非目标: add "不实现策略层逐 K 线重放器与信号缓存对齐审计（owner=F006/M3），但必须在晋级前阻断" — hmm 非目标 is product-intent exclusions. Better in §3 范围外 + §5 不变量. The finding wants explicit ownership. I'll add in §1 非目标 a line and §3 范围外 detail.

§3 范围外: modify the F006 line to name L2/L3 explicitly:
- 离线到决策时 parity、run_record、kill-switch 与启动对账，以及**无前视二层/三层（独立逐 K 线重放、信号缓存 merge/join 时间戳对齐）的审计器实现** → F006/M3；但 **paper 晋级前** F007 必须要求 L2/L3 审计引用齐备，缺失即阻断（见 §5 不变量）。

§4:
- FR-002: add 三层归属? Better new requirement? The finding: "F007 spec/design 明确三层归属". I'll extend FR-002 (方法论递增守卫) with a sub-clause and add a new requirement FR-007 (无前视三层归属与晋级阻断)? Adding FR-007 requires AC reference; FR-007 can be referenced by AC-009. Hmm, adding a requirement is cleaner than overloading FR-002 which is about the methodology gate.

Let me add **FR-007 无前视三层归属与晋级阻断**:
```
### Requirement: 无前视三层归属与晋级阻断（`FR-007`）

系统应当把 PRD FR3.6 的三层无前视防线归属显式化：AST 纯度门由 F007 方法论守卫在评测入口 fail-closed 执行（执行者在 F003 生成侧，F007 复检）；独立逐 K 线重放审计与信号缓存 merge/join 时间戳对齐检查的 owner 为 F006/M3，F007 不重复实现。manifest 必须记录三层各自的状态与证据引用；**L2/L3 未取得通过证据时，任何成员或组合不得晋级 paper**，状态记 `not_yet_available` 并携带 owner，不得记 PASS 或静默省略。
```
Then AC-009 references FR-007.

- FR-005: add three-tier sample verdict + retitle? Current FR-005 title 成本、容量与时间稳定性. Sample tier belongs to 样本量裁决. The reviewer suggested "在 spec FR-005 与 design 第 3.3/7 节冻结三级样本量裁决" and "AC-004 增三级断言". OK, extend FR-005 (or make FR-008). Since reviewer suggested FR-005, I'll extend FR-005 with a clause + scenario:
```
系统应当输出零成本/maker/taker 三档、资金费率、breakeven cost、换手、持有期与适用的容量代理，并以 purged/embargoed rolling split 记录选择期到留出的稳定性；成本后不为正时 verdict 为 `dead`。样本量按三级裁决：`<30` 为 `underpowered`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口）；`30~69` 为 `provisional`（最多临时 PASS，仅允许缩减仓位进入 paper，不构成可信判定）；`≈≥69` 才允许 `trustworthy` 完整成本后 PASS/FAIL 判定。
#### Scenario: 欠功效与临时 PASS 分离
- GIVEN 一个成本后为正但样本量分别为 25 / 50 / 80 的候选
- WHEN 裁决
- THEN 三者分别得 `underpowered` / `provisional`（仅缩减仓位 paper）/ `trustworthy`（可计入北极星判据），且 `provisional` 不得被任何实盘前置引述
```

- DR-005 holdout budget ledger:
```
- **DR-005**：`HoldoutBudgetLedger` 应当以 append-only 台账持久化每次留出评估（`candidate_id`、ISO 周、`experiment_id`、`cohort_id`、`verdict`、`recorded_at`、`execution_tier=canonical`）；只有 canonical capability 可追加；preview 越权写入必须被拒绝并写 `evaluation.gate_rejected`。台账与 manifest 同为可复现要件，不支持事后补记（ADR-0003 留出期使用预算）。
```
- DR-006? For calendar artifact ownership: 
```
- **DR-006**：`UniverseCalendarBinding` 应当把 universe 与 calendar 拆为两个独立 artifact 引用：universe 按 F008 `IR-002` 的内容寻址 digest 与 `universe_at(T)` 消费（CSV），calendar 由本 Feature 拥有并规范化保存为内容寻址 JSON；`universe_calendar_digest`（ADR-0007 字段）由两者的 digest 组合导出，不再是单一 JSON 文件摘要。
```
Hmm, is adding DR-006 necessary? D004 fix requires spec DR-001/IR-002 sync. DR-001 mentions "universe/calendar 摘要". I could edit DR-001 in place. But an explicit entity is clearer. Adding DR-006 is fine (referenced by AC-006? AC-006 references DR-001, DR-002, NFR-002). I'll add DR-006 and reference it in AC-006.

- TR-003: make `evaluation.registered` explicit:
```
- **TR-003**：canonical population 登记应使用 `evaluation.registered` 事件（experiment_id 幂等键）并引用 manifest ID；canonical 物理落 `reports/bench/`，与 preview 的 `reports/preview/` 隔离。
```

- IR-002: rewrite to split universe/calendar refs:
```
- **IR-002**：canonical 评测只接受已发布 ResearchSnapshot ID 和可解析的 FactorDef/冻结 PortfolioDef 引用；preview 请求 latest 时必须显式提供不可变 symbol-map ref、F008 universe artifact digest（或可解析引用）与 calendar artifact 输入，builder 分别校验 universe 的 `universe_at(T)` 语义与 calendar schema 后内容寻址冻结并返回 snapshot ID；任何 tier 都不直接接受任意数据库查询。缺失任一 artifact 即失败关闭。
```

- IR-003: add 最终确认窗 exclusion + approximation? D019 says spec NFR-003/IR-003 + design. I'll extend IR-003: "…结构化 failure；Agent/preview 可读产物不得包含最终确认窗上的任何统计量（fail-closed）。"
- NFR-003: extend "Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力；最终确认窗统计量不得出现于任何 Agent/preview 可读的 report/manifest/synthesis，违规即 fail-closed。"
- NFR-004: keep; add approximation field pointer.
- NFR-005: keep (D022 needs AC ref).
- UX-001: keep.

§5 生命周期与不变量: add invariants:
- "**无前视三层**：L1 由本 Feature 方法论守卫 fail-closed 执行；L2（独立逐 K 线重放）与 L3（信号缓存时间戳对齐）owner 为 F006/M3，未取得通过证据前不得晋级 paper，状态记 `not_yet_available` 并携带 owner。"
- "留出预算台账只由 canonical capability 追加；preview 写入尝试即失败并留拒绝事件。"
- "最终确认窗数据不得进入任何 Agent/preview 可读产物。"

§6 SC/AC: 
- SC-002 keep (D012 adds task).
- AC-001: add DR-005 + ledger zero-row clause.
- AC-003: add multi-member batch clause.
- AC-004: add three-tier clause.
- AC-006: add DR-006.
- AC-008: add placeholder rule.
- new AC-009 (FR-007), AC-010 (NFR-003 最终确认窗), AC-011 (NFR-004/NFR-005/UX-001), AC-012 (FR-003 五阶段/失败维度).
Hmm, AC-012 for D021 (five-stage IDs + failure dimension schema). Reviewer suggested design §3.3/§4 freeze + spec FR-003 same list + T014. AC ref optional but good. I'll add.

Careful: AC count growing to 12. Fine.

§7 测试策略: update 真实环境验证 line (D009): 
```
- 真实环境验证：在**本机不可变 crypto 快照**上以 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f007_controls_real.py` 独立取证（绑定 snapshot ID + `value_digest`、记录 hostname 与 `device=cpu`、证据落 `reports/f007/real_env/<run_id>/`）；不得与 fixture 控制（T016）共用同一命令或同一夹具充当证据。
```
- 决策与风险: D016 carrier? add row or extend 统计实现风险 row 后续 column → "T025（time-box 1 周）". Also D005 row? Let me add a row for 无前视三层归属.

### design.md changes

- frontmatter related_features: [F002, F003, F004, F008]; updated 2026-09-17.
- Remove/replace lines 16-18 (D023): keep a one-line constraint pointing to tasks:
```
> **开发前置约束**：`tasks.md` §3 的 `[TEST]` 组（层 2 旅程验收轨）是进入代码开发的前置门（编写早、执行晚）；缺失即被 SDD Flow T3 拒绝。约束的落地形态见 `tasks.md`。
```
Hmm the finding says design 只保留设计约束结论或一句指向 tasks 的约束. Good.
- §0 add F003/F008 upstream contract lines + calendar ownership.
- §1 add `reports/holdout_budget/` storage.
- §2 模块放置 add upstream contract adapter + holdout ledger + concurrency; add ingestion points.
- §3.1 add `sample_tier`? No, that's report. Add `universe_calendar_digest` composition note.
- §3.2 directory: add `holdout_budget/ledger.jsonl`; note canonical=`reports/bench/`.
- §3.3: add glossary table (D011), stage IDs (D021), failure taxonomy schema (D021), report fields `approximation` (D014), `sample_tier` (D006), `promotion_verdict` only in cohort_verdict, final-confirmation exclusion (D019).
- §4 CLI: split `--universe`/`--calendar` (D004); add F003 contract section (D002).
- §5: add concurrency/fault-injection notes (D012), three-layer no-lookahead (D005).
- §6: F005 via API only (D018).
- §7: failure mapping + sample tiers (D006), L2/L3 blocking, final confirmation window fail-closed (D019), placeholder rules (D017).
- §8: add missing test files (D020), real env row (D009), property test constraints (D025), mutation artifact (D015), SC-002 concurrency (D012), batch fixture (D013), AC-new rows.
- §9: decisions rows for second implementation (D016 carrier), sample tiers? etc.

### tasks.md changes

- frontmatter related_features: [F002, F003, F004, F008]; updated.
- §0: add 执行规则 for [TEST] group + property test + mutation artifact.
- §1 T001: extend to include F003/F008 ingestion contracts.
- §2 T014: add funnel first-level ingestion from F003.
- §2 add T? for holdout ledger: put in Phase 2 as T0xx. Hmm, adding a task requires renumber or insert. Renumbering all tasks is risky/noisy. Alternative: extend existing tasks to carry new work:
  - D010 holdout ledger → extend T012 (registration/population) with holdout ledger append-only + preview rejection. T012 is `FR-004, DR-004, TR-003, NFR-001`. Add DR-005 → T012. Good, no renumber.
  - D012 concurrency → new task. Could extend T012? The reviewer said "增并发/故障注入集成测试任务". A test task in §3 → I'll add T024.
  - D016 second implementation → T025.
  - D025 property tests → T026.
  - D024? (原 T024) → T027 回写.
  Actually renumbering the existing T024 → T027 and appending T024-T026 is clean: T024/T025/T026 in §3 before T027. Wait but that changes "T024" id semantics; the only reference to T024 elsewhere is... §4 doesn't reference T024. Fine.
  
  Hold on: T023 is 统一质量门 and T024 was 回写. If I insert new tasks T024-T026 in §3 and move 回写 to T027, then the order in §3 becomes T018...T023, then T024/T025/T026, then T027. Fine.

  - D021 five-stage schema → T014 (already) + T007 (stage model). Extend T007 with stage ID enum, T014 with failure taxonomy schema.
  - D006 sample tiers → T010 extend ("样本量三级裁决").
  - D015 → T017/T021 text + verify artifact.
  - D014 approximation → T015 extend.
  - D020 → design §8 only (already covered by adding rows).
  - D022 → T006 (CLI 首屏) + T015 (POSIX path) extend.
  - D004 → T001 extend with two-artifact split.
  - D003 → T001 (F008 universe) extend.
  - D005 → T008 methodology gate L1 + new invariant; add to T023? I'll add a line in T008 to record three-layer state in manifest, and a §3 T026? No, keep: T008 extend "并在 manifest 记录三层无前视状态（L2/L3 owner=F006，缺证据不得晋级）".
  - D017 placeholder → T001/T008? Put in T007 or T001. I'll extend T007 with signal source provenance + placeholder fail-closed rule for canonical.
  - D019 final confirmation window → T003 (capability fixtures) extend.
  - D009 real env → T022 extend.
  - D001 [TEST] group → add `### [TEST] 组` heading with T028/T029/T030? Since [TEST] tasks are journey acceptance, I'll add T028 (US-001 journey), T029 (US-002), T030 (US-003) — then max id = T030 and T027 (回写) needs... wait T027 must be last? If [TEST] group is in §3 and 回写 T027 comes after, max = T030 > T027. Then gate requires max (T030) to have incoming edges; and T027's edge T0xx->T027 is forward (T027>T026) fine. But logically 回写 should be after [TEST] journeys. F003 has [TEST] T036-T038 then T039 回写 at the end. Let me mirror: [TEST] group tasks placed at the END of §3, then 回写 last. So: §3 order: T018, T019, T020, T021, T022, T023, then `### [TEST] 组：层 2 旅程验收轨（必填）` with T024-T026, then T027 并发/故障注入? Hmm.

Let me design the final task id map cleanly:
- T001–T023 unchanged (T018–T023 in §3).
- §3 adds:
  - T024 并发/故障注入集成测试（SC-002, AC-001/AC-003）— D012
  - T025 统计第二实现对照抽查（time-box 1 周）— D016
  - T026 属性测试轨（身份稳定/快照敏感性，固定 seed）— D025
- `### [TEST] 组：层 2 旅程验收轨（必填）` heading then:
  - T027 [TEST] US-001 旅程验收 — D001
  - T028 [TEST] US-002 旅程验收
  - T029 [TEST] US-003 旅程验收
- T030 回写 spec 验收证据、BACKLOG 与状态 (原 T024)

Max = T030. Edges needed into T030. Also T024/T025/T026 need predecessors? The gate only requires max to have incoming edge, plus edge endpoints defined and forward. But for correctness I'll add explicit edges.

§4 edges to add:
- `T009 -> T012` (D007)
- `T012 -> T013` (D007)
- `T007 -> T010/T011` (D008)
- `T012/T014 -> T016` (D008)
- `T012/T013 -> T024` (concurrency needs claim + CLI)
- `T009/T016 -> T025` (second impl compares against canonical statistics evidence)
- `T004/T019 -> T026` (property track: identity + property runs)
- `T016/T017/T022/T023/T024/T025/T026 -> T027/T028/T029` — hmm [TEST] journeys need the acceptance suites + real evidence. F003 pattern: `T030..T035 -> T036/T037/T038`. I'll write `T016/T017/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029`.
- `T027/T028/T029 -> T030` (回写 last).

Check forward: T012->T013 ✓ (12<13), T009->T012 ✓, T007->T010/T011 ✓, T012/T014->T016 ✓, T012/T013->T024 ✓, T009/T016->T025 ✓, T004/T019->T026 ✓ (4<26, 19<26), ...->T027/T028/T029 ✓, T027/T028/T029->T030 ✓.
Check `[P]`: only T005 is [P]; no edge targets T005. ✓
Check max T030 has incoming ✓.

Careful: the parser splits each backticked segment. Multi-hop in one segment like `T007 -> T010/T011` works. And `T016/T017/T018/... -> T027/T028/T029` expands 11×3 = 33 edges. Fine.

Hmm one issue: the [TEST] group tasks include `[TEST]` marker; parse_task_lines checks `"[P]" in line` — "[TEST]" doesn't contain "[P]"... wait, does "[P]" appear in "[TEST]"? No. OK.

But careful: `[TEST]` — the string "[P]" is not a substring. Fine.

Another: `check_task_dag.parse_task_lines` uses `TASK_RE = ^-\s+\[[ xX]\]\s+(T\d{3})` — line `- [ ] T024 [TEST] (...)` matches ✓.

Also §0 执行规则 in tasks should mention property tests and mutation artifact? I'll add.

### tools/check_doc_consistency.py additions

Add F007 constants and checks. For each finding:

D001 → check `f007_test_group_present` requires F007_TASKS "### [TEST] 组：层 2 旅程验收轨"... hmm, but the review's proposed test name was `tools/validate_spec_lifecycle.py::test_test_group_required` (the existing gate). The `[TEST]` gate is generic but only enforced for non-draft statuses. To make the F007 fix mutation-testable now, add a check requiring the F007 tasks [TEST] group. I'll add both: TEXT_CHECKS entry `f007_test_group_present` (requires `### [TEST] 组` and `T027 [TEST]`) with finding F007-D001.

Let me define each check with distinctive needles:

1. D001 `f007_test_group_present`: requires (F007_TASKS, "### [TEST] 组：层 2 旅程验收轨"), (F007_TASKS, "US-001 旅程端到端验收") — hmm I'll use stable literals. Let me define the [TEST] task texts now and use a substring.
2. D002 `f007_ingests_f003_contracts`: requires (F007_DESIGN, "generation.run_completed"), (F007_DESIGN, "generation.candidate_rejected"), (F007_DESIGN, "算子能力登记表"), (F007_TASKS, "generation.candidate_rejected"), (F007_DESIGN, "F003"), (F007_TASKS, "F003").
3. D003 `f007_declares_f008_universe`: requires (F007_SPEC, "F008"), (F007_SPEC, "universe_at(T)"), (F007_DESIGN, "F008"), (F007_TASKS, "F008").
4. D004 `universe_calendar_artifacts_split`: requires (F007_DESIGN, "lake/_metadata/universes/"), (F007_DESIGN, "--calendar"), (F007_DESIGN, "--universe"), (F007_SPEC, "`universe_at(T)`"), and forbids (F007_DESIGN, "--universe-calendar"), (F007_DESIGN, "universe_calendars/<digest>.json")? Careful: ADR-0007 owns `reports/research_snapshots/_inputs/universe_calendars/<digest>.json` as the calendar path — that's ADR-owned and still valid for the calendar JSON. Hmm! ADR-0007:72-74 says "调用方提供的 universe/calendar JSON 由 experiment_store 规范化并保存于 reports/research_snapshots/_inputs/universe_calendars/<digest>.json". If I split, the calendar JSON stays at that path (ADR-compliant), while universe comes from F008's CSV in the lake. So design should keep `universe_calendars/<digest>.json` for calendar only, and add the F008 universe digest ref. So forbid only the combined CLI flag `--universe-calendar`. Good — fewer contradictions with the ADR.

   Hmm, but the path name `universe_calendars/` for calendar-only is a bit odd but ADR-mandated. I'll keep it and note it holds calendar only. Good.
5. D005 `no_lookahead_three_layers_owned`: requires (F007_SPEC, "无前视三层"), (F007_SPEC, "独立逐 K 线重放"), (F007_SPEC, "信号缓存"), (F007_DESIGN, "owner=F006"), (F007_TASKS, "无前视三层").
6. D006 `sample_size_three_tiers`: requires (F007_SPEC, "provisional"), (F007_SPEC, "trustworthy"), (F007_SPEC, "underpowered"), (F007_DESIGN, "provisional"), (F007_TASKS, "三级样本量").
7. D007 `task_graph_missing_edges_f007`: requires (F007_TASKS, "`T009 -> T012`"), (F007_TASKS, "`T012 -> T013`").
8. D008 `full_chain_controls_have_predecessors`: requires (F007_TASKS, "`T007 -> T010/T011`"), (F007_TASKS, "`T012/T014 -> T016`").
9. D009 `real_env_task_has_distinct_evidence`: requires (F007_TASKS, "ALPHAMILL_INTEGRATION=1"), (F007_TASKS, "test_f007_controls_real.py"), (F007_SPEC, "ALPHAMILL_INTEGRATION=1"), (F007_DESIGN, "test_f007_controls_real.py").
10. D010 `holdout_budget_ledger_exists`: requires (F007_SPEC, "DR-005"), (F007_SPEC, "HoldoutBudgetLedger"), (F007_DESIGN, "holdout_budget"), (F007_TASKS, "DR-005"), and forbids? (F007_SPEC, "留出预算零变化")? no, keep it. Hmm the AC-001 clause keeps "留出预算零变化"? I'll rewrite AC-001 to include ledger zero rows. Fine.
11. D011 `verdict_vocabulary_frozen`: requires (F007_DESIGN, "promotion_verdict"), (F007_DESIGN, "NOT_APPLICABLE"), (F007_SPEC, "promotion_verdict"), (F007_DESIGN, "术语表").
12. D012 `sc002_concurrency_has_task`: requires (F007_TASKS, "SC-002"), (F007_TASKS, "故障注入"), (F007_DESIGN, "SC-002").
13. D013 `ac003_multi_member_batch`: requires (F007_TASKS, "多成员"), (F007_SPEC, "多成员"), (F007_DESIGN, "多成员 cohort").
14. D014 `nfr004_approximation_covered`: requires (F007_DESIGN, "approximation"), (F007_SPEC, "NFR-004"), (F007_TASKS, "approximation").
15. D015 `mutation_targets_labels_aligned`: requires (F007_TASKS, "mutation_report.json"), (F007_TASKS, "AC-001"), hmm too generic. Use: requires (F007_TASKS, "mutant"), (F007_DESIGN, "mutant"), (F007_TASKS, "变异工具"). Let me craft: T017 add "变异工具 pin 于 `pyproject.toml` 的 dev 依赖，产出 `reports/mutation/f007/mutation_report.json` 作为 mutant-killed 证据". So requires (F007_TASKS, "mutation_report.json"), (F007_TASKS, "变异工具 pin"), (F007_DESIGN, "mutation_report.json").
16. D016 `second_implementation_has_task`: requires (F007_TASKS, "第二实现"), (F007_TASKS, "time-box"), (F007_SPEC, "第二实现").
17. D017 `f004_to_f007_factor_source_contract`: requires (F007_DESIGN, "source=placeholder"), (F007_SPEC, "placeholder"), (F007_TASKS, "placeholder"), (F007_DESIGN, "signals_log").
18. D018 `f005_frontend_does_not_bypass_api`: requires (F007_DESIGN, "src/alphamill/api/"), (F007_DESIGN, "不得成为前端直读路径").
19. D019 `final_confirmation_window_hidden`: requires (F007_SPEC, "最终确认窗"), (F007_DESIGN, "最终确认窗"), (F007_SPEC, "fail-closed"), (F007_TASKS, "最终确认窗").
20. D020 `design_test_map_covers_tasks`: custom check — parse design §8 test file paths and tasks verify paths; assert tasks' test files ⊆ design §8. Good, write a custom check `check_f007_design_test_map`.
21. D021 `stage_ids_and_failure_dimensions_frozen`: requires (F007_DESIGN, "signal_quality"), (F007_DESIGN, "execution_implementation"), (F007_DESIGN, "failure taxonomy"→ maybe Chinese "失败维度"), (F007_SPEC, "signal_quality"), (F007_TASKS, "failure_taxonomy")? Let me use "five stage" needles: requires (F007_SPEC, "`signal_quality`"), (F007_DESIGN, "`signal_quality`"), (F007_DESIGN, "`execution_implementation`"), (F007_DESIGN, "三维失败"), (F007_TASKS, "failure_taxonomy").
22. D022 `nfr005_ux001_traceable`: requires (F007_SPEC, "NFR-005"), (F007_SPEC, "UX-001"), and AC line containing both — text check can just require the AC-011 line content: (F007_SPEC, "`UX-001`") appears already in AC-007. Hmm. Need to assert AC-011 references them: use custom AC check? Simpler: requires (F007_SPEC, "**AC-011** (`NFR-004`, `NFR-005`, `UX-001`)"). That literal is stable and mutation-testable. Good.
23. D023 `design_no_task_directives`: forbids (F007_DESIGN, "开工门禁（SDD Flow T3）会拒绝缺失该组的流转") and requires (F007_TASKS, "[TEST] 组"), (F007_TASKS, "层 2 旅程验收轨").
24. D024 `state_vocab_and_bench_mapping_aligned`: requires (F007_SPEC, "evaluation.registered"), (F007_SPEC, "`reports/bench/`"), (F007_DESIGN, "`reports/bench/`"), (F007_SPEC, "PREVIEW_DONE").
25. D025 `property_strategy_has_execution_task`: requires (F007_TASKS, "属性测试"), (F007_DESIGN, "可复现 seed"), (F007_TASKS, "seed").

Plus custom check D020.

And update tests: ALL_DOC_FILES must include F007_DESIGN, F007_TASKS. Also `test_unknown_check_id_absent_from_registry` is weird (asserts sorted list equals sorted set — trivially true) — leave.

Also I need to double check: TEXT_CHECKS currently use F003 SPEC/DESIGN/TASKS and F007_SPEC. Adding F007 DESIGN/TASKS constants is fine.

Careful: `test_required_text_removed_goes_red` uses `chk.requires[0]`, and `_materialize` copies ALL_DOC_FILES ∪ rels. If ALL_DOC_FILES includes F007 design/tasks, copies work.

But some requires point to F008/F004 files — I decided not to add those (all needles are in F007 files). Good, no extra deps. Except D004: needle "lake/_metadata/universes/" in F007_DESIGN ✓.

Now: forbidden needles must not appear anywhere in the file. E.g. D023 forbid "开工门禁（SDD Flow T3）会拒绝缺失该组的流转" — I'll delete that text from design. Careful with exact matching of the Chinese text.

D004 forbid "--universe-calendar" — must remove from design. ✓

Now, this is a LOT of work. Let me start executing. I'll create todos and go.

Given the volume, I'll aim to do it in a structured way but not over-verify each step. Let me write the spec.md edits first (they're the largest), then design, then tasks, then tool+tests.

Actually — I realize I should reconsider the "one finding one commit" requirement given I cannot do partial-file staging. Per-finding commits require editing only the files of that finding per commit. Multiple findings share spec.md, so sequential commits touching spec.md are fine (each commit = the hunks from that finding's edits, since I edit then commit immediately).

So: for each finding: make its edits → run `python tools/check_doc_consistency.py` (may fail for checks not yet added — so add the check in the same commit) → commit. That means the tool file gets touched in every commit. Fine.

Order: D001..D025. But some findings' checks require needles that other findings' edits introduce... no, each check only needs its own finding's needles. But a check might reference text that I only add in a later finding's edit. E.g. D013 requires "多成员 cohort" in design — I'll add in D013's edit. OK, self-contained per finding if I'm careful.

Hmm, but many edits cluster (e.g., design §3.3 gets touched by D006, D011, D014, D019, D021). I'll just make the edits in the relevant finding's turn.

To reduce risk of running out of context, I'll do the edits efficiently and avoid re-reading files (I have them in context).

Let me also reconsider: is committing actually wanted? "Only commit... when explicitly requested." The user said "按照skill要求" — the skill requires per-finding commits as fixer evidence. The prior F003 round did exactly that. I'll commit locally, not push. I'll note this.

Let me start. First, todos.

Let me write out the todo list (25 findings, grouped into batches to keep the list manageable — the todo tool wants atomic items; I'll make 25-ish items but that's heavy. Let me group into bundles matching commits: actually each finding = 1 commit = 1 todo. 25 todos is fine but verbose. I'll use 25 concise todos including WHERE/HOW/EXPECT.

Hmm, the todo format requirement: "[WHERE] [HOW] to [WHY] - expect [RESULT]". Let me write them concisely:
1. "F007 spec/design/tasks: 增 [TEST] 组 (D001) - expect validate_spec_lifecycle 的 [TEST] 门在 ready-for-development 下可过"
...

OK let me just do it. I'll write 25 todos.

Actually to save effort I'll create todos in 4 batches of ~6-7 while working. The tool requires the full list each time. Let me create the full 25 now — it's a single call.

Let me go. I'll write them in a compact but compliant form.

Let me now draft all the exact edits. I'll start with D001 + D023 (related), then D002, etc.

Wait, D023 (remove design:16-18) and D001 (add tasks [TEST] group) are related. I'll do D001 first (add [TEST] group to tasks), then D023 (remove design instruction), both as separate commits.

Let me write the D001 edit: tasks.md §3, after T026 (property) — no wait, I planned: T024 concurrency, T025 second-impl, T026 property, then [TEST] group T027-T029, then T030 回写. But those tasks come in later findings' commits (D012, D016, D025). If D001's commit adds the [TEST] group with T027-T029 and T030 回写, then later D012 adds T024... which would sit before T027 numerically but be added after in file order? I must maintain file order by task number. If I add T027-T030 first in file (§3 end), then later insert T024-T026 before the [TEST] heading — that's fine, file order preserved.

Alternatively, to avoid id churn: assign the new tasks ids AFTER the [TEST] group? No, [TEST] journeys should be near the end per F003 pattern (T036-T038 then T039 回写). But the DAG gate requires src<dst, so tasks must be numbered in execution order. If concurrency test task = T024, it's fine as long as it's placed before T027.

Plan: 
- D001 commit: insert `### [TEST] 组…` with T027/T028/T029 and change "T024: 回写" → "T030: 回写". Also add §4 edges for [TEST] → T030 and keep the existing edges. Check the tool: D001 check requires the [TEST] heading + journey text. And the §4 needs T030 to have incoming edges (gate only for non-draft but let's be consistent). So D001 commit adds `` `T027/T028/T029 -> T030` ``.
   Hmm but if I add `-> T030` edges and T030 exists, while T024-T026 don't exist yet — the edges I add must only reference existing tasks in that commit, else check_task_dag would complain (only when status non-draft, which it's not — so no gate error). But the D007/D008 checks I add later assert specific edge literals; fine.
   Also `parse_edges` would produce edges referencing undefined tasks — only flagged for enforced statuses. F007 is draft → not enforced. But to keep the repo clean, I'd rather add all edges consistently. Since the gate isn't enforced for draft, temporary inconsistency within intermediate commits is invisible; the final state must be consistent. FIX-log will only be checked at the end state. OK.

Simplest robust approach: make edits finding-by-finding in an order that keeps the final state consistent, and verify the FINAL state with the full gate. Intermediate commits may transiently have edges referencing later-added tasks (acceptable; the gate isn't run per-commit per the skill: "commit 之间不要求各自过全量门禁").

Good — that frees me. Order: I'll do spec/design/tasks edits for all findings, then checks, with commits per finding. But the checks are needed in the same commit as the finding. Hmm, "一个 finding 一个 commit" — the check for finding X should ideally be in X's commit (the F003 log shows regression tests as part of the fix). Yes.

OK, let me finally start writing. To be efficient, I'll do each finding as: edits (2-4 edit calls) + add check + run `python tools/check_doc_consistency.py` + commit. That's ~5 tool calls per finding → 125 calls. Too many. Let me compress: 
- I can add multiple TextCheck entries in one edit per gap... but they belong to different commits.

Alternative: reduce to a coarser commit granularity — group findings by theme (e.g., 5-6 commits), and document in FIX-log that commits group related findings. The skill says one finding one commit to preserve bisect. Hmm. Deviating weakens compliance.

Compromise: I'll do one commit per finding but batch tool calls aggressively:
- For each finding: one `edit` on spec (if needed), one `edit` on design, one `edit` on tasks, one `edit` on the tool (add check), then one bash (run check + git add + commit). That's up to 5 calls per finding. With 25 findings ≈ 90-110 calls. That's a lot but each is small. Context growth is the real concern.

Given context limits, maybe I should delegate most of the mechanical work. Let me reconsider delegation seriously:

Plan: I write a precise, complete "fix specification" document (the anchor decisions + exact required literals + exact task ids/edges), then delegate:
- Agent A (deep): apply spec.md edits for findings D003,D004,D005,D006,D007,D008,D009,D010,D011,D012,D013,D014,D015,D016,D017,D019,D020,D021,D022,D024,D025 (the spec-visible ones).
- Agent B: design.md edits.
- Agent C: tasks.md edits.
- Agent D: tool+tests.
Sequential (write) then D after A-C. Risk: agents produce inconsistent text and the TEXT_CHECKS needles mismatch. High risk, high verification cost.

Versus doing it myself: slower but correct. I think the middle ground is best: I do it myself for spec+design+tasks (semantic core, ~50 edits), then delegate the tool/tests extension to one agent with the exact needle list (mechanical, verifiable by running the gate), then verify.

But "one finding one commit" with me doing all edits... I'll accept fewer, well-scoped commits? Let me re-read the skill once more on this... "一个 finding 一个 commit：本地提交，保 bisect/revert 能力——批修出回归时无法定位是哪条修复引入的（9 个问题挤一个 744 行提交是实测反面案例）。commit 之间不要求各自过全量门禁".

The rationale is bisect capability for code regressions. For doc fixes, the "regression" is the gate check. I'll comply: one finding per commit. I'll aim for efficiency: per finding, do edits with as few `edit` calls as possible (each finding touches 2-3 files; use one edit per file, possibly multi-line blocks).

OK. Enough deliberation. Given the sheer size, I'll start and be efficient. Let me begin with the todo list, then D001.

Actually, let me reconsider scope/time. This is going to be a very long session. The user's ADHD-style guidance says lead with next action, number steps, keep it tight. I'll work through methodically.

Let me create the todos now.

For the todo list, I'll list 25 finding-level items. Let me write them.

Hmm, the todowrite schema wants content/status/priority. Let me produce 25 items with concise content including the where/how/expect.

Let me go.

Actually — one more consideration on ordering: it's cleaner to do the **tool check additions** as I go (one per finding), because each check's needles must exist. I'll do: edit docs → edit tool → run `python tools/check_doc_consistency.py` (fast, ~0.1s) → commit. For spec-only/design-only needles the check passes immediately.

But careful: `check_doc_consistency.py` runs ALL checks including the F003 ones; if I transiently break an F003 needle, it fails. I won't touch F003 files. ✓

Also note: run direct script instead of pytest for speed, and run the pytest mutation test file once at the end of the round (it auto-covers all TEXT_CHECKS).

Let me start.

D001 (tasks [TEST] group) + final task renumbering.

Let me write the [TEST] group text:

```
### [TEST] 组：层 2 旅程验收轨（必填）

> 编写早、执行晚：以下条目在 Phase 1 先以红灯立起，收尾全量执行；每旅程步骤 ≥1 条可执行断言。
> 缺失该组时 SDD Flow T3 开工门禁拒绝流转（见 `design.md` §0 约束）。

- [ ] T027 [TEST] (`US-001`, `AC-001`, `AC-011`): 旅程 US-001 端到端验收——对固定 fixture 连续执行两次 preview：报告字节级稳定（排除 provenance 时间戳）、canonical 台账与留出预算台账均为零行、preview 越权写 official population/留出被拒并留 `evaluation.gate_rejected`、CLI 首屏含 tier/data digest/首个失败原因、近似标注在报告中显式可见 — verify: `pytest -q tests/integration/test_f007_execution_tiers.py tests/integration/test_f007_cli.py`
- [ ] T028 [TEST] (`US-002`, `AC-002`, `AC-003`, `AC-004`, `AC-009`, `AC-010`, `AC-012`): 旅程 US-002 端到端验收——冻结 cohort 后跑正控制/白噪声/故意泄漏 canonical：正控制五阶段完整且样本量三级裁决正确、白噪声被统计门拦截、泄漏被方法论门拦截；成员未收齐时 finalize 非零且 cohort 保持 OPEN；拒绝者仍入分母（多成员批量夹具）；必需估计器异常时 stage 不为 PASS 且 `promotion_verdict` 不为 `promising`；manifest 记录三层无前视状态且最终确认窗统计量不出现在任何 Agent 可读产物 — verify: `pytest -q tests/unit/evaluation/test_required_statistics.py tests/unit/evaluation/test_cost_and_stability.py tests/unit/validation/test_methodology_gate.py tests/integration/test_f007_controls.py`
- [ ] T029 [TEST] (`US-003`, `AC-005`, `AC-007`, `AC-008`): 旅程 US-003 端到端验收——从 finalized canonical ledger 确定性重建 synthesis：拒绝者进入漏斗分母、五阶段损失按 stage/owner/mechanism 三维聚合、事实/推断/建议三栏齐备；只有 preview 产物时输出空 canonical 结果；report/curves 标量互推在容差内一致 — verify: `pytest -q tests/integration/test_f007_synthesis.py tests/contract/test_f007_artifact_schemas.py`
```

Hmm, this is long but good — it's derived from journey steps.

And renumber T024 → T030:
```
- [ ] T030: 回写 spec 的真实 tests/验收证据、BACKLOG 和 feature 状态 — verify: `python3 tools/verify.py`
```

And §4 add: `` `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。 ``

D001 check: requires (F007_TASKS, "### [TEST] 组：层 2 旅程验收轨"), (F007_TASKS, "US-001 端到端验收"), (F007_TASKS, "T030: 回写"). Hmm simpler: "### [TEST] 组：层 2 旅程验收轨" + "T029 [TEST]".

Let me now also plan D023: remove design lines 16-18; replace with a one-line constraint. Check forbids the old text.

OK, writing now. Let me create todos and execute D001.

For my own sanity, I'll batch: do the todo write + D001 edits + check + commit in one assistant turn (multiple tool calls, sequential dependencies mean separate messages).

Let me go. First: todowrite + first edits in parallel where independent (todo write, and the tasks.md edit for D001 — the edit needs the file read already done ✓).

I'll do todowrite and the tasks.md edits together, then tool edit, then bash.

Let me identify exact oldString for tasks.md T024 line:
```
- [ ] T024: 回写 spec 的真实 tests/验收证据、BACKLOG 和 feature 状态 — verify: `python3 tools/verify.py`
```
And insert [TEST] group before it? No — the [TEST] group should be a `###` heading inside §3; §3 currently has no ### headings. Put it after T023 and before T030 (the renumbered 回写). And T024-T026 (concurrency etc.) will be inserted before the [TEST] heading in later commits.

So D001 edit: replace the T024 line with:
```
### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T027 [TEST] (...)
- [ ] T028 [TEST] (...)
- [ ] T029 [TEST] (...)

- [ ] T030: 回写 spec ...
```
Wait, ordering: [TEST] group T027-T029 then T030 回写. But T024/T025/T026 will be inserted before the heading later. Good.

Hmm, numbering: if [TEST] tasks are T027-T029 and T030 is 回写, then where do concurrency/second-impl/property go? T024-T026 (before T027). Their commits come later (D012, D016, D025) and insert before the `### [TEST]` heading. But in D001's commit, T024-T026 don't exist yet while T030 exists — gap in numbering (T023 → T027). The `validate_spec_lifecycle` doesn't check task id continuity. check_task_dag doesn't either. Fine at final state too (all filled).

Actually wait: should I number [TEST] as T027-T029, or put [TEST] at T027-T029 leaving T024-T026 for the new tasks — final state T001..T030 contiguous. ✓.

§4 additions for D001: add edge into T030. I'll add in D001: `` - `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。 `` (T030 must be max at final state — yes T030 > T029 ✓.)

Let me now do it.

One more thing: `updated:` frontmatter dates. I'll bump spec/design/tasks `updated: 2026-09-17`. Do it in the first commit touching each file. Since D001 touches tasks, set tasks updated there. D002 touches design → set design updated there. D003 touches spec → set spec updated there.

Let me go.
Full picture acquired. Baseline `main@d659db7`, worktree clean. F007 review round 1 = 25 findings (8 High / 13 Med / 4 Low), all `open`. I'll fix as the fixer side: doc fixes + gate checks (regression evidence) + per-finding local commits + `FIX-log.md` declaration. Reviewer's `CURRENT-doc-F007.md` stays untouched.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "tasks.md: 增 ### [TEST] 组 T027-T029 并重编号回写任务 (D001) - expect [TEST] 门在 ready-for-development 下可过",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "design.md + tasks.md: 补 F003 摄入点/算子登记表/协同池契约 (D002) - expect design 有 F003 且 check 可红",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "spec.md + design/tasks frontmatter: 声明 F008 上游与 universe_at(T) (D003) - expect F007_D003 check 绿",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "spec/design: universe 与 calendar 拆两个 artifact 引用 (D004) - expect 无 --universe-calendar 合并flag",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "spec/design/tasks: 无前视三层归属+晋级阻断 (D005) - expect L2/L3 owner=F006 且阻断点写明",
    "status": "pending",
  
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:25:21Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "oldString": "- [ ] T024: 回写 spec 的真实 tests/验收证据、BACKLOG 和 feature 状态 — verify: `python3 tools/verify.py`\n\n## 4. 依赖与并行关系", "newString": "### [TEST] 组：层 2 旅程验收轨（必填）\n\n> 编写早、执行晚：以下条目在 Phase 1 先以红灯立起（夹具与断言先写），收尾全量执行；\n> 每个旅程步骤至少一条可执行断言。缺失该组时 SDD Flow T3 开工门禁拒绝流转。\n\n- [ ] T027 [TEST] (`US-001`, `AC-001`, `AC-011`): 旅程 US-001 端到端验收——固定 fixture 连跑两次 preview：报告在排除 provenance 时间戳后稳定、canonical 台账与留出预算台账均零行
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "oldString": "- `T005 [P]` 可与 T004 并行：分别修改隔离能力与纯身份模块，不共享状态。", "newString": "- `T005 [P]` 可与 T004 并行：分别修改隔离能力与纯身份模块，不共享状态。\n- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "oldString": "doc_kind: tasks\ncreated: 2026-09-13\nupdated: 2026-09-13", "newString": "doc_kind: tasks\ncreated: 2026-09-13\nupdated: 2026-09-17"})`


> [reasoning] Now execute D001. Edit tasks.md:
1. Insert [TEST] group + renumber T024→T030.
2. Add §4 edge.
3. Update frontmatter `updated`.
4. Add check to tool.
5. Run + commit.

Let me make the edits.
**D001** (High, `test-group-missing`) — 增 `[TEST]` 旅程验收组。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:25:31Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "F007_SPEC = \"docs/features/0.2/F007-evaluation-gates/spec.md\"\nF007_DESIGN = \"docs/features/0.2/F007-evaluation-gates/design.md\"\nF007_TASKS = \"docs/features/0.2/F007-evaluation-gates/tasks.md\"", "oldString": "F007_SPEC = \"docs/features/0.2/F007-evaluation-gates/spec.md\""})`


> [reasoning] Now add the check to tools/check_doc_consistency.py. I need to add F007 DESIGN/TASKS constants and a check entry.

Let me add constants after F007_SPEC and add the TextCheck entry at the start of TEXT_CHECKS? Order doesn't matter but tests parametrize; I'll append F007 checks at the end of TEXT_CHECKS for clarity, with a comment.

Let me write the edit.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 127 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:25:37Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "    TextCheck(\n        \"vendor_hygiene_has_upstream_baseline\",\n        \"F003-D021\",\n        requires=((SPEC, \"上游基线\"), (TASKS, \"_upstream_baseline.json\")),\n    ),\n    # ---- F007 文档检视 Round 1 修复断言（finding id 前缀 F007-D）----\n    TextCheck(\n        \"f007_test_group_present\",\n        \"F007-D001\",\n        requires=(\n            (F007_TASKS, \"### [TEST] 组：层 2 旅程验收轨\"),\n            (F007_T
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 128 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:25:45Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py", "newString": "ALL_DOC_FILES = {\n    cdc.SPEC,\n    cdc.DESIGN,\n    cdc.TASKS,\n    cdc.F007_SPEC,\n    cdc.F007_DESIGN,\n    cdc.F007_TASKS,\n}", "oldString": "ALL_DOC_FILES = {cdc.SPEC, cdc.DESIGN, cdc.TASKS, cdc.F007_SPEC}"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 13 nodes, 121 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:25:52Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"f007_test_group\" 2>&1 | tail -5"})`


> [reasoning] The third edit was a mistake ordering — I should have read the test file fully first; but I did read the first 80 lines which contained that exact line. Edit applied. Good.

Now run the check + the mutation test for the new check + commit.

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
..                                                                       [100%]
2 passed, 31 deselected in 0.11s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:00Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A docs/features/0.2/F007-evaluation-gates/tasks.md tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && git commit -q -m \"fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组并重编号回写任务\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
65e1832 fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组并重编号回写任务


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:07Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dataset/version/value digest\n- **F003 生成侧 Contract（只读摄入）**：`generation.run_completed`（仅 `status=completed` 的运行）与 `generation.candidate_rejected`（漏斗第一级）；算子能力登记表（FR-002 的方法论守卫已登记能力清单来源）；协同池 meta-factor（`generator=\"pool\"` 的可执行 `FactorDef`）", "oldString": "- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dat
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- `src/alphamill/evaluation/cli.py`：薄入口，不承载裁决逻辑。\n- `src/alphamill/evaluation/upstream_contracts.py`：只读摄入 F003 的 `generation.*` 事件、算子能力登记表与协同池 `FactorDef`；F007 不写 F003 运行记录，也不解析 vendor 内部结构。", "oldString": "- `src/alphamill/evaluation/cli.py`：薄入口，不承载裁决逻辑。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "### 上游 Contract（F003）\n\n- **漏斗第一级只读摄入**：`generation.run_completed` 只在 `status=completed` 的运行上消费；`generation.candidate_rejected` 按原因码（未登记算子 / 前视 / 可达性不足 / 重复定义）计数。两者共同构成漏斗第一级，拒绝者仍计入分母。\n- **算子能力登记表**：装载为方法论门的「已登记能力」清单；未登记 capability 默认拒绝（FR-002），因此守卫覆盖面随登记表单调增强。\n- **协同池**：以 `generator=\"pool\"` 的可执行 `FactorDef` 与普通因子走同一评测路径，不因来源或聚合形态获得豁免；其成员 `factor_id` 与权重作为 provenance 进入 manifest。\n-
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "related_features: [F002, F003, F004]\ntopics: [evaluation, validation, evidence, experiments]\ndoc_kind: design\ncreated: 2026-09-13\nupdated: 2026-09-17", "oldString": "related_features: [F002, F004]\ntopics: [evaluation, validation, evidence, experiments]\ndoc_kind: design\ncreated: 2026-09-13\nupdated: 2026-09-13"})`


> [reasoning] D001 done. Next D002: F003 ingestion into design/tasks + frontmatter.

design.md changes:
1. frontmatter related_features: [F002, F004] → [F002, F003, F004] (F008 comes in D003; but to avoid touching the same line twice, I could do both here — but D003 is a separate commit. I'll do F003 now and F008 in D003; the frontmatter line gets edited twice. Acceptable.)

Hmm, that creates churn but keeps commits finding-scoped. Fine.

2. §0 add F003 upstream contract line.
3. §2 add module + ingestion.
4. §4 add F003 contract block.
5. tasks: T001 extend + T014 extend.

Check `f007_ingests_f003_contracts`: requires (F007_DESIGN, "generation.run_completed"), (F007_DESIGN, "generation.candidate_rejected"), (F007_DESIGN, "算子能力登记表"), (F007_TASKS, "generation.candidate_rejected"), (F007_TASKS, "算子能力登记表"). Needles must be in files.

Let me write the design §0 line:
```
- **上游 Contract**：F002 `(dataset, DataVersion, value_digest)` reader 与 `symbol_map`；F004/Kronos 与人工因子的产物经显式适配为 `FactorDef`（见 §7）；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级，只消费 `status=completed`）、算子能力登记表（FR-002 的方法论守卫覆盖清单来源）与协同池 meta-factor（`generator="pool"` 的 `FactorDef`）
```
Current §0 line 24: `- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dataset/version/value digest`

I'll replace it with separate lines.

§2 module placement: add
```
- `src/alphamill/evaluation/upstream_contracts.py`：只读摄入 F003 `generation.*` 事件、算子能力登记表与协同池 `FactorDef`；不复制 F003 的写入路径；
```
§2 dependency direction sentence: add "bench 不消费 F003 vendor 内部结构，只消费其 schema_version 化产物。"

§4 new subsection "### 上游 Contract（F003 / F008 / F004）" — but §4 needs both F003 (D002) and F004 (D017) and F008 (D004). D002 adds the F003 part.

```
### 上游 Contract

- **F003 生成侧**：漏斗第一级只读消费 `generation.run_completed`（仅 `status=completed` 的运行）与 `generation.candidate_rejected`（按原因码计数）；算子能力登记表装载为方法论守卫的已登记能力清单（FR-002 的「已登记算子」判定源）；协同池以 `generator="pool"` 的可执行 `FactorDef` 与普通因子走同一评测路径，不因来源获得豁免。
- 摄入是只读的：F007 不写 F003 的运行记录，也不解析 vendor 内部结构（只按 `schema_version` 消费）。
```

Then tasks T001 extend: add "以及 F003 上游契约（`generation.*` 事件、算子能力登记表、协同池 FactorDef）与 F008 universe digest 的只读摄入".

Wait F008 是 D003. Keep D002 to F003 only. But T001 will be edited again in D003. Fine.

T014 extend: add "漏斗第一级摄取 F003 的 `generation.run_completed`（仅 completed）与 `generation.candidate_rejected`（按原因码）".

Let me make edits.
**D002** (High, `cross-feature-contract-drift`) — F003 摄入契约。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:22Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot builder/reader contract；builder 只接收显式 universe/calendar artifact，验证其内容摘要并在 provenance 保留不可变引用；preview latest 必须先冻结，canonical 只收 snapshot ID；同时实现 F003 上游只读摄入契约（`generation.run_completed`/`generation.candidate_rejected`、算子能力登记表、协同池 `FactorDef`）— verify: `
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T014 (`FR-006`, `AC-007`): 实现只消费 canonical 的 synthesis builder 与五阶段/三维失败汇总；漏斗第一级只读摄取 F003 的 `generation.run_completed`（仅 `status=completed`）与 `generation.candidate_rejected`（按原因码） — verify: `tests/integration/test_f007_synthesis.py`", "oldString": "- [ ] T014 (`FR-006`, `AC-007`): 实现只消费 canonical 的 synthesis builder 与五阶段/三维失败汇总 — verify: `tests/integration/test_f007_synthesis.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        forbids=((F007_TASKS, \"- [ ] T024: 回写 spec\"),),\n    ),\n    TextCheck(\n        \"f007_ingests_f003_contracts\",\n        \"F007-D002\",\n        requires=(\n            (F007_DESIGN, \"generation.run_completed\"),\n            (F007_DESIGN, \"generation.candidate_rejected\"),\n            (F007_DESIGN, \"算子能力登记表\"),\n            (F007_TASKS, \"generation.candidate_rejected\"),\n        ),\n   
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 129 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:31Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"f007_ingests\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && git commit -q -m \"fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
..                                                                       [100%]
2 passed, 33 deselected in 0.15s
ccf577d fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:39Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "related_features: [F002, F003, F004, F008]\ntopics: [evaluation, validation, evidence, experiments]\ndoc_kind: spec\ncreated: 2026-09-13\nupdated: 2026-09-17", "oldString": "related_features: [F002, F003, F004]\ntopics: [evaluation, validation, evidence, experiments]\ndoc_kind: spec\ncreated: 2026-09-13\nupdated: 2026-09-13"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **上游 Contract 来源（F008）**：point-in-time 宇宙台账内容寻址 artifact——`universe_at(T)` 语义查询与 digest（F008 `IR-002`）与 `schema_version`（F008 `IR-003`）；ResearchSnapshot 的 universe 摘要按显式 digest 引用，不解析 latest\n- **上游决策**：ADR-0003（门禁不降级）、ADR-0005（曲线侧车）、ADR-0006（证据边界与身份）、ADR-0007（ResearchSnapshot）", "oldString": "- **上游决策**：ADR-0003（门禁不降级）、ADR-0005（曲线侧车）、ADR-0006（证据边界与身份）、ADR-0007（ResearchSnapshot）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **DR-001**：`ResearchSnapshot` 应当按 ADR-0007 持久化 cutoff、精确 dataset/version/value-digest 成员、as-of/覆盖语义、symbol-map 与 universe/calendar 摘要；universe 摘要以 **F008** 的内容寻址台账 digest 与 `universe_at(T)` 语义为锚点（`IR-003` 的 `schema_version`），calendar 摘要由本 Feature 拥有的 calendar artifact 导出；缺失或 invalid 成员不得发布。", "oldString": "- **DR-001**：`ResearchSnapshot` 应当按 ADR-0007 持久化 cutoff、精确 dataset/version/value-
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- **F003 生成侧 Contract（只读摄入）**：`generation.run_completed`（仅 `status=completed` 的运行）与 `generation.candidate_rejected`（漏斗第一级）；算子能力登记表（FR-002 的方法论守卫已登记能力清单来源）；协同池 meta-factor（`generator=\"pool\"` 的可执行 `FactorDef`）\n- **F008 上游 Contract（只读摄入）**：point-in-time 宇宙台账内容寻址 artifact——按 digest 加载并提供 `universe_at(T)` 语义查询与 `schema_version`（F008 `IR-002`/`IR-003`）；F007 不实现宇宙扩容，也不解析 latest", "oldString
…[truncated])`


> [reasoning] D002 done. **D003**: F008 upstream.

spec.md:
- frontmatter related_features: [F002, F003, F004] → [F002, F003, F004, F008]
- §0 add F008 upstream contract bullet
- IR-002 already needs F008 reference — will rewrite in D004; but D003 requires IR-002 to explicitly reference F008 digest + universe_at(T). D003 check: requires (F007_SPEC, "F008"), (F007_SPEC, "universe_at(T)"), (F007_DESIGN, "F008"), (F007_TASKS, "F008").

So minimally: spec FR-00x or IR-002 mention F008 + universe_at(T); design §0/§2 mention F008; tasks mention F008.

design: §0 add line `- **F008 上游 Contract（只读摄入）**：point-in-time 宇宙台账 artifact 按 `IR-002` 的内容寻址 digest 与 `universe_at(T)` 查询消费（`IR-003` 的 `schema_version`）`

tasks: T001 mention F008. But T001 was just edited. I'll edit again adding F008 clause → "以及 F008 的 universe artifact digest 与 `universe_at(T)` 语义校验". Hmm — D004 will also touch T001. Let me do T001's F008 mention here and the two-artifact detail in D004.

spec §0: add bullet:
```
- **上游 Contract 来源（F008）**：point-in-time 宇宙台账内容寻址 artifact —— `universe_at(T)` 语义查询与 digest（F008 `IR-002`）、`schema_version`（F008 `IR-003`）
```
And IR-002 add: "…、F008 universe artifact digest（或可解析引用）…" — that's D004's rewrite. For D003, I can add to IR-002 the F008 reference now and refine in D004. Let me just include the F008 mention in IR-002 now: "preview 请求 latest 时必须显式提供不可变 symbol-map ref、日历 artifact 与 F008 universe artifact digest（`universe_at(T)` 语义）".

Hmm, that duplicates D004 work. Let me instead do D003 with a dedicated new DR or the §0 bullet + reuse `universe_at(T)` mention in DR-001: DR-001 says "universe/calendar 摘要". I'll edit DR-001 to: "universe 摘要（F008 artifact digest 与 `universe_at(T)` 语义锚点）与 calendar 摘要". Then D004 adds DR-006 for the split. Good — D003 gets `universe_at(T)` + F008 into DR-001 and §0; check passes.

Let me write edits.
**D003** (High) — F008 universe 上游声明。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:26:52Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "related_features: [F002, F003, F004, F008]", "oldString": "related_features: [F002, F004]"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "canonical 只收 snapshot ID；同时实现 F003 上游只读摄入契约（`generation.run_completed`/`generation.candidate_rejected`、算子能力登记表、协同池 `FactorDef`）与 F008 universe artifact 的 digest 加载及 `universe_at(T)` 语义校验 — verify: `tests/contract/test_f007_upstream_contracts.py`、`tests/unit/experiment_store/test_research_snapshot.py`", "oldString": "canonical 只收 snapshot ID；同时实现 F003 上游只读摄入契约（`generation.run_completed`/`
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        forbids=((F007_DESIGN, \"related_features: [F002, F004]\"),),\n    ),\n    TextCheck(\n        \"f007_declares_f008_universe\",\n        \"F007-D003\",\n        requires=(\n            (F007_SPEC, \"related_features: [F002, F003, F004, F008]\"),\n            (F007_SPEC, \"universe_at(T)\"),\n            (F007_SPEC, \"F008\"),\n            (F007_DESIGN, \"F008 上游 Contract\"),\n            (F007_TAS
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 130 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 130 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:27:01Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"f007_declares_f008\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && git commit -q -m \"fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
.                                                                        [100%]
1 passed, 35 deselected in 0.09s
5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:27:51Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **DR-006**：`UniverseCalendarBinding` 应当把 universe 与 calendar 拆为两个独立 artifact 引用：universe 按 **F008** `IR-002` 的内容寻址台账消费（`lake/_metadata/universes/<digest>.csv`，提供 `universe_at(T)` 语义），calendar 由本 Feature 拥有并规范化保存为内容寻址 JSON（`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`）；ADR-0007 的 `universe_calendar_digest` 由两者 digest 组合导出（不再等于单一 JSON 文件摘要），拆解关系写入 ResearchSnapshot 
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **IR-002**：canonical 评测只接受已发布 ResearchSnapshot ID 和可解析的 FactorDef/冻结 PortfolioDef 引用；preview 请求 latest 时必须显式提供不可变 symbol-map ref、**F008** universe artifact 引用与 calendar artifact 输入，builder **分别**校验 universe 的 `universe_at(T)` 语义与 calendar schema 后内容寻址冻结并返回 snapshot ID；任何 tier 都不直接接受任意数据库查询，缺失任一 artifact 即失败关闭。", "oldString": "- **IR-002**：canonical 评测只接受已发布 ResearchSnapshot ID 和可解析的 Fac
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-006** (`DR-001`, `DR-002`, `DR-006`, `NFR-002`): ResearchSnapshot 跨路径/codec 身份稳定；动态 latest 先冻结；成员/cutoff/映射日历或实验语义变化使相应身份变化并可 supersede；universe（F008 digest + `universe_at(T)`）与 calendar 两个 artifact 引用分别校验，缺失或 digest 不符即拒绝发布", "oldString": "- [ ] **AC-006** (`DR-001`, `DR-002`, `NFR-002`): ResearchSnapshot 跨路径/codec 身份稳定；动态 latest 先冻结；成员/cutoff/映射日历或实验语义变化使相应身份变化并可 supersede"})`


> [reasoning] Note: only 1 test matched for D003 (requires only, no forbids) — good, mutation test for required text removal exists.

Wait, "1 passed, 35 deselected" — the parametrized `test_required_text_removed_goes_red` for this check ran... `-k f007_declares_f008` selects the parametrized test with that id (1 test) — for requires-only checks, only `test_required_text_removed_goes_red` is generated. Good.

**D004**: split universe/calendar artifacts.

Edits:
1. spec IR-002 rewrite (F008 universe digest + calendar separate).
2. spec DR-006 new entity for UniverseCalendarBinding (or edit DR-001 done). I'll add DR-006.
3. design §4 CLI: split `--universe-calendar <path>` into `--universe <digest|ref>` and `--calendar <path>`.
4. design §4 text about builder saving universe_calendars/<digest>.json — clarify it holds calendar only; universe read from F008 lake artifact.
5. design §3.1/§3.2? The research snapshot dir is in §3.2 `research_snapshots/`. Add `_inputs/universes/`? No — universe artifact lives in lake (`lake/_metadata/universes/<digest>.csv`), owned by F008. The snapshot provenance references it. So design text: provenance references F008 lake path + calendar JSON path.
6. design §5 step 1: "把显式 universe/calendar JSON 内容寻址保存后" → update.
7. AC-006 add DR-006 ref.
8. tasks T001: refine (already mentions F008) → add split detail: `--universe`/`--calendar` two refs.

Check `universe_calendar_artifacts_split`: requires (F007_DESIGN, "lake/_metadata/universes/"), (F007_DESIGN, "--calendar"), (F007_DESIGN, "--universe "), (F007_SPEC, "DR-006"); forbids (F007_DESIGN, "--universe-calendar"), (F007_TASKS, "--universe-calendar").

Let me write the spec DR-006:
```
- **DR-006**：`UniverseCalendarBinding` 应当把 universe 与 calendar 拆为两个独立 artifact 引用：universe 按 F008 `IR-002` 的内容寻址台账消费（`lake/_metadata/universes/<digest>.csv`，提供 `universe_at(T)` 语义），calendar 由本 Feature 拥有并规范化保存为内容寻址 JSON（`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`）；ADR-0007 的 `universe_calendar_digest` 字段由两者 digest 组合导出（不再等于单一 JSON 文件摘要），拆解关系写入 ResearchSnapshot provenance。
```
Careful: ADR-0007 says universe_calendar_digest is hashed into snapshot_id (decision 3). Composite digest preserves that. Good.

IR-002 rewrite:
```
- **IR-002**：canonical 评测只接受已发布 ResearchSnapshot ID 和可解析的 FactorDef/冻结 PortfolioDef 引用；preview 请求 latest 时必须显式提供不可变 symbol-map ref、F008 universe artifact digest（或可解析引用）与 calendar artifact 输入，builder 分别校验 universe 的 `universe_at(T)` 语义与 calendar schema 后内容寻址冻结并返回 snapshot ID；任何 tier 都不直接接受任意数据库查询。
```

design §4 CLI: the second preview block:
```
python -m alphamill.evaluation preview \
  --factor <factor-ref> --latest <dataset,...> --cutoff <UTC> \
  --symbol-map <digest> --universe <digest|ref> --calendar <path> \
  --config <path> --seed <int>
```
And the following paragraph:
```
CLI 仅解析参数和序列化结果；preview 的 `--latest` 模式要求显式 symbol-map digest、F008 universe artifact 引用与 calendar 输入。universe 按 F008 `IR-002` 从 `lake/_metadata/universes/<digest>.csv` 加载并走 `universe_at(T)` 语义，不复制进 reports；calendar 由 builder canonicalize 后原子保存为 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`（该路径只承载 calendar，universe 不再合并进此文件），再发布 ResearchSnapshot 并显示实际 ID；`--snapshot` 模式不重新选择这些输入。
```

Hmm "不再合并进此文件" — forbids f007_design "--universe-calendar" only. Fine.

design §5 step 1:
```
1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围、F008 universe artifact（`universe_at(T)` 语义与 digest）与不可变 symbol-map artifact，并把显式 calendar 输入内容寻址保存后，原子发布 snapshot。
```

AC-006: add DR-006: `- [ ] **AC-006** (`DR-001`, `DR-002`, `DR-006`, `NFR-002`): ...`

Also §3.1 identity: `research_snapshot_id` covers universe_calendar_digest; add note that composite. Let me add to §3.1 sentence: "`universe_calendar_digest` 是 universe（F008）与 calendar（F007）两个 artifact digest 的组合摘要".

tasks T001: add "builder 区分 `--universe`（F008 台账 digest，`universe_at(T)`）与 `--calendar`（本 Feature calendar JSON）两个引用".

Let me apply.
**D004** (High) — universe / calendar 两 artifact 拆分。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:28:16Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "python -m alphamill.evaluation preview \\\n  --factor <factor-ref> --latest <dataset,...> --cutoff <UTC> \\\n  --symbol-map <digest> --universe <digest|ref> --calendar <path> \\\n  --config <path> --seed <int>", "oldString": "python -m alphamill.evaluation preview \\\n  --factor <factor-ref> --latest <dataset,...> --cutoff <UTC> \\\n  --symbol-map <digest> --universe-calendar <path> --c
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "CLI 仅解析参数和序列化结果；preview 的 `--latest` 模式要求显式 symbol-map digest、**F008** universe artifact 引用（`--universe`）与 calendar 输入（`--calendar`）两个独立参数。universe 按 F008 `IR-002` 从 `lake/_metadata/universes/<digest>.csv` 加载并走 `universe_at(T)` 语义，**不复制进 reports**；calendar 由 builder canonicalize 后原子保存为\n`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`（该路径只承载 calendar，universe 不合并进此文
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围、**F008 universe artifact**（digest 与 `universe_at(T)` 语义）、不可变 symbol-map artifact，并把显式 calendar 输入内容寻址保存后，原子发布 snapshot。", "oldString": "1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围和不可变 sym
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "`experiment_id` 只哈希 upstream ID、cohort、规范化\n规则/窗口/成本配置、research_snapshot_id、code/build digest 与 seed。`universe_calendar_digest` 是 universe（F008 台账 digest）与 calendar（本 Feature calendar JSON digest）两个 artifact 的组合摘要。", "oldString": "`experiment_id` 只哈希 upstream ID、cohort、规范化\n规则/窗口/成本配置、research_snapshot_id、code/build digest 与 seed。"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:28:26Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "canonical 只收 snapshot ID；builder 区分 `--universe`（F008 台账 digest，`universe_at(T)` 语义）与 `--calendar`（本 Feature calendar JSON）两个独立引用并分别校验；同时实现 F003 上游只读摄入契约", "oldString": "canonical 只收 snapshot ID；同时实现 F003 上游只读摄入契约"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"universe_at(T)\"),\n        ),\n    ),\n    TextCheck(\n        \"universe_calendar_artifacts_split\",\n        \"F007-D004\",\n        requires=(\n            (F007_SPEC, \"DR-006\"),\n            (F007_DESIGN, \"lake/_metadata/universes/\"),\n            (F007_DESIGN, \"--calendar <path>\"),\n            (F007_DESIGN, \"--universe <digest|ref>\"),\n        ),\n        forbids=
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 131 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:28:34Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"universe_calendar\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
..                                                                       [100%]
2 passed, 36 deselected in 0.11s
b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:28:44Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- 不实现 F005 研究控制台，F007 只提供其只读真相源。\n- 不实现无前视 L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳对齐）的审计器——owner 为 F006/M3；F007 只消费其证据并在缺失时于晋级前失败关闭（`FR-007`）。", "oldString": "- 不实现 F005 研究控制台，F007 只提供其只读真相源。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- 离线到决策时 parity、run_record、kill-switch 与启动对账，以及**无前视 L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳与陈旧度对齐）的审计器实现** → F006/M3；F007 只消费其证据，并在 L2/L3 非 `PASS` 时于晋级前 fail-closed 阻断（`FR-007`、`AC-009`、PRD FR3.6 / SOP 原则 3）。", "oldString": "- 离线到决策时 parity、run_record、kill-switch 与启动对账 → F006/M3；"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "### Requirement: 无前视三层归属与晋级阻断（`FR-007`）\n\n系统应当把 PRD FR3.6 的三层无前视防线显式归属：**L1 = AST 纯度与未来算子门**（因子定义层）由 F007 方法论守卫在评测入口复检并 fail-closed（执行者在 F003 生成侧）；**L2 = 独立逐 K 线重放审计**（策略层）与 **L3 = 信号缓存 merge/join 时间戳与陈旧度对齐**（数据层）的 owner 为 F006/M3，F007 不重复实现。manifest 必须逐层记录状态（`PASS` / `FAIL` / `not_yet_available`）与证据引用，缺失层携带 owner。**L2/L3 未取得通过证据前，任何成员或组合不得晋级 paper**：状态不得记 `PASS`，也不得静默省略。\n\n#### Scenari
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- 历史证据不覆盖；变化产生新 ID，并通过 supersedes 表达替代关系。\n- 无前视三层归属显式：L1 由本 Feature 方法论守卫 fail-closed 执行；L2/L3 owner 为 F006/M3，非 `PASS` 前不得晋级 paper，缺失层记 `not_yet_available` 并携带 owner（`FR-007`）。", "oldString": "- 历史证据不覆盖；变化产生新 ID，并通过 supersedes 表达替代关系。"})`


> [reasoning] **D005**: no-lookahead three layers.

spec.md:
1. §1 非目标 add a line? Add:
```
- 不实现策略层逐 K 线重放器与信号缓存时间戳对齐审计（owner=F006/M3），但必须在晋级前阻断，见 FR-007；
```
2. §3 范围外 edit the F006 line to name L2/L3.
3. §4 add FR-007.
4. §5 不变量 add.
5. §6 add AC-009.
6. §7 决策与风险 add row.

design.md:
1. §5 or §7 add three-layer ownership + blocking.
2. §4? Put a subsection in §7.
3. §8 AC-009 row.

tasks:
1. T008 extend to record three-layer state in manifest.
2. §4 edge: `T008 -> T023`? Not needed. Maybe add to T023 verify? The finding wants explicit 承接. Add to T008 and to a §3 task. Let me extend T008 + T023 (quality gate) mention. Actually the D005 check requires (F007_TASKS, "无前视三层").

Let me write FR-007:
```
### Requirement: 无前视三层归属与晋级阻断（`FR-007`）

系统应当把 PRD FR3.6 / SOP 原则 3 的三层无前视防线显式归属：**L1 = AST 纯度与未来算子门**（因子定义层，执行者在 F003 生成侧，F007 方法论守卫在评测入口复检并 fail-closed）；**L2 = 独立逐 K 线重放审计**（策略层）与 **L3 = 信号缓存 merge/join 时间戳与陈旧度对齐**（数据层）的 owner 为 F006/M3。manifest 必须逐层记录状态（`PASS` / `FAIL` / `not_yet_available`）与证据引用，并携带缺失层的 owner。**L2/L3 未取得通过证据前，任何成员或组合不得晋级 paper**；缺失层记为 `not_yield_available`... 
```
careful typo. Use `not_yield_available`? No — `not_yet_available`.
```
不得记 `PASS`，也不得静默省略。
```
Scenario:
```
#### Scenario: 只有 L1 通过时不得晋级
- GIVEN 一个 canonical 成员仅 L1 通过，L2/L3 记 `not_yet_available`（owner=F006）
- WHEN 请求晋级 paper
- THEN 请求被拒绝（阻断点在 F007 manifest 的三层状态校验），拒绝事件含缺失层与 owner
```

§3 范围外 F006 line:
```
- 离线到决策时 parity、run_record、kill-switch 与启动对账，以及**无前视 L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳对齐）的审计器实现** → F006/M3；F007 只消费其证据，并在 L2/L3 缺失时于晋级前 fail-closed 阻断（`FR-007`、`AC-009`）。
```

§5 不变量 add:
```
- 无前视三层归属显式：L1 由本 Feature 方法论守卫 fail-closed 执行；L2/L3 owner 为 F006/M3，未取得通过证据前不得晋级 paper，缺失层记 `not_yet_available` 并携带 owner（`FR-007`）。
```

AC-009:
```
- [ ] **AC-009** (`FR-007`): 三层无前视状态逐层进入 manifest；L1 fail-closed 生效（未来算子负例被拒）；L2/L3 在缺证据时阻断晋级且拒绝事件携带缺失层与 owner；任何情况下不得把缺失层记为 PASS 或静默省略
```

§7 决策与风险 add row:
```
| 无前视 L2/L3 归属 | F007 不实现审计器；owner=F006/M3，晋级前以三层状态 + fail-closed 门阻断 | 逐 K 线重放与信号缓存对齐属策略/数据层，重复实现会产生第二真相源 | F006 落地后 F007 只接线其审计证据 |
```

design §7 add:
```
**无前视三层归属**：L1（AST 纯度与未来算子）由 MethodologyGate 在评测入口 fail-closed 执行；L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳与陈旧度对齐）的 owner=F006/M3，F007 不实现审计器。manifest 的 `no_lookahead` 段逐层记录 `status`（`PASS`/`FAIL`/`not_yet_available`）与 `evidence_refs`，缺失层带 `owner`；`promotion_verdict=promising` 与任何 paper 晋级请求在 L2/L3 非 `PASS` 时失败关闭（`E_REQUIRED_METRIC_FAILED`）。
```

design §8 add row:
```
| `AC-009` | unit + integration | `tests/unit/validation/test_methodology_gate.py`、`tests/integration/test_f007_execution_tiers.py` | 三层状态入 manifest；L2/L3 缺失时阻断晋级 |
```

tasks T008 extend + §4 edge? Let me extend T008: "...守卫 — verify: ...；同时在 manifest 写入三层无前视状态（L1 本 Feature 执行，L2/L3 owner=F006，缺失即阻断晋级）".

Also L2/L3 blocking is in T012? Not needed.

Check `no_lookahead_three_layers_owned`: requires (F007_SPEC, "FR-007"), (F007_SPEC, "独立逐 K 线重放"), (F007_SPEC, "信号缓存"), (F007_DESIGN, "owner=F006"), (F007_TASKS, "无前视三层").

Let me apply.
**D005** (High, `no-lookahead-layer-gap`) — 三层无前视归属 + 晋级阻断。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:28:58Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-008** (`IR-001`, `IR-002`, `IR-003`): CLI/schema 契约能拒绝非法 canonical 请求并返回结构化失败\n- [ ] **AC-009** (`FR-007`): 三层无前视状态逐层进入 manifest；L1 fail-closed 生效（未来算子负例被拒）；L2/L3 非 `PASS` 时阻断晋级且拒绝事件携带缺失层与 owner；任何情况下不得把缺失层记为 PASS 或静默省略", "oldString": "- [ ] **AC-008** (`IR-001`, `IR-002`, `IR-003`): CLI/schema 契约能拒绝非法 canonical 请求并返回结构化失败"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "| 统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查 | 门禁不能依赖会 warning 降级的黑盒 | ADR-0003 |\n| 无前视 L2/L3 归属 | F007 不实现审计器；owner=F006/M3，晋级前以三层状态 + fail-closed 门阻断 | 逐 K 线重放与信号缓存对齐属策略/数据层，重复实现会产生第二真相源 | F006 落地后 F007 只接线其审计证据 |", "oldString": "| 统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查 | 门禁不能依赖会 warning 降级的黑盒 | ADR-0003 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "统计函数不得 `except Exception -> warning/null`。可选 PBO/Reality Check/DML 诊断放独立\n`optional_diagnostics`，状态和失败原因可见，但其缺失既不能推翻硬门失败，也不能制造硬门通过。\n\n**无前视三层归属**：L1（AST 纯度与未来算子）由 MethodologyGate 在评测入口 fail-closed 执行；L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳与陈旧度对齐）的 owner=F006/M3，F007 不实现审计器。manifest 的 `no_lookahead` 段逐层记录 `status`（`PASS`/`FAIL`/`not_yet_available`）与 `evidence_refs`，缺失层带 `owner`；L2/L3 非 
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定 |\n| `AC-009` | unit + integration | `tests/unit/validation/test_methodology_gate.py`、`tests/integration/test_f007_execution_tiers.py` | 三层状态入 manifest；L2/L3 缺失时阻断晋级 |", "oldString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:29:24Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T008 (`FR-002`, `FR-007`, `AC-002`, `AC-009`): 实现 capability/guard 配对及 label endpoint/PIT/max-horizon/train-only-fit 守卫，并在 manifest 写入三层无前视状态（L1 本 Feature fail-closed 执行；L2/L3 owner=F006/M3，缺失层记 `not_yet_available` 并阻断晋级） — verify: `tests/unit/validation/test_methodology_gate.py`", "oldString": "- [ ] T008 (`FR-002`, `AC-002`): 实现 capability/guard 配对及 label endpoint/PIT/max-horizon
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        forbids=(\n            (F007_DESIGN, \"--universe-calendar\"),\n            (F007_TASKS, \"--universe-calendar\"),\n        ),\n    ),\n    TextCheck(\n        \"no_lookahead_three_layers_owned\",\n        \"F007-D005\",\n        requires=(\n            (F007_SPEC, \"FR-007\"),\n            (F007_SPEC, \"独立逐 K 线重放\"),\n            (F007_SPEC, \"信号缓存\"),\n            (F007_DESIGN, \"owner=F006\"),\
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 132 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:29:31Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"no_lookahead\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 失败
  - [no_lookahead_three_layers_owned] 缺少要求文本 '无前视三层'（docs/features/0.2/F007-evaluation-gates/tasks.md）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:29:37Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"三层无前视状态\"),", "oldString": "            (F007_TASKS, \"无前视三层\"),"})`


> [reasoning] The T008 edit text says "三层无前视状态" — the needle is "无前视三层". Let me fix the needle to match actual text "三层无前视状态" or change the check. I'll change the check needle to "三层无前视状态" (present in tasks and design? design says "无前视三层归属"). Use tasks-only needle: (F007_TASKS, "三层无前视状态").

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 132 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:29:45Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"no_lookahead\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
.                                                                        [100%]
1 passed, 38 deselected in 0.08s
59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:29:52Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "系统应当输出零成本/maker/taker 三档、资金费率、breakeven cost、换手、持有期与适用的容量代理，\n并以 purged/embargoed rolling split 记录选择期到留出的稳定性；成本后不为正时 verdict 为 `dead`。\n样本量按三级裁决（ADR-0003「样本量门槛」与 PRD FR3.5）：样本 `<30` 为 `sample_tier=underpowered`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口）；`30~69` 为 `provisional`（最多临时 PASS，仅允许缩减仓位进入 paper 并延长观察，不构成可信判定）；`≈≥69` 为 `trustworthy`（才允许完整成本后 PASS/FAIL 判定并计入北极星判据）。\n\n#### Scenario: 欠功效与临时 PASS 分
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-004** (`FR-005`): 三档成本、breakeven/换手/持有期和 rolling stability 完整，成本不存活者为 dead；样本量三级裁决正确（`<30` → `underpowered` 不判 PASS/FAIL、`30~69` → `provisional` 仅缩减仓位 paper、`≈≥69` → `trustworthy` 才可完整判定）", "oldString": "- [ ] **AC-004** (`FR-005`): 三档成本、breakeven/换手/持有期和 rolling stability 完整，成本不存活者为 dead"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "`report.json` 包含 identity refs、stage results、rank IC/HAC uncertainty、quantile/decay、dedup、\ncost/capacity、sample-size/stability、structured failure 与成员诊断 verdict。cohort 级 BH-FDR/DSR\n和可晋级 `promotion_verdict` 只存在于 `cohort_verdict.json`。每个阶段状态只能是\n`PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE`；`NOT_APPLICABLE` 需给原因，不能参与\n通过计数。\n\n`sample_tier` 三级（ADR-0003 样本量门槛）：`underpowered`（
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- 校验与失败映射：snapshot 成员/摘要/cutoff/映射日历不符 → `INCOMPLETE`；方法论/纯度门 → `FAIL`；统计估计器异常 →\n  `INCOMPLETE`；证据不足 → `UNDERPOWERED`（样本 `<30`，`sample_tier=underpowered`）；`30~69` 记 `provisional`，只允许缩减仓位 paper 且不得进入北极星判据；成本不存活 → `FAIL/dead`。", "oldString": "- 校验与失败映射：snapshot 成员/摘要/cutoff/映射日历不符 → `INCOMPLETE`；方法论/纯度门 → `FAIL`；统计估计器异常 →\n  `INCOMPLETE`；证据不足 → `UNDERPOWERED`；成本不存活 → `FAIL/dead`。"})`


> [reasoning] **D006**: sample size three tiers.

spec FR-005 extend + scenario. design §3.3 + §7 + §8. tasks T010.

spec FR-005 current:
```
### Requirement: 成本、容量与时间稳定性（`FR-005`）

系统应当输出零成本/maker/taker 三档、资金费率、breakeven cost、换手、持有期与适用的容量代理，
并以 purged/embargoed rolling split 记录选择期到留出的稳定性；成本后不为正时 verdict 为 `dead`。

#### Scenario: 高 IC 但成本不存活
...
```

Add after "成本后不为正时 verdict 为 `dead`。":
"样本量按三级裁决（ADR-0003 与 PRD FR3.5）：样本 `<30` → `sample_tier=underpowered`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口）；`30~69` → `provisional`（最多临时 PASS，仅允许缩减仓位进入 paper 并延长观察，不构成可信判定）；`≈≥69` → `trustworthy`（才允许完整成本后 PASS/FAIL 判定并计入北极星判据）。"

And scenario:
```
#### Scenario: 欠功效与临时 PASS 分离

- GIVEN 成本后均为正的三个候选，样本量分别为 25 / 50 / 80 笔
- WHEN canonical 裁决
- THEN 分别得 `sample_tier=underpowered` / `provisional` / `trustworthy`；`provisional` 的 `promotion_verdict` 不得被任何实盘前置引述，`underpowered` 不得记为 PASS
```

AC-004 add sample tier clause.

design §3.3 add: "`sample_tier`（`underpowered` | `provisional` | `trustworthy`）按 ADR-0003 三级裁决…" and report field.
design §7 failure mapping: 证据不足 → UNDERPOWERED — add "（样本 <30）; 30~69 为 `provisional`，只允许缩减仓位 paper".
design §8 AC-004 row: add three-tier assertion.
tasks T010: "实现 purged/embargoed rolling split、三级样本量裁决（underpowered/provisional/trustworthy）和稳定性报告".

Check `sample_size_three_tiers`: requires (F007_SPEC, "provisional"), (F007_SPEC, "trustworthy"), (F007_SPEC, "underpowered"), (F007_DESIGN, "provisional"), (F007_TASKS, "三级样本量").

Let me apply.
**D006** (High, `gate-without-teeth`) — 样本量三级裁决。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:30:11Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-004` | unit + golden | `tests/unit/evaluation/test_cost_and_stability.py` | 三档成本、breakeven、rolling split、三级样本量（`underpowered`/`provisional`/`trustworthy`）与 dead 裁决 |", "oldString": "| `AC-004` | unit + golden | `tests/unit/evaluation/test_cost_and_stability.py` | 三档成本、breakeven、rolling split 与 dead 裁决 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T010 (`FR-005`, `AC-004`): 实现 purged/embargoed rolling split、三级样本量裁决（`underpowered`/`provisional`/`trustworthy`）和稳定性报告 — verify: `tests/unit/evaluation/test_cost_and_stability.py`", "oldString": "- [ ] T010 (`FR-005`, `AC-004`): 实现 purged/embargoed rolling split、样本量裁决和稳定性报告 — verify: `tests/unit/evaluation/test_cost_and_stability.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"三层无前视状态\"),\n        ),\n    ),\n    TextCheck(\n        \"sample_size_three_tiers\",\n        \"F007-D006\",\n        requires=(\n            (F007_SPEC, \"sample_tier=underpowered\"),\n            (F007_SPEC, \"provisional\"),\n            (F007_SPEC, \"trustworthy\"),\n            (F007_DESIGN, \"sample_tier 三级\"),\n            (F007_TASKS, \"三级样本量\"),\n        ),\n    ),", "
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 133 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:30:22Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"sample_size\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 失败
  - [sample_size_three_tiers] 缺少要求文本 'sample_tier 三级'（docs/features/0.2/F007-evaluation-gates/design.md）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:30:29Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"三级（ADR-0003 样本量门槛）\"),", "oldString": "            (F007_DESIGN, \"sample_tier 三级\"),"})`


> [reasoning] The design text is "`sample_tier` 三级" with backticks around sample_tier. My needle "sample_tier 三级" doesn't match because of the backtick. Fix needle to "三级（ADR-0003 样本量门槛）".

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 133 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:30:38Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"sample_size\" 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
.                                                                        [100%]
1 passed, 39 deselected in 0.04s
36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:30:46Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。\n- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。", "oldString": "- `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"三级样本量\"),\n        ),\n    ),\n    TextCheck(\n        \"task_graph_missing_edges_f007\",\n        \"F007-D007\",\n        requires=(\n            (F007_TASKS, \"`T009 -> T012`\"),\n            (F007_TASKS, \"`T012 -> T013`\"),\n        ),\n    ),", "oldString": "            (F007_TASKS, \"三级样本量\"),\n        ),\n    ),"})`


> [reasoning] Progress: 6 of 25 done. Let me continue. **D007** and **D008** are task-graph edges — quick.

D007: add `T009 -> T012`, `T012 -> T013`.
D008: add `T007 -> T010/T011`, `T012/T014 -> T016`.

Both in §4. Since they're separate findings/commits, add D007's edges first, then D008's. Also add checks.

Note the check needle uses backticked text: (F007_TASKS, "`T009 -> T012`").

Let me put them as their own lines in §4.

Where to insert? After the existing `- \`T008,T009,T010 -> T011,T016,T017\`` line. Let me add:
- D007: `` - `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记与收齐校验实现。 ``
Hmm the parser: backticked segment contains "->" twice → hops = [T009, T012, T013] → edges T009->T012, T012->T013. Both forward ✓. And needle "`T009 -> T012`" appears as substring of "`T009 -> T012`：..." ✓ (the needle is exactly backtick T009 space arrow space T012 backtick — my text has "`T009 -> T012`" then "：". Yes substring matches.)

- D008: `` - `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry 与 synthesis。 `` → edges T007->T010, T007->T011, T012->T016, T014->T016. ✓ forward.

Checks: D007 requires "`T009 -> T012`" and "`T012 -> T013`"; D008 requires "`T007 -> T010/T011`" and "`T012/T014 -> T016`".

Let me apply both edits in sequence with two commits. Do D007 now.
**D007 / D008** (Medium, `task-graph-missing-edges`) — 补显式 DAG 边。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 134 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:08Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D007 补 T009->T012 与 T012->T013 依赖边\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
26c7b6d fix(f007): D007 补 T009->T012 与 T012->T013 依赖边


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:22Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。\n- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。", "oldString": "- `T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"`T012 -> T013`\"),\n        ),\n    ),\n    TextCheck(\n        \"full_chain_controls_have_predecessors\",\n        \"F007-D008\",\n        requires=(\n            (F007_TASKS, \"`T007 -> T010/T011`\"),\n            (F007_TASKS, \"`T012/T014 -> T016`\"),\n        ),\n    ),", "oldString": "            (F007_TASKS, \"`T012 -> T013`\"),\n        ),\n    ),"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 135 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:30Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。\n- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。", "oldString": "- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影
…[truncated])`


> [reasoning] The first edit failed — the file content differs. Let me check: the previous edit wrote "- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。" — it's one line, so "- `T012 -> T013`：finalize CLI..." isn't a standalone line start. Let me edit the whole line.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:36Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D008 补 T007->T010/T011 与 T012/T014->T016 依赖边\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
a0896fa fix(f007): D008 补 T007->T010/T011 与 T012/T014->T016 依赖边


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:41Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- 真实环境验证：在**执行机**的不可变 crypto 快照上以 `ALPHAMILL_INTEGRATION=1` 独立取证——独立命令 `tests/integration/test_f007_controls_real.py`，绑定 snapshot ID 与 `value_digest`，记录 hostname 与 `device=cpu`，证据落 `reports/f007/real_env/<run_id>/`；不得与 fixture 控制（`tests/integration/test_f007_controls.py`）共用同一命令或同一夹具充当真实环境证据（SOP §3）。", "oldString": "- 真实环境验证：在本机不可变 crypto 快照运行两个正控制；不需要交易所或 Freqtrade 联机。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定 |\n| `AC-001`/`AC-004` 真实环境 | real-env integration（执行机） | `tests/integration/test_f007_controls_real.py`，`ALPHAMILL_INTEGRATION=1` | 绑定不可变 snapshot ID/digest、记录 hostname；与 fixture 控制分属不同命令 |", "oldString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canoni
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T022 (`AC-001`, `AC-003`, `AC-004`, `AC-007`): 在**执行机**的不可变 crypto 快照跑四类正负控制并归档 manifest——绑定 snapshot ID 与 `value_digest`，证据落 `reports/f007/real_env/<run_id>/` 并记录 hostname 与 `device=cpu`；不得复用 T016 的 fixture 或命令 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f007_controls_real.py --snapshot <snapshot-id>`", "oldString": "- [ ] T022 (`AC-001`, `AC-003`, `AC-004`
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"`T012/T014 -> T016`\"),\n        ),\n    ),\n    TextCheck(\n        \"real_env_task_has_distinct_evidence\",\n        \"F007-D009\",\n        requires=(\n            (F007_TASKS, \"ALPHAMILL_INTEGRATION=1\"),\n            (F007_TASKS, \"test_f007_controls_real.py\"),\n            (F007_SPEC, \"ALPHAMILL_INTEGRATION=1\"),\n            (F007_DESIGN, \"test_f007_controls_real.py\"
…[truncated])`


> [reasoning] 8/25 done. **D009**: real-env T022 distinct evidence.

spec §7 测试策略 真实环境验证 line rewrite.
design §8 add real-env row / update.
tasks T022 rewrite.

Check: requires (F007_TASKS, "ALPHAMILL_INTEGRATION=1"), (F007_TASKS, "test_f007_controls_real.py"), (F007_SPEC, "ALPHAMILL_INTEGRATION=1"), (F007_DESIGN, "test_f007_controls_real.py").

tasks T022:
```
- [ ] T022 (`AC-001`, `AC-003`, `AC-004`, `AC-007`): 在**执行机**的不可变 crypto 快照跑四类正负控制并归档 manifest — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f007_controls_real.py --snapshot <snapshot-id>`，证据落 `reports/f007/real_env/<run_id>/` 并记录 hostname 与 `device=cpu`；不得复用 T016 的 fixture 或命令充当真实环境证据
```

spec §7:
```
- 真实环境验证：在**执行机**的不可变 crypto 快照上以 `ALPHAMILL_INTEGRATION=1` 独立取证（独立命令 `tests/integration/test_f007_controls_real.py`，绑定 snapshot ID 与 `value_digest`、记录 hostname 与 `device=cpu`、证据落 `reports/f007/real_env/<run_id>/`）；不得与 T016 的 fixture 控制共用同一命令或夹具充当证据（SOP §3）。
```

design §8: add row
```
| `AC-001`/`AC-004` 真实环境 | real-env integration | `tests/integration/test_f007_controls_real.py`（`ALPHAMILL_INTEGRATION=1`，执行机快照） | 独立 snapshot ID/digest 取证、hostname 记录；与 fixture 控制分开 |
```
And the line after the table mentioning fixtures: keep.

Let me apply.
**D009** (High) — T022 真实环境独立证据。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 136 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:51Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D009 T022 拆出执行机真实环境独立证据与集成命令\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
6b73c35 fix(f007): D009 T022 拆出执行机真实环境独立证据与集成命令


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:31:59Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **DR-004**：`CohortLedger` 应当保存预注册试验定义、选择阶段、全部候选和计数；preview 不得出现在 official population。\n- **DR-005**：`HoldoutBudgetLedger` 应当以 append-only 台账持久化每次留出评估（`candidate_id`、ISO 周、`experiment_id`、`cohort_id`、`verdict`、`recorded_at`、`execution_tier=canonical`）；只有 canonical capability 可追加，preview 越权写入必须被拒绝并写 `evaluation.gate_rejected`；台账与 manifest 同为可复现要件，不支持事后补记（ADR-0003 留出期使用预算）。", "oldString": 
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- GIVEN 一个 preview 运行上下文\n- WHEN 代码尝试登记 official population、追加留出预算台账或访问留出\n- THEN 操作失败，canonical 台账与留出预算台账均无变化并写入拒绝事件", "oldString": "- GIVEN 一个 preview 运行上下文\n- WHEN 代码尝试登记 official population 或访问留出\n- THEN 操作失败，canonical 台账无变化并写入拒绝事件"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-001** (`FR-001`, `DR-004`, `DR-005`, `NFR-003`): preview 越权被拒绝，正式台账与留出预算台账零变化（含「台账零行」正向断言与 preview 越权写入留出预算的负例）", "oldString": "- [ ] **AC-001** (`FR-001`, `DR-004`, `NFR-003`): preview 越权被拒绝，正式台账与留出预算零变化"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- 存储：`reports/preview/` 与 `reports/bench/` 隔离；`reports/cohorts/` 保存预注册 cohort 和事件；`reports/holdout_budget/ledger.jsonl` 为 append-only 留出预算台账（只有 canonical capability 可追加）。", "oldString": "- 存储：`reports/preview/` 与 `reports/bench/` 隔离；`reports/cohorts/` 保存预注册 cohort 和事件。"})`


> [reasoning] 9/25. **D010**: holdout budget ledger.

spec: add DR-005 (after DR-004); AC-001 add DR-005 + zero-row assertion; FR-001 scenario? The finding also wants a negative example (preview 越权写入留出预算须有负例) — FR-001 scenario already covers "代码尝试登记 official population 或访问留出". Extend to include 留出预算台账写入. Let me extend FR-001 scenario text: "WHEN 代码尝试登记 official population、写入留出预算台账或访问留出". And AC-001 clause.

design §3.2 dir add `holdout_budget/ledger.jsonl`; §1 存储 line; §5 note; §8 AC-001 row.
tasks T012 extend with DR-005.

Check: requires (F007_SPEC, "DR-005"), (F007_SPEC, "HoldoutBudgetLedger"), (F007_DESIGN, "holdout_budget"), (F007_TASKS, "DR-005"), (F007_TASKS, "留出预算台账").

Let me apply.
**D010** (High, `gate-without-teeth`) — 留出预算台账实体。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:00Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "```text\nreports/\n├── research_snapshots/<snapshot_id>/manifest.json\n├── holdout_budget/ledger.jsonl\n├── preview/<experiment_id>/<attempt_id>/{manifest.json,report.json,curves.parquet,events.jsonl}\n├── bench/<object_id>/<research_snapshot_id>/<experiment_id>/{manifest.json,report.json,curves.parquet,events.jsonl,registration.json}\n└── cohorts/<cohort_id>/\n    ├── cohort.json\n    
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T012 (`FR-004`, `DR-004`, `DR-005`, `TR-003`, `NFR-001`): 实现冻结 cohort、成员 registration、收齐校验、原子 finalize 与 official population 可重建投影；同时实现 append-only 留出预算台账（`holdout_budget/ledger.jsonl`，仅 canonical capability 可追加，preview 越权写入即失败关闭并写 `evaluation.gate_rejected`） — verify: `tests/integration/test_f007_canonical_registry.py`", "oldString": "- [ ] T012 (`FR-004`, `DR-004`, `TR-003`, `NFR
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账的负例） — verify: `tests/integration/test_f007_execution_tiers.py`", "oldString": "- [ ] T003 (`NFR-003`): 为 preview、canonical writer 和留出 reader 建立 capability 测试夹具 — verify: `tests/integration/test_f007_execution_tiers.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"test_f007_controls_real.py\"),\n        ),\n    ),\n    TextCheck(\n        \"holdout_budget_ledger_exists\",\n        \"F007-D010\",\n        requires=(\n            (F007_SPEC, \"DR-005\"),\n            (F007_SPEC, \"HoldoutBudgetLedger\"),\n            (F007_DESIGN, \"holdout_budget/ledger.jsonl\"),\n            (F007_TASKS, \"DR-005\"),\n            (F007_TASKS, \"留出预算台账\")
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 137 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:13Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D010 新增 DR-005 append-only 留出预算台账与越权负例\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
24fdab9 fix(f007): D010 新增 DR-005 append-only 留出预算台账与越权负例


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:19Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果；FactorDef 运行\n可将尚不适用的后续阶段显式记为 `NOT_APPLICABLE`，不得记为 PASS。必需输入/指标/实现失败时\n运行必须 `INCOMPLETE/FAIL`。阶段状态与晋升/成本 verdict 是**两层独立枚举**，不得互相替代：\n阶段状态（`PASS`/`FAIL`/`UNDERPOWERED`/`INCOMPLETE`/`NOT_APPLICABLE`）只描述单阶段结果，\n`promising`/`dead` 等晋升与成本裁决只在 cohort 级产出（完整术语表由 design §3.3 冻结，本 Feature 各 scenario 与 AC-003/AC-004 引用同一份）。", "oldString": "系统应当按信号质量、组合转换、成本/容
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- THEN stage 状态不得为 `PASS` 且 `promotion_verdict` 不得为 `promising`，失败记录包含 stage/owner/mechanism 与原始异常引用", "oldString": "- THEN verdict 不得为 PASS/promising，失败记录包含 stage/owner/mechanism 与原始异常引用"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "`sample_tier` 三级（ADR-0003 样本量门槛）：`underpowered`（<30 笔，不判 PASS 也不判 FAIL）、\n`provisional`（30~69 笔，最多临时 PASS、仅允许缩减仓位 paper）、`trustworthy`（≈≥69 笔，才允许完整\n成本后 PASS/FAIL 判定）。`underpowered` / `provisional` 都不得计入北极星判据。\n\n**术语表（冻结；spec FR-003/FR-005 与 AC-003/AC-004 引用同一份）**：\n\n| 层 | 字段 | 枚举 | 说明 |\n|---|---|---|---|\n| 阶段状态 | `stage_results[].status` | `PASS \\| FAIL \\| UNDERPOWERED \\| INCOMP
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T007 (`FR-003`, `FR-005`, `AC-004`): 实现最小信号质量、三档成本、breakeven 与阶段状态模型（按 design §3.3 术语表实现 stage 状态与 verdict 两层枚举） — verify: `tests/unit/evaluation/test_cost_and_stability.py`", "oldString": "- [ ] T007 (`FR-003`, `FR-005`, `AC-004`): 实现最小信号质量、三档成本、breakeven 与阶段状态模型 — verify: `tests/unit/evaluation/test_cost_and_stability.py`"})`


> [reasoning] 10/25. **D011**: verdict vocabulary frozen (two-layer glossary).

design §3.3 add glossary table. spec FR-003/FR-005 reference it. AC-003/AC-004 consistent.

spec FR-003 current scenario says "verdict 不得为 PASS/promising". Rewrite to be layer-precise:
"- THEN stage 状态不得为 `PASS` 且 `promotion_verdict` 不得为 `promising`，失败记录包含 stage/owner/mechanism 与原始异常引用"

And spec FR-003 requirement text add reference to the frozen glossary: "系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果（阶段状态枚举见 design §3.3 术语表）…" — that overlaps D021. Let me keep D011's spec edit focused: add a sentence in FR-003 about two layers:
"阶段状态（`PASS`/`FAIL`/`UNDERPOWERED`/`INCOMPLETE`/`NOT_APPLICABLE`）与晋升/成本 verdict（`promising`/`dead`/…）是两层独立枚举，不得互相替代；完整术语表由 design §3.3 冻结并被本节两个 scenario 引用。"

design §3.3 glossary table:
```
**术语表（冻结；spec FR-003/FR-005 与 AC-003/AC-004 引用同一份）**：

| 层 | 字段 | 枚举 | 说明 |
|---|---|---|---|
| 阶段状态 | `stage_results[].status` | `PASS \| FAIL \| UNDERPOWERED \| INCOMPLETE \| NOT_APPLICABLE` | 仅描述单阶段结果；`PASS` 不是晋级结论 |
| 成本裁决 | `cost_verdict` | `cost_positive \| cost_negative \| cost_undetermined` | 三档成本后收益判定 |
| 样本量裁决 | `sample_tier` | `underpowered \| provisional \| trustworthy` | 见 §7 与 ADR-0003 |
| 成员晋升裁决 | `promotion_verdict` | `promising \| dead \| underpowered \| incomplete` | 只在 `cohort_verdict.json`，cohort FINALIZED 后才产生 |
| cohort 状态 | `cohort_verdict.status` | `OPEN \| FINALIZED` | 未收齐承诺成员恒为 `OPEN`，不产生可晋级结论 |
```
Hmm, spec FR-005 scenario uses `cost_verdict=cost_negative` and verdict `dead`. My table says cost_verdict values lowercase snake `cost_positive|cost_negative|cost_undetermined` ✓ and promotion_verdict `dead` ✓. Consistent.

Check `verdict_vocabulary_frozen`: requires (F007_DESIGN, "promotion_verdict"), (F007_DESIGN, "NOT_APPLICABLE"), (F007_SPEC, "promotion_verdict"), (F007_DESIGN, "术语表"), (F007_SPEC, "cost_verdict").

tasks: does the finding require tasks change? "AC-003/AC-004 引用一致" — spec only. I'll add T007 (stage model) mention of the glossary: "按 design §3.3 术语表实现 stage/verdict 两层枚举". Then require (F007_TASKS, "术语表").

Let me apply: spec FR-003 text, spec FR-003 scenario, design glossary, tasks T007.
**D011** (Medium, `spec-internal-contradiction`) — 冻结两层 verdict 术语表。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:35Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"留出预算台账\"),\n        ),\n    ),\n    TextCheck(\n        \"verdict_vocabulary_frozen\",\n        \"F007-D011\",\n        requires=(\n            (F007_DESIGN, \"术语表（冻结\"),\n            (F007_DESIGN, \"promotion_verdict\"),\n            (F007_DESIGN, \"cost_verdict\"),\n            (F007_SPEC, \"promotion_verdict\"),\n            (F007_SPEC, \"两层独立枚举\"),\n            (F007_TASKS, 
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 138 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:45Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D011 冻结 stage 状态与晋升/成本裁决两层术语表\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
c9a1139 fix(f007): D011 冻结 stage 状态与晋升/成本裁决两层术语表


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:33:54Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T024 (`FR-001`, `FR-004`, `NFR-001`, `AC-001`, `AC-003`): 承接 SC-002 的并发与故障注入集成测试——同 ID 并发 claim 只有一个成功、崩溃后 lease 超时才可接管、finalize 原子性（失败不产生部分 `cohort_verdict`）、registration 幂等重试不重复计数 — verify: `tests/integration/test_f007_concurrency.py`\n\n### [TEST] 组：层 2 旅程验收轨（必填）", "oldString": "### [TEST] 组：层 2 旅程验收轨（必填）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "claim 包含 owner token 和启动时间。崩溃后只有恢复命令在确认无活进程、temp artifact 未发布且\n超出配置 lease 后才可接管；正常运行不能偷锁。canonical registration 失败时运行保持\n`EVIDENCE_READY` 但不属于 official population，重试只补同一幂等 registration。cohort finalize\n使用独立原子 claim；失败不产生部分 `cohort_verdict`，修复后可按同一 cohort ID 重试。\n`SC-002` 的同 ID 并发 claim、崩溃后 lease 接管与 finalize 原子性由 `tests/integration/test_f007_concurrency.py` 以故障注入取证。", "oldString": "cla
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-009` | unit + integration | `tests/unit/validation/test_methodology_gate.py`、`tests/integration/test_f007_execution_tiers.py` | 三层状态入 manifest；L2/L3 缺失时阻断晋级 |\n| `SC-002` | integration + fault injection | `tests/integration/test_f007_concurrency.py` | 同 ID 并发 claim、崩溃后 lease 接管、finalize 原子性、registration 幂等 |", "oldString": "| `AC-009` | unit + integration | `tests/unit/validation/
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。\n- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。", "oldString": "- `T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。"})`


> [reasoning] 11/25. **D012**: SC-002 concurrency task.

tasks §3 add T024 并发/故障注入, before the [TEST] heading. Note: T024 must be inserted before `### [TEST] 组` so ordering is T023, T024, [TEST] T027-T029, T030. But D016 (T025) and D025 (T026) will also be inserted there.

Order of insertion:
- D012 adds T024 before the [TEST] heading.
- D016 adds T025 after T024.
- D025 adds T026 after T025.
Each edit inserts after the previous task. Fine.

D012 task text:
```
- [ ] T024 (`FR-001`, `FR-004`, `NFR-001`, `AC-001`, `AC-003`): 实现并发与故障注入集成测试——同 ID 并发 claim 只有一个成功、崩溃后 lease 超时才可接管、finalize 原子性（失败不产生部分 `cohort_verdict`）、registration 幂等重试不重复计数 — verify: `tests/integration/test_f007_concurrency.py`
```
design §8 add row for SC-002:
```
| `SC-002` 并发/故障注入 | integration + fault injection | `tests/integration/test_f007_concurrency.py` | 同 ID 并发 claim、崩溃后 lease 接管、finalize 原子性、registration 幂等 |
```
And design §5 add a sentence about the claim/finalize concurrency being验证 by that test.
design §8 line 246-247 already mentions four fixtures; extend "对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异" + concurrency. Add SC-002 mention.

Also tasks §4 edges for T024: `T012/T013 -> T024`. And add to the [TEST] predecessor list? T024 must be predecessor of T027-T029? The [TEST] predecessor list currently `T027/T028/T029 -> T030`. I'll extend later in D025 or leave. Let me add in D012: `` `T012/T013 -> T024`：并发 claim/finalize 测试依赖登记与 CLI 实现。 ``

Check `sc002_concurrency_has_task`: requires (F007_TASKS, "SC-002"), (F007_TASKS, "故障注入"), (F007_DESIGN, "SC-002"), (F007_TASKS, "test_f007_concurrency.py").

Note: currently SC-002 appears in spec, not tasks. Need tasks to mention SC-002 → the T024 line includes `SC-002`? Let me include in tags: `(SC-002, FR-001, FR-004, NFR-001, AC-001, AC-003)`. Hmm, task tagging convention is requirement IDs; SC-002 is a success criterion. I'll write it in the text: "承接 SC-002：…". Good.

Let me apply.
**D012** (Medium, `gate-without-teeth`) — SC-002 并发/故障注入承接。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:10Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。\n- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。", "oldString": "全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"术语表\"),\n        ),\n    ),\n    TextCheck(\n        \"sc002_concurrency_has_task\",\n        \"F007-D012\",\n        requires=(\n            (F007_TASKS, \"SC-002\"),\n            (F007_TASKS, \"故障注入\"),\n            (F007_TASKS, \"test_f007_concurrency.py\"),\n            (F007_DESIGN, \"SC-002\"),\n        ),\n    ),", "oldString": "            (F007_TASKS, \"术语表\"),\n       
…[truncated])`


> [reasoning] The last edit failed because the line got merged earlier: D008's edit appended "；`T012/T014 -> T016`：..." to the T007 line. Let me recall the current §4 text:

```
- `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。
- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。
- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。
- `T011,T012 -> T014,T015`：综合只消费已发布并登记的 canonical 证据。
```

So the T012/T014 -> T016 text is mid-line. Append the new edge after that whole line.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 139 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:20Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D012 增并发/故障注入测试任务承接 SC-002\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
9825178 fix(f007): D012 增并发/故障注入测试任务承接 SC-002


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:36Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-003** (`FR-003`, `FR-004`): 必需统计失败关闭；拒绝者仍进入试验分母，成员未收齐时 cohort 不能 finalize 或晋级；**多成员 cohort 批量夹具**上被拒成员仍在分母、诊断性重算不重复计数", "oldString": "- [ ] **AC-003** (`FR-003`, `FR-004`): 必需统计失败关闭；拒绝者仍进入试验分母，成员未收齐时 cohort 不能 finalize 或晋级"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- GIVEN cohort 内一个候选在成本门被拒绝\n- WHEN 计算 cohort 多重检验与漏斗\n- THEN 该候选仍计入试验总数，多成员 cohort 的批量分母完整、诊断性重算不重复计数", "oldString": "- GIVEN cohort 内一个候选在成本门被拒绝\n- WHEN 计算 cohort 多重检验与漏斗\n- THEN 该候选仍计入试验总数，诊断性重算不重复计数"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-003` | unit + integration | `tests/unit/evaluation/test_required_statistics.py` | 估计器异常失败关闭，拒绝者在 cohort 分母；多成员 cohort 批量 fixture 验证分母完整 |", "oldString": "| `AC-003` | unit + integration | `tests/unit/evaluation/test_required_statistics.py` | 估计器异常失败关闭，拒绝者在 cohort 分母 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T016 (`FR-003`, `FR-004`, `FR-005`, `AC-003`): 跑正控制、白噪声与故意泄漏 golden，多成员 cohort 批量夹具全链记录拒绝者（被拒者仍入分母、诊断性重算不重复计数） — verify: `tests/integration/test_f007_controls.py`", "oldString": "- [ ] T016 (`FR-003`, `FR-004`, `FR-005`, `AC-003`): 跑正控制、白噪声与故意泄漏 golden，全链记录拒绝者 — verify: `tests/integration/test_f007_controls.py`"})`


> [reasoning] 12/25. **D013**: AC-003 multi-member batch.

spec AC-003 clause: add "多成员 cohort 批量夹具（被拒成员仍在分母、诊断性重算不重复计数）".
FR-004 scenario already says "该候选仍计入试验总数，诊断性重算不重复计数". Add "多成员" to the scenario? The check requires (F007_SPEC, "多成员"), (F007_DESIGN, "多成员 cohort"), (F007_TASKS, "多成员").

design §8 AC-003 row: add "多成员 cohort 批量 fixture，被拒者仍入分母".
tasks: T016 extend "全链记录拒绝者" → "多成员 cohort 批量夹具，被拒者仍入分母；诊断性重算不重复计数".
Also T027 [TEST] already mentions "多成员批量夹具" ✓ (I wrote "（多成员批量夹具）").

Let me apply. Check needle (F007_TASKS, "多成员") — T027 [TEST] contains "多成员批量夹具" ✓ already. But to be safe I'll also add to T016.

Let me apply.
**D013** (Medium, `batch-scenario-untested`) — AC-003 多成员批量分母。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:54Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"SC-002\"),\n        ),\n    ),\n    TextCheck(\n        \"ac003_multi_member_batch\",\n        \"F007-D013\",\n        requires=(\n            (F007_SPEC, \"多成员 cohort 批量夹具\"),\n            (F007_DESIGN, \"多成员 cohort 批量 fixture\"),\n            (F007_TASKS, \"多成员 cohort 批量夹具\"),\n        ),\n    ),", "oldString": "            (F007_DESIGN, \"SC-002\"),\n        ),\n    ),"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 140 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:02Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D013 AC-003 增多成员 cohort 批量分母与用例\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
7fec73c fix(f007): D013 AC-003 增多成员 cohort 批量分母与用例


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:10Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "`report.json` 包含 identity refs、stage results、rank IC/HAC uncertainty、quantile/decay、dedup、\ncost/capacity、sample-size/stability、structured failure 与成员诊断 verdict、以及 `approximation`\n（NFR-004：preview 采样/缩窗时的显式近似标注，字段含 `is_approximate` 与 `reduced_dimensions[]`；\ncanonical 恒为 `is_approximate=false`，不得因性能压力静默减少门禁或样本）。cohort 级 BH-FDR/DSR", "oldString": "`report.json` 包含 identity refs、stage re
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-009** (`FR-007`): 三层无前视状态逐层进入 manifest；L1 fail-closed 生效（未来算子负例被拒）；L2/L3 非 `PASS` 时阻断晋级且拒绝事件携带缺失层与 owner；任何情况下不得把缺失层记为 PASS 或静默省略\n- [ ] **AC-011** (`FR-006`, `NFR-004`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本", "oldString": "- [ ] **AC-009** (`FR-007`): 三层无前视状态逐层进入 manifest；L1 fail-closed 生效（未来算子负例被拒）；L2/L3 非 `PASS` 时阻断晋级且拒
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T015 (`FR-006`, `UX-002`, `AC-005`, `AC-011`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推；断言 `approximation` 标注存在且 canonical 恒为非近似 — verify: `tests/contract/test_f007_artifact_schemas.py`", "oldString": "- [ ] T015 (`FR-006`, `UX-002`, `AC-005`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推 — verify: `tests/contract/test_f007_artifact_schemas.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-005` | integration + fault injection | `tests/integration/test_f007_atomic_publish.py` | 任一文件失败均无可见半成品/PASS |\n| `AC-011` | contract + integration | `tests/contract/test_f007_artifact_schemas.py` | `approximation` 标注存在；canonical 非近似；POSIX 逻辑路径；CLI 首屏字段快照 |", "oldString": "| `AC-005` | integration + fault injection | `tests/integration/test_f007_atomic_publish.py` | 任一文件失败均无可见半成品/P
…[truncated])`


> [reasoning] 13/25. **D014**: NFR-004 approximation.

design §3.3 report schema add `approximation` field description. 
spec: NFR-004 already mentions 显式标注近似; the finding wants AC reference. Add NFR-004 to AC-011 (which I'll add in D022 for NFR-005/UX-001 — but D022 is later). To avoid depending on a later finding, add the NFR-004 clause now to AC-011? AC-011 doesn't exist yet. Hmm.

Option: add clause to existing AC-005 or AC-006? Approximation relates to NFR-004 preview. I could add a new AC now (AC-010) and let D019/D022 use AC-011/AC-012. But I planned AC-010 for D019's 最终确认窗 and AC-011 for D014+D022.

Let me restructure: 
- AC-010 → D019 (最终确认窗隔离, NFR-003/IR-003)
- AC-011 → D014 (NFR-004 近似标注) + D022 (NFR-005/UX-001) — D022's check requires the literal `**AC-011** (\`NFR-004\`, \`NFR-005\`, \`UX-001\`)`. So AC-011 must reference NFR-004, NFR-005, UX-001 all three. So D014 adds AC-011 with NFR-004 (and I can include NFR-005/UX-001 later in D022 — but then D014's check should not require NFR-005). Hmm, cleaner: D014 adds AC-011 referencing NFR-004 (+ FR-006), and D022 adds NFR-005/UX-001 to the same AC line. The D022 check literal requires the full `(\`NFR-004\`, \`NFR-005\`, \`UX-001\`)` form, which only exists after D022. Since checks are added per finding and must pass at that commit, D014's check must not require the full form. Fine: D014 requires (F007_SPEC, "**AC-011** (`NFR-004`") and (F007_SPEC, "approximation"); D022 changes the AC-011 line to include NFR-005/UX-001 and its check requires the full literal.

Hmm, but editing the AC-011 line in D022 means the AC-011 text changes. That's fine.

Actually simpler: D014 adds AC-011 with tags `(FR-006, NFR-004)` and text "preview 近似（采样/缩窗）在 report.json 的 `approximation` 字段显式标注，canonical 不因性能压力静默减少门禁或样本". D022 later edits that line to `(NFR-004, NFR-005, UX-001)`. Fine.

design §3.3: add `approximation` to report.json field list + note.
tasks: T015 extend "验证曲线-标量互推" + "校验 approximation 标注与 POSIX 逻辑路径" (D022 handles POSIX; D014 adds approximation).

Check D014: requires (F007_DESIGN, "approximation"), (F007_SPEC, "approximation"), (F007_TASKS, "approximation").

Let me apply.

design §3.3 first paragraph: "`report.json` 包含 identity refs、stage results、... 与成员诊断 verdict。" → add "、`approximation`（preview 采样/缩窗时的近似标注，canonical 恒为 false）".

Wait "canonical 恒为 false" — canonical doesn't sample per NFR-004. Good.

Let me apply.
**D014** (Medium) — NFR-004 近似标注字段。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:22Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"多成员 cohort 批量夹具\"),\n        ),\n    ),\n    TextCheck(\n        \"nfr004_approximation_covered\",\n        \"F007-D014\",\n        requires=(\n            (F007_SPEC, \"**AC-011** (`FR-006`, `NFR-004`)\"),\n            (F007_DESIGN, \"`approximation`\"),\n            (F007_TASKS, \"`approximation`\"),\n        ),\n    ),", "oldString": "            (F007_TASKS, \"多成员 cohort 批量夹
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 141 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:30Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D014 NFR-004 近似标注落 report schema 与 AC-011\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
c8b8c64 fix(f007): D014 NFR-004 近似标注落 report schema 与 AC-011


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:36Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T017 (`FR-001`, `FR-002`, `NFR-003`, `AC-001`, `AC-002`, `AC-003`, `AC-005`): 对 future-fill、embargo、guard 注册、preview writer、异常吞噬与 publish 完整性运行定向变异，逐 mutant 产出证据 — verify: `tests/mutation/test_f007_gate_mutations.py`；变异工具版本 pin 于 dev 依赖（范围上界，按 SOP §1），结果写 `reports/mutation/f007/mutation_report.json`（mutant-killed 报告）", "oldString": "- [ ] T017 (`FR-001`, `FR-002`, `NFR-003`): 对 fut
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T021 (`AC-001`, `AC-002`, `AC-003`, `AC-005`): 运行 F007 定向变异并确认每个 mutant 被门禁杀死（`reports/mutation/f007/mutation_report.json` 无 survived 项） — verify: `pytest -q tests/mutation/test_f007_gate_mutations.py`", "oldString": "- [ ] T021 (`AC-002`, `AC-005`): 运行 F007 定向变异并确认每个 mutant 被门禁杀死 — verify: `pytest -q tests/mutation/test_f007_gate_mutations.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；\n对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异，\n逐 mutant 产出 kill 证据到 `reports/mutation/f007/mutation_report.json`（无 survived 项才算通过），\n变异工具版本按 SOP §1 在 dev 依赖 pin 范围上界。", "oldString": "另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；\n对 guard 注册表、异常吞噬、preview writer、embar
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"`approximation`\"),\n        ),\n    ),\n    TextCheck(\n        \"mutation_targets_labels_aligned\",\n        \"F007-D015\",\n        requires=(\n            (F007_TASKS, \"变异工具版本 pin\"),\n            (F007_TASKS, \"mutation_report.json\"),\n            (F007_DESIGN, \"mutation_report.json\"),\n            (F007_TASKS, \"`AC-001`, `AC-002`, `AC-003`, `AC-005`\"),\n        ),\n 
…[truncated])`


> [reasoning] 14/25. **D015**: mutation alignment + tool pin + kill artifact.

tasks T017: add AC tags + mutation tool pin + report artifact.
```
- [ ] T017 (`FR-001`, `FR-002`, `NFR-003`, `AC-001`, `AC-002`, `AC-003`, `AC-005`): 对 future-fill、embargo、guard 注册、preview writer、异常吞噬与 publish 完整性运行定向变异 — verify: `tests/mutation/test_f007_gate_mutations.py`；变异工具版本 pin 于 dev 依赖，逐 mutant 产出 `reports/mutation/f007/mutation_report.json` 作为 mutant-killed 证据
```
T021: `(AC-001, AC-002, AC-003, AC-005)`: 运行 F007 定向变异并确认每个 mutant 被杀死，核对 `mutation_report.json` 无 survived 项 — verify: `pytest -q tests/mutation/test_f007_gate_mutations.py` + mutation_report.json
design §8 note: add "变异工具 pin 与 mutant-killed 报告（`reports/mutation/f007/mutation_report.json`）作为 verify 证据".

Check D015: requires (F007_TASKS, "mutation_report.json"), (F007_TASKS, "变异工具版本 pin"), (F007_DESIGN, "mutation_report.json"), (F007_TASKS, "mutant").

Let me apply.

Note: DEP pin gate `check_dep_pins.py` — adding "变异工具版本 pin" is only text; no actual dependency added. Fine. But careful: the test file mentions pinning in dev deps — that's text in tasks, no manifest edit needed for a doc feature. OK.

Also note the mutation tool choice: mutmut? cosmi? I shouldn't invent a specific tool since the finding says "增变异工具依赖 pin 与 mutant-killed 证据产物". I'll keep it tool-agnostic ("变异工具（选定后 pin 版本上界）").

Hmm, "变异工具版本 pin" must appear literally. Let me write "变异工具版本 pin 于 dev 依赖（范围上界，按 SOP §1 规则）".
**D015** (Medium) — 变异目标标签对齐 + pin/kill 证据。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 142 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:48Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D015 变异 AC 标签对齐并加工具 pin 与 mutant-killed 证据\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
278ebe2 fix(f007): D015 变异 AC 标签对齐并加工具 pin 与 mutant-killed 证据


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:01Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T025 (`FR-004`, `NFR-002`): 统计第二实现对照抽查（PRD FR3.7）——对高价值候选或统计实现变更，用独立实现（Vibe-Trading `quantlib_call` 或本仓手工第二实现）对照 BH-FDR/block bootstrap，**time-box 1 周**；对照对象、容差（估计量相对差 ≤1e-6，超出则显式记录差异与原因）与证据路径 `reports/second_impl/<experiment_id>/` 一并落档；超时不阻塞主链路 — verify: `tests/unit/evaluation/test_second_implementation.py`\n\n### [TEST] 组：层 2 旅程验收轨（必填）", "oldString": "### [TEST] 组：层 2 旅程验收轨（必填）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。\n- `T009/T016 -> T025`：第二实现对照以成员级统计实现与全链控制证据为对照对象。", "oldString": "- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "| 统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查 | 门禁不能依赖会 warning 降级的黑盒 | ADR-0003；抽查载体 T025（time-box 1 周、容差与证据路径入 tasks） |", "oldString": "| 统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查 | 门禁不能依赖会 warning 降级的黑盒 | ADR-0003 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| 方法统计 | 最小自研协议，第二实现只做对照（T025，time-box 1 周，证据落 `reports/second_impl/<experiment_id>/`） | 硬门需可控失败语义 | 不依赖 ml4t 配套包运行 |", "oldString": "| 方法统计 | 最小自研协议，第二实现只做对照 | 硬门需可控失败语义 | 不依赖 ml4t 配套包运行 |"})`


> [reasoning] 15/25. **D016**: second implementation carrier.

tasks §3 add T025 after T024:
```
- [ ] T025 (`FR-007`?) — no. The second implementation relates to PRD FR3.7 and spec §7 决策与风险 "第二实现抽查". Task:
- [ ] T025 (`NFR-002`? no) — let me tag `(FR-004, NFR-002)`? Hmm. The statistic协议 is FR-004. Second implementation spot-check validates statistics correctness. I'll tag `(FR-004, NFR-002)` and mention SC/PRD FR3.7.
```
Text:
```
- [ ] T025 (`FR-004`, `NFR-002`): 统计第二实现对照抽查（PRD FR3.7）——对高价值候选或统计实现变更，用独立实现（Vibe-Trading `quantlib_call` 或本仓手工第二实现）对照 BH-FDR/block bootstrap，time-box 1 周；对照对象、容差（估计量相对差 ≤1e-6 或显式记录差异）与证据路径 `reports/second_impl/<experiment_id>/` 一并落档；超时不阻塞主链路 — verify: `tests/unit/evaluation/test_second_implementation.py`
```
spec §7 决策与风险 row 后续 column: "T025（time-box 1 周）".
design §9 row: update "方法统计" row's 替代方案/后续 "第二实现只做对照" → add carrier.
Also §5 后移? No, it's a task now.

Check D016: requires (F007_TASKS, "第二实现"), (F007_TASKS, "time-box"), (F007_SPEC, "第二实现"), (F007_TASKS, "test_second_implementation.py").

Note spec already has "第二实现抽查" ✓.

Also §4 edge for T025: `T009/T016 -> T025`. And T025 predecessor to [TEST]? Not needed.

Let me apply.
**D016** (Medium, `deferred-work-without-carrier`) — 第二实现抽查承接。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:11Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"`AC-001`, `AC-002`, `AC-003`, `AC-005`\"),\n        ),\n    ),\n    TextCheck(\n        \"second_implementation_has_task\",\n        \"F007-D016\",\n        requires=(\n            (F007_TASKS, \"第二实现对照抽查\"),\n            (F007_TASKS, \"time-box 1 周\"),\n            (F007_TASKS, \"test_second_implementation.py\"),\n            (F007_SPEC, \"第二实现抽查\"),\n        ),\n    ),", "oldS
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 143 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:22Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D016 第二实现抽查落 T025（time-box/容差/证据路径）\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
10e91f1 fix(f007): D016 第二实现抽查落 T025（time-box/容差/证据路径）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:33Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **DR-007**：`SignalFactorProvenance` 应当记录从 F004/Kronos 信号或人工种子派生为可评测 `FactorDef` 的适配信息（来源 dataset 与 `source` 分布、适配器版本、原始信号列、标签与 horizon 映射）；`source=placeholder` 的来源在 canonical 被拒绝（`E_INPUT_INVALID`），preview 允许但报告必须标注 `signal_source=placeholder` 并置 `approximation=true`；F004 只交付真实信号源与 `/predict` 契约，不升级 `signals_log` 内容，消费者路由切换不在本 Feature 范围。\n- **DR-003**：`ExperimentManifest` 应当关联输入、逐阶段状态、
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-008** (`IR-001`, `IR-002`, `IR-003`, `DR-007`): CLI/schema 契约能拒绝非法 canonical 请求并返回结构化失败；`source=placeholder` 的 Kronos 信号源自 canonical 被拒（`E_INPUT_INVALID`）、preview 显式标注，适配 provenance 完整", "oldString": "- [ ] **AC-008** (`IR-001`, `IR-002`, `IR-003`): CLI/schema 契约能拒绝非法 canonical 请求并返回结构化失败"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "### 信号来源与 FactorDef 适配（F004 / 人工种子）\n\nF004 交付真实 Kronos 推理实例与 `/predict` 契约，但**不**升级 `signals_log` 内容，也不切换消费者路由；因此从信号到可评测 `FactorDef` 的适配契约由本 Feature 拥有：\n\n- 信号型 `FactorDef` 由 `signals_log` dataset（F002 只读）派生，定义与 manifest 记录 `SignalFactorProvenance`：来源 dataset、`source` 分布、适配器版本、原始信号列与标签/horizon 映射。\n- `source=placeholder` 的处理分层：**canonical 拒绝**（`E_INPUT_INVALID`，fail-closed，与 ADR-0003 
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T007 (`FR-003`, `FR-005`, `AC-004`): 实现最小信号质量、三档成本、breakeven 与阶段状态模型（按 design §3.3 术语表实现 stage 状态与 verdict 两层枚举），并写入信号来源 provenance（`source=placeholder` 在 canonical 失败关闭、preview 显式标注） — verify: `tests/unit/evaluation/test_cost_and_stability.py`", "oldString": "- [ ] T007 (`FR-003`, `FR-005`, `AC-004`): 实现最小信号质量、三档成本、breakeven 与阶段状态模型（按 design §3.3 术语表实现 stage 状态与 verdict 两层枚举） — ve
…[truncated])`


> [reasoning] 16/25. **D017**: F004 Kronos signals → FactorDef adaptation + placeholder rules.

spec: add to §0 upstream contract the Kronos signal factor contract; and a requirement clause. Where? IR-002 (input contract) or a new DR-007. Let me add to §4 数据/实体需求 a DR-007:

```
- **DR-007**：`SignalFactorProvenance` 应当记录从 F004/Kronos 或人工种子派生为可评测 `FactorDef` 的适配信息（信号 dataset 与 `source` 分布、适配器版本、原始信号列、标签与 horizon 映射）；`source=placeholder` 的来源在 canonical 被拒绝（`E_INPUT_INVALID`），preview 允许但报告必须标注 `signal_source=placeholder` 与 `approximation=true`；F004 只交付真实信号源与 `/predict` 契约，不升级 `signals_log` 内容，消费者路由切换不在 F007 范围。
```
And AC-008 add DR-007 + clause.

design §7 or §4 add the contract text with "signals_log" and "source=placeholder".
design §8 row? AC-008 row add placeholder assertion.
tasks: T001 or T007 — put in T007 (signal quality stage, source provenance) and mention "placeholder". Let me extend T007: "…并在 provenance 记录信号来源（`source=placeholder` 在 canonical 拒绝、preview 显式标注）".

Check D017: requires (F007_SPEC, "placeholder"), (F007_DESIGN, "source=placeholder"), (F007_DESIGN, "signals_log"), (F007_TASKS, "placeholder").

Let me apply.
**D017** (Medium) — Kronos 信号 → FactorDef 适配与 placeholder 分层。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:47Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定；`signals_log` 的 `source=placeholder` 在 canonical 被拒、preview 标注 |", "oldString": "| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_SPEC, \"第二实现抽查\"),\n        ),\n    ),\n    TextCheck(\n        \"f004_to_f007_factor_source_contract\",\n        \"F007-D017\",\n        requires=(\n            (F007_SPEC, \"DR-007\"),\n            (F007_SPEC, \"source=placeholder\"),\n            (F007_DESIGN, \"signals_log\"),\n            (F007_DESIGN, \"`source=placeholder` 的处理分层\"),\n            (F007_TASKS, \"placeholder\"),\n   
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 144 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:58Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D017 定义信号来源适配契约与 placeholder 分层规则\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
873a884 fix(f007): D017 定义信号来源适配契约与 placeholder 分层规则


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:37:07Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "F005 前端**只经** `src/alphamill/api/` 的统一只读 API 消费 report、curves 与 synthesis；文件 reader\n只允许作为 API/后端内部 adapter（由 API 进程持有），**不得成为前端直读路径**（前端不直接读文件系统、\n不托管产物静态目录）。前端不得重算 BH-FDR、漏斗、failure taxonomy 或 verdict。Grafana 只监控评测\n任务健康，不承载研究口径或门禁按钮。", "oldString": "F005 通过只读 API/文件 reader 渲染 report、curves 与 synthesis；不得重算 BH-FDR、漏斗、\nfailure taxonomy 或 verdict。Grafana 只监控评测任务健康，不承载研究口径或门禁按钮。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"placeholder\"),\n        ),\n    ),\n    TextCheck(\n        \"f005_frontend_does_not_bypass_api\",\n        \"F007-D018\",\n        requires=(\n            (F007_DESIGN, \"src/alphamill/api/\"),\n            (F007_DESIGN, \"不得成为前端直读路径\"),\n        ),\n    ),", "oldString": "            (F007_TASKS, \"placeholder\"),\n        ),\n    ),"})`


> [reasoning] 17/25. **D018**: F005 only via API.

design §6 current:
```
F005 通过只读 API/文件 reader 渲染 report、curves 与 synthesis；不得重算 BH-FDR、漏斗、
failure taxonomy 或 verdict。Grafana 只监控评测任务健康，不承载研究口径或门禁按钮。
```
Rewrite:
```
F005 前端只经 `src/alphamill/api/` 的统一只读 API 消费 report、curves 与 synthesis；文件 reader
只允许作为 API/后端内部 adapter（由 API 进程持有），**不得成为前端直读路径**（无前端直读文件系统/HTTP 静态目录）。
不得重算 BH-FDR、漏斗、failure taxonomy 或 verdict。Grafana 只监控评测任务健康，不承载研究口径或门禁按钮。
```

Check D018: requires (F007_DESIGN, "src/alphamill/api/"), (F007_DESIGN, "不得成为前端直读路径").

Also tasks? The finding says design §6 only. Maybe also spec UX-002 already says F005 只能读取 F007 产物. Fine.

Let me apply.
**D018** (Low) — F005 只经统一只读 API。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 145 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:37:17Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D018 明确 F005 只经统一只读 API，文件 reader 仅内部 adapter\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
6b7ef77 fix(f007): D018 明确 F005 只经统一只读 API，文件 reader 仅内部 adapter


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:37:31Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **NFR-003**：安全：Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力；**最终确认窗**统计量不得出现于任何 Agent/preview 可读的 report/manifest/synthesis，越权读取或写入即 fail-closed 并留拒绝事件（ADR-0003 复盘循环窥探防护）。", "oldString": "- **NFR-003**：安全：Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **IR-003**：机器输出应使用版本化 schema，并返回 experiment_id、状态、verdict、artifact refs 和结构化 failure；Agent/preview 可读产物不含最终确认窗的任何统计量（fail-closed）。", "oldString": "- **IR-003**：机器输出应使用版本化 schema，并返回 experiment_id、状态、verdict、artifact refs 和结构化 failure。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取或写入 fail-closed 并留拒绝事件\n\n## 7. 测试、依赖与决策", "oldString": "\n## 7. 测试、依赖与决策"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "- 权限边界：canonical writer、留出 reader 与**最终确认窗 reader** 作为显式 capability 注入；preview/Agent 构造器没有\n  这些接口。最终确认窗的任何统计量不得写入 Agent/preview 可读的 report/manifest/synthesis，违规即失败关闭\n  （`E_CANONICAL_FORBIDDEN`）。任何环境变量只能提供普通路径默认值，不能升级 tier/权限。", "oldString": "- 权限边界：canonical writer 和留出 reader 作为显式 capability 注入；preview/Agent 构造器没有\n  这些接口。任何环境变量只能提供普通路径默认值，不能升级 tier/权限。"})`


> [reasoning] 18/25. **D019**: final confirmation window exclusion.

spec: NFR-003 extend + IR-003 extend + AC-010 new.
design: §3.3/§7 + §8 row.
tasks: T003 or T012 mention 最终确认窗.

spec NFR-003: "安全：Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力。" → add "；**最终确认窗**统计量不得出现于任何 Agent/preview 可读的 report/manifest/synthesis，违规写入或读取即 fail-closed（ADR-0003 复盘循环窥探防护）。"

spec IR-003: "机器输出应使用版本化 schema，并返回 experiment_id、状态、verdict、artifact refs 和结构化 failure。" → add "；Agent/preview 可读产物不含最终确认窗任何统计量。"

AC-010:
```
- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权写入或读取 fail-closed 且留拒绝事件
```

design §3.3: add "`final_confirmation` 段对 Agent/preview 可读产物不可见（fail-closed）".
design §7 权限边界: extend "canonical writer 和留出 reader 作为显式 capability 注入" + 最终确认窗 reader 为独立 capability，preview/Agent 无。
design §8 add AC-010 row.

tasks T003: add 最终确认窗 reader capability + 负例.
T012? Add to T003 suffices. Also T027 [TEST] mentions 最终确认窗 already ("最终确认窗统计量不出现在任何 Agent 可读产物") ✓.

Check D019: requires (F007_SPEC, "最终确认窗"), (F007_DESIGN, "最终确认窗"), (F007_SPEC, "fail-closed"), (F007_TASKS, "最终确认窗").

Let me apply.
**D019** (Medium) — 最终确认窗隔离与 fail-closed。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:38:01Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `SC-002` | integration + fault injection | `tests/integration/test_f007_concurrency.py` | 同 ID 并发 claim、崩溃后 lease 接管、finalize 原子性、registration 幂等 |\n| `AC-010` | integration + mutation | `tests/integration/test_f007_execution_tiers.py` | 最终确认窗统计量不出现在 Agent/preview 可读产物；越权 fail-closed |", "oldString": "| `SC-002` | integration + fault injection | `tests/integration/test_f007_concurrenc
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader、预留最终确认窗 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账/读最终确认窗的负例） — verify: `tests/integration/test_f007_execution_tiers.py`", "oldString": "- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账的负例） — verify: `tests/integr
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"不得成为前端直读路径\"),\n        ),\n    ),\n    TextCheck(\n        \"final_confirmation_window_hidden\",\n        \"F007-D019\",\n        requires=(\n            (F007_SPEC, \"**AC-010** (`NFR-003`, `IR-003`)\"),\n            (F007_SPEC, \"最终确认窗\"),\n            (F007_SPEC, \"fail-closed\"),\n            (F007_DESIGN, \"最终确认窗\"),\n            (F007_TASKS, \"最终确认窗\"),\n        ),\n    
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 146 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:38:12Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D019 最终确认窗统计排除于 Agent/preview 产物并 fail-closed\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
c408ffc fix(f007): D019 最终确认窗统计排除于 Agent/preview 产物并 fail-closed


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:38:23Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py", "offset": 80})`


> [reasoning] 19/25. **D020**: design §8 test map covers all test files used by tasks. This needs a custom parser check. Let me:
1. Add the 5 missing test files to design §8 (as rows or in the table).
2. Write a custom check `check_f007_test_map_covers_tasks` that:
   - extracts test file paths from tasks.md verify clauses (`tests/...py`)
   - extracts test file paths from design §8 (section body)
   - asserts tasks ⊆ design.
3. Add custom check to CUSTOM_CHECKS and a mutation test for it in the test file.

The 5 files: `tests/contract/test_f007_upstream_contracts.py`, `tests/integration/test_f007_canonical_registry.py`, `tests/contract/test_f007_artifact_schemas.py`, `tests/integration/test_f007_controls.py`, `tests/mutation/test_f007_gate_mutations.py`. Also new ones I added: `test_f007_concurrency.py`, `test_f007_controls_real.py`, `test_second_implementation.py`. The custom check will require ALL tasks-referenced test paths to appear in design §8 — so I must add all of them. Let me collect all test paths in F007 tasks verify clauses:

From tasks.md (after my edits):
- tests/contract/test_f007_upstream_contracts.py (T001)
- tests/unit/experiment_store/test_research_snapshot.py (T001, T004)
- tests/fixtures/f007/README.md (T002) — not a .py; my regex should only capture `tests/...py`. Actually T002 verify is `tests/fixtures/f007/README.md`. If regex is `tests/[\w/]+\.py` it won't match .md. Good.
- tests/integration/test_f007_execution_tiers.py (T003)
- tests/unit/experiment_store/test_identity.py (T004)
- tests/integration/test_f007_cli.py (T006, T013)
- tests/unit/evaluation/test_cost_and_stability.py (T007, T010)
- tests/unit/validation/test_methodology_gate.py (T008)
- tests/unit/evaluation/test_required_statistics.py (T009)
- tests/integration/test_f007_atomic_publish.py (T011)
- tests/integration/test_f007_canonical_registry.py (T012)
- tests/integration/test_f007_synthesis.py (T014)
- tests/contract/test_f007_artifact_schemas.py (T015)
- tests/integration/test_f007_controls.py (T016)
- tests/mutation/test_f007_gate_mutations.py (T017)
- tests/integration/test_f007_concurrency.py (T024)
- tests/unit/evaluation/test_second_implementation.py (T025)
- (T026 property, to be added in D025 — will need design entry too)
- [TEST] T027/T028/T029 reference the same files.
- T022 test_f007_controls_real.py (mine)
- T018-T021 reference same files.
- T023/T030 reference tools/verify.py (not tests/).

So design §8 must contain all of these. Current design §8 table rows reference: execution_tiers, methodology_gate, required_statistics, cost_and_stability, atomic_publish, research_snapshot+identity, synthesis, cli, + I added AC-009 row (methodology+execution_tiers), real-env row (controls_real), SC-002 row (concurrency), AC-010 row (execution_tiers), AC-011 row (artifact_schemas).

Missing from design §8: upstream_contracts, canonical_registry, controls, gate_mutations, second_implementation, and (after D025) property test file.

I'll add:
- a row for AC-006/input contracts: `tests/contract/test_f007_upstream_contracts.py`
- a row for AC-003/FR-004 registry: `tests/integration/test_f007_canonical_registry.py`
- a row for AC-003 controls: `tests/integration/test_f007_controls.py`
- a row for mutation: `tests/mutation/test_f007_gate_mutations.py`
- a row for second impl: `tests/unit/evaluation/test_second_implementation.py`
- and note identity files already present.

The custom check's logic: parse tasks.md for regex `tests/[A-Za-z0-9_./-]+\.py` and design for the same; assert tasks set ⊆ design set. Also assert design doesn't reference test files not in tasks? Not required — but a one-way check is what the finding wants ("design 第 8 节测试映射遗漏 tasks 使用的多个测试文件").

Hmm, design §8 has a row "| `AC-006` | property + integration | `tests/unit/experiment_store/test_research_snapshot.py`、`test_identity.py` |" — the second path is written as bare `test_identity.py` without the tests/ prefix! My regex on design would then capture only if I make design's text have full path. Let me fix design: write full paths there. Actually the regex requires `tests/...`. If design writes `test_identity.py` bare, it won't match and the tasks set includes `tests/unit/experiment_store/test_identity.py`, so the check fails. I must fix design to include the full path. Let me update that cell to full paths.

Let me write the custom check:

```python
TEST_FILE_RE = re.compile(r"tests/[A-Za-z0-9_./-]+\.py")
TASKS_SECTION3 = "3. 验证与验收任务"


def check_f007_test_map_covers_tasks(root: pathlib.Path) -> list[tuple[str, str]]:
    """F007-D020：tasks 声明的测试文件必须能在 design §8 映射表里找到。"""
    errors: list[tuple[str, str]] = []
    tasks_text = read(root, F007_TASKS)
    design_text = read(root, F007_DESIGN)
    design_map = set(TEST_FILE_RE.findall(design_text))
    # design 映射表允许用 `tests/unit/experiment_store/test_x.py`、`tests/unit/experiment_store/test_y.py`
    # 共享目录的简写由 check 侧展开，这里仅要求完整路径出现。
    for path in sorted(set(TEST_FILE_RE.findall(tasks_text))):
        if path not in design_map:
            errors.append(("f007_design_test_map_covers_tasks", f"design §8 未映射 tasks 使用的测试文件 {path}"))
    return errors
```

Wait: design might legitimately reference test files not in tasks (e.g., design mentions `tests/unit/evaluation/test_identity.py`?). One-way is fine.

But careful: the shared-directory abbreviation in design (e.g. `test_identity.py` bare) — I'll just write full paths in design.

Also careful: the check must not be fooled by the fact that design mentions test files in prose (like `tests/integration/test_f007_concurrency.py`). That's fine.

Now, mutation test for the custom check: add to test file:
```python
def test_f007_design_test_map_goes_red_on_missing_mapping(tmp_path):
    _materialize(tmp_path, set())
    tasks = tmp_path / cdc.F007_TASKS
    tasks.write_text(tasks.read_text(encoding="utf-8") + "\n- verify: `tests/unit/evaluation/test_unmapped_ghost.py`\n", encoding="utf-8")
    assert "f007_design_test_map_covers_tasks" in _check_ids(cdc.check_f007_test_map_covers_tasks(tmp_path))
```
Hmm, appending a line with a test path not in design → check must go red. Good. But note: appending to tasks could break other things? No, we only call this check function.

Also need to register in CUSTOM_CHECKS.

Let me first check the existing test file's remaining part (lines 80+) to see how custom checks are tested, so I match style. Let me read the rest of the test file.
**D020** (Medium) — design §8 测试映射覆盖 tasks（含新增自定义一致性 check）。

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py</path>
<type>file</type>
<content>
80: def test_active_feature_indexes_go_red_on_claude_drift(tmp_path: pathlib.Path) -> None:
81:     _copy_index_tree(tmp_path)
82:     claude = tmp_path / "CLAUDE.md"
83:     claude.write_text(
84:         claude.read_text(encoding="utf-8").replace("F008 宇宙扩容", "F099 幽灵需求"),
85:         encoding="utf-8",
86:     )
87:     assert "active_feature_indexes_aligned" in _check_ids(
88:         cdc.check_active_feature_indexes(tmp_path)
89:     )
90: 
91: 
92: def test_active_feature_indexes_go_red_on_readme_drift(tmp_path: pathlib.Path) -> None:
93:     _copy_index_tree(tmp_path)
94:     readme = tmp_path / "docs" / "README.md"
95:     readme.write_text(
96:         readme.read_text(e
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:38:52Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-006` | property + integration | `tests/unit/experiment_store/test_research_snapshot.py`、`tests/unit/experiment_store/test_identity.py` | latest 先冻结；codec/path 不入身份，成员/cutoff/映射日历进入 snapshot 身份 |\n| 输入契约（AC-006/AC-008） | contract | `tests/contract/test_f007_upstream_contracts.py` | F002/F003/F008 上游契约摄入与 `source=placeholder` 分层 |\n| `AC-003` cohort 登记 | integration | `tests/integra
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:", "oldString": "def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:\n"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 11 nodes, 146 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:39:54Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "TEST_FILE_RE = re.compile(r\"tests/[A-Za-z0-9_./-]+\\.py\")\n\n\ndef check_f007_design_test_map_covers_tasks(root: pathlib.Path) -> list[tuple[str, str]]:\n    \"\"\"F007-D020：tasks 声明的测试文件必须能在 design §8 映射表里找到。\n\n    单向校验（tasks ⊆ design）：design 允许比 tasks 多列后备方案，反之则说明\n    tasks 的 verify 载体没有落进设计映射，测试面无人负责。\n    \"\"\"\n    errors: list[tuple[str, str]] = []\n    design_map = set(TEST_FILE_RE.findall(rea
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py", "newString": "def test_ac_body_coverage_goes_red(tmp_path: pathlib.Path) -> None:\n    target = tmp_path / cdc.SPEC\n    target.parent.mkdir(parents=True, exist_ok=True)\n    shutil.copyfile(REPO / cdc.SPEC, target)\n    target.write_text(\n        target.read_text(encoding=\"utf-8\").replace(\"DR-001 运行字段\", \"运行字段\"),\n        encoding=\"utf-8\",\n    )\n    assert cdc.AC_FINDING in _check_ids(cdc.check_ac_
…[truncated])`


> [reasoning] Oops, the second edit was a no-op-ish (removed a blank line). Not harmful but let me now add the custom check function properly.

Let me add the regex + function before CUSTOM_CHECKS and register it.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 156 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 14 nodes, 134 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:40:07Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"design_test_map\" 2>&1 | tail -3"})`

  <details><summary>tool output</summary>

  ```text
File "/home/georg/projects/alphamill/tools/check_doc_consistency.py", line 466
    expected = set(active_features(root))
IndentationError: unexpected indent


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:40:14Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "offset": 458, "limit": 18})`


> [reasoning] My earlier "no-op" edit removed the blank line after the function signature line, breaking the function (it removed the newline that terminated the def line? Let me look at the area).

Actually what happened: I replaced "def check_active_feature_indexes(...):\n" with "def check_active_feature_indexes(...):" — removing the trailing newline, which joined the def line with the next line? No — removing "\n" at the end of oldString means the newString ends without newline, so the following line got concatenated? Actually oldString was `def ...:\n` (including newline) and newString `def ...:` (without newline). The following content started with "    errors: ..." on the next line, and since the newline was consumed... hmm, the result would be `def check_active_feature_indexes(root):    errors: list[...]`? Let me just read that region and fix.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_doc_consistency.py</path>
<type>file</type>
<content>
458:             continue
459:         for needle in needles:
460:             if needle not in body:
461:                 errors.append((AC_FINDING, f"AC-{ac_num} 断言未覆盖其引用的子句 {needle!r}"))
462:     return errors
463: 
464: 
465: def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:    errors: list[tuple[str, str]] = []
466:     expected = set(active_features(root))
467: 
468:     backlog_rows: set[str] = set()
469:     for line in read(root, "BACKLOG.md").replace("\r\n", "\n").split("\n"):
470:         if line.lstrip().startswith("## "):
471:             break
472:         m = BACKLOG_ROW_RE.match(line.strip())
473:         if m:
474:             backlog_rows.add
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:40:20Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:\n    errors: list[tuple[str, str]] = []", "oldString": "def check_active_feature_indexes(root: pathlib.Path) -> list[tuple[str, str]]:    errors: list[tuple[str, str]] = []"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 156 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:40:27Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py -k \"design_test_map\" 2>&1 | tail -3 && .venv/bin/ruff check tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && .venv/bin/ruff format --check tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
.                                                                        [100%]
1 passed, 53 deselected in 0.08s
All checks passed!
2 files already formatted


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:40:34Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && git commit -q -m \"fix(f007): D020 design §8 补齐测试映射并加 tasks⊆design 一致性门\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
d9e0dd3 fix(f007): D020 design §8 补齐测试映射并加 tasks⊆design 一致性门


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:40:41Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果（阶段 ID 冻结为 `signal_quality`、`portfolio_transform`、`cost_capacity`、`temporal_stability`、`execution_implementation`，与 design §3.3 同一清单）；FactorDef 运行\n可将尚不适用的后续阶段显式记为 `NOT_APPLICABLE`，不得记为 PASS。", "oldString": "系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果；FactorDef 运行\n可将尚不适用的后续阶段显式记为 `NOT_APPLICABLE`，不得记为 PASS。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| cohort 状态 | `cohort_verdict.status` | `OPEN \\| FINALIZED` | 承诺成员未收齐时恒为 `OPEN`，不产生可晋级结论 |\n\n**五阶段 ID（冻结；spec FR-003 引用同一清单）**：\n\n| `stage_id` | 名称 | `owner` | 因子运行的适用性 |\n|---|---|---|---|\n| `signal_quality` | 信号质量 | `signal` | 必填 |\n| `portfolio_transform` | 组合转换 | `portfolio` | 可为 `NOT_APPLICABLE`（需给原因） |\n| `cost_capacity` | 成本/容量 | `cost` | 必填 |\n| `temporal_stability` | 时序稳定 |
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T014 (`FR-006`, `AC-007`, `AC-012`): 实现只消费 canonical 的 synthesis builder 与五阶段/三维失败汇总（按 design §3.3 冻结的 `failure_taxonomy` schema 与五阶段 ID 枚举聚合，未知取值失败关闭）；漏斗第一级只读摄取 F003 的 `generation.run_completed`（仅 `status=completed`）与 `generation.candidate_rejected`（按原因码） — verify: `tests/integration/test_f007_synthesis.py`", "oldString": "- [ ] T014 (`FR-006`, `AC-007`): 实现只消费 canonical 的 synthes
…[truncated])`


> [reasoning] 20/25. **D021**: five stage IDs + failure taxonomy schema.

spec FR-003: add stage IDs:
"系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果（阶段 ID 冻结为 `signal_quality`、`portfolio_transform`、`cost_capacity`、`temporal_stability`、`execution_implementation`）"

design §3.3 or §4: add stage ID enum table + failure taxonomy schema:
```
**五阶段 ID（冻结，spec FR-003 引用同一清单）**：

| stage_id | 名称 | owner | 适用性 |
|---|---|---|---|
| `signal_quality` | 信号质量 | signal | 因子运行必填 |
| `portfolio_transform` | 组合转换 | portfolio | FactorDef 运行可为 `NOT_APPLICABLE` |
| `cost_capacity` | 成本/容量 | cost | 必填 |
| `temporal_stability` | 时序稳定 | statistics | 必填 |
| `execution_implementation` | 执行实现 | execution | FactorDef 运行可为 `NOT_APPLICABLE` |

**失败维度 schema（`failure_taxonomy`，三维）**：每条失败记录必填 `{stage, owner, mechanism, error_code, first_seen, evidence_refs}`；`stage` 取上表枚举；`owner` ∈ `data|signal|method|statistics|cost|execution|infra`；`mechanism` ∈ `missing_input|invalid_input|capability_unguarded|lookahead|estimator_failure|publish_failure|underpowered|cost_negative`。synthesis 按 `(stage, owner, mechanism)` 三维聚合，未知枚举值失败关闭。
```
tasks T014: add "failure_taxonomy 三维 schema".

Check D021: requires (F007_SPEC, "`signal_quality`"), (F007_DESIGN, "`signal_quality`"), (F007_DESIGN, "`execution_implementation`"), (F007_DESIGN, "failure_taxonomy"), (F007_TASKS, "failure_taxonomy").

Let me apply.
**D021** (Medium) — 冻结五阶段 ID 与失败三维 schema。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:42:38Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-011** (`FR-006`, `NFR-004`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本\n- [ ] **AC-012** (`FR-003`): 五阶段 ID 与失败三维 schema 冻结并可校验——stage 取值限于 `signal_quality`/`portfolio_transform`/`cost_capacity`/`temporal_stability`/`execution_implementation`，`failure_taxonomy` 记录含 stage/owner/mechanism/error_code/evidence_refs，synthesis 按三维聚合且
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"最终确认窗\"),\n        ),\n    ),\n    TextCheck(\n        \"stage_ids_and_failure_dimensions_frozen\",\n        \"F007-D021\",\n        requires=(\n            (F007_SPEC, \"`signal_quality`\"),\n            (F007_SPEC, \"**AC-012**\"),\n            (F007_DESIGN, \"`execution_implementation`\"),\n            (F007_DESIGN, \"failure_taxonomy\"),\n            (F007_TASKS, \"failure_t
…[truncated])`


> [reasoning] I referenced AC-012 in T014 but haven't created AC-012 yet (planned for D021). Let me add AC-012 to spec now (this is D021's AC).

AC-012:
```
- [ ] **AC-012** (`FR-003`): 五阶段 ID 与失败三维 schema 冻结并可校验——stage 取值限于五个冻结 ID，failure_taxonomy 记录含 stage/owner/mechanism/error_code/evidence_refs，synthesis 按三维聚合且拒绝枚举外取值
```
Add after AC-011.

Also T014 tags AC-012 ✓.

Check D021 needles. Let me apply + add check.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 157 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:42:49Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D021 冻结五阶段 ID 与 failure_taxonomy 三维 schema\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
5b26dac fix(f007): D021 冻结五阶段 ID 与 failure_taxonomy 三维 schema


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:42:57Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-011** (`NFR-004`, `NFR-005`, `UX-001`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本；产物路径与 manifest 只用 POSIX 逻辑路径/URI（Windows/WSL 物理路径只进 provenance）；CLI 首屏含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定）", "oldString": "- [ ] **AC-011** (`FR-006`, `NFR-004`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T006 (`IR-001`, `IR-003`, `AC-008`, `AC-011`): 实现 preview CLI 与稳定结构化输出/错误码，首屏固定含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定） — verify: `tests/integration/test_f007_cli.py`", "oldString": "- [ ] T006 (`IR-001`, `IR-003`, `AC-008`): 实现 preview CLI 与稳定结构化输出/错误码 — verify: `tests/integration/test_f007_cli.py`"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T015 (`FR-006`, `UX-002`, `AC-005`, `AC-011`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推；断言 `approximation` 标注存在、canonical 恒为非近似，并对产物路径做 POSIX 逻辑路径断言（Windows/WSL 物理路径只进 provenance） — verify: `tests/contract/test_f007_artifact_schemas.py`", "oldString": "- [ ] T015 (`FR-006`, `UX-002`, `AC-005`, `AC-011`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推；断言 `approximati
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| `AC-011` | contract + integration | `tests/contract/test_f007_artifact_schemas.py`、`tests/integration/test_f007_cli.py` | `approximation` 标注存在；canonical 非近似；POSIX 逻辑路径；CLI 首屏字段快照 |", "oldString": "| `AC-011` | contract + integration | `tests/contract/test_f007_artifact_schemas.py` | `approximation` 标注存在；canonical 非近似；POSIX 逻辑路径；CLI 首屏字段快照 |"})`


> [reasoning] 21/25. **D022**: NFR-005 / UX-001 → AC-011 references + tasks verify.

Edit AC-011 line to include NFR-005 and UX-001:
```
- [ ] **AC-011** (`NFR-004`, `NFR-005`, `UX-001`): preview 近似在报告显式标注；产物路径与 manifest 只用 POSIX 逻辑路径/URI（Windows/WSL 物理路径只进 provenance）；CLI 首屏含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定）
```
Note: D014's check required literal "**AC-011** (`FR-006`, `NFR-004`)" — if I change the tags, D014's check will FAIL! I must update D014's check needle too. Hmm. D014's check needle is `(F007_SPEC, "**AC-011** (`FR-006`, `NFR-004`)")`. Now AC-011 becomes `(`NFR-004`, `NFR-005`, `UX-001`)`. So I need to change D014's needle to something else, e.g. `(F007_SPEC, "`approximation` 字段显式标注")` which stays. Let me update D014's check in this commit (D022) — allowed, it's a check adjustment; I'll note it.

Actually cleaner: keep D014's needle stable by choosing a text-independent needle. Let me change D014's check to require (F007_SPEC, "preview 的采样/缩窗在报告") — hmm after D022 edit, AC-011 text becomes "preview 近似（采样/缩窗）在报告中显式标注（`approximation` 字段…）". Let me just pick needle "NFR-004" for spec (exists) and "`approximation`" for spec. D014's check then: (F007_SPEC, "NFR-004"), (F007_SPEC, "`approximation`"), (F007_DESIGN, "`approximation`"), (F007_TASKS, "`approximation`").

I'll update D014's check in the D022 commit. That's a legitimate adjustment of an evidence needle (and I'll mention it in FIX-log).

tasks: T015 already has AC-011 tag; add POSIX path assertion to T015 and CLI 首屏 to T006.
- T006: "实现 preview CLI 与稳定结构化输出/错误码 — verify: tests/integration/test_f007_cli.py" → add "首屏固定含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定）".
- T015: add "并对产物路径做 POSIX 逻辑路径断言（Windows/WSL 物理路径只进 provenance）".

Check D022: requires (F007_SPEC, "**AC-011** (`NFR-004`, `NFR-005`, `UX-001`)"), (F007_TASKS, "POSIX 逻辑路径"), (F007_DESIGN, "首屏").

design §6 already mentions CLI 首屏; design §7 兼容 mentions 逻辑 artifact URI. Good — add needle (F007_DESIGN, "POSIX").

Let me apply.
**D022** (Medium) — NFR-005 / UX-001 追溯闭环。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:43:56Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        requires=(\n            (F007_SPEC, \"NFR-004\"),\n            (F007_SPEC, \"`approximation`\"),\n            (F007_DESIGN, \"`approximation`\"),\n            (F007_TASKS, \"`approximation`\"),\n        ),\n    ),", "oldString": "        requires=(\n            (F007_SPEC, \"**AC-011** (`FR-006`, `NFR-004`)\"),\n            (F007_DESIGN, \"`approximation`\"),\n            (F007_TASKS, \"`approxima
…[truncated])`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"failure_taxonomy\"),\n        ),\n    ),\n    TextCheck(\n        \"nfr005_ux001_traceable\",\n        \"F007-D022\",\n        requires=(\n            (F007_SPEC, \"**AC-011** (`NFR-004`, `NFR-005`, `UX-001`)\"),\n            (F007_SPEC, \"POSIX 逻辑路径\"),\n            (F007_TASKS, \"POSIX 逻辑路径断言\"),\n            (F007_TASKS, \"首个失败原因（快照测试锁定）\"),\n            (F007_DESIGN, \"POSIX
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 157 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 158 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py 2>&1 | tail -3 && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py tests/unit/test_check_doc_consistency.py && git commit -q -m \"fix(f007): D022 NFR-005/UX-001 落 AC-011 与 tasks verify\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
=========================== short test summary info ============================
FAILED tests/unit/test_check_doc_consistency.py::test_f007_upstream_declaration_goes_red
1 failed, 55 passed in 1.71s
80cbd3d fix(f007): D022 NFR-005/UX-001 落 AC-011 与 tasks verify


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:14Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py", "newString": "    target.write_text(\n        target.read_text(encoding=\"utf-8\").replace(\n            \"related_features: [F002, F003, F004, F008]\", \"related_features: [F002, F004, F008]\"\n        ),\n        encoding=\"utf-8\",\n    )\n    assert \"f007_declares_f003_upstream\" in _check_ids(cdc.check_f007_declares_f003(tmp_path))", "oldString": "    target.write_text(\n        target.read_text(encodin
…[truncated])`


> [reasoning] A pre-existing test now fails: `test_f007_upstream_declaration_goes_red` — it replaced "related_features: [F002, F003, F004]" with "related_features: [F002, F004]" in F007 spec and asserted the `f007_declares_f003_upstream` check goes red. But my D003 edit changed the F007 spec frontmatter to `[F002, F003, F004, F008]`, so the replace no longer matches → no drift → check stays green → test fails.

This is a test that needs updating as part of D003's change (it's a fixture-of-reality assertion). It's my change that broke it (the needle). I should fix it now (and note it). The fix: update the replace target to the new frontmatter value: replace "related_features: [F002, F003, F004, F008]" → "related_features: [F002, F004, F008]".

Also `test_active_feature_indexes_go_red_on_readme_drift` uses "活跃 feature 索引（当前 F003/F007/F008）" — unchanged.

Let me fix the test and amend? No — I already committed D022. The failing test belongs conceptually to D003. Since the skill says don't amend a failed commit... it didn't fail; it's a follow-up fix. I'll create a small follow-up commit fixing the test needle (and record it as a fix-regression note). Actually better: include it in the next commit? No, it should be its own small fix commit to keep bisect clean. Let me commit it now as a `test(f007)` fix for D003's regression.

Wait, careful: this is exactly the "fix-regression" the skill warns about (per-round self-harm). It's my change breaking an existing test — I should record it honestly in FIX-log as a fix-regression note. Let me fix it now.
Pre-existing mutation test broke on my D003 frontmatter change (its needle was the old value). Fixing that regression explicitly.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 14 nodes, 134 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:25Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py 2>&1 | tail -3 && git add -A tests/unit/test_check_doc_consistency.py && git commit -q -m \"test(f007): 修正 F003 上游变异测试针脚以对齐 D003 后的 frontmatter\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
........................................................                 [100%]
56 passed in 0.96s
24a7631 test(f007): 修正 F003 上游变异测试针脚以对齐 D003 后的 frontmatter


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:36Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "> **开发前置约束**：`tasks.md` §3 的 `[TEST]` 组（层 2 旅程验收轨，编写早、执行晚）是进入代码\n> 开发的硬性前置门；约束的落地形态与执行规则见 `tasks.md`（design 只声明该约束，不展开步骤）。", "oldString": "> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——\n> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。\n> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。\n- `[TEST]` 组（§3）是开发前置门：从 US-001/US-002/US-003 旅程步骤派生（每步骤 ≥1 条可执行断言），编写早（Phase 1 先立红灯）、执行晚（收尾全量跑）；缺失即被 SDD Flow T3 拒绝流转。\n- 属性测试与变异证据可复现：属性测试固定 seed 并约束输入生成器（见 design §8），变异结果写 `reports/mutation/f007/mutation_report.json`。", "oldString": "- 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"POSIX\"),\n        ),\n    ),\n    TextCheck(\n        \"design_no_task_directives\",\n        \"F007-D023\",\n        requires=(\n            (F007_DESIGN, \"约束的落地形态与执行规则见 `tasks.md`\"),\n            (F007_TASKS, \"编写早\"),\n            (F007_TASKS, \"[TEST] 组（§3）是开发前置门\"),\n        ),\n        forbids=((F007_DESIGN, \"开工门禁（SDD Flow T3）会拒绝缺失该组的流转\"),),\n    ),", "oldString": " 
…[truncated])`


> [reasoning] All 56 tests pass now. 22/25. **D023**: move design:16-18 instruction to tasks.

design currently has:
```
> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。
```
Replace with a one-line constraint pointing at tasks:
```
> **开发前置约束**：`tasks.md` §3 的 `[TEST]` 组（层 2 旅程验收轨，编写早、执行晚）是进入代码
> 开发的前置门；约束的落地形态与执行规则见 `tasks.md`。
```
Check forbids the old text "开工门禁（SDD Flow T3）会拒绝缺失该组的流转".

tasks §0 add execution rule:
```
- `[TEST]` 组（§3）是开发前置门：从 US-001/002/003 旅程步骤派生，编写早（Phase 1 先立红灯）、执行晚（收尾全量跑）；缺失即被 SDD Flow T3 拒绝流转。
```

Check D023: requires (F007_TASKS, "### [TEST] 组：层 2 旅程验收轨"), (F007_TASKS, "编写早"), (F007_DESIGN, "见 `tasks.md`"), forbids (F007_DESIGN, "开工门禁（SDD Flow T3）会拒绝缺失该组的流转").

Careful: my new design text says "约束的落地形态与执行规则见 `tasks.md`。" — needle "见 `tasks.md`" ✓.

Let me apply.
**D023** (Low, `responsibility-boundary-violation`) — 行动指令移入 tasks。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 159 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:48Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D023 design 行动指令移入 tasks，只保留前置约束声明\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 失败
  - [design_no_task_directives] 缺少要求文本 '[TEST] 组（§3）是开发前置门'（docs/features/0.2/F007-evaluation-gates/tasks.md）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:44:56Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_TASKS, \"组（§3）是开发前置门\"),", "oldString": "            (F007_TASKS, \"[TEST] 组（§3）是开发前置门\"),"})`


> [reasoning] The tasks text I wrote is "`[TEST]` 组（§3）是开发前置门" — with backticks. Fix needle to "组（§3）是开发前置门".

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 159 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:45:08Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D023 design 行动指令移入 tasks，只保留前置约束声明\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
e29563e fix(f007): D023 design 行动指令移入 tasks，只保留前置约束声明


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:45:17Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- **TR-003**：canonical population 登记应使用 `evaluation.registered` 事件（以 experiment_id 为幂等键）并引用 manifest ID；canonical 产物物理落 `reports/bench/`，与 preview 的 `reports/preview/` 物理隔离。", "oldString": "- **TR-003**：canonical population 登记应使用 experiment_id 幂等键并引用 manifest ID。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "不变量：", "oldString": "不变量：\n"})`


> [reasoning] 23/25. **D024**: state vocab + canonical=bench + `evaluation.registered` in TR-003.

spec TR-003: rewrite to name the event:
```
- **TR-003**：canonical population 登记应使用 `evaluation.registered` 事件（以 experiment_id 为幂等键）并引用 manifest ID；canonical 产物物理落 `reports/bench/`，与 preview 的 `reports/preview/` 隔离。
```
spec §5 lifecycle: `canonical EVIDENCE_READY -> REGISTERED` — add mapping note: "(canonical 物理根 `reports/bench/`，`REGISTERED` 对应 `evaluation.registered` 事件)". Let me add after lifecycle code block or in 不变量. I'll add a line right after the code block:
```
状态与物理/事件映射：preview 落 `reports/preview/`，`PREVIEW_DONE` 为隔离终态；canonical 落 `reports/bench/`，`REGISTERED` 对应 `evaluation.registered` 事件；`FINALIZED` 对应 `cohort_verdict.json` 原子写出。
```
design: TR contract event type list already includes `evaluation.registered` ✓; §3.2 dir has bench ✓. design §3.2 add note mapping? Let me add "canonical 物理落 `reports/bench/`（spec 生命周期 `REGISTERED` ↔ `evaluation.registered` 事件）".

Check D024: requires (F007_SPEC, "evaluation.registered"), (F007_SPEC, "`reports/bench/`"), (F007_SPEC, "PREVIEW_DONE"), (F007_DESIGN, "`reports/bench/`").

Let me apply.
**D024** (Low) — 状态词汇与 canonical=bench 映射。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:45:32Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 16, "offset": 247})`


> [reasoning] Careful — that second edit may have merged lines like before. The oldString was "不变量：\n" and newString "不变量：" — this removes a newline after "不变量：", which would join it with the next line ("- preview 永远不能转写为 canonical；..."). That's a formatting change, not necessarily breaking. Let me check and then add the mapping line properly.

Actually that was a careless call — I intended to insert a mapping line but wrote a no-op-ish edit. Let me read the region and fix it by inserting the mapping note.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
247: - **NFR-002**：可复现：固定 ResearchSnapshot 与其他语义输入跨路径/Parquet 编码重跑得到相同 snapshot/experiment ID 与数值容差内相同报告。
248: - **NFR-003**：安全：Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力；**最终确认窗**统计量不得出现于任何 Agent/preview 可读的 report/manifest/synthesis，越权读取或写入即 fail-closed 并留拒绝事件（ADR-0003 复盘循环窥探防护）。
249: - **NFR-004**：性能：preview 可采样/缩窗但必须显式标注近似；canonical 不因性能压力静默减少门禁或样本。
250: - **NFR-005**：兼容性：产物路径和 manifest 使用 POSIX 逻辑路径/URI，Windows/WSL 物理路径只进 provenance。
251: 
252: ## 5. 生命周期与不变量
253: 
254: ```text
255: CREATED -> VALIDATING       身份与输入可解析
256: VALIDATING -> RUNNING       方法论/PIT/纯度门通过
257: RUNNING -> EVIDENCE_READY   必需阶段完成且产物原子发布
258: 任意非终态 -> INCOMPLETE   输入、估计器、发布或恢复失败
259: can
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:45:40Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 12, "offset": 262})`

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
262: ```
263: 
264: 不变量：
265: - preview 永远不能转写为 canonical；晋级意图必须以冻结上下文重新执行 canonical。
266: - 任何 PASS/promising 都必须能追到完整 manifest、规则版本、data value digest 和 code/build digest。
267: - canonical 成员登记不等于晋级；cohort 未 FINALIZED 时不得产生可晋级结论。
268: - 必需门被 skip、warning 或 null 时，运行不能进入 `EVIDENCE_READY/REGISTERED`。
269: - 历史证据不覆盖；变化产生新 ID，并通过 supersedes 表达替代关系。
270: - 无前视三层归属显式：L1 由本 Feature 方法论守卫 fail-closed 执行；L2/L3 owner 为 F006/M3，非 `PASS` 前不得晋级 paper，缺失层记 `not_yet_available` 并携带 owner（`FR-007`）。
271: 
272: ## 6. 成功与验收
273: 

(Showing lines 262-273 of 323. Use offset=274 to continue.)
</content>
  ```
  </details>

## assistant · 2026-09-16T16:45:46Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "```\n\n状态与物理/事件映射：preview 落 `reports/preview/`，`PREVIEW_DONE` 为隔离终态；canonical 落\n`reports/bench/`，`REGISTERED` 对应 `evaluation.registered` 事件（`TR-003`）；`FINALIZED` 对应\n`cohort_verdict.json` 原子写出。\n\n不变量：\n- preview 永远不能转写为 canonical；晋级意图必须以冻结上下文重新执行 canonical。", "oldString": "```\n\n不变量：\n- preview 永远不能转写为 canonical；晋级意图必须以冻结上下文重新执行 canonical。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "每个 canonical artifact 目录只写一次。canonical 物理落 `reports/bench/`，spec 生命周期 `REGISTERED`\n对应 `evaluation.registered` 事件，`PREVIEW_DONE` 对应 `reports/preview/` 的隔离终态。", "oldString": "每个 canonical artifact 目录只写一次。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        forbids=((F007_DESIGN, \"开工门禁（SDD Flow T3）会拒绝缺失该组的流转\"),),\n    ),\n    TextCheck(\n        \"state_vocab_and_bench_mapping_aligned\",\n        \"F007-D024\",\n        requires=(\n            (F007_SPEC, \"`evaluation.registered`\"),\n            (F007_SPEC, \"`reports/bench/`\"),\n            (F007_SPEC, \"`PREVIEW_DONE`\"),\n            (F007_DESIGN, \"`reports/bench/`\"),\n            (F007_DES
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 160 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 160 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:45:57Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D024 对齐状态词汇、canonical=bench 与 evaluation.registered\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
aa348bb fix(f007): D024 对齐状态词汇、canonical=bench 与 evaluation.registered


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:05Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls tests/ && ls tests/* -d 2>/dev/null | head -20"})`


> [reasoning] 24/25. **D025**: property test execution task + seed/generator constraints.

tasks §3 add T026 before the [TEST] heading:
```
- [ ] T026 (`DR-001`, `DR-002`, `NFR-002`): 属性测试轨——身份稳定（同语义输入任意路径/codec 重跑得同一 ID）与 ResearchSnapshot 变化敏感性（成员/cutoff/映射日历变化必产生新 ID）以属性测试执行；固定可复现 seed、输入生成器由显式策略枚举（不依赖随机数据分布），失败样本落 `reports/property/f007/<seed>/` — verify: `pytest -q tests/property/test_f007_identity_properties.py`
```
design §8 add row + statement about seed/generator.
tasks §4 edge: `T004/T019 -> T026` and add T026 to the [TEST] predecessors? Not needed but let me add `T004/T019 -> T026`.

Hmm, T019 is a verify task (runs identity property tests). Edge T019 -> T026 is forward (19<26) ✓. But logically T026 should come before T019 runs it... eh. Let me instead use `T004 -> T026` only, plus `T026 -> T019`? T019 < T026 so that'd be a backward edge (forbidden). Hmm.

Problem: T019 (verify task) already includes `tests/unit/experiment_store/test_identity.py`. If I add a new property test path `tests/property/test_f007_identity_properties.py`, then T019's verify should include it, and T026 (the property track task) must come before T019 numerically for the DAG to be coherent... but T019 is T019 and T026 > T019. The gate only errors on backward edges (src >= dst) if an edge declares T026 -> T019. So I must not declare that edge. And the max task is T030 which has incoming edges ✓. So no edge needed between T019 and T026.

But then the design §8 mapping check: tasks uses `tests/property/test_f007_identity_properties.py` → must be in design §8. I'll add it.

Also the D020 check (tasks ⊆ design) will require the new file in design. I'll add it in the same commit.

Also the property test file must be referenced in design §8 with full `tests/...py` path.

Let me write design §8 addition:
```
| `AC-006`/`NFR-002` 属性测试 | property | `tests/property/test_f007_identity_properties.py` | 身份稳定与快照敏感性；固定可复现 seed，输入由显式策略枚举（不依赖随机分布），反例落盘 |
```
And a paragraph: "属性测试输入必须由显式策略生成并固定可复现 seed（`--property-seed`，写入 manifest）；禁止依赖随机数据分布；失败反例落 `reports/property/f007/<seed>/`。"

Hmm, but is a `tests/property/` dir consistent with repo layout? There's no tests/property dir currently. Let me check the tests dirs: tests/unit, tests/integration, tests/contract, tests/mutation? Let me check whether tests/contract and tests/mutation exist.

Actually the tasks reference tests/contract/test_f007_*.py and tests/mutation/test_f007_gate_mutations.py — do those dirs exist? Let me check. If they don't, the D020 check still passes (design textual), but `validate_spec_lifecycle` only checks test path existence for review/done status. F007 is draft → fine. But let me check the repo layout for consistency.

Let me check dirs quickly, then write.
**D025** (Low) — 属性测试执行轨与 seed/生成器约束。

  <details><summary>tool output</summary>

  ```text
integration
property
simulation
unit
tests/integration
tests/property
tests/simulation
tests/unit


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:17Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls tests/property/ && sed -n '1,25p' tests/property/*.py | head -40"})`


> [reasoning] `tests/property` exists. `tests/contract` and `tests/mutation` do NOT exist yet (they're F007-planned files for a future feature — that's fine at draft; the F003 review's proposed tests also are future). Hmm, wait: the existing design §8 already referenced `tests/contract/test_f007_artifact_schemas.py` and tasks too. The repo has no tests/contract dir. That's pre-existing (draft feature, planned tests). OK, acceptable.

Let me look at tests/property content to match convention.

  <details><summary>tool output</summary>

  ```text
zsh:1: no matches found: tests/property/*.py


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:24Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && find tests/property -type f | head -10"})`

  <details><summary>tool output</summary>

  ```text
tests/property/.gitkeep


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:31Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- [ ] T026 (`DR-001`, `DR-002`, `NFR-002`): 属性测试轨——身份稳定（同语义输入任意路径/codec 重跑得同一 ID）与 ResearchSnapshot 变化敏感性（成员/cutoff/映射日历变化必产生新 ID）以属性测试执行；固定可复现 seed、输入生成器由显式策略枚举（不依赖随机数据分布），反例落 `reports/property/f007/<seed>/` — verify: `pytest -q tests/property/test_f007_identity_properties.py`\n\n### [TEST] 组：层 2 旅程验收轨（必填）", "oldString": "### [TEST] 组：层 2 旅程验收轨（必填）"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "| 第二实现对照 | unit | `tests/unit/evaluation/test_second_implementation.py` | 独立实现与自研统计在既定容差内一致 |\n| `AC-006`/`NFR-002` 属性测试 | property | `tests/property/test_f007_identity_properties.py` | 身份稳定与快照敏感性；固定可复现 seed，输入由显式策略枚举 |", "oldString": "| 第二实现对照 | unit | `tests/unit/evaluation/test_second_implementation.py` | 独立实现与自研统计在既定容差内一致 |"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；", "oldString": "另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；\n"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:43Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"funding carry/BTC-ETH\" -A 6 docs/features/0.2/F007-evaluation-gates/design.md"})`


> [reasoning] Oops, that third edit again risked joining lines. Let me check the design §8 tail region and add the seed/generator paragraph properly.

  <details><summary>tool output</summary>

  ```text
316:另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异，
317-逐 mutant 产出 kill 证据到 `reports/mutation/f007/mutation_report.json`（无 survived 项才算通过），
318-变异工具版本按 SOP §1 在 dev 依赖 pin 范围上界。
319-
320-## 9. 已确认决策与残余风险
321-
322-| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:46:53Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "newString": "变异工具版本按 SOP §1 在 dev 依赖 pin 范围上界。\n\n属性测试的可复现约束：固定可复现 seed（`--property-seed`，写入 manifest），输入由显式策略枚举生成\n（不依赖随机数据分布，也不默认引入第三方 property-testing 框架；如引入则按 SOP §1 pin 版本范围），\n失败反例落 `reports/property/f007/<seed>/` 供复现。", "oldString": "变异工具版本按 SOP §1 在 dev 依赖 pin 范围上界。"})`
- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "            (F007_DESIGN, \"`evaluation.registered`\"),\n        ),\n    ),\n    TextCheck(\n        \"property_strategy_has_execution_task\",\n        \"F007-D025\",\n        requires=(\n            (F007_TASKS, \"属性测试轨\"),\n            (F007_TASKS, \"显式策略枚举\"),\n            (F007_DESIGN, \"固定可复现 seed\"),\n            (F007_DESIGN, \"`tests/property/test_f007_identity_properties.py`\"),\n        ),\n    
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 161 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 161 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:47:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py 2>&1 | tail -3"})`

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过
............................................................             [100%]
60 passed in 1.97s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:47:15Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A docs/features/0.2/F007-evaluation-gates tools/check_doc_consistency.py && git commit -q -m \"fix(f007): D025 属性测试执行轨与 seed/生成器可复现约束\" && git log --oneline -1"})`

  <details><summary>tool output</summary>

  ```text
b345e25 fix(f007): D025 属性测试执行轨与 seed/生成器可复现约束


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:47:25Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python - <<'PY'\nimport pathlib, sys\nsys.path.insert(0, \".\")\nfrom tools import check_task_dag as dag\nfrom tools import check_doc_consistency as cdc\nfrom tools import validate_spec_lifecycle as vsl\n\nroot = pathlib.Path(\".\").resolve()\nf007 = root / \"docs/features/0.2/F007-evaluation-gates\"\n\n# 1) task DAG on F007 tasks (even though status=draft, gate not enforced)\ntasks_text = (f007 / \"tasks.md\").read_text(encoding=\"utf-
…[truncated])`


> [reasoning] All 25 findings fixed. Now:

1. Update todos.
2. Final consistency verification: run the full doc gates, check the task DAG explicitly (F007 is draft so check_task_dag won't enforce; but I should verify the DAG logic would pass when it becomes ready-for-development). Let me run check_task_dag's `check_tasks` on F007 tasks directly via python to confirm no backward edges / all endpoints defined / max has incoming edge / [P] rule.
3. Verify the mutation-verification of new gates on the REAL repo (not just synthetic) — the skill requires "开门禁才有牙：新增/修改的每个门禁，必须当场做一次变异验证——删必填字段、改 ID、走旁路路径，门禁必须变红". The pytest mutation tests do this on tmp_path copies. The F003 FIX-log also did a real-repo mutation for one check. Let me do one real-repo mutation demonstration for a new F007 check and restore.
4. Run full `tools/verify.py` (round-end full gate, once).
5. Append FIX-log.md declaration with evidence trio.
6. Do NOT touch CURRENT-doc-F007.md; do NOT delete files; do not push.

Let me first check the [TEST] group requirement + task DAG by simulating status=ready-for-development? The gate functions take root and read actual spec status. To verify F007's tasks would pass the DAG gate, I can call `check_tasks(tasks_text)` directly.

Also I should double check `validate_spec_lifecycle` structure: AC uniqueness, requirement refs — all pass already (it ran green).

Let me run a verification script.
All 25 findings landed. Verifying the DAG/`[TEST]` gates would hold for F007 once it leaves `draft`, plus a real-repo mutation check on the new gates.

  <details><summary>tool output</summary>

  ```text
DAG errors: none
task ids: 30 min T001 max T030 unique True
edges: [('T007', 'T010'), ('T007', 'T011'), ('T009', 'T012'), ('T009', 'T025'), ('T012', 'T013'), ('T012', 'T016'), ('T012', 'T024'), ('T013', 'T024'), ('T014', 'T016'), ('T016', 'T025'), ('T027', 'T030'), ('T028', 'T030'), ('T029', 'T030')]
max has incoming: True
[TEST] group present: True
test-map errors: none
all doc-consistency errors: none


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:47:39Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python - <<'PY'\nimport pathlib, shutil, sys, tempfile\nsys.path.insert(0, \".\")\nfrom tools import check_doc_consistency as cdc\nfrom tools import validate_spec_lifecycle as vsl\n\nroot = pathlib.Path(\".\").resolve()\nREL = [cdc.F007_SPEC, cdc.F007_DESIGN, cdc.F007_TASKS]\nALL = set(REL) | {cdc.SPEC, cdc.DESIGN, cdc.TASKS}\n\ndef ids(errs): return {cid for cid, _ in errs}\n\ndef mutate(rel, old, new, fn, label):\n    with tempfile.Te
…[truncated])`


> [reasoning] DAG clean, 30 tasks contiguous T001..T030, no backward edges, max has incoming.

Note: the [TEST] predecessor list I planned (`T0xx -> T027/T028/T029`) wasn't added — the [TEST] tasks currently only have outgoing edges to T030. The DAG gate only requires max to have incoming edges, so it's fine. But logically the [TEST] journeys should have prerequisites (like F003's pattern). Should I add? The reviewer's D001 didn't require a predecessor list. The DAG gate is satisfied. Hmm, but for coherence, T027-T029 (journey acceptance) should depend on the acceptance suites. Let me add a predecessor edge to strengthen: `` `T016/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029` ``. That's 10×3 = 30 edges, forward (all < 27) ✓. This mirrors F003's pattern (`T030..T035 -> T036/T037/T038`). It improves quality and is consistent with the doc's intent.

Since it's beyond D001's required fix, I'd be adding scope. But D001's finding is about the [TEST] group; adding its prerequisite edges is part of making the [TEST] group usable/verifiable. And D008's finding is about missing edges generally. Hmm, I already committed D001. Adding another edge line = another commit. I think it's worth it for coherence (the [TEST] group otherwise floats). Let me add it as part of a final "R2 hardening" commit... but the skill says one finding per commit; extra coherence commits are fine as long as labeled honestly (F003's log had "附带提交" for such).

Actually, I earlier planned this and it's referenced in my [TEST] group note ("编写早、执行晚"). Let me add the edge line and mention it as an accompanying commit in FIX-log.

Now, real-repo mutation verification for the new gates. Let me do a couple of representative real-repo mutations:
1. Remove a required needle from F007 tasks (e.g. delete the `### [TEST] 组` heading) → check must go red. Restore.
2. Reintroduce a forbidden string in F007 design (e.g. append "--universe-calendar") → red. Restore.
3. Remove a test file path from design §8 → test-map check red. Restore.
4. Also the [TEST] lifecycle gate: simulate status=ready-for-development in a temp copy? The lifecycle gate depends on status; the mutation test for that already exists (`test_review_missing_test_group_rejected`). For F007 specifically, let me verify by temporarily flipping the frontmatter status in a tmp copy... Actually validate_spec_lifecycle reads the repo. Simulating in a temp copy is messy (BACKLOG etc.). Alternative: call `check_feature` on a synthesized feat dict with status ready-for-development and tasks text lacking [TEST]. Let me do that in-process — clean and no repo mutation.

Let me do these in one python script (mutations on tmp copies for the doc-consistency ones, in-process for lifecycle), and one real-repo mutation to satisfy "不只在合成树上" like F003 did.

Let me write it.

  <details><summary>tool output</summary>

  ```text
D001 remove [TEST] heading: RED (ok) -> ['f007_test_group_present']
D004 reintroduce merged flag: RED (ok) -> ['universe_calendar_artifacts_split']
D010 remove DR-005: STILL GREEN (BAD) -> []
D020 drop design mapping: RED (ok) -> ['f007_design_test_map_covers_tasks']
D023 reintroduce task directive: RED (ok) -> ['design_no_task_directives']
D007 remove T009->T012 edge: RED (ok) -> ['task_graph_missing_edges_f007']
lifecycle ready-for-dev without [TEST]: NONE (BAD)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:47:52Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py", "newString": "        requires=(\n            (F007_SPEC, \"**DR-005**：`HoldoutBudgetLedger`\"),\n            (F007_DESIGN, \"holdout_budget/ledger.jsonl\"),\n            (F007_TASKS, \"DR-005\"),\n            (F007_TASKS, \"留出预算台账\"),\n        ),", "oldString": "        requires=(\n            (F007_SPEC, \"DR-005\"),\n            (F007_SPEC, \"HoldoutBudgetLedger\"),\n            (F007_DESIGN, \"holdout_budget/ledger
…[truncated])`


> [reasoning] Two issues found by mutation verification — exactly what the skill wants:

1. **D010 remove DR-005 → STILL GREEN (BAD)**: My `holdout_budget_ledger_exists` check requires (F007_SPEC, "DR-005"), (F007_SPEC, "HoldoutBudgetLedger"), (F007_DESIGN, "holdout_budget/ledger.jsonl"), (F007_TASKS, "DR-005"), (F007_TASKS, "留出预算台账"). But wait, replacing "**DR-005**" with "**DR-X**" leaves "DR-005" still present in text (in other places? e.g. AC-001 references `DR-005`, T012 tags `DR-005`, design? and spec AC-001 has `DR-005`). The check only requires the literal "DR-005" which still exists in the AC line. So the mutation "删必填字段/改 ID" needs to remove all occurrences. My mutation was weak, not the check. But it does reveal the check could be stronger: require the *definition line* `**DR-005**：\`HoldoutBudgetLedger\``. Let me strengthen the D010 check: requires (F007_SPEC, "**DR-005**：`HoldoutBudgetLedger`").

Let me verify: spec text is "- **DR-005**：`HoldoutBudgetLedger` 应当以 append-only 台账持久化…". Yes. Strengthen and re-mutate.

2. **lifecycle ready-for-dev without [TEST] → NONE (BAD)**: Hmm! Why didn't the lifecycle gate flag it? Because my mutation replaced "### [TEST]" → "### 验收", but the text contains "### [TEST] 组：层 2 旅程验收轨（必填）" — replacing "### [TEST]" gives "### 验收 组：层 2 旅程验收轨（必填）". TEST_GROUP_RE = `^###\s+\[TEST\]` → no longer matches. So it should flag... unless `check_feature` returned early. Ah — `check_feature` reads `spec_fm` from feat["spec"] which I passed; status is `draft` (I didn't change it!). TEST_GROUP_STATUSES excludes draft → not enforced. My test was wrong: I need status=ready-for-development. Let me redo with modified spec frontmatter.

So it's a test artifact, not a real gap. Let me fix both and re-run.

Also let me do a real-repo mutation (on actual files, then restore) for at least one check as F003 did.

Let me strengthen D010's check and re-run mutation verification including the lifecycle with proper status.
Mutation verification caught a weak needle (D010) — strengthening it, and re-testing the lifecycle `[TEST]` gate with the correct status.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 1 files updated, 12 nodes, 161 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:48:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python - <<'PY'\nimport pathlib, shutil, sys, tempfile\nsys.path.insert(0, \".\")\nfrom tools import check_doc_consistency as cdc\nfrom tools import validate_spec_lifecycle as vsl\n\nroot = pathlib.Path(\".\").resolve()\nALL = {cdc.SPEC, cdc.DESIGN, cdc.TASKS, cdc.F007_SPEC, cdc.F007_DESIGN, cdc.F007_TASKS}\n\ndef mutate(rel, old, new, fn, label):\n    with tempfile.TemporaryDirectory() as td:\n        tmp = pathlib.Path(td)\n        fo
…[truncated])`

  <details><summary>tool output</summary>

  ```text
D010 remove DR-005 entity: RED (ok) -> ['holdout_budget_ledger_exists']
D010 rename DR-005 id only: RED (ok) -> ['holdout_budget_ledger_exists']
lifecycle ready-for-dev with [TEST]: green
lifecycle ready-for-dev without [TEST]: ['F007-evaluation-gates: tasks.md 缺少必需的 [TEST] 组（层 2 旅程验收轨）']


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:48:12Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。\n- `T016/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029`：旅程验收以各验收套件、变异/并发/属性证据与执行机真实证据为前提（编写早、执行晚）。", "oldString": "- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。"})`


> [reasoning] All mutation verifications now red as required, and the lifecycle gate correctly: green with [TEST], red without, at ready-for-development status.

Now the real-repo mutation demonstration (F003 did one). Let me do 2 on actual files then restore:
1. Append a merged CLI flag into F007 design → `check_doc_consistency.py` must fail.
2. Delete `### [TEST]` heading from F007 tasks → fail (both doc-consistency and, at ready-for-development, lifecycle). Let's do #1 and one that exercises the task DAG: temporarily flip F007 spec status to ready-for-development AND remove an edge → check_task_dag red. Hmm, that requires restoring precisely. Let me do it with git-tracked files so restore is via `git checkout --`.

Let me do it carefully:
- `printf X >> design` → run → red → `git checkout -- design`
- flip status in spec via sed → run check_task_dag (should pass) → remove `T012/T013 -> T024` edge → check_task_dag red → `git checkout -- spec tasks`.

But note the doc-consistency check requires the frontmatter literal `related_features: [F002, F003, F004, F008]` in spec — flipping status doesn't affect it. And `check_doc_consistency` requires (F007_SPEC, ...) needles — status flip doesn't break them. Fine.

Let me run.

Also I should add the [TEST] predecessor edges commit. Let me do that first (small commit), then mutation.

Actually, careful about "one finding one commit": adding `T0xx -> T027/T028/T029` — I'll add as an accompanying commit tied to D001/D008 (documented in FIX-log as 附带提交). Let me do it.

Hmm, is it needed? Let me reconsider. The DAG gate currently passes. The [TEST] tasks have no predecessors which means "journey acceptance" doesn't depend on the suites — a reviewer in Round 2 might flag it as a new finding (fix-regression/gap). Better to pre-empt: add the edge line. It's cheap and improves correctness. Let me add.

Edge line:
`` - `T016/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029`：旅程验收以各验收套件、变异/并发/属性证据与执行机真实证据为前提（编写早、执行晚）。 ``

Check: all sources < 27 ✓. Targets 27-29 ✓.

Then commit as "附带：补 [TEST] 组前置边" — I'll fold it into the D001 finding's scope honestly in FIX-log (附注).

Let me do it.
Adding the missing `[TEST]` 前置边 (keeps the journey track from floating), then real-repo mutation evidence.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:49:56Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -c \"\nimport sys,pathlib; sys.path.insert(0,'.')\nfrom tools import check_task_dag as dag\nt=pathlib.Path('docs/features/0.2/F007-evaluation-gates/tasks.md').read_text(encoding='utf-8')\nprint('DAG errors:', dag.check_tasks(t) or 'none')\nprint('edge count:', len(dag.parse_edges(t)))\n\" && .venv/bin/python tools/check_doc_consistency.py && git add -A docs/features/0.2/F007-evaluation-gates/tasks.md && git commit -q -m \"fix(f00
…[truncated])`

  <details><summary>tool output</summary>

  ```text
DAG errors: none
edge count: 43
check_doc_consistency: 全部通过
d2a55e6 fix(f007): D001 附带 补 [TEST] 组前置边（旅程验收不悬空）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:50:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && D=docs/features/0.2/F007-evaluation-gates && echo \"--- 变异1：真实仓库写回合并 flag ---\" && printf '\\n--universe-calendar <path>\\n' >> $D/design.md && .venv/bin/python tools/check_doc_consistency.py; echo \"exit=$?\" && git checkout -- $D/design.md && echo \"--- 变异2：真实仓库 DAG（先翻 ready-for-development）---\" && sed -i 's/^status: draft$/status: ready-for-development/' $D/spec.md && .venv/bin/python tools/check_task_dag.py; echo \"ok-exit=$?\" && sed -i 's|
…[truncated])`

  <details><summary>tool output</summary>

  ```text
--- 变异1：真实仓库写回合并 flag ---
check_doc_consistency: 失败
  - [universe_calendar_artifacts_split] 出现已废弃文本 '--universe-calendar'（docs/features/0.2/F007-evaluation-gates/design.md）
exit=1
--- 变异2：真实仓库 DAG（先翻 ready-for-development）---
check_task_dag: 全部通过
ok-exit=0
check_task_dag: 全部通过
mutated-exit=0
--- 已复原 ---
 M tools/check_doc_consistency.py


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:50:14Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A tools/check_doc_consistency.py && git commit -q -m \"test(f007): D010 断言针脚收紧到实体定义行（变异验证发现弱针脚）\" && D=docs/features/0.2/F007-evaluation-gates && printf '\\n' >> $D/design.md && printf 'x\\n' > /dev/null && sed -i 's|`T009 -> T012`|`T009`|' $D/tasks.md && .venv/bin/python tools/check_doc_consistency.py; echo \"doc-consistency-exit=$?\" && git checkout -- $D/tasks.md $D/design.md && echo \"--- ready-for-development 口径全门预演 ---\" && sed -i 
…[truncated])`


> [reasoning] 变异2 didn't go red: my sed for `T009 -> T012` — the actual text is "`T009 -> T012`：cohort 级校正…" and my sed replaced "`T009 -> T012`" with "`T009`". That removes the edge, but the DAG gate only errors if (a) endpoints undefined, (b) backward, (c) [P] with predecessor, (d) max task without incoming edge. Removing the T009->T012 edge doesn't trigger any of those — T012 still has incoming from T009->? no... T012 has incoming edges? Let me see: edges include T009->T012 (removed), T012->T013, T012->T016, T012->T024. So after removal, T012 has no incoming edge — but the gate only requires the MAX id (T030) to have incoming. So the mutation is not detected by the generic gate.

That's an important observation: the generic DAG gate doesn't check "every task has a predecessor", only the last one. My TEXT_CHECKS entry `task_graph_missing_edges_f007` requires the literal edge text, so a doc-level mutation (removing that edge) IS caught by check_doc_consistency. That's the finding-specific gate. So the real evidence: removing the edge makes check_doc_consistency red. Let me verify that.

Also note the second sed didn't apply to the T024 line (my sed pattern with escaped backticks failed) — irrelevant.

Also, importantly: git status shows ` M tools/check_doc_consistency.py` — that's the uncommitted D010 needle strengthening! I need to commit it.

Let me: (1) commit the strengthened D010 check, (2) run the real-repo doc-consistency mutation for the DAG-edge removal to show red.

Let me also double check nothing else got left modified. git status shows only tools file modified; design/tasks/spec restored ✓.

Wait — the mutation 2 flipped spec status to ready-for-development and then `git checkout --` restored it. Good. And `check_task_dag` passed in "ok-exit=0" (with ready-for-development Status!) — meaning F007's DAG would pass the gate at ready-for-development. 

But hold on: with status=ready-for-development, `check_task_dag` passed, but would `validate_spec_lifecycle` also pass at ready-for-development? It requires Q/DQ closed (spec §8 = 无 ✓, design §10 = 无 ✓), AC refs valid ✓, tests paths only enforced at review/done ✓, and [TEST] group ✓. Let me verify that too — it's a meaningful "would-be-ready" check. Let me do it in a temp copy of the whole repo? Simpler: temporarily flip status in the real repo, run both validate_spec_lifecycle and check_task_dag, restore. That gives strong evidence. Let me do that now (carefully restoring).

Then run the full verify.py, then write FIX-log.

Let me proceed.

  <details><summary>tool output</summary>

  ```text
check_doc_consistency: 失败
  - [task_graph_missing_edges_f007] 缺少要求文本 '`T009 -> T012`'（docs/features/0.2/F007-evaluation-gates/tasks.md）
doc-consistency-exit=1
--- ready-for-development 口径全门预演 ---
validate_spec_lifecycle: 失败
  - BACKLOG F007-evaluation-gates status=draft 与 spec (ready-for-development) 不一致
lifecycle=1
check_task_dag: 全部通过
dag=0
check_doc_consistency: 全部通过
consistency=0
6d5ad65 test(f007): D010 断言针脚收紧到实体定义行（变异验证发现弱针脚）
d2a55e6 fix(f007): D001 附带 补 [TEST] 组前置边（旅程验收不悬空）
b345e25 fix(f007): D025 属性测试执行轨与 seed/生成器可复现约束


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:50:31Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && D=docs/features/0.2/F007-evaluation-gates && cp BACKLOG.md /tmp/opencode/BACKLOG.bak && sed -i 's/^status: draft$/status: ready-for-development/' $D/spec.md && sed -i 's/\\(| F007-evaluation-gates | [^|]*| \\)draft\\( |\\)/\\1ready-for-development\\2/' BACKLOG.md && grep -n \"F007\" BACKLOG.md && .venv/bin/python tools/validate_spec_lifecycle.py; echo \"lifecycle=$?\" && git checkout -- $D/spec.md BACKLOG.md && git status --porcelain && echo rest
…[truncated])`


> [reasoning] Good. The `validate_spec_lifecycle` "failure" at ready-for-development is only the BACKLOG status mismatch (expected, since I only flipped the spec, not BACKLOG). That confirms the [TEST]/Q/AC parts pass. To get a clean pre-flight, I'd need to flip BACKLOG too and run in a temp copy. Let me do the full pre-flight in a temp copy of the repo docs tree... Actually simpler: temporarily flip both spec and BACKLOG status, run lifecycle, then restore. Let me do it — it's the strongest evidence that F007 is dev-ready after my fixes.

Also note: F008/F003 remain draft, so BACKLOG row status for F007 must match. Let me do it.

Then run the round-end full `tools/verify.py` once.

Then write FIX-log.md.

Also, `git status --porcelain` output was empty? It printed nothing between "consistency=0" and the log lines — yes, clean. Good.

Let me do the ready-for-development full pre-flight + full verify.

  <details><summary>tool output</summary>

  ```text
9:| F007-evaluation-gates | 0.2 | ready-for-development | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
22:递增，与执行顺序无关**（如 F007 评测台先于编号更小的 F005 研究控制台执行）。
validate_spec_lifecycle: 全部通过
lifecycle=0
restored


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:50:43Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && time .venv/bin/python tools/verify.py; echo \"verify-exit=$?\"", "timeout": 900000})`


> [reasoning] F007 at ready-for-development would pass the full lifecycle gate (structure, Q/DQ closed, AC refs, [TEST] group, BACKLOG consistency). That's strong evidence for D001 and structure.

Now: full round-end gate `tools/verify.py`. It takes ~6 minutes (mostly check_secrets rglob). Let me run it with a generous timeout (say 900s = 900000ms). Note the F003 log said 6m21s.

Let me run it.

While it runs I can't do much else (bash is sequential). Let's run.
Round-end full gate (`.venv/bin/python tools/verify.py`), same entry as CI.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_task_dag: 全部通过
check_doc_consistency: 全部通过
check_dep_pins: 全部依赖版本在声明范围内（runtime + dev）
check_secrets: 无密钥形态命中
........................................................................ [ 21%]
........................................................................ [ 43%]
........................................................................ [ 65%]
........................................................................ [ 87%]
....................s...............sssss                                [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/integration/test_f001_kronos_smoke.py:86: AC-006 需真实模型实例：设 KRONOS_REQUIRE_REAL_MODEL=1 并把 KRONOS_BASE_URL 指向真实实例（命令见本文件 docstrin
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:58:00Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline d659db7..HEAD | cat && echo \"---count---\" && git rev-list --count d659db7..HEAD && echo \"---worktree---\" && git status --porcelain && echo \"(clean if empty)\""})`


> [reasoning] Full gate green: 323 passed, 6 skipped (all capability-gated integration tests, pre-existing), ruff clean.

Note test count went from 294 (F003 round) to 323 = +29 tests (my new TEXT_CHECKS mutations + custom check test). Let me compute: new TEXT_CHECKS added: 25 entries, of which those with forbids also generate a second test. Let me count: I added checks: f007_test_group_present(forbids), f007_ingests_f003_contracts(forbids), f007_declares_f008_universe(no forbids), universe_calendar_artifacts_split(forbids), no_lookahead_three_layers_owned(no forbids), sample_size_three_tiers(no), task_graph_missing_edges_f007(no), full_chain_controls_have_predecessors(no), real_env_task_has_distinct_evidence(no), holdout_budget_ledger_exists(no), verdict_vocabulary_frozen(no), sc002_concurrency_has_task(no), ac003_multi_member_batch(no), nfr004_approximation_covered(no), mutation_targets_labels_aligned(no), second_implementation_has_task(no), f004_to_f007_factor_source_contract(no), f005_frontend_does_not_bypass_api(no), final_confirmation_window_hidden(no), stage_ids_and_failure_dimensions_frozen(no), nfr005_ux001_traceable(no), design_no_task_directives(forbids), state_vocab_and_bench_mapping_aligned(no), property_strategy_has_execution_task(no) = 24 checks + 1 custom = 25 checks; tests = 24 (required-removed) + 3 (deprecated-reintroduced for the 3 with forbids) + 1 custom test = 28. Plus 294 → 322... close enough; 323 observed.

Now: update todos to completed, then append FIX-log.md declaration.

Also I should double check the FIX-log docs: append `## F007 Round 1 修复声明 · 2026-09-17 · report_type: doc-review`? Hmm — per the template, "Round <N>" refers to the fix round. The review is F007 Round 1; the fix declaration corresponds to the fix for Round 1, and the reviewer's next step is Round 2 (diff-only). F003's FIX-log labeled "Round 1" for its round-1 fixes. To avoid ambiguity with F003's entry in the same file, I'll title: `## F007 · Round 1 修复声明 · 2026-09-17 · report_type: doc-review`.

Content per template:
```
## Round <N> · <YYYY-MM-DD>
- findings: <本轮处理的 issue id 列表>
- commits: <每条 finding 对应的 commit 短哈希>
- regression_tests: <file::test_name>
- gate: <轮末全量门禁命令 + 输出结论 + 时间戳>
- rejected: ...
```
Plus baseline declaration, evidence table (one row per finding with commit + check_id + mutation test), mutation verification evidence, gate output, and what the fixer did NOT do.

Let me gather commit hashes. Let me get the log of my commits with their mapping.

Let me run git log to get hashes for all 27 commits.
All gates green. Collecting commit hashes for the FIX-log declaration.

  <details><summary>tool output</summary>

  ```text
6d5ad65 test(f007): D010 断言针脚收紧到实体定义行（变异验证发现弱针脚）
d2a55e6 fix(f007): D001 附带 补 [TEST] 组前置边（旅程验收不悬空）
b345e25 fix(f007): D025 属性测试执行轨与 seed/生成器可复现约束
aa348bb fix(f007): D024 对齐状态词汇、canonical=bench 与 evaluation.registered
e29563e fix(f007): D023 design 行动指令移入 tasks，只保留前置约束声明
24a7631 test(f007): 修正 F003 上游变异测试针脚以对齐 D003 后的 frontmatter
80cbd3d fix(f007): D022 NFR-005/UX-001 落 AC-011 与 tasks verify
5b26dac fix(f007): D021 冻结五阶段 ID 与 failure_taxonomy 三维 schema
d9e0dd3 fix(f007): D020 design §8 补齐测试映射并加 tasks⊆design 一致性门
c408ffc fix(f007): D019 最终确认窗统计排除于 Agent/preview 产物并 fail-closed
6b7ef77 fix(f007): D018 明确 F005 只经统一只读 API，文件 reader 仅内部 adapter
873a884 fix(f007): D017 定义信号来源适配契约与 placeholder 分层规则
10e91f1 fix(f007): D016 第二实现抽查落 T025（time-box/容差/证据路径）
278ebe2 fix(f007): D015 变异 AC 标签对齐并加工具 pin 与 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:58:11Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && date \"+%Y-%m-%d %H:%M %Z\" && git rev-parse --short HEAD && git rev-list --count origin/main..HEAD && .venv/bin/python -c \"\nimport pathlib,sys; sys.path.insert(0,'.')\nfrom tools import check_doc_consistency as c\nprint('text_checks:', len(c.TEXT_CHECKS), 'f007:', len([x for x in c.TEXT_CHECKS if x.finding.startswith('F007')]))\nprint('custom:', [f.__name__ for f in c.CUSTOM_CHECKS])\""})`


> [reasoning] 28 commits. Now write the FIX-log declaration. Per skill, append-only to docs/reviews/FIX-log.md.

Let me compose the entry with:
- baseline
- findings: D001..D025 all fixed
- commit table (one per finding)
- regression_tests table (check_id + mutation test names)
- mutation verification evidence
- gate output
- rejected: none (with reasoning)
- fixer did NOT do list
- 附带提交 + 修复自伤记录 (the 2 test fixes: 24a7631, 6d5ad65)

Let me write it via the write tool... but the file exists; I must Read first (I did read it at the start). I'll use `edit` to append, or write with full content. Appending via edit on the last line is safer. The file's last line is:

"- **未推送 / 未取 CI**：CI 是收敛候选轮由检视人触发的最终门禁（§7/§8）；本地 `main` 领先\n  `origin/main` 23 个提交，等检视方核对后推送。"

I'll append after that. Let me construct the text.

Note head is now d659db7 + 28 commits. Let me capture the new HEAD short hash: 6d5ad65. Also origin/main ahead count: 23 + 28 = 51.

Let me write the entry. Date: 2026-09-17 (today per env).

Gate command output: I have the verify.py summary. Timestamp: I don't have exact wall clock; the run took 7m07s and I ran it just now. Let me get the timestamp via `date`.

Let me get date and ahead-count, then write.

  <details><summary>tool output</summary>

  ```text
2026-09-17 00:58 HKT
6d5ad65
51
text_checks: 41 f007: 24
custom: ['check_f007_declares_f003', 'check_ac_body_covers_clauses', 'check_active_feature_indexes', 'check_f007_design_test_map_covers_tasks']


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:58:18Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "newString": "- **未推送 / 未取 CI**：CI 是收敛候选轮由检视人触发的最终门禁（§7/§8）；本地 `main` 领先\n  `origin/main` 23 个提交，等检视方核对后推送。\n\n---\n\n## F007 · Round 1 修复声明 · 2026-09-17 · report_type: doc-review\n\n### 基线与范围\n\n- 基线：`main@d659db7`（工作树干净），与 `CURRENT-doc-F007.md` 声明的最终基线一致；修复期间无 HEAD 漂移。\n- 被检对象：`docs/features/0.2/F007-evaluation-gates/{spec,design,tasks}.md` 及其相邻契约\n  （F003 spec、F004 spec、F008 spec/design/tasks、ADR-0003/0005/0007、PRD FR3.5/F
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:58:43Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git check-ignore -v docs/reviews/FIX-log.md docs/reviews/CURRENT-doc-F007.md && echo \"--- tracked review files (should be only RETROSPECTIVE) ---\" && git ls-files docs/reviews/ && echo \"--- any review file in my commits? ---\" && git log --name-only d659db7..HEAD --pretty=format: | sort -u | grep -c \"docs/reviews\" ; echo \"--- worktree ---\" && git status --porcelain && echo \"(clean if empty)\""})`


> [reasoning] FIX-log is gitignored (docs/reviews/*), so no commit needed — and per the skill, review files never enter git.

Let me verify: `git check-ignore -v docs/reviews/FIX-log.md` should confirm. Also confirm worktree is clean (untracked ignored files don't show).

Also let me double-check the D020 mapping check counts and do a final full-doc sanity check: run the doc gates once more + confirm CURRENT-doc-F007.md unchanged (git diff won't show since ignored; let me check mtime/hash? I never edited it — verified by my tool calls).

Let me run final verification.

One more consideration: the skill requires per-round regression test = "新增的门禁失败测试" documented. Done.

Also I should double check that `docs/reviews/FIX-log.md` and `CURRENT-doc-F007.md` are gitignored so no accidental commit happened. My commits used `git add -A <specific paths>` mostly, and one `git add -A docs/features/0.2/F007-evaluation-gates ...`. Did any commit use `git add -A` broadly? Let me check: I used `git add -A docs/features/0.2/F007-evaluation-gates tools/... tests/...` — path-limited. Good. But let me confirm no review files ended up in git history: `git log --name-only -1` or check if FIX-log is tracked.

Let me run final checks.

  <details><summary>tool output</summary>

  ```text
.gitignore:39:docs/reviews/*	docs/reviews/FIX-log.md
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc-F007.md
--- tracked review files (should be only RETROSPECTIVE) ---
docs/reviews/RETROSPECTIVE.md
--- any review file in my commits? ---
0
--- worktree ---
(clean if empty)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:58:53Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git diff --stat d659db7..HEAD | tail -8 && echo \"--- F007 AC 清单 ---\" && grep -c \"^- \\[ \\] \\*\\*AC-\" docs/features/0.2/F007-evaluation-gates/spec.md && grep -n \"AC-01[0-2]\" docs/features/0.2/F007-evaluation-gates/spec.md | head -5 && echo \"--- tasks ---\" && grep -c \"^- \\[ \\] T0\" docs/features/0.2/F007-evaluation-gates/tasks.md"})`


> [reasoning] Everything is clean:
- Review files gitignored, only RETROSPECTIVE.md tracked, 0 review files in my commits.
- Worktree clean.

Wait — the worktree shows clean, but I edited FIX-log.md (ignored) — so it's clean. Good.

Hmm, one issue: the FIX-log edit is an ignored local file — fine.

Let me do one final consolidated verification of the three docs (structure + counts) and then update todos and report.

Let me also double check: did I miss any of the 25 findings' requirement that the reviewer's `suggested_fix` mentioned? Let me spot-check a few:
- D001 ✓, D002 ✓ (design frontmatter + sections + tasks), D003 ✓, D004 ✓, D005 ✓, D006 ✓, D007 ✓, D008 ✓, D009 ✓, D010 ✓, D011 ✓, D012 ✓ (design §8 mapping SC-002 + T024), D013 ✓, D014 ✓, D015 ✓, D016 ✓, D017 ✓, D018 ✓, D019 ✓, D020 ✓, D021 ✓, D022 ✓, D023 ✓, D024 ✓, D025 ✓.

Final state check: AC count in F007 spec = AC-001..AC-012 (12). Let me confirm AC-010/011/012 exist and are referenced properly. validate_spec_lifecycle passed, which checks AC uniqueness + requirement refs exist. Note AC-011 refs NFR-004/NFR-005/UX-001 — all exist ✓ (NFR-005 exists, UX-001 exists). AC-012 refs FR-003 ✓. AC-009 refs FR-007 ✓ (FR-007 defined). Good — and the gate passed so they're valid.

Let me print a final summary of the doc deltas (line counts) for the report.

Then mark todos complete.

Let me update the todo list to all completed and give the final report.

Actually the todos tool requires the full list. Let me just mark all completed in one call.

Let me also produce a compact diffstat.

  <details><summary>tool output</summary>

  ```text
docs/features/0.2/F007-evaluation-gates/design.md | 127 ++++++++--
 docs/features/0.2/F007-evaluation-gates/spec.md   |  77 ++++--
 docs/features/0.2/F007-evaluation-gates/tasks.md  |  55 +++--
 tests/unit/test_check_doc_consistency.py          |  23 +-
 tools/check_doc_consistency.py                    | 275 ++++++++++++++++++++++
 5 files changed, 491 insertions(+), 66 deletions(-)
--- F007 AC 清单 ---
12
296:- [ ] **AC-011** (`NFR-004`, `NFR-005`, `UX-001`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本；产物路径与 manifest 只用 POSIX 逻辑路径/URI（Windows/WSL 物理路径只进 provenance）；CLI 首屏含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定）
297:- [ ] **AC-012** (`FR-003`): 五阶段 ID 与失败三维 schema 冻结并可校验——stage 取值限于 `signal_quality`/`portfolio_transform`/`
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:59:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"^- \\[ \\] \\*\\*AC-\" docs/features/0.2/F007-evaluation-gates/spec.md"})`


> [reasoning] Interesting: AC-010 appears at line 298 AFTER AC-011/AC-012? That's because my AC-010 insertion used oldString "\n## 7. 测试、依赖与决策" and I inserted AC-010 before it — but AC-011/AC-012 were added before AC-008's neighborhood? Let me look at the order. AC order in file matters for readability, not for the gate (it checks uniqueness + refs). Let me check the ordering and fix it for cleanliness.

Lines: AC-011 at 296, AC-012 at 297, AC-010 at 298. So the order is ..., AC-009, AC-011, AC-012, AC-010? That's messy. Let me look at the AC block.

  <details><summary>tool output</summary>

  ```text
287:- [ ] **AC-001** (`FR-001`, `DR-004`, `DR-005`, `NFR-003`): preview 越权被拒绝，正式台账与留出预算台账零变化（含「台账零行」正向断言与 preview 越权写入留出预算的负例）
288:- [ ] **AC-002** (`FR-002`): label endpoint、per-pair 日历、最大 horizon、train-only fit 与 future-aware 算子负例全部被拦截
289:- [ ] **AC-003** (`FR-003`, `FR-004`): 必需统计失败关闭；拒绝者仍进入试验分母，成员未收齐时 cohort 不能 finalize 或晋级；**多成员 cohort 批量夹具**上被拒成员仍在分母、诊断性重算不重复计数
290:- [ ] **AC-004** (`FR-005`): 三档成本、breakeven/换手/持有期和 rolling stability 完整，成本不存活者为 dead；样本量三级裁决正确（`<30` → `underpowered` 不判 PASS/FAIL、`30~69` → `provisional` 仅缩减仓位 paper、`≈≥69` → `trustworthy` 才可完整判定）
291:- [ ] **AC-005** (`FR-006`, `DR-003`, `NFR-001`): report/curves/manifest 原子发布，失败注入不产生半个 PASS
292:- [ ] **AC-006** (`DR-001`, `DR-002`, `DR-006`, `NFR-002`): ResearchSnapshot 跨路径/codec 身份稳定；动态 latest 先冻结；成员/cutoff/映射日历或实验语义
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:59:12Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取或写入 fail-closed 并留拒绝事件\n- [ ] **AC-011** (`NFR-004`, `NFR-005`, `UX-001`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本；产物路径与 manifest 只用 POSIX 逻辑路径/URI（Windows/WSL 物理路径只进 provenance）；CLI 首屏含 tier/cohort/data+code digest/state/verdict 与首个失败
…[truncated])`


> [reasoning] AC-010 is out of numeric order (after AC-012). Let me fix the ordering: move AC-010 before AC-011. This is a cosmetic/documentation-quality fix. Do it as a small commit (labelled as ordering fix, accompanying).

Order should be AC-001..AC-012 sequential.

Edit: remove line 298 and insert before AC-011.

I'll do two edits: delete the AC-010 line at the end, and insert AC-010 before AC-011. Actually simpler: replace the block "AC-011 line\nAC-012 line\nAC-010 line" with "AC-010 line\nAC-011 line\nAC-012 line"? The lines are long; use unique anchors.

Edit 1: replace
"- [ ] **AC-011** (`NFR-004`, `NFR-005`, `UX-001`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本；产物路径与 manifest 只用 POSIX 逻辑路径/URI（Windows/WSL 物理路径只进 provenance）；CLI 首屏含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定）"
with AC-010 text + "\n" + AC-011 text? That inserts AC-010 before AC-011.

Edit 2: delete the trailing AC-010 line (the one after AC-012).

Let me construct with exact strings. I need the AC-010 exact text: "- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取或写入 fail-closed 并留拒绝事件"

Edit 2 oldString: "AC-012 line\n- [ ] **AC-010** ...拒绝事件\n" → replace with "AC-012 line\n". Let me do it.

Careful: AC-012 line is long; I'll use the ending portion as anchor: "synthesis 按三维聚合且拒绝枚举外取值\n- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取或写入 fail-closed 并留拒绝事件" → newString "synthesis 按三维聚合且拒绝枚举外取值".

And Edit 1 inserts AC-010 before AC-011.

Let me do it.
AC 编号顺序被我的插入弄乱了（AC-010 落在 AC-012 之后）——顺手校正。

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:59:31Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "newString": "synthesis 按三维聚合且拒绝枚举外取值", "oldString": "synthesis 按三维聚合且拒绝枚举外取值\n- [ ] **AC-010** (`NFR-003`, `IR-003`): 最终确认窗统计量不出现在任何 Agent/preview 可读的 report/manifest/synthesis；越权读取或写入 fail-closed 并留拒绝事件"})`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:59:42Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"^- \\[ \\] \\*\\*AC-\" docs/features/0.2/F007-evaluation-gates/spec.md | sed 's/\\(AC-0[0-9]*\\).*/\\1/' && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py tests/unit/test_validate_spec_lifecycle.py 2>&1 | tail -3"})`

  <details><summary>tool output</summary>

  ```text
287:- [ ] **AC-001
288:- [ ] **AC-002
289:- [ ] **AC-003
290:- [ ] **AC-004
291:- [ ] **AC-005
292:- [ ] **AC-006
293:- [ ] **AC-007
294:- [ ] **AC-008
295:- [ ] **AC-009
296:- [ ] **AC-010
297:- [ ] **AC-011
298:- [ ] **AC-012
validate_spec_lifecycle: 全部通过
check_doc_consistency: 全部通过
........................................................................ [100%]
72 passed in 2.32s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:59:55Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A docs/features/0.2/F007-evaluation-gates/spec.md && git commit -q -m \"docs(f007): AC-010 归位到 AC-009 之后，恢复编号顺序\" && git log --oneline -1 && git status --porcelain && echo \"(clean)\""})`

  <details><summary>tool output</summary>

  ```text
225376d docs(f007): AC-010 归位到 AC-009 之后，恢复编号顺序
(clean)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:00:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && date \"+%Y-%m-%d %H:%M %Z\" && git rev-parse --short HEAD && .venv/bin/python tools/verify.py 2>&1 | tail -6; echo \"verify-exit=$?\"", "timeout": 900000})`


> [reasoning] Now HEAD is 225376d. I need to update the FIX-log's baseline/HEAD references (6d5ad65 → 225376d, commit count 51 → 52, gate timestamp). Also record the AC reorder commit as an accompanying commit, and note that the full gate was run at 6d5ad65 but this last commit only touched spec AC ordering (validated with the doc gates + lifecycle tests). Per the skill, gate runs once per round at round end — the AC reorder came after. I should re-run the affected gates (already done: lifecycle, doc consistency, 62 tests pass). But the full verify.py was run before this cosmetic change. To be honest, I'll state: full verify at 6d5ad65; after the AC reorder (225376d) re-ran the three doc gates + 72 unit tests (lifecycle/consistency) — all green; the change is spec-only text.

Hmm, better: re-run the full verify.py once more so the round-end gate matches final HEAD exactly. It costs ~7 min. The skill says the round gate should be at the round end. Being rigorous matters here (the reviewer will independently verify). Let me re-run it. Actually, the pytest suite includes test_repo_passes_all_checks which reads the repo — already validated. But "gate at final HEAD" is cleaner evidence. Let me run it — 7 minutes is acceptable.

Let me run verify.py again, then update FIX-log accordingly.
Re-running the full gate at the final HEAD so the round-end evidence matches exactly.

  <details><summary>tool output</summary>

  ```text
2026-09-17 01:00 HKT
225376d

== ruff check ==

== ruff format check ==

verify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff
verify-exit=0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:07:04Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && { time .venv/bin/python tools/verify.py ; } > /tmp/opencode/f007_verify_final.log 2>&1; echo \"exit=$?\" && grep -E \"passed|skipped in|全部通过|全部可解析|All checks|already formatted\" /tmp/opencode/f007_verify_final.log && tail -3 /tmp/opencode/f007_verify_final.log && date \"+%Y-%m-%d %H:%M %Z\"", "timeout": 900000})`


> [reasoning] Hmm, the tail cut off the pytest summary. Wait — it ran very fast? 01:00 start; the previous run took 7 minutes. Let me check: I didn't see the pytest line. The output shows only the trailing sections. It printed "verify.py 全部通过" — so it completed (exit 0). Maybe caching made it faster? check_secrets takes 2min+... Suspicious. Let me re-run capturing more output and time. Actually the command returned quickly (my perception). Let me verify with a full output capture including time.

Wait, the `date` said 01:00 and previous run ended 00:58 — if this run took 7 min it'd be ~01:07. The response came back, so it either ran fast or... Hmm, the tool output doesn't include timing. Let me just re-run with `time` and grep for pytest summary to have accurate evidence. To avoid another 7 minutes, maybe I should trust exit 0 + the printed summary line. But I need the pytest count for the FIX-log evidence. Let me re-run with time and tee to a file, then grep.

Actually — maybe verify.py skips the slow secrets scan if unchanged? Unlikely. Let me just re-run with time; correctness of evidence matters more than 7 minutes.

  <details><summary>tool output</summary>

  ```text
exit=0
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_task_dag: 全部通过
check_doc_consistency: 全部通过
326 passed, 6 skipped in 276.57s (0:04:36)
All checks passed!
110 files already formatted
verify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff

verify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff
.venv/bin/python tools/verify.py  317.12s user 45.15s system 81% cpu 7:25.91 total
2026-09-17 01:14 HKT


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:14:40Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -m pytest -q --collect-only 2>/dev/null | tail -2 && grep -rn \"parametrize\" tests/unit/test_validate_spec_lifecycle.py | head -5 && grep -c \"\" /dev/null; grep -rln \"discover_features\\|glob(\" tests/unit/*.py | head"})`


> [reasoning] Final gate at 225376d: 326 passed, 6 skipped, 7m25.9s, 2026-09-17 01:14 HKT, exit 0.

Now update FIX-log to reflect: HEAD 225376d, 52 commits ahead, final gate numbers (326 passed, 6 skipped, 276.57s, exit 0, 01:14 HKT), the extra accompanying commit (AC reorder), and the note that both gate runs were green.

Let me edit the FIX-log sections:
1. "修复后 HEAD：`6d5ad65`（本地 `main` 领先 `origin/main` 51 个提交，未推送）" → `225376d` / 52.
2. 附带提交 list: add `225376d`.
3. gate block: update to final run.
4. The earlier verify (323 passed at 6d5ad65) — keep both? I'll present the final run as the round gate and mention the earlier intermediate run in one line. Let me restructure the gate section: show the final run (326 passed, 276.57s, 01:14) and note the intermediate run at 6d5ad65 (323 passed) plus why counts differ (spec-only AC reorder shouldn't change test count... hmm, 323 → 326? The AC reorder shouldn't add tests. Why 326 vs 323?

Hmm! 323 passed at 6d5ad65, and 326 passed at 225376d. I only changed spec.md AC ordering in between (one commit). That shouldn't add 3 tests. Unless... the earlier run was 323 and it included my new tests. Wait, both runs were after all my changes. Let me check: maybe the pytest count varies because of randomized/parametrized... no.

Hmm, actually: the first verify run (323) happened BEFORE I added... no, all commits were done. Wait, let me re-check the sequence: verify run #1 (323 passed) was after commit 6d5ad65 which was the last code/doc commit; then I only made the AC reorder commit (225376d).

Why +3 tests? Possibly `tests/unit/test_check_doc_consistency.py` parametrization depends on TEXT_CHECKS count — unchanged. Hmm. Or maybe pytest collected tests that depend on file content? E.g. test_doc_gate_command? Or the doc-consistency test file's `_materialize`... no.

OH. I bet it's `tests/unit/test_review_artifacts_gitignore.py` or similar scanning... Hmm.

Alternatively, could it be that the second run collected 3 tests that were skipped/not collected before due to file changes mid-run? Unlikely.

Wait — maybe I'm misreading: run #1 said "323 passed, 6 skipped in 247.72s". Run #2 says "326 passed, 6 skipped in 276.57s". A 3-test difference. Let me investigate: is there a test that parametrizes over doc files (e.g., per-feature tests)? Let me grep for parametrize over features/docs in tests.

Actually: `tests/unit/test_validate_spec_lifecycle.py` might parametrize per feature directory. If a per-feature parametrization exists... no new features were added.

Hmm, but `test_check_doc_consistency.py` — my `test_f007_design_test_map_goes_red_on_unmapped_test` is 1 test. The parametrized ones depend on TEXT_CHECKS (41 entries, 3 with forbids → 44 mutation tests). Unchanged.

Another thought: `tests/unit/test_doc_gate_command.py` or `test_review_artifacts_gitignore.py` may parametrize over files matched by glob — e.g., review artifacts. Since docs/reviews/FIX-log.md was appended... but tests can't see gitignored files? They can, on disk. Hmm, if a test parametrizes over `docs/reviews/*` files, adding content to FIX-log wouldn't change count but adding... no new files.

Wait — maybe the difference is that between the two runs, I created `/tmp/opencode/f007_verify_final.log`? No.

Let me just check by running pytest --collect-only -q and counting. Let me do that to be sure nothing weird (and to report accurately).

Actually, I realize: run #1 was `time .venv/bin/python tools/verify.py` — and the pytest count 323. Run #2: 326. Between them, the only repo change is spec.md AC reorder (a text move). Hmm, unless the spec AC reorder made `validate_spec_lifecycle`... no, that's not pytest.

Could pytest count depend on environment (e.g., ALPHAMILL_* env vars set in one shell)? The shell is persistent; no env changes.

Let me investigate via collect-only count. It's cheap.

  <details><summary>tool output</summary>

  ```text
338 tests collected in 1.86s
0
tests/unit/test_f001_line_limit_exemptions.py
tests/unit/test_f002_manifest.py


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:14:56Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"pytest\" tools/verify.py | head -20"})`


> [reasoning] 338 collected, 326 passed + 6 skipped = 332... doesn't match 338 either. Hmm, 338 collected includes 6 skipped + 326 passed = 332. 6 tests unaccounted. So collection is env-dependent (deselect/skip conditions) or some tests are collected at runtime differently. Whatever — pytest count differences likely come from environment-dependent collection (e.g. tests that conditionally skip at collection via `pytest.importorskip` or `collect_ignore`). 

Wait: `tests/unit/test_f001_line_limit_exemptions.py` — it globs files! If it parametrizes over repo files, then adding/removing tracked files changes the count. Did I add any new files? No new files were added by me (only edits). Hmm. But between run #1 and #2 I only edited spec.md... 

Actually — hold on. Between run 1 and run 2, did anything else change on disk? I created `/tmp/opencode/BACKLOG.bak` (outside repo). And I appended to docs/reviews/FIX-log.md (ignored). If a test globs `docs/reviews/*` or the repo tree for line limits... `test_f001_line_limit_exemptions.py` globs source files.

Let me not rabbit-hole. The important facts: both full runs exited 0 with 0 failures/errors, and the final run is at final HEAD. The count difference (323 vs 326) is confusing though and a reviewer might ask. Let me spend one cheap check to see if the count is stable now: run pytest --collect-only twice? It gave 338 collected. Hmm, 332 vs 338: 6 difference = exactly the skip count... so 338 = 332 executed + 6 not executed? No: skipped tests ARE collected. 

Maybe verify.py runs pytest with specific args that exclude some dirs (e.g., `--ignore`), giving a different total than my bare collect. So my collect-only (338) isn't comparable to verify.py's 332.

Let me check verify.py's pytest invocation, then reconcile: perhaps it uses `-p no:randomly` etc. Actually the difference between run1 (323+6=329) and run2 (326+6=332) is 3 — could be flaky parametrization from a glob over tracked files... Let me quickly check verify.py's pytest command and whether any test parametrizes over `git ls-files`-like globs that could change with my commits (e.g., a test that parametrizes over features' tasks AC counts?). 

Let me grep verify.py.

  <details><summary>tool output</summary>

  ```text
5:→ 文档一致性检查 → dev 依赖 pin 范围检查 → 密钥模式扫描 → pytest
44:        # symlink（如 .codegraph）被 pytest 当作 collection root 探查。
49:                "pytest",
56:            "pytest",
70:        "依赖 pin / 密钥扫描 / pytest / ruff"


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:15:09Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '40,70p' tools/verify.py"})`

  <details><summary>tool output</summary>

  ```text
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
 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:15:15Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -m pytest -q --collect-only --confcutdir=tests --rootdir=tests tests/unit tests/integration 2>/dev/null | tail -2 && grep -rn \"glob\\|rglob\\|iterdir\\|read_text\" tests/unit/test_f001_line_limit_exemptions.py | head -8"})`


> [reasoning] verify.py runs pytest on tests/unit and tests/integration only (no tests/property, tests/simulation). So collect count from those two dirs: let me count. 338 total collected (all dirs) minus tests/property (0) and tests/simulation (some). Let me count tests/unit + tests/integration collection: likely 332. So the run-2 numbers match collection exactly (326+6=332).

Then why did run 1 report 323+6=329? Because run 1 happened when... hmm, 3 fewer. The only intervening change is the AC reorder. Unless run 1 was executed while a test file was mid-edit? No.

OH WAIT. I know: run #1 (`323 passed`) was executed at a point where `test_f007_design_test_map_goes_red_on_unmapped_test` ... no.

Hmm, let me think about parametrized tests derived from repo content:
- `tests/unit/test_f001_line_limit_exemptions.py` globs files → parametrizes per file. Count changes only if files are added/removed from the glob.
- Maybe some test parametrizes over `docs/features/*/*/spec.md` AC counts? Let me grep for parametrize lists built from globs/globs of docs.

Let me grep for `glob` / `rglob` / `iterdir` in tests to find content-dependent parametrization. Actually simpler: the difference of 3 equals the number of AC-010...? no.

Alternatively, maybe run #1's pytest output "323 passed" was from a run where 3 tests were *still being written*... no, tests were finalized before run #1.

Hmm, hold on: run #1 happened right after commit 6d5ad65. Then I made the AC-reorder commit. The AC reorder changed `docs/features/.../spec.md`. If a test parametrizes over spec.md AC lines... e.g. a test verifying AC-xxx ordering or `tests/unit/test_validate_spec_lifecycle.py` is fixed-count.

Wait, is it possible that the counting difference is because `test_f007_design_test_map...` variant? No.

Let me just check directly: count tests in tests/unit + tests/integration via collect-only, and also check whether some tests are conditionally generated by reading docs (like `test_doc_gate_command.py`). Let me grep for tests that build parametrize from file content.

This is a 2-minute investigation and worth it for the report's credibility (the reviewer will run the gate and may see a different count than my FIX-log). Let me do it.

  <details><summary>tool output</summary>

  ```text
338 tests collected in 1.98s
10:    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
16:        for path in root.rglob("*")
19:        and len(path.read_text(encoding="utf-8").splitlines()) > 350


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:15:29Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -m pytest --version 2>&1 | head -5 && .venv/bin/pip list 2>/dev/null | grep -i \"pytest\" && grep -rn \"TEXT_CHECKS\\|AC_LINE_RE\\|spec.md\" tests/unit/*.py tests/integration/*.py | grep -i \"parametrize\\|for \" | head -10"})`


> [reasoning] 338 collected in tests/unit+tests/integration, but verify.py's run said "326 passed, 6 skipped" = 332. So 6 tests are reported differently... Ah — `-q` output "326 passed, 6 skipped" might omit "deselected"/"xfailed" or the summary might not count something. Actually 338 - 332 = 6. Coincidence that skip count is also 6? Maybe some tests are `xfail`? Or `--confcutdir` differences... my collect-only used the same flags. Hmm, my collect used the same flags and got 338.

Unless: 6 tests are collected but "deselected" — no deselect arg. Or "6 tests are ignored at runtime (pytest.ini `collect_ignore`)"? Collect-only respects that.

Wait, maybe the shell `2>/dev/null` hid a line like "6 deselected". Let me check the full footer: `pytest -q` prints "338 tests collected". In a run, the footer prints "326 passed, 6 skipped in ...". 326+6=332 ≠ 338.

Possibly 6 tests are in a subdir ignored at runtime due to a fixture-based `pytest.skip(allow_module_level=True)` — those show as skipped though.

Hmm: maybe the difference is between run #1's 329 total and collect 338: 9 tests missing? Inconsistent.

Let me stop guessing and get the real footer with full output: run only the two dirs quickly? That's 4+ minutes (the suite's slow parts are integration?). The earlier full verify pytest step took 247s (4min) — mostly what? Let me just run pytest on the two dirs and capture the footer, since I need an accurate number anyway. Actually no: I have accurate numbers from verify.py itself ("326 passed, 6 skipped"), which is the authoritative gate output. The collect-only count (338) differing by 6 could be because 6 tests are marked with something like `pytest.mark.skipif` evaluated at collection... those still show as skipped.

Hmm, maybe `--confcutdir` behaves differently when combined with `--collect-only`? Unlikely.

Whatever the cause, the honest thing: report the gate's own output verbatim (326 passed, 6 skipped) and note the discrepancy question only if relevant. Actually a cleaner approach for the FIX-log: report both runs' verbatim numbers and note that the pytest total differs by 3 between runs because ... I don't know why. That's unsatisfying.

Let me actually resolve it: run pytest with `-q` on the same dirs and see the exact footer + also check for "deselected"/"xfailed". Use `-rA`? Too verbose. Let me run with `-q --tb=no -p no:cacheprovider` and capture the last 3 lines. It'll take ~4min. I'll do it — accuracy matters, and I can also cross-check flakiness.

Actually — hold on. I bet the answer is `tests/unit/test_smoke.py` or something uses `pytest.mark.parametrize` with a list built from `check_doc_consistency.TEXT_CHECKS`: my `test_required_text_removed_goes_red` params = 41 checks... If TEXT_CHECKS count changed between runs — no, unchanged after 6d5ad65.

Hmm, unless run #1 (323 passed) was BEFORE my final commit 6d5ad65? Let me check the sequence again:
- I ran `time .venv/bin/python tools/verify.py` → 323 passed. At that moment HEAD was 6d5ad65? Let me verify: I committed 6d5ad65 ("D010 断言针脚收紧") BEFORE that verify run — yes: sequence was ... d2a55e6 → then mutation script → then commit 6d5ad65 → then verify (323). Yes.

Then AC reorder commit → verify (326).

So +3 tests from a spec-only text reorder?! That means some test parametrization depends on spec.md content. Which? Possibly `tests/unit/test_doc_gate_command.py` or a test that parametrizes over AC lines in F007 spec!? Let me grep for AC-line-driven parametrization. E.g., a test that asserts every AC has a `tests:` path for done features, parametrized over discovered ACs of ACTIVE features? If F007 is draft, maybe it's excluded... but the count changed, so something parametrized over spec content.

Hmm wait — the AC reorder changed line ORDER only. If a test parametrizes over AC IDs, order doesn't change the count. Unless the reorder accidentally changed something else! Did my edit duplicate or delete an AC? I verified AC-001..AC-012 all present exactly once, and validate_spec_lifecycle (which checks duplicates) passed.

Alternatively, maybe the count difference is due to test *ordering/randomization*: if a test module-level skip depends on a previous test? E.g. pytest-randomly plugin shuffles... no `-p no:randomly` seen. Is pytest-randomly installed? If so, with random ordering, tests that mutate global state could skip/error differently! That would explain non-determinism between runs.

Let me check installed plugins: pytest-randomly would explain variance (it also seeds and prints "Using --randomly-seed="). The verify output didn't show that (because `-q`?). Let me check quickly.

Rather than over-invest, let me run pytest twice on the two dirs and compare counts. If they differ, it's non-deterministic (plugin/ordering) and I'll note it honestly. Let me run twice, but that's ~8 min. Hmm.

Cheaper: check for pytest-randomly and for parametrization over docs. Let me grep plugins.

  <details><summary>tool output</summary>

  ```text
pytest 9.1.1
pytest             9.1.1
tests/unit/test_check_doc_consistency.py:19:TEXT_CHECK_IDS = [c.check_id for c in cdc.TEXT_CHECKS]
tests/unit/test_check_doc_consistency.py:21:ALL_DOC_FILES = {rel for chk in cdc.TEXT_CHECKS for rel, _ in (*chk.requires, *chk.forbids)}
tests/unit/test_check_doc_consistency.py:41:@pytest.mark.parametrize("chk", cdc.TEXT_CHECKS, ids=lambda c: c.check_id)
tests/unit/test_check_doc_consistency.py:53:@pytest.mark.parametrize("chk", [c for c in cdc.TEXT_CHECKS if c.forbids], ids=lambda c: c.check_id)
tests/unit/test_check_doc_consistency.py:64:    assert sorted(TEXT_CHECK_IDS) == sorted({c.check_id for c in cdc.TEXT_CHECKS})
tests/unit/test_f001_compose_contract.py:40:    for text, name in ((spec, "spec.md"), (smoke, "test_f001_kronos_smoke.py")):


Incremen
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:15:45Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '14,30p' tests/unit/test_check_doc_consistency.py && echo \"=== git log for this file ===\" && git log --oneline -- tests/unit/test_check_doc_consistency.py | head -8 && echo \"=== who introduced the comprehension ===\" && git log -S \"for chk in cdc.TEXT_CHECKS for rel\" --oneline -- tests/unit/test_check_doc_consistency.py && git status --porcelain"})`


> [reasoning] Interesting! `tests/unit/test_check_doc_consistency.py:21` now says `ALL_DOC_FILES = {rel for chk in cdc.TEXT_CHECKS for rel, _ in (*chk.requires, *chk.forbids)}` — that's NOT what I wrote! I wrote an explicit set:

```python
ALL_DOC_FILES = {
    cdc.SPEC,
    cdc.DESIGN,
    cdc.TASKS,
    cdc.F007_SPEC,
    cdc.F007_DESIGN,
    cdc.F007_TASKS,
}
```

But the file now shows a comprehension. Did something rewrite my test file?! Let me look at the file. Maybe a formatter/agent... or maybe I'm misreading and there are two definitions.

Hmm, this suggests something external modified the file (a hook? a background process?). Let me inspect the test file around lines 15-60 and check git log/blame for that file.

Also the count difference of 3 might be explained if TEXT_CHECKS count changed (e.g., the comprehension yields a different file set → no, that's not test count).

Wait: the test count difference (323 → 326) equals +3. Hmm, if `ALL_DOC_FILES` changed from explicit 6 to a computed set — that doesn't change test count.

Let me look at the file and its git history. Something modified it: possibly the "opencode" plugin auto-format? Or my own earlier edit? No — I wrote the explicit set and committed it in D001 (`65e1832`). Let me check `git log -p` for that file to see whether the comprehension came from a commit or is uncommitted.

git status was clean a moment ago, and HEAD includes d9e0dd3 etc. If the comprehension is committed, then some commit changed it. Let me check.
Something unexpected: my explicit `ALL_DOC_FILES` set now reads as a comprehension. Investigating.

  <details><summary>tool output</summary>

  ```text
import pytest

from tools import check_doc_consistency as cdc

REPO = cdc.ROOT
TEXT_CHECK_IDS = [c.check_id for c in cdc.TEXT_CHECKS]
# 由注册表推导，避免硬编码列表随新增断言（其他 feature 的检视轮次也会追加）失效。
ALL_DOC_FILES = {rel for chk in cdc.TEXT_CHECKS for rel, _ in (*chk.requires, *chk.forbids)}


def _materialize(tmp_path: pathlib.Path, rels: set[str]) -> None:
    # check_text_checks 会读取全部目标文档（便于跨 check 共享缓存），因此副本必须
    # 包含所有目标文件，否则未拷贝的文件会直接抛 FileNotFoundError。
    for rel in sorted(rels | ALL_DOC_FILES):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, dst)
=== git log for this file ===
f405395 fix(f003): R2-002..R2-005 契约补口（Kronos 生命周期/universe-calendar 拆分/DTO 形态/注册表 owner）
24a7631 test(f007): 修正 F003 上游变异测试针脚以对齐 D003 后的 frontmatter
d9e0d
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:15:53Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git rev-parse --short HEAD && git branch --show-current && git log --oneline -12 | cat && echo \"=== f405395 详情 ===\" && git show --stat --format=\"%H%n%an %ad%n%s\" f405395 | head -20 && echo \"=== 我的提交是否还在 ===\" && git merge-base --is-ancestor 225376d HEAD && echo \"225376d is ancestor of HEAD\" && git log --oneline d659db7..HEAD --author-date-order | wc -l"})`


> [reasoning] There's a commit `f405395 fix(f003): R2-002..R2-005 ...` that is NOT mine and NOT in my earlier `git log d659db7..HEAD` listing! Wait — my listing showed 28 commits ending at 6d5ad65 and included only my commits. Let me check: is f405395 an ancestor or a child? git log for the file lists f405395 first (most recent). If f405395 is not in d659db7..HEAD, then it must be an ancestor of HEAD but... Let me check where it is.

Hold on: `git log d659db7..HEAD` showed 28 commits but did NOT include f405395. And the sequence I saw was linear from 65e1832 → ... → 6d5ad65. But now HEAD is 225376d (my AC reorder) and the file log shows f405395 as newest for that file.

So f405395 must be a commit that appeared *after* my last look — i.e., ANOTHER SESSION/AGENT is committing to this repo concurrently! That's exactly the skill's warning: "工作中 HEAD 漂移（git rev-parse --short HEAD 与声明不一致）——先确认漂移来源" and "git status 出现本会话没有动过的文件——先向用户确认归属".

Let me check: `git rev-parse --short HEAD` now, `git log --oneline -12`, and whether f405395 is on top. This is a re-baseline situation. Per the skill I must:
1. Confirm the drift source.
2. Re-baseline and write it into the report.
3. Not attribute foreign changes to my own regressions.

Also the earlier verify runs: run #1 323 passed vs run #2 326 passed — the difference is explained by f405395 (another session adding tests/commits concurrently!). That also explains the ALL_DOC_FILES change (another agent improved it — and it's actually a better implementation than my explicit set, which would break when other features append checks).

Wait, but did f405395 land between run #1 and run #2? Let me check the commit timestamps and the log.

This is important. Let me investigate now.
HEAD moved — a **concurrent session** committed to this repo (`f405395`, not mine). Re-baselining before I finalize the FIX-log.

  <details><summary>tool output</summary>

  ```text
f405395
main
f405395 fix(f003): R2-002..R2-005 契约补口（Kronos 生命周期/universe-calendar 拆分/DTO 形态/注册表 owner）
779c78e fix(f003): R2-001+R2-006 DAG 门禁补收口可达性，T001 去已关闭 Q 引用
d1c1f8f fix(f003): R2-007 [TEST] 组门禁只在 tasks 第 3 节识别
225376d docs(f007): AC-010 归位到 AC-009 之后，恢复编号顺序
6d5ad65 test(f007): D010 断言针脚收紧到实体定义行（变异验证发现弱针脚）
d2a55e6 fix(f007): D001 附带 补 [TEST] 组前置边（旅程验收不悬空）
b345e25 fix(f007): D025 属性测试执行轨与 seed/生成器可复现约束
aa348bb fix(f007): D024 对齐状态词汇、canonical=bench 与 evaluation.registered
e29563e fix(f007): D023 design 行动指令移入 tasks，只保留前置约束声明
24a7631 test(f007): 修正 F003 上游变异测试针脚以对齐 D003 后的 frontmatter
80cbd3d fix(f007): D022 NFR-005/UX-001 落 AC-011 与 tasks verify
5b26dac fix(f007): D021 冻结五阶段 ID 与 failure_taxonomy 三维 schema
=== f405395 详情 ===
f405395f4638f98317a2ea3e5f175b25e1b76fe0
qiaozhi li Thu Sep 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:16:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== f405395 对 F007 spec 的改动 ===\" && git show f405395 -- docs/features/0.2/F007-evaluation-gates/spec.md | cat && echo \"=== f405395 对 tools 的改动 ===\" && git show f405395 -- tools/check_doc_consistency.py | head -110"})`


> [reasoning] YES — a concurrent session (author "qiaozhi li", same person presumably) committed 3 commits on top of mine, at 01:14 (right when my verify run #2 finished). They are:
- d1c1f8f fix(f003): R2-007 [TEST] 组门禁只在 tasks 第 3 节识别
- 779c78e fix(f003): R2-001+R2-006 DAG 门禁补收口可达性，T001 去已关闭 Q 引用
- f405395 fix(f003): R2-002..R2-005 契约补口（Kronos 生命周期/universe-calendar 拆分/DTO 形态/注册表 owner）

And f405395 touched `docs/features/0.2/F007-evaluation-gates/spec.md` (+1 line) and `tools/check_doc_consistency.py` (+76) and the test file (23 lines changed)!

So another agent (the F003 review round-2 fixer? or the F003 reviewer) is working concurrently, and it:
- modified my F007 spec (+1 line) — need to check what
- refactored my ALL_DOC_FILES into a comprehension (in their commit)
- modified tools/check_doc_consistency.py (+76) — need to check they didn't break my checks
- Possibly changed `[TEST]` group detection and DAG gates.

This is exactly the drift scenario. Per skill §0: 
- 工作中 HEAD 漂移 → 先确认漂移来源，把新基线写进报告再继续
- `git status` 出现本会话没有动过的文件 → 先向用户确认归属再决定并入或搁置

Also the "universe-calendar 拆分" in their F003 commit message is suspicious for D004-related scope: F003's finding R2-004 might be about `--universe-calendar`?? Their commit touched F007 spec and architecture. Let me inspect the diff of f405395 (and the other two) to see whether it conflicts with my D004 fix or with my F007 edits.

Key checks:
1. `git show f405395 -- docs/features/0.2/F007-evaluation-gates/spec.md` — what did they change in my file?
2. `git show f405395 -- tools/check_doc_consistency.py` and the test file — did they keep my F007 checks intact and just add theirs?
3. Verify the current state passes all gates (my last verify at 225376d was BEFORE these commits; run #2 showed 326 passed which likely already included some of their test changes? Hmm, run #2 was at 01:14 — the same minute f405395 was authored. Actually my run #2 command started ~01:07 and finished 01:14; their commit was authored 01:14:12. So my run #2 may have picked up their working-tree changes or not. Confusing.

Let me now:
a) inspect their diffs on F007 spec + tools + tests,
b) run the gates at current HEAD (f405395) to see if everything is still green,
c) decide: their changes look like they *strengthened* the F003-era gates (DAG 收口可达性, [TEST] 组只在第3节识别) — these might now enforce more on F007 (e.g. DAG "收口可达性" could flag my F007 task graph!).
d) Re-baseline and record in FIX-log; ask the user about attribution (per skill: confirm ownership with user) — but the ownership is clear (same user's concurrent session). The skill says confirm attribution with the user before merging/ignoring. I'll report it clearly in my answer and keep their changes (they're on top of mine, already committed).

Most urgent: does F007 still pass all gates at f405395? Especially the new "DAG 收口可达性" and "[TEST] 组只在第 3 节识别" gates. Let me run the doc gates + relevant tests now.

Let me inspect and run.
Concurrent session (author `qiaozhi li`, 01:14) committed 3 F003 commits **on top of mine**, touching F007 spec + the gate tools. Inspecting exactly what they changed and whether F007 still passes their strengthened gates.

  <details><summary>tool output</summary>

  ```text
=== f405395 对 F007 spec 的改动 ===
commit f405395f4638f98317a2ea3e5f175b25e1b76fe0
Author: qiaozhi li <qiaozhi_li@126.com>
Date:   Thu Sep 17 01:14:12 2026 +0800

    fix(f003): R2-002..R2-005 契约补口（Kronos 生命周期/universe-calendar 拆分/DTO 形态/注册表 owner）
    
    R2-002：架构 §7.1 新增版本化 Kronos 服务生命周期契约（status/stop/restore、
    contract_version、幂等、超时、E_* 错误码、显存确认、未部署语义）；F003 design §4
    增客户端行为与契约测试载体（tests/integration/test_f003_kronos_lifecycle.py，
    因 verify.py 只收集 unit/integration）；T025/T033 与 BACKLOG「规划中」登记服务端
    端点实现；D013 的 partial 由客户端契约 + 契约测试闭合。
    R2-003：过渡绑定把 universe 与 calendar 拆为两个独立 artifact（分别校验，
    universe_calendar_digest 改为两者组合导出），口径对齐 F007 DR-006。
    R2-004：明确 expression 的唯一形态（仅磁盘 DTO 顶层 + 加载写入 meta，架构对象
    不新增顶层字段），每层单一合法形态。
    R2-005：钉死因子注册表 owner——定义面归 F003 registry/，评测摘要/
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:16:16Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git show 779c78e --stat --format=\"%s\" | head -8 && git show 779c78e -- tools/check_task_dag.py | head -60 && echo \"=== d1c1f8f ===\" && git show d1c1f8f -- tools/validate_spec_lifecycle.py | head -50"})`


> [reasoning] The concurrent session:
- Added F003 R2 checks (fine, additive).
- Added F007 spec line (factor registry owner互认) — additive, no conflict with my D004/D005 (their R2-003 aligns with my DR-006! They wrote F003's transition binding to split universe/calendar "口径对齐 F007 DR-006" — i.e., they consumed my fix).
- Refactored ALL_DOC_FILES into a comprehension (that's why the test file line changed).
- The other two commits (d1c1f8f, 779c78e) changed `[TEST]` group detection to only §3, and DAG "收口可达性".

I need to check the two earlier commits' tool changes since they might now enforce rules on F007's tasks that my fixes must satisfy:
- `[TEST]` 组门禁只在 tasks 第 3 节识别 → my [TEST] group IS in §3 ✓ (need to verify their regex now requires it under §3 specifically).
- DAG 门禁补收口可达性 → might require every task? or that T030's predecessors reach... "收口可达性" could mean: the last task must be reachable from the first (all tasks connected?) or that each task has a path. If they require EVERY task to have an incoming edge (except the first), my F007 graph might fail! Let me check their new check_task_dag logic and run it.

Let me look at d1c1f8f and 779c78e diffs, then run the full doc gates + tests at current HEAD.

This is the critical step: verify F007 still passes the newly strengthened gates at HEAD f405395.

  <details><summary>tool output</summary>

  ```text
fix(f003): R2-001+R2-006 DAG 门禁补收口可达性，T001 去已关闭 Q 引用

 docs/features/0.2/F003-alphagen-vendor/tasks.md | 20 +++++++++++++------
 tests/unit/test_check_task_dag.py               | 26 +++++++++++++++++++++++++
 tools/check_task_dag.py                         | 17 +++++++++++++++-
 3 files changed, 56 insertions(+), 7 deletions(-)
commit 779c78e50dbba6c394ae0ed4efbeae0e3c7bd94f
Author: qiaozhi li <qiaozhi_li@126.com>
Date:   Thu Sep 17 01:14:01 2026 +0800

    fix(f003): R2-001+R2-006 DAG 门禁补收口可达性，T001 去已关闭 Q 引用
    
    R2-001：check_task_dag 从最高任务沿入边反向遍历，任何任务无路径到达收口任务即
    判红（'孤立任务'）；补 test_orphan_task_rejected 与
    test_missing_key_edge_breaks_reachability（最高任务规则通过但关键边缺失仍红）。
    F003 §4 补齐 T001/T002/T006/T010/T011/T012/T015/T022/T023/T026/T028 的边，
    12 个孤立任务清零；T030 验收补人工种子套件。
    R2-006：
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:16:26Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -c \"\nimport sys,pathlib; sys.path.insert(0,'.')\nfrom tools import check_task_dag as dag\nt=pathlib.Path('docs/features/0.2/F007-evaluation-gates/tasks.md').read_text(encoding='utf-8')\nerrs=dag.check_tasks(t)\nprint('F007 DAG errors (%d):' % len(errs))\nfor e in errs: print(' -', e)\n\" && echo \"=== 当前 HEAD 全门（不含 pytest）===\" && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python tools/check_doc_links.py && 
…[truncated])`


> [reasoning] Critical finding: the concurrent session added a **new DAG rule**: "每个任务都必须有路径到达收口任务" (every task must have a path to T030). My F007 task graph has many orphan tasks! Let me check:

Edges: T007→T010, T007→T011, T009→T012, T009→T025, T012→T013, T012→T016, T012→T024, T013→T024, T014→T016, T016→T025, T027→T030, T028→T030, T029→T030, plus the [TEST] predecessors T016,T018,...,T026 → T027/T028/T029.

From T030 backwards: T027/T028/T029 → their predecessors T016,T018..T026 → T016's predecessors: T008,T009,T010,T012,T014 → T012's predecessors: T009 → T009's pred: T008? T008's pred... 

Let me enumerate: T001, T002, T003, T004, T005, T006, T008, T017, T019, T020, T021, T022, T023, T026? (T026 has preds T004/T019? wait I didn't add that edge! Let me check my §4: I added `T0xx -> T026`? No — I never added T004->T026. I only added T026 to the [TEST] predecessor list as a SOURCE (`T016/T018/.../T026 -> T027/T028/T029`). So T026 has no incoming edge; it IS reachable from T027 (since T026→T027 edge exists), so reachability backwards from T030 includes T026 ✓.

Reachability from T030:
- T027,T028,T029 ✓ (preds of T030)
- preds of T027/28/29: T016,T018,T019,T020,T021,T022,T023,T024,T025,T026 ✓
- preds of T016: T008,T009,T010,T012,T014 ✓
- preds of T024: T012,T013 ✓
- preds of T025: T009,T016 ✓
- preds of T012: T009 ✓
- preds of T013: T012 ✓
- preds of T009: from `T008,T009,T010 -> T011,T016,T017` → sources T008,T009,T010 have target T011/T016/T017; they're not preds of T009. Does T009 have incoming? T009's preds: none! Also T008 preds: none (it's a source in T008,T009,T010 -> ...). T010 preds: T007 ✓. T011 preds: T007,T008,T009,T010 ✓. T014 preds: T011,T012 ✓. T017 preds: T008,T009,T010 ✓.

Reachable set from T030: {T030,T027,T028,T029,T016,T018,T019,T020,T021,T022,T023,T024,T025,T026,T008,T009,T010,T012,T014,T013,T007}
NOT reachable: T001,T002,T003,T004,T005,T006,T011,T015,T017 — wait T011 has preds T007,T008,T009,T010 and T011→T014,T015 so T011 is a pred of T014 → reachable ✓. T017: preds T008,T009,T010; T017 → T027? No! T017 is in the [TEST] predecessor list? Let me check: `T016/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029` — T017 is NOT included. So T017 is an orphan → RED.
T015: preds T011,T012; T015 → ? not in [TEST] preds → orphan → RED.
T006: preds T004,T005; T006→? no outgoing → orphan → RED.
T004,T005: T004→T006 (from `T004,T005 -> T006,T011,T012,T013`) → T006 orphan → so T004/T005 unreachable → RED.
T001,T002,T003: → T004 (from `T001,T002,T003 -> T004~T017`) — wait that edge uses `~` range so the parser produces NO edges (T004~T017 isn't T\d{3}). So T001/T002/T003 have no outgoing edges → orphan → RED.
T022: in [TEST] preds ✓ reachable.
T017, T015, T006, T004, T005, T001, T002, T003 = 8 orphans.

So at HEAD f405395, `check_task_dag` on F007 would report 8 orphan tasks. BUT: the gate only enforces for non-draft statuses (F007 is draft) → currently green. However, when F007 moves to ready-for-development, the gate would RED. That's a latent landmine — and it's exactly the kind of thing the reviewer's Round-2 diff-only review would catch (or the next round).

Per the skill: this is `spec-drift`/`process-gap` — a new upstream gate rule landed mid-round (my fix round), so my F007 task graph must be adapted (it's an obligation created by the concurrent commit). As the fixer I should:
1. Fix F007 §4 to eliminate orphans (add edges so every task reaches T030) — same as the concurrent session did for F003.
2. Re-run the DAG gate with status=ready-for-development to prove it passes.
3. Record the re-baseline + this cross-session obligation in FIX-log.

Also check the `[TEST]` §3-only rule: my [TEST] group is inside `## 3. 验证与验收任务` ✓ (I placed it before T030 which is in §3). Let me verify section_body("3. 验证与验收任务") contains "### [TEST]" — yes, since the heading is under §3.

Also the `no_stale_closed_question_task` check applies to F003 SPEC/TASKS only. Not F007. Fine.

Also they refactored ALL_DOC_FILES to be derived from TEXT_CHECKS — good, and it now includes ARCH/BACKLOG which they added as needles.

Let me now:
1. Check current full gate state (doc gates + verify) — my last verify was at 225376d; HEAD is f405395 with 3 more commits. The concurrent session presumably ran their own gate. Let me run the doc gates + the unit tests now (fast), then decide on the full verify.
2. Fix the F007 orphan tasks.
3. Re-baseline FIX-log to f405395(+my new commit).

Before that: per the skill, on foreign changes I should "先向用户确认归属再决定并入或搁置". The ownership is not ambiguous here (it's the same user's other session fixing F003; their commits are already in main on top of mine and largely additive/aligning). But the polite/correct thing is to report it clearly. Since their commits are already committed (not in my worktree), there's nothing to merge/ignore — I just continue on top. I'll flag it prominently in my final answer.

Let me first verify: does F007 pass the new DAG rule at ready-for-development? Let me test to enumerate the orphans precisely.
The concurrent session also **strengthened the DAG gate** (every task must reach the closing task). Checking whether F007's graph survives it.

  <details><summary>tool output</summary>

  ```text
F007 DAG errors (12):
 - 任务 T001 无路径到达收口任务 T030（孤立任务）
 - 任务 T002 无路径到达收口任务 T030（孤立任务）
 - 任务 T003 无路径到达收口任务 T030（孤立任务）
 - 任务 T004 无路径到达收口任务 T030（孤立任务）
 - 任务 T005 无路径到达收口任务 T030（孤立任务）
 - 任务 T006 无路径到达收口任务 T030（孤立任务）
 - 任务 T007 无路径到达收口任务 T030（孤立任务）
 - 任务 T008 无路径到达收口任务 T030（孤立任务）
 - 任务 T010 无路径到达收口任务 T030（孤立任务）
 - 任务 T011 无路径到达收口任务 T030（孤立任务）
 - 任务 T015 无路径到达收口任务 T030（孤立任务）
 - 任务 T017 无路径到达收口任务 T030（孤立任务）
=== 当前 HEAD 全门（不含 pytest）===
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_task_dag: 全部通过
check_doc_consistency: 全部通过


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:16:42Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "newString": "- `T001/T002/T003 -> T004`：先冻结上游契约、预注册方法与权限夹具，再实现身份与隔离。\n- `T004/T005 -> T006`：preview CLI 依赖身份模块与执行层级隔离。\n- `T004/T005 -> T012`：冻结 cohort 与登记依赖身份与隔离能力。\n- `T005 -> T011`：原子发布依赖 tier 物理根与 capability 边界。\n- `T006 -> T013`：canonical/finalize CLI 与 preview CLI 共用参数与错误码契约（`IR-001`/`IR-003`）。\n- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入。\n- `T008 -> T016/T017`：方法论门与 guard 注册表是可测
…[truncated])`


> [reasoning] 12 orphans in F007 (my earlier hand-analysis was incomplete because the [TEST] predecessor edge line has sources T016/T018..T026 but NOT T001-T008,T010,T011,T015,T017). Note T007,T008,T010,T011 appear as orphans too because their edges point to T010/T011/T016/T017, and T010/T011/T016/T017 are themselves orphans (T010→? T010 is a pred of T011? no: `T008,T009,T010 -> T011,T016,T017` — T010→T011, T010→T016, T010→T017. T011→T014,T015; T014→T016 → T014 reachable ✓; T011 reachable via T014 (T014's preds include T011) ✓... hmm, T011 reachable? preds of T014 = {T011, T012}; T014 reachable (pred of T016) → T011 reachable! But the output says T011 orphan. Let me recheck: `T011,T012 -> T014,T015` — that's the line "`T011,T012 -> T014,T015`：综合只消费已发布并登记的 canonical 证据。" So T014's preds = {T011, T012} ✓. T014 is a pred of T016 (from `T007 -> T010/T011`? no). T016's preds = {T008,T009,T010} (from `T008,T009,T010 -> T011,T016,T017`) and {T012,T014} (from my `T012/T014 -> T016`). So T014 → T016 ✓ → T014 reachable → T011 reachable. But output lists T011 as orphan?!

Hmm, maybe my `T012/T014 -> T016` line is part of the T007 line which I edited... Let me just print the parsed edges to see. Maybe some of my edge lines aren't being parsed due to the `~` or formatting. Let me dump edges and the §4 body.

Regardless: I must fix the graph so every task reaches T030. Design: add edges so the whole Phase-1 chain connects:

Current task flow intent:
- T001,T002,T003 → T004..T017 (line uses `T004~T017` which the parser ignores!) → I should rewrite as explicit edges.
- T004,T005 → T006,T011,T012,T013
- T008,T009,T010 → T011,T016,T017
- T009 → T012
- T012 → T013
- T007 → T010/T011
- T012/T014 → T016
- T011,T012 → T014,T015
- T012/T013 → T024
- T009/T016 → T025
- [TEST] preds: T016,T018..T026 → T027/T028/T029
- T027/T028/T029 → T030

To make everything reachable to T030, I need paths from every task to T016 or T024...T026 (which reach [TEST] which reach T030). Concretely add:
- `T001/T002/T003 -> T004` (replace the `~` range line with explicit T001,T002,T003 -> T004) — T001/T002/T003 → T004 ✓ then T004 → T006 → ?
- `T004/T005 -> T006`
- `T006 -> T015`? or `T006 -> T020`? Let me think about intent: T006 (preview CLI) is a prerequisite for T013 (canonical CLI) and T015? Actually T006→T013 would be natural. Let me add `T006 -> T013` (CLI family) — but T013's preds already T012. Adding T006→T013 makes T006 reachable ✓ and T004/T005 reachable via T006 → T013 → T024 → [TEST] → T030 ✓.
- `T007` → T010/T011 already; but T007 orphan means T007 has no *incoming* path to T030... reachability is computed backwards from T030 via incoming edges: for T007 to be reachable, some task reachable-set member must have T007 as a pred, i.e. an edge T007→X where X is reachable. T007→T010: is T010 reachable? T010→T011: is T011 reachable? T011→T014 (T014 reachable ✓) → so T011 reachable → T010 reachable → T007 reachable. But output says all three orphan. So the edges T007→T010/T011 must NOT be parsed!

Why? My line: "- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需..." — the backticked segment is "`T007 -> T010/T011`" then later "`T012/T014 -> T016`". EDGE_SEGMENT_RE = `([^`]*->[^`]*)` finds backticked segments containing "->" ✓. So it should parse. Unless... the `：` after the closing backtick is fine.

Hmm, but the FIRST line I wrote in D007: "- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记..." — parses to T009→T012, T012→T013 ✓.

And the line "`T008,T009,T010 -> T011,T016,T017`" → the hop "T008,T009,T010" split by "/" → ["T008,T009,T010"] which does NOT fullmatch T\d{3} → NO edges from the source side! The parser splits by "/" not ",". So comma-separated sources produce nothing!

Look at parse_edges: `left = [x.strip() for x in left_raw.split("/")]` — only "/" separators. So `T008,T009,T010 -> T011,T016,T017` yields left=["T008,T009,T010"] (not matching T\d{3}) and right=["T011,T016,T017"] (not matching) → zero edges! 

So all the original comma-style edges in F007 §4 (`T001,T002,T003 -> T004~T017`, `T004,T005 -> T006,T011,T012,T013`, `T008,T009,T010 -> T011,T016,T017`, `T011,T012 -> T014,T015`) produce ZERO edges. The gate's parse only supports "/" as the multi-item separator (as in F003's `T030/T031/... -> T036/T037/T038`).

That's why only my "/" style lines produced edges. Good to know — and it means the F003 session's F003 tasks use "/" style.

So to fix F007, I must rewrite §4 edges using "/" separators. Let me redesign §4 completely with "/" separators so every task reaches T030:

Task review:
- T001 (upstream contracts), T002 (prereg config + fixtures), T003 (capability fixtures) → prerequisites for everything: `T001/T002/T003 -> T004`
- T004 (identity/snapshot), T005 [P] (tier isolation) → `T004/T005 -> T006` (CLI), `T005 -> T011` (publish), plus `T004/T005 -> T012`
  But careful: T005 is [P] → `[P]` task must not have a predecessor edge (dst=T005 forbidden). Edges FROM T005 are fine.
- T006 (preview CLI) → `T006 -> T013` (canonical CLI), `T006 -> T015` (schema reader)? Let me keep `T006 -> T013`.
- T007 (stage/cost model) → `T007 -> T010` and `T007 -> T011`
- T008 (methodology gate) → `T008 -> T016`? T008 is a guard; T016 runs full-chain controls. Add `T008 -> T016` and `T008 -> T017` (mutation targets gate). Also `T008 -> T023`?
- T009 (statistics) → `T009 -> T012` (cohort corrections) and `T009 -> T016` (controls) and `T009 -> T025` (second impl)
- T010 (rolling split) → `T010 -> T016`
- T011 (events/atomic publish) → `T011 -> T014`, `T011 -> T015`, `T011 -> T016`
- T012 (cohort registry) → `T012 -> T013`, `T012 -> T016`, `T012 -> T024`
- T013 (canonical/finalize CLI) → `T013 -> T024`, `T013 -> T016`?
- T014 (synthesis) → `T014 -> T016`? Hmm T016 (controls) produces data; synthesis consumes canonical ledger. Let me have `T014 -> T016`? That seems reversed. Better: T016 → T014? But T014 < T016 so edge must go forward: `T014 -> T016` means T016 depends on T014. Semantically T016 (full-chain controls) exercises the whole chain including synthesis → yes T014 → T016 is fine (controls depend on synthesis existing).
- T015 (schema reader) → `T015 -> T016`? yes controls validate schemas. Let me add `T015 -> T019`? T019 runs property tests. Hmm keep simple: `T015 -> T016`.
- T016 (controls) → `T016 -> T025` (second impl), and → T027/28/29 [TEST]
- T017 (mutation) → T027/28/29
- T018..T023 (verify tasks) → T027/28/29
- T024 → T027/28/29
- T025 → T027/28/29
- T026 (property) → T027/28/29
- T027/28/29 → T030

Now verify reachability to T030 for each:
- T030 ← T027/28/29 ← {T016,T017,T018,...,T026} ← ...
- T001/T002/T003 → T004 ✓; T004 → T006 ✓; T006 → T013 ✓; T013 → T024 ✓; T024 → T027 ✓ → T030 ✓. Also T004/T005 → T012 → T024 ✓.
- T005 → T011 → T014 → T016 → T027 ✓. Also T005 → T012 ✓.
- T007 → T010 → T016 ✓ (need `T010 -> T016`).
- T008 → T016 ✓, T008 → T017 ✓
- T009 → T012 ✓
- T010 → T016 ✓ (add)
- T011 → T014 ✓
- T012 → T013 ✓ → T024 ✓
- T013 → T024 ✓
- T014 → T016 ✓
- T015 → T016 ✓ (add)
- T016 → T027 ✓
- T017 → T027 ✓
- T018..T023 → T027/28/29 ✓ (already)
- T024 → T027 ✓
- T025 → T027 ✓ (via [TEST] preds list) — wait I need T025 in that list ✓ yes.
- T026 → T027 ✓
- T027/28/29 → T030 ✓
All reachable ✓.

But wait: T004/T005 → T006 requires T006's preds include T004,T005 — and T006 is not [P], fine.
Also `T005 -> T011` and `T005 -> T012` fine (T005 is source).
Also T002/T003 → T004: T004's preds = {T001,T002,T003} ✓.

Now the `~` in the original line must go: "`T001,T002,T003 -> T004~T017`" → replace with "/" style.

Also keep the explanatory text.

Let me rewrite the whole §4 body cleanly. Current §4 content (after my edits):

```
## 4. 依赖与并行关系

- `T001,T002,T003 -> T004~T017`：先冻结上游、方法与权限夹具。
- `T004,T005 -> T006,T011,T012,T013`：CLI、发布和登记依赖身份与隔离。
- `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。
- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。
- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。
- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。
- `T009/T016 -> T025`：第二实现对照以成员级统计实现与全链控制证据为对照对象。
- `T011,T012 -> T014,T015`：综合只消费已发布并登记的 canonical 证据。
- `T005 [P]` 可与 T004 并行：分别修改隔离能力与纯身份模块，不共享状态。
- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。
- `T016/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029`：旅程验收以各验收套件、变异/并发/属性证据与执行机真实证据为前提（编写早、执行晚）。
```

New §4:
```
## 4. 依赖与并行关系

- `T001/T002/T003 -> T004`：先冻结上游契约、预注册方法与权限夹具，再实现身份与隔离。
- `T004/T005 -> T006`：preview CLI 依赖身份模块与执行层级隔离。
- `T004/T005 -> T012`：冻结 cohort 与登记依赖身份与隔离能力。
- `T005 -> T011`：原子发布依赖 tier 物理根与 capability 边界。
- `T006 -> T013`：canonical/finalize CLI 与 preview CLI 共用参数与错误码契约。
- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入。
- `T008 -> T016/T017`：方法论门与 guard 注册表是可测前置，全链控制与变异以其为前提。
- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现。
- `T010/T011 -> T016`：全链控制需要稳定性报告与已发布证据。
- `T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。
- `T012/T014 -> T016`：全链控制还需 canonical registry 与 synthesis（漏斗/失败汇总）。
- `T014/T015 -> T019`：schema reader 与综合报告是属性/验收测试的读取面。
- `T011/T012 -> T014/T015`：综合只消费已发布并登记的 canonical 证据。
- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。
- `T009/T016 -> T025`：第二实现对照以成员级统计实现与全链控制证据为对照对象。
- `T005 [P]` 可与 T004 并行：分别修改隔离能力与纯身份模块，不共享状态。
- `T016/T017/T018/T019/T020/T021/T022/T023/T024/T025/T026 -> T027/T028/T029`：旅程验收以各验收套件、变异/并发/属性证据与执行机真实证据为前提（编写早、执行晚）。
- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。
```

Check forward-only: T014/T015 -> T019 ✓ (15<19). All others ✓.
Check [P]: only T005; no edge with dst T005 ✓.
Reachability: T015→T019→T027 ✓. T017→T027 ✓ (in list). T010→T016 ✓. T011→T016 ✓. All good.

Hmm, T018/T019/T020 target from T014/T015 → fine.

Also T002 → T004 ✓.

Now, do the TEXT_CHECKS needles for D007/D008 still hold? 
- D007 requires "`T009 -> T012`" and "`T012 -> T013`" — my new text keeps both as substrings: "`T009 -> T012`：" ✓ and "`T012 -> T013`：" ✓.
- D008 requires "`T007 -> T010/T011`" ✓ and "`T012/T014 -> T016`" ✓ both retained.

Good.

Also the doc-consistency check runs on the whole repo; the concurrent session's checks require their F003 needles — those pass (their commits).

Also need to double-check: does the new DAG gate rule apply to other features? F003 non-draft — the concurrent session fixed F003. F008 is draft. Let me verify global check_task_dag passes at HEAD (it did pass in the run above ✓).

Now, additionally: does F008's task graph have orphans? Not my scope; gate skips draft. But if the reviewer's new rule is generic, F008 will need it later — not my concern now (F008 isn't in this review).

Let me now:
1. Apply the §4 rewrite.
2. Verify DAG passes (including with status=ready-for-development).
3. Commit.
4. Re-run full verify (round-end gate at final HEAD).
5. Update FIX-log with re-baseline + this extra finding (call it an added obligation from the concurrent gate change, honest labeling).
6. Report to user.

Let me apply the edit.
Config gap found: the new gate rule requires every task to reach the closing task, and F007's §4 used comma-style edges the parser ignores. Rewriting §4 with the parser's `/` syntax and full reachability.

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:17:09Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python -c \"\nimport sys,pathlib; sys.path.insert(0,'.')\nfrom tools import check_task_dag as dag\nt=pathlib.Path('docs/features/0.2/F007-evaluation-gates/tasks.md').read_text(encoding='utf-8')\nerrs=dag.check_tasks(t)\nprint('F007 DAG errors:', errs or 'none')\ne=dag.parse_edges(t); ids=[x for x,_ in dag.parse_task_lines(t)]\nprint('edges:', len(e), 'tasks:', len(ids))\nprint('unreachable check ok:', not errs)\n\" && .venv/bin/python t
…[truncated])`

  <details><summary>tool output</summary>

  ```text
F007 DAG errors: none
edges: 65 tasks: 30
unreachable check ok: True
check_doc_consistency: 全部通过
validate_spec_lifecycle: 全部通过


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:17:18Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && D=docs/features/0.2/F007-evaluation-gates && sed -i 's/^status: draft$/status: ready-for-development/' $D/spec.md && sed -i 's/\\(| F007-evaluation-gates | [^|]*| \\)draft\\( |\\)/\\1ready-for-development\\2/' BACKLOG.md && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python tools/check_task_dag.py && .venv/bin/python tools/check_doc_consistency.py && .venv/bin/python tools/check_doc_links.py; echo \"preflight-exit=$?\" ; git ch
…[truncated])`


> [reasoning] F007 DAG now clean under the strengthened rule (65 edges, 30 tasks, no orphans).

Now let me also confirm the ready-for-development pre-flight again (with the new stricter gate), then commit, then run the full verify at final HEAD.

Let me do the pre-flight: flip spec+BACKLOG status temporarily, run all four doc gates, restore.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_task_dag: 全部通过
check_doc_consistency: 全部通过
check_doc_links: 相对链接全部可解析
preflight-exit=0
 M docs/features/0.2/F007-evaluation-gates/tasks.md
(restored)


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:17:27Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git add -A docs/features/0.2/F007-evaluation-gates/tasks.md && git commit -q -m \"fix(f007): §4 依赖边改 / 语法并消除 12 个孤立任务（对齐 F003 R2-001 收口可达性门）\" && git log --oneline -1 && git rev-parse --short HEAD"})`

  <details><summary>tool output</summary>

  ```text
6b5aea3 fix(f007): §4 依赖边改 / 语法并消除 12 个孤立任务（对齐 F003 R2-001 收口可达性门）
6b5aea3


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:17:35Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"HEAD-before=$(git rev-parse --short HEAD)\" && { time .venv/bin/python tools/verify.py ; } > /tmp/opencode/f007_verify_final2.log 2>&1; echo \"exit=$?\" && grep -E \"全部通过|全部可解析|passed|All checks|already formatted\" /tmp/opencode/f007_verify_final2.log && tail -2 /tmp/opencode/f007_verify_final2.log && echo \"HEAD-after=$(git rev-parse --short HEAD)\" && date \"+%Y-%m-%d %H:%M %Z\"", "timeout": 900000})`


> [reasoning] Now run the full verify.py at final HEAD 6b5aea3 (round-end gate with the concurrent session's strengthened gates included).

Note: the concurrent session may still be working (they committed at 01:14; it's now ~01:2x). If they commit again mid-verify, I'd have another drift. I'll capture HEAD before/after the run and report accordingly.

Let me run the full gate.
Round-end full gate at final HEAD `6b5aea3` (now including the concurrent session's strengthened gates).

  <details><summary>tool output</summary>

  ```text
HEAD-before=6b5aea3
exit=0
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_task_dag: 全部通过
check_doc_consistency: 全部通过
329 passed, 9 skipped in 332.60s (0:05:32)
All checks passed!
110 files already formatted
verify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff
verify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥扫描 / pytest / ruff
.venv/bin/python tools/verify.py  268.60s user 44.85s system 70% cpu 7:26.14 total
HEAD-after=6b5aea3
2026-09-17 01:25 HKT


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:25:12Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git rev-list --count origin/main..HEAD && git log --oneline -1 && git log --oneline -3 | cat && grep -c \"passed\" /tmp/opencode/f007_verify_final2.log"})`


> [reasoning] Full gate green at 6b5aea3: 329 passed, 9 skipped (skips increased from 6 to 9 — because the concurrent session added F003 Kronos lifecycle contract tests that skip without环境; they mentioned "test_f003_kronos_lifecycle.py 因 verify.py 只收集 unit/integration"). 332.6s, exit 0, HEAD stable before/after (no new drift during the run), 01:25 HKT.

Now update FIX-log with:
1. Re-baseline note (concurrent session's 3 commits landed mid-round; new baseline f405395 → my final commit 6b5aea3).
2. The extra finding: cross-session gate strengthening created 12 orphan tasks in F007 → fixed in 6b5aea3.
3. Final gate numbers at 6b5aea3 (329 passed, 9 skipped, 332.60s, 01:25 HKT).
4. Update the "8 findings" mention? No.
5. Update HEAD/ahead count references: HEAD = 6b5aea3; ahead = ? let me compute (origin/main..HEAD). Previously 52 at 225376d; +3 concurrent +1 mine = 56.

Let me get the count and then edit FIX-log sections:
- "修复后 HEAD：`6d5ad65`（...51 个提交，未推送）" → "修复后 HEAD：`6b5aea3`（...56 个提交，未推送）"
- Add a 基线与范围 subsection about the drift.
- 附带提交: add 6b5aea3 + note the concurrent commits.
- gate block: replace with final run + keep the earlier runs summary.
- 需要检视方独立核对的点: add the cross-session item.

Let me get numbers.

  <details><summary>tool output</summary>

  ```text
56
6b5aea3 fix(f007): §4 依赖边改 / 语法并消除 12 个孤立任务（对齐 F003 R2-001 收口可达性门）
6b5aea3 fix(f007): §4 依赖边改 / 语法并消除 12 个孤立任务（对齐 F003 R2-001 收口可达性门）
f405395 fix(f003): R2-002..R2-005 契约补口（Kronos 生命周期/universe-calendar 拆分/DTO 形态/注册表 owner）
779c78e fix(f003): R2-001+R2-006 DAG 门禁补收口可达性，T001 去已关闭 Q 引用
2


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:25:23Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "newString": "- 修复后 HEAD：`6b5aea3`（本地 `main` 领先 `origin/main` 56 个提交，未推送）。\n\n**基线与漂移记录（本轮实测命中 skill §0 场景）**：修复开始于 `main@d659db7`。修复过程中\n`main` 被**另一并行会话**（commit author `qiaozhi li`，2026-09-17 01:14）在**我的提交之上**\n追加 3 个 F003 提交：`d1c1f8f`（[TEST] 组门禁只在 tasks 第 3 节识别）、`779c78e`（DAG 门禁补\n**收口可达性**：任何任务必须有路径到达收口任务，否则判\"孤立任务\"）、`f405395`（F003 R2-002..R2-005\n契约补口；其中 R2-003 的 universe/calendar 拆分明确\"口径对齐 F007 DR-006\"，即消费了本轮的 D004 
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:25:38Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "newString": "- `6d5ad65` — **修复自伤**：D010 断言初版针脚过弱（只要求字面 `DR-005`，改名后仍绿），\n  真实仓库变异验证发现后收紧为实体定义行 `**DR-005**：\\`HoldoutBudgetLedger\\``。\n- `d2a55e6` — D001 附带：补 `T0xx -> T027/T028/T029` 旅程验收前置边（避免 [TEST] 组悬空）。\n- `225376d` — 文档整理：`AC-010` 归位到 `AC-009` 之后，恢复 AC 编号顺序。\n- `6b5aea3` — 跨会话门禁义务：§4 依赖边改 `/` 语法并消除 12 个孤立任务（见上「跨会话门禁新增义务」）。", "oldString": "- `6d5ad65` — **修复自伤**：D010 断言初版针脚过弱（只要求字面 `DR-005`，改名后仍绿），\n  真实仓库变异验证发现后收紧为实体
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:25:51Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "newString": "```text\n$ time .venv/bin/python tools/verify.py            # 最终轮末门禁，基线 main@6b5aea3\nvalidate_spec_lifecycle: 全部通过\ncheck_doc_links: 相对链接全部可解析\ncheck_task_dag: 全部通过\ncheck_doc_consistency: 全部通过\ncheck_dep_pins: 全部依赖版本在声明范围内（runtime + dev）\ncheck_secrets: 无密钥形态命中\n329 passed, 9 skipped in 332.60s (0:05:32)\nAll checks passed!\n110 files already formatted\nverify.py 全部通过：生命周期 / 文档链接 / 任务 DAG / 文档一致性 / 依赖 pin / 密钥
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:26:05Z

- **tool**: `edit({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "newString": "1. 上表 commit 短哈希与 diff 是否一致（`git show <hash>`）；一条 finding 一个 commit，另有 4 条附带提交（2 条针脚修复 `24a7631`/`6d5ad65`、1 条 [TEST] 前置边 `d2a55e6`、1 条 AC 归位 `225376d`）+ 1 条跨会话门禁义务 `6b5aea3`。\n2. 新增 24 条 `TEXT_CHECKS` + 1 条解析式 check 是否逐条可红（见 `regression_tests`）；特别核对\n   `holdout_budget_ledger_exists` 收紧后的针脚（`6d5ad65`）。\n3. `docs/features/0.2/F007-evaluation-gates/tasks.md` 的 T001–T030 是否连续唯一、§4 入边是否覆盖 T030，\n   以及 T027–T029 是否为
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:26:18Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"--- 检视报告未被写入（25 条 open 应保持） ---\" && grep -c \"^    status: open\" docs/reviews/CURRENT-doc-F007.md && grep -c \"stop_condition_met: false\" docs/reviews/CURRENT-doc-F007.md && echo \"--- FIX-log 已有两轮声明 ---\" && grep -n \"^## \" docs/reviews/FIX-log.md && echo \"--- worktree ---\" && git status --porcelain && echo \"(clean)\" && echo \"--- 当前全门 ---\" && .venv/bin/python tools/validate_spec_lifecycle.py && .venv/bin/python tools/check_task_
…[truncated])`


> [reasoning] Also fix the "findings" intro line that says "本轮处理 F007-D001 … F007-D025，共 25 条，全部 fixed" — still accurate. And the "gate" sentence in 基线与范围 mentions 51 commits — already fixed.

Also I should double check the doc-consistency `f007_test_group_present` check still holds after my §4 rewrite (yes, verified green).

Let me do a final sanity pass:
1. Worktree clean? (FIX-log is ignored.)
2. Current gates green at HEAD.
3. Also verify the reviewer's CURRENT-doc-F007.md untouched (I never edited it). Let me confirm via mtime/hash comparison isn't possible without a stored copy; but I know I never wrote to it. I could check that its content still has 25 `status: open` entries — quick grep count.

Let me run final checks and then write the summary answer.

Also: update todos to completed.

Let me finalize.

  <details><summary>tool output</summary>

  ```text
--- 检视报告未被写入（25 条 open 应保持） ---
25
4
--- FIX-log 已有两轮声明 ---
9:## Round 1 · 2026-09-16 · report_type: doc-review
173:## F007 · Round 1 修复声明 · 2026-09-17 · report_type: doc-review
--- worktree ---
(clean)
--- 当前全门 ---
validate_spec_lifecycle: 全部通过
check_task_dag: 全部通过
check_doc_consistency: 全部通过
................                                                         [100%]
88 passed in 1.16s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T17:26:34Z

- **tool**: `todowrite({"todos": [{"content": "D001 tasks [TEST] 组 - done (65e1832/d2a55e6)", "priority": "high", "status": "completed"}, {"content": "D002 F003 摄入契约 - done (ccf577d)", "priority": "high", "status": "completed"}, {"content": "D003 F008 上游 - done (5728ccc)", "priority": "high", "status": "completed"}, {"content": "D004 universe/calendar 拆分 - done (b251826)", "priority": "high", "status": "completed"}, {"content": "D005 无前视三层 - done (59d28d5)", "priority": "high", "status": "completed"}, {"content": "D00
…[truncated])`


> [reasoning] Everything verified:
- Reviewer's CURRENT-doc-F007.md untouched (25 status: open, stop_condition_met: false, no writes from me).
- FIX-log has my new declaration appended (append-only respected).
- Worktree clean.
- All gates green; 88 tests pass in the three gate test files.

Let me update the todos to completed and write the final answer.

Final answer structure (ADHD-friendly): lead with next action/answer, numbered, short, with the one 2-minute next action.

Key content:
1. What I did: fixed all 25 F007 findings as fixer, per review-convergence fixer protocol; 25 finding-commits + 4 accompanying + 1 cross-session obligation.
2. Evidence: per-finding check_id + mutation tests; real-repo mutation verification; full gate green at 6b5aea3 (329 passed, 9 skipped); ready-for-development pre-flight green.
3. Two honest fix-regressions found & closed.
4. Re-baseline event: concurrent F003 session's 3 commits changed gates mid-round → 12 orphans fixed.
5. What I did NOT do: no writes to CURRENT-doc-F007.md, no deletion, no RETROSPECTIVE writeback, no push/CI. Reviewer's turn.
6. Next action (<2 min): reviewer runs the independent verification commands, or (user) tell me to hand off.

Keep it tight. Let me include the key file paths and commit hashes.

Let me mark todos complete first.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "D001 tasks [TEST] 组 - done (65e1832/d2a55e6)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D002 F003 摄入契约 - done (ccf577d)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D003 F008 上游 - done (5728ccc)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D004 universe/calendar 拆分 - done (b251826)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D005 无前视三层 - done (59d28d5)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D006 样本量三级 - done (36b6564)",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "D007 DAG 边 - done (26c7b6d)",
    "status": "completed",
    "priority": "medium"
  },
  {
    "content": "D00
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T17:26:49Z

F007 修复完成，等待检视方复核（不自行收口）。

## 结果

**25/25 finding 全部修复**（原 8 High / 13 Medium / 4 Low → 0 阻塞），一 finding 一 commit：`65e1832` … `b345e25`，最终 HEAD **`6b5aea3`**（本地 `main`，56 commits ahead，**未推送**）。

**轮末全量门禁**（`tools/verify.py` @ `6b5aea3`）：全绿 · `329 passed, 9 skipped` · exit 0 · 01:25 HKT；9 个 skip 全是需执行机能力/环境开关的集成用例。

## 3 件你需要知道的事

1. **并行会话改了我的基线**：F003 那边在 01:14 于我的提交之上追加 3 个 commit（`d1c1f8f`/`779c78e`/`f405395`），其中 `779c78e` 新增「每个任务必须有路径到收口任务」门禁。按 skill §0 我 re-baseline 而没当自己的回归，并补完新义务：F007 §4 原用**逗号分隔**边（门禁解析器只认 `/`）→ **12 个孤立任务**，已重写为 `/` 语法（65 边/30 任务/0 孤立，`6b5aea3`）。他们 R2-003 的 universe/calendar 拆分还明确「口径对齐 F007 DR-006」，即消费了我的 D004 修复。
2. **自己抓出 2 条 fix-regression**：`24a7631`（D003 改 frontmatter 使 F003 变异针脚失配变红）、`6d5ad65`（D010 针脚过弱：只要求字面 `DR-005`，改名后仍绿 → 收紧到实体定义行）。两条都在同轮闭合并已锁进测试。
3. **门禁有牙**：新增 24 条 `TEXT_CHECKS` + 1 条解析式 check（tasks⊆design 测试映射），逐条做变异验证；并做了**真实仓库**变异取证（写回 `--universe-calendar` → 红；删 `T009 -> T012` → 红；复原）。另把 F007 临时置 `ready-for-development` 预演，四道文档门全绿。

## 未执行（按 skill 归检视方）

- `docs/reviews/CURRENT-doc-F007.md` **零写入**（仍是 25×`status: open`、`stop_condition_met: false`）
- 未删 `CURRENT-doc-F007.md` / `FIX-log.md`；未回写 `RETROSPECTIVE.md`；未 push、未取 CI

修复声明已 append 到 `docs/reviews/FIX-log.md:173`（含逐 finding commit/check_id/变异用例表 + 基线漂移记录）。

## 下一步（<2 分钟，二选一）

1. **检视方视角**：`git show 6b5aea3 --stat` + `.venv/bin/python tools/check_doc_consistency.py`，从 `docs/reviews/FIX-log.md` 的「需要检视方独立核对的点」5 条逐条核对，通过后原子写 `CURRENT-doc-F007.md` 的 `status: fixed`（`fix_summary`+`regression_test`+`resolved_round` 同时落笔）。
2. 若要我做，就说「切检视方复核」——我会显式切视角独立核对（不把「我刚写完」当「已复核」）。
