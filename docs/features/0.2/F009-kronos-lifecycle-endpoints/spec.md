---
kind: feature
id: F009
version: "0.2"
status: draft
gate_version: 1
related_features: [F003, F004]
topics: [kronos, lifecycle, control-plane, gpu-slot, m2]
doc_kind: spec
created: 2026-09-20
updated: 2026-09-20
---

# F009：Kronos 服务生命周期控制面端点

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR6（运行监控）间接消费；本 feature 不新增 PRD 功能面，是架构契约的服务端落地
- **架构来源**：`docs/alphamill-architecture.md` §7.1「Kronos 服务生命周期契约（版本化，供夜槽编排消费）」——动作表、wire 绑定、显存确认、契约版本、观测→处置决策表、所有权条
- **系统设计 / Research / Contract 来源**：`docs/alphamill-integration.md`（Freqtrade / Kronos 集成操作细节）；契约测试 `tests/integration/test_f003_kronos_lifecycle.py`（客户端可见行为的锁定物）
- **上游决策**：ADR-0002（依赖管理策略：Kronos 上游 clone + pin，推理薄壳归本仓）、ADR-0005（呈现与观测架构：不新增口径载体）
- **基座来源**：F004（`src/alphamill/kronos_service/` 推理薄壳、`kronos-signal` mock 与 `kronos-signal-real` 两个 compose 服务、启动预检与 eager load）；F003（客户端 `gpu_slot` 与观测→处置决策表的消费方）
- **功能类型**：backend / runtime
- **规格模式**：full
- **变更类型**：ADDED
- **一句话意图**：把架构 §7.1 已定稿的版本化生命周期控制面（`status` / `stop` / `restore`）实现到 Kronos 推理薄壳并部署于执行机，让夜槽编排能真正卸载常驻推理、确认显存释放后取锁训练，从而解除 F003 T033 / AC-010 真实卸载取证的前置阻塞。

## 1. 问题、目标与非目标

### 问题

架构 §7.1 的生命周期契约已逐格定稿——动作语义、幂等性、超时默认值、错误码、wire 绑定、显存确认口径、观测→处置决策表一应俱全，且决策表被 `tools/check_doc_consistency.py` 的 `offload_decision_table_rows` 逐行锁死。消费侧也齐了：F003 的客户端（`gpu_slot`，T025）按决策表逐行实现并有单测，契约测试 `tests/integration/test_f003_kronos_lifecycle.py` 以 `xfail(strict=True)` 立着先红态。

唯独服务端一行没有：`src/alphamill/kronos_service/server.py` 只暴露 `/health`、`/ohlcv`、`/predict`、`/predict_batch`；F004 spec §3 明确把控制面端点划在交付范围之外，指向「待分配 feature」。2026-09-19 在执行机复测确认 `/lifecycle/status` 仍是 404（该次探测打在 mock 实例 `kronos-signal:8001` 上，按契约它本就不是合法目标，结论仍成立）。

后果有两层。**直接**：F003 的 T033 要求该契约测试以 0 xfailed 通过，端点不存在则 AC-010 的「真实卸载取证」无法完成，F003 收口被挂起。**每晚**：夜槽编排只能走决策表第三行的 404 回落探测，靠设备侧 `memory.used` 与阈值猜测，读数达到阈值或不可得即 fail-closed 留在单槽队列——单卡 8GB 的执行机上，这意味着挖掘训练可能整夜起不来，而卡上占着的很可能正是本可以被卸载的 Kronos 常驻推理。

### 目标

- `kronos-signal-real` 暴露 `GET /lifecycle/status`、`POST /lifecycle/stop`、`POST /lifecycle/restore`，行为与架构 §7.1 动作表逐格一致；
- `stop` 真正释放 GPU 显存并由 `status.vram_bytes`（设备侧已用显存口径）可确认，`restore` 可恢复常驻推理，两者重复调用不报错；
- 契约版本协商与错误信封成立：`X-Contract-Version` 不匹配一律 `{"error": "E_UNSUPPORTED_VERSION"}`，客户端不需要解读 HTTP 状态码即可判定；
- `tests/integration/test_f003_kronos_lifecycle.py` 转正——移除 `xfail(strict=True)`、补 `E_BUSY` / `E_TIMEOUT` 错误路径用例，在执行机以 0 xfailed 通过；
- F003 的 T033 解除阻塞，AC-010 可取真实卸载证据。

### 非目标

- 本 feature 不做挖掘侧编排、单槽 FIFO、取锁与夜槽决策——那是 F003（其 tasks T025 / T033），本 feature 只提供被调用的服务端；
- 本 feature 不改 Kronos 模型、推理质量或 `/predict*` 任何行为——F004 已收口，其行为面不在本次变更范围；
- 本 feature 不修改架构 §7.1 的契约正文——契约归该节所有，本 feature 只实现；确需改契约时先改架构文档再改实现；
- 本 feature 不做通用服务控制面框架或第二个服务的生命周期端点——只给 Kronos 一个实例，通用化留到出现第二个消费者时再谈；
- 本 feature 不引入鉴权体系（token / mTLS / 签名）——控制面的安全边界是网络可达性，见 NFR-003；
- 本 feature 不承诺 `restore` 的模型预热 SLA——恢复即返回 `running`，首个推理请求可能因懒加载而变慢。

## 2. 用户场景

### US-001：夜槽编排能卸载 Kronos 并确认显存已释放（Priority: P1）

作为挖掘编排（F003 `gpu_slot`），我希望在训练窗口边界调用一次 `stop` 就能让 Kronos 交出显存、并能从 `status` 读到释放后的设备侧已用显存，以便我在确认显存足够后才取锁开训，而不是靠阈值猜测或 fail-closed 放弃整夜。

**为什么是这个优先级**：这是本 feature 存在的唯一理由——没有它，F003 的 T033 取不到证据，夜槽每晚都在猜。`status` + `stop` 的往返是最小可交付切片，`restore` 之外的一切都可以后置。

**独立测试**：在执行机的 `kronos-signal-real` 上依次调 `status` → `stop` → `status`，断言字段面齐备、`state` 由 `running` 变 `stopped`、`vram_bytes` 为设备侧读数且停止后不高于停止前。

**验收场景**：

1. Given `kronos-signal-real` 正在常驻推理且模型已加载，when 调用 `GET /lifecycle/status`，then 返回 `{state: running, contract_version, model_loaded: true, vram_bytes, device}` 五个字段齐备。
2. Given 同一实例无在飞推理请求，when 调用 `POST /lifecycle/stop`，then 模型被卸载、GPU 缓存被释放，响应为 `{state: stopped, vram_bytes: <设备侧已用字节>}`，且随后的 `status` 仍可达并报 `state=stopped`、`model_loaded=false`。
3. Given 已经 `stopped`，when 再次调用 `stop`，then 返回 `state=stopped` 且不报错、不产生副作用。

### US-002：白天恢复常驻推理（Priority: P1）

作为挖掘编排，我希望训练窗口结束后调用 `restore` 让 Kronos 恢复常驻，以便白天 dry-run 能继续拿到实时信号，而不需要人工重启容器。

**为什么是这个优先级**：与 US-001 同批——只停不启会把白天的信号面打掉，契约把两者定义为一对往返动作，缺一不可交付。

**独立测试**：在已 `stopped` 的实例上调 `restore`，断言返回 `state=running`，再调 `restore` 仍返回 `running`，随后 `/predict` 可正常产出非 placeholder 信号。

**验收场景**：

1. Given 实例处于 `stopped`，when 调用 `POST /lifecycle/restore`，then 模型重新加载并返回 `state=running`。
2. Given 实例已是 `running`，when 再次调用 `restore`，then 返回 `state=running` 且不重复加载模型。
3. Given `restore` 因模型资产缺失而无法加载，when 调用返回，then 以 `{"error": "E_UNAVAILABLE"}` 拒绝，`status` 如实报 `state=stopped`、`model_loaded=false`，不伪报 `running`。

### US-003：契约版本与错误码可被客户端无歧义判定（Priority: P2）

作为客户端实现者，我希望所有拒绝都以统一的 `{"error": "E_*"}` 信封表达，以便我不必从 HTTP 状态码反推服务端意图，也不会把「端点未实现的 404」误读成「合法拒绝」。

**为什么是这个优先级**：它依赖 US-001/US-002 的端点存在，但独立于显存语义——错误面可以单独用单元测试锁死。契约测试已经写明「只认错误码信封，不认 HTTP 状态码」，否则端点未实现的现状会假性通过。

**独立测试**：以 `X-Contract-Version: 999` 调 `status`，断言响应体为 `{"error": "E_UNSUPPORTED_VERSION"}`；以缺失该头的请求调用，断言同样被拒绝。

**验收场景**：

1. Given 请求头 `X-Contract-Version` 的值不是服务端支持的版本，when 调用任一生命周期端点，then 响应体为 `{"error": "E_UNSUPPORTED_VERSION"}`。
2. Given 请求完全缺失 `X-Contract-Version` 头，when 调用任一生命周期端点，then 同样以 `E_UNSUPPORTED_VERSION` 拒绝，不按默认版本放行。
3. Given 存在在飞推理请求，when 调用 `stop`，then 以 `{"error": "E_BUSY"}` 拒绝，不等待也不强停，模型保持加载。

## 3. 范围与边界

### 范围内

- `src/alphamill/kronos_service/` 内的生命周期控制面实现：三个端点、契约版本协商、错误信封、在飞请求计数；
- `KronosRealSignal` 的卸载 / 恢复路径（`_predictor` 记忆化的反向操作、`torch.cuda.empty_cache()`、状态回报）；
- 设备侧已用显存探测（`torch.cuda.mem_get_info` 优先，`nvidia-smi --query-gpu=memory.used` 回退，两者皆不可得时的显式处置）；
- mock 实例（`kronos-signal`，无 torch）上的同端点行为：照常响应、`device=cpu`、`stop`/`restore` 为 no-op；
- 超时与阈值的可配化（不写死常数，迁移到 `qiaozhi-lab` 只改配置）；
- `tests/integration/test_f003_kronos_lifecycle.py` 的转正：移除 `xfail(strict=True)`、补错误路径用例；
- 执行机部署与真实取证（`kronos-signal-real`，GPU 实例）。

### 范围外

- 挖掘侧编排、单槽 FIFO、取锁判定、`kronos_offload` 运行记录字段 → F003（tasks T025 / T033），本 feature 只被调用；
- 架构 §7.1 契约正文的任何修改 → 归该节所有；
- `/predict`、`/predict_batch`、`/health`、`/ohlcv` 的行为变更 → F004 已收口，本 feature 只在 `/health` 之外新增路由；
- 审计事件入库与运营写路径（FR7.4）→ F006 运营操作入口；本 feature 只写结构化日志行（TR-001）；
- 通用服务生命周期框架、第二个服务的控制面 → 出现第二个消费者时再立项；
- 鉴权、限流、TLS → 见 NFR-003 的网络边界方案。

### 边界场景

- `stop` 之后客户端还要调 `status` 与 `restore`：因此 `stop` **只卸载模型、不终止进程**——进程退出会让控制面自身不可达，违反契约。
- 实例运行在无 CUDA 的机器上（mock、开发机、`KRONOS_DEVICE=cpu`）：`vram_bytes` 报 `0`、`device` 如实报 `cpu`，`stop`/`restore` 为 no-op 并返回对应 `state`——正好命中决策表第二行「`status` 可达且 `device=cpu` → 记 `offload_not_needed`，继续夜槽」。
- 设备侧显存读数不可得（`torch.cuda.mem_get_info` 抛错且 `nvidia-smi` 不可执行）：不得猜 `0`——`vram_bytes` 缺省为 `null` 并以 `E_UNAVAILABLE` 表达不确定，客户端据此 fail-closed（决策表第五行语义）。
- 在飞推理请求与 `stop` 并发：以 `E_BUSY` 拒绝，绝不在推理中途卸载模型——「队列赢，绝不并行赌 OOM」的同一条克制原则。
- 模型资产缺失或加载失败时调 `restore`：如实报错，绝不把未加载的实例伪报为 `running`（F004 C002 的同类失效模式：兜底信号不得标 `source=kronos`）。
- 端点部署到 mock 镜像后：mock 镜像绝不因此引入 torch 依赖——F004 NFR-001 的否证测试「默认镜像 `import torch` 判红」必须保持绿。

## 4. 需求

### 功能需求

### Requirement: 生命周期状态查询（`FR-001`）

系统应当提供 `GET /lifecycle/status`，返回 `{state, contract_version, model_loaded, vram_bytes, device}`；该端点为只读、天然幂等，默认超时 5s（可配）。当实例处于任何状态（含模型加载失败）时该端点都应当可达。

#### Scenario: 常驻推理中查询

- GIVEN 实例模型已加载且运行于 GPU
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回 `state=running`、`model_loaded=true`、`device` 为实际设备、`vram_bytes` 为设备侧已用字节

#### Scenario: 卸载后查询

- GIVEN 已成功执行过 `stop`
- WHEN 调用 `GET /lifecycle/status`
- THEN 端点仍可达，返回 `state=stopped`、`model_loaded=false`

### Requirement: 优雅停止并释放显存（`FR-002`）

系统应当提供 `POST /lifecycle/stop`，卸载已加载的模型、释放 GPU 缓存，并返回释放后的 `vram_bytes` 与 `state=stopped`；重复调用应当返回 `state=stopped` 而不报错；默认超时 60s（可配）。停止动作不得终止服务进程。

#### Scenario: 首次停止

- GIVEN 实例 `state=running` 且无在飞推理请求
- WHEN 调用 `POST /lifecycle/stop`
- THEN 模型被卸载、GPU 缓存被释放，返回 `state=stopped` 与设备侧 `vram_bytes`

#### Scenario: 重复停止

- GIVEN 实例已 `state=stopped`
- WHEN 再次调用 `POST /lifecycle/stop`
- THEN 返回 `state=stopped`，不报错、不产生副作用

#### Scenario: 停止不杀进程

- GIVEN 已成功执行 `stop`
- WHEN 随后调用 `status` 或 `restore`
- THEN 两者均可达（进程存活，仅模型被卸载）

### Requirement: 恢复常驻推理（`FR-003`）

系统应当提供 `POST /lifecycle/restore`，重新加载模型并返回 `state=running`；重复调用应当返回 `state=running` 且不重复加载；默认超时 120s（可配）。

#### Scenario: 从停止态恢复

- GIVEN 实例 `state=stopped`
- WHEN 调用 `POST /lifecycle/restore`
- THEN 模型重新加载，返回 `state=running`，随后 `/predict` 产出非 placeholder 信号

#### Scenario: 恢复失败不得伪报

- GIVEN 模型资产缺失或加载抛错
- WHEN 调用 `POST /lifecycle/restore`
- THEN 以 `{"error": "E_UNAVAILABLE"}` 拒绝，`status` 如实报 `state=stopped`、`model_loaded=false`

### Requirement: 契约版本协商与统一错误信封（`FR-004`）

系统应当要求所有生命周期请求携带 `X-Contract-Version` 头（当前 `1`）；版本不匹配或头缺失时应当以 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝。所有拒绝应当使用统一信封 `{"error": "E_*"}`，客户端不需要解读 HTTP 状态码即可判定。

#### Scenario: 版本不匹配

- GIVEN 请求头 `X-Contract-Version: 999`
- WHEN 调用任一生命周期端点
- THEN 响应体为 `{"error": "E_UNSUPPORTED_VERSION"}`

#### Scenario: 版本头缺失

- GIVEN 请求未携带 `X-Contract-Version`
- WHEN 调用任一生命周期端点
- THEN 同样以 `E_UNSUPPORTED_VERSION` 拒绝，不按默认版本放行

### Requirement: 在飞推理与不可用的错误语义（`FR-005`）

如果存在在飞推理请求，`stop` 应当立即以 `{"error": "E_BUSY"}` 拒绝，既不等待排空也不强制中断。如果动作在其可配超时内未完成，系统应当返回 `{"error": "E_TIMEOUT"}`。如果显存读数不可得或模型不可加载，系统应当返回 `{"error": "E_UNAVAILABLE"}`，不得以猜测值代替。

#### Scenario: 停止撞上在飞推理

- GIVEN 至少一个 `/predict` 或 `/predict_batch` 请求正在处理
- WHEN 调用 `POST /lifecycle/stop`
- THEN 返回 `{"error": "E_BUSY"}`，模型保持加载，`status` 仍报 `state=running`

#### Scenario: 显存读数不可得

- GIVEN `torch.cuda.mem_get_info` 抛错且 `nvidia-smi` 不可执行
- WHEN 调用 `status`
- THEN `vram_bytes` 为 `null` 且以 `E_UNAVAILABLE` 表达不确定，不猜 `0`

### Requirement: mock 实例的同端点行为（`FR-006`）

在 mock 实例（`kronos-signal`，`KRONOS_USE_REAL_MODEL=false`，无 torch）上，系统应当同样暴露三个端点并照常响应：`device=cpu`、`model_loaded=false`、`vram_bytes=0`，`stop` / `restore` 为 no-op 并返回对应 `state`。端点的引入不得使 mock 镜像产生 torch 依赖。

#### Scenario: mock 上查询状态

- GIVEN mock 实例在跑
- WHEN 调用 `GET /lifecycle/status`
- THEN 返回 `device=cpu`、`model_loaded=false`、`vram_bytes=0`，命中决策表第二行（客户端记 `offload_not_needed` 继续夜槽）

#### Scenario: mock 镜像不含 torch

- GIVEN 默认（mock 目标）镜像已构建
- WHEN 在镜像内执行 `import torch`
- THEN 失败（F004 NFR-001 的否证断言保持成立）

### Requirement: F003 契约测试转正（`FR-007`）

系统落地后，`tests/integration/test_f003_kronos_lifecycle.py` 应当移除模块级 `xfail(strict=True)` 标记，并补齐 `E_BUSY` 与 `E_TIMEOUT` 的错误路径用例；该文件应当在执行机以 0 xfailed 通过。

#### Scenario: 先红态转正

- GIVEN 端点已在执行机部署且 `KRONOS_CONTROL_URL` 指向 `kronos-signal-real`
- WHEN 以 `--runxfail` 运行该契约测试
- THEN 全部用例通过且 xfailed 数为 0

### 数据 / 实体需求

不适用：本 feature 不创建或修改任何持久化实体。控制面状态（`state`、`model_loaded`）是进程内存态，由 §5 的不变量约束；运行记录字段 `kronos_offload` 由 F003 客户端写入，不归本 feature。

### 事件 / Trace 需求

- **TR-001**：当 `stop` 或 `restore` 被调用时，系统应当写入一条结构化日志行，包含 `action`（stop/restore）、`result`（ok / E_*）、`state_before`、`state_after`、`vram_bytes_before`、`vram_bytes_after`、`contract_version` 与耗时毫秒数。
- **TR-002**：该日志行应当可通过容器日志（`docker logs kronos-signal-real`）按 `action=` 前缀检索，用于夜槽事后复盘卸载是否真的发生。
- **TR-003**：日志行不得包含模型路径之外的任何主机路径、凭据或数据库连接串。

### API / 接口需求

- **IR-001**：控制面应当提供 `GET /lifecycle/status`、`POST /lifecycle/stop`、`POST /lifecycle/restore` 三个 JSON 端点，路径与方法与架构 §7.1 wire 绑定逐字一致。
- **IR-002**：请求应当包含 `X-Contract-Version` 头；`stop` / `restore` 的请求体为空 JSON 对象或缺省（不接受额外参数，避免在契约外偷加开关）。
- **IR-003**：`status` 响应应当包含 `state`、`contract_version`、`model_loaded`、`vram_bytes`、`device` 五个字段；`stop` 响应应当包含 `state` 与 `vram_bytes`；`restore` 响应应当包含 `state`。
- **IR-004**：非法请求（版本不支持 / 头缺失）与被拒绝的动作（在飞、不可用、超时）应当返回统一信封 `{"error": "E_*"}`，错误码取值限于 `E_UNSUPPORTED_VERSION` / `E_BUSY` / `E_TIMEOUT` / `E_UNAVAILABLE`。

### UX 需求

不适用：本 feature 无用户可见界面。控制面的唯一消费者是 F003 挖掘编排（程序调用），运维可见性见 §6 与 TR-001 的日志面；按 ADR-0005，门禁与运营状态不页面化。

### 非功能需求

- **NFR-001**：兼容性（mock 边界）：端点的引入不得使默认（mock 目标）镜像产生 torch 依赖——F004 NFR-001 的否证测试「默认镜像 `import torch` 判红」必须保持绿；显存与模型相关的导入一律惰性化。
- **NFR-002**：可配置 / 迁移友好：三个动作的超时（默认 5s / 60s / 120s）与显存探测方式一律走配置并可经环境变量覆盖，不写死常数；执行机从 `qiaozhi-lt` 迁移至 `qiaozhi-lab` 时只改配置与重跑验收，不改代码。
- **NFR-003**：安全 / escalation 边界：控制面能停止生产推理服务，属于改变生产状态。端点只在容器网络与本机回环可达，不对宿主外网暴露（compose 不发布控制面到 `0.0.0.0`）；不引入鉴权体系，安全边界是网络可达性。按 CLAUDE.md 的 AI 权限红线，Agent 不得调用这些端点改变生产状态——合法调用方是 F003 编排与人工运维。
- **NFR-004**：可靠性 / 恢复：`stop` 不得终止服务进程；任何一次失败的 `stop` / `restore` 都必须保持实例处于一个如实可报的状态（要么 `running` 且模型已加载，要么 `stopped` 且 `model_loaded=false`），不得留下"半加载"的中间态。
- **NFR-005**：平台兼容：显存读数在 WSL2 下不得依赖 GPU 进程列表（`nvidia-smi` 在 WSL2 不列出 GPU 进程，架构 §7.1 已记录）；探测顺序为 `torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used`，两者皆不可得时按 FR-005 报 `E_UNAVAILABLE`。

## 5. 生命周期与不变量

```text
running  -> stopped  stop 成功（模型已卸载 + GPU 缓存已释放）
stopped  -> running  restore 成功（模型重新加载完成）
running  -> running  stop 被拒（E_BUSY 在飞 / E_TIMEOUT 超时）；restore 幂等重入
stopped  -> stopped  stop 幂等重入；restore 失败（E_UNAVAILABLE，资产缺失或加载抛错）
```

不变量：

- `state` 只有 `running` / `stopped` 两个取值，不存在第三态；任何中途失败都必须收敛到这两值之一（NFR-004）。
- `state=stopped` 蕴含 `model_loaded=false`；`state=running` 蕴含 `model_loaded=true`。两者不得互相矛盾——状态是从模型持有情况派生的，不单独存一份（derive, don't store）。
- `GET /lifecycle/status` 在任何状态下都可达，包括模型加载失败后；控制面的可达性不依赖模型可用性。
- 服务进程的生命周期严格长于模型的生命周期：`stop` 卸载模型，绝不终止进程。
- `vram_bytes` 是设备侧已用显存口径（整卡），与观测→处置决策表第三行的回落探测同口径；读数不可得时为 `null` 而非 `0`。
- 在 `device=cpu` 的实例上，三个端点的语义退化为无显存可管：`vram_bytes=0`、`stop`/`restore` 为 no-op，但端点仍照常响应。

## 6. 成功与验收

### 成功标准

- **SC-001**：契约成立——三个端点在 `kronos-signal-real` 上的行为与架构 §7.1 动作表逐格一致，含幂等性与错误码；
- **SC-002**：显存成立——`stop` 后设备侧已用显存实际下降，且可由 `status.vram_bytes` 确认，夜槽据此取锁不再靠阈值猜测；
- **SC-003**：先红态转正——`tests/integration/test_f003_kronos_lifecycle.py` 在执行机以 0 xfailed 通过，`xfail(strict=True)` 标记已移除；
- **SC-004**：阻塞解除——F003 的 T033 / AC-010 可取真实卸载证据，其未完成任务中不再有本 feature 造成的阻塞项。

### 验收清单

- [ ] **AC-001** (`FR-001`, `IR-001`, `IR-003`): `status` 返回 `state`/`contract_version`/`model_loaded`/`vram_bytes`/`device` 五字段；卸载后端点仍可达并如实报 `stopped` + `model_loaded=false` — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-002** (`FR-002`, `NFR-004`): `stop` 卸载模型并释放 GPU 缓存、返回 `state=stopped` 与设备侧 `vram_bytes`；重复调用不报错；进程存活（`status`/`restore` 随后可达） — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-003** (`FR-003`): `restore` 重新加载模型返回 `state=running`，重复调用不重复加载；加载失败时以 `E_UNAVAILABLE` 拒绝且不伪报 `running` — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-004** (`FR-004`, `IR-002`, `IR-004`): `X-Contract-Version` 不匹配或缺失一律以 `{"error": "E_UNSUPPORTED_VERSION"}` 拒绝；全部拒绝走统一信封，错误码取值限于契约四个 — tests: `tests/unit/test_f009_lifecycle_contract.py`
- [ ] **AC-005** (`FR-005`): 在飞推理时 `stop` 返回 `E_BUSY` 且模型保持加载；超时返回 `E_TIMEOUT`；显存读数不可得时 `vram_bytes=null` 且报 `E_UNAVAILABLE`，不猜 `0` — tests: `tests/unit/test_f009_lifecycle_errors.py`
- [ ] **AC-006** (`NFR-005`): 显存探测按 `torch.cuda.mem_get_info` → `nvidia-smi --query-gpu=memory.used` 顺序回退，不依赖 GPU 进程列表；无 CUDA 时报 `0` 且 `device=cpu` — tests: `tests/unit/test_f009_vram_probe.py`
- [ ] **AC-007** (`FR-006`, `NFR-001`): mock 实例三端点照常响应（`device=cpu`/`model_loaded=false`/`vram_bytes=0`、stop/restore 为 no-op）；默认镜像 `import torch` 仍判红 — tests: `tests/integration/test_f009_lifecycle_mock.py`
- [ ] **AC-008** (`TR-001`, `TR-002`, `TR-003`): 每次 stop/restore 写结构化日志行，含 action/result/state_before/state_after/vram 前后值/contract_version/耗时，可按 `action=` 检索，且不含主机路径或凭据 — tests: `tests/unit/test_f009_lifecycle_logging.py`
- [ ] **AC-009** (`NFR-002`, `NFR-003`): 三个超时与显存探测方式均可经环境变量覆盖、无写死常数；compose 不把控制面端口发布到 `0.0.0.0` — tests: `tests/integration/test_f009_lifecycle_mock.py`
- [ ] **AC-010** (`FR-007`, `SC-003`): 在执行机 `kronos-signal-real` 上 `tests/integration/test_f003_kronos_lifecycle.py` 以 0 xfailed 通过，`xfail(strict=True)` 已移除且补齐 `E_BUSY`/`E_TIMEOUT` 用例；证据记录 hostname、GPU 型号与 stop 前后显存读数 — tests: `tests/integration/test_f003_kronos_lifecycle.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：契约字段面与状态机（FastAPI TestClient，模型侧以 fake predictor 替身，不需要 GPU）、版本协商与错误信封、在飞计数与 `E_BUSY`、显存探测的三条回退分支、日志行字段面；
- 集成测试：mock 实例上的端到端三端点行为与 compose 暴露面断言；`kronos-signal-real` 上的真实停止/恢复往返；
- 真实环境 / 手动验证：执行机 `qiaozhi-lt` 上的真实卸载取证——`stop` 前后设备侧显存读数对照、F003 契约测试 0 xfailed，证据记录 hostname 与 GPU 型号。按 `docs/SOP.md` §3，开发机（无 NVIDIA）上 GPU 相关用例跳过属预期，不算证据也不算失败；
- 不做的：不为 `/predict*` 行为补测（F004 已收口）；不做夜槽编排侧的取锁与决策表断言（F003 T025 已覆盖）。

### 依赖

- 上游 Feature / Contract：架构 §7.1 生命周期契约（正文所有者，本 feature 只实现）；F004 的 `src/alphamill/kronos_service/` 薄壳、`KronosRealSignal` 的加载路径与 `_lock` 串行不变式、`kronos-signal` / `kronos-signal-real` 两个 compose 服务与三镜像构建；F004 tasks §5 登记的「转正契约测试」交付义务。
- 下游消费者：F003 的 `gpu_slot` 生命周期客户端（tasks T025）与夜槽取证（T033 / AC-010）——本 feature 落地即解除其阻塞；观测→处置决策表的前两行与第四行在端点存在后成为主路径，第三行（404 回落探测）退化为端点未部署时的兜底。
- 外部 / 环境依赖：执行机提供 CUDA 运行时与 GPU 实例（当前 `qiaozhi-lt`：Win11+WSL2 + RTX 4060 Laptop 8GB）；`nvidia-smi` 作为显存读数的回退路径；docker compose 编排（自 quant-crypto 迁入）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| `vram_bytes` 的测量源 | **设备侧已用显存**（`torch.cuda.mem_get_info` 优先，`nvidia-smi --query-gpu=memory.used` 回退） | 与观测→处置决策表第三行的回落探测同口径；夜槽真正要判断的是"整张卡还剩多少"，进程侧 `memory_allocated` 卸载后必然归零，却可能掩盖别的租户占着卡，F003 据此取锁仍会 OOM | 迁移到 `qiaozhi-lab` 后重标阈值，探测代码不变 |
| mock 实例上端点怎么行为 | **照常响应**：`device=cpu` / `model_loaded=false` / `vram_bytes=0`，stop/restore 为 no-op | 正好命中决策表第二行「`status` 可达且 `device=cpu` → 记 `offload_not_needed`，继续夜槽」，无需分叉镜像或条件挂载路由；若 mock 上返回 404，客户端将永远停在第三行的回落探测分支，假红面不变 | 若将来 mock 与 real 拆包，端点随 real 走 |
| `stop` 撞上在飞推理 | **立即 `E_BUSY`**，不等待排空也不强停 | 语义最简、最可测；契约的 `state` 只有 running/stopped 两值，引入 draining 态需要额外约定 status 在该期间报什么，属于改契约。夜槽 22:00 后 dry-run 读 signal_cache 存量信号、不实时推理（架构 §7.1 时段表），撞上的概率本就低；撞上时 F003 按决策表第四行 fail-closed 留队列下轮重试 | 若实测重试率高，再考虑向架构 §7.1 提 draining 态 |
| `stop` 是否终止进程 | **只卸载模型，进程保活** | 契约要求 `stop` 之后 `status` 与 `restore` 仍可达；杀进程会让控制面自身消失，客户端只能观测到"连接拒绝"，落进决策表第五行 fail-closed——等于把成功的卸载误报成未知状态 | — |
| 控制面无鉴权 | 安全边界取**网络可达性**：只在容器网络与本机回环暴露，compose 不发布到 `0.0.0.0` | 单机自用、调用方是同宿主的编排进程；引入 token/mTLS 会把凭据管理摊进本 feature，收益不抵成本 | 若将来跨机调用（执行机分离），必须先补鉴权再开放 |
| 端点让 mock 镜像引入 torch | 显存与模型相关导入**一律惰性化**，由 F004 NFR-001 的否证测试兜底 | F004 花了整轮检视才把 mock 镜像的依赖面收干净（Q001 `.dockerignore` 白名单、C001 mock 钉死 `KRONOS_USE_REAL_MODEL=false`），本 feature 不能把它破坏 | 在 CI 保持该否证测试为硬门 |
| 真实取证依赖执行机 | F003 同款约束：GPU 证据一律在 `qiaozhi-lt` 取，开发机 skip 属预期 | 架构 §7.1 机器边界、`docs/SOP.md` §3 | 迁移 `qiaozhi-lab` 后重跑 AC-010 |
| 2026-09-19 的 404 复测打在 mock 上 | 结论（端点未实现）仍成立，但**取证目标不合法**；本 feature 落地时以 `kronos-signal-real` 重取一次基线 | 契约明确 mock 不是合法测试目标（无显存可释放）；`server.py` 只有 4 条路由亦独立印证 | 落地后在 BACKLOG 的复测记录同步更正 |

## 8. 待确认问题

- [x] Q-001: `status.vram_bytes` 用进程侧还是设备侧口径？ — 决策（2026-09-20, owner）：**设备侧已用显存**（`torch.cuda.mem_get_info` 优先、`nvidia-smi --query-gpu=memory.used` 回退），与决策表第三行回落探测同口径；进程侧 `memory_allocated` 卸载后归零但掩盖其他租户，F003 据此取锁仍会 OOM。
- [x] Q-002: mock 实例（无 torch、`device=cpu`）上 `/lifecycle/*` 怎么行为？ — 决策（2026-09-20, owner）：**照常响应**，`device=cpu` / `model_loaded=false` / `vram_bytes=0`，stop/restore 为 no-op；命中决策表第二行，无需分叉镜像。返回 404 会让客户端永远停在第三行回落探测。
- [x] Q-003: `stop` 遇在飞推理请求如何处理？ — 决策（2026-09-20, owner）：**立即 `E_BUSY`**，不等待不强停；F003 按决策表第四行 fail-closed 留队列下轮重试。引入 draining 态需改架构 §7.1 的 `state` 取值，属改契约，不在本 feature。
