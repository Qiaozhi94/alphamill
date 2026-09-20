---
kind: feature
id: F009
version: "0.2"
status: ready-for-development
gate_version: 1
related_features: [F003, F004, F010]
topics: [kronos, lifecycle, control-plane, gpu-slot, m2]
doc_kind: spec
created: 2026-09-20
updated: 2026-09-20
---

# F009：Kronos 服务生命周期控制面端点

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR6（运行监控）间接消费；本 feature 不新增 PRD 功能面，是架构契约的服务端落地
- **架构来源**：`docs/alphamill-architecture.md` §7.1「Kronos 服务生命周期契约」——动作表、期望态与派生态、单飞与进行中语义、wire 绑定与错误信封、显存确认判据、客户端分动作超时、观测→处置决策表、GPU 基座前置条
- **系统设计 / Research / Contract 来源**：`docs/alphamill-integration.md`（Kronos 集成操作细节）；契约测试 `tests/integration/test_f003_kronos_lifecycle.py`（客户端可见行为的锁定物）
- **上游决策**：ADR-0002（Kronos 上游 clone + pin，推理薄壳归本仓）、ADR-0005（呈现与观测架构：不新增口径载体）
- **基座来源**：F004（`src/alphamill/kronos_service/` 推理薄壳、`kronos-signal` / `kronos-signal-real` 两个 compose 服务、启动预检与 eager load；**均为 CPU 实例**）；F003（客户端 `gpu_slot` 与观测→处置决策表的消费方）
- **硬前置**：GPU 推理基座（CUDA 镜像、compose 设备预留、`device`/healthcheck 断言改写、F004 回归契约迁移）归独立 Feature（BACKLOG「Kronos GPU 推理基座」，编号 F010 预留）。**仓内当前没有任何 GPU Kronos 实例**，故本 feature 的"真实显存下降"类结论在 F010 落地前一律不成立
- **功能类型**：backend / runtime
- **规格模式**：full
- **变更类型**：ADDED
- **一句话意图**：把架构 §7.1 已定稿的版本化生命周期控制面（`status` / `stop` / `restore`）实现到 Kronos 推理薄壳，让期望态可被外部置位、推理端点在停机期间不把显存吃回去、动作之间单飞可仲裁——使夜槽编排具备一个语义上可依赖的控制面；显存的真实释放取证随 GPU 基座（F010）落地后补。

## 1. 问题、目标与非目标

### 问题

架构 §7.1 的生命周期契约已定稿，消费侧也齐了：F003 的客户端（`gpu_slot` / `kronos_offload`，tasks T025）按观测→处置决策表逐行实现并有单测，契约测试 `tests/integration/test_f003_kronos_lifecycle.py` 以 `xfail(strict=True)` 立着先红态。唯独服务端一行没有：`src/alphamill/kronos_service/server.py` 只暴露 `/health`、`/ohlcv`、`/predict`、`/predict_batch`。

后果有两层。**直接**：F003 的 T033 要求该契约测试以 0 xfailed 通过，端点不存在则无法完成。**每晚**：夜槽编排只能走决策表第三行的 404 回落探测，靠设备侧读数与阈值猜测，读数达到阈值或不可得即 fail-closed 留在单槽队列。

但"把三个端点挂上去"并不足以解决问题，文档检视（循环 19 round 1）已经指出三处机制缺口：

1. **`stopped` 不稳定**：`KronosRealSignal.generate_signal()` 每次进入都会在同一把锁内调用 `_load_predictor()`。若 `state` 只从"模型在不在内存里"派生，那么 `stop` 成功之后任何一次 `/predict` 都会自行把模型加载回来、把显存吃回去，完全绕过 `restore`——卸载等于没卸。
2. **超时不是终态**：动作超时后若后台继续执行且无仲裁，客户端看到的错误与服务端最终状态之间没有稳定关系，相反动作还会迟到生效。
3. **基座不存在**：`kronos-signal-real` 是 CPU 实例（`KRONOS_DEVICE: cpu`、CPU wheel、healthcheck 以 `device=cpu` 为通过条件），且这些事实被 F004 的变异门锁死。没有 GPU 实例，"显存真实下降"无从取证。

### 目标

- `kronos-signal-real` 暴露 `GET /lifecycle/status`、`POST /lifecycle/stop`、`POST /lifecycle/restore`，行为与架构 §7.1 动作表逐格一致；
- **期望态可被外部置位且稳定**：`stop` 之后推理端点不隐式重载模型，`stopped` 能一直维持到显式 `restore`；
- **动作可仲裁**：同一时刻至多一个生命周期动作在执行，冲突动作立即 `E_BUSY`；`E_TIMEOUT` 表达"仍在进行"，最终落点经 `status.operation` 可观测；
- 契约版本协商与错误信封成立：`X-Contract-Version` 不匹配或缺失一律以恰为单键的 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝；
- `tests/integration/test_f003_kronos_lifecycle.py` 转正——移除模块级 `xfail(strict=True)`、补错误路径用例，在执行机以 0 xfailed 通过；显存判据另落独立载体 `test_f009_vram_release.py`，不占用该文件的 0-xfailed 门禁；
- F003 客户端的分动作超时与 `restore` 所有权在本 feature 内一并钉死（跨 Feature 交付边显式化）。

### 非目标

- 本 feature 不做 GPU 推理基座——CUDA 镜像、compose 设备预留、`device`/healthcheck 断言改写与 F004 回归契约迁移归 **F010**；本 feature 声明它为硬前置并在文档中如实标注哪些结论因此暂不成立；
- 本 feature 不做挖掘侧编排、单槽 FIFO 与取锁判定——那是 F003（tasks T025 / T033），本 feature 只提供被调用的服务端与其客户端契约约束；
- 本 feature 不改 Kronos 模型或推理质量；`/predict*` 的**对外契约不变**，只增加"停机期间不重载"的准入语义（走 F004 既有兜底路径）；
- 本 feature 不修改架构 §7.1 的契约正文——契约归该节所有，本次所需的契约修订已先行落在该节（见 §0 架构来源）；
- 本 feature 不为 mock 实例（`kronos-signal`）定义生命周期语义——架构 §7.1 明确 mock 不在契约范围；
- 本 feature 不做通用服务控制面框架、不引入鉴权体系、不承诺 `restore` 的模型预热 SLA。

## 2. 用户场景

### US-001：夜槽编排能把 Kronos 置为停机态并且它待得住（Priority: P1）

作为挖掘编排（F003 `gpu_slot`），我希望调用一次 `stop` 之后 Kronos 一直处于停机态、不会被白天的推理请求悄悄唤醒，以便我取锁训练期间显存预算是可依赖的。

**为什么是这个优先级**：这是本 feature 相对"把端点挂上去"的真正增量。停机态不稳定时，控制面即便三个端点全绿也毫无价值——这正是文档检视 R1-002 的判定。

**独立测试**：在 `kronos-signal-real` 上 `stop` → 连打若干 `/predict` → `status`：断言 `state` 始终 `stopped`、`model_loaded=false`，且这些 `/predict` 返回的信号来源不是 `kronos`。

**验收场景**：

1. Given 实例 `state=running`，when 调用 `POST /lifecycle/stop`，then 期望态置为 `stopped`、模型被卸载，响应为 `{state: stopped, vram_bytes}`。
2. Given 实例已 `stopped`，when 连续调用 `/predict`，then 每次都走兜底信号路径、来源不标 `kronos`，且 `status` 仍报 `state=stopped`、`model_loaded=false`。
3. Given 实例已 `stopped`，when 再次调用 `stop`，then 返回 `state=stopped` 且不报错、不产生副作用。

### US-002：白天恢复常驻推理，且恢复责任有明确 owner（Priority: P1）

作为挖掘编排，我希望训练窗口结束（含异常退出）时 Kronos 被恢复为常驻，以便白天 dry-run 能继续拿到实时信号，而不需要人工重启容器。

**为什么是这个优先级**：与 US-001 同批。只停不启会把白天的信号面打掉，而"谁负责恢复"若不在契约里钉死，服务端交付完了旅程仍然没有 owner（文档检视 R1-006）。

**独立测试**：在已 `stopped` 的实例上调 `restore`，断言返回 `state=running`、重复调用仍 `running`，随后 `/predict` 恢复产出 `kronos` 来源信号；客户端侧断言三条退出路径（正常结束 / 取锁失败 / 运行异常）都调用了 `restore`。

**验收场景**：

1. Given 实例处于 `stopped`，when 调用 `POST /lifecycle/restore`，then 模型重新加载并返回 `state=running`。
2. Given 实例已是 `running`，when 再次调用 `restore`，then 返回 `state=running` 且不重复加载模型。
3. Given `restore` 因模型资产缺失而无法加载，when 调用返回，then 以 `{"error": "E_UNAVAILABLE"}` 拒绝，`status` 如实报 `state=stopped`、`model_loaded=false`，不伪报 `running`；**进程不退出**（与 F004 的启动期预检失败即退出是两件事）。

### US-003：动作之间可仲裁，超时不产生不可解释的迟到副作用（Priority: P2）

作为客户端实现者，我希望任一时刻至多一个生命周期动作在执行、冲突动作被立即拒绝、超时有明确的"仍在进行"语义与可观测的最终落点，以便我能把服务端状态和我看到的响应对应起来。

**为什么是这个优先级**：它依赖 US-001/US-002 的端点存在，但独立于显存语义——可以完全用单元测试锁死，且不需要 GPU。

**独立测试**：注入慢卸载，在动作进行中并发调用 `restore`，断言立即 `E_BUSY`；把超时压到极短，断言返回 `E_TIMEOUT` 且随后 `status.operation` 从非空转为 `null`、最终落在两个稳定态之一。

**验收场景**：

1. Given 一个生命周期动作正在执行，when 并发到达任一生命周期动作，then 立即返回 `{"error": "E_BUSY"}`，不排队、不叠加。
2. Given 动作未在其可配超时内完成，when 调用返回，then 返回 `{"error": "E_TIMEOUT"}`，服务端**不中断**该动作，`status.operation` 仍非空。
3. Given 超时返回后动作最终完成，when 查询 `status`，then `operation=null` 且 `state` 落在 `running`/`stopped` 之一，与 `desired` 一致。
4. Given 加载中途抛错，when 查询 `status`，then 已分配显存已清理、`state=stopped`、`model_loaded=false`，不存在半加载态。

## 3. 范围与边界

### 范围内

- `src/alphamill/kronos_service/` 内的生命周期控制面：三个端点、契约版本协商、单键错误信封、期望态与准入、单飞仲裁与进行中语义、超时执行；
- `KronosRealSignal` 的期望态与卸载/恢复路径（`unload()`、`_predictor` 记忆化的反向操作、`torch.cuda.empty_cache()`、**`desired=stopped` 期间禁止隐式加载**）；
- 推理端点在停机期间的准入：走 F004 既有兜底路径且不标 `source=kronos`（F004 C002 同一纪律）；
- 设备侧显存探测与其**可配置契约**（`KRONOS_VRAM_PROBE_MODE` 等变量名、值域、默认值、非法值策略，见 FR-007）；读数不可得以 `vram_readable=false` + `vram_bytes=null` 表达；
- **F004 已验收端口契约的迁移**：把 host 绑定从 `8002:8001` 升级为 `127.0.0.1:8002:8001`，同步改写 F004 spec/design 的端口契约文字、`tests/unit/test_f004_compose_profile_contract.py` 的精确断言与变异表（保留「host 8002 不顶替 mock 8001」「container 8001」的原意）——本 feature 自己要过统一门禁，这笔账不能留给 F010；
- 超时与阈值的可配化（不写死常数，迁移执行机只改配置）；
- `tests/integration/test_f003_kronos_lifecycle.py` 的转正：移除模块级 `xfail(strict=True)`、补错误路径用例；显存判据落独立载体 `tests/integration/test_f009_vram_release.py`；
- **跨 Feature 交付边**：F003 客户端的分动作超时（5s/60s/120s）与 `restore` 所有权（三条退出路径均须恢复）在本 feature 内钉死并验收；
- 在 CPU 实例上可完成的部署与契约取证。

### 范围外

- GPU 推理基座（CUDA 镜像、compose 设备预留、`device`/healthcheck 断言改写、F004 回归契约与变异门迁移）→ **F010**，本 feature 的硬前置；
- 真实显存下降的取证与 **AC-012** 证据的采集、先红态的解除 → **归 F010（其 AC-009/T011）**；本 feature 只交付判据载体与先红态本身，不把 F010 的完成作为自己的完成条件；
- 挖掘侧编排、单槽 FIFO、取锁判定与 `kronos_offload` 运行记录字段 → F003（tasks T025 / T033）；
- 架构 §7.1 契约正文的修改 → 归该节所有（本次所需修订已先行落地）；
- mock 实例（`kronos-signal`）的生命周期语义 → 契约明确不在范围：**mock 不注册 `/lifecycle/*` 路由**，客户端对 mock 的处置由决策表既有行覆盖；
- 审计事件入库与运营写路径（FR7.4）→ F006；本 feature 只写结构化日志行；
- 鉴权、限流、TLS → 见 NFR-003 的网络边界方案。

### 边界场景

- `stop` 之后客户端还要调 `status` 与 `restore`：因此 `stop` **只卸载模型、不终止进程**——进程退出会让控制面自身不可达，客户端只能观测到"连接拒绝"，落进决策表第五行 fail-closed，等于把成功的卸载误报成未知状态。
- `desired=stopped` 期间到达的推理请求：**绝不隐式重载**。走兜底信号路径并如实标注非 `kronos` 来源；否则 `stop` 的显存释放会被下一个请求撤销。
- 生命周期动作进行中到达另一个生命周期动作：立即 `E_BUSY`，不排队——排队会让"相反动作迟到生效"变成常态。
- 动作超时：返回 `E_TIMEOUT` 但**不中断**后台动作；客户端据此 fail-closed，并以 `status.operation=null` 作为最终落点判据。
- 加载中途抛错：清理已分配显存后落回 `stopped`，不留半加载态；`restore` 失败不使进程退出（与 F004 启动期预检失败即退出区分）。
- 设备侧显存读数不可得：`status` 仍是**成功响应**，以 `vram_readable=false` + `vram_bytes=null` 如实表达，不借用错误码；编排按"读数不可得"fail-closed 处置。
- 实例运行在无 CUDA 的机器上（当前的 `kronos-signal-real` 即是）：`device` 如实报 `cpu`、`vram_bytes` 为 `0`、`vram_readable=true`；控制面语义完整可测，但**不得据此声称显存释放能力已验证**。
- mock 实例：不注册控制面路由，`/lifecycle/*` 返回 404，客户端命中决策表第三行的回落探测。

## 4. 需求

### 功能需求

### Requirement: 生命周期状态查询（`FR-001`）

系统应当提供 `GET /lifecycle/status`，返回 `{state, desired, contract_version, model_loaded, vram_bytes, vram_readable, device, operation}`；该端点为只读、天然幂等。`state` 应当是 `(desired, model_loaded)` 的函数，取值域为 `running | stopped | transitional`——动作执行窗口内 `desired` 已改而 `model_loaded` 未改，必然产生 `transitional`，此时 `operation` 非空；`operation` 为 `null` 或 `{id, action, started_at}`。当实例处于任何状态（含模型加载失败、动作进行中）时该端点都应当可达。

该端点的 5s 默认超时是**服务端处理 deadline**（可配）：显存探测只能在其剩余预算内执行，探测超时按读数不可得返回成功响应，不得把 status 拖过 deadline。

#### Scenario: 常驻推理中查询

- GIVEN 实例模型已加载、无动作进行中
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回 `state=running`、`desired=running`、`model_loaded=true`、`operation=null`

#### Scenario: 动作执行窗口内查询

- GIVEN 一个 `stop` 或 `restore` 正在执行（`desired` 已置位、`model_loaded` 尚未跟上）
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回 `state=transitional`、`operation` 非空，且八字段齐备（不得返回未入取值域的值，也不得省略 `state`）

#### Scenario: 探测卡住不拖垮 status

- GIVEN 显存探测子进程挂起
- WHEN 调用 `GET /lifecycle/status`
- THEN 在服务端 deadline 内返回成功响应，`vram_readable=false`、`vram_bytes=null`

#### Scenario: 读数不可得仍是成功响应

- GIVEN 设备侧显存读数两级探测皆不可得
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回成功响应且 `vram_readable=false`、`vram_bytes=null`，响应中不含 `error` 键

### Requirement: 置停机态并释放显存（`FR-002`）

系统应当提供 `POST /lifecycle/stop`，把期望态置为 `stopped`、卸载已加载的模型、释放 GPU 缓存，并返回释放后的 `vram_bytes` 与 `state=stopped`；重复调用应当返回 `state=stopped` 而不报错；默认超时 60s（服务端动作 deadline，可配）。停止动作不得终止服务进程。

卸载失败应当以 `{"error": "E_UNLOAD_FAILED"}` 拒绝，且返回前状态已收敛：卸载**尚未开始**即失败时 `desired` 回落 `running`（原状不变）；模型引用**已丢弃**之后失败（含 `empty_cache()` 抛错）时不回滚，保持 `desired=stopped` 且 `model_loaded=false`。任一情况下 `operation` 都应当已清空，不得停在过渡态。

#### Scenario: 首次停止

- GIVEN 实例 `state=running` 且无动作进行中
- WHEN 调用 `POST /lifecycle/stop`
- THEN 期望态变为 `stopped`、模型被卸载、GPU 缓存被释放，返回 `state=stopped` 与 `vram_bytes`

#### Scenario: 停止不杀进程

- GIVEN 已成功执行 `stop`
- WHEN 随后调用 `status` 或 `restore`
- THEN 两者均可达（进程存活，仅模型被卸载）

#### Scenario: 卸载尚未开始就失败

- GIVEN `stop` 在丢弃模型引用之前抛错
- WHEN 调用返回
- THEN 返回 `{"error": "E_UNLOAD_FAILED"}`，`status` 报 `state=running`、`desired=running`、`operation=null`

#### Scenario: 丢引用之后失败不假装回滚

- GIVEN `stop` 已把 `_predictor` 置空，随后 `empty_cache()` 抛错
- WHEN 调用返回
- THEN 返回 `{"error": "E_UNLOAD_FAILED"}`，`status` 报 `state=stopped`、`model_loaded=false`、`operation=null`，`vram_bytes` 如实反映显存可能未回收

### Requirement: 停机期间的推理准入（`FR-003`）

在 `desired=stopped` 期间，系统应当拒绝隐式加载模型：推理端点应当走既有兜底信号路径，并如实标注非 `kronos` 来源，且不改变 `state` 与 `model_loaded`。

#### Scenario: 停机期间的推理请求不唤醒模型

- GIVEN 实例 `state=stopped`
- WHEN 连续调用 `/predict` 与 `/predict_batch`
- THEN 每次都返回兜底信号且来源不是 `kronos`，`status` 始终报 `state=stopped`、`model_loaded=false`

### Requirement: 恢复常驻推理（`FR-004`）

系统应当提供 `POST /lifecycle/restore`，把期望态置为 `running`、重新加载模型并返回 `state=running`；重复调用应当返回 `state=running` 且不重复加载；默认超时 120s（可配）。加载失败应当以 `E_UNAVAILABLE` 拒绝且不终止进程。

#### Scenario: 从停止态恢复

- GIVEN 实例 `state=stopped`
- WHEN 调用 `POST /lifecycle/restore`
- THEN 模型重新加载，返回 `state=running`，随后 `/predict` 恢复产出 `kronos` 来源信号

#### Scenario: 恢复失败不得伪报也不得退出

- GIVEN 模型资产缺失或加载抛错
- WHEN 调用 `POST /lifecycle/restore`
- THEN 返回 `{"error": "E_UNAVAILABLE"}`，`status` 如实报 `state=stopped`、`model_loaded=false`，进程存活

### Requirement: 契约版本协商与单键错误信封（`FR-005`）

系统应当要求所有生命周期请求携带 `X-Contract-Version` 头（当前 `1`）；版本不匹配或头缺失时应当以 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝。错误响应应当**恰为该单键对象**，不携带其他字段；成功响应不得含 `error` 键。`stop` / `restore` 的请求体应当为空或空 JSON 对象，携带任何额外参数应当以 `{"error": "E_BAD_REQUEST"}` 拒绝。

#### Scenario: 版本不匹配或头缺失

- GIVEN 请求头 `X-Contract-Version: 999`，或请求未携带该头
- WHEN 调用任一生命周期端点
- THEN 响应体恰为 `{"error": "E_UNSUPPORTED_VERSION"}`

#### Scenario: 额外参数被拒绝

- GIVEN `POST /lifecycle/stop` 携带请求体 `{"force": true}`
- WHEN 服务端处理该请求
- THEN 返回 `{"error": "E_BAD_REQUEST"}` 且不执行任何停止动作（**不得**复用 `E_UNSUPPORTED_VERSION`）

### Requirement: 单飞仲裁与进行中语义（`FR-006`）

系统应当保证同一时刻至多一个生命周期动作在执行。如果已有动作进行中，任一生命周期动作应当立即返回 `{"error": "E_BUSY"}`，不排队、不叠加。如果动作未在其可配超时内完成，系统应当返回 `{"error": "E_TIMEOUT"}` 且**不中断**后台动作；`status.operation` 应当在动作真正结束后转为 `null`。如果动作中途抛错，系统应当清理已分配显存并落回两个稳定态之一。

#### Scenario: 冲突动作立即拒绝

- GIVEN 一个 `stop` 正在执行
- WHEN 并发到达 `restore`
- THEN 立即返回 `{"error": "E_BUSY"}`，`stop` 不受影响

#### Scenario: 超时不是失败终态

- GIVEN 动作耗时超过其可配超时
- WHEN 调用返回 `E_TIMEOUT`
- THEN `status.operation` 仍非空；动作完成后 `operation` 转为 `null` 且 `state` 与 `desired` 一致

### Requirement: 显存探测与可配置契约（`FR-007`）

系统应当按 `torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used` 顺序探测设备侧已用显存，不依赖 GPU 进程列表。探测方式与三个动作的超时应当由下列具名环境变量承载，每个变量都有明确值域与默认值，非法值应当在启动期判红而不是静默回退：

| 变量 | 值域 | 默认 | 含义 |
|---|---|---|---|
| `KRONOS_VRAM_PROBE_MODE` | `auto` / `torch` / `nvidia_smi` | `auto` | `auto`=按上述顺序回退；`torch`/`nvidia_smi`=只用该单一来源，该来源失败即"读数不可得"，不再回退 |
| `KRONOS_VRAM_PROBE_TIMEOUT_S` | 正数，且 ≤ status deadline | `2` | `nvidia-smi` 子进程超时；超时按读数不可得处理 |
| `KRONOS_LIFECYCLE_STATUS_TIMEOUT_S` | 正数 | `5` | **服务端** status 处理 deadline（非客户端 socket 超时） |
| `KRONOS_LIFECYCLE_STOP_TIMEOUT_S` | 正数 | `60` | **服务端** stop 动作 deadline |
| `KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S` | 正数 | `120` | **服务端** restore 动作 deadline |

#### Scenario: 非法配置启动期判红

- GIVEN `KRONOS_LIFECYCLE_STOP_TIMEOUT_S` 被设为非正数或非数值，或 `KRONOS_VRAM_PROBE_MODE` 被设为枚举外的值
- WHEN 服务启动
- THEN 启动失败并指出该变量，不静默回退到默认值

#### Scenario: 单一来源模式不回退

- GIVEN `KRONOS_VRAM_PROBE_MODE=torch` 且 `torch.cuda.mem_get_info` 不可用
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回 `vram_readable=false`、`vram_bytes=null`，**不**回退到 `nvidia-smi`

### Requirement: 契约测试转正与显存判据（`FR-008`）

系统落地后，`tests/integration/test_f003_kronos_lifecycle.py` 应当移除模块级 `xfail(strict=True)`，并补齐 `E_BUSY` / `E_TIMEOUT` / 额外参数拒绝的用例。**显存释放的判据应当是读数真实下降，且卸载后整卡可用显存达到训练预算**（与单槽取锁同一阈值 `vram_limit_gb`），而非 `vram_bytes` 是合法整数；该断言落在独立载体 `tests/integration/test_f009_vram_release.py`，以 `xfail(strict=True)` 标注先红态。**本 feature 的交付物是"载体与判据正确落盘且处于先红态"，不是显存真实下降本身**——解除 xfail 并取真实证据是 F010 的 AC-009/T011，两个 feature 不得互相把对方的完成作为自己的完成条件。

#### Scenario: 控制面语义用例转正

- GIVEN 端点已部署且 `KRONOS_CONTROL_URL` 指向 `kronos-signal-real`
- WHEN 以 `--runxfail` 运行 `tests/integration/test_f003_kronos_lifecycle.py`
- THEN 该文件的用例全部通过、0 xfailed（显存判据不在此文件内）

#### Scenario: 先红态本身可被验收

- GIVEN 尚无 GPU 实例（F010 未落地）
- WHEN 运行 `tests/integration/test_f009_vram_release.py`（不加 `--runxfail`）
- THEN 显存用例报 xfail 而非 XPASS，且判据文本是"下降且卸载后可用显存达到训练预算"

### Requirement: 客户端交付边（`FR-009`）

F003 客户端应当按动作分别设置 socket 超时，不得共用单一超时；每个动作的客户端 deadline 应当**严格大于**同一动作的服务端 deadline（缺省为服务端值 + 5s 余量，可配），否则客户端先超时抛 `OSError`，收不到服务端规范的 `E_TIMEOUT` 信封。

客户端应当在正常结束、取锁失败与运行异常三条退出路径上都执行 `restore`；触发条件是**本轮是否发出过 `stop`**，而不是"是否同步确认了 stopped"——`E_TIMEOUT`、其他错误与连接中断之后动作仍可能迟到完成，只按同步结果登记恢复责任会让那次卸载永久停机。`restore` 幂等，未真正停机时调用无副作用。

客户端见到 `state=transitional` 应当 fail-closed（既不取锁也不视为已停机），与架构 §7.1 决策表同行。

客户端对"已释放"的判定应当与架构 §7.1 显存确认条**逐字同一**：读数真实下降，且卸载后整卡可用显存达到训练预算；该预算应当与单槽取锁同源（`vram_limit_gb`），不新增第二份配置，未声明时不得猜测缺省值。`vram_readable=false`（读数缺失）应当与"确实没释放"分别记 reason——两者同为 fail-closed，但事后归因完全不同。

#### Scenario: 分动作超时

- GIVEN 一次 `stop` 调用
- WHEN 客户端发起请求
- THEN 使用 `stop` 的客户端 deadline（默认 60s + 5s 余量 = 65s），而不是 `status` 的量级；三个动作的值互不相同且各自大于对应服务端 deadline

#### Scenario: 超时后的迟到完成仍被恢复兜住

- GIVEN `stop` 返回 `E_TIMEOUT`（或请求连接中断），本轮夜槽随后 fail-closed
- WHEN 编排离开训练窗口
- THEN 仍调用一次 `restore`——因为本轮发出过 `stop`，恢复责任已成立

#### Scenario: 过渡态不取锁

- GIVEN `status` 返回 `state=transitional`
- WHEN 客户端判定能否取锁
- THEN fail-closed 留在单槽队列，不把它当作已停机

#### Scenario: 降了但腾不出训练预算

- GIVEN `stop` 返回 `state=stopped` 且确认读数确实下降
- WHEN 卸载后整卡可用显存仍达不到训练预算
- THEN 客户端 fail-closed 不取锁，且 reason 与"读数缺失"区分

#### Scenario: 读数缺失单独记账

- GIVEN 确认用的 `status` 返回 `vram_readable=false`
- WHEN 客户端判定是否已释放
- THEN fail-closed，并以"读数缺失"而非"未释放"记 reason

### 数据 / 实体需求

不适用：本 feature 不创建或修改任何持久化实体。期望态、`operation` 与派生 `state` 均为进程内存态，由 §5 的不变量约束；运行记录字段 `kronos_offload` 由 F003 客户端写入，不归本 feature。

### 事件 / Trace 需求

- **TR-001**：当 `stop` 或 `restore` 被调用时，系统应当写入一条结构化日志行，包含 `action`、`operation_id`、`result`（ok / E_*）、`state_before`、`state_after`、`desired`、`vram_bytes_before`、`vram_bytes_after`、`vram_readable`、`contract_version` 与耗时毫秒数。
- **TR-002**：该日志行应当可通过容器日志按 `action=` 前缀检索；超时返回后动作最终完成时应当补写一条同 `operation_id` 的收尾行，使"迟到落点"可追。
- **TR-003**：日志行不得包含模型路径之外的任何主机路径、凭据或数据库连接串。

### API / 接口需求

- **IR-001**：控制面应当提供 `GET /lifecycle/status`、`POST /lifecycle/stop`、`POST /lifecycle/restore` 三个 JSON 端点，路径与方法与架构 §7.1 wire 绑定逐字一致。
- **IR-002**：请求应当包含 `X-Contract-Version` 头；`stop` / `restore` 的请求体应当为空或 `{}`，其他形态一律拒绝。
- **IR-003**：`status` 响应应当包含 `state`（取值 `running`/`stopped`/`transitional`）、`desired`（取值 `running`/`stopped`）、`contract_version`、`model_loaded`、`vram_bytes`、`vram_readable`、`device`、`operation` 八个字段；动作执行窗口内也必须给出合法的 `state`，不得省略该字段或返回取值域外的值；`stop` 响应应当包含 `state` 与 `vram_bytes`；`restore` 响应应当包含 `state`。
- **IR-004**：错误响应应当恰为 `{"error": "E_*"}`，错误码取值限于 `E_UNSUPPORTED_VERSION`（**仅**版本协商失败）/ `E_BAD_REQUEST`（请求形态非法）/ `E_BUSY`、`E_TIMEOUT`（`stop`、`restore`）/ `E_UNLOAD_FAILED`（仅 `stop`）/ `E_UNAVAILABLE`（仅 `restore`）。`E_UNSUPPORTED_VERSION` 是客户端判定「服务端未实现本契约」的入口，不得被请求体校验复用。
- **IR-005**：mock 实例不注册 `/lifecycle/*` 路由；对其调用应当返回 404，由客户端决策表第三行处置。

### UX 需求

不适用：本 feature 无用户可见界面。控制面的唯一消费者是 F003 挖掘编排（程序调用），运维可见性见 TR-001 的日志面；按 ADR-0005，门禁与运营状态不页面化。

### 非功能需求

- **NFR-001**：兼容性（mock 边界）：控制面路由只在 real 实例注册；端点的引入不得使默认（mock 目标）镜像产生 torch 依赖——F004 NFR-001 的否证测试「默认镜像 `import torch` 判红」必须保持绿。
- **NFR-002**：可配置 / 迁移友好：三个动作的超时与显存探测方式由具名环境变量承载（值域与默认值见 FR-007），不写死常数；执行机迁移时只改配置与重跑验收。
- **NFR-003**：安全 / escalation 边界：控制面能改变生产状态，只在容器网络与本机回环可达，compose 不发布到 `0.0.0.0`；不引入鉴权体系。按 CLAUDE.md 的 AI 权限红线，Agent 不得调用这些端点改变生产状态——合法调用方是 F003 编排与人工运维。
- **NFR-004**：可靠性 / 恢复：`stop` 不得终止服务进程；任何一次失败的动作都必须使实例收敛到 `running`/`stopped` 之一，不留半加载态；`restore` 失败不使进程退出。
- **NFR-005**：平台兼容：显存读数不得依赖 GPU 进程列表（WSL2 下 `nvidia-smi` 不列出 GPU 进程）；探测顺序见 FR-007；无 CUDA 时 `device=cpu`、`vram_bytes=0`、`vram_readable=true`。
- **NFR-006**：**GPU 前置的诚实标注**：在 F010 落地前，凡依赖真实显存变化的结论（**SC-005、AC-012 的显存事实部分**）一律标注"未验证"，不得以 CPU 实例上的通过充当证据；SC-002（停机稳定性）不在此列——它在 CPU 实例上即可验证。

## 5. 生命周期与不变量

```text
running  -> stopped  stop 成功（desired=stopped ∧ 模型已卸载 ∧ GPU 缓存已释放）
stopped  -> running  restore 成功（desired=running ∧ 模型加载完成）
running  -> running  restore 幂等重入；请求被 E_BAD_REQUEST / E_UNSUPPORTED_VERSION 拒绝
过渡态   -> 过渡态   动作进行中时任一生命周期动作被拒（E_BUSY），原动作不受影响
stopped  -> stopped  stop 幂等重入；restore 失败（E_UNAVAILABLE）；停机期间的推理请求
*        -> 过渡态   动作进行中（operation 非空）；E_TIMEOUT 不改变期望态，也不是终态
过渡态   -> 稳定态   动作完成或抛错收敛后落回稳定态，operation 转 null；stop 丢引用前失败回落
                     running、丢引用后失败保持 stopped（均返回 E_UNLOAD_FAILED）
```

不变量：

- `desired ∈ {running, stopped}` 是**存储的**期望态，只能由 `stop` / `restore` 置位；`state` 是 `(desired, model_loaded)` 的函数，不单独存第二份。`stopped ≡ desired=stopped ∧ model_loaded=false`；`running ≡ desired=running ∧ model_loaded=true`；二者之外为过渡态，**其 wire 值是 `transitional`**——它是动作执行窗口内的必然状态，不是异常分支，客户端对它一律 fail-closed。
- **`desired=stopped` 期间 `model_loaded` 不得由推理路径变为 true**——这是 `stopped` 稳定性的唯一机制保证。
- 同一时刻至多一个生命周期动作在执行；`operation` 非空即视为过渡态。
- `E_TIMEOUT` 不改变 `desired`，也不终止后台动作；动作的最终落点由 `operation` 转 `null` 后的 `state` 表达。**发出过 `stop` 的客户端持有恢复责任**，与该请求返回什么无关（FR-009）。
- **任何错误信封返回之前，`operation` 已清空且 `(desired, model_loaded)` 已落在稳定态**——不存在"返回了错误但状态停在过渡态"。`stop` 在丢引用前失败回落 `running`，丢引用后失败保持 `stopped`（不可逆的一步之后只准前进），两者都返回 `E_UNLOAD_FAILED`。
- `GET /lifecycle/status` 在任何状态下都可达，包括模型加载失败后与动作进行中；控制面可达性不依赖模型可用性。
- 服务进程的生命周期严格长于模型的生命周期：`stop` 卸载模型，绝不终止进程；`restore` 失败同样不退出（与 F004 启动期预检失败即退出是两件事）。
- `vram_bytes` 是设备侧已用显存口径（整卡），与决策表第三行回落探测同口径；读数不可得时 `vram_readable=false` 且 `vram_bytes=null`，该响应仍是成功响应。
- 在 `device=cpu` 的实例上语义完整但显存能力未验证：`vram_bytes=0`、`vram_readable=true`，且**不得据此声称显存释放已验证**（NFR-006）。

## 6. 成功与验收

### 成功标准

- **SC-001**：契约成立——三个端点行为与架构 §7.1 动作表逐格一致，含幂等性、单飞仲裁、进行中语义与错误码；
- **SC-002**：停机稳定——`stop` 之后推理请求不再唤醒模型，`stopped` 能维持到显式 `restore`；
- **SC-003**：先红态转正——`tests/integration/test_f003_kronos_lifecycle.py` 的控制面语义用例在执行机以 0 xfailed 通过，`xfail(strict=True)` 模块级标记已移除；
- **SC-004**：交付边闭合——F003 客户端分动作超时与三条退出路径的 `restore` 均已落地并有断言；
- **SC-005**（**证据所有权归 F010**）：显存真实下降——`stop` 后设备侧读数下降，且卸载后整卡可用显存达到训练预算（`vram_limit_gb`）。**本 feature 的成功标准止于"判据已写成机器可判定断言并处于先红态"**；解除先红态与真实取证是 F010 的 SC-005/AC-009，两边不得互相等待对方完成（R4-003）。

### 验收清单

- [ ] **AC-001** (`FR-001`, `IR-001`, `IR-003`): `status` 返回八字段；模型加载失败后与动作进行中仍可达；**动作执行窗口内返回 `state=transitional` 且 `operation` 非空**（取值域外的值或缺字段即判红）；读数不可得时为成功响应且 `vram_readable=false`/`vram_bytes=null`、不含 `error` 键；探测卡住时仍在服务端 deadline 内返回 — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-002** (`FR-002`, `NFR-004`): `stop` 置 `desired=stopped`、卸载模型并释放缓存、返回 `state=stopped` 与 `vram_bytes`；重复调用不报错；进程存活（`status`/`restore` 随后可达）；**卸载失败返回 `E_UNLOAD_FAILED`，且丢引用前失败落回 `running`、丢引用后（含 `empty_cache` 抛错）保持 `stopped`，两种情况 `operation` 均已清空** — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-003** (`FR-003`): `desired=stopped` 期间连续 `/predict` 与 `/predict_batch` 均走兜底路径、来源不标 `kronos`，且 `model_loaded` 始终 false、`state` 始终 `stopped` — tests: `tests/unit/test_f009_stopped_admission.py`
- [ ] **AC-004** (`FR-004`): `restore` 重新加载返回 `state=running`，重复调用不重复加载；加载失败返回 `E_UNAVAILABLE`、不伪报 `running`、**进程不退出** — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-005** (`FR-005`, `IR-002`, `IR-004`): 版本不匹配与头缺失均以恰为单键的 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝；成功响应不含 `error`；空体与 `{}` 放行；含额外参数的请求体以 `E_BAD_REQUEST` 被拒且不执行动作（两个错误码互不代用） — tests: `tests/unit/test_f009_lifecycle_errors.py`
- [ ] **AC-006** (`FR-006`): 动作进行中时冲突动作立即 `E_BUSY`；超时返回 `E_TIMEOUT` 且 `operation` 仍非空、后台不被中断；动作完成后 `operation` 转 `null` 且 `state` 与 `desired` 一致；**对卸载前 / 丢引用后 / `empty_cache` 三个注入点分别断言响应、`desired`、`model_loaded`、`operation`**，任一注入点停在过渡态即判红 — tests: `tests/unit/test_f009_lifecycle_errors.py`
- [ ] **AC-007** (`FR-007`, `NFR-005`): 显存探测按 `mem_get_info` → `nvidia-smi` 顺序回退且不查进程列表；`KRONOS_VRAM_PROBE_MODE` 的三个合法值逐个生效（`torch`/`nvidia_smi` 不回退到另一来源）、`KRONOS_VRAM_PROBE_TIMEOUT_S` 生效且探测超时按读数不可得处理、status 不超过服务端 deadline；五个变量的非法值一律启动期判红不静默回退 — tests: `tests/unit/test_f009_vram_probe.py`
- [ ] **AC-008** (`TR-001`, `TR-002`, `TR-003`): stop/restore 各写一行含 `operation_id` 的结构化日志；超时后的迟到完成补写同 id 收尾行；字段集与 TR-001 一致且不含主机路径或凭据 — tests: `tests/unit/test_f009_lifecycle_logging.py`
- [ ] **AC-009** (`NFR-001`, `NFR-003`, `IR-005`): mock 实例不注册 `/lifecycle/*`（返回 404）且默认镜像 `import torch` 仍判红；compose 不把控制面端口发布到 `0.0.0.0` — tests: `tests/integration/test_f009_lifecycle_deployment.py`
- [ ] **AC-010** (`FR-009`, `SC-004`): F003 客户端对三个动作分别设置 socket deadline，且逐个**严格大于**对应服务端 deadline（缺省 5+5 / 60+5 / 120+5）；**只要本轮发出过 `stop`**（含 `E_TIMEOUT`、其他错误、连接中断），正常结束、取锁失败、运行异常三条退出路径都恰好调用一次 `restore`；`state=transitional` 判 fail-closed；"已释放"判定含训练预算条件（与 `vram_limit_gb` 同源、未声明即不可确认）且 `vram_readable=false` 单独记 reason。变异证明：把恢复条件改回"只在同步确认 stopped 时"、去掉 deadline 余量、去掉预算判据、忽略 `vram_readable` 各自判红 — tests: `tests/unit/test_f003_gpu_slot.py`、`tests/unit/test_f003_cli_contract.py`
- [ ] **AC-011** (`FR-008`, `SC-003`): 执行机上 `tests/integration/test_f003_kronos_lifecycle.py` 的控制面语义用例 0 xfailed 通过，模块级 `xfail(strict=True)` 已移除，补齐 `E_BUSY`/`E_TIMEOUT`/额外参数用例（额外参数断言 `E_BAD_REQUEST`，不得是 `E_UNSUPPORTED_VERSION`） — tests: `tests/integration/test_f003_kronos_lifecycle.py`
- [ ] **AC-012** (`SC-005`, `NFR-006`): 显存真实下降的判据以机器可判定断言落盘（读数下降，且卸载后可用显存达到训练预算 `vram_limit_gb`），以 `xfail(strict=True)` 标注且在无 GPU 环境下确为 xfail 而非 XPASS。**本 AC 到此为止即算满足**——解除先红态与真实显存证据归 F010 的 AC-009/T011，本 feature 不以 F010 的完成为完成条件（R4-003）。断言须落在独立载体：放进 `test_f003_kronos_lifecycle.py` 会与 F003 T033「该文件 0 xfailed」的机器门禁互相拆台（`--runxfail` 使先红态按真失败计） — tests: `tests/integration/test_f009_vram_release.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：契约字段面与状态机（FastAPI TestClient + fake predictor，不需要 GPU）、停机期间的推理准入、版本协商与单键信封、请求体拒绝、单飞与 `E_BUSY`、超时与 `operation` 生命周期、显存探测三条回退分支、配置非法值判红、日志行字段面；
- 单元测试（跨 Feature 侧）：客户端 deadline 余量与分动作值（`test_f003_gpu_slot.py`）、**三条退出路径各自恰调用一次 `restore`**（`test_f003_cli_contract.py`——恢复发生在 CLI 的 finally，控制流证据必须落在 CLI 套件，不能由 gpu_slot 套件代劳）；
- 集成测试：mock 实例上 `/lifecycle/*` 返回 404 与 compose 暴露面断言；`kronos-signal-real`（CPU）上的停止/恢复往返与准入；迁移后的 F004 端口契约与其变异表仍全绿；
- 真实环境 / 手动验证：执行机 `qiaozhi-lt` 上 `test_f003_kronos_lifecycle.py` 0 xfailed；`test_f009_vram_release.py` 确认为 xfail 而非 XPASS（**该载体的转正归 F010**）。按 `docs/SOP.md` §3，开发机上的跳过不算证据；
- 变异纪律：每条新断言须给出"改坏实现即判红"的证明（F004 循环 12、F003 循环 18 的既定做法）；
- 不做的：不为 `/predict*` 的既有行为补测（F004 已收口），只为"停机期间不重载"这一新准入语义补测。

### 依赖

- 上游 Feature / Contract：架构 §7.1 生命周期契约（正文所有者，含本次修订）；F004 的 `kronos_service` 薄壳、`KronosRealSignal._lock` 串行不变式、两个 compose 服务与三镜像构建、NFR-001 的 mock 依赖面否证测试；F004 tasks §5 登记的「转正契约测试」交付义务。
- **F010「Kronos GPU 推理基座」（`doc-reviewing`，已立项）**：显存**真实证据**的所有者。方向必须说清——本 feature **不以 F010 为完成前置**（AC-012 止于载体与先红态，无 GPU 也可验收）；F010 的 AC-009/T011/T018 反过来消费本 feature 的载体与控制面，因此本 feature 先合入主干、F010 再取证。这样两边的完成 DAG 无环（R4-003）。
- 下游消费者：F003 的 `gpu_slot` / `kronos_offload` / CLI 恢复路径（tasks T025）与夜槽取证（T033）；本 feature 落地后 F003 的 T033 可就控制面语义取证，真实卸载取证仍等 F010。
- **F004（`done`）的端口契约**：本 feature 要把 host 绑定收成回环，必须在本 feature 内迁移 F004 的 spec/design 文字、`test_f004_compose_profile_contract.py` 的精确断言与变异表；不迁移则统一门禁在本 feature 实现期即判红（R4-007）。
- 外部 / 环境依赖：执行机与 docker compose 编排；`nvidia-smi` 作为显存读数的回退路径（GPU 实例上才有意义）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| **GPU 基座归属**（检视 R1-001） | **独立 Feature F010**，F009 声明硬前置；控制面照常交付与验收，显存结论挂先红态 | 纳入 F009 会让它变成双头 feature，且必须改写 F004 已验收的 CPU 契约与变异门；降级为"只做 CPU 语义"则会交付一个声称释放显存、而没有任何东西占显存的门禁——正是本仓反复被咬的"绿得没意义"模式 | F010 落地后回到本 spec 取 AC-012 的证据并解除先红态 |
| **`stopped` 的稳定性**（检视 R1-002） | 引入**存储的期望态** `desired`，`state` 改为 `(desired, model_loaded)` 的函数；`desired=stopped` 期间推理端点禁止隐式加载，走 F004 既有兜底路径 | 原设计把 "derive, don't store" 用在了事实不足的地方：`generate_signal()` 每次都会调 `_load_predictor()`，只看"模型在不在内存里"无法表达停机意图，stop 之后一次 `/predict` 就把显存吃回去 | 兜底来源标注复用 F004 C002 的纪律，不新增来源枚举 |
| **超时语义**（检视 R1-003） | `E_TIMEOUT` = "动作仍在进行"，不中断后台；单飞 + `operation` 使最终落点可观测；冲突动作立即 `E_BUSY` 不排队 | 中断加载/卸载会留下半加载态；排队会让相反动作迟到生效。既然无法安全中断，就把"进行中"变成一等状态而不是隐藏状态 | 若实测 `E_BUSY` 重试率高，再向架构 §7.1 提 draining 态 |
| **错误信封形态**（检视 R1-004） | 错误响应**恰为单键** `{"error": "E_*"}`；显存读数不可得改由成功响应的 `vram_readable=false` + `vram_bytes=null` 表达 | 原来一边声明精确信封、一边要求错误响应附带 `vram_bytes`，JSON schema 无法定义，客户端也无从区分"控制面故障"与"读数缺失"这两件性质完全不同的事 | 契约测试按字段集精确断言，不做宽松匹配 |
| **mock 的生命周期语义**（检视 R1-005） | **反转此前的 Q-002 决策**：mock 不注册 `/lifecycle/*`，返回 404 | 架构 §7.1 明确 mock 不在契约范围；且 mock 永远 `model_loaded=false`，与 `running ⇒ model_loaded=true` 及 `restore` 返回 running 不可能同时成立。客户端对 404 的处置决策表第三行已覆盖，不需要 mock 假装实现契约 | 见 §8 Q-002 的裁决更新 |
| **客户端交付边**（检视 R1-006） | F003 的分动作超时与三条路径的 `restore` 纳入本 feature 的 FR-009 / AC-010 | 服务端端点做完但客户端没有 restore、且用 10s 去卡 60s 的 stop，白天恢复旅程仍无 owner，等于端点白做 | `restore` 半边已在 F003 循环 18 修复（R012）；超时半边归本 feature |
| **显存判据强度**（检视 R1-007 / R2-002） | 判据改为"读数真实下降，且卸载后可用显存达到训练预算"，并要求变异判红 | 原断言只检查 `vram_bytes` 是非负整数——端点完全不释放显存也能通过，门禁弱于成功声明 | 该断言随 F010 解除先红态 |
| **过渡态的 wire 表示**（检视 R4-001） | `state` 取值域加 `transitional`，客户端见到即 fail-closed | 动作一受理就先置 `desired`、后改 `model_loaded`，过渡态是每次 stop/restore 的必经窗口而非异常分支；二值取值域让服务端在这段窗口里构造不出合法响应，`operation` 非空只能补充信息、替代不了必填的 `state` | 决策表新增一行并同步 `check_doc_consistency` 的期望表 |
| **迟到 stop 的恢复所有权**（检视 R4-002） | **发出过 `stop` 即持有恢复责任**，与该请求返回什么无关；客户端 deadline = 服务端 deadline + 余量 | 只在"同步确认 stopped"时登记恢复，会让 60s 超时返回、61s 后台完成的那次卸载永久停机；两端同 deadline 则客户端先抛 `OSError`，规范的 `E_TIMEOUT` 根本收不到 | 采"无条件 restore"而非"轮询 operation"：`restore` 幂等，且轮询窗口之外的迟到完成轮询兜不住 |
| **显存证据的所有权**（检视 R4-003） | AC-012 止于"载体与先红态"，真实证据与解除 xfail 归 F010 AC-009 | 双边都把对方的完成写进自己的 AC 会形成收口环：F009 等 F010 取证才能 done，F010 等 F009 合入才能跑 AC-009；本仓没有 stacked branch 流程可依 | F010 的 spec 同步改为"取证消费 F009，但 F009 不等 F010" |
| **stop 失败的终态**（检视 R4-004） | 新增 `E_UNLOAD_FAILED`；丢引用前失败回落 `running`、丢引用后保持 `stopped`，返回错误前必已清 `operation` | 原文只为 restore 失败定义了回落，stop 失败时实现者可以"返回未声明错误 / 伪装成功 / 回滚 running / 强制 stopped"四选一而都不违反字面 | 丢引用不可逆——不可逆的一步之后只准前进，不准假装回滚 |
| **F004 端口契约迁移**（检视 R4-007） | 在本 feature 内迁移 F004 的 spec/design/测试与变异表 | `test_f004_compose_profile_contract.py` 精确断言 `- "8002:8001"`，本 feature 改回环绑定会立刻让统一门禁判红；而本 feature 自己就要过这道门 | 保留"host 8002 不顶替 mock 8001"与"container 8001"的原意，只把 host bind 收严 |
| HTTP 状态码 vs 错误信封 | 错误也走 HTTP 200 + 单键信封 | 契约测试只认信封；非 2xx 可能被中间件/代理改写成自己的错误页而丢掉 `error` 字段，届时客户端会误判成"端点不存在" | 若将来接入网关需要状态码语义，改架构 §7.1 而非改实现 |
| `stop` 后重启进程回到 running | 有意为之，不持久化停机意图 | 夜槽每轮都会重新 `stop`；持久化会让人工重启后白天拿不到信号，故障面更差 | — |
| 控制面无鉴权 | 网络边界替代鉴权：绑回环 + 容器网络 | 单机自用、调用方同宿主；引入凭据管理成本不抵收益 | 执行机分离或跨机调用前必须先补鉴权 |

## 8. 待确认问题

- [x] Q-001: `status.vram_bytes` 用进程侧还是设备侧口径？ — 决策（2026-09-20, owner）：**设备侧已用显存**（`torch.cuda.mem_get_info` 优先、`nvidia-smi --query-gpu=memory.used` 回退），与决策表第三行回落探测同口径；进程侧 `memory_allocated` 卸载后归零但掩盖其他租户。
- [x] Q-002: mock 实例上 `/lifecycle/*` 怎么行为？ — 决策（2026-09-20, owner）：**不注册路由，返回 404**。此项**推翻**同日更早的"照常响应 `device=cpu`"决策：架构 §7.1 明确 mock 不在契约范围，且 mock 永远 `model_loaded=false` 与 `running ⇒ model_loaded=true` 不相容（文档检视 R1-005）。客户端对 404 的处置由决策表第三行覆盖。
- [x] Q-003: `stop` 遇在飞推理请求如何处理？ — 决策（2026-09-20, owner）：问题被 FR-003 的准入语义取代——`stop` 先置 `desired=stopped`，此后推理请求一律走兜底路径不占模型，不再存在"停止撞上在飞推理"的竞态窗口；生命周期动作之间的互斥由 FR-006 的单飞 `E_BUSY` 承担。
- [x] Q-004: GPU 基座归 F009 还是独立 Feature？ — 决策（2026-09-20, owner）：**独立 Feature F010**（编号已在 BACKLOG「规划中」预留），F009 声明硬前置，SC-005 / AC-012 在其落地前保持先红态（文档检视 R1-001）。
