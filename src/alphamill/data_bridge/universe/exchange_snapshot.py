"""交易所侧：拉取 Binance 快照（`discover.py` 的唯一网络路径，拆出以守 350 行上限）。

排名侧取 USDⓈ-M 永续（`underlyingType=COIN` 才是加密资产），**数据侧**取现货命名空间：
研究数据集 `ohlcv_1m` 是 spot，`1000X` 缩放的永续映射到现货 `X`（只在不跨标的名时映射）。
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

from alphamill.data_bridge import symbol_map
from alphamill.data_bridge.universe.canonical import utc_iso
from alphamill.data_bridge.universe.criteria import Criteria
from alphamill.data_bridge.universe.discover import (
    CRYPTO_UNDERLYING,
    DATA_MARKET_TYPE,
    THOUSAND_PREFIX,
    MarketRecord,
    MarketSnapshot,
)
from alphamill.data_bridge.universe.errors import ExchangeUnreachableError
from alphamill.data_bridge.universe.rate_limit import is_retryable_error

#: 逐市场请求的最小间隔（秒）。发现要为每个候选取 90 根日线，市场数几百个：
#: 按 ccxt 的 `rateLimit`（50ms）打会形成 ~15 请求/秒的突发，权重 ~3000/分钟——
#: 2026-09-21 执行机实测就是这个节奏撞上 Binance `-1003`（418，出口 IP 封禁 1 小时）。
#: 默认 1 秒/市场 ⇒ 权重 ≤120/分钟，几百个市场约 5–8 分钟，与长跑回填叠加也安全。
DEFAULT_MARKET_INTERVAL_SECONDS = 1.0
INTERVAL_ENV = "ALPHAMILL_DISCOVER_INTERVAL_SECONDS"

#: 单市场日线的重试次数（瞬时故障退避重试；用尽才判红）
KLINES_ATTEMPTS = 4


def build_exchange(exchange_id: str):
    """构造 ccxt 交易所实例（只读公开行情）。"""
    import ccxt

    exchange_class = getattr(ccxt, exchange_id, None)
    if exchange_class is None:
        raise ExchangeUnreachableError(f"ccxt 不认识交易所 {exchange_id!r}")
    config: dict[str, Any] = {"enableRateLimit": True, "timeout": 30_000}

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
        spot_symbols = {
            str(market["symbol"])
            for market in loaded.values()
            if market.get("spot") and market.get("active") is not False
        }
        records = []
        interval = _market_interval(client)
        for index, market in enumerate(targets):
            if index:
                _sleep(interval)
            records.append(_record_for(client, market, criteria, spot_symbols))
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


def _market_interval(client: Any) -> float:
    """逐市场间隔：不取 ccxt 的 `rateLimit`（太激进，见常量注释），可用环境变量覆盖。"""
    override = os.getenv(INTERVAL_ENV, "").strip()
    if override:
        try:
            return max(0.05, float(override))
        except ValueError as exc:
            raise ExchangeUnreachableError(f"{INTERVAL_ENV} 不是数字: {override!r}") from exc
    return DEFAULT_MARKET_INTERVAL_SECONDS


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


def _record_for(
    client: Any, market: dict[str, Any], criteria: Criteria, spot_symbols: set[str]
) -> MarketRecord:
    base = str(market["base"])
    quote = str(market["quote"])
    rank_symbol = f"{base}/{quote}"
    data_symbol = _data_symbol_for(rank_symbol, spot_symbols)
    db_symbol = data_symbol or rank_symbol
    lake_pair, _ = symbol_map.derive_pairs(db_symbol, DATA_MARKET_TYPE)
    created = market.get("created") or (market.get("info") or {}).get("onboardDate")
    if not created:
        raise ExchangeUnreachableError(f"{market.get('symbol')} 缺少 onboardDate，无法判定上线天数")
    listed_at = datetime.fromtimestamp(int(created) / 1000, tz=UTC)
    return MarketRecord(
        symbol=str(market["symbol"]),
        rank_symbol=rank_symbol,
        db_symbol=db_symbol,
        lake_pair=lake_pair,
        base=base,
        quote=quote,
        underlying_type=str((market.get("info") or {}).get("underlyingType") or CRYPTO_UNDERLYING),
        listed_at=utc_iso(listed_at),
        daily_turnover_usdt=_daily_turnover(client, market, criteria.turnover_lookback_days),
        data_available=data_symbol is not None,
    )


def _klines_with_retry(client: Any, market: dict[str, Any], lookback_days: int) -> Any:
    last: Exception | None = None
    for attempt in range(1, KLINES_ATTEMPTS + 1):
        try:
            # limit 必须是 int：ccxt 在隐式 API 里对 str 会抛 TypeError（真实链路实测）
            return client.fapiPublicGetKlines(
                {"symbol": market["id"], "interval": "1d", "limit": int(lookback_days)}
            )
        except Exception as exc:  # noqa: BLE001 - 判据交给 is_retryable_error
            last = exc
            if not is_retryable_error(exc) or attempt >= KLINES_ATTEMPTS:
                break
            _sleep(min(2**attempt, 30))
    raise ExchangeUnreachableError(
        f"拉取 {market.get('symbol')} 日线成交额失败（重试 {KLINES_ATTEMPTS} 次）: {last}"
    ) from last


def _data_symbol_for(rank_symbol: str, spot_symbols: set[str]) -> str | None:
    """排名侧符号 → 数据侧符号：同名优先；`1000X` 命名的缩放合约映射到现货 `X`。

    只在现货确实存在对应市场时才映射，绝不跨标的猜测（`HYPE` 不会映射到 `HYPER`）。
    """
    if rank_symbol in spot_symbols:
        return rank_symbol
    base, _, quote = rank_symbol.partition("/")
    if base.startswith(THOUSAND_PREFIX) and len(base) > len(THOUSAND_PREFIX):
        candidate = f"{base[len(THOUSAND_PREFIX) :]}/{quote}"
        if candidate in spot_symbols:
            return candidate
    return None


def _daily_turnover(client: Any, market: dict[str, Any], lookback_days: int) -> tuple[float, ...]:
    """USDT 成交额口径：Binance USDM klines 的 quote asset volume（索引 7）。

    瞬时故障按退避重试（实测教训 2026-09-21：解禁后首个请求偶发失败，fail-closed 让
    整轮 6 分钟的发现全废）；重试用尽才判红。**空返回不算错误**——新上线市场本来就可能
    没有日线，记 0 根，由上线天数/排名自然排除（`turnover_points=0` 可审计）。
    """
    rows = _klines_with_retry(client, market, lookback_days)
    if not isinstance(rows, list) or not rows:
        return ()
    values: list[float] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 8:
            raise ExchangeUnreachableError(
                f"{market.get('symbol')} 日线字段不足（需要 quote asset volume）: {row!r}"
            )
        values.append(float(row[7]))
    return tuple(values)
