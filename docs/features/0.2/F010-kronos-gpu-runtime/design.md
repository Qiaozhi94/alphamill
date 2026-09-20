---
kind: feature
id: F010
version: "0.2"
related_features: [F003, F004, F009]
topics: [kronos, gpu, runtime, cuda, m2]
doc_kind: design
created: 2026-09-20
updated: 2026-09-20
---

# F010：Kronos GPU 推理基座 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：架构 §7.1（显存预算 ≤3GB 常驻 / ≤6GB 夜槽、GPU 基座前置条）
- **ADR / 上游 Contract**：ADR-0002；F003 `pyproject.toml` `mining` extra 的 CUDA wheel 约定（torch ≥2.7 + cu128，覆盖 Blackwell sm_120）
- **实现约束**：
  - **默认面不可动**：不带 GPU 参数时，构建产物与 compose 渲染结果须与落地前逐字一致；
  - `FROM mock AS real` 的派生关系不得破坏（F004 变异门之一）；
  - 模型目录 `:ro`、DB 依赖、端口暴露面不得放宽；
  - 开发机无 NVIDIA、CI 无 GPU——两者只能跑单元层，GPU 断言一律执行机取证。

## 1. 技术概要与影响面

把"设备"从写死的常量变成**一条贯穿构建期与运行期的参数链**：构建参数决定 torch 从哪个 wheel index 装，环境变量决定容器申请什么设备、`KRONOS_DEVICE` 是什么、healthcheck 拿什么判据比对。三者必须同源——只改其一就会出现"装了 CUDA wheel 但没申请设备"或"申请了设备但 healthcheck 还在比 cpu"这类半吊子状态。

- 前端：不适用。
- 后端 / API：**不改代码**。`KronosRealSignal._load_predictor()` 已按 `KRONOS_DEVICE` + `torch.cuda.is_available()` 选设备，`/health` 已如实报 `device`——本 feature 只喂给它正确的环境。唯一可能的代码改动是 TR-001 的启动日志补 torch CUDA 版本。
- 存储 / Migration：不适用。
- Runtime / Agent Adapter：`deployment/kronos-service.Dockerfile`（`real` 目标的 torch 安装参数化）、`deployment/docker-compose.yml`（`kronos-signal-real` 的设备预留、`KRONOS_DEVICE`、healthcheck 判据参数化）、`deployment/.env.example`。
- Event / Evidence：启动日志增设备与 CUDA 版本（TR-001）；显存标定证据进 spec §6。
- 文档 / 配置：架构 §7.1 的 GPU 基座前置条在本 feature 收口时改写为"已落地"；若实测显存超预算，§7.1 的时段表数字同步重标。
- **跨 Feature**：F009 的 `tests/integration/test_f009_vram_release.py` 解除 xfail；F004 的契约测试按 FR-005 迁移。

## 2. 架构与模块边界

```text
构建期                        运行期
──────                        ──────
TORCH_INDEX_URL ──┐           KRONOS_GPU_COUNT ──► compose 设备预留
TORCH_VERSION   ──┼─► real    KRONOS_DEVICE    ──► 容器环境 ──► _load_predictor()
                  │  镜像                                          │
                  └─────────── 必须同源 ─────────────────────────┘
                                                        /health.device（实际值）
                                                                  │
                                            healthcheck 判据 ◄─────┘
                                            （期望设备前缀，参数化）
```

- **参数同源是本设计的唯一要点**：三处（wheel / 设备预留 / 期望判据）由同一组变量驱动，`.env.example` 是它们的单一说明处。
- **服务代码零改动**（TR-001 的日志行除外）：`kronos_real.py` 已经是"按环境选设备、如实报告"的形态；把它改成"知道自己该在 GPU 上"反而会引入第二套真相。
- **失败可见优先于可用**：设备不可见时让启动预检失败（F004 既有路径），不加任何回落分支。

## 3. 数据模型与 Migration

不适用：无持久化实体。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

不新增端点。`/health` 字段与语义不变，`device` 仍是**实际**加载设备。

**构建参数**（Dockerfile `ARG`，均有缺省值 = 当前行为）：

| 参数 | 缺省 | GPU 取值示例 | 作用 |
|---|---|---|---|
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | `https://download.pytorch.org/whl/cu128` | torch wheel 来源 |
| `TORCH_VERSION` | `2.14.0`（与落地前一致） | `2.7.*`+（须 ≥2.7，见 spec §7） | torch 版本 |

**运行期变量**（compose，均有缺省值 = 当前行为）：

| 变量 | 缺省 | GPU 取值 | 作用 |
|---|---|---|---|
| `KRONOS_DEVICE` | `cpu` | `cuda` | 传给 `_load_predictor()` 的设备请求 |
| `KRONOS_GPU_COUNT` | `0` | `1` | 设备预留数量；`0` 时不渲染任何 GPU 预留 |
| `KRONOS_HEALTH_DEVICE_PREFIX` | `cpu` | `cuda` | healthcheck 比对 `/health.device` 的前缀 |

### Event / Trace Contract

启动日志增一行（TR-001）：实际解析设备 + `torch.version.cuda`（CPU wheel 下为 `None`）。这条的作用是让"以为在 GPU 上、实际在 CPU 上"在日志里一眼可见，而不是等到显存读数不动才发现。

## 5. Runtime、Workflow 与并发

不适用于并发：本 feature 不引入新的并发路径。运行时流程：

```text
compose up（GPU 配置）
  → 容器获得 NVIDIA 设备（KRONOS_GPU_COUNT=1 渲染出的预留）
  → lifespan: real_mode_startup() 预检资产 → eager load
      → _load_predictor(): KRONOS_DEVICE=cuda ∧ torch.cuda.is_available() → device="cuda:0"
      → 设备不可见 → is_available() 为假 → 回落 "cpu" ← **这是本 feature 必须堵的洞**
  → healthcheck: model_loaded=true ∧ device 前缀匹配 → 就绪
```

**关键设计点**：`_load_predictor()` 现有逻辑在 `KRONOS_DEVICE=cuda` 但 CUDA 不可用时会**静默回落 cpu**。本 feature 不改该函数的通用语义（它在开发机上是合理的），而是在 `real_mode_startup()` 的预检里加一条：**配置要求 cuda 而 `torch.cuda.is_available()` 为假 → 预检失败（非零退出）**。失败点放在预检而不是加载内部，理由是 F004 已经把"预检失败即可见退出"这条路径建好并测过，复用它比新造一条失败路径更稳。

healthcheck 的前缀比对是第二道网：即使预检被绕过，报 `cpu` 的实例也不会被判就绪。

## 6. UI 与可观测性

- 页面：不适用。
- 日志：TR-001 的启动行；其余沿用 F004。
- 指标：不新增口径载体（ADR-0005）。显存读数由 `nvidia-smi` 在取证时读取，不常驻采集。
- 运维可见性：`docker logs quant-kronos-signal-real | head` 应当一眼看出跑在哪个设备上。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：

  | 条件 | 行为 |
  |---|---|
  | 配置 `KRONOS_DEVICE=cuda` 且 CUDA 不可用 | 预检失败，非零退出，`restart: "no"` 保持失败态可见 |
  | 模型资产缺失 | 预检失败（F004 既有） |
  | CUDA wheel 与宿主驱动不匹配 | torch 导入或初始化抛错 → 启动失败可见，不吞异常 |
  | 显存不足以加载模型 | 加载抛错 → 启动失败可见 |
  | 未提供任何 GPU 参数 | 与落地前逐字一致（CPU 路径） |

- **重启与恢复**：沿用 F004（`restart: "no"`，失败不自愈以免掩盖配置错误）。
- **权限 / 凭据边界**：GPU 直通不放宽既有边界——模型目录仍 `:ro`，不新增暴露端口，不引入特权容器（设备预留走 compose 的 `deploy.resources.reservations.devices`，不用 `privileged: true`）。
- **Windows / POSIX / 版本兼容**：目标平台是执行机 WSL2 + docker-ce（非 Docker Desktop）。WSL2 的 GPU 直通与原生 Linux 有差异，是本 feature 的主要未知数——T002 先核验容器运行时可用性再动配置。显存读数不依赖 GPU 进程列表。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f010_build_args_contract.py` | Dockerfile 的 `TORCH_INDEX_URL`/`TORCH_VERSION` 有 ARG 且缺省值等于落地前的字面量；**变异证明**：改缺省值即判红 |
| `AC-002` | unit | `tests/unit/test_f010_compose_gpu_contract.py` | 默认渲染 `KRONOS_DEVICE: cpu` 且无 `devices:` 预留；`KRONOS_GPU_COUNT=1` 时渲染出预留；**变异证明**：把缺省改成 1 即判红 |
| `AC-003` | unit | 同上 | healthcheck 含 `model_loaded') is True` 且设备判据来自 `KRONOS_HEALTH_DEVICE_PREFIX`；**变异证明**：把判据写死回 `'cpu'` 即判红 |
| `AC-004` | integration（可在开发机执行） | `tests/integration/test_f010_gpu_runtime.py` | 在无 NVIDIA 的机器上以 GPU 配置启动 → 容器非零退出且 `/health` 不可达（**不是**报 cpu 的成功）。这条恰好在开发机可证伪，不需要 GPU |
| `AC-005` | unit | `tests/unit/test_f004_compose_profile_contract.py` + `tests/unit/test_f010_compose_gpu_contract.py` | F004 四类变异（改 target、删 pin、放开 `:ro`、删 DB 依赖）迁移后仍全部判红；默认镜像 `import torch` 仍判红 |
| `AC-006` | integration（执行机） | `tests/integration/test_f010_gpu_runtime.py` | 容器内 `torch.cuda.is_available()` 为真；`/health` 报 `device` 以 `cuda` 开头、`model_loaded=true`；启动日志含设备与 CUDA 版本 |
| `AC-007` | integration（执行机） | 同上 | `/predict` 返回 `source=kronos`；`nvidia-smi` 已用显存相对基线上升 |
| `AC-008` | 真实环境（执行机） | 同上 + 证据归档 | 常驻显存峰值与 ≤3GB 对照；超出时架构 §7.1 已重标 |
| `AC-009` | 真实环境（执行机，跨 Feature） | `tests/integration/test_f009_vram_release.py` | 移除 `xfail(strict=True)` 后真实通过：显存下降且卸载后整卡可用显存达到训练预算 |

补充纪律：

- 单元层（AC-001/002/003/005）在开发机与 CI 全绿是硬要求——它们保护的正是"默认面不变"；
- AC-004 虽是 integration，但**在没有 GPU 的机器上才最容易证伪**，应在开发机执行；
- AC-006/007/008/009 一律执行机取证，证据记录 hostname / GPU 型号 / 读数（SOP §3）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 升级现有实例 vs 新建 GPU 实例 | 升级 `kronos-signal-real`，参数区分 | 实例名是架构 §7.1 契约的一部分，改名等于改契约并波及 F009/F003 客户端 | 需要 CPU/GPU 并存时再谈第三个 profile |
| 服务代码要不要改 | **基本不改**（只加 TR-001 日志行） | `kronos_real.py` 已是"按环境选设备、如实报告"的形态；让它"知道自己该在 GPU 上"会造出第二套真相 | — |
| `_load_predictor` 的静默回落怎么堵 | 在 `real_mode_startup()` 预检里堵，不改 `_load_predictor` 的通用语义 | 该回落在开发机上是合理行为；把判断放到预检既复用了 F004 已测的失败路径，又不污染通用逻辑 | — |
| GPU 默认开/关 | 默认关 | 开发机 AMD iGPU、CI 无 GPU，默认开会推翻本仓绝大多数门禁的运行前提 | 执行机 `.env` 显式开启 |
| F004 断言迁移的无损判据 | "四类变异仍判红"作为机器判据（AC-005） | 迁移最容易悄悄丢掉保护；用变异集合而不是人工承诺来证明 | — |
| WSL2 GPU 直通的不确定性 | T002 先核验容器运行时，再动任何配置 | 这是本 feature 唯一真正的未知数；配置改完才发现直通不可用会浪费整轮 | 核验不通过则阻塞点上升为"执行机平台"，回 spec §8 重新裁决 |
| 常驻显存可能超 ≤3GB | 实测对照，超出即重标 §7.1 并连带影响 F003 的 `vram_limit_gb` 缺省 | §7.1 自己写明预算随执行机走、迁移后重标；本 feature 是它第一次被真实标定 | 重标须同一提交内同步 F003 侧缺省 |

## 10. 待确认设计问题

无
