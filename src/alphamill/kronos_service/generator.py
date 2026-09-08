from statistics import mean


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def generate_placeholder_signal(rows: list[dict]) -> dict:
    if len(rows) < 30:
        return {
            "signal_type": "neutral",
            "confidence": 0.0,
            "expected_return": 0.0,
            "volatility": 0.0,
            "direction_prob": 0.5,
            "reason": "not_enough_data",
        }

    closes = [float(row["close"]) for row in rows]
    returns = [
        (closes[idx] / closes[idx - 1]) - 1 for idx in range(1, len(closes)) if closes[idx - 1] != 0
    ]
    short_return = (closes[-1] / closes[-12]) - 1 if closes[-12] else 0.0
    avg_return = mean(returns[-30:]) if returns else 0.0
    volatility = mean(abs(value) for value in returns[-30:]) if returns else 0.0

    expected_return = (short_return * 0.7) + (avg_return * 0.3)
    confidence = min(abs(expected_return) / max(volatility, 1e-8), 1.0)
    direction_prob = clamp(0.5 + (expected_return / max(volatility, 1e-8)) * 0.25)

    if expected_return > 0.001:
        signal_type = "buy"
    elif expected_return < -0.001:
        signal_type = "sell"
    else:
        signal_type = "neutral"

    return {
        "signal_type": signal_type,
        "confidence": round(confidence, 6),
        "expected_return": round(expected_return, 8),
        "volatility": round(volatility, 8),
        "direction_prob": round(direction_prob, 6),
        "reason": "placeholder_momentum",
    }
