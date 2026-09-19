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
# 由注册表推导，避免硬编码列表随新增断言（其他 feature 的检视轮次也会追加）失效。
ALL_DOC_FILES = {rel for chk in cdc.TEXT_CHECKS for rel, _ in (*chk.requires, *chk.forbids)}


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


def test_find_task_line_ignores_checkbox_state() -> None:
    tasks = (
        "- [ ] T012 (`FR-004`): 先做查重\n"
        "- [x] T018 (`FR-008`): 只搬运结论、不重算\n"
        "- [ ] T0123: 另一条任务\n"
    )
    assert cdc.find_task_line(tasks, "T012").startswith("- [ ] T012")
    assert cdc.find_task_line(tasks, "T018").startswith("- [x] T018")
    assert cdc.find_task_line(tasks, "T0123").startswith("- [ ] T0123")
    assert cdc.find_task_line(tasks, "T999") == ""


def test_ticking_f007_tasks_keeps_the_dedup_gate_green(tmp_path: pathlib.Path) -> None:
    """回归：契约断言必须按任务号取行，勾选（`- [x]`）不得让 T012/T018 断言失效。"""
    for rel in (cdc.F007_SPEC, cdc.F007_DESIGN, cdc.F007_TASKS):
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / rel, dst)
    assert cdc.check_f007_dedup_precedes_verdict(tmp_path) == []
    tasks_path = tmp_path / cdc.F007_TASKS
    tasks_path.write_text(
        tasks_path.read_text(encoding="utf-8")
        .replace("- [ ] T012", "- [x] T012")
        .replace("- [ ] T018", "- [x] T018"),
        encoding="utf-8",
    )
    assert cdc.check_f007_dedup_precedes_verdict(tmp_path) == []


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
            "活跃 feature 索引（当前 F003/F008）",
            "活跃 feature 索引（当前 F003）",
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


def test_stale_closed_question_task_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R2-006：前置任务只引用已关闭的 Q 时必须判红。"""
    _materialize(tmp_path, {cdc.SPEC, cdc.TASKS})
    target = tmp_path / cdc.TASKS
    target.write_text(
        target.read_text(encoding="utf-8") + "\n- [ ] T099 (`Q-001`): 已关闭问题的过时前置动作\n",
        encoding="utf-8",
    )
    assert "no_stale_closed_question_task" in _check_ids(
        cdc.check_no_stale_closed_question_task(tmp_path)
    )


def _materialize_referenced_tests(tmp_path: pathlib.Path) -> None:
    """把三件套引用的、仓库中已存在的测试文件也拷进 tmp 根（carrier 检查用）。"""
    _materialize(tmp_path, {cdc.SPEC, cdc.DESIGN, cdc.TASKS})
    for rel in (cdc.SPEC, cdc.DESIGN, cdc.TASKS):
        text = (tmp_path / rel).read_text(encoding="utf-8")
        for ref in set(cdc.TEST_REF_RE.findall(text)):
            dst = tmp_path / ref
            src = cdc.ROOT / ref
            if src.is_file() and not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)


def test_declared_test_carrier_missing_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R2-002/R4-005：已落盘的载体文件被删除必须判红。

    变异：tmp 根含全部三件套与既有测试文件，唯独删掉契约测试文件——
    对应「声明的载体不存在」的失败模式（Round 3 曾以未落盘文件宣称修复）。
    """
    _materialize_referenced_tests(tmp_path)
    (tmp_path / "tests/integration/test_f003_kronos_lifecycle.py").unlink()
    errors = cdc.check_declared_test_carriers(tmp_path)
    assert "declared_test_carrier_exists" in _check_ids(errors)
    assert any("test_f003_kronos_lifecycle.py" in msg for _, msg in errors)


def test_declared_test_carrier_ghost_reference_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R4-005：引用未登记白名单的幽灵测试文件必须判红。"""
    _materialize_referenced_tests(tmp_path)
    tasks = tmp_path / cdc.TASKS
    tasks.write_text(
        tasks.read_text(encoding="utf-8")
        + "\n- [ ] T099: 幽灵用例 — verify: `tests/unit/test_f003_ghost.py`\n",
        encoding="utf-8",
    )
    errors = cdc.check_declared_test_carriers(tmp_path)
    assert "declared_test_carrier_exists" in _check_ids(errors)
    assert any("test_f003_ghost.py" in msg for _, msg in errors)


def test_declared_test_carrier_landed_allowlist_entry_goes_red(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F003-R4-005：白名单条目对应文件已落盘必须判红（过期豁免会盖住载体删除）。"""
    _materialize_referenced_tests(tmp_path)
    landed = "tests/integration/test_f003_kronos_lifecycle.py"
    monkeypatch.setattr(cdc, "DECLARED_TEST_ALLOWLIST", {landed: "T999"})
    errors = cdc.check_declared_test_carriers(tmp_path)
    assert any("白名单条目已落盘" in msg for _, msg in errors)


# ---- F007 Round 2 解析式检查的变异回归（修复方证据：解析门必须可红）----


def _materialize_f007(tmp_path: pathlib.Path) -> None:
    _materialize(tmp_path, {cdc.F007_SPEC, cdc.F007_DESIGN, cdc.F007_TASKS})


def _rewrite(path: pathlib.Path, old: str, new: str, count: int = -1) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(old, new) if count < 0 else text.replace(old, new, count)
    path.write_text(text, encoding="utf-8")


def test_f007_lifecycle_closure_goes_red_on_missing_registration(
    tmp_path: pathlib.Path,
) -> None:
    """F007-D026：拒绝成员的终态登记路径被删必须判红（状态机解析，非子串）。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_SPEC,
        "REJECTED -> REGISTERED",
        "REJECTED -> REGISTERED_X",
    )
    ids = _check_ids(cdc.check_f007_lifecycle_closure(tmp_path))
    assert "f007_lifecycle_closure" in ids


def test_f007_promotion_enum_goes_red_on_missing_blocked_state(tmp_path: pathlib.Path) -> None:
    """F007-D027：promotion_verdict 枚举丢 blocked_pending_audit 必须判红。"""
    _materialize_f007(tmp_path)
    design = tmp_path / cdc.F007_DESIGN
    before = design.read_text(encoding="utf-8")
    _rewrite(design, r"blocked_pending_audit \| dead", r"dead")
    # 变异必须真的改到文本，否则「门禁没报错」只是因为没变异（Round 3 实测的假绿）。
    assert design.read_text(encoding="utf-8") != before
    ids = _check_ids(cdc.check_f007_promotion_blocked_state_defined(tmp_path))
    assert "f007_promotion_blocked_state_defined" in ids


def test_f007_registry_writeback_carrier_goes_red_on_lost_requirement(
    tmp_path: pathlib.Path,
) -> None:
    """F007-D028：FR-008 需求块消失必须判红（评测面回写无载体）。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_SPEC,
        "### Requirement: 评测面回写与查重判定（`FR-008`）",
        "### Requirement: 评测面回写与查重判定（`FR-009`）",
    )
    ids = _check_ids(cdc.check_f007_registry_writeback_carrier(tmp_path))
    assert "f007_registry_writeback_carrier" in ids


def test_f007_design_ac_map_goes_red_on_missing_row(tmp_path: pathlib.Path) -> None:
    """F007-D035：design §8 丢 AC-012 映射行必须判红（spec AC ⊆ design §8）。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_DESIGN,
        "| `AC-012` | integration + contract |"
        " `tests/integration/test_f007_synthesis.py`、"
        "`tests/contract/test_f007_artifact_schemas.py`"
        " | 五阶段 ID 与 `failure_taxonomy` 三维聚合；枚举外取值拒绝 |\n",
        "",
    )
    ids = _check_ids(cdc.check_f007_design_covers_all_spec_acs(tmp_path))
    assert "f007_design_covers_all_spec_acs" in ids


def test_f007_test_group_verify_goes_red_on_uncovered_carrier(tmp_path: pathlib.Path) -> None:
    """F007-D029：[TEST] 条目 verify 不运行其 AC 载体文件必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_TASKS,
        " tests/contract/test_f007_artifact_schemas.py`",
        "`",
        count=1,
    )
    ids = _check_ids(cdc.check_f007_test_group_verify_covers_ac_map(tmp_path))
    assert "f007_test_group_verify_covers_ac_map" in ids


def test_f007_requirement_id_order_goes_red_on_reorder(tmp_path: pathlib.Path) -> None:
    """F007-D039：spec §4 需求 ID 乱序必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_SPEC,
        "### Requirement: 成本、容量与时间稳定性（`FR-005`）",
        "### Requirement: 成本、容量与时间稳定性（`FR-009`）",
    )
    ids = _check_ids(cdc.check_f007_requirement_id_order(tmp_path))
    assert "f007_requirement_id_order" in ids


def test_declared_test_carrier_orphan_entry_goes_red(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F003-R4-005/R5-004：三件套已不引用的白名单条目必须判红（孤儿豁免不得残留）。"""
    _materialize_referenced_tests(tmp_path)
    orphan = "tests/unit/test_ghost_carrier.py"
    monkeypatch.setattr(cdc, "DECLARED_TEST_ALLOWLIST", {orphan: "T999"})
    errors = cdc.check_declared_test_carriers(tmp_path)
    assert any(f"孤儿条目，请移除）：{orphan}" in msg for _, msg in errors)


def _arch_copy(tmp_path: pathlib.Path) -> pathlib.Path:
    _materialize(tmp_path, {cdc.ARCH})
    return tmp_path / cdc.ARCH


def test_offload_table_row_disposition_flip_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R4-004：把某行的处置改成放行必须判红（片段级 require 曾漏掉这种改写）。"""
    arch = _arch_copy(tmp_path)
    row = cdc.EXPECTED_OFFLOAD_TABLE[3]  # 停止失败 → fail-closed
    text = arch.read_text(encoding="utf-8")
    mutated = text.replace(
        f"| {row[0]} | {row[1]} | {row[2]} |",
        f"| {row[0]} | {row[1]} | 记 `offload_not_needed`，继续夜槽 |",
    )
    assert mutated != text
    arch.write_text(mutated, encoding="utf-8")
    assert "offload_decision_table_rows" in _check_ids(cdc.check_offload_decision_table(tmp_path))


def test_offload_table_row_removed_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R4-004：删掉整行（例如「控制面不可达但服务在」）必须判红。"""
    arch = _arch_copy(tmp_path)
    row = cdc.EXPECTED_OFFLOAD_TABLE[4]
    text = arch.read_text(encoding="utf-8")
    mutated = text.replace(f"  | {row[0]} | {row[1]} | {row[2]} |\n", "")
    assert mutated != text
    arch.write_text(mutated, encoding="utf-8")
    assert "offload_decision_table_rows" in _check_ids(cdc.check_offload_decision_table(tmp_path))


def test_offload_table_process_criterion_goes_red(tmp_path: pathlib.Path) -> None:
    """F003-R6-001：404 行退回「卡上无 Kronos 进程」判据必须判红（WSL2 下恒真）。"""
    arch = _arch_copy(tmp_path)
    text = arch.read_text(encoding="utf-8")
    mutated = text.replace(
        "或设备侧 `memory.used` 低于可配阈值 `kronos_vram_idle_threshold`",
        "或卡上无 Kronos 进程",
    )
    assert mutated != text
    arch.write_text(mutated, encoding="utf-8")
    assert "offload_decision_table_rows" in _check_ids(cdc.check_offload_decision_table(tmp_path))


def test_offload_table_anchor_missing_goes_red(tmp_path: pathlib.Path) -> None:
    """删掉决策表锚点（整张表被搬走/改名）必须判红，而不是静默通过。"""
    arch = _arch_copy(tmp_path)
    arch.write_text(
        arch.read_text(encoding="utf-8").replace(cdc.OFFLOAD_TABLE_ANCHOR, "**其它标题**"),
        encoding="utf-8",
    )
    assert "offload_decision_table_rows" in _check_ids(cdc.check_offload_decision_table(tmp_path))


# ---- F007 Round 3 解析式检查的变异回归（D041/D042/D043/D044）----


def test_f007_promotion_enum_goes_red_on_priority_output_not_in_enum(
    tmp_path: pathlib.Path,
) -> None:
    """F007-D041：优先级表输出一个枚举里没有的取值必须判红（Round 3 实测漏检点）。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_DESIGN,
        "| 6 | `sample_tier=provisional` | `provisional` |",
        "| 6 | `sample_tier=provisional` | `ghost_verdict` |",
    )
    ids = _check_ids(cdc.check_f007_promotion_blocked_state_defined(tmp_path))
    assert "f007_promotion_blocked_state_defined" in ids


def test_f007_promotion_enum_goes_red_on_spec_order_drift(tmp_path: pathlib.Path) -> None:
    """F007-D041：spec 优先级串与 design 表行序不一致必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_SPEC,
        "`rejected > incomplete > underpowered",
        "`incomplete > rejected > underpowered",
    )
    ids = _check_ids(cdc.check_f007_promotion_blocked_state_defined(tmp_path))
    assert "f007_promotion_blocked_state_defined" in ids


def test_f007_promotion_table_goes_red_when_rejected_state_uncovered(
    tmp_path: pathlib.Path,
) -> None:
    """F007-D043：优先级表不覆盖 run 终态 REJECTED / 查重结论必须判红。"""
    _materialize_f007(tmp_path)
    design = tmp_path / cdc.F007_DESIGN
    row = [ln for ln in design.read_text(encoding="utf-8").split("\n") if ln.startswith("| 1 |")][0]
    _rewrite(design, row, "| 1 | 统计判死的特殊情形 | `rejected` |")
    errors = cdc.check_f007_promotion_blocked_state_defined(tmp_path)
    assert any("REJECTED" in msg for _, msg in errors)


def test_f007_dedup_goes_red_when_writeback_recomputes(tmp_path: pathlib.Path) -> None:
    """F007-D042：回写侧重新计算查重（丢掉「不重算」约束）必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(tmp_path / cdc.F007_DESIGN, "不重算", "重新计算")
    ids = _check_ids(cdc.check_f007_dedup_precedes_verdict(tmp_path))
    assert "f007_dedup_precedes_verdict" in ids


def test_f007_dedup_goes_red_when_finalize_order_inverted(tmp_path: pathlib.Path) -> None:
    """F007-D042：finalize 段不再写明「先查重、再导出 verdict」必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(
        tmp_path / cdc.F007_DESIGN,
        "**先做 `|ρ|` 查重判定、再按 §3.3 优先级表导出 `promotion_verdict`**，",
        "",
    )
    ids = _check_ids(cdc.check_f007_dedup_precedes_verdict(tmp_path))
    assert "f007_dedup_precedes_verdict" in ids


def test_f007_lifecycle_goes_red_on_uncovered_failure_mapping(tmp_path: pathlib.Path) -> None:
    """F007-D044：design §7 的失败映射在 spec §5 无对应迁移必须判红。"""
    _materialize_f007(tmp_path)
    _rewrite(tmp_path / cdc.F007_SPEC, "RUNNING -> REJECTED", "RUNNING -> REJECTED_X")
    errors = cdc.check_f007_lifecycle_closure(tmp_path)
    assert any("RUNNING -> REJECTED" in msg for _, msg in errors)


def test_f007_lifecycle_goes_red_without_abandon_entrypoint(tmp_path: pathlib.Path) -> None:
    """F007-D044：abandon 没有 CLI 入口必须判红（INCOMPLETE 终态无法收口）。"""
    _materialize_f007(tmp_path)
    _rewrite(tmp_path / cdc.F007_DESIGN, "python -m alphamill.evaluation abandon", "# removed")
    errors = cdc.check_f007_lifecycle_closure(tmp_path)
    assert any("abandon" in msg for _, msg in errors)
