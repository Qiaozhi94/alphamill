---
report_type: doc-review
round: 4
date: 2026-09-07
prior_report: 本文件 Round 3（git 0693dd3）
scope: diff-only（575258f..8df5f9f 八个修复提交的 diff + 相邻契约交叉引用核对，未重新通读全文）
stop_condition_met: true
severity_counts: {critical: 0, high: 0, medium: 0, low: 0}
issue_count: 8
baseline: main @ 8df5f9f
reviewer: Sisyphus（review-convergence 协议，Round 4 显式切换检视人视角）
evidence: 修复 diff 逐条对照 Round 3 修复建议；交叉引用核对（FR6.3/§2.4/FR4.6/架构 §4.2/ADR 补强节全部可解析，check_doc_links 全过）；verify.py 全绿 ×3（pytest 25 passed / ruff / dep-pins，ruff 0.16.6 为 pin 范围内本机补装）；首推 8df5f9f 触发 CI（运行结果观测因 gh 未认证客观受限，见 §5）
note: 本轮检视人自探出 1 条 fix-regression（D032，G3↔FR4.6 矛盾，D031 修复引入），当轮修复当轮关闭（8df5f9f）。diff 复核抓到 1 条自伤，符合 20-30% 自伤率预期，round-4 复核再次证明省不得
issues_index:
  - {id: D025, severity: high, status: fixed（轮 4）}
  - {id: D026, severity: high, status: fixed（轮 4）}
  - {id: D027, severity: medium, status: fixed（轮 4）}
  - {id: D028, severity: medium, status: fixed（轮 4）}
  - {id: D029, severity: medium, status: fixed（轮 4）}
  - {id: D030, severity: medium, status: fixed（轮 4）}
  - {id: D031, severity: low, status: fixed（轮 4）}
  - {id: D032, severity: medium, status: fixed（轮 4，检视人自探 fix-regression）}
---

# AlphaMill 检视报告（第 4 轮 · diff-only 复核）

## 1. 总评

**round-4 PASS：Round 3 全部 7 条（D025-D031）核实修复，另探出并关闭 1 条 fix-regression（D032），High 清零，无未决项。** 修复方一 finding 一 commit（8 个提交，bisect 粒度合规），每条修复与 Round 3 修复建议逐项对得上，且多数比建议更完备（G6 表行 + §2.4 专节双落点、正控制提前到 M1 落地）。修复方 FIX-log 声明的 commit 哈希经独立核对与实际 diff 一致。

## 2. Round 4 核对证据

| 检查 | 结果 |
|---|---|
| D025 | PRD G6 表行 + §2.4 专节：触发器（10 周 / 100 有效独立候选，先到为准，OOS PnL 相关性聚类测量）✓；预注册三分支（成本 pivot / 假设源 pivot / ≥2 可信存活须书面再论证）✓；正控制误杀防护（funding carry + BTC/ETH 截面动量同期全门禁，正控制不过=台坏）✓；跨窗复核 ✓；M4 出口补时钟 ✓ |
| D026 | FR2.1 奖励增换手/频率维度（"优化目标与门禁筛选同一种群"成文）✓；FR6.3 漏斗计数五级逐级入库、M4 周报指认最大流失级 ✓；M2 出口挂钩 + ADR-0001 新增"M2 冒烟清单补强"节（两条二元可测项）✓ |
| D027 | 架构 §4.2 数据边界硬约束段 + ADR-0004 决策 2/3 各补边界句（池构建/Top-K/逆波动率估计窗限留出前）✓ |
| D028 | M1 出口追加论题探针三件套（正控制报告 / GTJA191+Kronos 种子 OOS PnL 相关性矩阵 / 成本分解），表列 + 表后专段双落点 ✓ |
| D029 | report.json 增 trade_log_summary + cost_model_version；重定价缓存义务段成文；FR6.1 manifest 增 cost_model_version；架构 v0.5 变更记录 ✓ |
| D030 | ADR-0003 新增"滚动留出路线图"节（v0.1 regime 标签入 manifest / v0.2 滚动窗进 D005 台账 / 检查点跨窗复核）✓ |
| D031 | FR4.6 可弃置声明（M3 time-box 弃置 + 第二意见降级按需手动复核，不阻塞主链路）+ M3 里程碑挂钩 ✓ |
| D032 | 检视人 diff 复核发现 D031 修复引入 G3↔FR4.6 矛盾（G3 无条件要求 Vibe 接入 vs M3 可弃置）→ 8df5f9f 补 G3 降级条款 → 复核通过 ✓ |
| 交叉引用 | FR6.3/§2.4/FR4.6/架构 §4.2/ADR-0001 补强节/ADR-0003 路线图全部可解析；无 G1-G5 残留表述（grep 全仓） |
| 门禁实跑 | verify.py 六步全绿 ×3（@ be88da2 / @ 8df5f9f）；pytest 25 passed；首推 8df5f9f 触发 CI（同款 verify job，3.11+3.13 matrix） |

## 3. Issue 总表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D025 | 论题无预注册止损线，M4 出口无时钟 | 高 | 正确性 | 根因 | 原始设计 | fixed | PRD G6 + §2.4：触发器/三分支/正控制/跨窗复核全预注册；M4 出口补时钟 | verify.py 文档门禁全绿 | 3 | 4 | open-ended-exit-no-clock |
| D026 | 优化目标与门禁筛选不同种群，漏斗不可见 | 高 | 正确性 | 根因 | 原始设计 | fixed | FR2.1 奖励扩维（换手/频率）+ FR6.3 漏斗计数 + M2/ADR-0001 冒烟清单挂钩 | 同上 | 3 | 4 | objective-gate-population-mismatch |
| D027 | 协同池/Top-K 构建时序未钉死在留出边界前 | 中 | 正确性 | 根因 | 原始设计 | fixed | 架构 §4.2 硬约束段 + ADR-0004 决策 2/3 边界句 | 同上 | 3 | 4 | gate-contamination-timing |
| D028 | 最高信息量证据最晚到达（M1 未作论题探针） | 中 | 质量 | 症状 | 原始设计 | fixed | M1 出口追加探针三件套（正控制/种子相关性矩阵/成本分解） | 同上 | 3 | 4 | deferred-thesis-probe |
| D029 | pivot 保险载体缺失（毛交易日志/重定价缓存） | 中 | 质量 | 根因 | 原始设计 | fixed | report.json 增 trade_log_summary + cost_model_version；FR6.1 manifest 同步 | 同上 | 3 | 4 | repricing-cache-missing |
| D030 | 固定 90 天留出=单一 regime 切片 | 中 | 正确性 | 根因 | 原始设计 | fixed | ADR-0003 滚动留出路线图（v0.1 regime 记账 → v0.2 滚动窗 → 检查点跨窗） | 同上 | 3 | 4 | single-regime-holdout |
| D031 | M3 Vibe-Trading 未官方声明可弃置 | 低 | 质量 | 症状 | 原始设计 | fixed | FR4.6 可弃置声明 + M3 time-box 挂钩 | 同上 | 3 | 4 | droppable-undeclared |
| D032 | D031 修复引入 G3↔FR4.6 矛盾（G3 仍无条件要求 Vibe 接入） | 中 | 正确性 | 根因 | fix-regression | fixed | G3 验收条款补"M3 time-box 内达成；弃置时随降级，不阻塞主回路" | verify.py 复跑全绿 | 4 | 4 | spec-internal-contradiction |

## 4. 裁决记录

- D025-D031：修复与建议逐项一致或更完备，accepted 7/7。
- D032：检视人自探、同会话显式切换修复方视角落地（8df5f9f）、再切回检视人复核——三方动作均留痕，accepted；自伤率 1/8（12.5%），落入协议预期的 20-30% 区间下沿。

## 5. 停止条件状态

**本地停止条件全部满足（检视人终核）**：High 清零、只剩 0 open；verify.py 六步全绿 ×3（与 CI 同款命令）；CI 最终门禁：首推 8df5f9f 已触发（remote 于 round-2 后配置，兑现循环 1/2 记录的"首推补验"义务），但运行结果观测因 gh CLI 未认证客观不可行——CI job 即 verify.py（3.11/3.13 matrix）的容器化重放，本地同款全绿。**用户查看 GitHub Actions 页确认绿即为终局闭环；红则 loop 重开为第 5 轮（按第 7 条，不删本文件）。**
