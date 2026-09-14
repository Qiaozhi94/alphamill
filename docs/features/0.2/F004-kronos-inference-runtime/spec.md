---
kind: feature
id: F004
version: "0.2"
status: draft
gate_version: 1
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: spec
created: 2026-09-12
updated: 2026-09-14
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

**独立测试**：新 clone + 权重就位 + DB 已迁移且目标 exchange/symbol 有 ≥30 根已闭合 1m K 线后，`docker compose -f deployment/docker-compose.yml --profile kronos-real up -d` 再跑 AC-006 命令全绿。

**验收场景**：

1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose -f deployment/docker-compose.yml --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。

## 3. 范围与边界

### 范围内

- `deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标；
- compose 增 `kronos-real` profile：挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`；
- F001 AC-006 的复跑命令改为 compose 形态并回写 F001 spec §6。

### 范围外

- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；
- GPU 直通（见非目标）；
- 消费者路由切换：Freqtrade `KRONOS_SIGNAL_URL` 与 runtime snapshot `-KronosHostUrl` 仍指向 mock `:8001`；真实实例接线由后续评估决定（见 tasks §5）；
- `signals_log` 内容的自动升级：本 feature 只提供真实信号源，不改变写入链路。

### 边界场景

- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock；
- 数据不足：目标 exchange/symbol 少于 30 根已闭合 1m K 线时 `/predict` 无有效输入（服务契约 `limit>=30` 之外还需 DB 有足够行），验收前置见 §7。

## 4. 需求

### 功能需求

### Requirement: 编排内真实推理（`FR-001`）

系统应当提供一个非默认的 compose profile，使真实模型实例在编排内启动并保持 F001 冻结的 HTTP API 契约不变。

#### Scenario: profile 拉起

- GIVEN `vendor/Kronos` 与 `models/` 就位
- WHEN 执行 `docker compose --profile kronos-real up -d`
- THEN `/health` 的 `model_enabled=true`，`/predict` 返回 `source=kronos`

### 非功能需求

- **NFR-001**：默认 `docker compose up` 的行为与镜像体积不受本 feature 影响（profile 未启用时不构建 torch 层）。

## 5. 生命周期与不变量

不适用：一次性运行时改造，无长生命周期状态机。

## 6. 成功与验收

### 成功标准

- **SC-001**：F001 AC-006 可由编排命令复跑（US-001）。

### 验收清单

- [ ] **AC-001** (`FR-001`, `NFR-001`): `--profile kronos-real` 起的实例 model_enabled=true 且 /predict 返回 source=kronos；不带该 profile 时默认编排行为与镜像层不变 — tests: `tests/integration/test_f001_kronos_smoke.py`

## 7. 测试、依赖与决策

### 测试策略

- 复用 F001 的 `test_f001_kronos_smoke.py`（`KRONOS_REQUIRE_REAL_MODEL=1` + `KRONOS_BASE_URL` 指向 profile 实例）。

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
