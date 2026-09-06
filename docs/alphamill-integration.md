# AlphaMill — 集成设计

> 版本：v0.1 | 日期：2026-09-06 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)
> ⚠️ 本文档为集成操作细节；外部依赖管理策略已提炼至 [ADR-0002](decisions/0002-external-dependency-policy.md)。
> 本文回答：AlphaMill 的三个外部系统（数据湖 / Vibe-Trading / Freqtrade）各自怎么接、接口长什么样、出问题怎么隔离。

---

## 一、数据桥：TimescaleDB → Parquet 湖

### 1.1 为什么需要这一层

- Vibe-Trading 的 `local` loader 支持 CSV / Parquet / DuckDB，**不直连 Postgres**；
- 研究需要不可变快照：TimescaleDB 数据会被回补/修订，Parquet 快照 + 版本号保证"同一版数据永远算出同一版结果"；
- 双口径落盘（adjusted/raw）在导出时点固定，避免消费端各自解释。

### 1.2 导出设计

| 项 | 设计 |
|---|---|
| 调度 | 每日 03:00 增量导出（昨日分区），每周日全量校验 |
| 分区 | `lake/ohlcv_1m/exchange=<ex>/pair=<pair>/date=<YYYY-MM-DD>.parquet` |
| 口径列 | crypto 无复权概念，保留 `open/high/low/close/volume` + `funding_rate/open_interest/basis`（衍生品表同构导出） |
| manifest | 每次导出写 `lake/_manifests/<dataset>/<data_version>.json`（schema 见架构文档 4.4） |
| 一致性 | 导出后行数/校验和与 TimescaleDB 对账；不一致则该 data_version 标记 `invalid`，消费端拒绝读取 |
| 质量继承 | `ohlcv_quality_flags` 未解决标记 > 0 的分区在 manifest 里标注，评测台可选跳过 |

### 1.3 宇宙扩容（FR1.3）

1. 运行 quant-crypto 的 `discover_okx_swap_universe.py`，按流动性（日均成交额）+ 上线时长（>180 天）筛 30~50 对；
2. 复用 `historical_backfill.py` 分批回补（限速保护）；
3. 新 pair 先进质量流程（缺失检测/异常跳变），通过后才入导出清单。

---

## 二、Vibe-Trading 接入

### 2.1 安装与形态

```bash
pip install vibe-trading-ai        # PyPI 包，MIT
vibe-trading --version             # 本项目只用到 CLI + 本机 REST，不开远程访问
```

- 仅本机回环运行；不配置 `API_AUTH_KEY` 之外的暴露面；不启用 shell 工具（保持默认关闭）。
- 其审计/manifest 机制天然契合 FR6（每次 run 有 hash manifest + run_card），实验台账直接引用其 run_id。

### 2.2 Parquet 湖 → local loader

Vibe-Trading 的 `local` loader 通过 `local:` 前缀符号读取本地文件，且**禁止静默回退到网络源**（口径可控的关键）。接入配置：

```text
# local loader 数据根目录指向 alphamill 湖（按其文档配置 data root）
# 回测 config.json 示例
{
  "codes": ["BTC-USDT"],          # 映射到湖内 pair 命名（vibe_bridge 做名称翻译）
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "interval": "1D",
  "source": "local"
}
```

`vibe_bridge/local_loader_config/` 维护：alphamill pair 命名 ↔ local loader 符号 的映射表、数据根路径、可用区间检查。

### 2.3 第二意见回测流程（FR4.2）

```text
候选通过统一评测台（RankIC 等达标）
   ↓
① Freqtrade 级回测（既有流程，含成本三档）
   ↓ 并行
② Vibe-Trading 回测（同窗口、同成本假设、local 源）
   ↓
差异报告：两者收益曲线/成交列表 diff，逐笔归因（数据差异 / 撮合假设差异 / 信号时间戳差异）
   ↓
差异可解释 → 候选进留出门；不可解释 → 回退排查（默认怀疑②的口径或①的前视）
```

### 2.4 Agent 复盘工作流（FR4.3）

- 输入物：失败实验的 manifest（alphamill 侧）+ Vibe-Trading run_card（若该候选跑过②）+ 因子注册表条目。
- 工作流（`vibe_bridge/postmortem/`）：收集材料 → `vibe-trading run -p "<复盘 prompt>"` → 归因报告落 `reports/postmortem/` → 提取新假设进入生成器队列（人工审阅后生效）。
- 论文→因子：上传论文 PDF，参照其 SDM 技能的五阶段（INGEST→EXTRACT→IMPLEMENT→EVALUATE→MONITOR），产出的因子定义走 AST 纯度门后入库。

### 2.5 明确隔离

| 不使用 | 原因 |
|---|---|
| 实盘交易栈（mandate/order_guard/HALT） | 与 quant-crypto 风控三件套职责重复，双栈徒增状态同步成本 |
| 行情 loader 网络源 | 数据口径必须收敛到自家湖，防止"哪个源先回答用哪个" |
| MCP 写类工具 / shell 工具 | 最小权限；alphamill 的写路径全部走自家脚本 |

---

## 三、Freqtrade 桥

### 3.1 信号缓存 → 策略（继承 kronos_cache 模式）

```python
# freqtrade_bridge/strategy_template.py.j2 渲染产物骨架
class {{ strategy_class }}(IStrategy):
    timeframe = "{{ timeframe }}"          # 1h / 4h
    can_short = True
    stoploss = {{ stoploss }}
    startup_candle_count = {{ warmup }}

    def informative_pairs(self):
        return self._cache_pairs()          # 从 signal_cache 目录自动发现

    def populate_indicators(self, df, metadata):
        sig = self._load_signal_cache("{{ factor_id }}", metadata["pair"])
        # 按时间戳 merge_asof 到 df，只允许 t 信号影响 t 收盘后的决策
        df["factor_signal"] = self._align_no_lookahead(df, sig)
        return df

    def populate_entry_trend(self, df, metadata):
        df.loc[df["factor_signal"] > {{ entry_threshold }}, "enter_long"] = 1
        df.loc[df["factor_signal"] < -{{ entry_threshold }}, "enter_short"] = 1
        return df

    def confirm_trade_entry(self, *args, **kwargs):
        return self._risk_hooks(*args, **kwargs)   # 挂 CircuitBreaker / CorrelationGuard
```

### 3.2 无前视对齐规则（审计器逐条检查）

1. 缓存行时间戳 = 信号确认时刻（K 线收盘之后）；
2. 策略在 t K 线上只能使用 `timestamp ≤ t 收盘时刻` 的信号（`merge_asof` 方向固定 backward）；
3. warmup 期禁止产生交易；
4. 审计不通过 → 部署流水线拒绝生成配置。

### 3.3 部署流水线（FR5.3）

```text
留出 PASS → writer 写 signal_cache → 渲染策略模板 → freqtrade backtesting 冒烟（7 天）
        → dry-run 挂载（与现有 KronosFusionStrategy 并存，独立策略类）
        → 人工确认 → paper
```

---

## 四、验证门禁迁移设计

quant-crypto 的门禁脚本参数化迁移到 `validation/`：

| 迁移件 | 改造点 |
|---|---|
| 选择期脚本 | 窗口/阈值外置配置（`validation/config.yaml`），规则先于数据确定并 git 提交 |
| 最终 90 天留出 | 新增 **≥30 trades 判定门槛**：样本不足输出 `UNDERPOWERED`（不判 PASS 也不判 FAIL，触发扩宇宙/延长窗口） |
| 独立重放器 | 接口化为 `no_lookahead_audit(factor_def)`，进入因子工厂流水线而非一次性脚本 |
| 成本敏感性 | 三档（taker/maker/零成本）为标准输出列，成本后 Sharpe 为排序主键 |
| KPI 检查 | 继承阈值（Sharpe>1.5 / MDD<20% / WinRate>50% / 月均>20 笔），报告格式沿用 `reports/phase4-kpi-*` |

**多条候选同时通过留出的处理**：按成本后 Sharpe 排序，取 Top1 进 dry-run；其余进入 monitoring 队列（防止 paper 组合同时验证多个高相关候选）。

---

## 五、外部依赖管理策略（vendor / fork / 原样依赖）

> 判断原则：**改动深度决定集成距离**。要动大手术的 vendor 进主仓；只用扩展面的原样依赖；fork 仅适用于"要上游全部 + 必须改核心 + 上游不收 PR"的窄缝——本项目三个引入项没有一个落在缝里，**一律不 fork**。

| 引入项 | 方式 | 理由 | 版本策略 |
|---|---|---|---|
| **AlphaGen** | **vendor** 进 `factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md`；不考虑跟随上游 |
| **Freqtrade** | 原样依赖（官方 docker 镜像 + `user_data/` 插件层） | 插件架构零改码即可用（quant-crypto 已验证）；上游月更，fork = rebase 跑步机 | pin 镜像 tag（如 2026.8），里程碑边界升级 |
| **Vibe-Trading** | 原样依赖（pip pin + 本机 CLI/服务） | 只碰 4 个外部面（loader/回测工具/quantlib/agent），全在配置层 | pin 小版本；只在里程碑边界升级（保证实验结果可比） |
| Kronos | 独立服务（上游 clone + pin commit，权重 HuggingFace 下载） | 模型代码上游化；服务薄壳为本仓 `kronos_service/` | pin 上游 commit；见 docs/05 |

### vendor 卫生规则（AlphaGen 专用）

1. vendor 目录内**最小 diff**：贴近上游原貌，每处修改标注 `# [alphamill] <原因>`；
2. 胶水代码（feather→tensor 适配器、FactorDef 包装）放 vendor **外面**（`generators/` 本体），保持可整体替换；
3. `alphagen_vendor/VENDORED.md` 记录：上游 repo + commit hash、vendor 日期、修改清单、许可说明（个人私有使用）；
4. 升级路径：上游若复活且需要新特性，按 VENDORED.md 的修改清单手工重移植（diff 小，成本可控）。

### 上游 bug 应对（Freqtrade / Vibe-Trading）

- 不改源码、不开 fork：上游提 issue → 策略/桥接层 monkey-patch 过渡（显式注释 + 关联 issue 号）→ 上游修复后撤销；
- 升级纪律：只在里程碑边界升级依赖版本；升级后先跑冒烟验证再继续实验。

---

## 六、失败模式与隔离

| 失败模式 | 隔离设计 |
|---|---|
| 导出桥数据错误 | manifest 对账 + data_version 失效标记；评测台拒绝 invalid 版本 |
| Vibe-Trading 升级破坏行为 | 回测只在 M3/M4 验证点跑；其 run manifest 记录版本，可复现到具体版本 |
| 生成器产出垃圾海啸 | 评测台分诊阈值（RankIC + 查重）先行过滤；注册表只收存活者 |
| Freqtrade 策略读取了坏缓存 | 冒烟回测前置 + 审计器校验时间戳对齐；坏缓存直接拒绝挂载 |
| 夜间批处理超时 | 生成器/评测台分任务队列，单代失败不回滚已入库结果 |
