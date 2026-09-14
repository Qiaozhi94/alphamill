---
kind: feature
id: F004
version: "0.2"
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: design
created: 2026-09-12
updated: 2026-09-12
---

# F004：Kronos 真实推理运行时 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`（FR-001 / NFR-001）
- **上游 Contract**：F001 冻结的 Kronos HTTP API（`GET /health`、`GET /predict/{symbol:path}`、`POST /predict_batch`），零改动
- **执行环境**：容器集成与验收在执行机 `qiaozhi-lt`（Win11 + WSL2 + docker-ce，RTX 4060 Laptop 8GB）取证，证据记录 hostname 与 `device=cpu`（本 feature 不做 GPU 直通；CPU 推理实测 3.4–7.2s/次）；开发机 `qiaozhi-gp`/`gp-wsl` 只跑静态编排断言与单元门禁（SOP §3、架构 §7.1）
- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取；`/predict` 数据前置为目标 exchange/symbol 至少 30 根已闭合 1m K 线（F001 回填产物，DB 已迁移）

## 1. 技术概要与影响面

给 `kronos-service.Dockerfile` 拆出 `mock`（保持现状、不含 torch）与 `real` 两个构建目标；compose 两个服务各自显式声明 target，`kronos-signal-real` 用 `profiles: [kronos-real]`，默认 `up` 不启用也不构建该服务。薄壳做三处最小改造：real 模式启动预检、模型 eager load 与进程级推理锁（§5）。

- 后端 / API：无变更（同一份 `kronos_service`）
- 存储 / Migration：无
- Event / Evidence：F001 AC-006 的复跑命令改为 compose 形态
- 文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明

## 2. 架构与模块边界

沿用 F001 的 `src/alphamill/kronos_service/`，不新增模块；差异=镜像层与挂载 + 薄壳三处最小改造（启动预检、eager load、推理锁，见 §5）。real 服务的容器挂载、环境变量与端口契约：

| 项 | real 服务契约 |
|---|---|
| 构建目标 | `target: real`，`profiles: [kronos-real]` |
| 挂载 | `../vendor/Kronos:/app/vendor/Kronos:ro`；`../models:/app/models:ro` |
| KRONOS_REPO_PATH | `/app/vendor/Kronos` |
| KRONOS_MODEL_PATH | `/app/models/Kronos-base` |
| KRONOS_TOKENIZER_PATH | `/app/models/Kronos-Tokenizer-base` |
| KRONOS_USE_REAL_MODEL / KRONOS_DEVICE | `true` / `cpu` |
| 端口 | host `8002` → container `8001`（mock 保持 host `8001`，互不顶替） |

**real 目标的依赖 pin（镜像内）**：`torch==2.14.0`（`--index-url https://download.pytorch.org/whl/cpu`，CPU wheel；与宿主 AC-006 实测同版）+ `einops==0.8.2`、`safetensors==0.8.0`、`huggingface_hub==1.31.0`、`tqdm==4.70.0`——pin 上游直接 import 的最小集（`model/kronos.py` 导入 torch/huggingface_hub/tqdm，`model/module.py` 导入 einops），版本取宿主 AC-006 实测集，以容器内真实权重加载验证后锁定；上游 `requirements.txt` 仅作参考。

## 3. 数据模型与 Migration

不适用：本 feature 不触碰数据库与湖。

## 4. 接口、Contract 与 Event

HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。real 实例在启动预检与 eager load 完成后才对外服务；预检/加载失败即进程非零退出（§7），不产生「enabled 但未加载」的可用中间态。

## 5. Runtime、Workflow 与并发

- 启动：`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 启动序列（real 模式）：进程启动 → **预检**（`KRONOS_REPO_PATH`、模型/分词器目录及必需文件存在）→ **eager load**（一次性加载 Kronos + Tokenizer，放在应用启动钩子、先于接收流量）→ 服务就绪；预检或加载任一失败 → 打印缺失路径/错误并**非零退出**（real 服务 `restart: "no"`，失败态可直接观察，不静默降级）；
- readiness：容器 healthcheck 以 `/health` 的 `model_loaded=true`（且 `device=cpu`）为通过条件；mock 服务保持现状；
- 端口：真实实例用 8002（host）→ 8001（container），与默认 mock 实例的 8001 并存，避免二者互相顶替；
- 并发：单实例单 worker；**进程级锁**保证模型加载至多一次、推理互斥（并发请求排队），无其它共享状态；
- 数据前置：`/predict` 需要目标 exchange/symbol ≥30 根已闭合 1m K 线（DB 已迁移，F001 回填产物）。

## 6. UI 与可观测性

无新 UI；`/health` 的 `model_enabled`/`device`/`model_error` 已足以判别实例形态。

## 7. 失败、恢复、安全与兼容

- 权重、分词器或 vendor 缺失/加载失败 → **启动期**即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；`restart: "no"` 使失败态保持可见；
- 资产只读：`vendor/Kronos` 与 `models/` 以 `:ro` 挂载，容器不写宿主资产；
- 镜像体积：real 目标（torch CPU wheel 约 200MB）仅在启用 profile 时构建；默认镜像（mock 目标）不含 torch，默认编排行为不变（NFR-001）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | 静态契约（unit，CI 常绿） | `tests/unit/test_f004_compose_profile_contract.py` | Dockerfile 有 mock/real 目标且 real 锁定依赖 pin；real 服务 profiles/只读挂载/端口/环境正确；默认 compose 配置不含 real 服务 |
| `AC-001` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | compose 拉起后容器身份成立（compose 托管 + real 目标 + 只读挂载 + 8002:8001）且 `/predict source=kronos`；默认镜像 `import torch` 判红 |
| `AC-002` | 单元 | `tests/unit/test_f004_kronos_runtime_contract.py` | 缺资产/加载失败 → 非零退出且不退回 mock（fake 目录注入）；并发请求加载至多一次、推理互斥 |
| `AC-002` | 容器集成（执行机） | `tests/integration/test_f004_real_profile.py` | 缺资产场景以非零退出结束并在日志保留缺失路径；不产生可服务的 mock 降级实例 |
| HTTP 契约（F001 AC-002/006 复用） | integration | `tests/integration/test_f001_kronos_smoke.py` | 保留：`source` 与 `model_enabled` 自洽（两方向判红）；不承担部署形态证明 |

- 容器集成测试遵循 F001 冒烟同款开关语义：未设 `ALPHAMILL_INTEGRATION` 时 skip；设了开关而服务/容器不可达时判红，不得以 skip 代替证据。
- 每道新门禁（静态契约、容器集成）做一次变异验证：改 target、删依赖 pin、放开 `:ro` 必须判红。
- 集成/容器证据必须在执行机 `qiaozhi-lt` 采集并记录 hostname 与 `device=cpu`（SOP §3、架构 §7.1）；开发机只跑静态与单元门禁，开发机 skip 不算证据。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 用 compose profile 而非新建服务文件 | 单一 compose 文件，默认不启用 | 避免多份编排入口（F001 的教训：编排必须唯一） | 若 profile 组合变复杂再拆 override 文件 |
| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |
| 串行推理用进程级锁而非多 worker | uvicorn 单 worker + 进程级锁 | CPU 推理本身串行；多 worker 无收益且破坏「加载至多一次」 | 若未来上 GPU 再评估批量吞吐 |
| 依赖 pin 取宿主 AC-006 实测版本 | torch 2.14.0（CPU index）+ einops 0.8.2 / safetensors 0.8.0 / huggingface_hub 1.31.0 / tqdm 4.70.0 | 与已实测通过的宿主环境一致；上游 requirements 仅参考 | 容器内真实权重加载验证通过后锁定 |
| 残余风险：torch 镜像层拖慢 CI | CI 不构建也不启用 real 目标；默认镜像不含 torch 由静态门禁锁定 | profile 未启用时 compose 不构建该服务 | 若 CI 需要 real 构建则单独 job |

## 10. 待确认设计问题

无
