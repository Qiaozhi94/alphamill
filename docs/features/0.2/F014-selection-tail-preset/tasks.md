---
kind: feature
id: F014
version: "0.2"
related_features: [F002, F003, F007, F012, F013]
topics: [factor-factory, generation, implementation-plan]
doc_kind: tasks
created: 2026-09-29
updated: 2026-09-29
---

# F014：F012 选择尾窗 preset 增量 — 实施任务

> Owner: Georg | [Spec](spec.md) | [Design](design.md)

## 0. 来源与执行规则

本次仅立项与需求设计，以下全部是后续实施清单，不代表已经开工或验证通过。
必须先文档检视收敛、readiness=PASS，再经 G1 计划批准后进入需求分支实施。
需求/验收以 spec 为准，接口以 design 为准；每项完成后凭新鲜证据勾选。
先 [TEST] 红灯，再实现；本文件不授权自动派生代理。

## 1. 前置条件

- [ ] T001 (`FR-001`, `FR-005`, `FR-006`, `AC-001`, `AC-002`, `AC-004`): 完成三件套文档检视并关闭契约问题，取得 readiness=PASS 与 G1 批准（spec Q-001 已由 owner 2026-09-29 关闭为 H=1、L=4320，此项已满足） — verify: 文档检视记录、`sdd_status.py --dry-run`。

## 2. 实现任务

### Phase 1：预设派生与持久化

- [ ] T002 (`FR-001`, `AC-001`, `AC-005`): 在 `generators/base.py` 实现预设注册表、`WindowPresetParams`、`resolve_window`，`Window.from_preset` 增加可选 `params` 并保持默认预设结果不变（改动点 `base.py:57-63`）；新预设在解析时要求 cutoff 为 UTC 整点 — verify: `tests/unit/test_f014_window_preset.py`。
- [ ] T003 (`FR-002`, `FR-003`, `AC-001`, `AC-003`): CLI `--window` choices 改取注册表（`cli.py:62-64`），新增 `--selection-hours`/`--label-horizon-bars` 与组合校验（退出 2、无运行目录）；`cli.py:111-117` 改用 `window_record.window_config`，默认预设保持四键；新预设要求合成 config 顶层 `resample`（若有）为 `"1h"`；CLI 下 snapshot 绑定沿 `validate_binding` 走 invalid_binding — verify: `tests/unit/test_f014_cli_window.py`。
- [ ] T004 (`FR-004`, `AC-001`, `AC-003`): run.json v3 `window_preset`（`run_schema.py` 版本集、`_V3_FIELDS`、v2 补 null、`_validate_terminal` 重算）；默认预设 `window_preset` 五键齐全、四项 null，非 completed 已解析则填；`manifest_builder` 与 `alphagen_generation.write_generation_manifest`（design §5「第二写入方」：以 `resolved` 取代 `window`，函数自身注入 `config["window"]`，内存摘要用 run_store 新增的只计算函数 `config_digest`（`write_config` 共用），写盘前 `verify_run_window` 自检，自检及之前失败（含非显式绑定）不写盘；`finalize_run` 失败按 design §5 如实处理）两个写入方同步；按 spec NFR-001 许可项修订 `tests/unit/test_f012_cli_contract.py:60,67`、`tests/unit/test_f012_run_schema.py:84-85,99`、completed 夹具补键与 `tests/integration/test_f003_generation_run.py:193-200`（显式绑定 + 按预设派生窗口；`:207-214` 断言不放宽），不放宽其他断言 — verify: `tests/unit/test_f014_run_window_record.py`、`tests/unit/test_f003_run_store.py`、`tests/unit/test_f012_cli_contract.py`、`tests/unit/test_f012_run_schema.py`、`tests/integration/test_f003_generation_run.py`。
- [ ] T005 (`FR-005`, `AC-001`): 新增 `registry/window_record.py`（`window_config`/`preset_info`/`verify_run_window`/`load_verified_run`；cutoff 取 `run.binding.cutoff_time`，非显式绑定拒绝）；CLI 发布前以 `verify_run_window` 自检；`show --run` 对 completed 走 `load_verified_run`；`_generate` 对新预设拒绝非显式绑定（纵深防护） — verify: `tests/unit/test_f014_run_window_record.py`。

### Phase 2：读取上界与 smoke 适配

- [ ] T006 (`FR-006`, `AC-002`, `AC-005`): `mine_dispatch.prepare_panel` 新增 `label_upper_bound`，仅新预设传 window.end，在 `build_tensor` 后断言面板标签 ⊂ `(start, end]`，越界 invalid_binding，默认预设不断言；`_print_summary` 在现有单行 JSON 内加 `window` 字段（preset/L/H/`[S,E)`/实际跨度，不另起一行）；确认 `lake_tensor.py:115-124` 之外无生成期湖读取 — verify: `tests/integration/test_f014_tail_read_bound.py`。
- [ ] T007 (`FR-007`, `AC-003`): `smoke_gate.py:169-174` 适配新签名，`default_smoke_config`/`default_smoke_window` 仍固定默认预设 — verify: `tests/integration/test_f003_smoke_gate.py` 与 `tests/unit/test_f014_cli_window.py`。

## 3. 验证与验收任务

### [TEST] 组：先立红灯

- [ ] T008 [TEST] (`AC-001`, `AC-003`, `AC-005`): 先入库 `tests/fixtures/f014/` 金样（design §3：v1 manual、v2 alphagen 的 run.json + config.json 原字节，默认预设 config 金样取自 main@cca44e0），再写预设公式、参数负例、非整点 cutoff 与 resample 30min/4h 负例、snapshot 绑定路径、默认预设五键形态、逐字段篡改（含非显式 binding）、金样读取与 legacy 校验、不截断 start 的单元测试 — verify: `tests/unit/test_f014_window_preset.py`、`tests/unit/test_f014_cli_window.py`、`tests/unit/test_f014_run_window_record.py` 的 RED/GREEN 记录。
- [ ] T009 [TEST] (`AC-002`): 写 reader 打桩 + 尾窗极值 + 负对照（强制 end=cutoff 必须被检出）+ 默认预设非整点 cutoff 不触发断言的读取上界集成测试 — verify: `tests/integration/test_f014_tail_read_bound.py` 的 RED/GREEN 记录。

### 回归与执行机验收

- [ ] T010 (`NFR-001`, `NFR-003`, `AC-003`): 跑 F012/F003 全量回归与统一门禁，确认默认预设零变化 — verify: `python3 tools/verify.py`。
- [ ] T011 (`NFR-002`, `AC-004`, `AC-005`): 在执行机 `qiaozhi-lt`（先 `hostname` 核对）按 design §8 以 Q-001 的 L=4320、H=1 生成 3–5 候选 completed run；核验 `load_verified_run` 通过、源日历 continuous_24_7/UTC、binding mode explicit_tuples、三处 resample = 1h；用 F007 `freeze_members` 重算成员事件时间并与绑定逐字段比对，计数双时间轴修订；写 `reports/f014/执行机取证-T011.md` — verify: `ALPHAMILL_INTEGRATION=1 ALPHAMILL_F014_RUN_DIR=<run_dir> python3 -m pytest tests/integration/test_f014_executor_run.py -q`。

### 文档与收口

- [ ] T012 (`FR-005`, `NFR-002`, `AC-004`): 回写 AC 实际测试/证据路径；把 run_id、L/H、`[S,E)` 与 `load_verified_run` 入口交 F013 T002；从 `BACKLOG.md`「规划中」移除增量行，并把 F013 spec §7 依赖与 tasks T002 的载体从该行改指本 spec（F013 design §4.1 与 T003 的 `load_verified_run` 指针已在 F014 文档检视第 1 轮修订时同步） — verify: `python3 tools/verify.py`。
- [ ] T013 (`NFR-001`, `AC-004`): 完成代码检视、质量门与收口记录后按 sdd-flow 流转，推送后核对当前提交 CI — verify: `python3 tools/verify.py`、检视收敛记录、CI 记录与状态脚本。

## 4. 依赖与并行关系

- `T001 -> T002`：文档收敛与 Q-001 关闭后才开工。
- `T002 -> T003 -> T004 -> T005`：派生函数先于 CLI/config，run schema 先于互验入口。
- `T005 -> T006 -> T007`：互验入口稳定后加读取断言与摘要，最后适配 smoke。
- `T005 -> T008`、`T006 -> T009`：[TEST] 红灯在 T001 后即可编写，此处边表示 GREEN 验收执行。
- `T002 -> T008`、`T003 -> T008`、`T007 -> T008`：T008 复用 T002（`test_f014_window_preset.py`）、T003 / T007（`test_f014_cli_window.py`）声明的测试文件，GREEN 验收须在这些生产者之后。
- `T007 -> T010`、`T008 -> T010`、`T009 -> T010`：全绿后跑统一回归。
- `T010 -> T011 -> T012 -> T013`：执行机取证依赖合入候选代码；交接与收口最后进行。
- 此列表无 [P] 任务：CLI、schema 与互验入口共享同一持久化口径，顺序执行。

## 5. 明确后移

- 评测快照 cutoff 晚于生成绑定（方案 b）→ M2 之后另立增量 / 0.2 之后：本 Feature 不改绑定 cutoff。
- 生成期 `as_of` 改为 window.end → 另立评审（F002/F012 后续）/ 0.2：本 Feature 只计数披露。
- 默认预设在非整点 cutoff 下最末标签 > cutoff 的收紧 → F012 后续评审 / 0.2 之后：本 Feature 守默认预设零变化。
- 多 horizon、非 1h 频率与交易日历窗口 → F013 后续增量 / 0.2 之后：当前入口显式拒绝。
- F013 的折、标签、快照与批量评测 → F013 / 0.2：本 Feature 只交付合规生成 run。
