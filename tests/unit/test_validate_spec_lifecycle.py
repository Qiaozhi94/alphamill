"""validate_spec_lifecycle 回归测试（CURRENT-code.md C002）。

三组真实校验：frontmatter 解析与 status 必填、AC tests 路径逃逸检查、
BACKLOG 双向一致性。全部走 verify_repo(root=tmp_path) 端到端断言。
"""

from __future__ import annotations

import pathlib
import re

import pytest

from tools import validate_spec_lifecycle as vsl

SPEC_GATE0_DRAFT = """---
kind: feature
id: F001
version: "0.1"
status: draft
gate_version: 0
---

# F001-demo

正文占位。
"""
DESIGN_MIN = "# F001-demo design\n"
TASKS_MIN = "# F001-demo tasks\n"
BACKLOG_HEADER = "# BACKLOG\n\n| Feature | 版本 | 状态 | 链接 |\n|---|---|---|---|\n"


def write_feature(tmp_path: pathlib.Path, spec: str) -> pathlib.Path:
    d = tmp_path / "docs" / "features" / "0.1" / "F001-demo"
    d.mkdir(parents=True)
    (d / "spec.md").write_text(spec, encoding="utf-8")
    (d / "design.md").write_text(DESIGN_MIN, encoding="utf-8")
    (d / "tasks.md").write_text(TASKS_MIN, encoding="utf-8")
    return d


def write_backlog(tmp_path: pathlib.Path, row: str | None) -> None:
    content = BACKLOG_HEADER + (row + "\n" if row else "")
    (tmp_path / "BACKLOG.md").write_text(content, encoding="utf-8")


VALID_BACKLOG_ROW = "| F001-demo | 0.1 | draft | [spec](docs/features/0.1/F001-demo/spec.md) |"


def test_frontmatter_parses_valid_file() -> None:
    fm = vsl.parse_frontmatter("---\nkind: feature\nstatus: draft\n---\n\n# t\n")
    assert fm == {"kind": "feature", "status": "draft"}


def test_missing_status_field_rejected(tmp_path: pathlib.Path) -> None:
    no_status = SPEC_GATE0_DRAFT.replace("status: draft\n", "")
    write_feature(tmp_path, no_status)
    write_backlog(tmp_path, VALID_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("非法 status: None" in e for e in errors)


def test_valid_gate0_tree_passes(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT)
    write_backlog(tmp_path, VALID_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert ok, errors


def _review_spec(ac_line: str) -> str:
    sections = "\n\n".join(f"## {s}\n无" for s in vsl.SPEC_SECTIONS)
    sections = sections.replace("## 4. 需求\n无", "## 4. 需求\n\n- FR-001: 示例需求")
    sections = sections.replace("## 6. 成功与验收\n无", f"## 6. 成功与验收\n\n{ac_line}")
    front = '---\nkind: feature\nid: F001\nversion: "0.1"\nstatus: review\ngate_version: 1\n---'
    return f"{front}\n\n# F001-demo\n\n{sections}\n"


REVIEW_DESIGN = "# d\n\n" + "\n\n".join(f"## {s}\n无" for s in vsl.DESIGN_SECTIONS) + "\n"
REVIEW_TASKS_NO_TEST_GROUP = (
    "# t\n\n" + "\n\n".join(f"## {s}\n无" for s in vsl.TASKS_SECTIONS) + "\n"
)
REVIEW_TASKS = REVIEW_TASKS_NO_TEST_GROUP.replace(
    "## 3. 验证与验收任务\n无",
    "## 3. 验证与验收任务\n\n"
    "### [TEST] 组：层 2 旅程验收轨（必填）\n\n"
    "- [ ] T009 [TEST] (`AC-1`): 旅程验收",
)
REVIEW_TASKS_TEST_GROUP_IN_SECTION5 = REVIEW_TASKS_NO_TEST_GROUP.replace(
    "## 5. 明确后移\n无",
    "## 5. 明确后移\n\n"
    "### [TEST] 组：层 2 旅程验收轨（必填）\n\n"
    "- [ ] T009 [TEST] (`AC-1`): 放错章节不算数",
)
REVIEW_BACKLOG_ROW = "| F001-demo | 0.1 | review | [spec](docs/features/0.1/F001-demo/spec.md) |"


def write_review_tree(tmp_path: pathlib.Path, spec: str) -> None:
    d = tmp_path / "docs" / "features" / "0.1" / "F001-demo"
    d.mkdir(parents=True)
    (d / "spec.md").write_text(spec, encoding="utf-8")
    (d / "design.md").write_text(REVIEW_DESIGN, encoding="utf-8")
    (d / "tasks.md").write_text(REVIEW_TASKS, encoding="utf-8")
    (tmp_path / "tests" / "unit").mkdir(parents=True)
    (tmp_path / "tests" / "unit" / "test_demo.py").write_text("def test_x(): pass\n")


def test_review_tests_path_exists_passes(tmp_path: pathlib.Path) -> None:
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/test_demo.py`"
    write_review_tree(tmp_path, _review_spec(ac))
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert ok, errors
    assert not [e for e in errors if "路径" in e]


def test_review_tests_path_missing_rejected(tmp_path: pathlib.Path) -> None:
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/missing.py`"
    write_review_tree(tmp_path, _review_spec(ac))
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("tests/unit/missing.py" in e and "路径不存在" in e for e in errors)


def test_review_tests_path_escape_rejected(tmp_path: pathlib.Path) -> None:
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/../../../outside.py`"
    write_review_tree(tmp_path, _review_spec(ac))
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("路径不合法（禁止绝对路径/.. 逃逸）" in e for e in errors)


def test_backlog_missing_active_feature_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT)
    write_backlog(tmp_path, None)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("BACKLOG 缺少非 done Feature: F001-demo" in e for e in errors)


def test_backlog_status_mismatch_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT)
    wrong_row = (
        "| F001-demo | 0.1 | ready-for-development | [spec](docs/features/0.1/F001-demo/spec.md) |"
    )
    write_backlog(tmp_path, wrong_row)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any(
        "BACKLOG F001-demo status=ready-for-development 与 spec (draft) 不一致" in e for e in errors
    )


def test_backlog_unknown_feature_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT)
    ghost_row = "| F099-ghost | 0.1 | draft | [spec](docs/features/0.1/F099-ghost/spec.md) |"
    write_backlog(tmp_path, VALID_BACKLOG_ROW + "\n" + ghost_row)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("BACKLOG 含未知 Feature: F099-ghost" in e for e in errors)


def test_backlog_planning_section_not_parsed_by_gate(tmp_path: pathlib.Path) -> None:
    """「规划中」小节即使行形状与活跃索引一致，也不得触发「含未知 Feature」误报。"""
    write_feature(tmp_path, SPEC_GATE0_DRAFT)
    planning = (
        BACKLOG_HEADER
        + VALID_BACKLOG_ROW
        + "\n\n## 规划中\n\n"
        + "| Feature | 需求 | 里程碑 | 编号状态 |\n|---|---|---|---|\n"
        + "| F099-ghost | 任意 | M9 | [spec](docs/features/0.9/F099-ghost/spec.md) |\n"
    )
    (tmp_path / "BACKLOG.md").write_text(planning, encoding="utf-8")
    ok, errors = vsl.verify_repo(tmp_path)
    assert ok, errors
    assert not any("F099-ghost" in e for e in errors)


def test_review_missing_test_group_rejected(tmp_path: pathlib.Path) -> None:
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/test_demo.py`"
    write_review_tree(tmp_path, _review_spec(ac))
    (tmp_path / "docs" / "features" / "0.1" / "F001-demo" / "tasks.md").write_text(
        REVIEW_TASKS_NO_TEST_GROUP, encoding="utf-8"
    )
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("[TEST] 组" in e for e in errors)


def test_draft_missing_test_group_allowed(tmp_path: pathlib.Path) -> None:
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/test_demo.py`"
    write_review_tree(tmp_path, _review_spec(ac).replace("status: review", "status: draft"))
    (tmp_path / "docs" / "features" / "0.1" / "F001-demo" / "tasks.md").write_text(
        REVIEW_TASKS_NO_TEST_GROUP, encoding="utf-8"
    )
    write_backlog(
        tmp_path,
        "| F001-demo | 0.1 | draft | [spec](docs/features/0.1/F001-demo/spec.md) |",
    )
    ok, errors = vsl.verify_repo(tmp_path)
    assert ok, errors


def test_test_group_in_wrong_section_rejected(tmp_path: pathlib.Path) -> None:
    """R2-007：[TEST] 标题出现在第 3 节之外不算数（放错章节必须判红）。"""
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/test_demo.py`"
    write_review_tree(tmp_path, _review_spec(ac))
    (tmp_path / "docs" / "features" / "0.1" / "F001-demo" / "tasks.md").write_text(
        REVIEW_TASKS_TEST_GROUP_IN_SECTION5, encoding="utf-8"
    )
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("[TEST] 组" in e for e in errors)


INFLIGHT_AC = "- [ ] **AC-1** (`FR-001`): 示例验收 tests: `tests/unit/test_demo.py`"


def _review_spec_with_status(status_word: str) -> str:
    return _review_spec(INFLIGHT_AC).replace("status: review", f"status: {status_word}")


def _backlog_row(status_word: str) -> str:
    return f"| F001-demo | 0.1 | {status_word} | [spec](docs/features/0.1/F001-demo/spec.md) |"


@pytest.mark.parametrize("status_word", ["doc-reviewing", "developing", "code-reviewing"])
def test_v4_status_words_allowed(tmp_path: pathlib.Path, status_word: str) -> None:
    """v4.2 词表迁移：doc-reviewing / developing / code-reviewing 必须判为合法。"""
    write_review_tree(tmp_path, _review_spec_with_status(status_word))
    write_backlog(tmp_path, _backlog_row(status_word))
    ok, errors = vsl.verify_repo(tmp_path)
    assert ok, errors


def test_unknown_status_word_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT.replace("status: draft", "status: shipping"))
    write_backlog(tmp_path, VALID_BACKLOG_ROW.replace("| draft |", "| shipping |"))
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("非法 status: shipping" in e for e in errors)


def test_illegal_gate_version_rejected(tmp_path: pathlib.Path) -> None:
    write_feature(tmp_path, SPEC_GATE0_DRAFT.replace("gate_version: 0", "gate_version: 2"))
    write_backlog(tmp_path, VALID_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("非法 gate_version: 2" in e for e in errors)


def test_norm_status_maps_legacy_aliases() -> None:
    assert vsl.norm_status("in-progress") == "developing"
    assert vsl.norm_status("review") == "code-reviewing"
    assert vsl.norm_status("ready") == "ready-for-development"
    assert vsl.norm_status("developing") == "developing"
    assert vsl.norm_status("shipping") == "shipping"


def test_legacy_in_progress_enforces_test_group_like_developing(tmp_path: pathlib.Path) -> None:
    """旧词 in-progress 与规范词 developing 执法一致：[TEST] 组缺失即判红。"""
    write_review_tree(tmp_path, _review_spec_with_status("in-progress"))
    (tmp_path / "docs" / "features" / "0.1" / "F001-demo" / "tasks.md").write_text(
        REVIEW_TASKS_NO_TEST_GROUP, encoding="utf-8"
    )
    write_backlog(tmp_path, _backlog_row("in-progress"))
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("[TEST] 组" in e for e in errors)


def test_legacy_review_requires_tests_path_like_code_reviewing(tmp_path: pathlib.Path) -> None:
    """旧词 review 与规范词 code-reviewing 执法一致：AC 缺 tests 路径即判红。"""
    ac = "- [ ] **AC-1** (`FR-001`): 示例验收"
    write_review_tree(tmp_path, _review_spec(ac))
    write_backlog(tmp_path, REVIEW_BACKLOG_ROW)
    ok, errors = vsl.verify_repo(tmp_path)
    assert not ok
    assert any("缺少 tests: 路径" in e for e in errors)


# ---------- AC tests 引用识别（F007 D-??：标识符 backtick 不是 tests 路径） ----------


@pytest.mark.parametrize(
    "token",
    [
        "tests/unit/evaluation/test_cost_and_stability.py",
        "tests/integration/test_f007_cli.py",
        "deployment/verify.ps1",
        "tests/fixtures/f007/README.md",
    ],
)
def test_path_shaped_tokens_are_treated_as_tests(token: str) -> None:
    assert vsl.looks_like_test_path(token) is True


@pytest.mark.parametrize(
    "token",
    [
        "promotion_verdict",
        "E_INPUT_INVALID",
        "DR-005",
        "[0,30)",
        "0.90~0.99",
        "universe_at(T)",
        "https://example.com/tests/unit/x.py",
        # 端点取值：F003 AC-010 的 `/health.device=cpu` 曾被当成「绝对路径」判红，
        # 逼着规格改措辞——而那句原文被 check_doc_consistency 钉死，两条门禁互相打架。
        "/health.device=cpu",
        "/lifecycle/status",
        "state=transitional",
    ],
)
def test_identifier_and_url_backticks_are_not_tests(token: str) -> None:
    assert vsl.looks_like_test_path(token) is False


def test_f007_ac_identifier_backticks_are_not_mistaken_for_test_paths() -> None:
    """回归：AC 正文的标识符 backtick 不得被判为 tests 路径，路径形 token 必须真实存在。"""
    spec = (vsl.ROOT / "docs" / "features" / "0.2" / "F007-evaluation-gates" / "spec.md").read_text(
        encoding="utf-8"
    )
    tokens = [
        token
        for line in spec.splitlines()
        if (matched := vsl.AC_RE.match(line))
        for token in re.findall(r"`([^`]+)`", matched.group(4))
    ]
    identifiers = [token for token in tokens if "/" not in token]
    assert identifiers, "F007 的 AC 正文应含标识符 backtick"
    assert [token for token in identifiers if vsl.looks_like_test_path(token)] == []
    paths = [token for token in tokens if vsl.looks_like_test_path(token)]
    assert paths, "F007 的 AC 正文应已回填 tests 路径"
    assert all((vsl.ROOT / path).is_file() for path in paths)
