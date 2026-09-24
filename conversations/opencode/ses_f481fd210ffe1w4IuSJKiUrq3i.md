---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f481fd210ffe1w4IuSJKiUrq3i"
title: "T025 gpu_slot FIFO + offload (@Sisyphus-Junior subagent)"
project: "/home/georg/projects/alphamill"
model: "gpt-5.6-sol"
created_at: "2026-09-19T04:15:17Z"
updated_at: "2026-09-19T04:36:44Z"
tokens_input: 186787
tokens_output: 25013
cost: 0.0
parent_id: "ses_f4b788fc5ffelpbXkQ5UC3D1sW"
---

# T025 gpu_slot FIFO + offload (@Sisyphus-Junior subagent)

## user · 2026-09-19T04:15:17Z

Implement F003 task T025 in /home/georg/projects/alphamill (branch `feat/F003-alphagen-vendor` MUST be checked out; verify `git status -sb`, abort if not).

HARD CONVERGENCE RULES:
- Rewrite any single file AT MOST 3 times; then STOP and report the blocker.
- NEVER edit gate/config files: `tools/**`, `docs/**`, `pyproject.toml`, `tests/unit/test_f001_line_limit_exemptions.py`, `tests/unit/test_check_doc_consistency.py`. If a gate goes red due to a file you may not touch, REPORT and stop.
- `tools/verify.py` is MINE — do NOT run it.
- You MUST end with a written report; never loop silently.
- Target ≤300 lines/file; SPLIT rather than compress. Never `# fmt: off`/`# noqa`/`type: ignore`.
- Run `.venv/bin/ruff format <your files>` EARLY and before the final check.

FILES (exactly two; do NOT touch the pre-existing `tests/integration/test_f003_kronos_lifecycle.py`):
- NEW `src/alphamill/factor_factory/generators/gpu_slot.py`
- NEW `tests/unit/test_f003_gpu_slot.py`

READ FIRST: `docs/features/0.2/F003-alphagen-vendor/design.md` §5 (单槽 FIFO 可验证协议; 显存自检; CPU 回退; 与 Kronos 协同 live owner=F003) and §4 (`Kronos 生命周期 Contract`: status/stop/restore, `contract_version`, 幂等, 超时, 错误码 E_UNAVAILABLE/E_BUSY/E_TIMEOUT/E_UNSUPPORTED_VERSION; 观测→处置决策表) and §7; `spec.md` NFR-002/NFR-005/AC-010 (the FULL decision-table paragraph) and DR-001; `docs/alphamill-architecture.md` §7.1 (机器边界 + 观测→处置决策表 + 时段表); `generators/base.py`; `registry/run_store.py` (`UniverseSummary`, run fields `device`/`hostname`/`vram_limit_gb`/`kronos_offload` payload); `errors.py`.

PUBLIC SURFACE (implement exactly):
```python
@dataclass(frozen=True, kw_only=True)
class GpuSlotConfig:
    vram_limit_gb: float                 # configurable, NEVER a hard-coded constant
    window_start: str                    # "22:00"
    window_end: str                      # "06:30"
    queue_timeout_s: int = 1800

@dataclass(frozen=True, kw_only=True)
class VramReading:
    total_gb: float
    free_gb: float

def query_vram() -> VramReading | None: ...          # via nvidia-smi; None when unavailable (no GPU)
def vram_is_sufficient(reading: VramReading | None, *, limit_gb: float) -> bool: ...
def in_training_window(now: datetime, *, window_start: str, window_end: str) -> bool: ...

@dataclass(frozen=True, kw_only=True)
class QueueRecord:
    queue_seq: int
    run_id: str
    event: Literal["queued", "acquired", "released", "timeout"]
    ts: datetime
    vram_free_gb: float | None

class GpuSlot:
    def __init__(self, *, locks_dir: Path, config: GpuSlotConfig) -> None: ...
    def acquire(self, run_id: str, *, now: datetime | None = None) -> QueueRecord: ...
    def release(self, run_id: str, *, now: datetime | None = None) -> QueueRecord: ...
    def queue_records(self) -> list[QueueRecord]: ...

@dataclass(frozen=True, kw_only=True)
class KronosOffloadOutcome:
    action: Literal["stopped", "not_needed", "fail_closed"]
    reason: str
    vram_before_gb: float | None
    vram_after_gb: float | None

def offload_kronos(*, control_url: str | None, contract_version: str, client=None,
                   vram_reader=query_vram, timeout_s: float = 10.0) -> KronosOffloadOutcome: ...
```

NORMATIVE SEMANTICS
- FIFO protocol MUST be verifiable by TWO CONCURRENT runs (design §5): exclusive file lock at `<locks_dir>/gpu.slot` (flock), append-only queue at `<locks_dir>/gpu.queue` with one JSON line per record; `queue_seq` monotonically increasing; first-queued acquires first; on release the next waiter proceeds; waiting beyond `queue_timeout_s` → a `timeout` record and the caller gets `termination=queue_timeout` semantics (raise a typed error the caller maps to a `rejected` terminal run). Each record carries `queue_seq`/`run_id`/`ts`/`event`/`vram_free_gb`.
- VRAM self-check: after acquiring and before building tensors, read free VRAM; if `free_gb < limit_gb` → release the lock and re-queue (document the exact loop/return contract; do NOT start anyway). `limit_gb` comes from config; nothing hard-coded. `query_vram()` returning `None` (no GPU) is a legitimate state → the caller must pass `--allow-cpu` explicitly (this module exposes the predicate; do not silently allow).
- `offload_kronos` implements the architecture §7.1 观测→处置决策表 LITERALLY. Ordered rules: (a) `control_url is None` / connection refused AND the deployment manifest has no such service → `not_needed`; (b) HTTP 404 or `E_UNSUPPORTED_VERSION` → FALLBACK probe: `/health.device == "cpu"` OR device-side `memory.used` below threshold → `not_needed`, else `fail_closed` with `reason="endpoint_absent_no_gpu_tenant"` (record readings); (c) `status.device == "cpu"` → `not_needed`; (d) stop fails / control plane unreachable but service present → `fail_closed` (NEVER parallel-race the GPU); (e) success → `stopped` after confirming via `status.vram_bytes` that VRAM was released. MUST NOT depend on GPU process lists. All thresholds/URLs are parameters, never constants.
- The client is injectable (`client=None` default constructs a thin HTTP client) so tests need NO real service.
- Every outcome records the readings it used; `fail_closed` never degrades to a warning.

TESTS (`tests/unit/test_f003_gpu_slot.py`, plain `def test_*`, Chinese module docstring naming NFR-002/NFR-005/AC-010; NO real GPU or network — inject fakes):
- `in_training_window` across midnight (`22:00`–`06:30`): 23:00 in, 05:00 in, 12:00 out, 21:59 out, 06:29 in, 06:30 out.
- `vram_is_sufficient`: None → False; below limit → False; equal/above → True.
- FIFO with TWO processes (use `multiprocessing` or two `GpuSlot` instances + a real second process via `subprocess`/`multiprocessing.Process`) contending for one lock: assert first-queued acquires first, second waits, and after release the next record is `acquired`; assert `queue_seq` monotonically increases and every event type is recorded.
- timeout: a very small `queue_timeout_s` yields a `timeout` record and a typed error.
- VRAM-below-limit → releases the lock and does not report acquired.
- `offload_kronos` decision table: fake client covering EACH row — no service / connection refused → `not_needed`; 404 with `/health` device cpu → `not_needed`; 404 with no readable health → `fail_closed` + `reason="endpoint_absent_no_gpu_tenant"`; 404 with device-side memory.used above threshold → `fail_closed`; `status.device=="cpu"` → `not_needed`; stop failure → `fail_closed`; happy path → `stopped` with vram_after < vram_before.
- MUST include the case: "GPU process list is empty BUT `memory.used` is at/above threshold → fail_closed" (explicitly required by T025).
- config is fully parameterised: changing `GpuSlotConfig.vram_limit_gb` / window changes behavior (no constant leaks).

CONSTRAINTS: no `eval`, no bare `except`, no suppressions, no gate edits, no commit. Keep tests deterministic and fast (no real sleeping beyond ~1s total; use small timeouts and injected clocks). Run from /home/georg/projects/alphamill: `.venv/bin/ruff format <both files>`, `.venv/bin/ruff check <both files>`, `.venv/bin/python -m pytest -q tests/unit/test_f003_gpu_slot.py`, `.venv/bin/python -m pytest -q tests/unit/test_f001_line_limit_exemptions.py`. Report paths, exact commands + results, `wc -l`, and any decision-table row you had to interpret.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-19T04:15:17Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort", "priority": "high", "status": "in_progress"}, {"content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map", "priority": "high", "status": "pending"}, {"content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, 
…[truncated])`


> [reasoning] **Planning branch verification and todo writing**

> [reasoning] **Executing branch verification and preparing todos**
Step 1 of 5: verifying the required branch and worktree before reading or changing anything. I will abort immediately if `git status -sb` is not on `feat/F003-alphagen-vendor`.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, VRAM, windows, and Kronos decisions - expect failures against the missing module",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "src/alphamill/factor_factory/generators/gpu_slot.py: Implement the typed slot and offload contracts to satisfy
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:15:37Z

- **tool**: `bash({"command": "git status -sb", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `skill({"name": "programming", "user_message": "Implement Python F003 T025 in exactly gpu_slot.py and its unit test, using TDD and strict verification."})`

  <details><summary>tool output</summary>

  ```text
## feat/F003-alphagen-vendor


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

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

## assistant · 2026-09-19T04:15:45Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort", "priority": "high", "status": "completed"}, {"content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map", "priority": "high", "status": "in_progress"}, {"content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout
…[truncated])`


> [reasoning] **Planning documentation and code inspection**

> [reasoning] **Starting README file reading**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, VRAM, windows, and Kronos decisions - expect failures against the missing module",
    "status": "pending",
    "priority": "high"
  },
  {
    "content": "src/alphamill/factor_factory/generators/gpu_slot.py: Implement the typed slot and offload contracts to satis
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:15:58Z

- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/README.md"})`
- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "generators/base.py registry/run_store.py UniverseSummary run fields device hostname vram_limit_gb kronos_offload errors.py existing typed errors and HTTP client patterns relevant to implementing GPU slot queue and Kronos lifecycle", "maxFiles": 10})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md"})`

Step 1 of 5 done: the branch is exactly `feat/F003-alphagen-vendor`, and the worktree is clean. Step 2 is extracting the written contracts and existing Python conventions before the first edit.

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
**Exploration: generators/base.py registry/run_store.py UniverseSummary run fields device hostname vram_limit_gb kronos_offload errors.py existing typed errors and HTTP client patterns relevant to implementing GPU slot queue and Kronos lifecycle**

Found 13 symbols across 5 files.

**Blast radius — what depends on these (update/verify before editing)**

- `UniverseSummary` (alphamill/src/alphamill/factor_factory/registry/run_store.py:42) — 3 callers in `alphamill/src/alphamill/factor_factory/cli.py`; tests: `alphamill/tests/unit/test_f003_run_store.py`
- `QueueRow` (deepseek-harness/packages/client/ui-conversation/src/client/contract/queue.ts:11) — 4 callers in `deepseek-harness/packages/client/ui-conversation/src/client/contract/input.ts`, `deepseek-harness/packages/client/ui-conversation
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
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: related_features: [F001, F002, F007, F008]
6: topics: [factor-factory, alphagen, vendor, generators, m2]
7: doc_kind: design
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F003：AlphaGen vendor 与可插拔生成器平面 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
17: > 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
18: > 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。
19: 
20: ## 0. 输入与约束
21: 
22: - **行为契约**：`spec.md`
23: - **PRD / Architecture / System Design**：`docs/alphamill-prd.md` FR2.1~FR2.6；`docs/alphamill-architecture.md` §三（`factor_factory/`
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: status: developing
6: branch: feat/F003-alphagen-vendor
7: gate_version: 1
8: related_features: [F001, F002, F007, F008]
9: topics: [factor-factory, alphagen, vendor, generators, m2]
10: doc_kind: spec
11: created: 2026-09-14
12: updated: 2026-09-14
13: ---
14: 
15: # F003：AlphaGen vendor 与可插拔生成器平面
16: 
17: > Owner: Georg | Target: v0.2.x
18: 
19: ## 0. 来源与意图
20: 
21: - **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册）、FR2.2（可插拔生成器）、FR2.3（目标对齐）、FR2.4（纯度与能力边界）、FR2.6（探索组合）；目标 G3；里程碑 M2
22: - **架构来源**：`docs/alphamill-architecture.md` §三（`factor_factory/` 目录分工）、§4.0（闭环核心对象）、§4.1（FactorDef 契约）、§4.1.1（AlphaGen 适配契约与截面边界）、§7.1
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
1: # AlphaMill — 系统架构设计
2: 
3: > 版本：v0.1 | 日期：2026-09-13 | 配套：[alphamill-prd.md](./alphamill-prd.md)
4: 
5: ---
6: 
7: ## 〇、存储三件套分工（TimescaleDB / Parquet / DuckDB）
8: 
9: **不是三选一的竞品，是流水线上的三段**：Parquet 是文件格式（箱子），DuckDB 是查询引擎（开箱的手），TimescaleDB 是数据库服务（实时柜台）。
10: 
11: | | TimescaleDB | Parquet 湖 | DuckDB |
12: |---|---|---|---|
13: | 本质 | PG 时序扩展（数据库服务） | 列式文件格式（无服务） | 进程内 OLAP 查询引擎 |
14: | 写入 | ✅ 流式写入、幂等 upsert、可修订 | ❌ 不可变，只增新文件 | ❌ 不负责存储 |
15: | 擅长 | 实时最新值、连续聚合、Grafana 直连 | 大范围列扫描、快照不可变=可复现 | 直接对 Parquet 跑 SQL |
16: | 复现性 | ❌ 数据会被回补/修订 | ✅ 同一 data_version 永远同结果 | 无关（读的人） |
17: | 角色 | **联机运营库** | **研究快照**（封存账本） | **取数入口**（会计的手） |
18: 
19: ```text
20: CCXT 采集 ──写入──▶ TimescaleDB（联机运营库，随时改）
21
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:16:19Z

- **tool**: `codegraph_codegraph_explore({"projectPath": "/home/georg/projects/alphamill", "query": "Exact files: src/alphamill/factor_factory/generators/base.py src/alphamill/factor_factory/registry/run_store.py src/alphamill/errors.py tests/integration/test_f003_kronos_lifecycle.py. Return their relevant source and any existing Kronos lifecycle client/protocol or typed error patterns.", "maxFiles": 12})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/data-modeling.md"})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/error-handling.md"})`
- **tool**: `read({"filePath": "/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/httpx2-optimization.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/pyproject.toml"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor", "include": "tasks.md", "pattern": "T025|gpu_slot|Kronos", "output_mode": "content", "head_limit": 30})`


> [reasoning] **Planning precise codegraph queries with exact paths**

> [reasoning] **Inspecting pyproject and integration tests with codegraph**

> [reasoning] **Grep task T025 and read pyproject**
The contract fixes two key boundaries: queue timeout must surface as a typed rejection signal, and 404/version fallback must fail closed when device-side memory is unreadable. I’m now matching those rules to the repository’s existing models, error style, and injectable HTTP-client conventions.

  <details><summary>tool output</summary>

  ```text
**Exploration: Exact files: src/alphamill/factor_factory/generators/base.py src/alphamill/factor_factory/registry/run_store.py src/alphamill/errors.py tests/integration/test_f003_kronos_lifecycle.py. Return their relevant source and any existing Kronos lifecycle client/protocol or typed error patterns.**

Found 24 symbols across 1 file.

**Blast radius — what depends on these (update/verify before editing)**

- `TESTS` (ml4t-zh/tests/test_no_shadowed_tests.py:20) — 1 caller; tests: `ml4t-zh/tests/test_no_shadowed_tests.py`
- `Source` (deepseek-harness/packages/api/workspace-files/tests/fake-remote.client.ts:12) — 7 callers in `deepseek-harness/packages/client/ui-chat/src/client/conversation-nodes/chat-snapshot-builder.ts`, `deepseek-harness/packages/experimental/inspector/src/shared/cordis
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
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/error-handling.md</path>
<type>file</type>
<content>
1: # Error Handling
2: 
3: Typed errors, exhaustive matching, union returns, and resource safety.
4: 
5: ---
6: 
7: ## Typed errors — no bare strings
8: 
9: Error types carry structured data. Pattern matching works. Callers know exactly what can go wrong.
10: 
11: ```python
12: from dataclasses import dataclass
13: from typing import NewType
14: 
15: UserId = NewType("UserId", int)
16: 
17: @dataclass(frozen=True, slots=True)
18: class UserNotFoundError(Exception):
19:     user_id: UserId
20: 
21:     def __str__(self) -> str:  # REQUIRED — see note below
22:         return f"user {self.user_id} not fou
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/.cache/opencode/packages/oh-my-openagent@latest/node_modules/oh-my-openagent/dist/skills/programming/references/python/httpx2-optimization.md</path>
<type>file</type>
<content>
1: # httpx2 — Production Defaults
2: 
3: > **Source**: [pydantic/httpx2](https://github.com/pydantic/httpx2) — next-generation HTTP client for Python 3, continuation of HTTPX under Pydantic stewardship.
4: >
5: > **Rule**: Every network request MUST use `httpx2`. **ALL optimizations below are ON by default** — HTTP/2, brotli+zstd, tuned connection pool, fine-grained timeouts, transport retries, TCP_NODELAY. This is the baseline, not a stretch goal. A bare `httpx2.AsyncClient()` is a bug.
6: 
7: ---
8: 
9: ## 1. Installation — all extras, always
10: 
11: ```toml
12: # pyproject.toml
13: dependencies
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/pyproject.toml</path>
<type>file</type>
<content>
1: [build-system]
2: requires = ["hatchling"]
3: build-backend = "hatchling.build"
4: 
5: [project]
6: name = "alphamill"
7: version = "0.1.0"
8: description = "以因子假设吞吐量为核心的加密量化研究系统：程序化挖掘 → 统一评测 → 严格留出门 → Freqtrade 执行"
9: readme = "README.md"
10: requires-python = ">=3.11"
11: dependencies = [
12:   "ccxt>=4.4,<5",
13:   # F002 数据桥：Parquet 湖（写 PyArrow / 读 DuckDB）。运行时依赖同样锁范围，
14:   # 是否在范围内由 check_dep_pins 门禁强制（F002 spec 决策表：版本漂移显式改动）。
15:   "duckdb>=1.5,<2",
16:   "fastapi>=0.115,<1",
17:   "pandas>=2.2,<3",
18:   "psycopg2-binary>=2.9,<3",
19:   "pyarrow>=25,<26",
20:   "pydantic>=2.10,<3",
21:   "uvicorn>=0.34,<1",
22: ]
23: 
24: [project.scripts]
25: alphamill-generate = "alphamill.factor_factory.cli:
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 8 match(es) in 1 file(s)

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md
  32: - [ ] T004 (`NFR-002`, `NFR-005`): 打通并标定执行机 `qiaozhi-lt`——**先恢复 shell 接入**（env-manager 台账记录 2026-09-14 全端口复测 22/2222/2200/8022/3389/5985 全闭，当前无 shell 路径，按 `references/access-methods.md` §4 启用 Windows OpenSSH）；再在其 WSL2 内实测 CUDA 可用性与可用显存，按 §7.1 标定显存上限写进配置（不写死代码）；确认该机 F002 湖可读且通过完整性校验 — verify: `tests/unit/test_f003_gpu_slot.py`（能力探测纯函数）+ 在 `qiaozhi-lt` 上用 `alphamill.data_bridge.reader` 读一次真实快照
  67: [Omitted long matching line]
  78: - [ ] T033 (`AC-006`, `AC-010`): 在执行机的真实训练夜槽复跑产能与显存断言，证据记录 hostname、GPU 型号、显存峰值与耗时；开发机的同名用例跳过属预期，不得以其 CPU 结果替代。其中 `test_f003_kronos_lifecycle.py` 必须以 **0 xfailed** 通过（前置：BACKLOG「Kronos 服务生命周期端点」feature 已落地并部署于执行机，`KRONOS_CONTROL_URL` 指向 `kronos-si
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:16:52Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/generators/base.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/registry/run_store.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/integration/test_f003_kronos_lifecycle.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md", "offset": 58, "limit": 18})`
- **tool**: `glob({"path": "/home/georg/projects/alphamill", "pattern": "**/errors.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/generators"})`


> [reasoning] **Locating errors.py with glob and raw reads**

> [reasoning] **Inspecting package directory structure and dataclass design**

> [reasoning] **Evaluating flock lock behavior and VRAM acquire logic**

> [reasoning] **Investigating VRAM check behavior without GPU**

> [reasoning] **Designing acquire behavior for CPU fallback**

> [reasoning] **Choosing timeout error name and parameters**

> [reasoning] **Checking VRAM threshold source**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/generators/base.py</path>
<type>file</type>
<content>
1: """F003 可插拔生成器的共享类型与边界校验。"""
2: 
3: from __future__ import annotations
4: 
5: from collections.abc import Mapping
6: from dataclasses import dataclass
7: from datetime import UTC, datetime, timedelta
8: from typing import TYPE_CHECKING, Literal, Protocol, TypeAlias
9: 
10: from alphamill.factor_factory.canonical import JSONValue
11: from alphamill.factor_factory.errors import ConclusionFieldError, SchemaValidationError
12: from alphamill.factor_factory.factor import FactorDef
13: 
14: if TYPE_CHECKING:
15:     from alphamill.factor_factory.generators.binding import SnapshotBinding
16: 
17: Expression: TypeAlias = tuple[str, ...]
18: RejectionReason: TypeAlias = Literal
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/registry/run_store.py</path>
<type>file</type>
<content>
1: """Persist generation run manifests, canonical configs, and append-only events."""
2: 
3: from __future__ import annotations
4: 
5: import fcntl
6: import json
7: import os
8: import re
9: import tempfile
10: import types
11: from collections.abc import Mapping, Sequence
12: from dataclasses import asdict, dataclass, fields, is_dataclass, replace
13: from datetime import UTC, datetime
14: from pathlib import Path
15: from typing import Literal, TypeAlias, TypeVar, get_args, get_origin, get_type_hints
16: from uuid import uuid4
17: 
18: from alphamill.factor_factory import canonical, errors
19: from alphamill.factor_factory.canonical import JSONValue
20: from alphami
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/integration/test_f003_kronos_lifecycle.py</path>
<type>file</type>
<content>
1: """F003 契约测试：Kronos 服务生命周期控制面（架构 §7.1，客户端可见行为）。
2: 
3: **契约目标是真实推理服务 `kronos-signal-real`（执行机 GPU 实例）**——夜槽卸载为的是
4: 释放 GPU 显存，mock 服务（`kronos-signal`，8001，无 torch）无显存可释放，不是本契约的
5: 对象，也不是合法的测试目标（R4-002）。服务端端点（`GET /lifecycle/status`、
6: `POST /lifecycle/stop`、`POST /lifecycle/restore`）属待分配 feature（BACKLOG「Kronos
7: 服务生命周期端点」）——本文件以 `xfail(strict=True)` 显式声明当前「服务端未实现」的
8: 先红态：端点落地后 XPASS 即红，落地 feature 必须移除本标记并补 `E_BUSY` / `E_TIMEOUT`
9: 错误路径用例（F004 tasks §5）。
10: 
11: 开关纪律（双保险，缺一即 skip）：
12: - 未设 `ALPHAMILL_INTEGRATION` → skip（与 F004 容器套件同纪律）；
13: - 未设 `KRONOS_CONTROL_URL` → skip（**无默认地址**：契约目标必须显式指定，避免默认
14:   打到 mock 的 404 上制造假红/假绿；T033 的 verify 命令给出执行机取值）。
15: 设了以后失败就
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md</path>
<type>file</type>
<content>
58: 
59: - [x] T020 (`FR-003`, `AC-003`): 实现 `lake_tensor` 完整路径——多 dataset 合并、重采样（默认 1h）、PIT 宇宙掩码（消费 F008 `universe_at(T)` 与台账 digest；F008 未落地时用显式 universe 配置并把 digest 与来源写进 `run.json`）、`feature_map` 与其 digest — verify: `tests/integration/test_f003_lake_tensor.py`
60: - [ ] T021 (`FR-004`, `AC-004`): 实现 `alphagen_adapter`——token 序列编译闭包、`meta["expression"]` 反解、`data_columns` 经 `feature_map` 反解、截面边界（no-signal 语义） — verify: `tests/unit/test_f003_alphagen_adapter.py`
61: - [x] T022 (`FR-005`, `AC-005`): 实现算子能力登记表（时序/截面语义、窗口语义、crypto 24/7 窗口换算），并导出为 `F007` 可消费的版本化能力清单（含 `schema_version`；`F007` FR-002 的已登记算子能力消费源） — verify: `tests/unit/test_f003_operator_registry.py`
62: - [x] 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 2 file(s)

/home/georg/projects/alphamill/src/alphamill/factor_factory/errors.py
/home/georg/projects/alphamill/src/alphamill/data_bridge/errors.py
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they run in background
// System will notify you when each completes
```

WHY:
- Agents can perform deeper,
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/generators</path>
<type>directory</type>
<entries>
__init__.py
__pycache__/
alphagen_vendor/
base.py
binding_checks.py
binding.py
egress_guard.py
expression_compiler.py
lake_tensor.py
manual/
mining_capability.py
operator_registry.py
purity.py
universe.py
write_guard.py

(15 entries)
</entries>
  ```
  </details>

## assistant · 2026-09-19T04:17:28Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/errors.py"})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/src/alphamill", "include": "*.py", "pattern": "urlopen\\(|urllib\\.request|requests\\.(get|post)|class .*Client\\(Protocol\\)|HTTPError|URLError", "output_mode": "content", "head_limit": 100})`
- **tool**: `grep({"path": "/home/georg/projects/alphamill/tests/unit", "include": "test_f003_*.py", "pattern": "multiprocessing|Process\\(|Queue\\(|monkeypatch|FakeClient|Protocol", "output_mode": "content", "head_limit": 100})`
- **tool**: `lsp_status({})`


> [reasoning] **Assessing HTTP client options and dependencies**

> [reasoning] **Inspecting FastAPI client usage and error handling**

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/errors.py</path>
<type>file</type>
<content>
1: """F003 因子工厂的共享类型化错误。
2: 
3: CLI 依此区分「可拒绝」(BindingValidationError / SchemaValidationError)
4: 与「运行失败」(其余)。
5: """
6: 
7: from __future__ import annotations
8: 
9: 
10: class FactorFactoryError(Exception):
11:     """因子工厂所有错误的基类。"""
12: 
13: 
14: class MiningCapabilityError(FactorFactoryError):
15:     """挖掘依赖或所需 CUDA 能力不可用，必须拒绝启动。"""
16: 
17: 
18: class SchemaValidationError(FactorFactoryError):
19:     """产物 schema 非法。"""
20: 
21: 
22: class UnknownSchemaVersionError(SchemaValidationError):
23:     """schema_version 不在已知集合内；禁止做兼容性猜测。"""
24: 
25: 
26: class ConclusionFieldError(SchemaValidationError):
27:     """生成结果携带了评测结论字段（AI 权限红线，AC-001）。"""
28: 
29: 
30: class UnknownHypot
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
No matches found
[Agent Usage Reminder]

You called a search/fetch tool directly without leveraging specialized agents.

RECOMMENDED: Use task with explore/librarian agents for better results:

```
// Parallel exploration - fire multiple agents simultaneously
task(subagent_type="explore", load_skills=[], prompt="Find all files matching pattern X")
task(subagent_type="explore", load_skills=[], prompt="Search for implementation of Y")
task(subagent_type="librarian", load_skills=[], prompt="Lookup documentation for Z")

// Then continue your work while they run in background
// System will notify you when each completes
```

WHY:
- Agents can perform deeper, more thorough searches
- Background tasks run in parallel, saving time
- Specialized agents have domain expertise
- Reduces context wind
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 14 match(es) in 2 file(s)

/home/georg/projects/alphamill/tests/unit/test_f003_mining_capability.py
  47: def test_all_missing_modules_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
  49: monkeypatch.setattr(
  66: def test_one_missing_module_is_named(monkeypatch: pytest.MonkeyPatch) -> None:
  69: monkeypatch.setattr(
  88: def test_required_cuda_unavailable_raises(monkeypatch: pytest.MonkeyPatch) -> None:
  90: monkeypatch.setattr(
  106: def test_all_capabilities_available_passes(monkeypatch: pytest.MonkeyPatch) -> None:
  108: monkeypatch.setattr(

/home/georg/projects/alphamill/tests/unit/test_f003_lifecycle_contract_config.py
  28: def test_control_url_has_no_default(monkeypatch) -> None:
  29: monkeypatch.setenv("ALPHAMILL_INTEGRATION", "1")
  30: monkeypatch.delenv("K
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Configured LSP servers: 42
Installed LSP servers: 0

- typescript: missing; source=builtin; extensions=.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts
- deno: missing; source=builtin; extensions=.ts, .tsx, .js, .jsx, .mjs
- vue: missing; source=builtin; extensions=.vue
- eslint: missing; source=builtin; extensions=.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue
- oxlint: missing; source=builtin; extensions=.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .vue, .astro, .svelte
- biome: missing; source=builtin; extensions=.ts, .tsx, .js, .jsx, .mjs, .cjs, .mts, .cts, .json, .jsonc, .vue, .astro, .svelte, .css, .graphql, .gql, .html
- gopls: missing; source=builtin; extensions=.go
- ruby-lsp: missing; source=builtin; extensions=.rb, .rake, .gemspec, .ru
- basedpyright: missing; source=builtin; e
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:17:42Z

- **tool**: `grep({"path": "/home/georg/projects/alphamill", "pattern": "kronos_vram_idle_threshold|idle_threshold|memory\\.used|memory.used", "include": "*.{py,md,json,yaml,yml,toml}", "output_mode": "content", "head_limit": 100})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_f003_run_store.py", "offset": 1, "limit": 180})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_f003_mining_capability.py", "offset": 1, "limit": 150})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/src/alphamill/factor_factory/generators/mining_capability.py"})`


> [reasoning] **Deciding LSP installation decline and diagnostics approach**

> [reasoning] **Analyzing client interface and test style requirements**

> [reasoning] **Modeling service absence with control_url and exceptions**

> [reasoning] **Designing client abstraction with introspection**

> [reasoning] **Designing flexible HTTP client wrapper**

> [reasoning] **Clarifying control_url none semantics**

> [reasoning] **Analyzing VRAM threshold sourcing**

> [reasoning] **Evaluating VRAM threshold parameter options**

> [reasoning] **Searching docs for VRAM idle threshold**

> [reasoning] **Planning repo grep for config key**
A specification gap is now isolated: `offload_kronos` must compare device-side `memory.used` with a configurable threshold, but the mandated function signature has no threshold argument. I’m checking whether that threshold already lives in an existing client/config contract; if not, I’ll keep the public signature unchanged and carry it through the injected client boundary.

  <details><summary>tool output</summary>

  ```text
Found 13 match(es) in 7 file(s)

/home/georg/projects/alphamill/docs/alphamill-architecture.md
  617: | HTTP 404 / `E_UNSUPPORTED_VERSION` | 端点未实现，**回落探测** `/health` 的 `device` 与设备侧显存读数（`nvidia-smi --query-gpu=memory.used`），**不依赖 GPU 进程列表**（WSL2 下 `nvidia-smi` 不列出 GPU 进程） | `/health.device=cpu`，或设备侧 `memory.used` 低于可配阈值 `kronos_vram_idle_threshold` → 记 `offload_not_needed`（`reason=endpoint_absent_no_gpu_tenant`，读数写入 `kronos_offload`），继续夜槽；`memory.used` 达到阈值或任一读数不可得 → **fail-closed** 留在单槽队列 |

/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md
  178: `E_UNSUPPORTED_VERSION`（端点未实现）按 404/`E_UNSUPPORTED_VERSION` 回落探测：`/health.device=cpu` 或设备侧 `memory.used` 低于阈值 → `offload_not_needed`；达到阈值或读数不可得 → fail-closed（不依赖 GPU 进程列表），`reason=endpoint_absent_no_gpu_tenant`，

/h
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_f003_run_store.py</path>
<type>file</type>
<content>
1: """F003 T008 运行存储契约：DR-001 / TR-001 / TR-002 / AC-009 / AC-012。"""
2: 
3: from __future__ import annotations
4: 
5: import json
6: import re
7: from dataclasses import replace
8: from datetime import UTC, datetime, timedelta
9: from pathlib import Path
10: 
11: import pytest
12: 
13: from alphamill.factor_factory.canonical import JSONValue, canonical_json_bytes, utc_iso
14: from alphamill.factor_factory.errors import (
15:     RunStoreError,
16:     SchemaValidationError,
17:     UnknownSchemaVersionError,
18: )
19: from alphamill.factor_factory.generators.base import (
20:     GenerationCounts,
21:     RejectionCounts,
22:     Window,
23: )
24: from alphamill.factor_factory.generat
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_f003_mining_capability.py</path>
<type>file</type>
<content>
1: """F003 挖掘能力自检测试：NFR-005 / T015 要求缺失能力 fail-closed。"""
2: 
3: from __future__ import annotations
4: 
5: from collections.abc import Callable
6: from dataclasses import dataclass
7: from types import ModuleType
8: 
9: import pytest
10: 
11: from alphamill.factor_factory import errors
12: from alphamill.factor_factory.generators import mining_capability
13: 
14: EXPECTED_REQUIRED_MODULES = ("torch", "numpy", "stable_baselines3", "gymnasium")
15: 
16: 
17: @dataclass(frozen=True, slots=True)
18: class _CudaAvailability:
19:     available: bool
20: 
21:     def is_available(self) -> bool:
22:         return self.available
23: 
24: 
25: class _TorchModule(ModuleType):
26:     cud
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/src/alphamill/factor_factory/generators/mining_capability.py</path>
<type>file</type>
<content>
1: """F003 挖掘运行的依赖与 CUDA 能力自检。"""
2: 
3: from __future__ import annotations
4: 
5: from importlib import import_module
6: from types import ModuleType
7: from typing import Final, Protocol, runtime_checkable
8: 
9: from alphamill.factor_factory.errors import MiningCapabilityError
10: 
11: MINING_REQUIRED_MODULES: Final[tuple[str, ...]] = (
12:     "torch",
13:     "numpy",
14:     "stable_baselines3",
15:     "gymnasium",
16: )
17: 
18: 
19: @runtime_checkable
20: class _CudaCapability(Protocol):
21:     def is_available(self) -> bool: ...
22: 
23: 
24: @runtime_checkable
25: class _TorchCapability(Protocol):
26:     cuda: _CudaCapability
27: 
28: 
29: def re
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:18:29Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort", "priority": "high", "status": "completed"}, {"content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map", "priority": "high", "status": "completed"}, {"content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, 
…[truncated])`


> [reasoning] **Designing threshold handling and testing approach**

> [reasoning] **Evaluating threshold integration methods**

> [reasoning] **Defining KronosClient protocol with threshold property**

> [reasoning] **Deciding default idle threshold handling**

> [reasoning] **Clarifying threshold defaults and test coverage**

> [reasoning] **Planning hidden restore method implementation**

> [reasoning] **Planning hidden restore implementation**

> [reasoning] **Defining flexible HTTP client protocol**

> [reasoning] **Designing fallback and stop logic**

> [reasoning] **Defining stop action idempotence and error handling**

> [reasoning] **Implementing service presence checks**

> [reasoning] **Clarifying health and VRAM fallback logic**

> [reasoning] **Defining fail-closed conditions and VRAM reading recording**

> [reasoning] **Setting VRAM before reading only**

> [reasoning] **Implementing robust GPU query with timeout**

> [reasoning] **Designing GPU slot queue with locking**

> [reasoning] **Refining queue re-acquisition logic**

> [reasoning] **Refining VRAM queue handling logic**

> [reasoning] **Designing concurrency and timeout logic**

> [reasoning] **Implementing locked queue append and read**

> [reasoning] **Designing custom GPU queue timeout error**

> [reasoning] **Defining acquire method semantics and error details**

> [reasoning] **Clarifying lock release and acquisition order**

> [reasoning] **Refining VRAM retry and FIFO test logic**

> [reasoning] **Implementing concurrent process acquisition test**

> [reasoning] **Refactoring GPU slot acquisition and release**

> [reasoning] **Implementing timeout and termination in GPU slot tests**

> [reasoning] **Allowing zero queue timeout for immediate attempts**

> [reasoning] **Designing timeout and window checks**

> [reasoning] **Planning training window gating in acquire**

> [reasoning] **Implementing dynamic now computation**

> [reasoning] **Analyzing lock acquisition race conditions**

> [reasoning] **Refining queue state tracking and parsing logic**

> [reasoning] **Adding timezone-aware timestamps and default queue records**

> [reasoning] **Evaluating frozen dataclass exceptions**

> [reasoning] **Designing domain HTTP client protocols**

> [reasoning] **Designing default URL client dataclass**

> [reasoning] **Planning status parsing and error handling**

> [reasoning] **Estimating file size distribution for splitting**

> [reasoning] **Planning parametrized test functions**

> [reasoning] **Designing fake client API dataclasses**

> [reasoning] **Designing mutable fixture class for fake client**

> [reasoning] **Planning TDD approach with test-first and formatting**

> [reasoning] **Creating stub module to prevent import errors**

> [reasoning] **Planning early test and skeleton integration**

> [reasoning] **Balancing TDD with minimal rewrites**

> [reasoning] **Drafting test file with multiprocessing details**

> [reasoning] **Planning GPU slot mock injection**

> [reasoning] **Implementing fork-based GPU query monkeypatch**

> [reasoning] **Verifying event sequencing and timeout behavior**

> [reasoning] **Adding window timeout and fake client tests**

> [reasoning] **Assessing fail-closed conditions for service and resource checks**

> [reasoning] **Designing parameterized tests for error code handling**

> [reasoning] **Implementing dataclasses and stubbing methods**

> [reasoning] **Outlining test skeleton and patch plan**
Step 2 of 5 done. Implementation shape is fixed: `gpu.queue` is the sequencing authority under its own `flock`, `gpu.slot` is the exclusive resource lock, low VRAM releases and appends a fresh queue position, and `None` VRAM is preserved for the caller’s explicit CPU decision. The injected Kronos client will carry deployment presence plus the configurable idle-memory threshold because the mandated `offload_kronos` signature exposes neither directly.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, VRAM, windows, and Kronos decisions - expect failures against the missing module",
    "status": "in_progress",
    "priority": "high"
  },
  {
    "content": "src/alphamill/factor_factory/generators/gpu_slot.py: Implement the typed slot and offload contracts to sat
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:22:38Z

- **tool**: `apply_patch({"patchText": "*** Begin Patch\n*** Add File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n+\"\"\"GPU slot arbitration and Kronos offload coordination for F003.\"\"\"\n+\n+from __future__ import annotations\n+\n+from collections.abc import Callable\n+from dataclasses import dataclass\n+from datetime import datetime\n+from pathlib import Path\n+from typing import Literal\n+\n+from alphamill.factor_factory.errors import FactorFactoryError\n+\n+\n+@dataclass(f
…[truncated])`


> [reasoning] **Designing multiprocessing test scaffold**

> [reasoning] **Refining GPU slot timeout and window tests**

> [reasoning] **Validating acquire and timeout event behavior**

> [reasoning] **Planning endpoint parameterization tests**

> [reasoning] **Estimating test code line counts**
Step 3 of 5: adding the complete behavioral test file and an importable public-surface scaffold. The first run is intentionally red on unimplemented behavior, while already exercising a real second process for FIFO ordering and fake-only Kronos/GPU boundaries.

  <details><summary>tool output</summary>

  ```text
Success. Updated the following files:
A src/alphamill/factor_factory/generators/gpu_slot.py
A tests/unit/test_f003_gpu_slot.py

COMMENT/DOCSTRING DETECTED - IMMEDIATE ACTION REQUIRED

Your recent changes contain comments or docstrings, which triggered this hook.
You need to take immediate action. You must follow the conditions below.
(Listed in priority order - you must always act according to this priority order)

CRITICAL WARNING: This hook message MUST NEVER be ignored, even if you receive it multiple times.
You MUST provide corresponding explanation or action for EACH occurrence of this message.
Ignoring this message or failing to respond appropriately is strictly prohibited.

PRIORITY-BASED ACTION GUIDELINES:

1. This is a comment/docstring that already existed before
	-> Explain to t
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:24:33Z

- **tool**: `bash({"command": ".venv/bin/ruff format src/alphamill/factor_factory/generators/gpu_slot.py tests/unit/test_f003_gpu_slot.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Deciding on module docstring removal**

> [reasoning] **Planning test size reduction under limit**

> [reasoning] **Running initial formatting and analysis**
The detected test comments are intentional BDD markers required by the Python workflow’s Given/When/Then rule, and the Chinese test module docstring is explicitly required by T025. The source module and fake-client docstrings identify non-obvious coordination/test boundaries; I’ll keep only those that remain necessary after implementation and line-limit cleanup.

  <details><summary>tool output</summary>

  ```text
1 file reformatted, 1 file left unchanged


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-19T04:24:57Z

- **tool**: `bash({"command": ".venv/bin/python -m pytest -q tests/unit/test_f003_gpu_slot.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Running initial pytest tests**

  <details><summary>tool output</summary>

  ```text
FFFFFFFFFFFFFFFFFFFFFFFFFF                                               [100%]
=================================== FAILURES ===================================
_______________ test_training_window_across_midnight[23-0-True] ________________

hour = 23, minute = 0, expected = True

    @pytest.mark.parametrize(
        ("hour", "minute", "expected"),
        [(23, 0, True), (5, 0, True), (12, 0, False), (21, 59, False), (6, 29, True), (6, 30, False)],
    )
    def test_training_window_across_midnight(hour: int, minute: int, expected: bool) -> None:
        # Given: the configured overnight boundary and a UTC wall-clock time.
        now = datetime(2026, 9, 19, hour, minute, tzinfo=UTC)
        # When: membership is evaluated.
>       actual = in_training_window(now, window_start="22:00", 
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:25:07Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort", "priority": "high", "status": "completed"}, {"content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map", "priority": "high", "status": "completed"}, {"content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, 
…[truncated])`


> [reasoning] **Confirming todo4 progress and planning source implementation**

> [reasoning] **Designing protocols and default client classes**

> [reasoning] **Finalizing JSON payload handling**

> [reasoning] **Planning error handling and client restore method**

> [reasoning] **Refining time parsing approach**

> [reasoning] **Defining GPU queue exceptions**

> [reasoning] **Refining file descriptor locking and error handling**

> [reasoning] **Verifying queue record handling and event parsing**

> [reasoning] **Reviewing release function locking and error handling**

> [reasoning] **Refining offload_kronos error handling and version checks**

> [reasoning] **Refining VRAM usage handling and error catching**

> [reasoning] **Planning concise patch within line limits**

> [reasoning] **Enforcing strict line count and formatting**

> [reasoning] **Assessing code line budget and dependencies**

> [reasoning] **Planning client protocol simplification and HTTP refactoring**

> [reasoning] **Implementing private restore method**
The red run is valid: all 26 cases fail at the public scaffold’s `NotImplementedError`, not at imports or fixtures. Step 3 of 5 is complete; step 4 now replaces only the source scaffold with the minimum queue, probe, and lifecycle implementation.

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, VRAM, windows, and Kronos decisions - expect failures against the missing module",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "src/alphamill/factor_factory/generators/gpu_slot.py: Implement the typed slot and offload contracts to satis
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:26:38Z

- **tool**: `apply_patch({"patchText": "*** Begin Patch\n*** Update File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n@@\n-\"\"\"GPU slot arbitration and Kronos offload coordination for F003.\"\"\"\n-\n-from __future__ import annotations\n-\n-from collections.abc import Callable\n-from dataclasses import dataclass\n-from datetime import datetime\n-from pathlib import Path\n-from typing import Literal\n-\n-from alphamill.factor_factory.errors import FactorFactoryError\n+\"\"\"GPU s
…[truncated])`

I’m implementing one explicit acquisition loop: queue head plus open window may try `flock`; insufficient measured VRAM appends `released`, unlocks, and appends a new `queued` position; timeout appends its record and raises `GpuQueueTimeoutError`. `query_vram() is None` remains observable as `vram_free_gb=None`, leaving CPU authorization to the caller instead of silently granting it.

  <details><summary>tool output</summary>

  ```text
Success. Updated the following files:
M src/alphamill/factor_factory/generators/gpu_slot.py

COMMENT/DOCSTRING DETECTED - IMMEDIATE ACTION REQUIRED

Your recent changes contain comments or docstrings, which triggered this hook.
You need to take immediate action. You must follow the conditions below.
(Listed in priority order - you must always act according to this priority order)

CRITICAL WARNING: This hook message MUST NEVER be ignored, even if you receive it multiple times.
You MUST provide corresponding explanation or action for EACH occurrence of this message.
Ignoring this message or failing to respond appropriately is strictly prohibited.

PRIORITY-BASED ACTION GUIDELINES:

1. This is a comment/docstring that already existed before
	-> Explain to the user that this is an existing co
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:28:05Z

- **tool**: `bash({"command": ".venv/bin/ruff format src/alphamill/factor_factory/generators/gpu_slot.py && .venv/bin/python -m pytest -q tests/unit/test_f003_gpu_slot.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Planning docstring clarification and testing**
These three new docstrings are required contract documentation: `query_vram` states the explicit no-process-list safety rule, `acquire` documents the requested requeue/return/timeout contract, and `offload_kronos` anchors the public fail-closed behavior to architecture §7.1. No narrative comments were added to production logic.

> [reasoning] **Running code formatting before tests**

  <details><summary>tool output</summary>

  ```text
1 file reformatted
.................FFFFFFFF.                                               [100%]
=================================== FAILURES ===================================
_________ test_absent_endpoint_with_cpu_health_is_not_needed[absent0] __________

absent = _Response(status_code=404, payload={})

    @pytest.mark.parametrize(
        "absent",
        [_Response(404, {}), _Response(200, {"error": "E_UNSUPPORTED_VERSION"})],
    )
    def test_absent_endpoint_with_cpu_health_is_not_needed(absent: _Response) -> None:
        # Given: lifecycle is absent but health proves a CPU tenant.
        client = _FakeClient(statuses=(absent,), health=_Response(200, {"device": "cpu"}))
        # When: fallback probing runs.
>       outcome = offload_kronos(control_url="http://kronos", contr
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:28:22Z

- **tool**: `apply_patch({"patchText": "*** Begin Patch\n*** Delete File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n*** Add File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n+\"\"\"GPU slot arbitration and Kronos offload coordination for F003.\"\"\"\n+\n+from __future__ import annotations\n+\n+import fcntl\n+import json\n+import os\n+import subprocess\n+import time\n+from collections.abc import Callable\n+from dataclasses import asdict, da
…[truncated])`


> [reasoning] **Evaluating rewrite limit enforcement**

> [reasoning] **Planning major source refactor to meet line limits**

> [reasoning] **Identifying simplification strategies to reduce source size**

> [reasoning] **Designing fake client with domain methods**

> [reasoning] **Simplifying client and optimizing code size**

> [reasoning] **Planning patch application for size check**

> [reasoning] **Assessing line count target for test files**

> [reasoning] **Designing minimal client protocol and serialization**

> [reasoning] **Evaluating Callable client vs object**

> [reasoning] **Designing _HttpCall dataclass and request handling**

> [reasoning] **Implementing request closure and fallback integration**

> [reasoning] **Assessing function parameter complexity**

> [reasoning] **Estimating code size reductions**

> [reasoning] **Planning test consolidation and parameterization**

> [reasoning] **Designing parameterized test cases with dataclass**

> [reasoning] **Optimizing test count by combining few cases**

> [reasoning] **Consolidating fallback test parameters**

> [reasoning] **Streamlining control decision tests**

> [reasoning] **Planning file delete and add patch**

> [reasoning] **Designing queue serialization methods**

> [reasoning] **Implementing queue read helper and refining HTTP client**

> [reasoning] **Designing streamlined fallback helper**

> [reasoning] **Refining outcome helper with grouped readings**

> [reasoning] **Refining stop payload error handling**

> [reasoning] **Consolidating exception handling with OSError**
The first green attempt exposed one mechanical bug: keyword-only outcome dataclasses were constructed positionally. Since the formatted source also exceeded the requested 300-line target, I’m using the final source rewrite to fix both at once by collapsing the injectable client to one typed request contract and reusing a keyword-safe outcome factory.

  <details><summary>tool output</summary>

  ```text
Success. Updated the following files:
D src/alphamill/factor_factory/generators/gpu_slot.py
A src/alphamill/factor_factory/generators/gpu_slot.py

COMMENT/DOCSTRING DETECTED - IMMEDIATE ACTION REQUIRED

Your recent changes contain comments or docstrings, which triggered this hook.
You need to take immediate action. You must follow the conditions below.
(Listed in priority order - you must always act according to this priority order)

CRITICAL WARNING: This hook message MUST NEVER be ignored, even if you receive it multiple times.
You MUST provide corresponding explanation or action for EACH occurrence of this message.
Ignoring this message or failing to respond appropriately is strictly prohibited.

PRIORITY-BASED ACTION GUIDELINES:

1. This is a comment/docstring that already existed befo
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:31:14Z

- **tool**: `bash({"command": "wc -l src/alphamill/factor_factory/generators/gpu_slot.py tests/unit/test_f003_gpu_slot.py", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": ".venv/bin/ruff check src/alphamill/factor_factory/generators/gpu_slot.py", "workdir": "/home/georg/projects/alphamill", "timeout": 120000})`


> [reasoning] **Confirming rewrite limit reached and task blocked**

> [reasoning] **Clarifying rewrite count allows one more attempt**

> [reasoning] **Planning final source line count verification**
The same production docstrings remain intentional and contract-bearing: the module ownership line, the no-process-list probe rule, the exact low-VRAM/no-GPU acquire behavior, and the public fail-closed lifecycle rule. I’m measuring the compact rewrite now; one source rewrite remains under the convergence cap if it still exceeds 300 lines.

  <details><summary>tool output</summary>

  ```text
362 src/alphamill/factor_factory/generators/gpu_slot.py
  335 tests/unit/test_f003_gpu_slot.py
  697 total


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
E501 Line too long (105 > 100)
   --> src/alphamill/factor_factory/generators/gpu_slot.py:254:101
    |
252 |         return status, payload
253 |
254 |     def restore(self, control_url: str, contract_version: str, timeout_s: float) -> tuple[int, _Payload]:
    |                                                                                                     ^^^^^
255 |         return self.request(
256 |             _HttpCall(
    |

Found 1 error.


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-19T04:31:42Z

- **tool**: `apply_patch({"patchText": "*** Begin Patch\n*** Delete File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n*** Add File: /home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py\n+\"\"\"GPU slot arbitration and Kronos offload coordination for F003.\"\"\"\n+\n+from __future__ import annotations\n+\n+import fcntl\n+import json\n+import os\n+import subprocess\n+import time\n+from collections.abc import Callable\n+from dataclasses import asdict, da
…[truncated])`


> [reasoning] **Evaluating code size reduction strategies**

> [reasoning] **Refactoring HTTP client for simplification**

> [reasoning] **Considering nested classes to save lines**

> [reasoning] **Evaluating HTTP client refactoring options**

> [reasoning] **Simplifying HTTP client design by dropping Protocol and dataclass**

> [reasoning] **Refactoring queue append and lock usage**

> [reasoning] **Planning code size reduction and refactoring**

> [reasoning] **Refactoring request handling logic**

> [reasoning] **Optimizing error class and request function**

> [reasoning] **Evaluating file size target feasibility**

> [reasoning] **Simplifying HTTP client with urllib.request**

> [reasoning] **Planning combined source and test patch**

> [reasoning] **Drafting compact fake request tests**

> [reasoning] **Parameterizing connection and status tests**

> [reasoning] **Verifying process termination handling**

> [reasoning] **Estimating code section line counts**

> [reasoning] **Refining locking and unlocking logic**

> [reasoning] **Implementing flexible HTTP client handling**

> [reasoning] **Planning hidden restore method implementation**

> [reasoning] **Refactoring error handling with decode helper**

> [reasoning] **Verifying data types and defaults**
The measured sizes are `362` and `335`, so both miss the explicit target. I’m applying the last source rewrite and first test rewrite together: same behavior, fewer private layers, no line-compression tricks, and the test rows become parameterized decision tables while retaining the named high-memory/no-process regression.

  <details><summary>tool output</summary>

  ```text
Success. Updated the following files:
D src/alphamill/factor_factory/generators/gpu_slot.py
A src/alphamill/factor_factory/generators/gpu_slot.py
D tests/unit/test_f003_gpu_slot.py
A tests/unit/test_f003_gpu_slot.py

COMMENT/DOCSTRING DETECTED - IMMEDIATE ACTION REQUIRED

Your recent changes contain comments or docstrings, which triggered this hook.
You need to take immediate action. You must follow the conditions below.
(Listed in priority order - you must always act according to this priority order)

CRITICAL WARNING: This hook message MUST NEVER be ignored, even if you receive it multiple times.
You MUST provide corresponding explanation or action for EACH occurrence of this message.
Ignoring this message or failing to respond appropriately is strictly prohibited.

PRIORITY-BASED ACTION
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:35:38Z

- **tool**: `bash({"command": "wc -l src/alphamill/factor_factory/generators/gpu_slot.py tests/unit/test_f003_gpu_slot.py", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] **Verifying source line count limit**
The test comments are the required Given/When/Then structure, and its Chinese module docstring names all three requested requirements. The four production docstrings are the same narrowly scoped public/safety contracts already justified; no additional explanatory comments were introduced.

> [reasoning] **Counting lines and words**

  <details><summary>tool output</summary>

  ```text
319 src/alphamill/factor_factory/generators/gpu_slot.py
  292 tests/unit/test_f003_gpu_slot.py
  611 total


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-19T04:35:50Z

- **tool**: `todowrite({"todos": [{"content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort", "priority": "high", "status": "completed"}, {"content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map", "priority": "high", "status": "completed"}, {"content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, 
…[truncated])`


> [reasoning] **Confirming rewrite limit reached and stopping**

> [reasoning] **Deciding against final tests due to rewrite limit**

> [reasoning] **Summarizing command results and test outcomes**

> [reasoning] **Marking todos as cancelled due to blocker**

> [reasoning] **Confirming final todo cancellations and statuses**

  <details><summary>tool output</summary>

  ```text
[
  {
    "content": "Repository root: Run git status -sb to enforce the required branch precondition - expect feat/F003-alphagen-vendor and no abort",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "F003 docs and Python conventions: Read required contracts, adjacent symbols, and language rules to derive behavior - expect a decision-complete implementation map",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "tests/unit/test_f003_gpu_slot.py: Add red tests for FIFO, timeout, VRAM, windows, and Kronos decisions - expect failures against the missing module",
    "status": "completed",
    "priority": "high"
  },
  {
    "content": "src/alphamill/factor_factory/generators/gpu_slot.py: Implement the typed slot and offload contracts to satis
…[truncated]
  ```
  </details>

## assistant · 2026-09-19T04:36:17Z


> [reasoning] **Summarizing findings and next steps**

> [reasoning] **Detailing blockers and test results**

> [reasoning] **Preparing concise final report outline**
**Blocked**
Stopped under the three-rewrite convergence rule.

- Branch verified: `feat/F003-alphagen-vendor`
- Only created:
  - [gpu_slot.py](/home/georg/projects/alphamill/src/alphamill/factor_factory/generators/gpu_slot.py)
  - [test_f003_gpu_slot.py](/home/georg/projects/alphamill/tests/unit/test_f003_gpu_slot.py)
- No forbidden files touched.
- Final `wc -l`: source `319`, test `292`. Source misses the ≤300 target by 19 lines.
- Splitting would require a third file, conflicting with the exact-two-files constraint.

Commands run:

```text
git status -sb
# ## feat/F003-alphagen-vendor

.venv/bin/ruff format <both files>
# 1 reformatted, 1 unchanged

.venv/bin/python -m pytest -q tests/unit/test_f003_gpu_slot.py
# Expected red: 26 failed on scaffold NotImplementedError

.venv/bin/ruff format gpu_slot.py && pytest ...
# 18 passed, 8 failed from keyword-only outcome construction
```

That construction defect was rewritten, but the convergence cap was reached before final formatting/testing. Therefore Ruff, focused pytest, line-limit gate, and LSP verification are not final-green.

Decision-table interpretation: because the required `offload_kronos` signature has no idle-memory threshold or deployment-manifest argument, those values are carried by the injected client.

Next action: authorize either one private helper file or a source limit of 319 lines.
