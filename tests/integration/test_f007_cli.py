"""T006 / `IR-001`·`IR-003`·`UX-001`·`AC-008`·`AC-011`：preview CLI 契约与稳定错误码。

覆盖：成功首屏固定字段（快照式锁定）、`--json` 结构化 payload 不含 Agent/preview 可读禁区字段、
preview 恒无 `promotion_verdict`、用法/领域错误的退出码与稳定 `error_code`、`--latest` 先冻结并
发布快照、`source=placeholder` 只在 preview 被标注、preview 不触碰 canonical/留出命名空间、
白噪声负控制在成本门判负。
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import registry, symbol_map
from alphamill.evaluation.cli import ERROR_CODES, main
from alphamill.evaluation.universe_ledger import UniverseMember, publish_universe
from alphamill.experiment_store import research_snapshot as snapshot_store

pytestmark = pytest.mark.integration

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "f007"
CONFIG = FIXTURES / "method-v1.json"
POSITIVE = FIXTURES / "controls" / "funding_carry.csv"
NOISE = FIXTURES / "controls" / "white_noise.csv"
DATASET = "derivatives_funding_rates"
DAY = "2026-09-01"
VERSION = "v2026.09.01"
CUTOFF = "2026-09-01T12:00:00Z"
FACTOR_REF = "factor_sha256:" + "1" * 64
CALENDAR = {
    "schema_version": 1,
    "timezone": "UTC",
    "windows": [{"start": "2026-09-01T00:00:00Z", "end": "2026-09-30T00:00:00Z"}],
}
FORBIDDEN_TOKENS = ("final_window", "holdout")


def _member() -> UniverseMember:
    return UniverseMember(
        exchange="binance",
        market_type="perp",
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT-PERP",
        valid_from="2026-08-01T00:00:00Z",
        valid_to="",
        reason="listed",
        universe_id="uni-1",
    )


def _lake(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "lake"
    spec = registry.require_dataset(DATASET)
    payload = b"x" * 10
    rel = f"{DATASET}/exchange=binance/pair=BTC-USDT/date={DAY}.r1.parquet"
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    partition = {
        "logical_partition_key": {"exchange": "binance", "pair": "BTC-USDT", "date": DAY},
        "path": rel,
        "rows": 10,
        "time_min": f"{DAY}T00:00:00Z",
        "time_max": f"{DAY}T23:59:00Z",
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
    universe_digest = publish_universe([_member()], root)
    return root, sm_digest, universe_digest


@pytest.fixture()
def env(tmp_path, monkeypatch) -> dict:
    lake, symbol_map_digest, universe_digest = _lake(tmp_path)
    reports = tmp_path / "reports"
    calendar_path = tmp_path / "calendar-v1.json"
    calendar_path.write_text(json.dumps(CALENDAR), encoding="utf-8")
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(lake))
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(reports))
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
    return {
        "lake": lake,
        "reports": reports,
        "symbol_map_digest": symbol_map_digest,
        "universe_digest": universe_digest,
        "calendar_path": calendar_path,
        "snapshot_id": snapshot.snapshot_id,
    }


def _args(env: dict, signals: Path = POSITIVE, **extra: object) -> list[str]:
    args = [
        "preview",
        "--factor",
        FACTOR_REF,
        "--config",
        str(CONFIG),
        "--seed",
        "7",
        "--signals",
        str(signals),
        "--snapshot",
        env["snapshot_id"],
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


def _assert_no_forbidden_keys(node: object) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            assert not any(token in key for token in FORBIDDEN_TOKENS), key
            _assert_no_forbidden_keys(value)
    elif isinstance(node, list):
        for item in node:
            _assert_no_forbidden_keys(item)


def test_preview_succeeds_on_positive_control(env, capsys):
    assert main(_args(env)) == 0
    out = capsys.readouterr().out
    assert "tier=preview cohort=cohort_sha256:" in out
    assert f"data={env['snapshot_id']}" in out
    assert "state=PREVIEW_DONE" in out
    assert "cost_verdict=cost_positive" in out
    assert "promotion_verdict=None" in out
    assert "first_failure=none" in out


def test_first_screen_field_order_is_locked(env, capsys):
    main(_args(env))
    lines = capsys.readouterr().out.splitlines()[:10]
    keys = [line.split("=", 1)[0].split()[0] for line in lines]
    assert keys == [
        "tier",
        "experiment_id",
        "data",
        "code",
        "state",
        "cost_verdict",
        "promotion_verdict",
        "stages",
        "approximation",
        "first_failure",
    ]
    assert lines[0].split()[0] == "tier=preview"
    assert "sample_tier=" in lines[5]
    assert lines[7].startswith("stages=signal_quality:")
    assert lines[7].count(" ") == 4


def test_json_payload_is_structured_and_free_of_agent_forbidden_fields(env, capsys):
    assert main(_args(env, json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    assert set(payload) >= {
        "execution_tier",
        "experiment_id",
        "cohort_id",
        "research_snapshot_id",
        "code_build_digest",
        "state",
        "cost_verdict",
        "sample_tier",
        "promotion_verdict",
        "stages",
        "approximation",
        "first_failure",
    }
    assert payload["execution_tier"] == "preview"
    assert payload["promotion_verdict"] is None
    _assert_no_forbidden_keys(payload)


def test_stage_payload_lists_all_five_stages_in_frozen_order(env, capsys):
    main(_args(env, json=True))
    payload = _payload(capsys.readouterr().out)
    assert [entry["stage"] for entry in payload["stages"]] == [
        "signal_quality",
        "portfolio_transform",
        "cost_capacity",
        "temporal_stability",
        "execution_implementation",
    ]
    assert payload["stages"][1]["status"] == "NOT_APPLICABLE"
    assert payload["stages"][1]["reason"]


def test_white_noise_control_is_not_cost_positive(env, capsys):
    assert main(_args(env, signals=NOISE, json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    assert payload["cost_verdict"] == "cost_negative"
    assert payload["first_failure"]["stage"] == "cost_capacity"


def test_placeholder_signal_source_is_annotated_in_preview(env, capsys):
    assert main(_args(env, signal_source="placeholder", json=True)) == 0
    payload = _payload(capsys.readouterr().out)
    assert payload["approximation"] == {
        "is_approximate": True,
        "reduced_dimensions": [],
        "signal_source": "placeholder",
    }
    assert payload["signal_provenance"]["source_distribution"] == {"placeholder": 40}


def test_preview_derives_stable_ephemeral_cohort(env, capsys):
    main(_args(env, json=True))
    first = _payload(capsys.readouterr().out)
    main(_args(env, json=True))
    second = _payload(capsys.readouterr().out)
    assert first["cohort_id"] == second["cohort_id"]
    assert first["cohort_id"].startswith("cohort_sha256:")
    assert first["experiment_id"] == second["experiment_id"]


def test_preview_does_not_touch_canonical_or_holdout_namespaces(env):
    assert main(_args(env)) == 0
    reports = env["reports"]
    assert not (reports / "bench").exists()
    assert not (reports / "cohorts").exists()
    assert not (reports / "holdout_budget" / "ledger.jsonl").exists()


def test_unknown_snapshot_fails_closed_with_stable_code(env, capsys):
    args = _args(env)
    args[args.index("--snapshot") + 1] = "sha256:" + "0" * 64
    assert main(args) == 1
    assert "error_code=E_INPUT_INVALID" in capsys.readouterr().out


def test_tampered_snapshot_is_reported_as_digest_mismatch(env, capsys):
    manifest_path = env["reports"] / "research_snapshots" / env["snapshot_id"] / "manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["cutoff_time"] = "2027-01-01T00:00:00Z"
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    assert main(_args(env)) == 1
    assert "error_code=E_DATA_DIGEST_MISMATCH" in capsys.readouterr().out


def test_missing_config_fails_closed(env, capsys):
    args = _args(env)
    args[args.index("--config") + 1] = str(env["reports"] / "nope.json")
    assert main(args) == 1
    assert "error_code=E_INPUT_INVALID" in capsys.readouterr().out


def test_snapshot_and_latest_are_mutually_exclusive(env):
    with pytest.raises(SystemExit) as excinfo:
        main(_args(env, latest=DATASET))
    assert excinfo.value.code == 2


def test_latest_mode_freezes_and_publishes_a_snapshot(env, capsys):
    args = [
        "preview",
        "--factor",
        FACTOR_REF,
        "--config",
        str(CONFIG),
        "--seed",
        "7",
        "--signals",
        str(POSITIVE),
        "--latest",
        DATASET,
        "--cutoff",
        CUTOFF,
        "--symbol-map",
        env["symbol_map_digest"],
        "--universe",
        env["universe_digest"],
        "--calendar",
        str(env["calendar_path"]),
        "--json",
    ]
    assert main(args) == 0
    payload = _payload(capsys.readouterr().out)
    assert (env["reports"] / "research_snapshots" / payload["research_snapshot_id"]).is_dir()
    assert payload["approximation"]["is_approximate"] is False
    assert payload["signal_provenance"]["source_distribution"] == {"real": 40}


def test_every_emitted_error_code_is_registered(env, capsys):
    args = _args(env)
    args[args.index("--snapshot") + 1] = "sha256:" + "0" * 64
    main(args)
    code = capsys.readouterr().out.splitlines()[0].removeprefix("error_code=")
    assert code in ERROR_CODES
