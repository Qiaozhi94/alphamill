---
kind: feature
id: F002
version: "0.2"
status: draft
gate_version: 1
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-12
---

# F002：数据桥——Parquet 湖导出与 DuckDB 研究取数层

> Owner: Georg | Target: v0.2.0

## 0. 来源与意图

- **PRD 来源**:`docs/alphamill-prd.md` FR1.2(不可变快照)、FR1.3(研究只读边界)、FR1.4(双口径与时间语义)、FR1.6(灾备,湖部分);里程碑 M1
- **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
- **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/宇宙扩容)、§2.2(symbol_map.csv M1 出口标准)
- **上游决策**:无新 ADR;导出设计以 `docs/alphamill-integration.md` §1.2 为唯一权威
- **基座来源**:F001(已 done)——TimescaleDB 631 万行数据、`lake/` NAS 备份目录位、`backup-nas.sh` 分块校验通道
- **功能类型**:backend / data-model
- **规格模式**:full
- **变更类型**:ADDED
- **一句话意图**:把 TimescaleDB 的修订态数据按日导出为带 manifest 的不可变 Parquet 快照,并提供拒绝失效版本的 DuckDB 研究取数入口,使挖掘/评测/回测从同一版数据算出同一版结果。

## 1. 问题、目标与非目标

### 问题

研究/回测目前若直读 TimescaleDB,读的是会被回补与修订的"活"数据:同一实验今天与明天跑出的结果不可比,也无法回答"当时的证据基于哪版数据"——这直接违反 PRD 数据红线(只读湖快照)与 FR7.2 不可变证据链的前提。F001 已交付 631 万行联机库与 NAS 灾备,但 lake/ 仍是空目录位,研究取数层不存在。

### 目标

- `lake/` 内出现分区化 Parquet 快照(ohlcv_1m、衍生品三表、signals_log),每次导出附 manifest(dataset/rows/data_version/对账状态);
- 导出与 TimescaleDB 逐 dataset 对账(行数 + 时间边界 + `row_digest`,口径见 design §3 唯一权威定义),不一致的 data_version 被标记 `invalid`;
- 提供统一 DuckDB 取数模块:按 dataset+data_version 查询,**拒绝读取 invalid 快照**;
- `symbol_map.csv` 落地(湖内 pair ↔ Freqtrade pair,UTC 锁定),满足集成文档 §2.2 的 M1 出口标准;
- 每日 **02:00** 增量导出 + 周日 04:00 全量校验进入调度;`backup-nas.sh` 的 `lake/` 目录位激活。

### 非目标

- 宇宙扩容到 30~50 对(FR1.5,后续 feature);
- 评测台/门禁泛化(FR3,M1 另立 feature);
- Vibe-Trading 适配器(FR3.7/FR6.4 可选项);
- TimescaleDB 阶段 B(纯 Parquet 化,撤库)——另立评估;
- 因子计算、信号缓存对齐校验(F002 只保证数据层;信号缓存消费属 M1 后续 feature)。

## 2. 用户场景

### US-001:研究员的可复现取数(Priority: P1)

作为 `量化研究员`,我希望 `用 DuckDB 按 dataset+data_version 读取 Parquet 快照`,以便 `同一版数据永远算出同一版结果,且不会误读失效快照`。

**为什么是这个优先级**:这是 PRD 数据红线的实现载体,是 M1 评测台与 M2 因子工厂的一切取数前提。

**独立测试**:跑一次导出后,用 DuckDB 模块查询某 dataset 某日期范围的行数,与 TimescaleDB 同口径行数一致;人为将 manifest 标记 `invalid` 后,取数模块抛错拒绝返回数据。

**验收场景**:

1. Given `TimescaleDB 有 6 个 binance 交易对的 ohlcv_1m 数据`,when `执行一次导出`,then `lake/ohlcv_1m/exchange=binance/pair=<pair>/date=<date>.parquet 按日分区生成`,`lake/_manifests/ohlcv_1m/<data_version>.json` 记录 rows/data_version/对账状态,且 DuckDB 取数模块返回的行数与库内一致。
2. Given `某 data_version 的 manifest 被标记 invalid(如对账失败)`,when `取数模块以该版本查询`,then `抛出明确异常拒绝读取,不返回任何行`。

### US-002:数据修订的可审计演进(Priority: P2)

作为 `量化研究员`,我希望 `TimescaleDB 历史数据被回补/修订时 data_version 递增且旧快照保留`,以便 `在途实验可审计地感知数据漂移,而不被静默污染`。

**为什么是这个优先级**:point-in-time 政策是评测公信力的前提(D014);没有版本演进语义,快照不可变就只是口号。

**独立测试**:周日全量校验模式检测到库内数据相对既有快照存在差异时,生成新 data_version 的 manifest,登记修订分区差异清单;旧版本文件原样保留且仍可读取。

**验收场景**:

1. Given `湖内存在 data_version=v1 的快照`,when `库内某历史分区数据被修订并执行全量校验导出`,then `生成 v2 快照与 manifest,v2 的 manifest 相对 v1 登记修订分区清单,v1 文件与 manifest 原样保留`。

## 3. 范围与边界

### 范围内

- `src/alphamill/data_bridge/exporter.py`:导出器(TimescaleDB → 分区 Parquet,增量/全量两种模式);
- manifest 生成与读写(架构 §4.4 JSON 契约 + `status: valid|invalid` + 修订差异清单字段);
- 导出后对账(逐分区 行数 + 时间边界 + `row_digest` vs TimescaleDB,同一 REPEATABLE READ 快照内);
- `src/alphamill/data_bridge/reader.py`:DuckDB 只读取数模块(dataset+data_version+时间范围查询,invalid 拒绝);
- `symbol_map.csv` 生成与加载(湖内 pair ↔ Freqtrade pair);
- 调度接入:每日 02:00 增量、周日 04:00 全量校验(systemd user timer,沿用 F001 模式);
- `backup-nas.sh` 的 `lake/` 目录位激活(湖与 manifest 进入每日 NAS 同步)。

### 范围外

- 宇宙扩容 30~50 对与新 pair 质量流程(FR1.5);
- 评测台/门禁/信号缓存对齐(FR3 与 M1 后续 feature);
- Vibe-Trading local loader 对接(集成 §二,可选time-box);
- 湖内数据的因子计算或口径加工(FR1.4 双口径在本期仅落列语义与映射,不做复权计算——crypto 无复权);
- 撤除 TimescaleDB(阶段 B)。

- **Kronos 真实推理容器化**(compose 可选 profile `kronos-real`):F002 只保证 signals_log 的**导出管线**正确,不保证其内容来自真实模型。原 T014 曾挂在 FR-001 名下,但 FR-001 只承诺导出五个 dataset、AC-001 只核对分区与行数,容器化既无对应需求也无验收闭环(F002-Q001),故移出 F002。**载体待 owner 裁决**:①单独立一个上游 Feature;②在 F002 新增独立 FR/AC 并裁定它是否阻塞 F002 done。在裁决前它记录于 `docs/reviews/RETROSPECTIVE.md` 循环 6,不随本feature 收口而消失。

### 边界场景

- 导出进行中 TimescaleDB 仍在写入:导出按 `time < 导出窗口终点` 快照读,窗口终点之前的分区保证完整;跨窗口的实时数据归下一窗口;
- 对账不一致:该 data_version 整体标记 `invalid`,消费端拒绝;修复后以新 data_version 重新导出,不复用污染版本号;
- 磁盘空间:湖按日分区单文件,单 pair 单日 1m 约 1440 行(<200KB),全量重导不产生写放大;
- 导出窗口内某 pair 无新数据:跳过该分区且 manifest 记录 skipped,不算失败。

## 4. 需求

### 功能需求

### Requirement: 每日增量导出与 manifest(`FR-001`,对应 FR1.2)

系统应当把 TimescaleDB 中 ohlcv_1m、derivatives_funding_rates、derivatives_open_interest、derivatives_mark_index_basis、signals_log 五个 dataset 按 `lake/<dataset>/exchange=<ex>/pair=<pair>/date=<YYYY-MM-DD>.parquet` 分区导出,每次导出生成符合架构 §4.4 契约的 manifest(含 rows、data_version、对账状态)。

#### Scenario: 首次全量导出

- GIVEN TimescaleDB 含 6 个 binance 交易对的 1m 数据
- WHEN 执行全量导出
- THEN 五个 dataset 的分区 Parquet 生成,manifest 记录 rows/data_version/对账=valid,且 DuckDB 可读

### Requirement: 导出对账与失效语义(`FR-002`,对应 FR1.2/FR1.3)

导出完成后必须逐分区与 TimescaleDB 对账(行数 + 时间边界 + `row_digest`;口径与规范编码见 design §3,该处为唯一权威定义);导出查询与源侧对账必须共享同一个 REPEATABLE READ 快照。不一致时该 data_version 标记 `invalid`,消费端必须拒绝读取 invalid 快照。

#### Scenario: 对账失败标记失效

- GIVEN 导出过程被中断或数据不一致
- WHEN 对账执行
- THEN 该 data_version manifest 标记 `invalid`,取数模块对该版本的一切查询抛出异常

### Requirement: DuckDB 研究只读取数入口(`FR-003`,对应 FR1.3)

提供统一的 DuckDB 取数模块:输入 dataset、data_version(缺省取最新 valid 版本)、可选时间范围与 pair 过滤,返回 DataFrame;模块内禁止任何写路径。

#### Scenario: 按版本与时间范围取数

- GIVEN 湖内存在有效快照
- WHEN 以 dataset=ohlcv_1m、时间范围查询
- THEN 返回的行数与该版本 manifest 及 TimescaleDB 对账口径一致

### Requirement: symbol 映射与时间语义(`FR-004`,对应 FR1.4)

生成并随湖维护 `symbol_map.csv`(湖内 pair ↔ Freqtrade pair),所有导出数据时间列为 UTC;映射关系由取数模块显式暴露,不依赖隐式约定。

#### Scenario: 映射查询

- GIVEN symbol_map.csv 已生成
- WHEN 以任一侧 pair 查询
- THEN 得到另一侧的显式映射值;全部时间为 UTC

### Requirement: 全量校验与修订版本递增(`FR-005`,对应 FR1.2 修订政策)

周日全量校验模式比对库内数据与既有快照;发现修订时递增 data_version 生成新快照,manifest 登记修订分区差异清单,旧版本原样保留且仍可读取。

#### Scenario: 修订触发新版本

- GIVEN v1 快照存在且库内某历史分区被修订
- WHEN 执行全量校验导出
- THEN 生成 v2,manifest 登记差异分区清单,v1 保留可读

### Requirement: 调度与灾备接入(`FR-006`,对应 FR1.6 湖部分)

每日 **02:00** 增量导出与周日 **04:00** 全量校验进入 systemd user timer 调度(02:00 是排序约束不是偏好:`alphamill-backup.timer` 03:00 起跑且带 10 分钟随机延迟,导出须先完成当日分区才会被同一晚的 NAS 备份带走;集成 §1.2 已同步);`backup-nas.sh` 同步 `lake/` 与 `lake/_manifests/` 到 NAS(激活 F001 预留目录位)。

#### Scenario: 调度运行

- GIVEN 定时器安装
- WHEN 定时触发
- THEN 导出无人工干预完成,失败非零退出并可从 journalctl 定位;NAS 端 lake/ 产物齐全

### 非功能需求

- **NFR-001**:研究取数模块零写路径——对 lake/ 只读;任何写操作只存在于导出器;
- **NFR-002**:可复现——同一 data_version 的快照文件不变(不可变),同版本同查询同结果;
- **NFR-003**:导出全量 631 万行在单机可完成(分钟级),增量导出(单日)秒级到分钟级。

## 5. 生命周期与不变量

不适用独立状态机;核心不变量:

- 快照不可变:已写入的 data_version 分区文件与 manifest 不修改,演进只增新版本;
- invalid 不可逆:标记 invalid 的版本不因后续修复自动变回 valid,修复走新版本;
- 消费端红线:研究/回测禁止直读 TimescaleDB,只允许经取数模块(D4 数据红线的技术落点)。

## 6. 成功与验收

### 成功标准

- **SC-001**:端到端链路成立——一次导出产生分区 Parquet + valid manifest,DuckDB 取数与库内对账一致(US-001);
- **SC-002**:失效语义成立——invalid 版本被取数模块拒绝(US-001 场景 2);
- **SC-003**:修订演进成立——全量校验产生递增版本与差异清单,旧版本保留(US-002);
- **SC-004**:调度与灾备成立——定时器安装且 backup-nas.sh 同步 lake/(FR-006)。

### 验收清单

- [ ] **AC-001** (`FR-001`): 全量导出后五 dataset 分区 Parquet + manifest 齐备,DuckDB 行数与库一致 — tests: `tests/integration/test_f002_export_reconcile.py`
- [ ] **AC-002** (`FR-002`): 对账失败路径——构造不一致后 data_version 标记 invalid 且取数模块拒绝 — tests: `tests/integration/test_f002_export_reconcile.py`
- [ ] **AC-003** (`FR-003`): 取数模块按 dataset+version+时间范围返回正确行集,invalid 拒绝 — tests: `tests/integration/test_f002_reader.py`
- [ ] **AC-004** (`FR-004`): symbol_map.csv 生成、双向映射查询正确、时间列全 UTC — tests: `tests/unit/test_f002_symbol_map.py`
- [ ] **AC-005** (`FR-005`): 修订检测产生 v2+差异清单,v1 保留可读 — tests: `tests/integration/test_f002_revision.py`
- [ ] **AC-006** (`FR-006`): 定时器安装且手动触发导出成功;backup-nas.sh 后 NAS 端 lake/ 产物齐全 — tests: `tests/integration/test_f002_schedule_backup.py`
- [ ] **AC-007** (`FR-005`, `FR-001`): 版本物理隔离——修订产生 v2 后,v1 manifest 列出的每个分区文件字节不变,按 v1 读取返回修订前的行;并发读 v1/v2 不串版 — tests: `tests/integration/test_f002_revision.py`
- [ ] **AC-008** (`FR-003`, `FR-001`): manifest 完整性 fail-closed——删一个分区文件 / 多一个未登记文件 / 改一字节,三种情形读取均抛 ManifestIntegrityError — tests: `tests/integration/test_f002_reader.py`
- [ ] **AC-009** (`FR-004`): signals_log 时间窗无前视——latest_candle < T 但 time > T 的行必须落在 end=T 的结果内;latest_candle > T 但 time < T 的行必须不在 — tests: `tests/integration/test_f002_reader.py`
- [ ] **AC-010** (`FR-002`, `FR-003`): 并发改写不产伪 valid——对账期间对已导出窗口 upsert 历史行,导出仍基于同一快照;结果或为 valid 且与该快照一致,或为 invalid,不出现「对账 ok 但湖内是旧值」 — tests: `tests/integration/test_f002_export_reconcile.py`

## 7. 测试、依赖与决策

### 测试策略

- 集成测试:导出→对账→取数全链路、失效拒绝、修订版本演进、调度+NAS(需要本地 TimescaleDB 在线,CI 跳过);
- 单元测试:symbol_map 生成/加载、manifest 读写、data_version 排序;
- 不做性能压测——631 万行全量导出的实测耗时记入验收证据即可。

### 依赖

- 上游:F001(TimescaleDB 数据与调度模式)、集成文档 §1.2 导出契约、架构 §4.4 manifest 契约;signals_log dataset 的**内容质量**另依赖 Kronos 真实推理容器化——薄壳为 mock 时导出的是 `source=placeholder` 行,导出管线正确不等于内容可用于因子研究;**该项不在 F002 契约内**(见 §3 范围外);
- 下游:M1 评测台(FR3)、FR7 manifest 实验链、Vibe local loader(可选);
- 新增依赖:DuckDB(pyproject 新增 pin,版本范围本地验证后落定);
- 外部/环境:无新外部依赖;lake/ 磁盘空间(全量约 1-2GB)。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| data_version 语义 | 日期版 `vYYYY.MM.DD` 起步,同日重导追加序号(`-r2`);修订递增不复用 | 简单可读;不可变与 invalid 不可逆不变量由测试锁定 | 版本号策略若不敷用,升 ADR |
| 对账口径 | 行数 + 时间边界 + 按主键排序的 SHA-256 `row_digest`(定义见 design §3;两侧由同一 Python 函数计算) | 摘要抗抵消,抓得住行数与极值都不变的内部数值改写;行数抓缺块 | 不一致定位到分区级;**不设降级出口**,性能不可接受时走 spec 修订 |
| 双口径 | 本期仅落列语义(close 原样)与 symbol_map;无复权计算 | crypto 无复权;集成 §1.2 已明确 | FR1.4 完整口径随评测台需求演进 |
| 风险:DuckDB 新依赖引入版本漂移 | pin 范围入 pyproject,check_dep_pins 门禁覆盖 | dev 依赖锁定惯例(C001 教训) | 版本升级走显式改动 |
| 风险:湖与库漂移不可见 | 每次导出强制对账;周日全量校验兜底 | 对账是本 feature 的灵魂(承 F001) | 漂移审计进 manifest 差异清单 |

## 8. 待确认问题

- [x] Q-001:导出哪些 dataset?——ohlcv_1m + 衍生品三表 + signals_log 五个(FR1.2 列举);quality_flags 不单独导出,以 manifest 质量标注继承(集成 §1.2)
- [x] Q-002:F002 放 0.1 还是 0.2?——0.2(0.1 已收口,M1 数据桥是新能力版本)
- [x] Q-003:data_version 全局唯一还是按 dataset 独立递增?——**裁决(2026-09-12, owner):按 dataset 独立递增**。理由:①各 dataset 导出节奏与失败域不同,全局版本号会让单 dataset 对账失败作废整批;②FR7 实验链引用 `dataset + data_version` 二元组,不需要全局时间戳;③「全局时点」可由各 manifest 的 `exported_at` 聚合派生。放弃的好处:没有单一数字能一句话描述「整个湖的状态」——需要时用 exported_at 聚合
