---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f55795a4bffeLj8TpSfbAt9ebS"
title: "Write F003 review report (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T14:02:26Z"
updated_at: "2026-09-16T14:04:40Z"
tokens_input: 86187
tokens_output: 12594
cost: 0.0289
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Write F003 review report (@Sisyphus-Junior subagent)

## user · 2026-09-16T14:02:26Z

TASK: Create /home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md as the Chinese Round-1 full-scan doc-review report for F003. EXPECTED OUTCOME: One complete report in the exact review-convergence format, with YAML frontmatter issues and a single fixed 13-column Chinese findings table. Success means issue count equals severity_counts and all findings have exact evidence locations, suggested fixes, and proposed/needed regression gates. REQUIRED TOOLS: Read repository docs only as needed and use apply_patch to create this one file. MUST DO: Baseline main@a333394, date 2026-09-16, clean tree before report, prior_report none (F003 first review), scope full-scan, stop_condition_met false. Record existing gates: `.venv/bin/python tools/validate_spec_lifecycle.py` passes; `.venv/bin/python tools/check_doc_links.py` passes; CURRENT-doc.md is ignored by .gitignore:39. Use stable IDs F003-D001 through F003-D022 and these deduplicated findings/severities: D001 High factor_id includes run_seq so contradicts cross-run stable IDs (spec 65/259/305, design 104-105); D002 High REJECTED/FAILED terminal facts/reasons are not durably persisted although spec requires run records and design says run.json sole truth but absent on failure (spec 169-171/268-270, design 81/190/206-207); D003 High two-day gate incorrectly permits L2 despite ADR requiring two L1 weeks (spec 43/213/272-275, ADR0001 40-50); D004 High F003 smoke acceptance omits ADR0001's full funnel recording and reward-frequency sample obligations (spec 74/303, tasks 52-55/77, ADR0001 52-62); D005 High temporary explicit tuples omit ResearchSnapshot cutoff/as-of/symbol-map/universe semantics (spec 112/239/320/329, design 114, ADR0007 27-60); D006 High cross-sectional PIT mask implementation is not explicitly dependent on F008 digest/universe_at contract (tasks 59/80/94, F008 spec 243-244); D007 High process monkeypatch/write whitelist cannot prove the stronger no-egress/no-write-capability claim (spec 260/307, design 208/226); D008 High SIGTERM marks partial run completed and emits consumable completion contrary to complete atomic-run semantics (spec 92/269-270, design 163/190); D009 High generation objective omits PRD-required after-cost return (PRD 153-158, spec 197, design 58/110); D010 High pool is persisted as AlphaPoolDef/pool.json rather than a standard executable FactorDef meta-factor (spec 227-235, design 97/116); D011 High mandatory [TEST] journey group is absent (design 16-18, template tasks 57-61, F003 tasks 73-81); D012 High task evidence order/DAG permits tests before implementation and final state writeback without all gates: T016/T017 use smoke test before T018 implements gate, T019 writes decision before T032 archives evidence, T036 has no incoming closure edge (tasks 52-55/77/81/90); D013 High GPU scheduling has neither a verifiable FIFO/shared scheduling protocol nor a live owner for Kronos unload; flock only gives exclusion and F004 defers GPU work (spec 121/258/335, design 174-187/191, F004 tasks 70-73); D014 High F003 claims F007 consumes generation events/operator registry but F007 does not declare F003 upstream or carrier contract (spec 247/321, tasks 61, F007 spec 7/22-23); D015 Medium FactorDef persisted DTO/load contract omits how compute/meta are restored and conflicts with architecture FactorDef executable contract (design 81/94-106, architecture 254-270); D016 Medium IR-003 schema_version has no AC/task carrier and GenerationRun schema omits it (spec 253/295-307, design 102/110); D017 Medium AC assertions do not cover all referenced DR/TR/NFR clauses: AC003 DR001 run fields, AC005 TR002 event/query, AC009 DR002/DR003/TR001/pool reproducibility, AC010 persisted device/hostname, AC011 CLI file mismatch (spec 297-307, design 216-226, tasks 41-45/62/70/75-80); D018 Medium reproducibility lacks canonical config artifact/digest and deterministic RNG/device contract (spec 239/259/305, design 110/189); D019 Medium CLI syntax cannot construct all mandatory GenerationRequest fields and lacks explicit smoke implementation carrier/defaults (design 124-155, tasks 45/52-55/69); D020 Medium HypothesisDef omits PRD FR2.1 applicable state/regime field (PRD 153-154, spec 241, design 108); D021 Medium vendor hygiene AC requires per-line upstream diff verification but tasks preserve only commit/list, not a reproducible upstream baseline/patch or file digests (spec 149-155/298, tasks 31/49); D022 Low active-feature indexes drift: CLAUDE lists F004/F007, docs README says F003/F004/F007/F008, BACKLOG source set is F003/F007/F008 (CLAUDE 49-52, docs/README 36, BACKLOG 3-8). Counts: critical 0, high 14, medium 7, low 1. For categories use correctness except D011/D016/D017/D021 as test-coverage and D022 quality. Root cause root-cause for all except D022 symptom-patch. Origins: spec-drift for cross-doc contradictions D003-D006,D009,D013-D015,D020,D022; process-gap for D011,D012,D016,D017,D021; original-coding for D001,D002,D007,D008,D010,D018,D019. Reuse pattern tags where fitting: spec-internal-contradiction, cross-feature-contract-drift, spec-tasks-traceability-gap, gate-without-teeth, deferred-work-without-carrier, task-graph-order-contradiction; leave blank when none fits. Suggested fixes must be concrete and mention the full landing points. All statuses open. `fix_summary`, `resolved_round`, `tracked_task`, `disposition_reason` empty/quoted empty in YAML and `—` in table. Include body sections: 结论先行; 基线与范围; 检视门槛与证据; findings table; 裁决记录 (none); 已通过项 (structure, Q/DQ closure, current machine gates); Round-2 entry/stop conditions. State Round 1 scan complete but loop not converged; Round 2 is diff-only unless fixes touch >30%. MUST NOT DO: Do not modify F003 docs or any other file; do not commit/push; do not add findings not listed; do not mark any issue fixed/tracked/rejected; do not use a simplified table or omit frontmatter issue fields. CONTEXT: Repo /home/georg/projects/alphamill. Report is gitignored local-only process artifact under review-convergence. The user requested a comprehensive review document, not fixes.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T14:02:26Z

- **tool**: `bash({"command": "git -C /home/georg/projects/alphamill rev-parse --short HEAD && git -C /home/georg/projects/alphamill status --porcelain && git -C /home/georg/projects/alphamill branch --show-current && git -C /home/georg/projects/alphamill check-ignore -v docs/reviews/CURRENT-doc.md; ls /home/georg/projects/alphamill/docs/reviews/ 2>/dev/null; ls /home/georg/projects/alphamill/docs/"})`
- **tool**: `glob({"pattern": "docs/**/*.md"})`


> [reasoning] Let me start by understanding the repository structure and the relevant docs. I need to gather evidence from various files: CLAUDE.md, docs/README, BACKLOG, spec files, design files, ADR0001, ADR0007, PRD, architecture, tasks, F003/F004/F007/F008 specs.

Let me first check the baseline and clean tree, and read the key files. The task provides detailed findings, so I mainly need to verify locations and produce the report. Let me read the relevant docs to get exact evidence locations.

Let me be efficient. First, baseline check and structure.

  <details><summary>tool output</summary>

  ```text
a333394
main
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc.md
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

## assistant · 2026-09-16T14:02:34Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`


> [reasoning] Working tree appears clean (no porcelain output). Baseline main@a333394 confirmed. CURRENT-doc.md is ignored at .gitignore:39.

Now I need to read the relevant files to verify evidence locations. The task gives me the findings with spec/design/ADR line numbers. I should verify these locations exist to be accurate. Let me read key files: F003 spec.md, F003 design.md, F003 tasks.md, ADR0001, ADR0007, PRD, architecture, F008 spec/tasks, F007 spec, F004 spec/tasks, TEMPLATE tasks, CLAUDE.md, docs/README, BACKLOG.

Note: BACKLOG file wasn't in docs glob. Let me find it. Also CLAUDE.md.

Let me read the F003 files which are central. I'll use Read in parallel. But files may be large. Let me read F003 spec, design, tasks fully.

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

## assistant · 2026-09-16T14:02:41Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/validate_spec_lifecycle.py; echo \"---EXIT:$?\"; .venv/bin/python tools/check_doc_links.py; echo \"---EXIT:$?\""})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md", "offset": 30, "limit": 40})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md", "offset": 20, "limit": 48})`


> [reasoning] Working tree clean. Now I need to verify supporting docs: ADR0001 lines 40-62, ADR0007 lines 27-60, PRD lines 153-158, architecture lines 254-270, F008 spec 243-244, F007 spec 7/22-23, F004 tasks 70-73, TEMPLATE tasks 57-61, CLAUDE.md 49-52, docs/README 36, BACKLOG 3-8. And confirm existing gates pass.

Let me read those. I'll read targeted ranges. Let me also run the two gate commands. The task says record existing gates: validate_spec_lifecycle passes, check_doc_links passes. I should verify they pass (evidence). Let me run them.

Let me batch reads.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
---EXIT:0
check_doc_links: 相对链接全部可解析
---EXIT:0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md</path>
<type>file</type>
<content>
30: 3. **降级阶梯**：L1 = AlphaGen 表达式求值器 + 自写搜索（绕开 sb3/RL，保留 GPU 批量评估）；
31:    L2 = 纯 gplearn（1h/4h 重采样 + 自建算子 + 滚动 fitness）。
32: 4. **对照基线**：AlphaGen 仓库自带的 gplearn/ 与 dso/ 直接利用，不单独引入 gplearn 项目。
33: 
34: ## 降级切换判据
35: 
36: 冒烟闸门 time-box 已定（2 个工作日），但"何时降级"此前未成文——单人 time-box 最容易
37: 自我豁免。以下判据预写为**二元可测项**：到期未达标即切换，不允许"再给一天"；切换动作
38: 与触发原因记入当日 experiment manifest。降级不自动回切，回切须重开一轮冒烟 time-box。
39: 
40: **切到 L1（AlphaGen 表达式求值器 + 自写搜索，绕开 sb3/RL）**——满足任一条即触发：
41: 
42: - [ ] 第 2 个工作日结束时仍未跑通 1 个 PPO epoch（time-box 用尽）；
43: - [ ] 第 1 个工作日结束时，sb3/gymnasium 现代栈仍未跑通最小训练循环（依赖阻塞，判定
44:   vendor+RL 路线风险不可控，直接止损）；
45: - [ ] 第 2 个工作日结束时，feather→tensor 适配器未产出首个可做 RankIC 对齐的因子。
46: 
47: **从 L1 切到 L2（纯
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md</path>
<type>file</type>
<content>
20: 因此需要一个位于 DatasetVersion 与 ExperimentContext 之间的引用对象：它不复制 Parquet，
21: 只冻结一次研究实际使用的成员版本、值摘要和时间/映射语义。
22: 
23: ## 决策
24: 
25: 1. **DatasetVersion 继续独立演进**：F002 仍以 `(dataset, data_version)` 唯一标识单 dataset
26:    的不可变快照；不新增全湖全局 `data_version`，也不让一个 dataset 的失败作废其他版本。
27: 2. **新增不可变 `ResearchSnapshot`**：它是对多个有效 DatasetVersion 的内容寻址引用集合，
28:    由 `experiment_store` 负责构造和持久化，F002 只提供 manifest/digest reader。最小契约为：
29: 
30:    ```text
31:    ResearchSnapshot = {
32:      schema_version,
33:      snapshot_id,
34:      cutoff_time,
35:      members: {
36:        <dataset>: {data_version, value_digest, as_of_fidelity,
37:                    event_time_min, event_time_max}
38:    
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T14:02:47Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 140, "limit": 28})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 245, "limit": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md", "offset": 232, "limit": 20})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md", "offset": 1, "limit": 30})`


> [reasoning] Gates pass. Now let me read PRD 145-165, architecture 245-275, F008 spec 235-250, F007 spec 1-30, F004 tasks 60-80, TEMPLATE tasks 50-65, CLAUDE.md 40-60, BACKLOG 1-15. Also ADR0001 1-30 to confirm "two L1 weeks" D003. Actually D003 says "two-day gate incorrectly permits L2 despite ADR requiring two L1 weeks (spec 43/213/272-275, ADR0001 40-50)". Wait, ADR0001 lines 47-50: L1→L2 requires L1 for two consecutive weeks. Spec 272-275 lifecycle shows "L1 -> L2 纯 gplearn 基线 任一 L2 判据触发". Spec line 43 says "2 个工作日 time-box 内得到二元裁决". Spec 213 similarly. So D003 is that the smoke gate is a 2-day binary that could jump to L2, but ADR L2 requires 2 weeks of L1. Let me check ADR0001 lines 40-50 - yes 47-50.

Let me read remaining files.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
140:   TimescaleDB；失效快照必须被下游拒绝。
141: - **FR1.4 双口径与时间语义**：`close_adjusted` 用于收益，`close_raw` 用于成交模拟；所有时间使用
142:   UTC，并维护湖内 pair、研究 symbol 与 Freqtrade pair 的显式映射。
143: - **FR1.5 数据质量与扩容**：宇宙扩至 30~50 对前完成缺失、重复、未闭合 K 线和跨周期对账，
144:   保存 point-in-time 宇宙成员关系以避免幸存者偏差。历史回填约 4600 万行，是项目所有者负责的
145:   独立工作流，预计 1~2 周 wall-clock。
146: - **FR1.6 灾备**：数据库、Parquet manifest 与实验报告每日备份至 NAS，本地保留滚动副本并定期恢复演练。
147: - **FR1.7 多数据集研究快照**：多数据集实验必须先生成不可变 `ResearchSnapshot`，显式绑定每个
148:   `(dataset, data_version, value_digest)`、信息 cutoff、symbol map 与 point-in-time universe/calendar
149:   摘要；canonical 不得在运行时解析 latest 或按导出时间猜测全湖版本。
150: 
151: ### FR2 AI 因子工厂
152: 
153: - **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
154
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
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md</path>
<type>file</type>
<content>
232: - **DR-003**：`BackfillRun` 应当记录目标 pair 集合、窗口、限速参数、逐 pair 进度与行数、重试与失败原因、断点位置、起止时间与 hostname。
233: - **DR-004**：质量门结果应当持久化为逐 pair 的判定记录（各项指标值、阈值、verdict、原因码），失败记录与通过记录同样保留。
234: 
235: ### 事件 / Trace 需求
236: 
237: - **TR-001**：成员进出时，系统应当写入 `universe.member_changed`，payload 包含 pair、方向（进/出）、生效时间、原因与 `universe_id`。
238: - **TR-002**：回填进度与失败应当写入 `backfill.progress` / `backfill.failed`，可按 run 与 pair 查询。
239: 
240: ### API / 接口需求
241: 
242: - **IR-001**：CLI 应当提供 `discover`、`freeze`、`backfill`、`gate`、`show` 五个显式子命令；`backfill` 在宇宙未冻结时以非零退出拒绝。
243: - **IR-002**：宇宙台账 artifact 应当以固定 canonical 格式（列序、排序、UTF-8、LF）发布到湖元数据目录，路径按 digest 寻址；读取接口应当支持按 digest 加载并提供 `universe_at(T)` 语义查询。
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

## assistant · 2026-09-16T14:02:53Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md", "offset": 45, "limit": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md", "offset": 55, "limit": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md", "offset": 35, "limit": 30})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`


> [reasoning] Now read F004 tasks 60-80, F007 spec 7? Wait F007 spec line 7 is related_features. The task says "F007 does not declare F003 upstream or carrier contract (F007 spec 7/22-23)". Line 7 is `related_features: [F002, F004]` - missing F003. Line 22-23: upstream contract sources mention F002 and F004, not F003. Good.

Now TEMPLATE tasks 50-65, F004 tasks 60-80, CLAUDE.md 40-60, BACKLOG 1-15. Let me read.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md</path>
<type>file</type>
<content>
45: ### Phase 2：<下一个独立切片>
46: 
47: - [ ] T005 (`US-002`, `FR-003`): ... — verify: `path/to/test.ts`
48: 
49: 按需要增删 Phase；Phase 只能是本节的三级标题，任务 ID 必须全文件连续且唯一。
50: 
51: ## 3. 验证与验收任务
52: 
53: - [ ] T006 (`AC-001`): 运行对应单元/集成测试 — verify: `path/to/test.ts`
54: - [ ] T007 (`AC-002`): 运行 UI/E2E 或真实环境验证 — verify: <命令或证据路径>
55: - [ ] T008 (`AC-001`, `AC-002`): 运行项目统一质量门 — verify: `<project verify command>`
56: 
57: ### [TEST] 组：层 2 旅程验收轨（必填）
58: 
59: - [ ] T009 [TEST] (`AC-001`): <旅程场景>，先立红灯夹具、收尾全量跑 — verify: <E2E 命令/证据路径>
60: 
61: 从体验旅程派生（每旅程步骤 ≥1 条可执行断言）；**编写早、执行晚**——夹具在里程碑早期以红灯立起，收尾全量执行作为验收。开工门禁（SDD Flow T3）要求本组存在，缺失将拒绝流转。
62: 
63: - [ ] T010: 回写 spec 验收证据、活跃索引和状态 — verify: `<feature gate comma
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md</path>
<type>file</type>
<content>
55: - [x] T013 (`AC-001`, `AC-002`): 执行机容器证据第二轮（review R002/R004 载体）：构建 kronos-service（mock/real 双目标）与 data-collector 镜像成功（验证 `.dockerignore` 白名单不破坏构建、上下文不含重资产）、容器内 `import alphamill` 成功；`ALPHAMILL_INTEGRATION=1` 重跑 F004 容器套件（含 compose config 双向断言、缺资产 exited+非零退出码、real 全链）并回写证据（hostname + device） — verify: 三个构建退出码 0 + `docker run --rm <镜像> python -c "import alphamill"` 退出码 0 + `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f004_real_profile.py tests/integration/test_f001_kronos_smoke.py -q` 全绿
56: 
57: ## 4. 依赖与并行关系
58: 
59: - `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/CLAUDE.md</path>
<type>file</type>
<content>
35: - 平台：Windows 11 宿主 + WSL2（Ubuntu 26.04，docker-ce，非 Docker Desktop）；docker-compose 自 quant-crypto 迁入
36: - 机器边界（架构 §7.1，事实源 env-manager `data/fleet.json`）：开发机 `qiaozhi-gp`/`gp-wsl`（AMD iGPU，**无 NVIDIA**）只跑编码/单元测试/`tools/verify.py`；集成与 GPU 证据一律在执行机取。执行机同一时刻只有一台，承载全部运营与批处理（TimescaleDB/采集/导出/dry-run/监控/Kronos 常驻/挖掘训练）——当前 `qiaozhi-lt`（Win11+WSL2，RTX 4060 Laptop 8GB），成熟后整体迁移至 `qiaozhi-lab`（原生 Ubuntu 26.04，RTX 5070 Ti 16GB，Blackwell sm_120）；开发机上的 skip 不算证据
37: 
38: ## 开发约定
39: 
40: - 开发流程见 `docs/SOP.md`。
41: - Feature 记录见 `BACKLOG.md` 和 `docs/features/`；新建 feature 从
42:   `docs/features/TEMPLATE/` 复制三件套，状态规则见 `docs/features/README.md`。
43: - 质量门禁：统一入口 `python3 tools/verify.py`（串联文档门禁与测试；技术栈落地后扩展 lint/
44:   typ
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

## assistant · 2026-09-16T14:02:58Z

- **tool**: `write({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md", "content": "---\nreport_type: doc-review\nround: 1\ndate: 2026-09-16\nprior_report: none\nscope: full-scan\nstop_condition_met: false\nseverity_counts: {critical: 0, high: 14, medium: 7, low: 1}\nissues:\n  - id: F003-D001\n    title: \"factor_id 含 run_seq，跨 run 变动，与「相同 factor_id 集合」矛盾\"\n    severity: high\n    category: correctness\n    root_cause: root-cause\n    origin: original-coding\n    pattern_tag: \"spec-interna
…[truncated])`


> [reasoning] I have all needed evidence. Let me verify a few specifics to ensure accuracy:

D001: spec 65/259/305, design 104-105. spec line 65: scenario "then 得到完全相同的 factor_id 集合". spec 259 NFR-003. spec 305 AC-009. design 104-105: definition_digest excludes run_id/created_at; factor_id includes run_seq `_r<run_seq>_`. Yes. Cross-run stable IDs contradicted since factor_id includes run_seq.

D002: spec 169-171 (Scenario 绑定失效: 拒绝原因写入运行记录), spec 268-270 (lifecycle REJECTED/FAILED), design 81 (run.json sole truth), 190 (非受控异常 FAILED 时 run.json 不写出), 206-207. Yes.

D003: spec 43, 213, 272-275; ADR0001 40-50. Yes.

D004: spec 74/303, tasks 52-55/77, ADR0001 52-62. ADR0001 52-62 = M2 冒烟验收 with two obligations (funnel counting, reward frequency). spec 74 independent test checks four criteria; spec 303 AC-007. tasks 52-55 T016-T019. Yes.

D005: spec 112/239/320/329, design 114, ADR0007 27-60. Yes.

D006: tasks 59/80/94, F008 spec 243-244. F008 IR-002 universe_at(T), IR-003 consumes by F003. Yes.

D007: spec 260/307, design 208/226. Yes (egress guard process-level, not kernel).

D008: spec 92/269-270, design 163/190. spec line 92: US-003 scenario 1 count ≥50 and counts written to GenerationRun. spec 269-270 lifecycle RUNNING→COMPLETED atomic, RUNNING→FAILED. design 163 run_completed event, 190 SIGTERM status=completed + termination=early. Yes.

D009: PRD 153-158, spec 197, design 58/110. PRD FR2.3 includes 成本后收益 (after-cost return). spec 197 objective omits after-cost return. design 58 objective.py turnover penalty/reachability. design 110 GenerationRun objective fields. Yes.

D010: spec 227-235 (FR-007 协同池导出 meta-factor), design 97/116. design 97 pool.json, 116 AlphaPoolDef. Yes - pool persisted as AlphaPoolDef/pool.json rather than standard executable FactorDef meta-factor.

D011: design 16-18, template tasks 57-61, F003 tasks 73-81. Yes - [TEST] group absent.

D012: tasks 52-55/77/81/90. T016/T017 use smoke test before T018 implements gate (line 52-54): T016 verify test_f003_smoke_gate.py, T017 verify test_f003_ic_parity.py, T018 implements. T019 writes decision before T032 archives evidence (line 55 vs 77). T036 no incoming closure edge (line 81; dependency section 83-95 has no edge into T036). Yes.

D013: spec 121/258/335, design 174-187/191, F004 tasks 70-73. spec 121 FIFO single slot, spec 258 NFR-002, spec 335 decision. design 174-187 flock, 191 Kronos unload belongs to F004. F004 tasks 70-73 GPU passthrough deferred. Yes.

D014: spec 247/321, tasks 61, F007 spec 7/22-23. F007 spec line 7 related_features [F002, F004] (no F003), lines 22-23 upstream contract F002 + F004. Yes.

D015: design 81/94-106, architecture 254-270. design 81 factors/<factor_id>.json truth, 102 FactorDef persisted fields (no compute field), architecture 254-270 FactorDef includes compute Callable. Yes.

D016: spec 253/295-307, design 102/110. IR-003 schema_version. design FactorDef has schema_version:1 but GenerationRun (110) omits schema_version. AC list 297-307 no schema_version AC. Yes.

D017: spec 297-307, design 216-226, tasks 41-45/62/70/75-80. AC coverage gaps: AC003 DR001 run fields, AC005 TR002 event/query, AC009 DR002/DR003/TR001/pool reproducibility, AC010 device/hostname, AC011 CLI file mismatch. Yes.

D018: spec 239/259/305, design 110/189. Reproducibility config digest/RNG. Yes.

D019: design 124-155, tasks 45/52-55/69. CLI syntax. Yes.

D020: PRD 153-154, spec 241, design 108. HypothesisDef omits 适用状态 (applicable state/regime). PRD FR2.1 records 适用状态. spec DR-003 omits. design 108 HypothesisDef fields omit. Yes.

D021: spec 149-155/298, tasks 31/49. vendor hygiene: spec FR-002 requires every modified line annotated; AC-002 test. tasks T003 clone and record commit, T013 vendor with per-change annotation. But "per-line upstream diff verification but tasks preserve only commit/list, not a reproducible upstream baseline/patch or file digests". Yes.

D022: CLAUDE 49-52 (lists F004/F007 only), docs/README 36 (says F003/F004/F007/F008), BACKLOG 3-8 (F003/F007/F008). Wait, docs/README line 36: let me check. In docs/README the matrix line "非 done Feature 派生索引 | `../BACKLOG.md` | 活跃 feature 索引（当前 F003/F004/F007/F008）". The read shows line 36 area. Yes it says F003/F004/F007/F008. CLAUDE lists only F004/F007. BACKLOG lists F003/F007/F008. So drift.

Now counts: critical 0, high 14 (D001-D014), medium 7 (D015-D021), low 1 (D022). Total 22. Good.

Categories: correctness except D011, D016, D017, D021 = test-coverage; D022 = quality.
Root cause: root-cause all except D022 = symptom-patch.
Origins: spec-drift for D003-D006, D009, D013-D015, D020, D022. process-gap for D011, D012, D016, D017, D021. original-coding for D001, D002, D007, D008, D010, D018, D019.

Let me verify that origins cover all 22:
- D001 original-coding
- D002 original-coding
- D003 spec-drift
- D004 spec-drift
- D005 spec-drift
- D006 spec-drift
- D007 original-coding
- D008 original-coding
- D009 spec-drift
- D010 original-coding
- D011 process-gap
- D012 process-gap
- D013 spec-drift
- D014 spec-drift
- D015 spec-drift
- D016 process-gap
- D017 process-gap
- D018 original-coding
- D019 original-coding
- D020 spec-drift
- D021 process-gap
- D022 spec-drift
Count spec-drift: D003,4,5,6,9,13,14,15,20,22 = 10. process-gap: D011,12,16,17,21 = 5. original-coding: D001,2,7,8,10,18,19 = 7. Total 22. ✓

Pattern tags: use fitting ones: spec-internal-contradiction, cross-feature-contract-drift, spec-tasks-traceability-gap, gate-without-teeth, deferred-work-without-carrier, task-graph-order-contradiction; blank when none fits.

Assign:
- D001 factor_id run_seq contradiction: spec-internal-contradiction
- D002 terminal facts not persisted: gate-without-teeth? Hmm. It's about durable persistence of failure records. Could be spec-internal-contradiction (spec requires run records but design says run.json sole truth absent on failure). Actually cross-doc = spec-internal-contradiction? The tag "spec-internal-contradiction" fits contradictions within spec/design. I'll use spec-internal-contradiction.
- D003 two-day gate permits L2: spec-internal-contradiction (spec vs ADR). Use spec-internal-contradiction.
- D004 smoke acceptance omits ADR obligations: gate-without-teeth
- D005 explicit tuples omit ResearchSnapshot semantics: cross-feature-contract-drift (ADR0007 vs F003)
- D006 PIT mask depends on F008: cross-feature-contract-drift
- D007 monkeypatch can't prove no-egress: gate-without-teeth
- D008 SIGTERM partial completed: spec-internal-contradiction
- D009 objective omits after-cost return: spec-internal-contradiction (PRD vs spec)
- D010 pool not FactorDef: spec-internal-contradiction? It's design vs spec/architecture. cross-feature-contract-drift? Hmm. Use spec-internal-contradiction.
- D011 [TEST] group absent: spec-tasks-traceability-gap
- D012 task order/DAG: task-graph-order-contradiction
- D013 GPU scheduling no verifiable protocol/no live owner: deferred-work-without-carrier
- D014 F007 doesn't declare F003 upstream: cross-feature-contract-drift
- D015 FactorDef DTO/load contract: spec-internal-contradiction
- D016 IR-003 schema_version no AC/task carrier: spec-tasks-traceability-gap
- D017 AC coverage gaps: spec-tasks-traceability-gap
- D018 reproducibility lacks canonical config/digest: gate-without-teeth
- D019 CLI can't construct all fields: spec-tasks-traceability-gap
- D020 HypothesisDef omits applicable state: spec-internal-contradiction (PRD vs spec/design)
- D021 vendor hygiene AC exceeds task evidence: gate-without-teeth
- D022 index drift: cross-feature-contract-drift? It's index drift. Could be cross-feature-contract-drift or blank. The task says leave blank when none fits. Index drift is a documentation-index drift. I'll use cross-feature-contract-drift. Hmm, maybe better blank. But "cross-feature-contract-drift" is about feature contracts. Index listing drift isn't contract. I'll leave D022 pattern_tag blank.

Actually let me reconsider D001: factor_id in design includes run_seq but spec says same factor_id set across reruns. That's design contradicting spec = spec-internal-contradiction. OK.

Now I need to be careful: the finding text for D002 says "REJECTED/FAILED terminal facts/reasons are not durably persisted although spec requires run records and design says run.json sole truth but absent on failure". Pattern: gate-without-teeth? The core is that rejection reasons aren't persisted, so evidence gate weak. But "spec-internal-contradiction" is also apt. I'll pick spec-internal-contradiction.

Let me now also confirm the task says "Reuse pattern tags where fitting" and "leave blank when none fits". Good.

Now, evidence locations need to be exact. I'll provide location field like `spec.md:65,259,305; design.md:104-105`. The task says "all findings have exact evidence locations". I'll use relative paths for clarity, e.g., `docs/features/0.2/F003-alphagen-vendor/spec.md:65,259,305`.

Now the YAML frontmatter has an issues list where each issue needs fields: id, title, severity, category, root_cause, origin, pattern_tag, status, tracked_task, fix_summary, regression_test, suggested_fix, disposition_reason, location, first_seen_round, resolved_round. The task says `fix_summary`, `resolved_round`, `tracked_task`, `disposition_reason` empty/quoted empty in YAML and `—` in table.

regression_test: the task says "proposed/needed regression gates" - The frontmatter regression_test field is typically path::test_name or empty待补. But task says "all findings have ... proposed/needed regression gates." Hmm. The findings description includes evidence and suggested fixes. Should regression_test be filled with proposed gate? Review-convergence format: regression_test is the gate that locks it; while open it can be "留空待补". But task explicitly asks for "proposed/needed regression gates" in success criteria. Let me interpret: provide the proposed regression gate (the test file/check that should lock the fix) in regression_test even though not yet implemented? The header comment says "regression_test: <path::test_name 或留空待补>". The task's MUST DO says "suggested fixes must be concrete and mention the full landing points." And success means "all findings have exact evidence locations, suggested fixes, and proposed/needed regression gates."

I think the safest is to fill `regression_test` with the proposed test/gate for each finding. But is that semantically right? In the format, `regression_test` is the actual regression test that locks the fix (evidence). For open findings, it's normally empty. But the task explicitly wants proposed/needed regression gates. However, the MUST DO also says `fix_summary`, `resolved_round`, `tracked_task`, `disposition_reason` empty — notably it does NOT say regression_test empty. So regression_test should be filled with proposed gates. I'll fill it with a descriptive proposed gate. Given "proposed/needed", I can prefix with a proposed marker, e.g. `proposed: tests/...::test_...`. Hmm, but format expects path::test_name. I'll use `待建: tests/...` or just the path::test_name. To be safe and explicit, I'll write e.g. `tests/unit/test_f003_factor_identity.py::test_factor_id_stable_across_runs (待建)`. Actually maybe cleaner: `proposed:tests/...::test_...`. Let me use `proposed: <path>::<test_name>`.

Hmm, but this is a doc-review (report_type: doc-review), not code-review. The closure evidence for doc review is "文档被改+链接/格式检查通过". So regression_test for doc findings could be a machine gate like `tools/validate_spec_lifecycle.py` or a new lint. The task says "proposed/needed regression gates". For doc-review, gates would be doc checks. Let me think.

Given this is a doc-review report, the "regression gate" for each finding should be a doc-level check that would fail if the finding regresses. Many findings are cross-doc contradictions; the proposed gate could be a new consistency checker script. I'll propose concrete gates:
- For contradictions, propose extending a checker: `tools/check_doc_consistency.py::test_...` or a specific existing checker.
- But better to be concrete per finding.

Actually, re-reading: the task's success criterion: "all findings have exact evidence locations, suggested fixes, and proposed/needed regression gates." I'll fill regression_test with a proposed gate per finding. Since this is doc-review and these are doc issues, the gate is often "document amendment + checker". I'll phrase them as `proposed:<gate>`.

Hmm, but frontmatter field `regression_test` is a single value. I'll put the proposed gate string. Fine.

Let me now design suggested_fix for each finding, concrete with full landing points. I need to write them in Chinese (report is Chinese). The table columns are fixed Chinese: | ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |

13 columns. Good.

Now suggested fixes must be concrete and mention full landing points. Let me draft each.

D001: 修复建议: 让 `factor_id` 跨 run 稳定：design §3 把 `factor_id = <generator>_<definition_digest[:12]>`（剔除 `run_seq`），运行归属改由 `run_id`/`GenerationRun.counts` 承载；同步修订 spec NFR-003、US-001 场景 2（spec 65/259/305）与 AC-009 断言，并让 AC-001/AC-009 测试锁 `factor_id` 跨 run 相等。落点：`design.md:104-105`、`spec.md:65,259,305`、`tasks.md T007/T028`。

D002: 让 REJECTED/FAILED 的运行事实与原因持久化到运行目录内一个原子可见的文件（如 `rejection.json` / `failure.json`），与 design:81「run.json 是运行事实唯一真相源」不冲突：design §3/§5 明确 REJECTED/FAILED 也写一份终态 manifest（含 status/termination/触发原因/时间戳）；spec 生命周期 268-270 与 FR-003 场景 171 的「拒绝原因写入运行记录」据此对齐；AC-003/AC-011 加断言。落点 design:81,190,206-207; spec:169-171,268-270; tasks T008/T009/T027。

D003: 把 spec 43/213/272-275 的降级阶梯改为忠实映射 ADR-0001 40-50：2 日 time-box 只产出 L0 锁定或 L1 降级；L1→L2 必须由「L1 连续 2 周每周入评测台候选 <50」或「连续 2 周零候选通过无前视审计」触发，不允许 2 日窗口直达 L2；同步 US-002 场景、FR-006、AC-007 与 design §5/§10。落点 spec:43,213,272-275; design:222 (AC-007).

D004: AC-007 与 tasks T016-T019/T032 纳入 ADR-0001 52-62 的两条冒烟记账义务：漏斗逐级计数自第一天入库、奖励频率维度抽查（换手/≥30 笔 90 天可达性），判据与抽查记录进当日冒烟 manifest；spec US-002 独立测试 74 与 AC-007 303 补两条判据。落点 spec:74,303; tasks:52-55,77; ADR0001:52-62.

D005: 过渡期显式元组绑定补齐 ADR-0007 的最小语义：design §3 `binding.explicit_tuples` 增加 `cutoff_time`、`as_of_fidelity`、`symbol_map_digest`、`universe_calendar_digest`（或声明过渡态不保证的字段并标注降级）；spec DR-001/依赖 320/决策表 329 同步说明与 F007 ResearchSnapshot 的字段映射。落点 spec:112,239,320,329; design:114; ADR0007:27-60.

D006: 在 F003 design §2/§5 与 tasks T020 明确 `lake_tensor` 的 PIT 掩码依赖 F008 的 `universe_at(T)` 与 ledger digest（F008 IR-002/IR-003），声明 F008 落地前用现有 6 对 universe 的过渡契约；tasks §4 增加 `F008.IR-002 -> T020` 边；F003 spec 依赖 320 与 F008 IR-002/IR-003 互相引用。落点 tasks:59,80,94; F008 spec:243-244.

D007: 把 NFR-004/AC-011 的强断言降级为可证明的弱断言，或补强实现：design §7 明确 egress guard 只证「进程内 socket 构造被替换」而不证「无网络能力」，AC-011 断言限定为 monkeypatch 生效 + 白名单拒绝；若要保留「无 egress」结论则引入 netns/容器隔离并登记为实现任务。落点 spec:260,307; design:208,226; tasks T011.

D008: design §5 优雅停机改为 `status=partial`（或 `interrupted`）+ 终态 manifest + 不写 `run_completed`；仅完整原子运行写 `status=completed` 与 `run_completed`；spec 生命周期 269-270 与 TR-001 同步；AC 加 SIGTERM 不进 consumable 完成态的断言。落点 spec:92,269-270; design:163,190.

D009: objective 与 GenerationRun.objective 补「成本后收益」项：design §2 objective.py、§3 GenerationRun objective 字段加成本门/after-cost 参数（如 `cost_model`、`min_after_cost_return`），spec FR-005 197 与 PRD FR2.3 157 对齐；AC-006 断言奖励/预筛同时含成本后收益。落点 PRD:153-158; spec:197; design:58,110.

D010: 把协同池持久化为标准可执行 FactorDef meta-factor（`compute` 闭包按成员 FactorDef 与权重重算）而非仅 `AlphaPoolDef/pool.json`：design §3/§4 将 `pool.json` 定义为 FactorDef（generator=`pool` 或 `meta`）并保留 AlphaPoolDef 作为内部成员描述；spec FR-007 227-235 与 architecture §4.1 对齐；AC-008 断言池是可执行 FactorDef。落点 spec:227-235; design:97,116; architecture:254-270.

D011: tasks.md 第 3 节补 `### [TEST] 组：层 2 旅程验收轨`，从 US-001/US-002/US-003 每旅程步骤派生 ≥1 可执行断言（早编写、晚执行），覆盖接口可复现、二元裁决、池导出；否则 SDD Flow T3 拒绝流转。落点 design:16-18; TEMPLATE tasks:57-61; F003 tasks:73-81.

D012: 重排 tasks 依赖与顺序：T018（闸门判定器）先于 T016/T017（判据实跑）；T032 归档证据先于 T019 回写裁决；为 T036 增加入边 `T030/T031/T032/T033/T034/T035 -> T036`；§4 依赖列表同步。落点 tasks:52-55,77,81,90.

D013: 在 design §5 补可验证的调度协议（FIFO 序号/等待超时/持锁与释放的状态记录）与「Kronos 卸载」的 live owner：要么在 F003 tasks 增卸载/等待编排任务，要么在 F004 tasks 增对应任务并登记跨 feature 边；F004 已把 GPU 直通后移（tasks 70-73），F003 需明确未被满足时 FIFO 如何证明。落点 spec:121,258,335; design:174-187,191; F004 tasks:70-73.

D014: F007 spec frontmatter `related_features` 增加 F003，并把 F003 的 `generation.*` 事件、算子能力登记表、协同池列为上游 Contract；F003 spec 247/321 与 tasks T022（导出能力清单给 F007）对齐；或反向在 F003 声明该契约的交付任务并让 F007 消费。落点 spec:247,321; tasks:61; F007 spec:7,22-23.

D015: design §3 FactorDef DTO 补 `compute` 的加载/恢复契约（如何由表达式与 feature_map 重建闭包、注册到哪个执行入口）与 `meta` 的规范字段，或明确 FactorDef 持久化 DTO 与 architecture §4.1 可执行 FactorDef 是两个对象并给转换函数；AC-001/AC-004 断言加载后可执行。落点 design:81,94-106; architecture:254-270.

D016: 为 IR-003 的 `schema_version` 增加 AC 与任务载体：GenerationRun manifest 也写 `schema_version`（design:110），spec 295-307 补 AC/断言，tasks 增 `schema_version` 持久化与拒绝未知版本的任务。落点 spec:253,295-307; design:102,110.

D017: 为 AC 补齐被引用但未覆盖的 DR/TR/NFR 断言：AC-003 加 DR-001 运行字段；AC-005 加 TR-002 事件可查；AC-009 加 DR-002/DR-003/TR-001/池可复现；AC-010 加持久化 device/hostname；AC-011 修正 CLI 文件命名不一致（`test_f003_cli_contract.py` vs design 226 `test_f003_boundaries.py`）。落点 spec:297-307; design:216-226; tasks:41-45,62,70,75-80.

D018: 补 canonical config artifact 与 digest（配置摘要内容寻址并写 `run.json`）及确定性 RNG/device 契约（seed 派生、torch 确定性开关、CPU/GPU 差异处理）；NFR-003/AC-009 断言加 config digest 与确定性声明。落点 spec:239,259,305; design:110,189.

D019: design §4 CLI 表补全 `GenerationRequest` 全字段的构造路径（window/config/quota 如何从 CLI 传入或给默认），并给 `smoke` 一个显式实现任务与默认值；tasks 增 smoke 子命令实现任务与默认 config。落点 design:124-155; tasks:45,52-55,69.

D020: HypothesisDef 补 `applicable_state`/`regime` 字段：spec DR-003 241 与 design HypothesisDef 108 增该字段并在 catalog/自动候选里填默认；AC-009 断言字段存在；与 PRD FR2.1 153-154 对齐。落点 PRD:153-154; spec:241; design:108.

D021: vendor 卫生 AC-002 要求逐行上游差异比对，但 tasks T003/T013 只留 commit 与清单：要么补「vendor 时冻结上游基线快照/补丁文件与逐文件 digest」任务，要么把 AC-002 降为「记录 commit + 有标注即通过」并声明；建议前者，落点 spec:149-155,298; tasks:31,49.

D022: 同步三处活跃 feature 索引：CLAUDE.md 49-52 补 F003/F008，docs/README 36 与 BACKLOG 3-8 对齐为 F003/F004/F007/F008（或统一由脚本派生），并在 CLAUDE 维护说明里加漂移检查。落点 CLAUDE:49-52; docs/README:36; BACKLOG:3-8.

These are concrete. Now, regression gates (proposed). Given doc-review, I'll propose gates. Some can reuse existing: `tools/validate_spec_lifecycle.py`, `tools/check_doc_links.py`. But those already pass; they don't lock these findings. The task wants "proposed/needed regression gates", so propose new/updated gates. I'll write e.g.:

- D001: `待建 tools/check_f003_doc_consistency.py::test_factor_id_stable_across_runs`
- D002: `待建 ...[::test_terminal_facts_persisted]`
- etc.

But a single generic checker isn't great. Better: for each, propose the gate that would catch regression. Since doc review, many findings can be locked by a doc-consistency test or by updating the AC/task so the eventual code test covers it. I'll propose the code-level regression test that will lock the fix at the spec/design/tasks level, e.g. `tests/...::test_...` marked 待建. Hmm.

Actually the cleanest interpretation: for a doc-review finding, the regression gate is the doc/CI mechanism that will fail if the doc regresses. I'll propose per-finding gate strings, mixing:
- New doc-consistency check: `tools/check_doc_consistency.py::<case>` (待建)
- Or AC test: `tests/...::test_...` (待建)
- Or existing gate that must be extended.

I'll write them as `proposed:<path>::<name>`.

Let me define a set of proposed checker cases. I'll create one proposed script `tools/check_doc_consistency.py` with per-finding test names. That is plausible and concrete. Plus some use pytest AC tests. Let me assign:

- D001: proposed:tools/check_doc_consistency.py::test_factor_id_has_no_run_seq
- D002: proposed:tools/check_doc_consistency.py::test_terminal_run_facts_persisted
- D003: proposed:tools/check_doc_consistency.py::test_tier_ladder_matches_adr0001
- D004: proposed:tools/check_doc_consistency.py::test_smoke_obligations_linked
- D005: proposed:tools/check_doc_consistency.py::test_explicit_tuple_fields_match_adr0007
- D006: proposed:tools/check_doc_consistency.py::test_pit_mask_depends_on_f008_universe_at
- D007: proposed:tools/check_doc_consistency.py::test_egress_claim_matches_guard_strength
- D008: proposed:tools/check_doc_consistency.py::test_sigterm_not_completed
- D009: proposed:tools/check_doc_consistency.py::test_objective_includes_after_cost
- D010: proposed:tools/check_doc_consistency.py::test_pool_is_executable_factordef
- D011: proposed:tools/validate_spec_lifecycle.py::test_test_group_required  (extend)
- D012: proposed:tools/check_task_dag.py::test_no_forward_or_missing_edges
- D013: proposed:tools/check_doc_consistency.py::test_gpu_schedule_protocol_and_owner
- D014: proposed:tools/check_doc_consistency.py::test_f007_declares_f003_upstream
- D015: proposed:tools/check_doc_consistency.py::test_factordef_dto_matches_architecture
- D016: proposed:tools/check_doc_consistency.py::test_ir003_schema_version_has_carrier
- D017: proposed:tools/check_doc_consistency.py::test_ac_requirement_coverage
- D018: proposed:tools/check_doc_consistency.py::test_reproducibility_config_digest
- D019: proposed:tools/check_doc_consistency.py::test_cli_builds_generation_request
- D020: proposed:tools/check_doc_consistency.py::test_hypothesis_has_applicable_state
- D021: proposed:tools/check_doc_consistency.py::test_vendor_hygiene_has_upstream_baseline
- D022: proposed:tools/check_doc_consistency.py::test_active_feature_indexes_aligned

Good.

Now frontmatter. The issues list with all fields. Since this is a doc-review, `report_type: doc-review`, `round: 1`, `date: 2026-09-16`, `prior_report: none`, `scope: full-scan`, `stop_condition_met: false`, `severity_counts: {critical: 0, high: 14, medium: 7, low: 1}`.

Now write the file. It must be complete. Let me construct carefully.

Body sections: 结论先行; 基线与范围; 检视门槛与证据; findings table; 裁决记录 (none); 已通过项; Round-2 entry/stop conditions. Plus state Round 1 scan complete but loop not converged; Round 2 diff-only unless >30%.

Also mention existing gates: validate_spec_lifecycle passes; check_doc_links passes; CURRENT-doc.md ignored by .gitignore:39.

Let me now write the file with the write tool (apply_patch equivalent; the task says use apply_patch but the available tool is `write`/`edit`; I'll use write to create the file).

Wait—the MUST NOT DO says "do not add findings not listed". I have exactly 22. Good.

Let me write the document. It's large. I'll produce full content.

For the table, 13 columns. Let me keep cell text concise but complete. The suggested_fix column can be long-ish. And there's a separate 修复方案 (fix_summary) column which is `—`, 状态 open.

Table header:
| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |

All rows: 修复方案 `—`, 修复轮次 `—`, 首次出现轮次 1.

Now prepare each row.

Let me draft titles (Chinese, concise):
D001 标题: factor_id 含 run_seq，跨 run 变动，与「相同 factor_id 集合」矛盾
D002: REJECTED/FAILED 终态事实与原因未持久化
D003: 2 日闸门可直达 L2，违反 ADR-0001「L1 连续两周」判据
D004: 冒烟验收缺 ADR-0001 的漏斗逐级记账与奖励频率抽查义务
D005: 过渡期显式元组缺 cutoff/as-of/symbol_map/universe 语义
D006: 横截面 PIT 掩码未显式依赖 F008 的 universe_at/digest 契约
D007: monkeypatch/写白名单无法证明「无 egress/无写能力」强断言
D008: SIGTERM 将部分运行标 completed 并发出可消费完成事件
D009: generation objective 缺 PRD 要求的成本后收益
D010: 协同池持久化为 AlphaPoolDef/pool.json，而非可执行 FactorDef meta-factor
D011: tasks 缺强制 [TEST] 旅程验收组
D012: task 顺序/DAG 允许测试先于实现、裁决先于归档、T036 无入边
D013: GPU 调度无可验证 FIFO 协议，Kronos 卸载无 live owner
D014: F003 声称 F007 消费其事件/算子登记表，F007 未声明 F003 上游
D015: FactorDef 持久化 DTO/加载契约缺 compute/meta 恢复，与架构可执行 FactorDef 冲突
D016: IR-003 schema_version 无 AC/task 载体，GenerationRun 缺该字段
D017: AC 未覆盖其引用的全部 DR/TR/NFR 子句
D018: 可复现性缺 canonical config artifact/digest 与确定性 RNG/device 契约
D019: CLI 语法无法构造全部强制 GenerationRequest 字段，smoke 无实现载体
D020: HypothesisDef 缺 PRD FR2.1 的适用状态/regime 字段
D021: vendor 卫生 AC 要求逐行上游比对，任务只留 commit/清单
D022: 活跃 feature 索引三处漂移

Now the suggested fixes in table. I'll write them compressed but concrete, and also include a fuller narrative? The body has findings table only; the task says suggested fixes must be concrete and mention full landing points. So table cell must contain landing points. That's fine, cells can be long.

Let me write them.

D001 修复建议: design §3 改 `factor_id = <generator>_<definition_digest[:12]>`（删 `run_seq`），运行归属移交给 `run_id`；spec 65/259/305 与 design 104-105 同步，AC-009 加跨-run 相等断言。

D002 修复建议: design §3/§5/§7 增加 REJECTED/FAILED 终态 manifest（`rejection.json`/`failure.json`，含 status/termination/原因/时间戳），照旧最后原子写；spec 169-171/268-270 对齐；AC-003/AC-011 加断言。

D003 修复建议: spec 43/213/272-275 重写为 ADR-0001 40-50 忠实映射：2 日只判 L0/L1，L2 须 L1 连续 2 周 <50 或连续 2 周零无前视通过；AC-007 与 design 222 同步。

D004 修复建议: AC-007/spec 74 与 tasks 52-55/77 纳入 ADR-0001 52-62 两条义务（漏斗逐级计数入库、奖励频率抽查），记录进当日 manifest。

D005 修复建议: design 114 的 explicit_tuples 增加 `cutoff_time`/`as_of_fidelity`/`symbol_map_digest`/`universe_calendar_digest`，并写与 ResearchSnapshot 字段映射；spec 112/239/320/329 同步。

D006 修复建议: design §2/§5 与 tasks T020 声明 PIT 掩码消费 F008 IR-002 的 `universe_at(T)`+digest；tasks §4 加 `F008.IR-002 -> T020`；F003 spec 320 与 F008 243-244 互引。

D007 修复建议: 二选一：AC-011 降断言为「socket 构造被替换+白名单拒绝」并在 spec 260/design 208 写明非内核隔离；或引入 netns/容器隔离并立任务。

D008 修复建议: design 190 改 SIGTERM 为 `status=partial`+终态 manifest、不写 `run_completed`；仅完整运行写 completed；spec 269-270/TR-001 与 AC 同步。

D009 修复建议: design 58 objective.py 与 110 objective 字段增成本后收益（`cost_model`/`min_after_cost_return`）；spec 197 与 PRD 157 对齐；AC-006 加断言。

D010 修复建议: design 97/116 把 pool.json 定义为可执行 FactorDef（generator=pool/meta，compute 按成员权重重算），AlphaPoolDef 降为内部成员描述；spec 227-235 与 architecture 254-270 对齐；AC-008 加断言。

D011 修复建议: tasks §3 增 `### [TEST] 组`，从 US-001/002/003 每步骤派生 ≥1 断言（早编写晚执行）；否则 T3 门禁拒绝。

D012 修复建议: 调整 tasks：T018 先于 T016/T017；T032 先于 T019；T036 加 `T030-T035 -> T036` 入边；§4 依赖同步。

D013 修复建议: design §5 增 FIFO 序号/超时/持锁释放状态记录协议；为 Kronos 卸载钉 live owner（F003 加编排任务或 F004 加任务并登记跨 feature 边），并写明 F004 后移时 FIFO 如何取证。

D014 修复建议: F007 spec 7 加 F003 到 related_features，22-23 增 F003 的 generation.*/算子清单/池为上游契约；F003 spec 247/321 与 tasks T022 对齐。

D015 修复建议: design 94-106 DTO 补 compute/meta 加载恢复契约（表达式+feature_map 重建闭包、注册入口），或声明 DTO 与架构可执行 FactorDef 为两对象并给转换；AC-001/AC-004 加加载后可执行断言。

D016 修复建议: design 110 GenerationRun manifest 增 `schema_version`；spec 253/295-307 增 AC 与断言；tasks 增 schema_version 持久化与未知版本拒绝任务。

D017 修复建议: 逐条补断言：AC-003←DR-001；AC-005←TR-002 可查；AC-009←DR-002/DR-003/TR-001/池复现；AC-010←持久化 device/hostname；AC-011 修正 CLI 测试文件命名不一致（design 226）。

D018 修复建议: design 110/189 增 canonical config artifact 与 digest 入 run.json，并写 seed 派生/torch 确定性/CPU-GPU 差异处理；spec 239/259/305 与 AC-009 同步。

D019 修复建议: design 124-155 CLI 表补 GenerationRequest 全字段构造（window/config/quota 来源或默认）；tasks 52-55/69 增 smoke 实现任务与默认 config。

D020 修复建议: spec DR-003 241 与 design 108 HypothesisDef 增 `applicable_state`/`regime`；catalog/自动候选填值；AC-009 加字段断言；对齐 PRD 153-154。

D021 修复建议: tasks 31/49 增「冻结上游基线（commit+补丁/逐文件 digest）」任务，或把 AC-002 降为「commit+标注」并声明；建议前者，spec 149-155/298 同步。

D022 修复建议: CLAUDE 49-52 补 F003/F008；docs/README 36 与 BACKLOG 3-8 统一为 F003/F004/F007/F008；维护说明加漂移检查。

Good.

Now the body narrative. Let me write it.

结论先行: Round 1 full-scan complete; 22 findings (0 critical, 14 high, 7 medium, 1 low). Loop NOT converged. All findings open. No fixes requested/performed. Baseline main@a333394, clean tree, date 2026-09-16. Round 2 diff-only unless fixes >30%.

基线与范围: baseline, scope full-scan, prior none, report artifact gitignored.

检视门槛与证据: list the finite checklist used; severity gating; two channels (correctness vs quality); evidence = doc line refs; existing gates recorded.

已通过项: structure (spec 9 sections, design 11, tasks 6), Q/DQ closure (spec Q all closed; design DQ all closed), current machine gates (validate_spec_lifecycle passes; check_doc_links passes), BACKLOG bidirectional consistency passes (validate_spec_lifecycle covers it). Also note CLAUDE/README/BACKLOG drift is D022 finding.

Round-2 entry/stop conditions: entry = fixes land as one finding per commit; Round 2 reviews only the fix diff + adjacent contracts; >30% touch → may upgrade to full-scan once. Stop condition for full loop: all High cleared, doc gates green, CI green once, no new uncovered. Round 2 must also verify no fix-regression.

Now let me write.

One more: "裁决记录 (none)" — write `无（本轮无 rejected/partial 条目）`.

Also frontmatter issues: I'll include all fields. For `tracked_task`, `fix_summary`, `disposition_reason`, `resolved_round` empty quoted: `""`.

Let me write the file now. This will be long but complete.

For YAML, I'll list 22 issues. Let me be careful with YAML quoting. Titles contain Chinese punctuation, fine. I'll quote strings containing colons or special chars. Better to quote all scalar values. Colons inside quoted strings are fine. Let me use double quotes for values that contain `:` or `#`. Actually `#` inside a double-quoted string is fine. Let me quote all title/suggested_fix/location/regression_test/pattern_tag values with double quotes to avoid issues. But suggested fixes contain `→` and `["`, `{`, `}` — fine within quotes as long as no unescaped double quotes. I must avoid double quotes inside values, use 「」 instead. Also avoid backslashes.

Let me ensure no `"` inside the quoted scalar. I'll use fullwidth quotes if needed.

Also values contain `:` — within double quotes, fine.

Let me construct.

For origin field of D022: spec-drift.

Now, one concern: the task says "for categories use correctness except D011/D016/D017/D021 as test-coverage and D022 quality." Done.

Let me write.

Body table cells: avoid pipes `|` inside cells (would break table). Use `／` or `;`. My suggested fixes contain `|`? D001 has `<generator>_<definition_digest[:12]>` no pipe. D002 has `rejection.json`/`failure.json` no pipe. Avoid `|`. Good. Also avoid `→`? Fine in table.

Check D005 fix: no pipe. D013: no pipe. Good.

Also `["` is fine.

Let me now write file.

I'll also include a "证据索引" perhaps not needed. Keep to required sections.

Let me write.
Working tree clean, baseline confirmed, both gates pass. Writing the report now.

  <details><summary>tool output</summary>

  ```text
Wrote file successfully.

Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T14:04:29Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python - <<'PY'\nimport yaml, re, collections\np=\"docs/reviews/CURRENT-doc.md\"\ns=open(p,encoding=\"utf-8\").read()\nfm=s.split(\"---\",2)[1]\nd=yaml.safe_load(fm)\nids=[i[\"id\"] for i in d[\"issues\"]]\nsev=collections.Counter(i[\"severity\"] for i in d[\"issues\"])\nprint(\"issues:\",len(ids),\"unique:\",len(set(ids)))\nprint(\"sev:\",dict(sev),\"declared:\",d[\"severity_counts\"])\nprint(\"expected_ids_ok:\", ids==[f\"F003-D{n:03d
…[truncated])`


> [reasoning] Now verify: issue count = 22, severity_counts match, file ignored, and no other files modified. Let me run checks. Also validate YAML frontmatter parses. I can use python yaml. Let me check.

Also verify git status shows only the new ignored file (not tracked). And confirm issue count programmatically.

  <details><summary>tool output</summary>

  ```text
issues: 22 unique: 22
sev: {'high': 14, 'medium': 7, 'low': 1} declared: {'critical': 0, 'high': 14, 'medium': 7, 'low': 1}
expected_ids_ok: True
statuses: {'open'}
empty_ok: True
all_have_tags_key: True
table rows: 22 pipe-counts: {14}
--- ignored check:
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T14:04:35Z


> [reasoning] Everything checks:
- 22 issues, unique, expected IDs, severities match (14 high, 7 medium, 1 low).
- all statuses open, empty fields, table 22 rows with 14 pipes = 13 columns.
- git status clean (file ignored, no tracked changes).
- gitignored at .gitignore:39.

Done. Provide concise summary.
Done. `docs/reviews/CURRENT-doc.md` created (local, gitignored).

Verified:
1. 22 unique findings `F003-D001`–`F003-D022`; count = severity_counts (high 14, medium 7, low 1, critical 0).
2. All statuses `open`; `fix_summary`/`resolved_round`/`tracked_task`/`disposition_reason` empty; table 22 rows × 13 columns (pipe count 14).
3. Baseline `main@a333394`, clean tree; `CURRENT-doc.md` ignored at `.gitignore:39`; no other file touched; no commit.

Existing gates recorded and re-run green: `validate_spec_lifecycle.py`, `check_doc_links.py`.

Next action (under 2 min): have the fixer append the first evidence entry to `docs/reviews/FIX-log.md` (findings list + one commit per finding + regression tests + round-end gate), then re-run this same file for Round 2 diff-only review.
