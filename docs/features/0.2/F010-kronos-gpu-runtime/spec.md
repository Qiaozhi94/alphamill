---
kind: feature
id: F010
version: "0.2"
status: draft
gate_version: 1
related_features: [F003, F004, F009]
topics: [kronos, gpu, runtime, cuda, m2]
doc_kind: spec
created: 2026-09-20
updated: 2026-09-20
---

# F010：Kronos GPU 推理基座

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR6 间接消费；本 feature 不新增 PRD 功能面，是让既有推理服务真正跑在 GPU 上的运行时工作
- **架构来源**：`docs/alphamill-architecture.md` §7.1——单卡时段调度（白天 Kronos 常驻 ≤3GB / 夜槽训练 ≤6GB 独占）、显存预算为硬上限、生命周期契约的 **GPU 基座前置条**
- **系统设计 / Research / Contract 来源**：`docs/alphamill-integration.md`（Kronos 集成与部署细节）
- **上游决策**：ADR-0002（Kronos 上游 clone + pin，推理薄壳归本仓）；F003 `pyproject.toml` 的 `mining` extra 已确立 CUDA wheel 约定（torch ≥2.7 + `--index-url .../cu128`，并要求覆盖 `qiaozhi-lab` 的 Blackwell sm_120）
- **基座来源**：F004（`kronos-service.Dockerfile` 的 `mock`/`real` 两级目标、`kronos-signal` / `kronos-signal-real` 两个 compose 服务、启动预检与 eager load、`tests/unit/test_f004_compose_profile_contract.py` 的契约与变异门）
- **功能类型**：runtime / infra
- **规格模式**：full
- **变更类型**：MODIFIED
- **一句话意图**：把 `kronos-signal-real` 从 CPU 实例升级为可在执行机 GPU 上真实推理的实例——torch 换 CUDA wheel、compose 做 GPU 直通、`device` 与 healthcheck 由参数驱动，并把 F004 锁死"必须是 CPU"的那组断言迁移为"默认是 CPU、GPU 需显式启用"，从而解除 F009 AC-012 与 F003 T033 的硬前置。

## 1. 问题、目标与非目标

### 问题

架构 §7.1 的整套单卡调度建立在一个前提上：Kronos 常驻推理占显存、夜槽把它卸载腾出 ≤6GB 给训练。但**仓内没有任何 GPU Kronos 实例**：

- `deployment/kronos-service.Dockerfile` 的 `real` 目标从 **CPU wheel index** 装 torch（`--index-url https://download.pytorch.org/whl/cpu`）；
- `deployment/docker-compose.yml` 的 `kronos-signal-real` 钉死 `KRONOS_DEVICE: cpu`，且没有任何 GPU 设备预留；
- healthcheck 以 `/health` 的 `device == 'cpu'` 为通过条件；
- 以上三点被 `tests/unit/test_f004_compose_profile_contract.py` 锁成硬断言，并配了变异门（删 CPU wheel index 必须判红）。

F004 把 GPU 直通显式划在范围外是合理的——它要交付的是编排与契约，CPU 推理即可验证。但下游已经攒了两笔账：**F009** 的 SC-005/AC-012（显存真实下降）只能挂先红态；**F003** 的 T033/AC-010（真实卸载取证）因此无法完成，而 F003 是 M2 的主线。换句话说，整条"夜槽腾显存给挖掘训练"的链路至今**没有任何一环在真实显存上验证过**。

### 目标

- `kronos-signal-real` 能在执行机以 CUDA 设备加载 Kronos 并产出推理信号，`/health` 如实报 `device=cuda*`、`model_loaded=true`；
- torch 的 wheel index 与 `KRONOS_DEVICE` 由**构建参数与环境变量**驱动，默认仍是 CPU（不破坏开发机与 CI 的既有行为），GPU 需显式启用；
- compose 具备 GPU 直通（设备预留），且在无 GPU 的机器上**默认路径不受影响**；
- F004 那组"必须是 CPU"的断言与变异门**迁移**为"默认取值是 CPU + GPU 取值由本 feature 断言覆盖"，迁移后 F004 的既有意图（默认镜像不含 torch、real 不退回 mock）一条不丢；
- 在执行机实测常驻显存占用并与架构 §7.1 的 ≤3GB 预算对照，超出即如实记录并触发预算重标；
- 解除 F009 AC-012 与 F003 T033 的硬前置。

### 非目标

- 本 feature 不改 Kronos 推理逻辑、不做推理质量或性能优化——只让它跑在 GPU 上；
- 本 feature 不做生命周期控制面（`status`/`stop`/`restore`）→ **F009**；两者的关系是 F009 依赖本 feature 取显存证据，本 feature 不依赖 F009 即可交付；
- 本 feature 不做挖掘侧编排与取锁 → F003；
- 本 feature 不做执行机从 `qiaozhi-lt` 到 `qiaozhi-lab` 的迁移（Win11+WSL2 → 原生 Ubuntu、RTX 4060 → Blackwell sm_120）→ 独立迁移 Feature；但 wheel 的选择须为该迁移留路（见 §7 决策）；
- 本 feature 不做多 GPU、不做 MPS/MIG 切分、不做显存配额强制（预算仍由 F003 的单槽仲裁在应用层执行）；
- 本 feature 不把 GPU 变成默认：开发机（AMD iGPU，无 NVIDIA）与 CI 的默认构建与默认 compose 行为必须保持不变。

## 2. 用户场景

### US-001：执行机上的 Kronos 真正占用显存（Priority: P1）

作为夜槽编排的运维者，我希望执行机上的 `kronos-signal-real` 以 CUDA 加载模型并占用可观测的显存，以便"卸载腾显存"这件事有真实对象。

**为什么是这个优先级**：这是本 feature 的全部理由。没有它，F009 的控制面在语义上完整但显存面空转，F003 的 T033 永远取不到证据。

**独立测试**：在执行机以 GPU 配置启动实例，断言 `/health` 的 `device` 以 `cuda` 开头、`model_loaded=true`，且 `nvidia-smi --query-gpu=memory.used` 相对启动前有可观测增长。

**验收场景**：

1. Given 执行机具备 NVIDIA 驱动与容器 GPU 直通，when 以 GPU 配置启动 `kronos-signal-real`，then `/health` 报 `device=cuda:0`、`model_loaded=true`，且设备侧已用显存相对基线上升。
2. Given 实例已在 GPU 上常驻，when 调用 `/predict`，then 返回 `source=kronos` 的真实信号（非兜底）。
3. Given 宿主没有可用 NVIDIA 设备，when 以 GPU 配置启动，then 启动**失败并可见**（沿用 F004 `restart: "no"` 的失败态可见纪律），不静默回落 CPU。

### US-002：默认路径不受影响（Priority: P1）

作为开发机与 CI 上的使用者，我希望默认构建与默认 compose 行为一字不变，以便本 feature 不把没有 NVIDIA 的机器推下悬崖。

**为什么是这个优先级**：与 US-001 同批。F004 花了整轮检视才把默认面的依赖与失败态收干净，本 feature 不能把它推翻——而"参数化"最容易在默认值上翻车。

**独立测试**：不带任何 GPU 参数构建与 `docker compose config`，断言 torch 仍走 CPU wheel index、`KRONOS_DEVICE` 仍解析为 `cpu`、默认（mock 目标）镜像 `import torch` 仍判红。

**验收场景**：

1. Given 不提供任何 GPU 构建参数，when 构建 `real` 目标，then torch 仍来自 CPU wheel index。
2. Given 不提供任何 GPU 环境变量，when `docker compose config`，then `kronos-signal-real` 的 `KRONOS_DEVICE` 解析为 `cpu` 且无 GPU 设备预留。
3. Given 默认（mock 目标）镜像，when 在其中 `import torch`，then 失败（F004 NFR-001 的否证断言保持成立）。

### US-003：显存预算可对照，超出即如实记录（Priority: P2）

作为架构 §7.1 的维护者，我希望常驻显存占用被实测并与 ≤3GB 预算对照，以便预算是标定出来的而不是拍出来的。

**为什么是这个优先级**：依赖 US-001，但独立于 F009/F003 的消费面；它决定架构里那张时段表的数字是否还成立。

**独立测试**：在执行机记录实例启动前后与一次 `/predict` 之后的设备侧显存读数，与 ≤3GB 对照并归档。

**验收场景**：

1. Given GPU 实例已常驻，when 记录显存峰值，then 读数与架构 §7.1 的 ≤3GB 预算对照结果被写入验收证据。
2. Given 实测峰值超过预算，when 归档证据，then 如实记录并在架构 §7.1 触发一次显式重标，不得直接沿用旧数字。

## 3. 范围与边界

### 范围内

- `deployment/kronos-service.Dockerfile`：`real` 目标的 torch wheel index 与版本改由构建参数驱动（默认 CPU），并保留 `FROM mock AS real` 的派生关系；
- `deployment/docker-compose.yml`：`kronos-signal-real` 的 `KRONOS_DEVICE` 与 GPU 设备预留由环境变量驱动（默认 cpu / 无预留）；healthcheck 的设备判据随之参数化；
- `deployment/.env.example`：新增 GPU 相关变量与其默认值；
- F004 契约测试的**迁移**：把"必须是 CPU"的硬断言改写为"默认取值是 CPU"，并把 GPU 取值的断言与变异门落在本 feature 的测试文件；F004 既有意图（默认镜像不含 torch、real 不退回 mock、`:ro` 挂载、DB 依赖）一条不丢；
- 执行机上的 GPU 直通落地（NVIDIA 容器运行时可用性核验）与真实推理取证；
- 常驻显存实测与架构 §7.1 预算对照；
- 解除 F009 AC-012 的先红态（跨 Feature 交付边，见 FR-006）。

### 范围外

- 生命周期控制面端点 → F009；
- 挖掘侧编排、单槽仲裁、夜槽取证 → F003；
- 执行机平台迁移（`qiaozhi-lab`、Blackwell sm_120、原生 Ubuntu）→ 独立迁移 Feature；本 feature 只保证 wheel 选择不挡路；
- 推理质量、性能优化、批处理吞吐 → 不做；
- 多 GPU、MIG/MPS、显存硬配额 → 不做（预算由 F003 应用层仲裁）；
- 把 GPU 设为默认 → 明确不做（见 US-002）。

### 边界场景

- 宿主无 NVIDIA 设备但配置要求 GPU：**启动失败且失败态可见**（`restart: "no"`），绝不静默回落 CPU——回落会让 `/health` 报 cpu 而编排以为拿到了 GPU 实例。
- CUDA 可见但显存不足以加载模型：启动预检失败即非零退出（F004 既有纪律），不进入"半加载"态。
- 开发机（无 NVIDIA）执行本 feature 的集成用例：按 SOP §3 跳过属预期，不算证据也不算失败。
- CI：默认路径必须全绿且不触碰 GPU；GPU 断言一律标注为执行机取证项。
- torch CUDA wheel 与宿主驱动不匹配：视为配置错误，启动期可见失败，不吞异常。
- 常驻显存超过 §7.1 的 ≤3GB 预算：不"就这样吧"——如实记录并触发预算重标（US-003 场景 2）。

## 4. 需求

### 功能需求

### Requirement: 参数化的 torch 安装源（`FR-001`）

`real` 目标应当由构建参数决定 torch 的 wheel index 与版本；**缺省值应当保持当前的 CPU wheel index 与版本**。构建参数缺失时的行为应当与本 feature 落地前逐字一致。

#### Scenario: 默认构建不变

- GIVEN 不提供任何 GPU 构建参数
- WHEN 构建 `real` 目标
- THEN torch 来自 CPU wheel index，版本与落地前一致

#### Scenario: 显式启用 CUDA wheel

- GIVEN 提供 CUDA wheel index 构建参数（如 `cu128`）
- WHEN 构建 `real` 目标
- THEN 镜像内 torch 报告 CUDA 可用（`torch.version.cuda` 非空）

### Requirement: 参数化的设备与 GPU 直通（`FR-002`）

`kronos-signal-real` 的 `KRONOS_DEVICE` 与 GPU 设备预留应当由环境变量驱动；**默认值应当是 `cpu` 且不声明任何 GPU 设备预留**。启用 GPU 时应当声明设备预留，使容器可见 NVIDIA 设备。

#### Scenario: 默认 compose 不含 GPU

- GIVEN 不提供 GPU 环境变量
- WHEN 执行 `docker compose config`
- THEN `kronos-signal-real` 的 `KRONOS_DEVICE` 解析为 `cpu` 且渲染结果中无 GPU 设备预留

#### Scenario: 启用 GPU 后设备可见

- GIVEN 提供 GPU 环境变量
- WHEN 渲染并启动 compose
- THEN 容器内 `torch.cuda.is_available()` 为真

### Requirement: 设备判据参数化的 healthcheck（`FR-003`）

healthcheck 应当以 `model_loaded=true` 且 `device` 匹配**当前配置的期望设备**为通过条件，而不是硬编码 `cpu`。

#### Scenario: GPU 实例的 healthcheck

- GIVEN 以 GPU 配置启动
- WHEN healthcheck 执行
- THEN 以 `device` 以 `cuda` 开头为通过条件；报 `cpu` 时不得通过

### Requirement: 无 GPU 时显式失败（`FR-004`）

如果配置要求 GPU 而宿主不具备可用 NVIDIA 设备，系统应当启动失败并保持失败态可见，不得静默回落 CPU。

#### Scenario: 缺 GPU 即失败

- GIVEN 宿主无可用 NVIDIA 设备
- WHEN 以 GPU 配置启动实例
- THEN 容器以非零码退出且不重启，`/health` 不可达——而不是报 `device=cpu` 的"成功"

### Requirement: F004 契约断言迁移（`FR-005`）

F004 中"必须是 CPU"的断言应当改写为"**默认取值**是 CPU"，其变异门同步改写；GPU 取值的断言与变异门应当落在本 feature 的测试文件。迁移后 F004 的既有意图——默认镜像不含 torch、`real` 不退回 mock、模型目录 `:ro` 挂载、DB 依赖——应当一条不丢。

#### Scenario: 迁移不丢意图

- GIVEN 迁移后的测试集
- WHEN 对 compose/Dockerfile 施加 F004 既有的四类变异（改 target、删 pin、放开 `:ro`、删 DB 依赖）
- THEN 全部仍判红

### Requirement: 解除下游先红态（`FR-006`）

本 feature 落地后，F009 的 AC-012 载体 `tests/integration/test_f009_vram_release.py` 应当移除 `xfail(strict=True)` 并在执行机真实通过；F003 的 T033 前置随之解除。

#### Scenario: 先红态转正

- GIVEN GPU 实例已在执行机常驻
- WHEN 执行一次 stop → 确认 → restore 往返
- THEN 显存读数真实下降且卸载后整卡可用显存达到训练预算，该用例不再需要 xfail 标记

### 数据 / 实体需求

不适用：本 feature 不创建或修改任何持久化实体，只改构建与编排配置。

### 事件 / Trace 需求

- **TR-001**：GPU 实例启动时，既有启动日志应当包含实际解析到的设备与 torch 的 CUDA 版本，使"以为在 GPU 上、实际在 CPU 上"不可能静默发生。
- **TR-002**：该信息应当可通过容器日志检索，并被 US-003 的显存对照证据引用。

### API / 接口需求

- **IR-001**：`/health` 的既有字段与语义不变；`device` 应当如实反映实际加载设备（`cpu` 或 `cuda:<n>`）。
- **IR-002**：不新增任何 HTTP 端点。

### UX 需求

不适用：本 feature 无用户可见界面。

### 非功能需求

- **NFR-001**：默认面不变——不提供 GPU 参数时，构建产物、compose 渲染结果与 CI 行为应当与落地前逐字一致；默认（mock 目标）镜像 `import torch` 仍判红。
- **NFR-002**：可配置 / 迁移友好——wheel index、torch 版本、设备、GPU 预留全部走参数，迁移 `qiaozhi-lab` 时只改参数与重跑验收；wheel 选择须能覆盖 Blackwell sm_120（与 F003 `mining` extra 的约定同源）。
- **NFR-003**：安全 / 边界——GPU 直通不放宽既有挂载与网络边界：模型目录仍 `:ro`，不新增对外暴露端口。
- **NFR-004**：可靠性——GPU 不可用时失败可见（FR-004），不静默降级；启动预检失败仍非零退出。
- **NFR-005**：平台兼容——目标平台为执行机 WSL2 + docker-ce（非 Docker Desktop）；显存读数不依赖 GPU 进程列表（WSL2 下 `nvidia-smi` 不列出进程）。

## 5. 生命周期与不变量

```text
构建：默认参数 -> CPU wheel 镜像（与落地前逐字一致）
     显式 CUDA 参数 -> CUDA wheel 镜像
启动：device=cpu 配置 -> CPU 加载 -> /health device=cpu
     device=cuda 配置 + 设备可见 -> CUDA 加载 -> /health device=cuda:<n>
     device=cuda 配置 + 设备不可见 -> 非零退出（失败态可见，不回落）
```

不变量：

- **默认即 CPU**：任何未显式启用 GPU 的路径，行为与本 feature 落地前逐字一致。
- `/health` 的 `device` 永远是**实际**加载设备，不是配置的期望值——两者不一致时以实际为准并使启动失败可见。
- 配置要求 GPU 而设备不可见时，实例不得进入可服务状态；"能回答 `/health`"必须蕴含"模型已按配置的设备加载完成"。
- GPU 的启用不放宽任何既有边界（`:ro` 挂载、端口暴露、DB 依赖）。
- 显存预算（架构 §7.1 的 ≤3GB）是**标定值**：实测超出即触发重标，不得沿用。

## 6. 成功与验收

### 成功标准

- **SC-001**：GPU 常驻成立——执行机上 `kronos-signal-real` 以 CUDA 加载并产出真实信号；
- **SC-002**：默认面无回归——不带 GPU 参数的构建、compose 渲染与 CI 行为逐字不变；
- **SC-003**：契约迁移无损——F004 的四类变异迁移后仍全部判红；
- **SC-004**：预算已标定——常驻显存实测并与 §7.1 的 ≤3GB 对照，超出即触发重标；
- **SC-005**：下游解锁——F009 AC-012 的先红态解除，F003 T033 的 GPU 前置不再成立。

### 验收清单

- [ ] **AC-001** (`FR-001`, `NFR-001`): 不提供 GPU 构建参数时 torch 仍来自 CPU wheel index 且版本不变；提供 CUDA 参数时镜像内 `torch.version.cuda` 非空 — tests: `tests/unit/test_f010_build_args_contract.py`
- [ ] **AC-002** (`FR-002`, `NFR-001`): 默认 `docker compose config` 渲染出 `KRONOS_DEVICE: cpu` 且无 GPU 设备预留；提供 GPU 变量时渲染出设备预留 — tests: `tests/unit/test_f010_compose_gpu_contract.py`
- [ ] **AC-003** (`FR-003`): healthcheck 以 `model_loaded=true` + 期望设备匹配为通过条件；GPU 配置下报 `cpu` 不得通过 — tests: `tests/unit/test_f010_compose_gpu_contract.py`
- [ ] **AC-004** (`FR-004`, `NFR-004`): 配置要求 GPU 而设备不可见时容器非零退出且不重启，`/health` 不可达（**不得**报 `device=cpu` 的成功） — tests: `tests/integration/test_f010_gpu_runtime.py`
- [ ] **AC-005** (`FR-005`, `SC-003`): F004 的四类变异（改 target、删 pin、放开 `:ro`、删 DB 依赖）在迁移后的测试集上仍全部判红；默认镜像 `import torch` 仍判红 — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/unit/test_f010_compose_gpu_contract.py`
- [ ] **AC-006** (`FR-002`, `TR-001`): 执行机上容器内 `torch.cuda.is_available()` 为真，`/health` 报 `device=cuda:<n>`、`model_loaded=true`，启动日志含实际设备与 torch CUDA 版本 — tests: `tests/integration/test_f010_gpu_runtime.py`
- [ ] **AC-007** (`US-001`): 执行机上 `/predict` 返回 `source=kronos` 的真实信号（非兜底），且设备侧已用显存相对基线上升 — tests: `tests/integration/test_f010_gpu_runtime.py`
- [ ] **AC-008** (`US-003`, `SC-004`): 常驻显存峰值实测并与架构 §7.1 的 ≤3GB 预算对照，证据记录 hostname / GPU 型号 / 读数；超出预算时架构 §7.1 已触发显式重标 — tests: `tests/integration/test_f010_gpu_runtime.py`
- [ ] **AC-009** (`FR-006`, `SC-005`): `tests/integration/test_f009_vram_release.py` 移除 `xfail(strict=True)` 并在执行机真实通过（显存下降且卸载后可用显存达到训练预算） — tests: `tests/integration/test_f009_vram_release.py`

## 7. 测试、依赖与决策

### 测试策略

- 单元测试：Dockerfile 构建参数的默认值与 CUDA 取值、compose 渲染的默认面与 GPU 面、healthcheck 判据；沿用 F004 的"断言抽成纯函数 + 文本变异判红"做法；
- 集成测试：执行机上的 GPU 实例启动、`torch.cuda.is_available()`、真实 `/predict`、缺 GPU 时的失败可见、显存读数对照；
- 真实环境 / 手动验证：GPU 直通可用性核验（NVIDIA 容器运行时）、显存峰值标定；按 SOP §3，开发机（无 NVIDIA）跳过属预期，不算证据也不算失败；
- 变异纪律：每条新断言须给出"改坏配置即判红"的证明；F004 迁移后的四类变异必须仍判红（AC-005）；
- 不做的：不为推理质量、吞吐、批处理补测。

### 依赖

- 上游 Feature / Contract：F004（Dockerfile 两级目标、compose 两个服务、启动预检、契约与变异门）；架构 §7.1（显存预算与 GPU 基座前置条）；F003 `mining` extra 的 CUDA wheel 约定。
- 下游消费者：**F009**（AC-012 的先红态由本 feature 解除）、**F003**（T033/AC-010 的 GPU 前置由本 feature 解除）。注意方向：F009 不阻塞本 feature，本 feature 阻塞 F009 的显存取证。
- 外部 / 环境依赖：执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）的 NVIDIA 驱动与容器 GPU 直通；PyTorch CUDA wheel 源。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 新建 GPU 实例还是升级 `kronos-signal-real` | **升级现有实例**，通过参数区分 CPU/GPU | 架构 §7.1 把生命周期契约的目标实例名写死为 `kronos-signal-real`；新增实例名会立刻制造契约漂移，F009 与 F003 客户端都要跟着改 | 若将来需要 CPU/GPU 并存，再谈第三个 profile |
| F004 的 CPU 硬断言怎么处理 | **迁移**为"默认取值是 CPU"，GPU 取值的断言归本 feature | 直接删掉会丢失 F004 花整轮检视收干净的默认面保护；保留原样则本 feature 无法落地——迁移是唯一既不丢意图又能前进的路径 | AC-005 以"四类变异仍判红"作为迁移无损的机器判据 |
| GPU 默认开还是默认关 | **默认关**，显式启用 | 开发机是 AMD iGPU、CI 无 GPU；默认开会把这两处推下悬崖，而它们承载着本仓绝大多数门禁 | 执行机在 `.env` 显式开启 |
| 设备不可见时回落 CPU | **不回落，失败可见** | 回落会让 `/health` 报 cpu 而编排以为拿到了 GPU 实例——夜槽据此卸载"并不占显存的东西"，比直接失败更难排查 | 沿用 F004 `restart: "no"` 的失败态可见纪律 |
| torch CUDA 版本选择 | 与 F003 `mining` extra 同源：≥2.7 + cu128 wheel index | 同一台执行机上 Kronos 推理与挖掘训练共存，两套 torch 若 CUDA 版本不一致会给驱动与显存行为增加不必要变量 | `qiaozhi-lab` 的 Blackwell sm_120 需要 cu128+，该选择已留路 |
| 常驻显存可能超 ≤3GB 预算 | 实测对照，超出即在架构 §7.1 显式重标，不沿用旧数字 | §7.1 自己写明"预算值与时段表随执行机走，迁移后按上文重标"；本 feature 是该预算第一次被真实标定的机会 | 重标会连带影响 F003 的 `vram_limit_gb` 缺省 |
| WSL2 下的 GPU 直通可靠性 | 作为风险如实记录：先核验容器运行时可用性再改配置（T002） | WSL2 + docker-ce（非 Docker Desktop）的 GPU 直通与原生 Linux 有差异，属本 feature 的主要未知数 | 若核验不通过，本 feature 的阻塞点上升为"执行机平台"，需回到 §8 重新裁决 |

## 8. 待确认问题

- [x] Q-001: GPU 基座归 F009 还是独立 Feature？ — 决策（2026-09-20, owner）：**独立 Feature（本 spec）**。纳入 F009 会让它变成双头 feature，且必须改写 F004 已验收的 CPU 契约与变异门；F009 的控制面语义可在 CPU 上完整交付，只有显存取证需要本 feature。
- [x] Q-002: 升级现有实例还是新建 GPU 实例？ — 决策（2026-09-20, owner）：**升级 `kronos-signal-real`**，CPU/GPU 由构建参数与环境变量区分。实例名是架构 §7.1 契约的一部分，改名等于改契约。
- [x] Q-003: F004 的"必须是 CPU"断言如何处置？ — 决策（2026-09-20, owner）：**迁移而非删除**——改写为"默认取值是 CPU"，GPU 取值断言归本 feature；以"F004 四类变异仍全部判红"作为迁移无损的机器判据（AC-005）。
