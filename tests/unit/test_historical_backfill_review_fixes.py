"""historical_backfill review regression tests."""

from datetime import UTC, datetime

import pytest

from alphamill.data_bridge.collector import historical_backfill as backfill


class _Exchange:
    rateLimit = 0

    def fetch_ohlcv(self, *_args, **_kwargs):
        return []


def test_empty_batch_before_end_is_stalled_not_complete(monkeypatch) -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 0, 2, tzinfo=UTC)
    progress = []
    monkeypatch.setattr(backfill, "load_progress", lambda *_args: (start, 0))
    monkeypatch.setattr(backfill, "save_progress", lambda *args: progress.append(args))

    with pytest.raises(RuntimeError, match="empty OHLCV batch"):
        backfill.fetch_symbol("binance", _Exchange(), object(), "BTC/USDT", start, end)

    assert progress[-1][6] == "stalled"
    assert not any(item[6] == "complete" for item in progress)


def test_retry_count_has_safe_lower_bound() -> None:
    assert backfill.retry_count(0) == 1
    assert backfill.retry_count("-2") == 1
    assert backfill.retry_count(3) == 3
