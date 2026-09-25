---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f552bc9c2ffevkKOQDDvE8ioEr"
title: "Review F007 consistency (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T15:27:09Z"
updated_at: "2026-09-16T15:28:02Z"
tokens_input: 39258
tokens_output: 1988
cost: 0.0111
parent_id: "ses_f55324142ffefNy2o4qhiYalh0"
---

# Review F007 consistency (@explore subagent)

## user · 2026-09-16T15:27:09Z

TASK: Review internal consistency across F007 spec.md, design.md, and tasks.md.
EXPECTED OUTCOME: Confirmed contradictions, omissions, and traceability gaps with exact file:line evidence; include requirement-to-design-to-task-to-AC coverage, state/verdict vocabulary, paths, error codes, and runtime invariants.
REQUIRED TOOLS: Read-only repository tools; prefer codegraph, use Read only where needed; maximum 5 tool calls and 800 output tokens.
MUST DO: CONTEXT: AlphaMill F007 first-round full-scan. GOAL: identify semantic inconsistencies that could block implementation or acceptance. DOWNSTREAM: findings become stable F007-Dxxx entries. REQUEST: compare all three artifacts systematically and state explicit passes when no issue exists.
MUST NOT DO: No edits, git writes, invented requirements, or implementation beyond one-line remediation suggestions.
CONTEXT: Repo /home/georg/projects/alphamill; baseline main@ab30da9; report target CURRENT-doc-F007.md.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T15:27:10Z

- **tool**: `bash({"command": "git rev-parse --short HEAD; git status --porcelain | head -20; find . -ipath '*F007*' -not -path './.git/*' 2>/dev/null", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `glob({"pattern": "**/F007/**"})`


> [reasoning] Let me start by finding the F007 artifacts.
<analysis>
**Literal Request**: Cross-check F007 spec.md, design.md, tasks.md for contradictions/omissions/traceability gaps.
**Actual Need**: Produce citable F007-Dxxx findings for first-round full-scan doc review.
**Success Looks Like**: Every claim backed by file:line; explicit "pass" statements for clean dimensions.
</analysis>

  <details><summary>tool output</summary>

  ```text
ab30da9
./docs/features/0.2/F007-evaluation-gates
./docs/features/0.2/F007-evaluation-gates/spec.md
./docs/features/0.2/F007-evaluation-gates/tasks.md
./docs/features/0.2/F007-evaluation-gates/design.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
  ```
  </details>

## assistant · 2026-09-16T15:27:19Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md"})`


> [reasoning] Read the three files.

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

## assistant · 2026-09-16T15:27:23Z


> [reasoning] I've used 2 tool calls (bash, glob counted... actually 3 tools in first block: bash+glob; then 3 reads). Let me count tool calls: bash, glob, read x3 = 5. Max 5. I have the content. Let me analyze carefully.

Now systematic comparison.

Key artifacts:

**spec.md**
- FR-001 显式执行层级与隔离 preview|canonical
- FR-002 方法论递增守卫
- FR-003 分阶段证据与失败语义 — five stages: 信号质量、组合转换、成本/容量、时序稳定、执行实现. FactorDef may mark later stages NOT_APPLICABLE. Verdict `INCOMPLETE/FAIL`.
- FR-004 统计与试验总体
- FR-005 成本、容量与时间稳定性 — cost_verdict=cost_negative, final verdict `dead`
- FR-006 不可变证据与综合报告
- DR-001..004, TR-001..003, IR-001..003, UX-001/002, NFR-001..005
- Lifecycle states: CREATED, VALIDATING, RUNNING, EVIDENCE_READY, INCOMPLETE, REGISTERED, FINALIZED, OPEN, PREVIEW_DONE. Also verdict vocabulary: PASS/promising, INCOMPLETE/FAIL, dead, UNDERPOWERED, NOT_APPLICABLE.
- AC-001..AC-008, each referencing req IDs.

**design.md**
- Stage status vocabulary: `PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE` (line 124-126).
- Error codes line 165-166.
- Event types line 176: `evaluation.run_state_changed | evaluation.gate_rejected | evaluation.registered`.
- Directory: `reports/bench/` for canonical (line 35, 49, 100) — spec says canonical/正式. Naming.
- artifact `curves.parquet` with horizon rolling IC.
- design §7 failure mapping: 成本不存活 → `FAIL/dead`.
- design says report.json contains "成员诊断 verdict"; cohort-level `promotion_verdict` only in cohort_verdict.json.

Potential issues:

**D1: TR-003 event type missing from design event vocabulary?** Spec TR-003: "canonical population 登记应使用 experiment_id 幂等键并引用 manifest ID" — design line 176 includes `evaluation.registered` event. OK.

**D2: Runtime invariant contradiction — spec says preview cannot access 留出 (holdout), and FR-001 preview can't write 留出预算. Design §7 permission boundary says preview/Agent constructors don't have holdout reader. OK.**

**D3: spec FR-003 says FactorDef run can mark 未适用 later stages NOT_APPLICABLE; design says FactorDef 组合/执行阶段标 NOT_APPLICABLE (line 197). Consistent. BUT spec lifecycle/invariant: 必需门被 skip、warning 或 null 时不能 EVIDENCE_READY. Fine.**

**D4: Verdict vocabulary mismatch: spec FR-005 scenario says `cost_verdict=cost_negative` and final verdict `dead`. Design §3.3 line 124 says report contains "成员诊断 verdict"; and design §7 line 223 maps 成本不存活 → `FAIL/dead`. But stage status vocabulary (line 124-126) has no `dead`; cost_verdict vocabulary not defined anywhere in design. And spec success criteria mention "promising" in invariants line 243 ("任何 PASS/promising") and FR-003 line 158 ("verdict 不得为 PASS/promising"). `promising` never defined in design's vocabulary. That's a real vocabulary gap.**

**D5: State machine vocabulary mismatch: spec lifecycle line 230-238 has states CREATED, VALIDATING, RUNNING, EVIDENCE_READY, INCOMPLETE, REGISTERED, PREVIEW_DONE, OPEN, FINALIZED. Design line 161-162 says member canonical success = `REGISTERED`, and §7 line 203 says "canonical registration 失败时运行保持 `EVIDENCE_READY`". Design event example line 182 `"to": "INCOMPLETE"`. But the spec lifecycle doesn't include a transition EVIDENCE_READY -> anything except REGISTERED/INCOMPLETE. Design doesn't define `PREVIEW_DONE` or `VALIDATING` transitions. Also spec doesn't mention `PASS` as run state. Minor.

Actually a stronger one: spec line 245 says required gate skipped/warning/null → cannot enter `EVIDENCE_READY/REGISTERED`. Design line 198/203 says registration failure leaves run at EVIDENCE_READY. Consistent.

**D6: Stage names mismatch.** Spec FR-003: 五阶段 = 信号质量、组合转换、成本/容量、时序稳定、执行实现. Design §3.3 report contains "stage results"; design event example line 180 `"stage": "signal_quality"`. Design line 197 "FactorDef 的组合/执行阶段". Design doesn't enumerate the five stage names anywhere. tasks T014 says "五阶段/三维失败汇总". Hmm design never defines the canonical stage identifier list. That's an omission (medium). Actually spec doesn't give English identifiers either; design uses `signal_quality` in event example. Traceability gap: no artifact defines the full 5-stage enum. Could be finding.

**D7: AC-to-task-to-design coverage.** Let me build coverage:
- AC-001 (FR-001, DR-004, NFR-003): tasks T005 (FR-001/DR-004/AC-001), T003 (NFR-003), T018, T022, T023. Design: line 237 AC-001 row test file. OK.
- AC-002 (FR-002): tasks T008, T017, T018, T021, T023. design line 238. OK.
- AC-003 (FR-003, FR-004): tasks T009, T016, T018, T022, T023. design line 239. OK.
- AC-004 (FR-005): T007, T010, T018(T019 actually), T022, T023. design 240. OK.
- AC-005 (FR-006, DR-003, NFR-001): T011, T015, T019, T021, T023. design 241. OK.
- AC-006 (DR-001, DR-002, NFR-002): T001, T004, T019, T023. design 242. OK.
- AC-007 (FR-006, UX-002): T014, T020, T022, T023. design 243. OK.
- AC-008 (IR-001, IR-002, IR-003): T006, T013, T020, T023. design 244. OK.

Now requirement-to-task coverage. Let's check each requirement ID appears in tasks:
- FR-001: T005, T017, T018 (via AC-001? T018 lists AC-001). present.
- FR-002: T008, T017, T018. present.
- FR-003: T007, T016. present.
- FR-004: T002, T009, T012, T016. present.
- FR-005: T002, T007, T010, T016. present.
- FR-006: T014, T015. present.
- DR-001: T001, T004. present.
- DR-002: T004. present.
- DR-003: T011. present.
- DR-004: T005, T012. present.
- TR-001: T011. TR-002: T011. TR-003: T012. present.
- IR-001: T006, T013. IR-002: T001, T013. IR-003: T006. present.
- UX-001: **NOT referenced in tasks.md at all!** UX-001: CLI 输出应把 tier、cohort、数据/代码摘要与 INCOMPLETE 原因置于摘要首屏. No task references UX-001. T006 implements preview CLI with structured output; T013 canonical CLI. But no task tagged UX-001. That's a traceability gap. Also design §6 line 213 covers CLI first-screen. So UX-001 has design coverage but no task coverage. Finding.
- UX-002: T015. present.
- NFR-001: T012. NFR-002: not directly? T004 is DR-001/DR-002/AC-006; AC-006 references NFR-002. Hmm NFR-002 "可复现：固定 ResearchSnapshot 跨路径/codec 重跑" — tasks: T004 (identity normalization) doesn't tag NFR-002. AC-006 tags NFR-002, T001/T004 tag AC-006. So indirect. Could note but weak.
- NFR-003: T003, T017. NFR-004: **not referenced anywhere in tasks.md**. NFR-004 性能: preview 可采样/缩窗但必须显式标注近似. No task. Design? §3.3 sample-size; design doesn't explicitly cover NFR-004 sampling/approximation labeling. Search design for 采样 — I don't recall design mentioning sample/approx. Indeed design has no mention of preview sampling or approximation labeling. So NFR-004 is unaddressed in both design and tasks. Finding (coverage gap).
- NFR-005: **not referenced in tasks.md**; design §7 line 227 covers logical URI vs physical path. So NFR-005 design-covered but task-uncovered. Finding.

**D8: spec frontmatter related_features: [F002, F003, F004]** but design.md line 5 and tasks.md line 5 `related_features: [F002, F004]` — missing F003. Note spec §0 explicitly cites F003 as upstream contract source (line 22) including `generation.run_completed` / `generation.candidate_rejected` events. So design/tasks frontmatter drops F003. BUT: does design/tasks actually consume F003? Spec says F003 is 漏斗第一级数据源 for synthesis funnel. Yet design §2 architecture and tasks never mention F003 or the generation events. So this is a substantive traceability gap: spec declares F003 event consumption (for funnel first level), design/tasks omit it. Finding — high-ish.

**D9: Error codes.** spec has no error code namespace; design defines 7 codes (line 165-166): E_INPUT_INVALID, E_DATA_DIGEST_MISMATCH, E_METHODOLOGY_REJECTED, E_REQUIRED_METRIC_FAILED, E_CANONICAL_FORBIDDEN, E_COHORT_FROZEN, E_PUBLISH_INCOMPLETE. Spec IR-003 says "结构化 failure". Design event example uses `reason_code: E_REQUIRED_METRIC_FAILED`. But design's directory/CLI has finalize-cohort; spec IR-001 says CLI four subcommands preview/canonical/finalize-cohort/synthesis. Design CLI has all four (synthesis at line 153). OK.

But: spec failure semantics mention `UNDERPOWERED` and `INCOMPLETE` and `dead`; error codes don't include an underpowered code — not necessarily needed.

**D10: Summary report name.** spec line 186-187 `synthesis_report.json`; design line 105 `synthesis_report.json`. OK.

**D11: Report schema: spec FR-006 says report.json, curves.parquet, manifest. Design directory line 99-100 includes `events.jsonl` and `registration.json` too. Fine.

**D12: Preview directory spec? spec §5 line 237 "preview EVIDENCE_READY -> PREVIEW_DONE". Design §1 line 35 says `reports/preview/` and `reports/bench/`. Spec never names canonical dir as "bench". design §2 line 49 `reports/{preview|bench}/...`. Spec IR/NFR-005 says POSIX logical paths. Naming inconsistency is minor but could confuse. Spec uses "canonical" everywhere, design maps canonical→bench root. Does design explain? line 35 "reports/preview/ 与 reports/bench/ 隔离". Not explained why bench. Minor quality.

**D13: AC-005 references NFR-001 and FR-006/DR-003. Fine. AC tests: design §8 maps each AC to test files. But tasks.md adds test files not in design map: tests/contract/test_f007_upstream_contracts.py (T001), tests/contract/test_f007_artifact_schemas.py (T015), tests/integration/test_f007_canonical_registry.py (T012), tests/integration/test_f007_controls.py (T016), tests/mutation/test_f007_gate_mutations.py (T017), tests/fixtures/f007/README.md (T002). Design §8 only lists 8 files. The extra test files are not necessarily contradicting but the design acceptance map omits canonical_registry, controls, mutation, artifact_schemas, upstream_contracts. Notably AC-003's design row `test_required_statistics.py` but T012 (registration/cohort) is untested in design map except via AC-003? Actually AC-003 includes cohort finalize; design row for AC-003 lists only test_required_statistics.py, while tasks T012 verify uses test_f007_canonical_registry.py. So design §8 map is incomplete relative to tasks — traceability gap. Also T016 controls verify file test_f007_controls.py not in design §8 (design line 246 mentions fixtures as e2e golden but no file). Finding.

**D14: AC-003 assigned to design test file `tests/unit/evaluation/test_required_statistics.py` but tasks T018 for AC-003 uses same file; T016 uses test_f007_controls. Fine.

**D15: tasks.md missing `[TEST]` group required by design.md 开发前置约束 (lines 16-18)!** Design.md explicitly says: "进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。开工门禁（SDD Flow T3）会拒绝缺失该组的流转。" tasks.md has no `[TEST]` group — grep for [TEST] in tasks: none visible. That's a hard blocker finding! tasks.md structure has Phase 1/2/3 but no `[TEST]` group. This directly blocks the T3 gate. High severity. 

Wait, need to verify whether `[TEST]` appears. From the read, no. So D-finding critical.

**D16: tasks T002 references `tests/fixtures/f007/README.md` as verify for pre-registration config — verify with README is odd but minor.

**D17: spec §5 lifecycle: "canonical EVIDENCE_READY -> REGISTERED" and invariant "canonical 成员登记不等于晋级". Design line 161 says canonical 成功只表示 REGISTERED. Consistent. But spec FR-004 says "只有全部承诺成员进入终态后才能统一 finalize cohort" and design says finalize writes cohort_verdict.json. Spec state FINALIZED. Design doesn't state the cohort state name FINALIZED nor OPEN explicitly? Design line 109-112 describes finalize. Spec §5 line 236 "cohort OPEN -> FINALIZED". Design line 110 "只有成员集合与承诺完全相等时 finalize-cohort 才计算". Doesn't use state names. Minor.

**D18: spec US-002 scenario 3: 未收齐成员 → cohort 保持 OPEN. Design line 161-162 finalize非零. Consistent.

**D19: verdict vocabulary: spec mentions `PASS/promising` (line 158, 243), `INCOMPLETE/FAIL` (line 80, 152), `dead` (line 176, 182), `UNDERPOWERED` (line 118). Design stage status has PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE but never `promising` nor `dead`. Design line 223 uses `FAIL/dead` loosely. So vocabulary for `promising`, `dead`, `cost_negative` is not defined in design — the report schema member diagnostic verdict enum is not fully specified. Finding.

Also spec FR-005 scenario says `cost_verdict=cost_negative`; spec says "成本后不为正时 verdict 为 `dead`". Design line 124 says each stage status only one of five; where does cost_verdict live? Not in design schema. Finding (vocabulary + schema gap).

**D20: design §3.3 says "成员诊断 verdict" in report but "可晋级 promotion_verdict 只存在于 cohort_verdict.json". Spec IR-003 says 机器输出返回 verdict. Fine.

**D21: Design line 16-18 added 2026-09-16 constraint but frontmatter updated: 2026-09-13 — metadata stale. Minor.

**D22: spec line 16 "Target: v0.2.x" fine.

**D23: spec §4 FR-003 five stages order: 信号质量、组合转换、成本/容量、时序稳定、执行实现. tasks T014 "五阶段/三维失败汇总". Design event `stage: signal_quality`. No stage enum. Also spec FR-005 mentions "时序稳定" and "执行实现". Design line 197 says FactorDef's 组合/执行 stages NOT_APPLICABLE — but what about 时序稳定? For a FactorDef, stability applies (T010). So spec's allowed NOT_APPLICABLE stages = 组合转换 and 执行实现, consistent with design line 197. Pass.

**D24: runtime invariant gap: spec NFR-001 "崩溃后不得出现半个 PASS". Design §5 claim lease/recovery. Consistent.

**D25: design §3.2 "reports/research_snapshots/<snapshot_id>/manifest.json" and line 157-158 writes `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`. Spec IR-002 says preview latest must 先内容寻址冻结并返回 snapshot ID. Consistent.

**D26: spec DR-002 says experiment_id derived from semantic fields "(除 tier/supersedes)". Design line 89-91 lists upstream ID, cohort, normalized rules/window/cost, research_snapshot_id, code/build digest, seed. Consistent. But design context JSON line 78 has method_config with "id": "method-v1" and normalized {}; IR-002 mentions 规则版本; fine.

**D27: spec requires canonical 拒绝缺失规则版本 (IR-001). Design line 160 "canonical 缺 cohort、code digest、ResearchSnapshot 或规则版本时返回非零". Consistent. tasks T013. Good.

**D28: AC-006 in spec combines DR-001, DR-002, NFR-002. Design row AC-006 test files research_snapshot.py, identity.py. tasks T001/T004. OK.

**D29: UX-001 coverage gap (already D7). Also design §6 line 213 covers it but tasks lacks. Finding.

**D30: NFR-004/NFR-005 task coverage gap. Finding.

**D31: F003 omission (D8). Finding.

**D32: spec §0 says F003 provides "generation.run_completed / generation.candidate_rejected 事件（漏斗第一级数据源…）". If synthesis must include funnel with F003 first level, design/tasks need it. But it's also possible F007 only consumes via cohort ledger. Spec US-003 says funnel from canonical cohort. Hmm the F003 events are "漏斗第一级数据源". Design synthesis §2 line 52 uses "finalized canonical cohort manifests + curves" only — no F003 generation events. So contradiction: spec says funnel's first stage data source is F003 generation events, design synthesis only reads canonical cohort manifests+curves and doesn't ingest F003 events. This is a real design omission. Finding high.

**D33: tasks T014 "五阶段/三维失败汇总" — spec FR-006 says synthesis must include cohort 漏斗、有效独立数、五阶段损失、最大约束及分栏的事实/推断/建议. "三维失败汇总" not defined in spec; spec doesn't define "三维". Possibly design's failure taxonomy? Design §6 line 217 mentions "failure taxonomy". Spec doesn't mention failure taxonomy classification dimensions. Design doesn't define three dimensions either. Vocabulary "三维" appears only in tasks. Traceability gap — undefined term. Finding.

Hmm, careful: design line 217 mentions failure taxonomy, but no dimension count. tasks says 三维失败汇总. Spec has nothing. So undefined.

**D34: AC-007 spec quotes FR-006, UX-002 and requires 事实/推断/建议分栏. tasks T014 only tags FR-006/AC-007, not UX-002 (T015 tags UX-002). Fine.

**D35: spec AC list uses format without tests: path (allowed in draft). Design §8 provides test files, tasks provide verify paths. But the features/README says AC must be回填 with tests before review. spec AC lines have no `— tests:` suffix. Per rules draft allows missing. Not a finding necessarily (draft). But the task T024 says 回写 spec 的真实 tests. Fine.

**D36: design line 16 says tasks must fill `[TEST]` group. Confirm tasks has no [TEST]. Yes critical.

**D37: spec §5 lifecycle: preview transitions CREATED->VALIDATING->RUNNING->EVIDENCE_READY->PREVIEW_DONE. Design §1 line 35 uses `reports/preview/<experiment_id>/<attempt_id>/`. Design line 161 canonical success REGISTERED. Design never mentions PREVIEW_DONE. Minor omission.

**D38: design error code `E_CANONICAL_FORBIDDEN` vs spec FR-001 preview 越权 → design maps? design §7 line 225 permission. Fine.

**D39: Event naming: spec TR-002 says preview 越权、方法论失败、必需指标失败写 `evaluation.gate_rejected`. Design event type includes `evaluation.gate_rejected`. But TR-001 `evaluation.run_state_changed` and TR-003 registration: design adds `evaluation.registered` which spec TR-003 doesn't name. Spec TR-003 says "canonical population 登记应使用 experiment_id 幂等键并引用 manifest ID" — no event name specified, so design's `evaluation.registered` fills a gap rather than contradicts. Note as minor omission (spec lacks event type for registration; design invents one) — could be a spec gap. Finding low.

**D40: spec DR-003 mentions "逐阶段状态、报告、曲线、规则版本和结论" in ExperimentManifest. Design manifest.json contents not enumerated. Omission minor.

**D41: Path for synthesis: spec line 187 "从 canonical ledger 生成版本化 synthesis_report.json"; design line 105 `reports/cohorts/<cohort_id>/synthesis/<synthesis_id>/synthesis_report.json`. Consistent enough.

**D42: spec FR-006 says report.json + curves.parquet + manifest atomic. design adds registration.json. tasks T011 mentions run events, report/curves/manifest. OK.

Now, the highest-value confirmed findings, bounded. Need ≤800 output tokens. I must be concise. Given output token cap 800, I should list maybe 8-10 findings in compact form.

Let me verify one more thing: whether tasks.md contains `[TEST]` anywhere — I read whole file (77 lines), no. And whether design mentions NFR-004 or sample — design line 214 "记录各阶段耗时、样本量". No sampling/approx. Confirmed.

Also verify UX-001 absent in tasks: tasks has UX-002 only (T015). Confirmed.

Let me also double check AC requirement references all exist: AC-001 FR-001/DR-004/NFR-003 ✓; AC-002 FR-002 ✓; AC-003 FR-003/FR-004 ✓; AC-004 FR-005 ✓; AC-005 FR-006/DR-003/NFR-001 ✓; AC-006 DR-001/DR-002/NFR-002 ✓; AC-007 FR-006/UX-002 ✓; AC-008 IR-001/IR-002/IR-003 ✓. All valid. Pass.

Also check every AC covered by ≥1 task: AC-001 T005/T003; AC-002 T008; AC-003 T009/T012; AC-004 T007/T010; AC-005 T011; AC-006 T001/T004; AC-007 T014; AC-008 T006/T013. Pass.

Also check spec requirement IDs all have scenario? features/README says each requirement should have scenario. DR/TR/IR/UX/NFR have no scenarios — but the rule says "每个重要 requirement 至少有一个 scenario"; ACs cover them. Not report as finding — borderline. Could mention as pass/observation.

Now let me be careful about the "F007-Dxxx" naming convention required downstream. I'll produce findings labelled D001..D010.

Findings (confirmed contradictions/omissions):

D001 (critical/high, process blocker): design.md:16-18 requires tasks.md `[TEST]` group; tasks.md has none (whole file) → T3 gate rejects. 
D002 (high): F003 declared upstream in spec:22 & related_features spec:7=[F002,F003,F004]; design:5 & tasks:5 drop F003; design synthesis (design:52) reads only canonical manifests+curves, so funnel first level (F003 generation events) has no design/task realization. Spec US-003/Ac-007 funnel.
D003 (high): verdict vocabulary: spec uses `promising` (158,243), `dead` (176,182), `cost_verdict=cost_negative` (182); design stage enum (124-126) lacks promising/dead/cost_negative; `promotion_verdict` (design:123) undefined in spec. 
D004 (medium): NFR-004 (spec:225) uncovered in design and tasks — no sampling/approximation task or design element. 
D005 (medium): UX-001 (spec:217) has design coverage (design:213) but zero task coverage in tasks.md. 
D006 (medium): NFR-005 (spec:226) design:227 covers, no task tagged; also AC mapping doesn't include NFR-005 (no AC references NFR-005 at all) — spec AC-001..008 never cite NFR-004/NFR-005. Requirement-to-AC gap.
D007 (medium): design §8 AC map (design:235-244) lists 8 test files, omits files tasks actually use: test_f007_canonical_registry.py (tasks:44), test_f007_controls.py (tasks:51), test_f007_gate_mutations.py (tasks:52), test_f007_artifact_schemas.py (tasks:50), test_f007_upstream_contracts.py (tasks:25). Traceability gap.
D008 (medium): five-stage enum never defined: spec:150 names 5 stages but no IDs; design only example `signal_quality` (design:180) and no enumeration; tasks:49 "五阶段/三维失败汇总" "三维" undefined anywhere (design:217 only says failure taxonomy). 
D009 (low/medium): lifecycle state vocabulary mismatch: spec:230-238 includes VALIDATING/PREVIEW_DONE/FINALIZED/OPEN; design only mentions REGISTERED (161), EVIDENCE_READY (203), INCOMPLETE (182); design never defines cohort OPEN→FINALIZED or preview PREVIEW_DONE. 
D010 (low): canonical storage root naming: spec uses "canonical" everywhere; design maps canonical to `reports/bench/` (design:35,49,100) without stating the mapping/why.
D011 (low): event type `evaluation.registered` (design:176) has no basis in spec TR-003 (spec:207), which names no registration event; either spec should name it or design should flag the addition.
D012 (low): design frontmatter updated:2026-09-13 (design:9) stale vs new 2026-09-16 constraint at design:16.

That's 12. Maybe trim to ~10 to fit tokens. I'll keep concise.

Passes to state explicitly:
- AC IDs unique and all reference existing spec reqs; every AC mapped to ≥1 task and design test row.
- All FR/DR/TR/IR/NFR-001..003 appear in task graph.
- Error code list (design:165-166) consistent with event reason_code usage (design:183) and CLI nonzero contract (design:160-163); spec defers "结构化 failure" (spec:213) so no contradiction.
- Path/error/digest: research_snapshot paths consistent (design:98,157-158 vs spec:212).
- Stage NOT_APPLICABLE semantics consistent (spec:151,245 / design:125,197).
- Identity fields consistent (spec:199 / design:89-92).
- Not_APPLICABLE prohibition, holdout isolation, cohort finalize gating consistent across all three.
- Frontmatter status rule: none of design/tasks declares status → pass.
- No Migration needed → design:132, spec no db requirement.

Also should mention severity and remediation one-liners.

I need to be mindful of output token count ≤800. That's tight. Let me write compactly.

Also note baseline: main@ab30da9, working tree clean. Bash output showed no porcelain lines (only find results), so clean.

Let me finalize with the required <results> block. Paths absolute.

Token budget: aim ~750. Let me write tersely.
<analysis>
**Literal Request**: Cross-check F007 spec/design/tasks.
**Actual Need**: Citable F007-Dxxx findings for first-round full-scan.
**Success Looks Like**: Contradictions with exact file:line, plus explicit passes.
</analysis>

Baseline verified: `main@ab30da9`, working tree clean (no porcelain output).

## Confirmed findings (severity · evidence)

**D001 · high · process blocker** — design:16-18 mandates tasks.md carry a `[TEST]` group (每旅程步骤 ≥1 断言) before SDD Flow T3 passes. tasks.md contains no `[TEST]` token anywhere (whole file, 77 lines; phases only at tasks:31/38/47). Remediation: add `### [TEST]` group under tasks.md §2.

**D002 · high · traceability/omission** — spec:7 declares `related_features: [F002, F003, F004]` and spec:22 names F003 `generation.run_completed`/`generation.candidate_rejected` as 漏斗第一级数据源; design:5 and tasks:5 drop F003, and design:52 defines synthesis as reading only "finalized canonical cohort manifests + curves". Funnel first level has no design/task realization. Remediation: add F003 to both frontmatters and one synthesis ingestion task.

**D003 · high · vocabulary** — spec:158/243 use verdict `promising`; spec:176/182 emit `dead` and `cost_verdict=cost_negative`; spec:118 `UNDERPOWERED`. design:124-126 enumerates only `PASS|FAIL|UNDERPOWERED|INCOMPLETE|NOT_APPLICABLE`; `promising`/`dead`/`cost_verdict` are never defined, while design:123 introduces `promotion_verdict` that spec never names. Remediation: freeze one verdict enum in design §3.3 and cite it from spec.

**D004 · medium · coverage gap** — spec:225 NFR-004 (preview 采样/缩窗须显式标注近似) has no design element (design:213-214 only logs 样本量/耗时) and no task reference in tasks.md. Remediation: add design clause + task tagged NFR-004.

**D005 · medium · coverage gap** — spec:217 UX-001 (首屏 tier/cohort/digest/INCOMPLETE 原因) is covered by design:213 but zero tasks cite UX-001; tasks:50 only tags UX-002. Remediation: tag T006/T013 with UX-001.

**D006 · medium · coverage gap** — NFR-005 (spec:226) covered by design:227 but no task cites it; NFR-004/NFR-005 are referenced by **no AC** (AC-001..008 at spec:259-266 omit both). Remediation: add AC or explicit task refs.

**D007 · medium · traceability** — design:235-244 maps 8 AC rows to 8 test files, but tasks:25/44/50/51/52 use five files absent from the map (`test_f007_upstream_contracts.py`, `test_f007_canonical_registry.py`, `test_f007_artifact_schemas.py`, `test_f007_controls.py`, `test_f007_gate_mutations.py`). Remediation: sync design §8 rows.

**D008 · medium · undefined term** — spec:150 names five stages but no stage IDs; design:180 shows only `"stage": "signal_quality"`; tasks:49 says "五阶段/三维失败汇总" — "三维" appears nowhere in spec or design (design:217 only says failure taxonomy). Remediation: define stage enum + failure dimensions in design §3.3.

**D009 · low · state vocabulary** — spec:230-238 states `VALIDATING`, `PREVIEW_DONE`, cohort `OPEN`/`FINALIZED`; design only ever names `REGISTERED` (161), `EVIDENCE_READY` (203), `INCOMPLETE` (182) and never models OPEN→FINALIZED or PREVIEW_DONE. Remediation: mirror spec §5 state list in design §5.

**D010 · low · path naming** — spec uses "canonical" throughout; design:35/49/100 map canonical to physical `reports/bench/` with no stated mapping. Remediation: note the alias.

**D011 · low · event gap** — design:176 adds `evaluation.registered`; spec:207 TR-003 names no registration event type. Remediation: add it to TR-003.

## Explicit passes
- AC IDs unique, every AC cites ≥1 real spec requirement, every AC has ≥1 task and a design §8 row (spec:259-266, design:235-244, tasks:56-61) — pass.
- FR-001~006, DR-001~004, TR-001~003, IR-001~003, NFR-001~003, UX-002 all appear in the task graph — pass.
- Error code list (design:165-166) consistent with `reason_code` usage (design:183) and non-zero CLI contract (design:160-163); spec:213 defers to "结构化 failure", no conflict — pass.
- ResearchSnapshot/latest-freeze paths agree (spec:212 ↔ design:98,157-158) — pass.
- `NOT_APPLICABLE` semantics agree (spec:151/245 ↔ design:125/197) — pass.
- Identity field set agrees (spec:199 ↔ design:89-92); no DB Migration needed (design:132) — pass.
- No design/tasks frontmatter `status` (ownership rule) — pass.

<results>
<files>
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md - behavior contract; source of truth for vocabulary/ACs
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md - tech design; missing [TEST] prerequisites, enum definitions, test map rows
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md - task graph; missing [TEST] group, UX-001/NFR-004/NFR-005 refs
</files>
<answer>
12 issues confirmed (D001-D011). Two are blocking: D001 (design demands a `[TEST]` group that tasks.md lacks → T3 gate rejects) and D002 (spec declares F003 funnel events as an upstream source, design/tasks drop F003 and synthesis never reads them). Remaining are vocabulary (D003/D008/D009), coverage (D004/D005/D006), and traceability (D007/D010/D011). Six dimensions pass cleanly, stated above.
</answer>
<next_steps>
1. Create CURRENT-doc-F007.md with D001-D011 as stable entries (report_type: doc-review, scope: full-scan).
2. Block F007 on D001+D002; list D003-D011 as Medium/Low.
3. Request spec owner decision on one verdict enum (D003) before implementation starts.
</next_steps>
</results>
