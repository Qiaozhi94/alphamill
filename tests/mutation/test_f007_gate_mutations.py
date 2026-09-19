"""T017 / `AC-001`~`AC-013`：F007 门禁的定向变异证据（判别力）。

每个 mutant 用「等价但被削弱」的判据与真实判据跑同一输入：
`killed = 真实拦截 ∧ 削弱放行`。任一项 survived 说明该门禁缺判别力，本文件即判红
（`design.md` §8：无 survived 才算通过）。报告路径见 `mutation.report_path`。
"""

from __future__ import annotations

import json

import pytest

from alphamill.validation.mutation import (
    HARNESS,
    MUTANTS,
    REPORT_NAME,
    build_report,
    report_path,
    survivors,
    write_report,
)


def test_every_mutant_is_killed():
    report = build_report()
    assert survivors(report) == ()
    assert report["totals"] == {"mutants": len(MUTANTS), "killed": len(MUTANTS), "survived": 0}


@pytest.mark.parametrize("mutant", MUTANTS, ids=lambda m: m.mutant_id)
def test_mutant_discriminates_real_gate_from_weakened_gate(mutant):
    assert mutant.real() is True, f"{mutant.mutant_id}: 真实判据未拦截"
    assert mutant.weakened() is False, f"{mutant.mutant_id}: 削弱判据竟然也拦截"
    assert mutant.killed is True
    payload = mutant.to_payload()
    assert payload["status"] == "killed"
    assert payload["real_detected"] is True
    assert payload["weakened_detected"] is False


def test_report_lists_every_gate_under_mutation():
    report = build_report()
    assert report["harness"] == HARNESS
    assert {entry["mutant_id"] for entry in report["mutants"]} == {
        "M01_future_fill",
        "M02_embargo_comparator",
        "M03_guard_registration",
        "M04_preview_writer",
        "M05_exception_swallowing",
        "M06_publish_completeness",
    }
    assert all(entry["gate"] and entry["description"] for entry in report["mutants"])


def test_report_is_written_to_the_mutation_evidence_path(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(tmp_path))
    path = write_report(tmp_path)
    assert path == report_path(tmp_path)
    assert path.name == REPORT_NAME
    assert path.parent.as_posix().endswith("mutation/f007")
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["totals"]["survived"] == 0
    assert stored["schema_version"] == 1


def test_write_report_is_idempotent(tmp_path):
    first = write_report(tmp_path).read_text(encoding="utf-8")
    second = write_report(tmp_path).read_text(encoding="utf-8")
    assert first == second
