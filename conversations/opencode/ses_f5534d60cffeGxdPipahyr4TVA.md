---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f5534d60cffeGxdPipahyr4TVA"
title: "Implement doc-consistency gates + tests (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-16T15:17:16Z"
updated_at: "2026-09-16T15:25:07Z"
tokens_input: 99073
tokens_output: 601
cost: 0.0
parent_id: "ses_f55495de1ffeU7Bf0hQEDc3Md7"
---

# Implement doc-consistency gates + tests (@Sisyphus-Junior subagent)

## user · 2026-09-16T15:17:16Z

Repo: /home/georg/projects/alphamill (Python 3.11+, stdlib only for tools/, ruff line-length 100, single layout `tools/*.py`). Use `.venv/bin/python`.

CONTEXT
A documentation review of feature F003 produced 22 findings, all now fixed in the docs. Your job is to add the **regression gates** that lock those fixes (the fixer's evidence requirement). Do NOT edit any file under `docs/` — the docs are already final; if a gate fails against the current docs, REPORT it in your final message instead of changing docs.

GATE FILES TO CREATE / MODIFY
1. NEW `tools/check_doc_consistency.py`
2. NEW `tools/check_task_dag.py`
3. MODIFY `tools/validate_spec_lifecycle.py` (add ONE new check)
4. MODIFY `tools/verify.py` (register the two new gates)
5. NEW `tests/unit/test_check_doc_consistency.py`
6. NEW `tests/unit/test_check_task_dag.py`
7. MODIFY `tests/unit/test_validate_spec_lifecycle.py` (add tests for the new check)

Follow the existing house style exactly: read `tools/validate_spec_lifecycle.py`, `tools/check_doc_links.py`, `tools/check_dep_pins.py` and `tests/unit/test_check_doc_links.py`, `tests/unit/test_validate_spec_lifecycle.py` first. Style: module docstring (Chinese, states what + usage + exit code), `from __future__ import annotations`, stdlib only, pure functions separated from `main()`, `ROOT = pathlib.Path(__file__).resolve().parent.parent`, exit 0 pass / 1 fail.

=== FILE 1: tools/check_doc_consistency.py ===
Purpose: a declarative, text-anchored consistency gate that fails if any of the F003 fixes is reverted. Design it as a table of check entries; each entry has: `check_id` (matches the names below), `finding` (e.g. "F003-D001"), `requires` (list of `(path_relative_to_repo, literal_substring)`), `forbids` (same shape, optional). A check fails when any required substring is missing OR any forbidden substring is present. Also support a small number of custom callables for checks that need parsing (see #11 and #21).

Target doc paths:
- spec:   docs/features/0.2/F003-alphagen-vendor/spec.md
- design: docs/features/0.2/F003-alphagen-vendor/design.md
- tasks:  docs/features/0.2/F003-alphagen-vendor/tasks.md
- f007:   docs/features/0.2/F007-evaluation-gates/spec.md

Implement these checks (read the docs to pick the EXACT literals; the forbids below are the OLD contradicted text that must never come back):

D001 `factor_id_no_run_seq` (F003-D001): require design contains `factor_id = <generator>_<definition_digest[:12]>` and spec DR-002 contains `不含 run 序号`; forbid design containing `run_seq`, and forbid spec containing `_r<run_seq>`.
D002 `terminal_run_facts` (F003-D002): require design contains `四种终态` and `write 前一律视为未完成`-equivalent — pick exact literal from design; require design contains `只有 `status=completed` 的运行可被下游消费`; forbid design containing `run.json 不写出` and forbid `原因入日志`.
D003 `tier_ladder_matches_adr0001` (F003-D003): require spec contains `L1→L2 不在 time-box 内` or the exact equivalent and `L1 连续 2 周`; forbid spec containing `降级到 L1/L2` and `四条判据`.
D004 `smoke_obligations_linked` (F003-D004): require spec contains `not_yet_available` and `奖励频率维度抽查`; require tasks contains `not_yet_available`.
D005 `explicit_tuple_fields_match_adr0007` (F003-D005): require design contains `"mode": "explicit_tuples"`, `as_of_fidelity`, `universe_calendar_digest`, `provenance`; forbid design containing `[{dataset, data_version, value_digest}]`.
D006 `pit_mask_depends_on_f008` (F003-D006): require design contains `universe_at(T)` and spec contains `universe_at(T)`.
D007 `egress_claim_matches_guard_strength` (F003-D007): require spec contains `进程级` and design contains `不等于内核级网络隔离`; forbid spec containing `生成运行在无网络出口下完成`.
D008 `sigterm_not_completed` (F003-D008): require design contains `status=partial` and `不发` + `generation.run_completed`; forbid design containing `status=completed` + `termination=early`.
D009 `objective_includes_after_cost` (F003-D009): require design contains `min_after_cost_return` and spec contains `成本后收益`.
D010 `pool_is_executable_factordef` (F003-D010): require design contains `generator="pool"` and `可执行` (in the pool paragraph) and spec DR-004 contains `generator="pool"`; forbid design containing `AlphaPoolDef**：` (the old top-level definition) and `pool_id`（内容寻址）.
D013 `gpu_schedule_protocol_and_owner` (F003-D013): require design contains `queue_seq` and `kronos_offload`; require spec contains `queue_timeout`; require tasks contains `卸载动作 owner 是 F004`.
D014 `f007_declares_f003_upstream` (F003-D014): CUSTOM — parse f007 frontmatter `related_features:` and require `F003` in the list; require f007 body contains `**F003**`.
D015 `factordef_dto_matches_architecture` (F003-D015): require design contains `加载契约（可执行恢复）` and `factor_store.load()`.
D016 `ir003_schema_version_has_carrier` (F003-D016): require design GenerationRun line contains `schema_version`; require spec contains `AC-012` and `IR-003`; require tasks contains `schema_version`.
D017 `ac_body_covers_clauses` (F003-D017): CUSTOM — for each AC line in spec (format `- [ ] **AC-0NN** (...): body — tests: ...`), assert the AC body contains required literals: AC-003 → `DR-001 运行字段`; AC-005 → `可按 run 查询`; AC-009 → `DR-002`, `DR-003`, `TR-001`, `池成员`; AC-010 → `hostname`; AC-011 → `cli_contract`.
D018 `reproducibility_config_digest` (F003-D018): require design contains `config_digest` and `canonical config artifact`; require spec contains `config_digest`.
D019 `cli_builds_generation_request` (F003-D019): require design contains `强制字段的构造` and `--window` and `--config`.
D020 `hypothesis_has_applicable_state` (F003-D020): require design contains `applicable_state` and spec DR-003 contains `applicable_state`.
D021 `vendor_hygiene_has_upstream_baseline` (F003-D021): require spec contains `上游基线` and tasks contains `_upstream_baseline.json`.
D022 `active_feature_indexes_aligned` (F003-D022): CUSTOM — compute the non-done feature set from `docs/features/*/F*/spec.md` frontmatter `status`; require that (a) `CLAUDE.md`'s 当前活跃 Feature section lists exactly those feature IDs, (b) `docs/README.md`'s `非 done Feature 派生索引` row mentions exactly that set, (c) `BACKLOG.md`'s active table (rows before the first `## ` heading) has exactly those feature dir names. (Reuse `tools/validate_spec_lifecycle.parse_frontmatter` via import.)

CLI: `python tools/check_doc_consistency.py` → prints `check_doc_consistency: 全部通过` (exit 0) or `check_doc_consistency: 失败` + one line per violation prefixed `- [<check_id>] <message>` (exit 1). Expose `run_checks(root: pathlib.Path = ROOT) -> list[tuple[str, str]]`.

=== FILE 2: tools/check_task_dag.py ===
Purpose: lock D012 (task ordering/DAG). Enforce ONLY for features whose spec `status` ∈ {`ready-for-development`, `in-progress`, `review`} — deliberately EXCLUDE `done` (grandfathering F004/F001) and `draft` (matches the repo's existing status-scoped pattern at validate_spec_lifecycle.py). Document this scoping in the module docstring with the reason (other features' existing docs would fail a repo-wide gate).

Rules per enforced feature:
1. Parse ordered task IDs from checkbox lines `^- \[[ x]\] (T\d{3})` in tasks.md (both the `[TEST]` group and normal tasks count).
2. Parse dependency edges from the `## 4. 依赖与并行关系` section: every backticked segment containing `->`. Split the chain on `->`; split each hop side on `/`; form the cross-product of edges (e.g. `T030/T031 -> T036` yields T030→T036 and T031→T036). Ignore non-backticked text.
3. Violations: (a) an edge endpoint is not a defined task ID; (b) an edge goes "backward" — source ID > target ID (numbering is execution order); (c) the highest-numbered task has no incoming edge (收口任务必须有入边); (d) a task marked `[P]` in its task line appears as an edge target (the tasks template forbids `[P]` tasks with predecessors).
CLI: `python tools/check_task_dag.py` → `check_task_dag: 全部通过` / `失败` + `- <feature>: <message>` lines; exit 0/1. Expose `run_checks(root: pathlib.Path = ROOT) -> list[tuple[str, str]]` (feature name, message).

=== FILE 3: tools/validate_spec_lifecycle.py (one addition) ===
Add the D011 gate: for features with status ∈ {`ready-for-development`, `in-progress`, `review`} (again EXCLUDE `done` and `draft`), `tasks.md` MUST contain a level-3 heading `### [TEST] 组` (match `^###\s+\[TEST\]` after stripping fenced code blocks). Error message must name the file and the requirement, e.g. `tasks.md 缺少必需的 [TEST] 组（层 2 旅程验收轨）`. Keep everything else unchanged.

=== FILE 4: tools/verify.py ===
Register the two new gates in the `steps` list, right after the existing `文档相对链接检查` step, as `([sys.executable, "tools/check_task_dag.py"], "任务 DAG 检查")` and `([sys.executable, "tools/check_doc_consistency.py"], "文档一致性检查")`. Update the module docstring and the final success print string to mention them.

=== FILES 5-7: tests ===
House pattern: pure functions, `tmp_path` end-to-end, real mutations (see tests/unit/test_validate_spec_lifecycle.py).
- `tests/unit/test_check_doc_consistency.py`: (i) one test asserting `run_checks(ROOT) == []` on the real repo; (ii) **one parametrized mutation test per check_id** that copies the needed doc tree into `tmp_path`, removes/changes the required literal for that check in the relevant file, and asserts `run_checks(tmp_path)` reports that check_id. Build the tree by copying the real `docs/features/0.2/F003-alphagen-vendor/{spec,design,tasks}.md`, `docs/features/0.2/F007-evaluation-gates/spec.md`, plus `CLAUDE.md`, `docs/README.md`, `BACKLOG.md` and any other feature spec files needed by D022 — for D022, mutate e.g. CLAUDE.md's feature list. Keep the mutation helper generic (drive it from the check table's `requires` entries) rather than hand-writing 20 near-identical tests.
- `tests/unit/test_check_task_dag.py`: synthetic features under `tmp_path/docs/features/0.2/F001-demo/tasks.md` with `status: review` spec frontmatter; assert (a) a valid DAG passes; (b) an unknown-endpoint edge fails; (c) a backward edge fails; (d) a highest-task-without-incoming-edge fails; (e) a `[P]` task targeted by an edge fails; (f) a `draft` feature with the same violations is NOT reported (proves the status scoping).
- `tests/unit/test_validate_spec_lifecycle.py`: add two tests — a `review` feature whose tasks.md lacks `### [TEST] 组` is rejected; a `draft` feature without it passes. Reuse the existing helpers (`_review_spec`, `write_review_tree`, `REVIEW_TASKS`); you will need a tasks variant WITH the `[TEST]` heading for the passing case.

MUST DO
- Run `.venv/bin/python tools/check_doc_consistency.py`, `.venv/bin/python tools/check_task_dag.py`, `.venv/bin/python tools/validate_spec_lifecycle.py` and confirm all pass on the current repo.
- Prove each new gate can go RED: your parametrized mutation tests must actually fail when the gate is weakened — i.e. run the tests, then temporarily delete the body of one check (or invert one `requires`) and confirm the corresponding test fails, then restore. Report the exact commands + observed results.
- Run `.venv/bin/python -m pytest -q --confcutdir=tests --rootdir=tests tests/unit` and `.venv/bin/python -m ruff check tools tests` + `.venv/bin/python -m ruff format --check tools tests`; all must be clean.
- Then run the full `.venv/bin/python tools/verify.py` and report the final line + exit code. Note: the full suite may take several minutes; use a generous timeout.

MUST NOT DO
- Do NOT modify anything under `docs/` (docs are final; report failures instead).
- Do NOT weaken, skip, or `xfail` any check to make it pass. Do NOT use `as any`-style escapes, bare `except`, or `# noqa` without a specific rule code.
- Do NOT add third-party dependencies. stdlib only.
- Do NOT touch any other tool or test file.
- Do NOT git-commit anything.

REQUIRED TOOLS: read, grep, glob, edit, write, bash (with workdir).

FINAL REPORT: list every file created/modified, the exact command + observed result for (a) each gate green on the repo, (b) each mutation going red, (c) full verify.py result, and any check that could not be made to pass against the current docs (with the exact literal you expected and what you found).
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T15:17:16Z

- **tool**: `todowrite({"todos": [{"content": "tools/validate_spec_lifecycle.py and related house-style files: inspect existing gate patterns and Python references - expect exact conventions captured before edits", "status": "in_progress", "priority": "high"}, {"content": "tools/check_doc_consistency.py and tests/unit/test_check_doc_consistency.py: add declarative F003 regression gate plus mutation coverage - expect all D001-D022 checks implemented and tested", "status": "pending", "priority": "high"}, {"content": "to
…[truncated])`

 

> [reasoning] **Planning codegraph exploration before editing**

> [reasoning] **Prioritizing detailed todo list creation**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "tools/validate_spec_lifecycle.py and related house-style files: inspect existing gate patterns and Python references - expect exact conventions captured before edits",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "tools/check_doc_consistency.py and tests/unit/test_check_doc_consistency.py: add declarative F003 regression gate plus mutation coverage - expect all D001-D022 checks implemented and tested",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tools/check_task_dag.py and tests/unit/test_check_task_dag.py: add status-scoped task ordering gate plus synthetic feature coverage - expect all five violations and draft exclusion locked",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tools
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T15:18:28Z

- **tool**: `skill({"name": "programming", "user_message": "Implement Python 3.11 stdlib-only regression gates and tests in /home/georg/projects/alphamill. Load the Python reference requirements before editing."})`


> [reasoning] **Preparing to invoke programming skills**

> [reasoning] **Planning module file inspection**

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

## assistant · 2026-09-16T15:19:57Z

- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "Read and explain the exact house style, parsing helpers, status scoping, CLI output, and test fixture patterns in tools/validate_spec_lifecycle.py tools/check_doc_links.py tools/check_dep_pins.py tools/verify.py tests/unit/test_check_doc_links.py tests/unit/test_validate_spec_lifecycle.py. Return complete relevant source and call relationships; these are the files to modify or emulate.", "maxFiles": 8})`


> [reasoning] **Planning parallel file reading and codegraph queries**

> [reasoning] **Coordinating parallel reading of README and codegraph queries**

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
**Exploration: Read and explain the exact house style, parsing helpers, status scoping, CLI output, and test fixture patterns in tools/validate_spec_lifecycle.py tools/check_doc_links.py tools/check_dep_pins.py tools/verify.py tests/unit/test_check_doc_links.py tests/unit/test_validate_spec_lifecycle.py. Return complete relevant source and call relationships; these are the files to modify or emulate.**

Found 16 symbols across 7 files.

**Blast radius — what depends on these (update/verify before editing)**

- `validate_spec_lifecycle` (MarketGameSim/tools/spec_validation.py:1269) — 1 caller in `MarketGameSim/tools/validate_spec_lifecycle.py`; ⚠️ no covering tests found
- `check` (alphamill/tools/check_secrets.py:57) — 12 callers in `alphamill/tools/check_secrets.py`; tests: `alphamill/tes
…[truncated]
  ```
  </details>
