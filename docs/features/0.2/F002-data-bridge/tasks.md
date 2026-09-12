---
kind: feature
id: F002
version: "0.2"
related_features: [F001]
topics: [data-bridge, parquet, duckdb, m1]
doc_kind: tasks
created: 2026-09-12
updated: 2026-09-12
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
- 设计待确认问题:DQ-003 留待实现期观察,不阻塞开工(见 design §10)。

## 2. 实现任务

### Phase 1:导出器核心(ohlcv_1m 端到端)

- [ ] T001 [P] (`FR-001`): pyproject 新增 `pyarrow`/`duckdb` 依赖 pin(版本范围本地验证后落定),`.venv` 安装验证 — verify: `.venv/bin/python -c "import pyarrow, duckdb"` 退出码 0
- [ ] T002 (`FR-001`): `src/alphamill/data_bridge/manifest.py`——manifest 契约读写(架构 §4.4 字段 + status/reconcile/revision_diff 扩展)、data_version 排序与最新 valid 解析 — verify: `tests/unit/test_f002_manifest.py`
- [ ] T003 (`FR-001`): `src/alphamill/data_bridge/exporter.py`——ohlcv_1m 全量导出:库查询 → 按 `exchange/pair/date` 分区原子写 Parquet → 生成 manifest — verify: 手动执行一次,`lake/ohlcv_1m/` 分区文件与 `_manifests/ohlcv_1m/<version>.json` 齐备
- [ ] T004 (`FR-002`): 对账器——逐分区行数 + hashtext 校验和 vs TimescaleDB,不一致标记 invalid — verify: `tests/integration/test_f002_export_reconcile.py`(AC-001/AC-002)
- [ ] T005 [P] (`FR-004`): `src/alphamill/data_bridge/symbol_map.py`——从库 DISTINCT symbol 生成 `symbol_map.csv`(lake_pair/freqtrade_pair/db_symbol)与双向解析 — verify: `tests/unit/test_f002_symbol_map.py`(AC-004)

### Phase 2:取数入口与 dataset 扩展

- [ ] T006 (`FR-003`): `src/alphamill/data_bridge/reader.py`——DuckDB 只读取数(dataset+data_version+时间范围+pair 过滤;invalid/缺失版本抛错) — verify: `tests/integration/test_f002_reader.py`(AC-003)
- [ ] T007 (`FR-001`): 导出器扩展至衍生品三表与 signals_log(signals_log 无 exchange 维度,按日分区) — verify: AC-001 测试覆盖五 dataset
- [ ] T008 [P] (`FR-005`): 全量校验模式——库内 vs 既有快照的分区级 diff,修订时递增 data_version 并登记 revision_diff,旧版本原样保留 — verify: `tests/integration/test_f002_revision.py`(AC-005)

### Phase 3:运维化

- [ ] T009 (`FR-006`): 导出 CLI 入口(`python -m alphamill.data_bridge.exporter --dataset ... --mode ...`)+ systemd user timer(每日 02:00 增量;周日 04:00 全量,与 03:00 NAS 备份错峰) — verify: 手动触发退出码 0,journalctl 可查
- [ ] T010 (`FR-006`): `backup-nas.sh` lake/ 同步实测——触发备份后 NAS 端 `lake/` 与 `_manifests/` 产物齐全 — verify: NAS 端 ls 校验(AC-006)
- [ ] T014 (`FR-001`): Kronos 真实推理容器化——compose 可选 profile `kronos-real`(torch/cpu 进镜像 + `vendor/Kronos` 与 `models/` 挂载,默认不启动),使 T007 导出的 signals_log 是真实信号而非 placeholder;同时让 F001 AC-006 可由编排直接复跑而非手工起实例 — verify: `docker compose --profile kronos-real up -d` 后 `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py -q` 全绿,且 `signals_log` 新增行 `source=kronos`

## 3. 验证与验收任务

- [ ] T011 (`FR-001`,`FR-002`,`FR-003`): 端到端验收——全量导出 → DuckDB 取数对账 → invalid 拒绝,记录全量导出耗时 — verify: `tests/integration/test_f002_export_reconcile.py` + `test_f002_reader.py` 全绿
- [ ] T012 (`FR-001`..`FR-006`): 全量集成测试 + 统一质量门 — verify: `.venv/bin/python -m pytest tests/integration -q` 与 `python3 tools/verify.py` 全绿
- [ ] T013: 回写 spec 验收证据、BACKLOG 状态与设计决策沉淀(DQ-003 处置结论) — verify: `python tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002/T003/T005/T006`:依赖就绪(P0)。
- `T002 -> T003 -> T004`:manifest 是导出与对账的公共契约。
- `T014 -> T007`(质量前置,非硬阻塞):薄壳仍是 mock 时 signals_log 导出的是 placeholder 行,湖内该 dataset 对因子研究无价值;导出管线本身不依赖 T014。
- `T003 -> T006`:取数测试依赖已有快照。
- `T004 -> T008`:修订 diff 复用对账器。
- `T002/T005 [P]`、`T006(依赖T003)`、`T008(依赖T004)` 分支并行。
- `T009/T010` 依赖 Phase 1-2 完成;`T011 -> T012 -> T013` 验收链顺序执行。

## 5. 明确后移

- 宇宙扩容 30~50 对与新 pair 质量流程(FR1.5)→ 后续 feature。
- 评测台/门禁/信号缓存对齐(FR3 与 M1 后续)→ 不在本 feature。
- Vibe-Trading local loader 对接(集成 §二)→ 可选 time-box,另立。
- TimescaleDB 阶段 B(纯 Parquet 化撤库)→ 独立评估。
