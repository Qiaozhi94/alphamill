"""F012 AC-009 取证校验：执行机夜槽 alphagen 实跑证据字段齐全且与 run.json 副本一致。

证据由 `tools/f012_capacity_evidence.py` 从真实运行生成并入库；本用例只核对，不重跑。
证据缺失即红——产能结论只认执行机 CUDA 实跑（spec §CPU 条款），不以 skip 充当证据。
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

EVIDENCE_DIR = Path(__file__).resolve().parents[2] / "reports" / "f012"
REQUIRED = (
    "host",
    "run_id",
    "binding",
    "status",
    "stop_reason",
    "device",
    "counts",
    "registered",
    "evaluations",
    "duration_s",
    "vram_peak_gb",
    "prefilter_ms_p50",
    "prefilter_ms_p95",
    "run_json_sha256",
)


@pytest.fixture(scope="module")
def evidence() -> tuple[dict, dict, bytes]:
    evidence_path = EVIDENCE_DIR / "capacity-evidence.json"
    run_path = EVIDENCE_DIR / "capacity-run.json"
    assert evidence_path.is_file() and run_path.is_file(), "T019 执行机夜槽取证尚未入库"
    raw = run_path.read_bytes()
    return json.loads(evidence_path.read_text(encoding="utf-8")), json.loads(raw), raw


def test_evidence_fields_are_complete(evidence) -> None:
    body, _, _ = evidence
    missing = [key for key in REQUIRED if body.get(key) is None]
    assert not missing, missing


def test_evidence_comes_from_a_cuda_run_on_the_execution_machine(evidence) -> None:
    body, run, _ = evidence
    assert body["host"] == run["hostname"] == "qiaozhi-lt"
    assert body["device"] == run["device"] == "cuda"
    assert run["generator"] == "alphagen" and run["tier_level"] == "L0"
    assert run["binding"]["mode"] == "explicit_tuples", "真实湖显式绑定"


def test_evidence_matches_the_run_manifest_copy(evidence) -> None:
    body, run, raw = evidence
    assert body["run_json_sha256"] == hashlib.sha256(raw).hexdigest()
    for key in ("run_id", "status", "stop_reason", "counts", "evaluations", "budget"):
        assert body[key] == run[key], key
    assert body["registered"] == run["counts"]["registered"]
    started = datetime.fromisoformat(run["started_at"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(run["finished_at"].replace("Z", "+00:00"))
    assert abs(body["duration_s"] - (finished - started).total_seconds()) < 1.0


def test_shortfall_below_fifty_is_registered_as_an_m2_finding(evidence) -> None:
    body, _, _ = evidence
    assert body["status"] in {"completed", "partial"}
    if body["registered"] < 50:
        assert body["m2_capacity_finding"], "未达 50 必须同时登记 M2 产能发现"
    else:
        assert body["m2_capacity_finding"] is None
