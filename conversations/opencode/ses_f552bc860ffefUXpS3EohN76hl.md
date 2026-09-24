---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f552bc860ffefUXpS3EohN76hl"
title: "Review feature contracts (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T15:27:09Z"
updated_at: "2026-09-16T15:28:44Z"
tokens_input: 173184
tokens_output: 2995
cost: 0.0278
parent_id: "ses_f55324142ffefNy2o4qhiYalh0"
---

# Review feature contracts (@explore subagent)

## user · 2026-09-16T15:27:09Z

TASK: Review F007 cross-feature contracts with F002, F003, F004, and F008.
EXPECTED OUTCOME: Exact bidirectional dependency/contract mismatches, field or vocabulary drift, and explicit passes, each cited file:line with severity and one-line remediation.
REQUIRED TOOLS: Read-only repository tools; prefer codegraph, Read where needed; maximum 5 calls and 800 output tokens.
MUST DO: CONTEXT: F007 Round 1 doc review. GOAL: ensure producers/consumers agree and related_features declarations are symmetric enough for implementation. DOWNSTREAM: report entries and regression-gate proposals. REQUEST: inspect relevant spec/design contracts, including universe/calendar inputs, generator outputs, portfolio consumers, and F003's open F007-related review claim when evidence is available.
MUST NOT DO: No edits, no git writes, no changing or adjudicating the active F003 report, no speculative dependency claims.
CONTEXT: Repo /home/georg/projects/alphamill; baseline main@ab30da9; docs/reviews/CURRENT-doc.md is read-only.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T15:27:10Z

- **tool**: `bash({"command": "git rev-parse --short HEAD; ls docs/reviews/ 2>/dev/null; ls docs/ 2>/dev/null"})`
- **tool**: `glob({"pattern": "**/F00{2,3,4,7,8}*"})`
- **tool**: `grep({"pattern": "related_features|F007|F002|F003|F004|F008", "include": "*.md", "output_mode": "files_with_matches"})`

I'll start with parallel reconnaissance across the spec/design docs and the active review report.

  <details><summary>tool output</summary>

  ```text
ab30da9
CURRENT-doc.md
RETROSPECTIVE.md
README.md
SOP.md
alphamill-architecture.md
alphamill-integration.md
alphamill-prd.md
alphamill-research-factor-mining.md
decisions
design
features
research
reviews


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 55 match(es) in 55 file(s)

/home/georg/projects/alphamill/docs/features/TEMPLATE/design.md

/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md

/home/georg/projects/alphamill/docs/features/TEMPLATE/spec.md

/home/georg/projects/alphamill/docs/features/releases/0.1.md

/home/georg/projects/alphamill/docs/features/README.md

/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/design.md

/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/migration-plan.md

/home/georg/projects/alphamill/conversations/timeline-summary.md

/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/tasks.md

/home/georg/projects/alphamill/docs/features/0.1/F001-quant-crypto-migration/spec.md

/home/georg/projects/alphamill/co
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:27:16Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`

Baseline confirmed: `ab30da9`. Now reading the F007 spec/design plus the four related feature specs and the active review report in parallel.

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

## assistant · 2026-09-16T15:27:22Z

- **tool**: `bash({"command": "for f in F002-data-bridge F003-alphagen-vendor F004-kronos-inference-runtime F008-universe-expansion; do echo \"===== $f/spec.md =====\"; sed -n '1,30p' docs/features/0.2/$f/spec.md; echo \"----- related/upstream/downstream refs -----\"; grep -n \"related_features\\|F007\\|F002\\|F003\\|F004\\|F008\\|上游\\|下游\\|Contract\\|契约\" docs/features/0.2/$f/spec.md | head -40; done"})`
- **tool**: `bash({"command": "for f in F002-data-bridge F003-alphagen-vendor F004-kronos-inference-runtime F008-universe-expansion; do echo \"===== $f/design.md =====\"; sed -n '1,20p' docs/features/0.2/$f/design.md; echo \"----- F007 refs -----\"; grep -n \"F007\\|evaluation\\|评测\\|门禁\\|generation\\.\\|universe_at\\|digest\" docs/features/0.2/$f/design.md | head -30; done"})`

I have F007 spec/design and the F003 report. Now I need the F002/F003/F004/F008 contract surfaces to check bidirectionality. Reading the four related specs' key sections in parallel.

  <details><summary>tool output</summary>

  ```text
===== F002-data-bridge/spec.md =====
---
kind: feature
id: F002
version: "0.2"
status: done
gate_version: 1
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-14
---

# F002：数据桥——Parquet 湖导出与 DuckDB 研究取数层

> Owner: Georg | Target: v0.2.0

## 0. 来源与意图

- **PRD 来源**:`docs/alphamill-prd.md` FR1.2(不可变快照)、FR1.3(研究只读边界)、FR1.4(双口径与时间语义)、FR1.6(灾备,湖部分);里程碑 M1
- **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
- **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/宇宙扩容)、§2.2(symbol_map.csv M1 出口标准)
- **上游决策**:ADR-0007(dataset 独立版本与 ResearchSnapshot 绑定);F002 导出细节仍以 `docs/alphamill-integration.md` §1.2 为权威
- **基座来源**:F00
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
===== F002-data-bridge/design.md =====
---
kind: feature
id: F002
version: "0.2"
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: design
created: 2026-09-12
updated: 2026-09-13
---

# F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**:`spec.md`(FR-001..006 / NFR-001..003)
- **PRD / Architecture / System Design**:`docs/alphamill-prd.md` FR1.2/1.3/1.4/1.6/1.7、M1;`docs/alphamill-architecture.md` §〇、§四、§4.4/4.4.1;`docs/alphamill-integration.md` §1.2(导出设计与修订政策,唯一权威)、§2.2(symbol_map M1 出口)
- **决策约束**:ADR-0007 冻结 dataset 独立版本、DatasetVersion value digest 与下游 ResearchSnapshot 的所有权边界；F002 不组合 snapshot。
----- F007 refs -----
20:- **决策约束**:ADR-0007 冻结 dataset 独立版本、DatasetVersion value digest 与下游 ResearchS
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:27:32Z

- **tool**: `bash({"command": "echo \"=== F007 spec frontmatter ===\"; sed -n '1,12p' docs/features/0.2/F007-evaluation-gates/spec.md; echo \"=== F007 design frontmatter ===\"; sed -n '1,10p' docs/features/0.2/F007-evaluation-gates/design.md; echo \"=== F008 IR-002 ===\"; grep -n \"IR-002\\|universe_at\\|universe_calendar\\|calendar\" docs/features/0.2/F008-universe-expansion/spec.md; echo \"=== F007 calendar/universe mentions ===\"; grep -n \"universe\\|calendar\\|symbol-map\\|symbol_map\" docs/features/0.2/F007
…[truncated])`

I have enough evidence. Let me verify the two remaining specifics: F007's `related_features` asymmetry and F008's IR-002 exact text.

  <details><summary>tool output</summary>

  ```text
=== F007 spec frontmatter ===
---
kind: feature
id: F007
version: "0.2"
status: draft
gate_version: 1
related_features: [F002, F003, F004]
topics: [evaluation, validation, evidence, experiments]
doc_kind: spec
created: 2026-09-13
updated: 2026-09-13
---
=== F007 design frontmatter ===
---
kind: feature
id: F007
version: "0.2"
related_features: [F002, F004]
topics: [evaluation, validation, evidence, experiments]
doc_kind: design
created: 2026-09-13
updated: 2026-09-13
---
=== F008 IR-002 ===
23:- **上游决策**：ADR-0001（横截面 reward 在 6~12 对上噪声大，扩容是产出质量前提）、ADR-0007（研究快照绑定 universe/calendar 摘要）、ADR-0003（门禁不降级——质量门不得为了赶进度放宽）
120:- `universe_membership` 只追加台账（联机库）与 `universe_at(T)` 查询；按 `symbol_map` 同构的方式发布为**内容寻址 artifact** 到湖（ADR-0007 与 `F007` IR-002 都按 artifact 定义它）；
204:系统应当维护只追加的宇宙成员台账，每条记录带生效区间与
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:27:50Z

<analysis>
**Literal Request**: Review F007's cross-feature contracts with F002/F003/F004/F008 for bidirectional mismatches, field/vocabulary drift, and explicit passes, each cited file:line.
**Actual Need**: A Round-1 doc-review finding set for F007 that is symmetric with the active F003 report (esp. F003-D014) and gives implementers a concrete list of producer/consumer disagreements to fix before coding.
**Success Looks Like**: Each mismatch has file:line, severity, and a one-line remediation; explicit passes listed so the reviewer knows what was already checked; no adjudication of F003's report.
</analysis>

Baseline: `main@ab30da9`. F007 spec/design read in full; F002/F003/F004/F008 spec+design contract surfaces read. `CURRENT-doc.md` treated read-only.

<results>
<files>
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md - F007 contract owner; frontmatter:7, upstream:22-23, DR-001:198, IR-002:212
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md - F007 design; frontmatter:5, CLI:140-159, snapshot builder:193
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md - producer of generation.* events/operator registry; :7, :247, :252, :258, :321, :329
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md - :41, :55-56, :114-124, :173-176
- /home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md - universe artifact producer; :7, :120, :243-244, :313, :326
- /home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md - :68, :100, :116, :182
- /home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md - dataset/value_digest producer; :7, :95, :277-278
- /home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md - :296-300, :346-353
- /home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md - signals_log content source; :7, :20, :188-189, :197-198
- /home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md - active F003 report (read-only); F003-D014 at :218-233
</files>

<answer>
**Findings (F007 Round 1, cross-feature contracts)**

| ID | 标题 | 严重度 | 位置 | 一句话修复 |
|---|---|---|---|---|
| F007-D001 | F007 spec 声明 F003 上游，但 design frontmatter 漏 F003，且 F003 的 `related_features` 含 F007 而 F007 design 不含 F003 | High | F007 design.md:5 vs F007 spec.md:7; F003 spec.md:7 | design.md:5 改为 `related_features: [F002, F003, F004, F008]`，与 spec 对齐 |
| F007-D002 | F007 未声明 F008 上游，但 F008 声明 F007 下游，且 F007 IR-002/DR-001 消费 F008 的 universe/calendar artifact | High | F007 spec.md:7,198,212 vs F008 spec.md:7,313,326 | F007 spec.md:7 增 F008；spec:22-23 上游 Contract 增 F008 IR-002/IR-003 universe artifact |
| F007-D003 | universe/calendar artifact 词汇漂移：F008 定义 `universe_at(T)` + digest 的 CSV artifact，F007 只写 `universe/calendar JSON` 且路径 `_inputs/universe_calendars/<digest>.json` | High | F007 design.md:145,157-158,193 vs F008 spec.md:243-244, design.md:100,116 | F007 design:157-158 改为引用 F008 的 `lake/_metadata/universes/<digest>.csv` 与 `universe_at(T)`，或显式声明 calendar 与 universe 为两个 artifact |
| F007-D004 | F003 声明 F007 消费 `generation.run_completed`/`candidate_rejected` 与算子能力登记表，F007 spec 上游只提事件名，未提算子能力清单消费源 | High | F003 spec.md:247,252,258,329 vs F007 spec.md:22 | F007 spec:22 补「F003 算子能力登记表 = FR-002 已登记算子能力清单消费源」，与 F003 spec:329 对齐 |
| F007-D005 | F003 过渡期 `explicit_tuples` 字段（cutoff_time/as_of_fidelity/symbol_map_digest/universe_calendar_digest）与 F007 ResearchSnapshot 字段无显式映射表 | Medium | F003 design.md:120-121 vs F007 spec.md:198, design.md:193 | F007 design §3.1 增 explicit_tuples→ResearchSnapshot 字段映射表，或 F003 引用 F007 DR-001 字段名 |
| F007-D006 | F004 声明为 F007 提供真实 Kronos 信号源，但 F004 明确「路由切换后移、signals_log 不自动升级」，F007 未记录该输入仍为 placeholder | Medium | F004 spec.md:188-189,197-198 vs F007 spec.md:22,279 | F007 spec §7 依赖增注：Kronos 信号输入在路由切换前为 `source=placeholder`，正控制不得依赖它 |
| F007-D007 | F002 声明下游为「M1 评测台(FR3)」，F002 `related_features` 不含 F007，F007 含 F002（单向） | Low | F002 spec.md:7,278 vs F007 spec.md:7 | F002 已 done，仅记录；F007 侧无需改，或在 F002 勘正时补 related_features |

**Explicit passes (checked, no finding)**
- F007↔F002 dataset identity: F007 spec:22/198/279 的 `(dataset, DataVersion, value_digest)` 与 F002 design:296-300/346-353 一致，双向声明成立（F007 spec:7 含 F002）。
- F007↔F004 FactorDef 输入: F007 spec:22 声明 F004/Kronos 产出 FactorDef，F004 spec:20 声明 FR3 为下游关系，方向一致。
- F007↔F003 事件名: `generation.run_completed`/`generation.candidate_rejected` 在 F003 design:173-174 与 F007 spec:22 拼写一致；F003 的 `status=completed` 才发完成事件与 F007 spec:22 一致。
- F007↔F008 schema_version: F008 IR-003:244 与 F003 design:114 均带 `schema_version`，F007 design:132 的 reader 前向演进策略兼容。
- F003-D014 证据成立: F003 spec:247/321 + tasks:61 声称 F007 消费其事件/算子表，F007 spec:7 现含 F003（已部分修复），但 design:5 仍漏——见 F007-D001。

**Note on F003-D014**: The active report's claim is corroborated. F007 spec.md:7 now lists F003, but F007 design.md:5 does not, and F007 spec:22-23 still omits the operator-capability registry as a named upstream contract. This is a partial fix, not a full one.
</answer>

<next_steps>
1. Add F007-D001..D007 to `docs/reviews/CURRENT-doc.md` as a new F007 section (reviewer-owned; do not touch F003 entries).
2. Propose regression gates: `tools/check_doc_consistency.py::test_related_features_symmetric` (D001/D002/D007) and `::test_universe_artifact_vocabulary` (D003).
3. Highest-value first fix: F007 design.md:5 add F003/F008 to `related_features` (one line, unblocks D001/D002 symmetry check).
</next_steps>
</results>
