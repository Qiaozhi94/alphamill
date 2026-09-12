---
kind: feature
id: F002
version: "0.2"
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: design
created: 2026-09-12
updated: 2026-09-12
---

# F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**:`spec.md`(FR-001..006 / NFR-001..003)
- **PRD / Architecture / System Design**:`docs/alphamill-prd.md` FR1.2/1.3/1.4/1.6、M1;`docs/alphamill-architecture.md` §〇、§四、§4.4;`docs/alphamill-integration.md` §1.2(导出设计与修订政策,唯一权威)、§2.2(symbol_map M1 出口)
- **执行环境(2026-09-12 实测钉死)**:与 F001 收口态一致——WSL2 Ubuntu 26.04 + docker-ce 29.8.0;TimescaleDB 容器 healthy(631 万行 binance 数据);pwsh 7.6.6 用户态;systemd user timers(backup/snapshot 两个先例);`.venv` Python 3.14 + pyproject 依赖管理;出网经 `BINANCE_HTTPS_PROXY`(本特性无需出网,DuckDB 为本地库)
- **实现约束**:D4 数据红线(研究只读湖快照);取数模块零写路径;湖分区文件与 manifest 不可变(NFR-002)

## 1. 技术概要与影响面

三步走:① 导出器核心——ohlcv_1m 一个 dataset 端到端(查询 → 分区 Parquet → manifest → 对账);② 扩展——衍生品三表与 signals_log、DuckDB 取数模块、symbol_map;③ 运维化——每日/周日调度与 NAS `lake/` 激活,修订检测(全量校验模式)。

- 前端:不适用
- 后端 / API:新增 `src/alphamill/data_bridge/exporter.py`(导出器)、`manifest.py`(manifest 读写)、`reader.py`(DuckDB 取数)、`symbol_map.py`(映射);全部为本地库/本地文件操作,无网络
- 存储 / Migration:`lake/` 目录结构落地(见 §3);TimescaleDB 只读(导出器 SELECT,零写)
- Runtime / Agent Adapter:无
- Event / Evidence:`lake/_manifests/<dataset>/<data_version>.json`(机器可读,FR7 实验链的输入);导出运行日志进 journalctl(调度模式)
- 文档 / 配置:`docs/README.md` 已挂 releases 索引(0.1 收口时完成);新增调度 timer 两枚

## 2. 架构与模块边界

```
src/alphamill/data_bridge/
├── collector/        # F001 已有(采集,直写 TimescaleDB)——不变
├── exporter.py       # 新增:TimescaleDB → 分区 Parquet + manifest(唯一写湖的模块)
├── manifest.py       # 新增:manifest 契约读写、data_version 排序、invalid 标记
├── reader.py         # 新增:DuckDB 只读取数(唯一合法研究入口)
└── symbol_map.py     # 新增:symbol_map.csv 生成与双向查询
```

依赖方向单向:`reader.py → manifest.py → lake/`(只读);`exporter.py → manifest.py + lake/`(读写,唯一写方);两者都依赖 `db_writer.db_connect` 的库连接约定。评测台/挖掘(M1 后续)只 import `reader.py`,禁止直接触碰 lake 文件路径——数据红线的技术落点。

## 3. 数据模型与 Migration

- **dataset registry**(F002-D007 / R2-04 冻结;`data_bridge/registry.py` 的只读常量。
  `export_dataset()` 与 `read()` 的 `dataset` 只接受下表键,其余抛 `UnknownDatasetError`。
  **投影列逐一枚举,不用「等」占位**——摘要的稳定性取决于输入是否被完全规范化):

  | dataset | 投影列(顺序即编码顺序) | 逻辑分区键 | **event_time** | **available_at** |
  |---|---|---|---|---|
  | `ohlcv_1m` | time,exchange,symbol,open,high,low,close,volume | (exchange,pair,date) | `time` | **无**(见下) |
  | `derivatives_funding_rates` | time,exchange,symbol,funding_rate,next_funding_time,mark_price,index_price,metadata,ingested_at | (exchange,pair,date) | `time` | `ingested_at` |
  | `derivatives_open_interest` | time,exchange,symbol,timeframe,open_interest,open_interest_value,base_volume,quote_volume,metadata,ingested_at | (exchange,pair,timeframe,date) | `time` | `ingested_at` |
  | `derivatives_mark_index_basis` | time,exchange,symbol,timeframe,mark_open,mark_high,mark_low,mark_close,index_open,index_high,index_low,index_close,basis_close,basis_pct,metadata,ingested_at | (exchange,pair,timeframe,date) | `time` | `ingested_at` |
  | `signals_log` | time,exchange,symbol,source,signal_type,confidence,metadata,latest_candle,expected_return,volatility,direction_prob,realized_return_60m,evaluated_at | (date) | `latest_candle` | `time` |

  类型只有五种,编码规则见下方 `row_digest`:`timestamptz` / `text` / `double precision` /
  `jsonb` / NULL。允许出现在 `read()` 过滤条件里的列**仅** `event_time`、`available_at`、
  `exchange`、`symbol`、`timeframe`;其余列只能读出来自己筛,不进 SQL/DuckDB 谓词。

- **双时间轴与 as-of 语义**(F002-R2-01 冻结,本节是前视防线的文档落点):
  研究侧的「T 时点可见」必须**同时**满足 `event_time <= T` **且** `available_at <= T`。
  反例:一条 `latest_candle=09:00`、`time=12:00` 的信号,在 `as_of=10:00` 时**根本还不存在**,
  把它算进 10:00 就是用未来模型/参数产生的信号倒灌历史。(Round 1 的 AC-009 正好把这条写反了,
  要求"晚写早事件必含"——那是把前视固化成验收契约,已作废重写。)
  `read(as_of=T)` 同时施加两条约束;不传 `as_of` 时只按 `start/end` 切 `event_time`,
  返回值显式标注 `as_of=None`(纯历史切片,**不得**用于任何回测/门禁判定)。

  **已知缺口(不掩盖)**:`ohlcv_1m` 表没有采集时间列,`available_at` 无法重建——回补写入的历史
  K 线在湖内看不出"何时才可见"。因此 ohlcv 的 as-of 只能退化为 `event_time <= T`,该退化
  **写进 manifest 的 `as_of_fidelity: "event_time_only"`**,由消费方自行判断可接受性;要做真正的
  双时间轴需给 `ohlcv_1m` 加 `ingested_at` 列,属 F001 schema 变更,不在本 feature 范围。

  **标签列的可用性单独处理**:`signals_log.realized_return_60m` 是事后回填的结果列,
  其可用时间是 `evaluated_at`。`read(as_of=T)` 时若 `evaluated_at > T` 或为 NULL,
  **该列置 NULL 而不是丢行**——丢行会让样本集随 T 变化,置 NULL 才是"当时还不知道结果"的忠实表达。
  不做这一步等于把标签泄漏进特征。

- **湖布局与版本隔离**(集成 §1.2;F002-D001 修订):
  ```
  lake/
  ├── ohlcv_1m/exchange=binance/pair=BTC-USDT/date=2026-09-11.r1.parquet
  │                                           date=2026-09-11.r2.parquet   # 修订产生新文件
  ├── derivatives_funding_rates/exchange=binance/pair=.../date=....r1.parquet
  ├── derivatives_open_interest/...
  ├── derivatives_mark_index_basis/...
  ├── signals_log/date=....r1.parquet        # 无 exchange 维度,按事件日
  └── _manifests/<dataset>/<data_version>.json
  ```
  **分区文件名带修订序号 `.rN`,写入后永不覆盖**:同一 (pair, date) 内容变化时写 `rN+1`,
  旧文件原样留存。版本与文件的绑定**不靠路径推导,靠 manifest 的 `partitions` 清单显式枚举**
  (见下),因此未变化的分区在多个 data_version 之间共享同一物理文件——既满足"旧快照字节不变"
  (NFR-002 / AC-005),又不必每个版本复制整个湖。

  **为什么不是把 data_version 放进路径**:那样每次周日全量校验都要复制 631 万行的全部分区,
  一年 52 份副本;而修订实际只涉及少数分区。代价是"哪些文件属于哪个版本"不能靠 `ls` 看出来,
  必须读 manifest——这正是 `partitions` 清单成为强制字段的原因。

  **原子发布**:分区文件先写到 `lake/_staging/<dataset>/<data_version>/` 再 rename 进正式路径;
  **manifest 是发布点**——最后写(临时名 + rename),写成功前该 data_version 对 reader 不存在。
  中断留下的 staging 目录与孤儿 `.rN` 文件不被任何 manifest 引用,不影响正确性,由全量模式顺带清理。
- **pair 目录命名**:湖内 pair 用 `BASE-QUOTE`(`/` 换 `-` 规避路径分隔符),永续加 `-PERP` 后缀区分市场类型。映射表的键、列与碰撞规则见 §4「symbol_map 键的冻结」——**不是三列、也不能由 `DISTINCT symbol` 单独推导**(F002-D010)。
- **data_version 语义**(spec Q-003 已裁决:**按 dataset 独立**,2026-09-12 owner):`vYYYY.MM.DD`,同日重导追加 `-r2/-r3`;排序 = 日期字典序 + 序号;最新 valid 版本 = 排序最大且 `status != invalid`。每 dataset 独立演进,互不阻塞。
- **manifest 契约**(架构 §4.4 + 本期扩展字段):
  ```json
  {
    "dataset": "ohlcv_1m",
    "source": "timescaledb@alphamill",
    "source_snapshot": {"backend_xmin": 84412, "taken_at": "2026-09-12T02:00:03Z"},
    "exported_at": "2026-09-12T02:04:11Z",
    "rows": 6312924,
    "pairs": ["BTC-USDT", "..."],
    "caliber": {"close": "raw", "adjclose": "none_crypto"},
    "data_version": "v2026.09.12",
    "status": "valid",
    "partitions": [
      {"path": "ohlcv_1m/exchange=binance/pair=BTC-USDT/date=2026-09-11.r1.parquet",
       "rows": 1440, "time_min": "2026-09-11T00:00:00Z", "time_max": "2026-09-11T23:59:00Z",
       "bytes": 41233, "sha256": "9f2c…"}
    ],
    "reconcile": {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"},
    "quality": {"flagged_partitions": [], "unresolved_total": 0},
    "skipped": [{"pair": "DOGE-USDT", "date": "2026-09-11"}],
    "excluded_null_event_time": 0,
    "revision_diff": []
  }
  ```
  **`partitions` 是必填的版本身份**(F002-D002):它同时回答"这个版本由哪些文件组成"与
  `reader` **只按 `partitions` 清单构造输入路径,从不扫描目录**(F002-R2-02):逐项校验
  **文件存在、字节数相符、sha256 相符**,任一不符抛 `ManifestIntegrityError`,不降级为警告。
  Round 1 写的「实际读到的文件集合与清单完全相等、多一个文件同样判红」是错的——`.rN` 共享模型下
  v1 的 `day.r1` 与 v2 的 `day.r2` 本来就必须同时在盘上,按目录全集比对会让两个版本互相判死。
  防止「误读别的版本」的机制不是目录比对,而是**根本不按目录读**:输入路径全部来自清单。
  这条是 NFR-002「同版本同查询同结果」的唯一技术保证,原设计只有 `rows/value_sum` 且只在导出时
  对源库比一次,证明不了以后读到的文件没被改。
- **质量标记继承与裁决**(F002-D005 冻结):`ohlcv_quality_flags` 的未解决标记
  (`resolved_at IS NULL`)按 (exchange, symbol, date(time)) **落到分区级**,写进 manifest 的
  `quality.flagged_partitions`;`unresolved_total` 只是派生总数,不再是唯一信息。裁决政策:

  | 情形 | 版本 status | reader 行为 |
  |---|---|---|
  | 无未解决标记 | `valid` | 正常返回 |
  | 有未解决标记,但分区数据本身导出成功且对账通过 | `valid` | **默认拒绝**读取被标记分区,抛 `FlaggedPartitionError` |
  | 对账失败 / manifest 完整性失败 | `invalid` | 一律拒绝(既有政策) |

  `read()` 增 `allow_flagged: bool = False`;显式传 `True` 才放行,且返回值随附被放行的分区清单,
  调用方无法"不知情地"用到带旗数据。**为什么不把带旗直接判 invalid**:质量标记描述的是源数据
  的已知瑕疵(缺 K 线/异常跳变),不是导出错误——整版作废会让一个坏分区废掉整天的可用数据;
  但默认放行同样不可接受,那正是原设计"只有总数、无裁决行为"的缺陷。默认拒绝 + 显式豁免
  把选择权交给研究者并留下痕迹。

  `skipped` 登记窗口内查不到行的 (pair, date),**不记原因**——采集断线与确实无行情同样落这里(DQ-003 裁决);`revision_diff` 仅全量校验模式填写:相对上一 valid 版本登记修订分区清单(`[{pair, date, reason}]`);`status: invalid` 时 `reconcile` 记录失败项。
- **对账口径**(F002-D003 / R2-04 冻结,唯一权威定义,spec/tasks/integration 引用此处):

  | 字段 | 计算方 | 定义 |
  |---|---|---|
  | `rows` | 两侧 | 分区行数 |
  | `time_min` / `time_max` | 两侧 | 分区 `event_time` 边界 |
  | `row_digest` | 两侧 | 规范编码后**按编码字节串字典序排序**的流式 SHA-256 |

  **规范编码(逐列,顺序 = registry 投影列顺序,无损)**:

  | 类型 | 编码 |
  |---|---|
  | `timestamptz` | UTC 微秒 int64,8 字节大端 |
  | `double precision` | **IEEE-754 binary64 原始位模式,8 字节大端**;`-0.0` 归一为 `+0.0`,`NaN` 归一为单一静默 NaN 位型 |
  | `text` | UTF-8 字节,前置 uint32 大端长度 |
  | `jsonb` | 规范 JSON(键按 Unicode 码点排序、无空白)后按 `text` 编码 |
  | NULL | 单字节哨兵 `0x00`;非 NULL 值前置 `0x01`,故哨兵不与任何值碰撞 |

  **`double` 必须走原始位模式,不得用 `Decimal` 定标**:Round 1 写的 `Decimal(10 位)` 会让
  小于 `1e-10` 的改写完全不可见,而 `row_digest` 存在的理由正是抓这类改写(F002-R2-04)。

  **排序键 = 该行的规范编码字节串本身**,不是逻辑主键。理由:`signals_log` 在库里**没有主键**
  (实查确认),Round 1 提的 `(latest_candle,exchange,symbol,source)` 可重复、给不出确定顺序;
  按编码字节串排序对任何 dataset 都成立——完全相同的两行编码相同且相邻,顺序唯一确定,
  重复行也不破坏确定性。逻辑主键只用于**分区替换**(见增量合成),不参与摘要。

  **两侧由 `digest.py` 的同一个 Python 函数计算**——源侧喂 psycopg2 游标、湖侧喂 PyArrow
  record batch,只有一份 `canonical_row_bytes()`。不让 PG 与 DuckDB 各算一次:`hashtext()` 是 PG
  内部未文档化函数、无跨引擎等价物;`sum(round(col::numeric,10))` 虽可跨引擎却**不抗抵消**
  (两行 +x/−x 的改写让和不变)。SHA-256 与聚合顺序无关(顺序由字节序固定)且抗抵消。
  **本设计不提供降级出口**:降级会让上述改写重新不可见;性能不可接受属规格问题,走 spec 修订。

  (原文称该方案「承 F001 design §3 同源」不成立:F001 的口径是行数 + 时间轴连续性 + 聚合桶
  精确一致,全程没有校验和,`hashtext` 在 F001 代码与文档中出现 0 次。)

- **源库一致性快照**(F002-D004):导出查询与源侧 `row_digest` 计算**必须在同一个
  `REPEATABLE READ` 只读事务内完成**。理由:F001 的采集与回补都是 `upsert`,能在窗口终点之前
  改写历史行——"只读 + 时间截断"并不等于快照隔离。若导出与对账各开一次连接,两者可能看到不同
  版本的同一行,产出"对账通过但湖内是旧值"的伪 valid。事务开始后记录
  `txid_current_snapshot()` 的 xmin 到 manifest 的 `source_snapshot`,使任何一次导出可以
  事后追溯它看到的是哪个时点的库。窗口截断 `[start, end)` 仍然保留,但它解决的是"分区边界",
  不是"并发一致性",两者不可互相替代。

- **manifest 合成算法**(F002-R2-03 冻结;**每个 manifest 都是累计完整快照,不是一日 delta**):

  1. 读上一个 valid manifest(无则空清单),把它的 `partitions` **全量继承**为基线;
  2. 本轮产出的每个分区按**逻辑分区键**(registry 的 `(exchange,pair[,timeframe],date)`)
     在基线里查找:命中则**整项替换**(新 `.rN` 路径 + 新 rows/边界/bytes/sha256),
     未命中则**追加**;基线中本轮没碰的项原样保留;
  3. `rows` / `pairs` / `quality.flagged_partitions` / `skipped` / `excluded_null_event_time`
     一律**按合成后的完整清单重算**,不是本轮增量的计数;
  4. 原子发布:清单齐备后写 manifest(临时名 + rename)。

  没有这一条,"每日增量"产出的 manifest 到底是当天 delta 还是累计快照就没有定义,
  `read(dataset, data_version=昨天)` 可能只拿到一天的数据——而 spec 承诺的是快照语义。
  全量校验模式走同一算法,区别只在本轮产出覆盖全 span。

- **导出窗口与增量语义**:增量导出窗口 = `[max(已有分区日期)+1, 导出日-1]`(昨日分区);**首次导出**(该 dataset 无任何已有分区)时 `max(已有分区日期)` 无定义,窗口起点取库内 `date(min(time))`,即首跑等价于一次全量;全量校验 = 全 span 重导至新 data_version 并做分区级 diff;窗口内无数据的 pair 跳过并记 skipped。
- **回滚/前向兼容**:导出失败留下的半成品只存在于 `lake/_staging/`,**不覆盖任何已发布分区**(已发布的 `.rN` 永不重写);未被任何 manifest 引用的 staging 残留与孤儿 `.rN` 由全量模式清理。invalid 版本永不复用版本号。DuckDB 侧无 migration。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

```python
# registry.py —— dataset 白名单(§3),其余模块的 dataset 参数一律经它校验
DATASETS: Mapping[str, DatasetSpec]          # 只读;未登记的名字 → UnknownDatasetError

# exporter.py
def export_dataset(dataset: str, mode: Literal["incremental", "full"],
                   window_end: datetime | None = None) -> dict   # 返回 manifest 摘要
# reader.py —— start/end 作用于 registry 声明的事件时间列(signals_log 即 latest_candle)
def read(dataset: str, data_version: str | None = None,          # None=最新 valid
         start: datetime | None = None, end: datetime | None = None,
         pairs: list[str] | None = None,
         allow_flagged: bool = False) -> ReadResult   # .frame: pd.DataFrame; .flagged: list[str]
def latest_valid_version(dataset: str) -> str                    # 无 valid 版本则抛 VersionNotFoundError
# symbol_map.py —— 映射键含 exchange 与 market_type(F002-D010)
def build_symbol_map(rows: list[SymbolRow]) -> pd.DataFrame   # 纯函数;SymbolRow=(exchange, market_type, db_symbol)
def export_symbol_map(conn=None) -> Path                      # 薄壳:查库后落 src/alphamill/data_bridge/symbol_map.csv
def resolve(value: str, direction: Literal["to_lake", "to_freqtrade", "to_db"],
            exchange: str, market_type: str = "spot") -> str  # 无 exchange 无法消歧,故为必填
```

异常契约:`DataBridgeError`(基类)/`InvalidVersionError`(拒绝读取 invalid)/
`VersionNotFoundError`/`ManifestIntegrityError`(文件缺失、字节数或 sha256 不符、文件集合不等)/
`FlaggedPartitionError`(带质量旗分区且未显式豁免)/`UnknownDatasetError`(不在 registry 中)。
取数模块对以上任一情形一律抛错,不降级为警告(D4 红线,SOP 安全降级须声明——本 feature 无降级)。

**symbol_map 键的冻结**(F002-D010):库内 `DISTINCT symbol` **不足以无损推导**映射——
同一个 `BTC/USDT` 在 spot 与 swap 上是不同的标的,Freqtrade 侧命名也不同,而 `ohlcv_1m` 与
`derivatives_*` 分别来自 `binance` 与 `binanceusdm`。故映射键为 **(exchange, market_type, db_symbol)**,
csv 五列:`exchange,market_type,db_symbol,lake_pair,freqtrade_pair`;格式冻结为
spot `BTC/USDT → BTC-USDT`(Freqtrade `BTC/USDT`)、perp `BTC/USDT:USDT → BTC-USDT-PERP`
(Freqtrade `BTC/USDT:USDT`)。**任意两行推导出相同 `lake_pair` 即为碰撞,导出直接失败**
(`SymbolCollisionError`),不做静默去重——碰撞意味着两个不同标的会写进同一个湖分区。
文件入库路径沿用集成 §2.2 的唯一权威值 `src/alphamill/data_bridge/symbol_map.csv`
(原 design 只说"写 symbol_map.csv" 未给路径)。

### Event / Trace Contract

不适用(无机器事件流);manifest 即证据文件,FR7 实验链后续引用其 `data_version` 字段。

## 5. Runtime、Workflow 与并发

- 调度:`alphamill-export.timer` 每日 **02:00** 增量导出;`alphamill-fullexport.timer` 周日 **04:00** 全量校验(systemd user timer,`Type=oneshot`,承 backup/snapshot 先例)。02:00 的取值不是随意的:`alphamill-backup.timer` 是 03:00 且带 `RandomizedDelaySec=10min`(实际 03:00-03:10),导出必须早于它完成,当日分区才会被同一晚的 NAS 备份带走;周日 04:00 的全量校验排在备份之后,本轮产出由次日备份带走。
- 并发:单机单实例;导出与实时采集的并行安全由 §3 的 **REPEATABLE READ 快照**保证——窗口截断只解决分区边界,不解决并发一致性,两者不可互相替代;DuckDB 查询为只读进程级并发,无锁。
- **退出码契约**(F002-D009):`0`=成功;`1`=**可重试**的瞬时故障(库连接失败、IO 错误、
  staging 写入中断);`2`=**不可重试**的数据裁决(对账失败 → 版本已标 invalid、manifest 完整性
  失败、registry 校验失败)。unit 用 `RestartPreventExitStatus=2` 锁定——原设计既要求"对账失败
  非零退出"又声明"对账失败不重试",而 `Restart=on-failure` 对任何非零码都会重试,两句直接冲突;
  退出码分层是让这两条同时成立的唯一方式。重试对账失败毫无意义:同一份数据重算必然同样失败,
  修复路径是产出新版本。
- 重试:可重试故障由 systemd `Restart=on-failure` + `RestartSec=15min` 重试;**次数上限必须显式写 `StartLimitIntervalSec` + `StartLimitBurst=3`**——`alphamill-backup.service` 的注释写了「最多 3 次」却没写这两个指令,实际不生效,F002 的两个 unit 不重复该疏漏(并顺手给 backup.service 补上,列为 T019)。对账失败(退出码 2)不重试——直接 invalid(修复=新版本)。
- 不可回滚副作用边界:invalid 标记与新版本创建均不可逆,但旧版本永在(不可变),最坏情况 = 多一个废版本目录,无破坏性。

## 6. UI 与可观测性

- 无新 UI;Grafana 不感知湖(监控仍走 TimescaleDB);
- 可观测:导出结束打印/记录 per-dataset rows、耗时、data_version、对账结论;journalctl 可查(调度模式);
- 后续 M1 评测台报告将引用 manifest 的 data_version(本期只生产,不消费)。

## 7. 失败、恢复、安全与兼容

- 校验与失败映射:对账不一致 → invalid + 非零退出;DuckDB 查询 invalid → InvalidVersionError;manifest 缺失 → VersionNotFoundError;
- 重启与恢复:分区文件原子写(临时名+rename),重导幂等覆盖;调度失败 systemd 重试;
- 权限 / escalation / 凭据边界:库凭据走 `.env`(既有);lake/ 无密钥;取数模块不接受任何"写"参数面(签名上不存在写路径,NFR-001 由接口形状保证 + 测试断言);
- Windows / POSIX / 版本兼容:纯 WSL2 内运行,无跨界文件交换;DuckDB/PyArrow 版本 pin 入 pyproject(check_dep_pins 覆盖);Parquet 文件格式与 DuckDB 版本解耦(列式开放格式)。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f002_export_reconcile.py` | 全量导出后五 dataset 分区+manifest 齐备;DuckDB 行数=库内行数 |
| `AC-002` | integration | `tests/integration/test_f002_export_reconcile.py` | 构造对账失败 → manifest invalid |
| `AC-003` | integration | `tests/integration/test_f002_reader.py` | 版本/时间范围/pair 过滤正确;invalid 抛 InvalidVersionError |
| `AC-004` | unit | `tests/unit/test_f002_symbol_map.py` | 生成/双向解析/UTC 断言(靠 `build_symbol_map(db_symbols)` 的纯函数形态脱离库依赖;查库那层由 AC-001 的集成路径覆盖) |
| `AC-005` | integration | `tests/integration/test_f002_revision.py` | 修订 → v2+差异清单;v1 文件字节不变 |
| `AC-006` | integration | `tests/integration/test_f002_schedule_backup.py` | 导出 CLI 退出码 0;NAS 端 lake/ 文件存在 |
| `AC-007` | integration | `tests/integration/test_f002_revision.py` | 修订后 v1 每个分区文件 sha256 与字节数不变;按 v1 读回修订前的值;v1/v2 并发读不串版 |
| `AC-008` | integration | `tests/integration/test_f002_reader.py` | 删清单内文件/改一字节 → 抛 ManifestIntegrityError;目录存在他版本 .rN → 正常返回(reader 不扫目录) |
| `AC-009` | integration | `tests/integration/test_f002_reader.py` | as-of 双时间轴:latest_candle=09:00/time=12:00 的信号在 as_of=10:00 必不在、as_of=13:00 必在;evaluated_at>T 时 realized_return_60m 置 NULL 不丢行 |
| `AC-011` | integration | `tests/integration/test_f002_revision.py` | 两次增量后第二版 partitions 覆盖全部逻辑分区,rows 为累计而非单日 |
| `AC-012` | unit | `tests/unit/test_f002_digest.py` | 两路输入同摘要;double 最低位改写摘要必变;+x/−x 抵消式改写摘要必变 |
| `AC-010` | integration | `tests/integration/test_f002_export_reconcile.py` | 对账期间并发 upsert 历史行,结果为 valid 且与快照一致,或 invalid;不出现伪 valid |

集成测试需要本地 TimescaleDB 在线,DB 不可达时跳过(CI),本地全绿为准;单元测试无条件跑。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 导出器直写 Parquet(PyArrow)而非经 DuckDB | PyArrow 写、DuckDB 只读,职责分离 | 写路径唯一(NFR-001);DuckDB 专注查询 | 若 DuckDB COPY 更简可评估,接口不变 |
| data_version 按 dataset 独立(spec Q-003 已裁决,2026-09-12) | 各 dataset 导出互不阻塞,演进解耦 | signals_log 与 ohlcv 节奏不同 | 放弃项:无单一全局版本号;需要「全湖时点」时由各 manifest 的 exported_at 聚合派生 |
| DuckDB 引入为运行时依赖 | pyproject dependencies 新增 pin | 取数入口是其唯一用途 | 备选:polars scan_parquet(接口已抽象,可替换) |
| 分区文件带 `.rN` 且由 manifest 枚举,而非 data_version 进路径 | 未变分区跨版本共享文件,不必整湖复制 | 周日全量若按版本分目录,一年 52 份 631 万行副本 | 代价:版本组成不能靠 `ls` 看出,必须读 manifest——故 `partitions` 为必填 |
| 对账摘要在 Python 单侧实现,不做跨引擎哈希 | PG 与 DuckDB 无共同的可复现行哈希;同一函数喂两路数据则由构造保证一致 | `hashtext` 无跨引擎等价物;`sum(numeric)` 不抗抵消 | 若性能不可接受走 spec 修订,不在实现期降级 |
| 导出与源侧对账共享一个 REPEATABLE READ 事务 | upsert 回补可在窗口终点前改写历史行 | 只读+时间截断不等于快照隔离 | 长事务会拖住 vacuum,全量模式需观察膨胀,必要时分 dataset 事务 |
| 带质量旗分区仍为 valid,但 reader 默认拒绝 | 一个坏分区不该废掉整天可用数据;默认放行又会静默污染研究 | 质量标记描述源数据瑕疵,不是导出错误 | `allow_flagged=True` 显式豁免并回报清单 |
| 残余风险:湖文件被误删/误改 | manifest 的 per-partition sha256 + 字节数在**每次读取前**校验;reader 只按清单读、不扫目录(目录余项是其他版本的合法分区) | 不可变 + 完整性校验 + 灾备三重 | 单盘故障场景由 F001 灾备覆盖 |

## 10. 待确认设计问题

- [x] DQ-001:signals_log 无 exchange 维度,分区省略 exchange 层——确认(spec 已同步)
- [x] DQ-002:导出窗口与实时采集重叠如何保证分区完整——窗口截断 `[start, end)` 语义,跨窗口数据归下一窗口(§3)
- [x] DQ-003:增量导出窗口内 pair 无数据记 skipped,是否与"确实无行情"区分?——**裁决(2026-09-12, owner):不区分**,manifest 记 `skipped` 清单即可。理由:①区分需要在导出器里引入行情可得性外部探测,把一个纯本地模块变成有出网依赖(限速/代理/失败重试全要处理),本期收益不抵成本;②采集断线由 FR1.5 质量流程与 K 线延迟面板覆盖,不靠导出器发现。**升级条件(预先定死,避免事后扯皮)**:M1 评测台一旦出现因 skipped 语义不明导致的实际误判,即为 `skipped` 增补 `reason` 字段并加 pair 级可得性探针
