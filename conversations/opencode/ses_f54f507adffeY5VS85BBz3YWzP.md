---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f54f507adffeY5VS85BBz3YWzP"
title: "Audit F003 cross-feature fixes (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T16:26:58Z"
updated_at: "2026-09-16T16:38:04Z"
tokens_input: 543100
tokens_output: 4667
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Audit F003 cross-feature fixes (@Sisyphus-Junior subagent)

## user · 2026-09-16T16:26:58Z

TASK: Recheck F003 cross-feature and upstream contracts after fixes, with attention to F007/F008/F004/architecture/PRD/ADR consistency. EXPECTED OUTCOME: A compact verdict list and any new or carried findings with exact file:line evidence. REQUIRED TOOLS: Read-only repository inspection. MUST DO: Check whether F007 now declares all F003 consumed contracts, whether F008's universe artifact is actually compatible, whether F003's Kronos owner/dep is legitimate despite F004 state, whether architecture FactorDef and pool contract align, and whether PRD/ADR requirements are fully represented. Inspect only changed or adjacent sections, except full-scan upgrade is allowed due >30% diff. MUST NOT DO: No edits, no status updates, no invented implementation assumptions. CONTEXT: /home/georg/projects/alphamill; HEAD d659db7; F003 Round 2. Output Chinese.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T16:26:58Z

- **tool**: `skill({"name": "review-convergence", "user_message": "Recheck F003 cross-feature and upstream contracts after fixes at HEAD d659db7. Read-only repository inspection only; output compact Chinese verdict list and exact file:line evidence. Focus F007/F008/F004/architecture/PRD/ADR consistency."})`


> [reasoning] **Preparing review-convergence approach**

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

## assistant · 2026-09-16T16:27:27Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件", "status": "in_progress", "priority": "high"}, {"content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据", "status": "pending", "priority": "high"}, {"content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict", "status": "pending", "priority": "high"}]})`


> [reasoning] **Planning git status and codegraph inspection**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T16:27:55Z

- **tool**: `codegraph_codegraph_explore({"query": "F003 Round 2 F007 F008 F004 FactorDef pool contract Kronos owner dependency PRD ADR architecture changed adjacent sections", "projectPath": "/home/georg/projects/alphamill", "maxFiles": 12})`

开始第 1/3 步：锁定 `d659db7` 基线与 Round 2 的实际变更范围；随后只读取相邻契约证据，不改动仓库。

  <details><summary>tool output</summary>

  ```text
**Dynamic-dispatch links among your symbols**
(synthesized — the indirect hops grep/Read would reconstruct; the `@file:line` is the wiring site)

- emit → changed   [dynamic: callback via `subscribe` @deepseek-harness/packages/extensions/ui-cordis/tests/versioning.client.spec.ts:104]

> Full source for these symbols is below — the call flow among them, followed by their bodies.
**Exploration: F003 Round 2 F007 F008 F004 FactorDef pool contract Kronos owner dependency PRD ADR architecture changed adjacent sections**

Found 32 symbols across 3 files.

**Blast radius — what depends on these (update/verify before editing)**

- `DependencySection` (deepseek-harness/scripts/verify-package-dependencies.ts:31) — 6 callers in `deepseek-harness/scripts/verify-package-dependencies.ts`; ⚠️ no covering
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:28:48Z

- **tool**: `bash({"command": "git branch --show-current && git rev-parse --short HEAD && git status --short && git diff --stat d659db7^ d659db7 && git diff --name-only d659db7^ d659db7", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/{CLAUDE.md,AGENTS.md,PRD*,ADR*,architecture*,tasks.md,CURRENT-*,FIX-log.md,RETROSPECTIVE.md}"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/*F00[3478]*"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/*{f003,F003,f007,F007,f008,F008,f004,F004}*"})`


> [reasoning] **Verifying repository contents and docs**

  <details><summary>tool output</summary>

  ```text
main
b251826
 M docs/features/0.2/F007-evaluation-gates/spec.md
 tests/unit/test_check_doc_consistency.py   | 135 ++++++++++++
 tests/unit/test_check_task_dag.py          |  84 +++++++
 tests/unit/test_validate_spec_lifecycle.py |  36 ++-
 tools/check_doc_consistency.py             | 338 +++++++++++++++++++++++++++++
 tools/check_task_dag.py                    | 169 +++++++++++++++
 tools/validate_spec_lifecycle.py           |   8 +
 tools/verify.py                            |  14 +-
 7 files changed, 779 insertions(+), 5 deletions(-)
tests/unit/test_check_doc_consistency.py
tests/unit/test_check_task_dag.py
tests/unit/test_validate_spec_lifecycle.py
tools/check_doc_consistency.py
tools/check_task_dag.py
tools/validate_spec_lifecycle.py
tools/verify.py


Incremental: 0 files updated, 0 no
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 13 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md
/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md
/home/georg/projects/alphamill/docs/reviews/FIX-log.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md
/home/georg/projects/alphamill/CLAUDE.md
/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md
/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md
/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md
/home/georg/projects/alphamill/docs
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md
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
-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 4 file(s)

/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md
/home/georg/projects/alphamill/tests/unit/test_f004_compose_profile_contract.py
/home/georg/projects/alphamill/tests/unit/test_f004_kronos_runtime_contract.py
/home/georg/projects/alphamill/tests/integration/test_f004_real_profile.py
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup do
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:29:03Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md", "limit": 240})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md", "limit": 240})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 280})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md", "limit": 220})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "limit": 220})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md", "limit": 220})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md", "limit": 220})`


> [reasoning] **Investigating commit mismatch and project indexing**
基线检查发现不一致：当前 `main` 的 HEAD 是 `b251826`，不是用户给定的 `d659db7`；且工作树有未提交的 F007 `spec.md` 修改。按审查协议以实际 HEAD 重新基线，并将该外部修改视为只读证据，不触碰。

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
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F008
4: version: "0.2"
5: related_features: [F001, F002, F003, F007]
6: topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
7: doc_kind: tasks
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F008：宇宙扩容与 point-in-time 宇宙台账 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
20: - `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
21: - 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
22: - **机器边界**（架构 §7.1、`docs/SOP.md` §3）：回填、质量门、导出、备份在执行机 `qiaozhi-lt` 执行并记 hostn
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-15
10: ---
11: 
12: # F004：Kronos 真实推理运行时 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
20: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
21: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
22: - 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。
23: - 实现任务遵循先红后绿：任务内的契约测试必须先失败（复现缺口）再随实现转绿，不得先实现后补测试。
24: 
25: ## 1. 前置条件
26: 
27
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 1
4: date: 2026-09-16
5: prior_report: none
6: scope: full-scan
7: stop_condition_met: false
8: severity_counts: {critical: 0, high: 14, medium: 7, low: 1}
9: issues:
10:   - id: F003-D001
11:     title: "factor_id 含 run_seq，跨 run 变动，与「相同 factor_id 集合」矛盾"
12:     severity: high
13:     category: correctness
14:     root_cause: root-cause
15:     origin: original-coding
16:     pattern_tag: "spec-internal-contradiction"
17:     status: open
18:     tracked_task: ""
19:     fix_summary: ""
20:     regression_test: "proposed:tools/check_doc_consistency.py::test_factor_id_has_no_run_seq"
21:     suggested_fix: "design §3 改为 factor_id = <generator>_<def
…[truncated]
  ```
  </details>

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

## assistant · 2026-09-16T16:29:54Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件", "status": "completed", "priority": "high"}, {"content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据", "status": "in_progress", "priority": "high"}, {"content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict", "status": "pending", "priority": "high"}]})`


> [reasoning] **Planning targeted spec and design review**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T16:30:38Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 360})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md", "limit": 360})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md", "limit": 260})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "limit": 260})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 180, "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 130, "limit": 80})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md", "limit": 140})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md", "limit": 140})`

第 1/3 步完成，实际基线为 `main@b251826`。第 2/3 步核对四条关键链：F007 是否真正承接 F003、F008 artifact 形态、F004 owner/状态、以及 FactorDef/pool 与 PRD/ADR 的一致性。

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
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md</path>
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
23: - **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR2.1~FR2.6；`docs/alphamill-architecture.md` §三（`factor_factory/`
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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F008
4: version: "0.2"
5: related_features: [F001, F002, F003, F007]
6: topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
7: doc_kind: design
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F008：宇宙扩容与 point-in-time 宇宙台账 - 设计
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
23: - **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR1.5/FR1.1/FR1.4/FR1.7；`docs/alphamill-archite
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
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
180: ├── db/                          # 口径唯一居所（ADR-0005）：init.sql + migrations/ 版本化 SQL 视图；
181: │                                #   应用账本与 runner 见 tools/apply_migrations.py（schema_migrations）
182: ├── web/                         # 自建前端 SPA（ADR-0005）：构建产物由 api 服务静态托管，生产运行时无 Node
183: ├── scripts/                     # 实验运行器、报告生成、verify 脚本（薄入口）
184: ├── reports/                     # 实验 manifest + 归档报告（运行产物）
185: └── src/alphamill/               # 唯一 Python 包
186:     ├── data_bridge/             # FR1：TimescaleDB → Parquet + manifest
187:     │   ├── export_ohlcv.py
188:     │   ├── export_derivatives.py
189:     │   └── manifest_schema.json
190:     ├── factor_factory/          # FR2：假
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
130: 
131: ## 四、功能需求
132: 
133: ### FR1 数据治理与研究快照
134: 
135: - **FR1.1 联机采集**：TimescaleDB 承担流式采集、幂等修订、连续聚合、质量标记和运营查询。
136: - **FR1.2 不可变快照**：data_bridge 将 OHLCV、funding、basis、OI、Kronos 信号与必要日志导出为
137:   分区 Parquet；每个 dataset 独立生成含来源、时间、口径、行数、质量状态、`data_version` 和
138:   语义 `value_digest` 的 manifest。
139: - **FR1.3 研究只读边界**：挖掘、评测和回测只通过 DuckDB 读取有效 Parquet 快照，不直读修订态
140:   TimescaleDB；失效快照必须被下游拒绝。
141: - **FR1.4 双口径与时间语义**：`close_adjusted` 用于收益，`close_raw` 用于成交模拟；所有时间使用
142:   UTC，并维护湖内 pair、研究 symbol 与 Freqtrade pair 的显式映射。
143: - **FR1.5 数据质量与扩容**：宇宙扩至 30~50 对前完成缺失、重复、未闭合 K 线和跨周期对账，
144:   保存 point-in-time 宇宙成员关系以避免幸存者偏差。历史回填约 4600 万行，是项目所有者负责的
145:   独立工作流，预计 1~2 周 wall-clock。
146: - **FR1.6 灾备**
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md</path>
<type>file</type>
<content>
1: # ADR-0001：因子挖掘主引擎选型 —— AlphaGen vendor + 冒烟闸门 + 降级阶梯
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 证据全文：[`docs/alphamill-research-factor-mining.md`](../alphamill-research-factor-mining.md)
7: 
8: ## 背景
9: 
10: PRD G3 要求因子工厂达到 ≥100 名义候选/周，同时报告有效独立数、来源和门禁漏斗；
11: quant-crypto 实测约 5 个/周，探索能力不足。
12: 对 2026-09 时点开源生态的调研结论：
13: 
14: - **AlphaGen**（ICT-FinD-Lab/alphagen，原 RL-MLDM，1.2k★）：RL 表达式生成 + 线性协同池；
15:   核心优势是代码冻结带不走的——协同池（增量 IC reward，机制性防冗余）+ GPU 张量评估（吞吐）+ 量化原生算子。
16:   已知问题：无 LICENSE（个人私有使用，风险可忽略）；核心 21 个月未实质更新；
17:   requirements.txt 自身损坏（`qlib==0.0.2.dev20` 是装错的包、numpy/pandas 为 2021 版）。
18: - **gplearn**：v0.4.3 复活（2026-01），BSD-3，但无协同概念、fitness 全样本评估有结构性泄漏
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

## assistant · 2026-09-16T16:31:09Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md", "offset": 1, "limit": 250})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md", "offset": 210, "limit": 260})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md", "offset": 1, "limit": 260})`
- **tool**: `bash({"command": "git diff -- docs/features/0.2/F007-evaluation-gates/spec.md && git log --oneline --decorate -8", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] **Analyzing F007 and F003 compatibility issues**

> [reasoning] **Clarifying F003 design and architecture discrepancies**

> [reasoning] **Reviewing PRD FR2.5 coverage in F003 and F007**

> [reasoning] **Inspecting F007 design and git diff**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: design
8: created: 2026-09-13
9: updated: 2026-09-17
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
24: - **ADR / 上游 Contract**：ADR-0003、ADR-0005、A
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
5: related_features: [F002, F003, F004, F008]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: tasks
8: created: 2026-09-13
9: updated: 2026-09-17
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
25: - [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md</path>
<type>file</type>
<content>
210:     tracked_task: ""
211:     fix_summary: ""
212:     regression_test: "proposed:tools/check_doc_consistency.py::test_gpu_schedule_protocol_and_owner"
213:     suggested_fix: "design §5 增可验证调度协议（FIFO 序号／等待超时／持锁与释放的状态记录）；为 Kronos 卸载钉 live owner（F003 加编排任务或 F004 加任务并登记跨 feature 边），写明 F004 后移时 FIFO 如何取证"
214:     disposition_reason: ""
215:     location: "docs/features/0.2/F003-alphagen-vendor/spec.md:121,258,335; docs/features/0.2/F003-alphagen-vendor/design.md:174-187,191; docs/features/0.2/F004-kronos-inference-runtime/tasks.md:70-73"
216:     first_seen_round: 1
217:     resolved_round: ""
218:   - id: F003-D014
219:     title: "F003 声称 F007 消费其事件/算子登记表，F007 未声明 F003 上游"
220:     seve
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

  <details><summary>tool output</summary>

  ```text
6b73c35 (HEAD -> main) fix(f007): D009 T022 拆出执行机真实环境独立证据与集成命令
a0896fa fix(f007): D008 补 T007->T010/T011 与 T012/T014->T016 依赖边
26c7b6d fix(f007): D007 补 T009->T012 与 T012->T013 依赖边
36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）
59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断
b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用
5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点
ccf577d fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:32:32Z

- **tool**: `bash({"command": "git rev-parse --short HEAD && git status --short && git diff --stat && git diff -- docs/features/0.2/F007-evaluation-gates/spec.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] **Rebaselining to current HEAD commit**

> [reasoning] **Assessing F007 and F003 contract compatibility**

> [reasoning] **Identifying cross-feature contract gap**

> [reasoning] **Assessing partial resolution of F003-D013 finding**

> [reasoning] **Confirming carried high-priority lifecycle finding**

> [reasoning] **Clarifying F007 registry ownership scope**

> [reasoning] **Reviewing F007-F008-F003 spec differences**
基线再次发生漂移：当前 HEAD 已到 `6b73c35`（在先前 `b251826` 之后的 F007 修复链），且 F007 `spec.md` 仍有未提交修改。以下以 `main@6b73c35` 为最终复核基线；已完成的证据显示 F007 的 F003/F008 声明已补齐，但 F003↔F008 的过渡绑定与 F004 生命周期接口仍需单独判定。

  <details><summary>tool output</summary>

  ```text
7fec73c


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:19Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件", "status": "completed", "priority": "high"}, {"content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据", "status": "completed", "priority": "high"}, {"content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict", "status": "completed", "priority": "high"}]})`


> [reasoning] **Confirming final commit state**

> [reasoning] **Preparing final Chinese lines**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与审查范围：确认分支、HEAD、工作树及 F003 Round 2 变更边界 - 明确只检查相邻契约且不修改文件",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "跨特性契约核对：检查 F007/F008/F004、architecture、PRD、ADR 与 F003 消费关系 - 形成逐项证据",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "输出复核结论：区分通过、携带发现与新发现并给出精确 file:line - 完成紧凑中文 verdict",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T16:35:53Z


> [reasoning] **Summarizing final F007 and F008 findings**

> [reasoning] **Flagging F003-F007 cross-reference incompatibility**

> [reasoning] **Identifying expression mismatch with architecture fields**

> [reasoning] **Assessing DTO schema completeness**

> [reasoning] **Identifying registry lifecycle representation gap**
**结论：F003 Round 2 尚未完全收敛。**  
复核期间 HEAD 从用户给定的 `d659db7` 漂移到最终观测的 `main@7fec73c`；本次仅做只读检查，未修改文件。

### 已通过

1. **F007 已声明 F003 的主要消费契约：通过**
   - F003 事件、算子能力清单、协同池均已列为上游契约：[F007/spec.md:22-24](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:22)
   - design 明确只读摄入并按 `schema_version` 消费：[F007/design.md:25-26](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md:25)、[F007/design.md:66](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md:66)、[F007/design.md:175-180](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md:175)
   - tasks 已有对应实现载体：[F007/tasks.md:23-25](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md:23)、[F007/tasks.md:47-50](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md:47)

2. **F003 协同池与架构 FactorDef：主体契约一致**
   - 架构要求 pool 是可执行 `FactorDef`，`generator="pool"`，成员和权重进入定义，加载后可执行：[alphamill-architecture.md:254-274](/home/georg/projects/alphamill/docs/alphamill-architecture.md:254)
   - F003 已同步该语义：[F003/spec.md:232-247](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:232)、[F003/design.md:124](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:124)

3. **PRD/ADR 的 F003 主责要求大体已覆盖**
   - F003 明确引用并承接 PRD FR2.1/2.2/2.3/2.4/2.6 与 ADR-0001/0003/0007：[F003/spec.md:20-24](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:20)
   - ADR-0001 的两条 M2 冒烟义务已落到生成侧计数、下游占位和奖励频率抽查：[F003/spec.md:211-218](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:211)、[F003/tasks.md:47-55](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:47)
   - L0/L1/L2 时间边界也已与 ADR-0001 对齐：[F003/spec.md:278-281](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:278)

### 携带发现

1. **High：F003 过渡绑定仍未与 F008/F007 的拆分 artifact 契约完全对齐**
   - F008 实际提供的是按 digest 加载、支持 `universe_at(T)` 的 universe CSV artifact：[F008/spec.md:218-244](/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md:218)
   - F007 已明确 universe 与 calendar 是两个独立输入：[F007/spec.md:210-212](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:210)、[F007/spec.md:224-225](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:224)
   - 但 F003 的 `explicit_tuples` 仍使用单一 `universe_calendar_digest` 与 `universe_calendar_path`，没有分别表达 universe artifact 和 calendar artifact：[F003/design.md:118-121](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:118)
   - **影响**：F008 的 universe artifact 可以满足 PIT 查询，但不能单独满足 F003 过渡绑定声明的完整字段；后续切换到 F007 `ResearchSnapshot` 时仍存在字段/路径迁移歧义。

2. **High：F003 的 Kronos owner 合法，但 F004 没有提供对应的生命周期控制契约**
   - F003 已明确 live owner 为自身，且通过 F004 交付的服务编排停止/恢复 Kronos，失败时留在 FIFO：[F003/design.md:194-201](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:194)
   - F003 tasks 也声明了该跨 feature 依赖：[F003/tasks.md:101-105](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:101)
   - 但 F004 已完成的契约只覆盖 real profile、资产预检和推理服务；其范围外明确没有消费者路由切换：[F004/spec.md:59-72](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md:59)
   - F004 tasks 的后移项也没有定义供 F003 调用的 graceful stop/restore 接口：[F004/tasks.md:70-73](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md:70)
   - **裁决**：`owner=F003` 在职责划分上成立，但当前文档不能证明 F003 所依赖的 F004 控制面实际存在；原 F003-D013 只能视为部分修复。

3. **Medium：FactorDef schema 仍有字段形态歧义**
   - 架构 FactorDef 的规范字段包含 `params`、`compute`、`data_columns`、`meta`，未定义顶层 `expression`：[alphamill-architecture.md:258-269](/home/georg/projects/alphamill/docs/alphamill-architecture.md:258)
   - F003 design 的持久化字段列表却把 `expression` 列为顶层字段：[F003/design.md:105](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:105)
   - 同一设计后文又要求通过 `meta["expression"]` 恢复：[F003/design.md:107-110](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:107)
   - **影响**：pool 契约本身已对齐，但普通 AlphaGen FactorDef 的磁盘 DTO 到架构对象仍未明确“顶层 expression”是否只是 DTO 字段，还是会进入标准 FactorDef。

4. **Medium：PRD FR2.5 的注册表生命周期责任仍未闭合**
   - PRD 要求注册表保存评测摘要、生命周期，并执行高相关查重：[alphamill-prd.md:161-164](/home/georg/projects/alphamill/docs/alphamill-prd.md:161)
   - F003 将评测摘要、查重和生命周期回交给 F007/F006：[F003/spec.md:109-114](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:109)
   - 但 F007 当前范围只明确评测、ResearchSnapshot、cohort/population 和报告，没有明确承接 Factor Registry 生命周期/高相关查重的 owner：[F007/spec.md:101-113](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:101)
   - **裁决**：不是 F003 自身越权，但 PRD 要求的最终承接方仍未在跨 feature 契约中钉死。

**最终 verdict：**
- F007 承接 F003：**通过**
- F008 universe artifact 语义：**基础兼容，通过；过渡绑定字段未闭合**
- F003 Kronos owner：**职责合法；F004 控制接口缺失，携带 High finding**
- FactorDef/pool：**pool 通过；普通 FactorDef expression 形态有 Medium finding**
- PRD/ADR：**ADR-0001 与 F003 主责条款已覆盖；PRD FR2.5 注册表责任仍需明确**
- 收敛状态：**未通过，仍有 2 个 High、2 个 Medium 携带/新增发现**
