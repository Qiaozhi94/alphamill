---
kind: feature
id: F010
version: "0.2"
related_features: [F003, F004, F009]
topics: [kronos, gpu, runtime, cuda, m2]
doc_kind: design
created: 2026-09-20
updated: 2026-09-21
---

# F010：Kronos GPU 推理基座 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`
- **PRD / Architecture / System Design**：架构 §7.1（显存预算 ≤3GB 常驻 / ≤6GB 夜槽、GPU 基座前置条）
- **ADR / 上游 Contract**：ADR-0002；F003 分支上 `mining` extra 的 CUDA 构建约定（torch ≥2.7、覆盖 Blackwell sm_120；未合入 main，其 `cu128` 示例与本设计的 pin 不兼容，见 §9）
- **实现约束**：
  - **默认面不可动**：本 feature 不改动 `deployment/docker-compose.yml` 与 `.env.example`（F009 T013 的端口改动归 F009）；不带构建参数时 torch 安装命令（版本 + 索引）与落地前等价；
  - `FROM mock AS real` 的派生关系不得破坏（F004 变异门之一）；
  - 模型目录 `:ro`、DB 依赖、端口暴露面不得放宽；
  - 开发机无 NVIDIA、CI 无 GPU——两者只跑单元层；集成与 GPU 断言一律执行机取证（机器边界）。

## 1. 技术概要与影响面

GPU 面是**一个叠加层**，不是散在默认文件里的一组开关：CUDA 构建参数、`KRONOS_DEVICE: cuda`、nvidia 设备预留、GPU 版 healthcheck 四项全部写在 `deployment/docker-compose.gpu.yml`，执行机以 `-f docker-compose.yml -f docker-compose.gpu.yml` 叠加启用。四项同处一个文件，就不会出现"装了 CUDA wheel 但没申请设备"或"申请了设备但 healthcheck 还在比 cpu"这类半吊子组合。

为什么不用变量开关：compose 插值删不掉 `deploy.resources.reservations.devices` 块——`count: ${KRONOS_GPU_COUNT:-0}` 渲染后 `count` 字段消失（语义变为"全部 GPU"），无 NVIDIA 的机器起容器即报 `could not select device driver "nvidia" with capabilities: [[gpu]]`（2026-09-21 开发机 Docker Compose v5.5.1 实测，文档检视 R1-001）。

- 前端：不适用。
- 后端 / API：**两处小改**，都在 `kronos_real.py`：① 设备解析的严格分支（§5）；② 启动日志一行（TR-001）。`/health` 字段与语义不变。
- 存储 / Migration：不适用。
- Runtime / Agent Adapter：`deployment/kronos-service.Dockerfile`（`real` 目标的 torch 安装参数化）、`deployment/docker-compose.gpu.yml`（新增）。
- Event / Evidence：启动日志增设备与 CUDA 版本（TR-001）；显存标定证据进 spec §6。
- 文档 / 配置：`docs/alphamill-integration.md` 增执行机 GPU 启动命令；架构 §7.1 的 GPU 基座前置条在本 feature 收口时改写为"已落地"；若实测显存超预算，§7.1 时段表对应行同步重标。
- **跨 Feature**：F009 的 `tests/integration/test_f009_vram_release.py` 解除 xfail；F004 契约测试只迁移 Dockerfile 段（FR-005）；F009 T013 同改 F004 测试文件的端口段（tasks §4 的基线规则）。

## 2. 架构与模块边界

```text
默认路径                               GPU 路径（执行机显式叠加）
────────                               ──────────────────────────
docker-compose.yml                     docker-compose.yml + docker-compose.gpu.yml
  build.args: 无 → ARG 缺省 = CPU wheel     build.args: TORCH_INDEX_URL=…/cu130
  KRONOS_DEVICE: cpu                       KRONOS_DEVICE: cuda
  无设备预留                                deploy…devices: nvidia × 1
  healthcheck: device == 'cpu'             healthcheck: device 以 'cuda' 开头
        │                                          │
        └──────────► kronos_real._resolve_device() ◄┘
                      显式 cuda + 拿不到 cuda → 抛错（启动与 restore 共用）
                               │
                        /health.device（实际值）
```

- **单一配置处**：GPU 面四项只在 override 文件出现；默认文件对 GPU 一无所知。
- **服务代码只加一道闸**：设备解析集中到一个函数，启动 eager load 与 F009 `restore` 的重载都经过它，不另开第二条加载路径。
- **失败可见优先于可用**：显式要求 cuda 而拿不到时抛错，由 F004 已建好的"加载失败 → `SystemExit(1)`"路径转成非零退出，不加任何回落分支。

## 3. 数据模型与 Migration

不适用：无持久化实体。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

不新增端点。`/health` 字段与语义不变，`device` 仍是**实际**加载设备。

**构建参数**（Dockerfile `ARG`，缺省 = 当前字面量）：

| 参数 | 缺省 | GPU 取值（override 文件给出） | 作用 |
|---|---|---|---|
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | `https://download.pytorch.org/whl/cu130` | torch wheel 来源 |
| `TORCH_VERSION` | `2.14.0` | `2.14.0`（不覆盖，CPU/GPU 同版本） | torch 版本 |

版本依据（2026-09-21 实查 download.pytorch.org，R1-002）：`cu128` 索引的 cp311 最高为 `2.11.0`；`2.14.0` 仅有 `+cu130` / `+cu132`。选 `cu130`：宿主驱动要求较 `cu132` 低，且同版本避免 CPU/GPU 镜像行为分叉。宿主驱动须满足 CUDA 13.0 最低要求（R580 系列及以上，以 NVIDIA 兼容表为准），由 T002 在执行机核验；`torch.cuda.get_arch_list()` 须含 `sm_89`（当前 RTX 4060）与 `sm_120`（迁移目标）。

**override 文件契约**（`deployment/docker-compose.gpu.yml`，只覆盖 `kronos-signal-real`）：

| 项 | 取值 | 说明 |
|---|---|---|
| `build.args.TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cu130` | 与上表同源 |
| `environment.KRONOS_DEVICE` | `cuda` | 显式设置 → 触发严格分支 |
| `deploy.resources.reservations.devices` | `driver: nvidia`、`count: 1`、`capabilities: [gpu]` | 不用 `privileged: true` |
| `healthcheck.test` | `model_loaded is True` 且 `device.startswith('cuda')` | 覆盖默认文件的 `== 'cpu'` 判据 |

override 不得改动端口、卷、`restart`、`depends_on`——这些仍由默认文件唯一定义（NFR-003）。

**启动命令**（执行机）：`docker compose -f deployment/docker-compose.yml -f deployment/docker-compose.gpu.yml --profile kronos-real up -d --build kronos-signal-real`，写入 `docs/alphamill-integration.md`。

### Event / Trace Contract

启动日志增一行（TR-001）：实际解析设备 + `torch.version.cuda`（CPU wheel 下为 `None`）。让"以为在 GPU 上、实际在 CPU 上"在日志里一眼可见，而不是等到显存读数不动才发现。

## 5. Runtime、Workflow 与并发

不引入新的并发路径。运行时流程：

```text
compose up（叠加 GPU override）
  → 守护进程按预留分配 NVIDIA 设备（无 nvidia 运行时 → 守护进程直接拒绝，容器不启动）
  → lifespan: real_mode_startup() 预检资产 → eager_load() → _load_predictor()
      → _resolve_device(torch):
          KRONOS_DEVICE 未设置        → 既有宽松语义：可用则 cuda:0，否则 cpu（开发机）
          显式 cpu                    → cpu
          显式 cuda* ∧ torch.version.cuda 为空 → 抛错「镜像是 CPU wheel」
          显式 cuda* ∧ not is_available()      → 抛错「容器内无可用 CUDA 设备」
          显式 cuda* ∧ 可用                    → cuda:0
      → 抛错 → real_mode_startup 捕获 → SystemExit(1)，restart: "no" 保持失败态
  → healthcheck: model_loaded=true ∧ device 以 cuda 开头 → 就绪
F009 restore → 重载 → 同一 _load_predictor() → 同一 _resolve_device()
```

**关键设计点**：现有 `_load_predictor()` 在 `device_request` 以 cuda 开头但不可用时**静默回落 cpu**（`kronos_real.py:175-179`）。只在启动预检里堵不够——F009 `restore` 的重载同样走 `_load_predictor()`，会绕过启动预检（文档检视 R1-005）。因此把判断收进 `_load_predictor()` 调用的 `_resolve_device()`：

- **"显式"的判据**：`os.environ` 中存在 `KRONOS_DEVICE`（区别于代码缺省值 `"cuda"`）。默认 compose 显式给 `cpu`，override 显式给 `cuda`，开发机直接跑服务时通常不设——保留了开发机上的宽松回落，又让编排出来的实例严格；
- **不另设判据变量**：healthcheck 判据写在各自 compose 文件里、与同文件的 `KRONOS_DEVICE` 相邻，不再有独立的 `KRONOS_HEALTH_DEVICE_PREFIX` 可以和设备配置不一致（R1-004）；
- healthcheck 的前缀比对是第二道网：即使加载闸被绕过，报 `cpu` 的实例也不会被判就绪。

## 6. UI 与可观测性

- 页面：不适用。
- 日志：TR-001 的启动行；严格分支的两条抛错文案（CPU wheel / 无设备）须可在 `docker logs` 中检索；其余沿用 F004。
- 指标：不新增口径载体（ADR-0005）。显存读数由 `nvidia-smi` 在取证时读取，不常驻采集。
- 运维可见性：`docker logs quant-kronos-signal-real | head` 应当一眼看出跑在哪个设备上。

## 7. 失败、恢复、安全与兼容

- **校验与失败映射**：

  | 条件 | 行为 |
  |---|---|
  | 叠加 override 但宿主无 nvidia 容器运行时 | 守护进程拒绝设备请求，容器不启动（可见，但**不是** AC-004 的证据） |
  | 显式 `KRONOS_DEVICE=cuda`，镜像是 CPU wheel | `_resolve_device` 抛错 → `SystemExit(1)`，`restart: "no"` 保持失败态 |
  | 显式 `KRONOS_DEVICE=cuda`，容器内无可用设备 | 同上 |
  | F009 restore 时 CUDA 不可用 | `_resolve_device` 抛错 → 按 F009 design §7 的既有落点返回 `E_UNAVAILABLE`、`desired` 回落 `stopped`，不回落 cpu（`desired=running` 时 `/predict` 的惰性加载同样经过此闸） |
  | 模型资产缺失 | 预检失败（F004 既有） |
  | CUDA wheel 与宿主驱动不匹配 | torch 初始化抛错 → 启动失败可见，不吞异常 |
  | 显存不足以加载模型 | 加载抛错 → 启动失败可见 |
  | 只用默认 compose 文件 | 与落地前一致（CPU 路径） |

- **重启与恢复**：沿用 F004（`restart: "no"`，失败不自愈以免掩盖配置错误）。
- **权限 / 凭据边界**：GPU 直通不放宽既有边界——模型目录仍 `:ro`，不新增暴露端口，不引入特权容器（设备预留走 `deploy.resources.reservations.devices`，不用 `privileged: true`）；override 不覆盖端口/卷/`restart`/`depends_on`。
- **Windows / POSIX / 版本兼容**：目标平台是执行机 WSL2 + docker-ce（非 Docker Desktop）。WSL2 的 GPU 直通与原生 Linux 有差异，是本 feature 的主要未知数——T002 先核验容器运行时、驱动版本与空载可用显存，再动配置。显存读数不依赖 GPU 进程列表。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | unit | `tests/unit/test_f010_build_args_contract.py` | Dockerfile `real` 段有 `ARG TORCH_INDEX_URL` / `ARG TORCH_VERSION`，缺省值等于落地前字面量，`pip install` 行引用这两个参数；**变异证明**：改任一缺省值即判红 |
| `AC-002` | unit | `tests/unit/test_f010_compose_gpu_contract.py` | 默认文件 `kronos-signal-real` 块含 `KRONOS_DEVICE: cpu`、无 `devices:`、无 GPU 变量插值；override 含 `driver: nvidia`、`count: 1`、`KRONOS_DEVICE: cuda`、`whl/cu130`，且不含 `ports`/`volumes`/`restart`/`privileged`；**变异证明**：往默认文件加 `devices:` 块、删 override 的 `count` 即判红。纯文本断言，不调 docker |
| `AC-003` | unit | 同上 | override healthcheck 含 `model_loaded') is True` 且 `startswith('cuda')`；**变异证明**：判据写回 `== 'cpu'`、删 `model_loaded` 条件即判红 |
| `AC-004` | unit + integration（执行机） | `tests/unit/test_f010_device_strict.py`；`tests/integration/test_f010_gpu_runtime.py` | 单元：monkeypatch 假 torch，显式 `KRONOS_DEVICE=cuda` × {`version.cuda=None`, `is_available()=False`} 两例 `_load_predictor` 抛错、`real_mode_startup` 抛 `SystemExit`；未设置 `KRONOS_DEVICE` 时仍回落 cpu；**变异证明**：删严格分支即判红。集成（执行机）：不叠加设备预留但 `KRONOS_DEVICE=cuda` 起容器 → 非零退出、日志含严格分支文案、`/health` 不可达 |
| `AC-005` | unit | `tests/unit/test_f004_compose_profile_contract.py` + `tests/unit/test_f010_compose_gpu_contract.py` | F004 全部既有变异迁移后仍判红；默认镜像 `import torch` 仍判红 |
| `AC-006` | integration（执行机） | `tests/integration/test_f010_gpu_runtime.py` | 容器内 `torch.cuda.is_available()` 为真；`/health` 报 `device` 以 `cuda` 开头、`model_loaded=true`；启动日志含设备与 CUDA 版本 |
| `AC-007` | integration（执行机） | 同上 | `/predict` 返回 `source=kronos`；`nvidia-smi` 已用显存相对基线上升 |
| `AC-008` | 真实环境（执行机） | 同上 + 证据归档 | 常驻显存峰值与 ≤3GB 对照；超出时架构 §7.1 白天行已重标 |
| `AC-009` | 真实环境（执行机，跨 Feature） | `tests/integration/test_f009_vram_release.py` | 移除 `xfail(strict=True)` 后真实通过：显存下降且卸载后整卡可用显存达到训练预算 |

补充纪律：

- 单元层（AC-001/002/003/004 单元部分/005）在开发机与 CI 全绿是硬要求——它们保护的正是"默认面不变"与"不静默回落"；
- 为什么 AC-004 不在开发机做集成：叠加 override 后守护进程会先拒绝设备请求，容器根本不启动，严格分支没被执行也会"通过"（R1-003）；而且开发机按机器边界不跑集成。严格分支的证伪放在单元层，集成层在执行机以"不挂预留 + 显式 cuda"触发；
- `docker compose config` 渲染比对作为执行机上的补充证据，不作为单元门禁（CI 不保证有 docker）；
- AC-004 集成部分与 AC-006/007/008/009 一律执行机取证，证据记录 hostname / GPU 型号 / 读数（SOP §3）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 升级现有实例 vs 新建 GPU 实例 | 升级 `kronos-signal-real`，默认文件 + GPU override 区分 | 实例名是架构 §7.1 契约的一部分，改名等于改契约并波及 F009/F003 客户端 | 需要 CPU/GPU 并存时再谈第三个 profile |
| GPU 面用变量开关还是 override 文件 | **override 文件** | 插值删不掉设备预留块（R1-001 实测）；四项配置同处一文件（R1-004）；本 feature 不改动默认文件，F004 compose 段断言无需迁移 | — |
| torch 版本与 CUDA 索引 | `2.14.0` 不变，GPU 用 `cu130` | `2.14.0` 无 `cu128` 包（R1-002）；同版本避免 CPU/GPU 分叉 | F003 `mining` 注释的 `cu128` 示例由 F003 在其分支同步 |
| 静默回落怎么堵 | 严格分支放进 `_load_predictor()` 调用的 `_resolve_device()`，只对**显式**设置的 `KRONOS_DEVICE` 生效 | 启动与 F009 restore 共用一个入口，任何重载都绕不开（R1-005）；未设置时的宽松回落对开发机仍合理 | — |
| GPU 默认开/关 | 默认关 | 开发机 AMD iGPU、CI 无 GPU，默认开会推翻本仓绝大多数门禁的运行前提 | 执行机以 `-f` 叠加 override |
| F004 断言迁移的无损判据 | 只迁移 Dockerfile 段；"F004 全部既有变异仍判红"作为机器判据（AC-005） | 迁移最容易悄悄丢掉保护；用变异集合而不是人工承诺来证明 | — |
| 与 F009 T013 同改 F004 测试文件 | 各改各段（本 feature 只动 Dockerfile 段）；先合入者为基线 | 两边都要过统一门禁，同文件不同段可机械 rebase（R1-007） | tasks §4 记录 |
| WSL2 GPU 直通的不确定性 | T002 先核验容器运行时、驱动版本与空载可用显存，再动任何配置 | 这是本 feature 唯一真正的未知数；配置改完才发现直通不可用会浪费整轮 | 核验不通过则阻塞点上升为"执行机平台"，回 spec §8 重新裁决 |
| 常驻显存可能超 ≤3GB | 实测对照，超出即重标 §7.1 白天行 | 常驻预算与训练预算（F003 `vram_limit_gb`，缺省 6.0）不是同一量；夜槽已卸载 Kronos，常驻超标不改训练预算（R1-006） | — |
| 卸载后可用显存可能 <6GB | T002 记录空载整卡可用显存；若 <6GB，重标 §7.1 夜槽行并同一提交同步 F003 `vram_limit_gb` 缺省 | WSL2 下 Windows 桌面也占显存，8GB 卡上 6GB 未必物理可得（R1-012） | — |

## 10. 待确认设计问题

无
