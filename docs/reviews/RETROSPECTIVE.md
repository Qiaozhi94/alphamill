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
| F004-R002 | `.dockerignore` 白名单未经真实构建验证，且同时作用于 data-collector 镜像（F001/F002 运行链） | Medium | 测试覆盖 | 根因 | 修复引入 | tracked(T013) | tasks.md 立条目含 AC，执行机构建后标 tracked | 载体 tasks T013：执行机构建三镜像 + 容器内 `import alphamill` + 容器套件复跑 | 待 T013 执行机取证 | 2 | — | gate-cannot-see-runtime-semantics |
| F004-R003 | spec §6 验收证据的门禁计数已失真（静态 16/变异 13/运行时 8） | Medium | 质量 | 根因 | 流程缺陷 | fixed | 按 T010 回写 spec §6，done 前必须完成 | 勘正为 26/20/13 并补依赖与构建上下文条目；检视方复核计数与实际用例数逐一相符 | `tools/validate_spec_lifecycle.py` + 实际用例计数核对 | 2 | 3 | evidence-record-drift |
| F004-R004 | 延后到执行机的容器证据（Q001/Q003/Q004/T004）只写在 FIX-log 备注里，tasks.md 无承载条目 | Low | 质量 | 根因 | 流程缺陷 | tracked(T013) | 增 T013 含 AC，可与 R002 合并 | 与 R002 合并为 T013（含可判定的退出码级 AC 与 DAG 边 `T013 -> 状态收口`） | 待 T013 执行机取证 | 2 | — | deferred-work-without-carrier |
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
- **`F004-R002` / `F004-R004`（tracked → T013）**：`.dockerignore` 的 docker 语义与容器级证据只能在执行机取。开发机 `docker info` 实测不可达，按 SOP §3 这不是失败也不是证据。T013 的 AC 是退出码级可判定的，F004 `review → done` 以它为前置。
- **CI 最终门禁：绿**。修复终态 `7fc67c7` 的 CI run `34953277116` success；本复盘提交 `af8bdce` 的 run `34954284354` success（py3.11 / py3.13 双矩阵，`verify.py` 全部步骤通过）。据此执行协议第 8 节的闭环清理：本地删除过程稿 `CURRENT-code.md` 与 `FIX-log.md`（二者 gitignored，无删除提交）。
- **取证环境备注**：默认沙箱内到 `api.github.com` 的 HTTPS 出口被拦截（`gh run list` → TLS handshake timeout / EOF），SSH 到 origin 正常；CI 状态最终在放开沙箱后取得。这条记下来是因为它会重复影响后续循环的"推送后确认 CI"步骤——不要因为 `gh` 首次超时就判定无 CI 权限。
