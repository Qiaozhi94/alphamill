---
kind: feature
id: F004
version: "0.2"
related_features: [F001, F002]
topics: [kronos, inference, deployment]
doc_kind: tasks
created: 2026-09-12
updated: 2026-09-12
---

# F004：Kronos 真实推理运行时 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。

## 1. 前置条件

- F001 已 done：薄壳、`vendor/Kronos` pin 与 `models/` 权重流程成立，AC-006 已有手工命令形态的实测证据。
- spec §8 Q-001（是否阻塞 F002 done）未关闭前，本 feature 不进入 `ready-for-development`。

## 2. 实现任务

- [ ] T001 (`FR-001`): `deployment/kronos-service.Dockerfile` 增加含 torch/cpu + einops + safetensors 的构建目标，默认目标保持现状不变 — verify: 默认 `docker compose build kronos-signal` 的镜像层与改前一致
- [ ] T002 (`FR-001`, `NFR-001`): compose 增 `kronos-signal-real` 服务，`profiles: [kronos-real]`，挂载 `vendor/Kronos` 与 `models/`，端口 8002 — verify: `docker compose config` 不含该服务，`docker compose --profile kronos-real config` 含之
- [ ] T003 (`FR-001`, `AC-001`): 启动 profile 并确认真实推理 — verify: `ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py -q` 全绿
- [ ] T004 (`FR-001`): 回写 F001 spec §6 的 AC-006 复跑命令为 compose 形态，并保留手工形态作为无 docker 时的回退 — verify: `python3 tools/verify.py`

## 3. 验证与验收任务

- [ ] T005 (`AC-001`): 运行项目统一质量门 — verify: `python3 tools/verify.py` 全绿
- [ ] T006: 回写 spec 验收证据与 BACKLOG 状态 — verify: `python tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T002 -> T003 -> T004`：镜像、编排、实测、文档回写顺序执行。
- `T005 -> T006`：验收链顺序执行。

## 5. 明确后移

- GPU 直通与推理性能优化 → 具备独立显卡的运行环境后另立评估，不属本 feature。
