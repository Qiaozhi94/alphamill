"""F003 人工种子测试：FR-001、DR-003、AC-001、AC-009。"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.generators.base import (
    GenerationRequest,
    RejectionCounts,
    Window,
)
from alphamill.factor_factory.generators.binding import SnapshotRefBinding
from alphamill.factor_factory.generators.manual.seeds import (
    MANUAL_FACTOR_ORDER,
    MANUAL_GENERATOR_VERSION,
    ManualGenerator,
)

FIXED_TIME = datetime(2026, 9, 19, 12, tzinfo=UTC)
FEATURE_MAP = {"close": 0, "funding_rate": 1, "basis_pct": 2, "open_interest": 3}
EXPRESSIONS = {
    "funding_carry": ("feature:funding_rate", "neg"),
    "basis_reversion": ("feature:basis_pct", "neg"),
    "open_interest_change": ("feature:open_interest", "pct_change:24"),
    "cross_sectional_momentum": ("feature:close", "return:168", "cs_rank"),
    "realized_volatility": ("feature:close", "return:1", "rolling_std:168", "neg"),
}
DATA_COLUMNS = {
    "funding_carry": ["funding_rate"],
    "basis_reversion": ["basis_pct"],
    "open_interest_change": ["open_interest"],
    "cross_sectional_momentum": ["close"],
    "realized_volatility": ["close"],
}
SCOPES = {
    "funding_carry": "time_series",
    "basis_reversion": "time_series",
    "open_interest_change": "time_series",
    "cross_sectional_momentum": "cross_sectional",
    "realized_volatility": "time_series",
}


def _request(
    tmp_path: Path,
    *,
    quota: int,
    generator: str = "manual",
    seed: int = 17,
) -> GenerationRequest:
    cutoff = datetime(2026, 9, 19, tzinfo=UTC)
    return GenerationRequest(
        generator=generator,
        binding=SnapshotRefBinding(
            mode="snapshot",
            research_snapshot_id=f"snapshot-{tmp_path.name}",
        ),
        seed=seed,
        window=Window(
            start=cutoff - timedelta(days=730),
            end=cutoff,
            resample="1h",
        ),
        config={},
        quota=quota,
    )


def _time_series_frame() -> pd.DataFrame:
    index = pd.date_range("2026-01-01", periods=200, freq="h", tz="UTC")
    steps = range(1, len(index) + 1)
    return pd.DataFrame(
        {
            "close": [float(step) for step in steps],
            "funding_rate": [step / 10_000 for step in steps],
            "basis_pct": [step / 1_000 for step in steps],
            "open_interest": [1_000.0 + step for step in steps],
        },
        index=index,
    )


def _cross_sectional_frame() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", periods=200, freq="h", tz="UTC")
    index = pd.MultiIndex.from_product(
        [timestamps, ("BTC/USDT", "ETH/USDT")],
        names=("timestamp", "pair"),
    )
    return pd.DataFrame(
        {
            "close": [float(step + 1) for step in range(len(index))],
            "__in_universe__": True,
        },
        index=index,
    )


def test_produce_returns_five_manual_factors_in_fixed_order(tmp_path: Path) -> None:
    generator = ManualGenerator(run_id="manual-run", clock=lambda: FIXED_TIME)

    result = generator.produce(_request(tmp_path, quota=8))

    assert [factor.name for factor in result.factors] == list(MANUAL_FACTOR_ORDER)
    assert [factor.hypothesis_id for factor in result.factors] == list(MANUAL_FACTOR_ORDER)
    assert result.counts.proposed == 5
    assert result.counts.registered == 5
    assert result.counts.rejected == RejectionCounts()
    assert result.pool is None
    assert result.device == "cpu"
    assert result.tier_level == "manual"
    assert result.run_id == "manual-run"


def test_produce_truncates_fixed_order_to_quota(tmp_path: Path) -> None:
    generator = ManualGenerator(run_id="quota-run", clock=lambda: FIXED_TIME)

    result = generator.produce(_request(tmp_path, quota=2))

    assert [factor.name for factor in result.factors] == list(MANUAL_FACTOR_ORDER[:2])
    assert result.counts.proposed == 2
    assert result.counts.registered == 2
    assert result.counts.rejected == RejectionCounts()


def test_each_manual_factor_has_fixed_definition_and_real_hypothesis(tmp_path: Path) -> None:
    generator = ManualGenerator(run_id="definition-run", clock=lambda: FIXED_TIME)

    factors = generator.produce(_request(tmp_path, quota=5)).factors

    for factor in factors:
        assert factor.hypothesis_id == factor.name
        assert factor.hypothesis_id != "mechanism_unknown"
        assert factor.generator == "manual"
        assert factor.meta["generator_version"] == MANUAL_GENERATOR_VERSION
        assert factor.meta["expression"] == list(EXPRESSIONS[factor.name])
        assert factor.meta["feature_map"] == FEATURE_MAP
        assert factor.data_columns == DATA_COLUMNS[factor.name]
        assert factor.scope == SCOPES[factor.name]


def test_factor_identity_ignores_run_clock_and_seed_provenance(tmp_path: Path) -> None:
    first = ManualGenerator(run_id="run-a", clock=lambda: FIXED_TIME).produce(
        _request(tmp_path, quota=5, seed=7)
    )
    second = ManualGenerator(
        run_id="run-b",
        clock=lambda: FIXED_TIME + timedelta(days=1),
    ).produce(_request(tmp_path, quota=5, seed=99))

    first_ids = sorted(factor.factor_id for factor in first.factors)
    second_ids = sorted(factor.factor_id for factor in second.factors)
    assert first_ids == second_ids


def test_each_manual_factor_compute_is_executable(tmp_path: Path) -> None:
    generator = ManualGenerator(run_id="compute-run", clock=lambda: FIXED_TIME)
    factors = generator.produce(_request(tmp_path, quota=5)).factors

    for factor in factors:
        frame = (
            _cross_sectional_frame() if factor.scope == "cross_sectional" else _time_series_frame()
        )

        result = factor.compute(frame)

        assert isinstance(result, pd.Series)
        assert result.index.equals(frame.index)
        assert result.notna().any()


def test_produce_rejects_request_for_another_generator(tmp_path: Path) -> None:
    generator = ManualGenerator(run_id="wrong-generator", clock=lambda: FIXED_TIME)

    with pytest.raises(SchemaValidationError, match="manual"):
        generator.produce(_request(tmp_path, quota=5, generator="alphagen"))
