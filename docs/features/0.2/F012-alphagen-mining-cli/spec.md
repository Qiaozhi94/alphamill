---
kind: feature
id: F012
version: "0.2"
status: code-reviewing
status_evidence: G1 计划批准（owner 2026-09-27，按 tasks.md T001-T020 连续开发）
branch: feat/F012-alphagen-mining-cli
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
- **系统设计 / Contract 来源**：`F003` spec `AC-006`（本 feature 是其 CLI 路径上的真实验收载体：零交易预筛生效 + 宇宙规模在运行记录中可区分，见 F003 spec「AC-006 的边界」注）、`SC-003`、`NFR-001`、`DR-003`、`TR-002`；`BACKLOG.md`「执行顺序」第 1 项
- **上游决策**：ADR-0001（挖掘引擎选型，冒烟裁决 L0 锁定）、ADR-0003（门禁不降级）、ADR-0006（证据边界与实验身份）、ADR-0008（产能降级为分母与能力标定，不设周产出配额）
- **功能类型**：backend / workflow
- **规格模式**：lite
- **变更类型**：MIXED（ADDED：AlphaGen `Generator` 实现、回调式训练入口、CLI 分支；MODIFIED：`run.json` schema 升 v2 且 `factor_store.load` 双读、预筛增截面仓位规则；`run_generation` 旧路径原样保留）
- **一句话意图**：让 `alphamill-generate mine --generator alphagen` 在执行机夜槽里真实挖掘湖数据，按入册上限产出一批**通过自检与目标对齐预筛**的 FactorDef，并留下如实、可被下游批量评测（F013）消费的运行记录。

## 1. 问题、目标与非目标

### 问题

F003 交付了 AlphaGen vendor、冒烟闸门与库级 `run_generation`，但工厂在 CLI 路径上仍只能跑 `manual` 后端：

- `alphamill-generate mine` 的 `--generator` 只接受 `manual`，且 `run_id` 前缀、config、`tier_level`、`GenerationRequest`、生成器构造、manifest、`objective` 等十余处写死（清单见 design §1）；
- AlphaGen 没有实现统一的 `Generator.produce()`：`run_generation` 只返回 token 元组，不产 FactorDef、不落盘、不写拒绝事件，run_id 与 CLI 不一致，查重用 `repr(tokens)` 而非 `definition_digest`；
- 目标对齐预筛（`objective.evaluate_objective`）在生产路径**无调用方**，`rejected.reachability` 恒为 0——F003 `AC-006`「零交易型表达式不进池」在 CLI 路径上不成立；
- `write_generation_manifest` 写死 `tier_level="L0"`、`vram_limit_gb=None`、`kronos_offload=None`、`universe.source="explicit"`，`code_digest` 误用 `config_digest`；
- `--quota` 只对 manual 有定义（固定种子表取前 N），对 AlphaGen 无意义；
- AlphaGen 表达式渲染器 `render_expression` 丢失滚动算子窗口（`Mean(c,10)` → `('feature:close','mean')`），纯度门据此把绝大多数候选判为 `lookahead`（F003 既有缺陷，文档检视 D23 实跑复现）。

结果：M2 出口要求的「单批 ≥50 候选」没有可运行的生产入口，F003 `AC-006` 也缺真实载体。

### 目标

- `mine --generator alphagen` 走与 manual 相同的护栏链（绑定校验 → 能力自检 → 训练时段 → Kronos 卸载 → GPU 单槽 → egress/写路径护栏），在执行机上对真实湖绑定完成挖掘；
- 候选**边训练边自检**：渲染 → token 绑定到湖通道 → 纯度/前视/算子自检 → 按 `definition_digest` 查重 → 目标对齐预筛（截面仓位 = 信号减当期截面中位数后取符号）→ 入册；入册数达到 `--quota` 即停止训练；
- 入册的每个候选都是可反解重算的 `FactorDef`（`generator="alphagen"`，假设 `mechanism_unknown`），每个拒绝都写 `generation.candidate_rejected` 事件；
- `run.json` 如实记录引擎、层级、宇宙规模、预算、停止原因与分级计数，漏斗不变量 `proposed == registered + Σrejected` 恒成立；
- 夜槽结束或中断时，已入册候选照常落盘，运行记为 `partial`，**不进入评测**；
- 本 feature **不注册协同池**：`pool` 恒为 `null`（owner 2026-09-27）。

### 非目标

- 不做批量评测编排、FactorDef → 信号 CSV、生成事件到 F007 漏斗的适配、显式绑定到已发布 ResearchSnapshot 的转换——全部属于 `F013`；
- 不做研究控制台（`F005`）与 M2 出口的 ≥50 批量验收实跑（BACKLOG 执行顺序第 3 项）；
- 不新增 GP/LLM 后端，不改冒烟闸门判据与 L0/L1/L2 阶梯；
- 不改 manual 后端行为（`--generator manual` 的产物与现状可观察等价）；
- 不做跨运行查重与 `|ρ|` 变体判定（F003 spec §7：归 F007 finalize）；
- 不改宇宙口径（BACKLOG「宇宙口径 v2」）；
- 不注册 AlphaGen 协同池 meta-factor（FR2.6 协同池另立项；owner 2026-09-27）。

## 2. 用户场景

### US-001：一次夜槽挖掘入册一批候选（Priority: P1）

作为工厂运营者，我希望在执行机上用一条 `mine --generator alphagen --quota 50` 命令对真实湖绑定挖掘，以便得到一批通过自检与预筛、可被批量评测的 FactorDef。

**为什么是这个优先级**：这是本 feature 唯一的最小有价值切片；没有它，M2 的批量能力标定没有生产入口。

**独立测试**：小张量面板 + 小步数运行 `produce()`，断言入册数 = 配额、每个入册因子可经 `factor_store.load`（读 v2 run.json）反解、run.json 为 `completed` 且计数守恒。

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
3. Given 一个常规截面因子（如对收益做截面排名、取值恒为正），when 进入预筛，then 仓位按「减当期截面中位数后取符号」换算，能产生交易并通过预筛（不因信号恒正被误判零交易）。

### US-003：夜槽结束时不丢已完成的工作（Priority: P2）

作为运营者，我希望挖掘超出训练时段或被中断时已入册的候选照常落盘，并清楚标记这是不完整运行，以便排障复用又不污染正式评测。

**为什么是这个优先级**：夜槽是无人值守的；丢工作浪费 GPU 时长，混入评测破坏 cohort 分母（ADR-0006）。

**独立测试**：注入「时段已结束」与 SIGTERM，断言 `partial`、候选落盘、无 pool、`factor_store.load` 拒绝加载。

**验收场景**：

1. Given 训练中途越过夜槽终点，when 下一次步边界检查，then 停止训练、`status=partial`、`stop_reason=window_closed`，已入册候选落盘。
2. Given 进程在排队等 GPU 槽或构建张量时收到 SIGTERM，when 下一次检查点，then 以 `status=partial`、`stop_reason=interrupted`、入册 0 结束并写 run.json，GPU 槽与 Kronos 按既有 finally 恢复。

## 3. 范围与边界

### 范围内

- AlphaGen `Generator` 实现（`produce()`）与 alphagen 编译器组装注册；
- 新增回调式训练入口（边训练边自检、可在步边界停止）；`run_generation` 旧路径原样保留；
- AlphaGen token 到湖通道的绑定规则；
- 修正 AlphaGen 表达式渲染器（滚动与成对滚动算子带窗口、`CSRank`/`Rank` 正确映射、未登记的时序 `Rank` 如实拒绝），vendor 动作空间不改；
- 目标对齐预筛接入生成路径（换手、可达性、成本后收益），增截面仓位规则；
- CLI `mine` 的生成器分发（manual / alphagen），去掉写死的 manual；
- `run.json` schema v2（预算、停止原因、如实引擎与层级字段），v1 只读兼容；`factor_store.load` 双读；
- 运行内单写者事件写出器（不回读、批量 fsync）；
- 张量数据面参数（datasets、resample、宇宙成员）进入 config 与 run.json。

### 范围外

- 见 §1 非目标；`seed` 子命令保持 manual 专用（种子后端本就不训练）。

### 边界场景

- **配额语义**：`--quota` = 本次最多入册的候选数；训练步数 `total_timesteps` 与协同池容量 `pool_capacity` 是 config 里的预算；「入册达配额 / 步数耗尽 / 夜槽结束 / 中断」任一先到即停。
- **配额达成后的剩余表达式**：训练停止前同一步内已渲染但未处理的表达式**不计入** `proposed`（漏斗只记处理过的候选，保持守恒）。
- **协同池**：本 feature 不注册，`pool` 恒为 `null`（completed 与 partial 均然）。
- **CPU**：`--allow-cpu` 可在无 CUDA 时运行（开发机冒烟），run.json 如实记 `device=cpu`；产能结论只认执行机 CUDA 证据。
- **张量构建零行**：张量在 Kronos 卸载与取 GPU 槽**之前**构建；零行即以 `rejected`、`termination=invalid_binding` 拒绝，不白卸载 Kronos、不产空运行；`datasets`/`resample` 非法以 `invalid_config` 拒绝。
- **token 缺湖通道**（如 `feature:vwap` 而 `ohlcv_1m` 无该列）：以 `unregistered_op` 拒绝，`detail=missing_channel:<name>`。
- **退化信号**（无任何观测值、非有限值、编译失败、畸形 token）：候选级拒绝（见 `FR-003`），不使运行失败；只有系统级异常（IO、存储、CUDA、内存、编译器未组装、面板结构错误）使运行 `failed`。
- **取数范围**：张量按运行窗口 `[window.start, window.end)` 构建，读取的 pair 为窗口内任一时点属于宇宙的成员并集，成员按逐时点 PIT 掩码（不以窗口终点成员筛整段历史，也不读宇宙外的湖内 pair）。
- **窗口内宇宙为空**：张量构建后若无任何在宇宙的单元格，以 `rejected`、`termination=invalid_binding` 拒绝。
- **同名通道冲突**：多个数据集出现同名 basename（如两个数据集都有 `close`）时启动期以 `invalid_config` 拒绝。
- **close 缺失的 bar**（重采样缺口）：预筛前视为未观测，不报错，计数留痕；只有面板结构类错误使运行失败。
- **绑定形态**：只接受显式绑定（现状 CLI 不传 `snapshot_resolver`）；ResearchSnapshot ID 绑定归 `F013`。
- **层级**：alphagen 固定 `L0`（ADR-0001：L1 为绕开 sb3/RL 的求值器 + 自写搜索，与本后端不符）；config 给出其他层级即 `rejected`、`termination=unknown_tier`。
- **绝不能发生**：未经自检/预筛的表达式入册；run.json 与实际不符（写死层级/宇宙来源）；`partial` 运行的候选被评测侧当作完整批次加载。

## 4. 需求

### 功能需求

### Requirement: AlphaGen 生成器实现（`FR-001`）

系统应当提供实现 `Generator` 协议的 AlphaGen 后端：按运行窗口从绑定构建 PIT 张量面板、训练 AlphaGen、把入册表达式（token 已绑定到湖通道名）编译为 `generator="alphagen"`、假设 `mechanism_unknown` 的 `FactorDef`，并组装 alphagen 编译器，使入册因子可经 `factor_store.load`（接受 v1/v2 run.json）反解重算。

#### Scenario: 入册因子可反解

- GIVEN 一次 `completed` 的 alphagen 运行
- WHEN 用 `factor_store.load` 读回任一入册因子并在同一面板上计算
- THEN 结果与入册时计算的信号逐点一致

### Requirement: 边训练边自检与配额停止（`FR-002`）

当 AlphaGen 评估一个表达式时，系统应当立即依次执行：渲染、token 绑定湖通道、纯度/前视/算子自检、按 `definition_digest` 在本运行内查重、目标对齐预筛；通过者入册。当入册数达到 `--quota` 时，系统应当在当前步结束后停止训练。

#### Scenario: 达到配额即停

- GIVEN `--quota 3` 与足够的步数预算
- WHEN 第 3 个候选入册
- THEN 训练在当前步结束后停止，`stop_reason=quota_reached`，`registered == 3`

### Requirement: 目标对齐预筛（`FR-003`）

系统应当对每个通过自检的候选在同一张量面板上计算信号，按**截面仓位规则**（每个时点以在宇宙内 pair 的信号减去该时点截面中位数后取符号，owner 2026-09-27）换算仓位，调用 `objective.evaluate_objective`；换手为零、90 天交易笔数低于 `reachability_min_trades_90d`、或成本后收益低于 `min_after_cost_return` 者以 `reachability` 拒绝。信号全 NaN 或含非有限值、编译失败等候选级退化同样以候选拒绝处理（`reachability` 或 `unregistered_op`，detail 写明原因），不使运行失败。预筛参数与仓位规则应当写入 run.json 的 `objective`；每个候选的预筛指标写入 `run_dir/prefilter.jsonl`，**不进入** FactorDef 身份。

#### Scenario: 零交易被拒

- GIVEN 一个恒定信号表达式
- WHEN 进入预筛
- THEN 以 `reachability` 拒绝、写拒绝事件、不入册

#### Scenario: 恒正的截面因子不被误判

- GIVEN 对收益做截面排名的因子（取值恒在 (0,1]）
- WHEN 进入预筛
- THEN 仓位按截面中位数换算后有多有空、能产生交易，按真实换手与收益判定

### Requirement: 拒绝留痕与计数守恒（`FR-004`）

系统应当为每个被拒候选追加一条 `generation.candidate_rejected` 事件（payload 为既有 `{expression, reason_code, detail}` 加可选 `definition_digest`；原因码为 F003 枚举 `unregistered_op | lookahead | reachability | duplicate_definition`；事件 schema 版本与 run.json schema 版本解耦），并保证 run.json `counts` 满足 `proposed == registered + Σrejected`。事件写出不得随事件数二次增长（单写者、不回读）。

#### Scenario: 事件与计数一致

- GIVEN 任一结束的运行
- WHEN 统计 events.jsonl 中各原因码的拒绝事件
- THEN 与 `counts.rejected` 逐项相等

### Requirement: 停止原因与不完整运行（`FR-005`）

当夜槽结束（未开 `--allow-offhours`）或进程收到 SIGTERM/SIGINT 时，系统应当停止训练、把已入册候选落盘、以 `status=partial` 结束；`stop_reason` 取值 `quota_reached | budget_exhausted | window_closed | interrupted`，`partial` 时 `termination` 取 `stop_reason` 值、`reason` 写明「已入册 k/quota 与停止原因」。信号处理器在 `mine` 入口安装、覆盖排队等槽与张量构建阶段；训练开始前被中断同样以 `partial`、入册 0 结束并写 run.json。`partial` 运行的因子不可被 `factor_store.load` 加载（现有不变量，评测侧不可见）。

#### Scenario: 夜槽结束

- GIVEN 训练越过夜槽终点
- WHEN 下一次自检回调检查时段
- THEN `status=partial`、`stop_reason=window_closed`、`pool=null`、已入册候选在 `factors/` 下

### Requirement: CLI 生成器分发（`FR-006`）

`alphamill-generate mine` 应当接受 `--generator manual|alphagen`，按生成器分发构造、`run_id` 前缀、config、层级与 manifest 字段（单一 manifest 构建器，消除全部写死点）；`manual` 路径与现状可观察等价，定义为：因子文件名集合一致且因子内容剔除 `run_id`、`created_at` 后逐字节一致；`config_digest` 不变（alphagen 缺省段不并入 manual config）；run.json 剔除易变字段（`run_id`、`started_at`、`finished_at`、`hostname`）、`schema_version` 与 v2 新增字段后逐项相等。

#### Scenario: manual 不变

- GIVEN 同一绑定与种子
- WHEN 以 `--generator manual` 运行
- THEN 按上述口径与改动前 main 的实跑产物等价

### Requirement: 如实的运行记录（`FR-007`）

run.json 应当如实记录：`engine.vendor_commit`（vendor 基线提交）与 `engine.code_digest`（代码构建摘要，不得复用 config_digest）、`tier_level`（alphagen 固定 `L0`，ADR-0001）、`universe.pair_count/source`（实际参与张量的宇宙）、`vram_limit_gb` 与 `kronos_offload`（实际值）、`objective`（实际预筛参数与仓位规则，不再写死），以及 v2 新增的 `budget{quota,total_timesteps,pool_capacity}`、`stop_reason`、`evaluations`。

#### Scenario: 不写死层级与宇宙来源

- GIVEN 一次 alphagen 运行
- WHEN 读取 run.json
- THEN `tier_level`、`universe.source`、`vram_limit_gb`、`kronos_offload` 与运行实际一致，`code_digest != config_digest`

### Requirement: 宇宙规模在运行记录中可区分（`FR-008`）

对 alphagen 运行，系统应当在 run.json 的 `universe.pair_count` 记录窗口内至少一个时点属于宇宙的 pair 数（manual 运行沿用现状口径以保持 `FR-006` 等价，检视 D43）（取自面板的 `__in_universe__` 掩码，不取窗口终点成员数，也不取湖内 pair 数），使「换宇宙后候选与计数差异」在 CLI 路径上可观测（F003 `AC-006` 边界注所委托的口径）。

#### Scenario: 两个宇宙可区分

- GIVEN 同一种子、数据版本相同而宇宙成员不同的两个显式绑定
- WHEN 分别运行 alphagen 挖掘
- THEN 两份 run.json 的 `universe.pair_count` 不同，且等于各自面板中窗口内曾在宇宙的 pair 数

### 数据 / 实体需求

- **DR-001**：`run.json` schema 升为 v2：新增 `budget`、`stop_reason`、`evaluations`，`objective` 增 `position_rule`；`load_run` 与 `factor_store.load` 同时接受 v1（既有 manual 运行只读）与 v2，新运行一律写 v2。
- **DR-002**：每个进入预筛的候选在 `run_dir/prefilter.jsonl` 记一行 `{definition_digest, outcome, turnover, trades_90d, after_cost_return, elapsed_ms}`；预筛指标**不写入** FactorDef `params`（避免 `definition_digest` 随面板变化）；不改 FactorDef schema。
- **DR-003**：不新增目录：沿用 `run_dir/{run.json,events.jsonl,factors/,feature_maps/}`，新增一个文件 `prefilter.jsonl`；本 feature 不写 `pool.json`。

### API / 接口需求

- **IR-001**：CLI `mine --generator {manual,alphagen}`；alphagen 的 config 按「`DEFAULT_MINE_CONFIG` 公共段 + `DEFAULT_ALPHAGEN_CONFIG`（含 `tier_level=L0`、`total_timesteps`、`pool_capacity`、`datasets`、`resample`、`objective.*`）+ 用户 `--config`」合成，`objective` 段一层深合并；manual 的 config 合成与现状一致。
- **IR-002**：`--quota` 对 alphagen 的语义为入册上限（≥1）；对 manual 语义不变。
- **IR-003**：退出码沿用 F003（0 OK / 1 FAILED / 2 REJECTED）；`partial` 以退出码 0 结束但 stdout 摘要标 `status=partial` 与 `stop_reason`（运维可见，不触发 systemd 重试）。
- **IR-004**：F013 消费本 feature 产物的契约 = `status=completed` 的 run_dir（run.json v2 + events.jsonl + factors/ + prefilter.jsonl），因子经 `factor_store.load` 读取；本 feature 不读写 `experiment_store`，不为 F007 改事件格式。

### 非功能需求

- **NFR-001**：产能目标：执行机 CUDA 下单次运行在一个夜槽（22:00–06:30）内以 `--quota 50` 入册 50 个候选（沿用 F003 `NFR-001`，M2 出口前置能力）。实跑须如实留痕耗时、显存峰值、各级计数；**未达 50 时如实登记为 M2 产能发现、由 owner 裁决预算或宇宙调整，不阻塞本 feature 收口，也不降低门槛**（owner 2026-09-27）。
- **NFR-002**：可复现：同一绑定、种子、config 与代码 ⇒ 同一入册 `definition_digest` 序列（CPU 下严格；CUDA 下记录非确定性来源）。
- **NFR-003**：预筛开销：逐候选计量并在运行摘要报告 p50/p95；开工前（T002）在执行机按真实面板实测，p95 > 1 s 时须先回写 design 的加速方案并经 owner 裁决后再实现；任何情况下不得静默跳过或抽样预筛。
- **NFR-004**：`src/**/*.py` ≤350 行（`cli.py` 343、`run_store.py` 350 行已近/达上限，必须拆分而非突破；迁出清单与导入方改动见 design §1）。
- **NFR-005**：事件与预筛记录写出为线性开销：万级事件写出耗时与事件数近似线性（单写者、不回读、批量 fsync）。

## 5. 生命周期与不变量

```text
mine --generator alphagen
  [安装 SIGTERM/SIGINT 标志] 绑定校验 → 能力自检 → build_tensor(窗口) → 训练时段 → Kronos 卸载 → GPU 单槽 → 护栏
  build_stock_data → 训练（每次表达式评估回调）:
      渲染 → 绑定湖通道 → 自检 → 查重(definition_digest) → 预筛(截面中位数仓位) → 入册 | 拒绝(事件)
      registered == quota ⇒ 停（quota_reached）
      夜槽结束 ⇒ 停（window_closed）; SIGTERM/SIGINT ⇒ 停（interrupted）
  步数耗尽 ⇒ budget_exhausted
  终态: quota_reached | budget_exhausted → completed
        window_closed | interrupted       → partial（评测不可见）
  pool 恒为 null
```

不变量：

- `proposed == registered + Σrejected`，且拒绝事件数与 `counts.rejected` 逐项相等；
- 入册 ⊆ 通过自检 ∩ 通过预筛 ∩ 本运行内 `definition_digest` 唯一；
- `registered <= quota`；
- run.json 只写一次，字段与实际一致（不写死）。

## 6. 成功与验收

### 成功标准

- **SC-001**：执行机上完成一次 `mine --generator alphagen --quota 50` 夜槽实跑并如实留痕；入册 50 为目标，未达即登记 M2 产能发现（NFR-001）；
- **SC-002**：零交易与重复表达式在生产路径上被拒且可审计，宇宙规模在运行记录中可区分（F003 `AC-006` 获得真实载体）；
- **SC-003**：F013 可仅凭 run_dir 契约消费本 feature 产物，无需读取 vendor 内部结构。

### 验收清单

- [x] **AC-001** (`FR-001`, `DR-001`, `DR-003`, `US-001`): 小面板 alphagen 运行（v2 run.json）入册的每个因子 `generator="alphagen"`、假设 `mechanism_unknown`、token 已绑定湖通道名，经 `factor_store.load` 反解后在同一面板上信号逐点一致；v1 manual 运行仍可 `load` — tests: `tests/integration/test_f012_alphagen_mining.py`
- [x] **AC-002** (`FR-002`, `IR-002`, `US-001`): `--quota 3` 时入册恰为 3、`stop_reason=quota_reached`；步数先耗尽时 `stop_reason=budget_exhausted` 且入册 < 配额；张量面板首尾时间戳落在 `(window.start, window.end]` — tests: `tests/integration/test_f012_alphagen_mining.py`
- [x] **AC-003** (`FR-003`, `DR-002`, `US-002`): 恒定信号以 `reachability` 拒绝；截面排名等恒正信号按截面中位数换算仓位后产生交易并按真实指标判定；低于最少交易笔数与成本后收益阈值者被拒；全 NaN / 非有限信号为候选拒绝而非运行失败；`objective` 含 `position_rule`；`prefilter.jsonl` 每候选一行且指标不进 FactorDef 身份 — tests: `tests/unit/test_f012_candidate_pipeline.py`
- [x] **AC-004** (`FR-004`, `NFR-005`, `US-002`): 重复表达式按 `definition_digest` 以 `duplicate_definition` 拒绝；缺湖通道 token 以 `unregistered_op`（`detail=missing_channel:*`）拒绝；畸形 token 以 `unregistered_op` 拒绝而非运行失败；events.jsonl 拒绝事件按原因码计数与 `counts.rejected` 逐项相等、`proposed == registered + Σrejected`；1 万条事件写出耗时近似线性 — tests: `tests/unit/test_f012_candidate_pipeline.py`
- [x] **AC-005** (`FR-005`, `US-003`): 夜槽结束、训练中 SIGTERM、排队等槽时 SIGTERM 三种停止均得 `status=partial`、对应 `stop_reason`/`termination`/`reason`、`pool=null`、已入册候选落盘且 `factor_store.load` 拒绝加载；GPU 槽释放、Kronos 恢复路径被调用；等槽时取消会写 `cancelled` 队列记录，随后另一运行可取到槽 — tests: `tests/unit/test_f012_stop_conditions.py`
- [x] **AC-006** (`FR-006`, `IR-001`, `IR-003`): CLI 接受 `--generator alphagen`；`--generator manual` 与改动前 main 基准按 `FR-006` 口径可观察等价；alphagen 缺省 config 合成后 `tier_level=L0`，用户只给部分 `objective` 键时 `position_rule` 仍为 `cs_median`；未知生成器被 argparse 拒绝；alphagen 给非 L0 层级以 `unknown_tier` 拒绝；零行张量与窗口内宇宙为空均在 Kronos 卸载前以 `invalid_binding` 拒绝；同名通道冲突以 `invalid_config` 拒绝 — tests: `tests/unit/test_f012_cli_contract.py`
- [x] **AC-007** (`FR-007`, `DR-001`): run.json v2 字段如实（`tier_level=L0`、`universe.source/pair_count`、`vram_limit_gb`、`kronos_offload`、`objective`、`budget`、`stop_reason`、`evaluations`，`code_digest != config_digest`）；v1 run.json 仍可 `load_run` — tests: `tests/unit/test_f012_run_schema.py`
- [x] **AC-008** (`FR-008`, `US-001`): 同一种子、数据版本相同而宇宙成员不同的两个显式绑定分别运行，两份 run.json 的 `universe.pair_count` 不同且等于各自窗口内曾在宇宙的 pair 数 — tests: `tests/integration/test_f012_alphagen_mining.py`
- [x] **AC-009** (`NFR-001`, `NFR-003`, `SC-001`): 执行机 `qiaozhi-lt` CUDA 夜槽以 CLI 实跑 `mine --generator alphagen --quota 50`（真实湖显式绑定），取证文件 `reports/f012/capacity-evidence.json` 记录 run_id、status、stop_reason、registered、各级拒绝、耗时、显存峰值、预筛 p50/p95；取证校验用例断言字段齐全且与 run.json 一致；未达 50 时同时登记 M2 产能发现 — tests: `tests/integration/test_f012_capacity_evidence.py`
- [x] **AC-010** (`FR-002`, `US-002`): vendor 默认动作空间内每个算子构造的表达式经修正后的渲染器渲染，滚动与成对滚动算子带窗口（`name:N`，含 `corr:N`/`cov:N`）且不再被判 `lookahead`、能被 `build_factor` 编译；`CSRank` 渲染为 `cs_rank`；时序 `Rank` 渲染为 `ts_rank:N` 并以 `unregistered_op` 拒绝 — tests: `tests/unit/test_f012_render.py`

取证（2026-09-27，执行机 `qiaozhi-lt`，需求分支 `feat/F012-alphagen-mining-cli`）：F012 七个测试文件
`test_f012_render.py`（25）、`test_f012_candidate_pipeline.py`（26）、`test_f012_stop_conditions.py`（5）、
`test_f012_cli_contract.py`（13）、`test_f012_run_schema.py`（16）、`test_f012_alphagen_mining.py`（12，真实 PPO +
scratch 湖经 CLI）、`test_f012_capacity_evidence.py`（4）共 101 passed；统一质量门 `tools/verify.py` exit=0
（1734 passed / 32 skipped / 1 xfailed）。manual 等价基准取自改动前 `main@84ab505` 实跑（AC-006）。变异验证判红：
畸形 token 分支、槽释放、护栏外预热（去掉即 3 条 CLI 集成红）。AC-009 夜槽实跑（`reports/f012/capacity-evidence.json`）：
run `alphagen-20260927T140500683819Z-67053132` completed/quota_reached，入册 50/50，proposed 325（unregistered_op 48 /
reachability 163 / duplicate 64），638 s，显存峰值 0.24 GB，Kronos 卸载并恢复。已知发现：预筛 p95 1563 ms（n=213）超
T002 的 1 s 阈值（p50 318 ms），尾部来自成对滚动算子，交代码检视裁决。

## 7. 测试、依赖与决策

### 测试策略

- 单元：候选流水线（通道绑定 → 自检 → 查重 → 预筛 → 入册/拒绝、事件线性写出）、停止条件与信号处理、run.json v2 schema 与 v1 双读、CLI 分发、manual 基准等价与退出码；AlphaGen 训练以桩替身驱动回调，不依赖 torch。
- 集成：`mining` extra 下小面板（scratch 湖）真实 AlphaGen 训练，覆盖入册反解、配额停止、窗口跨度、宇宙规模可区分；无 torch 环境按项目约定 `importorskip`。
- 执行机取证：AC-009 以 CLI 在 `qiaozhi-lt` CUDA 夜槽实跑并写取证文件，取证校验用例只校验文件；开发机 skip 不算证据。

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
| 截面因子信号→仓位（owner 2026-09-27，检视 D03） | 每个时点减在宇宙内 pair 的截面中位数后取符号 | 与 F007 多空分位评测口径一致；原 `sign(signal)` 把恒正的截面因子全判零交易 | — |
| 协同池（owner 2026-09-27，检视 D12） | F012 不注册，`pool` 恒 null | M2 出口只需单因子批量；协同池 meta-factor（FR2.6）另立项 | BACKLOG 登记 |
| 产能未达 50（owner 2026-09-27，检视 D17） | 如实登记 M2 产能发现，不阻塞收口、不降门槛 | 产能是能力标定（ADR-0008），不是本 feature 正确性 | owner 裁决预算/宇宙 |
| 层级 | alphagen 固定 L0 | ADR-0001：L1 为绕开 sb3/RL 的求值器 + 自写搜索 | — |
| 自检时机 | 边训练边自检（评估回调内） | 事后统一自检无法按配额提前停，也无法在夜槽结束时保留已完成工作 | — |
| 风险：预筛开销拖慢训练 | T002 在执行机实测 p95；>1 s 先回写加速方案并裁决 | 不得静默跳过或抽样预筛（ADR-0003） | 执行机实测 |
| 风险：35 对小宇宙上横截面 reward 噪声大 | 沿用 F003 §7 结论，运行留痕 `pair_count` | 宇宙扩大属「宇宙口径 v2」 | — |

## 8. 待确认问题

- [x] Q-001: F012 是否拆分？ — 决策（owner 2026-09-27）：拆为 F012（生成侧）与 F013（批量评测编排）。
- [x] Q-002: `--quota` 对 AlphaGen 的语义？ — 决策（owner 2026-09-27）：入册上限；`total_timesteps`、`pool_capacity` 为 config 预算，任一先到即停。
- [x] Q-003: 夜槽结束或中断的运行如何处理？ — 决策（owner 2026-09-27）：记 `partial`，已入册候选落盘，不进评测。
- [x] Q-004: 批量评测用 preview 还是 canonical？ — 决策（owner 2026-09-27）：直接 canonical，看结果前冻结整批 cohort（由 F013 实现）。
- [x] Q-005: 截面因子的信号如何换算成预筛仓位？ — 决策（owner 2026-09-27，文档检视 D03）：每个时点以在宇宙内 pair 的信号减去该时点截面中位数后取符号。
- [x] Q-006: F012 是否注册 AlphaGen 协同池？ — 决策（owner 2026-09-27，文档检视 D12）：不注册，`pool` 恒为 null；协同池另立项。
- [x] Q-007: 执行机实跑入册不足 50 时如何收口？ — 决策（owner 2026-09-27，文档检视 D17）：如实登记为 M2 产能发现、由 owner 裁决预算或宇宙调整，不阻塞本 feature 收口，不降低门槛。
