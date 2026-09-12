"""F001 dry-run compose/import contract regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_freqtrade_service_mounts_repo_strategy_dependencies() -> None:
    compose = (ROOT / "deployment/docker-compose.yml").read_text(encoding="utf-8")
    strategy = (ROOT / "freqtrade/user_data/strategies/KronosFusionStrategy.py").read_text(
        encoding="utf-8"
    )

    assert "  freqtrade:" in compose
    assert '      - "8080:8080"' in compose
    assert "HTTP_PROXY: ${BINANCE_HTTPS_PROXY:-}" in compose
    assert "HTTPS_PROXY: ${BINANCE_HTTPS_PROXY:-}" in compose
    assert "NO_PROXY: timescaledb,kronos-signal,localhost,127.0.0.1" in compose
    assert "SYMBOLS: ${SYMBOLS:-BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT}" in compose
    assert "../src:/app/src:ro" in compose
    assert "PYTHONPATH: /app/src:/freqtrade" in compose
    assert "../freqtrade/signal_fusion:/freqtrade/signal_fusion:ro" in compose
    # C009 的意图（衍生品 schema 必须随全新库自动初始化）不变，机制改为整目录挂载 +
    # initdb 脚本按序应用并登记账本（C402），逐文件挂载已移除。
    assert "../db/migrations:/docker-entrypoint-initdb.d/migrations:ro" in compose
    assert (
        "./initdb-apply-migrations.sh:/docker-entrypoint-initdb.d/02_apply_migrations.sh:ro"
    ) in compose
    assert "--strategy-path" in compose
    assert "from alphamill.freqtrade_bridge.risk.circuit_breaker import CircuitBreaker" in strategy
    assert "from risk." not in strategy


def test_ac006_command_carries_host_database_env() -> None:
    """C501：文档化的 AC-006 命令必须带宿主 DB 环境，否则照抄会 500（实测踩过）。"""
    spec = (ROOT / "docs/features/0.1/F001-quant-crypto-migration/spec.md").read_text(
        encoding="utf-8"
    )
    smoke = (ROOT / "tests/integration/test_f001_kronos_smoke.py").read_text(encoding="utf-8")
    for text, name in ((spec, "spec.md"), (smoke, "test_f001_kronos_smoke.py")):
        assert "DB_HOST=127.0.0.1" in text, f"{name} 的 AC-006 命令缺少 DB_HOST"
        assert "./deployment/.env" in text, f"{name} 的 AC-006 命令缺少 .env 载入"
