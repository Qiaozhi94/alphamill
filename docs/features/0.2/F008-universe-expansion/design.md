---
kind: feature
id: F008
version: "0.2"
related_features: [F001, F002, F003, F007]
topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
doc_kind: design
created: 2026-09-14
updated: 2026-09-19
---

# F008：宇宙扩容与 point-in-time 宇宙台账 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR1.5/FR1.1/FR1.4/FR1.7；`docs/alphamill-architecture.md` §三（`data_bridge/` 与 `collector/`）、§4.1.1（截面边界）、§7.1（机器边界）；`docs/alphamill-integration.md` §1.3
- **ADR / 上游 Contract**：ADR-0007（ResearchSnapshot 绑定 universe/calendar artifact）、ADR-0003（门禁不降级）、ADR-0001（扩容是产出质量前提）；F002 的 `symbol_map` 内容寻址发布范式、dataset registry、manifest 与 reader 契约
- **实现约束**：
  - Python 3.11+，`src/alphamill/data_bridge/` 下扩子包；350 行硬上限、ruff（`E,F,I,B,UP,SIM`）；
  - 测试只能落在 `tests/unit` 与 `tests/integration`（`tools/verify.py` 只收集这两个目录）；
  - **不改 `F002` 已冻结的语义**：导出、对账、manifest、修订与失效规则一律沿用，本 feature 只扩 pair 集合并新增元数据 artifact；
  - 数据库变更走 `db/migrations/` + `tools/apply_migrations.py`（`schema_migrations` 账本）；
  - **机器边界（架构 §7.1）**：回填、质量门、导出、备份都在执行机 `qiaozhi-lt` 执行并记录 hostname；开发机 `qiaozhi-gp` 只跑单元与契约测试（`docs/SOP.md` §3）；
  - 交易所为 **Binance**（F001 事故后的数据路线，`EXCHANGES=binance` 已进 compose/.env/策略配置）——不复用 quant-crypto 的 OKX 发现脚本。

## 1. 技术概要与影响面

四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。发现从 Binance 公开行情按口径筛候选；人工确认后冻结为内容寻址的 `UniverseDef`；回填复用 F001 的 `historical_backfill.py`，外面套一层可续跑的批次编排；每个 pair 回填完成后跑质量门（复用 `tools/f001_backfill_report.py` 的口径，参数化到多 pair）；过门的 pair 写入联机库的 `universe_membership` 台账并进 F002 导出清单，台账再以 canonical JSON 发布为湖内内容寻址 artifact（最小 PIT 投影，schema 见 §3）。

- 前端：不适用
- 后端 / API：新增 `src/alphamill/data_bridge/universe/` 子包与模块入口 CLI `python -m alphamill.data_bridge.universe`（§4；**不新增 `[project.scripts]`**，理由见 §2 边界规则）；`collector/historical_backfill.py` 由脚本升级为可被编排调用（同时解除其 350 行豁免）
- **既有文件的改动点（只有两处，均为默认 `None` 的可选参数透传）**：`partitions.py`（`lake_pairs_map` 增可选 `admitted`；`produce_partitions` 按同一集合剔除单元格）与 `exporter.py`（`export_dataset` / `_export_one` 把 `admitted` 传下去）。除此之外不改 F002 的 manifest / 对账 / 修订 / 失效语义
- 存储 / Migration：新增 TimescaleDB 表 `universe_membership`（只追加）；新增湖元数据目录 `lake/_metadata/universes/<digest>.json`
- Runtime：长跑回填编排（限速、退避、断点、逐 pair 进度）
- Event / Evidence：`universe.member_changed`、`backfill.progress`、`backfill.failed`；质量门判定记录
- 文档 / 配置：修订 `docs/alphamill-integration.md` §1.3 的 OKX 过期表述；`docs/SOP.md` 豁免表移除 `historical_backfill.py` 条目

## 2. 架构与模块边界

```text
src/alphamill/data_bridge/
├── universe/                   # 本 feature 新增
│   ├── discover.py             #   Binance USDⓈ-M 筛选（成交额排名前 N + 上线天数 + 排除规则）
│   ├── definition.py           #   UniverseDef 内容寻址、冻结与版本化
│   ├── membership.py           #   PIT 台账读写 + universe_at(T)
│   ├── artifact.py             #   台账 canonical JSON 序列化与 digest 发布（最小 PIT 投影）
│   ├── quality_gate.py         #   新 pair 准入门（复用 F001 完整性口径）
│   └── backfill_runner.py      #   批次编排：限速 / 退避 / 断点 / 逐 pair 进度
├── collector/historical_backfill.py   # 由脚本改为可编排调用（解除行数豁免）
├── partitions.py               # 改动点 1：lake_pairs_map 增可选 admitted + 单元格级剔除
├── exporter.py                 # 改动点 2：export_dataset/_export_one 透传 admitted（默认 None）
└── universe/__main__.py        # 模块入口：python -m alphamill.data_bridge.universe <子命令>
                                #   与 python -m alphamill.data_bridge.exporter 同约定，不加 console script
```

> **CLI 入口形态**：仓库既有 CLI 一律是 `python -m <module>`（`data_bridge/exporter.py`、`alphamill.evaluation`），
> `pyproject.toml` 在 main 上**没有** `[project.scripts]` 表；而 `feat/F003-alphagen-vendor` 正在同一插入点新增
> `alphamill-generate` entry point——同表同点各自改一次会制造无谓文本冲突，且新增 entry point 还需 editable
> 重装才在开发机生效。因此本 feature 用 `python -m alphamill.data_bridge.universe`，任务与验收命令一律写全称。

边界规则：

| 边界 | 规则 |
|---|---|
| universe → F002 核心 | 单向依赖：`universe/` 调用 `symbol_map`/`paths`/`registry`/`partitions`；**「不改语义」不等于「不碰文件」**——准入过滤按 §3 在 `partitions.py` 与 `exporter.py` 各加一个默认 `None` 的可选参数，manifest/对账/修订/失效语义一律不变 |
| CLI 入口形态 | `python -m alphamill.data_bridge.universe`（`universe/__main__.py`），**不新增 `[project.scripts]`**：main 无该表，F003 正在同一插入点加 `alphamill-generate`，同表同点各自改动会制造文本冲突，且 entry point 需 editable 重装才生效 |
| 发现 → 冻结 | 发现只产候选，不改变任何持久状态；只有冻结动作写 `UniverseDef` |
| 冻结 → 回填 | 未冻结的定义不得驱动回填（长跑任务的输入必须不可变） |
| 质量门 → 导出清单 | 唯一准入通道。导出清单不接受手工添加，只接受质量门的 ACTIVE 判定 |
| 台账真相源 | 联机库 `universe_membership` 表是可查询真相源；湖内 artifact 是它的内容寻址快照。两者不一致时以库为准并重新发布 |
| 下游 | `F003` 读 artifact 做横截面 PIT 掩码；`F007` 的 ResearchSnapshot 按显式 digest 引用。两者都不直连库 |

## 3. 数据模型与 Migration

**新表 `universe_membership`（TimescaleDB，只追加）**

| 列 | 说明 |
|---|---|
| `exchange` / `market_type` / `db_symbol` / `lake_pair` | 与 `symbol_map` 同一映射键（F002-D010：`(exchange, market_type, db_symbol)`） |
| `valid_from` / `valid_to` | 成员区间（UTC）；`valid_to IS NULL` = 当前有效 |
| `reason` | 仅可交易期事实：`listed` / `delisted` / `initial_seed`（准入/隔离原因码归质量门判定记录，不进台账） |
| `universe_id` | 触发本次变更的 `UniverseDef` 内容摘要 |
| `ingested_at` | 采集时间，支撑 bitemporal 语义与"何时知道的"审计 |

约束（追加语义，2026-09-19 实现期定稿）：**只追加的状态迁移行**——同一 pair 的 `valid_from` 严格递增（append 顺序即时间序），**没有 UPDATE / DELETE 路径**（数据库触发器 + 应用层单写封装双保险）。台账的「可交易区间」由行**派生**而不是直接存储：

- 每一行是一次状态迁移，`reason ∈ {listed, delisted, initial_seed}` 是迁移后的状态；
- `valid_to` 为空表示该状态开放；非空时用于一次性表达已闭合的历史区间（例如入库时已退市的 `initial_seed`）；
- **派生规则**：同一 pair 按 `valid_from` 升序，第 i 行的区间 = `[valid_from_i, valid_to_i ?? valid_from_{i+1} ?? ∞)`；`delisted` 行本身不贡献可交易区间（它只终止前一行）；
- `universe_at(T)`（库侧）= 「`valid_from <= T` 的最后一个状态是 `listed`/`initial_seed`」；artifact 内是派生后的**并集区间**，消费方的半开区间并集判定与库侧逐点一致。

这样「退市」= 追加一行 `delisted`（而不是改写旧行的 `valid_to`），历史行永远可审计；**区间不重叠**由「同一 pair 的 `valid_from` 严格递增」保证（与 `DR-002` 是同一约束的两种说法）。`universe_quality_verdicts` 同族：准入判定也只追加，最新一条（按 `judged_at, id`）是当前准入状态。

**Migration**：一个前向迁移 `db/migrations/005_universe_membership.sql`（现有编号止于 `004_`）建表 + 索引 `(lake_pair, valid_from)`；无回滚数据（新表）。`tools/apply_migrations.py` 有两条硬约束，迁移必须满足：**幂等**（`CREATE TABLE/INDEX IF NOT EXISTS`、`CREATE OR REPLACE FUNCTION`）与**不得含非事务语句**（`CREATE INDEX CONCURRENTLY` / `VACUUM` / `ALTER SYSTEM` 会被 `assert_transactional` 拦下）；整文件在单事务内执行，触发器与触发器函数是事务内合法语句、可用。首次迁移后必须立即执行"现有 6 对补台账"（`reason=initial_seed`，`valid_from` 取各自实际数据起点），否则老 pair 在 PIT 查询里会凭空全程存在。

**`UniverseDef`（内容寻址 JSON）**：`universe_id` / `criteria` / `snapshot_at`（交易所数据快照时间）/ `candidates[]`（含逐候选筛选指标与排除者的排除原因）/ `frozen_at` / `frozen_by`。`universe_id = sha256(canonical_json(criteria + snapshot_at + candidates))`——同口径同快照必然同 id。

`criteria` 字段（Q-001 裁决值）：

| 字段 | 值 | 说明 |
|---|---|---|
| `exchange` / `market_type` | `binance` / `perp` | **排名市场**（USDⓈ-M 永续的流动性最可比），不是湖内命名空间——见下方「湖内命名空间」 |
| `turnover_lookback_days` | 90 | 成交额统计窗口 |
| `turnover_rank_top_n` | 40 | **按排名取前 N，不设绝对金额阈值**——绝对阈值随市场周期漂移，产出规模不可控 |
| `min_listed_days` | 180 | 不要求满窗：要求上线满 2 年等于只选活过两年的币，是幸存者偏差的另一张脸 |
| `exclude_rules` | 稳定币对 / 杠杆代币 / 指数篮子类合约 | 横截面 rank 里的常数噪声与结构性重复 |

批次：`candidates` 按成交额排名有序，批 1 取前 30（含现有 6 对），批 2 取第 31–40。批次只影响回填与准入的时序，不影响 `universe_id`——冻结的是完整的 40 对定义。

**湖内命名空间（2026-09-19 实现期定稿）**：口径里的 `market_type=perp` 只决定**排名用哪个市场的成交额**；湖内 pair 名由**数据集自己的 `market_type`** 决定——`ohlcv_1m` 是 `spot`（`BTC-USDT`），`derivatives_*` 是 `perp`（`BTC-USDT-PERP`）。因此：

- 候选的 `lake_pair` 取研究数据集的命名空间（`spot`，`BTC-USDT`）；
- **准入时按同一 `db_symbol` 同源写两条命名空间**的台账行（`spot` + `perp`，同一 `valid_from`／`reason`）——`F003` 的张量掩码按 `lake_pair` 过滤（`generators/lake_tensor.py` 用 `spec.market_type` 映射后再 `isin(universe_at(T))`），少写一条就会让对应数据集的分区被整片掩掉；
- 导出过滤落到**被导出 dataset 的 `market_type`** 上：`export_admitted(conn, at, market_type=spec.market_type)` 以 `db_symbol` 为桥——准入判定按贸易符号，台账按命名空间。

**湖内 artifact**：`lake/_metadata/universes/<digest>.json`，**canonical JSON**，schema 冻结为

```json
{"schema_version": 1, "members": [{"lake_pair": "BTC-USDT", "valid_from": "2026-01-01T00:00:00Z", "valid_to": null}]}
```

- 顶层键**严格等于** `{schema_version, members}`，成员键**严格等于** `{lake_pair, valid_from, valid_to}`——多一个键即判非法，不做宽松忽略；
- `members` 按 `(lake_pair, valid_from)` 排序；对象键按字典序；UTF-8、无多余空白；时间为 UTC ISO-8601，`valid_to: null` 表示当前有效；
- **canonical 字节规则（自包含，不依赖未并入 main 的模块）**：`canonical_bytes = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")`，无尾随换行；值只允许 `str` / `int` / `bool` / `null` / 数组 / 对象，**不得出现浮点数**（消费方对非规范数值直接拒绝）；
- `digest = "sha256:" + sha256(canonical_bytes).hexdigest()`，**前缀进文件名**（main 上已实现的 `data_bridge/symbol_map.py::content_digest` 用的是同一 `sha256:` 前缀约定）。消费方加载时会**用解析后的文档重新规范化并重算 digest**与显式引用比对，所以上述规则必须与消费方逐字节一致——规范来源是 F003 的 `factor_factory/canonical.py::canonical_json_bytes`（当前只在 `feat/F003-alphagen-vendor` 上），本 feature 按其规则在 `universe/artifact.py` 内自实现，不 import 该模块；
- 同一 `lake_pair` 的区间不得重叠：库侧由区间约束保证，artifact 侧由消费方强制（重叠区间报 `overlapping validity windows`）；`(lake_pair, valid_from)` 排序是发布侧自证纪律，消费方不校验；
- 已有同 digest 文件必须逐字节一致，冲突即报错而非覆盖。

**artifact 只承载最小 PIT 投影**：`reason` / `universe_id` / `ingested_at` / `exchange` / `market_type` / `db_symbol` 留在联机库表，不进 artifact——它们不参与 `universe_at(T)` 判定，放进来只会让 digest 随审计噪声变化，使 ResearchSnapshot 身份无谓漂移。

**因此 artifact 不与 `symbol_map` 同构**（后者是 CSV 表格），不共用其序列化原语；但沿用同一套发布纪律：原子创建、同 digest 必须逐字节一致、只按显式 digest 读取。该 schema 与下游消费者 `src/alphamill/factor_factory/generators/universe.py`（`load_explicit_universe`）逐字段一致——实现完成后必须能被它直接加载，这是 `AC-009` 的断言之一。

> **开工前检查补记（2026-09-19）**：上述消费者当前只存在于 `feat/F003-alphagen-vendor`（F003 仍 `developing`、未并入 main），main 上 `src/alphamill/factor_factory/` 只有 `__init__.py` 与 `bench/`。因此 `AC-009` 的「下游可加载」断言在 F003 落地前**物理上不可执行**：F008 侧先由 `AC-013`（`tests/unit/test_f008_artifact.py`）锁死同一 schema 的键集合、排序与 `sha256:` digest 规则，跨消费者那条断言按项目 SOP「已知缺口显式标记」写成 `xfail(strict=True)` 并注明原因是该分支依赖，F003 并入 main 后 XPASS 转红、强制摘除标记并真跑。依赖登记见 `tasks.md` §4。

**导出清单（无独立实体）**：定义为「台账中在本次导出窗口终点 `window_end` 可交易 ∩ 质量门判定为 ACTIVE」的 pair 集合（增量与全量同口径），由 `universe_membership` 与质量门判定记录联合导出，并在**被导出 dataset 的 `market_type` 命名空间**上取交集（`export_admitted(conn, window_end, market_type=...)`；准入按 `db_symbol` 判定，命名空间按台账行区分）。落地方式：`partitions.lake_pairs_map(conn, market_type, admitted: set[str] | None = None)` 增加可选准入集合参数，`None` 时保持现行为——F002 既有测试与 manifest/对账/修订语义一律不变。**过滤必须同时作用于单元格发现**（开工前检查补记 2026-09-19）：`discover_cells()` 产出的 `(exchange, symbol, date)` 单元格要在映射 `lake_pair` 之前就按准入集合剔除——现行 `produce_partitions()` 对 `lake_pairs.get(...)` 返回 `None` 的单元格直接抛 `DataBridgeError`，只过滤 `lake_pairs_map` 会把「未准入」变成「导出失败」而不是「不导出」。剔除后的单元格既不产出分区，也不进 manifest 的 `pairs`；未准入 pair 的在湖分区按 F002 既有语义留给下个版本继承，不做删除。`symbol_map` **不**参与该过滤，保持全量（回填写库即产生新 digest，属预期；旧 digest 仍可按引用读取）。

**`BackfillRun`（JSON，落 `reports/backfill/<run_id>/`）**：`run_id` / `universe_id` / `pairs[]` / `window` / 限速参数 / 逐 pair `{rows, last_cursor, status, retries, error}` / `hostname` / 起止时间。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

调用形态：`python -m alphamill.data_bridge.universe <子命令> [选项]`（`universe/__main__.py`；仓库统一用 `python -m` 模块入口，见 §2 边界规则）。

| 子命令 | 作用 | 拒绝条件（非零退出） |
|---|---|---|
| `discover --criteria <file>` | 拉 Binance 行情按口径（排名前 N + 上线天数 + 排除规则）筛候选，产出 `UniverseDef` 草稿 | 口径缺字段；交易所不可达 |
| `freeze --def <universe_id> --confirm` | 人工确认后冻结定义 | 缺 `--confirm`；候选清单为空 |
| `backfill --universe <universe_id> [--batch 1\|2] [--pairs ...]` | 分批回填（批次按成交额排名切分） | 定义未冻结；窗口非法；磁盘余量不足 |
| `gate --universe <universe_id> [--pairs ...]` | 跑质量门并登记准入 | 回填未完成的 pair 直接判 `INCOMPLETE` |
| `show --universe <id> \| --at <T>` | 打印定义 / 某时点成员集合 | 定义或 digest 不存在 |

上表九类拒绝条件是 `AC-012` 的完整覆盖清单；拒绝原因必须可区分（各自独立的退出码或错误码，不共用一句笼统报错）。

关键读接口：`universe_at(T, digest) -> set[lake_pair]`，语义为 `valid_from <= T AND (valid_to IS NULL OR T < valid_to)`（左闭右开，与 F002 reader 的时间区间语义一致）。

### Event / Trace Contract

append-only JSONL：

- `universe.member_changed`：`lake_pair`、`direction`（in/out）、`effective_at`、`reason`、`universe_id`、`line`（`tradability` = 台账可交易期变更 / `admission` = 准入状态变更，见 spec TR-001）；
- `backfill.progress`：`run_id`、`lake_pair`、`rows`、`cursor`、`elapsed`；
- `backfill.failed`：`run_id`、`lake_pair`、`error_class`、`retries`、`last_cursor`。

幂等键：成员事件用 `(lake_pair, effective_at, direction, line)`；回填事件用 `(run_id, lake_pair, cursor)`。

## 5. Runtime、Workflow 与并发

```text
discover → （人工确认）→ freeze → backfill（长跑，可中断）→ gate → 台账追加 + artifact 发布 → F002 导出
```

- **限速与退避**：每个 pair 的请求间隔由配置给出，命中限流错误后指数退避并计数；超过重试上限即该 pair 标 `failed` 并保留 `last_cursor`，其他 pair 继续；**任何情况下不因失败而提高速率**；
- **断点续跑**：以 `(lake_pair, last_cursor)` 为断点，写库走既有幂等 upsert（F001 已验证"二次执行行数不变"），因此重跑天然安全；
- **并发**：pair 间可有限并发（受限速预算约束），单 pair 内严格串行；与 `data_bridge` 导出**串行**（架构 §7.1：导出与训练串行，回填同理占用同一库）；
- **长跑可观测**：进度事件按 pair 落盘，`show` 可随时查看；中断后重跑先读 `BackfillRun` 恢复断点；
- **质量门执行点**：在 pair 回填完成后单独执行，不混在回填循环里——门禁与生产数据的耦合越松越好；
- **台账写入时序**：先写库（`universe_membership` 追加）→ 再发布 artifact → 最后才把 pair 纳入导出清单（即写入准入记录，使其进入 `admitted` 集合）。顺序反了会出现"导出清单里有、台账里没有"的 pair。

## 6. UI 与可观测性

UI：不适用（只读呈现归 `F005`，ADR-0005：不新增口径载体）。

可观测性：

- 回填进度以事件 + `BackfillRun` 落盘，`python -m alphamill.data_bridge.universe show` 为诊断入口；
- 质量门判定记录逐 pair 保留（通过与失败同样保留），含各项指标值、阈值与原因码；
- 容量指标（磁盘占用、全量导出耗时、NAS 备份时长）在扩容后实测记录，与 F002 的 6 对基线（631 万行 / 全量 3m48s / NAS 8823 分区文件）并列对照；
- 不新增 Grafana 看板：长跑进度看 CLI 与事件文件即可。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：定义未冻结 → 启动期拒绝；磁盘余量不足 → 启动期拒绝（避免跑到一半写满盘）；限流 → 退避重试；超重试上限 → 该 pair `failed`；质量门任一项失败 → `QUARANTINED` 并记原因码；回填未完成就跑门禁 → `INCOMPLETE`，不判 PASS。
- **重启与恢复**：回填幂等 + 断点，直接重跑；台账为只追加，崩溃不会留下半改写的历史；artifact 发布用"写临时文件 → fsync → rename"，同 digest 已存在则校验逐字节一致而非覆盖。
- **权限 / 凭据边界**：只读 Binance 公开行情，不需要 API key（如需更高频配额再评估，届时凭据走 `.env`，不入库）；写路径限于 TimescaleDB、`lake/_metadata/universes/` 与 `reports/backfill/`。
- **兼容**：湖内既有五个 dataset 的 manifest 与 reader 行为完全不变；新 pair 只是让 `pairs` 列表变长、分区变多。`symbol_map` 会因新 pair 产生新 digest——这是预期行为，旧 digest 必须仍可按引用读取（F002 已保证）。
- **与 F002 全量导出收缩守卫的交互（开工前检查补记 2026-09-19）**：`export_policy.guard_full_shrink` 在「分区数跌破基线 50%」或「空快照」时拒绝发布全量导出，唯一放行通道是 `--allow-shrink`，放行后由调用方在 manifest 记既有字段 `shrink_confirmed`（F002-R3-02）。F008 的正常生命周期（退市移出、质量门隔离、跌出阈值落选）本身就会让分区数收缩，**准入过滤还会额外减少单元格**，因此扩容后的全量导出（`T023`）可能命中该守卫：处置是**按 F002 既有语义显式用 `--allow-shrink` 并在容量报告里记录原因与 `shrink_confirmed`**，不是放宽守卫；窗口截断（`window_end` 传错）依然任何情况下都拒绝。此处不新增 manifest 字段、不改判定阈值，`symbol_map` 全量与 `pairs` 不等属预期。
- **迁移前瞻**：执行机后续整体迁到 `qiaozhi-lab`，回填产物与台账随库/湖一起搬；容量与耗时基线届时重测（`docs/SOP.md` §3）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f008_discover.py` | 同口径同快照两次发现得同候选与同 universe_id；逐候选指标入档 |
| `AC-002` | unit | `tests/unit/test_f008_universe_def.py` | 未冻结驱动回填被拒；成员增删产生新版本，旧版本只读 |
| `AC-003` | integration | `tests/integration/test_f008_backfill.py` | 中断后重跑从断点继续、无重复行、行数符合预期 |
| `AC-004` | unit | `tests/unit/test_f008_rate_limit.py` | 限流触发指数退避、重试有上限、速率不因失败提高 |
| `AC-005` | integration | `tests/integration/test_f008_quality_gate.py` | 缺失率超限 / 边界未闭合 / 重复主键 / 连续聚合不一致四类 fixture 均被拦并各记原因码；重复主键 fixture 用无主键 scratch 源表承载 |
| `AC-006` | unit | `tests/unit/test_f008_quality_gate_window.py` | 上线晚于窗口起点的 pair 按实际可得窗口算缺失率，不误判 |
| `AC-007` | unit | `tests/unit/test_f008_membership.py` | 上市/退市/中途进出 fixture 上 universe_at(T) 各时点正确 |
| `AC-008` | unit | `tests/unit/test_f008_membership.py` | 原地改写历史区间被拒；退出记录保留历史数据 |
| `AC-009` | integration | `tests/integration/test_f008_export_integration.py` | 同内容同 digest 且逐字节一致；内容变化得新 digest 且旧 digest 仍可读；产物可被 `load_explicit_universe` 直接加载 |
| `AC-010` | integration | `tests/integration/test_f008_backfill.py` | 成员变更与回填事件可按 run/pair 查询；运行记录带 hostname |
| `AC-011` | integration | `tests/integration/test_f008_capacity_report.py` | 扩容后磁盘、全量导出耗时、NAS 备份时长实测入档并与 6 对基线对照 |
| `AC-012` | unit | `tests/unit/test_f008_cli_contract.py` | 五个子命令与 §4 的九类启动期拒绝各以可区分的非零原因退出 |
| `AC-013` | unit | `tests/unit/test_f008_artifact.py` | artifact 与 `BackfillRun` 均带 `schema_version`；版本不符或出现未知键即拒绝加载，不做宽松忽略 |

真实环境场景：全量回填（1~2 周 wall-clock，owner 主导）、扩容后首次全量导出与 NAS 备份实测，全部在执行机 `qiaozhi-lt` 执行并记录 hostname；开发机上这些用例跳过属预期，不算证据也不算失败。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 台账是 dataset 还是 artifact | **artifact**，内容寻址 | ADR-0007 与 `F007` IR-002 都按「universe/calendar artifact」定义；元数据按日分区没有意义 | 不进 dataset registry，不参与 data_version 修订语义 |
| artifact 用 JSON 还是 CSV | **canonical JSON**，只含最小 PIT 投影（§3） | CSV 无处安放 `IR-003` 的 `schema_version`；`valid_to` 可空在 CSV 里只能靠空串约定；calendar 已是 JSON，两者 digest 要组合；且 `generators/universe.py` 已按 JSON schema 落地并有集成测试 | 裁决 2026-09-19（owner）；联动修订 ADR-0007、架构 §4.3、`F007` DR-006/design §4 与 `tools/check_doc_consistency.py` 的路径断言 |
| 台账区间 vs 准入状态 | **拆成两条线**：台账记可交易期，准入状态归质量门判定记录 | 准入时点语义会让 `universe_at(T)` 在扩容日前返回空集，PIT 掩码失效 | 裁决 2026-09-19（owner）；§3 表的 `reason` 收敛为 `listed`/`delisted`/`initial_seed` |
| 导出准入怎么落地 | `lake_pairs_map` 加可选 `admitted` 参数，默认 `None` 保持现行为；`symbol_map` 不过滤 | F002 无清单实体，pair 由 `SELECT DISTINCT` 派生；改输入端不触碰 manifest/对账/修订语义 | 裁决 2026-09-19（owner）；`symbol_map` 与导出清单允许不等，须在实现期测试中显式断言 |
| 准入过滤具体落在哪一行 | `lake_pairs_map(admitted=…)` **加** `produce_partitions` 的单元格级剔除，并由 `exporter.export_dataset/_export_one` 透传；三者缺一不过滤或直接报错 | 开工前检查（2026-09-19）：`lake_pairs_map` 的生产调用点唯一（`exporter.py:160`），只加参数不接线等于空转；而 `produce_partitions` 对映射缺失的单元格是 `raise DataBridgeError`，只过滤 map 会把「不导出」变成「导出失败」 | 落在 T017；`admitted=None` 时三条路径行为与 F002 现状逐字节一致 |
| CLI 入口形态 | `python -m alphamill.data_bridge.universe`（`universe/__main__.py`），**不新增 `[project.scripts]`** | 开工前检查（2026-09-19）：main 的 `pyproject.toml` 无该表，F003 正在同一插入点加 `alphamill-generate`；同表同点各自改动制造文本冲突，entry point 还需 editable 重装才生效 | 落地于 T018；任务与验收命令一律写 `python -m` 全称 |
| canonical 字节规范的来源 | 在 `universe/artifact.py` 内**自实现**（规则见 §3），不 import F003 的 `factor_factory/canonical.py` | 该模块当前只在 `feat/F003-alphagen-vendor` 上；消费方是「解析后重新规范化再重算 digest」，所以字节规则必须一致但不必共享代码 | 依赖登记见 `tasks.md` §4；F003 并入 main 后由 `AC-009` 的跨消费者断言（当前 `xfail(strict=True)`）真跑复核 |
| 与 F002 全量导出收缩守卫的交互 | 命中时按 F002 既有语义用 `--allow-shrink` 人工确认并在 manifest 记既有字段 `shrink_confirmed`；**不放宽守卫** | F008 的退市/隔离/落选天然收缩分区数，准入过滤再减一层；守卫的立意（防空库误发布）依然成立 | 见 §7；容量报告（T023）须记录该确认 |
| 台账真相源放哪 | 联机库表为可查询真相源，湖内 artifact 为其快照 | 区间查询与追加需要 SQL；研究侧需要不可变引用 | 两者不一致时以库为准并重新发布 |
| 发现脚本 | 按 Binance USDⓈ-M 重写，不复用 OKX 脚本 | F001 事故后数据路线已改 Binance | 同步修订 integration §1.3 |
| 质量门阈值 | 复用 F001 口径（缺失率 ≤1%、边界闭合、连续聚合按桶重算精确一致），可配但默认不放宽 | ADR-0003；换阈值会让新老数据不可比 | 阈值变更须显式改配置并记理由 |
| 退市 pair | 保留历史数据，只写 `valid_to` 并移出导出清单（产品层理由见 `spec.md` §7） | 技术侧含义：`membership.py` 无 DELETE 路径 | — |
| 现有 6 对 | 首次台账发布即补 `initial_seed` 记录 | 否则老 pair 在 PIT 查询里凭空全程存在 | 与建表迁移同批完成 |
| `historical_backfill.py` 的行数豁免 | 本 feature 泛化它，同时从 `docs/SOP.md` 豁免表移除 | 豁免的解除期限本就写的是「F002 泛化阶段」，实际泛化发生在这里 | 若本轮未完成泛化则必须显式续期，不得静默留着 |
| 规模与阈值（Q-001 裁决） | 见 `spec.md` §7 同名条目（产品层取舍的唯一拥有者），本文不复述 | — | `criteria` 的落地字段见 §3 |
| 回填 1~2 周且依赖外部 | owner 主导，失败 pair 可单独重跑；批 2 失败不影响批 1 的准入 | PRD FR1.5 已把它定性为独立工作流 | 分批降低了"全跑完才有产出"的风险 |
| 扩容后导出/备份变慢 | 实测记录并与基线对照，不预设没问题 | F002 基线可比 | 超出可接受范围再评估分片导出 |

## 10. 待确认设计问题

- [x] DQ-001: 台账的不可改写用什么强制？ — 决策：应用层单写封装为主（所有写入只经 `membership.py` 的追加接口），并在落地任务中评估是否加数据库触发器兜底；二选一的结论写进 tasks，不留悬空
- [x] DQ-002: 回填并发度怎么定？ — 决策：pair 间有限并发但总请求速率受同一限速预算约束，单 pair 内严格串行；并发度可配，默认保守值，实测后再调
- [x] DQ-003: 质量门在回填循环内还是外？ — 决策：外——pair 回填完成后单独执行，避免门禁与生产数据写入耦合，也便于失败后单独重跑门禁
- [x] DQ-004: 缺失率对"上线晚"的 pair 怎么算？ — 决策：按该 pair 的实际可得窗口（真实上市时间到回填终点）计算，而不是按全局窗口；真实上市时间同时写入台账 `valid_from`
- [x] DQ-005: 写入时序如何避免"导出清单有、台账没有"？ — 决策：固定为 库追加 → artifact 发布 → 纳入导出清单 三步顺序，任一步失败则不进入下一步
