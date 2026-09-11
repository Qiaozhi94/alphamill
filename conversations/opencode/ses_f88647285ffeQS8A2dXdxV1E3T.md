---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f88647285ffeQS8A2dXdxV1E3T"
title: "Fix SOP/READMEs D009/D010/D021/D022/D023/D024/D011 (@general subagent)"
project: "D:/Projects/alphamill"
model: "glm-5.3-flash"
created_at: "2026-09-06T16:44:38Z"
updated_at: "2026-09-06T16:49:24Z"
tokens_input: 28281
tokens_output: 3342
cost: 0.0
parent_id: "ses_f886c33ddffed2Ehk0OBMbTqR2"
---

# Fix SOP/READMEs D009/D010/D021/D022/D023/D024/D011 (@general subagent)

## user · 2026-09-06T16:44:38Z

You are the FIXER in a review-convergence loop for AlphaMill (D:\Projects\alphamill), a crypto quant research system at design stage. Baseline: main @ 1bd8c4d. Language: Chinese, match each file's existing style.

YOUR FILE OWNERSHIP (do NOT touch any other file):
- docs/SOP.md
- CLAUDE.md (repo root)
- docs/README.md
- docs/features/README.md
- README.md (repo root)

First READ all five files + round-1 review report docs/reviews/CURRENT-doc.md (issues D009, D010, D021, D022, D023, D024, D011) + skim docs/alphamill-prd.md core principles section for D009 source material.

TASKS:

1. D009 (High): SOP.md §0 "项目不可违反原则" table — rows 2 and 3 are `<按项目定义>` empty placeholders while the doc claims to be the single source for principles. Fill with 4-6 REAL principles distilled from PRD/ADR-0003/CLAUDE.md (each: principle name, one-line summary, single owner doc):
   - 留出门不降级 → owner docs/decisions/0003-validation-gate-non-degradation.md
   - 无前视一等公民 → owner docs/alphamill-integration.md（无前视三层防线）
   - 研究只读 Parquet 湖快照，不直读 TimescaleDB 修订态（数据红线）→ owner docs/alphamill-architecture.md
   - 无候选通过最终留出前不触碰实盘下单路径（实盘红线）→ owner docs/alphamill-prd.md
   - 实验可复现（manifest：数据版本+代码版本+参数+结果）→ owner docs/alphamill-architecture.md（manifest 契约）
   Keep row 1 (可追溯规格优先) as is. Do not pile up more than 6 rows total; each must name exactly one owner doc.
2. D010 (High): SOP.md Code Quality line "python 按 `src/<pkg>/` 子包" → align to the decided convention: 单一布局 `src/alphamill/<module>/`（子包：data_bridge、factor_factory、validation、kronos_service 等）；非 Python 资产（docker-compose、deployment/、docs/）留仓库根。CLAUDE.md if it states layout anywhere, align likewise.
3. D021 (Low): docs/README.md — the 权威文档导航 section has "检视复盘" listed twice in a row (lines ~42-43). Delete the duplicate.
4. D001 propagation (High): docs/README.md ownership matrix — add one row: 组合构建/因子→策略映射 → `decisions/0004-portfolio-construction.md`（文件由另一 agent 并行创建，引用即为正确）。
5. D022 (Low): docs/features/README.md — "Relationship To Other Docs" section has a truncated orphan sentence "关系，稳定后应回写到这里。" — restore the intended full sentence (context: design 与架构边界的关系，稳定后应回写到这里。).
6. D023 (Low): SOP.md §3 验证与复核流程 — add one sentence disambiguating the two "verify" entrypoints: `python tools/verify.py` = 代码质量门禁（唯一公开验证入口）；`deployment/verify.ps1` = 全链路验收脚本（规划中，目录未建，随 F001 迁移落地）——同名不同物。Note deployment/ dir does not exist yet, phrase as planned.
7. D024 (Low): README.md root — "相关项目" section references D:\Projects\quant-crypto and D:\Projects\tradingview-quant-research absolute machine paths → replace with project names + relative-style references (e.g. `../quant-crypto`（本机路径，已归档）or just descriptive names). Keep meaning.
8. D011: fix any stale doc refs (docs/02-*, docs/05-*, "doc 03") in your five files → current names.
9. CLAUDE.md "当前结构" — docs/decisions/ line lists ADR 0001/0002/0003; extend with 0004 组合构建. Also CLAUDE.md line about 质量门禁 stays as is (tools/verify.py is already the stated entry).

Update each edited file's frontmatter `updated:` to 2026-09-07 (SOP.md, docs/README.md, docs/features/README.md have frontmatter; CLAUDE.md/README.md may not — if absent, skip).

VALIDATION: run `python tools/validate_spec_lifecycle.py` (cwd D:\Projects\alphamill) — must stay green; ignore unrelated concurrent-edit failures. Also verify every markdown link you touch points to an existing file (ls the target).

MUST NOT: touch docs/alphamill-prd.md / architecture / integration / decisions/* / features/0.1/* / any code file; commit.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-06T16:44:38Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\CLAUDE.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\README.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\features\\README.md"})`
- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\README.md"})`


> [reasoning] Let me start by reading all the required files: the five owned files, the review report, and the PRD core principles section.

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
<path>D:\Projects\alphamill\CLAUDE.md</path>
<type>file</type>
<content>
1: # AlphaMill
2: 
3: 以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行（中文别名：淘沙）
4: 
5: ## 当前结构
6: 
7: - `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
8: - `docs/alphamill-architecture.md`：分层架构与接口契约（架构真相源），随实现迭代。
9: - `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
10: - `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
11: - `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级。
12: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-crypto 资产清算迁移操作手册（F001 附属）。
13: - `docs/README.md`：文档所有权地图（唯一入口，两次点击可达任何权威文档）。
14: - `docs/SOP.md`：开发流程与质量门约定。
15: - `docs/features/`：SDD feature 规格目录，按大版本分层（0.1、0.2…）；
16:   `docs/f
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [docs, index, ownership]
3: doc_kind: guide
4: created: 2026-09-06
5: updated: 2026-09-06
6: ---
7: 
8: # AlphaMill 文档地图
9: 
10: 本文件是仓库文档的**唯一入口与所有权索引**：从一个入口最多两次点击即可到达任何
11: 权威文档。它只记录所有权和链接，**不复制正文**。产品、架构、数据模型、Feature 状态
12: 和流程各有且只有一个机器可读拥有者。
13: 
14: ## 权威文档所有权矩阵
15: 
16: | 信息 | 唯一拥有者 | 说明 |
17: |---|---|---|
18: | 产品目标、范围和路线 | `alphamill-prd.md` | 产品真相源（G1-G5 / FR1-6 / 里程碑 M0-M4） |
19: | 全局模块、进程与运行时边界 | `alphamill-architecture.md` | 分层架构（模块级）+ 存储三件套分工 + 闭环主循环 |
20: | 字段、表、数据契约（FactorDef / 评测台 / 信号缓存 / manifest） | `alphamill-architecture.md` §四 | 接口契约真源 |
21: | 因子挖掘主引擎选型（含降级阶梯） | `decisions/0001-factor-mining-engine.md` | 选型决策（证据：`alphamill-research-factor-mining.md`） |
22: | 外部依赖管理策略（vendor
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\features\README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [features, spec-driven-development, docs]
3: doc_kind: guide
4: created: 2026-09-06
5: updated: 2026-09-06
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
26:       spec.
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\README.md</path>
<type>file</type>
<content>
1: # AlphaMill（淘沙）
2: 
3: > 加密量化研究系统 v2 — 以**因子假设吞吐量**为核心指标：程序化批量挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行，Vibe-Trading 作为研究/回测/复盘上层建筑。
4: >
5: > 版本：v0.1 | 日期：2026-09-06 | 状态：设计阶段（未开工）
6: 
7: ---
8: 
9: ## 项目定位（一句话）
10: 
11: 不重造轮子：**quant-crypto 一次性清算迁移**（数据湖/风控/监控资产并入本仓，原仓库归档），接入 **Vibe-Trading**（研究回测复盘上层）与 **Freqtrade**（交易执行基建），补齐唯一致命缺口——**因子自动挖掘模块**。
12: 
13: ## 背景
14: 
15: 上一代项目 `D:\Projects\quant-crypto` 用 5 周建成完整基础设施（631 万行 OHLCV 数据湖、Kronos 信号 RankIC>0.05、Freqtrade dry-run、风控三件套），但 5 周只测了 3 个信号族，所有候选死在最终 90 天留出门（`blocked_no_paper_candidate`）。根因不是基建，是**假设吞吐量低**（~5 个/周 vs 需要 100+/周）。AlphaMill 的答案：程序化因子挖掘 + 统一评测台 + Vibe-Trading 复盘层。
16: 
17: ## 文档索引
18: 
19: | 文档 | 内容 |
20: |---|---|
21: | [docs/alphamill-prd.md](docs/alpha
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:44:46Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\reviews\\CURRENT-doc.md"})`
- **tool**: `grep({"pattern": "原则|无前视|红线|manifest", "path": "D:\\Projects\\alphamill\\docs\\alphamill-prd.md", "output_mode": "content", "head_limit": 40})`


> [reasoning] Now let me read the review report and skim the PRD core principles.

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
Found 10 match(es) in 1 file(s)

D:\Projects\alphamill\docs\alphamill-prd.md
  19: | 信号缓存模式 | ✅ 预计算 → feather → 策略按时间戳读取，**已通过无前视审计** | `freqtrade/user_data/kronos_cache/` |
  57: | G5 | 全链路可复现 | 100% 实验有 manifest（数据版本 + 代码版本 + 参数 + 结果摘要） |
  78: | S4 | 失败复盘 | 留出失败的候选 → Vibe-Trading agent 读取实验 manifest + 报告 → 产出归因与新假设 |
  88: - FR1.1 定时任务将 TimescaleDB 核心表导出为 **Parquet 分区 + manifest.json**（来源、抓取时间、口径、版本号）。
  104: - FR3.3 无前视审计：每个新因子必须通过独立逐 K 线重放器（复用 `independent_cross_backtest.py`）+ 信号缓存时间戳对齐检查。
  111: - FR4.3 agent 复盘工作流：输入失败实验的 manifest + 报告 → 产出归因分析 + 新特征假设清单（人审后进入 FR2.1 生成器队列）。
  123: - FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。
  132: | 可复现 | 任一历史结果可从 manifest 从零复现（对齐 research.md 第八节验收标准） |
  133: | 无前视 | 所有因子定义过 AST 纯度检查（借用 Vibe-Trading Alpha Zoo 的 lookahead 哨兵思
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:44:55Z

- **tool**: `grep({"include": "{README.md,CLAUDE.md,SOP.md}", "output_mode": "content", "path": "D:\\Projects\\alphamill", "pattern": "docs/0[0-9]|doc 0[0-9]|docs/sop|docs/readme"})`
- **tool**: `bash({"command": "ls docs/decisions/ docs/features/0.1/F001-quant-crypto-migration/ && ls docs/alphamill-architecture.md docs/alphamill-integration.md docs/alphamill-prd.md", "workdir": "D:\\Projects\\alphamill"})`


> [reasoning] I have all the material I need. Let me check the stale doc refs (D011) in my five files. Let me grep for docs/02, docs/05, "doc 03" in my five files:

From README.md (root): line 54: "（见 docs/05）" — stale ref. Need to fix to current name. The migration table is in architecture doc per D011. Let me check what the architecture doc name is: `docs/alphamill-architecture.md`. The README line 54 says "TimescaleDB 数据卷、风控三件套、Grafana/Prometheus 配置随迁移并入本仓（见 docs/05）" — the migration table is in alphamill-architecture.md (per 文档索引: "quant-crypto 资产清算迁移表" is in alphamill-architecture.md). So replace "（见 docs/05）" with "（见 docs/alphamill-architecture.md）" or link. Actually a better fix: link to the F001 migration-plan. The row is about quant-crypto 资产清算迁入, migration plan is at docs/features/0.1/F001-quant-crypto-migration/migration-plan.md. The review says stale refs correspond to files renamed alphamill-*. docs/05 was likely migration-related. The architecture doc has the "quant-crypto 资产清算迁移表". I'll point to alphamill-architecture.md.

Let me also grep my five files for docs/02, docs/05, doc 03.
Now checking stale refs (D011) in my five files:

  <details><summary>tool output</summary>

  ```text
Found 1 match(es) in 1 file(s)

D:\Projects\alphamill\README.md
  54: | quant-crypto 资产（清算迁入） | 数据湖/风控/监控 | TimescaleDB 数据卷、风控三件套、Grafana/Prometheus 配置随迁移并入本仓（见 docs/05） |
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
[31;1mGet-ChildItem: [31;1mCould not find a part of the path 'D:\Projects\alphamill\docs\decisions\docs\features\0.1\F001-quant-crypto-migration'.[0m
  ```
  </details>

## assistant · 2026-09-06T16:45:16Z

- **tool**: `bash({"command": "Get-ChildItem docs\\decisions | Select-Object Name; Test-Path docs\\features\\0.1\\F001-quant-crypto-migration\\migration-plan.md; Test-Path docs\\alphamill-architecture.md; Test-Path docs\\alphamill-integration.md; Test-Path docs\\alphamill-prd.md; Test-Path docs\\reviews\\RETROSPECTIVE.md", "workdir": "D:\\Projects\\alphamill"})`


> [reasoning] The bash command had an issue with PowerShell path handling. Let me run separate commands.

  <details><summary>tool output</summary>

  ```text
[32;1mName[0m
[32;1m----[0m
000-template.md
0001-factor-mining-engine.md
0002-external-dependency-policy.md
0003-validation-gate-non-degradation.md
True
True
True
True
True
  ```
  </details>

## assistant · 2026-09-06T16:45:29Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md", "newString": "created: 2026-09-06\nupdated: 2026-09-07\n---", "oldString": "created: 2026-09-06\nupdated: 2026-09-06\n---"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md", "newString": "| 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |\n| 2 | 留出门不降级 | 任何候选必须通过最终 90 天留出（≥30 笔）才能进 paper；吞吐提升只来自假设数量，不来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |\n| 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |\n| 4 | 数据红线（只读湖快照） | 研究/回测只读 Parquet 湖不可变快照（data_version），不直读 TimescaleDB 修订态 | `docs/alphamill-archite
…[truncated])`


> [reasoning] All target files exist. Now I'll make the edits.

**1. SOP.md edits:**
- D009: fill rows 2 and 3 in the principles table with 5 real principles (making 6 rows total). Each: principle name, one-line summary, single owner doc.
  - Row 2: 留出门不降级 → `docs/decisions/0003-validation-gate-non-degradation.md`
  - Row 3: 无前视一等公民 → `docs/alphamill-integration.md`
  - Row 4: 数据红线 → `docs/alphamill-architecture.md`
  - Row 5: 实盘红线 → `docs/alphamill-prd.md`
  - Row 6: 实验可复现 → `docs/alphamill-architecture.md`
  
  Total 6 rows — within the ≤6 limit. Keep row 1 as is. The owner column in rows 2/3 currently says `docs/alphamill-prd.md` / `-architecture.md` and `docs/decisions/` — these get replaced with the single owners.

- D023: §3 add one sentence disambiguating verify entrypoints.
- D010: Code Quality line: "python 按 `src/<pkg>/` 子包" → 单一布局 `src/alphamill/<module>/`（子包：data_bridge、factor_factory、validation、kronos_service 等）；非 Python 资产（docker-compose、deployment/、docs/）留仓库根。
- frontmatter updated: 2026-09-07.

**2. CLAUDE.md:**
- D010: check if layout stated anywhere. CLAUDE.md doesn't state layout explicitly (tech stack mentions `kronos_service/` as "本仓 kronos_service/" — hmm "GPU 推理薄壳为本仓 `kronos_service/`". That's a module name reference; with the decided convention it'd be `src/alphamill/kronos_service/`. But I should be careful not to overreach. The task says "CLAUDE.md if it states layout anywhere, align likewise." The `kronos_service/` mention is a layout-ish statement. Actually it says "GPU 推理薄壳为本仓 `kronos_service/`" — this is a reference to module location. Under the decided convention, it lives at `src/alphamill/kronos_service/`. I could leave it, since it refers to the module, not the layout. But it could mislead. Minimal touch: leave it — it names the service, not a path. Hmm, but to be safe and aligned, I could adjust to `src/alphamill/kronos_service/`. The instruction says align "if it states layout anywhere". That line states where kronos_service lives. I'll update it to `src/alphamill/kronos_service/` to be consistent.
  
  Actually wait — also README.md root "快速开始" has `python data_bridge/export_ohlcv.py` etc. Those are design-goal commands (with a note "命令为设计目标，实现后以实际为准"). Not required to change by tasks; leave alone. Task scope for D010 is SOP.md Code Quality + CLAUDE.md layout statements. The README commands are explicitly marked as design targets. I'll leave them.

- Task 9: CLAUDE.md decisions line 0001/0002/0003 → extend with 0004 组合构建.
- Task 9: 质量门禁 line stays as is.
- No frontmatter in CLAUDE.md → skip updated.

**3. docs/README.md:**
- D021: delete duplicate 检视复盘 line.
- D001 propagation: add ownership matrix row: 组合构建/因子→策略映射 → `decisions/0004-portfolio-construction.md`.
- frontmatter updated: 2026-09-07.

**4. docs/features/README.md:**
- D022: fix truncated orphan sentence "关系，稳定后应回写到这里。" → full sentence. Context: "design 与架构边界的关系，稳定后应回写到这里。" The current text:

```
- `docs/alphamill-architecture.md`：全局架构设计。Feature design 不应绕过其中的
  runtime / storage / safety 边界。
  关系，稳定后应回写到这里。
```

Restore intended: something like "…runtime / storage / safety 边界。design 与架构边界的关系，稳定后应回写到这里。" So the full sentence merges: "Feature design 不应绕过其中的 runtime / storage / safety 边界；design 与架构边界的关系，稳定后应回写到这里。" I'll write:

```
- `docs/alphamill-architecture.md`：全局架构设计。Feature design 不应绕过其中的
  runtime / storage / safety 边界。design 与架构边界的关系，稳定后应回写到这里。
```

- frontmatter updated: 2026-09-07.

**5. README.md root:**
- D024: 相关项目 section → replace absolute paths. E.g.:
  - `quant-crypto` — 上一代系统（本机路径 `../quant-crypto`，**已归档**…）
  - `tradingview-quant-research` — TradingView 定位调研（本机路径 `../tradingview-quant-research`）
  
  Task says: replace with project names + relative-style references (e.g. `../quant-crypto`（本机路径，已归档）or just descriptive names). Keep meaning.
  
- D011: line 54 "（见 docs/05）" → current name. The migration table lives in alphamill-architecture.md per the doc index. Change to "（见 [docs/alphamill-architecture.md](docs/alphamill-architecture.md)）" or plain text. Row says Grafana/Prometheus 配置随迁移并入本仓（见 docs/05）. Point to F001 migration-plan? The migration-plan covers 迁移清单与验收. docs/05 was likely the old migration doc. The safest: link to migration-plan since it's about 迁移并入. Actually the review D011 says "对应文件已改名 alphamill-*". So docs/05 → alphamill-architecture.md. I'll use plain reference: （迁移方案见 docs/alphamill-architecture.md 与 F001 migration-plan）? Keep minimal: replace "docs/05" with "docs/alphamill-architecture.md". 

  Also 背景 section line 15 has `D:\Projects\quant-crypto` absolute path! D024 is about PRD header per review, but task 7 says README.md root "相关项目" section. The 背景 line also has the absolute path. Task 7 scope is the 相关项目 section specifically. But D024's fix intent is machine-specific absolute paths. The task explicitly scopes to 相关项目 section. Hmm — should I also fix 背景? Task says "D024 (Low): README.md root — '相关项目' section references D:\Projects\quant-crypto and D:\Projects\tradingview-quant-research absolute machine paths → replace...". It scopes to 相关项目. But 背景 line 15 also contains `D:\Projects\quant-crypto`. The fixer role should stay in scope, but fixing the same issue in the same file is defensible and low-risk. The review's D024 fix suggestion: "改为相对/仓内引用或显式标注'本机路径'". I'll fix both occurrences in README.md since they're the same issue class in my owned file — replace `D:\Projects\quant-crypto` in 背景 with `quant-crypto`（上一代仓库）or just "上一代项目 quant-crypto". Keep meaning: "上一代项目 quant-crypto 用 5 周建成…". That keeps meaning and removes the machine path.

  For 相关项目:
  ```
  - `../quant-crypto`（本机相对路径）— 上一代系统（**已归档**：资产清算迁移至本仓，方案见 [F001 migration-plan](...)）
  - `../tradingview-quant-research`（本机相对路径）— TradingView 定位调研（可视化/Alert 层的参考依据）
  ```

- No frontmatter in README.md → skip.

Now write the edits. Start with SOP.md.
All targets verified. Now applying edits — SOP.md first (D009 principles table, D010, D023, frontmatter):

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

## assistant · 2026-09-06T16:46:24Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md", "newString": "- 唯一公开验证入口：`python tools/verify.py`，按固定顺序运行门禁与测试，失败即非零。\n  注意区分同名不同物的两个入口：`python tools/verify.py` 是代码质量门禁（唯一公开\n  验证入口）；`deployment/verify.ps1` 是规划中的全链路验收脚本（目录尚未创建，随\n  F001 迁移落地），二者不是同一件事。", "oldString": "- 唯一公开验证入口：`python tools/verify.py`，按固定顺序运行门禁与测试，失败即非零。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md", "newString": "- 分层与命名约定：node 见 `docs/decisions/` 目录结构 ADR；python 采用单一布局\n  `src/alphamill/<module>/`（子包：data_bridge、factor_factory、validation、\n  kronos_service 等）；非 Python 资产（docker-compose、deployment/、docs/）留仓库根。", "oldString": "- 分层与命名约定：node 见 `docs/decisions/` 目录结构 ADR；python 按 `src/<pkg>/` 子包。"})`

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

## assistant · 2026-09-06T16:46:47Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\CLAUDE.md", "newString": "- `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射）。", "oldString": "- `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级。"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\CLAUDE.md", "newString": "  Kronos（上游 clone + pin；GPU 推理薄壳为本仓 `src/alphamill/kronos_service/`）", "oldString": "  Kronos（上游 clone + pin；GPU 推理薄壳为本仓 `kronos_service/`）"})`


> [reasoning] SOP.md done. Now CLAUDE.md: task 9 (decisions line + 0004) and D010 alignment (kronos_service reference). CLAUDE.md has no frontmatter → skip updated.
SOP.md done. Now CLAUDE.md (decisions line + kronos_service layout alignment; no frontmatter, skip `updated:`):

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

## assistant · 2026-09-06T16:47:12Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\README.md", "newString": "created: 2026-09-06\nupdated: 2026-09-07\n---", "oldString": "created: 2026-09-06\nupdated: 2026-09-06\n---"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\README.md", "newString": "| 验证门禁不降级 | `decisions/0003-validation-gate-non-degradation.md` | quant-crypto 教训制度化 |\n| 组合构建（因子→策略映射） | `decisions/0004-portfolio-construction.md` | 协同池组合的部署路径与权重/换手/敞口规则 |", "oldString": "| 验证门禁不降级 | `decisions/0003-validation-gate-non-degradation.md` | quant-crypto 教训制度化 |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\README.md", "newString": "- **检视复盘**：→ [`reviews/RETROSPECTIVE.md`](reviews/RETROSPECTIVE.md)\n\n## 所有权规则（机器可校验）", "oldString": "- **检视复盘**：→ [`reviews/RETROSPECTIVE.md`](reviews/RETROSPECTIVE.md)\n- **检视复盘**：→ [`reviews/RETROSPECTIVE.md`](reviews/RETROSPECTIVE.md)\n\n## 所有权规则（机器可校验）"})`

Now docs/README.md (D021 duplicate line, D001 matrix row, frontmatter):

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

## assistant · 2026-09-06T16:47:32Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\README.md", "newString": "created: 2026-09-06\nupdated: 2026-09-07\n---", "oldString": "created: 2026-09-06\nupdated: 2026-09-06\n---"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\docs\\features\\README.md", "newString": "- `docs/alphamill-architecture.md`：全局架构设计。Feature design 不应绕过其中的\n  runtime / storage / safety 边界。design 与架构边界的关系，稳定后应回写到这里。", "oldString": "- `docs/alphamill-architecture.md`：全局架构设计。Feature design 不应绕过其中的\n  runtime / storage / safety 边界。\n  关系，稳定后应回写到这里。"})`

Now docs/features/README.md (D022 orphan sentence, frontmatter):

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

## assistant · 2026-09-06T16:47:52Z

- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\README.md", "newString": "上一代项目 quant-crypto 用 5 周建成完整基础设施", "oldString": "上一代项目 `D:\\Projects\\quant-crypto` 用 5 周建成完整基础设施"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\README.md", "newString": "| quant-crypto 资产（清算迁入） | 数据湖/风控/监控 | TimescaleDB 数据卷、风控三件套、Grafana/Prometheus 配置随迁移并入本仓（迁移表见 docs/alphamill-architecture.md） |", "oldString": "| quant-crypto 资产（清算迁入） | 数据湖/风控/监控 | TimescaleDB 数据卷、风控三件套、Grafana/Prometheus 配置随迁移并入本仓（见 docs/05） |"})`
- **tool**: `edit({"filePath": "D:\\Projects\\alphamill\\README.md", "newString": "## 相关项目\n\n- `../quant-crypto`（本机路径，已归档）— 上一代系统：资产清算迁移至本仓，方案见 [F001 migration-plan](docs/features/0.1/F001-quant-crypto-migration/migration-plan.md)\n- `../tradingview-quant-research`（本机路径）— TradingView 定位调研（可视化/Alert 层的参考依据）", "oldString": "## 相关项目\n\n- `D:\\Projects\\quant-crypto` — 上一代系统（**已归档**：资产清算迁移至本仓，方案见 [F001 migration-plan](docs/features/0.1/F001-quant-crypto-migration/migration-plan.md)）\n- `D:\\Projects\\tradingview-qua
…[truncated])`


> [reasoning] Now README.md root (D024 相关项目 + 背景 absolute path, D011 docs/05). No frontmatter → skip.
Now root README.md (D024 absolute paths, D011 `docs/05` stale ref; no frontmatter, skip `updated:`):

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

## assistant · 2026-09-06T16:48:19Z

- **tool**: `bash({"command": "python tools/validate_spec_lifecycle.py", "workdir": "D:\\Projects\\alphamill"})`
- **tool**: `grep({"include": "{README.md,CLAUDE.md,SOP.md,docs/README.md,docs/features/README.md}", "output_mode": "content", "path": "D:\\Projects\\alphamill", "pattern": "docs/0[0-9]|doc 0[0-9]|D:\\\\Projects|<按项目定义>|src/<pkg>|updated: 2026-09-06"})`


> [reasoning] All edits applied. Now validate: run the validator and re-check no stale refs remain in my files.
All edits applied. Validating:

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

## assistant · 2026-09-06T16:48:38Z

- **tool**: `read({"filePath": "D:\\Projects\\alphamill\\docs\\SOP.md", "limit": 25, "offset": 19})`


> [reasoning] Validation green, no stale refs / placeholders / absolute paths / old dates remain in my five files. Let me do a final quick sanity check on the edited sections (SOP.md table + verify disambiguation) to confirm formatting, and verify the doc links I touched point to existing files (already did: 0003 exists, architecture/integration/prd exist, migration-plan exists, RETROSPECTIVE exists). The 0004 ADR is created by another agent in parallel — per task instructions, referencing it is correct.

Quick final read of SOP.md changed areas to confirm.
Green. Final spot-check of edited sections:

  <details><summary>tool output</summary>

  ```text
<path>D:\Projects\alphamill\docs\SOP.md</path>
<type>file</type>
<content>
19: | # | 原则 | 短摘要 | 规范正文唯一拥有者 |
20: |---|---|---|---|
21: | 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |
22: | 2 | 留出门不降级 | 任何候选必须通过最终 90 天留出（≥30 笔）才能进 paper；吞吐提升只来自假设数量，不来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |
23: | 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |
24: | 4 | 数据红线（只读湖快照） | 研究/回测只读 Parquet 湖不可变快照（data_version），不直读 TimescaleDB 修订态 | `docs/alphamill-architecture.md` |
25: | 5 | 实盘红线（留出前置） | 无候选通过最终留出前，不触碰实盘下单路径 | `docs/alphamill-prd.md` |
26: | 6 | 实验可复现 | 每个实验写 manifest（数据版本 + 代码版本 + 参数 + 结果），任一历史结果可从 manifest 从零复现 | `docs/alphamill-architecture.md`（manifest 契约） |
27: 
28: > 新
…[truncated]
  ```
  </details>

## assistant · 2026-09-06T16:49:01Z

All 7 issues fixed, validator green. Step: fixes done, validation done — commit left to orchestrator.

**Fixes applied (5 owned files only):**

1. **D009** — `docs/SOP.md:21-26`: principles table now 6 real rows (was 2 empty placeholders), each with a single owner doc: 留出门不降级→ADR-0003, 无前视一等公民→integration, 数据红线→architecture, 实盘红线→PRD, 实验可复现→architecture（manifest 契约）. Row 1 untouched.
2. **D010** — `docs/SOP.md` Code Quality: now `src/alphamill/<module>/` 单一布局（data_bridge/factor_factory/validation/kronos_service 等），非 Python 资产留仓库根；`CLAUDE.md` kronos_service path aligned to `src/alphamill/kronos_service/`.
3. **D021** — `docs/README.md`: duplicate 检视复盘 nav line deleted.
4. **D001 propagation** — `docs/README.md` matrix: added row 组合构建（因子→策略映射）→ `decisions/0004-portfolio-construction.md`.
5. **D022** — `docs/features/README.md`: orphan restored to “design 与架构边界的关系，稳定后应回写到这里。”
6. **D023** — `docs/SOP.md` §3: disambiguation sentence added (`tools/verify.py` = 代码质量门禁唯一公开入口；`deployment/verify.ps1` = 规划中的全链路验收，随 F001 落地).
7. **D024** — root `README.md`: both `D:\Projects\...` paths (相关项目 + 背景) replaced with `../quant-crypto`/`../tradingview-quant-research`（本机路径标注）and plain name.
8. **D011** — root `README.md` `（见 docs/05）` → `（迁移表见 docs/alphamill-architecture.md）`; no other stale refs in my 5 files (grep-verified).
9. **CLAUDE.md** decisions line extended with `0004 组合构建（因子→策略映射）`; 质量门禁 line untouched as instructed.

**Validation:** `python tools/validate_spec_lifecycle.py` → 全部通过. Frontmatter `updated: 2026-09-07` set on the 3 files with frontmatter. All referenced owner docs verified to exist (0004 referenced per instruction; created by parallel agent). No commits made.
