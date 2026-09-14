---
kind: feature
id: F008
version: "0.2"
related_features: [F001, F002, F003, F007]
topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
doc_kind: design
created: 2026-09-14
updated: 2026-09-14
---

# F008：宇宙扩容与 point-in-time 宇宙台账 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

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

四段式流水线：**发现 → 冻结 → 回填 → 质量门 → 台账发布**。发现从 Binance 公开行情按口径筛候选；人工确认后冻结为内容寻址的 `UniverseDef`；回填复用 F001 的 `historical_backfill.py`，外面套一层可续跑的批次编排；每个 pair 回填完成后跑质量门（复用 `tools/f001_backfill_report.py` 的口径，参数化到多 pair）；过门的 pair 写入联机库的 `universe_membership` 台账并进 F002 导出清单，台账再以 `symbol_map` 同构的方式发布为湖内内容寻址 artifact。

- 前端：不适用
- 后端 / API：新增 `src/alphamill/data_bridge/universe/` 子包与 `alphamill-universe` CLI；`collector/historical_backfill.py` 由脚本升级为可被编排调用（同时解除其 350 行豁免）
- 存储 / Migration：新增 TimescaleDB 表 `universe_membership`（只追加）；新增湖元数据目录 `lake/_metadata/universes/<digest>.csv`
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
│   ├── artifact.py             #   台账 canonical 序列化与 digest 发布（symbol_map 同构）
│   ├── quality_gate.py         #   新 pair 准入门（复用 F001 完整性口径）
│   └── backfill_runner.py      #   批次编排：限速 / 退避 / 断点 / 逐 pair 进度
├── collector/historical_backfill.py   # 由脚本改为可编排调用（解除行数豁免）
└── cli.py                      # 既有 CLI 扩子命令，或新增 alphamill-universe 入口
```

边界规则：

| 边界 | 规则 |
|---|---|
| universe → F002 核心 | 单向依赖：`universe/` 调用 `symbol_map`/`paths`/`registry`，**不反向修改** exporter/manifest/reader 的既有语义 |
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
| `reason` | `listed` / `delisted` / `liquidity_in` / `liquidity_out` / `quality_fail` / `initial_seed` |
| `universe_id` | 触发本次变更的 `UniverseDef` 内容摘要 |
| `ingested_at` | 采集时间，支撑 bitemporal 语义与"何时知道的"审计 |

约束：区间不重叠（同一 pair 的 `valid_from` 严格递增）；**没有 UPDATE 路径**——退出用写 `valid_to` 的追加记录表达，历史行不可改写（数据库层用触发器或应用层单写封装，落地任务里择一并写明）。

**Migration**：一个前向迁移建表 + 索引 `(lake_pair, valid_from)`；无回滚数据（新表）。首次迁移后必须立即执行"现有 6 对补台账"（`reason=initial_seed`，`valid_from` 取各自实际数据起点），否则老 pair 在 PIT 查询里会凭空全程存在。

**`UniverseDef`（内容寻址 JSON）**：`universe_id` / `criteria` / `snapshot_at`（交易所数据快照时间）/ `candidates[]`（含逐候选筛选指标与排除者的排除原因）/ `frozen_at` / `frozen_by`。`universe_id = sha256(canonical_json(criteria + snapshot_at + candidates))`——同口径同快照必然同 id。

`criteria` 字段（Q-001 裁决值）：

| 字段 | 值 | 说明 |
|---|---|---|
| `exchange` / `market_type` | `binance` / `perp` | F001 事故后的数据路线 |
| `turnover_lookback_days` | 90 | 成交额统计窗口 |
| `turnover_rank_top_n` | 40 | **按排名取前 N，不设绝对金额阈值**——绝对阈值随市场周期漂移，产出规模不可控 |
| `min_listed_days` | 180 | 不要求满窗：要求上线满 2 年等于只选活过两年的币，是幸存者偏差的另一张脸 |
| `exclude_rules` | 稳定币对 / 杠杆代币 / 指数篮子类合约 | 横截面 rank 里的常数噪声与结构性重复 |

批次：`candidates` 按成交额排名有序，批 1 取前 30（含现有 6 对），批 2 取第 31–40。批次只影响回填与准入的时序，不影响 `universe_id`——冻结的是完整的 40 对定义。

**湖内 artifact**：`lake/_metadata/universes/<digest>.csv`，canonical 格式冻结（固定列序、按 `(lake_pair, valid_from)` 排序、UTF-8、LF、固定表头），digest 为 canonical 字节的 SHA-256；已有同 digest 文件必须逐字节一致（与 `symbol_map` 完全同构，实现可共用其发布原语）。

**`BackfillRun`（JSON，落 `reports/backfill/<run_id>/`）**：`run_id` / `universe_id` / `pairs[]` / `window` / 限速参数 / 逐 pair `{rows, last_cursor, status, retries, error}` / `hostname` / 起止时间。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 子命令 | 作用 | 拒绝条件（非零退出） |
|---|---|---|
| `discover --criteria <file>` | 拉 Binance 行情按口径（排名前 N + 上线天数 + 排除规则）筛候选，产出 `UniverseDef` 草稿 | 口径缺字段；交易所不可达 |
| `freeze --def <universe_id> --confirm` | 人工确认后冻结定义 | 缺 `--confirm`；候选清单为空 |
| `backfill --universe <universe_id> [--batch 1\|2] [--pairs ...]` | 分批回填（批次按成交额排名切分） | 定义未冻结；窗口非法；磁盘余量不足 |
| `gate --universe <universe_id> [--pairs ...]` | 跑质量门并登记准入 | 回填未完成的 pair 直接判 `INCOMPLETE` |
| `show --universe <id> \| --at <T>` | 打印定义 / 某时点成员集合 | 定义或 digest 不存在 |

关键读接口：`universe_at(T, digest) -> set[lake_pair]`，语义为 `valid_from <= T AND (valid_to IS NULL OR T < valid_to)`（左闭右开，与 F002 reader 的时间区间语义一致）。

### Event / Trace Contract

append-only JSONL：

- `universe.member_changed`：`lake_pair`、`direction`（in/out）、`effective_at`、`reason`、`universe_id`；
- `backfill.progress`：`run_id`、`lake_pair`、`rows`、`cursor`、`elapsed`；
- `backfill.failed`：`run_id`、`lake_pair`、`error_class`、`retries`、`last_cursor`。

幂等键：成员事件用 `(lake_pair, effective_at, direction)`；回填事件用 `(run_id, lake_pair, cursor)`。

## 5. Runtime、Workflow 与并发

```text
discover → （人工确认）→ freeze → backfill（长跑，可中断）→ gate → 台账追加 + artifact 发布 → F002 导出
```

- **限速与退避**：每个 pair 的请求间隔由配置给出，命中限流错误后指数退避并计数；超过重试上限即该 pair 标 `failed` 并保留 `last_cursor`，其他 pair 继续；**任何情况下不因失败而提高速率**；
- **断点续跑**：以 `(lake_pair, last_cursor)` 为断点，写库走既有幂等 upsert（F001 已验证"二次执行行数不变"），因此重跑天然安全；
- **并发**：pair 间可有限并发（受限速预算约束），单 pair 内严格串行；与 `data_bridge` 导出**串行**（架构 §7.1：导出与训练串行，回填同理占用同一库）；
- **长跑可观测**：进度事件按 pair 落盘，`show` 可随时查看；中断后重跑先读 `BackfillRun` 恢复断点；
- **质量门执行点**：在 pair 回填完成后单独执行，不混在回填循环里——门禁与生产数据的耦合越松越好；
- **台账写入时序**：先写库（`universe_membership` 追加）→ 再发布 artifact → 最后才把 pair 纳入导出清单。顺序反了会出现"导出清单里有、台账里没有"的 pair。

## 6. UI 与可观测性

UI：不适用（只读呈现归 `F005`，ADR-0005：不新增口径载体）。

可观测性：

- 回填进度以事件 + `BackfillRun` 落盘，`alphamill-universe show` 为诊断入口；
- 质量门判定记录逐 pair 保留（通过与失败同样保留），含各项指标值、阈值与原因码；
- 容量指标（磁盘占用、全量导出耗时、NAS 备份时长）在扩容后实测记录，与 F002 的 6 对基线（631 万行 / 全量 3m48s / NAS 8823 分区文件）并列对照；
- 不新增 Grafana 看板：长跑进度看 CLI 与事件文件即可。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：定义未冻结 → 启动期拒绝；磁盘余量不足 → 启动期拒绝（避免跑到一半写满盘）；限流 → 退避重试；超重试上限 → 该 pair `failed`；质量门任一项失败 → `QUARANTINED` 并记原因码；回填未完成就跑门禁 → `INCOMPLETE`，不判 PASS。
- **重启与恢复**：回填幂等 + 断点，直接重跑；台账为只追加，崩溃不会留下半改写的历史；artifact 发布用"写临时文件 → fsync → rename"，同 digest 已存在则校验逐字节一致而非覆盖。
- **权限 / 凭据边界**：只读 Binance 公开行情，不需要 API key（如需更高频配额再评估，届时凭据走 `.env`，不入库）；写路径限于 TimescaleDB、`lake/_metadata/universes/` 与 `reports/backfill/`。
- **兼容**：湖内既有五个 dataset 的 manifest 与 reader 行为完全不变；新 pair 只是让 `pairs` 列表变长、分区变多。`symbol_map` 会因新 pair 产生新 digest——这是预期行为，旧 digest 必须仍可按引用读取（F002 已保证）。
- **迁移前瞻**：执行机后续整体迁到 `qiaozhi-lab`，回填产物与台账随库/湖一起搬；容量与耗时基线届时重测（`docs/SOP.md` §3）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f008_discover.py` | 同口径同快照两次发现得同候选与同 universe_id；逐候选指标入档 |
| `AC-002` | unit | `tests/unit/test_f008_universe_def.py` | 未冻结驱动回填被拒；成员增删产生新版本，旧版本只读 |
| `AC-003` | integration | `tests/integration/test_f008_backfill.py` | 中断后重跑从断点继续、无重复行、行数符合预期 |
| `AC-004` | unit | `tests/unit/test_f008_rate_limit.py` | 限流触发指数退避、重试有上限、速率不因失败提高 |
| `AC-005` | integration | `tests/integration/test_f008_quality_gate.py` | 缺失率超限 / 边界未闭合 / 连续聚合不一致三类 fixture 均被拦并各记原因码 |
| `AC-006` | unit | `tests/unit/test_f008_quality_gate_window.py` | 上线晚于窗口起点的 pair 按实际可得窗口算缺失率，不误判 |
| `AC-007` | unit | `tests/unit/test_f008_membership.py` | 上市/退市/中途进出 fixture 上 universe_at(T) 各时点正确 |
| `AC-008` | unit | `tests/unit/test_f008_membership.py` | 原地改写历史区间被拒；退出记录保留历史数据 |
| `AC-009` | integration | `tests/integration/test_f008_export_integration.py` | 同内容同 digest 且逐字节一致；内容变化得新 digest 且旧 digest 仍可读 |
| `AC-010` | integration | `tests/integration/test_f008_backfill.py` | 成员变更与回填事件可按 run/pair 查询；运行记录带 hostname |
| `AC-011` | integration | `tests/integration/test_f008_capacity_report.py` | 扩容后磁盘、全量导出耗时、NAS 备份时长实测入档并与 6 对基线对照 |

真实环境场景：全量回填（1~2 周 wall-clock，owner 主导）、扩容后首次全量导出与 NAS 备份实测，全部在执行机 `qiaozhi-lt` 执行并记录 hostname；开发机上这些用例跳过属预期，不算证据也不算失败。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 台账是 dataset 还是 artifact | **artifact**，与 `symbol_map` 同构内容寻址 | ADR-0007 与 `F007` IR-002 都按「universe/calendar artifact」定义；元数据按日分区没有意义 | 发布原语与 `symbol_map` 共用，减少一套实现 |
| 台账真相源放哪 | 联机库表为可查询真相源，湖内 artifact 为其快照 | 区间查询与追加需要 SQL；研究侧需要不可变引用 | 两者不一致时以库为准并重新发布 |
| 发现脚本 | 按 Binance USDⓈ-M 重写，不复用 OKX 脚本 | F001 事故后数据路线已改 Binance | 同步修订 integration §1.3 |
| 质量门阈值 | 复用 F001 口径（缺失率 ≤1%、边界闭合、连续聚合按桶重算精确一致），可配但默认不放宽 | ADR-0003；换阈值会让新老数据不可比 | 阈值变更须显式改配置并记理由 |
| 退市 pair | 保留历史数据，只写 `valid_to` 并移出导出清单 | 删除即制造幸存者偏差 | — |
| 现有 6 对 | 首次台账发布即补 `initial_seed` 记录 | 否则老 pair 在 PIT 查询里凭空全程存在 | 与建表迁移同批完成 |
| `historical_backfill.py` 的行数豁免 | 本 feature 泛化它，同时从 `docs/SOP.md` 豁免表移除 | 豁免的解除期限本就写的是「F002 泛化阶段」，实际泛化发生在这里 | 若本轮未完成泛化则必须显式续期，不得静默留着 |
| 规模与阈值（Q-001 裁决） | 40 对分两批（前 30 / 第 31–40）；成交额**排名**前 N 而非绝对金额；上线 >180 天不要求满窗；排除结构性重复标的 | 噪声收益几乎全在前 30（rank 相关标准误 0.447→0.186→0.160→0.143），而导出与 NAS 成本线性且每天都付；绝对金额阈值随市场周期漂移会破坏 FR-001 的可复现性 | 批 1 过门后 `F003` 即可用；余量充足时按增量加 pair，台账天然支持 |
| 回填 1~2 周且依赖外部 | owner 主导，失败 pair 可单独重跑；批 2 失败不影响批 1 的准入 | PRD FR1.5 已把它定性为独立工作流 | 分批降低了"全跑完才有产出"的风险 |
| 扩容后导出/备份变慢 | 实测记录并与基线对照，不预设没问题 | F002 基线可比 | 超出可接受范围再评估分片导出 |

## 10. 待确认设计问题

- [x] DQ-001: 台账的不可改写用什么强制？ — 决策：应用层单写封装为主（所有写入只经 `membership.py` 的追加接口），并在落地任务中评估是否加数据库触发器兜底；二选一的结论写进 tasks，不留悬空
- [x] DQ-002: 回填并发度怎么定？ — 决策：pair 间有限并发但总请求速率受同一限速预算约束，单 pair 内严格串行；并发度可配，默认保守值，实测后再调
- [x] DQ-003: 质量门在回填循环内还是外？ — 决策：外——pair 回填完成后单独执行，避免门禁与生产数据写入耦合，也便于失败后单独重跑门禁
- [x] DQ-004: 缺失率对"上线晚"的 pair 怎么算？ — 决策：按该 pair 的实际可得窗口（真实上市时间到回填终点）计算，而不是按全局窗口；真实上市时间同时写入台账 `valid_from`
- [x] DQ-005: 写入时序如何避免"导出清单有、台账没有"？ — 决策：固定为 库追加 → artifact 发布 → 纳入导出清单 三步顺序，任一步失败则不进入下一步
