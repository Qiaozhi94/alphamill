"""Symbol configuration helpers shared by collector entry points."""

from collections.abc import Iterable

DEFAULT_SYMBOLS = ("BTC/USDT", "ETH/USDT")


def parse_symbols(
    value: str | Iterable[str] | None,
    default: Iterable[str] = DEFAULT_SYMBOLS,
) -> list[str]:
    """Return ordered, de-duplicated symbols with basic pair validation."""

    if value is None:
        candidates = list(default)
    elif isinstance(value, str):
        candidates = value.split(",")
    else:
        candidates = list(value)

    symbols: list[str] = []
    seen: set[str] = set()
    for raw in candidates:
        symbol = raw.strip().upper()
        if not symbol:
            continue
        if symbol.count("/") != 1:
            raise ValueError(f"invalid symbol {raw!r}; expected BASE/QUOTE")
        base, quote = symbol.split("/", 1)
        if not base or not quote or ":" in base or ":" in quote:
            raise ValueError(f"invalid symbol {raw!r}; expected BASE/QUOTE")
        if symbol not in seen:
            seen.add(symbol)
            symbols.append(symbol)

    if not symbols:
        raise ValueError("at least one symbol is required")
    return symbols
