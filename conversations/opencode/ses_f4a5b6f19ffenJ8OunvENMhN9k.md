---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f4a5b6f19ffenJ8OunvENMhN9k"
title: "F007 independent code review round 1 (@oracle subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-18T17:50:56Z"
updated_at: "2026-09-18T17:55:42Z"
tokens_input: 197337
tokens_output: 3656
cost: 0.0
parent_id: "ses_f4b709dbdffevQ17e9JKDUhkz6"
---

# F007 independent code review round 1 (@oracle subagent)

## user · 2026-09-18T17:50:56Z

You are the INDEPENDENT REVIEWER for a feature code review (round 1, full-scan). I am the author; I am explicitly switching to reviewer role, and I need your independent read because self-approval is worthless.

## Repository / baseline (declare-recheck basis)
- Worktree: `/home/georg/projects/alphamill-eval-gates` (git worktree on branch `feat/F007-evaluation-gates`)
- Baseline: `git rev-parse --short HEAD` (should be 99e8092), diff vs `main` = 29 commits, 90 files, ~15k insertions
- Use the worktree's own venv: `.venv/bin/python` (it resolves `alphamill` to THIS worktree's `src/`). Run any command with `workdir=/home/georg/projects/alphamill-eval-gates`.
- Feature docs (behavior/technical truth):
  - `docs/features/0.2/F007-evaluation-gates/spec.md`
  - `docs/features/0.2/F007-evaluation-gates/design.md`
  - `docs/features/0.2/F007-evaluation-gates/tasks.md`
- Existing gates: `python3 tools/verify.py` (the only public verify entry).

## Scope: review the F007 implementation diff (`git diff main...HEAD`) for CORRECTNESS only
Ignore pure style/naming/duplication (that's a separate quality channel). Prioritise the paths the design itself flags as high-risk (`design.md` §8): canonical writer, holdout access, statistics failure semantics, artifact publishing, plus the evidence-gate machinery.

## Frozen invariants to test the code against (quote design/spec when you cite)
1. **Canonical 禁止动态 latest**; preview latest must freeze first (ADR-0007 decision 5).
2. **universe 与 calendar 是两个独立 artifact**，分别校验内容摘要；`universe_calendar_digest = sha256(canonical_json({"universe":…,"calendar":…}))` 冻结（DR-006）。
3. **身份只哈希语义字段**：`execution_tier` 与 `supersedes` 不参与 `experiment_id`；`snapshot_id` 只哈希语义字段（ADR-0006 决策 3 / ADR-0007 决策 3）。
4. **两层枚举不得互相替代**：阶段状态（PASS/FAIL/UNDERPOWERED/INCOMPLETE/NOT_APPLICABLE）vs `promotion_verdict`；必需阶段不得记 NOT_APPLICABLE 或伪记 PASS（FR-003）。
5. **`promotion_verdict` 冻结优先级表**（design §3.3）：rejected > incomplete > underpowered > dead > blocked_pending_audit > provisional > promising；**`cost_negative` 必须是 `dead` 而不是 `incomplete`**（FR-005）。
6. **失败关闭**：统计估计器异常不得降级为 warning/null；`except Exception` 不得吞掉门禁失败（design §7）。
7. **preview 不得写 canonical / 留出预算 / official population**；越权即 `E_CANONICAL_FORBIDDEN` 并留拒绝事件（FR-001/NFR-003）。
8. **manifest 必须逐层记录三层无前视状态**（L1 owner=F007，L2/L3 owner=F006/M3，缺失层 `not_yet_available`，非 PASS 即阻断晋级）（FR-007）。
9. **发布原子性**：同盘 temp → 校验 → rename；失败不留可见半成品；callation registration.json 最后写（design §3.2 / AC-005）。
10. **synthesis 只消费 canonical**，绝不混入 preview；拒绝者仍入漏斗分母（FR-004/FR-006）。
11. **回写只搬运不重算**；定义面写入即 `E_CANONICAL_FORBIDDEN`（FR-008/DR-008）。
12. **样本量三级半开区间** `[0,30)`/`[30,69)`/`[69,∞)`（FR-005）。

## What I want from you (bounded output)
Read the diff plus the specific modules it introduces (`src/alphamill/{evaluation,experiment_store,validation,factor_factory/bench}/**`). Focus on: does the code actually enforce the invariants above, and are there **logic bugs, race conditions, boundary errors, or fail-open paths**?

Report findings, each with:
- severity (Critical / High / Medium / Low)
- category: correctness | test-coverage
- location: `file:line`
- title (one line)
- why it's wrong (cite the invariant or give a concrete counterexample / failing input)
- suggested fix (one line)

Rules:
- **Do not report style/naming/duplication.**
- If you claim a bug, give a concrete trigger (input/sequence) — no "could be risky" hand-waving.
- Explicitly list which of the 12 invariants you verified as correctly enforced (so I know coverage).
- You are read-only: do not edit files. You may run tests/read code.
- Keep it under ~800 words; findings table + verified-invariants list.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-18T17:50:56Z

- **tool**: `skill({"name": "review-convergence", "user_message": "Independent reviewer, round 1 full-scan correctness review of F007 diff in /home/georg/projects/alphamill-eval-gates vs main. Read-only. Focus 12 frozen invariants and specified modules; bounded findings under 800 words."})`


> [reasoning] **Preparing for review with convergence skill**

  <details><summary>tool output</summary>

  ```text
## Skill: review-convergence

**Base directory**: /home/georg/projects/skills-manager-backup/review-convergence

Base directory for this skill: /home/georg/projects/skills-manager-backup/review-convergence/
File references (@path) in this skill are relative to this directory.

# Review Convergence

> 优先级:本 skill 优先于任何一次性的 code-review skill(包括 `review-changes`、
> `code-review-agent` 之类)。那些只是报告生成器,没有停止条件——正是本 skill 要修的
> 失效模式。真正一次性、无后续的小审查,可按第 0 节缩减轮次,但仍走本流程。
> 项目 CLAUDE.md 要求优先用 code-review-graph MCP 工具时,把它当作本流程的**取证手段**,
> 而不是替代本流程。

十轮审查还能挑出中等问题、修复还大概率引入新问题——这不是审查不够仔细,是流程没有
收敛条件。"审到审查者没意见为止"不是良定义的停止条件:只要投入足够注意力,任何代码
都能挑出新问题。本skill的目的是让审查在有限轮次内收敛,而不是无限发散。

## 0. 项目适配(每次先做,不要跳过)

在开始之前,读取当前仓库的 `CLAUDE.md` / `AGENTS.md`(如果存在),提取:
- 该项目自己的测试/回归规范(例如"每次修复必须补充回归测试"这类硬性要求)
- 已知的历史教训(例如"assert 被悄
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:51:05Z

- **tool**: `bash({"command": "git rev-parse --short HEAD && git branch --show-current && git status --short && git diff --stat main...HEAD && git diff --name-only main...HEAD", "workdir": "/home/georg/projects/alphamill-eval-gates", "timeout": 120000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/CLAUDE.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/AGENTS.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/spec.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/design.md", "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/tasks.md", "limit": 2000})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "F007 evaluation gates high-risk implementation: canonical writer, preview latest freezing, universe/calendar artifacts and digests, experiment_id snapshot_id semantic hashing, stage status and promotion verdict priority, statistics estimator failure handling, preview authorization, no-lookahead manifest layers, atomic artifact publishing and registration.json ordering, synthesis canonical filtering and funnel denominator, bac
…[truncated])`


> [reasoning] **Planning parallel git and docs reading**
I’m establishing the declared baseline and extracting the repository’s review rules before inspecting implementation paths. I’ll treat any HEAD drift or uncommitted files as a re-baseline issue, then map each invariant to concrete code and tests.

  <details><summary>tool output</summary>

  ```text
99e8092
feat/F007-evaluation-gates
 .sdd/evidence/red-green-cycles.md                  |  67 +++
 .sdd/sdt-gate.json                                 |  56 ++
 BACKLOG.md                                         |   2 +-
 CLAUDE.md                                          |   2 +-
 docs/features/0.2/F007-evaluation-gates/spec.md    |  32 +-
 docs/features/0.2/F007-evaluation-gates/tasks.md   |  64 +-
 .../20260918T173439Z-1368718/manifest.json         | 261 +++++++++
 ...fa83ec2309416bb4462804e50644814a03f6e1b8c6.json |   1 +
 .../manifest.json                                  |  38 ++
 src/alphamill/evaluation/__init__.py               |   1 +
 src/alphamill/evaluation/__main__.py               |  10 +
 src/alphamill/evaluation/canonical.py              | 332 +++++++++++
 src/alphamill/eval
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/CLAUDE.md</path>
<type>file</type>
<content>
1: # AlphaMill
2: 
3: AI 原生的加密量化研究与交易管线：以 AI 因子工厂为核心，贯通数据治理 → 假设与因子 →
4: 证据评测 → 组合与策略 → Freqtrade 执行 → 监控归因与复盘（中文别名：淘沙）。
5: 
6: ## 当前结构
7: 
8: - `docs/alphamill-prd.md`：正式 PRD（产品真相源），产品判断以此为准。
9: - `docs/alphamill-architecture.md`：四平面架构与接口契约（架构真相源），随实现迭代。
10: - `docs/alphamill-research-factor-mining.md`：因子挖掘/ML 选型调研证据（决策已提炼至 ADR-0001）。
11: - `docs/alphamill-integration.md`：数据桥 / Vibe-Trading / Freqtrade 集成操作细节（依赖策略见 ADR-0002）。
12: - `docs/decisions/`：ADR——0001 挖掘引擎选型 / 0002 依赖管理策略 / 0003 验证门禁不降级 / 0004 组合构建（因子→策略映射） / 0005 呈现与观测架构 / 0006 证据边界与实验身份 / 0007 研究快照绑定（dataset 独立版本 + ResearchSnapshot） / 0008 北极星改为在跑组合持续盈利（产能降级为分母与能力标定）。
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/AGENTS.md</path>
<type>file</type>
<content>
1: # AlphaMill
2: 
3: 见 `CLAUDE.md`（项目说明与开发约定，对所有 AI 编码工具通用）。

(End of file - total 3 lines)
</content>

[Project README: /home/georg/projects/alphamill-eval-gates/README.md]
# AlphaMill（淘沙）

> 以 AI 因子工厂为核心的加密量化研究与交易管线。

AlphaMill 将数据治理、假设生成、因子评测、严格验证、组合构建、交易执行和绩效复盘连接为
可复现的闭环，目标是持续发现并运营成本后有效的 Alpha。候选吞吐量只是漏斗分母与能力
标定，不是项目目的；有效独立性、证据可信度、组合边际贡献和线上表现共同决定研究产出是否有价值。

## 核心闭环

```text
数据快照 → AI 因子工厂 → 证据评测与验证 → 组合与策略 → Freqtrade 执行
    ▲                                                      │
    └──────── 新假设 ← AI/人工复盘 ← 监控、归因与生命周期 ──┘
```

- **AI 负责探索**：生成假设和因子、分析失败、提出下一轮实验。
- **规则负责证据**：成本、多重检验、留出预算、最终确认和无前视审计均由确定性代码裁决。
- **组合负责转化**：单因子和协同池 meta-factor 只有对现有组合产生正边际贡献才构成可信产出。
- **执行负责反馈**：Freqtrade 承担 dr
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: status: code-reviewing
6: status_evidence: SDT 八闸 PASS（.sdd/sdt-gate.json）；T023 执行机真实环境取证完成于 qiaozhi-lt（RTX 4060）；tools/verify.py 全绿
7: branch: feat/F007-evaluation-gates
8: gate_version: 1
9: related_features: [F002, F003, F004, F008]
10: topics: [evaluation, validation, evidence, experiments]
11: doc_kind: spec
12: created: 2026-09-13
13: updated: 2026-09-19
14: ---
15: 
16: # F007：统一评测台与证据门禁
17: 
18: > Owner: Georg | Target: v0.2.x
19: 
20: ## 0. 来源与意图
21: 
22: - **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
23: - **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
24: - **上游 Contract
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004, F008]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: design
8: created: 2026-09-13
9: updated: 2026-09-18
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束**：`tasks.md` §3 的 `[TEST]` 组（层 2 旅程验收轨，编写早、执行晚）是进入代码
17: > 开发的硬性前置门；约束的落地形态与执行规则见 `tasks.md`（design 只声明该约束，不展开步骤）。
18: 
19: ## 0. 输入与约束
20: 
21: - **行为契约**：`spec.md` FR-001~FR-008、DR-001~DR-008、TR-001~TR-003、IR-001~IR-003
22: - **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
23: - **ADR / 上游 Contract**：ADR-0003、ADR-000
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004, F008]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: tasks
8: created: 2026-09-13
9: updated: 2026-09-18
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`。
19: - 技术方案与边界：`design.md`。
20: - 每项任务完成并跑对应 verify 后立即勾选；契约变化先修三件套。
21: - 任务编号按追加顺序分配，不代表执行顺序（回写轨 T018/T028 为检视轮追加后按阶段重排的编号）；执行顺序以 §4 依赖图为准。
22: - `[TEST]` 组（§3）是开发前置门：从 US-001/US-002/US-003 旅程步骤派生（每步骤 ≥1 条可执行断言），编写早（Phase 1 先立红灯）、执行晚（收尾全量跑）；缺失即被 SDD Flow T3 拒绝流转。
23: - 属性测试与变异证据可复现：属性
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
**Exploration: F007 evaluation gates high-risk implementation: canonical writer, preview latest freezing, universe/calendar artifacts and digests, experiment_id snapshot_id semantic hashing, stage status and promotion verdict priority, statistics estimator failure handling, preview authorization, no-lookahead manifest layers, atomic artifact publishing and registration.json ordering, synthesis canonical filtering and funnel denominator, backfill write restrictions, sample-size thresholds. Include relevant tests and call paths.**

Found 23 symbols across 5 files.

**Blast radius — what depends on these (update/verify before editing)**

- `freeze` (MarketGameSim/src/market_game_sim/experiment/h2/protocol.py:212) — 28 callers in `MarketGameSim/src/market_game_sim/experiment/h2/evidence_guard.
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:51:38Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "src/alphamill/evaluation/canonical.py src/alphamill/evaluation/publisher.py src/alphamill/evaluation/canonical_ops.py src/alphamill/evaluation/pipeline.py src/alphamill/evaluation/canonical_result.py exact source and call paths", "maxFiles": 12})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "src/alphamill/experiment_store/research_snapshot.py src/alphamill/experiment_store/universe_calendar.py src/alphamill/experiment_store/identity.py src/alphamill/experiment_store/experiment_context.py exact source, identity payload and digest validation", "maxFiles": 12})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "src/alphamill/experiment_store/population.py src/alphamill/experiment_store/promotion.py src/alphamill/experiment_store/dedup.py src/alphamill/experiment_store/synthesis.py src/alphamill/evaluation/registry_writeback.py exact source and call paths", "maxFiles": 12})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "src/alphamill/factor_factory/bench/statistics.py src/alphamill/factor_factory/bench/stage_model.py src/alphamill/factor_factory/bench/cost.py src/alphamill/factor_factory/bench/stability.py src/alphamill/validation/no_lookahead.py src/alphamill/validation/methodology_gate.py exact source and exception semantics", "maxFiles": 14})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill-eval-gates", "query": "src/alphamill/evaluation/capabilities.py src/alphamill/experiment_store/holdout_budget.py src/alphamill/evaluation/preview.py src/alphamill/evaluation/rejection.py src/alphamill/evaluation/events.py exact source authorization and rejection event paths", "maxFiles": 12})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill-eval-gates/src/alphamill", "include": "*.py", "pattern": "except Exception|except BaseException|warning\\(|warnings\\.warn|latest|NOT_APPLICABLE|registration\\.json|os\\.replace|rename\\(|replace\\(", "output_mode": "content", "head_limit": 500})`


> [reasoning] **Planning targeted Codegraph queries**
Baseline matches `feat/F007-evaluation-gates@99e8092`; the worktree is clean. The first graph query was noisy across a parent index, so I’m narrowing by exact F007 file paths and will use direct source reads only where the index omits details.

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/evaluation/canonical.py src/alphamill/evaluation/publisher.py src/alphamill/evaluation/canonical_ops.py src/alphamill/evaluation/pipeline.py src/alphamill/evaluation/canonical_result.py exact source and call paths**

Found 18 symbols across 2 files.

**Blast radius — what depends on these (update/verify before editing)**

- `publish` (alphamill-eval-gates/src/alphamill/evaluation/publisher.py:149) — 12 callers in `alphamill-eval-gates/src/alphamill/evaluation/canonical.py`, `alphamill-eval-gates/src/alphamill/evaluation/rejection.py`; tests: `alphamill-eval-gates/tests/integration/test_f007_atomic_publish.py`
- `PublishError` (alphamill-eval-gates/src/alphamill/evaluation/publisher.py:45) — 7 callers in `alphamill-eval-gates/src/alphamill/evaluation/cli.py`, `a
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/experiment_store/research_snapshot.py src/alphamill/experiment_store/universe_calendar.py src/alphamill/experiment_store/identity.py src/alphamill/experiment_store/experiment_context.py exact source, identity payload and digest validation**

Found 48 symbols across 2 files.

**Blast radius — what depends on these (update/verify before editing)**

- `digest` (MarketGameSim/src/market_game_sim/experiment/stress_protocol.py:158) — 7 callers in `MarketGameSim/src/market_game_sim/eventlog/digest.py`, `MarketGameSim/src/market_game_sim/experiment/factorial.py`, `MarketGameSim/src/market_game_sim/rng/__init__.py`, `MarketGameSim/src/market_game_sim/rng/distributions.py` +3 more; ⚠️ no covering tests found
- `snapshot` (deepseek-harness/packages/client/ui-chat/src/clie
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/experiment_store/population.py src/alphamill/experiment_store/promotion.py src/alphamill/experiment_store/dedup.py src/alphamill/experiment_store/synthesis.py src/alphamill/evaluation/registry_writeback.py exact source and call paths**

Found 37 symbols across 3 files.

**Blast radius — what depends on these (update/verify before editing)**

- `PromotionError` (alphamill-eval-gates/src/alphamill/experiment_store/promotion.py:57) — 3 callers in `alphamill-eval-gates/src/alphamill/experiment_store/promotion.py`; tests: `alphamill-eval-gates/tests/integration/test_f007_canonical_registry.py`
- `SynthesisError` (alphamill-eval-gates/src/alphamill/experiment_store/synthesis_analysis.py:24) — 8 callers in `alphamill-eval-gates/src/alphamill/evaluation/cli.py`, `alpha
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/factor_factory/bench/statistics.py src/alphamill/factor_factory/bench/stage_model.py src/alphamill/factor_factory/bench/cost.py src/alphamill/factor_factory/bench/stability.py src/alphamill/validation/no_lookahead.py src/alphamill/validation/methodology_gate.py exact source and exception semantics**

Found 37 symbols across 2 files.

**Blast radius — what depends on these (update/verify before editing)**

- `StatisticsError` (alphamill-eval-gates/src/alphamill/factor_factory/bench/statistics.py:28) — 13 callers in `alphamill-eval-gates/src/alphamill/factor_factory/bench/multiplicity.py`, `alphamill-eval-gates/src/alphamill/factor_factory/bench/statistics.py`; tests: `alphamill-eval-gates/tests/unit/evaluation/test_required_statistics.py`
- `StabilityReport` (al
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/evaluation/capabilities.py src/alphamill/experiment_store/holdout_budget.py src/alphamill/evaluation/preview.py src/alphamill/evaluation/rejection.py src/alphamill/evaluation/events.py exact source authorization and rejection event paths**

Found 21 symbols across 5 files.

**Blast radius — what depends on these (update/verify before editing)**

- `SessionEventSource` (deepseek-harness/packages/api/session-controller/src/client/contract/events.ts:117) — 5 callers in `deepseek-harness/packages/api/session-controller/src/client/index.ts`, `deepseek-harness/packages/api/session-controller/src/client/sessions/service.ts`, `deepseek-harness/packages/client/ui-conversation/src/client/conversation/assembly.ts`; ⚠️ no covering tests found

**Relationships**

**referenc
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 147 match(es) in 40 file(s)

/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/kronos_ic_decay_eval.py
  58: safe_exchange = exchange.replace("'", "''")
  59: safe_symbol = symbol.replace("'", "''")

/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/train_low_frequency_walk_forward_baselines.py
  138: except Exception as exc:
  152: column = f"pair_{pair.replace('/', '_')}"
  216: train[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)
  219: test[feature_columns].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy(dtype=float)

/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/kronos_rankic_eval.py
  58: safe_exchange = exchange.replace("'", "''")
  59: safe_symbo
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:52:08Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/canonical.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/run_config.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/research_snapshot.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/identity.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/experiment_context.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/population.py", "limit": 500})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/synthesis.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/registry_writeback.py", "limit": 350})`


> [reasoning] **Planning parallel reading for critical files**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/canonical.py</path>
<type>file</type>
<content>
1: """canonical 运行与 abandon（`FR-001`/`IR-001`/`IR-002`/`TR-003`；任务 T013）。
2: 
3: canonical 与 preview 的差别是**门禁强度**，不是流程分支：
4: 
5: - 必须显式给出冻结 cohort、已发布 ResearchSnapshot、规则版本与 `--code-build-digest` 期望值；
6:   digest 由 runner 自行计算（不接受调用方自报），工作树脏或无法判定即拒绝（`IR-001`）；
7: - 入口先跑方法论门 L1 静态纯度 fail-closed（`FR-002`/`FR-007`）；canonical 恒为非近似
8:   （`NFR-004`），`source=placeholder` 一律拒绝（`DR-007`）；
9: - 产物发布到 `reports/bench/`，必须带 `registration.json`，随后写 `evaluation.registered`；
10: - 同语义重跑**幂等返回既有实验**（同一 `experiment_id`，不重复计数）。
11: 
12: v0.2 的因子输入经由 `--signals` + `--expression` 夹具接缝；F003 注册表接线后由 `--factor` 解析
13: 替换该接缝，门禁与产物契约不变。abandon / finalize-cohort 见 `canonical_ops`。
14: """
15: 
16
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/run_config.py</path>
<type>file</type>
<content>
1: """preview 的输入装载与快照解析（任务 T006）。
2: 
3: - `load_run_config`：预注册 method/cost/window 配置（阈值不硬编码在评测函数，`FR-004`）；
4: - `load_unified_frame`：统一列集的信号夹具（T002 冻结的列契约）；
5: - `resolve_snapshot`：显式 `--snapshot` 直接读取；`--latest` **先解析并冻结**成 ResearchSnapshot
6:   再返回（ADR-0007 决策 5——canonical 禁止动态 latest，preview 也必须先冻结）；
7: - `preview_cohort_id`：未显式给 cohort 时的确定性 preview 专属引用（永不登记）。
8: """
9: 
10: from __future__ import annotations
11: 
12: import csv
13: import json
14: from collections.abc import Mapping, Sequence
15: from dataclasses import dataclass
16: from datetime import datetime
17: from pathlib import Path
18: from typing import Any
19: 
20: from alphamill.data_bridge import
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/research_snapshot.py</path>
<type>file</type>
<content>
1: """ResearchSnapshot builder/reader（ADR-0007；F007 `DR-001`/`DR-006`，任务 T001）。
2: 
3: 契约（ADR-0007「决策」第 2/3 条，字段名冻结）：
4: 
5: ```text
6: ResearchSnapshot = {
7:   schema_version, snapshot_id, cutoff_time,
8:   members: {<dataset>: {data_version, value_digest, as_of_fidelity,
9:                         event_time_min, event_time_max}},
10:   symbol_map_digest, universe_digest, calendar_digest, universe_calendar_digest,
11:   provenance: {created_at, artifact_path, member_manifest_paths,
12:                symbol_map_path, universe_path, calendar_path}
13: }
14: ```
15: 
16: 本模块负责**冻结与持久化**；身份规则见 `identity`，calendar 契约见 `universe_calendar`，
17: F008 universe 消
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/identity.py</path>
<type>file</type>
<content>
1: """ResearchSnapshot 身份：规范化编码、内容 ID 与两级摘要组合（ADR-0007；F007 `DR-001`）。
2: 
3: 这是身份规则的**唯一实现点**，`snapshot_id` 只哈希语义字段：
4: 
5: ```text
6: snapshot_id = sha256(canonical_json({
7:   schema_version, cutoff_time,
8:   members: [<按 dataset 名排序的成员六元组>],
9:   symbol_map_digest, universe_calendar_digest,
10: }))
11: ```
12: 
13: 创建时间、路径、Parquet codec、文件 SHA 与主机只进 `provenance`；相同语义必须得到相同 ID
14: （`NFR-002`/`SC-003`）。`universe_calendar_digest` 由 universe 与 calendar 两个独立 artifact 的
15: digest 按 ADR-0007 冻结公式组合导出，不回退为「单一 JSON 文件摘要」（`DR-006`）。
16: 
17: **两级内容 ID**（ADR-0007 决策 3 的同一原则，`DR-002`）：先对每个规范化的语义子对象取
18: **一级内容摘要**（component digest），再由这些子摘要组合出**二级 ID**——父级哈希子摘要，
19: 不重复哈希子
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/experiment_context.py</path>
<type>file</type>
<content>
1: """`ExperimentContext`：实验语义上下文的规范化、两级内容 ID 与 supersedes 谱系（`DR-002`）。
2: 
3: `experiment_id` **只**哈希语义字段（ADR-0006 决策 3）：
4: 
5: ```text
6: level 1  method_config_digest / window_digest / cost_model_digest   （子对象内容摘要）
7: level 2  experiment_id = sha256(canonical_json({
8:            schema_version, upstream, cohort_id,
9:            method_config_digest, window_digest, cost_model_digest,
10:            research_snapshot_id, code_build_digest, seed }))
11: ```
12: 
13: 父级哈希**子摘要**而不是重复哈希子对象的输入（与 ADR-0007 的
14: `universe_calendar_digest → snapshot_id` 同一条规则）。`execution_tier` 与 `supersedes` 明确
15: **不参与身份**：层级由 capability 强制，`supersedes` 只表达谱系（design §3.1）；
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/population.py</path>
<type>file</type>
<content>
1: """canonical 登记与官方总体（`DR-003`/`DR-004`/`TR-003`/`AC-003`；任务 T012）。
2: 
3: - `cohort.json` 在首个 canonical 运行前**冻结**，内容寻址（`cohort_sha256:<digest>`，`frozen_at`/
4:   `frozen_by` 只进 provenance、不入身份），冻结后不可原地修改；
5: - 每个承诺成员无论证据完整（`EVIDENCE_READY`）、`REJECTED` 还是 `INCOMPLETE` 终态，都必须有终态
6:   registration event（`evaluation.registered`）——被拒者仍计入漏斗分母（`FR-004`）；
7: - 只有「承诺成员集合 == 终态登记集合」时才允许 `finalize-cohort`（否则 `E_COHORT_FROZEN`），
8:   并**原子**写出 `cohort_verdict.json`（失败不产生部分 verdict）；
9: - official population 是 `cohort.json + events/*.json + cohort_verdict.json` 的**确定性投影**，
10:   不另建可手改真相表；删除派生索引必须能完全重建。
11: """
12: 
13: from __future__ import annotations
14: 
15: import jso
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/synthesis.py</path>
<type>file</type>
<content>
1: """综合报告：只读 canonical 证据的合成（`FR-006`/`AC-007`/`AC-012`；任务 T014）。
2: 
3: **只消费 canonical**：输入是已冻结 cohort、终态登记与 `cohort_verdict.json`；**从不读取 preview**
4: 产物。若只有 preview 产物（cohort 台账不存在），输出**空 canonical 结果**（计数为零、成员为空），
5: 不混入任何 preview 指标（`US-003` 场景 2）。
6: 
7: 聚合与三栏输出见 `synthesis_analysis`（五阶段漏斗、失败三维、事实/推断/建议）。漏斗第一级只读
8: 摄取 F003 的 `generation.run_completed`（仅 `status=completed`）与 `generation.candidate_rejected`
9: （按原因码），拒绝者仍计入分母（`FR-004`）。`synthesis_id` 是语义内容摘要，`generated_at` 是墙钟、
10: 不参与身份——同一 canonical 台账必须确定性重建出同一报告（`SC-004`）。
11: """
12: 
13: from __future__ import annotations
14: 
15: import json
16: import os
17: from collections.abc import Iterable, Mappin
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/registry_writeback.py</path>
<type>file</type>
<content>
1: """F003 注册表**评测面**回写适配器（`FR-008`/`DR-008`/`AC-013`；任务 T018）。
2: 
3: F007 是注册表**评测面**的唯一写入 owner，规则是**只搬运、不重算**：
4: 
5: - cohort `FINALIZED` 后才回写（否则 `E_COHORT_FROZEN`）；载荷严格取 `DR-008` 字段集，其中
6:   `promotion_verdict` / `sample_tier` / `dedup` 全部来自 T012 finalize 已产出的结论；
7: - 载荷**不含任何 lifecycle 状态字段**（衰减/下线判定后移 M3/F006）——出现即拒绝；
8: - **定义面不可写**：`FactorDef` 表达式/定义摘要/定义版本任何写入尝试即 `E_CANONICAL_FORBIDDEN`
9:   （`AC-013` 场景「定义面越权写入」）；
10: - 追加是 append-only 且按 `(cohort_id, factor_id)` 幂等：重复回写同一条目不产生第二行，也不
11:   重复计数（`FR-004` 的「诊断性重算不重复计数」在回写面同样成立）。
12: """
13: 
14: from __future__ import annotations
15: 
16: import json
17: from collections.abc import Iterable, Mapping, S
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:52:23Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/capabilities.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/holdout_budget.py", "limit": 260})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/stage_model.py", "limit": 400})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/validation/no_lookahead.py", "limit": 250})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/pipeline.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/claim.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/rejection.py", "limit": 320})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/universe_calendar.py", "limit": 200})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill-eval-gates", "include": "*.py", "pattern": "finalize_cohort\\(|resolve_cohort_dedup\\(|acquire_claim\\(|ClaimStore|register_member\\(", "output_mode": "content", "head_limit": 300})`


> [reasoning] **Identifying registration order bugs**

> [reasoning] **Detecting publication and registration inconsistencies**

> [reasoning] **Revealing missing deduplication in finalize_cohort**

> [reasoning] **Assessing data integrity and snapshot validation**

> [reasoning] **Analyzing concurrency and registration race conditions**

> [reasoning] **Identifying concurrency issues with finalization and claims**
The high-risk path is not just missing edge validation: the canonical orchestration bypasses parts of the designed recovery protocol. I’m now tracing finalize, registration, and concurrent retry behavior end to end, because those paths determine whether apparently valid artifacts can be omitted, duplicated, or finalized with stale verdicts.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/capabilities.py</path>
<type>file</type>
<content>
1: """执行层级 capability 边界（F007 `FR-001`/`NFR-003`；design §3.2/§7，任务 T003/T005）。
2: 
3: 执行层级必须**显式提供**，并由「物理根目录 + capability 双重隔离」强制：
4: 
5: - preview 落 `reports/preview/<experiment_id>/<attempt_id>/`，canonical 落
6:   `reports/bench/<object_id>/<research_snapshot_id>/<experiment_id>/`；
7: - `canonical writer`、`holdout reader`、**最终确认窗 reader**、`holdout budget ledger writer`
8:   是**显式注入**的 capability；preview / Agent 构造器**没有**这些接口，越权即 fail-closed
9:   并返回稳定错误码 `E_CANONICAL_FORBIDDEN`；
10: - 任何环境变量只能提供普通路径默认值，**不能升级 tier 或权限**——层级只从显式参数来，
11:   因此本模块不读取任何 tier 相关的环境变量。
12: 
13: 标签单隔离（只靠目录名）不足以防误写，故 capability 与路径同时强制（design §9 决策表）。
14: """
15: 
16: from __future__ import 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/holdout_budget.py</path>
<type>file</type>
<content>
1: """留出预算台账（`DR-005`/`AC-001`；任务 T012）。
2: 
3: `reports/holdout_budget/ledger.jsonl` 是 **append-only** 追加台账：每行一次留出评估，只有
4: canonical capability 持有 append 句柄；preview/Agent 构造器没有该句柄，越权写入即失败关闭并写
5: `evaluation.gate_rejected`。台账**不提供** UPDATE/DELETE 路径。
6: 
7: v0.2 边界（`DR-005`）：FactorDef 评测流程不访问最终留出（留出评估属 FR4/M3 的 PortfolioDef 留出
8: 门），因此 v0.2 **没有追加写入者**——台账零行是锁定「不存在旁路写入者」的预期不变量，不是功能
9: 缺失。`holdout_window` 与 `regime` 是为留出门预留的字段。
10: """
11: 
12: from __future__ import annotations
13: 
14: import json
15: from dataclasses import dataclass
16: from datetime import UTC, datetime
17: from pathlib import Path
18: from typing import Any
19: 
20: from alphamill.evaluat
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/stage_model.py</path>
<type>file</type>
<content>
1: """阶段状态与裁决枚举（design §3.3 术语表；`FR-003`/`FR-005`，任务 T007）。
2: 
3: 术语表是**冻结**的单一真相源：五阶段 ID、阶段状态、成本裁决、样本量三级、晋升裁决与失败三维
4: 都只在这里定义，其他模块引用而不另立枚举。阶段状态与晋升/成本 verdict 是**两层独立枚举**，
5: 不得互相替代：`PASS` 只描述单阶段结果，**不是**晋级结论（`FR-003`）。
6: 
7: 半开区间的样本量三级取自 `design.md` §3.3 / `spec.md` `FR-005`：
8: `[0,30)` underpowered（不判 PASS 也不判 FAIL）· `[30,69)` provisional（最多临时 PASS，仅缩减
9: 仓位 paper）· `[69,∞)` trustworthy（才允许完整成本后 PASS/FAIL 判定）。
10: """
11: 
12: from __future__ import annotations
13: 
14: from collections.abc import Iterable, Mapping
15: from dataclasses import dataclass, field
16: from typing import Any
17: 
18: STAGE_SIGNAL_QUALITY = "signal_quality"
19: STAGE_PORTFOLIO_
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/validation/no_lookahead.py</path>
<type>file</type>
<content>
1: """无前视三层状态与晋级阻断（`FR-007`/`AC-009`；任务 T008）。
2: 
3: 三层防线归属**冻结**（`spec.md` `FR-007`、`design.md` §7）：
4: 
5: | 层 | 内容 | owner | F007 的行为 |
6: |---|---|---|---|
7: | L1 | AST 纯度与未来算子门 | **F007** | 在评测入口 fail-closed 复检 |
8: | L2 | 独立逐 K 线重放审计 | F006/M3 | 不实现审计器，只消费证据 |
9: | L3 | 信号缓存 merge/join 时间戳与陈旧度对齐 | F006/M3 | 不实现审计器，只消费证据 |
10: 
11: 缺失层必须显式记 `not_yet_available` 并携带 `owner`，**不得记为 `PASS`、也不得静默省略**；任一层
12: 非 `PASS` 时证据达标的成员也只能是 `blocked_pending_audit`，由 F006 晋级入口消费后 fail-closed
13: （`E_PROMOTION_BLOCKED`）。
14: """
15: 
16: from __future__ import annotations
17: 
18: from dataclasses import dataclass
19: from typing import Any
20: 
21: LAYER_L1 = "L1"
22: LAYER_L2 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/pipeline.py</path>
<type>file</type>
<content>
1: """夹具信号的最小评测流水线（preview 与 canonical 共用；任务 T006/T013）。
2: 
3: 把「信号 + 前瞻收益」夹具跑成五阶段结果与成本/样本量裁决。canonical 与 preview 的差别只在
4: `execution_tier`（决定 `approximation` 与信号来源分层），阶段口径完全一致——因此两处共用同一
5: 实现，避免出现两套口径（`FR-003` 的失败语义、`FR-005` 的成本裁决）。
6: 
7: 阶段适用性：因子运行的 `portfolio_transform` 与 `execution_implementation` 显式记
8: `NOT_APPLICABLE`（组合构建属 FR4/M3、执行链属 F006/M3），**不得记为 PASS**。
9: """
10: 
11: from __future__ import annotations
12: 
13: from collections.abc import Mapping, Sequence
14: from dataclasses import dataclass
15: from typing import Any
16: 
17: from alphamill.evaluation.run_config import RunConfig
18: from alphamill.evaluation.signal_adapter import adapt_signal_records
19
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/claim.py</path>
<type>file</type>
<content>
1: """单写者 claim 与 lease 接管（`design.md` §5、`NFR-001`/`SC-002`；任务 T025）。
2: 
3: - runner 以 `<key>.claim` **原子创建**（`O_EXCL`）取得单写权；已有**完整** canonical 直接幂等
4:   返回（不是冲突），只有**在飞**的运行才构成冲突；
5: - claim 记录 owner token、启动时间、lease 秒数与 pid；
6: - **崩溃接管**只在三条件同时成立时允许：lease 已过期 ∧ 无活进程 ∧ temp artifact 未发布；
7:   正常路径**不能偷锁**（未过期或进程仍在即拒绝）；
8: - release 只有持有同一 owner token 才能执行，避免误释放他人锁。
9: 
10: 错误码映射说明：F007 的冻结错误码表没有独立的 busy/conflict 码，而 `E_COHORT_FROZEN` 在 T012 的
11: 语义已覆盖「单写者/登记冲突」，故在飞冲突映射到它（使用既有冻结码，不新增取值）；该映射记为
12: 待检视确认的假设。
13: """
14: 
15: from __future__ import annotations
16: 
17: import json
18: import os
19: from dataclasses import dataclass
20: from datetime import UTC, datetime, ti
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/rejection.py</path>
<type>file</type>
<content>
1: """方法论/纯度门拒绝后的终态登记（`spec.md` §5；任务 T016）。
2: 
3: `spec.md` §5 与 §5 不变量要求：方法论/纯度门入口失败是 `VALIDATING -> REJECTED` 的**终态结论**——
4: 必须照常发布 `evaluation.registered` 终态登记并计入 cohort 漏斗分母，**不得因失败而缺席登记**，
5: 也不得携带任何 PASS-like 结论。因此拒绝路径不是「抛错退出」，而是「跑出一个 REJECTED 结论」。
6: 
7: 被拒运行的五阶段记录：拒绝阶段记 `FAIL` + 三维失败记录（`mechanism=lookahead`）；下游两个必需
8: 阶段（成本/容量、时序稳定）因入口即被拒而**未执行**，记 `INCOMPLETE` 并给出原因——不得记为
9: `PASS`，也不得伪装成 `NOT_APPLICABLE`（必需阶段不允许 NOT_APPLICABLE）。曲线侧车为中性单点，
10: 并在 report 中显式标注 `evaluation=not_run_after_methodology_rejection`。
11: """
12: 
13: from __future__ import annotations
14: 
15: from datetime import datetime
16: from pathlib import Path
17: from typing import Any
18: 
19
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/experiment_store/universe_calendar.py</path>
<type>file</type>
<content>
1: """calendar artifact 契约（F007 `DR-006`；任务 T001）。
2: 
3: universe 与 calendar 是两个**独立** artifact：universe 归 F008 内容寻址台账（F007 只读），
4: calendar 由本 Feature 拥有——调用方给出 calendar JSON，本模块校验其 v1 schema、规范化后按
5: 内容寻址保存到 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`
6: （该目录只承载 calendar，universe 不合并进来）。ADR-0007 的 `universe_calendar_digest`
7: 由两者 digest 按冻结公式组合导出（见 `identity.universe_calendar_digest`）。
8: 
9: v1 calendar schema（本 Feature 拥有）：
10: 
11: ```json
12: {"schema_version": 1, "timezone": "UTC",
13:  "windows": [{"start": "2026-01-01T00:00:00Z", "end": "2026-04-01T00:00:00Z"}]}
14: ```
15: """
16: 
17: from __future__ import annotations
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 33 match(es) in 10 file(s)

/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/canonical_ops.py
  98: return population.register_member(reports, cohort_id, registration, registered)
  101: def finalize_cohort(cohort_id: str, *, finalized_at: str | None = None) -> Path:
  112: return population.finalize_cohort(

/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/cli.py
  180: def _run_finalize_cohort(args: argparse.Namespace) -> int:
  181: path = finalize_cohort(args.cohort)

/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/canonical.py
  281: population.register_member(

/home/georg/projects/alphamill-eval-gates/src/alphamill/evaluation/rejection.py
  198: population.register_member(

/home/georg/projects/alphamill-eval-gates/src/alp
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:53:00Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/signal_quality.py", "limit": 300})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/stability.py", "limit": 320})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/statistics.py", "limit": 350})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/multiplicity.py", "limit": 280})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_canonical_registry.py", "offset": 200, "limit": 340})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_concurrency.py", "limit": 280})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_atomic_publish.py", "limit": 400})`
- **tool**: `bash({"command": ".venv/bin/python tools/verify.py", "workdir": "/home/georg/projects/alphamill-eval-gates", "timeout": 600000})`


> [reasoning] **Planning targeted test execution**

> [reasoning] **Inspecting signal quality exception handling**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/signal_quality.py</path>
<type>file</type>
<content>
1: """信号质量阶段与近似/来源标注（`FR-003`/`NFR-004`/`DR-007`；任务 T007）。
2: 
3: - **最小信号质量**：Rank IC 与观测数。观测数为零记 `INCOMPLETE`（必需输入缺失），不足
4:   `min_observations` 记 `UNDERPOWERED`——两者都**不得**记为 `PASS`，也不得把空值当零
5:   （`design.md` §3.3 / `FR-003` 场景「指标样本不足」）。
6: - **近似标注**：`approximation.is_approximate` 与 `reduced_dimensions[]` 必须显式；canonical
7:   恒为 `is_approximate=false`，不因性能压力静默缩窗或采样（`NFR-004`）。
8: - **信号来源 provenance**：`source=placeholder` 在 canonical 失败关闭（`E_INPUT_INVALID`），
9:   preview 允许但必须标注 `signal_source=placeholder` 且 `approximation=true`（`DR-007`）。
10: """
11: 
12: from __future__ import annotations
13: 
14: from collections.abc import Sequence
15: from dataclass
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/stability.py</path>
<type>file</type>
<content>
1: """purged/embargoed rolling split 与稳定性报告（`FR-005`/`AC-004`；任务 T010）。
2: 
3: 切分纪律（`design.md` §5、ADR-0006「证据边界不变量」）：
4: 
5: - 切分以 outcome/label endpoint 为边界，**不是**信号起点：`label_horizon` 期内的训练观测被 purge，
6:   因为它们的标签落进了测试折；
7: - embargo 是额外的序列相关缓冲，覆盖测试折开始前 `embargo` 期（`embargo ≥ max label horizon`
8:   由 T008 的守卫另行断言）；
9: - 训练折只包含测试折**之前**的观测（rolling/expanding），有效训练集 = 训练区间 − purge − embargo。
10: 
11: 稳定性报告逐折给出 IC、有效训练/测试规模与一致性；折内退化（常数信号或样本不足）记
12: `INCOMPLETE` + `estimator_failure`（fail-closed），方向不一致记 `FAIL`（已评出、结论为负）。
13: """
14: 
15: from __future__ import annotations
16: 
17: from collections.abc import Sequence
18: from dataclasses import dataclass
19: from 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/statistics.py</path>
<type>file</type>
<content>
1: """成员级必需统计：HAC 稳健 IC 与 block bootstrap 置信区间（`FR-004`；任务 T009）。
2: 
3: 自研最小协议（不依赖 ml4t 配套包，ADR-0003）：逐期 Rank IC 序列 → 均值 IC 的 Newey-West(Bartlett)
4: 稳健标准误 → block bootstrap 置信区间。所有估计器**失败即抛错**，绝不 `except → warning/null`：
5: 异常由调用方映射为 `INCOMPLETE` + `estimator_failure`，不得伪装成 PASS（`design.md` §7）。
6: 
7: 周期 IC 序列的输入是「按时间排序的每期 (signal 向量, label 向量)」；纯 Python 实现（只用标准库），
8: 避免引入未声明依赖，也保证同一 seed 的 bootstrap 可复算（`NFR-002`）。
9: """
10: 
11: from __future__ import annotations
12: 
13: import math
14: import random
15: from collections.abc import Sequence
16: from dataclasses import dataclass
17: from typing import Any
18: 
19: MIN_PERIODS = 2
20: MIN_OBSERVATIONS = 3
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/src/alphamill/factor_factory/bench/multiplicity.py</path>
<type>file</type>
<content>
1: """多重检验与按有效独立数校正的显著性（`FR-004`；任务 T009）。
2: 
3: 自研最小协议：cohort 级 Benjamini-Hochberg FDR、由相关性导出的**有效独立试验数**、按有效独立数
4: 校正的 Deflated Sharpe Ratio（DSR）与最小 track-record length（MinTRL）。
5: 
6: 口径与冻结来源：`method-v1.json` 的 `multiplicity` 段（`fdr_method=benjamini_hochberg`、
7: `fdr_alpha`、`effective_independent=deflated_sharpe_ratio`、`min_track_record_years`）。阈值由
8: 预注册配置持有，不硬编码（`FR-004`）。
9: 
10: 失败语义：估计器异常一律抛 `StatisticsError`，由 `statistics_stage` 映射为 `INCOMPLETE` +
11: `estimator_failure`——stage 不得为 `PASS`（`AC-003` 场景「必需估计器异常」）。
12: """
13: 
14: from __future__ import annotations
15: 
16: import math
17: from collections.abc import Callable, Sequence
18: from datac
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_canonical_registry.py</path>
<type>file</type>
<content>
200: 
201: 
202: def test_pearson_and_max_abs_rho_pick_the_larger_metric():
203:     left = DedupCandidate("a", oos_pnl=(1.0, 2.0, 3.0, 4.0), rolling_ic=(0.1, -0.1, 0.2, -0.2))
204:     right = DedupCandidate("b", oos_pnl=(2.0, 4.0, 6.0, 8.0), rolling_ic=(0.1, -0.1, 0.2, -0.2))
205:     assert pearson(left.oos_pnl, right.oos_pnl) == pytest.approx(1.0)
206:     assert max_abs_rho(left, right) == pytest.approx(1.0)
207:     with pytest.raises(DedupError, match="常数"):
208:         pearson((1.0, 1.0), (1.0, 2.0))
209:     with pytest.raises(DedupError, match="长度不一致"):
210:         pearson((1.0, 2.0), (1.0,))
211:     with pytest.raises(DedupError, match="两个口径都缺序列
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_concurrency.py</path>
<type>file</type>
<content>
1: """T025 / `SC-002`·`NFR-001`·`AC-001`·`AC-003`：并发、lease 接管与 finalize 原子性故障注入。
2: 
3: 覆盖 SC-002 的四条：同 ID 并发 claim 只有一个成功；崩溃后只有 lease 过期 ∧ 无活进程 ∧ temp 未发布
4: 才可接管（正常路径不能偷锁）；finalize 失败不产生部分 `cohort_verdict`（失败后可重试）；registration
5: 幂等重试不重复计数。
6: """
7: 
8: from __future__ import annotations
9: 
10: import os
11: from datetime import UTC, datetime, timedelta
12: 
13: import pytest
14: 
15: from alphamill.evaluation.claim import (
16:     ClaimBusyError,
17:     acquire,
18:     assert_takeover_allowed,
19:     claim_path,
20:     is_process_alive,
21:     read_claim,
22:     recover,
23:     release,
24: )
25: from alphamill.evaluation.events import EVENT_REGISTERED,
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill-eval-gates/tests/integration/test_f007_atomic_publish.py</path>
<type>file</type>
<content>
1: """T011 / `AC-005`·`NFR-001`·`TR-001`·`TR-002`：原子发布、恢复与运行事件契约。
2: 
3: 覆盖：preview/canonical 发布目录与消费者判据、曲线-标量互推不符即拒绝且**不留可见半成品**、
4: 失败注入（缺 registration / 缺 curves_summary / 曲线损坏）一律 `E_PUBLISH_INCOMPLETE`、
5: quarantine 模式、同语义重发幂等与语义冲突拒绝、跨文件系统发布拒绝、
6: 事件幂等追加与按 cohort/stage/type 查询。
7: """
8: 
9: from __future__ import annotations
10: 
11: import json
12: import os
13: from dataclasses import replace
14: from datetime import UTC, datetime, timedelta
15: from pathlib import Path
16: 
17: import pytest
18: 
19: from alphamill.evaluation import publisher
20: from alphamill.evaluation.capabilities import CapabilityError, context_for
21: from alphamill.evaluation.cont
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
check_doc_links: 相对链接全部可解析
check_task_dag: 全部通过
check_doc_consistency: 全部通过
check_dep_pins: 全部依赖版本在声明范围内（runtime + dev）
check_secrets: 无密钥形态命中
........................................................................ [  9%]
........................................................................ [ 19%]
........................................................................ [ 28%]
........................................................................ [ 38%]
........................................................................ [ 47%]
........................................................................ [ 57%]
........................................................................ [ 67%]
...................................................................
…[truncated]
  ```
  </details>

## assistant · 2026-09-18T17:54:18Z


> [reasoning] **Assessing idempotency issue in finalize_cohort**

> [reasoning] **Identifying race condition in run_canonical registration**

> [reasoning] **Detecting recovery failure leaving cohort open**

> [reasoning] **Assessing finalize cohort idempotency**

> [reasoning] **Identifying missing statistical computations**

> [reasoning] **Highlighting finalize deduplication gaps**

> [reasoning] **Verifying artifact immutability invariants**

> [reasoning] **Identifying enforcement gaps in promotion and rejection invariants**

> [reasoning] **Confirming partial verification of synthesis and definition invariants**

> [reasoning] **Analyzing deduplication and test coverage**

> [reasoning] **Tracing canonical registration state issues**

> [reasoning] **Evaluating invariant validation failures**

> [reasoning] **Identifying critical test-coverage gaps in canonical.py**

> [reasoning] **Cataloging medium-severity registration and mutation issues**

> [reasoning] **Confirming output format for findings table**
Baseline confirmed: `feat/F007-evaluation-gates@99e8092`, clean worktree. `.venv/bin/python tools/verify.py` passed: 741 tests passed, 11 skipped.

**Findings**

| Severity | Category | Location | Title | Why it’s wrong / trigger | Suggested fix |
|---|---|---|---|---|---|
| Critical | correctness | `src/alphamill/evaluation/pipeline.py:88`; `src/alphamill/evaluation/canonical_ops.py:101` | Required statistics are not connected to the canonical workflow | Canonical only computes rank IC, cost, and stability; finalize only copies existing verdicts and hard-codes `fdr_alpha`. HAC, bootstrap, BH-FDR, DSR, and MinTRL implementations are never called. A candidate can finalize despite every FR-004 estimator being absent, so estimator failures cannot enforce invariant 6. | Invoke member statistics during canonical evaluation and cohort statistics during finalize; map every estimator exception to `INCOMPLETE`. |
| High | correctness | `src/alphamill/evaluation/canonical_ops.py:101` | Finalize never performs dedup or re-derives promotion verdicts | `resolve_cohort_dedup()` has no production caller. Two members with identical curves registered as `promising` remain `promising`, violating FR-008 and invariant 5’s frozen priority. | Load member/registry curves inside finalize, resolve dedup in commitment order, then derive verdicts and atomically publish both. |
| High | correctness | `src/alphamill/evaluation/canonical.py:143` | Published-but-unregistered runs cannot recover | If the process crashes after `publisher.publish()` at line 277 but before `population.register_member()` at line 281, retry returns immediately from the “published” branch and never repairs registration. The cohort remains OPEN permanently. | On reuse, verify and idempotently complete the population registration before returning. |
| High | correctness | `src/alphamill/evaluation/canonical.py:245` | Successful canonical runs invalidate their own event digest | The manifest hashes the initial events, then line 278 appends `evaluation.registered` after the directory is published. Every normal success therefore mutates canonical evidence and leaves `events_digest` stale, violating invariants 6 and 9. | Include the registration event before validation/rename, or keep it solely in the cohort event store without mutating the published batch. |
| High | correctness | `src/alphamill/evaluation/canonical.py:102` | Canonical runner bypasses the single-writer claim | `claim.acquire()` is tested only in isolation and never called by `run_canonical`. Concurrent same-ID runs can overlap; same-process threads share the PID-based temp path and can delete or corrupt each other’s attempt. | Acquire/release the experiment claim around the full canonical transaction and route recovery through `claim.recover()`. |
| High | correctness | `src/alphamill/experiment_store/holdout_budget.py:115`; `src/alphamill/evaluation/registry_writeback.py:164` | Forbidden writes do not leave rejection events | Preview `append_entry()` and definition-face writes only raise `E_CANONICAL_FORBIDDEN`. The tests manually construct a rejection event but production never persists it, violating invariant 7 and FR-008/TR-002. | Catch capability denial at the operation boundary and atomically append `evaluation.gate_rejected` before re-raising. |
| Medium | correctness | `src/alphamill/experiment_store/population.py:190` | Multiple registrations for one commitment silently become last-wins | Run one candidate twice with different seeds. Both event files are accepted; `registrations()` overwrites `by_candidate[candidate_id]` according to event filename order, allowing finalize with an arbitrary experiment. | Reject a second candidate registration unless its complete payload is identical to the existing registration. |
| Medium | correctness | `src/alphamill/experiment_store/population.py:243` | Repeating finalize is not idempotent | `canonical_ops.finalize_cohort()` supplies a new wall-clock `finalized_at` each call. A second identical finalize therefore differs bytewise and raises `RegistryIntegrityError`. | Exclude `finalized_at` from semantic idempotency or return the existing valid verdict before constructing a new timestamp. |
| Medium | test-coverage | `tests/integration/test_f007_atomic_publish.py:126` | “registration last” test does not test write ordering | `publisher._write_payload()` writes `registration.json` before `_validate_batch()` runs. The named test checks only eventual existence, so invariant 9’s commit-marker ordering is untested. | Write registration after validation and add fault injection asserting it is absent when validation fails. |

**Verified Invariants**

Correctly enforced in the inspected production path:

- **1**: canonical accepts only a published snapshot ID; preview latest freezes first.
- **2**: universe/calendar are independently validated and combined using the frozen digest formula.
- **3**: `execution_tier` and `supersedes` are excluded from `experiment_id`; snapshot provenance is excluded.
- **4**: stage and promotion enums are separate; required stages cannot be `NOT_APPLICABLE`.
- **8**: all three no-lookahead layers are emitted with frozen owners; non-PASS blocks promotion.
- **10**: synthesis reads cohort/canonical registrations only and retains rejected members in the denominator.
- **11**: writeback copies stored conclusions and definition-face writes are denied.
- **12**: sample tiers implement `[0,30)`, `[30,69)`, `[69,∞)`.

**Effort:** Medium, 1–2 days.  
**Confidence:** High; the disconnected call paths and recovery failures are directly visible despite the green gate.
