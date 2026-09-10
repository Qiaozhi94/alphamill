---
kind: feature
id: F001
version: "0.1"
related_features: []
topics: [migration, infra]
doc_kind: tasks
created: 2026-09-06
updated: 2026-09-10
---

# F001：quant-crypto 资产清算迁移 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`。
- 技术方案与边界：`design.md`。
- 每项任务只描述一个可验证动作，并引用合法的 US/需求/AC ID。
- SC-xxx（spec §6 成功标准 ID）在本文件中视为合法任务引用锚：迁移清单覆盖类任务
  （T012/T013/T014）无对应 FR（泛化改造属 F002/M1），以 SC-003 为验收锚。
- 完成且验证后立即把 `[ ]` 改为 `[x]`，不得最后统一补勾。
- `[P]` 只用于修改不同文件、没有显式前置依赖且不会争用同一状态的任务。
- 实现中若任务顺序或契约失效，先修订三件套，再继续编码。

## 1. 前置条件

### 当前进展（2026-09-11）

- **数据源灭失与路线修订**：宿主机 2026-09-07~08 整机重装，原 qiaozhi-lt Docker 卷
  `quant-crypto_timescale_data` 随旧 C 盘丢失，六路取证确认无备份副本（见
  `docs/reviews/RETROSPECTIVE.md` 模式教训 #16）。FR-001/AC-001 契约改为「交易所重建 +
  回填完整性校验」，T001/T004/T005 已重写。
- **回填源切换（2026-09-10 实证）**：OKX 域名在本机被 DNS 污染不可达（解析到假 IP），
  Binance 直连可用且回填窗口（2024-09-10 起）历史深度完整可得；回填与实时采集统一
  `EXCHANGES=binance`（纯配置变更），采集器新增 `{EXCHANGE}_HTTPS_PROXY` 代理开关
  （默认关闭），出网经内网 NAS mihomo。
- 代码/配置迁移已完成并通过本地质量门：T006、T011、T012、T013 已完成。
- 本机开发环境已恢复：`.venv` 重建、`tools/verify.py` 六步全绿（2026-09-10）。
- 本机无独立显卡，`nvidia-smi` 不可见；按 FR-003/AC-002 采用 CPU 推理回退，T003 的 GPU 直通前置条件不满足但回退决策已完成。
- 数据重建已完成并通过完整性校验（T005），NAS 每日备份与恢复演练已落地（T015）：
  dump 154MB 经分块校验通道上 NAS（md5 双端一致），临时容器恢复 631 万行与源库精确一致。
- 剩余：T017 Freqtrade dry-run、T018 verify.ps1 全链路、T019-T022 验收收口。

- [x] T001 (`NFR-001`): 旧仓只读基线钉死——`D:\Projects\quant-crypto`（git HEAD `d94f94f` 已实证）设为只读参照并留存清单（顶层目录 + HEAD + 关键资产盘点：`.env`、`db/`、`freqtrade/user_data/`、`reports/`）；原运行现场（Docker 卷）已灭失，数据基线改由 T005 回填报告承载 — verify: `reports/f001-source-inventory-2026-09-10.md` 存在且记录 HEAD `d94f94f`
- [x] T002 (`FR-001`): 确认 WSL2 内 docker-ce、PowerShell 7（apt 或用户态安装）、Python 3.11+ 就绪且主仓 docker-compose 可启动 — verify: `docker compose ps` 全部 Running（2026-09-10 实测：docker-ce 29.8.0、pwsh 7.6.6 用户态、Python 3.14 venv；timescaledb/kronos-signal/grafana/prometheus 四容器 Running，data-collector 有意待回填完成后拉起）
- [x] T003 (`FR-003`): GPU 直通检查——本机无独立显卡，WSL2 内 `nvidia-smi` 不可见 RTX 4060；已记录 CPU 推理回退决策（AC-002 冒烟不阻塞） — verify: 无 GPU 实测，CPU 回退决策见本节进展记录与 `spec.md` §4 FR-003

## 2. 实现任务

### Phase 1：数据资产重建

- [x] T004 (`FR-001`): 主仓编排起全新 TimescaleDB——`docker compose -f deployment/docker-compose.yml up -d timescaledb`，schema 由 `db/init.sql`（含 5 个连续聚合）自动初始化，`db/migrations/003_derivatives_market_data.sql` 手工应用 — verify: 容器 healthy + 全部公有表就位（2026-09-10 实测 11 张公有表 + 5 个连续聚合）
- [x] T005 (`FR-001`, `AC-001`): 重建 5 个连续聚合（ohlcv_5m/15m/1h/4h/1d）并执行交易所历史回填（`EXCHANGES=binance`，1m OHLCV + 衍生品三表，幂等 upsert、`backfill_progress` 断点续传，经 `{EXCHANGE}_HTTPS_PROXY` 内网代理出网），按 design §3 口径执行完整性校验并产出 `reports/f001-backfill-<date>.json` — verify: `tests/integration/test_f001_row_reconciliation.py`（2026-09-11 实测：6 对满窗 631 万行、BTC 缺 33 行=0.003% 其余零缺失；5 聚合与基表桶一致；funding 13152 行、OI 744 行（币安 30 天深度上限，缺口已记录）、basis 0（binanceusdm 无 index OHLCV，边界记录）；报告 `reports/f001-backfill-20260910.json` verdict=PASS；全量 pytest 50 passed）

### Phase 2：代码与服务搬迁

- [x] T006 [P] (`FR-002`): 采集器四模块迁入 `src/alphamill/data_bridge/collector/` 并并入 pyproject 依赖 — verify: `.venv/bin/python` 四模块 import smoke 通过；新增 `symbol_manager` 统一符号解析并有 6 个单元测试
- [x] T007 [P] (`FR-003`): 上游 Kronos fresh clone + pin commit + HF 权重下载（或旧仓 models/ 复制） — verify: 权重文件存在 + commit hash 记录于 VENDORED 说明（2026-09-10 实测：clone pin `67b630e`，`models/Kronos-base` 391MB + `models/Kronos-Tokenizer-base` 16MB safetensors 就位，记录见 `vendor/VENDORED.md`；旧仓 models/ 已灭失，走 HF 主路径）
- [x] T008 (`FR-003`, `AC-002`): kronos-signal 薄壳迁入 `src/alphamill/kronos_service/` 并指向新 DB 与上游代码路径 — verify: `tests/integration/test_f001_kronos_smoke.py`（2026-09-10 实测 2 passed：真实 Kronos-base CPU 推理单次 1.76s，`KRONOS_USE_REAL_MODEL=true` + `KRONOS_REPO_PATH=vendor/Kronos` + 本机 8002 端口；宿主真实推理额外依赖 torch/cpu + einops + safetensors，见 `vendor/VENDORED.md`。compose 容器实例默认 mock 模式，权重挂载随 T017 全链路联调评估）
- [x] T009 [P] (`FR-004`): 风控三件套迁入 `src/alphamill/freqtrade_bridge/risk/` — verify: 三模块 import 冒烟通过（2026-09-10 实测 CircuitBreaker/CorrelationGuard/DrawdownGuard）
- [x] T010 [P] (`FR-005`): Grafana/Prometheus 配置迁入 `monitoring/` 且数据源指向新 DB — verify: 容器启动无配置错误（2026-09-10 实测 grafana/prometheus/kronos-signal 容器 Up、HTTP 健康端点全 200、日志无配置错误）
- [x] T011 [P] (`FR-006`): docker-compose/.env 模板/verify 脚本迁入 `deployment/`（.env 人工搬运密钥，不进 git） — verify: `docker compose -f deployment/docker-compose.yml config` 无报错；PowerShell 脚本已迁入并固定 compose 文件路径
- [x] T012 [P] (`SC-003`): 评测器/门禁脚本原样物理迁移（kronos_rankic_eval、kronos_ic_decay_eval、independent_cross_backtest、validate_*_holdout → `src/alphamill/factor_factory/bench/` + `src/alphamill/validation/`；泛化改造属 F002/M1，不在本 feature） — verify: `.venv/bin/python` 迁入模块逐一 import smoke 通过
- [x] T013 [P] (`SC-003`): 宇宙发现脚本迁入 `scripts/`（discover_okx_swap_universe.py、download_okx_swap_1h.ps1，无改造） — verify: `.venv/bin/python scripts/discover_okx_swap_universe.py --help` 退出码 0
- [x] T014 [P] (`SC-003`): Freqtrade user_data 策略与 config 迁入 `freqtrade/user_data/`（kronos_cache / feather 行情按 migration-plan.md item 9 git 边界留本地，不进 git；幸存样本已从 `D:\Projects\quant-crypto` 确认在旧仓只读副本中） — verify: 策略与 config 文件存在，`py_compile` 语法冒烟通过（2026-09-10 实测 5 文件）；完整 import 验证由 T017 dry-run 容器承载（freqtrade 依赖不在主仓 venv）
- [x] T015 (`FR-006`): 在 `deployment/` 落每日 NAS 备份同步（TimescaleDB pg_dump + `reports/`，预留 `lake/` 与 manifest 目录位；目标 UGREEN NAS，见 migration-plan.md §七）——**数据重建完成后立即落地，不得后移到验收期**（2026-09-10 数据丢失事故的直接对策） — verify: 手动触发一次同步，NAS 端产物齐全（2026-09-11 实测：`deployment/backup-nas.sh` + systemd user timer 03:00；UGREEN sshd 流式 reset 的绕行——4MB 分块追加+逐块校验+md5 双端一致；154MB dump 已上 NAS；恢复演练 dump→临时容器 6,312,924 行与源库精确一致）

### Phase 3：全链路验证

- [x] T016 (`FR-002`, `AC-003`): 采集器单交易对冒烟 + 幂等复跑 — verify: `tests/integration/test_f001_collector_smoke.py`（2026-09-10 实测 passed：BTC/USDT 两个紧邻周期已闭 K 线零增长，未闭合 K 线被过滤）
- [ ] T017 (`FR-004`, `AC-004`): Freqtrade dry-run 启动并确认风控钩子与监控面板 — verify: `tests/integration/test_f001_dryrun_monitoring.py`
  - 2026-09-11 进展：dry-run 容器已运行（freqtrade:stable + config.dryrun.json 覆盖：binance/代理/JWT/fiat），策略经
    `KRONOS_SIGNAL_URL=host.docker.internal:8001` + `KRONOS_SIGNAL_EXCHANGE=binance` 成功取得 6 对信号（BTC buy/XRP sell/其余 neutral），
    heartbeat 稳定。策略新增 `KRONOS_SIGNAL_EXCHANGE` 环境变量出口（默认 okx 保持旧行为）。
  - 待完成：入场触发→confirm_trade_entry 风控钩子证据（入场受信号融合门控，属策略逻辑域）；`collect_runtime_snapshot.ps1`
    （旧仓 scripts/，写 dryrun_runtime_snapshots/open_positions，不在迁移清单）需迁入才能点亮监控面板——属 T018 前置发现项。
- [ ] T018 (`FR-006`, `AC-005`): 扩展并运行 deployment/verify.ps1 全链路检查 — verify: `deployment/verify.ps1` 退出码 0

## 3. 验证与验收任务

- [ ] T019 (`AC-001`, `AC-002`, `AC-003`, `AC-004`): 本地运行全部集成测试 — verify: `python -m pytest tests/integration -q`
- [ ] T020 (`NFR-002`): 确认全部脚本在 PowerShell 7 下无路径/编码错误 — verify: T018 附带输出无乱码
- [ ] T021 (`AC-005`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
- [ ] T022: 回写 spec 验收证据、BACKLOG 状态与 migration-plan.md 清单勾选 — verify: `python tools/validate_spec_lifecycle.py`

## 4. 依赖与并行关系

- `T004 -> T005`：回填依赖全新库就绪。
- `T005 -> T015`：备份在数据重建完成后立即落地（事故对策，不得后移）。
- `T006 -> T016`、`T007 -> T008 -> T017`：冒烟依赖搬迁完成。
- `T004 -> T016`：采集冒烟依赖 DB 可写。
- `T003 -> T008`：GPU 直通结论先行于薄壳联调（决定推理后端）。
- `T006/T007/T009/T010/T011/T012/T013/T014 [P]`：互相可并行（不同目录、无共享状态），但均依赖 T002。
- `T014 -> T017`：dry-run 冒烟依赖 user_data 策略就位。
- `T018 -> T019 -> T022`：验收链顺序执行。

## 5. 明确后移

- TimescaleDB 阶段 B（纯 Parquet 化）→ 后续独立 feature：属架构演进，不属迁移范围。
- Parquet 湖导出与 DuckDB 取数层 → F002：数据桥属 M1 范围。
- 宇宙扩容到 30~50 对 → F002/M1：依赖迁移完成的采集管线。
