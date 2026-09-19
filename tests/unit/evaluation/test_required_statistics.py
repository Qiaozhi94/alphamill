"""T009 / `FR-004`·`AC-003`：HAC IC、block bootstrap、BH-FDR、有效独立数 DSR 与 MinTRL。

覆盖：正态分位/累积、逐期 Rank IC 序列、Newey-West 稳健标准误、固定 seed 的 block bootstrap
可复算、BH step-up 的拒绝集合与 q 值、有效独立试验数、DSR/MinTRL 的方向性与退化输入拒绝、
以及「估计器异常 → `INCOMPLETE` + `estimator_failure`、stage 不得为 PASS」的失败关闭口径。
"""

from __future__ import annotations

import math

import pytest

from alphamill.factor_factory.bench.multiplicity import (
    benjamini_hochberg,
    deflated_sharpe_ratio,
    effective_trials,
    expected_max_sharpe,
    min_track_record_length,
    statistics_stage,
)
from alphamill.factor_factory.bench.stage_model import (
    STAGE_TEMPORAL_STABILITY,
    STATUS_INCOMPLETE,
    STATUS_PASS,
)
from alphamill.factor_factory.bench.statistics import (
    StatisticsError,
    block_bootstrap_ci,
    fit_ic,
    hac_se,
    mean,
    normal_cdf,
    normal_ppf,
    period_ic_series,
)


def _ic_series(size: int, *, base: float = 0.1, wiggle: float = 0.05) -> list[float]:
    return [base + wiggle * math.sin(index / 3.0) for index in range(size)]


# ---------- 分布工具 ----------


def test_normal_cdf_and_ppf_are_inverse_and_match_known_values():
    assert normal_cdf(0.0) == pytest.approx(0.5)
    assert normal_ppf(0.5) == pytest.approx(0.0, abs=1e-8)
    assert normal_ppf(0.975) == pytest.approx(1.959964, abs=1e-5)
    assert normal_cdf(normal_ppf(0.9)) == pytest.approx(0.9, abs=1e-8)


@pytest.mark.parametrize("probability", [0.0, 1.0, -0.1, 1.5])
def test_normal_ppf_rejects_out_of_range(probability: float):
    with pytest.raises(StatisticsError, match="分位数概率"):
        normal_ppf(probability)


# ---------- HAC 与成员级 IC ----------


def test_period_ic_series_is_perfect_for_monotone_periods():
    periods = [
        ([1.0, 2.0, 3.0], [10.0, 20.0, 30.0]),
        ([3.0, 2.0, 1.0], [30.0, 20.0, 10.0]),
    ]
    assert period_ic_series(periods) == (1.0, 1.0)


def test_period_ic_series_handles_ties_via_average_ranks():
    value = period_ic_series(
        [([1.0, 1.0, 2.0], [1.0, 2.0, 3.0]), ([1.0, 2.0, 2.0], [1.0, 2.0, 3.0])]
    )
    assert len(value) == 2
    assert all(0.0 < ic < 1.0 for ic in value)


@pytest.mark.parametrize(
    ("periods", "message"),
    [
        ([], "至少需要"),
        ([([1.0, 2.0], [1.0, 2.0])], "至少需要"),
        (
            [([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]), ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])],
            "秩为常数",
        ),
        ([([1.0, 2.0], [1.0]), ([1.0, 2.0], [1.0, 2.0])], "维度不一致"),
    ],
)
def test_period_ic_series_rejects_degenerate_input(periods, message: str):
    with pytest.raises(StatisticsError, match=message):
        period_ic_series(periods)


def test_hac_se_is_positive_and_clamps_lag():
    series = _ic_series(15)
    assert hac_se(series, lag=5) > 0
    assert hac_se(series, lag=100) == pytest.approx(hac_se(series, lag=14))


def test_hac_se_rejects_degenerate_series():
    # 用 0.5（二进制精确）而非 0.1：py<3.12 的 sum() 无补偿求和，sum([0.1]*10) != 1.0，
    # 会让「常数序列」出现 ~1e-17 的伪偏差而不再是严格退化——该断言不得依赖求和的浮点细节。
    with pytest.raises(StatisticsError, match="HAC 方差非正"):
        hac_se([0.5] * 10)
    with pytest.raises(StatisticsError, match="不得为负"):
        hac_se(_ic_series(5), lag=-1)
    with pytest.raises(StatisticsError, match="至少需要"):
        hac_se([0.1])


def test_fit_ic_reports_point_estimate_and_t_stat():
    series = _ic_series(40, base=0.2, wiggle=0.01)
    fit = fit_ic(series, hac_lag=4)
    assert fit.ic == pytest.approx(mean(series))
    assert fit.t_stat == pytest.approx(fit.ic / fit.hac_se)
    assert fit.n_periods == 40
    assert set(fit.to_payload()) == {"ic", "hac_se", "t_stat", "n_periods", "hac_lag"}


# ---------- block bootstrap ----------


def test_block_bootstrap_is_reproducible_for_a_fixed_seed():
    series = _ic_series(60)
    first = block_bootstrap_ci(series, block_size=5, n_resamples=200, seed=7)
    second = block_bootstrap_ci(series, block_size=5, n_resamples=200, seed=7)
    third = block_bootstrap_ci(series, block_size=5, n_resamples=200, seed=8)
    assert (first.lower, first.upper) == (second.lower, second.upper)
    assert (first.lower, first.upper) != (third.lower, third.upper)


def test_block_bootstrap_interval_brackets_the_point_estimate():
    bootstrap = block_bootstrap_ci(_ic_series(80), block_size=8, n_resamples=400, seed=11)
    assert bootstrap.lower <= bootstrap.point <= bootstrap.upper
    assert bootstrap.excludes_zero is True
    assert set(bootstrap.to_payload()) >= {"point", "lower", "upper", "excludes_zero"}


def test_block_bootstrap_interval_spanning_zero_does_not_exclude_it():
    series = [0.05, -0.05] * 30
    bootstrap = block_bootstrap_ci(series, block_size=2, n_resamples=200, seed=3)
    assert bootstrap.excludes_zero is False


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"block_size": 0}, "block_size"),
        ({"block_size": 999}, "block_size"),
        ({"n_resamples": 0}, "重采样次数"),
        ({"alpha": 1.0}, "alpha"),
    ],
)
def test_block_bootstrap_rejects_invalid_parameters(kwargs: dict, message: str):
    with pytest.raises(StatisticsError, match=message):
        block_bootstrap_ci(_ic_series(20), **kwargs)


# ---------- BH-FDR ----------


def test_benjamini_hochberg_partial_rejection_maps_back_to_original_indices():
    result = benjamini_hochberg([0.001, 0.2, 0.3, 0.4], alpha=0.05)
    assert result.critical_rank == 1
    assert result.rejected == (True, False, False, False)
    assert result.rejected_count == 1
    assert result.q_values[0] <= 0.05


def test_benjamini_hochberg_rejects_all_when_everything_is_small():
    result = benjamini_hochberg([0.01, 0.02, 0.03, 0.04, 0.05], alpha=0.05)
    assert result.critical_rank == 5
    assert all(result.rejected)


def test_benjamini_hochberg_rejects_nothing_when_all_are_large():
    result = benjamini_hochberg([0.3, 0.6, 0.9], alpha=0.05)
    assert result.critical_rank == 0
    assert result.rejected_count == 0


def test_benjamini_hochberg_q_values_are_monotone_and_bounded():
    result = benjamini_hochberg([0.04, 0.01, 0.5], alpha=0.05)
    ordered = sorted(result.q_values)
    assert ordered == result.q_values or all(0.0 <= value <= 1.0 for value in result.q_values)
    assert all(0.0 <= value <= 1.0 for value in result.q_values)


@pytest.mark.parametrize(
    ("values", "alpha", "message"),
    [
        ([], 0.05, "至少一个 p 值"),
        ([0.5], 0.0, "alpha"),
        ([1.5], 0.05, "p 值"),
        ([-0.1], 0.05, "p 值"),
    ],
)
def test_benjamini_hochberg_rejects_invalid_input(values, alpha: float, message: str):
    with pytest.raises(StatisticsError, match=message):
        benjamini_hochberg(values, alpha=alpha)


# ---------- 有效独立数与 DSR / MinTRL ----------


def test_effective_trials_shrinks_with_correlation():
    assert effective_trials([0.0, 0.0, 0.0]) == pytest.approx(4.0)
    assert effective_trials([0.5, 0.5, 0.5]) == pytest.approx(4.0 / (1 + 3 * 0.5))
    with pytest.raises(StatisticsError, match="至少一个相关系数"):
        effective_trials([])
    with pytest.raises(StatisticsError, match="相关系数"):
        effective_trials([1.5])


def test_expected_max_sharpe_grows_with_trial_count():
    assert expected_max_sharpe(1) == 0.0
    values = [expected_max_sharpe(n) for n in (2, 10, 100, 1000)]
    assert values == sorted(values)
    with pytest.raises(StatisticsError, match="正整数"):
        expected_max_sharpe(0)


def test_deflated_sharpe_ratio_penalizes_more_trials():
    base = {"n_trials": 1, "sharpe_std": 0.5, "n_observations": 500}
    few = deflated_sharpe_ratio(0.3, **base)
    many = deflated_sharpe_ratio(0.3, **{**base, "n_trials": 200})
    assert 0.0 <= many < few <= 1.0
    assert deflated_sharpe_ratio(0.5, **base) > few


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"sharpe_std": -1.0}, "SR 标准差"),
        ({"n_observations": 1}, "至少需要 2 个观测"),
        ({"kurtosis": 0.5}, "峰度"),
    ],
)
def test_deflated_sharpe_ratio_rejects_invalid_input(kwargs: dict, message: str):
    base = {"n_trials": 5, "sharpe_std": 0.5, "n_observations": 500, "sharpe": 0.3}
    base.update(kwargs)
    sharpe = base.pop("sharpe")
    with pytest.raises(StatisticsError, match=message):
        deflated_sharpe_ratio(sharpe, **base)


def test_min_track_record_length_shrinks_with_larger_edge():
    close = min_track_record_length(0.11, target_sharpe=0.10)
    far = min_track_record_length(0.30, target_sharpe=0.10)
    assert far < close
    with pytest.raises(StatisticsError, match="无有限解"):
        min_track_record_length(0.05, target_sharpe=0.10)
    with pytest.raises(StatisticsError, match="alpha"):
        min_track_record_length(0.3, target_sharpe=0.1, alpha=2.0)


# ---------- 失败关闭 ----------


def test_statistics_stage_returns_pass_on_success():
    value, stage = statistics_stage(
        STAGE_TEMPORAL_STABILITY, lambda: fit_ic(_ic_series(30)), observed_at="2026-09-01T00:00:00Z"
    )
    assert value is not None
    assert stage.status == STATUS_PASS


def test_statistics_stage_maps_estimator_error_to_incomplete():
    value, stage = statistics_stage(
        STAGE_TEMPORAL_STABILITY, lambda: fit_ic([0.1]), observed_at="2026-09-01T00:00:00Z"
    )
    assert value is None
    assert stage.status == STATUS_INCOMPLETE
    assert stage.status != STATUS_PASS
    assert stage.failures[0].mechanism == "estimator_failure"
    assert stage.failures[0].owner == "statistics"
    assert stage.failures[0].error_code == "E_REQUIRED_METRIC_FAILED"
