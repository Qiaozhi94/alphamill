---
kind: feature
id: F014
version: "0.2"
status: doc-reviewing
branch: docs/F014-selection-tail-preset
gate_version: 1
related_features: [F002, F003, F007, F012, F013]
topics: [factor-factory, generation, window, holdout, cli]
doc_kind: spec
created: 2026-09-29
updated: 2026-09-29
---

# F014：F012 选择尾窗 preset 增量（selection_tail_1h_2y_v1）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR3.3（预注册选择/留出）、FR3.9（canonical 只用预注册窗口）；M2 批量闭环前置。
- **架构来源**：`docs/alphamill-architecture.md` §4.4（研究快照、生成绑定）、§7.1（执行机边界）。
- **上游决策**：owner 2026-09-29 裁决 F013 文档检视 P0-1 选 (a)；载体为 `BACKLOG.md`「规划中」表
  「F012 选择尾窗 preset 增量（selection_tail_1h_2y_v1）」行（验收①–⑤）。消费契约见
  [F013 design](../F013-batch-evaluation/design.md) §4.1「F012 前置增量」段。ADR-0003/0007。
- **功能类型 / 规格模式 / 变更类型**：backend + data-model / full / MODIFIED（F012 窗口预设、CLI、config/run 持久化；
  已收口的 F012 文档不倒写，本增量独立立号）。
- **一句话意图**：让生成批次在绑定 cutoff 之前留出一段生成侧从未读过的选择尾窗，使 F013 能在同一绑定上做诚实的选择期评测。

## 1. 问题、目标与非目标

### 问题

F012 只有 `default_1h_2y` 一个窗口预设，`window.end = cutoff`（`generators/base.py:57-63`）。
F013 要求快照与生成绑定逐字段一致且选择窗起点 ≥ 生成窗终点，于是选择窗 `[cutoff, cutoff)` 恒为空；
现有两次 50 候选 run 都属此类，F013 无合规输入。

### 目标

新增版本化预设 `selection_tail_1h_2y_v1`：生成窗终点前移 `L + H·Δ`，CLI/config/run 三处持久化并互验
预设名、L、H 与派生窗口；生成、训练、预筛的湖读取上界严格为生成窗终点。
在执行机产出一个 3–5 候选的合规 completed run，交 F013 T002 预检。

### 非目标

不改绑定 cutoff、成员、symbol map、宇宙或日历；不实现 F013 的评测侧（折、标签、快照）；
不做「评测 cutoff 晚于生成绑定」（方案 b，M2 之后另立）；不改生成算法、预筛规则或 smoke 判定口径。

## 2. 用户场景

### US-001：生成带选择尾窗的批次（Priority: P1）

作为运营者，我希望用 `--window selection_tail_1h_2y_v1 --selection-hours L --label-horizon-bars H`
生成候选，以便 F013 在同一绑定上拿到生成侧未读过的选择窗 `[S,E)`。

**为什么是这个优先级**：F013 真实闭环的唯一前置阻塞。

**独立测试**：夹具湖 + 显式绑定跑 `mine`/`seed`，核对 config/run 的窗口与参数、读取上界与互验。

**验收场景**：

1. Given 显式绑定 cutoff=C（UTC 整点）、L=4320、H=1（Q-001 口径），when 以新预设生成，then `window.end = C − 4321h`、
   `start = end − 730d`，config/run 均记录 preset/L/H/`[S,E)=[end, C−1h)`，读取的 1m 开盘时间全部 < end。
2. Given 新预设缺 L 或 H、值非正整数，或默认预设带 L/H，when 解析命令，then 用法错误退出 2，不建运行目录。
3. Given 新预设但 cutoff 非 UTC 整点、或合成 config 的 `resample ≠ "1h"`，when 生成，then 在建面板前结束且不发布 completed
   （错误映射见 FR-001）。
4. Given 篡改 run.json 或 config.json 任一侧的 preset/L/H/window，when 以校验入口加载，then 拒绝。

### US-002：默认预设零变化（Priority: P1）

作为运营者，我希望不带新参数时生成行为、config_digest 与既有 run 读取完全不变。

**为什么是这个优先级**：F012 已收口，回归不可破坏既有证据链。

**独立测试**：默认预设的 config 字节与增量前一致；v1/v2 run.json 仍可读。

**验收场景**：

1. Given 同一输入与默认预设，when 生成，then config.json 字节与 config_digest 与增量前相同。
2. Given 入库金样 `tests/fixtures/f014/`（v1 manual 与 v2 alphagen completed run 各一份 run.json + config.json），
   when 加载，then 成功且 `window_preset` 为 null（旧产物），不补造参数。`reports/generation/` 下的真实 run 被
   `.gitignore` 忽略，只作执行机补充证据，不作单元测试输入。

## 3. 范围与边界

### 范围内

| 改动点 | 需求 | 验收 |
|---|---|---|
| `generators/base.py:57-63` `Window.from_preset` 只认默认预设 | FR-001 | AC-001/005 |
| `cli.py:63` `--window` choices 与 `cli.py:111-117` window_config | FR-002/003 | AC-001/003 |
| config 持久化（`mine_dispatch.compose_config` → `run_store.write_config`）与 config_digest | FR-003 | AC-001/003 |
| run.json schema（`registry/run_schema.py` 严格字段集）与两个 run 写入方 | FR-004 | AC-001/003 |
| 互验加载入口与 `show --run` | FR-005 | AC-001 |
| 读取上界（`mine_dispatch.prepare_panel` → `lake_tensor.py:115-124` `reader.read`） | FR-006 | AC-002 |
| `generators/smoke_gate.py:169-174` 默认 smoke 窗口 | FR-007 | AC-003 |
| 执行机合规 run 与事件时间口径比对 | NFR-002 | AC-004 |

### 范围外

v1 只支持 resample=1h、Δ=1h、单个正整数 H、UTC 整点 cutoff；显式绑定（`explicit_tuples`）之外的绑定模式对新预设拒绝。
不做多 horizon、其他频率、按日历/交易时段的窗口；不改 reader 的 `as_of`（仍为绑定 cutoff，见 FR-006 已知限制）。
不迁移、不改写既有 run；F012 已收口文档不改。F013 三件套只改指向本 Feature 的依赖指针（design §4.1、T003 已在本 Feature
文档检视时同步；spec §7、T002 由 T012 改），不动其他内容。

### 边界场景

L+H 使 `start` 早于湖起点（现为 2024-09-10）时照常按 `end − 730d` 派生、不截断，实际可用生成数据不足 730 天，
由运行摘要与执行机证据显示实际首根时间。派生 `end ≤ start` 不可能（730d 固定）；湖在 `[start,end)` 内零行按
F012 既有 invalid_binding 拒绝。snapshot 模式绑定：CLI 不注入 resolver，`validate_binding` 先抛
`SnapshotResolverUnavailableError`（`binding_checks.py:233-236`），任一预设都按 F012 既有路径 rejected/invalid_binding，
走不到预设解析；`_generate`（注入 resolver 的未来调用方）与 `load_verified_run` 对新预设再做显式模式检查，作为纵深防护。

## 4. 需求

### 功能需求

### Requirement: 版本化尾窗预设（`FR-001`）

当请求 `selection_tail_1h_2y_v1` 时，系统应要求 L（选择窗长度，正整数小时）与 H（标签 horizon，正整数 bar），Δ=1h，
派生 `end = cutoff − L − H·Δ`、`start = end − 730d`、`resample=1h`，以及 F013 消费的 `S = end`、`E = cutoff − H·Δ`，
满足 `E − S = L`。新预设另要求 cutoff 为 UTC 整点（分/秒/微秒为 0），在解析窗口时检查，不等到建完面板。
默认预设保持 `[cutoff − 730d, cutoff)` 且不接受 L/H，不加整点要求。未知预设名拒绝。
解析期（参数之外）的新预设违约抛 `SchemaValidationError`，沿用 F012 `finish_exception`（`manifest_builder.py:98-117`）
映射：`mine` 记 rejected/invalid_config，`seed`（`config_phase=False`）记 failed；两者都在建面板前结束、不发布 completed。

### Requirement: CLI 参数（`FR-002`）

当解析 `seed`/`mine` 时，`--window` 的可选值应来自预设注册表；新增 `--selection-hours INT`、`--label-horizon-bars INT`，
仅在新预设下必填、默认预设下出现即用法错误。参数错误在创建运行目录前以退出码 2 结束。

### Requirement: config 持久化与摘要（`FR-003`）

当生成开始时，系统应把预设名、L、H、派生 window 与 `selection_tail=[S,E)` 写入 config.json 的 `window` 对象，
随 config_digest 一起入身份；默认预设的 `window` 对象保持现有四键 `{preset,start,end,resample}`，字节不变。
用户 `--config` 中的 `window` 键不得覆盖 CLI 派生值（沿用现状）。新预设下合成 config 若含顶层 `resample`
（面板实际按它重采样，`mine_dispatch.py:140-157`；`needs_panel` 生成器必含，默认 `"1h"`），必须等于 `"1h"`，
否则按 FR-001 的解析期违约映射拒绝；默认预设不加此检查。

### Requirement: run 持久化（`FR-004`）

当发布 run.json 时，系统应写 schema v3，新增 `window_preset={name,selection_hours,label_horizon_bars,selection_start,selection_end}`
（五键齐全；默认预设下 `name="default_1h_2y"`，其余四项为 null）；completed 运行必填。
非 completed（rejected/failed/partial）：窗口已解析则按同一形态填写，未解析（如参数/绑定阶段即拒绝）为 null。
读取 v1/v2 时 `window_preset` 补 null 且不得推断参数；v1/v2 文件携带 v3 字段即非法。
两个 run 写入方（CLI `manifest_builder` 与 `alphagen_generation.write_generation_manifest`）一致。后者由函数自身按传入的
`resolved` 把 `window_config(resolved)` 注入 `config["window"]`（覆盖调用方同名键，调用方不负责），以 run_store 只计算、
不写盘的 `config_digest`（与 `write_config` 共用，先剔除 `_R` 键）求内存侧摘要，并在写盘前以 `verify_run_window` 自检；
自检及之前任一步失败（含非显式绑定）即抛 `SchemaValidationError`，不写 config.json/run.json。自检通过后 `finalize_run`
失败时 config.json 已落盘、run.json 不发布，不产生 completed run（design §5「第二写入方」）。

### Requirement: 三处互验（`FR-005`）

当加载 completed run 供下游消费时，系统应提供唯一校验入口 `load_verified_run`：config.json 字节摘要等于
run.config_digest；由 `window_preset` + `run.binding.cutoff_time`（仅显式绑定有此字段；非显式绑定一律拒绝）重算的
window 与 run.window、config.window 逐项相等；run 与 config 的 preset/L/H/`[S,E)` 相等。任一不等拒绝并指明字段。
窗口比对逻辑只有一个函数 `verify_run_window`：`load_verified_run` 内部复用它；CLI 发布 run.json 前直接以它自检
（此时 run.json 尚未落盘，不做字节摘要比对，摘要由 `write_config` 返回值保证）。消费方共三处且都只经
`load_verified_run`：`show --run`（completed）、F013 T003 的输入加载、F014 T011 执行机取证。

### Requirement: 读取上界（`FR-006`）

当以任一预设生成时，生成、训练、预筛只能经 `prepare_panel` 构建的面板取数：reader 请求 `[start,end)`（1m 开盘时间），
不得新增其他湖读取路径。新预设（cutoff、start、end 均为整点，resample=1h）下重采样标签 ∈ `(start, end]`，
面板构建后断言无标签 > end，否则失败关闭。默认预设不加该断言：重采样左闭右标签（`lake_tensor.py:65`），cutoff 非整点时
最末标签可 > cutoff，现为照常生成；为守 US-002 零行为变化不收紧，该口径问题记入后移。
`as_of` 维持绑定 cutoff：双时间轴成员可含 `available_at ∈ [end, cutoff]` 的对 end 前事件的修订，作为已知限制
在执行机证据中计数披露；改为 `as_of=end` 需另评审。

### Requirement: smoke 口径不变（`FR-007`）

当运行 ADR-0001 smoke 判定时，`default_smoke_config`/`default_smoke_window` 继续固定默认预设；本增量只适配调用签名，不改判定。

### 非功能需求

- **NFR-001**：F012/F003 既有单元/集成测试与 `python3 tools/verify.py` 全绿；默认预设 config_digest 与候选可复现断言不变。
  升 v3 必然触及的既有断言只允许下列修订，不得放宽其他断言：`tests/unit/test_f012_cli_contract.py:60` 的 volatile 集合
  加入 `window_preset`、`:67` 版本字面量 2→3；`tests/unit/test_f012_run_schema.py:84-85` 改为版本 3 与集合 `{1,2,3}`、
  `:99` 版本字面量 2→3；构造 completed `GenerationRun` 的测试夹具补默认预设 `window_preset`；
  `tests/integration/test_f003_generation_run.py:193-200` 只允许把 `SnapshotRefBinding` 改为显式绑定、把手写 1 天
  `Window` 改为按预设派生的 `resolved`（config 不必补 window 键，由函数注入）；`:207-214`（207 行 `load_run`，208-214 行 status/hostname/device/counts/universe 断言）一律不放宽。
- **NFR-002**：在执行机 `qiaozhi-lt` 以新预设生成 3–5 候选 completed run（显式绑定、1h、日历 continuous_24_7/UTC），
  用 F007 `research_snapshot.freeze_members` 同一函数按有数据分区重算成员 `event_time_min/max`，与绑定声明逐字段相等；
  开发机 skip 不算证据。
- **NFR-003**：不放宽 F012 绑定校验、不改 cutoff/成员，不读线上修订态、不触碰交易接口。

## 5. 生命周期与不变量

不适用新增状态机：沿用 F012 运行状态 `completed|rejected|failed|partial`。
不变量：`E − S = L`；`S = window.end`；`E + H·Δ = cutoff`；新预设下生成面板最大标签 ≤ `window.end`；
默认预设下 `window.end = cutoff` 且 `window_preset` 五键齐全、参数四项为 null；config.window 与 run.window_preset
由同一 `ResolvedWindow` 产生。

## 6. 成功与验收

### 成功标准

- **SC-001**：F013 T002 拿到的新 run 通过其 preset 互验与事件时间比对，无需手改任何 JSON。
- **SC-002**：默认预设与既有 run 的行为、摘要、读取零回归。

### 验收清单

以下 tests 路径为计划文件，此阶段不创建测试或伪造通过证据。

- [ ] **AC-001** (`FR-001`, `FR-002`, `FR-003`, `FR-004`, `FR-005`): 派生窗口公式与 `E−S=L` 正确；L/H 缺失、非正、非整数、布尔或默认预设携带 L/H 均退出 2 且无运行目录；新预设下 cutoff 非 UTC 整点、`--config` 给 `resample="30min"` 或 `"4h"` 均在建面板前结束（`mine` 为 rejected/invalid_config、`seed` 为 failed，都无 completed），同样输入的默认预设不受影响；snapshot 绑定走 invalid_binding；默认预设 `window_preset` 五键齐全、四项 null，少键即 schema 拒绝；分别篡改 run.json 的 window/window_preset、config.json 的 window（含重算摘要后改 run.config_digest 不一致）、把 binding 换成非显式均被 `load_verified_run` 拒绝；`write_generation_manifest` 覆盖调用方传入的 `config["window"]` 为 `window_config(resolved)`，非显式绑定时抛 `SchemaValidationError` 且 run 目录下无 config.json/run.json；config 含 `_R` 键（如 `hostname`）时 `run_store.config_digest` 与 `write_config` 返回值相等 — tests: `tests/unit/test_f014_window_preset.py`、`tests/unit/test_f014_cli_window.py`、`tests/unit/test_f014_run_window_record.py`
- [ ] **AC-002** (`FR-006`): 以新预设生成时 reader 请求上界等于 window.end、返回行开盘时间全部 < end、面板最大标签 ≤ end；负对照把 end 改为 cutoff 时该检测必须失败；尾窗注入极值不改变候选与面板；默认预设在非整点 cutoff 夹具上不触发标签断言（行为同增量前） — tests: `tests/integration/test_f014_tail_read_bound.py`
- [ ] **AC-003** (`FR-003`, `FR-004`, `FR-007`, `NFR-001`): 默认预设 config 字节与 config_digest 与增量前金样相同；入库金样 `tests/fixtures/f014/`（v1 manual 取自 `manual-20260925T112312220871Z-2570ce64`、v2 alphagen 取自 `alphagen-20260927T140500683819Z-67053132`，各 run.json + config.json）可读、`window_preset=null` 且 legacy 路径 `load_verified_run` 通过；smoke 默认窗口不变；NFR-001 所列既有断言只按许可项修订 — tests: `tests/unit/test_f014_run_window_record.py`、`tests/unit/test_f014_cli_window.py`
- [ ] **AC-004** (`NFR-002`, `FR-005`, `FR-006`): 执行机新预设 run 为 completed、入册 3–5、`load_verified_run` 通过；源日历为 `continuous_24_7`/UTC、绑定 mode 为 `explicit_tuples`、`config.resample == config.window.resample == run.window.resample == "1h"`；每成员 event_time_min/max 与 `freeze_members` 重算值相等；记录双时间轴成员 `available_at ≥ end` 且事件时间 < end 的行数 — tests: `tests/integration/test_f014_executor_run.py`
- [ ] **AC-005** (`FR-001`, `FR-006`): start 早于湖起点时不截断，面板实际首根标签 = 湖首根 1m 开盘所在小时 + 1h（右标签），运行摘要与执行机证据显示实际可用跨度 < 730 天 — tests: `tests/unit/test_f014_window_preset.py`、`tests/integration/test_f014_executor_run.py`

## 7. 测试、依赖与决策

### 测试策略

先写 AC-001/002/003 红灯测试，再实现。开发机跑 `python3 tools/verify.py`；AC-004 在执行机以
`ALPHAMILL_INTEGRATION=1` 跑，skip 不算验收。读取上界用 reader 打桩记录请求与返回并配负对照，避免只靠推理。

### 依赖

- **已存在**：F012 CLI/manifest/run_store、F003 binding/lake_tensor、F002 reader、F007 `freeze_members`（仅测试侧调用）。
- **下游**：F013 T002 以本 Feature 合入提交与 AC-004 的 run 为输入；F013 T003 只经 `load_verified_run` 加载 run/config
  并完成 preset 互验（F013 design §4.1 已指向本入口）；F013 批量配置的 selection/H 必须等于本 run 的 `[S,E)`/H。

### 决策与风险

| 决策 / 风险 | 结论与处置 |
|---|---|
| 另立 F014 而非改 F012 文档 | F012 已收口；沿 F009/F010/F011 的后续增量惯例独立立号 |
| 默认预设零字节变化 | config.window 对默认预设保持四键；新字段只在新预设出现 |
| run.json 升 v3 | 严格字段集（`run_schema._mapping` 要求键集相等）下只能升版本；沿 v1→v2 的补缺省模式 |
| start 早于湖起点 | 不截断，保持 2y 语义可比；实际跨度如实显示 |
| as_of 仍为 cutoff | 改 as_of 可能让回填数据不可见而改变生成输入；本增量只计数披露，另评审 |
| L/H 取值 | 已定 H=1、L=4320（Q-001）；F013 批量配置须逐项相等；测试夹具可用其他值，但不作口径 |
| 默认预设非整点 cutoff 的标签越界 | F012 既有行为；本增量不收紧（守零变化），后移另评 |

## 8. 待确认问题

- [x] Q-001: AC-004 执行机合规 run 的 L 与 H 取值（同时成为 F013 真实小批的预注册 selection/H） — 决策：H=1、L=4320（180 天）；按现 cutoff 2026-09-10 实际生成数据约 1.5 年（owner 2026-09-29 采纳建议值）
