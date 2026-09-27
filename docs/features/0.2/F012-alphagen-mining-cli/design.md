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

- **行为契约**：`spec.md`（`FR-001`~`FR-007`、`AC-001`~`AC-008`）
- **PRD / Architecture**：PRD FR2.1–FR2.4、FR2.6；架构 §7.1（夜槽、GPU 单槽、Kronos 卸载）
- **ADR / 上游 Contract**：ADR-0001、ADR-0003、ADR-0006、ADR-0008；F003 `DR-003`（alphagen 因子假设 `mechanism_unknown`）、`TR-002`（`generation.candidate_rejected` 事件）、run_store/factor_store 不变量
- **实现约束**：`src/**/*.py` ≤350 行——`factor_factory/cli.py` 现 343 行、`registry/run_store.py` 现 350 行，本 feature 的新增逻辑一律放新模块，两文件净增 ≤0；唯一门禁入口 `tools/verify.py`；无 torch 环境（含 CI）必须可收集（沿用 F003 惰性导入约定）

## 1. 技术概要与影响面

| # | 文件 | 变更 |
|---|---|---|
| 1 | `factor_factory/generators/candidate_pipeline.py`（**新增**） | `CandidatePipeline`：单表达式的 渲染 → 自检 → 查重 → 预筛 → 入册/拒绝；持有计数与拒绝事件写出器；纯 Python，无 torch |
| 2 | `factor_factory/generators/alphagen_generator.py`（**新增**） | `AlphaGenGenerator(Generator)`：`produce()` 编排 `build_tensor → build_stock_data → run_generation`，注入 run_id、流水线与停止判定；产出 `GenerationResult` |
| 3 | `factor_factory/generators/alphagen_generation.py` | `run_generation` 增 `on_expression`（每次评估回调）与 `should_stop`（停止判定）参数，经 SB3 `BaseCallback` 在步边界停止；移除内部 run_id 生成与事后统一自检；保留旧签名路径供冒烟用例（无回调时行为不变） |
| 4 | `factor_factory/generators/stop_conditions.py`（**新增**） | `StopController`：配额、夜槽时段、SIGTERM/SIGINT 标志 → `stop_reason` |
| 5 | `factor_factory/registry/run_schema.py`（**新增**） | 从 `run_store.py` 迁出 `GenerationRun` 字段定义与 `load_run` 校验，支持 v1/v2；`run_store.py` 只保留写入与事件，腾出行数 |
| 6 | `factor_factory/mine_dispatch.py`（**新增**） | 生成器分发表 `{manual, alphagen}` → 构造器、`run_id` 前缀、默认 config 段、层级校验、manifest 字段；`cli.py` 只调用它（净增 ≤0） |
| 7 | `factor_factory/mine_config.py` | 新增 `alphagen` 段缺省：`total_timesteps`、`pool_capacity`、`datasets=["ohlcv_1m"]`、`resample="1h"`、`objective{...}`、`tier_level="L0"` |
| 8 | `factor_factory/compiler_registry.py` | `DEFAULT_COMPILERS` 注册 alphagen 编译器（调用既有 `register_alphagen_compiler`） |

影响面：CLI 契约（`--generator` 增 `alphagen`）、run.json schema（v2，v1 只读兼容）、生成事件（alphagen 路径开始写拒绝事件）。**不改**：manual 后端行为、FactorDef schema、factor_store 落盘结构、冒烟闸门、F007 任何代码。

## 2. 架构与模块边界

```
cli.mine
  └─ mine_dispatch.resolve(generator) → Spec{build, run_prefix, tier_rule, manifest_fields}
       ├─ 既有护栏链：validate_binding → capability → 时段 → Kronos 卸载 → GpuSlot → egress/写路径护栏
       └─ AlphaGenGenerator.produce(request)
            ├─ lake_tensor.build_tensor(validated, datasets, resample, pairs=universe_at(cutoff))
            ├─ alphagen_runner.build_stock_data(panel, feature_map)
            ├─ StopController(quota, window, signals)
            ├─ CandidatePipeline(panel, objective_params, feature_map, run_id, events_writer)
            └─ alphagen_generation.run_generation(..., on_expression=pipeline.offer,
                                                   should_stop=stop.check)
                 → GenerationResult(factors=pipeline.registered, counts=pipeline.counts, …)
  factor_store.write × N → run_store.write_config → run_store.finalize_run(v2 字段)
```

- `CandidatePipeline` 不知道 AlphaGen：输入是渲染后的 token 序列，输出是 FactorDef 或拒绝；可用纯 Python 桩驱动单测；
- `run_generation` 只负责训练与回调时机，不做入册判断；
- `StopController` 是唯一停止判定点，`stop_reason` 只在这里产生；
- 预筛信号计算复用 FactorDef 的编译闭包（同一 `feature_map`、同一面板），保证「入册时算的」与「反解后算的」是同一函数（AC-001）。

## 3. 数据模型与 Migration

无数据库迁移。`run.json` v2 = v1 全部字段 +：

| 字段 | 类型 | 语义 |
|---|---|---|
| `budget` | `{quota:int, total_timesteps:int\|null, pool_capacity:int\|null}` | manual 只填 `quota` |
| `stop_reason` | `quota_reached\|budget_exhausted\|window_closed\|interrupted\|null` | manual 为 `null` |
| `evaluations` | `int\|null` | AlphaGen 环境评估次数（`core.eval_cnt`）；manual 为 `null` |

规则：`completed ⇔ stop_reason ∈ {quota_reached, budget_exhausted}`（alphagen）；`partial ⇔ stop_reason ∈ {window_closed, interrupted}`；`rejected/failed` 时 `stop_reason=null`。`load_run` 按 `schema_version ∈ {1,2}` 分派字段集校验，v1 缺省三字段视为 `null`。

入册 FactorDef `params` 增 `prefilter{turnover, trades_90d, after_cost_return}`（DR-002），参与 `definition_digest` 之外（与 `run_id` 同属排除字段）——**注意**：若 `params` 进入 digest，则同一表达式因面板不同而 digest 不同，破坏跨运行同一 id；实现须核对 `factor_store` digest 排除集，必要时把 `prefilter` 放入排除集（T002 核对）。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 接口 | 变更 | 说明 |
|---|---|---|
| `alphamill-generate mine --generator {manual,alphagen}` | 扩展 | 其余参数不变；`--quota` 对 alphagen 为入册上限 |
| `AlphaGenGenerator.produce(request) -> GenerationResult` | 新增 | `request.config` 取 alphagen 段；`result.tier_level` 取 config（默认 L0，仅允许 L0/L1） |
| `run_generation(..., on_expression=None, should_stop=None)` | 扩展 | 两者为 None 时行为与现状一致（冒烟用例不改） |
| `CandidatePipeline.offer(tokens) -> Outcome` | 新增 | `Outcome = Registered(factor) \| Rejected(reason_code)` |
| `StopController.check() -> str \| None` | 新增 | 返回首个触发的 `stop_reason` |
| `run_schema.load_run(path)` | 迁出 + 扩展 | v1/v2 双读 |

退出码不变（0/1/2）；`partial` 退出码 0，stdout 摘要含 `status` 与 `stop_reason`（IR-003）。

### Event / Trace Contract

沿用 F003 事件格式（`event_type` + `payload`）：每个拒绝写一条 `generation.candidate_rejected{reason_code, expression, definition_digest}`；`completed` 时写唯一的 `generation.run_completed`。**不**为适配 F007 改事件格式——格式适配归 F013（IR-004）。

## 5. Runtime、Workflow 与并发

```text
run_generation(on_expression, should_stop):
  env._evaluate 钩子: tokens = render(tree) → on_expression(tokens)   # 立即走流水线
  SB3 BaseCallback._on_step: return should_stop() is None             # False ⇒ learn() 在步边界返回
  learn(total_timesteps) 正常返回且 should_stop() 为 None ⇒ budget_exhausted

CandidatePipeline.offer(tokens):
  if stopped: 忽略（不计 proposed）
  proposed += 1
  check_expression(tokens, scope="cross_sectional")          → 拒: unregistered_op | lookahead
  digest = definition_digest(build_factor 草稿)               → 重复: duplicate_definition
  signal = compiled(panel); evaluate_objective(signal)       → 拒: reachability
  入册: registered.append(factor)；registered == quota ⇒ 通知 StopController
```

- 停止粒度：步边界。回调里一旦 `registered == quota`，流水线进入 `stopped`，同一步内后续表达式不计入 `proposed`，保证守恒；
- SIGTERM/SIGINT：注册信号处理器只置标志，不在处理器里做 IO；`finally` 中照常落盘已入册候选、释放 GPU 槽、恢复 Kronos；
- 并发：仍由 GpuSlot 保证单机单跑；不引入新锁。

## 6. UI 与可观测性

无 UI。日志：每 N 次评估一条 `INFO`（proposed/registered/各拒绝计数）；停止时一条 `INFO`（`stop_reason`、耗时、显存峰值）；运行结束 stdout 输出 JSON 摘要（`run_id/status/stop_reason/counts/budget`）。

## 7. 失败、恢复、安全与兼容

- **fail-closed**：张量构建零行、宇宙为空、alphagen 编译器未注册 ⇒ 启动期 `rejected`，不产空运行；
- **不降级**：预筛计算抛异常 ⇒ 整个运行 `failed`（ADR-0003：必需计算失败不得静默放行），不把异常候选当作拒绝吞掉；
- **兼容**：manual 路径产物不变（AC-006 基准对照）；既有 v1 run.json 可读；
- **安全**：沿用 egress 与写路径护栏，AlphaGen 训练与预筛都在护栏内；
- **恢复**：`partial` 不可续跑（新运行重新训练）；已入册候选只供排障查看。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f012_alphagen_mining.py`：小面板真实训练 | 入册因子 `generator=alphagen`、`mechanism_unknown`；反解后信号逐点一致 |
| `AC-002` | integration | 同上：`--quota 3` / 极小步数 | 入册数与 `stop_reason` |
| `AC-003` | unit | `tests/unit/test_f012_candidate_pipeline.py`：恒定信号、低可达性、低成本后收益 | 以 `reachability` 拒绝；`objective` 写入 |
| `AC-004` | unit | 同上：重复 token、事件计数 | `duplicate_definition`；事件计数 == `counts.rejected`；守恒 |
| `AC-005` | unit | `tests/unit/test_f012_stop_conditions.py`：时段结束、SIGTERM 标志 | `partial`、`stop_reason`、`pool=null`、load 拒绝 |
| `AC-006` | unit | `tests/unit/test_f012_cli_contract.py`：manual 基准（main 基线跑出的 digest 集）+ alphagen 分发 + 未知生成器 | 基准一致；argparse 拒绝 |
| `AC-007` | unit | `tests/unit/test_f012_run_schema.py`：v2 字段、v1 回读 | 字段如实；`code_digest != config_digest` |
| `AC-008` | integration（执行机） | 同 AC-001 文件的 CUDA 用例，`ALPHAMILL_INTEGRATION=1` | `completed`、入册 50、耗时/显存/预筛耗时留痕 |

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 自检放在评估回调内 | 边训练边自检，步边界停止 | 配额停止与夜槽保留工作的唯一可行点 | 事后统一自检（现状）无法按配额停 |
| 停止实现 | SB3 `BaseCallback._on_step` 返回 False | 官方停止机制，不抛异常打断训练状态 | — |
| 预筛异常 | 运行 `failed`，不吞为拒绝 | ADR-0003 | — |
| 行数约束 | 新逻辑进新模块；`cli.py`/`run_store.py` 净增 ≤0 | SOP 350 行硬上限 | — |
| 事件格式 | 沿用 F003，不为 F007 改格式 | 适配是 F013 的消费侧职责，避免双向耦合 | F013 |
| 残余风险：CUDA 非确定性 | NFR-002 只对 CPU 严格；CUDA 记录来源 | cuDNN/原子操作 | — |
| 残余风险：夜槽 8.5h 内能否入册 50 | AC-008 实测；不达标即为 M2 出口的产能发现，不降低门槛 | ADR-0003/0008 | 调整预算或宇宙（宇宙口径 v2） |

## 10. 待确认设计问题

无
