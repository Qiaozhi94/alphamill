---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4b4744afffeM1EPTLFBo0QxJo"
title: "F007 T002 prereg schema + control fixtures (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-18T13:33:20Z"
updated_at: "2026-09-18T13:34:25Z"
tokens_input: 98510
tokens_output: 599
cost: 0.0
parent_id: "ses_f4b709dbdffevQ17e9JKDUhkz6"
---

# F007 T002 prereg schema + control fixtures (@Sisyphus-Junior subagent)

## user · 2026-09-18T13:33:20Z

Implement task T002 of feature F007 in the AlphaMill repo.

## CONTEXT (read this fully before acting)
- Repo (git worktree): `/home/georg/projects/alphamill-eval-gates` — branch `feat/F007-evaluation-gates`. Work ONLY here.
- Feature docs (READ ALL THREE IN FULL FIRST):
  - `docs/features/0.2/F007-evaluation-gates/spec.md` (behavior truth)
  - `docs/features/0.2/F007-evaluation-gates/design.md` (technical truth; frozen enums/schemas/report fields)
  - `docs/features/0.2/F007-evaluation-gates/tasks.md` (task T002 text + §4 dependency graph)
- Python 3.11+, `src/` layout. Existing style references: `src/alphamill/factor_factory/`, `tests/` layout, any existing `tests/fixtures/` conventions.
- The worktree has NO synced venv. Use EXACTLY this invocation:
  `PYTHONPATH=/home/georg/projects/alphamill-eval-gates/src /home/georg/projects/alphamill/.venv/bin/python -m pytest -q --confcutdir=tests --rootdir=tests <paths>`
- Run pytest with `workdir=/home/georg/projects/alphamill-eval-gates`.

## TASK (T002, refs FR-004 / FR-005)
Pre-register the v1 method/threshold/cohort schema, and build the four control fixtures: two positive controls, a white-noise control, and a deliberate-leakage negative control.

## EXPECTED OUTCOME (concrete deliverables)
1. A versioned v1 pre-registration config schema (method + thresholds + cohort schema). Threshold VALUES live in the pre-registration config, NOT hardcoded in evaluation functions (design §1, design §3.3).
2. Fixture data files under `tests/fixtures/f007/` implementing exactly four controls:
   - positive control #1 (e.g. funding carry)
   - positive control #2 (e.g. BTC-ETH cross-sectional momentum)
   - white-noise control
   - deliberate future-fill / leakage negative control
3. `tests/fixtures/f007/README.md` documenting each fixture: what it is, its expected gate outcome, and how later tasks load it. This README is the T002 `verify` artifact.
4. The fixtures must be LOADABLE by later tasks (deterministic, no network, no wall-clock dependence).

## MUST DO
- Read design §3.3 (frozen terminology: `stage_results[].status`, `cost_verdict`, `sample_tier`, `promotion_verdict`, `cohort_verdict.status`) and §8 (test strategy mapping) and derive the thresholds/schema from them. Do not invent enums or rename fields.
- The two positive controls must be able to drive a full five-stage PASS path; the white-noise control must be catchable by the statistical gate; the leakage control must be catchable by the methodology gate (future-fill).
- Fixtures must be small, deterministic and committed as data (CSV/JSON/Parquet as appropriate), with fixed seeds where randomness is involved.
- Include a machine-readable pre-registration config file (e.g. under `tests/fixtures/f007/` or `configs/`) and document its schema (fields, units, allowed values) in the README.
- Cohort schema must include: hypothesis family, all candidate commitments/inclusion rules, selection stage, windows, thresholds, method version (design §3.2 `cohort.json`).
- Match existing repo conventions (naming, typing, docstrings). Prefer reusing existing fixture/loader helpers.

## MUST NOT DO
- Do NOT modify `spec.md`, `design.md`, or `tasks.md` (nor `BACKLOG.md`/`CLAUDE.md`). If docs are ambiguous or seem wrong, STOP and report the ambiguity in your final message instead of guessing.
- Do NOT touch files owned by the parallel task T001: `src/alphamill/experiment_store/research_snapshot.py`, `src/alphamill/evaluation/upstream_contracts.py`, `tests/unit/experiment_store/test_research_snapshot.py`, `tests/contract/test_f007_upstream_contracts.py`.
- Do NOT create or edit `tests/integration/test_f007_execution_tiers.py` (owned by a later task, T003).
- Do NOT hardcode thresholds inside evaluation functions; thresholds belong to the pre-registered config.
- Do NOT run `tools/verify.py` (the orchestrator runs the full gate).
- Do NOT weaken gates or add `except Exception: pass`; no type suppression.
- Do NOT exceed 350 lines per file (soft limit 200).
- Do NOT require network access or real market data.

## REQUIRED TOOLS
read, edit, write, bash (pytest + git status/diff only), grep, glob, lsp_diagnostics.

## FINAL REPORT (required format)
1. Files created/modified (paths).
2. The exact pre-registration config schema (field list + allowed values).
3. The four fixtures and each one's expected gate outcome.
4. Any test/loader command you ran + observed result.
5. Any ambiguity/assumption you had to make (or "none").
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T13:33:20Z

- **tool**: `todowrite({"todos": [{"content": "F007 docs and Python rules: Read frozen task/design/spec contracts before implementation - expect exact T002 schema and constraints extracted", "priority": "high", "status": "in_progress"}, {"content": "Existing fixture conventions: Inspect repository loaders, fixtures, and relevant factor-factory patterns - expect compatible data layout and test strategy", "priority": "high", "status": "pending"}, {"content": "tests/fixtures/f007: Add pre-registration config and four det
…[truncated])`


> [reasoning] **Planning initial worktree inspection**

> [reasoning] **Planning parallel reading of docs and references**
Step 1 of 5: reading the three frozen F007 documents in full, plus the repository and Python engineering rules. I will derive the fixture/config contract from those texts before inspecting existing fixture conventions.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F007 docs and Python rules: Read frozen task/design/spec contracts before implementation - expect exact T002 schema and constraints extracted",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Existing fixture conventions: Inspect repository loaders, fixtures, and relevant factor-factory patterns - expect compatible data layout and test strategy",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/fixtures/f007: Add pre-registration config and four deterministic control datasets - expect machine-loadable five-stage controls",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/fixtures/f007/README.md and tests: Document schema/outcomes and add loader/schema coverage - expect T002 verify
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:33:36Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/design.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/tasks.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/CLAUDE.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/.config/opencode/skills/programming/references/python/README.md", "limit": 2000})`

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: status: developing
6: status_evidence: 设计基线核对通过；tools/verify.py 全绿于 e06f4fa；进入 SDT 双轨开发
7: branch: feat/F007-evaluation-gates
8: gate_version: 1
9: related_features: [F002, F003, F004, F008]
10: topics: [evaluation, validation, evidence, experiments]
11: doc_kind: spec
12: created: 2026-09-13
13: updated: 2026-09-18
14: ---
15: 
16: # F007：统一评测台与证据门禁
17: 
18: > Owner: Georg | Target: v0.2.x
19: 
20: ## 0. 来源与意图
21: 
22: - **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
23: - **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
24: - **上游 Contract 来源**：F002 `(dataset, DataVersion, value_dige
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004, F008]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: design
8: created: 2026-09-13
9: updated: 2026-09-18
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束**：`tasks.md` §3 的 `[TEST]` 组（层 2 旅程验收轨，编写早、执行晚）是进入代码
17: > 开发的硬性前置门；约束的落地形态与执行规则见 `tasks.md`（design 只声明该约束，不展开步骤）。
18: 
19: ## 0. 输入与约束
20: 
21: - **行为契约**：`spec.md` FR-001~FR-008、DR-001~DR-008、TR-001~TR-003、IR-001~IR-003
22: - **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
23: - **ADR / 上游 Contract**：ADR-0003、ADR-000
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004, F008]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: tasks
8: created: 2026-09-13
9: updated: 2026-09-18
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
21: - 任务编号按追加顺序分配，不代表执行顺序（回写轨 T018/T028 为检视轮追加后按阶段重排的编号）；执行顺序以 §4 依赖图为准。
22: - `[TEST]` 组（§3）是开发前置门：从 US-001/US-002/US-003 旅程步骤派生（每步骤 ≥1 条可执行断言），编写早（Phase 1 先立红灯）、执行晚（收尾全量跑）；缺失即被 SDD Flow T3 拒绝流转。
23: - 属性测试与变异证据可复现：属性
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/CLAUDE.md</path>
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
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:33:55Z

- **tool**: `skill({"name": "programming", "user_message": "Implementing Python-adjacent fixture/config work for F007 T002 in /home/georg/projects/alphamill-eval-gates. Need mandatory Python reference path and rules before any code edits."})`


> [reasoning] **Locating programming skill path**

  <details><summary>tool output</summary>

  ```text
## Skill: programming

**Base directory**: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming

Base directory for this skill: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/
File references (@path) in this skill are relative to this directory.

# Programming

You are a lazy senior engineer — lazy meaning efficient, never careless. **The best code is the code never written; the code you do write is type-strict, stack-first, async-correct, and architecturally honest about size.**

This skill is an index. The hard per-language rules live under `references/`. Load the language-specific reference **before** writing a single line of code.

---

## PHASE 0 — LANGUAGE GAT
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:34:11Z

- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md", "limit": 2000})`


> [reasoning] **Reading file path**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md</path>
<type>file</type>
<content>
1: 
2: # Python Programmer
3: 
4: Modern Python. Type-strict, stack-first, async-correct.
5: 
6: ## Philosophy
7: 
8: The type checker is your compiler. Make illegal states unrepresentable. Parse at boundaries. Own resources explicitly. Every function has a contract; the type system enforces it.
9: 
10: ## Hard rules
11: 
12: These are deliberate project choices. Violations are always wrong, not "style preferences".
13: 
14: ### Tooling
15: 
16: | Category | Use | Never |
17: |---|---|---|
18: | Package manager | `uv` | pip, poetry, conda, pipenv |
19: | Type checker | `basedpyright` (`typeCheckingMode = "all"`
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:34:25Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "Existing test fixture loading conventions, tests/fixtures directory, JSON/CSV/Parquet fixture readers, factor_factory FactorDef and bench data schemas relevant to deterministic F007 controls and pre-registration config", "maxFiles": 12})`


> [reasoning] **Planning JSON Schema and Config Files**

> [reasoning] **Planning schema files and fixture tests**
