# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F003-alphagen-vendor | 0.2 | developing | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
| F011-export-universe-binding | 0.2 | draft | [spec](docs/features/0.2/F011-export-universe-binding/spec.md) |

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

| Feature | 需求 | 里程碑窗口 | 编号状态 | 关键约束 |
|---|---|---|---|---|
| 研究控制台 | FR8.1/8.2/8.4 | M2 前（评测台落地后立项） | F005（ADR-0005 预留） | 只读；渲染对象仅限研究版本态产物（含谱系 F005；台账只读视图为 F005.1 增量，组合只读视图随 M3 规划）；实时 PnL 不进控制台；版本归属 0.2 |
| F008 后续：门禁/台账改用**数据命名空间**的上市时间 | FR-004 `AC-006`、`FR-005` `valid_from` 语义 | 待排（F008 收口后单独评审） | 待分配 | 现状：`exchange_snapshot.py` 从**永续**市场取 `onboardDate` 作 `listed_at`，却被门禁窗口与 `valid_from` 用于**现货**数据命名空间；实测 BANK/ONDO/PUMP/TUT 现货晚于永续 7.5–213.6 天，按现语义被隔离（owner 2026-09-24 裁决：本轮接受隔离，本项单独评审）。修法须在发现阶段记录现货首根 K 线时间、门禁窗口与 `valid_from` 都用它；**需重新冻结宇宙（新 digest）**，故不属 F008 收口范围。证据：`reports/f008/执行机取证-T020-T023.md` §7 |
| F008 后续：采集清单由台账驱动（准入即采集） | FR-001/FR-005 与 `collector` 的联动 | 待排 | 待分配 | 现状：`deployment/.env` 的 `SYMBOLS` 是**静态清单**，采集器每轮只取最近 `FETCH_LIMIT=5` 根、无追赶逻辑；准入新 pair 后必须人工改 env + `--force-recreate` 采集容器，并另跑追赶回填，否则序列在冻结窗口终点断档（owner 2026-09-24 裁决：收口时按手动两步执行，本项列为后续候选）。修法：采集器按 `universe_membership` 的 `universe_at(now)` 派生清单并自带追赶。证据：`reports/f008/执行机取证-T020-T023.md` §4、§11 |
| F008 后续：发现口径去 ticker 启发式（杠杆代币误判） | FR-001、`AC-001` | 待排（需重新冻结宇宙） | 待分配 | 现状：`discover.py` 用「`UP`/`DOWN`/`BULL`/`BEAR` 后缀 + 前缀长度」判杠杆代币，实测把交易所元数据为 COIN 的 `SYRUP/USDT`（90/90 根日线、上线 503 天）误判为 `leveraged_token` 排除——本次成交额 5.10M 未进前 40 故实际影响 0，但同类真实标的若排名进前 40 会被静默丢掉。修法：判据改为交易所元数据的 `underlyingType`/`contractType`（或口径里的显式名单）；**改口径会改变 `universe_id`，须重新冻结宇宙**。证据：`docs/reviews/RETROSPECTIVE.md` 循环 21 · R1-017） |
| F008 后续：台账库侧加固（唯一约束 / 退市窗口 / 两口径统一 / 补种双命名空间） | FR-005、`AC-007`/`AC-008` | 待排 | 待分配 | 四项：①「同一 pair 的 `valid_from` 严格递增」只由 `BEFORE INSERT` 触发器先读后写保证，表上无 `UNIQUE (lake_pair, valid_from)`——并发写入可让两行同键提交，而 `no_mutation` 触发器禁止 DELETE，重复行落入后**无法清理**；②`delisting_end` 是死参数（`gate_pairs` 没有该形参），中途退市的 pair 按满窗口判缺失/边界，原因码指向「数据缺失」而事实是按定义不该有数据；③`members_at` 与 `materialize_intervals` 在「已闭合的 delisted 行（`valid_to` 非空）」上给出不同结论（库侧导出清单与 F003/F007 消费的 artifact 会分叉）；④`seed_initial_members` 只写单一 `market_type`，与「同一 `db_symbol` 必须在 spot/perp 成对登记」的不变量不对称，且生产链路从未调用。修法：加唯一约束（需新迁移）、透传 `delisting_end`、统一两口径、补种改双命名空间。证据：`docs/reviews/RETROSPECTIVE.md` 循环 21 · R1-018/R1-024/R1-025/R1-026） |
| 运营操作入口 | FR8.3；FR3.6 无前视 L2（逐 K 线重放）/L3（信号缓存 merge/join 对齐）审计器；FR2.5 评测面 lifecycle 状态判定 | M3/M4 | F006（架构文档预留） | 写路径唯一经 `alphamill/api/` 并落 FR7.4 审计；lifecycle 状态判定依赖 paper/实盘表现监控（F007 v0.2 只回写 `promotion_verdict` 等评测摘要，见其 `DR-008`）；F007 的 `promotion_verdict=blocked_pending_audit` 与三层状态由本入口消费（`E_PROMOTION_BLOCKED`） |
| 依赖声明门禁补强 | 无（工程内务） | 随手可做，不占里程碑 | 待分配 | `check_dep_pins` 现只校验「已声明的版本在范围内」，对「import 了但没声明」一无所知——httpx（F009 收口 `266c9d6`）与 pyyaml（F010 R2-002）两次 CI 干净环境收集期 ImportError 都由此漏网。实现见已撤回的 `8dc7d4c`（F010 R3-001 判为越界，`43bdb69` 撤回）：**立项前必须先解决两类误报**——① 本仓包被当成第三方（F008 分支 `import factor_factory`）；② 必装传递依赖不算未声明（F003 分支 `import numpy`，numpy 是 pandas 的必装依赖，CI 不会 ImportError）。合入前需在 F003/F008/F009/F010 四个 worktree 上各跑一次确认零误报 |
