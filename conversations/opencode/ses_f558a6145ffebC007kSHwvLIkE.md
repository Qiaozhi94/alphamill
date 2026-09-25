---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f558a6145ffebC007kSHwvLIkE"
title: "Verify F003 upstream contracts (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T13:43:50Z"
updated_at: "2026-09-16T13:50:24Z"
tokens_input: 219133
tokens_output: 5944
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Verify F003 upstream contracts (@Sisyphus-Junior subagent)

## user · 2026-09-16T13:43:50Z

TASK: Verify F003's upstream and cross-feature contract claims against authoritative repo documents. EXPECTED OUTCOME: A citation-verdict table and evidence-backed findings for inaccurate/dangling/drifting contracts, with exact file:line on both sides, severity, origin, and fix suggestion. REQUIRED TOOLS: Read in-repo PRD, architecture, ADR-0001/2/3/6/7, integration, research, F002/F004/F007/F008 docs, BACKLOG, docs/README, CLAUDE; codegraph only if an actual code API must be inspected. MUST DO: Check AlphaGen smoke criteria and L0/L1/L2 predicates; FactorDef and F002 reader/identity/symbol_map contracts; GPU/Kronos ownership; F007 event/operator consumption; F008 coupling; reports ownership; active-feature/index consistency; dependency pin/gate downgrade promise. Include only contradictions or omissions that are materially actionable. MUST NOT DO: No edits, no internet, no commits, no uncited assertions. CONTEXT: Repo /home/georg/projects/alphamill, baseline main@a333394 clean; F003 files at docs/features/0.2/F003-alphagen-vendor; Round 1 doc review. Output in Chinese.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T13:43:50Z

- **tool**: `skill({"name": "review-convergence", "user_message": "Round 1 文档审查：核验 F003 上游及跨 feature 契约，只读、不修改、不提交，输出中文引用裁决表。"})`
- **tool**: `skill({"name": "git-master", "user_message": "只读确认 baseline main@a333394 与工作树状态；不修改、不提交。"})`


> [reasoning] **Planning review convergence with git status**
先锁定基线与审查范围；随后逐项做“双边引用”核对，只报告可执行的矛盾或遗漏。

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

  <details><summary>tool output</summary>

  ```text
## Skill: git-master

**Base directory**: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/git-master

# Git Master Agent

You are a Git expert combining three specializations:
1. **Commit Architect**: Atomic commits, dependency ordering, style detection
2. **Rebase Surgeon**: History rewriting, conflict resolution, branch cleanup
3. **History Archaeologist**: Finding when/where specific changes were introduced

---

## GIT COMMAND PREFIX (MANDATORY)

<git_env_prefix>
**EVERY git command MUST be prefixed with `GIT_MASTER=1`.**

This allows custom git hooks to detect when git-master skill is active.

```bash
GIT_MASTER=1 git status
GIT_MASTER=1 git add <files>
GIT_MASTER=1 git commit -m "message"
GIT_MASTER=1 git push
GIT_MASTER=1 git reba
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:44:15Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围", "status": "in_progress", "priority": "high"}, {"content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决", "status": "pending", "priority": "high"}, {"content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏", "status": "pending", "priority": "high"}, {"content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度
…[truncated])`


> [reasoning]

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度、来源、修复建议 - expect 中文报告无未引用断言且不修改仓库",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:24Z

- **tool**: `bash({"command": "GIT_MASTER=1 git branch --show-current && GIT_MASTER=1 git rev-parse --short HEAD && GIT_MASTER=1 git status --short", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "docs/**/*.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/AGENTS.md"})`


> [reasoning] **Planning parallel git and glob file discovery**

  <details><summary>tool output</summary>

  ```text
main
a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 43 file(s)

/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md
/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md
/home/georg/projects/alphamill/docs/reviews/RETROSPECTIVE.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md
/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/spec.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
/home/georg/projects/alphamill/docs/design/ui-mockup/README.md
/home/georg/p
…[truncated]
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

## assistant · 2026-09-16T13:44:35Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围", "status": "completed", "priority": "high"}, {"content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决", "status": "in_progress", "priority": "high"}, {"content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏", "status": "pending", "priority": "high"}, {"content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严
…[truncated])`


> [reasoning] **Planning extensive document reading**
基线已确认：`main@a333394`，工作树洁净；本轮为 F003 `spec/design/tasks` 的 full-scan 文档审查。现在开始核对上游真相源与 F003 声明，所有裁决保留双边行号。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度、来源、修复建议 - expect 中文报告无未引用断言且不修改仓库",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:48Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md"})`

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
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
1: # AlphaMill — 产品需求文档（PRD）
2: 
3: > 版本：v0.1 | 日期：2026-09-15 | 状态：草案
4: 
5: ## 一、背景与问题定义
6: 
7: ### 1.1 quant-crypto 复盘
8: 
9: 上一代项目 quant-crypto 已建成可复用的数据、推理、执行、风控与监控基础设施：631 万行
10: 1m OHLCV、衍生品特征、Kronos 信号缓存、Freqtrade dry-run、风险保护、90 天留出门和信号
11: 质量监控。最终状态为 `blocked_no_paper_candidate`：所有候选均未通过最终留出。
12: 
13: 这次失败暴露的不是单点工具缺失，而是研究到交易之间没有形成可持续运转的闭环：
14: 
15: - 假设主要靠人工提出，5 周只覆盖 3 个信号族，探索速度慢；
16: - 因子生成、成本评估、统计验证与策略构建的优化目标不完全一致；
17: - 数据、实验、信号和交易结果之间缺少统一谱系，复现与重定价成本高；
18: - 失败结果没有结构化回流为下一轮假设，研究循环无法积累；
19: - 研究 PASS、组合纳入、部署和线上衰减之间缺少完整生命周期管理。
20: 
21: AlphaMill 要解决的不是“多生成一些公式”，而是把 **Alpha 的发现、证伪、部署和运营**
22: 做成一条可信、可复现、可持续学习的生产管线。
23: 
24: ### 1.2 项目决策
25: 
26: 1. **以 AI 因子工厂为核心引擎**：程序化、RL、人工与 LLM 共同生产带来
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
1: # AlphaMill — 系统架构设计
2: 
3: > 版本：v0.1 | 日期：2026-09-13 | 配套：[alphamill-prd.md](./alphamill-prd.md)
4: 
5: ---
6: 
7: ## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
8: 
9: **不是三选一的竞品，是流水线上的三段**：Parquet 是文件格式（箱子），DuckDB 是查询引擎（开箱的手），TimescaleDB 是数据库服务（实时柜台）。
10: 
11: | | TimescaleDB | Parquet 湖 | DuckDB |
12: |---|---|---|---|
13: | 本质 | PG 时序扩展（数据库服务） | 列式文件格式（无服务） | 进程内 OLAP 查询引擎 |
14: | 写入 | ✅ 流式写入、幂等 upsert、可修订 | ❌ 不可变，只增新文件 | ❌ 不负责存储 |
15: | 擅长 | 实时最新值、连续聚合、Grafana 直连 | 大范围列扫描、快照不可变=可复现 | 直接对 Parquet 跑 SQL |
16: | 复现性 | ❌ 数据会被回补/修订 | ✅ 同一 data_version 永远同结果 | 无关（读的人） |
17: | 角色 | **联机运营库** | **研究快照**（封存账本） | **取数入口**（会计的手） |
18: 
19: ```text
20: CCXT 采集 ──写入──▶ TimescaleDB（联机运营库，随时改）
21
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:44:58Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0006-evidence-boundary-and-experiment-identity.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md"})`


> [reasoning] **Planning ADRs and integration research**

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
<path>/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md</path>
<type>file</type>
<content>
1: # ADR-0002：外部依赖管理策略 —— vendor / fork / 原样依赖三分法
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 操作细节：[`docs/alphamill-integration.md`](../alphamill-integration.md) §五
7: 
8: ## 背景
9: 
10: AlphaMill 引入四个开源项目：AlphaGen（挖掘引擎）、Freqtrade（执行）、Vibe-Trading（可选第二实现/Agent）、
11: Kronos（时序基础模型）。需要统一"改谁、不改谁、怎么跟上游"的规则。
12: 
13: 判断原则：**改动深度决定集成距离**。fork 仅适用于"要上游全部功能 + 必须改核心 + 上游不收 PR"
14: 的窄缝——四个引入项没有一个落在缝里。
15: 
16: ## 决策
17: 
18: | 引入项 | 方式 | 要点 |
19: |---|---|---|
20: | AlphaGen | **vendor** 进主仓 | 动大手术（换数据层/现代化）+ 上游冻结 + 只用子集 |
21: | Freqtrade | 原样依赖（官方 docker 镜像 + `user_data/` 插件层） | 零源码改动；pin 镜像 tag；上游 bug 走 issue + monkey-patch 过渡 |
22: | Vibe-Trading | 可选原样依赖（pip pi
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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0006-evidence-boundary-and-experiment-identity.md</path>
<type>file</type>
<content>
1: # ADR-0006：证据边界与实验身份 —— 显式执行层级、内容寻址和失败关闭
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：PRD FR3 / FR7；ADR-0003；F007 评测台/门禁；ml4t 配套仓的研究工作区与方法门实践
7: 
8: ## 背景
9: 
10: AlphaMill 已有四平面、留出预算和不可变 manifest，但仍有三个跨 Feature 的空隙：探索运行与
11: 正式裁决只有逻辑约定；实验 ID 没有明确区分“决定结果的语义输入”和“仅用于追踪的运行元数据”；
12: 方法实现出错时，缺少统一的失败语义。若这些规则分别留给 F007、F005 和后续部署 Feature
13: 自行解释，preview 可能污染正式样本，重跑可能生成不稳定身份，缺失统计量也可能被误当成 PASS。
14: 
15: ml4t 配套仓提供了可借鉴的模式：显式 `preview/canonical` 执行层级、正式 population 与探索产物
16: 隔离、方法论静态守卫，以及 label endpoint / per-symbol calendar / widest-horizon embargo 等
17: 时间边界测试。它同时是教学与参考实现，不是可直接接入的生产研究平台；其部分统计函数依赖
18: 外部包并会把估计失败降为 warning/空值。因此 AlphaMill 接纳边界模式，
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

## assistant · 2026-09-16T13:45:09Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-integration.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-research-factor-mining.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/tasks.md"})`


> [reasoning] **Identifying contract conflicts in smoke criteria**

> [reasoning] **Clarifying factor definition contract discrepancies**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-integration.md</path>
<type>file</type>
<content>
1: # AlphaMill — 集成设计
2: 
3: > 版本：v0.1 | 日期：2026-09-07 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)
4: > ⚠️ 本文档为集成操作细节；外部依赖管理策略已提炼至 [ADR-0002](decisions/0002-external-dependency-policy.md)。
5: > 本文回答：数据栈、可选研究/Agent 工具与 Freqtrade 怎样接入稳定的 AlphaMill 契约。
6: 
7: ---
8: 
9: ## 一、数据桥：TimescaleDB → Parquet 湖
10: 
11: ### 1.1 为什么需要这一层
12: 
13: - 生成器、评测、回测和可选第二实现需要共享同一份只读研究数据；
14: - 研究需要不可变快照：TimescaleDB 数据会被回补/修订，Parquet 快照 + 版本号保证"同一版数据永远算出同一版结果"；
15: - 双口径落盘（adjusted/raw）在导出时点固定，避免消费端各自解释。
16: 
17: ### 1.2 导出设计
18: 
19: | 项 | 设计 |
20: |---|---|
21: | 调度 | 每日 **02:00** 增量导出（昨日分区），每周日 04:00 全量校验；02:00 是排序约束——NAS 备份 03:00 起跑（带 10 分钟随机延迟），导出须先完成当日分区才会被同一晚的备份带走 |
22: | 分区 | `lake/ohlc
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-research-factor-mining.md</path>
<type>file</type>
<content>
1: # AlphaMill — 因子挖掘与 ML 开源选型调研
2: 
3: > 版本：v0.1 | 日期：2026-09-06 | 调研基线：GitHub API 元数据 + 2026-09 时点网络证据（两个独立调研交叉核对）
4: > 配套：[alphamill-prd.md](./alphamill-prd.md)（FR2 因子工厂）、[alphamill-architecture.md](./alphamill-architecture.md)
5: > ⚠️ 本文档为调研证据归档；选型决策已提炼至 [ADR-0001](decisions/0001-factor-mining-engine.md)，依赖管理策略见 [ADR-0002](decisions/0002-external-dependency-policy.md)。
6: 
7: ---
8: 
9: ## 一、选型结论（TL;DR）
10: 
11: | 槽位（映射 PRD） | 选型 | 一句话理由 |
12: |---|---|---|
13: | **生成器·主引擎**（FR2.2） | **AlphaGen**（`ICT-FinD-Lab/alphagen`）✅ 已锁定 | RL 批量探索与协同池适合因子工厂；产量须与有效独立性、成本和门禁漏斗共同衡量 |
14: | **生成器·对照基线**（FR2.2） | **AlphaGen 仓库自带 gplearn/dso**（不单独引入） | 直接对接 AlphaGen；保留独立搜索范式作为对照 |
15: | **候选种
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F002
4: version: "0.2"
5: status: done
6: gate_version: 1
7: related_features: [F001]
8: topics: [data-bridge, parquet, duckdb, m1]
9: doc_kind: spec
10: created: 2026-09-12
11: updated: 2026-09-14
12: ---
13: 
14: # F002：数据桥——Parquet 湖导出与 DuckDB 研究取数层
15: 
16: > Owner: Georg | Target: v0.2.0
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**:`docs/alphamill-prd.md` FR1.2(不可变快照)、FR1.3(研究只读边界)、FR1.4(双口径与时间语义)、FR1.6(灾备,湖部分);里程碑 M1
21: - **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
22: - **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F002
4: version: "0.2"
5: related_features: [F001]
6: topics: [data-bridge, parquet, duckdb, m1]
7: doc_kind: design
8: created: 2026-09-12
9: updated: 2026-09-13
10: ---
11: 
12: # F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: ## 0. 输入与约束
17: 
18: - **行为契约**:`spec.md`(FR-001..006 / NFR-001..003)
19: - **PRD / Architecture / System Design**:`docs/alphamill-prd.md` FR1.2/1.3/1.4/1.6/1.7、M1;`docs/alphamill-architecture.md` §〇、§四、§4.4/4.4.1;`docs/alphamill-integration.md` §1.2(导出设计与修订政策,唯一权威)、§2.2(symbol_map M1 出口)
20: - **决策约束**:ADR-0007 冻结 dataset 独立版本、DatasetVersion value digest 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F002
4: version: "0.2"
5: related_features: [F001]
6: topics: [data-bridge, parquet, duckdb, m1]
7: doc_kind: tasks
8: created: 2026-09-12
9: updated: 2026-09-14
10: ---
11: 
12: # F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源:`spec.md`。
19: - 技术方案与边界:`design.md`。
20: - 每项任务只描述一个可验证动作,并引用合法的 US/需求/AC ID。
21: - 完成且验证后立即把 `[ ]` 改为 `[x]`,不得最后统一补勾。
22: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
23: - 实现中若任务顺序或契约失效,先修订三件套,再继续编码。
24: 
25: ## 1. 前置条件
26: 
27: - F001 已 done:TimescaleDB 数据就绪(631 万行 binance)、`lake/` 目录位与 NAS 通道已预留、调度先例(backup/snapshot timer)
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:45:27Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围", "status": "completed", "priority": "high"}, {"content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决", "status": "completed", "priority": "high"}, {"content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏", "status": "in_progress", "priority": "high"}, {"content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据
…[truncated])`


> [reasoning] **Identifying high-level contract contradiction**

> [reasoning] **Planning to review F004, F007, and F008 documentation**
上游核对已出现两类实质风险：F003 的两日裁决描述把 L2 两周判据压进了冒烟期；过渡期显式元组也未覆盖 ADR-0007 要求的 cutoff、symbol map、PIT universe/calendar 身份。下一步核对 F004/F007/F008 的实际所有权，避免把“已分配”误判成“已消费”。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度、来源、修复建议 - expect 中文报告无未引用断言且不修改仓库",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:45:45Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md"})`

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
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F004
4: version: "0.2"
5: related_features: [F001, F002]
6: topics: [kronos, inference, deployment]
7: doc_kind: design
8: created: 2026-09-12
9: updated: 2026-09-15
10: ---
11: 
12: # F004：Kronos 真实推理运行时 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: ## 0. 输入与约束
17: 
18: - **行为契约**：`spec.md`（FR-001 / NFR-001）
19: - **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动
20: - **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-ws
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
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F002, F004]
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
22: - **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`
23: - **上游决策**：ADR-0003（门禁不降级）、ADR-0005（曲线侧车）、ADR-0006（证据边界与身份）、ADR-0007（ResearchSnapshot）
24: - **
…[truncated]
  ```
  </details>

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

## assistant · 2026-09-16T13:46:01Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/.gitignore"})`


> [reasoning] **Identifying GPU ownership conflict and dangling contracts**

> [reasoning] **Analyzing F003 report ownership and registry conflicts**

> [reasoning] **Confirming staged division of factor registry responsibilities**

> [reasoning] **Planning documentation review priority**

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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/.gitignore</path>
<type>file</type>
<content>
1: __pycache__/
2: *.py[cod]
3: .pytest_cache/
4: .ruff_cache/
5: .mypy_cache/
6: .coverage
7: htmlcov/
8: .venv/
9: venv/
10: dist/
11: build/
12: *.egg-info/
13: .idea/
14: .vscode/
15: .DS_Store
16: 
17: # 本机 AI 工具本地授权配置：含本机用户名路径与本地授权，不可移植
18: .claude/settings.local.json
19: 
20: # 编辑器本地历史
21: .history/
22: 
23: # 本机代理运行续接状态
24: .sisyphus/
25: 
26: # 本机 OpenCode 运行状态（含会话转录，严禁入库——密钥扫描门禁的原因之一）
27: .omo/
28: 
29: # 仿真/实验产生的数据与输出
30: data/raw/
31: data/processed/
32: results/
33: artifacts/
34: *.parquet
35: *.feather
36: 
37: # 本地-only 文档（保留在磁盘，不纳入 git）
38: docs/research/
39: docs/reviews/*
40: # ...例外：curated 摘要入库
41: !docs/reviews/RETROSPECTIVE.md
42: 
43: # 本地运行时密钥（模板为 deployment/.env.example，真实凭据人工搬运不进 g
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:46:24Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围", "status": "completed", "priority": "high"}, {"content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决", "status": "completed", "priority": "high"}, {"content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏", "status": "completed", "priority": "high"}, {"content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严
…[truncated])`


> [reasoning] **Identifying feature/index consistency gaps**

> [reasoning] **Highlighting dependency version pinning conflict**

> [reasoning] **Detecting missing global gitignore for reports**

> [reasoning] **Analyzing report ownership and gitignore rules**

> [reasoning] **Mapping AlphaGen smoke criteria to specs**

> [reasoning] **Planning M2 smoke pass with F007 integration**

> [reasoning] **Analyzing FactorDef serialization issues**

> [reasoning] **Identifying factor_id contract contradictions**

> [reasoning] **Evaluating bitemporal data handling in F003**

> [reasoning] **Analyzing F002 reader time filtering limitations**

> [reasoning] **Defining F003 binding and identity consistency**

> [reasoning] **Verifying F003 and F008 integration details**

> [reasoning] **Analyzing universe mask dependencies**

> [reasoning] **Tracing factor registry and report ownership**

> [reasoning] **Verifying dependency pin in F003 spec**

> [reasoning] **Clarifying version pinning semantics**

> [reasoning] **Identifying dependency pinning coverage gap**

> [reasoning] **Flagging unignored runtime output directory**

> [reasoning] **Confirming no edits or verification needed**

> [reasoning] **Synthesizing detailed findings with citations**

> [reasoning] **Detailing dataset availability semantics**

> [reasoning] **Identifying factor_id contract mismatches**

> [reasoning] **Planning FactorDef schema and contract fixes**

> [reasoning] **Fixing ownership handshake and dependency coupling**

> [reasoning] **Fixing artifact binding and factor path conflicts**

> [reasoning] **Identifying task inconsistencies and refining citation criteria**

> [reasoning] **Defining severity and origin categories**

> [reasoning] **Planning precise single-line citations**

> [reasoning] **Scheduling final verification and git status check**
跨 Feature 核对完成：最重的缺口集中在三处，分别是 F007 未承接 F003 的拒绝事件/算子能力、F004 已 done 却未拥有 GPU 卸载协议、F003 未把 F008 的 universe artifact 纳入绑定与任务依赖。现在只做引用与严重度复核，不再扩大审查范围。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度、来源、修复建议 - expect 中文报告无未引用断言且不修改仓库",
    "status": "in_progress",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:48:12Z

- **tool**: `bash({"command": "GIT_MASTER=1 git status --short", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Formulating concise findings table**

> [reasoning] **Assessing reports ownership and task gaps**

> [reasoning] **Proposing medium-severity process-gap addition**

> [reasoning] **Identifying dangling dependency and calendar mismatch**

> [reasoning] **Analyzing event consumption and dangling funnel**

> [reasoning] **Validating data format and artifact bindings**

> [reasoning] **Designing citation-verdict table structure**

> [reasoning] **Finalizing 10 key defect items**

> [reasoning] **Verifying F003-related GPU row status**

  <details><summary>tool output</summary>

  ```text
(no output)

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:48:49Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围", "status": "completed", "priority": "high"}, {"content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决", "status": "completed", "priority": "high"}, {"content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏", "status": "completed", "priority": "high"}, {"content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严
…[truncated])`

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与文档清单] 确认 main@a333394、洁净状态并定位全部必读权威文档 - expect 固定 Round 1 审查基线与完整文件范围",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与上游契约] 逐行比对 AlphaGen、FactorDef、F002、GPU/Kronos 及依赖门禁声明 - expect 形成双边精确引用与初步裁决",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 与跨功能契约] 逐行比对 F007、F008、reports、索引/BACKLOG 状态声明 - expect 识别 materially actionable 的矛盾或遗漏",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[Round 1 审查输出] 汇总 citation-verdict 表并复核每条证据、严重度、来源、修复建议 - expect 中文报告无未引用断言且不修改仓库",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:49:02Z


> [reasoning] **Planning final report with 10 findings table**

> [reasoning] **Detailing concise fix suggestions with evidence**

> [reasoning] **Structuring severity levels and validating reports**

> [reasoning] **Verifying evidence and clarifying severity assignments**
**结论**
基线：`main@a333394`，Round 1 full-scan。发现 **9 项 High、2 项 Medium**；未修改文件，最终工作树洁净。

| ID | 裁决 | 严重度 | 来源 | F003 声明 | 权威/对端契约 | 修复建议 |
|---|---|---:|---|---|---|---|
| F003-R001 | ResearchSnapshot 过渡契约不完整 | High | spec-drift | F003 允许用显式 `(dataset, data_version, value_digest)` 替代 ResearchSnapshot，并把实现交给 F007：[spec.md:112](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:112)、[design.md:114](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:114) | ADR-0007 要求身份同时冻结 cutoff、as-of、symbol-map、universe/calendar，且下游统一引用 snapshot ID：[0007:27](/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md:27)、[0007:47](/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md:47)、[0007:57](/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md:57)；builder 尚在 F007 T001：[F007 tasks:25](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md:25) | 将显式元组限制为单数据集、非 canonical 的引擎冒烟；任何多数据集 `mine` 依赖 F007 T001 和正式 snapshot ID。 |
| F003-R002 | 未承接 F002 reader 的 PIT/fail-closed 语义 | High | spec-drift | F003 只规定 invalid/digest 拒绝和张量抽样一致：[spec.md:165](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:165)、[spec.md:299](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:299) | F002 要求同时处理 event/available time、标签可用时间、质量旗和 `event_time_only` 显式豁免：[F002 design:69](/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md:69)、[F002 design:77](/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md:77)、[F002 design:302](/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md:302)、[F002 design:322](/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md:322) | 在 FR-003/AC-003 中明确 `FlaggedPartitionError`、`InsufficientAsOfFidelityError` 和历史 available-at 过滤策略，并增加晚到数据负例。 |
| F003-R003 | `factor_id` 跨重跑不稳定 | High | original-coding | 设计把 `run_seq` 写入 ID：[design.md:105](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:105) | 同一语义输入必须产生相同 ID 集合：[spec.md:259](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:259)、[spec.md:305](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:305) | `factor_id` 仅由规范化定义摘要导出；`run_id/run_seq` 只作 provenance。 |
| F003-R004 | FactorDef 持久化、报告目录与消费者引用未闭合 | High | spec-drift | F003 把运行目录中的 JSON 定为候选唯一真相源，schema 没有 `compute/meta`：[design.md:81](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:81)、[design.md:94](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:94)、[design.md:102](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:102) | 架构 FactorDef 契约要求可执行 `compute` 与 `meta`：[architecture:254](/home/georg/projects/alphamill/docs/alphamill-architecture.md:254)；架构把 registry 与 reports 分列：[architecture:184](/home/georg/projects/alphamill/docs/alphamill-architecture.md:184)、[architecture:205](/home/georg/projects/alphamill/docs/alphamill-architecture.md:205)；F007 只说接受“可解析 FactorDef 引用”，未定义 F003 reader：[F007 spec:212](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:212) | 定义稳定的序列化 DTO、`load_factor(ref) -> FactorDef` 水合接口及 canonical artifact 路径；增加 F003→F007 contract test。 |
| F003-R005 | 两日闸门错误包含 L2 裁决 | High | spec-drift | FR-006 声称两日内可降到 L1/L2：[spec.md:213](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:213) | ADR-0001 的两日判据只触发 L1；L1→L2 要连续两周满足健康判据：[0001:40](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:40)、[0001:47](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:47) | 两日输出只能是 `L0 locked` 或 `L1`；另建持续两周的 L1 健康监测与 L2 裁决任务。 |
| F003-R006 | AlphaGen smoke 少了两项 ADR 验收 | High | spec-drift | F003 冒烟验收仅覆盖 PPO/训练循环/因子与 IC 对齐：[spec.md:74](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:74)、[tasks.md:77](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:77) | ADR 另要求首日起完整漏斗计数，以及奖励频率/可达性抽查：[0001:52](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:52)、[0001:57](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:57)、[0001:60](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:60) | 将两项加入 AC-007/T032；若下游门尚未实现，明确区分“引擎闸门通过”和“M2 smoke 未完成”。 |
| F003-R007 | F007 对 generation 事件和 operator registry 的消费是悬空声明 | High | spec-drift | F003 声称 F007 消费拒绝事件及算子能力清单：[spec.md:247](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:247)、[tasks.md:61](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:61) | F007 的 related/upstream/dependency 只列 F002、F004 和泛化 FactorDef：[F007 spec:7](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:7)、[F007 spec:22](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:22)、[F007 spec:279](/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:279) | 在 F007 增加 F003 related feature、事件/schema reader、operator-registry 输入和漏斗重建 contract test。 |
| F003-R008 | Kronos 卸载没有实际 owner | High | spec-drift | F003 依赖夜槽卸载 Kronos，并称动作归 F004：[design.md:186](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:186)、[spec.md:335](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:335) | F004 已 done，但明确不做 GPU、消费者路由仍指 mock，后移项也未立 Feature：[F004 spec:5](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md:5)、[F004 spec:42](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md:42)、[F004 tasks:72](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md:72) | 新建立项并指定 GPU 调度 owner；定义 Kronos stop/start、共享锁、失败恢复和 dry-run 存量缓存验证。 |
| F003-R009 | F008 universe artifact 未进入 F003 实现依赖 | High | spec-drift | F003 T020 直接实现 PIT mask，T035 仅在扩容后复跑：[tasks.md:59](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:59)、[tasks.md:80](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:80) | F008 明确提供按 digest 的 `universe_at(T)`，并要求 F003 只读消费：[F008 spec:243](/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md:243)、[F008 design:68](/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md:68)、[F008 tasks:84](/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md:84) | 让 cross-sectional run 强制接收 universe artifact digest；T020 依赖 F008 T009，扩容前仅允许明确标注的时序/冒烟路径。 |
| F003-R010 | pin 与门禁降级补偿未进入验收面 | Medium | process-gap | spec 称依赖全部 pin，但任务只要求版本范围；门禁改为“安装才检查”：[spec.md:322](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:322)、[tasks.md:50](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md:50)、[design.md:210](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:210) | ADR-0002 要求版本 pin 且升级后先冒烟：[0002:35](/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md:35) | 裁定“pin”是精确版本还是范围+lock；为“extra 缺失必拒绝启动”和“升级必重跑 smoke”增加独立 AC/变异测试。 |
| F003-R011 | active-feature 索引漂移 | Medium | process-gap | `CLAUDE.md` 只列 F004/F007：[CLAUDE.md:49](/home/georg/projects/alphamill/CLAUDE.md:49)；文档地图仍称 F003/F004/F007/F008 活跃：[docs/README.md:36](/home/georg/projects/alphamill/docs/README.md:36) | 派生真相 BACKLOG 实际为 F003/F007/F008：[BACKLOG.md:3](/home/georg/projects/alphamill/BACKLOG.md:3)、[BACKLOG.md:8](/home/georg/projects/alphamill/BACKLOG.md:8)；F004 已 done：[F004 spec:5](/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md:5) | 同步 `CLAUDE.md` 与 `docs/README.md`；把两者的 active 集合纳入生命周期门禁，避免再次漂移。 |

Round 1 **不满足收敛条件**：存在 High 级契约缺口。下一步应先修 F003-R001、R005、R007、R008、R009，再进入实现。
