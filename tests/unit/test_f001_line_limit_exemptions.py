"""F001 file-limit exemption register regression test."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_all_f001_over_limit_files_are_registered_with_an_expiry() -> None:
    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
    paths = [
        "src/alphamill/data_bridge/collector/derivatives_market_backfill.py",
        "freqtrade/user_data/strategies/KronosFusionStrategy.py",
        "src/alphamill/validation/validate_low_frequency_expanded_holdout.py",
        "src/alphamill/validation/train_low_frequency_walk_forward_baselines.py",
        "src/alphamill/validation/validate_low_frequency_regime_filters.py",
        "deployment/verify.ps1",
        "src/alphamill/validation/validate_low_frequency_candidate_holdout.py",
        "src/alphamill/factor_factory/bench/independent_cross_backtest.py",
    ]

    for path in paths:
        assert f"`{path}`" in sop
    assert "解除期限" in sop
    assert "F002" in sop
