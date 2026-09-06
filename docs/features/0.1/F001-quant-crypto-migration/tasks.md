---
kind: feature
id: F001
version: "0.1"
related_features: []
topics: [migration, infra]
doc_kind: tasks
created: 2026-09-06
updated: 2026-09-06
---

# F001：quant-crypto 资产清算迁移 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`。
- 技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
- 实现中若任务顺序或契约失效，先修订三件套，再继续编码。

## 1. 前置条件

- [ ] T001 (`NFR-001`): 旧仓建立只读基线（本地全量备份 + 记录当前 commit） — verify: 备份文件存在 + 旧仓 `git rev-parse HEAD` 记录
- [ ] T002 (`FR-001`): 确认 Docker Desktop、PowerShell 7、Python 3.11 就绪且旧仓 docker-compose 可启动 — verify: `docker compose ps` 全部 Running

## 2. 实现任务

### Phase 1：数据资产迁移

- [ ] T003 (`FR-001`): pg_dump 全库导出旧仓并 restore 进主仓编排的 TimescaleDB — verify: restore 命令退出码 0
- [ ] T004 (`FR-001`, `AC-001`): 逐表执行行数 + 校验和对账并产出 `reports/f001-reconciliation-<date>.json` — verify: `tests/integration/test_f001_row_reconciliation.py`

### Phase 2：代码与服务搬迁

- [ ] T005 [P] (`FR-002`): 采集器四模块迁入 `data_bridge/collector/` 并并入 pyproject 依赖 — verify: `python -c "import"` 冒烟
- [ ] T006 [P] (`FR-003`): 上游 Kronos fresh clone + pin commit + HF 权重下载（或旧仓 models/ 复制） — verify: 权重文件存在 + commit hash 记录于 VENDORED 说明
- [ ] T007 (`FR-003`, `AC-002`): kronos-signal 薄壳迁入 `kronos_service/` 并指向新 DB 与上游代码路径 — verify: `tests/integration/test_f001_kronos_smoke.py`
- [ ] T008 [P] (`FR-004`): 风控三件套迁入 `freqtrade_bridge/risk/` — verify: 策略 import 冒烟
- [ ] T009 [P] (`FR-005`): Grafana/Prometheus 配置迁入 `monitoring/` 且数据源指向新 DB — verify: 容器启动无配置错误
- [ ] T010 [P] (`FR-006`): docker-compose/.env 模板/verify 脚本迁入 `deployment/`（.env 人工搬运密钥，不进 git） — verify: `docker compose config` 无报错

### Phase 3：全链路验证

- [ ] T011 (`FR-002`, `AC-003`): 采集器单交易对冒烟 + 幂等复跑 — verify: `tests/integration/test_f001_collector_smoke.py`
- [ ] T012 (`FR-004`, `AC-004`): Freqtrade dry-run 启动并确认风控钩子与监控面板 — verify: `tests/integration/test_f001_dryrun_monitoring.py`
- [ ] T013 (`FR-006`, `AC-005`): 扩展并运行 deployment/verify.ps1 全链路检查 — verify: `deployment/verify.ps1` 退出码 0

## 3. 验证与验收任务

- [ ] T014 (`AC-001`, `AC-002`, `AC-003`, `AC-004`): 本地运行全部集成测试 — verify: `python -m pytest tests/integration -q`
- [ ] T015 (`NFR-002`): 确认全部脚本在 PowerShell 7 下无路径/编码错误 — verify: T013 附带输出无乱码
- [ ] T016 (`AC-005`): 运行项目统一质量门 — verify: `python tools/verify.py`
- [ ] T017: 回写 spec 验收证据、BACKLOG 状态与 docs/05 清单勾选 — verify: `python tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T001 -> T003`：备份基线先行。
- `T003 -> T004`：对账依赖 restore 完成。
- `T005 -> T011`、`T006 -> T007 -> T012`：冒烟依赖搬迁完成。
- `T005/T006/T008/T009/T010 [P]`：互相可并行（不同目录、无共享状态），但均依赖 T002。
- `T013 -> T014 -> T017`：验收链顺序执行。

## 5. 明确后移

- TimescaleDB 阶段 B（纯 Parquet 化）→ 后续独立 feature：属架构演进，不属迁移范围。
- Parquet 湖导出与 DuckDB 取数层 → F002：数据桥属 M1 范围。
- 宇宙扩容到 30~50 对 → F002/M1：依赖迁移完成的采集管线。
