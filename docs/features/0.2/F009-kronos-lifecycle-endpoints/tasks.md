---
kind: feature
id: F009
version: "0.2"
related_features: [F003, F004, F010]
topics: [kronos, lifecycle, control-plane, gpu-slot, m2]
doc_kind: tasks
created: 2026-09-20
updated: 2026-09-20
---

# F009：Kronos 服务生命周期控制面端点 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
- `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
- 全部新测试必须落在 `tests/unit` 或 `tests/integration`。
- **机器边界**（架构 §7.1、`docs/SOP.md` §3）：编码、单元测试与门禁在开发机；执行机证据记录 hostname 与设备。开发机上的跳过是预期行为，不算证据也不算失败。
- **契约不可改**：架构 §7.1 是契约正文所有者。实现期发现契约缺陷，先改该节再改实现，不得在本 feature 内单方面改语义。
- **变异判红纪律**：每条新断言须给出"改坏实现即判红"的证明，不接受只会绿的断言。
- **mock 依赖面红线**：F004 NFR-001 的否证测试「默认镜像 `import torch` 判红」全程保持绿；torch / GPU 相关导入一律惰性化，控制面路由只在 real 实例注册。
- **GPU 前置诚实纪律**：F010 落地前，凡依赖真实显存变化的结论一律标注未验证，不得以 CPU 实例上的通过充当证据（spec NFR-006）。
- **状态写入口唯一**：状态流转一律经 `scripts/sdd_status.py --dry-run/--advance`，不手改 frontmatter，不手工编辑 `BACKLOG.md` 的派生行。

## 1. 前置条件

- [x] T001 (`FR-001`): 确认 spec §8 与 design §10 无开放项，且三件套的接口表与架构 §7.1 逐格一致（动作 / 幂等 / 超时 / 错误码 / 字段集五列） — verify: `spec.md` §8、`design.md` §10、`docs/alphamill-architecture.md` §7.1 — 证据（2026-09-23）：动作/幂等/超时/错误码/字段集五列与架构 §7.1 逐格一致；spec §8、design §10 无开放项
- [x] T002 (`SC-005`, `NFR-006`): 核对 F010「Kronos GPU 推理基座」已是**活跃 Feature**（`docs/features/0.2/F010-kronos-gpu-runtime/`，非"规划中预留"），并确认两边的完成边界无环：本 feature 的 AC-012 止于载体与先红态，解除 xfail 与真实证据归 F010 AC-009/T011 — verify: `BACKLOG.md` 活跃行 + F010 `spec.md` §7 依赖段 + `docs/alphamill-architecture.md` §7.1 GPU 基座前置条 — 证据（2026-09-23）：F010 已是活跃 Feature（0.2/F010-kronos-gpu-runtime，status=developing）；完成边界无环：本 feature AC-012 止于载体+先红态，解除归 F010 AC-009/T011

## 2. 实现任务

### Phase 1：契约骨架、期望态与状态查询

- [x] T003 (`FR-005`, `IR-002`, `IR-004`, `AC-005`): 实现 `require_contract_version` 依赖、**恰为单键**的错误信封与请求体校验（空体/`{}` 放行，含额外键以 `E_BAD_REQUEST` 拒绝，**不复用** `E_UNSUPPORTED_VERSION`）；头缺失不按默认版本放行 — verify: `tests/unit/test_f009_lifecycle_errors.py` — 证据（2026-09-23）：red→green：`test_f009_lifecycle_errors.py` 19 passed；缺头与版本不匹配均恰为单键信封；额外参数 4 例均 E_BAD_REQUEST 且 unload_calls=0
- [x] T004 (`FR-001`, `IR-001`, `IR-003`, `AC-001`): 新建 `lifecycle.py` 与 `LifecycleController`：`desired` 存储 + `state` 由 `(desired, model_loaded)` 派生出 `running`/`stopped`/**`transitional`** 三值 + `operation` 台账；挂 `GET /lifecycle/status` 返回八字段，动作执行窗口内返回 `transitional` 且 `operation` 非空；status **不进单飞执行器**，自带 `time.monotonic()` deadline，动作进行中照样可达 — verify: `tests/unit/test_f009_lifecycle_contract.py` — 证据（2026-09-23）：`test_f009_lifecycle_contract.py` 13 passed；八字段齐备、动作窗口内 transitional + operation 非空；status 不进单飞执行器（并发动作中 <0.3s 返回）
- [x] T005 [P] (`FR-007`, `NFR-005`, `AC-007`): 新建 `vram.py`（`mem_get_info` → `nvidia-smi` → 不可得三级回退，不查进程列表；探测接受**剩余预算**参数并受 `KRONOS_VRAM_PROBE_TIMEOUT_S` 约束，超时按读数不可得处理）与 `lifecycle_config.py`（FR-007 五个变量的完整契约：`KRONOS_VRAM_PROBE_MODE=auto|torch|nvidia_smi`、`KRONOS_VRAM_PROBE_TIMEOUT_S`、三个服务端 deadline；单一来源模式不跨源回退；非法值/枚举外值启动期判红不回退默认） — verify: `tests/unit/test_f009_vram_probe.py` — 证据（2026-09-23）：`test_f009_vram_probe.py` 21 passed；三级回退且不查进程列表、单一来源不跨源、探测超时取配置与剩余预算较小者；五变量非法值逐条点名判红

### Phase 2：停机稳定性（本 feature 的真正增量）

- [x] T006 (`FR-002`, `NFR-004`, `AC-002`): 在 `kronos_real.py` 新增 `unload()`（与 `eager_load()` 对称、共用 `_lock`、`empty_cache`），挂 `POST /lifecycle/stop`：置 `desired=stopped`、卸载、返回 `{state, vram_bytes}`，幂等且**不终止进程**；卸载失败返回 `E_UNLOAD_FAILED`，落点按 design §5 表——丢引用前回落 `running`、丢引用后（含 `empty_cache` 抛错）保持 `stopped`，两者返回前都已清 `operation` — verify: `tests/unit/test_f009_lifecycle_contract.py` — 证据（2026-09-23）：unload() 以 UnloadFailed(discarded=) 表达落点；丢引用前失败回落 running、丢引用后保持 stopped，两者 operation 均已清空；幂等且不终止进程
- [x] T007 (`FR-003`, `AC-003`): 实现推理准入——`desired=stopped` 时 `generate_signal()` **不触碰** `_load_predictor()`，走 F004 既有兜底路径且来源不标 `kronos`；`/predict` 与 `/predict_batch` 共用该分支 — verify: `tests/unit/test_f009_stopped_admission.py` — 证据（2026-09-23）：`test_f009_stopped_admission.py` 5 passed；**变异**：去掉准入分支 → 3 failed（_load_predictor 被触碰）。执行机旅程：停机后 5 次 /predict 全部 source=placeholder、model_loaded 恒 false
- [x] T008 (`FR-004`, `AC-004`): 挂 `POST /lifecycle/restore`：置 `desired=running`、复用 `_load_predictor()` 既有早返回实现幂等；加载失败返回 `E_UNAVAILABLE`、`desired` 回落 `stopped`、**进程不退出**（与 F004 启动期预检失败即退出区分） — verify: `tests/unit/test_f009_lifecycle_contract.py` — 证据（2026-09-23）：restore 复用 _load_predictor 早返回实现幂等；加载失败 E_UNAVAILABLE + desired 回落 stopped + 进程不退出（未抛 SystemExit）

### Phase 3：单飞、进行中语义与可观测

- [x] T009 (`FR-006`, `AC-006`): 实现单飞仲裁——`operation` 非空时任一生命周期动作立即 `E_BUSY`，不排队不叠加；`status` 不受影响 — verify: `tests/unit/test_f009_lifecycle_errors.py` — 证据（2026-09-23）：执行机实测：2.27s 的 restore 期间并发 stop → `{'error':'E_BUSY'}`，原动作不受影响返回 running；同窗口 status 可达并报 transitional + operation 非空
- [x] T010 (`FR-006`, `NFR-004`, `AC-006`): 实现 `time.monotonic()` 截止执行器：超时返回 `E_TIMEOUT` 且**不中断**后台动作，`operation` 保持非空；后台结束后清 `operation` 并落回与 `desired` 一致的稳定态；中途抛错清理已分配显存 — verify: `tests/unit/test_f009_lifecycle_errors.py` — 证据（2026-09-23）：执行机（8013，KRONOS_LIFECYCLE_STOP_TIMEOUT_S=0.001）：stop → `{'error':'E_TIMEOUT'}`，动作未被中断，最终落点 state=stopped 且 desired=stopped、operation 转 null
- [x] T011 (`TR-001`, `TR-002`, `TR-003`, `AC-008`): 实现结构化日志行（logfmt，含 `operation_id`）与超时后迟到完成的 `result=late_complete` 收尾行；字段集为白名单，不含主机路径与凭据 — verify: `tests/unit/test_f009_lifecycle_logging.py` — 证据（2026-09-23）：`test_f009_lifecycle_logging.py` 6 passed；字段集白名单且顺序固定、含 operation_id；超时后补写同 id 的 result=late_complete；行内无主机路径/凭据

### Phase 4：部署、跨 Feature 交付边与先红态转正

- [x] T012 (`NFR-001`, `IR-005`, `AC-009`): 控制面路由**只在 real 实例注册**（`KRONOS_USE_REAL_MODEL=true`），mock 上 `/lifecycle/*` 返回 404；同时验证默认镜像 `import torch` 仍判红 — verify: `tests/integration/test_f009_lifecycle_deployment.py` — 证据（2026-09-23）：执行机：新镜像**带着**控制面代码（lifecycle_api 可导入）但 mock 实例注册的 /lifecycle 路由数为 0，三端点均 404；默认 mock 镜像 import torch 退出码非零
- [x] T013 (`NFR-002`, `NFR-003`, `AC-009`): compose 控制面端口绑 `127.0.0.1` 不发布 `0.0.0.0`（`127.0.0.1:8002:8001`）；**同一提交内迁移 F004 已验收端口契约**——改写 `docs/features/0.2/F004-kronos-inference-runtime/` 的 spec/design 端口文字、`tests/unit/test_f004_compose_profile_contract.py` 行内精确断言与变异表条目，保留「host 8002 不顶替 mock 8001」与「container 8001」原意（不迁移则统一门禁立刻判红，且这笔账不属于 F010）；FR-007 五个环境变量同步 `deployment/.env.example`；在执行机部署 `kronos-signal-real` 新镜像 — verify: `tests/integration/test_f009_lifecycle_deployment.py` + `tests/unit/test_f004_compose_profile_contract.py` + 执行机 `docker compose config` — 证据（2026-09-23）：compose 绑 127.0.0.1:8002:8001（文本契约 + 3 条变异判红 + compose config 解析双重覆盖）；.env.example 补 FR-007 五变量；F004 端口断言/变异/spec/design 同一提交内迁移，原意不变
- [x] T014 (`FR-009`, `AC-010`): 修 F003 客户端的跨 Feature 交付边（分支 `feat/F003-alphagen-vendor`）——① 分动作超时（`0ccf69e` 已落）；② "已释放"判定的训练预算条件与 `vram_readable` 分账（`ffdd805` / `2d75894` 已落）；③ **客户端 deadline = 服务端 deadline + 余量**（缺省 5s，可配），否则收不到 `E_TIMEOUT` 只收到 `OSError`；④ **恢复责任改为"本轮发出过 `stop`"触发**（`KronosOffloadOutcome` 增该事实，`cli.py` 的 finally 据此恢复），使超时/断连后的迟到完成不会永久停机；⑤ `state=transitional` 判 fail-closed。③④⑤ 为本轮新增 — verify: `tests/unit/test_f003_gpu_slot.py`、`tests/unit/test_f003_cli_contract.py` — 证据（2026-09-23）：五项在 `feat/F003-alphagen-vendor` 分支上均已落地并复核：① 分动作超时（STATUS/STOP/RESTORE_TIMEOUT_S）；② 训练预算条件（`vram_is_sufficient(limit_gb=vram_budget_gb)`，reason=training_budget_unconfirmed）与 `vram_readable` 分账（reason=vram_unreadable）；③ `client_deadline = 服务端 + CLIENT_DEADLINE_MARGIN_S(5s)`；④ `KronosOffloadOutcome.restore_required`——发出过 stop 即持有恢复责任，`restore_kronos_if_needed` 据此触发；⑤ `state=transitional` → fail_closed(reason=state_transitional)。`test_f003_gpu_slot.py` + `test_f003_cli_contract.py` 60 passed
- [x] T015 (`FR-008`, `AC-011`): 转正 F003 契约测试——移除模块级 `xfail(strict=True)`，补 `E_BUSY`（动作进行中）、`E_TIMEOUT`（短超时注入）与额外参数拒绝（断言恰为 `{"error": "E_BAD_REQUEST"}`，**不得**是 `E_UNSUPPORTED_VERSION`）三类用例 — verify: `tests/integration/test_f003_kronos_lifecycle.py` — 证据（2026-09-23）：移除模块级 xfail(strict)；补 E_BAD_REQUEST（恰为该码，非 E_UNSUPPORTED_VERSION）、E_BUSY、E_TIMEOUT 三类用例；执行机 8012 上 6 passed / **0 xfailed**
- [x] T016 (`SC-005`, `AC-012`, `NFR-006`): 把显存真实下降的判据写成机器可判定断言（`after < before` **且**卸载后整卡可用显存 ≥ 训练预算 `vram_limit_gb`），落在**独立载体** `tests/integration/test_f009_vram_release.py`，以 `xfail(strict=True)` 标注先红态并写明**解除条件与解除者**（F010 的 T011/AC-009；本 feature 不负责解除，也不以其为完成条件）。**不得放进 `test_f003_kronos_lifecycle.py`**——F003 T033 要求该文件在 `--runxfail` 下 0 xfailed，先红态放进去会让 F009 落地后 T033 仍然不可能通过 — verify: `tests/integration/test_f009_vram_release.py` — 证据（2026-09-23）：`test_f009_vram_release.py` 独立载体，判据为「读数下降 ∧ 卸载后可用显存 ≥ 训练预算」；不加 --runxfail 运行确认为 **1 xfailed 而非 XPASS**；解除条件与解除者写明 F010 AC-009/T011

## 3. 验证与验收任务

- [x] T017 (`AC-001`, `AC-002`, `AC-004`): 运行契约单元套件（字段面、stop/restore 往返与幂等、加载失败不伪报不退出） — verify: `tests/unit/test_f009_lifecycle_contract.py` — 证据（2026-09-23）：`test_f009_lifecycle_contract.py` 13 passed（字段面、stop/restore 往返与幂等、加载失败不伪报不退出）
- [x] T018 (`AC-003`): 运行停机准入套件并给出变异判红证明（去掉准入分支即红：`_load_predictor` 被调用次数从 0 变正） — verify: `tests/unit/test_f009_stopped_admission.py` — 证据（2026-09-23）：`test_f009_stopped_admission.py` 5 passed；变异判红见 T007
- [x] T019 (`AC-005`, `AC-006`, `AC-007`, `AC-008`): 运行错误面、单飞与超时、显存探测与配置、日志套件，逐条给出变异判红证明 — verify: `tests/unit/test_f009_lifecycle_errors.py`、`tests/unit/test_f009_vram_probe.py`、`tests/unit/test_f009_lifecycle_logging.py` — 证据（2026-09-23）：错误面 19 + 显存探测/配置 21 + 日志 6 = 46 passed，变异证明见各任务行
- [x] T020 (`AC-009`): 运行部署集成套件（mock 404、默认镜像 torch 否证、compose 暴露面） — verify: `tests/integration/test_f009_lifecycle_deployment.py` — 证据（2026-09-23）：`test_f009_lifecycle_deployment.py` 执行机 10 passed（mock 三端点 404、默认镜像 torch 否证、compose 回环绑定 + 3 条端口变异判红、.env.example 五变量）
- [x] T021 (`AC-010`): 运行客户端交付边套件并逐条给出变异判红证明——`test_f003_gpu_slot.py`（deadline 逐个不同且各自大于服务端值、`transitional` fail-closed、预算与 `vram_readable` 判定）与 `test_f003_cli_contract.py`（正常结束 / 取锁失败 / 运行异常三条退出路径各恰调用一次 `restore`；变异：把触发条件改回 `action=="stopped"` 即判红） — verify: `tests/unit/test_f003_gpu_slot.py`、`tests/unit/test_f003_cli_contract.py` — 证据（2026-09-23）：五条变异逐一判红（在 F003 分支实跑，跑后还原）：恢复条件退回「只在确认 stopped」→ 1 failed；去掉 deadline 余量 → 1 failed；去掉训练预算判据 → 1 failed；忽略 vram_readable → 1 failed；transitional 不再 fail-closed → 1 failed。还原后 60 passed
- [x] T022 (`AC-011`, `AC-012`): 在执行机取控制面语义证据——`ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q --runxfail tests/integration/test_f003_kronos_lifecycle.py`，该文件 **0 xfailed**（载体拆分后此文件内不得残留任何先红态）；再**单独**跑 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f009_vram_release.py`（**不加 `--runxfail`**）确认显存用例仍是 xfail 先红态、且不是 XPASS（解除它是 F010 T011 的事，不在本 feature 的收口条件里）；两次都记录 hostname 与 device — verify: `tests/integration/test_f003_kronos_lifecycle.py`、`tests/integration/test_f009_vram_release.py` — 证据（2026-09-23）：执行机 8012：`--runxfail` 跑 test_f003_kronos_lifecycle.py → **6 passed / 0 xfailed**；8013（短 deadline）单跑 E_TIMEOUT 用例 1 passed；单独跑 test_f009_vram_release.py（不加 --runxfail）→ 1 xfailed 非 XPASS。hostname=qiaozhi-lt，device=cpu
- [ ] T023 (`AC-001`, `AC-005`, `AC-009`): 运行项目统一质量门 — verify: `python3 tools/verify.py`

### [TEST] 组：层 2 旅程验收轨（必填）

- [x] T024 [TEST] (`AC-002`, `AC-003`, `AC-011`): 夜槽一轮完整旅程——`status`（running）→ `stop` → **连打若干 `/predict` 确认模型没有被唤醒**（`model_loaded` 恒 false、来源不为 kronos）→ `restore` → `status` 确认 running 且 `/predict` 恢复 kronos 来源；夹具在 Phase 1 即以红灯立起，收尾在执行机全量执行 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q tests/integration/test_f003_kronos_lifecycle.py` + 旅程逐步记录 — 证据（2026-09-23）：[TEST] 旅程在执行机全量执行：running → stop → 连打 5 次 /predict（source=placeholder、model_loaded 恒 false）→ restore → /predict 恢复 source=kronos
- [ ] T025: 回写 spec 验收证据并流转状态——**经 `scripts/sdd_status.py --dry-run` 确认门禁后 `--advance`**，不手改 frontmatter、不手工编辑 BACKLOG 派生行；同步更正 BACKLOG 中 2026-09-19 那条打在 mock 上的 404 复测记录 — verify: `python3 tools/validate_spec_lifecycle.py` + `sdd_status.py --dry-run` 输出

## 4. 依赖与并行关系

- `T001 -> T003`：契约表逐格核对通过前不落 wire 层，避免实现与架构 §7.1 漂移。
- `T002 -> T016`：GPU 基座前置在账面上可见之后，先红态的解除条件才有指向。
- `T003 -> T004`：版本协商与信封先立，三个端点共用同一拒绝路径。
- `T004 -> T006`：期望态与派生口径先定，stop 才知道该置什么、该报什么。
- `T005 -> T019`：显存探测与配置契约的载体由本项落盘。
- `T006 -> T007 -> T008`：卸载能力 → 停机准入 → 恢复，严格串行（准入依赖 stop 已置位的 desired）。
- `T008 -> T009 -> T010`：端点齐备后再加仲裁与超时，否则 `E_BUSY` / `E_TIMEOUT` 无处可挂。
- `T008 -> T017`：契约单元套件的载体由 T003–T008 共同声明，T008 是其直接生产者。
- `T007 -> T018`：准入套件的载体由 T007 落盘。
- `T010 -> T019`、`T011 -> T019`：错误面与日志两个载体分别由这两项落盘。
- `T012 -> T020`、`T013 -> T020`：部署集成套件的载体由路由注册与 compose 两项共同落盘。
- `T014 -> T021`：客户端超时改完才谈得上验收它。
- `T015 -> T016`：先移除模块级 xfail，再把显存判据挂成独立载体的先红态。
- `T015 -> T022`：T022 取证的文件由 T015 生产——载体拆分后 T016 产的是 `test_f009_vram_release.py`，不再承接 T022 的 verify 文件。
- `T016 -> T022`：先红态就位后，执行机上才分得清「控制面 0 xfailed」与「显存用例仍先红」。
- `T017 -> T023`、`T018 -> T023`、`T019 -> T023`、`T020 -> T023`、`T021 -> T023`：各条测试轨全绿后跑统一质量门。
- `T022 -> T024`：控制面证据取到后，旅程轨做收尾全量执行。
- `T023 -> T025`、`T024 -> T025`：质量门与旅程轨都绿才流转状态。
- `T005 [P]`：只新建 `vram.py` / `lifecycle_config.py` 与其单测，与契约层不共享状态、不改同一文件，可与 Phase 1 其余任务并行。

## 5. 明确后移

- GPU 推理基座（CUDA 镜像、compose 设备预留、`device`/healthcheck 断言改写、F004 回归契约与变异门迁移）→ **F010**：本 feature 的硬前置，AC-012 的证据随其落地补取。
- 挖掘侧编排、单槽 FIFO 取锁与 `kronos_offload` 运行记录字段 → `F003`（tasks T025 / T033）：本 feature 只提供服务端与客户端契约约束。
- 审计事件入库与运营写路径（FR7.4）→ `F006`：本 feature 只写容器日志行，不建第二个口径载体（ADR-0005）。
- 通用服务生命周期框架与第二个服务的控制面 → 出现第二个消费者时再立项。
- 控制面鉴权（token / mTLS）→ 执行机分离或跨机调用前必须先补；当前安全边界是网络可达性（NFR-003）。
- `stop` 的 draining 态（等待在飞请求排空再停）→ 需先改架构 §7.1 的状态取值域；当前由 FR-003 的准入语义消解了该需求（停机期间根本不加载模型）。
- 执行机整体迁移到 `qiaozhi-lab` 后的重新取证 → 随 F003 的同名迁移 Feature。
