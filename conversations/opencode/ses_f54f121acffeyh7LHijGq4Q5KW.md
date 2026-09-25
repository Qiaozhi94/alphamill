---
tool: "opencode"
tool_name: "OpenCode"
session_id: "ses_f54f121acffeyh7LHijGq4Q5KW"
title: "审计门禁与任务图 (@explore subagent)"
project: "/home/georg/projects/alphamill"
model: "deepseek-v4.1-flash"
created_at: "2026-09-16T16:31:13Z"
updated_at: "2026-09-16T16:38:12Z"
tokens_input: 127345
tokens_output: 10533
cost: 0.0455
parent_id: "ses_f54f50b00fferZAnoSPa21C62p"
---

# 审计门禁与任务图 (@explore subagent)

## user · 2026-09-16T16:31:13Z

Read-only audit /home/georg/projects/alphamill current relevant docs/tools/tests against a333394..HEAD, focusing task DAG semantics, lifecycle status, newly added consistency gates, snapshot binding, schema/version, F007/F008 contracts and regression risks. Inspect tools/check_doc_consistency.py, tools/check_task_dag.py, tools/validate_spec_lifecycle.py, tools/verify.py and tests. Return exact file:line evidence, severity/category/origin/pattern_tag, and identify contradictions or gates that can pass invalid docs. Do not edit files. Chinese output preferred.
<!-- OMO_INTERNAL_INITIATOR -->

## assistant · 2026-09-16T16:31:13Z

- **tool**: `bash({"command": "git log --oneline a333394..HEAD 2>/dev/null | head -50; echo \"---COUNT---\"; git rev-list --count a333394..HEAD 2>/dev/null; echo \"---DIFFSTAT---\"; git diff --stat a333394..HEAD 2>/dev/null | tail -60", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "ls -la; echo \"---TOOLS---\"; ls -la tools 2>/dev/null; echo \"---TESTS---\"; ls -la tests 2>/dev/null", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `glob({"pattern": "**/check_doc_consistency.py"})`
- **tool**: `glob({"pattern": "**/check_task_dag.py"})`
- **tool**: `glob({"pattern": "**/validate_spec_lifecycle.py"})`
- **tool**: `glob({"pattern": "**/verify.py"})`


> [reasoning] Let me start by exploring the repository structure and the specific files mentioned. The user wants a read-only audit comparing current docs/tools/tests against a333394..HEAD, focusing on task DAG semantics, lifecycle status, consistency gates, snapshot binding, schema/version, F007/F008 contracts, and regression risks. They want exact file:line evidence with severity/category/origin/pattern_tag, contradictions, and gates that can pass invalid docs.

Let me begin with parallel tool calls.
<analysis>
**Literal Request**: 对 alphamill 仓库相对 a333394..HEAD 做只读审计，检查 docs/tools/tests，重点 DAG 语义、生命周期状态、一致性门、快照绑定、schema/version、F007/F008 合约与回归风险；检查 4 个指定工具与测试，给出 file:line 证据、severity/category/origin/pattern_tag，指出矛盾与可放行非法文档的门。

**Actual Need**: 需要一份可行动的审计报告，能直接定位"哪些门形同虚设/哪些文档与实现矛盾/哪些合约未覆盖"，以便决定修复优先级。

**Success Looks Like**: 每条发现带 绝对路径:行号、severity、category、origin(commit)、pattern_tag，并明确指出放行非法文档的具体路径与原因。
</analysis>

I'll start with parallel reconnaissance across the repo, git history, and the named files.

  <details><summary>tool output</summary>

  ```text
36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）
59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断
b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用
5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点
ccf577d fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约
65e1832 fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组并重编号回写任务
d659db7 test(f003): 新增任务 DAG/文档一致性/[TEST] 组门禁 + 变异单测（D011/D012 及各 finding 回归锁定）
fcc14ad fix(f003): R2 复核修正——架构 pool 契约、Kronos owner 改 F003、AC-012 载体等
ab30da9 fix(f003): D002/D007/D010 术语归一——终态小写、池版本键改 factor_id、egress 措辞
32f4942 fix(f003): D011+D012 tasks 补 [TEST] 旅程验收组并修正任务图顺序
07e6649 fix(f003): D021 vendor 卫生补冻结上游基线，使逐行比对可复现
da4df56 fix(f003): D019 CLI 可构造完整 GenerationRequest + 默认值随运行留痕
60a51e8 fix(f003): D017+D018 AC 子
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
total 564
drwxr-xr-x 23 georg georg   4096 Sep 15 22:00 .
drwxr-xr-x 14 georg georg   4096 Sep 16 21:50 ..
drwxr-xr-x  2 georg georg   4096 Sep 17 00:31 .code-review-graph
lrwxrwxrwx  1 georg georg     62 Sep 13 12:30 .codegraph -> /home/georg/.omo/codegraph/projects/alphamill-9c04b030e83dacf2
-rw-r--r--  1 georg georg    312 Sep 15 22:00 .dockerignore
drwxr-xr-x 10 georg georg   4096 Sep 17 00:31 .git
drwxr-xr-x  3 georg georg   4096 Sep 10 00:25 .github
-rw-r--r--  1 georg georg   1222 Sep 14 01:49 .gitignore
drwxr-xr-x  3 georg georg   4096 Sep 13 12:35 .omo
drwxr-xr-x  3 georg georg   4096 Sep 10 23:06 .pytest_cache
drwxr-xr-x  3 georg georg   4096 Sep 10 23:07 .ruff_cache
-rw-r--r--  1 georg georg    343 Sep 15 22:00 .sdd.json
drwxr-xr-x  6 georg georg   4096 Sep 13 13:45 .venv
-rw-r-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/check_doc_consistency.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/check_task_dag.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
Found 1 file(s)

/home/georg/projects/alphamill/tools/verify.py
  ```
  </details>

## assistant · 2026-09-16T16:31:19Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/check_task_dag.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tools/verify.py"})`


> [reasoning] Let me read the four tools and the tests, plus docs and spec files. Let me parallelize.
Now reading the four named tools and their tests in parallel.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_doc_consistency.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """文档一致性门禁（doc review F003 契约断言回归门）。
3: 
4: 把 F003 检视闭环中被修复的每一处契约写成**可红的断言**：要求项缺失、或旧矛盾
5: 文本回归时即判红。每条 check 对应一个 finding id，便于检视方逐条独立核对。
6: 
7: 覆盖范围：
8:   - 声明式文本断言（`TEXT_CHECKS`）：要求/禁止的字面量，按 finding 分组；
9:   - 解析式断言：F007 是否声明 F003 上游（D014）、AC 断言是否覆盖其引用的子句
10:     （D017）、活跃 feature 索引三处是否一致（D022）。
11: 
12: 用法：python tools/check_doc_consistency.py
13: 退出码 0 = 全部通过；1 = 存在违规。
14: """
15: 
16: from __future__ import annotations
17: 
18: import dataclasses
19: import pathlib
20: import re
21: import sys
22: 
23: ROOT = pathlib.Path(__file__).resolve().parent.parent
24: 
25: SPEC = "docs/features/0.2/F003-alphagen-vendor/spec.md"
26: DESIGN = "docs/features/0.2/F00
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/check_task_dag.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """任务依赖 DAG 校验（doc review F003-D012 回归门）。
3: 
4: 对进入开发流转的 Feature（spec status ∈ {ready-for-development, in-progress,
5: review}）校验 `docs/features/<version>/Fxxx-*/tasks.md`：
6: 
7:   - §4「依赖与并行关系」里所有边端点都是已定义的任务 ID；
8:   - 边一律「向前」：源 ID < 目标 ID（任务编号即执行顺序，禁止依赖后序任务）；
9:   - 最高编号任务（收口任务）必须有至少一条入边；
10:   - `[P]` 任务不得同时声明前置边（tasks 模板规定）。
11: 
12: **作用域说明**：不收 `done`（F001/F004 等历史 Feature 已收口，纳入会立刻破坏
13: 既有文档）与 `draft`（尚未进入流转）。这与 `validate_spec_lifecycle.py` 的
14: status 作用域模式一致。
15: 
16: 用法：python tools/check_task_dag.py
17: 退出码 0 = 全部通过；1 = 存在违规。
18: """
19: 
20: from __future__ import annotations
21: 
22: import pathlib
23: import re
24: import sys
25: 
26: ROOT = pathlib
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """规格生命周期校验（骨架版，node flavor 的 check-feature-gates.mjs 的 Python 对应）。
3: 
4: 校验 docs/features/<version>/Fddd-*/ 三件套：
5:   - 三件套齐全、frontmatter 合法、ID 唯一、status/gate_version 合法
6:   - spec.md 是状态唯一真相源（design/tasks 不得声明独立 status）
7:   - gate v1：固定章节结构、Q/DQ 关闭、AC 引用第 4 节真实需求、
8:     review/done 的 tests 路径真实存在
9:   - 进入开发流转（ready-for-development / in-progress / review）的 tasks.md
10:     必须含 `### [TEST] 组`（层 2 旅程验收轨）
11:   - BACKLOG.md 与所有非 done Feature 双向集合一致
12: 
13: 纯函数 + CLI 分离，只用标准库；参考项目在此基础上抽了共享 spec_validation 模块
14: 并补了变异测试。用法：python tools/validate_spec_lifecycle.py
15: 退出码 0 = 全部通过；1 = 存在违规。
16: """
17: 
18: from __future__ import annotations
19: 
20: import
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tools/verify.py</path>
<type>file</type>
<content>
1: #!/usr/bin/env python3
2: """本地统一验证入口（公开验证唯一入口）。
3: 
4: 按固定顺序运行：规格生命周期校验 → 文档相对链接检查 → 任务 DAG 检查
5: → 文档一致性检查 → dev 依赖 pin 范围检查 → 密钥模式扫描 → pytest
6: → ruff check → ruff format check。任一步失败即记录，全部跑完后汇总返回非零
7: （不短路）。
8: 
9: 各底层命令仍可单独用于定位，但 README、SOP 与 CLAUDE 不再各自维护完整命令清单，
10: 统一指向本入口。
11: 
12: 用法：
13:     python3 tools/verify.py
14: 退出码 0 表示全部通过；非 0 时打印失败步骤。
15: """
16: 
17: from __future__ import annotations
18: 
19: import pathlib
20: import subprocess
21: import sys
22: 
23: ROOT = pathlib.Path(__file__).resolve().parent.parent
24: 
25: 
26: def _run(cmd: list[str], label: str) -> bool:
27:     print(f"\n== {label} ==")
28:     proc = subprocess.run(cmd, cwd=ROOT)
29:     if proc.returncode != 0:
30: 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:31:22Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py"})`
- **tool**: `bash({"command": "ls tests/unit; echo \"---\"; git diff a333394..HEAD -- tools/verify.py tools/validate_spec_lifecycle.py", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now let me read the tests and the docs (F003 and F007 spec/design/tasks). Also check the diff a333394..HEAD to understand what changed. Let me parallelize.

Key immediate observations from the tools:
1. `check_task_dag.py` line 27: ENFORCED_STATUSES excludes `done` and `draft`. So if a spec status is a typo like "ready-for-development " or an unknown status, DAG check is skipped. But validate_spec_lifecycle catches illegal status. However, a feature could be status `done` with invalid DAG — that's by design exemption.

2. `check_task_dag.py` line 121: `last = max(ids)` - string max, fine for T\d{3}. But if tasks.md only has T001... last. The gate requires last task has an incoming edge. But if edges parsed = empty and ids non-empty, then it errors. Fine.

3. `check_task_dag.py` line 117-119: checks dst in parallel. But doesn't check src in parallel. Actually [P] tasks must not have dependency edges at all - the template says [P] tasks must not declare prerequisites. Code checks if dst (target) is a [P] task, then error. But [P] semantics: a [P] task can be run in parallel with siblings, meaning it shouldn't have incoming edges. Actually the check "dst in parallel" catches incoming edges to [P]. That's correct-ish. But it doesn't catch [P] task having outgoing edges? That might be fine.

4. `parse_edges`: uses EDGE_SEGMENT_RE to find backticked segments containing "->". Then splits on "->". But if a segment has "T001 -> T002（...）" it might break. Also if edges are written without backticks, they're silently ignored. That's a gate that can pass invalid docs: §4 edges not in backticks are ignored. Also the cartesian expansion `A/B -> C/D`.

5. `check_tasks`: `errors = list(dict.fromkeys(errors))` at line 112 dedups undefined endpoint errors. Then backwards check only if both in ids. Then parallel check. Then last.

Potential gap: edges from cross-feature `F008.IR-002 -> Txxx` are ignored entirely (line 93 fullmatch T\d{3}). So a task that depends on an undefined external endpoint passes. Also note docstring line 81 says non-T endpoints not validated.

6. `check_doc_consistency.py`: TextCheck is pure substring matching. This is the key "gates that can pass invalid docs" — substring presence doesn't assert semantics; contradictory text elsewhere passes. E.g., requires "四种终态" but doesn't verify the four states are correct. Forbids specific strings only. Many gates check `requires` on one file and `forbids` on another. Indeed the audit says "identify contradictions or gates that can pass invalid docs."

7. `check_doc_consistency.py` line 323: `if "**F003**" not in text` - F007 spec must contain bold F003. But related_features regex `\bF003\b` in frontmatter. Note parse_frontmatter for related_features: `related_features: [F002, F003, F004, F008]` — regex `\bF003\b` works. But if frontmatter uses multi-line YAML list, parse fails → false? Actually would error (good). But if the value is quoted with brackets, it works.

8. `check_active_feature_indexes` line 348: `expected = set(active_features(root))` returns dir_name keys. Then compares BACKLOG rows to expected dir names. Note: BACKLOG_ROW_RE captures `F\d{3}-[^|]+`. Good.

CLAUDE_ACTIVE_RE matches lines starting with `- F\d{3}`. Only lines with leading `-`. If Claude uses a table instead, no match → error. Fine.

README_ACTIVE_RE = `当前\s*((?:F\d{3}\s*/\s*)+F\d{3})` — requires at least two F-ids separated by `/`. If only one active feature, it would NOT match (because `(?:F\d{3}\s*/\s*)+` requires at least one "Fxxx /" then Fxxx). So with exactly one active feature, README check silently gets readme_ids = set() and if expected_ids has 1 element → error. That's a bug but fails closed (errors). Actually it would cause false failure, not pass invalid. Hmm, but consider: if expected_ids is empty (all done), readme_ids = set() == expected → pass even if README still lists actives? Wait if expected empty, expected_ids empty, readme_ids from regex... if README says "当前 F001 / F002" then readme_ids = {F001,F002} != empty → error. If README says "当前无" no match → empty == empty pass. Fine.

Actually the more subtle issue: README regex requires the "当前" text. Let me check docs/README.md actual text.

9. `validate_spec_lifecycle.py` gate v0: if gate_version != "1", returns after structural checks — so features with gate_version "0" skip section/AC/Q/TEST checks entirely. That's a documented gate. But note line 178 ALLOWED_GATES = {"0","1"}. A feature can set gate_version: 0 to bypass all content gates. Severity: high-ish. But that's by design for legacy. Need to check which features have gate_version 0.

10. `validate_spec_lifecycle.py` line 241-254: tests paths only enforced review/done. In ready-for-development, no test paths required. So an AC with no tests passes at ready-for-development. That's by design perhaps.

11. `question_section_issues`: only allows Q/DQ checkboxes or "无". open_questions counts `- [ ]` Q/DQ. But if a question is written as `- [x] DQ-1` it's closed. If written without checkbox it errors in question_section_issues. Good.

12. Line 210: TEST_GROUP_RE `^###\s+\[TEST\]` with re.M. It requires at least one `### [TEST]` heading. But doesn't require the group to be under section 3 or contain tasks. A doc could add an empty `### [TEST] 组` heading and pass. Also note check_doc_consistency F007-D001 requires specific strings for F007 only.

13. Line 130: open_questions matches `^-\s+\[ \]\s+[QD]Q?-\d+`. So `- [ ] Q-1` and `- [ ] DQ-1`. Note `[QD]Q?` matches Q, DQ, QQ? Actually `[QD]` then optional `Q`. "QQ-1" would match. Minor.

14. Backlog parsing: row_re requires 4 columns with `[spec](...)`. Lines before first `## ` heading. If a non-done feature row is formatted differently (missing spec link), it's silently not parsed → then `active` loop adds "BACKLOG 缺少非 done Feature". Good fail closed. But if a done feature row is malformed it's also silently ignored — not a big issue.

Wait — `check_backlog`: it breaks at first line starting with `## `. But the BACKLOG active index table is at top before first `## `. If the table is below a `## 当前活跃` heading, then NO rows parsed → active features all reported missing → fail. Let me check BACKLOG.md.

15. `verify.py` runs pytest on tests/unit and tests/integration only; property/simulation excluded. That's a coverage gap (regression risk). Also ruff check.

Let me now read tests and docs.

Also importantly: check_doc_consistency forbids list uses substrings that might appear coincidentally. E.g., forbids `(DESIGN, "run_seq")` and `(DESIGN, "_r<run_seq>")`. If design uses `run_seq` anywhere else legitimately, fails. But more important is "gates that can pass invalid docs": e.g., `requires` "四种终态" but the doc could still list wrong states elsewhere.

Let me get the actual docs content and tests.
Now reading tests and F003/F007 docs, plus the diff of the tools against a333394.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py</path>
<type>file</type>
<content>
1: """check_doc_consistency 回归测试（修复方证据：每条断言必须可红）。
2: 
3: 两组断言：
4:   - 真实仓库上 `run_checks` 全绿；
5:   - 逐条 `TEXT_CHECKS` 做变异：删掉要求文本（或写回废弃文本）后，该 check 必须报错。
6:     变异在 tmp_path 的副本上做，不触碰仓库文件。
7: """
8: 
9: from __future__ import annotations
10: 
11: import pathlib
12: import shutil
13: 
14: import pytest
15: 
16: from tools import check_doc_consistency as cdc
17: 
18: REPO = cdc.ROOT
19: TEXT_CHECK_IDS = [c.check_id for c in cdc.TEXT_CHECKS]
20: ALL_DOC_FILES = {
21:     cdc.SPEC,
22:     cdc.DESIGN,
23:     cdc.TASKS,
24:     cdc.F007_SPEC,
25:     cdc.F007_DESIGN,
26:     cdc.F007_TASKS,
27: }
28: 
29: 
30: def _materialize(tmp_path: pathlib.Path, rels: set[str]) -> None:
31:     #
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_check_task_dag.py</path>
<type>file</type>
<content>
1: """check_task_dag 回归测试（修复方证据：DAG 门禁可红，且作用域正确）。
2: 
3: 用 tmp_path 下的合成 Feature 覆盖五类违规，并验证 `draft` 不在作用域内
4: （否则会把尚未进入流转的 Feature 一并判红）。
5: """
6: 
7: from __future__ import annotations
8: 
9: import pathlib
10: 
11: from tools import check_task_dag as dag
12: 
13: FEATURE_DIR = pathlib.Path("docs") / "features" / "0.2" / "F001-demo"
14: 
15: 
16: def write_feature(root: pathlib.Path, status: str, tasks: str) -> None:
17:     d = root / FEATURE_DIR
18:     d.mkdir(parents=True, exist_ok=True)
19:     (d / "spec.md").write_text(
20:         "---\n"
21:         "kind: feature\n"
22:         "id: F001\n"
23:         'version: "0.2"\n'
24:         f"status: {status}\n"
25:         "gate_v
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/tests/unit/test_validate_spec_lifecycle.py</path>
<type>file</type>
<content>
1: """validate_spec_lifecycle 回归测试（CURRENT-code.md C002）。
2: 
3: 三组真实校验：frontmatter 解析与 status 必填、AC tests 路径逃逸检查、
4: BACKLOG 双向一致性。全部走 verify_repo(root=tmp_path) 端到端断言。
5: """
6: 
7: from __future__ import annotations
8: 
9: import pathlib
10: 
11: from tools import validate_spec_lifecycle as vsl
12: 
13: SPEC_GATE0_DRAFT = """---
14: kind: feature
15: id: F001
16: version: "0.1"
17: status: draft
18: gate_version: 0
19: ---
20: 
21: # F001-demo
22: 
23: 正文占位。
24: """
25: DESIGN_MIN = "# F001-demo design\n"
26: TASKS_MIN = "# F001-demo tasks\n"
27: BACKLOG_HEADER = "# BACKLOG\n\n| Feature | 版本 | 状态 | 链接 |\n|---|---|---|---|\n"
28: 
29: 
30: def write_feature(tmp_path: pathlib
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
__pycache__
test_apply_migrations.py
test_backup_nas_contract.py
test_check_dep_pins.py
test_check_doc_consistency.py
test_check_doc_links.py
test_check_secrets.py
test_check_task_dag.py
test_doc_gate_command.py
test_f001_backfill_report.py
test_f001_backfill_window_source.py
test_f001_compose_contract.py
test_f001_credentials.py
test_f001_exchange_defaults.py
test_f001_line_limit_exemptions.py
test_f001_supervisor_contract.py
test_f002_cli_contract.py
test_f002_digest.py
test_f002_exporter.py
test_f002_manifest.py
test_f002_partitions.py
test_f002_paths.py
test_f002_reader_contract.py
test_f002_reconcile.py
test_f002_registry.py
test_f002_symbol_map.py
test_f002_timer_contract.py
test_f004_compose_profile_contract.py
test_f004_kronos_runtime_contract.py
test_historical_backfill_review_fix
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:33:57Z

- **tool**: `bash({"command": "python3 tools/validate_spec_lifecycle.py; echo \"EXIT=$?\"; echo \"==== DAG ====\"; python3 tools/check_task_dag.py; echo \"EXIT=$?\"; echo \"==== DOC ====\"; python3 tools/check_doc_consistency.py; echo \"EXIT=$?\"", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/BACKLOG.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/CLAUDE.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/README.md"})`


> [reasoning] Now I have good visibility. Let me look for actual docs to find contradictions. The test file test_check_doc_consistency.py has stale mutation strings that may not match current docs (e.g. `related_features: [F002, F003, F004]` vs actual `[F002, F003, F004, F008]`). This will make the test `test_f007_upstream_declaration_goes_red` fail (replace no-op). Similarly README test replaces "当前 F003/F007/F008" but actual might be "当前 F003/F007/F008". Let me check the actual docs and run the tools to see current state.

Let me read F003 and F007 docs, BACKLOG.md, CLAUDE.md, docs/README.md. And run the gates.

Let me parallelize reads and command runs.
Now checking actual doc contents, BACKLOG/README/CLAUDE indexes, and running the gates to see current status.

  <details><summary>tool output</summary>

  ```text
validate_spec_lifecycle: 全部通过
EXIT=0
==== DAG ====
check_task_dag: 全部通过
EXIT=0
==== DOC ====
check_doc_consistency: 全部通过
EXIT=0


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/BACKLOG.md</path>
<type>file</type>
<content>
1: # BACKLOG —— 活跃 Feature 索引
2: 
3: 本文件只列 `status != done` 的 Feature，是 `docs/features/<version>/Fxxx-*/spec.md`
4: frontmatter `status` 的派生索引（由门禁脚本双向校验，不是独立状态真相源）。
5: 
6: | Feature | 版本 | 状态 | 链接 |
7: |---|---|---|---|
8: | F003-alphagen-vendor | 0.2 | draft | [spec](docs/features/0.2/F003-alphagen-vendor/spec.md) |
9: | F007-evaluation-gates | 0.2 | draft | [spec](docs/features/0.2/F007-evaluation-gates/spec.md) |
10: | F008-universe-expansion | 0.2 | draft | [spec](docs/features/0.2/F008-universe-expansion/spec.md) |
11: 
12: > 规则：feature 状态变更（spec frontmatter）时必须同步本表；`done` 的 Feature 移出本表，
13: > 交付记录进入 `docs/features/releases/<version>.md`。
14: > 示例行（复制后替换，链接必须指向真实 spec.md）：
15: > `| F001-<name> | 0.1 | 
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
<path>/home/georg/projects/alphamill/docs/README.md</path>
<type>file</type>
<content>
1: ---
2: topics: [docs, index, ownership]
3: doc_kind: guide
4: created: 2026-09-06
5: updated: 2026-09-15
6: ---
7: 
8: # AlphaMill 文档地图
9: 
10: 本文件是仓库文档的**唯一入口与所有权索引**：从一个入口最多两次点击即可到达任何
11: 权威文档。它只记录所有权和链接，**不复制正文**。产品、架构、数据模型、Feature 状态
12: 和流程各有且只有一个机器可读拥有者。
13: 
14: ## 权威文档所有权矩阵
15: 
16: | 信息 | 唯一拥有者 | 说明 |
17: |---|---|---|
18: | 产品目标、范围和路线 | `alphamill-prd.md` | 产品真相源（指标体系 / G1-G7 / FR1-FR8 / 里程碑 M0-M4） |
19: | 全局模块、进程与运行时边界 | `alphamill-architecture.md` | AI 控制面 + 证据与治理面 + 策略与执行面 + 数据面 + 闭环主循环 |
20: | 字段、表、数据契约（HypothesisDef / FactorDef / PortfolioDef / 评测台 / 信号缓存 / manifest） | `alphamill-architecture.md` §四 | 接口契约真源 |
21: | 因子挖掘主引擎选型（含降级阶梯） | `decisions/0001-factor-mining-engine.md` | 选型决策（证据：`
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:34:07Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md"})`


> [reasoning] All three gates pass currently. Now I need to find contracts/contradictions and gates that can pass invalid docs. Key: F003, F007, F008 specs are status=draft, so check_task_dag and [TEST] group enforcement don't apply! BACKLOG shows all three draft. Wait — validate_spec_lifecycle TEST_GROUP_STATUSES excludes draft; check_task_dag excludes draft. So the newly added DAG gate and [TEST] group gate are effectively NO-OP on the current repo because all active features are draft. That's a big finding: gates pass but don't enforce anything currently. And when status moves to ready-for-development, they'd enforce.

But also the commit messages say "fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组" — so F007 tasks has a TEST group. Yet F007 spec status is draft, so it's not enforced. Let me verify statuses.

Now let me read the F003 and F007 docs. Let me also inspect the diffs for those docs to catch contradictions. Let me read the spec/design/tasks for F007 (smaller) and F003 (larger). Let me read them.

Let me parallelize.
All three gates pass, but all active features are `draft` (BACKLOG.md:8-10) — which exempts them from the new DAG and [TEST] gates. Reading the F007/F003 docs now.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F002, F003, F004, F008]
8: topics: [evaluation, validation, evidence, experiments]
9: doc_kind: spec
10: created: 2026-09-13
11: updated: 2026-09-17
12: ---
13: 
14: # F007：统一评测台与证据门禁
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR3、FR7.1~FR7.5、M1
21: - **架构来源**：`docs/alphamill-architecture.md` §2.1、§4.0、§4.2、§4.5
22: - **上游 Contract 来源**：F002 `(dataset, DataVersion, value_digest)`；F004/Kronos 与人工因子产出的 `FactorDef`；**F003** 的 `generation.run_completed` / `generation.candidate_rejected` 事件（漏斗第一级数据源，只有 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F007
4: version: "0.2"
5: related_features: [F002, F003, F004]
6: topics: [evaluation, validation, evidence, experiments]
7: doc_kind: design
8: created: 2026-09-13
9: updated: 2026-09-17
10: ---
11: 
12: # F007：统一评测台与证据门禁 - 设计
13: 
14: > Owner: Georg | Spec: `spec.md` | Tasks: `tasks.md`
15: 
16: > **开发前置约束（2026-09-16）**：进入代码开发前，`tasks.md` 必须补齐 `[TEST]` 组——
17: > 从体验旅程派生的可执行验收（编写早、执行晚，每旅程步骤 ≥1 条断言）。
18: > 开工门禁（SDD Flow T3）会拒绝缺失该组的流转。
19: 
20: ## 0. 输入与约束
21: 
22: - **行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003
23: - **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
24: - **ADR / 上游 Contract**：ADR-0003、ADR-0005、A
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md</path>
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
9: updated: 2026-09-17
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
21: - canonical writer、留出访问、统计失败语义与 artifact 发布属于高风险路径，必须变异验证。
22: 
23: ## 1. 前置条件
24: 
25: - [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:34:13Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md"})`
- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md"})`


> [reasoning] I found a big contradiction! F007 spec frontmatter related_features: [F002, F003, F004, F008] at spec.md:7, but F007 design.md:5 related_features: [F002, F003, F004] — missing F008. Also F007 tasks.md:5 has [F002, F003, F004, F008] (correct). The check_doc_consistency F007-D003 requires F007_SPEC related_features with F003, and F007_SPEC "universe_at(T)", "F008". It does NOT check design.md's related_features or tasks.md frontmatter. So design.md missing F008 is a real inconsistency that passes the gate.

Also: check_task_dag.py parse_edges — F007 tasks §4 line 77: `T001,T002,T003 -> T004~T017` — endpoints "T004~T017" not matching `T\d{3}`, so ignored. Line 78 `T004,T005 -> T006,T011,T012,T013` expands. Line 79 `T008,T009,T010 -> T011,T016,T017` expands. Line 80 contains `T009 -> T012` and `T012 -> T013`. Line 81: `T007 -> T010/T011` expands to T007->T010, T007->T011; `T012/T014 -> T016`; line 82 `T011,T012 -> T014,T015`; line 84 `T027/T028/T029 -> T030`.

But T024 is defined in section 3, and T027/T028/T029 defined under [TEST] group. The max task id: T027,T028,T029,T030 — max is T030. T030 has incoming edges (T027/T028/T029->T030). Good. But note: tasks T018-T024 have no incoming edges from §4 at all. That's not checked. Also T025/T026 are skipped (numbering gap) — the gate doesn't check for gaps or that all tasks are covered.

Important: since F007 status = draft, check_task_dag doesn't run at all on it. So the DAG could be broken and gate passes. Let me verify statuses of F003/F007/F008 are draft -> yes. This is the big "gates that can pass invalid docs" finding: ENFORCED_STATUSES and TEST_GROUP_STATUSES exclude draft; all three active features are draft; therefore both new gates are currently no-ops. To become meaningful, at least F007/F003 must move to ready-for-development. Actually the [TEST] group requirement is designed for "before development". But the review process presumably happens at ready-for-development. Currently the feature is draft, so the newly added [TEST] group in F007 tasks isn't enforced. Reasonable finding: origin commit 65e1832 / d659db7.

Now let me read F003 docs. And diff to see what changed. Let me also inspect F008 spec for IR-002/IR-003 contracts consistency.

Let me read F003 spec/design/tasks and F008 spec. These may be large. Let me read.
Found a concrete doc contradiction already (F007 design `related_features` missing F008). Now reading F003 and F008 artifacts.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002, F007, F008]
8: topics: [factor-factory, alphagen, vendor, generators, m2]
9: doc_kind: spec
10: created: 2026-09-14
11: updated: 2026-09-14
12: ---
13: 
14: # F003：AlphaGen vendor 与可插拔生成器平面
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR2.1（假设注册）、FR2.2（可插拔生成器）、FR2.3（目标对齐）、FR2.4（纯度与能力边界）、FR2.6（探索组合）；目标 G3；里程碑 M2
21: - **架构来源**：`docs/alphamill-architecture.md` §三（`factor_factory/` 目录分工）、§4.0（闭环核心对象）、§4.1（FactorDef 契约）、§4.1.1（AlphaGen 适配契约与截面边界）、§7.1（机器边界与 GPU 槽位）
22: - **系统设计 / Research / Co
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F003
4: version: "0.2"
5: related_features: [F001, F002, F007, F008]
6: topics: [factor-factory, alphagen, vendor, generators, m2]
7: doc_kind: tasks
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F003：AlphaGen vendor 与可插拔生成器平面 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
20: - `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
21: - 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
22: - **机器边界**（架构 §7.1、`docs/SOP.md` §3）：编码、单元测试与门禁在开发机 `qiaozhi-gp`；挖掘训练与全部 GPU/产能证据在执行机 `qiaozhi-
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/spec.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F008
4: version: "0.2"
5: status: draft
6: gate_version: 1
7: related_features: [F001, F002, F003, F007]
8: topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
9: doc_kind: spec
10: created: 2026-09-14
11: updated: 2026-09-14
12: ---
13: 
14: # F008：宇宙扩容与 point-in-time 宇宙台账
15: 
16: > Owner: Georg | Target: v0.2.x
17: 
18: ## 0. 来源与意图
19: 
20: - **PRD 来源**：`docs/alphamill-prd.md` FR1.5（数据质量与扩容、point-in-time 宇宙成员关系）、FR1.1（联机采集与质量标记）、FR1.4（pair/symbol 显式映射）、FR1.7（ResearchSnapshot 的 universe 摘要）；里程碑 M2
21: - **架构来源**：`docs/alphamill-architecture.md` §三（`data_bridge/` 与 `collector/` 分工）、§4.1.1（横截面只允许在同一 timestamp 的 point
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:34:22Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md"})`
- **tool**: `bash({"command": "python3 -m pytest -q tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py 2>&1 | tail -40", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "echo \"=== F007 design fm line blame ===\"; git blame -L 1,10 -- docs/features/0.2/F007-evaluation-gates/design.md | head -12; echo \"=== who touched check_task_dag ===\"; git log --oneline --follow -- tools/check_task_dag.py; echo \"=== who touched check_doc_consistency ===\"; git log --oneline --follow -- tools/check_doc_consistency.py; echo \"=== validate_spec_lifecycle recent ===\"; git log --oneline -3 -- tools/validate_spec_lifecycle.py", "workdir": "/home/georg/projects/alpha
…[truncated])`


> [reasoning] Now I have a lot. Let me note key findings so far and then verify a few by running specific probes/tests. Need to check the F003 design.md too. And also the F003 tasks DAG vs check_task_dag. Since F003 is draft, DAG gate doesn't run. Let me manually verify F003 DAG for issues (e.g., T035 has incoming? max task id? Let me examine).

F003 tasks: task ids T001..T039 (but note T035 is in §3, and [TEST] T036-T038, T039). Let me check numbering: Phase1 T005-T012, Phase2 T013-T019, Phase3 T020-T024, Phase4 T025-T029, then §3 T030-T035, then [TEST] T036,T037,T038, T039. Wait T030-T035 in §3. Then T036-T038 [TEST], T039. But note: there's no T033? Actually T033 exists in §3? Let me recheck: T030, T031, T032, T033, T034, T035 - yes. But the read showed T030, T031, T032, T033, T034, T035, then [TEST]. Wait it showed T033 at line 78, T034 at line 79, T035 at line 80. Yes.

Max id = T039. Incoming edges to T039: line 100 `T036/T037/T038 -> T039`. Good.

Now check backwards edges: Line 99 `T030/T031/T032/T033/T034/T035 -> T036/T037/T038`. Source T030-35 < target T036-38. Fine. But T034 (verify.py quality gate) -> T036/T037/T038 means quality gate before journey acceptance. Fine.

Line 102 `T020 -> T021 -> T024 -> T029`. Fine.

Line 92 `T004 -> T017`. Fine (T004<T017).
Line 95 `T007 -> T008 -> T029`. Fine.
Line 103 `T025 -> T027 -> T029`. Fine.
Line 98 `T013 -> T016 -> T017 -> T018 -> T019 -> T032`. Fine.
Line 104 `F004 交付（...）-> T025` — the backticked segment? Let's check: line 104 `- `F004 交付（kronos-signal 服务编排）-> T025`：...`. EDGE_SEGMENT_RE finds backticked segments with ->. The segment is `F004 交付（kronos-signal 服务编排）-> T025`. Endpoints: "F004 交付（kronos-signal 服务编排）" (not T\d{3}) and "T025" → skipped entirely. Good.
Line 97 `F008.IR-002 -> T020` skipped. Good.

Now, what about [P] tasks: T006 [P]. Is T006 a destination of any edge? Line 106 `T006 [P]` description only, no edge. So fine.

But wait: T005 [P] in F007 tasks (line 34). F007 §4 line 83 says `T005 [P]` 可与 T004 并行. No edge to T005. Good. But check_task_dag: T005 is [P]; any edge with dst T005? No. Fine.

Now: the critical flaw in check_task_dag: it doesn't detect tasks with missing/incoming edges except the max one. T018-T024 in F007 have no incoming edges in §4 at all, and T025/T026 missing entirely. But not flagged. Let me confirm F007 task ids: T001-T024, then T027, T028, T029, T030. Missing T025, T026. Max is T030. So the numbering gap is not detected. Also tasks T018-T024 lack any edge from earlier tasks — so they're not integrated into the DAG, but no error. This is a gate gap: a task can be orphaned except the highest.

Actually more subtle: max id computed as string max over ids. If a task T030 appears but also a task T100... fine.

Another gap: `parse_edges` ignores any edge not enclosed in backticks. So §4 edges written as `T001 → T002` (unicode arrow) or without backticks are silently ignored. And `->` inside non-backticked text ignored.

Another gap: line 88 `zip(hops, hops[1:], strict=False)` — strict=False silently truncates. Not an issue.

Another gap: `T004~T017` range notation ignored. So `T001,T002,T003 -> T004~T017` yields left {T001,T002,T003}, right {"T004~T017"} which fails fullmatch → no edges. So a whole cluster edge is dropped.

Also line 88: `left_raw.split("/")` — but for `T001,T002,T003`, comma-separated, not split! EDGE_SEGMENT_RE for `T001,T002,T003 -> T004~T017`: hops = ["T001,T002,T003", "T004~T017"]. Then left = ["T001,T002,T003"] (split by / does nothing), right = ["T004~T017"]. Neither matches T\d{3} fullmatch → no edges. So comma-separated multi-source edges are entirely ignored! The docstrings/test only cover `/`-separated (T001/T002). F007/F003 §4 heavily use comma-separated lists: `T001,T002,T003 -> ...`, `T004,T005 -> ...`, `T008,T009,T010 -> ...`, `T009 -> T012` (this one works), `T030/T031/... -> ...` (slash works). So comma-separated edges are NOT parsed. That means many declared dependencies are invisible to the gate. This is a concrete "gate can pass invalid docs" finding.

Wait, in F003 line 99: `T030/T031/T032/T033/T034/T035 -> T036/T037/T038` uses slashes → parsed. Good. But line 95 `T007 -> T008 -> T029` parsed. Line 102 `T020 -> T021 -> T024 -> T029` parsed. Most F003 edges use single or slash. F003 line 99 slash works. But F007 line 77 `T001,T002,T003 -> T004~T017` comma → dropped; line 78 `T004,T005 -> T006,T011,T012,T013` comma → dropped! Let me verify: hops = ["T004,T005", "T006,T011,T012,T013"]. split("/") yields the whole strings. fullmatch fails → no edges. So the entire line 78 is ignored. Line 79 `T008,T009,T010 -> T011,T016,T017` comma → dropped. Line 80 slashes `T009 -> T012` and `T012 -> T013` parsed. Line 81: `T007 -> T010/T011` parsed (single left). `T012/T014 -> T016` parsed. Line 82 `T011,T012 -> T014,T015` comma → dropped. Line 83 `T005 [P]` no edge. Line 84 `T027/T028/T029 -> T030` parsed.

So in F007, the gate only sees edges: T009->T012, T012->T013, T007->T010, T007->T011, T012->T014, T014->T016, T011->T014, T011->T015, T027->T030, T028->T030, T029->T030. That's a small subset. The comma-separated dependencies (identity/isolation → CLI/publish/registry, gates → publish, etc.) are invisible. So a large fraction of declared DAG is unenforced. High severity gate gap.

Now let me also verify the F007 design related_features mismatch and whether design.md's `related_features: [F002, F003, F004]` is a genuine contradiction with spec/tasks. Yes: spec.md:7 and tasks.md:5 have F008; design.md:5 lacks F008. This is a real doc inconsistency that check_doc_consistency doesn't catch. Severity medium-high. Origin: commit 5728ccc (D003) apparently wrote F008 into spec/tasks but not design frontmatter. Let me confirm via git show --stat / blame.

Also F007 design.md:5 related_features omits F008 but design body mentions F008 heavily. So it's an oversight.

Now check F003 design.md for contradictions and the DAG. Let me read F003 design. Also check the diff of F007 docs to see what changed in commits 5728ccc, 59d28d5, 36b6564 etc.

Also check tests: test_check_doc_consistency test_f007_upstream_declaration_goes_red uses `.replace("related_features: [F002, F003, F004]", "related_features: [F002, F004]")`. Actual F007_SPEC has `[F002, F003, F004, F008]`, so the replace is a no-op → test still passes because the original already has F003. Wait: the test asserts that after replacement, the check goes red. If replace is a no-op, the file still has F003, so check returns no error → assertion FAILS. So this test is currently RED? But the user says all tests presumably pass? Let me run the test. Actually the task says audit; maybe some tests fail. Let me run pytest on the two new test files.

Let me also check test_active_feature_indexes_go_red_on_readme_drift: replaces "活跃 feature 索引（当前 F003/F007/F008）" with "活跃 feature 索引（当前 F003/F007）". Actual docs/README.md line 36 says `活跃 feature 索引（当前 F003/F007/F008）`. So that works (no-op? no, actual contains the string without parens? Let me check: line 36: `| 非 done Feature 派生索引 | \`../BACKLOG.md\` | 活跃 feature 索引（当前 F003/F007/F008） |`. Yes contains. Good.

test_active_feature_indexes_go_red_on_claude_drift replaces "F008 宇宙扩容" — actual CLAUDE.md line 53 `- F008 宇宙扩容与 point-in-time 宇宙台账`. Contains "F008 宇宙扩容". Good.

test_f007_upstream_declaration_goes_red: replace "[F002, F003, F004]" with "[F002, F004]" — actual F007_SPEC frontmatter is `[F002, F003, F004, F008]` → no match → no-op. Then check_f007_declares_f003 returns [] → assertion fails. So this test SHOULD fail. Unless... wait, does check_f007_declares_f003 also check "**F003**" in text? The spec does contain **F003** (line 22). So no error. Test fails. Let me run to confirm.

Also test_required_text_removed_goes_red for f007_declares_f008_universe: requires[0] = (F007_SPEC, "related_features: [F002, F003, F004, F008]"). Mutation removes that string → check should fail. Fine.

Let me run the tests now. Also run full pytest maybe. Let me run the specific tests.

Also need to examine check_doc_consistency's F007-D001 requires `(F007_TASKS, "T030: 回写 spec")` and forbids `- [ ] T024: 回写 spec`. Actual tasks line 73: `- [ ] T030: 回写 spec ...`. Good. But note T024 in F007 tasks is now a concurrency task (line 62), not "回写 spec". The forbid is to prevent regression.

Now, the F007-D007 check `task_graph_missing_edges_f007` requires `T009 -> T012` and `T012 -> T013` strings in tasks. These exist at line 80. But note this exact-string requirement is odd: it only locks two edges that use slash/single form. It wouldn't catch comma edges being dropped. Also, the check requires the literal `T009 -> T012` inside backticks in §4. Fine.

Now F007-D002 forbids `related_features: [F002, F004]` in F007_DESIGN. Actual design has `related_features: [F002, F003, F004]` — not the forbidden exact string. So the design frontmatter missing F008 passes.

Now let me read F003 design and check F003 DAG manually against check_task_dag. Also examine the F003 design for D005 explicit tuple fields etc. Let me read design.md.

Also I should check the commits: origin information. Let me map findings to commits:
- check_task_dag.py added in d659db7 test(f003) "新增任务 DAG/文档一致性/[TEST] 组门禁 + 变异单测".
- check_doc_consistency.py added in d659db7.
- F007 design missing F008 related_features — likely from 5728ccc D003 (declared F008 universe) which updated spec/tasks but not design frontmatter. Let me confirm with git show.
- TEST_GROUP_STATUSES added in d659db7? Actually validate_spec_lifecycle diff is part of d659db7 or 65e1832? The diff shown is a333394..HEAD combined. Let me git log per file.

Let me gather git blame for specific lines and run tests. Parallel.
Now reading F003 design and running the new regression tests plus git blame on the key lines.

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
/home/georg/miniconda3/bin/python3: No module named pytest


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== F007 design fm line blame ===
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  1) ---
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  2) kind: feature
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  3) id: F007
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  4) version: "0.2"
ccf577d4 (qiaozhi li 2026-09-17 00:26:37 +0800  5) related_features: [F002, F003, F004]
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  6) topics: [evaluation, validation, evidence, experiments]
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  7) doc_kind: design
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800  8) created: 2026-09-13
ccf577d4 (qiaozhi li 2026-09-17 00:26:37 +0800  9) updated: 2026-09-17
8d2eae0e (qiaozhi li 2026-09-13 16:55:42 +0800 10) ---
=== who touched check_task_dag ===
d659db7 test(f003): 新增任务 
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:34:40Z

- **tool**: `bash({"command": "ls .venv/bin | head; echo \"---\"; .venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py 2>&1 | tail -45", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "echo \"=== a333394 info ===\"; git log --oneline -1 a333394; echo \"=== is check_doc_consistency at a333394? ===\"; git cat-file -e a333394:tools/check_doc_consistency.py 2>&1 && echo EXISTS || echo ABSENT; echo \"=== add commit ===\"; git log --oneline --diff-filter=A -- tools/check_doc_consistency.py; echo \"=== HEAD ancestry of 9825178? ===\"; git merge-base --is-ancestor 9825178 HEAD && echo \"9825178 is ancestor of HEAD\" || echo \"not ancestor\"; git merge-base --is-ancestor 9
…[truncated])`


> [reasoning] pytest not in that python. There's a .venv. Let me use .venv/bin/python or uv. Let me check.

Also the git log --follow for check_doc_consistency shows it existed before (many fix(f007) commits) — wait, those commits are from a different branch? The a333394..HEAD log showed only 29 commits, and the earliest is a547e03. But git log --follow shows commits like 9825178, c9a1139, etc., which are not in a333394..HEAD. Hmm, "a333394..HEAD" earlier returned 29 commits starting a547e03 down to 36b6564. But git log --follow check_doc_consistency returns 9825178 etc. That's odd — maybe those commits are ancestors of a333394 (i.e., earlier F007 doc-review rounds), and a333394..HEAD re-ran F003 review. So check_doc_consistency predates a333394 and was extended with F007 checks. Let me clarify the git topology.

Actually wait: the a333394..HEAD diffstat said tools/check_doc_consistency.py | 410 ++++++++++++++ (all added). But git log --follow shows many commits. If the file was added by 9825178 which is an ancestor of a333394... let me check: `git log --oneline a333394 -1`. Let me examine. The diff a333394..HEAD shows +410 for check_doc_consistency, implying at a333394 the file didn't exist. But --follow returned commits reachable from HEAD including ones not in a333394..HEAD. Possibly a333394 is not an ancestor on the same path? Actually `git log a333394..HEAD` lists commits reachable from HEAD but not a333394. The --follow log lists commits touching the file reachable from HEAD; 9825178 etc could be ancestors of a333394 OR not reachable from a333394 but still reachable from HEAD? If they're reachable from HEAD and touch the file, but file is added in a333394..HEAD, contradiction. Unless the file was deleted and re-added. Let me check git log --oneline --diff-filter=A.

Let me just investigate git history properly. Also run tests with venv.

Let me also check .venv and run pytest.
pytest isn't on the default interpreter. Locating the venv and clarifying git topology.

  <details><summary>tool output</summary>

  ```text
Activate.ps1
activate
activate.csh
activate.fish
f2py
fastapi
git-filter-repo
hf
httpx
huggingface-cli
---
............................................F....................        [100%]
=================================== FAILURES ===================================
___________________ test_f007_upstream_declaration_goes_red ____________________

tmp_path = PosixPath('/tmp/pytest-of-georg/pytest-408/test_f007_upstream_declaration0')

    def test_f007_upstream_declaration_goes_red(tmp_path: pathlib.Path) -> None:
        target = tmp_path / cdc.F007_SPEC
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / cdc.F007_SPEC, target)
        target.write_text(
            target.read_text(encoding="utf-8").replace(
                "related_features: [F002, F0
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== a333394 info ===
a333394 docs(sdd): [TEST] 组入驻 tasks 模板 + F003/F007/F008 设计补开发前置约束（T3 开工门禁）
=== is check_doc_consistency at a333394? ===
fatal: path 'tools/check_doc_consistency.py' exists on disk, but not in 'a333394'
ABSENT
=== add commit ===
d659db7 test(f003): 新增任务 DAG/文档一致性/[TEST] 组门禁 + 变异单测（D011/D012 及各 finding 回归锁定）
=== HEAD ancestry of 9825178? ===
9825178 is ancestor of HEAD
NOT ancestor of a333394


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:34:52Z

- **tool**: `bash({"command": "echo \"=== F007 spec AC ids ===\"; grep -nE 'AC-[0-9]+' docs/features/0.2/F007-evaluation-gates/spec.md | grep -oE 'AC-[0-9]+' | sort -u; echo \"=== F007 tasks AC refs ===\"; grep -noE 'AC-[0-9]+' docs/features/0.2/F007-evaluation-gates/tasks.md | sort -t: -k2 | uniq -c -f0 | head -40; echo \"=== AC-010/011/012 in F007 tasks ===\"; grep -nE 'AC-01[012]' docs/features/0.2/F007-evaluation-gates/tasks.md; echo \"=== gate_version across features ===\"; grep -rn 'gate_version' docs/featu
…[truncated])`
- **tool**: `bash({"command": ".venv/bin/python - <<'PY'\nimport pathlib, tempfile, sys\nsys.path.insert(0, \".\")\nfrom tools import check_task_dag as dag\n\n# Probe 1: comma-separated edges (real F007 style) silently ignored\ntasks_comma = \"\"\"# t\n## 2. 实现任务\n- [ ] T001 (`FR-1`): a\n- [ ] T002 (`FR-1`): b\n- [ ] T003 (`FR-1`): c\n## 4. 依赖与并行关系\n- `T001,T002 -> T003`：逗号分隔多源\n\"\"\"\nprint(\"COMMA edges parsed:\", dag.parse_edges(tasks_comma))\nprint(\"COMMA check_tasks:\", dag.check_tasks(tasks_comma))\n\n# P
…[truncated])`
- **tool**: `bash({"command": "git log --oneline --graph --decorate -20 | head -30; echo \"=== rev-list counts ===\"; git rev-list --count a333394..HEAD; git rev-list --count HEAD; echo \"=== is a333394 ancestor of HEAD ===\"; git merge-base --is-ancestor a333394 HEAD && echo YES || echo NO; echo \"=== where is 9825178 ===\"; git branch -a --contains 9825178 2>/dev/null | head", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Interesting. So check_doc_consistency.py does not exist at a333394 but was added by d659db7. Yet git log --follow showed commits 9825178 etc. that are ancestors of HEAD and NOT ancestors of a333394. That means they are on a side branch merged? Actually if a333394 is not an ancestor of those commits... The merge-base says 9825178 is NOT ancestor of a333394, and a333394... hmm but a333394..HEAD includes 29 commits and does not include 9825178. That means 9825178 is reachable from HEAD but not from a333394, AND not in a333394..HEAD? That's impossible unless a333394 is not a simple ancestor. a333394..HEAD = commits reachable from HEAD but not a333394. If 9825178 is reachable from HEAD and not from a333394, it should appear. Unless 9825178 IS reachable from a333394 but merge-base check failed... no.

Wait, maybe the repository was history-rewritten (git-filter-repo is installed!). The `git log --oneline a333394..HEAD` output had "Incremental: 0 files updated..." noise appended — that might be from a hook. Hmm.

Actually, look: a333394..HEAD diffstat listed check_doc_consistency as +410 added. And `git log --follow` for check_doc_consistency gave commits that are ancestors of HEAD but NOT of a333394, and apparently not in a333394..HEAD. Contradiction → likely the tool output was from a cached/incremental codegraph? No, it's git.

Let me re-run `git log --oneline a333394..HEAD` and `git log --oneline -- tools/check_doc_consistency.py`. Maybe the earlier --follow output was weird because of pre-existing history before a333394 on a different lineage that got merged. Let me check `git log --oneline --graph -15`.

Actually the simplest explanation: a333394 is NOT an ancestor of HEAD. `a333394..HEAD` then = commits reachable from HEAD but not a333394, which includes commits from the other lineage. But the log showed only 29 commits a547e03..36b6564, and 9825178 not among them. Hmm.

Let me investigate. This matters for "origin" attribution. Let me run more git commands.

Actually maybe I misread: git log --follow on check_doc_consistency printed commits including 9825178, c9a1139, ... 36b6564, 59d28d5, b251826, 5728ccc, ccf577d, 65e1832, d659db7. Those "fix(f007)" commits (9825178, c9a1139, 24fdab9, 6b73c35, a0896fa, 26c7b6d) are not in the a333394..HEAD list, but 36b6564 etc ARE. So check_doc_consistency is touched both by commits in a333394..HEAD (36b6564 downward) and by older commits (9825178 etc.). The older commits could be ancestors of a333394 AND also ancestors of HEAD. But merge-base check said 9825178 NOT ancestor of a333394. Let me recheck — maybe I need to check the actual a333394 commit. The `git merge-base --is-ancestor 9825178 a333394` returned not ancestor.

But if 9825178 is ancestor of HEAD and touches check_doc_consistency, and check_doc_consistency was add'ed by d659db7 (which is in HEAD lineage), then 9825178 must come after d659db7... but 9825178 is not in a333394..HEAD. Unless a333394 is a descendant of 9825178. If 9825178 is ancestor of a333394, then merge-base would say so. It said no. So a333394 and 9825178 are on divergent lineages, both ancestors of HEAD (a merge). Then a333394..HEAD should include 9825178 unless 9825178 is an ancestor of a333394. 

I'm confused. Let me just run the commands to get the graph. This is important for origin attribution but not central. Let me do it quickly.

Also the test failure confirms finding: test_f007_upstream_declaration_goes_red is RED because the mutation string is stale. This is a concrete regression and shows the gate `check_f007_declares_f003` cannot actually detect removal of F003 while F008 is present? Let's think: the test wanted to simulate removal of F003 from related_features. But the real line is `[F002, F003, F004, F008]`, so replace target `[F002, F003, F004]` doesn't match. If F003 were actually removed, the line would become `[F002, F004, F008]` and regex `\bF003\b` would still match "**F003**" in body text? No, check_f007_declares_f003 checks related frontmatter first: `re.search(r"\bF003\b", related)` → related = "[F002, F004, F008]" → no match → error. So the check function works; only the test's mutation is stale. So severity of finding: test failure / regression in test hygiene. It means `tools/verify.py` currently FAILS (pytest step) because of this test. Let me confirm verify.py would fail. Yes pytest runs tests/unit. So the unified gate is currently red. That's a significant finding: the repo's own verification entry fails.

Wait — but maybe the venv used by verify.py is different and the test passes there? The test logic is deterministic; it will fail regardless. So `python3 tools/verify.py` (which uses `sys.executable`) would fail at pytest. Unless verify.py is run with a different python that can't import. Let me run the full verify.py? It may take long and involve secrets etc. But at least the pytest step. Actually we already know pytest fails. Let me confirm by running verify.py with venv python, or just note it. Running full verify might be slow but let's try with a timeout; it also runs ruff and integration tests. Could be heavy. Let me just run pytest for the whole tests/unit + integration quickly to see if only this one fails. Actually to save time, run verify.py with .venv/bin/python and timeout ~110s.

Let me also check `test_doc_gate_command.py` and `test_review_artifacts_gitignore.py` for relevant assertions.

Now, other findings to verify:

A) check_task_dag comma-separated edges silently ignored. Let me write a quick probe (read-only, temp dir) using the module to demonstrate. I can run python inline that imports tools.check_task_dag and calls check_tasks on a synthetic tasks text with comma edges. That's allowed (no file edits in repo; uses tmp). Let me do that.

B) ENFORCED_STATUSES excludes draft → current F003/F007/F008 all draft → gate no-op. I can demonstrate with a probe: a draft feature with broken DAG passes.

C) validate_spec_lifecycle TEST_GROUP_STATUSES excludes draft → [TEST] group not enforced on current features. Also gate_version 0 bypass.

D) check_doc_consistency check_active_feature_indexes README regex requires ≥2 features (`(?:F\d{3}\s*/\s*)+F\d{3}`). With exactly one active feature, README can't be validated and would false-error. Minor.

E) F007 design related_features missing F008 (doc contradiction) — passes gate.

F) F007 spec §4 ordering: FR-007 appears before FR-006 (lines 195 and 205); not necessarily an error.

G) F007 spec line 111 references `AC-009` for L2/L3; tasks T028 references AC-012. Wait, spec has AC-009, not AC-012! Let me check: spec AC list lines 283-291: AC-001..AC-009. But tasks T028 [TEST] references `AC-012` (line 70) and T027 references `AC-011` (line 69). And F007 spec has no AC-010/AC-011/AC-012! Let me verify: spec ACs: 001,002,003,004,005,006,007,008,009. Yes only 9. But tasks T003 references `AC-010` (line 27), T027 references `AC-011` (line 69), T028 references `AC-012` (line 70). So tasks reference nonexistent AC-010/011/012. This is a real contract inconsistency! And the gate doesn't catch it: validate_spec_lifecycle checks AC references to requirement IDs, not task→AC references. check_doc_consistency's AC_BODY_REQUIREMENTS only for F003 spec. So F007 tasks references AC-010/011/012 which don't exist in F007 spec. HIGH severity.

Wait, also F003 tasks? F003 spec has AC-001..AC-012 (12 ACs). F003 tasks references AC-001..AC-011 and AC-012? T008 references AC-012. Yes F003 AC-012 exists. So F003 is fine. But F007 tasks references AC-010, AC-011, AC-012 which don't exist in F007 spec. Let me double-check F007 spec AC list by grep.

Actually, hold on — maybe AC-010/011/012 were intended for F007 but not added. Let me grep to confirm.

H) F007 tasks T027/T028 reference AC-011/AC-012; T003 references AC-010. Also check_doc_consistency F007-D001 requires T027/T029/T030. Doesn't catch AC refs.

I) F003 tasks line 84 T036 references AC-001, AC-003, AC-004 (exist). Fine.

Let me grep F007 spec for AC-010/011/012 and check.

J) check_doc_consistency `check_f007_declares_f003` requires "**F003**" in F007 spec text — present. But doesn't check tasks/design frontmatter.

K) Snapshot binding: F003 spec DR-001 requires transition tuple fields; check_doc_consistency explicit_tuple_fields requires `"mode": "explicit_tuples"`, as_of_fidelity, universe_calendar_digest, provenance, created_at. Design has them. But the `forbids` includes `[{dataset, data_version, value_digest}]`. Fine.

L) F007 design line 5 misses F008 — found.

M) check_doc_consistency: TEXT_CHECKS substring matching. E.g., `four terminal states` check requires "四种终态" in DESIGN and "写终态 run.json" in SPEC. But the SPEC section 5 line 271 says "四种终态 completed/rejected/failed/partial". Actually it says `生成运行（四种终态 ...）`. The requires for terminal_run_facts only asks DESIGN "四种终态", DESIGN "只有 `status=completed` 的运行可被下游消费", SPEC "写终态 run.json". It doesn't pin the four enum names. A doc could list wrong states and still pass. Medium.

N) egress check forbids SPEC "生成运行在无网络出口下完成". Good.

O) The `no_lookahead_three_layers_owned` check requires F007_SPEC "owner=F006" and F007_TASKS "三层无前视状态". It doesn't require `not_yet_available` in spec (FR-007 requires it). Actually FR-007 spec includes not_yet_available. The check doesn't require it, but design does. Minor.

P) F007 spec line 181 sample tier: `<30`, `30~69`, `≈≥69`. But note `≈≥69` is odd and the boundary: `<30`, `30~69`, `≈≥69` — what about exactly 69? 30~69 inclusive and ≈≥69 inclusive overlaps at 69. Ambiguous boundary. The check only requires the three strings. This is a semantic contradiction/ambiguity in the contract. Medium. Also F007 design line 134-136 says `30~69` and `≈≥69` (overlap at 69). And PRD/ADR-0003 referenced. Worth flagging as boundary ambiguity.

Q) check_task_dag `last = max(ids)` uses string max. If task IDs are unpadded or weird (e.g., T0001), max works lexically. Not major.

R) check_task_dag `[P]` check only flags [P] as destination, not [P] with outgoing edges — maybe intentional.

S) `check_tasks` doesn't verify all task IDs are unique. If T001 appears twice, parse_task_lines returns duplicates; ids list has duplicates; no error. Could mask. Minor.

T) `check_tasks` line 122: `last = max(ids)`; if the highest-numbered task has an incoming edge, passes. But if tasks numbering has a gap and the true "last" (e.g., T030) has incoming while T024 is orphaned, passes. Orphans not flagged. Medium.

U) `check_doc_consistency`'s `check_active_feature_indexes`: `active_features` only returns features whose spec status != done, keyed by dir name. If a feature dir exists but has no spec.md, it's skipped (line 309-310) → not counted as active; BACKLOG row for it would then be "unknown"? Actually check_backlog in validate_spec_lifecycle catches missing spec via discover_features (三件套缺失). But check_doc_consistency's active set would exclude it; if BACKLOG lists it, `backlog_rows != expected` → error. Fine.

V) `check_active_feature_indexes` CLAUDE section split: `claude.split("## 当前活跃 Feature", 1)[-1]`. If the heading is renamed/removed, split returns whole doc, and CLAUDE_ACTIVE_RE matches any `- Fxxx` at line start in the entire doc → could include historical F001 etc. Then mismatch error. Fail closed. But if heading exists and lists F001 incorrectly as active? CLAUDE_ACTIVE_RE matches `^-\s+(F\d{3})\b`. It doesn't validate the status text in parentheses. So CLAUDE could say "F003 ... (done)" and still pass. Minor.

W) docs/README active index: only checks the "当前 ..." regex. If README adds a second active list elsewhere, not checked. Minor.

X) validate_spec_lifecycle gate_version check: `str(spec_fm.get("gate_version")) not in ALLOWED_GATES`; if frontmatter missing gate_version → None → str(None)="None" → error. Good.

Y) validate_spec_lifecycle line 185: `if str(spec_fm.get("gate_version")) != "1": return`. So gate_version 0 features bypass [TEST] group, AC tests path, Q/DQ, section structure. The features README says gate 0 is legacy debt and not allowed for new features. But there's no gate preventing a NEW feature from using gate_version 0! The only guard is documentation. So an author can set gate_version: 0 to bypass everything. This is a gate that can pass invalid docs. HIGH. Let me check if any current feature uses gate_version 0. Let me grep.

Z) F003 tasks T004 says "先恢复 shell 接入" etc. Not relevant.

AA) F007 design line 300/275 test paths `tests/integration/test_f007_controls_real.py` etc. Since status draft, test paths not checked. But if moved to review, these files don't exist → would fail. Not a doc contradiction per se.

AB) Snapshot binding contract: F007 spec DR-006 says calendar stored at `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`; design line 177-178 same. F003 transition tuple uses `universe_calendar_digest` combined. Consistent.

AC) F007 spec DR-001 says "calendar 摘要由本 Feature 拥有的 calendar artifact 导出" and universe from F008. check `universe_calendar_artifacts_split` requires DR-006 etc. Fine.

AD) F008 IR-002 says artifact path "湖元数据目录 路径按 digest 寻址"; F007 design says `lake/_metadata/universes/<digest>.csv`. F008 spec doesn't specify exact path `<digest>.csv`. Minor gap; the two docs could diverge. Let me check F008 design exists? F008 only has spec? Let me list features. The check_task_dag discover requires tasks.md for F008? It requires spec and tasks; if tasks missing, skipped. validate_spec_lifecycle discover_features errors if三件套 missing. But validate passed, so F008 must have design/tasks. Let me list dir.

Let me run a batch of grep/probes:
1. grep F007 spec AC list and AC-010/011/012.
2. grep gate_version across features.
3. list F008 dir.
4. probe check_task_dag comma edges and draft exemption.
5. git graph for origin.

Let me also read tools/check_doc_links.py? Not required. Focus.

Let me do parallel.
Confirmed: the repo's own test suite is RED. Now verifying several contract contradictions and gate-gap probes.

  <details><summary>tool output</summary>

  ```text
=== F007 spec AC ids ===
AC-001
AC-002
AC-003
AC-004
AC-005
AC-006
AC-007
AC-008
AC-009
=== F007 tasks AC refs ===
      1 27:AC-001
      1 34:AC-001
      1 56:AC-001
      1 60:AC-001
      1 61:AC-001
      1 62:AC-001
      1 69:AC-001
      1 40:AC-002
      1 56:AC-002
      1 59:AC-002
      1 61:AC-002
      1 70:AC-002
      1 41:AC-003
      1 51:AC-003
      1 56:AC-003
      1 60:AC-003
      1 61:AC-003
      1 62:AC-003
      1 70:AC-003
      1 36:AC-004
      1 42:AC-004
      1 57:AC-004
      1 60:AC-004
      1 61:AC-004
      1 70:AC-004
      1 43:AC-005
      1 50:AC-005
      1 57:AC-005
      1 59:AC-005
      1 61:AC-005
      1 71:AC-005
      1 25:AC-006
      1 33:AC-006
      1 57:AC-006
      1 61:AC-006
      1 49:AC-007
      1 58:AC-007
      1 60:AC-007
 
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
COMMA edges parsed: []
COMMA check_tasks: ['最高编号任务 T003 无入边（收口任务必须有前置依赖）']
RANGE edges parsed: []
RANGE check_tasks: ['最高编号任务 T003 无入边（收口任务必须有前置依赖）']
DRAFT run_checks: []
REVIEW run_checks: [('F001-demo', '§4 存在向后边（依赖后序任务）: T003 -> T001'), ('F001-demo', '最高编号任务 T003 无入边（收口任务必须有前置依赖）')]
NOBT edges parsed: []
NOBT check_tasks: ['最高编号任务 T002 无入边（收口任务必须有前置依赖）']


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
* 7fec73c (HEAD -> main) fix(f007): D013 AC-003 增多成员 cohort 批量分母与用例
* 9825178 fix(f007): D012 增并发/故障注入测试任务承接 SC-002
* c9a1139 fix(f007): D011 冻结 stage 状态与晋升/成本裁决两层术语表
* 24fdab9 fix(f007): D010 新增 DR-005 append-only 留出预算台账与越权负例
* 6b73c35 fix(f007): D009 T022 拆出执行机真实环境独立证据与集成命令
* a0896fa fix(f007): D008 补 T007->T010/T011 与 T012/T014->T016 依赖边
* 26c7b6d fix(f007): D007 补 T009->T012 与 T012->T013 依赖边
* 36b6564 fix(f007): D006 冻结样本量三级裁决（underpowered/provisional/trustworthy）
* 59d28d5 fix(f007): D005 无前视三层归属显式化并加晋级前 fail-closed 阻断
* b251826 fix(f007): D004 universe 与 calendar 拆为两个独立 artifact 引用
* 5728ccc fix(f007): D003 声明 F008 universe 上游与 universe_at(T) 摘要锚点
* ccf577d fix(f007): D002 design/tasks 补 F003 事件/算子登记表/协同池只读摄入契约
* 65e1832 fix(f007): D001 tasks 补 [TEST] 层 2 旅程验收组并重编号回写任务
* d659db7 test
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:35:17Z

- **tool**: `bash({"command": "echo \"=== origin: F007 tasks AC-010/011/012 ===\"; git blame -L 27,27 -L 69,70 -- docs/features/0.2/F007-evaluation-gates/tasks.md | sed 's/^\\(.\\{8\\}\\).*/\\1/'; git blame -L 27,27 -- docs/features/0.2/F007-evaluation-gates/tasks.md; git blame -L 69,70 -- docs/features/0.2/F007-evaluation-gates/tasks.md; echo \"=== origin: test stale mutation ===\"; git blame -L 121,131 -- tests/unit/test_check_doc_consistency.py; echo \"=== origin: design §0 contract range ===\"; git blame -L 2
…[truncated])`
- **tool**: `bash({"command": "echo \"=== tests dirs ===\"; ls tests; echo \"=== verify pytest paths ===\"; grep -n 'tests/' tools/verify.py; echo \"=== F007 refs to tests/contract|mutation ===\"; grep -rn 'tests/\\(contract\\|mutation\\)' docs/features/0.2/F007-evaluation-gates/; echo \"=== check_doc_links references ===\"; grep -n 'tests/' tools/check_doc_links.py || true; echo \"=== test_doc_gate_command ===\"; sed -n '1,200p' tests/unit/test_doc_gate_command.py", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "git diff --stat a333394..HEAD | tail -25; echo \"=== HEAD ===\"; git rev-parse --short HEAD", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Now the git topology is clear: HEAD is 7fec73c, which is 3 commits ahead of 36b6564 (7fec73c, 9825178, c9a1139). Wait the graph shows HEAD=7fec73c, then 9825178, c9a1139, 24fdab9... down to d659db7. But the earlier `git log a333394..HEAD` showed 29 commits from a547e03..36b6564 and did NOT include 7fec73c/9825178/c9a1139 etc. That's because the first command was run at a different time? No... Actually the first command output ended at 36b6564 and count 29. But now rev-list count = 36, and HEAD=7fec73c. So between my first call and now, the repo HEAD advanced! The "Incremental: 0 files updated" noise suggests some background process/codegraph is committing. Indeed HEAD changed. Interesting — the workspace may be under active automated commits. So my audit should note HEAD is moving; I'll pin to current HEAD 7fec73c.

Wait, the first `git log a333394..HEAD` showed top 36b6564 with 29 commits. Now graph top is 7fec73c. So 3 new commits appeared (7fec73c, 9825178, c9a1139). Actually c9a1139 and 9825178 were listed as touched check_doc_consistency earlier via --follow, and now they are in the graph. So yes HEAD advanced during my session.

Hmm, this is concerning for an audit. I'll note the HEAD I audited (7fec73c) and that HEAD moved during the audit.

Actually wait, re-examine: the `git log --oneline --follow -- tools/check_doc_consistency.py` output I got earlier included 9825178, c9a1139, ... so HEAD at that time already included them. And the first `git log a333394..HEAD` returned only up to 36b6564 — maybe because the command ran before the commits were made. So HEAD advanced by 3 commits during the session. Let me re-run the diffstat a333394..HEAD now to get the full set.

Now, key confirmed findings:

1. **F007 tasks references nonexistent AC-010/AC-011/AC-012** (spec has only AC-001..AC-009). Lines tasks.md:27, 69, 70. Gate doesn't catch it. HIGH. Origin: 65e1832 (D001) introduced T027/T028 with AC-011/AC-012? Let me blame those lines to get origin. Also T003 AC-010 from 24fdab9 (D010) likely.

Actually wait — maybe AC-010/011/012 are intended to be added to spec in a later commit (D013 7fec73c "AC-003 增多成员 cohort 批量分母与用例"). Let me check if spec now has AC-010+ after HEAD advanced. My read of spec was before the HEAD advanced? No, I read spec after. It has 9 ACs. Let me re-grep now to be safe. Actually the grep above (just now) shows spec AC ids = 001-009. So confirmed. But note HEAD may keep advancing. I'll report as of 7fec73c.

2. **check_task_dag ignores comma-separated edges** (probe shows parsed=[]). Confirmed. Both F007 tasks.md:77-79,82 and any comma lists are invisible. HIGH gate gap. This means check_task_dag's backwards-edge/orphan checks miss most declared deps. Also range notation `T004~T017` ignored.

3. **check_task_dag ignores non-backticked edges** (probe). Medium.

4. **draft status exempts DAG gate** — probe confirms broken DAG passes under draft. All 3 active features draft. HIGH process gap (gate is currently a no-op).

5. **validate_spec_lifecycle TEST_GROUP_STATUSES excludes draft** — same no-op on current features. Also gate_version 0 bypass not blocked for new features. Let me probe gate_version 0 quickly? It's evident from code line 185. Medium/high.

6. **test_f007_upstream_declaration_goes_red is RED** — stale mutation string. HIGH (verify.py fails). Origin: test added d659db7, but spec frontmatter changed to include F008 in 5728ccc after. Let me blame the test line.

7. **F007 design.md:5 related_features missing F008** while spec:7 & tasks:5 include F008. Contradiction, passes gate. Origin ccf577d (D002) set `[F002, F003, F004]`, then 5728ccc added F008 to spec/tasks but not design frontmatter. MEDIUM.

8. **Sample tier boundary overlap** `30~69` vs `≈≥69` at 69. Spec:181, design:134-136. Ambiguity; `≈` non-deterministic symbol in a machine-checked contract. MEDIUM.

9. **check_doc_consistency TEXT_CHECKS are substring smoke tests** — can pass self-contradictory docs. E.g., `terminal_run_facts` doesn't pin enum values. And many checks assert on one file but not cross-file. General category.

10. **README active regex requires ≥2 features** — `(?:F\d{3}\s*/\s*)+F\d{3}`. If only one active feature, README can't express it and the check false-fails (not pass-invalid, but a latent bug). LOW/MEDIUM.

11. **`check_active_feature_indexes` doesn't validate CLAUDE status text**; can list a feature with any status. LOW.

12. **check_doc_consistency F007-D007 requires only two literal edges** `T009 -> T012`, `T012 -> T013` — but those are the only slash/single edges that parse; the check doesn't assert comma edges. Related to #2.

13. **validate_spec_lifecycle AC tests path only checked for review/done** — by design; but since current statuses draft, no test path enforcement.

14. **verify.py only runs tests/unit + tests/integration**; F007 design references tests/contract, tests/mutation dirs (design:50,52, tasks T015/T017/T021) which are NOT collected by verify.py → those planned tests would never run in the gate. This is a real regression risk! F007 tasks.md:50 `tests/contract/test_f007_artifact_schemas.py`, :52 `tests/mutation/test_f007_gate_mutations.py`, :59 T021. F003 tasks:21 explicitly says all new tests must land in tests/unit or tests/integration. But F007 tasks reference tests/contract and tests/mutation, which are outside verify.py's pytest paths and neither directory exists. So F007's planned contract/mutation tests would be silently excluded. HIGH. Let me verify those directories don't exist. tests/ has integration, property, simulation, unit. No contract/mutation. Confirmed. And verify.py lines 53-54 only tests/unit tests/integration.

15. Also F007 design:232 references `tests/integration/test_f007_concurrency.py` (ok), design:275 real env `tests/integration/test_f007_controls_real.py` (ok). But design:50 `tests/contract/...`, design:52 `tests/mutation/...`. Yes.

16. F007 design line 22 lists "spec.md FR-001~FR-006" but spec also has FR-007 (line 195). Minor doc inconsistency. Actually design 0 输入与约束 says 行为契约: spec.md FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003. But spec now has DR-006 and FR-007. So design §0 is stale: missing FR-007 and DR-006. Let me verify DR list: spec has DR-001..DR-006. design says DR-001~DR-004. So design §0 line 22 is stale. MEDIUM. Also design §0 line 22 misses NFR/UX? It says IR-001~IR-003. Fine.

Wait design line 22: "**行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003". Yes missing FR-007, DR-005, DR-006. The check_doc_consistency requires FR-007 in spec but not design §0. So stale.

17. check_doc_consistency `f007_ingests_f003_contracts` requires F007_DESIGN "generation.run_completed" etc. Present.

18. F003 spec §5 lifecycle code block uses `queued -> running` etc. check forbids `status=completed` + termination=early. Fine.

19. F003 design D005 explicit tuple: check requires `"mode": "explicit_tuples"`. Design line 120 uses `{"mode": "explicit_tuples", ...}`. Good. But note spec DR-001 says `research_snapshot_id` or explicit tuple; check requires created_at and provenance. Fine.

20. Snapshot binding consistency: F003 transition tuple field is `universe_calendar_digest`; F007 DR-006 says `universe_calendar_digest` derived from two digests. Consistent.

21. Check task DAG last-task rule: F003 max task T039; edges to T039 present via slash line. But note T035 has no incoming edge from §4? Line 105 `T029 -> T035` yes T035 has incoming. T033 has incoming? line 99 T030..T035 -> T036.. includes T033 as source, not dest. T033 dest? no. T034? no. T030? line 99 source. Orphans T033, T034 not flagged. Fine, but note the rule only checks max.

22. `check_task_dag` scope says done/draft exempt. F001/F004 are done? BACKLOG only lists non-done: F003/F007/F008. F001/F002/F004 are done. Since done exempt, historical docs not checked. That's the stated design.

Now let me get origins (blame) for:
- F007 tasks AC-010/011/012 lines.
- test_f007_upstream line.
- F007 design related_features line (already ccf577d).
- F007 design §0 FR-001~FR-006 line (line 22).
- sample tier boundary lines.
- tests/contract & tests/mutation references.

Let me run git blame for these. Also re-run diffstat for current HEAD.

Also check `test_doc_gate_command.py` — it might assert the verify command includes the new gates. Let me read it. And check whether there's a test ensuring check_doc_consistency full run passes in repo (test_repo_passes_all_checks) — that passes.

Let me also confirm `tools/verify.py` currently fails by running only pytest collection? Full verify may be heavy. I'll run the pytest step directly (already did: 1 failed). That's enough to state verify.py fails at pytest.

Actually, let me run the full verify.py to be authoritative, with a generous timeout. It runs pytest integration too which may need env; could skip. Let me try with .venv/bin/python tools/verify.py and timeout 180s. Might be heavy but let's attempt. Actually integration tests may attempt DB/docker and be slow/fail. To avoid noise, I'll just run the pytest step for tests/unit (already done) and note.

Let me get blame and read test_doc_gate_command.py.
HEAD moved during the audit (now `7fec73c`). Gathering origins via blame and checking the verify test-path coverage.

  <details><summary>tool output</summary>

  ```text
=== origin: F007 tasks AC-010/011/012 ===
24fdab96
65e18325
65e18325
24fdab96 (qiaozhi li 2026-09-17 00:33:18 +0800 27) - [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账的负例） — verify: `tests/integration/test_f007_execution_tiers.py`
65e18325 (qiaozhi li 2026-09-17 00:26:05 +0800 69) - [ ] T027 [TEST] (`US-001`, `AC-001`, `AC-011`): 旅程 US-001 端到端验收——固定 fixture 连跑两次 preview：报告在排除 provenance 时间戳后稳定、canonical 台账与留出预算台账均零行、preview 越权写 official population/留出被拒并留 `evaluation.gate_rejected`、CLI 首屏含 tier/data digest/首个失败原因、近似标注在报告中显式可见 — verify: `pytest -q tests/integration/test_f007_execution_tiers.py tests/integration/test_f007_cli.py`
65e18325 (qiaozhi li 2026-09-17 00:26:05 +0800 70) - [ ] T028 [TEST] (`US-002`, `A
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== tests dirs ===
integration
property
simulation
unit
=== verify pytest paths ===
53:                "tests/unit",
54:                "tests/integration",
=== F007 refs to tests/contract|mutation ===
docs/features/0.2/F007-evaluation-gates/tasks.md:25:- [ ] T001 (`DR-001`, `IR-002`, `AC-006`): 固定 F002 dataset/version/value-digest reader 与不可变 symbol-map ref，并实现 ADR-0007 ResearchSnapshot builder/reader contract；builder 只接收显式 universe/calendar artifact，验证其内容摘要并在 provenance 保留不可变引用；preview latest 必须先冻结，canonical 只收 snapshot ID；builder 区分 `--universe`（F008 台账 digest，`universe_at(T)` 语义）与 `--calendar`（本 Feature calendar JSON）两个独立引用并分别校验；同时实现 F003 上游只读摄入契约（`generation.run_completed`/`generation.candidate_rejected`、算子能力登记表、协同池 `FactorDef`）与 F008 universe artifact 的 digest 加载及 `universe_at(T)` 语义
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
CLAUDE.md                                         |   3 +-
 docs/README.md                                    |   2 +-
 docs/alphamill-architecture.md                    |   6 +-
 docs/features/0.2/F003-alphagen-vendor/design.md  |  89 ++--
 docs/features/0.2/F003-alphagen-vendor/spec.md    |  99 +++--
 docs/features/0.2/F003-alphagen-vendor/tasks.md   |  64 +--
 docs/features/0.2/F007-evaluation-gates/design.md |  62 ++-
 docs/features/0.2/F007-evaluation-gates/spec.md   |  59 ++-
 docs/features/0.2/F007-evaluation-gates/tasks.md  |  41 +-
 tests/unit/test_check_doc_consistency.py          | 142 +++++++
 tests/unit/test_check_task_dag.py                 |  84 ++++
 tests/unit/test_validate_spec_lifecycle.py        |  36 +-
 tools/check_doc_consistency.py                    | 487 +++++++++
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:35:42Z

- **tool**: `bash({"command": "H=$(git rev-parse --short HEAD); echo \"SNAPSHOT HEAD=$H\"; echo \"=== F007 spec AC definitions ===\"; grep -nE '^\\s*-\\s*\\[[ xX]\\]\\s+\\*\\*AC-' docs/features/0.2/F007-evaluation-gates/spec.md | grep -oE 'AC-[0-9]+' | tr '\\n' ' '; echo; echo \"=== F007 design AC refs ===\"; grep -oE 'AC-0[0-9]+' docs/features/0.2/F007-evaluation-gates/design.md | sort -u | tr '\\n' ' '; echo; echo \"=== F007 tasks AC refs ===\"; grep -oE 'AC-0[0-9]+' docs/features/0.2/F007-evaluation-gates/task
…[truncated])`
- **tool**: `bash({"command": ".venv/bin/python -m pytest -q tests/unit/test_check_doc_consistency.py tests/unit/test_check_task_dag.py tests/unit/test_validate_spec_lifecycle.py 2>&1 | tail -8", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "git log --oneline -6", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] HEAD advanced again to c8b8c64. The repo is under active automated commits (probably another agent). This is important context: my audit is against a moving target. I'll pin to the commit hashes I observed and note the churn.

Now more findings:
- F007 design line 274 references `AC-011` — wait, design §8 line 274 says `| `AC-011` | contract + integration | tests/contract/test_f007_artifact_schemas.py | ...`. But spec has only AC-001..AC-009. So design also references AC-011! And tasks T015 references AC-011 too (line 50). Let me grep design for AC-010..012. Actually design line 274 is AC-011. So both design and tasks reference nonexistent AC-010/011/012. Let me grep all.

Hold on: I read design §8 earlier and it showed rows AC-001..AC-009 and "AC-001/AC-004 真实环境" and AC-009 and SC-002. But now line 274 shows `AC-011`. That means the design changed since my read (HEAD advanced, 7fec73c or c8b8c64 added AC-011 row). So docs are actively being edited. Ugh. Let me re-read current F007 spec/design/tasks quickly to get the current AC set. The spec grep just now showed AC-001..AC-009 only. But design/tasks reference AC-010/011/012. Let me re-grep both spec and design for the full AC set now.

Also test line 50 T015 references AC-011, design line 274 AC-011. So there's an ongoing edit to add AC-010..012 possibly to spec. Let me check current state.

Let me re-run greps for AC ids in F007 spec, design, tasks, and check for AC-010/011/012 definitions. Also re-check the design related_features and §0. And re-read the changed hunks.

Given the moving HEAD, I should snapshot the current commit and do a final consistent pass. Let me get HEAD hash and immediately grep. But it keeps moving every ~30s. I'll note the churn explicitly and report findings with line numbers/contents as of the latest observed read, flagging where the working tree is unstable.

Actually, the churn could be a background process running `git commit`. The user asked to audit a333394..HEAD; maybe an agent is actively fixing. I'll report what I found and note the target is moving.

Let me do a final comprehensive grep now and capture HEAD.
HEAD keeps advancing (now `c8b8c64`) — the workspace is being actively committed to. Capturing a consistent current snapshot of F007 AC references.

  <details><summary>tool output</summary>

  ```text
SNAPSHOT HEAD=c8b8c64
=== F007 spec AC definitions ===
AC-001 AC-002 AC-003 AC-004 AC-005 AC-006 AC-007 AC-008 AC-009 AC-011 
=== F007 design AC refs ===
AC-001 AC-002 AC-003 AC-004 AC-005 AC-006 AC-007 AC-008 AC-009 AC-011 
=== F007 tasks AC refs ===
AC-001 AC-002 AC-003 AC-004 AC-005 AC-006 AC-007 AC-008 AC-009 AC-010 AC-011 AC-012 
=== definitions of AC-010/011/012 anywhere in F007 ===
docs/features/0.2/F007-evaluation-gates/spec.md:292:- [ ] **AC-011** (`FR-006`, `NFR-004`): preview 的采样/缩窗在报告 `approximation` 字段显式标注（`is_approximate` 与缩减维度可核），canonical 不因性能压力静默减少门禁或样本
docs/features/0.2/F007-evaluation-gates/tasks.md:27:- [ ] T003 (`NFR-003`, `AC-001`, `AC-010`): 为 preview、canonical writer、留出 reader 与留出预算台账 writer 建立 capability 测试夹具（含 preview 越权写台账的负例） — verify: `tests/integration/test_f0
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
E        +  where set() = _check_ids([])
E        +    where [] = <function check_f007_declares_f003 at 0x7204052307d0>(PosixPath('/tmp/pytest-of-georg/pytest-409/test_f007_upstream_declaration0'))
E        +      where <function check_f007_declares_f003 at 0x7204052307d0> = cdc.check_f007_declares_f003

tests/unit/test_check_doc_consistency.py:131: AssertionError
=========================== short test summary info ============================
FAILED tests/unit/test_check_doc_consistency.py::test_f007_upstream_declaration_goes_red
1 failed, 67 passed in 0.56s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
c8b8c64 fix(f007): D014 NFR-004 近似标注落 report schema 与 AC-011
7fec73c fix(f007): D013 AC-003 增多成员 cohort 批量分母与用例
9825178 fix(f007): D012 增并发/故障注入测试任务承接 SC-002
c9a1139 fix(f007): D011 冻结 stage 状态与晋升/成本裁决两层术语表
24fdab9 fix(f007): D010 新增 DR-005 append-only 留出预算台账与越权负例
6b73c35 fix(f007): D009 T022 拆出执行机真实环境独立证据与集成命令


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:35:51Z

- **tool**: `bash({"command": ".venv/bin/python - <<'PY'\nimport pathlib, tempfile, shutil, re, sys\nsys.path.insert(0, \".\")\nfrom tools import check_task_dag as dag\nfrom tools import validate_spec_lifecycle as vsl\n\nsrc = pathlib.Path(\"docs/features/0.2\")\nfor feat in (\"F003-alphagen-vendor\", \"F007-evaluation-gates\", \"F008-universe-expansion\"):\n    root = pathlib.Path(tempfile.mkdtemp())\n    dst = root/\"docs\"/\"features\"/\"0.2\"/feat\n    dst.mkdir(parents=True)\n    for n in (\"spec.md\",\"desi
…[truncated])`
- **tool**: `bash({"command": "echo \"=== F007 spec AC-010/012 definitions? ===\"; grep -nE 'AC-01[02]' docs/features/0.2/F007-evaluation-gates/spec.md || echo \"NONE\"; echo \"=== AC sequence in F007 spec ===\"; grep -nE '^\\s*-\\s*\\[[ xX]\\]\\s+\\*\\*AC-' docs/features/0.2/F007-evaluation-gates/spec.md | sed -E 's/.*(AC-[0-9]+).*/\\1/' | tr '\\n' ' '; echo; echo \"=== design §0 line 22 (current) ===\"; sed -n '20,28p' docs/features/0.2/F007-evaluation-gates/design.md", "workdir": "/home/georg/projects/alphamil
…[truncated])`


> [reasoning] Now AC-011 is defined in spec (line 292), added by c8b8c64 (D014). But AC-010 and AC-012 are still referenced in tasks (T003, T028) with no definitions. And spec AC ids are non-contiguous: AC-001..AC-009, AC-011 — missing AC-010. The gate validates AC IDs? validate_spec_lifecycle checks duplicates and requirement refs, not continuity/gaps. So missing AC-010 and dangling AC-012 in tasks pass. HIGH/medium.

Now let me verify: does validate_spec_lifecycle detect that tasks reference AC ids not defined in spec? No. It only checks spec ACs reference requirement ids. So dangling task→AC refs are invisible. Confirmed.

Let me finalize findings and assign severity/category/origin/pattern_tag. Let me also quickly check the F007 design §0 contract range line 22 (stale, says FR-001~FR-006 DR-001~DR-004). Since D014 added AC-011 and FR-007/DR-005/DR-006 exist. Confirmed stale. Origin 8d2eae0e (original), never updated.

Also note: check_doc_consistency `AC_BODY_REQUIREMENTS` only covers F003 spec ACs (003,005,009,010,011). Not F007. So F007 AC coverage not gated. Fine.

Also: `f007_test_group_present` requires T030: 回写 spec and T027/T029; but now tasks T030 still exists. Let me confirm no drift. It passed, so yes.

Now, one more: `check_task_dag` test scope: `test_draft_feature_not_enforced`. And the docstring says done/draft exempt. So the DAG gate only applies ready-for-development/in-progress/review. All current active features are draft. So new gate currently enforces nothing. Also note F007 tasks frontmatter has no status (correct). F003 tasks related_features includes F008 etc.

Let me also check whether F003/F007/F008 tasks would pass check_task_dag if promoted to review. That's a useful regression prediction. I can run a probe by copying the feature dirs to a temp root with status changed to review and run run_checks. But discover_features reads spec status from the temp copies. Let me do that: build a temp tree with docs/features/0.2/F003..., F007..., F008... copying spec/design/tasks, and rewrite status to review. Then run check_task_dag and validate_spec_lifecycle to predict failures. This is powerful for "regression risks". Let me do it.

But careful: validate_spec_lifecycle will also check AC tests paths existence (review status) → many would fail because test files don't exist yet. That's expected (feature not implemented). But the DAG check is the interesting one. Let me run check_task_dag on temp copies with status review.

Let me write the probe.

Also run check_doc_consistency's active_features? Not needed.

Let me probe DAG-on-promotion for F003, F007, F008.
Now predicting what the new gates will do the moment any feature leaves `draft` (regression risk), by running them on review-status copies in a temp tree.

  <details><summary>tool output</summary>

  ```text
===== F003-alphagen-vendor (status=review) DAG =====

===== F007-evaluation-gates (status=review) DAG =====

===== F008-universe-expansion (status=review) DAG =====
  DAG: F008-universe-expansion -> 最高编号任务 T029 无入边（收口任务必须有前置依赖）


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== F007 spec AC-010/012 definitions? ===
NONE
=== AC sequence in F007 spec ===
AC-001 AC-002 AC-003 AC-004 AC-005 AC-006 AC-007 AC-008 AC-009 AC-011 
=== design §0 line 22 (current) ===
## 0. 输入与约束

- **行为契约**：`spec.md` FR-001~FR-006、DR-001~DR-004、TR-001~TR-003、IR-001~IR-003
- **PRD / Architecture**：PRD FR3/FR7；架构 §4.2/§4.5
- **ADR / 上游 Contract**：ADR-0003、ADR-0005、ADR-0006、ADR-0007；F002 dataset/version/value digest
- **F003 生成侧 Contract（只读摄入）**：`generation.run_completed`（仅 `status=completed` 的运行）与 `generation.candidate_rejected`（漏斗第一级）；算子能力登记表（FR-002 的方法论守卫已登记能力清单来源）；协同池 meta-factor（`generator="pool"` 的可执行 `FactorDef`）
- **F008 上游 Contract（只读摄入）**：point-in-time 宇宙台账内容寻址 artifact——按 digest 加载并提供 `universe_at(T)` 语义查询与 `schema_version`（F008 `IR-002`/`IR-003`）；F007 不实现宇宙扩容，也不解析 latest
- **实
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:36:04Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md"})`


> [reasoning] Interesting! F008 (status review) fails DAG: "最高编号任务 T029 无入边". Let me examine F008 tasks.md to confirm. This is a latent regression: F008 currently draft so gate is green; if promoted to review (the next lifecycle step before dev), check_task_dag will fail. This is a concrete "gate currently no-op, will break on promotion". Let me read F008 tasks §4.

Also F003/F007 pass DAG because their max tasks have incoming edges. But the comma-edge invisibility means their DAG is under-checked. Let me confirm F003/F007 don't have actual backwards edges hidden by commas. Let me scan F003/F007 §4 for comma edges and check ordering manually.

F007 §4 lines 77-84:
- line 77: `T001,T002,T003 -> T004~T017` (comma, ignored)
- line 78: `T004,T005 -> T006,T011,T012,T013` (comma, ignored)
- line 79: `T008,T009,T010 -> T011,T016,T017` (comma, ignored)
- line 80: slashes parsed
- line 81: parsed
- line 82: `T011,T012 -> T014,T015` (comma, ignored)
- line 83: `T005 [P]` (no edge)
- line 84: parsed

All comma edges are forward (source < dest). So no hidden backward. But the gate can't tell.

F003 §4:
- line 92-97 mostly single `T004 -> T017`, `T003 -> T013`, `T005 -> T010`, `T005 -> T013`, `T007 -> T008 -> T029`, `T009 -> T020`, `F008.IR-002 -> T020` (skipped).
- line 98 single chain.
- line 99 `T030/T031/T032/T033/T034/T035 -> T036/T037/T038`
- line 100 `T036/T037/T038 -> T039`
- line 101 `T014 -> T015`
- line 102 `T020 -> T021 -> T024 -> T029`
- line 103 `T025 -> T027 -> T029`
- line 104 F004 -> T025 skipped
- line 105 `T029 -> T035`
- line 106 T006 [P]

All forward. Good.

Now F008 tasks. Let me read §4 and count. Also note: F008 is now in scope if status changes. This is a strong finding.

Also, I realize the check_task_dag gate's "max task must have incoming edge" is itself a weak heuristic and produces this false-ish positive. But per the gate's rules, F008's doc is invalid. Let me confirm F008 §4.

Let me read F008 tasks.md.
F008 already violates the DAG gate the moment it leaves `draft`. Reading its tasks to confirm.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md</path>
<type>file</type>
<content>
1: ---
2: kind: feature
3: id: F008
4: version: "0.2"
5: related_features: [F001, F002, F003, F007]
6: topics: [data-bridge, universe, backfill, data-quality, point-in-time, m2]
7: doc_kind: tasks
8: created: 2026-09-14
9: updated: 2026-09-14
10: ---
11: 
12: # F008：宇宙扩容与 point-in-time 宇宙台账 - 任务
13: 
14: > Owner: Georg | Spec: `spec.md` | Design: `design.md`
15: 
16: ## 0. 来源与执行规则
17: 
18: - 行为与验收真相源：`spec.md`；技术方案与边界：`design.md`。
19: - 每项任务完成并跑过对应 verify 后立即勾选，不得最后统一补勾。
20: - `[P]` 只用于修改不同文件、无顺序依赖且不争用同一状态的任务。
21: - 全部新测试必须落在 `tests/unit` 或 `tests/integration`——`tools/verify.py` 只收集这两个目录。
22: - **机器边界**（架构 §7.1、`docs/SOP.md` §3）：回填、质量门、导出、备份在执行机 `qiaozhi-lt` 执行并记 hostn
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:36:11Z

- **tool**: `bash({"command": "echo \"=== repo refs to _metadata/universes ===\"; grep -rn '_metadata/universes' docs/ src/ tools/ 2>/dev/null; echo \"=== F008 design universe_at / artifact path ===\"; grep -nE 'universe_at|_metadata|\\.csv|digest|canonical' docs/features/0.2/F008-universe-expansion/design.md | head -40; echo \"=== F003 refs to universes path ===\"; grep -rn 'universes/' docs/features/0.2/F003-alphagen-vendor/", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "echo \"=== F008 tasks T029 blame ===\"; git blame -L 69,70 -- docs/features/0.2/F008-universe-expansion/tasks.md; echo \"=== F008 status ===\"; grep -n 'status:' docs/features/0.2/F008-universe-expansion/spec.md; echo \"=== F003 spec AC-012 exists? ===\"; grep -n 'AC-012' docs/features/0.2/F003-alphagen-vendor/spec.md", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] F008 tasks §4 edges: T001->T019, T002->T020, T005->T013, T006->T007->T008->T009, T011->T013, T012->T013, T015->T017->T022, T020->T022, T021->T022, T022->T023. Max task id is T029. Edges into T029? None. So gate flags "最高编号任务 T029 无入边". Note T027/T028/T029 are the final writeback/verify tasks and have no declared prerequisites. So F008's tasks violate the gate's rule. Currently draft → exempt → gate green. On promotion to ready-for-development, gate goes red. This is a real latent regression. Origin: F008 tasks created 8d2eae0e? Actually F008 tasks likely from an earlier commit. Let me blame line 70. But not essential.

Also note: F008 tasks line 70 T029 is a writeback task with no deps; the gate requires an incoming edge. F008 will fail on promotion. HIGH regression risk.

Also F008 line 68 T027 has no AC refs (fine, not required by gates).

Also F008 `[P]` T003: is T003 a destination? no. Good.

Now also note F007 tasks: max T030 has incoming from T027/T028/T029 (slash parsed). Good. F007 §4 comma edges ignored but no backwards.

Now, another gate gap: check_task_dag doesn't require every task to have an incoming edge except max. So T027/T028/T029 in F008 could be orphans but only T029 (max) triggers. If they'd numbered T029 as something else, might pass. Fine.

Let me also verify validate_spec_lifecycle on promotion for F007 (will fail on AC tests paths? tests referenced don't exist). Actually spec ACs have `tests: ` paths? Let me check F007 spec AC lines: they don't have `tests:` paths (e.g., AC-001 line 283 has no tests: path). So at review, validate_spec_lifecycle requires tests path for each AC → all ACs missing tests → errors. So F007 can't be promoted to review without adding tests paths. That's expected gate behavior, not a bug. But worth noting as a lifecycle gate that will block promotion. Actually the spec AC list lines 283-292 have no `tests:` clauses. So promotion to review fails. That's intended (test paths required at review).

Hmm, but the "review" status in this repo seems to be the design review status, not code-done. The features are at "draft" during doc review. The lifecycle model: draft → ready-for-development → in-progress → review → done. "review" is near code completion. So requiring tests paths at review is intended. But doc review happens at draft. OK.

However, the key point: the DAG gate and [TEST] group gate only apply from ready-for-development onward, yet F003/F007 have already been through multiple doc-review rounds while draft. So the doc-review gates (check_doc_consistency) operate on draft, but the DAG gate doesn't. That means doc-review-round fixes (D007/D008 edges) were not validated by check_task_dag. Indeed the DAG test only tests synthetic. So the F007 §4 edge fixes (26c7b6d, a0896fa) were validated only by the literal-substring check_doc_consistency F007-D007 (two edges). That's a weak gate. Good finding.

Now let me also check whether `check_doc_consistency` requires F007 design related_features? No. And the stale test. Good.

Let me now also verify a potential "gate can pass invalid docs": check_doc_consistency `terminal_run_facts` requires SPEC "写终态 run.json" — this substring exists in spec. Fine.

One more: `check_doc_consistency` `tier_ladder_matches_adr0001` forbids SPEC "降级到 L1/L2" and "四条判据". Current spec has "降级到 L1" (line 273) which does not contain "降级到 L1/L2". Fine.

Another: `explicit_tuple_fields_match_adr0007` requires DESIGN `"mode": "explicit_tuples"`. Design uses that. Good. And requires `created_at` — design has provenance {created_at,...}. Good.

Now `pit_mask_depends_on_f008` requires DESIGN "universe_at(T)" and SPEC "universe_at(T)". Good.

`ir003_schema_version_has_carrier` requires DESIGN "**GenerationRun**：`schema_version`" — design line 114 uses `**GenerationRun**：`schema_version``? Let me check: line 114 "**GenerationRun**：`schema_version` / `run_id`..." yes. Good.

Now let me look for contradictions in snapshot binding specifically (user emphasized). 
- F003 spec DR-001 transition tuple: fields `schema_version`, `cutoff_time`, members with as_of_fidelity/event_time_min/max, symbol_map_digest, universe_calendar_digest, provenance. 
- F003 design line 120 same.
- F007 spec DR-006: universe artifact path `lake/_metadata/universes/<digest>.csv`; calendar path `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`; universe_calendar_digest 由两者 digest 组合导出.
- F007 design line 177-178 matches.
- F008 spec IR-002: artifact published to lake metadata dir, path by digest, canonical format, universe_at(T). F008 does NOT specify `.csv` extension or exact `lake/_metadata/universes/` path. F003 design line 55/82 references F008 `universe_at(T)`. F007 design pins `lake/_metadata/universes/<digest>.csv`. So F008 (the owner) doesn't pin the path/format that F007 assumes. Potential contract gap: F007 assumes `.csv` + directory; F008 only says "固定 canonical 格式（列序、排序、UTF-8、LF）...湖元数据目录". A consumer following F007 path would need F008 to produce exactly that. This is a cross-feature contract mismatch (owner F008 doesn't declare the path/extension its consumer F007 depends on). MEDIUM.

Let me verify F008 design maybe declares path. F008 has design.md. Let me grep it for `lake/_metadata/universes`.

Let me also grep the whole repo for `_metadata/universes`.

Also check F008 design for `universe_at(T)`.

Let me run.
Checking the cross-feature universe artifact path contract (F007 assumes a path F008 must produce).

  <details><summary>tool output</summary>

  ```text
=== repo refs to _metadata/universes ===
docs/features/0.2/F007-evaluation-gates/spec.md:221:- **DR-006**：`UniverseCalendarBinding` 应当把 universe 与 calendar 拆为两个独立 artifact 引用：universe 按 **F008** `IR-002` 的内容寻址台账消费（`lake/_metadata/universes/<digest>.csv`，提供 `universe_at(T)` 语义），calendar 由本 Feature 拥有并规范化保存为内容寻址 JSON（`reports/research_snapshots/_inputs/universe_calendars/<digest>.json`）；ADR-0007 的 `universe_calendar_digest` 由两者 digest 组合导出（不再等于单一 JSON 文件摘要），拆解关系写入 ResearchSnapshot provenance。
docs/features/0.2/F007-evaluation-gates/design.md:179:CLI 仅解析参数和序列化结果；preview 的 `--latest` 模式要求显式 symbol-map digest、**F008** universe artifact 引用（`--universe`）与 calendar 输入（`--calendar`）两个独立参数。universe 按 F008 `IR-002` 从 `lake/_metadata/universes/<digest>.csv` 加载并走 `universe_at(T)` 语义，**不复制进 reports**；ca
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
=== F008 tasks T029 blame ===
bd87eac0 (qiaozhi 2026-09-14 20:31:35 +0800 69) - [ ] T028 (`AC-001`, `AC-011`): 运行项目统一质量门 — verify: `python3 tools/verify.py`
bd87eac0 (qiaozhi 2026-09-14 20:31:35 +0800 70) - [ ] T029: 回写 spec 验收证据、勾选验收清单、更新 `BACKLOG.md` 状态与 spec frontmatter — verify: `python3 tools/validate_spec_lifecycle.py`
=== F008 status ===
5:status: draft
=== F003 spec AC-012 exists? ===
315:- [ ] **AC-012** (`IR-003`): `GenerationRun` manifest 与 FactorDef JSON 均持久化 `schema_version`；`show` 遇到未知 `schema_version` 以非零退出拒绝，不做兼容性猜测 — tests: `tests/unit/test_f003_cli_contract.py`


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:36:35Z

- **tool**: `bash({"command": "grep -nE 'universe_calendar_digest|as_of_fidelity|event_time|schema_version|cutoff|ResearchSnapshot|symbol_map_digest' docs/decisions/0007-research-snapshot-binding.md | head -40", "workdir": "/home/georg/projects/alphamill"})`
- **tool**: `bash({"command": "grep -rnE 'universe_calendar_digest' docs/features/0.2/F003-alphagen-vendor/ docs/features/0.2/F007-evaluation-gates/ | head -30", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] Good, F008 design does declare the exact `lake/_metadata/universes/<digest>.csv` path and format. So my cross-feature path gap is NOT valid — F008 design declares it. Drop that finding.

Now let me finalize. Let me also verify whether `check_doc_consistency` `requires` for `universe_calendar_artifacts_split` uses F007_DESIGN "lake/_metadata/universes/" (yes line 207). Good.

Now let me consider snapshot binding contract consistency more:
- F003 design line 120: explicit tuple includes `universe_calendar_digest` as a single combined digest.
- F007 DR-006: `universe_calendar_digest` combined from two digests. Consistent.
- ADR-0007 is the truth source. Let me quickly check ADR-0007 for the field name. If ADR-0007 says `universe_calendar_digest` = single JSON file digest (as F007 DR-006 says "不再等于单一 JSON 文件摘要"), F003 carries the new combined semantics. Let me grep ADR-0007 for universe_calendar_digest to check consistency. This is the "snapshot binding" focus.

Let me read ADR-0007 relevant lines.

Also check F003 design vs ADR-0007 for as_of_fidelity/event_time_min/max.

Let me grep.
Verifying snapshot-binding field semantics against ADR-0007 (the declared truth source).

  <details><summary>tool output</summary>

  ```text
27:2. **新增不可变 `ResearchSnapshot`**：它是对多个有效 DatasetVersion 的内容寻址引用集合，
31:   ResearchSnapshot = {
32:     schema_version,
34:     cutoff_time,
36:       <dataset>: {data_version, value_digest, as_of_fidelity,
37:                   event_time_min, event_time_max}
39:     symbol_map_digest,
40:     universe_calendar_digest,
47:3. **身份只哈希语义字段**：`snapshot_id` 由 `schema_version`、`cutoff_time`、按 dataset 名排序的
48:   `(dataset, data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)`、
49:   `symbol_map_digest` 与 `universe_calendar_digest` 导出。创建时间、路径、codec、文件 SHA 和主机
53:   ResearchSnapshot。已发布对象不原地修改；成员或 cutoff 改变生成新 ID。
56:   校验并发布一个 ResearchSnapshot，再开始计算；报告必须显示实际 snapshot ID。
59:   数据时，通过 ResearchSnapshot 反查 `(dataset, data_version, value_digest)`，不复制第二份成员
66:- `experiment_store
…[truncated]
  ```
  </details>

  <details><summary>tool output</summary>

  ```text
docs/features/0.2/F003-alphagen-vendor/spec.md:112:- ResearchSnapshot 的实现（归 `experiment_store/`，随 `F007` 落地）——F003 只消费绑定，冒烟期用显式元组过渡（Q-002）；过渡元组须携带与 ADR-0007 对齐的语义字段（`schema_version`、`cutoff_time`、逐 dataset `as_of_fidelity`/`event_time_min`/`event_time_max`、`symbol_map_digest`、`universe_calendar_digest` 与不可变 artifact 的 provenance 引用），仅不落 snapshot artifact；F007 落地时须先发布 `ResearchSnapshot` 再替换为 `snapshot_id`（ADR-0007 决策 4/5）；
docs/features/0.2/F003-alphagen-vendor/spec.md:244:- **DR-001**：`GenerationRun` 应当持久化快照绑定（`research_snapshot_id`，或过渡期的显式元组：`schema_version`、`cutoff_time`、逐 dataset 成员映射 `{<dataset>: (data_version, value_digest, as_of_fidelity, event_time_min, event_time_max)}`、`symbol_map_digest`、`universe_calendar_digest` 与不可变 artifact 的 `provenance` 引用——字段与身份语义与 ADR-0007 一致）、seed、生成器与引擎
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:36:48Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md"})`


> [reasoning] Let me read ADR-0007 lines 25-80 fully to check the universe_calendar_digest semantics and whether F007/F003 contradict it.

Key: ADR-0007 line 40 lists `universe_calendar_digest` as a top-level field. Line 74 says calendar artifact path. Does ADR-0007 define universe_calendar_digest as combined digest or single? F007 DR-006 says "不再等于单一 JSON 文件摘要" implying ADR-0007 originally had it as a single digest. Let me read ADR-0007.

Also F003 design line 120 explicit tuple has `universe_calendar_digest` plus provenance `universe_calendar_path` (singular). But now universe and calendar are split; F003 still has a singular `universe_calendar_path` in provenance. Is that a contradiction? F003 is the transition tuple; F007 DR-006 splits universe and calendar into two artifacts. F003's tuple has one `universe_calendar_digest` (combined) and provenance with `universe_calendar_path` singular. Given the split, provenance should ideally carry two paths. But F003 design line 120 says `provenance: {created_at, artifact_path, member_manifest_paths, symbol_map_path, universe_calendar_path}` — only one path. So when F003 consumes F008 universe artifact and F007 calendar, it can't record both. This is a potential inconsistency between F003 transition tuple and F007 DR-006 split. Let me check whether F003 mentions two separate paths anywhere. F003 design line 82 (boundary) mentions F008 universe digest written into run.json; spec line 328 mentions universe digest. No separate calendar path. So F003's transition tuple lumps universe+calendar into one digest+path, while F007 splits. Since F003 claims "字段与 ADR-0007 的成员/身份契约一一对应" and F007 changes the semantics of universe_calendar_digest to a combined digest, F003's single `universe_calendar_path` provenance cannot recover both. MEDIUM finding (snapshot binding contract drift).

Let me read ADR-0007 to confirm whether it already specifies two paths.
Reading ADR-0007 to settle the universe/calendar digest semantics.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md</path>
<type>file</type>
<content>
1: # ADR-0007：研究快照绑定 —— 独立 DatasetVersion 的不可变组合
2: 
3: - 日期：2026-09-13
4: - 状态：Accepted
5: - 决策人：Georg
6: - 背景：PRD FR1/FR7；F002 dataset 独立版本；F007 多数据集评测与实验身份；ADR-0006
7: 
8: ## 背景
9: 
10: F002 已决定 `data_version` 按 dataset 独立递增，因为 OHLCV、funding、basis、OI 与 signals
11: 具有不同采集节奏和失败域。这个决定对数据桥是正确的，但不能直接充当多数据集实验身份：
12: 若 F007 在运行时分别解析各 dataset 的 “latest valid”，相同命令在不同时间会绑定到不同版本，
13: 还可能把不同 source snapshot、不同覆盖范围的数据临时拼成一个不可复现的输入。
14: 
15: 用各 manifest 的 `exported_at` 临时聚合也不足以解决问题。`exported_at` 是写出 provenance，
16: 不是跨 dataset 的一致性边界；它既不固定 point-in-time universe/symbol map，也不证明各成员满足
17: 同一个信息截止时刻和评测窗口。另一方面，把所有 dataset 强绑成一个全湖版本会让单个低频
18: dataset 的延迟或失败阻塞全湖发布，反转 F002 已确立的独立失败域。
19:
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:36:56Z

- **tool**: `bash({"command": "grep -nE 'universe_calendar|ResearchSnapshot|universe_at|_metadata/universes|snapshot_id' docs/alphamill-architecture.md | head -40; echo \"=== ADR-0007 touched in a333394..HEAD? ===\"; git log --oneline a333394..HEAD -- docs/decisions/0007-research-snapshot-binding.md; echo \"=== architecture diff a333394..HEAD ===\"; git diff a333394..HEAD -- docs/alphamill-architecture.md | head -60", "workdir": "/home/georg/projects/alphamill"})`


> [reasoning] ADR-0007 line 72-75: symbol-map at `lake/_metadata/symbol_maps/<digest>.csv`; universe/calendar JSON provided by caller, `experiment_store` normalizes and saves at `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`; provenance references "这两个不可变 artifact". ADR-0007 explicitly says provenance references the two artifacts (symbol-map and universe/calendar combined). It says "universe/calendar artifact" as a single JSON provided by caller. F007 DR-006 now splits universe (from F008's `lake/_metadata/universes/<digest>.csv`) from calendar (F007's JSON). This is an evolution of ADR-0007 but ADR-0007 itself still says universe/calendar is a single caller-provided JSON at `universe_calendars/<digest>.json`.

Contradiction chain:
- ADR-0007 line 72-75: universe/calendar is a single caller-provided JSON artifact saved under `universe_calendars/<digest>.json`; provenance references symbol-map + that one JSON.
- F007 DR-006 (spec:221, design:179): universe is F008's CSV at `lake/_metadata/universes/<digest>.csv`, calendar is F007 JSON at `universe_calendars/<digest>.json`; `universe_calendar_digest` is combined from two digests; provenance records the split.
- F007 design line 40 in ADR-0007 lists provenance as `universe_calendar_path` (singular), and ResearchSnapshot schema top-level `universe_calendar_digest`. F007 does not update ADR-0007. So ADR-0007 (declared truth source) contradicts the F007 spec/design on universe artifact ownership/location/format. Also F008 spec owns the universe artifact at the lake path. So there are three documents with partially divergent universe/calendar contracts, and no gate checks ADR/architecture consistency (validate only checks feature docs structure and cross-feature text substrings).

This is a solid MEDIUM-HIGH finding under "snapshot binding / schema version". The docs/README ownership matrix says architecture §四 owns field/contract truth; but ADR-0007 owns snapshot binding. F007 modifies the semantics without updating ADR-0007. Contradiction.

Also F003 transition tuple provenance has `universe_calendar_path` singular (design:120), consistent with ADR-0007 but inconsistent with F007's split (which needs two artifact refs). F003 claims alignment with ADR-0007 field-by-field. Since F007 changes ADR-0007 semantics without updating it, F003's transition tuple may carry the wrong (single) provenance shape. MEDIUM.

Also the gate `check_doc_consistency.universe_calendar_artifacts_split` (F007-D004) requires F007_DESIGN `lake/_metadata/universes/`, `--calendar <path>`, `--universe <digest|ref>` and forbids `--universe-calendar`; it does NOT check ADR-0007. So the split can be "correct" inside F007 while contradicting ADR-0007. That's a gate that passes an invalid (globally inconsistent) doc.

Now, also check architecture doc §4.4/§4.5 for universe_calendar_digest. Let me grep architecture for it. The a333394..HEAD diff touched architecture.md +6-? Let me grep.

Let me also check F003 spec's related_features includes F007/F008 and F007 spec includes F008. F008 spec related_features [F001,F002,F003,F007]. F003 design/tasks related_features [F001,F002,F007,F008]. F007 design missing F008. Already found.

Let me grep architecture for ResearchSnapshot / universe_calendar_digest to see if there's a third contradiction.
Checking the architecture doc (declared contract truth source) for the same snapshot fields.

  <details><summary>tool output</summary>

  ```text
221:    │   ├── research_snapshot.py #   ADR-0007：dataset versions/digests + cutoff/映射/日历 → snapshot_id
240:ResearchSnapshot + HypothesisDef → FactorDef → factor ExperimentRun
301:  "research_snapshot_id": "snapshot_sha256:...",
314:  "cost_model_version": "cm-v1",   # 与 research_snapshot_id 并列进入 FR7 manifest
336:毛收益或等效摘要重定价，不重新运行生成器；`cost_model_version` 与 `research_snapshot_id` 并列进入
343:  （`reports/bench/<object_id>/<research_snapshot_id>/<experiment_id>/curves.parquet`，报告根 `reports/`
347:  `research_snapshot_id`、`cost_model_version` 并列，保证曲线可从真相源确定性重放；
380:路径：signal_cache/<portfolio_or_factor_id>/<research_snapshot_id>/<code_version+params_hash>/<pair>/<YYYY-MM-DD>.feather
387:1. **缓存键带版本维度**：缓存键 = (portfolio_or_factor_id, research_snapshot_id, code_version,
413:多数据集研究都必须先按 ADR-0007 冻结 Re
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:37:07Z

- **tool**: `read({"filePath": "/home/georg/projects/alphamill/docs/alphamill-architecture.md", "offset": 408, "limit": 62})`


> [reasoning] Architecture §4.4.1 line 428 has `universe_calendar_digest` and line 437 saves `universe_calendars/<digest>.json` — same as ADR-0007. Let me read architecture lines 416-440 to see the ResearchSnapshot contract. It likely still treats universe/calendar as one JSON. F007 splits universe to F008. So architecture also contradicts F007.

Let me read architecture 413-440.

Also note architecture line 240 says `ResearchSnapshot + HypothesisDef → FactorDef → factor ExperimentRun` but architecture was only changed for pool generator. So no update for split.

Let me read that section.

  <details><summary>tool output</summary>

  ```text
<path>/home/georg/projects/alphamill/docs/alphamill-architecture.md</path>
<type>file</type>
<content>
408: 
409: DatasetVersion 按 dataset 独立演进，稳定引用是 `(dataset, data_version, value_digest)`；
410: `value_digest` 是由 dataset 投影 schema 与按逻辑键排序的分区 `(rows, time bounds, row_digest)`
411: 计算的语义根摘要，不包含物理路径、codec、文件 SHA 或导出时间；具体规范以 F002 design §3 为准。
412: `exported_at` 只描述写出 provenance。单 dataset reader 可以为探索解析 latest valid，但任何正式
413: 多数据集研究都必须先按 ADR-0007 冻结 ResearchSnapshot，不能把多个 latest 或 exported_at
414: 临时聚合当作可复现实验输入。
415: 
416: #### 4.4.1 ResearchSnapshot
417: 
418: ```json
419: {
420:   "schema_version": 1,
421:   "snapshot_id": "snapshot_sha256:...",
422:   "cutoff_time": "2026-09-06T00:00:00Z",
423:   "members": {
424:     "ohlcv_1m": {"data_version": "v2026.09.06", "value_digest": "sha256:...
…[truncated]
  ```
  </details>

## assistant · 2026-09-16T16:37:12Z

- **tool**: `bash({"command": "echo \"HEAD=$(git rev-parse --short HEAD)\"; echo \"--- standalone gates ---\"; .venv/bin/python tools/check_task_dag.py >/dev/null 2>&1 && echo \"check_task_dag: PASS\" || echo \"check_task_dag: FAIL\"; .venv/bin/python tools/check_doc_consistency.py >/dev/null 2>&1 && echo \"check_doc_consistency: PASS\" || echo \"check_doc_consistency: FAIL\"; .venv/bin/python tools/validate_spec_lifecycle.py >/dev/null 2>&1 && echo \"validate_spec_lifecycle: PASS\" || echo \"validate_spec_lifecy
…[truncated])`


> [reasoning] Confirmed: architecture §4.4.1 lines 436-438 says "显式 universe/calendar JSON 由构造器规范化后保存于 `reports/research_snapshots/_inputs/universe_calendars/<digest>.json`" — treats universe AND calendar as one JSON. F007 DR-006 splits: universe from F008 CSV artifact at `lake/_metadata/universes/<digest>.csv`; calendar JSON at `universe_calendars/<digest>.json`. So F007 spec/design contradicts both ADR-0007 (lines 72-75) and architecture §4.4.1 (436-438). No gate catches it (check_doc_consistency only checks F007 internal). This is a strong MEDIUM-HIGH finding under snapshot binding/contracts.

Also the ownership matrix in docs/README says architecture §四 owns "字段、表、数据契约（...ResearchSnapshot...）". So per the project's own ownership rule, F007 changing ResearchSnapshot contract must update architecture. It didn't (architecture diff only pool generator). So this is a process/contradiction finding.

Now let me also double check F003's transition tuple provenance: ADR-0007 provenance has `universe_calendar_path` singular; F003 design:120 matches ADR. F007's split would require two paths. So F003 is consistent with ADR but F007 diverges. F003 spec says "字段与身份语义与 ADR-0007 一致". So F003 and F007 are mutually inconsistent on the number of artifact refs for universe vs calendar. Concretely: F003 transition tuple carries one `universe_calendar_digest` + single path; F007 requires the digest to be a combination of two artifacts and provenance to record the split. F003 does mention universe digest separately in boundary conditions (design:82, spec:328) but not the calendar path. So there is drift.

Now let me compile severity. I'll use a schema:
- severity: [Blocker|High|Medium|Low]
- category: [GateGap|DocContradiction|TestRegression|LifecycleScope|ContractMismatch|SchemaVersion]
- origin: commit hash + intent
- pattern_tag: e.g. `dag-comma-edge-unparsed`, `gate-scope-draft-noop`, `stale-mutation-test`, `frontmatter-drift`, `cross-doc-contract-drift`, `ac-id-dangling`, `substring-only-gate`, etc.

I should also assign severity for the current RED test: `verify.py` fails → High/Blocker for CI. Since the user asked for gates that can pass invalid docs and contradictions, the red test is important because the "all-green" claim is false. Let me note that running `tools/check_doc_consistency.py` alone passes (0), but the test suite fails. So the actual unified gate `verify.py` is red.

Let me verify whether `verify.py` fails at pytest by running it? It also runs ruff. Running full may take long, but let's do a quick targeted: `.venv/bin/python -m pytest -q tests/unit tests/integration` maybe heavy. We already know tests/unit has 1 failure. Since verify.py includes tests/unit, it will fail. Sufficient.

Now let me also check `tools/check_doc_links.py` since verify runs it — not needed.

Let me also verify the "active feature index" gate currently passes and note the README regex single-feature bug with a probe. Quick probe: construct a temp tree with one active feature and README "当前 F001"? The regex `当前\s*((?:F\d{3}\s*/\s*)+F\d{3})` requires slash. If README says "当前 F001", readme_ids=set() while expected_ids={F001} → error. So it's fail-closed (false negative on valid doc), not pass-invalid. I'll report as Low latent bug. Actually could it pass invalid? If expected has 0 active features and README regex no-match, both empty → pass. Fine. If there is exactly 1 active and README omits it entirely, regex may find some other "当前 Fxxx / Fyyy" elsewhere? Unlikely. So it's a false-failure risk, Low.

Also CLAUDE_ACTIVE_RE only matches `- Fxxx` lines; if CLAUDE lists active features in a table, claude_ids=empty → error (false failure). Low.

Now let me also check the DAG test file: it doesn't test comma edges or draft-in-other-statuses beyond draft; mutation coverage gap. The user asked "tests" audit and "regression risks". The test suite for check_task_dag lacks a test for comma-separated edges, which is the format used by F007. This is a test-coverage gap → HIGH because the production docs use a format the gate silently ignores and no test catches it.

Also test_check_doc_consistency: mutation tests only mutate `chk.requires[0]`, and only `chk.forbids[0]`. So later requires/forbids not independently verified. E.g., `f007_declares_f008_universe` has 5 requires; only requires[0] is mutated. So the other four (F007_SPEC "universe_at(T)", "F008", F007_DESIGN "F008 上游 Contract", F007_TASKS "universe_at(T)") aren't mutation-tested. Medium test-coverage gap.

Also `test_unknown_check_id_absent_from_registry` is a tautology (compares a set to itself) — it doesn't test anything. Low.

Now let me also note: `check_doc_consistency` run_checks reads all target docs; if a target file is missing, `read` raises FileNotFoundError → uncaught → tool crashes with traceback rather than clean non-zero error. The test `_materialize` comment acknowledges this. In verify.py, if a doc is deleted/renamed, check_doc_consistency raises instead of reporting a structured violation. Medium robustness.

Also `check_f007_declares_f003` reads F007_SPEC only; if missing → crash.

Also `check_ac_body_covers_clauses` only checks F003 ACs 003/005/009/010/011; no coverage for other ACs. Fine.

Now let me consider "schema/version" specifically:
- F003 IR-003/AC-012: `GenerationRun` manifest & FactorDef JSON carry `schema_version`; `show` rejects unknown. check `ir003_schema_version_has_carrier` requires DESIGN "**GenerationRun**：`schema_version`", SPEC AC-012, SPEC IR-003, TASKS schema_version. Good.
- F007 IR-003: versioned schema. F007 DR? design says schema_version.
- F008 IR-003: schema_version.
- Gate gap: validate_spec_lifecycle doesn't verify that IR-003-like schema_version requirements have AC carriers; only check_doc_consistency's F003-specific check. F007/F008 schema_version carriers aren't gated. Medium.

Also: F007 spec AC set missing AC-010 but tasks references it; and spec jumps 009→011. `validate_spec_lifecycle` doesn't check AC numbering continuity. So a spec can have AC-011 with no AC-010 and tasks can reference AC-012 that doesn't exist → passes. High-ish gate gap (dangling AC refs).

Also check_doc_consistency's AC_LINE_RE requires format `- [ ] **AC-NNN** (...)`; F007 spec line 292 AC-011 defined. Fine.

Now let me think about "lifecycle status" as a theme:
- `validate_spec_lifecycle`: status is only in spec frontmatter; design/tasks must not declare status. It checks `if fm and "status" in fm`. If design/tasks has a `status:` inside a code block or in body, parse_frontmatter only reads leading frontmatter, so a body `status:` line is not detected. That's intended.
- BUT: it only checks design.md and tasks.md frontmatter if parse_frontmatter returns non-None. If design.md is missing frontmatter entirely, no error. So a design.md without frontmatter passes. Minor.
- Also ALLOWED_STATUS has 5 values; no enforcement of forward-only transitions (doc says single-direction). A spec could go from done back to draft and BACKLOG re-add it; no gate. Low.
- test_validate_spec_lifecycle covers gate0/backlog/tests path but doesn't test [TEST] group enforcement (the newly added TEST_GROUP check) or gate_version bypass. Wait, it does test `test_review_missing_test_group_rejected` and `test_draft_missing_test_group_allowed`. Yes, added. Good.
- But no test for gate_version 0 bypass of [TEST]. The test `test_valid_gate0_tree_passes` with draft+gate0 doesn't have [TEST] group and passes (but draft exempt anyway). No test that a ready-for-development + gate_version 0 bypasses [TEST]. Medium test gap.

Now "task DAG semantics":
- comma edges ignored (confirmed)
- range notation ignored
- non-backtick ignored
- draft/done exempt
- [P] only dst checked
- no duplicate task id detection
- only max task requires incoming edge; orphans allowed
- cross-feature endpoints ignored (documented)
- `max(ids)` string compare
- `strict=False` in zip (py3.10+; project py3.11 ok)

Let me verify duplicate id not flagged by probe? Not necessary; code clearly doesn't check.

Let me also check `parse_task_lines` uses TASK_RE `^-\s+\[[ xX]\]\s+(T\d{3})` — requires exactly 3 digits. Tasks T001-T039 fine. If T1000, not matched. Minor.

Now "newly added consistency gates":
- check_doc_consistency (substring)
- check_task_dag
- [TEST] group in validate_spec_lifecycle
- verify wiring

Let me also check `tools/verify.py` step order: lifecycle → doc_links → task_dag → doc_consistency → dep_pins → secrets → pytest → ruff. Fine. But note check_doc_consistency depends on F003/F007 files; if a feature is renamed, crashes.

Now let me produce the report. I need exact file:line evidence. Let me compile all with line numbers (using current snapshot; note HEAD churn). I should mention HEAD at audit end. Let me get final HEAD just before writing.

Let me also quickly double-check the current F007 tasks line numbers (they may have shifted after c8b8c64). The grep gave: tasks:27 T003 AC-010, tasks:50 T015 AC-011, tasks:69 T027 AC-011, tasks:70 T028 AC-010/AC-012. And spec:292 AC-011; AC-010/AC-012 absent. design:274 AC-011. design:5 related_features missing F008. design:22 stale range. Good, those are current.

Also confirm check_task_dag line numbers: 27 ENFORCED_STATUSES, 84-95 parse_edges, 88 zip, 93 fullmatch, 115 backwards, 117-119 parallel, 121-123 max incoming. And line 81 docstring non-T endpoints. Good.

Let me get final HEAD and maybe re-confirm the one failing test + all three standalone gates still pass. Already have. Let me get final HEAD.

Let me also verify `tools/check_doc_consistency.py` line numbers for the relevant checks: F007_D004 forbids `--universe-calendar` (212-214), F007-D003 (192-201), check_f007_declares_f003 (316-325), check_active_feature_indexes README regex (260, 379-388), AC_LINE_RE (248). Good.

Now let me write the final report in Chinese with the required structured block. The user wants severity/category/origin/pattern_tag and exact file:line. I'll produce a findings table with each.

Given output-style instructions (ADHD reader, cap lists at 5 items), but the user explicitly wants a full audit with all findings. The audit instructions require completeness. I'll present a prioritized findings list, but keep each finding tight. I'll cap at maybe 14 findings but group. Actually "Cap lists at 5 items" is a general style rule; the domain requires more. I'll organize into sections with concise bullets. I'll include the required <results> block.

Let me decide severity assignments:

P0 / Blocker:
F1. verify.py 当前红：test_f007_upstream_declaration_goes_red 失败（stale mutation）。tests/unit/test_check_doc_consistency.py:121-131; origin d659db7; pattern_tag stale-mutation-test. Category TestRegression.
   Severity: Blocker (统一质量门无法通过). 

P1 / High:
F2. DAG 门禁忽略逗号分隔边（F007 §4 大量使用），且忽略 `T004~T017` 区间与非反引号边；gate 能放行后向/未定义边。check_task_dag.py:84-95 (88 zip, 93 fullmatch); origin d659db7; pattern_tag dag-comma-edge-unparsed. GateGap.
F3. DAG 门禁对 draft 完全豁免，而当前 F003/F007/F008 全是 draft → 新门禁当前零执行；且 F008 一旦晋级 ready-for-development 立即判红（T029 无入边）。check_task_dag.py:27, 150-151; F008 tasks.md:70; origin d659db7 / bd87eac; pattern_tag gate-scope-draft-noop + latent-dag-failure. LifecycleScope.
F4. F007 tasks 引用不存在的 AC-010/AC-012（AC-011 存在，AC-010 缺失，AC 序列 009→011）。spec AC 定义 001-009,011；tasks:27 AC-010, tasks:70 AC-010+AC-012. validate_spec_lifecycle 不校验 task→AC 引用与 AC 连续性。origin 65e1832 (AC-011/012) + 24fdab9 (AC-010); pattern_tag dangling-ac-ref. GateGap / DocContradiction.
F5. F007 快照绑定与 ADR-0007 / architecture §4.4.1 契约冲突：F007 把 universe 拆为 F008 CSV artifact，而 ADR-0007:72-75 与 architecture:436-438 仍把 universe/calendar 当作单一 JSON；ADR 未被更新。origin b251826; pattern_tag cross-doc-contract-drift. ContractMismatch. (Maybe P1)
F6. F007 计划测试放 tests/contract 与 tests/mutation，verify.py 只收集 tests/unit+tests/integration → 这些契约/变异测试永不进门禁。tools/verify.py:53-54; F007 tasks:25,50,52,58,59,71; design:274; origin 8d2eae0e/65e1832; pattern_tag verify-testpath-blindspot. GateGap.

P2 / Medium:
F7. F007 design frontmatter related_features 缺 F008（spec/tasks 都有）。design.md:5; origin ccf577d (then 5728ccc added F008 elsewhere); pattern_tag frontmatter-drift. DocContradiction.
F8. F007 design §0 行为契约范围过期（FR-001~FR-006、DR-001~DR-004），实际有 FR-007、DR-005/006。design.md:22; origin 8d2eae0e; pattern_tag stale-contract-range. DocContradiction.
F9. 样本量三级边界重叠且用 `≈≥69` 非确定性符号：`30~69` 与 `≈≥69` 在 69 重叠。spec:181, design:136; origin 36b6564; pattern_tag ambiguous-boundary. DocContradiction.
F10. check_doc_consistency 全为子串断言，只锁字面量、不锁语义/枚举/交叉文件一致性：可写出自相矛盾但仍含关键字的文档而通过。check_doc_consistency.py:281-293, TEXT_CHECKS 41-246; origin d659db7; pattern_tag substring-only-gate. GateGap.
F11. F003 过渡元组 provenance 仍是单一 `universe_calendar_path`（design:120），与 F007 拆成两 artifact 的语义不一致；F003 声称与 ADR-0007 一致。design:120, spec:244/112; pattern_tag transition-tuple-split-drift. ContractMismatch.
F12. 测试对 TEXT_CHECKS 只变异 requires[0]/forbids[0]，其余断言无回归保护；test_unknown_check_id_absent_from_registry 是自比较恒真。tests/unit/test_check_doc_consistency.py:47-70; pattern_tag shallow-mutation. TestRegression/GateGap.
F13. validate_spec_lifecycle 未校验 AC 连续性、task→AC 引用、schema_version 载体；F007/F008 的 IR-003 类需求无 AC 载体门。validate_spec_lifecycle.py:227-254; pattern_tag no-ac-reference-integrity. GateGap.

P3 / Low:
F14. check_active_feature_indexes 的 README 正则要求 ≥2 个 F-id（`(?:F\d{3}\s*/\s*)+F\d{3}`），单活跃 feature 时必然误报；CLAUDE 正则只锁 ID 不锁状态文案。check_doc_consistency.py:260, 367-388. GateGap.
F15. check_task_dag 不检测重复任务 ID、孤儿任务（除最高号）、`[P]` 出边；max(ids) 字符串比较。check_task_dag.py:98-124. GateGap.
F16. check_doc_consistency 目标文档缺失时直接抛 FileNotFoundError（非结构化违规）。check_doc_consistency.py:264-265, 286/318. robustness.
F17. gate_version:0 可绕过全部内容门，且无门禁阻止新建 gate0 feature（仅文档约定）。validate_spec_lifecycle.py:178,185. GateGap. (This might deserve Medium.)

I'll include ~15 findings but organize by severity. I must cap lists at 5 items per style... but the audit demands completeness. I'll use a table which isn't a "list" per se. I'll keep it scannable.

Also mention HEAD churn: audited a333394..c8b8c64, HEAD moved during audit (36 commits). And all three standalone gates pass at snapshot; unified verify fails at pytest.

Let me get final HEAD and also confirm the exact test failure count.

Let me do one final command to capture HEAD and the standalone gate statuses + test result summary. Then write.

Actually I already have everything. Let me just get HEAD quickly.

  <details><summary>tool output</summary>

  ```text
HEAD=6b7ef77
--- standalone gates ---
check_task_dag: PASS
check_doc_consistency: PASS
validate_spec_lifecycle: PASS
=========================== short test summary info ============================
FAILED tests/unit/test_check_doc_consistency.py::test_f007_upstream_declaration_goes_red
1 failed, 70 passed in 1.55s


Incremental: 0 files updated, 0 nodes, 0 edges (postprocess=minimal)
  ```
  </details>

## assistant · 2026-09-16T16:37:41Z


> [reasoning] HEAD now 6b7ef77 — still moving. I'll report the audit window and note churn. The key findings hold across the commits since they concern the gate tools (added d659db7) and doc structures.

Let me write the final report. Chinese preferred.

I'll structure:
- 结论摘要 (3 bullets)
- 审计快照与范围
- 发现列表（表格：ID/severity/category/origin/pattern_tag/证据/问题）
- 放行非法文档的具体路径（gates that can pass invalid docs）
- 修复优先级
- <results> block

Need exact file:line. Use absolute paths.

Let me write carefully with absolute paths.

Findings with evidence:

F-01 Blocker TestRegression stale-mutation-test
`/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:121-131` — replace target `related_features: [F002, F003, F004]` no longer matches actual spec `[F002, F003, F004, F008]` (`/home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md:7`). Test fails → `tools/verify.py:52-55` pytest step red. origin d659db7 (test added) vs ccf577d/5728ccc (frontmatter changed).
Impact: unified gate cannot be green; and this claim in commit "变异单测" is false now.

F-02 High GateGap dag-comma-edge-unparsed
`/home/georg/projects/alphamill/tools/check_task_dag.py:84-95`; line 88 `left_raw.split("/")` only splits `/`, not `,`; line 93 `fullmatch(r"T\d{3}")` drops ranges. Probe: `T001,T002 -> T003` parses to []. Real usage: F007 tasks.md:77 `T001,T002,T003 -> T004~T017`, :78 `T004,T005 -> T006,T011,T012,T013`, :79 `T008,T009,T010 -> T011,T016,T017`, :82 `T011,T012 -> T014,T015`. So the majority of F007 declared deps aren't validated; a hidden backward edge or undefined endpoint in comma form passes.
Impact: DAG gate can pass invalid docs.

F-03 High LifecycleScope gate-scope-draft-noop + latent-dag-failure
`/home/georg/projects/alphamill/tools/check_task_dag.py:27` ENFORCED_STATUSES excludes draft; :150-151 skip. All active features draft (`BACKLOG.md:8-10`, specs status draft). Probe: broken DAG under draft returns []. Also F008 tasks.md:70 T029 (max id) has no incoming edge; probe with status=review flags `最高编号任务 T029 无入边`. origin d659db7 / bd87eac. 
Impact: new gate enforces nothing today; blocks F008 promotion.

F-04 High GateGap dangling-ac-ref
F007 tasks reference AC-010/AC-012 that don't exist; spec AC set is AC-001..009 + AC-011 only. Evidence: tasks.md:27 (AC-010), tasks.md:70 (AC-010, AC-012); spec.md:283-292. `validate_spec_lifecycle.py:227-254` only checks spec AC→requirement, not task→AC nor continuity. Origin 65e1832 (AC-011/012), 24fdab9 (AC-010).
Impact: task-AC traceability gate can pass dangling ACs.

F-05 High ContractMismatch cross-doc-contract-drift (snapshot binding)
F007 spec DR-006 `spec.md:221` + design `design.md:177-180` split universe (F008 CSV `lake/_metadata/universes/<digest>.csv`) from calendar JSON; ADR-0007 `0007-research-snapshot-binding.md:72-75` and architecture `alphamill-architecture.md:436-438` still define a single caller-provided universe/calendar JSON saved at `universe_calendars/<digest>.json`. ADR-0007 untouched in a333394..HEAD. Gate `check_doc_consistency.py:202-215` only checks F007 internal text.
Impact: the declared truth sources contradict F007; no gate catches ADR/architecture drift.

F-06 High GateGap verify-testpath-blindspot
`/home/georg/projects/alphamill/tools/verify.py:53-54` collects only tests/unit + tests/integration. F007 plans tests/contract/test_f007_artifact_schemas.py and tests/mutation/test_f007_gate_mutations.py: tasks.md:25,50,52,58,59,71; design.md:274. Neither dir exists (`tests/` only unit/integration/property/simulation).
Impact: F007 contract/mutation tests silently excluded from quality gate.

F-07 Medium DocContradiction frontmatter-drift
F007 design.md:5 `related_features: [F002, F003, F004]` vs spec.md:7 and tasks.md:5 `[F002, F003, F004, F008]`. Origin ccf577d, not updated by 5728ccc. Gate only checks spec frontmatter (`check_doc_consistency.py:316-325`).

F-08 Medium DocContradiction stale-contract-range
F007 design.md:22 says 行为契约 FR-001~FR-006、DR-001~DR-004 but spec has FR-007 (`spec.md:195`) and DR-005/DR-006 (`spec.md:224,221`). Origin 8d2eae0e, never updated.

F-09 Medium DocContradiction ambiguous-boundary
spec.md:181 and design.md:134-136 define `30~69` provisional and `≈≥69` trustworthy → overlap at 69 and non-deterministic `≈`. Origin 36b6564.

F-10 Medium GateGap substring-only-gate
`check_doc_consistency.py:41-246` + `281-293` are pure substring presence/absence. E.g. `terminal_run_facts` (51-60) only requires "四种终态"/"写终态 run.json" but never pins completed/rejected/failed/partial; a doc could list wrong states elsewhere and pass. No cross-file semantic checks except 3 custom ones.

F-11 Medium ContractMismatch transition-tuple-split-drift
F003 design.md:120 provenance has single `universe_calendar_path`; spec.md:244/112 claims field/identity alignment with ADR-0007. Under F007's split this can't reference both universe and calendar artifacts. Origin c1a124f/b251826.

F-12 Medium TestRegression shallow-mutation
`tests/unit/test_check_doc_consistency.py:47-66` mutates only `requires[0]`/`forbids[0]`; multi-clause checks (e.g. f007_declares_f008_universe has 5 requires) have unprotected clauses. `test_unknown_check_id_absent_from_registry` (69-70) compares a set to itself — tautology, no coverage.

F-13 Medium GateGap no-ac-reference-integrity (part of F-04). Could merge. I'll keep F-04 covering it.

F-14 Low GateGap readme-single-feature-regex
`check_doc_consistency.py:260` `README_ACTIVE_RE = 当前\s*((?:F\d{3}\s*/\s*)+F\d{3})` requires ≥2 ids; exactly one active feature can't be represented → false error. CLAUDE regex :259/367-369 only locks IDs, not status text.

F-15 Low GateGap dag-orphans-dupes
`check_task_dag.py:98-124`: no duplicate-ID check, only max task requires incoming edge (orphans T018-T024 in F007 pass), `[P]` outgoing not checked, `max(ids)` lexicographic.

F-16 Low robustness crash-on-missing-doc
`check_doc_consistency.py:264-265` `read()` raises FileNotFoundError if a target doc is renamed/deleted (acknowledged in test comment `tests/unit/test_check_doc_consistency.py:31-33`), instead of structured violation.

F-17 Low/Medium GateGap gate0-bypass
`validate_spec_lifecycle.py:178,185`: gate_version "0" returns after metadata checks → bypasses section structure, AC, Q/DQ, test paths, [TEST] group. Only docs (`docs/features/README.md`) forbid new gate0 features; no machine gate. No current feature uses 0, but template/author can.

That's 17. Fine.

Also mention: `check_doc_consistency` requires F007 tasks literal `T009 -> T012`, `T012 -> T013` (line 241-244) — the only two edges the DAG gate can even parse; this is why the check exists but is narrow. Ties to F-02.

Now write the <results> block with files and answer and next_steps.

I'll write in Chinese.

Let me be mindful: no emojis. Absolute paths. Provide exact evidence.

Write it.
审计完成（快照 `a333394..6b7ef77`，HEAD 在审计期间持续被自动提交推进：36b6564→c8b8c64→6b7ef77，行号以最终快照为准）。

<analysis>
**Literal Request**: 只读审计 a333394..HEAD 的 docs/tools/tests，重点 DAG 语义、生命周期、门禁、快照绑定、schema/version、F007/F008 契约与回归风险。
**Actual Need**: 找出"哪些新门禁实际没生效/能放行非法文档/文档间互相矛盾"，用于决定修复优先级。
**Success Looks Like**: 每条发现带 绝对路径:行号 + severity/category/origin/pattern_tag，并明确 gate 绕过路径。
</analysis>

## 结论摘要

1. 三个门禁脚本单独跑都 PASS，但 `tools/verify.py` 整体是**红的**：`tests/unit/test_check_doc_consistency.py:121-131` 的变异断言已过期，pytest 步骤失败（1 failed, 70 passed）。"统一质量门全绿"不成立。
2. 新 DAG 门禁有两处结构性放行：**逗号分隔边被静默丢弃**（F007 §4 大量使用），且**对 draft 完全豁免**——当前 F003/F007/F008 全是 draft，所以 DAG 门禁今天实际零执行。
3. 存在跨文档契约漂移：F007 把 universe/calendar 拆成两个 artifact，而 ADR-0007 与 architecture §4.4.1（项目自称的契约真相源）仍写单一 JSON，且 a333394..HEAD 内 ADR-0007 未被修改；无门禁检测该漂移。

## 审计快照与范围

- 区间：`a333394`（含）.. 审计结束时 `6b7ef77`；工具/测试新增集中在 `d659db7`。
- 三个脚本单独结果：`validate_spec_lifecycle` PASS、`check_task_dag` PASS、`check_doc_consistency` PASS；`tools/verify.py` 的 pytest 步骤 FAIL。
- 未改动任何文件；探针均在临时目录/纯函数上运行。

## 发现清单

| ID | Sev | Category | Origin | pattern_tag | 证据（绝对路径:行号）与问题 |
|---|---|---|---|---|---|
| F-01 | Blocker | TestRegression | d659db7 vs 5728ccc | stale-mutation-test | `/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:121-131` 的变异目标 `related_features: [F002, F003, F004]` 已不存在（实际 `spec.md:7` 为 `[F002, F003, F004, F008]`），replace 变成 no-op → 断言失败 → `/home/georg/projects/alphamill/tools/verify.py:52-55` pytest 步骤红 |
| F-02 | High | GateGap | d659db7 | dag-comma-edge-unparsed | `/home/georg/projects/alphamill/tools/check_task_dag.py:88` 仅 `split("/")`，不拆逗号；`:93` `fullmatch(T\d{3})` 丢弃 `T004~T017` 区间。探针：`T001,T002 -> T003` 解析为 `[]`。真实用例：F007 `tasks.md:77,78,79,82` 全是逗号边，均不被校验 |
| F-03 | High | LifecycleScope | d659db7 / bd87eac | gate-scope-draft-noop + latent-dag-failure | `/home/georg/projects/alphamill/tools/check_task_dag.py:27,150-151` 豁免 draft；`BACKLOG.md:8-10` 三个活跃 feature 全 draft → 门禁零执行。探针把 F008 改 review 立即报 `最高编号任务 T029 无入边`（`/home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md:70`） |
| F-04 | High | GateGap | 65e1832 / 24fdab9 | dangling-ac-ref | F007 `tasks.md:27` 引 `AC-010`、`tasks.md:70` 引 `AC-010`/`AC-012`，但 spec 只定义 `AC-001..AC-009, AC-011`（`spec.md:283-292`，序列缺 AC-010）。`/home/georg/projects/alphamill/tools/validate_spec_lifecycle.py:227-254` 只校验 spec AC→需求，不校验 task→AC 引用与 AC 连续性 |
| F-05 | High | ContractMismatch | b251826 | cross-doc-contract-drift | F007 `spec.md:221` + `design.md:177-180` 拆 universe 为 F008 CSV（`lake/_metadata/universes/<digest>.csv`）、calendar 为 JSON；ADR-0007 `/home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md:72-75` 与 architecture `/home/georg/projects/alphamill/docs/alphamill-architecture.md:436-438` 仍写"显式 universe/calendar JSON"单一 artifact。ADR-0007 在区间内零改动。门禁 `check_doc_consistency.py:202-215` 只查 F007 内部文本 |
| F-06 | High | GateGap | 8d2eae0e / 65e1832 | verify-testpath-blindspot | `/home/georg/projects/alphamill/tools/verify.py:53-54` 只收 tests/unit + tests/integration；F007 计划 `tests/contract/...`（tasks.md:25,50,58,71；design.md:274）与 `tests/mutation/...`（tasks.md:52,59），这两个目录不存在 → 永不进门禁 |
| F-07 | Medium | DocContradiction | ccf577d | frontmatter-drift | F007 `design.md:5` `related_features: [F002, F003, F004]` 缺 F008，而 `spec.md:7`、`tasks.md:5` 都是 `[F002, F003, F004, F008]`。门禁 `check_doc_consistency.py:316-325` 只查 spec frontmatter |
| F-08 | Medium | DocContradiction | 8d2eae0e | stale-contract-range | F007 `design.md:22` 声明行为契约 `FR-001~FR-006、DR-001~DR-004`，但 spec 已有 `FR-007`（`spec.md:195`）与 `DR-005`/`DR-006`（`spec.md:224,221`），从未更新 |
| F-09 | Medium | DocContradiction | 36b6564 | ambiguous-boundary | 样本量三级重叠：`30~69` 与 `≈≥69`（`spec.md:181`、`design.md:134-136`）在 69 处重叠，且 `≈` 是非确定性符号，不可机器判定 |
| F-10 | Medium | GateGap | d659db7 | substring-only-gate | `/home/georg/projects/alphamill/tools/check_doc_consistency.py:41-246,281-293` 全是字面量 in/not-in 断言。例：`:51-60` `terminal_run_facts` 只要求"四种终态"字样，从不锁定 `completed/rejected/failed/partial`；自相矛盾但含关键字的文档可通过 |
| F-11 | Medium | ContractMismatch | c1a124f / b251826 | transition-tuple-split-drift | F003 `design.md:120` 过渡元组 provenance 仍是单一 `universe_calendar_path`，`spec.md:244,112` 却声明字段/身份与 ADR-0007 逐项对齐；在 F007 拆分语义下无法同时引用 universe 与 calendar 两个 artifact |
| F-12 | Medium | TestRegression | d659db7 | shallow-mutation | `/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:47-66` 只变异 `requires[0]`/`forbids[0]`，多子句 check（如 `f007_declares_f008_universe` 有 5 条 requires）其余子句无回归保护；`:69-70` `test_unknown_check_id_absent_from_registry` 是集合自比较恒真 |
| F-13 | Low | GateGap | d659db7 | readme-single-feature-regex | `check_doc_consistency.py:260` `README_ACTIVE_RE` 要求 ≥2 个 F-id（`(?:F\d{3}\s*/\s*)+F\d{3}`），单活跃 feature 无法表达 → 必然误报；`:259,367-369` CLAUDE 正则只锁 ID、不锁状态文案 |
| F-14 | Low | GateGap | d659db7 | dag-orphans-dupes | `check_task_dag.py:98-124` 不查重复任务 ID；只要求最高编号任务有入边（F007 T018-T024 是孤儿却通过）；不查 `[P]` 的出边；`max(ids)` 为字符串比较 |
| F-15 | Low | robustness | d659db7 | crash-on-missing-doc | `check_doc_consistency.py:264-265` 目标文档被改名/删除时直接抛 `FileNotFoundError`（`tests/unit/test_check_doc_consistency.py:31-33` 已承认），而非结构化违规 |
| F-16 | Low | GateGap | 4ff8e10 | gate0-bypass | `validate_spec_lifecycle.py:178,185` 当 `gate_version != "1"` 即 return，跳过章节/AC/Q-DQ/tests路径/[TEST] 组全部校验；仅 `docs/features/README.md` 文字禁止新建 gate0 feature，无机器门 |

## 能放行非法文档的具体路径（重点）

1. **逗号边绕过**（F-02）：在 §4 写 `` `T099 -> T001` ``（逗号变体 `T001,T099 -> T002`）不会被解析，`check_task_dag` 既不报未定义端点也不报向后边；F007 现有大部分依赖正是逗号格式。
2. **draft 绕过**（F-03）：spec 保持 `status: draft` 即可让 DAG 门与 [TEST] 组门完全不执行；当前三个活跃 feature 正在享受该豁免。
3. **子串绕过**（F-10）：在文档任意处放一句含要求关键字的话（例如把四个终态写错但保留"四种终态"），`check_doc_consistency` 仍全绿。
4. **悬空 AC 绕过**（F-04）：tasks 可引用任意不存在的 AC-NNN，门禁不检查。
5. **跨文档漂移绕过**（F-05/F-07/F-08）：只改 F007 内部文本即可让 `check_doc_consistency` 通过，即使 ADR-0007/architecture/同 feature design frontmatter 仍写旧语义。

## 修复优先级建议

1. 先修 F-01（把变异字符串更新为当前 frontmatter），恢复 `tools/verify.py` 绿色——这是门禁可信度的前提。
2. 修 F-02：`parse_edges` 按 `,`、`/`、`~` 统一展开；为逗号边补变异单测。
3. 修 F-03：明确 F008 tasks 收口任务入边，或让 DAG 门对 `ready-for-development` 前的 doc-review 阶段也做只读告警。
4. 修 F-04：在 `validate_spec_lifecycle` 增加"tasks 引用的 AC 必须在 spec 定义 + AC 编号连续"校验。
5. 修 F-05：更新 ADR-0007 与 architecture §4.4.1 为 universe/calendar 双 artifact，或在 F007 中显式声明 supersede。

<results>
<files>
- /home/georg/projects/alphamill/tools/check_doc_consistency.py - 子串门禁主体；:260 README 正则缺陷；:264-265 缺文件崩溃；:281-293 子串断言；:316-396 三个 custom check
- /home/georg/projects/alphamill/tools/check_task_dag.py - DAG 门禁主体；:27 draft/done 豁免；:88,93 逗号/区间边被丢弃
- /home/georg/projects/alphamill/tools/validate_spec_lifecycle.py - 生命周期门；:178,185 gate0 绕过；:227-254 不校验 task→AC
- /home/georg/projects/alphamill/tools/verify.py - 统一入口；:53-54 只收 tests/unit+tests/integration
- /home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py - :121-131 当前失败；:47-70 浅变异
- /home/georg/projects/alphamill/tests/unit/test_check_task_dag.py - 无逗号边/区间边用例
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/spec.md - :7 frontmatter；:181 样本量边界；:221 DR-006 拆分；:283-292 AC 序列
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/design.md - :5 缺 F008；:22 契约范围过期；:134-136 边界；:177-180 快照路径
- /home/georg/projects/alphamill/docs/features/0.2/F007-evaluation-gates/tasks.md - :27,70 悬空 AC；:52,59 tests/mutation；:77-82 逗号边
- /home/georg/projects/alphamill/docs/features/0.2/F008-universe-expansion/tasks.md - :70 T029 无入边，晋级即判红
- /home/georg/projects/alphamill/docs/features/0.2/F003-alphagen-vendor/design.md - :120 过渡元组单一 universe_calendar_path
- /home/georg/projects/alphamill/docs/decisions/0007-research-snapshot-binding.md - :72-75 仍定义单一 universe/calendar JSON
- /home/georg/projects/alphamill/docs/alphamill-architecture.md - :436-438 与 ADR-0007 同款旧语义
- /home/georg/projects/alphamill/BACKLOG.md - :8-10 三 feature 均 draft
</files>

<answer>
新门禁"能跑通"不等于"有效"。当前状态下：DAG 门对 F003/F007/F008 全豁免（draft），且即便生效也会因逗号边解析失败而漏掉 F007 大部分依赖；子串一致性门可被含关键字但语义错误/跨文档矛盾的文档通过；F007 引用不存在的 AC-010/AC-012、design frontmatter 缺 F008、design §0 契约范围过期均未被任何门禁发现；F007 的 universe/calendar 拆分与 ADR-0007/architecture 的单一 JSON 契约冲突且 ADR 未更新。此外统一入口 verify.py 因一处过期变异测试当前为红。
</answer>

<next_steps>
1) 修 `/home/georg/projects/alphamill/tests/unit/test_check_doc_consistency.py:127` 的替换字符串为 `related_features: [F002, F003, F004, F008]`，重跑 `python3 tools/verify.py` 确认回绿（约 2 分钟）。
2) 给 `tools/check_task_dag.py:parse_edges` 增加逗号/`~` 展开，并在 `tests/unit/test_check_task_dag.py` 加一条逗号边用例（约 15 分钟）。
3) 决定 F007 AC-010/AC-012 是补定义还是删引用；随后在 `validate_spec_lifecycle` 增加 task→AC 完整性校验。
</next_steps>
</results>
