---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f5f9a1cf7ffemPxb4yILEhSmY0"
title: "设计稿布局与流水线7节点审视建议"
project: "/home/georg/projects/alphamill"
model: "deepseek-flash"
created_at: "2026-09-14T14:50:26Z"
updated_at: "2026-09-14T14:56:19Z"
tokens_input: 100259
tokens_output: 5415
cost: 0.0505
---

# 设计稿布局与流水线7节点审视建议

## user · 2026-09-14T14:50:27Z

<system-reminder>Note: The user selected #20 from "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md". ``` ```

 This may or may not be relevant to the current task.</system-reminder>

当前项目的设计稿审视一下，看看从大的布局层面来看有哪些建议呢，还有总览里的动态流水线里的7个节点我觉得也需要审视一下，我总觉得不是很正式，你深入分析一下这个项目的重要节点和关注点和核心指标

## assistant · 2026-09-14T14:50:27Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `glob({"pattern": "docs/features/0.2/F004-kronos-inference-runtime/**/*"})`


> [reasoning] Let me understand the user's request. They're asking in Chinese:

"当前项目的设计稿审视一下，看看从大的布局层面来看有哪些建议呢，还有总览里的动态流水线里的7个节点我觉得也需要审视一下，我总觉得不是很正式，你深入分析一下这个项目的重要节点和关注点和核心指标"

Translation:
"Review the current project's design draft. From a big-picture layout perspective, what suggestions are there? Also, the 7 nodes in the dynamic pipeline in the overview section — I think they're not very formal/professional. Please do an in-depth analysis of this project's important nodes, focus points, and core metrics."

So this is an evaluation/review task. The user selected #20 from `/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md`. This might be a design document mockup (possibly HTML design draft of a dashboard). Let me first explore the project to understand what's going on.

The user mentions:
1. "当前项目的设计稿" — the design draft of the current project
2. "总览里的动态流水线里的7个节点" — the 7 nodes in the dynamic pipeline in the overview page
3. "重要节点和关注点和核心指标" — important nodes, focus points, core metrics

This sounds like there's an HTML design mockup or frontend design somewhere in the project with a "总览" (overview) page that has a dynamic pipeline visualization with 7 nodes.

Let me explore the project structure first to understand what we're dealing with. This is an evaluation/analysis task - per my intent gate:

Intent: Evaluation/Analysis — "审视一下" (review), "看看...有哪些建议" (see what suggestions), "深入分析" (deep analysis). This is NOT implementation. I should analyze and propose, then wait for confirmation.

Let me start by exploring the project:
1. Read CLAUDE.md to understand project conventions
2. Find the design.md file mentioned
3. Find the design mockup (likely HTML) with the overview page and pipeline
4. Analyze

Let me fire off parallel exploration. First let me do some quick reconnaissance myself to understand the structure, then possibly fire explore agents.

Given the complexity, I'll start with:
- Read CLAUDE.md
- Glob for design files in the F004 directory
- Look at the design.md file

Let me do these in parallel.

Actually, let me think about what "设计稿" means here. It could be:
1. A static UI mockup (HTML/CSS) of what the app should look like
2. The design document (design.md)

The user mentions "总览里的动态流水线里的7个节点" — the overview page's dynamic pipeline with 7 nodes. This strongly suggests a UI mockup (HTML file) with a dashboard. The F004-kronos-inference-runtime design.md line 20 was selected — maybe the design.md contains a description of a UI, or references an HTML mockup.

Let me explore. I'll:
1. Read the design.md file
2. Glob the F004 directory
3. Read CLAUDE.md

In parallel.
I detect evaluation/analysis intent — you want a design review of the project's mockup, focusing on big-picture layout, the 7-node dynamic pipeline in the overview, and a deeper analysis of important nodes/focus areas/core metrics. My approach: explore the design docs and mockup first, analyze deeply, then report findings with proposals — no implementation until you confirm.

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
9: updated: 2026-09-12
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
20: - **执行环境**：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）
21: - **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取
22: 
23: ## 1. 技术概要
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
12: - `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射） / 0005 呈现与观测架构 / 0006 证据边界与实验身份 / 0007 研究快照绑定（dataset 独立版本 + ResearchSnapshot）。
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-crypto 资产清算迁移操作手册（F001 附属）。
14: - `doc
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/design.md
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then conti
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:50:34Z

- **tool**: `glob({"pattern": "docs/design/**/*"})`
- **tool**: `bash({"command": "ls -la docs/design/ docs/design/ui-mockup/ 2>/dev/null"})`


> [reasoning] The user selected line 20 of the design.md, which is empty/whitespace, but the key clue is "总览里的动态流水线里的7个节点" — "the 7 nodes in the dynamic pipeline in the overview". This must refer to the UI mockup at `docs/design/ui-mockup/` mentioned in CLAUDE.md:

> `docs/design/ui-mockup/`：呈现层视觉原型（终局四面全景蓝图，非契约、非 F005 范围；见 ADR-0005 决策 7）。

So the "设计稿" (design draft) is in `docs/design/ui-mockup/`. Let me explore that directory. The user wants:
1. Big-picture layout review of the design draft
2. Review of the 7 nodes in the dynamic pipeline in the overview (总览)
3. Deep analysis of the project's important nodes, focus points, and core metrics

Let me look at the ui-mockup directory first.
The design draft is at `docs/design/ui-mockup/` (per CLAUDE.md). Let me explore it and the related ADR.

  <details><summary>tool output</summary>

  ```text
Found 4 file(s)

/home/georg/projects/alphamill/docs/design/ui-mockup/README.md
/home/georg/projects/alphamill/docs/design/ui-mockup/app.js
/home/georg/projects/alphamill/docs/design/ui-mockup/styles.css
/home/georg/projects/alphamill/docs/design/ui-mockup/index.html
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
docs/design/:
total 12
drwxr-xr-x 3 georg georg 4096 Sep 13 02:25 .
drwxr-xr-x 7 georg georg 4096 Sep 14 21:48 ..
drwxr-xr-x 2 georg georg 4096 Sep 14 01:22 ui-mockup

docs/design/ui-mockup/:
total 100
drwxr-xr-x 2 georg georg  4096 Sep 14 01:22 .
drwxr-xr-x 3 georg georg  4096 Sep 13 02:25 ..
-rw-r--r-- 1 georg georg  9273 Sep 14 01:52 README.md
-rw-r--r-- 1 georg georg 42670 Sep 14 01:51 app.js
-rw-r--r-- 1 georg georg 14559 Sep 14 01:38 index.html
-rw-r--r-- 1 georg georg 16838 Sep 14 01:38 styles.css


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:50:38Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/design/ui-mockup/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/design/ui-mockup/index.html"})`


> [reasoning] Found the UI mockup. Let me read all four files:
- README.md (9KB)
- index.html (14.5KB) — has the 7 nodes in the overview pipeline
- app.js (42KB)
- styles.css (16.8KB)

Let me read them all in parallel. Also I should read ADR-0005 (presentation & observability decision) and the PRD for core metrics understanding. Let me first read the mockup files.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/design/ui-mockup/README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [design, ui, mockup]
3: doc_kind: note
4: created: 2026-09-13
5: updated: 2026-09-13
6: ---
7: 
8: # AlphaMill Console — UI 交互设计稿说明
9: 
10: 配套文件：[`index.html`](./index.html) + [`styles.css`](./styles.css) + [`app.js`](./app.js)。
11: 浏览器直接打开 `index.html` 即可评审，支持 `#factors`、`#detail`、`#strategy` 等 hash 深链直达单页。
12: 
13: ## 定位
14: 
15: - 这是 **终局自建版**设计稿：按 ADR-0005 的自建前端路线绘制，不代表 Grafana/FreqUI 过渡形态；
16: - 开发可后置（F005 立项后实施），但信息架构与数据契约以本稿为准；
17: - **全部数字为占位假数据**，仅用于传达布局与信息密度，不表征任何真实回测/运营结果；
18: - UI 内不承载设计元注释，全部说明集中在本文档（设计稿即最终交付形态）。
19: 
20: ## 设计方向：简洁高效
21: 
22: - 浅色中性底（`#f6f7f8`）+ 白色卡片 + 细边框，无渐变、无重阴影、无装饰性纹理；
23: - **单强调色**（蓝 `#2563eb`）用于导航选中、主按钮、图表主线；语义色只保留两类：
24:   绿 `#1580
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/design/ui-mockup/index.html</path>
<type>file</type>
<content>
1: <!DOCTYPE html>
2: <html lang="zh-CN">
3: <head>
4: <meta charset="UTF-8">
5: <meta name="viewport" content="width=device-width, initial-scale=1.0">
6: <title>AlphaMill Console</title>
7: <link rel="stylesheet" href="styles.css">
8: </head>
9: <body>
10: 
11: <header>
12:   <div class="brand">AlphaMill <span>淘沙</span></div>
13:   <div class="top-cell">环境 <b>DRY-RUN</b></div>
14:   <div class="top-cell">数据版本 <b class="mono">v2026.09.12</b></div>
15:   <div class="top-cell">成本模型 <b class="mono">cm-v1</b></div>
16:   <div class="top-cell" style="margin-left:auto; border-right:none;">UTC <b id="clock">--:--:--</b></div>
17: </header>
18: 
19: <nav id="nav">
20:   <div class="nav-item act
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:50:40Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/design/ui-mockup/app.js"})`


> [reasoning] Now let me read app.js (42KB) to see the overview flow-anim node definitions — the 7 nodes for the dynamic pipeline. Also styles.css. Let me read both.
Now the key file — app.js (contains the pipeline animation with 7 nodes) and styles.css:

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/design/ui-mockup/app.js</path>
<type>file</type>
<content>
1: /* AlphaMill Console 设计稿 — 交互与假数据渲染
2:    全部数字为占位假数据；生产实现中每个渲染函数对应一个只读 API 端点（ADR-0005）。 */
3: 
4: "use strict";
5: 
6: /* ── 工具 ─────────────────────────────── */
7: function mulberry32(seed) {
8:   return function () {
9:     seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
10:     let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
11:     t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
12:     return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
13:   };
14: }
15: 
16: function series(seed, n, drift, vol, base) {
17:   const rnd = mulberry32(seed);
18:   const out = [];
19:   let v = base;
20:   for (let i = 0; i < n; i++) {
21:     v += drift + (rnd() - 0.5) * vol;
22:     out.push(v);
23:   }
24
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:50:43Z

- **tool**: `bash({"command": "wc -l docs/alphamill-prd.md docs/alphamill-architecture.md docs/decisions/0005-presentation-observability.md docs/SOP.md docs/design/ui-mockup/styles.css 2>/dev/null; echo \"---\"; ls docs/decisions/ docs/reviews/ 2>/dev/null"})`


> [reasoning] Now I have the full picture of the mockup's app.js. The 7 nodes in the overview pipeline (`OVERVIEW_FLOW`) are:

1. 生成 (128 本周产出, 存量提案 214)
2. 评测 (89 评测中, 本周初筛淘汰 81)
3. 选择期 (47 存续, 180 天窗口 · 查重通过)
4. 组合 (12 组合验证中, 边际贡献评估 + 冻结)
5. 验证 (17 留出 + 最终确认, 每周晋级上限 5)
6. 上线 (5 已挂载因子, PM-007 · PM-009 dry-run)
7. 监控 (18 监控中因子, PnL +6.42% · 衰减 41 · 停用 96)

This is what the user says "不是很正式" (not very formal/professional). They want me to deep-analyze the project's important nodes, concerns, and core metrics.

Now let me read:
1. `styles.css` for layout
2. `docs/decisions/0005-presentation-observability.md` (ADR-0005)
3. The PRD (`docs/alphamill-prd.md`) for the core metrics - FR1-FR8, metrics system
4. The architecture doc (`docs/alphamill-architecture.md`) for the lifecycle and important nodes

Let me also check the "FR3.4" validation order mentioned. The key question: are the 7 pipeline stages consistent with PRD/architecture lifecycle? Are the metrics correct/formal?

Let me read the PRD and architecture. These are likely large files. Let me check their sizes first, or just read them. I'll read styles.css + ADR-0005 first, then PRD + architecture.

Actually, let me be smart about context. The PRD and architecture are probably big. Let me check file sizes and then read.
The 7 overview nodes are in `OVERVIEW_FLOW` (app.js:602-610). Now I need the authoritative sources — PRD metrics, architecture lifecycle, ADR-0005 — to judge whether the pipeline nodes and metrics are the *right* ones. Let me check sizes then read.

  <details><summary>tool output</summary>

  ```text
309 docs/alphamill-prd.md
  577 docs/alphamill-architecture.md
   97 docs/decisions/0005-presentation-observability.md
  113 docs/SOP.md
  419 docs/design/ui-mockup/styles.css
 1515 total
---
docs/decisions/:
000-template.md
0001-factor-mining-engine.md
0002-external-dependency-policy.md
0003-validation-gate-non-degradation.md
0004-portfolio-construction.md
0005-presentation-observability.md
0006-evidence-boundary-and-experiment-identity.md
0007-research-snapshot-binding.md

docs/reviews/:
CURRENT-doc.md
RETROSPECTIVE.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:50:47Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md"})`

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
1: # AlphaMill — 产品需求文档（PRD）
2: 
3: > 版本：v0.1 | 日期：2026-09-13 | 状态：草案
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

## assistant · 2026-09-14T14:50:49Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md"})`


> [reasoning] Now I have the full PRD. Let me read the architecture doc, ADR-0005, and styles.css to understand the layout, then I can do the deep analysis.

Key observations already:

**The 7-node pipeline (overview) is**: 生成 → 评测 → 选择期 → 组合 → 验证 → 上线 → 监控

**From PRD §2.3 漏斗健康 (funnel health)**: 生成 → 纯度门 → 因子证据/成本门 → 去重/多重检验 → 选择期 → 组合门（冻结 PortfolioDef）→ 留出门（含样本量三级裁决）→ 最终确认 → 部署前复核

**From FR3.4 验证顺序**: FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef → PortfolioDef 最终 90 天留出 → 永久隔离最终确认窗

**From FR6.2 生命周期**: proposed/evaluating/validated/champion/challenger/monitoring/decayed/disabled

So the key review points for the 7 nodes:

1. The mockup's 7 macro stages are: 生成、评测、选择期、组合、验证、上线、监控 — while the README says "生成 → 评测（含纯度/成本/查重子门）→ 选择期 → 组合 → 验证（留出 90 天 + 最终确认）→ 上线（部署复核 + 挂载）→ 监控" and claims it aligns with "PRD FR3.4 的验证顺序".

Issues I can spot:

1. **"验证" node merges 留出 and 最终确认** — but PRD treats 留出 (90-day holdout with 3-level sample size adjudication) and 最终确认 (permanently isolated final confirmation window) as two separate gates, with 部署前复核 (pre-deployment review) as a third. The overview "验证" node says "留出 + 最终确认" and "每周晋级上限 5". This conflates them.

2. **"上线" node** — the mockup labels 5 已挂载因子; but there's an inconsistency: earlier "组合验证中" card in factory says 12, "其中最终确认 5"; the OVERVIEW_FLOW says 验证 num 17, 上线 num 5. Wait:
   - OVERVIEW_FLOW: 生成 128, 评测 89, 选择期 47, 组合 12, 验证 17, 上线 5, 监控 18.
   - But STAGES (factory pipeline distribution) says: 提案 214, 评测中 89, 选择期 47, 留出验证 12, 最终确认 5, Champion 2, Challenger 3, 监控 18, 衰减 41, 停用 96.
   - And the factory cards say: 本周产出 128 候选, 初筛存活 47, 组合验证中 12 (留出验证 90 天 · 其中最终确认 5), 在跑与监控 2 Champion, Challenger 3, 监控 18, 有效独立数 23.
   
   So there are **inconsistencies**: 组合 12 vs 组合验证中 12; 验证 17 vs (留出验证 12 + 最终确认 5 = 17); 上线 5 vs (Champion 2 + Challenger 3 = 5); 监控 18 vs 监控 18. OK so 验证 = 12+5 = 17, 上线 = 2+3 = 5. These are consistent actually (sums). But semantically weird: "上线" shows 5 (champion+challenger) — but 监控 18 includes champions? The mockup says 监控中因子 18, but STAGES says 监控 18. Hmm, Champion 2 + Challenger 3 = 5 mounted, and 监控 18. But 上线 = "已挂载因子" labeled 5, extra "PM-007 · PM-009 dry-run". 

   Wait, but in the factory card: "在跑与监控 2 Champion · Challenger 3 · 监控 18 · 有效独立数 23". So 在跑与监控 total: 2+3+18 = 23? That's a coincidence with 有效独立数 23 — actually it looks like they're conflating "监控" count with "有效独立数". That's a metrics mixing problem. 有效独立数 is the number of effective independent candidates (OOS PnL clustering), not the count of monitored factors. Actually in the mockup, both are 23 — suspicious.

3. **Numbers flow/topology logic issues:**
   - 生成 128 "本周产出" → 评测 89 — but 评测 should be cumulative (存量提案 214). Flows: "本周产出 128" while factory card says 128 候选 this week; batch B-20260912 has 124 candidates. 128 vs 124 — inconsistent between overview (128) and 昨夜产出 (124). Actually the sub in 昨夜产出 says "B-20260912 · 124 候选", and 因子工厂 says 本周产出 128 (本周 = multiple batches; B-20260912 has 124, so 128 could be week total — plausible but confusing).
   - 评测 89 "评测中" → but 初筛存活 47 and "本周初筛淘汰 81". 89 评测中 + 81 淘汰 this week = 170, doesn't match 128 本周产出. Hmm, 89 is existing stock in evaluation, 81 eliminated this week. OK-ish.
   - 组合 12 "组合验证中" with extra "边际贡献评估 + 冻结" — but 组合 stage should be "构建并冻结 PortfolioDef", and 12 with "组合验证中"... The factory card says "组合验证中 12 · 留出验证 90 天 · 其中最终确认 5" — this is confusing: 组合验证 in portfolio world, but the card mixes 留出验证 90 天 into 组合验证中.
   - 验证 17 "留出 + 最终确认" — should be reported separately (留出 12 / 最终确认 5).
   - 上线 5 "已挂载因子" — but the stage between 最终确认 and 监控 in FR5.2 is 部署前复核 (pre-deployment review), then 挂载 dry-run. And lifecycle states champion/challenger. The mockup "上线" = 5 (2 champion + 3 challenger); but then 监控 18 — what are these 18? If we have 2 champions and 3 challengers mounted, what does 监控 18 mean vs 衰减 41, 停用 96? In STAGES, 监控 18, 衰减 41, 停用 96 are separate bars. But OVERVIEW_FLOW 监控 = "监控中因子" 18 with extra "PnL +6.42% · 衰减 41 · 停用 96".
   
   Then the flow of the animation: particles flow from 生成 through to 监控, and 淘汰粒子 fall from stages 1,2,3,4,6 (FALL_FROM = [1, 2, 3, 4, 6] — 评测, 选择期, 组合, 验证, 监控). Note: no rejections from 生成 (fine) and 上线 (fine—probably), but also what about 监控 → 衰减/停用? Decayed particles fall to evidence pool from 监控 (m=6 with amber color). OK.

   But wait — there's a subtle issue: the fall from 验证 (m=4) and 组合 (m=3) counts as "淘汰" — however rejections at 留出门 aren't exactly "淘汰" in evidence-library terms... Actually the README says "证据库托盘（评测/选择期/组合/验证/监控的淘汰粒子均落入——对齐架构生命周期图「所有拒绝点进证据库 X」）". Let me check the architecture's lifecycle diagram for "所有拒绝点进证据库" to verify.

4. **The "证据库 · 归因复盘" strip**: "累计淘汰 306 · 本季复盘 12 次 → 新假设入队 9（generation +1）". Note in the factory batches: 淘汰 64 + 成本否定 17 for latest batch. 306 cumulative maybe.

5. **Missing nodes from PRD funnel**: 纯度门, 成本门, 查重/多重检验 are sub-gates of 评测 in the mockup (fine per design decision). But the arguably most important gate — 部署前复核 (FR5.2) — is squeezed into 上线. And 最终确认 (permanent isolation window) is squeezed into 验证. These are hard-gate semantics: 留出 = 90-day, 最终确认 = permanent isolation, new PortfolioDef consumes budget. Making them one "验证" node risks losing the "验证预算" (weekly cap of 5) and the "隔离" semantics.

6. **Lifecycle states not aligned**: PRD FR6.2 states: proposed/evaluating/validated/champion/challenger/monitoring/decayed/disabled. Mockup uses: 生成/评测/选择期/组合/验证/上线/监控 — that's the research pipeline. But the display in 因子库 filters "结论" uses promising/weak/dead/decayed — different vocabulary again. And badges: 淘汰/成本否定 in batches; verdict: promising/weak/dead/decayed; lifecycle: champion/challenger/monitoring/decayed/disabled.

7. **核心指标 review** — the PRD's 指标体系 (§2.3):
   - 北极星: 可信 Alpha 产出 (rolling 28d new effective independent PortfolioDefs)
   - 转化效率: 研究到证据周期, 证据到部署周期
   - 探索能力: 有效独立假设吞吐量 (名义 ≥100/周 + effective independent)
   - 漏斗健康: 分级转化率 (生成 → 纯度门 → 证据/成本门 → 去重/多重检验 → 选择期 → 组合门 → 留出门 → 最终确认 → 部署前复核)
   - 线上结果: 组合运行质量
   - 信任护栏: 数据与实验完整性

   The mockup's overview shows: 策略执行 (PNL), 信号与数据 (IC), 昨夜产出 — plus the pipeline. Missing from the overview: **北极星指标 (可信 Alpha 产出)**, 有效独立数 (buried in factory card as auxiliary), 漏斗最大流失级 (FR3.8 requires weekly report identifies it), 无前视/留出预算消耗 (weekly cap), 研究到部署周期. The pipeline DOES show stage conversion, but is missing the "weekly cap" consumption (每周晋级上限 5) and the holdout budget semantics.

   Also FR7.5 requires 周报 outputting 北极星领先指标、cohort 漏斗、有效独立数、来源多样性、资源消耗、五阶段损失、线上偏差和最大约束. "五阶段损失" — interesting, what are the 五阶段? Let me check architecture. Probably 信号质量、组合转换、成本/容量、时序稳定、执行实现 — the failure_stage dimensions from FR6.3. So the "五阶段损失" is a key metric dimension that could be reflected in the overview.

8. **The user's complaint "不是很正式" (not formal enough)**: The 7 nodes with particles + "落站脉冲" (pulse) animations may feel playful/game-like ("gamified"). For a quant research console, the pipeline should communicate stage inventory + flow semantics + gates, with hard-gate semantics visible (budget consumption, isolated windows). The animation may be decorative rather than informative. Also there's no time dimension (e.g., 7-day flow) — a Sankey-like daily/weekly flow with rejection destinations might be more "formal". Or simply a cleaner stage table/matrix with formal funnel metrics.

Let me now read the architecture doc and ADR-0005 + styles.css. Then I'll also check what "验证顺序" and the architecture lifecycle diagram look like, especially "所有拒绝点进证据库 X" — hmm wait, actually let me grep for 证据库 in architecture.

Also the design.md of F004 was the selected file — its line 20 is just blank; the user probably selected it accidentally or the pipeline relates. Actually the user message includes the system reminder that they selected #20 from F004 design.md — but that seems unrelated to the mockup review. It's probably just context noise. The real task: review the design mockup (设计稿).

Wait — maybe "设计稿" refers specifically to design.md? No... "总览里的动态流水线里的7个节点" — the 7 nodes are in the UI mockup overview (OVERVIEW_FLOW has exactly 7 nodes). So the 设计稿 = ui-mockup. Confirmed.

Let me read architecture + ADR-0005 + styles.css now. Architecture is 577 lines — readable.
Now the architecture doc (lifecycle, evidence library, metrics) and ADR-0005:

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

## assistant · 2026-09-14T14:51:05Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0005-presentation-observability.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/design/ui-mockup/styles.css"})`


> [reasoning] Now I have the architecture. Let me read ADR-0005 and styles.css to complete the picture. Then look at the 总览's exact layout more carefully.

Let me read the ADR-0005 and styles.css.
Now ADR-0005 and the styles for layout analysis:

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0005-presentation-observability.md</path>
<type>file</type>
<content>
1: # ADR-0005：呈现与观测架构 —— 真相源/投影/展示三分与自建前端路线
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：呈现层长期路线；PRD FR8 / FR6.1 / FR6.4 / FR7.2 / FR7.4；架构文档 §〇 / §七
7: 
8: ## 背景
9: 
10: 当前呈现面三件：Grafana（`quant-overview` 平台观测 + `dryrun-monitoring` 策略运营，F001
11: 迁入并验收有数）、FreqUI（Freqtrade 镜像自带，`api_server` 已启用）、CLI（`tools/verify.py`
12: 门禁与操作）。三个结构性问题随里程碑逼近：
13: 
14: 1. **研究证据没有承载面**：评测台（FR3）落地后 M2 出口要求周产能 ≥100 候选，版本化报告
15:    靠文件浏览不可持续；架构文档 §五 原计划的「Grafana 实验台账看板」与版本态产物形态
16:    （文件 + 谱系图 + 逐因子下钻）不匹配。
17: 2. **口径被困在看板里**：dashboard JSON 内嵌 SQL 会持续积累业务口径（成本后收益、胜率、
18:    延迟判定等），更换呈现工具即全部重写；且新旧两套实现并存期必然漂移——「哪个数字是
19:    真的」在量化系统中是不可接受的风险。
20: 3. **工具边界不清**：FreqUI（执行显微镜）、Gr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/design/ui-mockup/styles.css</path>
<type>file</type>
<content>
1: /* ALPHAMILL Console — 简洁高效设计系统
2:    浅色中性底 + 单强调色；语义色仅用于收益(绿/红)与告警(琥珀)；
3:    口径不进前端，UI 不承载任何设计元注释（见 README.md）。 */
4: 
5: :root {
6:   --bg: #f6f7f8;
7:   --panel: #ffffff;
8:   --border: #e5e7eb;
9:   --border-2: #d1d5db;
10:   --text: #111827;
11:   --text-2: #6b7280;
12:   --text-3: #9ca3af;
13:   --accent: #2563eb;
14:   --accent-weak: #eff6ff;
15:   --hover: #f4f5f6;
16:   --green: #15803d;
17:   --green-bg: #f0fdf4;
18:   --green-line: #10b981;
19:   --red: #dc2626;
20:   --red-bg: #fef2f2;
21:   --amber: #b45309;
22:   --amber-bg: #fffbeb;
23:   --radius: 8px;
24:   --shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
25:   --font: -apple-system, "Segoe UI", "PingFang SC", "Hiragino 
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:51:07Z

- **tool**: `bash({"command": "ls docs/features/0.2/ docs/features/0.1/ 2>/dev/null; echo \"---\"; cat BACKLOG.md 2>/dev/null | head -60"})`


> [reasoning] Now I have a complete picture. Let me also check the F005/F007 specs briefly to understand what exists, and the BACKLOG to know which features exist. Actually let me quickly check what F005 spec says about the mockup, and check if there's a "总览" view defined anywhere. Let me also verify: the user says "总览里的动态流水线里的7个节点我觉得不是很正式" — the 7 nodes in the overview:

1. 生成 (128, 本周产出, 存量提案 214)
2. 评测 (89, 评测中, 本周初筛淘汰 81)
3. 选择期 (47, 存续, 180 天窗口 · 查重通过)
4. 组合 (12, 组合验证中, 边际贡献评估 + 冻结)
5. 验证 (17, 留出 + 最终确认, 每周晋级上限 5)
6. 上线 (5, 已挂载因子, PM-007 · PM-009 dry-run)
7. 监控 (18, 监控中因子, PnL +6.42% · 衰减 41 · 停用 96)

Let me now think deeply about the user's three asks:
1. 大布局层面的建议 (big-picture layout suggestions)
2. 动态流水线 7 nodes review (formal/professional)
3. 深入分析项目的重要节点、关注点、核心指标 (deep analysis of important nodes, concerns, core metrics)

Let me do a careful analysis. Since this is a design review, I should reference authoritative sources (PRD §2.3, FR3.4, FR3.5, FR6.2, architecture lifecycle §2.2, ADR-0005, F007). Let me also check F007 spec quickly since "统一评测台与证据门禁" is active — it may define the canonical funnel/verdict vocabulary. Also check F005 — 研究控制台 spec exists? In BACKLOG, F005 may not yet exist. CLAUDE.md says F004 + F007 are the active ones. The docs/README says "F005 spec 落地后废弃或迁入 web/" — so F005 is planned. Let me check BACKLOG.
Let me check the active feature specs (F007 evaluation gates) and BACKLOG for the vocabulary that the console must align with:

  <details><summary>tool output</summary>

  ```text
docs/features/0.1/:
F001-quant-crypto-migration
README.md

docs/features/0.2/:
F002-data-bridge
F003-alphagen-vendor
F004-kronos-inference-runtime
F007-evaluation-gates
F008-universe-expansion
---
# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F003-alphagen-vendor | 0.2 | draft | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
| F004-kronos-inference-runtime | 0.2 | draft | [spec](docs/features/0.2/F004-kronos-inference-runtime/spec.md) |
| F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
| F008-universe-expansion | 0.2 | draft | [spec](docs/features/0.2/F008-universe-expansion/spec.
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:51:11Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`


> [reasoning] Let me quickly read F007 spec to understand the canonical pipeline vocabulary (stages, verdicts, cohort gates), which is directly relevant to reviewing the pipeline nodes' "formality". F007 is "统一评测台与证据门禁".

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

## assistant · 2026-09-14T14:51:14Z

- **tool**: `list_mcp_resources({})`


> [reasoning] Now I have a comprehensive understanding. Let me now do a serious deep analysis. The user wants:

1. **大布局层面 (big layout) suggestions** — for the whole mockup
2. **动态流水线 7 节点 review** — are they "formal"/professional?
3. **深入分析项目的重要节点、关注点、核心指标** — deep analysis of important nodes, concerns, core metrics

Let me now think about this as a systematic design review. I should probably also consult the Oracle? The instruction says for complex architecture design → Oracle. This is an evaluation task, not implementation. I could consider firing Oracle to review, but I have enough context to formulate the analysis myself. Actually, per my system prompt, for high-quality reasoning I could consult Oracle. But this is a design-review analysis task where the key input is project-internal docs I've already read thoroughly. The Oracle would need to read many docs. Hmm. Let me consider: the user asked for a deep review with suggestions. This is my core competency area (design critique). I think I can do this directly — but it's also a substantial analysis where a second opinion from Oracle could help. Let me think about whether to fire Oracle.

Actually, per my instructions: "Complex architecture design" → consult Oracle. This is not architecture design, it's a UI design review focused on information architecture. I've read all relevant materials (PRD, architecture, ADRs, mockup code). I can synthesize the review myself. The user wants my analysis now. Firing Oracle would add latency for marginal benefit since Oracle doesn't have the full context that I have gathered; I'd need to give it the full mockup + PRD excerpt. Hmm, it could still be valuable — a design review from a different angle. But let me keep it simple: the user asked me to analyze; I'll do the analysis. I can offer to use Oracle for verification if needed. Actually, let me reconsider — the instruction says "Work, delegate, verify, ship" and "Oracle - WHEN to Consult: Complex architecture design". This is design review, borderline. Given the user asked for "深入分析" (deep analysis), and this involves reconciling the mockup with PRD/architecture/ADRs — I have all the facts. I'll do it myself. 

Wait, but there's a strong bias in my system prompt to delegate. For analysis tasks like this, though, the value is in the synthesis which I've already done the reading for. Subagents wouldn't have my accumulated context unless I pass huge prompts. The pragmatic approach: do the analysis well. The user wants a review outcome, not code.

Let me check the mockup in a browser to see it visually? I could take a screenshot with Playwright to assess the layout properly. The user asks about "大布局层面" (big layout level). Visual inspection would help. Let me check if playwright is available. Actually, the skill mentions playwright MCP for browser tasks. Let me try to open the mockup and take screenshots — that would ground my layout review. Let me check if the playwright MCP tool is available via skill_mcp.

The available tools include `skill_mcp` with playwright — "MUST USE for any browser-related tasks. Browser automation via Playwright MCP". Let me check if I can use it. The skill list includes `/playwright` builtin. I can load it. But wait, the skill_mcp tool requires mcp_name. Let me see if playwright MCP is actually available. Let me first try loading the playwright skill or check MCP servers. 

Actually let me think about whether visual review is needed. The user selected the design and asked about layout suggestions + the 7 nodes. I have the code, so I know exactly the layout: header (brand + env + data_version + cost_model + UTC clock), left nav (4 items: 总览/监控/因子/设置), main with views. The overview = pipeline animation card + 3 cards (策略执行/信号与数据/昨夜产出). The visual inspection could reveal issues like the pipeline overflowing, but I can reason from the code.

Taking screenshots would be a nice addition for verification. Let me try — if playwright is available, screenshot the overview page. That would let me give a fully-grounded layout review. Let me check.

Actually, let me first check the playwright skill. The `skill` tool has `/playwright`. Let me invoke it to see instructions. Hmm, but that may set up a big MCP flow. Let me check if there's an existing playwright MCP available via skill_mcp. Actually the instructions say "skill_mcp ... Requires mcp_name plus exactly one of: tool_name, resource_name, prompt_name". Let me try checking whether the playwright server is configured by listing MCP resources. Let me do `list_mcp_resources` — that shows connected MCP servers. Let me try that quickly.

Actually — to keep scope tight, let me try a quick screenshot attempt. If it works, great; if not, proceed with code-based analysis. Let me check MCP servers first.
I have the full picture from the docs. Let me verify the actual rendering — a visual check of the mockup will ground the layout review. Checking if a browser tool is available:

  <details><summary>tool output</summary>

  ```text
{
  "resources": [
    {
      "name": "tools_list",
      "uri": "exa://tools/list",
      "description": "List of available Exa tools and their descriptions",
      "mimeType": "application/json",
      "server": "websearch"
    }
  ]
}
  ```
  </details>

## assistant · 2026-09-14T14:51:22Z

- **tool**: `bash({"command": "which playwright chromium google-chrome chromium-browser 2>/dev/null; ls ~/.cache/ms-playwright 2>/dev/null | head; node -e \"try{require.resolve('playwright');console.log('playwright module OK')}catch(e){console.log('no playwright module')}\" 2>/dev/null"})`


> [reasoning] Playwright MCP isn't connected. Let me check the playwright skill to see how it's set up. Actually, let me just try loading the builtin playwright skill - it may instruct to use skill_mcp with a specific mcp name.

Actually, simpler: let me check if playwright is installed locally and take a screenshot with a quick script. Let me check for node/npx playwright availability.

  <details><summary>tool output</summary>

  ```text
playwright not found
chromium not found
google-chrome not found
chromium-browser not found
chromium-1234
chromium_headless_shell-1234
ffmpeg-1011
no playwright module


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:51:25Z

- **tool**: `bash({"command": "python3 -c \"import playwright; print('py playwright OK')\" 2>/dev/null; npm ls -g --depth=0 2>/dev/null | head -20; ls ~/.cache/ms-playwright/chromium_headless_shell-1234/ 2>/dev/null"})`


> [reasoning] There are cached playwright browsers (`~/.cache/ms-playwright` has chromium-1234 and chromium_headless_shell-1234). So playwright browsers exist. Maybe there's a global playwright install somewhere, or a project with playwright. Let me check for npx playwright or a global npm installation.

Let me check: `npm ls -g --depth=0` or check if there's a python playwright installed. `python3 -c "import playwright"`. Let me check both.

  <details><summary>tool output</summary>

  ```text
/home/georg/.nvm/versions/node/v24.20.0/lib
├── @anthropic-ai/claude-code@2.1.268
├── @openai/codex@0.154.0
├── corepack@0.35.0
├── mcporter@0.13.12
├── npm@11.19.0
└── zcode-app-cli@3.11.2-22

DEPENDENCIES_VALIDATED
INSTALLATION_COMPLETE
chrome-headless-shell-linux64


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:51:29Z

- **tool**: `bash({"command": "BIN=~/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell; mkdir -p /tmp/opencode/am-shots; cd /home/georg/projects/alphamill/docs/design/ui-mockup && for v in overview factory detail strategy settings; do \"$BIN\" --headless --disable-gpu --no-sandbox --hide-scrollbars --window-size=1680,1050 --virtual-time-budget=2500 --screenshot=/tmp/opencode/am-shots/$v.png \"file://$PWD/index.html#$v\" 2>/dev/null; done; ls -la /tmp/opencode/am
…[truncated])`


> [reasoning] There's a chrome-headless-shell available at `~/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/`. I can use it directly to take screenshots:

```
chrome-headless-shell --headless --screenshot=/tmp/opencode/overview.png --window-size=1600,1000 file:///home/georg/projects/alphamill/docs/design/ui-mockup/index.html#overview
```

Wait, chrome-headless-shell is the old headless shell. It supports `--screenshot` flag. Let me try that. The index.html loads app.js and styles.css relatively — file:// should work. There's a clock that updates via JS. SVG animations need some runtime; for a screenshot that's ok.

Let me try taking screenshots of the overview and maybe factory + detail pages. The hash-based deep links: `#overview`, `#factory`, `#detail`, `#strategy`, `#settings`, `#compare`. Note `gotoView` handles it. For `#detail`, `renderDetail()` uses `selectedFactor` default FACTORS[0].

Let me take screenshots for the main views so I can review layout visually. Use the headless shell binary directly.
Playwright browsers are cached. I'll use the headless shell directly to screenshot the mockup views:

  <details><summary>tool output</summary>

  ```text
total 776
drwxr-xr-x  2 georg georg    140 Sep 14 22:51 .
drwxr-xr-x 12 georg georg   1300 Sep 14 22:51 ..
-rw-r--r--  1 georg georg 171947 Sep 14 22:51 detail.png
-rw-r--r--  1 georg georg 187166 Sep 14 22:51 factory.png
-rw-r--r--  1 georg georg 100186 Sep 14 22:51 overview.png
-rw-r--r--  1 georg georg 174463 Sep 14 22:51 settings.png
-rw-r--r--  1 georg georg 153863 Sep 14 22:51 strategy.png


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-14T14:51:36Z

- **tool**: `read({"filePath": "/tmp/opencode/am-shots/overview.png"})`


> [reasoning] Screenshots captured. Now let me look at them. The most important for this review: overview.png (with the 7-node pipeline), and factory.png for layout. Let me view the overview shot and the factory shot.

I'll use the read tool to view images, or look_at. For visual precision, Read is preferred. Let me read the overview and factory screenshots.

  <details><summary>tool output</summary>

  ```text
Image read successfully
  ```
  </details>

## assistant · 2026-09-14T14:51:37Z

- **tool**: `task({"subagent_type": "multimodal-looker", "description": "Analyze UI mockup screenshots", "prompt": "Analyze these screenshots of a desktop quant-research console UI mockup (Chinese language, light theme design draft):\n\n1. /tmp/opencode/am-shots/overview.png — \"总览\" (Overview) page. KEY FOCUS: the horizontal pipeline diagram at top with 7 circular nodes (生成/评测/选择期/组合/验证/上线/监控), animated particle lane, a purple \"证据库\" tray at bottom, and a feedback arc. Below: 3 cards (策略执行/信号与数据/昨夜产出).\n2. /tmp
…[truncated])`


> [reasoning] I can't view images with this model. Let me instead use the multimodal-looker agent to analyze the screenshots. There's a `multimodal-looker` subagent type for analyzing media. Let me fire it on the screenshots, particularly overview, to describe the layout and identify visual issues.

Actually, let me delegate the visual analysis to the multimodal-looker agent. I'll ask it to describe the layout in detail for the overview page and note any visual/formal issues: spacing, alignment, density, hierarchy, whether the pipeline looks professional, etc.

Let me fire it with multiple image paths. The tool description says "Use when you need analyzed/extracted data rather than literal file contents" — for visual precision, read is better but I can't read images. So multimodal-looker is my only option. Let me give it a focused goal.
I can't view images directly in this model — delegating visual analysis to the multimodal-looker agent:

  <details><summary>tool output</summary>

  ```text
Task completed in 8s.

Agent: multimodal-looker
Model: deepseek/deepseek-flash

---

The read tool is blocked entirely (deny * at the end). I'm told during look_at invocations, the file is already attached to the message. But here the user invoked me directly with file paths, not an attachment. The read tool is denied. Let me check if there are actual attachments in the conversation — no images attached, just paths.

Hmm. The instruction says the file is already attached. But no images present. I cannot read the files due to permission. I should report this clearly.

Wait — maybe I should try reading via a different route? The read tool itself is denied by permission rules. All external directory reads... actually the rule list ends with {"permission":"*","action":"deny","pattern":"*"}. So
…[truncated]
  ```
  </details>

## assistant · 2026-09-14T14:51:52Z

- **tool**: `look_at({"file_paths": ["/tmp/opencode/am-shots/overview.png", "/tmp/opencode/am-shots/factory.png"], "goal": "Describe the visual layout of both screenshots in precise detail. For overview.png (总览 page): describe the horizontal pipeline diagram with 7 circular nodes (生成/评测/选择期/组合/验证/上线/监控), the particle lane, the purple 证据库 tray at the bottom, the feedback arc, and the 3 cards below. Note any misalignment, unbalanced whitespace, tiny text, clipping, or visual hierarchy issues. For factory.png: describe
…[truncated])`


> [reasoning] The multimodal-looker agent couldn't read the files. Let me try using the `look_at` tool directly — it's the dedicated tool for media analysis. The look_at tool accepts `file_paths`. Let me try it directly from the main session. The description says "Extract basic information from media files (PDFs, images, diagrams) when a quick summary suffices". It's available in my tool list. Let me use it.

Actually wait, should I check whether the images are in an allowed location? /tmp/opencode is pre-approved per the bash description. The look_at tool is a main-session tool. Let me try it.
Trying the dedicated `look_at` tool directly:

  <details><summary>tool output</summary>

  ```text
I can't complete this request: the two attachments (overview.png, factory.png) are images, and this model does not support image input. Attempting to read either file returns:

`Cannot read "overview.png" (this model does not support image input)`
`Cannot read "factory.png" (this model does not support image input)`

No visual content was available to me, so I cannot describe the pipeline nodes, particle lane, 证据库 tray, feedback arc, overview cards, stat cards, distribution bars, batch table, factor table, filters, or any alignment/spacing/text-size issues. Inventing those details would be fabrication.

To get the extraction, re-run the request with an image-capable model, or provide a text/HTML/CSS source of the pages (e.g., the component markup), which I can read directly.
  ```
  </details>

## assistant · 2026-09-14T14:52:01Z


> [reasoning] The `look_at` tool routes through the same model (deepseek-flash), which doesn't support image input. So visual analysis of screenshots isn't possible in this session — neither directly nor via the look_at tool. The multimodal-looker subagent also failed due to permissions (read denied) and model limitation.

OK — I'll proceed with a rigorous code-level analysis. I actually have very complete knowledge of the layout from index.html + styles.css + app.js. The exact CSS gives me precise layout facts. I can do the design review from the source, which I've read fully. That's sufficient — I know:

**Layout facts from code:**

Global layout:
- Grid: header row 52px; nav column 212px (collapsible to 56px); main.
- Main: `.view { padding: 24px 28px 48px; max-width: 1400px; }` — Note: max-width 1400px but no margin auto → content is left-aligned, leaving empty space on the right at wide screens. Actually `max-width:1400px` without `margin:0 auto` means at viewport widths > 1400+212=1612px, the content stops at 1400px and leaves dead space on the right. This is a real layout issue (big screens: unbalanced right whitespace). Also no responsive/breakpoints at all (desktop-only design, acceptable for v0.1 self-hosted but worth noting).
- Header: brand + 4 top-cells; env/data version/cost model/UTC clock. Note: 环境 DRY-RUN / 数据版本 / 成本模型 — these are global context indicators. Good.

Overview page (the focus):
- view-head: 总览 + sub.
- One card with padding `6px 8px 0` containing `#flow-anim` SVG: viewBox 1200x268, `width:100%; height:268` — wait, the svg is created as `'<svg width="100%" height="' + H + '" viewBox="0 0 ' + W + ' ' + H + '">'` and preserveAspectRatio default (xMidYMid meet). Width 100%, so the SVG scales to container width and preserves aspect ratio. Container width = 1400 - 2*28 padding? Wait view padding 24px 28px; card inside; card padding 6px 8px. So card inner width ~1400-56-2(border)-16 = ~1326px. SVG viewBox 1200 wide → scales up slightly (1.105x), height stays 268 (fixed attribute height=268? Actually `height="268"` with width 100% — the SVG will be 268px tall, and viewBox content scaled with preserveAspectRatio meet — since container ratio (1326/268=4.95) vs viewBox ratio (1200/268=4.48), "meet" scales content to fit height... hmm, meet means scale to fit entirely: scale = min(1326/1200=1.105, 268/268=1) = 1. So content renders at 1x scale, centered horizontally with extra ~63px margins each side. OK fine.
  
  Nodes: N=7, x from 70 to 1130. Y=112. Numbers at y=56 (Y-56), labels y=80 (Y-32), name at y=148 (Y+36)?? wait: name at Y-56 = 56, number at Y-32 = 80, label at Y+36 = 148, extra at Y+52 = 164. Wait let me recheck: 

  ```
  svg += '<text x="' + x + '" y="' + (Y - 56) + '" ... >' + st.name + '</text>';   // y=56: 生成
  svg += '<text x="' + x + '" y="' + (Y - 32) + '" ... font-size 21 blue>' + st.num + '</text>';  // y=80: 128
  svg += '<text x="' + x + '" y="' + (Y + 36) + '" ... font-size 11>' + st.label + '</text>';  // y=148: 本周产出
  svg += '<text x="' + x + '" y="' + (Y + 52) + '" ... font-size 10 gray>' + st.extra + '</text>'; // y=164
  ```
  Halo circles at cy=Y=112, r=11. Lane line at y=112.
  
  So vertical stack per node: name (y=56), number (y=80), [halo on lane y=112], label (y=148), extra (y=164). The gap between number baseline 80 and halo top 101 is 21px; between halo bottom 123 and label baseline 148 is 25px. OK.
  
  But wait — there's a really important issue: the lane line and particles pass through the halo circles at y=112, and nodes are evenly spaced across 1060px (xs from 70 to 1130, step ~176.7px). Text "存量提案 214" etc at font-size 10 might be wider than 176px? ~7 chars × 5px = 35-80px, fine.
  
  Evidence tray: rect x=180 y=208 w=960 h=34; text at x=200 y=229; right text at x=1120 text-anchor=end y=229: "累计淘汰 306 · 本季复盘 12 次 → 新假设入队 9（generation +1）". Width 960 at font-size 11 — the right text is long: roughly 40+ chars → ~440px at 11px CJK (11px per full-width char, mixed). Let me estimate: "累计淘汰 306 · 本季复盘 12 次 → 新假设入队 9（generation +1）" ≈ 20 full-width chars (CJK+fullwidth punct ~ 11px each = 220) + latin ~ 20 chars (6px each = 120) ≈ 340px. Left text "证据库 · 归因复盘" ≈ 9 chars ≈ 99px. 200+99 = 299; right starts at 1120-340=780. No overlap. OK.
  
  Feedback arc: path from (185, 222) curving to (56, 134) with arrow at top. It goes from the tray's left edge up to the LEFT of the first node (生成 at x=70), the arrow at x0-14=56. OK.
  
  FALL_FROM = [1,2,3,4,6] — nodes 评测(index1), 选择期(2), 组合(3), 验证(4), 监控(6) drop particles to the tray. Node index 5 上线 never drops. Also note index 0 生成 doesn't drop (right). 
  
  Hmm wait, one issue: because "组合" stage (index 3) in OVERVIEW_FLOW is labeled "组合验证中" with number 12, and 验证 (index 4) is 17 = 留出+最终确认 (12+5), there's an internal inconsistency: the 12 in 组合 and the 12 in 验证 overlap! Let me check: 
  - 组合 num: 12 (组合验证中, extra 边际贡献评估 + 冻结)
  - 验证 num: 17 (留出 + 最终确认, extra 每周晋级上限 5)
  - In factory page: 组合验证中 12 = "留出验证 90 天 · 其中最终确认 5"
  - STAGES: 留出验证 12, 最终确认 5 → 17
  
  So the same 12 appears as "组合" count in overview and "留出验证" in factory. The overview says 组合 12 = "组合验证中" and 验证 17 = "留出 + 最终确认". If 组合=12 and 验证=17, then is 17 a subset of 12 or separate? In factory, "组合验证中 12" includes "留出验证 90 天 · 其中最终确认 5" — so 12 is the number of PortfolioDefs in portfolio validation stage, of which 5 are in 最终确认... but wait STAGES says 留出验证 12 + 最终确认 5 = 17. These are contradictory: factory card says 组合验证中=12 of which 最终确认 5 (so 留出=7, final=5), while STAGES says 留出验证=12 AND 最终确认=5 (total 17). And overview 组合=12, 验证=17.
  
  So the numbers are internally inconsistent across views. This is a design-draft bug: the funnel counts don't form a coherent flow. Good catch to report.

  Also: 生成 128 vs STAGES 提案 214. In overview "存量提案 214" as extra. And in factory "本周产出 128 · 目标 ≥100". The STAGES bar chart lists 提案 214, 评测中 89, 选择期 47 — so 214 is stock of proposals, 128 this week's output. 89 评测中... OK. But 选择期 47 with 初筛存活 47 (factory card). Then 组合 12, 验证 17 — wait, how can 验证 (17) > 组合 (12)? If portfolio verification follows combination, the downstream count can't exceed the upstream stock unless counting different things: 17 = 12 (留出) + 5 (最终确认) stacked, while 组合 12 = ... hmm. If 组合 12 are the ones in portfolio stage and they flow into 留出 (12), then 验证 17 = 12 leave-out + 5 final + ... no wait, 5 final would be PART of the 12, not additional. So 17 = 12+5 double counts. Unless 组合=12 means "in portfolio-gate evaluation" and those 12 will go to holdout, while 留出=12 and 最终确认=5 are cumulative numbers... Still confusing. The pipeline numbers should be monotonically non-increasing (a funnel). 12 → 17 violates monotonicity. It's because 验证 mixes two queues: 留出(12)+最终确认(5)=17. But then 组合 12 must be ≥ 17? No...
  
  Actually let me think again: perhaps intended semantics: 组合=12 (portfolio candidates being assembled / in combination stage), 验证=17 (12 in holdout + 5 in final confirmation) — but the 5 in final confirmation should come from the 12 that were in holdout previously. So stock semantics: stage counts are current stock; a funnel snapshot. Current stock can be non-monotonic if flows are slow (e.g., 17 currently in verification because accumulated over time, while combination currently has 12). Monotonicity isn't strictly required for stock counts. But the number labels: "组合 12 / 验证 17" — if read as funnel, decreasing counts would be expected; a viewer will read it as funnel and be confused when it goes up. That's a formality issue. The bigger issue: same stage naming inconsistently counts. And "上线 5" = "已挂载因子" plus 监控 18 — but mounted factors (champion 2 + challenger 3 = 5) which are monitoring, so 监控 18 includes them? The factory card: "在跑与监控 2 Champion · Challenger 3 · 监控 18 · 有效独立数 23". 2+3+18 = 23 = 有效独立数 — this is clearly wrong conceptually (monitoring count ≠ effective independence count). 有效独立数 is a clustering-based measure, not a sum of lifecycle states. Presenting them so they coincidentally sum to 23 is misleading.

- The overview cards below: 策略执行 (PnL), 信号与数据 (IC), 昨夜产出 (batch). 

**Now for the review structure.** The user wants:
1. Big layout suggestions (大布局层面)
2. Review the 7 nodes (formal professionalism)
3. Deep analysis: important nodes, concerns, core metrics

Let me now also think about what the correct "nodes" should be, from first principles, using PRD/architecture as the authority:

**Authoritative pipeline (PRD §2.3 漏斗健康 + FR3.4 + FR6.2 + architecture §2.2):**
生成 → 纯度门 → 因子证据/成本门 → 去重/多重检验 → 选择期 → 组合门（冻结）→ 留出门（样本量三级裁决）→ 最终确认 → 部署前复核 → 挂载/运行 → 监控（衰减/停用）

Note: PRD funnel lists 9 stages; architecture's lifecycle diagram lists: 方法论/PIT门 → 纯度门 → 评测+成本门 → 去重/多重检验 → 选择期 → 组合边际贡献门 → 冻结

## user · 2026-09-14T14:52:30Z

不要指派子agent，你直接读取html页面即可

## assistant · 2026-09-14T14:52:30Z


> [reasoning] The user says: "Don't assign subagents, just read the HTML page directly." OK — so the user wants me to do the analysis directly from the HTML source. I already read index.html, app.js, styles.css completely. I have everything I need. The image-based visual check isn't possible in this model anyway; the user says just read the HTML directly and analyze.

So now: produce the deep review based on my thorough reading. The user's asks:

1. 审视整个设计稿的**大布局层面** (big-picture layout) — suggestions
2. 审视总览里的**动态流水线的 7 个节点** — user feels it's "不是很正式" (not professional/formal enough)
3. **深入分析项目的重要节点、关注点和核心指标** (deep analysis of important nodes, concerns, core metrics)

Let me now think very carefully and produce a high-quality analysis. Let me re-derive from the sources:

## Sources of truth for "important nodes" and "core metrics":

**PRD §2.3 指标体系 (metrics system):**
| 层级 | 指标 | 口径 |
- 北极星结果: 可信 Alpha 产出 — 滚动 28 天内新增的有效独立 PortfolioDef 数（成本后为正、通过无前视与最终确认、达到可信样本量 ≥69 笔、部署前复核有效、对现有组合正边际贡献）
- 转化效率: 研究到证据周期；证据到部署周期（最终确认通过至可挂载 dry-run ≤1 天）
- 探索能力: 有效独立假设吞吐量（名义 ≥100/周 + 有效独立数）
- 漏斗健康: 分级转化率 — 生成 → 纯度门 → 因子证据/成本门 → 去重/多重检验 → 选择期 → 组合门（冻结 PortfolioDef）→ 留出门（含样本量三级裁决）→ 最终确认 → 部署前复核
- 线上结果: 组合运行质量（成本后收益、回撤、容量、回测偏差、因子衰减）
- 信任护栏: 数据与实验完整性（有效快照、manifest、留出台账、可复现率 100%；前视泄漏容忍度 0）

**PRD FR3.4 验证顺序**: FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef → PortfolioDef 最终 90 天留出 → 永久隔离最终确认窗。每周进入最终留出的组合候选上限默认 5，所有访问写 append-only 台账。不得先读取留出结果再新建或修改组合。

**PRD FR3.5 样本量裁决**: <30 UNDERPOWERED / 30~69 临时 PASS（只允许缩减仓位 paper）/ ≥69 可信判定.

**PRD FR4.2/4.3/4.5**: 组合门（边际贡献）→ Top-K (K=3, 上限5) 逆波动率权重 → 冻结 PortfolioDef → 进入留出. 防泄漏规则.

**PRD FR5.2 部署前复核**: 最终确认通过 ≠ 当前仍有效; 挂载前用晚于留出窗的最近窗口复核（架构 §2.2 says 最近 30 天窗口复核）。

**PRD FR6.2 生命周期状态**: proposed/evaluating/validated/champion/challenger/monitoring/decayed/disabled.

**PRD FR6.3 结构化归因**: failure_stage (信号质量、组合转换、成本/容量、时序稳定、执行实现=五阶段), failure_owner (数据、信号、市场状态、成本、组合、执行、风险), failure_mechanism.

**PRD FR7.5 synthesis_report**: 北极星领先指标、cohort 漏斗、有效独立数、来源多样性、资源消耗、五阶段损失、线上偏差、最大约束。

**架构 §2.2 lifecycle data flow**: 
HypothesisDef → FactorDef → 方法论/PIT门 → 纯度门 → 统一评测与成本门 → 去重/多重检验 → 选择期 → 组合边际贡献门 → 冻结 PortfolioDef → 90天留出与样本量门 → 永久隔离最终确认 → 部署前最近窗口复核 → 版本化信号缓存 → dry-run/paper → RunRecord → 绩效归因与衰减监控 → decayed/disabled; 所有拒绝点 → 证据库 X → 复盘 → 新假设.

**F007 five stages**: 信号质量、组合转换、成本/容量、时序稳定、执行实现.

**F007 lifecycle states**: CREATED → VALIDATING → RUNNING → EVIDENCE_READY → INCOMPLETE; canonical EVIDENCE_READY → REGISTERED; cohort OPEN → FINALIZED; preview → PREVIEW_DONE.

Now the mockup's 7 nodes:
1. 生成 128 本周产出 / 存量提案 214
2. 评测 89 评测中 / 本周初筛淘汰 81
3. 选择期 47 存续 / 180 天窗口 · 查重通过
4. 组合 12 组合验证中 / 边际贡献评估 + 冻结
5. 验证 17 留出 + 最终确认 / 每周晋级上限 5
6. 上线 5 已挂载因子 / PM-007 · PM-009 dry-run
7. 监控 18 监控中因子 / PnL +6.42% · 衰减 41 · 停用 96

Now let me carefully identify the issues.

### Issue A: The 7 nodes conflate/mix different objects and metrics (this is the big "formality" problem)

Let me scrutinize each node:

**1. 生成 (128 本周产出, 存量提案 214)** 
- "本周产出 128" mixes a *rate* (本周) into a *stock* pipeline (存量提案 214 in extra). The pipeline is presenting stocks (current counts at each stage) but the first node's main number is a weekly flow. Other nodes show stock. Mixed semantics in same row: 128 (flow/week) → 89 (stock) → 47 (stock) → 12 → 17 → 5 → 18. Also 128 vs the batch table (B-20260912 = 124 candidates; 昨夜产出 card says 124; factor factory card says 本周产出 128) — inconsistent-looking numbers (128 vs 124) for what a viewer will read as the same thing.
- Also: node 1 should be 提案/HypothesisDef (218 proposal) vs FactorDef level. The factor factory's STAGES list uses "提案 214" as first bar. In OVERVIEW_FLOW it says 存量提案 214 as extra of 生成 node. The distinction HypothesisDef → FactorDef matters (FR2.1). "生成" conflates hypothesis registration and factor generation.

**2. 评测 (89 评测中, 本周初筛淘汰 81)**
- "评测中" mixes with "淘汰 81" (weekly flow). Also includes 纯度门/成本门/查重/多重检验 per the design intent ("评测（含纯度/成本/查重子门）"). This is acceptable as macro-stage, but the sub-gates that matter most for credibility — 成本否定 and 多重检验 — are invisible at this level. The batch table shows 成本否定 17 explicitly; the pipeline node doesn't. The "证据库" tray shows 累计淘汰 306.
- Given the project's core narrative (§2.6: 论题检查点 driven by "成本主导流失" vs "假设源枯竭"), the *biggest* funnel question is: why do candidates die? The pipeline doesn't show loss attribution (五阶段损失), which FR7.5 says must be reported. This is a core metric missing from the overview.

**3. 选择期 (47 存续, 180 天窗口 · 查重通过)**
- "180 天窗口" — note PRD/architecture don't fix a 180-day selection window; mockup detail page says 选择期 2026-03-16 → 2026-09-12 (180 days). Fine as placeholder.
- "查重通过" appears in node 3's extra, but 查重 happens in node 2 (评测). Minor duplication/ordering confusion.
- Also "存续" is vague; this stage should be "选择期候选" with 进化率.

**4. 组合 (12 组合验证中, 边际贡献评估 + 冻结)**
- "组合验证中" mixes 组合门 (selection-side, portfolio-level marginal contribution on selection data) with 验证 (holdout). Actually by FR3.4: 组合构建 occurs after selection phase, then holdout. "组合验证中 12" — the number 12 should be PortfolioDefs under construction/marginal-contribution gate. But labelled "组合验证中" suggests verification. And the factory card says "组合验证中 12 · 留出验证 90 天 · 其中最终确认 5" — conflates 12 (portfolio stage) with 留出 (verification).
- The node's unit is now PortfolioDef (组合) — the entire pipeline before it counted FactorDefs; from here on it's PortfolioDefs. The 7-node lane visually implies a single continuous flow 128→89→47→12→17→5→18, but the object switches from factor to portfolio at node 4 (and holdings at node 6-7 mix factors/strategies). This is the single biggest formal problem: **the numbers are not a funnel** — they can't be read as conversion (47 factors → 12 portfolios is not a rejection rate because multiple factors go into one portfolio; 12 → 17 INCREASES, which looks wrong in a pipeline!). Node 5 (验证 17) > node 4 (组合 12)? 17 = 12 留出 + 5 最终确认 — so it's a cumulative sum, while other nodes are stocks. Actually 12+5=17 where 5 is the *subset* "其中最终确认 5" of the 12. So 12 = 留出验证中? and 5 = 最终确认中? Then 12+5 = 17 double-counts. From STAGES: 留出验证 12, 最终确认 5, so 17 total across two stages. But OVERVIEW_FLOW node 5 shows 17 with label "留出 + 最终确认" and extra "每周晋级上限 5". Meanwhile the factory card says "组合验证中 12 · 留出验证 90 天 · 其中最终确认 5" — reading as 12 portfolios in verify, 5 of which are in final confirmation. So node 4's 12 = portfolios in verification, node 5's 17 = ??? If node 4 = 组合 has 12 and node 5 = 验证 17 = 12+5... it's incoherent. Either way: **node 5's number 17 is larger than node 4's 12 — a pipeline that grows mid-flow; and 17 double-counts what the cards describe.** The user's instinct ("not formal") is right: the numbers don't form a coherent funnel, and an expert reviewer will notice.

Let me verify precisely:
- OVERVIEW_FLOW: 组合 num=12 label="组合验证中" extra="边际贡献评估 + 冻结"; 验证 num=17 label="留出 + 最终确认" extra="每周晋级上限 5".
- Factory card 3: 组合验证中 12 | sub: "留出验证 90 天 · 其中最终确认 5"
- STAGES: 留出验证 12 hot; 最终确认 5 hot. And hero card: "12 组合验证中 · 其中最终确认 5" — wait it says "留出验证 90 天 · 其中最终确认 5". Hmm: "组合验证中 12" with sub "留出验证 90 天 · 其中最终确认 5" means the 12 are in 留出验证, of which 5 are 最终确认? No — 最终确认 comes AFTER 留出. So probably: 12 in 留出验证 AND (separately) 5 in 最终确认. The factory card phrase "其中最终确认 5" (of which 5 in final confirmation) is ambiguous/wrong; and the overview adds them: 12+5=17.

So multiple doc-side inconsistencies:
(a) 组合 node counts portfolios at 12 while STAGES "留出验证 12" — same 12 in two different stages.
(b) 验证 node 17 = 12+5 mixes stocks of two different stages.
(c) 上线 5 = Champion 2 + Challenger 3 (这两个是执行面状态, FR6.2) — the "上线" node mixes champion/challenger (lifecycle) with 已挂载因子 (deployment). And 5 = same number as 最终确认 5 — likely coincidence in the fake data, but it *reads* as if final-confirmation candidates = mounted factors (confusing).
(d) 监控 18 "监控中因子" — but if champion/challenger are mounted and running, the 监控 should cover them too; 18 vs 2+3 inconsistent semantics. Also STAGES 监控 18 plus 衰减 41 plus 停用 96 are historical cumulative counts (populations), not current stock. The whole lane mixes "current stock" with "cumulative outcomes" (306 eliminated in the tray, 衰减 41 / 停用 96 in node 7's extra).

**Issue B: The lane's semantics (what flows) are ambiguous; and the animation is decorative rather than informative.**
- Particles move along the lane and "die" at their target node (fade out) — wait, actually reading the code: particles move to a target node picked by weight, then fade. That's fine as "flow". But what does the particle represent? A candidate? A batch? The particles spawn continuously and disappear — no time semantics, no count. The pulse at arrival is pure decoration.
- The "淘汰" falling particles from stages [1,2,3,4,6] drop into 证据库 — but nothing shows *which* stage's rejections dominate, nor volumes. And a stage-6 (监控) fall is labeled decay (amber); yet monitoring exits also include 停用. OK.
- The feedback arc from 证据库 → 生成 with 3 particles on a loop — decoration.
- The user says "不是很正式" — I agree: for a quant evidence console, an animated particle pipeline with pulsing halos is more "game dashboard" than "instrument panel". The core content (stage stocks, gates, budgets, loss attribution) could be delivered with a static, information-dense pipeline/step diagram (or a weekly-flow Sankey + stage table). The animation adds no decision value; it adds idle CPU/battery cost, and motion is often inappropriate for a tool used for hours. The README even emphasizes "信息密度优先于视觉表演" for the design system — the pipeline is the one place that violates it. Good catch to cite.

**Issue C: Missing "important nodes" from the authoritative funnel.**
The PRD §2.3 funnel: 生成 → 纯度门 → 因子证据/成本门 → 去重/多重检验 → 选择期 → 组合门 → 留出门 → 最终确认 → 部署前复核. The mockup's 7: 生成/评测/选择期/组合/验证/上线/监控. Missing as distinct gates:
1. **部署前复核 (FR5.2)** — squeezed into "上线". This is a *hard gate with its own semantics* (recent-window recheck, champion replacement triggers it). PRD G5: "最终确认通过至 dry-run ≤1 天" — a conversion-efficiency metric that depends on this step being visible.
2. **最终确认 (永久隔离窗)** — merged into 验证 with 留出. The permanent isolation and weekly budget (每周进入最终留出的组合候选上限默认 5 / 每周晋级上限 5) are core process invariants (FR3.4). The node extra mentions 每周晋级上限 5 but the label conflates two very different windows (90 天留出 vs 永久隔离确认).
3. **样本量三级裁决 (FR3.5)** — <30 / 30~69 / ≥69 — critical for interpreting whether numbers count toward 可信 Alpha. It's in the detail page ("毛交易样本" card with UNDERPOWERED / 30~69 临时 PASS / ≥69 可信判定) but absent from the overview/factory. A monitor of pipeline health probably should surface "多少候选处于 UNDERPOWERED".
4. **证据库/复盘回流** — present via tray + arc (good; architecture-aligned).
5. **上线后的 lifecycle states (champion/challenger/decayed/disabled)** — partially present in node 7's extra text; the overview mixes cumulative counts (衰减41/停用96) into a stock node.

Also the difference between **preview vs canonical** (F007, ADR-0006 — execution tier boundary) is entirely absent from the console. This is arguably an important "node/annotation" in a research console: every number must be canonical; preview products are isolated. At minimum the top bar should declare it (they do have 数据版本/成本模型 but not "canonical ledger" identity).

**Issue D: Core metrics missing/wrongly weighted in the overview.**
The overview's job (README): "总览 = 全工作流闭环的实时呈现", "不含任何待办类内容". The three cards: 策略执行 (PNL), 信号与数据 (IC), 昨夜产出 (candidates). Missing vs PRD §2.3 指标体系:
- **北极星：可信 Alpha 产出 (滚动 28 天有效独立 PortfolioDefs)** — NOT visible anywhere on overview. For the product whose North Star is this, the top of the landing page should show it, even if it's currently 0. (The design philosophy says "北极星允许长期为零" — showing 0 with context is honest and drives the checkpoint discipline.) Currently the overview leads with dry-run PnL +6.42% which is an *ops* number, not the research output. Actually wait — is the landing page overview or strategy? README: "左树 4 项（总览 / 监控 / 因子 / 设置）... 落地页 = 总览". Earlier bullet says "移除「工作台/总览」页，落地页 = 策略运营" — contradictory! Let me re-read.

README bullets:
- "**首屏命名「工作台」**：定位是个人工作台（今天需要关注什么），不是系统总览；"
- "**左树 4 项（总览 / 监控 / 因子 / 设置），带图标，可收起为纯图标栏**：「因子」页 = ...；落地页 = 总览；"
- "**移除「工作台/总览」页，落地页 = 策略运营**：管线核心是全自动闭环，界面不出现「待你处理」的待办与提醒；..."

These three bullets CONTRADICT each other: (1) first screen named 工作台 (workbench), (2) landing = 总览 with nav 总览/监控/因子/设置, (3) 总览 removed, landing = 策略运营. The actual index.html: nav has 总览/监控/因子/设置 and overview is active by default (landing = 总览). So the README contains stale decision records from earlier iterations — bullet 3 contradicts the built mockup. This is a real documentation defect: the "关键设计决策记录" mixes historical decisions without marking supersession. For a "正式" design asset, decision log must be ordered with dates/supersedes. Good catch.

Also "每行即未来实现时的一个（组）API 端点" — the README table says 一级视图共 4 个: "策略运营（落地页）/ 因子工厂 / 因子库 / 设置" — again says 策略运营 is the landing page, but nav order and default active are 总览. Contradiction #2 in the table vs bullet #2. So README inconsistent in at least two places. The user's feeling that things aren't formal is justified: the mockup's own README hasn't been reconciled.

Wait, but let me be careful: maybe「总览」was renamed to「工作台」then removed... Let me count decision bullets that conflict:
- Bullet 1: 首屏命名「工作台」... (implies first screen = 工作台)
- Bullet 9?: 左树 4 项（总览 / 监控 / 因子 / 设置）... 落地页 = 总览
- Bullet 10: 移除「工作台/总览」页，落地页 = 策略运营
And in index.html: nav = 总览/监控/因子/设置, overview active by default, and strategy view titled 策略运营.
So the built reality = nav with 总览, landing = 总览. The README's last bullet (10) is a *superseded* older decision? Or a newer decision not implemented? Which direction? The README says "移除「工作台/总览」页，落地页 = 策略运营" — if that were the latest decision, the mockup would have landing = strategy and no overview. But the mockup has overview with the fancy pipeline animation and the README elsewhere describes 总览 in detail ("总览 = 全工作流闭环的实时呈现：动画流水线..."). The bullet order in the README file places "移除总览" near the end — but bullet 9 describes 总览's full design. Actually I bet the history: initially built overview (workbench) with pipeline; then decided "remove 工作台/总览, landing = strategy ops" (because 全自动闭环, no todos); then... re-added 总览? The index.html today has both nav item 总览 (active default) and the pipeline. And the README bullet "总览 = 全工作流闭环的实时呈现" describes the current implementation. The "移除" bullet must be stale. Either way — unresolved contradiction in the doc itself. For a design asset used to lock the information architecture, this is exactly the "not formal" problem at the process level.

Hmm wait, actually let me re-read more carefully:
- Bullet: "**移除「工作台/总览」页，落地页 = 策略运营**：管线核心是全自动闭环，界面不出现「待你处理」的待办与提醒..."
- Bullet after: "**服务矩阵只列长驻服务**..." and "**设置页 tab 化**..."
- And earlier: "**左树 4 项（总览 / 监控 / 因子 / 设置）...；落地页 = 总览**"
- And: "**总览 = 全工作流闭环的实时呈现**：动画流水线（粒子流动 + 站点存量 + 落站脉冲）+..."

Yes — direct contradiction: "落地页 = 总览" vs "移除总览页，落地页 = 策略运营". Also "不含任何待办类内容" vs "首屏命名「工作台」：定位是个人工作台（今天需要关注什么）" — workbench implies "today's attention", which contradicts "不含待办". These are three incompatible generations of decisions. The README needs a decision log with timestamps/supersedes or the stale ones removed. This is a concrete, verifiable finding. 

**Issue E: Layout-level observations (大布局)**

Let me think about the layout structure from code:

- Global: header 52px (brand + 环境 DRY-RUN + 数据版本 + 成本模型 + UTC clock), nav 212px (4 items + collapse), main max-width 1400px, padding 24/28.
- Overview: pipeline card (6px 8px 0 padding) then g3 cards (策略执行/信号与数据/昨夜产出).
- The pipeline SVG: W=1200, H=268 viewBox, preserveAspectRatio NOT set (default xMidYMid meet for the outer svg? Actually svgChart uses preserveAspectRatio="none" for charts; the pipeline SVG in renderOverview sets width 100%, height=H=268 fixed, viewBox 0 0 1200 268, no preserveAspectRatio → default meet. So width scales, height fixed 268. On wide screens (viewport 1680 - nav 212 - padding 56 = 1412px content, view max 1400), it scales up moderately. OK.
- Pipeline card height ~274px + card padding; the lane Y=112, nodes labels above (y=56, 80), below (y=148, 164); tray at y=208 h=34 → 242; arc from 220 up. Total 268. The card is full width of the view; the 3 cards below are g3.

Big layout questions:
1. **Overview hierarchy**: The pipeline (the biggest, most expensive element) shows process state; the three below cards show strategy PnL, signal IC, and overnight output. Missing: the actual "North Star" (可信 Alpha), the funnel health (conversion rates / loss stages), and the gates' budget consumption (留出预算/每周晋级上限). The current overview answers "what's running" but not "what is our research output and where is it dying". For a product whose success is defined by evidence throughput, the landing page should lead with research output and evidence integrity, not dry-run PnL (which is M3/M4 concern — and per ADR-0005 decision 7, ops readings are only placeholder in this blueprint; fine for the blueprint, but the research half is under-represented).

Hmm, but careful: the README says the mockup is the 终局全景蓝图 (end-state blueprint across all four faces: research/ops/platform/emergency). So showing ops PnL on the overview is by design. But the overview should still carry the North Star since it's a "全工作流闭环" view. And FR8.1 red line: "实时运营数据不进入研究视图" — the overview mixing research pipeline + live PnL + IC is exactly the "研究/运营混面" red line question! The README claims FR8.1 落点: "研究视图（漏斗/因子库/详情/对比/谱系）只渲染版本态产物...实时运营数据不进入研究视图". But 总览 shows: 策略执行累计 +6.42% 今日 -0.31% (live ops), 信号与数据 (采集延迟 0.8s, 同步 42s, 陈旧信号 — live ops), 昨夜产出 (research-ish), pipeline (research states). So the 总览 is a mixed view combining 实时运营 + research. Is that a violation of FR8.1? FR8.1 says research *views* (研究视图) must be canonical-only; the overview is arguably an ops/combined view, not one of the listed research views. But then the overview itself becomes the wall where the two faces blur — the design needs an explicit rule for what "总览" is allowed to show and what "tier" its numbers are (preview vs canonical). Currently ambiguous. For a console whose ADR says "哪个数字是真的 is unacceptable risk", the 总览 being a mix of live ops and research stocks without tier/datasource annotation is a governance gap. Suggest: split 总览 into clearly labeled 研究段 (canonical, manifest-linked) and 运营段 (ops, TSDB), or annotate each card with its 真相源 (as the README's API table does) so viewers know what can be compared.

2. **The nav has 4 items: 总览/监控/因子/设置** — but the information architecture table says 一级视图共 4 个: "策略运营（落地页）/ 因子工厂 / 因子库 / 设置". Mismatch again (监控 = 策略运营 renamed; and landing conflict as noted). Also the "因子" page merges 因子工厂 (upper) + 因子库 (lower). Hmm — is merging factory and library into one page a good layout? 因子工厂 = weekly throughput/cohort funnel; 因子库 = the lookup table of all factors. Different jobs: "how is production going" vs "find/compare factors". Merging makes the page very long (4 stat cards + 2 chart cards + section + filters + long table). The README rationale: "产出到列表同页动线最短". Trade-off: the library table is the main workspace (research browsing), and having the production report above it means every visit starts with scrolling past factory stats. Possible refinement: default-collapsible factory summary strip (one row) with expand, or tabs. But honestly this is a judgment call; I should present it as a question with trade-offs rather than a defect. Also the left nav item is labeled 因子 but contains 工厂+库 — naming mismatch with the README's "因子工厂 / 因子库". And nav label 监控 vs page title 策略运营 — naming mismatch (nav says 监控, page says 策略运营; title attribute on nav = 监控). Also note: in the factory page, the 流水线状态分布 card has 10 bars including terminal states (衰减/停用) — fine.

3. **Settings page**: 业务配置 table (17 params, long) + 项目运维 (service matrix + logs). Reasonable. But service matrix rows have disabled buttons (design draft). Also "verify 门禁" is in the service matrix though it's not a long-running service (README says pace only long-running services: freqtrade/kronos/data-collector/timescaledb/grafana — but SERVICES includes "verify 门禁" as 6th row). Contradiction with its own decision ("服务矩阵只列长驻服务（freqtrade / kronos-signal / data-collector / timescaledb / grafana）") — the matrix includes verify 门禁 which is not in the list. Small but concrete inconsistency. Also operation "门禁立即运行" (run gate now) in README's service health description vs FR8.4 "门禁与统计裁决不出现在任何可点击路径上——「验证结果」面板只读呈现最近一次 verify 的结果". Another contradiction: README bullet says 服务健康 includes "门禁立即运行" (run gate now button!), then the FR8 red line says gates must NOT be on any clickable path. Indeed SERVICES has ops: ["立即运行"] for verify 门禁. If the design's own red line says "门禁裁决不出现在任何可点击路径上", then a "立即运行 gate" button in the matrix violates it (even though it "runs" rather than "adjudicates"... the FR8.4 wording: "门禁与统计裁决保持确定性脚本路径，界面只呈现裁决结果，不提供裁决按钮" — a "run now" button is arguably a trigger, not a verdict button; but the README's own FR8.4 落点 says "「验证结果」面板只读呈现最近一次 verify 的结果". Running verify.py from UI is a write-ish op; and the button is disabled in mockup anyway. Still, deserves flagging as an internal inconsistency to resolve in F006 spec.)

4. **Detail page layout**: fishbone with 11 columns for 7 stages — `grid-template-columns: repeat(11, minmax(88px, 1fr))`. 11 columns but only 7 stages? The fish-inner has 11 columns of grid but cols = MACRO_STAGES mappings only 7 `.fsh-col` elements. With repeat(11, ...) and 7 children, 4 empty columns at right. Probably leftover from a 11-node design (maybe earlier had 11 steps?). This is a concrete layout bug: 4/11 of the width is dead space at the right edge of the fishbone. Actually wait — let me double check: `grid-template-columns: repeat(11, minmax(88px, 1fr))` with 7 items → 7 filled, 4 empty tracks. Yes, dead space. Unless... the earlier version had 11 stages and current has 7. Either way, that's a layout defect worth fixing (should be repeat(7, ...) or auto-fit). Hmm, but maybe I should be careful — maybe they intentionally want columns wider? No — repeat(11,...) of minmax(88px,1fr) in a ~1350px container gives ~122px per column ×7 = 857px used, leaving ~490px blank on the right. The horizontal rule `.fish-inner::before` spans left:14 right:14 of the whole grid — so the axis line extends across ALL 11 columns including the empty ones! So the fishbone spine runs past the last node into empty space. That looks unfinished. Concrete defect. Let me verify by re-reading:

```css
.fish-inner {
  position: relative;
  display: grid;
  grid-template-columns: repeat(11, minmax(88px, 1fr));
  min-width: 990px;
}
.fish-inner::before { content:""; position:absolute; left:14px; right:14px; top:79px; height:2px; ... }
```
Yes: spine spans full inner width; columns = 11; stages = 7. Confirmed: line extends beyond last node into blank area. 

Hmm wait, actually there's a subtlety: the `.fsh-col` elements are direct children; grid auto-places them in the first 7 tracks; tracks 8-11 empty. Spine (::before) is positioned absolute across full width → extends past node 7. Yes. Fix: repeat(7, minmax(...)) or grid-auto-flow. Good catch.

Also in the detail page there's `.flow` and `.fstep` CSS (legacy stepper styles, lines 265-292) that are unused by current markup (renderWorkflow produces fishbone, miniFlow produces stepper). Dead CSS. Minor.

Also, `d-flow-aux` text in JS: `fl.reached >= 6 ? "当前挂载于 " + fl.pm : ...` — for rejected factors shows "于「评测」被拒绝". OK.

5. **Factor library table density**: 11 columns + checkboxes; includes 生命周期进展 mini-stepper with 7 steps ×32px = 224px wide plus text labels under dots (`.mlb` font-size 10px, nowrap) — stage names 生成/评测/选择期/组合/验证/上线/监控 under dots. That's a wide column; fine on 1400px. But labels under each dot at 10px, 7 labels — busy. The "结论" filter still uses promising/weak/dead/decayed — which per architecture §4.2 the `verdict` is "成员诊断标签，不是可晋级裁决" (diagnostic label, not promotion verdict; promotion comes from cohort_verdict promotion_verdict after finalize). The mockup labels the column "结论" (verdict) — but per F007, the factor-level verdict is diagnostic; the auditable conclusion is cohort-level `promotion_verdict`. Using "结论" for the diagnostic label risks over-claiming. Should be "诊断" or "成员标签" — minor wording, but this is exactly the precision issue that matters to this project (证据语义). Also 'underpowered' and 'incomplete' verdicts exist in F007 but the mockup filter offers only promising/weak/dead/decayed. Missing underpowered/incomplete — formality gap.

Also miniFlow tooltip: for decayed factors, shows "已降权（note11）" — ties lifecycle to monitoring stage. OK.

6. **Top bar**: 环境 DRY-RUN / 数据版本 v2026.09.12 / 成本模型 cm-v1 / UTC clock. Missing: the **canonical ledger / research snapshot** identity. Data version is a dataset-level reference but canonical experiments bind a ResearchSnapshot (multi-dataset). Per FR8.1: "每个数字可追溯 manifest（data_version / cost_model_version 在顶栏与详情页可见）" — README claims this. But strictly the binding identity for multi-dataset is research_snapshot_id (ADR-0007). Showing only one dataset's data_version is insufficient when multiple datasets (ohlcv/funding/kronos signals) can version independently. For formality: top bar should show the active ResearchSnapshot (or at least snapshot + constituent versions on hover/detail), plus maybe code_build_digest and execution tier (canonical). This is a core-metric identity concern.

7. **Line + bar mixing**: factory 流水线状态分布 uses horizontal bars for 10 stages mixing massively different magnitudes (提案 214, 评测中 89, ..., Champion 2) with log-ish visual distortion? No, linear — first bar 100%, others 42%,22%,5.6%... terminal 衰减 41, 停用 96. It's a funnel+outcomes mixed. Fine-ish, but the bar chart mixes "current stages" and "terminal outcomes" (same as the pipeline lane issue). Also the factory hero card #4: "在跑与监控 2 Champion · Challenger 3 · 监控 18 · 有效独立数 23" — mixing counts of different kinds and 有效独立数 is a *research metric* placed as auxiliary text. Per PRD, 有效独立数 is central to 探索能力 (must be reported with nominal throughput). It deserves better than a sub-line. 

8. **监控 page (策略运营)**: strip (策略/引擎/信号源/滚动IC/陈旧信号/推理耗时) + 6 stat cards + equity curve + IC chart + positions + closed trades. Layout: OK. But: "信号预测力（7 天 IC）" uses threshold 0.015 as 降权线 — consistent with PARAMS. Fine. One mismatch: strip shows "滚动 IC 0.038" but strategy stat card doesn't show it; overview "信号与数据" card shows 0.038 as big number; consistent fake. OK.

Also strategy page has 6 stat cards in g6 — narrow cards (1400/6 ≈ 220px). Fine.

9. **The overview pipeline node labels**: node name above number (name y=Y-56=56, number y=80, label y=148, extra y=164). Y=112. So: name, big number, then (lane), then label, then extra. The "label" (评测中) is BELOW the node and the "extra" (本周初筛淘汰 81) further below; but the big number is ABOVE. This creates the reading order: name → number → [line] → label → extra. The label "评测中" is the unit/description of the number; having the descriptive label separated from its number by the lane (with the number above and label below) makes scanning harder: you read a number, then must cross the line to know what it counts. Also the four lines of text at varying sizes (13/21/11/10px) with different vertical gaps: 32px gap between name and number, but number→label = 68px (crossing the rail + halo), label→extra = 16px. The hierarchy is: the number is prominent (good), but "本周产出/存量提案 214" for node 1 mixes flow/stock again. Also node widths: with 7 nodes across 1200 viewBox, each ~176px apart; Chinese text at 11px fits. The extra line "边际贡献评估 + 冻结" (11 chars) fits. OK.

Actually, let me reconsider the node number semantics for each: 128/89/47/12/17/5/18 with labels 本周产出/评测中/存续/组合验证中/留出+最终确认/已挂载因子/监控中因子:
- 128 = weekly flow
- 89 = current stock in evaluation
- 47 = stock in selection
- 12 = stock in portfolio stage
- 17 = SUM of two stages (or maybe "in verification" total, but 12+5)
- 5 = stock mounted (2 champ + 3 chall)
- 18 = monitored factors
So the lane mixes: flow (128), stocks (89/47/12/17/18), and a sum (17). And also these numbers come from different objects (Factor, Factor, Factor, Portfolio, Portfolio, Strategy, Factor?) — all but node 4-6 are factor counts. The pipeline *looks* like a funnel (one number per stage, left to right shrinking mostly) but 12→17 increases. A reviewer will ask "why is the pipeline growing?" — the user's instinct is validated.

Wait — actually let me think again: is 17 maybe correct as "留出+最终确认" = 12 留出 + 5 最终确认 where these are disjoint? STAGES: 留出验证 12, 最终确认 5 as separate rows. If disjoint, then the 12 in 组合 (portfolio verification) == 留出验证 12? and 最终确认 5 comes after 留出? Then 12 留出 cannot be "留出+确认"... The factory card says "组合验证中 12 · 留出验证 90 天 · 其中最终确认 5" — "其中" = of which. If the 12 are in 留出 and 5 of the 12 are in 最终确认, that's impossible because final confirmation is AFTER holdout completes (GATE → H in architecture: 90-day holdout gate then final confirmation). A candidate in final confirmation has PASSED the 90-day holdout, so it's not "of" the 12 in holdout. Unless the 12 = "组合验证中" = all portfolios currently in verification (either holdout or final confirm), of which 5 in final confirm. Then 留出 = 12-5 = 7. But STAGES says 留出验证 12. Either way, at least one of the sources is wrong: if 12 = holdout-only, 其中最终确认 5 is impossible; if 12 = total in verification, then STAGES' 留出验证 12 is wrong. And the overview's 验证 17 = 12+5 double counts. So: the fake data has a genuine internal inconsistency in exactly the most sensitive part of the pipeline (the verification gates). This is a perfect demonstration of "not formal" — in a product where gate accounting is sacred (每周留出晋级上限 5、budget consumption), the mockup's numbers for the gate area are muddled.

Let me also check "17" vs "每周晋级上限 5": node extra says "每周晋级上限 5". If 5 = 本周已晋级至最终确认的（budget used），and 17 = 留出+确认中的存量, the semantics are different again (budget usage per week vs stock). The mockup doesn't distinguish "本周用掉的预算 5" from "处于最终确认的存量 5" — same number 5 elsewhere (最终确认 5 in STAGES). Ambiguity.

10. **证据库 tray text**: "累计淘汰 306 · 本季复盘 12 次 → 新假设入队 9（generation +1）". Per PRD, generation is per HypothesisDef (来源与 generation) and feedback入队 must count into multiple-testing budgets. Displaying "generation +1" is nice. But "累计淘汰 306": the tray is the destination of ALL rejections/failures (方法论/PIT, 纯度, 去重, 成本, 组合, 留出, 最终确认, 部署复核失效 → all → X). The pipeline animation only shows falls from stages [1,2,3,4,6] (评测/选择期/组合/验证/监控) — missing falls from... hmm node 0 生成 has no rejections (fine), node 5 上线 no rejection? 部署前复核失效 goes to X (architecture: R →|失效| X). In the mockup, 上线 stage (m=5) has no fall particle. And 监控 (m=6) has one (decay amber). So deployment-recheck failures aren't represented — minor.

Actually wait, FALL_FROM = [1, 2, 3, 4, 6] — indices into OVERVIEW_FLOW (0=生成,1=评测,2=选择期,3=组合,4=验证,5=上线,6=监控). So falls from 评测/选择期/组合/验证/监控. Missing 上线 (部署前复核失效). Also missing the part where 监控 outputs 停用 (disabled, also goes to evidence library? The architecture says M →|降权/下线| N[decayed/disabled]; and X → 复盘. 停用 candidates: do they go into 证据库 for postmortem? Probably yes as part of 复盘 inputs: "所有拒绝点进证据库 X". The mockup's node-7 extra mentions 衰减 41 · 停用 96 as text, and fall particles from m=6 are amber ("decay"). Fine-ish.

11. **The 3 overview cards**:
- 策略执行: +6.42% 累计 · 今日 -0.31% · 回撤 -1.94% · 持仓 4 + sparkline. This duplicates the 策略运营 page almost exactly (same numbers). Is duplication on overview desired? README says overview has 策略执行/信号与数据/昨夜产出 cards. It's the "全工作流闭环" narrative. OK but then the overview is heavily ops-weighted (2 of 3 cards are ops). For the product's purpose (research factory + evidence), the overview should tell: what did the factory produce, what died and why, what's the North Star progress, what requires attention (no — no todos by design). Hmm. Actually there's an explicit design decision: no todos, no "needs you" — the console is a monitoring window; the human reviews logs. Then the overview's composition choice of "策略执行/信号与数据/昨夜产出" is defensible: immediately-running money (dry-run), signal health, and last night's factory output. But it underplays the North Star. I'll present suggestions: (a) top strip with 北极星：滚动 28 天可信 Alpha (当前 0，附解释 tooltip/脚注) + 有效独立数 + 研究到证据周期 median; (b) the pipeline lane as the centerpiece with gate budgets; (c) keep 3 cards.

12. **Typography/scale**: base font 13px, table 13px (with 12px th), cards h3 12px, big 26px. For a data console this is reasonable. The pipeline: name 13px, number 21px, label 11px, extra 10px. The 10px extra text (e.g., "边际贡献评估 + 冻结", "留出验证 90 天 · 其中最终确认 5") is below recommended minimum for dense reading; and `.mlb` mini-flow labels are 10px. On a 1440p screen at 100% zoom fine, but 10px × #9ca3af (text-3) is low-contrast small text. WCAG: #9ca3af on white ≈ 2.8:1 — fails 4.5:1 for normal text; even for large text fails 3:1. The design system uses --text-3: #9ca3af for aux text everywhere (chart-meta, hint, th). For a formality/accessibility pass, this might be acceptable for decorative aux but not for meaningful labels like stage extras. Suggest bumping the pipeline extra to 11-12px --text-2 (#6b7280, ~4.8:1? #6b7280 on white = around 4.54:1 — borderline pass). Hmm let me not over-index on WCAG since it's an internal tool; but "10px #9ca3af" as load-bearing text is a legit critique.

13. **The overview pipeline's vertical allocation**: H=268 but the tray occupies y=208..242; lane at 112; labels above start at 56; feedback arc sweeping below-left. There's a lot of empty vertical space in the middle-upper area (56-112 name/number) — fine. The bottom 26px (242-268) is empty. The card padding 6px top. Total card ≈ 274px tall for showing: 7 names, 7 numbers, 7 labels, 7 extras, a lane, a tray, an arc. Density: acceptable but the "extra" lines are the load-bearing semantic content and they're the smallest/closest to the tray. Also the layout in the SVG is done with manual coordinates; at other widths it scales (default preserveAspectRatio meet → uniform scale... wait, svg width=100% height=268 viewBox 0 0 1200 268; default preserveAspectRatio="xMidYMid meet" — so if the card's width ≠ 1200 proportion, the SVG scales uniformly and centers with possible vertical letterboxing. Card content width ~1360 → scale up 1.13 → drawn height 268*1.13 = 303 > 268 fixed height → actually "meet" scales to fit BOTH width and height: scale = min(1360/1200, 268/268)=1 → so at wider widths, the viewBox never scales up beyond height constraining; it centers horizontally with padding. Hmm: with width=100% (1360px) and height=268, viewBox 1200x268: meet → scale=min(1360/1200=1.133, 1)=1 → rendered content 1200x268 centered horizontally in 1360 → 80px empty left/right inside the card. So on a 1412px content area the pipeline graphic is centered with ~106px gutters each side; the nodes span x=70..1130 of 1200 → in-page from ~176 to ~1236 within card. Meh — acceptable, slight wasted margin. Alternatively preserveAspectRatio="none" would stretch. Minor; could set viewBox width dynamically. Not a big deal but if they want edge-to-edge alignment with the cards below, the 100px side gutters make the lane not align with the card grid. The tray is x=180..1140 within 1200 → in page ~286..1246. The 3 cards below span full content width. Visual alignment mismatch: pipeline's internal elements inset from card edges. Debatable — actually could look intentional (the lane has its own margins). I'll mention briefly.

14. **"昨夜产出" card**: 124 候选 sub: "B-20260912 · 晋级 9 · 淘汰 64 · 成本否定 17". But batch table: B-20260912: n=124, prom=9, weak=51, dead=64, cn=17. "淘汰 64" + "成本否定 17" + "晋级 9" + weak 51 = 141 ≠ 124. Hmm: 124 = 9 prom + 51 weak + 64 dead? = 124. And cn=17 is a subset of dead (cost_negative are dead) → 64 includes the 17. So "晋级 9 · 淘汰 64 · 成本否定 17" — the 64 includes 17; presenting them as parallel counts (9+64+17=90≠124) is confusing; and weak 51 is not shown. Also in the factory batch table the columns are 候选/晋级/淘汰/成本否定 — where 淘汰 64 presumably = weak+dead? or dead only? Ambiguity. And overview pipeline node 2 extra "本周初筛淘汰 81" vs batch B-20260912 dead 64 + cn 17 = 81? 64+17 = 81! Yes: "本周初筛淘汰 81" = 64 dead + 17 cn from the latest batch?? But that's a single batch, labeled "本周" — and it double counts cn within dead if 64 includes 17. If dead=64 includes cn=17, then 淘汰 81 = 64+17 double counts. If dead excludes cn... the table has separate columns so likely dead 64 EXCLUDES cost_negative 17 (separate column for emphasis), then 64+17=81. OK plausible: batch composition = 9 prom + 51 weak + 64 dead + 17 cn = 141 ≠ 124. Hmm, that doesn't work. OR: 124 = 9 + 51 + 64 where 64 includes cn(17)? Then cn subset of dead. 9+51+64=124 ✓. Then "淘汰 81" isn't derived from this batch's columns (81≠64). "本周初筛淘汰 81" could be week total across 4 batches (81 eliminations this week) — but then it conflicts with batch 1 alone having 64+17. Ugh — muddled. whichever way, the fake data doesn't add up cleanly, and totals can't be reconciled across views. Which is _exactly_ the kind of thing this project cares about (证据口径). For the mockup review: recommend making the fake data internally consistent and derivable (write it as one dataset with derived aggregates, or at least keep a consistency table in the README). This is a strong concrete finding.

Let me also check 128 vs 124 vs 117: factory card 本周产出 128; batches B-20260912=124, 0911=117, 0910=96, 0909=88 — the four batches shown (last 4) sum to 425, but 本周 might be 7 batches; 128 doesn't equal any obvious aggregation — unless 128 is the week to date. It reads as inconsistent though. If 本周 == 4 batches shown, 425≠128. If 128 is just the latest "本周累计"... whatever. Recommend consistency.

15. **S-curve of metrics on 监控 page**: "滚动 IC 0.038" in strip; overview "信号与数据" big 0.038 label "信号预测力 · 采集延迟 0.8s · 同步 42s · 陈旧信号 7". Meh.

16. **Naming/terminology consistency** (formality): 
- nav: 总览 / 监控 / 因子 / 设置
- page titles: 总览 / 策略运营 / 因子工厂(+因子库) / 设置
- README IA table: 策略运营（落地页）/ 因子工厂 / 因子库 / 设置
So nav 监控 ≠ page 策略运营; nav 因子 ≠ pages 因子工厂+因子库. Naming mismatches. For a console meant to make concepts precise: recommend aligning nav labels with page titles (either 监控→运营 or page title→监控...; probably 策略运营 is the better name per README decision; and 因子 → 因子工厂? but it contains the library too; maybe rename to 因子库 or make it two nav items). Anyway flag it.

17. **Lifecycle vocabulary**: four different vocabularies in play:
- Pipeline stages (mockup): 生成/评测/选择期/组合/验证/上线/监控
- Funnel gates (PRD §2.3): 生成 → 纯度门 → 证据/成本门 → 去重/多重检验 → 选择期 → 组合门 → 留出门 → 最终确认 → 部署前复核
- Lifecycle states (FR6.2): proposed/evaluating/validated/champion/challenger/monitoring/decayed/disabled
- Verdict (architecture §4.2): promising/weak/dead/underpowered/incomplete; cohort: promotion_verdict
- Factor list filter: promising/weak/dead/decayed (decayed is a lifecycle state, not a verdict! mixing)
- Factory STAGES: 提案/评测中/选择期/留出验证/最终确认/Champion/Challenger/监控/衰减/停用 (mix of stages + lifecycle states)
The mockup mixes lifecycle states into verdict filters ("decayed" in 结论 filter; "verdict === 'decayed'" in JS) — but architecture verdict enum = promising|weak|dead|underpowered|incomplete. decayed is lifecycle. Also 'underpowered'/'incomplete' missing from filter/badges. Formality: adopt a canonical status vocabulary mapping table in the README: research object states vs member diagnosis vs promotion verdict vs lifecycle states, and use each in its right place. This is probably THE core "not formal" issue for pipeline nodes: the 7 nodes are one vocabulary, the factory distribution another, the list verdict another, lifecycle another — a reader can't tell which is the same concept.

18. **F007 five-stage loss (五阶段损失)** — 信号质量/组合转换/成本容量/时序稳定/执行实现 — these are the loss *attribution* dimensions that synthesis reports must carry (FR7.5, F007 FR-003). The console's overview claims to be the "全工作流闭环的实时呈现" but nowhere shows stage loss/attribution; the batch table shows 晋级/淘汰/成本否定 only. For the project's stated learning loop ("失败也是资产", "最大流失级"), the overview should surface the top loss stage / distribution per cohort. Recommend: pipeline node sub-lines or a small "loss mix" bar (per phase) fed by synthesis. This is the biggest content gap vs the PRD.

19. Also missing: 论题检查点 clock (M4 10 weeks / 100 effective independent candidates) — G7. That's a long-horizon governance metric; maybe too much for overview, but worth a mention as a candidate for the settings/project view or weekly report only. Eh — mention lightly.

20. **The 反馈弧 (purple) → claim**: README says 紫色反馈弧（证据库 → 归因复盘 → 新假设入队 → 回到生成，FR6.3-6.5 闭环）. Good. But purple is a *third* semantic color introduced beyond the stated design system: "单强调色（蓝）用于导航选中、主按钮、图表主线；语义色只保留两类：绿/红表示收益正负，琥珀表示告警/降级状态" — purple is not in the declared palette! The design system says single accent + green/red/amber, but the pipeline uses purple #7c3aed for the evidence library/feedback arc, and the compare page uses 4 colors (blue/green/amber/purple CMP_COLORS), and quantile bars use #10b981/#ef4444 (different greens/reds from tokens --green-line/#dc2626?), detail charts use raw hex (#2563eb stroke in svg code instead of var). So the design system's "single accent + 2 semantic" rule is violated in the most prominent component (pipeline) and others. Either the palette rule should be amended (purple = feedback/evidence semantics) or the colors tokenized. Formality finding: the CSS declares tokens, but app.js hardcodes hex colors (e.g., #2563eb, #dc2626, #9ca3af, #7c3aed, #10b981, #ef4444, #334155) — so theme changes (dark mode claim in README: "深色偏好若回归：设计 token 全部集中在 styles.css :root，可派生暗色主题而不动结构") would NOT actually work, because all charts/pipeline colors are hardcoded in JS. Concrete contradiction with the README's own claim. 

Let me double check: app.js uses '#2563eb' in renderDetail equity line, '#dc2626' drawdown, '#9ca3af' text fills, renderOverview: fbColor = "#7c3aed", '#e5e7eb', '#2563eb', '#eff6ff', '#111827', '#374151', '#9ca3af', '#f5f3ff'; strategy: '#10b981', '#334155', '#dc2626'; compare: CMP_COLORS. Yes — hardcoded. So "设计 token 全部集中在 :root，可派生暗色主题而不动结构" is false for everything rendered via JS/SVG. Good finding: tokenize chart colors via CSS custom properties read at runtime, or centralize in JS constants file.

21. **HTML has stray/broken markup**: 
- Line 273-274: `</table></div>` then `</div>` extra? Let me look: 

```html
    <div class="card">
      <div style="padding:12px 16px 0;">...
        ...
      </div>
      <table style="margin-top:8px;">...</table>
    </div>
    </div>   ← extra closing div?
  </section>
```
Line 263-275:
```
      <div class="sec">日志记录</div>
      <div class="card">
        <div style="padding:12px 16px 0;"><div class="filters" ...>
          ...selects...
        </div></div>
        <table ...>...</table>
      </div>
      </div>     ← line 274: this closes...? 
  </section>
```
Count: `<section id="view-settings">` ... tabs, tab-biz panel (`<div class="tab-panel active" id="tab-biz">...` closed), then `<div class="tab-panel" id="tab-ops">` opens at 253, contains 服务健康 sec + card (closed 260), hint, 日志记录 sec, card (opened 264, closed 273). Then line 274 `</div>` closes tab-ops. Then `</section>`. OK actually balanced: let me recount the tab-ops closing. Line 264 `<div class="card">`; inside: 265 `<div style=...>` contains 266 filters div, 267 select etc, 268 span, 269 `</div>` closes filters? Let me carefully recount from the read output:

```
264:    <div class="card">
265:      <div style="padding:12px 16px 0;"><div class="filters" style="margin-bottom:0;">
266:        <label>类型</label>
267:        <select id="log-type">...</select>
268:        <span class="hint" style="margin-top:0;" id="log-count"></span>
269:      </div></div>
270:      <table style="margin-top:8px;"><thead><tr>
271:        <th>UTC 时间</th>...
272:      </tr></thead><tbody id="log-rows"></tbody></table>
273:    </div>
274:    </div>
275:  </section>
```
And tab-ops opened at 253: `<div class="tab-panel" id="tab-ops">`, so 274 closes it. Balanced. OK no stray. Good, no defect there.

- In detail view: `<div class="fsh-legend">` uses ✓ ● ✕ · symbols. fine.
- Line 97: legend includes span "自「验证」起为组合级环节..." fine.
- index.html line 96 `<div class="flow" id="d-flow"></div>` with CSS .flow flex — but renderWorkflow injects fishbone into it; `.flow {display:flex; gap:8px...}` conflicts with fishbone wrapper? The fish-inner is inside fish-wrap inside flow. .flow has display:flex, so .fish-wrap becomes a flex item; overflow-x:auto on fish-wrap. Probably OK but the .flow flex+overflow adds an extra scroll container (fish-wrap has its own overflow-x auto) — nested scroll contexts; the .flow padding-bottom 6px. Minor. Actually `.flow` is `display:flex; overflow-x:auto` and its child `.fish-wrap` has `overflow-x:auto; min-width:990px` → the inner one scrolls, not the outer, unless fish-wrap is sized by flex. Since .flow is flex row and .fish-wrap is the only child with min-width from content (fish-inner min-width:990px), the outer may not scroll. Fine.

22. **Fishbone semantics**: single-axis with alternating nodes — the README says nodes 上下交错; the code alternates by index parity. The connector: `.fish-inner::before` horizontal spine at top:79px. The dots row `.fsh-dotrow` height 20px is the middle; slots top/bottom 70px each. So the spine passes through dots. OK. But the *arrows* between stages: the horizontal spine is a line; the direction of flow (→) is implied. The final node's right side: spine extends to right edge (right:14px of 11-col grid) → past last node (as noted). Also there's no "拒绝后终止" visual on the spine (a rejected stage's downstream nodes show as pending "未到达" — fine, and dot ✕ red).

But wait: for rejected factors, `flowStatus` returns "reject" only for the exact rejected stage; downstream = "pending" (未到达) — correct semantics ("流程终止" per README). OK.

23. **Mini-flow in factor table**: for a factor rejected at stage 1 (评级), shows 7 steps with first red then 6 grey — good. For decayed factor (kronos_rev_v2): reached=6, cur=6, verdict=decayed → all steps done green except stage 6 active with amber ring (warn). Tooltip "监控：已降权". Hmm — a *decayed* factor shows mostly green (通过) with an amber-active monitor stage; but semantically it was 降权 (demoted) — the mini-flow shows green "done" for all stages including 监控? No: stage 6 cur=6 → active (blue dot usually, but warn amber border). Its tooltip conveys. It's subtle but OK.

24. **Compare page**: fine. CMP_COLORS hardcoded as noted. cmp-table headers show up to 4; best highlight per row; "换手" has best:null (never highlight). OK.

25. **A11y/keyboard**: nav items are div with click handler, not buttons/links — no keyboard access; tab-btns are buttons (good); collapse button ok. Table row click for detail; checkbox for compare. For an internal tool, acceptable, but "formality" could include focus states. Minor.

26. **Clock**: setInterval updates UTC clock; fine.

27. **prefers-reduced-motion**: renderOverview returns early if reduce — but it has already rendered the static SVG; good. The lane-dash CSS animation is NOT disabled under reduced-motion (CSS has no media query) — .lane-dash animates stroke-dashoffset infinitely even with reduced motion. Minor a11y defect: add @media (prefers-reduced-motion: reduce) { .lane-dash { animation: none } }.

28. **Overview card paddings**: `style="padding:6px 8px 0;"` inline on the pipeline card — inconsistent with design system (cards 16/18). Intent: tighter padding for the graphic. Fine but inline styles sprinkled (line 160, 169, 192, etc.) — style hygiene minor.

29. **字体**: states "数字一律 tabular-nums" — `.num` class used on numeric cells; but many numbers lack .num class (e.g., `.big` has font-variant-numeric in CSS ✓; `.val` in fstage ✓; pipeline SVG numbers don't get tabular-nums but SVG text in the numbers (21px 600) — SVG text doesn't inherit CSS font-variant? It can if applied. Not applied to SVG. Minor.

30. **服务矩阵 buttons all disabled** — fine for mockup (design shows intended positions).

31. **The pipeline animation runtime cost**: 34 particles + 3 fb particles + falls, requestAnimationFrame forever, DOM nodes created/removed (falls create and remove SVG circles). Every frame updates attributes for 34+ elements. It runs even when the overview view is hidden (switching views doesn't stop rAF) — CPU burn on battery; and particles keep moving invisibly. For an always-open console tab, this is wasteful. Also when hidden, getPointAtLength still computed. Worth flagging: pause animation when view inactive / document hidden (visibilitychange). Concrete improvement.

32. **Number formatting**: pipeline "128" etc. plain; PnL "+6.42%"; OK.

33. **Factory page "初筛存活 47" sub "其余 81 个被纯度门 / 成本 / 查重淘汰"** — wait: 本周产出 128, 初筛存活 47 → 128-47 = 81. So "81 淘汰" = 128-47 ✓. So the pipeline node 2 extra "本周初筛淘汰 81" is consistent with THIS derivation. But then batch B-20260912 alone has 124 candidates; 9 prom of 124... and 本周 128 across batches with 47 surviving initial screen. OK so 81 is week-level. Then "评测 89 评测中" stock vs 128 weekly output — plausible (89 currently in evaluation queue from multiple weeks). Fine. But the batch table's dead 64 + cn 17 = 81 for ONE batch equals the WEEK's 淘汰 81 — numerically suspicious coincidence (or the fake data was copied). Eh, it's fake data; but a careful reviewer sees 81 twice with different derivations. I'll note consistency work needed, not enumerate every coincidence.

Actually let me recompute: 本周产出 128; 初筛存活 47; so week eliminations = 81 (128-47). Batch B-20260912: n=124, prom 9, weak 51, dead 64, cn 17. If dead 64 includes cn 17: 9+51+64 = 124 ✓ → dead includes cn. Then week eliminations 81 vs batch eliminations (weak? no weak=存活?) Hmm "初筛存活 47" — for the week. Weak/Dead are verdicts; what survives "初筛"? promising+weak? If 初筛存活 = prom + weak? For batch: 9+51 = 60 of 124. For week: 47 of 128. Plausible.
Week eliminations = 128-47 = 81 = dead+cn weekend total. Batch1: dead? + cn = (64 or 47)+17. If dead excludes cn: 64+17=81 = exactly batch1! If dead excludes cn then batch1 = 9+51+64+17 = 141 ≠ 124 → contradiction. So dead includes cn: dead=64 total incl cn 17. Then batch1 elim = 64. Week elim 81 = sum over visible batches? 64 + (0911: dead 62) can't be. Whatever — inconsistent under every reading except the "week 81 = 128-47" identity. Fine: I'll say "the fake numbers cannot be reconciled across three views (overview/factory cards/batch table) — pick one ledger and derive all aggregates."

Hmm, let me double check one more: STAGES 提案 214; overview node 1 extra "存量提案 214" ✓ consistent. Factory card says 候选 128本周; STAGES has no 128; BATCHES sum for 4 days = 425. "提案 214" as stock vs "本周产出 128" flow — compatible if 128 are last week's new proposals and 214 total proposals stock. Fine-ish.

34. **Left nav ordering**: 总览 / 监控 / 因子 / 设置 — but the README says nav = 总览/监控/因子/设置 and the IA table lists 策略运营/因子工厂/因子库/设置. The workflow order would be 总览 → 因子(工厂→库) → 监控 → 设置? The current order puts 监控 before 因子 — for a "research-first AI factory" product, maybe factory before ops. Eh, minor. Also the nav has icons; collapse works.

35. **总览 pipeline card is the only place using SVG animation**; maybe suggest replacing with static "stage table" alternative or a "weekly flow Sankey + gate budget" view — but the user may like the animation. My job: give suggestions. I'll present options: (a) formalize it (make it a real funnel: one consistent unit per row, gates as separators, budgets, loss attribution, no fake motion), or (b) replace with a two-part component: 月度漏斗表 (numbers = canonical, sourced) + 实时队列条 (small). I lean: keep a pipeline visual but redesign the node semantics: label the object of each segment (FactorDef 段 / PortfolioDef 段 / 部署段), show gate names between nodes, show budget (每周上限 5 · 已用), separate flow vs stock explicitly (e.g., "本周新增 128" as a ticker line above, stage numbers as stock), and drop pure-decoration particles OR repurpose them as *meaningful* (e.g., each particle = one batch or the animation triggered only on real events — но in a mockup with fake data...). Actually a cleaner idea: animate only on data change (event pulse), no continuous motion — "instrument" feel: static diagram + pulse when a stage count changes. And the field should show, for each stage, both current count and net 7d delta (↑↓) — that's "formal".

36. **北极星/核心指标 summary**: The user asked me to "深入分析这个项目的重要节点和关注点和核心指标". So I should produce a structured analysis:

**Important nodes (authoritative, from PRD/arch/F007):**
Gates & phases (in order):
1. ResearchSnapshot 绑定 (FR1.7/ADR-0007) — input identity; every experiment binds snapshot.
2. 方法论/PIT 门 (methodology_gate, F007 FR-002) + AST 纯度门 (FR2.4) — first rejection points ("preview/canonical" tier gate even earlier: FR-001).
3. 评测台+成本门 (FR3.1/3.2, F007 FR-005): cost_negative → dead regardless of IC.
4. 去重 + 多重检验 + cohort finalize (FR3.3, F007 FR-004): rejects still count in denominators; cohort OPEN→FINALIZED before promotion.
5. 选择期 (FR3.4): purged CV, stability.
6. 组合门 (FR4.2): marginal contribution to existing book; Top-K freeze (FR4.3); 换手预算/净额化 (FR4.4).
7. 留出 90d + 样本量三级裁决 (FR3.5): <30 UNDERPOWERED / 30-69 temp PASS (reduced paper only) / ≥69 trust; weekly cap 5 (FR3.4); append-only budget ledger.
8. 永久隔离最终确认 (FR3.4, architecture GATE→H): separate from holdout; isolation; FAIL → evidence library.
9. 部署前复核 (FR5.2): recent window newer than holdout; champion/challenger replacement triggers recheck; ≤1 day to dry-run (G5).
10. 信号缓存 + parity + run record (FR5.1/5.7): versioned cache keys; decision-time consistency; four buckets; kill-switch.
11. 监控/生命周期 (FR6.1/6.2): IC/收益 decay, thresholds → 降权/暂停/下线; decayed/disabled.
12. 归因复盘 + 反馈入队 (FR6.3/6.4/6.5): failure_stage/owner/mechanism; human review; back to FR2 with generation+1, counts to budgets.
Plus the cross-cutting: 证据边界 (preview/canonical, ADR-0006), manifest 内容身份 (FR7.1), 留出台账, synthesis_report (FR7.5).

**Core metrics (PRD §2.3 + FR7.5 synthesis):**
- North Star: rolling 28d new trusted effective-independent PortfolioDefs.
- 转化效率: 研究到证据 median; 证据到部署 ≤1d.
- 探索: nominal weekly ≥100; effective independent (OOS PnL clustering); source diversity.
- 漏斗: per-gate conversion; max loss stage (weekly report must name it); five-stage loss (signal quality/portfolio conversion/cost-capacity/time stability/execution implementation).
- 信任护栏: snapshot/manifest/holdout ledger/repro rate = 100%; lookahead tolerance 0.
- Ops: post-cost return, drawdown, capacity, backtest deviation, decay; signal IC rolling; staleness; inference latency; sync delay; cost drift.
- Risk: circuit breaker events; correlation guard; kill-switch.

And how the mockup maps (or fails to map) to these. I'll build a table: 核心指标 | PRD 出处 | mockup 落点 | 问题/建议. Keep it tight (≤5 rows per list cap? The user asked for deep analysis so tables can be longer, but AGENTS.md says cap lists at 5 items... "Cap lists at 5 items" — that's a guideline for lists; tables maybe exempt but I should still be economical. I'll aim for compact tables.)

**大布局建议 (layout suggestions):** Let me craft the top-level recommendations:

1. **总览的信息重心**: currently weighted to ops (2/3 cards + pipeline). Suggest a 3-band structure: ① 顶部证据/产出 band (北极星 28d 可信 Alpha、有效独立数、研究→证据周期、本周名义吞吐); ② 中部流水线 (gates + budgets + loss attribution); ③ 底部运营 band (策略执行/信号与数据/快照与批处理). Or keep three cards but rebalance: replace one ops card with "证据与门禁" card. Also add 留出预算/队列 (每周上限 5, 已用 n) since it's a scarce resource — budget visibility is key for "formal" process.

2. **Research/ops 分面标注**: per ADR-0005 and FR8.1, annotate each card/tile with its 真相源 and tier (canonical vs ops-live), e.g., a small "source chip" (manifest / TSDB / freqtrade). This directly addresses "哪个数字是真的" concern; the top bar should carry ResearchSnapshot + canonical 标识 (not just one dataset version).

3. **Pipeline lane fix** (the 7 nodes): make it a **gate-aware funnel** — two segments: FactorDef 段 (生成→纯度/成本门→选择期) and PortfolioDef 段 (组合门→留出→最终确认→部署复核→挂载), with gate names on separators, one consistent unit per row (all current stock), moving "本周新增 128/淘汰 81" to a flow ticker, budgets annotated, removal of decorative continuous motion or repurposing it as event pulses. Node count may become more than 7 — that's fine: gates are the story. Also fix 12→17 growth (don't sum stages), fix fake data consistency, make every number derivable from one ledger.

4. **术语统一 (vocabulary registry)**: one canonical table in README mapping 研究对象状态/成员诊断 verdict (promising/weak/dead/underpowered/incomplete + cohort promotion_verdict)/生命周期状态 (proposed...disabled)/流水线阶段 — and use consistently across pipeline, factory distribution, list filters, details. Fix the "结论" column wording (it's a diagnostic label; the auditable conclusion is cohort-level). Add underpowered/incomplete to filters/badges.

5. **细节 defect list**: fishbone 11-column dead space + spine overflow; README self-contradictions (landing page 总览 vs 策略运营; workbench vs no-todos; IA table "4 一级视图" vs nav labels); tokenization (hardcoded colors in JS vs claimed dark-mode-ready tokens); purplenot-in-palette; reduced-motion for lane-dash; animation continues when hidden; 10px low-contrast text; verify 门禁 row + "立即运行" vs FR8.4/README service list; stale CSS (.flow/.fstep, .pipe, .todo) unused; naming nav vs page (监控≠策略运营, 因子≠工厂/库).

Hmm, wait. Let me reconsider #5 verify 门禁: README decided "服务矩阵只列长驻服务（freqtrade / kronos-signal / data-collector / timescaledb / grafana）" — verify 门禁 is NOT in that list, yet SERVICES includes it row 6 with ops "立即运行". Two README statements conflict ("只列长驻服务" list excludes verify; but "门禁立即运行" mentions it in service health description section: "服务健康：可操作的服务矩阵（freqtrade 启停与强制单、Kronos/采集器重启、快照手动触发、门禁立即运行）"). Hmm — actually the README service-health bullet *does* mention 快照手动触发 and 门禁立即运行 as matrix ops, while the later bullet says matrix only lists long-running services and snapshot trigger is NOT in the matrix (日志记录 carries it). So README contradicts itself: bullet A says matrix has 快照手动触发 + 门禁立即运行; bullet B says matrix only long-running services (snapshot trigger not in matrix; carried by log). The mockup implements: matrix has verify 门禁 row (with 立即运行), no snapshot trigger row, and the hint mentions "快照手动触发" nothing... let me recheck index.html SERVICES: freqtrade/ksignal/dcollector/timescaledb/grafana/verify门禁. No snapshot. And help text mentions GPU 时段调度 etc. So mockup follows bullet B partially (no snapshot) but includes verify with 立即运行. FR8.4 concern + internal inconsistency. Also 快照作为每日 02:00 计划任务 (bullet B) vs "快照手动触发" op in bullet A — contradiction across bullets. Good.

Also: "每天 02:00 导出快照" — PRD says data_bridge export; timing not fixed in PRD; fine.

37. Also the overview pipeline node 6 (上线) shows "5 已挂载因子" while factory card 4 shows "2 Champion + 3 Challenger" = 5 — consistent. But the pipeline node 7 监控 shows "18 监控中因子" and STAGES "监控 18" — but then champion/challenger (mounted) are... also monitoring? The lifecycle semantics per FR6.2: validated → champion/challenger → monitoring?? Actually FR6.2 states enum: proposed/evaluating/validated/champion/challenger/monitoring/decayed/disabled. Hmm, "monitoring" as a state vs champion/challenger as states — overlapping? In FR6.2 list, "monitoring" is presumably the state for factors under live observation. The mockup uses 监控 18 vs champion 2/challenger 3 — 18 might be "非挂载但监控" (e.g., watch-list). Ambiguous. Flag: define relationship champion/challenger ↔ 监控 counts.

38. One more layout thing: the 总览 view's pipeline card has `padding:6px 8px 0` while the SVG is 268px; then `.grid.g3.mt` cards. The whole view max-width 1400, so pipeline spans 1400. nodes from x=70 to 1130 in a 1200 viewbox centered in ~1384 content (1400-2*8card padding?) Whatever.

39. Check the "工程进度表达" idea: maybe suggest adding a "本周/本季漏斗报表" link to synthesis; FR7.5 weekly report — the console should render synthesis_report (F005 owns rendering; F007 provides). The overview should link/render key synthesis aggregates (cohort funnel, five-stage loss, max constraint). Because the current overview has no cohort concept at all — and F007 centers on cohorts. The mockup has no cohort anywhere (batches are not cohorts; B-20260912 is a batch). Actually "评测批次" table ≈ daily runs; cohorts are preregistered evaluation groups. Missing cohort dimension is a notable gap for formality: the promotion verdict is cohort-level. Suggest: factor detail or factory page shows cohort status (OPEN/FINALIZED) and membership; the pipeline/loss numbers keyed by cohort. Hmm, maybe for the blueprint this level is too deep; but at least the factor list could show cohort. I'll mention as "consider".

40. Number one question re "重要节点": since the project *is* a pipeline of gates whose credibility hinges on budgets (留出预算, weekly caps, permanent isolation), the console's most important job is **making gate accounting visible and un-fudgeable**: which gates consumed, what's the budget state, what failed where (five-stage loss), and what is canonical. The mockup currently makes visible: stage counts (muddled), verdicts (partial), evidence tray (decorative), logs (good). Missing: budget/accounting, loss attribution, canonical tier annotation, cohort state. That's my headline for the deep analysis.

41. Suggest also: "关注点" (concerns) — list the decision-relevant attention points the console should serve:
- 今天：运营是否健康（引擎/信号/数据/风控）→ current ops cards do this.
- 本周：工厂产能与漏斗健康（名义/有效独立/来源多样性/最大流失级）→ partially missing.
- 每 cohort：证据质量（拒绝者分母、成本主导、留出预算使用、UNDERPOWERED 比例）→ missing.
- 北极星：28d 可信 Alpha 与停止时钟 (G7 检查点) → missing.
- 审计：一切动作可追溯（日志+manifest 检索）→ logs present (good), but no manifest search from overview/detail? Detail has 证据链 kv. OK.

Let me also verify "每周晋级上限 5" vs PARAMS "每周留出晋级上限 5" ✓ consistent. And PARAMS "样本量裁决阈值 30 / 69 笔" ✓. Nice.

42. The strategy page strip: "陈旧信号 7（越界已置空）" — matches architecture §4.3 staleness semantics (NaN). Good formality point: it follows the spec. Actually wait — "越界已置空" = set to NaN/no-signal ✓. 

43. Detail page metric cards: 6 cards g6: Rank IC 均值/ICIR/IC 正率/成本后多空收益/换手率/毛交易样本 — with power verdict on 毛交易样本 (UNDERPOWERED etc.). Good. Missing: breakeven cost (F007 FR-005 asks breakeven), deflated significance, cohort context; but it's a factor detail view — the blueprint level may be OK. Mention in deep-dive as "consider adding breakeven cost + cohort".

Actually F007 FR-005: "输出零成本/maker/taker 三档、资金费率、breakeven cost、换手、持有期与适用的容量代理". The mockup detail cost card lists Taker/滑点/资金费/成本裁决 only — missing 三档 (zero/maker/taker), breakeven. Detail chart "成本分解 cm-v1". Suggest align with F007's cost output set (since F005 can only render F007 outputs — and if F007 does not output those fields in a consumable way... it does per FR-005. So console should render them). Concrete: add maker/zero-cost rows + breakeven to the cost decomposition; the compare table could use 成本后收益 ✓.

44. Also factories' "流水线状态分布" bars: cls "hot" for 留出验证/最终确认 (amber), ok for champion/challenger (green). Fine. But 10 stages: 提案/评测中/选择期/留出验证/最终确认/Champion/Challenger/监控/衰减/停用. The list mixes current-stage stocks with outcome states; ALSO it omits the gate-level losses (成本否定 etc.) that the batch table shows. Redundancy vs the overview pipeline (same-ish info). Maybe unify: one canonical "pipeline" component used in both overview and factory with different density.

45. **One more real inconsistency**: README claims "总览...不含任何待办类内容" ✓ mockup has none. README bullet "首屏命名「工作台」" contradicts. And the strategy page titled 策略运营 with nav 监控. Also README 交互说明: "`data-goto` 的「查看全部 →」跳转对应视图" — mockup has "进因子工厂 →" in 昨夜产出 card. fine.

46. Check "深链 #factors / #detail / #strategy" — actual view ids: factory/detail/compare/overview/strategy/settings. README says "#factors"! `#factors` doesn't exist → hash handler: `if (h && document.getElementById("view-" + h))` — "view-factors" doesn't exist → nothing happens, lands on default overview. So the README documents a broken deep-link (#factors should be #factory). Concrete defect. Nice catch. Let me double-check index: id="view-factory" — yes; README line 11: "支持 `#factors`、`#detail`、`#strategy` 等 hash 深链直达单页" — #factors broken (should be #factory). Also #detail: view-detail exists but renderDetail uses default selectedFactor; click nav absent for detail — deep link works via gotoView branch? In the hash init: `var navItem = document.querySelector('.nav-item[data-view="' + h + '"]'); if (navItem) navItem.click(); else gotoView(h);` — for h=detail, no nav item → gotoView("detail") → shows view-detail. OK works. #compare works similarly. So only #factors is wrong in README. 

47. Let me also double check the claim in README: "因子库以「生命周期进展」列替换「结论」列" — but the mockup factor table still HAS 结论 column? Columns: 选/Factor ID/假设/生成器/口径/Rank IC/ICIR/IC 正率/成本/生命周期进展/数据版本. No 结论 column ✓ replaced. But the filter still says "结论" with promising etc. ✓ so the filter remains named 结论 — contradicts "替换结论列" intent? The decision says replace the column, and the filter (结论/生成器/数据版本 三维过滤) still calls it 结论. Minor naming. Also earlier decision "原实验漏斗更名因子工厂" ✓. 

48. Small: factory 4 cards - card 2 "初筛存活 47" sub "其余 81 个被纯度门/成本/查重淘汰" — 128-47=81 ✓. Card 3 "组合验证中 12" sub "留出验证 90 天 · 其中最终确认 5" — as discussed, contradictory ("其中"). Card 4 "在跑与监控 2 Champion · Challenger 3 · 监控 18 · 有效独立数 23". So the 4 cards tell: 128 → 47 → 12 → 2. Pipeline overview tells 128 → 89 → 47 → 12 → 17 → 5 → 18. Different number sets (89, 17, 5, 18 appear only in overview; 47 etc. in both). The two components don't obviously derive from one another (e.g., factory card shows 12 组合验证中; overview 组合 12 ✓ same; factory doesn't show 89/17/18). Fine-ish but should share one source.

OK — I also should double-check the exact seven nodes list once more (app.js lines 602-610):
1. 生成 128 本周产出 存量提案 214
2. 评测 89 评测中 本周初筛淘汰 81
3. 选择期 47 存续 180 天窗口 · 查重通过
4. 组合 12 组合验证中 边际贡献评估 + 冻结
5. 验证 17 留出 + 最终确认 每周晋级上限 5
6. 上线 5 已挂载因子 PM-007 · PM-009 dry-run
7. 监控 18 监控中因子 PnL +6.42% · 衰减 41 · 停用 96

And MACRO_STAGES for detail fishbone = same 7 names. The README's claimed alignment: "生命周期模型 = 7 个宏观阶段：生成 → 评测（含纯度/成本/查重子门）→ 选择期 → 组合 → 验证（留出 90 天 + 最终确认）→ 上线（部署复核 + 挂载）→ 监控。对齐 PRD FR3.4 的验证顺序，不把子门禁升格为阶段".

My analysis on this claim: it does NOT fully align with FR3.4 sequence because:
- FR3.4: "FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef → PortfolioDef 最终 90 天留出 → 永久隔离最终确认窗" + 部署前复核 (FR5.2) + 每周上限 5 for final holdout entry. The macro-merge of 留出+最终确认 into one "验证" stage and 部署复核 into "上线" is defensible as *display* simplification ONLY IF the two hidden gates remain visible as internal states with their own budgets/status. Currently: 验证 node merges two windows and shows merged count 17 (which double counts!), and 上线 merges 复核+挂载. The claimed "不把子门禁升格为阶段" is fine; but the merge introduces a counting error, and the merge hides: (a) 最终确认 is a *permanent isolation* budget — architecturally distinct (no re-reading), (b) 留出 has the weekly cap 5 (appears as extra text but attached to wrong node number), (c) 部署复核 can FAIL (→证据库) and has the ≤1 day SLO.
- Also "评测" claims to include 纯度/成本/查重子门 — but PRD funnel counts them as distinct rows with distinct losses (纯度门, 证据/成本门, 去重/多重检验 as separate conversion levels). Since the product's metric is "分级转化率" per gate and "最大流失级" (FR3.8 weekly must identify), collapsing three loss points into one "评测" node makes the funnel *unable* to express per-gate conversion. That's a substantive formality issue: the console can't show which gate is the biggest killer — which is literally one of the PRD's required outputs. Strong argument. Recommend: show sub-gates as loss annotations (mini stacked bar or tooltip breakdown: 纯度 x / 成本 y / 查重 z / 方法论 w) on the 评测 node. That preserves the 7-macro-stage visual while restoring per-gate loss.

So my headline critique of the 7 nodes has three pillars:
(a) **Accounting errors**: mixed stock/flow units; 17 double count; un-derivable aggregates across views; 报告 units switch (Factor→Portfolio→Deployment) without mark.
(b) **Missing gate semantics**: budgets (每周上限/隔离性), per-gate losses (五阶段损失 + 最大流失级), deployment recheck as a fail point, sample-size three-level adjudication visibility.
(c) **Presentation register**: continuous decorative animation + pulsing halos + particle confetti = game-y; violates the project's own "信息密度优先于视觉表演" and "证据优先" ethos; plus it has a perf/energy cost and a11y gap (reduced motion) — recommend event-driven pulses or static informative diagram.

Plus the vocabulary inconsistency across views and the README internal contradictions.

Now — how to structure the answer? The user asked (in Chinese):
1. 大布局层面的建议
2. 7 nodes 审视 (formal?)
3. 深入分析重要节点/关注点/核心指标

The user is ADHD-profile per AGENTS.md global instructions: lead with answer/next action; number multi-step; cap lists at 5 items; no preamble. But this is an analysis request where "explain fully when asked" — they asked for deep analysis ("深入分析"). So a thorough structured response is right, but keep it scannable: short lead, then sections with tables/bullets, end with ONE next action.

Language: user writes Chinese; respond in Chinese.

Also note AGENTS.md says "End with one next action doable in under two minutes." — e.g., "如果你想，我可以先改一版：把总览流水线换成 9 门禁无动画漏斗 + 数据一致性重算，改 3 个文件，约 xx 分钟" — or ask which fix batch to prioritize. Actually the request was analysis-only; final should propose next action (pick a direction). Since this is evaluation intent — propose → wait for confirmation. Good.

Length: This is a deep review; I'll aim for a comprehensive but tight structure (~150-250 lines). Use tables sparingly (5-row caps where possible — I can bend for the 7-node table since it's inherent; actually 7 rows for the pipeline node table is fine as it mirrors requested item; the "cap lists at 5" is a guideline, tables of data can exceed if needed. I'll try to fold to 7 rows max).

Let me draft the content.

---

**结构:**

1. 一句总判断 (lead): 用户直觉成立——7 节点流水线目前是"装饰性动画 + 口径不统一的数字"，不是"证据管线仪表"；三个硬伤：口径混乱（存量/流量混排、17=12+5 重复计数、跨视图数字对不上）、门禁语义丢失（留出预算/永久隔离/部署复核/五阶段损失）、演示化过度（粒子动画违背自家"信息密度优先"原则）。并指出 README 自相矛盾（落地页 总览 vs 策略运营；工作台 vs 无待办；#factors 死链）。

2. 大布局（全局）审视 + 建议 — maybe 5 bullets:
   - 总览重心：运营重、研究轻；缺北极星。建议三段带。
   - 各页面与真相源/层级标注缺失（canonical vs ops、manifest 追溯）— 顶栏只有单数据集版本，应带 ResearchSnapshot。 
   - 术语四套词汇表（阶段/verdict/生命周期/门禁）混用 — 需要 vocabulary registry。 
   - README 内部矛盾 + 死链 #factors + 落地页冲突 — 设计资产自身要"决策日志化"（supersedes）。
   - 视觉 token 声明与实现不符（JS 硬编码色板 → 暗色不可派生；紫色超出调色板；10px #9ca3af; .lane-dash 无 reduced-motion；11 列死区）。
   
   Maybe split: 布局层 vs 细节缺陷. Keep ≤5 bullets each.

3. 7 节点逐个体检 (table): 节点 | 数字语义 | 问题 | 建议。That's 7 rows. Plus intro on the three pillars. Then concrete proposed re-design of the lane: propose either "7 宏观阶段 + 门禁分隔/预算/子门损失注记" or a 9-10 门禁正式漏斗. Give the proposed node semantics list. I'll propose a concrete alternative spec:

   Proposed lanes:
   - Keep 7 macro stages but fix semantics: each node shows 存量 (current object count), a 7d 变化 (↑/↓), and gate losses in tooltip/subline; separators show gate names; one segment break: FactorDef / PortfolioDef / Deployment.
   - Or elevate to gate view with 9 stops: 方法论+PIT / 纯度 / 成本 / 查重 / 选择期 / 组合门 / 90d 留出 (budget 5/wk) / 最终确认 (隔离) / 部署复核 → 挂载. 9-10 stops is arguably the formality the user wants ("正式").
   - Numbers: replace fake inconsistent data with one ledger; e.g., min example table showing coherent numbers (I can sketch: 提案 214 → 本周新 128 → 评测中 89 → 选择期 47 → 组合门后待留出 12 → 留出中 7 · 最终确认 5 → 挂载 5 (2 champ / 3 chall) → 监控 18...). Hmm, I shouldn't invent new numbers too precisely; better: state the rule "所有数字必须可由同一台账推导，且每节点注明对象类型与单位（存量/本周流量）".

   Also budgets: 留出预算每周 5 → show "本周 3/5，顺延 2"; 永久隔离 → show lock icon + "只读"; 部署复核 → show SLO ≤1d and pending count.

4. 重要节点/关注点/核心指标 深度分析:
   - Table A: 项目真正的关键节点（权威顺序，12 gates compressed maybe 10 rows) — but cap: I'll write as a compact pipeline string + 5 highlight notes on the ones with "hard semantics" (成本否定=直接 dead; 拒绝者入分母; cohort FINALIZED 才可晋级; 每周5+append-only台账; 永久隔离; 部署复核≠确认通过; preview/canonical 隔离; 样本量三级).
   - Table B: 核心指标 map: 北极星 / 转化效率 / 探索能力 / 漏斗健康 / 线上结果 / 信任护栏 → PRD 出处 → mockup 现状 → 建议落点. 6 rows.
   - "关注点"=the console's jobs: 今天/本周/cohort/北极星/审计 — 5 items, with mockup coverage check.
   Then: 总览缺的关键读数清单 (shortlist): 北极星 28d、有效独立数、最大流失级、留出预算、UNDERPOWERED 计数、部署复核队列。 

5. 建议的下一步 (one action): offer two options: (a) 我直接改设计稿（本轮交付：流水线重构为门禁化漏斗 + 数字一致性 + README 矛盾清理 + 死链/列宽 bug），约 30–40 分钟；(b) 先只出"流水线语义规格"一页纸（节点/单位/预算/损失字段 + 数据字典），你审完再动稿。推荐 (b)→(a)? Or recommend (a)? The user asked analysis; the next step is their call. I'll recommend: 先定语义规格再改稿 — one option; and give the exact files. Under 2 min action: "确认走 A 还是 B" is not a "doable action"... The guideline: end with ONE next action doable in <2 min. E.g., "下一步（<2分钟）：告诉我按 A 还是 B 走；若 A，直接说'改稿'我就开工。" That's fine.

Let me also reconsider: should I check with the user’s selection #20 of F004 design.md? The system reminder says the user selected line 20 in F004 design.md (empty). The user's message didn't reference F004. I think it's noise — the user opened that file and then asked about 设计稿. My answer doesn't need F004. Skip.

Also "当前项目的设计稿" = ui-mockup. Confirmed by "总览里的动态流水线里的7个节点". Good.

Now, let me double check a couple of factual claims before writing:

A) Fishbone 11 columns: `grid-template-columns: repeat(11, minmax(88px, 1fr))` — but only 7 .fsh-col children → 4 empty tracks. And spine spans full width. Let me re-verify app.js renders 7 cols: MACRO_STAGES has 7 entries; cols = map → 7 `.fsh-col` divs. Yes. So 11 tracks, 7 filled. Confirmed defect (or intentional extra space? min-width 990 = 11*90; with 7 cols at 141px = 987. Hmm interesting: minmax(88px,1fr) with 7 cols in a 1400px container → each 1fr = 200px (11 tracks → 127px each). Actually with 11 tracks and container ~1344px (1400-56 padding?), 11 tracks ~122px each; 7 cols use 854px; 4 empty tracks 488px. The spine ::before spans left:14 right:14 across all 11 → extends ~480px past last node. Even if the author intended wider tracks via 11 tracks... no, extra tracks are just empty. Confirmed.

Wait — maybe the intent: labels above/below need ~88px min each and they wanted 11 to make the total min-width 990 for scroll. min-width:990px = 11×90. If they used 7, min-width would be 7×90=630. Their min-width 990 + 11 columns suggests leftover from an earlier 11-node fishbone (maybe 10 gates +). So flag as "看起来是旧版 11 节点残留：7 个节点占 11 列，轴线延伸到空白区" — good.

B) README contradictions:
- "首屏命名「工作台」：定位是个人工作台（今天需要关注什么），不是系统总览；" 
- "左树 4 项（总览 / 监控 / 因子 / 设置）...落地页 = 总览；"
- "移除「工作台/总览」页，落地页 = 策略运营：..."
- IA table: "一级视图共 4 个：策略运营（落地页）/ 因子工厂 / 因子库 / 设置。"
Yes. Contradictions among: 工作台-first-screen, 总览-landing, removed-total-landing-strategy, table-landing-strategy. The built file: landing = 总览 (active class on overview view + nav active on 总览). So README is stale in ≥2 bullets, or the mockup is stale vs decisions. Either way: unresolved.

- "服务矩阵只列长驻服务（freqtrade / kronos-signal / data-collector / timescaledb / grafana）；快照导出是每日 02:00 的计划任务...不入矩阵" vs earlier bullet "服务健康：可操作的服务矩阵（freqtrade 启停与强制单、Kronos/采集器重启、快照手动触发、门禁立即运行）...". Contradiction (快照手动触发 vs 不入矩阵). Mockup: verify row present (contradicts "只列长驻服务" list), no snapshot row, and a "立即运行" op button for verify (which contradicts FR8.4? FR8.4: 门禁与统计裁决不出现在任何可点击路径上；界面只呈现裁决结果，不提供裁决按钮. "立即运行" is a trigger not a verdict button — borderline; the README's own FR8.4 落点 says "「验证结果」面板只读呈现最近一次 python3 tools/verify.py 的结果" — a run trigger contradicts "最近一次...结果"只读 spirit; also running the gate from a browser is a production-ish action requiring audit per FR8.3? Eh, flag as "需在 F006 spec 明确" rather than definite violation. I'll phrase carefully: "门禁立即运行按钮与该稿自称的 FR8.4 红色线存在解释空间，需要显式裁决：要么去掉按钮（只读），要么作为受审计操作（写入 FR7.4）并在 README 说明。"

- #factors dead link: README says supports "#factors ... 深链" but view id is view-factory. Confirmed: hash #factors → document.getElementById("view-factors") null → no navigation (stays default overview). Actually wait: `if (h && document.getElementById("view-"+h))` — null → skip entirely → default overview shows. So #factors silently broken. ✓.

C) JS hardcoded colors vs README claim "深色偏好若回归：设计 token 全部集中在 styles.css :root，可派生暗色主题而不动结构". app.js hardcodes: #2563eb, #10b981, #dc2626, #d97706, #7c3aed, #334155, #9ca3af, #111827, #374151, #e5e7eb, #eef0f2, #eff6ff, #f5f3ff, #b45309? (no), #ef4444, #fecaca? (css). Confirmed plenty. The claim is false for charts & pipeline. ✓.

D) Purple not in declared palette: styles :root has no purple token; README: "单强调色（蓝 #2563eb）...语义色只保留两类：绿/红表示收益正负，琥珀表示告警/降级". Pipeline uses #7c3aed (purple) for 证据库/反馈弧 and CMP_COLORS includes purple. So the most distinctive semantic (feedback loop) violates the declared palette. Either amend palette doc or add token. ✓ minor but worth listing under "形式统一".

E) 10px text: pipeline extra font-size 10 fill #9ca3af; mlb 10px. Contrast #9ca3af on white/#fff ≈ 2.54:1? Let me compute roughly: #9ca3af luminance: r=156,g=163,b=175. Relative luminance ~ (0.2126*0.34^2.2ish)... I'll just say "远低于 4.5:1（约 2.5:1）" — commonly cited as ~2.8:1. Let me be safe: "对白底对比度不足 3:1". Good.

F) Animation continues when view hidden: rAF loop always runs; renderOverview called once at init; switching views doesn't cancel. ✓. Also no document.hidden pause. Suggest visibilitychange / IntersectionObserver or pause when view not active.

G) lane-dash lacks reduced-motion CSS ✓ (only JS early-return for the particles; the CSS dashed lane still animates via @keyframes laneflow). Also halo pulses only via JS (stopped by reduce). OK.

H) Data inconsistencies — let me nail the strongest, simplest-to-verify ones for the response (I don't want to overclaim; pick 3 crisp ones):
   1. 验证 node 17 = 12(组合/留出存续) + 5(最终确认) — 若 5 是 12 的子集（工厂卡"其中最终确认 5"），则 17 重复计数；若 5 与 12 不相交（分属两个窗口），则工厂卡"其中"错误。两种读法必有一处错。Also 12 同时出现在"组合"节点与"留出验证"（STAGES）里。
   2. 上线 5（已挂载因子）= 最终确认 5 同数，且由 Champion 2 + Challenger 3 组成 — 三个不同概念同为 5，读起来像同一批对象走完流程，实际对象不同（PortfolioDef vs 挂载策略），需区分。
   Hmm, is that fair? It's fake data; the coincidence is misleading. Fine as a "readability" note.
   3. 昨夜产出卡 "124 候选 · 晋级 9 · 淘汰 64 · 成本否定 17"：64+17 与 124 的关系无法从 UI 判断（要么 64 含 17、要另外相加）；批次表同批次列（9/51/64/17）也无法与 124 对齐成会计恒等式显示（9+51+64=124 若 64 含 17）。建议表格显式给"合计"或层级说明（成本否定 ⊂ 淘汰）。Also 本周产出 128 vs B-20260912 124 vs 四批合计 425 — "本周"口径没有说明（128 为何不等于可见批次和）。
   4. Overview "本周初筛淘汰 81" = 128-47 ✓ but batch B-20260912 的 dead 64 + cn 17 = 81 exactly — suspicious duplication; a reader will think the pipeline is echoing one batch. Meh, mention briefly under "数字应来自单一台账并做恒等式说明".

   Also 有效独立数 23 sitting as auxiliary text next to "监控 18" — 23 = 2+3+18 coincidence, could be misread as sum. Probably mention: 有效独立数 deserve its own metric slot.

I) Naming: nav "监控" vs page "策略运营" vs README IA "策略运营"; nav "因子" vs heading "因子工厂"+section "因子库". Also README calls page 因子工厂/因子库 as separate IA rows but they're one nav page. Suggest decide: nav labels = page titles.

J) The overview title/sub: "总览 | 全工作流各阶段运行情况" — sub says 各阶段运行情况; fine.

K) The strategy page top strip uses 推理耗时 1.76s/次 — real F004 concern (CPU inference 3.4–7.2s per F004 design; mockup says 1.76s — fake data, but maybe worth noting it conflicts with the project's actual measured CPU latency; if the mockup is the "end-state" with GPU it's fine. Eh skip — too pedantic. Actually F004: CPU 推理实测 3.4–7.2s/次. Mockup 1.76s/次. If kept as fake it's fine, but it might mislead. Skip.)

L) "衰减 41 · 停用 96" in 监控 node extra + STAGES bars — cumulative counts (41/96) popped into a node whose number is a stock (18). Same mixed semantics pillar. ✓.

M) The 证据库 tray: "累计淘汰 306" — 306 = 41+96+... or from batches? Unclear derivation. Also tray label "证据库 · 归因复盘" merges two things: 证据库 (rejection archive) and 复盘 (activity). Acceptable shortcut.

N) The overview card 信号与数据: "0.038" 信号预测力 + "采集延迟 0.8s · 同步 42s · 陈旧信号 7" — 4 metrics crammed; 7 陈旧信号 should maybe warn if threshold? PARAMS: 陈旧度上限 4 根 K 线; 7 signals flagged "越界已置空" (strategy strip). OK fine.

O) 服务矩阵 metrics: "freqtrade 引擎 今日 -0.31% · 持仓 4 · 同步滞后 42s"; "kronos-signal 1.76s/次 · 滚动 IC 0.038". Reasonable.

P) One more possible issue: 设置页 tab "业务配置" vs heading "设置 | 业务配置与项目运维" ✓ fine. PARAMS groups: 交易风控/验证门禁/成本模型/信号执行/交易宇宙/组合工厂/通知 — good coverage; missing 数据与导出 (snapshot schedule)? Minor.

Q) The compare view: "对比（0）" button disabled initially but compareSet pre-seeded with 2 factors (FACTORS[0], FACTORS[2]) so button shows "对比（2）" enabled on load — and factor table checkboxes pre-checked. Fine for demo. renderCompare called at init populates even though view hidden. OK.

R) Big-picture IA: 4 nav items. README decision "移除工作台/总览" conflicts with built reality. My recommendation options: (1) keep 总览 as landing but rename to something honest + fill with the missing research metrics; (2) truly remove and make 策略运营 landing (then where do pipeline/evidence metrics live? A "研究" landing?). Actually the strongest IA question: where does 北极星 lived? Probably 总览. And ADR-0005 says ops readings shouldn't be in research console... but blueprint merges faces. The README itself flag "注意与 PRD 的张力" for human-review-as-log. Fine.

Let me also think: should the "总览" show 待办类? The design decided no todos — human review shows as records in log. Given the PRD tension already flagged in README, I won't re-litigate; but I might note: 留出预算/复核队列 is not a "todo" but a resource state — showing budget is not the same as showing todos, and it's arguably required for formality. Good nuance.

S) Presentation of numbers in the lane: color #2563eb for all numbers; no semantic encoding of status (e.g., bottleneck = amber). "站点存量" static. Could add: 存量相对上周变化箭头; bottleneck highlight; gate budget utilization. OK.

T) 大布局 suggestion one more: the four views' vertical rhythm: view-head (h1+sub) then content; factory has no KPI strip alignment issue... fine.

U) There's also the question: 流水线 lane as the ONLY overview centerpiece is 268px tall showing 7 numbers — vs a dense "漏斗报表" that could show 10 gates × (存量/本周+/-/拒绝原因) — the formal trade. Present as the core recommendation.

V) For "重要节点" deep analysis, I should ground with quotes and emphasize the **gates with irreversible/hard semantics**:
1. 成本门: cost_negative ⇒ dead regardless of IC (architecture §4.2; F007 FR-005). Console: cost badge in list ✓; but pipeline lacks cost-loss count.
2. 多重检验/cohort: rejects count in denominators; promotion only via cohort promotion_verdict after FINALIZED (F007 FR-004 / arch §4.2 note). Console: no cohort presence — biggest formal gap for research console.
3. 留出门: weekly cap 5 + append-only ledger + 样本量三级 (<30/30–69/≥69). Console: cap in text ✓, three-level in detail card ✓, but no budget usage bar; 30-69 temp PASS semantics not surfaced in list (verdict enum lacks underpowered).
4. 永久隔离最终确认: isolation, no re-read. Console: merged, invisible.
5. 部署前复核: ≠ final confirmation; recent window; champion replacement retriggers; SLO ≤1d (G5/SC "最终确认通过至 dry-run ≤1 天"). Console: merged into 上线; SLO absent.
6. preview/canonical: every number must declare tier; research views canonical-only. Console: absent — suggest tier chips.
7. 证据库 → 复盘 → 入队 (generation+1, counts into budgets). Console: present ✓ (tray/arc) — credit where due.
8. manifest 内容身份/可追溯 (FR7.1/7.2): detail page shows manifest kv ✓ — credit.

W) 核心指标表 (as analyzed above). Let me build concise mapping (PRD row → console presence):
- 北极星 可信 Alpha 28d → 缺 (只出现 PnL) → 建议首页首屏。
- 转化效率（研究→证据中位时长; 证据→部署 ≤1d）→ 缺 → 建议 overview/kpi。
- 探索能力（名义 ≥100/周 + 有效独立数 + 来源多样性）→ 名义=本周产出128 ✓；有效独立数=脚注 (工厂卡) △；来源多样性 缺 (生成器列有但是不聚合) → 建议升格。
- 漏斗健康（分级转化率 + 最大流失级 + 五阶段损失）→ 阶段存量 ✓ (口径乱) ；流失原因 缺 → 建议门禁损失注记 + synthesis 渲染。
- 线上结果（成本后收益/回撤/容量/偏差/衰减）→ 策略页 ✓ 部分（容量/回测偏差缺）。
- 信任护栏（快照/manifest/留出台账/复现率 100%、前视 0）→ 顶栏数据版本 ✓、manifest 详情 ✓、留出台账 仅在 detail 提示 + logs △ → 建议"完整性状态"块（如 快照有效/Ledger 孤账=0/复现率）。
- （附加 F007）五阶段损失 + 最大约束 → 缺。

X) One more: "关注点" list maybe: 
- 产能 vs 有效探索的区分（名义/有效独立/来源）
- 失败结构与停止时钟（成本主导 or 假设枯竭 or 可信存活；G7 检查点）
- 证据预算（留出周上限、隔离窗、样本量级别）
- 部署时滞（复核 SLO、champion 轮换）
- 口径单一（manifest 追溯、canonical 边界）
That's 5. 

Y) For the "7 节点" section, I'll give a table: 节点 | 现数字 | 问题 | 建议（保持宏观 7 段的话怎么改）。Problems:
1. 生成: 128 本周产出（流量）与存量提案 214 混排；与工厂卡/批次对不上 → 节点统一为存量，流量单独放"本周新增"条；明确对象=HypothesisDef/FactorDef。
2. 评测: 89 评测中 + 淘汰 81（流量）；纯度/成本/查重三子门无损失拆分（PRD 要求指认最大流失级）→ 子门损失注记/展开。
3. 选择期: 47 存续 + "查重通过"（查重属评测）；→ 去掉查重、给窗口与转化率。
4. 组合: 12 "组合验证中"（其实组合门在选择期数据上；验证是下一步）→ 改名"组合门/冻结中"；对象切换点标注。
5. 验证: 17 = 12+5 重复计数嫌疑；留出(90d/周上限5) 与 永久隔离最终确认 两种窗口合并；→ 拆成两个节点（或子节点），预算显示（本周 x/5），对象=PortfolioDef。
6. 上线: 5 = 2 Champion + 3 Challenger 与"已挂载"混叠；部署前复核（可失败、SLO≤1d）不可见；→ 拆"部署复核"与"挂载/运行"，显示复核队列与失败出口。
7. 监控: 18 存量与衰减41/停用96（累计）混排；PnL 放这里偏运营；→ 只留监控存量 + 生命周期动作计数；衰减/停用作为状态迁移（或并入证据库复盘输入）。

Actually wait — is 组合 stage "组合门" occurring before 留出? FR3.4: FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef → 留出. Yes 组合门 = after selection. Node fine, just naming/object clarity.

Z) Also propose: the lane's feedback arc is good conceptually (unique closing loop); keep but formalize: label the loop with SLA: "复盘→入队 ≤N 天；generation+1；计入试验预算" and metrics (本季复盘12次/入队9). Present in tray text already. Fine, minor.

Additionally, I want to propose an explicit **redesigned node data contract** (what each node shows): for each stage: 名称、对象（FactorDef/PortfolioDef/DeploymentRun）、存量、7d 净变化、等待中/进行中拆分、门禁拒绝数（分原因）、预算（若适用）。And a data dictionary line: all numbers from `v_funnel_status` (experiment_store 投影) — the README already maps endpoints; my addition: include gates/budgets/loss in that view. 

Also the format: maybe show a small ASCII of proposed lane:

```
[FactorDef 段]─────────────────────────────────────────────[PortfolioDef 段]──────────[执行段]
 生成 ─纯度门─▶ 评测 ─成本/查重门─▶ 选择期 ─组合门─▶ 冻结PortfolioDef ─90d留出(3/5)─▶ 最终确认(隔离) ─部署复核(≤1d)─▶ 挂载 ─▶ 监控
  128          89            47             12                7                5              2              5         18
  ↑存  ← 本周新增 128 / 本周拒绝 81（纯度 x / 成本 y / 查重 z / 方法论 w）
```
Something like that. Since the user says "7 个节点" maybe keep 7 visually but with gate sub-annotations... I'll present both options: A) 保 7 段、补语义（轻改）; B) 升格门禁视图（9-11 站，正式）— recommend B for "正式感", A as lower effort. Actually the user said "我总觉得不是很正式" — they want formal. So recommend B strongly, with A as fallback.

Also mention: replace decorative continuous animation with **事件脉冲**（数据变化时闪一下）or keep subtle; and remove the "落站脉冲" halo animation? Keep option.

Also: the lane currently has NO axis/units legend — add small caption "数字为存量（canonical 台账）· 更新于 xx:xx" and 来源 chip. Formal.

Now, importantly — the user asked "看看从大的布局层面来看有哪些建议" — that likely means the whole design's big layout (each page's composition), not only overview. Let me structure "大布局" review across the app:

1. 全局框架: header(52px)+nav(212/56)+main(≤1400) — sound; suggestions: (a) 顶栏补 ResearchSnapshot/canonical/tier 身份与"数据截止时间"(快照时间), 目前只有单个 dataset 版本；(b) nav 命名统一; (c) nav 顺序 & 分组 (研究/运营/平台) maybe.
2. 总览: rebalance research vs ops; pipeline rework; add budgets; three cards re-choose (e.g., 证据与门禁 instead of one ops card). Keep no-todos.
3. 因子页: factory summary above library — consider collapsible strip or tab; ensure the 4 factory cards align with the ONE ledger; the section split (h2 因子库) is fine. Maybe move the batch table under a collapsible. Also table is 11 cols wide — at 1400px could be tight with the mini-stepper (224px) + other cols; likely needs min-width/scroll. Check: 11 cols: 30px+ ~150(fid mono 12px ~ 150?)+假设 ~80+生成器70+口径40+RankIC~60+ICIR~50+正率~50+成本~90+mini-flow ~240+版本~100 ≈ 960 + paddings 10×2×11=220 → ~1180. Fits 1400. OK borderline fine.
   Actually 试验: 生命周期进展 column now contains 7 dots ×32 = 224 + label widths (选择期 3 chars at 10px ≈ 30px but width 32 fixed; 上线 2 chars, 选择期 might overflow 32px? .mlb nowrap width can exceed; .mstep width 32 fixed with centered label → 选择期 at 10px ≈ 30px fits barely; 监控 20px fine.
4. 详情: fishbone fix (7 cols, spine length); keep alternating is fine (or single-row stepper with cards?) — the fishbone with 7 stages + info above/below is unusual; is it the right affordance for a linear pipeline with terminal reject? A horizontal stepper with a vertical result panel might be more standard/formal; the fishbone's "交错" adds visual noise for no semantic reason (it's not a fishbone diagram in the Ishikawa sense — no cause branches). Recommend: linear stepper (same rhythm, aligned labels, status chips) OR keep alternation only if it solves space (7 stages × info text is wide). Eh — the alternating exists to fit info text (node info above/below). But a cleaner pattern: horizontal stepper with a single info band under each node (uniform, both below), or a vertical timeline list (stage rows with status/date/evidence) — vertical list is the MOST formal for lifecycle with per-stage details (dates, evidence IDs, failure reasons). Given detail page already has plenty of horizontal charts, a vertical "阶段台账" table could be stronger. I'll suggest as option.
   Also detail page has 6 metric cards — includes 毛交易样本 with power verdict ✓ good. Add breakeven/三档成本 per F007; add cohort ID + promotion verdict once available.
5. 策略运营: fine; alignment: status strip + 6 cards + charts + 2 tables — good density; suggest adding 容量/回测偏差 (PRD 线上结果) and 风控事件 count (CircuitBreaker) — maybe in strip; also 信号陈旧度 semantics shown ✓ good.
6. 设置: split is clear; resolve verify row/FR8.4; add 快照任务 status (since daily task not in matrix, show in logs only — README says so; but ops view then has no snapshot visibility; suggest a "计划任务" mini-row or card in ops tab listing daily jobs & last run — it's a real ops need). Hmm README explicitly decided not in matrix; a separate "计划任务" line keeps that decision while giving visibility. Good suggestion.
7. Cross-cutting defects list (README contradictions, dead link, tokens, motion, fishbone, 11-col, #9ca3af/10px, unused CSS, source chips).

Cap: I'll fold layout suggestions to 5 top items + detail defect list ≤ 7 items. Hmm, "Cap lists at 5 items" — I'll aim 5 per list where possible; tables can be longer but keep tight.

One more check — the README claim "8px 圆角、轻阴影、克制的留白；信息密度优先于视觉表演" ✓ and the pipeline violates via animation. Also the pipeline card padding 6px vs cards 16px — visual inconsistency but intentional tight.

Also potential improvement: pipeline uses blue numbers for ALL stages — no semantic color; maybe encode: bottleneck amber, healthy green — but color semantics per design system limited to 收益/告警. Bottleneck highlight = 告警-ish amber, acceptable per palette (琥珀=告警/降级). Good suggestion aligned with tokens.

Let me also prep the "核心指标" as the user asked "深入分析这个项目的重要节点和关注点和核心指标" — I want this section to be genuinely insightful, not just "add labels". Key insight to lead: **这个项目的第一性对象不是“因子数量”，而是“带预算的证据流”（试验分母、留出预算、隔离窗、样本量）——所以控制台的正式感来自“门禁会计”，而不是动画**。The console should be an "evidence accounting instrument". The mockup is currently a "production line story". Suggest reframing the overview around 3 questions: 产出/证据/运行.

Also I can note the tension: 北极星 (28d trusted PortfolioDefs) is intentionally allowed to be 0 early — so the overview should display it with leading indicators (有效独立数, 漏斗, 周期) rather than fake-positive vibes. The mockup's PnL +6.42% lead could be misread as success; the README says numbers are fake placeholders — fine for density illustration, but the *hierarchy* choices teach what matters. For a review, suggest making the hierarchical choice "research output first".

Hmm, actually wait — I should double-check my claim that the North Star isn't anywhere. Search mockup for "可信" — appears in README (可信样本量) and PARAMS note "需最终确认 + 可信样本量后人工开启"; overview? No. Factory cards? No. So yes missing.

Also missing: 研究到证据周期 (median time) — nowhere.
Missing: 来源多样性 — nowhere. 

OK. Also one subtle thing: the README says "有效独立数等研究指标作为辅助信息收纳" for factory — that was a decision ("收纳为辅助"). My critique can push back: 有效独立数 is a *primary* exploration metric per PRD §2.3 ("名义目标 ≥100/周，不单独作为成功判据") — PRD explicitly says nominal must be reported *alongside* effective independent count. So burying it in a sub-line contradicts "必须与有效独立数、完整漏斗、来源多样性、研究周期和线上偏差一起报告" (README of repo, top). Great grounding: repo README says: "每周 ≥100 个名义候选仍是 AI 因子工厂的产能目标，但必须与有效独立数、完整漏斗、来源多样性、研究周期和线上偏差一起报告，不能单独作为成功判据。" So the console's factory card showing "128 候选 ✓ 已达成" as the big number with 有效独立数 as footnote is exactly the anti-pattern the project warned against ("不能单独作为成功判据"). Excellent — this is a *sharp* review point with authoritative grounding. The 4 factory cards tell: 128 达成 (success vibes) → ... → 有效独立数 23 as footnote. Recommend: pair nominal+effective side by side with 来源多样性 and 研究周期. Strong.

Similarly the overview "昨夜产出 124 候选" leads with nominal. OK.

Now let me write the response in Chinese. Plan the structure:

```
先给结论 (3-4 lines)
一、7 节点流水线：三个硬伤 (with table of 7 nodes, problems, fixes; then proposed redesign options A/B; sketch)
二、大布局层面的建议 (全局 5 条 + 总览/工厂/详情/设置 quick notes; keep ≤5 bullets with sub-points)
三、重要节点 × 关注点 × 核心指标（权威梳理 + 对照表）
   - 关键节点链（权威，压缩成一条链）+ 6 条硬语义（每行: 节点 | 硬规则 | 现在是否可见）
   - 核心指标对照表 (6 行 PRD 指标 → 现状 → 建议)
   - 关注点 5 条（控制台要回答的问题）
四、一致性缺陷清单（可修）— 7 bullets incl README contradictions, dead link, tokens, fishbone bug, motion/a11y, terminology registry, fake data ledger.
五、下一步 (one action)
```

Hmm, that's long but the user asked for deep analysis. Let me make sure the tables are tight. Also "Restate progress each turn" — not needed (single-turn analysis).

One decision: should I check with the user before writing the long analysis? No — they asked for it. Deliver.

Also should I mention the F004 file they had selected? The selected snippet was empty; irrelevant. Skip.

Let me also reconsider: is there something in the repo about a "正式" pipeline that the user might be comparing against? E.g., maybe they saw the mockup screenshots themselves and disliked it. My analysis stands on its own.

Let me now also double-check node #2 "评测 89": STAGES "评测中 89" ✓. Node #3 47 ✓ "选择期 47". Node #4 12 ✓ "组合验证中 12" (card). Node #5 17 = 12+5 per STAGES 留出验证12+最终确认5. Node #6 5 = Champion2+Challenger3. Node #7 18 = STAGES 监控18. So overview derives from STAGES with node5 = sum of two rows and node6 = sum of two rows, node7 = one row. Inconsistent aggregation rule (sum-of-two for 5/6, single for others; and 12 double-appears in node4 and node5). Actually node4's 12 comes from "组合验证中 12" (card) which equals STAGES' 留出验证 12?? The card sub says "留出验证 90 天 · 其中最终确认 5" — so card's "组合验证中 12" encompasses 留出验证. So node4=12 (PortfolioDefs in verification sphere), node5=17=12+5?? That double counts within the overview itself (12 counted at 组合 AND inside 验证 17). Hmm so cleanest statement: **组合 12 与 验证 17 相邻两节点存在重复计数嫌疑（17=12+5，而 12 已在组合节点计过）**。或者 12 与 17 分属不同口径（组合=组合门中，验证=留出+确认中；则 17 里不该含 12）。Either way, incoherent. 

Also "组合 12 组合验证中" vs node label "组合验证中" — combines 组合门 (selection-data) and 验证 (holdout)?? confusing. I'll present.

Let me also quantify the proposal's effort if user opts in — not needed now, maybe in next action mention ~30–60 min for draft revision depending scope. AGENTS.md: give time estimates in concrete units. Next action: "二选一：A) 我直接改稿（先出流水线语义规格 + 重画总览，预计 30–40 分钟）；B) 先只出规格一页纸（~15 分钟）你审后再改。" Actually make the recommended first: "下一步：回复 A 或 B（<2 分钟）。推荐 B（先立语义规格再动稿）。" Hmm, but is B actually better? The design mockup is 非契约设计资产; the highest-value fix is the pipeline semantics + README contradictions. A one-page 语义规格 could be a `docs/design/ui-mockup/PIPELINE-SPEC.md`... but per doc ownership, it'd live with the mockup as part of the design asset. Alternatively, fix in place. I'll recommend B→A sequence and let them pick. Actually simpler: recommend "我先出一个『流水线语义规格 + 节点×指标对照表』草稿（不改稿），你看完点头我再一次性改稿" — that's B. Good.

Wait — one more consideration: The instructions say when user asks evaluation → propose → wait for confirmation. And don't create todos. I'm not creating todos; just analysis + next action. Good.

Also — per the AGENTS.md ADHD style: lead with the answer; use numbered steps; cap lists at 5. I'll be disciplined: use tables and bullets, avoid long prose paragraphs. But depth is required; I'll allow moderate length.

Now — one more sanity check on a few more mockup details I might cite:

- README says "左树 4 项（总览 / 监控 / 因子 / 设置)" — actual nav: 总览/监控/因子/设置 ✓.
- README IA table rows: 因子工厂/因子库/因子详情/因子对比/策略运营/设置. Nav lacks 因子工厂/因子库 as separate items ✓ (they're one page). And "策略运营（落地页）" in IA table vs nav "监控". Contradiction noted.
- 策略运营 page title "策略运营" ✓.
- hash #factors dead ✓.
- Factory card 1 sub "目标 ≥ 100 · 已达成" — the "已达成" is interesting given PRD says nominal alone ≠ success; and with 有效独立 23 as footnote. My point stands.

- Let me verify the pipeline "extra" for node 1: "存量提案 214" — STAGES "提案 214" ✓. So node1 main number 128 is the *weekly flow*, extra is stock. For node 2: main 89 stock, extra 81 weekly flow. Inconsistent ordering (node1 shows flow first, node2 shows stock first). Nice concrete detail for "口径混乱".

- STAGES list has 10 entries with cls: 留出验证 hot, 最终确认 hot, Champion ok, Challenger ok. In the factory bars, colors: amber = hot (verification), green = ok (champion/challenger). Fine.

- The factory distribution card shows 提案214 as a bar at 100% width — includes ALL proposals ever? "提案" as all-time stock. vs pipeline. OK.

Now, about "大布局" — maybe also note **responsive/скролл**: .view max-width 1400; pipeline min-width not scrollable on narrow screens (SVG scales down content). At 1024px width, the pipeline text shrinks (scale <1) — 10-11px text becomes 8px effective. Since user is on desktop probably fine. Skip or one line.

Also: main scroll: body overflow hidden; main overflow-y auto ✓.

OK let me also decide what to name the three "hard defects" of the pipeline:
1. **口径不统一**（存量/流量/求和混排；跨组件无法对账；17 与 12 重复计数嫌疑）
2. **门禁语义缺失**（留出预算、隔离性、部署复核、子门损失、样本量级别 —— 项目最“贵”的规则全部不可见）
3. **演示化过度**（连续粒子动画 + 脉冲光晕，违背稿子自称的“信息密度优先”；且有效独立数被降级为脚注、"达成"字样把名义产能当成功——与仓库 README“不能单独作为成功判据”直接冲突）

Good.

And the "redesign" proposal in the table or as bullet:
- Option A（轻改，保留 7 宏观段）：按"对象分段"标注 FactorDef/PortfolioDef/部署；节点统一为"存量+近7日净变化"；门禁以"站间闸口"形式标注（纯度/成本/查重/组合门/留出/隔离确认/部署复核）并在闸口下挂"本周拒绝数/预算";流量数字移入一条"本周节拍"ticker；动画改事件脉冲。
- Option B（正式化，升格门禁视图，推荐）：9~11 个"站"：方法论/PIT、纯度、成本、查重+多重检验（cohort finalize）、选择期、组合门、90d 留出（预算 x/5）、永久隔离确认、部署复核、挂载/运行、监控。每站：存量、本周进出、拒绝原因分布、预算/状态。
Actually PRD lists: 生成 → 纯度门 → 证据/成本门 → 去重/多重检验 → 选择期 → 组合门 → 留出门 → 最终确认 → 部署前复核 = 9 gates after 生成 = 10 nodes. With 方法论门 before purity (architecture Z). So 10-11 stations. That's the "正式"版本 grounded in §2.3. Provide this as the recommended target.

I think I should present the 10-station mapping to the PRD's funnel line directly — that's the strongest "formal" argument:

PRD §2.3 漏斗链 = 生成 → 纯度门 → 证据/成本门 → 去重/多重检验 → 选择期 → 组合门 → 留出门 → 最终确认 → 部署前复核 (9 stages). Plus architecture adds 方法论/PIT 门 after generation. So the formal pipeline = 生成 → 方法论/PIT → 纯度 → 成本/证据 → 去重/多重检验 → 选择期 → 组合门 → 留出 → 最终确认 → 部署复核 → 监控 (11). The mockup's 7 macro stages compress 纯度/成本/查重 into 评测 and 留出/最终确认 into 验证 and 部署复核 into 上线 — net effect: the three compression points are precisely where the project's credibility rules live. That's my核心论点. 

Alright — also worth confirming: does PRD G1/G3/G5/G7 give concrete "核心指标" numbers the console should show? G5 "最终确认通过至 dry-run ≤1 天"; G3 "≥100 名义/周 + 报告有效独立数、来源分布、各级漏斗"; M4 checklist "周报输出完整指标体系"; §2.3 table. Yes.

Now the response. Also I might briefly note at the top: "我读了三个源：设计稿代码（index/app/styles + README）、权威文档（PRD §2.3/FR3.4/FR3.5、架构 §2.2、F007、ADR-0005），对 7 节点逐站对账。" Establish rigor.

Length target: maybe 120-180 lines of markdown. Let me write carefully in Chinese, precise, no fluff, tables where they compress.

Draft:

---

## 总判断

你的直觉成立，而且问题比"不正式"更具体：**7 节点流水线目前是一段"好看的装饰动画 + 一组对不上账的数字"，它没有承担这个项目最需要的功能——门禁会计**。三处硬伤：

1. 口径混乱：存量/流量混排；`验证 17 = 组合 12 + 最终确认 5` 和旁边"其中最终确认 5"互相矛盾（重复计数 vs 子集，两种读法必有一错）；跨视图（总览/工厂卡/批次表）数字无法对账。
2. 门禁语义丢失：项目最"贵"的三组规则——留出周预算 5、永久隔离确认窗、部署前复核——在流水

## user · 2026-09-14T14:55:35Z

继续

## assistant · 2026-09-14T14:55:35Z


> [reasoning] The user says "继续" (continue). I was in the middle of delivering the analysis. I haven't actually delivered the full response yet — my previous message got cut off mid-draft (the visible message shows I was starting to write the analysis, ending at "门禁会计" paragraph). Now I need to deliver the full deep analysis.

Let me compose the complete, well-structured review in Chinese, per my extensive analysis. Key content:

1. Lead with the conclusion (7-node pipeline issues: accounting errors, missing gate semantics, decorative over-animation)
2. Deep dive on the 7 nodes with a table
3. Big layout suggestions
4. Deep analysis of important nodes / focus points / core metrics (grounded in PRD/architecture/F007/ADR-0005)
5. Consistency defect list
6. One next action

I should be careful to keep it scannable (ADHD style), in Chinese, tables to compress. Let me write it fully now.

Key facts to be precise about:

**The 7 nodes (app.js OVERVIEW_FLOW):**
1. 生成 128（本周产出 / 存量提案 214）
2. 评测 89（评测中 / 本周初筛淘汰 81）
3. 选择期 47（存续 / 180 天窗口 · 查重通过）
4. 组合 12（组合验证中 / 边际贡献评估 + 冻结）
5. 验证 17（留出 + 最终确认 / 每周晋级上限 5）
6. 上线 5（已挂载因子 / PM-007 · PM-009 dry-run）
7. 监控 18（监控中因子 / PnL +6.42% · 衰减 41 · 停用 96）

**Issues per node:**
- Node 1: flow number (128/week) as main, stock (214) as extra; other nodes show stock as main. Also 128 vs batch table (124) vs 4-batch sum (425) unclear. HypothesisDef vs FactorDef not distinguished.
- Node 2: sub-gates (纯度/成本/查重/多重检验) collapsed; per-gate loss invisible — but PRD FR3.8 requires identifying 最大流失级; batch table shows 成本否定 17 but pipeline doesn't.
- Node 3: "查重通过" belongs to evaluation stage not selection; vague "存续".
- Node 4: "组合验证中" wording mixes 组合门 (selection-data) with 验证 (holdout); object switches FactorDef→PortfolioDef here without marking.
- Node 5: 17 = 12+5 while 12 already counted at node 4 (double count) OR factory card "其中最终确认 5" wrong; two windows (90d holdout + permanent isolation) merged; budget 5/wk attached as text.
- Node 6: 5 = Champion 2 + Challenger 3; merges 部署复核 (can fail, SLO ≤1d) + 挂载; same number 5 as final confirmation (confusing).
- Node 7: stock 18 mixed with cumulative 衰减41/停用96; PnL is ops data.

Cross-view ledger: 昨夜产出 124 候选 · 晋级 9 · 淘汰 64 · 成本否定 17 (64+17=81, if 64 includes 17 double count; batch table 9+51+64=124 if includes); 本周产出 128 vs 124; STAGES 10 rows.

**README contradictions:**
- "首屏命名工作台" vs "落地页=总览" vs "移除工作台/总览，落地页=策略运营" vs IA table "策略运营（落地页）" — four statements, built mockup = 总览 landing.
- Service matrix: "只列长驻服务（freqtrade/kronos/data-collector/timescaledb/grafana）" vs bullet "服务矩阵（…快照手动触发、门禁立即运行）" — and mockup includes verify 门禁 row with "立即运行" (contradicts FR8.4 spirit + its own FR8 落点 "只读呈现").
- #factors deep link dead (view id = view-factory).
- "深色偏好：token 全部集中 :root" — false; app.js hardcodes hex everywhere.
- Purple #7c3aed not in declared palette (single accent blue + green/red/amber).

**Code defects:**
- Fishbone: `grid-template-columns: repeat(11, ...)` but only 7 stages → 4 empty columns + spine (::before) extends past last node ~480px.
- .lane-dash animation not disabled under prefers-reduced-motion (JS particles do stop).
- Animation runs even when overview hidden (rAF keeps going).
- 10px #9ca3af extra text (low contrast ~2.5:1).
- Dead CSS: .flow/.fstep (legacy), .pipe, .todo, .nav-group.
- Inline styles sprinkled.
- 监控 18 stock vs champion/challenger relationship undefined.
- Verdict vocabulary: filter uses promising/weak/dead/decayed where decayed is lifecycle not verdict; missing underpowered/incomplete (F007 enum promising|weak|dead|underpowered|incomplete); "结论" named but per architecture verdict is diagnostic label, promotion is cohort-level.

**Authoritative nodes/metrics (PRD §2.3, FR3.4/3.5, FR5.2, FR6.2, FR7.5, arch §2.2, F007):**

Funnel: 生成 → 方法论/PIT 门 → 纯度门 → 证据/成本门 → 去重/多重检验 → 选择期 → 组合门（冻结 PortfolioDef）→ 90d 留出门（样本量三级 + 周上限 5 + append-only 台账）→ 永久隔离最终确认 → 部署前复核（SLO ≤1d）→ 挂载 → 监控（生命周期动作）
All rejections → 证据库 X → 复盘 → 入队（generation+1, 计入预算）

Hard semantics summary:
- cost_negative ⇒ dead regardless of IC
- 拒绝者进入试验分母 (BH-FDR etc.)
- cohort 未 FINALIZED 不能晋级; promotion_verdict only
- weekly cap 5, append-only ledger
- 永久隔离: cannot re-read
- 部署前复核 ≠ final confirmation; champion replacement retriggers; ≤1d to dry-run
- preview/canonical isolation; research views canonical only
- sample size: <30 UNDERPOWERED / 30–69 temp PASS (reduced paper only) / ≥69 trusted

Core metrics map (PRD §2.3):
| 层级 | 指标 | 稿中现状 |
- 北极星 可信 Alpha 28d → absent
- 转化效率 (研究→证据 median; 证据→部署 ≤1d) → absent
- 探索能力 (名义≥100 + 有效独立 + 来源多样性) → nominal shown as "已达成", effective as footnote 23, diversity absent — conflicts with repo README "不能单独作为成功判据"
- 漏斗健康 (分级转化率 + 最大流失级 + 五阶段损失) → stocks only, no loss attribution
- 线上结果 → strategy page partial (容量/回测偏差 absent)
- 信任护栏 (快照/manifest/留出台账/复现率 100%, 前视 0) → top bar single data_version; manifest in detail; no ledger/integrity status

Console's 5 attention questions: 今天运营 / 本周产能与漏斗 / 每 cohort 证据 / 北极星与停止时钟 / 审计追溯

**Layout recommendations:**
1. 总览重平衡：研究产出 band on top (北极星 + 有效独立 + 周期), pipeline middle (gates + budgets + loss), ops cards bottom (or 2 ops + 1 evidence card).
2. Pipeline rework: Option A (轻改: keep 7 stages, fix units/objects, gate annotations, event pulses) vs Option B (推荐: promote gates — 10 stations per PRD funnel). Include sketch.
3. Identity & source chips: top bar add snapshot id / canonical tier; cards annotate 真相源 (manifest/TSDB/freqtrade).
4. Vocabulary registry: one table mapping 阶段/verdict/lifecycle; use consistently; fix 结论 column naming; add underpowered/incomplete.
5. Detail page: fishbone fix or replace with vertical stage ledger (more formal); add breakeven/three-tier cost per F007; cohort status.

Defect list (可立即修):
1. README 自相矛盾 4 处 + #factors 死链
2. fishbone 11 列/轴线溢出
3. 数字对账（fake data 单一台账 + 恒等式）
4. token 化 & reduced-motion & 隐藏页暂停动画
5. verify 门禁行 vs FR8.4 裁决
6. 命名统一 (监控→策略运营? nav vs title)
7. dead CSS

Next action: choose A or B... Actually offer concrete next step: 我建议先出「流水线语义规格」一页纸 + 重画方案（不动稿），你点头后一次性改稿。回复「B」或「改稿」即可。Give time estimate: 规格 15 分钟，改稿 40 分钟.

Since the user said "继续", they want the rest of the analysis. Let me deliver the complete thing now. I'll keep the structure tight. I'll write it as the full response now, continuing from where I "left off" but re-presenting coherently — actually the previous partial message showed the beginning (总判断 + 三处硬伤). Since the user saw it, I should continue from there rather than repeat. But safer: continue the content — start with "二、7 节点逐站体检" perhaps. Hmm, but the previous message ended mid-sentence in "门禁会计" paragraph? Looking at my previous turn: it ended with "三处硬伤： 1. 口径混乱：... 2. 门禁语义丢失：项目最"贵"的三组规则——留出周预算 5、永久隔离确认窗、部署前复核——在流水" — cut off. I should continue smoothly: restate briefly the three 硬伤 completed, then go into sections. Or cleanly: "接着上面——" and deliver sections 2-6. Let me just deliver the full analysis compactly, maybe slightly restating the conclusion lines (3 bullets) to make the message self-contained, then sections. The user has ADHD profile — a self-contained complete answer is better than "continuing" awkwardly. But don't over-repeat. I'll do: short completion of the 总判断 (3 硬伤 as bullets), then 二/三/四/五 sections.

Let me write it well. Also keep tables ≤ manageable width. Use Chinese. No emojis (per instructions, avoid unless requested).

One important check: I must not offer to implement yet — analysis + proposal + wait for confirmation. The next action offer is fine.

Also time estimates in concrete units.

Let me finalize the exact content of each section.

Section 二、7 节点逐站体检 (table 7 rows):

| # | 节点（稿中数字） | 问题 | 建议语义（保留 7 段时） |
1. 生成 128/214: 主数字是"本周流量"，副文本才是"存量"；其他站相反。HypothesisDef 与 FactorDef 不分。→ 统一为"存量+近7日净增"；明确对象。
2. 评测 89/淘汰81: 纯度/成本/查重/多重检验四种死法合并成一个数；PRD 要求"周报指认最大流失级"、F007 要求五阶段损失——这里什么都看不出来。→ 站内挂"拒绝拆分"（纯度x/成本y/查重z/方法论w），至少成本否定要显式。
3. 选择期 47: "查重通过"是评测的动作，放错了站；"存续"没信息量。→ 改为"选择期通过 + 窗口 + 稳定性"。
4. 组合 12: 名"组合验证中"把组合门（选择期数据上的边际贡献裁决）和验证窗混为一谈；对象在此从 FactorDef 变 PortfolioDef 但无标注。→ 改"组合门/冻结中"，标注对象切换。
5. 验证 17: 17=12+5，而 12 已在上一站计过（重复计数嫌疑）；或工厂卡"其中最终确认 5"的"其中"是错的。90 天留出与永久隔离确认是两种不同窗口（预算/隔离规则完全不同）被并成一个。→ 拆两站：留出（本周 x/5 预算、追加只写台账）/ 最终确认（隔离、只读）。
6. 上线 5: 5=2 Champion+3 Challenger，与"最终确认 5"同数易读成同一批；部署前复核是可失败、有 ≤1 天 SLO 的独立门，被藏进"上线"。→ 拆"部署复核 / 挂载运行"；显示复核队列与失败出口。
7. 监控 18: 存量 18 与累计 41/96 混排；PnL 属运营口径，不应挂在研究流水线上。→ 只留监控存量与状态迁移计数（降权/暂停/下线），PnL 移入运营卡。

Then 两个改造选项:
- A 轻改（保留 7 段）: 每站=存量+7日净变+门禁注记; 流量条单独; 数字全来自同一台账; 动画→事件脉冲.
- B 升格门禁视图（推荐，正式感来自会计）: 按 PRD §2.3 漏斗 + 架构 §2.2 串 10-11 站: 生成→方法论/PIT→纯度→成本/证据→去重+多重检验(cohort)→选择期→组合门→90d留出(3/5)→永久确认(隔离)→部署复核(≤1d)→挂载→监控; 每站: 存量/本周进出/拒绝原因分布/预算与状态. 附 ASCII 示意.

Section 三、大布局建议 (5 items):
1. 总览三段带（产出/管线/运行）; 北极星上首屏，即使为 0（PRD 允许长期为零，0 要带着领先指标出现）。
2. 全站身份与来源标注: 顶栏补 ResearchSnapshot + canonical 徽标 + 快照时间; 每卡标真相源；研究/运营同屏时明确分面对比规则（否则违反 ADR-0005 的"哪个数字是真的"原则）。
3. 因子页: 工厂摘要与因子库同页合理，但建议把工厂块做成可折叠、默认收起的一行摘要（每周高频使用的是库）；4 卡改为"名义/有效独立/来源多样性/周期"并排，删除"已达成"的字样（仓库 README: 不能单独作为成功判据）。
4. 详情页: 鱼骨图 → 竖排"阶段台账"（更正式、可承载日期/证据号/失败原因）；保留横向 stepper 作为轻量视图会被数字+预算压扁；成本分解补 breakeven 与三档（F007 FR-005），显示 cohort 状态。
5. 设置/运维: 服务矩阵去掉 verify 行或明确裁决边界（FR8.4）；加"计划任务"一线（快照 02:00 等）补上矩阵不列计划任务的缺口；参数表 OK。

Section 四、重要节点/关注点/核心指标（深度）:

4.1 关键节点链（权威）:
生成 → 方法论/PIT+纯度 → 成本裁决 → 去重/多重检验（cohort finalize）→ 选择期 → 组合门/冻结 → 留出（90d，预算 5/wk，样本量三级）→ 永久隔离确认 → 部署前复核（≤1d）→ 挂载/运行 → 监控/生命周期 → 证据库复盘入队
六条硬语义每条附出处（表格），例如:
- cost_negative ⇒ dead（不管 IC 多高）| arch §4.2 / F007 FR-005 | 稿中：列表成本徽标有，管线无
- 拒绝者入分母 | FR3.3 / F007 FR-004 | 稿中：无 cohort 概念
- cohort OPEN→FINALIZED 才可晋级，promotion_verdict ≠ verdict | arch §4.2 / F007 | 稿中：无
- 留出周上限 5 + append-only 台账 | FR3.4 | 稿中：文字有、无预算状态
- 永久隔离窗不可回读 | FR3.4 | 稿中：并进"验证"
- 样本量三级 <30/30–69/≥69 | FR3.5 | 稿中：仅在详情卡一角
- 部署复核 ≠ 最终确认；champion 轮换重触发；≤1d | FR5.2 / G5 | 稿中：藏进"上线"
- preview/canonical 隔离，研究视图只读 canonical | ADR-0006 / FR8.1 / F007 FR-001 | 稿中：无
→ 建议这 8 条作为"门禁注释"显示在工作流/管线（可 hover）。

4.2 核心指标对照表 (6 rows):
北极星 / 转化效率 / 探索能力 / 漏斗健康 / 线上结果 / 信任护栏 — 现状 & 建议。

4.3 控制台应回答的 5 个问题（关注点）:
今天运行健康？/ 本周探索产出（名义×有效×来源）？/ 证据预算用在哪（留出队列、预算、样本量级别）？/ 北极星与停止时钟（28d 可信 Alpha、G7 检查点）？/ 每个数字能否追溯（manifest/台账）？
每问给 1 行"现在哪看/缺什么"。

Section 五、可直接修的缺陷清单 (7 items w/ file:line):
1. README 矛盾（落地页 3 种说法；服务矩阵两种说法）— README.md L45/71/79-85
2. #factors 死链 — README.md L11 vs index.html L42 (view-factory)
3. 鱼骨图 11 列 7 站 + 轴线溢出 — styles.css L337-343
4. JS 硬编码色板（暗色主题 claim 不成立; 紫不在调色板）— app.js 多处
5. lane-dash 无 reduced-motion; 隐藏页仍跑动画 — styles.css L418, app.js L706-769
6. 10px #9ca3af 承载语义文本（管线 extra / mini-flow 标签）— app.js L641, styles.css L386
7. dead CSS / 命名不一致（nav 监控 vs 页 策略运营；结论 filter 含 decayed 且缺 underpowered/incomplete）

Section 六、下一步:
选择 A/B（B 推荐）：我可以先产出"流水线语义规格一页纸"（节点/对象/单位/预算/拒绝拆分/数据字段映射 + 总览重排草图），预计 15 分钟；你确认后一次性改稿，预计 40 分钟。回复 A 或 B 即可。

Wait — the user's AGENTS.md says "End with one next action doable in under two minutes." The next action = "回复 A 或 B" — doable in seconds. Good.

Also: should I mention that I couldn't visually verify (no image support) and did source-based review? Maybe one line at the end or top. It's relevant: user said don't delegate, read HTML directly. I did. Fine — maybe not needed; I already read the code. Keep one short note that conclusions are from source+authoritative docs. Skip to save space. Actually the user explicitly said "你直接读取html页面即可" — so they know. No need.

Cap lists at 5: my tables exceed 5 rows in places (7-node table is inherently 7; that's the requested item). The defect list — I'll compress to 5-7 items in a table. The instructions say cap lists at 5; tables of data are acceptable when they're the content. I'll try to keep bullets ≤5 per group, and merge minor items.

Let me now also double-check a couple of line references for accuracy so I can cite file:line correctly:
- OVERVIEW_FLOW: app.js L602-610 ✓
- FALL_FROM: app.js L701: `var FALL_FROM = [1, 2, 3, 4, 6];` ✓
- fishbone grid: styles.css L337: `grid-template-columns: repeat(11, minmax(88px, 1fr));` ✓ L340-344 ::before ✓
- README landing contradictions: README.md L45 ("首屏命名「工作台」"), L71-72 ("左树 4 项（总览 / 监控 / 因子 / 设置）... 落地页 = 总览"), L79 ("移除「工作台/总览」页，落地页 = 策略运营") and L32-33 ("一级视图共 4 个：策略运营（落地页）/ 因子工厂 / 因子库 / 设置") ✓
- README hash: L11 "#factors" vs index.html L42 id="view-factory" ✓
- README dark-mode claim: L110 "深色偏好若回归：设计 token 全部集中在 styles.css :root" vs app.js hardcodes ✓
- SERVICES verify: app.js L148-149 ✓ with ops ["立即运行"] ✓; README L83-84 "服务矩阵只列长驻服务（freqtrade / kronos-signal / data-collector / timescaledb / grafana）" ✓ vs L62-64 "（…快照手动触发、门禁立即运行）" ✓
- lane-dash: styles.css L417-419 ✓; reduced-motion only in app.js L706-707 ✓
- .mlb 10px: styles.css L386 ✓; pipeline extra 10px: app.js L641 `font-size="10"` ✓ (label 11 at L640, extra 10 at L641)
- .flow/.fstep dead: styles.css L266-292; .pipe L237-241; .todo L302-314 — check usage: .pipe never used in index.html ✓ (class "pipe" not present); .todo not present; .fstep not used (fishbone uses fsh-*). Actually `.fs-` classes L279-292 also unused. And `.nav-group` L91 unused. OK.

- Node table numbers: OVERVIEW_FLOW entries ✓.

For the batch data: B-20260912: n:124 prom:9 weak:51 dead:64 cn:17 (app.js L117). 9+51+64=124 → dead includes cn 17. Overview 昨夜产出: "124 候选 · B-20260912 · 晋级 9 · 淘汰 64 · 成本否定 17" (index.html L179). So "淘汰 64" already includes 成本否定 17 → listing both as parallel sub-stats is double counting (9+64+17=90; but if dead incl cn, then 9+64=73+weak51=124). The sub probably means: 晋级9、淘汰64（其中成本否定17）— but it's written as parallel ·. Flag: 建议写成 "淘汰 64（含成本否定 17）"。 Good concrete.
- 本周产出 128 vs B-20260912 124: factory card L46 "128 候选", sub "目标 ≥ 100 · 已达成". Overview node 1 num 128 "本周产出". Batch table latest 124. So 128 ≠ 124 — "本周"可能含不止一批（可见4批: 124+117+96+88=425）。So if 128 is 本周 and visible batches sum 425, mismatch. I'll mention "批次表四批合计 425，与'本周产出 128'无法对账（除非'本周'只指最后两天）——没说明口径". Be precise but not overclaim; phrase as "无法从界面读出对账关系".

- STAGES: 提案214, 评测中89, 选择期47, 留出验证12, 最终确认5, Champion2, Challenger3, 监控18, 衰减41, 停用96 (app.js L123-134).
- 有效独立数 23 in factory card 4 sub (index.html L49). Overview? No. OK.

One more check: the overview node 5 extra "每周晋级上限 5" — PARAMS has "每周留出晋级上限 5" (app.js L159) note "超出的候选顺延下一周" ✓ consistent. Good.

Now write the final response in Chinese. Make it well-organized, information-dense but scannable. Use headers ##/###. Avoid emojis. Keep tone direct.

Length: substantial but bounded. Let me write.

Actually one more thing to verify — the claim "研究视图只渲染版本态产物；实时运营数据不进入研究视图" and the overview mixing. README FR8.1 落点 says 研究视图（漏斗/因子库/详情/对比/谱系）— 总览 not listed. So overview is a special mixed page. I'll phrase: 总览是唯一"研究×运营混面"页面，需要有明确规则（哪些数字属 canonical 研究面、哪些属实时运营面），否则与 ADR-0005 的"哪个数字是真的"原则冲突。建议每卡带来源徽标。Good.

Also ADD: the top bar "数据版本 v2026.09.12" singular but multi-dataset: FR1.7/ADR-0007 ResearchSnapshot binds multiple dataset versions. Suggest top bar shows snapshot_id (short) + 快照截止时间, hover shows members (ohlcv/funding/kronos信号). And canonical/预览 tier badge. Good.

Also I could mention the "成本模型 cm-v1" ✓ good already.

OK writing now. I'll also add at the very end the A/B choice. And under 6. 下一步 give estimate numbers.

Wait, also one of my strongest overall points: "正式感来自门禁会计 (budget/accounting/invariants), 而不是动画" — lead with that. And the repo README itself says nominal must not be sole success measure — quote it. Let me include exactly: README: "每周 ≥100 个名义候选仍是 AI 因子工厂的产能目标，但必须与有效独立数、完整漏斗、来源多样性、研究周期和线上偏差一起报告，不能单独作为成功判据。" And factory card 1 says "128 候选 · 目标 ≥ 100 · 已达成" — direct conflict in presentation. Strong.

Let me write the final answer now. Keep tables compact. Chinese. No emoji. Maybe use ✅/✗? No — avoid emojis; use 有/缺. The README/mockup use ✓✕ symbols; fine to use in quotes but avoid decorative emoji. I'll use plain text.

Draft final: (will compose in the reply)
继续。以下是完整审视结论。

---

# 一、总判断：问题不是"不够好看"，是"没有会计"

你的直觉成立，而且可以说得更具体：**7 节点流水线目前是一段装饰性动画 + 一组互相对不上账的数字，没有承担这个项目最需要的功能——门禁会计（evidence accounting）**。三处硬伤：

1. **口径混乱**：存量与流量混排；`验证 17 = 组合 12 + 最终确认 5`，而 12 已在上一站计过（重复计数），且工厂卡写"12 中**其中**最终确认 5"（子集读法）——两种读法必有一错；总览/工厂卡/批次表三个组件数字无法互推。
2. **门禁语义丢失**：项目最"贵"的规则——留出周预算 5、永久隔离确认窗、部署前复核（≤1 天 SLO）——全部压缩进了"验证/上线"两个节点里，看不见预算、看不见隔离、看不见可失败点。而 PRD §2.3 的漏斗链、F007 的五阶段损失，恰恰要求这些可见。
3. **演示化过度 + 与自家原则冲突**：连续粒子流动 + 落站脉冲光晕，违背该稿 README 自称的"信息密度优先于视觉表演"；更尖锐的是工厂首卡把"128 候选 · 已达成"当成功展示——而仓库 README 明说名义候选数"不能单独作为成功判据，必须与有效独立数、来源多样性、完整漏斗并列报告"，有效独立数（23）却被收进脚注小字。

---

# 二、7 节点逐站体检（app.js `OVERVIEW_FLOW` L602-610）

| # | 节点（现数字） | 具体问题 | 建议语义（若保留 7 段） |
|---|---|---|---|
| 1 | 生成 128 / 存量提案 214 | 主数字是"本周流量"，副文本才是存量；其余站相反（主=存量）。HypothesisDef 与 FactorDef 不分。128 与批次表（124，四批合计 425）对不上且无口径说明 | 统一"存量 + 近 7 日净增"；流量单独做一条"本周节拍" |
| 2 | 评测 89 / 初筛淘汰 81 | 纯度/成本/查重/多重检验四种死法合并成一个数。PRD FR3.8 要求"指认最大流失级"、F007 要求五阶段损失——此处什么都看不出 | 站内挂拒绝拆分：纯度 x / 成本 y / 查重 z / 方法论 w（成本否定必须显式） |
| 3 | 选择期 47 / "查重通过" | "查重"是评测站的动作，放错了站；"存续"无信息量 | 改为"选择期通过 + 窗口 + 稳定性" |
| 4 | 组合 12 / 组合验证中 | "验证"混入：组合门是在选择期数据上做边际贡献裁决，不是验证窗。且对象在此从 FactorDef 切换为 PortfolioDef，无任何标注 | 改"组合门 / 冻结中"，标注对象切换点 |
| 5 | 验证 17 / 每周上限 5 | 17=12+5 重复计数（见上）；90 天留出（有周预算、写台账）与永久隔离确认（不可回读）是两种窗口，规则完全不同，被并成一个 | **拆两站**：留出（本周 3/5 预算、顺延 n）/ 最终确认（隔离、只读锁） |
| 6 | 上线 5 / 已挂载因子 | 5 = Champion 2 + Challenger 3，又与"最终确认 5"同数，极易读成同一批；部署前复核是独立可失败门（可回证据库、≤1 天 SLO），被藏进"上线" | **拆两站**：部署复核（队列 + 失败出口）/ 挂载运行 |
| 7 | 监控 18 / 衰减 41 · 停用 96 | 存量 18 与累计 41/96 混排；PnL 属运营口径，不应挂研究流水线 | 只留监控存量 + 状态迁移计数（降权/暂停/下线）；PnL 移入运营卡 |

**改造两选项：**

- **A. 轻改（保 7 段）**：每站 = 存量 + 7 日净变 + 门禁注记；流量数字移入一条"本周节拍"ticker；动画改为**事件脉冲**（数据变化时亮一下，不常动）。
- **B. 升格为门禁视图（推荐，正式感来自会计）**：按 PRD §2.3 漏斗 + 架构 §2.2 串成 10~11 站，每站四要素（存量 / 本周进出 / 拒绝原因分布 / 预算或状态）：

```text
生成 → 方法论/PIT → 纯度 → 成本/证据 → 去重+多重检验(cohort) → 选择期
     → 组合门 → 90d留出(3/5) → 永久确认(隔离) → 部署复核(≤1d) → 挂载 → 监控
```

---

# 三、大布局层面的 5 条建议

1. **总览重排三段带**：上=产出（北极星 28d 可信 Alpha、有效独立数、研究→证据周期中位）；中=流水线（含预算与损失拆分）；下=运行（策略执行/信号与数据/昨夜产出）。北极星即使为 0 也放首屏——PRD 明确允许它长期为零，0 要配领先指标出现，而不是用 PnL +6.42% 顶在最上面。
2. **全站"来源与层级"标注**：这是稿子最大的治理缺口。顶栏现在只有一个 dataset 版本，应补 **ResearchSnapshot 短 ID + canonical 徽标 + 快照截止时间**（FR1.7/ADR-0007：多数据集绑定身份）；每张卡片标真相源（manifest / TSDB / freqtrade）。总览是全稿唯一"研究×运营混面"页面，必须给混面数字定规则，否则与 ADR-0005"哪个数字是真的不可接受"直接冲突。
3. **因子页**：工厂摘要与因子库同页动线合理，但建议工厂块可折叠、默认一行摘要（高频使用的是库）；4 卡改为"名义 / 有效独立 / 来源多样性 / 研究周期"并列，删掉"已达成"。
4. **详情页**：鱼骨图建议换成**竖排阶段台账**（每行：阶段 / 状态 / 日期 / 拒绝原因 / 证据号）——这才是"正式"的生命周期表达；横向交错只解决了排版问题，没有语义。成本分解补 breakeven + 零成本/maker/taker 三档（F007 FR-005 的输出，F005 只准渲染不准重算），并显示所属 cohort 与其状态（OPEN/FINALIZED）。
5. **设置页**：服务矩阵里的"verify 门禁 · 立即运行"要在 F006 里显式裁决——要么去按钮（FR8.4 只读裁决结果），要么定义为受审计操作；另加一行"计划任务"（快照 02:00 等）补上"矩阵不列计划任务"的可见性缺口。

---

# 四、重要节点 × 关注点 × 核心指标（深入）

## 4.1 项目真正的关键节点与硬规则（权威梳理）

生成 → 方法论/PIT+纯度 → 成本裁决 → 去重/多重检验（cohort finalize）→ 选择期 → 组合门/冻结 → 90d 留出 → 永久隔离确认 → 部署前复核 → 挂载 → 监控 → 证据库复盘入队。

八条"昂贵"语义（建议做成工作流/管线的 hover 注释）：

| 硬规则 | 出处 | 稿中现状 |
|---|---|---|
| cost_negative ⇒ 一律 dead，不论 IC 多高 | 架构 §4.2 / F007 FR-005 | 列表有成本徽标，管线无 |
| 被拒绝者仍进试验分母（BH-FDR） | FR3.3 / F007 FR-004 | 无 cohort 概念 |
| cohort 未 FINALIZED 不可晋级；晋级看 promotion_verdict，成员 verdict 只是诊断标签 | 架构 §4.2 / F007 | 无（列表筛选项叫"结论"，用词过强） |
| 留出周上限 5 + append-only 台账 | FR3.4 | 只有一行小字，无预算状态 |
| 永久隔离确认窗不可回读 | FR3.4 | 并进"验证" |
| 样本量三级：<30 / 30~69 临时 / ≥69 可信 | FR3.5 | 仅详情页一角 |
| 部署复核 ≠ 最终确认；champion 轮换重触发；≤1 天到 dry-run | FR5.2 / G5 | 藏进"上线" |
| preview/canonical 隔离，研究视图只读 canonical | ADR-0006 / FR8.1 | 全站无呈现 |

## 4.2 核心指标对照（PRD §2.3 六个层级）

| 层级 | 指标 | 稿中现状 | 建议落点 |
|---|---|---|---|
| 北极星 | 滚动 28d 新增可信 PortfolioDef | **缺** | 总览首屏 |
| 转化效率 | 研究→证据中位时长；证据→部署 ≤1d | **缺** | 总览 + 工厂 |
| 探索能力 | 名义 ≥100/周 + 有效独立数 + 来源多样性 | 名义=128"已达成"；独立数=脚注；多样性缺 | 工厂 4 卡重排为并列 |
| 漏斗健康 | 分级转化率 + 最大流失级 + 五阶段损失 | 只有存量，无流失结构 | 管线站内拆分 + synthesis 渲染 |
| 线上结果 | 成本后收益/回撤/容量/偏差/衰减 | 策略页部分（缺容量、回测偏差） | 策略页补 |
| 信任护栏 | 快照/manifest/留出台账/复现率 100%、前视 0 | 顶栏版本 + 详情 manifest（部分） | 顶栏身份块 + 完整性状态 |

## 4.3 控制台应回答的 5 个问题

1. **今天运行健康吗**——引擎/信号/数据/风控（现在有，策略页做得好）。
2. **本周探索产出值不值**——名义×有效×来源×周期（现在最弱）。
3. **证据预算花在哪**——留出队列/预算/样本量级别/UNDERPOWERED 占比（现在缺）。
4. **离北极星和停止时钟多远**——28d 可信 Alpha、G7 检查点（10 周或 100 个有效独立候选）（现在缺）。
5. **这个数字能追溯吗**——manifest/台账/审计（详情页已有雏形，全局缺）。

---

# 五、可直接修的一致性缺陷清单

| # | 缺陷 | 位置 |
|---|---|---|
| 1 | README 自相矛盾：落地页三种说法（工作台 / 总览 / 策略运营）；服务矩阵两种说法（列 verify + 快照触发 vs 只列长驻服务） | README L45 / L71 / L79 / L32；L62-64 vs L83-84 |
| 2 | `#factors` 深链是死链（实际 id 是 `view-factory`） | README L11 vs index.html L42 |
| 3 | 鱼骨图 11 列只放 7 站，轴线（`::before`）延伸过最后一站约 480px 空白 | styles.css L337-344 |
| 4 | "token 全在 :root，可派生暗色"不成立——图表/管线颜色全部硬编码在 JS；且紫色 #7c3aed 不在声明的调色板（蓝 + 绿红 + 琥珀）里 | app.js 多处 |
| 5 | `.lane-dash` 无 reduced-motion 保护；切走视图后粒子动画仍在跑（耗电） | styles.css L418；app.js L706-769 |
| 6 | 10px `#9ca3af` 承载语义文本（管线副行、迷你流程标签），对比度不足 3:1 | app.js L641；styles.css L386 |
| 7 | 术语四套混用（阶段/verdict/生命周期/结论）；"结论"筛选项含 decayed（那是生命周期态），缺 underpowered/incomplete；nav"监控"≠页题"策略运营" | README + app.js |

---

# 六、下一步（二选一，回复即可）

- **B（推荐）**：我先产出「流水线语义规格」一页纸——节点/对象/单位/预算/拒绝拆分/数据字段映射 + 总览重排草图。不碰设计稿，约 15 分钟。
- **A**：跳过规格，直接按上述结论改稿（流水线重构 + 数字对账 + README 矛盾与死链清理）。约 40 分钟。

回复 **A** 或 **B** 即开工。
