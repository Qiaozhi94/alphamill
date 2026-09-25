---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f54f121e3ffeKFW3iy81gp7JcR"
title: "审计 F003 文档修复 (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T16:31:13Z"
updated_at: "2026-09-16T16:41:37Z"
tokens_input: 112539
tokens_output: 7432
cost: 0.0334
parent_id: "ses_f54f50b00fferZAnoSPa21C62p"
---

# 审计 F003 文档修复 (@explore subagent)

## user · 2026-09-16T16:31:13Z

Read-only audit /home/georg/projects/alphamill current F003 docs against a333394..HEAD, focusing D001..D022 and semantic correctness. Check run terminal persistence, factor/pool identity, ADR-0001 smoke ladder, snapshot binding, PIT/F008, egress wording, task order, FIFO/Kronos ownership, F007 contract, schema/version and AC coverage. Return only evidence-backed findings with exact file:line, severity, category, origin, pattern_tag, and a fixed/not-fixed verdict for each D001..D022. Do not edit files. Chinese output preferred.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T16:31:13Z

- **tool**: `bash({"command": "git -C /home/georg/projects/alphamill log --oneline -30 a333394..HEAD 2>&1 | head -60; echo \"---STAT---\"; git -C /home/georg/projects/alphamill diff --stat a333394..HEAD 2>&1 | tail -60"})`
- **tool**: `bash({"command": "git -C /home/georg/projects/alphamill show --stat --oneline a333394 2>&1 | head -30; echo \"---HEAD---\"; git -C /home/georg/projects/alphamill rev-parse HEAD; git -C /home/georg/projects/alphamill log --oneline -5"})`
- **tool**: `glob({"pattern": "**/F003*/**"})`
- **tool**: `glob({"pattern": "**/*F003*"})`
- **tool**: `glob({"pattern": "**/D0[0-2][0-9]*"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`


> [reasoning] The user wants a read-only audit of /home/georg/projects/alphamill current F003 docs against commit range a333394..HEAD. This is a complex task. Let me start by exploring the repo, the git range, and F003 docs.

Let me launch parallel investigations.
<analysis>
**Literal Request**: 对 /home/georg/projects/alphamill 当前 F003 文档，对照 a333394..HEAD 做只读审计，聚焦 D001..D022、语义正确性，检查 8 个主题，输出精确 file:line、severity、category、origin、pattern_tag、fixed/not-fixed 判定，不改文件。
**Actual Need**: 拿一份可直接落地的审计结论，判断 D001..D022 哪些已在代码/文档中修复、哪些仍缺失或语义错误。
**Success Looks Like**: 每条 D 项有证据行号 + 判定；无相对路径；中文。
</analysis>

先并行摸清仓库结构、git 范围与 F003 文档位置。

  <details><summary>tool output</summary>

  ```text
26c7b6d fix(f007): D007 补 T009->T012 与 T012->T013 依赖边
36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）
59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断
b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用
5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点
ccf577d fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约
65e1832 fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组并重编号回写任务
d659db7 test(f003): 新增任务 DAG/文档一致性/[TEST] 组门禁 + 变异单测（D011/D012 及各 finding 回归锁定）
fcc14ad fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
ab30da9 fix(f003): D002/D007/D010 术语归一——终态小写、池版本键改 factor_id、egress 措辞
32f4942 fix(f003): D011+D012 tasks 补 [TEST] 旅程验收组并修正任务图顺序
07e6649 fix(f003): D021 vendor 卫生补冻结上游基线，使逐行比对可复现
da4df56 fix(f003): D019 CLI 可构造完整 Generati
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
a333394 docs(sdd): [TEST] 组入驻 tasks 模板 + F003/F007/F008 设计补开发前置约束（T3 开工门禁）
 docs/features/0.2/F003-alphagen-vendor/design.md    | 4 ++++
 docs/features/0.2/F007-evaluation-gates/design.md   | 4 ++++
 docs/features/0.2/F008-universe-expansion/design.md | 4 ++++
 docs/features/TEMPLATE/tasks.md                     | 9 ++++++++-
 4 files changed, 20 insertions(+), 1 deletion(-)
---HEAD---
26c7b6d4ff179f9f066b713b286afff9871456b7
26c7b6d fix(f007): D007 补 T009->T012 与 T012->T013 依赖边
36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）
59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断
b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用
5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No files found
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

## assistant · 2026-09-16T16:31:27Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls -la docs/reviews/ 2>&1; echo \"---gitignored?---\"; git status --porcelain --ignored 2>&1 | grep -i -E \"review|FIX|CURRENT\" | head -40; echo \"---glob reviews---\"; find docs -iname \"*D0*\" -o -iname \"*finding*\" -o -iname \"*FIX*\" 2>/dev/null | head"})`
- **tool**: `grep({"pattern": "D0(0[1-9]|1[0-9]|2[0-2])", "output_mode": "files_with_matches"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`


> [reasoning] The task mentions D001..D022. Let me find the review/FIX-log or findings doc. The commit messages reference D001..D022 fixes. Let me search docs/reviews and any F003 findings. Also need the audit checklist. Let me find D0xx definitions.

Let me look for review docs, the F003 three files, and the check tools. Also git diff of F003 docs across range.

Note: the user says "current F003 docs against a333394..HEAD, focusing D001..D022". So D001..D022 are findings from some review (maybe docs/reviews/CURRENT-...). Let me find them.
并行读取 F003 三件套与查找 D001..D022 findings 定义。

  <details><summary>tool output</summary>

  ```text
total 220
drwxr-xr-x 2 georg georg   4096 Sep 16 23:41 .
drwxr-xr-x 7 georg georg   4096 Sep 15 01:58 ..
-rw-r--r-- 1 georg georg  43064 Sep 17 00:16 CURRENT-doc-F007.md
-rw-r--r-- 1 georg georg  35300 Sep 16 22:26 CURRENT-doc.md
-rw-r--r-- 1 georg georg  13434 Sep 17 00:07 FIX-log.md
-rw-r--r-- 1 georg georg 117606 Sep 16 02:11 RETROSPECTIVE.md
---gitignored?---
!! .code-review-graph/
!! docs/reviews/CURRENT-doc-F007.md
!! docs/reviews/CURRENT-doc.md
!! docs/reviews/FIX-log.md
---glob reviews---
docs/reviews/FIX-log.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 27 match(es) in 27 file(s)

/home/georg/projects/alphamill/tools/check_doc_links.py

/home/georg/projects/alphamill/tools/check_doc_consistency.py

/home/georg/projects/alphamill/tools/check_task_dag.py

/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md

/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/design.md

/home/georg/projects/alphamill/docs/features/0.2/F002-data-bridge/spec.md

/home/georg/projects/alphamill/tests/unit/test_check_doc_links.py

/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest.py

/home/georg/projects/alphamill/src/alphamill/data_bridge/symbol_map.py

/home/georg/projects/alphamill/src/alphamill/data_bridge/digest.py

/home/georg/projects/alphamill/src/alphamill/data_bridge/reconcile.py

/home/
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

## assistant · 2026-09-16T16:31:32Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/CURRENT-doc.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/reviews/FIX-log.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git diff a333394..HEAD -- docs/features/0.2/F003-alphagen-vendor/ 2>&1"})`


> [reasoning] Now I need the D001..D022 findings. They are likely in docs/reviews/CURRENT-doc.md (gitignored but present). Let me read that. Also FIX-log.md. And the diff of F003 docs a333394..HEAD to know what changed.

Let me read CURRENT-doc.md and FIX-log.md.
D001..D022 定义应在本地检视稿。读取检视稿与 FIX-log，并取 F003 文档 diff。

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
<path>/home/georg/projects/alphamill/docs/reviews/FIX-log.md</path>
<type>file</type>
<content>
1: # FIX-log — 修复方声明（append-only）
2: 
3: > 本文件是修复方独占的发声通道（review-convergence skill §8）：只按轮追加，不修改/删除历史条目。
4: > 检视报告 `CURRENT-doc.md` 的写权归检视方，修复方对它的合法动作是**零写入**。
5: > 本文件与 `CURRENT-doc.md` 同为 gitignored 本地过程稿，闭环时由检视方一并删除。
6: 
7: ---
8: 
9: ## Round 1 · 2026-09-16 · report_type: doc-review
10: 
11: ### 基线与范围
12: 
13: - 基线：`main@a333394`（工作树干净），与本轮检视报告声明的基线一致。
14: - 被检对象：`docs/features/0.2/F003-alphagen-vendor/{spec,design,tasks}.md` 及相邻契约。
15: - 本轮处理范围：`CURRENT-doc.md` Round 1 全量扫描的全部 22 条 finding（high 14 / medium 7 / low 1）。
16: - 说明：F003 仍为 `status: draft`（无实现代码），本轮为**文档修复**；证据类型按 skill §3「文档检视靠文档被改 + 链接/格式检查通过」执行。
17: 
18: ### findings
19: 
20: 本轮处理 `F003-D001` … `F003-D022`，共 22 条，全部 `fixed`，无 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
...output truncated...

Full output saved to: /home/georg/.local/share/opencode/tool-output/tool_0ab0f3b70001mKvFvZv04RD7rN

 
 #### Scenario: 未标注的 vendor 改动
 
@@ -194,7 +194,7 @@ ADR-0001 已锁定主引擎为 AlphaGen（vendor 方式），但同一份调研
 
 ### Requirement: 生成侧能力边界与目标对齐（`FR-005`）
 
-系统应当维护算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 日历下的窗口换算），对每个候选执行生成侧自检：引用未登记算子、隐含前视、未支持的跨 pair 算子或不满足 ≥30 笔/90 天可达性预筛的候选一律拒绝并计数；奖励或前置筛选应当同时考虑预测证据与换手，禁止只优化 RankIC。
+系统应当维护算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 日历下的窗口换算），对每个候选执行生成侧自检：引用未登记算子、隐含前视、未支持的跨 pair 算子或不满足 ≥30 笔/90 天可达性预筛的候选一律拒绝并计数；奖励或前置筛选应当同时考虑预测证据、换手、≥30 笔/90 天可达性**与成本后收益**（按可配成本参数计算，参数与口径写入运行记录），禁止只优化 RankIC。成本后收益在此是**预筛信号而非成本裁决**——三档成本结论与 `cost_model_version` 归 `F007`（ADR-0003）。
 
 #### Scenario: 零交易型表达式
 
@@ -210,7 +210,12 @@ ADR-0001 已锁定主引擎为 AlphaGen（vendor 方式），但同一份调研
 
 ### Re
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:31:38Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_task_dag.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git diff a333394..HEAD -- docs/alphamill-architecture.md docs/README.md CLAUDE.md docs/features/0.2/F007-evaluation-gates/ tools/validate_spec_lifecycle.py tools/verify.py 2>&1"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`


> [reasoning] Now I have the D001..D022 definitions, the FIX-log claims, and the current F003 docs. The task: audit current F003 docs against a333394..HEAD, focusing D001..D022 and semantic correctness; check the 8 themes. Return evidence-backed findings with exact file:line, severity, category, origin, pattern_tag, and fixed/not-fixed verdict for each D001..D022.

So I need to independently verify each D001..D022 against current docs. Let me systematically check each. Also inspect the check tools (check_doc_consistency.py) to see if claims match, and the architecture changes, F007 changes, CLAUDE/README/BACKLOG.

Let me read the relevant files: architecture §4.1, F007 spec/design/tasks, BACKLOG, tools/check_doc_consistency.py, check_task_dag.py, validate_spec_lifecycle.py, F008 spec, ADR-0001, ADR-0007.

Let me be efficient and read in parallel. This is a big audit. Let me gather evidence.

Key checks per D:

D001 factor_id no run_seq. current design.md:108 says factor_id = <generator>_<definition_digest[:12]> no run. spec:245, AC-009. Verify.

D002 terminal run facts persisted: design.md:96 run.json "四态都写", line 103 terminal states, 216 failure mapping. spec:271-276, TR-001:251. Verify.

D003 2-day time-box only L0/L1, L2 2 weeks. spec:43,213,278-280 (current lines). design:255. AC-007. Verify.

D004 ADR-0001 M2 obligations: spec:215-218, design:116,211, tasks:52,112. Verify.

D005 explicit tuple fields ADR-0007: design:120, spec:112,244,328,337. Verify.

D006 PIT depends F008 universe_at: design:55,82, tasks:59,97. spec:328. Verify F008 spec references.

D007 egress wording: spec:122,265, AC-011:314; design:218,251. Verify.

D008 SIGTERM partial: spec:276, design:200. AC? TR-001:251. Verify.

D009 objective after-cost: spec:197, design:58,114. AC-006:309. PRD FR2.3. Verify.

D010 pool executable FactorDef: design:124, spec:234,247, AC-008:311. architecture §4.1 generator pool. Verify.

D011 [TEST] group: tasks:82-86. validate_spec_lifecycle. Verify.

D012 task DAG order: tasks §4:92-106, T032 merged archive+writeback, T039. Verify check_task_dag.

D013 GPU FIFO protocol + Kronos owner: design:196-201, spec:263, AC-010:313, tasks T025. Verify.

D014 F007 declares F003 upstream: F007 spec frontmatter related_features + upstream. Verify.

D015 FactorDef DTO load contract: design:110. AC-001/004. Verify.

D016 schema_version: design:105,114; spec:258, AC-012:315; tasks T008/T012. Verify.

D017 AC coverage of DR/TR/NFR clauses: AC-003 DR-001, AC-005 TR-002, AC-009, AC-010, AC-011 test file naming. Verify design:226 vs spec:314.

D018 config digest determinism: design:122, spec:264, AC-009. Verify.

D019 CLI builds GenerationRequest: design:132-166, tasks T027, T016 smoke. Verify.

D020 HypothesisDef applicable_state: design:112, spec:246, PRD FR2.1. Verify.

D021 vendor baseline: design:84, spec:149, AC-002:305, tasks T003/T013. Verify.

D022 active indexes: CLAUDE:49-52, docs/README:36, BACKLOG. Verify.

Now let me read the supporting files. Parallel reads.

Also note the theme list in the user request: "run terminal persistence, factor/pool identity, ADR-0001 smoke ladder, snapshot binding, PIT/F008, egress wording, task order, FIFO/Kronos ownership, F007 contract, schema/version and AC coverage." That maps to D002/D008, D001/D010, D003/D004, D005, D006, D007, D012, D013, D014, D016/D017.

The user asks: "Return only evidence-backed findings with exact file:line, severity, category, origin, pattern_tag, and a fixed/not-fixed verdict for each D001..D022."

So output a table/list of 22 entries with verdicts. I need to verify each independently, not trust FIX-log. Let me gather the evidence. Some findings might still be unfixed or partially fixed (e.g., D004 tasks references, D012 DAG). Let me check.

Let me read files.
读取支撑契约与门禁工具以独立核对每条 finding。

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_doc_consistency.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """文档一致性门禁（doc review F003 契约断言回归门）。
3: 
4: 把 F003 检视闭环中被修复的每一处契约写成**可红的断言**：要求项缺失、或旧矛盾
5: 文本回归时即判红。每条 check 对应一个 finding id，便于检视方逐条独立核对。
6: 
7: 覆盖范围：
8:   - 声明式文本断言（`TEXT_CHECKS`）：要求/禁止的字面量，按 finding 分组；
9:   - 解析式断言：F007 是否声明 F003 上游（D014）、AC 断言是否覆盖其引用的子句
10:     （D017）、活跃 feature 索引三处是否一致（D022）。
11: 
12: 用法：python tools/check_doc_consistency.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15: 
16: from __future__ import annotations
17: 
18: import dataclasses
19: import pathlib
20: import re
21: import sys
22: 
23: ROOT = pathlib.Path(__file__).resolve().parent.parent
24: 
25: SPEC = "docs/features/0.2/F003-alphagen-vendor/spec.md"
26: DESIGN = "docs/features/0.2/F00
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_task_dag.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """任务依赖 DAG 校验（doc review F003-D012 回归门）。
3: 
4: 对进入开发流转的 Feature（spec status ∈ {ready-for-development, in-progress,
5: review}）校验 `docs/features/<version>/Fxxx-*/tasks.md`：
6: 
7:   - §4「依赖与并行关系」里所有边端点都是已定义的任务 ID；
8:   - 边一律「向前」：源 ID < 目标 ID（任务编号即执行顺序，禁止依赖后序任务）；
9:   - 最高编号任务（收口任务）必须有至少一条入边；
10:   - `[P]` 任务不得同时声明前置边（tasks 模板规定）。
11: 
12: **作用域说明**：不收 `done`（F001/F004 等历史 Feature 已收口，纳入会立刻破坏
13: 既有文档）与 `draft`（尚未进入流转）。这与 `validate_spec_lifecycle.py` 的
14: status 作用域模式一致。
15: 
16: 用法：python tools/check_task_dag.py
17: 退出码 0 = 全部通过；1 = 存在违规。
18: """
19: 
20: from __future__ import annotations
21: 
22: import pathlib
23: import re
24: import sys
25: 
26: ROOT = pathlib
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
diff --git a/CLAUDE.md b/CLAUDE.md
index f5da7a3..12be84a 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -48,5 +48,6 @@ AI 原生的加密量化研究与交易管线：以 AI 因子工厂为核心，
 
 ## 当前活跃 Feature
 
-- F004 Kronos 推理运行时（v0.2, draft）→ `docs/features/0.2/F004-kronos-inference-runtime/`
+- F003 AlphaGen vendor 与可插拔生成器平面（v0.2, draft）→ `docs/features/0.2/F003-alphagen-vendor/`
 - F007 统一评测台与证据门禁（v0.2, draft）→ `docs/features/0.2/F007-evaluation-gates/`
+- F008 宇宙扩容与 point-in-time 宇宙台账（v0.2, draft）→ `docs/features/0.2/F008-universe-expansion/`
diff --git a/docs/README.md b/docs/README.md
index b96634a..3b574d6 100644
--- a/docs/README.md
+++ b/docs/README.md
@@ -33,7 +33,7 @@ updated: 2026-09-15
 | Feature 实现方案 | `features/<version>/Fxxx-*/design.md` | 技术设计 |
 | 开发、验收和检视纪律 | `SOP.md` | 开发流程约定 |
 | 当前 active Feature 与强提醒 | `../
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

## assistant · 2026-09-16T16:31:49Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '240,300p' docs/alphamill-architecture.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"FR2.1\\|FR2.3\\|适用状态\\|regime\\|作用机制\\|成本后\" docs/alphamill-prd.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"IR-002\\|IR-003\\|universe_at\\|schema_version\" docs/features/0.2/F008-universe-expansion/spec.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && .venv/bin/python tools/validate_spec_lifecycle.py; echo \"EXIT=$?\"; .venv/bin/python tools/check_task_dag.py; echo \"EXIT=$?\"; .venv/bin/python tools/check_doc_consistency.py; echo \"EXIT=$?\""})`


> [reasoning] Now I have a lot. I need to independently verify each finding. Let me note some potential issues I've already spotted:

1. ADR-0001: need to check the actual text — the L2 criteria. spec:43 says "L1→L2 不在 time-box 内——须由 L1 连续 2 周满足 ADR-0001 判据触发". spec:213 says L1→L2 only when "L1 连续 2 周满足 ADR-0001 判据（周候选 <50 或零候选通过无前视审计）". Need to verify ADR-0001 text.

2. D017 AC coverage: check_doc_consistency AC_BODY_REQUIREMENTS has "011": ("cli_contract",) — but the AC-011 body doesn't literally contain "cli_contract". Wait, the check searches for "cli_contract" in the AC-011 body. Current AC-011 body (spec:314) is: "egress guard 安装后出网尝试被拒绝（socket 构造被替换、只放行 AF_UNIX；断言范围为**进程级护栏，非内核隔离**）、护栏缺失时拒绝启动；写 `reports/generation/<run_id>/` 之外路径（证据台账/留出/晋级状态）的尝试被拒绝；缺绑定的 `mine` 请求非零退出并留 `rejected` 终态 run.json — tests: `tests/integration/test_f003_boundaries.py`, `tests/unit/test_f003_cli_contract.py`". Hmm, the body captured by AC_LINE_RE is group(3) which is everything after `:`. That includes the tests: backtick string `tests/unit/test_f003_cli_contract.py`. So "cli_contract" is contained. OK. That's a weak check though - it only matches the test filename, which is arguably gaming the gate. But it's the D017 suggested fix "AC-011 修正 CLI 测试文件命名不一致（design:226）". Actually D017 suggested fix mentions design:226 test file naming inconsistency. Let me verify design §8 AC-011 row says `tests/integration/test_f003_boundaries.py`, `tests/unit/test_f003_cli_contract.py` — yes design:236 now. Good.

3. D012: check_task_dag only enforced for status in {ready-for-development, in-progress, review}. F003 is draft, so the DAG gate does NOT run on F003! That's a significant point: D012 regression test `test_no_forward_or_missing_edges` claims coverage, but F003 status=draft means the gate is not enforced on it. The fix commits adjusted tasks.md, and the gate would catch it once status advances. Is that a finding? The fix itself (reordering) can still be verified by reading tasks. But the "regression lock" is not active until status changes. Worth noting as residual risk / partial. Similarly D011 [TEST] gate: validate_spec_lifecycle TEST_GROUP_STATUSES = {ready-for-development, in-progress, review}, so draft is exempt. The regression test `test_review_missing_test_group_rejected` only tests the positive at review status. But [TEST] group is present. So D011 fixed in doc, gate only active later. Note.

4. D014: check requires F007 spec related_features F003 and "**F003**" in text. Verified present.

5. D022: active feature indexes. BACKLOG has F003/F007/F008. CLAUDE has F003/F007/F008. docs/README has F003/F007/F008. Verified.

Now potential semantic correctness problems the user wants me to find. The instruction: "focusing D001..D022 and semantic correctness. Check run terminal persistence, factor/pool identity, ADR-0001 smoke ladder, snapshot binding, PIT/F008, egress wording, task order, FIFO/Kronos ownership, F007 contract, schema/version and AC coverage."

I should look for remaining semantic errors even in "fixed" items. Let me look carefully.

Potential issue A: design.md:104 (updated at line 105?) Let me recheck exact line numbers in current design.md. From the read:
- line 103: 终态与可消费性: run.json four states, fields status/termination/reason/started_at/finished_at
- line 104: 只有 completed 可下游消费
- line 105: FactorDef schema_version
- line 107: definition_digest
- line 108: factor_id
- line 110: 加载契约
- line 112: HypothesisDef
- line 114: GenerationRun
- line 116: counts
- line 118-121: binding
- line 122: config
- line 124: pool

Wait, in the read output, line 96 says run.json, 97 factors, 98 pool, 99 events, 100 checkpoints. 103 终态. 104 只有. 105 FactorDef. 107 definition_digest. 108 factor_id. 110 加载契约. 112 HypothesisDef. 114 GenerationRun. 116 counts. 117 universe. 118 binding 两种形态. 119 snapshot mode. 120 explicit_tuples. 121 两种形态都校验. 122 config. 124 pool. Yes.

Potential issue: D002 suggested terminal manifest for rejected/failed with rejection.json/failure.json. Actual fix used unified run.json four states, which is arguably better. Fixed.

Potential semantic issue: design.md line 96 says "run.json # GenerationRun 终态 manifest（唯一运行事实；四态都写，tmp+fsync+rename 最后写）" and line 98 says "pool.json # 协同池 meta-factor（可选；仅 status=completed 的运行产出）". Good.

Potential issue: spec §5 lifecycle: queued -> rejected includes "队列等待超时（写终态 run.json）". NFR-002 says wait timeout leaves `rejected` terminal (termination=queue_timeout). Consistent.

But design.md:196 says "等待超过可配超时（默认 30min）即释放队位并写 `termination=queue_timeout` 的终态 `run.json`" - consistent.

Potential issue: D008 SIGTERM. spec:276 "running -> partial SIGTERM 优雅停机；保留已产候选供诊断，不写 pool.json、不发 run_completed". design:200. TR-001 spec:251. Consistent.

Now let me check ADR-0001 to verify the ladder. And ADR-0007. And PRD FR2.1/FR2.3. And F008 spec IR-002/IR-003.

Also I should actually run the gates to confirm green, and maybe test that the checks are meaningful. But the task is a doc audit; running tools is allowed (read-only). Let me run check_doc_consistency.py, check_task_dag.py, validate_spec_lifecycle.py to confirm current state green. Actually verify.py is heavy. Let me run the three lightweight gates.

Also verify the git state: is HEAD exactly 26c7b6d? The FIX-log says main ahead of origin by 23 commits. The user says a333394..HEAD. HEAD=26c7b6d.

Let me now check ADR-0001, ADR-0007, PRD relevant lines, F008 spec IR-002/IR-003.

Let me also grep for possible leftover contradictions. E.g., design.md:110 (now line 110) says FactorDef load contract. spec:305 AC-002 etc.

One thing I noticed: spec DR-002 (line 245) lists factor_id and run_id. design:108 says factor_id no run seq. Good.

Potential issue: design.md:108 says "factor_id = <generator>_<definition_digest[:12]>". But note architecture §4.1 example "alphagen_gen042_f003" at architecture:259 — the example still shows run-like suffix "f003". Actually that's a comment in architecture. It says `factor_id: str # 如 "alphagen_gen042_f003"`. Hmm, that example "f003" looks like a run sequence or feature id. It might contradict the new content-addressing convention. The FIX-log even says "附带提交 fcc14ad — 架构 generator 增 pool". But architecture example still "alphagen_gen042_f003". Is that a semantic inconsistency? Possibly a residual D001-adjacent issue: architecture's example factor_id includes a trailing identifier that could be misread as run seq. But it's just an example. Severity low. Let me note as observation maybe.

Actually wait — D001 was about F003 design/spec, and architecture example was not in scope. But semantic correctness: the example "alphagen_gen042_f003" would now be <generator>_<definition_digest[:12]> = alphagen_<12 hex>. So "gen042_f003" isn't hex 12. It's a stale example. Could flag as low medium. Let me verify architecture line.

Let me read the relevant docs.
并行核对 ADR-0001/ADR-0007/PRD/F008 与架构示例，并实跑三条轻量门禁。

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
ResearchSnapshot + HypothesisDef → FactorDef → factor ExperimentRun
FactorDef(s) → PortfolioDef → portfolio ExperimentRun → DeploymentCandidate
→ DeploymentRun → RunRecord → AttributionReport →（人审通过）新 HypothesisDef
```

- `HypothesisDef` 拥有经济动机、来源、generation、数据依赖、预期持有期和成本敏感性；
- `FactorDef` 拥有可执行定义和版本，不承载评测结论；
- `PortfolioDef` 拥有成员、权重、估计窗口、约束和组合门报告；
- `ExperimentRun` 拥有显式 execution tier、cohort、冻结规则和内容寻址 ID；
- `DeploymentRun` 固定引用 portfolio、信号缓存和审批版本；
- `RunRecord` 保存 intended/attempted/accepted/failed 四桶及执行事实；
- `AttributionReport` 区分事实、推断与建议，经规则或人审才触发生命周期/新假设动作；
- `ExperimentManifest` 是各对象和所有证据之间的不可变索引，不把结果复制回定义对象。

### 4.1 因子定义（FactorDef）

```python
@dataclass(frozen=True)
class FactorDef:
    factor_id: str            # 如 "alphagen_gen042_f003"
    hypothesis_id: str        # 指向 Hypothes
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
41:> 可复现的闭环，持续发现并运营成本后有效的 Alpha。
51:4. **成本后结果优先**：交易费、滑点和资金费率是选择回路的一部分，不是事后报告。
61:| 北极星结果 | **在跑组合持续盈利** | 所有在跑组合合并资金曲线的成本后净超额收益（相对各策略预注册基准，不设跨策略统一收益承诺）：滚动 90 天净超额收益 > 0，且最近 4 个滚动 90 天窗中至少 3 个为正（持续性判据）；同时满足最大回撤 ≤ 预注册阈值、单组合达到可信样本量（约 ≥69 笔）；组合须有效独立、在选择期构建并冻结、成本后为正、通过无前视与最终确认、部署前复核有效，且对现有组合有正边际贡献。满足判据的在跑产出计为「可信 Alpha」 |
66:| 线上结果 | 组合运行质量 | paper/live 的成本后收益、回撤、容量、回测偏差与因子衰减；按策略预注册基准判断；作为北极星的分解与领先指标（信号质量 → 组合转换 → 成本容量 → 执行实现） |
69:北极星以在跑组合的持续成本后表现为唯一结果判据；产能类数字（周候选数、批次组合数）一律
153:- **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
157:- **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
172:  成本后收益不为正则 `dead`。参数以 dry-run 实际成交校准并带 `cost_model_version`。
200:- **FR4.3 Top-K、权重与冻结**：按选择期成本后指标选 Top-K（v0.1 K=3，硬上限 5），用选择期估计的
306:| 信号成本后不可交易 | 成本与换手进入生成目标和硬门；实际成交持续校准并保留重定价摘要 |


Incremental: 0 fi
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
120:- `universe_membership` 只追加台账（联机库）与 `universe_at(T)` 查询；按 `symbol_map` 同构的方式发布为**内容寻址 artifact** 到湖（ADR-0007 与 `F007` IR-002 都按 artifact 定义它）；
204:系统应当维护只追加的宇宙成员台账，每条记录带生效区间与进出原因；系统应当提供 `universe_at(T)` 查询，返回 T 时刻的成员集合。历史区间一经发布不得修改。
243:- **IR-002**：宇宙台账 artifact 应当以固定 canonical 格式（列序、排序、UTF-8、LF）发布到湖元数据目录，路径按 digest 寻址；读取接口应当支持按 digest 加载并提供 `universe_at(T)` 语义查询。
244:- **IR-003**：台账与运行记录应当带 `schema_version`，供 `F003`（横截面 PIT 掩码）与 `F007`（ResearchSnapshot 的 universe 摘要）只读消费。
250:- **NFR-003**：正确性：`universe_at(T)` 对任意 T 返回的成员集合不含 T 之后才进入的 pair，也不排除 T 时在册但之后退出的 pair（无幸存者偏差）。
284:- **SC-003**：台账成立——`universe_at(T)` 对历史任意时点返回正确成员集合，台账只追加；
295:- [ ] **AC-007** (`FR-005`, `NFR-003`): 含上市/退市/中途进出的 fixture 上，universe_at(T) 在各时点返回正确成员集合 — tests: `tests/unit/test_f008_membership.py`
297:- [ ] **A
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
EXIT=0
check_task_dag: 全部通过
EXIT=0
check_doc_consistency: 全部通过
EXIT=0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:32:48Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"Kronos\\|kronos\\|卸载\\|F003\\|F004\" docs/alphamill-architecture.md | head -60"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '1,15p' docs/features/0.2/F004-kronos-inference-runtime/spec.md; echo \"---TASKS 60-80---\"; sed -n '55,85p' docs/features/0.2/F004-kronos-inference-runtime/tasks.md; echo \"---grep scheduler/offload---\"; grep -rn \"kronos_offload\\|卸载\\|mining\\|F003\\|F004\" docs/features/0.2/F004-kronos-inference-runtime/ | head -40"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '150,160p' docs/alphamill-prd.md"})`


> [reasoning] Now I need to check ADR-0007 and PRD FR2.1 full text, and verify D005 field alignment. Also check architecture example inconsistency.

Let me read ADR-0007 and PRD lines 150-160.

Also need to check F003 spec line numbers precisely. The read gave line numbers. Let me map D-findings to current lines.

Let me also verify D003: ADR-0001 says L1→L2 when "L1 连续 2 周每周进评测台候选 <50" or "L1 连续 2 周零候选通过无前视审计". spec:213 says "周候选 <50 或零候选通过无前视审计" - consistent enough. spec:280 says "L1 连续 2 周：周候选 <50 或零候选通过无前视审计（ADR-0001）". Good.

Wait — there's a subtle issue in spec:43: "2 个工作日 time-box 内得到二元裁决：主引擎锁定 L0，或按 ADR-0001 判据降级到 L1...；**L1→L2 不在 time-box 内**——须由 L1 连续 2 周满足 ADR-0001 判据触发。" Good.

D004: ADR-0001 lines 52-62. spec:215-218 covers both obligations. Yes.

D005: ADR-0007 fields. Need to read ADR-0007.

Let me read ADR-0007 and PRD 150-160. Also check design.md:120 explicit tuple includes symbol_map_digest, universe_calendar_digest, provenance — yes.

Now the main task: produce verdicts. But the user wants "evidence-backed findings", implying I should find residual issues. Let me hunt for semantic issues that remain after the fixes. Candidates:

1. Architecture §4.1 example `factor_id: str # 如 "alphagen_gen042_f003"` (architecture:259) still contradicts content-addressing convention (factor_id = <generator>_<definition_digest[:12]>). Since a333394..HEAD changed architecture generator comment but not the example. This is a residual semantic inconsistency adjacent to D001/D010. Severity low-medium, category correctness, origin original-coding? Actually spec-drift, pattern spec-internal-contradiction. Verdict: not part of any D item — but the user asked focusing D001..D022 and semantic correctness. I can report as extra finding.

2. D002: design.md says "run.json ... 四态都写" but the terminal states `rejected` can occur in `queued` stage. Fine.

But wait: design.md:103 says fields at least `status`,`termination`,`reason`,`started_at`/`finished_at`. For a `rejected` run that fails binding validation before start, `started_at` might not exist. Minor.

3. D008: spec:276 says partial "保留已产候选供诊断，不写 pool.json、不发 run_completed". design:200. Good. But is there an AC covering partial? AC list doesn't explicitly mention SIGTERM/partial. TR-001 spec:251 mentions non-completed terminal states don't emit. AC-009 covers "completed 运行的 run_completed 事件可查（TR-001）" — covers only positive. No AC asserts that partial/rejected/failed do NOT emit run_completed. That's an AC-coverage gap for D008/D002. D017 was about AC covering referenced clauses. The "非完成终态不发 run_completed" clause is in TR-001 and appended to AC-009's requirement list? AC-009 lists TR-001 but body only says "completed 运行的 run_completed 事件可查". The negative assertion (partial/failed 不发) lacks an AC. This is a residual gap. Severity medium, category test-coverage, origin process-gap, pattern_tag gate-without-teeth / spec-tasks-traceability-gap. Verdict: D008 fixed in doc but AC coverage not fixed (D017 partial?). Hmm. Let me be careful: D017 suggested "AC-009 增 DR-002/DR-003/TR-001/池可复现". The regression check for D017 is AC-005 "可按 run 查询", AC-009 needles "DR-002","DR-003","TR-001","池成员". It checks literal strings in AC body. AC-009 body contains "TR-001" (in tests? no). Let me look: AC-009 body: "...completed 运行的 run_completed 事件可查（TR-001）；重跑得到相同协同池成员（NFR-003）；..." yes contains "TR-001" and "池成员". So the mechanical check passes by literal token. But semantically the negative clause isn't asserted. So D008's behavior is documented, but no test/AC asserts the partial case. Is that a finding? It's a real traceability gap. I'll flag as medium.

Actually, let me reconsider. The user wants a verdict for each D001..D022 fixed/not-fixed. I should give verdicts primarily. Extra semantic findings are bonus. Let me determine honest verdicts.

Let me examine each carefully for residual issues.

D001 (factor_id no run seq): Fixed. spec:245 DR-002, design:108, AC-009. Evidence present. Verdict: fixed. Residual: architecture:259 example stale (separate).

D002 (terminal persistence): Fixed. design:96,103; spec:271-276; AC-003:306 "留 rejected 终态 run.json（含 termination/reason/时间戳...）", AC-011:314 "留 rejected 终态 run.json". Good. But `failed`/`partial` terminal persistence: spec lifecycle covers all states write run.json; design:200. AC only asserts rejected. No AC asserts failed/partial manifest persistence. Medium gap. But the D002 fix scope was "REJECTED/FAILED 终态 manifest". AC-003/AC-011 per suggested fix add assertions — those cover rejected. FAILED not covered by AC. So D002 partially fixed? The doc is fixed; the AC coverage for FAILED is missing. Hmm. The finding's suggested fix says "AC-003/AC-011 加断言" — AC-003 covers rejected startup; FAILED (training exception) not asserted. I'd call D002 fixed (doc) with residual AC gap. To be fair to "fixed/not-fixed", I'll say fixed, but note residual.

D003: Fixed. spec:43,213,280; design:255. Verdict fixed.

D004: Fixed. spec:215-218; design:116,211; tasks:52,85,112. Verdict fixed.

D005: Fixed. design:120; spec:112,244,337; ADR-0007 alignment. Need to verify ADR-0007 exact fields. Let me read.

D006: Fixed. design:55,82; tasks:59,97; spec:328; F008 IR-002/003 confirmed. Verdict fixed.

D007: Fixed. spec:122,265; design:218,251; AC-011:314. Verdict fixed. But note egress guard only AF_UNIX allowed; architecture says prototype... fine.

D008: Fixed doc; residual no AC for partial. Verdict fixed (doc) — but maybe "fixed" with residual.

D009: Fixed. spec:197, AC-006:309, design:58. Need to verify PRD FR2.3 line. Confirmed PRD:157 includes 成本后收益. Verdict fixed. But AC-006 only asserts params in run.json, not that pre-screen actually rejects cost-negative; acceptable.

D010: Fixed. design:124, spec:234/247, AC-008:311, architecture:269-272. Verdict fixed.

D011: Fixed (tasks:82-86). Gate only enforced at ready+; draft exempt. Verdict fixed.

D012: Fixed (tasks §4). But check_task_dag not enforced on draft. The claim "regression lock" not active. Verdict fixed in doc; gate deferred. Also need to verify edges are actually acyclic/forward. Let me manually check: T004->T017 forward. T003->T013. T005->T010, T005->T013. T007->T008->T029. T009->T020. F008.IR-002->T020 (non-T endpoint ignored). T013->T016->T017->T018->T019->T032 forward. T030/031/032/033/034/035->T036/037/038. T036/037/038->T039. T014->T015. T020->T021->T024->T029. T025->T027->T029. F004->T025 (ignored). T029->T035. All forward. T039 has incoming. Good.

Wait: F003 is draft, so check_task_dag skips it. So "全部通过" doesn't actually validate F003. That's important to state: the gate is vacuous for F003 at draft. Similarly D011's validate gate. So D011/D012 regression tests don't cover current F003 (draft). I'll note as residual "gate not active until status change" — severity medium/low, pattern gate-without-teeth.

Hmm, but the FIX-log regression tests for D011/D012 use synthetic fixtures (test_review_missing_test_group_rejected, check_task_dag tests) — they test the gate logic on synthetic input, so the gate itself works; it's just scoped to non-draft. This is acceptable by design per their docstrings. So verdict fixed, residual noted.

D013: Fixed. design:196-201, spec:263, AC-010:313, tasks:67. Kronos owner=F003. Also ADR? architecture §7.1 says? Let me verify architecture supports F003 as live owner. FIX-log says "架构 Kronos 卸载 owner 改 F003" in fcc14ad. But the architecture diff I saw only shows generator and pool changes... Wait, the diff a333394..HEAD for architecture only showed the generator comment + pool paragraph. It did NOT show a Kronos owner change! FIX-log fcc14ad says "架构 `generator` 增 `pool`、Kronos 卸载 owner 改 F003..." Hmm. Let me re-check: the diff output for docs/alphamill-architecture.md only had 2 hunks (generator comment and pool meta-factor paragraph). Maybe the Kronos owner change was already in architecture before a333394? Let me check architecture §7.1 for Kronos unload owner. Let me grep.

Actually the FIX-log claim could be inaccurate. Let me verify architecture §7.1 mentions F003 as owner of Kronos offload. If not, that's a cross-doc inconsistency: F003 claims live owner but architecture (truth source for machine boundary) may say F004. Let me grep.

D014: Fixed. F007 spec related_features F003 and upstream contract. Verdict fixed.

D015: Fixed. design:110 load contract. AC-001:304, AC-004:307. Verdict fixed.

D016: Fixed. design:105/114, spec:258 IR-003, AC-012:315, tasks T008/T012/T030. Verdict fixed. But note: AC-012 only covers unknown schema_version rejection + presence. Fine.

D017: Partially fixed mechanical. Let me examine AC_BODY_REQUIREMENTS vs actual. AC-011 needle "cli_contract" matches the test filename — arguably a weak/gamed assertion. Also Design §8 AC-011 row references `tests/unit/test_f003_cli_contract.py` now. Good. But the finding also mentioned "AC-003 增 DR-001 运行字段" — AC-003 body includes "DR-001 运行字段" per check. Yes spec:306 "含 termination/reason/时间戳与 DR-001 运行字段". Good.

D018: Fixed. design:122, spec:264, AC-009. Verdict fixed.

D019: Fixed. design:165 强制字段的构造; tasks T016/T027. Verdict fixed. But smoke subcommand: does smoke build a GenerationRequest? design:160 smoke has --day, --binding, --window, --config, --quota. T016 "并提供 smoke 的默认 config/window 构造". OK.

D020: Fixed. design:112, spec:246 DR-003, AC-009. Verdict fixed.

D021: Fixed. design:84, spec:149, AC-002:305, tasks T003/T013. Verdict fixed.

D022: Fixed. CLAUDE:51-53, docs/README:36, BACKLOG:8-10. Verdict fixed.

Now, extra semantic issues to hunt. Let me check:
- architecture Kronos owner
- F004 tasks references (D013 original location included F004 tasks:70-73). Did F004 get updated? The diff a333394..HEAD didn't include F004 tasks. So F004 tasks may still say Kronos unload owned by F004 (or not mention F003). Cross-feature mismatch? D013 fix claimed owner moved to F003 in F003 docs + architecture. But F004 tasks unchanged. Let me check F004 tasks lines 70-73 and architecture §7.1.

- Also "F004 交付（kronos-signal 服务编排）-> T025" dependency. F004 status? F004 might be done (CLAUDE previously listed F004 as active at a333394; now removed → F004 became done). If F004 is done but doesn't provide the container-orchestration service that F003 depends on, that's a "deferred-work-without-carrier" or cross-feature drift. Let me check F004 spec status and tasks.

Let me grep architecture §7.1 and F004.

Also check F007 spec: it now lists F008 as related and upstream; and FR-007/AC-009. Fine, but the user asked about F007 contract (D014) — fixed.

Another potential semantic issue: F003 spec:213 says L1→L2 triggered by "L1 连续 2 周满足 ADR-0001 判据（周候选 <50 或零候选通过无前视审计）". ADR-0001:49-50 says both are "满足任一条即触发". spec:280 matches. Good.

Another: spec:262 NFR-001 says window "22:00–06:30，≤8.5h" — 22:00 to 06:30 is 8.5h. correct.

Another: design:114 GenerationRun fields include `tier_level`, `window`, `objective`. AC coverage? AC-009 asserts GenerationRun records 引擎版本/绑定/seed/device/档位/逐级计数. tier_level yes. objective not in AC-009 but AC-006. universe in AC? AC-009 mentions 绑定; universe asserted in T035 and design §6. D017 didn't include DR-001 universe. Hmm spec DR-001 requires universe scale persisted, but no AC explicitly asserts `universe` in run.json. Actually AC-009's requirement list is (DR-002, DR-003, TR-001, NFR-003) — DR-001 not in AC-009. DR-001 is in AC-003 (which is about binding). AC-003 covers DR-001 "运行字段" but universe? AC-003 body says "含 termination/reason/时间戳与 DR-001 运行字段" — vague. Could be a gap: universe scale persistence not asserted by any AC. D017 suggested only "AC-003 增 DR-001 运行字段". The mechanical check accepts the literal token. Semantically weak. I'd flag: AC coverage for DR-001 universe/symbol_map_digest is only via the generic phrase "DR-001 运行字段". Medium.

Let me verify F004 and architecture Kronos.

Also "snapshot binding" theme: D005. design:120 explicit_tuples includes members keyed by dataset and symbol_map_digest, universe_calendar_digest, provenance. But note: DR-001 spec:244 mentions "universe_calendar_digest". F003 design:120 lists "universe_calendar_digest". However F007 DR-006 (new) says universe_calendar_digest is a *combined digest* of universe artifact + calendar artifact. F003's explicit tuple says `universe_calendar_digest` and separately `provenance` with universe_calendar_path. Hmm — is F003's single `universe_calendar_digest` aligned with F007's new two-artifact split (DR-006)? F007 now requires universe and calendar as two independent artifact references, with `universe_calendar_digest` = combination of two digests. F003 only carries one `universe_calendar_digest` + `provenance.universe_calendar_path`. And design:120 provenance lists `symbol_map_path, universe_calendar_path`. If F008/F007 split universe and calendar, F003's explicit tuple should arguably carry both universe digest and calendar digest (or at least align). The FIX-log fcc14ad says "provenance 补 ADR-0007 字段". But cross-feature contract: F007's DR-006 changed after F003's D005 fix. Did F003 align? F003 design:120 has `universe_calendar_digest` singular and provenance with `universe_calendar_path` singular. That may now be inconsistent with F007 DR-006 (universe and calendar separate). This is a genuine cross-feature contract drift introduced by the F007 fixes (D003/D004 in F007 round). Let me verify exact strings.

Actually let me check: F007 D004 fix (b251826 "universe 与 calendar 拆为两个独立 artifact 引用") happened, and F007 DR-006 now says universe_calendar_digest = combination of two digests. F003 still uses a single universe_calendar_digest field name (which is fine as a combined digest) but its provenance only has a single `universe_calendar_path`. ADR-0007 might define `universe_calendar_digest`. Need to read ADR-0007 to see canonical fields. Let me read it.

Also F003 design:120 provenance: `{created_at, artifact_path, member_manifest_paths, symbol_map_path, universe_calendar_path}`. ADR-0007's expected fields? Let's read.

Let me do these reads.
核对架构 §7.1 Kronos 归属、F004 载体、ADR-0007 字段与 F004 状态。

  <details><summary>tool output</summary>

  ```text
77:        GEN["生成器组<br/>AlphaGen · GP/表达式 · manual/LLM · Kronos"]
173:**单一 Python 布局 = `src/alphamill/<module>/`**（src-layout 已由 pyproject `[tool.hatch.build.targets.wheel] packages = ["src/alphamill"]` 固化）。概念模块名作为子包名：`alphamill/data_bridge`、`alphamill/factor_factory`、`alphamill/validation`、`alphamill/kronos_service` 等；非 Python 资产（docker-compose、`deployment/` 运维脚本、`docs/`）留在仓库根，不进包。全文档所有"平铺目录"（`data_bridge/`、`factor_factory/`…）表述一律指该布局。
199:    │   ├── bench/               # FR3.1：统一评测台（泛化 kronos_rankic_eval）
216:    │   └── writer.py            #   兼容 kronos_cache schema
227:    ├── kronos_service/          # Kronos 推理服务薄壳（自 quant-crypto 迁入）
262:    generator: str            # alphagen / genetic / expression / manual / kronos / pool（协同池 meta-factor）
274:成员集合或权重变化产生新 `factor_id`，不原地改写（契约详
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
---
kind: feature
id: F004
version: "0.2"
status: done
gate_version: 1
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-16
---

# F004：Kronos 真实推理运行时（编排内可复现）

---TASKS 60-80---
- [x] T013 (`AC-001`, `AC-002`): 执行机容器证据第二轮（review R002/R004 载体）：构建 kronos-service（mock/real 双目标）与 data-collector 镜像成功（验证 `.dockerignore` 白名单不破坏构建、上下文不含重资产）、容器内 `import alphamill` 成功；`ALPHAMILL_INTEGRATION=1` 重跑 F004 容器套件（含 compose config 双向断言、缺资产 exited+非零退出码、real 全链）并回写证据（hostname + device） — verify: 三个构建退出码 0 + `docker run --rm <镜像> python -c "import alphamill"` 退出码 0 + `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f004_real_profile.py tests/integ
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
### FR2 AI 因子工厂

- **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
  generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。
- **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
  生成器只产出 FactorDef/协同池定义，不拥有最终评测权。
- **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
  禁止只优化 RankIC。
- **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；前视、网络访问、隐式全样本统计和未支持的跨 pair
  算子直接拒绝，不得静默降级。


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:54Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git show --stat --oneline fcc14ad; echo \"=== full name-only ===\"; git show --name-only --pretty=format: fcc14ad; echo \"=== architecture mentions F003/F004 near 7.1 ===\"; sed -n '570,585p' docs/alphamill-architecture.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -rn \"停\\|stop\\|down\\|生命周期\\|lifecycle\\|编排\\|SIGTERM\\|卸载\" docs/features/0.2/F004-kronos-inference-runtime/design.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline a333394..HEAD -- docs/features/0.2/F004-kronos-inference-runtime/ docs/alphamill-architecture.md; echo \"=== commit f004 last change ===\"; git -C /home/georg/projects/alphamill log --oneline -3 -- docs/features/0.2/F004-kronos-inference-runtime/spec.md"})`


> [reasoning] Important findings:

1. **Architecture §7.1 does not mention F003 as Kronos offload owner** — architecture:577 says "训练窗口内 Kronos 卸载" but no owner. FIX-log claims "Kronos 卸载 owner 改 F003" in architecture fcc14ad, but the diff a333394..HEAD for architecture showed only generator/pool changes, and grep shows no F003/F004 near line 577. Let me check architecture lines 570-585 precisely and git log for architecture. Actually the FIX-log says fcc14ad changed architecture generator + pool + "Kronos 卸载 owner 改 F003". But the diff a333394..HEAD didn't show Kronos owner change. Maybe fcc14ad changed a different file or the claim is about F003 docs, not architecture. Let me verify with git show fcc14ad --stat.

2. **F004 status = done** and F004 does NOT provide the "kronos-signal 容器编排控制/服务生命周期" API that F003 T025 depends on. F004 delivered a real Kronos inference runtime (container), and "GPU 直通与推理性能优化 → 后移". F003 design:201 says "经 F004 交付的服务生命周期（容器编排控制）优雅停止 kronos-signal". Is that service lifecycle hook actually delivered by F004? F004 tasks show compose profiles, container integration, but no lifecycle/orchestration API for externally stopping the service. F003 tasks §4 adds dependency `F004 交付（kronos-signal 服务编排）-> T025`. But F004 is done and its scope doesn't include a stop/lifecycle contract for F003. This is a cross-feature carrier gap (D013 pattern "deferred-work-without-carrier"). The F004 spec §5 moved "消费者路由切换" but not stop orchestration. So F003 depends on an F004 deliverable that F004 never committed (F004 done). That's a genuine residual finding, high/medium. Category correctness, origin spec-drift, pattern deferred-work-without-carrier.

Wait, need to check if F004 design/spec mentions a lifecycle/stop capability. grep for "stop", "生命周期", "lifecycle", "SIGTERM", "compose down". Let me check.

3. **ADR-0007 provenance fields**: created_at, artifact_path, member_manifest_paths, symbol_map_path, universe_calendar_path. F003 design:120 provenance has exactly {created_at, artifact_path, member_manifest_paths, symbol_map_path, universe_calendar_path}. Matches ADR-0007 exactly. Good. So D005 fixed. Note ADR-0007 uses singular universe_calendar_path — consistent with F003. But F007's newer DR-006 splits universe and calendar into two artifacts, stating universe comes from F008 and calendar from F007, and universe_calendar_digest is a composite. ADR-0007 (truth source) still says single `universe_calendar_digest` / `universe_calendar_path` and "调用方提供的 universe/calendar JSON 由 experiment_store 规范化并保存于 .../universe_calendars/<digest>.json" (ADR-0007:72-75). This now conflicts with F007 DR-006: universe NOT copied into reports, located at `lake/_metadata/universes/<digest>.csv`; only calendar at `.../universe_calendars/<digest>.json`. And ADR-0007 says universe/calendar JSON provided by caller and saved by experiment_store. So there's a THREE-way drift: ADR-0007 (single artifact, both in universe_calendars), F007 DR-006 (two artifacts, universe from F008 lake/_metadata/universes, calendar in universe_calendars), F008 IR-002 (artifact at lake metadata). And F003 still uses single `universe_calendar_digest` + provenance universe_calendar_path.

This is exactly "snapshot binding" theme and cross-feature-contract-drift. D005 fixed F003 against ADR-0007, but F007's later D003/D004 fix (b251826, and F007 D003 5728ccc) introduced a split that ADR-0007 and F003 didn't follow. So residual: semantic inconsistency between ADR-0007 / F003 explicit tuple and F007 DR-006. Severity high (contract drift), category correctness, origin spec-drift, pattern cross-feature-contract-drift.

Hmm, but is F007 allowed to diverge from ADR-0007? F007's DR-006 explicitly says "ADR-0007 的 universe_calendar_digest 由两者 digest 组合导出（不再等于单一 JSON 文件摘要）". So F007 reinterpreted ADR-0007 rather than updating it. ADR-0007 not updated. That's a documentation drift: ADR-0007 says artifact path universe_calendars for both; F007 says universe lives in lake/_metadata/universes and not copied. Also ADR-0007:83-84 "universe/calendar artifact 由调用 F007 snapshot builder 的研究配置显式提供，不扩入 F002" while F008 now owns universe artifact in lake metadata. This is a real cross-doc inconsistency. Worth flagging as a finding (not one of D001..D022 but adjacent to D005). The user explicitly listed "snapshot binding" and "F007 contract" as themes. I'll include it.

4. Architecture:262 example factor_id "alphagen_gen042_f003" — stale vs content addressing. Low.

5. PRD FR2.1 line 153 says "适用状态" — F003 uses applicable_state. fixed. PRD FR2.3 line 157 includes 成本后收益. fixed.

6. F004 done and D022 index: CLAUDE now lists F003/F007/F008 (F004 removed because done). Good.

Let me check F004 for lifecycle/stop contract and git show fcc14ad to see whether architecture got the Kronos owner change.

Also I should check whether F003's dependency on F004 contradicts F004's done state. The tasks reference "F004 交付（kronos-signal 服务编排）". If F004 didn't deliver a control API, F003 T025's approach may be unimplementable as written. But maybe "容器编排控制" just means docker compose stop, which the operator/F003 can invoke via compose; F004 delivered the compose profiles. Then "经 F004 交付的服务生命周期" = the compose service. Possibly acceptable. But the wording "F004 交付的容器编排控制" suggests an API. Let me check F004 design for anything about being stopped by external scheduler.

Let me run git show fcc14ad --stat and grep F004 design for stop/lifecycle.

  <details><summary>tool output</summary>

  ```text
fcc14ad fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
 docs/alphamill-architecture.md                   |  6 +++++-
 docs/features/0.2/F003-alphagen-vendor/design.md | 10 +++++-----
 docs/features/0.2/F003-alphagen-vendor/spec.md   |  6 +++---
 docs/features/0.2/F003-alphagen-vendor/tasks.md  | 14 +++++++-------
 4 files changed, 20 insertions(+), 16 deletions(-)
=== full name-only ===
docs/alphamill-architecture.md
docs/features/0.2/F003-alphagen-vendor/design.md
docs/features/0.2/F003-alphagen-vendor/spec.md
docs/features/0.2/F003-alphagen-vendor/tasks.md
=== architecture mentions F003/F004 near 7.1 ===
**单卡 GPU 时段调度（当前执行机 `qiaozhi-lt`，RTX 4060 Laptop 8GB）**

三个 GPU 负载（Kronos 常驻推理 / AlphaGen 夜间训练 / Vibe MC）共用一张卡，采用**时段表 + 单槽队列**，不做 OOM 赌博：

| 时段 | 负载 | VRAM 预算 | 说明 |
|---
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
20:- **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）
51:**real 目标的依赖 pin（镜像内）**：`torch==2.14.0`（`--index-url https://download.pytorch.org/whl/cpu`，CPU wheel；与宿主 AC-006 实测同版）+ `einops==0.8.2`、`safetensors==0.8.0`、`huggingface_hub==1.31.0`、`tqdm==4.70.0`——pin 上游直接 import 的最小集（`model/kronos.py` 导入 torch/huggingface_hub/tqdm，`model/module.py` 导入 einops），版本取宿主 AC-006 实测集，以容器内真实权重加载验证后锁定；上游 `requirements.txt` 仅作参考。
78:- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。
98:| 用 compose profile 而非新建服务文件 | 单一 compose 文件，默认不启用 | 避免多份编排入口（F001 的教训：编排必须唯一） | 若 profile 组合变复杂再拆 override 文件 |
100:| profi
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
fcc14ad fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
=== commit f004 last change ===
2d5eace docs(f004): T013 回写 spec §6 第二轮执行机容器证据（三构建/import/容器套件 7 passed）；状态收口 review → done；BACKLOG 移出
4bcf1fd docs(f004): R003 回写 spec §6 验收证据——门禁计数勘正 26/20/13、依赖与构建上下文条目
07dd1dd chore(f004): F004 状态 draft → review，BACKLOG 同步（T012）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:10Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git show fcc14ad -- docs/alphamill-architecture.md; echo \"=== grep F003 in architecture ===\"; grep -n \"F003\" docs/alphamill-architecture.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '30,50p' docs/features/0.2/F003-alphagen-vendor/design.md; echo \"=== grep line nums for key strings ===\"; grep -n \"kronos_offload\\|live owner\\|queue_seq\\|termination=queue_timeout\\|SIGTERM\\|status=partial\\|explicit_tuples\\|universe_calendar_digest\\|universe_calendar_path\\|applicable_state\\|min_after_cost_return\\|config_digest\\|加载契约\" docs/features/0.2/F003-alphagen-vendor/design.md"})`


> [reasoning] fcc14ad changed architecture by 6 lines (+++++-). Let me see the actual diff of fcc14ad for architecture. The a333394..HEAD diff I saw for architecture was 6 lines: 1 generator comment change + 5 pool paragraph. That's the total a333394..HEAD, so the "Kronos owner 改 F003" was NOT an architecture change. Let me check git show fcc14ad -- docs/alphamill-architecture.md.

Actually git show --stat says docs/alphamill-architecture.md | 6 +++++- which is the pool paragraph (5 additions + 1 context?). Combined with earlier commits? Let me just show it.

  <details><summary>tool output</summary>

  ```text
commit fcc14adaea11c3ae285d821373d293061af504b0
Author: qiaozhi li <qiaozhi_li@126.com>
Date:   Wed Sep 16 23:38:17 2026 +0800

    fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
    
    Oracle 二轮复核（fix-verification 预检）发现的 6 项：
    1. 架构 §4.1 generator 增 pool 并补协同池 FactorDef 契约段（D010 收口）。
    2. Kronos 夜槽卸载 live owner 由「F004 提供控制契约」改为 F003 编排（经 F004 交付
       的容器生命周期，fail-closed 留队列），移除无载体的 offload_contract_unavailable
       与被动的 F004 后移条目（D013 收口）。
    3. explicit_tuples provenance 补 created_at/artifact_path（对齐 ADR-0007）。
    4. T036/T038 的 verify 命令补齐其声称覆盖的测试文件。
    5. AC-012 纳入 T030/T031 验证载体。
    6. CLI seed 子命令 --seed 改必填（禁止隐式默认 seed）。

diff --git a/docs/alphamill-architecture.md b/docs/alphamill-architecture.md
index cda411a..9625196 100644
--- a/docs/alphamill-archi
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
- **湖与训练同机**：执行机同时承载 TimescaleDB、导出与挖掘训练，`lake_root` 指向本机湖目录，没有跨机数据传输问题；NAS 仍只承担 F002 的备份职责。
  - **迁移前瞻**：显存上限、时段表、耗时/产能相关的值必须可配且写入运行记录，**不得写死常数**。迁移不只是换卡：平台从 Win11+WSL2 变成原生 Ubuntu，GPU 架构从 Ada 变成 Blackwell sm_120（**torch 必须是 CUDA 12.8+ 的构建，默认 wheel 不一定含该架构**），因此 `mining` extra 的 pin 要显式选择带 sm_120 的轮子。

## 1. 技术概要与影响面

三层结构，自外向内：**生成器平面（接口 + 两个后端 + 持久化 + CLI）→ 胶水层（数据面 / 适配器 / 算子登记 / 目标对齐 / 调度）→ vendor（AlphaGen 核心，原样最小 diff）**。依赖方向严格单向 `平面 → 胶水 → vendor`，vendor 不认识 alphamill。挖掘运行读 F002 湖快照构造张量，训练产出表达式，胶水层把表达式编译为 `FactorDef` 并做生成侧自检，最后把候选与协同池以内容寻址 JSON 落到 `reports/generation/<run_id>/`，同时写 append-only 事件供 F007 的漏斗第一级消费。

- 前端：不适用（无 UI；只读展示归 F005，ADR-0005）
- 后端 / API：新增 `src/alphamill/factor_factory/{generators,hypotheses,registry}/` 与 `cli.py`；不改 F002 任何模块，只调用其只读 reader
- 存储 / Migration：无数据库
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:35:23Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== F004 lifecycle/control terms ===\"; grep -rn \"control\\|graceful\\|compose down\\|停止\\|停用\\|生命周期\\|lifecycle\\|stop\" docs/features/0.2/F004-kronos-inference-runtime/spec.md docs/features/0.2/F004-kronos-inference-runtime/design.md docs/features/0.2/F004-kronos-inference-runtime/tasks.md | head -30; echo \"=== F003 leftover terms ===\"; grep -rn \"run_seq\\|pool_id\\|AlphaPoolDef\\|降级到 L1/L2\\|无网络出口\" docs/features/0.2/F003-alphagen-v
…[truncated])`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"AC-00[0-9]\\|AC-01[0-2]\\|TR-001\\|partial\\|failed\\|universe\" docs/features/0.2/F003-alphagen-vendor/spec.md | sed -n '1,80p'"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git log --oneline a333394..HEAD | wc -l; echo \"=== status draft? ===\"; grep -n \"^status:\" docs/features/0.2/F003-alphagen-vendor/spec.md docs/features/0.2/F007-evaluation-gates/spec.md docs/features/0.2/F008-universe-expansion/spec.md"})`


> [reasoning] Confirmed: fcc14ad commit message claims "Kronos owner 改 F003" but the actual architecture diff has NO Kronos owner change. So architecture §7.1 still says only "训练窗口内 Kronos 卸载" with no owner. The F003 docs now say live owner = F003. Is that a contradiction? Not necessarily — architecture doesn't state an owner, so F003's claim isn't contradicted; it's just not reflected in architecture. But the commit message overstates. More importantly: F003 assumes F004 delivered a "service lifecycle (container orchestration control)" to gracefully stop kronos-signal. F004 is done and its scope does not include any lifecycle/stop control API — F004 delivered compose profiles + container integration tests. F004 tasks §5 explicitly deferred routing switch. Nothing about an external stop API. So F003 T025's dependency on "F004 交付的容器编排控制/服务生命周期" lacks a carrier; and F004 is done, so it can't be added without reopening a done feature. That's a real finding. Pattern: deferred-work-without-carrier, cross-feature-contract-drift.

Let me double check F004 design for any "control" interface. grep gave nothing about stop/lifecycle. Let me grep spec.

Also check F003 design:201 says "经 F004 交付的服务生命周期（容器编排控制）优雅停止 kronos-signal". If F004 has no such deliverable, F003's claim is unbacked. Also, architecture §7.1 says the machine hosts one executor at a time and the unload is required; F003 is now claiming to own it but F004 (owner of kronos_service) is done. This is a residual cross-feature gap.

Now let me also verify the `universe_calendar_digest` vs F007 DR-006 conflict more carefully. ADR-0007:40 has universe_calendar_digest. F007 DR-006 now says universe+calendar split into two artifacts, universe at lake/_metadata/universes, calendar at reports/.../universe_calendars, and universe_calendar_digest = combination. F003 design:120 keeps single universe_calendar_digest + provenance.universe_calendar_path pointing to one artifact. But F003 design:121 says "字段与 ADR-0007 的成员/身份契约一一对应". ADR-0007 hasn't been updated to reflect the split. So there's a 3-way drift. Also note F003 D006 references F008 IR-002 universe_at. The F008 artifact path is lake/_metadata/universes per F007. F003's explicit tuple doesn't carry a separate universe digest or universe artifact path; it has universe_calendar_digest (could be composite) and universe_calendar_path (single path). Hmm, F003's binding needs to reference the F008 universe artifact (for PIT mask) — design §4 (line 167?) says time_series/cross_sectional. design:82 says "F008 未落地时用显式 universe 配置并把其 digest 与来源写进 run.json". So F003 sometimes reads universe from config. But the explicit_tuples binding structure lacks a distinct universe artifact reference field. Given F007 D004 explicitly split universe from calendar, F003 should too. This is a genuine semantic drift adjacent to D005/D006. Severity high or medium. I'll call medium-high. Let's classify as high since it affects snapshot identity contract (research reproducibility red line). Category correctness, origin spec-drift, pattern_tag cross-feature-contract-drift.

Actually, wording: F003 design:120's `universe_calendar_digest` name matches ADR-0007 exactly, so D005 fixed. The drift is that ADR-0007 / F003 use a single combined digest+path, while F007 DR-006 requires two separate artifacts. Since ADR-0007 is the truth source for the snapshot contract and F003 explicitly aligns to it, the inconsistency is arguably F007's (not F003's). But the user asked about F003 docs semantic correctness; the cross-doc inconsistency is real and impacts F003's transition binding (it won't be able to reference the F008 universe artifact by digest distinctly). I'll report it as a residual cross-feature finding, verdict for D005 = "fixed (as scoped), but new drift introduced by F007 D004 not propagated to F003/ADR-0007".

Now let me also examine the F003 design:120 `members` keyed by dataset — D005 fix. Good.

Other possible issues:
- design:103 says run.json "字段至少含 status、termination、reason、started_at/finished_at". For `partial`, no `reason`? fine.
- spec:251 TR-001 payload includes counts; design:173 same.
- D002 terminal manifest: design:96 says four states all write; but design:100 checkpoints "可清理，不属于证据". fine.

- D003: spec:280 says L1→L2 when "周候选 <50 或零候选通过无前视审计". ADR-0001:49 "L1 连续 2 周每周进评测台候选 <50". Slight wording: "每周...<50" vs "周候选 <50". Fine.

- D004: spec:215-218 obligations. design:211 says manifest carries both obligations. tasks:52,112. Good. But ADR-0001:57 funnel obligations reference PRD FR3.8/FR7.5. F003 only handles generation first level. Fine.

- D007: AC-011 "断言范围为进程级护栏，非内核隔离". Good. But NFR-004 says "只放行 AF_UNIX" — socket constructor replaced. It also says both guards fail-closed. Good.

- D009: spec:197 now includes 成本后收益. Good.

- D010: AC-008, design:124, architecture updated. Good.

- D013: FIFO protocol, Kronos owner. But as noted, owner carrier gap. D013's own suggested fix: "为 Kronos 卸载钉 live owner（F003 加编排任务或 F004 加任务并登记跨 feature 边），写明 F004 后移时 FIFO 如何取证". They added T025 and the F004 dependency edge. But F004 is done and has no such deliverable. Also the fix explicitly says "F004 交付未部署（该服务不存在）→ 记 offload_not_needed" in design:201. Hmm, actually design:201 handles "F004 交付未部署（该服务不存在）→ 记 offload_not_needed". So if F004 didn't deliver a lifecycle service, F003 records offload_not_needed and proceeds? But kronos-signal IS deployed (F004 done, real runtime). So F003 would need to stop it. If there's no stop control, F003 can't. The conditional "F004 交付未部署（该服务不存在）" only covers non-deployment, not "deployed but no stop API". This is the gap. So D013 has a residual: owner assigned, but the F004-side carrier for the stop/lifecycle control doesn't exist and F004 is done. Verdict: partially fixed. Severity high (blocks T025 implementation), category correctness, origin spec-drift, pattern deferred-work-without-carrier.

Let me confirm F004 spec/design truly has no lifecycle/stop deliverable. grep found nothing for stop/lifecycle in design. Let me grep spec + full F004 for "control", "graceful", "compose down", "停".

- D012: task order fixed; but check_task_dag not enforced on draft. Also note: T036/T037/T038 [TEST] entries appear after §3 heading and before T039, but they're within section 3. Fine. However, the [TEST] group placement: T039 is outside the [TEST] subgroup but in §3. Good.

Potential D012 residual: §4 edge `T030/T031/T032/T033/T034/T035 -> T036/T037/T038`. The gate check_task_dag only checks src<dst and endpoints defined and last task has incoming edge. T039 has incoming from T036/037/038. Good. All forward.

But wait: check_task_dag skips draft, so "全部通过" isn't evidence. Yet the fix is in the doc. I'll note.

- D017 residual: AC-011 needle "cli_contract" is satisfied only by the `tests:` path, i.e., the gate is gameable. Also AC for `partial`/`failed` non-emission missing. Also AC-006 doesn't assert `universe` persisted. And DR-001's universe requirement lacks a strong AC. Let me flag "AC 覆盖仍以字面 token 匹配为主，语义断言缺口：非 completed 终态不发 run_completed、DR-001 的 universe 字段无显式断言". Severity medium, category test-coverage, origin process-gap, pattern gate-without-teeth.

Actually let me verify AC_BODY for AC-003 and whether "DR-001 运行字段" is the literal. Yes design spec line 306 has it. This is a vague phrase. OK.

- D016: AC-012 covers schema_version presence + show rejection. Fixed.

- D019: CLI `seed` requires --seed; design:165. `smoke` has no --seed, but smoke is a gate command, not produce() request. Fine.

- D021: baseline sha256; AC-002; T003; T013. Fixed. But note: `_upstream_baseline.json` doesn't exist yet (feature is draft, no implementation) — expected. Fine.

- D022: fixed. Verify docs/README:36 text "当前 F003/F007/F008". The README read shows line 36 (in table) "非 done Feature 派生索引 | `../BACKLOG.md` | 活跃 feature 索引（当前 F003/F007/F008）". Good. CLAUDE 51-53. Good.

Now, let me also check the `architecture:259` stale example factor_id. And check whether any other F003 doc uses old factor_id format.

grep "gen042" or "_f003".

Also check spec:289 invariant "(run_id, seed, 快照绑定, 表达式原文)" rebuild — consistent.

Let me also search for remaining "pool_id" or "AlphaPoolDef" anywhere (should be removed). And "run_seq". And "降级到 L1/L2". check passed, but let me grep F003 docs to be thorough.

Let me run these greps and F004 spec grep.

  <details><summary>tool output</summary>

  ```text
=== F004 lifecycle/control terms ===
docs/features/0.2/F004-kronos-inference-runtime/spec.md:109:## 5. 生命周期与不变量
docs/features/0.2/F004-kronos-inference-runtime/spec.md:111:不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：
docs/features/0.2/F004-kronos-inference-runtime/tasks.md:54:- [x] T012: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期与 BACKLOG 双向校验）
=== F003 leftover terms ===
docs/features/0.2/F003-alphagen-vendor/design.md:62:│   ├── egress_guard.py       # 进程级无网络出口护栏（NFR-004）
docs/features/0.2/F003-alphagen-vendor/design.md:124:**协同池 meta-factor**：`pool.json` 持久化为**可执行 `FactorDef`**（`generator="pool"`、`scope="cross_sectional"`、`factor_id = pool_<definition_digest[:12]>`），其 `params`/`meta` 携带成员引用与权重 `members: [{factor_id, weight}]`、`run_id` 与 `pool_version`；`compute`
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
102:- 快照绑定的湖→张量数据面（读 F002 reader，point-in-time 宇宙掩码取 F008 的 `universe_at(T)` 与内容寻址台账 digest，特征列→张量通道 `feature_map`）；
112:- ResearchSnapshot 的实现（归 `experiment_store/`，随 `F007` 落地）——F003 只消费绑定，冒烟期用显式元组过渡（Q-002）；过渡元组须携带与 ADR-0007 对齐的语义字段（`schema_version`、`cutoff_time`、逐 dataset `as_of_fidelity`/`event_time_min`/`event_time_max`、`symbol_map_digest`、`universe_calendar_digest` 与不可变 artifact 的 provenance 引用），仅不落 snapshot artifact；F007 落地时须先发布 `ResearchSnapshot` 再替换为 `snapshot_id`（ADR-0007 决策 4/5）；
244:- **DR-001**：`GenerationRun` 应当持久化快照绑定（`research_snapshot_id`，或过渡期的显式元组：`schema_version`、`cutoff_time`、逐 dataset 成员映射 `{<dataset>: (data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)}`、`symbol_map_digest`、`universe_calendar_digest` 与不可变 artifact 的 `provenance` 引用——字段与身份语义与 A
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
37
=== status draft? ===
docs/features/0.2/F003-alphagen-vendor/spec.md:5:status: draft
docs/features/0.2/F007-evaluation-gates/spec.md:5:status: draft
docs/features/0.2/F008-universe-expansion/spec.md:5:status: draft


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:41Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== F007 tasks AC refs ===\"; grep -n \"T027\\|T028\\|T029\\|AC-010\\|AC-011\\|AC-012\" docs/features/0.2/F007-evaluation-gates/tasks.md; echo \"=== F007 spec AC list ===\"; grep -n \"AC-0\" docs/features/0.2/F007-evaluation-gates/spec.md; echo \"=== F007 DR-006 ===\"; grep -n \"DR-006\\|universe_calendar_digest\\|universe_at(T)\" docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== F004 spec 105-115 ===\"; sed -n '105,115p' docs/features/0.2/F004-kronos-inference-runtime/spec.md; echo \"=== F004 tasks section5 ===\"; sed -n '70,75p' docs/features/0.2/F004-kronos-inference-runtime/tasks.md; echo \"=== architecture 256-275 ===\"; sed -n '256,275p' docs/alphamill-architecture.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== F003 tasks §4 lines ===\"; grep -n \"F004\\|T025\\|live owner\\|F008.IR-002\\|T039\" docs/features/0.2/F003-alphagen-vendor/tasks.md; echo \"=== F003 design lines 195-202 ===\"; sed -n '194,202p' docs/features/0.2/F003-alphagen-vendor/design.md"})`


> [reasoning] Now I have enough to produce verdicts. Let me also double-check a couple of subtle semantic issues.

Issue: D006 says PIT mask consumes F008 universe_at(T). design:82 explicitly. F008 IR-002 confirmed. Fixed.

Issue: spec:328 says "ADR-0007 的 ResearchSnapshot 语义字段（... universe_calendar_digest）". F007 split not reflected. Yes drift.

Issue: design:124 says pool factor_id = pool_<definition_digest[:12]>. Spec AC-008/DR-004 say generator="pool". factor_id prefix "pool" not generator "pool". Minor, consistent.

Issue: design:124 says `pool_version` in params/meta, but DR-004/spec says "池版本". Fine.

Issue: D002: spec:306 AC-003 says "留 `rejected` 终态 run.json". design:216 failure mapping. `failed` terminal run.json writing — design:200 says non-controlled exception writes `status=failed` terminal run.json; if write fails, dir incomplete. Good.

Now the D002 verdict: fixed.

Let me also check the F003 design §8 AC-011 row (line 236) references test_f003_cli_contract.py — verified earlier: line 236 shows `tests/unit/test_f003_cli_contract.py`. Good, D017 naming fixed.

Now about the `[TEST]` gate and task DAG gate being inactive for draft: This matters for "fixed/not-fixed" verdict? The findings D011/D012 are about tasks.md content. Content is fixed. The regression gates are scoped out for draft by design. I'll mark fixed with a residual note (medium) for both: "门禁作用域仅 ready+，draft 期间不实际校验 F003，回归锁定延后到状态推进".

Actually the user asked for "fixed/not-fixed verdict for each D001..D022" — main answer is a table. I'll add "残余" column / notes.

Now, are there any D items that are genuinely NOT fixed? Let me scrutinize:

- D002 suggested `rejection.json/failure.json`; actual used unified run.json. The finding's core was "REJECTED/FAILED 终态事实与原因未持久化". Now persisted in run.json. Fixed (different mechanism, still satisfies). 

- D017: mechanically fixed but the check is token-literal. Semantically, AC-003's "DR-001 运行字段" is vague; AC-010 covers hostname/queue_seq; AC-011 "cli_contract" matched via test path — that's arguably gaming. Is D017 fixed or not? I'd say "部分修复（partial）": doc text updated, but the regression assertion for AC-011 is satisfied only by the test filename, not by an AC-body clause about CLI mismatch. Actually the D017 suggested fix item "AC-011 修正 CLI 测试文件命名不一致（design:226）" — the actual inconsistency was that design §8 AC-011 row listed only `tests/integration/test_f003_boundaries.py` while spec AC-011 listed two files; the fix harmonized. That's now consistent. So D017 fixed mechanically. But new semantic gaps remain (partial/failed, universe). I'll mark D017 "fixed（字面）/部分（语义）". Hmm, to be decisive: fixed, with residual findings listed separately.

Let me decide per-D verdicts:

D001 fixed
D002 fixed
D003 fixed
D004 fixed
D005 fixed (but see F003-D005-R new drift with F007 DR-006)
D006 fixed
D007 fixed
D008 fixed
D009 fixed
D010 fixed
D011 fixed (gate inactive at draft)
D012 fixed (gate inactive at draft)
D013 partial (owner assigned in F003; F004 carrier absent & F004 done; architecture §7.1 has no owner statement)
D014 fixed
D015 fixed
D016 fixed
D017 fixed (mechanical; residual semantic AC gaps)
D018 fixed
D019 fixed
D020 fixed
D021 fixed
D022 fixed

New/residual findings (not in D list but relevant):
N1 (high): F003 T025/design:201 depends on "F004 交付的服务生命周期（容器编排控制）" but F004 is done and delivered no such control/lifecycle deliverable; F004 tasks §5 defers routing only. Cross-feature carrier gap. Location: F003 design:201, tasks:67,104; F004 spec:109-111, tasks §5; F004 status done. Pattern: deferred-work-without-carrier.
N2 (high/medium): universe_calendar drift: ADR-0007:40-42/72-75 keeps single universe_calendar_digest + universe_calendar_path and says caller-provided universe/calendar JSON saved to reports/.../universe_calendars; F007 DR-006/AC-006 (spec:214-216? let me get exact lines) splits universe (F008, lake/_metadata/universes, not copied) and calendar. F003 design:120/121 still single combined field + single universe_calendar_path, spec:112/244/328. Pattern cross-feature-contract-drift.
N3 (low): architecture:259 example factor_id "alphagen_gen042_f003" contradicts new content-addressed factor_id (design:108). Pattern spec-internal-contradiction / stale-example.
N4 (medium): AC coverage: no AC asserts non-completed terminal states (partial/failed/rejected) do NOT emit generation.run_completed (TR-001 negative), nor that DR-001 `universe`/`symbol_map_digest` are persisted; AC-003 uses vague "DR-001 运行字段". Also check_doc_consistency AC-011 needle "cli_contract" is satisfied by the tests: filename, making the D017 regression gameable. Pattern gate-without-teeth.
N5 (medium/low): D011/D012 gates scope {ready-for-development,in-progress,review}; F003 draft, so no live enforcement now. Pattern gate-without-teeth (deferred). Not a defect per se but a coverage note.

Also maybe: F007 task T027 references AC-011/AC-012 which don't exist in F007 spec (its ACs go to AC-009). But that's F007 scope, out of F003. The user said focus D001..D022 F003. Skip or mention lightly? Actually F007 tasks T027 says (`US-001`, `AC-001`, `AC-011`) and T028 (`..., AC-010, AC-012`) — F007 only has AC-001..AC-009. That's a reference error in F007 tasks introduced by D011 fix (32f4942). But that's F007 finding, not F003. The user's scope: "F003 docs ... F007 contract" theme. Hmm, "F007 contract" likely refers D014 (F007 declares F003 upstream). But F007 AC refs AC-010/011/012 nonexistent is a real defect, though outside F003. I could mention as adjacent observation. Let me verify F007 tasks lines. From diff: T027 (`US-001`, `AC-001`, `AC-011`), T028 (... `AC-010`, `AC-012`), T029 (`US-003`, `AC-005`, `AC-007`, `AC-008`). F007 spec has AC-001..AC-009 (we saw AC-009 added). So AC-010/AC-011/AC-012 are undefined references. That's a genuine traceability bug. But the user asked F003 audit with F007 contract theme. I'll include as adjacent (medium), clearly marked out-of-F003-scope.

Hmm, actually wait. Let me re-read the user request: "Read-only audit /home/georg/projects/alphamill current F003 docs against a333394..HEAD, focusing D001..D022 and semantic correctness. Check ... F007 contract, schema/version and AC coverage." So F007 contract theme = D014. But since they said semantic correctness broadly, and the F007 task AC refs are broken, it may be worth a brief mention. But the primary deliverable is D001..D022 verdicts. I'll add a short "相邻发现" section.

Let me verify F007 task lines to get exact line numbers. And architecture:259 exact. And F004 spec:109-111. And F007 spec DR-006 line numbers.

Let me get these precise line numbers.

  <details><summary>tool output</summary>

  ```text
=== F007 tasks AC refs ===
27:- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账的负例） — verify: `tests/integration/test_f007_execution_tiers.py`
50:- [ ] T015 (`FR-006`, `UX-002`, `AC-005`, `AC-011`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推；断言 `approximation` 标注存在且 canonical 恒为非近似 — verify: `tests/contract/test_f007_artifact_schemas.py`
71:- [ ] T027 [TEST] (`US-001`, `AC-001`, `AC-011`): 旅程 US-001 端到端验收——固定 fixture 连跑两次 preview：报告在排除 provenance 时间戳后稳定、canonical 台账与留出预算台账均零行、preview 越权写 official population/留出被拒并留 `evaluation.gate_rejected`、CLI 首屏含 tier/data digest/首个失败原因、近似标注在报告中显式可见 — verify: `pytest -q tests/integration/test_f007_execution_tiers.py tests/integration/test_f007_cli.py`
72:- [ ] T028 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== F004 spec 105-115 ===
### 非功能需求

- **NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（`mock` 构建目标）不含 torch，profile 未启用时不启动、不构建 real 服务。

## 5. 生命周期与不变量

不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：

- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**；
- **串行推理**：进程内模型加载至多一次、推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；
- **默认隔离**：未启用 profile 时默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。
=== F004 tasks section5 ===
## 5. 明确后移

- GPU 直通与推理性能优化 → `v0.2.x` 后续评估：需执行机 GPU 直通条件，不属本 feature。
- 消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 指向真实实例）→ `v0.2.x` 后续评估（未立项）：真实实例与 mock 并存是本期形态，路由切换涉及默认链路可用性与跨 feature 契约，F004 只交付编排内可复现的真实信号源（spec §3 范围外）。
=== architecture 256-275 ===
```python
@dataclass(frozen=True)
cla
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== F003 tasks §4 lines ===
67:- [ ] T025 (`NFR-002`, `AC-010`): 实现 `gpu_slot`——显存自检（上限可配，不写死常数）、flock 单槽 FIFO（`queue_seq` / 取锁 / 释放 / 超时状态记录）、训练窗口校验、`--allow-cpu` / `--allow-offhours` 显式开关，运行记录写 `hostname` / `device` / `kronos_offload`；并实现夜槽切换的 Kronos 卸载编排（**live owner = F003**）：经 F004 交付的容器编排控制优雅停止 `kronos-signal`、校验显存释放、窗口结束恢复，停止失败或显存未释放则 fail-closed 留在 FIFO（不向未知进程发 signal） — verify: `tests/unit/test_f003_gpu_slot.py`
88:- [ ] T039: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter — verify: `python3 tools/validate_spec_lifecycle.py`
97:- `F008.IR-002 -> T020`：PIT 掩码依赖 F008 的内容寻址宇宙台账（`universe_at(T)` 与 digest、IR-003 的 `schema_version`）；F008 未落地前 T020 用显式 universe 配置并在 `run.json` 记录 digest 与来源，任何情况下都不得用当前成员表回填历史。
100:- `T036/T037/T038 -> T039`：三条旅程验收全绿后才回写 spec 验收证据与状态。
103:- `T02
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:37:19Z


> [reasoning] Now I have solid evidence. Note F007 spec AC-011 exists now (line 293) — my earlier assumption of only AC-001..AC-009 was wrong because there are more ACs added by another finding? Actually F007 spec has AC-011 (line 293), and AC-010/AC-012 referenced in tasks — do AC-010 and AC-012 exist in F007 spec? The grep for "AC-0" in F007 spec returned AC-001..AC-009 and AC-011. No AC-010, no AC-012. So F007 tasks T003 references AC-010 (undefined), T028 references AC-010 and AC-012 (undefined), T015/T027 reference AC-011 (defined). So F007 AC-010/AC-012 refs are dangling. But this is F007, not F003. Out of scope but worth a one-liner.

Wait, grep pattern "AC-0" only matches AC-0xx. AC-010, AC-011, AC-012 all start with AC-01... "AC-0" matches "AC-01" prefix? "AC-010" contains "AC-01" so "AC-0" matches. The grep returned lines 284-293 with AC-001..AC-009 and AC-011. So AC-010 and AC-012 absent. But maybe they're defined with different formatting (e.g., not starting with "- [ ]"?). Let me not over-invest; it's out of F003 scope. I'll mention briefly.

Now I need exact line numbers for F003 spec and design citations. Let me compile.

F003 spec current lines (from read):
- 43 (目标): L1→L2 不在 time-box
- 74? Actually US-002 independent test line 74. Let me recheck: spec lines 68-80 US-002. Line 74 is "独立测试" mentioning ADR-0001 L1 三条判据 + two M2 obligations. Yes line 74.
- 92 US-003 scenario: 入册 ≥50
- 112: 范围外 snapshot
- 121: 边界 scenario Kronos
- 122: egress scenario
- 149-155: FR-002 vendor hygiene (149 is the requirement paragraph; 153-155 scenarios)
- 169-171: FR-003 binding scenarios (169 Scenario 绑定失效? let me recheck: 167 Scenario 绑定失效, 169 GIVEN... Actually lines 167-171). From read: 167 "#### Scenario: 绑定失效", 169 "- GIVEN ...", 170 "- WHEN", 171 "- THEN". 
- 197: FR-005 paragraph
- 213: FR-006 paragraph
- 215-218: M2 obligations
- 227-235: FR-007 (232 heading, 234 paragraph)
- 244: DR-001
- 245: DR-002
- 246: DR-003
- 247: DR-004
- 251: TR-001
- 252: TR-002
- 258: IR-003
- 262-266: NFR
- 263: NFR-002
- 264: NFR-003
- 265: NFR-004
- 266: NFR-005
- 271-282: lifecycle
- 280: L1→L2
- 284-291: invariants
- 304-315: AC-001..AC-012
- 328: dependencies
- 337: decision table snapshot

F003 design current lines:
- 16-18 前置约束
- 55 lake_tensor PIT
- 58 objective.py
- 82 PIT

## assistant · 2026-09-16T16:37:32Z


> [reasoning] I have enough. Let me write the audit report in Chinese, structured, with a D001..D022 table with fixed/not-fixed verdicts, plus residual findings with file:line, severity, category, origin, pattern_tag.

Let me be precise on line citations.

D001: design.md:108 (factor_id), spec.md:245 (DR-002), spec.md:312 (AC-009). Fixed.

D002: design.md:96,103,104,216; spec.md:251,271,287,306,314. Fixed.

D003: spec.md:43,213,280; design.md:255; AC-007 spec.md:310. Fixed.

D004: spec.md:74,215-218,310; design.md:116,211; tasks.md:52,85,112. Fixed.

D005: design.md:120,121; spec.md:112,244,328,337; ADR-0007:31-43. Fixed.

D006: design.md:55,82; spec.md:102,328; tasks.md:59,97; F008 spec:243-244. Fixed.

D007: spec.md:122,265,314; design.md:218,251. Fixed.

D008: design.md:200; spec.md:251,276,287. Fixed (doc); residual no AC for partial.

D009: design.md:58,114; spec.md:197,309; PRD:157. Fixed.

D010: design.md:67,124; spec.md:234,247,311; architecture:269-274. Fixed.

D011: tasks.md:82-86; tools/validate_spec_lifecycle.py:60-63,210-211. Fixed (gate scope excludes draft).

D012: tasks.md:90-106,88,100; tools/check_task_dag.py:27,150. Fixed (scope excludes draft).

D013: design.md:196-201; spec.md:263,313; tasks.md:67,104. Partial (carrier gap).

D014: F007 spec.md:7,22-23; F007 design.md:5,25-26,175-181. Fixed.

D015: design.md:110; spec.md:304,307; tasks.md:40. Fixed.

D016: design.md:105,114; spec.md:258,315; tasks.md:41,45. Fixed.

D017: spec.md:306,308,309,312,313,314; design.md:236; check_doc_consistency.py:257-263. Fixed (mechanical) + residual semantic gaps.

D018: design.md:122,199; spec.md:264,312. Fixed.

D019: design.md:156-166; tasks.md:52,69; spec.md:256. Fixed.

D020: design.md:112; spec.md:246,312; PRD:153; tasks.md:39. Fixed.

D021: design.md:84; spec.md:149,305; tasks.md:31,49. Fixed.

D022: CLAUDE.md:51-53; docs/README.md:36; BACKLOG.md:8-10. Fixed.

Now residual findings:

R1 (high): Kronos 卸载 carrier gap. F003 design.md:201, tasks.md:67,104,117 claim dependency on "F004 交付的服务生命周期（容器编排控制）"; F004 is status:done (F004 spec.md:5) and its delivered scope contains no external stop/lifecycle control (F004 spec.md:109-115; F004 tasks.md:70-73 only defers routing). Also architecture §7.1 (alphamill-architecture.md:577) only says "训练窗口内 Kronos 卸载" without owner. So D013's owner assignment has no upstream carrier; fcc14ad message "Kronos owner 改 F003" didn't actually modify architecture. Category correctness. Origin spec-drift. pattern_tag deferred-work-without-carrier. Severity high. Verdict D013: 部分修复.

R2 (high): universe/calendar artifact 语义三方漂移. F003 design.md:120 uses single `universe_calendar_digest` + provenance `universe_calendar_path`; F003 spec.md:112/244/328 same. ADR-0007:40-42,72-75 defines single combined artifact at reports/.../universe_calendars. But F007 DR-006 (F007 spec.md:221) and IR-002 (F007 spec.md:236), AC-006 (F007 spec.md:289) now split universe (F008, lake/_metadata/universes/<digest>.csv, not copied) and calendar (F007-owned). ADR-0007 and F003 not updated. Impact: F003 explicit-tuple binding cannot reference the F008 universe artifact by its own digest; transition tuple and ADR-0007 are now stale. Category correctness. Origin spec-drift. pattern cross-feature-contract-drift. Severity high (snapshot identity/reproducibility red line). Verdict D005: fixed as scoped, but new drift; D006: fixed.

R3 (medium): AC 语义覆盖残口. (a) No AC asserts non-completed terminal states (`rejected`/`failed`/`partial`) do NOT write `generation.run_completed` — TR-001 negative clause (spec.md:251) only has positive AC-009 (spec.md:312 "completed 运行的 run_completed 事件可查"). (b) DR-001's `universe` (pair 数) and `symbol_map_digest` persistence (spec.md:244) has no explicit AC; AC-003 (spec.md:306) only says the vague "DR-001 运行字段". Category test-coverage. Origin process-gap. pattern gate-without-teeth. Verdict D017: fixed（字面）; these are residual.

R4 (medium): D017 regression assertion gameable — `tools/check_doc_consistency.py:262` AC-011 check needle "cli_contract" is satisfied only by the `tests:` filename in the AC body, not by a behavioral clause; the check cannot distinguish a corrected test path from an incomplete AC. Category test-coverage, origin process-gap, pattern gate-without-teeth.

R5 (low/medium): 门禁作用域不含 draft. tools/check_task_dag.py:27 `ENFORCED_STATUSES` and tools/validate_spec_lifecycle.py:60-63 `TEST_GROUP_STATUSES` exclude `draft`; all three active features are draft (spec:5 each), so D011/D012 regression gates currently do not execute against F003. The gate logic is unit-tested with synthetic inputs, but the claimed "回归锁定" is not live until status advances. pattern gate-without-teeth (deferred). Severity low.

R6 (low): architecture stale example. alphamill-architecture.md:259 `factor_id: str # 如 "alphagen_gen042_f003"` contradicts the new content-addressed convention (design.md:108, spec.md:245). Category correctness, origin spec-drift, pattern spec-internal-contradiction. Severity low.

R7 (adjacent, out of F003 scope, low): F007 tasks.md:27,72 reference AC-010/AC-012 that are not defined in F007 spec (F007 spec AC list has AC-001..AC-009, AC-011 at spec.md:284-293). Also check_doc_consistency F007-D001 check requires T027/T029/T030 but doesn't validate AC refs exist. Category test-coverage, origin process-gap. Low.

Actually let me double check F007 AC-010/AC-012 truly absent. grep "AC-0" returned lines 284-293, including AC-011. No AC-010/012. But maybe AC-010 is later in the file? The grep should have caught any line containing "AC-0". It returned all such lines. So absent. But wait — maybe the F007 spec uses AC-010 but grep output was truncated at head? No head not used for that grep. It returned 6 lines. So indeed absent. Adjacent finding valid.

Also check F007 AC-011 exists but was probably added by another commit. Fine.

Now let me also double-check D004's tasks references: tasks.md:52 (T016) includes M2 obligations, tasks.md:112 (§5) includes not_yet_available placeholder. Good.

D011 [TEST] group at tasks.md:82-86. The template at a333394 added [TEST] requirement. Good.

One more: D002 AC-011 says "缺绑定的 mine 请求非零退出并留 rejected 终态 run.json". fine.

I think we're ready. Also should I run the actual mutation/unit tests? Not necessary; gates ran green.

Let me produce the final answer in Chinese, with the required <results> block. The user wants "Return only evidence-backed findings with exact file:line, severity, category, origin, pattern_tag, and a fixed/not-fixed verdict for each D001..D022."

I'll produce:
1. 结论
2. D001..D022 判定表 (ID | 判定 | 证据 file:line | severity | category | origin | pattern_tag)
3. 残余/新增 findings (with file:line, severity, category, origin, pattern_tag)
4. verification commands / gates status
5. next steps

Given output style, lead with answer. Keep punctuation. Chinese.

Let me be careful: severity/category/origin/pattern_tag for each D per the original issue table, plus my verdict. The user asked for these fields per finding. I'll reuse the original values (since they're the D definitions) and annotate verdict.

For residual findings I give new severity etc.

Let me write the table compactly. 22 rows.

Verdicts:
D001 fixed
D002 fixed
D003 fixed
D004 fixed
D005 fixed（但见 R2）
D006 fixed
D007 fixed
D008 fixed
D009 fixed
D010 fixed
D011 fixed（门禁 draft 期不生效）
D012 fixed（门禁 draft 期不生效）
D013 partial
D014 fixed
D015 fixed
D016 fixed
D017 fixed（语义残口见 R3/R4）
D018 fixed
D019 fixed
D020 fixed
D021 fixed
D022 fixed

Count: fixed 21 (D005/D011/D012/D017 with caveats), partial 1 (D013). No not-fixed.

Hmm, is it fair to call all others fixed? Let me sanity-check D002 one more time: the finding demanded REJECTED/FAILED terminal facts persisted. Current design:96 "四态都写"; 103 terminal semantics; 200 failed terminal. Yes.

D008: design:200 partial. Yes.

D009: yes.

D018: yes.

OK.

Also mention that the unified gate ran green: validate_spec_lifecycle 通过, check_task_dag 通过, check_doc_consistency 通过 (I ran them; exit 0).

Let me include evidence for the gate run.

Now write final. Need <results> block at end with <files> and <answer> and <next_steps>. The instructions say always end with that exact format. Paths absolute.

I'll keep the report then the results block.

For file paths in the results block use absolute.

Let me compose. Also mention HEAD=26c7b6d, 37 commits, baseline a333394.

Careful about line numbers for ADR-0007: fields at lines 31-43, artifact path lines 72-75. F007 spec DR-006 line 221, IR-002 line 236, AC-006 line 289. F004 spec status line 5, lifecycle 109-115. F004 tasks line 70-73. architecture:259 example, architecture:577 unload. F003 design:201, tasks:67,104,117. F007 tasks:27,72. F007 spec AC list 284-293.

Let me write.
# F003 文档审计（a333394..HEAD，HEAD=26c7b6d）

**结论**：D001–D022 中 **21 条已修复**、**1 条部分修复（D013）**；无「未修复」。但修复引入/遗留 **3 条高价值语义缺口**（R1 Kronos 卸载载体、R2 universe/calendar 契约漂移、R3 AC 语义残口），其中 R1/R2 会阻塞后续实现。

实跑门禁（当前工作树，只读）：
- `.venv/bin/python tools/validate_spec_lifecycle.py` → 全部通过（exit 0）
- `.venv/bin/python tools/check_task_dag.py` → 全部通过（exit 0）
- `.venv/bin/python tools/check_doc_consistency.py` → 全部通过（exit 0）

---

## 一、D001..D022 逐条判定

| ID | 判定 | 证据（file:line） | severity | category | origin | pattern_tag |
|---|---|---|---|---|---|---|
| D001 | **fixed** | design.md:108；spec.md:245,312 | high | correctness | original-coding | spec-internal-contradiction |
| D002 | **fixed** | design.md:96,103,104,200,216；spec.md:251,271,287,306,314 | high | correctness | original-coding | spec-internal-contradiction |
| D003 | **fixed** | spec.md:43,213,280,310；design.md:255 | high | correctness | spec-drift | spec-internal-contradiction |
| D004 | **fixed** | spec.md:74,215-218,310；design.md:116,211；tasks.md:52,112 | high | correctness | spec-drift | gate-without-teeth |
| D005 | **fixed**（字面）/ 见 R2 | design.md:120,121；spec.md:112,244,328,337；ADR-0007:31-43 | high | correctness | spec-drift | cross-feature-contract-drift |
| D006 | **fixed** | design.md:55,82；spec.md:102,328；tasks.md:59,97；F008 spec.md:243-244 | high | correctness | spec-drift | cross-feature-contract-drift |
| D007 | **fixed** | spec.md:122,265,314；design.md:218,251 | high | correctness | original-coding | gate-without-teeth |
| D008 | **fixed** | design.md:200；spec.md:251,276,287,312 | high | correctness | original-coding | spec-internal-contradiction |
| D009 | **fixed** | design.md:58,114；spec.md:197,309；PRD:157 | high | correctness | spec-drift | spec-internal-contradiction |
| D010 | **fixed** | design.md:67,124；spec.md:234,247,311；architecture.md:269-274 | high | correctness | original-coding | spec-internal-contradiction |
| D011 | **fixed**（门禁 draft 期不生效，见 R5） | tasks.md:82-86；validate_spec_lifecycle.py:60-63,210-211 | high | test-coverage | process-gap | spec-tasks-traceability-gap |
| D012 | **fixed**（门禁 draft 期不生效，见 R5） | tasks.md:88,90-106；check_task_dag.py:27,150 | high | correctness | process-gap | task-graph-order-contradiction |
| D013 | **部分修复**（见 R1） | design.md:196-201；spec.md:263,313；tasks.md:67,104 | high | correctness | spec-drift | deferred-work-without-carrier |
| D014 | **fixed** | F007 spec.md:7,22-23；F007 design.md:5,25-26,175-181 | high | correctness | spec-drift | cross-feature-contract-drift |
| D015 | **fixed** | design.md:110；spec.md:304,307；tasks.md:40 | medium | correctness | spec-drift | spec-internal-contradiction |
| D016 | **fixed** | design.md:105,114；spec.md:258,315；tasks.md:41,45 | medium | test-coverage | process-gap | spec-tasks-traceability-gap |
| D017 | **fixed**（字面）/ 见 R3/R4 | spec.md:306,308,309,312,313,314；design.md:236；check_doc_consistency.py:257-263 | medium | test-coverage | process-gap | spec-tasks-traceability-gap |
| D018 | **fixed** | design.md:122,199；spec.md:264,312 | medium | correctness | original-coding | gate-without-teeth |
| D019 | **fixed** | design.md:156-166；tasks.md:52,69；spec.md:256 | medium | correctness | original-coding | spec-tasks-traceability-gap |
| D020 | **fixed** | design.md:112；spec.md:246,312；PRD:153；tasks.md:39 | medium | correctness | spec-drift | spec-internal-contradiction |
| D021 | **fixed** | design.md:84；spec.md:149,305；tasks.md:31,49 | medium | test-coverage | process-gap | gate-without-teeth |
| D022 | **fixed** | CLAUDE.md:51-53；docs/README.md:36；BACKLOG.md:8-10 | low | quality | spec-drift | — |

---

## 二、残余 / 新增发现（证据驱动）

### R1（high）Kronos 卸载 live owner 已钉 F003，但 F004 载体不存在且 F004 已 done
- F003 design.md:201 声明「经 **F004 交付的服务生命周期（容器编排控制）**优雅停止 `kronos-signal`」；tasks.md:67,104,117 同。
- F004 spec.md:5 `status: done`；F004 交付面只有 compose profile + 容器集成（F004 spec.md:109-115），tasks.md:70-73 后移项只有「消费者路由切换」，**无任何供外部停止/生命周期控制的接口或契约**。
- architecture.md:577 只写「训练窗口内 Kronos 卸载」，未声明 owner；`fcc14ad` commit message 声称「Kronos owner 改 F003」，但该 commit 对 architecture 的实际 diff 只改了 `generator` 注释与协同池段（architecture.md:262,269-274），**未改 Kronos owner**。
- 影响：F003 T025 的依赖 `F004 交付（kronos-signal 服务编排）-> T025`（tasks.md:104）无上游载体；F004 已 done，补交付需重开 done Feature。
- verdict：**D013 部分修复**（owner 声明成立，carrier 缺失）。

### R2（high）universe/calendar 快照绑定三方漂移
- F003 仍用单一 `universe_calendar_digest` + provenance 单一 `universe_calendar_path`（design.md:120,121；spec.md:112,244,328）。
- ADR-0007 定义单文件 artifact：`universe_calendar_digest` + `universe_calendar_path`，调用方提供的 universe/calendar JSON 由 `experiment_store` 存到 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`（ADR-0007:40-42,72-75）。
- F007 已改为**两个独立 artifact**：universe 按 F008 从 `lake/_metadata/universes/<digest>.csv` 加载、不复制进 reports；calendar 由 F007 拥有；`universe_calendar_digest` = 两 digest 组合（F007 spec.md:221 DR-006、236 IR-002、289 AC-006）。
- 影响：ADR-0007 与 F003 显式元组未同步 F007 D004 的拆分；F003 过渡绑定无独立 universe digest/引用字段，无法显式锚定 F008 台账 digest（研究可复现红线）。
- 影响面：D005 字面修复通过，但新漂移由 F007 修复引入、未回灌 ADR-0007/F003。

### R3（medium）AC 对终态与 DR-001 的语义断言仍缺
- TR-001 负向条款「`rejected`/`failed`/`partial` 不得写 `run_completed`」（spec.md:251）**无 AC 断言**；AC-009 只断言正向「completed 运行的 run_completed 事件可查」（spec.md:312）。
- DR-001 要求 `universe`（pair 数）与 `symbol_map_digest` 随运行留痕（spec.md:244），AC-003 仅以泛化短语「DR-001 运行字段」承载（spec.md:306），无显式字段断言。

### R4（medium）D017 回归断言可被文件名满足
- `tools/check_doc_consistency.py:262` 对 AC-011 的检查 needle 为 `"cli_contract"`；该串仅由 AC 体内 `tests: .../test_f003_cli_contract.py` 命中（spec.md:314），并非行为子句。检查无法区分「测试路径已改正」与「AC 行为断言未补全」。

### R5（low）D011/D012 门禁对 draft 不生效
- `tools/check_task_dag.py:27` `ENFORCED_STATUSES` 与 `tools/validate_spec_lifecycle.py:60-63` `TEST_GROUP_STATUSES` 均排除 `draft`；F003/F007/F008 spec.md:5 全为 `draft`，故 D011/D012 的「回归锁定」在状态推进前对 F003 不实际执行（门禁逻辑本身由合成用例覆盖）。

### R6（low）架构 Phase 0 示例 factor_id 与新约定冲突
- `alphamill-architecture.md:259` `# 如 "alphagen_gen042_f003"` 与内容寻址 `factor_id = <generator>_<definition_digest[:12]>`（F003 design.md:108、spec.md:245）不一致，属陈旧示例。

### R7（low，相邻，非 F003 范围）F007 tasks 引用未定义 AC
- `F007 tasks.md:27` 引用 `AC-010`、`tasks.md:72` 引用 `AC-010`/`AC-012`；F007 spec.md:284-293 的 AC 列表为 AC-001..AC-009 与 AC-011，**无 AC-010/AC-012**。D017 类同问题的 F007 镜像。

---

<results>
<files>
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md - F003 行为契约；D001/D003/D004/D005/D006/D007/D008/D009/D010/D014/D016/D017/D020 证据
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md - F003 设计；D001/D002/D005/D006/D008/D010/D013/D015/D016/D018/D019 证据，R1/R6 证据
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md - D011/D012/D013/D017/D019/D021 证据，R1 依赖边
- /home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md - D005 上游契约；R2 漂移的锚点（:31-43,:72-75）
- /home/georg/projects/alphamill/docs/decisions/0001-factor-mining-engine.md - D003/D004 判据与 M2 义务（:40-50,:52-62）
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md - D014 收口；R2 新拆分（:221,:236,:289）；R7 无 AC-010/012
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md - R2/R7 证据
- /home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/spec.md - R1 证据（:5 done，:109-115 无生命周期控制）
- /home/georg/projects/alphamill/docs/features/0.2/F004-kronos-inference-runtime/tasks.md - R1 证据（:70-73 仅后移路由）
- /home/georg/projects/alphamill/docs/alphamill-architecture.md - D010 收口（:269-274）；R1（:577 无 owner）；R6（:259 陈旧示例）
- /home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md - D006 上游 IR-002/IR-003（:243-244）
- /home/georg/projects/alphamill/tools/check_doc_consistency.py - D014/D017/D022 门禁；R4 弱点（:262）
- /home/georg/projects/alphamill/tools/check_task_dag.py - D012 门禁；R5 作用域（:27）
- /home/georg/projects/alphamill/tools/validate_spec_lifecycle.py - D011 门禁；R5 作用域（:60-63）
- /home/georg/projects/alphamill/CLAUDE.md - D022（:51-53）
- /home/georg/projects/alphamill/docs/README.md - D022（:36）
- /home/georg/projects/alphamill/BACKLOG.md - D022（:8-10）
</files>

<answer>
对照 a333394..HEAD 独立核对（不采信 FIX-log 文字），D001–D022 的文档修复基本落实：21 条 fixed，D013 partial。

相对原始 finding 表的字段（severity/category/origin/pattern_tag）见上表，逐条附了当前 file:line。

关键剩余问题（会导致实现期返工）：
1. R1：D013 的 Kronos 卸载 owner 已钉 F003，但依赖的「F004 交付的容器编排/服务生命周期」不存在，且 F004 已 done；architecture §7.1 也未声明 owner。
2. R2：F007 D004 把 universe/calendar 拆成两个 artifact，但 ADR-0007 与 F003 显式元组仍是单一 universe_calendar_digest/path，快照身份契约三方不一致。
3. R3/R4：AC 仍缺「非 completed 终态不发 run_completed」与 DR-001 universe 字段的显式断言；D017 的门禁断言仅靠 test 文件名命中，可被绕过。

门禁实跑：validate_spec_lifecycle / check_task_dag / check_doc_consistency 均通过（exit 0）。
</answer>

<next_steps>
1. 先裁决 R1：在 architecture §7.1 补 Kronos 卸载 owner=F003（一行），并确认「容器编排控制」是 docker compose stop 还是需 F004 补交付；若需补，重开 F004 或把 T025 改为直连 compose。
2. 再裁决 R2：决定 universe_calendar_digest 是「组合摘要」还是「单 artifact 摘要」，同步修改 ADR-0007:31-43,72-75 与 F003 design.md:120/spec.md:244；F003 元组需增独立 universe artifact digest 字段。
3. 补 R3/R4：给 TR-001 负向条款与 DR-001 universe 字段各加一条 AC 断言；把 check_doc_consistency.py:262 的 needle 从 `cli_contract` 改成行为短语。
4. （低优先）修 architecture.md:259 示例、F007 tasks.md:27,72 的 AC-010/AC-012 悬空引用。
</next_steps>
</results>
