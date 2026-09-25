---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f478a4060ffeh3rglNusIrerkw"
title: "T028 reproducibility contract (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-19T06:58:39Z"
updated_at: "2026-09-19T09:22:03Z"
tokens_input: 61217
tokens_output: 1885
cost: 0.0
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# T028 reproducibility contract (@Sisyphus-Junior subagent)

## user · 2026-09-19T06:58:39Z

Implement F003 task T028 in /home/georg/projects/alphamill (branch `feat/F003-alphagen-vendor` MUST be checked out; verify `git status -sb`, abort if not).

HARD CONVERGENCE RULES:
- Rewrite any single file AT MOST 3 times; then STOP and report the blocker.
- NEVER edit gate/config files: `tools/**`, `docs/**`, `pyproject.toml`, `tests/unit/test_f001_line_limit_exemptions.py`, `tests/unit/test_check_doc_consistency.py`. If a gate goes red due to a file you may not touch, REPORT and stop.
- `tools/verify.py` is MINE — do NOT run it.
- You MUST end with a written report; never loop silently.
- Run `.venv/bin/ruff format <your files>` EARLY and again before the final check.
- Target ≤300 lines/file; SPLIT rather than compress. Never `# fmt: off`/`# noqa`/`type: ignore`.
- Keep tests fast (<20s total). CUDA torch IS installed but these tests are CPU-only.

FILES (exactly two):
- NEW `src/alphamill/factor_factory/generators/reproducibility.py`
- NEW `tests/integration/test_f003_generation_run.py`   ← this exact path is declared by T028 in tasks.md; create it.

READ FIRST: `docs/features/0.2/F003-alphagen-vendor/design.md` §3 (`配置与确定性（NFR-003）`: canonical config artifact + `config_digest`; RNG 由 seed 稳定派生各组件子种子，不依赖全局 random 状态；训练侧显式开启 torch 确定性开关；**CPU/GPU 差异只允许影响浮点末位，不改变候选集合**——断言的是 factor_id 集合与池成员一致，不承诺逐位数值相同) and §5; `spec.md` NFR-003/AC-009/AC-006; `tasks.md` T028; `canonical.py`; `registry/run_store.py` (`write_config`, `config_digest` semantics, `new_run_id`, `generation_run_dir`, `GenerationRun`); `registry/factor_store.py` (`build_factor`, `definition_digest`, `write`, `load`); `generators/manual/seeds.py`; `generators/objective.py`; `generators/alphagen_adapter.py`.

PUBLIC SURFACE (implement exactly):
```python
def derive_seed(seed: int, *components: str) -> int: ...
def torch_determinism(enabled: bool = True) -> "contextlib.AbstractContextManager[None]": ...
def canonical_run_id(*, generator: str, seed: int, binding_digest: str, config_digest: str,
                     code_digest: str, now: datetime | None = None) -> str: ...
@dataclass(frozen=True, kw_only=True)
class RunIdentity:
    seed: int
    binding_digest: str
    config_digest: str
    code_digest: str
    @property
    def identity_digest(self) -> str: ...
def factor_id_set(factors: Iterable[FactorDef]) -> frozenset[str]: ...
def pool_member_set(pool: FactorDef) -> frozenset[str]: ...
```

NORMATIVE SEMANTICS
- `derive_seed(seed, *components)` = a STABLE, documented hash-based derivation (e.g. `int.from_bytes(sha256(canonical_json([seed, *components]))[:8], "big")`) so each component gets an independent sub-seed and results never depend on global `random` state. Deterministic across processes/interpreters.
- `torch_determinism()` is a context manager that (if torch is importable) sets `torch.manual_seed`, `torch.use_deterministic_algorithms(True, warn_only=True)`, and restores prior state on exit; it MUST be a no-op-safe context manager when torch is absent (import lazily inside the function so importing this module never requires torch). Do not leave global torch state mutated after exit.
- `RunIdentity.identity_digest` = content-addressed digest over the four identity fields (canonical JSON → sha256). Two runs with the same `(seed, binding_digest, config_digest, code_digest)` MUST have the same `identity_digest`; changing any one changes it.
- `canonical_run_id` is deterministic given its inputs and a supplied `now` (so tests are reproducible), and MUST be a single safe path component (usable as `reports/generation/<run_id>`).
- `factor_id_set` / `pool_member_set` are the reproducibility comparison primitives: the reproducibility claim is **set equality of `factor_id`s and pool members**, NOT bitwise numeric equality (design §3/§5). Do NOT assert numeric identity.
- The module must not emit any evaluation verdict.

TESTS (`tests/integration/test_f003_generation_run.py`, `pytestmark = pytest.mark.integration`, service-free so it ALWAYS runs, plain `def test_*`, Chinese module docstring naming NFR-003/AC-009):
- `derive_seed` determinism: same inputs → same value; different component → different value; depends on no global state (call after `random.seed(...)` churn and assert unchanged).
- `RunIdentity` identity digest stability + sensitivity to each of the four fields.
- `canonical_run_id` deterministic with a fixed `now`; safe single path component; differs when any input differs.
- **End-to-end reproducibility**: run the manual generator TWICE with the same `(seed, binding, config, code_digest)` but different run ids/timestamps → identical `factor_id_set`; and a THIRD run with a different seed/config → different or explicitly-not-required-to-be-equal set (assert only what the spec promises).
- `torch_determinism` context: with torch available, seeds are set inside and prior RNG state is restored after; works (no-op) when torch import fails (monkeypatch the import seam you design to be injectable).
- config digest reproducibility: same config dict in different key order → same `config_digest`; changing a semantic key changes it (reuse `run_store` behaviour, do not reimplement).
- asserts no verdict/conclusion fields are produced anywhere.

CONSTRAINTS: no `eval`, no bare `except`, no suppressions, no gate edits, no commit. Docstrings on public API expected; no comments restating code. Run from /home/georg/projects/alphamill: `.venv/bin/ruff format <both files>`, `.venv/bin/ruff check <both files>`, `.venv/bin/python -m pytest -q tests/integration/test_f003_generation_run.py`, `.venv/bin/python -m pytest -q tests/unit/test_f001_line_limit_exemptions.py`. Report paths, exact commands + results, `wc -l`, deviations.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-19T06:58:39Z

- **tool**: `todowrite({"todos": [{"content": "repository branch guard: Run git status -sb to enforce the required feat/F003-alphagen-vendor branch - expect work may proceed only on the exact branch", "priority": "high", "status": "in_progress"}, {"content": "project contracts and Python rules: Read mandated F003 docs, source APIs, CLAUDE.md, and Python guidance to ground T028 - expect an implementation/test contract with no forbidden-file edits", "priority": "high", "status": "pending"}, {"content": "tests/integratio
…[truncated])`


> [reasoning] **Verifying git branch before proceeding**

> [reasoning] **Planning atomic todo steps and branch verification**
1 of 7: checking the required branch before reading or changing anything. I will abort immediately if `git status -sb` does not show `feat/F003-alphagen-vendor`.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "repository branch guard: Run git status -sb to enforce the required feat/F003-alphagen-vendor branch - expect work may proceed only on the exact branch",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "project contracts and Python rules: Read mandated F003 docs, source APIs, CLAUDE.md, and Python guidance to ground T028 - expect an implementation/test contract with no forbidden-file edits",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/integration/test_f003_generation_run.py: Add failing T028 integration coverage before production code to prove NFR-003/AC-009 behavior - expect focused CPU-only failures against the missing API",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "both re
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:59:03Z

- **tool**: `skill({"name": "git-master", "user_message": "Only inspect `git status -sb` as a mandatory branch guard; do not commit or change git state."})`

  <details><summary>tool output</summary>

  ```text
## Skill: git-master

**Base directory**: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/git-master

# Git Master Agent

You are a Git expert combining three specializations:
1. **Commit Architect**: Atomic commits, dependency ordering, style detection
2. **Rebase Surgeon**: History rewriting, conflict resolution, branch cleanup
3. **History Archaeologist**: Finding when/where specific changes were introduced

---

## GIT COMMAND PREFIX (MANDATORY)

<git_env_prefix>
**EVERY git command MUST be prefixed with `GIT_MASTER=1`.**

This allows custom git hooks to detect when git-master skill is active.

```bash
GIT_MASTER=1 git status
GIT_MASTER=1 git add <files>
GIT_MASTER=1 git commit -m "message"
GIT_MASTER=1 git push
GIT_MASTER=1 git reba
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:59:10Z

- **tool**: `bash({"command": "GIT_MASTER=1 git status -sb", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`

  <details><summary>tool output</summary>

  ```text
## feat/F003-alphagen-vendor


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-19T06:59:16Z

- **tool**: `todowrite({"todos": [{"content": "repository branch guard: Run git status -sb to enforce the required feat/F003-alphagen-vendor branch - expect work may proceed only on the exact branch", "priority": "high", "status": "completed"}, {"content": "project contracts and Python rules: Read mandated F003 docs, source APIs, CLAUDE.md, and Python guidance to ground T028 - expect an implementation/test contract with no forbidden-file edits", "priority": "high", "status": "in_progress"}, {"content": "tests/integrat
…[truncated])`


> [reasoning] **Planning parallel reading and programming tasks**

> [reasoning] **Prioritizing codegraph query and docs scanning**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "repository branch guard: Run git status -sb to enforce the required feat/F003-alphagen-vendor branch - expect work may proceed only on the exact branch",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "project contracts and Python rules: Read mandated F003 docs, source APIs, CLAUDE.md, and Python guidance to ground T028 - expect an implementation/test contract with no forbidden-file edits",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "tests/integration/test_f003_generation_run.py: Add failing T028 integration coverage before production code to prove NFR-003/AC-009 behavior - expect focused CPU-only failures against the missing API",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "both 
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:59:31Z

- **tool**: `skill({"name": "programming", "user_message": "Implement T028 in two Python files using strict TDD. Need Python reference guidance before any code edits."})`


> [reasoning] **Invoking programming skill for references**
Branch guard passed: `## feat/F003-alphagen-vendor`, with a clean worktree. Step 2 of 7 is now mapping the exact config, run-store, factor-store, manual-generator, and determinism contracts before the red test.

  <details><summary>tool output</summary>

  ```text
## Skill: programming

**Base directory**: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming

Base directory for this skill: /home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/
File references (@path) in this skill are relative to this directory.

# Programming

You are a lazy senior engineer — lazy meaning efficient, never careless. **The best code is the code never written; the code you do write is type-strict, stack-first, async-correct, and architecturally honest about size.**

This skill is an index. The hard per-language rules live under `references/`. Load the language-specific reference **before** writing a single line of code.

---

## PHASE 0 — LANGUAGE GAT
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:59:41Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "canonical.py registry/run_store.py write_config config_digest new_run_id generation_run_dir GenerationRun registry/factor_store.py build_factor definition_digest write load generators/manual/seeds.py generators/objective.py generators/alphagen_adapter.py; return the relevant verbatim source and call paths needed to implement F003 T028 reproducibility utilities and an end-to-end manual generator test", "maxFiles": 12})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md", "offset": 1, "limit": 2000})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md", "offset": 1, "limit": 2000})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor", "include": "design.md", "pattern": "^##?\\s*(3|5)(\\.|\\s|$)|NFR-003|config_digest|CPU/GPU|候选集合|factor_id|池成员", "output_mode": "content", "head_limit": 200})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor", "include": "spec.md", "pattern": "NFR-003|AC-009|AC-006|^##?\\s", "output_mode": "content", "head_limit": 200})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor", "include": "tasks.md", "pattern": "T028|^##?\\s", "output_mode": "content", "head_limit": 200})`


> [reasoning] **Planning parallel code and docs reading**

> [reasoning] **Designing targeted doc reading with codegraph**

  <details><summary>tool output</summary>

  ```text
**Interface dispatch (a named method has many implementations)**

- `write` → runtime dispatch to **115** types implementing `Service` — the static path ends here, the target is chosen at runtime. e.g. `SessionProjectionCache.write` (deepseek-harness/packages/session/session-projection-cache/src/index.ts:246), `SettingsProvider.write` (deepseek-harness/packages/settings/settings/src/index.ts:621) +113 more
- `load` → runtime dispatch to **16** types implementing `SettingsProvider` — the static path ends here, the target is chosen at runtime. e.g. `FileSettingsProvider.load` (deepseek-harness/packages/settings/settings-file/src/index.ts:171), `MemorySettings.load` (deepseek-harness/packages/client/locale/tests/host.client.spec.ts:10), `MemorySettings.load` (deepseek-harness/packages/client/
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/CLAUDE.md</path>
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
13: - `docs/features/0.1/F001-quant-crypto-migration/migration-plan.md`：quant-cry
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md</path>
<type>file</type>
<content>
1: 
2: # Python Programmer
3: 
4: Modern Python. Type-strict, stack-first, async-correct.
5: 
6: ## Philosophy
7: 
8: The type checker is your compiler. Make illegal states unrepresentable. Parse at boundaries. Own resources explicitly. Every function has a contract; the type system enforces it.
9: 
10: ## Hard rules
11: 
12: These are deliberate project choices. Violations are always wrong, not "style preferences".
13: 
14: ### Tooling
15: 
16: | Category | Use | Never |
17: |---|---|---|
18: | Package manager | `uv` | pip, poetry, conda, pipenv |
19: | Type checker | `basedpyright` (`typeCheckingMode = "all"`
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 17 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  81: | 唯一真相源 | 候选定义 = `factors/<factor_id>.json`；运行事实 = `run.json`；两者之外不得出现第二份候选清单 |
  88: ## 3. 数据模型与 Migration
  97: ├── factors/<factor_id>.json  # FactorDef 定义（只含定义，无结论；仅 status=completed 的运行可被下游入册）
  105: **FactorDef（`schema_version: 1`）**：`factor_id` / `definition_digest` / `hypothesis_id` / `name` / `generator` / `generator_version` / `scope` / `expression` / `params` / `data_columns` / `feature_map_digest` / `run_id` / `created_at`。
  107: - `definition_digest = sha256(canonical_json(定义字段))`，规范化时**排除** `factor_id`、`run_id`、`created_at`——同一表达式在不同 run 得到同一 digest，用于重复定义识别（拒绝原因码 `duplicate_definition`）；
  108: - `factor_id = <generator>_<definition_digest[:12]>`：人读前缀 + 内容后
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 13 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
  15: # F003：AlphaGen vendor 与可插拔生成器平面
  19: ## 0. 来源与意图
  31: ## 1. 问题、目标与非目标
  53: ## 2. 用户场景
  97: ## 3. 范围与边界
  128: ## 4. 需求
  265: - **NFR-003**：可复现：相同 `(seed, 快照绑定, code digest, config_digest)` 重跑应当得到相同的 factor_id 集合与相同的协同池成员。配置摘要定义为 canonical config artifact（键排序、排除时间戳/主机字段）的 sha256，artifact 随运行落盘、可重放；RNG 由 `seed` 稳定派生，训练侧开启 torch 确定性开关；**CPU/GPU 差异只允许影响浮点末位、不改变候选集合**——本项断言的是集合与池成员一致（跨 device 亦然），不承诺逐位数值相同。
  269: ## 5. 生命周期与不变量
  294: ## 6. 成功与验收
  310: - [ ] **AC-006** (`FR-005`, `NFR-001`): 换手惩罚/可达性预筛生效——零交易型表达式不进池；成本后收益预筛参数（`cost_model`、`min_after_cost_return`）写入 run.json 的 objective；在执行机上单次挖掘入册 ≥50 个通过自检候选 — tests: `tests/integration/test_f003_generation_run.py`
  313:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 10 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md
  12: # F003：AlphaGen vendor 与可插拔生成器平面 - 任务
  16: ## 0. 来源与执行规则
  27: ## 1. 前置条件
  34: ## 2. 实现任务
  70: - [ ] T028 (`NFR-003`, `AC-009`): 实现并验证可复现性——canonical config artifact 与 `config_digest` 落盘、seed 稳定派生、torch 确定性开关；同 `(seed, binding, code_digest, config_digest)` 重跑得到相同 factor_id 集合与相同池成员 — verify: `tests/integration/test_f003_generation_run.py`
  73: ## 3. 验证与验收任务
  90: ## 4. 依赖与并行关系
  108: - `T028 -> T029`：可复现性由完整运行验收。
  110: - `T011/T020/T026/T027/T028 -> T031`：边界、数据面、协同池、CLI 契约与可复现性由 T031 集成套件验收（生产者 → 验证者）。
  120: ## 5. 明确后移

[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian a
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T07:00:09Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "src/alphamill/factor_factory/canonical.py src/alphamill/factor_factory/generators/manual/seeds.py src/alphamill/factor_factory/generators/objective.py src/alphamill/factor_factory/generators/alphagen_adapter.py FactorDef AlphaPoolDef pool_store manual generator GenerationRequest GeneratorResult; show complete relevant source, signatures, and construction flow for running the manual generator and comparing pool members", "maxFiles": 12})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "offset": 88, "limit": 154})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "offset": 128, "limit": 194})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md", "offset": 34, "limit": 55})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/data-modeling.md", "offset": 1, "limit": 1000})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/type-patterns.md", "offset": 1, "limit": 1000})`
- **tool**: `context7_resolve-library-id({"libraryName": "PyTorch", "query": "Current PyTorch Python API documentation for manual_seed, deterministic algorithm state getter/setter, RNG state get/set, and restoring deterministic state in a context manager."})`


> [reasoning] **Planning targeted document reading**

> [reasoning] **Detailing codegraph queries and test strategy**

> [reasoning] **Assessing import seam monkeypatch design**
Step 2 of 7: the governing contract is confirmed—identity is content-addressed, run metadata is excluded from factor identity, and reproducibility is set equality rather than numeric equality. I’m now resolving the concrete manual-generator and torch state APIs needed for a faithful red test.

  <details><summary>tool output</summary>

  ```text
**Exploration: src/alphamill/factor_factory/canonical.py src/alphamill/factor_factory/generators/manual/seeds.py src/alphamill/factor_factory/generators/objective.py src/alphamill/factor_factory/generators/alphagen_adapter.py FactorDef AlphaPoolDef pool_store manual generator GenerationRequest GeneratorResult; show complete relevant source, signatures, and construction flow for running the manual generator and comparing pool members**

Found 39 symbols across 3 files.

**Blast radius — what depends on these (update/verify before editing)**

- `FactorDef` (alphamill/src/alphamill/factor_factory/factor.py:25) — 10 callers in `alphamill/src/alphamill/factor_factory/generators/base.py`, `alphamill/src/alphamill/factor_factory/registry/factor_store.py`, `alphamill/src/alphamill/factor_factory/r
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md</path>
<type>file</type>
<content>
88: ## 3. 数据模型与 Migration
89: 
90: 无数据库 schema、无 migration。全部为文件系统内容寻址产物。
91: 
92: **产物布局**（`reports/` 是架构定义的运行产物目录）：
93: 
94: ```text
95: reports/generation/<run_id>/
96: ├── run.json                  # GenerationRun 终态 manifest（唯一运行事实；四态都写，tmp+fsync+rename 最后写）
97: ├── factors/<factor_id>.json  # FactorDef 定义（只含定义，无结论；仅 status=completed 的运行可被下游入册）
98: ├── pool.json                 # 协同池 meta-factor（可选；仅 status=completed 的运行产出）
99: ├── events.jsonl              # TR-001/TR-002 append-only
100: └── checkpoints/              # 训练 checkpoint（可清理，不属于证据）
101: ```
102: 
103: **终态与可消费性**：`run.json` 是唯一运行事实，四种终态 `completed` / `rejected` / `failed` / `partial` 都必须写出，字段至少含 `statu
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md</path>
<type>file</type>
<content>
128: ## 4. 需求
129: 
130: ### 功能需求
131: 
132: ### Requirement: 可插拔生成器接口（`FR-001`）
133: 
134: 系统应当提供统一生成器接口，输入为生成请求（快照绑定、seed、配置、配额），输出为 FactorDef 列表与逐级自检计数；后端替换不得要求调用方改动，且任何后端都不得在返回值中携带评测结论字段。
135: 
136: #### Scenario: 两个后端同一接口
137: 
138: - GIVEN AlphaGen 后端与人工种子后端各自的配置
139: - WHEN 调用方以相同请求结构分别执行 `produce()`
140: - THEN 两者返回同一 schema 的结果，调用方代码无分支差异
141: 
142: #### Scenario: 后端试图返回结论
143: 
144: - GIVEN 一个后端在结果中写入 IC 或 verdict 字段
145: - WHEN 结果通过 schema 校验
146: - THEN 校验失败并拒绝入册
147: 
148: ### Requirement: AlphaGen vendor 卫生与可复现构建（`FR-002`）
149: 
150: 系统应当把 AlphaGen 核心子集置于 `factor_factory/generators/alphagen_vendor/`，丢弃上游 `requirements.txt` 并改用本仓 pin 的现代栈；vendor 目录内每处修改标注 `# [
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md</path>
<type>file</type>
<content>
34: ## 2. 实现任务
35: 
36: ### Phase 1：生成器平面骨架与人工种子后端（US-001，不依赖 AlphaGen）
37: 
38: - [x] T005 (`FR-001`, `IR-002`, `AC-001`): 实现 `Generator` 协议与 `GenerationRequest/Result/Counts`，含结论字段白名单拒绝 — verify: `tests/unit/test_f003_generator_contract.py`
39: - [x] T006 [P] (`DR-003`, `AC-009`): 实现 `HypothesisDef` schema 与 catalog（含 `mechanism`、`applicable_state` 默认值），内置 `mechanism_unknown` 条目 — verify: `tests/unit/test_f003_hypotheses.py`
40: - [x] T007 (`DR-002`, `AC-009`): 实现 FactorDef 规范化 JSON（带 `schema_version`）、`definition_digest`、`factor_id` 生成与 `factor_store` 读写（`load()` 由表达式 + `feature_map` 重建可执行 `compute`） — verify: `tests/unit/test_f003_factor_store.py`
41: - [x] T008 (`DR-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/data-modeling.md</path>
<type>file</type>
<content>
1: # Data Modeling
2: 
3: Which container to use, how to structure data, and why frozen is the default.
4: 
5: ---
6: 
7: ## Decision flowchart
8: 
9: ```
10: Is it a fixed set of named constants?
11:   YES → StrEnum / IntEnum
12:   NO ↓
13: Is it just branding a primitive (int, str, float)?
14:   YES → NewType("X", base)
15:   NO ↓
16: Is it an interface / contract ("this thing can do X")?
17:   ├─ Shape only, no shared code → Protocol
18:   └─ Shared method implementation needed → ABC
19:   NO ↓
20: Does the data cross a trust boundary (user input, API, file, external DB)?
21:   YES → pydantic.BaseMode
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/type-patterns.md</path>
<type>file</type>
<content>
1: # Type Patterns
2: 
3: How to use Python's type system to catch bugs at check time, not runtime.
4: 
5: ---
6: 
7: ## NewType — distinct primitives
8: 
9: Same runtime type, different meaning. The type checker prevents mixing.
10: 
11: ```python
12: from typing import NewType
13: 
14: UserId = NewType("UserId", int)
15: MovieId = NewType("MovieId", int)
16: Email = NewType("Email", str)
17: Seconds = NewType("Seconds", float)
18: Milliseconds = NewType("Milliseconds", float)
19: 
20: def get_user(user_id: UserId) -> User: ...
21: def get_movie(movie_id: MovieId) -> Movie: ...
22: def sleep(duration: S
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Available Libraries:

- Title: PyTorch
- Context7-compatible library ID: /pytorch/pytorch
- Description: PyTorch is an open-source machine learning framework that accelerates the path from research prototyping to production deployment, offering tensor computation with strong GPU acceleration and deep neural networks built on a tape-based autograd system.
- Code Snippets: 8551
- Source Reputation: High
- Benchmark Score: 73.88
- Versions: v2.5.1, v2_8_0, v2.9.1, v2.11.0
----------
- Title: PyTorch
- Context7-compatible library ID: /websites/pytorch_2_13
- Description: PyTorch is an open-source machine learning framework and optimized tensor library for deep learning applications on GPUs and CPUs.
- Code Snippets: 15060
- Source Reputation: High
- Benchmark Score: 76.04
----------
- Title: P
…[truncated]
  ```
  </details>

## user · 2026-09-19T09:22:03Z

[SYSTEM DIRECTIVE: OH-MY-OPENCODE - TODO CONTINUATION]

Incomplete tasks remain in your todo list. Continue working on the next pending task.

- Proceed without asking for permission
- Mark each task complete when finished
- Do not stop until all tasks are done
- If you believe all work is already complete, the system is questioning your completion claim. Critically re-examine each todo item from a skeptical perspective, verify the work was actually done correctly, and update the todo list accordingly.

[Status: 1/7 completed, 6 remaining]

Remaining tasks:
- [in_progress] project contracts and Python rules: Read mandated F003 docs, source APIs, CLAUDE.md, and Python guidance to ground T028 - expect an implementation/test contract with no forbidden-file edits
- [pending] tests/integration/test_f003_generation_run.py: Add failing T028 integration coverage before production code to prove NFR-003/AC-009 behavior - expect focused CPU-only failures against the missing API
- [pending] both requested files: Run early Ruff formatting after the initial test file exists to satisfy the convergence gate - expect canonical formatting without touching other files
- [pending] src/alphamill/factor_factory/generators/reproducibility.py: Implement deterministic seed, run identity, torch context, and factor-set primitives - expect all T028 tests to pass without verdict output
- [pending] both requested files: Run final Ruff formatting, lint, focused integration test, and mandated line-limit unit test - expect every requested command to pass within the test budget
- [pending] changed Python files: Run diagnostics, count lines, and inspect scoped diff/status for final evidence - expect clean diagnostics, <=300 lines per file, and exactly two new files
<!-- OMO_INTERNAL_INITIATOR -->
