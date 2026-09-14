---
kind: feature
id: F008
version: "0.2"
related_features: [F001, F002, F003, F007]
topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
doc_kind: tasks
created: 2026-09-14
updated: 2026-09-14
---

# F008：宇宙扩容与 point-in-time 宇宙台账 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
- `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
- 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
- **机器边界**（架构 §7.1、`docs/SOP.md` §3）：回填、质量门、导出、备份在执行机 `qiaozhi-lt` 执行并记 hostname；开发机 `qiaozhi-gp` 只跑单元与契约测试。
- **不动 `F002` 已冻结语义**：导出/对账/manifest/修订规则一律沿用，本 feature 只扩 pair 集合并新增元数据 artifact。
- 回填是 1~2 周 wall-clock 的 owner 主导长跑；它**不阻塞**除产能对照外的任何一项，开发与测试用 fixture 推进。

## 1. 前置条件

- [ ] T001 (`FR-001`, `DR-001`): 把 Q-001 的裁决值落成可复核的口径文件（`turnover_lookback_days=90`、`turnover_rank_top_n=40`、`min_listed_days=180`、排除规则），作为 `discover` 的输入 — verify: `tests/unit/test_f008_discover.py`
- [ ] T002 (`NFR-005`): 估算并确认执行机磁盘余量能装下 40 对约 4200 万行及其 Parquet 快照（外推：约 29,300 个 ohlcv 分区、NAS 约 58,800 文件），不足则先扩容 — verify: 执行机 `df -h` 记录 + 与 F002 的 631 万行实测占用外推
- [ ] T003 [P] (`FR-001`): 确认 Binance USDⓈ-M 永续的行情接口与限流策略（可用字段、成交额口径、速率上限） — verify: `tests/unit/test_f008_discover.py`（接口响应 fixture）

## 2. 实现任务

### Phase 1：宇宙定义与台账（不依赖长跑回填）

- [ ] T004 (`FR-001`, `AC-001`): 实现 `discover.py`——按成交额排名取前 N、上线天数过滤与排除规则筛候选，记录逐候选指标、排除者与排除原因、快照时间；候选按排名有序以支持批次切分 — verify: `tests/unit/test_f008_discover.py`
- [ ] T005 (`FR-002`, `DR-001`, `AC-002`): 实现 `definition.py`——`UniverseDef` canonical JSON、`universe_id` 内容寻址、人工确认冻结与版本化 — verify: `tests/unit/test_f008_universe_def.py`
- [ ] T006 (`DR-002`): 编写 `db/migrations/` 前向迁移建 `universe_membership` 表与 `(lake_pair, valid_from)` 索引 — verify: `tests/unit/test_apply_migrations.py`
- [ ] T007 (`FR-005`, `DR-002`, `AC-007`, `AC-008`): 实现 `membership.py`——只追加写入封装、区间不重叠约束、`universe_at(T)`（左闭右开）；按 `DQ-001` 结论决定是否加数据库触发器兜底并记录结论 — verify: `tests/unit/test_f008_membership.py`
- [ ] T008 (`FR-005`, `DR-002`): 为现有 6 对补 `initial_seed` 台账记录，`valid_from` 取各自实际数据起点 — verify: `tests/integration/test_f008_export_integration.py`
- [ ] T009 (`FR-006`, `IR-002`, `AC-009`): 实现 `artifact.py`——台账 canonical 序列化与 digest 发布，复用 `symbol_map` 的内容寻址发布原语 — verify: `tests/integration/test_f008_export_integration.py`
- [ ] T010 (`TR-001`): 实现 `universe.member_changed` 事件写入与按 run/pair 查询 — verify: `tests/integration/test_f008_backfill.py`

### Phase 2：回填编排与质量门

- [ ] T011 (`FR-003`): 把 `collector/historical_backfill.py` 从一次性脚本泛化为可编排调用，并从 `docs/SOP.md` 豁免表移除该条目（若本轮未完成泛化则必须显式续期） — verify: `python3 tools/verify.py` + `tests/unit/test_f001_line_limit_exemptions.py`
- [ ] T012 (`FR-003`, `NFR-001`, `AC-004`): 实现限速与指数退避（重试上限、失败不提速），速率预算在 pair 间共享 — verify: `tests/unit/test_f008_rate_limit.py`
- [ ] T013 (`FR-003`, `DR-003`, `NFR-002`, `AC-003`): 实现 `backfill_runner.py`——批次编排、`(lake_pair, last_cursor)` 断点、逐 pair 进度与失败隔离、`BackfillRun` 落盘 — verify: `tests/integration/test_f008_backfill.py`
- [ ] T014 (`TR-002`, `AC-010`): 实现 `backfill.progress` / `backfill.failed` 事件与 hostname 标注 — verify: `tests/integration/test_f008_backfill.py`
- [ ] T015 (`FR-004`, `DR-004`, `AC-005`): 实现 `quality_gate.py`——复用 `tools/f001_backfill_report.py` 的缺失率/边界闭合/连续聚合口径并参数化到多 pair，逐 pair 判定记录（通过与失败同样保留） — verify: `tests/integration/test_f008_quality_gate.py`
- [ ] T016 (`FR-004`, `AC-006`): 实现"实际可得窗口"缺失率语义——上线晚于窗口起点不算缺失，真实上市时间写入台账 `valid_from` — verify: `tests/unit/test_f008_quality_gate_window.py`
- [ ] T017 (`FR-006`): 实现准入联动——固定 库追加 → artifact 发布 → 纳入 F002 导出清单 三步顺序，任一步失败不进入下一步 — verify: `tests/integration/test_f008_export_integration.py`
- [ ] T018 (`IR-001`): 实现 CLI 五个子命令与全部启动期拒绝条件（未冻结/窗口非法/磁盘不足/回填未完成就跑门禁） — verify: `tests/unit/test_f008_cli_contract.py`

### Phase 3：真实扩容执行

- [ ] T019 (`FR-001`, `FR-002`): 用 T001 的口径跑一次真实发现，人工复核 40 个候选（重点看第 25–40 名的流动性是否仍支持 ≥30 笔/90 天可达性）后冻结目标宇宙 — verify: `alphamill-universe show --universe <id>` 输出 + 冻结记录
- [ ] T020 (`FR-003`, `NFR-001`): 在执行机回填**批 1**（成交额前 30，含现有 6 对）——owner 主导，失败 pair 单独重跑 — verify: 批 1 的 `BackfillRun` 逐 pair `status=completed`
- [ ] T021 (`FR-003`, `NFR-001`): 回填**批 2**（第 31–40），复用同一套编排；批 1 已过门的 pair 不受影响 — verify: 批 2 的 `BackfillRun` 逐 pair `status=completed`
- [ ] T022 (`FR-004`): 每批回填完成后立即对该批 pair 跑质量门，通过者准入、失败者隔离并记录原因；**批 1 过门即可供 `F003` 使用，不必等批 2** — verify: `pytest -q tests/integration/test_f008_quality_gate.py` + 逐 pair 判定记录
- [ ] T023 (`FR-006`, `NFR-005`, `AC-011`): 两批都过门后跑一次全量导出与 NAS 备份，实测磁盘占用、导出耗时与备份时长并与 6 对基线及外推值对照 — verify: `tests/integration/test_f008_capacity_report.py`

## 3. 验证与验收任务

- [ ] T024 (`AC-001`, `AC-002`, `AC-004`, `AC-006`, `AC-007`, `AC-008`): 运行发现、定义、限速、窗口语义与台账单元套件 — verify: `pytest -q tests/unit/test_f008_discover.py tests/unit/test_f008_universe_def.py tests/unit/test_f008_rate_limit.py tests/unit/test_f008_quality_gate_window.py tests/unit/test_f008_membership.py`
- [ ] T025 (`AC-003`, `AC-005`, `AC-009`, `AC-010`): 运行回填、质量门与导出联动集成套件 — verify: `pytest -q tests/integration/test_f008_backfill.py tests/integration/test_f008_quality_gate.py tests/integration/test_f008_export_integration.py`
- [ ] T026 (`AC-011`, `NFR-004`): 在执行机 `qiaozhi-lt` 归档容量与耗时实测证据（含 hostname），开发机跳过属预期不得以其结果替代 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f008_capacity_report.py`
- [ ] T027: 修订 `docs/alphamill-integration.md` §1.3 的 OKX 过期表述为 Binance 路线 — verify: `python3 tools/check_doc_links.py` + 人工复核该节
- [ ] T028 (`AC-001`, `AC-011`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
- [ ] T029: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T019`：规模与阈值没定就不能跑真实发现与回填。
- `T002 -> T020`：磁盘余量确认在长跑之前，避免跑到一半写满盘。
- `T005 -> T013`：冻结定义是回填编排的不可变输入。
- `T006 -> T007 -> T008 -> T009`：建表 → 写入封装 → 补种历史 → 发布 artifact，顺序不可换。
- `T011 -> T013`：先泛化回填脚本，再套编排。
- `T012 -> T013`：限速策略是编排的组成部分。
- `T015 -> T017 -> T022`：质量门是导出清单的唯一准入通道。
- `T020 -> T022`、`T021 -> T022`：每批回填完成后各跑一次质量门；批 2 不阻塞批 1 的准入。
- `T022 -> T023`：两批都过门后才做容量实测（实测对象是最终的 40 对）。
- `T003 [P]`：只产接口 fixture，与定义/台账实现无共享状态。
- 与 `F003` 的关系：**批 1 过门（T022 的第一次执行）即满足 `F003` T035 的 ≥30 对前提**，不必等批 2 或 T023；在此之前 F003 的一切工作不被阻塞。

## 5. 明确后移

- 多交易所聚合与跨所 symbol 归一 → 后续 Feature：当前数据路线只有 Binance（F001 裁决）。
- 实时上下架监听与自动扩缩容 → 后续 Feature：M2 只需批处理周期发现成员变化。
- calendar artifact（交易日历/停机窗口）→ `F007` 或后续 Feature：ADR-0007 把它与 universe 并列，但 crypto 24/7 下优先级低于宇宙台账。
- 扩容到 40 对以上（含 50 对方案）与分片导出优化 → 视 T024 的实测余量再决定：50 对的全量导出约 32min、NAS 约 73,500 个分区文件，噪声改善仅 11%，当前不做；台账支持增量加 pair，需要时不必重来一轮。
