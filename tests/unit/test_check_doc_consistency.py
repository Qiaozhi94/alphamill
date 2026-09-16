"""check_doc_consistency 回归测试（修复方证据：每条断言必须可红）。

两组断言：
  - 真实仓库上 `run_checks` 全绿；
  - 逐条 `TEXT_CHECKS` 做变异：删掉要求文本（或写回废弃文本）后，该 check 必须报错。
    变异在 tmp_path 的副本上做，不触碰仓库文件。
"""

from __future__ import annotations

import pathlib
import shutil

import pytest

from tools import check_doc_consistency as cdc

REPO = cdc.ROOT
TEXT_CHECK_IDS = [c.check_id for c in cdc.TEXT_CHECKS]
ALL_DOC_FILES = {
    cdc.SPEC,
    cdc.DESIGN,
    cdc.TASKS,
    cdc.F007_SPEC,
    cdc.F007_DESIGN,
    cdc.F007_TASKS,
}


def _materialize(tmp_path: pathlib.Path, rels: set[str]) -> None:
    # check_text_checks 会读取全部目标文档（便于跨 check 共享缓存），因此副本必须
    # 包含所有目标文件，否则未拷贝的文件会直接抛 FileNotFoundError。
    for rel in sorted(rels | ALL_DOC_FILES):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, dst)


def _check_ids(errors: list[tuple[str, str]]) -> set[str]:
    return {cid for cid, _ in errors}


def test_repo_passes_all_checks() -> None:
    assert cdc.run_checks(REPO) == []


@pytest.mark.parametrize("chk", cdc.TEXT_CHECKS, ids=lambda c: c.check_id)
def test_required_text_removed_goes_red(tmp_path: pathlib.Path, chk: cdc.TextCheck) -> None:
    rels = {rel for rel, _ in chk.requires} | {rel for rel, _ in chk.forbids}
    _materialize(tmp_path, rels)
    rel, needle = chk.requires[0]
    target = tmp_path / rel
    target.write_text(
        target.read_text(encoding="utf-8").replace(needle, "REMOVED"), encoding="utf-8"
    )
    assert chk.check_id in _check_ids(cdc.check_text_checks(tmp_path))


@pytest.mark.parametrize("chk", [c for c in cdc.TEXT_CHECKS if c.forbids], ids=lambda c: c.check_id)
def test_deprecated_text_reintroduced_goes_red(tmp_path: pathlib.Path, chk: cdc.TextCheck) -> None:
    rels = {rel for rel, _ in chk.requires} | {rel for rel, _ in chk.forbids}
    _materialize(tmp_path, rels)
    rel, needle = chk.forbids[0]
    target = tmp_path / rel
    target.write_text(target.read_text(encoding="utf-8") + f"\n{needle}\n", encoding="utf-8")
    assert chk.check_id in _check_ids(cdc.check_text_checks(tmp_path))


def test_unknown_check_id_absent_from_registry() -> None:
    assert sorted(TEXT_CHECK_IDS) == sorted({c.check_id for c in cdc.TEXT_CHECKS})


def _copy_index_tree(tmp_path: pathlib.Path) -> None:
    shutil.copytree(REPO / "docs" / "features", tmp_path / "docs" / "features")
    shutil.copyfile(REPO / "docs" / "README.md", tmp_path / "docs" / "README.md")
    shutil.copyfile(REPO / "BACKLOG.md", tmp_path / "BACKLOG.md")
    shutil.copyfile(REPO / "CLAUDE.md", tmp_path / "CLAUDE.md")


def test_active_feature_indexes_go_red_on_claude_drift(tmp_path: pathlib.Path) -> None:
    _copy_index_tree(tmp_path)
    claude = tmp_path / "CLAUDE.md"
    claude.write_text(
        claude.read_text(encoding="utf-8").replace("F008 宇宙扩容", "F099 幽灵需求"),
        encoding="utf-8",
    )
    assert "active_feature_indexes_aligned" in _check_ids(
        cdc.check_active_feature_indexes(tmp_path)
    )


def test_active_feature_indexes_go_red_on_readme_drift(tmp_path: pathlib.Path) -> None:
    _copy_index_tree(tmp_path)
    readme = tmp_path / "docs" / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "活跃 feature 索引（当前 F003/F007/F008）",
            "活跃 feature 索引（当前 F003/F007）",
        ),
        encoding="utf-8",
    )
    assert "active_feature_indexes_aligned" in _check_ids(
        cdc.check_active_feature_indexes(tmp_path)
    )


def test_active_feature_indexes_go_red_on_backlog_drift(tmp_path: pathlib.Path) -> None:
    _copy_index_tree(tmp_path)
    backlog = tmp_path / "BACKLOG.md"
    kept = [
        ln
        for ln in backlog.read_text(encoding="utf-8").split("\n")
        if not ln.startswith("| F008-universe-expansion ")
    ]
    backlog.write_text("\n".join(kept), encoding="utf-8")
    assert "active_feature_indexes_aligned" in _check_ids(
        cdc.check_active_feature_indexes(tmp_path)
    )


def test_f007_upstream_declaration_goes_red(tmp_path: pathlib.Path) -> None:
    target = tmp_path / cdc.F007_SPEC
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / cdc.F007_SPEC, target)
    target.write_text(
        target.read_text(encoding="utf-8").replace(
            "related_features: [F002, F003, F004, F008]", "related_features: [F002, F004, F008]"
        ),
        encoding="utf-8",
    )
    assert "f007_declares_f003_upstream" in _check_ids(cdc.check_f007_declares_f003(tmp_path))


def test_ac_body_coverage_goes_red(tmp_path: pathlib.Path) -> None:
    target = tmp_path / cdc.SPEC
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO / cdc.SPEC, target)
    target.write_text(
        target.read_text(encoding="utf-8").replace("DR-001 运行字段", "运行字段"),
        encoding="utf-8",
    )
    assert cdc.AC_FINDING in _check_ids(cdc.check_ac_body_covers_clauses(tmp_path))


def test_f007_design_test_map_goes_red_on_unmapped_test(tmp_path: pathlib.Path) -> None:
    _materialize(tmp_path, set())
    tasks = tmp_path / cdc.F007_TASKS
    tasks.write_text(
        tasks.read_text(encoding="utf-8")
        + "\n- [ ] T099: 幽灵用例 — verify: `tests/unit/evaluation/test_ghost_unmapped.py`\n",
        encoding="utf-8",
    )
    errors = cdc.check_f007_design_test_map_covers_tasks(tmp_path)
    assert "tests/unit/evaluation/test_ghost_unmapped.py" in " ".join(msg for _, msg in errors)
