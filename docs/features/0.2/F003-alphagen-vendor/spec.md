---
kind: feature
id: F003
version: "0.2"
status: developing
branch: feat/F003-alphagen-vendor
gate_version: 1
related_features: [F001, F002, F007, F008]
topics: [factor-factory, alphagen, vendor, generators, m2]
doc_kind: spec
created: 2026-09-14
updated: 2026-09-26
---

# F003：AlphaGen vendor 与可插拔生成器平面

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册）、FR2.2（可插拔生成器）、FR2.3（目标对齐）、FR2.4（纯度与能力边界）、FR2.6（探索组合）；目标 G3；里程碑 M2
- **架构来源**：`docs/alphamill-architecture.md` §三（`factor_factory/` 目录分工）、§4.0（闭环核心对象）、§4.1（FactorDef 契约）、§4.1.1（AlphaGen 适配契约与截面边界）、§7.1（机器边界与 GPU 槽位）
- **系统设计 / Research / Contract 来源**：`docs/alphamill-research-factor-mining.md` §3.1（AlphaGen 证据：核心冻结、requirements 腐化、算子集、可替换数据层）；`docs/alphamill-integration.md` §五（vendor 卫生规则）
- **上游决策**：ADR-0001（主引擎选型、冒烟即闸门、降级阶梯与切换判据）、ADR-0002（vendor/fork/原样依赖三分法与 vendor 卫生规则）、ADR-0003（门禁不降级——生成器不得自裁决证据）、ADR-0007（研究快照绑定）
- **基座来源**：F001（`src/alphamill/` 布局、GPU/WSL2 执行环境）、F002（Parquet 湖 `(dataset, data_version, value_digest)` 只读 reader 与 symbol_map）
- **功能类型**：backend / runtime
- **规格模式**：full
- **变更类型**：ADDED
- **一句话意图**：把 AlphaGen 核心按 vendor 卫生规则接进主仓并在现代栈上跑通，配上不可变快照绑定的数据面与表达式↔FactorDef 适配层，让「可插拔生成器」从纸面选型变成能批量产出候选定义的生成器平面，并用二元闸门决定主引擎锁定还是降级。

## 1. 问题、目标与非目标

### 问题

PRD G3（ADR-0008 修订后）要求因子工厂具备单批 ≥50 候选自动评测的批量能力并同时报告有效独立数与来源分布——名义吞吐仅作能力标定与漏斗分母，不设周产出配额；quant-crypto 实测约 5 个/周。今天仓内 `src/alphamill/factor_factory/` 只有 F001 原样迁入的评测脚本：没有生成器接口、没有可执行的 FactorDef、没有把 F002 湖快照喂进挖掘引擎的数据面——因子工厂这一平面是空的。

ADR-0001 已锁定主引擎为 AlphaGen（vendor 方式），但同一份调研也记录了它的硬伤：核心代码冻结约 21 个月、`requirements.txt` 自身损坏（`qlib==0.0.2.dev20` 是装错的包，numpy/pandas 为 2020-2021 年版本）、内置数据层绑死 qlib bin。**"能不能在现代栈跑起来"至今没有被任何人在本项目验证过**——选型目前只是纸面决策，而 ADR-0001 为此预写的 2 个工作日 time-box 与降级判据还没有被执行过一次。

### 目标

- `factor_factory/generators/` 出现统一 `produce()` 接口与**两个独立后端**（AlphaGen RL 主引擎 + 人工 crypto 原生种子后端），替换后端不改调用方；
- AlphaGen 核心在 vendor 卫生规则下进主仓（最小 diff、`# [alphamill]` 标注、`VENDORED.md` 溯源），在 pin 的现代栈上跑通训练并向协同池产出因子；
- 挖掘运行的输入是 F002 不可变快照的**显式版本绑定**，输出是只带定义、不带结论的 FactorDef 与协同池 meta-factor，全部可由 `(seed, 快照绑定, 表达式)` 重建；
- 2 个工作日 time-box 内得到二元裁决：主引擎锁定 L0，或按 ADR-0001 判据降级到 L1，裁决与触发原因入档；**L1→L2 不在 time-box 内**——须由 L1 连续 2 周满足 ADR-0001 判据触发。

### 非目标

- 本 feature 不做证据评测、统计裁决、多重检验与**成本裁决**（三档成本结论与 `cost_model_version` 归 `F007`）——生成侧只做可配参数下的**成本后收益预筛**，不产 verdict；漏斗记账见 FR-006 的第一级义务（评测权归 `F007`，生成器只产候选，ADR-0003、PRD AI 权限红线）；
- 本 feature 不做 PortfolioDef 构建、权重与组合门 → FR4 / M3 Feature；
- 本 feature 不做宇宙扩容（30~50 对，FR1.5）——那是数据面工作，已分配 `F008` 与本 feature **并行**推进（Q-001 裁决）；
- 本 feature 不追随 AlphaGen 上游：vendor 后由本项目全权维护，**永不 fork**（ADR-0002）。

## 2. 用户场景

### US-001：用统一接口拿到可复现的候选定义（Priority: P1）

作为研究员，我希望任意生成器后端都通过同一个接口产出结构一致、可复现、只含定义的 FactorDef，以便下游评测台不必为每个后端写一套适配。

**为什么是这个优先级**：这是与 AlphaGen 风险解耦的最小切片——即使冒烟闸门判定降级，接口与人工种子后端仍然成立，FR2.2 的"另一种独立后端"也随之交付。

**独立测试**：只启用人工种子后端，对固定快照绑定与固定 seed 连续跑两次 `produce()`，验证得到相同的 factor_id 集合与可执行的 `compute`，全程不加载任何 AlphaGen 代码。

**验收场景**：

1. Given 一个有效的快照绑定与人工种子后端，when 执行生成运行，then 产出的每个 FactorDef 通过 schema 校验、带真实 `hypothesis_id`，且不含任何评测结论字段。
2. Given 同一 `(seed, 快照绑定, code digest)`，when 重跑生成运行，then 得到完全相同的 factor_id 集合。
3. Given 快照绑定指向 `invalid` 的 data_version，when 启动生成运行，then 运行被拒绝且不产出任何候选。

### US-002：两个工作日内得到引擎的二元裁决（Priority: P1）

作为研究负责人，我希望 AlphaGen 的可用性在固定 time-box 内被判定为"锁定"或"降级"，以便不把沉没成本变成里程碑风险。

**为什么是这个优先级**：ADR-0001 的选型结论依赖这个闸门；闸门不跑，M2 的全部批量能力承诺都建立在未验证假设上。单人 time-box 最容易自我豁免，因此判据必须是自动判定的二元项。

**独立测试**：在最小数据切片上执行 `alphamill-generate smoke`，检查 ADR-0001 的 **L1 三条判据**逐条产出 `pass/fail` 与时间戳，并核验 ADR-0001 的两条 M2 义务（逐级计数自第一天入库、奖励频率抽查）已写入当日冒烟 manifest。

**验收场景**：

1. Given 现代栈与 vendor 核心就位，when 冒烟第 1 天结束，then 记录"是否跑通 1 个 PPO epoch"与"最小训练循环是否跑通"的二元结果。
2. Given 冒烟第 2 天结束仍未产出可做 IC 口径对齐的因子，when 判定闸门，then 输出降级裁决（L1）并记录触发判据，不输出"通过"。
3. Given 闸门已判定降级，when 有人请求回切主引擎，then 系统要求重开一轮 time-box，不接受直接回切。

### US-003：一次挖掘批量产出候选与协同池（Priority: P2）

作为研究员，我希望一次夜间挖掘运行产出足量互补候选，并把协同池本身注册为可部署 meta-factor，以便产能按 FR2.6 以"有效互补"而非"公式数量"衡量。

**为什么是这个优先级**：它依赖 US-001 的接口与 US-002 的引擎裁决，但独立于 F007 评测台——候选定义先攒起来，评测台就位后即可批量入场。

**独立测试**：在固定快照绑定上跑一次完整挖掘运行，统计入册候选数、自检拒绝数与协同池成员，验证池的重算值与训练期记录一致。

**验收场景**：

1. Given 一次训练窗口内的挖掘运行，when 运行完成，then 入册候选数 ≥50 且每级计数（产出/自检拒绝/入册）写入 GenerationRun。
2. Given 协同池已产出，when 把池导出为 meta-factor，then 成员 factor_id 与权重可反解，且按成员定义重算的池值与记录一致。
3. Given 一个零交易/持仓型表达式（信号几乎不变号），when 参与池选择，then 它被换手惩罚或可达性预筛排除，不占据池位。

## 3. 范围与边界

### 范围内

- 生成器接口 `produce()` 与两个独立后端：AlphaGen RL 主引擎、人工 crypto 原生种子后端；
- AlphaGen 核心子集 vendor（表达式/张量求值器/线性协同池/RL 环境）+ 现代依赖栈 pin + `VENDORED.md` 溯源 + vendor 卫生门禁；
- 快照绑定的湖→张量数据面（读 F002 reader，point-in-time 宇宙掩码取 F008 的 `universe_at(T)` 与内容寻址台账 digest，特征列→张量通道 `feature_map`）；
- 表达式 token 序列 ↔ FactorDef 适配层（闭包编译、表达式原文可反解、`data_columns` 反解、截面边界）；
- 算子能力登记表与生成侧自检（未登记算子/前视/跨 pair 非法算子直接拒绝并计数）；
- 目标对齐（换手惩罚、≥30 笔/90 天可达性预筛与成本后收益预筛）与其参数入档；
- 冒烟闸门、二元降级判据（time-box 内只裁 L0/L1）、L1/L2 降级阶梯定义与裁决记录；
- FactorDef / HypothesisDef / GenerationRun 的定义级持久化与 CLI 入口。

### 范围外

- RankIC/IC 衰减/分位数/成本门三档裁决/多重检验/样本量裁决与任何 verdict → `F007`；F003 只保留参数化的成本后收益预筛（不产成本裁决）；
- ResearchSnapshot 的实现（归 `experiment_store/`，随 `F007` 落地）——F003 只消费绑定，冒烟期用显式元组过渡（Q-002）；过渡元组须携带与 ADR-0007 对齐的语义字段（`schema_version`、`cutoff_time`、逐 dataset `as_of_fidelity`/`event_time_min`/`event_time_max`、`symbol_map_digest`、**独立且分别校验的 universe（F008 台账）与 calendar artifact 引用**及其组合导出的 `universe_calendar_digest`、不可变 artifact 的 provenance 引用），仅不落 snapshot artifact；F007 落地时须先发布 `ResearchSnapshot` 再替换为 `snapshot_id`（ADR-0007 决策 4/5）；
- 因子注册表的**定义面**（`FactorDef` 内容寻址读写、内容版本与定义级引用）归本 feature 的 `registry/`；**评测摘要回写与 `|ρ|`（`>0.99` 拒绝 / `0.90~0.99` 标记变体）查重判定** 的 owner = `F007`（评测面唯一写入者，v0.2 起，载荷见 F007 `DR-008`）；**lifecycle 状态判定** v0.2 无 owner——依赖 paper/实盘表现监控数据，后移 M3 归 `F006`（与无前视 L2/L3 审计同批，BACKLOG「规划中」行）；**lifecycle 动作执行** 的 owner = `F006`（运营操作入口）；F003 不持有评测摘要或 lifecycle 状态，只向下游提供定义与 `generation.*` 事件；
- 宇宙扩容 30~50 对与新 pair 质量流程（FR1.5）→ `F008`（并行推进，不阻塞本 feature 的接口与闸门交付）；
- 批量移植 GTJA191 / WQ101 公式库作为种子宇宙 → 后移（见 §7 决策）；
- 研究控制台与任何页面 → `F005`。

### 边界场景

- 快照绑定指向 `invalid` 或缺失 `value_digest` 的 data_version：拒绝启动，不做"先跑再说"。
- 训练窗口外或可用显存低于预算时启动挖掘：进单槽 FIFO 队列等待，绝不与 Kronos 常驻推理并行赌 OOM。夜槽开始时先卸载 Kronos 常驻推理（**live owner = F003**，经架构 §7.1 服务生命周期契约，服务端实现归 BACKLOG 待分配 feature）并校验显存释放，失败即留在队列。
- vendor 代码尝试联网（下载数据/权重）：生成运行在**进程级** egress guard 下执行，任何 egress 尝试视为失败（护栏缺失即拒绝启动；不等价于内核级网络隔离）。
- 表达式引用了未登记算子或未在 `feature_map` 中的特征：生成侧拒绝该候选并计数，不静默丢弃、不降级为"可用"。
- 冒烟闸门 time-box 到期而判据未达标：输出降级裁决；不允许以"再给一天"延期。
- 在开发机（`qiaozhi-gp`/`gp-wsl`，AMD iGPU 无 NVIDIA）执行：只允许走单元/契约层的 CPU 回退路径，运行记录标注 `device=cpu` 与 hostname，该运行不得用于产能或显存结论；挖掘训练的真实证据一律在执行机取（架构 §7.1、`docs/SOP.md` §3 机器边界）。

## 4. 需求

### 功能需求

### Requirement: 可插拔生成器接口（`FR-001`）

系统应当提供统一生成器接口，输入为生成请求（快照绑定、seed、配置、配额），输出为 FactorDef 列表与逐级自检计数；后端替换不得要求调用方改动，且任何后端都不得在返回值中携带评测结论字段。

#### Scenario: 两个后端同一接口

- GIVEN AlphaGen 后端与人工种子后端各自的配置
- WHEN 调用方以相同请求结构分别执行 `produce()`
- THEN 两者返回同一 schema 的结果，调用方代码无分支差异

#### Scenario: 后端试图返回结论

- GIVEN 一个后端在结果中写入 IC 或 verdict 字段
- WHEN 结果通过 schema 校验
- THEN 校验失败并拒绝入册

### Requirement: AlphaGen vendor 卫生与可复现构建（`FR-002`）

系统应当把 AlphaGen 核心子集置于 `factor_factory/generators/alphagen_vendor/`，丢弃上游 `requirements.txt` 并改用本仓 pin 的现代栈；vendor 目录内每处修改标注 `# [alphamill] <原因>`，`VENDORED.md` 记录上游 repo、commit hash、vendor 日期、修改清单与许可说明；并冻结**可复现的上游基线**（上游 commit 的逐文件 sha256 清单，随 vendor 入库），使"每处修改"能与基线逐文件比对，而不是只靠人工承认的修改清单；胶水代码一律放在 vendor 目录之外。

#### Scenario: 未标注的 vendor 改动

- GIVEN vendor 目录内存在与上游不同、且无 `# [alphamill]` 标注的行
- WHEN 运行 vendor 卫生检查
- THEN 检查失败并指出具体文件与行

#### Scenario: 依赖方向反转

- GIVEN vendor 目录内的模块 import 了 `alphamill` 胶水模块
- WHEN 运行 vendor 卫生检查
- THEN 检查失败（依赖方向必须是 glue → vendor 单向）

### Requirement: 快照绑定的湖→张量数据面（`FR-003`）

当生成运行启动时，系统应当按显式快照绑定经 F002 只读 reader 取数，构造 `(时间 × pair × 特征)` 张量与 point-in-time 宇宙掩码；绑定缺失、指向 `invalid` 版本或 `value_digest` 校验不符时，系统应当拒绝启动。数据面不得直读 TimescaleDB，也不得在运行时解析 `latest`。

#### Scenario: 绑定失效

- GIVEN 快照绑定引用的 data_version 已标记 invalid
- WHEN 启动生成运行
- THEN 运行被拒绝，不产出候选，拒绝原因写入运行记录

#### Scenario: 张量与湖一致

- GIVEN 一个已构造的特征张量与同一绑定下的 reader 行集
- WHEN 在抽样时间点与 pair 上比对
- THEN 数值在浮点容差内一致，且 pair 在不可交易时点的掩码为不可用

### Requirement: 表达式 ↔ FactorDef 适配（`FR-004`）

系统应当把 AlphaGen 产出的表达式 token 序列编译为标准 `FactorDef.compute` 闭包（`generator="alphagen"`），把表达式原文写入 `meta["expression"]` 保证可反解，并由表达式引用的特征经 `feature_map` 反解出 `data_columns`；横截面 rank/标准化/去均值只允许在同一 timestamp 的 point-in-time 宇宙内计算。

#### Scenario: 编译结果与张量求值一致

- GIVEN 同一表达式与同一数据切片
- WHEN 分别用编译后的 `compute` 与 vendor 张量求值器计算
- THEN 两者结果在浮点容差内一致

#### Scenario: 截面越界

- GIVEN 某 pair 在该时点不可交易或缺少宇宙成员快照
- WHEN 计算横截面算子
- THEN 结果为 no-signal，不得用当前成员表回填历史

### Requirement: 生成侧能力边界与目标对齐（`FR-005`）

系统应当维护算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 日历下的窗口换算），对每个候选执行生成侧自检：引用未登记算子、隐含前视、未支持的跨 pair 算子或不满足 ≥30 笔/90 天可达性预筛的候选一律拒绝并计数；奖励或前置筛选应当同时考虑预测证据、换手、≥30 笔/90 天可达性**与成本后收益**（按可配成本参数计算，参数与口径写入运行记录），禁止只优化 RankIC。成本后收益在此是**预筛信号而非成本裁决**——三档成本结论与 `cost_model_version` 归 `F007`（ADR-0003）。

#### Scenario: 零交易型表达式

- GIVEN 一个信号在整个窗口内几乎不变号的表达式
- WHEN 计算奖励或执行可达性预筛
- THEN 该候选被排除且拒绝原因记为可达性不足，不进入协同池

#### Scenario: 未登记算子

- GIVEN 表达式引用了不在算子能力登记表中的算子
- WHEN 执行生成侧自检
- THEN 候选被拒绝并计数，不得静默降级为可用

### Requirement: 冒烟闸门与降级阶梯（`FR-006`）

系统应当把 ADR-0001 的切换判据实现为自动判定的二元项：2 个工作日 time-box 内只输出「主引擎锁定 L0」或「降级到 L1」的裁决，并把裁决、触发判据与时间戳写入当日冒烟 manifest；**L1→L2 的降级不由 time-box 裁决**，只在 L1 连续 2 周满足 ADR-0001 判据（周候选 <50 或零候选通过无前视审计）时触发；降级不自动回切，回切须重开一轮 time-box。

冒烟期同时履行 ADR-0001「M2 冒烟验收」的两条义务，不推迟到"以后补"：

1. **漏斗逐级计数自第一天入库**：F003 负责生成侧第一级（`proposed`／各拒绝原因码／`registered`）写入 `run.json` 与 `generation.*` 事件；纯度门之后的下游各级在当日冒烟 manifest 中按 `owner=F007` + `state=not_yet_available` **显式占位**（不得省略、不得记为 0），交接契约为 `generation.*` 事件与算子能力清单（见 §5 明确后移）；
2. **奖励频率维度抽查**：对首批候选抽查换手惩罚／≥30 笔 90 天可达性预筛是否生效、IC 最优解是否机制性偏向零交易/持仓型表达式，抽查记录写入当日冒烟 manifest。

#### Scenario: time-box 用尽

- GIVEN 第 2 个工作日结束时仍未跑通 1 个 PPO epoch
- WHEN 判定闸门
- THEN 裁决为降级到 L1，触发判据与时间戳入档，不输出"通过"

#### Scenario: 请求直接回切

- GIVEN 当前档位为 L1
- WHEN 请求切回 L0 主引擎
- THEN 请求被拒绝，除非提供一轮新的冒烟 time-box 记录

### Requirement: 协同池导出为 meta-factor（`FR-007`）

系统应当把线性协同池导出为**可执行** meta-factor `FactorDef`（`generator="pool"`，加载后 `compute` 可按成员定义与权重重算、无需调用方拼装），成员引用 factor_id 与权重随定义持久化且可反解，池定义随成员或权重变化产生新 `factor_id` 版本；池的重算值应当与训练期记录在容差内一致。

#### Scenario: 池可反解重算

- GIVEN 一个已导出的协同池 meta-factor
- WHEN 按成员 FactorDef 与权重重算池值
- THEN 结果与训练期记录在容差内一致

### 数据 / 实体需求

- **DR-001**：`GenerationRun` 应当持久化快照绑定（`research_snapshot_id`，或过渡期的显式元组：`schema_version`、`cutoff_time`、逐 dataset 成员映射 `{<dataset>: (data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)}`、`symbol_map_digest`、**相互独立的** `universe` 引用（F008 台账 digest、`universe_at(T)` 语义、`schema_version`）与 `calendar` 引用（自身 schema 的内容寻址 artifact），以及由两者 digest **组合导出**的 `universe_calendar_digest` 与不可变 artifact 的 `provenance` 引用——字段与身份语义与 ADR-0007 一致，universe/calendar 拆分口径同 F007 DR-006）、seed、生成器与引擎版本、配置摘要（canonical config artifact 与 `config_digest`）、device、hostname、宇宙规模（pair 数与 `symbol_map_digest`）、档位与逐级计数；**宇宙规模是候选质量结论的前提条件，必须随运行留痕**。
- **DR-002**：`FactorDef` 应当以规范化 JSON 内容寻址持久化，`factor_id = <generator>_<definition_digest[:12]>`（**不含 run 序号**；运行归属由 `run_id` 承载，跨 run 重跑同一表达式得到同一 `factor_id`），并保存 `generator`、表达式原文、`params`、`scope`、`data_columns`、`hypothesis_id`、`definition_digest`、`run_id` 与生成来源引用；**不得**保存任何评测结论。
- **DR-003**：`HypothesisDef` 应当至少记录经济动机、作用机制、数据依赖、适用状态/regime（`applicable_state`，缺失时给显式默认值而非留空）、预期持有期、成本敏感性、来源与 generation；自动候选绑定 `mechanism_unknown` 假设并如实标记。
- **DR-004**：协同池 meta-factor 应当持久化为可执行 `FactorDef`（`generator="pool"`），定义中保存成员 `factor_id` 与权重、池版本与产出运行引用，加载后 `compute` 可按成员 `FactorDef` 重算；成员集合或权重变化必须产生新 `factor_id` 版本而非原地改写。

### 事件 / Trace 需求

- **TR-001**：生成运行**以 `status=completed` 结束**时，系统应当写入 `generation.run_completed`，payload 包含 run_id、generator、引擎版本、快照绑定、seed、device、档位与逐级计数；`rejected`/`failed`/`partial` 等非完成终态只写终态 `run.json`，不得写该事件。
- **TR-002**：生成侧自检拒绝时，系统应当写入 `generation.candidate_rejected`，payload 包含表达式原文、拒绝原因码（未登记算子 / 前视 / 可达性不足 / 重复定义）；事件应当可按 run 查询，供 `F007` 的漏斗第一级消费。

### API / 接口需求

- **IR-001**：CLI 应当提供 `smoke`、`mine`、`seed`、`show` 四个显式子命令；缺少快照绑定或引擎档位不明的 `mine` 请求应当以非零退出码拒绝。
- **IR-002**：`produce()` 应当接收生成请求对象并返回包含 FactorDef 列表与逐级计数的结果对象；接口不暴露任何评测或晋级能力。
- **IR-003**：`GenerationRun` manifest 与 FactorDef JSON 应当带 `schema_version`，供 `F007` / `F005` 只读消费；消费者不需要读取 vendor 内部结构即可还原候选定义。

### 非功能需求

- **NFR-001**：产能：单次挖掘运行应当在执行机的一个夜间训练窗口（22:00–06:30，≤8.5h）内产出 ≥50 个通过生成侧自检的候选（M2 出口量化线）。
- **NFR-002**：资源：挖掘训练按架构 §7.1 的时段表在夜槽内以 ≤6GB 独占运行（当前执行机 RTX 4060 Laptop 8GB 的标定值），显存上限可配并写入运行记录；启动前自检可用显存，低于上限或与在跑任务撞车时进单槽 FIFO 队列，不允许并行抢卡。**FIFO 须可验证**：入队 / 取锁 / 释放 / 等待超时各写一条带 `queue_seq`、`run_id`、时间戳的状态记录；先入队者先取锁，释放后由队首等待者取得；等待超过可配超时则留 `rejected` 终态（`termination=queue_timeout`），不无限挂起。
- **NFR-003**：可复现：相同 `(seed, 快照绑定, code digest, config_digest)` 重跑应当得到相同的 factor_id 集合与相同的协同池成员。配置摘要定义为 canonical config artifact（键排序、排除时间戳/主机字段）的 sha256，artifact 随运行落盘、可重放；RNG 由 `seed` 稳定派生，训练侧开启 torch 确定性开关；**CPU/GPU 差异只允许影响浮点末位、不改变候选集合**——本项断言的是集合与池成员一致（跨 device 亦然），不承诺逐位数值相同。
- **NFR-004**：安全 / 边界：生成运行在**进程级 egress guard** 下执行（runner 入口替换 socket 构造函数、只放行 AF_UNIX；这是进程级护栏，**不等于内核级网络隔离**——本 feature 不引入 netns/容器，如实声明）；写路径白名单限定 `reports/generation/<run_id>/`，生成器进程不具备写入证据台账、留出数据或晋级状态的能力（AI 权限红线、ADR-0003）。两类护栏都 **fail-closed**：护栏安装失败或白名单无法生效即拒绝启动，不降级为"仅警告"。
- **NFR-005**：兼容性：执行机的 WSL2 + CUDA 为主路径；开发机无 GPU，只允许 CPU 回退用于单元与契约测试；运行记录必须标注 `device` 与 hostname，开发机运行不得用于产能或显存结论。

## 5. 生命周期与不变量

```text
生成运行（四种终态 `completed` / `rejected` / `failed` / `partial`，均写终态 `run.json`）：
queued    -> running    取得 GPU 单槽 + 快照绑定校验通过 + 时段允许
queued    -> rejected   绑定缺失/invalid、digest 不符、档位不明、队列等待超时（写终态 run.json）
running   -> completed  候选集与 GenerationRun manifest 原子写出；仅本态发 run_completed、可被下游消费
running   -> failed     训练/求值/写出异常；写终态 run.json，已产候选不入册
running   -> partial    SIGTERM 优雅停机；保留已产候选供诊断，不写 pool.json、不发 run_completed

引擎档位（ADR-0001 降级阶梯，单向）：
L0 AlphaGen RL -> L1 表达式求值器 + 自写搜索   任一 L1 判据触发（2 日 time-box 内，自动判定）
L1             -> L2 纯 gplearn 基线           L1 连续 2 周：周候选 <50 或零候选通过无前视审计（ADR-0001）
L1/L2          -> L0                           仅在重开一轮冒烟 time-box 并通过后
```

不变量：

- 生成器只产定义：`FactorDef` 与 `GenerationRun` 内不得出现 verdict、IC、PnL 等结论字段；
- 终态唯一且可消费性明确：任何终止路径都写 `run.json`（`completed`/`rejected`/`failed`/`partial`），只有 `completed` 发 `run_completed` 并可被下游入册；
- 依赖方向单向：胶水代码可以依赖 vendor，vendor 不得依赖胶水代码；
- 任一入册候选都能由 `(run_id, seed, 快照绑定, 表达式原文)` 重建；
- 降级只由判据触发、不由主观判断推迟；档位变化必须留下触发原因；
- 研究数据来源只有 F002 湖快照，任何路径都不得直读 TimescaleDB 修订态。

## 6. 成功与验收

### 成功标准

- **SC-001**：接口成立——两个独立后端经同一接口产出可执行 FactorDef，FR2.2 的"至少两类可插拔生成器"达成；
- **SC-002**：裁决成立——2 个工作日内输出主引擎锁定或降级的二元结论，判据与时间戳入档；
- **SC-003**：产能成立——单次挖掘运行入册 ≥50 个通过自检的候选，协同池作为 meta-factor 注册并可反解重算；
- **SC-004**：边界成立——生成侧拒绝可计数、不静默降级，生成器无任何评测或晋级能力。

> **成功标准取证**：SC-001 由 AC-001/AC-004 锁定；SC-002 由 T019/T032 的 time-box 实跑与裁决回写（spec §7 决策表「冒烟闸门 time-box 裁决」行，2026-09-19 L0 锁定 AlphaGen）；SC-003 由 `test_f003_generation_run.py::test_generation_run_registers_fifty_candidates_when_integration_cuda_enabled`在执行机 CUDA 下断言 registered ≥ 50；SC-004 由 AC-005/AC-011/AC-012 与 `rejected` 终态用例锁定。

### 验收清单


> **取证（2026-09-26，执行机 `qiaozhi-lt` / RTX 4060 Laptop 8GB / 驱动 616.64）**：12 条 AC 引用的全部测试一次跑通——`ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q`（11 个文件）→ **163 passed，exit=0**（377.97s）。统一质量门 `python3 tools/verify.py` exit=0（1577 passed / 32 skipped / 1 xfailed）。
> **AC-006 的边界**：换手惩罚/可达性预筛与 run.json 参数记录已由 `test_f003_generation_run.py` 锁定；但「宇宙扩容 → 候选质量差异」在 CLI 路径上结构性不可观测（`--generator` 只接受 `manual`），T035 实测两次运行的 proposed/registered 与拒绝计数逐项相同，该口径的真实载体已登记为 BACKLOG 规划中的独立 Feature（AlphaGen 后端接入 CLI）。
> **AC-010 的显存证据**：T033 在执行机取得（54 passed / 1 skipped / 0 xfailed），夜槽卸载判据1.637 → 1.191 GB 见 T035 两次运行的 `kronos_offload`。
- [x] **AC-001** (`FR-001`, `IR-002`): 两个后端经同一 produce() 接口产出通过 schema 校验的 FactorDef；返回值含结论字段时校验失败；落盘 DTO 加载后得到的 FactorDef 可直接执行（compute 由表达式重建、meta 还原） — tests: `tests/unit/test_f003_generator_contract.py`
- [x] **AC-002** (`FR-002`): vendor 目录内每处改动带 alphamill 标注、VENDORED.md 记录上游 repo/commit/日期/修改清单/许可，且**改动集合与冻结的上游基线逐文件比对一致（差异集合 = 标注集合）**，vendor 不反向依赖胶水模块 — tests: `tests/unit/test_f003_vendor_hygiene.py`
  - **证据（2026-09-20）**：vendor 子集完整性此前只在开发机工作树上成立。`.gitignore` 的裸 `models/` 规则（本意是 Kronos 权重）匹配任意层级目录，把 `alphagen/models/{alpha_pool,linear_alpha_pool}.py` 整目录静默排除——`_upstream_baseline.json` 声明 20 个 blob，入库只有 18 个，任何干净 clone 上`from alphagen.models.linear_alpha_pool import MseAlphaPool` 都会失败。已对该路径显式反选并按 pin commit `259687e` 取回两个 blob，sha256 与 baseline 逐字节一致（属无修改集合，不需 `# [alphamill]` 标注）。AC-002 的成立范围由此从「开发机工作树」修正为「干净 clone」，取证载体为 CI（py3.11/py3.13）。
- [x] **AC-003** (`FR-003`, `DR-001`): 按显式绑定构造张量；invalid 版本或 digest 不符时拒绝启动并留 `rejected` 终态 run.json（含 termination/reason/时间戳与 DR-001 运行字段）；张量与 reader 行集在抽样点数值一致且不可交易时点掩码为不可用 — tests: `tests/integration/test_f003_lake_tensor.py`
- [x] **AC-004** (`FR-004`): 编译后的 compute 闭包与 vendor 张量求值在同一切片容差内一致；meta.expression 可反解为等价表达式；data_columns 由 feature_map 反解得到；落盘后加载的 FactorDef 可直接执行 — tests: `tests/unit/test_f003_alphagen_adapter.py`
- [x] **AC-005** (`FR-005`, `TR-002`): 算子能力登记表覆盖全部启用算子；未登记算子/前视/非法跨 pair 候选被拒绝并按原因码计数；拒绝事件含表达式原文与原因码且可按 run 查询（TR-002） — tests: `tests/unit/test_f003_operator_registry.py`
- [x] **AC-006** (`FR-005`, `NFR-001`): 换手惩罚/可达性预筛生效——零交易型表达式不进池；成本后收益预筛参数（`cost_model`、`min_after_cost_return`）写入 run.json 的 objective；在执行机上单次挖掘入册 ≥50 个通过自检候选 — tests: `tests/integration/test_f003_generation_run.py`
- [x] **AC-007** (`FR-006`): 冒烟闸门判据逐条自动判定并写入当日 manifest；任一触发即输出降级裁决且不输出"通过"；2 日 time-box 只裁 L0 锁定或 L1 降级，L2 须 L1 连续 2 周判据（ADR-0001）；ADR-0001 两条 M2 冒烟义务（逐级计数自第一天入库、奖励频率抽查）可核验，下游漏斗级以 owner=F007/not_yet_available 显式占位；回切须重开 time-box — tests: `tests/integration/test_f003_smoke_gate.py`
- [x] **AC-008** (`FR-007`, `DR-004`): 协同池导出为 meta-factor 并持久化为可执行 FactorDef（`generator=pool`，加载后可直接重算），成员 factor_id 与权重可反解，重算值与训练期记录容差内一致，成员或权重变化产生新 `factor_id` 版本 — tests: `tests/integration/test_f003_alpha_pool.py`
- [x] **AC-009** (`DR-002`, `DR-003`, `TR-001`, `NFR-003`): GenerationRun 记录引擎版本/绑定/seed/device/档位与逐级计数；同一组 seed/绑定/code digest/配置 重跑得到相同 factor_id 集合（factor_id 内容寻址、不含 run 序号，运行归属由 run_id 承载）；自动候选绑定 mechanism_unknown 假设且 `applicable_state` 取显式默认值（不留空）；FactorDef 以内容寻址 JSON 持久化且不含结论字段（DR-002）；HypothesisDef 字段齐备（DR-003）；completed 运行的 run_completed 事件可查（TR-001）；重跑得到相同协同池成员（NFR-003）；配置摘要以 canonical config artifact + `config_digest` 落盘（见 NFR-003） — tests: `tests/integration/test_f003_generation_run.py`
- [x] **AC-010** (`NFR-002`, `NFR-005`): 可用显存低于上限或与在跑任务撞车时运行进队列而非并行；FIFO 每类状态记录含 `queue_seq`/`run_id`/时间戳，先入队先取锁、释放后队首取得、等待超时留 `queue_timeout` 终态；夜槽卸载 Kronos（live owner = F003，经架构 §7.1 服务生命周期契约——服务端实现归 BACKLOG 待分配 feature，校验显存释放，失败即 fail-closed 留队列；未部署与 `device=cpu` 实例按架构 §7.1 观测→处置决策表记 `offload_not_needed`，404/`E_UNSUPPORTED_VERSION` 回落探测：`/health.device=cpu` 或设备侧 `memory.used` 低于阈值 → `offload_not_needed`；达到阈值或读数不可得 → fail-closed（不依赖 GPU 进程列表），停止失败与控制面不可达但服务在 fail-closed）且运行记录持久化 `device` / `hostname` / `kronos_offload`，开发机 CPU 运行被拒绝用于产能/显存结论 — tests: `tests/unit/test_f003_gpu_slot.py`
- [x] **AC-011** (`NFR-004`, `IR-001`): egress guard 安装后出网尝试被拒绝（socket 构造被替换、只放行 AF_UNIX；断言范围为**进程级护栏，非内核隔离**）、护栏缺失时拒绝启动；写 `reports/generation/<run_id>/` 之外路径（证据台账/留出/晋级状态）的尝试被拒绝；缺绑定的 `mine` 请求非零退出并留 `rejected` 终态 run.json — tests: `tests/integration/test_f003_boundaries.py`, `tests/unit/test_f003_cli_contract.py`
- [x] **AC-012** (`IR-003`): `GenerationRun` manifest 与 FactorDef JSON 均持久化 `schema_version`；`show` 遇到未知 `schema_version` 以非零退出拒绝，不做兼容性猜测 — tests: `tests/unit/test_f003_cli_contract.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：生成器接口 schema 与结论字段拒绝、算子能力登记表与自检原因码、表达式↔FactorDef 适配与反解、vendor 卫生检查、GPU 单槽与显存自检；
- 集成测试：真实 F002 湖快照上的张量构造与一致性比对、完整挖掘运行（计数/可复现/产能）、协同池导出与重算、冒烟闸门判据、边界（进程级 egress 护栏、越权写入、缺绑定拒绝）；
- 真实环境 / 手动验证：GPU 直通下的 PPO 训练窗口实测（显存峰值、单次运行耗时、入册候选数）与冒烟闸门 time-box 实跑；CI 无 GPU 时相应用例走 CPU 回退或按环境开关判红，不以 skip 代替证据（`docs/SOP.md` §3）；
- 不做的：任何 RankIC/成本/统计显著性的**裁决性**测试——那是 `F007` 的验收面；F003 只做 vendor 张量 IC 与 pandas 参考实现之间的数值一致性回归。

### 依赖

- 上游 Feature / Contract：F002 的 `data_bridge.reader.read()` 与 `(dataset, data_version, value_digest)` 身份、`symbol_map`；ADR-0007 的 `ResearchSnapshot` 语义字段（`cutoff_time`、`as_of_fidelity`、`event_time_min/max`、`symbol_map_digest`、`universe_calendar_digest`）——过渡期由显式元组承载同一语义；F001 的 `src/alphamill/` 布局；架构 §4.1/§4.1.1 的 FactorDef 与适配契约、§7.1 的机器边界与 GPU 槽位。**并行依赖**：`F008` 宇宙扩容——PIT 掩码消费其 IR-002 的 `universe_at(T)` 与内容寻址台账 digest（IR-003 的 `schema_version`），不阻塞接口与冒烟闸门，但候选质量结论以其落地后的宇宙为准；F008 未落地时掩码用显式 universe 配置并在运行记录里留 digest 与来源。
- 下游消费者：`F007`（把 FactorDef 与协同池作为评测输入，把 `generation.candidate_rejected` 作为漏斗第一级，把算子能力登记表作为 FR-002 的已登记算子能力清单消费；**因子注册表评测摘要回写与 `|ρ|` 查重判定的唯一写入 owner**——lifecycle 状态判定后移 M3/F006，BACKLOG 已登记）、`F006`（**lifecycle 动作执行入口**）、`F005`（只读展示候选与产能）、FR4/M3 组合构建。
- 外部 / 环境依赖：AlphaGen 上游仓库（vendor 时点 clone，之后不跟随）；torch 2.x / numpy 2.x / pandas 2.x / gymnasium / stable-baselines3，全部 pin；执行机提供挖掘训练的 CUDA 运行时（当前 `qiaozhi-lt`：Win11+WSL2 + RTX 4060 Laptop 8GB，按架构 §7.1 时段表；湖与训练同机，无跨机传输）；宇宙规模当前为 6 对（见 Q-001）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 第二独立后端选谁 | 人工 crypto 原生种子后端（FR2.2 的"人工"分支） | 与 AlphaGen 风险解耦，冒烟失败也能交付 FR2.2；顺带为 F007 提供正控制因子 | vendor 自带 gplearn/dso 仅在降级到 L2 时启用 |
| 是否等 F007 的 ResearchSnapshot | 不等：冒烟与挖掘期用显式元组绑定并标注过渡态，元组携带 `schema_version`／`cutoff_time`／`as_of_fidelity`／`event_time` 范围／`symbol_map_digest`，并把 universe 与 calendar 拆为两个独立 artifact 引用（口径同 F007 DR-006，组合导出 `universe_calendar_digest`）与 artifact provenance（与 ADR-0007 语义对齐） | ResearchSnapshot 归 `experiment_store/`，在 F003 内重复实现会产生第二真相源；若只带 `(dataset, data_version, value_digest)` 会丢失 PIT、映射与 provenance 语义，过渡态与正式身份不可互换 | F007 落地时先构造并发布 `ResearchSnapshot` 再切 `research_snapshot_id`（ADR-0007 决策 4/5），过渡路径删除 |
| 冒烟的 IC 对齐会不会变成影子评测台 | 只做数值一致性回归（vendor 张量 IC vs pandas 参考实现），不产 verdict、不写台账 | 评测权唯一属 F007（ADR-0003 门禁不降级） | F007 落地后该检查退化为 vendor 回归测试 |
| 生成侧要不要成本后收益 | 要：按可配成本参数（taker/maker/零成本）做预筛并把参数写进 `run.json` 的 `objective`，但不产成本裁决 | PRD FR2.3 要求目标对齐同时考虑成本后收益；ADR-0003 禁止生成器自裁决，成本门真相源在 F007（FR3.2 的 `cost_model_version` 与三档结论） | F007 落地后生成侧改为引用其 `cost_model_version`，预筛口径与其对齐 |
| 批量移植 GTJA191 / WQ101 作种子 | 不做：只手写少量 crypto 原生种子（funding carry、basis、OI 变化、截面动量、波动） | 公式库假设 A 股日频，含行业/市值/财报依赖，crypto 24/7 需重定义窗口 | 批量种子宇宙后移到独立 Feature |
| 横截面 reward 在 6~12 对上噪声大 | 接口与闸门验收允许 6 对；**产出质量结论**必须标注宇宙规模前提，并在 `F008` 落地后用扩容宇宙复跑一次对照 | ADR-0001 后果条：宇宙扩容是产出质量前提；小宇宙下 ADR-0001 的 L2 判据（连续 2 周候选 <50）也会失真 | `F008` 与本 feature 并行（Q-001 已裁决） |
| AlphaGen 无 LICENSE | 个人私有使用，非阻塞；`VENDORED.md` 如实记录许可状态 | ADR-0001 已裁决 | 若未来公开分发或商业化，须先向作者澄清 |
| 上游核心冻结、requirements 腐化 | 丢弃上游 requirements，自定 pin 现代栈；冒烟即闸门控制现代化成本 | ADR-0001/ADR-0002 | 超 time-box 即降级，不沉没成本 |
| 单卡三负载抢占 | 时段表 + 单槽 FIFO（带 `queue_seq`/超时的可验证协议）+ 启动前显存自检 | 架构 §7.1：队列赢，绝不并行赌 OOM——Kronos 常驻与挖掘训练在同一张卡上 | 夜槽卸载的 live owner = F003（经架构 §7.1 服务生命周期契约，服务端实现归 BACKLOG 待分配 feature，失败 fail-closed 留队列）；FIFO 协议由两个并发挖掘运行独立取证 |
| 开发机无 GPU | **预期状态，不是阻塞**：`qiaozhi-gp` 是 AMD iGPU 掌机，只跑编码/单元/门禁；挖掘训练、显存与产能证据一律在 `qiaozhi-lt` 取，验收证据记录 hostname 与设备 | 架构 §7.1 机器边界；`docs/SOP.md` §3：开发机 skip 不是证据也不是失败 | 执行机实测可用显存在 tasks T004 标定 |
| 执行机后续整体迁移到 `qiaozhi-lab` | F003 只面向**当前执行机 `qiaozhi-lt`** 验收；显存上限、时段表与产能结论都标注取证机器，迁移后重跑而非继承 | 迁移同时换平台（Win11+WSL2 → 原生 Ubuntu）与换架构（Blackwell sm_120 需 CUDA 12.8+ 的 torch 构建），沿用旧结论会失真 | 迁移动作按独立 Feature 立项（架构 §7.1） |
| **冒烟闸门 time-box 裁决（2026-09-19 实跑）** | **L0 锁定**：主引擎 AlphaGen 保留，不降级 L1，不产 L2（time-box 无此裁决权） | 第 1 天判据「跑通 ≥1 个 PPO epoch」pass（真实 615 次求值、252 个候选通过生成侧自检）；第 2 天判据「vendor 张量 IC vs pandas 参考对齐」pass（1200 点、`max_abs_diff=0.0`）；ADR-0001 两条 M2 义务入当日 manifest（生成侧逐级计数；下游 `owner=F007` + `state=not_yet_available` 显式占位，未省略未记 0）；无触发降级，`trigger=null` | 取证机器 `qiaozhi-lt` / `device=cuda` / RTX 4060 / torch 2.10.0+cu128；当日 manifest 归档于 `reports/generation/smoke/`（运行证据，`.gitignore` 不入库，需复跑可重放）；L1→L2 仍须 L1 连续 2 周满足 ADR-0001 判据，不由本裁决触发 |
| **CI 绿度曾是假绿（2026-09-20 修正）** | 两类缺陷并列修复：(a) `alphagen_generation.py` 顶层 from-import 触发 runner 的模块级 `__getattr__`，在无 mining extra 的环境（含 CI）于收集期拉起 torch；`test_f003_smoke_gate.py` 顶层 `import torch` 同理。两者使 pytest 整轮 `Interrupted`，**全部用例一条都没跑**。(b) 见 AC-002 证据的 vendor 缺文件。 | 收集期中断会让所有门禁静默失效——vendor 卫生门（T013 回归）正是被它挡住才没在 CI 暴露 (b)；「CI 红」当时被读成单点失败，实际是全量未执行 | 惰性导入 + 使用点 `pytest.importorskip("torch")`（沿用 `test_f003_generation_run.py` 既有约定），`ALPHAMILL_INTEGRATION` 判定仍排在 skip 之前，执行机 fail-closed 语义不变；修复后 CI py3.11/py3.13 双绿，本地 `tools/verify.py` 1132 passed / 39 skipped |

## 8. 待确认问题

- [x] Q-005: GPU 直通未就绪时 F003 怎么排期？ — 决策（2026-09-14, owner）：**问题不成立**——本机 `qiaozhi-gp` 是纯开发机（AMD iGPU），项目有独立执行机（同一时刻一台：当前 `qiaozhi-lt` / RTX 4060 Laptop 8GB，成熟后整体迁移至 `qiaozhi-lab` / RTX 5070 Ti 16GB）。开发机无 GPU 属预期状态，不阻塞 F003；挖掘训练与全部 GPU/产能证据在执行机取，验收记录 hostname 与设备。F003 只面向当前执行机验收，迁移后按 `docs/SOP.md` §3 重跑相关项。架构 §7.1 已同步
- [x] Q-001: 宇宙扩容（FR1.5，30~50 对）是否与 F003 并行立项？ — 决策（2026-09-14, owner）：**并行**。扩容分配为 `F008`，与 F003 同期推进；F003 的接口、vendor 与冒烟闸门验收可在现有 6 对宇宙上完成，但**候选质量结论**以 `F008` 落地后的宇宙为准，且每次运行必须留痕宇宙规模（DR-001）。并行的理由：小宇宙下无法区分「引擎不行」与「宇宙太小」，而 ADR-0001 的降级阶梯正要靠这个区分做裁决
- [x] Q-002: F003 是否等待 F007 的 ResearchSnapshot 落地？ — 决策：不等；冒烟与挖掘期使用显式 `(dataset, data_version, value_digest)` 元组绑定并标注为过渡态，F007 落地后切换为只收 `research_snapshot_id`，不在 F003 内重复实现快照身份
- [x] Q-003: 第二个独立后端选什么？ — 决策：人工 crypto 原生种子后端；不单独引入 gplearn 项目，vendor 自带的 gplearn/dso 仅作 L2 降级与对照基线
- [x] Q-004: 冒烟闸门的 IC 口径对齐是否需要评测台？ — 决策：不需要；F003 只做 vendor 张量 IC 与 pandas 参考实现的数值一致性回归，不产出证据、不裁决，评测权属 F007
