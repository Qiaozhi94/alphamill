---
kind: feature
id: F004
version: "0.2"
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: tasks
created: 2026-09-12
updated: 2026-09-15
---

# F004：Kronos 真实推理运行时 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
- 集成与容器验收只在执行机 `qiaozhi-lt` 采集，证据记录 hostname 与 `device=cpu`；开发机只跑静态与单元门禁（SOP §3）。
- 实现任务遵循先红后绿：任务内的契约测试必须先失败（复现缺口）再随实现转绿，不得先实现后补测试。

## 1. 前置条件

- F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态实测证据；回填数据满足目标 exchange/symbol ≥30 根已闭合 1m K 线。
- spec §8 Q-001 已关闭（F004 不阻塞 F002 done）；design §10 待确认设计问题为空，无阻塞性设计问题。

## 2. 实现任务

### Phase 1：薄壳运行时改造

- [x] T001 (`FR-001`): 先红后绿——新增 `tests/unit/test_f004_kronos_runtime_contract.py::test_real_mode_preflight_fails_closed_without_assets`（fake 目录注入，先失败）；实现 `kronos_real.py` 启动预检与 eager load，并由 `server.py` 启动钩子在 real 模式调用：校验 `KRONOS_REPO_PATH`、模型与分词器目录及必需文件（`config.json`、权重文件），任一缺失或加载失败即打印缺失路径并非零退出，不退回 mock — verify: 该用例由红转绿
- [x] T002 (`FR-001`): 先红后绿——新增同文件 `::test_predictor_loads_once_and_inference_serializes`（先失败）；实现进程级推理锁：模型加载至多一次、推理互斥（含并发首请求同时到达的场景） — verify: 该用例由红转绿

### Phase 2：镜像与编排

- [x] T003 (`FR-001`, `NFR-001`): 先红后绿——新增 `tests/unit/test_f004_compose_profile_contract.py::test_dockerfile_targets_pin_real_dependencies`（先失败）；实现 `deployment/kronos-service.Dockerfile` 拆 `mock`/`real` 两个构建目标：real 从 CPU wheel index 安装 design §2 锁定的 torch 与最小推理依赖（einops/safetensors/huggingface_hub/tqdm），mock 保持现状且不含 torch — verify: 该用例由红转绿
- [x] T004 (`FR-001`, `NFR-001`): 先红后绿——新增同文件 `::test_compose_real_service_contract`（先失败）；实现 compose 两服务：`kronos-signal-real`（`profiles: [kronos-real]`、`target: real`、`:ro` 挂载、`8002:8001`、KRONOS_* 与 DB_* 环境、`depends_on: timescaledb: {condition: service_healthy}`、`networks: [alphamill]`、healthcheck 以 `model_loaded=true` 为通过条件、失败不自动重启）；`kronos-signal` 显式 `target: mock` — verify: 该用例由红转绿 + `docker compose -f deployment/docker-compose.yml config --services`（不含 real）与 `docker compose -f deployment/docker-compose.yml --profile kronos-real config`（含 real）

### Phase 3：门禁补全与文档回写

- [x] T005 (`AC-001`): 静态门禁补全与变异验证：默认配置不含 real 服务、mock 目标不含 torch、real 含 DB 接线；变异验证（改 target、删依赖 pin、去掉 `:ro`、删 DB 依赖必须判红） — verify: `tests/unit/test_f004_compose_profile_contract.py` 全绿 + 变异记录
- [x] T006 (`AC-001`, `AC-002`): 容器集成测试：compose 拉起 real 实例后校验容器身份（compose 托管 + real 目标 + 只读挂载 + 端口映射）与完整运行链（模型 + TimescaleDB：`/health` 的 `database` 可达 + `/predict source=kronos`）；缺资产场景非零退出；默认镜像 `import torch` 判红 — verify: `tests/integration/test_f004_real_profile.py`
- [x] T007 (`FR-001`): 更新 `vendor/VENDORED.md`：补容器内路径（`/app/vendor/Kronos`、`/app/models/Kronos-base`、`/app/models/Kronos-Tokenizer-base`）与 real profile 说明 — verify: `grep -n "/app/vendor/Kronos" vendor/VENDORED.md`

## 3. 验证与验收任务

- [x] T008 (`AC-001`, `AC-002`): 在执行机 `qiaozhi-lt` 跑集成验收：F001 冒烟（HTTP 契约）+ F004 容器集成 + 默认镜像否证，证据记录 hostname 与 `device=cpu` — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`
- [x] T009 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`
- [x] T010 (`AC-001`): 回写 spec §6 验收证据（命令、输出摘要、取证机 hostname、device） — verify: `python3 tools/verify.py`（文档门禁）
- [x] T011 (`AC-001`, `NFR-001`): 运行项目统一质量门并全绿 — verify: `python3 tools/verify.py`
- [x] T012: 状态推进（spec frontmatter）与 BACKLOG 同步 — verify: `python3 tools/verify.py`（含生命周期与 BACKLOG 双向校验）

## 4. 依赖与并行关系

- `T001 -> T002`：同一薄壳文件的顺序改造（预检/加载 → 锁；各自测试在同一任务内先红后绿）。
- `T001/T002 -> T006`：容器集成依赖启动预检、eager load 与串行推理行为成立。
- `T003 -> T004`：compose `target` 依赖 Dockerfile 目标定义。
- `T003/T004 -> T005`：静态门禁在全量断言（含默认隔离）与变异验证后定稿。
- `T002/T005 -> T006`：容器集成建立在薄壳行为与静态契约通过之上。
- `T006 -> T007`：VENDORED.md 容器路径回写以编排与薄壳契约定稿为前提（不依赖实测）。
- `T006 -> T008`：执行机实测以容器集成测试定稿为前提（其依赖闭包已含全部实现与门禁任务）。
- `T008 -> T009/T010`：F001 命令回写与 F004 验收证据回写都以执行机实测通过为前提；二者修改不同文件，顺序无关。
- `T007/T009/T010 -> T011 -> T012`：全量门禁覆盖全部回写后执行；状态/BACKLOG 同步以门禁全绿为前提。

## 5. 明确后移

- GPU 直通与推理性能优化 → `v0.2.x` 后续评估：需执行机 GPU 直通条件，不属本 feature。
- 消费者路由切换（Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 指向真实实例）→ `v0.2.x` 后续评估（未立项）：真实实例与 mock 并存是本期形态，路由切换涉及默认链路可用性与跨 feature 契约，F004 只交付编排内可复现的真实信号源（spec §3 范围外）。
