"""T005 / AC-004：symbol_map 生成、双向解析、内容寻址发布与可重放。"""

import pandas as pd
import pytest

from alphamill.data_bridge import symbol_map as sm
from alphamill.data_bridge.errors import (
    DataBridgeError,
    SymbolCollisionError,
    SymbolNotFoundError,
)

ROWS = [
    sm.SymbolRow("binance", "spot", "BTC/USDT"),
    sm.SymbolRow("binance", "spot", "ETH/USDT"),
    sm.SymbolRow("binanceusdm", "perp", "BTC/USDT"),
]


class _FakeCursor:
    def __init__(self, rows_by_table: dict[str, list[tuple]], executed: list[str]):
        self._rows = rows_by_table
        self._executed = executed

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql: str) -> None:
        self._executed.append(sql)
        table = sql.split("FROM ")[1].strip()
        self._result = self._rows[table]

    def fetchall(self):
        return self._result


class _FakeConn:
    def __init__(self, rows_by_table: dict[str, list[tuple]]):
        self._rows = rows_by_table
        self.executed: list[str] = []

    def cursor(self):
        return _FakeCursor(self._rows, self.executed)


def test_build_formats_spot_and_perp_not_confused():
    frame = sm.build_symbol_map(ROWS)
    assert list(frame.columns) == list(sm.COLUMNS)
    by_key = {(r.exchange, r.market_type, r.db_symbol): r for r in frame.itertuples(index=False)}
    assert by_key[("binance", "spot", "BTC/USDT")].lake_pair == "BTC-USDT"
    assert by_key[("binance", "spot", "BTC/USDT")].freqtrade_pair == "BTC/USDT"
    assert by_key[("binanceusdm", "perp", "BTC/USDT")].lake_pair == "BTC-USDT-PERP"
    assert by_key[("binanceusdm", "perp", "BTC/USDT")].freqtrade_pair == "BTC/USDT:USDT"


def test_perp_with_explicit_settle_derives_same_ft_pair():
    assert sm.derive_pairs("BTC/USDT:USDT", "perp") == ("BTC-USDT-PERP", "BTC/USDT:USDT")
    assert sm.derive_pairs("BTC/USDT", "spot") == ("BTC-USDT", "BTC/USDT")


def test_collision_fails_loudly():
    with pytest.raises(SymbolCollisionError, match="碰撞"):
        sm.build_symbol_map(
            [
                sm.SymbolRow("binance", "spot", "BTC/USDT"),
                sm.SymbolRow("okx", "spot", "BTC/USDT"),
                sm.SymbolRow("binance", "perp", "BTC/USDT"),
            ]
        )
    # 同一 lake_pair 但 market_type 不同不碰撞（键含 market_type）
    ok = sm.build_symbol_map(
        [sm.SymbolRow("binance", "spot", "BTC/USDT"), sm.SymbolRow("binance", "perp", "BTC/USDT")]
    )
    assert len(ok) == 2


def test_runtime_pair_map_keeps_market_type_in_lookup_key(monkeypatch):
    from alphamill.data_bridge import partitions

    rows = [
        sm.SymbolRow("binance", "spot", "BTC/USDT"),
        sm.SymbolRow("binance", "perp", "BTC/USDT"),
    ]
    monkeypatch.setattr(sm, "_rows_from_conn", lambda _conn: rows)
    pairs = partitions.lake_pairs_map(object())
    assert pairs[("binance", "spot", "BTC/USDT")] == "BTC-USDT"
    assert pairs[("binance", "perp", "BTC/USDT")] == "BTC-USDT-PERP"


def test_canonical_bytes_digest_stable_and_content_sensitive():
    frame = sm.build_symbol_map(ROWS)
    first = sm.canonical_csv_bytes(frame)
    reordered = frame.iloc[::-1]
    assert sm.canonical_csv_bytes(reordered) == first  # 行序无关，编码即规范
    assert first.startswith(b"exchange,market_type,db_symbol,lake_pair,freqtrade_pair\n")
    assert b"\r" not in first

    changed = sm.build_symbol_map([*ROWS, sm.SymbolRow("binance", "spot", "SOL/USDT")])
    assert sm.canonical_csv_bytes(changed) != first
    assert sm.content_digest(first) != sm.content_digest(sm.canonical_csv_bytes(changed))


def test_default_current_map_is_lake_local_not_in_source_tree(tmp_path, monkeypatch):
    monkeypatch.delenv("ALPHAMILL_SYMBOL_MAP_CURRENT", raising=False)
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(tmp_path))
    assert sm.current_csv_path() == tmp_path / "_metadata" / "symbol_map.csv"


def test_export_publishes_immutable_artifact_and_replays(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "current" / "symbol_map.csv"))
    conn = _FakeConn(
        {
            "ohlcv_1m": [("binance", "BTC/USDT"), ("binance", "ETH/USDT")],
            "derivatives_funding_rates": [("binanceusdm", "BTC/USDT")],
            "derivatives_open_interest": [],
            "derivatives_mark_index_basis": [],
            "signals_log": [],
        }
    )
    ref = sm.export_symbol_map(conn=conn, lake_root=tmp_path)
    assert ref.path.name == f"{ref.digest}.csv"
    assert ref.path.is_file()
    # conn=None 走 db_connect 的路径不在此测；signals_log 不参与全局映射推导。
    assert sum("FROM " in sql for sql in conn.executed) == 4
    assert all("FROM signals_log" not in sql for sql in conn.executed)

    # 同内容再导出：同 digest、逐字节一致，不产生第二个文件
    ref_again = sm.export_symbol_map(conn=conn, lake_root=tmp_path)
    assert ref_again.digest == ref.digest
    assert ref_again.path.read_bytes() == ref.path.read_bytes()

    # 按 digest 重放；内容变化生成新 digest，旧 digest 仍可读
    loaded = sm.load_symbol_map(ref.digest, lake_root=tmp_path)
    assert isinstance(loaded, pd.DataFrame)
    assert len(loaded) == 3

    conn2 = _FakeConn(
        {
            "ohlcv_1m": [("binance", "BTC/USDT")],
            "derivatives_funding_rates": [],
            "derivatives_open_interest": [],
            "derivatives_mark_index_basis": [],
            "signals_log": [],
        }
    )
    ref_v2 = sm.export_symbol_map(conn=conn2, lake_root=tmp_path)
    assert ref_v2.digest != ref.digest
    assert sm.load_symbol_map(ref.digest, lake_root=tmp_path).shape[0] == 3

    with pytest.raises(DataBridgeError, match="不存在"):
        sm.load_symbol_map("sha256:" + "0" * 64, lake_root=tmp_path)

    ref.path.write_bytes(ref.path.read_bytes() + b"\n")
    with pytest.raises(DataBridgeError, match="digest 校验"):
        sm.load_symbol_map(ref.digest, lake_root=tmp_path)


def test_artifact_creation_does_not_overwrite_existing_digest_file(tmp_path):
    target = tmp_path / "artifact.csv"
    target.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        sm._atomic_create(target, b"replacement")
    assert target.read_bytes() == b"original"


def test_artifact_creation_falls_back_when_hard_links_are_unavailable(tmp_path, monkeypatch):
    target = tmp_path / "artifact.csv"

    def unsupported_link(*_args):
        raise OSError(18, "cross-device link")

    monkeypatch.setattr(sm.os, "link", unsupported_link)
    sm._atomic_create(target, b"payload")
    assert target.read_bytes() == b"payload"


def test_signals_log_symbols_do_not_assume_spot_market_type():
    conn = _FakeConn(
        {
            "ohlcv_1m": [("binance", "BTC/USDT")],
            "derivatives_funding_rates": [],
            "derivatives_open_interest": [],
            "derivatives_mark_index_basis": [],
            "signals_log": [("binanceusdm", "BTC/USDT")],
        }
    )
    frame = sm.build_symbol_map(sm._rows_from_conn(conn))
    assert len(frame) == 1
    assert frame.iloc[0]["lake_pair"] == "BTC-USDT"


def test_resolve_directions_and_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "current" / "symbol_map.csv"))
    conn = _FakeConn(
        {
            "ohlcv_1m": [("binance", "BTC/USDT")],
            "derivatives_funding_rates": [("binanceusdm", "BTC/USDT")],
            "derivatives_open_interest": [],
            "derivatives_mark_index_basis": [],
            "signals_log": [],
        }
    )
    sm.export_symbol_map(conn=conn, lake_root=tmp_path)

    assert sm.resolve("BTC/USDT", "to_lake", exchange="binance") == "BTC-USDT"
    assert sm.resolve("BTC-USDT", "to_db", exchange="binance") == "BTC/USDT"
    assert (
        sm.resolve("BTC/USDT", "to_freqtrade", exchange="binanceusdm", market_type="perp")
        == "BTC/USDT:USDT"
    )
    # 同名 db_symbol 跨 spot/perp 不混淆：exchange+market_type 消歧
    with pytest.raises(SymbolNotFoundError):
        sm.resolve("BTC-USDT-PERP", "to_db", exchange="binance")  # spot 侧无此 lake_pair
    assert (
        sm.resolve("BTC-USDT-PERP", "to_db", exchange="binanceusdm", market_type="perp")
        == "BTC/USDT"
    )

    with pytest.raises(DataBridgeError, match="方向"):
        sm.resolve("x", "sideways", exchange="binance")


def test_to_db_symbols_for_reader(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_SYMBOL_MAP_CURRENT", str(tmp_path / "current" / "symbol_map.csv"))
    conn = _FakeConn(
        {
            "ohlcv_1m": [("binance", "BTC/USDT"), ("binance", "ETH/USDT")],
            "derivatives_funding_rates": [],
            "derivatives_open_interest": [],
            "derivatives_mark_index_basis": [],
            "signals_log": [],
        }
    )
    sm.export_symbol_map(conn=conn, lake_root=tmp_path)
    assert sorted(sm.to_db_symbols(["BTC-USDT"], "spot", lake_root=tmp_path)) == ["BTC/USDT"]
    assert sm.to_db_symbols(["BTC-USDT", "ETH-USDT"], "spot", lake_root=tmp_path) == [
        "BTC/USDT",
        "ETH/USDT",
    ]
    with pytest.raises(SymbolNotFoundError):
        sm.to_db_symbols(["SOL-USDT"], "spot", lake_root=tmp_path)
