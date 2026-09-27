---
kind: feature
id: F012
version: "0.2"
related_features: [F003, F007, F013]
topics: [factor-factory, alphagen, generation, cli, funnel]
doc_kind: tasks
created: 2026-09-27
updated: 2026-09-27
---

# F012：AlphaGen 后端接入挖掘 CLI - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成并验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾；勾选时附 `RED:` / `GREEN:` 证据。
- 实现中若任务顺序或契约失效，先修订三件套，再继续编码。
- 统一格式：`- [ ] T001 (`US-001`, `FR-001`, `AC-001`): <可验证动作> — verify: `path/to/test.py``

## 1. 前置条件

- [ ] T001 (`DQ-001`): 关闭所有阻塞性 spec/design 问题（`Q-001`~`Q-004` 已关闭，design §10 无开放问题）— verify: `spec.md`、`design.md`
- [ ] T002 (`FR-001`, `FR-007`, `DR-002`): 核对上游真实签名——`Generator`/`GenerationRequest`/`GenerationResult`、`run_generation`、`build_tensor`/`build_stock_data`、`evaluate_objective` 面板列契约、`factor_store` 的 `definition_digest` 排除字段集（决定 `params.prefilter` 放置）、`register_alphagen_compiler`、`cli.py`/`run_store.py` 行数预算 — verify: `src/alphamill/factor_factory/generators/base.py`

## 2. 实现任务

### Phase 1：候选流水线与停止判定（纯 Python 最小切片）

- [ ] T003 (`FR-003`, `FR-004`, `AC-003`, `AC-004`): 新增 `generators/candidate_pipeline.py`：渲染后 token → 自检 → 按 `definition_digest` 查重 → 目标对齐预筛 → 入册/拒绝；拒绝写 `generation.candidate_rejected`；计数守恒 — verify: `tests/unit/test_f012_candidate_pipeline.py`
- [ ] T004 (`FR-005`, `AC-005`): 新增 `generators/stop_conditions.py`：配额、夜槽时段、SIGTERM/SIGINT 标志 → `stop_reason`；配额达成后流水线不再计入 `proposed` — verify: `tests/unit/test_f012_stop_conditions.py`

### Phase 2：运行记录与 CLI 分发

- [ ] T005 (`FR-007`, `DR-001`, `AC-007`): 新增 `registry/run_schema.py`（自 `run_store.py` 迁出字段定义与校验），run.json v2（`budget`、`stop_reason`、`evaluations`）与 v1 双读；`run_store.py` 净增 ≤0 — verify: `tests/unit/test_f012_run_schema.py`
- [ ] T006 (`FR-006`, `IR-001`, `IR-002`, `IR-003`, `AC-006`): 新增 `factor_factory/mine_dispatch.py` 与 `mine_config.py` alphagen 段；`cli.py` 去掉六处写死的 manual，改走分发表；`cli.py` 净增 ≤0 — verify: `tests/unit/test_f012_cli_contract.py`

### Phase 3：AlphaGen 生成器接线

- [ ] T007 (`FR-002`, `AC-002`): `run_generation` 增 `on_expression` / `should_stop`（SB3 `BaseCallback` 步边界停止），两者为 None 时行为不变；移除内部 run_id 生成 — verify: `tests/integration/test_f012_alphagen_mining.py`
- [ ] T008 (`FR-001`, `FR-002`, `DR-003`, `AC-001`, `AC-002`): 新增 `generators/alphagen_generator.py`：`produce()` 编排张量 → 训练 → 流水线 → `GenerationResult`；`DEFAULT_COMPILERS` 注册 alphagen 编译器 — verify: `tests/integration/test_f012_alphagen_mining.py`
- [ ] T009 (`FR-007`, `AC-007`): run.json 如实字段接线（`vendor_commit`、`code_digest`、`tier_level`、`universe.source/pair_count`、`vram_limit_gb`、`kronos_offload`、`budget`、`stop_reason`、`evaluations`），修正 `write_generation_manifest` 写死项 — verify: `tests/unit/test_f012_run_schema.py`

## 3. 验证与验收任务

- [ ] T010 (`AC-003`, `AC-004`, `AC-005`): 单元套件：流水线拒绝路径与计数守恒、停止条件与 `partial` 语义 — verify: `tests/unit/test_f012_candidate_pipeline.py`、`tests/unit/test_f012_stop_conditions.py`
- [ ] T011 (`AC-006`, `AC-007`): CLI 与 schema 套件：manual 基准对照（改动前 main 跑出的 `definition_digest` 集）、alphagen 分发、v1/v2 双读 — verify: `tests/unit/test_f012_cli_contract.py`、`tests/unit/test_f012_run_schema.py`
- [ ] T012 (`AC-001`, `AC-002`): 集成套件（`mining` extra，小面板真实训练）全绿；无 torch 环境按约定 skip — verify: `tests/integration/test_f012_alphagen_mining.py`
- [ ] T013 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`): 运行项目统一质量门 — verify: `python3 tools/verify.py`

### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T014 [TEST] (`AC-008`, `AC-001`, `AC-002`): 层 2 旅程验收：执行机 `qiaozhi-lt` CUDA 夜槽，真实湖显式绑定 `mine --generator alphagen --quota 50` → `completed`、入册 50、run.json 如实、耗时/显存峰值/单候选预筛耗时留痕；开发机 skip 不算证据 — verify: `tests/integration/test_f012_alphagen_mining.py`
- [ ] T015 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`): 收口回写：spec 验收证据与 AC 勾选、`BACKLOG.md` 状态、`docs/features/releases/0.2.md` 交付记录、frontmatter 流转 — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002`：先关问题再核契约。
- `T002 -> T003`、`T002 -> T004`、`T002 -> T005`：契约核对后三条纯 Python 任务可并行。
- `T005 -> T006`：CLI 分发依赖 v2 schema。
- `T002 -> T007`：训练回调改造依赖签名核对。
- `T003 -> T008`、`T004 -> T008`、`T007 -> T008`：生成器编排依赖流水线、停止判定与回调。
- `T005 -> T009`、`T008 -> T009`：如实字段接线依赖 schema 与生成器。
- `T003 -> T010`、`T004 -> T010`：单元套件覆盖流水线与停止。
- `T006 -> T011`、`T009 -> T011`：CLI 与 schema 套件在接线之后。
- `T008 -> T012`：集成套件依赖生成器。
- `T010 -> T013`、`T011 -> T013`、`T012 -> T013`：统一质量门在三条验证轨之后。
- `T012 -> T014`：执行机旅程与集成套件同载体，先有集成用例再跑执行机取证。
- `T013 -> T014`：执行机旅程在本地全绿之后。
- `T013 -> T015`、`T014 -> T015`：门禁与旅程双绿后才收口回写。

## 5. 明确后移

- 批量评测编排、FactorDef → 信号 CSV、生成事件到 F007 漏斗的适配、显式绑定 → ResearchSnapshot 转换——`F013`。
- M2 出口的 ≥50 自动评测验收实跑——BACKLOG 执行顺序第 3 项（依赖 F013 与 F005）。
- `seed` 子命令接入 alphagen、GP/LLM 后端——不在 v0.2 规划内。
