# AlphaMill

以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行（中文别名：淘沙）

## 当前结构

- `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
- `docs/alphamill-architecture.md`：分层架构与接口契约（架构真相源），随实现迭代。
- `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
- `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
- `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级。
- `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-crypto 资产清算迁移操作手册（F001 附属）。
- `docs/README.md`：文档所有权地图（唯一入口，两次点击可达任何权威文档）。
- `docs/SOP.md`：开发流程与质量门约定。
- `docs/features/`：SDD feature 规格目录，按大版本分层（0.1、0.2…）；
  `docs/features/releases/` 存放版本收口摘要。
- `docs/decisions/`：重要决策记录（ADR）。
- `docs/reviews/`：设计/代码评审记录；只有 `RETROSPECTIVE.md`（复盘）与
  `CURRENT-doc.md`/`CURRENT-code.md`（进行中的检视报告）入库，其余本地-only（见 `.gitignore`）。
- `docs/research/`：前期调研归档，本地-only（见 `.gitignore`）。
- `BACKLOG.md`：近期功能拆分和执行跟踪入口，只列非 done Feature。
- `conversations/`：AI 对话归档（由 conversation-archive skill 管理）。

## 技术栈

- 语言/运行时：Python 3.11+（研究/采集/门禁/服务薄壳）
- 核心依赖：pandas/polars（因子计算）、DuckDB（湖上 SQL 取数）、pyarrow（Parquet 湖）、
  ccxt（采集）、Freqtrade（执行，docker 镜像 2026.8，零源码改动）、
  vibe-trading-ai（研究上层，pip pin，零源码改动）、AlphaGen 核心 vendor（RL 挖掘主引擎）、
  Kronos（上游 clone + pin；GPU 推理薄壳为本仓 `kronos_service/`）
- 数据栈：TimescaleDB（联机运营库，自 quant-crypto 迁入）→ data_bridge → Parquet 湖（不可变快照）
- 测试/质量：pytest + ruff（check + format），唯一入口 `python tools/verify.py`
- 平台：Windows 11 单机 + RTX 4060 Laptop GPU；docker-compose 自 quant-crypto 迁入

## 开发约定

- 开发流程见 `docs/SOP.md`。
- Feature 记录见 `BACKLOG.md` 和 `docs/features/`；新建 feature 从
  `docs/features/TEMPLATE/` 复制三件套，状态规则见 `docs/features/README.md`。
- 质量门禁：统一入口 `python tools/verify.py`（串联文档门禁与测试；技术栈落地后扩展 lint/
  typecheck/build）。Feature 状态变更前必须运行它。
- 数据红线：研究/回测只读 Parquet 湖（data_version 快照），不直读 TimescaleDB 修订态；信号缓存时间戳对齐是硬门禁。
- 实盘红线：无候选通过最终 90 天留出（≥30 笔）前，不触碰实盘下单路径。

## 当前活跃 Feature

- F001 quant-crypto 资产清算迁移（v0.1, draft）→ `docs/features/0.1/F001-quant-crypto-migration/`
