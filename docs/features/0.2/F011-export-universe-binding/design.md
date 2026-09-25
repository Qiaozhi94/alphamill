---
kind: feature
id: F011
version: "0.2"
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: design
created: 2026-09-25
updated: 2026-09-25
---

# F011：导出清单绑定当前宇宙版本 - 设计

## 0. 输入与约束

- **行为契约**：`spec.md`（`FR-001`~`FR-005`、`AC-001`~`AC-007`）
- **PRD / Architecture / System Design**：`docs/alphamill-architecture.md` §4.1.1；`docs/alphamill-integration.md` §1.2
- **ADR / 上游 Contract**：ADR-0003（门禁不降级）、ADR-0007（快照绑定）；`F008` `IR-002`（artifact canonical JSON）、`F002`（导出/manifest 契约）
- **实现约束**：`src/**/*.py` ≤350 行；唯一门禁入口 `tools/verify.py`；台账只读；默认路径行为逐字节不变

## 1. 技术概要与影响面

改动集中在三个点，都是既有函数的**参数扩展**，不新增模块：

1. `data_bridge/universe/definition.py`：新增 `latest_frozen(lake_root)` —— 遍历已冻结定义，按冻结时刻取最新（同时刻按 `universe_id` 定序）。
2. `data_bridge/universe/quality_gate.py::export_admitted`：新增 `universe_id: str | None = None`，按 `db_symbol` 与 `definition.selected` 求交；`None` 时解析最新冻结定义（解析失败抛 `UniverseNotFrozenError`）。
3. `data_bridge/exporter.py` + `data_bridge/cli.py`：`--universe-filter` 打开时解析绑定版本、把 `universe_id` 与 `dropped_by_universe` 写进运行摘要；新增 `--universe-id` 覆盖。

影响面：导出准入集合的口径（默认关闭时不变）、CLI 契约（新增一个可选参数）、运行摘要（新增两个键）。**不改**：台账、artifact、manifest schema、质量门阈值、`symbol_map` 全量语义。

## 2. 架构与模块边界

```
CLI (--universe-filter / --universe-id)
  └─ exporter.export_dataset
       ├─ definition.latest_frozen(lake_root)        # 解析绑定版本（可被 --universe-id 覆盖）
       └─ quality_gate.export_admitted(conn, at, market_type=..., universe_id=...)
            = universe_at(at) ∩ verdicts(ACTIVE) ∩ selected(bound)   # 全部按 db_symbol 求交
```

- `definition` 只答「有哪些版本、哪一版最新」，不碰台账与判定；
- `export_admitted` 是唯一交集点（`F008` 既有结构），导出侧不再有第二处准入过滤；
- `exporter` 只负责把解析结果带进摘要与日志，不参与集合运算。

## 3. 数据模型与 Migration

**无 migration、无实体变更**。`universe_membership` 与 `universe_quality_verdicts` 均只读（`DR-001`）；被绑定版本从既有 `_metadata/universe_defs/*.json` 解析，不新建索引或指针文件。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 接口 | 变更 | 说明 |
|---|---|---|
| `exporter --universe-filter` | 语义扩展 | 由「台账 ∩ ACTIVE」变为「台账 ∩ ACTIVE ∩ 当前宇宙入选集」 |
| `exporter --universe-id <digest>` | 新增（可选） | 显式绑定；必须已冻结且存在 |
| `export_admitted(..., universe_id=None)` | 新增关键字参数 | `None` ⇒ 最新冻结定义；解析失败抛 `UniverseNotFrozenError` |
| 运行摘要 dict | 新增 `universe_id` / `dropped_by_universe` | 关闭过滤时 `null` / `[]`；列表排序稳定 |

退出码与原因码沿用既有表：无冻结定义 → `E_UNIVERSE_NOT_FROZEN`；指定 id 不存在 → `E_UNIVERSE_NOT_FOUND`（均为非零，`IR-003`）。

### Event / Trace Contract

不新增事件类型。`F008` 的 `universe.member_changed` 语义不变——**落选不是成员变更**（台账不动），因此**不得**为落选写事件；绑定结果只进运行摘要/日志（`DR-002`）。

## 5. Runtime、Workflow 与并发

```text
resolve_bound_universe():
  explicit_id? -> load_definition(explicit_id)（未冻结/不存在 -> 拒绝）
  else         -> latest_frozen(lake_root)（无 -> 拒绝）
admitted = export_admitted(conn, window_end, market_type, universe_id=bound)
dropped  = sorted(active_symbols - selected_symbols(bound))
```

- 导出仍是单进程批处理；集合运算为内存操作（`NFR-001`），定义一次读入、台账一次读入；
- 并发安全性与现状一致（导出自身有 REPEATABLE READ 快照）；不引入新的锁或共享状态。

## 6. UI 与可观测性

无 UI。可观测性：

- 日志：绑定版本 `INFO`；被剔除 pair 逐条 `INFO`（`db_symbol` + 原因 `not_in_universe_selection`）；
- 运行摘要：`universe_id`、`dropped_by_universe`（`IR-002`）——这是本 feature 唯一的留痕面（manifest 不改，`DR-002`）。

## 7. 失败、恢复、安全与兼容

- **fail-closed**：无冻结定义 / 指定 id 不存在 ⇒ 拒绝启动，**不发布新版本**（`AC-004`）；
- **兼容**：默认（不传 `--universe-filter`）路径不解析绑定、不写新摘要键 → 与现状逐字节一致（`AC-006`）；
- **安全**：交集只会**收窄**清单，不会新增数据；湖分区不删（继承语义），不触碰台账；
- **恢复**：无状态变更 ⇒ 无需恢复路径；失败重跑幂等。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f011_export_universe_binding.py`：U1→U2→U3 三版旅程 | 集合含/不含 X 的 `lake_pair` 随绑定版本变化 |
| `AC-002` | integration | 同上：落选前后读台账与 manifest | 台账行数/区间零变化；X 的既有分区仍在 manifest |
| `AC-003` | unit | `tests/unit/test_f011_export_universe_binding.py`：两版 + 显式 id | 默认取最新；显式覆盖生效且结果不同 |
| `AC-004` | unit | `tests/unit/test_f011_cli_contract.py`：无冻结定义 / 未知 id | 非零退出 + 对应原因码；未落盘新版本 |
| `AC-005` | unit | `tests/unit/test_f011_export_universe_binding.py`：摘要字段 | `universe_id` 正确、`dropped_by_universe` 排序稳定；关闭时为 `null`/`[]` |
| `AC-006` | integration | 默认关闭过滤跑一次导出 | manifest 字段与分区集与改动前一致（同 fixture 对照） |
| `AC-007` | unit | 重复解析 + 查询计数探针 | 两次集合相同；不产生按 pair 的额外查询 |

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 绑定版本解析默认值 | 最新冻结定义 | 冻结定义是权威且不可变；不引入可变指针 | 「生效指针」另立 feature |
| 交集实现位置 | `export_admitted` 单点 | 与 `F008` 既有结构一致，避免第二处过滤 | — |
| manifest 不记绑定 | 只进运行摘要/日志 | `F002` 契约冻结；`pairs` 已是结果证据 | 更强的审计留痕单独评审 |
| 残余风险：`gate` 只遍历 `selected` | 本 feature 不修；落选 pair 的旧 ACTIVE 判定仍留在判定表 | 判定表只追加是 `F008` 的既定语义，交集已能覆盖其影响 | 若需要「判定随宇宙收窄」，另立 feature |
| 残余风险：多版本并存时的「最新」歧义 | 定序规则明确（冻结时刻 → `universe_id`）并写进摘要 | 可复现优先 | — |

## 10. 待确认设计问题

无
