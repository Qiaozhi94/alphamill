---
kind: feature
id: F001
version: "0.1"
status: in-progress
gate_version: 1
related_features: []
topics: [migration, infra]
doc_kind: spec
created: 2026-09-06
updated: 2026-09-08
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
- **一句话意图**：在 quant-crypto 归档前，把数据资产与可复用胶水代码一次性迁入本仓，使 AlphaMill 自包含可运行。

## 1. 问题、目标与非目标

### 问题

quant-crypto 决定归档废弃，但其中 631 万行 OHLCV 数据、采集器、Kronos 服务薄壳、风控三件套、监控与部署编排是 AlphaMill M1+ 的运行前提；不迁移则主仓无法独立工作，数据重购成本为数周。

### 目标

- 完成本仓内全链路可运行：数据可查、Kronos 推理服务健康、Freqtrade dry-run 挂载真实信号、监控面板有数。
- quant-crypto 仓库可安全归档（打 tag，之后只读）。

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

1. Given `旧仓已停止服务且数据卷已迁移`，when `docker compose up + 启动 Kronos 薄壳`，then `/health` 返回 200、DB 行数与旧仓对账一致、Freqtrade dry-run 收到 Kronos 信号。
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

- 数据卷直迁失败时：回退 pg_dump/restore 方案，两方案都失败则中止并保留旧仓服务（绝不在数据未对账前归档）。
- HF 权重下载失败（网络）：允许从旧仓 `models/` 目录直接复制已下载权重。
- 迁移期间发现旧仓代码依赖缺失：先在主仓 pyproject 落依赖再迁移代码，不留全局站点包隐式依赖。

## 4. 需求

### 功能需求

### Requirement: 数据卷迁移与对账（`FR-001`）

系统应当将 quant-crypto 的 TimescaleDB 数据卷完整迁入主仓 docker-compose 编排，且迁移后行数与校验和同旧仓完全一致。

#### Scenario: 行数对账

- GIVEN 旧仓 DB 与新仓 DB 同时可读
- WHEN 按 design §3 对账口径对全部迁入表（ohlcv_1m、衍生品三表、quality_flags、signals_log、trades_log 及连续聚合）逐表执行行数与校验和比对
- THEN 差异为 0，且 quality_flags 未解决标记数一致

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

- **NFR-001**：迁移期间旧仓必须保持只读（除 git tag 外零改动）；对账完成前不得归档。
- **NFR-002**：跨环境路径与 UTF-8 编码兼容——所有迁移脚本在执行环境（WSL2 Ubuntu + PowerShell 7）下可运行，与 Windows 宿主交换文件时无路径/编码错误，中文内容无乱码。

## 5. 生命周期与不变量

不适用：本 feature 为一次性迁移作业，无可观察的长生命周期状态机；验收即终点。

## 6. 成功与验收

### 成功标准

- **SC-001**：主仓内单机全链路可运行且 verify 全绿（US-001）。
- **SC-002**：旧仓完成 tag 归档，主仓 grep 无旧仓运行路径硬依赖（US-002）。
- **SC-003**：migration-plan.md §一 迁移总览清单 9 项全部标记完成。

### 验收清单

- [ ] **AC-001** (`FR-001`, `NFR-001`): 全部迁入表（口径见 design §3，含 signals_log/trades_log 与连续聚合）行数与校验和对账差异为 0，旧仓零改动 — tests: `tests/integration/test_f001_row_reconciliation.py`
- [ ] **AC-002** (`FR-003`): Kronos /health 200 且 /predict 返回 source=kronos — tests: `tests/integration/test_f001_kronos_smoke.py`
- [ ] **AC-003** (`FR-002`): 采集器单交易对冒烟通过且重复执行幂等 — tests: `tests/integration/test_f001_collector_smoke.py`
- [ ] **AC-004** (`FR-004`, `FR-005`): dry-run 风控钩子生效且监控面板非空 — tests: `tests/integration/test_f001_dryrun_monitoring.py`
- [ ] **AC-005** (`FR-006`, `NFR-002`): deployment/verify.ps1 单命令全绿 — tests: `deployment/verify.ps1`

## 7. 测试、依赖与决策

### 测试策略

- 集成测试：行数对账、Kronos 冒烟、采集幂等、dry-run 风控挂载（pytest，需要本地服务在线）。
- 真实环境 / 手动验证：Grafana 面板人工目检；HF 权重下载一次人工确认文件校验。
- 不做单元测试覆盖——本 feature 以系统级对账为主。

### 依赖

- 上游：quant-crypto 仓库（只读源；代码已克隆至本机 `/root/projects/quant-crypto`，HEAD `d94f94f`；**数据源在 qiaozhi-lt**（Tailscale `100.98.228.125`）`D:\Projects\quant-crypto` 的 Docker 卷 `quant-crypto_timescale_data`，SSH 访问路径见 tasks T001/T004）；HuggingFace 网络（权重）；docker-ce（WSL2）。
- 下游消费者：F002（数据桥）、F003（AlphaGen vendor）、所有后续 feature 的运行基座。
- 外部 / 环境依赖：RTX 4060 GPU（WSL2 直通；未就绪时 AC-002 冒烟允许 CPU 推理回退）、docker-compose、PowerShell 7（apt 安装于 WSL2）。

### 决策与风险

| 决策 / 风险 | 结论或缓解 | 理由 | 后续 |
|---|---|---|---|
| TimescaleDB 去留 | 阶段 A 保留（随编排迁入） | 零风险接续；阶段 B 另立 feature | F-后续评估 |
| 数据卷直迁失败 | 回退 pg_dump/restore | 两种方案覆盖主流失败模式 | 迁移当天决定 |
| HF 下载受网络限制 | 允许复制旧仓 models/ 已有权重 | 权重是静态资产，复制等价 | 无 |
| 本机无独立显卡 | AC-002 采用 CPU 推理回退；GPU 直通不作为迁移完成前置条件 | `nvidia-smi` 实测不可见，且当前主机无独立 GPU | 后续具备 GPU 的运行环境再做性能验证 |

## 8. 待确认问题

- [x] Q-001: TimescaleDB 迁移后保留还是转纯 Parquet？ — 决策：阶段 A 保留（migration-plan.md §四），阶段 B 另立 feature 评估
