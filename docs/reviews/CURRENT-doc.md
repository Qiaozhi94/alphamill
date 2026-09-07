---
report_type: doc-review
round: 3
date: 2026-09-07
prior_report: 本文件 round-3 重开版（前序：round-2 闭环过早被本审计推翻）
scope: diff-only（R3-01/R3-02 修复 diff 复核 + 数据源端到端实证）
stop_condition_met: true
severity_counts: {critical: 0, high: 0, medium: 0, low: 0}
baseline: main @ 9ff8fd5 → 修复后本文件记录
reviewer: Sisyphus（review-convergence 协议，循环 4 round-3；修复方视角落地 R3-01/R3-02 后切回检视方复核，角色切换留痕）
evidence: 数据源端到端实证——qiaozhi-lt（Tailscale 100.98.228.125，SSH Georg@ + 密钥 ~/.ssh/gp-to-lt 实测可登）；D:\Projects\quant-crypto 在位（含 .env 凭据键 19 个、Docker 引擎活）；卷 quant-crypto_timescale_data 在位；容器 quant-timescaledb 临时启动 healthy 后实查：ohlcv_1m=6,504,359 行、11 张公有表、5 个连续聚合（ohlcv_5m/15m/1h/4h/1d），查毕已停回归档态（Exited 0）；实测 Tailscale 直连 5432 被防火墙拦截而 SSH 22 通——迁移路径定为 SSH 流式 pg_dump，无需开防火墙。本机身份实证：hostname=qiaozhi-gp（非 qiaozhi-lt，旧 skill 设备表过期）
note: round-2 闭环判定的根本缺陷由本轮修正：数据源从「承认可达性未验」升级为「容器内实查行数级实证」。另发现 design §3 权威表清单与实库差 4 张表（dryrun_*×2、backfill_progress×2）——已随 R3-01 修复一并补全（11 表全列 + 以 pg_tables 实查为准的兜底条款）
issues_index:
  - {id: R3-01, severity: high, status: fixed（轮 3）}
  - {id: R3-02, severity: low, status: fixed（轮 3）}
---

# F001 开发前检视报告（循环 4 · 第 3 轮 · 重开后当轮关闭）

## 1. 总评

**round-3 PASS：R3-01（数据源不可达未定义）经端到端实证修复**——数据源 qiaozhi-lt 已定位到卷级（quant-crypto_timescale_data，6,504,359 行实测），访问路径已钉死（SSH + docker exec 流式 pg_dump，免开防火墙），T001/T004/design §0/spec §7/migration-plan 五处同步落位。R3-02 以 tasks §0 显式扩展条款关闭。附带修正：design §3 对账口径按实库补全（6→11 表）。循环 4 关闭，F001 可进入 ready-for-development。

## 2. Round-3 修复核对

| 检查 | 结果 |
|---|---|
| R3-01 修复 | design §0 双现场钉死（代码副本 gp / 运行现场+数据源 qiaozhi-lt 含 SSH 密钥/卷名/实测行数/防火墙约束）；tasks T001 双现场、T004 六步迁移路径（start→dump→流式传输→restore→stop）；spec §7 依赖、migration-plan item 1 同步 ✓ |
| R3-01 实证 | SSH 登录 ✓ / 卷存在 ✓ / 容器启停 ✓ / 行数 6,504,359 ✓ / 11 表 + 5 caggs ✓ / 归档态恢复（Exited 0）✓ |
| R3-02 修复 | tasks §0 增显式扩展条款：SC-xxx 为合法任务引用锚（记录枚举偏离与理由）✓ |
| 附带修正 | design §3 权威表清单 6→11 表（补 dryrun_open_positions、dryrun_runtime_snapshots、backfill_progress、derivatives_backfill_progress）+ caggs 实名 5 个 + 「以 pg_tables 实查为准」兜底 ✓ |
| fix-regression 扫描 | 五处修改相互引用一致（T001↔design §0↔spec §7↔migration-plan item 1 的主机/IP/卷名/行数完全一致）；无新引入矛盾 ✓ |

## 3. Issue 总表

| ID | 标题 | 严重度 | 分类 | 根因/症状 | 来源 | 状态 | 修复方案 | 回归测试 | 首次出现轮次 | 修复轮次 | 模式标签 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3-01 | T004 数据源不可达且未定义（六路探测全否，round-2 闭环过早） | 高 | 正确性 | 根因 | fix-regression（D035 数据面残留） | fixed | 数据源实证钉死：qiaozhi-lt `D:\Projects\quant-crypto` Docker 卷 `quant-crypto_timescale_data`，SSH 流式 pg_dump 路径（免开 5432），五文档同步 | verify.py 文档门禁 | 3 | 3 | unpinned-data-source |
| R3-02 | T012/T013/T014 任务引用 SC-003 偏离模板 ID 枚举 | 低 | 质量 | 症状 | fix-regression（D034/R2-01 修复引入） | fixed | tasks §0 显式扩展条款（SC-xxx 为合法锚 + 理由记录） | validate_spec_lifecycle | 3 | 3 | template-id-drift |

## 4. 裁决记录

- Round-2 七条修复：accepted 7/7（round-3 开局已核）。
- R3-01/R3-02：检视人自探自修自核（角色切换留痕于 frontmatter），修复含行数级实证，accepted。
- Round-2 闭环判定过早：不追认（已由本轮重开-修复-关闭完整纠正，教训入 RETROSPECTIVE 模式教训 #10）。

## 5. 停止条件状态

**满足**：High/Low 清零（R3-01/R3-02 fixed）；本轮修复 diff 亲核 + fix-regression 扫描无新问题；verify.py 全绿；闭环提交推送后 CI 观测绿（见 RETROSPECTIVE）。F001 具备进入 ready-for-development 的全部文档前置。
