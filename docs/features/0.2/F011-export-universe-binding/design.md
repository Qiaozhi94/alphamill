---
kind: feature
id: F011
version: "0.2"
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: design
created: 2026-09-25
updated: 2026-09-26
---

# F011：导出清单绑定当前宇宙版本 - 设计

## 0. 输入与约束

- **行为契约**：`spec.md`（`FR-001`~`FR-005`、`AC-001`~`AC-009`；术语见 spec §1「术语」）
- **PRD / Architecture / System Design**：`docs/alphamill-architecture.md` §4.1.1；`docs/alphamill-integration.md` §1.2
- **ADR / 上游 Contract**：ADR-0003（门禁不降级）、ADR-0007（快照绑定）；`F008` `IR-002`（artifact canonical JSON）、`F002`（导出/manifest 契约）
- **实现约束**：`src/**/*.py` ≤350 行（`docs/SOP.md`；`exporter.py` 现已 350 行，**净增必须 ≤0**）；唯一门禁入口 `tools/verify.py`；台账只读；默认关闭过滤时与现状可观察等价（`NFR-002`）

## 1. 技术概要与影响面

| # | 文件 | 变更 |
|---|---|---|
| 1 | `data_bridge/universe/binding.py`（**新增**） | `resolve_bound_universe(at, *, universe_id=None, lake_root=None) -> UniverseDef`：按 spec `FR-002` 解析被绑定版本（枚举 `defs_dir` 下 `*.frozen.json` → `load_freeze` + `load_definition`） |
| 2 | `data_bridge/universe/verdicts.py` | 新增 `export_admission(...) -> Admission`（唯一交集点，同时产出准入集合与 `dropped`）；`export_admitted` 改为其薄包装，新增 `bound_universe: UniverseDef \| None = None`，`None` 保持 `F008` 原语义 |
| 3 | `data_bridge/universe/errors.py` | 新增 `UniverseAmbiguousError`（`E_UNIVERSE_AMBIGUOUS`）；按该文件头约定只增不改 |
| 4 | `data_bridge/export_policy.py` | `merge_partitions` 增 `admitted` 形参：全量 + 过滤时继承非准入 pair 的基线分区（`FR-005`）；skipped 同理 |
| 5 | `data_bridge/exporter.py` | `export_dataset` 增 `bound_universe`；`_export_one` 的准入块（现 176-184 行）改调 `export_admission`；摘要合并两键。**净增 ≤0 行**：不够时先把 `_admitted_only`（现 144-156 行）迁到 `export_policy.py` |
| 6 | `data_bridge/cli.py` | `--universe-id`；过滤开启时在 `_refresh_symbol_map()` **之前**一次性解析绑定并传给所有 dataset；拒绝时 stderr 带原因码 |

影响面：导出准入集合的口径（默认关闭时不变）、全量 + 过滤的版本组成（非准入 pair 由丢弃改为继承）、CLI 契约（新增一个可选参数）、运行摘要（新增两个键）、错误码（新增一个）。**不改**：台账、artifact、manifest schema、质量门阈值、`symbol_map` 全量语义、`F008` 既有调用的语义。

## 2. 架构与模块边界

```
cli.main (--universe-filter / --universe-id)
  ├─ at = 窗口终点（一次定值，所有 dataset 共用）
  ├─ binding.resolve_bound_universe(at, universe_id=...)   # 失败 → 退出码 2，湖内零写入
  ├─ _refresh_symbol_map()
  └─ for dataset: exporter.export_dataset(..., universe_filter=True, bound_universe=bound)
        └─ _export_one
             ├─ verdicts.export_admission(conn, at, market_type=spec.market_type, bound_universe=bound)
             │     = universe_at(at) ∩ verdicts(ACTIVE) ∩ selected(bound)  → Admission(admitted, dropped)
             └─ export_policy.merge_partitions(mode, baseline, produced, admitted=admission.admitted)
```

- `binding` 只答「绑哪一版」，不碰台账与判定、不连库；
- `export_admission` 是**唯一交集点**：`admitted` 与 `dropped` 由同一次判定读数、同一次台账读数、同一 `market_type`、同一 `at` 算出，导出侧不做任何集合运算；
- `exporter` 只负责把 `Admission` 带进分区选择、版本组成与摘要。

### 库 API 与 CLI 的分工

- **CLI 是唯一生产入口**，负责 `FR-003` 的 fail-closed：开过滤就必须解析出绑定，否则拒绝启动。
- 库函数 `export_dataset(universe_filter=True)` 与 `export_admitted(conn, at)` 在**不给** `bound_universe` 时保持 `F008` 原语义（不做宇宙交集），摘要 `universe_id=null` 使这一点可见；`F008` 既有测试因此零修改（`AC-009`）。

## 3. 数据模型与 Migration

**无 migration、无实体变更**。`universe_membership` 与 `universe_quality_verdicts` 均只读（`DR-001`）；被绑定版本从既有 `_metadata/universe_defs/*.json` 与 `*.frozen.json` 解析，不新建索引或指针文件。

`Admission`（`verdicts.py` 内 frozen dataclass，不落盘）：

| 字段 | 类型 | 语义 |
|---|---|---|
| `admitted` | `frozenset[str]` | 导出准入集合（`lake_pair`） |
| `dropped` | `tuple[str, ...]` | `{ACTIVE ∧ 本 market_type 命名空间于 at 可交易的 db_symbol} − selected(bound)`，升序去重；`bound is None` 时为 `()` |

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 接口 | 变更 | 说明 |
|---|---|---|
| `exporter --universe-filter` | 语义扩展 | 由「台账 ∩ ACTIVE」变为「台账 ∩ ACTIVE ∩ 被绑定版本入选集」 |
| `exporter --universe-id <digest>` | 新增（可选） | 显式绑定；只能与 `--universe-filter` 同给，单给由 `parser.error` 拒绝（argparse 退出码 2） |
| `binding.resolve_bound_universe(at, *, universe_id=None, lake_root=None)` | 新增 | 规则见 spec `FR-002`；失败抛 spec `IR-003` 表中的 `UniverseError` 子类 |
| `verdicts.export_admission(conn, at, *, market_type=None, universe_id=None, bound_universe=None)` | 新增 | 返回 `Admission`；`universe_id` 仍是既有的**判定记录**过滤，与 `bound_universe`（定义版本）互不干扰 |
| `verdicts.export_admitted(..., bound_universe=None)` | 新增关键字参数 | `= export_admission(...).admitted`；`None` ⇒ `F008` 原语义，不读湖、不做默认解析 |
| `export_policy.merge_partitions(mode, baseline, produced, *, admitted=None)` | 新增关键字参数 | `mode == "full"` 且 `admitted` 非 `None` 时，继承基线中 pair ∉ `admitted` 的分区；其余情况与现状一致 |
| `exporter.export_dataset(..., bound_universe=None)` | 新增关键字参数 | 仅在 `universe_filter=True` 时生效 |
| 运行摘要 dict | 新增 `universe_id` / `dropped_by_universe` | 键始终存在；关闭过滤或未绑定时 `null` / `[]`（`IR-002`） |

### 失败码与 stderr

绑定解析失败统一退出码 2（`EXIT_FATAL`，systemd `RestartPreventExitStatus=2` 不重试），stderr 形如 `FATAL: E_UNIVERSE_NOT_FROZEN: <消息>`——原因码取 `exc.code`，测试以此断言。六种情形见 spec `IR-003` 表，抛出点：

| 情形 | 抛出点 |
|---|---|
| 默认解析无候选 | `binding`：`UniverseNotFrozenError` |
| 显式 id 不存在 | `load_definition` → `_read_json`：`UniverseNotFoundError` |
| 显式 id 为草稿 | `require_frozen`：`UniverseNotFrozenError` |
| 显式 id 前视 | `binding`：`WindowError`（`E_UNIVERSE_WINDOW`） |
| 默认解析多口径 | `binding`：`UniverseAmbiguousError`（新增） |
| 定义/冻结记录损坏 | `load_definition` / `load_freeze`：`UniverseArtifactError` |

### Event / Trace Contract

不新增事件类型。`F008` 的 `universe.member_changed` 语义不变——**落选不是成员变更**（台账不动），因此**不得**为落选写事件；绑定结果只进运行摘要/日志（`DR-002`）。

## 5. Runtime、Workflow 与并发

```text
cli.main:
  if args.universe_id and not args.universe_filter: parser.error(...)
  if args.universe_filter:
      window_end = args.window_end or 今日 00:00Z        # 定值后传给全部 dataset，免跨午夜漂移
      at = combine(as_date(window_end), 00:00, UTC)      # 与 _export_one 的 PIT 时点同一口径
      bound = resolve_bound_universe(at, universe_id=args.universe_id)   # 失败 → FATAL: <code>，return 2
  _refresh_symbol_map()
  for dataset: export_dataset(..., window_end=window_end, universe_filter=..., bound_universe=bound)

resolve_bound_universe(at, universe_id):
  explicit -> load_definition(id)（NOT_FOUND）→ require_frozen（NOT_FROZEN）→ snapshot_at ≤ at（WINDOW）
  default  -> frozen = [def for *.frozen.json]; cands = [d for d in frozen if d.snapshot_at ≤ at]
              cands 为空 → NOT_FROZEN；{(criteria.exchange, criteria.market_type)} > 1 → AMBIGUOUS
              max by (snapshot_at, frozen_at, universe_id)

_export_one（过滤开启且给了 bound）:
  admission = export_admission(conn, at, market_type=spec.market_type, bound_universe=bound)
  produced  = 仅 admission.admitted 的单元格
  merged    = merge_partitions(mode, baseline, produced, admitted=admission.admitted)
  summary  |= {universe_id: bound.universe_id, dropped_by_universe: list(admission.dropped)}
```

- 判定表、台账各读一次，集合运算在内存完成（`NFR-001`）；定义文件在 CLI 启动时读一次；
- 导出仍是单进程批处理，并发安全性与现状一致（导出自身有 REPEATABLE READ 快照）；不引入新的锁或共享状态。

### 全量 + 过滤的版本组成（`FR-005`）

| mode | 准入 pair | 非准入 pair（落选/退市） | 非 pair 分区 dataset |
|---|---|---|---|
| incremental | 基线继承 + 新窗口分区 | 基线继承，无新分区 | 与现状一致 |
| full | 源库全量重导 | **基线分区与 skipped 条目原样继承**（现状：丢弃） | 与现状一致 |

- `guard_full_shrink` 以 `merged`（含继承）为 `current`，落选不会触发收缩守卫误报；
- 继承分区与基线字节一致，不产生 `revision_diff`；它们不再与源库对账（spec §7 残余风险）。

## 6. UI 与可观测性

无 UI。可观测性：

- 日志：绑定版本 `INFO`（`universe_id` + `snapshot_at` + 解析方式 explicit/default）；被剔除 pair 逐条 `INFO`（`db_symbol` + 原因 `not_in_universe_selection`）；
- 运行摘要：`universe_id`、`dropped_by_universe`（`IR-002`）——本 feature 唯一的留痕面。摘要是 CLI 的 stdout JSON 行，生产由 systemd 单元捕获进 journald，保留期随执行机 journald 配置；manifest 不改（`DR-002`），且 manifest `pairs` 含继承的历史分区，不能替代摘要回答「按哪个宇宙算的」。

## 7. 失败、恢复、安全与兼容

- **fail-closed**：绑定解析在 `symbol_map` 刷新与任何 dataset 之前完成；任一拒绝 ⇒ 退出码 2、湖内零写入（`AC-004`）；
- **兼容（默认路径）**：不传 `--universe-filter` 时不解析绑定；摘要多出 `universe_id: null` / `dropped_by_universe: []` 两键（`IR-002`），manifest 与现状可观察等价（`NFR-002`/`AC-006`）；
- **兼容（`F008` 调用方）**：`export_admitted(conn, at)`、`export_dataset(universe_filter=True)` 不给 `bound_universe` 时语义不变（`AC-009`）；
- **安全**：交集只会**收窄**导出准入集合，不会新增数据；湖分区在两种 mode 下都不删，不触碰台账；
- **恢复**：无状态变更 ⇒ 无需恢复路径；失败重跑幂等。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f011_export_universe_binding.py`：U1→U2→U3 三版旅程 | 导出准入集合含/不含 X 的 `lake_pair` 随绑定版本变化 |
| `AC-002` | integration | 同上：增量与全量两种 mode 各跑一次 | 台账行数/区间零变化；新 manifest 含 X 全部基线分区（与基线一致）、无 X 新窗口分区 |
| `AC-003` | unit | `tests/unit/test_f011_export_universe_binding.py`：多版定义（含晚冻结的旧快照、历史 `at`）+ 显式 id；`tests/unit/test_f011_cli_contract.py`：单给 `--universe-id` | 默认取 `snapshot_at ≤ at` 最新；显式覆盖生效且结果不同；参数错误退出 |
| `AC-004` | unit | `tests/unit/test_f011_cli_contract.py`：spec `IR-003` 六种情形 | 退出码 2 + stderr 原因码；`symbol_map` 与新版本均未落盘 |
| `AC-005` | unit | `tests/unit/test_f011_export_universe_binding.py`：摘要字段 | `universe_id` 正确、`dropped_by_universe` 排序稳定且只含本 market_type 可交易者；关闭时为 `null`/`[]` |
| `AC-006` | integration | 默认关闭过滤跑一次导出 | manifest 字段与分区集与改动前一致（同 fixture 对照） |
| `AC-007` | unit | 重复解析 + 查询计数探针 | 两次集合相同；判定与台账各一次查询 |
| `AC-008` | unit | `tests/unit/test_f011_cli_contract.py`：两个 dataset 一次运行（`resolve_bound_universe` 调用计数）+ 读两份 `deployment/*export.service` | 解析恰好一次、两份摘要 `universe_id` 相同；两单元 `--universe-filter` 同有或同无 |
| `AC-009` | integration | `tests/integration/test_f008_quality_gate.py`、`tests/integration/test_f008_export_integration.py` | 零修改全绿 |

仓库目前没有自动行数门禁：`exporter.py`/`binding.py`/`verdicts.py` ≤350 行由 `tests/unit/test_f011_cli_contract.py` 内一条行数断言锁定（tasks `T006`）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 绑定版本解析默认值 | `snapshot_at ≤ at` 的冻结定义中最新者；多口径拒绝 | 按市场时点定序才不会让晚冻结的旧快照胜出、不会让历史窗口前视 | 「生效指针」/多口径并行导出另立 feature |
| 解析放在哪里 | CLI 启动期一次，传 `UniverseDef` 对象 | 保证启动期拒绝、全 dataset 同版本；交集函数不依赖 `lake_root` | — |
| 交集实现位置 | `export_admission` 单点，`export_admitted` 为薄包装 | `admitted` 与 `dropped` 同源，避免导出侧第二处集合运算；`F008` 签名兼容 | — |
| 解析逻辑放哪个模块 | 新增 `binding.py` | `exporter.py` 已达 350 行硬上限；`definition.py` 只管单个定义的读写 | — |
| 全量 + 过滤的非准入 pair | 继承基线分区 | 否则每周全量会抹掉落选/退市 pair 的历史（幸存者偏差，`F008` `Q-003`） | 源库复核另立 feature |
| manifest 不记绑定 | 只进运行摘要/日志（journald） | `F002` 契约冻结；manifest `pairs` 含继承历史，不是绑定证据 | 长期审计另立 feature |
| 残余风险：`gate` 只遍历 `selected` | 本 feature 不修；落选 pair 的旧 ACTIVE 判定仍留在判定表 | 判定表只追加是 `F008` 的既定语义，交集已能覆盖其影响 | 若需要「判定随宇宙收窄」，另立 feature |
| 残余风险：两生产单元开关不一致 | `AC-008` 测试锁定一致性 | 只开增量时周日全量会重新产出落选 pair 的新分区 | 开关由 owner 决定（spec `Q-002`） |
| 形参命名 | 新参数用 `bound_universe`，与既有 `universe_id`（判定过滤）区分 | 同名会让两个语义在一个调用点混叠 | — |

## 10. 待确认设计问题

无
