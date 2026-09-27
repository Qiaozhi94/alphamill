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

- **行为契约**：`spec.md`（`FR-001`~`FR-008`、`AC-001`~`AC-010`；§8 `Q-001`~`Q-007` 已裁决）
- **PRD / Architecture**：PRD FR2.1–FR2.4、FR2.6；架构 §7.1（夜槽、GPU 单槽、Kronos 卸载）；数据红线（研究只读 PIT 湖、不引入幸存者偏差）
- **ADR / 上游 Contract**：ADR-0001（alphagen = L0）、ADR-0003（必需计算失败不得静默放行）、ADR-0006、ADR-0008；F003 `DR-003`、`TR-002`、run_store/factor_store 不变量
- **实现约束**：`src/**/*.py` ≤350 行——`factor_factory/cli.py` 现 343、`registry/run_store.py` 现 350、`registry/factor_store.py` 现 267，新增逻辑进新模块，前两者净增 ≤0；无 torch 环境（含 CI）必须可收集（F003 惰性导入约定）；本设计对现有代码的每条声明均以文档检视第 1、2 轮核对过的行号为准（第 2 轮 D23–D36）

## 1. 技术概要与影响面

| # | 文件 | 变更 |
|---|---|---|
| 1 | `generators/candidate_pipeline.py`（**新增**） | `CandidatePipeline.offer(tokens)`：通道绑定 → 自检 → 查重 → 预筛 → 入册/拒绝；计数守恒；候选级异常分类（§7）；纯 Python |
| 2 | `generators/alphagen_training.py`（**新增**） | `train_with_callbacks(*, stock_data, target, device, seed, total_timesteps, on_expression, should_stop, pool_capacity=10) -> TrainingOutcome{evaluations, stopped, timesteps}`：回调式训练独立入口；SB3 日志器显式设为无输出（缺省日志器即使 `verbose=0` 也在系统临时目录建目录，被写护栏拒）；`warm_runtime()` 供 CLI 在写护栏安装前预热导入期副作用（`torch._dynamo` 首次导入建 inductor 缓存目录）；SB3 回调停止时 `learn()` 同样正常返回，故以 `stopped` 标志区分而非「正常返回即耗尽」（检视 D33）；**`alphagen_generation.run_generation` 原样保留**（检视 D19） |
| 2b | `generators/alphagen_runner.py` | **修正 `render_expression` / `_operator_token`（F003 既有缺陷，检视 D23）**：滚动算子（`Ref/Mean/Sum/Std/Var/Max/Min/Med/Mad/Delta/WMA/EMA`）以末位 `DeltaTime` 渲染为 `name:N`，窗口不再丢失；成对滚动算子 `Cov/Corr`（非 RollingOperator 子类，现渲染为 `…,'delta:N','corr'`）改为以末位 `DeltaTime` 渲染为 `corr:N`/`cov:N`——二者已登记（`operator_registry.py:41,48`，arity 2 见 `:163`）且可编译，按正常候选处理（检视 D37）；`CSRank` → `cs_rank`；时序 `Rank(x,N)` → `ts_rank:N`（未登记 ⇒ `unregistered_op`，不再错译为 `cs_rank`）。vendor 默认动作空间（`alphagen/config.py` `OPERATORS`，不含 `Rank`/`CSRank`）保持不改（vendor 零修改）。`run_generation` 代码不改，但因调用 `render_expression`（`alphagen_generation.py:107`）其 token 输出随修正而变；仓内无测试钉住旧渲染结果（检视 D39） |
| 3 | `generators/alphagen_generator.py`（**新增**） | `AlphaGenGenerator(ctx: BuildContext).produce(request)`：以 `request.panel`（CLI 已建好的张量）→ stock_data → 训练 → 流水线 → `GenerationResult`；停止判定、事件写者、编译器注册表与 `device` 经 `BuildContext` 注入（检视 D31）；`BuildContext`、`objective_params`、`ALPHAGEN_GENERATOR_VERSION` 定义在 `generators/alphagen_context.py`（生成器不反向导入 CLI 层，代码检视 R-C6）；配额恰在最后一步达成而训练未被叫停时仍记 `quota_reached` |
| 4 | `generators/channel_binding.py`（**新增**） | `bind_feature_tokens(tokens, feature_map) -> tokens`：`feature:<basename>` → `feature:<dataset>.<column>@<resample>`，映射规则与 `alphagen_runner.build_stock_data:162-166` 的 FeatureType 槽位同源（取 `name.split('.')[-1].split('@')[0].lower()`）；无对应通道 → `MissingChannelError(name)`（检视 D02）；多个数据集出现同名 basename（会被 `build_stock_data` 后写者覆盖）⇒ 启动期以 `invalid_config` 拒绝（检视 D35） |
| 5 | `generators/stop_conditions.py`（**新增**） | `StopController`：配额、夜槽（复用纯函数 `gpu_slot.in_training_window`）、信号标志 → `stop_reason`；`install_signal_flags()` 上下文管理器 |
| 6 | `generators/objective.py` | `evaluate_objective(..., position_rule="sign")` 新增关键字 `position_rule ∈ {"sign","cs_median"}`；`cs_median` = 每个时点在宇宙内 pair 上 `signal − median(signal)` 后取符号（owner 裁决 Q-005，检视 D03）；缺省 `sign` 保持 F003 用例不变 |
| 7 | `generators/base.py` | `GenerationResult` 末尾增可选字段 `stop_reason=None`、`evaluations=None`、`budget=None`；`GenerationRequest` 末尾增可选字段 `panel: TensorPanel \| None = None`（默认值使 `ManualGenerator` 不改，检视 D09/D31） |
| 8 | `registry/run_schema.py`（**新增**） | 自 `run_store.py` 迁出：`RUN_SCHEMA_VERSION=2`（当前写入版本；`test_f003_run_store.py:256` 断言 `+1` 被拒仍成立）、`RUN_SCHEMA_VERSIONS={1,2}`、`RunStatus`、`TierLevel`、`GenerationRun`、`EngineInfo`、`UniverseSummary`、`ObjectiveInfo`（增 `position_rule`，v1 缺省 `"sign"`）、`load_run`、`_validate_terminal`、`_parse_model`（按版本分派字段集，v1 严格集不含 v2 字段）；`run_store.py` 以 `from .run_schema import …` 再导出**上述全部名字**，导入方（`test_f003_run_store.py:25-37`、`cli.py:83`、`alphagen_generation.py:167`、`objective.py`）零改动（检视 D22/D29） |
| 9 | `registry/event_writer.py`（**新增**） | `RunEventWriter`：运行内单写者（单写者由 `run_id` 唯一保证，与是否取 GPU 槽无关，`--allow-cpu` 同样成立）；打开时读一次现有行数得 seq，此后每条以**无用户态缓冲**的 `os.write` 追加、不回读，每 256 条及 `close()` 时 fsync（检视 D07/D30）；`close()` 必须在 `finalize_run` 与 `_finish_error` **之前**调用，保证 run.json 发布时事件已落盘、`_append_event` 取到的 seq 正确；事件 schema 版本常量 `EVENT_SCHEMA_VERSION=1` 定义在叶子模块 `run_schema.py`（`run_store` 与 `event_writer` 都从那里取，避免二者互相导入成环，检视 D40），`run_store.append_candidate_rejected`（`:143`）与 `finalize_run`（`:166`）的事件信封改用它，与 run schema 解耦（检视 D20/D29） |
| 10 | `registry/factor_store.py` | `load` 的 run.json 校验改为 `schema_version ∈ run_schema.RUN_SCHEMA_VERSIONS` 且 `status=="completed"`（原比较 `FACTOR_SCHEMA_VERSION`，检视 D01）；`build_factor`（`:73`）与 `load` 的 `compilers` 缺省改为 `None` → 函数内惰性取 `default_compilers.full_registry()`（`write` 无此参数，不改；检视 D18/D28） |
| 11 | `registry/default_compilers.py`（**新增**） | `full_registry()`：`{manual: compile_postfix, alphagen: …}`，在函数内导入 `alphagen_adapter`，打破 `compiler_registry→adapter→factor_store→compiler_registry` 环（检视 D18）；`compiler_registry.DEFAULT_COMPILERS` 不动 |
| 12 | `factor_factory/manifest_builder.py`（**新增**） | 唯一 run.json 构建器：自 `cli.py` 迁出 `_SeedState`、`_manifest`，按生成器取字段（检视 D14）；alphagen 路径不再调用 `write_generation_manifest`（该函数仅留给 F003 冒烟用例） |
| 13 | `factor_factory/mine_dispatch.py`（**新增**） | 生成器分发表 `{manual, alphagen}` → 构造器、`run_id` 前缀、默认 config、层级规则、universe 汇总取值（`cli.py:163-168` 的汇总也按生成器取，检视 D14）。**config 合成顺序**（检视 D27）：manual = `DEFAULT_MINE_CONFIG` + 用户 `--config`（与现状一致，`config_digest` 不变）；alphagen = `DEFAULT_MINE_CONFIG` 公共段（显存/排队/时段/Kronos） + `DEFAULT_ALPHAGEN_CONFIG`（覆盖 `tier_level="L0"`） + 用户 `--config`；其中 `objective` 段做一层深合并（用户只给部分键时其余键取缺省，`position_rule` 不会静默退回 `sign`，检视 D44），其余键浅合并与现状一致 |
| 14 | `factor_factory/mine_config.py` | 新增独立常量 `DEFAULT_ALPHAGEN_CONFIG`（`tier_level="L0"`、`total_timesteps`、`pool_capacity`、`datasets=["ohlcv_1m"]`、`resample="1h"`、`objective{…, position_rule:"cs_median"}`），不并入 `DEFAULT_MINE_CONFIG` |
| 15 | `factor_factory/cli.py` | 删去写死点，改调 `mine_dispatch`/`manifest_builder`/`StopController`；净增 ≤0 |
| 16 | `generators/gpu_slot.py` | `acquire(..., cancel=None)`：等待循环每轮检查 `cancel()`；为真时**先追加队列终态记录 `cancelled`**（`QueueRecord.event` 增此值；`_waiting_head` 只认最新记录为 `queued` 者，故取消即出队）再抛 `AcquireCancelled`（检视 D11/D25） |
| 17 | `generators/lake_tensor.py` | 新增 `pairs_during(ledger: UniverseLedger, start, end) -> tuple[str, ...]`：窗口内任一时点属于宇宙的 pair 并集（由绑定的宇宙台账区间求交），作为 `build_tensor(pairs=...)` 的输入——仍逐时点 PIT 掩码，不以终点成员筛历史，且只读宇宙相关 pair（检视 D04/D24） |

**代码检视回写**（循环 26 第 1 轮，2026-09-27）：
- 取数窗口与重采样（R-B4 → R2-1）：`ohlcv_1m.time` 是 K 线开盘时间。`lake_tensor._aggregate` 由右闭右标签改为**左闭右标签**（原口径让标签 H 含 H 开盘、H+1m 才收盘的那根，前视 1 分钟；F003 既有），`prepare_panel` 按原窗口调 reader `[start, end)`，标签 ∈ `(start, end]` 且最后一根在 cutoff 收盘、不越绑定截止；第 1 轮曾以 ±1µs 偏移对齐右闭口径，第 2 轮查出其把 cutoff 开盘的 K 线拉进 cutoff 标签而撤销；T019 夜槽证据按新口径重取（owner 2026-09-27）；
- 启动期（卸载 Kronos 前）校验：`compose_config` 后立即解析 `objective_params`，缺键/错型 → `invalid_config`（R-A2）；`objective.position_rule` 只接受 `cs_median`（预筛只实现该规则，Q-005，R-A3）；
- 异常归属：`manifest_builder.finish_exception` 以 `config_phase`（进入生成器之前）区分——仅该阶段的 Schema/Type/ValueError 记 `invalid_config`，生成器内一律 `failed`；未列出的异常同样收尾为 `failed` 并写 run.json（R-A1/R-A2，兑现 §7）；
- 信号：仅 `mine` 安装 `install_signal_flags`，生成前再加一个中断检查点（manual 同样经过，R-A4）；
- 预筛带上面板中唯一的 funding 通道（`objective.funding_feature_columns` 同一口径），`funding_8h_bps` 生效（R-B3）；`CandidatePipeline.prefilter_ms` 供每 500 次评估的进度日志算 p95；生成器在 CLI 未配置 logging 时自挂 stderr handler。

**写死点清单**（检视 D14，全部由 12/13 接管；另 `cli.py:163-168` universe 汇总由 13 按生成器取）：`cli.py:32`（`_MANUAL_CODE_DIGEST`）、`:62`（`choices=("manual",)`）、`:85`、`:99`（`generator`/`tier_level` 写死）、`:101-106`（`objective` 写死 0.0/30/{}）、`:132`（`run_id` 前缀）、`:159`（config `generator`）、`:176`（`tier_level=="manual"`）、`:221`（`GenerationRequest(generator="manual")`）、`:232`（`ManualGenerator()`）、`mine_config.py:16`（`tier_level="manual"`）。

影响面：CLI 契约、run.json schema（v2，v1 双读）、`factor_store.load` 版本判定、预筛函数新增关键字参数、生成事件（alphagen 路径开始写拒绝事件）、新增 `prefilter.jsonl`。**不改**：manual 后端行为、FactorDef schema 与 digest 规则、`run_generation` 代码（其 token 输出随渲染修正而变，检视 D39）、冒烟闸门、F007 任何代码。

## 2. 架构与模块边界

```
cli.mine  ── with install_signal_flags():               # 入口即安装（检视 D11）
  dispatch = mine_dispatch.resolve(args.generator)
  validate_binding → capability
  pairs = pairs_during(validated.universe_ledger, window.start, window.end)           # D24：窗口内宇宙成员并集
  panel = build_tensor(validated, datasets=..., resample=...,
                       start=window.start, end=window.end, pairs=pairs)  # D04/D15/D21：先建张量
  panel 校验：__in_universe__.any() 否则 invalid_binding；同名 basename 否则 invalid_config（D34/D35）
  training window → Kronos 卸载 → GpuSlot.acquire(cancel=flags.is_set)   # 排队可被中断
  护栏内: generator = dispatch.build(stop=StopController(...), writer=RunEventWriter(run_dir),
                                    compilers=full_registry())
          result = generator.produce(GenerationRequest(..., panel=panel))
  factor_store.write × N ; writer.close()（先于 finalize） ; manifest_builder.build(result, …) → run_store.finalize_run
  异常路径：writer.close() → _finish_error
  finally: 释放槽位 / 恢复 Kronos

AlphaGenGenerator.produce(request)
  stock_data, target, pairs = build_stock_data(request.panel, feature_map=request.panel.feature_map)
  pipeline = CandidatePipeline(panel, feature_map, objective, run_id, writer, prefilter_log)
  outcome = train_with_callbacks(..., on_expression=pipeline.offer, should_stop=stop.check)
  → GenerationResult(factors=pipeline.registered, counts=pipeline.counts, pool=None,
                     stop_reason=stop.reason if outcome.stopped else "budget_exhausted", evaluations=outcome.evaluations,
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

**universe 汇总**（检视 D24/D43）：alphagen 运行的 `pair_count` = 面板中 `__in_universe__` 在窗口内至少一次为真的 pair 数（不是湖内 pair 数）；manual 运行沿用现状（`cli.py:163-168` 取 `universe_at(cutoff_time)`）以保持 `FR-006` 等价；`source` 取绑定的宇宙来源（显式绑定为 `explicit`）。

**FactorDef 身份**：alphagen 表达式 token 在入册前已绑定为湖通道名（`feature:ohlcv_1m.close@1h`），因此 `definition_digest` 天然包含数据集与重采样身份（与 `feature_map_digest` 一致）；查重在绑定之后按该 digest 进行。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 接口 | 变更 | 说明 |
|---|---|---|
| `alphamill-generate mine --generator {manual,alphagen}` | 扩展 | `--quota` 对 alphagen 为入册上限 |
| `AlphaGenGenerator.produce(request) -> GenerationResult` | 新增 | `tier_level` 固定 `"L0"`；config 声明其他层级 → CLI 以 `unknown_tier` 拒绝（检视 D10） |
| `train_with_callbacks(*, ...)` | 新增 | SB3 `BaseCallback._on_step` 返回 `should_stop() is None`；返回 `stopped`（回调叫停）与 `evaluations` |
| `CandidatePipeline.offer(tokens) -> Outcome` | 新增 | `Registered(factor) \| Rejected(code, detail)`；`stopped` 后调用直接忽略、不计数 |
| `bind_feature_tokens(tokens, feature_map)` | 新增 | 缺通道 → `MissingChannelError` |
| `evaluate_objective(..., position_rule="sign")` | 扩展 | `cs_median` 见 §1 第 6 行 |
| `GpuSlot.acquire(..., cancel=None)` | 扩展 | 等待循环每轮检查 `cancel()`，为真即先写 `cancelled` 队列记录再抛 `AcquireCancelled`（映射为 `partial/interrupted`） |
| `lake_tensor.pairs_during(ledger, start, end)` | 新增 | 窗口内宇宙成员并集 |
| `render_expression(expr)` | 修正 | 滚动与成对滚动算子 `name:N`、`CSRank→cs_rank`、`Rank→ts_rank:N`（见 §1 第 2b 行） |
| `factor_store.load` | 修改 | run.json 版本 ∈ {1,2} 且 `completed` |
| `run_schema.load_run` | 迁出 + 扩展 | v1/v2 双读 |
| `RunEventWriter.rejected(expression, reason_code, detail, *, definition_digest=None)` / `.prefilter(record)` | 新增 | 无缓冲线性写出（events.jsonl / prefilter.jsonl），批量与 `close()` 时 fsync；`close()` 先于 finalize |

退出码不变（0/1/2）；`partial` 退出码 0，stdout JSON 摘要含 `run_id`、`generator`、`status`、`stop_reason`、`counts`、`budget`、预筛 p50/p95、`vram_peak_gb`（CUDA 时为 `torch.cuda.max_memory_allocated`，否则 null）；摘要在 run.json 发布后打印，失败只告警、不改退出码（代码检视 R-A5）。`prefilter.jsonl` 每条进入预筛的候选一行：`definition_digest`、`masked_bars`、`outcome`、`elapsed_ms`，走到目标函数的另含 `turnover`/`trades_90d`/`after_cost_return`（退化候选无这三项）。

### Event / Trace Contract

`generation.candidate_rejected` payload = 既有 `{expression, reason_code, detail}` + 可选 `definition_digest`（`unregistered_op` 可能无 digest）；`completed` 时照旧写唯一 `generation.run_completed`（沿用 `run_store._append_event` 的唯一性检查，只一次，不在热路径）。事件 envelope 的 `schema_version` 取 `EVENT_SCHEMA_VERSION=1`，不随 run.json 升 v2（检视 D20）。**不**为 F007 改事件格式——适配归 F013。

## 5. Runtime、Workflow 与并发

```text
CandidatePipeline.offer(tokens):
  if stopped: return None                               # 配额达成后同一步的剩余表达式不计 proposed
  proposed += 1
  tokens = bind_feature_tokens(tokens, feature_map)     # MissingChannelError → Rejected(unregistered_op, missing_channel:*)
  verdict = check_expression(tokens, scope="cross_sectional",
                             seen_definition_digests=frozenset(), definition_digest="")
            # 先按 purity 的归属顺序分类（unknown → lookahead），避免缺窗口 token 在编译期被误记（检视 D42）
            # 拒: unregistered_op | lookahead；畸形 token 抛 SchemaValidationError → Rejected(unregistered_op)
  draft = build_factor(..., params={}, compilers=registry)   # FactorCompilationError/FeatureMapIntegrityError → Rejected(unregistered_op)
  if draft.definition_digest in seen → Rejected(duplicate_definition)
  seen.add(draft.definition_digest)                     # 编译成功即入 seen：退化/预筛被拒者再次出现也判 duplicate（检视 D45）
  signal = draft.compute(panel)
  signal = signal.where(close 可得 且 close > 0)         # close 缺失或非正的 bar 视为未观测（先掩码，检视 D41），计入 masked_bars
  若在宇宙内已无任何非 NaN 信号，或含非有限值 → Rejected(reachability, degenerate_signal)
  result = evaluate_objective(signal_panel, params=objective_params, position_rule="cs_median")
           # 此时 SchemaValidationError 只剩面板/列结构类 ⇒ 系统级，运行 failed（不伪装成候选拒绝）
  prefilter_log.append(...)
  result.accepted ? Registered : Rejected(reachability, result.detail)
  registered == quota ⇒ stopped = True；StopController.mark_quota()

train_with_callbacks: 钩子 _evaluate → render → on_expression；_on_step → should_stop()
StopController.check(): 优先级 interrupted > window_closed > quota_reached
```

- 停止粒度：步边界；单 env 下每步至多一次 `_evaluate`（vendor `core.py:67-76`），配额达成后不再处理新候选；`check_expression` 以真实签名调用（`purity.py:35-42`）且先于编译做归属分类，查重在编译后按 `definition_digest` 对 `seen` 进行；`evaluate_objective` 与 `build_stock_data` 的参数均按仅限关键字传入（`objective.py:172-177`、`alphagen_runner.py:143-148`，检视 D33）；
- 信号：`install_signal_flags()` 在 `mine` 入口安装 SIGTERM/SIGINT 处理器，只置标志；检查点 = 绑定校验后、张量构建后、`GpuSlot.acquire` 等待循环每轮、训练每步；任一检查点见标志即走 `partial/interrupted`：先 `writer.close()` 再 finalize（partial）或 `_finish_error`（异常），`finally` 只负责释放槽位、恢复 Kronos，并对写者做幂等兜底 close（检视 D11/D38）；
- 事件写出：整个运行一个 `RunEventWriter`，单写者由 `run_id` 唯一保证，不再每条加锁回读；`finalize_run` 内唯一一次 `_append_event` 在 `writer.close()` 之后执行，seq 连续；
- 并发：仍由 GpuSlot 保证单机单跑。

## 6. UI 与可观测性

无 UI。日志：每 500 次评估一条 `INFO`（proposed/registered/各拒绝计数/预筛 p95）；停止时一条 `INFO`（`stop_reason`、耗时、显存峰值）；运行结束 stdout JSON 摘要（见 §4）。

## 7. 失败、恢复、安全与兼容

- **启动期拒绝**（run.json `rejected`，不卸载 Kronos、不取槽）：绑定非法；张量零行（`build_tensor` 零行抛 `SchemaValidationError`，`lake_tensor.py:130,153`）或窗口内宇宙为空（`build_tensor` 不抛错，由建后校验 `__in_universe__.any()` 判定，检视 D34）→ `termination=invalid_binding`；`datasets`/`resample` 非法（`lake_tensor.py:86-96,109`）或同名 basename 冲突 → `invalid_config`；alphagen 层级非 L0 → `unknown_tier`；能力不足；
- **候选级拒绝**（不影响运行）：`MissingChannelError`、`FactorCompilationError`、`FeatureMapIntegrityError`、`check_expression` 对畸形 token 抛的 `SchemaValidationError`（`purity.py:63-149`）→ `unregistered_op`；close 缺失或非正的 bar 先视为未观测（不报错、计数留痕，检视 D32/D41），之后在宇宙内无任何非 NaN 信号或含非有限值 → `reachability`（`detail=degenerate_signal:<原因>`）；
- **运行级失败**（`failed`，ADR-0003）：`OSError`、`RunStoreError`、`MemoryError`、`torch.cuda` 错误、`CompilerNotRegisteredError`（编译器未组装属配置缺陷）、`evaluate_objective` 的面板/列结构类 `SchemaValidationError`、其他未列出的异常——不把系统故障或数据缺陷伪装成候选拒绝（检视 D05/D28/D32）；
- **兼容**：manual 可观察等价（检视 D26）：因子文件名集合一致，且因子内容剔除 `run_id`、`created_at` 后逐字节一致；`config_digest` 不变；run.json 剔除易变字段（`run_id`、`started_at`、`finished_at`、`hostname`）、`schema_version` 与 v2 新字段后逐项相等；基准由改动前 main 在临时 detached worktree 上以同一绑定/种子实跑取得并固化为测试夹具（检视 D13）；v1 run.json 与 v1 下的因子仍可读；
- **安全**：训练、预筛、写出都在 egress 与写路径护栏内；`prefilter.jsonl` 位于 `run_dir`，写路径护栏允许；
- **恢复**：`partial` 不续跑；已入册候选只供排障查看。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f012_alphagen_mining.py`：scratch 湖小面板真实训练 | 入册因子通道已绑定、`mechanism_unknown`；v2 下 `factor_store.load` 反解逐点一致；v1 manual 仍可 load |
| `AC-002` | integration | 同上：`--quota 3` / 极小步数；窗口跨度 | 入册数与 `stop_reason`；面板首尾时间戳 ∈ `(window.start, window.end]`（`time` 为 1m K 线开盘时间：reader `[start, end)` + 1h 重采样 `closed="left", label="right"`，标签 H 只含 H 前已收盘的 K 线；检视 D36，代码检视 R2-1 由右闭改左闭以消除 1 分钟前视） |
| `AC-003` | unit | `tests/unit/test_f012_candidate_pipeline.py`：恒定信号、截面排名因子、阈值边界、全 NaN/inf | `reachability`；`cs_median` 下有交易；退化为候选拒绝；`prefilter.jsonl` 行数与身份 |
| `AC-004` | unit | 同上：重复 token、缺通道 token、畸形 token、事件计数、1 万条写出计时、`close` 先于 finalize | `duplicate_definition`；`missing_channel`；畸形 → `unregistered_op`；事件 == `counts.rejected`；守恒；线性 |
| `AC-010` | unit | `tests/unit/test_f012_render.py`：vendor `OPERATORS` 逐算子构造表达式渲染后过 `check_expression` | 滚动算子带窗口不再判 lookahead；`Cov/Corr` 渲染为 `corr:N`/`cov:N`、通过 `check_expression` 并能被 `build_factor` 编译；`CSRank→cs_rank`；`Rank→ts_rank:N` 以 `unregistered_op` 拒绝 |
| `AC-005` | unit | `tests/unit/test_f012_stop_conditions.py`：夜槽结束、训练中 SIGTERM、等槽时 SIGTERM（真实 GpuSlot 队列文件） | `partial` + `stop_reason/termination/reason`；`pool=null`；load 拒绝；释放/恢复被调用；取消后队列有 `cancelled` 记录且下一 run 能取到槽 |
| `AC-006` | unit | `tests/unit/test_f012_cli_contract.py`：manual 基准夹具对照、alphagen 分发与 config 合成、未知生成器、非 L0、零行张量、空宇宙、同名 basename | 按 D26 口径等价；alphagen 缺省 `tier_level=L0`；用户只给部分 `objective` 键时 `position_rule` 仍为 `cs_median`；argparse 拒绝；`unknown_tier`；零行/空宇宙 `invalid_binding` 且 Kronos 卸载未被调用；同名 basename `invalid_config` |
| `AC-007` | unit | `tests/unit/test_f012_run_schema.py`：v2 字段、v1 回读 | 字段如实；`code_digest != config_digest` |
| `AC-008` | integration | `tests/integration/test_f012_alphagen_mining.py`：数据版本相同、宇宙成员不同的两个显式绑定 | `pair_count` 不同，且 == 各自面板中窗口内曾在宇宙的 pair 数 |
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
| 渲染器修正归 F012 | 修 F003 `render_expression` 丢窗口缺陷；vendor 动作空间不改 | 不修则绝大多数候选被错判 lookahead，产能与漏斗失真（检视 D23） | — |
| 取数 pair 集 | 窗口内宇宙成员并集 + 逐时点掩码 | `pairs=None` 读全湖且 `pair_count` 失真（检视 D24） | — |
| 残余风险：CUDA 非确定性 | NFR-002 只对 CPU 严格；CUDA 记录来源 | cuDNN/原子操作 | — |
| 残余风险：夜槽入册不足 50 | 如实登记 M2 产能发现（Q-007） | ADR-0008 | owner 裁决预算/宇宙 |
| 残余风险：预筛 p95 超 1 s | T002 执行机先测，超限先回写加速方案并裁决 | 不得静默跳过/抽样 | — |

## 10. 待确认设计问题

无
