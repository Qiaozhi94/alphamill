---
kind: feature
id: F004
version: "0.2"
status: done
gate_version: 1
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-18
---

# F004：Kronos 真实推理运行时（编排内可复现）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` M0（自包含运行基线：Kronos 服务在编排内健康）、FR1.2（`signals_log` 进入不可变快照）与 FR5（运行链：信号服务的运行时载体）；FR3（证据评测与验证）仅为下游关系——F004 为评测提供可复现的真实 Kronos 信号源，不实现评测本身
- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）、§7.1（机器边界）
- **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）
- **功能类型**：backend / infra
- **规格模式**：lite
- **变更类型**：ADDED
- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并在编排内提供可复用的真实信号源；消费者路由切换（Freqtrade 与 runtime snapshot 指向真实实例）不在本 feature 范围（见 §3）。

## 1. 问题、目标与非目标

### 问题

compose 的 `kronos-signal` 服务默认 `KRONOS_USE_REAL_MODEL=false`（镜像基于 `python:3.11-slim`，不含 torch，也不挂载 `vendor/Kronos` 与 `models/`）。真实推理只能靠人工在宿主 venv 起一个 8002 实例——F001 AC-006 因此是「留档命令」而非编排内证据；F002 导出的 `signals_log` 内容全是 `source=placeholder`。

### 目标

- `docker compose -f deployment/docker-compose.yml --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；
- F001 AC-006 的复跑不再依赖手工起进程。

### 非目标

- 不改 Kronos 上游代码与 HTTP API 契约（F001 已冻结）；
- 不做 GPU 推理与性能优化（Kronos 常驻推理的目标机是执行机（当前 `qiaozhi-lt` 的 RTX 4060，架构 §7.1）；本 feature 的编排与契约验收在 CPU 推理上即成立，GPU 直通留给执行机落地时处理）；
- 不把真实推理设为默认启动项——torch 与权重会让只做数据桥的开发者付出无谓代价。

## 2. 用户场景

### US-001：编排内取得真实信号（Priority: P2）

作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 的真实推理证据不依赖任何仓外手工步骤，且真实信号源在编排内可复用`。

**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；F002 的 signals_log dataset 要有研究价值需要可复现的真实信号源（消费者接线见 §3 范围外）。

**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿；容器集成验收在执行机 `qiaozhi-lt` 取证（记录 hostname + `device=cpu`），开发机只跑静态与单元门禁（见 §7）。

**验收场景**：

1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。

## 3. 范围与边界

### 范围内

- `deployment/kronos-service.Dockerfile` 拆 `mock`（保持现状、不含 torch）与 `real` 两个构建目标，compose 两个服务各自显式声明 target；real 目标含 torch CPU wheel + einops + safetensors + huggingface_hub + tqdm（版本与 wheel 来源在 design 锁定）；
- compose 增 `kronos-signal-real` 服务（`profiles: [kronos-real]`）：只读挂载 `vendor/Kronos` 与 `models/`（`:ro`），`KRONOS_USE_REAL_MODEL=true`，host 8002 → container 8001（**F009 T013 起 host bind 收严为 `127.0.0.1:8002:8001`**，原意不变：host 8002 不顶替 mock 的 8001、container 仍是 8001），与 mock 相同的 DB 环境、`depends_on: timescaledb: {condition: service_healthy}` 与 `alphamill` 网络；
- F001 AC-006 的复跑命令改为 compose 形态并回写 F001 spec §6。

### 范围外

- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；
- GPU 直通（见非目标）；
- 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`；真实实例接线由后续评估决定（见 tasks §5）；
- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。
- Kronos 服务生命周期控制面：版本化 `status` / `stop` / `restore` 契约（幂等、可配超时、`E_*` 错误码、显存确认与未部署语义）正文归架构 §7.1，wire 绑定为 HTTP `/lifecycle/*` + `X-Contract-Version`；**契约目标实例为 `kronos-signal-real`（执行机 GPU 实例）**。本 feature 交付的 `kronos-signal`（mock）与 `kronos-signal-real` 均**不含**控制面端点；服务端实现归待分配 feature（BACKLOG「Kronos 服务生命周期端点」，F003 夜槽实测 T033 / AC-010 真实卸载取证前落地）。端点缺失或未部署时 F003 客户端按架构 §7.1 观测→处置决策表记 `offload_not_needed` 或 fail-closed 留在单槽队列，不降级为并行抢卡（F003 design §4；客户端契约测试 `tests/integration/test_f003_kronos_lifecycle.py`）。

### 边界场景

- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock；
- 数据不足：目标 exchange/symbol 少于 30 根已闭合 1m K 线时 `/predict` 无有效输入（服务契约 `limit>=30` 之外还需 DB 有足够行），验收前置见 §7。

## 4. 需求

### 功能需求

### Requirement: 编排内真实推理（`FR-001`）

系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动、完成启动期资产预检与模型加载、串行处理推理请求，并保持 F001 冻结的 HTTP API 契约不变。

#### Scenario: profile 拉起

- GIVEN `vendor/Kronos` 与 `models/` 就位
- WHEN 执行 `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`
- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`

#### Scenario: 缺资产失败关闭

- GIVEN `vendor/Kronos`、模型或分词器任一缺失
- WHEN 启动 profile 实例
- THEN 进程非零退出并在日志打印缺失路径，不退回 mock

#### Scenario: 并发推理串行

- GIVEN 真实实例已就绪
- WHEN 多个 `/predict` 请求并发到达
- THEN 请求按序执行，模型加载至多一次，且无请求并发进入 predictor

### 非功能需求

- **NFR-001**：默认 `docker compose -f deployment/docker-compose.yml up` 的行为与镜像不受本 feature 影响——默认镜像（`mock` 构建目标）不含 torch，profile 未启用时不启动、不构建 real 服务。

## 5. 生命周期与不变量

不适用长生命周期状态机（一次性运行时改造）；三条运行时不变式由测试锁定：

- **失败关闭**：real 模式启动期校验 vendor clone、模型与分词器目录及必需文件；任一缺失或加载失败即非零退出并打印缺失路径，**绝不退回 mock**；
- **串行推理**：进程内模型加载至多一次、推理互斥（进程级锁）；并发请求排队执行，不并发进入 predictor；
- **默认隔离**：未启用 profile 时默认编排不启动 real 服务，默认镜像不含 torch（NFR-001）。

## 6. 成功与验收

### 成功标准

- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。
- **SC-002**：失败关闭与串行推理不变式成立（US-001）。

### 验收清单

- [x] **AC-001** (`FR-001`, `NFR-001`): --profile kronos-real 拉起的实例由目标 compose 服务与 real 构建目标产生（容器身份、只读挂载、`127.0.0.1:8002:8001` 成立——F009 T013 迁移后的形式），且完整运行链（模型 + TimescaleDB）可用：model_enabled=true、/health 的 database 可达、/predict 返回 source=kronos；不带该 profile 时默认编排不启用也不构建 real 服务、默认镜像不含 torch — tests: `tests/unit/test_f004_compose_profile_contract.py`、`tests/integration/test_f004_real_profile.py`
- [x] **AC-002** (`FR-001`): 失败关闭与串行推理——vendor/权重/分词器缺失或加载失败时 real 实例启动即非零退出并打印缺失路径（不退回 mock）；并发 /predict 下模型加载至多一次且推理互斥 — tests: `tests/unit/test_f004_kronos_runtime_contract.py`、`tests/integration/test_f004_real_profile.py`

### 验收证据（2026-09-15）

- **取证机**：执行机 `qiaozhi-lt`（WSL2 + docker-ce），容器内 `torch=2.14.0+cpu`、
  `/health` 的 `device=cpu`（CPU 推理，本 feature 不含 GPU 直通）。
- **T008 验收命令**：`ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1
  KRONOS_BASE_URL=http://127.0.0.1:8002 pytest tests/integration/test_f001_kronos_smoke.py
  tests/integration/test_f004_real_profile.py -q` → **6 passed**（F001 冒烟 3 +
  F004 容器集成 3）。真实实例先经 `docker compose --profile kronos-real up -d
  kronos-signal-real` 拉起，`/health`：`status=ok, model_enabled=true, model_loaded=true,
  device=cpu, database.total_rows=6346061`（latest candle 2026-09-14T17:35Z，lag 74s）；
  `/predict BTC/USDT` → `source=kronos`、`model=/app/models/Kronos-base`、
  `reason=kronos_base_pred_len_12_infer_2.032s`。
- **失败关闭实测**：real 镜像以 `KRONOS_USE_REAL_MODEL=true` + 资产路径指向不存在处运行 →
  uvicorn lifespan 预检失败，打印 `[kronos-real] missing asset: …` + `refusing to start`，
  退出码非零，无可服务的 mock 降级实例（宿主侧同语义实测退出码 3）。
- **默认镜像否证**：mock 目标镜像 `python -c "import torch"` 退出码非零（NFR-001）；
  `docker compose config --services` 默认不含 `kronos-signal-real`、`--profile kronos-real`
  时包含。
- **门禁**（2026-09-15 复核勘正计数）：静态编排/构建契约 26 项——6 组合约断言
  （Dockerfile 目标与依赖 pin、compose 双服务接线、默认隔离、块注释边界、注释剥离
  语义、.dockerignore 白名单）+ 20 项变异（Dockerfile 5、compose 13、.dockerignore 2；
  含整行注释类与 mock real 开关类变异 → 全部判红）；薄壳运行时契约 13 项（失败关闭、
  加载至多一次、推理互斥、lifespan 接线变异可杀、not_enough_data 的 source/model
  不虚标双向、批量信封 source/model 汇总、DeprecationWarning 清零）；收口时全量集成
  `ALPHAMILL_INTEGRATION=1 ALPHAMILL_REAL_LAKE_DIR=<lake> pytest tests/integration -q`
  通过（1 skip 为 F001 AC-006 的显式开关语义，预期行为）。
- **依赖与构建上下文**：集成测试顶层 import 的 requests 显式声明为 dev 依赖并锁范围
  （`requests>=2.32,<3`，纳入 `check_dep_pins`）；仓库根新增白名单式 `.dockerignore`
  （`*` + `!pyproject.toml` + `!README.md` + `!src/`），构建上下文不再携带
  `.git`/`.venv`/`models`/`vendor` 等重资产（docker 构建语义在执行机取证，载体 tasks T013）。
- **实测勘误**：容器集成测试镜像引用采用 compose 默认命名（`<project>-<service>`）解析
  ——buildkit 每次构建生成新 manifest list，容器 `.Image` 摘要在重建后悬空不可 `run`。
- **第二轮容器证据（T013，2026-09-16）**：R002/R004 载体——修复后代码三镜像全量重建 + 容器套件复跑：
  - 构建：`kronos-service`（mock/real 双目标）与 `data-collector` 退出码均 0；构建上下文经
    `.dockerignore` 白名单收敛至 354B / 6.67kB 级（buildkit `transferring context` 实测，
    不含 `.git`/`.venv`/`models`/`vendor` 重资产）——R002 的 docker 语义由此闭环；
  - 容器内 `import alphamill`：三镜像均退出码 0；
  - 套件：`ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1
    KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest
    tests/integration/test_f001_kronos_smoke.py tests/integration/test_f004_real_profile.py -q`
    → **7 passed**（F001 冒烟 3 + F004 容器集成 4，含 compose config 双向断言、缺资产
    exited + 非零退出码、real 全链）；`/health`：`model_loaded=true, device=cpu,
    database.total_rows=6352187`；取证机 hostname=`qiaozhi-lt`；
  - 环境说明：本机 WSL2 mirrored 网络下 docker 默认桥对大流量下载整段卡死（torch 200MB
    流中断），构建须经 host 网络完成（`docker build --network=host` / hostnet 构建器）；
    产物与编排未改，属取证环境适配。

## 7. 测试、依赖与决策

### 测试策略

- **静态编排契约（单元，CI 常绿）**：`tests/unit/test_f004_compose_profile_contract.py`——Dockerfile mock/real 目标与依赖 pin、compose real 服务的 profile/挂载/端口/环境、默认配置不含 real 服务；
- **薄壳运行时契约（单元，CI 常绿）**：`tests/unit/test_f004_kronos_runtime_contract.py`——缺资产启动失败关闭、模型加载至多一次、推理互斥；
- **容器集成（执行机）**：`tests/integration/test_f004_real_profile.py`——构建 real 目标并拉起 profile，校验容器身份（compose 托管 + real 目标 + 只读挂载 + `127.0.0.1:8002:8001`）与完整运行链（模型 + TimescaleDB）：`/health` 的 `database` 可达且 `/predict` 返回 `source=kronos`；缺资产场景非零退出；默认镜像 `import torch` 判红；开关语义与 F001 冒烟一致（未设 `ALPHAMILL_INTEGRATION` 时 skip、设了不可达判红）；
- F001 的 `test_f001_kronos_smoke.py` 保留 HTTP 契约职责（`source` 与 `model_enabled` 自洽、两方向判红），不再单独承担部署形态证明；
- **取证纪律**：容器与集成证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。

### 依赖

- 上游：F001（薄壳、权重流程、AC-006 命令）；
- 下游（非本 feature 承诺）：`signals_log` 内容真实化需消费者路由切换（范围外、后移）；FR3 评测台的真实 Kronos 信号输入在路由完成后成立；
- 外部 / 环境依赖：`vendor/Kronos`（pin `67b630e`）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）；执行机 docker-ce 可构建 torch CPU 镜像；DB 已迁移且目标 exchange/symbol 至少有 30 根已闭合 1m K 线（F001 回填产物）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 做成可选 profile 而非默认服务 | 默认编排不含 torch 与权重挂载 | 只做数据桥的开发者不该背 torch 镜像体积 | 若真实信号成为常态再评估默认化 |
| 是否阻塞 F002 done | **不阻塞**（2026-09-13 owner 裁决，见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 代价已写进 F002 spec §6 限制说明；**F004 落地后 `signals_log` 不会自动升级**——runtime snapshot 与 Freqtrade 仍指向 mock `:8001`，路由切换后移（§3 范围外、tasks §5） |
| 消费者路由（profile 启用时是否切换 Freqtrade / runtime snapshot） | 不接线，显式后移 | 路由切换改变默认链路可用性与跨 feature 契约，需独立评估 | v0.2.x 后续评估（tasks §5） |

## 8. 待确认问题

- [x] Q-001：F004 是否阻塞 F002 done？——**裁决（2026-09-13, owner）：不阻塞**。F002 的契约是导出管线正确性，`signals_log` 的内容质量是数据源问题；把它设为阻塞会让数据桥等一个与它无关的运行时改造。**接受的代价**：F002 done 时湖内 signals_log 仍是 `source=placeholder`，该状态已写进 F002 spec §6 验收清单下方的限制说明，done 时必须在验收证据里如实记录行数与 source 分布，不得含糊带过
