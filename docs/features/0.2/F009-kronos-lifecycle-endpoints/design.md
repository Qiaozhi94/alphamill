---
kind: feature
id: F009
version: "0.2"
related_features: [F003, F004]
topics: [kronos, lifecycle, control-plane, gpu-slot, m2]
doc_kind: design
created: 2026-09-20
updated: 2026-09-20
---

# F009：Kronos 服务生命周期控制面端点 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：`docs/alphamill-architecture.md` §7.1（生命周期契约正文、wire 绑定、观测→处置决策表；本 feature **只实现不改**，改动须先改该节并同步 `tools/check_doc_consistency.py` 的 `offload_decision_table_rows` 期望值）
- **ADR / 上游 Contract**：ADR-0002（Kronos 上游 clone + pin，推理薄壳归本仓 `src/alphamill/kronos_service/`）；ADR-0005（不新增口径载体，门禁裁决不页面化）
- **实现约束**：
  - mock 镜像不得引入 torch（F004 NFR-001 否证测试为硬门）→ 所有 torch / GPU 相关导入惰性化；
  - `KronosRealSignal._lock` 的既有不变式（模型加载至多一次 + 推理互斥）不得被破坏；
  - 超时与探测方式走配置，不写死常数（迁移 `qiaozhi-lab` 只改配置）；
  - 超时判定用 `time.monotonic()` 截止时刻，**不用固定步长累加**——F004 Q003 已经踩过一次（固定步长会把等待拉到 2× 窗口）。

## 1. 技术概要与影响面

在 Kronos 推理薄壳内新增一个**生命周期控制面模块**，持有「模型是否加载」这一派生状态的读写动作，并以三个 FastAPI 路由暴露。状态不单独存储——`state` 由 `KronosRealSignal` 是否持有 predictor 派生（spec §5 不变量）。显存读数单独成一个探测函数，按 `torch.cuda.mem_get_info` → `nvidia-smi` → 不可得三级回退。在飞推理由一个计数器承载，`/predict*` 进出时增减，`stop` 读到非零即 `E_BUSY`。

- 前端：不适用（无 UI，ADR-0005）。
- 后端 / API：`src/alphamill/kronos_service/lifecycle.py`（新增：状态机、错误码、在飞计数、超时执行器）、`src/alphamill/kronos_service/vram.py`（新增：设备侧显存探测与回退）、`server.py`（新增三路由 + 版本协商依赖 + `/predict*` 的在飞计数包装）、`kronos_real.py`（**最小改动**：新增 `unload()`，`status()` 复用既有 `ModelStatus`）。
- 存储 / Migration：不适用（无持久化实体）。
- Runtime / Agent Adapter：`deployment/docker-compose.yml` 的 `kronos-signal-real` 服务——控制面端口只在容器网络与回环可达，不发布到 `0.0.0.0`；新增超时与探测方式的环境变量（`.env.example` 同步）。
- Event / Evidence：结构化日志行（TR-001），落容器日志，不入库、不建新表（ADR-0005 不新增口径载体）。
- 文档 / 配置：`BACKLOG.md`（本行从「规划中」转入活跃表）、`CLAUDE.md` 当前活跃 Feature、`docs/README.md` 活跃索引三处同步（`check_doc_consistency` 的 `active_feature_indexes_aligned` 会双向校验）；`docs/alphamill-integration.md` 补控制面运维段。

## 2. 架构与模块边界

```text
                      ┌──────────────────────────────┐
  F003 gpu_slot  ───►  │ server.py  /lifecycle/*      │
  （夜槽编排，唯一     │  - require_contract_version  │  依赖方向：
    程序调用方）       │  - 三路由，统一错误信封       │  server → lifecycle → kronos_real
                      └──────────┬───────────────────┘              └→ vram
                                 │
                      ┌──────────▼───────────────────┐
                      │ lifecycle.py                 │
                      │  - LifecycleController       │  状态由 kronos_real 派生，
                      │  - 在飞计数 / E_BUSY          │  本模块不存第二份 state
                      │  - 超时执行（monotonic 截止） │
                      └──────┬───────────────┬───────┘
                             │               │
                 ┌───────────▼──┐      ┌─────▼────────┐
                 │ kronos_real  │      │ vram.py      │
                 │  load/unload │      │ 设备侧已用字节 │
                 └──────────────┘      └──────────────┘
```

职责划分：

- **`server.py`** 只做 wire 层：解析 `X-Contract-Version`、调用控制器、把结果或错误码序列化成契约信封。不含状态判断逻辑。
- **`lifecycle.py`** 是控制面唯一真相源的**读写入口**，但它不存 `state`——每次都从 `KronosRealSignal.status().loaded` 派生（derive, don't store）。它持有的自有状态只有一个：在飞推理计数器。
- **`kronos_real.py`** 只增 `unload()`，与既有 `eager_load()` 对称，共用同一把 `_lock`，既有推理路径零改动。
- **`vram.py`** 是纯探测，无状态、可单测，三条回退分支各自可独立触发。
- 依赖方向单向：`server → lifecycle → {kronos_real, vram}`，下层不回调上层。

## 3. 数据模型与 Migration

不适用：本 feature 不新增或修改任何持久化实体、表或 artifact。控制面状态是进程内存态，进程重启后由 F004 既有的启动预检 + eager load 决定初始态（real 模式下为 `running`）。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

| 方法 | 路径 | 请求 | 成功响应 | 默认超时（可配） | 错误码 |
|---|---|---|---|---|---|
| GET | `/lifecycle/status` | `X-Contract-Version: 1` | `{state, contract_version, model_loaded, vram_bytes, device}` | 5s (`KRONOS_LIFECYCLE_STATUS_TIMEOUT_S`) | `E_UNAVAILABLE` / `E_UNSUPPORTED_VERSION` |
| POST | `/lifecycle/stop` | 同上，空体 | `{state: "stopped", vram_bytes}` | 60s (`KRONOS_LIFECYCLE_STOP_TIMEOUT_S`) | `E_BUSY` / `E_TIMEOUT` / `E_UNSUPPORTED_VERSION` |
| POST | `/lifecycle/restore` | 同上，空体 | `{state: "running"}` | 120s (`KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S`) | `E_BUSY` / `E_TIMEOUT` / `E_UNSUPPORTED_VERSION` / `E_UNAVAILABLE` |

- **错误信封**：一律 `{"error": "E_*"}`，**响应体即判据**。契约测试明确「只认错误码信封，不认 HTTP 状态码」——因为把 404 当合法拒绝会让"端点未实现"假性通过。实现上错误响应用 HTTP 200 + 错误信封，避免任何中间件把非 2xx 改写成自己的错误页而丢掉 `error` 字段。
- **版本协商**：FastAPI 依赖 `require_contract_version`——读 `X-Contract-Version`，缺失或 != `SUPPORTED_CONTRACT_VERSION`（`"1"`）即返回 `E_UNSUPPORTED_VERSION`。**缺失不按默认版本放行**（spec FR-004 场景二）。
- **请求体**：`stop` / `restore` 不接受任何参数，防止在契约外偷加开关（如 `force=true` 强停）。
- **`vram_bytes` 语义**：设备侧整卡已用字节（int），无 CUDA 时为 `0`，读数不可得时为 `null` 且该次 `status` 以 `E_UNAVAILABLE` 表达不确定。

### Event / Trace Contract

结构化日志行（TR-001），单行 `logfmt` 风格，便于 `docker logs | grep 'action='`：

```text
action=stop result=ok state_before=running state_after=stopped vram_bytes_before=3221225472 vram_bytes_after=142606336 contract_version=1 elapsed_ms=412
action=stop result=E_BUSY state_before=running state_after=running vram_bytes_before=3221225472 vram_bytes_after=3221225472 contract_version=1 elapsed_ms=1
```

- 幂等键：无（动作本身幂等，日志按时间序追加即可）；
- 查询方式：容器日志按 `action=` 前缀检索（TR-002）；
- 禁止字段：主机路径（模型路径之外）、凭据、数据库连接串（TR-003）——日志行的字段集是白名单，不是黑名单过滤。

## 5. Runtime、Workflow 与并发

**状态派生**：`state = "running" if kronos_real.real_signal.status().loaded else "stopped"`。不设独立状态变量，因此不存在"状态与事实不一致"的类别（spec §5 不变量）。

**在飞计数**：`lifecycle.inflight` 是一个带锁的整数。`/predict` 与 `/predict_batch` 用上下文管理器 `inflight.track()` 包裹推理调用，进入 +1、退出（含异常）-1。`stop` 读到 `> 0` 立即返回 `E_BUSY`——**不等待、不强停**（spec FR-005）。这是个读-判-改的竞态窗口：判定与卸载之间可能进来新请求，因此卸载动作本身仍在 `KronosRealSignal._lock` 内执行，与推理互斥；最坏情况是新请求阻塞到卸载完成后拿到"模型未加载"的兜底路径，而不是拿到半卸载的模型。

**卸载路径**（`kronos_real.unload()`，与 `eager_load()` 对称）：

1. 持 `self._lock`；
2. `self._predictor = None`（丢弃 KronosPredictor 及其持有的 model/tokenizer 引用）；
3. 若 `self._torch is not None`：`self._torch.cuda.empty_cache()`——把 caching allocator 的块还给驱动，否则设备侧读数不会下降；
4. 保留 `self._device` 与 `self._torch` 引用（`restore` 时不必重新探测设备），清空 `self._load_error`。

**恢复路径**：复用既有 `_load_predictor()`（已含"已加载即直接返回"的幂等分支），因此 `restore` 的幂等性天然成立，不需要额外判断。

**超时执行**：`stop` / `restore` 的实际工作（卸载 / 加载）放进一个单线程执行器，主协程以 `time.monotonic() + timeout` 为**截止时刻**等待；超时返回 `E_TIMEOUT`，后台工作不取消（强行中断加载会留下半加载态，违反 NFR-004）——下一次 `status` 会如实反映最终落点。截止时刻必须用 monotonic，不得用固定步长累加（F004 Q003 的原样教训）。

**并发与幂等汇总**：

| 动作 | 并发保护 | 幂等实现 |
|---|---|---|
| `status` | 无锁只读 | 天然幂等 |
| `stop` | 在飞计数判定 + `_lock` 内卸载 | `_predictor is None` 时直接返回 `stopped` |
| `restore` | `_lock` 内加载 | `_load_predictor()` 既有早返回分支 |

**不可回滚副作用边界**：`stop` 会中断白天的实时信号能力（dry-run 退回读 `signal_cache` 存量信号，架构 §7.1 时段表已如此设计），这是预期的、可由 `restore` 复原的副作用；除此之外本 feature 不产生任何不可逆副作用。

## 6. UI 与可观测性

- 页面：不适用（无 UI；按 ADR-0005，运营状态不进研究控制台，门禁裁决不页面化）。
- 日志：TR-001 的结构化行是唯一新增观测面，落容器日志，不新增指标口径载体、不建 Grafana 面板（ADR-0005：不新增口径载体）。
- `/health` 保持 F004 原样不动——它报的是模型与数据库健康，`state` 的权威读法是 `/lifecycle/status`。两者字段有重叠（`model_loaded`、`device`）但语义一致，不构成第二真相源：两者都从 `real_signal.status()` 派生。
- 运维可见性：夜槽事后复盘用 `docker logs kronos-signal-real | grep 'action='` 即可还原当晚是否真的卸载、显存降了多少、失败在哪一步。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：

  | 条件 | 返回 |
  |---|---|
  | 缺 `X-Contract-Version` 或值不匹配 | `E_UNSUPPORTED_VERSION` |
  | 在飞推理计数 > 0（仅 `stop`） | `E_BUSY` |
  | 动作未在可配超时内完成 | `E_TIMEOUT` |
  | 模型资产缺失 / 加载抛错（`restore`） | `E_UNAVAILABLE` |
  | 显存读数两级探测皆不可得（`status`） | `vram_bytes: null` + `E_UNAVAILABLE` |

- **重启与恢复**：进程重启后由 F004 既有 lifespan（`real_mode_startup()` 预检 + eager load）决定初始态；本 feature 不持久化 `stopped`，即**重启即回到 `running`**。这是有意的：夜槽编排每次训练窗口开始时都会重新调 `stop`，把"停机意图"持久化反而会让人工重启后白天拿不到信号。
- **权限 / escalation / 凭据边界**：控制面能改变生产状态，按 NFR-003 只在容器网络与本机回环可达（compose 端口映射绑 `127.0.0.1`，不发布 `0.0.0.0`）；不引入鉴权。按 CLAUDE.md 的 AI 权限红线，Agent 不得调用这些端点——合法调用方是 F003 编排与人工运维。
- **Windows / POSIX / 版本兼容**：显存探测在 WSL2 下**不得依赖 GPU 进程列表**（`nvidia-smi` 在 WSL2 不列出 GPU 进程，架构 §7.1 已记录）；`nvidia-smi` 回退路径用 `--query-gpu=memory.used --format=csv,noheader,nounits` 解析整数 MiB 并换算字节。无 `nvidia-smi` 可执行文件时视为读数不可得，不抛栈到响应里。
- **mock 边界**：`vram.py` 与卸载路径中的 torch 导入一律函数内惰性化；mock 实例走 `device=cpu` 分支，全程不 import torch，F004 NFR-001 的否证测试（默认镜像 `import torch` 判红）保持有效。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f009_lifecycle_contract.py`：TestClient + fake predictor | status 五字段齐备；卸载后端点仍可达且 `state=stopped`/`model_loaded=false` |
| `AC-002` | unit | 同上：stop 往返与幂等 | 卸载后 `_predictor is None`、`empty_cache` 被调用；重复 stop 返回 `stopped` 不报错；stop 后 status/restore 仍可达（进程未退出） |
| `AC-003` | unit | 同上：restore 往返、加载失败分支 | 重复 restore 不重复加载（加载函数只被调一次）；加载抛错时返回 `E_UNAVAILABLE` 且 status 仍报 `stopped` |
| `AC-004` | unit | 同上：版本协商 | `X-Contract-Version: 999` 与**头缺失**两种输入都返回 `{"error": "E_UNSUPPORTED_VERSION"}`；成功响应不含 `error` 键 |
| `AC-005` | unit | `tests/unit/test_f009_lifecycle_errors.py` | 在飞计数 > 0 时 stop 返回 `E_BUSY` 且 predictor 仍在；超时分支返回 `E_TIMEOUT`（注入慢加载 + 短超时）；显存不可得时 `vram_bytes is None` + `E_UNAVAILABLE`，**断言不是 0** |
| `AC-006` | unit | `tests/unit/test_f009_vram_probe.py` | 三条回退分支逐条命中：`mem_get_info` 可用 / 抛错后走 `nvidia-smi` / 两者皆不可得返回 `None`；断言探测命令不含进程列表查询（不出现 `--query-compute-apps`） |
| `AC-007` | integration | `tests/integration/test_f009_lifecycle_mock.py`（容器，`ALPHAMILL_INTEGRATION=1`） | mock 实例三端点照常响应且 `device=cpu`/`vram_bytes=0`；stop/restore 为 no-op；默认镜像 `import torch` 判红（沿用 F004 `test_f004_real_profile.py` 的否证式断言） |
| `AC-008` | unit | `tests/unit/test_f009_lifecycle_logging.py`（caplog） | stop/restore 各写一行，字段集与 TR-001 逐项一致；变异证明：删掉 `vram_bytes_after` 字段即判红；断言行内不含主机路径与凭据模式 |
| `AC-009` | integration | `tests/integration/test_f009_lifecycle_mock.py` | 三个超时均可由环境变量覆盖（改环境变量后生效值随之变，反向断言默认值不是硬编码）；`docker compose config` 断言控制面端口绑 `127.0.0.1` 而非 `0.0.0.0` |
| `AC-010` | 真实环境（执行机） | `tests/integration/test_f003_kronos_lifecycle.py` + 人工取证 | 执行机上 `--runxfail` 0 xfailed；stop 前后设备侧显存读数对照（真实下降）；证据记录 hostname / GPU 型号 / 前后读数 |

补充纪律：

- 每条新断言须有**变异判红**证明（改坏实现后测试必须红），F004 检视循环 12 的既定做法；
- 开发机（`qiaozhi-gp`，无 NVIDIA）上 GPU 相关用例跳过属预期，不算证据也不算失败（SOP §3）；AC-010 一律在执行机取。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 状态存哪 | **不存**，每次从 `real_signal.status().loaded` 派生 | derive, don't store；避免"状态变量说 running、模型实际没了"这类第二真相源缺陷 | — |
| 错误响应的 HTTP 状态码 | 错误也走 **HTTP 200 + `{"error": "E_*"}`** 信封 | 契约测试只认信封；非 2xx 可能被中间件/代理改写成自己的错误页而丢掉 `error` 字段，届时客户端会把它误判成"端点不存在" | 若将来接入网关需要状态码语义，改契约（架构 §7.1）而非改实现 |
| 超时后是否取消后台工作 | **不取消**，只返回 `E_TIMEOUT` | 强行中断加载/卸载会留下半加载态，违反 NFR-004 的"必须收敛到两个状态之一" | 下一次 `status` 如实反映最终落点；客户端按决策表第四行 fail-closed |
| `stop` 后重启进程回到 running | **有意为之**，不持久化停机意图 | 夜槽每轮都会重新 `stop`；持久化会让人工重启后白天拿不到信号，故障面更差 | — |
| 在飞判定与卸载之间的竞态 | 卸载仍在 `_lock` 内执行，与推理互斥 | 最坏情况是新请求阻塞后走兜底路径，而不是拿到半卸载的模型 | 若实测竞态可观测，再引入 draining 态（须先改架构 §7.1） |
| 设备侧读数含其他租户 | **接受**：这正是夜槽要的判断 | F003 要判的是"整张卡还剩多少能开训"，而不是"Kronos 自己占了多少" | 日志同时记前后两个读数，便于事后区分是谁没让出来 |
| `nvidia-smi` 回退在 WSL2 的可靠性 | 只用 `--query-gpu=memory.used`，**绝不查进程列表** | WSL2 下 `nvidia-smi` 不列出 GPU 进程（架构 §7.1 已记录），查进程会得到空结果并被误读成"卡是空的" | 单测断言探测命令里不出现 `--query-compute-apps` |
| 控制面无鉴权 | 网络边界替代鉴权：绑回环 + 容器网络 | 单机自用、调用方同宿主；引入凭据管理成本不抵收益 | 执行机分离或跨机调用前必须先补鉴权 |

## 10. 待确认设计问题

无
