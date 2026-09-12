---
topics: [sop, workflow]
doc_kind: note
created: 2026-09-06
updated: 2026-09-07
---

# 开发流程（AlphaMill）

本文是项目的**原则入口与质量门**唯一真源：汇总「项目不可违反原则」的短摘要与各自
唯一拥有者链接，规定开发纪律、验证流程、状态转换与复核协议。

## 0. 项目不可违反原则（入口）

以下原则是**阻断性**的：违反其中任何一条的规格/实现不得进入实现或收口阶段。规范
正文在各自的唯一拥有者中，本文只给摘要与入口。**每条原则的规范正文只放一个唯一
拥有者**，本文只写短摘要与链接，不重复 PRD、architecture、decisions 的完整定义。

| # | 原则 | 短摘要 | 规范正文唯一拥有者 |
|---|---|---|---|
| 1 | 可追溯规格优先 | 功能必须先有已评审规格；实现/测试/实验/结论必须引用需求编号；未写入规格的行为不视为承诺 | 本文 + `docs/features/README.md` |
| 2 | 证据门不降级 | 候选按样本功效分级并经过留出与最终确认；效率提升不得来自放宽门禁 | `docs/decisions/0003-validation-gate-non-degradation.md` |
| 3 | 无前视一等公民 | 因子定义过 AST 纯度门 + 独立逐 K 线重放审计 + 信号缓存时间戳对齐检查（三层防线） | `docs/alphamill-integration.md` |
| 4 | 数据红线（只读湖快照） | 研究/回测只读 Parquet 湖不可变快照（data_version），不直读 TimescaleDB 修订态 | `docs/alphamill-architecture.md` |
| 5 | AI 权限边界 | Agent 只产候选和建议，不裁决门禁、不改变生产状态、不触发真实下单 | `docs/alphamill-prd.md` |
| 6 | 实盘红线（最终确认前置） | 无候选通过最终确认并满足可信样本量前，不触碰实盘下单路径 | `docs/alphamill-prd.md` |
| 7 | 实验可复现 | 每个实验写 manifest 并串联数据、因子、组合、信号和成交，任一历史结果可重建 | `docs/alphamill-architecture.md`（manifest 契约） |

> 新建项目时：从 PRD/架构中提炼 3-7 条真正不可违反的原则填表，其余原则不要堆砌；
> 每加一条必须同时指定唯一拥有者文档。

## 1. 开发纪律

- **提交前本地全绿**：`python3 tools/verify.py`（唯一公开入口）运行门禁与测试，失败即返回非零。
- **推送后确认 CI**：`git push` 后用 `gh run watch <run-id> --exit-status` 确认当前
  HEAD 的全部必需 CI job 全绿，推完不算结束。
- **每次修复补回归测试**：同一提交内为修复的行为补正反两面的仓库内测试；已知但暂不
  修复的缺口显式标记（python 用 `pytest.mark.xfail(strict=True)`）并写明原因。
- **安全校验降级必须声明**：若「失败即拒绝」改为「仅警告/仅记录」，必须在提交信息或
  代码注释中显式说明原因。
- **开发工具锁定版本上界**：dev 依赖写范围（如 `ruff>=0.16,<0.17`），工具升级必须是
  一次显式、本地验证过的改动。

## 2. 状态门

- **状态唯一真源**是各 Feature `spec.md` 的 frontmatter `status`；`design.md`、
  `tasks.md`、README、CLAUDE 不得声明第二份独立状态。
- 状态机：`draft → ready-for-development → in-progress → review → done`。
- 进入 `ready-for-development` 前：spec/design 待确认问题（`Q-xxx` / `DQ-xxx`）全部
  关闭；tasks 可追踪到合法引用。
- `done` 时：tasks、AC 与退出条件非空且全部完成，每条 AC 引用存在的仓库内测试路径。

## 3. 验证与复核流程

- 唯一公开验证入口：`python3 tools/verify.py`，按固定顺序运行门禁与测试，失败即非零。
  注意区分同名不同物的两个入口：`python3 tools/verify.py` 是代码质量门禁（唯一公开
  验证入口）；`deployment/verify.ps1` 是规划中的全链路验收脚本（目录尚未创建，随
  F001 迁移落地），二者不是同一件事。
- 复核（review）检查：规格完整性、测试证据、复现信息、研究边界；机器门只证明引用与
  结构自洽，语义覆盖由人工复核判断。
- **检视文档生命周期**：`docs/reviews/CURRENT-doc.md` / `CURRENT-code.md` /
  `FIX-log.md` 是本地过程稿，不进入 git（见 `.gitignore`）；只能由检视人复核完成后
  删除，执行修复的一方不得自行删除（配合 review-convergence skill）。
- **真实环境测试纪律**：本机就是真实环境；需要真实进程/文件系统/端到端的测试一律直接
  在本机执行，不允许默认标记成「待用户在真实环境验证」而跳过。唯一允许延后的情形是
  客观不可执行（缺凭证、缺二进制、需外部账号），此时必须在自检结论里显式列出原因与
  补齐方式。Feature 收口前，集成验收必须运行
  `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration -q`；服务不可达或
  mock 模式在该开关下必须判红，不能以 skip 代替证据。

## Workflow

进入 Step 1 前的强制前提：对应 feature 的 `design.md` 的「待确认设计问题」章节必须
已清空。带着未解决的设计问题开工，等于把设计判断推迟到实现中间做。

| Step | What |
|------|------|
| 1 | 建分支/worktree 做隔离开发 |
| 2 | 严格按 `tasks.md` 里的顺序逐项实现，每完成一项立即勾掉；`[P]` 任务可并行；顺序过时先改 `tasks.md` 再继续 |
| 3 | 自检：对照 spec / acceptance criteria 过一遍，跑 `python3 tools/verify.py` |
| 4 | （可选）让 AI agent 扮演 reviewer 角色审一遍 diff，输出 findings |
| 5 | 合并 + 清理分支 |

## Code Quality

- File limits: 200 行建议拆分 / 350 行硬上限。
- 分层与命名约定：node 见 `docs/decisions/` 目录结构 ADR；python 采用单一布局
  `src/alphamill/<module>/`（子包：data_bridge、factor_factory、validation、
  kronos_service 等）；非 Python 资产（docker-compose、deployment/、docs/）留仓库根。

### F001 原样迁移文件豁免

以下文件是 F001 从旧仓原样迁入、且尚未进入 F002 泛化范围的历史脚本，暂不按 350 行
硬上限拆分。豁免截止 `F002` 完成对应模块泛化时，由 owner 复核并删除或续期；豁免不
放宽运行时验证和质量门。

| 文件 | 豁免原因 | 解除期限 |
|---|---|---|
| `src/alphamill/data_bridge/collector/derivatives_market_backfill.py` | F001 原样迁移的回填脚本 | F002 泛化阶段 |
| `src/alphamill/data_bridge/collector/historical_backfill.py` | F001 原样迁移的回填脚本 | F002 泛化阶段 |
| `freqtrade/user_data/strategies/KronosFusionStrategy.py` | F001 原样迁移的策略模板 | F002 策略整合阶段 |
| `src/alphamill/validation/validate_low_frequency_expanded_holdout.py` | F001 原样迁移的评测脚本 | F002 评测台阶段 |
| `src/alphamill/factor_factory/bench/train_low_frequency_walk_forward_baselines.py` | F001 原样迁移的评测脚本 | F002 评测台阶段 |
| `src/alphamill/validation/validate_low_frequency_regime_filters.py` | F001 原样迁移的评测脚本 | F002 评测台阶段 |
| `deployment/verify.ps1` | F001 全链路验收脚本 | F002 验收门重构阶段 |
| `src/alphamill/validation/validate_low_frequency_candidate_holdout.py` | F001 原样迁移的评测脚本 | F002 评测台阶段 |
| `src/alphamill/factor_factory/bench/independent_cross_backtest.py` | F001 原样迁移的评测脚本 | F002 评测台阶段 |
