---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f5531a8b1ffempMnbSM5BYhbHx"
title: "Plan F007 document review (@plan subagent)"
project: "/home/georg/projects/alphamill"
model: "claude-opus-5"
created_at: "2026-09-16T15:20:44Z"
updated_at: "2026-09-16T15:26:11Z"
tokens_input: 20
tokens_output: 12515
cost: 0.0
parent_id: "ses_f55324142ffefNy2o4qhiYalh0"
---

# Plan F007 document review (@plan subagent)

## user · 2026-09-16T15:20:44Z

TASK: Produce a decision-complete work plan for a first-round, comprehensive review of the AlphaMill F007 design documentation and creation of docs/reviews/CURRENT-doc.md.
EXPECTED OUTCOME: A bounded sequence covering project baseline, governing conventions, all F007 artifacts and related contracts, correctness/quality review channels, report generation, and document validation. Identify parallelizable evidence collection and exact success criteria.
REQUIRED TOOLS: Read-only repository inspection tools only; prefer codegraph for indexed source and Read/Glob for docs/configs. No edits, no git writes.
MUST DO: Follow the loaded review-convergence workflow; account for its fixed report schema, first-round full-scan scope, severity semantics, baseline declaration, and the fact that this is document review rather than code review. Include how to handle a dirty worktree without touching unrelated changes.
MUST NOT DO: Do not modify files, commit, push, close the review loop, or assume filenames/content without inspecting them. Do not propose implementation fixes beyond review recommendations.
CONTEXT: Repository root is /home/georg/projects/alphamill. User says F007 design docs are complete and asks for a comprehensive reviewer-perspective inspection with a review document as output. Project AGENTS.md points to CLAUDE.md.

Additional requirements for this planning request:
- Answer in English.
- Write the plan in English.
- Plan well for ultrawork execution.
- Include a clear atomic commit strategy.
- Use TDD-oriented planning.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T15:20:44Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && git rev-parse --abbrev-ref HEAD && git rev-parse --short HEAD && echo \"--- STATUS ---\" && git status --porcelain | head -60 && echo \"--- COUNT ---\" && git status --porcelain | wc -l"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls -a && echo \"--- docs ---\" && ls docs 2>/dev/null && echo \"--- reviews ---\" && ls -a docs/reviews 2>/dev/null && echo \"--- gitignore ---\" && cat .gitignore 2>/dev/null"})`

I'll gather context on the repo state, conventions, and F007 artifacts before planning.

  <details><summary>tool output</summary>

  ```text
main
ab30da9
--- STATUS ---
--- COUNT ---
0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
.
..
.code-review-graph
.codegraph
.dockerignore
.git
.github
.gitignore
.omo
.pytest_cache
.ruff_cache
.sdd.json
.venv
AGENTS.md
BACKLOG.md
CLAUDE.md
README.md
conversations
db
deployment
docs
freqtrade
lake
models
monitoring
pyproject.toml
reports
scripts
src
tests
tools
uv.lock
vendor
--- docs ---
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
--- reviews ---
.
..
CURRENT-doc.md
RETROSPECTIVE.md
--- gitignore ---
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/
.venv/
venv/
dist/
build/
*.egg-info/
.idea/
.vscode/
.DS_Store

# 本机 AI 工具本地授权配置：含本机用户名路径与本地授权，不可移植
.claude/settings.local.json

# 编辑器本地历史
.history/

# 本机代理运行续接状态
.sisyphus/

# 本机
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:21:15Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== CURRENT-doc.md (head 80) ===\" && head -80 docs/reviews/CURRENT-doc.md && echo \"... TOTAL LINES:\" && wc -l docs/reviews/CURRENT-doc.md && echo \"=== RETROSPECTIVE head 60 ===\" && head -60 docs/reviews/RETROSPECTIVE.md && echo \"... TOTAL:\" && wc -l docs/reviews/RETROSPECTIVE.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== features ===\" && ls -R docs/features | head -80 && echo \"=== design ===\" && ls -R docs/design | head -60 && echo \"=== decisions ===\" && ls docs/decisions && echo \"=== F007 grep files ===\" && grep -rl \"F007\" --include=\"*.md\" --include=\"*.json\" --include=\"*.py\" --include=\"*.toml\" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=.codegraph --exclude-dir=.omo | head -40"})`


> [reasoning] 
Worktree is clean. There's already a `CURRENT-doc.md` — need to inspect it. Launching parallel exploration.

  <details><summary>tool output</summary>

  ```text
=== CURRENT-doc.md (head 80) ===
---
report_type: doc-review
round: 1
date: 2026-09-16
prior_report: none
scope: full-scan
stop_condition_met: false
severity_counts: {critical: 0, high: 14, medium: 7, low: 1}
issues:
  - id: F003-D001
    title: "factor_id 含 run_seq，跨 run 变动，与「相同 factor_id 集合」矛盾"
    severity: high
    category: correctness
    root_cause: root-cause
    origin: original-coding
    pattern_tag: "spec-internal-contradiction"
    status: open
    tracked_task: ""
    fix_summary: ""
    regression_test: "proposed:tools/check_doc_consistency.py::test_factor_id_has_no_run_seq"
    suggested_fix: "design §3 改为 factor_id = <generator>_<definition_digest[:12]>（删 run_seq），运行归属交给 run_id；同步 spec:65/259/305 与 AC-009，加跨-run 相等断言"
    disposition_reason: ""
    location: "docs/features
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== features ===
docs/features:
0.1
0.2
README.md
TEMPLATE
releases

docs/features/0.1:
F001-quant-crypto-migration
README.md

docs/features/0.1/F001-quant-crypto-migration:
design.md
migration-plan.md
spec.md
tasks.md

docs/features/0.2:
F002-data-bridge
F003-alphagen-vendor
F004-kronos-inference-runtime
F007-evaluation-gates
F008-universe-expansion

docs/features/0.2/F002-data-bridge:
design.md
spec.md
tasks.md

docs/features/0.2/F003-alphagen-vendor:
design.md
spec.md
tasks.md

docs/features/0.2/F004-kronos-inference-runtime:
design.md
spec.md
tasks.md

docs/features/0.2/F007-evaluation-gates:
design.md
spec.md
tasks.md

docs/features/0.2/F008-universe-expansion:
design.md
spec.md
tasks.md

docs/features/TEMPLATE:
design.md
spec.md
tasks.md

docs/features/releases:
0.1.md
README.md
=== 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:21:25Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== issue ids + status in CURRENT-doc ===\" && grep -E \"^  - id:|^    status:|^    severity:|^report_type|^round|^date|^scope|^stop_condition_met|^severity_counts|^feature\" docs/reviews/CURRENT-doc.md && echo \"=== body after frontmatter ===\" && awk 'f{print} /^---$/{c++; if(c==2) f=1}' docs/reviews/CURRENT-doc.md | head -60"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls docs/reviews/ -la && echo \"=== FIX-log? ===\" && ls docs/reviews/FIX-log.md 2>&1; echo \"=== F007 sizes ===\" && wc -l docs/features/0.2/F007-evaluation-gates/*.md && echo \"=== .sdd.json ===\" && cat .sdd.json && echo \"=== tools ===\" && ls tools scripts"})`


> [reasoning] I notice `docs/reviews/CURRENT-doc.md` already exists, which creates a collision with the task's expectation that this file should be created fresh — I need to check whether it's an active review loop covering F002/F003/F004/F008 and examine its scope and stop condition before proceeding, along with CLAUDE.md, SOP.md, and F007 artifacts.

I'll spawn parallel explore agents to read these key files simultaneously.
Critical finding: `docs/reviews/CURRENT-doc.md` **already exists** (466 lines, round 1, open findings on F003/F008). Let me check its scope before planning.

  <details><summary>tool output</summary>

  ```text
=== issue ids + status in CURRENT-doc ===
report_type: doc-review
round: 1
date: 2026-09-16
scope: full-scan
stop_condition_met: false
severity_counts: {critical: 0, high: 14, medium: 7, low: 1}
  - id: F003-D001
    severity: high
    status: open
  - id: F003-D002
    severity: high
    status: open
  - id: F003-D003
    severity: high
    status: open
  - id: F003-D004
    severity: high
    status: open
  - id: F003-D005
    severity: high
    status: open
  - id: F003-D006
    severity: high
    status: open
  - id: F003-D007
    severity: high
    status: open
  - id: F003-D008
    severity: high
    status: open
  - id: F003-D009
    severity: high
    status: open
  - id: F003-D010
    severity: high
    status: open
  - id: F003-D011
    severity: high
    status: open
  - id: F00
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 160
drwxr-xr-x 2 georg georg   4096 Sep 16 22:04 .
drwxr-xr-x 7 georg georg   4096 Sep 15 01:58 ..
-rw-r--r-- 1 georg georg  35300 Sep 16 22:26 CURRENT-doc.md
-rw-r--r-- 1 georg georg 117606 Sep 16 02:11 RETROSPECTIVE.md
=== FIX-log? ===
ls: cannot access 'docs/reviews/FIX-log.md': No such file or directory
=== F007 sizes ===
  261 docs/features/0.2/F007-evaluation-gates/design.md
  294 docs/features/0.2/F007-evaluation-gates/spec.md
   77 docs/features/0.2/F007-evaluation-gates/tasks.md
  632 total
=== .sdd.json ===
{
  "$comment": "SDD Flow (sdd-flow skill) 项目适配。缺省字段自动探测；规范见 ~/.config/opencode/skills/sdd-flow/references/project-adapter.md",
  "verify": ".venv/bin/python tools/verify.py",
  "test": ".venv/bin/python -m pytest -q",
  "gates": { "G1": true, "G2": false, "G3": false, "
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:21:37Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n '1,200p' CLAUDE.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"######## F007 spec.md ########\" && cat docs/features/0.2/F007-evaluation-gates/spec.md"})`


> [reasoning] I notice there's already an open F003 doc-review report sitting in CURRENT-doc.md that was never closed, and now the task wants me to create a CURRENT-doc.md for F007 too — I need to figure out how the naming convention handles two parallel doc-reviews without overwriting or conflicting with each other.

I should hold off asking about this until I've dug deeper. Let me check CLAUDE.md's conventions, look at the F007 artifacts, and verify the skill's frontmatter fields — I notice the existing F003 report is actually missing a `feature:` field, which might be part of the issue. I'll launch parallel exploration to pull in the F007 docs and the relevant governing conventions.
Now let me read the governing conventions and F007 artifacts in parallel.

  <details><summary>tool output</summary>

  ```text
# AlphaMill

AI 原生的加密量化研究与交易管线：以 AI 因子工厂为核心，贯通数据治理 → 假设与因子 →
证据评测 → 组合与策略 → Freqtrade 执行 → 监控归因与复盘（中文别名：淘沙）。

## 当前结构

- `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
- `docs/alphamill-architecture.md`：四平面架构与接口契约（架构真相源），随实现迭代。
- `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
- `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
- `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射） / 0005 呈现与观测架构 / 0006 证据边界与实验身份 / 0007 研究快照绑定（dataset 独立版本 + ResearchSnapshot） / 0008 北极星改为在跑组合持续盈利（产能降级为分母与能力标定）。
- `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-crypto 资产清算迁移操作手册（F001 附属）。
- `docs/README.md`：文档所有权地图（唯一入口，两次点击可达任何权威文档）。
- `docs/SOP.md`：开发流程与质量门约定。
- `docs/features/`：SDD fe
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
######## F007 spec.md ########
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

# F007：统一评测台与证据门禁

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
- **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
- **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级数据源，只有 `status=completed` 的运行才发完成事件）、算子能力登记表（FR-002 已登记算子能力清单的消费源）与协同池 meta-factor
- **上游决策**：ADR-0003（门禁不降级）、ADR-0005（曲线侧车）、ADR-0006（证据边界与身份）、ADR-0007（ResearchSnapshot）
- **功能类型**：
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:21:48Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"######## F007 design.md ########\" && cat docs/features/0.2/F007-evaluation-gates/design.md && echo \"######## F007 tasks.md ########\" && cat docs/features/0.2/F007-evaluation-gates/tasks.md"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== SOP ===\" && cat docs/SOP.md && echo \"=== features/README ===\" && cat docs/features/README.md"})`


> [reasoning] I should check the SOP, features/README spec lifecycle rules, the TEMPLATE structure, and F007's design/tasks docs — and I notice the existing CURRENT-doc.md is an F003 review that isn't closed, which conflicts with the plan and needs addressing. Let me gather these facts in parallel.
Key conflict found. Let me verify remaining conventions and F007 design/tasks structure.

  <details><summary>tool output</summary>

  ```text
######## F007 design.md ########
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

# F007：统一评测台与证据门禁 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。

## 0. 输入与约束

- **行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003
- **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dataset/version/value digest
- **实现约束**：研究只读有效 Parquet；执行层级显式传参；Agent 无 canonical writer/留出能力；
  必需门失败关闭；不引入 ml4t 运行时依赖

## 1. 技术概要与影响面

实现一条“冻结运行上下文 → 方法论预检 → 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== SOP ===
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
| 4 | 数据红线（只读湖快照） | 研究/回测只读 Parquet 湖不可变快照（data_version），不直读 TimescaleDB 修订态 | `docs/alphamil
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:22:01Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== BACKLOG F007 ===\" && grep -n \"F007\" BACKLOG.md && echo \"=== docs/README F007 ===\" && grep -n \"F007\" docs/README.md && echo \"=== PRD FR3/FR7 headings ===\" && grep -nE \"^#+.*(FR3|FR7)|^### FR\" docs/alphamill-prd.md | head -30 && echo \"=== ARCH sections ===\" && grep -nE \"^#+ \" docs/alphamill-architecture.md | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== tests tree ===\" && ls tests && echo \"=== f007 test files? ===\" && find tests -name \"*f007*\" 2>/dev/null | head && echo \"=== gate timing: validate_spec_lifecycle ===\" && time timeout 120 .venv/bin/python tools/validate_spec_lifecycle.py 2>&1 | tail -5 && echo \"=== check_doc_links ===\" && time timeout 120 .venv/bin/python tools/check_doc_links.py 2>&1 | tail -5"})`


> [reasoning] 
Let me confirm the cross-document reference surface and gate runtimes.

  <details><summary>tool output</summary>

  ```text
=== BACKLOG F007 ===
9:| F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
22:递增，与执行顺序无关**（如 F007 评测台先于编号更小的 F005 研究控制台执行）。
=== docs/README F007 ===
36:| 非 done Feature 派生索引 | `../BACKLOG.md` | 活跃 feature 索引（当前 F003/F007/F008） |
=== PRD FR3/FR7 headings ===
133:### FR1 数据治理与研究快照
151:### FR2 AI 因子工厂
166:### FR3 证据评测与验证
194:### FR4 组合与策略构建
208:### FR5 部署与交易执行
226:### FR6 监控、归因与学习闭环
240:### FR7 实验治理与可复现
256:### FR8 呈现与审查界面
=== ARCH sections ===
1:# AlphaMill — 系统架构设计
7:## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
30:## 一、总体架构与职责边界
69:## 二、Mermaid 架构图
71:### 2.1 闭环架构（模块级）
131:### 2.2 Alpha 生命周期数据流
171:## 三、模块与目录设计
235:## 四、关键接口契约
237:### 4.0 闭环核心对象
254:### 4.1 因子定义（FactorDef）
272:#### 4.1.1 AlphaGen 适配契约（表达式树/张量世界 ↔ FactorDef pandas 世界）
287:### 4.2
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== tests tree ===
integration
property
simulation
unit
=== f007 test files? ===
=== gate timing: validate_spec_lifecycle ===
validate_spec_lifecycle: 全部通过
timeout 120 .venv/bin/python tools/validate_spec_lifecycle.py 2>&1  0.07s user 0.03s system 90% cpu 0.107 total
tail -5  0.00s user 0.00s system 4% cpu 0.108 total
=== check_doc_links ===
check_doc_links: 相对链接全部可解析
timeout 120 .venv/bin/python tools/check_doc_links.py 2>&1  0.08s user 0.01s system 83% cpu 0.106 total
tail -5  0.00s user 0.01s system 5% cpu 0.107 total


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T15:22:35Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== RETROSPECTIVE loop headers ===\" && grep -nE \"^## 循环|^- report_type\" docs/reviews/RETROSPECTIVE.md | tail -30 && echo \"=== related_features across F007 ===\" && grep -n \"related_features\\|^updated:\\|^status:\" docs/features/0.2/F007-evaluation-gates/*.md && echo \"=== ADR sizes ===\" && wc -l docs/decisions/0003*.md docs/decisions/0005*.md docs/decisions/0006*.md docs/decisions/0007*.md docs/alphamill-prd.md docs/alphamill-archit
…[truncated])`


> [reasoning] I see a critical blocker: `docs/reviews/CURRENT-doc.md` already holds an open, unconverged F003 doc-review with 22 findings and stop_condition_met false. Creating a F007 review at that same path would overwrite it, but the review-convergence skill allows multiple CURRENT files to coexist since they're named by report_type.

I'm also spotting that finding F003-D014 claims F007's spec must declare F003 as upstream, but the current spec.md already lists F003 in related_features and mentions it in the contract section — so that finding may be stale relative to a drifted baseline, since the F003 review was written back at commit a333394 while HEAD is now ab30da9. On top of that, I notice a real inconsistency within F007 itself: spec.md lists related_features as [F002, F003, F004], while design.md and tasks.md only list [F002, F004] — that's worth flagging as its own finding.

I'm also noting design.md's created/updated timestamp looks stale against a later note, and that F007's ACs lack the "— tests:" suffix required by the README format, though that's permissible in draft status. Tasks.md is also missing the [TEST] group that design.md's preamble mandates, mirroring an issue already flagged in the F003 review.

Given all this, I think the right move is to surface the CURRENT-doc.md naming collision as an explicit decision gate in Task 0 of the plan, rather than trying to resolve it silently, so the user can confirm before the review proceeds.

  <details><summary>tool output</summary>

  ```text
=== RETROSPECTIVE loop headers ===
6:## 循环 1：全项目文档检视（项目开工前全量）
8:- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
42:## 循环 2：代码区检视（脚手架）
44:- report_type: code-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
56:## 循环 3：目标与计划专项检视（战略层）
58:- report_type: doc-review | round: 3（strategic full-scan）→ 4（diff-only 复核）| 状态: 闭环
75:## 循环 4：F001 设计文档开发前检视（full-scan）
77:- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核，含 R2-01 发现与当轮修复及封顶复核——闭环过早）→ 3（闭环后审计重开：发现 R3-01/R3-02 并当轮修复关闭）| 状态: 闭环
95:## 循环 5：目标重构文档检视
97:- report_type: doc-review | round: 1（full-scan）→ 2（diff-only，未验证即误报闭环）→ 3（回到基线重做 + diff-only 复核）| 状态: 闭环
116:## 循环 6：F001 实现代码检视（quant-crypto 迁移，v0.1 收口后）
118:- report_type: code-review | round: 1（full-scan）→ 2/3/4/5（diff-only 复核）| 状态: 闭环
233:## 循环 7：F00
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:23:03Z

I have enough context. One blocking conflict needs your decision before I finalize.

## User Request Summary
First-round comprehensive doc review of AlphaMill **F007** (统一评测台与证据门禁, 3 artifacts, 632 lines) from reviewer perspective, output `docs/reviews/CURRENT-doc.md` per review-convergence schema. Read-only planning now; no edits.

## Blocking Conflict

**`docs/reviews/CURRENT-doc.md` already exists and is an open, unclosed F003 review loop.**

- 466 lines, `report_type: doc-review`, `round: 1`, `scope: full-scan`, date 2026-09-16, baseline `main@a333394`
- 22 findings (14 high / 7 medium / 1 low), **all `status: open`**, `stop_condition_met: false`
- No `FIX-log.md` exists → the fix side has not yet declared anything
- Its own body says "等待修复方按 `FIX-log.md` 逐条声明，再进 Round 2"
- `RETROSPECTIVE.md` has 12 closed loops; the F003 loop is **not** among them

Writing the F007 review to that same path would destroy an active review loop's only record (the file is gitignored — `git` cannot recover it). Skill §8 also says multiple `CURRENT-*.md` may coexist, but its naming is `CURRENT-<report_type>.md`, which collides here.

## Question (pick one)

1. **Archive-then-reuse** — first append the F003 issue table verbatim into `RETROSPECTIVE.md` as an explicitly **unclosed/carried-forward** loop, then write F007 into `CURRENT-doc.md`. (Loses live F003 loop continuity; deviates from skill, which only permits RETROSPECTIVE write-back at closure.)
2. **Per-feature filenames** — write to `docs/reviews/CURRENT-doc-F007.md`, leave F003's file untouched. Both `.gitignore`d by `docs/reviews/*`. Deviates from the literal `CURRENT-<type>.md` name, but matches the skill's explicit "多个 CURRENT-*.md 并行" allowance and the new `feature:` frontmatter field.
3. **Rename F003's file first** to `CURRENT-doc-F003.md`, then write F007 to the canonical `CURRENT-doc.md`.

**I recommend option 2** — zero risk to the F003 loop, no file moves, and the `feature: F007` frontmatter field makes the association machine-readable.

## Secondary uncertainties (I'll assume defaults unless you say otherwise)

1. **Report language** — you asked for the *plan* in English; F003's existing report and RETROSPECTIVE are Chinese. Default: **write the F007 report in Chinese** to match repo convention.
2. **Scope of "related contracts"** — default: PRD FR3/FR7, architecture §2.1/§4.0/§4.2/§4.2.1/§4.4.1/§4.5, ADR-0003/0005/0006/0007, F002/F003/F004/F008 spec+design, CLAUDE.md, docs/README.md, BACKLOG.md, features/README.md, TEMPLATE, SOP.md.
3. **`tools/verify.py`** — the F003 report notes it never finished within 300s. Default: run the three fast doc gates individually (each ~0.1s, verified) and record verify.py as "not claimed green, timeout" rather than blocking on it.
4. **Already-visible candidate findings** (I'll re-derive properly in the review, not assume): `related_features` mismatch between spec `[F002,F003,F004]` vs design/tasks `[F002,F004]`; F003-D014 asserts F007 fails to declare F003 upstream — but spec §0 *does* mention F003, so that cross-loop finding needs verification either way; `design.md` has a dated 2026-09-16 pre-development constraint requiring a `[TEST]` group in tasks.md that `tasks.md` does not have.

Confirm option 1/2/3 and I'll emit the full plan.

## user · 2026-09-16T15:24:05Z

User chose option 2: preserve docs/reviews/CURRENT-doc.md for the active F003 loop and write the new review to docs/reviews/CURRENT-doc-F007.md. Finalize the decision-complete plan now. Use Chinese report output, inspect the related contracts you identified, and use the verified fast documentation gates rather than claiming tools/verify.py green if it times out. Keep the plan bounded to first-round full-scan review and report generation; no fixes, commits, pushes, or review closure.

Additional requirements for this planning request:
- Answer in English.
- Write the plan in English.
- Plan well for ultrawork execution.
- Include a clear atomic commit strategy.
- Use TDD-oriented planning.

## assistant · 2026-09-16T15:24:05Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== check-ignore new name ===\" && git check-ignore -v docs/reviews/CURRENT-doc-F007.md; echo \"exit=$?\" && echo \"=== check-ignore existing ===\" && git check-ignore -v docs/reviews/CURRENT-doc.md; echo \"=== verify.py steps ===\" && grep -nE \"STEPS|check_|pytest|def main|subprocess|ruff\" tools/verify.py | head -40"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && echo \"=== does check_doc_links scan docs/reviews? ===\" && grep -nE \"reviews|glob|rglob|SKIP|EXCLUDE|ignore|Path\\(\" tools/check_doc_links.py | head -30 && echo \"=== validate_spec_lifecycle scope ===\" && grep -nE \"reviews|glob|rglob|features|EXCLUDE|Path\\(\" tools/validate_spec_lifecycle.py | head -30"})`


> [reasoning] 
Let me verify the mechanics the plan depends on: gitignore coverage for the new filename, and whether the doc gates scan `docs/reviews/`.

  <details><summary>tool output</summary>

  ```text
=== check-ignore new name ===
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc-F007.md
exit=0
=== check-ignore existing ===
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc.md
=== verify.py steps ===
5:→ 密钥模式扫描 → pytest → ruff check → ruff format check。任一步失败即记录，
19:import subprocess
27:    proc = subprocess.run(cmd, cwd=ROOT)
34:def main() -> int:
37:        ([sys.executable, "tools/check_doc_links.py"], "文档相对链接检查"),
38:        ([sys.executable, "tools/check_dep_pins.py"], "dev 依赖版本在 pin 范围内"),
39:        ([sys.executable, "tools/check_secrets.py"], "密钥模式扫描"),
41:        # symlink（如 .codegraph）被 pytest 当作 collection root 探查。
46:                "pytest",
53:            "pytest",
55:        ([sys.executable, "-m", "ruff", "check", "."], "ruff check"),
56:        ([sys.executable, "
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== does check_doc_links scan docs/reviews? ===
19:ROOT = pathlib.Path(__file__).resolve().parent.parent
21:SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")
22:EXCLUDED_PARTS = {"conversations", ".sisyphus"}
23:EXCLUDED_REL_PREFIXES = ("docs/research/",)
34:        candidates.extend(p for p in sorted(docs.rglob("*.md")) if p.is_file())
38:        if any(part in EXCLUDED_PARTS for part in p.relative_to(root).parts):
40:        if any(rel.startswith(prefix) for prefix in EXCLUDED_REL_PREFIXES):
77:                if target.startswith(SKIP_PREFIXES):
=== validate_spec_lifecycle scope ===
4:校验 docs/features/<version>/Fddd-*/ 三件套：
22:ROOT = pathlib.Path(__file__).resolve().parent.parent
128:def discover_features(root: pathlib.Path) -> tuple[dict, list[str]]:
131:    features_dir = root /
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:24:21Z

Important: `check_doc_links.py` scans **all** of `docs/**.md` and does not exclude `docs/reviews/`. So the new report's relative links will be gate-checked. That's a real constraint for the plan.

# Work Plan — F007 Design Documentation Review (Round 1, full-scan)

## 0. Objective & Hard Boundaries

**Deliverable:** exactly one new file — `docs/reviews/CURRENT-doc-F007.md` (Chinese body, review-convergence frontmatter schema), containing a first-round full-scan document review of F007.

**Out of scope (do not do):**
- No edits to any F007 artifact, ADR, PRD, architecture, CLAUDE.md, BACKLOG.md, or `docs/reviews/CURRENT-doc.md`
- No `FIX-log.md` creation (that file belongs to the fix side, not the reviewer)
- No fixes, no `git add`/`commit`/`push`
- No `RETROSPECTIVE.md` write-back (that happens only at closure; this loop stays open)
- No setting `stop_condition_met: true`; no status other than `open` on any finding
- No deletion of any file

**Verified facts this plan rests on** (already confirmed, do not re-verify):
- Worktree clean at `main@ab30da9`; `git status --porcelain` empty
- `docs/reviews/CURRENT-doc-F007.md` is gitignored by `.gitignore:39` (`docs/reviews/*`), confirmed via `git check-ignore -v`
- `docs/reviews/CURRENT-doc.md` = active, unclosed F003 loop, 22 findings all `open` — **read-only, untouched**
- `tools/check_doc_links.py` scans all `docs/**/*.md` **including `docs/reviews/`** (excludes only `conversations/`, `.sisyphus`, `docs/research/`)
- `tools/validate_spec_lifecycle.py` scans only `docs/features/<ver>/Fddd-*/` + BACKLOG — unaffected by the report
- Fast gates measured: `validate_spec_lifecycle.py` 0.11s, `check_doc_links.py` 0.11s
- `tools/verify.py` chains 6 steps ending in pytest+ruff; F003 round-1 recorded it as unfinished at 300s

---

## 1. Baseline Declaration (skill §0) — Step 1, ~2 min

**Action:** record baseline before any reading, and re-check it at report-write time.

```bash
git rev-parse --abbrev-ref HEAD && git rev-parse --short HEAD && git status --porcelain
```

**Record into the report:** `main@ab30da9`, worktree clean, date `2026-09-16`.

**Dirty-worktree protocol (skill §0, required by task even though currently clean):**
1. If `git status --porcelain` is non-empty at any checkpoint, **do not touch, stage, stash, or revert** anything.
2. Classify each dirty path: (a) inside F007 review target set → the reviewed content is moving under the review; (b) elsewhere → foreign to this loop.
3. For case (a): stop, re-declare baseline with the new HEAD/dirty file list, and state in the report's 基线与范围 section that findings are pinned to working-tree content, not to `ab30da9`. Re-read the changed artifact before citing line numbers.
4. For case (b): record the foreign paths verbatim in the report's baseline section as "本会话未改动，归属待确认", and proceed. Never attribute them to this review.
5. If HEAD drifts mid-review (re-check before writing), abort line-number citation and re-run Step 3 evidence collection against the new HEAD.

**Success criterion:** report frontmatter/body carries branch + short SHA + worktree state, and either "clean" or an explicit foreign-change list.

---

## 2. Governing Conventions Extraction — Step 2, ~5 min (already largely done)

Conventions binding this review (re-read only if not already in context):

| Source | Binding rule for this review |
|---|---|
| `docs/features/README.md` | spec 9 fixed sections / design 11 / tasks 6; AC format + unique `AC-xxx` + real requirement ID reference; `Q-xxx`/`DQ-xxx` checkbox or lone `无`; status only in spec frontmatter; `gate_version: 1` obligations; Review Checklist (9 items) |
| `docs/SOP.md` | 7 inviolable principles (§0); status machine §2; review doc lifecycle §3 (reviewer-only deletion); machine-boundary evidence rules §3; file limits |
| `CLAUDE.md` | active-feature index must list F007; doc ownership map; data/AI/live-trading red lines |
| `~/.config/opencode/skills/review-convergence` | report schema, severity semantics, first-round full-scan, minimum-2-rounds, no closure in round 1 |
| `.sdd.json` | `verify` = `.venv/bin/python tools/verify.py`; gates G1/G4 on |

**Bounded checklist (skill §1 — walk it once, then stop; do not review until no opinions remain):**

1. **Structure compliance** — spec 9 / design 11 / tasks 6 top-level headings present, unrenumbered; Q/DQ form; frontmatter required keys.
2. **Internal consistency** — spec ↔ design ↔ tasks: requirement IDs, state machine, verdict vocabulary, directory/path naming, error codes.
3. **Cross-document consistency** — F007 vs PRD FR3/FR7, architecture §2.1/§4.0/§4.2/§4.2.1/§4.4.1/§4.5, ADR-0003/0005/0006/0007, and bidirectional declarations with F002/F003/F004/F008.
4. **Gate effectiveness (teeth)** — can each AC/TR/NFR actually prove its claimed conclusion, and would a mutation make it red? Flag "looks like an assertion, proves nothing".
5. **Task executability** — ordering, dependency DAG, no-inbound-edge tasks, test-before-implementation inversions, `[P]` legality, `[TEST]` group presence per design.md's dated pre-development constraint.
6. **Index consistency** — CLAUDE.md active list, `docs/README.md`, `BACKLOG.md` row + status match with spec frontmatter.

**Severity policy:** Critical/High block convergence; Medium/Low record only. Round 1 = record only; **no fixes, no adjudication**.

---

## 3. Evidence Collection — PARALLELIZABLE (Step 3, ~15 min wall-clock)

Launch **5 independent read-only explore agents in a single message** (all `run_in_background=true`), since no lane depends on another. Each returns findings with precise `file:line` citations and is instructed: *read-only, no edits, cite line numbers, do not propose implementation beyond a one-line review recommendation*.

| Lane | Scope | Primary checklist items |
|---|---|---|
| **A — Structure & lifecycle** | F007 spec/design/tasks; `docs/features/README.md`; `docs/features/TEMPLATE/*`; frontmatter keys across all three | 1, 6 |
| **B — Internal tri-artifact consistency** | F007 spec ↔ design ↔ tasks: FR/DR/TR/IR/UX/NFR ↔ AC ↔ T-task coverage matrix; state machine vs §5 Runtime; verdict vocabulary (`PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE/dead/promising`); error codes; directory layout | 2 |
| **C — Upstream contracts** | PRD FR3/FR7 (`docs/alphamill-prd.md:166-255`), architecture §2.1/§4.0/§4.2/§4.2.1/§4.4.1/§4.5, ADR-0003/0005/0006/0007 | 3 |
| **D — Peer-feature contracts** | F002/F003/F004/F008 spec+design: bidirectional upstream/downstream declarations, `related_features` symmetry, contract field drift | 3 |
| **E — Gate teeth & task DAG** | AC-001..008 provability; §7 测试策略 vs design §8 mapping table; tasks T001-T024 ordering/DAG/`[P]`/`[TEST]` group; SOP §0 7 principles vs F007 claims | 4, 5 |

**Reviewer's own independent pass (not delegated):** I read all three F007 artifacts directly (already done this session) so agent output is cross-checked, not trusted blindly. Skill §8 requires evidence be independently verifiable.

**Resource budget (skill §2):** each lane ≤5 tool calls, ≤800 tokens output. Overrun ⇒ narrow scope, do not deepen.

**Known candidate findings to verify, not assume** (surfaced during planning; each must be re-confirmed with line citations before entering the report):
- `related_features` asymmetry: spec `[F002, F003, F004]` vs design/tasks `[F002, F004]` (`spec.md:7` vs `design.md:5`, `tasks.md:5`)
- F003's finding F003-D014 claims F007 does not declare F003 upstream, but `spec.md:22-23` does mention F003 — cross-loop contradiction needing adjudication evidence either way
- `design.md:17-20` dated 2026-09-16 pre-development constraint mandates a `[TEST]` group in `tasks.md`; `tasks.md` §3 has no `### [TEST]` group
- F008 is absent from all three `related_features` lists although F007 depends on universe/calendar artifacts (`spec.md` IR-002, DR-001)
- `updated: 2026-09-13` in all three frontmatters vs the 2026-09-16 constraint added to design.md

---

## 4. Two-Channel Triage (skill §3) — Step 4, ~10 min

Split agent output into **two separate channels before writing**, then merge into one issue table with a `category` column:

- **Correctness channel** (`category: correctness` / `test-coverage`) — contradictions, contract drift, unprovable gates, DAG errors, missing PIT/embargo semantics. Critical/High here **block** convergence.
- **Quality channel** (`category: quality`) — naming, duplication, readability, redundant prose. **Never blocking** in round 1.

Per finding, assign (skill §4):
- `root_cause`: `root-cause` | `symptom-patch` — answerable by "can a regression test lock this so a silent revert turns red?"
- `origin`: `original-coding` | `fix-regression` | `spec-drift` | `process-gap`
- Second classification: product defect vs. **unexecuted upstream task**. If the latter and a `tasks.md` entry exists → `status: tracked` + `tracked_task`; if none exists → still `open` in round 1 with a note that closure requires a task entry with AC (I do not create it — that is a fix-side action).
- `pattern_tag`: reuse existing repo tags where they genuinely apply (`spec-internal-contradiction`, `cross-feature-contract-drift`, `gate-without-teeth`, `spec-tasks-traceability-gap`, `task-graph-order-contradiction`, `deferred-work-without-carrier`, `unfilled-template-placeholder`); empty if no reusable pattern. Do not invent tags to fill the field.

**ID scheme:** `F007-D001`, `F007-D002`, … — stable across rounds, mirrors the existing `F003-Dxxx` convention. Never renumber in later rounds.

---

## 5. TDD-Oriented Planning: Regression-Test Proposals

This is a document review, so the TDD discipline applies as **"every finding must name the gate that would have caught it"** (skill §6: a finding is only closable once fixed as a failing-gate test that goes red→green).

For each finding, `regression_test` must be filled with one of:

| Form | When | Example |
|---|---|---|
| `proposed:tools/check_doc_consistency.py::test_<name>` | Cross-document contract drift, mechanically checkable | `test_related_features_symmetric` |
| `proposed:tools/validate_spec_lifecycle.py::test_<name>` | Structure/lifecycle rule the existing gate should enforce but doesn't | `test_test_group_required` |
| `proposed:tools/check_task_dag.py::test_<name>` | Task ordering / DAG | `test_no_forward_or_missing_edges` |
| `existing:tools/check_doc_links.py` | Already covered by a live gate | link integrity |
| `manual-review-only: <reason>` | Genuinely semantic, not mechanizable | e.g. "AC wording proves nothing" judgments |

Rules:
- `proposed:` prefix is mandatory for tests that do not exist yet — never write a bare path implying an existing test.
- Follow the F003 report's precedent so both loops aggregate consistently.
- **Mutation-thinking requirement:** for each `proposed:` test, the `suggested_fix` must be specific enough that a fix-side implementer can make the test red before the doc fix and green after. If I cannot state that red→green transition, the finding is downgraded to `manual-review-only` and I say so explicitly rather than pretending it is mechanizable.
- I do **not** create any of these test files. Round 1 is record-only.

---

## 6. Report Generation — Step 6, ~20 min

**Target:** `docs/reviews/CURRENT-doc-F007.md` (new file, Chinese body).

### 6.1 Frontmatter (exact schema from skill §8)

```yaml
---
report_type: doc-review
feature: F007
round: 1
date: 2026-09-16
prior_report: none
scope: full-scan
stop_condition_met: false
severity_counts: {critical: N, high: N, medium: N, low: N}
issues:
  - id: F007-D001
    title: "..."
    severity: high|medium|low|critical
    category: correctness|quality|test-coverage
    root_cause: root-cause|symptom-patch
    origin: original-coding|spec-drift|process-gap|fix-regression
    pattern_tag: "..."          # or ""
    status: open                 # round 1: open only
    tracked_task: ""
    fix_summary: ""              # empty — not fixed
    regression_test: "proposed:..."
    suggested_fix: "..."         # mandatory, one line, review recommendation only
    disposition_reason: ""
    location: "path:line[,line]"
    first_seen_round: 1
    resolved_round: ""
---
```

`feature: F007` is what makes the non-canonical filename machine-associable — it is a schema field, so nothing is lost by the rename.

### 6.2 Body sections (Chinese, mirroring the F003 report so both aggregate identically)

1. `# F007 文档检视 · Round 1（full-scan）`
2. `## 结论先行` — counts, the 2-3 dominant failure clusters, explicit `stop_condition_met: false` + "本轮不修复、不裁决，等待修复方 FIX-log.md 声明"
3. `## 基线与范围` — `main@ab30da9`, worktree state, reviewed artifact list, related-contract list, `scope: full-scan`, `prior_report: none`, **explicit note on the filename deviation**: canonical `CURRENT-doc.md` is occupied by the open F003 loop; this loop uses `CURRENT-doc-F007.md` per skill §8's parallel-`CURRENT-*` allowance; both gitignored by `.gitignore:39`
4. `## 检视门槛与证据` — the 6-item bounded checklist, severity policy, evidence standard (every finding line-cited), and the machine-gate results from Step 7
5. `## Findings` — **single unified table, Chinese column headers**, no simplified variant:

   `| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |`

   Empty cells use `—`. Every row must have a non-empty 标题 and 修复建议.
6. `## 裁决记录` — present but stating `无（Round 1 未产生裁决）`, so the section exists for round 2+
7. `## 下一步` — fix side writes `docs/reviews/FIX-log.md` with the 3-part evidence (findings / commits / regression_tests / gate); then round 2 `diff-only`; reviewer-only deletion at closure

### 6.3 Link-safety constraint (critical, easy to miss)

`check_doc_links.py` **does scan `docs/reviews/`**. Therefore:
- Every relative Markdown link in the new report must resolve from `docs/reviews/`.
- **Mitigation: use plain inline-code paths (`` `docs/features/0.2/F007-evaluation-gates/spec.md:65` ``), not Markdown links.** This is exactly what the F003 report does — zero link risk, and it is why that report passes the gate today.

---

## 7. Document Validation — Step 7, ~2 min

Run after writing, record verbatim output in the report's 证据 section:

```bash
.venv/bin/python tools/validate_spec_lifecycle.py    # ~0.11s — must stay exit 0
.venv/bin/python tools/check_doc_links.py            # ~0.11s — must stay exit 0 (new file IS scanned)
git check-ignore -v docs/reviews/CURRENT-doc-F007.md # must print .gitignore:39
git status --porcelain                                # must be EMPTY (report is ignored)
```

**`tools/verify.py` policy (per your instruction):** attempt it with a bounded timeout (300s). If it does not complete, record honestly:

> `tools/verify.py`：前四道文档/密钥门禁通过，pytest 阶段在 300 秒内未完成，**本轮不宣称统一门禁全绿**。

Never claim green on a timeout. This matches the F003 report's precedent and SOP §1.

**Gate-teeth note:** the two fast gates passing proves only "structure parses", not "contracts are correct" — the report must say so, because "门禁能跑通 ≠ 门禁抓得住错" is precisely what several findings will be about.

---

## 8. Atomic Commit Strategy

**This round produces ZERO commits.** That is the correct atomic strategy here, and it is deliberate, not an omission:

1. The only artifact produced — `docs/reviews/CURRENT-doc-F007.md` — is gitignored by `.gitignore:39` (verified). It is a local process draft by design (skill §8, SOP §3, CLAUDE.md).
2. Skill §8 states review files **never** enter git history; the curated `RETROSPECTIVE.md` write-back is the only thing that is ever committed — and that happens **only at loop closure**, which this task explicitly excludes.
3. `git status --porcelain` must remain **empty** after the report is written. A non-empty status is a bug in the execution, not a commit opportunity.
4. **Guard:** never run `git add -A`/`git add .` during this loop. The gitignore protects the file, but the habit is the failure mode the skill warns about.

**Commit strategy for the *downstream* fix round (documented here so the fix side inherits it, not executed now):**
- One finding → one commit (skill §6), enabling bisect/revert; batching N findings into one large commit is the documented anti-pattern.
- Each commit pairs the doc fix with its regression test (the `proposed:` gate made real), so the test goes red before and green after.
- Per-commit: run only that finding's targeted gate (sub-second). Full `verify.py` + CI: **once per round at round end**, not per commit.
- The fix side declares in `docs/reviews/FIX-log.md` (append-only, its own file) with the mandatory 3-part evidence: `findings` / `commits` (short SHAs, one per finding) / `regression_tests` / `gate` (command + result + timestamp). The reviewer independently verifies hashes and re-runs gates before flipping any `status`.

---

## 9. Success Criteria (all must hold)

1. `docs/reviews/CURRENT-doc-F007.md` exists, frontmatter parses as valid YAML, contains `feature: F007`, `round: 1`, `scope: full-scan`, `stop_condition_met: false`.
2. Every finding has: unique `F007-Dxxx` id, non-empty `title`, `severity`, `category`, `root_cause`, `origin`, `status: open`, non-empty `suggested_fix`, non-empty `regression_test` (with `proposed:`/`existing:`/`manual-review-only:` prefix), `location` with `file:line`, `first_seen_round: 1`, empty `fix_summary`/`resolved_round`.
3. `severity_counts` in frontmatter equals the actual per-severity row count in the Findings table (arithmetic verified, not assumed).
4. Findings table uses Chinese headers and the single unified 13-column format; no simplified variant; `—` for empty cells.
5. All 6 bounded-checklist items are explicitly covered in the report (each either produced findings or is stated as passing).
6. `validate_spec_lifecycle.py` and `check_doc_links.py` both exit 0 **after** the file is written; results quoted verbatim.
7. `git status --porcelain` is empty; `git check-ignore -v` confirms `.gitignore:39` covers the new file.
8. `docs/reviews/CURRENT-doc.md` is **byte-identical** to its pre-review state (verify with `md5sum` before and after).
9. `docs/reviews/RETROSPECTIVE.md`, `BACKLOG.md`, `CLAUDE.md`, and all F007 artifacts are unmodified.
10. No `FIX-log.md` created; no commit, push, or closure; `stop_condition_met` stays `false`.
11. `verify.py` is either recorded green or recorded as timed-out — never claimed green on timeout.

---

## 10. Execution Sequence (bounded, ~55 min total)

| # | Step | Parallel? | Est. |
|---|---|---|---|
| 1 | Baseline declaration + `md5sum docs/reviews/CURRENT-doc.md` (pre-state snapshot) | no | 2 min |
| 2 | Conventions extraction (mostly cached) | no | 5 min |
| 3 | Launch 5 explore lanes A–E in one message | **yes** | 15 min |
| 4 | Collect lanes, cross-check against my own read, two-channel triage + classification | no | 10 min |
| 5 | Assign regression-test proposals with red→green reasoning | no | 5 min |
| 6 | Write `docs/reviews/CURRENT-doc-F007.md` | no | 20 min |
| 7 | Run fast gates + gitignore + status + md5sum re-check | no | 2 min |
| 8 | Report to user: counts, dominant clusters, next action (fix side writes FIX-log.md) | no | 1 min |

**Stop condition for this task:** report written, validation clean, loop left explicitly **open**. Round 2 (`diff-only`) is a separate future task after the fix side declares.

---

**Next action (under 2 min):** Approve this plan and I will start with Step 1 — capture the baseline and the `md5sum` guard on the F003 report before any agent fans out.
