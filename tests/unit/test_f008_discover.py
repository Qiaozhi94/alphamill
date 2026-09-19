"""T001/T003/T004 与 `AC-001`：筛选口径、交易所接口 fixture 与候选清单可复现。

覆盖：默认口径 = Q-001 裁决值、口径键集合严格校验、排名法不受市场整体量级影响、
结构性排除（稳定币 base / 杠杆代币 / 指数篮子）、上线天数严格大于阈值、
以及 `fetch_snapshot` 在固定接口响应 fixture 上的解析（不触网）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from alphamill.data_bridge.universe import criteria as criteria_mod
from alphamill.data_bridge.universe import discover
from alphamill.data_bridge.universe.criteria import load_criteria
from alphamill.data_bridge.universe.definition import build_definition
from alphamill.data_bridge.universe.discover import (
    Candidate,
    Evaluation,
    MarketSnapshot,
)
from alphamill.data_bridge.universe.errors import CriteriaError, ExchangeUnreachableError
from tests.f008_fixtures import criteria_for, market, snapshot

SNAPSHOT_AT = "2026-09-19T00:00:00Z"


_market = market
_snapshot = snapshot
_criteria = criteria_for


# ---------- T001：口径文件 ----------


def test_default_criteria_is_the_q001_ruling() -> None:
    loaded = load_criteria()
    assert loaded.exchange == "binance"
    assert loaded.market_type == "perp"
    assert loaded.quote_currency == "USDT"
    assert loaded.turnover_lookback_days == 90
    assert loaded.turnover_rank_top_n == 40
    assert loaded.min_listed_days == 180
    assert loaded.exclude_rules == ("stablecoin_pair", "leveraged_token", "index_basket")


def test_criteria_rejects_unknown_and_missing_keys(tmp_path) -> None:
    path = tmp_path / "criteria.json"
    path.write_text(
        '{"schema_version":1,"exchange":"binance","market_type":"perp","quote_currency":"USDT",'
        '"turnover_lookback_days":90,"turnover_rank_top_n":40,"min_listed_days":180,'
        '"exclude_rules":[],"absolute_turnover_floor":1000000}',
        encoding="utf-8",
    )
    with pytest.raises(CriteriaError, match="unknown"):
        load_criteria(path)

    path.write_text('{"schema_version":1,"exchange":"binance"}', encoding="utf-8")
    with pytest.raises(CriteriaError, match="missing"):
        load_criteria(path)


def test_criteria_rejects_unknown_rule_and_bad_market_type(tmp_path) -> None:
    good = (
        '{"schema_version":1,"exchange":"binance","market_type":"%s","quote_currency":"USDT",'
        '"turnover_lookback_days":90,"turnover_rank_top_n":40,"min_listed_days":180,'
        '"exclude_rules":%s}'
    )
    path = tmp_path / "criteria.json"
    path.write_text(good % ("perp", '["meme_coin"]'), encoding="utf-8")
    with pytest.raises(CriteriaError, match="未知排除规则"):
        load_criteria(path)
    path.write_text(good % ("options", "[]"), encoding="utf-8")
    with pytest.raises(CriteriaError, match="market_type"):
        load_criteria(path)


def test_min_listed_days_is_strictly_greater() -> None:
    """spec §3：上线 **>180 天**——整整 180 天不算过线（边界按字面口径锁定）。"""
    at_threshold = _market("AAA", listed_days=180)
    above = _market("BBB", listed_days=181)
    evaluation = discover.evaluate(_snapshot(at_threshold, above), _criteria(turnover_rank_top_n=5))
    reasons = {item.db_symbol: item.excluded_reason for item in evaluation.candidates}
    assert reasons["AAA/USDT"] == discover.REASON_LISTED_DAYS
    assert reasons["BBB/USDT"] is None
    assert evaluation.selected_pairs() == ("BBB/USDT",)


# ---------- T004：候选筛选 ----------


def test_ranking_is_ordered_and_rest_records_reason() -> None:
    evaluation = discover.evaluate(
        _snapshot(
            _market("BTC", turnover=9_000.0),
            _market("ETH", turnover=5_000.0),
            _market("SOL", turnover=1_000.0),
        ),
        _criteria(turnover_rank_top_n=2),
    )
    assert evaluation.selected_pairs() == ("BTC/USDT", "ETH/USDT")
    assert [item.rank for item in evaluation.selected] == [1, 2]
    dropped = [item for item in evaluation.candidates if item.excluded_reason]
    assert [(item.db_symbol, item.excluded_reason) for item in dropped] == [
        ("SOL/USDT", discover.REASON_RANK)
    ]
    # 排除者也带完整指标（DR-001：逐候选筛选指标入档）
    assert dropped[0].turnover_usdt == 1_000.0
    assert dropped[0].listed_days == 700


def test_rank_scale_is_immune_to_market_cycle() -> None:
    """排名法：全市场成交额整体放大 10 倍，候选数量与成员不变（FR-001 场景 2）。"""
    small = _snapshot(
        _market("BTC", turnover=9_000.0),
        _market("ETH", turnover=5_000.0),
        _market("SOL", turnover=1_000.0),
    )
    large = _snapshot(
        _market("BTC", turnover=90_000.0),
        _market("ETH", turnover=50_000.0),
        _market("SOL", turnover=10_000.0),
    )
    criteria = _criteria(turnover_rank_top_n=2)
    assert discover.evaluate(small, criteria).selected_pairs() == (
        discover.evaluate(large, criteria).selected_pairs()
    )


def test_ties_break_on_db_symbol_for_determinism() -> None:
    evaluation = discover.evaluate(
        _snapshot(
            _market("ZZZ", turnover=1.0),
            _market("AAA", turnover=1.0),
        ),
        _criteria(turnover_rank_top_n=1),
    )
    assert evaluation.selected_pairs() == ("AAA/USDT",)


def test_structural_exclusions_each_record_their_own_reason() -> None:
    evaluation = discover.evaluate(
        _snapshot(
            _market("USDC"),
            _market("BTCUP"),
            _market("BTCDOM"),
            _market("JUP"),
        ),
        _criteria(turnover_rank_top_n=10),
    )
    reasons = {item.db_symbol: item.excluded_reason for item in evaluation.candidates}
    assert reasons["USDC/USDT"] == discover.REASON_STABLECOIN
    assert reasons["BTCUP/USDT"] == discover.REASON_LEVERAGED
    assert reasons["BTCDOM/USDT"] == discover.REASON_INDEX
    # `JUP` 以 UP 结尾但不是杠杆代币：护栏必须挡住误判
    assert reasons["JUP/USDT"] is None


def test_repeat_evaluation_yields_identical_candidates_and_universe_id() -> None:
    """AC-001：同一口径 + 同一快照，两次发现得到同一候选清单与同一 universe_id。"""
    snapshot = _snapshot(
        _market("BTC", turnover=9_000.0),
        _market("ETH", turnover=5_000.0),
        _market("USDC", turnover=7_000.0),
    )
    criteria = _criteria(turnover_rank_top_n=1)
    first = build_definition(criteria, discover.evaluate(snapshot, criteria))
    second = build_definition(criteria, discover.evaluate(snapshot, criteria))
    assert first.universe_id == second.universe_id
    assert first.payload() == second.payload()


def test_universe_id_moves_when_snapshot_members_move() -> None:
    criteria = _criteria(turnover_rank_top_n=3)
    baseline = build_definition(
        criteria, discover.evaluate(_snapshot(_market("BTC"), _market("ETH")), criteria)
    )
    changed = build_definition(
        criteria,
        discover.evaluate(_snapshot(_market("BTC"), _market("ETH"), _market("SOL")), criteria),
    )
    assert baseline.universe_id != changed.universe_id


def test_evaluation_payload_is_stable_for_identical_inputs() -> None:
    snapshot = _snapshot(_market("BTC"), _market("ETH", listed_days=180))
    criteria = _criteria()
    assert discover.evaluate(snapshot, criteria).payload() == (
        discover.evaluate(snapshot, criteria).payload()
    )


# ---------- T003：交易所接口 fixture（不触网） ----------


class _FakeExchange:
    """固定响应 fixture：形状照 CCXT binanceusdm 的 load_markets + fapiPublicGetKlines。"""

    def __init__(self, markets: dict[str, dict[str, Any]], klines: dict[str, list[list[Any]]]):
        self._markets = markets
        self._klines = klines
        self.calls: list[dict[str, Any]] = []
        self.closed = False
        self.rateLimit = 1

    def load_markets(self):
        return self._markets

    def fapiPublicGetKlines(self, params):
        self.calls.append(params)
        return self._klines[params["symbol"]]

    def close(self):
        self.closed = True


def _binance_market(base: str, *, created_ms: int, symbol_id: str | None = None) -> dict[str, Any]:
    return {
        "symbol": f"{base}/USDT:USDT",
        "id": symbol_id or f"{base}USDT",
        "base": base,
        "quote": "USDT",
        "swap": True,
        "linear": True,
        "contract": True,
        "active": True,
        "created": created_ms,
        "info": {"onboardDate": created_ms},
    }


def _klines(quote_volume: float, days: int) -> list[list[Any]]:
    return [
        [1_700_000_000_000 + index * 86_400_000, 1, 1, 1, 1, 10, 0, quote_volume, 0, 0, 0, 0]
        for index in range(days)
    ]


def test_fetch_snapshot_parses_klines_and_derives_pairs(monkeypatch) -> None:
    monkeypatch.setattr(discover, "_sleep", lambda _seconds: None)
    created_ms = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)
    markets = {
        "BTC/USDT:USDT": _binance_market("BTC", created_ms=created_ms),
        "ETH/USDT:USDT": _binance_market("ETH", created_ms=created_ms),
        # 非 USDT 计价与现货合约都必须被跳过
        "BTC/USDC:USDC": {**_binance_market("BTC", created_ms=created_ms), "quote": "USDC"},
        "SPOT/USDT": {"symbol": "SPOT/USDT", "base": "SPOT", "quote": "USDT", "swap": False},
    }
    klines = {
        "BTCUSDT": _klines(1_000.0, 3),
        "ETHUSDT": _klines(500.0, 3),
    }
    exchange = _FakeExchange(markets, klines)
    snapshot = discover.fetch_snapshot(
        _criteria(turnover_lookback_days=3),
        exchange=exchange,
        now=datetime(2026, 9, 19, tzinfo=UTC),
    )

    assert [record.db_symbol for record in snapshot.markets] == ["BTC/USDT", "ETH/USDT"]
    # 研究数据集 ohlcv_1m 是 spot 命名空间（BTC-USDT）；perp 是 derivatives_* 的命名空间，
    # 口径里的 market_type=perp 只是排名市场，不参与湖内命名
    assert snapshot.markets[0].lake_pair == "BTC-USDT"
    assert snapshot.markets[0].daily_turnover_usdt == (1_000.0, 1_000.0, 1_000.0)
    assert snapshot.snapshot_at == "2026-09-19T00:00:00Z"
    assert snapshot.markets[0].listed_at == "2025-01-01T00:00:00Z"
    assert exchange.closed is False  # 外部注入的实例不由我们发现流程关闭

    evaluation = discover.evaluate(snapshot, _criteria(turnover_lookback_days=3))
    assert evaluation.selected_pairs() == ("BTC/USDT", "ETH/USDT")


def test_fetch_snapshot_lookback_window_truncates_series(monkeypatch) -> None:
    monkeypatch.setattr(discover, "_sleep", lambda _seconds: None)
    created_ms = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)
    exchange = _FakeExchange(
        {"BTC/USDT:USDT": _binance_market("BTC", created_ms=created_ms)},
        {"BTCUSDT": _klines(2_000.0, 5) + _klines(1_000.0, 3)},
    )
    snapshot = discover.fetch_snapshot(
        _criteria(turnover_lookback_days=3),
        exchange=exchange,
        now=datetime(2026, 9, 19, tzinfo=UTC),
    )
    evaluation = discover.evaluate(snapshot, _criteria(turnover_lookback_days=3))
    # 只取最近 3 天：2000,2000,1000,1000,1000,1000,1000,1000 → 末 3 天均值为 1000
    assert evaluation.selected[0].turnover_usdt == 1_000.0
    assert evaluation.selected[0].turnover_points == 3


def test_fetch_snapshot_rejects_missing_onboard_date(monkeypatch) -> None:
    monkeypatch.setattr(discover, "_sleep", lambda _seconds: None)
    market = _binance_market("BTC", created_ms=0)
    market["created"] = None
    market["info"] = {}
    exchange = _FakeExchange({"BTC/USDT:USDT": market}, {"BTCUSDT": _klines(1.0, 1)})
    with pytest.raises(ExchangeUnreachableError, match="onboardDate"):
        discover.fetch_snapshot(
            _criteria(), exchange=exchange, now=datetime(2026, 9, 19, tzinfo=UTC)
        )


def test_fetch_snapshot_rejects_short_kline_rows(monkeypatch) -> None:
    monkeypatch.setattr(discover, "_sleep", lambda _seconds: None)
    created_ms = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)
    exchange = _FakeExchange(
        {"BTC/USDT:USDT": _binance_market("BTC", created_ms=created_ms)},
        {"BTCUSDT": [[1, 1, 1, 1, 1, 1]]},
    )
    with pytest.raises(ExchangeUnreachableError, match="字段不足"):
        discover.fetch_snapshot(
            _criteria(), exchange=exchange, now=datetime(2026, 9, 19, tzinfo=UTC)
        )


def test_fetch_snapshot_rejects_unreachable_exchange() -> None:
    class _Boom:
        rateLimit = 1

        def load_markets(self):
            raise RuntimeError("connection refused")

    with pytest.raises(ExchangeUnreachableError, match="加载"):
        discover.fetch_snapshot(_criteria(), exchange=_Boom())


def test_evaluate_rejects_market_type_mismatch() -> None:
    snapshot = MarketSnapshot(
        exchange="binance", market_type="spot", snapshot_at=SNAPSHOT_AT, markets=()
    )
    with pytest.raises(ExchangeUnreachableError, match="market_type"):
        discover.evaluate(snapshot, _criteria())


def test_criteria_module_exposes_default_path() -> None:
    assert criteria_mod.DEFAULT_CRITERIA_PATH.is_file()
    assert "turnover_rank_top_n" in criteria_mod.DEFAULT_CRITERIA_PATH.read_text(encoding="utf-8")


def test_candidate_payload_round_trips_through_definition() -> None:
    candidate = Candidate(
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT-PERP",
        base="BTC",
        quote="USDT",
        listed_at="2024-01-01T00:00:00Z",
        listed_days=600,
        turnover_usdt=1.5,
        turnover_points=90,
        rank=1,
        excluded_reason=None,
    )
    evaluation = Evaluation(snapshot_at=SNAPSHOT_AT, candidates=(candidate,))
    assert evaluation.payload()["candidates"][0]["turnover_usdt"] == 1.5
