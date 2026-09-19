---
kind: feature
id: F003
version: "0.2"
related_features: [F001, F002, F007, F008]
topics: [factor-factory, alphagen, vendor, generators, m2]
doc_kind: tasks
created: 2026-09-14
updated: 2026-09-14
---

# F003：AlphaGen vendor 与可插拔生成器平面 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
- `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
- 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
- **机器边界**（架构 §7.1、`docs/SOP.md` §3）：编码、单元测试与门禁在开发机 `qiaozhi-gp`；挖掘训练与全部 GPU/产能证据在执行机 `qiaozhi-lt` 取（成熟后整体迁移至 `qiaozhi-lab`），验收证据必须记录 hostname 与设备。开发机上 GPU 用例跳过是预期行为，不算证据也不算失败。
- **迁移友好**：显存上限、时段、耗时阈值一律走配置并写入运行记录，不得写死常数——执行机迁移时只改配置与重跑验收，不改代码。
- Phase 2 是 ADR-0001 的 **2 个工作日 time-box**：到期按判据出二元裁决，不允许"再给一天"。
- vendor 目录内的改动一律最小 diff 并标注 `# [alphamill] <原因>`；胶水代码不得写进 vendor 目录。

## 1. 前置条件

- [x] T001 (`FR-003`, `AC-003`): 冻结并校验 F008 宇宙台账 artifact 的消费契约（按 digest 加载、`universe_at(T)` 与 `schema_version` 可读），产出 T020 的输入夹具；F008 未落地时以显式 universe 配置作为等价夹具 — verify: `tests/unit/test_f003_binding.py`
- [x] T002 (`FR-003`, `DR-001`): 固定绑定文件格式并验证目标 dataset 的 valid 版本与 `value_digest` 可由 F002 reader 解析 — verify: `tests/unit/test_f003_binding.py`
- [x] T003 (`FR-002`): clone 上游 AlphaGen、记录 commit hash、核对核心子集的实际文件布局，产出 vendor 清单初稿，并**冻结可复现的上游基线**（逐文件 sha256 清单写入 `alphagen_vendor/_upstream_baseline.json`） — verify: `src/alphamill/factor_factory/generators/alphagen_vendor/VENDORED.md`
- [x] T004 (`NFR-002`, `NFR-005`): 打通并标定执行机 `qiaozhi-lt`——**先恢复 shell 接入**（env-manager 台账记录 2026-09-14 全端口复测 22/2222/2200/8022/3389/5985 全闭，当前无 shell 路径，按 `references/access-methods.md` §4 启用 Windows OpenSSH）；再在其 WSL2 内实测 CUDA 可用性与可用显存，按 §7.1 标定显存上限写进配置（不写死代码）；确认该机 F002 湖可读且通过完整性校验 — verify: `tests/unit/test_f003_gpu_slot.py`（能力探测纯函数）+ 在 `qiaozhi-lt` 上用 `alphamill.data_bridge.reader` 读一次真实快照

## 2. 实现任务

### Phase 1：生成器平面骨架与人工种子后端（US-001，不依赖 AlphaGen）

- [x] T005 (`FR-001`, `IR-002`, `AC-001`): 实现 `Generator` 协议与 `GenerationRequest/Result/Counts`，含结论字段白名单拒绝 — verify: `tests/unit/test_f003_generator_contract.py`
- [x] T006 [P] (`DR-003`, `AC-009`): 实现 `HypothesisDef` schema 与 catalog（含 `mechanism`、`applicable_state` 默认值），内置 `mechanism_unknown` 条目 — verify: `tests/unit/test_f003_hypotheses.py`
- [x] T007 (`DR-002`, `AC-009`): 实现 FactorDef 规范化 JSON（带 `schema_version`）、`definition_digest`、`factor_id` 生成与 `factor_store` 读写（`load()` 由表达式 + `feature_map` 重建可执行 `compute`） — verify: `tests/unit/test_f003_factor_store.py`
- [x] T008 (`DR-001`, `TR-001`, `TR-002`, `AC-009`, `AC-012`): 实现 `run_store`——GenerationRun manifest（带 `schema_version`）原子写（终态 `run.json` 最后写，含 `hostname` / `device` / `vram_limit_gb` / `universe`）与 `events.jsonl` append-only — verify: `tests/unit/test_f003_run_store.py`
- [x] T009 (`FR-003`, `AC-003`): 实现 `binding.py`：两种绑定形态解析、逐 dataset `value_digest` 校验、invalid 立即拒绝 — verify: `tests/unit/test_f003_binding.py`
- [x] T010 (`US-001`, `FR-001`, `AC-001`): 实现人工 crypto 原生种子后端（funding carry、basis、OI 变化、截面动量、波动），每个种子绑定真实 `HypothesisDef` — verify: `tests/unit/test_f003_manual_seeds.py`
- [x] T011 (`NFR-004`, `AC-011`): 实现 `egress_guard` 与写路径白名单（只允许 `reports/generation/<run_id>/`），两者 fail-closed（安装/生效失败即拒绝启动，不降级为仅警告） — verify: `tests/integration/test_f003_boundaries.py`
- [x] T012 (`IR-001`, `AC-011`, `AC-012`): 实现 CLI `seed` / `show` 子命令与缺绑定的非零拒绝、未知 `schema_version` 的拒绝 — verify: `tests/unit/test_f003_cli_contract.py`

### Phase 2：AlphaGen vendor 与冒烟闸门（US-002，2 个工作日 time-box）

- [x] T013 (`FR-002`, `AC-002`): vendor 核心子集落地（表达式/算子、张量求值器、线性协同池、RL 环境），丢弃 `requirements.txt` 与 `alphagen_qlib/`，逐处改动标注并补齐 `VENDORED.md` 五项，且与 T003 冻结的上游基线逐文件比对（差异集合 == 标注集合） — verify: `tests/unit/test_f003_vendor_hygiene.py`
- [x] T014 (`FR-002`): `pyproject.toml` 新增 `mining` 可选依赖组（torch / numpy / stable-baselines3 / gymnasium 全部写版本范围；torch 需显式选 CUDA 构建，且必须覆盖 `qiaozhi-lab` 的 Blackwell sm_120，为迁移留路）、`ruff extend-exclude` 排除 vendor 目录，并在 `docs/SOP.md` Code Quality 豁免表登记 vendor 目录 — verify: `python3 tools/verify.py`
- [x] T015 (`FR-002`, `NFR-004`): 扩展 `tools/check_dep_pins.py` 为"可选 extras 已安装才校验范围"，并在 runner 入口加 mining extra 能力自检 fail-closed（两者必须同时落地） — verify: `tests/unit/test_check_dep_pins.py`
- [x] T016 (`FR-006`, `AC-007`): 实现冒烟闸门判据判定器、当日冒烟 manifest（含 ADR-0001 两条 M2 义务：生成侧逐级计数、下游级 `owner=F007`+`not_yet_available` 占位、奖励频率抽查）、档位状态机与降级裁决（L1→L0 回切须新 time-box 记录），并提供 `smoke` 的默认 config/window 构造 — verify: `tests/integration/test_f003_smoke_gate.py`
- [x] T017 (`FR-006`, `AC-007`): 在执行机用最小数据切片跑通 1 个 PPO epoch（含 gym→gymnasium env wrapper 适配）——冒烟第 1 天判据 — verify: `tests/integration/test_f003_smoke_gate.py`
      — 复勾（2026-09-19）：首版取证为空转（`eval_cnt=0`），已按 review-convergence §7.5 回退；根因修复后重取证为真。修复包括张量布局 `(days, features, stocks)` + feature 轴按 `FeatureType` 索引、`n_days` 应为求值窗口（`LakeStockData` 与 `_VendorStockData` 两处都要减余量）、`Ref` 为滞后故 `max_future_days` 取 target horizon、MaskablePPO + sb3-contrib。现已加**反空转断言** `evaluations >= 1`；`ALPHAMILL_INTEGRATION=1` 下 13 passed（512 步，device=cuda，eval_cnt ≥ 1）。
- [x] T018 (`FR-006`, `AC-007`): 实现 IC 口径对齐回归（vendor 张量 IC vs pandas 参考实现，容差内一致）——冒烟第 2 天判据；只做数值回归，不产 verdict — verify: `tests/unit/test_f003_ic_parity.py`
- [ ] T019 (`FR-006`): 在执行机实跑 time-box（第 1、2 天判据），产出裁决记录（L0 锁定或 L1 降级；L2 不属 time-box 裁决）与触发判据写入当日 manifest；**不在此步回写 spec**（回写在 T032，须先归档证据） — verify: `tests/integration/test_f003_smoke_gate.py` + 当日 manifest 含裁决与触发判据

### Phase 3：完整数据面、适配器与生成侧自检

- [x] T020 (`FR-003`, `AC-003`): 实现 `lake_tensor` 完整路径——多 dataset 合并、重采样（默认 1h）、PIT 宇宙掩码（消费 F008 `universe_at(T)` 与台账 digest；F008 未落地时用显式 universe 配置并把 digest 与来源写进 `run.json`）、`feature_map` 与其 digest — verify: `tests/integration/test_f003_lake_tensor.py`
- [x] T021 (`FR-004`, `AC-004`): 实现 `alphagen_adapter`——token 序列编译闭包、`meta["expression"]` 反解、`data_columns` 经 `feature_map` 反解、截面边界（no-signal 语义） — verify: `tests/unit/test_f003_alphagen_adapter.py`
- [x] T022 (`FR-005`, `AC-005`): 实现算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 窗口换算），并导出为 `F007` 可消费的版本化能力清单（含 `schema_version`；`F007` FR-002 的已登记算子能力消费源） — verify: `tests/unit/test_f003_operator_registry.py`
- [x] T023 (`FR-005`, `TR-002`, `AC-005`): 实现生成侧 AST 自检与四类拒绝原因码（`unregistered_op` / `lookahead` / `reachability` / `duplicate_definition`）计数 — verify: `tests/unit/test_f003_operator_registry.py`
- [x] T024 (`FR-005`, `AC-006`): 实现目标对齐——换手惩罚、≥30 笔/90 天可达性预筛与成本后收益预筛（按可配成本参数，只产预筛信号不产裁决），参数写入 `run.json` 的 `objective` — verify: `tests/unit/test_f003_objective.py`

### Phase 4：批量挖掘、协同池与产能

- [x] T025 (`NFR-002`, `AC-010`): 实现 `gpu_slot`——显存自检（上限可配，不写死常数）、flock 单槽 FIFO（`queue_seq` / 取锁 / 释放 / 超时状态记录）、训练窗口校验、`--allow-cpu` / `--allow-offhours` 显式开关，运行记录写 `hostname` / `device` / `kronos_offload`；实现夜槽 Kronos 生命周期客户端（**live owner = F003**）：按架构 §7.1 契约调用 `status` / `stop` / `restore`（含 `contract_version`、幂等、超时与错误码），用 `status.vram_bytes` 确认显存释放，失败或版本不匹配则 fail-closed 留在 FIFO，并按架构 §7.1 观测→处置决策表逐行断言（连接拒绝且部署清单无该服务 / `device=cpu` → `offload_not_needed`；404/`E_UNSUPPORTED_VERSION` 回落探测：`/health.device=cpu` 或设备侧 `memory.used` 低于阈值 → `offload_not_needed`；达到阈值或读数不可得 → fail-closed（不依赖 GPU 进程列表），`reason=endpoint_absent_no_gpu_tenant`，读数写入 `kronos_offload`；单测须含「进程列表为空但 `memory.used` 达到阈值 → fail-closed」用例；停止失败 / 控制面不可达但服务在 → fail-closed） — verify: `tests/unit/test_f003_gpu_slot.py`, `tests/integration/test_f003_kronos_lifecycle.py`
- [x] T026 (`FR-007`, `DR-004`, `AC-008`): 实现协同池导出为可执行 FactorDef（`generator=pool`，加载后可按成员重算）与 `pool_store`，成员权重可反解且重算一致，成员或权重变化产生新 `factor_id` — verify: `tests/integration/test_f003_alpha_pool.py`
- [x] T027 (`IR-001`, `FR-001`, `AC-011`): 实现 CLI `mine` 子命令与全部启动期拒绝条件（缺绑定/invalid/档位不明/窗口外/无 CUDA），并支持 `--window` / `--config` 默认值以构造完整 `GenerationRequest`（默认值来自代码内常量并写入 config artifact） — verify: `tests/unit/test_f003_cli_contract.py`
- [x] T028 (`NFR-003`, `AC-009`): 实现并验证可复现性——canonical config artifact 与 `config_digest` 落盘、seed 稳定派生、torch 确定性开关；同 `(seed, binding, code_digest, config_digest)` 重跑得到相同 factor_id 集合与相同池成员 — verify: `tests/integration/test_f003_generation_run.py`
- [x] T029 (`NFR-001`, `AC-006`): 在执行机跑一次完整挖掘运行，入册 ≥50 个通过自检候选并记录逐级计数、hostname 与设备 — verify: `tests/integration/test_f003_generation_run.py`
      — 取证（2026-09-19，qiaozhi-lt / RTX 4060 / CUDA 2.10.0+cu128）：`ALPHAMILL_INTEGRATION=1` 下 13 passed（170s）；`run_generation` 8192→4096 步即可满足 ≥50（实测 4096 步自检通过 119，原因码分布 lookahead 95 / unregistered_op 7 / duplicate_definition 54），断言含 `registered >= 50`、`evaluations >= registered`、`sum(rejected)+registered == proposed`、`device == "cuda"`。参数写在测试内，画面可复跑。

## 3. 验证与验收任务

- [x] T030 (`AC-001`, `AC-002`, `AC-004`, `AC-005`, `AC-012`): 运行生成器契约、vendor 卫生、适配器、算子登记、人工种子与 CLI 契约单元套件 — verify: `pytest -q tests/unit/test_f003_generator_contract.py tests/unit/test_f003_vendor_hygiene.py tests/unit/test_f003_alphagen_adapter.py tests/unit/test_f003_operator_registry.py tests/unit/test_f003_manual_seeds.py tests/unit/test_f003_cli_contract.py`
- [x] T031 (`AC-003`, `AC-008`, `AC-009`, `AC-011`): 运行数据面、协同池、运行记录、边界与 CLI 契约集成套件 — verify: `pytest -q tests/integration/test_f003_lake_tensor.py tests/integration/test_f003_alpha_pool.py tests/integration/test_f003_generation_run.py tests/integration/test_f003_boundaries.py tests/unit/test_f003_cli_contract.py`
- [ ] T032 (`AC-007`): 归档冒烟闸门 time-box 的真实执行证据（逐条判据 pass/fail、时间戳、两条 M2 义务记录），并**在证据归档之后**把裁决结论与触发判据回写 `spec.md` §7 决策表 — verify: `pytest -q tests/integration/test_f003_smoke_gate.py` + `spec.md` §7 含裁决记录
- [ ] T033 (`AC-006`, `AC-010`): 在执行机的真实训练夜槽复跑产能与显存断言，证据记录 hostname、GPU 型号、显存峰值与耗时；开发机的同名用例跳过属预期，不得以其 CPU 结果替代。其中 `test_f003_kronos_lifecycle.py` 必须以 **0 xfailed** 通过（前置：BACKLOG「Kronos 服务生命周期端点」feature 已落地并部署于执行机，`KRONOS_CONTROL_URL` 指向 `kronos-signal-real`；端点未落地时本任务不可勾，真实卸载取证随该载体后移） — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q --runxfail tests/integration/test_f003_generation_run.py tests/integration/test_f003_kronos_lifecycle.py tests/unit/test_f003_gpu_slot.py`（`--runxfail` 使 xfail 先红态按真失败计：端点缺失即非零退出，0 xfailed 成为机器门禁而非程序性要求）
- [x] T034 (`AC-001`, `AC-011`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
- [ ] T035 (`AC-006`, `DR-001`): `F008` 宇宙扩容落地后，用扩容宇宙（≥30 对）复跑一次挖掘运行作对照，记录两次运行的 `universe` 与候选质量差异；在此之前的质量结论一律标注「6 对宇宙」前提 — verify: `pytest -q tests/integration/test_f003_generation_run.py` + 两次 `run.json` 的 `universe` 对照

### [TEST] 组：层 2 旅程验收轨（必填）

- [x] T036 [TEST] (`US-001`, `AC-001`, `AC-003`, `AC-004`): 旅程 US-001 端到端验收——固定快照绑定与 seed 经 `produce()` 连跑两次得到同一 `factor_id` 集合、落盘后加载的 FactorDef 可直接执行、invalid 绑定被拒并留 `rejected` 终态；夹具在 Phase 1 先以红灯立起，收尾全量执行 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/unit/test_f003_generator_contract.py tests/unit/test_f003_factor_store.py tests/unit/test_f003_alphagen_adapter.py tests/integration/test_f003_lake_tensor.py`
- [ ] T037 [TEST] (`US-002`, `AC-007`): 旅程 US-002 端到端验收——在执行机按 `smoke --day 1`、`--day 2` 走完 time-box：逐条 L1 判据 pass/fail、两条 M2 义务入 manifest、判据未达标即输出 L1 降级、回切请求被拒；收尾全量执行 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f003_smoke_gate.py` + 当日 manifest
- [x] T038 [TEST] (`US-003`, `AC-006`, `AC-008`, `AC-009`): 旅程 US-003 端到端验收——执行机训练夜槽一次完整挖掘：入册 ≥50、逐级计数入 run.json、成本后收益与可达性预筛参数入 objective、协同池可导出且按成员重算一致、零交易型表达式被排除、同配置重跑得到相同 factor_id 集合与池成员 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f003_generation_run.py tests/integration/test_f003_alpha_pool.py tests/unit/test_f003_objective.py`

- [ ] T039: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T004 -> T017`：执行机环境与湖可读性没钉死前不得开跑 time-box 的判据实跑（否则闸门结论的环境前提不明）；T016 判定器实现不依赖执行机。
- `T003 -> T013`：先核对上游实际布局，再落 vendor 子集。
- `T005 -> T010`、`T005 -> T013`：接口先定，两个后端都按同一协议实现。
- `T007 -> T008 -> T029`：候选持久化 → 运行记录 → 产能计数。
- `T009 -> T020`：绑定校验是数据面的启动前置。
- `T001 -> T020`：F008 宇宙台账消费契约（或等价显式 universe 夹具）是 PIT 掩码的输入前置。
- `T002 -> T009`：绑定文件格式与 digest 解析先于 `binding.py` 实现。
- `F008.IR-002 -> T020`：PIT 掩码依赖 F008 的内容寻址宇宙台账（`universe_at(T)` 与 digest、IR-003 的 `schema_version`）；F008 未落地前 T020 用显式 universe 配置并在 `run.json` 记录 digest 与来源，任何情况下都不得用当前成员表回填历史。
- `T013 -> T016 -> T017 -> T018 -> T019 -> T032`：判定器（T016）先于判据实跑（T017/T018），判据先于 time-box 实跑与裁决记录（T019）；证据归档与裁决回写（T032）以裁决为前提，禁止先回写后归档。
- `T007/T024/T030/T031/T032/T033/T034/T035 -> T036/T037/T038`：[TEST] 组三条旅程验收以各验收套件与真实执行证据为前提（编写早、执行晚），并需 `ALPHAMILL_INTEGRATION=1` 在执行机取证；`T007/T024` 是 T036/T038 verify 文件（factor_store/objective）的直接生产者，一并作为前置。
- `T036/T037/T038 -> T039`：三条旅程验收全绿后才回写 spec 验收证据与状态。
- `T014 -> T015`：先声明 `mining` extra，再扩展 pin 门禁。
- `T022 -> T023 -> T024`：算子能力登记表先于生成侧自检，自检先于目标对齐。
- `T020 -> T021 -> T024 -> T029`：数据面 → 适配 → 目标对齐 → 批量产出。
- `T025 -> T027 -> T029`：调度就位后才允许完整挖掘运行。
- `T026 -> T031`：协同池导出由集成套件验收。
- `T028 -> T029`：可复现性由完整运行验收。
- `T005/T010/T012/T013/T021/T022 -> T030`：生成器接口、人工种子、CLI 契约、vendor 卫生、适配器与算子登记各由 T030 单元套件验收（verify 文件的直接生产者须为其前置）。
- `T011/T020/T026/T027/T028 -> T031`：边界、数据面、协同池、CLI 契约与可复现性由 T031 集成套件验收（生产者 → 验证者）。
- `T015 -> T016`：pin 门禁与 mining extra 声明就绪后才判定器结构可用。
- `F004 交付（kronos-signal 服务编排；不含生命周期控制面端点）-> T025`：夜槽卸载客户端的编码与单测以服务编排形态就绪为前提；端点缺失按架构 §7.1 观测→处置决策表记 `offload_not_needed` 或 fail-closed 留在 FIFO。FIFO 协议用两个并发挖掘运行独立取证。
- `BACKLOG「Kronos 服务生命周期端点」feature 落地并部署于执行机 -> T033`：真实卸载取证以控制面端点可用为前提（T033 对 `test_f003_kronos_lifecycle.py` 要求 0 xfailed）；端点未落地时 T033 不可勾，取证随该载体后移，不以 xfail 先红态冒充夜槽证据。
- `T029 -> T035`：先有 6 对宇宙的基线运行，`F008` 落地后才有可对照的第二次运行；`F008` 不阻塞 T001–T039 的任何一项。
- `T025/T029 -> T033`：产能与显存复跑以 gpu_slot/Kronos 客户端实现与首次完整运行为前提（§3 验证任务不得先于实现执行）。
- `T029 -> T034`：统一质量门在完整挖掘运行之后运行。
- `T006 -> T010`：假设 catalog 供人工种子后端绑定真实 `HypothesisDef`。
- `T006 [P]`：只改假设模块，与接口/存储任务无共享状态（无前置边，仅可并行）。

## 5. 明确后移

- ResearchSnapshot 的实现与 `research_snapshot_id` 唯一绑定形态 → `F007`：身份归 `experiment_store/`，F003 过渡期用显式元组绑定（spec Q-002）。
- 因子注册表的评测摘要回写、`|ρ|>0.99` 查重与生命周期状态机 → `F007` / `F006`：依赖评测结论，生成器不持有。
- 漏斗逐级入库（纯度门之后各级）与多重检验 cohort 记账 → `F007`：F003 只产 `generation.*` 事件作为第一级数据源，并在当日冒烟 manifest 中以 `owner=F007` + `state=not_yet_available` 显式占位（ADR-0001 两条 M2 义务之一），不静默省略或记 0。
- 宇宙扩容 30~50 对与新 pair 质量流程（FR1.5）→ `F008`：**并行推进而非后移**（spec Q-001 已裁决），本 feature 只消费其产出的宇宙，不实现扩容本身。
- 批量移植 GTJA191 / WQ101 公式库作为种子宇宙 → 后续 Feature：需先做 crypto 24/7 窗口重定义与 A 股专有因子剔除。
- 模型族级联与 DML 诊断 → 独立研究 Feature（`F007` spec §3 已把它指向 F003 或独立立项；本 spec 不纳入范围）。
- 执行机从 `qiaozhi-lt` 整体迁移到 `qiaozhi-lab`（RTX 5070 Ti）→ 独立 Feature：不只是换卡，还包括 Win11+WSL2 → 原生 Ubuntu 的平台迁移（docker 编排、路径、自启、备份通道）与 Blackwell sm_120 的 torch 构建切换；F003 只面向当前执行机验收，迁移时重标显存上限与时段表，并按 `docs/SOP.md` §3 重跑依赖机器能力的验收项。
- `kronos-signal` 服务端 `status` / `stop` / `restore` 端点实现（版本化契约见架构 §7.1）→ 待分配 Feature（`BACKLOG.md`「规划中」登记）：契约已定义、F003 客户端与契约测试在本 feature（T025 / `tests/integration/test_f003_kronos_lifecycle.py`）；服务端未实现时 F003 记 `offload_not_needed`（服务确实不存在）或 fail-closed 留在队列，不降级为并行抢卡。Kronos 推理性能优化与 GPU 直通仍按 `F004` / v0.2.x 后续评估。
