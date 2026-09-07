---
report_type: doc-review
round: 1
date: 2026-09-07
prior_report: 无（循环 4 首轮；循环 1-3 已闭环，见 RETROSPECTIVE.md）
scope: full-scan（F001 三件套 + migration-plan.md 全文；交叉契约：PRD M0/非目标、架构 §五/§七、SOP、features/README；开发环境实况取证）
stop_condition_met: false
severity_counts: {critical: 0, high: 3, medium: 1, low: 2}
baseline: main @ 9a95cee
reviewer: Sisyphus（review-convergence 协议，循环 4：F001 开发前检视）
evidence: 四份 F001 文档逐句通读；PRD M0 行与 spec AC 对齐核对；架构 §五 迁移表逐行比对；环境实测（uname=darwin 无——实为 WSL2 内核 6.18.33.2-microsoft；docker-ce 29.1.3 非 Docker Desktop；which pwsh 无；../quant-crypto 不存在；/mnt/c /mnt/d maxdepth-3 无 quant-crypto；nvidia-smi 不存在）；verify.py 六步全绿（含新密钥门禁）
note: 机器门禁全部通过（结构/链接/AC 引用/BACKLOG 双向一致）——本轮发现全部是语义层与环境层问题，印证 SOP 所述"机器门只证明引用与结构自洽，语义覆盖由人工复核判断"。三条 High 均为"现在改半天文档、开工后改返工"型。
issues_index:
  - {id: D033, severity: high, status: open}
  - {id: D034, severity: high, status: open}
  - {id: D035, severity: high, status: open}
  - {id: D036, severity: medium, status: open}
  - {id: D037, severity: low, status: open}
  - {id: D038, severity: low, status: open}
---

# F001 开发前检视报告（循环 4 · 第 1 轮 · full-scan）

## 1. 总评

**三件套结构合规（Q-001 已关闭、DQ 空、AC 引用合法、BACKLOG 一致、verify 六步全绿），但有 3 条 High 阻塞开工**：① spec 与 migration-plan 在 Parquet 导出是否属 F001 上直接矛盾（按现状验收清单永远无法全绿）；② SC-003 要求 9 项全勾但 tasks 缺 2 项迁移任务（评测/门禁脚本、宇宙发现脚本）；③ 文档全线假设 Windows + PowerShell + Docker Desktop + RTX 4060 执行环境，实际开发环境是 WSL2 + docker-ce、无 pwsh、GPU 不可见、旧仓位置未成文——T002/AC-002/AC-005 在当前环境按字面不可执行。三条都是半天可修的文档活，不修则迁移第一天就撞墙。

## 2. 核对证据

| 检查 | 结果 |
|---|---|
| 结构合规 | spec 9 节齐、design 11 节齐、tasks 6 节齐；Q-001 已关闭（决策成文）；design §10 为"无"；AC-001..005 均引用真实需求 ID；BACKLOG 与 frontmatter 双向一致（validate_spec_lifecycle 全绿） |
| PRD 对齐 | M0 行（2-3 天，verify 全绿=行数对账/Kronos/dry-run/监控）与 spec AC 一一对应 ✓ |
| D033 | migration-plan §五 验收清单含"□ data_bridge：首次全量导出 Parquet 湖成功，manifest 完整"；spec §1 非目标："不实现 Parquet 湖导出与 DuckDB 取数层（属 F002 / M1 数据桥）"——直接矛盾 |
| D034 | spec §3 范围内引用"§一 迁移总览 1-9 项"但 prose 枚举只有 8 项（漏 item 5 评测器/门禁脚本）；tasks.md T001-T018 无 item 5（评测/门禁脚本物理迁移）与 item 8（宇宙发现脚本迁 scripts/）的任何任务；SC-003 要求"9 项全部标记完成" |
| D035 | 环境实测：WSL2 内核（6.18.33.2-microsoft-standard-WSL2）；docker-ce 29.1.3（Ubuntu 构建，非 Docker Desktop）；`which pwsh` 无；`../quant-crypto` 不存在；/mnt/c、/mnt/d maxdepth-3 搜索无 quant-crypto；`nvidia-smi` 不存在。文档假设（CLAUDE.md/spec 依赖/NFR-002/T015/AC-005）：Windows 11 + PowerShell 7 + Docker Desktop + RTX 4060 |
| D036 | AC-001 说"三表行数与校验和对账"；design §3 逐表清单为六表（ohlcv_1m、衍生品三表、quality_flags、signals_log、trades_log）；FR-001 scenario 为三组（ohlcv_1m、衍生品表、质量标记表）——按 AC 验收会漏掉 signals_log/trades_log 两表 |
| D037 | tasks.md Phase 2 内 T010 之后出现 T018，Phase 3 又从 T011 开始——编号与执行顺序交错 |
| D038 | migration-plan item 9 含 kronos_cache 与 feather 行情；.gitignore 忽略 *.feather/*.parquet——"kronos_cache 作为首批信号缓存样本"入库与否未说明 |

## 3. Issue 总表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D033 | migration-plan §五 验收含 data_bridge Parquet 导出，spec 非目标明确排除（属 F002/M1）——F001 验收清单按现状永远无法全绿 | 高 | 正确性 | 根因 | 原始设计 | open | migration-plan §五 删除该验收框（移入 F002 范围引用），或改为"预留 data_bridge 目录位"级别的非验收项 | verify.py 文档门禁 | 1 | — | spec-internal-contradiction |
| D034 | SC-003 要求 §一 9 项全勾，但 tasks.md 无 item 5（评测器/门禁脚本物理迁移，泛化属 M1）与 item 8（宇宙发现脚本）迁移任务；spec 范围内 prose 枚举也漏 item 5 | 高 | 正确性 | 根因 | 原始设计 | open | tasks.md Phase 2 补两条迁移任务（T019/T020：原样物理迁移+import 冒烟，泛化明确留给 M1）；spec 范围内 prose 枚举补 item 5 | validate_spec_lifecycle + verify | 1 | — | spec-tasks-traceability-gap |
| D035 | 环境契约漂移：文档假设 Windows 11 + PowerShell 7 + Docker Desktop + RTX 4060，实际开发环境 WSL2 + docker-ce、无 pwsh、GPU 不可见、旧仓位置未成文——T002/AC-002/AC-005 按字面不可执行 | 高 | 正确性 | 根因 | 原始设计 | open | 三件套+CLAUDE.md 增"执行环境"一节：钉死旧仓实际路径（含跨 OS 挂载点）、迁移执行机（WSL or Windows）、pwsh 安装决策（apt 装 pwsh 或 verify.ps1 出 POSIX 等价物）、GPU 直通方案（AC-002 前置） | verify.py 文档门禁 | 1 | — | environment-contract-drift |
| D036 | 对账表口径三方不一致：AC-001"三表" vs design §3 六表 vs FR-001 scenario 三组——按 AC 验收漏 signals_log/trades_log | 中 | 正确性 | 症状 | 原始设计 | open | AC-001/FR-001/design 统一为同一份逐表清单（含 signals_log/trades_log 与连续聚合），一处定义两处引用 | verify.py 文档门禁 | 1 | — | spec-internal-contradiction |
| D037 | tasks.md T018 编号乱序（Phase 2 内 T010 与 Phase 3 T011 之间出现 T018） | 低 | 质量 | 症状 | 原始设计 | open | T018 重编号为 T011，后续顺延（或移入 Phase 3 之前独立小节） | validate_spec_lifecycle | 1 | — | — |
| D038 | item 9 user_data 的 git 边界未说明：kronos_cache/feather 受 .gitignore 覆盖，"首批信号缓存样本"入库与否无定论 | 低 | 质量 | 症状 | 原始设计 | open | migration-plan item 9 改造点注明"feather/缓存为本地数据资产不进 git，入库仅策略与 config；缓存样本供 F002 校验用" | — | 1 | — | — |

## 4. 裁决记录

（首轮无修复方声明，无裁决。）

## 5. 停止条件状态

**未满足**：High 3 条 open（D033/D034/D035 均为阻塞开工级）。修复轮完成后进入第 2 轮 diff-only 复核。本地门禁基线全绿（main @ 9a95cee，含新密钥扫描门禁）。
