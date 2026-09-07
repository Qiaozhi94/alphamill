# AlphaMill — quant-crypto 清算迁移方案

> 版本：v0.1 | 日期：2026-09-07 | 决策：quant-crypto 仓库**归档废弃**，资产一次性清算迁入本仓
> 红线：代码可以弃，**数据必须迁**（631 万行 OHLCV + 衍生品特征 + 质量标记 = 数周采集成本，不可重购）

---

## 一、迁移总览

| # | 资产 | 来源（quant-crypto） | 去处（AlphaMill） | 改造点 |
|---|---|---|---|---|
| 1 | **TimescaleDB 数据卷** | qiaozhi-lt（Tailscale `100.98.228.125`）`D:\Projects\quant-crypto` 的 Docker 卷 `quant-crypto_timescale_data`（实测 ohlcv_1m 6,504,359 行、11 表、5 连续聚合；凭据在同目录 `.env`） | 随 docker-compose 迁入，数据不重建 | SSH 流式 pg_dump/restore（路径实证见 tasks T004，无需开 5432 防火墙），行数对账 |
| 2 | 数据采集器 | `data-collector/`（ccxt_ingestor、db_writer、historical_backfill、symbol_manager、derivatives_market_backfill） | `src/alphamill/data_bridge/collector/` | 并入主仓依赖管理；保留 REST 轮询模式 |
| 3 | Kronos 服务薄壳 | `kronos-signal/`（server/generator/db_adapter/kronos_real） | `src/alphamill/kronos_service/` | db_adapter 改读迁移后 DB；上游 Kronos 代码改为 clone+pin（见第三节） |
| 4 | 风控三件套 | `risk/`（circuit_breaker、correlation_guard、drawdown_guard） | `src/alphamill/freqtrade_bridge/risk/` | 随策略模板挂载进 Freqtrade |
| 5 | 评测器/门禁脚本 | `scripts/kronos_rankic_eval.py`、`kronos_ic_decay_eval.py`、`independent_cross_backtest.py`、`validate_*_holdout.py` | `src/alphamill/factor_factory/bench/` + `src/alphamill/validation/` | 泛化改造（M1 主体工作，见 PRD） |
| 6 | 监控配置 | `grafana/`、`prometheus/` | `monitoring/` | 数据源指向迁移后 DB |
| 7 | 部署编排 | `docker-compose.yml`、`.env` 模板、`scripts/verify.ps1` | `deployment/` | 端口/网络按主仓调整；verify 扩展为全链路 |
| 8 | 宇宙发现 | `scripts/discover_okx_swap_universe.py`、`download_okx_swap_1h.ps1` | `scripts/` | 无改造 |
| 9 | Freqtrade user_data | `freqtrade/user_data/`（策略、config、kronos_cache、feather 行情） | `freqtrade/user_data/` | 入库仅策略与 config；kronos_cache / feather 行情为本地数据资产不进 git（主仓 .gitignore 已覆盖 *.feather/*.parquet）；缓存样本留存本地，作为首批信号缓存样本供 F002 信号缓存对齐校验用 |

## 二、留下不搬（归档处置）

- 一次性实验脚本：`scripts/` 中的网格搜索/敏感性/诊断脚本（数十个）——方法论已被 PRD 的评测台+门禁吸收
- 历史 `reports/`： dated 报告与回测 zip——旧仓只读留存，不迁
- 过期策略实验版本（KronosFusionStrategy 历史迭代、LowFrequencyBaselineStrategy 实验版）——保留最终版参考即可
- `.sisyphus/`、`.code-review-graph/` 等工具目录

**旧仓处置**：迁移验收通过后，quant-crypto 本地目录打 tag 归档（`archive/2026-09-migration`），不再更新。

## 三、Kronos 上游化三步

```text
① 模型代码：fresh clone shiyu-coder/Kronos → 第三方目录（如 vendor/Kronos），pin commit，零改动
            （待遇与 Freqtrade 相同：各自上游仓，我们不维护 fork）
② 模型权重：HuggingFace 下载 NeoQuasar/Kronos-base + Kronos-Tokenizer-base → models/（不进 git）
③ 服务薄壳：quant-crypto 的 kronos-signal/ FastAPI 包装迁入本仓 src/alphamill/kronos_service/
            ——这层本来就是自研胶水，负责：DB 读数 → Kronos 推理 → 信号输出/缓存
```

> 边界说明：Kronos 上游只提供模型本体（预测器/分词器）；"常驻 GPU 推理服务 + HTTP API"一直是我们的薄壳。上游化 = 模型代码回到上游仓，薄壳进主仓。

## 四、TimescaleDB 去留（分阶段，可逆）

- **阶段 A（迁移期，推荐）**：TimescaleDB 随 docker-compose 迁入照常运行——采集、聚合、质量监控全链路零风险接续；data_bridge（F002 起）照原设计导出 Parquet 湖
- **阶段 B（可选，跑稳后）**：若想精简运维，采集器改为直写 Parquet + DuckDB 查询层，撤掉 TimescaleDB——需重写聚合与质量监控查询，届时单独立项评估

## 五、迁移验收（全绿才算完成）

```text
□ 行数对账：迁移后 DB 与旧仓行数/校验和一致（quality_flags 未解决数一致）
□ Kronos：/health 200；/predict/BTC-USDT 返回 source=kronos
□ Freqtrade：dry-run 启动，读到 Kronos 信号缓存，风控三件套挂载
□ 监控：Grafana 面板有数据（K 线延迟/信号质量/交易健康）
□ verify.ps1 全绿（扩展为上述全链路检查）
□ 旧仓打 tag 归档，主仓 git 历史干净（迁移 commit 单独可审）
```

> 范围澄清（D033）：Parquet 湖首次全量导出与 manifest 产出属 F002 / M1 数据桥范围（见
> `spec.md` §1 非目标），不列入本迁移验收——本迁移只保证 TimescaleDB 数据完整可查、
> 全链路可运行；`lake/` 目录位仅随 §七 备份方案预留。

## 六、执行顺序建议（与里程碑对齐）

1. **M0（新增，~2-3 天）**：数据卷迁移 + 采集器/薄壳/风控/监控代码搬迁 + verify 全绿
2. M1 起：所有开发只在 AlphaMill 主仓进行；旧仓只读
3. Kronos 上游化（clone+pin+权重下载）放在 M0 内完成，避免迁移期间推理断供

## 七、备份与灾备（单盘故障 ≠ 项目清零）

- 每日定时向局域网 UGREEN NAS 同步三类资产：TimescaleDB 逻辑 dump（`deployment/backups/db/<date>.dump`）、Parquet 湖分区（`lake/`，F002 起生效）+ manifest（`lake/_manifests/`）、对账与报告（`reports/`）；
- 同步脚本随 `deployment/` 迁入；NAS 不可达时本地保留 7 天滚动副本，恢复后自动补同步；
- 恢复演练：M0 验收时从 NAS 副本完整恢复一次 DB 到临时容器并通过行数对账，此后每季度抽验一次。
