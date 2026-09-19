---
kind: feature
id: F008
version: "0.2"
related_features: [F001, F002, F003, F007]
topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
doc_kind: tasks
created: 2026-09-14
updated: 2026-09-19
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
- `[TEST]` 组（§3）是开发前置门：从 US-001~US-004 的旅程步骤派生（每旅程 ≥1 条可执行断言），编写早（Phase 1 先立红灯）、执行晚（收尾全量跑）；缺失即被 SDD Flow T3 拒绝流转（见 `design.md` 开发前置约束）。
- 回填是 1~2 周 wall-clock 的 owner 主导长跑；它**不阻塞**除产能对照外的任何一项，开发与测试用 fixture 推进。

## 1. 前置条件

- [x] T001 (`FR-001`, `DR-001`): 把 Q-001 的裁决值落成可复核的口径文件（`turnover_lookback_days=90`、`turnover_rank_top_n=40`、`min_listed_days=180`、排除规则），作为 `discover` 的输入 — verify: `tests/unit/test_f008_discover.py`
- [ ] T002 (`NFR-005`): 估算并确认执行机磁盘余量能装下 40 对约 4200 万行及其 Parquet 快照（外推：约 29,300 个 ohlcv 分区、NAS 约 58,800 文件），不足则先扩容 — verify: 执行机 `df -h` 记录 + 与 F002 的 631 万行实测占用外推
- [x] T003 [P] (`FR-001`): 确认 Binance USDⓈ-M 永续的行情接口与限流策略（可用字段、成交额口径、速率上限） — verify: `tests/unit/test_f008_discover.py`（接口响应 fixture）

## 2. 实现任务

### Phase 1：宇宙定义与台账（不依赖长跑回填）

- [x] T004 (`FR-001`, `AC-001`): 实现 `discover.py`——按成交额排名取前 N、上线天数过滤与排除规则筛候选，记录逐候选指标、排除者与排除原因、快照时间；候选按排名有序以支持批次切分 — verify: `tests/unit/test_f008_discover.py`
- [x] T005 (`FR-002`, `DR-001`, `AC-002`): 实现 `definition.py`——`UniverseDef` canonical JSON、`universe_id` 内容寻址、人工确认冻结与版本化 — verify: `tests/unit/test_f008_universe_def.py`
- [x] T006 (`DR-002`): 编写前向迁移 `db/migrations/005_universe_membership.sql`（现有编号止于 004）建 `universe_membership` 表与 `(lake_pair, valid_from)` 索引；须满足 runner 两条硬约束——幂等（`IF NOT EXISTS`）、无非事务语句，整文件单事务执行 — verify: `tests/unit/test_apply_migrations.py`
- [x] T007 (`FR-005`, `DR-002`, `AC-007`, `AC-008`): 实现 `membership.py`——只追加写入封装、区间不重叠约束、`universe_at(T)`（左闭右开）；按 `DQ-001` 结论决定是否加数据库触发器兜底并记录结论——**结论：应用层单写封装 + 数据库触发器双保险**（`005_universe_membership.sql` 里 `no_mutation` 拒绝 UPDATE/DELETE、`increasing` 拒绝 valid_from 回填与区间重叠） — verify: `tests/unit/test_f008_membership.py`
- [x] T008 (`FR-005`, `DR-002`): 为现有 6 对补 `initial_seed` 台账记录，`valid_from` 取各自实际数据起点 — verify: `tests/unit/test_f008_membership.py`
- [x] T009 (`FR-006`, `IR-002`, `IR-003`, `AC-009`, `AC-013`): 实现 `artifact.py`——按 `IR-002` 冻结的 canonical JSON schema（顶层 `{schema_version, members}`、成员严格三键、最小 PIT 投影）序列化并按 `sha256:` 前缀 digest 原子发布；产物必须能被 `factor_factory.generators.universe.load_explicit_universe` 直接加载 — verify: `tests/unit/test_f008_artifact.py` + `tests/integration/test_f008_export_integration.py`
- [x] T010 (`TR-001`): 实现 `universe.member_changed` 事件写入与按 run/pair 查询 — verify: `tests/integration/test_f008_backfill.py`

### Phase 2：回填编排与质量门

- [x] T011 (`FR-003`): 把 `collector/historical_backfill.py` 从一次性脚本泛化为可编排调用，并从 `docs/SOP.md` 豁免表移除该条目（若本轮未完成泛化则必须显式续期） — verify: `python3 tools/verify.py` + `tests/unit/test_f001_line_limit_exemptions.py`
- [x] T012 (`FR-003`, `NFR-001`, `AC-004`): 实现限速与指数退避（重试上限、失败不提速），速率预算在 pair 间共享 — verify: `tests/unit/test_f008_rate_limit.py`
- [x] T013 (`FR-003`, `DR-003`, `NFR-002`, `AC-003`): 实现 `backfill_runner.py`——批次编排、`(lake_pair, last_cursor)` 断点、逐 pair 进度与失败隔离、`BackfillRun` 落盘 — verify: `tests/integration/test_f008_backfill.py`
- [x] T014 (`TR-002`, `AC-010`): 实现 `backfill.progress` / `backfill.failed` 事件与 hostname 标注 — verify: `tests/integration/test_f008_backfill.py`
- [x] T015 (`FR-004`, `DR-004`, `AC-005`): 实现 `quality_gate.py`——复用 `tools/f001_backfill_report.py` 的缺失率/边界闭合/连续聚合三项口径并参数化到多 pair，**另补一项它没有的显式重复主键检查**（`GROUP BY exchange, symbol, time HAVING count(*) > 1`；参考表 `ohlcv_1m` 的主键使重复结构性不可发生，故该项在真实表上恒为 0，其检测路径必须由无主键 scratch 源表 fixture 真实触发，不得写成空转断言），逐 pair 判定记录（通过与失败同样保留，该记录是准入状态真相源） — verify: `tests/integration/test_f008_quality_gate.py`
- [x] T016 (`FR-004`, `AC-006`, `DR-002`): 实现"实际可得窗口"缺失率语义——上线晚于窗口起点不算缺失；真实上市时间写入台账 `valid_from`（可交易期语义，与准入时点无关） — verify: `tests/unit/test_f008_quality_gate_window.py`
- [x] T017 (`FR-006`, `DR-004`): 实现准入联动——固定 库追加 → artifact 发布 → 写准入记录并进入导出清单 三步顺序，任一步失败不进入下一步；`admitted = universe_at(本次导出 window_end)`，接线三处缺一不可：`partitions.lake_pairs_map(admitted=…)` + `produce_partitions` 的单元格级剔除（否则未准入 pair 会抛 `DataBridgeError` 而非被排除）+ `exporter.export_dataset/_export_one` 透传；`admitted=None` 时行为与 F002 现状逐字节一致，且断言 `symbol_map` 保持全量（与导出清单允许不等）；全量导出若因收缩命中 `guard_full_shrink`，按 F002 既有语义走 `--allow-shrink` 并在容量报告记录 `shrink_confirmed`，不得放宽守卫 — verify: `tests/integration/test_f008_export_integration.py`
- [x] T018 (`IR-001`, `AC-012`): 实现 `universe/__main__.py` 模块入口（`python -m alphamill.data_bridge.universe`，不新增 `[project.scripts]`）的五个子命令与 design §4 登记的全部九类启动期拒绝条件（未冻结/窗口非法/磁盘不足/`freeze` 缺 `--confirm`/`gate` 遇回填未完成/口径缺字段/交易所不可达/候选清单为空/定义或 digest 不存在），各自以可区分的非零原因退出 — verify: `tests/unit/test_f008_cli_contract.py`

### Phase 3：真实扩容执行

- [ ] T019 (`FR-001`, `FR-002`): 用 T001 的口径跑一次真实发现，人工复核 40 个候选（逐候选核对成交额排名、上线天数与排除原因均按 `DR-001` 入档）后冻结目标宇宙 — verify: `python -m alphamill.data_bridge.universe show --universe <id>` 输出 + 冻结记录
- [ ] T020 (`FR-003`, `NFR-001`): 在执行机回填**批 1**（成交额前 30，含现有 6 对）——owner 主导，失败 pair 单独重跑 — verify: 批 1 的 `BackfillRun` 逐 pair `status=completed`
- [ ] T021 (`FR-003`, `NFR-001`): 回填**批 2**（第 31–40），复用同一套编排；批 1 已过门的 pair 不受影响 — verify: 批 2 的 `BackfillRun` 逐 pair `status=completed`
- [ ] T022 (`FR-004`): 每批回填完成后立即对该批 pair 跑质量门，通过者准入、失败者隔离并记录原因；**批 1 过门即可供 `F003` 使用，不必等批 2** — verify: `pytest -q tests/integration/test_f008_quality_gate.py` + 逐 pair 判定记录
- [ ] T023 (`FR-006`, `NFR-005`, `AC-011`): 两批都过门后跑一次全量导出与 NAS 备份，实测磁盘占用、导出耗时与备份时长并与 6 对基线及外推值对照 — verify: `tests/integration/test_f008_capacity_report.py`

## 3. 验证与验收任务

- [ ] T024 (`AC-001`, `AC-002`, `AC-004`, `AC-006`, `AC-007`, `AC-008`): 运行发现、定义、限速、窗口语义与台账单元套件 — verify: `pytest -q tests/unit/test_f008_discover.py tests/unit/test_f008_universe_def.py tests/unit/test_f008_rate_limit.py tests/unit/test_f008_quality_gate_window.py tests/unit/test_f008_membership.py`
- [ ] T025 (`AC-003`, `AC-005`, `AC-009`, `AC-010`): 运行回填、质量门与导出联动集成套件 — verify: `pytest -q tests/integration/test_f008_backfill.py tests/integration/test_f008_quality_gate.py tests/integration/test_f008_export_integration.py`
- [ ] T026 (`AC-011`, `NFR-004`): 在执行机 `qiaozhi-lt` 归档容量与耗时实测证据（含 hostname），开发机跳过属预期不得以其结果替代 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f008_capacity_report.py`
- [x] T027: 修订 `docs/alphamill-integration.md` §1.3 的 OKX 过期表述为 Binance 路线 — verify: `python3 tools/check_doc_links.py` + 人工复核该节
- [ ] T028 (`AC-001`, `AC-011`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
- [x] T029 (`AC-014`, `IR-002`, `FR-006`): 把 `F007` 的 universe 只读消费面从废弃的 CSV 契约迁到 `IR-002` 的 canonical JSON——`evaluation/universe_ledger.py` 改为按 `<digest>.json` 加载（顶层 `{schema_version, members}`、成员严格三键、digest 用解析后重新规范化的字节重算、未知键与版本不符 fail-closed）、`contract_common.py` 的 `UNIVERSE_COLUMNS` 换成 JSON 键集合常量、`upstream_contracts.py` 门面再导出同步，并改三处 CSV fixture 测试（`tests/contract/test_f007_upstream_contracts.py`、`tests/integration/test_f007_controls.py`、`tests/integration/test_f007_cli.py`）；`universe_at(T)` 半开区间语义与 ResearchSnapshot 身份公式不得改动 — verify: `pytest -q tests/contract/test_f007_upstream_contracts.py tests/integration/test_f007_controls.py tests/integration/test_f007_cli.py tests/unit/experiment_store/`

### [TEST] 组：层 2 旅程验收轨（必填）

从体验旅程派生，Phase 1 先以红灯立起夹具，收尾全量执行；真实环境项在执行机 `qiaozhi-lt` 取证。

- [ ] T030 [TEST] (`US-001`, `AC-001`, `AC-002`, `AC-012`): 旅程 US-001 端到端验收——对固定交易所快照 fixture 连跑两次 `discover` 得同一候选清单与同一 `universe_id`；逐候选指标与排除原因入档；未冻结清单驱动 `backfill` 被非零拒绝；`freeze` 缺 `--confirm` 被拒；冻结后成员增删产生新 `universe_id` 且旧版本只读 — verify: `pytest -q tests/unit/test_f008_discover.py tests/unit/test_f008_universe_def.py tests/unit/test_f008_cli_contract.py`
- [ ] T031 [TEST] (`US-002`, `AC-003`, `AC-004`, `AC-010`): 旅程 US-002 端到端验收——单 pair 窗口回填跑到一半中断后重跑，从断点继续、无重复行、行数与预期一致；注入限流错误触发指数退避且不超上限、速率不因失败提高；单 pair 失败不影响其他 pair 的已完成进度；`BackfillRun` 与进度/失败事件可按 run 与 pair 查询且带 hostname — verify: `pytest -q tests/unit/test_f008_rate_limit.py tests/integration/test_f008_backfill.py`
- [ ] T032 [TEST] (`US-003`, `AC-005`, `AC-006`, `AC-009`): 旅程 US-003 端到端验收——缺失率超限/边界未闭合/连续聚合不一致/重复主键四类 fixture 均被隔离并各记原因码、均不进导出清单；上线晚于窗口起点的 pair 按实际可得窗口算缺失率不被误判；全项通过者按 库追加 → artifact 发布 → 写准入记录 三步准入，发布的 artifact 可被下游 `load_explicit_universe` 加载，且 `symbol_map` 与导出清单允许不等 — verify: `pytest -q tests/integration/test_f008_quality_gate.py tests/unit/test_f008_quality_gate_window.py tests/integration/test_f008_export_integration.py`
- [ ] T033 [TEST] (`US-004`, `AC-007`, `AC-008`, `AC-013`): 旅程 US-004 端到端验收——含上市/退市/中途进出的成员 fixture 上 `universe_at(T)` 在各时点返回正确集合（左闭右开）；原地改写已发布历史区间被拒、退出只以追加新区间表达且历史数据不删；`schema_version` 不符或出现未知键时加载被拒 — verify: `pytest -q tests/unit/test_f008_membership.py tests/unit/test_f008_artifact.py`

- [ ] T034: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter — verify: `python3 tools/validate_spec_lifecycle.py`
      （编号说明：原收口任务在检视收口时由 `T029` 改编号为 `T034`，以满足 `check_task_dag` 的「收口任务编号最高、须有入边」两条规则；`T029` 现由「F007 消费面迁移」占用——它是开工前检查发现的契约漂移修复，必须排在最高编号之前。）

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
- `T003 -> T004`：发现实现以交易所接口 fixture 为前提（`[P]` 仅表示它与定义/台账实现无共享状态，可并行起步）。
- `T004 -> T005`：先有候选清单才谈得上冻结为定义。
- `T009 -> T017`：artifact 发布是准入联动三步的中间环节。
- `T010 -> T014`：成员事件写入先于回填事件的统一落盘与 hostname 标注。
- `T013 -> T020`、`T019 -> T020`：编排实现与真实冻结都是批 1 回填的前提。
- `T016 -> T022`：实际可得窗口语义先落地，质量门才不会误判晚上线的 pair。
- `T023 -> T026`：先有全量导出与备份实测，才谈得上在执行机归档证据。
- `T004/T005/T018 -> T030`、`T012/T013/T014 -> T031`、`T015/T016/T017 -> T032`、`T007/T008/T009 -> T033`：
  [TEST] 组四条旅程验收各以对应实现任务为前提（夹具编写早、全量执行晚）。
- `T004/T005/T007/T008/T012/T016 -> T024`：单元套件以发现、定义、台账与限速/窗口语义实现为前提。
- `T009/T013/T014/T015/T017 -> T025`：集成套件以回填编排、质量门与导出联动实现为前提。
- `T011 -> T027`：先完成 `historical_backfill.py` 泛化（含 SOP 豁免表处理），再统一修订 integration §1.3 的过期表述。
- `T009 -> T029`：F007 消费面迁移以 artifact 的 canonical JSON 契约为输入（T009 冻结该格式），并由 T029 的契约测试复核两侧 digest 一致。
- `T024/T025 -> T028`：统一质量门在各验收套件之后跑。
- `T024/T025/T026/T027/T028/T029/T030/T031/T032/T033 -> T034`：全部验收套件、真实环境证据、文档修订、
  下游消费面迁移与旅程验收通过后，才回写 spec 验收证据与状态。
- 与 `F003` 的关系：**批 1 过门（T022 的第一次执行）即满足 `F003` T035 的 ≥30 对前提**，不必等批 2 或 T023；在此之前 F003 的一切工作不被阻塞。
- `F003 并入 main -> AC-009 跨消费者断言`：`factor_factory/generators/universe.py::load_explicit_universe` 当前只存在于 `feat/F003-alphagen-vendor`（F003 仍 `developing`），AC-009 的「产物可被它直接加载」一条在 F003 落地前**不可执行**——按项目 SOP「已知缺口显式标记」写成 `xfail(strict=True)` 并在 reason 里写明该分支依赖，F003 并入 main 后 XPASS 转红、强制摘除标记并真跑；F008 侧先由 `AC-013`（`tests/unit/test_f008_artifact.py`）锁死同一 schema 的键集合、排序与 digest 规则。
- `T017 -> T023`：准入过滤与退市/隔离都会减少全量导出的分区数，可能命中 F002 的 `guard_full_shrink`；容量实测（T023）必须显式记录是否用了 `--allow-shrink` 与 manifest 的 `shrink_confirmed`，不得放宽守卫。

## 5. 明确后移

- 多交易所聚合与跨所 symbol 归一 → 后续 Feature：当前数据路线只有 Binance（F001 裁决）。
- 实时上下架监听与自动扩缩容 → 后续 Feature：M2 只需批处理周期发现成员变化。
- calendar artifact（交易日历/停机窗口）→ `F007` 或后续 Feature：ADR-0007 把它与 universe 并列，但 crypto 24/7 下优先级低于宇宙台账。
- 逐期重算排名的 PIT 宇宙构造（消除成员选取前视）→ 后续 Feature：需要全市场历史成交额，不在 M2 范围；台账只追加结构天然支持升级（裁决见 `spec.md` §7）。
- 扩容到 40 对以上（含 50 对方案）与分片导出优化 → 视 T023/T026 的实测余量再决定：50 对的全量导出约 32min、NAS 约 73,500 个分区文件，噪声改善仅 11%，当前不做；台账支持增量加 pair，需要时不必重来一轮。
