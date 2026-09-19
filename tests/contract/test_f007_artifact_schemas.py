"""T015 / `AC-005`·`AC-011`·`AC-012`·`NFR-005`：report/curves/synthesis schema reader 契约。

覆盖：schema 版本门（当前版可读、未知高版本失败关闭）、必填字段、`approximation` 标注必须存在且
canonical 恒为非近似、曲线-标量互推必须一致、五阶段 ID 与失败三维枚举校验、以及产物路径必须是
POSIX 逻辑路径（反斜杠/盘符/UNC 一律拒绝）。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.factor_factory.bench.artifact_schema import (
    ArtifactSchemaError,
    assert_approximation,
    assert_failure_taxonomy,
    assert_logical_posix_paths,
    assert_stage_ids,
    is_logical_posix_path,
    read_artifact_dir,
    read_report,
    read_synthesis,
)
from alphamill.factor_factory.bench.curves import build_equity_curves, write_curves
from alphamill.factor_factory.bench.stage_model import (
    STAGE_COST_CAPACITY,
    STAGE_EXECUTION_IMPLEMENTATION,
    STAGE_PORTFOLIO_TRANSFORM,
    STAGE_SIGNAL_QUALITY,
    STAGE_TEMPORAL_STABILITY,
    STATUS_FAIL,
    STATUS_PASS,
    FailureRecord,
    StageResult,
    StageResults,
    not_applicable,
)

START = datetime(2026, 9, 1, tzinfo=UTC)
EXPERIMENT = "sha256:" + "e" * 64
NOW = "2026-09-01T00:00:00Z"


def _curves(size: int = 10):
    times = tuple(START + timedelta(hours=index) for index in range(size))
    periods = tuple(0.01 if index % 2 else -0.005 for index in range(size))
    return build_equity_curves(periods, times=times)


def _stage_results(cost_fail: bool = False) -> StageResults:
    failures = ()
    if cost_fail:
        failures = (
            FailureRecord(
                stage=STAGE_COST_CAPACITY,
                owner="cost",
                mechanism="cost_negative",
                error_code="E_REQUIRED_METRIC_FAILED",
                first_seen=NOW,
            ),
        )
    return StageResults(
        results=(
            StageResult(STAGE_SIGNAL_QUALITY, STATUS_PASS),
            not_applicable(STAGE_PORTFOLIO_TRANSFORM, "因子运行不建组合"),
            StageResult(
                STAGE_COST_CAPACITY, STATUS_FAIL if cost_fail else STATUS_PASS, failures=failures
            ),
            StageResult(STAGE_TEMPORAL_STABILITY, STATUS_PASS),
            not_applicable(STAGE_EXECUTION_IMPLEMENTATION, "无执行实现"),
        )
    )


def _report_payload(curves, *, canonical: bool = False, stage_results=None) -> dict:
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT,
        "approximation": {
            "is_approximate": False,
            "reduced_dimensions": [],
            "signal_source": "real",
        },
        "curves_summary": curves.scalar_summary(),
        "stage_results": (stage_results or _stage_results()).to_payload(),
        "provenance": {"physical_path": "C:\\data\\reports\\bench"},
    }


def _write_bundle(directory: Path, *, canonical: bool = False, stage_results=None) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    curves = _curves()
    write_curves(directory / "curves.parquet", curves)
    (directory / "report.json").write_text(
        json.dumps(_report_payload(curves, canonical=canonical, stage_results=stage_results)),
        encoding="utf-8",
    )


# ---------- POSIX 逻辑路径 ----------


@pytest.mark.parametrize(
    "value",
    [
        "reports/bench/x/curves.parquet",
        "reports/research_snapshots/sha256:ab/manifest.json",
        "a/b.json",
    ],
)
def test_posix_logical_paths_are_accepted(value: str):
    assert is_logical_posix_path(value) is True


@pytest.mark.parametrize(
    "value",
    [
        "C:\\data\\reports\\x.parquet",
        "reports\\bench\\x.parquet",
        "\\\\wsl$\\Ubuntu\\mnt\\c",
        "",
        "/abs/path.json",
    ],
)
def test_non_posix_paths_are_rejected(value: str):
    assert is_logical_posix_path(value) is False


def test_logical_path_assertion_scans_nested_payloads():
    clean = {"experiment_id": EXPERIMENT, "artifact_ref": "reports/bench/x/curves.parquet"}
    assert_logical_posix_paths(clean)
    dirty = {"artifact_refs": [{"evidence_ref": "D:\\lake\\x.json"}]}
    with pytest.raises(ArtifactSchemaError, match="不是 POSIX 逻辑路径"):
        assert_logical_posix_paths(dirty)


def test_provenance_is_exempt_from_the_logical_path_rule():
    payload = {
        "artifact_ref": "reports/bench/x/curves.parquet",
        "provenance": {
            "physical_path": "C:\\data\\reports\\bench",
            "member_manifest_paths": {"ohlcv_1m": "\\\\wsl$\\Ubuntu\\mnt\\c\\x.json"},
        },
    }
    assert_logical_posix_paths(payload)


def test_provenance_physical_path_is_exempt_from_contract_paths(tmp_path):
    """物理路径只允许出现在 provenance 这类非契约字段里；契约字段仍受断言。"""
    _write_bundle(tmp_path)
    payload = read_report(tmp_path / "report.json")
    assert payload["provenance"]["physical_path"].startswith("C:")


# ---------- approximation ----------


def test_approximation_annotation_is_mandatory():
    with pytest.raises(ArtifactSchemaError, match="缺 approximation"):
        assert_approximation({"experiment_id": EXPERIMENT}, canonical=False)
    with pytest.raises(ArtifactSchemaError, match="缺 is_approximate"):
        assert_approximation({"approximation": {}}, canonical=False)


def test_canonical_must_not_be_approximate():
    approximate = {"approximation": {"is_approximate": True, "reduced_dimensions": ["window"]}}
    with pytest.raises(ArtifactSchemaError, match="不得为近似"):
        assert_approximation(approximate, canonical=True)
    reduced = {"approximation": {"is_approximate": False, "reduced_dimensions": ["symbols"]}}
    with pytest.raises(ArtifactSchemaError, match="reduced_dimensions"):
        assert_approximation(reduced, canonical=True)


def test_preview_approximation_is_allowed_and_visible():
    payload = {"approximation": {"is_approximate": True, "reduced_dimensions": ["symbols"]}}
    assert_approximation(payload, canonical=False)


# ---------- schema 版本与必填字段 ----------


def test_unknown_schema_version_fails_closed(tmp_path):
    _write_bundle(tmp_path)
    path = tmp_path / "report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["schema_version"] = 99
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactSchemaError, match="schema_version 不支持"):
        read_report(path)


def test_report_missing_required_fields_fails_closed(tmp_path):
    _write_bundle(tmp_path)
    path = tmp_path / "report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    del payload["curves_summary"]
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactSchemaError, match="缺必填字段"):
        read_report(path)


def test_missing_artifact_file_fails_closed(tmp_path):
    with pytest.raises(ArtifactSchemaError, match="report 不存在"):
        read_report(tmp_path / "nope.json")
    with pytest.raises(ArtifactSchemaError, match="synthesis 不存在"):
        read_synthesis(tmp_path / "nope.json")


def test_synthesis_required_fields_and_columns(tmp_path):
    path = tmp_path / "synthesis_report.json"
    path.write_text(json.dumps({"schema_version": 1, "synthesis_id": "sha256:x"}), encoding="utf-8")
    with pytest.raises(ArtifactSchemaError, match="缺必填字段"):
        read_synthesis(path)
    payload = {
        "schema_version": 1,
        "synthesis_id": "sha256:" + "b" * 64,
        "cohort_id": "cohort_sha256:" + "c" * 64,
        "status": "FINALIZED",
        "funnel": {},
        "stage_funnel": {},
        "failures": [],
        "facts": [],
        "inferences": [],
        "recommendations": [],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert read_synthesis(path)["status"] == "FINALIZED"


# ---------- 互推与枚举 ----------


def test_artifact_dir_recomputes_scalars_from_sidecar(tmp_path):
    _write_bundle(tmp_path)
    bundle = read_artifact_dir(tmp_path)
    assert bundle.curves.scalar_summary() == bundle.report["curves_summary"]
    assert bundle.synthesis is None


def test_tampered_scalar_summary_is_detected(tmp_path):
    _write_bundle(tmp_path)
    path = tmp_path / "report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["curves_summary"]["final_equity"] = 999.0
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactSchemaError, match="互推不符"):
        read_artifact_dir(tmp_path)


def test_stage_ids_and_failure_taxonomy_are_enforced(tmp_path):
    payload = _report_payload(_curves(), stage_results=_stage_results(cost_fail=True))
    assert_stage_ids(payload)
    assert_failure_taxonomy(payload)
    broken_stage = json.loads(json.dumps(payload))
    broken_stage["stage_results"][0]["stage"] = "unknown_stage"
    with pytest.raises(ArtifactSchemaError, match="未登记阶段"):
        assert_stage_ids(broken_stage)
    broken_mechanism = json.loads(json.dumps(payload))
    broken_mechanism["stage_results"][2]["failures"][0]["mechanism"] = "vibes"
    with pytest.raises(ArtifactSchemaError, match="mechanism 未登记"):
        assert_failure_taxonomy(broken_mechanism)


def test_canonical_bundle_rejects_approximate_report(tmp_path):
    directory = tmp_path / "bench"
    _write_bundle(directory)
    path = directory / "report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["approximation"] = {"is_approximate": True, "reduced_dimensions": ["window"]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ArtifactSchemaError, match="不得为近似"):
        read_artifact_dir(directory, canonical=True)
