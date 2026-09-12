"""F001 authoritative backfill window single-source regression test."""

from pathlib import Path

import tools.f001_backfill_config as backfill_config
from tools.f001_backfill_config import (
    WINDOW_FILE,
    configured_derivatives_exchange,
    configured_exchanges,
    configured_symbols,
    window_values,
)

ROOT = Path(__file__).resolve().parents[2]


def test_window_file_is_used_by_code_and_supervisor() -> None:
    assert WINDOW_FILE == ROOT / "deployment/f001-backfill-window.env"
    start, end = window_values()
    window_file = WINDOW_FILE.read_text(encoding="utf-8")
    supervisor = (ROOT / "deployment/f001-backfill-supervisor.sh").read_text(encoding="utf-8")

    assert f"BACKFILL_WINDOW_START={start}" in window_file
    assert f"BACKFILL_WINDOW_END={end}" in window_file
    assert "source deployment/f001-backfill-window.env" in supervisor
    assert "BACKFILL_START=2024-09-10" not in supervisor
    assert "BACKFILL_END=2026-09-10" not in supervisor


def test_backfill_universe_comes_from_tracked_window_file(monkeypatch) -> None:
    monkeypatch.delenv("SYMBOLS", raising=False)
    monkeypatch.delenv("EXCHANGES", raising=False)
    window_file = WINDOW_FILE.read_text(encoding="utf-8")
    symbols = configured_symbols()
    exchanges = configured_exchanges()

    assert symbols
    assert exchanges
    assert f"SYMBOLS={','.join(symbols)}" in window_file
    assert f"EXCHANGES={','.join(exchanges)}" in window_file
    assert f"DERIVATIVES_EXCHANGE={configured_derivatives_exchange()}" in window_file


def test_runtime_dotenv_overrides_tracked_defaults_consistently(
    monkeypatch, tmp_path: Path
) -> None:
    supervisor = (ROOT / "deployment/f001-backfill-supervisor.sh").read_text(encoding="utf-8")
    assert supervisor.index("source deployment/f001-backfill-window.env") < supervisor.index(
        "source deployment/.env"
    )

    window_file = tmp_path / "window.env"
    dotenv_file = tmp_path / "runtime.env"
    window_file.write_text("SYMBOLS=TRACKED/USDT\n", encoding="utf-8")
    dotenv_file.write_text("SYMBOLS=RUNTIME/USDT\n", encoding="utf-8")
    monkeypatch.setattr(backfill_config, "WINDOW_FILE", window_file)
    monkeypatch.setattr(backfill_config, "DOTENV_FILE", dotenv_file)
    monkeypatch.delenv("SYMBOLS", raising=False)

    assert configured_symbols() == ["RUNTIME/USDT"]


def test_verdict_settings_ignore_runtime_dotenv(monkeypatch, tmp_path: Path) -> None:
    """判据量只认入库的 window.env：本机 .env 不得改窄 AC-001 的验收口径。"""
    window_file = tmp_path / "window.env"
    dotenv_file = tmp_path / "runtime.env"
    window_file.write_text(
        "BACKFILL_WINDOW_START=2024-09-10T00:00:00Z\n"
        "BACKFILL_WINDOW_END=2026-09-10T15:52:00Z\n"
        "BACKFILL_UNAVAILABLE_SYMBOLS=\n",
        encoding="utf-8",
    )
    dotenv_file.write_text(
        "BACKFILL_WINDOW_START=2026-09-01T00:00:00Z\n"
        "BACKFILL_WINDOW_END=2026-09-02T00:00:00Z\n"
        "BACKFILL_UNAVAILABLE_SYMBOLS=BTC/USDT\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(backfill_config, "WINDOW_FILE", window_file)
    monkeypatch.setattr(backfill_config, "DOTENV_FILE", dotenv_file)
    for name in backfill_config.VERDICT_SETTINGS:
        monkeypatch.delenv(name, raising=False)

    assert window_values() == ("2024-09-10T00:00:00Z", "2026-09-10T15:52:00Z")
    assert backfill_config.unavailable_symbols() == set()


def test_runtime_dotenv_files_carry_no_verdict_settings() -> None:
    """deployment/.env 与 .env.example 都不得携带判据量，避免优先级再次回潮。"""
    for name in ("deployment/.env", "deployment/.env.example"):
        path = ROOT / name
        if not path.is_file():
            continue
        keys = {
            line.split("=", 1)[0].strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if "=" in line and not line.lstrip().startswith("#")
        }
        assert not keys & set(backfill_config.VERDICT_SETTINGS), (
            f"{name} 含判据量 {sorted(keys & set(backfill_config.VERDICT_SETTINGS))}，"
            "应只留在 deployment/f001-backfill-window.env"
        )
