# RETROSPECTIVE —— 检视复盘

本文件由 review-convergence skill 维护，记录每轮检视发现的缺陷与过程教训。
`docs/reviews/` 下其它文件本地-only（见 `.gitignore`）。

## 循环 1：全项目文档检视（项目开工前全量）

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 | 基线：1bd8c4d → 终基线 7969a97（修复轮 7 个分批提交）
- 检视人：Sisyphus；修复方：项目所有者（Georg/qiaozhi li）
- 范围：docs/ 全部 17 份入库文件 + CLAUDE.md/README.md/BACKLOG.md + 三路独立取证（检视人通读 + explore agent 代码区实测 + Oracle agent 战略评审）
- 结论：首轮 2 Critical / 8 High / 10 Medium / 4 Low 共 24 条；修复轮全数处理并自查发现 fix-regression N1 一条（PRD 与架构成本口径矛盾，当轮修复）；round-2 diff-only 复核逐条验证通过，verify.py 六步全绿 ×3，检视人独立变异验证两道新门禁（死链注入→红→还原→绿；pin 复现 C001 原始故障→红→还原→绿）。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D001 | 组合构建层缺失，协同池产物无部署路径 | 严重 | 正确性 | 根因 | 原始设计 | fixed | ADR-0004：meta-因子同门禁+Top-K(K=3,上限5)+逆波动率权重+换手预算+净额化 | — | 1 | 1 | — |
| D002 | 成本墙不在选择回路，资金费率零出现 | 严重 | 正确性 | 根因 | 原始设计 | fixed | PRD FR2.1/2.2/2.5+架构 §4.2 cost_verdict 硬过滤（N1 后与 PRD 对齐 dead） | — | 1 | 1 | objective-mismatch-throughput |
| D003 | FactorDef 单 pair 契约与 AlphaGen 张量栈无适配契约 | 高 | 正确性 | 根因 | 原始设计 | fixed | 架构 §4.1.1 适配契约（表达式树↔callable、feature_map、截面算子显式裁剪） | — | 1 | 1 | — |
| D004 | 多重检验"一次试验"口径未定义 | 高 | 正确性 | 根因 | 原始设计 | fixed | FR2.4：每条进评测台表达式计 1 次（含被拒者），禁存活者计数 | — | 1 | 1 | — |
| D005 | 留出期复用退化无预算 | 高 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003：周度 top-k(5) 预算+append-only 台账+永久隔离确认窗 | — | 1 | 1 | — |
| D006 | ≥30 笔与"69 笔不可信"自相矛盾 | 高 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003：30=资格线，30-69=UNDERPOWERED 带（临时 PASS+缩仓），≈69+ 才可信判定 | — | 1 | 1 | spec-internal-contradiction |
| D007 | 回填（~4600 万行）无估算无归属 | 高 | 正确性 | 症状 | 原始设计 | fixed | FR1.3 显式工作流（1-2 周 wall-clock、归属所有者）；M1 改"1 周开发+1~2 周回填并行" | — | 1 | 1 | hidden-workstream-no-owner |
| D008 | 复盘循环是数据窥探放大器 | 高 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003：generation 标签入台账+计入试验预算+确认窗对复盘不可见 | — | 1 | 1 | — |
| D009 | SOP 原则表 2/3 空占位 | 高 | 流程缺陷 | 症状 | 原始设计 | fixed | 填实 6 行（规格/留出/无前视/数据红线/实盘红线/可复现），单一 owner | — | 1 | 1 | unfilled-template-placeholder |
| D010 | 目录约定三方矛盾（平铺 vs src/<pkg> vs 打包） | 高 | 契约漂移 | 根因 | 原始设计 | fixed | 拍板 src/alphamill/<module>/，传播 8 处（架构/SOP/CLAUDE/F001×4/integration） | — | 1 | 1 | — |
| D011 | 13 处死链（docs/05、docs/02、doc 03） | 中 | 契约漂移 | 症状 | 原始设计 | fixed | 全部改现名+verify 第 2 步 check_doc_links.py 门禁化 | test_check_doc_links.py::6 tests | 1 | 1 | renamed-doc-stale-refs |
| D012 | M2 迁移乐观，L1/L2 切换判据未预成文 | 中 | 质量 | 症状 | 原始设计 | fixed | ADR-0001：二元判据清单（→L1 三条/→L2 两条），禁自我豁免 | — | 1 | 1 | — |
| D013 | Vibe 符号映射契约未前置 M1 | 中 | 质量 | 症状 | 原始设计 | fixed | integration §2.2 M1 出口标准：symbol_map.csv 初版+三条契约 | — | 1 | 1 | — |
| D014 | 数据修订/point-in-time 政策缺失 | 中 | 正确性 | 根因 | 原始设计 | fixed | integration §1.2：修订→data_version 递增+差异登记+drift 标记不强制重跑 | — | 1 | 1 | — |
| D015 | 成本参数校准来源未指定 | 中 | 正确性 | 症状 | 原始设计 | fixed | FR3.4：以 dry-run 实际成交校准，不用牌价 | — | 1 | 1 | — |
| D016 | 单卡 GPU 争用无调度 | 中 | 质量 | 根因 | 原始设计 | fixed | 架构 §7.1 时段表+FIFO 队列，禁 OOM 赌博 | — | 1 | 1 | — |
| D017 | 备份/DR 缺失 | 中 | 质量 | 根因 | 原始设计 | fixed | migration-plan §七 NAS 每日同步+7 天本地滚动+M0 恢复演练；T018 | — | 1 | 1 | — |
| D018 | RL 种子/确定性开关未进 manifest | 中 | 正确性 | 症状 | 原始设计 | fixed | FR6.1：必录随机种子+torch/cudnn deterministic | — | 1 | 1 | — |
| D019 | merge_asof 三细节未定义 | 中 | 正确性 | 症状 | 原始设计 | fixed | 架构 §4.3：缓存键版本化+陈旧界 N=1 因子周期+审计覆盖 join | — | 1 | 1 | — |
| D020 | 部署时滞 vs 衰减错配 | 中 | 质量 | 根因 | 原始设计 | fixed | 架构 §2.2 部署前再验证节点（champion 最近 30 天重过粗筛） | — | 1 | 1 | — |
| D021 | docs/README 导航行重复 | 低 | 质量 | 症状 | 原始设计 | fixed | 删除 | — | 1 | 1 | — |
| D022 | features/README 截断孤句 | 低 | 质量 | 症状 | 原始设计 | fixed | 补全 | — | 1 | 1 | — |
| D023 | verify 双入口命名混淆 | 低 | 质量 | 症状 | 原始设计 | fixed | SOP §3 显式分工 | — | 1 | 1 | — |
| D024 | committed 文档含机器绝对路径 | 低 | 质量 | 症状 | 原始设计 | fixed | PRD+README 改相对引用（ADR-0003:6 残留记观察项 N2） | — | 1 | 1 | — |
| N1 | D002 修复引入 PRD/架构成本口径矛盾 | 低 | 正确性 | 根因 | fix-regression | fixed | 架构对齐 PRD：cost_negative 一律 dead | verify.py 复跑全绿 | 2 | 2 | spec-internal-contradiction |

## 循环 2：代码区检视（脚手架）

- report_type: code-review | round: 1（full-scan）→ 2（diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 | 基线：同上 | 检视人：Sisyphus
- 范围：src/tests/tools/.github + pyproject；explore agent 实测（含 verify.py 实跑）
- 结论：首轮 2 Medium / 2 Low；修复轮全数处理；round-2 独立复核通过（含检视人双变异验证）。"设计阶段未开工"声称与代码实况一致，门禁链真实可用。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C001 | pytest pin 与本地实装矛盾（9.0.3 vs <9） | 中 | 正确性 | 流程缺陷 | 原始编码 | fixed | pin 放宽 <10+诚实注释+check_dep_pins.py 接入 verify 第 3 步 | test_check_dep_pins.py::9 tests | 1 | 1 | claim-vs-reality-pin-drift |
| C002 | validate_spec_lifecycle.py 零自身测试 | 中 | 测试覆盖 | 流程缺陷 | 原始编码 | fixed | 9 个端到端测试（verify_repo(tmp) 实测）+变异验证；本体零改动 | test_validate_spec_lifecycle.py::9 tests | 1 | 1 | gate-without-tests |
| C003 | CI 复制 verify 步骤清单 | 低 | 质量 | 症状 | 原始编码 | fixed | ci.yml 收敛单 verify job（matrix 3.11/3.13）只调 verify.py | — | 1 | 1 | — |
| C004 | pytest-cov 装而未用 | 低 | 质量 | 症状 | 原始编码 | fixed | 移除依赖；配套 pythonpath=["."] 根因修复 | — | 1 | 1 | — |

## 循环 3：目标与计划专项检视（战略层）

- report_type: doc-review | round: 3（strategic full-scan）→ 4（diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 | 基线：2411dcb（报告入库于 0693dd3）→ 终基线 8df5f9f（修复轮 8 个分批提交）
- 检视人：Sisyphus（检视人独立发起，Oracle 专项交叉验证）；修复方：同会话显式切换视角执行
- 范围：问题域为"开工后大规模方向变更风险"（论题经济学与核心回路），非文档缺陷复审；7 条 finding 落点 PRD/架构/ADR-0001/0003/0004
- 结论：首轮 2 High / 4 Medium / 1 Low（全部"现在改=半天文档、开发后改=返工"类型）；修复轮一 finding 一 commit 全数处理；round-4 diff-only 复核逐条验证通过，另探出 1 条 fix-regression（D032）当轮关闭。verify.py 全绿 ×3，首推 8df5f9f 触发 CI（运行观测因 gh 未认证受限，见循环 1 记录的同款例外）

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D025 | 论题无预注册止损线，M4 出口无时钟（G1 算术被 FR2.4 修正架空：诚实期望 1 存活/2-20 周，零存活被"门禁正确工作"无限合理化） | 高 | 正确性 | 根因 | 原始设计 | fixed | PRD G6+§2.4：触发器 10 周/100 有效独立候选（先到为准，OOS PnL 聚类测量）；预注册三分支；正控制误杀防护；跨窗复核 | verify.py 文档门禁 | 3 | 4 | open-ended-exit-no-clock |
| D026 | 优化目标与门禁筛选不同种群：奖励缺换手/频率维度，IC 最优解被 ≥30 笔门槛结构性拒绝；漏斗逐级计数缺失 | 高 | 正确性 | 根因 | 原始设计 | fixed | FR2.1 奖励扩维 + FR6.3 漏斗计数（五级逐级入库，M4 周报指认最大流失级）+ M2/ADR-0001 冒烟清单挂钩 | 同上 | 3 | 4 | objective-gate-population-mismatch |
| D027 | 协同池/Top-K 构建的数据边界未钉死在留出前（组合获得事内优势，门槛形同虚设） | 中 | 正确性 | 根因 | 原始设计 | fixed | 架构 §4.2 硬约束段 + ADR-0004 决策 2/3：池构建/Top-K/逆波动率估计窗限留出前 | 同上 | 3 | 4 | gate-contamination-timing |
| D028 | 最高信息量证据最晚到达：M1 天然是论题探针却被框定为管道工作 | 中 | 质量 | 症状 | 原始设计 | fixed | M1 出口追加探针三件套（正控制报告/GTJA191+Kronos 种子 OOS PnL 相关性矩阵/成本分解） | 同上 | 3 | 4 | deferred-thesis-probe |
| D029 | pivot 保险载体缺失：评测台只存 pass/fail 则成本模型变更=全量重跑（周级） | 中 | 质量 | 根因 | 原始设计 | fixed | report.json 增 trade_log_summary + cost_model_version（重定价降为小时级）；FR6.1 manifest 同步 | 同上 | 3 | 4 | repricing-cache-missing |
| D030 | 固定 90 天留出=单一 regime 切片；dry-run 与留出背离时验证栈公信力崩塌 | 中 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003 滚动留出路线图（v0.1 regime 标签入 manifest → v0.2 滚动窗进台账 → 检查点跨窗复核） | 同上 | 3 | 4 | single-regime-holdout |
| D031 | M3 Vibe-Trading 未官方声明可弃置（最不承重的里程碑会吞噬主回路排期） | 低 | 质量 | 症状 | 原始设计 | fixed | FR4.6 可弃置声明 + 第二意见降级"按需手动复核"（不阻塞主链路） | 同上 | 3 | 4 | droppable-undeclared |
| D032 | D031 修复引入 G3↔FR4.6 矛盾：G3 仍无条件要求 Vibe 接入 | 中 | 正确性 | 根因 | fix-regression | fixed | G3 验收条款补"M3 time-box 内达成；弃置时随降级" | verify.py 复跑全绿 | 4 | 4 | spec-internal-contradiction |

## 循环 4：F001 设计文档开发前检视（full-scan）

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核，含 R2-01 发现与当轮修复及封顶复核——闭环过早）→ 3（闭环后审计重开：发现 R3-01/R3-02 并当轮修复关闭）| 状态: 闭环
- 日期：2026-09-07 | 基线：9a95cee（报告入库于 a7e93cd）→ 终基线 56c5724（修复轮 6 个提交）
- 检视人：Sisyphus；修复方：同会话显式切换视角执行（状态翻转权归检视人）
- 范围：F001 三件套 + migration-plan.md 全文；交叉契约 PRD M0/非目标、架构 §五/§七、SOP、features/README；开发环境实测取证
- 结论：首轮 3 High / 1 Medium / 2 Low，全部"现在改半天文档、开工后改返工"型；修复轮一 finding 一 commit 全数处理（D034+D037 因共用 tasks.md 编号编辑面合并为一 commit，检视人追认）；round-2 diff-only 复核逐条验证通过，另探出 1 条首轮漏检（R2-01：D034 修复只覆盖检视人点名的 item 5/8，未对 SC-003 九项清单做全集核对——item 9 user_data 仍无任务）当轮修复；第 3 轮封顶复核无新发现。`python3 tools/verify.py` 全量七步全绿 ×2，闭环提交推送后 CI 观测绿。round-2 闭环被检视人事后审计推翻——数据源「承认可达性未验」不应计入闭环；重开 round-3 实证（qiaozhi-lt 实为用户另一台 Windows 工作机，本开发机是 qiaozhi-gp，旧 skill 设备表已过期；数据在 qiaozhi-lt Docker 卷 `quant-crypto_timescale_data`，实测 ohlcv_1m 6,504,359 行 / 11 表 / 5 连续聚合；SSH 流式 pg_dump 路径免开 5432 防火墙），R3-01/R3-02 当轮修复关闭，附带 design §3 对账口径按实库 6→11 表补全，循环正式闭环。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D033 | migration-plan §五 验收含 data_bridge Parquet 导出，与 spec 非目标（F002/M1）直接矛盾——F001 验收清单永远无法全绿 | 高 | 正确性 | 根因 | 原始设计 | fixed | §五 删除该验收框+范围澄清引注；§四 阶段 A 钉"（F002 起）" | verify.py 文档门禁 | 1 | 1 | spec-internal-contradiction |
| D034 | SC-003 要求 §一 9 项全勾，tasks 缺 item 5（评测/门禁脚本）与 item 8（宇宙发现）任务；spec 范围内枚举漏 item 5 | 高 | 正确性 | 根因 | 原始设计 | fixed | tasks 补 T012/T013（原样迁移+import 冒烟，泛化留 M1）；spec 枚举补 item 5 | validate_spec_lifecycle + verify | 1 | 1 | spec-tasks-traceability-gap |
| D035 | 环境契约漂移：文档假设 Windows 11+Docker Desktop+RTX 4060，实况 WSL2+docker-ce、无 pwsh、GPU 不可见、旧仓本机不可见——T002/AC-002/AC-005 按字面不可执行 | 高 | 正确性 | 根因 | 原始设计 | fixed | design §0 执行环境实测钉死（WSL2/docker-ce 29.1.3/Ubuntu 26.04）；pwsh=apt 安装；GPU=T003 前置直通检查+CPU 回退；旧仓=T001 定位钉死；spec 依赖+NFR-002+FR-003、design §7、CLAUDE.md、tasks 同步 | verify.py 文档门禁 | 1 | 1 | environment-contract-drift |
| D036 | 对账口径三方不一致：AC-001"三表" vs design §3 六表 vs FR-001 三组——按 AC 验收漏 signals_log/trades_log | 中 | 正确性 | 症状 | 原始设计 | fixed | design §3 为唯一权威口径（补连续聚合），FR-001/AC-001/design §8 引用之，废除"三表"措辞 | verify.py 文档门禁 | 1 | 1 | spec-internal-contradiction |
| D037 | tasks.md T018 编号乱序（Phase 2 内 T010 与 Phase 3 T011 之间） | 低 | 质量 | 症状 | 原始设计 | fixed | 全量重编号使编号=执行顺序（R2-01 插入后延至 T022 仍保持） | validate_spec_lifecycle | 1 | 1 | — |
| D038 | item 9 kronos_cache/feather 的 git 边界未说明，"首批信号缓存样本"入库与否无定论 | 低 | 质量 | 症状 | 原始设计 | fixed | item 9 改造点注明：入库仅策略+config；缓存/feather 本地资产不进 git；样本供 F002 校验 | — | 1 | 1 | — |
| R2-01 | D034 修复未对 SC-003 九项做全集核对：item 9（user_data 策略+config）仍无任务，SC-003 仍不可全勾 | 高 | 正确性 | 症状 | 原始设计（首轮漏检） | fixed | tasks 补 T014（user_data 迁移）+依赖 T014→T017，后续顺延至 T022 | validate_spec_lifecycle + verify | 2 | 2 | spec-tasks-traceability-gap |
| R3-01 | T004 数据源不可达且未定义：六路探测全否（本机无 Docker Desktop/无原生 PG/无其他发行版/5432 全闭/无备份痕迹），round-2 以「承认未验」状态闭环过早 | 高 | 正确性 | 根因 | fix-regression（D035 数据面残留） | fixed | 数据源实证钉死：qiaozhi-lt（Tailscale `100.98.228.125`，SSH `Georg@` 密钥 `~/.ssh/gp-to-lt`）`D:\Projects\quant-crypto` Docker 卷 `quant-crypto_timescale_data`（实测 6,504,359 行/11 表/5 caggs）；SSH 流式 pg_dump 路径（免开 5432 防火墙）；design §0/§3、tasks T001/T004、spec §7、migration-plan item 1 五处同步 | verify.py 文档门禁 | 3 | 3 | unpinned-data-source |
| R3-02 | T012/T013/T014 任务引用 SC-003 偏离 tasks 模板的「US/需求/AC ID」枚举 | 低 | 质量 | 症状 | fix-regression（D034/R2-01 修复引入） | fixed | tasks §0 显式扩展条款：SC-xxx 为合法任务引用锚 + 理由记录（泛化属 F002/M1，无对应 FR） | validate_spec_lifecycle | 3 | 3 | template-id-drift |

## 循环 5：目标重构文档检视

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only，未验证即误报闭环）→ 3（回到基线重做 + diff-only 复核）| 状态: 闭环
- 日期：2026-09-07 → 2026-09-08 | 基线：f6cd6a1 → 终基线 d2bb055（8 个 finding 修复提交 + 2 个 fix-regression 补充提交；D047 的 FIX-log 为 local-only 过程证据）
- 检视人：Sisyphus；修复方：项目所有者（round-3 开工前独立核对 round-2 声明）
- 范围：目标重构后的 PRD / 架构 / ADR-0001/0003/0004 / 三入口文档 / 检视产物生命周期 / 统一门禁可执行性。
- 结论：共 5 High / 2 Medium / 3 Low，D039–D048 全数关闭。round-2 对 D039–D043 的 fixed 声明经工作树核对证伪；round-3 回到 f6cd6a1 重做后逐项复核，并在轮末门禁再捕获 2 处 fix-regression（功效论证引语、命令扫描器自引用），均已修复。本地 `python3 tools/verify.py` 七步全绿（40 passed）；GitHub Actions run 34133866296（@ d2bb055）success，正式满足停止条件。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D039 | ADR-0001 M2 漏斗顺序与组合冻结契约冲突 | 高 | 正确性 | 根因 | fix-regression | fixed | 重做为「选择期 → 组合门/冻结 → 留出门 → 最终确认 → 部署前复核」 | 链接门 + 三处漏斗对照 | 1 | 3 | cross-doc-contract-drift |
| D040 | PRD 漏斗与 FR3.2/3.4/3.5 不对齐 | 中 | 正确性 | 根因 | 原始编写 | fixed | 成本门前置，补去重/多重检验、组合冻结和样本量三级裁决 | 链接门 + 三处漏斗对照 | 1 | 3 | cross-doc-contract-drift |
| D041 | ADR-0003 决策 2 缺 30–69 笔临时 PASS 档 | 低 | 正确性 | 症状 | 规格漂移 | fixed | 改为三级口径并同步功效论证引语 | 链接门 + 四处口径检索 | 1 | 3 | — |
| D042 | 架构目录树 holdout_gate.py 仍是旧的二级口径 | 低 | 质量 | 症状 | 规格漂移 | fixed | 注释改为三级裁决并引用 FR3.5 | 链接门 + 注释复核 | 1 | 3 | — |
| D043 | CLAUDE/README/docs README 的四平面命名不一致 | 低 | 质量 | 症状 | 规格漂移 | fixed | 三入口统一四平面全称 | 链接门 + 入口措辞检索 | 1 | 3 | — |
| D044 | CURRENT 过程稿被反向放行且文档声明应入库 | 高 | 正确性 | 根因 | 流程缺口 | fixed | 仅放行 RETROSPECTIVE，同步 CLAUDE/SOP，增加 gitignore 契约测试 | 变异验证 + test_review_artifacts_gitignore | 2 | 3 | review-artifact-lifecycle-drift |
| D045 | 组合门/PortfolioDef 冻结同时归属两个平面 | 中 | 正确性 | 根因 | 原始编写 | fixed | 冻结职责唯一归策略与执行面，同步面间箭头 | 链接门 + 平面职责复核 | 2 | 3 | cross-plane-ownership-drift |
| D046 | 文档唯一门禁命令在目标环境不可执行 | 高 | 正确性 | 根因 | 原始编写 | fixed | 全仓统一 `python3 tools/verify.py`，ruff 改为 `sys.executable -m`，增命令契约测试 | 变异验证 + test_doc_gate_command | 2 | 3 | documented-command-not-runnable |
| D047 | 修复缺 FIX-log、原子提交和可核验哈希 | 高 | 测试覆盖 | 根因 | 流程缺口 | fixed | 补齐 local-only FIX-log，逐条核对 f6cd6a1..d2bb055 提交证据 | git log 独立核验 | 2 | 3 | review-evidence-missing |
| D048 | round-2 将未落地或错误落地的 D039–D043 标为 fixed | 高 | 正确性 | 根因 | 流程缺口 | fixed | 工作树证伪后从基线重做，fixed 翻转改为必须核对 diff 与测试 | baseline-vs-claim diff 核对 | 3 | 3 | marked-fixed-not-implemented |

## 循环 6：F001 实现代码检视（quant-crypto 迁移，v0.1 收口后）

- report_type: code-review | round: 1（full-scan）→ 2/3/4/5（diff-only 复核）| 状态: 闭环
- 日期：2026-09-12 | 基线：39875e1 → 终基线 8d6b775（5 轮，46 个修复提交）
- 检视人：Claude Opus 5（第 5 轮后按 skill §7 升级协议(b) 角色合并，亲自修复 C401）；修复方：项目所有者的 AI 助手
- 范围：F001 全部代码资产 ~10.5k 行——`src/alphamill/`（采集器/Kronos 薄壳/风控三件套/评测脚本）、`deployment/`（compose/verify.ps1/备份/supervisor）、`db/`、`freqtrade/user_data/`、`scripts/`、`tools/`、`tests/`
- 结论：首轮 0 Critical / 4 High / 13 Medium / 6 Low 共 23 条；五轮累计 49 条，其中 26 条为修复引入（fix-regression）。High 曲线 4→3→1→0→0，每轮新增 fix-regression 8→7→4→3，两条线同时收敛后判定闭环。
- 核心结论（首轮）：搬迁本身完整，但 F001 的 done 状态主要由一次性人工实测支撑，仓内固化的门禁大多不具备判红能力——AC-005 的 26 项检查里 16 项只打印不断言、AC-001 的完整性口径由实得数据自身推导、AC-001 的衍生品子句零实现、策略 import 的 risk 包根本不在仓树内。
- 检视人独立验证（非采信声明）：verify.ps1 的 `-ExpectPass` 变异验证（删断言→红）、对线上 631 万行库实跑 NULL INSERT + ROLLBACK（C105）、`docker compose ps` + `/api/v1/ping` 实测容器状态（C101/C201）、`apply_migrations.py` 对线上库两次实跑验幂等（C301）、`bash -c 'set -u; SYMBOLS=a true; echo $SYMBOLS'` 实证 shell 作用域（C110）、C401 两道新门禁各做一次变异验证。

| ID | 一句话 | 严重度 | 分类 | 根因 | 来源 | 状态 | 修复方案（摘要） | 回归测试 | 首现轮 | 关闭轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C001 | verify.ps1 的 16 项 DB 检查只打印不断言，4 个聚合抽样算出 checked/matching 却从不比较 | 高 | 正确性 | 根因 | 原始编码 | fixed | Invoke-DbCheck 增 MinRows/-ExpectPass/-Validator 三档断言，标量 SQL 统一 CASE WHEN…THEN 1 | test_verify_db_gate_contract.py | 1 | 2 | gate-without-teeth |
| C002 | AC-001 完整性口径自证：expected 由实得数据 min/max 推导，截断回填恒 PASS | 高 | 正确性 | 根因 | 原始编码 | fixed | 改由权威窗口计算 expected_minute_rows + boundary_ok 双断言，verify.ps1 同步 | test_f001_backfill_report.py | 1 | 2 | gate-measures-itself |
| C003 | 衍生品三表零门禁，但 AC-001 已勾选"衍生品表逐表行数符合预期" | 高 | 正确性 | 根因 | 契约漂移 | fixed | derivative_verdict 并入 report verdict；derivatives main 失败即返回 1 | test_f001_backfill_report.py | 1 | 2 | marked-done-not-implemented |
| C004 | 策略 from risk.* 的顶层包不在仓树内，dry-run 容器也不在编排里 | 高 | 正确性 | 根因 | 契约漂移 | fixed | import 改 alphamill.freqtrade_bridge.risk；compose 新增 freqtrade service + entrypoint + PYTHONPATH | test_f001_compose_contract.py | 1 | 2(partial)→3 | orchestration-outside-repo |
| C005 | 回填遇空批即 break 并无条件标记 complete，截断被记成完成 | 中 | 正确性 | 根因 | 原始编码 | fixed | 空批/游标不前进写 stalled 并抛错，main 汇总 failed 返回 1 且不刷新聚合 | test_historical_backfill_review_fixes.py | 1 | 2 | silent-truncation |
| C006 | 聚合一致性比较不对称：视图不按 exchange 过滤、基表按 exchange 过滤 | 中 | 正确性 | 根因 | 原始编码 | fixed | 视图侧补 WHERE exchange = %s | test_f001_backfill_report.py | 1 | 2 | asymmetric-comparison |
| C007 | okx 默认值成簇残留（9 处），与钉死的 binance 路线冲突 | 中 | 正确性 | 根因 | 契约漂移 | fixed | compose/.env.example/server/db_adapter/两个回填/snapshot/策略/config 统一 binance | test_f001_exchange_defaults.py | 1 | 2 | stale-default-after-pivot |
| C008 | KRONOS_REPO_PATH 默认 external/Kronos，仓内实际是 vendor/Kronos | 中 | 正确性 | 根因 | 原始编码 | fixed | 默认改 vendor/Kronos；/health 在 enabled 且 unavailable 时返回 degraded | test_kronos_health.py | 1 | 2 | stale-default-after-pivot |
| C009 | 003 衍生品迁移未挂进 compose initdb，新 clone 起库缺表 | 中 | 正确性 | 根因 | 契约漂移 | fixed | compose 以 02_ 挂进 docker-entrypoint-initdb.d | test_f001_compose_contract.py | 1 | 2 | doc-says-auto-code-says-manual |
| C010 | 快照脚本把 null 指标写成 0，面板"有数"可由伪造 0 满足 | 中 | 正确性 | 根因 | 原始编码 | fixed | ConvertTo-SqlNumber 对 null/空返回 NULL | test_runtime_snapshot_contract.py | 1 | 2 | null-coerced-to-zero |
| C011 | 备份的 reports//lake/ 走未校验单流通道，脚本自己记录了 NAS 10MB 会 reset | 中 | 正确性 | 根因 | 原始编码 | fixed | transfer_directory_to_nas 分块+双端 md5；dump 加 pg_restore --list；dd 改 iflag=skip_bytes | test_backup_nas_contract.py | 1 | 2 | known-broken-path-left-in |
| C012 | 明文凭据入库（API 口令/JWT/WS token），同口令硬编码进门禁与测试 | 中 | 正确性 | 根因 | 原始编码 | fixed | config 改 ${FREQTRADE_*} 占位 + entrypoint 运行时渲染；check_secrets 增明文口令规则 | test_f001_credentials.py | 1 | 2(partial)→3 | plaintext-credential-in-repo |
| C013 | 备份通道 StrictHostKeyChecking=no + known_hosts=/dev/null | 低 | 正确性 | 根因 | 原始编码 | fixed | 改 yes + 专用 known_hosts + ssh-keygen -F 预检 | test_backup_nas_contract.py | 1 | 2 | — |
| C014 | BACKFILL_RETRIES=0 时 rows 保持 None 触发 TypeError | 低 | 正确性 | 根因 | 原始编码 | fixed | retry_count() 把重试下限钳到 1 | test_historical_backfill_review_fixes.py | 1 | 2 | — |
| Q001 | F001 四条 AC 的集成测试在工作树 100% skip，证据不可复现 | 中 | 测试覆盖 | 根因 | 流程缺陷 | fixed | _require_or_skip：ALPHAMILL_INTEGRATION=1 时服务不可达/mock 一律 fail；SOP 增收口纪律 | tests/integration/ 全部 | 1 | 2 | evidence-not-reproducible |
| Q002 | 风控三件套零单元测试，含批量场景（多持仓相关性）无用例 | 中 | 测试覆盖 | 根因 | 原始编码 | fixed | test_risk_guards.py 四例：熔断日界/连亏冷却/回撤正反/相关性多持仓批量 | test_risk_guards.py | 1 | 2 | — |
| Q003 | DrawdownGuard 在 lookback_days>0 时权益基线错位 | 中 | 质量 | 根因 | 原始编码 | fixed | evaluate 增 starting_equity 形参 | test_risk_guards.py | 1 | 2(partial)→3 | — |
| Q004 | 权威回填窗口常量在三处各写一份 | 中 | 质量 | 根因 | 原始编码 | fixed | 新增 f001-backfill-window.env 单一来源 + f001_backfill_config.py 读取层 | test_f001_backfill_window_source.py | 1 | 2 | constant-duplicated-across-layers |
| Q005 | 8 个文件超 CLAUDE.md 350 行硬上限且未登记豁免 | 中 | 质量 | 根因 | 原始编码 | fixed | SOP 增豁免表（原因+F002 解除期限） | test_f001_line_limit_exemptions.py | 1 | 2(partial)→3 | unregistered-exemption |
| Q006 | backfill_progress 表有两份 DDL（init.sql 与 ensure_progress_table） | 低 | 质量 | 根因 | 原始编码 | fixed | ensure_progress_table 改 to_regclass 存在性校验，DDL 唯一来源回到 init.sql | test_historical_backfill_review_fixes.py | 1 | 2 | — |
| Q007 | supervisor 硬编码个人绝对路径与内网 IP，只 set -u 无 -e | 低 | 质量 | 根因 | 原始编码 | fixed | set -euo pipefail + BASH_SOURCE 相对 REPO_ROOT + 配置读取 + 未达标非零退出 | test_f001_supervisor_contract.py | 1 | 2(partial)→3 | — |
| Q008 | db_adapter 的 docker 回退路径拼字符串 SQL 且 compose 不带 -f | 低 | 质量 | 根因 | 原始编码 | fixed | 改 psql -v 变量传参；compose 调用固定 -f | test_kronos_db_adapter.py | 1 | 2 | — |
| Q009 | verify.ps1 的 psql 硬编码 -U quant -d quant | 低 | 质量 | 根因 | 原始编码 | fixed | 统一从 .env 解析 $dbUser/$dbName | test_verify_env_contract.py | 1 | 2 | — |
| C101 | compose 的 freqtrade 服务没有 8080 端口映射，自身门禁够不到 | 高 | 正确性 | 根因 | fix-regression | fixed | 补 ports ["8080:8080"] 并在契约测试断言 | test_f001_compose_contract.py | 2 | 3 | orchestration-outside-repo |
| C102 | deployment/.env 未补 FREQTRADE_API_*，凭据 fail-closed 后门禁实测 401 | 高 | 正确性 | 根因 | fix-regression | fixed | .env 补四变量；conftest 载入 .env 并把 DB_HOST 由服务名改回回环 | tests/integration/conftest.py | 2 | 3 | fail-closed-without-migration |
| C105 | 快照写 NULL 违反 dryrun_runtime_snapshots 的 NOT NULL 约束，采集必崩 | 高 | 正确性 | 根因 | fix-regression | fixed | 新增 004 迁移把 8 个指标列 DROP NOT NULL；init.sql 同步；compose 挂 03_ | test_runtime_snapshot_contract.py（另经线上 NULL INSERT 实测） | 2 | 3 | fix-breaks-schema-contract |
| C103 | 衍生品预期行数由"已尝试窗口"推导，自证问题上移一层 | 中 | 正确性 | 根因 | fix-regression | fixed | 增 progress_window_covers_authoritative_window 前置；有效窗口改显式 MAX_DAYS 配置 | test_f001_backfill_report.py | 2 | 3 | gate-measures-itself |
| C104 | 新边界判据与 spec §3"深度不足/下架不判红"冲突 | 中 | 正确性 | 根因 | fix-regression | fixed | backfill_boundaries：listing_start + unavailable 显式配置；剩余下架场景转 C202 | test_historical_backfill_review_fixes.py | 2 | 3(partial)→4 | over-correction-vs-spec |
| C107 | starting_equity 无生产调用方，Q003 在真实路径未生效 | 中 | 正确性 | 根因 | fix-regression | fixed | 策略两处 evaluate 传入 _drawdown_starting_equity()，缺基线即抛错 | test_risk_guards.py | 2 | 3 | api-added-caller-not-updated |
| C109 | 行数豁免登记路径写错，真实超限文件未登记且测试锁错对象 | 中 | 质量 | 根因 | fix-regression | fixed | 路径修正 + 测试改为"扫实际 >350 行集合与登记表等值断言" | test_f001_line_limit_exemptions.py | 2 | 3 | test-simulates-itself |
| C110 | supervisor 的 $SYMBOLS 未导出，set -u 下衍生品回填前中断或只跑 2 对 | 中 | 正确性 | 根因 | fix-regression | fixed | 显式 BACKFILL_SYMBOLS + EXPECTED_SYMBOL_COUNT，去掉写死的 6 | test_f001_supervisor_contract.py | 2 | 3 | shell-scope-assumption |
| C106 | NAS 远端解包结果未校验，解包失败仍算备份成功 | 低 | 正确性 | 根因 | fix-regression | fixed | 远端 tar 退出码显式判断，失败 return 1 | test_backup_nas_contract.py | 2 | 3 | known-broken-path-left-in |
| C108 | 集成测试仍硬编码 6 对与 binance 字面量 | 低 | 质量 | 根因 | 原始编码 | fixed | configured_symbols/configured_exchanges 从配置取 | test_f001_backfill_window_source.py | 2 | 3 | constant-duplicated-across-layers |
| C111 | collect_runtime_snapshot.ps1 的 psql 仍硬编码 DB 身份 | 低 | 质量 | 根因 | 原始编码 | fixed | Read-DotEnv 取 DB_USER/DB_NAME | test_runtime_snapshot_contract.py | 2 | 3 | — |
| Q101 | 13 个新增"回归测试"是源码字符串 grep，挡回退不挡行为错误 | 中 | 测试覆盖 | 根因 | 流程缺陷 | fixed | test_script_runtime_contracts.py：bash -n + stub ssh 真跑 nas_append_chunk + pwsh 真跑 Invoke-DbCheck | test_script_runtime_contracts.py | 2 | 3 | test-simulates-itself |
| C201 | FREQTRADE_JWT_SECRET_KEY 仅 31 字符 < minLength 32，compose 服务崩溃重启 | 高 | 正确性 | 根因 | fix-regression | fixed | 三处口令改 ≥32；entrypoint 渲染后校验 jwt 长度，<32 即非零退出 | test_f001_credentials.py（另经容器实拉起验证） | 3 | 4 | fail-closed-without-migration |
| C202 | 窗口中途下架的交易对仍硬失败，与 spec §3 冲突（C104 剩余载体） | 中 | 正确性 | 根因 | fix-regression | fixed | delisting_end_for + BACKFILL_SYMBOL_DELISTING_ENDS；回填按 availability_end 收口写 complete | test_historical_backfill_review_fixes.py | 3 | 4 | over-correction-vs-spec |
| C203 | AC-001 的校验宇宙改读 gitignored 的 .env，.env.example 只有 2 对 | 中 | 正确性 | 根因 | fix-regression | fixed | EXCHANGES/DERIVATIVES_EXCHANGE/SYMBOLS 权威值写入入库的 window.env | test_f001_backfill_window_source.py | 3 | 4 | evidence-not-reproducible |
| C204 | 衍生品覆盖判据用跨 symbol 的 min/max 聚合，单 symbol 缺口被掩盖 | 低 | 正确性 | 根因 | fix-regression | fixed | progress_coverage() 改 GROUP BY symbol + bool_or，要求每个配置 symbol 自行覆盖 | test_f001_backfill_report.py | 3 | 4 | gate-measures-itself |
| C205 | 快照脚本每 5 分钟执行一次 DDL 迁移，与 Q006"DDL 唯一来源"相反 | 低 | 质量 | 根因 | fix-regression | fixed | 改 information_schema 校验 8 列可空性，不满足即抛错 | test_script_runtime_contracts.py | 3 | 4 | — |
| C206 | 报告工具遗留一条结果被丢弃的查询与失配提示语 | 低 | 质量 | 根因 | fix-regression | fixed | 删死代码，提示语与默认值来源改为 configured_exchanges() | test_f001_backfill_window_source.py | 3 | 4 | — |
| P201 | 修复声明把仓内配置缺陷归因为"外部服务可用性"，且声明含未提交改动 | 低 | 质量 | 根因 | 流程缺陷 | fixed | FIX-log 增 attribution correction；未提交改动随 bca686a 入库 | —（证据为更正段与干净工作树） | 3 | 4 | attribution-drift |
| C301 | 004/003 迁移对既有库没有应用入口，升级后快照脚本直接停摆 | 中 | 正确性 | 根因 | fix-regression | fixed | tools/apply_migrations.py：按文件名序幂等执行 + schema_migrations 账本 + 手册 | test_apply_migrations.py（另经线上库两次实跑） | 4 | 5 | fail-closed-without-migration |
| C302 | 符号宇宙两份来源，采集面（.env）与校验面（window.env）优先级相反 | 中 | 正确性 | 根因 | fix-regression | fixed | _setting 优先级改 os.getenv→.env→window.env；四处回退默认值统一 6 对；supervisor 调换 source 顺序 | test_f001_backfill_window_source.py | 4 | 5 | constant-duplicated-across-layers |
| C303 | 报告里 progress_window_start/end 恒为 None | 低 | 质量 | 根因 | fix-regression | fixed | 形参与 JSON 字段一并删除 | test_f001_backfill_report.py | 4 | 5 | — |
| C304 | FIX-log 对 Freqtrade API 的归因仍不准（称 502 由上游代理） | 低 | 质量 | 根因 | 流程缺陷 | fixed | 复测并定位真实根因：NAS mihomo 的 HK 组用 Google 204 做泛化探针、与 Binance 可达性不一致，改 api.binance.com/api/v3/ping 探针 | —（证据为可复跑探针命令） | 4 | 5 | attribution-drift |
| C401 | C302 反转优先级后，AC-001 判据窗口变成可被 gitignored 的 .env 覆盖（C203 模式回潮） | 中 | 正确性 | 根因 | fix-regression | fixed | 判据量（窗口+可用性边界+OI 深度上限）改走 _verdict_setting()：只认 env 与入库 window.env；运行量保持 .env 覆盖 | test_f001_backfill_window_source.py::test_verdict_settings_ignore_runtime_dotenv / ::test_runtime_dotenv_files_carry_no_verdict_settings（两道各做一次变异验证） | 5 | 5 | evidence-not-reproducible |
| C402 | initdb 路径不写版本账本，runner 首跑会重放全部迁移 | 低 | 正确性 | 根因 | fix-regression | fixed | compose 整挂 db/migrations 到 initdb 子目录 + initdb-apply-migrations.sh 按序应用并登记 schema_migrations，与 tools/apply_migrations.py 共用同一账本 | test_apply_migrations.py::test_initdb_and_runner_share_one_migration_ledger（另经一次性容器实证：initdb 登记两条账本后 runner 输出 migrations applied: none） | 5 | 收尾轮 | — |
| C403 | 迁移 runner 在单事务内整文件执行，容不下 CREATE INDEX CONCURRENTLY 类语句 | 低 | 质量 | 根因 | fix-regression | fixed | 新增 assert_transactional()：CONCURRENTLY/VACUUM/ALTER SYSTEM/CREATE DATABASE|TABLESPACE 提前报可读错误；约束写进 runner docstring | test_apply_migrations.py::test_non_transactional_statements_are_rejected_before_execution / ::test_shipped_migrations_pass_the_transactional_guard | 5 | 收尾轮 | — |
| C501 | 文档化的 AC-006 命令缺少宿主 DB 环境，照抄必失败（/health 500） | 中 | 正确性 | 根因 | fix-regression | fixed | DB_HOST 默认是 compose 服务名 timescaledb，宿主上不可解析；spec §6 与测试 docstring 补 `set -a; . ./deployment/.env; set +a` + `DB_HOST=127.0.0.1`，与 f001-backfill-supervisor.sh 同一约定 | test_f001_compose_contract.py::test_ac006_command_carries_host_database_env | 收尾轮 | 收尾轮 | documented-command-never-run |
| AC-002-gap | compose 的 kronos 默认 mock，AC-002 要求 source=kronos，仓内编排产不出该证据 | 中 | 测试覆盖 | 根因 | 上游任务未执行 | fixed | owner 裁决取「编排内降级证据 + 真实推理独立命令」：AC-002 拆为 AC-002（编排内契约，source 与 model_enabled 双向 fail-closed）+ AC-006（真实推理证据，KRONOS_REQUIRE_REAL_MODEL=1 显式命令，证据即原 T008 实测）；容器化落 F002 T014。验收范围不缩小，ALPHAMILL_INTEGRATION=1 由 1 failed 变 7 passed 1 skipped | test_f001_kronos_smoke.py::test_kronos_predict_source_matches_declared_mode / ::test_kronos_predict_returns_kronos_source（两条各经一次变异验证） | 2 | 裁决轮 | evidence-not-reproducible |

## 模式教训

1. **spec-internal-contradiction 五次复现**：D006（PRD 内部自相矛盾）、N1（PRD↔架构跨文档矛盾）、D032（G3↔FR4.6，由 D031 修复引入）、D033（migration-plan §五验收↔spec 非目标）、D036（AC-001↔design §3↔FR-001 三方口径）共用同一模式——多文档体系里"同一语义多处表述"必然漂移，且新条款引入时最容易砸中旧条款。循环 4 两条（D033/D036）都在 F001 三件套内部，印证"验收清单+范围声明"是漂移重灾区。防线已部分门禁化（check_doc_links 抓死链），但语义级一致性仍靠检视；后续同类风险点：cost_verdict 口径、30/69 笔数字、§2.4 检查点与 G1/G6 的触发器口径、FR6.3 漏斗分级名（PRD/ADR-0001 两处表述须同步改）。
2. **文档改名不 grep 全引用**（D011）：编号命名 → alphamill-* 改名留下 13 处死链。已门禁化（相对链接存在性检查进 verify），机器可防。
3. **claim-vs-reality 声明与事实漂移**（C001）：注释承诺"上界与本地验证版本一致"被 __pycache__ 物证推翻。教训：物证（pyc/lock/manifest）优先于声明；已门禁化（check_dep_pins）。
4. **gate-without-tests**（C002）：校验器自身是全仓最复杂代码却零测试——"门禁自己没人审"是结构性盲区。已补端到端测试+变异验证。
5. **hidden-workstream-no-owner**（D007）：大工作量藏在"并行推进"一句话里且无归属。M1 路标修正为显式双轨。
6. **objective-mismatch-throughput**（D002）：吞吐量放大的是与上一代死因相同的候选群体——修复方向是把成本（含资金费率）前置进选择回路，这是循环 1 最重要的战略级修正。
7. **open-ended-exit-no-clock**（D025）：无时钟的出口条款会被"系统正确工作"叙事无限续期——任何"等首个 X 出现"型验收都必须配触发器时钟与预注册分支，独立性口径要写明"测量而非名义计数"。
8. **战略层问题域单独成轮**（循环 3）：D025-D031 全部是"计划接触现实后活不活"的问题，症状一致（系统绿灯运转但零存活），与循环 1 的"文档对不对/全不全"是不同问题域——两类检视交替扫，比混在同一轮更有效；战略层的修复多数是"预注册条款"（检查点/漏斗/边界/可弃置声明），特征是现在改半天、开工后改返工。
9. **archive-without-secret-scan**（2026-09-07 事件，非检视循环内发现）：对话归档提交把会话转录中带 Bearer 凭证的 curl 命令原样入库并推送（火山 Ark API key，私有仓暴露约 1 小时，GitHub 侧检出告警）。处置：key 轮换 + git filter-repo 历史重写 + force push（21c95cd→c6ecf29、c3bad7b→3e4a260，早期哈希不变）。防线已门禁化：verify.py 第 4 步 check_secrets.py（uuid-bearer/apikey、github-token、sk-、AKIA、PEM 六类形态）+ test_repo_tree_self_scan_clean 双层拦截。教训：转录/归档类内容不是惰性文档——会话里执行过的带凭证命令会被原样记录；OpenCode 本地库仍含旧 key 串，将来重导归档会被门禁拦下，届时需先做导出侧脱敏。
10. **closure-without-verification / marked-fixed-not-implemented**（循环 4 round-2→3；循环 5 D048）：循环 4 把「数据源可达性未验」计入闭环；循环 5 round-2 又将未落地或错序落地的 D039–D043 标为 fixed。两者共同证明：闭环不认口头指认、FIX-log 自述或「已知未验」，只认目标环境实测、工作树 diff、回归测试和可核验提交。fixed 翻转前必须由检视人独立核对这四类物证。
11. **spec-tasks-traceability-gap：清单验收只抽查不普查**（D034+R2-01，循环 4）：SC-003 要求 9 项全勾，首轮检视只点名了缺任务的 item 5/8，修复方照单补齐——但 item 9（user_data）同样无任务，round-2 diff-only 才暴露。教训：**凡是"清单全覆盖"型 finding（SC 要求 N 项全 X），修复时必须对清单全集逐项重新核对，不能只修检视人点名的子集**——检视人点名的是样本不是全集，照单全收会把漏检从检视方转移给修复方再一起背。round-2 抓到的是"首轮漏检"而非"修复引入"，证明 diff-only 复核对采样遗漏同样有效。
12. **environment-contract-drift：环境假设未实测就成文**（D035，循环 4）：三件套+CLAUDE.md 全线假设 Windows 11+Docker Desktop+RTX 4060+`../quant-crypto`，无一行的真实（实况 WSL2+docker-ce、无 pwsh、GPU 不可见、旧仓不在本机），机器门禁全绿——结构门禁不校验环境事实。教训：**环境类契约写入文档前必须有当日实测记录**（内核/引擎版本/工具存在性/路径存在性），且"本机不可见"这类负事实（absence）也要成文，否则执行第一天撞墙。修复时把不可取证的项（旧仓路径）留为显式前置任务而非编造值。
13. **合并 commit 的协议边界**（循环 4，D034+D037）：两 finding 共用同一编号编辑面时，拆分提交会人为制造"中间态编号错序"（恰是 D037 要修的缺陷）——此时合并为一 commit 并在 commit message 与 FIX-log 双处声明理由，属可追认偏差；判据是"拆分是否违背其中一条 finding 的修复目标本身"。
14. **cross-doc-contract-drift：全局契约改写必须按语义全集复核**（D039–D043/D045，循环 5）：漏斗顺序、样本量口径、四平面命名和职责在 PRD/架构/ADR/入口文档多处投影，只修某个点会立即造成新的 fix-regression。此类修复的验收单位应是「语义的全部表示」，不是单文件 diff。
15. **流程契约也要做可执行回归**（D044/D046，循环 5）：「过程稿不入库」和「统一命令可运行」不能只写在 SOP；前者用 gitignore 契约测试，后者用目标 shell 实跑与命令扫描器固化，且都应做变异验证确认门禁能真正变红。
16. **reinstall-without-data-inventory：高危操作前未盘点不可重购资产**（2026-09-10 事件，非检视循环内发现）：宿主机（实为 F001 数据源现场，hostname qiaozhi-lt）于 2026-09-07~08 整机重装 Windows 11——C 盘格式化前仅备份了 AI 会话/配置/旧 WSL 归档，未盘点 Docker Desktop 数据盘；quant-crypto 的 TimescaleDB 命名卷 `quant-crypto_timescale_data`（ohlcv_1m 6,504,359 行、11 表、5 连续聚合及 signals/trades/quality 研究产物）随旧 C 盘 VHDX 灭失。2026-09-10 六路取证（D:/E: 全盘 vhdx、pre-format 备份清单、旧 WSL tar、NAS docker 卷、qiaozhi-gp、Windows .ssh）确认无副本；NVMe+TRIM 下不可恢复。D017 设计的 NAS 每日备份（migration-plan §七）因 T015 未执行而未生效——**备份方案写在纸上但未落地，等于没有**。处置：F001 契约修订（FR-001/AC-001 改「交易所重建 + 回填完整性校验」，T001/T004/T005 重写，migration-plan §八 附录）；T015 提前至数据重建完成即落地；旧仓副本（HEAD `d94f94f`）只读保留。教训：①格式化/重装类高危操作前，必须对「不可重购资产」做显式清单并逐一验证备份可恢复，而不是只备份"配置文件"；②基础设施类任务（备份）是其余一切任务的前置，不得排在迁移收尾；③「两台机器分工」的拓扑认知必须落成实证记录——本次 F001 文档把数据源钉在另一台机器上，而宿主机重装时无人意识到数据就在本机；④**`git add -A` 是大文件事故的高频入口**（2026-09-11 补记，同事故响应中的未遂二次事故）：重建期间的 `git add -A` 把 400MB+ Kronos 权重与 153MB NAS dump 提交进历史——.gitignore 是事后补的，**对已跟踪文件无效**，后续 `git rm --cached` 又漏掉了 `deployment/backups/`；结果 push pack 膨胀到 500MB+，传输 25 分钟反复被短超时杀掉，表象是「push 卡死」，第一判断「网络阻塞」实为误诊（lfs 钩子探测不可达的 lfs.github.com 报错进一步误导）。修复：filter-repo 重写未推送历史清除大对象、过期 reflog、清 406MB `.git/lfs` 缓存、移除无效 pre-push 钩子，`.git` 从 555MB 回到 736KB 后秒级推送。防线：大对象目录（`deployment/backups/`、`vendor/Kronos/`、`models/`）已全部 gitignore 且入过门禁测试的契约由 `check_secrets`/结构门禁兜底；处置红线——**push 卡死先查 `git count-objects -vH` 与 pack 大小，确认传输体量后再谈网络**；`git add -A` 之前必须先 `git status` 目视新增文件清单。

17. **gate-without-teeth / gate-measures-itself 是循环 6 的主症**（C001/C002/C003/C103/C204）：AC-005 的"26 项检查全绿"里 16 项只把 psql 结果打印出来、4 个聚合抽样算出 checked/matching 却从不比较；AC-001 的期望行数由被测数据自身的 min/max 推导，截断的回填恒 PASS；AC-001 明写的衍生品子句零实现。"跑绿了"与"有判据"是两回事——代码检视的第一问应该是"这条 AC 有没有一条会变红的仓内断言"，而不是"测试过了吗"。
18. **fix-regression 占比 26/49（53%）**（循环 6）：修复引入的问题比原始编码带来的还多。三次典型：C010 把"写假 0"改成"写不进去"（NULL 撞 NOT NULL 约束）、C012 凭据改 fail-closed 但没同步迁移 `.env`（门禁 401）、C302 反转配置优先级时顺带把 AC-001 的判据边界也交给了 `.env`（C401 回潮）。教训：fail-closed 改造必须同时迁移配置与数据；优先级/默认值这类横切改动要先按语义分类（运行量 vs 判据量）再动，不能一刀切。
19. **test-simulates-itself：字符串 grep 冒充回归测试**（Q101/C109，循环 6）：第 2 轮新增的 13 个"回归测试"几乎都是 `assert "xxx" in script`，能挡住有人把那行删掉，但挡不住行为错误——C101（compose 少一段 ports）、C105（与 DDL 约束冲突）、C110（shell 变量作用域）三条全部从这类测试的盲区漏出。第 3 轮改成真实执行（`bash -n`、stub ssh 真跑 `nas_append_chunk` 并 cmp 字节、pwsh 真跑 `Invoke-DbCheck` 断言抛错）后立刻见效。可执行对象必须有可执行的测试。
20. **attribution-drift：把仓内缺陷归因为外部环境**（P201/C304，循环 6 连续两轮）：第 3 轮声明"集成失败均为外部服务可用性"，实测根因是 `.env` 里 31 字符的 JWT 撞 freqtrade 的 minLength 32；第 4 轮声明"API 仍因上游代理 502"，实测 `/api/v1/ping` 返回 200。归因必须附当轮实跑的日志证据，否则等于把 bug 挂到一个不受控的对象上、下一轮还得重查。第 4 轮最终定位到真实根因（NAS mihomo 的 HK 组用 Google 204 做泛化探针，探针通≠Binance 通）才闭合。
21. **收敛判据不是"发现数归零"**（循环 6 五轮）：High 曲线 4→3→1→0→0、每轮新增 fix-regression 8→7→4→3，两条线同时下降才是停止信号。第 5 轮仍能挑出 1 medium + 2 low，但都属"配置与文档约束"类、不影响数据/门禁/实盘路径——继续开轮次只是重复采样。反过来，前四轮每轮都抓到真实的 fix-regression，所以突破 skill 默认的"第 3 轮封顶"是有依据的，不是无限续轮。

## 裁决分布与建议命中率

- 裁决：accepted 56/56（29 + 循环 3 的 8 + 循环 4 的 9 + 循环 5 的 10，含 N1/D032/R2-01/R3-01/D048），rejected 0，partial 0；建议命中率 ≈100%。循环 4 round-2 与循环 5 round-2 的过早/false 闭环声明均已由重开复核纠正，沉淀为模式教训 #10。
- 协议偏差 3 项，裁决均接受并记录：① "一 finding 一 commit"改为按域分批 7 提交（循环 1；并行修复+同文件承载多条 finding，理由成立；bisect 粒度从 finding 级降为域级，后续修复轮应回到细粒度）；② 修复方在 7969a97 中翻 CURRENT 状态（协议规定检视人独占）——round-2 独立核对逐条证实翻状态与实际修复一致，予以追认；后续轮次状态翻权应仍由检视人执行（循环 3/4 已回归此惯例）；③ 循环 4 的 D034+D037 合并为一 commit（共用 tasks.md 编号编辑面，拆分将人为制造中间态错序，判据与记录见模式教训 13）。
- origin 分布：循环 1–4 主体为原始设计/编码，已记录 fix-regression 包括 N1、D032 与 R3-01；循环 5 新增 3 条原始编写、3 条规格漂移、3 条流程缺口、1 条 fix-regression，复核另抓到 2 处当轮 fix-regression 并在闭环前清零。
- 存活轮数：循环 1/2 的 29 条全部首轮关闭；循环 3 的 D025–D031 存活 1 轮，D032 当轮关闭；循环 4 的 D033–D038 首轮关闭，R2-01/R3-01/R3-02 均在发现或重开轮关闭；循环 5 的 D039–D043 经 2 轮后关闭，D044–D047 经 1 轮关闭，D048 当轮关闭。最长存活 2 轮，无滞留项。
- CI 终局门禁：循环 1/2 时无 git remote，客观不可执行（如实记录）；remote 配置后循环 3/4 闭环提交均已观测为绿。循环 5 终基线 d2bb055 对应 GitHub Actions run 34133866296（2026-09-07T14:36Z）**success**，于 2026-09-08 正式确认闭环。

### 循环 6 裁决分布

- 裁决：accepted 47/49（全部 fixed），partial 6（C004/C012/Q003/Q005/Q007 于 round 2、C104 于 round 3——每条都按协议写明接纳部分与剩余载体，剩余部分分别由 C101/C102/C107/C109/C110/C202 承接并在后续轮关闭），rejected 0；建议命中率 ≈92%——`suggested_fix` 与实际 `fix_summary` 实质一致，两处修复方给出了比建议更好的方案并如实记录：C104 的建议是"下架对记入报告而非 raise"，实际做成了与 listing_start 同形态的显式 `BACKFILL_SYMBOL_DELISTING_ENDS` 配置；C304 的建议只是"下结论前先跑同款命令"，实际追到了 mihomo 健康探针的根因并修掉。全接纳但命中率不满分，说明检视没有凑数、修复方也没有照单全收。
- origin 分布：原始编码 22 条、fix-regression 26 条（53%）、契约漂移 4 条、流程缺陷 4 条（含 1 条"上游任务未执行"型的 AC-002 缺口）。fix-regression 过半是本循环最强的过程信号，已沉淀为模式教训 18。
- 存活轮数：`resolved_round - first_seen_round` 全部 ≤1 轮，最长的是四条 partial 链（C004/C012 首现 1 轮、经 2 轮 partial、3 轮关闭，存活 2 轮）。无滞留项。
- 协议偏差 1 项：第 5 轮后按 skill §7 升级协议(b) 角色合并——C101/C102→C201 在"编排层真实拉起"这条链上连续两轮未收敛，且 owner 明确授权，检视人带完整上下文亲自修复 C401（提交 8d6b775），修完切换视角重新核对并对两道新门禁各做一次变异验证。
- CI 终局门禁：见下方闭环记录。

## 残余观察项与闭环处置

- N2：ADR-0003 第 6 行机器路径已改为仓库名引用（见本轮清理提交）。
- FIX-log 计数笔误：FIX-log 已按闭环协议删除（local-only 过程稿，内容已沉淀于本文件与 CURRENT 终态）；勘误记录留存：test_check_dep_pins 实为 9 tests。
- 终局复核补记（2026-09-07 12:55，检视人独立审计，非新开轮次）：① CURRENT-code.md §5 已同步「首推补验」兑现记录（原文停留在"无 remote 不可执行"时点，与本文件闭环状态不一致）；② 闭环提交 0242075 自身触发的 CI run 因本机 gh token 失效 + 匿名 API 限流/断连未及观测——该提交仅触及 docs/reviews/ 两个过程文档，本地同款门禁全绿（检视人复验），ci.yml 与两次绿 run（34081647116/34081864805）之间无差异，风险≈0；已补看（2026-09-07 12:59）：34084533920（@0242075）与 34085129903（@cb0720e）均 success，残余项消解。审计另抽验 D025-D032 八条修复实物（PRD G6/§2.4/FR2.1/FR4.6/FR6.3、架构 §4.2、ADR-0001/0003/0004 补强节）均在位且交叉自洽。
- 终态清理（2026-09-07 12:59，检视人执行）：三循环全部闭环、CI 全绿后，按闭环协议删除 docs/reviews/CURRENT-doc.md 与 CURRENT-code.md——过程稿生命周期终点，完整 issue 表与模式教训已沉淀于本文件；本仓惯例（CLAUDE.md/.gitignore 例外）下它们随循环进行而入库、随闭环而删除。
- 循环 5 终态清理（2026-09-08）：D039–D048 完整证据、模式教训和 CI 终局结果已迁入本文件；按协议删除 local-only `docs/reviews/CURRENT-doc.md` 与 `docs/reviews/FIX-log.md`，未留任何开放 finding。
- 循环 6 终态处置（2026-09-12）：C001–C014/Q001–Q009/C101–C111/Q101/C201–C206/P201/C301–C304/C401 共 46 条全部 fixed 并各配仓内回归测试；三条未修项**不因闭环而消失**，明确移交：C402（initdb 路径不写版本账本）、C403（迁移 runner 单事务执行约束）转 F002 数据桥阶段随迁移体系一并处理；AC-002 证据缺口已由 owner 于 2026-09-12 裁决并落地（见下条）。
- AC-002 缺口裁决与落地（2026-09-12，owner 决策后由检视人实施）：采纳「编排内降级证据 + 真实推理独立命令」。F001 spec §6 增「验收修订」条目（不静默改写原文），AC-002 改为编排内契约（source 与 model_enabled 双向 fail-closed，声称 real 却回 placeholder 判红），新增 AC-006 承载真实推理证据（复跑命令与前置条件写进 spec §6/§7）；design §8 同步两行。编号用 AC-006 而非 AC-002a/b——`validate_spec_lifecycle.py` 的 `AC_RE` 只接受纯数字编号，字母后缀会被**静默忽略**而不是报错，这类看不见的失效本身值得记住（另发现该校验器把 AC 行内所有反引号内容都当作 tests 路径，描述里的 /health、source 等不能加反引号）。容器化真实推理（compose 可选 profile `kronos-real`）落 F002 T014，锚到 FR-001——F002 T007 要把 signals_log 导出进湖，薄壳为 mock 时导出的全是 placeholder 行、对因子研究无价值，这是真实的 F002 利害关系而非硬塞。结果：`ALPHAMILL_INTEGRATION=1` 从长期 1 failed 变为 7 passed 1 skipped，skip 项带可执行命令而非沉默跳过；两道新断言各做一次变异验证（假实例声称 real 却回 placeholder → AC-002 红；KRONOS_REQUIRE_REAL_MODEL=1 指向 mock → AC-006 红）。
- 收尾轮（2026-09-12，owner 要求「跑一下真实推理并处理掉那两个问题」）：① **AC-006 真实推理实跑通过**——既有 :8002 实例 3 passed（BTC/USDT，source=kronos，Kronos-base，256 行上下文，CPU 单次 7.2s）；另按 spec 文档命令从零起 :8003 复现，同样 3 passed（ETH/USDT，CPU 单次 3.4s）。② 实跑过程中发现 **C501**——我上一轮写进 spec 的那条 AC-006 命令**自己没跑过**，缺 DB 环境导致 /health 500；这是「文档化的命令从未被执行」的典型，已修并配契约测试。③ C402/C403 一并关闭，不再转 F002。三道新门禁各做一次变异验证。
- 模式教训补记 #22 **documented-command-never-run**：把一条命令写进规格并不等于验证过它。C501 的根因是我在拆分 AC-002 时凭既有实例的行为推断命令形态，而那个实例带着 DB_HOST 覆盖启动。**凡是写进验收文档的命令，必须在干净环境里从零跑一遍**——这一轮的证据正是：同一条命令，在既有实例上"验证通过"，从零执行却直接 500。

## 循环 7：F002 数据桥需求设计检视

- report_type: doc-review | round: 1（full-scan）→ 2（修复覆盖 >30%，一次性 full-scan）→ 3（diff-only 封顶与 owner 角色合并）| 状态: 闭环
- 日期：2026-09-12 → 2026-09-13 | 基线：`6491224` → 终态工作树基于 `a99a1c9`
- 范围：F002 需求设计三件套起步；owner 后续明确收窄为 `docs/features/0.2/F002-data-bridge/design.md`，spec/tasks/integration/F004 与 ADR-0005 工作区改动不纳入最终裁决。
- 结论：设计范围内 Critical/High/Medium/Low 全部清零；本地 `tools/verify.py` 101 passed、8 个环境依赖项 skipped、ruff 全绿；最终 CI 由闭环提交触发并由 reviewer 观测。
- 终态门禁（2026-09-13）：GitHub Billing 阻塞解除（仓库转 public，Actions 免费额度生效）。rerun 原失败 run `34737667094`（@ `aa0ebbe`）双 job 全绿（py3.11 29s / py3.13 37s）；另 run `34738191708`（@ `2d9c556`）亦双绿。全绿后按闭环协议删除 local-only `CURRENT-doc.md` 与 `FIX-log.md`。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F002-D001 | data_version 无物理隔离会覆盖旧快照 | Critical | 正确性 | 根因 | 原始设计 | fixed | 版本化寻址或完整文件集 | `.rN` 不覆盖 + manifest 累计完整清单 | AC-007（计划）+ 文档门禁 | 1 | 3 | immutable-version-without-versioned-storage |
| F002-D002 | manifest 未绑定文件身份与摘要 | High | 正确性 | 根因 | 原始设计 | fixed | 记录路径/行数/边界/字节/sha256 | reader 只按清单读取并逐项验完整性 | AC-008（计划）+ 文档门禁 | 1 | 3 | manifest-without-artifact-identity |
| F002-D003 | 对账真相源与弱降级契约漂移 | High | 正确性 | 根因 | 规格漂移 | carried-forward | 删除弱摘要与降级 | design 已冻结 canonical row_digest；tasks 最终核对按 owner 范围排除 | — | 1 | — | cross-doc-contract-drift |
| F002-D004 | 时间截断不能替代一致性快照 | High | 正确性 | 根因 | 原始设计 | fixed | 同一 REPEATABLE READ 事务 | 导出与源摘要共享快照并记录 xmin | AC-010（计划）+ 文档门禁 | 1 | 2 | cutoff-without-snapshot-isolation |
| F002-D005 | 质量旗只有总数且无裁决行为 | High | 正确性 | 根因 | 原始设计 | fixed | 分区级旗标并 fail-closed | 默认拒绝，显式 allow_flagged 才放行 | 文档门禁 | 1 | 2 | quality-signal-without-gate-policy |
| F002-D006 | signals_log 事件时间含糊导致前视 | High | 正确性 | 根因 | 原始设计 | fixed | 区分事件与可得时间 | latest_candle/time 双轴 + 标签按 evaluated_at 掩码 | AC-009（计划）+ 文档门禁 | 1 | 3 | ambiguous-event-time |
| F002-D007 | 异构 dataset 无受控 registry | Medium | 正确性 | 根因 | 原始设计 | fixed | 枚举投影/类型/键/过滤列 | 五个 dataset 契约完整登记 | AC-012（计划）+ 文档门禁 | 1 | 3 | generic-api-without-schema-registry |
| F002-D008 | 调度时间跨文档不一致 | Medium | 正确性 | 症状 | 规格漂移 | fixed | owner 统一时点 | design 固定每日 02:00、周日 04:00 | 文档门禁 | 1 | 2 | cross-doc-contract-drift |
| F002-D009 | 非零退出与不重试策略冲突 | Medium | 正确性 | 根因 | 原始设计 | fixed | 分层退出码 | 0/1/2 + RestartPreventExitStatus=2 | 文档门禁 | 1 | 2 | retry-policy-exit-code-conflict |
| F002-D010 | symbol_map 键与格式有损 | Medium | 正确性 | 根因 | 规格漂移 | partial | 冻结三元键与五列映射 | design 已修；跨文档核对按 owner 最终范围排除 | design §4 | 1 | — | lossy-symbol-canonicalization |
| F002-Q001 | Kronos 容器化无正式需求载体 | Medium | 质量 | 根因 | 流程缺口 | fixed | 建独立 Feature 并裁决阻塞关系 | F004 已建立，owner 于 `4883061` 裁决不阻塞 F002 | 生命周期门禁 | 1 | 3 | task-outside-feature-contract |
| F002-Q002 | T009 捆绑四类动作 | Low | 质量 | 症状 | 流程缺口 | fixed | 拆为单一可验证任务 | 拆为 T009/T017/T018/T019 | 文档门禁 | 1 | 2 | bundled-task-breaks-bisectability |
| F002-R2-01 | as-of 把未来生成信号倒灌历史 | Critical | 正确性 | 根因 | 修复引入 | fixed | event_time 与 available_at 同时约束 | 双时间轴 + 标签可用性掩码 | AC-009（计划） | 2 | 3 | bitemporal-availability-loss |
| F002-R2-02 | 目录余项判错与共享 `.rN` 冲突 | High | 正确性 | 根因 | 修复引入 | fixed | reader 不扫描目录 | 输入路径仅取 manifest partitions | AC-008（计划） | 2 | 3 | integrity-check-conflicts-with-version-sharing |
| F002-R2-03 | 增量 manifest 未形成完整快照 | High | 正确性 | 根因 | 原始设计 | fixed | 继承、替换、重算、原子发布 | 累计清单 + manifest-only 游标 + 附属状态来源 | AC-011/AC-014（计划） | 2 | 3 | incremental-manifest-without-cumulative-state |
| F002-R2-04 | row_digest 输入与顺序不 canonical | High | 正确性 | 根因 | 修复引入 | fixed | 完整投影、无损编码和稳定排序 | IEEE 位模式、规范 JSON、全行字节排序 | AC-012（计划） | 2 | 3 | canonical-digest-without-canonical-schema |
| F002-R2-Q01 | 新方案未对称传播到旧恢复文字 | Low | 质量 | 症状 | 修复引入 | partial | 清理覆盖/全集读取等旧句 | design 残余由 R3-04 关闭；tasks 最终核对按范围排除 | design diff + 门禁 | 2 | — | partial-symmetric-fix |
| F002-R3-01 | as-of 未进入 API 且 OHLCV 默认放行 | High | 正确性 | 根因 | 修复引入 | fixed | 接口承载 fidelity 并默认拒绝退化 | read/ReadResult/异常/manifest 已同步 | AC-013（计划）+ 门禁 | 3 | 3 | safety-contract-not-enforced-by-interface |
| F002-R3-02 | 物理文件推进游标会永久漏日 | High | 正确性 | 根因 | 修复引入 | fixed | 游标只认上一 valid manifest | manifest-only 游标与孤儿重跑已冻结 | AC-014（计划）+ 门禁 | 3 | 3 | cursor-derived-from-unpublished-state |
| F002-R3-03 | 累计附属状态不能从清单反推 | High | 正确性 | 根因 | 修复引入 | fixed | skipped 继承/替换，null 独立计数 | 两类状态来源已拆开定义 | AC-011/AC-014（计划）+ 门禁 | 3 | 3 | cumulative-metadata-without-reconstructible-state |
| F002-R3-04 | invalid 引用文件留存与回收冲突 | Medium | 正确性 | 症状 | 修复引入 | fixed | owner 冻结完整保留或 tombstone | 审计优先：invalid manifest 与引用 `.rN` 一并保留 | AC-014（计划）+ 门禁 | 3 | 3 | partial-symmetric-fix |

### 循环 7 模式教训

1. `partial-symmetric-fix` 连续跨轮出现：新增不变量后必须扫描其全部正向断言，而不只搜索已废弃关键词。R3-04 最终用“引用状态三分法”替代继续补句子。
2. origin 分布：原始设计 8、修复引入 8、规格漂移 3、流程缺口 2；修复引入占 38%，说明 diff-only 复核是本循环的主要价值来源。
3. 裁决分布：fixed 18、partial 2、carried-forward 1、rejected 0；建议命中率约 95%。partial/carried-forward 均因 owner 将最终范围收窄为 design，不冒充跨文档核对完成。
4. 最长存活问题为 D001/D002/D006/D007 与 R2-03，均跨至 Round 3 才关闭；R3-01～04 在发现轮关闭。R3-04 连续补丁未收敛后按协议升级角色合并，owner 授权 reviewer 直接冻结不变量。

---

## 循环 8：ADR-0005 呈现与观测架构检视

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only 复核）→ 3（diff-only 封顶）→ 4（CI 红重开，检视方自伤）| 状态: 闭环
- 日期：2026-09-13 | 基线：`2d9c556` → `e129fb7` → `2e64750` → 终态 `3f9cded`+
- 范围：ADR-0005 全文 + 配套改动（PRD FR8/S8/里程碑、架构 §三/§4.2/§五/§七、ADR-0002、docs/README、CLAUDE.md、BACKLOG、TEMPLATE design、docs/design/ui-mockup 静态原型）
- 结论：Critical/High/Medium/Low 全部清零；决策本身成立（三分边界、口径进视图、备选方案 B 零沉没成本、裁决不页面化红线），问题集中于**约束传播不完整**——ADR 提出的 4 个新资产位置/契约（`db/migrations/`、评测台曲线序列、前端构建期依赖、静态原型）首轮全部未落到真相源或门禁上。
- 终态门禁（2026-09-13）：`python3 tools/verify.py`（本机经 `.venv` 解释器实跑）exit 0（109 passed / 1 skipped，ruff 全绿）；D009 门禁经检视方独立变异验证（撤 `## ` 截断 → 测试变红，恢复 → 10 passed）。首次闭环提交 `3f9cded` 的 CI（run `34748297701`）双 job 红——检视方回写复盘时用了非规范的门禁命令写法，触发 D046 命令契约门（见 ADR5-R4-01）；修正后重推，CI 绿方闭环。闭环后按检视结论修复门禁自身缺陷 ADR5-R4-02，三道变异验证：旧豁免写法→新测试红、豁免目录塞裸命令→保持绿、非豁免文件塞裸命令→红。
- 遗留说明：闭环时工作树存在另一会话的未提交改动（ADR-0006 草稿 + PRD FR3/FR5/FR6/FR7 扩写 + 未跟踪 `uv.lock`），不属本循环文件集合，未纳入本循环提交与裁决；已核实其未回滚本循环 D005 对 M2/M4 出口标准的修复。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ADR5-D001 | `db/migrations/` 未登记进架构目录树，却被 ADR 提为「口径唯一居所」 | High | 正确性 | 根因 | 契约漂移 | fixed | 架构 §三 树补 `db/` | §三 在 monitoring/ 与 web/ 之间登记 db/，注明 init.sql + migrations/ 与账本 tools/apply_migrations.py | 文档门禁（check_doc_links） | 1 | 2 | cross-doc-contract-drift |
| ADR5-D002 | 静态原型覆盖三面，与决策 4「实时 PnL 不进控制台」矛盾且 ADR 未声明其地位 | High | 正确性 | 根因 | 契约漂移 | fixed | ADR 加小节声明蓝图地位 + 页内标注归属 | ADR 新增决策 7（终局四面全景蓝图、非契约、不参与验收、F005 只做研究面）+ index.html 范围横幅 | 文档门禁 + 检视方实物核实 ph 标记既有 | 1 | 2 | prototype-scope-creep |
| ADR5-D003 | 「前端构建期依赖按 ADR-0002 纪律 pin」是空头引用——ADR-0002 无 Node 条目，门禁不覆盖 | High | 正确性 | 根因 | 契约漂移 | fixed | 扩 ADR-0002 + 后续行动扩 check_dep_pins | ADR-0002 新增「前端构建期工具链（Node/npm）」原样依赖行（lockfile 入库、pin 主版本、里程碑边界升级）+ ADR-0005 后续行动 ④ | 文档门禁（门禁扩展本身见 R2-04） | 1 | 2 | gate-without-teeth |
| ADR5-D004 | 评测台曲线级时间序列契约未落进接口真相源 §4.2 | Medium | 正确性 | 根因 | 契约漂移 | fixed | §4.2 加 curves 侧车约定 | §4.2 新增侧车：路径 + manifest 键 `curves{path,rows,columns,sha256}` + 最小列集 + 时间轴口径 | 文档门禁 | 1 | 2 | cross-doc-contract-drift |
| ADR5-D005 | PRD 里程碑表 M2/M4 范围列加了 FR8.1/FR8.3，出口标准列未同步 | Medium | 正确性 | 根因 | 契约漂移 | fixed | M2/M4 出口各补一条可验收断言 | M2 补「控制台与 report.json/curves.parquet 对数一致」；M4 补「经统一 API 完成并落 FR7.4 审计」 | 文档门禁 | 1 | 2 | scope-without-exit-criteria |
| ADR5-D006 | `docs/design/` 新目录无所有权归属与入库处置声明 | Low | 质量 | 根因 | 原始设计 | fixed | 文档地图 + CLAUDE.md 各补一行 | docs/README 所有权矩阵新增「呈现层视觉原型（非契约，设计资产）」行；CLAUDE.md 结构清单同步 | 文档门禁 | 1 | 2 | unowned-artifact |
| ADR5-D007 | F005/F006/F007 编号与执行时序倒置，BACKLOG 按里程碑排列时易误读 | Low | 质量 | 根因 | 原始设计 | fixed | 注明编号与执行顺序无关 | BACKLOG 规划节补「编号按分配时刻递增，与执行顺序无关（F007 先于 F005）」 | 文档门禁 | 1 | 2 | — |
| ADR5-D008 | 决策 4 把「(M3+) 组合与台账只读视图」写进窗口为「M2 前」的 F005 | Low | 质量 | 根因 | 原始设计 | fixed | 拆为后续增量或独立条目 | 划为 F005.1；R3 进一步拆为「台账 F005.1 / 组合随 M3 规划」 | 文档门禁 | 1 | 2 | scope-without-exit-criteria |
| ADR5-D009 | BACKLOG 新增规划表对 `check_backlog` 正则脆弱，首列若写成 Fxxx- 即误报 | Low | 质量 | 症状 | 原始设计 | fixed | 门禁加 section 感知 | `check_backlog` 在首个 `## ` 处 break，只解析活跃索引表；fail-closed（活跃表上方若插 `## ` 则报「缺少非 done Feature」） | tests/unit/test_validate_spec_lifecycle.py::test_backlog_planning_section_not_parsed_by_gate（检视方独立变异验证通过） | 1 | 2 | gate-without-teeth |
| ADR5-D010 | CLAUDE.md `docs/decisions/` 条目重复两次 | Low | 质量 | 根因 | 原始设计 | fixed | 删重复条目 | 删除「当前结构」中无编号的重复行，保留带 0001~0005 编号版本 | 文档门禁 | 1 | 2 | — |
| ADR5-R2-01 | D004 修复把曲线侧车路径写成 `results/`，与仓内既有报告根 `reports/` 冲突 | Medium | 正确性 | 根因 | 修复引入 | fixed | 对齐 §三 报告根 | 改为 `reports/bench/<object_id>/<data_version>/curves.parquet` 并注明报告根见 §三 | 文档门禁 + 检视方核实 `results/` 全仓无定义 | 2 | 2 | cross-doc-contract-drift |
| ADR5-R2-02 | 「谱系」归属三处不一致：ADR 决策 4 说属 F005，原型横幅列举 F005 范围时漏掉它，原型 nav 把「谱系与台账」整页标 M3+ | Medium | 正确性 | 根因 | 修复引入 | fixed | 谱系留 F005 则横幅补列 + 原型拆两个 ph；否则 ADR 一并移入 F005.1 | 取建议 (a)：ADR 决策 4 显式「谱系归 F005 / 台账 F005.1 / 组合随 M3 规划」；横幅、nav、view-head、两个面板 h3、BACKLOG 五处同步 | 文档门禁 | 2 | 3 | partial-symmetric-fix |
| ADR5-R2-03 | 曲线侧车最小列集中 `ic_decay`/`quantile_returns` 与 report.json 标量同名重复，且与「时间轴为逐日/逐 bar UTC 时间戳」的行轴口径矛盾 | Medium | 正确性 | 根因 | 修复引入 | fixed | 列名改时间展开式并写明与标量可互推 | 列集改 `q1_cum`..`q5_cum` / `long_short_cum` / `rolling_ic_h1..h24`，并补「标量是全样本汇总、侧车是其时间展开，两者口径必须可互推」 | 文档门禁 | 2 | 3 | cross-doc-contract-drift |
| ADR5-R2-04 | ADR-0005 后续行动 ④（扩 check_dep_pins 覆盖 package-lock）无验收判据，属未执行任务 | Low | 测试覆盖 | 根因 | 流程缺陷 | fixed | 补 AC 并指定转入 tasks.md 的时点 | 后续行动 ④ 补「验收判据：对 package-lock.json 做一次变异验证（改一个依赖版本号使门禁变红），F005 立 spec 时转入其 tasks.md」 | 载体为 F005 tasks（未立项，非本轮可跑） | 2 | 3 | gate-without-teeth |
| ADR5-R4-01 | 检视方回写复盘时把门禁命令写成解释器全路径形式，与 D046 确立的「全仓统一 `python3 tools/verify.py`」规范不符，触发命令契约门使闭环提交 CI 双红 | Medium | 正确性 | 根因 | 修复引入 | fixed | 改用 D046 规范写法，解释器信息降为括注 | 改为「`python3 tools/verify.py`（本机经 `.venv` 解释器实跑）」；复跑 test_doc_gate_command 2 passed 后重推 | tests/unit/test_doc_gate_command.py::test_no_bare_python_gate_command_in_tracked_sources | 4 | 4 | documented-command-not-runnable |
| ADR5-R4-02 | R4-01 暴露出门禁自身缺陷：命令契约门的豁免集合用 `part in {"docs/reviews", ...}` 对 `Path.parts` 做成员判断，多段前缀永不命中，`docs/reviews` 实际从未被豁免（`conversations` 恰为单段路径而生效，长期掩盖该缺陷） | Medium | 正确性 | 根因 | 原始设计 | fixed | 改为按 posix 目录前缀匹配，并补一条锁住豁免生效的回归测试 | `_SCAN_EXEMPT_DIRS` 改带尾斜杠元组 + `as_posix().startswith()`；抽出 `_TEXT_SUFFIXES`/`_tracked_files()`；新测试先断言豁免目录有 tracked 样本（18 个）再断言未泄漏，避免空集恒真 | tests/unit/test_doc_gate_command.py::test_exempt_dirs_are_actually_skipped | 4 | 4 | gate-without-teeth |

### 循环 8 模式教训

1. **本循环的支配模式是 `cross-doc-contract-drift`（4 条，含 2 条修复引入）**：ADR 是"提出新契约"的文档，但契约真正生效的位置在架构 §三目录树、§4.2 接口契约、ADR-0002 依赖表和 `tools/` 门禁里。ADR 自己写下"先于 F005 开发锁定"并不构成锁定——**写进 ADR 的约束传播条款，必须在同一次提交内落到被传播的那份文档上**，否则它只是一条待办。
2. **`origin` 分布：原始设计 5、契约漂移 5、修复引入 3、流程缺陷 1。** 修复引入占 21%（3/14），全部由 diff-only 复核抓出，且 R2-01 是修复方自审发现——第 2/3 轮的价值再次被验证：R2-02/R2-03 在第 1 轮物理上不存在。
3. **`partial-symmetric-fix` 再次出现（R2-02）**，与循环 7 同模式：D008 拆分"组合与台账"时只拆了台账，"谱系"被并列结构误带走，三处表述各说各话。教训同循环 7——**拆分一个并列短语时，必须枚举该短语在全仓的每一处出现并逐个裁定归属**，而不是只改提出问题的那一处。
4. **`gate-without-teeth`（3 条）**：D003 引用了不存在的 ADR-0002 条款、D009 的门禁对新表格形状脆弱、R2-04 的后续行动无 AC。三者共同指向同一判据——**声称"有纪律约束"时，先问"哪个脚本会因为违反它而变红"**；答不出来的就是待办，应按未执行任务建 AC，而不是当成已完成的约束。
5. **最长存活：D001~D010 均跨 2 轮关闭，R2-02/R2-03 跨至第 3 轮**；无条目超过封顶轮。
6. **检视方独立核对抓到的实质点**：D002 的修复声明称"各页 ph 标记给出归属"——实物 grep 证实为改前既有而非事后编造（声明为真）；D009 的门禁做了变异验证（撤 break → 红）。两次核对都通过，说明本循环修复方声明可信度高，但核对本身不可省略：循环 7 的历史教训正是"纯文字转述连续 4 轮为假"。

### 循环 8 裁决分布与建议命中率

- fixed 14 / partial 0 / rejected 0 / carried-forward 0 / tracked 0（14 条全部接纳并关闭）。
- 建议命中率约 93%（13/14 实质采纳检视方 `suggested_fix`）；唯一分歧为 R2-02——检视方给出 (a)/(b) 二选一，修复方取 (a) 并在执行中进一步拆出「组合只读视图随 M3 规划」，比原建议更细。
- 全接纳率 100% 需警惕"检视在凑数"的反向信号；本循环的对冲证据是：3 条为修复引入（非首轮凑数可得）、1 条（D003）在修复后仍被降级为待办（R2-04），说明发现具备实质性而非形式化。
- 协议偏差 1 项（已追认）：R2-02 占两笔 commit（`9509933` + `2e64750`），修复方主动声明，两笔均限于 R2-02 文件集合，不影响 bisect 定位。

---

## 循环 9：ADR-0007 后 F002 三件套追踪补齐

- report_type: doc-review | round: 1（定向核对）→ 2（diff-only 复核）| 状态: 闭环
- 日期：2026-09-13 | 基线：`0405865` → `ba3cc8e`
- 范围：`docs/features/0.2/F002-data-bridge/{spec,design,tasks}.md`；只补 ADR 来源、验收映射与任务追踪，不改变 F002 产品范围。
- 结论：三项 Medium 全部修复，Critical/High/Low 为 0；spec/design/tasks 的 AC 集合均为 AC-001..015；本地 `python3 tools/verify.py`（经项目 `.venv` 解释器实跑）103 passed / 8 skipped；源文档提交 `ba3cc8e` 的 CI run `34763002847` 双 job 全绿（py3.11 / py3.13）。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F002-RS-01 | ADR-0007 已生效但 spec 仍声明无新 ADR | Medium | 正确性 | 根因 | 规格漂移 | fixed | spec 来源区显式引用 ADR-0007 | spec 引用 ADR-0007 并保留导出细节权威边界 | 文档链接/生命周期门禁 + ADR 关键词定向检查 | 1 | 2 | cross-doc-contract-drift |
| F002-RS-02 | design 验收映射未同步新增摘要与映射契约 | Medium | 测试覆盖 | 根因 | 规格漂移 | fixed | 补 AC-015 并更新 AC-003/AC-004 关键断言 | 补 ADR 输入约束、AC-015，并扩写 AC-001/003/004 | AC 集合差异检查 + 文档门禁 | 1 | 2 | cross-doc-contract-drift |
| F002-RS-03 | tasks 缺 AC-007/011/012 显式追踪且前置条件仍称 DQ-003 待确认 | Medium | 测试覆盖 | 根因 | 规格漂移 | fixed | 对应任务补 AC 引用并更新 DQ-003 状态 | T016/T002/T008 补 AC 引用；DQ-003 改为已裁决 | AC 集合差异检查 + 文档门禁 | 1 | 2 | cross-doc-contract-drift |

### 循环 9 模式教训

1. 三项均为 `cross-doc-contract-drift`：新增 ADR/AC 时应在同一批次检查来源区、design 验收映射和 tasks 显式 ID 三个落点。
2. origin 分布为规格漂移 3；三项均跨一轮修复，第二轮 diff-only 未产生新问题。
3. 裁决分布：fixed 3、partial/rejected/tracked 0；建议命中率 100%，修复严格限定为追踪补齐，没有借机扩大 F002 范围。

---

## 循环 10：F002 数据桥实现代码检视

- report_type: code-review（round 1）→ fix-verification（round 2、3）| 状态: 闭环
- 日期：2026-09-14 | 基线：`569359b` →（re-baseline）`ad09ff4` → 第 3 轮修复序列
- 范围：`src/alphamill/data_bridge/` 全部 F002 新增模块 + `tests/{unit,integration}/test_f002_*` +
  三件套与调度/备份脚本；不含 F001 采集器（collector/）与历史评测脚本。
- 结论：27 条发现中 25 条 fixed、1 条 partial（R2-01，带可核对理由）、1 条 tracked（R2-06 → `tasks.md` T021）。
  Critical 0 / High 0 收口。本地 `python3 tools/verify.py` 全绿（`192 passed, 25 skipped`）；
  F002 真实数据库用例因当前用户无 docker socket 权限全部 skip，该缺口由 T021 承接，未以 skip 充作证据。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F002-C001 | signals_log 的 skipped 把有数据的日期也登记进去（`dim_of` 恒返三元组，查表却用空元组） | high | 正确性 | 根因 | 原始编码 | fixed | 非 pair 分支改用 `dim_of({})` 查表并补回归测试 | 两处查表键改为 `non_pair_dim = dim_of({})` | test_f002_partitions.py::test_non_pair_empty_cells_use_data_dates_not_an_unreachable_dimension | 1 | 3 | key-shape-mismatch |
| F002-C002 | signals_log 同日多 symbol 重复写 N 个整日分区，N-1 个立即成孤儿 | medium | 正确性 | 根因 | 原始编码 | fixed | group_cols 由 spec.partition_keys 推导 | discover_cells 按 partition_keys 分组；非 pair dataset 不拼 db_symbol | test_f002_partitions.py 两条 | 1 | 2 | key-shape-mismatch |
| F002-C003 | full 模式对源端已删除分区无感知，仍继承并声明 reconcile ok | medium | 正确性 | 根因 | 原始编码 | fixed | 判 removed 写进 revision_diff；是否移出 partitions 交 owner 裁决 | full 不继承基线，版本组成=本轮源库结果（`merge_partitions`），design §3 同步 | test_f002_exporter.py + test_f002_revision.py::test_full_export_removes_source_partition_and_records_removed | 1 | 2 | inherit-without-reverify |
| F002-C004 | reader 每次读取都对全清单分区做 sha256，查一天也要 hash 整个湖 | medium | 质量 | 根因 | 原始编码 | fixed | 只校验本次 selected 分区 | validate_manifest_integrity 增 partitions 形参，reader 传 selected | test_f002_manifest.py::test_integrity_can_validate_only_reader_selected_partitions | 1 | 3 | whole-scan-on-hot-path |
| F002-C005 | 质量旗 lake_pair 反查失败静默降级为 warning，带旗分区默认拒绝随之失效 | medium | 正确性 | 根因 | 原始编码 | fixed | 抛错并补「映射缺失→导出判红」测试 | quality_flags 改抛 DataBridgeError（退出码 2） | test_f002_partitions.py::test_quality_flag_without_symbol_mapping_fails_closed | 1 | 3 | silent-safety-downgrade |
| F002-Q001 | AC-006 真实湖用例恒 skip，且唯一断言 `or True` 恒真 | medium | 测试覆盖 | 根因 | 原始编码 | fixed | 删 `or True`；改用独立环境变量 | ALPHAMILL_REAL_LAKE_DIR 开关 + 删恒真断言（后续见 R3-01） | 用例自身（本轮以构造湖实跑，含判红变异） | 1 | 3 | vacuous-assertion |
| F002-Q002 | uv.lock 缺 duckdb/pyarrow，按 lock 复现环境跑不起 F002 | medium | 质量 | 根因 | 规格漂移 | fixed | 重生成 lock 或移除该文件 | uv.lock 重新生成，含两个新增运行时依赖 | lock 内容核对 | 1 | 3 | lockfile-drift |
| F002-Q003 | row_digest 聚合层有两份实现 | low | 质量 | 根因 | 原始编码 | fixed | 委托 digest.row_digest | row_digest_of_rows 改为直接委托 | 既有 digest 用例 | 1 | 3 | duplicate-authority |
| F002-Q004 | staging 目录硬编码 "current" 与 design 不符 | low | 质量 | 根因 | 规格漂移 | fixed | 传真实 data_version 或改 design | design §3 跟随实现 | 文档一致性 | 1 | 2 | — |
| F002-Q005 | begin_snapshot_tx 依赖 psycopg2 隐式 BEGIN 的副作用 | low | 质量 | 根因 | 原始编码 | fixed | 改用 set_session | set_session + 新增 reset_snapshot_session | test_f002_reconcile.py::test_snapshot_transaction_sets_and_restores_session_defaults | 1 | 3 | fragile-by-construction |
| F002-Q006 | CLI/symbol_map 自建的 DB 连接不关闭 | low | 质量 | 根因 | 原始编码 | fixed | try/finally 关闭 | export_symbol_map 加 own_conn + try/finally | 结构性 | 1 | 2 | — |
| F002-Q007 | 测试文件底部 `_conn_kwargs_shim` 死代码 | low | 质量 | 根因 | 原始编码 | fixed | 删除 | 已删除 | — | 1 | 3 | — |
| F002-Q008 | reader docstring 的时间过滤语义自相矛盾 | low | 质量 | 根因 | 原始编码 | fixed | 改为「end 不含」 | 已改 | — | 1 | 3 | — |
| F002-Q009 | 定时导出覆写 git 跟踪的 symbol_map.csv，每晚弄脏工作树 | low | 质量 | 症状 | 规格漂移 | fixed | owner 裁决 current 副本落点 | current 副本改址 lake/_metadata/，集成 §2.2 / design §4 / tasks T005 同步 | test_f002_symbol_map.py | 1 | 3 | runtime-writes-into-source-tree |
| F002-P001 | spec §6 的验收证据在当前工作树/当前用户下全部不可复现 | high | 测试覆盖 | 根因 | 流程缺陷 | fixed | 在收口机器重跑，或写明证据所属环境 | §6 改标「历史验收证据」+ 环境归属 + 如实声明未复跑项，真实 DB 证据转 T021 | 文档如实性 | 1 | 3 | evidence-not-reproducible |
| F002-P002 | `.codegraph` 不可读软链使本工作树 pytest / verify.py 完全无法运行 | high | 测试覆盖 | 根因 | 流程缺陷 | fixed | 绕开 collection root | verify.py 限定 `--rootdir=tests --confcutdir=tests` + 显式测试目录 | 门禁自身可运行即证据 | 1 | 2 | gate-cannot-run |
| F002-R2-01 | 修复未走 FIX-log/commit 流程，多条 finding 无处置声明 | high | 测试覆盖 | 根因 | 流程缺陷 | partial(见裁决记录) | 补 FIX-log 证据三件套 + 按 finding 拆提交 | FIX-log 补齐五项；提交粒度未拆，理由经核对成立 | — | 2 | 3 | fix-without-declaration |
| F002-R2-02 | full 不继承基线后，空源库/截断窗口会发布 valid 空版本并成 latest | medium | 正确性 | 根因 | 修改引入 | fixed | 收缩阈值 fail-closed + owner 裁决归档语义 | `guard_full_shrink` 三条拒绝路径 + spec/design 同步 | test_f002_exporter.py 两条 shrink guard 用例 | 2 | 3 | fail-open-on-empty-source |
| F002-R2-03 | signals_log symbol 被当 spot 并入映射，永续 symbol 一出现即碰撞阻断全部导出 | medium | 正确性 | 根因 | 修改引入 | fixed | registry 显式标注是否参与映射 | 新增 `symbol_map_enabled`，signals_log=False | test_f002_symbol_map.py::test_signals_log_symbols_do_not_assume_spot_market_type | 2 | 3 | market-type-inference-gap |
| F002-R2-04 | 本地门禁红：F001 entrypoint 用例依赖裸 `python` 可执行名 | medium | 测试覆盖 | 根因 | 原始编码 | fixed | 改 python3 或注入 PATH 垫片 | freqtrade-entrypoint.sh 改 `python3` | test_f001_credentials.py 由红转绿 | 2 | 3 | host-dependent-test |
| F002-R2-05 | publish_manifest / symbol_map artifact 改用 os.link，隐含硬链接文件系统前提 | low | 质量 | 根因 | 修改引入 | fixed | OSError 回退 O_EXCL 或写死前提 | EXDEV/EPERM/EOPNOTSUPP 回退 O_EXCL + fsync，design 记录 | test_f002_manifest.py / test_f002_symbol_map.py 两条 fallback 用例 | 2 | 3 | hidden-platform-assumption |
| F002-R2-06 | full 模式语义变更缺真实数据库证据 | medium | 测试覆盖 | 根因 | 修改引入 | tracked(T021) | 有 DB 环境跑集成套件 + 补 removed 用例 | 集成用例已补，执行落 tasks.md T021（带 AC） | test_f002_revision.py::test_full_export_removes_source_partition_and_records_removed（待执行） | 2 | — | contract-change-untested |
| F002-R3-01 | 去掉 `or True` 后换成断言 `Path.glob` 枚举顺序，真实湖上大概率假红 | low | 测试覆盖 | 根因 | 修改引入 | fixed | 改断言版本名可解析 | 逐个 `mf.parse_data_version` 解析 + 文件名唯一性 | 同上用例（构造湖实跑：合法 passed / 非法文件名判红） | 3 | 3 | assertion-asserts-wrong-property |
| F002-R3-02 | 收缩护栏只有拒绝路径，缺「人工确认后放行」的执行通道 | low | 质量 | 根因 | 修改引入 | fixed | 加 `--allow-shrink` 显式确认并留痕 | CLI `--allow-shrink` → `allow_shrink=True`，manifest 记 `shrink_confirmed`；窗口截断不在确认范围 | test_f002_exporter.py::test_shrink_guard_can_be_confirmed_but_window_truncation_never_is + test_f002_cli_contract.py::test_allow_shrink_flag_is_forwarded_to_exporter | 3 | 3 | guard-without-escape-hatch |
| F002-R3-03 | 旧 `src/alphamill/data_bridge/symbol_map.csv` 仍被 git 跟踪但已无人读写 | low | 质量 | 根因 | 修改引入 | fixed | `git rm` + 旧引用加改址说明 | 文件删除；F001 design 旧路径处补一行改址（不改写原句） | 全套件绿 | 3 | 3 | orphaned-artifact |
| F002-R3-04 | `finally` 里的 reset_snapshot_session 会用二次异常覆盖原始导出异常 | low | 质量 | 根因 | 修改引入 | fixed | 吞掉清理期的 psycopg2.Error | reset_snapshot_session 捕获 psycopg2.Error 降级为 warning | test_f002_reconcile.py + test_f002_exporter.py 两条（变异验证：还原旧实现判红） | 3 | 3 | finally-masks-original-error |
| F002-R3-05 | FIX-log 与 spec §6 记录的 HEAD 是父提交而非固化提交 | low | 质量 | 根因 | 流程缺陷 | fixed | 回写正确哈希 | §6 与 FIX-log 改指 `ad09ff4` + 第 3 轮序列，并补 T021 指针 | 文档如实性 | 3 | 3 | stale-evidence-pointer |

### 循环 10 模式教训

1. **`key-shape-mismatch` 出现两次（C001/C002），根子是同一个**：`signals_log` 是唯一没有
   pair 维度的 dataset，凡是「按维度分组/按维度查表」的代码都对它走了另一条分支，而测试
   种子数据恰好每天只有一个 symbol、每个日期只出现一次，两条分支的错误都测不出来。
   教训：**registry 里任何一个"形状特例"，测试种子必须专门造出能区分它的数据**。
2. **origin 分布：原始编码 12 / 修改引入 8 / 流程缺陷 4 / 规格漂移 3。**「修改引入」占到
   30%，且集中在第 2 轮那次大范围加固——一次性提交 15 改 + 5 新增、没有按 finding 拆分时，
   自伤率明显高于小步修复。这条直接支撑 skill 的「一 finding 一 commit」。
3. **同一处代码连续两轮出缺陷（Q001 → R3-01）**：第一轮是恒真断言 `or True`，修复时去掉了
   `or True` 却换上了「断言 `Path.glob` 枚举顺序」这个同样不成立的性质。教训：**把恒真断言
   改成"有内容的断言"时，要先问这个性质是否真的被保证**，否则只是把空转换成假红。
4. **最长存活 2 轮，持有者是 C001**——它在第 2 轮被声明修复但代码一行没动。检视方靠第 1 轮
   留下的离线探针一跑即戳破。教训：**发现缺陷时顺手留一个可重跑的最小复现脚本**，比任何
   文字描述都更能防住"口头已修复"。
5. **门禁真的会咬人**：第 3 轮加 `--allow-shrink` 把 exporter.py 顶到 358 行，
   `test_f001_line_limit_exemptions` 当场判红。豁免表只对 F001 原样迁移文件有效，新代码
   不得挂靠，于是按 SOP 拆出 `export_policy.py`。这是本循环里门禁阻止范围蔓延的正面案例。

### 循环 10 裁决分布与建议命中率

- fixed 25 / partial 1 / rejected 0 / tracked 1 / carried-forward 0（共 27 条）。
- 唯一 partial 为 R2-01：FIX-log 补齐部分接纳并核对通过；「一 finding 一 commit」部分不接纳，
  理由「起始工作树无可还原的 commit 历史」经核对成立（检视方第 2 轮亲见起始态为未提交工作树、
  HEAD 仍是 569359b）。剩余载体=后续轮次必须按 finding 拆提交，第 3 轮已按此执行（5 条修复
  拆成 5 个提交）。
- 建议命中率约 93%（25/27 实质采纳 `suggested_fix`）。两处偏差都有价值：
  C003 的建议是「判 removed + 是否移出 partitions 交 owner 裁决」，实现直接取了"移出"，
  由此产生 R2-02；Q001 的建议被字面执行后产生 R3-01。**教训：检视建议不能只写"做什么"，
  涉及语义变更时要同时写清"这么做会打开哪个新口子"**，否则建议本身就是下一条 finding 的来源。
- 全接纳率 96% 需警惕"检视在凑数"的反向信号；本循环的对冲证据是：8 条为修改引入（首轮
  物理上不存在）、1 条第 2 轮被误报已修复后在第 3 轮才真正关闭、1 条转 tracked 而非硬关，
  说明发现具备实质性而非形式化。

---

## 循环 11：F004 Kronos 真实推理运行时设计检视

- report_type: doc-review | round: 1（full-scan）→ 2（修复覆盖 52%，一次性 full-scan）→ 3/4（diff-only）| 状态: 闭环
- 日期：2026-09-14～2026-09-15 | 基线：`bc314f0` → `c5100a0`
- 范围：`docs/features/0.2/F004-kronos-inference-runtime/{spec,design,tasks}.md` 及必要的 F001/F002 契约勘正；不含 UI mockup 与非 F004 PRD 改动。
- 结论：14 条 finding 全部 fixed，Critical/High/Medium/Low 开放项均为 0；本地 `python3 tools/verify.py`（经项目 `.venv` 解释器实跑）`194 passed, 23 skipped`，图谱风险分 0.0；最终 CI 由本总结提交触发。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F004-D001 | 真实 profile 未接入 `signals_log` 的生产消费者 | High | 正确性 | 根因 | 规格漂移 | fixed | 接线并验收 `signals_log.source=kronos`，或删除自动升级承诺 | 删除自动升级承诺，将消费者路由排除并同步勘正 F002 限制说明 | 文档生命周期 + 链接门 | 1 | 2 | cross-feature-contract-drift |
| F004-D002 | 失败关闭与串行推理没有实现路径 | High | 正确性 | 根因 | 初始设计 | fixed | 增启动预检、eager load/readiness、推理锁和对应测试 | 增加启动预检、eager load、readiness、非零退出、进程级锁及 AC-002 | 文档生命周期 + 链接门 | 1 | 2 | fail-closed-contract-unimplemented |
| F004-D003 | 一条命令复现缺 compose 定位与数据前置条件 | High | 正确性 | 根因 | 初始设计 | fixed | 固定 compose 文件并补数据准备前置 | compose 命令固定 `-f`，并补齐 DB 迁移和至少 30 根闭合 K 线前置 | 文档生命周期 + 链接门 | 1 | 2 | incomplete-reproduction-contract |
| F004-D004 | AC-001 的现有测试可绕过 compose 假绿 | High | 测试覆盖 | 根因 | 流程缺陷 | fixed | 新增 F004 专属静态与容器门禁 | AC-001/002 改由 F004 专属静态、运行时与容器门证明，F001 冒烟只验证 HTTP | 文档生命周期 + 链接门 | 1 | 2 | test-does-not-prove-deployment |
| F004-D005 | real 镜像依赖清单漏掉上游直接依赖 | High | 正确性 | 根因 | 规格漂移 | fixed | 补齐 `huggingface_hub`、`tqdm` 并锁定 CPU wheel 来源 | 锁定已验证的 torch CPU wheel 与四项最小推理依赖版本 | 文档生命周期 + 链接门 | 1 | 2 | upstream-dependency-drift |
| F004-D006 | 验收环境违反执行机取证纪律 | High | 正确性 | 根因 | 规格漂移 | fixed | 指定执行机及 hostname/device 证据要求 | 指定 qiaozhi-lt 执行集成并记录 hostname/device，开发机只跑静态和单元门 | 文档生命周期 + 链接门 | 1 | 2 | wrong-evidence-machine |
| F004-D007 | NFR-001 的构建隔离机制与判据未定义 | Medium | 测试覆盖 | 根因 | 初始设计 | fixed | 固定 target 并改用稳定可断言判据 | 固定 mock/real target，判据改为默认镜像无 torch 且不启用或构建 real | 文档生命周期 + 链接门 | 1 | 2 | unverifiable-nonfunctional-requirement |
| F004-D008 | 资产挂载契约缺 tokenizer 路径与只读约束 | Medium | 正确性 | 根因 | 初始设计 | fixed | 补全路径、只读性和端口两侧契约 | 补齐只读挂载、模型/tokenizer 路径、开关、设备及 8002:8001 映射 | 文档生命周期 + 链接门 | 1 | 2 | incomplete-runtime-mount-contract |
| F004-D009 | PRD 来源把 FR3 误写为信号生产 | Medium | 正确性 | 根因 | 规格漂移 | fixed | 改正 PRD 来源与 FR3 关系 | 来源改指 M0、FR1.2、FR5，FR3 明确为下游评测关系 | 文档生命周期 + 链接门 | 1 | 2 | requirement-source-mismatch |
| F004-D010 | 任务依赖图断链且收口任务混合两个动作 | Medium | 质量 | 根因 | 初始设计 | fixed | 串完整 DAG 并拆分收口动作 | 重构三阶段 DAG，拆开证据回写与状态同步，最终门统一为 verify.py | 文档生命周期 + 链接门 | 1 | 2 | task-graph-gap |
| F004-D011 | real 服务契约遗漏数据库依赖与网络接入 | High | 正确性 | 根因 | 初始设计 | fixed | 补齐 DB_*、TimescaleDB healthy dependency、alphamill 网络及正反门禁 | design/spec/T004-T006 同步完整运行链与静态、容器断言 | 文档生命周期 + 链接门 | 2 | 3 | incomplete-runtime-wiring |
| F004-D012 | 应用启动钩子和配套文档没有任务所有者 | Medium | 质量 | 根因 | 修复引入 | fixed | 校正影响面并明确 `server.py`/VENDORED 所有者 | 校正 HTTP 契约与实现影响面，T001 明列 server.py，并新增 VENDORED.md 回写任务 | 文档生命周期 + 链接门 | 2 | 3 | implementation-artifact-unowned |
| F004-D013 | 实现任务引用的测试门在执行顺序中尚不存在 | Medium | 测试覆盖 | 根因 | 修复引入 | fixed | 测试先红后实现，或将测试创建并入对应任务 | T001-T004 改为任务内测试先红后实现转绿，T005 收窄为门禁补全与变异验证 | 文档生命周期 + 链接门 | 2 | 3 | test-created-after-implementation |
| F004-D014 | 文档回写任务声称依赖实测通过但排在实测任务之前 | Medium | 质量 | 根因 | 修复引入 | fixed | 重排依赖或把需实测通过的回写移至实测后 | VENDORED 回写与实测拆为独立分支，实测后并行回写 F001 命令与 F004 证据，最终门禁汇合全部分支 | 文档生命周期 + 链接门 | 3 | 4 | task-graph-order-contradiction |

所有 finding 的 `disposition_reason` 均为 `—`：本循环没有 rejected 或 partial 裁决。

### 循环 11 模式教训

1. **没有重复的精确 `pattern_tag`，但 14 条问题集中在三类传播断点**：运行时契约没有同步到 compose/test（D004/D007/D008/D011）、跨 feature 承诺没有同步消费者（D001/D009）、任务图没有同步实现与取证顺序（D010/D012-D014）。设计三件套检视应固定走「行为承诺 → 实现所有者 → 测试门 → 执行/证据任务」四跳核对。
2. **origin 分布：初始设计 6、规格漂移 4、修复引入 3、流程缺陷 1。** 修复引入占 21%（3/14），均由后续 diff-only 捕获；这再次证明修复后独立复核不能省略。
3. **所有 finding 的存活轮数均为 1（`resolved_round - first_seen_round`）**。最长存活没有超过一轮；Round 2 因修复覆盖 52% 按协议一次性升级 full-scan，后续恢复 diff-only，未发生无限重读。
4. **任务 DAG 是本循环最易自伤的编辑面**：D010 的重构解决断链，却在后续补所有者和测试顺序时引出 D012-D014。以后新增或重排任务后，必须同时验证编号连续、所有任务可达、无环、文字前提与箭头一致。

### 循环 11 裁决分布与建议命中率

- fixed 14 / partial 0 / rejected 0 / tracked 0（14 条全部接纳并关闭）。
- 建议命中率 100%（14/14 实质采纳 `suggested_fix`）；D001、D014 都从检视给出的备选方案中选择了边界更小的一项。
- 全接纳率 100% 需警惕检视意见是否过度保守；对冲证据是 7 条 High 中包含可复现的 DB/compose 断链和测试假绿，3 条修复引入只在后续轮次出现，并非首轮形式化凑数。
- 提交纪律有两项透明偏差：D001、D003 各有补遗提交；tasks.md 是共享编辑面，D010/D013 提交承载了其他 finding 的任务级同步。偏差已在 FIX-log 逐条声明，未影响 diff 归属核对。

## 循环 12：F004 Kronos 真实推理运行时实现代码检视

- report_type: code-review | round: 1（full-scan）→ 2（fix-verification，diff-only）→ 3（fix-verification，diff-only，封顶轮）| 状态: 闭环（CI 最终门禁受环境限制，见下）
- 日期：2026-09-15 | 基线：`fe9403b` → `3216a6d` → `7fc67c7`
- 范围：F004 实现交付 `b4968cc..fe9403b`（12 files，+791/−40）及其两轮修复；含 `deployment/kronos-service.Dockerfile`、`docker-compose.yml`、`.dockerignore`、`src/alphamill/kronos_service/{server,kronos_real}.py`、三个 F004 测试文件、F001 spec §6 AC-006 命令与 `vendor/VENDORED.md`。不含 F004 设计三件套的规格检视（循环 11 已闭环）。
- 结论：23 条 finding——**fixed 18 / partial 1 / tracked 2 / open(Low) 3**，Critical 0、High 2（均 round 2 关闭）。本地 `.venv/bin/python tools/verify.py` 全绿（231 passed, 29 skipped），检视方三轮共复现 **28 组反向变异**独立核对，未采信任何纯文字修复声明。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F004-T001 | 静态编排门禁读裸子串，把关键行整行注释掉后门禁仍全绿 | High | 测试覆盖 | 根因 | 初始实现 | fixed | 切块前统一 `_strip_comments` 并补注释类变异 | `_service_block` 切块前剥离注释；变异表 +4 项「整行注释掉」 | `test_f004_compose_profile_contract.py::test_compose_mutations_fail_the_gate` | 1 | 2 | gate-reads-text-not-semantics |
| F004-T002 | `app` 解绑 lifespan 钩子后 F004 全部单测仍绿——失败关闭接线在 CI 侧无门 | High | 测试覆盖 | 根因 | 初始实现 | fixed | 走 `app.router.lifespan_context` 而非模块函数 | `_consume_lifespan` 改走 `server.app.router.lifespan_context(server.app)` | `test_f004_kronos_runtime_contract.py::test_server_lifespan_invokes_startup_hook_in_real_mode` | 1 | 2 | gate-tests-function-not-wiring |
| F004-C001 | mock 服务保留 `KRONOS_USE_REAL_MODEL` 覆盖，置 true 即让默认编排陷入崩溃重启循环 | Medium | 正确性 | 根因 | 初始实现 | fixed | compose 钉死 `"false"` + 静态断言与变异 | 钉死 `"false"`，`.env.example` 删该键，门禁双向断言 + 2 项变异 | `test_f004_compose_profile_contract.py::test_compose_real_service_contract` | 1 | 2 | fail-closed-hook-hits-unintended-service |
| F004-C002 | rows<30 时 `/predict` 仍标 `source=kronos`，湖内无法区分真实推理与兜底中性信号 | Medium | 正确性 | 根因 | 初始实现 | partial(见裁决记录#1) | 未进模型不得写 kronos（抬 4xx 或按 reason 决定 source） | `build_prediction` 按 `reason` 判定 `source`，双向单测 | `test_f004_kronos_runtime_contract.py::test_not_enough_data_signal_never_labeled_kronos` | 1 | 2 | evidence-label-not-earned |
| F004-Q001 | 缺 `.dockerignore`，build context 是仓库根，real 目标每次构建重传 `.venv`/`models`/`vendor` | Medium | 质量 | 根因 | 初始实现 | fixed | 加仓库根 `.dockerignore` 排除重资产 | 白名单 `*` + `!pyproject.toml` + `!README.md` + `!src/`，静态门禁 + 2 项变异 | `test_f004_compose_profile_contract.py::test_dockerignore_keeps_build_context_minimal` | 1 | 2 | — |
| F004-T003 | 去掉 `_load_predictor` 记忆化后单测仍全绿——「加载至多一次」由测试自带 fake 复刻 | Low | 测试覆盖 | 根因 | 初始实现 | fixed | 只 patch 更底层的加载，用生产 `_load_predictor` 验证 | 新增用例 patch `sys.modules` 的 torch/model，断言第二次调用不再 `from_pretrained` | `test_f004_kronos_runtime_contract.py::test_production_load_predictor_memoizes` | 1 | 2 | test-simulates-itself |
| F004-T004 | 「默认编排不启用/不构建 real 服务」只有 tasks 里的手工命令，无自动门禁 | Low | 测试覆盖 | 根因 | 初始实现 | fixed | 加 `compose config --services` 双向断言 | 集成层新增双向断言（默认不含 real / 带 profile 含） | `test_f004_real_profile.py::test_default_compose_excludes_real_service` | 1 | 2 | — |
| F004-Q002 | `_service_block` 把下一服务的前置注释并入上一块，默认隔离断言实际在核对注释文本 | Low | 质量 | 根因 | 初始实现 | fixed | 同 T001 一处修复 | 随 T001 剥离注释一并解决，加独立边界回归用例 | `test_f004_compose_profile_contract.py::test_service_block_never_reads_next_service_comments` | 1 | 2 | — |
| F004-Q003 | `_wait_for_real_model` 的 deadline 不计请求超时，实际等待窗口最多约 2×POLL_SECONDS | Low | 质量 | 根因 | 初始实现 | fixed | 改用 `time.monotonic()` 截止时刻 | 同建议，去掉固定步长递减 | 静态复核（容器证据载体 tasks T013） | 1 | 2 | — |
| F004-Q004 | `assert "placeholder" not in output` 是偶然性断言，不构成「不退回 mock」的证据 | Low | 质量 | 症状 | 初始实现 | fixed | 换成容器 exited + 退出码非零 | 去 `--rm`，断言 `State.Status=exited` 且 `ExitCode≠0`，`finally` 清理 | `test_f004_real_profile.py::test_missing_assets_fail_closed` | 1 | 2 | — |
| F004-Q005 | `_future_timestamps` 触发 NumPy generic-unit DeprecationWarning（未来版本会报错） | Low | 质量 | 根因 | 初始实现 | fixed | 用 `pd.Timedelta("1min")` 替代裸整数换算 | **`pd.Timedelta(1, unit="min")`**——建议方案实测同样告警（见裁决记录#2） | `test_f004_kronos_runtime_contract.py::test_future_timestamps_emits_no_deprecation_warning` | 1 | 2 | — |
| F004-Q006 | 集成测试顶层 `import requests`，而 requests 未在 pyproject 声明（靠 ccxt 传递） | Low | 质量 | 根因 | 初始实现 | fixed | 写进 dev 依赖并锁范围 | `requests>=2.32,<3` 入 dev 依赖，纳入 `check_dep_pins` | `tools/check_dep_pins.py`（verify.py 步骤） | 1 | 2 | undeclared-test-dependency |
| F004-Q007 | F001 spec §6 compose 形态给了「等待 model_loaded=true」的注释却没有等待命令 | Low | 质量 | 根因 | 初始实现 | fixed | `up -d --wait` 让 healthcheck 充当等待步骤 | 同建议 | `tools/check_doc_links.py` + `test_f001_compose_contract.py` | 1 | 2 | — |
| F004-Q008 | 集成测试里的驼峰参数名与错误的 fixture 返回标注 | Low | 质量 | 根因 | 初始实现 | fixed | `reason_unavailable`；标注改 `Iterator[dict]` | 同建议 | `ruff check`（verify.py 步骤） | 1 | 2 | — |
| F004-R001 | C002 修复不对称——`/predict_batch` 信封仍无条件 `source=kronos`，与其内含 predictions 矛盾 | Medium | 正确性 | 根因 | 修复引入 | fixed | 信封 source 由 predictions 汇总决定 + batch 双向单测 | 信封 source/model 由 predictions 汇总：全 kronos→kronos、全兜底→placeholder、混合→mixed | `test_f004_kronos_runtime_contract.py::test_batch_envelope_source_reflects_predictions` | 2 | 3 | partial-symmetric-fix |
| F004-R002 | `.dockerignore` 白名单未经真实构建验证，且同时作用于 data-collector 镜像（F001/F002 运行链） | Medium | 测试覆盖 | 根因 | 修复引入 | fixed | tasks.md 立条目含 AC，执行机构建后标 tracked | 载体 tasks T013：执行机构建三镜像 + 容器内 `import alphamill` + 容器套件复跑 | T013 执行机取证通过（spec §6 第二轮：三构建 exit 0 + import 0 + 7 passed，2026-09-16） | 2 | 3 | gate-cannot-see-runtime-semantics |
| F004-R003 | spec §6 验收证据的门禁计数已失真（静态 16/变异 13/运行时 8） | Medium | 质量 | 根因 | 流程缺陷 | fixed | 按 T010 回写 spec §6，done 前必须完成 | 勘正为 26/20/13 并补依赖与构建上下文条目；检视方复核计数与实际用例数逐一相符 | `tools/validate_spec_lifecycle.py` + 实际用例计数核对 | 2 | 3 | evidence-record-drift |
| F004-R004 | 延后到执行机的容器证据（Q001/Q003/Q004/T004）只写在 FIX-log 备注里，tasks.md 无承载条目 | Low | 质量 | 根因 | 流程缺陷 | fixed | 增 T013 含 AC，可与 R002 合并 | 与 R002 合并为 T013（含可判定的退出码级 AC 与 DAG 边 `T013 -> 状态收口`） | T013 执行机取证通过（spec §6 第二轮：三构建 exit 0 + import 0 + 7 passed，2026-09-16） | 2 | 3 | deferred-work-without-carrier |
| F004-R005 | `source=placeholder` 的兜底响应仍回报真实权重路径 `model=/app/models/Kronos-base` | Low | 正确性 | 根因 | 修复引入 | fixed | model 与 source 同一处判定 | 兜底分支 model 一并退回 `"placeholder"`（限 real 模式兜底，不动 mock 语义） | `test_f004_kronos_runtime_contract.py::test_not_enough_data_signal_never_labeled_kronos` | 2 | 3 | partial-symmetric-fix |
| F004-R006 | `_strip_comments` 对「值内含 `#`」无免疫，是静态门禁的潜在假红面 | Low | 质量 | 根因 | 修复引入 | fixed | 正则收窄或加约束注释 | 收窄为整行注释 `^[ \t]*#.*$`；13 组注释类变异复跑仍全判红 | `test_f004_compose_profile_contract.py::test_strip_comments_ignores_hashes_inside_values` | 2 | 3 | — |
| F004-R007 | R001 修复后 mock 模式下 `/predict_batch` 信封 `model=placeholder` 与内含条目 `models/Kronos-base` 矛盾 | Low | 正确性 | 根因 | 修复引入 | open | 信封 model 同样由 `{p.model}` 汇总，而非非-kronos 分支硬编码 `"placeholder"` | — | — | 3 | — | partial-symmetric-fix |
| F004-R008 | `/predict_batch` 信封 source 新增 `"mixed"` 取值，扩展了 F001 冻结的 HTTP 契约且未同步文档 | Low | 质量 | 根因 | 规格漂移 | open | F004 spec §4 记一句信封汇总语义，并同步 `db/init.sql:160` 的取值注释 | — | — | 3 | — | contract-extension-undocumented |
| F004-R009 | `_strip_comments` 收窄后行尾注释不再剥离，可被行尾注释冒充满足断言 | Low | 测试覆盖 | 根因 | 修复引入 | open | 断言改行级精确匹配（不引入新依赖），或解析 YAML 并显式声明 pyyaml 依赖 | — | — | 3 | — | gate-reads-text-not-semantics |

### 循环 12 裁决记录

**#1 · F004-C002 · partial · 裁决轮次 2** —— 接纳部分（`/predict` 单条按 `reason` 判定 `source`）已 fixed 并经变异复核（把 `source` 改回无条件 `"kronos"` → 回归测试判红）。未完成部分有明确载体：`/predict_batch` 信封 → `F004-R001`（round 3 已 fixed）；`model` 字段 → `F004-R005`（round 3 已 fixed）。证据为本地实跑输出：`单条 source=placeholder / 信封 source=kronos / 批量内单条 source=placeholder`。

**#2 · F004-Q005 · 建议未命中、修复方案更优 · 裁决轮次 2** —— 修复方指出检视建议的 `pd.Timedelta("1min")` 同样触发告警。检视方复跑核实成立（pandas 2.3.3 / numpy 2.5.3：`minutes=1` 告警、`"1min"` 告警、`1, unit="min"` 无告警）。finding 本身成立且已修，不记 rejected，只计入建议命中率的未命中项。

**#3 · F004-R006 · 取舍接纳 · 裁决轮次 3** —— 修复方采用「仅剥整行注释」而非检视建议的「空白+# 行尾注释」，理由是二者与「值内 `#` 免疫」在正则层不可兼得。检视方接受该取舍（行尾注释不改变 YAML/Dockerfile 语义），但残余的行尾注释冒充面已单列为 `F004-R009`，不让取舍吞掉问题。

### 循环 12 模式教训

1. **两条 High 是同一个失效模式的两面：门禁在"验函数"而不是"验接线/验语义"。** `gate-reads-text-not-semantics`（静态编排门禁读裸子串，注释掉整行照样绿）与 `gate-tests-function-not-wiring`（测试直接调模块函数，绕开 `app` 实际绑定的 lifespan）合计 2/23，但它们守的恰好是 F004 仅有的两条核心不变式（默认隔离、失败关闭）。**教训：新增门禁必须对"配置/接线被移除"这一类变异做验证，而不是只对"值被改错"做验证。** Round 1 的 13 项变异全是改值/删行，因此全部判红却全部无效。
2. **`partial-symmetric-fix` 出现 3 次（R001/R005/R007），是本循环复发率最高的模式。** C002 的原则（未进模型的标签不得声称 kronos）有四个落点：单条 source、单条 model、信封 source、信封 model。修一个落点就宣布修完，导致同一原则被拆成三轮才补齐，且 R007 至今仍开着。**教训：发现"标签/状态语义"类缺陷时，先枚举该语义的全部落点再动手，把枚举写进 finding 的 suggested_fix。**
3. **origin 分布：初始实现 14、修复引入 7、流程缺陷 2。修复引入占 30%（7/23），全部由后续 diff-only 轮次抓到，首轮物理上不可能发现。** 这是本项目第二次实测到该比例（循环 11 是 21%），"最低 2 轮"的协议规定再次被证明不是形式主义。
4. **存活轮数：18 条为 1 轮，3 条（R007/R008/R009）仍为 0 轮内新发现，无任何 finding 跨 2 轮以上未解决。** 没有触发不收敛升级协议。
5. **`deferred-work-without-carrier`：修复方把四条延后到执行机的容器证据只写在 FIX-log 备注里，tasks.md 无条目。** 这正是协议第 4 条要堵的"按缺陷走检视循环永远关不掉"。建立 T013（含退出码级 AC 与 DAG 边）后才允许标 `tracked` 并移出收敛统计。**教训：任何"本机没有这个能力"的延后，落点必须是带 AC 的任务条目，不是声明文字。**
6. **`evidence-record-drift`：两轮修复加了 10 个门禁用例，spec §6 的验收证据计数没人动。** 证据记录不是写一次就完的静态文本；只要门禁集合变化，AC 引用的计数就失真。**教训：把"门禁计数回写"绑到"新增门禁"这个动作上，而不是绑到 feature 收口。**

### 循环 12 裁决分布与建议命中率

- fixed 18 / partial 1 / tracked 2 / rejected 0 / open(Low) 3。无 rejected——三轮里修复方一次都没有行使不接纳权，两次分歧（Q005 的方案、R006 的取舍）都以"finding 成立、方案更优"的形式收敛，这是健康形态。
- 建议命中率 **85%（17/20 实质采纳 `suggested_fix`）**。三条未命中各有原因：Q005（我的 `Timedelta("1min")` 实测同样告警，修复方方案更优）、C002（我给了"抬 4xx 或按 reason 判定"两个选项，修复方选了边界更小的后者）、R006（取舍不同，见裁决记录#3）。**85% 比循环 11 的 100% 更健康**——全接纳往往说明检视在凑数或修复方在照单全收。
- **检视质量的自证靠变异，不靠条数**：三轮共 28 组反向变异，Round 1 抓到 2 条 High 都是"既有门禁全绿但变异不红"，Round 2/3 的每一条 fixed 都由检视方重跑变异从绿翻红。修复声明中没有一条是靠文字采信的。
- 提交纪律：三轮共 19 个 commit，一 finding 一 commit，仅 R002+R004 按检视方明示建议合并为同一条目。无批量大提交。

### 循环 12 残余观察项与闭环处置

- **`F004-R007` / `F004-R008` / `F004-R009`（均 Low，open）**：不阻塞闭环（协议第 7 条只以 Critical/High 为阻塞判据），但也不允许蒸发——三条完整留在上表，含 `suggested_fix`。R007/R008 的现实影响面为零：`/predict_batch` HTTP 端点在仓内**没有任何消费者**（`KronosFusionStrategy` 只用单条 `/predict`；bench 脚本调的是 Kronos 库自带的 `predict_batch` 方法；`signals_log.source` 是无约束 TEXT）。建议在消费者路由切换（spec §3 范围外、tasks §5 后移项）立项时一并处理。
- **`F004-R002` / `F004-R004`（tracked → T013）**：`.dockerignore` 的 docker 语义与容器级证据只能在执行机取。开发机 `docker info` 实测不可达，按 SOP §3 这不是失败也不是证据。T013 的 AC 是退出码级可判定的，F004 `review → done` 以它为前置。**已闭环（2026-09-16）**：T013 在执行机 `qiaozhi-lt` 完成——三镜像重建 exit 0（上下文 354B/6.67kB）、三容器 `import alphamill` exit 0、容器套件 7 passed（见 spec §6 第二轮证据）；R002/R004 状态更新为 fixed。
- **CI 最终门禁：绿**。修复终态 `7fc67c7` 的 CI run `34953277116` success；本复盘提交 `af8bdce` 的 run `34954284354` success（py3.11 / py3.13 双矩阵，`verify.py` 全部步骤通过）。据此执行协议第 8 节的闭环清理：本地删除过程稿 `CURRENT-code.md` 与 `FIX-log.md`（二者 gitignored，无删除提交）。
- **取证环境备注**：默认沙箱内到 `api.github.com` 的 HTTPS 出口被拦截（`gh run list` → TLS handshake timeout / EOF），SSH 到 origin 正常；CI 状态最终在放开沙箱后取得。这条记下来是因为它会重复影响后续循环的"推送后确认 CI"步骤——不要因为 `gh` 首次超时就判定无 CI 权限。

## 循环 13：F003 AlphaGen vendor 与可插拔生成器平面 规格文档检视

- report_type: doc-review
- 周期：2026-09-16 ~ 2026-09-18（7 轮，Round 7 为角色合并修复+复核）
- 状态：闭环（stop_condition_met: true）
- 被检对象：`docs/features/0.2/F003-alphagen-vendor/{spec,design,tasks}.md` 及相邻契约（架构 §7.1、ADR-0001/0007、F004、F007、F008、BACKLOG）

### 循环 13 完整 issue 表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首现轮 | 修复轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F003-D001 | factor_id 含 run_seq，跨 run 变动 | high | correctness | root-cause | original-coding | fixed | 删除 run_seq 并补跨 run 相等断言 | factor_id 改为 generator + definition_digest 内容寻址，run_id 不参与身份 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[factor_id_no_run_seq] | 1 | 2 | spec-internal-contradiction |
| F003-D002 | REJECTED/FAILED 终态事实未持久化 | high | correctness | root-cause | original-coding | fixed | 为失败和拒绝保留终态 manifest | 四种终态均写 run.json，只有 completed 可消费 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[terminal_run_facts] | 1 | 2 | spec-internal-contradiction |
| F003-D003 | 2 日闸门错误直达 L2 | high | correctness | root-cause | spec-drift | fixed | 按 ADR-0001 分离 L1 与 L2 判据 | time-box 只裁 L0/L1，L1→L2 改为连续两周判据 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[tier_ladder_matches_adr0001] | 1 | 2 | spec-internal-contradiction |
| F003-D004 | 冒烟验收缺漏斗记账与奖励频率抽查 | high | correctness | root-cause | spec-drift | fixed | 将 ADR-0001 两项 M2 义务写入冒烟 manifest | 补生成侧逐级计数、F007 not_yet_available 占位和奖励频率抽查 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[smoke_obligations_linked] | 1 | 2 | gate-without-teeth |
| F003-D005 | 过渡绑定缺少 ADR-0007 语义字段 | high | correctness | root-cause | spec-drift | fixed | 显式元组与 ResearchSnapshot 语义逐项对齐 | 补 schema_version、cutoff、as-of、映射、日历和 provenance 字段 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[explicit_tuple_fields_match_adr… | 1 | 2 | cross-feature-contract-drift |
| F003-D006 | PIT 掩码未依赖 F008 universe_at/digest | high | correctness | root-cause | spec-drift | fixed | 将 F008 IR-002/IR-003 设为 PIT 掩码契约 | F003 明确消费 F008 universe_at(T)、digest 和 schema_version | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[pit_mask_depends_on_f008] | 1 | 2 | cross-feature-contract-drift |
| F003-D007 | 安全断言强于进程级护栏能力 | high | correctness | root-cause | original-coding | fixed | 明确不等价于内核网络隔离 | 将 NFR/AC 断言收敛为进程级护栏、白名单和 fail-closed | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[egress_claim_matches_guard_stre… | 1 | 2 | gate-without-teeth |
| F003-D008 | SIGTERM 将部分运行标为 completed | high | correctness | root-cause | original-coding | fixed | 增加 partial 终态并限制下游消费 | SIGTERM 改为 partial，不写 pool.json，不发 completed 事件 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[sigterm_not_completed] | 1 | 2 | spec-internal-contradiction |
| F003-D009 | generation objective 缺成本后收益 | high | correctness | root-cause | spec-drift | fixed | 将成本后收益加入 objective 和 run.json | 增加参数化成本后收益预筛，不产 F007 成本裁决 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[objective_includes_after_cost] | 1 | 2 | spec-internal-contradiction |
| F003-D010 | 协同池不是可执行 FactorDef | high | correctness | root-cause | original-coding | fixed | 以标准 FactorDef 持久化协同池 | pool.json 改为 generator=pool 的可执行 FactorDef | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[pool_is_executable_factordef] | 1 | 2 | spec-internal-contradiction |
| F003-D011 | tasks 缺 [TEST] 旅程验收组 | high | test-coverage | root-cause | process-gap | fixed | 在 tasks §3 增加必填 [TEST] 组 | 增加 US-001/002/003 三条 [TEST] 旅程任务并加入流转门禁 | tests/unit/test_validate_spec_lifecycle.py::test_review_missing_test_group_rejected | 1 | 2 | spec-tasks-traceability-gap |
| F003-D012 | 任务顺序与收口依赖不足 | high | correctness | root-cause | process-gap | fixed | 实现任务先于验证和回写，并为收口任务增加依赖 | 重排 smoke 任务并增加 T032/T039 收口边 | tests/unit/test_check_task_dag.py::test_backward_edge_rejected | 1 | 2 | task-graph-order-contradiction |
| F003-D013 | GPU FIFO 协议有文字定义但 Kronos 生命周期接口未闭合 | high | correctness | root-cause | spec-drift | fixed | 在 F004 或 F003 补可调用的 stop/status/restore contract、错误码、幂等和版本化跨 Feature 测试；保留 owner=F003 | FIFO/owner 已修；剩余 F004 侧生命周期接口由 R2-002 承接并于 Round 4 核对闭合（载体级） | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[kronos_lifecycle_contract_defin… | 1 | 7 | deferred-work-without-carrier |
| F003-D014 | F007 未声明 F003 上游契约 | high | correctness | root-cause | spec-drift | fixed | 上下游双向声明 generation.*、算子清单和 pool | F007 补 F003 events/operator registry/pool 的只读摄入契约和任务载体 | tests/unit/test_check_doc_consistency.py::test_f007_declares_f003_upstream | 1 | 2 | cross-feature-contract-drift |
| F003-D015 | FactorDef 持久化 DTO 缺加载恢复契约 | medium | correctness | root-cause | spec-drift | fixed | 明确磁盘 DTO 到可执行 FactorDef 的转换 | 补 factor_store.load() 重建 compute/meta 的加载契约 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[factordef_dto_matches_architect… | 1 | 2 | spec-internal-contradiction |
| F003-D016 | GenerationRun 缺 schema_version 载体 | medium | test-coverage | root-cause | process-gap | fixed | 为 run/factor schema version 配置 AC 和任务 | 补 GenerationRun schema_version、AC-012 和 CLI 未知版本拒绝 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[ir003_schema_version_has_carrie… | 1 | 2 | spec-tasks-traceability-gap |
| F003-D017 | AC 未覆盖全部 DR/TR/NFR 子句 | medium | test-coverage | root-cause | process-gap | fixed | 逐条把引用需求的关键子句写入 AC 和验证载体 | 补 AC-003/005/009/010/011 的字段、事件、查询和 CLI 断言 | tests/unit/test_check_doc_consistency.py::test_ac_body_coverage_goes_red | 1 | 2 | spec-tasks-traceability-gap |
| F003-D018 | 可复现性缺 canonical config 与确定性契约 | medium | correctness | root-cause | original-coding | fixed | 将 canonical config 和设备差异写入重现契约 | 增加 config artifact/digest、稳定子种子和 torch 确定性约束 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[reproducibility_config_digest] | 1 | 2 | gate-without-teeth |
| F003-D019 | CLI 无法构造完整 GenerationRequest | medium | correctness | root-cause | original-coding | fixed | 为所有强制字段定义 CLI 来源或默认值 | 补 smoke/mine/seed 的参数、默认 window/config/quota 和 config 留痕 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[cli_builds_generation_request] | 1 | 2 | spec-tasks-traceability-gap |
| F003-D020 | HypothesisDef 缺 applicable_state | medium | correctness | root-cause | spec-drift | fixed | 与 PRD FR2.1 对齐适用状态字段 | 补 applicable_state/regime 和 unspecified 显式默认值 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[hypothesis_has_applicable_state] | 1 | 2 | spec-internal-contradiction |
| F003-D021 | vendor 卫生逐行比对缺可复现基线 | medium | test-coverage | root-cause | process-gap | fixed | 冻结上游 commit 的逐文件 digest | 增加逐文件 sha256 上游基线 artifact 并要求差异集合等于标注集合 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[vendor_hygiene_has_upstream_bas… | 1 | 2 | gate-without-teeth |
| F003-D022 | 活跃 feature 索引漂移 | low | quality | symptom-patch | spec-drift | fixed | 以 BACKLOG 非 done 集合作为索引真源 | CLAUDE/docs README 按 BACKLOG 非 done 集合对齐并加一致性门禁 | tests/unit/test_check_doc_consistency.py::test_active_feature_indexes_go_red_on_claude_drift | 1 | 2 | — |
| F003-R2-001 | 任务 DAG 门禁不检查所有任务可达收口或既有关键边 | high | correctness | root-cause | fix-regression | fixed | check_task_dag.py 从最高任务反向遍历所有 T-id，并固化 F003 的 T036/T037/T038 -> T039 必需边；孤立任务或删除任一关键边必须判红，补真实变异测试 | check_task_dag.py 增加从收口任务反向遍历的可达性检查，并锁定关键边删除变异 | tests/unit/test_check_task_dag.py::test_orphan_task_rejected; tests/unit/test_check_task_dag.py::test_missing… | 2 | 3 | gate-without-teeth |
| F003-R2-002 | Kronos stop/restore 生命周期接口未定义 | high | correctness | root-cause | fix-regression | fixed | 在 F004/F003 契约中定义版本化 stop/status/restore API、幂等性、超时、错误码、显存确认和未部署行为，并将契约测试纳入两边 tasks | 架构补 HTTP /lifecycle/* + X-Contract-Version + 错误信封 wire 绑定；F004 spec 范围外/tasks §5 登记载体；契约测试落盘为 xfail(strict)；门… | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[kronos_lifecycle_contract_defin… | 2 | 7 | deferred-work-without-carrier |
| F003-R2-003 | 过渡绑定把 universe 与 calendar 压成单一 artifact | high | correctness | root-cause | spec-drift | fixed | 将 explicit_tuples 改为独立 universe_digest/universe_path 与 calendar_digest/calendar_path，并分别校验、写 provenance，之后再映射… | explicit_tuples 拆分 universe/calendar artifact、path、schema_version 和组合 digest | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[explicit_binding_splits_univers… | 2 | 3 | cross-feature-contract-drift |
| F003-R2-004 | FactorDef expression 的 DTO 字段形态仍不明确 | medium | correctness | root-cause | fix-regression | fixed | 明确 expression 只存在于磁盘 DTO/meta，或扩展架构 FactorDef；给 canonical_json、加载恢复和字段白名单一套唯一形态 | 明确 expression 只存在于磁盘 DTO，加载后进入 meta.expression | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[factordef_expression_dto_shape] | 2 | 3 | spec-internal-contradiction |
| F003-R2-005 | PRD FR2.5 注册表生命周期与查重 owner 未闭合 | medium | correctness | root-cause | spec-drift | fixed | 在 F007/F006/独立 Feature 中明确评测摘要、／rho／ 查重、lifecycle 状态和唯一写入 owner，并在 F003 下游契约引用 | 明确 F007 负责评测摘要/查重/lifecycle 判定，F006 负责 lifecycle 动作 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[factor_registry_owner_declared] | 2 | 3 | cross-feature-contract-drift |
| F003-R2-006 | T001 仍是已关闭 Q-001 的过时前置任务 | medium | correctness | root-cause | process-gap | fixed | 删除 T001 或改为可执行的 F008 artifact contract 前置任务；同步任务编号、依赖边和验收载体，不能把已关闭问题当作开发前动作 | T001 改为 F008 universe artifact contract 前置任务并补依赖边 | tests/unit/test_check_doc_consistency.py::test_stale_closed_question_task_goes_red | 2 | 3 | spec-tasks-traceability-gap |
| F003-R2-007 | [TEST] 组门禁不校验其位于 tasks 第 3 节 | medium | test-coverage | root-cause | fix-regression | fixed | 先提取 tasks 第 3 节正文，再只在该节识别 `### [TEST]`；增加错误章节伪造标题的变异测试 | 生命周期门只在 tasks 第 3 节识别 [TEST] 组 | tests/unit/test_validate_spec_lifecycle.py::test_test_group_in_wrong_section_rejected | 2 | 3 | gate-without-teeth |
| F003-R4-001 | 生命周期契约的先红态会被 F003 执行机验收吸收为通过 | high | correctness | root-cause | fix-regression | fixed | 把端点 feature 设为 T033 前置边并要求 T033 对该文件 0 xfailed（或把真实卸载取证显式后移到有载体的任务），同步修正 tasks §4 过时的 F004->T025 边与 BACKLOG 自… | require 改钉 T033 命令整串 pytest -q --runxfail tests/integration/test_f003_generation_run.py（角色合并：检视方修复） | check_doc_consistency::kronos_t033_zero_xfail_gate（变异：删 --runxfail / 删 0 xfailed 均判红） | 7 | 7 | gate-without-teeth |
| F003-R4-002 | 契约目标实例与测试默认地址指向 mock（8001），XPASS 转正警报打不响 | high | correctness | root-cause | fix-regression | fixed | 契约明确目标实例为真实推理服务（kronos-signal-real / 执行机 GPU 实例），测试去掉 8001 默认值，未设 KRONOS_CONTROL_URL 时 skip 并在 T033 verify 命令… | 测试去 mock 默认值，lifecycle_test_no_mock_default 钉 getenv 无默认形态 + 行为单测 | tests/unit/test_f003_lifecycle_contract_config.py::test_control_url_has_no_default / ::test_require_ready_ski… | 7 | 7 | cross-feature-contract-drift |
| F003-R4-003 | status 动作错误码缺 E_UNSUPPORTED_VERSION，与 wire 绑定和契约测试矛盾 | medium | correctness | root-cause | fix-regression | fixed | status 行错误码补 E_UNSUPPORTED_VERSION，并在 kronos_lifecycle_contract_defined 钉住 | status 行补 E_UNSUPPORTED_VERSION 与 device 字段，门禁钉字面量 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[kronos_lifecycle_contract_defin… | 7 | 7 | spec-internal-contradiction |
| F003-R4-004 | “服务确未部署”无判定方法，404/连接拒绝/CPU 实例的归类未定义 | medium | correctness | root-cause | spec-drift | fixed | 在架构 §7.1 补决策表：连接拒绝+编排中无该服务→offload_not_needed；404/E_UNSUPPORTED_VERSION→fail-closed；status 报 device=cpu→offlo… | 改为解析式 check_offload_decision_table：解析架构 §7.1 决策表与 EXPECTED_OFFLOAD_TABLE 逐格比对；AC-010/design/T025 共用规范子句且 desi… | tests/unit/test_check_doc_consistency.py::test_offload_table_row_disposition_flip_goes_red / ::test_offload_t… | 7 | 7 | spec-internal-contradiction |
| F003-R4-005 | 载体存在性门禁硬编码单一路径，不泛化到其他声明的测试文件 | low | quality | symptom-patch | fix-regression | fixed | 改为扫描 spec/design/tasks 中所有 tests/**.py 引用并校验存在（可对尚未开工的文件用显式白名单） | 泛化为 check_declared_test_carriers：扫描三件套全部 tests/**.py 引用 + 18 项白名单台账，落盘即须移除 | tests/unit/test_check_doc_consistency.py::test_declared_test_carrier_missing_goes_red / ::test_declared_test_… | 7 | 7 | — |
| F003-R5-001 | 架构声称对 mock 的探测归 offload_not_needed，决策表推不出来 | medium | correctness | root-cause | fix-regression | fixed | 删掉该括注（客户端只探测 KRONOS_CONTROL_URL 指定的真实实例），或给 mock 加一行明确规则 | 删 mock 探测括注，改为客户端只探测 KRONOS_CONTROL_URL 指定实例；forbid 旧括注 | check_doc_consistency::kronos_offload_classification_defined（forbid 对其探测按下方决策表归） | 7 | 7 | spec-internal-contradiction |
| F003-R5-002 | device=cpu 放行行在端点缺失时不可达，CPU 实例会无限期阻塞夜槽 | medium | correctness | root-cause | fix-regression | fixed | 用户裁决方案 A（裁决记录#3）：决策表补行——HTTP 404 / E_UNSUPPORTED_VERSION 时回落 /health 的 device 或设备侧读数（nvidia-smi 进程/显存），device… | 按裁决#3 落 404 回落探测于架构/design/AC-010/T025，reason=endpoint_absent_no_gpu_tenant | check_doc_consistency::kronos_offload_classification_defined（回落探测 / endpoint_absent_no_gpu_tenant requires） | 7 | 7 | spec-internal-contradiction |
| F003-R5-003 | F003 多处仍写经 F004 交付的服务生命周期控制，与 F004 不含控制面矛盾 | low | correctness | root-cause | spec-drift | fixed | 统一改为经架构 §7.1 契约（服务端归 BACKLOG 待分配 feature），并加 forbids | design/spec 四处统一为经架构 §7.1 服务生命周期契约，forbid 旧措辞 | check_doc_consistency::kronos_owner_wording_unified | 7 | 7 | cross-feature-contract-drift |
| F003-R5-004 | 载体白名单不报孤儿条目（文档已不引用的条目静默残留） | low | quality | root-cause | fix-regression | fixed | 白名单条目不在 refs 中即判红 | 白名单条目不在三件套引用中即判红 | tests/unit/test_check_doc_consistency.py::test_declared_test_carrier_orphan_entry_goes_red | 7 | 7 | — |
| F003-R6-001 | WSL2 下 nvidia-smi 列不出 GPU 进程，“卡上无 Kronos 进程”恒真，回落探测会放行并行抢卡 | high | correctness | root-cause | fix-regression | fixed | 进程列表不可得（WSL2）视为设备信息不可读 → fail-closed；放行判据改为 /health.device=cpu 或 memory.used 低于可配阈值；T025 单测覆盖“进程列表为空但显存占用高 → … | 404 行判据改为 /health.device=cpu 或 memory.used 低于 kronos_vram_idle_threshold；读数不可得即 fail-closed；四份文档 forbid 旧进程判据… | tests/unit/test_check_doc_consistency.py::test_offload_table_process_criterion_goes_red；check_doc_consistency… | 7 | 7 | platform-assumption-unverified |

### 循环 13 裁决记录

1. `F003-D013` · `partial` → Round 4 翻 `fixed`。
2. 修复方 Round 4 偏差 1 · 不接纳 · `--runxfail` 可机器化 · Round 5。
3. `F003-R5-002` · 用户裁决 · 方案 A · 2026-09-18；Round 6 起判据由 R6-001 修正为显存读数（方案 A 方向不变）。
4. 修复方 Round 5 偏差 1（按内容而非提交消息归属核对）· 接受 · Round 6。
5. Round 7 · 角色合并（协议 §7）· R4-004 片段锁连续两轮失败，检视方下场改为解析式检查并自检 · 2026-09-18。

### 循环 13 模式教训

1. **`gate-without-teeth` 是本循环第一大模式（7 条）**，且以最贵的方式复发：R4-004 的「钉字面量片段」连续两轮被行级改写绕过（改处置、删行、删条件、改 AC 措辞全部门禁全绿）。**教训：锁一张有语义的表，要解析这张表逐格比对，而不是钉几段字符串**——片段 require 只能证明「某句话还在」，证明不了「这张表还是那个意思」。同一教训的小号版本：`--runxfail` 的 require 被旁边说明文字里的同名串满足；以及同一规范子句在 design 出现两处时改其一不红（去重后才判红）。
2. **`deferred-work-without-carrier` 跨 4 轮才关闭（D013 → R2-002 → R4-* → R6-001）**，存活轮数全循环最长。根因是「契约写完了但没人能验」：先是接口只有动作语义没有 wire 绑定，然后是契约测试文件被声明却从未落盘（Round 3 独立核对抓到），再是先红态被 T033 的验收命令吸收成通过。**教训：跨 feature 的延后项，载体必须同时满足三件事——文本定义、落盘测试、验收命令里能判红。**
3. **`platform-assumption-unverified`（R6-001）由检视方自己引入。** 上一轮我给出的方案 A 用「卡上无 Kronos 进程」作放行判据，而执行机是 WSL2，`nvidia-smi` 在那里根本不列 GPU 进程——判据恒真，等于把「绝不并行抢卡」红线自动放行。**教训：写进契约的观测判据，必须先确认目标平台上该观测真的可得**；检视方给的方案同样要过这道关，本条按 fix-regression 归因于检视方。
4. **origin 分布：original-coding 8、spec-drift 11、fix-regression 14、process-gap 6。** 修复引入占 36%（14/39），高于循环 11（21%）与循环 12（30%）。集中在同一块契约（Kronos 生命周期）连续四轮修复上——**每轮针对上一条失败断言打补丁而不锁不变量，正是协议 §7 升级条款描述的形态**；最终靠角色合并（检视方下场改为解析式检查）一轮收敛。
5. **并行会话是本循环的持续性噪声源**：F007 会话与 F003 会话共享同一工作区，先后造成——修复方 amend 撞上对方 HEAD 产生混合提交 `cc453a8`、检视方两次在工作区看到非本轮改动、`test_repo_passes_all_checks` 因对方在飞文本变红。**教训：共享工作区时，取证一律在 `git worktree` 的干净树里做；amend 前必须重验 HEAD 归属。**

### 循环 13 裁决分布与建议命中率

- fixed 39 / partial 0（D013 的 partial 已在 Round 4 转 fixed）/ tracked 0 / rejected 0 / open 0。
- 不接纳权行使 1 次（修复方 Round 4 偏差 1：主张 0 xfailed 只能是程序性要求），检视方不接受并给出可执行反证（`--runxfail` 实测端点缺失即 3 failed）——这是本循环唯一一次分歧，以证据收敛，未上升到用户裁决。
- 用户裁决 1 次（R5-002 方案 A：CPU 实例放行 vs 一律 fail-closed），裁决后该条一轮修复到位；其判据缺陷由 R6-001 在下一轮修正，方向未变。
- 建议命中率约 **90%**（多数 `fix_summary` 与 `suggested_fix` 实质一致）；偏离的主要是 R4-004——检视方建议的「逐行钉字面量」本身被证明不够，最终由检视方自己改为解析式检查，**这是建议错误而非修复方偏离**。
- 变异取证：7 轮共约 30 组反向变异，其中 3 轮（Round 4/5/6）各抓到「修复方声称已锁、实测门禁全绿」的假锁，合计 9 处。**没有一条 fixed 是靠文字采信的。**

### 循环 13 闭环处置

- 过程稿 `CURRENT-doc-F003.md` / `FIX-log-F003.md`（均 gitignored，本地-only）在本次收口时删除；F003 Round 1–3 的历史修复声明留在 `FIX-log.md`，该文件随 F007 循环一并收口。
- 收口提交推送后由 CI 作最终门禁；CI 红则恢复过程稿并按第 8 轮重开。
- 遗留执行义务（不属检视 finding）：R6-001 的判据需在执行机 `qiaozhi-lt` 实测取证（WSL2 下 `nvidia-smi` 进程列表确实为空、`memory.used` 读数可得），载体为 T025 单测与 T033 夜槽证据。

## 循环 14：F007 统一评测台与证据门禁 规格文档检视

- report_type: doc-review
- 周期：2026-09-16 ~ 2026-09-18（3 轮：R1 full-scan → R2 全量升级（diff>30%）→ R3 diff-only 封顶 + 不收敛升级（角色合并）+ 独立复核闭环）
- 状态：闭环（stop_condition_met: true）
- 被检对象：`docs/features/0.2/F007-evaluation-gates/{spec,design,tasks}.md` 及相邻契约（F003 spec/design/tasks、F008 IR-002/003、ADR-0003/0007、架构 §4.4、PRD FR2.5/FR3.4/3.5、BACKLOG、`tools/check_doc_consistency.py`、`tools/check_task_dag.py`）
- 检视/修复角色：R1/R2 检视=会话A、修复=会话B；R3 检视=会话B，因 D041 连续 3 轮不收敛触发 review-convergence §7 升级路径 (b)，由检视方角色合并修复 D041–D047；**R3 修复由会话C（独立会话）复核后闭环**——复核证据：五提交 diff 逐条比对、四道文档门 + 136 门禁单测复跑、tar 副本上三处独立变异（优先级表输出越界/查重顺序倒置/删 RUNNING->REJECTED）全部判红、verify.py 全绿、CI run 35342337086 绿。
- 结论：R1 25 条（high 8/medium 13/low 4）；R2 复核 24 通过、1 条未修完，新增 15 条（自伤 11/16≈69% 按当轮 open 口径 38–44%）；R3 复核 16 条全过、新增 7 条（自伤 6/7）；R3 修复后独立复核 7/7 通过。47 条全部 fixed，无 rejected/partial/tracked。
- 同步义务：F003 spec/design/tasks、ADR-0007 修订、架构 §4.4、BACKLOG 随跨文档 finding 一并修订（各自提交，见 FIX-log 两轮声明）。

### 循环 14 完整 issue 表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首现轮 | 修复轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  | tasks 缺 design.md:16-18 强制的 [TEST] 旅程验收组 | high | test-coverage | root-cause | process-gap | fixed | tasks 第 3 节增补 [TEST] 层 2 旅程验收组，从 US-001/002/003 派生可执行断言 | tasks §3 增 [TEST] 组 T027/T028/T029（US-001/002/003），重编号到 T030 并补旅程前置边 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[f007_test_group_present]; tes… | 1 | 2 | test-group-missing |
|  | F003 上游只在 spec 声明，design/tasks 缺其事件/算子登记表/协同池摄入 | high | correctness | root-cause | spec-drift | fixed | design/tasks 增 F003 与 generation.* / 算子登记表 / 协同池摄入点及任务 | design §0/§2/§4 增 F003 只读摄入契约与 upstream_contracts.py；T001/T014 承接 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[f007_ingests_f003_contracts] | 1 | 2 | cross-feature-contract-drift |
|  | F008 未列入 F007 related_features/上游（R2：design frontmatter 仍缺 F008） | medium | correctness | root-cause | spec-drift | fixed | 'design.md:5 改为 [F002, F003, F004, F008]；check f007_declares_f008_universe 增 (F007_DESI… | design frontmatter 补 F008；f007_declares_f008_universe 两侧钉 frontmatter | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[f007_declares_f008_universe] | 1 | 3 | partial-symmetric-fix |
|  | universe 与 calendar 合并为单 JSON，与 F008 冲突 | high | correctness | root-cause | spec-drift | fixed | 拆分两个 artifact 契约，universe 按 F008 IR-002 消费 | 新增 DR-006 拆两个 artifact 引用；CLI 拆 --universe/--calendar；T001 分别校验 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[universe_calendar_artifacts_s… | 1 | 2 | cross-feature-contract-drift |
|  | 三层无前视只覆盖 L1，L2/L3 未显式承接 | high | correctness | root-cause | spec-drift | fixed | 明确三层执行者、证据与晋级前 fail-closed 门 | 新增 FR-007/AC-009，manifest 逐层记录，L2/L3 标 owner 并 fail-closed | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[no_lookahead_three_layers_owned] | 1 | 2 | no-lookahead-layer-gap |
|  | 样本量三级契约缺失 | high | correctness | root-cause | spec-drift | fixed | 冻结三级裁决并加断言 | FR-005/design §3.3/T010/AC-004 冻结 underpowered/provisional/trustworthy | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[sample_size_three_tiers] | 1 | 2 | gate-without-teeth |
|  | T012 缺 T009 入边；T013 缺 T012 入边 | medium | correctness | root-cause | process-gap | fixed | 显式补边 | §4 补 T009 -> T012、T012 -> T013 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[task_graph_missing_edges_f007] | 1 | 2 | task-graph-missing-edges |
|  | T016 缺 T012/T014 入边；T007 无出边 | medium | correctness | root-cause | process-gap | fixed | 显式补边 | §4 补 T007 -> T010/T011、T012/T014 -> T016 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[full_chain_controls_have_pred… | 1 | 2 | task-graph-missing-edges |
|  | 真实环境 T022 与 T016 复用同一 fixture | high | test-coverage | root-cause | process-gap | fixed | T022 绑不可变 snapshot 与 hostname，独立命令 | T022 改执行机 ALPHAMILL_INTEGRATION=1 独立命令与 test_f007_controls_real.py，绑定 snapshot/hostname | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[real_env_task_has_distinct_ev… | 1 | 2 | gate-without-teeth |
|  | 留出预算断言零变化，但无预算台账实体 | high | correctness | root-cause | spec-drift | fixed | 新增 holdout budget ledger 实体与 DR | 新增 DR-005 HoldoutBudgetLedger（append-only）、design 目录、T012、AC-001 零行/越权负例 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[holdout_budget_ledger_exists] | 1 | 2 | gate-without-teeth |
|  | verdict 词汇冲突 | medium | correctness | root-cause | spec-drift | fixed | 冻结 stage 状态与 verdict 两层枚举 | design §3.3 冻结两层术语表，FR-003 引用 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[verdict_vocabulary_frozen] | 1 | 2 | spec-internal-contradiction |
|  | SC-002 并发与故障注入无 task/test | medium | test-coverage | root-cause | process-gap | fixed | 增并发/故障注入集成测试任务 | 新增 T024 与 test_f007_concurrency.py，design §5/§8 映射 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[sc002_concurrency_has_task] | 1 | 2 | gate-without-teeth |
|  | AC-003 缺多成员批量用例 | medium | test-coverage | root-cause | process-gap | fixed | 增多成员 cohort 批量 fixture | AC-003/FR-004 scenario/T016 增多成员 cohort 批量夹具 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[ac003_multi_member_batch] | 1 | 2 | batch-scenario-untested |
|  | NFR-004 近似标注无覆盖 | medium | correctness | root-cause | spec-drift | fixed | report schema 增 approximation 字段并加断言 | report schema 增 approximation 字段；AC-011；T015 断言 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[nfr004_approximation_covered] | 1 | 2 | spec-tasks-traceability-gap |
|  | 变异目标与 AC 标签不一致，无 kill 证据/工具锁定 | medium | test-coverage | root-cause | process-gap | fixed | 统一标签，增工具 pin 与 kill 证据 | T017/T021 AC 标签对齐；mutation_report.json；dev 依赖 pin 约束 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[mutation_targets_labels_aligned] | 1 | 2 | gate-without-teeth |
|  | 统计第二实现抽查无任务承接 | medium | correctness | root-cause | spec-drift | fixed | 增第二实现对照任务 | 新增 T025（time-box 1 周、容差、证据路径） | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[second_implementation_has_task] | 1 | 2 | deferred-work-without-carrier |
|  | F004 信号源到 FactorDef 的适配契约缺失 | medium | correctness | root-cause | spec-drift | fixed | 冻结 Kronos→FactorDef 适配与 placeholder 分层规则 | 新增 DR-007 SignalFactorProvenance；placeholder canonical 拒绝、preview 标注 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[f004_to_f007_factor_source_co… | 1 | 2 | cross-feature-contract-drift |
|  | F005 文件 reader 层级歧义 | low | correctness | root-cause | spec-drift | fixed | 明确前端只经 API | design §6 明确前端只经统一只读 API，文件 reader 仅 API 内部 adapter | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[f005_frontend_does_not_bypass… | 1 | 2 | cross-feature-contract-drift |
|  | 最终确认窗统计未排除在 Agent 可读产物之外 | medium | correctness | root-cause | spec-drift | fixed | 显式排除并 fail-closed | NFR-003/IR-003/AC-010 与 design §7 显式排除并 fail-closed | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[final_confirmation_window_hid… | 1 | 2 | gate-without-teeth |
|  | design §8 遗漏 tasks 使用的测试文件 | medium | test-coverage | root-cause | process-gap | fixed | 补映射 | design §8 补映射，新增解析式 tasks⊆design 门 | tests/unit/test_check_doc_consistency.py::test_f007_design_test_map_goes_red_on_unmapped_test | 1 | 2 | spec-tasks-traceability-gap |
|  | 五阶段 ID 与失败维度未冻结 | medium | correctness | root-cause | original-coding | fixed | 冻结 schema | design §3.3 冻结 stage_id 与 failure_taxonomy；AC-012 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[stage_ids_and_failure_dimensi… | 1 | 2 | spec-tasks-traceability-gap |
|  | NFR-005 与 UX-001 无 task/AC 追溯 | medium | correctness | root-cause | spec-drift | fixed | 增 AC 与 verify | AC-011 覆盖 NFR-005/UX-001，T006/T015 verify | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[nfr005_ux001_traceable] | 1 | 2 | spec-tasks-traceability-gap |
|  | design 内嵌 tasks 行动指令 | low | quality | root-cause | process-gap | fixed | 移到 tasks | 行动指令移入 tasks §0，design 只留约束声明 | tests/unit/test_check_doc_consistency.py::test_deprecated_text_reintroduced_goes_red[design_no_task_directi… | 1 | 2 | responsibility-boundary-violation |
|  | 状态词汇与 canonical=bench/事件注册未对齐 | low | correctness | root-cause | original-coding | fixed | 统一命名与映射 | TR-003 命名 evaluation.registered，spec §5 与 design §3.2 写明 bench/preview 映射 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[state_vocab_and_bench_mapping… | 1 | 2 | spec-internal-contradiction |
|  | 属性测试缺执行任务与生成器约束 | low | test-coverage | root-cause | process-gap | fixed | 补执行任务与可复现约束 | 新增 T026 与 design §8 固定 seed/显式策略约束 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[property_strategy_has_executi… | 1 | 2 | spec-tasks-traceability-gap |
|  | 运行生命周期没有失败成员的终态登记路径，cohort 可能永远无法 finalize | high | correctness | root-cause | original-coding | fixed | spec §5 增 VALIDATING/RUNNING -> REJECTED(FAIL) 终态，并允许 REJECTED/UNDERPOWERED/INCOMPLETE(… | spec §5 增 REJECTED 终态、REJECTED/INCOMPLETE(重试耗尽)→REGISTERED、INCOMPLETE→RUNNING 重试；finalize 判据=全部 REGISTERED（残留缺口见 D044） | tests/unit/test_check_doc_consistency.py::test_f007_lifecycle_closure_goes_red_on_missing_registration | 2 | 3 | spec-internal-contradiction |
|  | L2/L3 未落地时 promotion_verdict 无合法取值，且「晋级 paper」没有接口承载阻断点 | high | correctness | root-cause | fix-regression | fixed | promotion_verdict 增 `blocked_pending_audit`（或拆 evidence_verdict 与 promotion_eligibility… | promotion_verdict 增 blocked_pending_audit、冻结导出优先级表、新错误码 E_PROMOTION_BLOCKED，阻断点交 F006 入口（枚举闭合缺口见 D041） | tests/unit/test_check_doc_consistency.py::test_f007_promotion_enum_goes_red_on_missing_blocked_state | 2 | 3 | gate-without-teeth |
|  | 因子注册表评测面写入 owner 只在 spec §3 声明，design/tasks/AC 无载体 | high | correctness | root-cause | spec-drift | fixed | 按 operator 裁决（裁决记录#1）拆分：v0.2 由 F007 实现评测摘要回写与 |ρ| 查重（spec 增 FR-008 + AC、design §2/§4 增模… | 按裁决#1：FR-008/DR-008/AC-013、registry_writeback 模块与下游契约、T030/T031；lifecycle 后移 F006；F003 与 BACKLOG 同步（查重时序缺口见 D042） | tests/unit/test_check_doc_consistency.py::test_f007_registry_writeback_carrier_goes_red_on_lost_requirement | 2 | 3 | cross-feature-contract-drift |
|  | '[TEST] 旅程 T027–T029 的 verify 命令没有运行承载其断言的测试文件' | high | test-coverage | root-cause | fix-regression | fixed | 按 design §8 的 AC→文件映射补齐：T027 加 test_f007_artifact_schemas.py；T028 加 test_f007_execution… | T027–T029 verify 按 design §8 映射补齐载体；解析式门 f007_test_group_verify_covers_ac_map | tests/unit/test_check_doc_consistency.py::test_f007_test_group_verify_goes_red_on_uncovered_carrier | 2 | 3 | gate-weaker-than-claim |
|  | DR-006 改写了 ADR-0007 的 universe_calendar_digest 定义，但 ADR 未修订、组合算法未冻结 | medium | correctness | root-cause | fix-regression | fixed | 修订 ADR-0007（schema 的 provenance 拆 universe_path/calendar_path，写明组合公式，如 sha256(canonical… | ADR-0007 修订：provenance 拆 universe_path/calendar_path，冻结 sha256(canonical_json) 组合公式；DR-006/design §3.1/F003 同式（架构 §4.4 未同步见 D045） | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[adr0007_universe_calendar_spl… | 2 | 3 | cross-feature-contract-drift |
|  | 样本量三级的边界、计量单位和与其他裁决的优先级未定义 | medium | correctness | root-cause | fix-regression | fixed | 冻结半开区间 [0,30)/[30,69)/[69,∞) 并去掉「≈」；写明 FactorDef 运行的「笔」如何计数（成本模拟交易数或独立观测数）；给 promotion_… | 半开区间 [0,30)/[30,69)/[69,∞)、「笔」口径与 sample_unit、优先级表引用、AC-004 边界用例 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[sample_tier_boundaries_frozen] | 2 | 3 | spec-internal-contradiction |
|  | 留出预算台账没有写入路径，也不执行周度 top-k 与滚动窗位置 | medium | correctness | root-cause | fix-regression | fixed | 明确 v0.2 FactorDef 流程是否访问留出（PRD FR3.4 规定留出属 PortfolioDef）；若访问，design §5 增追加步骤、DR-005 增 h… | 按「不访问」分支：DR-005/design 写明 v0.2 无追加写入者、预留 holdout_window/regime，写入者后移 FR4/M3 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[holdout_ledger_writer_deferred] | 2 | 3 | gate-without-teeth |
|  | 任务 DAG 仍缺边：实现任务无前置，验证任务可先于实现执行，T025 自相矛盾 | medium | correctness | root-cause | fix-regression | fixed | 补 T001 -> T007/T008、T002 -> T009、T004 -> T007；T018 依赖 T005/T008/T009，T020 依赖 T006/T013/… | §4 补 14 条生产者边、T025 移出旅程前置；DAG 门禁新增 §3 前置与 verify 生产者规则 | tests/unit/test_check_task_dag.py::test_section3_task_with_unwired_producer_rejected | 2 | 3 | task-graph-missing-edges |
|  | T025 容差 1e-6 对 block bootstrap 不可达，单元测试依赖可选外部实现 | medium | correctness | root-cause | fix-regression | fixed | 按估计器分容差：确定性量（BH-FDR、HAC）用 1e-6，bootstrap 用固定 seed 同实现复算或按置信区间重叠/分位差阈值判定；Vibe-Trading 对照… | T025 容差按估计器分档；Vibe-Trading 对照移到可 skip 的 integration | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[second_impl_tolerance_by_esti… | 2 | 3 | '' |
|  | design §0 需求范围陈旧，design §8 缺 AC-012 映射 | medium | correctness | root-cause | fix-regression | fixed | design §0 改为 FR-001~FR-007、DR-001~DR-007、TR-001~TR-003、IR-001~IR-003；§8 增 AC-012 行（test… | design §0 更新到 FR-008/DR-008；§8 补 AC-012/AC-013；解析式门 spec AC ⊆ design §8 | tests/unit/test_check_doc_consistency.py::test_f007_design_ac_map_goes_red_on_missing_row | 2 | 3 | partial-symmetric-fix |
|  | L2/L3 owner 指向「F006/M3」，但 F006 只是运营操作入口的预留 ID，范围不含审计器 | medium | correctness | root-cause | fix-regression | fixed | 在 BACKLOG 为 L2 重放审计与 L3 信号缓存对齐建条目（或并入 F006 预留行并写明范围）；F007 tasks §5 明确后移增这一行 | BACKLOG F006 预留行扩范围（L2/L3 审计器 + lifecycle 状态判定）；tasks §5 增后移行 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[deferred_owner_has_carrier] | 2 | 3 | deferred-work-without-carrier |
|  | canonical CLI 让调用方自报 --code-build-digest，身份关键字段未校验 | medium | correctness | root-cause | original-coding | fixed | 由 runner 从已安装构建（包内容/锁文件/git tree）计算 digest；CLI 参数只作期望值，不一致即 E_INPUT_INVALID；工作树脏时拒绝 can… | --code-build-digest 只作期望值，runner 自算，不一致或脏工作树拒绝 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[code_digest_runner_computed] | 2 | 3 | self-declared-identity |
|  | F003 约定 F007 为 cost_model_version 真相源，F007 未声明该对外字段 | low | correctness | root-cause | spec-drift | fixed | design §3.1 把 cost_model.id 命名/别名为 cost_model_version 并声明对 F003 的只读发布位置 | design §3.1 声明 cost_model.id 对外即 cost_model_version 并随 report/DR-008 发布 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[cost_model_version_published] | 2 | 3 | cross-feature-contract-drift |
|  | spec 需求 ID 乱序、IR-003 指代歧义、T023 AC 标签不全 | low | quality | root-cause | fix-regression | fixed | FR-007 移到 FR-006 之后，DR 按编号排列；DR-001 写成「F008 IR-003」；T023 标签补到 AC-012 | FR/DR 按编号重排、DR-001 写成 F008 IR-003、T023 标签补全；解析式排序门 | tests/unit/test_check_doc_consistency.py::test_f007_requirement_id_order_goes_red_on_reorder | 2 | 3 | '' |
|  | 新增证据目录未进 design §3.2 目录树 | low | quality | root-cause | fix-regression | fixed | §3.2 目录树补 f007/real_env、mutation/f007、property/f007、second_impl，并注明哪些是 canonical 证据、哪些是… | design §3.2 目录树补四个证据目录并标注 canonical/开发期属性 | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[evidence_dirs_in_design_tree] | 2 | 3 | '' |
|  | promotion_verdict 枚举缺 provisional，与导出优先级表第 5 级及 spec FR-005 矛盾 | high | correctness | root-cause | fix-regression | fixed(pending-independent-review) | 枚举补 provisional（或第 5 级改输出既有值并删掉 spec 中的 provisional 顺位）；门禁改为从优先级表解析输出值集合并断言 ⊆ 术语表枚举，删除硬… | 枚举补 provisional/rejected；优先级表扩 7 级；门禁改为解析比对并删除硬编码枚举 | tests/unit/test_check_doc_consistency.py::test_f007_promotion_enum_goes_red_on_priority_output_not_in_enum | 3 | 3 | enum-closure-drift |
|  | '|ρ| 查重在 cohort FINALIZED 之后才产出，重复因子可带 promising 被 F006 消费；比较数据源与 cohort 内互查未定义' | high | correctness | root-cause | fix-regression | fixed(pending-independent-review) | 把查重前移到 finalize 内（cohort_verdict 计算前），dedup.verdict=rejected 进入优先级表（归 dead 或新增取值）；写明相关性… | 查重移入 finalize 且先于 verdict 导出、同一次原子写；口径取 OOS PnL/rolling IC；补 cohort 内互重规则；回写只搬运 | tests/unit/test_check_doc_consistency.py::test_f007_dedup_goes_red_when_finalize_order_inverted | 3 | 3 | spec-internal-contradiction |
|  | 导出优先级表不完全：REJECTED 成员对应哪个 promotion_verdict 未定义 | medium | correctness | root-cause | fix-regression | fixed(pending-independent-review) | 优先级表增一行：run 状态 REJECTED（方法论/纯度门拒绝）→ dead（或 rejected，与 D041 一并决定枚举）；并注明表按 run 终态与 stage … | 优先级表第 1 级覆盖 REJECTED 与 dedup rejected；门禁断言条件覆盖 | tests/unit/test_check_doc_consistency.py::test_f007_promotion_table_goes_red_when_rejected_state_uncovered | 3 | 3 | spec-internal-contradiction |
|  | 状态机删去「任意非终态 → INCOMPLETE」后，CREATED/VALIDATING 的输入失败与 RUNNING 期运行时守卫失败没有迁移；「显式 abandon」无入口 | medium | correctness | root-cause | fix-regression | fixed(pending-independent-review) | 补 CREATED/VALIDATING → INCOMPLETE（输入/快照摘要不符，对应 design §7 映射）与 RUNNING → REJECTED（运行时守卫：… | §5 补三条迁移、重试边改 INCOMPLETE -> VALIDATING；IR-001/design 增 abandon；门禁断言 §7 映射覆盖 | tests/unit/test_check_doc_consistency.py::test_f007_lifecycle_goes_red_on_uncovered_failure_mapping | 3 | 3 | spec-internal-contradiction |
|  | 架构 §4.4 仍按合并的 universe/calendar JSON 描述，未随 ADR-0007 修订同步 | medium | correctness | root-cause | fix-regression | fixed(pending-independent-review) | architecture §4.4 与 ResearchSnapshot 示例改为 universe_digest/calendar_digest 两个引用 + 冻结组合公式… | 架构 §4.4 与示例随 ADR-0007 同步；新增 architecture_universe_calendar_split_aligned | tests/unit/test_check_doc_consistency.py::test_required_text_removed_goes_red[architecture_universe_calenda… | 3 | 3 | partial-symmetric-fix |
|  | T023 声称覆盖 AC-013 但前置不含 T030；T030 缺 T007/T010/T011 前置；T030 在文档中编号不单调 | low | correctness | root-cause | fix-regression | fixed(pending-independent-review) | T023 前置补 T030；T030 前置补 T007/T010/T011；T030 挪到 §2 末尾并说明编号为追加编号（或整体重编号） | 回写轨重排为 T018/T028，消除向后边；§4 补生产者边；§0 说明编号语义 | tests/unit/test_check_task_dag.py::test_real_feature_tasks_satisfy_verification_rules | 3 | 3 | task-graph-missing-edges |
|  | 修复声明证据哈希不可达：5071476 已被 amend 为 cc453a8；修复期间两次用 git checkout 覆盖了未提交修复 | low | quality | root-cause | process-gap | fixed(pending-independent-review) | FIX-log 以 cc453a8 更正 5071476；变异取证只在临时副本（git archive / worktree）上做，禁止在工作区 checkout 复原 | 本轮变异只在副本上做；FIX-log [review-r3] 更正哈希 5071476 → cc453a8 | — | 3 | 3 | evidence-hash-rewritten |

### 循环 14 模式教训

- **修复自伤率持续偏高**：R2 新增 15 条中 11 条 `fix-regression`、R3 新增 7 条中 6 条——对抗式「修复→检视」循环在规格文档上自伤率 38–69%，远高于 skill 经验值 20–30%，印证「第 2 轮 diff 复核必须做」与「3 轮封顶 + 升级」两条规则。
- **词汇类矛盾对抗式修不稳**：`promotion_verdict` 枚举三轮失稳（D011 → D027 → D041），每轮都在补上一轮的断言；收敛靠两件事——门禁从「硬编码正确答案」改为**解析不变量**（枚举集合 == 优先级表输出集合、spec 串 == 表行序），以及角色合并直接锁不变量。模式标签 `enum-closure-drift`。
- **子串针脚的固有盲区**：TEXT_CHECKS 只能证明「文字没被删」，证明不了「契约闭合」——D026/D027/D029/D041 都在全部门禁绿的情况下成立。R2 起新契约一律配解析式门（状态机迁移解析、表格解析、任务图解析），子串针脚只用于措辞级回归。
- **跨 feature 契约漂移是最大来源**：`cross-feature-contract-drift` ×7（F003 注册表 owner、F008 宇宙台账、ADR-0007 摘要公式、架构 §4.4、cost_model_version）——上游/平行 feature 的每次修订都要显式核对下游三处（spec/design/tasks）+ 架构 + ADR 的同步义务。
- **门禁加强的跨会话义务**：收口可达性（779c78e）与 §3 前置/生产者规则（本轮）两次使既有 feature 文档判出新问题；门禁变更必须在同一轮内把全部活跃 feature 修到绿，并在 FIX-log 单独声明。
- **流程教训**（D047，`evidence-hash-rewritten`）：真实仓库变异取证必须在改动提交后或 tar 副本上做——R2 曾两次 `git checkout --` 误复原未提交修复；并行会话 append-only 注册表（`tools/check_doc_consistency.py`）使逐 finding 提交不可行，以 finding↔断言映射表替代并在声明中说明。
- **存活轮数最长**：F007-D003（1→3，partial-symmetric-fix：先修 spec 漏 design，下轮才补齐）；D026/D027/D028/D030/D033 等 R2 修复均带出 R3 残留缺口，按「另立新 finding 不回退原条目」统计。
- **裁决分布**：47 条全部 accepted（无 rejected/partial），`suggested_fix` 与 `fix_summary` 实质一致率约 80%（偏差集中在 D026 状态机形态、D029 门禁范围、D032「不访问」分支三处，均为修复方声明理由后检视方核对接受）——全接纳且建议命中率高，说明检视建议质量稳定；无对抗性拒绝也说明双方对契约事实无分歧。

## 循环 15：F007 统一评测台与证据门禁 实现代码检视

- report_type: code-review | round: 1（full-scan）→ 2（diff-only）| 状态: 闭环
- 日期：2026-09-19 | 基线：`99e8092` → 终基线 `1d005d5`
- 检视人：Sisyphus（首轮独立取证由 Oracle 承担）| 修复方：并行会话
- 范围：`git diff main...HEAD`（90 文件 / ~15k 行新增），聚焦 design §8 指定的高风险路径：canonical writer、留出访问、统计失败语义、artifact 发布
- 结论：首轮 1 严重 / 4 高 / 3 中 / 0 低；第 2 轮 diff-only 复核 9/9 `fixed`，Critical/High 清零；R1-001（Critical）与 R1-002（High）的**接线**经**实际执行变异**验证——删掉生产调用 → 对应测试 RED，恢复 → GREEN

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-001 | 必需统计（HAC/bootstrap/BH-FDR/DSR/MinTRL）已实现但从未接入 canonical 流程 | 严重 | 正确性 | 根因 | 原始编码 | fixed | canonical 调成员级统计、finalize 调 cohort 级；异常 → INCOMPLETE | pipeline 接 member_statistics、finalize 接 cohort_statistics | test_f007_controls.py::test_canonical_report_wires_member_required_statistics / ::test_finalize_wires_cohort_level_multiplicity | 1 | 2 | implemented-not-wired |
| R1-002 | finalize 从不做 \|ρ\| 查重，也不重导 promotion_verdict | 高 | 正确性 | 根因 | 原始编码 | fixed | finalize 内按承诺顺序 resolve_cohort_dedup 后导出 verdict | canonical_ops 内 resolve_cohort_dedup + 重导 verdict，同一次原子写 | test_f007_canonical_registry.py::test_finalize_wires_cohort_dedup_and_overrides_verdict | 1 | 2 | implemented-not-wired |
| R1-003 | 已发布但未登记的运行无法恢复，cohort 永久挂 OPEN | 高 | 正确性 | 根因 | 原始编码 | fixed | 复用分支返回前幂等补登记 | 复用分支调 ensure_member_registered | test_f007_cli.py::test_published_but_unregistered_run_is_recovered_on_rerun | 1 | 2 | crash-window-loss |
| R1-004 | 发布后追加事件，改坏自己的 events_digest | 高 | 正确性 | 根因 | 原始编码 | fixed | 登记事件纳入发布前集合 | registered_events 预先纳入 digest、删除发布后 append | test_f007_controls.py::test_published_events_match_manifest_digest_and_are_immutable | 1 | 1 | post-publish-mutation |
| R1-005 | canonical 未获取单写者 claim | 高 | 正确性 | 根因 | 原始编码 | fixed | 事务用 claim.acquire/release 包裹 | acquire 包裹 + finally 释放；复用分支在 acquire 前返回 | test_f007_cli.py::test_canonical_refuses_when_single_writer_claim_is_held | 1 | 2 | implemented-not-wired |
| R1-006 | 越权写入只抛异常、不留拒绝事件 | 高 | 正确性 | 根因 | 原始编码 | fixed | 边界捕获后原子追加 gate_rejected 再重抛 | holdout_budget / registry_writeback 各补 append_events(gate_rejected) | test_f007_canonical_registry.py::test_preview_overreach_on_ledger_leaves_gate_rejected_event | 1 | 2 | fail-closed-without-evidence |
| R1-007 | 同一承诺的多次登记静默 last-wins | 中 | 正确性 | 根因 | 原始编码 | fixed | 二次登记须载荷一致，否则拒绝 | register_member 对同 candidate 冲突载荷抛 RegistryIntegrityError | test_f007_canonical_registry.py::test_conflicting_duplicate_registration_is_rejected | 1 | 2 | silent-overwrite |
| R1-008 | finalize 重复执行不幂等（finalized_at 为墙钟） | 中 | 正确性 | 根因 | 原始编码 | fixed | 幂等判据排除 finalized_at | population 语义摘要剔除 finalized_at | test_f007_canonical_registry.py::test_finalize_is_idempotent_across_finalized_at_values | 1 | 2 | wallclock-in-identity |
| R1-009 | registration-last 的顺序契约没有被测试真正断言 | 中 | 测试覆盖 | 症状 | 原始编码 | fixed | 校验后再写 registration + 故障注入断言 | publisher 拆出 _write_registration 在校验后调用 | test_f007_atomic_publish.py::test_registration_is_written_only_after_validation | 1 | 2 | test-asserts-weaker-property |

### 循环 15 模式教训

- **新增最大模式：`implemented-not-wired`（×3）**——T009 的必需统计、T012 的 `resolve_cohort_dedup`、T025 的 `claim.acquire` 都**实现且有单测，却没有任何生产调用者**。单元测试证明「函数对」，证明不了「流程用了它」，于是 FR-004（多重检验/校正）与 FR-008（查重）在**门禁全绿**的情况下实际未被强制执行。这是本 Feature 最贵的教训。
- **验收任务的隐性失效**：T019/T021/T024 这类「运行测试」验收任务，实际执行的是**复跑单测**——它们本来就绿，于是占位设施被当成已接线。**验收必须证明接线**：新增契约的验收应至少包含一条「删掉生产调用 → 测试变红」的变异证据，否则验收只覆盖了函数级正确性。修复轮已按此补齐（R1-001/R1-002 逐条实测 RED→GREEN）。
- **`origin` 分布**：9 条全部 `original-coding`（首次实现就带的），**无 `fix-regression`**——本轮修复没有引入新问题，罕见地低于 skill 经验的 20–30% 自伤率；原因推测是修复集中在「接线」这类二值可验证动作，且每条都先做了变异验证再提交。
- **失败关闭的两种残缺**：`fail-closed-without-evidence`（R1-006：拒绝路径对，但拒绝事件没落盘）与 `post-publish-mutation`/`crash-window-loss`（R1-003/004：证据不可变性与崩溃窗口）——都是「行为对、证据错」，只有读**副作用与持久化**才看得出来，纯单测与快照断言抓不到。
- **存活轮数**：R1-004 为 1→1（第 1 轮内修复），其余 8 条 1→2。最长存活 1 轮，收敛快。
- **裁决分布**：9 条全部 accepted（无 rejected/partial），`suggested_fix` 与 `fix_summary` 实质一致率高——检视建议到修复的转化路径通畅，双方对契约事实无分歧。

## 循环 16：F007 统一评测台与证据门禁 并入后独立复检

- report_type: code-review | round: 1（full-scan）→ 2 → 3 → 4（升级）→ 5（角色合并后复核）| 状态: 闭环
- 日期：2026-09-19 | 基线：`49bd122`（F007 已 `done` 并在 main）→ 终基线 `c06a23c`
- 检视人：Sisyphus | 修复方：并行会话（第 1~3 轮）→ 检视人下场（第 4 轮升级后角色合并）
- 范围：`src/alphamill/evaluation/`、`src/alphamill/experiment_store/`、`factor_factory/bench/` 的统计与曲线（6142 行源码 / 7410 行测试）
- 结论：32 条（1 严重 / 9 高 / 14 中 / 8 低），全部关闭；其中 8 条为修复引入（`fix-regression`，自伤率 25%）。`R2-202` 连续 3 轮修复未闭合，触发 skill §7 升级协议，由检视人角色合并、先锁不变量后换实现关闭。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-101 | cohort 级必需统计对任何 promotion_verdict 都不产生影响，FR-004 在生产上空转 | 严重 | 正确性 | 根因 | 原始编码 | fixed | 降级判据覆盖证据达标类取值，并把 BH-FDR/DSR 接进 statistically_dead | 降级集扩为 EVIDENCE_ADEQUATE_VERDICTS（含 blocked_pending_audit）；统计 PASS 时按 BH 未显著或 DSR 不达标判 dead | test_f007_canonical_registry.py::test_finalize_downgrades_evidence_adequate_when_stats_incomplete | 1 | 2 | wired-but-ineffective |
| R1-102 | DSR/MinTRL 缺失或估计器异常时 cohort 统计仍判 PASS | 高 | 正确性 | 根因 | 原始编码 | fixed | 三条缺失路径一律 INCOMPLETE + reason | 无 p 值/无可算 Sharpe/最佳成员 DSR 异常/MinTRL 异常四条路径一律 INCOMPLETE | test_f007_controls.py::test_finalize_wires_cohort_level_multiplicity | 1 | 2 | fail-open-on-missing-metric |
| R1-103 | 多标的面板被当单条时间序列跑成本，裁决依赖 CSV 行序 | 高 | 正确性 | 症状 | 原始编码 | partial | 面板去重排序 + 按 symbol 分组聚合，或多标的 fail-closed | load_unified_panel 强制 (time,symbol) 唯一并按 (symbol,time) 排序；行序依赖闭合，拼成单条序列的部分转 R2-209 | test_unified_panel.py::test_panel_loading_is_independent_of_csv_row_order | 1 | 2 | panel-treated-as-series |
| R1-104 | AC-013 的评测面回写无生产入口，跨 cohort 查重比较集恒为空 | 高 | 正确性 | 根因 | 原始编码 | fixed | finalize 后调 writeback + 变异证据 | finalize_cohort 写出 verdict 后调用 writeback_evaluation_face | test_f007_canonical_registry.py::test_finalize_wires_cohort_dedup_and_overrides_verdict | 1 | 2 | implemented-not-wired |
| R1-105 | 零字节 claim 文件让 acquire/recover/release 全抛未映射异常 | 高 | 正确性 | 根因 | 原始编码 | fixed | read_claim 容错 + 生产接 recover | read_claim 对损坏内容返回 None；recover 把损坏文件当失效锁接管 | test_f007_concurrency.py::test_crashed_holder_is_always_recoverable | 1 | 2 | crash-window-loss |
| R1-106 | preview 的 NFR-003 泄漏守卫作用在自造两键字典上，恒真 | 高 | 正确性 | 根因 | 原始编码 | fixed | 校验 to_payload() 全量并递归扫描 | assert_no_canonical_leak 递归扫描嵌套键；preview 改校验 result.to_payload() | test_f007_execution_tiers.py::test_agent_readable_payload_rejects_nested_final_window_fields | 1 | 2 | guard-on-synthetic-input |
| R1-107 | 唯一质量门禁与 CI 不运行 contract/property/mutation 三个测试目录 | 高 | 测试覆盖 | 根因 | 流程缺陷 | fixed | verify.py 加入三个目录 | verify.py pytest 步骤加入三个目录（67 用例此前从未被门禁执行） | tools/verify.py（门禁本体） | 1 | 2 | evidence-outside-the-gate |
| R1-108 | synthesis 缺有效独立数、用 finalize 前 verdict、漏斗第一级恒零 | 中 | 正确性 | 根因 | 契约漂移 | fixed | 补 effective_trials / 读 verdict members / CLI 传事件 | effective_trials 进 semantic_payload；cohort 段改读 verdict.members；CLI 增 --generation-events | test_f007_controls.py::test_synthesis_carries_effective_trials_and_final_verdicts | 1 | 2 | derived-view-drift |
| R1-109 | _comparable 与 max_abs_rho 契约矛盾，单个跨窗口成员拖垮整个 cohort | 中 | 正确性 | 根因 | 原始编码 | fixed | 跳过不等长口径而非抛错 | max_abs_rho 逐口径跳过；删除 _comparable，decide_dedup 捕获 DedupError 跳过 | test_f007_canonical_registry.py（跨窗口成员用例） | 1 | 2 | guard-contract-mismatch |
| R1-110 | block_size == 序列长度时 bootstrap CI 零宽且 excludes_zero=True | 中 | 正确性 | 根因 | 原始编码 | fixed | 强制 block_size < len(series) | block_size 约束收紧为 [1, len-1] | test_required_statistics.py::test_block_bootstrap_rejects_invalid_parameters | 1 | 2 | degenerate-ci-reads-as-significant |
| R1-111 | p 值/收益/相关性成员对齐丢失，fdr_alpha last-wins，ρ 取 max | 中 | 正确性 | 根因 | 原始编码 | fixed | 改按 candidate_id 映射；alpha 冲突即拒绝；ρ 取均值 | 改 candidate_id 映射；alpha 集合>1 即 CanonicalOpError；相关性改两两均值 | test_f007_canonical_registry.py::test_finalize_rejects_conflicting_member_fdr_alpha | 1 | 2 | silent-overwrite |
| R1-112 | 证据文件不可读被静默吞掉，成员逃过查重且仍 PASS | 中 | 正确性 | 根因 | 原始编码 | fixed | 写 gate_rejected 并标 INCOMPLETE | 写 gate_rejections.jsonl 事件并把 cohort 统计强制 INCOMPLETE | test_f007_canonical_registry.py::test_unreadable_evidence_marks_cohort_incomplete_and_records_rejection | 1 | 2 | fail-open-on-unreadable-evidence |
| R1-113 | 事件链状态不自洽（INCOMPLETE 后接 EVIDENCE_READY→REGISTERED），迁移表零调用者 | 中 | 正确性 | 根因 | 原始编码 | fixed | from_state 取实际终态 + assert_transition 校验 | registered_events 取实际终态；_run_events 与登记事件均过 assert_transition | test_f007_atomic_publish.py::test_registered_event_uses_actual_terminal_state_and_validates_transition | 1 | 2 | implemented-not-wired |
| R1-114 | 复用分支可返回另一份信号的已发布结论 | 中 | 正确性 | 根因 | 原始编码 | fixed | 复用前比对信号 digest | manifest 记录 signal_digest，复用前比对 | test_f007_cli.py::test_canonical_reuse_rejects_different_signal_input | 1 | 2 | identity-misses-input |
| R1-115 | int 5 与 float 5.0 得到不同 experiment_id | 中 | 正确性 | 根因 | 原始编码 | fixed | normalize_numbers 对 int 同样定标 | normalize_numbers 对 int/float 统一走 decimal_text（bool 仍原样） | test_identity.py::test_normalize_numbers_scales_ints_and_floats_alike_but_keeps_bools | 1 | 2 | identity-instability |
| R1-116 | 测试夹具手工注入 promising，掩盖 R1-101 | 中 | 测试覆盖 | 根因 | 流程缺陷 | fixed | 起点改生产可达取值或显式 xfail | 夹具起点改为生产可达的 blocked_pending_audit | test_f007_canonical_registry.py::test_finalize_wires_cohort_dedup_and_overrides_verdict | 1 | 2 | test-simulates-itself |
| R1-117 | write_definition_face 是只有测试调用的陷阱函数 | 中 | 测试覆盖 | 症状 | 流程缺陷 | fixed | 删除或说明真实越权入口 | 删除该函数，定义面字段由 assert_payload_is_dr008 显式拒绝 | test_f007_registry_writeback.py::test_definition_face_payload_is_rejected_and_definitions_untouched | 1 | 2 | test-simulates-itself |
| R1-118 | abandon 丢弃 observed_at，用 assert moment 掩盖未使用变量 | 低 | 正确性 | 根因 | 原始编码 | fixed | 加 occurred_at 或删参数 | 删除未使用的 observed_at 参数与 assert | test_f007_cli.py（abandon 既有断言） | 1 | 2 | — |
| R1-119 | register_rejection 返回类型注解 CanonicalResult 与实际返回 Path 不符 | 低 | 质量 | 根因 | 原始编码 | fixed | 注解改 Path；评估加类型检查门 | 注解改为 Path | —（ruff 覆盖） | 1 | 2 | — |
| R1-120 | 非法 recorded_at 抛裸 ValueError，read_ledger 的 except 接不住 | 低 | 正确性 | 根因 | 原始编码 | fixed | 重抛为 HoldoutBudgetError | __post_init__ 捕获并重抛 HoldoutBudgetError | test_f007_canonical_registry.py::test_ledger_invalid_recorded_at_is_mapped_to_holdout_error | 1 | 2 | — |
| R1-121 | assert_projection_rebuilds 的确定性断言不可能失败 | 低 | 测试覆盖 | 症状 | 原始编码 | fixed | 改真实往返断言 | 改为先删派生索引、再要求投影与删除前相等且索引确已删除 | test_f007_canonical_registry.py::test_finalize_records_counts_and_projection_rebuilds | 1 | 2 | test-asserts-weaker-property |
| R2-201 | finalize 把本 cohort 回写进评测面，二次 finalize verdict 不一致 | 高 | 正确性 | 根因 | 修改引入 | fixed | _load_registry 排除当前 cohort 并补两次 finalize 相等的回归测试 | load_registry 增 exclude_cohort_id | test_f007_canonical_registry.py::test_finalize_is_stable_after_writeback_records_own_cohort | 2 | 3 | write-then-reread-own-output |
| R2-202 | 单写者接管非原子：三版实现（unlink→acquire / rename 移开 / .takeover 哨兵）均可致两进程同时持有 | 高 | 正确性 | 根因 | 修改引入 | fixed | （2 轮）rename+O_EXCL 或 compare-and-swap →（4 轮）改用 fcntl.flock，内核在进程死亡时自动释放 | 放弃「哨兵文件 + 内容回读持有者身份」形态，改用 flock(LOCK_EX\|LOCK_NB) 锁 <key>.claim.lock；acquire/release/recover 全部在同一临界区内串行，锁文件只创建不删除 | test_f007_concurrency.py::test_single_writer_invariant_holds_when_takeover_is_preempted | 2 | 5 | exclusive-create-then-write-identity |
| R2-203 | finally 内 release 抛错吞掉已成功的 canonical 结果 | 中 | 正确性 | 根因 | 修改引入 | fixed | finally 内释放改尽力而为 + 记事件 | finally 改用 _release_quietly（suppress ClaimBusyError） | test_f007_cli.py::test_canonical_succeeds_even_if_release_fails | 2 | 3 | cleanup-masks-result |
| R2-204 | 身份规范化口径变更未升 CONTEXT_SCHEMA_VERSION | 低 | 正确性 | 根因 | 修改引入 | partial | 升版 + ADR 记变更 | 升为 2、SUPPORTED_CONTEXT_SCHEMA_VERSIONS=(1,2)、ADR-0006 追加说明；「v1 按 v1 读取」的注释部分转 R3-302 | test_identity.py::test_context_schema_version_bumped_and_v1_still_readable | 2 | 3 | identity-change-without-version-bump |
| R2-205 | DSR 判死阈值硬编码为 1 − fdr_alpha，与 FR-004「阈值由预注册配置持有」冲突 | 中 | 正确性 | 根因 | 契约漂移 | fixed | 从预注册 multiplicity 取独立 dsr_threshold | dsr_threshold 取自 method_config.normalized.multiplicity，缺省即 INCOMPLETE | test_required_statistics.py::test_cohort_statistics_requires_preregistered_dsr_threshold | 2 | 3 | threshold-hardcoded-in-evaluator |
| R2-206 | 最佳成员 Sharpe<=0 判 INCOMPLETE，把「有结论的负结果」报成「测不出来」 | 中 | 正确性 | 根因 | 修改引入 | fixed | MinTRL 记 not_applicable，统计保持 PASS，成员走 dead | 按建议实现，成员经 statistically_dead 走 dead | test_required_statistics.py::test_negative_best_sharpe_is_pass_with_nontrl_not_applicable_and_dead | 2 | 3 | negative-result-reported-as-incomplete |
| R2-207 | 仅部分成员缺 p 值时 cohort 统计仍 PASS | 低 | 正确性 | 根因 | 原始编码 | fixed | p 值键集合须覆盖全部终态成员 | required_candidates 覆盖不全即 INCOMPLETE | test_required_statistics.py::test_cohort_statistics_requires_p_values_for_all_members | 2 | 3 | fail-open-on-missing-metric |
| R2-208 | 旧 manifest 缺 signal_digest 时静默跳过复用校验 | 低 | 正确性 | 症状 | 修改引入 | fixed | 缺字段即拒绝复用；拒绝路径也写该字段 | 缺字段即 E_INPUT_INVALID；register_rejection 的 manifest 也写 signal_digest | test_f007_cli.py::test_canonical_reuse_rejects_manifest_without_signal_digest | 2 | 3 | backward-compat-silently-skips-guard |
| R2-209 | 多标的面板仍被拼成单条序列：排序后时间戳回跳，跨标的边界产生虚假换手 | 高 | 正确性 | 根因 | 原始编码 | fixed | 按 symbol 分组聚合；曲线对非单调 times 失败关闭 | evaluate_fixture 按 timestamp 聚合出组合序列供成本/稳定/曲线用、按 symbol 分组汇总交易摘要；build_equity_curves 对非单调时间轴 CurvesError | test_unified_panel.py::test_panel_evaluation_groups_by_symbol_and_has_monotonic_times | 2 | 3 | panel-treated-as-series |
| R3-301 | 面板交易摘要按标的求和、而曲线与逐期收益按标的取均值，两份已发布证据标度不一致 | 中 | 正确性 | 根因 | 修改引入 | fixed | 统一为等权组合口径并补同标度断言 | _panel_trade_summary 的 gross_return/turnover 改为按标的取均值 | test_unified_panel.py::test_panel_evaluation_groups_by_symbol_and_has_monotonic_times | 3 | 4 | mixed-aggregation-scales |
| R3-302 | experiment_context 注释声称 v1 产物按 v1 读取，但规范化未按版本分支 | 低 | 质量 | 根因 | 修改引入 | fixed | 改注释或实装版本分支 | 注释与 ADR-0006 改为「v1 仅保留可构造性，历史 ID 不可复算」 | test_identity.py::test_context_schema_version_bumped_and_v1_still_readable | 3 | 4 | comment-overclaims-behavior |

### 循环 16 模式教训

- **本轮最大模式：`wired-but-ineffective`——循环 15 `implemented-not-wired` 的下一层。** 循环 15 修好了「必需统计没有任何生产调用者」，本轮发现它被接进了一条**生产上不可达的分支**：`canonical_ops` 只在 `promotion_verdict == "promising"` 时按统计降级，而 v0.2 的 L2/L3 恒为 `not_yet_available`，导出优先级表在第 5 级就返回 `blocked_pending_audit`，`promising` 永不出现。**净效果与修复前相同，只是这次有调用栈。** 教训：验收「已接线」不够，必须验收「该分支在生产配置下可达」——变异证据要跑在生产口径的输入上，而不是夹具手工注入的状态上。
- **`exclusive-create-then-write-identity`：同一形态连吃 4 次。** `R1-105`（`.claim` 先 `O_EXCL` 创建后写内容 → 崩溃留空文件 → 永久堵死）与 `R2-202` 的三版修复（`unlink→acquire` 非原子 / `rename` 移走的是"路径上任何文件"而非校验过的那个 / `.takeover` 哨兵**从未写入 pid**，实测恒为 0 字节，人人可回收）本质是同一个洞：**「创建」与「写入身份」之间必然存在一个"文件已存在但不可识别"的窗口，而所有恢复逻辑都把"不可识别"当成"可回收"。** 直到第 4 轮停下来命名这条存疑假设、第 5 轮换成 `flock`（内核在进程死亡时自动释放，无空文件状态，不需要任何回收启发式）才关闭。**教训：同一 finding 第 3 次修复失败时，要质疑的是形态/抽象，不是这一版代码。**
- **`test-simulates-itself` ×3（R1-116、R1-117、R2-202 的哨兵测试）。** 三次都是测试**手写了生产代码产生不出的状态**再去断言它——`promotion_verdict="promising"` 手工注入、`write_definition_face` 只有测试调用、`guard.write_text(json.dumps({"pid": os.getpid()}))` 而生产路径从不写该内容。这类测试全绿，却把它要保护的缺陷一路放行。**判据：写完一条测试，先问"生产代码能不能产生我 setup 里这个状态？"**
- **`origin` 分布（32 条）**：`original-coding` 19 / `fix-regression` 8 / `process-gap` 3 / `spec-drift` 2。**自伤率 25%（8/32）**，正好落在 skill 经验的 20–30%——与循环 15 的「0 自伤」形成对比，原因是循环 15 的修复集中在「接线」这类二值可验证动作，而本轮涉及并发、聚合口径与身份规范化等语义改动。**这正是"最低 2 轮"不能省的实证：这 8 条在第 1 轮物理上不存在。**
- **存活轮数**：最长 `R2-202`（2→5，存活 3 轮），且它是唯一触发升级协议的条目；`R2-209`（2→3）与 `R3-*`（3→4）次之；第 1 轮 21 条除 `R1-103` 外全部 1→2。**收敛慢的条目 100% 集中在并发语义上**，与"纯函数正确性易收敛、副作用与时序难收敛"的直觉一致。
- **门禁覆盖面本身是一等缺陷（R1-107）**：`tools/verify.py` 的 pytest 步骤写死 `tests/unit tests/integration`，而 CI 只调用它——`tests/contract`（AC-008/011/012 引用的验收证据）、`tests/property`、`tests/mutation`（门禁变异证据）共 67 个用例**从未被任何自动门禁执行过**，却被 spec 的 AC 行当作证据引用。**教训：AC 引用的测试路径，应由脚本校验它确实在门禁的执行集合内，而不只是"文件存在"。**
- **回归测试的交错覆盖**：`R2-202` 三次修复的回归测试都选了"安全的那一种交错"（对手在移锁之后到达），因此每次都绿。第 5 轮改为**先写出违反不变量的交错**（接管者在判定后、替换前被抢占）让它红，再换实现。**并发类 finding 的回归测试必须从"能让不变量失败的交错"写起。**

### 循环 16 裁决分布与建议命中率

- **裁决分布**：32 条中 accepted 30、partial 2（`R1-103`、`R2-204`，两条的剩余部分都指定了载体 `R2-209`/`R3-302` 并各自关闭）、rejected 0。无一条被"部分接纳"蒸发。
- **建议命中率**：`suggested_fix` 与 `fix_summary` 实质一致 29/32（≈91%）。三条不一致：`R1-103`（建议"或多标的 fail-closed"，实际走了聚合路线）、`R1-117`（建议二选一，实际选了删除）、**`R2-202`（建议在第 2、3 轮两次落空——rename/CAS 方向本身就是错的形态，直到第 4 轮改提 `flock` 才命中）**。后者说明：**建议命中率高不等于建议质量高，最贵的那条恰恰是建议连错两轮的那条**；当同一条 finding 的建议连续落空时，检视方应当怀疑自己的方案空间而不是修复方的执行。
- **角色合并的效果**：`R2-202` 在对抗式分离循环下 3 轮未收敛，角色合并后 1 轮关闭。与 skill 记录的经验一致（分离循环在 4-5 轮修复声明里零自行收敛）。

## 循环 17：F008 宇宙扩容与 point-in-time 宇宙台账 规格文档检视

- report_type: doc-review | round: 1（full-scan）→ 2（diff-only）→ 3（diff-only，裁决后） | 状态: 闭环
- 日期：2026-09-19 | 基线：`7872666`（F008 `draft`）→ 终基线 `619dadc`（worktree `feat/F008-universe-expansion`，PR #3，CI 35447503084 绿）
- 检视人：Claude Opus 5（第 2/3 轮按 skill §7 角色合并下场修复）| 裁决：owner（artifact 格式、台账语义、准入通道、前视处理四条）
- 范围：`docs/features/0.2/F008-universe-expansion/` 三件套，及其与 ADR-0007 / 架构 §4.3 / F007 DR-006 / 已落地的 `factor_factory/generators/universe.py` 的契约一致性
- 结论：24 条（6 高 / 12 中 / 6 低），全部关闭；其中 4 条为修复引入（`fix-regression`，自伤率 4/12 ≈ 67% 按轮次内新发现计）。3 条 High 属"规格本身矛盾"，按 skill §7 升级为规格裁决，冻结修复直至 owner 拍板。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| universe-artifact-format-conflict | universe artifact 规定为 CSV 富列，但已落地的下游消费者只接受严格 JSON schema | 高 | 正确性 | 根因 | 跨 feature 契约漂移 | fixed | 在 spec IR-002 与 design §3 冻结 artifact 的确切 schema（键集合、类型、digest 前缀、文件扩展名），二选一：对齐既有实现改为 JSON 最小 PIT 投影（{schema_version, members[{lake_pair, valid_from, valid_to}]}），或走规格裁决同时改 ADR-0007/F007 DR-006/F003 universe.py | artifact 载体裁决为 canonical JSON：spec IR-002 冻结顶层/成员严格键集合、排序与 `sha256:` 前缀；design §3 整段重写并声明与 `load_explicit_universe` 逐字段一致；ADR-0007 补 2026-09-19 修订记录；架构 §4.3、F007 spec DR-006/design §4 路径同步 `.csv`→`.json` | tools/check_doc_consistency.py::architecture_universe_calendar_split_aligned（断言已同步为 <digest>.json，门禁通过）；实现期由 AC-009/T009 的“产物可被 load_explicit_universe 加载”锁定 | 1 | 2 | cross-feature-contract-drift |
| quality-gate-not-actually-gating-export | “质量门是导出清单唯一准入通道”在 F002 现状下不可实现，回填写库即自动准入 | 高 | 正确性 | 根因 | 契约漂移 | fixed | 先定义“导出清单”的实体载体（新增准入表或 registry 侧 pair 过滤），并显式声明它是否触碰 F002 exporter/symbol_map——若必须改，把“不改 F002 已冻结语义”的约束改写为“只在 pair 选择处插入过滤，不动 manifest/对账/修订语义”，并为“未过门 pair 不得出现在导出 manifest.pairs 与 symbol_map”补一条 AC | 裁决：在导出侧 pair 选择处过滤——`lake_pairs_map` 加可选 `admitted` 参数（默认 None 保持现行为），导出清单定义为「台账可交易 ∩ 质量门 ACTIVE」的联合导出，无独立实体；`symbol_map` 不过滤、保持全量，与导出清单允许不等 | AC-009/T017 — tests/integration/test_f008_export_integration.py（含 admitted=None 与 F002 现状逐字节一致、symbol_map 全量两条断言） | 1 | 3 | gate-without-teeth |
| valid-from-semantics-conflict | 台账 valid_from 有三种互斥语义（准入时间/真实上市时间/实际数据起点） | 高 | 正确性 | 根因 | 原始编码 | fixed | 明确台账区间的被定义对象是“研究宇宙成员资格”还是“标的可交易期”；若是前者，§5 状态机保留“准入时点写 valid_from”，把真实上市时间放独立列 listed_at；若是后者，改写 §5 并说明未过门 pair 也会出现在 universe_at(T) 结果里 | 裁决：台账区间 = 标的可交易期（valid_from=上市 / valid_to=退市），准入状态拆到质量门判定记录（DR-004）；§5 状态机改写为两条独立时间线，DR-002 的 reason 收敛为 listed/delisted/initial_seed | AC-007/AC-008 — tests/unit/test_f008_membership.py | 1 | 3 | ambiguous-key-semantics |
| universe-selection-lookahead | 按快照时点成交额排名选 40 对再回填历史，宇宙成员本身带前视选择偏差，spec 未承认 | 高 | 正确性 | 根因 | 原始编码 | fixed | 在 §1 与 NFR-003 显式区分两类偏差——本 feature 消除的是“成员区间”偏差，未消除的是“成员选取”偏差；要么把残余偏差写成已知限制并给出后续（按滚动窗口逐期重算排名的 PIT 宇宙），要么把 criteria 改为逐期重算并相应改 universe_id 语义 | 裁决：承认为已知限制——§1 问题、§3 非目标、NFR-003 均写明「消除成员区间偏差、不消除成员选取偏差」，并要求下游把「按 frozen_at 排名选取的 40 对宇宙」作为结论前提标注；逐期重算列入 tasks §5 后移 | 无代码回归（文档约束）；下游标注由 F003 运行记录的 universe 字段承载 | 1 | 3 | survivorship-bias-residual |
| ir001-ir003-no-acceptance | IR-001（CLI 五子命令与拒绝条件）与 IR-003（schema_version）无任何 AC 覆盖 | 高 | 测试覆盖 | 根因 | 原始编码 | fixed | 新增 AC-012 (IR-001) 覆盖五个子命令与四类启动期拒绝（tests/unit/test_f008_cli_contract.py，该文件已被 T018 引用但不挂任何 AC），新增 AC-013 (IR-003) 覆盖 schema_version 存在性与版本不符时拒绝加载 | 新增 AC-012（CLI 五子命令 + 五类启动期拒绝各以可区分非零原因退出）与 AC-013（schema_version 与未知键拒绝）；T018 挂 AC-012，design §8 测试映射同步 | AC-012 — tests/unit/test_f008_cli_contract.py；AC-013 — tests/unit/test_f008_artifact.py | 1 | 2 | requirement-without-ac |
| missing-test-group | tasks.md 缺 [TEST] 旅程验收组，design 自己声明它是开工门禁 | 高 | 测试覆盖 | 根因 | 流程缺陷 | fixed | 在 tasks.md §3 增加 “### [TEST] 组：层 2 旅程验收轨（必填）”，按 US-001~US-004 各派生 ≥1 条端到端断言（参照 F003 T036-T038 / F007 T029-T031 的写法），并在 §0 补一条执行规则说明“编写早、执行晚” | tasks §3 末尾新增 [TEST] 组 T030–T033，按 US-001~US-004 各一条端到端验收；§0 补“编写早执行晚”执行规则，§4 补 T004..T018 → T030..T033 依赖 | tools/check_task_dag.py（通过）；组内四条各自的 pytest verify 命令 | 1 | 2 | marked-ready-not-gated |
| schema-version-no-carrier | IR-003 要求台账带 schema_version，但 canonical CSV 格式里没有承载位置 | 中 | 正确性 | 根因 | 原始编码 | fixed | 与 universe-artifact-format-conflict 一并裁决：JSON 方案天然有 top-level schema_version；若坚持 CSV，需明确它是表头注释行、独立列还是旁车 JSON，并写进 canonical 字节定义（会影响 digest） | JSON 顶层整数字段 `schema_version` 承载，且参与 canonical 字节因而参与 digest；IR-003 补“加载方校验版本不符即拒绝” | AC-013 — tests/unit/test_f008_artifact.py | 1 | 2 | — |
| digest-prefix-undefined | digest 是否带 sha256: 前缀未定义，与既有实现不一致会直接导致引用解析失败 | 中 | 正确性 | 根因 | 契约漂移 | fixed | 在 FR-006/IR-002 写死 “digest = 'sha256:' + hexdigest，且前缀进文件名”，与 data_bridge/symbol_map.py:124 的 content_digest 和 factor_factory/canonical.py:39 的 sha256_prefixed_bytes 对齐 | spec FR-006/IR-002 与 design §3 写死 `digest = "sha256:" + hexdigest` 且前缀进文件名，并标注与 symbol_map.content_digest / canonical.sha256_prefixed_bytes 同一约定 | AC-009 — tests/integration/test_f008_export_integration.py | 1 | 2 | cross-feature-contract-drift |
| duplicate-key-check-unverified | FR-004 列出“重复主键”检查项，但 AC-005 只覆盖三类 fixture，重复主键无验收 | 中 | 测试覆盖 | 根因 | 原始编码 | fixed | AC-005 的 fixture 扩到四类（缺失率/边界未闭合/连续聚合不一致/重复主键），或把“重复主键”从 FR-004 移除并说明由 F002 既有对账保证 | AC-005 fixture 由三类扩到四类（含重复主键），T015 口径同步为四项，design §8 映射同步 | AC-005 — tests/integration/test_f008_quality_gate.py | 1 | 2 | requirement-without-ac |
| row-count-inconsistent | 回填行数 4200 万与 4600 万在同一份 spec 内混用 | 中 | 质量 | 根因 | 原始编码 | fixed | 统一为 “40 对外推约 4200 万行（PRD FR1.5 的 4600 万对应约 44 对）”，把 US-002 与 §7 依赖两处的 4600 万改掉或显式标注为 PRD 原值 | US-002 与 §7 依赖两处 4600 万改为 4200 万；PRD 的 4600 万在 §7 决策表保留并标注为约 44 对口径 | tools/check_doc_consistency.py（通过） | 1 | 2 | — |
| capacity-gate-not-quantified | “实测显著劣于外推必须报告”没有量化阈值，AC-011 无法成为可断言门禁 | 中 | 测试覆盖 | 根因 | 原始编码 | fixed | 给 NFR-005 一个数值判据（如“实测导出耗时 > 外推值 1.5 倍或 > 40min 即判红”），让 tests/integration/test_f008_capacity_report.py 有可失败的断言，而不是只落盘记录 | NFR-005 补量化判红阈值：导出耗时 > 外推值 1.5 倍（> 38min）或磁盘/NAS 文件数 > 1.3 倍即判不可接受 | AC-011 — tests/integration/test_f008_capacity_report.py | 1 | 2 | gate-without-teeth |
| wrong-task-references | 三处引用了错误的任务号（T022/T024），真正的容量实测是 T023/T026 | 中 | 质量 | 根因 | 原始编码 | fixed | spec §7「为什么不是 50 对」的 “若 T022 实测余量充足” 与 design §9 同句改为 T023；tasks §5 的 “视 T024 的实测余量” 改为 T023/T026 | spec §7「为什么不是 50 对」与 tasks §5 的 T022/T024 均改为 T023/T026（复核发现 design §9 并无该引用，首轮 location 记宽） | tools/check_task_dag.py（通过） | 1 | 2 | — |
| reachability-criterion-orphan | T019 引入 spec 未定义的筛选口径“≥30 笔/90 天可达性” | 中 | 正确性 | 根因 | 契约漂移 | fixed | 该参数属 F003 objective 的 reachability_min_trades_90d；要么把它作为 criteria 的第五项写进 FR-001/DR-001（并进 universe_id），要么把 T019 的复核口径改为“人工确认排名与排除规则”，不引入未入档阈值 | T019 的复核口径改为“逐候选核对成交额排名、上线天数与排除原因均按 DR-001 入档”，移除未入档的「≥30 笔/90 天」阈值 | AC-001 — tests/unit/test_f008_discover.py | 1 | 2 | — |
| disk-precheck-not-in-spec | “磁盘余量不足即启动期拒绝”只在 design/tasks 出现，spec 无对应需求 | 低 | 正确性 | 根因 | 契约漂移 | fixed | 在 FR-003 或 IR-001 补一句“启动期校验磁盘余量，不足以非零退出拒绝”，使 T018 的该项断言有需求锚点 | FR-003 补“启动期校验磁盘余量，不足即非零退出拒绝”，AC-012 覆盖该拒绝路径 | AC-012 — tests/unit/test_f008_cli_contract.py | 1 | 2 | — |
| dr002-missing-ingested-at | DR-002 的字段元组缺 ingested_at，design §3 却把它列为表列 | 低 | 质量 | 根因 | 契约漂移 | fixed | 把 ingested_at 补进 DR-002 的字段列表并说明 bitemporal 用途，或从 design §3 移除 | DR-002 字段元组补 `ingested_at` 并说明 bitemporal 用途；同时补“湖内快照只含最小 PIT 投影” | tools/validate_spec_lifecycle.py（通过） | 1 | 2 | — |
| t008-verify-mismatch | T008（补 initial_seed 台账）的 verify 指向导出集成测试，与任务内容不匹配 | 低 | 质量 | 根因 | 原始编码 | fixed | verify 改为 tests/unit/test_f008_membership.py（或新增 initial_seed 专项断言），导出集成测试留给 T009/T017 | T008 的 verify 由 test_f008_export_integration.py 改为 tests/unit/test_f008_membership.py | tools/check_task_dag.py（通过） | 1 | 2 | — |
| decision-table-duplicated | spec §7 与 design §9 决策表六行几乎逐字重复，双份维护易漂移 | 低 | 质量 | 根因 | 原始编码 | fixed | spec §7 保留产品层取舍（规模/阈值/退市处理），design §9 只保留技术取舍（artifact vs dataset、真相源位置、行数豁免），重复项改为单向引用 | design §9 的「规模与阈值」「退市 pair」两行改为引用 spec §7（产品取舍唯一拥有者），design 只留技术侧含义 | tools/check_doc_consistency.py（通过） | 1 | 2 | — |
| export-manifest-term-undefined | “导出清单”作为核心术语全文使用但未定义载体 | 低 | 质量 | 症状补丁 | 原始编码 | fixed | 随 quality-gate-not-actually-gating-export 一并定义；在 design §3 增加该载体的存储形态与唯一写入者 | 随准入通道裁决一并定义：导出清单 = 台账可交易 ∩ ACTIVE 的联合查询结果，无第三实体；写入 spec FR-006 与 design §3 | AC-009 — tests/integration/test_f008_export_integration.py | 1 | 3 | — |
| r001-backfillrun-missing-schema-version | IR-003 要求运行记录带 schema_version，DR-003 的字段清单没有它 | 中 | 正确性 | 根因 | 原始编码 | fixed | 在 DR-003 补 schema_version 字段并让 AC-013 一并断言 | DR-003 字段清单补 `schema_version`（引 IR-003），AC-013 的断言对象由 artifact 扩到 artifact + BackfillRun | AC-013 — tests/unit/test_f008_artifact.py | 2 | 2 | — |
| r002-ac013-wrong-test-path | 新增的 AC-013 断言 artifact 加载，测试路径却指向库侧 membership 套件 | 中 | 测试覆盖 | 根因 | 修复引入 | fixed | artifact 契约断言应落在 artifact 自己的测试文件 | AC-013 的 tests 改为 tests/unit/test_f008_artifact.py（新文件），design §8 映射、T009 与 T033 的 verify 同步补该路径 | tools/check_task_dag.py（通过） | 2 | 2 | ac-test-path-mismatch |
| r003-test-group-numbering-order | 新增的 [TEST] 组编号 T030–T033 排在 T024 之前，与“按顺序逐项实现”冲突 | 低 | 质量 | 根因 | 修复引入 | fixed | 新增任务块的位置应与编号单调一致 | 把 [TEST] 组整块移到 §3 末尾（T029 之后），并移除多余的「验收套件与质量门」分节标题 | tools/check_task_dag.py（通过） | 2 | 2 | — |
| r004-admission-written-as-ledger-time | US-003 场景 3 仍把准入写成「在台账登记生效时间」，与拆分后的语义冲突 | 中 | 正确性 | 根因 | 修复引入 | fixed | 语义拆分必须同步扫一遍所有引用旧语义的场景句 | 改为「写入准入记录（ACTIVE）并进入导出清单；台账区间由上市/退市事实决定，不因准入改写」 | AC-005 — tests/integration/test_f008_quality_gate.py | 3 | 3 | partial-symmetric-fix |
| r005-delist-vs-dropout-conflated | 「退市」与「跌出流动性阈值」被当成同一件事写进台账退出 | 中 | 正确性 | 根因 | 原始编码 | fixed | 可交易期与成员资格是两个谓词，退出路径也要分开 | 拆开——退市追加台账 valid_to(reason=delisted)；跌出阈值但仍可交易只在新版定义中落选并移出导出清单，台账区间不动。§3 边界场景、§5 状态机、§7 决策表与 Q-003 同步 | AC-007/AC-008 — tests/unit/test_f008_membership.py | 3 | 3 | ambiguous-key-semantics |
| r006-member-changed-event-ambiguous | universe.member_changed 在两条时间线拆分后无法区分变更来源 | 中 | 正确性 | 根因 | 修复引入 | fixed | 事件流承载两条语义线时必须带来源判别字段 | TR-001 payload 增 `line` 字段（tradability / admission）并各自限定 reason 取值；design 事件契约与幂等键同步加 line；AC-010 补可区分断言 | AC-010 — tests/integration/test_f008_backfill.py | 3 | 3 | — |

### 模式教训

**来源分布**：原始编码 13 / 契约漂移 5 / 修复引入 4 / 跨 feature 契约漂移 1 / 流程缺陷 1。

**反复出现的模式**（按 `pattern_tag` 聚合）：`cross-feature-contract-drift` ×2, `gate-without-teeth` ×2, `ambiguous-key-semantics` ×2, `requirement-without-ac` ×2, `survivorship-bias-residual` ×1, `marked-ready-not-gated` ×1, `ac-test-path-mismatch` ×1, `partial-symmetric-fix` ×1。

1. **文档写的契约 vs 代码已落地的契约**（`cross-feature-contract-drift` ×2）——本轮最贵的一条。
   ADR-0007、F007 DR-006、F008 IR-002 三份文档一致写 CSV，而下游 `generators/universe.py` 早已按
   JSON 落地并有通过的集成测试。**三份文档互相一致，不等于它们与代码一致**；跨 feature 契约检视
   必须去读消费方的实现，不能只做文档间比对。
2. **语义拆分的连带漏项**（`partial-symmetric-fix`、`ambiguous-key-semantics` ×2）——把 `valid_from`
   从"三义"收敛成"可交易期"后，第 3 轮仍在三处发现引用旧语义的句子（US-003 场景、"退市 vs 跌出阈值"
   混为一谈、`member_changed` 事件无法区分来源）。**改语义必须全文扫引用，不能只改定义处**。
3. **门禁把错误答案锁死**（`gate-without-teeth` ×2）——`tools/check_doc_consistency.py:63` 断言架构文
   必须含 `<digest>.csv`。门禁有牙是好事，但它锁的是"当时认为对的东西"；裁决改变契约时，门禁断言
   是联动修改清单的一部分，漏改则 verify 判红。另一条是 `NFR-005` 的"显著劣于外推"无量化阈值，
   写成了永远无法判红的门。
4. **需求写了但没有 AC**（`requirement-without-ac` ×2）——`IR-001`/`IR-003` 与"重复主键"检查项都在
   第 4 节有定义、在 tasks 有任务，唯独没进验收清单。`tasks.md` 里出现了一个不挂任何 AC 的测试文件
   （`test_f008_cli_contract.py`）是这类漏洞的可检信号。
5. **diff 复核的价值被证实**：三轮共 6 条轮次内新发现，4 条是 `fix-regression`——第 1 轮物理上不存在
   这些问题。最长存活 2 轮（valid-from-semantics-conflict、universe-selection-lookahead、quality-gate-not-actually-gating-export，均为待 owner 裁决项）。

**裁决分布**：accepted 24 / partial 0 / rejected 0。全接纳按 skill 的说法是"检视在凑数"的信号，
但本轮 18 条首轮发现中有 3 条直接改变了设计方向（artifact 格式、台账语义、准入通道），另有 6 条阻塞流转，
不属于凑数；无 rejected 更可能反映的是"检视方与修复方在第 2 轮后合并为同一角色"——**这本身是需要警惕的
制衡削弱**，下次同类检视若仍由同一 agent 双角色，应在报告里显式记录哪些条目被自己否决过。

### 过程事故：并行会话清空工作树

第 2 轮的 7 个文档改动（未提交）在 20:40 被另一个并行会话清理工作树（提交 `41c3911` 前）全部丢弃——
`git stash` 为空、不在任何 commit 中、无法从 git 恢复。改动靠会话内的替换脚本原样重放才找回。

**教训**：多会话并行改同一仓库时，未提交的工作树改动没有任何保护。重放后立即 `git add` 进 index
（能挡 `git checkout -- .`，挡不住 `git reset --hard`），并尽快落到独立 worktree 的分支上。
本次最终把 F008 文档收进 `feat/F008-universe-expansion` worktree，与 F003 的代码分支物理隔离。

## 循环 15：F009 Kronos 服务生命周期控制面端点 规格文档检视

- report_type: doc-review
- 周期：2026-09-20（3 轮 + 1 条跨会话补正；Round 1 全量扫描由独立会话完成，Round 2 full-scan 升级复核，Round 3 封顶 diff 复核）
- 状态：闭环（stop_condition_met: true，readiness: PASS）
- 基线：`main@8e85171` → 修复终态 `main@1d985d1`；契约修订 `57c9edb`；消费端 `feat/F003-alphagen-vendor@0ccf69e..ffdd805`
- 被检对象：`docs/features/0.2/F009-kronos-lifecycle-endpoints/{spec,design,tasks}.md` 及相邻契约（架构 §7.1、F003 客户端与契约测试、F004 基座与回归门、BACKLOG）
- 角色：Round 1 检视方为独立会话；Round 2/3 由修复方显式切换视角承接（每条修复以变异判红或门禁判红作为独立证据）

### 循环 15 完整 issue 表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首现轮 | 修复轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F009-R1-001 | 核心验收依赖的 GPU Kronos 基座并不存在 | high | correctness | root-cause | spec-drift | fixed | 纳入 GPU runtime 或建硬前置 Feature | owner 裁决立独立 F010；F009 声明硬前置，SC-005/AC-012 改先红态，新增 NFR-006 禁止以 CPU 通过充当证据 | 文档侧：BACKLOG F010 行 + 架构 §7.1 前置条 | 1 | 2 | cross-feature-contract-drift |
| F009-R1-002 | stop 不能形成稳定 stopped，下一次 predict 隐式重载 | high | correctness | root-cause | spec-drift | fixed | 重写期望态、准入与线性化设计 | 引入存储的 desired，state 改为 (desired, model_loaded) 的函数；FR-003 停机准入禁止隐式加载，走 F004 兜底且不标 kronos | 实现期载体 tests/unit/test_f009_stopped_admission.py（AC-003，要求 _load_predictor 调用次数为 0 + 变异判红） | 1 | 2 | state-derived-from-insufficient-fact |
| F009-R1-003 | E_TIMEOUT 后后台继续，状态机约束不了迟到副作用 | high | correctness | root-cause | original-coding | fixed | 定义进行中语义、动作仲裁和最终落点 | 架构 §7.1 + FR-006：单飞 + operation 台账；冲突立即 E_BUSY 不排队；E_TIMEOUT 明确为"仍在进行"，落点以 operation 转 null 为判据 | 实现期载体 tests/unit/test_f009_lifecycle_errors.py（AC-006） | 1 | 2 | timeout-late-side-effect |
| F009-R1-004 | 错误码与错误响应形态越过架构契约 | high | correctness | root-cause | spec-drift | fixed | 先在架构唯一化再同步三方 | 信封恰为单键、成功与错误互斥；读数不可得改由 vram_readable=false + vram_bytes=null 表达；restore 补 E_UNAVAILABLE | 文档侧：架构 §7.1 动作表 + IR-004 + design §4 | 1 | 2 | cross-feature-contract-drift |
| F009-R1-005 | mock 纳入契约后与权威范围及自身不变量冲突 | high | correctness | root-cause | spec-drift | fixed | 移出契约或单独定义 CPU 状态机 | 推翻早先 Q-002，改为 mock 不注册 /lifecycle/*（404）；裁决写入 §7 决策表与 §8 | 实现期载体 tests/integration/test_f009_lifecycle_deployment.py（AC-009） | 1 | 2 | cross-feature-contract-drift |
| F009-R1-006 | 下游 F003 无 restore 且用单一 10 秒超时 | high | correctness | root-cause | spec-drift | fixed | 补明确的跨 Feature 客户端交付边 | FR-009/AC-010 把客户端纳入验收；超时改分动作 5/60/120s（0ccf69e），restore 由循环 14 R012 落地 | tests/unit/test_f003_gpu_slot.py::test_each_lifecycle_action_uses_its_own_contract_timeout；test_f003_cli_contract.py::test_mine_restores_kronos_after_stopping_it | 1 | 2 | cross-feature-contract-drift |
| F009-R1-007 | 现有契约测试不能证明显存真实释放 | high | test-coverage | root-cause | process-gap | fixed | 强化真实下降/阈值断言并变异判红 | 判据改为「下降且卸载后整卡可用显存达到训练预算」，写进架构 §7.1、AC-012 与 design §8（首次落笔误写成已用侧，见 R2-005） | 实现期载体 tests/integration/test_f009_vram_release.py（见 R2-001 对落点的修正） | 1 | 2 | gate-weaker-than-claim |
| F009-R1-008 | status 的超时机制没有设计落点 | medium | correctness | root-cause | original-coding | fixed | 裁决 deadline owner 并补探测超时 | 三个超时一并纳入 FR-007 环境变量契约，design §4 接口表逐格列出 | 实现期载体 tests/unit/test_f009_vram_probe.py（AC-007） | 1 | 2 | mechanism-weaker-than-claim |
| F009-R1-009 | 显存探测可配置的契约不可实现也不可验收 | medium | correctness | root-cause | original-coding | fixed | 定义变量、值域、默认和非法值策略 | FR-007 明确变量名/值域/默认值/非法值启动期判红不回退；AC-007 覆盖 | 同上 | 1 | 2 | underspecified-config-contract |
| F009-R1-010 | status 始终可达与既有启动失败即退出冲突 | medium | correctness | root-cause | spec-drift | fixed | 区分启动失败与运行期 restore 失败 | design §7 显式区分：启动期预检失败进程退出（F004 不改）；运行期 restore 失败进程存活 + E_UNAVAILABLE | 实现期载体 tests/unit/test_f009_lifecycle_contract.py（AC-004） | 1 | 2 | cross-feature-contract-drift |
| F009-R1-011 | 空请求体和额外参数拒绝规则没有验收覆盖 | medium | test-coverage | root-cause | process-gap | partial | 补三类请求与错误信封断言 | FR-005/AC-005 覆盖空体、{}、含额外键三类；所用错误码的冲突另立 R2-003 | 实现期载体 tests/unit/test_f009_lifecycle_errors.py | 1 | 2 | acceptance-mapping-gap |
| F009-R1-012 | T022 指示人工改状态与派生账本 | medium | quality | root-cause | process-gap | fixed | 改用 sdd_status dry-run/advance | T025 明确经 sdd_status.py 流转，tasks §0 增"状态写入口唯一"纪律条 | 文档侧：tasks §0 与 T025 | 1 | 2 | manual-state-write |
| F009-R2-001 | AC-012 先红态放进 F003 的 0-xfailed 门禁文件，互相拆台 | high | correctness | root-cause | fix-regression | fixed | 显存断言移到独立载体 | 改落 tests/integration/test_f009_vram_release.py，spec/tasks 写明不得放进那个文件及原因；F003 侧一行未动 | 文档侧：AC-012 / T016 载体路径 + DAG 校验 | 2 | 2 | cross-feature-contract-drift |
| F009-R2-002 | 契约收紧了显存判据，唯一消费端没跟上 | high | correctness | root-cause | fix-regression | fixed | 客户端补预算阈值并读 vram_readable | vram_budget_gb 成无默认必填参数（由 vram_limit_gb 透传）；released 加预算条件；vram_readable=false 单列 vram_unreadable | tests/unit/test_f003_gpu_slot.py::test_release_requires_falling_below_the_training_budget / ::test_unreadable_vram_is_distinguished_from_not_released（双向变异判红） | 2 | 2 | cross-feature-contract-drift |
| F009-R2-003 | 额外请求参数复用 E_UNSUPPORTED_VERSION，与端点缺失判定混淆 | medium | correctness | root-cause | fix-regression | fixed | 契约补 E_BAD_REQUEST 并同步三方 | 架构 §7.1 补 E_BAD_REQUEST 与"错误码各司其职"条；F009 IR-004/FR-005/AC-005 与 design §4/§7 同步；check_doc_consistency 新增两条钉点 | tools/check_doc_consistency.py::kronos_lifecycle_contract_defined（变异判红：删分工条即红） | 2 | 2 | error-code-overloaded |
| F009-R2-004 | §5 状态机把"动作进行中被拒"画成 running→running | low | quality | root-cause | fix-regression | fixed | 改写状态机文本或加过渡态自环 | 拆为 running 自环（幂等/请求被拒）与过渡态自环（E_BUSY） | 文档侧：spec §5 | 2 | 2 | — |
| F009-R3-001 | 载体拆分打断 DAG：T022 的 verify 文件无生产者前置 | medium | correctness | root-cause | fix-regression | fixed | 补 T015 -> T022 边 | 拆开原 T015->T016->T022 三元链，显式补 T015->T022；F009 处于 doc-reviewing 不在 check_task_dag 强制作用域，verify.py 是绿的，只有手动跑 check_tasks 才看得到 | tools/check_task_dag.py::check_tasks 手动校验 | 3 | 3 | gate-scope-blind-spot |
| F009-R2-005 | 显存判据写成已用侧「降到训练预算之下」，与夜槽真正要判的方向相反 | high | correctness | root-cause | fix-regression | fixed | 判据改挂可用侧 | 架构 §7.1 与 F009 三件套统一为「读数真实下降，且卸载后整卡可用显存达到训练预算」（与取锁同阈值 vram_limit_gb）；实现本就是可用侧（vram_is_sufficient 判 free_gb >= limit），本条修的是契约措辞与实现之间的口径漂移 | tests/unit/test_f003_gpu_slot.py::test_release_requires_falling_below_the_training_budget | 2 | 2 | spec-impl-wording-drift |
| F009-R3-002 | spec §1/§3 残留"在旧文件补显存判据用例"的引用 | low | quality | root-cause | fix-regression | fixed | 与 AC-012/T016 的新载体口径对齐 | 两处改写并在 design §1 影响面同步注明拆分原因 | 文档侧 | 3 | 3 | — |

### 裁决记录

#1 · F009-R1-011 · partial · 覆盖面（空体 / `{}` / 含额外键）已由 FR-005 与 AC-005 补齐，接纳；但所用错误码与契约的端点缺失判定冲突，拒绝以当时形态关闭。剩余部分载体 = `F009-R2-003`（已于 Round 2 fixed）。· 裁决轮次 2

### 模式教训

- **`cross-feature-contract-drift` 占 18 条中的 6 条，且跨越了全部三轮**。Round 1 的 R1-001/004/005/006 是原始漂移；Round 2 的 R2-001/002 是**修复动作自己造出来的新漂移**——收紧了契约却没同步消费端、拆了载体却没同步另一个 feature 的门禁。结论：这个 feature 位于 F003/F004/架构三方接缝上，任何一侧的单边修改都会立刻产生漂移。**教训**：改契约的提交必须在同一轮内把三侧（契约正文 / 本 feature 文档 / 消费端实现）一起过一遍，不能"先改契约，消费端下轮再说"。
- **`fix-regression` 有 6 条（R2-001..004、R3-001..002），占总数三分之一**。这远高于循环 14 的 1/13。直接原因是本轮是 `rewrite` 而非打补丁——重写的自伤面天然更大。**因此 rewrite 裁决必须配套"升级 full-scan 的复核轮"**，diff-only 在重写场景下覆盖不住。Round 2 显式升级 full-scan 是正确的，Round 3 封顶轮仍抓到 R3-001 则说明封顶轮不是形式主义。
- **R3-001 暴露了一个门禁作用域盲区**（`gate-scope-blind-spot`）：`check_task_dag` 只对进入开发流转的状态生效，`doc-reviewing` 的 feature 不在作用域内。于是 `verify.py` 全绿，而 tasks 的 DAG 实际是断的。这不是门禁写错了——作用域设计有其理由（draft/doc-reviewing 期间 tasks 尚在变动）——但**文档检视轮必须手动对 tasks 跑一次 `check_tasks`**，不能以 verify.py 绿作为 DAG 无误的证据。建议写进 SOP 的文档检视清单。
- **R2-005 是一条「文档比实现更弱」的漂移**：8GB 卡上「已用 5GB」同时满足「低于 6GB 预算」和「取不到 6GB」——收紧 R1-007 的判据时把它写在了已用侧，而夜槽要判的是可用侧。实现（`vram_is_sufficient` 判 `free_gb >= limit_gb`）一直是对的，错的只有契约措辞，由并行会话在本循环收尾时发现并补正。**教训**：给判据加强度时必须同时问「这个量从哪一侧度量」，否则加的是一条看起来更严、实际判错方向的门。
- **`origin` 分布**：spec-drift 6、original-coding 3、process-gap 3、fix-regression 7。与循环 14（12 original-coding / 1 fix-regression）正好相反：代码检视面对的是"从没被看过的实现"，文档检视面对的是"反复被改的契约"，两者的主风险完全不同。
- **存活轮数**：R1 的 12 条均为 1→2（存活 1 轮），R2 的 4 条为 2→2，R3 的 2 条为 3→3。没有跨多轮悬而未决的条目，未触发不收敛升级协议。
- **裁决分布**：accepted 17 / partial 1 / rejected 0。**建议命中率**：18 条中 15 条 `fix_summary` 与 `suggested_fix` 实质一致；三条偏离都是往更彻底的方向走——R1-001 从"纳入或等待"具体化为立 F010 并配先红态纪律；R1-007 的判据同时写进了契约正文而不只是 AC；R2-003 的修复顺带给 `check_doc_consistency` 加了会判红的钉点。
- **跨循环联动**：R1-006 与循环 14 的 R012 是同一条缺陷的两半（restore 所有权 / 分动作超时），由两个独立视角分别发现——代码检视从实现侧撞上"停了不恢复"，文档检视从契约侧看出"客户端没有 restore 且超时口径错"。这条互证说明两类检视不是重复劳动。

## 循环 19：F009 Kronos 服务生命周期控制面端点 代码检视

report_type: code-review · feature: F009 · status: closed · rounds: 1（full-scan）→ 2（diff-only）→ 3（diff-only，封顶轮） · 收口 CI: 35995587247 绿

- 日期：2026-09-24 | 基线：`304b336`（F009 `code-reviewing`，分支 `feat/F009-kronos-lifecycle-endpoints`）→ 终基线见收口提交
- 检视人：Claude Opus 5（同会话内先实现后检视，按 skill §8 显式切换视角逐条独立核对）| 裁决：owner（AC-010 验收边界一条）
- 范围：源码 `lifecycle.py` / `lifecycle_api.py` / `lifecycle_config.py` / `vram.py` 四个新模块 + `kronos_real.py` / `server.py` / compose / `.env.example`，以及它们与架构 §7.1 生命周期契约的逐格一致性
- 结论：10 条（3 高 / 4 中 / 3 低），全部关闭；其中 1 条为修复引入（`fix-regression`，自伤率 1/4 = 25% 按第 2 轮新发现计）。1 条 High 属"规格自身不可满足"（AC-010 把验收挂在另一分支的文件上），按 skill §7 升级为规格裁决。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-001 | 未预期异常逃出控制器，客户端拿到 HTTP 500 而不是单键信封，且 status 随之不可达 | 高 | 正确性 | 根因 | 原始编码 | fixed | 动作执行器把非 LifecycleError 异常按动作映射成契约码并收敛 desired；status 的探测异常按"读数不可得"吞掉 | 映射 `ACTION_FAILURE_CODE`（stop→E_UNLOAD_FAILED / restore→E_UNAVAILABLE）+ 收敛 desired；`_probe` 吞异常记为不可读；`finally` 观测段改为不可抛（否则顶替原始异常且日志断线） | tests/unit/test_f009_lifecycle_errors.py::test_unexpected_exception_still_returns_contract_envelope、::test_status_stays_reachable_when_probe_raises | 1 | 1 | unhandled-path-escapes-contract |
| R1-006 | AC-010 把验收挂在 F003 分支的测试文件上，`code-reviewing` 状态下规格门禁必红 | 高 | 正确性 | 契约漂移 | 规格自身不可满足 | fixed | 把跨分支载体从 AC 的 tests 字段移出，改由本分支可跑的服务端侧契约载体承载，交付边记录留在 tasks | 拆验收边界（owner 裁决）：F009 新增 `SERVER_DEADLINES` / `client_deadline_floor()` 与 9 条断言只管服务端侧契约；客户端五项行为与变异判红仍由 `feat/F003-alphagen-vendor` 的 `test_f003_gpu_slot.py` / `test_f003_cli_contract.py` 承载，写进 AC-010 的边界说明 | tests/unit/test_f009_client_edge_contract.py（9 条） | 1 | 1 | cross-branch-evidence-unreachable |
| R2-001 | 卸载已成功、只是随后读状态失败时谎报 E_UNLOAD_FAILED 并停在 transitional | 高 | 正确性 | 根因 | **修复引入** | fixed | 把"报告失败"与"卸载失败"分开；兜底收敛按事实而不是按动作方向 | `_stop_worker` 的卸载后读数步骤自带 try（失败只让 `vram_bytes=None`，动作仍算成功）；兜底网改为 `_converge_after_failure`，按"模型是否还在内存里"收敛，读不到时取 fail-closed 一侧（绝不声称已卸载，否则夜槽取锁会 OOM） | tests/unit/test_f009_lifecycle_errors.py::test_reporting_failure_after_successful_unload_is_not_a_failed_unload | 2 | 2 | error-path-lies-about-irreversible-step |
| R1-002 | 冲突动作先做显存探测才判忙，探测卡住时 E_BUSY 会被拖到 probe_timeout | 中 | 正确性 | 根因 | 原始编码 | fixed | 把单飞判定移到探测之前：受理失败的路径不该碰设备 | 判忙前置；基线显存改在受理成功后才读（只服务日志行，不参与受理判定） | tests/unit/test_f009_lifecycle_errors.py::test_busy_is_immediate_and_does_not_touch_the_device | 1 | 1 | ordering-defeats-fast-path |
| R1-003 | 迟到标记 `_timed_out` 的读写有竞态，且竞态发生时 operation id 永久泄漏 | 中 | 正确性 | 根因 | 原始编码 | fixed | add/discard 一律在 `_meta_lock` 内，且仅当 operation 仍非空时登记迟到 | 迟到记账与 operation 读写同锁；`add` 前确认动作仍在飞 | tests/unit/test_f009_lifecycle_errors.py::test_timeout_keeps_background_running_then_operation_clears | 1 | 2 | unsynchronized-bookkeeping |
| R2-002 | 受理**之前**抛出的异常绕过控制器兜底网，端点仍会漏成 HTTP 500 | 中 | 正确性 | 根因 | 原始编码 | fixed | 在 wire 层收口这一类，而不是逐个路径堵漏 | wire 层加最后一道兜底（按端点映射 `ACTION_FAILURE_CODE`）；status 无失败码可用，改为如实降级 `model_loaded=false` / `device=unknown` / 读数不可得 | tests/unit/test_f009_lifecycle_errors.py::test_wire_layer_never_leaks_non_contract_response、::test_status_reports_unknown_instead_of_leaking_500 | 2 | 2 | unhandled-path-escapes-contract |
| R2-003 | 非 cuda 且非 cpu 的设备名（空串/unknown）被按 CPU 实例报 0 且可读，即编造读数 | 中 | 正确性 | 根因 | 原始编码 | fixed | 把"确实是 0"与"读不到"在探测层就分开，不靠调用方补救 | 只有 `cpu`/`cpu:*` 报 0 且可读；其余非 cuda 设备一律 `readable=false`/`bytes=None`（source=unknown_device） | tests/unit/test_f009_vram_probe.py::test_non_cuda_non_cpu_device_is_unreadable_not_zero | 2 | 2 | fabricated-reading-masquerades-as-fact |
| R3-001 | 用 1ms 的 stop deadline 取 E_TIMEOUT 证据是竞态的，同一实例上时红时绿 | 中 | 测试覆盖 | 根因 | 流程缺陷 | fixed | 改用慢动作制造窗口：卸载在 CPU 上瞬时，加载模型是秒级 | 集成用例改为 stop→等空闲→restore（配 `KRONOS_LIFECYCLE_RESTORE_TIMEOUT_S=0.05`）取 E_TIMEOUT，同窗口顺带取 E_BUSY 与"不中断"的落点证据；连跑 3 次稳定通过 | tests/integration/test_f003_kronos_lifecycle.py::test_timeout_envelope_is_not_a_terminal_failure | 3 | 3 | flaky-evidence-from-racy-window |
| R1-004 | `wait_idle` 是测试专用等待器，却留在生产控制器的公开面上 | 低 | 质量 | 根因 | 原始编码 | fixed | 明确它的用途与非契约地位（docstring + 不进 wire 层） | docstring 写明非契约地位、存在理由与客户端等价手段（轮询 `operation` 转 null） | —（文档性修复，无行为变更） | 1 | 1 | test-hook-in-production-api |
| R1-005 | `E_TIMEOUT` 的服务端 deadline 无法在契约集成用例里默认取证，只能靠外部改配置 | 低 | 测试覆盖 | 症状 | 原始编码 | fixed | 保持现状但在 tasks/spec 写明取证方式，避免以后误读成"未覆盖" | tasks §0 补一条：E_TIMEOUT 须用短 deadline 实例 + `KRONOS_EXPECT_SHORT_DEADLINE=1`，E_BUSY 的窗口须用 restore 制造 | —（文档性修复） | 1 | 1 | — |

**模式性教训**

- **`unhandled-path-escapes-contract` 出现两次（R1-001、R2-002）**：契约面写得再细，只要"未预期异常"没有归口，客户端拿到的就是无 `error` 字段的 500——而按架构 §7.1，那会被读成"服务端未实现本契约"并转入回落探测，一次内部故障被误判成契约缺失。教训：**错误信封的完备性要在最外层收口一次**（wire 层按端点映射），而不是逐个内部路径堵漏；第一次修复只堵了 worker 内部，第二次才把类关掉。
- **`fabricated-reading-masquerades-as-fact`（R2-003）与 F009 自己的设计原则同源**：spec 花了整节区分"读数不可得"与"确实是 0"，实现却在 `device` 非 cuda 时一律报 0/可读——即把"不知道"写成了"确定为零"。教训：凡是有"不可得"语义的字段，默认分支必须落在不可得那一侧，而不是落在看起来无害的 0。
- **`error-path-lies-about-irreversible-step`（R2-001，本轮唯一自伤）**：兜底网按"动作方向"回滚期望态，而不是按"不可逆的一步是否已发生"。卸载丢引用之后回滚 running 是谎报——spec §5 早已写明"不可逆的一步之后只准前进"，修复时没有回读该不变量。教训：写兜底分支前先回读该动作的失败落点表，兜底不是"随便落在一个看起来安全的态"。
- **`flaky-evidence-from-racy-window`（R3-001）**：取证手段本身有竞态时，"通过"不构成证据——同一实例上先红后绿，红绿都不可信。教训：制造观测窗口要用**量级确定**的慢动作（加载模型秒级），不要拿毫秒级 deadline 去撞瞬时动作。
- **`origin` 分布**：original-coding 6、规格自身不可满足 1、fix-regression 1、流程缺陷 1、症状 1。**存活轮数**：R1 的 6 条中 5 条 1→1 当轮关闭、R1-003 跨到第 2 轮；R2 的 3 条当轮关闭；R3-001 当轮关闭。未触发不收敛升级协议（无 finding 连续 3 轮修不动）。
- **裁决分布**：accepted 10 / partial 0 / rejected 0。**建议命中率**：10 条中 9 条实质一致；唯一偏离是 R1-005——建议"保持现状 + 写文档"，实际在第 3 轮发现该取证方式本身竞态（R3-001），改成了 restore 制造窗口。这说明"接受现状并写进文档"这类处置要警惕：文档化的是一个不稳的做法。
- **执行机证据的时效性**：检视改了 wire 层之后，第 1/2 轮之前取的执行机证据（T022/T024）全部失效，收口前用新镜像重取（8012 正常 deadline + 8013 短 restore deadline 两台 CPU 实例）。教训：代码检视改动生产路径后，执行机证据必须重取，不能沿用改动前的"已通过"。
- **跨分支交付边（R1-006）**：`validate_spec_lifecycle` 在 `code-reviewing`/`done` 状态强制 AC 的 tests 路径存在，这与"跨 feature 交付边在本 feature 内验收"的写法结构性冲突。裁决为拆边界——服务端侧契约归 F009、客户端行为归 F003 分支承载。这条模式（`cross-branch-evidence-unreachable`）以后凡是"本 feature 要验收另一分支的代码"都会撞上，立项时就该按此拆。


## 循环 18：F010 Kronos GPU 推理基座 规格文档检视

- report_type: doc-review
- 周期：2026-09-21（3 轮：Round 1 全量扫描；Round 2 因 design 整体重写升级 full-scan 复核；Round 3 封顶 diff 复核 + 流转后门禁补抓 1 条）
- 状态：闭环（stop_condition_met: true，readiness: PASS）
- 基线：`docs/F010-kronos-gpu-runtime@f4a1321`（自 `origin/main` 开出的 worktree）→ 修复终态 `fa2fda0`；流转提交 `1a993fc`
- 被检对象：`docs/features/0.2/F010-kronos-gpu-runtime/{spec,design,tasks}.md` 及相邻契约（`deployment/` Dockerfile 与 compose、`kronos_real.py`、F004 契约测试、F009 tasks T013 与 restore 失败落点、F003 `mining` extra 与 `vram_limit_gb`、架构 §7.1）
- 角色：同一会话先后担任检视方与修复方，每轮显式切换视角；关键修复以实物取证核对（`docker compose config` 合并语义、download.pytorch.org 索引实查、`check_task_dag` 红→绿）

### 循环 18 完整 issue 表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首现轮 | 修复轮 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F010-R1-001 | compose 变量插值做不到"`KRONOS_GPU_COUNT=0` 不渲染预留"；默认路径渲染出无 count 的 nvidia 预留，开发机/CI 起 `kronos-real` 即失败 | high | correctness | root-cause | original-coding | fixed | GPU 面整体移入 `deployment/docker-compose.gpu.yml` override（`-f` 叠加：设备预留 + `KRONOS_DEVICE=cuda` + healthcheck 判据 + GPU build args），默认 compose 文件字节不动；同步改 design §2/§4/§5、spec FR-002/AC-002、tasks T004 | GPU 面四项移入 `deployment/docker-compose.gpu.yml`，默认文件不改；compose 合并语义 R2 实测成立 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | mechanism-cannot-deliver-promise |
| F010-R1-002 | 默认 pin `torch==2.14.0` 没有 cu128 wheel（cu128 止于 2.11.0）；"≥2.7 + cu128 与 F003 同源"决策按现状构建失败，design §4 的 `2.7.*+` 也不是合法 pin | high | correctness | root-cause | original-coding | fixed | 重做 spec §7/design §4 的版本决策：GPU 取 `2.14.0 + cu130`（与 CPU 同版本）并写明宿主驱动下限，或显式接受 CPU/GPU 版本分叉；T002 的核验项加"驱动版本满足所选 CUDA wheel"；F003 `mining` 注释同步 | torch 维持 2.14.0，GPU 用 cu130；写明 R580+ 驱动下限与 arch 核验；BACKLOG 登记 F003 同步项 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | unverified-external-fact |
| F010-R1-003 | AC-004/T015 在开发机执行时，守护进程先拒绝 nvidia 设备请求，容器从未启动，T006 预检不被执行也能"通过"；且开发机按机器边界不跑集成 | high | test-coverage | root-cause | original-coding | fixed | AC-004 拆两层：① 单元层——`KRONOS_DEVICE=cuda` + mock `torch.cuda.is_available()=False` → `real_mode_startup()` 抛 `SystemExit`，变异（删预检）必须判红；② 执行机集成层——不挂设备预留但 `KRONOS_DEVICE=cuda` 起容器，断言非零退出且日志含预检失败文案（区分"守护进程拒绝"与"预检拒绝"） | AC-004 拆单元层 `test_f010_device_strict.py` + 执行机层（不挂预留 + 显式 cuda），明令守护进程拒绝不算证据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | gate-weaker-than-claim |
| F010-R1-004 | 声称"三处同源"，实际是 `KRONOS_DEVICE` / `KRONOS_GPU_COUNT` / `KRONOS_HEALTH_DEVICE_PREFIX` + build arg 四个独立旋钮；`GPU_COUNT=1, DEVICE=cpu, PREFIX=cpu` 会得到占着 GPU 预留的健康 CPU 实例；CPU wheel 镜像 + `DEVICE=cuda` 只能靠 `is_available()` 间接拦 | medium | correctness | root-cause | original-coding | fixed | healthcheck 判据直接读容器内 `KRONOS_DEVICE`（去掉独立前缀变量）；预检加一条"要求 cuda 而 `torch.version.cuda is None` → 失败并点名镜像是 CPU wheel"；配合 R1-001 由 override 文件一处给齐 | 取消独立 GPU_COUNT/HEALTH_PREFIX 变量，四项集中 override；加 `torch.version.cuda is None` 判据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | single-source-claimed-not-enforced |
| F010-R1-005 | 静默回落只在启动预检堵；F009 `restore` 的重载路径复用 `_load_predictor()`，可绕过预检回落 cpu，违背 spec §5"能回答 /health 蕴含按配置设备加载" | medium | correctness | root-cause | spec-drift | fixed | 把"要求 cuda 必须真拿到 cuda"放进启动与 restore 共用的加载入口（如 `eager_load()` 的严格分支），或在 F009 restore 契约中显式复用该校验；AC 增一条 restore 路径用例 | 严格分支进 `_load_predictor()` 调用的 `_resolve_device()`，覆盖启动、restore、惰性加载；restore 失败落 F009 `E_UNAVAILABLE` | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | cross-feature-contract-drift |
| F010-R1-006 | T010 / design §9 把 Kronos 常驻预算（≤3GB）超标与 F003 `vram_limit_gb`（训练预算 6.0）绑定重标，二者不是同一量 | medium | correctness | root-cause | original-coding | fixed | 常驻超标只重标 §7.1 白天行；`vram_limit_gb` 仅在 AC-009 实测"卸载后可用显存 < 训练预算"时才进入重标，并改写 T010 与 design §9 对应行 | 常驻超标只重标 §7.1 白天行；`vram_limit_gb` 仅在卸载后可用 <6GB 时随夜槽行重标 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| F010-R1-007 | 与 F009 T013 撞车：同一 compose 块（端口）、同一 `test_f004_compose_profile_contract.py`、同一 `.env.example`，F010 Phase 1 与 F009 T013 无先后边 | medium | correctness | root-cause | spec-drift | fixed | tasks §4 加边"F009 T013 合入 → F010 T004/T005"（或写明以 F009 合入后的 main 为基线）；采纳 R1-001 后 F010 基本不再改默认 compose，冲突面缩到测试文件 | tasks §4 加 F009 T013 ⇄ T005 同文件非阻塞边与基线规则；spec §7 依赖段同步 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | cross-feature-contract-drift |
| F010-R1-008 | AC-002 写"`docker compose config` 渲染"，而 F004 契约测试是纯文本断言；未说明单元测试是否调 docker、CI 无 docker 时怎么办 | low | test-coverage | root-cause | original-coding | fixed | 明确单元层用文本断言（沿用 F004 纯函数 + 变异）；`docker compose config` 渲染比对作为执行机/有 docker 环境的补充证据 | AC-002 明确纯文本断言、不调 docker；`compose config` 作执行机补充证据 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| F010-R1-009 | spec §0/§7 称 F003 `mining` extra "已确立"，该 extra 只存在于未合入的 `feat/F003-alphagen-vendor` | low | quality | symptom-patch | spec-drift | fixed | 改为"F003 分支上的约定（未合入 main）"，并注明以合入后版本为准 | spec §0 / design §0 标注 mining extra 在未合入分支 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| F010-R1-010 | design §1"后端不改代码/唯一改动是日志行"与 §5、T006 在 `real_mode_startup()` 加预检矛盾 | low | quality | symptom-patch | original-coding | fixed | §1 与 §2"服务代码零改动"改为"两处小改：预检一条 + 日志一行" | design §1/§2 改为「两处小改」 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| F010-R1-011 | NFR-001/SC-002 要求"构建产物逐字一致"不可证伪（引入 ARG 后层缓存键/镜像 digest 必变） | low | quality | root-cause | original-coding | fixed | 改为"默认参数下 Dockerfile 解析出的安装命令与落地前等价 + 默认 compose 文件/渲染结果不变" | NFR-001/SC-002 改为安装命令等价 + 本 feature 不改默认文件，注明不承诺 digest | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | unfalsifiable-claim |
| F010-R1-012 | 8GB 笔记本卡在 WSL2 下 Windows 桌面也占显存，AC-009"卸载后整卡可用 ≥6GB"可能物理达不到，风险表未列 | low | correctness | root-cause | original-coding | fixed | spec §7 风险表加一行：T002 顺带记录空载可用显存；若 <6GB，走 §7.1 重标而非判 AC-009 失败 | spec §7 风险行 + T002 ④ 记录空载可用显存 + T011 重标分支 | `tools/verify.py` 文档门禁（规格生命周期/链接/DAG/一致性） | 1 | 2 | — |
| F010-R2-001 | override 未给 GPU 构建独立 `image:`，默认与 GPU 构建共用 `<project>-kronos-signal-real` 标签，执行机上互相覆盖：GPU 构建后不带 `--build` 的默认启动会跑 CUDA wheel 镜像（反之由严格分支拦下） | medium | correctness | root-cause | fix-regression | fixed | override 增 `image: alphamill/kronos-signal-real:gpu`（默认文件不变），AC-002 断言该标签存在且不等于默认名 | override 增 `image: alphamill/kronos-signal-real:gpu`，AC-002/design §8 断言并加删除变异；开发机 compose config 实测生效 | `tools/verify.py` 文档门禁 | 2 | 3 | shared-artifact-name |
| F010-R2-002 | T002 ③ 只核验 `sm_89`，tasks §5 却称 T002 已核验 `sm_120`；design §4 要求两者 | low | quality | symptom-patch | fix-regression | fixed | T002 ③ 改为 `get_arch_list()` 同时含 `sm_89` 与 `sm_120` | T002 ③ 改为 arch list 同时含 sm_89 与 sm_120 | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| F010-R2-003 | T015 执行机层"不叠加设备预留但显式 cuda 启动 CUDA 镜像"没给出做法；两条严格分支（CPU wheel / 无设备）各需一个触发方式 | low | test-coverage | root-cause | fix-regression | fixed | 写明：GPU 标签镜像 `docker run` 不加 `--gpus` + `-e KRONOS_DEVICE=cuda` → 无设备分支；默认 CPU 镜像 + `-e KRONOS_DEVICE=cuda` → CPU wheel 分支 | AC-004/T015/design §8 写明执行机两例（GPU 镜像不加 --gpus；CPU 镜像显式 cuda） | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| F010-R2-004 | AC-002 的 override 禁止项列 ports/volumes/restart/privileged，漏了 design §4 同样禁止的 `depends_on` | low | quality | symptom-patch | fix-regression | fixed | AC-002 与 design §8 补 `depends_on` | AC-002 与 design §8 禁止项补 depends_on | `tools/verify.py` 文档门禁 | 2 | 3 | — |
| F010-R3-001 | R2-003 让 T015 共用 `test_f010_gpu_runtime.py` 并依赖 GPU 镜像，但 tasks §4 未接生产者前置边；流转后 `check_task_dag` 判红 | low | quality | root-cause | fix-regression | fixed | 补 `T008 -> T015` 边 | tasks §4 补 `T008 -> T015`（GPU 镜像 + 共用载体） | `tools/check_task_dag.py`（红→绿） | 3 | 3 | gate-caught-fix-regression |

### 裁决记录

无（17 条全部接纳）。

### 模式教训

- **三条 High 都是"写在纸上的机制没有对照实物"**（`mechanism-cannot-deliver-promise` / `unverified-external-fact` / `gate-weaker-than-claim`）：compose 插值删不掉设备预留块、`2.14.0` 没有 cu128 包、开发机上守护进程先于预检拒绝——三条都是一条命令就能证伪的事实。**教训：涉及外部工具语义（compose 合并/插值）与外部制品（wheel 索引）的设计断言，文档检视必须当场实测，不能只做文本一致性核对。**
- **`gate-scope-blind-spot` 第二次出现**（循环 15 的 F009-R3-001 是第一次）：`check_task_dag` 只对进入开发流转的状态生效，R2-003 引入的缺边在 `doc-reviewing` 下门禁全绿，流转到 `ready-for-development` 后才判红（R3-001）。同一摩擦 ≥2 次，按元规则应修 harness：让 `check_task_dag` 覆盖 `doc-reviewing`。
- **`fix-regression` 5 条（R2-001..004、R3-001；另有 R1 修复首版的"字节不动"自伤在同轮 `94c2d27` 修正，未单列）**：集中在 override 方案带出的新面（镜像标签共享、执行机取证做法、DAG 边）。与循环 15 相同：方案级重写的自伤面天然大于补丁，第 2 轮 diff 复核不可省。
- **`origin` 分布**：original-coding 9、spec-drift 3、fix-regression 5。**存活轮数**：R1 的 12 条 1→2，R2 的 4 条 2→3，R3-001 当轮关闭；未触发不收敛升级协议。
- **裁决分布**：accepted 17 / partial 0 / rejected 0。**建议命中率**：17 条中 15 条实质一致；两条偏离——R1-004 建议"healthcheck 读容器内 `KRONOS_DEVICE`"，实际改为"判据与 `KRONOS_DEVICE` 同处 override 文件"（override 方案下更简单）；R1-005 建议"放进 `eager_load()`"，实际下沉到 `_load_predictor()` 调用的 `_resolve_device()`，同时覆盖 `/predict` 惰性加载。
- **跨 Feature 联动**：R1-005（restore 绕过预检）与 R1-007（F009 T013 同改 F004 测试文件）说明 F009/F010 的交付边不止 AC-012 一条；F010 → F003 的 cu130 同步项已登记在 BACKLOG。
- **合入前 rebase 抓到的漂移**（未编号，收口时修复）：检视期间 `origin/main` 落入 `9e12512`（F003 T033 只依赖 F009、不依赖 F010），F010 spec/tasks 里七处"解除 F003 T033 前置"随即失真；rebase 后同一收口提交改写。教训：并行会话下，闭环前的 `fetch + rebase` 不是机械步骤，要重新扫一遍被检文档对上游的引用。
- **事实更正（2026-09-21，收口后）**：R1-001 的 compose 实测与 R2 的合并语义实测都在**执行机 `qiaozhi-lt`** 上完成，检视档与 spec/design 曾误写为"开发机"——检视方从未核对 `hostname`，而是按 CLAUDE.md 的机器分工默认自己在开发机。同一次核对还发现：执行机 docker 未装 nvidia 容器运行时（Runtimes 仅 `runc`），这才是 `could not select device driver "nvidia"` 在执行机出现的原因，也是 F010 T002 ① 的真实阻塞点。教训：取证记录的机器名必须来自 `hostname` 输出，不能来自对环境的假设（SOP §3 本就要求记录取证机器）。

## 循环 20：F008 宇宙扩容与 point-in-time 宇宙台账 实现代码检视

report_type: code-review · feature: F008 · status: closed · rounds: 1（full-scan，5 片并行）→ 2（diff-only 复核） · 收口 CI: 见收口提交

- 日期：2026-09-25 | 基线：`b456f3c`（F008 `code-reviewing`，分支 `feat/F008-universe-expansion`）→ 修复终态见收口提交
- 检视人：Claude（同会话内先实现后检视，按 skill §8 显式切换视角；正确性通道按模块切 4 片并行只读扫描，测试覆盖通道单独一片并做 DB-free 内存变异）| 裁决：owner（7 条 Medium/Low 转为 tracked 后续项）
- 范围：`data_bridge/universe/**`（23 个新模块）、`collector/**` 回填编排重构、导出面（`exporter`/`manifest`/`partitions`）、F007 只读消费面迁移（`evaluation/universe_ledger.py`）、`db/migrations/005`、`scripts/f008-*.sh`
- 结论：27 条（1 Critical / 7 High / 7 Medium / 12 Low 计入 8 组）。Critical 与 High **全部当轮修复并锁定**；7 组 Medium/Low 转为 `tracked`（载体：`BACKLOG.md`「规划中」三行新增项 + `tasks.md` §4 既有登记），不计入收敛统计。

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复建议 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1-001 | `usable_baseline` 整版回退被增量模式当继承基线 → 静默数据链损失 | Critical | correctness | 根因 | 修复引入 | fixed | 继承基线不得因回退降级（强制 full／显式确认），回退来源入 manifest | `allow_fallback` 只允许全量模式打开；增量遇损坏的最新 valid 版本拒绝启动并给出处置 | `test_f002_exporter.py::test_usable_baseline_refuses_fallback_in_incremental_mode` | 1 | 1 | `coarse-fallback-semantics` |
| R1-002 | 清单自身不可读时逃出 `usable_baseline`（捕获列表窄于契约） | Medium | correctness | 根因 | 原始编码 | fixed | 捕获清单不可读一并处理 | 捕获 `(VersionNotFoundError, ManifestIntegrityError)`，按模式回退或拒绝 | `test_f002_exporter.py::test_usable_baseline_falls_back_when_newest_version_is_corrupt` | 1 | 1 | `narrow-exception-catch` |
| R1-003 | 跨周期对账是 exchange 级作用域（相消掩盖 / 连带误伤） | High | correctness | 根因 | 原始编码 | fixed | 两侧加 `symbol` 过滤，作用域＝被检 pair | 两侧 `exchange + symbol` 同参；批量回归用例 | `test_f008_quality_gate.py::test_batch_gate_isolates_the_broken_pair` | 1 | 1 | `check-scope-wider-than-decision` |
| R1-004 | 准入过滤把质量标记映射一起收窄 → 导出 FATAL | High | correctness | 根因 | 修复引入 | fixed | `quality_flags` 用未过滤映射 | 质量标记用未收窄映射；导出侧本地收窄 | `test_f008_export_integration.py::test_universe_filter_tolerates_flags_of_excluded_pairs` | 1 | 1 | `partial-symmetric-fix` |
| R1-005 | 未准入 pair 的日期被判成空单元格写进 `skipped` | Low | correctness | 根因 | 修复引入 | fixed | 把准入集合传进 `empty_cell_keys` | `_admitted_only` 同时用于 `empty_cell_keys` 与 `synthesize_skipped` | `test_f008_export_integration.py::test_incremental_universe_filter_does_not_mark_excluded_pairs_skipped` | 1 | 1 | `exclusion-recorded-as-gap` |
| R1-006 | 分片启动器读同名 `FETCH_LIMIT`（`.env` 的采集器值 5） | High | correctness | 根因 | 原始编码 | fixed | 与分片脚本对齐用独立命名空间 | 改读 `BACKFILL_FETCH_LIMIT`（取值在 `source .env` 之后） | `test_script_runtime_contracts.py::test_f008_backfill_launcher_ignores_collector_fetch_limit` | 1 | 1 | `partial-symmetric-fix` |
| R1-007 | `_emit` 载荷违反已冻结事件契约（接线即中断整轮回填） | High | correctness | 根因 | 原始编码 | fixed | 严格命中 `PAYLOAD_FIELDS` | 补 `elapsed`、去 `hostname/status/error`、`retries` 取真实尝试数 | `test_f008_backfill_events.py::test_emitted_payloads_pass_event_contract` | 1 | 1 | `event-contract-drift` |
| R1-008 | 事件平面生产路径无写入方（AC-010 由自证测试兜底） | High | correctness | 根因 | 流程缺陷 | fixed | CLI 接真 sink + `admit_pair` 发成员事件 | CLI 回填接 `event_sink`；`admit_pair` 发 `line=tradability/admission` | `test_f008_backfill.py::test_backfill_events_land_in_store_and_are_queryable` | 1 | 1 | `test-simulates-itself` |
| R1-009 | `--resume-run-id` 不校验目标集合/窗口 → 静默 no-op 报成功 | High | correctness | 根因 | 原始编码 | fixed | 续跑前校验一致性，不一致拒绝 | 校验 `universe_id`/窗口/目标集合 | `test_f008_backfill.py::test_resume_rejects_mismatched_window_or_batch` | 1 | 1 | `resume-without-target-validation` |
| R1-010 | AC-012 的磁盘余量与 gate 非零退出两项无牙（变异存活） | High | test-coverage | 根因 | 原始编码 | fixed | 补真实断言，不许替身 | `capacity` 真单测（`free=` 注入）+ gate 非 ACTIVE 非零退出 | `test_f008_capacity.py::test_require_headroom_rejects_shortfall_by_one_byte_or_more` | 1 | 1 | `stubbed-out-sut` |
| R1-011 | 四类门禁 fixture 全是单 pair，批量掩盖/连坐无锁 | High | test-coverage | 根因 | 原始编码 | fixed | 双 pair fixture 锁批量语义 | 批量双 pair 用例（坏 pair 隔离、干净 pair ACTIVE） | `test_f008_quality_gate.py::test_batch_gate_isolates_the_broken_pair` | 1 | 1 | `single-record-fixture` |
| R1-012 | 非法时间戳抛裸 `ValueError` → exit 1 + traceback | Medium | correctness | 根因 | 原始编码 | fixed | `parse_moment` 转 `WindowError` | 一处收口，`E_UNIVERSE_WINDOW`/2 | `test_f008_cli_contract.py::test_backfill_rejects_malformed_window_timestamp` | 1 | 1 | `error-code-escape` |
| R1-013 | AC-014 从未跨实现验证（F007 自产自读） | Medium | test-coverage | 根因 | 契约漂移 | fixed | 把 F008 产物交给 F007 装载 | 契约用例 + stdlib 独立复算 + 字面 canonical 文档 | `test_f007_upstream_contracts.py::test_f008_publisher_digest_is_loadable_by_f007` | 1 | 1 | `cross-module-digest-untested` |
| R1-014 | `BackfillRun.schema_version` 零断言、`load_run` 不校验版本 | Medium | test-coverage | 根因 | 原始编码 | fixed | 断言版本 + 载入校验 | `load_run` 拒绝版本不符记录 | `test_f008_backfill.py::test_run_record_carries_schema_version` | 1 | 1 | `schema-field-unasserted` |
| R1-015 | `gate --pairs` 对「候选但被排除」静默空跑 exit 0（fail-open） | Medium | correctness | 根因 | 原始编码 | fixed | 校验改对 `selected`；空判定集判红 | `_selected` 对 `definition.selected` 校验 | `test_f008_cli_contract.py::test_gate_rejects_pairs_excluded_from_selection` | 1 | 1 | `fail-open-empty-selection` |
| R1-016 | 「落选」不移出导出清单（导出集合不绑定当前宇宙版本） | Medium | correctness | 根因 | 契约漂移 | tracked | 导出入口带当前 `universe_id`，与 `selected` 求交 | — | — | 1 | — | `derived-set-missing-scope` |
| R1-017 | 杠杆代币后缀启发式误判正常标的（SYRUP 实测命中） | Medium | correctness | 根因 | 原始编码 | tracked | 改判据为交易所元数据（`underlyingType`） | — | — | 1 | — | `ticker-heuristic-false-positive` |
| R1-018 | `valid_from` 唯一性不是 DB 约束（TOCTOU），重复行不可删 | Medium | correctness | 根因 | 原始编码 | tracked | 加 `UNIQUE (lake_pair, valid_from)` | — | — | 1 | — | `check-then-act-without-constraint` |
| R1-019 | AC-008 只有源码文本扫描，真实触发器只测 UPDATE | Low | test-coverage | 症状 | 流程缺陷 | fixed | 补 DELETE 库侧断言 | journeys 补 DELETE 被触发器拒绝 | `test_f008_journeys.py::test_us004_membership_delete_is_rejected_by_trigger` | 1 | 1 | `static-source-proxy` |
| R1-020 | 两处不会红的断言（假连接恒等 + journey 放量被 `**0` 抹平） | Low | test-coverage | 根因 | 原始编码 | fixed | 让断言真的能红 | 假游标区分两侧计数并断言 mismatch；fixture 真实 ×10 | `test_f008_quality_gate_window.py::test_aggregate_check_reports_mismatch_when_counts_differ` | 1 | 1 | `vacuous-assertion` |
| R1-021 | `xfail(strict=True)` 体内断言与 fixture 不符且从未执行 | Low | test-coverage | 根因 | 流程缺陷 | tracked | 摘标记时同步核对期望值 | — | — | 1 | — | `xfail-body-never-run` |
| R1-022 | 缺失 digest 报 `E_UNIVERSE_ARTIFACT` 而非 `E_UNIVERSE_NOT_FOUND` | Low | correctness | 根因 | 契约漂移 | fixed | 读前判存在性，缺失报 NOT_FOUND | `load_artifact` 显式 `is_file()` 判定 | `test_f008_artifact.py::test_load_missing_artifact_fails_closed` | 1 | 1 | `error-code-contract-drift` |
| R1-023 | 消费面 digest 只查前缀（路径成分可越出 artifact 目录） | Low | correctness | 根因 | 原始编码 | fixed | 严格 `<64 hex>` 校验 | 本地独立实现该校验 | `test_f007_upstream_contracts.py::test_load_universe_rejects_malformed_digest_before_io` | 1 | 1 | `weak-input-validation` |
| R1-024 | `seed_initial_members` 只写单一命名空间且从未执行 | Low | correctness | 根因 | 原始编码 | tracked | 对 spot/perp 各写一行并给显式入口 | — | — | 1 | — | `asymmetric-invariant-implementation` |
| R1-025 | `delisting_end` 是死参数：退市 pair 按满窗口判缺失 | Low | correctness | 根因 | 原始编码 | tracked | 透传到 `gate_pairs`/`gate_and_admit` | — | — | 1 | — | `dead-parameter` |
| R1-026 | `members_at` 与区间并集在「已闭合 delisted 行」上不一致 | Low | correctness | 根因 | 原始编码 | tracked | 先选最后状态再判其 `valid_to` | — | — | 1 | — | `two-implementations-diverge` |
| R1-027 | `run.json` 截断式原地覆盖写，中断即损坏断点记录 | Low | correctness | 根因 | 原始编码 | fixed | 同目录临时文件 + `os.replace` | 原子替换；`load_run` 对损坏/版本不符报明确错误 | `test_f008_run_record.py::test_interrupted_run_record_write_keeps_previous_document` | 1 | 1 | `non-atomic-runtime-record` |
**模式性教训**

- **`partial-symmetric-fix` 出现两次（R1-004、R1-006）**：同一处共享语义只修了一半——准入过滤收窄了 `produce_partitions` 的映射却漏了同一份映射的 `quality_flags` 消费方；分片脚本改了 `BACKFILL_FETCH_LIMIT` 却漏了启动器（`.env` 里同名的采集器值把它压成 5）。教训：**改一处共享语义（收窄映射、同名变量）前先列出它的全部消费方**，否则"修好了"只是修好了被看见的那条路径。
- **`check-scope-wider-than-decision`（R1-003）与 `fail-open-empty-selection`（R1-015）是同一枚硬币**：判定范围比判定对象宽（exchange 级对账 vs pair 级结论）会同时带来误伤与相消掩盖；而 `all([])` 恒真让"什么都没跑"退出 0。教训：**门禁的 scope 必须与它声称的作用域同宽**，且"空输入"必须有自己的判红路径——`all(空)` 不是判据。
- **唯一的 Critical 来自 `fix-regression`（R1-001）**：为了消除"一次损坏让此后所有导出跑不动"的死锁引入整版回退，却在增量模式上打开了静默的数据链损失（回退版当继承基线 → 新清单丢中间版本分区，而收缩守卫只在全量生效）。教训：**回退/降级类修复必须先逐条调用路径回答"这个降级在语义上是否等价安全"**，只在能重算的来源（全量）上放行。
- **`test-simulates-itself`（R1-008）+ `vacuous-assertion`（R1-020）+ `stubbed-out-sut`（R1-010）**：事件平面的测试自注入 sink 并断言自造载荷，"事件从未落盘"因此活过了整个开发期；假游标对任何计数查询都回 `(7,)`，`match` 断言在任何实现下都真；把被测函数本身猴补成抛异常，于是删掉真实校验仍全绿。教训：**"写出去了"必须经真实出口再读回；"能判红"必须做一次变异证明**——本轮 3 条 High 完全靠变异存活才被定性。
- **`error-code-escape` / `error-code-contract-drift`（R1-012、R1-022）**：契约登记的九类启动期拒绝里，两类在真实输入上拿不到登记的码（语法非法时间戳抛裸 `ValueError` → exit 1 被脚本当可重试故障；缺失 artifact 报内容类错误）。教训：**"有分支"不等于"可区分"**，登记的码要逐条真跑一遍。
- **`origin` 分布**：original-coding 17、fix-regression 4、spec-drift 3、process-gap 3。**存活轮数**：27 条全部 `first_seen_round=1` 当轮关闭（无跨轮项，未触发不收敛升级协议）。
- **裁决分布**：accepted 27 / partial 0 / rejected 0。**建议命中率**：27 条中修复方案与建议实质一致 26 条；唯一偏离是 R1-001——建议"回退来源写入 manifest + 守卫以最新已发布版本为参照"，实际选择更窄的解法（**增量模式直接拒绝回退**），理由是这样连"回退留痕"都不需要，语义面更小。
- **成本观察（供下轮采样参考）**：两条最高价值项（Critical + High）都落在**上一轮"实测驱动的修复"的邻域**（T023 的 `usable_baseline` 回退与准入过滤收窄）。教训：**修复密集区应作为下一轮检视的优先采样区**，而不是"刚修过、应该没问题"的免检区。
- **并行检视的实际形态**：5 片只读 + 1 片测试覆盖并行扫描，再由 4 个修复代理分头落地；跨代理的文件冲突（同一测试文件、同一报错文案）出现了两次，靠"派活时按文件切分 + 报告里显式声明并发面"化解。教训：**并行检视要按文件边界派活**，共享文件（CLI/测试聚合文件）要么独占、要么约定最小 literal edit。
