---
kind: feature
id: F002
version: "0.2"
status: done
gate_version: 1
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-14
---

# F002：数据桥——Parquet 湖导出与 DuckDB 研究取数层

> Owner: Georg | Target: v0.2.0

## 0. 来源与意图

- **PRD 来源**:`docs/alphamill-prd.md` FR1.2(不可变快照)、FR1.3(研究只读边界)、FR1.4(双口径与时间语义)、FR1.6(灾备,湖部分);里程碑 M1
- **架构来源**:`docs/alphamill-architecture.md` §〇(存储三件套分工)、§四 data_bridge(质量门·对账·manifest)、§4.4(Parquet 湖 manifest 契约)
- **系统设计 / Research / Contract 来源**:`docs/alphamill-integration.md` §一(TimescaleDB → Parquet 湖,导出设计/修订政策/宇宙扩容)、§2.2(symbol_map.csv M1 出口标准)
- **上游决策**:ADR-0007(dataset 独立版本与 ResearchSnapshot 绑定);F002 导出细节仍以 `docs/alphamill-integration.md` §1.2 为权威
- **基座来源**:F001(已 done)——TimescaleDB 631 万行数据、`lake/` NAS 备份目录位、`backup-nas.sh` 分块校验通道
- **功能类型**:backend / data-model
- **规格模式**:full
- **变更类型**:ADDED
- **一句话意图**:把 TimescaleDB 的修订态数据按日导出为带 manifest 的不可变 Parquet 快照,并提供拒绝失效版本的 DuckDB 研究取数入口,使挖掘/评测/回测从同一版数据算出同一版结果。

## 1. 问题、目标与非目标

### 问题

研究/回测目前若直读 TimescaleDB,读的是会被回补与修订的"活"数据:同一实验今天与明天跑出的结果不可比,也无法回答"当时的证据基于哪版数据"——这直接违反 PRD 数据红线(只读湖快照)与 FR7.2 不可变证据链的前提。F001 已交付 631 万行联机库与 NAS 灾备,但 lake/ 仍是空目录位,研究取数层不存在。

### 目标

- `lake/` 内出现分区化 Parquet 快照(ohlcv_1m、衍生品三表、signals_log),每次导出附 manifest(dataset/rows/data_version/value_digest/对账状态);
- 导出与 TimescaleDB 逐 dataset 对账(行数 + 时间边界 + `row_digest`,口径见 design §3 唯一权威定义),不一致的 data_version 被标记 `invalid`;
- 提供统一 DuckDB 取数模块:按 dataset+data_version 查询,**拒绝读取 invalid 快照**;
- `symbol_map.csv` 落地并按 digest 保留不可变副本(湖内 pair ↔ Freqtrade pair,UTC 锁定),满足集成文档 §2.2 的 M1 出口标准;
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

1. Given `TimescaleDB 有 6 个 binance 交易对的 ohlcv_1m 数据`,when `执行一次导出`,then `lake/ohlcv_1m/exchange=binance/pair=<pair>/date=<date>.parquet 按日分区生成`,`lake/_manifests/ohlcv_1m/<data_version>.json` 记录 rows/data_version/value_digest/对账状态,且 DuckDB 取数模块返回的行数与库内一致。
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
- `symbol_map.csv` 生成、内容寻址不可变发布与按 digest 加载(湖内 pair ↔ Freqtrade pair);
- 调度接入:每日 02:00 增量、周日 04:00 全量校验(systemd user timer,沿用 F001 模式);
- `backup-nas.sh` 的 `lake/` 目录位激活(湖与 manifest 进入每日 NAS 同步)。

### 范围外

- 宇宙扩容 30~50 对与新 pair 质量流程(FR1.5);
- 评测台/门禁/信号缓存对齐(FR3 与 M1 后续 feature);
- 多 dataset `ResearchSnapshot` 的组合、身份和发布(ADR-0007;由 F007/`experiment_store` 承担);
- Vibe-Trading local loader 对接(集成 §二,可选time-box);
- 湖内数据的因子计算或口径加工(FR1.4 双口径在本期仅落列语义与映射,不做复权计算——crypto 无复权);
- 撤除 TimescaleDB(阶段 B)。

- **Kronos 真实推理容器化**:F002 只保证 signals_log 的**导出管线**正确,不保证其内容来自真实模型。原 T014 曾挂在 FR-001 名下,但 FR-001 只承诺导出五个 dataset、AC-001 只核对分区与行数,容器化既无对应需求也无验收闭环(F002-Q001),故移出 F002。**正式载体已建立**:`docs/features/0.2/F004-kronos-inference-runtime/`(draft,带 FR-001/AC-001)。**F004 不阻塞 F002 done**(2026-09-13 owner 裁决,F004 spec §8 Q-001);代价见 §6 限制说明。

### 边界场景

- 导出进行中 TimescaleDB 仍在写入:导出按 `time < 导出窗口终点` 快照读,窗口终点之前的分区保证完整;跨窗口的实时数据归下一窗口;
- 对账不一致:该 data_version 整体标记 `invalid`,消费端拒绝;修复后以新 data_version 重新导出,不复用污染版本号;
- 磁盘空间:湖按日分区单文件,单 pair 单日 1m 约 1440 行(<200KB),全量重导不产生写放大;
- 导出窗口内某 pair 无新数据:跳过该分区且 manifest 记录 skipped,不算失败。

## 4. 需求

### 功能需求

### Requirement: 每日增量导出与 manifest(`FR-001`,对应 FR1.2)

系统应当把 TimescaleDB 中 ohlcv_1m、derivatives_funding_rates、derivatives_open_interest、derivatives_mark_index_basis、signals_log 五个 dataset 按 `lake/<dataset>/exchange=<ex>/pair=<pair>/date=<YYYY-MM-DD>.parquet` 分区导出,每次导出生成符合架构 §4.4 契约的 manifest(含 rows、data_version、对账状态与按 design §3 计算的 `value_digest`)。

#### Scenario: 首次全量导出

- GIVEN TimescaleDB 含 6 个 binance 交易对的 1m 数据
- WHEN 执行全量导出
- THEN 五个 dataset 的分区 Parquet 生成,manifest 记录 rows/data_version/value_digest/对账=valid,且 DuckDB 可读

### Requirement: 导出对账与失效语义(`FR-002`,对应 FR1.2/FR1.3)

导出完成后必须逐分区与 TimescaleDB 对账(行数 + 时间边界 + `row_digest`;口径与规范编码见 design §3,该处为唯一权威定义);导出查询与源侧对账必须共享同一个 REPEATABLE READ 快照。不一致时该 data_version 标记 `invalid`,消费端必须拒绝读取 invalid 快照。

#### Scenario: 对账失败标记失效

- GIVEN 导出过程被中断或数据不一致
- WHEN 对账执行
- THEN 该 data_version manifest 标记 `invalid`,取数模块对该版本的一切查询抛出异常

### Requirement: DuckDB 研究只读取数入口(`FR-003`,对应 FR1.3)

提供统一的 DuckDB 取数模块:输入 dataset、data_version(缺省取最新 valid 版本)、可选时间范围与 pair 过滤,返回 DataFrame,并显式回报解析后的 dataset/data_version/value_digest;模块内禁止任何写路径。缺省 latest 只供探索/preview 解析,canonical 消费者必须按 ADR-0007 传入已冻结 ResearchSnapshot 中的显式版本。

#### Scenario: 按版本与时间范围取数

- GIVEN 湖内存在有效快照
- WHEN 以 dataset=ohlcv_1m、时间范围查询
- THEN 返回的行数与该版本 manifest 及 TimescaleDB 对账口径一致

### Requirement: symbol 映射与时间语义(`FR-004`,对应 FR1.4)

生成并随湖维护 `symbol_map.csv`(湖内 pair ↔ Freqtrade pair),并按内容摘要保留不可变副本供 ResearchSnapshot 引用；所有导出数据时间列为 UTC,映射关系由取数模块显式暴露,不依赖隐式约定。

#### Scenario: 映射查询

- GIVEN symbol_map.csv 已生成
- WHEN 以任一侧 pair 查询
- THEN 得到另一侧的显式映射值、稳定 symbol_map_digest 与可按 digest 重放的不可变映射;全部时间为 UTC

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
- **NFR-002**:可复现——同一 dataset+data_version 的快照文件不变(不可变),同版本同查询同结果;跨 dataset 可复现性由 ADR-0007 ResearchSnapshot 组合契约负责;
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

- [x] **AC-001** (`FR-001`): 全量导出后五 dataset 分区 Parquet + manifest 齐备,DuckDB 行数与库一致 — tests: `tests/integration/test_f002_export_reconcile.py`
- [x] **AC-002** (`FR-002`): 对账失败路径——构造不一致后 data_version 标记 invalid 且取数模块拒绝 — tests: `tests/integration/test_f002_export_reconcile.py`
- [x] **AC-003** (`FR-003`): 取数模块按 dataset+version+时间范围返回正确行集并回报解析版本/value_digest;invalid 拒绝;显式版本读取不受后来 latest 变化影响 — tests: `tests/integration/test_f002_reader.py`
- [x] **AC-004** (`FR-004`): symbol_map.csv 生成、双向映射查询正确、时间列全 UTC；同内容得到同 symbol_map_digest，内容变化得到新 digest 且旧 digest 仍可读取 — tests: `tests/unit/test_f002_symbol_map.py`
- [x] **AC-005** (`FR-005`): 修订检测产生 v2+差异清单,v1 保留可读 — tests: `tests/integration/test_f002_revision.py`
- [x] **AC-006** (`FR-006`): 定时器安装且手动触发导出成功;backup-nas.sh 后 NAS 端 lake/ 产物齐全 — tests: `tests/integration/test_f002_schedule_backup.py`
- [x] **AC-007** (`FR-005`, `FR-001`): 版本物理隔离——修订产生 v2 后,v1 manifest 列出的每个分区文件字节不变,按 v1 读取返回修订前的行;并发读 v1/v2 不串版 — tests: `tests/integration/test_f002_revision.py`
- [x] **AC-008** (`FR-003`, `FR-001`): manifest 完整性 fail-closed——删清单内文件 / 改一字节,两种情形读取均抛 ManifestIntegrityError;而目录中存在**本版本未引用**的 .rN 文件(其他版本的合法分区)时必须正常返回,reader 全程不扫描目录 — tests: `tests/integration/test_f002_reader.py`
- [x] **AC-009** (`FR-004`): as-of 双时间轴无前视——read(as_of=T) 当且仅当事件时间与可用时间均不晚于 T 才返回该行;反例 latest_candle=09:00 / time=12:00 的信号在 as_of=10:00 必须**不在**结果内,在 as_of=13:00 必须在;realized_return_60m 在 evaluated_at > T 时置 NULL 而非丢行 — tests: `tests/integration/test_f002_reader.py`
- [x] **AC-011** (`FR-001`, `FR-005`): manifest 是累计完整快照——连续两次增量导出后,第二个版本的 partitions 覆盖第一个版本的全部逻辑分区(未变项原样继承、变更项替换),rows 等于合成后清单的总和而非单日增量;按第二个版本读取返回全 span — tests: `tests/integration/test_f002_revision.py`
- [x] **AC-012** (`FR-002`): row_digest 规范性——同一批数据经 psycopg2 与 PyArrow 两路输入摘要相同;改写任一 double 的最低有效位摘要必变(证明未走定标丢精度);两行 +x/−x 抵消式改写摘要必变 — tests: `tests/unit/test_f002_digest.py`
- [x] **AC-013** (`FR-003`, `FR-004`): as-of 保真度 fail-closed——对 as_of_fidelity=event_time_only 的 dataset(ohlcv_1m)传 as_of 且未显式 allow_event_time_only 时抛 InsufficientAsOfFidelityError;显式豁免时 ReadResult.as_of_fidelity 如实回报 event_time_only — tests: `tests/integration/test_f002_reader.py`
- [x] **AC-014** (`FR-001`, `FR-005`): 失败重跑不漏日——构造「分区文件已 rename 但 manifest 未发布」的中断态后重跑增量,窗口起点仍由上一 valid manifest 推导,该日分区出现在新版本清单中;本轮未覆盖的 skipped 键原样继承而非被清空 — tests: `tests/integration/test_f002_export_reconcile.py`
- [x] **AC-015** (`FR-001`, `FR-003`): DatasetVersion value_digest 按 design §3 的 canonical 投影与分区摘要计算；同值数据仅改变 Parquet codec/path 时摘要不变，改任一值、投影 schema 或分区覆盖时摘要必变；缺失或重算不符时 reader fail-closed — tests: `tests/unit/test_f002_manifest.py`、`tests/integration/test_f002_reader.py`
- [x] **AC-010** (`FR-002`, `FR-003`): 并发改写不产伪 valid——对账期间对已导出窗口 upsert 历史行,导出仍基于同一快照;结果或为 valid 且与该快照一致,或为 invalid,不出现「对账 ok 但湖内是旧值」 — tests: `tests/integration/test_f002_export_reconcile.py`

**done 时的已知限制(2026-09-13 裁决记录)**:F004(Kronos 真实推理运行时)不阻塞本 feature 收口,
因此 F002 done 时湖内 `signals_log` 的内容预期仍以 `source=placeholder` 为主——**导出管线正确
不等于内容可用于因子研究**。收口时验收证据必须如实记录该 dataset 的行数与 `source` 分布,
不得以"五 dataset 齐备"含糊带过;F004 落地后内容自动升级,F002 无需返工。

### 验收证据(2026-09-14 实测,WSL2 Ubuntu + docker-ce + TimescaleDB 631 万行生产库)

- **端到端(AC-001/AC-002/AC-003)**:`lake/` 五 dataset 全量导出全部 `valid`,对账三项全 ok——
  ohlcv_1m 6,331,981 行/4,398 分区/184.5s(含逐分区 row_digest 对账);funding 13,152/4,386;
  OI 744/36;basis 空表合法空快照;signals_log 2,040/3 分区/skipped 3(源数据生成器停机缺口)。
  reader 对真实湖读取行数与库内 `time < '2026-09-13'` 行数精确相等;对账失败路径经
  `tests/integration/test_f002_export_reconcile.py` 注入不一致后版本以 `invalid` 发布且 reader 拒绝。
- **修订演进(AC-005/AC-007/AC-011)**:`test_f002_revision.py` 全绿——UPDATE 历史行产生 v2+
  revision_diff(changed),v1 manifest 及其引用分区文件字节不变,按 v1 读回修订前值,并发读不串版;
  连续两次增量的 manifest 为累计完整快照(未变分区跨版本共享同一物理文件)。
- **失效与完整性(AC-008/AC-002)**:删清单内文件/改一字节均抛 `ManifestIntegrityError`;
  目录中存在本版本未引用的 `.rN` 正常返回(reader 不扫目录)。
- **as-of 双时间轴(AC-009/AC-013)**:`latest_candle=09:00/time=12:00` 的信号在 as_of=10:00
  不在结果内、as_of=13:00 在;`evaluated_at > T` 时 `realized_return_60m` 置 NULL 不丢行;
  ohlcv_1m 传 as_of 默认抛 `InsufficientAsOfFidelityError`,显式豁免后如实回报 `event_time_only`。
- **摘要规范性(AC-012/AC-015)**:`test_f002_digest.py`/`test_f002_manifest.py` 全绿——psycopg2
  与 PyArrow 两路输入同摘要;double 最低有效位改写与 ±x 抵消式改写摘要必变;value_digest 对
  path/codec 稳定、对值/投影/覆盖变化必变;reader 重算不符 fail-closed。
- **中断恢复(AC-014)**:构造「分区已 rename、manifest 未发布」孤儿态后重跑,窗口起点由上一
  valid manifest 推导,该日以 `.r2` 进入新版本清单,skipped 键正确继承。
- **调度与灾备(AC-006/FR-006)**:`alphamill-export.timer`(每日 02:00)与
  `alphamill-fullexport.timer`(周日 04:00)已安装启用,手动触发 `alphamill-export.service`
  退出码 0,journalctl 可查摘要;`backup-nas.sh` 真实跑通,NAS 端
  `/volume1/alphamill-backups/lake/` 8,823 个分区文件与本地精确一致,`_manifests/` 与
  `_metadata/symbol_maps/<digest>.csv` 齐备。附带修复:F001 遗留的 NAS known_hosts 缺失
  (曾致 backup.service 无效重试 89 次,T019 的 StartLimit 回补同时使重试上限真正生效)。
- **信号内容限制证据(如上裁决记录要求)**:湖内 signals_log `data_version=v2026.09.13` 共
  2,040 行,`source` 分布 = `{placeholder: 100%}`——内容不可用于因子研究,待 F004 落地升级。
- **全量导出耗时**:ohlcv_1m 单 dataset 184.5s,五 dataset 合计 3m48s(NFR-003 分钟级达成;
  增量导出秒级,journalctl no-op 运行 1.4s 实证)。

## 7. 测试、依赖与决策

### 测试策略

- 集成测试:导出→对账→取数全链路、失效拒绝、修订版本演进、调度+NAS(需要本地 TimescaleDB 在线,CI 跳过);
- 单元测试:symbol_map 内容寻址生成/按 digest 加载、manifest/value_digest 读写校验、data_version 排序;
- 不做性能压测——631 万行全量导出的实测耗时记入验收证据即可。

### 依赖

- 上游:F001(TimescaleDB 数据与调度模式)、集成文档 §1.2 导出契约、架构 §4.4 manifest 契约;signals_log dataset 的**内容质量**另依赖 Kronos 真实推理容器化——薄壳为 mock 时导出的是 `source=placeholder` 行,导出管线正确不等于内容可用于因子研究;**该项不在 F002 契约内**(见 §3 范围外);
- 下游:M1 评测台(FR3)、ADR-0007 ResearchSnapshot builder、FR7 manifest 实验链、Vibe local loader(可选);
- 新增依赖:DuckDB(pyproject 新增 pin,版本范围本地验证后落定);
- 外部/环境:无新外部依赖;lake/ 磁盘空间(全量约 1-2GB)。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| data_version 语义 | 日期版 `vYYYY.MM.DD` 起步,同日重导追加序号(`-r2`);按 dataset 独立、修订递增不复用 | 简单可读;不可变与 invalid 不可逆不变量由测试锁定 | 跨 dataset 绑定由 ADR-0007 ResearchSnapshot,不造全湖版本号 |
| 对账口径 | 行数 + 时间边界 + 按主键排序的 SHA-256 `row_digest`(定义见 design §3;两侧由同一 Python 函数计算) | 摘要抗抵消,抓得住行数与极值都不变的内部数值改写;行数抓缺块 | 不一致定位到分区级;**不设降级出口**,性能不可接受时走 spec 修订 |
| 双口径 | 本期仅落列语义(close 原样)与 symbol_map;无复权计算 | crypto 无复权;集成 §1.2 已明确 | FR1.4 完整口径随评测台需求演进 |
| 风险:DuckDB 新依赖引入版本漂移 | pin 范围入 pyproject,check_dep_pins 门禁覆盖 | dev 依赖锁定惯例(C001 教训) | 版本升级走显式改动 |
| 风险:湖与库漂移不可见 | 每次导出强制对账;周日全量校验兜底 | 对账是本 feature 的灵魂(承 F001) | 漂移审计进 manifest 差异清单 |

## 8. 待确认问题

- [x] Q-001:导出哪些 dataset?——ohlcv_1m + 衍生品三表 + signals_log 五个(FR1.2 列举);quality_flags 不单独导出,以 manifest 质量标注继承(集成 §1.2)
- [x] Q-002:F002 放 0.1 还是 0.2?——0.2(0.1 已收口,M1 数据桥是新能力版本)
- [x] Q-003:data_version 全局唯一还是按 dataset 独立递增?——**裁决(2026-09-13, owner;ADR-0007 补正):按 dataset 独立递增**。各 dataset 导出节奏与失败域不同,全局版本号会让单 dataset 对账失败作废整批;跨 dataset 实验不按 `exported_at` 临时聚合,而由不可变 ResearchSnapshot 显式绑定 `(dataset,data_version,value_digest)`、cutoff 与映射/日历摘要。放弃的好处:没有单一全湖版本号;获得不耦合发布节奏的可复现引用集合
