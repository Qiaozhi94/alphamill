---
topics: [docs, index, ownership]
doc_kind: guide
created: 2026-09-06
updated: 2026-09-15
---

# AlphaMill 文档地图

本文件是仓库文档的**唯一入口与所有权索引**：从一个入口最多两次点击即可到达任何
权威文档。它只记录所有权和链接，**不复制正文**。产品、架构、数据模型、Feature 状态
和流程各有且只有一个机器可读拥有者。

## 权威文档所有权矩阵

| 信息 | 唯一拥有者 | 说明 |
|---|---|---|
| 产品目标、范围和路线 | `alphamill-prd.md` | 产品真相源（指标体系 / G1-G7 / FR1-FR8 / 里程碑 M0-M4） |
| 全局模块、进程与运行时边界 | `alphamill-architecture.md` | AI 控制面 + 证据与治理面 + 策略与执行面 + 数据面 + 闭环主循环 |
| 字段、表、数据契约（HypothesisDef / FactorDef / PortfolioDef / 评测台 / 信号缓存 / manifest） | `alphamill-architecture.md` §四 | 接口契约真源 |
| 因子挖掘主引擎选型（含降级阶梯） | `decisions/0001-factor-mining-engine.md` | 选型决策（证据：`alphamill-research-factor-mining.md`） |
| 外部依赖管理策略（vendor/fork/原样） | `decisions/0002-external-dependency-policy.md` | 依赖策略（操作细节：`alphamill-integration.md`） |
| 验证门禁不降级 | `decisions/0003-validation-gate-non-degradation.md` | quant-crypto 教训制度化 |
| 组合构建（因子→策略映射） | `decisions/0004-portfolio-construction.md` | 协同池组合的部署路径与权重/换手/敞口规则 |
| 呈现与观测架构（真相源/投影/展示三分、自建前端路线） | `decisions/0005-presentation-observability.md` | Grafana/FreqUI/自建控制台边界、口径进视图、统一只读 API |
| 证据边界与实验身份 | `decisions/0006-evidence-boundary-and-experiment-identity.md` | 四平面之上的横向 seam、preview/canonical、内容寻址与失败关闭 |
| 研究快照与多数据集版本绑定 | `decisions/0007-research-snapshot-binding.md` | dataset 独立版本 + ResearchSnapshot 引用集合；canonical 禁止动态 latest |
| 北极星与指标口径（在跑组合持续盈利；产能=分母与能力标定） | `decisions/0008-north-star-sustained-profitability.md` | 结果/护栏/分母三层职责划界；PRD §2.3 指标体系的口径依据 |
| 呈现层视觉原型（非契约，设计资产） | `design/ui-mockup/`（设计稿，本地） | 终局四面全景蓝图，**非权威、非 F005 范围**；F005 spec 落地后废弃或迁入 `web/`（ADR-0005 决策 7） |
| quant-crypto 资产清算迁移 | `features/0.1/F001-quant-crypto-migration/migration-plan.md` | 迁移清单与验收（F001 附属） |
| 跨 Feature 长期决策 | `decisions/` | ADR 决策记录 |
| Feature 行为与状态 | `features/<version>/Fxxx-*/spec.md` | 状态唯一真相源 |
| Feature 实现方案 | `features/<version>/Fxxx-*/design.md` | 技术设计 |
| 开发、验收和检视纪律 | `SOP.md` | 开发流程约定 |
| 当前 active Feature 与强提醒 | `../CLAUDE.md` | 自动加载入口 |
| 非 done Feature 派生索引 | `../BACKLOG.md` | 活跃 feature 索引（当前 F003/F008/F009/F010） |
| 版本收口摘要 | `features/releases/0.1.md` | 0.1 收口于 2026-09-12 |
| 缺陷和过程教训 | `reviews/RETROSPECTIVE.md` | 检视复盘 |

## 权威文档导航

- **PRD（产品判断）**：→ [`alphamill-prd.md`](alphamill-prd.md)
- **架构（含契约）**：→ [`alphamill-architecture.md`](alphamill-architecture.md)
- **选型调研证据**：→ [`alphamill-research-factor-mining.md`](alphamill-research-factor-mining.md)
- **集成操作细节**：→ [`alphamill-integration.md`](alphamill-integration.md)
- **ADR（决策记录）**：→ [`decisions/`](decisions/)
- **开发流程 SOP**：→ [`SOP.md`](SOP.md)
- **Feature 规格指南与状态门禁规则**：→ [`features/README.md`](features/README.md)
- **检视复盘**：→ [`reviews/RETROSPECTIVE.md`](reviews/RETROSPECTIVE.md)

## 所有权规则（机器可校验）

- `status` 只能出现在 Feature `spec.md` frontmatter；`design.md` / `tasks.md`
  不得声明独立 Status。
- `BACKLOG.md` 与所有非 done Feature 做双向集合比较（ID/version/status/链接一致）。
- 本 README 中的权威入口必须存在且唯一。
- `releases/` 与 `RETROSPECTIVE.md` 仅作历史记录与复盘，不得充当当前产品、状态或
  实现的权威入口。

以上规则由 `python3 tools/verify.py`（含 `validate_spec_lifecycle.py`）强制执行。
