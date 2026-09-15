---
kind: feature
id: F007
version: "0.2"
related_features: [F002, F004]
topics: [evaluation, validation, evidence, experiments]
doc_kind: design
created: 2026-09-13
updated: 2026-09-13
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
- **实现约束**：研究只读有效 Parquet；执行层级显式传参；Agent 无 canonical writer/留出能力；
  必需门失败关闭；不引入 ml4t 运行时依赖

## 1. 技术概要与影响面

实现一条“冻结运行上下文 → 方法论预检 → 因子计算 → 分阶段评测 → 原子发布 → canonical
登记 → cohort 综合”的确定性流水线。文件 manifest/报告是研究真相源；索引仅是可重建投影。

- 前端：无；F005 后续读取版本化 artifact/schema。
- 后端 / API：新增 `alphamill.evaluation` CLI 与编排服务，不新增 HTTP 写入口。
- 存储：`reports/preview/` 与 `reports/bench/` 隔离；`reports/cohorts/` 保存预注册 cohort 和事件。
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
规则/窗口/成本配置、research_snapshot_id、code/build digest 与 seed。`execution_tier` 由物理根目录
和 capability 强制，`supersedes` 只表达谱系，二者均不参与身份。物理路径、Parquet
codec/row-group、文件 SHA、主机、PID、开始/结束时间与 duration 仅进 provenance。

### 3.2 目录与不可变事件

```text
reports/
├── research_snapshots/<snapshot_id>/manifest.json
├── preview/<experiment_id>/<attempt_id>/{manifest.json,report.json,curves.parquet,events.jsonl}
├── bench/<object_id>/<research_snapshot_id>/<experiment_id>/{manifest.json,report.json,curves.parquet,events.jsonl,registration.json}
└── cohorts/<cohort_id>/
    ├── cohort.json
    ├── events/<event_id>.json
    ├── cohort_verdict.json
    └── synthesis/<synthesis_id>/synthesis_report.json
```

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
cost/capacity、sample-size/stability、structured failure 与成员诊断 verdict。cohort 级 BH-FDR/DSR
和可晋级 `promotion_verdict` 只存在于 `cohort_verdict.json`。每个阶段状态只能是
`PASS | FAIL | UNDERPOWERED | INCOMPLETE | NOT_APPLICABLE`；`NOT_APPLICABLE` 需给原因，不能参与
通过计数。

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
  --symbol-map <digest> --universe-calendar <path> --config <path> --seed <int>

python -m alphamill.evaluation canonical \
  --factor <factor-ref> --snapshot <id> --cohort <frozen-cohort> \
  --config <path> --code-build-digest <sha256> --seed <int>

python -m alphamill.evaluation finalize-cohort --cohort <cohort-id>

python -m alphamill.evaluation synthesis --cohort <cohort-id>
```

CLI 仅解析参数和序列化结果；preview 的 `--latest` 模式要求显式 symbol-map digest 和
universe/calendar JSON，builder 将后者 canonicalize 后原子保存为
`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`，再发布 ResearchSnapshot 并显示
实际 ID；`--snapshot` 模式不重新选择这些输入。
`canonical` 缺 cohort、code digest、ResearchSnapshot 或规则版本时
返回非零。成员 canonical 成功只表示 `REGISTERED`，不输出可晋级 verdict；`finalize-cohort` 在
成员未收齐或存在非终态 attempt 时非零。成功响应打印 experiment ID/cohort ID、tier、state、
verdict 和 artifact URI；领域错误输出稳定 error code，不输出 PASS-like exit code。

稳定错误码：`E_INPUT_INVALID`、`E_DATA_DIGEST_MISMATCH`、`E_METHODOLOGY_REJECTED`、
`E_REQUIRED_METRIC_FAILED`、`E_CANONICAL_FORBIDDEN`、`E_COHORT_FROZEN`、`E_PUBLISH_INCOMPLETE`。

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

1. preview 可由 ResearchSnapshotBuilder 解析 latest，或两种 tier 读取既有 snapshot；builder 校验每个 F002 manifest/value digest、cutoff、覆盖范围和不可变 symbol-map artifact，并把显式 universe/calendar JSON 内容寻址保存后，原子发布 snapshot。
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

方法论门采用“能力声明 + 守卫注册”配对：标签、变换、join、forward-fill、跨 pair/operator
每新增一种 capability，测试必须证明存在对应 guard；未知 capability 默认拒绝。运行时守卫至少
断言 label endpoint 不跨折、embargo ≥ max horizon、transform fit indices ⊆ train indices、
as-of join 方向为 backward 且陈旧度有上限。

## 6. UI 与可观测性

无页面。CLI 首屏固定显示 tier/cohort/experiment ID、data/code digest、state/verdict 和首个失败原因。
结构化日志按 experiment/cohort/stage 关联；记录各阶段耗时、样本量、拒绝数与 artifact publish
状态，但不记录数据内容或凭据。

F005 通过只读 API/文件 reader 渲染 report、curves 与 synthesis；不得重算 BH-FDR、漏斗、
failure taxonomy 或 verdict。Grafana 只监控评测任务健康，不承载研究口径或门禁按钮。

## 7. 失败、恢复、安全与兼容

- 校验与失败映射：snapshot 成员/摘要/cutoff/映射日历不符 → `INCOMPLETE`；方法论/纯度门 → `FAIL`；统计估计器异常 →
  `INCOMPLETE`；证据不足 → `UNDERPOWERED`；成本不存活 → `FAIL/dead`。
- 重启与恢复：只消费完整发布目录；temp/无 registration 的目录不可见；同 ID 重试不重复计数。
- 权限边界：canonical writer 和留出 reader 作为显式 capability 注入；preview/Agent 构造器没有
  这些接口。任何环境变量只能提供普通路径默认值，不能升级 tier/权限。
- 兼容：逻辑 artifact URI 与物理路径分离；Windows/WSL 路径只进 provenance；schema reader
  允许当前版与前一版，未知高版本失败关闭。

统计函数不得 `except Exception -> warning/null`。可选 PBO/Reality Check/DML 诊断放独立
`optional_diagnostics`，状态和失败原因可见，但其缺失既不能推翻硬门失败，也不能制造硬门通过。

## 8. 测试策略与验收映射

| 验收项 | 测试层级 | 计划文件 / 场景 | 关键断言 |
|---|---|---|---|
| `AC-001` | integration + mutation | `tests/integration/test_f007_execution_tiers.py` | preview 无 canonical/holdout 写能力，越权必红 |
| `AC-002` | unit + property + mutation | `tests/unit/validation/test_methodology_gate.py` | label endpoint/PIT/max horizon/train-only fit/future-fill 全覆盖 |
| `AC-003` | unit + integration | `tests/unit/evaluation/test_required_statistics.py` | 估计器异常失败关闭，拒绝者在 cohort 分母 |
| `AC-004` | unit + golden | `tests/unit/evaluation/test_cost_and_stability.py` | 三档成本、breakeven、rolling split 与 dead 裁决 |
| `AC-005` | integration + fault injection | `tests/integration/test_f007_atomic_publish.py` | 任一文件失败均无可见半成品/PASS |
| `AC-006` | property + integration | `tests/unit/experiment_store/test_research_snapshot.py`、`test_identity.py` | latest 先冻结；codec/path 不入身份，成员/cutoff/映射日历进入 snapshot 身份 |
| `AC-007` | integration + golden | `tests/integration/test_f007_synthesis.py` | 只读 canonical、五阶段漏斗、三栏输出、确定重建 |
| `AC-008` | CLI integration | `tests/integration/test_f007_cli.py` | 非法 canonical 非零退出且 error code 稳定 |

另以 funding carry/BTC-ETH 截面动量、白噪声、故意 future-fill 四类 fixture 做端到端 golden；
对 guard 注册表、异常吞噬、preview writer、embargo 比较符与 artifact 完整性各做一次定向变异。

## 9. 已确认决策与残余风险

| 决策 / 风险 | 结论或缓解 | 理由 | 替代方案 / 后续 |
|---|---|---|---|
| 官方总体存储 | 冻结 cohort + 不可变 event 文件；索引可重建 | 符合 ADR-0005 研究真相源，避免可手改双真相 | 数据量大后可加 SQLite 投影 |
| preview/canonical 隔离 | 物理根目录 + capability 双重隔离 | 标签单隔离不足以防误写 | 不采用全局 env tier |
| 方法统计 | 最小自研协议，第二实现只做对照 | 硬门需可控失败语义 | 不依赖 ml4t 配套包运行 |
| 固定 90 天的 regime 风险 | v0.2 记录 regime 并实现 rolling split；最终留出纪律不改 | 单窗口结论有条件性 | 按 ADR-0003 路线滚动化 |
| 文件系统原子性 | temp 与目标必须同一文件系统；跨盘发布拒绝 | rename 才能提供可见性边界 | 对象存储后改 manifest commit protocol |

## 10. 待确认设计问题

无
