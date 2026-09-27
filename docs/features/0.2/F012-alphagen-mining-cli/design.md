---
kind: feature
id: F012
version: "0.2"
related_features: [F003, F007, F013]
topics: [factor-factory, alphagen, generation, cli, funnel]
doc_kind: design
created: 2026-09-27
updated: 2026-09-27
---

# F012：AlphaGen 后端接入挖掘 CLI - 设计

## 0. 输入与约束

- **行为契约**：`spec.md`（`FR-001`~`FR-008`、`AC-001`~`AC-009`；§8 `Q-001`~`Q-007` 已裁决）
- **PRD / Architecture**：PRD FR2.1–FR2.4、FR2.6；架构 §7.1（夜槽、GPU 单槽、Kronos 卸载）；数据红线（研究只读 PIT 湖、不引入幸存者偏差）
- **ADR / 上游 Contract**：ADR-0001（alphagen = L0）、ADR-0003（必需计算失败不得静默放行）、ADR-0006、ADR-0008；F003 `DR-003`、`TR-002`、run_store/factor_store 不变量
- **实现约束**：`src/**/*.py` ≤350 行——`factor_factory/cli.py` 现 343、`registry/run_store.py` 现 350、`registry/factor_store.py` 现 267，新增逻辑进新模块，前两者净增 ≤0；无 torch 环境（含 CI）必须可收集（F003 惰性导入约定）；本设计对现有代码的每条声明均以文档检视第 1 轮（22 条）核对过的行号为准

## 1. 技术概要与影响面

| # | 文件 | 变更 |
|---|---|---|
| 1 | `generators/candidate_pipeline.py`（**新增**） | `CandidatePipeline.offer(tokens)`：通道绑定 → 自检 → 查重 → 预筛 → 入册/拒绝；计数守恒；候选级异常分类（§7）；纯 Python |
| 2 | `generators/alphagen_training.py`（**新增**） | `train_with_callbacks(stock_data, target, device, seed, total_timesteps, on_expression, should_stop) -> TrainingOutcome{evaluations, exhausted}`：回调式训练独立入口；**`alphagen_generation.run_generation` 原样保留**（F003 冒烟/容量用例不改，检视 D19） |
| 3 | `generators/alphagen_generator.py`（**新增**） | `AlphaGenGenerator.produce(request)`：张量 → stock_data → 训练 → 流水线 → `GenerationResult` |
| 4 | `generators/channel_binding.py`（**新增**） | `bind_feature_tokens(tokens, feature_map) -> tokens`：`feature:<basename>` → `feature:<dataset>.<column>@<resample>`，映射规则与 `alphagen_runner.build_stock_data:162-166` 的 FeatureType 槽位同源（取 `name.split('.')[-1].split('@')[0].lower()`）；无对应通道 → `MissingChannelError(name)`（检视 D02） |
| 5 | `generators/stop_conditions.py`（**新增**） | `StopController`：配额、夜槽（复用纯函数 `gpu_slot.in_training_window`）、信号标志 → `stop_reason`；`install_signal_flags()` 上下文管理器 |
| 6 | `generators/objective.py` | `evaluate_objective(..., position_rule="sign")` 新增关键字 `position_rule ∈ {"sign","cs_median"}`；`cs_median` = 每个时点在宇宙内 pair 上 `signal − median(signal)` 后取符号（owner 裁决 Q-005，检视 D03）；缺省 `sign` 保持 F003 用例不变 |
| 7 | `generators/base.py` | `GenerationResult` 增可选字段 `stop_reason=None`、`evaluations=None`、`budget=None`（默认值使 `ManualGenerator` 不改，检视 D09） |
| 8 | `registry/run_schema.py`（**新增**） | 自 `run_store.py` 迁出：`RUN_SCHEMA_VERSIONS={1,2}`、`GenerationRun`、`EngineInfo`、`UniverseInfo`、`ObjectiveInfo`（增 `position_rule`，v1 缺省 `"sign"`）、`load_run`、`_validate_terminal`；`run_store.py` 以 `from .run_schema import …` 再导出这些名字，导入方（`objective.py`、`cli.py`、`alphagen_generation.py`、F003 测试）零改动（检视 D22） |
| 9 | `registry/event_writer.py`（**新增**） | `RunEventWriter`：运行内单写者，打开时读一次现有行数得 seq，此后只追加、不回读，每 256 条或关闭时 fsync（检视 D07）；事件 schema 版本常量 `EVENT_SCHEMA_VERSION=1` 与 run schema 解耦（检视 D20） |
| 10 | `registry/factor_store.py` | `load` 的 run.json 校验改为 `schema_version ∈ run_schema.RUN_SCHEMA_VERSIONS` 且 `status=="completed"`（原比较 `FACTOR_SCHEMA_VERSION`，检视 D01）；`load/write` 的 `compilers` 缺省改为函数内惰性取 `default_compilers.full_registry()` |
| 11 | `registry/default_compilers.py`（**新增**） | `full_registry()`：`{manual: compile_postfix, alphagen: …}`，在函数内导入 `alphagen_adapter`，打破 `compiler_registry→adapter→factor_store→compiler_registry` 环（检视 D18）；`compiler_registry.DEFAULT_COMPILERS` 不动 |
| 12 | `factor_factory/manifest_builder.py`（**新增**） | 唯一 run.json 构建器：自 `cli.py` 迁出 `_SeedState`、`_manifest`，按生成器取字段（检视 D14）；alphagen 路径不再调用 `write_generation_manifest`（该函数仅留给 F003 冒烟用例） |
| 13 | `factor_factory/mine_dispatch.py`（**新增**） | 生成器分发表 `{manual, alphagen}` → 构造器、`run_id` 前缀、默认 config 段、层级规则；manual 的默认 config **不含** alphagen 段（`config_digest` 不变，检视 D13） |
| 14 | `factor_factory/mine_config.py` | 新增独立常量 `DEFAULT_ALPHAGEN_CONFIG`（`total_timesteps`、`pool_capacity`、`datasets=["ohlcv_1m"]`、`resample="1h"`、`objective{…, position_rule:"cs_median"}`），不并入 `DEFAULT_MINE_CONFIG` |
| 15 | `factor_factory/cli.py` | 删去写死点，改调 `mine_dispatch`/`manifest_builder`/`StopController`；净增 ≤0 |

**写死点清单**（检视 D14，全部由 12/13 接管）：`cli.py:32`（`_MANUAL_CODE_DIGEST`）、`:62`（`choices=("manual",)`）、`:85`、`:99`（`generator`/`tier_level` 写死）、`:101-106`（`objective` 写死 0.0/30/{}）、`:132`（`run_id` 前缀）、`:159`（config `generator`）、`:176`（`tier_level=="manual"`）、`:221`（`GenerationRequest(generator="manual")`）、`:232`（`ManualGenerator()`）、`mine_config.py:16`（`tier_level="manual"`）。

影响面：CLI 契约、run.json schema（v2，v1 双读）、`factor_store.load` 版本判定、预筛函数新增关键字参数、生成事件（alphagen 路径开始写拒绝事件）、新增 `prefilter.jsonl`。**不改**：manual 后端行为、FactorDef schema 与 digest 规则、`run_generation` 旧路径、冒烟闸门、F007 任何代码。

## 2. 架构与模块边界

```
cli.mine  ── with install_signal_flags():               # 入口即安装（检视 D11）
  dispatch = mine_dispatch.resolve(args.generator)
  validate_binding → capability
  panel = build_tensor(validated, datasets, resample,
                       start=window.start, end=window.end, pairs=None)   # D04/D15/D21：先建张量
  training window → Kronos 卸载 → GpuSlot.acquire(cancel=flags.is_set)   # 排队可被中断
  护栏内: result = dispatch.generator.produce(request(panel=panel, stop=StopController(...)))
  factor_store.write × N ; manifest_builder.build(result, …) → run_store.finalize_run
  finally: 释放槽位 / 恢复 Kronos / writer.close()

AlphaGenGenerator.produce
  stock_data, target, pairs = build_stock_data(panel, feature_map)
  pipeline = CandidatePipeline(panel, feature_map, objective, run_id, writer, prefilter_log)
  outcome = train_with_callbacks(..., on_expression=pipeline.offer, should_stop=stop.check)
  → GenerationResult(factors=pipeline.registered, counts=pipeline.counts, pool=None,
                     stop_reason=stop.reason or "budget_exhausted", evaluations=outcome.evaluations,
                     budget={quota, total_timesteps, pool_capacity}, tier_level="L0", device=…)
```

- `CandidatePipeline` 不依赖 AlphaGen，输入是 vendor 渲染出的 token；可用纯 Python 桩单测；
- `train_with_callbacks` 只管训练与回调时机；`StopController` 是唯一停止判定点；
- 预筛信号用候选 FactorDef 的编译闭包在同一 `panel` 上计算，与 `factor_store.load` 反解走同一编译器（AC-001 逐点一致）。

## 3. 数据模型与 Migration

无数据库迁移。

**run.json v2** = v1 全部字段 +：

| 字段 | 类型 | 语义 |
|---|---|---|
| `budget` | `{quota:int, total_timesteps:int\|null, pool_capacity:int\|null}` | manual 只填 `quota` |
| `stop_reason` | `quota_reached\|budget_exhausted\|window_closed\|interrupted\|null` | manual 为 `null` |
| `evaluations` | `int\|null` | AlphaGen 环境评估次数；manual 为 `null` |
| `objective.position_rule` | `"sign"\|"cs_median"` | v1 回读缺省 `"sign"`；alphagen 为 `"cs_median"` |

规则：alphagen `completed ⇔ stop_reason ∈ {quota_reached, budget_exhausted}`；`partial ⇔ stop_reason ∈ {window_closed, interrupted}`，此时 `termination = stop_reason`、`reason = "已入册 {k}/{quota}：{stop_reason}"`；`rejected/failed` 时 `stop_reason=null`；`pool` 恒为 `null`（Q-006）。

**prefilter.jsonl**（DR-002）：每个进入预筛的候选一行 `{definition_digest, outcome, turnover, trades_90d, after_cost_return, elapsed_ms}`，经 `RunEventWriter` 同一写者写出；预筛指标不写入 FactorDef `params`——`params` 整体参与 `definition_digest`（`factor_dto.py:27-29,81-86`），写入会使同一表达式随面板变 id（检视 D06）。

**FactorDef 身份**：alphagen 表达式 token 在入册前已绑定为湖通道名（`feature:ohlcv_1m.close@1h`），因此 `definition_digest` 天然包含数据集与重采样身份（与 `feature_map_digest` 一致）；查重在绑定之后按该 digest 进行。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 接口 | 变更 | 说明 |
|---|---|---|
| `alphamill-generate mine --generator {manual,alphagen}` | 扩展 | `--quota` 对 alphagen 为入册上限 |
| `AlphaGenGenerator.produce(request) -> GenerationResult` | 新增 | `tier_level` 固定 `"L0"`；config 声明其他层级 → CLI 以 `unknown_tier` 拒绝（检视 D10） |
| `train_with_callbacks(...)` | 新增 | SB3 `BaseCallback._on_step` 返回 `should_stop() is None`；`learn()` 正常返回即 `exhausted=True` |
| `CandidatePipeline.offer(tokens) -> Outcome` | 新增 | `Registered(factor) \| Rejected(code, detail)`；`stopped` 后调用直接忽略、不计数 |
| `bind_feature_tokens(tokens, feature_map)` | 新增 | 缺通道 → `MissingChannelError` |
| `evaluate_objective(..., position_rule="sign")` | 扩展 | `cs_median` 见 §1 第 6 行 |
| `GpuSlot.acquire(..., cancel=None)` | 扩展 | 等待循环每轮检查 `cancel()`，为真即抛 `AcquireCancelled`（映射为 `partial/interrupted`） |
| `factor_store.load` | 修改 | run.json 版本 ∈ {1,2} 且 `completed` |
| `run_schema.load_run` | 迁出 + 扩展 | v1/v2 双读 |
| `RunEventWriter.append(event_type, payload)` | 新增 | 线性写出，`close()` 时 fsync |

退出码不变（0/1/2）；`partial` 退出码 0，stdout JSON 摘要含 `status`、`stop_reason`、`counts`、`budget`、预筛 p50/p95。

### Event / Trace Contract

`generation.candidate_rejected` payload = 既有 `{expression, reason_code, detail}` + 可选 `definition_digest`（`unregistered_op` 可能无 digest）；`completed` 时照旧写唯一 `generation.run_completed`（沿用 `run_store._append_event` 的唯一性检查，只一次，不在热路径）。事件 envelope 的 `schema_version` 取 `EVENT_SCHEMA_VERSION=1`，不随 run.json 升 v2（检视 D20）。**不**为 F007 改事件格式——适配归 F013。

## 5. Runtime、Workflow 与并发

```text
CandidatePipeline.offer(tokens):
  if stopped: return None                               # 配额达成后同一步的剩余表达式不计 proposed
  proposed += 1
  tokens = bind_feature_tokens(tokens, feature_map)     # MissingChannelError → Rejected(unregistered_op, missing_channel:*)
  verdict = check_expression(tokens, scope="cross_sectional")  → Rejected(unregistered_op | lookahead)
  draft = build_factor(..., params={})                  # FactorCompilationError/FeatureMapIntegrityError → Rejected(unregistered_op)
  if draft.definition_digest in seen → Rejected(duplicate_definition)
  signal = draft.compute(panel)                         # 全 NaN / 非有限 → Rejected(reachability, degenerate_signal)
  result = evaluate_objective(signal_panel, params, position_rule="cs_median")
           # SchemaValidationError（信号退化类）→ Rejected(reachability, degenerate_signal)
  prefilter_log.append(...)
  result.accepted ? Registered : Rejected(reachability, result.detail)
  registered == quota ⇒ stopped = True；StopController.mark_quota()

train_with_callbacks: 钩子 _evaluate → render → on_expression；_on_step → should_stop()
StopController.check(): 优先级 interrupted > window_closed > quota_reached
```

- 停止粒度：步边界；单 env 下每步至多一次 `_evaluate`（vendor `core.py:67-76`），配额达成后不再处理新候选；
- 信号：`install_signal_flags()` 在 `mine` 入口安装 SIGTERM/SIGINT 处理器，只置标志；检查点 = 绑定校验后、张量构建后、`GpuSlot.acquire` 等待循环每轮、训练每步；任一检查点见标志即走 `partial/interrupted`，`finally` 照常释放槽位、恢复 Kronos、关闭写者（检视 D11）；
- 事件写出：整个运行一个 `RunEventWriter`，GPU 单槽已保证单写者，不再每条加锁回读；
- 并发：仍由 GpuSlot 保证单机单跑。

## 6. UI 与可观测性

无 UI。日志：每 500 次评估一条 `INFO`（proposed/registered/各拒绝计数/预筛 p95）；停止时一条 `INFO`（`stop_reason`、耗时、显存峰值）；运行结束 stdout JSON 摘要（见 §4）。

## 7. 失败、恢复、安全与兼容

- **启动期拒绝**（run.json `rejected`，不卸载 Kronos、不取槽）：绑定非法 / 张量零行或宇宙为空（`build_tensor` 抛 `SchemaValidationError` 时由 CLI 显式映射为 `termination=invalid_binding`，不再落入 `invalid_config`，检视 D21）/ alphagen 层级非 L0（`unknown_tier`）/ 能力不足；
- **候选级拒绝**（不影响运行）：`MissingChannelError`、`FactorCompilationError`、`FeatureMapIntegrityError` → `unregistered_op`；信号全 NaN、含非有限值、`evaluate_objective` 抛 `SchemaValidationError` → `reachability`（`detail=degenerate_signal:<原因>`）；
- **运行级失败**（`failed`，ADR-0003）：`OSError`、`RunStoreError`、`MemoryError`、`torch.cuda` 错误、其他未列出的异常——不把系统故障吞成候选拒绝（检视 D05）；
- **兼容**：manual 可观察等价（`factors/` 逐字节、`config_digest` 不变、run.json 除 `schema_version` 与 v2 新字段外逐项相等）；基准由改动前 main 在临时 detached worktree 上以同一绑定/种子实跑取得并固化为测试夹具（检视 D13）；v1 run.json 与 v1 下的因子仍可读；
- **安全**：训练、预筛、写出都在 egress 与写路径护栏内；`prefilter.jsonl` 位于 `run_dir`，写路径护栏允许；
- **恢复**：`partial` 不续跑；已入册候选只供排障查看。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f012_alphagen_mining.py`：scratch 湖小面板真实训练 | 入册因子通道已绑定、`mechanism_unknown`；v2 下 `factor_store.load` 反解逐点一致；v1 manual 仍可 load |
| `AC-002` | integration | 同上：`--quota 3` / 极小步数；窗口跨度 | 入册数与 `stop_reason`；面板时间跨度 == 窗口 |
| `AC-003` | unit | `tests/unit/test_f012_candidate_pipeline.py`：恒定信号、截面排名因子、阈值边界、全 NaN/inf | `reachability`；`cs_median` 下有交易；退化为候选拒绝；`prefilter.jsonl` 行数与身份 |
| `AC-004` | unit | 同上：重复 token、缺通道 token、事件计数、1 万条写出计时 | `duplicate_definition`；`missing_channel`；事件 == `counts.rejected`；守恒；线性 |
| `AC-005` | unit | `tests/unit/test_f012_stop_conditions.py`：夜槽结束、训练中 SIGTERM、等槽时 SIGTERM（桩 GpuSlot） | `partial` + `stop_reason/termination/reason`；`pool=null`；load 拒绝；释放/恢复被调用 |
| `AC-006` | unit | `tests/unit/test_f012_cli_contract.py`：manual 基准夹具对照、alphagen 分发、未知生成器、非 L0、零行张量 | 逐项等价；argparse 拒绝；`unknown_tier`；`invalid_binding` 且 Kronos 卸载未被调用 |
| `AC-007` | unit | `tests/unit/test_f012_run_schema.py`：v2 字段、v1 回读 | 字段如实；`code_digest != config_digest` |
| `AC-008` | integration | `tests/integration/test_f012_alphagen_mining.py`：两个成员集合不同的绑定 | `pair_count` 不同且 == 面板 pair 数 |
| `AC-009` | integration（执行机取证） | CLI 实跑 + `tests/integration/test_f012_capacity_evidence.py` 校验 `reports/f012/capacity-evidence.json` | 字段齐全、与 run.json 一致；未达 50 时产能发现已登记 |

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 回调式训练独立入口 | 新增 `train_with_callbacks`，`run_generation` 原样保留 | F003 用例依赖旧路径的 `run_id` 与 manifest（检视 D19） | — |
| 停止实现 | SB3 `BaseCallback._on_step` 返回 False | 官方停止机制 | — |
| 截面仓位规则 | `cs_median`（Q-005） | 与 F007 多空分位口径一致 | — |
| 取数范围 | 窗口起止 + `pairs=None`，靠 `build_tensor` 逐时点 PIT 掩码 | 不以终点成员筛历史（数据红线，检视 D04） | — |
| 预筛指标去向 | `prefilter.jsonl` 旁路文件 | `params` 进 digest（检视 D06） | — |
| 事件写出 | 运行内单写者、批量 fsync | 原每条回读全文件 O(n²)（检视 D07） | — |
| 编译器组装 | `default_compilers.full_registry()` 惰性导入 | 打破导入环（检视 D18） | — |
| 行数 | 迁出 `run_schema`/`manifest_builder`/`mine_dispatch`，再导出保持导入方不变 | SOP 350 行 | — |
| 残余风险：CUDA 非确定性 | NFR-002 只对 CPU 严格；CUDA 记录来源 | cuDNN/原子操作 | — |
| 残余风险：夜槽入册不足 50 | 如实登记 M2 产能发现（Q-007） | ADR-0008 | owner 裁决预算/宇宙 |
| 残余风险：预筛 p95 超 1 s | T002 执行机先测，超限先回写加速方案并裁决 | 不得静默跳过/抽样 | — |

## 10. 待确认设计问题

无
