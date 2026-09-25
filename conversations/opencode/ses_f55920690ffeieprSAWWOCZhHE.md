---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f55920690ffeieprSAWWOCZhHE"
title: "Plan F003 document review (@plan subagent)"
project: "/home/georg/projects/alphamill"
model: "claude-opus-5"
created_at: "2026-09-16T13:35:29Z"
updated_at: "2026-09-16T13:42:02Z"
tokens_input: 20
tokens_output: 22809
cost: 0.0
parent_id: "ses_f5599e715ffe8GLbGgDGUSyCFc"
---

# Plan F003 document review (@plan subagent)

## user · 2026-09-16T13:35:29Z

TASK: Produce a concise execution plan for a first-round full review of AlphaMill feature F003's completed requirements/design documentation and creation of the repository review artifact. EXPECTED OUTCOME: A bounded checklist and ordered work breakdown covering project conventions, spec/design/tasks cross-consistency, requirement-to-acceptance-to-task traceability, architecture/data/error/security/test feasibility, severity classification, and report verification. REQUIRED TOOLS: Read-only repository inspection only; no edits. MUST DO: Respect review-convergence Round 1 full-scan semantics and fixed CURRENT-doc.md report format; account for baseline main@a333394; include concrete evidence expectations and validation commands inferred from project files once read. MUST NOT DO: Do not edit files, commit, push, or invent findings without evidence. CONTEXT: Repo /home/georg/projects/alphamill; F003 path docs/features/0.2/F003-alphagen-vendor; project instructions in CLAUDE.md; user explicitly requests a comprehensive reviewer-perspective review document in Chinese.

Additional requirements for this planning request:
- Answer in English.
- Write the plan in English.
- Plan well for ultrawork execution.
- Include a clear atomic commit strategy.
- Use TDD-oriented planning.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T13:35:29Z

- **tool**: `bash({"command": "git -C /home/georg/projects/alphamill log --oneline -5 && git -C /home/georg/projects/alphamill status --porcelain | head -30 && git -C /home/georg/projects/alphamill rev-parse --short HEAD && git -C /home/georg/projects/alphamill branch --show-current"})`
- **tool**: `bash({"command": "ls -la /home/georg/projects/alphamill && ls -R /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor 2>/dev/null"})`

I'll gather context on the repo conventions and F003 docs before planning.

  <details><summary>tool output</summary>

  ```text
a333394 docs(sdd): [TEST] 组入驻 tasks 模板 + F003/F007/F008 设计补开发前置约束（T3 开工门禁）
c877587 docs(reviews): 循环 12 R002/R004 关闭——T013 执行机取证回写（spec §6 第二轮）
2d5eace docs(f004): T013 回写 spec §6 第二轮执行机容器证据（三构建/import/容器套件 7 passed）；状态收口 review → done；BACKLOG 移出
92e8276 chore(sdd): add project adapter (.sdd.json)
affa034 docs(reviews): 循环 12 回写 CI 最终门禁结果（7fc67c7 / af8bdce 双绿）
a333394
main


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 564
drwxr-xr-x 23 georg georg   4096 Sep 15 22:00 .
drwxr-xr-x 13 georg georg   4096 Sep 16 21:20 ..
drwxr-xr-x  2 georg georg   4096 Sep 16 21:35 .code-review-graph
lrwxrwxrwx  1 georg georg     62 Sep 13 12:30 .codegraph -> /home/georg/.omo/codegraph/projects/alphamill-9c04b030e83dacf2
-rw-r--r--  1 georg georg    312 Sep 15 22:00 .dockerignore
drwxr-xr-x 10 georg georg   4096 Sep 16 21:35 .git
drwxr-xr-x  3 georg georg   4096 Sep 10 00:25 .github
-rw-r--r--  1 georg georg   1222 Sep 14 01:49 .gitignore
drwxr-xr-x  3 georg georg   4096 Sep 13 12:35 .omo
drwxr-xr-x  3 georg georg   4096 Sep 10 23:06 .pytest_cache
drwxr-xr-x  3 georg georg   4096 Sep 10 23:07 .ruff_cache
-rw-r--r--  1 georg georg    343 Sep 15 22:00 .sdd.json
drwxr-xr-x  6 georg georg   4096 Sep 13 13:45 .venv
-rw-r-
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:35:50Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/.sdd.json"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/.gitignore"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && wc -l docs/features/0.2/F003-alphagen-vendor/*.md && ls docs/ docs/reviews 2>/dev/null && ls docs/features/0.2/"})`


> [reasoning] Confirmed the baseline is clean at main@a333394, so now I want to check CLAUDE.md, .sdd.json, and the F003 docs, along with docs/reviews and .gitignore to get full context.

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
<path>/home/georg/projects/alphamill/.sdd.json</path>
<type>file</type>
<content>
1: {
2:   "$comment": "SDD Flow (sdd-flow skill) 项目适配。缺省字段自动探测；规范见 ~/.config/opencode/skills/sdd-flow/references/project-adapter.md",
3:   "verify": ".venv/bin/python tools/verify.py",
4:   "test": ".venv/bin/python -m pytest -q",
5:   "gates": { "G1": true, "G2": false, "G3": false, "G4": true },
6:   "quick_max_files": 3
7: }

(End of file - total 7 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/.gitignore</path>
<type>file</type>
<content>
1: __pycache__/
2: *.py[cod]
3: .pytest_cache/
4: .ruff_cache/
5: .mypy_cache/
6: .coverage
7: htmlcov/
8: .venv/
9: venv/
10: dist/
11: build/
12: *.egg-info/
13: .idea/
14: .vscode/
15: .DS_Store
16: 
17: # 本机 AI 工具本地授权配置：含本机用户名路径与本地授权，不可移植
18: .claude/settings.local.json
19: 
20: # 编辑器本地历史
21: .history/
22: 
23: # 本机代理运行续接状态
24: .sisyphus/
25: 
26: # 本机 OpenCode 运行状态（含会话转录，严禁入库——密钥扫描门禁的原因之一）
27: .omo/
28: 
29: # 仿真/实验产生的数据与输出
30: data/raw/
31: data/processed/
32: results/
33: artifacts/
34: *.parquet
35: *.feather
36: 
37: # 本地-only 文档（保留在磁盘，不纳入 git）
38: docs/research/
39: docs/reviews/*
40: # ...例外：curated 摘要入库
41: !docs/reviews/RETROSPECTIVE.md
42: 
43: # 本地运行时密钥（模板为 deployment/.env.example，真实凭据人工搬运不进 g
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
252 docs/features/0.2/F003-alphagen-vendor/design.md
  345 docs/features/0.2/F003-alphagen-vendor/spec.md
  105 docs/features/0.2/F003-alphagen-vendor/tasks.md
  702 total
docs/:
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

docs/reviews:
RETROSPECTIVE.md
F002-data-bridge
F003-alphagen-vendor
F004-kronos-inference-runtime
F007-evaluation-gates
F008-universe-expansion


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:36:01Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls -la docs/reviews/F003-alphagen-vendor docs/reviews/F007-evaluation-gates && ls docs/features/TEMPLATE docs/features/0.2 && wc -l docs/SOP.md docs/features/README.md docs/reviews/RETROSPECTIVE.md tools/verify.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/SOP.md"})`


> [reasoning] I should check the existing docs/reviews structure, SOP.md, the features README status rules, the tasks template, and briefly the F003 docs themselves, along with any prior review artifacts for F003.

  <details><summary>tool output</summary>

  ```text
ls: cannot access 'docs/reviews/F003-alphagen-vendor': No such file or directory
ls: cannot access 'docs/reviews/F007-evaluation-gates': No such file or directory


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
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

## assistant · 2026-09-16T13:36:09Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`


> [reasoning] I should just read the F003 spec, design, and tasks files along with features/README, the verify.py gates, and RETROSPECTIVE structure directly since they're small—about 702 lines total.

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

## assistant · 2026-09-16T13:36:18Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`


> [reasoning] I should look at tasks.md, BACKLOG.md, and RETROSPECTIVE.md's structure, plus tools/verify.py and the TEMPLATE tasks, since the design references a [TEST] group requirement added at a333394.

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
<path>/home/georg/projects/alphamill/docs/features/TEMPLATE/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: Fxxx
4: version: "0.x"
5: related_features: []
6: topics: []
7: doc_kind: tasks
8: created: YYYY-MM-DD
9: updated: YYYY-MM-DD
10: ---
11: 
12: # Fxxx：功能名称 - 任务
13: 
14: > Owner: TBD | Spec: `spec.md` | Design: `design.md`
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
25: 统一任务格式：
26: 
27: ```markdown
28: - [ ] T001 [P] (`US-001`, `FR-001`, `AC-001`): <一个可验证动作> — verify: `path/to/test.ts`
29: ```
30: 
31: ## 1. 前置条件
32: 
33: - [ ] T001 (`DQ-001`): 关闭所有阻塞性 spec/de
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

## assistant · 2026-09-16T13:36:26Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls tools/ && sed -n 1,80p tools/verify.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && head -60 docs/reviews/RETROSPECTIVE.md && echo ---- && grep -n \"report_type\" docs/reviews/RETROSPECTIVE.md | head -20 && echo ---- && grep -c \"\" docs/reviews/RETROSPECTIVE.md"})`


> [reasoning] I notice tasks.md is missing the [TEST] group that the latest commit required for design front-load constraints, while design.md does have that note — I should flag this as something to verify rather than assert as a conclusion yet. Next I want to check tools/verify.py.

  <details><summary>tool output</summary>

  ```text
__pycache__
apply_migrations.py
check_dep_pins.py
check_doc_links.py
check_secrets.py
f001_backfill_config.py
f001_backfill_report.py
validate_spec_lifecycle.py
verify.py
#!/usr/bin/env python3
"""本地统一验证入口（公开验证唯一入口）。

按固定顺序运行：规格生命周期校验 → 文档相对链接检查 → dev 依赖 pin 范围检查
→ 密钥模式扫描 → pytest → ruff check → ruff format check。任一步失败即记录，
全部跑完后汇总返回非零（不短路）。

各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
统一指向本入口。

用法：
    python3 tools/verify.py
退出码 0 表示全部通过；非 0 时打印失败步骤。
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(cmd: list[str], label: str) -> bool:
    print(f"\n== {label} ==")
    proc = subprocess.run(cmd, cwd=ROOT)
    if proc.returncode != 0:
        print(f"FAILED: {label}")
        return F
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
# RETROSPECTIVE —— 检视复盘

本文件由 review-convergence skill 维护，记录每轮检视发现的缺陷与过程教训。
`docs/reviews/` 下其它文件本地-only（见 `.gitignore`）。

## 循环 1：全项目文档检视（项目开工前全量）

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 | 基线：1bd8c4d → 终基线 7969a97（修复轮 7 个分批提交）
- 检视人：Sisyphus；修复方：项目所有者（Georg/qiaozhi li）
- 范围：docs/ 全部 17 份入库文件 + CLAUDE.md/README.md/BACKLOG.md + 三路独立取证（检视人通读 + explore agent 代码区实测 + Oracle agent 战略评审）
- 结论：首轮 2 Critical / 8 High / 10 Medium / 4 Low 共 24 条；修复轮全数处理并自查发现 fix-regression N1 一条（PRD 与架构成本口径矛盾，当轮修复）；round-2 diff-only 复核逐条验证通过，verify.py 六步全绿 ×3，检视人独立变异验证两道新门禁（死链注入→红→还原→绿；pin 复现 C001 原始故障→红→还原→绿）。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D001 | 组合构建层缺失，协同池产物无部署路径 | 严
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:36:38Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"def \\|ERROR\\|错误\\|必须\" tools/validate_spec_lifecycle.py | head -60 && wc -l tools/validate_spec_lifecycle.py"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && sed -n 400,519p docs/reviews/RETROSPECTIVE.md"})`


> [reasoning] I want to check a recent doc-review cycle in RETROSPECTIVE for F007/F008 style, look at the cycle 12 entry format, and understand existing conventions for CURRENT-doc.md. I'll also glance at validate_spec_lifecycle.py to see what's already machine-checked so the review can focus on semantic gaps instead.

  <details><summary>tool output</summary>

  ```text
63:def parse_frontmatter(text: str) -> dict | None:
76:def strip_code_blocks(text: str) -> str:
80:def top_level_sections(text: str) -> list[str]:
84:def section_body(text: str, title: str) -> str | None:
103:def requirement_ids(text: str) -> set[str]:
107:def question_section_issues(body: str | None) -> list[str]:
122:def open_questions(body: str | None) -> int:
128:def discover_features(root: pathlib.Path) -> tuple[dict, list[str]]:
156:def check_feature(feat: dict, root: pathlib.Path, errors: list[str]):
159:    def tag(msg: str) -> None:
249:def check_backlog(root: pathlib.Path, feats: dict, errors: list[str]):
289:def verify_repo(root: pathlib.Path = ROOT) -> tuple[bool, list[str]]:
303:def main() -> int:
315 tools/validate_spec_lifecycle.py


Incremental: 0 files updated, 0 nodes, 0 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
### 循环 10 裁决分布与建议命中率

- fixed 25 / partial 1 / rejected 0 / tracked 1 / carried-forward 0（共 27 条）。
- 唯一 partial 为 R2-01：FIX-log 补齐部分接纳并核对通过；「一 finding 一 commit」部分不接纳，
  理由「起始工作树无可还原的 commit 历史」经核对成立（检视方第 2 轮亲见起始态为未提交工作树、
  HEAD 仍是 569359b）。剩余载体=后续轮次必须按 finding 拆提交，第 3 轮已按此执行（5 条修复
  拆成 5 个提交）。
- 建议命中率约 93%（25/27 实质采纳 `suggested_fix`）。两处偏差都有价值：
  C003 的建议是「判 removed + 是否移出 partitions 交 owner 裁决」，实现直接取了"移出"，
  由此产生 R2-02；Q001 的建议被字面执行后产生 R3-01。**教训：检视建议不能只写"做什么"，
  涉及语义变更时要同时写清"这么做会打开哪个新口子"**，否则建议本身就是下一条 finding 的来源。
- 全接纳率 96% 需警惕"检视在凑数"的反向信号；本循环的对冲证据是：8 条为修改引入（首轮
  物理上不存在）、1 条第 2 轮被误报已修复后在第 3 轮才真正关闭、1 条转 tracked 而非硬关，
  说明发现具备实质性而非形式化。

---

## 循环 11：F004 Kronos 真实推理运行时设计检视

- report_type: doc-review | round: 1（full-scan）→ 2（修复覆盖 52%，一次性 full-scan）→ 3/4（diff-only）| 状态: 闭环
- 日期：2026-09-14～2
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:36:48Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py", "offset": 128, "limit": 130})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls docs/features/0.2/*/ && ls tests/unit tests/integration | head -40 && ls src/alphamill/factor_factory 2>/dev/null"})`


> [reasoning] I should confirm F007/F008 specs and related architecture/PRD sections exist for cross-feature consistency, though that's part of the actual review rather than planning. I also want to check the docs/features/0.2/ directory and what validate_spec_lifecycle.py mechanically covers, so I know what the review should focus on semantically versus what's already gated automatically—along with whether there's a .venv python setup to use.

I notice design.md requires tasks.md to include a [TEST] group, and F003's tasks.md appears to be missing one—that's a potential finding, but I shouldn't jump to conclusions; the plan should just verify it properly. I'll also look at check_feature to understand what's mechanically covered already.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py</path>
<type>file</type>
<content>
128: def discover_features(root: pathlib.Path) -> tuple[dict, list[str]]:
129:     feats: dict[str, dict] = {}
130:     errors: list[str] = []
131:     features_dir = root / "docs" / "features"
132:     if not features_dir.is_dir():
133:         return feats, errors
134:     for ver in features_dir.iterdir():
135:         if not ver.is_dir() or ver.name in ("TEMPLATE", "releases"):
136:             continue
137:         for f in ver.iterdir():
138:             if not f.is_dir() or not re.match(r"^F\d{3}-", f.name):
139:                 continue
140:             files = {n: f / n for n in ("spec.md", "design.md", "tasks.md")}
141:             missing = [n for n, p in files.items() if not
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

docs/features/0.2/F007-evaluation-gates/:
design.md
spec.md
tasks.md

docs/features/0.2/F008-universe-expansion/:
design.md
spec.md
tasks.md
tests/integration:
__pycache__
conftest.py
test_f001_collector_smoke.py
test_f001_dryrun_monitoring.py
test_f001_kronos_smoke.py
test_f001_row_reconciliation.py
test_f002_export_reconcile.py
test_f002_reader.py
test_f002_revision.py
test_f002_schedule_backup.py
test_f004_real_profile.py

tests/unit:
__pycache__
test_apply_migrations.py
test_backup_nas_contract.py
test_check_dep_pins.py
test_check_doc_links.py
test_check_secrets.py
test_doc_gat
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T13:37:03Z

- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && ls docs/decisions/ && grep -n \"^### 4.1.1\\|^#### 4.1.1\\|4.1.1\" docs/alphamill-architecture.md | head -5 && grep -n \"7.1\" docs/alphamill-architecture.md | head -5 && ls src/alphamill/data_bridge/ && grep -rn \"def read\" src/alphamill/data_bridge/reader.py 2>/dev/null | head"})`
- **tool**: `bash({"command": "cd /home/georg/projects/alphamill && grep -n \"FR2\\.\\|FR1.5\" docs/alphamill-prd.md | head -20 && echo ---- && grep -n \"status:\" docs/features/0.2/F007-evaluation-gates/spec.md docs/features/0.2/F008-universe-expansion/spec.md && echo ---- && git check-ignore -v docs/reviews/CURRENT-doc.md"})`


> [reasoning] I have enough context now, but I should quickly verify a few anchors reviewers will need — architecture sections, ADR files, and the F002 reader function — to make sure cross-feature contract claims can actually be checked.

  <details><summary>tool output</summary>

  ```text
000-template.md
0001-factor-mining-engine.md
0002-external-dependency-policy.md
0003-validation-gate-non-degradation.md
0004-portfolio-construction.md
0005-presentation-observability.md
0006-evidence-boundary-and-experiment-identity.md
0007-research-snapshot-binding.md
0008-north-star-sustained-profitability.md
194:    │   │   ├── alphagen_adapter.py  # 表达式树/张量 ↔ FactorDef 适配层（§4.1.1；放 vendor 外，见集成文档卫生规则）
272:#### 4.1.1 AlphaGen 适配契约（表达式树/张量世界 ↔ FactorDef pandas 世界）
333:experiment manifest（FR7.1）。
517:            MINE[生成器挖掘<br/>GPU 夜槽 §7.1]
546:产出，研究控制台先行，ADR-0005；Grafana 逐步退守平台观测与告警）。GPU 占用按时段表调度（见 7.1）。
548:### 7.1 机器边界与单卡 GPU 时段调度
__init__.py
__pycache__
cli.py
collector
digest.py
errors.py
export_policy.py
export_summary.py
exporter.py
manifest.py
manifest_validation.py
partitions.py
p
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
143:- **FR1.5 数据质量与扩容**：宇宙扩至 30~50 对前完成缺失、重复、未闭合 K 线和跨周期对账，
153:- **FR2.1 假设注册**：记录经济动机、作用机制、数据依赖、适用状态、持有期、成本敏感性、来源与
155:- **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达式或人工/LLM 中的一种独立后端。
157:- **FR2.3 目标对齐**：奖励或前置筛选同时考虑预测证据、换手、≥30 笔/90 天可达性及成本后收益，
159:- **FR2.4 纯度与能力边界**：因子通过 AST 纯度门；前视、网络访问、隐式全样本统计和未支持的跨 pair
161:- **FR2.5 因子注册表**：保存定义、参数、数据依赖、来源、版本、评测摘要和生命周期；IC/OOS PnL
163:- **FR2.6 探索组合**：AlphaGen 协同池作为可部署 meta-factor 注册；名义产量、有效独立数、来源多样性
----
docs/features/0.2/F007-evaluation-gates/spec.md:5:status: draft
docs/features/0.2/F008-universe-expansion/spec.md:5:status: draft
----
.gitignore:39:docs/reviews/*	docs/reviews/CURRENT-doc.md


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T13:37:18Z


> [reasoning] I've found a clear gap: F003's tasks.md is missing the [TEST] group that the design.md now mandates as of commit a333394, since tasks.md wasn't updated after that design change. I'm also noticing spec §8 Q-001 is marked closed but T001's wording about closing the spec's remaining item still needs checking.

I'll treat these as hypotheses to verify with evidence rather than confirmed findings, then move into producing the plan itself — mandated sections, English, TDD-oriented, atomic commits, waves, categories, skills, and a TODO list wrapped in `<plan>`. Since the actual review deliverable is a local, gitignored Chinese document and Round 1 makes no code changes, the commit strategy should honestly state zero commits this round, with RETROSPECTIVE.md as the only committable artifact at closure. For the TDD angle, I'm treating "test-first" as defining the falsifiable checklist of assertions before doing the actual review reading.

Now I'm laying out Wave 1 as parallel, read-only tasks: extracting baseline conventions from CLAUDE.md, SOP, features/README, and .sdd.json into a constraints scratchpad; running machine-gate checks like verify.py, validate_spec_lifecycle.py, and check_doc_links.py and recording their output; building traceability matrices linking requirements, acceptance criteria, task IDs, and test paths; and verifying upstream citations against the PRD, architecture doc sections, and relevant ADRs.

Wave 2 then builds on that foundation with deep reviews of spec.md, design.md, and tasks.md against their structural requirements — checking scenario coverage, invariants, module boundaries, DAG legality, and verify-command executability — followed by a cross-document consistency pass checking for contract drift across related features and the backlog.

Wave 3 handles severity classification, root-cause/pattern tagging, and suggested fixes for findings, then authors the Chinese-language review doc in the fixed frontmatter/table format. Wave 4 self-verifies the report for format compliance and evidence integrity. I'm mapping which task categories and skills apply to each phase — deep analysis models for review work, quick extraction models for pulling data, and specific skills like review-convergence for the core process.

I'm evaluating other skills for relevance: omitting ci-verify since no CI changes exist this round, omitting git-master and ast-grep as not applicable, but keeping full-output-enforcement for report writing to prevent truncation, and weighing whether sdd-project-scaffold applies given the authoritative structure rules already live in repo docs.

For validation, I'll prefer targeted doc gates over the full verify script since it writes to pytest cache, and I'll confirm the current commit hash, clean git status, and that the review doc is properly gitignored before writing everything up.

The report needs frontmatter with the doc-review type, round 1, full-scan scope, and severity counts, followed by a body with a conclusion-first structure, a fixed Chinese-column table, and a verdict record section — using consistent ID naming like F003-D001 matching the prior cycle's F004-D001 pattern. Round 1 itself creates no commits since CURRENT-doc.md stays gitignored until RETROSPECTIVE.md gets committed at loop closure, so I should still spell out the atomic one-finding-per-commit rule for the eventual fix round to make the plan complete.
<plan>
# F003 Round-1 Full-Scan Documentation Review — Execution Plan

## Context

### User Request Summary
Produce and execute a bounded, reviewer-perspective **Round 1 full-scan review** of AlphaMill feature **F003 (AlphaGen vendor 与可插拔生成器平面)** design documentation (`spec.md` / `design.md` / `tasks.md`), and author the repository review artifact `docs/reviews/CURRENT-doc.md` **in Chinese**, following the `review-convergence` protocol. Read-only: no edits to reviewed files, no commits, no pushes, no invented findings.

### Baseline (declared, verified)
- Branch `main`, HEAD `a333394` (`docs(sdd): [TEST] 组入驻 tasks 模板 + F003/F007/F008 设计补开发前置约束（T3 开工门禁）`)
- Working tree clean (`git status --porcelain` empty at plan time)
- If HEAD drifts or foreign modifications appear mid-review → **re-baseline explicitly** in the report header before continuing (protocol §0)

### Facts established by read-only inspection (no findings asserted yet)
| Fact | Source |
|---|---|
| F003 status `draft`, gate_version `1`, 345/252/105 lines (spec/design/tasks) | `docs/features/0.2/F003-alphagen-vendor/*` |
| Fixed section contracts: spec 9 sections, design 11, tasks 6; AC format + Q/DQ checkbox rules; BACKLOG bidirectional check | `docs/features/README.md`, `tools/validate_spec_lifecycle.py:156-257` |
| Sole verification entry `python3 tools/verify.py`; project adapter prefers `.venv/bin/python tools/verify.py` | `docs/SOP.md:34`, `.sdd.json` |
| `tools/verify.py` runs: spec-lifecycle → doc-links → dep-pins → secrets → pytest(`tests/unit`,`tests/integration`) → ruff check → ruff format | `tools/verify.py:35-56` |
| Machine boundary discipline (dev box no GPU; GPU/integration evidence only on executor `qiaozhi-lt`; dev-box skip ≠ evidence) | `CLAUDE.md:36`, `docs/SOP.md:70-75` |
| 7 non-negotiable project principles (traceable spec, gate non-degradation, no-lookahead, lake-only data, AI authority, live-trading red line, reproducibility) | `docs/SOP.md:19-27` |
| `docs/reviews/*` is gitignored except `RETROSPECTIVE.md`; CURRENT-*/FIX-log are local-only process drafts | `.gitignore:37-41`, verified via `git check-ignore -v` |
| Prior loops 11/12 (F004) established the report table format, pattern_tag vocabulary, and recurring failure modes (`partial-symmetric-fix`, `cross-feature-contract-drift`, `deferred-work-without-carrier`, `test-created-after-implementation`, `task-graph-order-contradiction`) | `docs/reviews/RETROSPECTIVE.md` 循环 11/12 |
| A new repo-wide constraint landed at HEAD: tasks must carry a `[TEST]` journey-acceptance group; F003 `design.md:16-18` states it, `TEMPLATE/tasks.md:57-61` carries it | commit `a333394` |

### Uncertainties (state as assumptions; do not block)
1. **Review depth of upstream docs.** Assumption: upstream PRD/architecture/ADRs are treated as *authoritative and out of scope* — F003 is judged against them; a contradiction is filed against F003 unless the upstream text is demonstrably wrong, in which case it is filed as `spec-drift` with both locations cited.
2. **Whether `python3 tools/verify.py` may be run.** It writes only caches (`.pytest_cache`, `.ruff_cache`) and no tracked files. Assumption: allowed as evidence collection; if cache writes are unacceptable, fall back to the two doc gates only (`validate_spec_lifecycle.py`, `check_doc_links.py`), which are pure readers.
3. **Report language/scope.** Assumption: `CURRENT-doc.md` body and table headers in Chinese (per protocol §8 fixed Chinese column names), frontmatter keys in English (protocol template).
4. **Code review is excluded.** `src/alphamill/factor_factory/` contains only `bench/` + `__init__.py`; F003 has no implementation. This is a pure `doc-review`, so `CURRENT-code.md` is not created.

### TDD orientation for a document review
There is no production code to test, so "test-first" maps to **assertion-first**:
1. Write the *falsifiable checklist* (Wave 1) **before** reading the documents for defects — a bounded assertion set, each assertion phrased so it can come out `pass`/`fail` from cited evidence.
2. Every finding must name the **gate or test that would have caught it** (`regression_test` column) — either an existing gate (`validate_spec_lifecycle.py`, `check_doc_links.py`), a proposed new gate assertion, or `—` with a stated reason why no machine gate is possible.
3. Every finding must carry a **concrete evidence pointer** (`file:line` or command output). No pointer → not a finding, drop it.
4. Where a finding claims an existing gate is blind, prove it by describing the **mutation** that leaves the gate green (mutation evidence is the Round-1 analogue of a red test) — describe it, do not perform it in Round 1 (read-only).

---

## Task Dependency Graph

| Task | Depends On | Reason |
|------|------------|--------|
| Task 1 (Convention & lessons extraction → checklist constraints) | None | Starting point; reads repo governance docs only |
| Task 2 (Machine-gate + baseline evidence capture) | None | Independent read-only command execution |
| Task 3 (Traceability matrix extraction) | None | Mechanical extraction from the three F003 files |
| Task 4 (Upstream citation verification) | None | Independent resolution of every source reference in F003 |
| Task 5 (spec.md deep review) | Task 1, Task 3 | Needs the bounded checklist and the requirement↔AC matrix |
| Task 6 (design.md deep review) | Task 1, Task 4 | Needs checklist + verified upstream contracts (arch §4.1.1/§7.1, F002 reader) |
| Task 7 (tasks.md deep review incl. DAG + `[TEST]` group) | Task 1, Task 3 | Needs checklist + AC↔task matrix to judge coverage/ordering |
| Task 8 (Cross-document & cross-feature consistency) | Task 2, Task 3, Task 4 | Needs gate output, matrices, and resolved upstream refs |
| Task 9 (Finding consolidation, severity/origin/pattern classification) | Task 5, Task 6, Task 7, Task 8 | Consumes all raw findings |
| Task 10 (Author `docs/reviews/CURRENT-doc.md` in Chinese) | Task 9 | Writes the classified finding set into the fixed format |
| Task 11 (Report self-verification / format + evidence audit) | Task 10 | Verifies the artifact produced by Task 10 |

---

## Parallel Execution Graph

```
Wave 1 (start immediately — all read-only, no interdependencies):
├── Task 1: Convention & lessons extraction → checklist constraints
├── Task 2: Baseline + machine-gate evidence capture
├── Task 3: Traceability matrix extraction (FR/DR/TR/IR/NFR ↔ US ↔ AC ↔ T-ID ↔ test path)
└── Task 4: Upstream citation verification (PRD / architecture / ADR / F002 API)

Wave 2 (after Wave 1):
├── Task 5: spec.md deep review            (needs 1, 3)
├── Task 6: design.md deep review          (needs 1, 4)
├── Task 7: tasks.md deep review + DAG     (needs 1, 3)
└── Task 8: Cross-document / cross-feature (needs 2, 3, 4)

Wave 3 (after Wave 2):
└── Task 9: Consolidation + severity/origin/pattern_tag + suggested_fix

Wave 4 (after Wave 3):
└── Task 10: Author CURRENT-doc.md (Chinese, fixed format)

Wave 5 (after Wave 4):
└── Task 11: Report self-verification (format, counts, evidence pointers, no-invention audit)

Critical Path: Task 1 → Task 5/6/7 → Task 9 → Task 10 → Task 11
Estimated Parallel Speedup: ~55% vs sequential (4-wide Wave 1, 4-wide Wave 2)
Estimated wall-clock: Wave 1 ~15 min · Wave 2 ~35 min · Wave 3 ~15 min · Wave 4 ~25 min · Wave 5 ~10 min (~1h40m total)
```

---

## Tasks

### Task 1: Extract project conventions and prior-loop lessons into a bounded checklist

**Description**: Read `CLAUDE.md`, `docs/SOP.md`, `docs/features/README.md`, `docs/README.md`, `.sdd.json`, `.gitignore`, and `docs/reviews/RETROSPECTIVE.md` (loops 10–12 in particular). Emit to scratchpad `checklist.md` containing:
- The **7 non-negotiable principles** (SOP §0) restated as F003-applicable assertions.
- Structural rules: spec 9 / design 11 / tasks 6 fixed sections; AC format `- [ ] **AC-xxx** (\`FR-xxx\`): behavior — tests: \`path\``; Q/DQ checkbox rules; `status` single-source rule; `[P]` legality; `[TEST]` group requirement (design.md:16-18 + TEMPLATE/tasks.md:57-61).
- Machine-boundary evidence rules (SOP §3): executor-only GPU/integration evidence, hostname+device recording, skip≠evidence.
- Prior-loop `pattern_tag` vocabulary to reuse (do **not** invent new tags when an existing one fits).
- **Bounded scope declaration**: the checklist is closed — once every assertion has a verdict, Round 1 scanning stops. No open-ended re-reading.

**Delegation Recommendation**:
- Category: `unspecified-low` — bounded extraction/summarization of known files, no deep reasoning
- Skills: [`review-convergence`] — supplies the round semantics, checklist-first discipline, and pattern_tag taxonomy this task must encode

**Skills Evaluation**:
- INCLUDED `review-convergence`: the protocol *is* the checklist framework (§1 bounded checklist, §8 report format)
- OMITTED `code-review-agent`, `review-changes`, `review-work`: one-shot report generators; `review-convergence` explicitly supersedes them
- OMITTED `programming`, `ast-grep`, `refactor`: no source code is read or changed
- OMITTED `ci-verify`: no changes are pushed in Round 1; CI is the closure gate, not a Round-1 step
- OMITTED `git-master`: baseline commands are two plain read-only `git` calls (Task 2)
- OMITTED `sdd-project-scaffold`: it generates scaffolds; the authoritative structure rules already live in `docs/features/README.md`

**Depends On**: None

**Acceptance Criteria**:
- `checklist.md` exists with ≥6 assertion groups (principles / spec structure / design structure / tasks structure / traceability / evidence discipline), each assertion phrased pass-fail
- Every rule line cites its owner `file:line`
- Prior-loop pattern_tag list present with ≥8 tags copied verbatim from `RETROSPECTIVE.md`

---

### Task 2: Capture baseline and machine-gate evidence

**Description**: Run read-only evidence commands and record verbatim output to scratchpad `gates.md`:
1. `git -C /home/georg/projects/alphamill rev-parse --short HEAD` (expect `a333394`) and `git status --porcelain` (expect clean; any foreign file → stop and report drift)
2. `git check-ignore -v docs/reviews/CURRENT-doc.md` (expect `.gitignore:39`) — confirms the report will never enter git
3. `.venv/bin/python tools/validate_spec_lifecycle.py` — record pass/fail and any F003 messages
4. `.venv/bin/python tools/check_doc_links.py` — record dead-link results
5. `.venv/bin/python tools/verify.py` — full gate run, record the 7-step summary (**assumption**: cache writes acceptable; if not, skip this step and say so explicitly in the report)
6. Record which F003 AC test paths exist today: `ls tests/unit tests/integration` vs the 11 AC `tests:` paths (expected: none exist — F003 is `draft`, which the lifecycle gate permits)

**Delegation Recommendation**:
- Category: `quick` — mechanical command execution and transcription
- Skills: [] — no specialized knowledge needed; commands are fully specified here

**Skills Evaluation**:
- OMITTED `ci-verify`: that skill is about pre-commit/post-push CI confirmation; Round 1 pushes nothing
- OMITTED all others: pure command transcription

**Depends On**: None

**Acceptance Criteria**:
- `gates.md` contains verbatim output (or explicit "not run + reason") for all 6 items
- Baseline line present: `main@a333394`, tree-clean verdict
- Explicit statement of which of the 11 AC test paths exist (with `ls` evidence)

---

### Task 3: Build the traceability matrices

**Description**: Mechanically extract from the three F003 files into scratchpad `traceability.md`:
- **Matrix A — Requirement coverage**: every ID defined in spec §4 (`FR-001..007`, `DR-001..004`, `TR-001..002`, `IR-001..003`, `NFR-001..005`) × the AC(s) referencing it × the task(s) referencing it. Flag: requirements with **no AC**, requirements with **no task**, ACs referencing IDs not defined in §4, tasks referencing IDs not defined anywhere.
- **Matrix B — AC ↔ test path ↔ design §8 mapping**: for each `AC-001..011`, the `tests:` path in spec §6, the row in design §8, and the tasks whose `verify:` names that path. Flag mismatches in layer (unit vs integration) or filename between spec §6 and design §8.
- **Matrix C — User-story coverage**: `US-001/002/003` × their acceptance scenarios × ACs × tasks. Flag any US scenario with no AC/task carrier.
- **Matrix D — Task graph**: all task IDs T001–T036, their declared edges from tasks §4, plus `[P]` markers. Compute: ID continuity, unreachable tasks, cycles, edges referencing nonexistent IDs, `[P]` tasks that also have a declared edge (prohibited by TEMPLATE `tasks.md:73`), and whether textual prerequisites in task bodies match declared edges.

**Delegation Recommendation**:
- Category: `unspecified-low` — deterministic extraction and set comparison; low reasoning, high precision
- Skills: [`review-convergence`] — matrix output must map onto the report's issue fields (`regression_test`, `location`)

**Skills Evaluation**:
- INCLUDED `review-convergence`: keeps the extraction aligned to the finding schema
- OMITTED `data-scientist`: matrices are ≤40 rows; DuckDB/Polars is overkill
- OMITTED `explore-codebase`, `debug-issue`: graph tools target code symbols, not markdown IDs

**Depends On**: None

**Acceptance Criteria**:
- Matrices A–D complete, every cell traceable to a `file:line`
- Explicit gap lists (uncovered requirement IDs / orphan ACs / dangling task refs / DAG anomalies), each with line citation
- Matrix D reports "acyclic: yes/no" and lists any `[P]`+edge violations

---

### Task 4: Verify every upstream citation in F003 resolves

**Description**: For each source reference in `spec.md` §0/§7 and `design.md` §0/§2 — PRD `FR2.1/2.2/2.3/2.4/2.6`, `FR1.5`, goal `G3`, milestone `M2`; architecture §三 / §4.0 / §4.1 / §4.1.1 / §7.1; `alphamill-research-factor-mining.md` §3.1; `alphamill-integration.md` §五; ADR-0001/0002/0003/0007; F001 layout; F002 `data_bridge.reader.read()` + `(dataset, data_version, value_digest)` + `symbol_map` — confirm the target section/API **exists** and **says what F003 claims it says**. Record to scratchpad `citations.md`: reference → resolved `file:line` → verdict `{resolves+accurate | resolves+misstated | dangling}` → one-line quote of the upstream text.

Specific checks with elevated risk (verify, do not presume): ADR-0001's four smoke criteria and L1/L2 degradation predicates vs spec `FR-006`/§5 tier machine; ADR-0002 vendor-hygiene rules vs `FR-002`; architecture §4.1.1 adapter contract vs `FR-004`; architecture §7.1 time-table/VRAM budget vs `NFR-002`; F002 reader's actual signature vs design §2's "only entry point" claim.

**Delegation Recommendation**:
- Category: `deep` — requires reading several large upstream docs and judging semantic fidelity, one deliverable (citation verdict table)
- Skills: [`review-convergence`] — verdicts feed the `origin: spec-drift` classification

**Skills Evaluation**:
- INCLUDED `review-convergence`: `origin` taxonomy (`spec-drift` vs `original-coding`) is decided here
- OMITTED `agent-reach`, `ultimate-browsing`, `context7`-style doc lookup: all sources are in-repo; no internet research is warranted
- OMITTED `explore-codebase`: one Python symbol (`reader.read`) needs checking — a direct read is cheaper

**Depends On**: None

**Acceptance Criteria**:
- Every citation listed in F003 spec §0/§7 and design §0/§2 appears with a verdict and resolved `file:line`
- Zero verdicts left as "unchecked"
- Any `resolves+misstated` entry quotes both the F003 claim and the upstream text

---

### Task 5: Deep review of `spec.md`

**Description**: Run the Task-1 checklist against `spec.md` (345 lines). Bounded assertion set:
1. **Structure**: exactly the 9 fixed top-level sections, correct numbering/titles; frontmatter has `kind/id/version/status/gate_version/updated`; no second status source.
2. **Intent & scope**: single one-line intent; §1 非目标 vs §3 范围外 are not copies of each other; 范围外 items each name a receiving feature.
3. **Requirements quality**: each `FR/DR/TR/IR/NFR` describes one observable behavior; each important requirement has ≥1 Given/When/Then scenario; error/boundary/recovery scenarios present.
4. **Falsifiability of NFRs**: `NFR-001` (≥50 candidates per night window), `NFR-002` (≤6GB, configurable), `NFR-003` (reproducibility tuple), `NFR-004` (no egress + no evidence-write), `NFR-005` (device/hostname) — each must be judgeable by a stated procedure, on a stated machine, with a stated pass predicate.
5. **Invariants (§5)**: state machine transitions total and single-directional; each invariant has a carrier (AC or task).
6. **Acceptance clause quality**: every `AC-001..011` has unique ID, references only §4-defined IDs, states an observable behavior, and names a plausible test layer.
7. **Q closure**: §8 all `Q-xxx` closed with decisions; each closed decision consistent with the body text (e.g., Q-001 parallel-F008 decision vs §3 范围外 wording vs tasks T001).
8. **Principle compliance**: no path violating SOP §0 principles 1–7 (notably: generator must not adjudicate evidence — ADR-0003; lake-only data; no live-trading path).

**Delegation Recommendation**:
- Category: `ultrabrain` — genuinely hard consistency/logic reasoning over a dense spec; give the goal, not step-by-step
- Skills: [`review-convergence`, `full-output-enforcement`] — protocol for finding schema/severity; full-output to prevent truncated finding lists on a 345-line document

**Skills Evaluation**:
- INCLUDED `review-convergence`: severity layering (Critical/High block; Medium/Low record) and root-cause vs symptom classification
- INCLUDED `full-output-enforcement`: prior loops produced 14–23 findings; truncation would silently drop findings
- OMITTED `code-review-agent`: superseded by `review-convergence` for loop-based review
- OMITTED `programming`: spec contains no code beyond illustrative blocks
- OMITTED `i-have-adhd`: output format for the report is fixed by the protocol

**Depends On**: Task 1, Task 3

**Acceptance Criteria**:
- Every checklist assertion for `spec.md` has an explicit verdict (no "not assessed")
- Each finding carries: `file:line`, one-line problem statement, severity, category (correctness/quality/test-coverage), root-cause-vs-symptom, and a `suggested_fix`
- Zero findings without an evidence pointer

---

### Task 6: Deep review of `design.md`

**Description**: Run the checklist against `design.md` (252 lines). Bounded assertion set:
1. **Structure**: exactly the 11 fixed sections; inapplicable sections say `不适用：<理由>` rather than being deleted (§6 UI, §3 migration).
2. **Architecture feasibility**: the module tree (§2) covers every requirement; one-way dependency rule `平面 → 胶水 → vendor` has an enforcing mechanism (AC-002) and the enforcement is actually decidable; vendor subset defined by function (DQ-001) leaves no undecidable implementation step.
3. **Data model**: FactorDef / HypothesisDef / GenerationRun / AlphaPoolDef fields cover DR-001..004; content-addressing definition (`definition_digest` excludes `factor_id`/`run_id`/`created_at`) is self-consistent with `factor_id` construction; the conclusion-field blacklist is specified as a *whitelist* schema (design §3 says both — check consistency).
4. **Contracts & events**: CLI table's rejection conditions cover every `IR-001` requirement; `GenerationRequest/Result/Generator` protocol matches `IR-002`; event payloads match `TR-001/TR-002`; `schema_version` present per `IR-003`; idempotency key `(run_id, event_seq)` is producible by the described writer.
5. **Runtime/concurrency**: flock single-slot + VRAM self-check + window validation ordering is race-free as described; SIGTERM/`FAILED`/no-`run.json` recovery semantics are complete; checkpoint explicitly excluded from identity vs `NFR-003`.
6. **Failure/security/compat**: `egress_guard` honestly scoped as process-level (not isolation) — check the honesty claim is carried into spec/AC; write-path whitelist enforceable; `check_dep_pins` relaxation ("installed-only") is paired with a fail-closed runtime check — per SOP §1 this is a *gate downgrade* and must be declared; WSL/POSIX portability constraints consistent with §7.1.
7. **Test mapping (§8)**: all 11 ACs mapped, layer choices coherent with what the assertion actually needs (e.g., AC-006 `≥50 registered` is an executor-machine claim — does the mapping say so?); real-environment paragraph matches SOP §3.
8. **DQ closure (§10)**: all `DQ-001..005` closed; each closed decision has a task carrier in `tasks.md` (protocol: deferred verification must become a task with AC, not prose).
9. **New pre-condition**: the 2026-09-16 development-gate note (design.md:16-18) requires a `[TEST]` group in `tasks.md` — verify whether the stated precondition is satisfied by the current `tasks.md` and, if not, whether that is a finding against design, tasks, or both.

**Delegation Recommendation**:
- Category: `ultrabrain` — architecture/contract/concurrency reasoning with cross-document implications
- Skills: [`review-convergence`, `full-output-enforcement`] — same rationale as Task 5

**Skills Evaluation**:
- INCLUDED `review-convergence`, `full-output-enforcement`: as Task 5
- OMITTED `debug-issue`, `refactor-safely`: no runtime defect and no code to restructure
- OMITTED `security-review`: the security surface here is a documented process-level guard, reviewed as a spec claim; a full adversarial security team-mode run is disproportionate for a doc round and would produce unevidenced speculation

**Depends On**: Task 1, Task 4

**Acceptance Criteria**:
- All 11 design sections have an explicit verdict, including the `不适用` ones
- Every finding cites `design.md:<line>` plus the contradicted counterpart location
- §8 mapping table checked row-by-row against spec §6 (11/11 rows reported)

---

### Task 7: Deep review of `tasks.md` including DAG and `[TEST]` group

**Description**: Run the checklist against `tasks.md` (105 lines) using Matrix D:
1. **Structure**: exactly the 6 fixed sections; Phases appear only as `###` under §2; unified task format `- [ ] Txxx [P] (refs): action — verify: path`.
2. **ID integrity**: T001–T036 continuous and unique; every `(FR/DR/TR/IR/NFR/AC/US/Q)` reference resolves to a real ID in spec/design.
3. **DAG integrity**: acyclic; every task reachable; edge list consistent with prose prerequisites; no `[P]` task carrying a declared edge; ordering respects "test before implementation" (loop-11 lesson `test-created-after-implementation`) and "evidence-producing task precedes the write-back task" (loop-11 lesson `task-graph-order-contradiction`).
4. **AC coverage**: every `AC-001..011` has ≥1 implementing task and ≥1 verification task in §3; every `verify:` path is under `tests/unit` or `tests/integration` (tasks §0 rule + `tools/verify.py` collection scope), or is a document/command with a decidable pass predicate.
5. **`[TEST]` group**: check for the journey-acceptance group mandated by design.md:16-18 and `TEMPLATE/tasks.md:57-61`; if absent, classify (`origin: spec-drift` vs `process-gap`) and note that the T3 development gate would reject the transition.
6. **Deferral discipline**: §5 items each name a target feature/version; no in-scope work parked there; every "executor-machine evidence" deferral has a task carrier with a decidable AC (loop-12 lesson `deferred-work-without-carrier`).
7. **Stale prerequisites**: e.g. T001 asks to close a `Q-001` that spec §8 already records as closed — verify and classify rather than presume.

**Delegation Recommendation**:
- Category: `deep` — graph-consistency reasoning plus cross-file ID resolution; one deliverable (tasks finding set)
- Skills: [`review-convergence`] — deferral/tracked-vs-defect classification rules (protocol §4) are decided here

**Skills Evaluation**:
- INCLUDED `review-convergence`: protocol §4 distinguishes "product defect" from "upstream task not yet executed" — critical for T001/T035-type items
- OMITTED `full-output-enforcement`: 105-line file with a bounded matrix; truncation risk is low
- OMITTED `pm`: cross-project phase management, not single-feature task-graph auditing

**Depends On**: Task 1, Task 3

**Acceptance Criteria**:
- All 36 tasks audited; DAG verdict stated (acyclic yes/no, unreachable list, violating `[P]` list)
- 11/11 AC coverage verdicts reported
- `[TEST]` group presence/absence stated with line evidence from both `tasks.md` and the mandating source

---

### Task 8: Cross-document and cross-feature consistency

**Description**: Verify F003 against its neighbours and repo indices:
1. **Internal tri-document consistency**: same claim stated in spec vs design vs tasks must not diverge (VRAM ≤6GB, 22:00–06:30 window, ≥50 candidates, 6-pair universe, executor `qiaozhi-lt`, `mining` extra, resample 1h, transition-mode binding).
2. **BACKLOG ↔ spec**: `BACKLOG.md:8` row (`F003-alphagen-vendor | 0.2 | draft | link`) matches spec frontmatter and the link resolves.
3. **CLAUDE.md active-feature list**: `CLAUDE.md:51-52` lists F004 and F007 as active but not F003 — verify against BACKLOG/spec status and classify any mismatch.
4. **docs/README ownership map**: F003's new artifacts (`reports/generation/`, `VENDORED.md`, `mining` extra, SOP exemption-table entry) — check whether each has a declared owner document, or whether F003 silently creates an unowned artifact.
5. **Cross-feature contract drift** (loop-11's top pattern): F002 (reader API + `symbol_map` + `value_digest` semantics), F004 (shared GPU, Kronos unload responsibility — F003 claims it belongs to F004; check F004's docs actually own it), F007 (consumes `generation.candidate_rejected` as funnel level 1 and `operator_registry` export — check F007's spec agrees), F008 (parallel universe expansion, T035 dependency — check F008's spec accepts the coupling).
6. **SOP/CLAUDE promises**: design §1 promises edits to `docs/SOP.md` Code Quality exemption table and `pyproject.toml` — check a task owns each promised edit.

**Delegation Recommendation**:
- Category: `deep` — multi-document contract-drift hunting; one deliverable (cross-consistency finding set)
- Skills: [`review-convergence`] — `cross-feature-contract-drift` pattern tagging and origin classification

**Skills Evaluation**:
- INCLUDED `review-convergence`: this task is exactly where loop-11's four-hop rule ("behavior promise → implementation owner → test gate → evidence task") is applied
- OMITTED `github-repo-standard`: repo-hygiene standard, not feature-spec consistency
- OMITTED `explore-codebase`: the referenced code surface is one module (`data_bridge/reader.py`), directly readable

**Depends On**: Task 2, Task 3, Task 4

**Acceptance Criteria**:
- All 6 consistency dimensions reported with verdicts
- Every cross-feature claim checked against the *other* feature's document, with that document's `file:line` cited
- Index checks (BACKLOG, CLAUDE, docs/README) reported pass/fail with evidence

---

### Task 9: Consolidate, deduplicate, and classify findings

**Description**: Merge Task 5–8 outputs into a single issue set. For each finding assign, per protocol §8 frontmatter schema: stable `id` (`F003-D001…`, continuing the loop-11 `F004-Dxxx` convention), `title` (one line), `severity` (Critical/High/Medium/Low), `category` (correctness | quality | test-coverage), `root_cause` (root-cause | symptom-patch), `origin` (original-coding | fix-regression | spec-drift | process-gap), `pattern_tag` (reuse prior-loop tags; blank if none fits — do not invent filler), `status` (`open`, or `tracked` + `tracked_task` if it is an unexecuted upstream task rather than a defect), `suggested_fix` (mandatory, one line, and per loop-10's lesson it must state *which new hole the fix could open*), `regression_test` (the gate/test that would catch it, or `—` with reason), `location`, `first_seen_round: 1`, `resolved_round` blank.

Deduplicate: identical root cause with multiple manifestations = one finding enumerating all landing points (loop-12 lesson `partial-symmetric-fix` — enumerate every landing point in `suggested_fix`). Then compute `severity_counts` and set `stop_condition_met: false` (Round 1 cannot close; protocol §8 mandates ≥2 rounds).

**Delegation Recommendation**:
- Category: `ultrabrain` — severity calibration and root-cause-vs-symptom judgement are the highest-leverage decisions in the whole review
- Skills: [`review-convergence`] — the classification taxonomy is the skill's core content

**Skills Evaluation**:
- INCLUDED `review-convergence`: severity blocking rules, tracked-vs-defect rule, pattern taxonomy
- OMITTED `full-output-enforcement`: consolidation output is a structured table; the authoring task (10) carries the truncation risk
- OMITTED `writing`-domain skills: classification, not prose

**Depends On**: Task 5, Task 6, Task 7, Task 8

**Acceptance Criteria**:
- Every finding has all 13 schema fields populated (or explicit `—` with justification)
- No duplicate root causes across IDs; multi-landing-point issues consolidated with all points enumerated
- Severity counts computed; Critical/High list explicitly separated from Medium/Low
- Zero findings lacking an evidence pointer (invention audit passes)

---

### Task 10: Author `docs/reviews/CURRENT-doc.md` (Chinese)

**Description**: Write the report at `docs/reviews/CURRENT-doc.md` — **the only file this entire plan creates** — in Chinese, in the protocol's fixed format:

- **Frontmatter**: `report_type: doc-review`, `round: 1`, `date: <today>`, `prior_report: 无（F003 首轮）`, `scope: full-scan`, `stop_condition_met: false`, `severity_counts: {...}`, `issues:` list with the full per-issue schema from Task 9.
- **Body, 结论先行**: baseline declaration (`main@a333394`, tree-clean), scope statement (three F003 files + necessary upstream cross-checks; code review excluded and why), evidence sources (gate outputs from Task 2, matrices from Task 3, citation verdicts from Task 4), and the headline verdict with counts.
- **Single fixed Chinese-header issue table** (one format for all entries, `—` for empty cells):
  `| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |`
- **裁决记录 section** immediately below the table (empty in Round 1: `本轮无 rejected / partial 裁决`).
- **Closing section**: Round-2 entry criteria (diff-only unless the fix diff exceeds 30% of the reviewed content, in which case one — and only one — full-scan upgrade), the stop conditions that remain unmet, and the explicit statement that this file is a local-only process draft (gitignored, never committed, deleted only by the reviewer after closure).

**Delegation Recommendation**:
- Category: `writing` — Chinese technical prose in a rigid template
- Skills: [`review-convergence`, `full-output-enforcement`] — exact report template + a hard ban on truncating the issue table

**Skills Evaluation**:
- INCLUDED `review-convergence`: frontmatter schema, Chinese table headers, 裁决记录 placement, lifecycle statement
- INCLUDED `full-output-enforcement`: the table must be emitted complete; a "… (remaining items omitted)" placeholder would silently destroy findings
- OMITTED `baoyu-translate`: content is authored in Chinese natively, not translated
- OMITTED `i-have-adhd`: the report format is prescribed by the protocol and outranks output-style preferences

**Depends On**: Task 9

**Acceptance Criteria**:
- File exists at `docs/reviews/CURRENT-doc.md`; `git check-ignore -v docs/reviews/CURRENT-doc.md` confirms it is ignored
- Frontmatter contains all required keys; `stop_condition_met: false`; `scope: full-scan`; `round: 1`
- Issue table row count == frontmatter `issues` count == sum of `severity_counts`
- All table headers in Chinese; no English frontmatter field names used as table headers
- 裁决记录 section present (explicitly empty)

---

### Task 11: Self-verify the report

**Description**: Reviewer-perspective audit of the Task-10 artifact:
1. **Format**: 13 columns present in every row; `—` used for empty cells (never a missing column); IDs unique and stably named.
2. **Count reconciliation**: table rows == frontmatter issues == severity_counts sum.
3. **Evidence audit**: sample **every** Critical/High finding and ≥50% of Medium/Low — re-open the cited `file:line` and confirm the quoted text says what the finding claims. Any finding that fails → delete or downgrade it (no-invention rule).
4. **Checklist closure**: every Task-1 assertion has a verdict somewhere in the report; the report states the bounded checklist is exhausted (Round 1 scanning stops here).
5. **Protocol compliance**: `stop_condition_met: false` justified (Round 1 can never close); Round-2 entry criteria stated; no file outside `docs/reviews/CURRENT-doc.md` was created or modified — prove with `git status --porcelain` (expect still clean, since the report is gitignored).

**Delegation Recommendation**:
- Category: `unspecified-high` — verification pass requiring care but not novel reasoning
- Skills: [`review-convergence`] — the independent-verification discipline ("核对，不是采信") is the skill's central rule

**Skills Evaluation**:
- INCLUDED `review-convergence`: protocol §8 mandates independent verification rather than accepting claims at face value
- OMITTED `ci-verify`: nothing pushed; CI is the closure-round gate
- OMITTED `code-review-agent`: would produce a second, differently-formatted report — exactly the inconsistency the protocol forbids

**Depends On**: Task 10

**Acceptance Criteria**:
- Audit log lists each sampled finding with `verified | corrected | dropped`
- Count reconciliation printed and matching
- `git status --porcelain` output shown and clean (proving read-only compliance)
- Explicit statement: "Round 1 closed as a scan; loop not converged; Round 2 = diff-only after fixes"

---

## Commit Strategy

**Round 1 produces zero commits. This is the correct outcome, not an omission.**

| Artifact | Git disposition | Why |
|---|---|---|
| `docs/reviews/CURRENT-doc.md` | **Never committed** — gitignored at `.gitignore:39`, verified via `git check-ignore -v` | Protocol §8: review files are process drafts that never enter git history; the only safety net is copying content into `RETROSPECTIVE.md` at closure |
| F003 `spec/design/tasks.md` | **Unmodified** — review is read-only | Reviewer authors findings; the fix side owns the edits |
| `docs/reviews/FIX-log.md` | Not created in Round 1 | Owned exclusively by the fix side; append-only fix declarations |
| `docs/reviews/RETROSPECTIVE.md` | Committed **only at loop closure**, by the reviewer | Protocol §8 closure sequence — after fixes land, Round 2 verifies, and CI is green |

**Atomic commit rules for the subsequent fix round (documented now so the plan is complete — not executed here):**
1. **One finding = one commit.** Message: `docs(f003): <finding-id> <one-line fix>`, matching repo style (`docs(f004): …`, `docs(sdd): …`). This preserves bisect/revert; the 744-line 9-finding commit is the known anti-pattern.
2. Each fix runs its own targeted gate immediately (`.venv/bin/python tools/validate_spec_lifecycle.py` for structure/AC changes; `check_doc_links.py` for link changes) — seconds, not the full suite.
3. **Full gate once per round, at round end**: `.venv/bin/python tools/verify.py` must be green before pushing; push once per round, not once per commit.
4. Fix declarations go to `FIX-log.md` (append-only, evidence triple: findings / commits / regression_tests / gate output+timestamp) — **never** by editing `CURRENT-doc.md`; only the reviewer flips issue `status`.
5. `docs/reviews/` must never appear in `git add -A` output — confirm with `git status --porcelain` before each commit.
6. **Closure**: reviewer copies the complete issue table (all 13 fields, not a summary) plus pattern lessons into `RETROSPECTIVE.md` as "循环 13：F003 …", commits **that file only**, pushes, watches CI to green (`gh run watch <run-id> --exit-status`), then deletes `CURRENT-doc.md` and `FIX-log.md` locally (untracked; no deletion commit). **CI red → do not delete; reopen as round N+1.**

---

## Success Criteria

1. `docs/reviews/CURRENT-doc.md` exists in Chinese, Round-1 full-scan format-compliant, and is confirmed gitignored.
2. `git status --porcelain` is clean after the review — proof that nothing was edited, staged, or committed.
3. Every Task-1 checklist assertion has a recorded verdict; the checklist is declared exhausted (bounded scan, no open-ended re-reading).
4. Every finding carries a resolvable `file:line` evidence pointer; the Task-11 audit sampled 100% of Critical/High and ≥50% of Medium/Low with zero unverifiable claims surviving.
5. Traceability is reported as data, not opinion: requirement→AC→task coverage gaps, AC↔test-path↔design-§8 mismatches, and the task DAG verdict are all explicit.
6. `stop_condition_met: false` with Round-2 entry criteria stated (diff-only; single full-scan upgrade permitted only if the fix diff exceeds 30% of reviewed content).
7. Machine-gate evidence (`validate_spec_lifecycle.py`, `check_doc_links.py`, and `verify.py` if run) is transcribed verbatim, with any not-run step explicitly justified.

---

## TODO List (ADD THESE)

> CALLER: Add these TODOs using TodoWrite/TaskCreate and execute by wave.
> Scratchpad root: `/tmp/claude-1000/-home-ryan-projects-platform/36621a8e-e150-416a-8fac-e14e20115a6c/scratchpad` → use `.../f003-review/`.
> Repo root for all commands: `/home/georg/projects/alphamill`.

### Wave 1 (Start Immediately - No Dependencies)

- [ ] **1. Extract conventions + prior-loop lessons into a bounded checklist**
  - What: Read `CLAUDE.md`, `docs/SOP.md`, `docs/features/README.md`, `docs/README.md`, `.sdd.json`, `.gitignore`, `docs/reviews/RETROSPECTIVE.md` (loops 10–12). Write `<scratch>/f003-review/checklist.md` with ≥6 pass-fail assertion groups (7 principles / spec 9 sections / design 11 sections / tasks 6 sections + `[TEST]` group / traceability rules / evidence-machine discipline), each citing its owner `file:line`, plus the reusable `pattern_tag` list.
  - Depends: None
  - Blocks: 5, 6, 7
  - Category: `unspecified-low`
  - Skills: [`review-convergence`]
  - QA: `checklist.md` has ≥6 groups; every rule cites `file:line`; ≥8 pattern tags copied verbatim from RETROSPECTIVE.

- [ ] **2. Capture baseline + machine-gate evidence**
  - What: Run and transcribe to `<scratch>/f003-review/gates.md`: `git rev-parse --short HEAD` (expect `a333394`), `git status --porcelain` (expect empty), `git check-ignore -v docs/reviews/CURRENT-doc.md`, `.venv/bin/python tools/validate_spec_lifecycle.py`, `.venv/bin/python tools/check_doc_links.py`, `.venv/bin/python tools/verify.py` (or record "skipped + reason"), and `ls tests/unit tests/integration` vs the 11 AC `tests:` paths.
  - Depends: None
  - Blocks: 8
  - Category: `quick`
  - Skills: []
  - QA: All 6 items present with verbatim output or explicit not-run reason; baseline line `main@a333394` recorded; HEAD drift or dirty tree → stop and report.

- [ ] **3. Build traceability matrices A–D**
  - What: From the three F003 files, write `<scratch>/f003-review/traceability.md`: (A) requirement ID × AC × task coverage with gap lists; (B) AC ↔ spec §6 `tests:` path ↔ design §8 row ↔ task `verify:` path; (C) US-001/002/003 scenarios → AC/task carriers; (D) task DAG from tasks §4 — ID continuity, reachability, cycles, dangling refs, `[P]`-with-edge violations, prose-vs-arrow mismatches.
  - Depends: None
  - Blocks: 5, 7, 8
  - Category: `unspecified-low`
  - Skills: [`review-convergence`]
  - QA: Matrices A–D complete with `file:line` per cell; explicit gap lists; Matrix D states "acyclic: yes/no" + violation lists.

- [ ] **4. Verify every upstream citation resolves and is accurately stated**
  - What: Resolve each reference in spec §0/§7 and design §0/§2 (PRD FR2.1/2.2/2.3/2.4/2.6, FR1.5, G3, M2; architecture §三/§4.0/§4.1/§4.1.1/§7.1; research §3.1; integration §五; ADR-0001/0002/0003/0007; F002 `reader.read()` + identity tuple + `symbol_map`). Write `<scratch>/f003-review/citations.md`: reference → `file:line` → `{resolves+accurate | resolves+misstated | dangling}` → upstream quote. Prioritize ADR-0001 smoke criteria vs `FR-006`/§5 tier machine, ADR-0002 vs `FR-002`, arch §4.1.1 vs `FR-004`, arch §7.1 vs `NFR-002`.
  - Depends: None
  - Blocks: 6, 8
  - Category: `deep`
  - Skills: [`review-convergence`]
  - QA: Zero "unchecked" verdicts; every `resolves+misstated` quotes both F003's claim and the upstream text.

### Wave 2 (After Wave 1 Completes)

- [ ] **5. Deep review of `spec.md`**
  - What: Apply `checklist.md` + Matrix A/C to all 345 lines — 9-section structure, frontmatter, intent/scope non-duplication, requirement observability, NFR falsifiability (NFR-001..005 each need a stated procedure + machine + pass predicate), §5 invariants with carriers, AC quality, §8 Q-closure consistency (incl. Q-001 vs §3 vs tasks T001), and SOP §0 principle compliance. Output raw findings with `file:line` + severity + category + root-cause/symptom + `suggested_fix`.
  - Depends: 1, 3
  - Blocks: 9
  - Category: `ultrabrain`
  - Skills: [`review-convergence`, `full-output-enforcement`]
  - QA: Every spec checklist assertion has a verdict; zero findings without an evidence pointer.

- [ ] **6. Deep review of `design.md`**
  - What: Apply checklist + citation verdicts to all 252 lines — 11 sections incl. `不适用` handling; module tree vs requirement coverage; one-way dependency enforceability; data-model self-consistency (digest exclusion vs `factor_id`, blacklist-vs-whitelist wording in §3); CLI/protocol/event contracts vs IR/TR; runtime race-freedom, recovery, checkpoint-vs-identity; `egress_guard` honesty propagation; `check_dep_pins` relaxation as a declared gate downgrade (SOP §1); §8 AC mapping row-by-row against spec §6; DQ-001..005 closure each having a task carrier; and whether the design.md:16-18 `[TEST]` pre-condition is satisfied.
  - Depends: 1, 4
  - Blocks: 9
  - Category: `ultrabrain`
  - Skills: [`review-convergence`, `full-output-enforcement`]
  - QA: All 11 sections verdicted; 11/11 §8 rows compared to spec §6; every finding cites both sides of each contradiction.

- [ ] **7. Deep review of `tasks.md` + task DAG + `[TEST]` group**
  - What: Apply checklist + Matrix B/D to all 105 lines — 6-section structure, Phase placement, unified task format, T001–T036 continuity and reference resolution, DAG acyclicity/reachability/prose-arrow agreement, `[P]` legality, test-before-implementation ordering, evidence-before-write-back ordering, `verify:` paths inside `tests/unit|tests/integration`, 11/11 AC implementation+verification coverage, `[TEST]` group presence, §5 deferral discipline (each deferral needs a target feature or an AC-bearing task carrier), and stale prerequisites such as T001 vs already-closed Q-001.
  - Depends: 1, 3
  - Blocks: 9
  - Category: `deep`
  - Skills: [`review-convergence`]
  - QA: All 36 tasks audited; DAG verdict stated; 11/11 AC coverage verdicts; `[TEST]` presence/absence cited from both files.

- [ ] **8. Cross-document and cross-feature consistency check**
  - What: Verify (a) tri-document agreement on VRAM ≤6GB / 22:00–06:30 / ≥50 candidates / 6-pair universe / `qiaozhi-lt` / `mining` extra / 1h resample / transition binding; (b) `BACKLOG.md:8` ↔ spec frontmatter ↔ link; (c) `CLAUDE.md:51-52` active-feature list vs F003 status; (d) `docs/README.md` ownership map vs F003's new artifacts (`reports/generation/`, `VENDORED.md`, `mining` extra, SOP exemption entry); (e) cross-feature drift against F002/F004/F007/F008 — each claim checked in the *other* feature's document with `file:line`; (f) design §1's promised edits to `docs/SOP.md` and `pyproject.toml` each having a task owner.
  - Depends: 2, 3, 4
  - Blocks: 9
  - Category: `deep`
  - Skills: [`review-convergence`]
  - QA: All 6 dimensions verdicted; every cross-feature claim cites the counterpart document; index checks reported pass/fail.

### Wave 3 (After Wave 2 Completes)

- [ ] **9. Consolidate, deduplicate, and classify all findings**
  - What: Merge outputs of 5–8 into one issue set. Assign per finding: `id` (`F003-D001…`), `title`, `severity`, `category`, `root_cause`, `origin`, `pattern_tag` (reuse prior-loop tags; blank rather than invented), `status` (`open` / `tracked`+`tracked_task`), `suggested_fix` (must also state what new hole the fix could open), `regression_test` (gate that would catch it, or `—`+reason), `location`, `first_seen_round: 1`. Merge same-root-cause findings into one entry that **enumerates every landing point**. Compute `severity_counts`; set `stop_condition_met: false`.
  - Depends: 5, 6, 7, 8
  - Blocks: 10
  - Category: `ultrabrain`
  - Skills: [`review-convergence`]
  - QA: All 13 schema fields populated per finding; no duplicate root causes; Critical/High separated from Medium/Low; every finding has an evidence pointer.

### Wave 4 (After Wave 3 Completes)

- [ ] **10. Author `docs/reviews/CURRENT-doc.md` in Chinese**
  - What: Write the report — frontmatter (`report_type: doc-review`, `round: 1`, `date`, `prior_report: 无（F003 首轮）`, `scope: full-scan`, `stop_condition_met: false`, `severity_counts`, full `issues` list); 结论先行 body with baseline `main@a333394`, scope statement (three F003 files; code review excluded and why), evidence sources, headline verdict; the single fixed Chinese-header 13-column issue table (`—` for empty cells); an empty 裁决记录 section; and a closing section stating Round-2 entry criteria, unmet stop conditions, and the local-only lifecycle of this file.
  - Depends: 9
  - Blocks: 11
  - Category: `writing`
  - Skills: [`review-convergence`, `full-output-enforcement`]
  - QA: `git check-ignore -v docs/reviews/CURRENT-doc.md` → matches `.gitignore:39`; table rows == frontmatter issues == severity_counts sum; all headers Chinese; 裁决记录 present.

### Wave 5 (After Wave 4 Completes)

- [ ] **11. Self-verify the report (reviewer audit)**
  - What: Check 13 columns in every row and `—` usage; reconcile counts three ways; re-open cited `file:line` for 100% of Critical/High and ≥50% of Medium/Low findings and drop/downgrade any that don't hold; confirm every Task-1 assertion has a verdict and declare the checklist exhausted; confirm `stop_condition_met: false` with Round-2 criteria stated; run `git status --porcelain` to prove nothing outside the gitignored report was touched.
  - Depends: 10
  - Blocks: None
  - Category: `unspecified-high`
  - Skills: [`review-convergence`]
  - QA: Audit log lists each sampled finding as `verified|corrected|dropped`; count reconciliation printed and matching; `git status --porcelain` output shown and empty; explicit "Round 1 scan complete; loop not converged; Round 2 = diff-only" statement.

## Execution Instructions

1. **Wave 1**: Fire all four IN PARALLEL (no dependencies)
   ```
   task(category="unspecified-low", load_skills=["review-convergence"], run_in_background=false, prompt="Task 1: ...")
   task(category="quick",           load_skills=[],                     run_in_background=false, prompt="Task 2: ...")
   task(category="unspecified-low", load_skills=["review-convergence"], run_in_background=false, prompt="Task 3: ...")
   task(category="deep",            load_skills=["review-convergence"], run_in_background=false, prompt="Task 4: ...")
   ```

2. **Wave 2**: After Wave 1 completes, fire all four IN PARALLEL
   ```
   task(category="ultrabrain",       load_skills=["review-convergence","full-output-enforcement"], run_in_background=false, prompt="Task 5: ...")
   task(category="ultrabrain",       load_skills=["review-convergence","full-output-enforcement"], run_in_background=false, prompt="Task 6: ...")
   task(category="deep",             load_skills=["review-convergence"],                          run_in_background=false, prompt="Task 7: ...")
   task(category="deep",             load_skills=["review-convergence"],                          run_in_background=false, prompt="Task 8: ...")
   ```

3. **Wave 3**: Single consolidation task
   ```
   task(category="ultrabrain", load_skills=["review-convergence"], run_in_background=false, prompt="Task 9: ...")
   ```

4. **Wave 4**: Authoring
   ```
   task(category="writing", load_skills=["review-convergence","full-output-enforcement"], run_in_background=false, prompt="Task 10: ...")
   ```

5. **Wave 5**: Audit
   ```
   task(category="unspecified-high", load_skills=["review-convergence"], run_in_background=false, prompt="Task 11: ...")
   ```

6. **Final QA**: Confirm all 7 Success Criteria. Report to the user: severity counts, the Critical/High list, the location of `docs/reviews/CURRENT-doc.md`, and that **no commits were made and the working tree is clean**. Do not proceed to fixes or closure — Round 1 ends here; the fix side owns edits and `FIX-log.md`, and closure (RETROSPECTIVE write-back + CI-green + file deletion) happens only after Round 2.

**Hard constraints for every wave** (repeat verbatim in each delegated prompt):
- Read-only. Do not edit, create, stage, commit, or push anything except `docs/reviews/CURRENT-doc.md` in Task 10 and scratchpad files.
- No finding without a resolvable `file:line` or command-output pointer. If you cannot evidence it, drop it.
- Baseline is `main@a333394`. If `git rev-parse --short HEAD` differs or `git status --porcelain` is non-empty, stop and report drift instead of proceeding.
</plan>
