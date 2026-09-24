---
kind: feature
id: F009
version: "0.2"
related_features: [F003, F004, F010]
topics: [kronos, lifecycle, control-plane, gpu-slot, m2]
doc_kind: design
created: 2026-09-20
updated: 2026-09-20
---

# F009：Kronos 服务生命周期控制面端点 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：`docs/alphamill-architecture.md` §7.1（契约正文所有者；本次的期望态、单飞与进行中语义、单键错误信封、显存确认判据、分动作超时、GPU 基座前置均已先行落在该节。**本 feature 只实现不改**；再有契约缺陷须先改该节并同步 `tools/check_doc_consistency.py` 的 `offload_decision_table_rows` 期望值）
- **ADR / 上游 Contract**：ADR-0002（Kronos 上游 clone + pin）；ADR-0005（不新增口径载体）
- **F010「Kronos GPU 推理基座」**：显存**真实证据**的所有者（其 AC-009/T011）。本 feature 不以它为完成前置——AC-012 止于载体与先红态；方向是 F010 消费本 feature，不是互相等待（R4-003）
- **实现约束**：
  - mock 镜像不得引入 torch（F004 NFR-001 否证测试为硬门）→ torch / GPU 相关导入一律惰性化，**控制面路由只在 real 实例注册**；
  - `KronosRealSignal._lock` 的既有不变式（模型加载至多一次 + 推理互斥）不得破坏；
  - 超时用 `time.monotonic()` 截止时刻，不用固定步长累加（F004 Q003 的原样教训）；
  - `/predict*` 的**对外响应契约不变**，只增加停机期间的准入分支。

## 1. 技术概要与影响面

控制面的核心不是三个路由，而是**一份被显式存储的期望态**加上**一个单飞的动作执行器**。`desired` 由 `stop` / `restore` 置位；`state` 由 `(desired, model_loaded)` 派生；推理路径读 `desired` 决定是否允许加载模型——这三件事合起来才让 `stopped` 稳定。动作执行器保证同一时刻至多一个动作在跑，并把"进行中"提升为一等可观测状态（`operation`），使超时不再产生无法解释的迟到副作用。

- 前端：不适用（无 UI，ADR-0005）。
- 后端 / API：`kronos_service/lifecycle.py`（新增：期望态持有者、单飞执行器、operation 台账、错误码）、`kronos_service/vram.py`（新增：设备侧探测与三级回退）、`kronos_service/lifecycle_config.py`（新增：环境变量契约与启动期校验）、`server.py`（新增三路由 + 版本协商依赖 + real 实例条件注册）、`kronos_real.py`（新增 `unload()` 与 `allow_load` 准入判定；`generate_signal` 在 `desired=stopped` 时走兜底不加载）。
- 存储 / Migration：不适用（无持久化实体）。
- Runtime / Agent Adapter：`deployment/docker-compose.yml` 的 `kronos-signal-real`——host 绑定由 `8002:8001` 收严为 `127.0.0.1:8002:8001`；新增生命周期环境变量（`.env.example` 同步）。**同一提交内迁移 F004 已验收端口契约**：F004 spec/design 的端口文字、`tests/unit/test_f004_compose_profile_contract.py` 的精确断言与变异表（保留「host 8002 不顶替 mock 8001」与「container 8001」原意）——否则统一门禁在本 feature 实现期就判红（R4-007）。
- Event / Evidence：结构化日志行（TR-001/002），落容器日志，不入库、不建面板。
- 文档 / 配置：BACKLOG「规划中」新增 F010 行；`docs/alphamill-integration.md` 补控制面运维段。
- **跨 Feature**：F003 的 `kronos_offload` 客户端改分动作超时（并加 deadline 余量）、把"已释放"判定收紧到训练预算与 `vram_readable` 分账（FR-009，预算由 `mine_config` 从 `vram_limit_gb` 透传）、把恢复触发条件从"同步确认 stopped"改为"本轮发出过 stop"（R4-002，落点在 `cli.py` 的 finally）；`tests/integration/test_f003_kronos_lifecycle.py` 转正并补用例；显存判据落独立载体 `tests/integration/test_f009_vram_release.py`（避免与 F003 T033 的 0-xfailed 门禁互相拆台）。

## 2. 架构与模块边界

```text
  F003 gpu_slot ──► server.py  /lifecycle/*            仅 real 实例注册路由
 （夜槽编排，唯一     - require_contract_version        （mock 不注册 → 404）
   程序调用方）       - 三路由，单键错误信封
                            │
                    ┌───────▼─────────────────────┐
                    │ lifecycle.py                │
                    │  LifecycleController        │   desired 是唯一被存储的意图；
                    │   - desired（存储）          │   state 由 (desired, loaded) 派生
                    │   - single-flight + operation│
                    │   - monotonic 截止执行器      │
                    └───┬──────────────┬───────────┘
                        │              │
          ┌─────────────▼──┐     ┌─────▼────────┐     ┌──────────────────┐
          │ kronos_real    │     │ vram.py      │     │ lifecycle_config │
          │  unload/load   │     │ 设备侧已用字节 │     │ 环境变量 + 校验   │
          │  allow_load ◄──┘     └──────────────┘     └──────────────────┘
          │  （推理准入读 desired）
          └────────────────┘
```

职责划分：

- **`server.py`** 只做 wire 层：版本协商、请求体校验、调用控制器、序列化成契约信封。不含状态判断。
- **`lifecycle.py`** 是控制面的唯一写入口：持有 `desired` 与 `operation`，保证单飞。它**不存 `state`**——每次从 `(desired, real_signal.status().loaded)` 计算。
- **`kronos_real.py`** 增 `unload()`（与 `eager_load()` 对称）与 `allow_load` 准入：`generate_signal()` 在不允许加载时直接走既有兜底路径，不碰 `_load_predictor()`。
- **`vram.py`** / **`lifecycle_config.py`** 是无状态的探测与配置解析，各自可单测。
- 依赖方向单向：`server → lifecycle → {kronos_real, vram, lifecycle_config}`。

## 3. 数据模型与 Migration

不适用：不新增或修改持久化实体。`desired` 与 `operation` 是进程内存态；进程重启后由 F004 既有的启动预检 + eager load 决定初始态（real 模式为 `desired=running`）。停机意图**有意不持久化**——夜槽每轮都会重新 `stop`，持久化会让人工重启后白天拿不到信号。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 方法 | 路径 | 成功响应字段 | 默认超时（环境变量） | 错误码 |
|---|---|---|---|---|
| GET | `/lifecycle/status` | `state`(`running`/`stopped`/`transitional`)`, desired, contract_version, model_loaded, vram_bytes, vram_readable, device, operation` | 服务端处理 deadline 5s (`KRONOS_LIFECYCLE_STATUS_TIMEOUT_S`) | `E_UNSUPPORTED_VERSION` |
| POST | `/lifecycle/stop` | `state, vram_bytes` | 服务端动作 deadline 60s (`KRONOS_LIFECYCLE_STOP_TIMEOUT_S`) | `E_BUSY` / `E_TIMEOUT` / `E_UNLOAD_FAILED` / `E_BAD_REQUEST` / `E_UNSUPPORTED_VERSION` |
| POST | `/lifecycle/restore` | `state` | 服务端动作 deadline 120s (`KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S`) | `E_BUSY` / `E_TIMEOUT` / `E_UNAVAILABLE` / `E_BAD_REQUEST` / `E_UNSUPPORTED_VERSION` |

- **错误信封**：恰为 `{"error": "E_*"}` 单键对象，HTTP 200。成功与错误互斥：成功响应不含 `error`，错误响应不含任何其他字段。用 200 而非 4xx/5xx 是因为契约测试只认信封——非 2xx 可能被中间件改写成错误页而丢掉 `error` 字段。
- **版本协商**：依赖 `require_contract_version` 读 `X-Contract-Version`；缺失或 ≠ `"1"` 即 `E_UNSUPPORTED_VERSION`，**缺失不按默认版本放行**。
- **请求体**：`stop` / `restore` 接受空体或 `{}`；任何其他键一律 `E_BAD_REQUEST`，防止在契约外偷加 `force` 之类开关。**不复用 `E_UNSUPPORTED_VERSION`**——后者是客户端判定"服务端未实现本契约"的入口（决策表第三行回落探测），两者混用会让请求构造错误被误读成服务端缺失。
- **`state` 的取值域**：`running` / `stopped` / `transitional`。动作受理后先置 `desired`、后改 `model_loaded`，这段窗口里 `state` 只能是 `transitional`（`operation` 同时非空）——二值取值域会让服务端在自己最常见的执行路径上构造不出合法响应（R4-001）。客户端对 `transitional` fail-closed。
- **超时的归属**：表中三个值都是**服务端** deadline，由服务端环境变量承载。客户端的 socket deadline 另算，且必须严格更大（缺省 +5s 余量）；两端同值时客户端先抛 `OSError`，服务端的 `E_TIMEOUT` 信封收不到（R4-002）。
- **`status` 的 deadline 执法**：处理入口取 `time.monotonic() + status_deadline`，显存探测（`mem_get_info` / `nvidia-smi` 子进程）只拿**剩余预算**且再受 `KRONOS_VRAM_PROBE_TIMEOUT_S`（缺省 2s）约束；探测超时/失败按读数不可得返回成功响应。status **不进单飞执行器**——它必须在动作进行中也可达（R1-008）。
- **探测模式**：`KRONOS_VRAM_PROBE_MODE=auto|torch|nvidia_smi`，缺省 `auto`（torch → nvidia-smi → 不可得）；`torch` / `nvidia_smi` 只用单一来源，失败即不可得、不跨源回退。非法值启动期判红（R1-009）。
- **`operation`**：`null` 或 `{id, action, started_at}`；`id` 为 uuid4 十六进制前 8 位，进入日志行做关联键。
- **`vram_bytes` 语义**：设备侧整卡已用字节。读数不可得时 `vram_readable=false` + `vram_bytes=null`，**仍是成功响应**；无 CUDA 时 `vram_bytes=0` + `vram_readable=true` + `device=cpu`。
- **mock**：路由在 `KRONOS_USE_REAL_MODEL=false` 时不注册，`/lifecycle/*` 自然 404。

### Event / Trace Contract

单行 `logfmt`，便于 `docker logs | grep 'action='`：

```text
action=stop operation_id=9f3a1c02 result=ok state_before=running state_after=stopped desired=stopped vram_bytes_before=3221225472 vram_bytes_after=142606336 vram_readable=true contract_version=1 elapsed_ms=412
action=stop operation_id=9f3a1c02 result=late_complete state_before=running state_after=stopped desired=stopped ... elapsed_ms=71204
```

- 超时返回后动作最终完成时补写一条同 `operation_id` 的 `result=late_complete` 收尾行（TR-002），使迟到落点可追；
- 字段集是白名单，不含主机路径（模型路径除外）、凭据或连接串（TR-003）。

## 5. Runtime、Workflow 与并发

**期望态与派生态**：`desired` 是控制器里唯一被存储的意图；`state = running if desired == "running" and loaded else stopped if desired == "stopped" and not loaded else transitional`。过渡态对外通过 `operation` 非空表达——这样"状态变量与事实不一致"这一类缺陷仍被排除（不存第二份 `state`），同时"停机意图"这项**事实不足以从内存推断**的信息被显式持有。

**推理准入（`stopped` 稳定性的机制保证）**：`generate_signal()` 进入时先问 `allow_load`（由控制器的 `desired` 决定）：

```text
desired=running  → 既有路径（必要时 _load_predictor()）
desired=stopped  → 直接走 F004 既有兜底信号路径，不触碰 _load_predictor()，
                   来源如实标注非 kronos（F004 C002 同一纪律）
```

没有这一条，`stop` 之后任一 `/predict` 都会重新加载模型、把显存吃回去——这是原设计最严重的机制缺口（检视 R1-002）。

**单飞执行器**：控制器持一把 `threading.Lock` 保护 `(desired, operation)` 元数据，另以"是否已有 operation"实现动作互斥：

| 到达动作 | `operation is None` | `operation` 非空 |
|---|---|---|
| `stop` / `restore` | 置 `desired`、开 operation、提交后台执行 | 立即 `E_BUSY`（不排队、不叠加） |
| `status` | 正常返回 | 正常返回，`operation` 非空 |

**超时与迟到落点**：后台工作提交到单线程执行器；主协程以 `time.monotonic() + timeout` 为**截止时刻**等待。超时返回 `E_TIMEOUT` 且**不取消**后台工作（强行中断会留下半加载态，违反 NFR-004）。后台工作完成时由 finally 清 `operation`、补写 `late_complete` 日志。客户端据此 fail-closed，并以 `operation=null` 作为最终落点判据。

**卸载路径**（`kronos_real.unload()`，与 `eager_load()` 对称）：持 `_lock` → `_predictor = None` → 若 `_torch` 非空则 `empty_cache()`（否则设备侧读数不会下降）→ 保留 `_device` / `_torch` 引用、清 `_load_error`。

**卸载失败的落点**（R4-004）：以"模型引用是否已丢弃"为分界，因为那一步不可逆。

| 注入点 | `desired` | `model_loaded` | 响应 | 依据 |
|---|---|---|---|---|
| 取锁 / 卸载**尚未开始**即抛错 | 回落 `running` | `true` | `E_UNLOAD_FAILED` | 什么都没动，回到原状最诚实 |
| `_predictor = None` **之后**抛错 | 保持 `stopped` | `false` | `E_UNLOAD_FAILED` | 引用已丢，回滚 `running` 是谎报——模型并不在内存里 |
| `empty_cache()` 抛错 | 保持 `stopped` | `false` | `E_UNLOAD_FAILED` | 同上；显存可能未回收，`status.vram_bytes` 如实报，编排据"未释放"fail-closed |

三种情况都必须**先清 `operation`、先收敛状态，再返回错误信封**——"返回了错误但状态停在过渡态"是被不变量禁止的。

**迟到副作用的端到端归属**（R4-002）：服务端只保证"可观测"（`operation` 转 `null`），补偿由客户端做：**发出过 `stop` 就持有恢复责任**，不看该请求返回什么。选"无条件 restore"而不是"轮询 operation 到终态"——`restore` 幂等，未真停机时无副作用；而轮询必须设界，界外的迟到完成照样漏。

**恢复路径**：复用 `_load_predictor()` 既有的"已加载即返回"分支，幂等天然成立。加载抛错 → 清理已分配显存 → `desired` 保持 `running` 还是回落 `stopped`？**回落 `stopped`**：否则实例会停在"期望 running 但加载不上"的过渡态里，`state` 无法落回稳定态，违反 §5 不变量；同时返回 `E_UNAVAILABLE` 让调用方知道恢复没成。

**不可回滚副作用边界**：`stop` 会中断白天的实时信号能力（dry-run 退回读 `signal_cache` 存量信号，架构 §7.1 时段表即如此设计），可由 `restore` 复原；除此之外无不可逆副作用。

## 6. UI 与可观测性

- 页面：不适用（ADR-0005：运营状态不进研究控制台）。
- 日志：TR-001/002 的结构化行是唯一新增观测面，落容器日志，不新增指标口径载体、不建面板。
- `/health` 保持 F004 原样不动——它报模型与数据库健康，`state`/`desired` 的权威读法是 `/lifecycle/status`。两者字段有重叠但都从 `real_signal.status()` 派生，不构成第二真相源。
- 运维可见性：`docker logs kronos-signal-real | grep 'action='` 可还原当晚是否真的卸载、显存降了多少、有没有迟到完成。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：

  | 条件 | 返回 |
  |---|---|
  | 缺 `X-Contract-Version` 或值不匹配 | `E_UNSUPPORTED_VERSION` |
  | 请求体含契约外的键 | `E_BAD_REQUEST` |
  | 已有动作进行中 | `E_BUSY` |
  | 动作未在可配超时内完成（后台继续） | `E_TIMEOUT` |
  | 卸载 / `empty_cache` 抛错（`stop`） | `E_UNLOAD_FAILED`（落点见 §5 表：丢引用前回落 `running`，丢引用后保持 `stopped`） |
  | 模型资产缺失 / 加载抛错（`restore`） | `E_UNAVAILABLE`（`desired` 回落 `stopped`） |
  | 显存探测超时 / 失败（`status`） | **成功响应** + `vram_readable=false`，status 不得超过服务端 deadline |
  | 显存读数两级探测皆不可得（`status`） | **成功响应** + `vram_readable=false` + `vram_bytes=null` |
  | **状态查询本身抛错**（`status`；代码检视 R2-002 补） | **成功响应** + `model_loaded=false` + `device=unknown` + 读数不可得——status 没有可用失败码（契约只给 `E_UNSUPPORTED_VERSION`），漏成 500 会被客户端读成"端点不存在"并转入回落探测 |
  | **未预期异常**（`stop`/`restore`；代码检视 R2-002 补） | wire 层按端点映射为 `E_UNLOAD_FAILED`/`E_UNAVAILABLE`；控制器侧先按事实把 `desired` 收敛到稳定态（`_converge_after_failure`，读不到状态时取 fail-closed 一侧，绝不声称已卸载） |
  | **卸载成功但随后读数失败**（`stop`；代码检视 R2-001） | 仍是**成功**响应 `{state: stopped, vram_bytes: null}`——卸载不可逆，"报告失败"不等于"卸载失败" |

- **重启与恢复**：进程重启由 F004 既有 lifespan（预检 + eager load）决定初始态，`desired` 初始为 `running`。停机意图不持久化（见 §3）。
- **启动失败 vs 运行期失败**（检视 R1-010）：**两件事，处置不同**。启动期预检失败 → 进程非零退出（F004 既有行为，不改）；运行期 `restore` 失败 → 进程存活、`state=stopped`、返回 `E_UNAVAILABLE`。控制面的"任何状态下可达"只承诺进程活着以后。
- **权限 / escalation / 凭据边界**：控制面只在容器网络与本机回环可达（compose 端口绑 `127.0.0.1`）；不引入鉴权。Agent 不得调用（CLAUDE.md AI 权限红线）；合法调用方是 F003 编排与人工运维。
- **Windows / POSIX / 版本兼容**：显存探测不依赖 GPU 进程列表（WSL2 下 `nvidia-smi` 不列出进程）；`nvidia-smi` 回退用 `--query-gpu=memory.used --format=csv,noheader,nounits` 解析 MiB 换算字节；不可执行即视为读数不可得。
- **mock 边界**：控制面路由条件注册 + torch 惰性导入，F004 NFR-001 的否证测试保持有效。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f009_lifecycle_contract.py`：TestClient + fake predictor | status 八字段齐备；动作进行中返回 `state=transitional` + `operation` 非空（**变异证明**：把取值域改回二值即判红）；加载失败后仍可达；读数不可得为成功响应且无 `error` 键；探测挂起时仍在服务端 deadline 内返回 |
| `AC-002` | unit | 同上：stop 往返、幂等与失败落点 | `desired` 置位、`_predictor is None`、`empty_cache` 被调用；重复 stop 不报错；stop 后 status/restore 可达（进程未退出）；三个失败注入点分别断言 `E_UNLOAD_FAILED` + `desired`/`model_loaded`/`operation`（**变异证明**：把丢引用后的落点改成回滚 `running` 即判红） |
| `AC-003` | unit | `tests/unit/test_f009_stopped_admission.py` | stop 后连打 `/predict`、`/predict_batch`：`_load_predictor` **零次调用**（以 spy 断言）、来源不为 `kronos`、`model_loaded` 恒 false。**变异证明**：去掉准入分支即判红 |
| `AC-004` | unit | `tests/unit/test_f009_lifecycle_contract.py` | restore 幂等（加载函数只调一次）；加载抛错 → `E_UNAVAILABLE` + `state=stopped` + 进程未退出（断言未抛 SystemExit） |
| `AC-005` | unit | `tests/unit/test_f009_lifecycle_errors.py` | 版本 999 / 头缺失 → `E_UNSUPPORTED_VERSION`；体含 `{"force": true}` → `E_BAD_REQUEST`（**断言两者不相等**）；三者均**恰为单键**信封（`set(payload) == {"error"}`）；成功响应不含 `error`；空体与 `{}` 放行 |
| `AC-006` | unit | 同上：单飞与超时 | 慢动作进行中并发 restore → `E_BUSY` 且原动作不受影响；短超时 → `E_TIMEOUT` 且 `operation` 仍非空；后台完成后 `operation` 转 `null` 且 `state` 与 `desired` 一致；加载中途抛错后显存清理、落回 `stopped` |
| `AC-007` | unit | `tests/unit/test_f009_vram_probe.py` | 三条回退分支逐条命中；探测命令不含 `--query-compute-apps`；`KRONOS_VRAM_PROBE_MODE` 三个合法值逐个生效且单一来源模式不跨源回退；探测超时按读数不可得处理且 status 不超 deadline；五个变量的非法值（0 / 负数 / 非数值 / 枚举外）启动期判红，不回退默认 |
| `AC-008` | unit | `tests/unit/test_f009_lifecycle_logging.py`（caplog） | stop/restore 各一行且含 `operation_id`；超时后的迟到完成补写同 id 的 `result=late_complete`；字段集与 TR-001 逐项一致；不含主机路径与凭据。**变异证明**：删任一必填字段即判红 |
| `AC-009` | integration | `tests/integration/test_f009_lifecycle_deployment.py`（`ALPHAMILL_INTEGRATION=1`） | mock 实例 `/lifecycle/status` 返回 **404**；默认镜像 `import torch` 判红（沿用 F004 否证式断言）；`docker compose config` 断言控制面端口绑 `127.0.0.1` |
| `AC-010` | unit | `tests/unit/test_f003_gpu_slot.py`（客户端判定）+ `tests/unit/test_f003_cli_contract.py`（退出路径控制流） | 客户端 deadline 逐个不同且各自 = 服务端值 + 余量；`state=transitional` fail-closed；**三条退出路径（正常结束 / 取锁失败 / 运行异常）各恰调用一次 restore，触发条件是「发出过 stop」而非「确认 stopped」**（变异证明：改回按 `action=="stopped"` 登记即判红）；"已释放"判定含训练预算条件且 `vram_readable=false` 单独记 reason。**变异证明**：去掉预算判据 / 忽略 `vram_readable` 各自判红 |
| `AC-011` | 真实环境（执行机） | `tests/integration/test_f003_kronos_lifecycle.py` | 控制面语义用例 `--runxfail` 下 0 xfailed；模块级 xfail 已移除；补齐 `E_BUSY`/`E_TIMEOUT`/额外参数用例 |
| `AC-012` | 集成（**无需 GPU 即可验收**） | `tests/integration/test_f009_vram_release.py`（独立载体，不与 F003 的 0-xfailed 门禁同文件） | 断言 `after < before` **且**卸载后整卡可用显存 ≥ 训练预算（`vram_limit_gb`，与单槽取锁同阈值）；以 `xfail(strict=True)` 标注且在无 GPU 环境确为 xfail 而非 XPASS。**解除 xfail 与真实证据归 F010 AC-009**，本 feature 不等它，落地后 XPASS 即红、须显式解除 |

补充纪律：

- 每条新断言须有**变异判红**证明（F004 循环 12、F003 循环 14 既定做法）；
- 开发机上 GPU 相关用例跳过属预期，不算证据也不算失败（SOP §3）；
- AC-012 在 F010 落地前**不得**以 CPU 实例上的通过充当证据（spec NFR-006）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| `desired` 要不要存 | **存**；`state` 仍只派生 | "模型在不在内存里"这项事实不足以表达停机意图（检视 R1-002）。把该存的存、该派生的派生，才既排除第二真相源又让 `stopped` 稳定 | — |
| 停机期间的推理请求怎么答 | 走 F004 既有兜底路径，来源不标 `kronos` | 不改 `/predict*` 对外契约；复用已验收的兜底语义与其测试 | 若将来需要显式 503，须先改架构契约 |
| 超时后是否取消后台工作 | **不取消**，把"进行中"升为一等状态（`operation`） | 强行中断会留下半加载态；无法安全中断就不要假装可以。可观测优于可中断 | 客户端 fail-closed，下一轮重试 |
| 冲突动作排队还是拒绝 | **拒绝**（`E_BUSY`），不排队 | 排队会让相反动作迟到生效，客户端看到的响应与最终状态失去稳定关系（检视 R1-003） | 若重试率高，再提 draining 态到架构 §7.1 |
| `restore` 加载失败后的 `desired` | 回落 `stopped` | 否则停在"期望 running 但加载不上"的过渡态，`state` 落不回稳定态，违反不变量 | `E_UNAVAILABLE` 让调用方知道恢复没成 |
| mock 是否实现控制面 | **不注册路由**（推翻早先决策） | 架构明确 mock 不在契约范围；mock 永远 `model_loaded=false`，与 `running ⇒ model_loaded=true` 不相容（检视 R1-005） | 客户端 404 处置由决策表第三行覆盖 |
| GPU 基座不存在 | 归 F010，本 feature 声明硬前置；显存结论挂先红态 | 控制面语义可在 CPU 上完整交付与验收；把"显存释放"当成已验证才是真风险 | F010 落地后回本 spec 取 AC-012 证据 |
| 过渡态要不要进 wire enum | **进**：`state` 加 `transitional` | 动作一受理就先置 `desired`、后改 `model_loaded`，过渡态是必经窗口；二值取值域下服务端在该窗口内构造不出合法响应，`operation` 补充不了必填字段（R4-001） | 客户端一律 fail-closed；决策表与一致性钉点同步 |
| 迟到 stop 谁来补偿 | **客户端无条件 restore**：发出过 stop 即持有恢复责任 | 只按同步结果登记恢复，60s 超时返回 / 61s 后台完成的那次卸载会永久停机（R4-002）。轮询 `operation` 必须设界，界外的迟到完成兜不住；而 `restore` 幂等，无条件调用的代价是一次空操作 | 客户端 deadline = 服务端 deadline + 5s 余量，保证能收到 `E_TIMEOUT` 而不是 `OSError` |
| stop 失败要不要回滚 | **以"引用是否已丢"为界**：丢引用前回落 `running`，丢引用后保持 `stopped` | 丢引用不可逆，回滚 `running` 等于谎报模型仍在内存；不可逆的一步之后只准前进（R4-004） | 两种情况同码 `E_UNLOAD_FAILED`，靠 `status` 区分落点 |
| AC-012 等不等 F010 | **不等**：本 feature 交付载体与先红态，F010 交付真实证据 | 双边互写 AC 会形成收口环，而本仓没有 stacked branch 流程；先红态本身在无 GPU 环境可验收（R4-003） | F010 spec 同步澄清方向 |
| status 走不走单飞执行器 | **不走**：单独的 deadline + 探测预算 | status 必须在动作进行中可达，进执行器就会被 `E_BUSY`/排队挡住；卡住的 `nvidia-smi` 也不得把它拖过 deadline（R1-008） | 探测超时按读数不可得处理，不新增错误码 |
| 设备侧读数含其他租户 | 接受：这正是夜槽要的判断 | F003 要判的是"整张卡还剩多少能开训"，不是"Kronos 自己占了多少" | 日志同时记前后读数，便于事后区分 |
| 控制面无鉴权 | 网络边界替代鉴权 | 单机自用、调用方同宿主 | 跨机调用前必须先补鉴权 |

## 10. 待确认设计问题

无
