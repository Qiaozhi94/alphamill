---
report_type: doc-review
round: 2
date: 2026-09-07
prior_report: 本文件 Round 1（同文件覆盖写，Round 1 全量内容已含于本轮 issue 表的"标题/修复建议"列与 FIX-log）
scope: diff-only（修复 diff 覆盖 docs 全域 + 新增 2 份 ADR/1 份新 ADR，检视人升级说明：本轮按协议只审 diff 及相邻契约，未重读未改动文档全文）
stop_condition_met: true
severity_counts: {critical: 0, high: 0, medium: 0, low: 0}
baseline: main @ 7969a97（终基线；round-1 基线 1bd8c4d，修复轮 7 个分批提交后由检视人 re-baseline）
reviewer: Sisyphus（review-convergence 协议，Round 2 显式切换检视人视角）
evidence: 逐 issue 对照 git diff + 6 个新文件全文 + 实测（pytest tests/unit 25 passed；python tools/verify.py 六步全绿 ×2 轮）+ Round 2 独立复审 agent 的 7 项专项检查（a-g 全过）
note: 检视人终核完成（2026-09-07）：基线已 re-baseline 至 7969a97；RETROSPECTIVE 已回写；本仓无 git remote，CI 最终门禁客观不可执行（协议允许例外），配置 remote 后首推即补验
issues_index:
  - {id: D001-D024, status: 全部 fixed（D001-D024 修复轮次=1）}
  - {id: N1, severity: low, title: PRD FR2.2 与架构 §4.2 成本裁决档位矛盾（dead vs weak）, status: fixed（修复轮次=2，当场修复）}
---

# AlphaMill 文档检视报告（第 2 轮 · diff-only 复核）

## 1. 总评

**round-2 PASS：Round 1 的 24 条 issue 全部核实修复（fixed），7 项专项回归检查全过，无阻塞性 fix-regression。** 复审中新发现 1 条 low（N1，修复引入的措辞矛盾），已当场修复并复跑门禁全绿。修复动作自伤率落在协议预期内（1 条/28 条），且被 diff-only 复审捕获——单轮闭环会漏掉它。

## 2. Round 2 检视范围与方法

- **范围**：git diff（17 个修改文件）+ 6 个新文件（ADR-0004、check_dep_pins.py、check_doc_links.py、3 个测试文件）+ 相邻契约交叉点；不重读未改动文档全文。
- **方法**：独立复审 agent 逐 issue 对照 diff 给出 verdict 表；检视人复核 7 项专项检查（ADR-0003 冻结本体 diff 零触碰 / D010 四处口径一致 / D002 PRD↔架构一致 / ADR-0004 四处引用同义 / CI↔verify.py 收敛 / 日期戳齐 / validator 字节级还原）；实跑 pytest（25 passed）与 verify.py 全链路（两轮全绿）。
- **基线**：main @ 1bd8c4d，无外来改动归属争议（工作树改动全部可追溯到本轮 6 路修复声明）。

## 3. 专项检查结果（fix-regression 猎捕）

| # | 检查项 | 结果 |
|---|---|---|
| a | ADR-0003 冻结判据本体只增不改 | ✅ diff 仅新增（修订行+三节补强），决策节 1-5 无任何 hunk；D006 补强显式声明"≥30 硬下限不变、只收紧" |
| b | D010 目录约定四处一致 | ✅ 架构 §三 / SOP Code Quality / F001 design·tasks·migration-plan / integration 全部 `src/alphamill/<module>/` + 非 Python 资产留根；架构兜底条款覆盖未改动文档的平铺写法残留 |
| c | D002 PRD↔架构契约一致 | ⚠️→✅ 核心规则一致（硬过滤、资金费率入模），发现 N1 档位措辞矛盾，已修复对齐（dead） |
| d | ADR-0004 引用同义性 | ✅ PRD S5/FR5.3、docs/README 矩阵、CLAUDE.md 与 ADR 决策 1/2/3/5 完全同义（Top-K、meta-因子、逆波动率、每 pair 单策略） |
| e | CI 与 verify.py 收敛 | ✅ ci.yml 单 verify job 调 `python tools/verify.py`，permissions/concurrency/matrix(3.11+3.13) 保留 |
| f | 日期戳 | ✅ 有 frontmatter 的 6 个文件 `updated: 2026-09-07`；头部行式文档（PRD/架构/集成/migration-plan）同步 2026-09-07 |
| g | validate_spec_lifecycle.py 还原完整性 | ✅ `git diff` 为空，字节级等同 HEAD；变异验证声明与物证一致 |

## 4. Issue 总表（Round 1 全量 24 条 + Round 2 新增 1 条）

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D001 | 组合构建层缺失：协同池产物无部署路径，Top1-only 政策丢弃组合价值，多因子并存方案未设计 | 严重 | 正确性 | 根因 | 原始设计 | fixed | 立 ADR-0004 | 新建 ADR-0004：协同池组合=可部署 meta-因子同门禁无捷径；Top-K（K=3，上限 5）取代 Top1-only；逆波动率权重；换手预算 ≤100%/周期作成本门禁输入；每 pair 单策略+组合层净额化 | — | 1 | 1 | — |
| D002 | 成本墙不在选择回路：RL 奖励=RankIC、评测台 verdict 按 IC、成本三档在验证期才介入；资金费率全文档零出现 | 严重 | 正确性 | 根因 | 原始设计 | fixed | 评测台 taker 档硬过滤；成本模型加资金费率；挖掘奖励引入成本惩罚 | PRD FR2.1 奖励成本罚项/预筛 + FR2.2 成本硬过滤 + 新增 FR2.5 资金费率成本模型；架构 §4.2 cost 块 + cost_verdict 规则（N1 修复后与 PRD 对齐：cost_negative→dead） | — | 1 | 1 | objective-mismatch-throughput |
| D003 | FactorDef（单 pair pandas callable）↔ AlphaGen（表达式树+张量栈）适配契约未定义 | 高 | 正确性 | 根因 | 原始设计 | fixed | 架构 §4.1 扩展契约 | 架构新增 §4.1.1：表达式树↔callable、张量面板↔DataFrame（v0.1 单 pair 路径）、feature_map 显式映射；跨 pair 真截面算子显式裁剪（scope=cross_sectional_deferred） | — | 1 | 1 | — |
| D004 | 多重检验"试验"计数口径未定义；有效独立假设 ≈5-10/周 | 高 | 正确性 | 根因 | 原始设计 | fixed | FR2.4 明确计数口径 | FR2.4：每条进入评测台的表达式（含被拒者）计 1 次试验；deflated significance 分母=全量试验数；禁止用存活者计数替代 | — | 1 | 1 | — |
| D005 | 留出期复用统计退化无预算/台账 | 高 | 正确性 | 根因 | 原始设计 | fixed | 留出预算+台账+最终确认窗补进 ADR-0003 | ADR-0003 增补：周度访问预算（k=5 配置项）+ append-only 使用台账 + 永久隔离最终确认窗（晋升 paper 前一次性使用） | — | 1 | 1 | — |
| D006 | "≥30 笔"门槛与"69 笔不可信"诊断自相矛盾 | 高 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003 补功效论证 | ADR-0003 增补：≥30=绝对硬下限（评估资格）；30-69=UNDERPOWERED 带（仅临时 PASS+缩减仓位+延长观察）；可信判定需 ≈69+ 笔（α=0.05/80% 功效）；只收紧不放松 | — | 1 | 1 | spec-internal-contradiction |
| D007 | 宇宙扩容回填（约 4600 万行）无估算无归属 | 高 | 正确性 | 症状 | 原始设计 | fixed | 回填独立成显式工作流写入 M1 | PRD FR1.3 显式工作流（1-2 周 wall-clock、归属项目所有者、与开发并行）；M1 表述改"开发 1 周+回填并行 1~2 周" | — | 1 | 1 | hidden-workstream-no-owner |
| D008 | 复盘循环是数据窥探放大器，无防护设计 | 高 | 正确性 | 根因 | 原始设计 | fixed | generation 标签+试验台账+隔离窗 | ADR-0003 增补：复盘假设带 generation 标签入试验台账、计入 FR2.4 多重检验预算、最终确认窗对复盘循环不可见 | — | 1 | 1 | — |
| D009 | SOP"不可违反原则表"2/3 行是空占位符 | 高 | 流程缺陷 | 症状 | 原始设计 | fixed | 从 PRD/ADR-0003/CLAUDE.md 提炼真原则填表 | SOP §0 填实 6 行（可追溯规格/留出不降级/无前视/数据红线/实盘红线/可复现），每条单一 owner 文档 | — | 1 | 1 | unfilled-template-placeholder |
| D010 | 目录约定三方矛盾（平铺 vs src/<pkg> vs pyproject 打包） | 高 | 契约漂移 | 根因 | 原始设计 | fixed | M0 开工前拍板单一目录规范 | 拍板 `src/alphamill/<module>/`（src-layout 由 pyproject 固化）+ 非 Python 资产留根；传播至架构 §三（含兜底条款）/SOP/CLAUDE/F001 tasks T005·T007·T008/design/migration-plan §一·§三/integration ×8 | — | 1 | 1 | — |
| D011 | 13 处死链（docs/05、docs/02、doc 03 旧编号残留于 6 文件） | 中 | 契约漂移 | 症状 | 原始设计 | fixed | 全局替换；verify 加链接存在性检查防复发 | 6 文件死链全部改现名（→migration-plan.md §一/§二/§四、ADR-0001、alphamill-architecture.md）；并落地 verify 第 2 步 check_doc_links.py | tests/unit/test_check_doc_links.py::6 tests（变异验证：注入死链→exit 1 精确报 file:line→还原） | 1 | 1 | renamed-doc-stale-refs |
| D012 | M2 迁移切片乐观，L1/L2 切换标准未预定义 | 中 | 质量 | 症状 | 原始设计 | fixed | 切换判据写成可勾选清单并入 ADR-0001 | ADR-0001 增补二元判据：→L1 三条（冒烟第 2 日未通 PPO epoch / 第 1 日 sb3+gymnasium 最小循环未通 / 第 2 日无首个可对齐因子）；→L2 两条（连续 2 周候选 <50/周或零过审）；禁止自我豁免 | — | 1 | 1 | — |
| D013 | Vibe-Trading 接入契约未前置到 M1 | 中 | 质量 | 症状 | 原始设计 | fixed | M1 出口标准加映射表初版 | integration §2.2「M1 出口标准」：symbol_map.csv 初版表骨架（pair↔Vibe symbol↔Freqtrade pair+UTC 约定）+三条契约；F001 design §4 前置引用 | — | 1 | 1 | — |
| D014 | 数据修订/point-in-time 政策缺失 | 中 | 正确性 | 根因 | 原始设计 | fixed | manifest 增修订差异记录+版本失效策略 | integration §1.2：修订→data_version 必须递增+旧快照不可变；manifest 登记修订分区差异；在途实验打 data_version_drift 标记，gate 判定前建议重跑 | — | 1 | 1 | — |
| D015 | 成本参数校准来源未指定 | 中 | 正确性 | 症状 | 原始设计 | fixed | FR3.4 加实测校准条款 | FR3.4：成本参数以 quant-crypto dry-run 实际成交记录校准，不得采用交易所牌价 | — | 1 | 1 | — |
| D016 | 单卡 GPU 争用无调度策略 | 中 | 质量 | 根因 | 原始设计 | fixed | 部署拓扑补 GPU 时段表或队列 | 架构 §7.1 时段表（白天 Kronos ≤3GB / 工作日夜 AlphaGen ≤6GB 独占 / 周末 Vibe MC ≤2GB 共存）+碰撞走单槽 FIFO 队列，禁止 OOM 赌博 | — | 1 | 1 | — |
| D017 | 备份/DR 缺失，单盘故障=项目清零 | 中 | 质量 | 根因 | 原始设计 | fixed | F001 或 M1 加每日 NAS 同步 | migration-plan 新增 §七（每日 NAS 同步 DB dump+湖+manifests+reports、本地 7 天滚动副本、M0 恢复演练+季度抽验）；tasks 增 T018（依赖 T010） | — | 1 | 1 | — |
| D018 | RL 挖掘可复现细节（种子/确定性开关）未进 manifest 规范 | 中 | 正确性 | 症状 | 原始设计 | fixed | FR6.1 manifest 增 seed 与确定性开关 | FR6.1：挖掘类 manifest 必录随机种子+torch/cudnn 确定性开关 | — | 1 | 1 | — |
| D019 | merge_asof 三处细节未定义 | 中 | 正确性 | 症状 | 原始设计 | fixed | 信号缓存契约增补三规则 | 架构 §4.3：缓存键带 (data_version, code_version, params_hash) 版本维度；混合频率陈旧界 N=1 因子周期+越界写 NaN=no-signal；审计显式覆盖 join 步骤 | — | 1 | 1 | — |
| D020 | 部署时滞与因子衰减错配，缺 champion-challenger 再验证 | 中 | 质量 | 根因 | 原始设计 | fixed | 生命周期增部署前再验证 | 架构 §2.2 新增「部署前再验证」节点：champion 上线前最近 30 天窗口重过评测台粗筛；challenger 轮换触发同规则 | — | 1 | 1 | — |
| D021 | docs/README.md 导航行重复 | 低 | 质量 | 症状 | 原始设计 | fixed | 删重复行 | 已删除 | — | 1 | 1 | — |
| D022 | features/README.md 截断孤句 | 低 | 质量 | 症状 | 原始设计 | fixed | 补全原句 | 补全为"design 与架构边界的关系，稳定后应回写到这里。" | — | 1 | 1 | — |
| D023 | verify 双入口命名混淆 | 低 | 质量 | 症状 | 原始设计 | fixed | 一句话显式分工 | SOP §3：tools/verify.py=代码质量门禁唯一公开入口；deployment/verify.ps1=规划中的全链路验收（随 F001 落地） | — | 1 | 1 | — |
| D024 | committed 文档含机器特定绝对路径 | 低 | 质量 | 症状 | 原始设计 | fixed | 改为相对/仓内引用 | PRD 头部/资产表 + 根 README（背景+相关项目）全部改为相对/描述性引用；ADR-0003:6 背景行残留属范围外观察项 | — | 1 | 1 | — |
| N1 | PRD FR2.2"成本后为负→dead"与架构 §4.2"自动降级 weak"措辞矛盾（D002 修复引入） | 低 | 正确性 | 根因 | fix-regression | fixed | 一词对齐（PRD 为产品真相源，架构对齐 dead） | 架构 §4.2 改为 cost_negative 一律直接判 dead（覆盖 taker+滑点与资金费率拖累两情形），与 PRD FR2.2 一致 | verify.py 复跑全绿（含 check_doc_links） | 2 | 2 | spec-internal-contradiction |

## 5. 裁决记录

#1 · 提交粒度 · 追认接受 · "一 finding 一 commit"改为按域分批 7 提交（3d37552..7969a97）。证据：FIX-log 声明理由（6 路并行修复+同文件承载多条 finding）+ 各批提交边界与域对应清晰。裁决轮次：Round 2（检视人）。后续修复轮应回到一 finding 一 commit。
#2 · 状态翻权 · 追认接受 · 修复方在 7969a97 提交中翻 CURRENT 状态（协议规定检视人独占）。证据：round-2 检视人对 24+1 条逐一独立核对 diff，翻状态与实际修复全部一致。裁决轮次：Round 2（检视人）。后续轮次翻权仍归检视人。

## 6. 停止条件状态（检视人终核 · 2026-09-07）

**闭环**。基线 re-baseline：1bd8c4d → 7969a97（修复轮 7 个分批提交，HEAD 漂移来源=项目所有者按 FIX-log 提案执行，已确认）。

- Critical/High 清零（2+8 → 0/0）；28 条 + N1 全部 fixed，逐条经检视人独立 diff 核对。
- `python tools/verify.py` 六步全绿（检视人独立复跑 ×3：生命周期/文档链接/依赖 pin/pytest 25 passed/ruff×2）。
- **门禁长牙（检视人独立变异验证，非采信声明）**：① 注入死链至 RETROSPECTIVE.md → check_doc_links exit 1 精确报 file:line → git 还原 → exit 0；② 复现 C001 原始故障（pin 改回 <9 vs 本地 9.0.3）→ check_dep_pins exit 1 → 备份还原字节一致（git diff 为空）→ exit 0。
- 残余观察项 N2（low，不阻塞）：ADR-0003:6 残留 `D:\Projects\quant-crypto` 机器路径（D024 同类、原 finding 范围外），随手清。
- **CI 最终门禁客观不可执行**：本仓未配置 git remote，无推送目标——协议允许的例外情形，如实列出；配置 remote 后首推即触发 CI 补验。
- 闭环收尾已执行：RETROSPECTIVE.md 回写完整 issue 表（29 条）+ 模式教训 + 裁决分布；CURRENT 文件按 CLAUDE.md 项目约定保留入库为终态记录（内容已完整沉淀 RETROSPECTIVE + git 历史，如需按 skill 默认删除可随时执行）。
