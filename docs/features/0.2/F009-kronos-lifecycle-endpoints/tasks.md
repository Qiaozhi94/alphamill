---
kind: feature
id: F009
version: "0.2"
related_features: [F003, F004]
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
- 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录（及 `tests/contract`、`tests/property`、`tests/mutation`）。
- **机器边界**（架构 §7.1、`docs/SOP.md` §3）：编码、单元测试与门禁在开发机 `qiaozhi-gp`；真实卸载与显存证据一律在执行机 `qiaozhi-lt` 取，证据必须记录 hostname、GPU 型号与 stop 前后读数。开发机上 GPU 用例跳过是预期行为，不算证据也不算失败。
- **契约不可改**：架构 §7.1 是契约正文的所有者。任何实现期发现的契约缺陷，先改架构文档并同步 `tools/check_doc_consistency.py` 的 `offload_decision_table_rows` 期望值，再改实现——不得在本 feature 内单方面改语义。
- **变异判红纪律**（F004 检视循环 12 的既定做法）：每条新断言须给出"改坏实现即判红"的证明，不接受只会绿的断言。
- **mock 依赖面红线**：F004 NFR-001 的否证测试「默认镜像 `import torch` 判红」在本 feature 全程必须保持绿；torch / GPU 相关导入一律函数内惰性化。

## 1. 前置条件

- [ ] T001 (`FR-001`): 确认 spec §8 与 design §10 无开放问题，且架构 §7.1 契约表与本 feature 的接口表逐格一致（动作/幂等/超时/错误码四列） — verify: `spec.md` §8、`design.md` §10、`docs/alphamill-architecture.md` §7.1
- [ ] T002 (`FR-002`, `NFR-005`): 在执行机 `qiaozhi-lt` 取基线——确认 `kronos-signal-real` 在跑且 `device` 非 cpu，记录 `nvidia-smi --query-gpu=memory.used` 可用性与当前读数，作为 AC-010 的 stop 前对照 — verify: 执行机上 `docker compose ps kronos-signal-real` + `nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits`

## 2. 实现任务

### Phase 1：契约骨架与状态查询（US-001 最小切片）

- [ ] T003 (`FR-004`, `IR-002`, `AC-004`): 实现 `require_contract_version` 依赖与统一错误信封 `{"error": "E_*"}`（错误亦走 HTTP 200，避免中间件改写丢字段）；头缺失与版本不匹配都拒绝，不按默认版本放行 — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T004 (`FR-001`, `IR-001`, `IR-003`, `AC-001`): 新建 `lifecycle.py` 与 `LifecycleController.status()`，`state` 从 `real_signal.status().loaded` 派生（不存第二份状态），挂 `GET /lifecycle/status` 返回五字段 — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T005 [P] (`NFR-005`, `AC-006`): 新建 `vram.py` 设备侧显存探测——`torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used` → 不可得返回 `None` 三级回退；torch 导入惰性化；**不查 GPU 进程列表**（WSL2 下不列出） — verify: `tests/unit/test_f009_vram_probe.py`

### Phase 2：停止、恢复与错误面（US-001 / US-002 / US-003）

- [ ] T006 (`FR-002`, `NFR-004`, `AC-002`): 在 `kronos_real.py` 新增 `unload()`，与 `eager_load()` 对称、共用 `_lock`：丢弃 predictor 引用 + `torch.cuda.empty_cache()`，保留 device/torch 引用，清空 `_load_error`；既有推理路径零改动 — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T007 (`FR-002`, `AC-002`): 挂 `POST /lifecycle/stop`——卸载后返回 `{state: stopped, vram_bytes}`，重复调用返回 `stopped` 不报错，**不终止进程**（stop 后 status/restore 仍可达） — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T008 (`FR-003`, `AC-003`): 挂 `POST /lifecycle/restore`——复用 `_load_predictor()` 既有早返回分支实现幂等；加载失败返回 `E_UNAVAILABLE` 且 `status` 如实报 `stopped`/`model_loaded=false`，不伪报 running — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T009 (`FR-005`, `AC-005`): 实现在飞推理计数（带锁整数 + `track()` 上下文管理器），包装 `/predict` 与 `/predict_batch`；`stop` 读到非零立即返回 `E_BUSY`，不等待不强停，模型保持加载 — verify: `tests/unit/test_f009_lifecycle_errors.py`
- [ ] T010 (`FR-005`, `NFR-002`, `AC-005`): 实现超时执行器——工作放单线程执行器，主协程以 `time.monotonic()` **截止时刻**等待（禁止固定步长累加，F004 Q003 教训），超时返回 `E_TIMEOUT` 且不取消后台工作；显存读数不可得时 `vram_bytes=null` + `E_UNAVAILABLE`，**不猜 0** — verify: `tests/unit/test_f009_lifecycle_errors.py`

### Phase 3：可观测性与配置化

- [ ] T011 (`TR-001`, `TR-002`, `TR-003`, `AC-008`): 实现 stop/restore 的结构化日志行（logfmt：action/result/state_before/state_after/vram_bytes_before/vram_bytes_after/contract_version/elapsed_ms），字段集为白名单，不含主机路径与凭据 — verify: `tests/unit/test_f009_lifecycle_logging.py`
- [ ] T012 (`NFR-002`, `AC-009`): 三个超时（5s/60s/120s）与显存探测方式改为环境变量可覆盖，全部无写死常数；同步 `deployment/.env.example` — verify: `tests/integration/test_f009_lifecycle_mock.py`

### Phase 4：mock 面、部署与先红态转正

- [ ] T013 (`FR-006`, `NFR-001`, `AC-007`): mock 实例（`KRONOS_USE_REAL_MODEL=false`，无 torch）三端点照常响应：`device=cpu`/`model_loaded=false`/`vram_bytes=0`，stop/restore 为 no-op；同时验证默认镜像 `import torch` 仍判红 — verify: `tests/integration/test_f009_lifecycle_mock.py`
- [ ] T014 (`NFR-003`, `AC-009`): compose 把控制面端口绑 `127.0.0.1` 而非 `0.0.0.0`（不对宿主外网暴露），并在执行机部署 `kronos-signal-real` 新镜像 — verify: `tests/integration/test_f009_lifecycle_mock.py` + 执行机 `docker compose config`
- [ ] T015 (`FR-007`, `AC-010`): 转正 F003 契约测试——移除模块级 `xfail(strict=True)`，补 `E_BUSY`（在飞时 stop）与 `E_TIMEOUT`（短超时注入）两条错误路径用例 — verify: `tests/integration/test_f003_kronos_lifecycle.py`

## 3. 验证与验收任务

- [ ] T016 (`AC-001`, `AC-002`, `AC-003`, `AC-004`): 运行契约单元套件（字段面、停止/恢复往返与幂等、版本协商） — verify: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] T017 (`AC-005`, `AC-006`, `AC-008`): 运行错误面、显存探测与日志单元套件；逐条给出变异判红证明 — verify: `tests/unit/test_f009_lifecycle_errors.py`、`tests/unit/test_f009_vram_probe.py`、`tests/unit/test_f009_lifecycle_logging.py`
- [ ] T018 (`AC-007`, `AC-009`): 运行 mock 集成套件（三端点行为、超时可配反向断言、compose 暴露面、默认镜像 torch 否证） — verify: `tests/integration/test_f009_lifecycle_mock.py`
- [ ] T019 (`AC-010`): 在执行机取真实卸载证据——`ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q --runxfail tests/integration/test_f003_kronos_lifecycle.py` **0 xfailed**，并记录 hostname、GPU 型号与 stop 前后设备侧显存读数对照 — verify: `tests/integration/test_f003_kronos_lifecycle.py`
- [ ] T020 (`AC-001`, `AC-004`, `AC-007`): 运行项目统一质量门 — verify: `python3 tools/verify.py`

### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T021 [TEST] (`AC-002`, `AC-010`): 夜槽一轮完整旅程——`status`（running，记显存）→ `stop` → `status` 确认 `stopped` 且设备侧显存实际下降 → 模拟取锁训练窗口 → `restore` → `status` 确认 `running` 且 `/predict` 产出非 placeholder 信号；夹具在 Phase 1 即以红灯立起，收尾在执行机全量执行 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q tests/integration/test_f003_kronos_lifecycle.py` + 旅程逐步读数记录
- [ ] T022: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter；同步更正 BACKLOG 中 2026-09-19 那条打在 mock 上的 404 复测记录 — verify: `python3 tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T003`：契约表逐格核对通过前不落 wire 层，避免实现与架构 §7.1 漂移。
- `T002 -> T019`：执行机基线读数是 AC-010 的 stop 前对照，没有它真实取证无从判断显存是否真的降了。
- `T003 -> T004`：版本协商与错误信封先立，三个端点共用同一拒绝路径。
- `T004 -> T006`：状态派生口径先定，卸载才知道该让 `status` 报什么。
- `T006 -> T007 -> T008`：卸载能力 → stop 端点 → restore 端点，严格串行（restore 复用 stop 之后的状态面）。
- `T008 -> T009 -> T010`：端点齐备后再加错误面，否则 `E_BUSY` / `E_TIMEOUT` 无处可挂。
- `T008 -> T016`：契约单元套件的载体由 T003–T008 共同声明，T008 是其直接生产者。
- `T005 -> T017`、`T010 -> T017`、`T011 -> T017`：错误面、显存探测与日志三个载体分别由这三项落盘。
- `T012 -> T018`、`T013 -> T018`：mock 集成套件的载体由配置化与 mock 行为两项共同落盘。
- `T014 -> T015`：端点部署到执行机之后，才有可能让 F003 契约测试真正转正。
- `T015 -> T019`：先红态移除与错误路径用例补齐后，才谈得上 0 xfailed 的取证。
- `T016 -> T020`、`T017 -> T020`、`T018 -> T020`：三条测试轨全绿后跑统一质量门。
- `T019 -> T021`：真实取证通过后，旅程轨做收尾全量执行。
- `T020 -> T022`、`T021 -> T022`：质量门与旅程轨都绿才回写状态。
- `T005 [P]`：只新建 `vram.py` 与其单测，与契约层不共享状态、不改同一文件，可与 Phase 1 其余任务并行。

## 5. 明确后移

- 挖掘侧编排、单槽 FIFO 取锁与 `kronos_offload` 运行记录字段 → `F003`（tasks T025 / T033）：本 feature 只提供被调用的服务端，编排侧证据归 F003。
- 审计事件入库与运营写路径（FR7.4）→ `F006` 运营操作入口：本 feature 只写容器日志行，不建第二个口径载体（ADR-0005）。
- 通用服务生命周期框架与第二个服务的控制面 → 出现第二个消费者时再立项：只有一个实例时抽象是负债。
- 控制面鉴权（token / mTLS）→ 执行机分离或跨机调用前必须先补：当前安全边界是网络可达性（NFR-003），单机自用成立。
- `stop` 的 draining 态（等待在飞请求排空再停）→ 需先改架构 §7.1 的 `state` 取值域：当前契约只有 running/stopped 两值，引入第三态属改契约。实测重试率高时再提。
- 执行机整体迁移到 `qiaozhi-lab` 后的重新取证 → 随 F003 的同名迁移 Feature：本 feature 只面向当前执行机 `qiaozhi-lt` 验收，迁移后重跑 AC-010 而非继承结论。
