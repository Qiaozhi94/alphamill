"""ADR-0001 smoke gate and its separately evaluated downgrade ladder.

The two-day time-box judges only ``L0_locked`` or ``L1_downgraded`` and can
never emit L2. L1-to-L2 evaluation is isolated in :func:`ladder_from_l1`; its
two-week and 50-candidate constants come from ADR-0001's downgrade criteria.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar, Final, Literal, TypeAlias, assert_never

from pydantic import ConfigDict, JsonValue, TypeAdapter, ValidationError

from alphamill.factor_factory.canonical import canonical_json_bytes, parse_utc, utc_iso
from alphamill.factor_factory.errors import (
    RunStoreError,
    SchemaValidationError,
    UnknownSchemaVersionError,
)
from alphamill.factor_factory.generators.base import (
    DEFAULT_WINDOW_PRESET,
    GenerationCounts,
    Window,
)

TierLevel: TypeAlias = Literal["L0", "L1", "L2"]
JSONValue: TypeAlias = JsonValue
_SmokeVerdict: TypeAlias = Literal["L0_locked", "L1_downgraded"]
SMOKE_SCHEMA_VERSION: Final = 1
L1_TO_L2_MIN_WEEKS: Final = 2
L1_TO_L2_WEEKLY_CANDIDATE_FLOOR: Final = 50

_DAY1_CRITERION: Final = "ran >=1 PPO epoch"
_DAY2_CRITERION: Final = "vendor tensor IC vs pandas reference parity within tolerance"
_COUNT_FIELDS: Final = frozenset(("proposed", "rejected", "registered"))
_REJECTION_FIELDS: Final = frozenset(
    ("unregistered_op", "lookahead", "reachability", "duplicate_definition")
)
_COUNTS_ADAPTER: Final = TypeAdapter(GenerationCounts)


@dataclass(frozen=True, kw_only=True)
class SmokeCriterion:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    name: str
    passed: bool
    detail: str
    evidence: str


@dataclass(frozen=True, kw_only=True)
class FunnelObligations:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    generator_counts: dict[str, JSONValue]
    downstream: dict[str, JSONValue]

    def __post_init__(self) -> None:
        rejected = self.generator_counts.get("rejected")
        valid_shape = (
            set(self.generator_counts) == _COUNT_FIELDS
            and isinstance(rejected, dict)
            and set(rejected) == _REJECTION_FIELDS
        )
        if not valid_shape:
            raise SchemaValidationError(
                "generator_counts must contain the complete rejection funnel"
            )
        try:
            _COUNTS_ADAPTER.validate_json(
                canonical_json_bytes(self.generator_counts),
                strict=True,
            )
        except ValidationError as exc:
            raise SchemaValidationError("generator_counts is invalid") from exc
        if self.downstream != {"owner": "F007", "state": "not_yet_available"}:
            raise SchemaValidationError(
                "downstream must identify F007 with state='not_yet_available'"
            )


@dataclass(frozen=True, kw_only=True)
class RewardSpotCheck:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    turnover_prefilter_applied: bool
    reachability_prefilter_applied: bool
    zero_trade_bias_observed: bool
    notes: str


@dataclass(frozen=True, kw_only=True)
class SmokeManifest:
    __pydantic_config__: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

    schema_version: int
    day: int
    generated_at: datetime
    criteria: tuple[SmokeCriterion, ...]
    obligations: FunnelObligations
    reward_spot_check: RewardSpotCheck
    tier_before: TierLevel
    tier_after: TierLevel
    verdict: Literal["L0_locked", "L1_downgraded"]
    trigger: str | None

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != SMOKE_SCHEMA_VERSION:
            raise SchemaValidationError("SmokeManifest.schema_version must be 1")
        if type(self.day) is not int or self.day not in (1, 2):
            raise SchemaValidationError("SmokeManifest.day must be 1 or 2")
        if self.generated_at.tzinfo is None or self.generated_at.utcoffset() != UTC.utcoffset(
            self.generated_at
        ):
            raise SchemaValidationError("SmokeManifest.generated_at must be timezone-aware UTC")
        failed = frozenset(item.name for item in self.criteria if not item.passed)
        match self.verdict:
            case "L0_locked":
                valid = self.tier_after == "L0" and self.trigger is None and not failed
            case "L1_downgraded":
                valid = self.tier_after == "L1" and self.trigger in failed
            case unreachable:
                assert_never(unreachable)
        if not self.criteria or not valid:
            raise SchemaValidationError("SmokeManifest verdict, tier_after, and trigger disagree")


@dataclass(frozen=True, slots=True)
class _Judgement:
    day: Literal[1, 2]
    criterion: SmokeCriterion
    tier_before: TierLevel
    now: datetime

    def manifest(
        self,
        counts: GenerationCounts,
        reward_spot_check: RewardSpotCheck,
    ) -> SmokeManifest:
        tier_after: TierLevel = "L0" if self.criterion.passed else "L1"
        verdict: _SmokeVerdict = "L0_locked" if self.criterion.passed else "L1_downgraded"
        return SmokeManifest(
            schema_version=SMOKE_SCHEMA_VERSION,
            day=self.day,
            generated_at=parse_utc(utc_iso(self.now), field="now"),
            criteria=(self.criterion,),
            obligations=FunnelObligations(
                generator_counts=_counts_payload(counts),
                downstream={"owner": "F007", "state": "not_yet_available"},
            ),
            reward_spot_check=reward_spot_check,
            tier_before=self.tier_before,
            tier_after=tier_after,
            verdict=verdict,
            trigger=None if self.criterion.passed else self.criterion.name,
        )


_SMOKE_ADAPTER: Final = TypeAdapter(SmokeManifest)


def default_smoke_config() -> dict[str, JSONValue]:
    return {"window_preset": DEFAULT_WINDOW_PRESET}


def default_smoke_window(*, cutoff_time: datetime) -> Window:
    return Window.from_preset(DEFAULT_WINDOW_PRESET, cutoff_time=cutoff_time)


def judge_day1(
    *,
    ppo_epoch_ok: bool,
    counts: GenerationCounts,
    reward_spot_check: RewardSpotCheck,
    tier_before: TierLevel,
    now: datetime,
) -> SmokeManifest:
    criterion = SmokeCriterion(
        name=_DAY1_CRITERION,
        passed=ppo_epoch_ok,
        detail=f"ppo_epoch_completed={str(ppo_epoch_ok).lower()}",
        evidence="run.json#/training/ppo_epochs_completed",
    )
    return _Judgement(1, criterion, tier_before, now).manifest(counts, reward_spot_check)


def judge_day2(
    *,
    ic_parity_ok: bool,
    counts: GenerationCounts,
    reward_spot_check: RewardSpotCheck,
    tier_before: TierLevel,
    now: datetime,
) -> SmokeManifest:
    criterion = SmokeCriterion(
        name=_DAY2_CRITERION,
        passed=ic_parity_ok,
        detail=f"ic_parity_within_tolerance={str(ic_parity_ok).lower()}",
        evidence="ic-parity.json#/vendor_vs_reference",
    )
    return _Judgement(2, criterion, tier_before, now).manifest(counts, reward_spot_check)


def ladder_from_l1(
    *,
    consecutive_weeks: int,
    weekly_candidates: list[int],
    zero_candidates_through_lookahead_audit: bool,
) -> TierLevel:
    below_floor = (
        min(weekly_candidates, default=L1_TO_L2_WEEKLY_CANDIDATE_FLOOR)
        < L1_TO_L2_WEEKLY_CANDIDATE_FLOOR
    )
    if consecutive_weeks >= L1_TO_L2_MIN_WEEKS and (
        below_floor or zero_candidates_through_lookahead_audit
    ):
        return "L2"
    return "L1"


def request_revert_to_l0(*, new_timebox_record: SmokeManifest | None) -> TierLevel:
    if new_timebox_record is None:
        raise SchemaValidationError("reverting to L0 requires a new smoke time-box record")
    return "L0"


def write_smoke_manifest(path: Path, manifest: SmokeManifest) -> Path:
    payload: JSONValue = json.loads(_SMOKE_ADAPTER.dump_json(manifest))
    if not isinstance(payload, dict):
        raise SchemaValidationError("SmokeManifest must serialize to a JSON object")
    payload["generated_at"] = utc_iso(manifest.generated_at)
    temporary: Path | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(canonical_json_bytes(payload))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise RunStoreError(f"cannot publish smoke manifest: {path}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def load_smoke_manifest(path: Path) -> SmokeManifest:
    try:
        content = path.read_bytes()
        payload: JSONValue = json.loads(content)
    except OSError as exc:
        raise RunStoreError(f"cannot read smoke manifest: {path}") from exc
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise SchemaValidationError(f"invalid smoke manifest JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise SchemaValidationError("smoke manifest must be a JSON object")
    version = payload.get("schema_version")
    if type(version) is not int:
        raise SchemaValidationError("schema_version must be an integer")
    if version != SMOKE_SCHEMA_VERSION:
        raise UnknownSchemaVersionError(f"unsupported smoke schema_version: {version}")
    try:
        return _SMOKE_ADAPTER.validate_json(content, strict=True)
    except ValidationError as exc:
        raise SchemaValidationError(f"invalid smoke manifest schema: {path}") from exc


def _counts_payload(counts: GenerationCounts) -> dict[str, JSONValue]:
    payload: JSONValue = json.loads(json.dumps(asdict(counts), allow_nan=False))
    if not isinstance(payload, dict):
        raise SchemaValidationError("GenerationCounts must serialize to a JSON object")
    return payload
