---
kind: feature
id: F007
version: "0.2"
related_features: [F002, F003, F004]
topics: [evaluation, validation, evidence, experiments]
doc_kind: design
created: 2026-09-13
updated: 2026-09-17
---

# F007：统一评测台与证据门禁 - 设计

> Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`

> **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
> 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
> 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。

## 0. 输入与约束

- **行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003
- **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dataset/version/value digest
- **F003 生成侧 Contract（只读摄入）**：`generation.run_completed`（仅 `status=completed` 的运行）与 `generation.candidate_rejected`（漏斗第一级）；算子能力登记表（FR-002 的方法论守卫已登记能力清单来源）；协同池 meta-factor（`generator="pool"` 的可执行 `FactorDef`）
- **F008 上游 Contract（只读摄入）**：point-in-time 宇宙台账内容寻址 artifact——按 digest 加载并提供 `universe_at(T)` 语义查询与 `schema_version`（F008 `IR-002`/`IR-003`）；F007 不实现宇宙扩容，也不解析 latest
- **实现约束**：研究只读有效 Parquet；执行层级显式传参；Agent 无 canonical writer/留出能力；
  必需门失败关闭；不引入 ml4t 运行时依赖

## 1. 技术概要与影响面

实现一条“冻结运行上下文 → 方法论预检 → 因子计算 → 分阶段评测 → 原子发布 → canonical
登记 → cohort 综合”的确定性流水线。文件 manifest/报告是研究真相源；索引仅是可重建投影。

- 前端：无；F005 后续读取版本化 artifact/schema。
- 后端 / API：新增 `alphamill.evaluation` CLI 与编排服务，不新增 HTTP 写入口。
- 存储：`reports/preview/` 与 `reports/bench/` 隔离；`reports/cohorts/` 保存预注册 cohort 和事件；`reports/holdout_budget/ledger.jsonl` 为 append-only 留出预算台账（只有 canonical capability 可追加）。
- Runtime：单次运行无守护进程；同 ID 通过原子 claim 幂等，失败可重试。
- Event / Evidence：report、curves、manifest、registration event、synthesis；全部 schema versioned。
- 文档 / 配置：新增方法/阈值配置 schema；阈值值由预注册 config 持有，不硬编码在评测函数。

## 2. 架构与模块边界

```text
CLI
 └─ EvaluationRunner
     ├─ ResearchSnapshotBuilder ── F002 ManifestReader
     ├─ ContextBuilder ── IdentityHasher
     ├─ MethodologyGate ── F002 SnapshotReader
     ├─ FactorEvaluator ── Statistics / Cost / Stability
     ├─ ArtifactPublisher ── reports/{preview|bench}/...
     └─ CanonicalRegistrar ── reports/cohorts/.../events/...

SynthesisBuilder ── finalized canonical cohort manifests + curves ── synthesis_report.json
```

模块放置：

- `src/alphamill/experiment_store/identity.py`：规范化语义上下文、计算 ID、校验 supersedes；
- `src/alphamill/experiment_store/research_snapshot.py`：冻结 dataset 版本集合、映射/日历摘要与 cutoff；
- `src/alphamill/experiment_store/population.py`：canonical claim、registration event 与可重建索引；
- `src/alphamill/experiment_store/synthesis.py`：只读 canonical 证据并生成综合报告；
- `src/alphamill/validation/methodology_gate.py`：能力清单、静态检查与运行时边界检查；
- `src/alphamill/factor_factory/bench/`：信号、统计、成本、稳定性与 artifact schema；
- `src/alphamill/evaluation/cli.py`：薄入口，不承载裁决逻辑。
- `src/alphamill/evaluation/upstream_contracts.py`：只读摄入 F003 的 `generation.*` 事件、算子能力登记表与协同池 `FactorDef`；F007 不写 F003 运行记录，也不解析 vendor 内部结构。

依赖方向固定为 CLI → orchestration → domain evaluators/store ports → F002 reader/filesystem。
bench 不读取环境变量、不决定 tier/窗口/cohort，也不写 official population。synthesis 不访问 preview。

## 3. 数据模型与 Migration

### 3.1 运行上下文与身份

```json
{
  "schema_version": 1,
  "execution_tier": "canonical",
  "upstream": {"kind": "factor", "id": "factor_sha256:..."},
  "cohort_id": "cohort_sha256:...",
  "method_config": {"id": "method-v1", "normalized": {}},
  "window": {"selection": ["...", "..."], "label_horizons": [1, 4, 24]},
  "cost_model": {"id": "cm-v1", "normalized": {}},
  "research_snapshot_id": "snapshot_sha256:...",
  "code_build_digest": "sha256:...",
  "seed": 7,
  "supersedes": null
}
```

规范化规则：UTF-8 canonical JSON、key 排序、时间统一 UTC ISO-8601、数值使用配置 schema 的
十进制定标格式、集合字段先去重再排序。`experiment_id` 只哈希 upstream ID、cohort、规范化
规则/窗口/成本配置、research_snapshot_id、code/build digest 与 seed。`universe_calendar_digest` 是 universe（F008 台账 digest）与 calendar（本 Feature calendar JSON digest）两个 artifact 的组合摘要。`execution_tier` 由物理根目录
和 capability 强制，`supersedes` 只表达谱系，二者均不参与身份。物理路径、Parquet
codec/row-group、文件 SHA、主机、PID、开始/结束时间与 duration 仅进 provenance。

### 3.2 目录与不可变事件

```text
reports/
├── research_snapshots/<snapshot_id>/manifest.json
├── holdout_budget/ledger.jsonl
├── preview/<experiment_id>/<attempt_id>/{manifest.json,report.json,curves.parquet,events.jsonl}
├── bench/<object_id>/<research_snapshot_id>/<experiment_id>/{manifest.json,report.json,curves.parquet,events.jsonl,registration.json}
└── cohorts/<cohort_id>/
    ├── cohort.json
    ├── events/<event_id>.json
    ├── cohort_verdict.json
    └── synthesis/<synthesis_id>/synthesis_report.json
```

`holdout_budget/ledger.jsonl` 是 append-only 追加台账（`DR-005`）：每行一次留出评估，仅 canonical capability 持有 append 句柄；preview/Agent 构造器不注入该句柄，越权追加即失败关闭并写 `evaluation.gate_rejected`。台账不提供 UPDATE/DELETE 路径。

`cohort.json` 在首个 canonical 运行前冻结，内容含 hypothesis family、全部候选承诺/纳入规则、
选择阶段、窗口、阈值和方法版本。每个承诺成员无论 PASS、FAIL、UNDERPOWERED 或 INCOMPLETE
都必须有终态 registration event；只有成员集合与承诺完全相等时，`finalize-cohort` 才计算
BH-FDR/有效独立数 DSR 等 cohort 级指标并原子写 `cohort_verdict.json`。成员 report 不回写，
最终调整后结论由 cohort verdict 关联。official population 是 `cohort.json + events/*.json +
cohort_verdict.json` 的确定性投影，不另建可手改真相表；SQLite/DuckDB 索引若存在，删除后必须
能完全重建。

每个 canonical artifact 目录只写一次。publisher 先在同一文件系统的 sibling temp 目录完成
文件写入、schema/hash/曲线-标量互推校验，再原子 rename；`registration.json` 最后生成。失败目录
保留在 quarantine 或清理为未发布 attempt，消费者只认带完整 manifest+registration 的目录。

### 3.3 报告 schema

`report.json` 包含 identity refs、stage results、rank IC/HAC uncertainty、quantile/decay、dedup、
cost/capacity、sample-size/stability、structured failure 与成员诊断 verdict、以及 `approximation`
（NFR-004：preview 采样/缩窗时的显式近似标注，字段含 `is_approximate` 与 `reduced_dimensions[]`；
canonical 恒为 `is_approximate=false`，不得因性能压力静默减少门禁或样本）。cohort 级 BH-FDR/DSR
和可晋级 `promotion_verdict` 只存在于 `cohort_verdict.json`。每个阶段状态只能是
`PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE`；`NOT_APPLICABLE` 需给原因，不能参与
通过计数。

`sample_tier` 三级（ADR-0003 样本量门槛）：`underpowered`（<30 笔，不判 PASS 也不判 FAIL）、
`provisional`（30~69 笔，最多临时 PASS、仅允许缩减仓位 paper）、`trustworthy`（≈≥69 笔，才允许完整
成本后 PASS/FAIL 判定）。`underpowered` / `provisional` 都不得计入北极星判据。

**术语表（冻结；spec FR-003/FR-005 与 AC-003/AC-004 引用同一份）**：

| 层 | 字段 | 枚举 | 说明 |
|---|---|---|---|
| 阶段状态 | `stage_results[].status` | `PASS \| FAIL \| UNDERPOWERED \| INCOMPLETE \| NOT_APPLICABLE` | 只描述单阶段结果；`PASS` 不是晋级结论 |
| 成本裁决 | `cost_verdict` | `cost_positive \| cost_negative \| cost_undetermined` | 三档成本后收益判定 |
| 样本量裁决 | `sample_tier` | `underpowered \| provisional \| trustworthy` | 见 §7 与 ADR-0003 |
| 成员晋升裁决 | `promotion_verdict` | `promising \| dead \| underpowered \| incomplete` | 只在 `cohort_verdict.json`，cohort FINALIZED 后才产生 |
| cohort 状态 | `cohort_verdict.status` | `OPEN \| FINALIZED` | 承诺成员未收齐时恒为 `OPEN`，不产生可晋级结论 |

**五阶段 ID（冻结；spec FR-003 引用同一清单）**：

| `stage_id` | 名称 | `owner` | 因子运行的适用性 |
|---|---|---|---|
| `signal_quality` | 信号质量 | `signal` | 必填 |
| `portfolio_transform` | 组合转换 | `portfolio` | 可为 `NOT_APPLICABLE`（需给原因） |
| `cost_capacity` | 成本/容量 | `cost` | 必填 |
| `temporal_stability` | 时序稳定 | `statistics` | 必填 |
| `execution_implementation` | 执行实现 | `execution` | 可为 `NOT_APPLICABLE`（需给原因） |

**失败维度 schema（`failure_taxonomy`，三维）**：每条失败记录必填
`{stage, owner, mechanism, error_code, first_seen, evidence_refs}`。`stage` 取上表枚举；
`owner` ∈ `data | signal | method | statistics | cost | execution | infra`；
`mechanism` ∈ `missing_input | invalid_input | capability_unguarded | lookahead | estimator_failure | publish_failure | underpowered | cost_negative`。
synthesis 按 `(stage, owner, mechanism)` 三维聚合；出现枚举外的取值即失败关闭。

`curves.parquet` 最小列集沿用架构 §4.2：UTC time、成本后权益、回撤、q1~q5/long-short 累计收益、
各 horizon rolling IC；列 metadata 记录 schema/return convention/window。标量摘要必须能从侧车
在容差内重算。

不需要数据库 Migration；schema 以 `schema_version` 前向演进，reader 支持当前版与前一版，
旧 artifact 不原地迁移。

## 4. 接口、Contract 与 Event

### API / CLI / Adapter Contract

```text
python -m alphamill.evaluation preview \
  --factor <factor-ref> --snapshot <id> --config <path> --seed <int>

python -m alphamill.evaluation preview \
  --factor <factor-ref> --latest <dataset,...> --cutoff <UTC> \
  --symbol-map <digest> --universe <digest|ref> --calendar <path> \
  --config <path> --seed <int>

python -m alphamill.evaluation canonical \
  --factor <factor-ref> --snapshot <id> --cohort <frozen-cohort> \
  --config <path> --code-build-digest <sha256> --seed <int>

python -m alphamill.evaluation finalize-cohort --cohort <cohort-id>

python -m alphamill.evaluation synthesis --cohort <cohort-id>
```

CLI 仅解析参数和序列化结果；preview 的 `--latest` 模式要求显式 symbol-map digest、**F008** universe artifact 引用（`--universe`）与 calendar 输入（`--calendar`）两个独立参数。universe 按 F008 `IR-002` 从 `lake/_metadata/universes/<digest>.csv` 加载并走 `universe_at(T)` 语义，**不复制进 reports**；calendar 由 builder canonicalize 后原子保存为
`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`（该路径只承载 calendar，universe 不合并进此文件；ADR-0007 的 `universe_calendar_digest` 由两个 digest 组合导出），再发布 ResearchSnapshot 并显示
实际 ID；`--snapshot` 模式不重新选择这些输入。
`canonical` 缺 cohort、code digest、ResearchSnapshot 或规则版本时
返回非零。成员 canonical 成功只表示 `REGISTERED`，不输出可晋级 verdict；`finalize-cohort` 在
成员未收齐或存在非终态 attempt 时非零。成功响应打印 experiment ID/cohort ID、tier、state、
verdict 和 artifact URI；领域错误输出稳定 error code，不输出 PASS-like exit code。

稳定错误码：`E_INPUT_INVALID`、`E_DATA_DIGEST_MISMATCH`、`E_METHODOLOGY_REJECTED`、
`E_REQUIRED_METRIC_FAILED`、`E_CANONICAL_FORBIDDEN`、`E_COHORT_FROZEN`、`E_PUBLISH_INCOMPLETE`。

### 上游 Contract（F003）

- **漏斗第一级只读摄入**：`generation.run_completed` 只在 `status=completed` 的运行上消费；`generation.candidate_rejected` 按原因码（未登记算子 / 前视 / 可达性不足 / 重复定义）计数。两者共同构成漏斗第一级，拒绝者仍计入分母。
- **算子能力登记表**：装载为方法论门的「已登记能力」清单；未登记 capability 默认拒绝（FR-002），因此守卫覆盖面随登记表单调增强。
- **协同池**：以 `generator="pool"` 的可执行 `FactorDef` 与普通因子走同一评测路径，不因来源或聚合形态获得豁免；其成员 `factor_id` 与权重作为 provenance 进入 manifest。
- 摄入只读且按 `schema_version` 消费：F007 不写 F003 侧记录，也不读取 vendor 内部结构。

### 信号来源与 FactorDef 适配（F004 / 人工种子）

F004 交付真实 Kronos 推理实例与 `/predict` 契约，但**不**升级 `signals_log` 内容，也不切换消费者路由；因此从信号到可评测 `FactorDef` 的适配契约由本 Feature 拥有：

- 信号型 `FactorDef` 由 `signals_log` dataset（F002 只读）派生，定义与 manifest 记录 `SignalFactorProvenance`：来源 dataset、`source` 分布、适配器版本、原始信号列与标签/horizon 映射。
- `source=placeholder` 的处理分层：**canonical 拒绝**（`E_INPUT_INVALID`，fail-closed，与 ADR-0003 一致）；**preview 允许**但报告必须标注 `signal_source=placeholder` 并置 `approximation=true`，且不得据此产生任何晋级结论。
- 适配器只做形状/语义映射，不改变信号数值；数值一致性由 `tests/contract/test_f007_upstream_contracts.py` 以 fixture 固定。

### Event / Trace Contract

`events.jsonl` 保存本次 run 内事件；canonical 的总体登记另写不可变 cohort event：

```json
{
  "schema_version": 1,
  "event_id": "sha256:...",
  "type": "evaluation.run_state_changed | evaluation.gate_rejected | evaluation.registered",
  "experiment_id": "sha256:...",
  "execution_tier": "canonical",
  "cohort_id": "sha256:...",
  "stage": "signal_quality",
  "from": "RUNNING",
  "to": "INCOMPLETE",
  "reason_code": "E_REQUIRED_METRIC_FAILED",
  "evidence_refs": []
}
```

`event_id` 由类型、experiment ID、状态迁移序号和 payload digest 导出。重复登记同一 event 是
幂等成功；同一 ID 不同 payload 是完整性错误。

## 5. Runtime、Workflow 与并发

1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围、**F008 universe artifact**（digest 与 `universe_at(T)` 语义）、不可变 symbol-map artifact，并把显式 calendar 输入内容寻址保存后，原子发布 snapshot。
2. ContextBuilder 只接收 snapshot ID 并解析其他引用；IdentityHasher 生成 experiment ID。
3. runner 以 `<experiment_id>.claim` 原子创建取得单写权；已有完整 canonical 直接幂等返回。
4. MethodologyGate 先跑能力/静态守卫，再构造 per-pair、label-end-aware purged splits。
5. evaluator 依次写五阶段结果；FactorDef 的组合/执行阶段标 `NOT_APPLICABLE`，不是 PASS。
6. publisher 在 temp 目录完成全部校验并 rename；canonical 随后写成员 registration event；
   finalize-cohort 收齐承诺成员后才计算 cohort 指标与最终裁决。

claim 包含 owner token 和启动时间。崩溃后只有恢复命令在确认无活进程、temp artifact 未发布且
超出配置 lease 后才可接管；正常运行不能偷锁。canonical registration 失败时运行保持
`EVIDENCE_READY` 但不属于 official population，重试只补同一幂等 registration。cohort finalize
使用独立原子 claim；失败不产生部分 `cohort_verdict`，修复后可按同一 cohort ID 重试。
`SC-002` 的同 ID 并发 claim、崩溃后 lease 接管与 finalize 原子性由 `tests/integration/test_f007_concurrency.py` 以故障注入取证。

方法论门采用“能力声明 + 守卫注册”配对：标签、变换、join、forward-fill、跨 pair/operator
每新增一种 capability，测试必须证明存在对应 guard；未知 capability 默认拒绝。运行时守卫至少
断言 label endpoint 不跨折、embargo ≥ max horizon、transform fit indices ⊆ train indices、
as-of join 方向为 backward 且陈旧度有上限。

## 6. UI 与可观测性

无页面。CLI 首屏固定显示 tier/cohort/experiment ID、data/code digest、state/verdict 和首个失败原因。
结构化日志按 experiment/cohort/stage 关联；记录各阶段耗时、样本量、拒绝数与 artifact publish
状态，但不记录数据内容或凭据。

F005 前端**只经** `src/alphamill/api/` 的统一只读 API 消费 report、curves 与 synthesis；文件 reader
只允许作为 API/后端内部 adapter（由 API 进程持有），**不得成为前端直读路径**（前端不直接读文件系统、
不托管产物静态目录）。前端不得重算 BH-FDR、漏斗、failure taxonomy 或 verdict。Grafana 只监控评测
任务健康，不承载研究口径或门禁按钮。

## 7. 失败、恢复、安全与兼容

- 校验与失败映射：snapshot 成员/摘要/cutoff/映射日历不符 → `INCOMPLETE`；方法论/纯度门 → `FAIL`；统计估计器异常 →
  `INCOMPLETE`；证据不足 → `UNDERPOWERED`（样本 `<30`，`sample_tier=underpowered`）；`30~69` 记 `provisional`，只允许缩减仓位 paper 且不得进入北极星判据；成本不存活 → `FAIL/dead`。
- 重启与恢复：只消费完整发布目录；temp/无 registration 的目录不可见；同 ID 重试不重复计数。
- 权限边界：canonical writer、留出 reader 与**最终确认窗 reader** 作为显式 capability 注入；preview/Agent 构造器没有
  这些接口。最终确认窗的任何统计量不得写入 Agent/preview 可读的 report/manifest/synthesis，违规即失败关闭
  （`E_CANONICAL_FORBIDDEN`）。任何环境变量只能提供普通路径默认值，不能升级 tier/权限。
- 兼容：逻辑 artifact URI 与物理路径分离；Windows/WSL 路径只进 provenance；schema reader
  允许当前版与前一版，未知高版本失败关闭。

统计函数不得 `except Exception -> warning/null`。可选 PBO/Reality Check/DML 诊断放独立
`optional_diagnostics`，状态和失败原因可见，但其缺失既不能推翻硬门失败，也不能制造硬门通过。

**无前视三层归属**：L1（AST 纯度与未来算子）由 MethodologyGate 在评测入口 fail-closed 执行；L2（独立逐 K 线重放审计）与 L3（信号缓存 merge/join 时间戳与陈旧度对齐）的 owner=F006/M3，F007 不实现审计器。manifest 的 `no_lookahead` 段逐层记录 `status`（`PASS`/`FAIL`/`not_yet_available`）与 `evidence_refs`，缺失层带 `owner`；L2/L3 非 `PASS` 时 `promotion_verdict` 不得为 `promising`，任何 paper 晋级请求失败关闭（`E_REQUIRED_METRIC_FAILED`）。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration + mutation | `tests/integration/test_f007_execution_tiers.py` | preview 无 canonical/holdout 写能力，越权必红 |
| `AC-002` | unit + property + mutation | `tests/unit/validation/test_methodology_gate.py` | label endpoint/PIT/max horizon/train-only fit/future-fill 全覆盖 |
| `AC-003` | unit + integration | `tests/unit/evaluation/test_required_statistics.py` | 估计器异常失败关闭，拒绝者在 cohort 分母；多成员 cohort 批量 fixture 验证分母完整 |
| `AC-004` | unit + golden | `tests/unit/evaluation/test_cost_and_stability.py` | 三档成本、breakeven、rolling split、三级样本量（`underpowered`/`provisional`/`trustworthy`）与 dead 裁决 |
| `AC-005` | integration + fault injection | `tests/integration/test_f007_atomic_publish.py` | 任一文件失败均无可见半成品/PASS |
| `AC-011` | contract + integration | `tests/contract/test_f007_artifact_schemas.py` | `approximation` 标注存在；canonical 非近似；POSIX 逻辑路径；CLI 首屏字段快照 |
| `AC-006` | property + integration | `tests/unit/experiment_store/test_research_snapshot.py`、`tests/unit/experiment_store/test_identity.py` | latest 先冻结；codec/path 不入身份，成员/cutoff/映射日历进入 snapshot 身份 |
| 输入契约（AC-006/AC-008） | contract | `tests/contract/test_f007_upstream_contracts.py` | F002/F003/F008 上游契约摄入与 `source=placeholder` 分层 |
| `AC-003` cohort 登记 | integration | `tests/integration/test_f007_canonical_registry.py` | 冻结 cohort、收齐校验、原子 finalize、official population 可重建 |
| `AC-003` 全链控制 | integration | `tests/integration/test_f007_controls.py` | 正控制/白噪声/泄漏四类 fixture；多成员分母完整 |
| 变异证据 | mutation | `tests/mutation/test_f007_gate_mutations.py` | 定向 mutant 全部被杀死；`reports/mutation/f007/mutation_report.json` |
| 第二实现对照 | unit | `tests/unit/evaluation/test_second_implementation.py` | 独立实现与自研统计在既定容差内一致 |
| `AC-007` | integration + golden | `tests/integration/test_f007_synthesis.py` | 只读 canonical、五阶段漏斗、三栏输出、确定重建 |
| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定；`signals_log` 的 `source=placeholder` 在 canonical 被拒、preview 标注 |
| `AC-001`/`AC-004` 真实环境 | real-env integration（执行机） | `tests/integration/test_f007_controls_real.py`，`ALPHAMILL_INTEGRATION=1` | 绑定不可变 snapshot ID/digest、记录 hostname；与 fixture 控制分属不同命令 |
| `AC-009` | unit + integration | `tests/unit/validation/test_methodology_gate.py`、`tests/integration/test_f007_execution_tiers.py` | 三层状态入 manifest；L2/L3 缺失时阻断晋级 |
| `SC-002` | integration + fault injection | `tests/integration/test_f007_concurrency.py` | 同 ID 并发 claim、崩溃后 lease 接管、finalize 原子性、registration 幂等 |
| `AC-010` | integration + mutation | `tests/integration/test_f007_execution_tiers.py` | 最终确认窗统计量不出现在 Agent/preview 可读产物；越权 fail-closed |

另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；
对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异，
逐 mutant 产出 kill 证据到 `reports/mutation/f007/mutation_report.json`（无 survived 项才算通过），
变异工具版本按 SOP §1 在 dev 依赖 pin 范围上界。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 官方总体存储 | 冻结 cohort + 不可变 event 文件；索引可重建 | 符合 ADR-0005 研究真相源，避免可手改双真相 | 数据量大后可加 SQLite 投影 |
| preview/canonical 隔离 | 物理根目录 + capability 双重隔离 | 标签单隔离不足以防误写 | 不采用全局 env tier |
| 方法统计 | 最小自研协议，第二实现只做对照（T025，time-box 1 周，证据落 `reports/second_impl/<experiment_id>/`） | 硬门需可控失败语义 | 不依赖 ml4t 配套包运行 |
| 固定 90 天的 regime 风险 | v0.2 记录 regime 并实现 rolling split；最终留出纪律不改 | 单窗口结论有条件性 | 按 ADR-0003 路线滚动化 |
| 文件系统原子性 | temp 与目标必须同一文件系统；跨盘发布拒绝 | rename 才能提供可见性边界 | 对象存储后改 manifest commit protocol |

## 10. 待确认设计问题

无
