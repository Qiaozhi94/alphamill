---
kind: feature
id: F002
version: "0.2"
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: tasks
created: 2026-09-12
updated: 2026-09-13
---

# F002:数据桥——Parquet 湖导出与 DuckDB 研究取数层 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源:`spec.md`。
- 技术方案与边界:`design.md`。
- 每项任务只描述一个可验证动作,并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`,不得最后统一补勾。
- `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
- 实现中若任务顺序或契约失效,先修订三件套,再继续编码。

## 1. 前置条件

- F001 已 done:TimescaleDB 数据就绪(631 万行 binance)、`lake/` 目录位与 NAS 通道已预留、调度先例(backup/snapshot timer)成立。
- 设计问题 DQ-001~003 已全部裁决；实现期仅观察 DQ-003 预先定义的升级条件，不阻塞开工(见 design §10)。

## 2. 实现任务

### Phase 1:导出器核心(ohlcv_1m 端到端)

- [x] T001 [P] (`FR-001`): pyproject 新增 `pyarrow`/`duckdb` 依赖 pin(版本范围本地验证后落定),`.venv` 安装验证 — verify: `.venv/bin/python -c "import pyarrow, duckdb"` 退出码 0
- [x] T015 (`FR-001`): `src/alphamill/data_bridge/registry.py`——dataset 只读白名单(design §3 表:源表/主键/事件时间列/分区键/数值列/允许过滤列),未登记名字抛 `UnknownDatasetError` — verify: `tests/unit/test_f002_registry.py`(五个 dataset 齐备 + 未知名字判红 + signals_log 事件时间列为 latest_candle)
- [x] T016 (`FR-002`, `AC-012`): `src/alphamill/data_bridge/digest.py`——`canonical_row_bytes()` 与流式 SHA-256 `row_digest`(design §3 规范编码),**同一函数同时喂 psycopg2 游标与 PyArrow batch** — verify: `tests/unit/test_f002_digest.py`(同数据两路输入摘要相同;单行单列改写摘要必变;两行 +x/-x 抵消式改写摘要必变——这正是 sum 口径抓不住的)
- [x] T002 (`FR-001`, `AC-011`, `AC-015`): `src/alphamill/data_bridge/manifest.py`——manifest 契约读写(架构 §4.4 字段 + status/reconcile/revision_diff/**partitions/quality/source_snapshot/value_digest** 扩展)、data_version 排序与最新 valid 解析、**partitions 完整性校验(只按清单逐项验存在/字节数/sha256,不扫目录、不要求目录全集相等,任一不符抛 ManifestIntegrityError)**、按 design §3 从 registry 投影与排序后的分区 row_digest 计算/校验 DatasetVersion `value_digest`、**增量合成算法(继承上一 valid 清单 → 按逻辑分区键替换/追加 → 重算累计量与 value_digest)** — verify: `tests/unit/test_f002_manifest.py`
- [x] T003 (`FR-001`): `src/alphamill/data_bridge/exporter.py`——ohlcv_1m 全量导出:**单个 REPEATABLE READ 只读事务**内查询 → 按 `exchange/pair/date` 写 `date=YYYY-MM-DD.rN.parquet`(写入后永不覆盖,内容变化写 rN+1)→ 先落 `lake/_staging/` 再 rename → **最后写 manifest 作为原子发布点**,含 partitions 清单与 source_snapshot;**增量游标只从上一 valid manifest 推导,不看磁盘分区**(design §3,防孤儿 .rN 造成永久漏日) — verify: 手动执行一次,`lake/ohlcv_1m/` 分区文件与 `_manifests/ohlcv_1m/<version>.json` 齐备
- [x] T004 (`FR-002`): 对账器——逐分区 `rows` + `time_min/time_max` + `row_digest`(design §3 唯一权威口径:规范编码 + 按编码字节序排序的流式 SHA-256,两侧调 `digest.py` 同一函数),不一致标记 invalid。**无降级分支**——不得退回 numeric/弱口径,性能不可接受走 spec 修订 — verify: `tests/integration/test_f002_export_reconcile.py`(AC-001/AC-002/AC-010)
- [x] T005 [P] (`FR-004`): `src/alphamill/data_bridge/symbol_map.py`——映射键 **(exchange, market_type, db_symbol)**,五列 canonical csv current 副本落 `src/alphamill/data_bridge/symbol_map.csv`(集成 §2.2 权威路径)，内容寻址副本原子发布到 `lake/_metadata/symbol_maps/<digest>.csv` 并支持按 digest 加载；spot/perp 格式按 design §4 冻结，**lake_pair 碰撞直接抛 `SymbolCollisionError`** — verify: `tests/unit/test_f002_symbol_map.py`(AC-004 + 碰撞判红 + 同 symbol 跨 spot/perp 不混淆 + 旧 digest 可重放)

### Phase 2:取数入口与 dataset 扩展

- [x] T006 (`FR-003`): `src/alphamill/data_bridge/reader.py`——DuckDB 只读取数(dataset+data_version+时间范围+pair 过滤),`ReadResult` 必须回报实际 dataset/data_version/value_digest 供 ADR-0007 snapshot builder 冻结;**返回数据前先跑 manifest 完整性校验**;`as_of=T` 同时施加 `event_time <= T` **与** `available_at <= T`(双时间轴,design §3);对 `as_of_fidelity=event_time_only` 的 dataset 默认抛 `InsufficientAsOfFidelityError`,`allow_event_time_only=True` 才放行且 `ReadResult` 如实回报;`realized_return_60m` 在 `evaluated_at > T` 时置 NULL 而非丢行;带质量旗分区默认抛 `FlaggedPartitionError`,`allow_flagged=True` 显式豁免并回报清单;invalid/缺失版本抛错;显式版本读取不受 latest 后移影响 — verify: `tests/integration/test_f002_reader.py`(AC-003/AC-008/AC-009/AC-013)
- [x] T007 (`FR-001`): 导出器扩展至衍生品三表与 signals_log(signals_log 无 exchange 维度,按日分区) — verify: AC-001 测试覆盖五 dataset
- [x] T020 (`FR-001`, `AC-014`): 中断恢复用例——构造「分区已 rename、manifest 未发布」的孤儿态,重跑增量确认不漏日且 skipped 继承正确 — verify: `tests/integration/test_f002_export_reconcile.py`
- [x] T008 [P] (`FR-005`, `AC-005`, `AC-007`): 全量校验模式——库内 vs 既有快照的分区级 diff,修订时递增 data_version 并登记 revision_diff,旧版本原样保留并验证 v1/v2 并发读取不串版 — verify: `tests/integration/test_f002_revision.py`

### Phase 3:运维化

- [x] T009 (`FR-006`): 导出 CLI 入口(`python -m alphamill.data_bridge.exporter --dataset ... --mode ...`),**退出码契约 0/1/2**(design §5) — verify: `tests/unit/test_f002_cli_contract.py`(三类结局各返回约定退出码)
- [x] T017 (`FR-006`): 增量导出 timer——`alphamill-export.{service,timer}`,每日 **02:00**,`Type=oneshot` + `Restart=on-failure` + `RestartSec=15min` + `StartLimitIntervalSec`/`StartLimitBurst=3` + **`RestartPreventExitStatus=2`** — verify: `tests/unit/test_f002_timer_contract.py`(unit 文件含上述全部指令且 OnCalendar=02:00)
- [x] T018 (`FR-006`): 全量校验 timer——`alphamill-fullexport.{service,timer}`,周日 **04:00**,指令同 T017 — verify: 同上契约测试覆盖第二组 unit
- [x] T019 (`FR-006`): 回补 F001 疏漏——`alphamill-backup.service` 注释声称「最多 3 次」却缺 `StartLimitIntervalSec`/`StartLimitBurst`,实际不生效,补齐使注释与行为一致 — verify: `tests/unit/test_backup_nas_contract.py` 增断言(两指令存在)
- [x] T010 (`FR-006`): `backup-nas.sh` lake/ 同步实测——触发备份后 NAS 端 `lake/` 与 `_manifests/` 产物齐全 — verify: NAS 端 ls 校验(AC-006)

## 3. 验证与验收任务

- [x] T011 (`FR-001`,`FR-002`,`FR-003`): 端到端验收——全量导出 → DuckDB 取数对账 → invalid 拒绝,记录全量导出耗时 — verify: `tests/integration/test_f002_export_reconcile.py` + `test_f002_reader.py` 全绿
- [x] T012 (`FR-001`..`FR-006`): 全量集成测试 + 统一质量门 — verify: `.venv/bin/python -m pytest tests/integration -q` 与 `python3 tools/verify.py` 全绿
- [x] T013: 回写 spec 验收证据、BACKLOG 状态与设计决策沉淀(DQ-003 处置结论) — verify: `python tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T015/T016 -> T002/T003/T005/T006`:依赖就绪(P0)后先落 registry 与 digest 两个契约模块。
- `T015 -> T003/T006`:投影列、分区键与双时间轴是导出与取数的共同输入。
- `T016 -> T004`:对账器直接调用 `digest.py`,不自带第二份实现。
- `T002 -> T003 -> T004`:manifest 是导出与对账的公共契约。
- `T003 -> T006`:取数测试依赖已有快照。
- `T004 -> T008`:修订 diff 复用对账器。
- `T002/T005 [P]`、`T006(依赖T003)`、`T008(依赖T004)` 分支并行。
- `T009 -> T017/T018`:timer 依赖 CLI 的退出码契约;`T019` 独立(回补 F001 backup.service),可并行。
- `T009/T010` 依赖 Phase 1-2 完成;`T011 -> T012 -> T013` 验收链顺序执行。

## 5. 明确后移

- 宇宙扩容 30~50 对与新 pair 质量流程(FR1.5)→ 后续 feature。
- 评测台/门禁/信号缓存对齐(FR3 与 M1 后续)→ 不在本 feature。
- Vibe-Trading local loader 对接(集成 §二)→ 可选 time-box,另立。
- TimescaleDB 阶段 B(纯 Parquet 化撤库)→ 独立评估。
