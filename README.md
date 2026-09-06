# AlphaMill（淘沙）

> 加密量化研究系统 v2 — 以**因子假设吞吐量**为核心指标：程序化批量挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行，Vibe-Trading 作为研究/回测/复盘上层建筑。
>
> 版本：v0.1 | 日期：2026-09-06 | 状态：设计阶段（未开工）

---

## 项目定位（一句话）

不重造轮子：**quant-crypto 一次性清算迁移**（数据湖/风控/监控资产并入本仓，原仓库归档），接入 **Vibe-Trading**（研究回测复盘上层）与 **Freqtrade**（交易执行基建），补齐唯一致命缺口——**因子自动挖掘模块**。

## 背景

上一代项目 quant-crypto 用 5 周建成完整基础设施（631 万行 OHLCV 数据湖、Kronos 信号 RankIC>0.05、Freqtrade dry-run、风控三件套），但 5 周只测了 3 个信号族，所有候选死在最终 90 天留出门（`blocked_no_paper_candidate`）。根因不是基建，是**假设吞吐量低**（~5 个/周 vs 需要 100+/周）。AlphaMill 的答案：程序化因子挖掘 + 统一评测台 + Vibe-Trading 复盘层。

## 文档索引

| 文档 | 内容 |
|---|---|
| [docs/alphamill-prd.md](docs/alphamill-prd.md) | 背景诊断、目标（G1-G5 量化验收）、功能需求 FR1-FR6、非功能需求、里程碑 M0-M4、风险 |
| [docs/alphamill-architecture.md](docs/alphamill-architecture.md) | 存储三件套分工（TimescaleDB/Parquet/DuckDB）、三层模块级架构图（ASCII+Mermaid）、因子生命周期数据流、目录设计、4 个接口契约、quant-crypto 资产清算迁移表 |
| [docs/alphamill-research-factor-mining.md](docs/alphamill-research-factor-mining.md) | 选型调研证据：因子挖掘引擎（AlphaGen/gplearn）、ML 框架（Qlib/FreqAI）、验证库、vectorbt、LLM agent |
| [docs/alphamill-integration.md](docs/alphamill-integration.md) | 集成操作细节：数据桥、Vibe-Trading 四面接入、Freqtrade 策略模板与无前视对齐、门禁迁移、失败隔离 |
| [docs/decisions/0001-factor-mining-engine.md](docs/decisions/0001-factor-mining-engine.md) | ADR：AlphaGen vendor 主引擎 + 冒烟闸门 + L1/L2 降级阶梯 |
| [docs/decisions/0002-external-dependency-policy.md](docs/decisions/0002-external-dependency-policy.md) | ADR：外部依赖三分法（vendor/fork/原样）+ 卫生规则 |
| [docs/decisions/0003-validation-gate-non-degradation.md](docs/decisions/0003-validation-gate-non-degradation.md) | ADR：验证门禁不降级（90 天留出 + ≥30 笔 + 无前视三层） |
| [docs/features/0.1/F001-quant-crypto-migration/](docs/features/0.1/F001-quant-crypto-migration/spec.md) | F001 三件套 + migration-plan：quant-crypto 归档清算迁移 |

## 架构总览

```text
Vibe-Trading（研究/复盘上层）
        ▲ manifest/报告        ▲ Parquet
Freqtrade（执行） ← 信号缓存 ← 验证门禁 ← 因子工厂（评测台+生成器+注册表） ← 数据桥 ← TimescaleDB 湖（迁入）
```

详细图见 [docs/alphamill-architecture.md](docs/alphamill-architecture.md)。

## 核心原则（继承自 quant-crypto 的教训）

1. **留出门不降级**：任何候选必须通过最终 90 天留出（≥30 笔交易）才能进 paper——上一代的 `blocked_no_paper_candidate` 是系统在正确工作。
2. **无前视是一等公民**：AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查。
3. **吞吐量优先**：先量产候选（≥100/周），人只审评测台分诊后的存活者。
4. **可复现**：每个实验有 manifest（数据版本 + 代码版本 + 参数 + 结果）。
5. **实盘前置条件不变**：没有留出通过的候选，就不碰真金白银。

## 外部依赖

| 组件 | 角色 | 说明 |
|---|---|---|
| [Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)（HKUDS, MIT, v0.1.14） | 研究/回测/复盘上层 | 只接 4 个面：local loader、回测/验证工具、quantlib、agent 复盘；**不接**其实盘栈与数据源 |
| [Freqtrade](https://github.com/freqtrade/freqtrade)（GPL-3.0, 2026.8） | 交易执行 | 沿用 quant-crypto 的 dry-run 部署与策略模式（随迁移并入） |
| quant-crypto 资产（清算迁入） | 数据湖/风控/监控 | TimescaleDB 数据卷、风控三件套、Grafana/Prometheus 配置随迁移并入本仓（迁移表见 docs/alphamill-architecture.md） |
| **AlphaGen**（vendor 接入） | FR2 核心：因子挖掘主引擎 | vendor + 现代依赖栈策略见 [ADR-0001](docs/decisions/0001-factor-mining-engine.md) 与 [选型调研](docs/alphamill-research-factor-mining.md) |

## 快速开始（设计阶段之后）

```bash
# M1 后可用
python data_bridge/export_ohlcv.py            # TimescaleDB → Parquet + manifest
python factor_factory/bench/run_bench.py --factor <factor_id>
python validation/holdout_gate.py --factor <factor_id> --window 90d
```

（命令为设计目标，实现后以实际为准。）

## 相关项目

- `../quant-crypto`（本机路径，已归档）— 上一代系统：资产清算迁移至本仓，方案见 [F001 migration-plan](docs/features/0.1/F001-quant-crypto-migration/migration-plan.md)
- `../tradingview-quant-research`（本机路径）— TradingView 定位调研（可视化/Alert 层的参考依据）
