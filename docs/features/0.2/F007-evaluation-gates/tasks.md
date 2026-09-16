---
kind: feature
id: F007
version: "0.2"
related_features: [F002, F003, F004, F008]
topics: [evaluation, validation, evidence, experiments]
doc_kind: tasks
created: 2026-09-13
updated: 2026-09-17
---

# F007：统一评测台与证据门禁 - 任务

> Owner: Georg | Spec: `spec.md` | Design: `design.md`

## 0. 来源与执行规则

- 行为与验收真相源：`spec.md`。
- 技术方案与边界：`design.md`。
- 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。
- canonical writer、留出访问、统计失败语义与 artifact 发布属于高风险路径，必须变异验证。

## 1. 前置条件

- [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot builder/reader contract；builder 只接收显式 universe/calendar artifact，验证其内容摘要并在 provenance 保留不可变引用；preview latest 必须先冻结，canonical 只收 snapshot ID；builder 区分 `--universe`（F008 台账 digest，`universe_at(T)` 语义）与 `--calendar`（本 Feature calendar JSON）两个独立引用并分别校验；同时实现 F003 上游只读摄入契约（`generation.run_completed`/`generation.candidate_rejected`、算子能力登记表、协同池 `FactorDef`）与 F008 universe artifact 的 digest 加载及 `universe_at(T)` 语义校验 — verify: `tests/contract/test_f007_upstream_contracts.py`、`tests/unit/experiment_store/test_research_snapshot.py`
- [ ] T002 (`FR-004`, `FR-005`): 预注册 v1 方法/阈值/cohort schema 与两个正控制、白噪声、泄漏负控制 — verify: `tests/fixtures/f007/README.md`
- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader、预留最终确认窗 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账/读最终确认窗的负例） — verify: `tests/integration/test_f007_execution_tiers.py`

## 2. 实现任务

### Phase 1：身份、隔离与最小 preview

- [ ] T004 (`DR-001`, `DR-002`, `AC-006`): 实现 snapshot/experiment canonical JSON 规范化、两级内容 ID 与 supersedes 校验 — verify: `tests/unit/experiment_store/test_research_snapshot.py`、`tests/unit/experiment_store/test_identity.py`
- [ ] T005 [P] (`FR-001`, `DR-004`, `AC-001`): 实现 preview/canonical 物理根目录和 capability 边界 — verify: `tests/integration/test_f007_execution_tiers.py`
- [ ] T006 (`IR-001`, `IR-003`, `AC-008`, `AC-011`): 实现 preview CLI 与稳定结构化输出/错误码，首屏固定含 tier/cohort/data+code digest/state/verdict 与首个失败原因（快照测试锁定） — verify: `tests/integration/test_f007_cli.py`
- [ ] T007 (`FR-003`, `FR-005`, `AC-004`): 实现最小信号质量、三档成本、breakeven 与阶段状态模型（按 design §3.3 术语表实现 stage 状态与 verdict 两层枚举），并写入信号来源 provenance（`source=placeholder` 在 canonical 失败关闭、preview 显式标注） — verify: `tests/unit/evaluation/test_cost_and_stability.py`

### Phase 2：方法论门与 canonical 证据

- [ ] T008 (`FR-002`, `FR-007`, `AC-002`, `AC-009`): 实现 capability/guard 配对及 label endpoint/PIT/max-horizon/train-only-fit 守卫，并在 manifest 写入三层无前视状态（L1 本 Feature fail-closed 执行；L2/L3 owner=F006/M3，缺失层记 `not_yet_available` 并阻断晋级） — verify: `tests/unit/validation/test_methodology_gate.py`
- [ ] T009 (`FR-004`, `AC-003`): 实现成员级 HAC IC/block bootstrap 与 cohort 级 BH-FDR、有效独立数 DSR、MinTRL，异常统一失败关闭 — verify: `tests/unit/evaluation/test_required_statistics.py`
- [ ] T010 (`FR-005`, `AC-004`): 实现 purged/embargoed rolling split、三级样本量裁决（`underpowered`/`provisional`/`trustworthy`）和稳定性报告 — verify: `tests/unit/evaluation/test_cost_and_stability.py`
- [ ] T011 (`DR-003`, `TR-001`, `TR-002`, `AC-005`): 实现 run 事件、report/curves/manifest 同盘原子发布与恢复 — verify: `tests/integration/test_f007_atomic_publish.py`
- [ ] T012 (`FR-004`, `DR-004`, `DR-005`, `TR-003`, `NFR-001`): 实现冻结 cohort、成员 registration、收齐校验、原子 finalize 与 official population 可重建投影；同时实现 append-only 留出预算台账（`holdout_budget/ledger.jsonl`，仅 canonical capability 可追加，preview 越权写入即失败关闭并写 `evaluation.gate_rejected`） — verify: `tests/integration/test_f007_canonical_registry.py`
- [ ] T013 (`IR-001`, `IR-002`, `AC-008`): 实现 canonical/finalize-cohort CLI，缺上下文或成员未收齐时非零拒绝 — verify: `tests/integration/test_f007_cli.py`

### Phase 3：综合、控制与契约交付

- [ ] T014 (`FR-006`, `AC-007`, `AC-012`): 实现只消费 canonical 的 synthesis builder 与五阶段/三维失败汇总（按 design §3.3 冻结的 `failure_taxonomy` schema 与五阶段 ID 枚举聚合，未知取值失败关闭）；漏斗第一级只读摄取 F003 的 `generation.run_completed`（仅 `status=completed`）与 `generation.candidate_rejected`（按原因码） — verify: `tests/integration/test_f007_synthesis.py`
- [ ] T015 (`FR-006`, `UX-002`, `AC-005`, `AC-011`): 实现 report/curves/synthesis schema reader 并验证曲线-标量互推；断言 `approximation` 标注存在、canonical 恒为非近似，并对产物路径做 POSIX 逻辑路径断言（Windows/WSL 物理路径只进 provenance） — verify: `tests/contract/test_f007_artifact_schemas.py`
- [ ] T016 (`FR-003`, `FR-004`, `FR-005`, `AC-003`): 跑正控制、白噪声与故意泄漏 golden，多成员 cohort 批量夹具全链记录拒绝者（被拒者仍入分母、诊断性重算不重复计数） — verify: `tests/integration/test_f007_controls.py`
- [ ] T017 (`FR-001`, `FR-002`, `NFR-003`, `AC-001`, `AC-002`, `AC-003`, `AC-005`): 对 future-fill、embargo、guard 注册、preview writer、异常吞噬与 publish 完整性运行定向变异，逐 mutant 产出证据 — verify: `tests/mutation/test_f007_gate_mutations.py`；变异工具版本 pin 于 dev 依赖（范围上界，按 SOP §1），结果写 `reports/mutation/f007/mutation_report.json`（mutant-killed 报告）

## 3. 验证与验收任务

- [ ] T018 (`AC-001`, `AC-002`, `AC-003`): 运行执行层级、方法论与必需统计测试 — verify: `pytest -q tests/integration/test_f007_execution_tiers.py tests/unit/validation/test_methodology_gate.py tests/unit/evaluation/test_required_statistics.py`
- [ ] T019 (`AC-004`, `AC-005`, `AC-006`): 运行成本/稳定性、原子发布和身份属性测试 — verify: `pytest -q tests/unit/evaluation/test_cost_and_stability.py tests/integration/test_f007_atomic_publish.py tests/unit/experiment_store/test_identity.py`
- [ ] T020 (`AC-007`, `AC-008`): 运行综合、artifact contract 与 CLI 测试 — verify: `pytest -q tests/integration/test_f007_synthesis.py tests/contract/test_f007_artifact_schemas.py tests/integration/test_f007_cli.py`
- [ ] T021 (`AC-001`, `AC-002`, `AC-003`, `AC-005`): 运行 F007 定向变异并确认每个 mutant 被门禁杀死（`reports/mutation/f007/mutation_report.json` 无 survived 项） — verify: `pytest -q tests/mutation/test_f007_gate_mutations.py`
- [ ] T022 (`AC-001`, `AC-003`, `AC-004`, `AC-007`): 在**执行机**的不可变 crypto 快照跑四类正负控制并归档 manifest——绑定 snapshot ID 与 `value_digest`，证据落 `reports/f007/real_env/<run_id>/` 并记录 hostname 与 `device=cpu`；不得复用 T016 的 fixture 或命令 — verify: `ALPHAMILL_INTEGRATION=1 pytest -q tests/integration/test_f007_controls_real.py --snapshot <snapshot-id>`
- [ ] T023 (`AC-001`, `AC-002`, `AC-003`, `AC-004`, `AC-005`, `AC-006`, `AC-007`, `AC-008`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
- [ ] T024 (`FR-001`, `FR-004`, `NFR-001`, `AC-001`, `AC-003`): 承接 SC-002 的并发与故障注入集成测试——同 ID 并发 claim 只有一个成功、崩溃后 lease 超时才可接管、finalize 原子性（失败不产生部分 `cohort_verdict`）、registration 幂等重试不重复计数 — verify: `tests/integration/test_f007_concurrency.py`

- [ ] T025 (`FR-004`, `NFR-002`): 统计第二实现对照抽查（PRD FR3.7）——对高价值候选或统计实现变更，用独立实现（Vibe-Trading `quantlib_call` 或本仓手工第二实现）对照 BH-FDR/block bootstrap，**time-box 1 周**；对照对象、容差（估计量相对差 ≤1e-6，超出则显式记录差异与原因）与证据路径 `reports/second_impl/<experiment_id>/` 一并落档；超时不阻塞主链路 — verify: `tests/unit/evaluation/test_second_implementation.py`

### [TEST] 组：层 2 旅程验收轨（必填）

> 编写早、执行晚：以下条目在 Phase 1 先以红灯立起（夹具与断言先写），收尾全量执行；
> 每个旅程步骤至少一条可执行断言。缺失该组时 SDD Flow T3 开工门禁拒绝流转。

- [ ] T027 [TEST] (`US-001`, `AC-001`, `AC-011`): 旅程 US-001 端到端验收——固定 fixture 连跑两次 preview：报告在排除 provenance 时间戳后稳定、canonical 台账与留出预算台账均零行、preview 越权写 official population/留出被拒并留 `evaluation.gate_rejected`、CLI 首屏含 tier/data digest/首个失败原因、近似标注在报告中显式可见 — verify: `pytest -q tests/integration/test_f007_execution_tiers.py tests/integration/test_f007_cli.py`
- [ ] T028 [TEST] (`US-002`, `AC-002`, `AC-003`, `AC-004`, `AC-009`, `AC-010`, `AC-012`): 旅程 US-002 端到端验收——冻结 cohort 后跑正控制/白噪声/故意泄漏 canonical：正控制五阶段完整且样本量三级裁决正确、白噪声被统计门拦截、泄漏被方法论门拦截；成员未收齐时 finalize 非零且 cohort 保持 OPEN；拒绝者仍入分母（多成员批量夹具）；必需估计器异常时 stage 不为 PASS 且 `promotion_verdict` 不为 `promising`；manifest 记录三层无前视状态，最终确认窗统计量不出现在任何 Agent 可读产物 — verify: `pytest -q tests/unit/evaluation/test_required_statistics.py tests/unit/evaluation/test_cost_and_stability.py tests/unit/validation/test_methodology_gate.py tests/integration/test_f007_controls.py`
- [ ] T029 [TEST] (`US-003`, `AC-005`, `AC-007`, `AC-008`): 旅程 US-003 端到端验收——从 finalized canonical ledger 确定性重建 synthesis：拒绝者进入漏斗分母、五阶段损失按 stage/owner/mechanism 三维聚合、事实/推断/建议三栏齐备；只有 preview 产物时输出空 canonical 结果；report/curves 标量互推在容差内一致 — verify: `pytest -q tests/integration/test_f007_synthesis.py tests/contract/test_f007_artifact_schemas.py`

- [ ] T030: 回写 spec 的真实 tests/验收证据、BACKLOG 和 feature 状态 — verify: `python3 tools/verify.py`

## 4. 依赖与并行关系

- `T001,T002,T003 -> T004~T017`：先冻结上游、方法与权限夹具。
- `T004,T005 -> T006,T011,T012,T013`：CLI、发布和登记依赖身份与隔离。
- `T008,T009,T010 -> T011,T016,T017`：先有可独立测试的门，再组装 canonical 全链。
- `T009 -> T012`：cohort 级校正（BH-FDR/DSR/MinTRL）依赖成员级估计器实现；`T012 -> T013`：finalize CLI 依赖登记、收齐校验与 official population 投影实现。
- `T007 -> T010/T011`：阶段状态模型是 rolling split 与事件/原子发布实现的输入；`T012/T014 -> T016`：全链控制需 canonical registry（登记/收齐）与 synthesis（漏斗/失败汇总）实现。
- `T012/T013 -> T024`：并发 claim 与 finalize 原子性测试依赖登记与 CLI 实现。
- `T009/T016 -> T025`：第二实现对照以成员级统计实现与全链控制证据为对照对象。
- `T011,T012 -> T014,T015`：综合只消费已发布并登记的 canonical 证据。
- `T005 [P]` 可与 T004 并行：分别修改隔离能力与纯身份模块，不共享状态。
- `T027/T028/T029 -> T030`：三条旅程验收全绿后才回写 spec 验收证据与状态。

## 5. 明确后移

- PortfolioDef 构建、边际贡献与完整组合转换门 → FR4/M3 Feature：F007 只预留输入与阶段 schema。
- offline→decision-time parity、run_record 四桶、持久化 kill-switch 和启动对账 → F006/M3。
- DML、PBO、Reality Check 的通用化与阈值 → 独立研究 Feature：v0.2 只允许 optional diagnostics。
- F005 页面与 F005.1 台账视图 → F005/F005.1：只读 F007 schema，不复制口径。
