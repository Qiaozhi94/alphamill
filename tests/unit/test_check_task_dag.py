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


def test_multi_source_multi_target_edge_expansion(tmp_path: pathlib.Path) -> None:
    text = tasks("- `T001/T002 -> T003`：多源边展开。")
    write_feature(tmp_path, "review", text)
    assert dag.run_checks(tmp_path) == []
