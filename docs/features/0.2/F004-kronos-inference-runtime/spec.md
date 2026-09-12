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
updated: 2026-09-12
---

# F004：Kronos 真实推理运行时（编排内可复现）

> Owner: Georg | Target: v0.2.x

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` FR3（信号生产）与 M1 运行基座
- **架构来源**：`docs/alphamill-architecture.md` §七（部署拓扑）
- **上游来源**：F001 AC-006（真实推理证据，当前靠仓外手工实例）、F002 检视 F002-Q001（容器化不在数据桥契约内，需独立载体）
- **功能类型**：backend / infra
- **规格模式**：lite
- **变更类型**：ADDED
- **一句话意图**：把 Kronos 真实模型推理纳入 `deployment/` 编排（可选 profile），使 F001 AC-006 由一条手工命令变成编排内可复现的验收，并让 F002 导出的 `signals_log` 能承载真实信号而非 placeholder。

## 1. 问题、目标与非目标

### 问题

compose 的 `kronos-signal` 服务默认 `KRONOS_USE_REAL_MODEL=false`（镜像基于 `python:3.11-slim`，不含 torch，也不挂载 `vendor/Kronos` 与 `models/`）。真实推理只能靠人工在宿主 venv 起一个 8002 实例——F001 AC-006 因此是「留档命令」而非编排内证据；F002 导出的 `signals_log` 内容全是 `source=placeholder`。

### 目标

- `docker compose --profile kronos-real up` 后，真实模型实例在编排内可达且 `/predict` 返回 `source=kronos`；
- F001 AC-006 的复跑不再依赖手工起进程。

### 非目标

- 不改 Kronos 上游代码与 HTTP API 契约（F001 已冻结）；
- 不做 GPU 直通与性能优化（本机无独立显卡，CPU 推理即可满足验收）；
- 不把真实推理设为默认启动项——torch 与权重会让只做数据桥的开发者付出无谓代价。

## 2. 用户场景

### US-001：编排内取得真实信号（Priority: P2）

作为 `量化研究员`，我希望 `用一条 compose 命令拉起真实 Kronos 推理`，以便 `AC-006 与 signals_log 的内容有效性不依赖任何仓外手工步骤`。

**为什么是这个优先级**：F001 已用独立命令留档证据，不阻塞 M1 开工；但 F002 的 signals_log dataset 要有研究价值就需要它。

**独立测试**：新 clone + 权重就位后，`docker compose --profile kronos-real up -d` 再跑 AC-006 命令全绿。

**验收场景**：

1. Given `vendor/Kronos 与 models/ 就位`，when `docker compose --profile kronos-real up -d`，then `/health` 的 `model_enabled=true` 且 `/predict` 返回 `source=kronos`。

## 3. 范围与边界

### 范围内

- `deployment/kronos-service.Dockerfile` 增加 torch/cpu + einops + safetensors 的可选构建目标；
- compose 增 `kronos-real` profile：挂载 `vendor/Kronos` 与 `models/`，`KRONOS_USE_REAL_MODEL=true`；
- F001 AC-006 的复跑命令改为 compose 形态并回写 F001 spec §6。

### 范围外

- 权重与 vendor clone 的获取（F001 已有流程，仍不入库）；
- GPU 直通（见非目标）。

### 边界场景

- 权重或 vendor 缺失：profile 启动即失败并打印缺失路径，不静默退回 mock。

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
- 下游消费者：F002 的 `signals_log` dataset 内容有效性。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| 做成可选 profile 而非默认服务 | 默认编排不含 torch 与权重挂载 | 只做数据桥的开发者不该背 torch 镜像体积 | 若真实信号成为常态再评估默认化 |
| 是否阻塞 F002 done | **待 owner 裁决**（见 §8 Q-001） | F002 只承诺导出管线正确，不承诺内容来自真实模型 | 裁决结果回写 F002 spec §3 |

## 8. 待确认问题

- [ ] Q-001：F004 是否阻塞 F002 done？——AI 建议：不阻塞。F002 的契约是导出管线正确性，`signals_log` 内容质量是数据源问题；把它设为阻塞会让数据桥等一个与它无关的运行时改造。代价是 F002 done 时湖内 signals_log 仍是 placeholder，需在 F002 验收证据里显式记录。待 owner 裁决后关闭
