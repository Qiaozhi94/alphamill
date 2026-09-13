# BACKLOG —— 活跃 Feature 索引

本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。

| Feature | 版本 | 状态 | 链接 |
|---|---|---|---|
| F002-data-bridge | 0.2 | ready-for-development | [spec](docs/features/0.2/F002-data-bridge/spec.md) |
| F004-kronos-inference-runtime | 0.2 | draft | [spec](docs/features/0.2/F004-kronos-inference-runtime/spec.md) |

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
| 评测台/门禁（FR3） | FR3.1~FR3.6 | M1 收尾（F002/F004 之后） | F007（已调配） | ADR-0005 约束传播：报告必须持久化曲线级时间序列（权益/回撤/分位数/IC 衰减） |
| 研究控制台 | FR8.1/8.2/8.4 | M2 前（评测台落地后立项） | F005（ADR-0005 预留） | 只读；渲染对象仅限研究版本态产物（含谱系 F005；组合/台账只读视图为 F005.1 增量，M3+）；实时 PnL 不进控制台；版本归属 0.2 |
| AlphaGen vendor | FR2.2 | M2 | F003（F001 spec 预留） | ADR-0001 选型与 vendor 卫生规则 |
| 运营操作入口 | FR8.3 | M3/M4 | F006（架构文档预留） | 写路径唯一经 `alphamill/api/` 并落 FR7.4 审计 |
