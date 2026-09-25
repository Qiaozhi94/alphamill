---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f558a633affeZ24lEdC6XzMlIh"
title: "Audit F003 spec design (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T13:43:49Z"
updated_at: "2026-09-16T13:52:29Z"
tokens_input: 154859
tokens_output: 7128
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Audit F003 spec design (@Sisyphus-Junior subagent)

## user · 2026-09-16T13:43:49Z

TASK: Perform a read-only deep semantic review of F003 spec.md and design.md. EXPECTED OUTCOME: A complete, deduplicated finding list with exact file:line evidence, severity, category, root-cause/symptom, origin, suggested fix, and proposed regression/document gate. REQUIRED TOOLS: Read repository markdown files and use codegraph only if code symbols are needed; no edits. MUST DO: Check all requirements/NFRs/lifecycle states/ACs against design contracts, failure/recovery/security/concurrency semantics, data identity, determinism, event persistence, CLI behavior, execution-machine evidence, and project non-negotiable principles. Validate especially whether rejected/failed runs can preserve required reasons/events when run.json is absent; whether factor_id is stable across runs despite run_seq; whether FIFO via flock is actually specified well enough; whether early SIGTERM completed semantics violate atomic full-run claims; whether egress/write boundary tests prove the claimed boundary. Include only evidence-backed findings. MUST NOT DO: Do not edit/create files, commit, speculate without a cited contradiction, or review implementation code. CONTEXT: Repo /home/georg/projects/alphamill, baseline main@a333394 clean. Files docs/features/0.2/F003-alphagen-vendor/spec.md and design.md. Round 1 full scan under review-convergence. Output in Chinese.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T13:43:50Z

- **tool**: `skill({"name": "review-convergence", "user_message": "对 F003 spec.md 和 design.md 做第 1 轮 full-scan 只读深度语义检视，输出中文证据化 findings，不编辑文件。"})`


> [reasoning] **Planning review and reading tasks**
第 1/4 步：先锁定审查门槛与基线，再并行通读项目约束、F003 规格和设计。全程只读，不检查实现代码，也不写入检视文件。

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

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单", "status": "in_progress", "priority": "high"}, {"content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号", "status": "pending", "priority": "high"}, {"content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings", "status": "pending", "priority": "high"}, {"content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 find
…[truncated])`

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 finding 列表且零文件改动",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:18Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/AGENTS.md"})`
- **tool**: `bash({"command": "git branch --show-current && git rev-parse --short HEAD && git status --short", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Reading CLAUDE and AGENTS files in parallel**

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
main
a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:44:28Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单", "status": "completed", "priority": "high"}, {"content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号", "status": "in_progress", "priority": "high"}, {"content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings", "status": "pending", "priority": "high"}, {"content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 fi
…[truncated])`


> [reasoning] **Planning full repository markdown review**
第 1/4 步完成：基线与用户声明一致，`main@a333394`，工作树无改动。项目硬约束包括统一 `verify.py` 门禁、不可变数据快照、确定性规则裁决、Agent 无生产写权限，以及执行机证据不可由开发机 skip 替代。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 finding 列表且零文件改动",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:44:40Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/README.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0003-validation-gates-non-degradation.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0006-evidence-boundary-experiment-identity.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md", "limit": 2000})`

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

## assistant · 2026-09-16T13:44:52Z

- **tool**: `glob({"path": "/home/georg/projects/alphamill/docs/decisions", "pattern": "*.md"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "pattern": "FR2\\.|G3|生成器|因子工厂|权限|生产写", "output_mode": "content", "head_limit": 120})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "pattern": "^## |^### |FactorDef|AlphaGen|GenerationRun|单槽|FIFO|flock|run.json|manifest|SIGTERM|事件|append-only|执行机|egress", "output_mode": "content", "head_limit": 240})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-integration.md", "pattern": "vendor|网络|egress|写入|权限|FactorDef|AlphaGen", "output_mode": "content", "head_limit": 160})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md", "limit": 2000})`


> [reasoning] **Planning targeted markdown extraction**

> [reasoning] **Confirming document targeting strategy**
第 2/4 步进行中：规格已完整展开。接下来只读取它明确引用的权威文档段落，核对身份、持久化、单卡调度和安全边界是否发生契约漂移；不会触碰实现代码。

  <details><summary>tool output</summary>

  ```text
Found 9 file(s)

/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md
/home/georg/projects/alphamill/docs/decisions/0005-presentation-observability.md
/home/georg/projects/alphamill/docs/decisions/0008-north-star-sustained-profitability.md
/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md
/home/georg/projects/alphamill/docs/decisions/0006-evidence-boundary-and-experiment-identity.md
/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md
/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md
/home/georg/projects/alphamill/docs/decisions/0004-portfolio-construction.md
/home/georg/projects/alphamill/docs/decisions/000-template.md
[Agent Usage Reminder]

You called a search/fetch tool d
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 15 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-prd.md
  26: 1. **以 AI 因子工厂为核心引擎**：程序化、RL、人工与 LLM 共同生产带来源和经济假设的
  39: > AlphaMill（中文别名：淘沙）是一套 **AI 原生的加密量化研究与交易管线**：以 AI 因子工厂
  80: | G3 | 建立 AI 因子工厂 | 至少两类可插拔生成器；具备单批 ≥50 候选自动评测的批量能力（能力标定，非持续产出目标）；同时报告有效独立数、来源分布和各级漏斗 |
  151: ### FR2 AI 因子工厂
  153: - **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
  155: - **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
  156: 生成器只产出 FactorDef/协同池定义，不拥有最终评测权。
  157: - **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
  159: - **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；前视、网络访问、隐式全样本统计和未支持的跨 pair
  161: - **FR2.5 因子注册表**：保存定义、参数、数据依赖、来源、版本、评测摘要和生命周期；IC/OOS PnL
  163: - **FR2.6 探索组合**：AlphaGen 协同池作为可部署 meta-factor 注册；名义产量、有效独立数、来源多样性
  219: paper/live 路径生效；Agent 无下单权和绕门
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 58 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  7: ## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
  21: │  data_bridge：导出不可变快照 + manifest
  30: ## 一、总体架构与职责边界
  45: │ HypothesisDef / FactorDef                    │ 报告与事件
  64: 监控归因 → 人审后的新假设。Vibe-Trading 可提供第二意见或 Agent 能力，AlphaGen 可提供因子，
  69: ## 二、Mermaid 架构图
  71: ### 2.1 闭环架构（模块级）
  77: GEN["生成器组<br/>AlphaGen · GP/表达式 · manual/LLM · Kronos"]
  111: BR["data_bridge<br/>质量门 · 对账 · manifest"]
  124: MON -->|"报告与事件"| POST
  131: ### 2.2 Alpha 生命周期数据流
  135: A[HypothesisDef] --> B[FactorDef / meta-factor]
  171: ## 三、模块与目录设计
  184: ├── reports/                     # 实验 manifest + 归档报告（运行产物）
  186: ├── data_bridge/             # FR1：TimescaleDB → Parquet + manifest
  189: │   └── manifest_schema.j
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 11 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-integration.md
  60: Vibe-Trading 的 `local` loader 通过 `local:` 前缀符号读取本地文件，且**禁止静默回退到网络源**（口径可控的关键）。接入配置：
  113: → 归因报告落 `reports/postmortem/` → 新假设草案经人工审阅后进入队列。Agent 无生产写权限。
  121: | 行情 loader 网络源 | 数据口径必须收敛到自家湖，防止"哪个源先回答用哪个" |
  122: | MCP 写类工具 / shell 工具 | 最小权限；alphamill 的写路径全部走自家脚本 |
  194: ## 五、外部依赖管理策略（vendor / fork / 原样依赖）
  196: > 判断原则：**改动深度决定集成距离**。要动大手术的 vendor 进主仓；只用扩展面的原样依赖；fork 仅适用于"要上游全部 + 必须改核心 + 上游不收 PR"的窄缝——本项目三个引入项没有一个落在缝里，**一律不 fork**。
  200: | **AlphaGen** | **vendor** 进 `src/alphamill/factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md`；不考虑跟随上游 |
  205: ### vendor 卫生规则（AlphaGen 专用）
  207: 
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

## assistant · 2026-09-16T13:45:07Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0002-external-dependency-policy.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0006-evidence-boundary-and-experiment-identity.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 145, "limit": 25})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 235, "limit": 56})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 436, "limit": 34})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 548, "limit": 32})`


> [reasoning] **Planning targeted ADR and source reviews**

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
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
145:   独立工作流，预计 1~2 周 wall-clock。
146: - **FR1.6 灾备**：数据库、Parquet manifest 与实验报告每日备份至 NAS，本地保留滚动副本并定期恢复演练。
147: - **FR1.7 多数据集研究快照**：多数据集实验必须先生成不可变 `ResearchSnapshot`，显式绑定每个
148:   `(dataset, data_version, value_digest)`、信息 cutoff、symbol map 与 point-in-time universe/calendar
149:   摘要；canonical 不得在运行时解析 latest 或按导出时间猜测全湖版本。
150: 
151: ### FR2 AI 因子工厂
152: 
153: - **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
154:   generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。
155: - **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
156:   生成器只产出 FactorDef/协同池定义，不拥有最终评测权。
157: - **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
158:   禁止只优化 RankIC。
159: - **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
235: ## 四、关键接口契约
236: 
237: ### 4.0 闭环核心对象
238: 
239: ```text
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
252: -
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
436: ### 4.5 实验身份与执行上下文
437: 
438: ```text
439: ExperimentContext = {
440:   execution_tier: preview | canonical,
441:   upstream_object_id,
442:   cohort_id,
443:   normalized_method_config,
444:   research_snapshot_id,
445:   code_build_digest,
446:   seed,
447:   supersedes?
448: }
449: 
450: experiment_id = digest(upstream_object_id, cohort_id, normalized_method_config,
451:                        research_snapshot_id, code_build_digest, seed)
452: provenance = {artifact_path, file_sha256, codec, created_at, host, duration}
453: ```
454: 
455: `execution_tier` 必须由调用方显式构造并沿调用链传递，不读取环境变量或进程全局默认值。
456: 它与 `supersedes` 不参与 `experiment_id`：前者由命名空间/capability 强制，后者只是谱系关系；
457: preview 与 can
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

## assistant · 2026-09-16T13:45:23Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单", "status": "completed", "priority": "high"}, {"content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号", "status": "completed", "priority": "high"}, {"content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings", "status": "in_progress", "priority": "high"}, {"content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 
…[truncated])`


> [reasoning] **Verifying rejection handling contradictions**

> [reasoning] **Proposing fixes for spec-drift and concurrency**

> [reasoning] **Highlighting FIFO semantics incompleteness**

> [reasoning] **Assessing concurrency and correctness issues**

> [reasoning] **Identifying run completion atomicity violation**

> [reasoning] **Highlighting network egress enforcement weakness**

> [reasoning] **Testing subprocess AF_INET blocking and tuple binding compliance**

> [reasoning] **Identifying reproducibility and identity specification gaps**

> [reasoning] **Highlighting missing deterministic ordering and reproducibility contracts**

> [reasoning] **Analyzing event storage atomicity and deletions**

> [reasoning] **Evaluating atomic visibility and event durability issues**

> [reasoning] **Clarifying factor fields and pool ID content addressing**

> [reasoning] **Assessing pool_id and run_id ambiguities**

> [reasoning] **Identifying CLI and scheduling inconsistencies**

> [reasoning] **Consolidating scheduler queue contract issues**

> [reasoning] **Refining timeout and window gating logic**

> [reasoning] **Assessing execution environment test limitations**

> [reasoning] **Identifying missing reports backup retention**

> [reasoning] **Assessing event persistence gaps**

> [reasoning] **Investigating reports backup architecture**

> [reasoning] **Reviewing candidate findings and design progress**
第 2/4 步完成：需求、NFR、生命周期、AC、CLI 与权威 ADR 已建立映射。已确认至少三类硬冲突：过渡绑定缺少完整研究快照语义、跨运行 `factor_id` 被 `run_seq` 破坏、终态持久化无法覆盖 REJECTED/FAILED；现在继续收敛并发、SIGTERM 与边界测试证据。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 finding 列表且零文件改动",
    "status": "pending",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:46:35Z

- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "pattern": "备份|NAS|reports/|运行产物|恢复", "output_mode": "content", "head_limit": 100})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "pattern": "REJECTED|FAILED|run_completed|candidate_rejected|run.json|原子|factor_id|FIFO|SIGTERM|egress|无网络|写入|allow-offhours|determin|确定|重跑", "output_mode": "content", "head_limit": 160})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "pattern": "REJECTED|FAILED|run_completed|candidate_rejected|run.json|原子|factor_id|FIFO|SIGTERM|egress|无网络|写入|allow-offhours|determin|确定|重跑|flock|socket|白名单", "output_mode": "content", "head_limit": 200})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "pattern": "AC-00[1-9]|AC-010|AC-011|test_f003", "output_mode": "content", "head_limit": 120})`

  <details><summary>tool output</summary>

  ```text
Found 5 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  184: ├── reports/                     # 实验 manifest + 归档报告（运行产物）
  339: （`reports/bench/<object_id>/<research_snapshot_id>/<experiment_id>/curves.parquet`，报告根 `reports/`
  428: ResearchSnapshot 位于 `reports/research_snapshots/<snapshot_id>/manifest.json`，只引用 lake manifests，
  433: `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`，二者均可按 snapshot provenance
  560: - **平台变了**：Windows 11 + WSL2 → 原生 Ubuntu，docker 编排、路径、开机自启、备份通道都要重新落地；
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 30 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
  60: **独立测试**：只启用人工种子后端，对固定快照绑定与固定 seed 连续跑两次 `produce()`，验证得到相同的 factor_id 集合与可执行的 `compute`，全程不加载任何 AlphaGen 代码。
  65: 2. Given 同一 `(seed, 快照绑定, code digest)`，when 重跑生成运行，then 得到完全相同的 factor_id 集合。
  74: **独立测试**：在最小数据切片上执行 `alphamill-generate smoke`，检查四条 ADR-0001 判据逐条产出 `pass/fail` 与时间戳，并写入当日冒烟 manifest。
  92: 1. Given 一次训练窗口内的挖掘运行，when 运行完成，then 入册候选数 ≥50 且每级计数（产出/自检拒绝/入册）写入 GenerationRun。
  93: 2. Given 协同池已产出，when 把池导出为 meta-factor，then 成员 factor_id 与权重可反解，且按成员定义重算的池值与记录一致。
  121: - 训练窗口外或可用显存低于预算时启动挖掘：进单槽 FIFO 队列等待，绝不与 Kronos 常驻推理并行赌 OOM。
  122: - vendor 代码尝试联网（下载数据/权重）：生成运行在无网络出口下执行，任何 egress 视为失败。
  143: - GIVEN 一个后端在结果中写入 IC 或 verdict 字段
  171: - THEN 运行被拒绝，不产出候选，拒绝原因写入
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 41 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  31: - **迁移前瞻**：显存上限、时段表、耗时/产能相关的值必须可配且写入运行记录，**不得写死常数**。迁移不只是换卡：平台从 Win11+WSL2 变成原生 Ubuntu，GPU 架构从 Ada 变成 Blackwell sm_120（**torch 必须是 CUDA 12.8+ 的构建，默认 wheel 不一定含该架构**），因此 `mining` extra 的 pin 要显式选择带 sm_120 的轮子。
  41: - Event / Evidence：新增 `generation.run_completed` / `generation.candidate_rejected` 两类 append-only 事件；**不写任何 F007 台账、留出或晋级路径**
  61: │   ├── gpu_slot.py           # 显存自检 + 单槽 FIFO + 训练窗口校验（NFR-002）
  62: │   ├── egress_guard.py       # 进程级无网络出口护栏（NFR-004）
  81: | 唯一真相源 | 候选定义 = `factors/<factor_id>.json`；运行事实 = `run.json`；两者之外不得出现第二份候选清单 |
  83: **vendor 子集边界（按功能定义，不预先钉死上游路径）**：取表达式与算子、张量求值器、线性协同池、RL 环境与 token 化四块；**明确丢弃** `alphagen_qlib/`（qlib 数据层）、上游 `requireme
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 13 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  77: | 胶水 → vendor | 单向。vendor 内任何 `import alphamill.*` 视为卫生检查失败（AC-002） |
  106: - **禁止字段**：`ic`、`rank_ic`、`pnl`、`verdict`、`promoted` 等结论字段由 schema 白名单显式拒绝（AC-001）。
  216: | `AC-001` | unit | `tests/unit/test_f003_generator_contract.py` | 两后端同一 schema；含 `ic`/`verdict` 等结论字段的结果被拒绝 |
  217: | `AC-002` | unit | `tests/unit/test_f003_vendor_hygiene.py` | vendor 内无标注差异行报错；vendor 内 `import alphamill` 报错；`VENDORED.md` 五项齐备 |
  218: | `AC-003` | integration | `tests/integration/test_f003_lake_tensor.py` | invalid/digest 不符拒绝启动；张量与 reader 抽样点容差内一致；不可交易时点掩码为不可用 |
  219: | `AC-004` | unit | `tests/unit/test_f003_alphagen_adapter.py` | 编译闭包与张量求值一致；表达式反解等价；`data_columns` 由 `feature_map` 反解
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:46:46Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单", "status": "completed", "priority": "high"}, {"content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号", "status": "completed", "priority": "high"}, {"content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings", "status": "completed", "priority": "high"}, {"content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 fi
…[truncated])`


> [reasoning] **Clarifying smoke gate criteria count**

> [reasoning] **Identifying L2 decision timing inconsistency**

> [reasoning] **Highlighting funnel ledger delegation conflict**

> [reasoning] **Clarifying reward and cost specification conflicts**

> [reasoning] **Planning cost proxy addition and alignment fixes**

> [reasoning] **Assessing feature slice responsibility**

> [reasoning] **Clarifying FactorDef compute serialization**

> [reasoning] **Resolving FactorDef and AlphaPoolDef discrepancy**

> [reasoning] **Identifying CLI inconsistencies and limitations**

> [reasoning] **Clarifying CLI seed handling and test coverage**

> [reasoning] **Assessing execution environment evidence and CPU usage controls**

> [reasoning] **Noting missing timezone in execution scheduling**

> [reasoning] **Identifying inconsistent lock ownership across services**

> [reasoning] **Assessing atomic commit and lifecycle protocol gaps**

> [reasoning] **Highlighting event persistence and schema version issues**

> [reasoning] **Identifying schema_version omission in run.json**

> [reasoning] **Highlighting missing normalized config for reproducibility**

> [reasoning] **Noting missing design for reproducibility mechanism**

> [reasoning] **Planning detailed findings table**

> [reasoning] **Tracing reason code taxonomy inconsistency**

> [reasoning] **Evaluating distinct operator reason codes**

> [reasoning] **Identifying missing event assertions in AC009**

> [reasoning] **Finding multiple test coverage gaps and event persistence issues**

> [reasoning] **Highlighting commit-marker consumer contract gap**

> [reasoning] **Analyzing ID concurrency and GPU locking conflicts**

> [reasoning] **Planning final design verification and crosscheck**
第 3/4 步完成：并发与安全语义已收敛。关键结论是 `flock` 只证明互斥，当前设计既未定义可验证的 FIFO 排序，也把窗口外请求从“排队”改成拒绝/绕过；`socket` monkeypatch 与应用层写白名单同样不能证明“进程不具备能力”的边界。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 finding 列表且零文件改动",
    "status": "in_progress",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:48:20Z

- **tool**: `bash({"command": "git status --short && git branch --show-current && git rev-parse --short HEAD", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Finalizing root-cause spec-drift analysis**

> [reasoning] **Detailing multiple root-cause spec-drift issues**

> [reasoning] **Assessing correctness root causes and fixes**

> [reasoning] **Fixing config determinism and CLI spec drift**

> [reasoning] **Refining finding category vocabulary**

> [reasoning] **Assigning spec-drift origin to findings**

> [reasoning] **Planning final verification and formatting**

> [reasoning] **Verifying no uncommitted changes**
第 4/4 步：正在做最终去重和证据反查。当前候选为 13 条：9 条 High、4 条 Medium；每条都能落到明确的规格/设计/权威文档行号，并配有可执行的文档或回归门禁。

  <details><summary>tool output</summary>

  ```text
main
a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:49:22Z

- **tool**: `todowrite({"todos": [{"content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单", "status": "completed", "priority": "high"}, {"content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号", "status": "completed", "priority": "high"}, {"content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings", "status": "completed", "priority": "high"}, {"content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 fi
…[truncated])`


> [reasoning] **Marking final todo complete**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "[仓库基线与项目文档] 读取 CLAUDE.md/AGENTS.md 并核验 main@a333394 clean 以锁定审查门槛 - expect 有明确基线和项目非协商原则清单",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 spec.md] 全量提取需求、NFR、生命周期、AC、CLI 与证据契约以建立审查矩阵 - expect 每项契约都有精确行号",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[F003 design.md] 对照审查失败恢复、安全并发、身份确定性、事件持久化与执行机证据 - expect 形成证据支持且去重的候选 findings",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "[最终报告] 交叉核对候选 finding 的矛盾证据、分级和文档门禁以排除推测 - expect 中文完整 finding 列表且零文件改动",
    "status": "completed",
    "priority": "high"
  }
]
  ```
  </details>

## assistant · 2026-09-16T13:49:36Z


> [reasoning] **Finalizing report format and links**

> [reasoning] **Defining detailed finding structure and categories**

> [reasoning] **Verifying specification consistency and omissions**

> [reasoning] **Evaluating schema and defining next action**

> [reasoning] **Planning numbered findings presentation**


> [reasoning] **Planning formatted findings with line references**

> [reasoning] **Defining finding categories and severity levels**

> [reasoning] **Identifying spec contradiction on F003 tuple consumption**

> [reasoning] **Analyzing spec-drift risks in dataset generation**

> [reasoning] **Assessing severity levels for specification gaps**

> [reasoning] **Clarifying distinct specification requirement overlaps**

> [reasoning] **Planning concise Chinese summary**

> [reasoning] **Confirming Chinese punctuation usage**
**结论**

基线：`main@a333394`，Round 1 `full-scan`，工作树保持干净。共发现 **13 条去重问题：High 10、Medium 3**。存在阻塞项，当前规格不应进入开发阶段。

### F003-R001：REJECTED/FAILED 运行没有可持久化的终态事实
`High | correctness | root-cause | spec-drift`

- 证据：规格要求拒绝原因写入运行记录 [spec.md:171](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:171)，并定义 `REJECTED/FAILED` 状态 [spec.md:268](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:268)。设计却将 `run.json` 定义为运行事实唯一真源 [design.md:81](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:81)，FAILED 不写 `run.json`、REJECTED 只入日志 [design.md:190](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:190) [design.md:206](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:206)，且无 manifest 的目录可直接删除 [design.md:207](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:207)。
- 建议修复：为所有已分配 `run_id` 的终态写不可变最小 manifest，或在独立耐久事件流中增加 `run_rejected/run_failed`；原因码、阶段和时间戳必须保留。
- 文档/回归门：分别触发 invalid binding、训练异常、写出异常；进程退出及恢复清理后仍能按 `run_id` 查询终态与原因，且不得出现 `run_completed`。

### F003-R002：`run_seq` 使 `factor_id` 无法跨运行稳定
`High | correctness | root-cause | spec-drift`

- 证据：规格要求相同语义输入重跑得到相同 `factor_id` 集合 [spec.md:65](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:65) [spec.md:259](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:259)。设计虽从 digest 排除 `run_id` [design.md:104](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:104)，却定义 `factor_id=<generator>_r<run_seq>_<digest>` [design.md:105](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:105)。
- 建议修复：`factor_id` 只由规范化定义摘要派生；运行归属仅保存在 `run_id`/provenance 中。
- 文档/回归门：使用不同 `run_id/run_seq` 重跑相同定义，断言 ID 相同；修改任一语义字段后断言 ID 改变。

### F003-R003：过渡绑定缺失 cutoff、PIT universe/calendar 等语义身份
`High | correctness | root-cause | spec-drift`

- 证据：PRD 要求多数据集研究冻结 cutoff、symbol map 与 PIT universe/calendar 摘要 [alphamill-prd.md:147](/home/georg/projects/alphamill/docs/alphamill-prd.md:147)；ADR-0007 将这些字段纳入 `snapshot_id` [0007-research-snapshot-binding.md:47](/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md:47)。设计的过渡绑定只有 `(dataset,data_version,value_digest)` [design.md:114](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:114)，无法冻结构造张量所用的 PIT 掩码语义。
- 建议修复：过渡绑定必须携带并内容寻址 cutoff、as-of fidelity、symbol-map artifact、universe/calendar artifact；否则仅允许单数据集且不使用截面/PIT 语义。
- 文档/回归门：缺任一摘要时拒绝；保持 dataset 元组不变而改变 universe/calendar 时，绑定 ID 和运行身份必须改变。

### F003-R004：`flock` 只定义互斥，未定义可验证 FIFO，且窗口外行为相互矛盾
`High | correctness | root-cause | spec-drift`

- 证据：规格与架构要求窗口外、显存不足或碰撞时进入 FIFO [spec.md:121](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:121) [alphamill-architecture.md:575](/home/georg/projects/alphamill/docs/alphamill-architecture.md:575)。设计仅声明 `flock` 和“按取锁顺序” [design.md:174](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:174) [design.md:186](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:186)，没有票号、持久队列、取消/重启规则；窗口外又变成拒绝或 `--allow-offhours` 绕过 [design.md:153](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:153)。
- 建议修复：定义共享调度协议，包括单调 ticket、资格时间、锁所有者、崩溃回收、取消和跨 F003/F004/Vibe 的共同参与方式。
- 文档/回归门：在执行机启动 A/B/C 三个独立进程并验证严格顺序、最大并发为 1；窗口外任务保持 QUEUED 到窗口开启；模拟持锁进程崩溃后顺序不倒置。

### F003-R005：早期 SIGTERM 被标为 COMPLETED，破坏完整运行语义
`High | correctness | root-cause | spec-drift`

- 证据：规格将 COMPLETED 定义为候选集与 manifest 原子写出 [spec.md:269](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:269)，完成运行还要求入册至少 50 个候选 [spec.md:92](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:92)。设计允许任意 SIGTERM 导出部分结果并写 `status=completed` [design.md:190](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:190)。
- 建议修复：增加 `INTERRUPTED/CANCELLED`；部分产物不可入册、不可发 `run_completed`。只有满足完整性检查后才能原子转为 COMPLETED。
- 文档/回归门：在配额未完成时发送 SIGTERM，断言无 `run_completed`、无可消费候选，终态明确为中断；完成边界后 SIGTERM 才允许保持 COMPLETED。

### F003-R006：进程内 monkeypatch 和应用层白名单不能证明能力边界
`High | correctness/security | root-cause | spec-drift`

- 证据：规格声称“无网络出口”且生成器进程“不具备”写正式证据路径的能力 [spec.md:260](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:260)。设计明确承认仅替换 socket 构造函数、不是内核隔离 [design.md:208](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:208)，但 AC 只验证 guard 拦截 [design.md:226](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:226)。
- 建议修复：要么采用容器/netns、只读挂载、独立 UID 与目录权限实现能力边界；要么把 NFR 降为“合作式进程内防误用”，不得继续声称无出口/无写能力。
- 文档/回归门：从生成器子进程尝试原始 AF_INET、外部二进制出网、直接文件 API 和子进程写证据目录，全部必须由执行沙箱拒绝；合法运行目录写入仍成功。

### F003-R007：两日闸门无法合法裁决 L2
`High | correctness | root-cause | spec-drift`

- 证据：规格要求两日内输出锁定或 L1/L2 [spec.md:213](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:213)。ADR-0001 则规定 L2 只能由 L1 连续两周低产出或零候选通过无前视审计触发 [0001-factor-mining-engine.md:47](/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md:47)，后者还依赖 F007。
- 建议修复：两日闸门只能裁决 `L0 locked` 或 `L1`；`L1→L2` 改为独立的两周健康观测状态机，消费 F007 审计事实。
- 文档/回归门：未积累两个完整周窗或缺少 F007 审计事件时，任何 L2 转换必须失败；两个周窗满足判据后才允许转换。

### F003-R008：生成目标遗漏 PRD 强制的成本后收益
`High | correctness | root-cause | spec-drift`

- 证据：PRD FR2.3 要求同时考虑预测证据、换手、可达性和成本后收益 [alphamill-prd.md:157](/home/georg/projects/alphamill/docs/alphamill-prd.md:157)。规格 FR-005 只保留预测证据与换手 [spec.md:197](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:197)，设计 objective 也只有换手与交易数 [design.md:110](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:110)。
- 建议修复：增加非裁决性的版本化成本代理及其参数；明确这只是生成目标，不产生 F007 verdict。
- 文档/回归门：两个预测证据相同、换手成本不同的候选，净成本代理更差者不得优先；运行记录必须保存成本模型版本和参数。

### F003-R009：协同池被设计为独立 `AlphaPoolDef`，不是要求的 FactorDef
`High | correctness | root-cause | spec-drift`

- 证据：FR-007 明确要求 meta-factor 是 FactorDef [spec.md:227](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:227)。设计却把它写成独立 `pool.json` 与 `AlphaPoolDef` [design.md:97](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:97) [design.md:116](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:116)，不具备通用 FactorDef 的可执行接口。
- 建议修复：将池持久化为标准 FactorDef，成员和权重作为规范化定义字段；附加 pool metadata 可以保留，但不能替代 FactorDef。
- 文档/回归门：仅通过通用 FactorDef reader 加载并执行池；不调用 pool 专用 API；成员或权重变化必须产生新 factor ID。

### F003-R010：可复现性缺少规范化配置和确定性执行契约
`High | correctness | root-cause | spec-drift`

- 证据：DR-001 要求持久化配置摘要 [spec.md:239](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:239)，NFR-003 把配置摘要纳入重跑身份 [spec.md:259](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:259)。设计的 GenerationRun 字段没有规范化配置或摘要 [design.md:110](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:110)，并仅凭 seed 声称可重算相同集合 [design.md:189](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:189)。
- 建议修复：冻结规范化配置 artifact/digest，并明确 RNG、确定性算子、并行度、排序与 tie-break 规则；若只保证同设备重现，应把设备加入语义前提。
- 文档/回归门：独立冷进程重跑得到同一集合和池顺序；配置任一语义字段变化导致运行身份变化；CPU/GPU 不保证一致时必须显式拒绝跨设备等价声明。

### F003-R011：CLI 文法不能构造它声明的必需请求
`Medium | correctness | root-cause | spec-drift`

- 证据：`GenerationRequest` 强制需要 binding、seed、window、config、quota [design.md:124](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:124)。但 `smoke --day` 没有 binding 参数却以缺绑定为拒绝条件，`seed` 也没有 seed/window/quota 或明确定义的默认值 [design.md:148](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:148)。
- 建议修复：给四个子命令写完整参数语法、默认值来源、互斥项和稳定退出码；所有隐式默认必须进入配置摘要。
- 文档/回归门：CLI 参数矩阵测试覆盖最小成功命令、每个必填项缺失、未知 schema、冲突开关和稳定退出码。

### F003-R012：GenerationRun 漏掉强制 `schema_version`
`Medium | test-coverage | root-cause | spec-drift`

- 证据：IR-003 要求 GenerationRun 和 FactorDef 都带 `schema_version` [spec.md:253](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:253)。设计只为 FactorDef 声明版本 [design.md:102](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:102)，GenerationRun 字段没有该项 [design.md:110](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:110)，AC 映射也未覆盖 IR-003。
- 建议修复：给 run、factor、pool 及必要事件 envelope 明确独立 schema version 和兼容策略。
- 文档/回归门：缺版本或未知版本读取失败；受支持旧版本按明确迁移规则读取；AC 增加 IR-003 追踪。

### F003-R013：HypothesisDef 遗漏 PRD 的“适用状态”
`Medium | correctness | root-cause | spec-drift`

- 证据：PRD FR2.1 要求记录适用状态 [alphamill-prd.md:153](/home/georg/projects/alphamill/docs/alphamill-prd.md:153)。规格 DR-003 [spec.md:241](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md:241) 和设计 HypothesisDef [design.md:108](/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md:108) 均未包含该字段。
- 建议修复：增加版本化的 `applicable_regimes`/`applicable_states`，未知机制必须显式记录 unknown，而不是省略。
- 文档/回归门：schema 拒绝字段缺失；人工种子保存明确状态；自动候选保存显式 unknown。

验证状态：未编辑或创建文件，未检查实现代码；最终仍为 `main@a333394` clean。下一步：先修复 R001–R010，再按 review-convergence 做 Round 2 `diff-only` 复核。
