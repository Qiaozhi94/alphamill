---
kind: feature
id: F011
version: "0.2"
status: code-reviewing
status_evidence: G1 计划批准（owner 2026-09-26，按 tasks.md T001-T014）
branch: feat/F011-export-universe-binding
gate_version: 1
related_features: [F002, F008]
topics: [data-bridge, universe, export, contract]
doc_kind: spec
created: 2026-09-25
updated: 2026-09-26
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
- **变更类型**：MODIFIED（导出准入集合的解析口径；开启过滤时离开准入集合的 pair（落选/退市）按**截止日**继续产出历史分区，不再整体丢弃；不改 manifest schema、不改台账结构）
- **一句话意图**：让「跌出流动性阈值但仍可交易」的 pair 在**新版宇宙定义**中落选后真正离开导出准入集合（不再产出新分区），同时台账区间与历史分区一动不动——把 `F008` 已冻结的状态机补齐成可执行路径。

## 1. 问题、目标与非目标

### 术语

本 spec 中以下概念严格区分，「导出清单」一词**只**作为第一项的别名使用：

- **导出准入集合**（= 导出清单）：本次运行、某个 dataset 上**不限日期**产出分区的 `lake_pair` 集合 = `universe_at(at)` ∩ 质量门 ACTIVE ∩ `selected(bound)`，按窗口终点 `at` 现算；
- **截止日**：已离开导出准入集合、但判定为 ACTIVE 的 pair 的历史产出上界（UTC 日期，**含当日**）。落选 pair = 其**本次连续落选段**内各版本 `frozen_at` 的最早日期；退市 pair = 台账**派生可交易区间**（`materialize_intervals`：`delisted` 行终止前一行，或行上显式 `valid_to`）中 `at` 之前最后一个区间终点所在日（终点恰为某日 00:00 时取前一日）；两者兼有取较早者。分区日期 ≤ 截止日照常产出与对账，> 截止日不产出；
- **本轮产出集合**：本次运行实际新写/重写分区的 pair（导出准入集合 ∪ 有截止日且窗口内有 ≤ 截止日单元格的 pair）；
- **manifest `pairs`**：新版本内全部分区涉及的 pair = 本轮产出 ∪ 继承分区（含落选/退市 pair 截止日前的**历史**分区）。落选 pair 留在这里是正确的 point-in-time 语义——它在截止日前确实是成员。

「连续落选段」按 `FR-002` 的版本定序取：从被绑定版本向前、直到最近一个选中该 pair 的版本为止（不含）的那一段版本。用这一段的**最早**冻结日而不是被绑定版本自己的冻结日，是为了不让截止日随每次重新冻结向后漂移——否则 `U2` 落选、`U3` 仍落选时，绑定 `U3` 会把 `U2`~`U3` 之间本不该产出的数据补产出来。

### 问题

`F008` 冻结了状态机（spec §5）：`ACTIVE -> RETIRED` 有两条路——**退市**（台账追加 `valid_to`）与**在新版定义中落选**（台账不动），两者都移出导出清单。但实现只做了第一条：

- `export_admitted(conn, at, market_type=...)` = `universe_at(at)` ∩ **每 pair 最新判定 ACTIVE**，且 `universe_id=None`（取全表最新判定）；
- 落选的 pair 不会被 `gate` 重新判定（`gate` 只遍历 `definition.selected`），旧 ACTIVE 判定因此**永久有效**；
- 结果：落选 pair 继续留在导出清单里，与 spec/`Q-003` 的承诺相反。真实场景里这会把「已经跌出前 40 的 pair」当成长期成员喂给下游横截面算子。

### 目标

- 导出准入集合 = `universe_at(窗口终点)` ∩ 质量门 ACTIVE ∩ **被绑定宇宙版本的入选集合**；
- 「被绑定宇宙版本」有确定、可复现、不前视的解析口径，并可被显式指定（审计与回放）；
- 落选**只影响导出准入集合**：台账区间不写、截止日前的历史在增量与全量两种 mode 下都照常产出与对账（不依赖湖里已有内容）、`symbol_map` 保持全量；重新入选即可回来；
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
2. Given 指定了不存在的 id 或未冻结的草稿 id，when 解析，then 非零退出且原因码可区分（`E_UNIVERSE_NOT_FOUND` / `E_UNIVERSE_NOT_FROZEN`）。

### US-003：落选后重新入选可以回来（Priority: P3）

作为研究者，我希望落选的 pair 在后续定义中重新入选时能**无需人工修补**地回到导出清单，以便阈值波动不产生永久性缺口。

**为什么是这个优先级**：它验证「落选 ≠ 退市」这条不变量是双向的；P1 只需单向移除。

**独立测试**：`U2` 落选 → `U3` 重新入选 → 断言集合再次包含该 pair，且全程未写台账。

**验收场景**：

1. Given `X` 在 `U2` 落选、在 `U3` 重新入选，when 重新解析，then `X` 回到集合内（台账仍零变化）。

## 3. 范围与边界

### 范围内

- 导出准入集合的解析口径（新增「被绑定宇宙版本入选集合」这一交集项）；
- 被绑定版本的解析（默认规则见 `FR-002`）与显式覆盖（CLI/调用参数）；
- 不可用时的启动期拒绝与原因码；
- 离开导出准入集合的 pair（落选/退市）按截止日产出历史分区，增量与全量同一规则（`FR-005`）；
- 运行摘要/日志的审计留痕（绑定 id + 被剔除 pair）。

### 范围外

- 生产调度单元是否开启准入过滤（`deployment/alphamill-export.service` 与 `deployment/alphamill-fullexport.service` 的 `--universe-filter`）——属**部署决策**，本 feature 只保证打开后语义正确，并用测试锁定「两单元开关一致」（见 §8 `Q-002`）；
- 台账的库侧加固（唯一约束、退市窗口等）——`BACKLOG.md`「规划中」另有条目；
- 发现口径的上市时间语义（永续 vs 现货）——同上，且需重新冻结宇宙。

### 边界场景

- **没有任何冻结定义**：开启准入过滤时**拒绝启动**（不得静默按「全集」放行）。
- **同一 pair 在多个版本**：以被绑定版本的入选集合为准；旧版本的判定不参与。
- **落选 ≠ 退市**：落选不写 `valid_to`、不删湖分区，台账区间仍由 `F008` 维护；两者在导出侧用同一条截止日规则，只是截止日来源不同（冻结日 / 台账派生区间终点）。
- **落选 pair 的历史分区**：截止日及之前的单元格在增量与全量两种 mode 下都从源库产出并对账，之后的不产出；空湖重建、基线缺该 pair 时同样能导回历史——导出准入集合变窄不等于数据消失。
- **重新入选**：pair 在新版本中重新入选后不再有截止日。增量只导新窗口，不回填；**下一次全量**会一次性从源库补回落选期间（截止日到重新入选之间）已采集的数据，并发布一个内容变化的新版本，此后增量与全量稳定一致。这是有意的语义：湖回答「有哪些数据」，某一天某 pair 是否属于宇宙由版本历史回答（下游横截面按 point-in-time 宇宙取成员，见架构 §4.1.1「截面边界」），不由湖里有没有分区回答。
- **截止日之后的缺口**：属于策略排除，不记 `skipped`；截止日之前的空单元格是真实缺口，照常记 `skipped`（两种 mode 同一规则）。
- **历史窗口**（`--window-end` 早于最新定义的 `frozen_at`）：只能绑定 `frozen_at ≤ 窗口终点`（当时已生效）的定义，不得绑定当时尚未冻结的宇宙（前视）。
- **多口径并存**（冻结定义的 `criteria.exchange`/`criteria.market_type` 不止一种）：默认解析拒绝并要求显式 `--universe-id`，不得串线。
- **单给 `--universe-id` 而不开 `--universe-filter`**：参数错误，拒绝（不隐式开启过滤）。
- **默认关闭**（不传 `--universe-filter`）：与现状**可观察等价**（`NFR-002`），本 feature 不改变默认路径。
- **绝不能发生**：为落选 pair 追加台账行、关闭其区间、或改写已发布历史分区。

## 4. 需求

### 功能需求

### Requirement: 导出清单绑定当前宇宙版本（`FR-001`）

系统应当把导出准入集合解析为 `universe_at(窗口终点)` ∩ 质量门 ACTIVE ∩ **被绑定宇宙版本的入选集合**（按 `db_symbol` 求交，与判定记录到湖内命名空间的既有桥一致）。

交集所用的版本与 `export_admitted` **既有的** `universe_id` 形参（它过滤的是**判定记录**）是两件事：本 feature 新增的形参名为 `bound_universe`，类型为已解析的绑定对象（被绑定 `UniverseDef` + 版本链，用于算截止日；不是 id），两者各自独立、可同时给出。`bound_universe=None`（缺省）**保持 `F008` 原语义**——不做宇宙交集；版本解析由调用方（导出 CLI）完成后显式传入，交集函数本身不读湖、不做默认解析。

#### Scenario: 落选即移出

- GIVEN `U1` 含 `X` 且 ACTIVE，`U2` 不含 `X`
- WHEN 绑定 `U2` 解析导出准入集合
- THEN `X` 的 `lake_pair` 不在集合内

### Requirement: 被绑定宇宙版本的解析与显式覆盖（`FR-002`）

系统应当按以下规则解析被绑定版本（`at` = 本次运行的窗口终点，与导出窗口同一口径）：

1. **默认**：候选 = 全部 `frozen_at ≤ at` 且 `snapshot_at ≤ at` 的冻结定义（当时已生效的版本）；若其 `(criteria.exchange, criteria.market_type)` 不止一种 ⇒ 拒绝（`E_UNIVERSE_AMBIGUOUS`，要求显式指定）；否则按 `snapshot_at` 取最新，并列按 `frozen_at`、再按 `universe_id` 定序。候选为空 ⇒ 拒绝（`E_UNIVERSE_NOT_FROZEN`）。
2. **显式** `universe_id`：定义必须存在（否则 `E_UNIVERSE_NOT_FOUND`）、已冻结（否则 `E_UNIVERSE_NOT_FROZEN`）、且 `frozen_at ≤ at` 与 `snapshot_at ≤ at` 同时成立（否则 `E_UNIVERSE_LOOKAHEAD`，不许前视）。

**过滤**用 `frozen_at`（版本何时生效），**定序**用 `snapshot_at`（宇宙反映的市场时点）：前者保证历史回放与当时实际绑定一致、并与截止日同一口径；后者保证晚冻结的旧快照不覆盖更新的快照。`freeze_definition(frozen_at=...)` 允许注入冻结时刻，代码不保证冻结晚于求值，所以两个条件都要显式检查。

同一解析同时给出**版本链**：与被绑定版本同口径、`frozen_at ≤ at`、按上述定序排在被绑定版本及之前的全部冻结定义，用于计算落选 pair 的截止日（§1 术语）。

#### Scenario: 显式绑定可复现

- GIVEN 两个已冻结版本
- WHEN 显式指定较早版本
- THEN 解析结果与「当时绑定该版本」一致

#### Scenario: 历史窗口不前视

- GIVEN `U1.frozen_at ≤ t < U2.frozen_at`（即使 `U2.snapshot_at < t`）
- WHEN 以 `--window-end t` 默认解析
- THEN 绑定 `U1`；显式指定 `U2` 被拒绝（`E_UNIVERSE_LOOKAHEAD`）

### Requirement: 不可用时的启动期拒绝（`FR-003`）

当开启准入过滤且无法解析出可用的宇宙版本（`FR-002` 任一拒绝分支，或定义/冻结记录损坏）时，系统应当以非零退出拒绝启动，并给出可区分的原因码（`IR-003`）；不得静默退化为「不做交集」。**启动期**指：绑定在一次运行内只解析一次，发生在刷新 `symbol_map` 与任何 dataset 导出之前，同一次运行的全部 dataset 共用同一个被绑定版本；拒绝时湖内零写入（不发布 `symbol_map`、不发布任何新版本）。本要求约束导出 CLI（唯一生产入口）；库函数 `export_dataset(universe_filter=True)` 不给 `bound_universe` 时保持 `F008` 原语义，摘要 `universe_id` 为 `null`，不做宇宙交集这一事实可见。

#### Scenario: 无冻结定义

- GIVEN 湖内没有任何冻结定义
- WHEN 开启准入过滤跑导出
- THEN 非零退出、原因码可区分，且未发布 `symbol_map` 与任何新版本

### Requirement: 绑定结果的审计留痕（`FR-004`）

系统应当在每个 dataset 的运行摘要与日志中记录本次绑定的 `universe_id` 以及因该交集而被剔除的 pair 列表，使「这一版导出准入集合按哪个宇宙算的」可事后回答。被剔除列表 `dropped_by_universe` 的精确定义是：**在不做宇宙交集时会进导出准入集合、但因绑定而被剔除的 `db_symbol`**，即 `{判定 ACTIVE 且在本 dataset 的 market_type 命名空间于 at 可交易} − selected(bound)`，按 `db_symbol` 升序、去重；它与导出准入集合由同一次计算、同一份判定与台账读数产出。

**留痕载体**：摘要是导出 CLI 的 stdout JSON 行，生产由 systemd 单元捕获进 journald（保留期受执行机 journald 配置约束）；manifest 不记（`DR-002`）。超出 journald 保留期的长期审计不在本 feature 范围（`tasks.md` §5 后移）。

#### Scenario: 摘要可查

- GIVEN 一次绑定 `U2` 的导出
- WHEN 读取运行摘要
- THEN 含 `universe_id=U2` 与被剔除 pair 列表

### Requirement: 落选与退市分离、截止日产出（`FR-005`）

落选**不得**触发任何台账写入（不追加行、不关闭区间），也不得改写已发布版本；重新入选时无需人工修补即可回到导出准入集合。

开启过滤且给出被绑定版本时，对 pair 分区的 dataset，单元格 `(pair, date)` 的产出判据**在增量与全量两种 mode 下相同**：

- pair ∈ 导出准入集合 ⇒ 产出；
- pair 有截止日（落选或退市，且判定 ACTIVE）⇒ `date ≤ 截止日` 时产出，之后不产出；
- 其余 pair ⇒ 不产出。

产出即照常走源库对账与修订检测；版本组成仍按 `F002`（增量 = 基线继承 + 窗口产出；全量 = 源库全量产出）。`skipped` 用同一判据：只对「会产出」的单元格判缺，基线 `skipped` 条目在增量模式按同一判据保留或移除。这同时修正了 `F008` 过滤实现在全量模式下丢弃退市 pair 历史的行为（仅在给出被绑定版本时生效；`bound_universe=None` 的 `F008` 路径不变）。

#### Scenario: 落选后台账零变化

- GIVEN `X` 的台账区间为开区间
- WHEN `X` 在 `U2` 落选
- THEN 台账行数与内容零变化，湖分区原样继承

#### Scenario: 全量模式不丢落选 pair 的历史

- GIVEN `X` 在被绑定版本中落选，截止日为 `c`
- WHEN 分别以增量、全量、空湖首导三种方式 `--universe-filter` 导出
- THEN 三者的新版本都含 `X` 在 `c` 及之前的全部分区（与源库对账一致），都不含 `X` 在 `c` 之后的分区，`skipped` 中 `X` 的条目只落在 `c` 及之前

#### Scenario: 截止日前的源库修订会被全量导出吸收

- GIVEN `X` 截止日前某日的数据在源库被修订
- WHEN `--mode full --universe-filter` 导出
- THEN 新版本中该分区为修订后的内容，并出现在 `revision_diff`

### 数据 / 实体需求

- **DR-001**：本 feature **不新增、不修改**任何持久化实体；`universe_membership` 只读。
- **DR-002**：导出 manifest 的 schema 与既有字段语义不变（`F002` 契约冻结）；被绑定的宇宙版本只出现在**运行摘要/日志**，不进 manifest。

### API / 接口需求

- **IR-001**：导出入口的 `--universe-filter` 语义扩展为「按被绑定宇宙版本求交」；新增可选 `--universe-id <digest>` 显式覆盖。`--universe-id` 只能与 `--universe-filter` 同时给出，单独给出由参数解析拒绝（非零退出），不隐式开启过滤。
- **IR-002**：运行摘要 dict 新增两个键：`universe_id`（被绑定版本）、`dropped_by_universe`（被剔除的 `db_symbol` 列表，排序稳定）；默认关闭过滤时二者分别为 `null` / `[]`（键始终存在）。
- **IR-003**：无法解析绑定版本时以退出码 2（不可重试，`RestartPreventExitStatus=2`）拒绝，stderr 行首带原因码（`FATAL: <code>: <消息>`）：

  | 情形 | 原因码 |
  |---|---|
  | 默认解析：无 `frozen_at ≤ at` 且 `snapshot_at ≤ at` 的冻结定义（含湖内根本没有定义） | `E_UNIVERSE_NOT_FROZEN` |
  | 显式 id 的定义文件不存在 | `E_UNIVERSE_NOT_FOUND` |
  | 显式 id 存在但未冻结（草稿） | `E_UNIVERSE_NOT_FROZEN` |
  | 显式 id 的 `frozen_at > at` 或 `snapshot_at > at`（前视） | `E_UNIVERSE_LOOKAHEAD`（新增） |
  | 默认解析时冻结定义存在多种 `(exchange, market_type)` 口径 | `E_UNIVERSE_AMBIGUOUS`（新增） |
  | 定义或冻结记录损坏（非法 JSON / 键集合 / schema_version / id 不符） | `E_UNIVERSE_ARTIFACT` |

### 非功能需求

- **NFR-001**：绑定解析不得引入按 pair 的额外数据库往返（集合运算在内存完成；定义与台账各读一次）。
- **NFR-002**：**向后兼容**：不传 `--universe-filter` 时，导出结果与改动前在同一输入下**可观察等价**——manifest 的关键字段与分区集与改动前一致（不要求跨运行逐字节相同，因为导出本身会写新的 data_version 与 exported_at）。
- **NFR-003**：确定性：同一 `universe_id` + 同一窗口终点 ⇒ 同一准入集合（与调用顺序、字典序无关，输出排序稳定）。

## 5. 生命周期与不变量

```text
解析绑定版本（每次运行一次，早于 symbol_map 与任何 dataset）:
  显式 --universe-id（存在∧已冻结∧frozen_at, snapshot_at ≤ at）> 默认（单口径∧frozen_at, snapshot_at ≤ at 中 snapshot_at 最新）> 拒绝启动（IR-003）
导出准入集合 = universe_at(at) ∩ verdicts(ACTIVE) ∩ selected(bound_universe)
落选/退市: 移出上述集合，按截止日产出历史（date ≤ 截止日），增量与全量同一判据 —— 台账/判定记录 均不动
重新入选: 下一版定义重新纳入 ⇒ 自动回到集合（无需写台账）
```

不变量：

- 本 feature **没有任何对 `universe_membership` 的写路径**（只读校验由测试与源码扫描共同锁定）；
- 落选/退市 pair 截止日前的分区在增量、全量、空湖重建下都能从源库产出，不因导出准入集合变窄而丢失；
- 单元格产出与 `skipped` 判缺在增量与全量两种 mode 下用同一判据；
- 同一次运行的全部 dataset 绑定同一个宇宙版本；
- 默认关闭过滤时，导出链路的可观察行为不变。

## 6. 成功与验收

### 成功标准

- **SC-001**：落选 pair 在新版定义冻结后不再进入导出准入集合、截止日后不再产出分区（manifest `pairs` 中只保留其截止日前的历史分区；真实库可复现）；
- **SC-002**：落选前后台账行数、区间与湖分区集合零变化；
- **SC-003**：绑定对象可复现（显式 id）且记录在运行摘要里。

### 验收清单

- [x] **AC-001** (`FR-001`, `US-001`): `U1` 含 X → `U2` 不含 X 时，导出准入集合不含 X 的 `lake_pair`；`U3` 重新含 X 时又回到集合内 — tests: `tests/integration/test_f011_export_journey.py`
- [x] **AC-002** (`FR-005`, `DR-001`, `US-001`): 上述全过程 `universe_membership` 行数/区间零变化；增量、全量、空湖首导三种导出下，新版本均含 X（落选）与 Y（退市）截止日及之前的全部分区且对账通过、均无截止日之后的分区，`skipped` 在增量与全量间一致（连跑「增量→全量→增量」不因 `skipped` 翻转产生新版本）；截止日前的源库修订被全量导出吸收；连续落选段跨 `U2`→`U3` 时截止日仍为 `U2` 的冻结日；X 在后续版本重新入选后，首次全量新增其落选期间的分区，之后「增量→全量」不再产生新版本 — tests: `tests/integration/test_f011_export_journey.py`
- [x] **AC-003** (`FR-002`, `IR-001`, `US-002`): 默认在 `frozen_at ≤ at` 的冻结定义中取 `snapshot_at` 最新者（晚冻结的旧快照不胜出；`snapshot_at ≤ t < frozen_at` 的版本不被历史 `--window-end t` 绑定）；显式 `--universe-id` 时以指定版本为准（两个版本给出不同集合）；单给 `--universe-id` 不开 `--universe-filter` 被参数解析拒绝 — tests: `tests/unit/test_f011_export_universe_binding.py`、`tests/unit/test_f011_cli_contract.py`
- [x] **AC-004** (`FR-003`, `IR-003`): `IR-003` 表六种情形逐一触发：退出码 2、stderr 含对应原因码；且均未发布 `symbol_map` 与任何新版本 — tests: `tests/unit/test_f011_cli_contract.py`
- [x] **AC-005** (`FR-004`, `IR-002`, `SC-003`): 运行摘要含被绑定 `universe_id` 与排序稳定的 `dropped_by_universe`；关闭过滤时为 `null`/`[]` — tests: `tests/unit/test_f011_export_universe_binding.py`
- [x] **AC-006** (`NFR-002`): 不传 `--universe-filter` 时，同一 fixture 下 manifest 的 `pairs`/`partitions`/`skipped`/`rows` 与改动前一致（可观察等价）— tests: `tests/integration/test_f011_export_journey.py`
- [x] **AC-007** (`NFR-003`, `NFR-001`): 同一绑定 + 同一窗口终点重复解析得到同一集合；集合运算不产生按 pair 的额外查询 — tests: `tests/unit/test_f011_export_universe_binding.py`
- [x] **AC-008** (`FR-003`, `FR-005`, `Q-002`): 多 dataset 运行只解析一次绑定、全部 dataset 摘要的 `universe_id` 相同；`deployment/alphamill-export.service` 与 `deployment/alphamill-fullexport.service` 的 `--universe-filter` 开关一致 — tests: `tests/unit/test_f011_cli_contract.py`
- [x] **AC-009** (`FR-001`): `export_admitted(conn, at)`（不给 `bound_universe`）保持 `F008` 语义——`F008` 既有测试零修改全绿 — tests: `tests/integration/test_f008_quality_gate.py`、`tests/integration/test_f008_export_integration.py`

取证（2026-09-26，执行机 `qiaozhi-lt`，需求分支 `feat/F011-export-universe-binding`）：上列三个测试文件
`tests/unit/test_f011_export_universe_binding.py`（28）、`tests/unit/test_f011_cli_contract.py`（17）、
`tests/integration/test_f011_export_journey.py`（8，真实 scratch 库）全部通过（含代码检视循环 24 的 7 条回归）；`F008` 集成测试零修改
21 passed / 1 xfailed（AC-009）；统一质量门 `tools/verify.py` exit=0（1633 passed / 32 skipped / 1 xfailed）。AC-006 的默认路径另以改动前代码
（main@80c1a53）在同一 fixture 上实跑的 pairs/rows/skipped/value_digest 作基准对照。
关键判据的变异验证 6/6 判红（截止日取最早冻结日、截止日含当日、生效过滤含 `frozen_at`、判缺过截止日判据、
单元格产出用 `allows` 而非 `covers`、CLI 在刷新 `symbol_map` 之前解析）。真实环境只读核对：生产湖默认绑定
`sha256:6d85a249…`，spot/perp 准入各 35 对，与 `F008` 口径逐一相同（当前无落选，符合 `Q-002` 判断）。

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：绑定解析（显式/默认/失败/前视/多口径）、交集语义、摘要字段、确定性（`tests/unit/test_f011_export_universe_binding.py`）、CLI 契约、原因码与部署单元一致性（`tests/unit/test_f011_cli_contract.py`）。
- 集成测试：真实 scratch 库 + 临时湖上跑「三版定义」旅程（`tests/integration/test_f011_export_journey.py`），覆盖 AC-001/002/006；增量、全量、空湖首导都跑，另含退市 pair 与源库修订。
- 回归：`F008` 既有测试零修改全绿（AC-009）。
- 真实环境 / 手动验证：执行机上对**生产湖**跑一次绑定解析（只读、不发布），核对当前 35 对清单与摘要字段。

### 依赖

- 上游 Feature / Contract：`F008`（台账、artifact、verdicts、`export_admitted`）；`F002`（导出编排与 manifest 契约）。
- 下游消费者：`F003`（挖掘取数）、`F007`（ResearchSnapshot 绑定）。
- 外部 / 环境依赖：执行机 `qiaozhi-lt`（真实库/湖证据）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 被绑定版本默认怎么选 | `frozen_at ≤ at` 的冻结定义中 `snapshot_at` 最新者（并列按 `frozen_at`→`universe_id`）；多口径并存则拒绝 | 冻结定义是唯一权威且不可变；按生效时刻过滤才能让历史回放与当时一致，按市场时点定序才不会让旧快照覆盖新快照；不引入可变指针（derive, don't store） | 若将来需要「生效指针」或多口径并行导出，另立 feature |
| 交集放在哪一层 | `verdicts` 内单一函数同时产出准入集合与 `dropped`；`export_admitted` 为其薄包装，`bound_universe=None` 保持 `F008` 原语义 | 台账与判定记录不动，交集是导出侧口径；`F007`/`F003` 消费 artifact 的路径与 `F008` 既有调用不受影响 | — |
| 是否改 manifest 记录绑定 | **不改**（只进运行摘要/日志，journald 留存） | `F002` manifest 契约冻结；manifest `pairs` 含继承的历史分区，**不能**回答「按哪个宇宙算的」，审计只靠摘要 | 超出 journald 保留期的长期审计另立 feature |
| 落选/退市 pair 的历史（owner 2026-09-26 拍板） | 截止日规则：截止日及之前照常产出并对账，之后不产出；增量与全量同一判据 | 删数据等于制造幸存者偏差（`F008` `Q-003`）；从源库产出而非继承湖内分区，空湖重建与源库修订都成立 | — |
| 截止日取连续落选段的最早冻结日 | 而非被绑定版本自身的冻结日 | 后者会随每次重新冻结后移，补产出落选期间的数据 | — |
| 残余风险：截止日之后仍留在基线里的分区（仅在显式回绑更早版本等非常规操作下出现） | 增量按 `F002` 继承、全量不再产出 | 不改写已发布版本；全量本就按源库重组版本 | — |
| 默认关闭时行为变化 | 零变化（`NFR-002` 锁定） | 避免影响在跑的生产导出 | 生产开关由 owner 决策（`Q-002`） |

## 8. 待确认问题

- [x] Q-001: 「当前宇宙版本」如何解析才既可复现又不需要人工维护？ — 决策（第 2 轮检视后修订）：默认取 `frozen_at ≤ 窗口终点` 的冻结定义中 `snapshot_at` 最新者（并列按 `frozen_at`→`universe_id`），多口径并存即拒绝；支持显式 `--universe-id` 覆盖（同样不许前视，`E_UNIVERSE_LOOKAHEAD`）；不引入可变「生效指针」。
- [x] Q-002: 生产导出（日常 `deployment/alphamill-export.service` 与每周日 `deployment/alphamill-fullexport.service`）是否在本 feature 内打开 `--universe-filter`？ — 决策：**不在本 feature 内改生产单元**（它是部署行为、且当前生产判定的落选场景尚未发生）；本 feature 只保证开关打开后语义正确。两单元的开关**必须一致**：只开日常增量时，周日全量不过滤会重新产出落选 pair 的新分区，过滤形同虚设——一致性由 AC-008 测试锁定，开关本身由 owner 另行决定并登记。
