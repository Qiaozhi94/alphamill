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
- 统一格式：`- [x] T001 (`US-001`, `FR-001`, `AC-001`): <可验证动作> — verify: `path/to/test.py``（GREEN: spec §8 Q-001~Q-007 均 [x]，design §10「无」，2026-09-27 核对）

## 1. 前置条件

- [ ] T001 (`DQ-001`): 关闭所有阻塞性 spec/design 问题（`Q-001`~`Q-007` 已关闭，design §10 无开放问题）— verify: `spec.md`、`design.md`
- [x] T002 (`FR-001`, `FR-003`, `NFR-003`): 核对 design §1 所列真实签名与行号，并在执行机 `qiaozhi-lt` 按真实面板实测单候选预筛耗时 p50/p95（`cs_median` 规则）；p95 > 1 s 时先回写 design 加速方案并交 owner 裁决 — verify: `src/alphamill/factor_factory/generators/objective.py`（GREEN: 签名与行号经文档检视 4 轮逐条核对；执行机 qiaozhi-lt 实测预筛 p50 355 ms / p95 403 ms < 1 s，面板 601,520 行、湖内 35 对 / 窗口内在宇宙 26 对，建张量 78.6 s；取证 `reports/f012/prefilter-timing.json`）

## 2. 实现任务

### Phase 1：渲染与候选流水线（纯 Python 最小切片）

- [x] T003 (`FR-002`, `AC-010`): 修正 `alphagen_runner.render_expression` / `_operator_token`：滚动与成对滚动算子 `name:N`（含 `corr:N`/`cov:N`，正常候选）、`CSRank→cs_rank`、`Rank→ts_rank:N`；提交说明注明 `run_generation` 的 token 输出随之变化 — verify: `tests/unit/test_f012_render.py`（RED: 渲染往返 17 failed；GREEN: 25 passed；F003 回归 88 passed；执行机 CUDA `ALPHAMILL_INTEGRATION=1 test_f003_generation_run.py` 单独跑 13 passed（含 ≥50 产能）。另见：F003 两个集成文件同进程跑时确定性开关泄漏致 `Med` CUDA 报错，为既有测试隔离问题，收口登记）
- [x] T004 (`FR-001`, `FR-004`, `AC-004`): 新增 `generators/channel_binding.py`：`feature:<basename>` → 湖通道名，缺通道抛 `MissingChannelError`，同名 basename 冲突检测 — verify: `tests/unit/test_f012_candidate_pipeline.py`（RED: 076308b 收集期 ImportError；GREEN: 通道绑定 3 passed）
- [x] T005 (`FR-003`, `AC-003`): `objective.evaluate_objective` 增 `position_rule`（`sign` 缺省 / `cs_median`，只统计 observed 行），F003 既有用例零修改 — verify: `tests/unit/test_f012_candidate_pipeline.py`（RED: 同 076308b；GREEN: cs_median 2 passed——恒正排名 sign 下 trades_90d=0、cs_median 下 >0；F003 objective 回归零修改通过）
- [x] T006 (`FR-004`, `DR-002`, `NFR-005`, `AC-004`): 新增 `registry/event_writer.py`（无缓冲单写者、批量 fsync、事件版本解耦；`run_store` 两处事件信封改用 `EVENT_SCHEMA_VERSION`）与 `prefilter.jsonl` 写出 — verify: `tests/unit/test_f012_candidate_pipeline.py`（RED: 同 076308b；GREEN: 写者 4 passed——序号续接、信封 EVENT_SCHEMA_VERSION、1 万条线性；run_store 仍 350 行，F003 run_store 回归通过）
- [x] T007 (`FR-002`, `FR-003`, `FR-004`, `AC-003`, `AC-004`): 新增 `generators/candidate_pipeline.py`：绑定 → `build_factor` → `check_expression(seen, digest)` → 预筛（close 缺失视为未观测）→ 入册/拒绝，候选级与系统级异常按 design §7 分类，配额达成后不计数 — verify: `tests/unit/test_f012_candidate_pipeline.py`（RED: 20797c3 ModuleNotFoundError；GREEN: 流水线 11 passed——五类拒绝码、digest 查重、退化再现判 duplicate、计数守恒与事件对账、配额停止、缺价掩码）
- [x] T008 (`FR-005`, `AC-005`): 新增 `generators/stop_conditions.py`（配额/夜槽/信号标志）；`GpuSlot.acquire(cancel=...)` 取消时先写 `cancelled` 队列记录再抛 `AcquireCancelled` — verify: `tests/unit/test_f012_stop_conditions.py`（RED: 18f02c8 ImportError；GREEN: 5 passed——配额、夜槽、SIGTERM 优先与处理器恢复、sticky、取消写 cancelled 后下一 run 取得槽；F003 gpu_slot 回归 35 passed）

### Phase 2：运行记录、编译器组装、取数与 CLI 分发

- [x] T009 (`FR-007`, `DR-001`, `AC-007`): 新增 `registry/run_schema.py`（迁出并由 `run_store` 再导出 design §1 第 8 行全部名字，`RUN_SCHEMA_VERSION=2`），v1/v2 双读；`factor_store.load` 接受 {1,2}；`GenerationRequest`/`GenerationResult` 增可选字段 — verify: `tests/unit/test_f012_run_schema.py`（RED: 978675d ImportError BudgetInfo；GREEN: schema 15 passed + F003 run_store/factor_store/cli_contract 回归通过；run_store 350→217 行）
- [x] T010 (`FR-001`, `AC-001`): 新增 `registry/default_compilers.py`（惰性组装 manual + alphagen），`build_factor`/`load` 缺省改用它，无导入环 — verify: `tests/unit/test_f012_run_schema.py`（RED: 2 failed——缺省编译器无 alphagen；GREEN: 3 passed + F003 因子存储/协同池/适配器/种子/CLI 回归通过；F003 `test_build_factor_rejects_unknown_generator` 示例生成器由 alphagen 改为 gp，意图不变）
- [x] T011 (`FR-008`, `AC-008`): `lake_tensor.pairs_during(validated, start, end)`：窗口内宇宙成员并集；建后校验 `__in_universe__.any()` — verify: `tests/integration/test_f012_alphagen_mining.py`（RED: 6125601 ImportError；GREEN: 3 passed——期间退出者仍在并集、pair_count 按掩码、空宇宙拒绝；F003 lake_tensor 回归通过。签名取 `UniverseLedger`（调用方传 `validated.universe_ledger`），design §1 第 17 行随 T012 回写）
- [x] T012 (`FR-006`, `IR-001`, `IR-002`, `IR-003`, `AC-006`): 新增 `mine_dispatch.py`（含 config 合成顺序与 universe 汇总）、`manifest_builder.py`、`DEFAULT_ALPHAGEN_CONFIG`；`cli.py` 去掉 design §1 所列全部写死点、先建张量后卸载 Kronos、入口安装信号标志、`writer.close()` 先于 finalize；`cli.py`/`run_store.py` 净增 ≤0 — verify: `tests/unit/test_f012_cli_contract.py`（RED: 9837fb2 ImportError；GREEN: a2a7ba4 11 passed——manual 与 main@84ab505 基准等价、alphagen 分发/v2 如实/objective 深合并/非 L0 拒绝/坏张量先于卸载/partial；单测全量 1338 passed；cli.py 342 行（原 343），run_store.py 217 行；design §1 第 17 行 pairs_during 签名已回写）

### Phase 3：AlphaGen 训练与生成器

- [x] T013 (`FR-002`, `AC-002`): 新增 `generators/alphagen_training.py::train_with_callbacks`（SB3 回调步边界停止，返回 `stopped`/`evaluations`），`run_generation` 原样保留 — verify: `tests/integration/test_f012_alphagen_mining.py`（RED: 5d3f663 ModuleNotFoundError；GREEN: 5 passed——执行机 qiaozhi-lt CPU 小面板真实 PPO：每个被评估表达式以 token 进钩子、should_stop 叫停后 stopped=True 且不再推进训练步）
- [ ] T014 (`FR-001`, `FR-002`, `FR-008`, `DR-003`, `AC-001`, `AC-002`, `AC-008`): 新增 `generators/alphagen_generator.py::AlphaGenGenerator`（构造器注入停止判定、写者、编译器；`produce` 消费 `request.panel`；`pool=None`、`tier_level=L0`、`pair_count` 取宇宙掩码）— verify: `tests/integration/test_f012_alphagen_mining.py`

## 3. 验证与验收任务

- [ ] T015 (`AC-003`, `AC-004`, `AC-005`, `AC-010`): 单元套件：渲染逐算子往返、流水线拒绝路径、截面仓位、退化信号、事件线性写出与计数守恒、停止条件、信号处理与取消出队 — verify: `tests/unit/test_f012_render.py`、`tests/unit/test_f012_candidate_pipeline.py`、`tests/unit/test_f012_stop_conditions.py`
- [ ] T016 (`AC-006`, `AC-007`): CLI 与 schema 套件：manual 基准夹具（改动前 main 在临时 detached worktree 实跑取得）按 `FR-006` 口径等价、alphagen config 合成、非 L0、零行/空宇宙、同名通道、v1/v2 双读 — verify: `tests/unit/test_f012_cli_contract.py`、`tests/unit/test_f012_run_schema.py`
- [ ] T017 (`AC-001`, `AC-002`, `AC-008`): 集成套件（`mining` extra，scratch 湖小面板真实训练）全绿；无 torch 环境按约定 skip — verify: `tests/integration/test_f012_alphagen_mining.py`
- [ ] T018 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-010`): 运行项目统一质量门 — verify: `python3 tools/verify.py`

### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T019 [TEST] (`AC-009`, `AC-001`, `AC-002`): 层 2 旅程验收：执行机 `qiaozhi-lt` CUDA 夜槽以 CLI 实跑 `mine --generator alphagen --quota 50`（真实湖显式绑定），写 `reports/f012/capacity-evidence.json` 并由取证校验用例核对；未达 50 时同步登记 M2 产能发现 — verify: `tests/integration/test_f012_capacity_evidence.py`
- [ ] T020 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-009`, `AC-010`): 收口回写：spec 验收证据与 AC 勾选、`BACKLOG.md` 状态、`docs/features/releases/0.2.md` 交付记录、frontmatter 流转 — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002`：先关问题再核契约与实测预筛耗时。
- `T002 -> T003`、`T002 -> T004`、`T002 -> T005`、`T002 -> T006`、`T002 -> T008`、`T002 -> T009`：契约核对后基础任务可并行。
- `T003 -> T007`、`T004 -> T007`、`T005 -> T007`、`T006 -> T007`：流水线依赖渲染、通道绑定、仓位规则与写者。
- `T009 -> T010`：编译器组装依赖 v2 schema 下的 `factor_store`。
- `T009 -> T011`：取数辅助依赖 schema 中的 universe 汇总定义。
- `T008 -> T012`、`T010 -> T012`、`T011 -> T012`：CLI 接线依赖停止判定、编译器组装与取数。
- `T002 -> T013`：回调式训练依赖签名核对。
- `T007 -> T014`、`T008 -> T014`、`T010 -> T014`、`T011 -> T014`、`T013 -> T014`：生成器编排依赖流水线、停止、编译器、取数与训练入口。
- `T003 -> T015`、`T007 -> T015`、`T008 -> T015`：单元套件在渲染、流水线与停止判定之后。
- `T010 -> T016`、`T012 -> T016`：CLI 与 schema 套件在编译器组装与接线之后。
- `T011 -> T017`、`T013 -> T017`、`T014 -> T017`：集成套件依赖取数、训练入口与生成器。
- `T015 -> T018`、`T016 -> T018`、`T017 -> T018`：统一质量门在三条验证轨之后。
- `T017 -> T019`、`T018 -> T019`：执行机旅程在集成用例与本地全绿之后。
- `T018 -> T020`、`T019 -> T020`：门禁与旅程双绿后才收口回写。

## 5. 明确后移

- 批量评测编排、FactorDef → 信号 CSV、生成事件到 F007 漏斗的适配、显式绑定 → ResearchSnapshot 转换——`F013`。
- M2 出口的 ≥50 自动评测验收实跑——BACKLOG 执行顺序第 3 项（依赖 F013 与 F005）。
- `seed` 子命令接入 alphagen、GP/LLM 后端——不在 v0.2 规划内。
- AlphaGen 协同池 meta-factor 注册（FR2.6）——owner 2026-09-27 裁决另立项（`Q-006`）。
