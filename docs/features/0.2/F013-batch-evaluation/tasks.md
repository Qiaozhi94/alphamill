---
kind: feature
id: F013
version: "0.2"
related_features: [F002, F003, F005, F007, F008, F012]
topics: [evaluation, batch, implementation-plan]
doc_kind: tasks
created: 2026-09-29
updated: 2026-09-29
---

# F013：工厂批量闭环·评测侧 — 实施任务

> Owner: Georg | [Spec](spec.md) | [Design](design.md)

## 0. 来源与执行规则

本次仅立项与需求设计，以下全部是后续实施清单，不代表已经开工或验证通过。
必须先文档检视收敛、readiness=PASS，再经 G1 计划批准后进入需求分支实施。
需求/验收以 spec 为准，接口以 design 为准；每项完成后凭新鲜证据勾选。
先 [TEST] 旅程红灯，再实现和全量验收；实现测试分轨但本文件不授权自动派生代理。

## 1. 前置条件

- [ ] T001 (`FR-001`, `FR-006`, `FR-009`, `AC-001`, `AC-007`, `AC-012`): 完成三件套文档检视并关闭契约问题，取得 readiness=PASS 与 G1 批准 — verify: 文档检视记录与 `sdd_status.py --dry-run`。
- [ ] T002 (`FR-001`, `NFR-002`, `AC-001`, `AC-011`): 前置依赖闭环：取得 F012 选择尾窗 preset 增量（载体 `BACKLOG.md`「规划中」表「F012 选择尾窗 preset 增量（selection_tail_1h_2y_v1）」行，契约 design §4.1，`window.end = cutoff − L − H`）按该行验收标准的合入提交与回归证据；在执行机以该 preset 重新生成 3–5 候选 completed run，核验 preset 参数互验、尾窗容纳预注册折与标签、源日历为 continuous_24_7/UTC、显式绑定模式与 1h，并按 F007 `build_snapshot` 口径（有数据分区）预算每成员 event_time_min/max，与 run 绑定声明值逐字段相等（不等则按 AC-001 必拒，先回 F012 处理，不放宽比较）；旧 end=cutoff 产物只作负例；冻结真实小批与 N=50 基准输入计划 — verify: F012 增量合入提交与其回归记录；`$ALPHAMILL_REPORTS_DIR/f013/input-preflight.json`（工作树外，只做前置校验，不看评测结果）。

## 2. 实现任务

### Phase 1：输入与身份（缺口①、③）

- [ ] T003 (`FR-001`, `DR-001`, `AC-001`): 经 F014 `load_verified_run` 加载 run/config 并完成 preset 参数互验（不另写口径），验证因子清单，实现 `continuous-to-windows-v1` 日历转换与 digest 映射、显式绑定到已发布 snapshot 的逐字段比对 — verify: `tests/contract/test_f013_batch_binding.py`。
- [ ] T004 (`FR-004`, `AC-005`): 实现生成事件格式/原因/reachability 子原因/counts 展平适配及守恒校验 — verify: `tests/contract/test_f013_generation_adapter.py`。
- [ ] T005 (`FR-005`, `DR-001`, `NFR-001`, `AC-002`, `AC-006`): 实现批次 manifest、source/cohort binding、冻结锁事务与外置 reports 根前置校验（未设置/仓内零写入拒绝） — verify: `tests/contract/test_f013_batch_binding.py`。

### Phase 2：信号与表达式（缺口②）

- [ ] T006 (`FR-003`, `AC-004`): 实现版本化后缀 AST renderer 与完整算子/负例契约测试 — verify: `tests/unit/test_f013_expression_render.py`。
- [ ] T007 (`FR-002`, `DR-002`, `AC-003`): 实现只读湖到确定性 CSV/sidecar 的生产者（整批面板只建一次、显式 isfinite、日历 mask/折索引/标签端点、空/退化候选在 loader 前识别） — verify: `tests/unit/test_f013_signal_producer.py`。
- [ ] T008 (`FR-002`, `FR-003`, `NFR-003`, `AC-003`, `AC-004`): 扩展 F007 批量路径消费 panel_context：segment 内持仓/成本/bootstrap/HAC、按预注册 n_folds/H/embargo 的稳定性切分、填实 GuardContext，缺上下文不记 PASS；保留 L1/L2/L3 真实状态 — verify: `tests/unit/test_f013_signal_producer.py` 与 F007 方法论门/稳定性回归。

### Phase 3：有界重试与正式发布（缺口④）

- [ ] T009 (`FR-006`, `TR-001`, `AC-007`): 实现 canonical attempt 写入、持久化尝试预算与重试分类（确定性 INCOMPLETE 一次终态，仅瞬态/中断重试，未知异常暂停） — verify: `tests/integration/test_f013_batch_recovery.py`。
- [ ] T010 (`FR-006`, `FR-009`, `NFR-003`, `AC-007`, `AC-012`): 实现选定尝试到正式发布/唯一登记/abandon 的事务、closure publisher 与 batch_blocked 弃置（含未启动成员）及旧单候选兼容 — verify: `tests/integration/test_f013_batch_recovery.py` 与既有 canonical 测试。
- [ ] T011 (`FR-001`, `FR-005`, `NFR-001`, `AC-002`, `AC-006`): 在所有正式写入口执行 batch binding/capability/锁约束，防单候选入口绕过 — verify: `tests/contract/test_f013_batch_binding.py`。
- [ ] T012 (`FR-007`, `AC-008`): 实现 finalize 事务：已有 verdict 核验复用、finalize_inputs 冻结、带输入摘要的原子 verdict、锁 + 原子替换的幂等补回写与冲突检测，按 design §5 完整性口径（比较集合 = 全部登记成员）输出 cohort_incomplete_causes — verify: `tests/integration/test_f013_batch_recovery.py`。
- [ ] T013 (`FR-007`, `FR-008`, `AC-008`, `AC-009`): 实现按规范时间键的相关性配对、comparison_unavailable 关闭与 `ordered_mean_abs_rho_v1` 方法元数据 — verify: `tests/contract/test_f013_batch_correlations.py`。

### Phase 4：命令与报告（缺口④、⑤）

- [ ] T014 (`FR-005`, `FR-006`, `FR-007`, `FR-009`, `IR-001`, `IR-002`, `IR-003`, `AC-006`, `AC-008`, `AC-012`): 接入 batch 与 batch-close CLI 的完整阶段流、状态枚举与错误/退出输出 — verify: `tests/integration/test_f013_batch_journey.py`。
- [ ] T015 (`FR-008`, `AC-009`): 实现来源分布、独立 first-loss 结构和最大流失级的 v2 报告聚合 — verify: `tests/unit/test_f013_batch_synthesis.py`。
- [ ] T016 (`FR-008`, `NFR-003`, `AC-010`): 实现 synthesis v1/v2 双读与不可变 ID 重建兼容 — verify: `tests/contract/test_f013_synthesis_compatibility.py`。

## 3. 验证与验收任务

### [TEST] 组：先立红灯的旅程验收轨

- [ ] T017 [TEST] (`AC-001`, `AC-002`, `AC-005`, `AC-006`): 建「completed 生成批次→冻结→正式评测」旅程，断言五处边界、默认 reports 根零写入、外置根 git 干净与 Agent/坏输入拒绝 — verify: `tests/integration/test_f013_batch_journey.py` 的 RED/GREEN 记录。
- [ ] T018 [TEST] (`AC-007`, `AC-008`, `AC-012`): 建各写边界中断与续跑旅程，断言确定性失败仅评测一次、瞬态尝试 ≤3、分母不变、无部分 verdict、无覆盖历史及 batch-close 收尾 — verify: `tests/integration/test_f013_batch_recovery.py` 的 RED/GREEN 记录。
- [ ] T019 [TEST] (`AC-009`, `AC-010`): 建「终态报告→删除派生视图→重建」旅程，断言来源/流失/语义 ID 一致及旧报告读取 — verify: `tests/contract/test_f013_synthesis_compatibility.py` 的 RED/GREEN 记录。

### 执行机与完整验收

- [ ] T020 (`NFR-002`, `AC-006`, `AC-011`): 在执行机以真实湖和 T002 的新 preset run（3–5 个候选）跑完整批次及续跑，记录机器和设备 — verify: `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration/test_f013_batch_journey.py -q`；`$ALPHAMILL_REPORTS_DIR/f013/journey-evidence.json`（工作树外）。
- [ ] T021 (`NFR-002`, `AC-011`): 在执行机按 design §8 的 N=50 固定配置（R=0/R=50 两组）测信号生产/canonical/finalize/RSS 并判预算 — verify: `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration/test_f013_batch_capacity.py -q`；`$ALPHAMILL_REPORTS_DIR/f013/capacity-evidence.json`（工作树外）。
- [ ] T022 (`NFR-003`, `AC-001`, `AC-003`, `AC-004`, `AC-005`, `AC-010`): 跑 F013 契约测试与 F003/F007/F012 兼容/正负控制回归 — verify: `python3 tools/verify.py`。
- [ ] T023 (`NFR-003`, `AC-006`, `AC-007`, `AC-008`, `AC-011`, `AC-012`): 在执行机运行完整集成验收且保存 skip/失败明细 — verify: `ALPHAMILL_INTEGRATION=1 python3 -m pytest tests/integration -q`。

### 文档与收口

- [ ] T024 (`DR-001`, `DR-002`, `IR-001`, `IR-003`, `AC-010`): 回写架构、操作入口和 AC 实际测试/证据路径，明确 F005 消费及 M2 尚未验收边界；T002/T020/T021 的外置根证据只在 T023 结束（执行机最后一次 canonical 之后）才按 design §8 复制入库 `reports/f013/` 并提交，之后若需再跑 canonical 须先提交或移出该副本 — verify: `python3 tools/verify.py`。
- [ ] T025 (`NFR-003`, `AC-011`): 完成代码检视、质量门与收口记录后按 sdd-flow 流转，推送后核对当前提交 CI — verify: `python3 tools/verify.py`、检视收敛记录、CI 记录与状态脚本。

## 4. 依赖与并行关系

- `T001 -> T002`：文档收敛后才核验 F012 前置增量与新 run；增量未合入则 F013 实施不开始。
- `T002 -> T003 -> T004 -> T005`：输入契约依赖合规 run；日历映射与 binding 先于事件适配和冻结事务。
- `T005 -> T006 -> T007 -> T008`：冻结后才生产信号；F007 消费端依赖 sidecar 契约。
- `T008 -> T009 -> T010 -> T011 -> T012 -> T013`：尝试协议、正式发布/收尾、写入口约束、finalize 事务与相关性共享 F007 发布/登记状态，顺序执行。
- `T013 -> T014 -> T015 -> T016`：CLI 接线在全部内核之后；报告聚合与双读在 finalize 语义稳定后。
- `T014 -> T017`、`T012 -> T018`、`T014 -> T018`、`T016 -> T019`：旅程 GREEN 依赖对应生产者；
  三条 [TEST] 旅程的红灯夹具在 T002 后即编写（编写早、执行晚），此处边表示 GREEN 验收执行。
- `T017 -> T020`、`T018 -> T020`、`T019 -> T020`：执行机真实小批在三条旅程本地全绿之后。
- `T020 -> T021 -> T022 -> T023 -> T024 -> T025`：容量基准、统一门禁、执行机集成、回写与收口依次进行。
- T002 发现覆盖不足或增量未合入时，先补 F012 增量或重新生成合规 run；不得以改快照/窗口静默绕过。
- 此列表无 [P] 任务：输入契约、共享 F007 发布/登记和报告存在顺序依赖。

## 5. 明确后移

- 研究控制台及 v2 报告渲染 → F005 / 0.2：只读界面必须先于 M2 爬坡上线。
- ≥50 个真实候选完整自动评测的 M2 出口 → 0.2 M2 验收（F005 后）：本 Feature 的 N=50 finalize 基准不代替该出口。
- 评测快照 cutoff 晚于生成绑定（owner P0-1 方案 b）→ M2 之后另立增量：v1 坚持逐字段一致。
- 协同池 meta-factor、预筛慢算子/资金费修正 → BACKLOG 独立后续 Feature / 0.2，不扩入本批量切片。
- 多 run 混批、多 horizon 信号、1m 输出与生成器扩展 → 0.2 后续增量，当前入口显式拒绝。
- L2/L3 审计、组合最终确认与生产写入口 → F006 / M3，不由本编排器授予晋级或下单权限。
