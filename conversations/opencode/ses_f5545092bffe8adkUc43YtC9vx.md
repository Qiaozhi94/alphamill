---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f5545092bffe8adkUc43YtC9vx"
title: "Validate F003 doc-fix contract decisions (@oracle subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T14:59:34Z"
updated_at: "2026-09-16T15:05:25Z"
tokens_input: 258813
tokens_output: 1972
cost: 0.0
parent_id: "ses_f55495de1ffeU7Bf0hQEDc3Md7"
---

# Validate F003 doc-fix contract decisions (@oracle subagent)

## user · 2026-09-16T14:59:34Z

You are validating a fix plan for a **documentation review** (not code) in the repo /home/georg/projects/alphamill.

CONTEXT
- The reviewed feature is F003 "alphagen-vendor", still `status: draft`, no code. Its docs are:
  - docs/features/0.2/F003-alphagen-vendor/spec.md
  - docs/features/0.2/F003-alphagen-vendor/design.md
  - docs/features/0.2/F003-alphagen-vendor/tasks.md
- The round-1 review report with 22 findings is docs/reviews/CURRENT-doc.md (read its issue table + suggested_fix for each).
- Upstream truth sources you must check against: docs/decisions/0001-factor-mining-engine.md (降级切换判据 + M2 冒烟验收), docs/decisions/0007-research-snapshot-binding.md, docs/alphamill-prd.md (FR2.1/FR2.3/FR2.4/FR2.6; FR1.7), docs/alphamill-architecture.md (§4.1 FactorDef, §4.1.1 adapter, §7.1 GPU slot), docs/features/0.2/F007-evaluation-gates/spec.md, docs/features/0.2/F008-universe-expansion/spec.md.
- Repo rules: docs/features/README.md; SOP docs/SOP.md; gates tools/validate_spec_lifecycle.py, tools/check_doc_links.py, tools/verify.py. Only the reviewer writes CURRENT-doc.md; I am the fixer.

TASK
I am the fixer. For each item below I state the resolution I intend to write into the F003 docs. Critique it: (a) does it contradict an upstream truth source or another F003 clause? (b) does it leave the original finding still true under any reading? (c) is there a simpler resolution? Answer per item, short, with file:line evidence. Do NOT rewrite the docs; this is consultation. Also flag any *additional* contradiction you notice inside F003 spec/design/tasks that the 22 findings missed (only if it is a correctness/blocking-class issue; ignore style).

MY PLANNED RESOLUTIONS

1. F003-D001 (factor_id): design:105 becomes `factor_id = <generator>_<definition_digest[:12]>`, run_seq removed; run attribution carried by existing `run_id` field; spec DR-002 states factor_id is content-addressed and contains no run ordinal; AC-009 asserts identical factor_id set across reruns.

2. F003-D002 (terminal facts): instead of adding separate rejection.json/failure.json, keep ONE `run.json` as the sole run-fact artifact (design:81 already says 运行事实 = run.json) and make it the terminal manifest for all three terminal states COMPLETED / REJECTED / FAILED, always written last via tmp+fsync+rename; delete design:190's "非受控异常…run.json 不写出" and design:206's "原因入日志" only. If the terminal manifest write itself fails, the run dir is treated as incomplete (fail-safe). AC-003/AC-011 assert REJECTED terminal run.json exists with reason.

3. F003-D003 (tier ladder): 2-day time-box yields only {L0 locked, L1 downgrade}; L1→L2 requires L1 连续 2 周 per ADR-0001 and is explicitly out of the smoke scope. spec:43/213/272-275 + FR-006 + AC-007 + design:222 synced. Also the "四条判据" wording in US-002 (spec:74) is numerically wrong (ADR-0001 has 3 L1 criteria); change to "L1 三条判据".

4. F003-D004 (ADR-0001 M2 smoke obligations): F003 commits only to (i) generation-side per-level counts (proposed / each reject reason code / registered) recorded from day 1 into run.json + generation.* events = funnel level 1, and (ii) reward-frequency spot check (turnover penalty / ≥30 trades-90d) recorded into the day's smoke manifest. The downstream funnel levels stay owned by F007 (already in tasks §5 明确后移). So FR-006 + AC-007 + tasks T018/T032 gain these two obligations, worded as level-1 scope rather than the full ADR funnel.

5. F003-D005 (explicit_tuples): the transitional binding mirrors ResearchSnapshot semantics field-for-field: {mode:"explicit_tuples", cutoff_time, members:[{dataset,data_version,value_digest,as_of_fidelity,event_time_min,event_time_max}], symbol_map_digest, universe_calendar_digest}; only the experiment_store artifact is absent. Switching to research_snapshot_id later is a pure identity swap.

6. F003-D007 (egress): keep the process-level guard, downgrade the claim honestly. NFR-004/AC-011/spec:122/design:208 now say: generation runs execute behind a process-level egress guard (socket constructors replaced, only AF_UNIX allowed) and a write-path whitelist limited to reports/generation/<run_id>/; this is NOT kernel-level network isolation (no netns/container in this feature, recorded). No absolute "runs with no network egress" claim.

7. F003-D008 (SIGTERM): SIGTERM → `status=partial` + `termination=early`, terminal run.json written, and NO `generation.run_completed` event; only a complete atomic run writes `status=completed` + run_completed. TR-001 restricted to completed runs. spec §5 gains RUNNING→PARTIAL.

8. F003-D009 (after-cost objective): FR-005/design objective.py/GenerationRun.objective gain cost-after-return (`cost_model` reference + `min_after_cost_return`), with a new decision-table row stating F003 does *pre-filtering* with configurable cost params (taker/maker/zero-cost, params recorded) and never adjudicates cost (that stays F007 / ADR-0003); F007's cost_model_version is the eventual truth source.

9. F003-D010 (pool): pool.json becomes an executable `FactorDef` (generator="pool", scope="cross_sectional") whose compute recomputes from member FactorDefs + weights; `AlphaPoolDef` is demoted to an internal member description embedded in that FactorDef's params/meta (no longer a separate top-level persisted object); DR-004 reworded accordingly; AC-008 asserts load-then-recompute.

10. F003-D011/D012 (new gates): I plan to add (a) a `[TEST]` group requirement in tools/validate_spec_lifecycle.py and (b) a task-DAG checker tools/check_task_dag.py, but BOTH scoped to features whose spec status ∈ {ready-for-development, in-progress, review, done} — because every other existing feature (F001/F002/F004/F007/F008) lacks a [TEST] group and F002/F007/F008 have backward/absent edges, so a repo-wide gate would break them. F003 is draft, so these gates are inert *now* and only fire at the T3 transition. Question: is status-scoped gating the right call here, or would you gate differently (e.g. require the group unconditionally and retro-fix other features)? Consider the cost of breaking F004 which is `done`.

RETURN
A short verdict per numbered item: OK / CHANGE(what) / RISK(why), plus a list of any additional blocking contradictions found. Be concise — this feeds a fix, not a report.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T14:59:34Z

- **tool**: `skill({"name": "review-convergence", "user_message": "Validate planned resolutions for documentation review findings F003 in /home/georg/projects/alphamill. Read CURRENT-doc.md and upstream truth sources, then critique items 1-10 with concise verdicts and identify additional blocking contradictions. Consultation only; do not edit docs."})`


> [reasoning] **Planning documentation review and codegraph inspection**

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

## assistant · 2026-09-16T15:00:23Z

- **tool**: `codegraph_codegraph_explore({"query": "F003 alphagen-vendor spec.md design.md tasks.md docs/decisions/0001-factor-mining-engine.md docs/decisions/0007-research-snapshot-binding.md docs/alphamill-prd.md docs/alphamill-architecture.md F007-evaluation-gates F008-universe-expansion CURRENT-doc.md", "maxFiles": 12, "projectPath": "/home/georg/projects/alphamill"})`


> [reasoning] **Planning codegraph inspection and query**

  <details><summary>tool output</summary>

  ```text
**Exploration: F003 alphagen-vendor spec.md design.md tasks.md docs/decisions/0001-factor-mining-engine.md docs/decisions/0007-research-snapshot-binding.md docs/alphamill-prd.md docs/alphamill-architecture.md F007-evaluation-gates F008-universe-expansion CURRENT-doc.md**

Found 7 symbols across 3 files.

**Blast radius — what depends on these (update/verify before editing)**

- `DecisionArtifact` (ml4t-zh/case_studies/research/decisions.py:167) — 11 callers in `ml4t-zh/case_studies/cme_futures/research_workflow.py`, `ml4t-zh/case_studies/crypto_perps_funding/research_workflow.py`, `ml4t-zh/case_studies/research/__init__.py`, `ml4t-zh/case_studies/research/execution.py` +3 more; tests: `ml4t-zh/tests/test_cme_futures_research.py`, `ml4t-zh/tests/test_research_contract_execution.py`, `ml4t-z
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:00:47Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `bash({"command": "git branch --show-current && git rev-parse --short HEAD && git status --short", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] **Planning parallel source reads**

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
main
11eeb96


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:01:00Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 145, "limit": 35})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 245, "limit": 45})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 380, "limit": 35})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md", "offset": 1, "limit": 100})`


> [reasoning] **Planning upstream docs review**
基线已确认：`main@11eeb96`，工作树干净。当前 F003 已有部分拟修复内容落在文档中（例如 D001、D005、D007），我正在对照 ADR/架构和 F007/F008 的双向契约，重点找“表面修复但仍可被另一条现行条款推翻”的情况。

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
245: - `HypothesisDef` 拥有经济动机、来源、generation、数据依赖、预期持有期和成本敏感性；
246: - `FactorDef` 拥有可执行定义和版本，不承载评测结论；
247: - `PortfolioDef` 拥有成员、权重、估计窗口、约束和组合门报告；
248: - `ExperimentRun` 拥有显式 execution tier、cohort、冻结规则和内容寻址 ID；
249: - `DeploymentRun` 固定引用 portfolio、信号缓存和审批版本；
250: - `RunRecord` 保存 intended/attempted/accepted/failed 四桶及执行事实；
251: - `AttributionReport` 区分事实、推断与建议，经规则或人审才触发生命周期/新假设动作；
252: - `ExperimentManifest` 是各对象和所有证据之间的不可变索引，不把结果复制回定义对象。
253: 
254: ### 4.1 因子定义（FactorDef）
255: 
256: ```python
257: @dataclass(frozen=True)
258: class FactorDef:
259:     factor_id: str            # 如 "alphagen_gen042_f003"
260:     hypothesis_id: str        # 指向 HypothesisDef；自动公式可指向 mechanism_unknown 假设
26
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
380: 
381: 三条补充规则（与集成文档 §3.2 无前视对齐规则配套）：
382: 
383: 1. **缓存键带版本维度**：缓存键 = (portfolio_or_factor_id, research_snapshot_id, code_version,
384:    params_hash, pair)，不是仅 timestamp+pair。任一输入 dataset 修订或代码/参数变化后写新版本目录，旧版本
385:    只读不覆盖。
386: 2. **混合频率陈旧策略**（4h 因子进 1h 决策）：merge_asof（backward）对齐后允许前向填充，但仅在最大陈旧度界内——因子值有效至下一个因子 K 线收盘，硬过期 = N 根决策 K 线（默认 N = 1 个因子周期，4h→1h 即 N=4）。越过界的行 `signal_value` 写 NaN（no-signal 语义），**不得当旧信号继续使用**；`stale` 列记录该行相对因子 K 线收盘的滞后根数，供审计核对。
387: 3. **审计覆盖 join 步骤**：无前视审计的范围显式包含 merge/join 步骤本身，不只因子计算——逐 K 线重放时对每个决策 bar 校验（信号时间戳 ≤ t 收盘）∧（陈旧度 ≤ 界），两项任一不满足即审计失败。
388: 
389: ### 4.4 DatasetVersion manifest
390: 
391: ```json
392: {
393:   "dataset": "ohlcv_1m",
394:   "source"
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
23: ALLO
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

## assistant · 2026-09-16T15:01:21Z

- **tool**: `codegraph_codegraph_explore({"query": "FactorDef PortfolioDef meta-factor AlphaPoolDef pool.json GenerationResult GenerationRun F003 contradictions", "projectPath": "/home/georg/projects/alphamill", "maxFiles": 8})`


> [reasoning] **Assessing run manifest handling**

> [reasoning] **Clarifying factor obligation divisions**

> [reasoning] **Noting task dependencies and scope**

> [reasoning] **Assessing schema_version inclusion**

> [reasoning] **Clarifying artifact references and binding semantics**

> [reasoning] **Updating process-level guard wording**

> [reasoning] **Clarifying NFR security claims and partial statuses**

> [reasoning] **Defining cost model roles and prefilter limits**

> [reasoning] **Planning pool factor ID and recompute contract**

> [reasoning] **Planning GenerationResult redesign**

  <details><summary>tool output</summary>

  ```text
**Exploration: FactorDef PortfolioDef meta-factor AlphaPoolDef pool.json GenerationResult GenerationRun F003 contradictions**

Found 58 symbols across 2 files.

**Blast radius — what depends on these (update/verify before editing)**

- `FactorialRunParameters` (MarketGameSim/src/market_game_sim/experiment/factorial.py:84) — 1 caller in `MarketGameSim/src/market_game_sim/experiment/factorial.py`; ⚠️ no covering tests found
- `parseJson` (deepseek-harness/packages/session/session-persistence-jsonl/src/generation.ts:293) — 2 callers in `deepseek-harness/packages/session/session-persistence-jsonl/src/generation.ts`; ⚠️ no covering tests found
- `JsonlGenerationRuntime` (deepseek-harness/packages/session/session-persistence-jsonl/src/generation.ts:201) — 3 callers in `deepseek-harness/packages/
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:02:10Z


> [reasoning] **Assessing ADR funnel ownership contradictions**

> [reasoning] **Clarifying cross-feature handoffs and cost model tracking**

> [reasoning] **Verifying terminal status handling and manifest distinctions**

> [reasoning] **Clarifying smoke scope and criteria**

> [reasoning] **Reconciling generator design and API contracts**

> [reasoning] **Validating pool factor ID exclusion**

> [reasoning] **Clarifying task status checks scope**

> [reasoning] **Assessing F003 contradictions and status gating**

> [reasoning] **Identifying GenerationResult API conflict**

> [reasoning] **Clarifying partial candidate registration conflicts**

> [reasoning] **Defining failure semantics and factor visibility**

> [reasoning] **Assessing F007 funnel ownership and run attribution**

> [reasoning] **Validating run_id usage and status gating**

> [reasoning] **Planning status gating excluding done to prevent breakage**
1. **OK** — Matches F003’s current DR-002/AC-009 and design identity rule: `spec.md:239-240,305`, `design.md:104-106`.

2. **OK, with one clarification** — A single terminal `run.json` is simpler and preserves fail-safe publication. Define that `REJECTED`, `FAILED`, and `PARTIAL` all include `status`, `termination`, `reason`, timestamps, and that consumers ignore factor files unless terminal status is explicitly consumable. This resolves the current contradiction at `design.md:95-99,183-193,209-210`.

3. **CHANGE** — Correct direction, but remove all remaining “二元裁决 = L0/L1/L2” wording. ADR-0001 permits only L0→L1 in this time-box; L1→L2 requires either two consecutive weeks of `<50` candidates or zero no-lookahead passes: `0001-factor-mining-engine.md:40-50`. Also update `spec.md:43,106,213,272-275`, not only the cited lines.

4. **RISK** — This still leaves D004 substantially true. ADR-0001 requires the full funnel to be recorded from day one, not merely generation-side counts: `0001-factor-mining-engine.md:52-62`. F003 may own only level 1, but the smoke manifest must explicitly record downstream levels as F007-owned, with a concrete F003→F007 handoff/contract and “not yet available” semantics. Otherwise the planned resolution proves only one of the two obligations.

5. **CHANGE** — The field set is incomplete. ADR-0007 also requires `schema_version` and immutable `provenance` references, and its `members` contract is semantically a dataset-keyed mapping: `0007-research-snapshot-binding.md:27-50`. “Pure identity swap” is too strong: later migration must construct/persist a ResearchSnapshot and replace the duplicated binding with `research_snapshot_id`, consistent with canonical rules at `0007:51-60`. Current F003 clauses are otherwise aligned at `spec.md:112,239,329` and `design.md:114-117`.

6. **OK** — This accurately narrows the claim and matches the current design’s own caveat that the guard is process-level, not kernel-level: `spec.md:260`, `design.md:209-213,243`. Preserve the separate write-whitelist and fail-closed claims; do not describe socket monkeypatching as complete network isolation.

7. **OK, with synchronization required** — The state transition and event rule are correct: `spec.md:265-270`, `design.md:187-194`. Update every occurrence of “run ends ⇒ `generation.run_completed`”, including `spec.md:246` and the AC/design mapping, so `PARTIAL` cannot still satisfy TR-001.

8. **CHANGE** — Add the cost model reference/version and after-cost objective fields, but explicitly state that F003’s result is a screening signal, never a cost verdict. PRD FR2.3 requires cost-after-return consideration: `alphamill-prd.md:157-158`; F007 owns the adjudicated three-tier cost result and `cost_model_version`: `F007/spec.md:173-182`. Also remove or qualify the current “不做成本门” wording at `spec.md:47,111` so it does not contradict the new pre-filter.

9. **CHANGE** — The persistence direction is right, but the resolution must also update the API contract: `design.md:137-142` still returns `AlphaPoolDef`, and `design.md:119` still defines it as a top-level persisted object. Define the executable pool FactorDef’s persisted member references/weights and deterministic load-time `compute` reconstruction, matching architecture’s callable FactorDef contract: `alphamill-architecture.md:254-270`.

10. **CHANGE** — Status-scoped gating is correct; unconditional retro-fixing would unnecessarily break existing features. However, do **not** include `done` in the newly enforced set, because that immediately breaks the stated `done` feature F004. Gate `ready-for-development`, `in-progress`, and `review`; treat `done` as grandfathered unless its docs are changed, or add an explicit migration/legacy exception. `validate_spec_lifecycle.py:214-246` already demonstrates the repository’s status-scoped pattern.

**Additional blocking contradiction**

- `design.md:193` currently says SIGTERM exports candidates and writes `status=completed`, while `design.md:209-210` says failed/incomplete runs’ candidates are not registered. After adopting `PARTIAL`, specify whether partial factor files are quarantined/ignored and whether `pool.json` is omitted. Otherwise downstream readers can consume factor files from a non-completed run despite the new terminal-manifest rule. Evidence: `design.md:94-99,183-193,209-210`; related lifecycle contract: `spec.md:265-284`.
