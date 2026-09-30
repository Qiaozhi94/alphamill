---
kind: feature
id: F014
version: "0.2"
related_features: [F002, F003, F007, F012, F013]
topics: [factor-factory, generation, window, contracts]
doc_kind: design
created: 2026-09-29
updated: 2026-09-29
---

# F014：F012 选择尾窗 preset 增量 — 技术设计

> Owner: Georg | [行为契约](spec.md) | [任务](tasks.md)

## 0. 输入与约束

消费契约：`BACKLOG.md`「规划中」表 F012 选择尾窗 preset 行验收①–⑤；F013 design §4.1「F012 前置增量」段
（`end = cutoff − L − H·Δ`、`start = end − 730d`、`S = end`、`E = cutoff − H·Δ`、`E − S = L`、三处互验、读取上界）。
约束：绑定 cutoff/成员不变；默认预设零字节变化；只读湖；F012 已收口文档不倒写。以下接口均为设计，尚未实现。

代码基线（main@cca44e0）：

- `generators/base.py:57-63` `Window.from_preset` 只认 `DEFAULT_WINDOW_PRESET`，`end = cutoff_time`。
- `cli.py:62-64` `--window` choices 仅默认预设；`cli.py:111-117` 组装 `window_config={preset,start,end,resample}`，
  经 `mine_dispatch.compose_config` 覆盖用户 `window` 键后进入 config_digest（`cli.py:132`、`cli.py:230` `write_config`）。
- `registry/run_schema.py`：run.json v2，`GenerationRun.window: base.Window`（三键），`_mapping` 要求键集严格相等。
- `mine_dispatch.prepare_panel:154-164` 以 `[window.start, window.end)` 调 `build_tensor`，重采样频率取
  config 顶层 `resample`（`mine_dispatch.py:140-157`，不是 `window.resample`），后者在
  `lake_tensor.py:115-124` 调 `reader.read(start, end, as_of=cutoff)`；重采样左闭右标签（`lake_tensor.py:65`）。
  生成/训练/预筛只用该面板。另一处湖读取 `binding_checks.py:92-98` 为 `[cutoff, cutoff)` 空区间存在性校验，不产生数据。
- `binding_checks.py:233-236`：CLI 不注入 snapshot resolver，snapshot 绑定先抛 `SnapshotResolverUnavailableError`
  （`BindingValidationError` 子类）→ rejected/invalid_binding。
- `manifest_builder.finish_exception:98-117`：`SchemaValidationError` 仅在 `config_phase`（= `mine` 且未进入生成器）
  记 invalid_config，`seed` 记 failed。
- `alphagen_generation.write_generation_manifest:150-163` 是第二个 run 写入方，接收 `window: Window`、自行 `write_config`，
  绕过 CLI；唯一调用方为 `tests/integration/test_f003_generation_run.py:193-200`（传 `SnapshotRefBinding`、手写 1 天窗口、
  config 仅 `{"generator":"alphagen"}`）。
- `manifest_builder._print_summary:162-176` 只对 `needs_panel` 生成器打印单行 JSON；`test_f012_cli_contract.py:105` 取最后一行解析。
- `smoke_gate.py:169-174` 的默认 smoke 配置/窗口固定默认预设，生产 CLI 不调用（仅测试与 smoke 流程）。

## 1. 技术概要与影响面

| 区域 / 契约 | 去向 | 本次影响 |
|---|---|---|
| `generators/base.py` 预设派生 | 修改 | 预设注册表 + 参数化派生；默认预设结果不变 |
| `registry/window_record.py` | 新增 | config.window / run.window_preset 的构造、重算与三处互验、`load_verified_run` |
| `registry/run_schema.py` | 修改 | run.json v3 `window_preset`；v1/v2 补 null 读取 |
| `cli.py` | 修改 | `--window` choices、`--selection-hours`/`--label-horizon-bars`、发布前自检、`show --run` 用校验入口 |
| `manifest_builder.py`、`generators/alphagen_generation.py` | 修改 | 两个 run 写入方填 `window_preset`；`_print_summary` 在现有 JSON 对象内加 `window` 字段；`write_generation_manifest` 见 §5「第二写入方」 |
| `mine_dispatch.prepare_panel` | 修改 | 新增关键字 `label_upper_bound: datetime | None = None`，非空时断言面板标签（失败关闭）；默认预设传 None |
| `lake_tensor.build_tensor`/`reader.read` | 不改 | 上界本就由 `end` 决定；由测试证明 |
| `smoke_gate.py` | 适配签名 | 判定口径不变 |
| 既有 F012/F003 测试 | 许可修订 | 仅 spec NFR-001 列出的版本字面量、volatile 集合、夹具补键，以及 `test_f003_generation_run.py:193-200` 改为显式绑定 + 按预设派生窗口 |
| F013 | 下游只读消费 | F013 design §4.1 与 T003 已改为经 `load_verified_run` 加载（本轮只改指针）；T012 再把 spec §7 与 T002 的载体从 BACKLOG 行改指本 spec |

无 SQL migration、无 UI、无新服务。

## 2. 架构与模块边界

- `base.py` 拥有「名 → 派生窗口」的纯函数：`WINDOW_PRESETS = ("default_1h_2y", "selection_tail_1h_2y_v1")`、
  `WindowPresetParams(selection_hours:int, label_horizon_bars:int)`、`ResolvedWindow(window, preset, params|None,
  selection:tuple[datetime,datetime]|None)`、`resolve_window(name, *, cutoff_time, params=None)`。
  `resolve_window` 对新预设检查参数与 cutoff 为 UTC 整点，违约抛 `SchemaValidationError`；默认预设不检查整点。
  `Window.from_preset(name, *, cutoff_time, params=None)` 保留并返回 `resolve_window(...).window`，旧调用不改。
- `registry/window_record.py`（叶子，依赖 base/run_schema/canonical）拥有持久化形态：`window_config(resolved)`、
  `preset_info(resolved)`、`verify_run_window(run, config)`、`load_verified_run(run_dir)`。
  窗口比对逻辑只在 `verify_run_window` 一处；`load_verified_run` 复用它并加字节摘要与绑定检查。
  CLI 发布前自检直接调 `verify_run_window`；`show --run`、F013 T003、F014 T011 只经 `load_verified_run`。
- 读取上界只在 `prepare_panel` 一个收口点断言；不在训练/预筛处重复取湖。

## 3. 数据模型与 Migration

**派生规则**（Δ=1h，参数须为 `int` 且非 `bool`、≥1）：

| 预设 | window.start | window.end | selection `[S,E)` |
|---|---|---|---|
| `default_1h_2y` | cutoff − 730d | cutoff | null（不接受参数） |
| `selection_tail_1h_2y_v1` | end − 730d | cutoff − L·Δ − H·Δ | `[end, cutoff − H·Δ)`，`E − S = L` |

时间均为 UTC，持久化用 `canonical.utc_iso`。新预设要求 cutoff 为 UTC 整点，故 start/end/S/E 均为整点。
start 不截到湖起点（现湖起点 2024-09-10，新预设 start 早 L+H；实际首根由面板决定，见 §6）。
Q-001 口径 L=4320、H=1、cutoff 2026-09-10T00:00Z：end=2026-03-13T23:00Z，start=2024-03-13T23:00Z，
`[S,E)=[2026-03-13T23:00Z, 2026-09-09T23:00Z)`，实际可用生成数据约 549 天。

**config.json `window`**：

- 默认预设：保持 `{preset,start,end,resample}` 四键，字节不变 ⇒ config_digest 不变。
- 新预设：`{preset,start,end,resample,params:{selection_hours,label_horizon_bars},selection_tail:{start:S,end:E}}`。

**run.json v3**：`RUN_SCHEMA_VERSION=3`，`RUN_SCHEMA_VERSIONS={1,2,3}`，新增顶层可空字段
`window_preset: WindowPresetInfo | None = None`，`WindowPresetInfo={name, selection_hours, label_horizon_bars,
selection_start, selection_end}`，五键齐全（`_mapping` 键集严格相等，`run_schema.py:227-234`）；默认预设
`name="default_1h_2y"`、其余四项 null。`_V3_FIELDS=("window_preset",)`：v2 读取补 null，
v2 文件出现该字段非法；v1 先按现逻辑升 v2 再补。`_validate_terminal`：v3 completed 必须有 `window_preset`；
新预设要求 binding 为显式模式并由 `binding.cutoff_time` 重算 window 与 `window_preset.selection_*` 相等。
非 completed：窗口已解析（`state.window` 已设）则按同一形态填写，否则 null。既有 run 不迁移。

**测试金样**（`tests/fixtures/f014/`，T008 入库）：从本机 `reports/generation/`（`.gitignore:69` 忽略，开发机/CI 不存在）
复制 v1 manual `manual-20260925T112312220871Z-2570ce64` 与 v2 alphagen `alphagen-20260927T140500683819Z-67053132`
的 run.json + config.json 原字节；默认预设 config 金样在实现前由 main@cca44e0 生成。真实 run 只作执行机补充证据。

## 4. 接口、Contract 与 Event

```text
alphamill-generate {seed|mine} --generator G --binding PATH --seed INT
    [--window {default_1h_2y,selection_tail_1h_2y_v1}]
    [--selection-hours INT --label-horizon-bars INT] [--config PATH] ...
```

- 组合规则在 `build_parser` 之后、`_run_generation` 之前校验：新预设缺任一参数、默认预设带任一参数、值 ≤0 →
  `parser.error`（退出 2，不建运行目录）。`type=int` 拒非整数。
- `verify_run_window(run, config) -> ResolvedWindow`：纯比对，不读盘；cutoff 取 `run.binding.cutoff_time`，
  binding 非 `ExplicitSnapshotBinding`（`SnapshotRefBinding` 无 cutoff 字段）即拒；`resolve_window(run.window_preset
  或 legacy 默认, cutoff, params)` 重算后要求 `== run.window`、`window_config(resolved) == config["window"]`、
  `preset_info(resolved) == run.window_preset`。legacy（`window_preset=null`）只允许 config.window 为默认四键形态。
- `load_verified_run(run_dir) -> VerifiedRun(run, config, resolved, legacy)`：仅接受 completed；读 config.json 字节，
  `sha256_prefixed(bytes) == run.config_digest`，再调 `verify_run_window`；legacy 返回 `preset="default_1h_2y"`、`legacy=True`。
  不等抛 `SchemaValidationError("<field> mismatch")`。
- `show --run`：completed 运行走 `load_verified_run`，其他状态沿用 `load_run`；错误码沿用 `main` 映射
  （schema 版本未知 2，其余 FactorFactoryError 1）。非显式绑定的 completed run 现不存在（CLI 无 resolver 生成不了）。
- 事件：生成事件信封不变（`EVENT_SCHEMA_VERSION=1`）；窗口信息只在 run/config，不写入事件。

## 5. Runtime、Workflow 与并发

`_generate` 顺序：`validate_binding`（CLI 下 snapshot 绑定在此即 invalid_binding）→ 新预设且非显式绑定则
`SchemaValidationError`（纵深防护，供未来注入 resolver 的调用方）→ `resolve_window`（新预设参数与 cutoff 整点）→
`window_config` 进 `compose_config` → 新预设检查合成 config 的顶层 `resample`（若有）等于 `"1h"` → 其余不变。
上述解析期 `SchemaValidationError` 按 `finish_exception` 映射：`mine` rejected/invalid_config、`seed` failed，
均在建面板前、不发布 completed。`write_config` 之后、`finalize_run` 之前，以 `verify_run_window(manifest, config)` 自检；
失败按既有异常路径收尾为 failed。`prepare_panel(..., label_upper_bound=window.end)` 仅对新预设传值，在
`build_tensor` 返回后断言面板时间标签 ⊂ `(window.start, window.end]`，越界即 `BindingValidationError`（invalid_binding）。
默认预设传 None，不断言：cutoff 非整点时现有最末标签可 > cutoff，收紧会破坏零变化，后移另评。
并发、GPU 槽、夜槽、Kronos 卸载逻辑不变。

**第二写入方**（owner 裁决 M8：由函数注入）：`write_generation_manifest(outcome, *, run_dir, binding, resolved, seed,
config, ...)` 以 `resolved: ResolvedWindow` 取代 `window`。函数内：`config = {**config, "window": window_config(resolved)}`
（调用方传入的 `window` 键被覆盖，与 `compose_config` 同口径）→ 以 `run_store.config_digest(config)` 求摘要并在内存构造 run
（`window=resolved.window`、`window_preset=preset_info(resolved)`）→ `verify_run_window(run, config)`（非显式绑定即拒）→
通过后 `write_config`（返回摘要须等于内存摘要）→ `finalize_run`。

- **摘要算法单一来源**：`write_config` 先剔除 `_R` 键（`run_store.py:39-41` 定义、`:81-83` 剔除）再做 canonical 序列化与
  `sha256_prefixed`，与直接对整个 config 求摘要不等价。故 run_store 新增只计算、不写盘的
  `config_digest(config) -> str`（剔除 `_R` → `canonical_json_bytes` → `sha256_prefixed_bytes`），`write_config` 改为内部调用它；
  第二写入方的内存侧摘要只用它，不自行拼算法。
- **不写盘的保证范围**：只覆盖自检之前的步骤，即 window 注入、摘要、内存构造 run 与 `verify_run_window` 任一失败时抛
  `SchemaValidationError`，config.json/run.json 都不写。自检通过之后：`write_config` 失败（如已有内容不同的 config.json →
  `RunStoreError`）时不发布 run.json；`finalize_run`（`run_store.py:118-140`）失败时 config.json 已落盘，run.json 未发布
  （`_atomic_write` 原子发布，不留半文件）；若失败发生在其追加 `generation.run_completed` 事件之后，events 可残留该事件。
  两种情形都不产生 completed run，下游只认 run.json 且经 `load_verified_run`；run 目录不自动清理，与 CLI 路径现状一致。
- 调用方测试的许可修订见 spec NFR-001。

## 6. UI 与可观测性

不适用图形 UI。`_print_summary` 不另起一行，只在现有单行 JSON 对象内新增 `window` 字段：`{preset, selection_hours,
label_horizon_bars, selection_start, selection_end, panel_first_label, panel_last_label, span_days, short_of_2y}`；
实际跨度 < 730 天时 `short_of_2y=true`。manual 仍不打印（`print_summary` 现状）。执行机证据记录同一信息。

## 7. 失败、恢复、安全与兼容

| 位置 / 错误 | 行为 |
|---|---|
| 参数组合非法 | 退出 2，无运行目录 |
| snapshot 绑定（任一预设，CLI） | `validate_binding` 抛 `SnapshotResolverUnavailableError` → rejected（invalid_binding），走不到预设解析 |
| 新预设 cutoff 非整点 / config.resample ≠ 1h | `mine` rejected（invalid_config）；`seed` failed；均不建面板 |
| 面板标签越界（仅新预设） | rejected（invalid_binding），不训练 |
| 发布前自检不等 | failed，不发布 completed |
| 下游篡改 run/config | `load_verified_run` 拒绝并指明字段 |
| 读取 v1/v2 | 成功，`window_preset=null`，不推断参数 |

兼容：默认预设 config 字节、config_digest、候选可复现断言（`generators/reproducibility.py`）不变；
run.json 新写入均为 v3（默认预设下 `window_preset` 五键齐全、name 之外四项 null）。
既有测试修订范围以 spec NFR-001 列表为限。已知限制：`as_of` 仍为 cutoff，双时间轴成员
（现为 `derivatives_funding_rates`）可含 `available_at ∈ [end, cutoff]` 的 end 前事件，执行机计数披露；
改为 `as_of=end` 可能使历史回填不可见而改变生成输入，须另评审。

## 8. 测试策略与验收映射

| 验收 | 层级 / 计划文件（tests 下） | 关键证据 |
|---|---|---|
| AC-001 | unit/test_f014_window_preset.py；unit/test_f014_cli_window.py；unit/test_f014_run_window_record.py | 公式与 `E−S=L`、参数负例退出 2 且无目录、新预设非整点 cutoff 与 resample 30min/4h 负例（mine/seed 各自终态、无 completed）、snapshot 绑定 invalid_binding、默认预设 `window_preset` 五键形态、逐字段篡改（run.window、run.window_preset、config.window、config_digest、binding 非显式）拒绝、第二写入方注入 window 与非显式绑定不写盘、config 含 `_R` 键（如 `hostname`）时 `config_digest` 与 `write_config` 返回值相等 |
| AC-002 | integration/test_f014_tail_read_bound.py | 打桩 `reader.read` 记录 `end` 参数与返回行最大开盘时间；面板最大标签 ≤ end；尾窗写极值不改变面板/候选；负对照（强制 end=cutoff）使断言失败；默认预设非整点 cutoff 不触发断言 |
| AC-003 | unit/test_f014_run_window_record.py；unit/test_f014_cli_window.py | 默认预设 config 金样字节/摘要；`tests/fixtures/f014/` 的 v1 manual、v2 alphagen 金样可读且 legacy 校验通过；smoke 默认窗口；NFR-001 许可修订之外的既有断言不变 |
| AC-004 | integration/test_f014_executor_run.py（`ALPHAMILL_INTEGRATION=1`，`ALPHAMILL_F014_RUN_DIR` 指向 run） | completed、入册 3–5、`load_verified_run` 通过、源日历 continuous_24_7/UTC、binding mode explicit_tuples、三处 resample = 1h、`freeze_members` 事件时间逐字段相等、双时间轴修订计数 |
| AC-005 | 同 AC-001/004 | 不截断 start、面板首根标签 = 湖首根 1m 开盘所在小时 + 1h（右标签）、摘要实际跨度 |

**执行机取证（T011）**：先 `hostname` 确认为 `qiaozhi-lt`；以合入提交运行
`alphamill-generate mine --generator alphagen --binding reports/f003/t035/bindings/sha256:3529a2a5….json
--seed 7 --window selection_tail_1h_2y_v1 --selection-hours 4320 --label-horizon-bars 1 --quota 5`
（L/H 为 spec Q-001 结论；夜槽内或显式 `--allow-offhours`）。复用该绑定前先用 `freeze_members(lake_root,
{dataset: data_version}, cutoff=2026-09-10T00:00Z, require_bitemporal=False)` 重算，与绑定声明
`event_time_min/max` 规范化后逐字段比对；不等则停止并另备绑定，不改比较口径。证据写
`reports/f014/执行机取证-T011.md`：hostname、commit/code digest、run_id、状态/计数、preset/L/H/`[S,E)`、
源日历 kind/timezone、binding mode、三处 resample、面板实际跨度、事件时间比对表、修订计数、`load_verified_run` 结果、测试退出码。该 run 目录在
`reports/generation/`（已 ignore），交 F013 T002。

## 9. 已确认决策与残余风险

| 事项 | 设计决定与边界 |
|---|---|
| 预设逻辑放 base、持久化放 window_record | 纯派生与持久化分层，下游只有一个比对入口 |
| 默认预设零字节 | 新键只在新预设出现，避免既有 config_digest 与证据失效 |
| 升 run v3 | 严格键集下唯一兼容路径，沿 v1→v2 模式 |
| 不截断 start | 保持 2y 语义；实际跨度可观测 |
| as_of 不变 | 只计数披露；另评审 |
| 执行机复用 t035 绑定 | cutoff 与成员与现有真实输入一致；先按 F007 口径复核事件时间 |
| 新预设要求 cutoff 整点、resample=1h | 解析期拒绝，避免建完面板才失败或 H 根 bar ≠ H 小时 |
| 标签断言只对新预设 | 默认预设非整点 cutoff 的越界属 F012 既有行为，守零变化，后移另评 |
| 单元测试用入库金样 | 真实 run 目录被 ignore，开发机/CI 不可见 |

## 10. 待确认设计问题

无
