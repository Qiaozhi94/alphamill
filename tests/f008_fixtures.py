"""F008 测试共享的确定性构造器（unit 与 integration 都用）。

放在 `tests/` 根下而不是某个测试文件里：`tests/unit` 与 `tests/integration` 各自
被 pytest 插入 sys.path，跨目录 `from test_xxx import ...` 会 ImportError。
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge import symbol_map
from alphamill.data_bridge.universe.criteria import Criteria, load_criteria
from alphamill.data_bridge.universe.discover import MarketRecord, MarketSnapshot

SNAPSHOT_AT = "2026-09-19T00:00:00Z"


def market(
    base: str,
    *,
    listed_days: int = 700,
    turnover: float = 1_000_000.0,
    points: int = 90,
    quote: str = "USDT",
    underlying_type: str = "COIN",
    data_available: bool = True,
    data_base: str | None = None,
) -> MarketRecord:
    """构造排名侧市场；`data_base` 用于模拟 1000× 命名映射（如 1000PEPE → PEPE）。"""
    rank_symbol = f"{base}/{quote}"
    db_symbol = f"{data_base or base}/{quote}"
    # 与生产一致：研究数据集 ohlcv_1m 是 spot 命名空间（见 discover.DATA_MARKET_TYPE）
    lake_pair, _ = symbol_map.derive_pairs(db_symbol, "spot")
    listed_at = datetime(2026, 9, 19, tzinfo=UTC).timestamp() - listed_days * 86400
    return MarketRecord(
        symbol=f"{rank_symbol}:{quote}",
        rank_symbol=rank_symbol,
        db_symbol=db_symbol,
        lake_pair=lake_pair,
        base=base,
        quote=quote,
        underlying_type=underlying_type,
        listed_at=datetime.fromtimestamp(listed_at, tz=UTC).isoformat().replace("+00:00", "Z"),
        daily_turnover_usdt=tuple([turnover] * points),
        data_available=data_available,
    )


def snapshot(*records: MarketRecord) -> MarketSnapshot:
    return MarketSnapshot(
        exchange="binance",
        market_type="perp",
        snapshot_at=SNAPSHOT_AT,
        markets=tuple(records),
    )


def criteria_for(**overrides: Any) -> Criteria:
    base = load_criteria()
    return Criteria(
        exchange=overrides.get("exchange", base.exchange),
        market_type=overrides.get("market_type", base.market_type),
        quote_currency=overrides.get("quote_currency", base.quote_currency),
        turnover_lookback_days=overrides.get("turnover_lookback_days", base.turnover_lookback_days),
        turnover_rank_top_n=overrides.get("turnover_rank_top_n", base.turnover_rank_top_n),
        min_listed_days=overrides.get("min_listed_days", base.min_listed_days),
        exclude_rules=overrides.get("exclude_rules", base.exclude_rules),
    )
