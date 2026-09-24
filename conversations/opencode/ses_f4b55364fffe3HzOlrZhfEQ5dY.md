---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4b55364fffe3HzOlrZhfEQ5dY"
title: "Phase 1 interface spec for F003 (@oracle subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-18T13:18:06Z"
updated_at: "2026-09-18T13:32:55Z"
tokens_input: 155215
tokens_output: 9936
cost: 0.0
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# Phase 1 interface spec for F003 (@oracle subagent)

## user · 2026-09-18T13:18:06Z

You are designing the Phase-1 module interfaces for feature F003 in the alphamill repo (branch `feat/F003-alphagen-vendor`, checked out at /home/georg/projects/alphamill). I need a DECISION-COMPLETE interface spec that I will hand verbatim to parallel implementer agents, so they produce mutually compatible modules without guessing.

READ THESE FIRST (authoritative):
- docs/features/0.2/F003-alphagen-vendor/design.md  (§2 module tree + boundaries, §3 data model/DTOs, §4 API/CLI/Event contracts, §5 workflow, §7 failure/security)
- docs/features/0.2/F003-alphagen-vendor/spec.md    (§4 requirements FR-001..FR-007, DR/TR/IR/NFR; §6 AC-001..AC-012)
- docs/features/0.2/F003-alphagen-vendor/tasks.md   (§1 T001-T004 prerequisites, §2 Phase 1 T005-T012, §4 dependencies)
- docs/alphamill-architecture.md §4.1 / §4.1.1 (FactorDef contract) and §7.1 (machine boundary)
- src/alphamill/data_bridge/{reader,manifest,symbol_map,registry,partitions,paths}.py (the F002 read API you must call; do NOT reimplement)

ESTABLISHED FACTS (already researched, trust these):
- Repo rules: src-layout; Python 3.11+; ruff E,F,I,B,UP,SIM line-length 100; NEW src files MUST stay ≤350 lines (enforced by tests/unit/test_f001_line_limit_exemptions.py which scans src/ for >350-line .py). Tests must land in tests/unit or tests/integration only (tools/verify.py collects only those). pytest config: `pythonpath=["." ,"src"]`, marker `integration`.
- Test style: plain module-level `def test_*` functions (NO test classes anywhere), no tests/unit/conftest.py (unit tests use bare `tmp_path`/`monkeypatch`), integration tests use `pytestmark = pytest.mark.integration` and an env gate where unset→skip, `ALPHAMILL_INTEGRATION=1` but capability missing→pytest.fail.
- NO FactorDef/HypothesisDef/FactorInput/FactorOutput type exists anywhere in src/ or tests/ today — they must be created.
- `src/alphamill/factor_factory/__init__.py` has no exports. Existing only: `factor_factory/bench/*` (F001-migrated scripts, not to be touched).
- F002 read API (verbatim from code):
  * `reader.read(dataset, data_version=None, start=None, end=None, pairs=None, as_of=None, allow_flagged=False, allow_event_time_only=False, lake_root=None) -> ReadResult` where `ReadResult(frame, dataset, data_version, value_digest, as_of, as_of_fidelity, flagged, symbol_map_digest)`. `end` EXCLUSIVE. `data_version=None` resolves latest-valid — ADR-0007 forbids canonical consumers from using that; F003 must pass explicit version.
  * `manifest.load_manifest(root, dataset, version) -> dict`; manifest fields include `status ∈ {"valid","invalid"}`, `value_digest`, `symbol_map_digest`, `partitions[]` each with `logical_partition_key, path, rows, time_min, time_max, row_digest, bytes, sha256`; `manifest.verify_value_digest(spec, manifest) -> str` recomputes and compares, raising ManifestIntegrityError; `manifest.list_versions(root, dataset)`; `manifest.latest_valid_version(root, dataset)`; `registry.require_dataset(name) -> DatasetSpec`.
  * `symbol_map.load_symbol_map(digest=None, lake_root=None) -> DataFrame` columns `(exchange, market_type, db_symbol, lake_pair, freqtrade_pair)`; `symbol_map.to_db_symbols(pairs, market_type, lake_root=None, digest=None)`.
  * Errors live in `data_bridge/errors.py` (InvalidVersionError, ManifestIntegrityError, VersionNotFoundError, InsufficientAsOfFidelityError).
- F003 design requires: run artifacts at `reports/generation/<run_id>/` with `run.json` (written LAST via tmp+fsync+rename), `factors/<factor_id>.json`, `pool.json` (completed only), `events.jsonl` (append-only, events `generation.run_completed` only for status=completed, `generation.candidate_rejected`). Four terminal run states `completed|rejected|failed|partial`, ALL write run.json; only `completed` is downstream-consumable.
- `FactorDef` executable object (architecture §4.1, verbatim): frozen dataclass with `factor_id, hypothesis_id, name, generator, scope: Literal["time_series","cross_sectional"], params: dict, compute: Callable[[FactorInput], FactorOutput], data_columns: list[str], meta: dict`. `expression` must NOT be a top-level field on the executable object — it lives in `meta["expression"]`.
- `FactorDef` disk DTO (design §3, schema_version:1): `factor_id, definition_digest, hypothesis_id, name, generator, generator_version, scope, expression, params, data_columns, feature_map_digest, run_id, created_at`. `definition_digest = sha256(canonical_json(dto minus factor_id/run_id/created_at))`. `factor_id = <generator>_<definition_digest[:12]>` (NO run seq). Conclusion fields (`ic, rank_ic, pnl, verdict, promoted`) are rejected by an explicit whitelist.
- design §3 line 110 says `factor_store.load()` rebuilds `compute` from `expression` + a digest-verified `feature_map` via `alphagen_adapter`. BUT tasks.md puts `alphagen_adapter` (T021) in Phase 3, while `factor_store` (T007, with a test that must pass in Phase 1) is Phase 1. This ordering tension is the core thing I need you to resolve cleanly.

THE PHASE-1 TASK SET (verbatim intent, must all be satisfiable by the interface spec):
- T001: freeze/validate the F008 universe-台账 consumption contract (load by digest, `universe_at(T)`, `schema_version`) OR, since F008 is not landed, an equivalent explicit-universe fixture; verify tests/unit/test_f003_binding.py
- T002: fix the binding file format; verify a target dataset's valid version + value_digest parse via the F002 reader; verify tests/unit/test_f003_binding.py
- T005: `Generator` protocol + `GenerationRequest/Result/Counts`, including conclusion-field whitelist rejection; verify tests/unit/test_f003_generator_contract.py
- T006 [P]: `HypothesisDef` schema + catalog (with `mechanism`, `applicable_state` default), built-in `mechanism_unknown`; verify tests/unit/test_f003_hypotheses.py
- T007: FactorDef canonical JSON (schema_version), `definition_digest`, `factor_id`, `factor_store` read/write, and `load()` rebuilding an executable `compute` from expression + feature_map; verify tests/unit/test_f003_factor_store.py
- T008: `run_store` — GenerationRun manifest atomic write (run.json last; includes hostname/device/vram_limit_gb/universe) + append-only events.jsonl; verify tests/unit/test_f003_run_store.py
- T009: `binding.py` — parse the two binding forms, per-dataset value_digest validation, immediate reject on invalid; verify tests/unit/test_f003_binding.py
- T010: manual crypto-native seed backend (funding carry, basis, OI change, cross-sectional momentum, volatility), each bound to a real HypothesisDef; verify tests/unit/test_f003_manual_seeds.py
- T011: `egress_guard` + write-path whitelist (only `reports/generation/<run_id>/`), both fail-closed; verify tests/integration/test_f003_boundaries.py
- T012: CLI `seed`/`show` subcommands, non-zero reject on missing binding, reject unknown schema_version; verify tests/unit/test_f003_cli_contract.py
Dependency edges stated in tasks.md §4: T002→T009; T005→T010; T005→T013; T006→T010; T007→T008→T029; T009→T020; T011/T020/T026/T027/T028→T031; T005/T010/T012/T013/T021/T022→T030.

WHAT I NEED FROM YOU (be decision-complete, no options):
1. **Final Phase-1 file/module layout** under `src/alphamill/factor_factory/`: every new file path, and which module OWNS the executable `FactorDef`, `FactorInput`, `FactorOutput`, `GenerationRequest/Result/Counts`, `Window`, `SnapshotBinding`, `HypothesisDef`, the FactorDef disk DTO, and the run manifest DTO. Explicitly avoid circular imports and justify placement against design §2's tree (design didn't place the executable FactorDef module — decide whether to add a module or reuse `generators/base.py`, and say which).
2. **Resolve the compiler-ordering tension**: exactly how `factor_store.load()` rebuilds `compute` in Phase 1 given `alphagen_adapter` is Phase 3. Specify the mechanism (injected compiler / registry keyed by generator / minimal phase-1 compiler) and the exact signature. It must (a) work for T007's Phase-1 test, (b) let T021 plug in `generator="alphagen"` later without changing `load()`'s signature, (c) let T026's `pool` recompute later, (d) raise a clear, typed error (not silent) for a generator with no registered compiler.
3. **Exact signatures** (verbatim Python) for every Phase-1 public callable/class, including constructors, so parallel implementers can code against them: `generators/base.py`, `hypotheses/schema.py`, `hypotheses/catalog.py`, `registry/factor_store.py`, `registry/run_store.py`, `generators/binding.py`, `generators/egress_guard.py`, `cli.py` entry point. Include the canonical-JSON helper contract (key ordering, excluded fields) and the `egress_guard` mechanism (how socket is patched, how fail-closed is enforced) and the write-path whitelist mechanism.
4. **Build order + parallelization groups** for T001,T002,T005-T012 given the dependency edges, listing which tasks can run concurrently with zero shared files.
5. **Any interface decisions the design leaves ambiguous that would otherwise cause two implementers to diverge** — resolve each with a single decision and one-line rationale. Examples to address: is `SnapshotBinding` a dataclass or a parsed-dict wrapper; how is `feature_map` represented and digest-verified; how do manual seeds express a machine-loadable `expression` (DSL string? builder call?) so `load()` can rebuild compute; what `Window` contains and the `default_1h_2y` preset values; how `GenerationCounts` names the four rejection reason codes; whether the FactorDef DTO↔executable conversion is one module's job and its name.

Constraints on your answer: read the actual files (don't guess), respect the ≤350-line rule (propose splitting files where needed), and prefer the minimum interface surface that satisfies the ACs. Do NOT write implementation code beyond signatures/dataclasses/type aliases and short contract notes. Output a single structured spec I can paste into implementer prompts.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T13:18:06Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "F003 Phase 1 interface context: src/alphamill/data_bridge/reader.py manifest.py symbol_map.py registry.py partitions.py paths.py; existing factor_factory package and CLI patterns; exact public signatures, errors, path handling, canonical JSON patterns", "maxFiles": 12})`


> [reasoning] **Planning codegraph exploration**

  <details><summary>tool output</summary>

  ```text
**Exploration: F003 Phase 1 interface context: src/alphamill/data_bridge/reader.py manifest.py symbol_map.py registry.py partitions.py paths.py; existing factor_factory package and CLI patterns; exact public signatures, errors, path handling, canonical JSON patterns**

Found 17 symbols across 1 file.

**Blast radius — what depends on these (update/verify before editing)**

- `read` (alphamill/src/alphamill/data_bridge/reader.py:97) — 17 callers; tests: `alphamill/tests/integration/test_f002_reader.py`, `alphamill/tests/integration/test_f002_export_reconcile.py`, `alphamill/tests/integration/test_f002_revision.py`, `alphamill/tests/unit/test_f002_reader_contract.py`
- `handle` (personahub/server/src/services/run-escalation-handler.ts:18) — 1 caller in `personahub/server/src/services/run-dis
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:18:25Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "limit": 1200})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "limit": 1200})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md", "limit": 1200})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 80, "limit": 340})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md", "limit": 500})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill/src/alphamill", "pattern": "factor_factory/**/*.py"})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill/src/alphamill/data_bridge", "pattern": "*.py"})`


> [reasoning] **Planning precise project file indexing**

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
5: status: developing
6: branch: feat/F003-alphagen-vendor
7: gate_version: 1
8: related_features: [F001, F002, F007, F008]
9: topics: [factor-factory, alphagen, vendor, generators, m2]
10: doc_kind: spec
11: created: 2026-09-14
12: updated: 2026-09-14
13: ---
14: 
15: # F003：AlphaGen vendor 与可插拔生成器平面
16: 
17: > Owner: Georg | Target: v0.2.x
18: 
19: ## 0. 来源与意图
20: 
21: - **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册）、FR2.2（可插拔生成器）、FR2.3（目标对齐）、FR2.4（纯度与能力边界）、FR2.6（探索组合）；目标 G3；里程碑 M2
22: - **架构来源**：`docs/alphamill-architecture.md` §三（`factor_factory/` 目录分工）、§4.0（闭环核心对象）、§4.1（FactorDef 契约）、§4.1.1（AlphaGen 适配契约与截面边界）、§7.1
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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
80:         POST -->|"人审后"| HYP
81:     end
82: 
83:     subgraph EVIDENCE["证据与治理面（确定性裁决）"]
84:         METHOD["方法论门<br/>label endpoint · PIT · train-only fit"]
85:         PURITY["AST 纯度门"]
86:         BENCH["因子评测<br/>IC/收益 · 成本 · 去重 · 多重检验"]
87:         SELECT["选择期筛选"]
88:         GATE["冻结组合的 90 天留出<br/>→ 永久隔离最终确认"]
89:         LEDGER["canonical cohort/population<br/>实验与留出台账"]
90:         SYNTH["synthesis_report<br/>漏斗 · 五阶段损失 · 约束"]
91:         METHOD --> PURITY --> BENCH --> SELECT
92:         LEDGER --> SYNTH
93:         LEDGER -.-> PURITY
94:         LEDGER -.-> BENCH
95:         LEDGER -.-> GATE
96:         LEDGER -.-> SELECT
97:     end
98: 
99:     subgraph TRADE["策略与执行面"]
100:  
…[truncated]
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

  <details><summary>tool output</summary>

  ```text
Found 6 file(s)

/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/kronos_rankic_eval.py
/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/kronos_ic_decay_eval.py
/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/independent_cross_backtest.py
/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/__init__.py
/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/train_low_frequency_walk_forward_baselines.py
/home/georg/projects/alphamill/src/alphamill/factor_factory/__init__.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 22 file(s)

/home/georg/projects/alphamill/src/alphamill/data_bridge/partitions.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/reader.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/symbol_map.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/paths.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/reconcile.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/registry.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest_validation.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/digest.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/exporter.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/export_policy.py
/home/geo
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:18:36Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/reader.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest.py", "limit": 600})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/symbol_map.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/registry.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/partitions.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/paths.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/errors.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/data_bridge/cli.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/pyproject.toml", "limit": 400})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "pattern": "^### 7\\.1|^## 七|机器边界|GPU 槽位", "output_mode": "content", "head_limit": 20})`


> [reasoning] **Planning detailed module and CLI inspection**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/reader.py</path>
<type>file</type>
<content>
1: """DuckDB 研究只读取数入口（FR-003，NFR-001 零写路径）。
2: 
3: - 只按 manifest `partitions` 清单构造输入路径，**从不扫描目录**（F002-R2-02）；
4: - 返回数据前先跑清单完整性校验（存在/字节数/sha256）与 `value_digest` 重算，
5:   任一不符抛 `ManifestIntegrityError`（fail-closed，NFR-002 的技术保证）；
6: - `as_of=T` 同时施加 `event_time <= T` **与** `available_at <= T`（双时间轴，
7:   design §3）；`as_of_fidelity=event_time_only` 的 dataset 默认抛
8:   `InsufficientAsOfFidelityError`，显式 `allow_event_time_only=True` 才放行；
9: - 事后回填标签（`realized_return_60m`）在其可用时间（`evaluated_at`）晚于 T
10:   时**置 NULL 而非丢行**——丢行会让样本集随 T 变化；
11: - 带未解决质量旗的分区默认拒绝，`allow_flagged=True` 显式豁免并随附清单；
12: - 时间过滤语义：`start` 含、`end` 不含（半开区间 [start, end)）。
13: """
14: 
15: from __future__ import annotation
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest.py</path>
<type>file</type>
<content>
1: """manifest 契约读写、data_version 排序、完整性与增量合成（design §3/§4，架构 §4.4）。
2: 
3: 关键不变量：
4: - `partitions` 是必填的版本身份；reader 只按清单构造输入路径，从不扫描目录
5:   （F002-R2-02）——完整性校验逐项验存在/字节数/sha256，任一不符即
6:   `ManifestIntegrityError`，不要求目录全集相等（`.rN` 共享模型）。
7: - `value_digest` 是 DatasetVersion 的语义根摘要：只含 dataset、registry 投影与
8:   分区级 (key, rows, bounds, row_digest)，不含物理 path/codec/bytes/sha256/
9:   exported_at（F002-D011）。
10: - manifest 合成是**累计完整快照**而非一日 delta：增量从上一 valid 清单继承基线，
11:   full 用基线复用未变文件但按当前源库组成版本；本轮分区按逻辑分区键替换/追加，
12:   `rows`/`pairs`/quality 重算，`skipped` 走同样的继承/替换（F002-R2-03/R3-03）。
13: """
14: 
15: from __future__ import annotations
16: 
17: import errno
18: import hashlib
19: import json
2
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/symbol_map.py</path>
<type>file</type>
<content>
1: """symbol_map：湖内 pair ↔ Freqtrade pair 的映射与内容寻址发布（design §4）。
2: 
3: 映射键冻结为 **(exchange, market_type, db_symbol)**（F002-D010）——库内
4: `DISTINCT symbol` 不足以无损推导（spot 与 perp 的 `BTC/USDT` 是不同标的）。
5: 输出格式冻结：spot `BTC/USDT → BTC-USDT`（Freqtrade `BTC/USDT`）、perp
6: `BTC/USDT[:USDT] → BTC-USDT-PERP`（Freqtrade `BTC/USDT:USDT`）。任意两行推导
7: 出相同 lake_pair 即为碰撞，导出直接失败（`SymbolCollisionError`）。
8: 
9: current 副本位于湖元数据目录，不改写源码树；它不是可复现身份：canonical CSV
10: （五列排序、UTF-8、LF、固定表头）原子发布到
11: `lake/_metadata/symbol_maps/<digest>.csv`，digest 为 canonical bytes 的
12: SHA-256；已有同 digest 文件必须逐字节一致。ResearchSnapshot 只引用显式 digest。
13: """
14: 
15: from __future__ import annotations
16: 
17: import csv
18: impor
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/registry.py</path>
<type>file</type>
<content>
1: """Dataset registry——F002-D007 / R2-04 冻结的只读白名单（design §3）。
2: 
3: `export_dataset()` 与 `read()` 的 `dataset` 参数只接受 `DATASETS` 中的键，
4: 其余一律抛 `UnknownDatasetError`。投影列逐一枚举、顺序即编码顺序——摘要的
5: 稳定性取决于输入是否被完全规范化，禁止用「等」占位。
6: 
7: 类型只有五种：`timestamptz` / `text` / `double` / `jsonb` / NULL（NULL 的
8: 哨兵编码见 digest.py）。
9: """
10: 
11: from __future__ import annotations
12: 
13: from dataclasses import dataclass, field
14: from types import MappingProxyType
15: 
16: from alphamill.data_bridge.errors import UnknownDatasetError
17: 
18: TIMESTAMPTZ = "timestamptz"
19: TEXT = "text"
20: DOUBLE = "double"
21: JSONB = "jsonb"
22: 
23: AS_OF_BITEMPORAL = "bitemporal"
24: AS_OF_EVENT_TIME_ONLY = "even
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/partitions.py</path>
<type>file</type>
<content>
1: """分区文件层操作：单元格发现、`.rN` 写入、空单元格判定、质量标记（design §3）。
2: 
3: 本模块只做「源行集 → 湖分区文件」的机械转换与窗口内的网格判定；导出编排
4: （事务、基线继承、manifest 合成与发布）在 exporter.py。分区写入永不覆盖：
5: 内容变化写 `.rN+1`，序号由盘上现有最大值推导，孤儿文件不阻塞重跑。
6: """
7: 
8: from __future__ import annotations
9: 
10: import datetime as dt
11: import re
12: from collections import defaultdict
13: from pathlib import Path
14: from typing import Any
15: 
16: import pyarrow as pa
17: import pyarrow.parquet as pq
18: 
19: from alphamill.data_bridge import manifest as mf
20: from alphamill.data_bridge import paths, reconcile, registry, symbol_map
21: from alphamill.data_bridge.digest import canonical_json_text, canonical_row_bytes, row_digest
22: from alph
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/paths.py</path>
<type>file</type>
<content>
1: """湖根路径与目录布局约定（design §3）。
2: 
3: 唯一入口 `lake_root()`：默认仓库根 `lake/`，可用环境变量 `ALPHAMILL_LAKE_DIR`
4: 覆盖（测试与多环境部署用）。所有模块经此处取湖路径，不各自硬编码。
5: """
6: 
7: from __future__ import annotations
8: 
9: import os
10: from pathlib import Path, PureWindowsPath
11: 
12: from alphamill.data_bridge.errors import DataBridgeError
13: 
14: REPO_ROOT = Path(__file__).resolve().parents[3]
15: 
16: 
17: def lake_root() -> Path:
18:     override = os.getenv("ALPHAMILL_LAKE_DIR", "").strip()
19:     if override:
20:         return Path(override).expanduser().resolve()
21:     return (REPO_ROOT / "lake").resolve()
22: 
23: 
24: def manifests_dir(root: Path, dataset: str) -> Path:
25:     return root / "_manife
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/errors.py</path>
<type>file</type>
<content>
1: """F002 数据桥异常契约（design §4）。
2: 
3: 取数与导出对以下任一情形一律抛错，不降级为警告（D4 数据红线；本 feature
4: 无 SOP 所述的「安全校验降级声明」出口）。
5: """
6: 
7: 
8: class DataBridgeError(Exception):
9:     """数据桥异常基类。"""
10: 
11: 
12: class UnknownDatasetError(DataBridgeError):
13:     """dataset 不在 registry 白名单中。"""
14: 
15: 
16: class VersionNotFoundError(DataBridgeError):
17:     """请求的 data_version manifest 不存在，或不存在任何 valid 版本。"""
18: 
19: 
20: class InvalidVersionError(DataBridgeError):
21:     """请求的 data_version 已被标记 invalid，消费端拒绝读取。"""
22: 
23: 
24: class ManifestIntegrityError(DataBridgeError):
25:     """manifest 清单内文件缺失、字节数或 sha256 不符，或 value_digest 缺失/重算不符。
26: 
27:     不含「目录里存在本版本未引用的文件」——`.rN` 共享模型下那是其他版本的
28
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/data_bridge/cli.py</path>
<type>file</type>
<content>
1: """导出 CLI——`python -m alphamill.data_bridge.exporter`（design §5 退出码契约）。
2: 
3: 退出码：0 = 成功（含 no-op）；1 = 可重试的瞬时故障（库连接失败、IO 错误、
4: staging 写入中断）；2 = 不可重试的数据裁决（对账失败→版本已标 invalid、
5: manifest 完整性失败、registry/symbol 校验失败）。systemd unit 以
6: `RestartPreventExitStatus=2` 锁定「对账失败不重试」。
7: """
8: 
9: from __future__ import annotations
10: 
11: import argparse
12: import json
13: import logging
14: import sys
15: 
16: import psycopg2
17: 
18: from alphamill.data_bridge import registry
19: from alphamill.data_bridge.errors import DataBridgeError
20: 
21: EXIT_OK = 0
22: EXIT_TRANSIENT = 1
23: EXIT_FATAL = 2
24: 
25: 
26: def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
27:     p
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/pyproject.toml</path>
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
26:   # 固定到范围：CI 每次 `pip inst
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 2 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  516: ## 七、部署拓扑
  561: ### 7.1 机器边界与单卡 GPU 时段调度
  ```
  </details>

## assistant · 2026-09-18T13:18:50Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 516, "limit": 110})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion", "pattern": "*.md"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion", "include": "*.md", "pattern": "universe_at|schema_version|digest|artifact", "output_mode": "content", "head_limit": 120})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill/tests", "pattern": "**/test_f003*.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/__init__.py", "limit": 100})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md", "pattern": "ResearchSnapshot|members|cutoff_time|schema_version|universe_calendar_digest|provenance", "output_mode": "content", "head_limit": 120})`


> [reasoning] **Analyzing F008 design and architecture**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
516: ## 七、部署拓扑
517: 
518: ```mermaid
519: flowchart LR
520:     subgraph HOST["执行机（当前 qiaozhi-lt · RTX 4060 Laptop 8GB；迁移目标 qiaozhi-lab · RTX 5070 Ti 16GB）"]
521:         subgraph DOCKER["docker-compose（自 quant-crypto 迁入）"]
522:             TS[(TimescaleDB)]
523:             FTD[Freqtrade dry-run]
524:             GRAF[Grafana<br/>退守平台观测与告警]
525:             PROM[Prometheus]
526:             API[统一呈现后端<br/>只读 API + SPA 托管<br/>F005+ · ADR-0005]
527:         end
528:         subgraph NIGHT["夜间批处理（宿主机/独立容器）"]
529:             EXPORT[data_bridge 导出]
530:             MINE[生成器挖掘<br/>GPU 夜槽 §7.1]
531:             BENCHX[评测台批量]
532:             GATES[门禁回测]
533:             PORT[组合门与构建]
534:      
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md
/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md
/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 43 match(es) in 3 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md
  24: - **ADR / 上游 Contract**：ADR-0007（ResearchSnapshot 绑定 universe/calendar artifact）、ADR-0003（门禁不降级）、ADR-0001（扩容是产出质量前提）；F002 的 `symbol_map` 内容寻址发布范式、dataset registry、manifest 与 reader 契约
  28: - **不改 `F002` 已冻结的语义**：导出、对账、manifest、修订与失效规则一律沿用，本 feature 只扩 pair 集合并新增元数据 artifact；
  35: 四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。发现从 Binance 公开行情按口径筛候选；人工确认后冻结为内容寻址的 `UniverseDef`；回填复用 F001 的 `historical_backfill.py`，外面套一层可续跑的批次编排；每个 pair 回填完成后跑质量门（复用 `tools/f001_backfill_report.py` 的口径，参数化到多 pair）；过门的 pair 写入联机库的 `universe_membership` 台账并进 F002 导出清单，台账再以 `symbol_map` 同构的方式发布为湖内内容寻址 artifact。
  39: - 存储 / Migration：新增 TimescaleDB 表 `universe_membership`（只追加）；新增湖元数据目录 `lake/_metadata
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 2 file(s)

/home/georg/projects/alphamill/tests/unit/test_f003_lifecycle_contract_config.py
/home/georg/projects/alphamill/tests/integration/test_f003_kronos_lifecycle.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/__init__.py</path>
<type>file</type>
<content>
1: """Factor generation and evaluation components."""

(End of file - total 1 lines)
</content>
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 25 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md
  4: - 状态：Accepted（2026-09-18 修订：universe/calendar 拆为两个独立 artifact 引用并冻结 `universe_calendar_digest` 组合公式，见文末「修订记录」）
  15: 用各 manifest 的 `exported_at` 临时聚合也不足以解决问题。`exported_at` 是写出 provenance，
  27: 2. **新增不可变 `ResearchSnapshot`**：它是对多个有效 DatasetVersion 的内容寻址引用集合，
  31: ResearchSnapshot = {
  32: schema_version,
  34: cutoff_time,
  35: members: {
  42: universe_calendar_digest,
  43: provenance: {created_at, artifact_path, member_manifest_paths,
  48: `universe_calendar_digest` 由两个独立 artifact 的 digest 按冻结的组合公式导出：
  53: `universe_calendar_digest`（它已确定性地决定 digest 对），不重复哈希两个成员 digest。
  55: `members` 只包含本次研究声明的必需数据集，不要求每个快照固定包含湖内全部 dataset。
  56: 3. **身份只哈希语义字段**：`snapshot_id` 由 `
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:19:06Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md", "offset": 20, "limit": 100})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md", "offset": 88, "limit": 50})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_f003_lifecycle_contract_config.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/integration/test_f003_kronos_lifecycle.py", "limit": 500})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill", "include": "*.py", "pattern": "canonical_json|json\\.dumps\\(.*sort_keys=True|os\\.replace\\(tmp|fsync", "output_mode": "content", "head_limit": 120})`


> [reasoning] **Reviewing ADR and F008 schema sections**

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

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/design.md</path>
<type>file</type>
<content>
88: `criteria` 字段（Q-001 裁决值）：
89: 
90: | 字段 | 值 | 说明 |
91: |---|---|---|
92: | `exchange` / `market_type` | `binance` / `perp` | F001 事故后的数据路线 |
93: | `turnover_lookback_days` | 90 | 成交额统计窗口 |
94: | `turnover_rank_top_n` | 40 | **按排名取前 N，不设绝对金额阈值**——绝对阈值随市场周期漂移，产出规模不可控 |
95: | `min_listed_days` | 180 | 不要求满窗：要求上线满 2 年等于只选活过两年的币，是幸存者偏差的另一张脸 |
96: | `exclude_rules` | 稳定币对 / 杠杆代币 / 指数篮子类合约 | 横截面 rank 里的常数噪声与结构性重复 |
97: 
98: 批次：`candidates` 按成交额排名有序，批 1 取前 30（含现有 6 对），批 2 取第 31–40。批次只影响回填与准入的时序，不影响 `universe_id`——冻结的是完整的 40 对定义。
99: 
100: **湖内 artifact**：`lake/_metadata/universes/<digest>.csv`，canonical 格式冻结（固定列序、按 `(lake_pair, valid_from)` 排序、UTF-8、LF、固定表头），digest 为 cano
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_f003_lifecycle_contract_config.py</path>
<type>file</type>
<content>
1: """F003-R4-002 锁：生命周期契约测试模块不得有 mock 默认地址。
2: 
3: 契约目标是 `kronos-signal-real`（执行机 GPU 实例）；`KRONOS_CONTROL_URL` 未设时
4: 模块级 `CONTROL_URL` 必须为空串并使用例 skip——绝不回落到 mock 的 8001（XPASS
5: 转正警报因此只可能打在真实实例上）。直接以文件位置加载被测模块，避免受本进程
6: 已导入副本或收集期环境的影响。
7: """
8: 
9: from __future__ import annotations
10: 
11: import importlib.util
12: import pathlib
13: 
14: import pytest
15: 
16: MODULE = (
17:     pathlib.Path(__file__).resolve().parents[1] / "integration" / "test_f003_kronos_lifecycle.py"
18: )
19: 
20: 
21: def _load_fresh():
22:     spec = importlib.util.spec_from_file_location("_f003_lifecycle_under_test", MODULE)
23:     mod = importlib.util.module_from_spec(spec)
24:     spec.
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/integration/test_f003_kronos_lifecycle.py</path>
<type>file</type>
<content>
1: """F003 契约测试：Kronos 服务生命周期控制面（架构 §7.1，客户端可见行为）。
2: 
3: **契约目标是真实推理服务 `kronos-signal-real`（执行机 GPU 实例）**——夜槽卸载为的是
4: 释放 GPU 显存，mock 服务（`kronos-signal`，8001，无 torch）无显存可释放，不是本契约的
5: 对象，也不是合法的测试目标（R4-002）。服务端端点（`GET /lifecycle/status`、
6: `POST /lifecycle/stop`、`POST /lifecycle/restore`）属待分配 feature（BACKLOG「Kronos
7: 服务生命周期端点」）——本文件以 `xfail(strict=True)` 显式声明当前「服务端未实现」的
8: 先红态：端点落地后 XPASS 即红，落地 feature 必须移除本标记并补 `E_BUSY` / `E_TIMEOUT`
9: 错误路径用例（F004 tasks §5）。
10: 
11: 开关纪律（双保险，缺一即 skip）：
12: - 未设 `ALPHAMILL_INTEGRATION` → skip（与 F004 容器套件同纪律）；
13: - 未设 `KRONOS_CONTROL_URL` → skip（**无默认地址**：契约目标必须显式指定，避免默认
14:   打到 mock 的 404 上制造假红/假绿；T033 的 verify 命令给出执行机取值）。
15: 设了以后失败就
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 20 match(es) in 7 file(s)

/home/georg/projects/alphamill/tools/check_doc_consistency.py
  64: (ARCH, 'sha256(canonical_json({"universe": <universe_digest>,'),
  579: (ADR7, 'sha256(canonical_json({"universe"'),
  580: (F007_SPEC, 'sha256(canonical_json({"universe"'),
  581: (F007_DESIGN, 'sha256(canonical_json({"universe"'),
  582: (DESIGN, "sha256(canonical_json"),

/home/georg/projects/alphamill/src/alphamill/data_bridge/manifest_validation.py
  25: return json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

/home/georg/projects/alphamill/src/alphamill/data_bridge/partitions.py
  21: from alphamill.data_bridge.digest import canonical_json_text, canonical_row_bytes, row_digest
  99: None if v is None else canonical_json_text(v, parse_text=False) for v in valu
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:19:18Z

- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs", "include": "*.md", "pattern": "expected_holding_period|cost_sensitivity|mechanism_unknown|HypothesisDef", "output_mode": "content", "head_limit": 120})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill", "include": "*.py", "pattern": "argparse\\.ArgumentParser|\\[project\\.scripts\\]|entry_points", "output_mode": "content", "head_limit": 100})`


> [reasoning] **Designing factor.py for core models**

> [reasoning] **Planning modular registry and loading interfaces**

> [reasoning] **Ensuring convenient load function signature**

> [reasoning] **Refactoring compiler registry initialization**

> [reasoning] **Designing centralized compiler registry and lazy loading**

> [reasoning] **Isolating default registry from imports**

> [reasoning] **Designing explicit compiler_registry injection**

> [reasoning] **Finalizing feature map storage and digest handling**

> [reasoning] **Deciding digest format conventions**

> [reasoning] **Defining expression tokens and data types**

> [reasoning] **Designing GenerationCounts and RejectionCounts dataclasses**

> [reasoning] **Implementing GenerationResult.from_mapping and HypothesisCatalog interface**

> [reasoning] **Designing immutable SnapshotBinding dataclasses**

> [reasoning] **Defining SnapshotBinding parsing and validation protocols**

> [reasoning] **Clarifying digest verification during read call**

> [reasoning] **Defining UniverseLoader protocol and artifact**

> [reasoning] **Designing UniverseProvider and JSON fixtures**

> [reasoning] **Specifying universe loader and window binding**

> [reasoning] **Defining exact GenerationRun schema**

> [reasoning] **Assessing run_store dependencies and functions**

> [reasoning] **Designing atomic run finalization and factor store schema**

> [reasoning] **Defining FactorDefDTO and CompileContext**

> [reasoning] **Designing CompileRequest and CompilerRegistry structure**

> [reasoning] **Reviewing feature map validation and save logic**

> [reasoning] **Refining factor DTO serialization and identity digest**

> [reasoning] **Defining DTO identity fields**

> [reasoning] **Planning factor load with hypothesis catalog**

> [reasoning] **Designing CLI seed command with default quota**

> [reasoning] **Refining CLI options and designing network socket guard**

> [reasoning] **Designing egress guard context manager**

> [reasoning] **Planning write-path whitelist with audit hook**

> [reasoning] **Designing write guard with audit hooks**

> [reasoning] **Planning test task sequencing and dependencies**

> [reasoning] **Defining test execution sequencing and ownership**

> [reasoning] **Assigning package scaffold to T005**

> [reasoning] **Defining module ownership and export limits**

> [reasoning] **Defining DTO constructor standards**

> [reasoning] **Designing FactorStore path and DTO handling**

> [reasoning] **Designing FactorDefinition identity function**

> [reasoning] **Defining factor metadata and save process**

> [reasoning] **Designing run ID generation and validation**

> [reasoning] **Refining rejected run DTO with nullable fields**

> [reasoning] **Refining factor ID search across runs**

> [reasoning] **Designing factor artifact selection and validation**

> [reasoning] **Clarifying hypothesis quota behavior**

> [reasoning] **Designing validation and error handling structure**

> [reasoning] **Preventing import collisions**

> [reasoning] **Planning detailed project change specification**

> [reasoning] **Mapping task directory and package ownership**

> [reasoning] **Assigning binding file creation to tasks**

> [reasoning] **Refining task dependency graph**

> [reasoning] **Designing concurrency execution phases**

> [reasoning] **Designing factor_store load enforcement**

> [reasoning] **Refining run.json and config canonicalization**

> [reasoning] **Defining strict schema parsing rules**

> [reasoning] **Planning output structure and content**

> [reasoning] **Designing compiler registry and load signatures**

> [reasoning] **Reviewing factor and binding validation details**

> [reasoning] **Defining generation boundary and write guard behavior**


> [reasoning] **Designing core factor module layout**

> [reasoning] **Finalizing type aliases and window contracts**

> [reasoning] **Planning schema parser and compiler registry structure**

> [reasoning] **Designing explicit compiler registry with defaults**

> [reasoning] **Designing factor store file structure**

> [reasoning] **Defining feature map loading and compiler interfaces**

> [reasoning] **Resolving circular imports by isolating CompileContext**

> [reasoning] **Defining canonical digest and JSON contract**

> [reasoning] **Resolving DTO definition_digest exclusion**

> [reasoning] **Designing expression token sequence format**

> [reasoning] **Designing feature map DTO and digest**

> [reasoning] **Planning factor DTO build and serialization API**

> [reasoning] **Renaming factor compilation function**

> [reasoning] **Designing lazy compiler registry imports**

> [reasoning] **Introducing configurable compiler registry parameter**

> [reasoning] **Refining compiler registration with dependency injection**

> [reasoning] **Implementing lazy compiler module loading**

> [reasoning] **Reorganizing compiler ownership between T007 and T010**

> [reasoning] **Designing GenerationRun dataclass and SnapshotBinding union**

> [reasoning] **Defining SnapshotBinding type alias and validation rules**

> [reasoning] **Planning explicit snapshot binding validation steps**

> [reasoning] **Designing explicit universe fixture artifact shape**

> [reasoning] **Defining Phase1 fixture format**

> [reasoning] **Planning universe calendar validation and run storage**

> [reasoning] **Designing atomic run file writes**

> [reasoning] **Implementing run finalization and egress guard**

> [reasoning] **Designing process-level write path guard**

> [reasoning] **Defining strict write path validation logic**

> [reasoning] **Designing CLI argument parsing**

> [reasoning] **Resolving factor ID ambiguity in show command**

> [reasoning] **Confirming data types for schema**

  <details><summary>tool output</summary>

  ```text
Found 20 match(es) in 7 file(s)

/home/georg/projects/alphamill/docs/alphamill-prd.md
  154: generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  50: │   ├── schema.py             # HypothesisDef 结构与校验（DR-003）
  51: │   └── catalog.py            # 假设注册；mechanism_unknown 内置项
  113: **HypothesisDef**：`hypothesis_id` / `mechanism`（经济动机与作用机制）/ `data_columns` / `applicable_state`（适用状态/regime；catalog 与自动候选给显式默认值 `unspecified`，不隐式留空）/ `expected_holding_period` / `cost_sensitivity` / `source` / `generation`。内置 `mechanism_unknown` 条目供自动候选绑定，并在 FactorDef 上如实标记（PRD FR2.1）。
  248: | `AC-009` | integration | `tests/integration/test_f003_generation_run.py` | 同 `(seed, binding, code_digest, config_digest)` 重跑 factor_id 集合与池成
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 11 match(es) in 11 file(s)

/home/georg/projects/alphamill/scripts/discover_okx_swap_universe.py
  16: parser = argparse.ArgumentParser(

/home/georg/projects/alphamill/tools/f001_backfill_report.py
  389: parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])

/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/kronos_rankic_eval.py
  99: parser = argparse.ArgumentParser(

/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/kronos_ic_decay_eval.py
  123: parser = argparse.ArgumentParser(

/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/independent_cross_backtest.py
  23: parser = argparse.ArgumentParser(

/home/georg/projects/alphamill/src/alphamill/factor_factory/bench/train_low_frequency_walk_forward_baselines.py
  18: p
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:27:59Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-prd.md", "offset": 142, "limit": 20})`


> [reasoning] **Identifying lineage string type**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-prd.md</path>
<type>file</type>
<content>
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
154:   generation；只有表达式没有假设的自动候选必须标记 `mechanism_unknown`。
155: - **FR2.2 可插拔生成器**：至少包含 AlphaGen RL 主引擎与 GP/表达
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T13:28:14Z


> [reasoning] **Defining hypothesis ID fields and formats**

> [reasoning] **Designing hypothesis catalog integration**

> [reasoning] **Refining factor save and load design**

> [reasoning] **Planning module splitting and error handling**

> [reasoning] **Designing test build order with waves**

> [reasoning] **Assigning package init ownership and task dependencies**

> [reasoning] **Defining interface including ConfigRef**

> [reasoning] **Summarizing data model structures**

> [reasoning] **Designing event idempotency and config exclusions**

> [reasoning] **Clarifying data reader usage with empty pairs**

> [reasoning] **Verifying manifest and schema validation logic**

> [reasoning] **Adding required run manifest argument**

> [reasoning] **Defining exit codes and validation guards**

> [reasoning] **Resolving run ID generation ownership**

> [reasoning] **Confirming run ID exclusion from request design**

> [reasoning] **Deciding run_id handling strategy**

> [reasoning] **Evaluating run_id injection approaches**

> [reasoning] **Proposing GenerationRunner with run_id guard**

> [reasoning] **Exploring deterministic run_id generation**

> [reasoning] **Defining Phase1 write guard with preallocated run_id**

> [reasoning] **Amending GenerationRequest with provisional run_id**

> [reasoning] **Designing run-scoped generator construction**

> [reasoning] **Defining run ID injection and write guard scope**

> [reasoning] **Adding allow_noncompleted flag to load**

> [reasoning] **Adjusting load method with require_completed flag**

> [reasoning] **Designing precise frozen dataclasses for Factor DTOs**

> [reasoning] **Refining dataclass fields with kw_only defaults**

> [reasoning] **Refactoring compiler registration for explicit imports**

> [reasoning] **Defining public compiler factory and refining factor serialization**

> [reasoning] **Defining ValidatedBinding dataclass**

> [reasoning] **Finalizing SnapshotBinding design**

> [reasoning] **Listing test file mappings**
**Bottom Line**

Add a root-level `factor.py`; do not put executable `FactorDef` in `generators/base.py`. Resolve the Phase-1/Phase-3 compiler ordering with a generator-keyed `CompilerRegistry`: Phase 1 registers the manual postfix compiler, T021 registers `alphagen`, and T026 registers `pool`; `factor_store.load()` keeps the same signature throughout and raises `CompilerNotRegisteredError` when unresolved.

# F003 Phase-1 Interface Specification

This specification is normative for T001, T002, and T005-T012. Public names listed below are the only Phase-1 compatibility surface.

## 1. Final File Layout

```text
src/alphamill/factor_factory/
├── __init__.py                       # no public re-exports
├── errors.py                         # shared typed F003 errors
├── canonical.py                      # canonical JSON and digest primitives
├── factor.py                         # executable FactorDef/Input/Output contract
├── cli.py                            # alphamill-generate: seed/show
├── hypotheses/
│   ├── __init__.py                   # no public re-exports
│   ├── schema.py                     # HypothesisDef
│   └── catalog.py                    # immutable catalog + built-ins
├── generators/
│   ├── __init__.py                   # no public re-exports
│   ├── base.py                       # Generator, request/result/counts, Window
│   ├── binding.py                    # binding DTOs, parsing, F002 validation
│   ├── universe.py                   # Phase-1 explicit universe fixture contract
│   ├── expression_compiler.py        # minimal manual postfix compiler
│   ├── egress_guard.py               # process socket guard
│   ├── write_guard.py                # process write-path whitelist
│   └── manual/
│       ├── __init__.py               # no public re-exports
│       └── seeds.py                  # ManualGenerator and five seed definitions
└── registry/
    ├── __init__.py                   # no public re-exports
    ├── compiler_registry.py          # generator -> FactorCompiler dispatch
    ├── factor_store.py               # FactorDefDTO, conversion, feature map, I/O
    └── run_store.py                  # GenerationRun DTO, config, events, run.json
```

Ownership is fixed:

| Type | Owning module |
|---|---|
| `FactorDef`, `FactorInput`, `FactorOutput` | `factor.py` |
| `Generator`, `GenerationRequest`, `GenerationResult`, `GenerationCounts` | `generators/base.py` |
| `Window` | `generators/base.py` |
| `SnapshotBinding` and binding member DTOs | `generators/binding.py` |
| `HypothesisDef` | `hypotheses/schema.py` |
| `FactorDefDTO`, `FeatureMapDTO`, DTO/executable conversion | `registry/factor_store.py` |
| `GenerationRun` and nested run DTOs | `registry/run_store.py` |

`FactorDef` is a domain object shared by generators, storage, pools, and later evaluation. Placing it under `generators/base.py` would make storage and downstream consumers depend on a backend interface module and creates the wrong dependency direction.

### Import direction

```text
canonical / errors / factor
        ↑
hypotheses/schema
        ↑
hypotheses/catalog

factor + binding + canonical
        ↑
generators/base
        ↑
manual/seeds

factor + errors
        ↑
registry/compiler_registry
        ↑
registry/factor_store

base + binding + canonical
        ↑
registry/run_store

cli imports and composes all of the above
```

No `registry` module may be imported by `factor.py`, `generators/base.py`, or `hypotheses/schema.py`.

## 2. Common Scalar Contracts

### `canonical.py`

```python
from typing import TypeAlias

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

def canonical_json_bytes(value: JSONValue) -> bytes: ...
def canonical_json_text(value: JSONValue) -> str: ...
def sha256_hex(value: JSONValue) -> str: ...
def sha256_prefixed_bytes(payload: bytes) -> str: ...
def utc_iso(value: datetime) -> str: ...
def parse_utc(value: str, *, field: str) -> datetime: ...
```

Canonical JSON is exactly:

```python
json.dumps(
    value,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")
```

Rules:

- No trailing newline participates in a digest.
- NaN and infinity are rejected.
- `Path`, `datetime`, tuples, dataclasses, bytes, and arbitrary objects must be converted before calling.
- F003 `definition_digest` is an unprefixed 64-character lowercase hex string.
- External artifact digests and `feature_map_digest` use `sha256:<64 lowercase hex>`.
- UTC disk timestamps use `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`.

### `errors.py`

```python
class FactorFactoryError(Exception): ...

class SchemaValidationError(FactorFactoryError): ...
class UnknownSchemaVersionError(SchemaValidationError): ...
class ConclusionFieldError(SchemaValidationError): ...
class UnknownHypothesisError(SchemaValidationError): ...

class CompilerNotRegisteredError(FactorFactoryError): ...
class FactorCompilationError(FactorFactoryError): ...
class FactorDependencyError(FactorCompilationError): ...
class FeatureMapIntegrityError(FactorFactoryError): ...
class FactorStoreError(FactorFactoryError): ...

class BindingValidationError(FactorFactoryError): ...
class SnapshotResolverUnavailableError(BindingValidationError): ...

class RunStoreError(FactorFactoryError): ...

class BoundaryGuardError(FactorFactoryError): ...
class EgressDeniedError(BoundaryGuardError): ...
class WriteDeniedError(BoundaryGuardError): ...
```

## 3. Executable Factor Contract

### `factor.py`

```python
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeAlias

import pandas as pd

FactorScope: TypeAlias = Literal["time_series", "cross_sectional"]
FactorInput: TypeAlias = pd.DataFrame
FactorOutput: TypeAlias = pd.Series
FactorCompute: TypeAlias = Callable[[FactorInput], FactorOutput]
FactorResolver: TypeAlias = Callable[[str], "FactorDef"]


@dataclass(frozen=True)
class FactorDef:
    factor_id: str
    hypothesis_id: str
    name: str
    generator: str
    scope: FactorScope
    params: dict[str, JSONValue]
    compute: FactorCompute
    data_columns: list[str]
    meta: dict[str, JSONValue]
```

Input/output rules:

- `time_series`: input index is a UTC `DatetimeIndex`; output is a float `Series` with the identical index.
- `cross_sectional`: input index is a UTC `MultiIndex` named `("timestamp", "pair")`; output has the identical index.
- Cross-sectional input contains reserved boolean column `__in_universe__`.
- Rows outside the PIT universe must produce `NaN`, the sole no-signal representation.
- `compute` must not mutate its input.
- `expression` never becomes a `FactorDef` top-level field.

Every generated executable factor has these `meta` keys:

```python
{
    "schema_version": 1,
    "expression": list[str],
    "definition_digest": str,
    "generator_version": str,
    "feature_map": dict[str, int],
    "feature_map_digest": str,
    "run_id": str,
    "created_at": str,
    "hypothesis_source": str,
}
```

## 4. Generator Contract

### `generators/base.py`

```python
Expression: TypeAlias = tuple[str, ...]
RejectionReason: TypeAlias = Literal[
    "unregistered_op",
    "lookahead",
    "reachability",
    "duplicate_definition",
]

CONCLUSION_FIELDS: frozenset[str] = frozenset(
    {
        "ic",
        "rank_ic",
        "pnl",
        "verdict",
        "promoted",
        "cost_verdict",
        "promotion_verdict",
    }
)

DEFAULT_WINDOW_PRESET = "default_1h_2y"
DEFAULT_SEED_QUOTA = 5


@dataclass(frozen=True)
class Window:
    start: datetime
    end: datetime
    resample: str

    @classmethod
    def from_preset(
        cls,
        name: str,
        *,
        cutoff_time: datetime,
    ) -> "Window": ...


@dataclass(frozen=True)
class RejectionCounts:
    unregistered_op: int = 0
    lookahead: int = 0
    reachability: int = 0
    duplicate_definition: int = 0


@dataclass(frozen=True)
class GenerationCounts:
    proposed: int
    rejected: RejectionCounts
    registered: int


@dataclass(frozen=True)
class GenerationRequest:
    generator: str
    binding: SnapshotBinding
    seed: int
    window: Window
    config: Mapping[str, JSONValue]
    quota: int


@dataclass(frozen=True)
class GenerationResult:
    run_id: str
    factors: list[FactorDef]
    pool: FactorDef | None
    counts: GenerationCounts
    device: str
    tier_level: str


class Generator(Protocol):
    name: str

    def produce(self, request: GenerationRequest) -> GenerationResult: ...


def reject_conclusion_fields(
    payload: Mapping[str, object],
    *,
    context: str,
) -> None: ...
```

Validation rules:

- `Window` requires timezone-aware UTC datetimes, `start < end`, and Phase-1 `resample == "1h"`.
- `default_1h_2y` expands to `[cutoff_time - 730 days, cutoff_time)` with `resample="1h"`.
- `quota >= 1`.
- Counts must satisfy `proposed == registered + sum(rejected fields)`.
- `GenerationResult.pool`, if present, must have `generator == "pool"`.
- Unknown constructor fields are rejected by Python; mapping/JSON parsers additionally use exact allowed-field sets.
- Conclusion-field rejection applies to schema top-level fields, not recursively to `params` or `config`.

Concrete generators are run-scoped: the orchestrator allocates `run_id`, constructs the backend with that ID, and requires `result.run_id` to match. `run_id` is not added to `GenerationRequest`.

## 5. Hypothesis Contract

### `hypotheses/schema.py`

```python
CostSensitivity: TypeAlias = Literal["low", "medium", "high", "unknown"]


@dataclass(frozen=True, kw_only=True)
class HypothesisDef:
    hypothesis_id: str
    mechanism: str
    data_columns: tuple[str, ...]
    expected_holding_period: str
    cost_sensitivity: CostSensitivity
    source: str
    generation: int
    applicable_state: str = "unspecified"
```

All strings must be nonempty. `data_columns` must be unique, `generation >= 0`, and an empty `applicable_state` is normalized by neither parser nor constructor: it is rejected.

### `hypotheses/catalog.py`

```python
class HypothesisCatalog:
    def __init__(self, entries: Iterable[HypothesisDef] = ()) -> None: ...
    def register(self, hypothesis: HypothesisDef) -> None: ...
    def require(self, hypothesis_id: str) -> HypothesisDef: ...
    def all(self) -> tuple[HypothesisDef, ...]: ...


def builtin_catalog() -> HypothesisCatalog: ...

DEFAULT_CATALOG: HypothesisCatalog
MECHANISM_UNKNOWN_ID = "mechanism_unknown"
```

`register()` rejects duplicate IDs; replacement is never implicit.

Built-ins are exactly:

```text
mechanism_unknown
funding_carry
basis_reversion
open_interest_change
cross_sectional_momentum
realized_volatility
```

The five manual hypotheses use their corresponding required data columns. `mechanism_unknown` has `applicable_state="unspecified"`, `cost_sensitivity="unknown"`, `source="system"`, and `generation=0`.

## 6. Snapshot Binding Contract

### `generators/universe.py`

Phase 1 freezes a JSON fixture contract without pretending that F008's final CSV parser already exists.

```python
@dataclass(frozen=True, kw_only=True)
class UniverseMembership:
    lake_pair: str
    valid_from: datetime
    valid_to: datetime | None


@dataclass(frozen=True, kw_only=True)
class UniverseLedger:
    schema_version: int
    digest: str
    memberships: tuple[UniverseMembership, ...]

    def universe_at(self, at: datetime) -> frozenset[str]: ...


def load_explicit_universe(
    path: Path,
    *,
    expected_digest: str,
    expected_schema_version: int,
) -> UniverseLedger: ...
```

Fixture JSON:

```json
{
  "schema_version": 1,
  "members": [
    {
      "lake_pair": "BTC-USDT-PERP",
      "valid_from": "2024-01-01T00:00:00Z",
      "valid_to": null
    }
  ]
}
```

It is canonicalized before digest verification. Membership semantics are:

```text
valid_from <= T AND (valid_to IS NULL OR T < valid_to)
```

T020 may add an F008 CSV loader implementing the same return contract; `binding.py` signatures do not change.

### `generators/binding.py`

```python
BindingMode: TypeAlias = Literal["snapshot", "explicit_tuples"]
AsOfFidelity: TypeAlias = Literal["bitemporal", "event_time_only"]


@dataclass(frozen=True, kw_only=True)
class DatasetBinding:
    data_version: str
    value_digest: str
    as_of_fidelity: AsOfFidelity
    event_time_min: datetime
    event_time_max: datetime


@dataclass(frozen=True, kw_only=True)
class ArtifactRef:
    digest: str
    path: Path
    schema_version: int


@dataclass(frozen=True, kw_only=True)
class BindingProvenance:
    created_at: datetime
    artifact_path: Path
    member_manifest_paths: dict[str, Path]
    symbol_map_path: Path
    universe_path: Path
    calendar_path: Path


@dataclass(frozen=True, kw_only=True)
class SnapshotRefBinding:
    mode: Literal["snapshot"]
    research_snapshot_id: str


@dataclass(frozen=True, kw_only=True)
class ExplicitSnapshotBinding:
    mode: Literal["explicit_tuples"]
    schema_version: int
    cutoff_time: datetime
    members: dict[str, DatasetBinding]
    symbol_map_digest: str
    universe: ArtifactRef
    calendar: ArtifactRef
    universe_calendar_digest: str
    provenance: BindingProvenance


SnapshotBinding: TypeAlias = SnapshotRefBinding | ExplicitSnapshotBinding


class SnapshotResolver(Protocol):
    def __call__(
        self,
        research_snapshot_id: str,
    ) -> ExplicitSnapshotBinding: ...


UniverseLoader: TypeAlias = Callable[
    [Path, str, int],
    UniverseLedger,
]


@dataclass(frozen=True, kw_only=True)
class ValidatedBinding:
    source: SnapshotBinding
    resolved: ExplicitSnapshotBinding
    universe_ledger: UniverseLedger


def parse_binding(payload: Mapping[str, object]) -> SnapshotBinding: ...

def load_binding_file(path: Path) -> SnapshotBinding: ...

def binding_to_dict(binding: SnapshotBinding) -> dict[str, JSONValue]: ...

def validate_binding(
    binding: SnapshotBinding,
    *,
    lake_root: Path | None = None,
    snapshot_resolver: SnapshotResolver | None = None,
    universe_loader: UniverseLoader = load_explicit_universe,
) -> ValidatedBinding: ...
```

Validation is fail-closed:

1. Both forms use exact top-level field whitelists. Unknown fields and unknown `schema_version` are errors.
2. Snapshot mode requires `snapshot_resolver`; its absence raises `SnapshotResolverUnavailableError`.
3. Each member is checked through:

```python
reader.read(
    dataset,
    data_version=member.data_version,
    start=resolved.cutoff_time,
    end=resolved.cutoff_time,
    pairs=[],
    as_of=resolved.cutoff_time,
    allow_event_time_only=(member.as_of_fidelity == "event_time_only"),
    lake_root=lake_root,
)
```

4. Returned `data_version`, `value_digest`, `as_of_fidelity`, and `symbol_map_digest` must exactly match the binding.
5. `manifest.load_manifest()` is used only for declared coverage/provenance comparison; F003 does not reimplement digest or status logic.
6. `symbol_map.load_symbol_map(digest=..., lake_root=...)` must succeed.
7. Universe and calendar files are checked independently.
8. Calendar Phase-1 schema is exactly:

```json
{"schema_version":1,"kind":"continuous_24_7","timezone":"UTC"}
```

9. `universe_calendar_digest` is:

```python
"sha256:" + sha256(
    canonical_json_bytes(
        {
            "universe": universe.digest,
            "calendar": calendar.digest,
        }
    )
).hexdigest()
```

10. Every provenance path must exist and resolve to the actual immutable artifact referenced by the semantic fields. Dynamic current/latest paths are rejected.

## 7. Compiler Registry and Ordering Resolution

### `registry/compiler_registry.py`

```python
@dataclass(frozen=True, kw_only=True)
class CompileContext:
    generator: str
    expression: tuple[str, ...]
    scope: FactorScope
    params: Mapping[str, JSONValue]
    data_columns: tuple[str, ...]
    feature_map: Mapping[str, int]
    resolver: FactorResolver | None


FactorCompiler: TypeAlias = Callable[[CompileContext], FactorCompute]


class CompilerRegistry:
    def __init__(
        self,
        compilers: Mapping[str, FactorCompiler] | None = None,
    ) -> None: ...

    def register(
        self,
        generator: str,
        compiler: FactorCompiler,
    ) -> None: ...

    def require(self, generator: str) -> FactorCompiler: ...

    def compile(self, context: CompileContext) -> FactorCompute: ...


DEFAULT_COMPILERS: CompilerRegistry
```

Rules:

- Duplicate registration is rejected.
- Missing registration raises `CompilerNotRegisteredError` containing the generator name.
- Phase 1 registers only `"manual"` using `compile_postfix`.
- T021 registers `"alphagen"` with the same `FactorCompiler` signature.
- T026 registers `"pool"` with the same signature; its compiler requires `context.resolver`, otherwise raises `FactorDependencyError`.
- Registration is explicit at the composition root or test setup. No silent fallback to another compiler.

This resolves the task-order tension without a fake AlphaGen implementation in Phase 1.

## 8. Manual Expression DSL

### `generators/expression_compiler.py`

```python
def referenced_features(
    expression: tuple[str, ...],
) -> tuple[str, ...]: ...

def compile_postfix(context: CompileContext) -> FactorCompute: ...
```

Expression is a disk JSON list of string tokens and an in-memory `tuple[str, ...]`.

Phase-1 tokens are exactly:

```text
feature:<column>
neg
pct_change:<positive integer bars>
return:<positive integer bars>
rolling_std:<positive integer bars>
cs_rank
```

No arbitrary Python, `eval`, AST execution, attribute access, or imports are permitted.

Manual seed expressions are fixed:

```text
funding carry:
  ["feature:funding_rate", "neg"]

basis reversion:
  ["feature:basis_pct", "neg"]

OI change:
  ["feature:open_interest", "pct_change:24"]

cross-sectional momentum:
  ["feature:close", "return:168", "cs_rank"]

volatility:
  ["feature:close", "return:1", "rolling_std:168", "neg"]
```

`cs_rank` groups strictly by timestamp, uses only rows with `__in_universe__ == True`, and returns `NaN` elsewhere.

## 9. Factor DTO and Store

### `registry/factor_store.py`

```python
FACTOR_SCHEMA_VERSION = 1

FACTOR_DTO_FIELDS: frozenset[str] = frozenset(
    {
        "schema_version",
        "factor_id",
        "definition_digest",
        "hypothesis_id",
        "name",
        "generator",
        "generator_version",
        "scope",
        "expression",
        "params",
        "data_columns",
        "feature_map_digest",
        "run_id",
        "created_at",
    }
)

FACTOR_IDENTITY_EXCLUDED_FIELDS: frozenset[str] = frozenset(
    {
        "factor_id",
        "definition_digest",
        "run_id",
        "created_at",
    }
)


@dataclass(frozen=True, kw_only=True)
class FeatureMapDTO:
    schema_version: int
    features: dict[str, int]


@dataclass(frozen=True, kw_only=True)
class FactorDefDTO:
    schema_version: int
    factor_id: str
    definition_digest: str
    hypothesis_id: str
    name: str
    generator: str
    generator_version: str
    scope: FactorScope
    expression: tuple[str, ...]
    params: dict[str, JSONValue]
    data_columns: tuple[str, ...]
    feature_map_digest: str
    run_id: str
    created_at: datetime


def feature_map_digest(feature_map: Mapping[str, int]) -> str: ...

def definition_digest(dto: FactorDefDTO) -> str: ...

def build_factor(
    *,
    hypothesis: HypothesisDef,
    name: str,
    generator: str,
    generator_version: str,
    scope: FactorScope,
    expression: Sequence[str],
    params: Mapping[str, JSONValue],
    feature_map: Mapping[str, int],
    run_id: str,
    created_at: datetime,
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
    resolver: FactorResolver | None = None,
) -> FactorDef: ...

def factor_to_dto(factor: FactorDef) -> FactorDefDTO: ...

def factor_from_dto(
    dto: FactorDefDTO,
    *,
    feature_map: Mapping[str, int],
    compiler: FactorCompiler,
    hypothesis: HypothesisDef,
    resolver: FactorResolver | None = None,
) -> FactorDef: ...

def write(run_dir: Path, factor: FactorDef) -> Path: ...

def read(path: Path) -> FactorDefDTO: ...

def load(
    path: Path,
    *,
    compilers: CompilerRegistry = DEFAULT_COMPILERS,
    catalog: HypothesisCatalog = DEFAULT_CATALOG,
    resolver: FactorResolver | None = None,
    require_completed: bool = True,
) -> FactorDef: ...
```

Identity payload includes:

```text
schema_version
hypothesis_id
name
generator
generator_version
scope
expression
params
data_columns
feature_map_digest
```

`definition_digest` itself must also be excluded from its own hash input. The design's phrase “DTO minus factor_id/run_id/created_at” cannot literally include `definition_digest` without a recursive fixed-point; this specification resolves that contradiction explicitly.

Other rules:

- `factor_id = f"{generator}_{definition_digest[:12]}"`.
- Feature map JSON is:

```json
{"schema_version":1,"features":{"close":0,"funding_rate":1}}
```

- Feature names are nonempty; channel numbers are unique and exactly `0..N-1`.
- Feature map path is `run_dir/feature_maps/<hex-part>.json`.
- Factor path is `run_dir/factors/<factor_id>.json`.
- `write()` writes the feature map before the factor DTO.
- Existing identical content is idempotent; conflicting content at the same path raises `FactorStoreError`.
- `read()` enforces exact fields and digest/ID consistency but does not compile.
- `load()` derives `run_dir` from the factor path, loads and digest-verifies the feature map, resolves the hypothesis, dispatches by `dto.generator`, and returns an executable `FactorDef`.
- With `require_completed=True`, sibling `run.json` must exist with `schema_version == 1` and `status == "completed"`.
- T007 tests use `require_completed=False` because T008 is not yet implemented.
- `partial` factors remain inspectable through `read()` but are not executable through default `load()`.

## 10. Manual Generator

### `generators/manual/seeds.py`

```python
MANUAL_GENERATOR_VERSION = "manual-v1"
MANUAL_FACTOR_ORDER: tuple[str, ...] = (
    "funding_carry",
    "basis_reversion",
    "open_interest_change",
    "cross_sectional_momentum",
    "realized_volatility",
)


class ManualGenerator:
    name = "manual"

    def __init__(
        self,
        *,
        run_id: str,
        catalog: HypothesisCatalog = DEFAULT_CATALOG,
        clock: Callable[[], datetime] | None = None,
        compilers: CompilerRegistry = DEFAULT_COMPILERS,
    ) -> None: ...

    def produce(
        self,
        request: GenerationRequest,
    ) -> GenerationResult: ...
```

Rules:

- `request.generator` must equal `"manual"`.
- Fixed seed definitions are selected in `MANUAL_FACTOR_ORDER`; `quota` truncates this list.
- Phase 1 has no candidate rejection in this backend.
- `proposed == registered == min(quota, 5)`.
- `pool is None`, `device == "cpu"`, `tier_level == "manual"`.
- `seed` does not alter the five fixed definitions; it remains part of run provenance.
- The same semantic request across runs gives the same `factor_id` values despite different run IDs and timestamps.

## 11. Run Manifest and Events

### `registry/run_store.py`

```python
RUN_SCHEMA_VERSION = 1
RunStatus: TypeAlias = Literal["completed", "rejected", "failed", "partial"]
TierLevel: TypeAlias = Literal["L0", "L1", "L2", "manual"]


@dataclass(frozen=True, kw_only=True)
class EngineInfo:
    vendor_commit: str | None
    code_digest: str
    dependencies: dict[str, str]


@dataclass(frozen=True, kw_only=True)
class UniverseSummary:
    pair_count: int
    symbol_map_digest: str
    universe_digest: str
    source: str


@dataclass(frozen=True, kw_only=True)
class ObjectiveInfo:
    turnover_penalty_lambda: float
    reachability_min_trades_90d: int
    cost_model: dict[str, JSONValue]
    min_after_cost_return: float


@dataclass(frozen=True, kw_only=True)
class GenerationRun:
    schema_version: int
    run_id: str
    generator: str
    engine: EngineInfo
    binding: SnapshotBinding | None
    seed: int | None
    config_digest: str
    device: str
    hostname: str
    vram_limit_gb: float | None
    universe: UniverseSummary | None
    tier_level: TierLevel
    window: Window | None
    objective: ObjectiveInfo
    counts: GenerationCounts
    pool: str | None
    started_at: datetime
    finished_at: datetime
    status: RunStatus
    termination: str
    reason: str | None


@dataclass(frozen=True, kw_only=True)
class GenerationEvent:
    schema_version: int
    event_seq: int
    event_type: Literal[
        "generation.run_completed",
        "generation.candidate_rejected",
    ]
    ts: datetime
    run_id: str
    payload: dict[str, JSONValue]


def new_run_id(
    generator: str,
    *,
    now: datetime | None = None,
) -> str: ...

def generation_run_dir(
    run_id: str,
    *,
    reports_root: Path | None = None,
) -> Path: ...

def write_config(
    run_dir: Path,
    config: Mapping[str, JSONValue],
) -> str: ...

def append_candidate_rejected(
    run_dir: Path,
    *,
    run_id: str,
    expression: Sequence[str],
    reason_code: RejectionReason,
    detail: str,
    ts: datetime | None = None,
) -> GenerationEvent: ...

def finalize_run(
    run_dir: Path,
    run: GenerationRun,
) -> Path: ...

def load_run(path: Path) -> GenerationRun: ...
```

Terminal validation:

- `finished_at >= started_at`.
- `completed`: binding/window/universe/seed required; `reason is None`; pool optional.
- `rejected` and `failed`: `reason` required; no factors are considered consumable.
- `partial`: `reason` required and `pool is None`.
- Missing binding may therefore be represented honestly by `binding=None` in a rejected startup manifest.

Write ordering:

1. `config.json`
2. feature maps
3. `factors/*.json`
4. `pool.json`, completed only
5. candidate rejection events
6. `generation.run_completed`, completed only
7. `run.json`, always last

`finalize_run()` is the only public writer of `run.json`. It:

- appends one idempotent completed event only when `status == "completed"`;
- never appends that event for other statuses;
- writes same-directory temporary bytes;
- flushes and `fsync()`s the temporary file;
- uses `os.replace()` to publish;
- `fsync()`s the run directory afterward;
- rejects an already-existing `run.json`.

`events.jsonl` uses one canonical JSON object plus `\n` per event, `O_APPEND`, an exclusive `flock`, one write call, and `fsync()`. `event_seq` starts at 1 and increases monotonically per run.

Config canonicalization removes only these top-level runtime fields before hashing and writing:

```text
created_at, started_at, finished_at, hostname, device, vram_limit_gb
```

`config_digest` uses `sha256:<hex>`.

## 12. Boundary Guards

### `generators/egress_guard.py`

```python
class EgressGuard:
    @property
    def active(self) -> bool: ...
    def verify(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> "EgressGuard": ...
    def __exit__(self, exc_type, exc, traceback) -> None: ...


def install_egress_guard() -> EgressGuard: ...
```

Mechanism:

- Save original `socket.socket`, `socket.create_connection`, and `socket.fromfd`.
- Replace them process-wide before importing or invoking backend/vendor code.
- `socket.socket` permits only `family == socket.AF_UNIX`.
- `create_connection` always raises `EgressDeniedError`.
- `fromfd` permits only explicit `AF_UNIX`.
- Existing sockets are outside this guard's claim; the guard is explicitly process-level, not kernel isolation.
- Installation self-tests one denied `AF_INET` socket and one successful `AF_UNIX` socket.
- Partial installation rolls back and raises `BoundaryGuardError`.
- The runner must retain the guard until generation and artifact publication finish.

### `generators/write_guard.py`

```python
class WritePathGuard:
    @property
    def active(self) -> bool: ...
    @property
    def root(self) -> Path: ...
    def verify(self) -> None: ...
    def close(self) -> None: ...
    def __enter__(self) -> "WritePathGuard": ...
    def __exit__(self, exc_type, exc, traceback) -> None: ...


def install_write_path_guard(
    run_dir: Path,
    *,
    reports_root: Path | None = None,
) -> WritePathGuard: ...

def assert_write_allowed(
    path: str | os.PathLike[str],
    *,
    root: Path,
) -> Path: ...
```

Mechanism:

- `run_dir` must resolve to exactly `reports_root/generation/<one safe path component>`.
- The resolved run directory must exist before installation.
- Patch write-capable paths through `builtins.open`, `io.open`, `os.open`, `os.mkdir`,
  `os.makedirs`, `os.rename`, `os.replace`, `os.remove`, `os.unlink`, and `os.rmdir`.
- Reads remain unrestricted.
- Rename/replace require both source and destination inside the root.
- Symlink and hard-link creation are denied while active.
- Existing symlink parents are resolved before containment checks.
- Installation verifies an allowed write inside the run directory and a denied write outside it.
- Any patch or self-test failure rolls back and raises `BoundaryGuardError`.
- This guard targets accidental/vendor writes, not a hostile native extension or kernel-level adversary.

Backend `produce()` must execute only while both guards report `active=True`.

## 13. CLI Contract

### `cli.py`

```python
EXIT_OK = 0
EXIT_FAILED = 1
EXIT_REJECTED = 2


def build_parser() -> argparse.ArgumentParser: ...

def main(
    argv: Sequence[str] | None = None,
    *,
    reports_root: Path | None = None,
    lake_root: Path | None = None,
) -> int: ...
```

Console entry point:

```toml
[project.scripts]
alphamill-generate = "alphamill.factor_factory.cli:main"
```

Phase-1 commands:

```text
alphamill-generate seed
  --generator manual
  --binding PATH
  --seed INT
  [--window default_1h_2y]
  [--config PATH]

alphamill-generate show
  (--run RUN_ID | --factor FACTOR_ID)
```

Rules:

- `--binding` is parsed as optional by `argparse` so the application can create a rejected `run.json`; absence returns `EXIT_REJECTED`.
- `--seed` remains argparse-required.
- Seed quota is `DEFAULT_SEED_QUOTA`; Phase 1 does not expose `--quota`.
- The CLI allocates `run_id`, constructs `ManualGenerator(run_id=...)`, validates the binding, installs both guards, executes, persists, and finalizes.
- Binding/schema/startup refusal returns 2 and writes a rejected run.
- Runtime/compiler/storage failure returns 1 and writes a failed run when terminal publication remains possible.
- `show --run` prints the parsed `run.json`.
- `show --factor` searches terminal runs, chooses the match with greatest `(finished_at, run_id)`, and prints its DTO plus an `occurrences` list.
- Every encountered matching factor definition must have the same `definition_digest`; disagreement is corruption and returns 1.
- Unknown run or factor schema versions return 2. No compatibility guessing is allowed.

## 14. Build Order and Zero-Conflict Parallelization

Package `__init__.py` ownership is fixed to avoid merge conflicts:

```text
T001 owns generators/__init__.py
T006 owns hypotheses/__init__.py
T007 owns registry/__init__.py
T010 owns generators/manual/__init__.py
```

### Wave 1

1. **T001 alone**

Files: `generators/universe.py`, `generators/__init__.py`, universe fixture, binding test additions.

Reason: T001 and T002 both modify `tests/unit/test_f003_binding.py`, so they cannot run concurrently.

### Wave 2

Run concurrently after T001:

1. **T002**: binding JSON fixtures and `test_f003_binding.py`.
2. **T005**: `errors.py`, `canonical.py`, `factor.py`, `generators/base.py`, generator contract test.
3. **T006**: hypothesis schema/catalog and hypothesis tests.

These tasks share no files.

### Wave 3

Run concurrently after T002 and T005:

1. **T007**: compiler registry, postfix compiler, factor store, factor-store tests.
2. **T009**: `generators/binding.py` and the next sequential binding-test additions.
3. **T011**: egress/write guards and boundary integration tests.

These tasks share no files. T009 follows T002 because both edit the same test module.

### Wave 4

Run concurrently after T006 and T007:

1. **T008**: `registry/run_store.py`, run-store tests.
2. **T010**: `generators/manual/seeds.py`, manual-seed tests.

T010 has an additional practical dependency on T007 because factor identity and executable construction are owned by `factor_store`.

### Wave 5

1. **T012 alone**, after T008-T011.

Files: `cli.py`, `pyproject.toml`, CLI contract tests.

T012 needs binding validation, manual generation, boundary guards, factor persistence, and rejected/terminal run writing.

## 15. Remaining Ambiguities Resolved

1. **SnapshotBinding representation**: a tagged union of two frozen dataclasses, never a mutable parsed-dict wrapper. This prevents invalid mixed-mode objects.

2. **Feature-map location**: `run_dir/feature_maps/<digest>.json`. The factor DTO stores only its digest, preserving the DTO whitelist while making `load()` self-contained.

3. **Expression representation**: disk JSON list of string tokens; in memory `tuple[str, ...]`. No Python-expression strings and no `eval`.

4. **DTO/executable conversion owner**: exclusively `registry/factor_store.py`. Generator modules must not construct disk DTO dictionaries themselves.

5. **Compiler ownership**: `compiler_registry.py` dispatches; each backend owns only its compiler function. Missing compilers are typed failures.

6. **Factor identity self-reference**: `definition_digest` is excluded from its own payload in addition to `factor_id`, `run_id`, and `created_at`.

7. **Definition identity includes name and schema version**: both are semantic definition fields in the declared DTO and therefore participate in the digest.

8. **Manual seed feature map**:

```python
{
    "close": 0,
    "funding_rate": 1,
    "basis_pct": 2,
    "open_interest": 3,
}
```

9. **Window semantics**: all windows are concrete UTC half-open intervals; `default_1h_2y` means exactly 730 days ending at the binding cutoff.

10. **Run ownership**: orchestration allocates the run ID; concrete generator instances are run-scoped and must return that same ID.

11. **Only completed factors execute by default**: `factor_store.load(require_completed=True)` enforces the downstream-consumption rule; diagnostics use `read()`.

12. **Digest conventions**: F003 definition digest is raw hex for the mandated factor-ID formula; artifact digests remain `sha256:` prefixed.

13. **No public package-root exports in Phase 1**: implementers import from owning modules, preventing initialization-time compiler/catalog cycles.

14. **Line limit**: the split above keeps binding, factor persistence, boundary guards, and run persistence in separate files; no new source file should approach 350 lines.

**Effort:** Medium, 1-2 days for all Phase-1 interfaces and unit coverage.

**Confidence:** High. The only necessary correction to the written design is excluding `definition_digest` from its own hash input; otherwise the digest definition is not computable.
