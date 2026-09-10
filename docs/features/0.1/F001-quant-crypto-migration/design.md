---
kind: feature
id: F001
version: "0.1"
related_features: []
topics: [migration, infra]
doc_kind: design
created: 2026-09-06
updated: 2026-09-10
---

# F001：quant-crypto 资产清算迁移 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

## 0. 输入与约束

- **行为契约**：`spec.md`（FR-001..006 / NFR-001..002）
- **PRD / Architecture / System Design**：`docs/alphamill-prd.md` M0；`docs/alphamill-architecture.md` §五、§七；`migration-plan.md` 全文（本目录）
- **ADR / 上游 Contract**：Kronos HTTP API 契约以旧仓 `kronos-signal/server.py` 现行为准（不新增不修改）
- **执行环境（2026-09-07 实测钉死，2026-09-10 更新）**：Windows 11 宿主 + WSL2（Ubuntu 26.04，内核 6.18.33.2-microsoft-standard-WSL2）；docker-ce（29.8.0 实测）+ compose v2（非 Docker Desktop）；PowerShell 7 于 WSL2 内可用（apt 或用户态安装）；GPU：当前 `nvidia-smi` 不可见（T003 已记录 CPU 推理回退决策，AC-002 冒烟不阻塞）。
- **执行环境（2026-09-10 事故更新）**：宿主机于 2026-09-07~08 整机重装 Windows 11（重装后 hostname 仍为 qiaozhi-lt），原数据现场——Docker Desktop 命名卷 `quant-crypto_timescale_data`（实测 ohlcv_1m 6,504,359 行、11 张公有表、5 个连续聚合）——驻旧 C 盘 Docker Desktop 数据盘，随格式化灭失；2026-09-10 六路取证（D:/E: 全盘 vhdx、pre-format 备份、旧 WSL tar、NAS docker 卷、qiaozhi-gp、Windows .ssh）确认无任何副本，详见 `docs/reviews/RETROSPECTIVE.md` 模式教训 #16。**数据路线由「pg_dump 迁移 + 新旧对账」改为「全新起库 + OKX 回填 + 完整性校验」**。代码基线不变：`D:\Projects\quant-crypto`（git HEAD `d94f94f`，2026-09-10 实证，只读参照）。
- **实现约束**：旧仓副本只读（NFR-001）；数据重建通过完整性校验前，不得删除/归档旧仓副本。

## 1. 技术概要与影响面

三步走：① 主仓编排起全新 TimescaleDB（原 schema 初始化），从 OKX 回填历史数据并重建连续聚合，按 design §3 口径校验完整性；② 代码目录按 migration-plan.md §一 清单物理搬迁并并入主仓 pyproject 依赖；③ Kronos 上游化（clone pin + HF 权重 + 薄壳改造路径）后全链路 verify。

- 前端：不适用（无 UI 变更，Grafana 仅改数据源）
- 后端 / API：src/alphamill/kronos_service/ 迁入；API 契约不变
- 存储 / Migration：全新 TimescaleDB + 交易所数据回填 + 完整性校验（本 feature 核心）
- Runtime / Agent Adapter：无
- Event / Evidence：回填完整性报告写入 `reports/`（manifest 风格 JSON）
- 文档 / 配置：migration-plan.md 清单项勾选；deployment/verify.ps1 扩展

## 2. 架构与模块边界

迁移后模块边界与 `docs/alphamill-architecture.md` 目录设计一致（目录约定已拍板：Python 包一律 `src/alphamill/<module>/`，非 Python 资产留在仓根）：`src/alphamill/data_bridge/collector/`（采集）与 `src/alphamill/data_bridge/`（导出，F002 实现）分离；`src/alphamill/kronos_service/` 只做 DB→推理→信号，不含业务策略；`src/alphamill/freqtrade_bridge/risk/` 只被策略模板 import；`monitoring/`、`deployment/` 为非 Python 资产留在仓根，`deployment/` 是唯一编排入口。依赖方向单向：deployment → services → data。旧仓迁移后仅作为只读历史参照，任何运行时路径不得指向旧仓。

## 3. 数据模型与 Migration

- 方案：主仓编排起全新 TimescaleDB（`db/init.sql` + `db/migrations/003_derivatives_market_data.sql` 自动初始化）→ 迁入的采集器 `historical_backfill` 从 OKX 回填（幂等 upsert、`backfill_progress` 断点续传）→ 重建 5 个连续聚合。**完整性校验口径（唯一权威定义，spec FR-001 / AC-001 与 design §8 引用此处）**：
  - `ohlcv_1m`：逐交易对行数 ≥ 交易所可得区间预期行数 × 阈值（容忍交易所侧偶发缺失）；抽样时间轴连续性——相邻 K 线间隔超出 1 分钟的孤立缺口数在阈值内（交易所停服/下架对导致的系统缺口记入报告而非判红）；
  - 衍生品三表（derivatives_funding_rates / derivatives_mark_index_basis / derivatives_open_interest）：同口径回填与校验；
  - 连续聚合（ohlcv_5m / 15m / 1h / 4h / 1d）：重建后行数与 1m 基表按桶重算结果一致（精确断言，无阈值）；
  - `signals_log` / `trades_log` / `quality_flags` / `dryrun_*`：研究产物与运行态历史，不可重建，**空表起步**并在报告中显式记录损失范围；
  - 执行时以 `pg_tables` 实查清单为准，新增表自动纳入。
- 回滚/前向兼容：回填幂等（重复执行不产生重复行，FR-002 行为不变式），可中断续传；校验不通过即中止下游任务并保留报告。
- 历史数据：回填数据原样入库，不做任何清洗/改写（口径改造属后续 feature）。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

Kronos HTTP API 契约不变：`GET /health`、`POST /predict/{symbol}`、`POST /predict_batch`。Freqtrade 容器经 `host.docker.internal` 访问薄壳。verify 脚本契约：单命令、退出码 0/非 0。

符号映射契约前置：本 feature 对 pair 命名原样直迁、不改名；M1 数据桥须按集成文档 §2.2
产出 `data_bridge/symbol_map.csv`（湖内 pair ↔ Freqtrade pair，按需附 Vibe symbol）并锁定 UTC。

### Event / Trace Contract

不适用：本 feature 无新事件类型；回填完整性报告落 `reports/`（非机器事件流）。

## 5. Runtime、Workflow 与并发

启动顺序：TimescaleDB → Kronos 薄壳（等待 /health）→ Freqtrade dry-run → 监控栈。回填批处理为单机人工触发，受控速率串行执行，无并发竞争；重试策略仅限回填请求与权重下载（指数退避，各 ≤3 次）。不可回滚副作用边界：旧仓副本删除/归档一旦发生即不可逆——因此它是最后一步，且以数据重建验收通过为前提。

## 6. UI 与可观测性

- Grafana 数据源指向新 DB；导入旧仓 dashboard JSON 并逐面板确认非空。
- verify.ps1 输出逐项 PASS/FAIL 清单（数据完整性/Kronos/采集/风控挂载/监控）。
- 回填完整性报告落 `reports/f001-backfill-<date>.json`（逐表预期行数、实际行数、缺口清单、损失记录）。

## 7. 失败、恢复、安全与兼容

- 校验与失败映射：完整性校验不过 → 中止下游任务 + 报告留档；回填请求失败 → 重试 ×3（指数退避）→ 记录断点；权重缺失 → 配置代理重试 HF 下载。
- 重启与恢复：所有步骤幂等（upsert 回填、目录覆盖写、脚本可重复执行）。
- 权限 / escalation / 凭据边界：交易所 API Key 仅存旧仓 .env → 人工复制到主仓 .env（不进 git）；脚本不打印密钥。
- Windows / POSIX / 版本兼容：执行环境为 WSL2（见 §0 执行环境）；脚本用 PowerShell 7（WSL2 内可用）+ Python 3.11+；路径统一 `pathlib`；UTF-8 显式编码（NFR-002）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration | `tests/integration/test_f001_row_reconciliation.py` | design §3 口径：ohlcv_1m/衍生品表行数与连续性达标，连续聚合与基表重算一致 |
| `AC-002` | integration | `tests/integration/test_f001_kronos_smoke.py` | /health 200；/predict source=kronos |
| `AC-003` | integration | `tests/integration/test_f001_collector_smoke.py` | 单对采集写入且二次执行行数不变 |
| `AC-004` | integration | `tests/integration/test_f001_dryrun_monitoring.py` | 风控钩子日志存在；Grafana API 返回非空序列 |
| `AC-005` | integration | `deployment/verify.ps1` | 全部检查 PASS，退出码 0 |

集成测试需要本地服务在线（标注 integration，CI 上默认跳过，本地全绿为准——真实环境纪律见 SOP）。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 数据源灭失后选择交易所重建而非放弃历史 | OKX 回填 1m/衍生品 + 连续聚合重建；signals/trades 历史接受损失 | OHLCV 可重购，研究产物不可重建——损失范围已在 §3 口径显式记录 | 旧实体机若复得，可评估 signals/trades 补迁 |
| 交易所回填优先于自建下载器 | 复用迁入的 `historical_backfill`（幂等 upsert + 断点续传） | 采集器行为不变式（FR-002）已验证幂等 | 限速不满足时再评估并行度 |
| 阶段 A 保留 TimescaleDB | 见 spec Q-001 | 零风险接续 | 阶段 B 另立 feature |
| 残余风险：旧仓隐藏依赖在运行期才暴露 | verify 全链路覆盖启动路径；暴露即补 pyproject | 静态 grep 无法穷尽运行时 import | 运行一周后复核 |

## 10. 待确认设计问题

无
