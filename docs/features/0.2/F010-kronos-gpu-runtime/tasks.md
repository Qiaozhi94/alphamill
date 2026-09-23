---
kind: feature
id: F010
version: "0.2"
related_features: [F003, F004, F009]
topics: [kronos, gpu, runtime, cuda, m2]
doc_kind: tasks
created: 2026-09-20
updated: 2026-09-21
---

# F010：Kronos GPU 推理基座 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
- `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
- 全部新测试必须落在 `tests/unit` 或 `tests/integration`。
- **机器边界**（架构 §7.1、`docs/SOP.md` §3）：单元层在开发机与 CI 必须全绿（它们保护的正是"默认面不变"）；GPU 证据一律在执行机 `qiaozhi-lt` 取，记录 hostname 与 GPU 型号。开发机跳过属预期，不算证据也不算失败。
- **默认面红线**：任何一步之后，本 feature 不改动 `deployment/docker-compose.yml` 与 `.env.example`（F009 T013 的端口改动归 F009），不带构建参数时 torch 安装命令（版本 + 索引）与落地前等价；GPU 面只允许出现在 `deployment/docker-compose.gpu.yml`；默认（mock 目标）镜像 `import torch` 全程保持判红。
- **迁移不丢意图**：改 F004 的断言只允许把 Dockerfile 段"收窄为构建参数缺省值断言"，compose 段不动，不允许删除；以 F004 全部既有变异仍判红作为机器判据（AC-005）。
- **失败可见优先**：不得为任何失败路径添加回落分支——设备不可见就让它非零退出。
- **状态写入口唯一**：状态流转经 `scripts/sdd_status.py --dry-run/--advance`，不手改 frontmatter 与派生行。

## 1. 前置条件

- [x] T001 (`FR-001`, `FR-002`): 确认 spec §8 与 design §10 无开放项，且 GPU 面四项（CUDA 构建参数、`KRONOS_DEVICE: cuda`、设备预留、healthcheck 判据）只在 override 契约表一处定义（design §4 两张表逐格核对） — verify: `spec.md` §8、`design.md` §4/§10 — 证据（2026-09-22）：design §4 构建参数表「GPU 取值」列与 override 契约表逐格一致（cu130 / 同版本 2.14.0），spec §8、design §10 无开放项
- [x] T002 (`NFR-005`, `NFR-002`): **先核验再改配置**——在执行机核验：① NVIDIA 容器运行时可用（`docker run --rm --gpus all <cuda-image> nvidia-smi` 可出卡）；② 驱动版本满足 CUDA 13.0 最低要求（R580 系列及以上，以 NVIDIA 兼容表为准）；③ 在该容器内装 `torch==2.14.0` 自 `whl/cu130`，`torch.cuda.is_available()` 为真、`get_arch_list()` 含 `sm_120`（迁移目标），当前卡以实跑一次 GPU 张量运算且与 CPU 结果一致为准（sm_89 不在 cu130 arch list 内，见 design §4 开发期变更）；④ 记录空载整卡可用显存（`nvidia-smi --query-gpu=memory.free`），<6GB 则按 spec §7 风险行进入重标。① 不通过时先装 nvidia-container-toolkit 并执行 `nvidia-ctk runtime configure --runtime=docker`、重启 docker（运维动作，记录版本）后重测；其余项或装后仍不通过即停下回 spec §8 重新裁决，不得先改配置再试。**预探（2026-09-21，`qiaozhi-lt`）**：① 不通过（Runtimes 仅 `runc`）；② 驱动 616.64；④ 空载 free 7956 MiB — verify: 执行机命令输出归档（hostname / 驱动 / CUDA 版本 / arch list / 空载可用显存） — 证据（2026-09-23，`qiaozhi-lt`）：① 装 nvidia-container-toolkit 1.20.0-1 + `nvidia-ctk runtime configure --runtime=docker` + 重启 docker → `docker info` Runtimes 含 `nvidia`；`docker run --gpus all nvidia/cuda:13.0.1-base-ubuntu24.04 nvidia-smi` 出卡（RTX 4060 Laptop）；② 驱动 616.64（≥ R580）；③ 离线装 `torch==2.14.0+cu130`：`cuda=13.0`、`is_available=true`、`get_arch_list()=[sm_75,80,86,90,100,120]`（**含 sm_120，不含 sm_89**）、`capability=(8,9)`，GPU 矩阵乘与 CPU 结果一致（-2041.476）、显存分配 10.1 MiB——判据据此变更（见本行下方记录）；④ 空载 free 7956 MiB（≥ 6GB 训练预算）。**取包路径**：cu130 索引把 NVIDIA 依赖指向 `pypi.nvidia.com`，经本机代理下载其大文件连续 4 次失败（断开/截断致 sha256 不符/读超时）；改用清华 PyPI 镜像一次成功（29 wheel / 2.9GB，pip 逐个校验）→ Dockerfile 增 `ARG TORCH_EXTRA_INDEX_URL`（缺省空串），GPU override 传镜像地址

## 2. 实现任务

### Phase 1：参数化与 GPU override（默认面不动）

- [x] T003 (`FR-001`, `AC-001`): Dockerfile `real` 目标把 torch 的 wheel index 与版本改为 `ARG`，缺省值等于当前字面量；保留 `FROM mock AS real` 派生关系 — verify: `tests/unit/test_f010_build_args_contract.py` — 证据（2026-09-22）：red: `test_f010_build_args_contract.py` 10 failed（Dockerfile 未参数化）→ green: 10 passed；`ARG` 声明在 `FROM mock AS real` 之后（stage 作用域，另有挪到全局即红的用例）
- [x] T004 (`FR-002`, `FR-003`, `AC-002`, `AC-003`): 新增 `deployment/docker-compose.gpu.yml`，只覆盖 `kronos-signal-real` 的四项加独立镜像标签（`image: alphamill/kronos-signal-real:gpu`，与默认 CPU 构建互不覆盖；`build.args.TORCH_INDEX_URL=…/cu130`、`KRONOS_DEVICE: cuda`、nvidia × 1 设备预留、`startswith('cuda')` healthcheck），不碰端口/卷/`restart`/`depends_on`；**默认 compose 与 `.env.example` 不改**；执行机启动命令写入 `docs/alphamill-integration.md` — verify: `tests/unit/test_f010_compose_gpu_contract.py` — 证据（2026-09-22）：red: `test_f010_compose_gpu_contract.py` 15 failed（override 缺失，默认面 4 条本就绿）→ green: 19 passed；执行机 `docker compose -f … -f docker-compose.gpu.yml config` 渲染确认 target/端口/`:ro`/`restart`/`depends_on` 继承默认文件、GPU 五项生效（补充证据）；启动命令写入 `docs/alphamill-integration.md` §七
- [x] T005 (`FR-005`, `AC-005`): 迁移 F004 契约测试的 **Dockerfile 段**——`torch==2.14.0` 与 CPU wheel 索引两条字面量断言收窄为"`ARG` 缺省值等于该字面量且 `pip install` 引用该参数"，对应变异条目改写为"改 `ARG` 缺省值"；compose 段断言（`KRONOS_DEVICE: cpu`、healthcheck `== 'cpu'`）原样保留；F004 全部既有变异一条不删。**同文件并行**：F009 T013 改同一文件的端口段——本任务不碰端口段，先合入者为基线，后合入者 rebase — verify: `tests/unit/test_f004_compose_profile_contract.py` — 证据（2026-09-22）：T003 后 F004 Dockerfile 段 3 条红（预期顺序红）→ 迁移后 27 passed；Dockerfile 变异 5→6 条（改 pin 缺省 / 改索引缺省 / 删索引引用），compose 段未改，无删除

### Phase 2：失败可见与可观测

- [x] T006 (`FR-004`, `NFR-004`, `AC-004`): 把设备解析抽成 `_resolve_device()` 并由 `_load_predictor()` 调用（启动 eager load、F009 restore 重载、`/predict` 惰性加载共用）——**显式**设置 `KRONOS_DEVICE=cuda*` 时，`torch.version.cuda` 为空或 `is_available()` 为假即抛错并点名原因；`KRONOS_DEVICE` 未设置时保留既有宽松回落。先写单元测试（假 torch，两种拿不到 cuda 的情形 + 未设置回落 + `real_mode_startup` 抛 `SystemExit`）红，再实现转绿；删严格分支必须判红 — verify: `tests/unit/test_f010_device_strict.py` — 证据（2026-09-22）：red: `test_f010_device_strict.py` 7 failed / 2 passed（宽松回落为既有语义）→ green: 9 passed；变异：把 `if not self.device_explicit` 改成 `if True`（删严格分支）→ 5 failed；F004 运行时契约与 `/health` 套件同跑 23 passed
- [x] T007 (`TR-001`, `TR-002`, `AC-006`): 启动日志补一行"实际解析设备 + `torch.version.cuda`"，使"以为在 GPU、实际在 CPU"在日志里一眼可见 — verify: `tests/integration/test_f010_gpu_runtime.py` — 证据（2026-09-23，`qiaozhi-lt`）：启动日志 `[kronos-real] model loaded: device=cuda:0 torch_cuda=13.0`，集成用例逐字断言该行（AC-006 通过）

### Phase 3：执行机落地与取证

- [x] T008 (`FR-002`, `AC-006`): 在执行机以 GPU 参数构建并启动 `kronos-signal-real`，断言容器内 `torch.cuda.is_available()` 为真、`/health` 报 `device=cuda:<n>` 且 `model_loaded=true` — verify: `tests/integration/test_f010_gpu_runtime.py` — 证据（2026-09-23，`qiaozhi-lt`）：GPU 镜像 `alphamill/kronos-signal-real:gpu`（9.7GB）叠加 override 起实例：`/health` 报 `device=cuda:0`、`model_loaded=true`，容器 healthy；容器内 `torch.cuda.is_available()=true`、RTX 4060 Laptop / 驱动 616.64 / torch 2.14.0+cu130、capability (8,9)、arch=[sm_75,80,86,90,100,120]、GPU 实算与 CPU 一致。**构建约束**：默认 builder（bridge 网络）连续 3 次在清华镜像读超时（约 155s 处），改用仓内 `hostnet` builder（host 网络，实测 20MB/s vs 7MB/s）一次成功
- [x] T009 (`US-001`, `AC-007`): 执行机上 `/predict` 产出 `source=kronos` 的真实信号，并记录设备侧已用显存相对基线的上升 — verify: `tests/integration/test_f010_gpu_runtime.py` — 证据（2026-09-23，`qiaozhi-lt`）：`/predict` 返回 `source=kronos` 真实信号；设备侧已用显存 0 MiB（基线）→ 563 MiB
- [x] T010 (`US-003`, `AC-008`): 实测常驻显存峰值并与架构 §7.1 的 ≤3GB 预算对照；**超出即在架构 §7.1 白天行显式重标**（常驻预算与 F003 `vram_limit_gb` 训练预算不是同一量，常驻超标不改后者） — verify: `tests/integration/test_f010_gpu_runtime.py` + 架构 §7.1 时段表 — 证据（2026-09-23，`qiaozhi-lt`）：常驻峰值 **565 MiB**（5 次 /predict 采样均为 565），远低于架构 §7.1 白天行 ≤3GB（3072 MiB）预算 → **不触发重标**，§7.1 数字维持

### Phase 4：解除下游先红态

- [ ] T011 (`FR-006`, `AC-009`): 移除 `tests/integration/test_f009_vram_release.py` 的 `xfail(strict=True)`，在执行机真实通过（显存下降且卸载后整卡可用显存达到训练预算）。若 T002 记录的空载可用显存已 <6GB，先按 spec §7 风险行重标 §7.1 夜槽行并在同一提交同步 F003 `vram_limit_gb` 缺省，再以重标后的预算判定。**前置**：F009 已合入主干（载体与控制面由它交付并保持先红态）；F009 不反向等待本任务（F009 检视 R4-003） — verify: `tests/integration/test_f009_vram_release.py`
- [ ] T012 (`FR-006`): 架构 §7.1 的"GPU 基座前置"条改写为已落地，并把 F009 spec 的 NFR-006 / SC-005 的显存结论前置同步为已解除（F003 T033 只依赖 F009，不在本任务改写范围） — verify: `docs/alphamill-architecture.md` §7.1 + `python3 tools/verify.py`

## 3. 验证与验收任务

- [x] T013 (`AC-001`, `AC-002`, `AC-003`): 运行参数化单元套件并逐条给出变异判红证明（改缺省值 / 把判据写死回 cpu 即红） — verify: `tests/unit/test_f010_build_args_contract.py`、`tests/unit/test_f010_compose_gpu_contract.py` — 证据（2026-09-22）：`test_f010_build_args_contract.py`（6 条缺省值/引用变异 + 全局 ARG 变异）与 `test_f010_compose_gpu_contract.py`（默认面 3 条 + override 13 条 + 越界服务 1 条变异）全部判红，含判据写回 `== 'cpu'`、删 `model_loaded`
- [x] T014 (`AC-005`): 运行迁移后的 F004 契约套件，全部既有变异必须仍判红，默认镜像 `import torch` 仍判红 — verify: `tests/unit/test_f004_compose_profile_contract.py` — 证据（2026-09-23）：迁移后 `test_f004_compose_profile_contract.py` 27 passed，Dockerfile 变异 5→6 条（改 pin 缺省 / 改索引缺省 / 删索引引用）、compose 变异 13 条与 dockerignore 变异 2 条一条未删，全部判红；执行机上默认（mock 目标）镜像 `docker run --entrypoint python deployment-kronos-signal:latest -c 'import torch'` → `ModuleNotFoundError: No module named 'torch'`、退出码 1（NFR-001 否证仍成立）
- [x] T015 (`AC-004`): 两层证伪——单元层（开发机/CI）跑 `tests/unit/test_f010_device_strict.py` 并做删严格分支的变异判红；执行机层两例：① `docker run` GPU 镜像 `alphamill/kronos-signal-real:gpu`、**不加 `--gpus`**、`-e KRONOS_DEVICE=cuda` → 无设备分支；② 默认 CPU 镜像 + `-e KRONOS_DEVICE=cuda` → CPU wheel 分支；均断言非零退出、日志含对应文案、`/health` 不可达。**不得**以"开发机叠加 override 被守护进程拒绝"充当证据——那条路径容器从未启动，严格分支没被执行（文档检视 R1-003） — verify: `tests/unit/test_f010_device_strict.py` + 执行机上 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f010_gpu_runtime.py` — 证据（2026-09-23，`qiaozhi-lt`）：单元层 9 passed + 删严格分支变异 5 failed（见 T006）；执行机层两例均 exit=3、未重启、日志含对应文案、`/health` 不可达：① GPU 镜像不加 `--gpus` → `no CUDA device visible`；② CPU 镜像 → `torch is a CPU wheel`。两例均挂真实资产，预检通过后才触发严格分支（非守护进程拒绝）
- [x] T016 (`AC-006`, `AC-007`, `AC-008`): 在执行机取 GPU 证据（CUDA 可用、真实信号、显存上升与峰值对照），记录 hostname 与 GPU 型号 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f010_gpu_runtime.py` — 证据（2026-09-23，`qiaozhi-lt`）：`ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f010_gpu_runtime.py` → 5 passed, 1 xfailed（T018 旅程待 F009）；hostname=qiaozhi-lt、RTX 4060 Laptop / 驱动 616.64 / torch 2.14.0+cu130
- [ ] T017 (`AC-001`, `AC-002`, `AC-004`, `AC-005`): 运行项目统一质量门 — verify: `python3 tools/verify.py`

### [TEST] 组：层 2 旅程验收轨（必填）

- [ ] T018 [TEST] (`AC-006`, `AC-007`, `AC-009`): 夜槽完整旅程——GPU 常驻（显存 >0）→ F009 `stop` → 显存真实下降且可用显存达训练预算 → 模拟取锁 → `restore` → `/predict` 恢复 `source=kronos`；夹具在 Phase 1 即以红灯立起，收尾在执行机全量执行 — verify: 执行机上 `ALPHAMILL_INTEGRATION=1 KRONOS_CONTROL_URL=http://127.0.0.1:8002 pytest -q tests/integration/test_f010_gpu_runtime.py tests/integration/test_f009_vram_release.py`
- [ ] T019: 回写 spec 验收证据并流转状态——经 `scripts/sdd_status.py --dry-run` 确认门禁后 `--advance` — verify: `python3 tools/validate_spec_lifecycle.py` + `sdd_status.py --dry-run` 输出

## 4. 依赖与并行关系

- `T001 -> T003`：三处参数同源核对通过前不动配置，否则会出现"装了 CUDA wheel 却没申请设备"的半吊子状态。
- `T002 -> T008`：容器运行时可用性是执行机落地的前提；不通过则本 feature 的阻塞点上升为执行机平台。
- `T003 -> T005`：先参数化 Dockerfile，再迁移 F004 的 Dockerfile 段断言——顺序反了会有一轮红。
- `F009 T013 ⇄ T005`（同文件不同段，非阻塞边）：两者都改 `tests/unit/test_f004_compose_profile_contract.py`——F009 改端口段，本任务改 Dockerfile 段；先合入 main 者为基线，后合入者 rebase 并以对方的段为准。
- `T004 -> T006`：override 就位后，"显式 `KRONOS_DEVICE=cuda`"才有真实来源。
- `T006 -> T007`：失败路径先堵住，再补可观测。
- `T003 -> T013`、`T004 -> T013`：参数化单元套件的载体由这两项落盘。
- `T005 -> T014`：迁移后的 F004 套件由 T005 改写。
- `T006 -> T015`：两层失败可见断言都依赖 T006 的严格分支。
- `T008 -> T015`：执行机层两例要用 T008 构建出的 GPU 镜像（`alphamill/kronos-signal-real:gpu`），且共用 `tests/integration/test_f010_gpu_runtime.py` 载体（R2-003 引入的依赖）。
- `T007 -> T008 -> T009 -> T010`：日志就位 → GPU 起得来 → 真实信号 → 显存标定，严格串行。
- `T010 -> T016`：峰值对照完成后才谈得上归档执行机证据。
- `T010 -> T011`：显存预算标定之后，"可用显存达到训练预算"这个判据才有确定的阈值。
- `T011 -> T012`：先解除先红态，再把架构与两个下游 feature 的前置线改写为已解除。
- `T013 -> T017`、`T014 -> T017`、`T015 -> T017`、`T016 -> T017`：各条测试轨全绿后跑统一质量门。
- `T011 -> T018`：旅程轨的 F009 载体由 T011 解除先红态后才可执行。
- `T012 -> T018`、`T016 -> T018`：契约与证据都就位后，旅程轨做收尾全量执行。
- `T017 -> T019`、`T018 -> T019`：质量门与旅程轨都绿才流转状态。

## 5. 明确后移

- 执行机平台迁移（`qiaozhi-lab`、原生 Ubuntu、Blackwell sm_120）→ 独立迁移 Feature：本 feature 选定的 `cu130` 已覆盖 sm_120（T002 以 `get_arch_list()` 核验；当前卡 sm_89 走二进制兼容），不做迁移本身。
- F003 `mining` extra 注释中的 `cu128` 索引示例（对 torch ≥2.12 已无对应 wheel）→ 由 F003 在 `feat/F003-alphagen-vendor` 分支同步为 `cu130`，本 feature 不跨分支修改；同步项已登记在 BACKLOG 活跃表下方的「F010 → F003 同步项」。
- 生命周期控制面端点 → `F009`：本 feature 为其提供可取证的显存基座，不实现端点。
- 挖掘侧编排与夜槽取锁 → `F003`（T025 / T033）。
- 多 GPU、MIG/MPS 切分、显存硬配额 → 不在 M2 范围：显存预算仍由 F003 的单槽仲裁在应用层执行。
- 推理性能优化（批处理、半精度、编译）→ 独立 Feature：本 feature 只求"跑在 GPU 上且占显存可观测"，不求快。
- Kronos 常驻实例的多副本与高可用 → 不做：单卡单实例是架构 §7.1 的既定前提。
