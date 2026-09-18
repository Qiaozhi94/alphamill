"""F003 生成器契约测试：AC-001 / IR-002 约束统一接口与结论字段边界。"""

from datetime import UTC, datetime, timedelta

import pytest

from alphamill.factor_factory.errors import ConclusionFieldError, SchemaValidationError
from alphamill.factor_factory.factor import FactorDef, FactorInput, FactorOutput
from alphamill.factor_factory.generators.base import (
    DEFAULT_WINDOW_PRESET,
    GenerationCounts,
    GenerationRequest,
    GenerationResult,
    Generator,
    RejectionCounts,
    Window,
    reject_conclusion_fields,
)


def _first_column(frame: FactorInput) -> FactorOutput:
    return frame.iloc[:, 0]


def _factor(*, generator: str) -> FactorDef:
    return FactorDef(
        factor_id=f"{generator}_example",
        hypothesis_id="mechanism_unknown",
        name="example",
        generator=generator,
        scope="time_series",
        params={},
        compute=_first_column,
        data_columns=["close"],
        meta={},
    )


def _empty_counts() -> GenerationCounts:
    return GenerationCounts(proposed=0, rejected=RejectionCounts(), registered=0)


def _request(*, quota: int) -> GenerationRequest:
    cutoff = datetime(2026, 9, 18, tzinfo=UTC)
    return GenerationRequest(
        generator="stub",
        binding=None,
        seed=17,
        window=Window.from_preset(DEFAULT_WINDOW_PRESET, cutoff_time=cutoff),
        config={},
        quota=quota,
    )


class _StubGenerator:
    name = "stub"

    def produce(self, request: GenerationRequest) -> GenerationResult:
        return GenerationResult(
            run_id=f"{self.name}-{request.seed}",
            factors=[],
            pool=None,
            counts=_empty_counts(),
            device="cpu",
            tier_level="L0",
        )


@pytest.mark.parametrize("field", ["ic", "verdict", "promotion_verdict"])
def test_reject_conclusion_fields_rejects_each_top_level_field(field: str) -> None:
    with pytest.raises(ConclusionFieldError) as exc_info:
        reject_conclusion_fields({field: 1}, context="backend result")

    assert field in str(exc_info.value)
    assert "backend result" in str(exc_info.value)


def test_reject_conclusion_fields_accepts_clean_payload() -> None:
    reject_conclusion_fields({"factor_id": "manual_example"}, context="backend result")


def test_reject_conclusion_fields_does_not_descend_into_params() -> None:
    reject_conclusion_fields({"params": {"ic": 1}}, context="factor definition")


def test_window_preset_expands_to_end_exclusive_730_day_range() -> None:
    cutoff = datetime(2026, 9, 18, 6, 30, tzinfo=UTC)

    window = Window.from_preset(DEFAULT_WINDOW_PRESET, cutoff_time=cutoff)

    assert window.start == cutoff - timedelta(days=730)
    assert window.end == cutoff
    assert window.start < window.end
    assert window.resample == "1h"


def test_window_rejects_naive_datetime() -> None:
    with pytest.raises(SchemaValidationError, match="start"):
        Window(
            start=datetime(2024, 9, 18),
            end=datetime(2026, 9, 18, tzinfo=UTC),
            resample="1h",
        )


def test_window_rejects_unknown_preset() -> None:
    with pytest.raises(SchemaValidationError, match="unknown"):
        Window.from_preset("unknown", cutoff_time=datetime(2026, 9, 18, tzinfo=UTC))


def test_generation_counts_accepts_consistent_arithmetic() -> None:
    rejected = RejectionCounts(
        unregistered_op=1,
        lookahead=2,
        reachability=3,
        duplicate_definition=4,
    )

    counts = GenerationCounts(proposed=15, rejected=rejected, registered=5)

    assert counts.proposed == 15


def test_generation_counts_rejects_inconsistent_arithmetic() -> None:
    with pytest.raises(SchemaValidationError, match="proposed"):
        GenerationCounts(proposed=2, rejected=RejectionCounts(lookahead=1), registered=2)


def test_generation_counts_rejects_negative_values() -> None:
    with pytest.raises(SchemaValidationError, match="non-negative"):
        GenerationCounts(proposed=-1, rejected=RejectionCounts(), registered=0)


def test_generation_result_rejects_pool_with_wrong_generator() -> None:
    with pytest.raises(SchemaValidationError, match="pool"):
        GenerationResult(
            run_id="run-invalid-pool",
            factors=[],
            pool=_factor(generator="manual"),
            counts=_empty_counts(),
            device="cpu",
            tier_level="L0",
        )


def test_generation_result_accepts_absent_pool() -> None:
    result = GenerationResult(
        run_id="run-no-pool",
        factors=[],
        pool=None,
        counts=_empty_counts(),
        device="cpu",
        tier_level="L0",
    )

    assert result.pool is None


def test_generation_result_accepts_pool_factor() -> None:
    pool = _factor(generator="pool")

    result = GenerationResult(
        run_id="run-with-pool",
        factors=[],
        pool=pool,
        counts=_empty_counts(),
        device="cpu",
        tier_level="L0",
    )

    assert result.pool is pool


def test_generation_request_rejects_zero_quota() -> None:
    with pytest.raises(SchemaValidationError, match="quota"):
        _request(quota=0)


def test_generator_protocol_accepts_structural_backend() -> None:
    generator: Generator = _StubGenerator()

    result = generator.produce(_request(quota=1))

    assert generator.name == "stub"
    assert result.run_id == "stub-17"
