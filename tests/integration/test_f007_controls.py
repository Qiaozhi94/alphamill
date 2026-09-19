"""T016 / `AC-003`·`SC-001`：四类控制的全链 golden 与多成员 cohort 分母完整性。

用 T002 冻结的四个控制夹具（正控制 ×2、白噪声、故意泄漏）走 canonical 全链，逐项对照
`expected-outcomes-v1.json` 的预期门禁结果；再 finalize 多成员 cohort，验证：

- **拒绝者仍入分母**：泄漏控制的 `promotion_verdict=rejected` 但 `trial_count` / `member_count`
  仍计入它，`rejected_count=1`；
- **多成员批量夹具分母完整**：四个成员各自终态登记，集合与承诺完全相等；
- **诊断性重算不重复计数**：同语义重跑幂等复用既有实验，成员数不变；
- synthesis 从 finalized 台账重建时，拒绝者出现在漏斗分母中。
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import registry, symbol_map
from alphamill.evaluation.cli import main
from alphamill.evaluation.universe_ledger import UniverseMember, publish_universe
from alphamill.experiment_store import population
from alphamill.experiment_store import research_snapshot as snapshot_store
from alphamill.experiment_store.synthesis import STATUS_FINALIZED, build_synthesis

pytestmark = pytest.mark.integration

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "f007"
CONFIG = FIXTURES / "method-v1.json"
OUTCOMES = json.loads((FIXTURES / "expected-outcomes-v1.json").read_text(encoding="utf-8"))
CONTROLS = {control["name"]: control for control in OUTCOMES["controls"]}
DATASET = "derivatives_funding_rates"
VERSION = "v2026.09.01"
CUTOFF = "2026-09-01T12:00:00Z"
NOW = "2026-09-01T00:00:00Z"
CALENDAR = {
    "schema_version": 1,
    "timezone": "UTC",
    "windows": [{"start": "2026-09-01T00:00:00Z", "end": "2026-09-30T00:00:00Z"}],
}
CANDIDATES = {
    name: f"factor_sha256:{index:064d}" for index, name in enumerate(sorted(CONTROLS), start=1)
}


def _lake(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "lake"
    spec = registry.require_dataset(DATASET)
    payload = b"x" * 10
    day = "2026-09-01"
    rel = f"{DATASET}/exchange=binance/pair=BTC-USDT/date={day}.r1.parquet"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    partition = {
        "logical_partition_key": {"exchange": "binance", "pair": "BTC-USDT", "date": day},
        "path": rel,
        "rows": 10,
        "time_min": f"{day}T00:00:00Z",
        "time_max": f"{day}T23:59:00Z",
        "row_digest": "sha256:" + "a" * 64,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    mf.publish_manifest(
        root,
        {
            "dataset": DATASET,
            "data_version": VERSION,
            "status": "valid",
            "rows": partition["rows"],
            "value_digest": mf.compute_value_digest(spec, [partition]),
            "partitions": [partition],
        },
    )
    frame = symbol_map.build_symbol_map([symbol_map.SymbolRow("binance", "perp", "BTC/USDT")])
    sm_payload = symbol_map.canonical_csv_bytes(frame)
    sm_digest = symbol_map.content_digest(sm_payload)
    sm_path = root / "_metadata" / "symbol_maps" / f"{sm_digest}.csv"
    sm_path.parent.mkdir(parents=True, exist_ok=True)
    sm_path.write_bytes(sm_payload)
    universe_digest = publish_universe(
        [
            UniverseMember(
                exchange="binance",
                market_type="perp",
                db_symbol="BTC/USDT",
                lake_pair="BTC-USDT-PERP",
                valid_from="2026-08-01T00:00:00Z",
                valid_to="",
                reason="listed",
                universe_id="uni-1",
            )
        ],
        root,
    )
    return root, sm_digest, universe_digest


@pytest.fixture()
def sandbox(tmp_path, monkeypatch):
    lake, symbol_map_digest, universe_digest = _lake(tmp_path)
    reports = tmp_path / "reports"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(lake))
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
    monkeypatch.setattr("alphamill.evaluation.code_build.worktree_dirty", lambda root=None: False)
    snapshot = snapshot_store.build_snapshot(
        lake_root=lake,
        root=reports,
        cutoff=datetime.fromisoformat(CUTOFF),
        datasets={DATASET: VERSION},
        universe_digest=universe_digest,
        calendar=CALENDAR,
        symbol_map_digest=symbol_map_digest,
    )
    snapshot_store.publish_snapshot(reports, snapshot)
    definition = {
        "schema_version": 1,
        "hypothesis_family": "f007-controls",
        "selection_stage": "cross_sectional",
        "method_config_ref": "method-v1",
        "cost_model_ref": "cm-v1",
        "inclusion_rules": "全部承诺成员计入分母",
        "commitments": [
            {"candidate_id": CANDIDATES[name], "generator": "manual", "registered_at": NOW}
            for name in sorted(CONTROLS)
        ],
        "window": {
            "selection": ["2026-01-01T00:00:00Z", "2026-04-01T00:00:00Z"],
            "label_horizons": [1, 4, 24],
        },
        "universe_digest": universe_digest,
        "calendar_digest": "sha256:" + "0" * 64,
        "frozen_at": NOW,
        "frozen_by": "Georg",
    }
    cohort_id, _ = population.freeze_cohort(reports, definition)
    return {
        "reports": reports,
        "snapshot_id": snapshot.snapshot_id,
        "cohort_id": cohort_id,
    }


def _run(sandbox: dict, name: str, **extra: object) -> list[str]:
    control = CONTROLS[name]
    args = [
        "canonical",
        "--factor",
        CANDIDATES[name],
        "--candidate",
        CANDIDATES[name],
        "--cohort",
        sandbox["cohort_id"],
        "--snapshot",
        sandbox["snapshot_id"],
        "--config",
        str(CONFIG),
        "--seed",
        "7",
        "--signals",
        str(FIXTURES / control["path"]),
        "--expression",
        control["factor"]["expression"],
    ]
    for key, value in extra.items():
        flag = f"--{key.replace('_', '-')}"
        if value is True:
            args.append(flag)
        else:
            args.extend([flag, str(value)])
    return args


def _payload(stdout: str) -> dict:
    lines = stdout.splitlines()
    return json.loads("\n".join(lines[lines.index("{") :]))


@pytest.mark.parametrize("name", ["funding_carry", "eth_btc_momentum", "white_noise"])
def test_positive_and_noise_controls_reach_expected_verdicts(sandbox, capsys, name: str):
    control = CONTROLS[name]
    assert main(_run(sandbox, name, json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    expected = control["expected"]
    assert payload["state"] == "EVIDENCE_READY"
    assert payload["cost_verdict"] == expected["cost_verdict"]
    assert payload["sample_tier"] == expected["sample_tier"]
    statuses = {entry["stage"]: entry["status"] for entry in payload["stages"]}
    assert statuses["signal_quality"] == "PASS"
    assert statuses["cost_capacity"] == (
        "PASS" if expected["cost_verdict"] == "cost_positive" else "FAIL"
    )


def test_white_noise_is_intercepted_by_the_cost_gate(sandbox, capsys):
    assert main(_run(sandbox, "white_noise", json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    assert payload["cost_verdict"] == "cost_negative"
    assert payload["first_failure"]["stage"] == "cost_capacity"
    assert payload["promotion_verdict"] is None


def test_leakage_control_is_rejected_and_still_registered(sandbox, capsys):
    assert main(_run(sandbox, "future_fill_leakage", json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    assert payload["state"] == "REJECTED"
    assert payload["promotion_verdict"] == "rejected"
    assert payload["first_failure"]["mechanism"] == "lookahead"


def test_full_cohort_records_rejecters_without_double_counting(sandbox, capsys):
    for name in sorted(CONTROLS):
        assert main(_run(sandbox, name, json=True)) == 0
        capsys.readouterr()

    entries = population.registrations(sandbox["reports"], sandbox["cohort_id"])
    assert len(entries) == len(CONTROLS)
    assert {entry.candidate_id for entry in entries} == set(CANDIDATES.values())

    # 诊断性重算：同语义重跑幂等复用，不新增成员（不重复计数）
    assert main(_run(sandbox, "white_noise", json=True)) == 0
    rerun = _payload(capsys.readouterr().out)
    assert rerun["reused"] is True
    assert len(population.registrations(sandbox["reports"], sandbox["cohort_id"])) == len(CONTROLS)

    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 0
    capsys.readouterr()
    verdict = population.load_verdict(sandbox["reports"], sandbox["cohort_id"])
    assert verdict["trial_count"] == len(CONTROLS)
    assert verdict["member_count"] == len(CONTROLS)
    assert verdict["rejected_count"] == 1
    assert verdict["status"] == "FINALIZED"


def test_synthesis_keeps_rejecters_in_the_denominator(sandbox, capsys):
    for name in sorted(CONTROLS):
        assert main(_run(sandbox, name)) == 0
        capsys.readouterr()
    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 0
    capsys.readouterr()
    report = build_synthesis(cohort_id=sandbox["cohort_id"], generated_at=NOW)
    assert report.status == STATUS_FINALIZED
    assert report.funnel["cohort"]["trial_count"] == len(CONTROLS)
    assert report.funnel["cohort"]["rejected_count"] == 1
    assert (
        report.funnel["cohort"]["promotion_verdicts"][CANDIDATES["future_fill_leakage"]]
        == "rejected"
    )
    assert [bucket.mechanism for bucket in report.failures] == ["cost_negative", "lookahead"]


# ---------- T030 [TEST] 层 2 旅程验收：US-002 正式评测与裁决 ----------


def test_us002_canonical_journey_records_members_and_lookahead_layers(sandbox, capsys):
    for name in sorted(CONTROLS):
        assert main(_run(sandbox, name)) == 0
        capsys.readouterr()
    manifests = sorted((sandbox["reports"] / "bench").rglob("manifest.json"))
    assert len(manifests) == len(CONTROLS)
    for path in manifests:
        payload = json.loads(path.read_text(encoding="utf-8"))
        layers = {entry["layer"]: entry for entry in payload["no_lookahead"]["layers"]}
        expected_l1 = "FAIL" if payload["state"] == "REJECTED" else "PASS"
        assert layers["L1"]["status"] == expected_l1
        assert layers["L1"]["evidence_refs"]
        assert layers["L2"]["status"] == "not_yet_available"
        assert layers["L2"]["owner"] == "F006/M3"
        assert layers["L3"]["owner"] == "F006/M3"
        blob = json.dumps(payload)
        assert "final_window" not in blob
        assert "holdout" not in blob
    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 0
    capsys.readouterr()
    report = build_synthesis(cohort_id=sandbox["cohort_id"], generated_at=NOW)
    assert report.status == STATUS_FINALIZED
    assert report.funnel["cohort"]["trial_count"] == len(CONTROLS)
    assert report.funnel["cohort"]["member_count"] == len(CONTROLS)
    assert report.funnel["cohort"]["rejected_count"] == 1


def test_us002_finalize_stays_open_until_every_commitment_is_terminal(sandbox, capsys):
    assert main(_run(sandbox, "funding_carry")) == 0
    capsys.readouterr()
    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 1
    assert "error_code=E_COHORT_FROZEN" in capsys.readouterr().out
    assert population.load_verdict(sandbox["reports"], sandbox["cohort_id"]) is None
    assert build_synthesis(cohort_id=sandbox["cohort_id"], generated_at=NOW).status == "OPEN"


def test_us002_required_estimator_failure_never_yields_promising(sandbox, capsys):
    from alphamill.evaluation.pipeline import evaluate_fixture
    from alphamill.evaluation.run_config import load_run_config
    from alphamill.experiment_store.promotion import PromotionInputs, derive_promotion_verdict
    from alphamill.validation.no_lookahead import build_no_lookahead

    config = load_run_config(CONFIG)
    evaluation = evaluate_fixture(
        config=config,
        times=("2026-09-01T00:00:00Z", "2026-09-01T01:00:00Z"),
        signals=(0.0, 1.0),
        labels=(0.0, 0.01),
        execution_tier="canonical",
        observed_at=NOW,
    )
    assert evaluation.stage_results.evidence_complete is False
    verdict = derive_promotion_verdict(
        PromotionInputs(
            run_state="INCOMPLETE",
            stage_results=evaluation.stage_results,
            sample_tier=evaluation.sample_tier,
            cost_verdict=evaluation.cost_verdict,
            no_lookahead=build_no_lookahead(
                l1_status="PASS", l1_evidence_refs=("sha256:" + "a" * 64,)
            ),
        )
    )
    assert verdict == "incomplete"
    assert verdict != "promising"


def test_canonical_report_wires_member_required_statistics(sandbox, capsys):
    """R1-001 回归：canonical 评测阶段必须接线成员级 HAC IC / block bootstrap。

    删除 `evaluate_fixture` 里的 `member_statistics(...)` 调用后 `required_statistics` 缺失/为空，
    本断言变红——证明统计原语确有生产调用者，而不是只有单测。
    """
    assert main(_run(sandbox, "funding_carry")) == 0
    capsys.readouterr()
    manifest_path = next((sandbox["reports"] / "bench").rglob("manifest.json"))
    report = json.loads((manifest_path.parent / "report.json").read_text(encoding="utf-8"))
    stats = report["required_statistics"]
    assert stats is not None
    assert stats["status"] == "PASS"
    assert stats["periods"] >= 2
    assert {"ic", "hac_se", "t_stat"} <= set(stats["ic"])
    assert {"point", "lower", "upper", "excludes_zero"} <= set(stats["bootstrap"])
    assert stats["bootstrap"]["n_resamples"] == 1000
    assert 0.0 <= stats["p_value"] <= 1.0
    statuses = {entry["stage"]: entry["status"] for entry in report["stage_results"]}
    assert statuses["temporal_stability"] != "INCOMPLETE"


def test_finalize_wires_cohort_level_multiplicity(sandbox, capsys):
    """R1-001 回归：finalize 必须接线 cohort 级 BH-FDR / 有效独立数 / DSR。"""
    for name in sorted(CONTROLS):
        assert main(_run(sandbox, name)) == 0
        capsys.readouterr()
    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 0
    capsys.readouterr()
    verdict = population.load_verdict(sandbox["reports"], sandbox["cohort_id"])
    stats = verdict["cohort_statistics"]["cohort_statistics"]
    assert stats["status"] == "PASS", stats
    assert {"bh", "effective_trials", "dsr"} <= set(stats)
    assert stats["bh"]["alpha"] == 0.05
    assert stats["effective_trials"] >= 1.0


def test_synthesis_carries_effective_trials_and_final_verdicts(sandbox, capsys):
    """R1-108 回归：synthesis 必须带有效独立数，并用 cohort verdict 的最终成员结论。"""
    for name in sorted(CONTROLS):
        assert main(_run(sandbox, name)) == 0
        capsys.readouterr()
    assert main(["finalize-cohort", "--cohort", sandbox["cohort_id"]]) == 0
    capsys.readouterr()
    report = build_synthesis(cohort_id=sandbox["cohort_id"], generated_at=NOW)
    assert report.status == STATUS_FINALIZED
    assert report.effective_trials is not None
    assert report.funnel["cohort"]["effective_trials"] == report.effective_trials
    verdict = population.load_verdict(sandbox["reports"], sandbox["cohort_id"])
    final = verdict["cohort_statistics"]["promotion_verdicts"]
    assert report.funnel["cohort"]["promotion_verdicts"] == final


def test_published_events_match_manifest_digest_and_are_immutable(sandbox, capsys):
    """R1-004 回归：已发布批次的 events_digest 必须与实际事件一致，且复用不得改动它。

    修复前 canonical 在 publish 之后追加 evaluation.registered，导致 (a) 事件文件与
    manifest.events_digest 不符，(b) 已发布的不可变证据被就地修改。
    """
    from alphamill.evaluation.events import events_digest, read_events

    assert main(_run(sandbox, "funding_carry")) == 0
    capsys.readouterr()
    manifest_path = next((sandbox["reports"] / "bench").rglob("manifest.json"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    events_path = manifest_path.parent / "events.jsonl"
    stored = read_events(events_path)
    assert events_digest(stored) == manifest["events_digest"]
    assert any(event.type == "evaluation.registered" for event in stored)

    before = events_path.read_bytes()
    assert main(_run(sandbox, "funding_carry")) == 0
    capsys.readouterr()
    assert events_path.read_bytes() == before
