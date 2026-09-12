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
- **执行环境**：与 F001 收口态一致（WSL2 + docker-ce；本机无独立显卡，CPU 推理实测 3.4–7.2s/次）
- **实现约束**：`vendor/Kronos`（pin `67b630e`）与 `models/`（391MB + 16MB）不入库，由 F001 既有流程获取

## 1. 技术概要与影响面

给 `kronos-service.Dockerfile` 增一个包含 torch/cpu 的构建目标，compose 用 `profiles: [kronos-real]` 挂一个额外服务，默认 `up` 不触发其构建。

- 后端 / API：无变更（同一份 `kronos_service`）
- 存储 / Migration：无
- Event / Evidence：F001 AC-006 的复跑命令改为 compose 形态
- 文档 / 配置：F001 spec §6 命令回写；`vendor/VENDORED.md` 补容器内路径说明

## 2. 架构与模块边界

沿用 F001 的 `src/alphamill/kronos_service/`，不新增 Python 模块。差异只在镜像层与挂载：容器内 `KRONOS_REPO_PATH=/app/vendor/Kronos`、`KRONOS_MODEL_PATH=/app/models/Kronos-base`。

## 3. 数据模型与 Migration

不适用：本 feature 不触碰数据库与湖。

## 4. 接口、Contract 与 Event

HTTP 契约与 F001 完全一致；唯一可观察差异是 `/health` 的 `model_enabled=true`、`/predict` 的 `source=kronos` 与 `model` 字段回报权重路径。

## 5. Runtime、Workflow 与并发

- 启动：`docker compose --profile kronos-real up -d kronos-signal-real`；默认 profile 不含该服务；
- 端口：真实实例用 8002，与默认 mock 实例的 8001 并存，避免二者互相顶替；
- 并发：单实例，CPU 推理串行，无共享状态。

## 6. UI 与可观测性

无新 UI；`/health` 的 `model_enabled`/`device`/`model_error` 已足以判别实例形态。

## 7. 失败、恢复、安全与兼容

- 权重或 vendor 缺失 → 容器启动即非零退出并打印缺失路径，**不退回 mock**（退回会让 AC-006 假绿）；
- 镜像体积：torch/cpu wheel 约 200MB，仅在启用 profile 时构建（NFR-001）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f001_kronos_smoke.py` | profile 实例 model_enabled=true 且 source=kronos；默认 compose 配置不含 torch 层与权重挂载 |

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 用 compose profile 而非新建服务文件 | 单一 compose 文件，默认不启用 | 避免多份编排入口（F001 的教训：编排必须唯一） | 若 profile 组合变复杂再拆 override 文件 |
| 真实实例走 8002 而非顶替 8001 | 两种形态可并存对比 | mock 实例仍是默认链路的依赖 | 稳定后可评估是否合并 |
| 残余风险：torch 镜像层拖慢 CI | CI 不构建该 profile | profile 未启用时 compose 不解析其构建 | 若 CI 需要则单独 job |

## 10. 待确认设计问题

无
