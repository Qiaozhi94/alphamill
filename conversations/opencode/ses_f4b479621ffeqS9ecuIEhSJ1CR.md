---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4b479621ffeqS9ecuIEhSJ1CR"
title: "F007 T001 upstream contracts + ResearchSnapshot (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-18T13:32:59Z"
updated_at: "2026-09-18T13:34:28Z"
tokens_input: 132348
tokens_output: 1244
cost: 0.0
parent_id: "ses_f4b709dbdffevQ17e9JKDUhkz6"
---

# F007 T001 upstream contracts + ResearchSnapshot (@Sisyphus-Junior subagent)

## user · 2026-09-18T13:32:59Z

Implement task T001 of feature F007 in the AlphaMill repo.

## CONTEXT (read this fully before acting)
- Repo (git worktree): `/home/georg/projects/alphamill-eval-gates` — branch `feat/F007-evaluation-gates`. Work ONLY here.
- Feature docs (READ ALL THREE IN FULL FIRST):
  - `docs/features/0.2/F007-evaluation-gates/spec.md` (behavior truth: FR-001..FR-008, DR-001..DR-008, IR-001..IR-003, AC-001..AC-013)
  - `docs/features/0.2/F007-evaluation-gates/design.md` (technical truth; §2 module placement, §3.1 identity, §3.2 dirs/events, §4 contracts — enums/schemas are FROZEN)
  - `docs/features/0.2/F007-evaluation-gates/tasks.md` (task T001 text + §4 dependency graph)
- Also read: `docs/decisions/0007-research-snapshot-binding.md`, `docs/decisions/0006-evidence-boundary-and-experiment-identity.md`, and `docs/alphamill-architecture.md` §4 (HypothesisDef/FactorDef/manifest contracts).
- Python 3.11+, `src/` layout. Existing style references: `src/alphamill/data_bridge/`, `src/alphamill/factor_factory/`, `tests/contract/`, `tests/unit/`.
- The worktree has NO synced venv. Use EXACTLY this test invocation:
  `PYTHONPATH=/home/georg/projects/alphamill-eval-gates/src /home/georg/projects/alphamill/.venv/bin/python -m pytest -q --confcutdir=tests --rootdir=tests <paths>`
- Run pytest with `workdir=/home/georg/projects/alphamill-eval-gates`.

## TASK (T001, refs DR-001 / IR-002 / AC-006)
Freeze the F002 dataset/version/value-digest reader and immutable symbol-map ref; implement the ADR-0007 ResearchSnapshot builder/reader contract; implement the F003 read-only upstream ingestion contracts; implement F008 universe artifact digest loading + `universe_at(T)` semantic validation.

## EXPECTED OUTCOME (concrete deliverables)
1. `src/alphamill/experiment_store/research_snapshot.py` — ResearchSnapshot builder + reader.
2. `src/alphamill/evaluation/upstream_contracts.py` — read-only F003 ingestion + F008 universe artifact loading.
3. `tests/unit/experiment_store/test_research_snapshot.py` — GREEN.
4. `tests/contract/test_f007_upstream_contracts.py` — GREEN.
Success criteria: both test files pass under the invocation above, and the code matches the frozen contracts in design.md and the ADR.

## MUST DO
- Builder takes the F008 universe registry digest (`--universe`) and this feature's calendar JSON (`--calendar`) as TWO INDEPENDENT explicit references and validates each one's content digest separately. Never merge them into one input file.
- Builder must only accept explicit universe/calendar artifacts, verify their content summaries, and keep immutable references in `provenance`.
- `preview --latest` must FREEZE first (resolve latest → immutable versions) before anything else; `canonical` accepts only a snapshot ID (never re-resolves "latest").
- Compute `universe_calendar_digest = sha256(canonical_json({"universe": <universe_digest>, "calendar": <calendar_digest>}))` — this exact combined formula is frozen and shared with ADR-0007 / F003 transition tuple.
- Universe artifact is loaded from `lake/_metadata/universes/<digest>.csv` (F008 IR-002) and queried with `universe_at(T)` semantics; validate `schema_version` (F008 IR-003). Do NOT copy the universe into `reports/`.
- Canonicalize the calendar and atomically save it to `reports/research_snapshots/_inputs/universe_calendars/<digest>.json` (calendar only — universe is not merged in).
- Publish the snapshot to `reports/research_snapshots/<snapshot_id>/manifest.json` (design §3.2) and print/expose the actual snapshot ID; `--snapshot` mode must not re-select these inputs.
- Canonical JSON rules: UTF-8, keys sorted, UTC ISO-8601, set fields de-duplicated then sorted. Identity must NOT include physical paths, Parquet codec/row-group, file SHA, host, PID, or timings — those go to provenance only.
- F003 ingestion (read-only): consume `generation.run_completed` ONLY for runs with `status=completed`; consume `generation.candidate_rejected` keyed by reason code (unregistered operator / lookahead / insufficient reachability / duplicate definition). Load the operator capability registry as the methodology gate's "registered capability" list. Pool meta-factor = `generator="pool"` executable `FactorDef`, treated identically to a normal factor; its member `factor_id`s and weights go into manifest provenance.
- Ingest strictly read-only, keyed by `schema_version`. Do NOT write F003 run records and do NOT parse vendor internals.
- Signal-source layering (`source=placeholder`): canonical must REJECT with `E_INPUT_INVALID` (fail-closed); preview may allow it but must annotate `signal_source=placeholder` and set `approximation=true`. Adapter maps shape/semantics only and must NOT change signal values.
- Match existing repo conventions (naming, typing, docstring style, error types). Reuse existing readers/utilities where they already exist instead of duplicating.

## MUST NOT DO
- Do NOT modify `spec.md`, `design.md`, or `tasks.md` (nor `BACKLOG.md`/`CLAUDE.md`). If the docs are ambiguous or seem wrong, STOP and report the ambiguity in your final message instead of guessing.
- Do NOT touch any file owned by the parallel task T002 (`tests/fixtures/f007/**`) or any other feature's files.
- Do NOT run `tools/verify.py` (the orchestrator runs the full gate).
- Do NOT weaken gates: no `except Exception: pass`, no `except Exception` → warning/null for statistics or validation paths (design §7 explicitly forbids this).
- Do NOT use type suppression (`# type: ignore`, `cast` abuse) or `assert` for control flow in production code.
- Do NOT exceed 350 lines per file (soft limit 200 — split if needed).
- Do NOT invent enum values or field names; use exactly the frozen enums from design §3.3 / §4.

## REQUIRED TOOLS
read, edit, write, bash (pytest + git status/diff only), grep, glob, lsp_diagnostics.

## FINAL REPORT (required format)
1. Files created/modified (paths).
2. Exact pytest command(s) run + observed result (pass counts).
3. `lsp_diagnostics` status for files you changed.
4. Any ambiguity/assumption you had to make (or "none").
5. Anything you deliberately left stubbed for later tasks.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T13:32:59Z

- **tool**: `todowrite({"todos": [{"content": "F007 docs and Python rules: Read all frozen contracts and task dependencies to identify exact T001 schemas - expect a field-by-field implementation checklist", "status": "in_progress", "priority": "high"}, {"content": "Existing AlphaMill interfaces: Explore F002/F003/F008 readers, manifests, errors, and test conventions to reuse established contracts - expect an implementation map with no duplicated readers", "status": "pending", "priority": "high"}, {"content": "T001 tes
…[truncated])`


> [reasoning] **Planning full documentation review**
Step 1 of 4: I’m loading the frozen contracts and Python rules in `/home/georg/projects/alphamill-eval-gates`; no code will change until those constraints and existing interfaces are mapped.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F007 docs and Python rules: Read all frozen contracts and task dependencies to identify exact T001 schemas - expect a field-by-field implementation checklist",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Existing AlphaMill interfaces: Explore F002/F003/F008 readers, manifests, errors, and test conventions to reuse established contracts - expect an implementation map with no duplicated readers",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "T001 tests and source modules: Add failing contract/unit tests where absent, then implement snapshot and upstream contracts - expect requested behaviors passing",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Changed files: Run diagnostics, target
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:33:13Z

- **tool**: `skill({"name": "programming", "user_message": "Implement Python task T001 for F007 in /home/georg/projects/alphamill-eval-gates, using strict TDD and existing repo conventions."})`

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

## assistant · 2026-09-18T13:33:24Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/design.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/tasks.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/decisions/0007-research-snapshot-binding.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/decisions/0006-evidence-boundary-and-experiment-identity.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/alphamill-architecture.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/CLAUDE.md", "limit": 4000})`


> [reasoning] **Planning parallel reading of key sections**

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
<path>/home/georg/projects/alphamill-eval-gates/docs/decisions/0007-research-snapshot-binding.md</path>
<type>file</type>
<content>
1: # ADR-0007：研究快照绑定 —— 独立 DatasetVersion 的不可变组合
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted（2026-09-18 修订：universe/calendar 拆为两个独立 artifact 引用并冻结 `universe_calendar_digest` 组合公式，见文末「修订记录」）
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
16: 不是跨 dataset 的一致性边界；它既不固定 point-in-time universe/symbol map，也
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/decisions/0006-evidence-boundary-and-experiment-identity.md</path>
<type>file</type>
<content>
1: # ADR-0006：证据边界与实验身份 —— 显式执行层级、内容寻址和失败关闭
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：PRD FR3 / FR7；ADR-0003；F007 评测台/门禁；ml4t 配套仓的研究工作区与方法门实践
7: 
8: ## 背景
9: 
10: AlphaMill 已有四平面、留出预算和不可变 manifest，但仍有三个跨 Feature 的空隙：探索运行与
11: 正式裁决只有逻辑约定；实验 ID 没有明确区分“决定结果的语义输入”和“仅用于追踪的运行元数据”；
12: 方法实现出错时，缺少统一的失败语义。若这些规则分别留给 F007、F005 和后续部署 Feature
13: 自行解释，preview 可能污染正式样本，重跑可能生成不稳定身份，缺失统计量也可能被误当成 PASS。
14: 
15: ml4t 配套仓提供了可借鉴的模式：显式 `preview/canonical` 执行层级、正式 population 与探索产物
16: 隔离、方法论静态守卫，以及 label endpoint / per-symbol calendar / widest-horizon embargo 等
17: 时间边界测试。它同时是教学与参考实现，不是可直接接入的生产研究平台；其部分统计函数依赖
18: 外部包并会把估计失败降为 warning/空值。因此 AlphaM
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
1: # AlphaMill — 系统架构设计
2: 
3: > 版本：v0.1 | 日期：2026-09-13 | 配套：[alphamill-prd.md](./alphamill-prd.md)
4: 
5: ---
6: 
7: ## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
8: 
9: **不是三选一的竞品，是流水线上的三段**：Parquet 是文件格式（箱子），DuckDB 是查询引擎（开箱的手），TimescaleDB 是数据库服务（实时柜台）。
10: 
11: | | TimescaleDB | Parquet 湖 | DuckDB |
12: |---|---|---|---|
13: | 本质 | PG 时序扩展（数据库服务） | 列式文件格式（无服务） | 进程内 OLAP 查询引擎 |
14: | 写入 | ✅ 流式写入、幂等 upsert、可修订 | ❌ 不可变，只增新文件 | ❌ 不负责存储 |
15: | 擅长 | 实时最新值、连续聚合、Grafana 直连 | 大范围列扫描、快照不可变=可复现 | 直接对 Parquet 跑 SQL |
16: | 复现性 | ❌ 数据会被回补/修订 | ✅ 同一 data_version 永远同结果 | 无关（读的人） |
17: | 角色 | **联机运营库** | **研究快照**（封存账本） | **取数入口**（会计的手） |
18: 
19: ```text
20: CCXT 采集 ──写入──▶ TimescaleDB（联机
…[truncated]
  ```
  </details>

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

## assistant · 2026-09-18T13:33:37Z

- **tool**: `todowrite({"todos": [{"content": "F007 docs and Python rules: Read all frozen contracts and task dependencies to identify exact T001 schemas - expect a field-by-field implementation checklist", "status": "completed", "priority": "high"}, {"content": "Existing AlphaMill interfaces: Explore F002/F003/F008 readers, manifests, errors, and test conventions to reuse established contracts - expect an implementation map with no duplicated readers", "status": "in_progress", "priority": "high"}, {"content": "T001 t
…[truncated])`


> [reasoning] **Planning data modeling and error handling**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "F007 docs and Python rules: Read all frozen contracts and task dependencies to identify exact T001 schemas - expect a field-by-field implementation checklist",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Existing AlphaMill interfaces: Explore F002/F003/F008 readers, manifests, errors, and test conventions to reuse established contracts - expect an implementation map with no duplicated readers",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "T001 tests and source modules: Add failing contract/unit tests where absent, then implement snapshot and upstream contracts - expect requested behaviors passing",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Changed files: Run diagnostics, targ
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:33:49Z

- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/type-patterns.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/data-modeling.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/error-handling.md", "limit": 4000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/pyproject.toml", "limit": 4000})`

Step 1 of 4 is done. The frozen identity is now clear: snapshot identity contains semantic member summaries plus the combined universe/calendar digest, while all physical locations stay in provenance; next I’m tracing the concrete F002/F003/F008 DTOs and readers already present.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/type-patterns.md</path>
<type>file</type>
<content>
1: # Type Patterns
2: 
3: How to use Python's type system to catch bugs at check time, not runtime.
4: 
5: ---
6: 
7: ## NewType — distinct primitives
8: 
9: Same runtime type, different meaning. The type checker prevents mixing.
10: 
11: ```python
12: from typing import NewType
13: 
14: UserId = NewType("UserId", int)
15: MovieId = NewType("MovieId", int)
16: Email = NewType("Email", str)
17: Seconds = NewType("Seconds", float)
18: Milliseconds = NewType("Milliseconds", float)
19: 
20: def get_user(user_id: UserId) -> User: ...
21: def get_movie(movie_id: MovieId) -> Movie: ...
22: def sleep(duration: S
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/data-modeling.md</path>
<type>file</type>
<content>
1: # Data Modeling
2: 
3: Which container to use, how to structure data, and why frozen is the default.
4: 
5: ---
6: 
7: ## Decision flowchart
8: 
9: ```
10: Is it a fixed set of named constants?
11:   YES → StrEnum / IntEnum
12:   NO ↓
13: Is it just branding a primitive (int, str, float)?
14:   YES → NewType("X", base)
15:   NO ↓
16: Is it an interface / contract ("this thing can do X")?
17:   ├─ Shape only, no shared code → Protocol
18:   └─ Shared method implementation needed → ABC
19:   NO ↓
20: Does the data cross a trust boundary (user input, API, file, external DB)?
21:   YES → pydantic.BaseMode
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/error-handling.md</path>
<type>file</type>
<content>
1: # Error Handling
2: 
3: Typed errors, exhaustive matching, union returns, and resource safety.
4: 
5: ---
6: 
7: ## Typed errors — no bare strings
8: 
9: Error types carry structured data. Pattern matching works. Callers know exactly what can go wrong.
10: 
11: ```python
12: from dataclasses import dataclass
13: from typing import NewType
14: 
15: UserId = NewType("UserId", int)
16: 
17: @dataclass(frozen=True, slots=True)
18: class UserNotFoundError(Exception):
19:     user_id: UserId
20: 
21:     def __str__(self) -> str:  # REQUIRED — see note below
22:         return f"user {self.user_id} not fou
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/pyproject.toml</path>
<type>file</type>
<content>
1: [build-system]
2: requires = ["hatchling"]
3: build-backend = "hatchling.build"
4: 
5: [project]
6: name = "alphamill"
7: version = "0.1.0"
8: description = "以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行"
9: readme = "README.md"
10: requires-python = ">=3.11"
11: dependencies = [
12:   "ccxt>=4.4,<5",
13:   # F002 数据桥：Parquet 湖（写 PyArrow / 读 DuckDB）。运行时依赖同样锁范围，
14:   # 是否在范围内由 check_dep_pins 门禁强制（F002 spec 决策表：版本漂移显式改动）。
15:   "duckdb>=1.5,<2",
16:   "fastapi>=0.115,<1",
17:   "pandas>=2.2,<3",
18:   "psycopg2-binary>=2.9,<3",
19:   "pyarrow>=25,<26",
20:   "pydantic>=2.10,<3",
21:   "uvicorn>=0.34,<1",
22: ]
23: 
24: [project.optional-dependencies]
25: dev = [
26:   # 固定到范围：CI 每
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:34:03Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "T001 existing F002 DatasetVersion manifest/value_digest/latest reader, immutable symbol map artifact, F003 generation.run_completed generation.candidate_rejected operator capability registry pool FactorDef, F008 universe registry universe_at schema_version, existing errors/canonical JSON/atomic writer, and target tests test_research_snapshot.py test_f007_upstream_contracts.py. Return exact relevant source and tests.", "maxFil
…[truncated])`


> [reasoning] **Exploring codegraph queries for tests**

  <details><summary>tool output</summary>

  ```text
**Exploration: T001 existing F002 DatasetVersion manifest/value_digest/latest reader, immutable symbol map artifact, F003 generation.run_completed generation.candidate_rejected operator capability registry pool FactorDef, F008 universe registry universe_at schema_version, existing errors/canonical JSON/atomic writer, and target tests test_research_snapshot.py test_f007_upstream_contracts.py. Return exact relevant source and tests.**

Found 25 symbols across 3 files.

**Blast radius — what depends on these (update/verify before editing)**

- `Generation` (ml4t-zh/tests/test_superseded_members_registries.py:52) — 6 callers; tests: `ml4t-zh/tests/test_superseded_members_registries.py`, `deepseek-harness/packages/api/gateway/tests/control-retry.client.spec.ts`, `deepseek-harness/packages/api/g
…[truncated]
  ```
  </details>
