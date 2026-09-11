---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f8864154effee43BxsyghmKN0c"
title: "Fix integration+F001 D013/D014/D017/D011/D010 (@general subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T16:45:02Z"
updated_at: "2026-09-06T16:53:30Z"
tokens_input: 54481
tokens_output: 7039
cost: 0.0
parent_id: "ses_f886c33ddffed2Ehk0OBMbTqR2"
---

# Fix integration+F001 D013/D014/D017/D011/D010 (@general subagent)

## user · 2026-09-06T16:45:02Z

You are the FIXER in a review-convergence loop for AlphaMill (D:\Projects\alphamill), a crypto quant research system at design stage. Baseline: main @ 1bd8c4d. Language: Chinese, match existing doc style.

YOUR FILE OWNERSHIP (do NOT touch any other file):
- docs/alphamill-integration.md
- docs/features/0.1/F001-quant-crypto-migration/spec.md
- docs/features/0.1/F001-quant-crypto-migration/design.md
- docs/features/0.1/F001-quant-crypto-migration/tasks.md
- docs/features/0.1/F001-quant-crypto-migration/migration-plan.md

First READ all five files + round-1 review report docs/reviews/CURRENT-doc.md (issues D013, D014, D017, D011, D010) + docs/SOP.md §2 (feature state machine rules).

CRITICAL CONSTRAINT: F001 files are machine-validated by tools/validate_spec_lifecycle.py (frontmatter status only in spec.md, Q-xxx/DQ-xxx must be closed, AC must reference existing test paths, tasks structure, BACKLOG bidirectional consistency). spec.md is `draft` — do NOT change its status. Any edit must keep the validator green. Prefer minimal, surgical insertions.

DIRECTORY DECISION ALREADY MADE (D010): single Python layout = src/alphamill/<module>/ (subpackages: alphamill/data_bridge, alphamill/factor_factory, alphamill/validation, alphamill/kronos_service...); non-Python assets (docker-compose, deployment/, docs/) stay at repo root. Wherever F001 tasks/design/migration-plan write flat target paths (data_bridge/..., factor_factory/...), change to src/alphamill/<module>/... accordingly (tasks T005-T009 per the review report — verify actual task ids yourself).

TASKS:

1. D010 (High): propagate the layout decision through F001 tasks.md target paths, design.md module layout references, migration-plan.md target paths, and integration.md directory mentions. Keep concept names identical; only paths change.
2. D014 (Medium, data revision/point-in-time policy): integration.md §1.2 (data bridge / export area) — add revision policy: when TimescaleDB revision detected by the weekly full-validation, data_version MUST bump (new snapshot, old snapshot immutable and retained); in-flight experiments pinning the old data_version are NOT auto-invalidated but flagged (manifest comparison shows data_version drift → rerun recommended before any gate decision); document the rule as 3-4 bullet lines.
3. D013 (Medium, Vibe-Trading contract front-loading): integration.md Vibe-Trading section + note in F001 design.md if it touches naming — M1 decides Parquet partitioning & pair naming; symbol mapping to Vibe-Trading must be pre-agreed: add "M1 出口标准" item — vibe_bridge symbol-mapping initial table (pair naming ↔ Vibe-Trading symbol ↔ Freqtrade pair), UTC alignment convention. One table skeleton + 3 lines of contract, no more.
4. D017 (Medium, backup/DR): migration-plan.md scope (or integration.md deployment section — pick the more natural home, likely migration-plan since NAS sync rides the migration) — add: daily sync of Parquet lake + manifests + TimescaleDB dumps to the user's NAS (UGREEN NAS exists on LAN); single-disk failure must not equal project loss. 3-5 lines with concrete paths/ cadence; if placed in F001 scope, add one task line in tasks.md consistent with its task format.
5. D011 (Medium): fix stale refs (docs/02-系统架构, docs/05-*, "doc 03") in integration.md + all four F001 files → current names (docs/alphamill-architecture.md etc.). Grep for `docs/0` and `doc 0`.

Update frontmatter `updated:` to 2026-09-07 where frontmatter exists.

VALIDATION: run `python tools/validate_spec_lifecycle.py` (cwd D:\Projects\alphamill) after edits — MUST stay green for F001-related checks; ignore unrelated concurrent-edit failures from other agents' files but fix any failure caused by your own edits. Also run `python ../alphamill/BACKLOG` consistency implicitly via the validator (it checks BACKLOG bidirectional consistency — if you edit F001 status-linked fields, keep BACKLOG.md in sync ONLY if the validator forces it; you do NOT own BACKLOG.md, so prefer edits that don't touch status/links).

MUST NOT: touch docs/prd / architecture / SOP / READMEs / decisions/ / code files; change F001 status; loosen gates; commit.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T16:45:02Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\reviews\\CURRENT-doc.md"})`


> [reasoning] Let me start by reading all the required files. I need to read:
1. docs/alphamill-integration.md
2. docs/features/0.1/F001-quant-crypto-migration/spec.md
3. docs/features/0.1/F001-quant-crypto-migration/design.md
4. docs/features/0.1/F001-quant-crypto-migration/tasks.md
5. docs/features/0.1/F001-quant-crypto-migration/migration-plan.md
6. docs/reviews/CURRENT-doc.md (round-1 review report)
7. docs/SOP.md §2

Let me read these in parallel.

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\alphamill-integration.md</path>
<type>file</type>
<content>
1: # AlphaMill — 集成设计
2: 
3: > 版本：v0.1 | 日期：2026-09-06 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)
4: > ⚠️ 本文档为集成操作细节；外部依赖管理策略已提炼至 [ADR-0002](decisions/0002-external-dependency-policy.md)。
5: > 本文回答：AlphaMill 的三个外部系统（数据湖 / Vibe-Trading / Freqtrade）各自怎么接、接口长什么样、出问题怎么隔离。
6: 
7: ---
8: 
9: ## 一、数据桥：TimescaleDB → Parquet 湖
10: 
11: ### 1.1 为什么需要这一层
12: 
13: - Vibe-Trading 的 `local` loader 支持 CSV / Parquet / DuckDB，**不直连 Postgres**；
14: - 研究需要不可变快照：TimescaleDB 数据会被回补/修订，Parquet 快照 + 版本号保证"同一版数据永远算出同一版结果"；
15: - 双口径落盘（adjusted/raw）在导出时点固定，避免消费端各自解释。
16: 
17: ### 1.2 导出设计
18: 
19: | 项 | 设计 |
20: |---|---|
21: | 调度 | 每日 03:00 增量导出（昨日分区），每周日全量校验 |
22: | 分区 | `lake/ohlcv_1m/exchange=<ex>/pa
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F001
4: version: "0.1"
5: status: draft
6: gate_version: 1
7: related_features: []
8: topics: [migration, infra]
9: doc_kind: spec
10: created: 2026-09-06
11: updated: 2026-09-06
12: ---
13: 
14: # F001：quant-crypto 资产清算迁移
15: 
16: > Owner: Georg | Target: v0.1.0
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` §1.3 决策 2（清算迁移）与里程碑 M0
21: - **架构来源**：`docs/alphamill-architecture.md` §五（资产清算迁移表）、§七（部署拓扑）
22: - **系统设计 / Research / Contract 来源**：`docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`（迁移清单与验收）
23: - **上游决策**：`docs/decisions/`（暂无；仓库归档决策记录于 docs/05）
24: - **功能类型**：backend / workflow
25: - **规格模式**：full
26: -
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F001
4: version: "0.1"
5: related_features: []
6: topics: [migration, infra]
7: doc_kind: design
8: created: 2026-09-06
9: updated: 2026-09-06
10: ---
11: 
12: # F001：quant-crypto 资产清算迁移 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: ## 0. 输入与约束
17: 
18: - **行为契约**：`spec.md`（FR-001..006 / NFR-001..002）
19: - **PRD / Architecture / System Design**：`docs/alphamill-prd.md` M0；`docs/alphamill-architecture.md` §五、§七；`migration-plan.md` 全文（本目录）
20: - **ADR / 上游 Contract**：Kronos HTTP API 契约以旧仓 `kronos-signal/server.py` 现行为准（不新增不修改）
21: - **实现约束**：Windows 11 + PowerShell 7；旧仓只读（NFR-001）；迁移期间不得中断旧仓服务直至对账通过
22: 
23: ## 1. 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F001
4: version: "0.1"
5: related_features: []
6: topics: [migration, infra]
7: doc_kind: tasks
8: created: 2026-09-06
9: updated: 2026-09-06
10: ---
11: 
12: # F001：quant-crypto 资产清算迁移 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`。
19: - 技术方案与边界：`design.md`。
20: - 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
21: - 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
22: - `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
23: - 实现中若任务顺序或契约失效，先修订三件套，再继续编码。
24: 
25: ## 1. 前置条件
26: 
27: - [ ] T001 (`NFR-001`): 旧仓建立只读基线（本地全量备份 + 记录当前 commit） — verify: 备份文件存在 + 旧仓 `git rev-parse HEAD` 记录
28: - [ ] T002 (`FR-001`)
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\migration-plan.md</path>
<type>file</type>
<content>
1: # AlphaMill — quant-crypto 清算迁移方案
2: 
3: > 版本：v0.1 | 日期：2026-09-06 | 决策：quant-crypto 仓库**归档废弃**，资产一次性清算迁入本仓
4: > 红线：代码可以弃，**数据必须迁**（631 万行 OHLCV + 衍生品特征 + 质量标记 = 数周采集成本，不可重购）
5: 
6: ---
7: 
8: ## 一、迁移总览
9: 
10: | # | 资产 | 来源（quant-crypto） | 去处（AlphaMill） | 改造点 |
11: |---|---|---|---|---|
12: | 1 | **TimescaleDB 数据卷** | docker volume（6.3M 行 1m OHLCV、衍生品表、质量标记、连续聚合） | 随 docker-compose 迁入，数据不重建 | pg_dump/restore 或 volume 直迁，行数对账 |
13: | 2 | 数据采集器 | `data-collector/`（ccxt_ingestor、db_writer、historical_backfill、symbol_manager、derivatives_market_backfill） | `data_bridge/collector/` | 并入主仓依赖管理；保留 REST 轮询模式 |
14: | 3 | Kronos 服务薄壳 | `kronos-signal/`（server/generator/db_
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

## assistant · 2026-09-06T16:45:21Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md"})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs", "pattern": "docs/0|doc 0"})`


> [reasoning] Now let me read SOP.md §2 and check the validator to understand constraints. Also grep for stale refs.

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\SOP.md</path>
<type>file</type>
<content>
1: ---
2: topics: [sop, workflow]
3: doc_kind: note
4: created: 2026-09-06
5: updated: 2026-09-06
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
22: | 2 | <按项目定义> | <短摘要> | `docs/alphamill-prd.md` / `-architecture.md` |
23: | 3 | <按项目定义> | <短摘要> | `docs/decisions/` |
24: 
25: > 新建项目时：从 PRD/架构中提炼 3-7 条真正不可违反的
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 14 match(es) in 6 file(s)

D:\Projects\alphamill\docs\alphamill-integration.md
  168: | Kronos | 独立服务（上游 clone + pin commit，权重 HuggingFace 下载） | 模型代码上游化；服务薄壳为本仓 `kronos_service/` | pin 上游 commit；见 docs/05 |

D:\Projects\alphamill\docs\alphamill-prd.md
  61: - ❌ 不重建数据管道/数据湖（quant-crypto 数据资产整体迁入，见 docs/05）
  95: - FR2.1 **生成器**：至少两种可插拔后端——程序化（**AlphaGen RL 挖掘为主**，vendor 策略见 doc 03；GP/表达式枚举对照）与人工/LLM 辅助（论文因子、假设清单）。生成器只负责产出**因子定义**，不做评测。
  145: | **M0 资产清算迁移** | docs/05 迁移清单：数据卷 + 采集器 + Kronos 上游化 + 风控/监控搬迁 | verify 全绿：行数对账 / Kronos /health / Freqtrade dry-run / 监控有数据 | 2-3 天 |

D:\Projects\alphamill\docs\reviews\CURRENT-doc.md
  25: - {id: D011, severity: medium, title: 13 处死链（docs/05、docs/02、doc 03 旧编号残留）}
  121: | D011 | 13 处死链：docs/05、docs/02、"doc 03" 旧编号残留于 6 文件（README/PRD/integrat
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:45:34Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\tools\\validate_spec_lifecycle.py"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\BACKLOG.md"})`


> [reasoning] Now I have a full picture. Let me note what needs to change:

**D011 stale refs** in my owned files:
- integration.md line 168: `见 docs/05` → the referenced content is about Kronos deployment/upstream. What is docs/05? Old docs numbering: docs/05 = deployment/部署? Let me think. The migration plan references `docs/05 §一 迁移清单` — the migration checklist. In the new doc naming, the asset migration table lives in `docs/alphamill-architecture.md` §五 (资产清算迁移表) per F001 spec line 21. And F001 spec line 77: "docs/05 §一 迁移清单 1-9 项" — this migration checklist is now in migration-plan.md §一 (迁移总览 table with 9 items). Also "docs/05 §四" (Q-001: 阶段 A 保留) — the TimescaleDB 阶段A/B decision now lives in migration-plan.md §四.

So mapping:
- `docs/05 §一 迁移清单` → `migration-plan.md §一 迁移总览`（同目录）
- `docs/05 §四` (TimescaleDB 去留) → `migration-plan.md §四`
- `docs/05` (generic, deployment related) → `docs/alphamill-architecture.md` §七（部署拓扑）? For integration.md line 168: "pin 上游 commit；见 docs/05" — context is Kronos 独立服务 deployment. The architecture doc §七 is 部署拓扑. So `见 docs/alphamill-architecture.md §七`.
- integration.md line 24: `schema 见架构文档 4.4` — that's fine already ("架构文档 4.4"), not a stale ref. Actually check: "manifest | 每次导出写 `lake/_manifests/<dataset>/<data_version>.json`（schema 见架构文档 4.4）" — fine.
- design.md line 25: `docs/05 清单` → `migration-plan.md §一 迁移总览清单`
- design.md line 32: `docs/05 清单项勾选` → `migration-plan.md 清单勾选`
- design.md line 36: `docs/02 §三目录设计` → `docs/alphamill-architecture.md` 目录设计 section. Architecture has "目录设计" per README index ("三层模块级架构图（ASCII+Mermaid）、因子生命周期数据流、目录设计、4 个接口契约"). But D010 decision changes the directory design! The architecture doc §三 currently shows flat layout (data_bridge/...), which is the contradiction. The review says "同步改架构 §三/SOP" but I don't own architecture/SOP. I only own F001 files + integration.md. So in design.md, I should reference the architecture doc but state the layout decision. Actually D010 decision already made: src/alphamill/<module>/. So design.md §2 should say: 迁移后模块边界与 `docs/alphamill-architecture.md` 目录设计一致（目录约定已拍板：Python 包统一 `src/alphamill/<module>/`）...

Hmm, but I must be careful: the architecture doc still says flat. The review D010 says fix F001 tasks T005-T009 paths etc. The decision was already made by orchestrator: "single Python layout = src/alphamill/<module>/". I propagate through my files. I can note "（目录约定以 D010 拍板为准：src/alphamill/<module>/）" — but referencing the review report in design docs is odd. Better: just write the canonical form "src/alphamill/..." and reference architecture doc for module boundaries generally. Let me keep it simple: change `docs/02 §三目录设计` → `docs/alphamill-architecture.md` 目录设计（Python 模块统一 `src/alphamill/<module>/`）.

- tasks.md line 57: `docs/05 清单勾选` → `migration-plan.md 清单勾选`
- spec.md lines 23, 77, 172, 206: `docs/05` refs:
  - line 23: `- **上游决策**：docs/decisions/（暂无；仓库归档决策记录于 docs/05）` → migration-plan.md has 旧仓处置 (打 tag 归档) in §二. So → `（暂无；仓库归档处置记录于 migration-plan.md §二）`
  - line 77: `- docs/05 §一 迁移清单 1-9 项：...` → `- migration-plan.md §一 迁移总览 1-9 项：...`
  - line 172: `- **SC-003**：docs/05 迁移清单 9 项全部标记完成。` → `- **SC-003**：migration-plan.md §一 迁移总览 9 项全部标记完成。`
  - line 206: `— 决策：阶段 A 保留（docs/05 §四），阶段 B 另立 feature 评估` → `— 决策：阶段 A 保留（migration-plan.md §四），阶段 B 另立 feature 评估`

Wait — the review report says stale refs exist in "README/PRD/integration/F001 三件套" — 13 occurrences in 6 files. PRD and README I don't own. My scope: integration.md (1: line 168), F001 spec (4), tasks (1), design (3: lines 25, 32, 36). Let me check migration-plan.md — grep found no docs/0 matches in migration-plan.md. OK.

Also integration.md line 4 mentions `[alphamill-architecture.md](./alphamill-architecture.md)` — fine. decisions/0002 relative link `decisions/0002-external-dependency-policy.md` — from docs/alphamill-integration.md, relative would be docs/decisions/... — it says `(decisions/0002-external-dependency-policy.md)` — relative to docs/ that works. Fine.

**D010 path propagation**: Where do F001 tasks/design/migration-plan/integration write flat target paths?

tasks.md:
- T005: `data_bridge/collector/` → `src/alphamill/data_bridge/collector/`
- T007: `kronos_service/` → `src/alphamill/kronos_service/`
- T008: `freqtrade_bridge/risk/` → `src/alphamill/freqtrade_bridge/risk/`
- T009: `monitoring/` → monitoring is not Python. Per decision: "non-Python assets (docker-compose, deployment/, docs/) stay at repo root". What about monitoring/ (Grafana/Prometheus config)? Not Python → stays at root `monitoring/`. The decision lists docker-compose, deployment/, docs/ as non-Python staying at root; "..." implies other non-Python too. monitoring/ is non-Python → root. Keep `monitoring/`.
- T010: `deployment/` → stays root (explicitly stated).

Hmm wait, but the D010 fix suggestion says "F001 tasks T005-T009 路径". T009 monitoring — the decision says non-Python assets stay at root. monitoring/ is YAML/JSON configs → root. So T005/T007/T008 get src/alphamill/ prefix; T009/T010 unchanged. Also T016/T017 fine.

Wait, what about `scripts/` (宇宙发现) — migration-plan item 8 target `scripts/` — non-Python? They're Python scripts but repo-root scripts/? Hmm. The decision: "single Python layout = src/alphamill/<module>/ (subpackages: alphamill/data_bridge, alphamill/factor_factory, alphamill/validation, alphamill/kronos_service...)". Discover scripts are Python. But they're listed in migration-plan as `scripts/`. Hmm — "..." in the subpackage list. The safest interpretation: Python code goes under src/alphamill/. But one-off utility scripts at root scripts/ is common. The decision text says "non-Python assets (docker-compose, deployment/, docs/) stay at repo root" — it explicitly enumerates docker-compose, deployment/, docs/. scripts/ are Python...

Let me re-read the task instruction: "Wherever F001 tasks/design/migration-plan write flat target paths (data_bridge/..., factor_factory/...), change to src/alphamill/<module>/... accordingly (tasks T005-T009 per the review report — verify actual task ids yourself)."

The examples given: data_bridge/..., factor_factory/... — i.e., the module packages. migration-plan targets: data_bridge/collector/, kronos_service/, freqtrade_bridge/risk/, factor_factory/bench/ + validation/, monitoring/, deployment/, scripts/, freqtrade/user_data/.

- data_bridge/collector/ → src/alphamill/data_bridge/collector/
- kronos_service/ → src/alphamill/kronos_service/
- freqtrade_bridge/risk/ → src/alphamill/freqtrade_bridge/risk/
- factor_factory/bench/ + validation/ → src/alphamill/factor_factory/bench/ + src/alphamill/validation/
- monitoring/ → root (non-Python config)
- deployment/ → root (explicit)
- scripts/ → hmm. The universe discovery scripts are Python. But they're utility scripts. The decision says "single Python layout = src/alphamill/<module>/". Scripts could go to src/alphamill/scripts/ or stay scripts/. The review D010 fix suggestion only mentions "F001 tasks T005-T009 路径/pyproject packages". To be conservative and minimal, I'll leave `scripts/` and `freqtrade/user_data/` as-is (freqtrade user_data is Freqtrade's own plugin layout, must stay root freqtrade/user_data/ since Freqtrade docker mounts it; scripts/ is a utility dir). Actually, wait — minimal & surgical. The review's concrete fix: "同步改架构 §三/SOP Code Quality/F001 tasks T005-T009 路径/pyproject packages". So tasks T005-T009. I'll change module-package paths only: data_bridge, kronos_service, freqtrade_bridge, factor_factory, validation. Leave monitoring/, deployment/, scripts/, freqtrade/user_data/ untouched (non-Python / external tool layouts).

Hmm, but actually scripts/ contains Python (discover_okx_swap_universe.py). The decision statement in my prompt lists subpackages "alphamill/data_bridge, alphamill/factor_factory, alphamill/validation, alphamill/kronos_service..." — these are the four migrated module families. I'll apply src/alphamill/ prefix to those module families and leave scripts/ alone (it's a repo-root utility convention, and the review didn't flag it). Actually to be safe, should I? The instruction: "Wherever F001 tasks/design/migration-plan write flat target paths (data_bridge/..., factor_factory/...)". The parenthetical gives module-package examples. I'll stick to module packages.

design.md:
- line 28: "kronos_service/ 迁入" → "src/alphamill/kronos_service/ 迁入"
- line 32: "deployment/verify.ps1 扩展" fine.
- line 36 (§2): rewrite with src/alphamill/ paths: `src/alphamill/data_bridge/collector/`（采集）与 `src/alphamill/data_bridge/`（导出，F002 实现）分离... `src/alphamill/kronos_service/` ... `src/alphamill/freqtrade_bridge/risk/` ... `deployment/` 是唯一编排入口. Also fix docs/02 → alphamill-architecture.md. Note dependency direction "deployment → services → data" — keep.

integration.md flat path mentions:
- §四: `quant-crypto 的门禁脚本参数化迁移到 validation/` → `src/alphamill/validation/`
- §五 table: AlphaGen vendor 进 `factor_factory/generators/alphagen_vendor/` → `src/alphamill/factor_factory/generators/alphagen_vendor/`
- §2.2: `vibe_bridge/local_loader_config/` → `src/alphamill/vibe_bridge/local_loader_config/`
- §2.4: `vibe_bridge/postmortem/` → `src/alphamill/vibe_bridge/postmortem/`
- §1.2 table: `lake/ohlcv_1m/...`, `lake/_manifests/...` — data lake paths, not Python packages → keep.
- README quick start mentions `python data_bridge/export_ohlcv.py` — README not mine.
- integration.md §3.1: `freqtrade_bridge/strategy_template.py.j2` → `src/alphamill/freqtrade_bridge/strategy_template.py.j2`
- integration.md §六 table: no paths.
- kronos_service/ in §五 table line 168: `服务薄壳为本仓 kronos_service/` → `src/alphamill/kronos_service/`.

Also integration.md line 3: "版本：v0.1 | 日期：2026-09-06" — no frontmatter in integration.md (it's a plain doc, no frontmatter — starts with `# AlphaMill — 集成设计`). "Update frontmatter `updated:` to 2026-09-07 where frontmatter exists." integration.md has no frontmatter → skip. F001 spec/design/tasks have frontmatter → update to 2026-09-07. migration-plan.md no frontmatter → skip.

**D014**: integration.md §1.2 — add revision policy as 3-4 bullet lines. Where? After the §1.2 table, add a short block:

```
**数据修订政策（point-in-time）**：

- 周日全量校验发现 TimescaleDB 历史数据被修订（回补/更正）→ `data_version` 必须递增：旧快照不可变、原样保留，新快照另起版本号；
- 在途实验不自动失效：manifest 对比发现 data_version 漂移 → 标记“版本漂移”，建议在任何 gate 判定前用新版本重跑，但不强制作废既有结果；
- 消费端读取时以 manifest 记录的 data_version 为准，禁止跨版本混读同一实验。
```

That's 3 bullets. Good. The review fix suggestion: "manifest 增修订差异记录+消费端版本失效策略，写入集成 §1.2". Include "manifest 记录修订差异"? The orchestrator instruction: "document the rule as 3-4 bullet lines" with specified content. I'll write 4 bullets:

- 修订检测：周日全量校验发现 TimescaleDB 历史分区被修订（回补/更正）时，`data_version` 必须递增——新修订生成新快照，旧快照不可变且保留；
- manifest 记录：新版本 manifest 相对旧版本标注修订分区清单（差异记录），便于审计哪些数据变了；
- 在途实验不自动作废：实验 manifest 记录的 data_version 与湖内最新版本比对，发现漂移仅打标（`data_version_drift`），建议在任何 gate 判定前用新版本重跑，不强制重跑；
- gate 判定前置检查：进入留出/dry-run 等 gate 决策前，评测台检查实验数据版本是否为当前版本。

Hmm, that's more than instructed. The orchestrator says: "when TimescaleDB revision detected by the weekly full-validation, data_version MUST bump (new snapshot, old snapshot immutable and retained); in-flight experiments pinning the old data_version are NOT auto-invalidated but flagged (manifest comparison shows data_version drift → rerun recommended before any gate decision); document the rule as 3-4 bullet lines." Keep it to 3-4 bullets covering exactly this. I'll do 3 bullets + keep tight.

**D013**: integration.md Vibe-Trading section (§二) + note in F001 design.md if it touches naming. Add "M1 出口标准" item: vibe_bridge symbol-mapping initial table (pair naming ↔ Vibe-Trading symbol ↔ Freqtrade pair), UTC alignment convention. One table skeleton + 3 lines of contract, no more.

In integration.md §2.2, after the vibe_bridge paragraph, add:

```
**M1 出口标准（契约前置，D013）**：M1 决定 Parquet 分区与 pair 命名时，必须同步产出 `src/alphamill/vibe_bridge/symbol_map.csv` 初版并冻结命名约定：

| alphamill pair（湖内命名） | Vibe-Trading symbol（local loader） | Freqtrade pair | UTC 约定 |
|---|---|---|---|
| `BTC-USDT`（okx 永续） | `BTC-USDT`（同源直映，差异行必须显式登记） | `BTC/USDT:USDT` | 湖内与两侧时间戳一律 UTC naive，K 线按交易所原始 UTC 对齐 |

契约三条：
1. 映射表是唯一翻译点：湖内 pair 命名、Vibe-Trading symbol、Freqtrade pair 三方只经此表互译，禁止散落硬编码；
2. 无法直映的 pair（命名规则冲突）必须在初版中显式标注，不允许留空；
3. 时间戳全链路 UTC（naive UTC，无时区后缀），任何本地时区换算只发生在展示层。
```

Hmm, "One table skeleton + 3 lines of contract, no more." OK. Should I mention D013 ID? The review protocol may match fixes to issue IDs. Other fixes in these docs don't reference review IDs. But for the convergence loop it helps. The orchestrator didn't ask for ID references. I'll keep it clean without D013 mention — actually, adding "（修复 D013）" could help reviewer verification but pollutes design docs. Hmm, in review-convergence loops, fixers usually just fix; the verifier greps. I'll not add IDs — keep doc style consistent. Actually wait, let me reconsider: the note says "One table skeleton + 3 lines of contract, no more". Keep minimal.

For F001 design.md: "note in F001 design.md if it touches naming". F001 migrates freqtrade user_data with kronos_cache samples, and pair naming exists in data. Does F001 touch naming? Migration copies pairs as-is. Minimal note: in design.md §4 (接口、Contract) add a line: "符号映射契约前置：F001 迁移的 pair 命名保持原样直迁；M1 数据桥落地 vibe_bridge 符号映射初版（见集成文档 §2.2 M1 出口标准），本 feature 不改命名。" That's a reasonable single-line note in §4 or §9. I'll put it in §4 under API/CLI/Adapter Contract as a bullet. Actually §4 has "### API / CLI / Adapter Contract" prose. Add a short paragraph after.

**D017**: migration-plan.md scope — add backup section. "add: daily sync of Parquet lake + manifests + TimescaleDB dumps to the user's NAS (UGREEN NAS exists on LAN); single-disk failure must not equal project loss. 3-5 lines with concrete paths/cadence; if placed in F001 scope, add one task line in tasks.md consistent with its task format."

I'll put it in migration-plan.md as a new section (七、备份与灾备) — natural home since NAS sync rides migration. Also the review fix suggestion: "F001 范围或 M1 加'每日湖+manifests 同步 NAS'，写进 deployment". Should I add a task to tasks.md? The orchestrator says "if placed in F001 scope, add one task line in tasks.md consistent with its task format". Placement decision: I'm placing it in migration-plan.md. Is migration-plan "F001 scope"? It's the F001 migration plan document. Hmm. The backup is a recurring daily sync, not a one-time migration step. But NAS sync initial setup rides the migration (M0). I think: add §七 to migration-plan + add one task in tasks.md (e.g., T018 or insert into Phase 2/3?). 

Careful: tasks.md validator checks task structure. Task format: `- [ ] T0xx (FR-xxx, AC-xxx): <action> — verify: <cmd>`. A new task needs to reference legal US/requirement/AC IDs? Rule: "每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID" — T017 has no ID reference (`- [ ] T017: 回写...`). So an ID-less task is tolerated by the validator (T017 exists). But safer to keep format. Backup task doesn't map to any existing FR. Options: (a) add task without FR reference like T017; (b) not add a task at all, only migration-plan §七. 

The orchestrator: "if placed in F001 scope, add one task line in tasks.md consistent with its task format." Placing the policy in migration-plan.md (which IS the F001 附属 doc, owned by F001). The daily sync itself is an operational recurring thing; the migration feature can include "搭建 NAS 同步" as part of M0 since "NAS sync rides the migration". I'll add one task: `- [ ] T018 (\`FR-006\`): 配置 Parquet 湖 + manifest + TimescaleDB 每日 dump 向 NAS（UGREEN）的定时同步（deployment/backup/） — verify: 手动触发一次同步并核对 NAS 上产物齐全`. Hmm, referencing FR-006 (部署编排迁入与全链路验证) is a stretch but deployment-related. T017 style: no ID. The validator — let me check what validate_spec_lifecycle.py actually checks for tasks. I should read the validator to be safe before editing tasks.md. Let me read tools/validate_spec_lifecycle.py.

Also need to check where in tasks.md to put it — adding to Phase 2 or as part of section 2? If I add T018 after T017 in section 3, that breaks the AC-chain numbering flow. Better: add to Phase 2 as T018? Task IDs are sequential; inserting T018 into Phase 2 after T010 would be out of numeric order within phases (T010 then T018 then Phase 3 T011-T013) — ugly. Alternative: append at end of §3 (验证与验收任务) as T018 after T017. Hmm, but backup setup isn't a validation task.

Alternatively add it to Phase 2 and renumber? No — renumbering breaks dependencies section and spec references? Spec doesn't reference task IDs. But minimal edit: append T018 in Phase 2 (after T010) — numeric ordering would be T005..T010, T018, then Phase 3 T011..T013. That's odd but not invalid. Actually cleaner: append T018 at the end of §2 Phase 3? Phase 3 is "全链路验证" — backup sync setup could ride as part of deployment verification... eh.

Simplest clean option: add T018 at the end of section 3 (验证与验收任务) after T017? Also odd.

Alternative: put in Phase 2 right after T010 with ID T018. The dependency section: add "T018 依赖 T010（deployment 编排就绪后配置 NAS 同步）" or similar. Actually the instruction says "one task line" — minimal. Let me check the validator first to see what constraints exist (task ID uniqueness, ordering, etc.).

Let me read the validator now. Also check BACKLOG.md to make sure I don't break bidirectional consistency (I'm not editing status/links, so fine).

**D011 remaining**: integration.md line 168 `见 docs/05` — context: Kronos deployment. Architecture doc §七 is 部署拓扑. → `见 docs/alphamill-architecture.md §七`.

Also "doc 03" — grep showed `doc 03` only in PRD (line 95), not my files. README quick-start... not mine. So my D011 fixes: integration.md ×1, spec.md ×4, tasks.md ×1, design.md ×3.

Wait, also check for other stale refs like `docs/05` spelled differently in migration-plan? Grep found none. Also `架构文档 4.4` in integration line 24 — "schema 见架构文档 4.4" refers to alphamill-architecture.md §4.4 — fine, not stale.

Let me also double check integration.md line 3: "配套：[alphamill-architecture.md](./alphamill-architecture.md)" — good.

Now frontmatter updates: spec.md `updated: 2026-09-06` → `2026-09-07`; design.md; tasks.md same. integration.md and migration-plan.md have no frontmatter — they have header lines "版本：v0.1 | 日期：2026-09-06". Should I bump those dates? The instruction only says frontmatter. Minimal: leave the 版本/日期 lines? Hmm, editing content means the docs changed on 2026-09-07. The instruction: "Update frontmatter `updated:` to 2026-09-07 where frontmatter exists." So only frontmatter files. For integration.md/migration-plan.md header date — I could bump to reflect revision, but instruction says minimal. I'll bump the date in those header lines too since they serve as the doc's date metadata and are part of my owned files' style... Actually "prefer minimal, surgical insertions" — bumping the 日期 is one tiny edit and keeps docs honest. But it might create conflicts with other agents? Other agents own PRD/architecture/etc., not these files. I'll bump 日期：2026-09-06 → 2026-09-07 in the two header lines. Hmm, wait — "版本：v0.1 | 日期：2026-09-06" — changing date without version bump is normal for doc edits. I'll do it. Actually, let me reconsider: the instruction explicitly limited to frontmatter. To avoid scope creep I'll skip non-frontmatter date edits? But then docs say 2026-09-06 while containing 09-07 content — minor. The round-1 report dated 2026-09-07. I think bumping is correct and harmless. I'll bump both header dates.

Now, before editing tasks.md, read the validator to understand task-format constraints.

Also read BACKLOG.md quickly to confirm F001 entry fields (not editing it, but to be safe).

Let me read tools/validate_spec_lifecycle.py and BACKLOG.md.
Read the round-1 report and SOP §2. Before editing tasks.md I need to check what the validator enforces on task structure.

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

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\BACKLOG.md</path>
<type>file</type>
<content>
1: # BACKLOG —— 活跃 Feature 索引
2: 
3: 本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
4: frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。
5: 
6: | Feature | 版本 | 状态 | 链接 |
7: |---|---|---|---|
8: | F001-quant-crypto-migration | 0.1 | draft | [spec](docs/features/0.1/F001-quant-crypto-migration/spec.md) |
9: 
10: > 规则：feature 状态变更（spec frontmatter）时必须同步本表；`done` 的 Feature 移出本表，
11: > 交付记录进入 `docs/features/releases/<version>.md`。
12: > 示例行（复制后替换，链接必须指向真实 spec.md）：
13: > `| F001-<name> | 0.1 | draft | [spec](docs/features/0.1/F001-<name>/spec.md) |`

(End of file - total 13 lines)
</content>
  ```
  </details>

## assistant · 2026-09-06T16:48:05Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md", "newString": "updated: 2026-09-07", "oldString": "updated: 2026-09-06"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md", "newString": "- **上游决策**：`docs/decisions/`（暂无；仓库归档处置记录于同目录 migration-plan.md §二）", "oldString": "- **上游决策**：`docs/decisions/`（暂无；仓库归档决策记录于 docs/05）"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md", "newString": "- migration-plan.md §一 迁移总览 1-9 项：数据卷、采集器、Kronos 薄壳、风控三件套、监控、部署编排、宇宙发现脚本、Freqtrade user_data。", "oldString": "- docs/05 §一 迁移清单 1-9 项：数据卷、采集器、Kronos 薄壳、风控三件套、监控、部署编排、宇宙发现脚本、Freqtrade user_data。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md", "newString": "- **SC-003**：migration-plan.md §一 迁移总览清单 9 项全部标记完成。", "oldString": "- **SC-003**：docs/05 迁移清单 9 项全部标记完成。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\spec.md", "newString": "- [x] Q-001: TimescaleDB 迁移后保留还是转纯 Parquet？ — 决策：阶段 A 保留（migration-plan.md §四），阶段 B 另立 feature 评估", "oldString": "- [x] Q-001: TimescaleDB 迁移后保留还是转纯 Parquet？ — 决策：阶段 A 保留（docs/05 §四），阶段 B 另立 feature 评估"})`


> [reasoning] Validator constraints for tasks.md:
- Top-level sections fixed (6) — I keep all.
- Phase headings only under section 2.
- Checked tasks must not contain unfinished markers.
- No task ID uniqueness/ordering checks, no requirement-reference checks on tasks. Good — I can add a task line without breaking anything.

BACKLOG consistency: F001 draft/0.1 — I'm not changing status/version. Fine.

Now execute the edits. Plan (5 tasks):

**Step 1 — D011 stale refs** (in my files):
- spec.md: lines 23, 77, 172, 206 (`docs/05` → migration-plan.md refs)
- tasks.md: line 57 (`docs/05 清单勾选` → `migration-plan.md 清单勾选`)
- design.md: lines 25, 32, 36
- integration.md: line 168 (`见 docs/05` → `见 docs/alphamill-architecture.md §七`)

**Step 2 — D010 path propagation**:
- tasks.md: T005 `data_bridge/collector/` → `src/alphamill/data_bridge/collector/`; T007 `kronos_service/` → `src/alphamill/kronos_service/`; T008 `freqtrade_bridge/risk/` → `src/alphamill/freqtrade_bridge/risk/`. T009 monitoring/, T010 deployment/ stay (non-Python).
- design.md: §1 line 28 kronos_service; §2 line 36 rewrite paths + directory decision note.
- migration-plan.md: §一 table targets: item 2 `data_bridge/collector/` → `src/alphamill/data_bridge/collector/`; item 3 `kronos_service/` → `src/alphamill/kronos_service/`; item 4 `freqtrade_bridge/risk/` → `src/alphamill/freqtrade_bridge/risk/`; item 5 `factor_factory/bench/ + validation/` → `src/alphamill/factor_factory/bench/ + src/alphamill/validation/`. Items 6 (monitoring/), 7 (deployment/), 8 (scripts/), 9 (freqtrade/user_data/) stay root (non-Python / external tool layout). Also §三 ③ `迁入本仓 kronos_service/` → `src/alphamill/kronos_service/`. Also §四 "data_bridge 照原设计导出" — concept name, no path, keep.
- integration.md: §2.2 `vibe_bridge/local_loader_config/` → `src/alphamill/vibe_bridge/local_loader_config/`; §2.4 `vibe_bridge/postmortem/` → `src/alphamill/vibe_bridge/postmortem/`; §四 `validation/` → `src/alphamill/validation/`; §五 AlphaGen `factor_factory/generators/alphagen_vendor/` → `src/alphamill/factor_factory/generators/alphagen_vendor/`; §5 vendor hygiene `generators/` 本体 → `factor_factory/generators/` 本体 (inside src? "胶水代码放 vendor 外面（generators/ 本体）" — refers to factor_factory/generators, I can write `generators/` 本体 stays as concept; minimal change: leave it, since it says "generators/ 本体" generically. Hmm — to be consistent I could leave; it's shorthand relative to the vendor path above it. Leave.); §3.1 `freqtrade_bridge/strategy_template.py.j2` → `src/alphamill/freqtrade_bridge/strategy_template.py.j2`; §五 table line 168 `kronos_service/` → `src/alphamill/kronos_service/`.

Also integration.md §1.2 partition path `lake/...` stays (data lake, root-level non-Python asset). Good.

Also add a note about layout decision somewhere in integration.md? The orchestrator says "integration.md directory mentions" — just change paths. Maybe add one line in §五 Kronos row? No, keep minimal. Maybe add a small note at top? Not required. Keep paths only.

**Step 3 — D014** integration.md §1.2: append revision policy block after the table (before §1.3). 3-4 bullets.

**Step 4 — D013** integration.md §2.2: add M1 出口标准 table skeleton + 3 contract lines. F001 design.md §4: one-line note.

**Step 5 — D017** migration-plan.md: new §七 备份与灾备 (3-5 lines). tasks.md: add one task. Where? I'll add to Phase 2 after T010 as T018? Or into section 3? Backup config is implementation → Phase 2. But numbering order... The tasks doc isn't required to be strictly ordered by ID within phases? Convention: IDs sequential. Cleanest minimal approach: append T018 at the end of Phase 2 — numbering becomes T005-T010, T018 in Phase 2, T011-T013 in Phase 3. Slightly odd but validator doesn't care. Alternatively give it T014+? IDs T014-T017 already used in section 3. So T018 it is, appended to Phase 2 (backup/DR setup belongs to implementation/deployment config). And add dependency note: `T018 依赖 T010`（deployment 就绪后配置 NAS 同步）. Also update §4 dependency list — add one line. And Phase 3 verify? Not needed.

Task line format: `- [ ] T018 [P] (\`FR-006\`): 配置 deployment/backup/ 每日同步 Parquet 湖 + manifest + TimescaleDB dump 到局域网 NAS（UGREEN） — verify: 手动触发同步，NAS 端产物齐全（湖分区/manifest/dump）`.

Hmm wait — Parquet 湖 doesn't exist in F001 (F002 scope: 不实现 Parquet 湖导出). The backup covers future lake; F001 can set up the sync job scaffold + TimescaleDB dumps + manifests dir. To stay consistent with F001 scope (non-goal: 不实现 Parquet 湖导出), the task should be: "配置每日 NAS 同步任务（TimescaleDB dump + reports + manifests 目录约定，Parquet 湖目录位预留）". Good — that respects the non-goal. Let me write: `- [ ] T018 (\`FR-006\`): 在 deployment/ 落每日 NAS 同步（TimescaleDB pg_dump + reports/ + lake 目录位预留，UGREEN NAS） — verify: 手动触发一次同步，NAS 端三类产物齐全`.

And migration-plan §七:

```
## 七、备份与灾备（单盘故障 ≠ 项目清零）

- 每日定时把三类资产同步到局域网 UGREEN NAS：TimescaleDB 逻辑 dump（`deployment/backups/db/<date>.dump`）、Parquet 湖分区（`lake/`，F002 起生效）、manifest 与报告（`lake/_manifests/`、`reports/`）；
- 同步脚本随 deployment/ 迁入（NAS 不可达时保留本地 7 天滚动副本，恢复可达后补同步）；
- 恢复演练：M0 验收时从 NAS 副本完整恢复一次 DB 到临时容器并通过对账，之后每季度抽验一次。
```

Wait — "daily sync of Parquet lake + manifests + TimescaleDB dumps to the user's NAS... 3-5 lines with concrete paths/cadence". OK my block is ~4 lines. The restore drill line is extra value; keep it short or drop? "3-5 lines" — I have 3 bullets. Fine.

Should the D017 fix live in migration-plan §七? Reviewer suggested "F001 范围或 M1 加...写进 deployment". migration-plan is the natural home per orchestrator. Good.

**Frontmatter updates**: spec.md, design.md, tasks.md `updated: 2026-09-06` → `2026-09-07`.

**Header dates**: integration.md line 3, migration-plan.md line 3: 日期 2026-09-06 → 2026-09-07.

One concern: design.md §2 line 36 references "docs/02 §三目录设计一致" — since architecture still shows flat layout and D010 decision changes it, writing "与...一致" would be false. I'll write: "迁移后模块边界与 `docs/alphamill-architecture.md` 目录设计一致（目录约定已拍板为单一 Python 布局：Python 包一律 `src/alphamill/<module>/`，非 Python 资产留在仓根）：" then the path list. That documents the decision without touching architecture (not mine).

Also spec.md — does spec contain flat paths? Line 109: `data_bridge/collector/` (FR-002), line 119 `kronos_service/` (FR-003), line 129 `freqtrade_bridge/risk/` (FR-004), line 139 `monitoring/` (FR-005), line 149 `deployment/` (FR-006). D010 propagation should include spec? Orchestrator: "propagate the layout decision through F001 tasks.md target paths, design.md module layout references, migration-plan.md target paths, and integration.md directory mentions." Spec not listed! And "prefer edits that don't touch status/links" — spec FR text edits are safe for the validator (requirement IDs unchanged, AC refs unchanged). But the orchestrator deliberately excluded spec.md from D010 propagation. Hmm, why? Maybe to keep spec as behavioral contract (paths in spec are behavioral target locations though). If tasks/design/migration-plan say src/alphamill/... but spec says data_bridge/collector/, there's an internal inconsistency — the reviewer flagged "F001 按平铺执行将落进打包盲区" referencing tasks. D010 fix suggestion: "同步改架构 §三/SOP Code Quality/F001 tasks T005-T009 路径/pyproject packages" — spec not mentioned either. 

I'll follow the orchestrator exactly: don't edit spec.md except stale refs (D011) + frontmatter date. The FR text says "迁入 `data_bridge/collector/`" — hmm, that IS a flat path in spec. But instructions are explicit about which files get D010 propagation. However, leaving spec inconsistent invites a D011-style follow-up... The orchestrator's list is deliberate ("F001 tasks.md target paths, design.md module layout references, migration-plan.md target paths, and integration.md directory mentions"). I'll respect it — spec edits limited to D011 + date. If the verifier flags spec paths, that's a decision for the orchestrator.

Wait, actually, let me reconsider once more. The spec's FR-002 says "迁入 `data_bridge/collector/`" — if tasks T005 migrates to `src/alphamill/data_bridge/collector/`, is that violating spec? Arguably spec's path is conceptual module name. Minimal-change discipline wins. Leave spec.

Also D011 in spec: line 23 "仓库归档决策记录于 docs/05" — where does 旧仓处置 live now? migration-plan §二. → "记录于 migration-plan.md §二". Line 77 "docs/05 §一 迁移清单 1-9 项" → "migration-plan.md §一 迁移总览清单 1-9 项". Line 172 SC-003 "docs/05 迁移清单 9 项全部标记完成" → "migration-plan.md §一 迁移总览 9 项全部标记完成". Line 206 Q-001 "（docs/05 §四）" → "（migration-plan.md §四）".

design.md line 25: "代码目录按 docs/05 清单物理搬迁" → "代码目录按 migration-plan.md §一 清单物理搬迁". Line 32: "docs/05 清单项勾选" → "migration-plan.md 清单项勾选". Line 36: docs/02 → architecture + rewrite.

tasks.md line 57: "docs/05 清单勾选" → "migration-plan.md 清单勾选".

integration.md line 168: "见 docs/05" → "见 docs/alphamill-architecture.md §七"。

Now also — integration.md §2.2 example config `"codes": ["BTC-USDT"]` comment mentions "映射到湖内 pair 命名（vibe_bridge 做名称翻译）" — concept, fine.

D013 M1 出口标准 block — where exactly in §2.2? After the existing paragraph "`vibe_bridge/local_loader_config/` 维护：..." Add:

```markdown
**M1 出口标准（契约前置）**：M1 冻结 Parquet 分区与 pair 命名时，必须同时产出符号映射初版表（`src/alphamill/vibe_bridge/symbol_map.csv`）并锁定 UTC 对齐约定，不允许推迟到 M3 接入时再发明：

| alphamill pair（湖内） | Vibe-Trading symbol | Freqtrade pair | 时间戳约定 |
|---|---|---|---|
| `BTC-USDT` | `BTC-USDT`（能直映则同名；冲突行显式登记） | `BTC/USDT:USDT` | 全链路 UTC，K 线按交易所原始 UTC 边界切分 |

契约三条：① 三方命名只经映射表互译，禁止散落硬编码；② 无法直映的 pair 必须在初版中显式登记翻译规则，不留空；③ 映射表进 git 并随命名变更走评审，保证历史实验可复现。
```

That's one table + 3 contract lines. Good.

F001 design.md note (§4, after the API/CLI paragraph):

"符号映射契约前置：本 feature 迁移的 pair 命名原样直迁不改名；M1 数据桥须按集成文档 §2.2「M1 出口标准」产出 vibe_bridge 符号映射初版（pair ↔ Vibe-Trading symbol ↔ Freqtrade pair + UTC 约定），避免 M3 接入时返工。"

D014 block in integration.md §1.2, after the table:

```markdown
**数据修订政策（point-in-time）**：

- 周日全量校验发现 TimescaleDB 历史数据被修订（回补/更正）时，`data_version` 必须递增：修订内容落成新快照，旧快照不可变、原样保留；
- 新版本 manifest 相对旧版本登记修订分区清单（差异记录），可审计"哪些数据变了"；
- 在途实验不作废：其实验 manifest 固定的 data_version 与湖内最新版本比对发现漂移时，仅打 `data_version_drift` 标记并提示——在任何 gate 判定（留出/dry-run 决策）前建议用新版本重跑，不强制自动重跑。
```

3 bullets. Good.

Now perform edits. Order: spec.md, design.md, tasks.md, migration-plan.md, integration.md. Multiple edit calls. Let me be careful with exact strings.

spec.md edits:
1. Line 11: `updated: 2026-09-06` → `updated: 2026-09-07` (frontmatter).
2. Line 23: `- **上游决策**：\`docs/decisions/\`（暂无；仓库归档决策记录于 docs/05）` → `...记录于同目录 migration-plan.md §二）`
3. Line 77: `- docs/05 §一 迁移清单 1-9 项：` → `- migration-plan.md §一 迁移总览 1-9 项：`
4. Line 172: `- **SC-003**：docs/05 迁移清单 9 项全部标记完成。` → `- **SC-003**：migration-plan.md §一 迁移总览清单 9 项全部标记完成。`
5. Line 206: `（docs/05 §四）` → `（migration-plan.md §四）`

design.md edits:
1. frontmatter updated → 2026-09-07
2. Line 25: `② 代码目录按 docs/05 清单物理搬迁` → `② 代码目录按 migration-plan.md §一 清单物理搬迁`
3. Line 28: `- 后端 / API：kronos_service/ 迁入；API 契约不变` → `- 后端 / API：src/alphamill/kronos_service/ 迁入；API 契约不变`
4. Line 32: `- 文档 / 配置：docs/05 清单项勾选；deployment/verify.ps1 扩展` → `- 文档 / 配置：migration-plan.md 清单项勾选；deployment/verify.ps1 扩展`
5. Line 36 rewrite.
6. §4 add D013 note.

tasks.md edits:
1. frontmatter updated → 2026-09-07
2. T005 path
3. T007 path
4. T008 path
5. T017 docs/05 → migration-plan.md
6. Add T018 in Phase 2 + dependency line in §4.

migration-plan.md edits:
1. Header date bump
2. §一 items 2/3/4/5 targets
3. §三 ③ path
4. New §七

integration.md edits:
1. Header date bump
2. Line 168 docs/05 → architecture §七 (+ kronos_service path in same line: `服务薄壳为本仓 kronos_service/` → `src/alphamill/kronos_service/`)
3. §1.2 D014 block
4. §2.2 vibe_bridge path + D013 block
5. §2.4 vibe_bridge/postmortem path
6. §3.1 freqtrade_bridge path
7. §四 validation/ path
8. §五 AlphaGen vendor path

Let me now write the edits. I'll do them file by file. Multiple parallel edit calls on the same file are risky (sequential dependency on file state? The edit tool applies to current content; parallel edits to the same file might conflict). I'll batch per file but sequential across edits to same file — actually I can issue multiple edit calls in one block even for the same file as long as oldStrings are unique and don't overlap; they're applied sequentially. Safe enough since non-overlapping unique strings. I'll still do file-by-file batches to catch errors early.

spec.md batch:
Validator checked: tasks need only fixed 6 sections + Phase headings under §2; no ID-ordering enforcement; BACKLOG untouched since F001 stays draft. Proceeding with edits.

**Step 1/5 — spec.md (D011 stale refs + frontmatter date):**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:50:02Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "updated: 2026-09-07", "oldString": "updated: 2026-09-06"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "三步走：① 数据卷按 pg_dump/restore 迁移（首选可校验方案）并逐表对账；② 代码目录按 migration-plan.md §一 清单物理搬迁并并入主仓 pyproject 依赖；③ Kronos 上游化（clone pin + HF 权重 + 薄壳改造路径）后全链路 verify。", "oldString": "三步走：① 数据卷按 pg_dump/restore 迁移（首选可校验方案）并逐表对账；② 代码目录按 docs/05 清单物理搬迁并并入主仓 pyproject 依赖；③ Kronos 上游化（clone pin + HF 权重 + 薄壳改造路径）后全链路 verify。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "- 后端 / API：src/alphamill/kronos_service/ 迁入；API 契约不变", "oldString": "- 后端 / API：kronos_service/ 迁入；API 契约不变"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "- 文档 / 配置：migration-plan.md 清单项勾选；deployment/verify.ps1 扩展", "oldString": "- 文档 / 配置：docs/05 清单项勾选；deployment/verify.ps1 扩展"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "迁移后模块边界与 `docs/alphamill-architecture.md` 目录设计一致（目录约定已拍板：Python 包一律 `src/alphamill/<module>/`，非 Python 资产留在仓根）：`src/alphamill/data_bridge/collector/`（采集）与 `src/alphamill/data_bridge/`（导出，F002 实现）分离；`src/alphamill/kronos_service/` 只做 DB→推理→信号，不含业务策略；`src/alphamill/freqtrade_bridge/risk/` 只被策略模板 import；`monitoring/`、`deployment/` 为非 Python 资产留在仓根，`deployment/` 是唯一编排入口。依赖方向单向：deploymen
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\design.md", "newString": "Kronos HTTP API 契约不变：`GET /health`、`POST /predict/{symbol}`、`POST /predict_batch`。Freqtrade 容器经 `host.docker.internal` 访问薄壳。verify 脚本契约：单命令、退出码 0/非 0。\n\n符号映射契约前置：本 feature 对 pair 命名原样直迁、不改名；M1 数据桥须按集成文档 §2.2「M1 出口标准」产出 vibe_bridge 符号映射初版（湖内 pair ↔ Vibe-Trading symbol ↔ Freqtrade pair + UTC 对齐约定），避免 M3 接入时返工。", "oldString": "Kronos HTTP API 契约不变：`GET /health`、`POST /predict/{symbol}
…[truncated])`


> [reasoning] spec.md done. Now design.md: frontmatter, D011 refs, D010 paths, D013 note.
**Step 2/5 — design.md (D011 refs + D010 paths + D013 note + date):**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:50:30Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "updated: 2026-09-07", "oldString": "updated: 2026-09-06"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- [ ] T005 [P] (`FR-002`): 采集器四模块迁入 `src/alphamill/data_bridge/collector/` 并并入 pyproject 依赖 — verify: `python -c \"import\"` 冒烟", "oldString": "- [ ] T005 [P] (`FR-002`): 采集器四模块迁入 `data_bridge/collector/` 并并入 pyproject 依赖 — verify: `python -c \"import\"` 冒烟"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- [ ] T007 (`FR-003`, `AC-002`): kronos-signal 薄壳迁入 `src/alphamill/kronos_service/` 并指向新 DB 与上游代码路径 — verify: `tests/integration/test_f001_kronos_smoke.py`", "oldString": "- [ ] T007 (`FR-003`, `AC-002`): kronos-signal 薄壳迁入 `kronos_service/` 并指向新 DB 与上游代码路径 — verify: `tests/integration/test_f001_kronos_smoke.py`"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- [ ] T008 [P] (`FR-004`): 风控三件套迁入 `src/alphamill/freqtrade_bridge/risk/` — verify: 策略 import 冒烟", "oldString": "- [ ] T008 [P] (`FR-004`): 风控三件套迁入 `freqtrade_bridge/risk/` — verify: 策略 import 冒烟"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- [ ] T010 [P] (`FR-006`): docker-compose/.env 模板/verify 脚本迁入 `deployment/`（.env 人工搬运密钥，不进 git） — verify: `docker compose config` 无报错\n- [ ] T018 [P] (`FR-006`): 在 `deployment/` 落每日 NAS 备份同步（TimescaleDB pg_dump + `reports/`，预留 `lake/` 与 manifest 目录位；目标 UGREEN NAS，见 migration-plan.md §七） — verify: 手动触发一次同步，NAS 端产物齐全", "oldString": "- [ ] T010 [P] (`FR-006`): docker-compose/.env 模板/ver
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- [ ] T017: 回写 spec 验收证据、BACKLOG 状态与 migration-plan.md 清单勾选 — verify: `python tools/validate_spec_lifecycle.py`", "oldString": "- [ ] T017: 回写 spec 验收证据、BACKLOG 状态与 docs/05 清单勾选 — verify: `python tools/validate_spec_lifecycle.py`"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\tasks.md", "newString": "- `T005/T006/T008/T009/T010 [P]`：互相可并行（不同目录、无共享状态），但均依赖 T002。\n- `T010 -> T018`：NAS 备份同步随部署编排就绪后配置。", "oldString": "- `T005/T006/T008/T009/T010 [P]`：互相可并行（不同目录、无共享状态），但均依赖 T002。"})`


> [reasoning] Now tasks.md: frontmatter, D010 paths (T005/T007/T008), D011 (T017), D017 task T018 + dependency line.
**Step 3/5 — tasks.md (D010 paths + D011 + D017 task + date):**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:50:55Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md", "newString": "> 版本：v0.1 | 日期：2026-09-07 | 决策：quant-crypto 仓库**归档废弃**，资产一次性清算迁入本仓", "oldString": "> 版本：v0.1 | 日期：2026-09-06 | 决策：quant-crypto 仓库**归档废弃**，资产一次性清算迁入本仓"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md", "newString": "| 2 | 数据采集器 | `data-collector/`（ccxt_ingestor、db_writer、historical_backfill、symbol_manager、derivatives_market_backfill） | `src/alphamill/data_bridge/collector/` | 并入主仓依赖管理；保留 REST 轮询模式 |\n| 3 | Kronos 服务薄壳 | `kronos-signal/`（server/generator/db_adapter/kronos_real） | `src/alphamill/kronos_service/` | db_adapter 改读迁移后 DB；上游 Kronos 代码改为 clone+pin（见第三节） |\n| 4 | 风控三件套 | `risk/`
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md", "newString": "③ 服务薄壳：quant-crypto 的 kronos-signal/ FastAPI 包装迁入本仓 src/alphamill/kronos_service/", "oldString": "③ 服务薄壳：quant-crypto 的 kronos-signal/ FastAPI 包装迁入本仓 kronos_service/"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md", "newString": "1. **M0（新增，~2-3 天）**：数据卷迁移 + 采集器/薄壳/风控/监控代码搬迁 + verify 全绿\n2. M1 起：所有开发只在 AlphaMill 主仓进行；旧仓只读\n3. Kronos 上游化（clone+pin+权重下载）放在 M0 内完成，避免迁移期间推理断供\n\n## 七、备份与灾备（单盘故障 ≠ 项目清零）\n\n- 每日定时向局域网 UGREEN NAS 同步三类资产：TimescaleDB 逻辑 dump（`deployment/backups/db/<date>.dump`）、Parquet 湖分区（`lake/`，F002 起生效）+ manifest（`lake/_manifests/`）、对账与报告（`reports/`）；\n- 同步脚本随 `deployment/` 迁入；NAS 不可达时本地保
…[truncated])`


> [reasoning] Now migration-plan.md: header date, D010 paths (§一 items 2/3/4/5, §三 ③), new §七 (D017).
**Step 4/5 — migration-plan.md (D010 paths + D017 备份节 + date):**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:51:23Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "> 版本：v0.1 | 日期：2026-09-07 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)", "oldString": "> 版本：v0.1 | 日期：2026-09-06 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "| 质量继承 | `ohlcv_quality_flags` 未解决标记 > 0 的分区在 manifest 里标注，评测台可选跳过 |\n\n**数据修订政策（point-in-time）**：\n\n- 周日全量校验发现 TimescaleDB 历史数据被修订（回补/更正）时，`data_version` 必须递增：修订内容落成新快照，旧快照不可变、原样保留；\n- 新版本 manifest 相对旧版本登记修订分区清单（差异记录），可审计\"哪些数据变了\"；\n- 在途实验不自动作废：实验 manifest 固定的 data_version 与湖内最新版本比对发现漂移时，仅打 `data_version_drift` 标记——建议在任何 gate 判定（留出/dry-run 决策）前用新版本重跑，但不强制。", "oldString": "| 质量继承 | `ohlcv_quality_flags` 未解决标记
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "`vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。\n\n**M1 出口标准（契约前置）**：M1 冻结 Parquet 分区与 pair 命名时，必须同时产出符号映射初版表（`src/alphamill/vibe_bridge/symbol_map.csv`）并锁定 UTC 对齐约定，不允许推迟到 M3 接入时再发明：\n\n| alphamill pair（湖内） | Vibe-Trading symbol | Freqtrade pair | 时间戳约定 |\n|---|---|---|---|\n| `BTC-USDT` | `BTC-USDT`（能直映则同名） | `BTC/USDT:USDT` | 全链路 UTC，K 线按交易所原始 UTC 边界切分 |\n\n契约三条：①
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "- 工作流（`src/alphamill/vibe_bridge/postmortem/`）：收集材料 → `vibe-trading run -p \"<复盘 prompt>\"` → 归因报告落 `reports/postmortem/` → 提取新假设进入生成器队列（人工审阅后生效）。", "oldString": "- 工作流（`vibe_bridge/postmortem/`）：收集材料 → `vibe-trading run -p \"<复盘 prompt>\"` → 归因报告落 `reports/postmortem/` → 提取新假设进入生成器队列（人工审阅后生效）。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "# src/alphamill/freqtrade_bridge/strategy_template.py.j2 渲染产物骨架", "oldString": "# freqtrade_bridge/strategy_template.py.j2 渲染产物骨架"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "quant-crypto 的门禁脚本参数化迁移到 `src/alphamill/validation/`：", "oldString": "quant-crypto 的门禁脚本参数化迁移到 `validation/`："})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "| **AlphaGen** | **vendor** 进 `src/alphamill/factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md`；不考虑跟随上游 |", "oldString": "| **AlphaGen** | **vendor** 进 `factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md
…[truncated])`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "| Kronos | 独立服务（上游 clone + pin commit，权重 HuggingFace 下载） | 模型代码上游化；服务薄壳为本仓 `src/alphamill/kronos_service/` | pin 上游 commit；见 docs/alphamill-architecture.md §七 |", "oldString": "| Kronos | 独立服务（上游 clone + pin commit，权重 HuggingFace 下载） | 模型代码上游化；服务薄壳为本仓 `kronos_service/` | pin 上游 commit；见 docs/05 |"})`


> [reasoning] Now integration.md: header date, D011 line 168, D014 block in §1.2, D013 block in §2.2 + vibe_bridge paths, §2.4 path, §3.1 path, §四 validation path, §五 AlphaGen vendor path + kronos_service path.
**Step 5/5 — integration.md (D010 paths + D014 + D013 + D011 + date):**

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:51:53Z

- **tool**: `bash({"command": "python tools/validate_spec_lifecycle.py", "workdir": "D:\\Projects\\alphamill"})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration", "pattern": "docs/0|doc 0"})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs", "pattern": "`?(data_bridge|factor_factory|freqtrade_bridge|kronos_service|vibe_bridge|validation)/"})`


> [reasoning] All edits applied. Now verify:
1. Run validator.
2. Grep for remaining stale refs in my files.
3. Grep for remaining flat module paths in my files.
All edits applied. Now validating:

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No matches found
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 39 match(es) in 12 file(s)

D:\Projects\alphamill\docs\alphamill-research-factor-mining.md
  65: - **对接策略：vendor 而非安装**——① 将 `alphagen/` 核心（expression / tensor calculator / LinearAlphaPool）vendor 进 `factor_factory/generators/alphagen_vendor/`；② **整个丢弃 requirements.txt**，自定现代栈（torch 2.x 最新 + numpy 2.x + pandas 2.x + sb3 最新/gymnasium），不装 qlib/baostock/旧 matplotlib；③ 自写 feather→tensor 数据适配器替代 `alphagen_qlib`（本来就是计划，顺带绕开装错包的坑）；④ PPO 训练器用 stable-baselines3 2.0 + gym 0.26，升到 sb3 最新版需小改 env wrapper（gym→gymnasium）。冒烟目标：现代栈跑通 1 个训练 epoch 并向池子产出因子。预估 shakedown 1-2 天 + 适配器约 1 周。

D:\Projects\alphamill\docs\alphamill-integration.md
  70: `vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。
  72: **M1 出口标准（契约前置）**：M1 冻结 Parquet 分区与 pair 命名时，必须同时产出符号映射初版表（`s
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:52:04Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "`src/alphamill/vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。", "oldString": "`vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "newString": "| 选择期脚本 | 窗口/阈值外置配置（`src/alphamill/validation/config.yaml`），规则先于数据确定并 git 提交 |", "oldString": "| 选择期脚本 | 窗口/阈值外置配置（`validation/config.yaml`），规则先于数据确定并 git 提交 |"})`


> [reasoning] Validator green. Analysis of remaining matches:

1. integration.md line 70: `vibe_bridge/local_loader_config/` — I missed this one! Line 70 is the original paragraph I anchored on; my edit added the M1 block after it but didn't change its path. Fix: `src/alphamill/vibe_bridge/local_loader_config/`.
2. integration.md line 163: `validation/config.yaml` — this is a config file path within validation/. Should be `src/alphamill/validation/config.yaml`. Hmm — minimal. The module path mention "validation/config.yaml" refers to the config inside the module. For consistency, prefix it. Also architecture doc line 204 says "全文档所有'平铺目录'（data_bridge/、factor_factory/…）表述一律指该布局" — architecture added a global rule that flat mentions refer to the src layout. But that's the architecture agent's fix, not mine. Still, for my files, I'll prefix line 163 to be safe: `src/alphamill/validation/config.yaml`.

Also ADR docs (0001/0002) and research doc mention flat paths — NOT my files. Architecture has the global rule covering them. decisions/0004, 0003 `validation/config.yaml` — not mine.

3. spec.md lines 78, 109, 119, 129: flat paths in spec FR text. The orchestrator excluded spec.md from D010 propagation. Architecture line 204's global rule ("全文档所有平铺目录表述一律指该布局") — does it cover docs/? It says "全文档所有'平铺目录'（`data_bridge/`、`factor_factory/`…）表述一律指该布局" — that's in architecture doc §三, a global convention statement that resolves spec's flat mentions too. Given that explicit global rule exists (another agent fixed architecture), leaving spec.md as-is is now consistent — the flat names are concept names resolved by the global rule. And the orchestrator explicitly told me to only change tasks/design/migration-plan/integration. Also "Keep concept names identical; only paths change" — for spec, FR behavioral text stays. I'll leave spec.md FR paths. Hmm, but the grep shows they could be flagged by the verifier... The architecture global rule was clearly added to handle exactly this. Plus my instruction: "Keep concept names identical; only paths change" for the four listed docs. Spec untouched per instruction. OK.

Wait — but should I double check whether architecture doc really has that rule now (line 204 shows it does — added by another agent concurrently). Yes: "**单一 Python 布局 = `src/alphamill/<module>/`**...全文档所有'平铺目录'（`data_bridge/`、`factor_factory/`…）表述一律指该布局。" Great — that confirms the decision and provides the umbrella. My design.md line 36 says "与 docs/alphamill-architecture.md 目录设计一致（目录约定已拍板...）" — now true.

4. integration.md line 70 fix needed (local_loader_config path). Let me fix that + line 163 validation/config.yaml.

Also check integration.md §5 vendor hygiene rules: "胶水代码（feather→tensor 适配器、FactorDef 包装）放 vendor **外面**（`generators/` 本体）" — generic shorthand, fine.

Also check remaining docs/0 refs in integration.md — grep earlier on F001 dir showed none; for integration.md the last grep output doesn't show docs/05 anymore (line 182 fixed). Let me also grep integration.md for `docs/0` to confirm, plus check "见 docs/05" gone. Earlier grep (docs-wide, first one) showed integration.md line 168 was the only one. Fixed.

Also double-check: integration.md line 145 (§四 KPI 检查 row) mentions `reports/phase4-kpi-*` — fine.

One more: integration.md §1.2 partition table row `lake/...` — root-level data assets, fine.

Fix the two remaining integration.md paths now, then re-run validator + final greps.
Validator green. Two residual flat paths in integration.md (line 70 `vibe_bridge/local_loader_config/`, line 163 `validation/config.yaml`) need the prefix. spec.md FR text keeps concept names — architecture doc now carries the global rule that flat mentions resolve to `src/alphamill/<module>/`, so no spec body change (per instruction).

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Edit applied successfully.
  ```
  </details>

## assistant · 2026-09-06T16:52:38Z

- **tool**: `bash({"command": "python tools/validate_spec_lifecycle.py", "workdir": "D:\\Projects\\alphamill"})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs\\alphamill-integration.md", "pattern": "docs/0|doc 0|`?(data_bridge|factor_factory|freqtrade_bridge|kronos_service|vibe_bridge|validation)/"})`
- **tool**: `grep({"include": "*.md", "output_mode": "content", "path": "D:\\Projects\\alphamill\\docs\\features\\0.1\\F001-quant-crypto-migration", "pattern": "updated: |M1 出口标准|数据修订政策|备份与灾备|T018"})`


> [reasoning] Final verification: re-run validator, confirm no docs/0 stale refs in my 5 files, confirm no unprefixed module paths in my 5 files (excluding spec.md body which is intentionally kept as concept names), and confirm D014/D013/D017 blocks are present. Also verify frontmatter dates.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 8 match(es) in 1 file(s)

D:\Projects\alphamill\docs\alphamill-integration.md
  70: `src/alphamill/vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。
  72: **M1 出口标准（契约前置）**：M1 冻结 Parquet 分区与 pair 命名时，必须同时产出符号映射初版表（`src/alphamill/vibe_bridge/symbol_map.csv`）并锁定 UTC 对齐约定，不允许推迟到 M3 接入时再发明：
  97: - 工作流（`src/alphamill/vibe_bridge/postmortem/`）：收集材料 → `vibe-trading run -p "<复盘 prompt>"` → 归因报告落 `reports/postmortem/` → 提取新假设进入生成器队列（人工审阅后生效）。
  115: # src/alphamill/freqtrade_bridge/strategy_template.py.j2 渲染产物骨架
  159: quant-crypto 的门禁脚本参数化迁移到 `src/alphamill/validation/`：
  163: | 选择期脚本 | 窗口/阈值外置配置（`src/alphamill/validation/config.yaml`），规则先于数据确定并 git 提交 |
  179: | **AlphaGen** | **vendor** 进 `src/alphamill/factor_factory/generators/alphagen_vendor/`
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 7 match(es) in 4 file(s)

D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\design.md
  9: updated: 2026-09-07
  50: 符号映射契约前置：本 feature 对 pair 命名原样直迁、不改名；M1 数据桥须按集成文档 §2.2「M1 出口标准」产出 vibe_bridge 符号映射初版（湖内 pair ↔ Vibe-Trading symbol ↔ Freqtrade pair + UTC 对齐约定），避免 M3 接入时返工。

D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\migration-plan.md
  66: ## 七、备份与灾备（单盘故障 ≠ 项目清零）

D:\Projects\alphamill\docs\features\0.1\F001-quant-crypto-migration\tasks.md
  9: updated: 2026-09-07
  45: - [ ] T018 [P] (`FR-006`): 在 `deployment/` 落每日 NAS 备份同步（TimescaleDB pg_dump + `reports/`，预留 `lake/` 与 manifest 目录位；目标 UGREEN NAS，见 migration-plan.md §七） — verify: 手动触发一次同步，NAS 端产物齐全
  66: - `T010 -> T018`：NAS 备份同步随部署编排就绪后配置。

D:\Projects\alphamill\docs\features\0.1\F001-quant
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:52:51Z

- **tool**: `bash({"command": "set CI=\"true\" && set DEBIAN_FRONTEND=\"noninteractive\" && set GIT_TERMINAL_PROMPT=\"0\" && set GCM_INTERACTIVE=\"never\" && set HOMEBREW_NO_AUTO_UPDATE=\"1\" && set GIT_EDITOR=\":\" && set EDITOR=\":\" && set VISUAL=\"\" && set GIT_SEQUENCE_EDITOR=\":\" && set GIT_MERGE_AUTOEDIT=\"no\" && set GIT_PAGER=\"cat\" && set PAGER=\"cat\" && set npm_config_yes=\"true\" && set PIP_NO_INPUT=\"1\" && set YARN_ENABLE_IMMUTABLE_INSTALLS=\"false\" && git status --porcelain && git diff --stat",
…[truncated])`


> [reasoning] All green:
- Validator: 全部通过 (spec stays draft, Q-001 closed, AC/tests untouched, BACKLOG bidirectional consistency intact).
- integration.md: zero stale `docs/0` refs; all module paths prefixed `src/alphamill/` (§2.2 config, symbol_map, postmortem, §3.1 template, §四 validation, §五 AlphaGen vendor + Kronos).
- D014 block in integration.md §1.2 (数据修订政策, 3 bullets).
- D013: M1 出口标准 table + 3 contract lines in integration.md §2.2; one-line note in design.md §4.
- D017: migration-plan §七 (3 bullets with paths/cadence) + T018 task + dependency line.
- D011: all docs/05, docs/02 refs replaced in my 5 files.
- Frontmatter `updated: 2026-09-07` on spec/design/tasks; header dates bumped on integration/migration-plan.
- Files touched: only my 5 owned files. No commits.

Final diff check to be thorough — let me quickly confirm nothing outside my files changed. Run git status/diff --stat quickly. That's a read-only check, good practice before reporting.

  <details><summary>tool output</summary>

  ```text
M CLAUDE.md
 M README.md
 M docs/README.md
 M docs/SOP.md
 M docs/alphamill-architecture.md
 M docs/alphamill-integration.md
 M docs/alphamill-prd.md
 M docs/decisions/0001-factor-mining-engine.md
 M docs/decisions/0003-validation-gate-non-degradation.md
 M docs/features/0.1/F001-quant-crypto-migration/design.md
 M docs/features/0.1/F001-quant-crypto-migration/migration-plan.md
 M docs/features/0.1/F001-quant-crypto-migration/spec.md
 M docs/features/0.1/F001-quant-crypto-migration/tasks.md
 M docs/features/README.md
?? docs/decisions/0004-portfolio-construction.md
?? docs/reviews/CURRENT-code.md
?? docs/reviews/CURRENT-doc.md
warning: in the working copy of 'CLAUDE.md', LF will be replaced by CRLF the next time Git touches it
warning: in the working copy of 'README.md', LF will be replace
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:53:11Z


> [reasoning] Other agents' concurrent edits are present in the worktree (CLAUDE.md, README, SOP, architecture, PRD, ADRs) — expected, I didn't touch them. My changes are confined to my 5 owned files. Validator green. Done — report concisely per ADHD output style: lead with result, what now works, next action.
All 5 fixes applied, validator green, only my 5 owned files touched (other dirty files are concurrent agents' work).

**What now works** (steps 1-5 of 5 done):

1. **D010** — all Python module targets now `src/alphamill/<module>/`: tasks T005/T007/T008, design.md §1-§2, migration-plan §一 items 2-5 + §三③, integration.md ×8 (`vibe_bridge`, `freqtrade_bridge`, `validation`, `factor_factory`, `kronos_service`). Non-Python (`monitoring/`, `deployment/`, `lake/`, `scripts/`, `freqtrade/user_data/`) stay at root; spec.md body keeps concept names — architecture doc now carries the global "flat mentions = src layout" rule, so no spec contradiction.
2. **D014** — integration.md §1.2 「数据修订政策（point-in-time）」： 3 bullets (weekly validation detects revision → data_version MUST bump, old snapshot immutable/retained; manifest revision-diff record; in-flight experiments flagged `data_version_drift`, rerun recommended before gate decisions, not auto-invalidated).
3. **D013** — integration.md §2.2 「M1 出口标准（契约前置）」: symbol-map table skeleton (pair ↔ Vibe symbol ↔ Freqtrade pair + UTC) + 3 contract lines; design.md §4 one-line note (F001 migrates names unchanged, M1 owns the initial map).
4. **D017** — migration-plan.md new §七 备份与灾备 (daily NAS sync of `deployment/backups/db/<date>.dump` + `lake/`+manifests + `reports/` to UGREEN NAS, 7-day local rolling buffer, restore drill at M0 + quarterly); tasks.md T018 (`FR-006`, depends T010) + dependency line.
5. **D011** — all `docs/05`/`docs/02` refs in my 5 files → `migration-plan.md §一/§二/§四` and `docs/alphamill-architecture.md §七` (spec ×4, design ×3, tasks ×1, integration ×1). `updated: 2026-09-07` set on spec/design/tasks frontmatter; header dates bumped on the two frontmatter-less docs.

**Validation**: `python tools/validate_spec_lifecycle.py` → 全部通过 (F001 stays `draft`, Q-001 closed, AC tests paths untouched, BACKLOG bidirectional consistency intact — no status/link edits).

**Next action (<2 min)**: verifier re-runs the validator and checks D010/D013/D014/D017 blocks against CURRENT-doc.md.
