# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F003-alphagen-vendor | 0.2 | developing | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
| F008-universe-expansion | 0.2 | ready-for-development | [spec](docs/features/0.2/F008-universe-expansion/spec.md) |
| F009-kronos-lifecycle-endpoints | 0.2 | ready-for-development | [spec](docs/features/0.2/F009-kronos-lifecycle-endpoints/spec.md) |

> **F009 与 F003 的前置边**：F009 的端点缺失**不阻塞 F003 开工与接口验收**（客户端按
> 架构 §7.1 观测→处置决策表 fail-closed 兜底）。
> T033 要求 `test_f003_kronos_lifecycle.py` 以 0 xfailed 通过，即真实卸载取证的先决条件是
> 端点就绪并部署于执行机。
> **2026-09-19 复测**：`kronos-signal` 服务在 `qiaozhi-lt:8001` 在跑（`/health` 正常、
> `device=cpu`），但 `/lifecycle/status` 返回 **404**，端点仍未实现；该次探测打在 mock
> 实例上，按契约 mock 不是合法取证目标（无显存可释放），结论成立但基线须在 F009
> 落地时以 `kronos-signal-real` 重取（F009 tasks T022）。

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
| 运营操作入口 | FR8.3；FR3.6 无前视 L2（逐 K 线重放）/L3（信号缓存 merge/join 对齐）审计器；FR2.5 评测面 lifecycle 状态判定 | M3/M4 | F006（架构文档预留） | 写路径唯一经 `alphamill/api/` 并落 FR7.4 审计；lifecycle 状态判定依赖 paper/实盘表现监控（F007 v0.2 只回写 `promotion_verdict` 等评测摘要，见其 `DR-008`）；F007 的 `promotion_verdict=blocked_pending_audit` 与三层状态由本入口消费（`E_PROMOTION_BLOCKED`） |
| Kronos GPU 推理基座 | 架构 §7.1 单卡时段调度的显存语义前提 | F009 真实卸载取证 / F003 T033 之前 | F010（本次预留） | CUDA 镜像与 torch CUDA wheel、compose GPU 设备预留、`device`/healthcheck 断言改写、F004 已验收的 CPU 契约与变异门迁移。**现状**：`kronos-signal-real` 是 CPU 实例（`KRONOS_DEVICE: cpu`、CPU wheel index、healthcheck 以 `device=cpu` 为通过条件），仓内没有任何 GPU Kronos 实例；F009 控制面可独立交付与验收，但显存真实下降类结论在本 feature 落地前一律不成立 |
