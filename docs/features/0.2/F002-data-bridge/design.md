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
- **实现约束**:D4 数据红线(研究只读湖快照);取数模块零写路径;湖分区文件与 manifest 不可变(INFR-002)

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

- **湖布局**(集成 §1.2):
  ```
  lake/
  ├── ohlcv_1m/exchange=binance/pair=BTC-USDT/date=2026-09-11.parquet
  ├── derivatives_funding_rates/exchange=binance/pair=.../date=....parquet
  ├── derivatives_open_interest/...
  ├── derivatives_mark_index_basis/...
  ├── signals_log/date=....parquet          # 无 exchange 维度,按日
  └── _manifests/<dataset>/<data_version>.json
  ```
- **pair 目录命名**:湖内 pair 用 Freqtrade 风格 `BASE-QUOTE`(如 `BTC-USDT`,`/` 换 `-` 规避路径分隔符);`symbol_map.csv` 三列:`lake_pair,freqtrade_pair,db_symbol`,由库内 DISTINCT symbol 直接生成,双向查询 O(1)。
- **data_version 语义**(spec Q-003 裁定:按 dataset 独立):`vYYYY.MM.DD`,同日重导追加 `-r2/-r3`;排序 = 日期字典序 + 序号;最新 valid 版本 = 排序最大且 `status != invalid`。每 dataset 独立演进,互不阻塞。
- **manifest 契约**(架构 §4.4 + 本期扩展字段):
  ```json
  {
    "dataset": "ohlcv_1m",
    "source": "timescaledb@alphamill",
    "exported_at": "2026-09-12T03:00:00Z",
    "rows": 6312924,
    "pairs": ["BTC-USDT", "..."],
    "caliber": {"close": "raw", "adjclose": "none_crypto"},
    "data_version": "v2026.09.12",
    "status": "valid",
    "reconcile": {"row_count": "ok", "checksum": "ok"},
    "quality_flags_unresolved": 0,
    "revision_diff": []
  }
  ```
  `revision_diff` 仅全量校验模式填写:相对上一 valid 版本登记修订分区清单(`[{pair, date, reason}]`);`status: invalid` 时 `reconcile` 记录失败项。
- **对账口径**:逐 dataset 逐分区——行数 + `sum(hashtext(ohlcv_1m.*::text))` 式校验和(承 F001 design §3 同源方案);校验和在导出端与库端各算一次比对。性能预估:631 万行 hashtext 全表约 1-2 分钟,可接受;增量模式只对新增分区算。
- **导出窗口与增量语义**:增量导出窗口 = `[max(已有分区日期)+1, 导出日-1]`(昨日分区);全量校验 = 全 span 重导至新 data_version 并做分区级 diff;窗口内无数据的 pair 跳过并记 skipped。
- **回滚/前向兼容**:导出失败留下的半个分区文件,下次同 data_version 重导覆盖(分区文件原子写:临时名 + rename);invalid 版本永不复用版本号。DuckDB 侧无 migration。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

```python
# exporter.py
def export_dataset(dataset: str, mode: Literal["incremental", "full"],
                   window_end: datetime | None = None) -> dict   # 返回 manifest 摘要
# reader.py
def read(dataset: str, data_version: str | None = None,         # None=最新 valid
         start: datetime | None = None, end: datetime | None = None,
         pairs: list[str] | None = None) -> pl.DataFrame | pd.DataFrame
def latest_valid_version(dataset: str) -> str                    # 无 valid 版本则抛 DataBridgeError
# symbol_map.py
def build_symbol_map() -> pd.DataFrame    # 从库 DISTINCT symbol 生成并写 symbol_map.csv
def resolve(value: str, direction: Literal["to_lake", "to_freqtrade", "to_db"]) -> str
```

异常契约:`DataBridgeError`(基类)/`InvalidVersionError`(拒绝读取 invalid)/`VersionNotFoundError`;取数模块对任何 manifest 缺失、校验失败、invalid 状态一律抛错,不降级为警告(D4 红线,SOP 安全降级须声明——本 feature 无降级)。

### Event / Trace Contract

不适用(无机器事件流);manifest 即证据文件,FR7 实验链后续引用其 `data_version` 字段。

## 5. Runtime、Workflow 与并发

- 调度:`alphamill-export.timer` 每日 03:00 增量导出;`alphamill-fullexport.timer` 周日 04:00 全量校验(systemd user timer,承 backup/snapshot 先例);与 backup-nas(03:00)错峰——导出 timer 改 02:00,确保 03:00 NAS 备份带走当日分区。
- 并发:单机单实例;导出与实时采集并行安全(导出只读库 + 窗口截断);DuckDB 查询为只读进程级并发,无锁。
- 重试:导出步骤失败即失败(退出码非零),由 systemd `Restart=on-failure` 重试 ×3;对账失败不重试——直接 invalid(修复=新版本)。
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
| `AC-004` | unit | `tests/unit/test_f002_symbol_map.py` | 生成/双向解析/UTC 断言 |
| `AC-005` | integration | `tests/integration/test_f002_revision.py` | 修订 → v2+差异清单;v1 文件字节不变 |
| `AC-006` | integration | `tests/integration/test_f002_schedule_backup.py` | 导出 CLI 退出码 0;NAS 端 lake/ 文件存在 |

集成测试需要本地 TimescaleDB 在线,DB 不可达时跳过(CI),本地全绿为准;单元测试无条件跑。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 导出器直写 Parquet(PyArrow)而非经 DuckDB | PyArrow 写、DuckDB 只读,职责分离 | 写路径唯一(NFR-001);DuckDB 专注查询 | 若 DuckDB COPY 更简可评估,接口不变 |
| data_version 按 dataset 独立(spec Q-003 裁定) | 各 dataset 导出互不阻塞,演进解耦 | signals_log 与 ohlcv 节奏不同 | 全局版本号若 FR7 需要再评估 |
| DuckDB 引入为运行时依赖 | pyproject dependencies 新增 pin | 取数入口是其唯一用途 | 备选:polars scan_parquet(接口已抽象,可替换) |
| 残余风险:湖文件被误删/误改 | manifest 校验和可在读取时发现;NAS 每日副本兜底 | 不可变 + 对账 + 灾备三重 | 单盘故障场景由 F001 灾备覆盖 |

## 10. 待确认设计问题

- [x] DQ-001:signals_log 无 exchange 维度,分区省略 exchange 层——确认(spec 已同步)
- [x] DQ-002:导出窗口与实时采集重叠如何保证分区完整——窗口截断 `[start, end)` 语义,跨窗口数据归下一窗口(§3)
- [ ] DQ-003:增量导出窗口内 pair 无数据记 skipped——是否需要与"确实无行情"区分?倾向不区分(manifest 记录即可),实现时若误判风险显现再升级
