"""F001 authoritative backfill window single-source regression test."""

from pathlib import Path

from tools.f001_backfill_config import WINDOW_FILE, window_values

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
