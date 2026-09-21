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
from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge import symbol_map
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
REASON_LISTED_DAYS = "listed_days_not_enough"
REASON_RANK = "rank_below_top_n"
_TURNOVER_DECIMALS = 6


@dataclass(frozen=True, kw_only=True)
class MarketRecord:
    """单个市场的规范化快照：`daily_turnover_usdt` 为按日 USDT 成交额（旧→新）。"""

    symbol: str
    db_symbol: str
    lake_pair: str
    base: str
    quote: str
    listed_at: str
    daily_turnover_usdt: tuple[float, ...]


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
                    "db_symbol": record.db_symbol,
                    "lake_pair": record.lake_pair,
                    "base": record.base,
                    "quote": record.quote,
                    "listed_at": record.listed_at,
                    "daily_turnover_usdt": list(record.daily_turnover_usdt),
                }
                for record in self.markets
            ],
        }


@dataclass(frozen=True, kw_only=True)
class Candidate:
    """逐候选筛选指标（含被排除者与原因），`DR-001` 要求全部入档。"""

    db_symbol: str
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
        listed_at = parse_utc(market.listed_at, field=f"{market.db_symbol}.listed_at")
        listed_days = int((snapshot_at - listed_at).total_seconds() // 86400)
        window = market.daily_turnover_usdt[-criteria.turnover_lookback_days :]
        turnover = round(
            sum(window) / len(window) if window else 0.0,
            _TURNOVER_DECIMALS,
        )
        reason = _structural_exclusion(market.base, market.quote, criteria.exclude_rules)
        if reason is None and listed_days <= criteria.min_listed_days:
            reason = REASON_LISTED_DAYS
        rows.append(
            Candidate(
                db_symbol=market.db_symbol,
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

    eligible = [row for row in rows if row.excluded_reason is None]
    eligible.sort(key=lambda row: (-row.turnover_usdt, row.db_symbol))
    ranked: list[Candidate] = []
    for index, row in enumerate(eligible, start=1):
        inside = index <= criteria.turnover_rank_top_n
        ranked.append(
            Candidate(
                db_symbol=row.db_symbol,
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


def _structural_exclusion(base: str, quote: str, rules: tuple[str, ...]) -> str | None:
    """结构性重复标的的排除判定。

    稳定币规则只看 **base**：全线以 `USDT` 计价是常态，把 quote 也算进去会把整个
    宇宙排空（`BTCDOM/USDT`、`BTC/USDT` 都会被误判）。
    """
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


def build_exchange(exchange_id: str):
    """构造 ccxt 交易所实例（只读公开行情）。"""
    import ccxt

    exchange_class = getattr(ccxt, exchange_id, None)
    if exchange_class is None:
        raise ExchangeUnreachableError(f"ccxt 不认识交易所 {exchange_id!r}")
    config: dict[str, Any] = {"enableRateLimit": True, "timeout": 30_000}
    import os

    proxy = os.getenv(f"{exchange_id.upper()}_HTTPS_PROXY", "").strip()
    if proxy:
        config["httpsProxy"] = proxy
    return exchange_class(config)


def fetch_snapshot(
    criteria: Criteria,
    *,
    exchange: Any | None = None,
    now: datetime | None = None,
) -> MarketSnapshot:
    """唯一网络路径：拉取目标市场日线成交额，产出规范化快照。"""
    if criteria.market_type != "perp":
        raise ExchangeUnreachableError(
            f"发现仅实现 USDⓈ-M 永续路线（market_type=perp），得到 {criteria.market_type!r}"
        )
    owned = exchange is None
    client = exchange if exchange is not None else build_exchange(criteria.exchange)
    try:
        try:
            loaded = client.load_markets()
        except Exception as exc:  # noqa: BLE001 - 交易所不可达一律启动期拒绝
            raise ExchangeUnreachableError(f"加载 {criteria.exchange} 市场失败: {exc}") from exc
        targets = sorted(
            (market for market in loaded.values() if _is_target_market(market, criteria)),
            key=lambda market: market["symbol"],
        )
        if not targets:
            raise ExchangeUnreachableError(
                f"{criteria.exchange} 没有 {criteria.quote_currency} 线性永续市场可选"
            )
        records = []
        interval = (getattr(client, "rateLimit", None) or 200) / 1000
        for index, market in enumerate(targets):
            if index:
                _sleep(interval)
            records.append(_record_for(client, market, criteria))
    finally:
        if owned:
            close = getattr(client, "close", None)
            if callable(close):
                close()
    moment = now or datetime.now(UTC)
    return MarketSnapshot(
        exchange=criteria.exchange,
        market_type=criteria.market_type,
        snapshot_at=utc_iso(moment.astimezone(UTC)),
        markets=tuple(records),
    )


def _sleep(seconds: float) -> None:
    import time

    time.sleep(seconds)  # 测试注入点


def _is_target_market(market: dict[str, Any], criteria: Criteria) -> bool:
    return bool(
        market.get("swap")
        and market.get("linear")
        and market.get("contract")
        and market.get("active") is not False
        and str(market.get("quote", "")).upper() == criteria.quote_currency
    )


def _record_for(client: Any, market: dict[str, Any], criteria: Criteria) -> MarketRecord:
    base = str(market["base"])
    quote = str(market["quote"])
    db_symbol = f"{base}/{quote}"
    lake_pair, _ = symbol_map.derive_pairs(db_symbol, DATA_MARKET_TYPE)
    created = market.get("created") or (market.get("info") or {}).get("onboardDate")
    if not created:
        raise ExchangeUnreachableError(f"{market.get('symbol')} 缺少 onboardDate，无法判定上线天数")
    listed_at = datetime.fromtimestamp(int(created) / 1000, tz=UTC)
    return MarketRecord(
        symbol=str(market["symbol"]),
        db_symbol=db_symbol,
        lake_pair=lake_pair,
        base=base,
        quote=quote,
        listed_at=utc_iso(listed_at),
        daily_turnover_usdt=_daily_turnover(client, market, criteria.turnover_lookback_days),
    )


def _daily_turnover(client: Any, market: dict[str, Any], lookback_days: int) -> tuple[float, ...]:
    """USDT 成交额口径：Binance USDM klines 的 quote asset volume（索引 7）。"""
    try:
        # limit 必须是 int：ccxt 在隐式 API 里对 str 会抛 TypeError（真实链路实测）
        rows = client.fapiPublicGetKlines(
            {"symbol": market["id"], "interval": "1d", "limit": int(lookback_days)}
        )
    except Exception as exc:  # noqa: BLE001 - 单市场失败即启动期拒绝，不静默补零
        raise ExchangeUnreachableError(
            f"拉取 {market.get('symbol')} 日线成交额失败: {exc}"
        ) from exc
    if not isinstance(rows, list) or not rows:
        raise ExchangeUnreachableError(f"{market.get('symbol')} 日线返回为空，无法计算成交额")
    values: list[float] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 8:
            raise ExchangeUnreachableError(
                f"{market.get('symbol')} 日线字段不足（需要 quote asset volume）: {row!r}"
            )
        values.append(float(row[7]))
    return tuple(values)
