# AlphaMill — 因子挖掘与 ML 开源选型调研

> 版本：v0.1 | 日期：2026-09-06 | 调研基线：GitHub API 元数据 + 2026-09 时点网络证据（两个独立调研交叉核对）
> 配套：[alphamill-prd.md](./alphamill-prd.md)（FR2 因子工厂）、[alphamill-architecture.md](./alphamill-architecture.md)
> ⚠️ 本文档为调研证据归档；选型决策已提炼至 [ADR-0001](decisions/0001-factor-mining-engine.md)，依赖管理策略见 [ADR-0002](decisions/0002-external-dependency-policy.md)。

---

## 一、选型结论（TL;DR）

| 槽位（映射 PRD） | 选型 | 一句话理由 |
|---|---|---|
| **生成器·主引擎**（FR2.1） | **AlphaGen**（`ICT-FinD-Lab/alphagen`）✅ 已锁定 | RL 批量产因子最匹配"100+/周"目标；张量核心与 qlib 数据层解耦，feather→tensor 适配器是被验证过的模式（纯个人私有使用，LICENSE 风险降级，见第五节） |
| **生成器·对照基线**（FR2.1） | **AlphaGen 仓库自带 gplearn/dso**（不单独引入） | 直接对接 AlphaGen；GP 对照白捡，算子适配在需要时再做 |
| **候选种子**（FR2.1） | **py-alpha-lib**（GTJA191）+ WQ101 参考 | 现成公式库做冷启动候选宇宙 |
| **评测台**（FR2.2/2.4） | **自研泛化**（kronos_rankic_eval）+ **purgedcv**（CV 层）+ alphalens-reloaded（可选） | 已有资产泛化成本最低；purged CV 补多重检验防线 |
| **快速候选回测** | **vectorbt OSS v1.1.0** | 向量化 sweep 秒级跑完 12~50 对；留出门前置粗筛 |
| **信号研究 ML**（可选深水区） | **Qlib v0.9.7**（dump_bin 路径） | RollingGen 滚动重训与本项目 walk-forward 协议 1:1 对应；但表达式引擎必须转 bin 格式 |
| **执行侧 ML** | **FreqAI 保持现状** | 逐对时序自适应模型——执行侧够用，**不要**拿它做横截面因子研究 |
| **时序基础模型** | **Kronos**（既有资产，保持） | AAAI 2026，微调工具已发布；定位为"又一个信号族"而非策略 |
| **LLM 挖掘补充**（观察项） | **RD-Agent(Q)** / FactorMiner | 观察而非引入：Qlib 耦合重 / 项目太年轻 |

**已决策（2026-09-06）**：主引擎 = **AlphaGen**（纯个人使用 + 私有仓库管理，LICENSE 风险降级为非阻塞）。**直接对接**：vendor 核心 + 现代依赖栈，跳过"先上 gplearn"的前置阶段；仓库内自带的 `gplearn/`/`dso/` 仅作对照基线，不单独引入。宇宙扩容到 30~50 对与对接**并行推进**（横截面 reward 在 6~12 对上噪声大，扩宇宙是产出质量的前提）。

---

## 二、因子挖掘引擎对比（2026-09 时点）

| 项目 | 方法 | 许可证 | 活跃度 | crypto 适配性 | 集成成本（pandas/feather 栈） |
|---|---|---|---|---|---|
| [ICT-FinD-Lab/alphagen](https://github.com/ICT-FinD-Lab/alphagen)（原 RL-MLDM） | RL(PPO) 表达式生成 + 线性协同池；已并入 LLM 扩展（HARLA, FCS 2026） | **无 LICENSE** ⚠️ | 1.2k★，pushed 2026-06 | 高——核心张量化，适配模式已被第三方验证 | **中**：写 feather→tensor 数据适配器，绕开 qlib bin |
| [trevorstephens/gplearn](https://github.com/trevorstephens/gplearn) | 遗传规划符号回归（sklearn API） | BSD-3 | 1.9k★，v0.4.3（2026-01-07，4 年来首次发版） | 高——通用，算子自备 | **低-中**：自定义适应度 + 算子集 + walk-forward 自管 |
| [microsoft/qlib](https://github.com/microsoft/qlib)（仅表达式引擎视角） | 表达式 AST 引擎（Alpha158/360，~40 算子） | MIT | 48.3k★，pushed 2026-09 | 不适用——引擎绑死 bin 数据 | **高**：必须 dump_bin；maintainer 确认无 DataFrame 直通 |
| [microsoft/RD-Agent](https://github.com/microsoft/RD-Agent)（RD-Agent(Q)） | LLM 多智能体因子+模型挖掘，Qlib 闭环 | MIT | 14.5k★，v0.8.0，pushed 2026-09（NeurIPS 2025） | 中——Qlib/中证默认，移植需换数据路径 | **高**：LLM API + Qlib 回测栈 |
| [RndmVariableQ/AlphaAgent](https://github.com/RndmVariableQ/AlphaAgent)（KDD 2025） | LLM agent + AST 新颖性正则 | **无 LICENSE** ⚠️ | 407★，pushed 2026-07 | 低-中（A 股/SPX 为主，基于 RD-Agent） | 高 |
| [ZhuZhouFan/AlphaQCM](https://github.com/ZhuZhouFan/AlphaQCM) | AlphaGen 的分布式 RL 变体 | MIT | 121★，pushed 2025-07 | 同 AlphaGen | 中 |
| [gta0804/AlphaPROBE](https://github.com/gta0804/AlphaPROBE)（2026 论文） | 进化挖掘 + 检索 | 无 | 93★，pushed 2026-02 | 低（qlib bin） | 高 |
| [DulyHao/AlphaForge](https://github.com/DulyHao/AlphaForge)（AAAI 2025） | 生成-预测网络 + 动态组合 | 无 | **pushed 2024-09，休眠** ⚠️ | 低（qlib） | 高 |
| [minihellboy/factorminer](https://github.com/minihellboy/factorminer)（2026） | LLM 驱动 + 类型化 OHLCV DSL + 经验记忆 | MIT | 107★，pushed 2026-08 | 高（OHLCV 原生，自述 A 股+crypto 验证） | 中——太年轻，论文出处未独立核实 |
| [Huang-Hg/alpha-foundry](https://github.com/Huang-Hg/alpha-foundry)（2026） | 类型化 GP(DEAP) + GFlowNet，**crypto 永续原生** | MIT | 9★，created 2026-06 | 很高（永续 funding 进回测核） | 中——零社区验证 |

### 公式库（种子候选宇宙，非挖掘器）

| 项目 | 说明 | 许可证 | 状态 |
|---|---|---|---|
| [msd-rs/py-alpha-lib](https://github.com/msd-rs/py-alpha-lib) | GTJA191（190/191 可算），Rust 核 + pandas 参考实现，长表 OHLCV 输入，PyPI 可装 | BSD-2 | 118★，pushed 2026-09-03，**首选** |
| [yli188/WorldQuant_alpha101_code](https://github.com/yli188/WorldQuant_alpha101_code) | WQ101 权威 pandas 实现，helper 算子可复用 | **无** | **死（2019）**，仅公式参考 |
| [Daic115/alpha191](https://github.com/Daic115/alpha191) | GTJA191 宽表 pandas | 无 | 停滞 2023，次要 |
| [JustinF8/qlib-factor-zoo](https://github.com/JustinF8/qlib-factor-zoo) | GTJA191+Alpha101 的 qlib 表达式版 + 50 自定义算子 | MIT | 仅当走 Qlib 路线时有用 |

> ⚠️ 公式库共同注意：均假设 A 股日频——引用行业/市值/财报的因子直接跳过；crypto 24/7 日历需重定义窗口（`days(N)` → `bars(N×24)`）。

---

## 三、关键证据

### 3.1 AlphaGen（主选）——活跃、已迁移、数据层可替换

- `RL-MLDM/alphagen` 重定向至 `ICT-FinD-Lab/alphagen`（pushed 2026-06-04），README 已含 `alphagen_llm` 与 HARLA 扩展。
- 内置数据路径依赖 qlib bin（[`alphagen_qlib/stock_data.py` 中 `initialize_qlib`](https://github.com/ICT-FinD-Lab/alphagen/blob/259687e8f316994426416c530a94842a2fe6405e/alphagen_qlib/stock_data.py#L19-L25)），**但挖掘核心（expression/tensor calculator/LinearAlphaPool）不触 qlib**——两个独立项目证明可替换：[Wrigggy/alpha-harness](https://github.com/Wrigggy/alpha-harness)（"CryptoStockData produces the same tensor format AlphaGen expects — no Qlib dependency for crypto"，在 crypto 上跑通 AlphaGen PPO）；`jintaoxie02/alphagen_crypto`（BTC 管线，⚠️ 现 404，仅作先例佐证）。
- 算子集（[KDD'23 论文 Appendix A](https://arxiv.org/abs/2306.12964)）：截面 Abs/Log/四则/Greater/Less；时序 Ref/Mean/Med/Sum/Std/Var/Max/Min/Mad/Delta/WMA/EMA/Cov/Corr + 特征/常量/时间增量 token——**特征就是具名列**，funding/OI/basis 直接作为额外张量进入。
- Reward = 对线性池的增量 IC 贡献 → 与本项目 RankIC 评测台天然对齐。
- **无 LICENSE 文件**（GitHub license API 404）。本项目纯个人使用 + 私有仓库，实际执行风险可忽略，**非阻塞**；若未来公开分发或商业化，再向作者澄清。
- **核心停滞与依赖腐化（2026-09 核实）**：核心代码（`alphagen/data/expression.py`、`requirements.txt`）最后实质提交 **2024-12-18**（约 21 个月前），此后仅 README/`alphagen_llm` 扩展。issue 区确认依赖烂：#57（requirements 过老）、#59（numpy 冲突）、#62（qlib 依赖不正确）。requirements.txt 本身即坏：`qlib==0.0.2.dev20` 是**装错的包**（微软 qlib 的 PyPI 包名为 `pyqlib`），`numpy==1.20.1`/`pandas==1.2.4`/`matplotlib==3.3.4` 均为 2020-2021 年版本。
- **对接策略：vendor 而非安装**——① 将 `alphagen/` 核心（expression / tensor calculator / LinearAlphaPool）vendor 进 `factor_factory/generators/alphagen_vendor/`；② **整个丢弃 requirements.txt**，自定现代栈（torch 2.x 最新 + numpy 2.x + pandas 2.x + sb3 最新/gymnasium），不装 qlib/baostock/旧 matplotlib；③ 自写 feather→tensor 数据适配器替代 `alphagen_qlib`（本来就是计划，顺带绕开装错包的坑）；④ PPO 训练器用 stable-baselines3 2.0 + gym 0.26，升到 sb3 最新版需小改 env wrapper（gym→gymnasium）。冒烟目标：现代栈跑通 1 个训练 epoch 并向池子产出因子。预估 shakedown 1-2 天 + 适配器约 1 周。
- **冒烟即闸门（time-box 2 个工作日）**：调研加深后（核心冻结 21 个月 + requirements 腐化），AlphaGen 的优势从"明确更好"收窄为"**结构上更好 + 冒烟验证的正确**"——上游维护优势已被冻结事实抹掉，剩下的是代码冻结带不走的硬优势（协同池 / GPU 张量评估 / 量化原生算子）。闸门流程：第 1 天 vendor 核心 + 现代栈跑通 1 个 PPO epoch；第 2 天产出因子并做 RankIC 计算对齐检查。**通过 → 锁定主引擎，进入适配器开发；超时或坑深 → 立即降级，不沉没成本**：
  - **L1**：AlphaGen 表达式求值器 + 自写简单搜索（随机/枚举），绕开最框架耦合的 sb3/RL 部分——GPU 批量评估这一核心优势保留，算子实现直接从 `expression.py` 移植；
  - **L2**：纯 gplearn（1h/4h 重采样 + 自建算子库 + 滚动 fitness 防全样本泄漏）。
- **附带发现**：仓库内已 vendor `gplearn/`（+`gp.py`）与 `dso/`（Deep Symbolic Regression）作为论文基线——双引擎/多引擎的对照实现是现成的，无需单独引入 gplearn 项目（L1/L2 降级阶梯的料就在仓库里）。issue 区的研究性提醒（#61 测试 IC 为负、#49 IC 高但回测差、#64 池权重过拟合风险）与本项目"评测台 + 留出门"防线一一对应；#53 的数据窗口边界 IndexError 在自写数据层时注意对齐。

### 3.2 gplearn（基线）——复活但泄漏自管

- v0.4.3（2026-01-07，[发版 commit](https://github.com/trevorstephens/gplearn/commit/09b5f22c675c407f9610533680c30607a3f9f477)），要求 sklearn ≥1.8、Python ≥3.11；repo pushed 2026-08。
- 自定义适应度：[`make_fitness(*, function, greater_is_better, wrap=True)`](https://github.com/trevorstephens/gplearn/blob/0390aea8639ce5f6c0b388400e07b58c05acad6a/gplearn/fitness.py#L50)——RankIC 直接可插。并行：joblib（[`Parallel` in `genetic.py`](https://github.com/trevorstephens/gplearn/blob/0390aea8639ce5f6c0b388400e07b58c05acad6a/gplearn/genetic.py#L13-L18)，`n_jobs` 构造参数）。
- **泄漏警示（结构性分析，无权威 issue 可引）**：`fit()` 对整段数组做全样本适应度评估，无 walk-forward 概念——GP 全样本 RankIC 选择 = 样本内选择偏差。必须自实现滚动/扩展窗口适应度或逐代 train/validate 切分。
- 性能：逐程序 numpy 评估跑 631 万行分钟线会很慢——建议重采样（1h/4h）或小切片搜索；AlphaGen 的 GPU 批量面板评估更适合分钟级吞吐目标。

### 3.3 Qlib 表达引擎——**不可独立提取**（maintainer 确认）

- [issue #1988](https://github.com/microsoft/qlib/issues/1988)（2025-08）：表达式引擎位于 DataHandler 基础设施之下，唯一存储实现是 `.bin`（"currently there is no other version of implementation"）；DataFrame 用户必须走 `scripts/dump_bin.py`。
- 算子是惰性 AST，经 `feature.load(instrument, ...)` 从 qlib 数据层取数（[ops.py](https://github.com/microsoft/qlib/blob/7ccf3f76/qlib/data/ops.py)）。
- 未发现维护中的"只提取求值器"的 fork；社区实践是用自有 pandas 算子重写 Alpha158 表达式（表达式**字符串**可移植：见 [Alpha158DL](https://github.com/microsoft/qlib/blob/main/qlib/contrib/data/loader.py)）。
- **结论**：要 Qlib 就整建制接入（dump_bin：3-5 天 spike；滚动基准回路成熟 1-2 周），否则不碰。Qlib 其余价值仍在：[v0.9.7](https://github.com/microsoft/qlib/releases/tag/v0.9.7)（2025-08-15）、24 个模型 zoo（LightGBM/XGBoost/CatBoost/Transformer/TRA/TFT/TabNet/DoubleEnsemble…，含 IC/RankIC 基准表）、[`RollingGen`](https://github.com/microsoft/qlib/blob/main/qlib/workflow/task/gen.py)（ROLL_SD/ROLL_EX + trunc_days 防泄漏 + TaskManager）与本项目 walk-forward 协议 1:1 对应。**注意**：Qlib 1m 回测记账弱（2025 年 open issue "PortAnaRecord back test fail for highfreq data"）——分工应是 Qlib 做信号/IC 研究 + 滚动重训，vectorbt/Vibe-Trading 做真实回测模拟。官方数据集因数据安全政策暂时禁用（自带数据无影响）。

### 3.4 2024-2026 新浪潮（观察项，不引入）

RD-Agent(Q)（强但重）、AlphaAgent（无许可）、AlphaPROBE、FactorMiner（自述 crypto 验证，年轻）、alpha-foundry（crypto 原生但 9★）、AlphaQCM（MIT，AlphaGen 变体）、AlphaForge（休眠，仅作基线引用）。

---

## 四、ML 与评测配套

### 4.1 FreqAI——执行侧定位不动摇

freqtrade v2026.8（2026-08-31），模型清单（[`freqai/prediction_models/`](https://github.com/freqtrade/freqtrade/tree/develop/freqtrade/freqai/prediction_models)）：LightGBM（Reg/Clsf + MultiTarget）、XGBoost（+RF 变体）、PyTorch MLP/Transformer、ReinforcementLearner、SKLearnRandomForest（**CatBoost 已移出**）。
横截面局限（文档确认）："For each pair in the whitelist, FreqAI trains a model"——逐对训练、顺序执行（模型年龄偏斜）、不支持动态 pairlist；`include_corr_pairlist` 只是**输入侧**注入其他对的特征，不是横截面排序目标。无官方横截面扩展。**结论：FreqAI 留在执行侧（继承现状），横截面因子研究不指望它。**

### 4.2 特征工程

| 库 | 许可 | 活跃度（2026） | 判定 |
|---|---|---|---|
| [polars](https://github.com/pola-rs/polars) | MIT | pushed 每日，39.7k★ | **主力**：6.3M 行 RAM 无压力，`.over("symbol")` 滚动/分组，手写因子表达式 = 完全控制前视 |
| [functime](https://github.com/functime-org/functime) | Apache-2.0 | pushed 2026-05，1.2k★（放缓） | 可借用的 polars 原生 TS 原语（基准 ~2.5× 单序列 / ~10× groupby vs tsfresh） |
| [tsfresh](https://github.com/blue-yonder/tsfresh) | MIT | pushed 2026-07，9.3k★ | 仅作批量**发现**电池（~794 特征 + Benjamini-Yekutieli FDR）；慢、吃内存，需窗口采样 + dask |
| [featuretools](https://github.com/alteryx/featuretools) | BSD-3 | pushed 2026-07，发版慢（v1.31.0, 2024-05） | 仅当关系型 join（OHLCV ↔ funding/OI）主导时用；cutoff_time 防前视 |

### 4.3 验证库（purged / CPCV）

| 项目 | 状态 | 许可 | 备注 |
|---|---|---|---|
| [purgedcv](https://github.com/eslazarev/purged-cross-validation) | **2026-05 新建**，pushed 2026-09 | MIT | `PurgedKFold` / `PurgedGroupKFold` / `WalkForwardSplit` / `CombinatorialPurgedCV` + 路径重建 + PSR/DSR/MinTRL；sklearn 协议、354 测试、mypy strict。**选它**，但：31★ 单维护者 → pin 版本 + 考虑 vendor |
| [mlfinlab](https://github.com/hudson-and-thames/mlfinlab) | **死**（pushed 2023-10） | NOASSERTION | 已转闭源付费，不可作为依赖 |
| [skfolio](https://github.com/skfolio/skfolio) | pushed 2026-09，2.4k★ | BSD-3 | `CombinatorialPurgedCV` 可用；更偏组合优化——**保守备选** |
| timeseriescv | 2018 年起失修，已知正确性问题 | — | 回避 |

叠加方式：purgedcv 作为 CPCV/隔离层，叠在本项目既有 walk-forward + 90 天留出协议**之上**，不替代门禁。

### 4.4 Kronos（既有资产）

38.5k★，MIT，pushed 2026-04-13，AAAI 2026 接收；微调工具 2025-08-17 已发布（`finetune/`：Qlib 数据预处理、tokenizer + predictor `torchrun` 训练、Qlib 回测脚本）。mini(4.1M)/small(24.7M)/base(102.3M) 开源（HF: NeoQuasar），**large(499M) 未开源**；官方 live demo 即 BTC/USDT 1h（crypto 原生）。RTX 4060 8GB 推理与微调均可容纳（单卡跑微调脚本属合理推断，未验证）。**定位：微调后作为又一个信号族进评测台——是因子不是策略。** 集成 1-2 周。

### 4.5 vectorbt OSS（快速候选回测）

| | OSS | PRO |
|---|---|---|
| 许可 | Fair-code：Apache-2.0 + **Commons Clause**（内部研究免费，不可转售） | 专有 |
| 版本 | **1.1.0**（PyPI 2026-07-05） | 持续发版 |
| 状态 | 维护模式（修 bug），README 已改称"PRO 的社区版" | 活跃，单维护者 |
| 能力 | 向量化/Numba（可选 Rust）、参数 sweep、walk-forward splitter、组合分析 | + 混合事件驱动引擎、细粒度订单、**purged & combinatorial CV**、CCXT 接口、MCP server |
| 价格 | 免费 | $25/mo / $240/yr / $500 lifetime（2026-08 核实；另有 2026-06 来源称 $150/mo——**冲突，低置信**） |

契合点：因子矩阵 → `Portfolio.from_signals` 对 12~50 对秒级 sweep，做留出门前置粗筛。无执行层（正确——Freqtrade 管执行）。集成 1-3 天。

### 4.6 LLM agent 补充（与 Vibe-Trading 的关系）

1. **[RD-Agent(Q)](https://github.com/microsoft/RD-Agent)**——MIT，14.5k★，NeurIPS 2025，对 Qlib 的闭环 LLM 因子+模型挖掘（IC 去重、bandit 方向选择）。**最强候选补充**，但 Qlib/中证耦合——移植 crypto 需换 Qlib 配置 + StaticDataLoader parquet 路径（~1-2 周）。观察项。
2. **[FactorMiner](https://github.com/shadowto/factorminer)**（2026）——技能+经验记忆，自述 A 股**和 crypto** 双验证（110 因子、IC 门、deflated Sharpe）。年轻，先验证成熟度。
3. **[TradingAgents](https://github.com/TauricResearch/TradingAgents)**（Apache-2.0，102.7k★）——LLM 多智能体**决策**模拟，与 Vibe-Trading 角色重叠，二选一（选 Vibe-Trading）。
4. **[AI-Trader](https://github.com/HKUDS/AI-Trader)**（HKUDS，22.2k★）——与 Vibe-Trading 同源，自然共存。
5. alphalens-reloaded（0.4.5，2025-07-23，Apache-2.0）——可选的分位 tear-sheet 配件，与自研评测台互补不冲突。

---

## 五、不确定性清单（引用时需注明）

1. **AlphaGen 无 LICENSE**——事实已核实（license API 404 两次）。纯个人私有使用下风险降级为非阻塞；仅在未来公开/商业化时需重新处理。
2. `jintaoxie02/alphagen_crypto` 出现在搜索索引但仓库现 404——可证明 crypto 适配先例存在，无法给出链接。
3. AlphaAgent / AlphaForge 无 LICENSE（API 核实）；AlphaAgent 2026-07 push 之后的维护节奏未验证。
4. gplearn 时序泄漏：issue 跟踪器中未找到权威记录，按 `fit()` API 结构性分析表述。
5. FactorMiner 的论文出处与 alpha-foundry 的 crypto 能力均为 README 自述，未独立核实。
6. vectorbt PRO 定价来源冲突（$25/mo vs $150/mo）；OSS "维护模式"是 1.1.0 发版前的共识，7 月重发版未改变功能轨迹。
7. Kronos 单卡微调可行性属合理推断，未实测。
8. AlphaGen 核心 21 个月未实质更新（2024-12 后仅 README/LLM 扩展），issue 区依赖问题无上游修复动作——按 **vendor + 现代栈**策略规避，不指望上游。

---

## 六、落地映射

| PRD 需求 | 落地 | 成本 |
|---|---|---|
| FR2.1 生成器·主 | AlphaGen **vendor**（丢 requirements，现代栈 + gymnasium 化）+ feather→tensor 适配器 | 冒烟 1-2 天 + 适配器 ~1 周 |
| FR2.1 生成器·基线 | gplearn + 自定义 RankIC 适应度 + 滚动窗口（重采样 1h/4h） | 1 周 |
| FR2.1 种子 | py-alpha-lib（GTJA191）→ AST 纯度门 → 评测台 | 2 天 |
| FR2.2 评测台 | kronos_rankic_eval 泛化（M1，已在路线图） | 2-3 天 |
| FR2.4 多重检验 | purgedcv（CPCV + PSR/DSR）+ 白噪声对照 | 2 天 |
| 快速粗筛 | vectorbt OSS sweep | 1-3 天 |
| 可选深水区 | Qlib dump_bin spike → RollingGen 滚动重训 | 3-5 天 spike |
| 观察 | RD-Agent(Q) / FactorMiner / alpha-foundry | — |

**下一步（<2 分钟）**：主引擎已锁定 AlphaGen，M1（数据桥 + 统一评测台）可直接开工。可选：顺手向作者提 issue 问 crypto/OHLCV 数据适配建议（非阻塞，纯技术交流）。
