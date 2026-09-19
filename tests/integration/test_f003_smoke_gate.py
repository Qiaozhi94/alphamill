"""F003 FR-006/AC-007：冒烟闸门、降级阶梯与 manifest 契约。"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from alphamill.factor_factory.canonical import canonical_json_bytes
from alphamill.factor_factory.errors import SchemaValidationError, UnknownSchemaVersionError
from alphamill.factor_factory.generators.base import (
    DEFAULT_WINDOW_PRESET,
    GenerationCounts,
    RejectionCounts,
    Window,
)
from alphamill.factor_factory.generators.smoke_gate import (
    FunnelObligations,
    RewardSpotCheck,
    SmokeManifest,
    default_smoke_config,
    default_smoke_window,
    judge_day1,
    judge_day2,
    ladder_from_l1,
    load_smoke_manifest,
    request_revert_to_l0,
    write_smoke_manifest,
)

pytestmark = pytest.mark.integration

NOW = datetime(2026, 9, 19, 12, 30, tzinfo=UTC)


def _counts() -> GenerationCounts:
    return GenerationCounts(
        proposed=15,
        rejected=RejectionCounts(
            unregistered_op=1,
            lookahead=2,
            reachability=3,
            duplicate_definition=4,
        ),
        registered=5,
    )


def _spot_check() -> RewardSpotCheck:
    return RewardSpotCheck(
        turnover_prefilter_applied=True,
        reachability_prefilter_applied=True,
        zero_trade_bias_observed=False,
        notes="首批候选抽查记录",
    )


def _day1(*, passed: bool, tier_before: str = "L0") -> SmokeManifest:
    return judge_day1(
        ppo_epoch_ok=passed,
        counts=_counts(),
        reward_spot_check=_spot_check(),
        tier_before=tier_before,
        now=NOW,
    )


def test_day1_failure_downgrades_to_l1_and_names_trigger() -> None:
    # Given: day 1 has not completed a PPO epoch.
    # When: the day-1 gate is judged.
    manifest = _day1(passed=False)

    # Then: the failed criterion is the downgrade trigger.
    assert manifest.verdict == "L1_downgraded"
    assert manifest.tier_after == "L1"
    assert manifest.trigger == manifest.criteria[0].name
    assert manifest.criteria[0].passed is False


def test_day1_success_locks_l0() -> None:
    # Given/When: day 1 completed a PPO epoch and is judged.
    manifest = _day1(passed=True)

    # Then: L0 is locked without a trigger.
    assert manifest.verdict == "L0_locked"
    assert manifest.tier_after == "L0"
    assert manifest.trigger is None


def test_day2_ic_parity_failure_downgrades_to_l1() -> None:
    # Given/When: vendor and reference IC do not match within tolerance.
    manifest = judge_day2(
        ic_parity_ok=False,
        counts=_counts(),
        reward_spot_check=_spot_check(),
        tier_before="L0",
        now=NOW,
    )

    # Then: the parity criterion triggers L1.
    assert manifest.verdict == "L1_downgraded"
    assert manifest.tier_after == "L1"
    assert manifest.trigger == manifest.criteria[0].name


def test_day2_ic_parity_success_locks_l0() -> None:
    # Given/When: vendor and reference IC match within tolerance.
    manifest = judge_day2(
        ic_parity_ok=True,
        counts=_counts(),
        reward_spot_check=_spot_check(),
        tier_before="L1",
        now=NOW,
    )

    # Then: L0 is locked without a trigger.
    assert manifest.verdict == "L0_locked"
    assert manifest.tier_after == "L0"
    assert manifest.trigger is None


def test_two_day_judges_never_emit_l2() -> None:
    # Given: every pass/fail state and every possible incoming tier.
    manifests = tuple(
        judge(
            **{argument: passed},
            counts=_counts(),
            reward_spot_check=_spot_check(),
            tier_before=tier,
            now=NOW,
        )
        for judge, argument in ((judge_day1, "ppo_epoch_ok"), (judge_day2, "ic_parity_ok"))
        for passed in (False, True)
        for tier in ("L0", "L1", "L2")
    )

    # When/Then: the time-box result remains strictly L0 or L1.
    assert {manifest.tier_after for manifest in manifests} == {"L0", "L1"}


def test_obligations_preserve_full_generator_funnel_and_f007_placeholder() -> None:
    # Given/When: a day-1 manifest is produced from all rejection categories.
    obligations = _day1(passed=True).obligations

    # Then: generation counts remain complete and downstream work is explicitly deferred.
    assert obligations.generator_counts == {
        "proposed": 15,
        "rejected": {
            "unregistered_op": 1,
            "lookahead": 2,
            "reachability": 3,
            "duplicate_definition": 4,
        },
        "registered": 5,
    }
    assert obligations.downstream == {"owner": "F007", "state": "not_yet_available"}

    with pytest.raises(SchemaValidationError):
        FunnelObligations(generator_counts={}, downstream={"owner": "F007", "state": 0})


def test_l1_ladder_requires_two_weeks_and_documented_trigger() -> None:
    # Given/When/Then: one week never reaches L2.
    assert (
        ladder_from_l1(
            consecutive_weeks=1,
            weekly_candidates=[49],
            zero_candidates_through_lookahead_audit=True,
        )
        == "L1"
    )

    # Given/When/Then: two weeks with a sub-50 week reaches L2.
    assert (
        ladder_from_l1(
            consecutive_weeks=2,
            weekly_candidates=[50, 49],
            zero_candidates_through_lookahead_audit=False,
        )
        == "L2"
    )

    # Given/When/Then: healthy counts and audit stay at L1.
    assert (
        ladder_from_l1(
            consecutive_weeks=2,
            weekly_candidates=[50, 51],
            zero_candidates_through_lookahead_audit=False,
        )
        == "L1"
    )


def test_revert_to_l0_requires_a_new_timebox_record() -> None:
    # Given/When/Then: direct reversion is rejected.
    with pytest.raises(SchemaValidationError):
        request_revert_to_l0(new_timebox_record=None)

    # Given/When/Then: a fresh time-box record authorizes L0.
    assert request_revert_to_l0(new_timebox_record=_day1(passed=True)) == "L0"


def test_manifest_round_trip_is_canonical_and_atomic(tmp_path: Path) -> None:
    # Given: a nested destination and a complete smoke manifest.
    path = tmp_path / "smoke" / "day-1.json"
    manifest = _day1(passed=True)

    # When: the manifest is atomically published and loaded.
    written = write_smoke_manifest(path, manifest)
    restored = load_smoke_manifest(path)

    # Then: the value round-trips, JSON is canonical, and no temp artifact remains.
    assert written == path
    assert restored == manifest
    assert path.read_bytes() == canonical_json_bytes(json.loads(path.read_bytes()))
    assert tuple(path.parent.iterdir()) == (path,)


def test_unknown_manifest_schema_version_is_rejected(tmp_path: Path) -> None:
    # Given: a valid manifest whose schema version is changed to an unknown value.
    path = write_smoke_manifest(tmp_path / "smoke.json", _day1(passed=True))
    payload = json.loads(path.read_bytes())
    payload["schema_version"] = 2
    path.write_bytes(canonical_json_bytes(payload))

    # When/Then: loading fails closed rather than guessing compatibility.
    with pytest.raises(UnknownSchemaVersionError):
        load_smoke_manifest(path)


def test_default_smoke_config_and_window_are_valid() -> None:
    # Given/When: defaults are constructed for a UTC cutoff.
    config = default_smoke_config()
    window = default_smoke_window(cutoff_time=NOW)

    # Then: the config selects the built-in preset and Window invariants hold.
    assert config["window_preset"] == DEFAULT_WINDOW_PRESET
    assert isinstance(window, Window)
    assert window.start.tzinfo is UTC
    assert window.end == NOW
    assert window.start < window.end
    assert window.resample == "1h"
