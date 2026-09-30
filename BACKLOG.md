# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F013-batch-evaluation | 0.2 | draft | [spec](docs/features/0.2/F013-batch-evaluation/spec.md) |
| F014-selection-tail-preset | 0.2 | draft | [spec](docs/features/0.2/F014-selection-tail-preset/spec.md) |

> **F012 已收口（2026-09-28，done）**：AlphaGen 后端接入挖掘 CLI（生成侧）已在 main 上（merge `4e1455e`
> + CI 修复 merge `2710723`，CI 36411197094 py3.11/3.13/3.14 绿）；执行机夜槽实跑入册 50/50（235 s），
> 交付记录与已知限制见 `docs/features/releases/0.2.md`。后续：[F013 批量评测编排](docs/features/0.2/F013-batch-evaluation/spec.md)已立项（执行顺序 1 的评测侧）；
> 预筛加速见下表「F012 后续：vendor 慢算子向量化加速」。

> **F011 已收口（2026-09-26，done）**：导出清单绑定当前宇宙版本（落选即移出）已在 main 上
> （merge `1d830aa`），交付记录与已知限制见 `docs/features/releases/0.2.md`；生产两个导出单元已同时开启
> `--universe-filter`（`8bbe681`，2026-09-26 部署），首轮 09-27 02:00 增量 / 04:00 全量均绑定
> `sha256:6d85a249…`、`dropped_by_universe=[]`，`ohlcv_1m` 全量判 content-unchanged。

> **F003 已收口（2026-09-26，done）**：AlphaGen vendor 与可插拔生成器平面已在 main 上，
> 交付记录见 `docs/features/releases/0.2.md`；「AlphaGen 后端接入 CLI `--generator`」作为
> AC-006 的真实验收载体留在下方规划中队列。

> **F009 已收口（2026-09-24，done）**：控制面三端点已在 main 上，交付记录见
> `docs/features/releases/0.2.md`；F010 的 T011/T012/T018 可以开始。
> **F010 已收口（2026-09-25，done）**：GPU 基座已在 main 上（PR #6，`d6e2525`），交付记录见
> `docs/features/releases/0.2.md`；F009 AC-012 的显存先红态已解除。
> **F009 与 F003 的前置边**：F009 的端点缺失**不阻塞 F003 开工与接口验收**（客户端按
> 架构 §7.1 观测→处置决策表 fail-closed 兜底）。
> T033 要求 `test_f003_kronos_lifecycle.py` 以 0 xfailed 通过，即真实卸载取证的先决条件是
> 端点就绪并部署于执行机。
> **~~2026-09-19 复测~~**（已被 F009 T022 取代）：那次 404 打在 mock 实例 `qiaozhi-lt:8001`
> 上，而按契约 mock **本就不注册** `/lifecycle/*`（F009 IR-005），因此它既不能证明"端点未
> 实现"，也不是合法取证目标。
> **2026-09-24 重取（F009 T022，`kronos-signal-real`）**：控制面已落地——`--runxfail` 跑
> `test_f003_kronos_lifecycle.py` 得 **6 passed / 0 xfailed**（含 E_BUSY / E_TIMEOUT /
> E_BAD_REQUEST 三类错误路径）；同一新镜像在 mock 实例上注册的 `/lifecycle` 路由数为 0、
> 三端点仍 404，两件事各自成立。真实卸载的**显存**取证已由 F010 于 2026-09-24 完成（其 AC-009/T011）。

> **F010 → F003 同步项**（F010 文档检视 R1-002，2026-09-21）：`pyproject.toml` `mining` extra
> 注释中的 `--index-url .../cu128` 示例对 torch ≥2.12 已无对应 wheel（cu128 止于 2.11.0）；
> Kronos GPU 镜像定为 `torch==2.14.0` + `whl/cu130`。**已同步**（2026-09-21，
> `feat/F003-alphagen-vendor@fb915f0`）：注释改为写明 cu128 上限与 cu130 + 驱动 R580+
> 的对齐路径；执行机现用 `2.10.0+cu128` 不变，驱动下限由 F010 T002 核验。

> 规则：feature 状态变更（spec frontmatter）时必须同步本表；`done` 的 Feature 移出本表，
> 交付记录进入 `docs/features/releases/<version>.md`。
> 示例行（复制后替换，链接必须指向真实 spec.md）：
> `| F001-<name> | 0.1 | draft | [spec](docs/features/0.1/F001-<name>/spec.md) |`

## 规划中（编号已预留 / 待分配，未立 spec）

手工维护的前瞻队列，不是上表的派生索引，也不参与门禁双向校验（`check_backlog` 只解析本
标题之上的活跃索引表，本节表格即使行形状相同也不会被误判）；spec 立项后转入上表
并从本节移除。编号规则：跨版本连续递增（见 `docs/features/README.md`）；**编号按分配时刻
递增，与执行顺序无关**（如 F007 评测台先于编号更小的 F005 研究控制台执行）。

**执行顺序（owner 2026-09-27 裁决：先补核心能力，告警后移）**：

1. **F012 AlphaGen 接入挖掘 CLI（生成侧）→ F013 批量评测编排（评测侧）**（M2 核心，owner 2026-09-27 拆分）：挖掘按入册上限产出通过自检与预筛的候选 → 看结果前冻结整批 cohort、逐个 canonical、finalize、漏斗报告；开发期小批量验证；
2. **F005 研究控制台**（M2，PRD 要求先于批量评测爬坡上线）；
3. **M2 出口验收**：执行机夜槽单批 ≥50 候选自动评测 + 漏斗报告（ADR-0008 批量能力标定，不设周产出配额）；
4. **平台告警通道（飞书推送）**：须在第 5 项重新冻结宇宙前落地；
5. **宇宙口径 v2**：下表 4 条「F008 后续」合并为一个 Feature，只重新冻结一次；
6. 技术债两条（F002 `skipped` 口径、依赖声明门禁）不单独排期，空隙顺手做（quick 通道）。

| Feature | 需求 | 里程碑窗口 | 编号状态 | 关键约束 |
|---|---|---|---|---|
| 研究控制台 | FR8.1/8.2/8.4 | M2 前（评测台落地后立项） | F005（ADR-0005 预留） | 只读；渲染对象仅限研究版本态产物（含谱系 F005；台账只读视图为 F005.1 增量，组合只读视图随 M3 规划）；实时 PnL 不进控制台；版本归属 0.2 |
| F012 后续：vendor 慢算子向量化加速（预筛 p95） | F012 `NFR`（T002 预筛 p95 ≤ 1 s 阈值）；`generators/vendor_operators.py` | 待排（M2 出口不依赖：夜槽 50/50 仅用 235 s） | 待分配 | owner 2026-09-27 裁决（F012 代码检视 R-B1）：另立后续需求，F012 不改。实测（qiaozhi-lt，真实面板 45 万行 × 35 对）：`ema/wma/med/mad` 走 `rolling().apply(raw=True)` 逐窗调 Python、`corr/cov` 纯 Python 循环——`corr:20` 3.8 s、`mad:20` 2.1 s、`ema:20` 1.4 s，对照 `delta/mean/cs_rank` 0.25–0.42 s；夜槽 p95 1347 ms（n=147，首跑旧口径 1563 ms / n=213）。方案：`numpy.lib.stride_tricks.sliding_window_view` 按 pair 向量化，须与 vendor 逐点一致（ic_parity）。顺带（R-B2）：流水线每候选重复的 close 掩码/宇宙掩码/排序在构造时缓存（`evaluate_objective` 约占单候选 76%）。另附（R3-2，F003 既有）：资金费通道稀疏而预筛每行按 1h/8h 扣费，配置 `funding_8h_bps>0` 时可能低估约 8 倍，随预筛改造一并修正 |
| AlphaGen 协同池 meta-factor 注册 | PRD FR2.6（协同池作为可部署 meta-factor 注册）；F003 `SC-003` 协同池部分 | 待排（M2 出口不依赖） | 待分配 | owner 2026-09-27 裁决（F012 文档检视 D12 / spec `Q-006`）：F012 只交付单因子入册，`pool` 恒为 null。立项时须定：成员须全部为 F012 流水线已入册因子（vendor `MseAlphaPool` 成员未经自检/预筛）、权重来源与冻结时点、经 `pool_store.build_pool` 注册的验收与反解 |
| F008 后续：门禁/台账改用**数据命名空间**的上市时间 | FR-004 `AC-006`、`FR-005` `valid_from` 语义 | 待排（F008 收口后单独评审） | 待分配 | 现状：`exchange_snapshot.py` 从**永续**市场取 `onboardDate` 作 `listed_at`，却被门禁窗口与 `valid_from` 用于**现货**数据命名空间；实测 BANK/ONDO/PUMP/TUT 现货晚于永续 7.5–213.6 天，按现语义被隔离（owner 2026-09-24 裁决：本轮接受隔离，本项单独评审）。修法须在发现阶段记录现货首根 K 线时间、门禁窗口与 `valid_from` 都用它；**需重新冻结宇宙（新 digest）**，故不属 F008 收口范围。证据：`reports/f008/执行机取证-T020-T023.md` §7 |
| F008 后续：采集清单由台账驱动（准入即采集） | FR-001/FR-005 与 `collector` 的联动 | 待排 | 待分配 | 现状：`deployment/.env` 的 `SYMBOLS` 是**静态清单**，采集器每轮只取最近 `FETCH_LIMIT=5` 根、无追赶逻辑；准入新 pair 后必须人工改 env + `--force-recreate` 采集容器，并另跑追赶回填，否则序列在冻结窗口终点断档（owner 2026-09-24 裁决：收口时按手动两步执行，本项列为后续候选）。修法：采集器按 `universe_membership` 的 `universe_at(now)` 派生清单并自带追赶。证据：`reports/f008/执行机取证-T020-T023.md` §4、§11 |
| F008 后续：发现口径去 ticker 启发式（杠杆代币误判） | FR-001、`AC-001` | 待排（需重新冻结宇宙） | 待分配 | 现状：`discover.py` 用「`UP`/`DOWN`/`BULL`/`BEAR` 后缀 + 前缀长度」判杠杆代币，实测把交易所元数据为 COIN 的 `SYRUP/USDT`（90/90 根日线、上线 503 天）误判为 `leveraged_token` 排除——本次成交额 5.10M 未进前 40 故实际影响 0，但同类真实标的若排名进前 40 会被静默丢掉。修法：判据改为交易所元数据的 `underlyingType`/`contractType`（或口径里的显式名单）；**改口径会改变 `universe_id`，须重新冻结宇宙**。证据：`docs/reviews/RETROSPECTIVE.md` 循环 21 · R1-017） |
| F008 后续：台账库侧加固（唯一约束 / 退市窗口 / 两口径统一 / 补种双命名空间） | FR-005、`AC-007`/`AC-008` | 待排 | 待分配 | 四项：①「同一 pair 的 `valid_from` 严格递增」只由 `BEFORE INSERT` 触发器先读后写保证，表上无 `UNIQUE (lake_pair, valid_from)`——并发写入可让两行同键提交，而 `no_mutation` 触发器禁止 DELETE，重复行落入后**无法清理**；②`delisting_end` 是死参数（`gate_pairs` 没有该形参），中途退市的 pair 按满窗口判缺失/边界，原因码指向「数据缺失」而事实是按定义不该有数据；③`members_at` 与 `materialize_intervals` 在「已闭合的 delisted 行（`valid_to` 非空）」上给出不同结论（库侧导出清单与 F003/F007 消费的 artifact 会分叉）；④`seed_initial_members` 只写单一 `market_type`，与「同一 `db_symbol` 必须在 spot/perp 成对登记」的不变量不对称，且生产链路从未调用。修法：加唯一约束（需新迁移）、透传 `delisting_end`、统一两口径、补种改双命名空间。证据：`docs/reviews/RETROSPECTIVE.md` 循环 21 · R1-018/R1-024/R1-025/R1-026） |
| 平台告警通道（飞书推送；含 F011 后续：导出失败告警） | PRD FR6.1（数据延迟/缺失）；F011 `FR-003`、F002 退出码契约 | 执行顺序 4（M2 后、宇宙口径 v2 重新冻结前） | 待分配 | 渠道：飞书群自定义机器人（签名校验，webhook 与密钥只进 `deployment/.env`）；v1 = 通用通知脚本 + export/fullexport/backup/snapshot 四单元 `OnFailure=`；v2 = 湖新鲜度 / 采集滞后告警接 Grafana/Prometheus。 现状：`alphamill-export` / `alphamill-fullexport` 自 `8bbe681`（2026-09-26 部署）起带 `--universe-filter`，绑定不到可用宇宙（无生效冻结定义 / 定义损坏 / 多口径）即退出码 2 且 `RestartPreventExitStatus=2` 不重试；部署目录无 `OnFailure=` 与湖新鲜度告警，失败只留在 journald，可能多日无人发现。候选：单元加 `OnFailure=` 触发通知单元，或 Prometheus 按各 dataset 最新 manifest `exported_at` 做新鲜度告警（>26h 报警）；验收须以一次人为制造的 `E_UNIVERSE_NOT_FROZEN` 实测触发 |
| F002 后续：增量/全量对 `skipped` 判缺口径不一致（每周白发布版本） | F002 版本发布语义（内容不变不发布） | 待排（随手可做，先查根因） | 待分配 | 现象：周日全量对 `derivatives_funding_rates` / `derivatives_open_interest` / `signals_log` 各发布一个 `-r2`，分区数、行数、`revision_diff` 均不变，只有 `skipped` 变——09-26 增量 90 条 → 全量 0 条；09-24（未开过滤）0 → 78 条。`ohlcv_1m` 不受影响（F011 截止日路径已判 content-unchanged）。疑点：`partitions.empty_cell_keys` 增量按「基线维度 × 窗口日期」判缺、全量只在各维度首末数据日之间判缺，对 8h 资金费率 / 1h 持仓量这类稀疏或 `timeframe` 维度的数据集两边结论不同。验收：同一源库连跑「增量→全量→增量」，三个数据集第二、三次均为 no-op（参照 `tests/integration/test_f011_export_journey.py` 的同构断言）|
| 运营操作入口 | FR8.3；FR3.6 无前视 L2（逐 K 线重放）/L3（信号缓存 merge/join 对齐）审计器；FR2.5 评测面 lifecycle 状态判定 | M3/M4 | F006（架构文档预留） | 写路径唯一经 `alphamill/api/` 并落 FR7.4 审计；lifecycle 状态判定依赖 paper/实盘表现监控（F007 v0.2 只回写 `promotion_verdict` 等评测摘要，见其 `DR-008`）；F007 的 `promotion_verdict=blocked_pending_audit` 与三层状态由本入口消费（`E_PROMOTION_BLOCKED`） |
| 依赖声明门禁补强 | 无（工程内务） | 随手可做，不占里程碑 | 待分配 | `check_dep_pins` 现只校验「已声明的版本在范围内」，对「import 了但没声明」一无所知——httpx（F009 收口 `266c9d6`）与 pyyaml（F010 R2-002）两次 CI 干净环境收集期 ImportError 都由此漏网。实现见已撤回的 `8dc7d4c`（F010 R3-001 判为越界，`43bdb69` 撤回）：**立项前必须先解决两类误报**——① 本仓包被当成第三方（F008 分支 `import factor_factory`）；② 必装传递依赖不算未声明（F003 分支 `import numpy`，numpy 是 pandas 的必装依赖，CI 不会 ImportError）。合入前需在 F003/F008/F009/F010 四个 worktree 上各跑一次确认零误报 |
| F012 选择尾窗 preset 增量（selection_tail_1h_2y_v1） | F012 window preset / CLI / config / run 持久化；F013 `FR-001`/`AC-001`（**F013 前置依赖**，F013 tasks T002） | M2（执行顺序 1 内，须先于 F013 实施合入） | F014（2026-09-29 已立 [spec](docs/features/0.2/F014-selection-tail-preset/spec.md)，draft；本行保留至 F014 T012 同步 F013 指针后移除） | owner 2026-09-29 裁决（F013 文档检视 P0-1 选 a）。现状：`generators/base.py` 只有 `default_1h_2y`，window.end = cutoff，F013 选择窗 `[S,E)` 恒为空；现有两次 50 候选 run 均属此类，只作 F013 负例。契约（全文见 F013 design §4.1）：参数 L（选择窗长度，正整数小时）、H（标签 horizon，正整数 bar）、Δ=1h；`generation.window.end = cutoff − L − H·Δ`、`start = end − 730d`；CLI/config/run 持久化并互验 preset 名、L、H 与派生 window（新增元数据纳入 config_digest）；生成/训练/预筛不得读到 end 及之后。**验收**：①单元——派生窗口公式、L/H 非正或非整数拒绝、篡改 run/config 任一侧的 preset/L/H/window 被互验拒绝；②集成——生成/训练/预筛的实际读取上界 < end（注入读尾窗即失败）；③`default_1h_2y` 行为与既有 run 读取不变（回归）；④执行机以新 preset 生成 3–5 候选 completed run（显式绑定、resample 1h、日历 continuous_24_7/UTC），成员 `event_time_min/max` 与按有数据分区重算值相等，交 F013 T002 预检；⑤文档注明 start 比现有湖起点（2024-09-10）早 L+H，实际可用生成数据不足 730 天。评测 cutoff 晚于生成绑定（方案 b）不在本增量，M2 之后另立 |
