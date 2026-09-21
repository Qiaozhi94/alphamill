"""宇宙发现：按口径从交易所公开行情筛候选（`FR-001` / `AC-001` / T004）。

三层分工，让「可复现」成为结构性质而不是口号：

- `MarketRecord` / `MarketSnapshot`：交易所数据的**规范化快照**（纯数据、可落盘、可复算）；
- `evaluate(snapshot, criteria)`：**纯函数**——同一快照 + 同一口径必然得到同一候选清单
  与同一 `universe_id`（`AC-001`），且候选按成交额排名有序（供批次切分）；
- `fetch_snapshot(criteria, ...)`：**唯一网络路径**（ccxt 隐式 API 取 USDT 成交额口径），
  失败一律抛 `ExchangeUnreachableError`，不降级、不拿 24h ticker 顶替 90 天口径。

排除规则的判别数据（稳定币集合、指数篮子、杠杆代币后缀）是本模块常量而非口径文件的一部分：
口径文件只登记**规则名**（`DR-001` 的 `exclude_rules`），规则内容随代码评审演进。杠杆代币
后缀另加「标的段 ≥3 字符」护栏，避免把 `JUP` 这类正常代币误判成 `UP` 结尾的杠杆代币。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from alphamill.data_bridge.universe.canonical import parse_utc, utc_iso
from alphamill.data_bridge.universe.criteria import Criteria
from alphamill.data_bridge.universe.errors import ExchangeUnreachableError

STABLECOIN_BASES = frozenset(
    {
        "USDT",
        "USDC",
        "FDUSD",
        "BUSD",
        "TUSD",
        "USDP",
        "DAI",
        "USD1",
        "EUR",
        "EURI",
        "AEUR",
    }
)
INDEX_BASKET_BASES = frozenset({"BTCDOM", "DEFI"})
LEVERAGED_SUFFIXES = ("BULL", "BEAR", "DOWN", "UP")
MIN_LEVERAGED_UNDERLYING = 3

#: 研究数据集 `ohlcv_1m` 的湖内命名空间是 **spot**（`derivatives_*` 才是 perp）；口径里的
#: `market_type` 是**排名市场**。两者混用会让候选 lake_pair 与湖内分区对不上（F003 的张量
#: 掩码按 `lake_pair` 过滤）；准入时按同一 `db_symbol` 同源派生出 perp 命名空间一并进台账。
DATA_MARKET_TYPE = "spot"
LAKE_MARKET_TYPES = ("spot", "perp")

REASON_STABLECOIN = "stablecoin_pair"
REASON_LEVERAGED = "leveraged_token"
REASON_INDEX = "index_basket"
REASON_TRADFI = "tokenized_tradfi"
REASON_LISTED_DAYS = "listed_days_not_enough"
REASON_NO_SPOT = "no_spot_market"
REASON_DUPLICATE_DATA = "duplicate_data_pair"
REASON_RANK = "rank_below_top_n"

#: 加密资产的判别：Binance USDM 的 `underlyingType` 为 `COIN` 才是加密永续；
#: `EQUITY` / `COMMODITY`（配 `contractType=TRADIFI_PERPETUAL`）是代币化股票与商品。
CRYPTO_UNDERLYING = "COIN"

#: 1000× 命名约定：永续 `1000PEPE` 对应现货 `PEPE`（单位缩放，同一标的）。
#: 仅在「去前缀后确实存在现货市场」时才做映射，且不跨标的猜测（HYPE ≠ HYPER）。
THOUSAND_PREFIX = "1000"
_TURNOVER_DECIMALS = 6


@dataclass(frozen=True, kw_only=True)
class MarketRecord:
    """单个市场快照：`daily_turnover_usdt` 为按日 USDT 成交额（旧→新）。

    `rank_symbol` 是**排名侧**（USDⓈ-M 永续）的 db symbol；`db_symbol`/`lake_pair` 是
    **数据侧**（研究数据集 `ohlcv_1m` 的现货命名空间，含 1000× 命名映射）。
    `data_available=False` 表示数据路线取不到这个标的（只有永续、无现货）。
    """

    symbol: str
    rank_symbol: str
    db_symbol: str
    lake_pair: str
    base: str
    quote: str
    underlying_type: str
    listed_at: str
    daily_turnover_usdt: tuple[float, ...]
    data_available: bool


@dataclass(frozen=True, kw_only=True)
class MarketSnapshot:
    """一次交易所快照；`snapshot_at` 是候选清单可复现的锚点。"""

    exchange: str
    market_type: str
    snapshot_at: str
    markets: tuple[MarketRecord, ...]

    def payload(self) -> dict[str, Any]:
        return {
            "exchange": self.exchange,
            "market_type": self.market_type,
            "snapshot_at": self.snapshot_at,
            "markets": [
                {
                    "symbol": record.symbol,
                    "rank_symbol": record.rank_symbol,
                    "db_symbol": record.db_symbol,
                    "lake_pair": record.lake_pair,
                    "base": record.base,
                    "quote": record.quote,
                    "underlying_type": record.underlying_type,
                    "listed_at": record.listed_at,
                    "daily_turnover_usdt": list(record.daily_turnover_usdt),
                    "data_available": record.data_available,
                }
                for record in self.markets
            ],
        }


@dataclass(frozen=True, kw_only=True)
class Candidate:
    """逐候选筛选指标（含被排除者与原因），`DR-001` 要求全部入档。"""

    db_symbol: str
    rank_symbol: str
    lake_pair: str
    base: str
    quote: str
    listed_at: str
    listed_days: int
    turnover_usdt: float
    turnover_points: int
    rank: int | None
    excluded_reason: str | None

    def payload(self) -> dict[str, Any]:
        return {
            "db_symbol": self.db_symbol,
            "rank_symbol": self.rank_symbol,
            "lake_pair": self.lake_pair,
            "base": self.base,
            "quote": self.quote,
            "listed_at": self.listed_at,
            "listed_days": self.listed_days,
            "turnover_usdt": self.turnover_usdt,
            "turnover_points": self.turnover_points,
            "rank": self.rank,
            "excluded_reason": self.excluded_reason,
        }


@dataclass(frozen=True, kw_only=True)
class Evaluation:
    """发现结果：候选按排名有序，未入选者带原因码排在后面。"""

    snapshot_at: str
    candidates: tuple[Candidate, ...]

    @property
    def selected(self) -> tuple[Candidate, ...]:
        return tuple(item for item in self.candidates if item.rank is not None)

    def selected_pairs(self) -> tuple[str, ...]:
        return tuple(item.db_symbol for item in self.selected)

    def payload(self) -> dict[str, Any]:
        return {
            "snapshot_at": self.snapshot_at,
            "candidates": [item.payload() for item in self.candidates],
        }


def evaluate(snapshot: MarketSnapshot, criteria: Criteria) -> Evaluation:
    """纯函数：快照 + 口径 → 有序候选清单（含排除者与原因）"""
    if snapshot.market_type != criteria.market_type:
        raise ExchangeUnreachableError(
            f"快照 market_type={snapshot.market_type!r} 与口径 {criteria.market_type!r} 不一致"
        )
    snapshot_at = parse_utc(snapshot.snapshot_at, field="snapshot.snapshot_at")
    rows: list[Candidate] = []
    for market in snapshot.markets:
        if market.quote.upper() != criteria.quote_currency:
            continue
        listed_at = parse_utc(market.listed_at, field=f"{market.rank_symbol}.listed_at")
        listed_days = int((snapshot_at - listed_at).total_seconds() // 86400)
        window = market.daily_turnover_usdt[-criteria.turnover_lookback_days :]
        turnover = round(sum(window) / len(window) if window else 0.0, _TURNOVER_DECIMALS)
        reason = _structural_exclusion(
            market.base, market.quote, criteria.exclude_rules, market.underlying_type
        )
        if reason is None and listed_days <= criteria.min_listed_days:
            reason = REASON_LISTED_DAYS
        if reason is None and not market.data_available:
            # 数据可达性前置：只有永续、现货取不到数的标的进不了研究宇宙
            reason = REASON_NO_SPOT
        rows.append(
            Candidate(
                db_symbol=market.db_symbol,
                rank_symbol=market.rank_symbol,
                lake_pair=market.lake_pair,
                base=market.base,
                quote=market.quote,
                listed_at=utc_iso(listed_at),
                listed_days=listed_days,
                turnover_usdt=turnover,
                turnover_points=len(window),
                rank=None,
                excluded_reason=reason,
            )
        )

    rows = _dedupe_data_pairs(rows)
    eligible = [row for row in rows if row.excluded_reason is None]
    eligible.sort(key=lambda row: (-row.turnover_usdt, row.db_symbol))
    ranked: list[Candidate] = []
    for index, row in enumerate(eligible, start=1):
        inside = index <= criteria.turnover_rank_top_n
        ranked.append(
            Candidate(
                db_symbol=row.db_symbol,
                rank_symbol=row.rank_symbol,
                lake_pair=row.lake_pair,
                base=row.base,
                quote=row.quote,
                listed_at=row.listed_at,
                listed_days=row.listed_days,
                turnover_usdt=row.turnover_usdt,
                turnover_points=row.turnover_points,
                rank=index if inside else None,
                excluded_reason=None if inside else REASON_RANK,
            )
        )
    dropped = sorted(
        (row for row in rows if row.excluded_reason is not None), key=lambda row: row.db_symbol
    )
    return Evaluation(snapshot_at=utc_iso(snapshot_at), candidates=tuple(ranked) + tuple(dropped))


def _dedupe_data_pairs(rows: list[Candidate]) -> list[Candidate]:
    """多个永续映射到同一数据侧 pair 时（如 1000× 与基础符号并存）只保留流动性最高者。"""
    best: dict[str, Candidate] = {}
    for row in rows:
        if row.excluded_reason is not None:
            continue
        current = best.get(row.lake_pair)
        if current is None or row.turnover_usdt > current.turnover_usdt:
            best[row.lake_pair] = row
    out: list[Candidate] = []
    for row in rows:
        winner = best.get(row.lake_pair)
        if row.excluded_reason is None and winner is not None and winner is not row:
            out.append(_with_reason(row, REASON_DUPLICATE_DATA))
            continue
        out.append(row)
    return out


def _with_reason(row: Candidate, reason: str) -> Candidate:
    return Candidate(
        db_symbol=row.db_symbol,
        rank_symbol=row.rank_symbol,
        lake_pair=row.lake_pair,
        base=row.base,
        quote=row.quote,
        listed_at=row.listed_at,
        listed_days=row.listed_days,
        turnover_usdt=row.turnover_usdt,
        turnover_points=row.turnover_points,
        rank=None,
        excluded_reason=reason,
    )


def _structural_exclusion(
    base: str, quote: str, rules: tuple[str, ...], underlying_type: str = CRYPTO_UNDERLYING
) -> str | None:
    """结构性重复标的的排除判定。

    稳定币规则只看 **base**：全线以 `USDT` 计价是常态，把 quote 也算进去会把整个
    宇宙排空（`BTCDOM/USDT`、`BTC/USDT` 都会被误判）。代币化 TradFi（`underlyingType`
    为 `EQUITY`/`COMMODITY`）不是加密资产，按规则名 `tokenized_tradfi` 排除。
    """
    if REASON_TRADFI in rules and underlying_type.upper() != CRYPTO_UNDERLYING:
        return REASON_TRADFI
    upper_base = base.upper()
    if REASON_STABLECOIN in rules and upper_base in STABLECOIN_BASES:
        return REASON_STABLECOIN
    if REASON_LEVERAGED in rules:
        for suffix in LEVERAGED_SUFFIXES:
            underlying_len = len(upper_base) - len(suffix)
            if upper_base.endswith(suffix) and underlying_len >= MIN_LEVERAGED_UNDERLYING:
                return REASON_LEVERAGED
    if REASON_INDEX in rules and upper_base in INDEX_BASKET_BASES:
        return REASON_INDEX
    return None
