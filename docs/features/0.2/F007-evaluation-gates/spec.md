---
kind: feature
id: F007
version: "0.2"
status: draft
gate_version: 1
related_features: [F002, F003, F004, F008]
topics: [evaluation, validation, evidence, experiments]
doc_kind: spec
created: 2026-09-13
updated: 2026-09-17
---

# F007：统一评测台与证据门禁

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
- **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
- **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级数据源，只有 `status=completed` 的运行才发完成事件）、算子能力登记表（FR-002 已登记算子能力清单的消费源）与协同池 meta-factor
- **上游 Contract 来源（F008）**：point-in-time 宇宙台账内容寻址 artifact——`universe_at(T)` 语义查询与 digest（F008 `IR-002`）与 `schema_version`（F008 `IR-003`）；ResearchSnapshot 的 universe 摘要按显式 digest 引用，不解析 latest
- **上游决策**：ADR-0003（门禁不降级）、ADR-0005（曲线侧车）、ADR-0006（证据边界与身份）、ADR-0007（ResearchSnapshot）
- **功能类型**：backend / workflow / validation / data-model
- **规格模式**：full
- **变更类型**：ADDED
- **一句话意图**：让任意 FactorDef 能在不可变快照上经过显式 preview/canonical、方法论守卫、统计与成本裁决，产出可复现、可综合且不会污染正式试验总体的证据。

## 1. 问题、目标与非目标

### 问题

AlphaMill 已定义严格的产品门槛，但还没有可运行的统一评测入口、稳定实验身份、正式试验总体
或机器可消费的综合报告。直接迁入旧脚本会继续制造窗口、成本和统计口径分裂；直接依赖 ml4t
配套实现则无法满足必需指标失败关闭、crypto 日历和 F002 数据身份契约。

### 目标

- 同一 FactorDef、语义配置、ResearchSnapshot、代码摘要和种子稳定得到同一 `experiment_id`；
- preview 快速诊断但不能污染 canonical cohort、留出预算和 official population；
- canonical 运行按五阶段生成结构化裁决、不可变报告/曲线和跨 cohort 综合报告；
- 时间边界、统计估计器或产物发布失败时停止晋级并留下可定位证据。

### 非目标

- 不实现因子生成、PortfolioDef 构建或 Freqtrade 下单；
- 不为所有资产/频率承诺“只改配置即可迁移”；
- 不把 DML、PBO 或 Reality Check 设为 v0.2 的通用硬门；
- 不实现 F005 研究控制台，F007 只提供其只读真相源。
- 不实现无前视 L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳对齐）的审计器——owner 为 F006/M3；F007 只消费其证据并在缺失时于晋级前失败关闭（`FR-007`）。

## 2. 用户场景

### US-001：安全预览候选证据（Priority: P1）

作为研究员，我希望在不消耗正式试验与留出预算的情况下预览一个 FactorDef，以便尽早发现
数据、时间边界、信号质量和成本问题。

**为什么是这个优先级**：这是最小可用切片，能在 F002 快照和现有 Kronos/人工因子上独立运行。

**独立测试**：对固定 fixture 连续执行 preview，验证报告稳定且 canonical 台账完全不变。

**验收场景**：

1. Given 有效 DataVersion 与 FactorDef，when 显式运行 preview，then 只在 preview 命名空间生成诊断产物。
2. Given preview 请求留出或 official population 写入，when 执行，then 请求被拒绝且留下失败事件。

### US-002：正式评测与裁决（Priority: P1）

作为研究负责人，我希望以预注册 cohort 正式运行候选，以便得到能审计、能复现且统计口径一致
的 canonical 结论。

**为什么是这个优先级**：没有 canonical 单写边界与失败关闭，M1 的“可信证据底座”不成立。

**独立测试**：用正控制、白噪声控制和故意泄漏 fixture 跑 canonical；正控制产出完整证据，后两者
分别被统计/方法论门拦截。

**验收场景**：

1. Given 已冻结 cohort/窗口/规则和有效输入，when canonical 运行完成，then official population 只登记一次且报告引用完整身份链。
2. Given 必需统计量报错、值摘要变化或方法论守卫失败，when 运行，then verdict 为 `INCOMPLETE/FAIL` 且不能晋级。
3. Given cohort 还有承诺成员未形成终态证据，when 请求最终裁决，then cohort 保持 OPEN，任何成员不能晋级。

### US-003：跨实验综合诊断（Priority: P2）

作为研究负责人，我希望按 canonical cohort 查看漏斗、五阶段损失与最大约束，以便决定下一轮应
改数据、信号、组合、成本还是执行，而不是只看存活者排名。

**为什么是这个优先级**：它依赖 US-002 的稳定台账，但在 F005 上线前也可作为 JSON/Parquet 消费。

**独立测试**：从固定 canonical ledger 与曲线 fixture 重建报告，验证结果确定且不读取 preview。

**验收场景**：

1. Given 同一 cohort 的完成与失败运行，when 生成 synthesis，then 拒绝者也进入漏斗和分母。
2. Given 只有 preview 产物，when 生成 synthesis，then 输出空 canonical 结果而不混入 preview 指标。

## 3. 范围与边界

### 范围内

- FactorDef 的 preview/canonical 运行上下文、方法论门、统计/成本评测与样本量裁决；
- ResearchSnapshot、experiment/cohort/population 台账、report/curves/synthesis 不可变产物与 supersedes 谱系；
- 为冻结 PortfolioDef 预留同一评测输入协议和五阶段字段，但本 Feature 不负责构建组合；
- funding carry、BTC/ETH 截面动量正控制与白噪声/故意泄漏负控制。

### 范围外

- PortfolioDef 的成员选择、权重和边际贡献算法 → FR4/M3 Feature；
- 离线到决策时 parity、run_record、kill-switch 与启动对账，以及**无前视 L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳与陈旧度对齐）的审计器实现** → F006/M3；F007 只消费其证据，并在 L2/L3 非 `PASS` 时于晋级前 fail-closed 阻断（`FR-007`、`AC-009`、PRD FR3.6 / SOP 原则 3）。
- 模型族级联与 DML 诊断 → F003 或独立研究 Feature；
- 研究页面、人工审批和生命周期写路径 → F005/F006。

### 边界场景

- 数据值相同但 Parquet codec/路径不同：实验身份相同，provenance/file SHA 不同。
- preview 请求 latest：先把实际解析的 dataset versions/value digests 冻结为 ResearchSnapshot 再计算；canonical 禁止动态 latest。
- 最大标签 horizon 大于 embargo：方法论门拒绝，不自动扩大窗口后继续。
- 指标样本不足：输出 `UNDERPOWERED`，不把空值当作零或 PASS。
- 同一 canonical 语义运行重试：幂等返回既有实验；语义变化必须新建 ID 并可声明 supersedes。
- 市场/频率变化：必须重新验证日历、标签、成本和正控制，不能继承旧门禁结论。

## 4. 需求

### 功能需求

### Requirement: 显式执行层级与隔离（`FR-001`）

系统应当要求每次运行显式提供 `preview | canonical`，并以存储能力边界阻止 preview 写正式总体、
留出预算或晋级结论；执行层级不得从环境变量或进程全局状态推断。

#### Scenario: preview 越权写入

- GIVEN 一个 preview 运行上下文
- WHEN 代码尝试登记 official population、追加留出预算台账或访问留出
- THEN 操作失败，canonical 台账与留出预算台账均无变化并写入拒绝事件

### Requirement: 方法论递增守卫（`FR-002`）

系统应当在执行因子前校验 label endpoint、per-pair PIT 日历、最大 horizon embargo、train-only fit、
安全 join/forward-fill 与已登记算子能力；新增标签/变换/join/跨 pair 能力时必须有覆盖该能力的守卫。

#### Scenario: 标签结果跨越切分边界

- GIVEN 信号时刻在训练期但 label endpoint 落入验证期
- WHEN 构造切分
- THEN 该观测从训练折 purge，不能按信号时刻保留

### Requirement: 分阶段证据与失败语义（`FR-003`）

系统应当按信号质量、组合转换、成本/容量、时序稳定、执行实现五阶段记录结果；FactorDef 运行
可将尚不适用的后续阶段显式记为 `NOT_APPLICABLE`，不得记为 PASS。必需输入/指标/实现失败时
运行必须 `INCOMPLETE/FAIL`。阶段状态与晋升/成本 verdict 是**两层独立枚举**，不得互相替代：
阶段状态（`PASS`/`FAIL`/`UNDERPOWERED`/`INCOMPLETE`/`NOT_APPLICABLE`）只描述单阶段结果，
`promising`/`dead` 等晋升与成本裁决只在 cohort 级产出（完整术语表由 design §3.3 冻结，本 Feature 各 scenario 与 AC-003/AC-004 引用同一份）。

#### Scenario: 必需估计器异常

- GIVEN canonical 运行的 BH-FDR 或 block bootstrap 估计器报错
- WHEN 汇总 verdict
- THEN stage 状态不得为 `PASS` 且 `promotion_verdict` 不得为 `promising`，失败记录包含 stage/owner/mechanism 与原始异常引用

### Requirement: 统计与试验总体（`FR-004`）

系统应当在预注册 cohort 内计入所有受评表达式（含拒绝者），至少计算 HAC/稳健 IC 摘要、
BH-FDR、block bootstrap、不确定性区间、按有效独立数校正的 deflated significance 和最小
track-record length；阈值和选择阶段在看结果前冻结。成员先登记不可变原始证据，只有全部承诺
成员进入终态后才能统一 finalize cohort、计算 cohort 级校正并产生可晋级结论。

#### Scenario: 拒绝者仍进入分母

- GIVEN cohort 内一个候选在成本门被拒绝
- WHEN 计算 cohort 多重检验与漏斗
- THEN 该候选仍计入试验总数，多成员 cohort 的批量分母完整、诊断性重算不重复计数

### Requirement: 成本、容量与时间稳定性（`FR-005`）

系统应当输出零成本/maker/taker 三档、资金费率、breakeven cost、换手、持有期与适用的容量代理，
并以 purged/embargoed rolling split 记录选择期到留出的稳定性；成本后不为正时 verdict 为 `dead`。
样本量按三级裁决（ADR-0003「样本量门槛」与 PRD FR3.5）：样本 `<30` 为 `sample_tier=underpowered`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口）；`30~69` 为 `provisional`（最多临时 PASS，仅允许缩减仓位进入 paper 并延长观察，不构成可信判定）；`≈≥69` 为 `trustworthy`（才允许完整成本后 PASS/FAIL 判定并计入北极星判据）。

#### Scenario: 欠功效与临时 PASS 分离

- GIVEN 成本后均为正的三个候选，样本量分别为 25 / 50 / 80 笔
- WHEN canonical 裁决
- THEN 分别得 `sample_tier=underpowered` / `provisional` / `trustworthy`；`provisional` 不得被任何实盘前置引述，`underpowered` 不得记为 PASS

#### Scenario: 高 IC 但成本不存活

- GIVEN 一个 RankIC 达标但 taker 档成本后收益不为正的候选
- WHEN canonical 裁决
- THEN `cost_verdict=cost_negative` 且最终 verdict 为 `dead`

### Requirement: 无前视三层归属与晋级阻断（`FR-007`）

系统应当把 PRD FR3.6 的三层无前视防线显式归属：**L1 = AST 纯度与未来算子门**（因子定义层）由 F007 方法论守卫在评测入口复检并 fail-closed（执行者在 F003 生成侧）；**L2 = 独立逐 K 线重放审计**（策略层）与 **L3 = 信号缓存 merge/join 时间戳与陈旧度对齐**（数据层）的 owner 为 F006/M3，F007 不重复实现。manifest 必须逐层记录状态（`PASS` / `FAIL` / `not_yet_available`）与证据引用，缺失层携带 owner。**L2/L3 未取得通过证据前，任何成员或组合不得晋级 paper**：状态不得记 `PASS`，也不得静默省略。

#### Scenario: 只有 L1 通过时不得晋级

- GIVEN 一个 canonical 成员仅 L1 通过，L2/L3 记 `not_yet_available`（owner=F006）
- WHEN 请求晋级 paper
- THEN 请求被拒绝（阻断点在三层状态校验），拒绝事件含缺失层与 owner

### Requirement: 不可变证据与综合报告（`FR-006`）

系统应当原子发布 `report.json`、`curves.parquet` 和 manifest，并从 canonical ledger 生成版本化
`synthesis_report.json`；综合报告必须包含 cohort 漏斗、有效独立数、五阶段损失、最大约束及
分栏的事实/推断/建议。

#### Scenario: 原子发布失败

- GIVEN 曲线侧车写出或摘要互推校验失败
- WHEN 发布证据批次
- THEN report 不对消费者可见，运行标为 `INCOMPLETE` 且可安全重试

### 数据 / 实体需求

- **DR-001**：`ResearchSnapshot` 应当按 ADR-0007 持久化 cutoff、精确 dataset/version/value-digest 成员、as-of/覆盖语义、symbol-map 与 universe/calendar 摘要；universe 摘要以 **F008** 的内容寻址台账 digest 与 `universe_at(T)` 语义为锚点（`IR-003` 的 `schema_version`），calendar 摘要由本 Feature 拥有的 calendar artifact 导出；缺失或 invalid 成员不得发布。
- **DR-002**：`ExperimentContext` 应当持久化 tier、upstream ID、cohort、规范化规则/窗口/成本配置、research_snapshot_id、code/build digest、seed 与可选 supersedes；`experiment_id` 由这些语义字段（除 tier/supersedes）导出，path、codec、created_at、host、duration 与 file SHA 不参与身份。
- **DR-006**：`UniverseCalendarBinding` 应当把 universe 与 calendar 拆为两个独立 artifact 引用：universe 按 **F008** `IR-002` 的内容寻址台账消费（`lake/_metadata/universes/<digest>.csv`，提供 `universe_at(T)` 语义），calendar 由本 Feature 拥有并规范化保存为内容寻址 JSON（`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`）；ADR-0007 的 `universe_calendar_digest` 由两者 digest 组合导出（不再等于单一 JSON 文件摘要），拆解关系写入 ResearchSnapshot provenance。
- **DR-003**：`ExperimentManifest` 应当关联输入、逐阶段状态、报告、曲线、规则版本和结论；canonical 历史产物只增不改。
- **DR-004**：`CohortLedger` 应当保存预注册试验定义、选择阶段、全部候选和计数；preview 不得出现在 official population。
- **DR-005**：`HoldoutBudgetLedger` 应当以 append-only 台账持久化每次留出评估（`candidate_id`、ISO 周、`experiment_id`、`cohort_id`、`verdict`、`recorded_at`、`execution_tier=canonical`）；只有 canonical capability 可追加，preview 越权写入必须被拒绝并写 `evaluation.gate_rejected`；台账与 manifest 同为可复现要件，不支持事后补记（ADR-0003 留出期使用预算）。

### 事件 / Trace 需求

- **TR-001**：运行状态变化应写 `evaluation.run_state_changed`，包含 experiment_id、tier、from/to、stage、reason 与 evidence refs。
- **TR-002**：preview 越权、方法论失败和必需指标失败应写 `evaluation.gate_rejected`，可按 cohort/object/stage 查询。
- **TR-003**：canonical population 登记应使用 experiment_id 幂等键并引用 manifest ID。

### API / 接口需求

- **IR-001**：CLI 应提供 preview、canonical、finalize-cohort 与 synthesis 四个显式子命令；拒绝缺失 cohort/规则版本的 canonical 请求，也拒绝在成员未收齐时 finalize。
- **IR-002**：canonical 评测只接受已发布 ResearchSnapshot ID 和可解析的 FactorDef/冻结 PortfolioDef 引用；preview 请求 latest 时必须显式提供不可变 symbol-map ref、**F008** universe artifact 引用与 calendar artifact 输入，builder **分别**校验 universe 的 `universe_at(T)` 语义与 calendar schema 后内容寻址冻结并返回 snapshot ID；任何 tier 都不直接接受任意数据库查询，缺失任一 artifact 即失败关闭。
- **IR-003**：机器输出应使用版本化 schema，并返回 experiment_id、状态、verdict、artifact refs 和结构化 failure。

### UX 需求

- **UX-001**：本 Feature 不提供页面；CLI 输出应把 tier、cohort、数据/代码摘要与 `INCOMPLETE` 原因置于摘要首屏。
- **UX-002**：F005 只能读取 F007 产物，不得在前端重算指标或触发门禁。

### 非功能需求

- **NFR-001**：可靠性：canonical 登记与证据发布必须幂等、原子或可检测为未完成，崩溃后不得出现半个 PASS。
- **NFR-002**：可复现：固定 ResearchSnapshot 与其他语义输入跨路径/Parquet 编码重跑得到相同 snapshot/experiment ID 与数值容差内相同报告。
- **NFR-003**：安全：Agent 与 preview 上下文没有 canonical writer、留出读取或晋级能力。
- **NFR-004**：性能：preview 可采样/缩窗但必须显式标注近似；canonical 不因性能压力静默减少门禁或样本。
- **NFR-005**：兼容性：产物路径和 manifest 使用 POSIX 逻辑路径/URI，Windows/WSL 物理路径只进 provenance。

## 5. 生命周期与不变量

```text
CREATED -> VALIDATING       身份与输入可解析
VALIDATING -> RUNNING       方法论/PIT/纯度门通过
RUNNING -> EVIDENCE_READY   必需阶段完成且产物原子发布
任意非终态 -> INCOMPLETE   输入、估计器、发布或恢复失败
canonical EVIDENCE_READY -> REGISTERED  cohort/population 幂等登记完成
cohort OPEN -> FINALIZED          全部承诺成员已终态，cohort 级校正与裁决原子发布
preview EVIDENCE_READY -> PREVIEW_DONE  保持隔离，不可晋级
```

不变量：

- preview 永远不能转写为 canonical；晋级意图必须以冻结上下文重新执行 canonical。
- 任何 PASS/promising 都必须能追到完整 manifest、规则版本、data value digest 和 code/build digest。
- canonical 成员登记不等于晋级；cohort 未 FINALIZED 时不得产生可晋级结论。
- 必需门被 skip、warning 或 null 时，运行不能进入 `EVIDENCE_READY/REGISTERED`。
- 历史证据不覆盖；变化产生新 ID，并通过 supersedes 表达替代关系。
- 无前视三层归属显式：L1 由本 Feature 方法论守卫 fail-closed 执行；L2/L3 owner 为 F006/M3，非 `PASS` 前不得晋级 paper，缺失层记 `not_yet_available` 并携带 owner（`FR-007`）。

## 6. 成功与验收

### 成功标准

- **SC-001**：正控制、白噪声控制和故意泄漏控制分别得到完整证据、统计拒绝/弱证据和方法论拒绝。
- **SC-002**：preview/canonical 隔离、canonical 幂等与 cohort finalize 经并发/故障注入验证，official population 无污染或重复，未收齐成员不能晋级。
- **SC-003**：同 ResearchSnapshot 语义跨路径/codec 重跑身份稳定；任一成员版本/value digest、cutoff、映射/日历摘要或其他实验语义变化都会生成新 ID。
- **SC-004**：canonical cohort 可确定性重建 synthesis，拒绝者进入分母，标量与曲线侧车可互推。

### 验收清单

- [ ] **AC-001** (`FR-001`, `DR-004`, `DR-005`, `NFR-003`): preview 越权被拒绝，正式台账与留出预算台账零变化（含「台账零行」正向断言与 preview 越权写入留出预算的负例）
- [ ] **AC-002** (`FR-002`): label endpoint、per-pair 日历、最大 horizon、train-only fit 与 future-aware 算子负例全部被拦截
- [ ] **AC-003** (`FR-003`, `FR-004`): 必需统计失败关闭；拒绝者仍进入试验分母，成员未收齐时 cohort 不能 finalize 或晋级；**多成员 cohort 批量夹具**上被拒成员仍在分母、诊断性重算不重复计数
- [ ] **AC-004** (`FR-005`): 三档成本、breakeven/换手/持有期和 rolling stability 完整，成本不存活者为 dead；样本量三级裁决正确（`<30` → `underpowered` 不判 PASS/FAIL、`30~69` → `provisional` 仅缩减仓位 paper、`≈≥69` → `trustworthy` 才可完整判定）
- [ ] **AC-005** (`FR-006`, `DR-003`, `NFR-001`): report/curves/manifest 原子发布，失败注入不产生半个 PASS
- [ ] **AC-006** (`DR-001`, `DR-002`, `DR-006`, `NFR-002`): ResearchSnapshot 跨路径/codec 身份稳定；动态 latest 先冻结；成员/cutoff/映射日历或实验语义变化使相应身份变化并可 supersede；universe（F008 digest + `universe_at(T)`）与 calendar 两个 artifact 引用分别校验，缺失或 digest 不符即拒绝发布
- [ ] **AC-007** (`FR-006`, `UX-002`): synthesis 只消费 canonical，输出五阶段漏斗且事实/推断/建议分栏
- [ ] **AC-008** (`IR-001`, `IR-002`, `IR-003`): CLI/schema 契约能拒绝非法 canonical 请求并返回结构化失败
- [ ] **AC-009** (`FR-007`): 三层无前视状态逐层进入 manifest；L1 fail-closed 生效（未来算子负例被拒）；L2/L3 非 `PASS` 时阻断晋级且拒绝事件携带缺失层与 owner；任何情况下不得把缺失层记为 PASS 或静默省略
- [ ] **AC-011** (`FR-006`, `NFR-004`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：身份规范化、时间切分、统计估计器、成本公式、状态机与 schema。
- 集成测试：F002 fixture → FactorDef → report/curves/manifest/ledger/synthesis 全链路。
- 变异/属性测试：故意改变 future-fill、embargo、fit 范围、preview writer、codec 与异常吞噬逻辑，确认门禁变红。
- 真实环境验证：在**执行机**的不可变 crypto 快照上以 `ALPHAMILL_INTEGRATION=1` 独立取证——独立命令 `tests/integration/test_f007_controls_real.py`，绑定 snapshot ID 与 `value_digest`，记录 hostname 与 `device=cpu`，证据落 `reports/f007/real_env/<run_id>/`；不得与 fixture 控制（`tests/integration/test_f007_controls.py`）共用同一命令或同一夹具充当真实环境证据（SOP §3）。

### 依赖

- 上游 Feature / Contract：F002 有效 `(dataset, DataVersion, value_digest)` reader；ADR-0007 ResearchSnapshot；FactorDef schema。
- 下游消费者：F005 研究控制台、FR4 组合构建、F006 生命周期/运营入口。
- 外部 / 环境依赖：统计基础库必须 pin；不依赖 ml4t 教学仓或 `ml4t-diagnostic` 作为运行时硬门。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 四平面是否变化 | 不变；两条横向 seam | 避免复制台账与所有权 | ADR-0006 |
| DML/PBO/Reality Check | 可选诊断，不做通用硬门 | 前提敏感且非所有候选适用 | 数据与用途成熟后独立立项 |
| PortfolioDef 五阶段 | 协议预留；组合构建/执行阶段可为 NOT_APPLICABLE | F007 先完成 M1 因子证据切片 | M3 Feature 补齐，不能伪记 PASS |
| 统计实现风险 | 自研最小协议 + 正/负控制 + 第二实现抽查 | 门禁不能依赖会 warning 降级的黑盒 | ADR-0003；抽查载体 T025（time-box 1 周、容差与证据路径入 tasks） |
| 无前视 L2/L3 归属 | F007 不实现审计器；owner=F006/M3，晋级前以三层状态 + fail-closed 门阻断 | 逐 K 线重放与信号缓存对齐属策略/数据层，重复实现会产生第二真相源 | F006 落地后 F007 只接线其审计证据 |

## 8. 待确认问题

无
