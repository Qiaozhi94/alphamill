---
kind: feature
id: F001
version: "0.1"
status: done
gate_version: 1
related_features: []
topics: [migration, infra]
doc_kind: spec
created: 2026-09-06
updated: 2026-09-12
---

# F001：quant-crypto 资产清算迁移

> Owner: Georg | Target: v0.1.0

## 0. 来源与意图

- **PRD 来源**：`docs/alphamill-prd.md` §1.2 决策 4（复用成熟基础设施）与里程碑 M0
- **架构来源**：`docs/alphamill-architecture.md` §五（资产清算迁移表）、§七（部署拓扑）
- **系统设计 / Research / Contract 来源**：`docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`（迁移清单与验收）
- **上游决策**：`docs/decisions/`（暂无；仓库归档处置记录于同目录 migration-plan.md §二）
- **功能类型**：backend / workflow
- **规格模式**：full
- **变更类型**：ADDED
- **一句话意图**：在 quant-crypto 归档前，把可复用胶水代码一次性迁入本仓，并把其历史数据资产在主仓编排内从交易所重建，使 AlphaMill 自包含可运行。
- **路线修订（2026-09-10）**：原「数据卷 pg_dump 迁移 + 新旧库对账」契约因数据源灭失失效——宿主机于 2026-09-07~08 整机重装，quant-crypto 的 TimescaleDB 命名卷随 Docker Desktop 数据盘（旧 C 盘）丢失（六路取证钉死，见 `docs/reviews/RETROSPECTIVE.md` 模式教训 #16）。FR-001/AC-001/T001/T004/T005 已按「交易所重建 + 回填完整性校验」重写。

## 1. 问题、目标与非目标

### 问题

quant-crypto 已随宿主机重装停止服务，其历史数据卷在重装中丢失（2026-09-10 取证钉死，无任何备份副本）；其采集器、Kronos 服务薄壳、风控三件套、监控与部署编排是 AlphaMill M1+ 的运行前提。数据侧须以交易所回填方式重建历史 OHLCV 与衍生品数据，signals/trades 等研究产物历史接受损失。

### 目标

- 完成本仓内全链路可运行：数据可查（重建后）、Kronos 推理服务健康、Freqtrade dry-run 挂载真实信号、监控面板有数。
- 旧仓资产处置收口：`D:\Projects\quant-crypto`（HEAD `d94f94f`）只读保留，主仓不再依赖旧仓任何运行路径。

### 非目标

- 不实现 Parquet 湖导出与 DuckDB 取数层（属 F002 / M1 数据桥）。
- 不做 TimescaleDB 阶段 B（纯 Parquet 化），仅记录为后续候选。
- 不引入 AlphaGen vendor（属 F003 / M2）。

## 2. 用户场景

### US-001：主仓自包含运行（Priority: P1）

作为 `量化研究员`，我希望 `在本仓内一键拉起数据/推理/执行/监控全链路`，以便 `后续所有开发不依赖旧仓库`。

**为什么是这个优先级**：这是 M1+ 一切功能的前置；没有它主仓不是可运行系统。

**独立测试**：在新 clone 的主仓上按 deployment/verify.ps1 跑全链路检查并全绿。

**验收场景**：

1. Given `旧仓已停止服务且数据已重建`，when `docker compose up + 启动 Kronos 薄壳`，then `/health` 返回 200、回填完整性校验通过、Freqtrade dry-run 收到 Kronos 信号。
2. Given `迁移后任一时点`，when `对比新旧 DB 的行数与校验和`，then `完全一致且旧仓零改动`。

### US-002：旧仓安全归档（Priority: P2）

作为 `项目所有者`，我希望 `quant-crypto 打 tag 归档且不再被引用`，以便 `消除双仓维护负担`。

**为什么是这个优先级**：依赖 US-001 完成；归档过早会破坏回滚能力。

**独立测试**：grep 主仓代码不存在指向旧仓运行路径的硬编码依赖（文档引用除外）。

**验收场景**：

1. Given `US-001 验收通过`，when `旧仓打 tag archive/2026-09-migration`，then `主仓 CI/verify 不依赖旧仓任何路径`。

## 3. 范围与边界

### 范围内

- migration-plan.md §一 迁移总览 1-9 项：数据卷、采集器、Kronos 薄壳、风控三件套、评测器/门禁脚本（原样物理迁移；泛化改造属 F002/M1）、监控、部署编排、宇宙发现脚本、Freqtrade user_data。
- Kronos 上游化三步（上游 clone + pin commit、HF 权重下载、薄壳迁入 `kronos_service/`）。
- 迁移验收脚本（deployment/verify.ps1 扩展为全链路）。

### 范围外

- Parquet 湖导出、DuckDB 取数、统一评测台泛化（F002+）。
- 宇宙扩容到 30~50 对的执行（FR1.5 属 M1）。
- 任何策略逻辑修改。

### 边界场景

- 交易所历史 K 线深度不足的交易对：以 API 实际可得最早时间为准，缺口记入回填报告，不视为校验失败；连续聚合一律从 1m 基表重建，不单独回填。
- HF 权重下载失败（网络）：配置代理后重试；旧仓 `models/` 已确认不存在，无复制回退。
- 迁移期间发现旧仓代码依赖缺失：先在主仓 pyproject 落依赖再迁移代码，不留全局站点包隐式依赖。

## 4. 需求

### 功能需求

### Requirement: 数据资产重建与完整性校验（`FR-001`）

系统应当在主仓 docker-compose 编排内重建 quant-crypto 的数据资产：全新 TimescaleDB（原 schema 初始化）→ 从交易所回填历史 1m OHLCV 与衍生品数据 → 重建连续聚合，且回填完整性可校验。

#### Scenario: 回填完整性校验

- GIVEN 全新 TimescaleDB 且 schema 已初始化（init.sql + 衍生品迁移）
- WHEN 对配置宇宙的每个交易对执行 1m OHLCV 与衍生品数据回填，并按 design §3 口径执行完整性校验（逐表行数对交易所可得区间的预期、抽样时间轴连续性、连续聚合与基表重算一致）
- THEN 校验差异在允许范围内且报告落 `reports/`，连续聚合行数与 1m 基表重算结果一致

### Requirement: 采集器迁入并持续运行（`FR-002`）

采集器代码（ccxt_ingestor、db_writer、historical_backfill、symbol_manager）应当迁入 `data_bridge/collector/` 并以主仓依赖运行，保持幂等 upsert 与未闭合 K 线过滤行为不变。

#### Scenario: 采集冒烟

- GIVEN 迁移后 DB 可写
- WHEN 采集器对单一交易对运行一个采集周期
- THEN 新写入行幂等（重复执行不产生重复行）且过滤未闭合 K 线

### Requirement: Kronos 上游化与服务健康（`FR-003`）

Kronos 模型代码应当来自上游仓库 fresh clone（pin commit，零改动），权重来自 HuggingFace（NeoQuasar/Kronos-base + Tokenizer-base），服务薄壳迁入 `kronos_service/` 并保持 HTTP API 契约不变。

#### Scenario: 推理冒烟

- GIVEN 权重就位且推理后端可用（GPU 直通优先；GPU 未就绪时 CPU 回退，见 tasks T003）
- WHEN 请求 GET /health 与 POST /predict/BTC-USDT
- THEN /health 返回 200 且 /predict 返回 source=kronos 的信号

### Requirement: 风控与策略模板迁入挂载（`FR-004`）

风控三件套（CircuitBreaker、CorrelationGuard、DrawdownGuard）应当迁入 `freqtrade_bridge/risk/` 并在 dry-run 策略中保持 confirm_trade_entry 挂载行为。

#### Scenario: dry-run 冒烟

- GIVEN Freqtrade dry-run 容器启动
- WHEN 策略加载并触发一次模拟开仓判断
- THEN 风控钩子被调用且日志可见三件套生效

### Requirement: 监控迁入且有数（`FR-005`）

Grafana/Prometheus 配置应当迁入 `monitoring/`，数据源指向迁移后 DB，核心面板（K 线延迟、信号质量、交易健康）有数据。

#### Scenario: 面板有数

- GIVEN 监控栈启动
- WHEN 打开核心看板
- THEN 各面板返回非空序列

### Requirement: 部署编排迁入与全链路验证（`FR-006`）

docker-compose、.env 模板与 verify 脚本应当迁入 `deployment/`，verify 扩展为覆盖上述全部场景的全链路检查，且单命令可执行。

#### Scenario: 全链路 verify

- GIVEN 全部服务就绪
- WHEN 运行 deployment/verify.ps1
- THEN 全部检查通过（退出码 0）

### 非功能需求

- **NFR-001**：旧仓副本（`D:\Projects\quant-crypto`，HEAD `d94f94f`）保持只读；数据重建完成并通过完整性校验前，不得删除/归档该副本。
- **NFR-002**：跨环境路径与 UTF-8 编码兼容——所有迁移脚本在执行环境（WSL2 Ubuntu + PowerShell 7）下可运行，与 Windows 宿主交换文件时无路径/编码错误，中文内容无乱码。

## 5. 生命周期与不变量

不适用：本 feature 为一次性迁移作业，无可观察的长生命周期状态机；验收即终点。

## 6. 成功与验收

### 成功标准

- **SC-001**：主仓内单机全链路可运行且 verify 全绿（US-001）。
- **SC-002**：旧仓完成 tag 归档，主仓 grep 无旧仓运行路径硬依赖（US-002）。
- **SC-003**：migration-plan.md §一 迁移总览清单 9 项全部标记完成。

### 验收清单

- [x] **AC-001** (`FR-001`, `NFR-001`): 回填完整性校验通过（口径见 design §3：1m OHLCV 与衍生品表逐表行数符合交易所可得区间预期、抽样无缺口、连续聚合与基表重算一致），旧仓副本零改动 — tests: `tests/integration/test_f001_row_reconciliation.py`
- [x] **AC-002** (`FR-003`): Kronos 编排内契约——/health 200 且 /predict 返回结构合法信号，source 与 /health 的 model_enabled 一致（mock→placeholder，real→kronos；声明 real 却回 placeholder 判红） — tests: `tests/integration/test_f001_kronos_smoke.py`
- [x] **AC-003** (`FR-002`): 采集器单交易对冒烟通过且重复执行幂等 — tests: `tests/integration/test_f001_collector_smoke.py`
- [x] **AC-004** (`FR-004`, `FR-005`): dry-run 风控钩子生效且监控面板非空 — tests: `tests/integration/test_f001_dryrun_monitoring.py`
- [x] **AC-005** (`FR-006`, `NFR-002`): deployment/verify.ps1 单命令全绿 — tests: `deployment/verify.ps1`
- [x] **AC-006** (`FR-003`): 真实推理证据——真实模型实例 /predict 返回 source=kronos 且回报权重路径；权重（391MB）与 vendor clone 不入库，故由独立命令验证而非默认编排 — tests: `tests/integration/test_f001_kronos_smoke.py`

**验收修订（2026-09-12，F001 done 后）**：原 AC-002 一条同时承载「薄壳遵守 HTTP 契约」与
「真实 Kronos 模型出信号」两个主张——前者编排内可证，后者依赖 391MB 权重与 vendor clone
（二者均不入库），因此 `ALPHAMILL_INTEGRATION=1` 下该条恒红。现拆为 **AC-002（编排内契约，
常绿且双向 fail-closed）** 与 **AC-006（真实推理证据，独立命令）**，验收范围不缩小：AC-006
的证据即原 AC-002 的 T008 实测。AC-006 复跑命令（前置条件见 §7 依赖与 `vendor/VENDORED.md`）：

**compose 形态（首选，F004 落地后）**：

```bash
# 拉起编排内真实实例（首启含 torch 镜像构建与模型加载）；--wait 以 healthcheck
# （model_loaded=true 且 device=cpu）为通过条件，返回即就绪
docker compose -f deployment/docker-compose.yml --profile kronos-real up -d --wait kronos-signal-real
ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 \
  .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py -q
docker compose -f deployment/docker-compose.yml --profile kronos-real down kronos-signal-real
```

**手工形态（无 docker / 镜像不可构建时的回退）**：

```bash
# 宿主侧运行：DB_HOST 默认是 compose 服务名 timescaledb，宿主上解析不到，
# 必须先载入 .env 并改指回环——与 deployment/f001-backfill-supervisor.sh 同一约定。
set -a; . ./deployment/.env; set +a
DB_HOST=127.0.0.1 KRONOS_USE_REAL_MODEL=true KRONOS_REPO_PATH=vendor/Kronos \
  .venv/bin/python -m uvicorn alphamill.kronos_service.server:app --port 8002 &
ALPHAMILL_INTEGRATION=1 KRONOS_REQUIRE_REAL_MODEL=1 KRONOS_BASE_URL=http://127.0.0.1:8002 \
  .venv/bin/python -m pytest tests/integration/test_f001_kronos_smoke.py -q
```

F004 已把真实推理纳入 compose（torch 进镜像 + 权重挂载，可选 profile `kronos-real`，
见 `docs/features/0.2/F004-kronos-inference-runtime/`）——原挂 F002 T014，但 F002 检视
（F002-Q001）判定它不在数据桥契约内已移出。AC-006 复跑不再依赖手工起进程。

**验收证据（2026-09-12）**：AC-001 `reports/f001-backfill-20260910.json` verdict=PASS（631 万行满窗，缺失率≤0.13%）+ `tests/integration/test_f001_row_reconciliation.py`；AC-002 `tests/integration/test_f001_kronos_smoke.py` 编排内契约与模式自洽通过（两个方向各经一次变异验证：声称 real 却回 placeholder 判红）；AC-006 同文件真实模型 CPU 推理通过（`KRONOS_REQUIRE_REAL_MODEL=1` + :8002 实例，1.76s/次，T008 记录）；AC-003 `tests/integration/test_f001_collector_smoke.py` 幂等复跑通过；AC-004 `tests/integration/test_f001_dryrun_monitoring.py` 3 passed + tasks T017 forceenter 双路径实测；AC-005 `deployment/verify.ps1` 退出码 0（26 项检查，含回填完整性阈值）。集成测试汇总：`ALPHAMILL_INTEGRATION=1 pytest tests/integration` → 7 passed 1 skipped（skip 项为 AC-006，需上面的显式命令；默认编排是 mock 实例）。

## 7. 测试、依赖与决策

### 测试策略

- 集成测试：回填完整性校验、Kronos 冒烟、采集幂等、dry-run 风控挂载（pytest，需要本地服务在线）。
- 真实环境 / 手动验证：Grafana 面板人工目检；HF 权重下载一次人工确认文件校验。
- 不做单元测试覆盖——本 feature 以系统级数据完整性为主。

### 依赖

- 上游：quant-crypto 仓库副本（`D:\Projects\quant-crypto`，HEAD `d94f94f`，只读；原 Docker 数据卷已灭失，见 §0 路线修订）；OKX 交易所 API（历史数据重建）；HuggingFace 网络（权重）；docker-ce（WSL2）。
- 下游消费者：F002（数据桥）、F003（AlphaGen vendor）、所有后续 feature 的运行基座。
- 外部 / 环境依赖：GPU（未就绪时 AC-006 真实推理允许 CPU 回退）；AC-006 前置：`vendor/Kronos`（pin `67b630e`）+ `models/Kronos-base`、`models/Kronos-Tokenizer-base`（HF 下载，不入库）+ 宿主 venv 的 torch/cpu、einops、safetensors（见 `vendor/VENDORED.md`）、docker-compose、PowerShell 7（WSL2 内可用，apt 或用户态安装均可）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| TimescaleDB 去留 | 阶段 A 保留（随编排重建） | 零风险接续；阶段 B 另立 feature | F-后续评估 |
| 数据源灭失（2026-09-10 钉死） | 路线改为交易所重建 + 回填完整性校验；signals/trades/quality 历史接受损失 | 原卷随宿主机重装丢失且无备份副本（RETROSPECTIVE #16） | 旧实体机若复得可再评估补迁 |
| 回填受交易所限速/历史深度/DNS 污染限制 | `EXCHANGES=binance`（实证可达且历史深度完整）；受控速率串行回填 + `backfill_progress` 断点续传；`{EXCHANGE}_HTTPS_PROXY` 内网代理开关；深度缺口记入报告 | OKX 域名被 DNS 污染不可达（2026-09-10 实证），Binance 直连可用 | 回填报告落 `reports/`，记录行级 provenance |
| HF 下载受网络限制 | 配置代理后重试（旧仓 `models/` 已确认不存在） | 权重是静态资产，网络问题可解 | 无 |
| 本机无独立显卡 | AC-002 采用 CPU 推理回退；GPU 直通不作为迁移完成前置条件 | `nvidia-smi` 实测不可见，且当前主机无独立 GPU | 后续具备 GPU 的运行环境再做性能验证 |

## 8. 待确认问题

- [x] Q-001: TimescaleDB 迁移后保留还是转纯 Parquet？ — 决策：阶段 A 保留（migration-plan.md §四），阶段 B 另立 feature 评估
