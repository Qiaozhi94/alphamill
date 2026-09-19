"""统一列集面板装载的确定性（`R1-103`）：结果不得依赖 CSV 原始行序。"""

from __future__ import annotations

from pathlib import Path

import pytest

from alphamill.evaluation.contract_common import UpstreamContractError
from alphamill.evaluation.run_config import load_unified_panel

HEADER = "time,symbol,close,signal,forward_return\n"
GROUPED = (
    "2026-01-01T00:00:00Z,BTC-USDT,100,1.0,0.01\n"
    "2026-01-01T01:00:00Z,BTC-USDT,101,2.0,0.02\n"
    "2026-01-01T00:00:00Z,ETH-USDT,50,3.0,0.03\n"
    "2026-01-01T01:00:00Z,ETH-USDT,51,4.0,0.04\n"
)
SHUFFLED = (
    "2026-01-01T01:00:00Z,ETH-USDT,51,4.0,0.04\n"
    "2026-01-01T00:00:00Z,BTC-USDT,100,1.0,0.01\n"
    "2026-01-01T01:00:00Z,BTC-USDT,101,2.0,0.02\n"
    "2026-01-01T00:00:00Z,ETH-USDT,50,3.0,0.03\n"
)


def _write(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "panel.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(HEADER + body, encoding="utf-8")
    return path


def test_panel_loading_is_independent_of_csv_row_order(tmp_path):
    grouped = load_unified_panel(_write(tmp_path / "a", GROUPED))
    shuffled = load_unified_panel(_write(tmp_path / "b", SHUFFLED))
    assert grouped == shuffled
    assert grouped[0] == (
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
        "2026-01-01T00:00:00Z",
        "2026-01-01T01:00:00Z",
    )
    assert grouped[1] == ("BTC-USDT", "BTC-USDT", "ETH-USDT", "ETH-USDT")


def test_duplicate_time_symbol_is_rejected(tmp_path):
    duplicated = GROUPED + "2026-01-01T00:00:00Z,BTC-USDT,100,9.0,9.0\n"
    with pytest.raises(UpstreamContractError, match="重复"):
        load_unified_panel(_write(tmp_path, duplicated))
