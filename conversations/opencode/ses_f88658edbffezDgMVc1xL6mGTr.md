---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f88658edbffezDgMVc1xL6mGTr"
title: "Fix D001/D005/D006/D008/D012 via ADRs (@general subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T16:43:25Z"
updated_at: "2026-09-06T16:50:27Z"
tokens_input: 86769
tokens_output: 4093
cost: 0.0
parent_id: "ses_f886c33ddffed2Ehk0OBMbTqR2"
---

# Fix D001/D005/D006/D008/D012 via ADRs (@general subagent)

## user · 2026-09-06T16:43:25Z

You are the FIXER in a review-convergence loop for AlphaMill (D:\Projects\alphamill), a crypto quant research system at design stage. Baseline: main @ 1bd8c4d, working tree has only untracked review reports. Language: ALL doc content in Chinese (match existing doc style: frontmatter with topics/doc_kind/created/updated, tables, concise engineering prose).

YOUR FILE OWNERSHIP (do NOT touch any other file):
- docs/decisions/0004-portfolio-construction.md (NEW FILE)
- docs/decisions/0003-validation-gate-non-degradation.md (AMEND)
- docs/decisions/0001-factor-mining-engine.md (AMEND)
- docs/decisions/README.md or index file if one exists (update ADR list only if such file exists)

First READ all three existing ADRs + docs/alphamill-prd.md sections on G1-G5/FR2/FR3/milestones to anchor context. Read the round-1 review report at docs/reviews/CURRENT-doc.md issues D001, D005, D006, D008, D012 for exact findings.

MANDATORY CONTEXT — positive confirmations you must NOT break: ADR-0003's frozen gate criteria must NOT be loosened in any way (your amendments only ADD protections); storage trio division; no-lookahead three layers; PRD non-goals list.

TASKS:

1. CREATE docs/decisions/0004-portfolio-construction.md (fixes D001, Critical): The AlphaGen synergy-pool output (linear factor combos) currently has NO deployment path — deployment model is single-factor single-strategy + Top1-only dry-run. Write ADR-0004 deciding:
   - Synergy pool combos ARE deployable as meta-factors (one combo = one strategy candidate going through the same validation gate, no shortcut).
   - Factor→strategy mapping: Top-K portfolio (v0.1: K small, e.g. 3-5) replaces Top1-only; weight scheme v0.1 = inverse-volatility or equal-risk (state one, keep simple, defer optimization).
   - Turnover budget: explicit cap per rebalance period (state a v0.1 default and that it's a gate input to the cost model).
   - Net exposure cap + same-pair conflict rule: v0.1 = one strategy per pair; conflicting signals on same pair are netted at portfolio-construction layer before hitting Freqtrade (state this explicitly, defer advanced netting).
   - Consequences/alternatives section per ADR house style (match 0001/0003 structure exactly: 背景/决策/备选/后果 or whatever the existing ADRs use).
   - Status: accepted. Date 2026-09-07.

2. AMEND docs/decisions/0003-validation-gate-non-degradation.md (fixes D005, D006, D008 — all High). Add new sections (do not alter existing frozen criteria wording):
   - D005 Holdout budget: holdout window is an exhaustible statistical resource. Add: weekly access budget (top-k candidates per week pass to holdout, state k as a config with v0.1 default), a holdout usage ledger (append-only, one row per holdout evaluation: candidate id, date, result), and a permanently isolated final-confirmation window (data segment that NO candidate evaluated during development may touch, used only once before paper promotion).
   - D006 Threshold power argument: PRD §1.2 itself diagnosed that a 69-trade FAIL/PASS judgment is statistically unreliable, yet the gate says ≥30 trades. Resolve the contradiction WITHOUT loosening: declare ≥30 as the absolute hard floor below which a candidate cannot even be evaluated; explicitly state that 30-69 trades = UNDERPOWERED band — a PASS there is provisional (paper-trial only with reduced size + extended observation), and reliable judgment needs ≈69+ trades (reference the PRD's own diagnosis; add a short power-rationale sentence: at α=0.05/80% power the minimum detectable effect implies sample sizes in that range). The gate becomes stricter in effect, never looser.
   - D008 Review-loop peeking guard: the FR4.3 review agent loop (agent reads results → proposes hypothesis → retest on same history) is a data-snooping amplifier. Add: every hypothesis produced by the review loop carries a generation tag and enters the trials ledger (same ledger as D005); the final-confirmation window (from D005) is never exposed to the review loop; review-loop hypotheses count toward the multiple-testing budget (PRD FR2.4).
   - Update the ADR's frontmatter `updated:` to 2026-09-07 if it has frontmatter.

3. AMEND docs/decisions/0001-factor-mining-engine.md (fixes D012, Medium): the M2 time-boxed smoke gate is right but the L1/L2 downgrade switch criteria are not pre-written — a solo dev will self-exempt. Add a checkable downgrade-criteria list: e.g. switch to L1 (simplified engine) if smoke gate exceeds its time-box by X or vendor deps fail Y; switch to L2 (non-RL generator) if L1 misses weekly candidate quota for N consecutive weeks. Make each criterion concrete and binary (measurable), matching the existing L1/L2 ladder already defined in the ADR.

VALIDATION: After writing, run `python tools/validate_spec_lifecycle.py` (cwd D:\Projects\alphamill) — it must stay green. If your new ADR trips any validator check (e.g. a hardcoded ADR list), adapt the doc to comply and report it.

MUST NOT: touch PRD/architecture/SOP/README (other agents own them); loosen any frozen gate; invent new dependencies or tools; write in English; commit anything.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T16:43:25Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0001-factor-mining-engine.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0003-validation-gate-non-degradation.md"})`
- **tool**: `glob({"pattern": "docs/decisions/*"})`


> [reasoning] Let me start by reading the required context files: the three existing ADRs, the PRD sections, and the review report.

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0001-factor-mining-engine.md</path>
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
10: PRD G1 要求因子假设吞吐量 ≥100 候选/周（quant-crypto 实测 ~5/周是卡死留出门的根因）。
11: 对 2026-09 时点开源生态的调研结论：
12: 
13: - **AlphaGen**（ICT-FinD-Lab/alphagen，原 RL-MLDM，1.2k★）：RL 表达式生成 + 线性协同池；
14:   核心优势是代码冻结带不走的——协同池（增量 IC reward，机制性防冗余）+ GPU 张量评估（吞吐）+ 量化原生算子。
15:   已知问题：无 LICENSE（个人私有使用，风险可忽略）；核心 21 个月未实质更新；
16:   requirements.txt 自身损坏（`qlib==0.0.2.dev20` 是装错的包、numpy/pandas 为 2021 版）。
17: - **gplearn**：v0.4.3 复活（2026-01），BSD-3，但无协同概念、fitness 全样本评估有结构性泄漏、分钟级慢。
18: - **Qlib 表达引擎**：maint
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0003-validation-gate-non-degradation.md</path>
<type>file</type>
<content>
1: # ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：`D:\Projects\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
7:   PRD G2 / FR3
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
20: 1. **留出门不降级**：任何候选必须通过最终 90 天留出才能进入 paper/实盘——此规则从
21:    quant-crypto 原样继承，永不为吞吐量让路。
22: 2. **样本量门槛**：留出期 ≥30 笔交易才允许 FAIL/PASS 判定；样本不足输出 `UNDERPOWERED`
23:    
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 4 file(s)

D:\Projects\alphamill\docs\decisions\0003-validation-gate-non-degradation.md
D:\Projects\alphamill\docs\decisions\0002-external-dependency-policy.md
D:\Projects\alphamill\docs\decisions\0001-factor-mining-engine.md
D:\Projects\alphamill\docs\decisions\000-template.md
  ```
  </details>

## assistant · 2026-09-06T16:43:34Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\000-template.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0002-external-dependency-policy.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\reviews\\CURRENT-doc.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\tools\\validate_spec_lifecycle.py"})`


> [reasoning] There's no ADR README/index in docs/decisions/ — only 000-template.md, 0001, 0002, 0003. docs/README.md has an ADR list section though. My ownership says "docs/decisions/README.md or index file if one exists (update ADR list only if such file exists)". docs/README.md exists but it's owned by others? The task says "update ADR list only if such file exists" — the file docs/README.md exists and has a doc index table including ADR rows. Hmm, but the ownership list says "docs/decisions/README.md or index file if one exists". docs/README.md is a docs index that lists ADRs individually (0001, 0002, 0003 rows). Since 0004 is new, should I add it? The ownership says "docs/decisions/README.md or index file if one exists (update ADR list only if such file exists)". docs/README.md is arguably "an index file" — it lists ADRs. But it also might be owned by another agent. The mandate is scoped: "update ADR list only if such file exists". The docs/README.md contains the ADR list (three rows for ADRs). To keep cross-references consistent, I should add an ADR-0004 row there. But wait — MUST NOT touch README? "MUST NOT: touch PRD/architecture/SOP/README (other agents own them)". That says README — likely means the root README.md. docs/README.md is "or index file if one exists (update ADR list only if such file exists)" — my ownership explicitly includes an index file if one exists. The safest interpretation: docs/decisions/ has no README/index → skip. But docs/README.md's ownership matrix says "跨 Feature 长期决策 | decisions/ | ADR 决策记录" — it doesn't hardcode a list of ADR numbers in the matrix... Actually it does list individual ADRs in the 权威文档所有权矩阵: rows for 0001, 0002, 0003. And the root README.md also lists ADRs in 文档索引 table.

The validator might check that the docs README entries exist. Let me check the validator and review report first. Let me read the template, 0002 (for style), the review report, and the validator.

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\000-template.md</path>
<type>file</type>
<content>
1: # ADR-NNN：[决策标题]
2: 
3: 日期：[YYYY-MM-DD]
4: 状态：Proposed
5: 关联规格：[spec link]
6: 
7: ## 背景
8: 
9: [需要做出什么决策，约束是什么。]
10: 
11: ## 决策
12: 
13: [选择及其明确边界。]
14: 
15: ## 备选方案
16: 
17: - [方案 A：优缺点]
18: - [方案 B：优缺点]
19: 
20: ## 后果
21: 
22: - 正面：
23: - 负面：
24: - 后续行动：

(End of file - total 24 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0002-external-dependency-policy.md</path>
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
10: AlphaMill 引入四个开源项目：AlphaGen（挖掘引擎）、Freqtrade（执行）、Vibe-Trading（研究上层）、
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
22: | Vibe-Trading | 原样依赖（pip pin + 本机 CLI/服务） | 只碰
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\reviews\CURRENT-doc.md</path>
<type>file</type>
<content>
1: ---
2: report_type: doc-review
3: round: 1
4: date: 2026-09-07
5: prior_report: 无（首轮全量检视）
6: scope: full-scan
7: stop_condition_met: false
8: severity_counts: {critical: 2, high: 8, medium: 10, low: 4}
9: issue_count: 24
10: baseline: main @ 1bd8c4d（2026-09-07 00:08 +0800，唯一 bootstrap 提交，工作树干净）
11: reviewer: Sisyphus（review-convergence 协议）
12: evidence: 检视人全量通读 docs 全部 17 份文件 + explore agent 代码区实测（verify.py 四步全绿）+ Oracle agent 战略/架构交叉评审（三路独立取证）
13: note: 本仓 CLAUDE.md 约定 CURRENT-doc.md / CURRENT-code.md 入库（覆盖 skill 默认的 local-only）；本文件为第 1 轮全量扫描，尚无修复方声明
14: issues_index:
15:   - {id: D001, severity: critical, title: 组合构建层缺失——协同池产物无部署路径}
16:   - {id: D002, severity: critical, title: 成本墙（费用+滑点+资金费率）不在
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\tools\validate_spec_lifecycle.py</path>
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
9:   - BACKLOG.md 与所有非 done Feature 双向集合一致
10: 
11: 纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
12: 并补了变异测试。用法：python tools/validate_spec_lifecycle.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15: 
16: from __future__ import annotations
17: 
18: import pathlib
19: import re
20: import sys
21: 
22: ROOT = pathlib.Path(__file__).resolve().parent.parent
23: ALLOWED_STATU
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:43:54Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md"})`


> [reasoning] The validator only checks features/ and BACKLOG.md — ADRs are not checked. Good, low risk.

Now let me read the PRD sections on G1-G5/FR2/FR3/milestones to anchor context. Let me read the PRD.
Validator only checks `docs/features/` + BACKLOG — ADRs are unvalidated, low risk. Now reading PRD for anchoring:

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\alphamill-prd.md</path>
<type>file</type>
<content>
1: # AlphaMill — 产品需求文档（PRD）
2: 
3: > 版本：v0.1 | 日期：2026-09-06 | 状态：草案
4: > 前置文档：`D:\Projects\tradingview-quant-research\research.md`（TradingView 调研）、`D:\Projects\quant-crypto\00-系统总体方案.md`（上一代系统）
5: 
6: ---
7: 
8: ## 一、背景与问题定义
9: 
10: ### 1.1 quant-crypto 复盘（2026-05 ~ 2026-06）
11: 
12: 上一代项目 quant-crypto 用 5 周时间完成了大量基础设施：
13: 
14: | 资产 | 状态 | 位置 |
15: |---|---|---|
16: | TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | `D:\Projects\quant-crypto` |
17: | 衍生品特征数据 | ✅ funding / mark-index basis / open interest 已回补 | `db/migrations/003` |
18: | Kronos 信号基建 | ✅ Kronos-base GPU 推理，RankIC > 0.05（自定"强有效"门槛） | `kronos-signal/` |
19: | 信号缓存模式 | ✅ 预计算 → feather → 策略按时间戳读取，**已通过无前视审计** | `freq
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:44:04Z

- **tool**: `grep({"include": "alphamill-integration.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs", "pattern": "Top1|单因子|单策略|协同池"})`


> [reasoning] Now let me also check the integration doc's §四 (deployment model: single-factor single-strategy + Top1-only dry-run) since ADR-0004 must reference it accurately. Let me quickly grep for Top1 in integration doc.

  <details><summary>tool output</summary>

  ```text
Found 1 match(es) in 1 file(s)

D:\Projects\alphamill\docs\alphamill-integration.md
  155: **多条候选同时通过留出的处理**：按成本后 Sharpe 排序，取 Top1 进 dry-run；其余进入 monitoring 队列（防止 paper 组合同时验证多个高相关候选）。
  ```
  </details>

## assistant · 2026-09-06T16:44:12Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "limit": 60, "offset": 130})`

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\alphamill-integration.md</path>
<type>file</type>
<content>
130: 3. warmup 期禁止产生交易；
131: 4. 审计不通过 → 部署流水线拒绝生成配置。
132: 
133: ### 3.3 部署流水线（FR5.3）
134: 
135: ```text
136: 留出 PASS → writer 写 signal_cache → 渲染策略模板 → freqtrade backtesting 冒烟（7 天）
137:         → dry-run 挂载（与现有 KronosFusionStrategy 并存，独立策略类）
138:         → 人工确认 → paper
139: ```
140: 
141: ---
142: 
143: ## 四、验证门禁迁移设计
144: 
145: quant-crypto 的门禁脚本参数化迁移到 `validation/`：
146: 
147: | 迁移件 | 改造点 |
148: |---|---|
149: | 选择期脚本 | 窗口/阈值外置配置（`validation/config.yaml`），规则先于数据确定并 git 提交 |
150: | 最终 90 天留出 | 新增 **≥30 trades 判定门槛**：样本不足输出 `UNDERPOWERED`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口） |
151: | 独立重放器 | 接口化为 `no_lookahead_audit(factor_def)`，进入因子工厂流水线而非一次性脚本 |
152: | 成本敏感性 | 三档（taker/maker/零成本）为标准输出列，成本后 Sharpe 为排序主键 |
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:44:19Z

- **tool**: `write({"content": "# ADR-0004：组合构建层 —— 协同池组合可部署化与 Top-K 策略映射\n\n- 日期：2026-09-07\n- 状态：Accepted\n- 决策人：Georg\n- 背景：检视报告 D001（[`docs/reviews/CURRENT-doc.md`](../reviews/CURRENT-doc.md)）；集成文档 §四 的\n  Top1-only 部署政策；PRD FR2.1 / FR5\n\n## 背景\n\nAlphaGen 主引擎的核心产出是协同池（LinearAlphaPool：基础因子的线性组合，增量 IC reward\n机制性防冗余），但当前部署设计只有两条路：单因子单策略模板（集成文档 §3.3）+ 多候选同过\n留出时取 Top1 进 dry-run（集成文档 §四）。结果是：\n\n1. **组合 alpha 没有部署路径**——主引擎最有价值的输出在系统里是死产出；\n2. Top1-only 同时丢弃了多存活因子的组合价值：N 个存活因子 = N 个独立策略的替代方案，\n   资本碎片化、费用×N、同一 pa
…[truncated])`


> [reasoning] I have all the context. Now let me write the three files.

Note on ownership: docs/decisions/ has no README/index file (only 000-template + 3 ADRs), so per my ownership instructions "update ADR list only if such file exists" — no such file exists, skip. The root README.md and docs/README.md are owned by others (MUST NOT touch README).

Now write ADR-0004. House style from 0001/0002/0003: H1 title "ADR-000N：标题 —— 副标题", bullet metadata (日期/状态/决策人/links), then sections. 0001/0003 use 背景/决策/后果; template includes 备选方案. Task says "Consequences/alternatives section per ADR house style (match 0001/0003 structure exactly: 背景/决策/备选/后果 or whatever the existing ADRs use)". Existing ADRs (0001, 0002, 0003) use 背景/决策/后果 — no 备选 section. But the task explicitly requires an alternatives section. I'll follow 背景/决策/备选/后果 and add 备选 — that matches the template too, and satisfies the task's requirement.

Content for ADR-0004:

Title: ADR-0004：组合构建层 —— 协同池组合可部署化 + Top-K 组合策略映射
Date: 2026-09-07, Status: Accepted, 决策人: Georg, 关联: PRD FR2.1/FR5, ADR-0003, integration §四.

背景: D001 — AlphaGen 核心产出为协同池（线性组合），但部署模型（integration §四）只支持"单因子单策略模板 + 多候选同过留出时取 Top1 进 dry-run"。即主引擎最有价值的输出（组合 alpha）没有部署路径；且 Top1-only 政策丢弃了组合价值、资本碎片化、费用×N、同 pair 多空冲突未设计。

决策:
1. 协同池组合 = 可部署 meta-因子。一条组合（若干基础因子的线性组合）视作一个策略候选，注册进因子注册表，走与单因子完全相同的评测台→选择期→90 天留出门禁路径，无任何捷径（ADR-0003 判据原样适用）。
2. 因子→策略映射：Top-K 组合取代 Top1-only。v0.1 K=3（上限 5）；权重方案 v0.1 = 逆波动率加权（inverse-volatility），简单、参数少；优化类权重（等风险/最小方差）明确后移。多候选同过留出时，取成本后 Sharpe 前 K（而非 Top1）分别挂 dry-run；其余进 monitoring 队列（防高相关候选同验证）。
3. 换手预算：每个再平衡周期设显式换手上限，v0.1 默认单周期换手 ≤ 100%（全仓翻转一次）；换手预算作为成本模型的门禁输入（超过预算的候选在评测台即标记，不进留出）。
4. 净敞口上限 + 同 pair 冲突规则：v0.1 = 每 pair 仅一个策略持有信号；同一 pair 上出现方向冲突的信号时，在组合构建层先净额化（netting）再写信号缓存，Freqtrade 只看到净后信号；进阶净额化（跨策略 margin 级对冲）后移。
5. 组合层落位：`portfolio/`（或 validation 内?）——不要发明架构新模块？ADR 可以说落位在 factor_factory 与 freqtrade 之间的组合构建层。我可以说明实现层位为组合构建层（架构文档归属他人，不指定目录路径，避免和架构文档冲突）。 Better to keep implementation location loose: "组合构建层作为独立层实现，介于因子注册表与信号缓存之间"。

备选:
- 方案 A（选定）：Top-K meta-因子组合 + 简单权重。
- 方案 B：维持 Top1-only —— 优点零新增复杂度；缺点协同池价值全丢弃，资本碎片化、费用×N。
- 方案 C：组合优化器（mean-variance/风险平价 + 约束求解）—— 优点理论上最优；缺点 v0.1 无统计功效支撑估计协方差，复杂度先行违反"简单优先"。

后果:
- 正面：主引擎核心产出有部署路径；组合 alpha 可被验证；Top-K 提供分散化与策略间对照。
- 负面/义务：K>1 使 dry-run 资源×K；净额化规则需在信号缓存写入前实现，是新增组件；逆波动率权重在因子高度相关时分散化效果有限——须配合注册表 IC 相关性查重（FR2.3）。
- 后续：K/换手预算/权重方案参数全部进 validation/config.yaml，规则先于数据确定。

Also mention net exposure cap — task says "Net exposure cap + same-pair conflict rule: v0.1 = one strategy per pair". So the net exposure cap in v0.1 IS the one-strategy-per-pair rule? Reading again: "Net exposure cap + same-pair conflict rule: v0.1 = one strategy per pair; conflicting signals on same pair are netted at portfolio-construction layer before hitting Freqtrade (state this explicitly, defer advanced netting)." So v0.1: net exposure cap is implicitly enforced by one-strategy-per-pair; conflicts netted at portfolio layer. I'll state both.

ADR-0003 amendments (D005, D006, D008): add new sections WITHOUT altering existing frozen criteria wording. Structure: keep 背景/决策/后果 intact, add new sections after 决策 (or after 后果?). Since I cannot alter existing wording, I'll add new top-level sections:

- ## 留出期使用预算（D005 补强，2026-09-07）
- ## 样本量门槛的功效论证（D006 补强，2026-09-07）
- ## 复盘循环窥探防护（D008 补强，2026-09-07)

Wait — the 30-69 band: existing criterion says ≥30 allows FAIL/PASS judgment. I can't alter that wording. I add a section that: ≥30 是绝对硬下限（低于 30 连评测都不允许）；30-69 笔为 UNDERPOWERED 带——该带内 PASS 仅是临时性的（仅限缩减仓位的 paper 试运行 + 延长观察期），不构成可信判定；可信判定需要 ≈69+ 笔（引用 PRD §1.2 自身诊断）；功效依据：α=0.05/80% 功效下最小可检测效应对应的样本量在该区间。

Careful: original 决策 2 says "留出期 ≥30 笔交易才允许 FAIL/PASS 判定；样本不足输出 UNDERPOWERED". My addition reframes 30-69 as provisional. That's stricter, never looser. Good — task explicitly says "The gate becomes stricter in effect, never looser."

D005: holdout budget — weekly access budget: top-k candidates per week pass to holdout, k as config with v0.1 default. State k=5. Holdout usage ledger: append-only, one row per holdout evaluation (candidate id, date, result). Permanently isolated final-confirmation window: data segment no candidate evaluated during development may touch, used only once before paper promotion.

D008: review-loop peeking guard — generation tag + trials ledger (same ledger as D005); final-confirmation window never exposed to review loop; review-loop hypotheses count toward multiple-testing budget (PRD FR2.4).

Update frontmatter `updated:` — but ADR-0003 has no frontmatter! It uses bullet metadata (- 日期：2026-09-06). Task says "Update the ADR's frontmatter `updated:` to 2026-09-07 if it has frontmatter." It doesn't have frontmatter, so I add a line to the metadata bullets instead? Hmm. The style is `- 日期：2026-09-06`. I could add `- 修订：2026-09-07（补强 D005/D006/D008，判据本体不变）`. That preserves style without touching frozen wording. The instruction "do not alter existing frozen criteria wording" refers to gate criteria; metadata line addition is fine. I'll add a 修订 bullet after 日期.

ADR-0001 amendment (D012): add a checkable downgrade-criteria list. Add a section "## 降级切换判据（D012 补强，2026-09-07）" with binary criteria:

切换到 L1（AlphaGen 表达式求值器 + 自写搜索，绕开 RL）当且仅当满足任一条：
- [ ] 冒烟闸门 time-box（2 个工作日）到期时未跑通 1 个 PPO epoch → 立即切 L1，不留缓冲；
- [ ] vendor 现代栈适配在冒烟期内出现阻塞依赖（sb3/gymnasium 不兼容无法在冒烟期内修复）——具体化：依赖失败：sb3+gymnasium 无法在第 1 天结束前跑通最小训练循环；
- [ ] feather→tensor 适配器未在第 2 天结束前产出首个可评测因子。

切换到 L2（纯 gplearn）当且仅当满足任一条：
- [ ] L1 启用后连续 2 周周产出 < 50 候选进评测台（M2 出口标准的量化线）；
- [ ] L1 连续 2 周未能产出任何通过无前视审计的候选。

Hmm, need to be careful about matching M2 exit standard: "单次挖掘 ≥50 候选". Weekly candidate quota — task says "if L1 misses weekly candidate quota for N consecutive weeks". Use N=2, quota = 50 候选/周 (matching M2 出口 "单次挖掘 ≥50 候选 → 自动评测"). I'll define quota as ≥50/周.

Also add self-exemption guard: "判据为二元可测项；到期未达标即切换，不允许'再给一天'的自我豁免；切换决策记录进 experiment manifest" or similar.

Also ADR-0001 has metadata bullets `- 日期：2026-09-06`. Add `- 修订：2026-09-07（补降级切换判据）`.

Now dates: today is 2026-09-07 per env. Good.

Also should I mention the review report? ADRs reference PRD etc. I'll reference the review report lightly (D-IDs) since it's in-repo. Actually current-doc.md is a review report — fine to cite as evidence.

Let me also check CLAUDE.md quickly? Not strictly needed. Skip to save time — actually the instructions say match doc style. I've seen 3 ADRs; that's enough.

One more check: docs/README.md ownership matrix — "跨 Feature 长期决策 | decisions/". No per-ADR hardcoded list that requires updating. docs/decisions/ has no README/index → skip per my ownership instruction.

Also verify tools/verify.py — does it check anything about docs (like dead links)? The task says run validate_spec_lifecycle.py only. The validator code I read doesn't touch decisions/. Fine.

Now write the files.

ADR-0004 content draft:

# ADR-0004：组合构建层 —— 协同池组合可部署化与 Top-K 策略映射

- 日期：2026-09-07
- 状态：Accepted
- 决策人：Georg
- 背景：检视报告 D001（`docs/reviews/CURRENT-doc.md`）+ 集成文档 §四 的 Top1-only 部署政策

## 背景

AlphaGen 主引擎的核心产出是协同池（LinearAlphaPool：基础因子的线性组合，增量 IC reward
机制性防冗余），但当前部署设计（集成文档 §四）只支持两条路：单因子单策略模板 + 多候选
同过留出时取 Top1 进 dry-run。结果：

1. **组合 alpha 没有部署路径**——主引擎最有价值的输出在系统里是死产出；
2. Top1-only 同时丢弃了"多存活因子"的分散化价值：5 个存活因子 = 5 个独立策略的替代方案
   （资本碎片化、费用×N、同一 pair 上多空信号冲突）均未设计。

组合构建层缺失是 Critical：现在拍板是改文档，M1 之后拍板是改代码+改数据。

## 决策

1. **协同池组合 = 可部署 meta-因子**：协同池输出的每条线性组合视作一个策略候选，与单因子
   走完全相同的路径——注册表查重（FR2.3）→ 统一评测台 → 选择期 → 最终 90 天留出
   （ADR-0003 判据原样适用）→ 部署流水线。**没有任何捷径**：组合不因"来自协同池"而豁免
   任何门禁或无前视审计。
2. **因子→策略映射：Top-K 组合取代 Top1-only**：多候选同过留出时，按成本后 Sharpe 取
   前 K 个分别进 dry-run（v0.1：K=3，硬上限 5），其余进 monitoring 队列（防高相关候选
   同窗验证，沿用原 Top1 规则的动机）。K 为配置项（`validation/config.yaml`，规则先于
   数据确定）。
3. **权重方案 v0.1 = 逆波动率加权**：组合内各 meta-因子按已实现波动率倒数加权。选择理由：
   参数少、无需估计协方差矩阵；等风险/最小方差等优化类权重明确后移到 v0.2+，不与 v0.1
   里程碑耦合。
4. **换手预算为门禁输入**：每个再平衡周期设显式换手上限，v0.1 默认单周期换手 ≤100%
   （全仓翻转一次）。换手预算进入成本模型（ADR-0003 决策 4 的三档成本敏感性）：超预算
   的候选在评测台即标记 `over_turnover_budget`，不进留出——成本墙在评测台前置拦截的
   一部分（D002 的修复口径归评测台条款，本 ADR 只定义预算本身）。
5. **净敞口与同 pair 冲突（v0.1 规则）**：每 pair 同时只允许一个策略持有活跃信号；同一
   pair 上出现方向冲突的候选信号时，在组合构建层先净额化再写信号缓存——Freqtrade 只
   看到净后信号，永不接收自相矛盾的信号流。进阶净额化（跨策略对冲、保证金级合并）后移，
   v0.1 不做。
6. **落位**：组合构建层是因子注册表与信号缓存 writer 之间的独立层（输入 = 通过留出的
   候选集合，输出 = 净后信号缓存条目 + 权重配置）；目录与接口归属架构文档，
   本 ADR 只约束行为。

## 备选方案

- 方案 A（选定）：Top-K meta-因子 + 逆波动率权重 + 换手预算。优点：主引擎产出全有路径；
  实现简单、参数可数；K 与权重全部配置化。缺点：逆波动率在因子高相关时分散化有限，
  依赖注册表查重兜底。
- 方案 B：维持 Top1-only。优点：零新增组件。缺点：协同池价值全丢弃；同时过留出的候选
  只能串行验证，周期×K。
- 方案 C：组合优化器（均值方差/风险平价 + 约束求解）。优点：理论上资本效率最优。缺点：
  v0.1 样本量撑不起协方差估计（正是 D006 指出的功效问题）；复杂度先行违反冒烟闸门精神。

## 后果

- 正面：协同池产出获得完整部署路径；Top-K 提供策略间对照（champion-challenger 的雏形）；
  同 pair 冲突在进入 Freqtrade 前被结构化消解。
- 负面/义务：K>1 使 dry-run 资源占用×K；组合构建层是新增组件，必须在 M4 前实现且过
  独立重放审计；净额化逻辑是正确性敏感代码，属于 review 从严范围。
- 后续行动：K/换手预算/权重方案参数进 `validation/config.yaml`；组合构建层的验收标准
  在对应 feature spec 中定义（引用本 ADR）。

Hmm — one issue: task says "Turnover budget: explicit cap per rebalance period (state a v0.1 default and that it's a gate input to the cost model)". Done. "state one [weight scheme], keep simple, defer optimization" — done (inverse-vol).

Also D006 reference in 方案 C — keep it, it's fine.

Length is reasonable and matches house style.

ADR-0003 amendments — add after "## 决策" list and before "## 后果"? Or after 后果? Adding new top-level sections between 决策 and 后果 keeps 决策 as the frozen core. I'll insert three new sections after 决策 (i.e., between 决策 and 后果):

## 留出期使用预算（2026-09-07 补强 · D005）

留出窗口是**可耗竭的统计资源**：5000 候选/年过同一个 90 天窗，窗口在统计上退化为训练集，
留出门"从不放水"的可信度随之蒸发。补强规则（判据本体不动）：

1. **周度访问预算**：每周允许进入最终留出评估的候选上限 top-k，v0.1 默认 k=5（配置项，
   `validation/config.yaml`）；未获配额的候选排队下一周期，不得"顺手多跑一个"。
2. **留出使用台账**：append-only，每次留出评估一行——候选 ID、日期、判定结果；台账与
   manifest 同为可复现要件。预算消耗以台账为准，不支持事后补记。
3. **永久隔离的最终确认窗**：一段独立数据片段，开发期任何候选（含评测台/选择期/复盘循环）
   均不得接触，仅在候选晋升 paper 前使用一次——最终确认窗的判定为终局判定。

## 样本量门槛的功效论证（2026-09-07 补强 · D006）

PRD §1.2 自身诊断："69 笔交易的 FAIL/PASS 判定统计上不可信"。本 ADR 决策 2 的 ≥30 笔
在此显式澄清为**绝对硬下限**（低于 30 笔连评估资格都没有，直接 `UNDERPOWERED`），
而非可信判定的充分条件：

- **30~69 笔 = UNDERPOWERED 带**：该区间内即使指标达标，判定也仅为**临时 PASS**——只允许
  进入缩减仓位的 paper 试运行 + 延长观察期（观察至样本跨过 69 笔或触发衰减下线），
  不构成可信判定，不得用于任何实盘前置论证。
- **可信判定需 ≈69+ 笔**：α=0.05、80% 功效下，最小可检测效应对应的样本量落在该区间量级
  （与 PRD §1.2 对 69 笔的不可信诊断一致，69 笔是下界而非充分值）。
- 本补强只收紧、不放松：≥30 的评估资格下限不变，30-69 带新增的是限制而非豁免。

Wait — careful with the power rationale sentence. The task says: "add a short power-rationale sentence: at α=0.05/80% power the minimum detectable effect implies sample sizes in that range". And "reliable judgment needs ≈69+ trades (reference the PRD's own diagnosis)". OK my draft covers it. But note: "69 笔不可信" in PRD means 69 trades is NOT reliable. Hmm, the review report D006 says: "要么按 ≥69/功效计算定门槛，要么显式声明 30 仅为 UNDERPOWERED 下限、可信判定需更高样本并说明". And the task instructs: "reliable judgment needs ≈69+ trades (reference the PRD's own diagnosis...)" and "30-69 trades = UNDERPOWERED band". So the task wants: 30-69 = underpowered; ≈69+ = reliable. But PRD says 69 is unreliable... The task explicitly says "reliable judgment needs ≈69+ trades". I'll phrase carefully: "≈69 笔只是下界量级参考——功效论证要求样本量在该量级之上" — hmm, that might overcomplicate. Let me follow the task literally but add nuance: "可信判定需要样本量达到 ≈69 笔量级及以上（69 笔在 PRD §1.2 的语境中已被诊断为勉强/不可信的边界，故 69 是下界而非安全值）". Actually re-reading PRD: "留出期样本量不足（69 笔交易的 FAIL/PASS 判定统计上不可信）". So PRD says at 69 trades the judgment is unreliable. Task says: "reliable judgment needs ≈69+ trades (reference the PRD's own diagnosis; add a short power-rationale sentence: at α=0.05/80% power the minimum detectable effect implies sample sizes in that range)". So the intended reading: the power analysis says you need samples in the range of ~69 (i.e., 30-69 is underpowered; at ~69 you're at the edge where the MDE becomes detectable at 80% power). The PRD's "69 笔不可信" diagnosis aligns with "69 is the boundary where power is just barely adequate" — the fix direction per the review: declare 30 as floor, 30-69 provisional, ≈69+ needed. I'll phrase: "可信判定需要 ≈69+ 笔（PRD §1.2 对 69 笔'不可信'的诊断，正说明 69 笔只是功效勉强及格的量级下界——低于它必然更不可信）"。 Hmm, that's a fair reconciliation: PRD diagnosed 69 as untrustworthy; the gate currently allows judgment at 30. The resolution: 30 = floor, 30-69 provisional, ≈69+ = the range where power analysis says MDE is detectable at 80% power. But if PRD says 69 itself is untrustworthy, then ≈69+ means "around 69 or more" — the boundary. I'll write it so that ≈69 is the lower bound of the reliable band and note the PRD diagnosis refers to being below/near that boundary. Keep it simple:

- **30~69 笔 = UNDERPOWERED 带**...
- **可信判定需要 ≈69 笔及以上**：α=0.05 / 80% 功效下，最小可检测效应对应的样本量即在该
  量级；PRD §1.2 对"69 笔不可信"的诊断指的正是这一临界带——30 笔显然更不可信，故
  30-69 只能作临时判定，69+ 才是功效论证支持的最低可信量级。

Hmm, slight tension but defensible. Actually let me re-read the task once more: "reliable judgment needs ≈69+ trades (reference the PRD's own diagnosis; add a short power-rationale sentence: at α=0.05/80% power the minimum detectable effect implies sample sizes in that range)". OK so task wants exactly that. I'll write it as instructed, referencing PRD §1.2.

## 复盘循环窥探防护（2026-09-07 补强 · D008）

FR4.3 的 agent 复盘循环（读结果 → 产假设 → 同一段历史再测）是数据窥探放大器：同一段
留出/选择期历史被反复"看图说话"，假设生成与评估共用数据，多重检验风险随代次累积。
补强规则：

1. **代次标记**：复盘循环产出的每条假设带 generation 标签（来源 = review-loop，代次 = 第几轮），
   与普通候选一样计入试验台账（与留出使用台账同一台账体系）；
2. **试验预算计入**：复盘假设的每一次评估计入 PRD FR2.4 的多重检验预算——复盘产出的
   假设不享受任何"人工智慧"豁免，与程序化候选同一口径计数；
3. **最终确认窗隔离**：上一节定义的永久隔离最终确认窗，对复盘循环不可见——agent 的输入
   （manifest + 报告）不得包含最终确认窗上的任何统计量；确认窗只在晋升 paper 前使用一次。

三节的日期标记用 (2026-09-07 · D00X 补强)。

For ADR-0003 metadata: add `- 修订：2026-09-07（补强留出预算 / 功效论证 / 复盘防护，判据本体不变）` after the 背景 bullet or after 日期? The metadata block is:

- 日期：2026-09-06
- 状态：Accepted
- 决策人：Georg
- 背景：...

I'll insert 修订 after 日期:
- 日期：2026-09-06（2026-09-07 补强：D005/D006/D008）
Or a separate bullet: `- 修订：2026-09-07`. I'll add separate bullet.

ADR-0001 amendment (D012): add section after 决策 (before 后果), plus 修订 bullet.

## 降级切换判据（2026-09-07 补强 · D012）

冒烟闸门 time-box 已定（2 个工作日），但"何时降级"此前未成文——单人 time-box 最容易
自我豁免。切换判据预写成二元可测项，到期未达标即切换，**不允许"再给一天"的自我豁免**；
切换动作与原因记入当日 experiment manifest。

**切到 L1（表达式求值器 + 自写搜索，绕开 RL）**——满足任一条即触发：

- [ ] 冒烟 time-box（第 2 个工作日结束）未跑通 1 个 PPO epoch；
- [ ] 第 1 个工作日结束时，sb3/gymnasium 现代栈适配仍未跑通最小训练循环（依赖阻塞，
  判定 vendor+RL 路线风险不可控）；
- [ ] 第 2 个工作日结束时，feather→tensor 适配器未产出首个可 RankIC 对齐的因子。

**从 L1 切到 L2（纯 gplearn）**——满足任一条即触发：

- [ ] L1 连续 2 周、每周进评测台候选 <50（M2 出口标准的量化线：单次挖掘 ≥50）；
- [ ] L1 连续 2 周零候选通过无前视审计（产出质量归零，吞吐无意义）。

判据里引用 M2 出口 "单次挖掘 ≥50 候选" — careful: weekly quota vs 单次挖掘. Task says "if L1 misses weekly candidate quota for N consecutive weeks". M2 exit: 单次挖掘 ≥50 候选. I'll define the weekly quota as: 周产出（进评测台）< 50，连续 2 周. That's the "weekly candidate quota". Fine — I'm defining it, matching the M2 number for coherence.

Also note in ADR-0001, the ladder: L1 = AlphaGen 表达式求值器 + 自写搜索; L2 = 纯 gplearn. My criteria match.

One consideration: "switch to L1 ... if smoke gate exceeds its time-box by X or vendor deps fail Y". My criteria: time-box exceeded (day 2 end without PPO epoch) → L1; deps fail (day 1 end without minimal training loop) → L1. Good, concrete and binary.

Also add: 降级路径单向? No — allow re-attempt? Keep simple: 切换后不自动回切；回切需重新过冒烟闸门（重开 time-box）。That's a sensible addition, keep short.

Now write the files. First create ADR-0004, then edit 0003, then edit 0001. Then run validator.

For 0003 edit, I need to insert new sections. I'll insert them between 决策 section end and ## 后果. The oldString anchor: 

```
5. **实盘前置条件不变**：没有留出通过的候选，不触碰实盘下单路径（PRD 非目标硬约束）。

## 后果
```

And for metadata: 
```
- 日期：2026-09-06
- 状态：Accepted
```
→ add 修订 line after 决策人 line? Put it at the end of metadata block:
```
- 背景：`D:\Projects\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
  PRD G2 / FR3
```
Add after that: `- 修订：2026-09-07（D005/D006/D008 补强：留出预算 / 功效论证 / 复盘防护；判据本体未动）`

For 0001: metadata add 修订 line after 证据全文 line. Insert section between 决策 item 4 and ## 后果.

Let me now write everything.
All context anchored. `docs/decisions/` has no README/index file (only 000-template + 3 ADRs), so no index update needed. Validator only checks `docs/features/` + BACKLOG — ADRs unvalidated.

**Step 1 of 4: Create ADR-0004 (D001)**

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.
  ```
  </details>

## assistant · 2026-09-06T16:47:28Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0003-validation-gate-non-degradation.md", "newString": "- 背景：`D:\\Projects\\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与\n  PRD G2 / FR3\n- 修订：2026-09-07（检视 D005/D006/D008 补强：留出预算 / 功效论证 / 复盘防护；下列\"决策\"节\n  判据本体一字未动，补强只收紧、不放松）", "oldString": "- 背景：`D:\\Projects\\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与\n  PRD G2 / FR3"})`


> [reasoning] Step 2: amend ADR-0003. Two edits: metadata line + three new sections before ## 后果.
**Step 2 of 4: Amend ADR-0003 (D005/D006/D008)**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:47:48Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0003-validation-gate-non-degradation.md", "newString": "5. **实盘前置条件不变**：没有留出通过的候选，不触碰实盘下单路径（PRD 非目标硬约束）。\n\n## 留出期使用预算（2026-09-07 补强 · D005）\n\n留出窗口是**可耗竭的统计资源**：5000 候选/年过同一个 90 天窗，窗口在统计上退化为训练集，\n\"从不放水\"的可信度随之蒸发。补强规则（判据本体不动）：\n\n1. **周度访问预算**：每周允许进入最终留出评估的候选上限 top-k，v0.1 默认 k=5（配置项，\n   `validation/config.yaml`）；未获配额的候选排队下一周期，不得\"顺手多跑一个\"。\n2. **留出使用台账**：append-only，每次留出评估一行——候选 ID、日期、判定结果；台账与\n   manifest 同为可复现要件。预算消耗以台账为准，不支持事后补记。\n3. *
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:48:23Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0001-factor-mining-engine.md", "newString": "- 日期：2026-09-06\n- 修订：2026-09-07（检视 D012 补强：L1/L2 降级切换判据预成文；决策本体未动）\n- 状态：Accepted", "oldString": "- 日期：2026-09-06\n- 状态：Accepted"})`


> [reasoning] Step 3: amend ADR-0001 (D012). Add 修订 bullet + downgrade criteria section before ## 后果.
**Step 3 of 4: Amend ADR-0001 (D012)**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:48:47Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0001-factor-mining-engine.md", "newString": "4. **对照基线**：AlphaGen 仓库自带的 gplearn/ 与 dso/ 直接利用，不单独引入 gplearn 项目。\n\n## 降级切换判据（2026-09-07 补强 · D012）\n\n冒烟闸门 time-box 已定（2 个工作日），但\"何时降级\"此前未成文——单人 time-box 最容易\n自我豁免。以下判据预写为**二元可测项**：到期未达标即切换，不允许\"再给一天\"；切换动作\n与触发原因记入当日 experiment manifest。降级不自动回切，回切须重开一轮冒烟 time-box。\n\n**切到 L1（AlphaGen 表达式求值器 + 自写搜索，绕开 sb3/RL）**——满足任一条即触发：\n\n- [ ] 第 2 个工作日结束时仍未跑通 1 个 PPO epoch（time-box 用尽）；\n- [ ] 第 1 个工作日结束时，
…[truncated])`

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:49:11Z

- **tool**: `bash({"command": "python tools/validate_spec_lifecycle.py", "workdir": "D:\\Projects\\alphamill"})`


> [reasoning] Step 4: validation. Run validate_spec_lifecycle.py. Also quickly re-read the amended files to sanity-check rendering.
**Step 4 of 4: Validate + verify final files**

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
  ```
  </details>

## assistant · 2026-09-06T16:49:27Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0003-validation-gate-non-degradation.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\decisions\\0001-factor-mining-engine.md", "limit": 30})`

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0003-validation-gate-non-degradation.md</path>
<type>file</type>
<content>
1: # ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：`D:\Projects\quant-crypto` Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
7:   PRD G2 / FR3
8: - 修订：2026-09-07（检视 D005/D006/D008 补强：留出预算 / 功效论证 / 复盘防护；下列"决策"节
9:   判据本体一字未动，补强只收紧、不放松）
10: 
11: ## 背景
12: 
13: quant-crypto 的最终 90 天留出门连续拦下全部候选（低频 Ridge/HGB、regime 增强、成本感知、
14: 衍生品 basis），看起来是"失败"，实际是验证协议在正确工作——它拦下的是会亏钱的东西。
15: 真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
16: 判定统计上不可信；regime filter 方向正确但 27 笔欠功效）。
17: 
18: 该门禁的价值来自它**从不放水**。任何"先上盘再观察"的妥协都会摧毁整个系统的可信度。
19: 
20: ## 决策
21: 
22: 1. **留出门不降级**：任何候选必须通过最终 90 天留出才能进入 paper/实盘——此规则从
23:    quant-cr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\decisions\0001-factor-mining-engine.md</path>
<type>file</type>
<content>
1: # ADR-0001：因子挖掘主引擎选型 —— AlphaGen vendor + 冒烟闸门 + 降级阶梯
2: 
3: - 日期：2026-09-06
4: - 修订：2026-09-07（检视 D012 补强：L1/L2 降级切换判据预成文；决策本体未动）
5: - 状态：Accepted
6: - 决策人：Georg
7: - 证据全文：[`docs/alphamill-research-factor-mining.md`](../alphamill-research-factor-mining.md)
8: 
9: ## 背景
10: 
11: PRD G1 要求因子假设吞吐量 ≥100 候选/周（quant-crypto 实测 ~5/周是卡死留出门的根因）。
12: 对 2026-09 时点开源生态的调研结论：
13: 
14: - **AlphaGen**（ICT-FinD-Lab/alphagen，原 RL-MLDM，1.2k★）：RL 表达式生成 + 线性协同池；
15:   核心优势是代码冻结带不走的——协同池（增量 IC reward，机制性防冗余）+ GPU 张量评估（吞吐）+ 量化原生算子。
16:   已知问题：无 LICENSE（个人私有使用，风险可忽略）；核心 21 个月未实质更新；
17:   requirements.txt 自身损坏（`qlib==0.0.2.dev20` 是装错的包、numpy/pandas 为 2021 版）。
18: - **gplearn**：v0.4.3 复活（2026-01），BSD-3，但无协
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:49:38Z

- **tool**: `bash({"command": "set CI=\"true\" && set DEBIAN_FRONTEND=\"noninteractive\" && set GIT_TERMINAL_PROMPT=\"0\" && set GCM_INTERACTIVE=\"never\" && set HOMEBREW_NO_AUTO_UPDATE=\"1\" && set GIT_EDITOR=\":\" && set EDITOR=\":\" && set VISUAL=\"\" && set GIT_SEQUENCE_EDITOR=\":\" && set GIT_MERGE_AUTOEDIT=\"no\" && set GIT_PAGER=\"cat\" && set PAGER=\"cat\" && set npm_config_yes=\"true\" && set PIP_NO_INPUT=\"1\" && set YARN_ENABLE_IMMUTABLE_INSTALLS=\"false\" && git status --short", "workdir": "D:\\Projec
…[truncated])`


> [reasoning] All done. Validator green. Let me do a final git status check to confirm only my 3 owned files changed (plus the pre-existing untracked review reports untouched).

  <details><summary>tool output</summary>

  ```text
M CLAUDE.md
 M README.md
 M docs/README.md
 M docs/SOP.md
 M docs/alphamill-prd.md
 M docs/decisions/0001-factor-mining-engine.md
 M docs/decisions/0003-validation-gate-non-degradation.md
 M docs/features/0.1/F001-quant-crypto-migration/spec.md
 M docs/features/README.md
?? docs/decisions/0004-portfolio-construction.md
?? docs/reviews/CURRENT-code.md
?? docs/reviews/CURRENT-doc.md
  ```
  </details>

## assistant · 2026-09-06T16:49:57Z


> [reasoning] Note: other files (CLAUDE.md, README.md, docs/README.md, SOP, PRD, F001 spec, features README) are modified by OTHER agents in parallel — not by me. My changes: 0001, 0003 (M) + 0004 (new). That matches my ownership exactly. Done.

Summary for the user, concise per ADHD style.
All 4 tasks done, validator green. Git status confirms I touched only my 3 owned files (other modified files belong to parallel agents).

**Changes:**
1. `docs/decisions/0004-portfolio-construction.md` (NEW, D001 Critical) — synergy-pool combos = deployable meta-factors through the identical gate (no shortcut); Top-K (v0.1 K=3, cap 5) replaces Top1-only; inverse-volatility weighting (optimization deferred); turnover cap ≤100%/rebalance as cost-model gate input; v0.1 = one strategy per pair + netting at portfolio layer before Freqtrade. 背景/决策/备选方案/后果 matches house style; Status Accepted, 2026-09-07.
2. `docs/decisions/0003-…md` (D005/D006/D008) — three new sections appended, frozen 决策 wording untouched: holdout budget (top-k/week, k=5 config, append-only ledger, permanently isolated final-confirmation window); 30=hard floor, 30–69=UNDERPOWERED band (provisional PASS only, reduced size, observation to ≥69), power rationale α=0.05/80%; review-loop hypotheses get generation tags + trials ledger + final-window invisibility + count toward FR2.4 multiple-testing budget.
3. `docs/decisions/0001-…md` (D012) — new binary checklist: →L1 if PPO epoch not running at day-2 end, OR sb3/gymnasium minimal loop not running at day-1 end, OR no RankIC-alignable factor at day-2 end; →L2 if <50 candidates/week for 2 consecutive weeks OR zero no-lookahead-audit passes for 2 weeks; no self-exemption, no auto-revert.
4. ADR index file: none exists in `docs/decisions/` (only 000-template) — skipped per instructions.

**Validation:** `python tools/validate_spec_lifecycle.py` → `全部通过`. No ADR-specific validator rules exist to trip (it only checks features/ + BACKLOG).

Next action (<2 min): reviewer can re-run the validator and spot-check ADR-0004's decision list against D001's five required elements.
