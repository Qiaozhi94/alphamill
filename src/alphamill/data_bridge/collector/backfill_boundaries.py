"""Explicit exchange-availability boundaries used by F001 backfills."""

from __future__ import annotations

from datetime import datetime, timedelta


def parse_symbol_listing_starts(raw: str) -> dict[str, datetime]:
    """Parse ``SYMBOL=ISO_TIMESTAMP`` entries from a comma-separated setting."""
    result: dict[str, datetime] = {}
    for item in raw.split(","):
        item = item.strip()
        if not item or "=" not in item:
            continue
        symbol, value = item.split("=", 1)
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError(f"listing start must include a timezone: {symbol}")
        result[symbol.strip()] = parsed
    return result


def listing_start_for(symbol: str, window_start: datetime, raw: str = "") -> datetime:
    listing_start = parse_symbol_listing_starts(raw).get(symbol)
    if listing_start is None:
        return window_start
    return max(window_start, listing_start.astimezone(window_start.tzinfo))


def parse_unavailable_symbols(raw: str) -> set[str]:
    return {item.strip() for item in raw.split(",") if item.strip()}


def effective_derivative_window(
    dataset: str, window_start: datetime, window_end: datetime, max_open_interest_days: int = 0
) -> tuple[datetime, datetime]:
    """Return the explicit exchange-available interval for a derivative dataset."""
    if dataset == "open_interest" and max_open_interest_days > 0:
        return max(window_start, window_end - timedelta(days=max_open_interest_days)), window_end
    return window_start, window_end
