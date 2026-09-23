# AlphaMill — 集成设计

> 版本：v0.1 | 日期：2026-09-07 | 配套：[alphamill-architecture.md](./alphamill-architecture.md)
> ⚠️ 本文档为集成操作细节；外部依赖管理策略已提炼至 [ADR-0002](decisions/0002-external-dependency-policy.md)。
> 本文回答：数据栈、可选研究/Agent 工具与 Freqtrade 怎样接入稳定的 AlphaMill 契约。

---

## 一、数据桥：TimescaleDB → Parquet 湖

### 1.1 为什么需要这一层

- 生成器、评测、回测和可选第二实现需要共享同一份只读研究数据；
- 研究需要不可变快照：TimescaleDB 数据会被回补/修订，Parquet 快照 + 版本号保证"同一版数据永远算出同一版结果"；
- 双口径落盘（adjusted/raw）在导出时点固定，避免消费端各自解释。

### 1.2 导出设计

| 项 | 设计 |
|---|---|
| 调度 | 每日 **02:00** 增量导出（昨日分区），每周日 04:00 全量校验；02:00 是排序约束——NAS 备份 03:00 起跑（带 10 分钟随机延迟），导出须先完成当日分区才会被同一晚的备份带走 |
| 分区 | `lake/ohlcv_1m/exchange=<ex>/pair=<pair>/date=<YYYY-MM-DD>.parquet` |
| 口径列 | crypto 无复权概念，保留 `open/high/low/close/volume` + `funding_rate/open_interest/basis`（衍生品表同构导出） |
| manifest | 每次导出写 `lake/_manifests/<dataset>/<data_version>.json`（schema 见架构文档 4.4） |
| 一致性 | 导出后逐分区行数 + 时间边界 + `row_digest`（按主键排序的 SHA-256，两侧由同一 Python 函数计算；口径唯一权威定义见 F002 design §3）与 TimescaleDB 对账，且与导出共享同一 REPEATABLE READ 快照；不一致则该 data_version 标记 `invalid`，消费端拒绝读取 |
| 质量继承 | `ohlcv_quality_flags` 未解决标记 > 0 的分区在 manifest 里标注，评测台可选跳过 |

**数据修订政策（point-in-time）**：

- 周日全量校验发现 TimescaleDB 历史数据被修订（回补/更正）时，`data_version` 必须递增：修订内容落成新快照，旧快照不可变、原样保留；
- 新版本 manifest 相对旧版本登记修订分区清单（差异记录），可审计"哪些数据变了"；
- 在途实验不自动作废：实验 manifest 固定的 data_version 与湖内最新版本比对发现漂移时，仅打 `data_version_drift` 标记——建议在任何 gate 判定（留出/dry-run 决策）前用新版本重跑，但不强制。

### 1.3 宇宙扩容（FR1.5）

1. 运行 quant-crypto 的 `discover_okx_swap_universe.py`，按流动性（日均成交额）+ 上线时长（>180 天）筛 30~50 对；
2. 复用 `historical_backfill.py` 分批回补（限速保护）；
3. 新 pair 先进质量流程（缺失检测/异常跳变），通过后才入导出清单。

---

## 二、可选 Vibe-Trading 适配器

Vibe-Trading 只作为 FR3.7 第二实现与 FR6.4 AI 复盘的一种提供者，不是研究主链路或里程碑
前置。接入 time-box 为 1 周；超时即弃置适配器，分别退化为独立重放器/手工第二实现和其他
只读 Agent，不影响评测、门禁、组合或部署。

### 2.1 安装与形态

```bash
pip install vibe-trading-ai        # PyPI 包，MIT
vibe-trading --version             # 本项目只用到 CLI + 本机 REST，不开远程访问
```

- 仅本机回环运行；不配置 `API_AUTH_KEY` 之外的暴露面；不启用 shell 工具（保持默认关闭）。
- 每次 run 的 hash manifest 与 run_card 由 FR7 实验台账引用，不作为 AlphaMill manifest 的替代。

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

`src/alphamill/vibe_bridge/local_loader_config/` 维护 Vibe 专属读取配置；三方符号翻译的唯一真源为
湖元数据中的 `lake/_metadata/symbol_map.csv`（current 副本），历史可复现读取使用
`lake/_metadata/symbol_maps/<symbol_map_digest>.csv`。

**M1 出口标准（契约前置）**：M1 冻结 Parquet 分区与 pair 命名时，同时产出符号映射初版
（`lake/_metadata/symbol_map.csv`）并锁定 UTC；Vibe 列只在适配器启用时填写，不影响
AlphaMill ↔ Freqtrade 的强制映射：

映射键为 **(exchange, market_type, db_symbol)**——同一个 `BTC/USDT` 在现货与永续上是不同标的，
仅凭 symbol 无法无损推导（F002-D010）。csv 五列：`exchange,market_type,db_symbol,lake_pair,freqtrade_pair`。

| exchange | market_type | db_symbol（库内） | alphamill pair（湖内） | Freqtrade pair | Vibe-Trading symbol |
|---|---|---|---|---|---|
| `binance` | `spot` | `BTC/USDT` | `BTC-USDT` | `BTC/USDT` | `BTC-USDT`（能直映则同名） |
| `binanceusdm` | `perp` | `BTC/USDT:USDT` | `BTC-USDT-PERP` | `BTC/USDT:USDT` | `BTC-USDT-PERP` |

时间戳约定：全链路 UTC，K 线按交易所原始 UTC 边界切分。任意两行推导出相同 `lake_pair` 即为碰撞，
导出直接失败（`SymbolCollisionError`），不做静默去重。

契约三条：① 三方命名只经此映射表互译，禁止散落硬编码；② 无法直映的 pair 必须在初版中显式登记翻译规则，不留空；③ canonical 映射随湖元数据和 digest artifact 保存，命名变更走评审，保证历史实验可复现。

### 2.3 第二意见回测流程（FR3.7）

```text
高价值候选、实现升级或评测差异触发复核
   ↓
① Freqtrade 级回测（既有流程，含成本三档）
   ↓ 并行
② Vibe-Trading 回测（同窗口、同成本假设、local 源）
   ↓
差异报告：两者收益曲线/成交列表 diff，逐笔归因（数据差异 / 撮合假设差异 / 信号时间戳差异）
   ↓
差异可解释 → 复核完成；不可解释 → 候选冻结并排查，不以任一实现自动胜出
```

### 2.4 Agent 复盘工作流（FR6.4）

- 输入物：失败实验的 manifest（alphamill 侧）+ Vibe-Trading run_card（若该候选跑过②）+ 因子注册表条目。
- 工作流（`src/alphamill/vibe_bridge/postmortem/`）：收集不含永久确认窗的材料 → 运行只读 Agent
  → 归因报告落 `reports/postmortem/` → 新假设草案经人工审阅后进入队列。Agent 无生产写权限。
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
# src/alphamill/freqtrade_bridge/strategy_template.py.j2 渲染产物骨架
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

### 3.3 部署流水线（FR4 / FR5）

```text
因子选择期 → 组合边际贡献门 → Top-K/权重/净额化 → 冻结 PortfolioDef
        → PortfolioDef 通过 90 天留出与永久隔离最终确认
        → 部署前最近窗口复核 → writer 写版本化 signal_cache
        → 渲染策略模板 → freqtrade backtesting 冒烟（7 天）
        → dry-run → 人工确认 → paper
```

---

## 四、验证门禁迁移设计

quant-crypto 的门禁脚本参数化迁移到 `src/alphamill/validation/`：

| 迁移件 | 改造点 |
|---|---|
| 选择期脚本 | 窗口/阈值外置配置；因子筛选、组合成员和权重在此阶段完成并冻结 PortfolioDef |
| 最终 90 天留出 | <30 笔为 `UNDERPOWERED`；30~69 笔最多临时 PASS 并缩减仓位 paper；约 ≥69 笔才形成可信判定 |
| 永久隔离最终确认 | 开发期不可见，每个晋级候选只使用一次；访问写 append-only 留出台账 |
| 独立重放器 | 接口化为 `no_lookahead_audit(factor_def)`，进入因子工厂流水线而非一次性脚本 |
| 成本敏感性 | 三档（taker/maker/零成本）为标准输出列，成本后 Sharpe 为排序主键 |
| KPI 检查 | 继承阈值（Sharpe>1.5 / MDD<20% / WinRate>50% / 月均>20 笔），报告格式沿用 `reports/phase4-kpi-*` |

**多候选处理**：按 ADR-0004 在选择期构建 Top-K（v0.1 K=3、硬上限 5），同时评估组合边际
贡献、相关性、容量和约束；其余进入 monitoring。冻结后的 PortfolioDef 以整体进入留出，禁止
根据留出结果换成员或调权重。

---

## 五、外部依赖管理策略（vendor / fork / 原样依赖）

> 判断原则：**改动深度决定集成距离**。要动大手术的 vendor 进主仓；只用扩展面的原样依赖；fork 仅适用于"要上游全部 + 必须改核心 + 上游不收 PR"的窄缝——本项目三个引入项没有一个落在缝里，**一律不 fork**。

| 引入项 | 方式 | 理由 | 版本策略 |
|---|---|---|---|
| **AlphaGen** | **vendor** 进 `src/alphamill/factor_factory/generators/alphagen_vendor/` | 动大手术（换数据层、numpy/torch 现代化、gymnasium 化）+ 上游核心冻结（无 rebase 负担）+ 只用子集 | 记录 vendor 时的上游 commit hash 于 `VENDORED.md`；不考虑跟随上游 |
| **Freqtrade** | 原样依赖（官方 docker 镜像 + `user_data/` 插件层） | 插件架构零改码即可用（quant-crypto 已验证）；上游月更，fork = rebase 跑步机 | pin 镜像 tag（如 2026.8），里程碑边界升级 |
| **Vibe-Trading** | 可选原样依赖（pip pin + 本机 CLI/服务） | 只读第二实现/Agent 适配；1 周 time-box，可弃置 | 启用时 pin 小版本；仅在里程碑边界升级 |
| Kronos | 独立服务（上游 clone + pin commit，权重 HuggingFace 下载） | 模型代码上游化；服务薄壳为本仓 `src/alphamill/kronos_service/` | pin 上游 commit；见 docs/alphamill-architecture.md §七 |

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
| Vibe-Trading 升级破坏行为 | 冻结适配器并用独立重放器复核；其 run manifest 记录版本；主链路不受影响 |
| 生成器产出垃圾海啸 | 评测台分诊阈值（RankIC + 查重）先行过滤；注册表只收存活者 |
| Freqtrade 策略读取了坏缓存 | 冒烟回测前置 + 审计器校验时间戳对齐；坏缓存直接拒绝挂载 |
| 夜间批处理超时 | 生成器/评测台分任务队列，单代失败不回滚已入库结果 |

---

## 七、Kronos 推理实例：CPU 默认与 GPU 叠加（F010）

`kronos-signal-real` 只有一个实例名（架构 §7.1 生命周期契约的目标），CPU/GPU 由是否叠加
`deployment/docker-compose.gpu.yml` 区分。默认文件对 GPU 一无所知，开发机与 CI 不受影响。

| 项 | 默认（CPU） | 叠加 GPU override（仅执行机） |
|---|---|---|
| 镜像 | compose 生成的 `<project>-kronos-signal-real` | `alphamill/kronos-signal-real:gpu` |
| torch | `2.14.0` + `whl/cpu`（`ARG` 缺省） | `2.14.0` + `whl/cu130`（只覆盖索引） |
| `KRONOS_DEVICE` | `cpu` | `cuda`（显式 → 拿不到 CUDA 即启动失败，不回落 cpu） |
| 设备预留 | 无 | `nvidia × 1` |
| healthcheck | `device == 'cpu'` | `device` 以 `cuda` 开头 |

**前置**（执行机，一次性）：宿主驱动满足 CUDA 13.0 最低要求（R580+）；docker 装有
nvidia-container-toolkit 并 `nvidia-ctk runtime configure --runtime=docker` 后重启 docker——
`docker info` 的 Runtimes 须含 `nvidia`，否则守护进程直接拒绝设备请求（容器不启动，这**不是**
严格分支的失败，见 F010 design §7）。

**构建器**：GPU 镜像的 CUDA 依赖单个 wheel 达数百 MB，默认 buildx builder 的 RUN 步骤走
bridge 网络，在执行机上连续三次读超时（约 155s 处）；改用 host 网络的 builder 一次成功
（实测 20MB/s vs 7MB/s）。因此构建前 `export BUILDX_BUILDER=hostnet`（集成用例会自动选它）。
Dockerfile 侧已固定 `--retries 10 --timeout 120`，并把 NVIDIA 依赖指向国内 PyPI 镜像
（`TORCH_EXTRA_INDEX_URL`）——cu130 索引默认把它们指向 pypi.nvidia.com，该域名在本机不可用。

```bash
# 启用 GPU 实例（执行机）
export BUILDX_BUILDER=hostnet
docker compose -f deployment/docker-compose.yml -f deployment/docker-compose.gpu.yml \
  --profile kronos-real up -d --build kronos-signal-real
docker logs quant-kronos-signal-real | grep '\[kronos-real\] model loaded'   # 实际设备 + torch CUDA 版本

# 切回 CPU 实例：不叠加 override 重新 up（两类镜像标签互不覆盖，无需重建 GPU 镜像）
docker compose -f deployment/docker-compose.yml --profile kronos-real up -d --build kronos-signal-real
```

注意：F004 的 `tests/integration/test_f004_real_profile.py` 断言的是**默认（CPU）配置**
（`KRONOS_DEVICE=cpu`、容器 torch 可导入），在 GPU 实例常驻时跑它会判红——这不是回归；
GPU 配置的集成断言在 `tests/integration/test_f010_gpu_runtime.py`。
