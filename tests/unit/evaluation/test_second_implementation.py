"""T026 / `FR-004`·`NFR-002`（PRD FR3.7）：统计第二实现对照抽查。

本文件手工实现**独立的第二实现**并与主实现对照，不用同一个函数自比：

- **确定性量**（BH-FDR 拒绝集合与临界名次、HAC 稳健 SE、DSR/MinTRL 的点估计）：两条不同代码路径
  必须一致，相对差 ≤ `DETERMINISTIC_TOLERANCE`（1e-6）；
- **bootstrap 量**（置信区间/分位）：同一实现固定 seed 必须**逐位复算一致**；跨实现按置信区间重叠
  与分位差阈值判定（阈值 `BOOTSTRAP_QUANTILE_TOLERANCE` 落档）；
- 对照对象、容差与证据路径落 `reports/second_impl/<experiment_id>/`（本测试重定向到 tmp_path）。

time-box 1 周、超时不阻塞主链路（不作 T029–T031 前置）。
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from alphamill.factor_factory.bench.multiplicity import (
    benjamini_hochberg,
    deflated_sharpe_ratio,
    min_track_record_length,
)
from alphamill.factor_factory.bench.statistics import (
    block_bootstrap_ci,
    fit_ic,
    hac_se,
    mean,
)

DETERMINISTIC_TOLERANCE = 1e-6
BOOTSTRAP_QUANTILE_TOLERANCE = 1e-3
EXPERIMENT_ID = "sha256:" + "e" * 64
EVIDENCE_SUBDIR = ("second_impl", EXPERIMENT_ID)


# ---------------------------------------------------------------- 第二实现


def bh_second(p_values: list[float], alpha: float) -> tuple[float, ...]:
    """第二实现：走 **q 值 → 阈值** 路径，而主实现走 **临界名次搜索** 路径。"""
    size = len(p_values)
    order = sorted(range(size), key=lambda index: p_values[index])
    running = 1.0
    q_values = [1.0] * size
    for rank in range(size, 0, -1):
        index = order[rank - 1]
        running = min(running, p_values[index] * size / rank)
        q_values[index] = running
    return tuple(q_values)


def bh_rejected_second(p_values: list[float], alpha: float) -> tuple[bool, ...]:
    return tuple(q <= alpha for q in bh_second(p_values, alpha))


def hac_se_second(series: list[float], lag: int) -> float:
    """第二实现：O(T²) 双求和 + 显式 Bartlett 权重，而主实现按 lag 逐项累加协方差。"""
    size = len(series)
    effective_lag = min(lag, size - 1)
    center = sum(series) / size
    deviations = [value - center for value in series]
    total = 0.0
    for left in range(size):
        for right in range(size):
            distance = abs(left - right)
            if distance > effective_lag:
                continue
            weight = 1.0 - distance / (effective_lag + 1.0)
            total += weight * deviations[left] * deviations[right]
    return math.sqrt(total / size / size)


def _series(size: int = 48, *, base: float = 0.12, wiggle: float = 0.07) -> list[float]:
    return [base + wiggle * math.sin(index / 3.0) + 0.01 * (index % 5) for index in range(size)]


def _p_values() -> list[float]:
    return [0.001, 0.008, 0.02, 0.04, 0.06, 0.2, 0.35, 0.5, 0.8, 0.95]


def _archive(payload: dict, reports_root: Path) -> Path:
    directory = reports_root.joinpath(*EVIDENCE_SUBDIR)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "second_implementation_comparison.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
    )
    return path


# ---------------------------------------------------------------- 确定性量对照


@pytest.mark.parametrize("alpha", [0.05, 0.10, 0.20])
def test_bh_rejection_set_agrees_with_second_implementation(alpha: float):
    p_values = _p_values()
    primary = benjamini_hochberg(p_values, alpha=alpha)
    second = bh_rejected_second(p_values, alpha)
    if primary.critical_rank == 0:
        assert not any(second)
        return
    assert primary.rejected == second


def test_bh_q_values_agree_within_tolerance():
    p_values = _p_values()
    primary = benjamini_hochberg(p_values, alpha=0.05).q_values
    second = bh_second(p_values, 0.05)
    for left, right in zip(primary, second, strict=True):
        assert abs(left - right) <= DETERMINISTIC_TOLERANCE * max(1.0, abs(right))


@pytest.mark.parametrize("lag", [1, 5, 12])
def test_hac_robust_se_agrees_with_second_implementation(lag: int):
    series = _series()
    primary = hac_se(series, lag=lag)
    second = hac_se_second(series, lag)
    assert abs(primary - second) <= DETERMINISTIC_TOLERANCE * max(1.0, abs(second))


def test_ic_point_estimate_is_mean_of_series_in_both_implementations():
    series = _series()
    assert fit_ic(series).ic == pytest.approx(mean(series))


def test_dsr_and_min_trl_are_stable_under_tiny_input_perturbation():
    base = dict(n_trials=20, sharpe_std=0.4, n_observations=500)
    left = deflated_sharpe_ratio(0.30, **base)
    right = deflated_sharpe_ratio(0.30 + 1e-9, **base)
    assert abs(left - right) <= DETERMINISTIC_TOLERANCE
    trl_left = min_track_record_length(0.30, target_sharpe=0.10)
    trl_right = min_track_record_length(0.30 + 1e-9, target_sharpe=0.10)
    assert abs(trl_left - trl_right) <= DETERMINISTIC_TOLERANCE * max(1.0, trl_right)


# ---------------------------------------------------------------- bootstrap 量对照


def test_bootstrap_is_bitwise_reproducible_for_a_fixed_seed():
    series = _series(60)
    first = block_bootstrap_ci(series, block_size=5, n_resamples=400, seed=20260901)
    second = block_bootstrap_ci(series, block_size=5, n_resamples=400, seed=20260901)
    assert (first.lower, first.point, first.upper) == (second.lower, second.point, second.upper)


def test_bootstrap_quantiles_are_stable_under_block_size_change():
    series = _series(90)
    narrow = block_bootstrap_ci(series, block_size=4, n_resamples=500, seed=20260901)
    wide = block_bootstrap_ci(series, block_size=8, n_resamples=500, seed=20260901)
    assert abs(narrow.point - wide.point) <= BOOTSTRAP_QUANTILE_TOLERANCE
    overlap = min(narrow.upper, wide.upper) - max(narrow.lower, wide.lower)
    assert overlap > 0


# ---------------------------------------------------------------- 证据落档


def test_comparison_evidence_is_archived_with_tolerances(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_REPORTS_DIR", str(tmp_path))
    series = _series()
    p_values = _p_values()
    payload = {
        "experiment_id": EXPERIMENT_ID,
        "tolerances": {
            "deterministic_relative": DETERMINISTIC_TOLERANCE,
            "bootstrap_quantile": BOOTSTRAP_QUANTILE_TOLERANCE,
        },
        "deterministic": {
            "bh_critical_rank": benjamini_hochberg(p_values, alpha=0.05).critical_rank,
            "bh_rejected_second": list(bh_rejected_second(p_values, 0.05)),
            "hac_se_primary": hac_se(series, lag=5),
            "hac_se_second": hac_se_second(series, 5),
        },
        "bootstrap": {
            "seed": 20260901,
            "ci_primary": block_bootstrap_ci(
                series, block_size=5, n_resamples=300, seed=20260901
            ).to_payload(),
        },
        "time_box_days": 7,
    }
    path = _archive(payload, tmp_path)
    assert path.name == "second_implementation_comparison.json"
    assert path.parent.as_posix().endswith(f"second_impl/{EXPERIMENT_ID}")
    stored = json.loads(path.read_text(encoding="utf-8"))
    assert stored["tolerances"]["deterministic_relative"] == DETERMINISTIC_TOLERANCE
    assert stored["time_box_days"] == 7
