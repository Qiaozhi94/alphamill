"""check_task_dag 回归测试（修复方证据：DAG 门禁可红，且作用域正确）。

用 tmp_path 下的合成 Feature 覆盖五类违规，并验证 `draft` 不在作用域内
（否则会把尚未进入流转的 Feature 一并判红）。
"""

from __future__ import annotations

import pathlib

from tools import check_task_dag as dag

FEATURE_DIR = pathlib.Path("docs") / "features" / "0.2" / "F001-demo"


def write_feature(root: pathlib.Path, status: str, tasks: str) -> None:
    d = root / FEATURE_DIR
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(
        "---\n"
        "kind: feature\n"
        "id: F001\n"
        'version: "0.2"\n'
        f"status: {status}\n"
        "gate_version: 1\n"
        "---\n\n# F001-demo\n",
        encoding="utf-8",
    )
    (d / "tasks.md").write_text(tasks, encoding="utf-8")


def tasks(edges: str, *, t002_parallel: bool = False) -> str:
    p = " [P]" if t002_parallel else ""
    return (
        "# F001-demo tasks\n\n"
        "## 2. 实现任务\n\n"
        "- [ ] T001 (`FR-001`): a\n"
        f"- [ ] T002{p} (`FR-001`): b\n"
        "- [ ] T003 (`FR-001`): c\n"
        f"\n## 4. 依赖与并行关系\n\n{edges}\n"
    )


VALID = tasks("- `T001 -> T002 -> T003`：线性依赖。")
UNKNOWN = tasks("- `T001 -> T099`：指向不存在任务。")
BACKWARD = tasks("- `T003 -> T001`：依赖后序任务。")
NO_INCOMING = tasks("- `T001 -> T002`：最高编号任务 T003 无入边。")
PARALLEL_TARGET = tasks("- `T001 -> T002`：T002 是 [P] 却声明了前置边。", t002_parallel=True)
ORPHAN = tasks("- `T001 -> T003`：T002 不在任何边上。")
KEY_EDGE_REMOVED = (
    "# F001-demo tasks\n\n"
    "## 2. 实现任务\n\n"
    "- [ ] T001 (`FR-001`): a\n"
    "- [ ] T002 (`FR-001`): b\n"
    "- [ ] T003 (`FR-001`): c\n"
    "- [ ] T004 (`FR-001`): d\n"
    "\n## 4. 依赖与并行关系\n\n"
    "- `T001 -> T002 -> T003`：链\n"
    "- `T001 -> T004`：收口任务另有入边，故最高任务规则通过\n"
)


def test_valid_dag_passes(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", VALID)
    assert dag.run_checks(tmp_path) == []


def test_unknown_endpoint_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", UNKNOWN)
    assert any("未定义" in msg for _, msg in dag.run_checks(tmp_path))


def test_backward_edge_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", BACKWARD)
    assert any("向后边" in msg for _, msg in dag.run_checks(tmp_path))


def test_last_task_without_incoming_edge_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", NO_INCOMING)
    assert any("无入边" in msg for _, msg in dag.run_checks(tmp_path))


def test_parallel_task_with_predecessor_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", PARALLEL_TARGET)
    assert any("[P]" in msg for _, msg in dag.run_checks(tmp_path))


def test_orphan_task_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", ORPHAN)
    errors = dag.run_checks(tmp_path)
    assert any("T002" in msg and "孤立任务" in msg for _, msg in errors)


def test_missing_key_edge_breaks_reachability(tmp_path: pathlib.Path) -> None:
    """T004 仍有入边（最高任务规则通过），但 T003 失去通往收口的边——必须判红。"""
    write_feature(tmp_path, "review", KEY_EDGE_REMOVED)
    errors = dag.run_checks(tmp_path)
    assert not any("无入边" in msg for _, msg in errors)
    assert any("T003" in msg and "孤立任务" in msg for _, msg in errors)


def test_draft_feature_not_enforced(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "draft", BACKWARD + NO_INCOMING)
    assert dag.run_checks(tmp_path) == []


def test_v4_status_words_enforced(tmp_path: pathlib.Path) -> None:
    """v4.2 词表迁移：developing / code-reviewing 必须与旧词一样进入 DAG 执法范围。"""
    for word in ("developing", "code-reviewing"):
        write_feature(tmp_path, word, BACKWARD)
        assert any("向后边" in msg for _, msg in dag.run_checks(tmp_path)), word


def test_doc_reviewing_feature_enforced(tmp_path: pathlib.Path) -> None:
    """doc-reviewing 也在作用域内：检视整改改动 tasks §4 时就要能判红，而不是等流转后
    才暴露（F009-R3-001、F010-R3-001 两次复现的 gate-scope-blind-spot）。"""
    write_feature(tmp_path, "doc-reviewing", BACKWARD)
    assert any("向后边" in msg for _, msg in dag.run_checks(tmp_path))


def test_multi_source_multi_target_edge_expansion(tmp_path: pathlib.Path) -> None:
    text = tasks("- `T001/T002 -> T003`：多源边展开。")
    write_feature(tmp_path, "review", text)
    assert dag.run_checks(tmp_path) == []


# ---- F007-D033：§3 验证任务前置规则与 verify 生产者规则 ----

S3_OK = (
    "# F001-demo tasks\n\n"
    "## 2. 实现任务\n\n"
    "- [ ] T001 (`FR-001`): impl — verify: `tests/unit/test_impl.py`\n"
    "- [ ] T002 (`FR-001`): impl2\n"
    "\n## 3. 验证与验收任务\n\n"
    "- [ ] T003 (`AC-001`): run — verify: `pytest -q tests/unit/test_impl.py`\n"
    "\n## 4. 依赖与并行关系\n\n"
    "- `T001/T002 -> T003`：生产者 → 验证者。\n"
)

S3_NO_PRED = (
    "# F001-demo tasks\n\n"
    "## 2. 实现任务\n\n"
    "- [ ] T001 (`FR-001`): impl — verify: `tests/unit/test_impl.py`\n"
    "- [ ] T002 (`FR-001`): impl2\n"
    "\n## 3. 验证与验收任务\n\n"
    "- [ ] T003 (`AC-001`): run — verify: `pytest -q tests/unit/test_impl.py`\n"
    "\n## 4. 依赖与并行关系\n\n"
    "- `T001 -> T002`：验证任务没有前置。\n"
)

S3_UNWIRED_PRODUCER = (
    "# F001-demo tasks\n\n"
    "## 2. 实现任务\n\n"
    "- [ ] T001 (`FR-001`): impl — verify: `tests/unit/test_impl.py`\n"
    "- [ ] T002 (`FR-001`): impl2\n"
    "\n## 3. 验证与验收任务\n\n"
    "- [ ] T003 (`AC-001`): run — verify: `pytest -q tests/unit/test_impl.py`\n"
    "\n## 4. 依赖与并行关系\n\n"
    "- `T002 -> T003`：前置不是文件生产者。\n"
)


def test_section3_with_wired_producer_passes(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", S3_OK)
    assert dag.run_checks(tmp_path) == []


def test_section3_task_without_predecessor_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", S3_NO_PRED)
    errors = dag.run_checks(tmp_path)
    assert any("T003" in msg and "无前置边" in msg for _, msg in errors)


def test_section3_task_with_unwired_producer_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, "review", S3_UNWIRED_PRODUCER)
    errors = dag.run_checks(tmp_path)
    assert any("T003" in msg and "test_impl.py" in msg for _, msg in errors)


def test_real_feature_tasks_satisfy_verification_rules() -> None:
    """真实仓库锁定：F007/F003 的 §3 规则当前满足（draft 不强制，这里显式钉住）。"""
    for rel in (
        "docs/features/0.2/F007-evaluation-gates/tasks.md",
        "docs/features/0.2/F003-alphagen-vendor/tasks.md",
    ):
        text = (dag.ROOT / rel).read_text(encoding="utf-8")
        assert dag.check_tasks(text) == [], rel


def test_f007_producer_rule_goes_red_on_unwired_edge() -> None:
    """F007-D033：删掉 `T017 -> T022` 生产者边必须判红（真实文本变异）。"""
    rel = "docs/features/0.2/F007-evaluation-gates/tasks.md"
    text = (dag.ROOT / rel).read_text(encoding="utf-8")
    mutated = text.replace("`T017 -> T022`", "`T017`")
    assert any("T022" in msg for msg in dag.check_tasks(mutated))
