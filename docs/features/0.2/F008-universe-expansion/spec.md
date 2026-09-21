---
kind: feature
id: F008
version: "0.2"
status: developing
branch: feat/F008-universe-expansion
gate_version: 1
related_features: [F001, F002, F003, F007]
topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
doc_kind: spec
created: 2026-09-14
updated: 2026-09-19
---

# F008：宇宙扩容与 point-in-time 宇宙台账

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR1.5（数据质量与扩容、point-in-time 宇宙成员关系）、FR1.1（联机采集与质量标记）、FR1.4（pair/symbol 显式映射）、FR1.7（ResearchSnapshot 的 universe 摘要）；里程碑 M2
- **架构来源**：`docs/alphamill-architecture.md` §三（`data_bridge/` 与 `collector/` 分工）、§4.1.1（横截面只允许在同一 timestamp 的 point-in-time 宇宙内计算）、§7.1（机器边界，回填与导出都在执行机）
- **系统设计 / Research / Contract 来源**：`docs/alphamill-integration.md` §1.3（宇宙扩容三步）、§1.2（导出设计与修订政策）、§2.2（symbol_map 出口标准）
- **上游决策**：ADR-0001（横截面 reward 在 6~12 对上噪声大，扩容是产出质量前提）、ADR-0007（研究快照绑定 universe/calendar 摘要）、ADR-0003（门禁不降级——质量门不得为了赶进度放宽）
- **基座来源**：F001（Binance 回填路线、`historical_backfill.py`、`tools/f001_backfill_report.py` 的完整性口径）、F002（Parquet 湖、`symbol_map`、dataset registry 与 reader）
- **功能类型**：backend / data-model / workflow
- **规格模式**：full
- **变更类型**：MIXED（新增宇宙台账与扩容工作流；修改 data_bridge registry/导出清单）
- **一句话意图**：把研究宇宙从 6 对扩到 40 对（分两批：先前 30 再补 10），并且在扩容的同时把「某个历史时点上到底有哪些 pair 可交易」变成不可变的 point-in-time 台账，让横截面研究既有足够样本，又不吃幸存者偏差。

## 1. 问题、目标与非目标

### 问题

湖内当前只有 6 个交易对。这带来两个独立的问题：

**样本太少**——AlphaGen 的奖励是对协同池的增量 IC 贡献，而 IC 是横截面统计量；每个时间截面只有 6 个样本算 rank 相关，噪声大到 RL 很可能在学噪声。ADR-0001 已把"扩容与对接并行"写成产出质量前提，`F003` 的 Q-001 也据此裁决为并行。

**没有 point-in-time 宇宙**——今天的"宇宙"是库内 `DISTINCT symbol` 的隐式结果，只反映**现在**有哪些 pair，不回答"2025-03-01 那天有哪些 pair 可交易"。用当前成员表回填历史就是幸存者偏差：退市的、后来才上市的 pair 会被错误地当成全程存在。

**本 feature 消除成员区间偏差，不消除成员选取偏差**——目标宇宙的 40 对按**冻结时点**的滚动 90 天成交额排名选出，历史截面里因此会出现「当时不在前 40、今天才在」的 pair。彻底消除需要按每个历史时点重算全市场排名，依赖全市场（而非这 40 对）的历史成交额，不在 M2 范围；台账只追加的结构天然支持后续升级为逐期重算。架构 §4.1.1 明确要求横截面算子只在同一 timestamp 的 point-in-time 宇宙内计算，`F007` 的 ResearchSnapshot 也要绑定 universe 摘要——这两处现在都没有可消费的真相源。

### 目标

- 按可复现的筛选口径（交易所、流动性、上线时长）产出候选清单，经人工确认冻结为**目标宇宙**，口径与快照时间入档；
- 约 4200 万行历史数据分两批回填完成（批 1 = 成交额前 30 含现有 6 对，批 2 = 第 31–40），限速不触发交易所封禁，可中断可续跑，进度与失败可见；
- 新 pair 必须通过质量门（缺失率、重复、未闭合 K 线、跨周期对账）才进导出清单，不过门的隔离并记原因；
- 湖内出现只追加的 `universe_membership` 台账，任一历史时点可还原当时的宇宙成员，供 `F003` 的 PIT 掩码与 `F007` 的 ResearchSnapshot 直接消费。

### 非目标

- 本 feature 不做因子生成、评测与门禁——它只交付数据与宇宙台账；
- 本 feature 不改 `F002` 已冻结的导出、对账与 manifest 语义，只按同一套契约新增一个 dataset 并扩大 pair 集合；
- 本 feature 不承诺把宇宙扩到 50 对以上，也不做多交易所聚合（当前只有 Binance，见 §3 范围外）；
- 本 feature 不做实时上下架监听——成员变化按批处理周期发现即可；
- 本 feature 不做逐期重算排名的 PIT 宇宙构造（消除成员选取前视）——见 §1 问题与 `NFR-003` 的已知残余。

## 2. 用户场景

### US-001：产出可复核的目标宇宙（Priority: P1）

作为项目所有者，我希望按明确口径筛出 40 个候选 pair 并人工确认后冻结，以便后续所有回填、导出与研究都指向同一个有据可查的宇宙定义。

**为什么是这个优先级**：回填要花 1~2 周 wall-clock，选错宇宙的代价极高；先冻结定义才谈得上后面的一切。

**独立测试**：对固定的交易所快照数据跑筛选，验证同一口径与同一快照得到同一候选清单与同一 `universe_id`。

**验收场景**：

1. Given 筛选口径（交易所、市场类型、成交额排名窗口与名次、上线天数下限、排除规则），when 执行发现，then 产出候选清单并记录口径与快照时间，可复现。
2. Given 候选清单未经人工确认，when 请求启动回填，then 请求被拒绝——未冻结的宇宙不得驱动长跑任务。
3. Given 已冻结的宇宙定义，when 成员发生增删，then 产生新版本并留痕变更原因，旧版本不可改写。

### US-002：分批回填不被交易所打断（Priority: P1）

作为项目所有者，我希望约 4200 万行的回填能限速、能断点续跑、能看到进度，以便这件 1~2 周的事不会因为一次中断就从头再来。

**为什么是这个优先级**：这是本 feature 里唯一的长跑工作流，也是唯一会被外部（交易所限流）打断的环节。

**独立测试**：对单个 pair 的窗口跑回填，人为中断后重跑，验证不重复写入、从断点继续、行数与预期一致。

**验收场景**：

1. Given 回填进行到一半被中断，when 重跑同一任务，then 从断点继续且不产生重复行。
2. Given 交易所返回限流错误，when 回填遇到该错误，then 退避重试而不是放弃或加速，且重试次数有上限。
3. Given 回填任一 pair 失败，when 查看运行记录，then 该 pair 的失败原因与已完成进度可见，其他 pair 不受影响。

### US-003：新 pair 必须过质量门才准入（Priority: P1）

作为研究员，我希望只有通过完整性校验的 pair 才进导出清单，以便湖里不会混入缺口大、未闭合或跨周期对不上的数据。

**为什么是这个优先级**：ADR-0003 的门禁不降级在数据面的对应物；脏数据一旦进湖，后面所有证据都被污染。

**独立测试**：构造一个缺失率超阈值和一个未闭合 K 线的 fixture，验证两者都被拦在导出清单之外并各自记录原因码。

**验收场景**：

1. Given 一个缺失率超过阈值的 pair，when 执行质量门，then 该 pair 不进导出清单且原因码为缺失率超限。
2. Given 一个 1m 聚合与连续聚合对不上的 pair，when 执行质量门，then 判定失败，不允许以"差得不多"放行。
3. Given 一个通过全部检查的 pair，when 执行质量门，then 写入准入记录（ACTIVE）并进入导出清单；台账区间由该 pair 的上市/退市事实决定，不因准入而改写。

### US-004：任一历史时点可还原当时宇宙（Priority: P2）

作为研究员，我希望查询任意时刻的宇宙成员集合，以便横截面因子与评测不吃幸存者偏差。

**为什么是这个优先级**：它依赖前三个场景产出的数据与台账，但是 `F003` 横截面掩码与 `F007` ResearchSnapshot 的直接前置。

**独立测试**：构造含上市、退市与中途进出的成员 fixture，对若干时点查询成员集合，逐一比对期望值。

**验收场景**：

1. Given 某 pair 于 T1 上市、T2 退市，when 查询 T0（<T1）、T1.5、T3（>T2）的宇宙，then 该 pair 只出现在 T1.5 的结果里。
2. Given 台账已发布，when 尝试修改历史区间，then 操作被拒绝——台账只追加。
3. Given 某 pair 因流动性不足退出目标宇宙，when 查询其历史区间，then 历史数据仍在湖内且台账记录退出时间与原因，不做删除。

## 3. 范围与边界

### 范围内

- 宇宙发现与筛选口径（Binance USDⓈ-M **加密**永续；滚动 90 天日均 USDT 成交额**排名前 40** + 上线 >180 天 + 排除稳定币对/杠杆代币/指数篮子类合约/代币化 TradFi + **数据可达性前置**——候选须能被研究数据路线（现货 `ohlcv_1m`）取到数）；
- 目标宇宙的人工确认冻结、版本化与变更留痕；
- 分批历史回填编排：限速、退避重试、断点续跑、幂等、进度与失败可见；
- 新 pair 质量门：复用 `tools/f001_backfill_report.py` 的完整性口径（缺失率、边界闭合、连续聚合与 1m 基表按桶重算一致）并参数化到多 pair；
- `universe_membership` 只追加台账（联机库）与 `universe_at(T)` 查询；以 canonical JSON 发布为**内容寻址 artifact** 到湖（最小 PIT 投影，schema 见 `IR-002`；ADR-0007 与 `F007` IR-002 都按 artifact 定义它）；
- 导出清单与 `symbol_map` 的联动：过门的 pair 才进导出，映射 digest 变化可追溯。

### 范围外

- 多交易所聚合与跨所 symbol 归一 → 当前数据路线只有 Binance（F001 裁决），留给后续；
- 现货以外的新市场类型（期权等）→ 不在 M2 范围；
- 实时上下架监听与自动扩缩容 → 成员变化按批处理周期发现即可；
- 因子、评测、门禁与组合 → `F003` / `F007` / M3；
- 修改 `F002` 已冻结的 manifest / 对账 / 修订语义 → 只新增 dataset，不动既有契约。

### 边界场景

- 候选清单未经人工确认就请求回填：拒绝启动，避免 1~2 周的长跑指向未冻结的定义。
- 回填中途交易所限流：退避重试且有上限，绝不提速绕过；超上限则该 pair 标失败并保留已完成进度。
- 新 pair 只有部分历史（上线晚于回填窗口起点）：这是合法状态，不算缺失——缺失率按该 pair 的**实际可得窗口**计算，并在台账记录真实上市时间。
- pair **退市**：历史数据保留、台账追加 `valid_to`（`reason=delisted`）、导出清单移除；**不删数据**（删了就制造幸存者偏差）。
- pair **跌出流动性阈值但仍在交易**：它仍可交易，台账区间不动；只在下一版 `UniverseDef` 中落选并移出导出清单——把它写成台账退出会污染 `universe_at(T)` 的可交易期语义。
- 质量门失败的 pair：隔离并记原因码，可在修复后重跑门禁，但不得手工塞进导出清单。
- 扩容后单次导出耗时与磁盘占用显著上升：属预期，必须实测记录（F002 实测 6 对全量 3m48s、631 万行），不得以"跑得动"含糊带过。

## 4. 需求

### 功能需求

### Requirement: 宇宙发现与筛选口径（`FR-001`）

系统应当按显式口径从交易所公开数据产出候选 pair 清单，并记录口径、数据快照时间与每个候选的筛选指标；同一口径与同一快照应当得到同一候选清单。口径由五部分组成：交易所与市场类型（**排名市场**：Binance USDⓈ-M **加密**永续，`underlyingType=COIN`）；**按滚动窗口日均成交额排名取前 N**（不使用绝对金额阈值）；上线天数下限；排除规则（稳定币对、杠杆代币、指数/篮子类合约、**代币化 TradFi**——股票/商品类 `TRADIFI_PERPETUAL`）；**数据可达性前置**——候选必须在研究数据路线（`ohlcv_1m` 的现货命名空间）有对应市场，只有永续、取不到数的标的不得进入目标宇宙（`1000X` 缩放命名按同标的映射到现货 `X`，不跨标的猜测）。

#### Scenario: 口径可复现

- GIVEN 一份固定的交易所快照数据与一组筛选口径
- WHEN 两次执行发现
- THEN 候选清单与 `universe_id` 完全一致

#### Scenario: 排名法不受市场周期影响规模

- GIVEN 全市场成交额整体放大或缩小
- WHEN 按同一排名口径执行发现
- THEN 候选数量仍为 N，不随行情周期漂移

#### Scenario: 结构性重复标的被排除

- GIVEN 候选中含稳定币对、杠杆代币或指数/篮子类合约
- WHEN 执行发现
- THEN 这些标的被排除并记录排除原因

### Requirement: 目标宇宙冻结与变更留痕（`FR-002`）

系统应当要求人工确认后才能把候选清单冻结为目标宇宙；冻结后的定义不可原地修改，成员增删必须产生新版本并记录变更原因。

#### Scenario: 未冻结不得驱动长跑

- GIVEN 一份尚未冻结的候选清单
- WHEN 请求启动回填
- THEN 请求以非零退出被拒绝，并提示需要先冻结

### Requirement: 分批回填（`FR-003`）

系统应当分批回填目标宇宙的历史数据，遵守交易所限速并在限流错误上退避重试（重试次数有上限）；回填应当幂等、可中断、可从断点续跑，且逐 pair 的进度与失败原因可查。系统应当在启动期校验执行机磁盘余量，不足以覆盖本批预估写入量时以非零退出拒绝——避免跑到一半写满盘。

#### Scenario: 中断后续跑

- GIVEN 回填在某 pair 的中途被中断
- WHEN 重跑同一任务
- THEN 从断点继续、不写重复行，最终行数与预期一致

#### Scenario: 限流退避

- GIVEN 交易所返回限流错误
- WHEN 回填遇到该错误
- THEN 按退避策略重试且不超过上限，绝不提高请求速率

### Requirement: 新 pair 质量门（`FR-004`）

系统应当对每个新 pair 执行完整性校验——缺失率（按该 pair 实际可得窗口计算）、时间边界闭合、重复主键（同一 `(exchange, symbol, time)` 出现多行）、1m 基表与连续聚合按桶重算一致——全部通过才允许进入导出清单；任一项失败即隔离并记录原因码，不得静默放行或放宽阈值。参考源表 `ohlcv_1m` 的主键 `(exchange, symbol, time)` 使重复在源侧结构性不可发生，该检查防的是写入/导入路径异常，因此其检测路径必须由测试真实触发（fixture 载体见 `AC-005`），不得写成恒真的空转断言。

#### Scenario: 跨周期对不上

- GIVEN 某 pair 的连续聚合行数与 1m 基表按桶重算不一致
- WHEN 执行质量门
- THEN 判定失败，该 pair 不进导出清单

### Requirement: point-in-time 宇宙成员台账（`FR-005`）

系统应当维护只追加的宇宙成员台账，每条记录带生效区间与进出原因；**生效区间表达标的的可交易期**（`valid_from` = 真实上市时间，`valid_to` = 退市时间），不表达准入时点。系统应当提供 `universe_at(T)` 查询，返回 T 时刻可交易的成员集合。历史区间一经发布不得修改。

#### Scenario: 历史时点还原

- GIVEN 某 pair 于 T1 进入宇宙、T2 退出
- WHEN 查询 T0(<T1)、T1.5、T3(>T2) 的宇宙成员
- THEN 该 pair 只出现在 T1.5 的结果中

#### Scenario: 台账不可改写

- GIVEN 已发布的成员区间
- WHEN 尝试原地修改
- THEN 操作被拒绝，变更只能以追加新区间表达

### Requirement: 导出清单与湖内 artifact 联动（`FR-006`）

当 pair 通过质量门时，系统应当把它纳入 `F002` 的导出清单——**导出清单定义为「台账中在本次导出窗口终点（`window_end`）可交易 且 质量门判定为 ACTIVE」的 pair 集合**（无独立实体，由台账与判定记录联合导出），由导出侧在 pair 选择处按该集合过滤实现（按被导出 dataset 的 `market_type` 取命名空间交集），不改 `F002` 的 manifest / 对账 / 修订与失效语义；`symbol_map` 保持全量（回答「库里有什么」），与导出清单（回答「研究能用什么」）**允许不等**，回填写库即让 `symbol_map` 产生新 digest 属预期行为；宇宙台账应当以 canonical JSON 发布为内容寻址 artifact（digest 为 canonical 字节的 SHA-256 并带 `sha256:` 前缀，同 digest 文件必须逐字节一致），供 ResearchSnapshot 按显式 digest 引用。`symbol_map` 因新 pair 产生新 digest 时，旧 digest 应当仍可读取。

#### Scenario: artifact 内容寻址

- GIVEN 台账内容未变
- WHEN 两次发布
- THEN 得到同一 digest 且文件逐字节一致；内容变化则产生新 digest，旧 digest 仍可按引用读取

### 数据 / 实体需求

- **DR-001**：`UniverseDef` 应当持久化 `universe_id`（内容寻址）、筛选口径（`turnover_lookback_days`、`turnover_rank_top_n`、`min_listed_days`、`exclude_rules`）、交易所数据快照时间、候选清单与逐候选筛选指标（含排除者与排除原因）、冻结时间与冻结人。
- **DR-002**：`universe_membership` 应当以 `(exchange, market_type, db_symbol, lake_pair, valid_from, valid_to, reason, universe_id, ingested_at)` 表达成员区间（`ingested_at` 为采集时间，支撑 bitemporal 的「何时知道的」审计）；`reason` 取值限于可交易期事实——`listed` / `delisted` / `initial_seed`，准入与隔离原因码不进台账（见 `DR-004`）；`valid_to` 为空表示当前有效；**只追加，历史区间不可改写**。联机库持有可查询的真相源，湖内持有其内容寻址快照 artifact（只含 `lake_pair` / `valid_from` / `valid_to` 的最小 PIT 投影，见 `IR-002`）。
- **DR-003**：`BackfillRun` 应当记录 `schema_version`（`IR-003`）、目标 pair 集合、窗口、限速参数、逐 pair 进度与行数、重试与失败原因、断点位置、起止时间与 hostname。
- **DR-004**：质量门结果应当持久化为逐 pair 的判定记录（各项指标值、阈值、verdict、原因码、判定时间），失败记录与通过记录同样保留；**该记录是准入状态（ACTIVE / QUARANTINED）的真相源**，与台账的可交易期区间相互独立。

### 事件 / Trace 需求

- **TR-001**：成员进出时，系统应当写入 `universe.member_changed`，payload 包含 pair、方向（进/出）、生效时间、原因、`universe_id` 与 `line`——`line` 标明这是台账可交易期变更（`tradability`，原因取 `listed`/`delisted`/`initial_seed`）还是准入状态变更（`admission`，原因取质量门原因码或 `universe_reselect`）。两条线共用一个事件流但必须可区分，否则下游无法还原「当时为什么不在导出清单里」。
- **TR-002**：回填进度与失败应当写入 `backfill.progress` / `backfill.failed`，可按 run 与 pair 查询。

### API / 接口需求

- **IR-001**：CLI 应当提供 `discover`、`freeze`、`backfill`、`gate`、`show` 五个显式子命令；`backfill` 在宇宙未冻结时以非零退出拒绝。
- **IR-002**：宇宙台账 artifact 应当以 **canonical JSON** 发布到 `lake/_metadata/universes/<digest>.json`：顶层键严格等于 `{schema_version, members}`，每个成员的键严格等于 `{lake_pair, valid_from, valid_to}`（`valid_to` 为 `null` 表示当前有效，时间为 UTC ISO-8601），多一个键即判非法；`members` 按 `(lake_pair, valid_from)` 排序，对象键按字典序、UTF-8、无多余空白。digest 为 canonical 字节的 SHA-256 并带 `sha256:` 前缀，前缀参与文件名。artifact 只承载**最小 PIT 投影**——`reason` / `universe_id` / `ingested_at` 等审计列留在联机库，不进 artifact。读取接口应当支持按 digest 加载并提供 `universe_at(T)` 语义查询。
- **IR-003**：台账 artifact 与运行记录应当带 `schema_version`（artifact 为顶层整数字段，参与 canonical 字节因而参与 digest），供 `F003`（横截面 PIT 掩码）与 `F007`（ResearchSnapshot 的 universe 摘要）只读消费；加载方应当校验 `schema_version` 与期望值一致，不一致即拒绝加载。

### 非功能需求

- **NFR-001**：外部配额：回填请求速率应当在交易所限制内，遇限流退避重试；整个回填的 wall-clock 预期 1~2 周属可接受范围（PRD FR1.5）。
- **NFR-002**：可靠性：回填幂等、可中断、可续跑；任一 pair 失败不影响其他 pair 的已完成进度。
- **NFR-003**：正确性：`universe_at(T)` 对任意 T 返回的成员集合不含 T 时尚未上市的 pair，也不排除 T 时在册但之后退市的 pair（无**成员区间**偏差）。**已知残余**：成员**选取**仍基于冻结时点的排名，存在选取前视；消费方（`F003` 候选质量结论、`F007` ResearchSnapshot）必须把「按 `frozen_at` 排名选取的 40 对宇宙」作为结论前提标注，与现行「6 对宇宙前提」同一性质。
- **NFR-004**：机器边界：回填、质量门与导出都在执行机执行（架构 §7.1）；开发机只跑单元与契约测试，运行记录必须标注 hostname。
- **NFR-005**：容量：40 对的数据量约 4200 万行（按 F002 基线外推：约 29,300 个 ohlcv 分区、全量导出约 25min、NAS 约 58,800 个分区文件）；磁盘占用、单次全量导出耗时与 NAS 备份时长必须实测记录，与 6 对基线（631 万行、全量 3m48s、NAS 8,823 文件）对照。**实测显著劣于外推时必须报告，不得默认可接受**——判红阈值：单次全量导出耗时 > 外推值的 1.5 倍（即 > 38min），或磁盘占用 / NAS 分区文件数 > 外推值的 1.3 倍；触线即判不可接受并评估分片导出，不得以「跑得动」放行。

## 5. 生命周期与不变量

```text
pair 状态机：
DISCOVERED  -> BACKFILLING    宇宙已冻结且该 pair 在目标集合内
BACKFILLING -> GATING         回填完成（或达到该 pair 的实际可得窗口）
GATING      -> ACTIVE         质量门全项通过；写入**准入记录**（DR-004），进导出清单
GATING      -> QUARANTINED    任一项失败；记原因码，不进导出清单，可修复后重跑
ACTIVE      -> RETIRED        退市（台账追加 valid_to）或在新版定义中落选（台账不动）；
                              两者都移出导出清单，历史数据一律保留不删

台账区间（独立时间线，不由准入时点决定）：
标的上市  -> 台账追加 valid_from = 真实上市时间（现有 6 对取各自实际数据起点，reason=initial_seed）
标的退市  -> 台账追加 valid_to  = 退市时间，reason=delisted

宇宙定义：
DRAFT -> FROZEN   人工确认
FROZEN -> 新版本  成员增删产生新 universe_id，旧版本只读
```

不变量：

- **台账区间记录标的可交易期，不是准入时点**：`valid_from` = 真实上市时间、`valid_to` = 退市时间；准入与隔离是另一条状态线，落在质量门判定记录（`DR-004`）与导出清单里，不写进台账区间——两者混用会让 `universe_at(T)` 在扩容日之前返回空集，横截面掩码直接失效；
- 台账只追加：历史区间一经发布不可改写，成员变化只能以新区间表达；
- **成员按湖内命名空间成对登记**：同一 `db_symbol` 在研究数据集（`ohlcv_1m`，`spot`）与派生品数据集（`derivatives_*`，`perp`）里是两条 `lake_pair`（`BTC-USDT` / `BTC-USDT-PERP`），台账两条都要有——少一条会让 `F003` 的横截面掩码把对应数据集的分区整片掩掉。口径里的 `market_type=perp` 是**排名市场**（用 USDⓈ-M 永续成交额排名），不是湖内命名空间；
- 退出不等于删除：退市/剔除的 pair 历史数据永久保留——删了就是幸存者偏差；
- 未过质量门的数据不进导出清单，也不能被手工塞进去；
- 未冻结的宇宙定义不得驱动回填等长跑任务；
- 缺失率按 pair 的**实际可得窗口**计算，上线晚不算缺失。

## 6. 成功与验收

### 成功标准

- **SC-001**：宇宙成立——目标宇宙按可复现口径冻结为 40 对，分两批进入回填；
- **SC-002**：数据成立——约 4200 万行回填完成且全部新 pair 通过质量门，导出清单扩大；批 1（前 30）过门即可供 `F003` 使用，不必等批 2；
- **SC-003**：台账成立——`universe_at(T)` 对历史任意时点返回正确成员集合，台账只追加；
- **SC-004**：下游可用——`F003` 的横截面 PIT 掩码与 `F007` 的 ResearchSnapshot universe 摘要都能直接消费本台账。

### 验收清单

- [ ] **AC-001** (`FR-001`, `DR-001`): 同一口径与同一交易所快照两次发现得到相同候选清单与相同 universe_id；逐候选筛选指标入档 — tests: `tests/unit/test_f008_discover.py`
- [ ] **AC-002** (`FR-002`): 未冻结的候选清单驱动回填被非零拒绝；冻结后成员增删产生新版本且旧版本不可改写 — tests: `tests/unit/test_f008_universe_def.py`
- [ ] **AC-003** (`FR-003`, `NFR-002`): 回填中断后重跑从断点继续、不写重复行、行数与预期一致 — tests: `tests/integration/test_f008_backfill.py`
- [ ] **AC-004** (`FR-003`, `NFR-001`): 限流错误触发退避重试且不超过上限，请求速率不因失败而提高 — tests: `tests/unit/test_f008_rate_limit.py`
- [ ] **AC-005** (`FR-004`, `DR-004`): 缺失率超限、未闭合边界、连续聚合对不上、重复主键四类 fixture 均被拦在导出清单外并各记原因码；全项通过者进入清单（重复主键 fixture 以无主键约束的 scratch 源表承载——参考表 `ohlcv_1m` 的主键使重复无法构造，用真实表只能得到恒真的空转断言） — tests: `tests/integration/test_f008_quality_gate.py`
- [ ] **AC-006** (`FR-004`): 上线晚于回填窗口起点的 pair 按实际可得窗口计算缺失率，不被误判为缺失 — tests: `tests/unit/test_f008_quality_gate_window.py`
- [ ] **AC-007** (`FR-005`, `NFR-003`): 含上市/退市/中途进出的 fixture 上，universe_at(T) 在各时点返回正确成员集合 — tests: `tests/unit/test_f008_membership.py`
- [ ] **AC-008** (`FR-005`, `DR-002`): 尝试原地改写已发布历史区间被拒绝；退出记录保留历史数据不删除 — tests: `tests/unit/test_f008_membership.py`
- [ ] **AC-009** (`FR-006`, `IR-002`): 台账 artifact 同内容得同 digest 且逐字节一致、内容变化得新 digest 且旧 digest 仍可读；发布出的 artifact 能被下游 `factor_factory.generators.universe.load_explicit_universe` 按 digest 直接加载通过；新 pair 进入导出清单后 symbol_map 同样满足该性质 — tests: `tests/integration/test_f008_export_integration.py`
- [ ] **AC-010** (`TR-001`, `TR-002`, `DR-003`, `NFR-004`): 成员变更与回填进度/失败事件可按 run 与 pair 查询，且台账可交易期变更与准入状态变更可按 `line` 区分；运行记录标注 hostname — tests: `tests/integration/test_f008_backfill.py`
- [ ] **AC-011** (`NFR-005`): 扩容后实测记录磁盘占用、单次全量导出耗时与 NAS 备份时长，并与 F002 的 6 对基线对照 — tests: `tests/integration/test_f008_capacity_report.py`
- [ ] **AC-012** (`IR-001`, `FR-002`, `FR-003`, `FR-004`): CLI 五个子命令的契约与 `design.md` §4 登记的全部九类启动期拒绝全覆盖——`discover` 口径缺字段 / 交易所不可达，`freeze` 缺 `--confirm` / 候选清单为空，`backfill` 定义未冻结 / 窗口非法 / 磁盘余量不足，`gate` 对回填未完成的 pair 判 `INCOMPLETE`，`show` 定义或 digest 不存在——各自以非零退出并给出可区分的原因 — tests: `tests/unit/test_f008_cli_contract.py`
- [ ] **AC-013** (`IR-003`, `IR-002`, `DR-003`): 台账 artifact 与 `BackfillRun` 均带 `schema_version`；artifact 加载方在 `schema_version` 与期望值不符、顶层或成员出现未知键时拒绝加载并报错，不做宽松忽略 — tests: `tests/unit/test_f008_artifact.py`
- [ ] **AC-014** (`IR-002`, `FR-006`, `NFR-003`): `F007` 的只读消费面（`evaluation/universe_ledger.py`，被 `experiment_store/research_snapshot.py` 调用）按 IR-002 的 canonical JSON 加载同一 digest 的 artifact，`universe_at(T)` 各时点结果与本 feature 台账一致；消费面不再残留任何 `<digest>.csv` 读写路径 — tests: `tests/contract/test_f007_upstream_contracts.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：筛选口径可复现、宇宙冻结与版本化、限速退避策略、缺失率窗口语义、台账区间与 `universe_at(T)`、只追加约束；
- 集成测试：真实库上的分批回填与断点续跑、质量门三类失败 fixture、新 dataset 的导出与 reader 读取、symbol_map digest 联动、容量实测报告；
- 真实环境 / 手动验证：全量回填（1~2 周 wall-clock，owner 主导）与扩容后的首次全量导出、NAS 备份时长实测，全部在执行机执行并记录 hostname；
- 不做的：任何因子/评测相关断言——本 feature 只交付数据与台账。

### 依赖

- 上游 Feature / Contract：F001（Binance 数据路线、`historical_backfill.py`、`tools/f001_backfill_report.py` 完整性口径）；F002（Parquet 湖、dataset registry、`symbol_map`、reader 与 manifest 契约）。
- 下游消费者：`F003`（横截面 PIT 掩码与候选质量结论的宇宙前提）、`F007`（ResearchSnapshot 的 universe/calendar 摘要，ADR-0007）、FR4/M3 组合构建。
  - **`F007` 消费面待迁移（开工前检查 2026-09-19）**：main 上 `evaluation/universe_ledger.py` 仍按已被裁决废弃的 CSV 契约（`<digest>.csv` + 9 列）读写，而 ADR-0007 / 架构 §4.3 / F007 DR-006 与本文 `IR-002` 都已冻结为 canonical JSON——**三份文档一致，代码没跟上**。`SC-004`（F007 可直接消费）要求把该消费面迁到 JSON，由 `AC-014` 验收、`tasks.md` T029 承载；迁移只改消费面与其测试，F007 的 ResearchSnapshot 身份语义（ADR-0007 组合 digest 公式）不变。
- 外部 / 环境依赖：Binance 公开行情与限流策略；执行机的磁盘余量（约 4200 万行）；NAS 备份窗口。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 复用 quant-crypto 的 OKX 发现脚本 | **不复用**：按 Binance USDⓈ-M 永续重写筛选 | F001 事故后数据路线已由 OKX 改为 Binance（`EXCHANGES=binance` 已进 compose/.env/策略配置），OKX 脚本的交易所与接口都不匹配 | 同步修订 `docs/alphamill-integration.md` §1.3 的过期表述 |
| 退市 / 跌出阈值的 pair 怎么处理 | 历史数据永久保留；退市追加台账 `valid_to`，跌出阈值只落选并移出导出清单（台账不动） | 删数据等于制造幸存者偏差；把「落选」写成台账退出会污染可交易期语义 | 两类变更都进 `universe.member_changed`，用 `line` 字段区分（TR-001） |
| 现有 6 对怎么并入 | 直接并入目标宇宙，同样补台账记录（`valid_from` = 实际数据起点） | 不能只给新 pair 建台账——那会让老 pair 在 PIT 查询里"凭空全程存在" | 首次台账发布即覆盖全部成员 |
| 质量门阈值 | 复用 F001 口径：缺失率 ≤1%、边界闭合、连续聚合按桶重算精确一致；阈值可配但默认不放宽 | ADR-0003 门禁不降级；换一套阈值会让新老数据不可比 | 阈值变更须显式改配置并记录理由 |
| 回填是长跑且会被打断 | 幂等 + 断点续跑 + 退避重试 + 逐 pair 进度 | PRD FR1.5 明确这是 1~2 周 wall-clock 的 owner 主导工作流 | 失败 pair 可单独重跑，不影响其他 |
| 扩容后导出与备份变慢 | 属预期；实测记录并与 6 对基线对照，不预设"没问题" | F002 基线：631 万行、全量 3m48s、NAS 8823 个分区文件 | 若超出可接受范围，再评估分片导出 |
| 台账是新 dataset 还是 artifact | **artifact**：内容寻址发布，不进 dataset registry | ADR-0007 与 `F007` IR-002 都把它定义为「universe/calendar artifact」；它是元数据不是时序数据，按日分区没有意义 | ResearchSnapshot 按显式 digest 引用，不解析 latest |
| artifact 用 JSON 还是 CSV | **canonical JSON**（`<digest>.json`），只含最小 PIT 投影 | CSV 放不下 `IR-003` 要求的 `schema_version`（表头注释行 / 每行重复列 / 旁车文件三种承载各有副作用）；`valid_to` 可空在 CSV 里只能靠空串约定，正是 PIT 查询最易出歧义处；calendar artifact 已是 JSON，两者 digest 要组合成 `universe_calendar_digest`，维护两套 canonical 规则无收益 | 裁决 2026-09-19（owner）；同步修订 ADR-0007、架构 §4.3 与 `F007` DR-006 的路径表述；代价是放弃与 `symbol_map` 共用发布原语 |
| 台账区间记什么 | **标的可交易期**（`valid_from`=上市、`valid_to`=退市）；准入状态另记于质量门判定记录 | 若把 `valid_from` 记成准入时点，40 对会全落在扩容当日，`universe_at(2025-xx)` 返回空集，F003 的横截面掩码拿不到任何历史成员 | 裁决 2026-09-19（owner）；§5 状态机与 `DR-002`/`DR-004` 同步拆分 |
| 质量门怎么成为唯一准入通道 | 在**导出侧 pair 选择处**按「可交易 ∩ ACTIVE」过滤；`symbol_map` 保持全量 | F002 的 pair 集合由 `SELECT DISTINCT` 从源表派生，不存在清单实体；「不改 F002 已冻结语义」保护的是 manifest/对账/修订/失效，不含输入端 pair 选择 | 裁决 2026-09-19（owner）；`lake_pairs_map` 加可选准入集合参数，默认 `None` 保持现行为 |
| 成员选取前视怎么处理 | **承认为已知限制**，不在 M2 解决 | 逐期重算需要全市场历史成交额（非这 40 对），是另一个 feature 的数据量；M2 的目标是把截面样本从 6 抬到 40 以压 IC 噪声 | 裁决 2026-09-19（owner）；结论前提须标注「按 frozen_at 排名选取的 40 对宇宙」；台账天然支持后续升级 |
| 目标宇宙规模 | **40 对，分两批回填**（批 1 = 前 30 含现有 6 对，批 2 = 第 31–40） | 截面噪声收益几乎全在前 30（rank 相关标准误 6 对 0.447 → 30 对 0.186 → 40 对 0.160 → 50 对 0.143），而导出耗时与 NAS 文件数线性上涨且**每天都要付**；PRD FR1.5 的 4600 万行估算本身对应约 44 对，40 与之一致 | 分两批让 `F003` 在批 1 过门后即可用，不必等满两周 |
| 为什么不是 50 对 | 不做：50 对全量导出约 32min、NAS 约 73,500 个分区小文件，已踩在 F002「分钟级导出」承诺的边缘，换来的噪声改善只有 11% | 成本永久、收益递减 | 若 T023/T026 实测余量充足且确有需要，按增量加 pair（台账天然支持） |
| 流动性阈值用绝对金额还是排名 | **排名**：滚动 90 天日均成交额前 N | 绝对金额会随市场周期漂移——牛市可能 60 个 pair 过线、熊市只剩十几个，同一口径产出的宇宙规模不可控，与 FR-001 的可复现要求冲突；排名法自适应且直接产出目标规模 | 窗口与名次进 `UniverseDef.criteria`，变更即新 `universe_id` |
| 上线天数要不要求满窗 | **不要求**：维持 >180 天，允许部分历史 | 要求"上线满 2 年"等于只选活过两年的币，这是幸存者偏差的另一张脸——而消除它正是本 feature 的立意；PIT 台账已正确处理"何时进入"，部分历史是合法状态 | 缺失率按实际可得窗口计算（AC-006） |
| 结构性重复标的 | 排除稳定币对、杠杆代币、指数/篮子类合约（如 BTCDOM） | 它们在横截面 rank 里要么是常数噪声，要么与主流币结构性重复，会污染 IC | 排除规则与排除原因一并入档（DR-001） |
| 代币化 TradFi 与「只有永续」的标的 | **排除**：`underlyingType` 非 `COIN`（EQUITY/COMMODITY）按 `tokenized_tradfi` 排除；无现货对应市场的按 `no_spot_market` 排除；`1000X` 只按同标的映射到现货 `X` | 排名用永续流动性，但**研究数据来自现货路线**（`ohlcv_1m` 是 spot）；把取不到数的标的放进宇宙会在台账与导出清单里制造「有成员、无数据」的缺口，而代币化股票/商品与加密资产的横截面驱动因素不同，混进去会污染 IC | 2026-09-21 首次真实发现（T019）实测：40 对里 12 对无现货（含 XAU/XAG/MSTR/CRCL/EWY/INTC），owner 裁决按本行处理 |
| F007 消费面仍是 CSV 契约 | **随本 feature 迁移到 canonical JSON**（`evaluation/universe_ledger.py` 与其契约/集成测试），迁移只改读写面，不动 ResearchSnapshot 身份公式 | 2026-09-19 裁决把 artifact 定为 JSON 后，ADR-0007 / 架构 §4.3 / F007 DR-006 / 本文 IR-002 四份文档都改了，**F007 已 `done` 的代码没改**——文档一致不等于代码一致；不迁移则 `SC-004` 落空，ResearchSnapshot 的 `--universe` 路径直接找不到 artifact | 开工前检查 2026-09-19 发现；`AC-014` 验收、T029 承载；F007 状态保持 `done`（属契约对齐维护，不重开 feature） |

## 8. 待确认问题

- [x] Q-001: 目标宇宙规模与流动性阈值取什么值？ — 决策（2026-09-14, owner）：**规模 40 对，分两批回填**（批 1 = 成交额前 30 含现有 6 对，批 2 = 第 31–40）；**阈值用排名不用绝对金额**——滚动 90 天日均 USDT 成交额排名前 40；**上线天数维持 >180 天，不要求满窗**；并补排除规则（稳定币对、杠杆代币、指数/篮子类合约）。依据与取舍见 §7 决策与风险前五行
- [x] Q-002: 复用 quant-crypto 的 `discover_okx_swap_universe.py` 吗？ — 决策：不复用；F001 事故后数据路线改为 Binance，按 Binance USDⓈ-M 永续重写筛选，并同步修订 `docs/alphamill-integration.md` §1.3 的过期表述
- [x] Q-003: 退市或跌出阈值的 pair 怎么处理？ — 决策：历史数据永久保留；**退市**才追加台账 `valid_to`（`reason=delisted`），**跌出阈值但仍可交易**只在新版定义中落选并移出导出清单、台账区间不动；删除等于制造幸存者偏差（区间/准入两条线的拆分见 §5 不变量）
- [x] Q-004: 现有 6 对要不要补台账？ — 决策：要；首次台账发布必须覆盖全部成员，`valid_from` 取各自实际数据起点，否则老 pair 在 PIT 查询里会"凭空全程存在"
