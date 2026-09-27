---
kind: feature
id: F012
version: "0.2"
status: doc-reviewing
branch: docs/F012-alphagen-mining-cli
gate_version: 1
related_features: [F003, F007, F013]
topics: [factor-factory, alphagen, generation, cli, funnel]
doc_kind: spec
created: 2026-09-27
updated: 2026-09-27
---

# F012：AlphaGen 后端接入挖掘 CLI（工厂批量闭环·生成侧）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册，自动候选标 `mechanism_unknown`）、FR2.2（可插拔生成器，AlphaGen RL 主引擎）、FR2.3（目标对齐：换手、≥30 笔/90 天可达性、成本后收益进入前置筛选）、FR2.4（纯度门）、FR2.6（名义产量、有效独立数、来源多样性与资源消耗并列记录）；§六 M2 出口「单次 ≥50 候选自动评测（批量能力标定）」
- **架构来源**：`docs/alphamill-architecture.md` §7.1（执行机训练夜槽、GPU 单槽、Kronos 卸载）
- **系统设计 / Contract 来源**：`F003` spec `AC-006`（本 feature 是其真实验收载体，见 F003 spec「AC-006 的边界」注）、`SC-003`、`NFR-001`、`DR-003`、`TR-002`；`BACKLOG.md`「执行顺序」第 1 项
- **上游决策**：ADR-0001（挖掘引擎选型，冒烟裁决 L0 锁定）、ADR-0003（门禁不降级）、ADR-0006（证据边界与实验身份）、ADR-0008（产能降级为分母与能力标定，不设周产出配额）
- **功能类型**：backend / workflow
- **规格模式**：lite
- **变更类型**：MIXED（ADDED：AlphaGen `Generator` 实现与 CLI 分支；MODIFIED：`run.json` schema 升 v2、`run_generation` 改为边训练边自检）
- **一句话意图**：让 `alphamill-generate mine --generator alphagen` 在执行机夜槽里真实挖掘湖数据，按入册上限产出一批**通过自检与目标对齐预筛**的 FactorDef，并留下如实、可被下游批量评测（F013）消费的运行记录。

## 1. 问题、目标与非目标

### 问题

F003 交付了 AlphaGen vendor、冒烟闸门与库级 `run_generation`，但工厂在 CLI 路径上仍只能跑 `manual` 后端：

- `alphamill-generate mine` 的 `--generator` 只接受 `manual`，且 `run_id` 前缀、config、`tier_level`、`GenerationRequest`、生成器构造、manifest 六处写死 `manual`；
- AlphaGen 没有实现统一的 `Generator.produce()`：`run_generation` 只返回 token 元组，不产 FactorDef、不落盘、不写拒绝事件，run_id 与 CLI 不一致，查重用 `repr(tokens)` 而非 `definition_digest`；
- 目标对齐预筛（`objective.evaluate_objective`）在生产路径**无调用方**，`rejected.reachability` 恒为 0——F003 `AC-006`「零交易型表达式不进池」在 CLI 路径上不成立；
- `write_generation_manifest` 写死 `tier_level="L0"`、`vram_limit_gb=None`、`kronos_offload=None`、`universe.source="explicit"`，`code_digest` 误用 `config_digest`；
- `--quota` 只对 manual 有定义（固定种子表取前 N），对 AlphaGen 无意义。

结果：M2 出口要求的「单批 ≥50 候选」没有可运行的生产入口，F003 `AC-006` 也缺真实载体。

### 目标

- `mine --generator alphagen` 走与 manual 相同的护栏链（绑定校验 → 能力自检 → 训练时段 → Kronos 卸载 → GPU 单槽 → egress/写路径护栏），在执行机上对真实湖绑定完成挖掘；
- 候选**边训练边自检**：渲染 → 纯度/前视/算子自检 → 按 `definition_digest` 查重 → 目标对齐预筛 → 入册；入册数达到 `--quota` 即停止训练；
- 入册的每个候选都是可反解重算的 `FactorDef`（`generator="alphagen"`，假设 `mechanism_unknown`），每个拒绝都写 `generation.candidate_rejected` 事件；
- `run.json` 如实记录引擎、层级、宇宙规模、预算、停止原因与分级计数，漏斗不变量 `proposed == registered + Σrejected` 恒成立；
- 夜槽结束或中断时，已入册候选照常落盘，运行记为 `partial`，**不进入评测**。

### 非目标

- 不做批量评测编排、FactorDef → 信号 CSV、生成事件到 F007 漏斗的适配、显式绑定到已发布 ResearchSnapshot 的转换——全部属于 `F013`；
- 不做研究控制台（`F005`）与 M2 出口的 ≥50 批量验收实跑（BACKLOG 执行顺序第 3 项）；
- 不新增 GP/LLM 后端，不改冒烟闸门判据与 L0/L1/L2 阶梯；
- 不改 manual 后端行为（`--generator manual` 的产物与现状可观察等价）；
- 不做跨运行查重与 `|ρ|` 变体判定（F003 spec §7：归 F007 finalize）；
- 不改宇宙口径（BACKLOG「宇宙口径 v2」）。

## 2. 用户场景

### US-001：一次夜槽挖掘入册一批候选（Priority: P1）

作为工厂运营者，我希望在执行机上用一条 `mine --generator alphagen --quota 50` 命令对真实湖绑定挖掘，以便得到一批通过自检与预筛、可被批量评测的 FactorDef。

**为什么是这个优先级**：这是本 feature 唯一的最小有价值切片；没有它，M2 的批量能力标定没有生产入口。

**独立测试**：小张量面板 + 小步数运行 `produce()`，断言入册数 = 配额、每个入册因子可 `factor_store.load` 反解、run.json 为 `completed` 且计数守恒。

**验收场景**：

1. Given 有效显式绑定与 CUDA 能力，when `mine --generator alphagen --quota N`，then 入册 N 个 `generator="alphagen"` 的 FactorDef，run.json `status=completed`、`stop_reason=quota_reached`。
2. Given 训练步数预算先于配额耗尽，when 运行结束，then `status=completed`、`stop_reason=budget_exhausted`，入册数 < N 且如实记录。

### US-002：零交易与重复候选不进册（Priority: P1）

作为研究者，我希望换手为零、90 天内达不到最少交易笔数、成本后收益不达标或与本批已有定义重复的表达式被拒并留痕，以便下游评测的分母干净、漏斗第一级可审计。

**为什么是这个优先级**：F003 `AC-006` 的核心承诺；没有它，入册数是虚高的名义产量（FR2.6）。

**独立测试**：构造零交易、低可达性与重复表达式，断言对应拒绝计数与事件。

**验收场景**：

1. Given 一个恒定信号表达式，when 自检通过进入预筛，then 以 `reachability` 拒绝并写 `generation.candidate_rejected`，不入册。
2. Given 同一表达式第二次出现，when 查重，then 以 `duplicate_definition` 拒绝（按 `definition_digest`，不是 `repr(tokens)`）。

### US-003：夜槽结束时不丢已完成的工作（Priority: P2）

作为运营者，我希望挖掘超出训练时段或被中断时已入册的候选照常落盘，并清楚标记这是不完整运行，以便排障复用又不污染正式评测。

**为什么是这个优先级**：夜槽是无人值守的；丢工作浪费 GPU 时长，混入评测破坏 cohort 分母（ADR-0006）。

**独立测试**：注入「时段已结束」与 SIGTERM，断言 `partial`、候选落盘、无 pool、`factor_store.load` 拒绝加载。

**验收场景**：

1. Given 训练中途越过夜槽终点，when 下一次自检回调，then 停止训练、`status=partial`、`stop_reason=window_closed`，已入册候选落盘。

## 3. 范围与边界

### 范围内

- AlphaGen `Generator` 实现（`produce()`）与 alphagen 编译器注册；
- `run_generation` 改为边训练边自检、可由回调提前停止；
- 目标对齐预筛接入生成路径（换手、可达性、成本后收益）；
- CLI `mine` 的生成器分发（manual / alphagen），去掉写死的 manual；
- `run.json` schema v2（预算、停止原因、如实引擎与层级字段），v1 只读兼容；
- 张量数据面参数（datasets、resample、宇宙成员）进入 config 与 run.json。

### 范围外

- 见 §1 非目标；`seed` 子命令保持 manual 专用（种子后端本就不训练）。

### 边界场景

- **配额语义**：`--quota` = 本次最多入册的候选数；训练步数 `total_timesteps` 与协同池容量 `pool_capacity` 是 config 里的预算；「入册达配额 / 步数耗尽 / 夜槽结束 / 中断」任一先到即停。
- **配额达成后的剩余表达式**：训练停止前同一步内已渲染但未处理的表达式**不计入** `proposed`（漏斗只记处理过的候选，保持守恒）。
- **协同池**：只在 `completed` 时注册；`partial` 禁止 pool（沿用 run_store 不变量）。
- **CPU**：`--allow-cpu` 可在无 CUDA 时运行（开发机冒烟），run.json 如实记 `device=cpu`；产能结论只认执行机 CUDA 证据。
- **宇宙为空或张量构建零行**：拒绝启动（`invalid_binding` 或 `capability_unavailable`），不产空运行。
- **绑定形态**：只接受显式绑定（现状 CLI 不传 `snapshot_resolver`）；ResearchSnapshot ID 绑定归 `F013`。
- **绝不能发生**：未经自检/预筛的表达式入册；run.json 与实际不符（写死层级/宇宙来源）；`partial` 运行的候选被评测侧当作完整批次加载。

## 4. 需求

### 功能需求

### Requirement: AlphaGen 生成器实现（`FR-001`）

系统应当提供实现 `Generator` 协议的 AlphaGen 后端：从绑定构建 PIT 张量面板、训练 AlphaGen、把入册表达式编译为 `generator="alphagen"`、假设 `mechanism_unknown` 的 `FactorDef`，并注册 alphagen 编译器，使入册因子可经 `factor_store.load` 反解重算。

#### Scenario: 入册因子可反解

- GIVEN 一次 `completed` 的 alphagen 运行
- WHEN 用 `factor_store.load` 读回任一入册因子并在同一面板上计算
- THEN 结果与入册时计算的信号逐点一致

### Requirement: 边训练边自检与配额停止（`FR-002`）

当 AlphaGen 评估一个表达式时，系统应当立即依次执行：渲染、纯度/前视/算子自检、按 `definition_digest` 在本运行内查重、目标对齐预筛；通过者入册。当入册数达到 `--quota` 时，系统应当停止训练。

#### Scenario: 达到配额即停

- GIVEN `--quota 3` 与足够的步数预算
- WHEN 第 3 个候选入册
- THEN 训练在当前步结束后停止，`stop_reason=quota_reached`，`registered == 3`

### Requirement: 目标对齐预筛（`FR-003`）

系统应当对每个通过自检的候选在同一张量面板上计算信号，调用 `objective.evaluate_objective`；换手为零、90 天交易笔数低于 `reachability_min_trades_90d`、或成本后收益低于 `min_after_cost_return` 者以 `reachability` 拒绝。预筛参数应当写入 run.json 的 `objective`。

#### Scenario: 零交易被拒

- GIVEN 一个恒定信号表达式
- WHEN 进入预筛
- THEN 以 `reachability` 拒绝、写拒绝事件、不入册

### Requirement: 拒绝留痕与计数守恒（`FR-004`）

系统应当为每个被拒候选追加一条 `generation.candidate_rejected` 事件（原因码为 F003 枚举 `unregistered_op | lookahead | reachability | duplicate_definition`），并保证 run.json `counts` 满足 `proposed == registered + Σrejected`。

#### Scenario: 事件与计数一致

- GIVEN 任一结束的运行
- WHEN 统计 events.jsonl 中各原因码的拒绝事件
- THEN 与 `counts.rejected` 逐项相等

### Requirement: 停止原因与不完整运行（`FR-005`）

当夜槽结束（未开 `--allow-offhours`）或进程收到 SIGTERM/SIGINT 时，系统应当停止训练、把已入册候选落盘、以 `status=partial` 结束且不注册协同池；`stop_reason` 取值 `quota_reached | budget_exhausted | window_closed | interrupted`。`partial` 运行的因子不可被 `factor_store.load` 加载（现有不变量，评测侧不可见）。

#### Scenario: 夜槽结束

- GIVEN 训练越过夜槽终点
- WHEN 下一次自检回调检查时段
- THEN `status=partial`、`stop_reason=window_closed`、`pool=null`、已入册候选在 `factors/` 下

### Requirement: CLI 生成器分发（`FR-006`）

`alphamill-generate mine` 应当接受 `--generator manual|alphagen`，按生成器分发构造、`run_id` 前缀、config、层级与 manifest 字段；`manual` 路径的产物与现状可观察等价。

#### Scenario: manual 不变

- GIVEN 同一绑定与种子
- WHEN 以 `--generator manual` 运行
- THEN 入册因子集合与 `definition_digest` 与改动前一致

### Requirement: 如实的运行记录（`FR-007`）

run.json 应当如实记录：`engine.vendor_commit`（vendor 基线提交）与 `engine.code_digest`（代码构建摘要，不得复用 config_digest）、`tier_level`（取自 config 的冻结层级，默认 L0，仅允许 F003 冒烟裁决允许的层级）、`universe.pair_count/source`（实际参与张量的宇宙）、`vram_limit_gb` 与 `kronos_offload`（实际值）、以及 v2 新增的 `budget{quota,total_timesteps,pool_capacity}`、`stop_reason`、`evaluations`。

#### Scenario: 不写死层级与宇宙来源

- GIVEN 一次 alphagen 运行
- WHEN 读取 run.json
- THEN `tier_level`、`universe.source`、`vram_limit_gb`、`kronos_offload` 与运行实际一致，`code_digest != config_digest`

### 数据 / 实体需求

- **DR-001**：`run.json` schema 升为 v2：新增 `budget`、`stop_reason`、`evaluations`；`load_run` 同时接受 v1（既有 manual 运行只读）与 v2，新运行一律写 v2。
- **DR-002**：入册 FactorDef 的 `params` 记录其预筛指标（`turnover`、`trades_90d`、`after_cost_return`），供下游溯源；不改 FactorDef schema。
- **DR-003**：不新增持久化目录结构：沿用 `run_dir/{run.json,events.jsonl,factors/,feature_maps/,pool.json}`。

### API / 接口需求

- **IR-001**：CLI `mine --generator {manual,alphagen}`；alphagen 专用配置键（`total_timesteps`、`pool_capacity`、`datasets`、`resample`、`objective.*`）经 `--config` 给出，缺省取 `DEFAULT_MINE_CONFIG` 中的 alphagen 段。
- **IR-002**：`--quota` 对 alphagen 的语义为入册上限（≥1）；对 manual 语义不变。
- **IR-003**：退出码沿用 F003（0 OK / 1 FAILED / 2 REJECTED）；`partial` 以退出码 0 结束但 stdout 摘要标 `status=partial`（运维可见，不触发 systemd 重试）。
- **IR-004**：F013 消费本 feature 产物的契约 = `status=completed` 的 run_dir（run.json v2 + events.jsonl + factors/）；本 feature 不读写 `experiment_store`。

### 非功能需求

- **NFR-001**：产能：执行机 CUDA 下单次运行在一个夜槽（22:00–06:30）内以 `--quota 50` 入册 ≥50 个候选（沿用 F003 `NFR-001`，为 M2 出口的前置能力；实测记录耗时与显存峰值）。
- **NFR-002**：可复现：同一绑定、种子、config 与代码 ⇒ 同一入册 `definition_digest` 序列（CPU 下严格；CUDA 下记录非确定性来源）。
- **NFR-003**：预筛开销：单候选预筛耗时在执行机上 ≤ 1 s（35 对 × 2 年 × 1h 面板量级），否则须在 design 给出降级采样方案并经裁决，不得静默跳过预筛。
- **NFR-004**：`src/**/*.py` ≤350 行（`cli.py` 343、`run_store.py` 350 行已近/达上限，必须拆分而非突破）。

## 5. 生命周期与不变量

```text
mine --generator alphagen
  绑定校验 → 能力自检 → 训练时段 → Kronos 卸载 → GPU 单槽 → 护栏
  build_tensor → build_stock_data → 训练（每次表达式评估回调）:
      渲染 → 自检 → 查重(definition_digest) → 预筛 → 入册 | 拒绝(事件)
      registered == quota ⇒ 停（quota_reached）
      夜槽结束 ⇒ 停（window_closed）; SIGTERM/SIGINT ⇒ 停（interrupted）
  步数耗尽 ⇒ budget_exhausted
  终态: quota_reached | budget_exhausted → completed（可注册 pool）
        window_closed | interrupted       → partial（禁 pool，评测不可见）
```

不变量：

- `proposed == registered + Σrejected`，且拒绝事件数与 `counts.rejected` 逐项相等；
- 入册 ⊆ 通过自检 ∩ 通过预筛 ∩ 本运行内 `definition_digest` 唯一；
- `registered <= quota`；
- run.json 只写一次，字段与实际一致（不写死）。

## 6. 成功与验收

### 成功标准

- **SC-001**：执行机上一次 `mine --generator alphagen --quota 50` 在夜槽内 `completed` 并入册 50 个候选（M2 出口前置）；
- **SC-002**：零交易与重复表达式在生产路径上被拒且可审计（F003 `AC-006` 获得真实载体）；
- **SC-003**：F013 可仅凭 run_dir 契约消费本 feature 产物，无需读取 vendor 内部结构。

### 验收清单

- [ ] **AC-001** (`FR-001`, `DR-003`, `US-001`): 小面板 alphagen 运行入册的每个因子 `generator="alphagen"`、假设 `mechanism_unknown`，经 `factor_store.load` 反解后在同一面板上信号逐点一致 — tests: `tests/integration/test_f012_alphagen_mining.py`
- [ ] **AC-002** (`FR-002`, `IR-002`, `US-001`): `--quota 3` 时入册恰为 3、`stop_reason=quota_reached`；步数先耗尽时 `stop_reason=budget_exhausted` 且入册 < 配额 — tests: `tests/integration/test_f012_alphagen_mining.py`
- [ ] **AC-003** (`FR-003`, `US-002`): 恒定信号以 `reachability` 拒绝；低于最少交易笔数与成本后收益阈值者同样被拒；预筛参数写入 run.json `objective` — tests: `tests/unit/test_f012_candidate_pipeline.py`
- [ ] **AC-004** (`FR-004`, `US-002`): 重复表达式按 `definition_digest` 以 `duplicate_definition` 拒绝；events.jsonl 拒绝事件按原因码计数与 `counts.rejected` 逐项相等，`proposed == registered + Σrejected` — tests: `tests/unit/test_f012_candidate_pipeline.py`
- [ ] **AC-005** (`FR-005`, `US-003`): 注入夜槽结束与 SIGTERM 两种停止，均得 `status=partial`、对应 `stop_reason`、`pool=null`、已入册候选落盘且 `factor_store.load` 拒绝加载 — tests: `tests/unit/test_f012_stop_conditions.py`
- [ ] **AC-006** (`FR-006`, `IR-001`, `IR-003`): CLI 接受 `--generator alphagen`；`--generator manual` 同绑定同种子的入册 `definition_digest` 集合与改动前基准一致；未知生成器被 argparse 拒绝 — tests: `tests/unit/test_f012_cli_contract.py`
- [ ] **AC-007** (`FR-007`, `DR-001`): run.json v2 字段如实（`tier_level`、`universe.source/pair_count`、`vram_limit_gb`、`kronos_offload`、`budget`、`stop_reason`、`evaluations`，`code_digest != config_digest`）；v1 run.json 仍可 `load_run` — tests: `tests/unit/test_f012_run_schema.py`
- [ ] **AC-008** (`NFR-001`, `NFR-003`, `SC-001`): 执行机 CUDA 夜槽真实湖绑定 `--quota 50` 运行 `completed` 且入册 50，记录耗时、显存峰值与单候选预筛耗时 — tests: `tests/integration/test_f012_alphagen_mining.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元：候选流水线（自检 → 查重 → 预筛 → 入册/拒绝）、停止条件、run.json v2 schema、CLI 分发与退出码；AlphaGen 训练以桩替身驱动回调，不依赖 torch。
- 集成：`mining` extra 下小面板（合成或 scratch 湖）真实 AlphaGen 训练，覆盖入册反解、配额停止、计数守恒；无 torch 环境按项目约定 `importorskip`。
- 执行机取证：AC-008 在 `qiaozhi-lt` CUDA 夜槽实跑，开发机 skip 不算证据。

### 依赖

- 上游：`F003`（生成器协议、AlphaGen vendor、run_store/factor_store、GPU 槽与护栏）、`F002`（湖读取）、`F008`（宇宙台账，经绑定进入张量）。
- 下游：`F013`（批量评测编排，消费 `completed` run_dir）。
- 环境：执行机 `qiaozhi-lt`（CUDA、夜槽、Kronos 卸载）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 是否拆成两个 Feature（owner 2026-09-27） | 拆：F012 生成侧、F013 批量评测编排 | 链路 5 处断点，单 Feature 约 2 周、失败面大 | F013 立项消费 IR-004 |
| `--quota` 对 AlphaGen 的语义（owner 2026-09-27） | 入册上限；步数与池容量为 config 预算，任一先到即停 | M2 验收需要确定的入册数；ADR-0008 不设周配额但单批标定需要可控批量 | — |
| 中断运行的去向（owner 2026-09-27） | `partial`，候选落盘可查，不进评测 | cohort 分母只来自完整运行（ADR-0006） | — |
| 批量评测层级（owner 2026-09-27，归 F013） | 直接 canonical：看结果前冻结整批 cohort | 先 preview 再挑选违反「看结果前冻结」 | F013 |
| 自检时机 | 边训练边自检（评估回调内） | 事后统一自检无法按配额提前停，也无法在夜槽结束时保留已完成工作 | — |
| 风险：预筛开销拖慢训练 | NFR-003 限 ≤1 s/候选，超限须裁决降级方案 | 不得静默跳过预筛（ADR-0003） | 执行机实测 |
| 风险：35 对小宇宙上横截面 reward 噪声大 | 沿用 F003 §7 结论，运行留痕 `pair_count` | 宇宙扩大属「宇宙口径 v2」 | — |

## 8. 待确认问题

- [x] Q-001: F012 是否拆分？ — 决策（owner 2026-09-27）：拆为 F012（生成侧）与 F013（批量评测编排）。
- [x] Q-002: `--quota` 对 AlphaGen 的语义？ — 决策（owner 2026-09-27）：入册上限；`total_timesteps`、`pool_capacity` 为 config 预算，任一先到即停。
- [x] Q-003: 夜槽结束或中断的运行如何处理？ — 决策（owner 2026-09-27）：记 `partial`，已入册候选落盘，不进评测。
- [x] Q-004: 批量评测用 preview 还是 canonical？ — 决策（owner 2026-09-27）：直接 canonical，看结果前冻结整批 cohort（由 F013 实现）。
