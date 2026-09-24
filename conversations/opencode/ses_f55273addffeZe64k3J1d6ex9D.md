---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f55273addffeZe64k3J1d6ex9D"
title: "Draft F007 review report (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T15:32:08Z"
updated_at: "2026-09-16T15:35:08Z"
tokens_input: 124214
tokens_output: 16277
cost: 0.0415
parent_id: "ses_f55324142ffefNy2o4qhiYalh0"
---

# Draft F007 review report (@Sisyphus-Junior subagent)

## user · 2026-09-16T15:32:08Z

TASK: Create the first-round full-scan F007 document review at /home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md.
EXPECTED OUTCOME: One complete Chinese review report following review-convergence exactly: valid YAML frontmatter, `report_type: doc-review`, `feature: F007`, `round: 1`, date 2026-09-16, `prior_report: none`, `scope: full-scan`, `stop_condition_met: false`, accurate severity counts, complete issue objects, conclusion-first body, baseline/scope, bounded checklist/evidence, exactly one unified 13-column Chinese findings table, adjudication section, and next steps. Every finding must be traceable to exact file:line evidence and have a concrete suggested fix plus a prefixed regression_test (`proposed:`, `existing:`, or `manual-review-only:`).
REQUIRED TOOLS: Read files needed for exact citations, then apply_patch only for the new target file. Do not use git writes or modify any other file.
MUST DO:
- Baseline: `main@ab30da9`, worktree clean before report; date 2026-09-16.
- Explain filename deviation: docs/reviews/CURRENT-doc.md is an active open F003 loop, so parallel report uses CURRENT-doc-F007.md; both ignored by `.gitignore:39`.
- Preserve CURRENT-doc.md untouched.
- Use stable IDs F007-D001 onward. Keep all Round-1 statuses `open`; empty fix_summary/resolved_round/tracked_task/disposition_reason.
- Consolidate duplicates and include these independently verified substantive findings:
  1) High test-coverage/process-gap: missing mandatory `[TEST]` journey group despite design.md:16-18; tasks.md:54-62.
  2) High correctness/spec-drift: F003 upstream is present in spec but omitted in design/tasks related_features and its generation events/operator registry have no complete synthesis/design/task ingestion path; spec.md:7,22; design.md:5,52; tasks.md:5; F003 spec.md:251-258,328-330.
  3) High correctness/cross-feature drift: F008 omitted from F007 related_features/upstream although F008 explicitly produces universe artifact consumed by ResearchSnapshot; F007 spec.md:7,198,212; F008 spec.md:7,243-244,313,326.
  4) High correctness/cross-feature drift: F007 conflates universe and calendar into one JSON at design.md:145,157-159,193 while F008 defines universe CSV artifact + universe_at(T), and F008 tasks.md:90 explicitly leaves calendar artifact to F007/later; require separate ownership/artifacts.
  5) High correctness/spec-drift: PRD FR3.6/SOP three-layer no-lookahead requires AST purity + independent per-bar replay + signal-cache alignment, but F007 covers methodology guard only and does not explicitly assign remaining layers; PRD:181-183; SOP:22-24; F007 spec:137-147,108-111; design:206-209.
  6) High correctness/spec-drift: sample-size three-tier contract missing (30-69 temporary PASS/reduced paper; >=69 credible); F007 collapses insufficiency and has no conditional verdict; PRD:179-180; ADR-0003:22-24,63-71; F007 design:124-126,222-223; tasks:T010.
  7) High correctness/task DAG: T012 cohort finalize computes BH-FDR/DSR but dependency graph lacks T009->T012; T013 lacks T012->T013; tasks.md:41,44-45,67.
  8) High correctness/task DAG: full-chain controls T016 need registry/synthesis, but graph lacks T012/T014->T016; T010/T011 consume T007 stage model without T007 edges; tasks.md:36,42-43,49,51,68-69.
  9) High test-coverage/gate-without-teeth: real-environment evidence task T022 reuses same fixture test as T016, no distinct immutable crypto snapshot/integration command; spec.md:275; tasks.md:51,60; SOP:64-75.
  10) High correctness/gate-without-teeth: holdout budget is asserted zero-change but no budget ledger/entity/append-only contract exists in DR/design/tasks; spec.md:40,55,128-135,201,259; ADR-0003:42-56.
  11) Medium correctness: verdict vocabulary conflicts: spec uses promising/dead/UNDERPOWERED; design stage enum PASS/FAIL/... and promotion_verdict; freeze layered enums.
  12) Medium test-coverage: SC-002 concurrency/fault injection for claim/registration/finalize is not owned by a task/test.
  13) Medium test-coverage: AC-003 denominator needs multi-member batch test, not isolated controls.
  14) Medium correctness: NFR-004 preview approximation has no design/task/AC coverage.
  15) Medium test-coverage: mutation targets/AC labels inconsistent; T017 targets more than T021 declares, no kill artifact/tooling.
  16) Medium correctness: second-implementation spot-check decision has no task.
  17) Medium correctness: F004 real Kronos source is not routed; F007 dependency ignores placeholder limitation, so controls could consume placeholder signals.
  18) Medium correctness: F005 is allowed to read files directly, weakening ADR-0005 unified read-only API boundary.
  19) Medium correctness: permanent final-confirmation-window stats are not explicitly excluded from Agent-readable report/manifest/synthesis.
  20) Medium test-coverage: design test map omits several tests used in tasks (`upstream_contracts`, `canonical_registry`, `artifact_schemas`, `controls`, `gate_mutations`).
  21) Medium correctness: five stage IDs and failure dimensions are not frozen; tasks says three dimensions without schema.
  22) Medium correctness: NFR-005 path portability and UX-001 CLI first-screen have no complete task/AC traceability.
  23) Low quality: design embeds procedural tasks.md action directive, despite design responsibility rule.
  24) Low correctness: state vocabulary and canonical=`bench` mapping/event registration are not fully mirrored across spec/design.
  25) Low test-coverage: T005 marked [P] but T004 is not; property-test strategy lacks explicit execution/tool task.
- You may merge #22/#24/#25 internally only if no evidence is lost, but do not omit substantive concerns. Severity counts must exactly match final issue list.
- State explicit passes: required section structures, frontmatter/status ownership, Q/DQ closed, AC IDs/references valid for draft, active indexes consistent, identity and ResearchSnapshot contracts aligned, fail-closed and AI authority aligned.
- Note existing active F003-D014 appears partially addressed by F007 spec but not design/tasks; do not modify or adjudicate F003 report.
- Use inline-code file paths rather than Markdown links so check_doc_links has no new risk.
MUST NOT DO: Do not edit F007 docs, CURRENT-doc.md, RETROSPECTIVE.md, FIX-log.md, or any source/config. Do not commit/push. Do not claim gates have run yet. Do not close the review or mark findings fixed/tracked/rejected.
CONTEXT: This is document review, not code review. The parent independently reviewed all source documents and will validate the report and run gates afterward.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T15:32:08Z

- **tool**: `bash({"command": "git rev-parse --short HEAD && git status --porcelain && echo \"---BRANCH---\" && git branch --show-current", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "ls -la docs/reviews/ 2>/dev/null; echo \"---\"; ls docs/features/ 2>/dev/null", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Let me start by understanding the task. I need to create a document review report for F007 following the review-convergence protocol. Let me first read the necessary files to gather exact citations.

Let me explore the repository structure and the relevant docs.

Let me start by reading the key files:
- docs/reviews/CURRENT-doc.md (F003 active loop)
- F007 spec/design/tasks
- F008 spec
- F003 spec
- PRD, SOP, ADR-0003, ADR-0005, etc.

Let me find the files first.
I'll start by exploring the repository structure and the key documents needed for exact citations.

  <details><summary>tool output</summary>

  ```text
ab30da9
---BRANCH---
main


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 160
drwxr-xr-x 2 georg georg   4096 Sep 16 22:04 .
drwxr-xr-x 7 georg georg   4096 Sep 15 01:58 ..
-rw-r--r-- 1 georg georg  35300 Sep 16 22:26 CURRENT-doc.md
-rw-r--r-- 1 georg georg 117606 Sep 16 02:11 RETROSPECTIVE.md
---
0.1
0.2
README.md
TEMPLATE
releases


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:32:12Z

- **tool**: `bash({"command": "find docs -type d | head -80; echo \"=== F007 ===\"; find docs -iname '*F007*' -o -path '*F007*' | head -50", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "grep -n \"docs/reviews\" .gitignore; echo \"---\"; sed -n '30,45p' .gitignore", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Worktree is clean, HEAD ab30da9, branch main. Good baseline.

Let me find F007 docs. Let me look at docs/features/0.1 and 0.2.
Baseline confirmed: `main@ab30da9`, worktree clean. Now locating F007 docs.

  <details><summary>tool output</summary>

  ```text
docs
docs/reviews
docs/decisions
docs/design
docs/design/ui-mockup
docs/research
docs/features
docs/features/0.2
docs/features/0.2/F003-alphagen-vendor
docs/features/0.2/F007-evaluation-gates
docs/features/0.2/F002-data-bridge
docs/features/0.2/F008-universe-expansion
docs/features/0.2/F004-kronos-inference-runtime
docs/features/0.1
docs/features/0.1/F001-quant-crypto-migration
docs/features/releases
docs/features/TEMPLATE
=== F007 ===
docs/features/0.2/F007-evaluation-gates
docs/features/0.2/F007-evaluation-gates/spec.md
docs/features/0.2/F007-evaluation-gates/tasks.md
docs/features/0.2/F007-evaluation-gates/design.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
39:docs/reviews/*
41:!docs/reviews/RETROSPECTIVE.md
---
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
!docs/reviews/RETROSPECTIVE.md

# 本地运行时密钥（模板为 deployment/.env.example，真实凭据人工搬运不进 git）
deployment/.env



Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:32:15Z

- **tool**: `bash({"command": "wc -l docs/features/0.2/F007-evaluation-gates/spec.md docs/features/0.2/F007-evaluation-gates/design.md docs/features/0.2/F007-evaluation-gates/tasks.md docs/features/0.2/F003-alphagen-vendor/spec.md docs/features/0.2/F008-universe-expansion/spec.md docs/features/0.2/F008-universe-expansion/tasks.md docs/features/0.2/F002-data-bridge/spec.md 2>/dev/null; echo \"===\"; find docs -iname '*PRD*' -o -iname '*SOP*' -o -path '*decisions*' -name '*.md' | head -40", "workdir": "/home/georg/
…[truncated])`
- **tool**: `bash({"command": "ls -R docs/decisions docs/design 2>/dev/null | head -60; echo \"=== root docs ===\"; ls docs/*.md 2>/dev/null", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Confirmed: `.gitignore:39` is `docs/reviews/*`, with line 41 exception for RETROSPECTIVE.md. So CURRENT-doc-F007.md will be ignored too. Good.

Now let me read all the F007 docs, plus relevant references (F003, F008, PRD, SOP, ADRs). These are large files. Let me read them.

Let me set up a todo list first since this is multi-step.

Actually, let me read the docs first to gather evidence. Let me read F007 spec, design, tasks in full.

  <details><summary>tool output</summary>

  ```text
294 docs/features/0.2/F007-evaluation-gates/spec.md
   261 docs/features/0.2/F007-evaluation-gates/design.md
    77 docs/features/0.2/F007-evaluation-gates/tasks.md
   354 docs/features/0.2/F003-alphagen-vendor/spec.md
   338 docs/features/0.2/F008-universe-expansion/spec.md
    91 docs/features/0.2/F008-universe-expansion/tasks.md
   296 docs/features/0.2/F002-data-bridge/spec.md
  1711 total
===
docs/SOP.md
docs/alphamill-prd.md
docs/decisions/000-template.md
docs/decisions/0003-validation-gate-non-degradation.md
docs/decisions/0008-north-star-sustained-profitability.md
docs/decisions/0007-research-snapshot-binding.md
docs/decisions/0002-external-dependency-policy.md
docs/decisions/0004-portfolio-construction.md
docs/decisions/0005-presentation-observability.md
docs/decisions/0006-eviden
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
docs/decisions:
000-template.md
0001-factor-mining-engine.md
0002-external-dependency-policy.md
0003-validation-gate-non-degradation.md
0004-portfolio-construction.md
0005-presentation-observability.md
0006-evidence-boundary-and-experiment-identity.md
0007-research-snapshot-binding.md
0008-north-star-sustained-profitability.md

docs/design:
ui-mockup

docs/design/ui-mockup:
README.md
app.js
index.html
styles.css
=== root docs ===
docs/README.md
docs/SOP.md
docs/alphamill-architecture.md
docs/alphamill-integration.md
docs/alphamill-prd.md
docs/alphamill-research-factor-mining.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:32:21Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`


> [reasoning] Now let me read the F007 docs, F003 spec, F008 spec/tasks, PRD, SOP, ADR-0003, ADR-0005. Let me read them all. I'll read F007 spec, design, tasks fully first.

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

## assistant · 2026-09-16T15:32:24Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md"})`


> [reasoning] Now let me read F007 tasks.md, F003 spec, F008 spec/tasks.

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

## assistant · 2026-09-16T15:32:27Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "offset": 240, "limit": 100})`


> [reasoning] Now let me read F003 spec (relevant sections), F008 tasks, PRD (FR3.6, sample-size, etc.), SOP, ADR-0003, ADR-0005.

The task says specific lines:
- design.md:16-18 (the dev preconstraint about [TEST] group) — I've seen it.
- tasks.md:54-62 (validation & acceptance tasks) — seen.
- spec.md:7,22; design.md:5,52; tasks.md:5 — F003 upstream.
- F003 spec.md:251-258,328-330.
- F008 spec.md:7,243-244,313,326.
- F007 spec.md:7,198,212.
- design.md:145,157-159,193.
- F008 tasks.md:90.
- PRD:181-183; SOP:22-24; F007 spec:137-147,108-111; design:206-209.
- PRD:179-180; ADR-0003:22-24,63-71; F007 design:124-126,222-223; tasks:T010.
- tasks.md:41,44-45,67.
- tasks.md:36,42-43,49,51,68-69.
- spec.md:275; tasks.md:51,60; SOP:64-75.
- spec.md:40,55,128-135,201,259; ADR-0003:42-56.

Let me read F003 spec, F008 tasks, PRD relevant sections, SOP, ADR-0003, ADR-0005.

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

## assistant · 2026-09-16T15:32:32Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 40})`
- **tool**: `bash({"command": "ls docs/features/0.2/F003-alphagen-vendor/ docs/features/0.2/F008-universe-expansion/ docs/features/0.2/F004-kronos-inference-runtime/ docs/features/0.2/F002-data-bridge/ 2>/dev/null; echo \"=== BACKLOG ===\"; cat BACKLOG.md 2>/dev/null; echo \"=== CLAUDE ===\"; cat CLAUDE.md 2>/dev/null | head -60", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now let me read F003 spec frontmatter (lines 1-30) and F008 spec lines noted. Also need F003 tasks (for cross-feature drift about generation events ingestion path). Let me read PRD relevant sections, SOP, ADR-0003, ADR-0005, and F003 tasks.

The task mentions F007 spec.md:7,22; design.md:5,52; tasks.md:5. F003 spec.md:251-258,328-330.

Let me read F003 spec top (1-30) and its tasks.md. Also F008 design? Probably exists. Let me check.

Also need to read the F003 CURRENT-doc.md to understand the active loop and F003-D014 context. And check BACKLOG.md, CLAUDE.md.

Let me read several things in parallel.

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
docs/features/0.2/F002-data-bridge/:
design.md
spec.md
tasks.md

docs/features/0.2/F003-alphagen-vendor/:
design.md
spec.md
tasks.md

docs/features/0.2/F004-kronos-inference-runtime/:
design.md
spec.md
tasks.md

docs/features/0.2/F008-universe-expansion/:
design.md
spec.md
tasks.md
=== BACKLOG ===
# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F003-alphagen-vendor | 0.2 | draft | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
| F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
| F008-universe-expansion | 0.2 | draft | [spec](docs/features/0.2/F008-universe-expansion/spec.md) |

> 规则：
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:32:36Z

- **tool**: `bash({"command": "sed -n '1,40p' docs/decisions/0003-validation-gate-non-degradation.md; echo \"===== 40-80 =====\"; sed -n '40,80p' docs/decisions/0003-validation-gate-non-degradation.md", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "sed -n '1,120p' docs/SOP.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now read PRD relevant lines: 179-183, 40, 55, 128-135, 201, 259 (F007 spec lines actually). Wait, finding #10 says spec.md:40,55,128-135,201,259 — that's F007 spec. And PRD:179-180, PRD:181-183. Let me read PRD around 170-200 and also sample-size sections. SOP:22-24, 64-75. ADR-0003:22-24, 42-56, 63-71. ADR-0005. Let me read.

  <details><summary>tool output</summary>

  ```text
# ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化

- 日期：2026-09-06
- 状态：Accepted
- 决策人：Georg
- 背景：quant-crypto 仓库 Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
  PRD G4 / FR3

## 背景

quant-crypto 的最终 90 天留出门连续拦下全部候选（低频 Ridge/HGB、regime 增强、成本感知、
衍生品 basis），看起来是"失败"，实际是验证协议在正确工作——它拦下的是会亏钱的东西。
真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
判定统计上不可信；regime filter 方向正确但 27 笔欠功效）。

该门禁的价值来自它**从不放水**。任何"先上盘再观察"的妥协都会摧毁整个系统的可信度。

## 决策

1. **证据门不降级**：FactorDef 在选择期筛选后先构建并冻结 PortfolioDef，再由完整组合依次
   通过最终 90 天留出和永久隔离最终确认；不得先看留出再组装策略，效率提升也不得来自放宽门禁。
2. **样本量门槛**：留出期 <30 笔输出 `UNDERPOWERED`（不判 PASS 也不判 FAIL），触发扩宇宙/
   延长窗口，而不是放行；30~69 笔最多临时 PASS（仅可缩减仓位进入 paper）；约 ≥69 笔才允许
   完整 FAIL/PASS 判定（分级口径见下文功效论证与 PRD FR3.5）。
3. **无前视是一等公民**：AST 纯度门（因子定义层）+ 独立逐 K 线重放审计（策略层）+
   信号缓存时间戳对齐检查（数据层），三层全部通过才算干净。

…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
---
topics: [sop, workflow]
doc_kind: note
created: 2026-09-06
updated: 2026-09-07
---

# 开发流程（AlphaMill）

本文是项目的**原则入口与质量门**唯一真源：汇总「项目不可违反原则」的短摘要与各自
唯一拥有者链接，规定开发纪律、验证流程、状态转换与复核协议。

## 0. 项目不可违反原则（入口）

以下原则是**阻断性**的：违反其中任何一条的规格/实现不得进入实现或收口阶段。规范
正文在各自的唯一拥有者中，本文只给摘要与入口。**每条原则的规范正文只放一个唯一
拥有者**，本文只写短摘要与链接，不重复 PRD、architecture、decisions 的完整定义。

| # | 原则 | 短摘要 | 规范正文唯一拥有者 |
|---|---|---|---|
| 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |
| 2 | 证据门不降级 | 候选按样本功效分级并经过留出与最终确认；效率提升不得来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |
| 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |
| 4 | 数据红线（只读湖快照） | 研究/回测只读 Parquet 湖不可变快照（data_version），不直读 TimescaleDB 修订态 | `docs/alphamill-architectu
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:32:40Z

- **tool**: `bash({"command": "sed -n '150,205p' docs/alphamill-prd.md", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "grep -n \"4.1.1\\|无前视\\|三层\\|AST\\|重放\\|信号缓存\" docs/SOP.md | head; echo \"=== ADR-0005 ===\"; sed -n '1,80p' docs/decisions/0005-presentation-observability.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now PRD lines 179-183, 40, 55, 128-135, 201, 259. Wait — the task says finding #5: PRD:181-183; SOP:22-24. finding #6: PRD:179-180. Let me read PRD around those. Also PRD FR3.6, FR3.5. Let me read PRD around 160-200 and search for FR3.6, sample sizes.

Also finding #10: spec.md:40,55,128-135,201,259; ADR-0003:42-56. Wait those spec.md lines are F007 spec lines. Let me re-check: "holdout budget is asserted zero-change but no budget ledger/entity/append-only contract exists in DR/design/tasks; spec.md:40,55,128-135,201,259". So:
- F007 spec.md:40 "preview 快速诊断但不能污染 canonical cohort、留出预算和 official population"
- spec.md:55 preview scenario
- spec.md:128-135 FR-001
- spec.md:201 DR-004
- spec.md:259 AC-001
Yes.

Now check: does F007 spec/design/tasks have any "budget ledger" entity? Search for 预算/ledger/budget. Let me grep.

Let me also read PRD target lines and ADR-0005. And check the F003 CURRENT-doc.md for F003-D014 context and the schema for the report (to match expected structure). And RETROSPECTIVE not needed.

Let me also verify F002 spec, F004 spec for finding #17/#18. Finding #17: F004 real Kronos source is not routed; F007 dependency ignores placeholder limitation. Need F004 spec lines. Finding #18: F005 allowed to read files directly, weakening ADR-0005. Need F005 spec? F005 is not in features/0.2? It's planned. Hmm, "F005 is allowed to read files directly" — where? Let me search F007 design for F005 read. design.md:217 "F005 通过只读 API/文件 reader 渲染". So "只读 API/文件 reader" includes direct file reader, weakening ADR-0005's unified read-only API boundary. Let me read ADR-0005 to confirm.

Let me batch searches.

  <details><summary>tool output</summary>

  ```text
### FR2 AI 因子工厂

- **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
  generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。
- **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
  生成器只产出 FactorDef/协同池定义，不拥有最终评测权。
- **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
  禁止只优化 RankIC。
- **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；前视、网络访问、隐式全样本统计和未支持的跨 pair
  算子直接拒绝，不得静默降级。
- **FR2.5 因子注册表**：保存定义、参数、数据依赖、来源、版本、评测摘要和生命周期；IC/OOS PnL
  高相关候选查重，`|ρ|>0.99` 拒绝，`0.90~0.99` 标记变体。
- **FR2.6 探索组合**：AlphaGen 协同池作为可部署 meta-factor 注册；名义产量、有效独立数、来源多样性
  与资源消耗并列记录，禁止只用公式数量汇报产能。

### FR3 证据评测与验证

- **FR3.1 统一评测台**：输入 FactorDef 或已冻结 PortfolioDef 和显式窗口。因子报告输出 RankIC、
  IC 衰减、分状态和分位数收益；组合报告输出收益风险、换手、容量、持有期和毛交易摘要。
  评测台不自行选择窗口或改变组合成员。
- **FR3.2 成本模型**：交易费、滑点、资金费率进入选择回路；taker/maker/零成本三档为标准输出，
  成本后收益不为正则 `dead`。参
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
23:| 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |
=== ADR-0005 ===
# ADR-0005：呈现与观测架构 —— 真相源/投影/展示三分与自建前端路线

- 日期：2026-09-13
- 状态：Accepted
- 决策人：Georg
- 背景：呈现层长期路线；PRD FR8 / FR6.1 / FR6.4 / FR7.2 / FR7.4；架构文档 §〇 / §七

## 背景

当前呈现面三件：Grafana（`quant-overview` 平台观测 + `dryrun-monitoring` 策略运营，F001
迁入并验收有数）、FreqUI（Freqtrade 镜像自带，`api_server` 已启用）、CLI（`tools/verify.py`
门禁与操作）。三个结构性问题随里程碑逼近：

1. **研究证据没有承载面**：评测台（FR3）落地后 M2 出口要求周产能 ≥100 候选，版本化报告
   靠文件浏览不可持续；架构文档 §五 原计划的「Grafana 实验台账看板」与版本态产物形态
   （文件 + 谱系图 + 逐因子下钻）不匹配。
2. **口径被困在看板里**：dashboard JSON 内嵌 SQL 会持续积累业务口径（成本后收益、胜率、
   延迟判定等），更换呈现工具即全部重写；且新旧两套实现并存期必然漂移——「哪个数字是
   真的」在量化系统中是不可接受的风险。
3. **工具边界不清**：FreqUI（执行显微镜）、Grafana（运营观测）、未来页面（研究证据）
   各自该看什么、数据从哪来、谁能写什么，无明文约定。

长期意图：项目若持续推进，**前台页面最
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:32:49Z

- **tool**: `bash({"command": "grep -n \"Kronos\\|kronos\\|占位\\|placeholder\\|上游\\|clone\\|真实\" docs/features/0.2/F004-kronos-inference-runtime/spec.md | head -40", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "grep -n \"F007\\|generation.run_completed\\|candidate_rejected\\|算子能力\\|registry\\|T035\\|≥30\\|30 对\\|漏斗\" docs/features/0.2/F003-alphagen-vendor/tasks.md | head -50", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "grep -n \"universe\\|calendar\\|artifact\\|CSV\\|csv\\|摘要\" docs/features/0.2/F008-universe-expansion/design.md | head -40; echo \"=== ADR-0007 ===\"; grep -n \"universe\\|calendar\\|artifact\\|摘要\" docs/decisions/0007-research-snapshot-binding.md | head -30", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now I have good evidence. Let me gather the remaining evidence:

- F004 spec (Kronos placeholder limitation, real source not routed).
- F003 tasks (for F003-D014, and generation events/operator registry ingestion path).
- F007 CURRENT-doc.md (F003-D014 context, and schema of report format).
- F002 spec (upstream contract) — for finding #24 canonical=bench mapping.
- ADR-0007 (ResearchSnapshot) for universe/calendar.
- F008 design (universe CSV artifact, universe_at).

Let me read F004 spec and F003 tasks, and CURRENT-doc.md (large 35KB, ~ maybe read fully). Also F008 design to confirm universe CSV.

Let me grep for key terms to be efficient. But task says every finding traceable to exact file:line. I already have many. Let me get:
- F004 spec: lines about Kronos source placeholder.
- F003 tasks: lines about generation events/operator registry, T035, F007 ingestion path.
- F007 CURRENT-doc.md: read to learn format and F003-D014.
- F008 design: universe artifact CSV + universe_at.
- ADR-0007: universe/calendar artifact.

Let me search.

  <details><summary>tool output</summary>

  ```text
8:topics: [kronos, inference, deployment]
14:# F004：Kronos 真实推理运行时（编排内可复现）
20:- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身
22:- **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）
26:- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）。
32:compose 的 `kronos-signal` 服务默认 `KRONOS_USE_REAL_MODEL=false`（镜像基于 `python:3.11-slim`，不含 torch，也不挂载 `vendor/Kronos` 与 `models/`）。真实推理只能靠人工在宿主 venv 起一个 8002 实例——F001 AC-006 因此是「留档命令」而非编排内证据；F002 导出的 `signals_log` 内容全是 `source=placeholder`。
36:- `docker compose -f deployment/docker-compose.y
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
5:related_features: [F001, F002, F007, F008]
52:- [ ] T016 (`FR-006`, `AC-007`): 实现冒烟闸门判据判定器、当日冒烟 manifest（含 ADR-0001 两条 M2 义务：生成侧逐级计数、下游级 `owner=F007`+`not_yet_available` 占位、奖励频率抽查）、档位状态机与降级裁决（L1→L0 回切须新 time-box 记录），并提供 `smoke` 的默认 config/window 构造 — verify: `tests/integration/test_f003_smoke_gate.py`
61:- [ ] T022 (`FR-005`, `AC-005`): 实现算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 窗口换算），并导出为 `F007` 可消费的版本化能力清单（含 `schema_version`；`F007` FR-002 的已登记算子能力消费源） — verify: `tests/unit/test_f003_operator_registry.py`
62:- [ ] T023 (`FR-005`, `TR-002`, `AC-005`): 实现生成侧 AST 自检与四类拒绝原因码（`unregistered_op` / `lookahead` / `reachability` / `duplicate_definition`）计数 — verify: `tests/unit/test_f003_operator_registry.py`
63:- [ ] T024 (`FR-005`, `AC-006`): 实现目标对齐——换手惩罚、≥30 笔/90 天可达性预筛与成本后收益预筛（按可配成本参数，只产预筛信号不产裁决），参数写
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
6:topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
24:- **ADR / 上游 Contract**：ADR-0007（ResearchSnapshot 绑定 universe/calendar artifact）、ADR-0003（门禁不降级）、ADR-0001（扩容是产出质量前提）；F002 的 `symbol_map` 内容寻址发布范式、dataset registry、manifest 与 reader 契约
28:  - **不改 `F002` 已冻结的语义**：导出、对账、manifest、修订与失效规则一律沿用，本 feature 只扩 pair 集合并新增元数据 artifact；
35:四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。发现从 Binance 公开行情按口径筛候选；人工确认后冻结为内容寻址的 `UniverseDef`；回填复用 F001 的 `historical_backfill.py`，外面套一层可续跑的批次编排；每个 pair 回填完成后跑质量门（复用 `tools/f001_backfill_report.py` 的口径，参数化到多 pair）；过门的 pair 写入联机库的 `universe_membership` 台账并进 F002 导出清单，台账再以 `symbol_map` 同构的方式发布为湖内内容寻址 artifact。
38:- 后端 / API：新增 `src/alphamill/data_bridge/universe/` 子包与 `alphamill-universe` CLI；`collector/historical_backfill.py` 由脚本升级为可被编排调用（同时解除其
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:32:55Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`


> [reasoning] The last line got cut: "universe/calendar artifact 由调用 F007" — let me read ADR-0007 lines 80-95. But I have enough.

Now, F004 spec is important for finding #17: "F004 real Kronos source is not routed; F007 dependency ignores placeholder limitation, so controls could consume placeholder signals." Need exact lines in F004 spec about placeholder and routing. I have:
- F004 spec:32: container default `KRONOS_USE_REAL_MODEL=false`, 真实推理 only manual, F002 exports `source=placeholder`.
- F004 spec:71: 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`; real instance wiring 由后续评估决定 (tasks §5).
- F004 spec:72: signals_log 内容自动升级不在本 feature。

So F007's dependency/controls might consume placeholder signals. Where does F007 mention F004? spec.md:22 mentions F004/Kronos FactorDef. design.md:24 ADR... F002. spec:279 upstream F002 only. Actually F007 spec.md:279 lists upstream F002 only (not F004). Hmm.

Let me get exact F004 line numbers and content. Let me read F004 spec lines 28-75 and check F004 tasks §5. Also I need F007 CURRENT-doc.md schema. Let me read it.

Let me read F007 CURRENT-doc.md fully (the F003 active loop) to understand format and F003-D014. It's 35KB ~ maybe 500 lines. Let me read.

Actually wait — the file is `docs/reviews/CURRENT-doc.md`. Task says it's an active F003 loop. I must not modify it. Let me read it.

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

## assistant · 2026-09-16T15:33:02Z

- **tool**: `bash({"command": "grep -n \"FR3.5\\|FR3.6\\|FR3.7\\|FR3.9\" docs/alphamill-prd.md; echo \"=== SOP real-env ===\"; grep -n \"真实环境测试纪律\\|ALPHAMILL_INTEGRATION\\|三层防线\\|无前视\" docs/SOP.md; echo \"=== ADR0003 ===\"; grep -n \"样本量\\|UNDERPOWERED\\|30~69\\|30-69\\|≥69\\|留出使用台账\\|append-only\\|永久隔离\\|周度访问预算\\|三层\\|AST\" docs/decisions/0003-validation-gate-non-degradation.md", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "echo \"=== design 预算/留出/ledger ===\"; grep -n \"预算\\|留出\\|holdout\\|ledger\\|台账\" docs/features/0.2/F007-evaluation-gates/design.md; echo \"=== tasks 预算/留出 ===\"; grep -n \"预算\\|留出\\|holdout\" docs/features/0.2/F007-evaluation-gates/tasks.md; echo \"=== design F003 events ===\"; grep -n \"generation\\|F003\\|算子\\|registry\\|漏斗\" docs/features/0.2/F007-evaluation-gates/design.md; echo \"=== spec sample size ===\"; grep -n \"样本\\|UNDERPOWERED\\|promising\\|dead\\|69\\|30\" docs/featur
…[truncated])`


> [reasoning] Now I have the exact format. Good. The F003 report used `location` with full paths but in the table just short. Also it noted machine gates run.

Task says "Do not claim gates have run yet." Hmm — actually MUST NOT DO says "Do not claim gates have run yet." So in my F007 report, I should NOT claim I ran tools/validate_spec_lifecycle.py etc. But "State explicit passes: required section structures, frontmatter/status ownership, Q/DQ closed, AC IDs/references valid for draft, active indexes consistent, identity and ResearchSnapshot contracts aligned, fail-closed and AI authority aligned." These passes are document-level inspections, not gate runs. So I should phrase them as manual document review passes, not as having run scripts. Actually wait, should I run the gates? The parent will validate and run gates afterward. MUST NOT DO: "Do not claim gates have run yet." So I should not run/claim tools/verify.py. I can state the structural passes based on manual inspection. Maybe I can run validate_spec_lifecycle to confirm? But task explicitly says parent will run gates afterward, and don't claim gates have run. So avoid running them. I'll phrase passes as "人工核对" and note that machine gates are to be run by parent.

Hmm, but note: the F003 report mentions it ran gates. My instructions say not to claim gates ran. Let me just not include a "machine gates" pass claim, or explicitly state "本轮未运行机器门禁（由复核方在收口前执行），以下为人工文档核对结论". That's safest.

Now let me figure out the baseline: task says `main@ab30da9`. Confirmed. Date 2026-09-16.

Now let me verify a few remaining evidence points and line numbers:

Finding #2: F003 upstream present in spec but omitted in design/tasks related_features and its generation events/operator registry have no complete synthesis/design/task ingestion path.
- F007 spec.md:7 `related_features: [F002, F003, F004]` — includes F003. ✅
- F007 spec.md:22 mentions F003 events & operator registry & pool. ✅
- F007 design.md:5 `related_features: [F002, F004]` — omits F003. ✅
- F007 tasks.md:5 `related_features: [F002, F004]` — omits F003. ✅
- F003 spec.md:251-258 (TR-001/TR-002 events), 328-330 (dependency: F007 consumes...). ✅
- Also design.md:24 lists ADR/upstream contract: only F002; design.md:52 SynthesisBuilder — no generation events. tasks've no task for ingesting generation.run_completed / candidate_rejected / operator registry / pool. Indeed tasks.md has T016 controls but no F003 event ingestion. The spec adds these to upstream contract (line 22) but no design/task. So finding #2 is strong.

Wait, but the task says "F003 upstream is present in spec but omitted in design/tasks related_features and its generation events/operator registry have no complete synthesis/design/task ingestion path". Need to verify no ingestion path. design.md:52 SynthesisBuilder only finalized canonical cohort. spec.md:22 says F003 events consumed for funnel first level. Is there a design for funnel ingestion? design doesn't mention generation.run_completed anywhere. Let me grep to confirm.

Finding #3: F008 omitted from F007 related_features/upstream. F007 spec.md:7 related_features [F002,F003,F004] — no F008. F007 spec.md:198 DR-001 says ResearchSnapshot persists universe/calendar summary. F007 spec.md:212 IR-002 says universe/calendar artifact. F008 spec.md:7 related_features includes F007. F008 spec.md:243-244 IR-002/IR-003 universe_at(T) + content-addressed artifact for F007. F008 spec.md:313 downstream consumers F007. F008 spec.md:326 decision artifact. ✅ Confirmed omission.

Finding #4: F007 conflates universe and calendar into one JSON at design.md:145,157-159,193 while F008 defines universe CSV artifact + universe_at(T), and F008 tasks.md:90 explicitly leaves calendar artifact to F007/later.
- design.md:145 `--universe-calendar <path>` single arg.
- design.md:157-159 builder saves `universe_calendars/<digest>.json`.
- design.md:193 "显式 universe/calendar JSON".
- F008 design.md:100 universe artifact CSV `lake/_metadata/universes/<digest>.csv`.
- F008 tasks.md:90 calendar artifact → F007 or later.
- ADR-0007:72-74 separates symbol-map artifact (CSV) from universe/calendar JSON. Hmm actually ADR-0007 says symbol-map artifact CSV; universe/calendar JSON saved by experiment_store. And ADR-0007:83 says "F002 提供 symbol-map artifact；universe/calendar artifact 由调用 F007" (cut off). Let me read that.
- F007 spec.md:198 DR-001 says "universe/calendar 摘要" — one summary.
- F007 spec.md:212 IR-002 "universe/calendar artifact".
So F007 treats universe+calendar as a single opaque JSON, while F008 owns universe as a separate content-addressed CSV with universe_at(T). Conflict: F007 requires universe artifact but has no ingestion of F008's CSV/digest/universe_at semantics; and calendar ownership is deferred to F007 by F008 tasks.md:90 but F007 doesn't define calendar artifact ownership. Good.

Finding #5: PRD FR3.6/SOP three-layer no-lookahead requires AST purity + independent per-bar replay + signal-cache alignment, but F007 covers methodology guard only and does not explicitly assign remaining layers.
- PRD:181-183 (FR3.6 无前视三层审计). Let me check exact lines. From the sed output, FR3.6 is at the line starting "- **FR3.6 无前视三层审计**". The sed range 150-205 printed. I need exact line numbers. Let me grep -n.
- SOP:22-24 (principle 3 table row).
- F007 spec:137-147 (FR-002 methodology guard), spec:108-111 (范围外: offline→decision-time parity, run_record, kill-switch → F006/M3). Hmm spec:108-111 is 范围外 listing parity etc. Actually let me check: lines 106-111 are 范围外. Yes 108-111: "- 离线到决策时 parity、run_record、kill-switch 与启动对账 → F006/M3". So F007 defers parity/replay to F006, but the three-layer no-lookahead includes signal-cache alignment which is a hard gate. And design:206-209 methodology gate guard. So finding: F007 only covers methodology guard (AST/embargo etc.) but the independent per-bar replay and signal-cache alignment layers aren't explicitly assigned. Actually F007 spec:110 assigns "离线到决策时 parity、run_record、kill-switch 与启动对账 → F006/M3" which might include replay, but signal cache alignment is a data-layer gate that PRD FR3.6 requires before promotion, and F007 is the promotion gate (canonical). So finding stands: F007 doesn't explicitly own/assign the other two layers, and defers to F006 yet F007 is where 晋级 happens.

Finding #6: sample-size three-tier contract missing.
- PRD:179-180 FR3.5: <30 UNDERPOWERED; 30~69 temporary PASS; ≥69 credible. Let me get exact lines.
- ADR-0003:22-24 decision 2; 63-71 efficacy argument (30~69 UNDERPOWERED band, temporary PASS, ≥69 credible). Let me get exact lines.
- F007 design:124-126 stage states PASS|FAIL|UNDERPOWERED|INCOMPLETE|NOT_APPLICABLE; 222-223 failure mapping: 证据不足 → UNDERPOWERED.
- F007 spec:173-182 FR-005; spec:118 "指标样本不足：输出 UNDERPOWERED"; tasks T010.
- So F007 collapses 30-69 into UNDERPOWERED and has no conditional/temporary PASS verdict. PRD FR3.5 says 30~69 = temporary PASS (缩减仓位 paper), <30 = UNDERPOWERED. F007 spec:118 says 样本不足→UNDERPOWERED generically. And F007 spec §3 边界场景 line 118. Also SC/AC. Let me confirm exact F007 spec lines mentioning sample size. grep.

Finding #7: T012 cohort finalize computes BH-FDR/DSR but dependency graph lacks T009->T012; T013 lacks T012->T013.
- tasks.md:41 T009 implements member HAC IC/block bootstrap + cohort BH-FDR, DSR, MinTRL.
- tasks.md:44 T012 implements frozen cohort, registration, finalize → official population projection. It computes finalize (BH-FDR etc.) — design.md:111 says finalize computes BH-FDR/DSR. So T012 needs T009.
- tasks.md:45 T013 canonical/finalize-cohort CLI.
- tasks.md:67 dependency: `T004,T005 -> T006,T011,T012,T013`. No T009->T012; no T012->T013. ✅
- tasks.md:68 `T008,T009,T010 -> T011,T016,T017` — T009→T011 but not T012. So T012 (finalize cohort computes cohort stats) lacks T009 edge. Confirmed.

Finding #8: full-chain controls T016 need registry/synthesis, but graph lacks T012/T014->T016; T010/T011 consume T007 stage model without T007 edges.
- tasks.md:36 T007 implements stage status model.
- tasks.md:42 T010 rolling split, sample-size verdict & stability report — consumes T007 stage model. tasks.md:43 T011 run events/report/manifest atomic publish — consumes T007 report schema.
- tasks.md:49 T014 synthesis builder.
- tasks.md:51 T016 run controls golden full chain.
- tasks.md:68-69 dependencies: `T008,T009,T010 -> T011,T016,T017`; `T011,T012 -> T014,T015`. No T012->T016, no T014->T016. And T007 has no out-edges to T010/T011. ✅
- Also T016 "全链记录拒绝者" needs synthesis/funnel & registry. tasks.md:51.

Finding #9: real-environment evidence task T022 reuses same fixture test as T016, no distinct immutable crypto snapshot/integration command.
- spec.md:275 真实环境验证：在本机不可变 crypto 快照运行两个正控制.
- tasks.md:51 T016 verify uses tests/integration/test_f007_controls.py.
- tasks.md:60 T022 verify uses same test file.
- SOP:64-75 (真实环境测试纪律). Actually SOP §3 lines. Let me get exact SOP lines for 真实环境测试纪律. From the read, it's in section 3, after review lifecycle. Let me grep line numbers.
- So T022 claims "在不可变 crypto fixture 跑" but verify command is identical to T016's fixture test — no distinct integration command (e.g. ALPHAMILL_INTEGRATION=1) or immutable snapshot artifact. Gate without teeth. ✅

Finding #10: holdout budget asserted zero-change but no budget ledger/entity/append-only contract.
- spec.md:40 "preview ... 不能污染 canonical cohort、留出预算和 official population".
- spec.md:55 US-001 "不消耗正式试验与留出预算".
- spec.md:128-135 FR-001 (preview cannot write 留出预算).
- spec.md:201 DR-004 CohortLedger (preview not in official population) — no holdout budget ledger.
- spec.md:259 AC-001 "正式台账与留出预算零变化".
- ADR-0003:42-56 holdout budget: weekly budget top-k, append-only 留出使用台账, 永久隔离最终确认窗. Let me get exact lines.
- design.md and tasks.md have no budget ledger entity/task. grep 预算/留出 in design/tasks.
- So F007 asserts zero-change but never defines the ledger to measure it. AC-001 has no regression test proving zero-change (well, design §8 maps AC-001 to execution tiers test). Still no budget entity. ✅

Finding #11: verdict vocabulary conflicts.
- spec uses promising/dead/UNDERPOWERED (spec:158 promising; spec:176 dead; spec:118 UNDERPOWERED; spec:182 dead; spec:243 PASS/promising).
- design stage enum PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE (design:124-126) and promotion_verdict (design:123-124), cohort_verdict.
- So there's no freeze of layered enums: e.g., spec uses `dead`, `promising` but design stage enum has PASS/FAIL only. Need design to define verdict vocabulary separately from stage states. ✅

Finding #12: SC-002 concurrency/fault injection for claim/registration/finalize not owned by a task/test.
- spec.md:253 SC-002 preview/canonical isolation, canonical idempotency & cohort finalize verified via concurrency/fault injection.
- design.md:201-204 claim/lease/recovery.
- tasks: T011 atomic publish; T012 registration/finalize; no concurrency test. design §8 maps AC-005 to atomic publish fault injection, but SC-002 concurrency not mapped. No task. ✅

Finding #13: AC-003 denominator needs multi-member batch test, not isolated controls.
- spec.md:261 AC-003.
- design §8 AC-003 → tests/unit/evaluation/test_required_statistics.py (unit; isolated estimators).
- T016 controls golden (tasks:51) — could be single member. No multi-member cohort batch test where rejected candidates all counted in denominator. review-convergence §5 batch scenario. ✅

Finding #14: NFR-004 preview approximation has no design/task/AC coverage.
- spec.md:225 NFR-004 preview 可采样/缩窗但必须显式标注近似.
- No AC references NFR-004. design doesn't mention approximation. tasks none. grep. ✅

Finding #15: mutation targets/AC labels inconsistent; T017 targets more than T021 declares, no kill artifact/tooling.
- tasks.md:52 T017 (FR-001, FR-002, NFR-003): future-fill, embargo, guard registry, preview writer, exception swallowing, publish integrity.
- tasks.md:59 T021 (AC-002, AC-005): run mutation and confirm each mutant killed — only AC-002/AC-005, but T017 covers FR-001 (preview writer) not AC-labeled. So labels inconsistent. Also no mutation tooling dependency pinned, no kill artifact. ✅
- design.md:247 "对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异" — 5 targets, T017 says 6. Minor.

Finding #16: second-implementation spot-check decision has no task.
- spec.md:290 决策：统计实现风险 自研最小协议 + 正/负控制 + 第二实现抽查.
- design.md:255 "第二实现只做对照".
- No task for second-implementation spot-check. ✅ (PRD FR3.7 too.)

Finding #17: F004 real Kronos source is not routed; F007 dependency ignores placeholder limitation.
- F004 spec:32 placeholder default; spec:71 consumer routing still to mock; spec:42/72 real signal only source.
- F007 spec:22 mentions F004/Kronos FactorDef; F007 spec:104 "funding carry、BTC/ETH 截面动量正控制" — positive controls. Controls are funding carry and BTC/ETH momentum, manual/crypto-native, not Kronos. Hmm. But F007 input to FactorDef includes F004/Kronos. The controls may use signals whose source is placeholder. Actually let's think: F007's upstream is "F004/Kronos 与人工因子产出的 FactorDef" (spec:22). But F004 hasn't routed real Kronos (F004 spec:71), so F002 signals_log is `source=placeholder` (F004 spec:32). If F007's FactorDef inputs include Kronos-derived signals, it could consume placeholder signals. The finding says "F007 dependency ignores placeholder limitation, so controls could consume placeholder signals." Need to point to F007 spec:22 and maybe spec:279 dependency (only F002). Also design.md:24 upstream contract. The finding is that F007 declares F004/Kronos as upstream but does not record the placeholder limitation / require real-source verification, so a canonical run could pass on placeholder signals. Concrete: F007 spec:22 "F004/Kronos 与人工因子产出的 FactorDef"; F007 spec:104 positive controls; F004 spec:32,71. ✅

Finding #18: F005 allowed to read files directly, weakening ADR-0005 unified read-only API boundary.
- design.md:217 "F005 通过只读 API/文件 reader 渲染 report、curves 与 synthesis".
- ADR-0005 decision 3: unified read-only API is permanent human interface backend; F005 API + web SPA (decision 4).
- spec:218 UX-002 "F005 只能读取 F007 产物".
- So allowing direct file reader bypasses the unified API boundary. ✅

Finding #19: permanent final-confirmation-window stats are not explicitly excluded from Agent-readable report/manifest/synthesis.
- ADR-0003:56 "...永久隔离的最终确认窗... 仅在候选晋升 paper 前使用一次".
- F007 spec:224 NFR-003 Agent/preview no holdout read or promotion. But final confirmation window is separate from holdout; spec only mentions 留出. design.md:225 "留出 reader". No explicit exclusion of that window from Agent-readable artifacts. ✅ Evidence: ADR-0003:52-56 (need exact), F007 spec:224, design.md:225.

Finding #20: design test map omits several tests used in tasks (`upstream_contracts`, `canonical_registry`, `artifact_schemas`, `controls`, `gate_mutations`).
- design.md §8 table maps AC-001..AC-008 to 8 test files. tasks use additionally: `tests/contract/test_f007_upstream_contracts.py` (T001), `tests/integration/test_f007_canonical_registry.py` (T012), `tests/contract/test_f007_artifact_schemas.py` (T015), `tests/integration/test_f007_controls.py` (T016), `tests/mutation/test_f007_gate_mutations.py` (T017). Missing from design §8. ✅
- Note design §8 last paragraph mentions guard registry/mutation but no file.

Finding #21: five stage IDs and failure dimensions are not frozen; tasks says three dimensions without schema.
- design:197 "evaluator 依次写五阶段结果" but stage IDs not enumerated in design's structured schema (report.json stage results). Actually design §3.3 says stage states enum but no stage ID list. spec FR-003:150 五阶段 named 信号质量、组合转换、成本/容量、时序稳定、执行实现. tasks T014 says 五阶段/三维失败汇总 (tasks:49). design §0/§4 no enum of failure dimensions. So frozen schema missing. Design's event example stage: "signal_quality" only. ✅
- Finding #21 says "five stage IDs and failure dimensions are not frozen; tasks says three dimensions without schema." Evidence: design:197, spec:150, tasks:49.

Finding #22: NFR-005 path portability and UX-001 CLI first-screen have no complete task/AC traceability.
- spec:226 NFR-005; spec:217 UX-001.
- No AC references NFR-005 or UX-001. tasks none. design:213 CLI first screen. ✅

Finding #23: Low quality: design embeds procedural tasks.md action directive, despite design responsibility rule.
- design.md:16-18 the "开发前置约束" block instructs tasks.md must add [TEST] group; features/README says design doesn't write step-by-step coding tasks and 10 节 only DQ. Actually the rule: "design 只描述结构、契约、状态、失败和技术取舍，不写逐步编码任务." So embedding a tasks action directive in design is a responsibility violation (quality). ✅

Finding #24: Low correctness: state vocabulary and canonical=`bench` mapping/event registration are not fully mirrored across spec/design.
- spec §5 lifecycle states: CREATED→VALIDATING→RUNNING→EVIDENCE_READY→INCOMPLETE→REGISTERED→FINALIZED→PREVIEW_DONE (spec:231-237).
- design directory: preview/, bench/, cohorts/ (design:35,100). design:100 canonical artifacts under bench/ — so spec "canonical" vs design "bench" mapping not explained; event types: spec TR-001 `evaluation.run_state_changed`, TR-002 `evaluation.gate_rejected`, TR-003 population registration; design event type adds `evaluation.registered` (design:176) which isn't in spec. Also spec lifecycle has `REGISTERED`/`FINALIZED`/`PREVIEW_DONE` states but design's event example from/to only RUNNING/INCOMPLETE. So state vocabulary not fully mirrored: spec uses verdicts `promising`/`dead` while design uses PASS/FAIL; and canonical=bench not stated. Actually finding #11 covers verdict vocabulary. Finding #24 is specifically state vocabulary + canonical=bench mapping + event registration. ✅
- Evidence: spec:231-237, design:35,100,176; spec:205-207.

Finding #25: Low test-coverage: T005 marked [P] but T004 is not; property-test strategy lacks explicit execution/tool task.
- tasks.md:33 T004, tasks.md:34 T005 [P], tasks.md:70 "T005 [P] 可与 T004 并行".
- Rule from features/README: `[P]` only for tasks modifying different files without ordering dependency; T005 modifies isolation capability; T004 modifies identity modules — stated no shared state. Hmm, the finding is T005 [P] but T004 not [P]? Actually [P] marks can be on either. But the task text says "T005 marked [P] but T004 is not". That's odd but I'll report as stated: designation inconsistent (only one of a mutually-parallel pair marked [P]), plus property-test strategy (spec:274, design:242) lacks explicit task/tooling (property test framework pinned). I can merge into one low finding. ✅

Now I need exact line numbers for PRD, SOP, ADR-0003. Let me grep.

Also need to verify design.md has no mention of 留出预算 ledger, generation.run_completed, etc.

Let me run a batch of greps.
Now gathering exact line numbers for PRD/SOP/ADR citations and verifying absence claims.

  <details><summary>tool output</summary>

  ```text
179:- **FR3.5 样本量裁决**：少于 30 笔为 `UNDERPOWERED`；30~69 笔最多临时 PASS，只允许缩减仓位
181:- **FR3.6 无前视三层审计**：AST 纯度、独立逐 K 线重放、信号缓存 merge/join 时间戳与陈旧度检查
184:- **FR3.7 第二实现复核**：高价值候选、评测差异或系统升级时用独立实现复核。Vibe-Trading 可在 1 周
189:- **FR3.9 证据执行层级与失败语义**：所有运行显式声明 `preview | canonical`。preview 写隔离产物，
=== SOP real-env ===
23:| 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |
64:- **真实环境测试纪律**：需要真实进程/文件系统/端到端/GPU 的测试一律在**能力所在的机器**上
68:  `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration -q`；服务不可达或
=== ADR0003 ===
13:真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
21:   通过最终 90 天留出和永久隔离最终确认；不得先看留出再组装策略，效率提升也不得来自放宽门禁。
22:2. **样本量门槛**：留出期 <30 笔输出 `UNDERPOWERED`（不判 PASS 也不判 FAIL），触发扩宇宙/
23:   延长窗口，而不是放行；30~69 笔最多临时 PASS（仅可缩减仓位进入 paper）；约 ≥69 笔才允许
25:3. 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== design 预算/留出/ledger ===
25:- **实现约束**：研究只读有效 Parquet；执行层级显式传参；Agent 无 canonical writer/留出能力；
225:- 权限边界：canonical writer 和留出 reader 作为显式 capability 注入；preview/Agent 构造器没有
237:| `AC-001` | integration + mutation | `tests/integration/test_f007_execution_tiers.py` | preview 无 canonical/holdout 写能力，越权必红 |
256:| 固定 90 天的 regime 风险 | v0.2 记录 regime 并实现 rolling split；最终留出纪律不改 | 单窗口结论有条件性 | 按 ADR-0003 路线滚动化 |
=== tasks 预算/留出 ===
21:- canonical writer、留出访问、统计失败语义与 artifact 发布属于高风险路径，必须变异验证。
27:- [ ] T003 (`NFR-003`): 为 preview、canonical writer 和留出 reader 建立 capability 测试夹具 — verify: `tests/integration/test_f007_execution_tiers.py`
=== design F003 events ===
217:F005 通过只读 API/文件 reader 渲染 report、curves 与 synthesis；不得重算 BH-FDR、漏斗、
243:| `AC-007` | integration + golden | `tests/integration/test_f0
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:33:29Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md", "offset": 28, "limit": 50})`
- **tool**: `bash({"command": "echo \"=== PRD 176-192 ===\"; sed -n '176,192p' docs/alphamill-prd.md; echo \"=== SOP 60-76 ===\"; sed -n '60,76p' docs/SOP.md; echo \"=== ADR0005 dec4 ===\"; grep -n \"研究面自建先行\\|统一只读 API 是永久\" docs/decisions/0005-presentation-observability.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Good. Confirmed design/tasks have no holdout budget ledger/task beyond capability fixture; no F003 event ingestion in design; no approximation.

Now let me get exact lines for ADR-0003:42-56 (I have 47,49,51), and 63-71 (I have 64,65,68,71). Good enough.

Now let me verify finding #5 details: F007 spec:137-147 (FR-002), spec:108-111 (范围外), design:206-209 (methodology gate).

Let me also get exact lines for:
- F004 spec:32,42,43,71,72 (placeholder/routing).
- F007 spec:22,104; design:24.
- F007 design:35,100,176.
- F007 spec:231-237.
- F007 design:145,157-159,193.
- F008 tasks:90.
- F008 design:100.
- PRD:179-183.
- SOP:22-24,64-75.
- F007 spec:290/design:255 second impl.
- spec:274, design:242 property test.

Let me get F004 exact lines around 32,71 with context, and confirm second-implementation lines.

I think I have enough. Let me also check the TEMPLATE tasks.md for [TEST] group reference (design.md:16-18 references it). F003-D011 cited `docs/features/TEMPLATE/tasks.md:57-61`. For F007 finding #1, we cite design.md:16-18 and tasks.md:54-62. Let me check TEMPLATE to confirm [TEST] group requirement. Not strictly needed.

Now, the task says exactly one unified 13-column Chinese findings table. Columns (from review-convergence): ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签.

Now let me count findings and severities. The task lists 25 items, with permission to merge #22/#24/#25 internally only if no evidence lost. Let me decide whether to merge.

Let me carefully assign severities:
1) High test-coverage/process-gap: missing mandatory [TEST] group
2) High correctness/spec-drift: F003 upstream omitted in design/tasks + no ingestion path
3) High correctness/cross-feature drift: F008 omitted
4) High correctness/cross-feature drift: universe/calendar conflation
5) High correctness/spec-drift: three-layer no-lookahead not assigned
6) High correctness/spec-drift: sample-size three-tier missing
7) High correctness/task DAG
8) High correctness/task DAG
9) High test-coverage/gate-without-teeth: T022
10) High correctness/gate-without-teeth: holdout budget ledger
11) Medium correctness: verdict vocabulary
12) Medium test-coverage: SC-002 concurrency
13) Medium test-coverage: AC-003 denominator batch
14) Medium correctness: NFR-004 preview approximation
15) Medium test-coverage: mutation targets/AC labels
16) Medium correctness: second-implementation spot-check
17) Medium correctness: F004 placeholder
18) Medium correctness: F005 direct file read
19) Medium correctness: final-confirmation window stats
20) Medium test-coverage: design test map omissions
21) Medium correctness: stage IDs/failure dimensions not frozen
22) Medium correctness: NFR-005/UX-001 traceability
23) Low quality: design embeds tasks directive
24) Low correctness: state vocab + canonical=bench mapping
25) Low test-coverage: T005 [P] + property test tooling

Count: High = 1-10 = 10. Medium = 11-22 = 12. Low = 23-25 = 3. Total 25.

If I merge #22/#24/#25, total reduces. The task says "You may merge #22/#24/#25 internally only if no evidence is lost, but do not omit substantive concerns. Severity counts must exactly match final issue list." Merging three separate concerns (NFR-005/UX-001 traceability = medium; state vocab = low; [P]/property tooling = low) into one doesn't make sense since severities differ. Better to keep all 25 separate. That gives severity_counts: {critical: 0, high: 10, medium: 12, low: 3}. Total 25.

Hmm, but wait. Let me reconsider #25 severity: it's listed as "Low test-coverage". And #24 Low correctness, #23 Low quality. So low=3.

Actually, let me reconsider whether to merge #24 into #11 (both about vocabulary). #11 is verdict vocabulary (Medium correctness). #24 is state vocabulary + canonical=bench + event registration (Low correctness). They are distinct: #11 verdicts (promising/dead vs PASS/FAIL), #24 state machine vocabulary and directory mapping (bench) and event types. I'll keep separate to preserve evidence. The instruction says "You may merge ... only if no evidence is lost" — I'll keep separate to be safe; the counts then are high 10, medium 12, low 3.

Let me double check #20 category: "Medium test-coverage: design test map omits several tests". Yes medium.

Now let me finalize the finding IDs: F007-D001 through F007-D025 in the order listed.

Now I need to build the report. Let me also gather exact line refs to make each location precise.

Let me quickly verify a few remaining exact lines:
- F007 spec.md:22 (F003), spec.md:7.
- design.md:5, design.md:52.
- tasks.md:5.
- F003 spec.md:251-258, 328-330.
- F008 spec.md:7, 243-244, 313, 326.
- F007 spec.md:198, 212.
- design.md:145,157-159,193.
- F008 tasks.md:90.
- PRD:181-183; SOP:22-24; F007 spec:137-147,108-111; design:206-209.
- PRD:179-180; ADR-0003:22-24,63-71; design:124-126,222-223; tasks T010 (tasks.md:42).
- tasks.md:41,44-45,67.
- tasks.md:36,42-43,49,51,68-69.
- spec.md:275; tasks.md:51,60; SOP:64-75.
- spec.md:40,55,128-135,201,259; ADR-0003:42-56.
- design:124-126,222-223 + spec:158,176,182,218? For #11: spec:158,176,182,243,118; design:109,123-126,222-223.
- #12: spec:253; design:201-204; tasks:44-45,60.
- #13: spec:261; design:239; tasks:41,51.
- #14: spec:225; design §8 (233-247); tasks (no).
- #15: tasks:52,59; design:247.
- #16: spec:290; design:255; tasks (none).
- #17: spec:22,104,279; F004 spec:32,71,72.
- #18: design:217; spec:218; ADR-0005 decision 4 (line ~55-65).
- #19: ADR-0003:51-56,82; F007 spec:224; design:225.
- #20: design:235-247; tasks:25,44,50,51,52.
- #21: spec:150; design:197; tasks:49.
- #22: spec:217,226; design:213; tasks (none).
- #23: design:16-18; features/README rule.
- #24: spec:231-237; design:35,100,176; spec:205-207.
- #25: tasks:33-34,70; spec:272-274; design:238,242.

Let me verify F004 spec line numbers precisely by reading lines 28-75.

Also verify ADR-0005 decision 4 line numbers. And PRD exact lines 179-183, and SOP 64-75, 22-24.

Let me batch.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md</path>
<type>file</type>
<content>
28: ## 1. 问题、目标与非目标
29: 
30: ### 问题
31: 
32: compose 的 `kronos-signal` 服务默认 `KRONOS_USE_REAL_MODEL=false`（镜像基于 `python:3.11-slim`，不含 torch，也不挂载 `vendor/Kronos` 与 `models/`）。真实推理只能靠人工在宿主 venv 起一个 8002 实例——F001 AC-006 因此是「留档命令」而非编排内证据；F002 导出的 `signals_log` 内容全是 `source=placeholder`。
33: 
34: ### 目标
35: 
36: - `docker compose -f deployment/docker-compose.yml --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；
37: - F001 AC-006 的复跑不再依赖手工起进程。
38: 
39: ### 非目标
40: 
41: - 不改 Kronos 上游代码与 HTTP API 契约（F001 已冻结）；
42: - 不做 GPU 推理与性能优化（Kronos 常驻推理的目标机是执行机（当前 `qiaozhi-lt` 的 RTX 4060，架构 §7.1）；本 feature 的编排与契约验收在 CPU 推理上即成立，GPU 直通留给执行机落地时处理）；
43: - 不把真实推理设为
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== PRD 176-192 ===
- **FR3.4 验证顺序**：规则在看数据前固定；FactorDef 粗筛/选择期 → FR4 构建并冻结 PortfolioDef
  → PortfolioDef 最终 90 天留出 → 永久隔离最终确认窗。每周进入最终留出的组合候选上限默认 5，
  所有访问写 append-only 台账。不得先读取留出结果再新建或修改组合。
- **FR3.5 样本量裁决**：少于 30 笔为 `UNDERPOWERED`；30~69 笔最多临时 PASS，只允许缩减仓位
  paper；约 ≥69 笔才可形成可信判定并计入北极星判据。
- **FR3.6 无前视三层审计**：AST 纯度、独立逐 K 线重放、信号缓存 merge/join 时间戳与陈旧度检查
  全部通过才可晋级；切分以 label endpoint 为边界，按 pair 的 point-in-time 可交易日历处理，
  embargo 不短于最大标签 horizon，拟合型变换只在训练折拟合。
- **FR3.7 第二实现复核**：高价值候选、评测差异或系统升级时用独立实现复核。Vibe-Trading 可在 1 周
  time-box 内提供 local loader、Bootstrap/Walk-Forward 和回测对照；超时则用独立重放器或手工第二
  实现，不阻塞主链路。
- **FR3.8 正控制与漏斗**：funding carry、BTC/ETH 截面动量同期跑完整门禁；逐级记录 §2.3 漏斗，
  周报必须指认最大流失级。
- **FR3.9 证据执行层级与失败语义**：所有运行显式声明 `preview | canonical`。preview 写隔离产物，
  不进入 official population、不消耗留出预算、不访问永久确
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:33:42Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc-F007.md", "content": "---\nreport_type: doc-review\nfeature: F007\nround: 1\ndate: 2026-09-16\nprior_report: none\nscope: full-scan\nstop_condition_met: false\nseverity_counts: {critical: 0, high: 10, medium: 12, low: 3}\nissues:\n  - id: F007-D001\n    title: \"tasks 缺 design.md:16-18 强制的 [TEST] 旅程验收组\"\n    severity: high\n    category: test-coverage\n    root_cause: root-cause\n    origin: process-gap\n    pattern_tag: \"te
…[truncated])`


> [reasoning] Now I have all the evidence. Let me also confirm F007 design lines 124-126 and 222-223, and 206-209, and spec:108-111, 137-147. Already have from read.

Let me now verify exact line for design.md:52 (SynthesisBuilder). Line 52 is `SynthesisBuilder ── finalized canonical cohort manifests + curves ── synthesis_report.json`. ✅

design.md:35 storage: `reports/bench/`. ✅

Now let me build the report. I'll write the file with apply_patch. Wait — the instruction says "apply_patch only for the new target file". I have a `write` tool and an `edit` tool, but no `apply_patch` tool in my available tools. Hmm. The task says "REQUIRED TOOLS: Read files needed for exact citations, then apply_patch only for the new target file." There's no apply_patch tool exposed. I'll use the `write` tool to create the new file, which is the equivalent. That's fine.

Let me set up a todo list? The task is essentially one deliverable (write one report). Multi-step but single artifact. I'll create a short todo list to comply with todo discipline. Actually, the report is the deliverable; I've done research. Let me just create the file. But Todo discipline says 2+ steps → todowrite FIRST. I've already done exploration. Let me just proceed to write; I'll add minimal todos to track.

Actually let me just write the file now. It's a big write. Let me compose carefully.

Report structure:
- YAML frontmatter: report_type: doc-review, feature: F007, round: 1, date: 2026-09-16, prior_report: none, scope: full-scan, stop_condition_met: false, severity_counts: {critical: 0, high: 10, medium: 12, low: 3}, issues: [25 objects].
- Body: conclusion-first, baseline/scope, checklist/evidence, findings table (13 columns), adjudication section, passed items, next steps/stop condition.

Each issue object fields: id, title, severity, category, root_cause, origin, pattern_tag, status: open, tracked_task: "", fix_summary: "", regression_test, suggested_fix, disposition_reason: "", location, first_seen_round: 1, resolved_round: "".

The task says empty fix_summary/resolved_round/tracked_task/disposition_reason. And every finding must have concrete suggested fix + prefixed regression_test (`proposed:`, `existing:`, or `manual-review-only:`).

Since it's doc review, most regression_test will be `proposed:tools/...::test_...`. Some may be `manual-review-only:` where no automated test makes sense (e.g., #23 quality). Let me assign.

Let me define each finding in detail:

**F007-D001** High / test-coverage / process-gap / original-coding (design.md:16-18 mandates it; F007's own design constraint). pattern_tag: "test-group-missing". regression_test: `proposed:tools/validate_spec_lifecycle.py::test_test_group_required`.
title: tasks 缺 design.md 强制的 [TEST] 旅程验收组
location: docs/features/0.2/F007-evaluation-gates/design.md:16-18; docs/features/0.2/F007-evaluation-gates/tasks.md:54-62
suggested_fix: tasks §3 增补 `### [TEST] 组：层 2 旅程验收轨`，从 US-001/002/003 每旅程步骤派生 ≥1 条可执行断言（早编写晚执行），使 SDD Flow T3 不拒绝流转；同步 design.md:16-18。

**F007-D002** High / correctness / spec-drift / cross-feature-contract-drift. title: F003 上游仅出现在 spec，design/tasks 的 related_features 与实现任务缺其事件/算子登记表摄入路径.
location: F007 spec.md:7,22; design.md:5,52; tasks.md:5; F003 spec.md:251-258,328-330.
suggested_fix: design/tasks frontmatter related_features 增 F003；design §2/§4 增 generation.run_completed/candidate_rejected/算子能力清单/协同池的摄入与漏斗第一级映射；tasks 增对应实现与契约任务（如 T001 上游契约扩展或新增任务）。
regression_test: proposed:tools/check_doc_consistency.py::test_f007_ingests_f003_contracts

**F007-D003** High / correctness / spec-drift / cross-feature-contract-drift. title: F008 未列入 F007 related_features/上游，尽管 F008 显式产 ResearchSnapshot 消费的 universe artifact.
location: F007 spec.md:7,198,212; F008 spec.md:7,243-244,313,326.
suggested_fix: F007 spec.md:7 related_features 与 §0 上游 Contract 增 F008；design.md:5/tasks.md:5 同步；IR-002 引用 F008 的 universe artifact digest 与 universe_at(T)。
regression_test: proposed:tools/check_doc_consistency.py::test_f007_declares_f008_universe

**F007-D004** High / correctness / spec-drift / cross-feature-contract-drift. title: F007 把 universe 与 calendar 合并为单个 JSON，与 F008 的 universe CSV artifact + universe_at(T) 及 calendar 归属冲突.
location: F007 design.md:145,157-159,193; F007 spec.md:198,212; F008 design.md:100; F008 tasks.md:90; ADR-0007:72-74.
suggested_fix: 拆分 universe 与 calendar 两个 artifact 契约：universe 按 F008 IR-002 的 digest + universe_at(T) 消费（CSV），calendar 明确 owner 与 schema（F007 或另立）；CLI 与 builder 分别接收两 ref；A/DR/IR 同步。
regression_test: proposed:tools/check_doc_consistency.py::test_universe_calendar_artifacts_split

**F007-D005** High / correctness / spec-drift. title: PRD FR3.6/SOP 三层无前视中，F007 只覆盖方法论守卫层，独立逐 K 线重放与信号缓存对齐未显式承接.
location: PRD:181-183; SOP:22-24; F007 spec.md:137-147,108-111; design.md:206-209.
suggested_fix: F007 spec/design 明确三层归属：AST 纯度+方法论守卫（已有）之外，显式声明独立逐 K 线重放与信号缓存时间戳对齐层由谁在晋级前执行、产出何证据；若确实后移 F006，需给出晋级前 fail-closed 门与 owner，不能只在范围外一行带过。
regression_test: proposed:tools/check_doc_consistency.py::test_no_lookahead_three_layers_owned

**F007-D006** High / correctness / spec-drift. title: 样本量三级契约（<30 UNDERPOWERED；30~69 临时 PASS/缩减 paper；≥69 可信）缺失，F007 把不足合并为单一 UNDERPOWERED 且无可晋级条件裁决.
location: PRD:179-180; ADR-0003:22-24,63-71; F007 design.md:124-126,222-223; F007 spec.md:118,173-182; tasks.md:42 (T010).
suggested_fix: 在 spec FR-005/design §3.3/§7 冻结三级样本量裁决与 `temporary_pass`/可信样本量判定，AC-004 增对应断言；T010 verify 增三级用例。
regression_test: proposed:tools/check_doc_consistency.py::test_sample_size_three_tiers

**F007-D007** High / correctness / process-gap? Actually category correctness, root_cause root-cause, origin process-gap? The task says "task DAG". Let me use origin: process-gap, pattern_tag "task-graph-missing-edges". title: T012 finalize 计算 BH-FDR/DSR 但依赖图缺 T009→T012；T013 缺 T012→T013.
location: tasks.md:41,44-45,67.
suggested_fix: §4 依赖补 `T009 -> T012`、`T012 -> T013`。
regression_test: proposed:tools/check_task_dag.py::test_no_missing_edges_f007

**F007-D008** High / correctness / process-gap. title: 全链控制 T016 需 registry/synthesis 但图缺 T012/T014→T016；T010/T011 消费 T007 阶段模型却无 T007 出边.
location: tasks.md:36,42-43,49,51,68-69.
suggested_fix: §4 增 `T007 -> T010,T011`、`T012 -> T016`、`T014 -> T016`（或显式说明可由 fixture 解耦并补替代前置）。
regression_test: proposed:tools/check_task_dag.py::test_no_missing_edges_f007 (reuse? better distinct). Use `proposed:tools/check_task_dag.py::test_full_chain_controls_have_predecessors`.

**F007-D009** High / test-coverage / gate-without-teeth / process-gap. title: 真实环境证据 T022 与 T016 复用同一 fixture 测试，无独立不可变 crypto 快照与集成命令.
location: F007 spec.md:275; tasks.md:51,60; SOP:64-75.
suggested_fix: T022 拆出真实环境验证：绑定不可变 crypto snapshot 证据（hostname + digest）并用 `ALPHAMILL_INTEGRATION=1` 独立命令；设计固定 snapshot 引用与归档路径；SOP §3 纪律对齐。
regression_test: proposed:tools/check_doc_consistency.py::test_real_env_task_has_distinct_evidence

**F007-D010** High / correctness / gate-without-teeth / spec-drift. title: 留出预算被断言零变化，但 DR/design/tasks 无预算台账/实体/append-only 契约.
location: F007 spec.md:40,55,128-135,201,259; ADR-0003:42-56.
suggested_fix: 新增 holdout budget ledger 实体（append-only，字段含 candidate/week/verdict）与 DR，并给 preview 越权写入的负例；AC-001 增「台账零行」断言；design §3 增目录/schema，tasks 增实现。
regression_test: proposed:tools/check_doc_consistency.py::test_holdout_budget_ledger_exists

**F007-D011** Medium / correctness / spec-internal-contradiction / spec-drift. title: verdict 词汇冲突：spec 用 promising/dead/UNDERPOWERED，design 用 PASS/FAIL/... 与 promotion_verdict，缺分层枚举冻结.
location: F007 spec.md:118,158,176,182,243; design.md:109,123-126,222-223.
suggested_fix: 冻结两层枚举：stage 状态（PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE）与晋升/成本 verdict（promising/dead/temporary_pass 等），在 spec FR-003/FR-005 与 design §3.3 用同一术语表；AC-004/AC-003 引用一致。
regression_test: proposed:tools/check_doc_consistency.py::test_verdict_vocabulary_frozen

**F007-D012** Medium / test-coverage / gate-without-teeth / process-gap. title: SC-002 的 claim/registration/finalize 并发与故障注入无 task/test 承接.
location: F007 spec.md:253; design.md:201-204; tasks.md:44-45,60.
suggested_fix: 增并发/故障注入集成测试任务（同 ID 并发 claim、崩溃后 lease 接管、finalize 原子性），design §8 映射 SC-002；T023 引用该测试。
regression_test: proposed:tools/check_doc_consistency.py::test_sc002_concurrency_has_task

**F007-D013** Medium / test-coverage / spec-tasks-traceability-gap / process-gap. title: AC-003 分母语义缺多成员批量用例，isolated controls 无法证明拒绝者也计入分母.
location: F007 spec.md:261; design.md:239; tasks.md:41,51.
suggested_fix: 增多成员 cohort 批量 fixture 测试（含被拒成员仍在分母、诊断性重算不重复计数），tasks T016 与该测试绑定。
regression_test: proposed:tools/check_doc_consistency.py::test_ac003_multi_member_batch

**F007-D014** Medium / correctness / spec-tasks-traceability-gap / spec-drift. title: NFR-004 preview 近似标注无 design/task/AC 覆盖.
location: F007 spec.md:225; design.md:233-247; tasks.md.
suggested_fix: design §3.3 report schema 增 approximation 字段与标注契约；tasks 增实现与断言；AC 增 NFR-004 引用（或新增 AC）。
regression_test: proposed:tools/check_doc_consistency.py::test_nfr004_approximation_covered

**F007-D015** Medium / test-coverage / gate-without-teeth / process-gap. title: 变异目标与 AC 标签不一致；T017 覆盖多于 T021 声明，且无 kill artifact/工具锁定.
location: tasks.md:52,59; design.md:247; spec.md:274.
suggested_fix: 统一 T017/T021 的 AC 标签（含 FR-001/preview writer）；增变异工具依赖 pin 与 mutant-killed 证据产物（报告 JSON）作为 verify。
regression_test: proposed:tools/check_doc_consistency.py::test_mutation_targets_labels_aligned

**F007-D016** Medium / correctness / deferred-work-without-carrier / spec-drift. title: 统计第二实现抽查决策无任务承接.
location: F007 spec.md:290; design.md:255; tasks.md.
suggested_fix: 新增第二实现对照任务（明确 time-box、对照对象、容差与证据路径）或写入 §5 明确后移并给 owner。
regression_test: proposed:tools/check_doc_consistency.py::test_second_implementation_has_task

**F007-D017** Medium / correctness / cross-feature-contract-drift / spec-drift. title: F004 真实 Kronos 未接线，F007 依赖未记录 placeholder 限制，控制可能消费 placeholder 信号.
location: F007 spec.md:22,104,279; F004 spec.md:32,71,72.
suggested_fix: F007 spec/design 记录 F004 signals_log 的 source 契约与真实源前置；正控制/评测输入不得接受 `source=placeholder`（或显式标注并阻断 canonical）；与 F004 tasks §5 联动。
regression_test: proposed:tools/check_doc_consistency.py::test_f007_rejects_placeholder_signals

**F007-D018** Medium / correctness / cross-feature-contract-drift / spec-drift. title: F005 被允许直接用文件 reader 读 F007 产物，削弱 ADR-0005 统一只读 API 边界.
location: F007 design.md:217; spec.md:218; ADR-0005:40-52.
suggested_fix: design/spec 明确 F005 只经 `src/alphamill/api/` 只读 API 消费，或声明文件 reader 为过渡并给收敛任务与 owner；与 ADR-0005 决策 3/4 对齐。
regression_test: proposed:tools/check_doc_consistency.py::test_f005_reads_via_api

**F007-D019** Medium / correctness / gate-without-teeth / spec-drift. title: 永久最终确认窗统计未显式排除在 Agent 可读 report/manifest/synthesis 之外.
location: ADR-0003:51-56,82; F007 spec.md:224; design.md:225.
suggested_fix: spec NFR-003/IR-003 与 design §3.3/§7 明确最终确认窗数据不进任何 Agent/preview 可读产物并 fail-closed；AC 增断言。
regression_test: proposed:tools/check_doc_consistency.py::test_final_confirmation_window_hidden

**F007-D020** Medium / test-coverage / spec-tasks-traceability-gap / process-gap. title: design §8 测试映射遗漏 tasks 使用的多个测试文件.
location: design.md:235-247; tasks.md:25,44,50,51,52.
suggested_fix: design §8 表补 `test_f007_upstream_contracts.py`、`test_f007_canonical_registry.py`、`test_f007_artifact_schemas.py`、`test_f007_controls.py`、`test_f007_gate_mutations.py` 的 AC 映射。
regression_test: proposed:tools/check_doc_consistency.py::test_design_test_map_covers_tasks

**F007-D021** Medium / correctness / spec-tasks-traceability-gap / original-coding. title: 五阶段 ID 与失败维度未冻结，tasks 只说「三维失败汇总」无 schema.
location: F007 spec.md:150; design.md:197; tasks.md:49.
suggested_fix: design §3.3/§4 冻结五阶段 ID 枚举与失败维度 schema（枚举、owner、必填字段），spec FR-003 引用同一清单，tasks T014 按该 schema 实现。
regression_test: proposed:tools/check_doc_consistency.py::test_stage_ids_and_failure_dimensions_frozen

**F007-D022** Medium / correctness / spec-tasks-traceability-gap / process-gap. title: NFR-005 路径可移植与 UX-001 CLI 首屏无完整 task/AC 追溯.
location: F007 spec.md:217,226; design.md:213; tasks.md.
suggested_fix: 为 NFR-005 与 UX-001 增 AC 引用与 tasks verify（路径/URI 断言、CLI 首屏字段快照测试）。
regression_test: proposed:tools/check_doc_consistency.py::test_nfr005_ux001_traceable

**F007-D023** Low / quality / design-responsibility-violation / process-gap. title: design 内嵌 tasks.md 行动指令，越界写逐步任务.
location: design.md:16-18; docs/features/README.md（design 职责）.
suggested_fix: 把该行动指令移到 tasks.md（作为 [TEST] 组说明或 §0 执行规则），design 只留设计约束结论；或改为一句话约束指向 tasks。
regression_test: manual-review-only:docs/features/README.md 责任边界人工复核

**F007-D024** Low / correctness / spec-internal-contradiction / original-coding. title: 状态词汇与 canonical=`bench` 映射/事件注册未在 spec/design 完全对齐.
location: F007 spec.md:205-207,231-237; design.md:35,100,176.
suggested_fix: 统一 spec 生命周期状态与 design 目录/事件命名（明确 canonical 落 `bench/`），并把 `evaluation.registered` 纳入 spec TR-003 事件表。
regression_test: proposed:tools/check_doc_consistency.py::test_state_vocab_and_bench_mapping_aligned

**F007-D025** Low / test-coverage / spec-tasks-traceability-gap / process-gap. title: T005 标 [P] 而 T004 未标；属性测试策略缺显式执行/工具任务.
location: F007 tasks.md:33-34,70; spec.md:272-274; design.md:238,242.
suggested_fix: 修正 [P] 标注一致性；为属性测试补执行任务与工具 pin（如 hypothesis），并在 design §8 映射。
regression_test: proposed:tools/check_task_dag.py::test_parallel_markers_consistent

Now severity counts: high: D001-D010 = 10; medium: D011-D022 = 12; low: D023-D025 = 3. Total 25. ✅

Now, the table needs columns: ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签.

Now "已通过项" must state explicit passes:
- required section structures (spec 9 / design 11 / tasks 6)
- frontmatter/status ownership (status only in spec frontmatter)
- Q/DQ closed (spec §8 无, design §10 无)
- AC IDs/references valid for draft (AC-001..AC-008 unique IDs + requirement refs; tests path optional in draft)
- active indexes consistent (BACKLOG F003/F007/F008; CLAUDE:49-52; docs/README:36)
- identity and ResearchSnapshot contracts aligned (F007 identity DR-002 vs ADR-0006/ADR-0007; snapshot fields)
- fail-closed and AI authority aligned (spec invariants, NFR-003, ADR-0003)

Wait — must be careful: are the AC tests paths present? In draft they may be absent. F007 ACs (spec:259-266) do not include `tests:` paths. Design §8 has the mapping. So AC IDs/references valid for draft = pass; tests paths deferred to design §8. Good.

Identity contracts aligned: F007 spec DR-002 identity excludes path/codec/created_at/host/duration/file SHA (spec:199); matches ADR-0006 evidence-and-identity. ResearchSnapshot DR-001 matches ADR-0007 fields (cutoff, dataset/version/value-digest, as-of/coverage, symbol-map, universe/calendar summary). So aligned at contract level though the universe/calendar ownership is D004. I should note it as pass "身份契约" and ResearchSnapshot contract aligned, while universe/calendar ownership is a separate finding.

Hmm, careful: don't say "ResearchSnapshot contracts aligned" while D004 says conflict on universe/calendar. I'll phrase: "身份与 ResearchSnapshot 字段契约（DR-001/DR-002 vs ADR-0006/ADR-0007）对齐；universe/calendar 的 artifact 归属见 D003/D004。" That's honest.

Now the note about F003-D014: "Note existing active F003-D014 appears partially addressed by F007 spec but not design/tasks; do not modify or adjudicate F003 report." I'll add a note in a section, e.g., "与 F003 检视的关系". Good.

Also explain filename deviation.

Also state baseline main@ab30da9 and worktree clean.

Also MUST NOT claim gates have run. I'll add a note that machine gates were not run in this round; parent will run them. But the F003 report included gate runs. Since instructions explicitly forbid claiming gates ran, I'll write: "本轮未运行任何机器门禁（`tools/verify.py` 等由复核方在收口前执行）；以下通过项均为人工文档核对结论。" Good.

Wait, but a subtlety: task MUST DO says "State explicit passes: required section structures, ... active indexes consistent". These are documentation checks. Fine.

Now let me write the YAML carefully. Note that YAML values with colons/Chinese need quoting. I'll follow the F003 report style: title quoted with double quotes; regression_test quoted; suggested_fix quoted; location quoted; status unquoted; severity unquoted.

Also `category` values; `origin` values; `pattern_tag` quoted. `root_cause: root-cause`.

Let me write the file. I need to be careful about the exact regression_test prefix. Use `proposed:` for all proposed, and `manual-review-only:` for D023.

Also `tracked_task: ""`, `fix_summary: ""`, `disposition_reason: ""`, `resolved_round: ""`.

Let me now write it. First a todo? I'll do a brief todowrite. Actually I'm nearly done; I'll just write the file then verify.

Let me create the file.

One more check: the filename `CURRENT-doc-F007.md` — task says create at that path. And preserve CURRENT-doc.md untouched. Since write creates a new file, fine.

Let me also double-check `.gitignore:39` is `docs/reviews/*`. Confirmed.

Now compose the big file.

For the findings table, I'll use concise suggested_fix text (the full version is in frontmatter). The F003 report used fuller text in table. I'll write moderately concise with file:line.

Let me write the body sections:
1. 结论先行
2. 基线与范围 (including filename deviation & baseline, scope, prior_report, lifecycle)
3. 检视门槛与证据 (bounded checklist, severity layering, evidence caliber, note gates not run)
4. Findings (one table)
   - severity distribution line
5. 裁决记录 (无)
6. 已通过项
7. 与 F003 检视的关系 (F003-D014 note)
8. Round-2 入口与停止条件 / 下一步

Let me write.

For the "13-column" requirement, ensure exactly 13 columns and separator with 13 dashes.

Header: | ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
Separator: |---|---|---|---|---|---|---|---|---|---|---|---|---|

Now write.

I must avoid em dashes/en dashes in prose per anti-AI-slop. But the source documents use Chinese punctuation; I'll use Chinese commas/顿号. Avoid "—" as em dash in my prose? The table uses "—" placeholder for empty cells which is required by review-convergence ("没有数据的字段填 — 占位"). That's a placeholder, acceptable and explicitly required. The anti-slop rule targets prose. I'll keep — only as table placeholders.

Also avoid AI-sounding phrases. Write concise Chinese.

Let me now produce the file content.

I should double check design.md line 109: `选择阶段、窗口、阈值和方法版本。每个承诺成员无论 PASS、FAIL、UNDERPOWERED 或 INCOMPLETE` — yes uses UNDERPOWERED and PASS/FAIL. And spec uses promising/dead. Good.

design.md:176 event types: `evaluation.run_state_changed | evaluation.gate_rejected | evaluation.registered`. spec TR-001/TR-002/TR-003: TR-003 says canonical population 登记 uses experiment_id idempotent key, but event name not given. design adds `evaluation.registered`. So spec TR-003 lacks event type name. And spec lifecycle states REGISTERED/FINALIZED vs design event example from RUNNING to INCOMPLETE only. And design:100 puts canonical under `bench/`. Good.

Now, F007 spec.md:205-207 TR-001/TR-002/TR-003. Let me confirm: line 205 TR-001, 206 TR-002, 207 TR-003. Yes.

Now write.

For location fields, I'll use full repo-relative paths like the F003 report's location. But the task says use inline-code file paths rather than Markdown links so check_doc_links has no new risk. YAML location isn't a markdown link anyway. In the body table I'll use backticks around paths. Good. Actually to be safe, use backticks only in table cells and plain paths in YAML (no links). Fine.

Let me write the file now.
Evidence gathered. Writing the review report now.

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:34:51Z

- **tool**: `bash({"command": ".venv/bin/python - <<'PY'\nimport yaml, collections, re, io\np=\"docs/reviews/CURRENT-doc-F007.md\"\nraw=open(p,encoding=\"utf-8\").read()\nm=re.match(r\"^---\\n(.*?)\\n---\\n\", raw, re.S)\nfm=yaml.safe_load(m.group(1))\nprint(\"keys:\", list(fm.keys()))\nprint(\"report_type:\", fm[\"report_type\"], \"| feature:\", fm.get(\"feature\"), \"| round:\", fm[\"round\"], \"| date:\", fm[\"date\"], \"| prior:\", fm[\"prior_report\"], \"| scope:\", fm[\"scope\"], \"| stop:\", fm[\"stop_cond
…[truncated])`
- **tool**: `bash({"command": "git status --porcelain; echo \"---ignored check---\"; git check-ignore -v docs/reviews/CURRENT-doc-F007.md; echo \"---md5 CURRENT-doc.md unchanged?---\"; git status --porcelain docs/reviews/CURRENT-doc.md docs/features/0.2/F007-evaluation-gates/ 2>/dev/null; md5sum docs/reviews/CURRENT-doc.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now verify the file: YAML validity, frontmatter counts, table columns, no links. Let me run a quick check with python yaml and count issues.

Also confirm CURRENT-doc.md untouched and no other files changed.
Now verifying the report: YAML validity, issue counts vs severity_counts, table columns, and that no other file changed.

  <details><summary>tool output</summary>

  ```text
keys: ['report_type', 'feature', 'round', 'date', 'prior_report', 'scope', 'stop_condition_met', 'severity_counts', 'issues']
report_type: doc-review | feature: F007 | round: 1 | date: 2026-09-16 | prior: none | scope: full-scan | stop: False
issues: 25 sev: {'high': 10, 'medium': 12, 'low': 3} declared: {'critical': 0, 'high': 10, 'medium': 12, 'low': 3}
ids ok: F007-D001 ... F007-D025
all issue-object invariants ok
table rows: 25 | header cols: 13
no markdown links; table 13 cols; 25 rows


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
---ignored check---
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc-F007.md
---md5 CURRENT-doc.md unchanged?---
294cf2c3609b139a69bf489c462071c8  docs/reviews/CURRENT-doc.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:34:59Z


> [reasoning] All checks pass:
- YAML valid, frontmatter fields correct.
- 25 issues, severity counts match: high 10, medium 12, low 3, critical 0.
- All statuses open, empty required fields, regression_test prefix valid, suggested_fix and location present.
- Table 25 rows, 13 columns, no markdown links.
- git status --porcelain empty → worktree remains clean (new file is ignored). CURRENT-doc.md untouched.
- git check-ignore confirms docs/reviews/CURRENT-doc-F007.md ignored by .gitignore:39.

Note: `git status --porcelain` is empty which means the new ignored file doesn't show. That's expected and desired.

Done. Report the result concisely.
Done. Report created at `docs/reviews/CURRENT-doc-F007.md`.

**Verification (all passed):**
- YAML valid; `report_type: doc-review`, `feature: F007`, `round: 1`, `date: 2026-09-16`, `prior_report: none`, `scope: full-scan`, `stop_condition_met: false`.
- 25 issues: `severity_counts {critical: 0, high: 10, medium: 12, low: 3}` matches the table exactly.
- All IDs `F007-D001`…`F007-D025` unique and stable; every status `open`; `fix_summary`/`resolved_round`/`tracked_task`/`disposition_reason` empty; every `regression_test` prefixed (`proposed:` / `manual-review-only:`); every issue has `suggested_fix` + `location`.
- Exactly one 13-column Chinese findings table (25 rows). No Markdown links added.
- `docs/reviews/CURRENT-doc-F007.md` confirmed ignored by `.gitignore:39`; `git status --porcelain` empty, so `CURRENT-doc.md` and all F007 docs are untouched. No git writes, no gate claims.

Baseline recorded: `main@ab30da9`, worktree clean. Filename deviation explained (active F003 loop owns `CURRENT-doc.md`).

Next (<2 min): hand `CURRENT-doc-F007.md` to the reviewer to confirm frontmatter `severity_counts` against the table before Round 2.
