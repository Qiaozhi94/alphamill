# AlphaMill — 产品需求文档（PRD）

> 版本：v0.1 | 日期：2026-09-06 | 状态：草案
> 前置文档：`D:\Projects\tradingview-quant-research\research.md`（TradingView 调研）、`D:\Projects\quant-crypto\00-系统总体方案.md`（上一代系统）

---

## 一、背景与问题定义

### 1.1 quant-crypto 复盘（2026-05 ~ 2026-06）

上一代项目 quant-crypto 用 5 周时间完成了大量基础设施：

| 资产 | 状态 | 位置 |
|---|---|---|
| TimescaleDB 数据湖 | ✅ 631 万行 1m OHLCV（6 个 OKX 永续对，2 年回补）+ 质量标记表 + 多周期连续聚合 | `D:\Projects\quant-crypto` |
| 衍生品特征数据 | ✅ funding / mark-index basis / open interest 已回补 | `db/migrations/003` |
| Kronos 信号基建 | ✅ Kronos-base GPU 推理，RankIC > 0.05（自定"强有效"门槛） | `kronos-signal/` |
| 信号缓存模式 | ✅ 预计算 → feather → 策略按时间戳读取，**已通过无前视审计** | `freqtrade/user_data/kronos_cache/` |
| Freqtrade 执行 + 风控 | ✅ dry-run 运行；CircuitBreaker / CorrelationGuard / DrawdownGuard 验证触发 | `risk/` |
| 验证协议 | ✅ 选择期 + 最终 90 天留出门，正确拦截了所有过拟合候选 | `scripts/validate_*` |
| 监控 | ✅ Grafana + Prometheus + 信号质量监控（60m 收益回填、7 天滚动 IC） | `grafana/`, `prometheus/` |

**最终状态：`blocked_no_paper_candidate`** —— 所有候选（低频 Ridge/HGB、regime 增强、成本感知、衍生品 basis）全部死在最终留出期，Phase 5/6 未进入。

### 1.2 根因诊断

系统没有坏，坏掉的是 **alpha 假设吞吐量**：

- 5 周只测了 3 个信号族（Kronos 择时 / OHLCV+衍生品特征 Ridge/HGB / 阈值网格），每个族手工调数周；
- 量化中诚实 OOS 通过率通常 1~5%，需要每周 100+ 假设的测试量，当前每周约 5 个；
- 留出期样本量不足（69 笔交易的 FAIL/PASS 判定统计上不可信）；
- Kronos 5m 信号 RankIC > 0.05 但无法在成本后货币化——信号存在，**成本墙**未正面攻坚。

### 1.3 项目决策

1. **不重造轮子**：复用成熟开源。**Vibe-Trading**（HKUDS，20 万行 Python）作为研究回测与复盘总结的上层建筑；**Freqtrade** 作为交易执行基础设施。
2. **清算迁移 quant-crypto**：数据湖、信号缓存模式、验证门禁、风控三件套、监控栈一次性并入本仓（迁移清单见 [F001 migration-plan](features/0.1/F001-quant-crypto-migration/migration-plan.md)），原仓库归档废弃，只做必要适配。
3. **补齐唯一致命缺口**：因子自动挖掘模块（程序化批量生成 + 统一评测 + 生命周期管理）。

---

## 二、产品定位与目标

### 2.1 一句话定位

> AlphaMill（中文别名：淘沙）是一个**以因子假设吞吐量为核心指标**的加密量化研究系统：程序化批量挖掘因子 → 统一评测 → 严格留出门 → Freqtrade 执行，Vibe-Trading 作为研究/回测/复盘的上层建筑。

### 2.2 目标（含量化验收）

| ID | 目标 | 验收指标 |
|---|---|---|
| G1 | 因子假设吞吐量 ×20 | ≥ **100 个因子候选/周** 进入统一评测台（当前 ~5/周） |
| G2 | 验证协议不降级 | 100% 候选经过：选择期 → 最终 90 天留出（≥30 笔交易）才可进入 paper |
| G3 | Vibe-Trading 上层建筑接入 | ① Parquet→local loader 第二意见回测跑通；② agent 复盘工作流产出失败归因报告 |
| G4 | Freqtrade 执行基建继承 | 信号缓存契约兼容 kronos_cache；留出通过候选 ≤1 天内可挂 dry-run |
| G5 | 全链路可复现 | 100% 实验有 manifest（数据版本 + 代码版本 + 参数 + 结果摘要） |

### 2.3 非目标（明确排除）

- ❌ 不重建数据管道/数据湖（quant-crypto 数据资产整体迁入，见 docs/05）
- ❌ 不替换 Freqtrade 执行引擎、不重建风控（继承 CircuitBreaker 等）
- ❌ 不做实盘：Phase 6 前置条件不变——必须有候选通过最终留出（quant-crypto 决策报告的规则原样继承）
- ❌ 不追求全市场覆盖：先做 OKX USDT 永续 30~50 对、1h/4h 低频
- ❌ 不用 TradingView 作为数据源（仅保留可选的可视化/Alert 层）

---

## 三、用户与核心场景

用户即项目所有者（研究员 + 交易员一体）。

| # | 场景 | 期望流程 |
|---|---|---|
| S1 | 批量挖掘因子 | 挖掘器（遗传/表达式/LLM）在 12~50 对数据上跑一代 → 产出 N 个因子定义 → 自动进评测台 |
| S2 | 统一评测 | 因子 → RankIC / IC 衰减 / 分市场状态 / 分位数收益 → 存活者进回测与留出 |
| S3 | 第二意见回测 | 存活候选同时投喂 Vibe-Trading 回测引擎（local loader 吃 Parquet），与 Freqtrade 级回测互相校验 |
| S4 | 失败复盘 | 留出失败的候选 → Vibe-Trading agent 读取实验 manifest + 报告 → 产出归因与新假设 |
| S5 | 部署 | 留出通过 → 信号写 feather 缓存 → Freqtrade 策略模板挂载 → dry-run → paper |
| S6 | 生命周期管理 | 已部署因子持续衰减监控（7 天滚动 IC 已有）→ 衰减超限自动降权/下线 |

---

## 四、功能需求

### FR1 数据桥（Data Bridge）

- FR1.1 定时任务将 TimescaleDB 核心表导出为 **Parquet 分区 + manifest.json**（来源、抓取时间、口径、版本号）。
- FR1.2 双口径：`close_adjusted`（算收益）与 `close_raw`（模拟成交）分离存储。
- FR1.3 宇宙扩容：复用 `discover_okx_swap_universe.py`，从 6 对扩到 30~50 对，质量标记流程沿用。
- FR1.4 Kronos 缓存与衍生品特征表纳入导出范围。

### FR2 因子工厂（Factor Factory）★ 核心

- FR2.1 **生成器**：至少两种可插拔后端——程序化（**AlphaGen RL 挖掘为主**，vendor 策略见 doc 03；GP/表达式枚举对照）与人工/LLM 辅助（论文因子、假设清单）。生成器只负责产出**因子定义**，不做评测。
- FR2.2 **统一评测台**：由 `kronos_rankic_eval.py` / `kronos_ic_decay_eval.py` 泛化而来——输入任意因子信号序列，输出 RankIC、IC 衰减曲线、分市场状态表现、分位数分组收益。评测台与生成器完全解耦。
- FR2.3 **因子注册表**：元数据（定义、参数、数据依赖、所属生成器、评测结果摘要、生命周期状态 active/monitoring/decayed/disabled），带 IC 相关性查重（与现存因子 |IC 相关| > 0.99 拒绝，0.90~0.99 标记变体）。
- FR2.4 多重检验控制：候选通过数随时间累积时，显著性阈值需要校正（deflated significance / 白噪声基准对照）。

### FR3 验证门禁（原样继承 + 补强）

- FR3.1 选择期：验证集上选候选，规则先于数据确定。
- FR3.2 最终 90 天留出：≥30 笔交易才允许 FAIL/PASS 判定（解决 quant-crypto 的欠功效问题）。
- FR3.3 无前视审计：每个新因子必须通过独立逐 K 线重放器（复用 `independent_cross_backtest.py`）+ 信号缓存时间戳对齐检查。
- FR3.4 成本敏感性：taker/maker/零成本三档回测，成本后收益为主要指标。

### FR4 Vibe-Trading 接入（研究上层建筑）

- FR4.1 Parquet 湖接入 Vibe-Trading `local` loader（`local:` 前缀，禁止静默回退网络源）。
- FR4.2 第二意见回测：存活候选在 Vibe-Trading 引擎（含 quantlib、MC/Bootstrap/Walk-Forward 验证）复跑，与 Freqtrade 级回测差异需可解释。
- FR4.3 agent 复盘工作流：输入失败实验的 manifest + 报告 → 产出归因分析 + 新特征假设清单（人审后进入 FR2.1 生成器队列）。
- FR4.4 因子生命周期：参考其 SDM（注册/状态/衰减扫描）模式，对接 FR2.3 注册表。
- FR4.5 **边界**：不使用 Vibe-Trading 的实盘交易栈（与现有风控重复）；不作为行情数据源。

### FR5 信号缓存与部署

- FR5.1 信号缓存契约与 `kronos_cache` 兼容：feather 按日分片，列 = (timestamp, pair, signal_value, [confidence])，时间戳为信号确认时刻。
- FR5.2 Freqtrade 策略模板：读缓存 → 入场/出场条件 → `confirm_trade_entry` 风控钩子，模板化使新因子接入 ≤ 半天。
- FR5.3 部署流水线：留出 PASS → 自动生成策略配置 → dry-run 冒烟 → 人工确认挂载。

### FR6 实验台账与复盘

- FR6.1 每个实验写 manifest：数据快照版本、代码 commit、参数、评测结果、结论（PASS/FAIL + 原因）。
- FR6.2 失败案例库：留出失败候选的归因报告沉淀，供 S4 场景与后续生成器参考。

---

## 五、非功能需求

| 类别 | 要求 |
|---|---|
| 可复现 | 任一历史结果可从 manifest 从零复现（对齐 research.md 第八节验收标准） |
| 无前视 | 所有因子定义过 AST 纯度检查（借用 Vibe-Trading Alpha Zoo 的 lookahead 哨兵思路）；评测/回测分离数据窗口 |
| 成本现实 | 默认按 taker 0.05% + 滑点建模；maker-only 策略显式声明 |
| 安全 | 实盘前置条件不变；API key 仅存 `.env`/系统凭据库；Vibe-Trading 仅本机回环运行 |
| 资源 | 复用现有单机（RTX 4060 Laptop GPU）；挖掘/评测为 CPU 密集可夜间批跑 |
| 里程碑纪律 | 每个里程碑出口有可运行验证脚本（沿用 quant-crypto verify 习惯） |

---

## 六、里程碑

| 里程碑 | 内容 | 出口标准 | 预估 |
|---|---|---|---|
| **M0 资产清算迁移** | docs/05 迁移清单：数据卷 + 采集器 + Kronos 上游化 + 风控/监控搬迁 | verify 全绿：行数对账 / Kronos /health / Freqtrade dry-run / 监控有数据 | 2-3 天 |
| **M1 数据桥 + 统一评测台** | FR1 全部 + FR2.2/2.3（kronos 评测器泛化） | 任意 feather 信号 → 一条命令出 RankIC/衰减/分状态报告；Kronos 现有缓存全部重新入库 | 1 周 |
| **M2 因子挖掘管线** | FR2.1 程序化生成器（**AlphaGen vendor + 现代栈冒烟 → feather→tensor 适配器**）+ FR2.4 + FR3.3 | 冒烟：现代栈跑通 1 个 PPO epoch 产出因子；单次挖掘 ≥50 候选 → 自动评测 → ≥5 个进选择期；无前视审计通过 | 2 周（冒烟 1-2 天 + 适配器 ~1 周） |
| **M3 Vibe-Trading 接入** | FR4.1/4.2/4.3 | Parquet→local loader 回测跑通并与 Freqtrade 级回测出对比报告；agent 复盘工作流产出首份归因报告 | 1 周 |
| **M4 生产循环** | FR5 + FR6 + 宇宙扩容 | 每周 ≥100 候选进评测；首个候选通过 90 天留出（≥30 笔）→ dry-run | 持续 |

---

## 七、风险与缓解

| 风险 | 缓解 |
|---|---|
| 程序化挖掘（RL/GP）大量产出伪因子（泄漏/幸存者偏差/RL reward hacking） | AST 纯度门 + 独立重放审计 + 白噪声对照 + 多重检验校正（FR2.4/FR3.3） |
| 扩宇宙后数据质量下降 | 沿用 quant-crypto 质量标记表与缺失告警流程 |
| 信号仍过不了成本墙 | 成本三档敏感性为一级指标；maker-only/微择时 overlay 方向优先实验 |
| Vibe-Trading 学习成本 | 只接 4 个面：local loader、回测工具、quantlib、agent 复盘；不碰其实盘栈 |
| 吞吐量上来后人审瓶颈 | 评测台自动分诊：RankIC + 相关性查重先行过滤，人只看存活者 |
