---
kind: feature
id: F011
version: "0.2"
status: ready-for-development
branch: docs/F011-export-universe-binding
gate_version: 1
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: spec
created: 2026-09-25
updated: 2026-09-25
---

# F011：导出清单绑定当前宇宙版本（落选即移出）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR1.5（宇宙成员关系与 data_version 快照）
- **架构来源**：`docs/alphamill-architecture.md` §4.1.1（横截面只在同一 timestamp 的 point-in-time 宇宙内计算）、§三（`data_bridge/` 导出契约）
- **系统设计 / Contract 来源**：`docs/alphamill-integration.md` §1.2（导出清单与修订政策）；`F008` spec §3 边界场景、§5 状态机、§8 `Q-003`
- **上游决策**：ADR-0003（门禁不降级）、ADR-0007（研究快照绑定 dataset 独立版本）
- **功能类型**：backend / data-model
- **规格模式**：lite
- **变更类型**：MODIFIED（导出准入集合的解析口径；不改 manifest 契约、不改台账结构）
- **一句话意图**：让「跌出流动性阈值但仍可交易」的 pair 在**新版宇宙定义**中落选后真正离开导出清单，同时台账区间与历史数据一动不动——把 `F008` 已冻结的状态机补齐成可执行路径。

## 1. 问题、目标与非目标

### 问题

`F008` 冻结了状态机（spec §5）：`ACTIVE -> RETIRED` 有两条路——**退市**（台账追加 `valid_to`）与**在新版定义中落选**（台账不动），两者都移出导出清单。但实现只做了第一条：

- `export_admitted(conn, at, market_type=...)` = `universe_at(at)` ∩ **每 pair 最新判定 ACTIVE**，且 `universe_id=None`（取全表最新判定）；
- 落选的 pair 不会被 `gate` 重新判定（`gate` 只遍历 `definition.selected`），旧 ACTIVE 判定因此**永久有效**；
- 结果：落选 pair 继续留在导出清单里，与 spec/`Q-003` 的承诺相反。真实场景里这会把「已经跌出前 40 的 pair」当成长期成员喂给下游横截面算子。

### 目标

- 导出清单 = `universe_at(窗口终点)` ∩ 质量门 ACTIVE ∩ **当前宇宙版本的入选集合**；
- 「当前宇宙版本」有确定、可复现的解析口径，并可被显式指定（审计与回放）；
- 落选**只影响导出清单**：台账区间不写、历史分区不删、`symbol_map` 保持全量；重新入选即可回来；
- 没有可用宇宙版本时**拒绝启动**，而不是静默跳过交集（否则承诺形同虚设）。

### 非目标

- 不改 `F008` 的台账结构、触发器与 artifact 契约（`IR-002`）；
- 不改 `F002` 的 manifest schema 与对账语义（本 feature 只改「哪些单元格进清单」）；
- 不做「按每个历史时点重算全市场排名」的逐期 PIT 宇宙（`F008` `NFR-003` 的已知残余）；
- 不改质量门阈值、不放宽任何既有守卫。

## 2. 用户场景

### US-001：落选 pair 离开导出清单（Priority: P1）

作为数据管线的 owner，我希望跌出前 N 的 pair 在新版定义冻结后**不再进导出清单**，以便下游横截面研究不会把已跌出阈值的 pair 当成长期成员。

**为什么是这个优先级**：这是本 feature 唯一的最小有价值切片——没有它，`F008` 的状态机只兑现了一半，且缺陷是静默的（清单看起来正常）。

**独立测试**：冻结 `U1`（含 X）→ 准入 → 冻结 `U2`（不含 X，X 仍可交易）→ 断言导出准入集合不含 X、而 X 的台账区间与湖分区原样保留。

**验收场景**：

1. Given `U1` 含 `X` 且已过门（ACTIVE），when 冻结不含 `X` 的 `U2` 后跑导出准入解析，then `X` 不在集合内（`lake_pair` 层）。
2. Given 同一时刻 `X` 的台账区间（`valid_from`~`valid_to IS NULL`），when 上述落选发生，then 台账**零变化**（不追加、不关闭区间）。

### US-002：可复现的绑定与审计（Priority: P2）

作为排障者，我希望导出的绑定对象（宇宙版本）可显式指定并写进运行摘要，以便回答「这一版清单是按哪个宇宙算的」。

**为什么是这个优先级**：没有它，落选行为不可回放、事故只能靠猜；但它不阻塞 P1。

**独立测试**：显式传入 `--universe-id` 时以它为准；摘要 JSON 含该 id 与被落选剔除的 pair 列表。

**验收场景**：

1. Given 两个已冻结版本，when 显式指定较早的那个，then 绑定以指定版本为准（可复现）。
2. Given 指定了不存在的 id，when 解析，then 非零退出且原因码可区分。

### US-003：落选后重新入选可以回来（Priority: P3）

作为研究者，我希望落选的 pair 在后续定义中重新入选时能**无需人工修补**地回到导出清单，以便阈值波动不产生永久性缺口。

**为什么是这个优先级**：它验证「落选 ≠ 退市」这条不变量是双向的；P1 只需单向移除。

**独立测试**：`U2` 落选 → `U3` 重新入选 → 断言集合再次包含该 pair，且全程未写台账。

**验收场景**：

1. Given `X` 在 `U2` 落选、在 `U3` 重新入选，when 重新解析，then `X` 回到集合内（台账仍零变化）。

## 3. 范围与边界

### 范围内

- 导出准入集合的解析口径（新增「当前宇宙版本入选集合」这一交集项）；
- 「当前宇宙版本」的解析（默认取最新冻结定义）与显式覆盖（CLI/调用参数）；
- 不可用时的启动期拒绝与原因码；
- 运行摘要/日志的审计留痕（绑定 id + 被剔除 pair）。

### 范围外

- 生产调度单元是否开启准入过滤（`deployment/alphamill-export.service` 的 `--universe-filter`）——属**部署决策**，本 feature 只保证打开后语义正确（见 §8 `Q-002`）；
- 台账的库侧加固（唯一约束、退市窗口等）——`BACKLOG.md`「规划中」另有条目；
- 发现口径的上市时间语义（永续 vs 现货）——同上，且需重新冻结宇宙。

### 边界场景

- **没有任何冻结定义**：开启准入过滤时**拒绝启动**（不得静默按「全集」放行）。
- **同一 pair 在多个版本**：以被绑定版本的入选集合为准；旧版本的判定不参与。
- **落选 ≠ 退市**：落选不写 `valid_to`、不删湖分区；退市仍走 `F008` 既有路径。
- **落选 pair 的既有分区**：仍按 `F002` 语义继承（不因落选被删）——清单变窄不等于数据消失。
- **默认关闭**（不传 `--universe-filter`）：行为与现状**逐字节一致**（本 feature 不改变默认路径）。
- **绝不能发生**：为落选 pair 追加台账行、关闭其区间、或改写已发布历史分区。

## 4. 需求

### 功能需求

### Requirement: 导出清单绑定当前宇宙版本（`FR-001`）

系统应当把导出准入集合解析为 `universe_at(窗口终点)` ∩ 质量门 ACTIVE ∩ **被绑定宇宙版本的入选集合**（按 `db_symbol` 求交，与判定记录到湖内命名空间的既有桥一致）。

交集所用的版本与 `export_admitted` **既有的** `universe_id` 形参（它过滤的是**判定记录**）是两件事：本 feature 新增的形参名为 `bound_universe`（定义版本），两者各自独立、可同时给出。

#### Scenario: 落选即移出

- GIVEN `U1` 含 `X` 且 ACTIVE，`U2` 不含 `X`
- WHEN 绑定 `U2` 解析导出准入集合
- THEN `X` 的 `lake_pair` 不在集合内

### Requirement: 当前宇宙版本的解析与显式覆盖（`FR-002`）

系统应当默认把「当前宇宙版本」解析为**最新冻结**的 `UniverseDef`（按冻结时刻，同一时刻按 `universe_id` 定序），并允许调用方显式指定 `universe_id` 覆盖默认；显式指定的版本必须已冻结且存在。

#### Scenario: 显式绑定可复现

- GIVEN 两个已冻结版本
- WHEN 显式指定较早版本
- THEN 解析结果与「当时绑定该版本」一致

### Requirement: 不可用时的启动期拒绝（`FR-003`）

当开启准入过滤且无法解析出可用的宇宙版本（无冻结定义、或指定 id 不存在/未冻结）时，系统应当以非零退出拒绝启动，并给出可区分的原因码；不得静默退化为「不做交集」。

#### Scenario: 无冻结定义

- GIVEN 湖内没有任何冻结定义
- WHEN 开启准入过滤跑导出
- THEN 非零退出、原因码可区分，且未发布任何新版本

### Requirement: 绑定结果的审计留痕（`FR-004`）

系统应当在运行摘要与日志中记录本次绑定的 `universe_id` 以及因该交集而被剔除的 pair 列表，使「这一版清单按哪个宇宙算的」可事后回答。被剔除列表 `dropped_by_universe` 的精确定义是：**在不做交集时会进清单、但因绑定而被剔除的 `db_symbol`**，即 `{verdicts(ACTIVE) 且当前可交易} − selected(bound)`，按 `db_symbol` 升序、去重。

#### Scenario: 摘要可查

- GIVEN 一次绑定 `U2` 的导出
- WHEN 读取运行摘要
- THEN 含 `universe_id=U2` 与被剔除 pair 列表

### Requirement: 落选与退市分离（`FR-005`）

落选**不得**触发任何台账写入（不追加行、不关闭区间），也不得删除或改写该 pair 的既有湖分区与已发布历史；重新入选时无需人工修补即可回到清单。

#### Scenario: 落选后台账零变化

- GIVEN `X` 的台账区间为开区间
- WHEN `X` 在 `U2` 落选
- THEN 台账行数与内容零变化，湖分区原样继承

### 数据 / 实体需求

- **DR-001**：本 feature **不新增、不修改**任何持久化实体；`universe_membership` 只读。
- **DR-002**：导出 manifest 的 schema 与既有字段语义不变（`F002` 契约冻结）；被绑定的宇宙版本只出现在**运行摘要/日志**，不进 manifest。

### API / 接口需求

- **IR-001**：导出入口的 `--universe-filter` 语义扩展为「按当前宇宙版本绑定」；新增可选 `--universe-id <digest>` 显式覆盖。
- **IR-002**：运行摘要 dict 新增两个键：`universe_id`（被绑定版本）、`dropped_by_universe`（被剔除的 `db_symbol` 列表，排序稳定）；默认关闭过滤时二者分别为 `null` / `[]`。
- **IR-003**：无法解析绑定版本时以 `E_UNIVERSE_NOT_FROZEN`（无冻结定义）或 `E_UNIVERSE_NOT_FOUND`（指定 id 不存在）非零退出。

### 非功能需求

- **NFR-001**：绑定解析不得引入按 pair 的额外数据库往返（集合运算在内存完成；定义与台账各读一次）。
- **NFR-002**：**向后兼容**：不传 `--universe-filter` 时，导出结果与改动前在同一输入下**可观察等价**——manifest 的关键字段与分区集与改动前一致（不要求跨运行逐字节相同，因为导出本身会写新的 data_version 与 exported_at）。
- **NFR-003**：确定性：同一 `universe_id` + 同一窗口终点 ⇒ 同一准入集合（与调用顺序、字典序无关，输出排序稳定）。

## 5. 生命周期与不变量

```text
解析绑定版本: 显式 --universe-id > 最新冻结定义 > 拒绝启动（E_UNIVERSE_NOT_FROZEN）
导出准入集合 = universe_at(window_end) ∩ verdicts(ACTIVE) ∩ selected(bound_universe)
落选: 仅从上述交集剔除 —— 台账/湖分区/判定记录 均不动
重新入选: 下一版定义重新纳入 ⇒ 自动回到集合（无需写台账）
```

不变量：

- 本 feature **没有任何对 `universe_membership` 的写路径**（只读校验由测试与源码扫描共同锁定）；
- 落选 pair 的既有湖分区按 `F002` 语义继承，不因清单变窄而删除；
- 默认关闭过滤时，导出链路的可观察行为不变。

## 6. 成功与验收

### 成功标准

- **SC-001**：落选 pair 在新版定义冻结后不再出现在导出清单（真实库可复现）；
- **SC-002**：落选前后台账行数、区间与湖分区集合零变化；
- **SC-003**：绑定对象可复现（显式 id）且记录在运行摘要里。

### 验收清单

- [ ] **AC-001** (`FR-001`, `US-001`): `U1` 含 X → `U2` 不含 X 时，导出准入集合不含 X 的 `lake_pair`；`U3` 重新含 X 时又回到集合内 — tests: `tests/integration/test_f011_export_universe_binding.py`
- [ ] **AC-002** (`FR-005`, `DR-001`, `US-001`): 上述全过程 `universe_membership` 行数/区间零变化，X 的既有湖分区原样继承 — tests: `tests/integration/test_f011_export_universe_binding.py`
- [ ] **AC-003** (`FR-002`, `IR-001`, `US-002`): 默认取最新冻结定义；显式 `--universe-id` 时以指定版本为准（两个版本给出不同集合）— tests: `tests/unit/test_f011_export_universe_binding.py`
- [ ] **AC-004** (`FR-003`, `IR-003`): 无冻结定义时开启过滤 → 非零退出且码为 `E_UNIVERSE_NOT_FROZEN`；指定不存在的 id → `E_UNIVERSE_NOT_FOUND`；两种情况都未发布新版本 — tests: `tests/unit/test_f011_cli_contract.py`
- [ ] **AC-005** (`FR-004`, `IR-002`, `SC-003`): 运行摘要含被绑定 `universe_id` 与排序稳定的 `dropped_by_universe`；关闭过滤时为 `null`/`[]` — tests: `tests/unit/test_f011_export_universe_binding.py`
- [ ] **AC-006** (`NFR-002`): 不传 `--universe-filter` 时，同一 fixture 下 manifest 的 `pairs`/`partitions`/`skipped`/`rows` 与改动前一致（可观察等价）— tests: `tests/integration/test_f011_export_universe_binding.py`
- [ ] **AC-007** (`NFR-003`, `NFR-001`): 同一绑定 + 同一窗口终点重复解析得到同一集合；集合运算不产生按 pair 的额外查询 — tests: `tests/unit/test_f011_export_universe_binding.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：绑定解析（显式/默认/失败）、交集语义、摘要字段、确定性（`tests/unit/test_f011_export_universe_binding.py`）、CLI 契约与原因码（`tests/unit/test_f011_cli_contract.py`）。
- 集成测试：真实 scratch 库 + 临时湖上跑「三版定义」旅程（`tests/integration/test_f011_export_universe_binding.py`），覆盖 AC-001/002/006。
- 真实环境 / 手动验证：执行机上对**生产湖**跑一次绑定解析（只读、不发布），核对当前 35 对清单与摘要字段。

### 依赖

- 上游 Feature / Contract：`F008`（台账、artifact、verdicts、`export_admitted`）；`F002`（导出编排与 manifest 契约）。
- 下游消费者：`F003`（挖掘取数）、`F007`（ResearchSnapshot 绑定）。
- 外部 / 环境依赖：执行机 `qiaozhi-lt`（真实库/湖证据）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 「当前宇宙」用什么定义 | **最新冻结的 `UniverseDef`**（可按 `--universe-id` 覆盖） | 冻结定义是唯一权威且不可变；不引入可变指针（derive, don't store） | 若将来需要「生效指针」，另立 feature |
| 交集放在哪一层 | `export_admitted`（导出侧解析） | 台账与判定记录不动，交集是导出侧口径；`F007`/`F003` 消费 artifact 的路径不受影响 | — |
| 是否改 manifest 记录绑定 | **不改**（只进运行摘要/日志） | `F002` manifest 契约冻结；清单本身（`pairs`）已是结果证据 | 若审计需要更强留痕，单独评审 |
| 落选 pair 的湖分区 | 保留（按 `F002` 继承语义） | 删数据等于制造幸存者偏差（`F008` `Q-003`） | — |
| 默认关闭时行为变化 | 零变化（`NFR-002` 锁定） | 避免影响在跑的生产导出 | 生产开关由 owner 决策（`Q-002`） |

## 8. 待确认问题

- [x] Q-001: 「当前宇宙版本」如何解析才既可复现又不需要人工维护？ — 决策：默认取**最新冻结**的 `UniverseDef`（冻结时刻定序，同时刻按 `universe_id`），并支持显式 `--universe-id` 覆盖；不引入可变「生效指针」。
- [x] Q-002: 生产日常导出（`deployment/alphamill-export.service`）是否在本 feature 内打开 `--universe-filter`？ — 决策：**不在本 feature 内改生产单元**（它是部署行为、且当前生产判定的落选场景尚未发生）；本 feature 只保证开关打开后语义正确，开关本身由 owner 另行决定并登记。
