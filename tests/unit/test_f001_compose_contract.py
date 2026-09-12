"""F001 dry-run compose/import contract regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_freqtrade_service_mounts_repo_strategy_dependencies() -> None:
    compose = (ROOT / "deployment/docker-compose.yml").read_text(encoding="utf-8")
    strategy = (ROOT / "freqtrade/user_data/strategies/KronosFusionStrategy.py").read_text(
        encoding="utf-8"
    )

    assert "  freqtrade:" in compose
    assert "../src:/app/src:ro" in compose
    assert "../freqtrade/signal_fusion:/freqtrade/signal_fusion:ro" in compose
    assert (
        "../db/migrations/003_derivatives_market_data.sql:"
        "/docker-entrypoint-initdb.d/02_derivatives_market_data.sql:ro"
    ) in compose
    assert "--strategy-path" in compose
    assert "from alphamill.freqtrade_bridge.risk.circuit_breaker import CircuitBreaker" in strategy
    assert "from risk." not in strategy
