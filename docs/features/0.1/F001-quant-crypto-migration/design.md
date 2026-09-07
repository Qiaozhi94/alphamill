---
kind: feature
id: F001
version: "0.1"
related_features: []
topics: [migration, infra]
doc_kind: design
created: 2026-09-06
updated: 2026-09-07
---

# F001：quant-crypto 资产清算迁移 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`（FR-001..006 / NFR-001..002）
- **PRD / Architecture / System Design**：`docs/alphamill-prd.md` M0；`docs/alphamill-architecture.md` §五、§七；`migration-plan.md` 全文（本目录）
- **ADR / 上游 Contract**：Kronos HTTP API 契约以旧仓 `kronos-signal/server.py` 现行为准（不新增不修改）
- **执行环境（2026-09-07 实测钉死）**：Windows 11 宿主 + WSL2（Ubuntu 26.04，内核 6.18.33.2-microsoft-standard-WSL2）；docker-ce 29.1.3 + compose v2.40.3（非 Docker Desktop）；PowerShell 7 经 apt 安装于 WSL2（旧仓 verify.ps1 资产沿用，AC-005 语义不变）；GPU：RTX 4060 需 Windows 宿主驱动 + WSL 直通（当前 `nvidia-smi` 不可见，tasks T003 前置检查），未就绪时 AC-002 冒烟允许 CPU 推理回退；旧仓双现场钉死（2026-09-07 实证）：①代码副本 `/root/projects/quant-crypto`（origin `git@github.com:Qiaozhi94/quant-crypto.git`，HEAD `d94f94f`，在本开发机 qiaozhi-gp）；②运行现场＝数据源 **qiaozhi-lt**（用户另一台 Windows 工作机，Tailscale `100.98.228.125`；本开发机实为 qiaozhi-gp，勿混淆）之 `D:\Projects\quant-crypto`——含 `.env` 凭据与 Docker 命名卷 `quant-crypto_timescale_data`（容器 `quant-timescaledb`，归档停用态；实测临时启动后 ohlcv_1m **6,504,359 行**、11 张公有表、5 个连续聚合，查毕已停回）。数据迁移经 SSH 流式 pg_dump（`docker exec` + SSH 重定向）：实测 Tailscale 直连 5432 被 Windows 防火墙拦截而 SSH 22 通，故不依赖开放 5432，见 T004
- **实现约束**：旧仓只读（NFR-001）；迁移期间不得中断旧仓服务直至对账通过

## 1. 技术概要与影响面

三步走：① 数据卷按 pg_dump/restore 迁移（首选可校验方案）并逐表对账；② 代码目录按 migration-plan.md §一 清单物理搬迁并并入主仓 pyproject 依赖；③ Kronos 上游化（clone pin + HF 权重 + 薄壳改造路径）后全链路 verify。

- 前端：不适用（无 UI 变更，Grafana 仅改数据源）
- 后端 / API：src/alphamill/kronos_service/ 迁入；API 契约不变
- 存储 / Migration：TimescaleDB 数据卷迁移 + 行数/校验和对账（本 feature 核心）
- Runtime / Agent Adapter：无
- Event / Evidence：迁移对账结果写入 `reports/`（manifest 风格 JSON）
- 文档 / 配置：migration-plan.md 清单项勾选；deployment/verify.ps1 扩展

## 2. 架构与模块边界

迁移后模块边界与 `docs/alphamill-architecture.md` 目录设计一致（目录约定已拍板：Python 包一律 `src/alphamill/<module>/`，非 Python 资产留在仓根）：`src/alphamill/data_bridge/collector/`（采集）与 `src/alphamill/data_bridge/`（导出，F002 实现）分离；`src/alphamill/kronos_service/` 只做 DB→推理→信号，不含业务策略；`src/alphamill/freqtrade_bridge/risk/` 只被策略模板 import；`monitoring/`、`deployment/` 为非 Python 资产留在仓根，`deployment/` 是唯一编排入口。依赖方向单向：deployment → services → data。旧仓迁移后仅作为只读历史参照，任何运行时路径不得指向旧仓。

## 3. 数据模型与 Migration

- 方案：`pg_dump -Fc` 全库导出 → 新容器 `pg_restore`；表级 `SELECT COUNT(*)` + `SUM(hashtext(rostertuple))` 式校验和对账。**对账口径（唯一权威定义，spec FR-001 / AC-001 与 design §8 引用此处）**：逐表覆盖旧库实测全部 11 张公有表（2026-09-07 qiaozhi-lt 容器内 `pg_tables` 实查）：ohlcv_1m（6,504,359 行）、ohlcv_quality_flags、衍生品三表（derivatives_funding_rates / derivatives_mark_index_basis / derivatives_open_interest）、signals_log、trades_log、dryrun_open_positions、dryrun_runtime_snapshots、backfill_progress、derivatives_backfill_progress，及 5 个连续聚合（ohlcv_5m / 15m / 1h / 4h / 1d）——不遗漏任何迁入表（执行时以 `pg_tables` 实查清单为准，新增表自动纳入）。
- 回滚/前向兼容：restore 失败可重试（幂等，先 DROP 新库再 restore）；对账不一致即中止迁移并保留旧仓服务（NFR-001）。
- 历史数据：原样迁移，不做任何清洗/改写（口径改造属后续 feature）。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

Kronos HTTP API 契约不变：`GET /health`、`POST /predict/{symbol}`、`POST /predict_batch`。Freqtrade 容器经 `host.docker.internal` 访问薄壳。verify 脚本契约：单命令、退出码 0/非 0。

符号映射契约前置：本 feature 对 pair 命名原样直迁、不改名；M1 数据桥须按集成文档 §2.2
产出 `data_bridge/symbol_map.csv`（湖内 pair ↔ Freqtrade pair，按需附 Vibe symbol）并锁定 UTC。

### Event / Trace Contract

不适用：本 feature 无新事件类型；对账结果以 JSON 报告落 `reports/`（非机器事件流）。

## 5. Runtime、Workflow 与并发

启动顺序：TimescaleDB → Kronos 薄壳（等待 /health）→ Freqtrade dry-run → 监控栈。迁移批处理为单机人工触发，无并发竞争；重试策略仅限 pg_dump/restore 与权重下载（指数退避，各 ≤3 次）。不可回滚副作用边界：旧仓 git tag 一旦打出，归档即视为事实——因此 tag 是最后一步。

## 6. UI 与可观测性

- Grafana 数据源指向新 DB；导入旧仓 dashboard JSON 并逐面板确认非空。
- verify.ps1 输出逐项 PASS/FAIL 清单（数据对账/Kronos/采集/风控挂载/监控）。
- 迁移对账报告落 `reports/f001-reconciliation-<date>.json`（来源行数、目标行数、表级 diff）。

## 7. 失败、恢复、安全与兼容

- 校验与失败映射：对账 diff≠0 → 中止 + 保留旧仓；restore 失败 → 重试 ×3 → 换 volume 直迁方案；权重缺失 → 复制旧仓 models/。
- 重启与恢复：所有步骤幂等（DROP-then-restore、目录覆盖写、脚本可重复执行）。
- 权限 / escalation / 凭据边界：交易所 API Key 仅存旧仓 .env → 人工复制到主仓 .env（不进 git）；脚本不打印密钥。
- Windows / POSIX / 版本兼容：执行环境为 WSL2（见 §0 执行环境）；脚本用 PowerShell 7（apt 安装于 WSL2）+ Python 3.11+；路径统一 `pathlib`；UTF-8 显式编码（NFR-002）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f001_row_reconciliation.py` | design §3 口径全表（含 signals_log/trades_log 与连续聚合）count/hash 与旧仓基准一致 |
| `AC-002` | integration | `tests/integration/test_f001_kronos_smoke.py` | /health 200；/predict source=kronos |
| `AC-003` | integration | `tests/integration/test_f001_collector_smoke.py` | 单对采集写入且二次执行行数不变 |
| `AC-004` | integration | `tests/integration/test_f001_dryrun_monitoring.py` | 风控钩子日志存在；Grafana API 返回非空序列 |
| `AC-005` | integration | `deployment/verify.ps1` | 全部检查 PASS，退出码 0 |

集成测试需要本地服务在线（标注 integration，CI 上默认跳过，本地全绿为准——真实环境纪律见 SOP）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| pg_dump 优先而非 volume 直迁 | dump 可跨版本/可校验/幂等重试 | 对账是本 feature 的灵魂 | volume 直迁作为回退 |
| 阶段 A 保留 TimescaleDB | 见 spec Q-001 | 零风险接续 | 阶段 B 另立 feature |
| 残余风险：旧仓隐藏依赖在运行期才暴露 | verify 全链路覆盖启动路径；暴露即补 pyproject | 静态 grep 无法穷尽运行时 import | 运行一周后复核 |

## 10. 待确认设计问题

无
