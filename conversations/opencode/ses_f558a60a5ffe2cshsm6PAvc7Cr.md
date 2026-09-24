---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f558a60a5ffe2cshsm6PAvc7Cr"
title: "Independent F003 reviewer pass (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T13:43:50Z"
updated_at: "2026-09-16T13:50:42Z"
tokens_input: 156319
tokens_output: 5358
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Independent F003 reviewer pass (@Sisyphus-Junior subagent)

## user · 2026-09-16T13:43:50Z

TASK: Independently review the completed F003 requirements/design package from a skeptical implementation-reviewer perspective. EXPECTED OUTCOME: Evidence-backed issues that other lanes may miss, focused on implementability, falsifiable acceptance, failure states, security claims, machine-boundary evidence, and hidden work/dependencies. REQUIRED TOOLS: Read-only repository inspection. MUST DO: Read project CLAUDE/SOP/features README and all F003 spec/design/tasks; compare with prior retrospective patterns; cite exact file:line; classify severity and identify whether Critical/High blocks ready-for-development. Specifically inspect contradictions between claims and task carriers, acceptance tests that cannot prove the claimed behavior, and deferred work without an owner/closure condition. MUST NOT DO: No edits, no files, no code review, no unsupported stylistic suggestions. CONTEXT: /home/georg/projects/alphamill, baseline main@a333394 clean, Round 1 full-scan under review-convergence. Output in Chinese.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T13:43:50Z

- **tool**: `skill({"name": "review-convergence", "user_message": "独立审查已完成的 F003 需求/设计包；只读；Round 1 full-scan；中文输出；重点检查可实现性、可证伪验收、失败态、安全声明、机器边界证据、隐藏依赖/工作。"})`


> [reasoning] **Planning doc review and verification**
先固定基线并建立有限检查清单；本轮只读文档，按 `main@a333394` 做 Round 1 全量审查，Critical/High 作为 ready-for-development 阻塞项。

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

## assistant · 2026-09-16T13:44:09Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确", "status": "in_progress", "priority": "high"}, {"content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作", "status": "pending", "priority": "high"}, {"content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据", "status": "pending", "priority": "high"}, {"content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line
…[truncated])`

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line 与修复方向",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:20Z

- **tool**: `bash({"command": "git branch --show-current && git rev-parse --short HEAD && git status --short", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/{CLAUDE.md,AGENTS.md,SOP*.md,*SOP*.md,README.md}"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/*F003*"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "docs/features/**"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/RETROSPECTIVE.md"})`


> [reasoning] **Starting file inspection with glob search**

  <details><summary>tool output</summary>

  ```text
main
a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 10 file(s)

/home/georg/projects/alphamill/docs/design/ui-mockup/README.md
/home/georg/projects/alphamill/docs/README.md
/home/georg/projects/alphamill/README.md
/home/georg/projects/alphamill/CLAUDE.md
/home/georg/projects/alphamill/conversations/README.md
/home/georg/projects/alphamill/docs/SOP.md
/home/georg/projects/alphamill/docs/features/0.1/README.md
/home/georg/projects/alphamill/docs/features/releases/README.md
/home/georg/projects/alphamill/docs/features/README.md
/home/georg/projects/alphamill/AGENTS.md
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", l
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
Found 26 file(s)

/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md
/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md
/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/spec.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md
/home/georg/projects/alphamill/docs/features/0.2
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md
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
- Sp
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:44:32Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/AGENTS.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/README.md"})`


> [reasoning] **Planning parallel documentation reading**
基线已核对：`main@a333394`，工作树为空，和用户给定基线一致。接下来提取项目级门禁与文档状态机，重点确认“完成/可开发”在本仓库要求哪些可机检证据。

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
<path>/home/georg/projects/alphamill/AGENTS.md</path>
<type>file</type>
<content>
1: # AlphaMill
2: 
3: 见 `CLAUDE.md`（项目说明与开发约定，对所有 AI 编码工具通用）。

(End of file - total 3 lines)
</content>

[Project README: /home/georg/projects/alphamill/README.md]
# AlphaMill（淘沙）

> 以 AI 因子工厂为核心的加密量化研究与交易管线。

AlphaMill 将数据治理、假设生成、因子评测、严格验证、组合构建、交易执行和绩效复盘连接为
可复现的闭环，目标是持续发现并运营成本后有效的 Alpha。候选吞吐量只是漏斗分母与能力
标定，不是项目目的；有效独立性、证据可信度、组合边际贡献和线上表现共同决定研究产出是否有价值。

## 核心闭环

```text
数据快照 → AI 因子工厂 → 证据评测与验证 → 组合与策略 → Freqtrade 执行
    ▲                                                      │
    └──────── 新假设 ← AI/人工复盘 ← 监控、归因与生命周期 ──┘
```

- **AI 负责探索**：生成假设和因子、分析失败、提出下一轮实验。
- **规则负责证据**：成本、多重检验、留出预算、最终确认和无前视审计均由确定性代码裁决。
- **组合负责转化**：单因子和协同池 meta-factor 只有对现有组合产生正边际贡献才构成可信产出。
- **执行负责反馈**：Freqtrade 承担 dry-run/paper/live 路径，成交
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
<path>/home/georg/projects/alphamill/docs/features/README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [features, spec-driven-development, docs]
3: doc_kind: guide
4: created: 2026-09-06
5: updated: 2026-09-07
6: ---
7: 
8: # Feature Specs Guide
9: 
10: 本目录记录 AlphaMill 的 feature-level SDD artifacts。所有需求按「一 feature 一
11: 文件夹」输出，feature 文件夹按 PRD 的大版本（`0.1`、`0.2`…）分层存放。
12: 
13: ## Directory Shape
14: 
15: ```text
16: docs/features/
17:   README.md                   本文：规则与入口
18:   TEMPLATE/
19:     spec.md                   feature 行为契约模板（状态唯一真源）
20:     design.md                 技术设计模板
21:     tasks.md                  实施 checklist 模板
22:   releases/
23:     <version>.md              版本发布与收口摘要（全部 done 后创建）
24:   <version>/                  例如 0.1/
25:     Fxxx-feature-name/
26:   
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [docs, index, ownership]
3: doc_kind: guide
4: created: 2026-09-06
5: updated: 2026-09-15
6: ---
7: 
8: # AlphaMill 文档地图
9: 
10: 本文件是仓库文档的**唯一入口与所有权索引**：从一个入口最多两次点击即可到达任何
11: 权威文档。它只记录所有权和链接，**不复制正文**。产品、架构、数据模型、Feature 状态
12: 和流程各有且只有一个机器可读拥有者。
13: 
14: ## 权威文档所有权矩阵
15: 
16: | 信息 | 唯一拥有者 | 说明 |
17: |---|---|---|
18: | 产品目标、范围和路线 | `alphamill-prd.md` | 产品真相源（指标体系 / G1-G7 / FR1-FR8 / 里程碑 M0-M4） |
19: | 全局模块、进程与运行时边界 | `alphamill-architecture.md` | AI 控制面 + 证据与治理面 + 策略与执行面 + 数据面 + 闭环主循环 |
20: | 字段、表、数据契约（HypothesisDef / FactorDef / PortfolioDef / 评测台 / 信号缓存 / manifest） | `alphamill-architecture.md` §四 | 接口契约真源 |
21: | 因子挖掘主引擎选型（含降级阶梯） | `decisions/0001-factor-mining-engine.md` | 选型决策（证据：`
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:44:43Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确", "status": "completed", "priority": "high"}, {"content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作", "status": "in_progress", "priority": "high"}, {"content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据", "status": "pending", "priority": "high"}, {"content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:li
…[truncated])`


> [reasoning] **Updating second todo and planning parallel reads**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line 与修复方向",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:52Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`

审查门槛已固定：状态推进前必须关闭问题、任务可追踪；真实集成/GPU 证据必须在执行机取，开发机 skip 不构成证据。现在逐项建立 F003 的“声明 → AC → 测试 → task → 机器/依赖”映射。

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

## assistant · 2026-09-16T13:45:01Z

- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/decisions", "include": "0001*.md", "pattern": "time-box|PPO|L1|L2|50|IC|工作日|切换|回切", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates", "include": "*.md", "pattern": "F003|research_snapshot_id|ResearchSnapshot|explicit|过渡|GenerationRun|operator", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion", "include": "*.md", "pattern": "F003|30|50|阻塞|依赖|完成|验收", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime", "include": "*.md", "pattern": "status:|卸载|F003|GPU|夜槽|Kronos", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs", "include": "alphamill-architecture.md", "pattern": "7\\.1|22:00|06:30|GPU|Kronos|F003|FIFO|卸载", "output_mode": "content", "head_limit": 100})`


> [reasoning] **Identifying high blockers and design contradictions**

> [reasoning] **Highlighting critical design and security inconsistencies**

> [reasoning] **Assessing incomplete results from early termination**

> [reasoning] **Analyzing GPU queue and FIFO behavior**

> [reasoning] **Investigating F004 and related spec statuses**

> [reasoning] **Planning targeted grep for references**

> [reasoning] **Identifying test coverage gaps and limitations**

> [reasoning] **Analyzing vendor baseline test limitations**

> [reasoning] **Evaluating vendor code licensing risks**

> [reasoning] **Identifying unlicensed code blocking risk**

> [reasoning] **Analyzing hidden dependency contradictions**

> [reasoning] **Inspecting F007 task ownership**
首轮映射已经暴露出几处结构性冲突：可复现身份、time-box、执行机调度与安全边界的“声明强度”高于现有任务/测试能证明的强度。下一步只核对这些跨 Feature 所有权与上游判据，避免把已有载体误报成隐藏工作。

  <details><summary>tool output</summary>

  ```text
Found 23 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md
  14: - **AlphaGen**（ICT-FinD-Lab/alphagen，原 RL-MLDM，1.2k★）：RL 表达式生成 + 线性协同池；
  15: 核心优势是代码冻结带不走的——协同池（增量 IC reward，机制性防冗余）+ GPU 张量评估（吞吐）+ 量化原生算子。
  16: 已知问题：无 LICENSE（个人私有使用，风险可忽略）；核心 21 个月未实质更新；
  28: 2. **冒烟即闸门（time-box 2 个工作日）**：第 1 天 vendor+现代栈跑通 1 个 PPO epoch；第 2 天产出
  29: 因子做 RankIC 对齐。通过 → 锁定；超时/坑深 → 降级，不沉没成本。
  30: 3. **降级阶梯**：L1 = AlphaGen 表达式求值器 + 自写搜索（绕开 sb3/RL，保留 GPU 批量评估）；
  31: L2 = 纯 gplearn（1h/4h 重采样 + 自建算子 + 滚动 fitness）。
  34: ## 降级切换判据
  36: 冒烟闸门 time-box 已定（2 个工作日），但"何时降级"此前未成文——单人 time-box 最容易
  37: 自我豁免。以下判据预写为**二元可测项**：到期未达标即切换，不允许"再给一天"；切换动作
  38: 与触发原因记入当日 experiment manifest。降级不自动回切，回切须重开一轮冒烟 time-box。
  40: **切到 L1（AlphaGen 表达式求值器 + 自写搜索，绕开 sb3/RL）**——满足任一条
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 21 match(es) in 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md
  45: ├─ ResearchSnapshotBuilder ── F002 ManifestReader
  81: "research_snapshot_id": "snapshot_sha256:...",
  90: 规则/窗口/成本配置、research_snapshot_id、code/build digest 与 seed。`execution_tier` 由物理根目录
  100: ├── bench/<object_id>/<research_snapshot_id>/<experiment_id>/{manifest.json,report.json,curves.parquet,events.jsonl,registration.json}
  158: `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`，再发布 ResearchSnapshot 并显示
  160: `canonical` 缺 cohort、code digest、ResearchSnapshot 或规则版本时
  193: 1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围和不可变 symbol-map artifact，并把显式 universe/calendar JSON 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 65 match(es) in 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md
  5: related_features: [F001, F002, F003, F007]
  17: > 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
  26: - Python 3.11+，`src/alphamill/data_bridge/` 下扩子包；350 行硬上限、ruff（`E,F,I,B,UP,SIM`）；
  35: 四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。发现从 Binance 公开行情按口径筛候选；人工确认后冻结为内容寻址的 `UniverseDef`；回填复用 F001 的 `historical_backfill.py`，外面套一层可续跑的批次编排；每个 pair 回填完成后跑质量门（复用 `tools/f001_backfill_report.py` 的口径，参数化到多 pair）；过门的 pair 写入联机库的 `universe_membership` 台账并进 F002 导出清单，台账再以 `symbol_map` 同构的方式发布为湖内内容寻址 artifact。
  38: - 后端 / API：新增 `src/alphamill/data_bridge/universe/` 子包与 `alphamill-universe` CLI；`collector/historical_backfill.py` 由脚本升级为可被编排调用（同时解除其 350 行豁免）
  63: | universe → F002 核心 | 单向依赖：`universe
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 34 match(es) in 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md
  12: # F004：Kronos 真实推理运行时 - 设计
  19: - **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动
  20: - **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）
  21: - **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物，DB 已迁移）
  39: | 挂载 | `../vendor/Kronos:/app/vendor/Kronos:ro`；`../models:/app/models:ro` |
  40: | KRONOS_REPO_PATH | `/app/vendor/Kronos` |
  41: | KRONOS_M
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 21 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  77: GEN["生成器组<br/>AlphaGen · GP/表达式 · manual/LLM · Kronos"]
  227: ├── kronos_service/          # Kronos 推理服务薄壳（自 quant-crypto 迁入）
  274: FactorDef 同时承载单 pair 时序和多 pair 横截面契约；主引擎 AlphaGen 使用表达式树与 GPU 张量。
  333: experiment manifest（FR7.1）。
  476: | `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` | **泛化为统一评测台**（FR3.1），Kronos 信号作为第一批入库因子 |
  481: | Kronos 信号服务 + 缓存 | 薄壳迁入 `src/alphamill/kronos_service/`；模型代码上游 clone + pin |
  517: MINE[生成器挖掘<br/>GPU 夜槽 §7.1]
  524: KRN[Kronos 推理服务<br/>GPU 常驻]
  526: subgraph DEV["开发机 qiaozhi-gp/gp-wsl（AMD iGPU，无 NVIDIA）"]
  546: 产出，研究控制台先行，ADR-0005；Grafana 逐步退守平台观测与告警）。GPU 占用按时段表调度（见 7.1）。
  548: ### 7.1 机器边界与单卡 GPU 时段调度
  552: | 角色 | 主机 | 平台与 GPU | 职责 |
  554
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:45:57Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md", "offset": 24, "limit": 50})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 548, "limit": 36})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "offset": 16, "limit": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md", "offset": 18, "limit": 75})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "offset": 20, "limit": 58})`


> [reasoning] **Identifying missing GPU unload ownership**

> [reasoning] **Analyzing GPU and dependency mismatches**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md</path>
<type>file</type>
<content>
24: 1. **主引擎 = AlphaGen，vendor 方式接入**（非安装）：核心子集（expression / tensor calculator /
25:    LinearAlphaPool）进 `factor_factory/generators/alphagen_vendor/`；丢弃其 requirements.txt，
26:    自定现代栈（torch 2.x / numpy 2.x / pandas 2.x / sb3 最新+gymnasium）；自写 feather→tensor
27:    数据适配器替代 `alphagen_qlib`（qib 依赖连同装错包问题一起消失）。
28: 2. **冒烟即闸门（time-box 2 个工作日）**：第 1 天 vendor+现代栈跑通 1 个 PPO epoch；第 2 天产出
29:    因子做 RankIC 对齐。通过 → 锁定；超时/坑深 → 降级，不沉没成本。
30: 3. **降级阶梯**：L1 = AlphaGen 表达式求值器 + 自写搜索（绕开 sb3/RL，保留 GPU 批量评估）；
31:    L2 = 纯 gplearn（1h/4h 重采样 + 自建算子 + 滚动 fitness）。
32: 4. **对照基线**：AlphaGen 仓库自带的 gplearn/ 与 dso/ 直接利用，不单独引入 gplearn 项目。
33: 
34: ## 降级切换判据
35: 
36: 冒烟闸门 time-box 已定（2 个工作日），但"何时降级"
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
548: ### 7.1 机器边界与单卡 GPU 时段调度
549: 
550: **两类机器，职责不重叠**（事实源：env-manager `data/fleet.json`）：
551: 
552: | 角色 | 主机 | 平台与 GPU | 职责 |
553: |---|---|---|---|
554: | 开发机 | `qiaozhi-gp` / `gp-wsl` | Legion Go，AMD Ryzen Z2 + Radeon 780M iGPU（**无 NVIDIA**），Win11 + WSL2 Ubuntu 26.04 | 编码、单元测试、`python3 tools/verify.py` 门禁；不承载 GPU 负载，不作为集成/性能证据来源 |
555: | 执行机（当前） | `qiaozhi-lt` | Windows 11 笔记本 + WSL2，RTX 4060 Laptop 8GB | 全部联机运营与批处理：TimescaleDB + 采集 + 导出 + Parquet 湖 + dry-run + 监控 + Kronos 常驻 + 挖掘训练 + 评测门禁 |
556: | 执行机（最终） | `qiaozhi-lab` | **原生 Ubuntu 26.04**（与 Windows 侧 `qiaozhi-ws` 双系统互斥），Intel Ultra 7 265K 20 核 / 45GB RAM / 1.1TB `/data`，RTX 5070 Ti 16GB（Blackwell sm_120），CUDA 13.1/13.2 | 迁移完成后接
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`。
19: - 技术方案与边界：`design.md`。
20: - 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。
21: - canonical writer、留出访问、统计失败语义与 artifact 发布属于高风险路径，必须变异验证。
22: 
23: ## 1. 前置条件
24: 
25: - [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot builder/reader contract；builder 只接收显式 universe/calendar artifact，验证其内容摘要并在 provenance 保留不可变引用；preview latest 必须先冻结，canonical 只收 snapshot ID — verify: `tests/contract/test_f007_upstream_contracts.py`、`tests/unit/experiment_store/test_research_snapshot.py`
26: - [ ] T002 (`FR-004`, `FR-005`): 预注册 v1 方法/阈值/cohort schema 与两个正控制、白噪声、泄漏负
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md</path>
<type>file</type>
<content>
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
20: - `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
21: - 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
22: - **机器边界**（架构 §7.1、`docs/SOP.md` §3）：回填、质量门、导出、备份在执行机 `qiaozhi-lt` 执行并记 hostname；开发机 `qiaozhi-gp` 只跑单元与契约测试。
23: - **不动 `F002` 已冻结语义**：导出/对账/manifest/修订规则一律沿用，本 feature 只扩 pair 集合并新增元数据 artifact。
24: - 回填是 1~2 周 wall-clock 的 owner 主导长跑；它**不阻塞**除产能对照外的任何一项，开发与测试用 fixture 推进。
25: 
26: ## 1. 前置条件
27: 
28: - [ ] T001 (`FR-001`, `DR-001`): 把 Q-001 的裁决值落成可复核的口径文件（`turnover_lookback_days=90`、`turnover_rank_top_n=40`、`min_listed_days=180`、排除规则），作为 `discover` 的输入 — verif
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
20: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
21: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
22: - 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。
23: - 实现任务遵循先红后绿：任务内的契约测试必须先失败（复现缺口）再随实现转绿，不得先实现后补测试。
24: 
25: ## 1. 前置条件
26: 
27: - F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态实测证据；回填数据满足目标 exchange/symbol ≥30 根已闭合 1m K 线。
28: - spec §8 Q-001 已关闭（F004 不阻塞 F002 done）；design §10 待确认设计问题为空，无阻塞性设计问题。
29: 
30: ## 2. 实现任务
31: 
32: ### Phase 1：薄壳运行时改造
33: 
34: - [x] T001 (`FR-001`): 先红后绿——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）；实现 `kronos_real
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:46:20Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确", "status": "completed", "priority": "high"}, {"content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作", "status": "completed", "priority": "high"}, {"content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据", "status": "in_progress", "priority": "high"}, {"content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:
…[truncated])`


> [reasoning] **Investigating ADR and F003 test discrepancies**

> [reasoning] **Analyzing timing and scope contradictions in tests**

> [reasoning] **Inspecting missing test group precondition**

> [reasoning] **Prioritizing top five critical project issues**

> [reasoning] **Compiling five high-priority nuanced issues**

> [reasoning] **Planning concise findings structure**

> [reasoning] **Prioritizing impactful acceptance evidence**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line 与修复方向",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:46:56Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md"})`

F003 全量与跨 Feature 载体已核完。最关键的不是缺少实现细节，而是若干验收会“绿但不能证明主张”：尤其二日闸门、跨 run 身份、安全隔离、vendor 差异检测和 GPU 交接。现在用历史复盘确认这些是否是项目已知复发模式。

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md</path>
<type>file</type>
<content>
1: # RETROSPECTIVE —— 检视复盘
2: 
3: 本文件由 review-convergence skill 维护，记录每轮检视发现的缺陷与过程教训。
4: `docs/reviews/` 下其它文件本地-only（见 `.gitignore`）。
5: 
6: ## 循环 1：全项目文档检视（项目开工前全量）
7: 
8: - report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
9: - 日期：2026-09-07 | 基线：1bd8c4d → 终基线 7969a97（修复轮 7 个分批提交）
10: - 检视人：Sisyphus；修复方：项目所有者（Georg/qiaozhi li）
11: - 范围：docs/ 全部 17 份入库文件 + CLAUDE.md/README.md/BACKLOG.md + 三路独立取证（检视人通读 + explore agent 代码区实测 + Oracle agent 战略评审）
12: - 结论：首轮 2 Critical / 8 High / 10 Medium / 4 Low 共 24 条；修复轮全数处理并自查发现 fix-regression N1 一条（PRD 与架构成本口径矛盾，当轮修复）；round-2 diff-only 复核逐条验证通过，verify.py 六步全绿 ×3，检视人独立变异验证两道新门禁（死链注入→红→还原→绿；pin 复现 C001 原始故障→红→还原→绿）。
13: 
14: | ID | 一
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:47:06Z

- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/decisions", "include": "0002*.md", "pattern": "vendor|VENDORED|标注|diff|LICENSE|许可|卫生", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-integration.md", "pattern": "vendor|VENDORED|标注|diff|LICENSE|许可|卫生", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md", "pattern": "hidden-workstream-no-owner|gate-without-teeth|gate-measures-itself|test-simulates-itself|environment-contract-drift|spec-tasks-traceability-gap|cross-doc-contract-drift", "output_mode": "content"})`


> [reasoning] **Comparing specific code lines**

  <details><summary>tool output</summary>

  ```text
Found 7 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md
  1: # ADR-0002：外部依赖管理策略 —— vendor / fork / 原样依赖三分法
  20: | AlphaGen | **vendor** 进主仓 | 动大手术（换数据层/现代化）+ 上游冻结 + 只用子集 |
  28: vendor 卫生规则（AlphaGen 专用）：
  30: 1. vendor 目录内最小 diff，贴近上游原貌，每处修改标注 `# [alphamill] <原因>`；
  31: 2. 胶水代码（feather→tensor 适配器、FactorDef 包装）放 vendor 外，保持可整体替换；
  32: 3. `alphagen_vendor/VENDORED.md` 记录上游 repo + commit hash、vendor 日期、修改清单、许可说明；
  42: - 负面：AlphaGen 放弃上游更新（冻结代码 vendor 后由本项目全权维护）；Freqtrade/Vibe-Trading
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 10 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-integration.md
  26: | 质量继承 | `ohlcv_quality_flags` 未解决标记 > 0 的分区在 manifest 里标注，评测台可选跳过 |
  104: 差异报告：两者收益曲线/成交列表 diff，逐笔归因（数据差异 / 撮合假设差异 / 信号时间戳差异）
  194: ## 五、外部依赖管理策略（vendor / fork / 原样依赖）
  196: > 判断原则：**改动深度决定集成距离**。要动大手术的 vendor 进主仓；只用扩展面的原样依赖；fork 仅适用于"要上游全部 + 必须改核心 + 上游不收 PR"的窄缝——本项目三个引入项没有一个落在缝里，**一律不 fork**。
  200: | **AlphaGen** | **vendor** 进 `src/alphamill/factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md`；不考虑跟随上游 |
  205: ### vendor 卫生规则（AlphaGen 专用）
  207: 1. vendor 目录内**最小 diff**：贴近上游原貌，每处修改标注 `# [alphamill] <原因>`；
  208: 2. 胶水代码（feather→tensor 适配器、FactorDef 包装）放 vendor **外面**（`generators/` 本
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 35 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md
  22: | D007 | 回填（~4600 万行）无估算无归属 | 高 | 正确性 | 症状 | 原始设计 | fixed | FR1.3 显式工作流（1-2 周 wall-clock、归属所有者）；M1 改"1 周开发+1~2 周回填并行" | — | 1 | 1 | hidden-workstream-no-owner |
  86: | D034 | SC-003 要求 §一 9 项全勾，tasks 缺 item 5（评测/门禁脚本）与 item 8（宇宙发现）任务；spec 范围内枚举漏 item 5 | 高 | 正确性 | 根因 | 原始设计 | fixed | tasks 补 T012/T013（原样迁移+import 冒烟，泛化留 M1）；spec 枚举补 item 5 | validate_spec_lifecycle + verify | 1 | 1 | spec-tasks-traceability-gap |
  87: | D035 | 环境契约漂移：文档假设 Windows 11+Docker Desktop+RTX 4060，实况 WSL2+docker-ce、无 pwsh、GPU 不可见、旧仓本机不可见——T002/AC-002/AC-005 按字面不可执行 | 高 | 正确性 | 根因 | 原始设计 | fixed | design §0 执行环境实测钉死（WSL2/docker-ce 29.1.3/Ubuntu 26.04）；pwsh=apt 安装；GPU=T003 前置直通检查+CPU 回退；旧仓=T001 定位钉死；spec 依赖+NFR-002+
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:47:22Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md", "offset": 430, "limit": 60})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md", "offset": 230, "limit": 90})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md", "offset": 20, "limit": 30})`


> [reasoning] **Planning targeted log rereading**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md</path>
<type>file</type>
<content>
430: | F004-D005 | real 镜像依赖清单漏掉上游直接依赖 | High | 正确性 | 根因 | 规格漂移 | fixed | 补齐 `huggingface_hub`、`tqdm` 并锁定 CPU wheel 来源 | 锁定已验证的 torch CPU wheel 与四项最小推理依赖版本 | 文档生命周期 + 链接门 | 1 | 2 | upstream-dependency-drift |
431: | F004-D006 | 验收环境违反执行机取证纪律 | High | 正确性 | 根因 | 规格漂移 | fixed | 指定执行机及 hostname/device 证据要求 | 指定 qiaozhi-lt 执行集成并记录 hostname/device，开发机只跑静态和单元门 | 文档生命周期 + 链接门 | 1 | 2 | wrong-evidence-machine |
432: | F004-D007 | NFR-001 的构建隔离机制与判据未定义 | Medium | 测试覆盖 | 根因 | 初始设计 | fixed | 固定 target 并改用稳定可断言判据 | 固定 mock/real target，判据改为默认镜像无 torch 且不启用或构建 real | 文档生命周期 + 链接门 | 1 | 2 | unverifiable-nonfunctional-requirement |
433: | F004-D008 | 资产挂载契约缺 tokenizer 路径与只读约束 | Medium | 正确性 | 根因 | 初始设计 | 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md</path>
<type>file</type>
<content>
230: - 收尾轮（2026-09-12，owner 要求「跑一下真实推理并处理掉那两个问题」）：① **AC-006 真实推理实跑通过**——既有 :8002 实例 3 passed（BTC/USDT，source=kronos，Kronos-base，256 行上下文，CPU 单次 7.2s）；另按 spec 文档命令从零起 :8003 复现，同样 3 passed（ETH/USDT，CPU 单次 3.4s）。② 实跑过程中发现 **C501**——我上一轮写进 spec 的那条 AC-006 命令**自己没跑过**，缺 DB 环境导致 /health 500；这是「文档化的命令从未被执行」的典型，已修并配契约测试。③ C402/C403 一并关闭，不再转 F002。三道新门禁各做一次变异验证。
231: - 模式教训补记 #22 **documented-command-never-run**：把一条命令写进规格并不等于验证过它。C501 的根因是我在拆分 AC-002 时凭既有实例的行为推断命令形态，而那个实例带着 DB_HOST 覆盖启动。**凡是写进验收文档的命令，必须在干净环境里从零跑一遍**——这一轮的证据正是：同一条命令，在既有实例上"验证通过"，从零执行却直接 500。
232: 
233: ## 循环 7：F002 数据桥需求设计检视
234: 
235: - report_type: doc-review | round: 1（full-scan）→ 2（修复覆盖 >30%，一次性 full-scan）→ 3（diff-only 封顶与 owner
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md</path>
<type>file</type>
<content>
20: | AlphaGen | **vendor** 进主仓 | 动大手术（换数据层/现代化）+ 上游冻结 + 只用子集 |
21: | Freqtrade | 原样依赖（官方 docker 镜像 + `user_data/` 插件层） | 零源码改动；pin 镜像 tag；上游 bug 走 issue + monkey-patch 过渡 |
22: | Vibe-Trading | 可选原样依赖（pip pin + 本机 CLI/服务） | 只碰只读配置层接入面；1 周 time-box，可弃置，不阻塞主链路 |
23: | Kronos 模型代码 | 原样依赖（上游 fresh clone + pin commit） | 零改动；权重走 HuggingFace；服务薄壳为本仓 `kronos_service/` |
24: | 前端构建期工具链（Node/npm，`web/` SPA） | 原样依赖（**仅构建期**，pin lockfile） | 生产运行时零新增（构建产物静态托管）；`package-lock.json` 入库、pin Node 主版本；仅在里程碑边界升级（ADR-0005 决策 4/7） |
25: 
26: **永不 fork。**
27: 
28: vendor 卫生规则（AlphaGen 专用）：
29: 
30: 1. vendor 目录内最小 diff，贴近上游原貌，每处修改标注 `# [alphamill] <原因>`；
31: 2. 胶水代码（feather→tensor 适配器、Factor
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:47:35Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md", "offset": 46, "limit": 40})`


> [reasoning] **Planning final git status checks**

> [reasoning] **Synthesizing findings and test absence**

> [reasoning] **Documenting scheduling conflicts and test block**

> [reasoning] **Assessing factor_id and run_seq consistency**

> [reasoning] **Identifying gaps in vendor hygiene testing**

> [reasoning] **Separating license issues from vendor provenance task**

> [reasoning] **Analyzing unload and transition inconsistencies**

> [reasoning] **Identifying missing task closure gates and owners**

> [reasoning] **Documenting CLI day parameter and test simulation**

> [reasoning] **Evaluating failure state impact on results**

> [reasoning] **Consolidating failure state and reproducibility findings**

> [reasoning] **Refining final five key findings**

> [reasoning] **Planning integration of historical comparisons**

> [reasoning] **Mapping line references and ordering findings**

> [reasoning] **Planning incremental completion and baseline check**

> [reasoning] **Identifying ADR and FR006 contradiction**

> [reasoning] **Highlighting run_seq and lifecycle inconsistencies**

> [reasoning] **Noting missing explicit [TEST] group**

> [reasoning] **Verifying feature ownership for unload**

> [reasoning] **Reading remaining F007 task lines**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
46: 
47: ### Phase 3：综合、控制与契约交付
48: 
49: - [ ] T014 (`FR-006`, `AC-007`): 实现只消费 canonical 的 synthesis builder 与五阶段/三维失败汇总 — verify: `tests/integration/test_f007_synthesis.py`
50: - [ ] T015 (`FR-006`, `UX-002`, `AC-005`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推 — verify: `tests/contract/test_f007_artifact_schemas.py`
51: - [ ] T016 (`FR-003`, `FR-004`, `FR-005`, `AC-003`): 跑正控制、白噪声与故意泄漏 golden，全链记录拒绝者 — verify: `tests/integration/test_f007_controls.py`
52: - [ ] T017 (`FR-001`, `FR-002`, `NFR-003`): 对 future-fill、embargo、guard 注册、preview writer、异常吞噬与 publish 完整性运行定向变异 — verify: `tests/mutation/test_f007_gate_mutations.py`
53: 
54: ## 3. 验证与验收任务
55: 
56: - [ ]
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:48:47Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确", "status": "completed", "priority": "high"}, {"content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作", "status": "completed", "priority": "high"}, {"content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据", "status": "completed", "priority": "high"}, {"content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:li
…[truncated])`


> [reasoning] **Clarifying task dependency ambiguities**

> [reasoning] **Reviewing test group validation approach**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line 与修复方向",
    "status": "in_progress",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:49:04Z

- **tool**: `bash({"command": "git branch --show-current && git rev-parse --short HEAD && git status --short", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Performing final git check**
历史对照完成：本轮 5 个阻塞点分别复现了 `cross-doc-contract-drift`、`gate-without-teeth`、`spec-tasks-traceability-gap`、`deferred-work-without-carrier` 与 `environment-contract-drift`。我正在做只读基线复核并整理最终严重度；没有文件改动，因此 LSP/build 不适用。

  <details><summary>tool output</summary>

  ```text
main
a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:49:24Z

- **tool**: `todowrite({"todos": [{"content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确", "status": "completed", "priority": "high"}, {"content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作", "status": "completed", "priority": "high"}, {"content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据", "status": "completed", "priority": "high"}, {"content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:li
…[truncated])`


> [reasoning] **Marking conclusion complete**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "仓库基线与规范文件：核对分支/HEAD/清洁状态并读取 CLAUDE、SOP、features README 以固定审查门槛 - expect 基线与项目硬约束明确",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 规格包：逐行读取 spec/design/tasks 及关联文档并建立声明到任务/验收/依赖映射 - expect 找出矛盾、不可证伪验收和无载体工作",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "历史复盘：读取 RETROSPECTIVE 并将既有失效模式对照 F003 - expect 每个复现模式有历史证据",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "审查结论：按严重度汇总证据并判定 ready-for-development 阻塞状态 - expect 中文 findings 含精确 file:line 与修复方向",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:49:36Z


> [reasoning] **Planning concise evidence-backed findings**

> [reasoning] **Detailing high-priority test and security findings**

> [reasoning] **Designing concise numbered list format**
**审查发现**
1. **High｜二日闸门与 ADR-0001 不可同时实现，且测试可伪造“到期”**
   
   F003 承诺两日内裁决至 L1/L2（[spec.md:43](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:43)、[spec.md:213](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:213)），但 ADR 规定两日闸门只能触发 L1；L2 必须观察 L1 连续两周并依赖评测台与无前视审计（[ADR-0001:40](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:40)、[ADR-0001:47](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:47)）。ADR 还要求冒烟首日起完整漏斗记账和奖励频率抽查（[ADR-0001:54](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:54)），F003 却排除 F007，并把目标对齐安排在裁决任务之后（[tasks.md:55](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:55)、[tasks.md:63](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:63)）。此外 `smoke --day {1,2}` 由调用者指定，没有权威开始时间、工作日算法或不可重置时钟（[design.md:152](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:152)），测试可以构造“第 2 天”而无法证明真的到期。
   
   **阻塞修复标准**：两日裁决限定为 L0/L1；L2 建立两周且由 F007 数据驱动的独立载体；补不可重置的 time-box 身份与到期否证测试。

2. **High｜`factor_id` 设计直接破坏跨运行可复现验收**
   
   设计将 `run_seq` 编入 `factor_id`，同时说明不同 run 只会得到相同 digest（[design.md:104](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:104)、[design.md:105](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:105)）。但 NFR、AC 和 T028 都要求重跑得到相同 `factor_id` 集合（[spec.md:259](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:259)、[spec.md:305](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:305)、[tasks.md:70](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:70)）。除非测试固定或伪造 `run_seq`，该 AC 必然失败。
   
   **阻塞修复标准**：明确稳定身份是内容寻址 `factor_id`，或把验收改为只要求 `definition_digest` 稳定；不能同时保留两种定义。

3. **High｜SIGTERM 把不完整运行标成 `COMPLETED`，下游会误收部分结果**
   
   spec 定义 `COMPLETED` 为候选集与 manifest 原子写出，异常则 `FAILED` 且候选不入册（[spec.md:269](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:269)）。设计却让 SIGTERM 导出已产候选和池并写 `status=completed, termination=early`（[design.md:190](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:190)）；完成事件又会被 F007 当作漏斗输入（[design.md:163](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:163)）。现有 AC/任务没有断言早停运行不得满足 ≥50 产能、不得产生普通 `run_completed`、不得被正式消费。
   
   **阻塞修复标准**：增加独立终态或明确 `completed` 的最低完整性条件，并补真实进程 SIGTERM 集成测试。

4. **High｜安全和 vendor 卫生验收无法证明其声称的边界**
   
   NFR 声称进程无网络出口、无证据台账写能力（[spec.md:260](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:260)），但设计承认网络护栏只是替换 Python socket、不是内核隔离（[design.md:208](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:208)）；子进程、原生扩展、直接文件描述符和符号链接均不受该声明覆盖。vendor 卫生 AC 又要求找出与上游不同的每一行（[spec.md:151](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:151)），但任务只保存 commit、清单和最终子集，没有保存可离线比较的上游基线或规范 patch（[tasks.md:31](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:31)、[tasks.md:49](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:49)）。两类测试都可能只验证自身包装层。
   
   **阻塞修复标准**：安全声明落到 OS capability/container/netns/权限边界并加入绕过测试；vendor 门保存上游文件摘要与规范 patch，离线重建差异后逐行校验。

5. **High｜任务包缺开工门，且两个跨 Feature 交接没有所有者**
   
   design 明确要求开发前必须有 `[TEST]` 体验旅程任务组（[design.md:16](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:16)），当前 tasks 到 T036 均没有该组。GPU 夜槽又声明 Kronos 卸载归 F004（[design.md:191](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:191)），但 F004 已 done，且 GPU 直通明确后移、未立项（[F004 tasks.md:72](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md:72)）；F003 的被动排队可能永久不出队。显式绑定切换到 `research_snapshot_id` 也被交给 F007（[F003 tasks.md:99](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:99)），而 F007 只有 snapshot builder，没有删除 F003 过渡入口或迁移调用方的任务（[F007 tasks.md:25](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md:25)）。
   
   **阻塞修复标准**：补 `[TEST]` 组；为 GPU 交接和 F003→F007 绑定迁移各指定唯一任务、owner、失败态与关闭条件。

**结论**
Round 1 full-scan：`Critical 0 / High 5`。**不满足 ready-for-development**；当前保持 `draft` 是正确状态。

这些问题复现了既有 `cross-doc-contract-drift`、`gate-without-teeth`、`spec-tasks-traceability-gap` 和 `deferred-work-without-carrier` 模式（[RETROSPECTIVE.md:192](/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md:192)、[RETROSPECTIVE.md:199](/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md:199)、[RETROSPECTIVE.md:483](/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md:483)）。

只读复核结束：基线仍为 `main@a333394`，工作树干净，无文件改动；LSP/build 不适用。下一步先裁决 F003-R1-001，将二日闸门的唯一合法输出收窄为 L0/L1。
