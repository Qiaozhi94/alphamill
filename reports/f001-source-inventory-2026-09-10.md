# F001 旧仓只读基线清单

> 日期：2026-09-10 | 执行：T001（`NFR-001`）| 依据：spec §0 路线修订、RETROSPECTIVE #16

## 代码基线

- 路径：`D:\Projects\quant-crypto`（WSL2 内 `/mnt/d/Projects/quant-crypto`，9p 挂载只读使用）
- git HEAD：`d94f94f1b48a2bd8f5b630e8a87d9358f6e60059`（2026-09-06 实测 `git rev-parse`）
- HEAD 提交：`docs: 归档回测研究报告（md/json/svg）`
- 处置：只读参照，不修改、不删除；数据重建完成并通过完整性校验（AC-001）前不得归档。

## 运行现场（已灭失）

- 原 Docker 命名卷 `quant-crypto_timescale_data`：驻旧 C 盘 Docker Desktop 数据盘，2026-09-07~08 宿主机重装时随格式化丢失。
- 灭失前实测（2026-09-07 记录）：ohlcv_1m 6,504,359 行、11 张公有表、5 个连续聚合。
- 取证结论：无任何备份副本（六路全否），详见 migration-plan.md §八。

## 幸存资产盘点

| 资产 | 路径（旧仓内） | 状态 |
|---|---|---|
| 全套代码（git 仓） | `/mnt/d/Projects/quant-crypto` | ✅ 完整，HEAD `d94f94f` |
| DB schema | `db/init.sql`（10.5KB）、`db/migrations/` | ✅ 已迁入主仓 `db/` |
| 环境凭据 | `.env`（980B） | ✅ 在（数据库/采集配置以此参照，密钥不进 git） |
| Freqtrade user_data | `freqtrade/user_data/`（88MB） | ✅ 在：7 个 config JSON、`signals/*.feather` 3 件、`kronos_cache/` 样本（含 `kronos_signals_5m_20260501.feather`）、`data/okx/futures/leverage_tiers_USDT.json`（12MB） |
| 历史回测报告 | `reports/`（SVG/MD/JSON） | ✅ 在（只读留存，不迁） |
| Kronos 权重 | `models/` | ❌ 不存在（T007 走 HF 下载主路径，无复制回退） |
| TimescaleDB 数据卷 | Docker Desktop 数据盘（旧 C 盘） | ❌ 灭失（T005 交易所重建） |

## 结论

- 代码与配置基线以本清单为准；数据基线由 T005 回填报告（`reports/f001-backfill-<date>.json`）承载。
- 本清单不含任何密钥内容；`.env` 仅确认存在性与大小。
