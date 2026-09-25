---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f478a587affeGxsxAm3ch0OyPN"
title: "T018 vendor tensor vs pandas IC parity (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-19T06:58:33Z"
updated_at: "2026-09-19T07:00:08Z"
tokens_input: 66236
tokens_output: 1141
cost: 0.0
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# T018 vendor tensor vs pandas IC parity (@Sisyphus-Junior subagent)

## user · 2026-09-19T06:58:33Z

Implement F003 task T018 in /home/georg/projects/alphamill (branch `feat/F003-alphagen-vendor` MUST be checked out; verify `git status -sb`, abort if not).

HARD CONVERGENCE RULES:
- Rewrite any single file AT MOST 3 times; then STOP and report the blocker.
- NEVER edit gate/config files: `tools/**`, `docs/**`, `pyproject.toml`, `tests/unit/test_f001_line_limit_exemptions.py`, `tests/unit/test_check_doc_consistency.py`. If a gate goes red due to a file you may not touch, REPORT and stop.
- `tools/verify.py` is MINE — do NOT run it.
- You MUST end with a written report; never loop silently.
- Run `.venv/bin/ruff format <your files>` EARLY and again before the final check.
- Target ≤300 lines/file; SPLIT rather than compress. Never `# fmt: off`/`# noqa`/`type: ignore`.
- Keep tests fast (<10s total). CUDA torch 2.10.0+cu128 IS installed; CPU is fine for this test.

FILES (exactly two):
- NEW `src/alphamill/factor_factory/generators/ic_parity.py`
- NEW `tests/unit/test_f003_ic_parity.py`

READ FIRST: `docs/features/0.2/F003-alphagen-vendor/design.md` §7 (冒烟闸门: 「IC 口径对齐不是评测台」——只做 vendor 张量 IC 与 pandas 参考实现的数值一致性回归；**不产 verdict、不写台账、不产证据**；评测权唯一属 F007 / ADR-0003) and §8 (`AC-007`/day-2 judgement); `spec.md` FR-006/AC-007; `docs/decisions/0003-validation-gate-non-degradation.md`; `docs/alphamill-architecture.md` §4.1.1; `generators/expression_compiler.py`; `generators/alphagen_adapter.py` (T021, just landed); `generators/operator_registry.py`; and the vendored AlphaGen at `src/alphamill/factor_factory/generators/alphagen_vendor/` — especially `alphagen/data/expression.py` (the `Expression` classes and their tensor `evaluate`), `alphagen/data/tokens.py`, and the new `alphamill_qlib_shim.py` (minimal `FeatureType` + a `StockData` protocol with `tensor data / backtrack / n_days / n_stocks`).

KEY CONTEXT: the vendor's only concrete tensor calculator lived in the DISCARDED `alphagen_qlib/calculator.py`. So to get a "vendor tensor" evaluation you must build a minimal tensor-backed `StockData`-compatible object yourself (numpy/torch array) and feed it to the vendored `Expression.evaluate`. If that proves impossible for some expression classes, say so explicitly in your report and fall back to an INDEPENDENT pandas reference implementation of the same expression — but do NOT ship a test that only compares the adapter against itself (that is `test-simulates-itself` and worthless).

PUBLIC SURFACE (implement exactly):
```python
IC_PARITY_TOLERANCE: Final = 1e-6

@dataclass(frozen=True, kw_only=True)
class IcParityResult:
    matched: bool
    max_abs_diff: float
    points: int
    detail: str

def tensor_ic(values: "np.ndarray | torch.Tensor", forward_returns: "np.ndarray | torch.Tensor",
              *, universe_mask: "np.ndarray | None" = None) -> float: ...
def pandas_ic(values: pd.Series, forward_returns: pd.Series, *,
              universe_mask: pd.Series | None = None) -> float: ...
def compare_ic(expression: tuple[str, ...], panel: pd.DataFrame, forward_returns: pd.Series, *,
               tolerance: float = IC_PARITY_TOLERANCE) -> IcParityResult: ...
```

NORMATIVE SEMANTICS
- This module is a **numerical consistency regression ONLY**. It MUST NOT produce a verdict, promotion, evidence artifact, ledger entry, or any conclusion field. State this in the module docstring citing ADR-0003 and that evaluation authority belongs solely to F007.
- IC definition must be identical on both sides: cross-sectional (per-timestamp) rank correlation between the signal and forward returns, restricted to in-universe rows, then averaged over timestamps. Document the exact formula. Do NOT let the two implementations differ in any convention (e.g. one using Pearson) — that would make the parity test vacuous.
- NaN/no-signal rows and rows outside `__in_universe__` are excluded on BOTH sides identically.
- `tensor_ic` operates on arrays/tensors; `pandas_ic` on Series. `compare_ic` computes the adapter/compiler-produced signal for the given expression (via `generators.alphagen_adapter.compile_alphagen_expression`) AND an independent reference, then returns the max abs difference.
- Degenerate inputs (single pair per timestamp, zero variance, empty after masking) → define and document behaviour (e.g. return 0.0 or raise `SchemaValidationError`); make it explicit and test it. No silent NaN propagation.
- No hard-coded thresholds from spec/AC text beyond the documented tolerance constant.

TESTS (`tests/unit/test_f003_ic_parity.py`, plain `def test_*`, Chinese module docstring naming FR-006/AC-007):
- parity on a synthetic panel for several expressions (`("feature:close","return:1","cs_rank")`, `("feature:close","neg")`, etc.): `compare_ic(...).matched is True` and `max_abs_diff <= tolerance`.
- the two implementations agree on a hand-computable case (assert the actual IC value within tolerance of a manually computed number, so the test is not self-referential).
- universe masking changes the result identically on both sides; rows outside the universe never contribute.
- a deliberately perturbed input makes `matched False` (proves the comparison can fail — no vacuously-passing test).
- degenerate cases behave as documented.
- asserts the result object exposes NO verdict/conclusion field names.

CONSTRAINTS: no `eval`, no bare `except`, no suppressions, no gate edits, no commit. Docstrings on public API expected; no comments restating code. Run from /home/georg/projects/alphamill: `.venv/bin/ruff format <both files>`, `.venv/bin/ruff check <both files>`, `.venv/bin/python -m pytest -q tests/unit/test_f003_ic_parity.py`, `.venv/bin/python -m pytest -q tests/unit/test_f001_line_limit_exemptions.py`. Report paths, exact commands + results, `wc -l`, the exact IC formula, and — importantly — whether you achieved a genuine vendor-tensor-vs-pandas comparison or had to fall back, with the reason.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-19T06:58:33Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor or immediate abort", "priority": "high", "status": "in_progress"}, {"content": "Required F003 docs and Python rules: Read mandated contracts before coding to preserve FR-006/AC-007 boundaries - expect exact IC semantics and coding constraints captured", "priority": "high", "status": "pending"}, {"content": "Generator and vendor sources: Trace compiler, adapte
…[truncated])`


> [reasoning] **Verifying git branch status**

> [reasoning] **Planning atomic todo list**
1. 检查分支与工作树；若不是 `feat/F003-alphagen-vendor`，立即停止。预计 10 秒。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor or immediate abort",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Required F003 docs and Python rules: Read mandated contracts before coding to preserve FR-006/AC-007 boundaries - expect exact IC semantics and coding constraints captured",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "Generator and vendor sources: Trace compiler, adapter, registry, and tensor Expression APIs to design an independent parity path - expect genuine vendor-tensor-vs-pandas approach identified",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_ic_parity.py: Add red tests for 
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:58:57Z

- **tool**: `bash({"command": "git status -sb", "workdir": "/home/georg/projects/alphamill", "timeout": 10000})`

  <details><summary>tool output</summary>

  ```text
## feat/F003-alphagen-vendor


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-19T06:59:16Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor or immediate abort", "priority": "high", "status": "completed"}, {"content": "Required F003 docs and Python rules: Read mandated contracts before coding to preserve FR-006/AC-007 boundaries - expect exact IC semantics and coding constraints captured", "priority": "high", "status": "in_progress"}, {"content": "Generator and vendor sources: Trace compiler, adap
…[truncated])`


> [reasoning] **Planning parallel doc and skill reading**

> [reasoning] **Scheduling source inspection with codegraph**
分支前置条件通过：当前为 `feat/F003-alphagen-vendor`，工作树无变更。现在读取规范与 Python 规则，先锁定边界和退化行为。

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor or immediate abort",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "Required F003 docs and Python rules: Read mandated contracts before coding to preserve FR-006/AC-007 boundaries - expect exact IC semantics and coding constraints captured",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "Generator and vendor sources: Trace compiler, adapter, registry, and tensor Expression APIs to design an independent parity path - expect genuine vendor-tensor-vs-pandas approach identified",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_ic_parity.py: Add red tests fo
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T06:59:38Z

- **tool**: `skill({"name": "programming", "user_message": "Implement two new Python files for F003 T018 with strict TDD, tensor/pandas IC parity, and the user's exact verification commands."})`


> [reasoning] **Planning reading Python docs sections**

> [reasoning] **Invoking programming skill and grepping headings**

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

## assistant · 2026-09-19T06:59:52Z

- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md", "pattern": "^#{1,6}\\s+(7|8)(?:\\.|\\s|$)|AC-007|冒烟闸门|day-2", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md", "pattern": "FR-006|AC-007", "output_mode": "content"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "pattern": "^#{1,6}\\s+4\\.1\\.1|4\\.1\\.1", "output_mode": "content"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md"})`


> [reasoning] **Planning parallel reading of README and CLAUDE docs**

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
Found 6 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  24: - **ADR / 上游 Contract**：ADR-0001（选型、冒烟闸门、降级判据）、ADR-0002（vendor 卫生规则、pin 纪律、永不 fork）、ADR-0003（门禁不降级）、ADR-0007（快照绑定）；F002 的 `alphamill.data_bridge.reader.read()` 与 `(dataset, data_version, value_digest)` 身份
  225: - 冒烟闸门：每条判据的 `pass/fail` + 时间戳 + 证据指针写当日冒烟 manifest，裁决结论人可读、机器可解析；manifest 同时承载 ADR-0001 两条 M2 义务的证据（生成侧逐级计数、奖励频率抽查），下游漏斗级以 `owner=F007` + `state=not_yet_available` 占位；
  228: ## 7. 失败、恢复、安全与兼容
  236: ## 8. 测试策略与验收映射
  246: | `AC-007` | integration | `tests/integration/test_f003_smoke_gate.py` | L1 三条判据逐条二元判定并入 manifest；任一触发即 L1 降级裁决；time-box 不裁 L2（L2 须 L1 连续 2 周判据）；L1→L0 回切请求被拒 |
  253: 真实环境场景：冒烟闸门 time-box 实跑（US-002）与训练窗口实测（显存峰值、耗时、入册数）必须在**执行机**上执行并记录 hostname 与设
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 3 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md
  48: - 本 feature 不做证据评测、统计裁决、多重检验与**成本裁决**（三档成本结论与 `cost_model_version` 归 `F007`）——生成侧只做可配参数下的**成本后收益预筛**，不产 verdict；漏斗记账见 FR-006 的第一级义务（评测权归 `F007`，生成器只产候选，ADR-0003、PRD AI 权限红线）；
  212: ### Requirement: 冒烟闸门与降级阶梯（`FR-006`）
  311: - [ ] **AC-007** (`FR-006`): 冒烟闸门判据逐条自动判定并写入当日 manifest；任一触发即输出降级裁决且不输出"通过"；2 日 time-box 只裁 L0 锁定或 L1 降级，L2 须 L1 连续 2 周判据（ADR-0001）；ADR-0001 两条 M2 冒烟义务（逐级计数自第一天入库、奖励频率抽查）可核验，下游漏斗级以 owner=F007/not_yet_available 显式占位；回切须重开 time-box — tests: `tests/integration/test_f003_smoke_gate.py`

[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 2 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  194: │   │   ├── alphagen_adapter.py  # 表达式树/张量 ↔ FactorDef 适配层（§4.1.1；放 vendor 外，见集成文档卫生规则）
  279: #### 4.1.1 AlphaGen 适配契约（表达式树/张量世界 ↔ FactorDef pandas 世界）

[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they r
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0003-validation-gate-non-degradation.md</path>
<type>file</type>
<content>
1: # ADR-0003：验证门禁不降级 —— quant-crypto 教训制度化
2: 
3: - 日期：2026-09-06
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：quant-crypto 仓库 Phase 4 决策报告（2026-06-17，`blocked_no_paper_candidate`）与
7:   PRD G4 / FR3
8: 
9: ## 背景
10: 
11: quant-crypto 的最终 90 天留出门连续拦下全部候选（低频 Ridge/HGB、regime 增强、成本感知、
12: 衍生品 basis），看起来是"失败"，实际是验证协议在正确工作——它拦下的是会亏钱的东西。
13: 真正的问题是 alpha 供给量（每周 ~5 个假设）与留出期样本量不足（69 笔交易的 FAIL/PASS
14: 判定统计上不可信；regime filter 方向正确但 27 笔欠功效）。
15: 
16: 该门禁的价值来自它**从不放水**。任何"先上盘再观察"的妥协都会摧毁整个系统的可信度。
17: 
18: ## 决策
19: 
20: 1. **证据门不降级**：FactorDef 在选择期筛选后先构建并冻结 PortfolioDef，再由完整组合依次
21:    通过最终 90 天留出和永久隔离最终确认；不得先看留出再组装策略，效率提升也不得来自放宽门禁。
22: 2. **样本量门槛**：留出期 <30 笔输出 `UNDERPOWERED`（不判 
…[truncated]
  ```
  </details>
