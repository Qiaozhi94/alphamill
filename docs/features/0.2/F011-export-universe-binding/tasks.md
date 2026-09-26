---
kind: feature
id: F011
version: "0.2"
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: tasks
created: 2026-09-25
updated: 2026-09-26
---

# F011：导出清单绑定当前宇宙版本 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成并验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- 实现中若任务顺序或契约失效，先修订三件套，再继续编码。
- 统一格式：`- [ ] T001 (`US-001`, `FR-001`, `AC-001`): <可验证动作> — verify: `path/to/test.py``

## 1. 前置条件

- [x] T001 (`DQ-001`): 关闭所有阻塞性 spec/design 问题（`Q-001`/`Q-002` 已关闭，§10 无开放设计问题）— verify: `spec.md`、`design.md`（2026-09-26 核对：spec §8 Q-001/Q-002 均 [x]，design §10「无」）
- [x] T002 (`FR-001`, `FR-002`): 核对上游契约与真实签名——`F008` 的 `export_admitted`/`load_definition`/`load_freeze`/`require_frozen`/定义枚举落点，定序字段（`snapshot_at` / `frozen_at` / `universe_id`）与口径字段（`criteria.exchange` / `criteria.market_type`），以及 `exporter.py` 当前行数（净增预算）— verify: `src/alphamill/data_bridge/universe/definition.py`（2026-09-26 核对：签名与字段均符合 design；`exporter.py`/`partitions.py` 均 350 行；单元格键 = `(exchange, symbol[, timeframe], date_iso)`，`allows(pair, date)` 取 `cell[-1]`；**偏差 1 处已修三件套**：台账以追加 `delisted` 行记退市而非写 `valid_to`，退市截止日改由 `materialize_intervals` 派生区间终点求得）

## 2. 实现任务

### Phase 1：绑定解析与交集（最小切片 = US-001）

- [x] T003 (`FR-002`, `FR-003`, `IR-003`, `AC-003`, `AC-004`): 新增 `data_bridge/universe/binding.py::resolve_binding(at, *, universe_id=None, lake_root=None) -> Binding`（候选：已冻结 ∧ `frozen_at ≤ at` ∧ `snapshot_at ≤ at`；多口径抛 `UniverseAmbiguousError`；按 `snapshot_at`→`frozen_at`→`universe_id` 取最新；显式：存在/已冻结/不前视，前视抛 `UniverseLookaheadError`）与 `Binding.drop_cutoff`（连续落选段最早冻结日）；`errors.py` 新增 `E_UNIVERSE_AMBIGUOUS`、`E_UNIVERSE_LOOKAHEAD` — verify: `tests/unit/test_f011_export_universe_binding.py`（red: b66ac27 收集期 `ImportError: cannot import name 'binding'`；green: 401bf1b 17 passed）
- [x] T004 (`FR-001`, `FR-004`, `AC-001`, `AC-005`, `AC-009`): `verdicts.export_admission` 一次读判定与台账、同时产出 `Admission(admitted, cutoffs, dropped)`（`cutoffs` = min(落选截止日, 退市截止日)）；`export_admitted` 改为其薄包装并增 `bound_universe: Binding | None = None`（`None` 保持 `F008` 原语义）；台账/判定记录保持只读 — verify: `tests/unit/test_f011_export_universe_binding.py`（red: d95b01b 收集期 `ImportError: cannot import name 'Admission'`；green: 24 passed + F008 集成 21 passed/1 xfailed 零修改）
- [x] T005 (`FR-005`, `AC-002`): 截止日判据接线：`produce_partitions` 单元格过滤改用 `Admission.allows(pair, date)`；`_admitted_only` 迁入 `export_policy.admitted_only` 并按同一判据过滤判缺候选与增量继承的基线 `skipped`；`merge_partitions` 不改；`partitions.py`/`exporter.py` 净增 ≤0 — verify: `tests/integration/test_f011_export_journey.py`（red: 883ef45 `TypeError: export_dataset() got an unexpected keyword argument 'bound_universe'`；green: 集成旅程 5 passed、F002/F008 回归 91 passed/1 xfailed）
- [ ] T006 (`FR-003`, `FR-004`, `IR-001`, `IR-002`, `IR-003`, `AC-003`, `AC-004`, `AC-005`, `AC-008`): 导出侧接线：`--universe-id`（单给即 `parser.error`）；`cli.main` 在 `_refresh_symbol_map()` 之前一次性解析绑定、固定 `window_end` 并传给全部 dataset；stderr 输出 `FATAL: <code>: <消息>`；运行摘要两键 + 逐条剔除日志；`exporter.py`/`binding.py`/`verdicts.py` ≤350 行由行数断言锁定 — verify: `tests/unit/test_f011_cli_contract.py`

### Phase 2：真实库/湖旅程（US-002 / US-003）

- [ ] T007 (`AC-001`, `AC-002`, `AC-006`): 集成旅程：三版定义（U1 含 X → U2 不含 → U3 重新含）+ 落选前后台账零变化 + 增量/全量/空湖首导下截止日前分区齐全且截止日后无分区、`skipped` 不翻转、源库修订被吸收 + 默认关闭过滤的对照导出 — verify: `tests/integration/test_f011_export_journey.py`

## 3. 验证与验收任务

- [ ] T008 (`AC-003`, `AC-005`, `AC-007`): 单元套件：默认/显式绑定、摘要字段、确定性（重复解析同集合）、无按 pair 的额外查询 — verify: `tests/unit/test_f011_export_universe_binding.py`
- [ ] T009 (`AC-003`, `AC-004`, `AC-008`): CLI 契约套件：`IR-003` 六种情形逐一断言退出码 2 + stderr 原因码 + `symbol_map`/新版本未落盘；单给 `--universe-id` 被拒；多 dataset 只解析一次；两份 `deployment/*export.service` 的 `--universe-filter` 一致 — verify: `tests/unit/test_f011_cli_contract.py`
- [ ] T010 (`AC-001`, `AC-002`, `AC-006`): 集成套件（真实 scratch 库 + 临时湖）全绿 — verify: `tests/integration/test_f011_export_journey.py`
- [ ] T011 (`AC-009`): `F008` 既有测试零修改全绿（`git diff main -- tests/integration/test_f008_*.py` 为空）— verify: `tests/integration/test_f008_quality_gate.py`、`tests/integration/test_f008_export_integration.py`
- [ ] T012 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-009`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T013 [TEST] (`AC-001`, `AC-002`, `AC-005`, `AC-006`): 层 2 旅程验收（US-001/002/003 端到端：落选即移出 → 台账与数据零变化 → 显式绑定可复现 → 摘要可查 → 重新入选自动回来）— verify: `tests/integration/test_f011_export_journey.py`
- [ ] T014 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`, `AC-009`): 收口回写：spec 验收证据与 AC 勾选、`BACKLOG.md` 状态、`docs/features/releases/0.2.md` 交付记录、frontmatter 流转 — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002`：先关问题再核契约。
- `T002 -> T003`：定序/口径字段与签名确认后才能实现解析。
- `T003 -> T004`：交集需要一个已解析出的绑定版本。
- `T004 -> T005`：截止日判据依赖 `Admission.allows`。
- `T004 -> T006`：CLI 接线依赖 `export_admission` 与新的 `bound_universe` 参数。
- `T005 -> T007`、`T006 -> T007`：旅程要跑完整的导出接线（含截止日判据与默认关闭对照）。
- `T004 -> T008`：单元套件覆盖交集实现本体。
- `T006 -> T009`：原因码取自 CLI 接线。
- `T007 -> T010`：集成套件与旅程同载体，先实现后全量跑。
- `T004 -> T011`：`export_admitted` 改为薄包装后回归 `F008` 既有测试。
- `T008 -> T012`、`T009 -> T012`、`T010 -> T012`、`T011 -> T012`：统一质量门在四条验证轨之后。
- `T010 -> T013`：旅程验收在集成载体就绪后执行。
- `T012 -> T014`、`T013 -> T014`：门禁与旅程双绿后才收口回写。

## 5. 明确后移

- 生产调度单元是否打开 `--universe-filter`（`deployment/alphamill-export.service` 与 `deployment/alphamill-fullexport.service`，两者必须同开同关）——部署决策，由 owner 决定后单独执行（`spec.md` §8 `Q-002`）。
- 超出 journald 保留期的绑定审计留痕（运行摘要长期持久化）——本 feature 只落 journald（`spec.md` `FR-004`），需要时另立 feature。
- 判定表随宇宙收窄（落选 pair 的旧 ACTIVE 判定仍留在只追加的判定表）——本 feature 只用交集覆盖其影响，语义层面的收窄另立 feature。
