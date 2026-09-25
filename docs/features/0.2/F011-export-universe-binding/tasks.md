---
kind: feature
id: F011
version: "0.2"
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: tasks
created: 2026-09-25
updated: 2026-09-25
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

- [ ] T001 (`DQ-001`): 关闭所有阻塞性 spec/design 问题（`Q-001`/`Q-002` 已关闭，§10 无开放设计问题）— verify: `spec.md`、`design.md`
- [ ] T002 (`FR-001`, `FR-002`): 核对上游契约与真实签名——`F008` 的 `export_admitted`/`load_definition`/`freeze_definition`/定义枚举落点，以及冻结记录里可用的定序字段（`frozen_at` / `universe_id`）— verify: `src/alphamill/data_bridge/universe/definition.py`

## 2. 实现任务

### Phase 1：绑定解析与交集（最小切片 = US-001）

- [ ] T003 (`FR-002`, `FR-003`, `AC-003`, `AC-004`): 实现 `definition.latest_frozen(lake_root)`（枚举 `defs_dir` 下 `*.frozen.json`，按 `frozen_at` 定序、同时刻按 `universe_id`）与显式版本解析；无冻结定义抛 `UniverseNotFrozenError`、指定 id 不存在抛 `UniverseNotFoundError` — verify: `tests/unit/test_f011_export_universe_binding.py`
- [ ] T004 (`FR-001`, `FR-005`, `AC-001`, `AC-002`): `export_admitted` 增 `bound_universe` 关键字参数（区别于既有 `universe_id` 判定过滤），按 `db_symbol` 与 `definition.selected` 求交；台账/判定记录保持只读 — verify: `tests/unit/test_f011_export_universe_binding.py`
- [ ] T005 (`FR-004`, `IR-001`, `IR-002`, `AC-005`): 导出侧接线：`--universe-id` 可选参数、绑定解析接入 `--universe-filter`、运行摘要写入 `universe_id` 与排序稳定的 `dropped_by_universe`，逐条日志记录被剔除 pair — verify: `tests/unit/test_f011_cli_contract.py`

### Phase 2：真实库/湖旅程（US-002 / US-003）

- [ ] T006 (`AC-001`, `AC-002`, `AC-006`): 集成旅程：三版定义（U1 含 X → U2 不含 → U3 重新含）+ 落选前后台账零变化 + 既有分区原样继承 + 默认关闭过滤的对照导出 — verify: `tests/integration/test_f011_export_universe_binding.py`

## 3. 验证与验收任务

- [ ] T007 (`AC-003`, `AC-005`, `AC-007`): 单元套件：默认/显式绑定、摘要字段、确定性（重复解析同集合）、无按 pair 的额外查询 — verify: `tests/unit/test_f011_export_universe_binding.py`
- [ ] T008 (`AC-004`): CLI 契约套件：无冻结定义 → `E_UNIVERSE_NOT_FROZEN`；未知 id → `E_UNIVERSE_NOT_FOUND`；两者均非零退出且不发布新版本 — verify: `tests/unit/test_f011_cli_contract.py`
- [ ] T009 (`AC-001`, `AC-002`, `AC-006`): 集成套件（真实 scratch 库 + 临时湖）全绿 — verify: `tests/integration/test_f011_export_universe_binding.py`
- [ ] T010 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T011 [TEST] (`AC-001`, `AC-002`, `AC-005`, `AC-006`): 层 2 旅程验收（US-001/002/003 端到端：落选即移出 → 台账与数据零变化 → 显式绑定可复现 → 摘要可查 → 重新入选自动回来）— verify: `tests/integration/test_f011_export_universe_binding.py`
- [ ] T012 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`): 收口回写：spec 验收证据与 AC 勾选、`BACKLOG.md` 状态、`docs/features/releases/0.2.md` 交付记录、frontmatter 流转 — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002`：先关问题再核契约。
- `T002 -> T003`：定序字段与签名确认后才能实现解析。
- `T003 -> T004`：交集需要一个已解析出的绑定版本。
- `T004 -> T005`：CLI 接线依赖新的 `export_admitted` 参数。
- `T005 -> T006`：旅程要跑完整的导出接线（含默认关闭对照）。
- `T004 -> T007`：单元套件覆盖交集实现本体。
- `T005 -> T008`：原因码取自 CLI 接线。
- `T006 -> T009`：集成套件与旅程同载体，先实现后全量跑。
- `T007 -> T010`、`T008 -> T010`、`T009 -> T010`：统一质量门在三条验证轨之后。
- `T009 -> T011`：旅程验收在集成载体就绪后执行。
- `T010 -> T012`、`T011 -> T012`：门禁与旅程双绿后才收口回写。

## 5. 明确后移

- 生产调度单元是否打开 `--universe-filter`（`deployment/alphamill-export.service`）——部署决策，由 owner 决定后单独执行（`spec.md` §8 `Q-002`）。
- 判定表随宇宙收窄（落选 pair 的旧 ACTIVE 判定仍留在只追加的判定表）——本 feature 只用交集覆盖其影响，语义层面的收窄另立 feature。
