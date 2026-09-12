"""F001 default exchange contract regression tests."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_runtime_defaults_follow_binance_migration_route() -> None:
    compose = (ROOT / "deployment/docker-compose.yml").read_text(encoding="utf-8")
    env_example = (ROOT / "deployment/.env.example").read_text(encoding="utf-8")
    server = (ROOT / "src/alphamill/kronos_service/server.py").read_text(encoding="utf-8")
    adapter = (ROOT / "src/alphamill/kronos_service/db_adapter.py").read_text(encoding="utf-8")
    config = json.loads((ROOT / "freqtrade/user_data/config.json").read_text(encoding="utf-8"))

    assert "EXCHANGES: ${EXCHANGES:-binance}" in compose
    assert "EXCHANGES=binance" in env_example
    assert "DERIVATIVES_EXCHANGE=binanceusdm" in env_example
    assert 'exchange: str = "binance"' in server
    assert 'exchange: str = "binance"' in adapter
    assert config["exchange"]["name"] == "binance"
