"""T013/T014 与 `AC-003`/`AC-010`：分批回填编排、断点续跑与运行记录。

真实库（docker `quant-timescaledb` 的 scratch 库）+ 假交易所：断点续跑、幂等不重复、
失败隔离、`BackfillRun` 落盘与 hostname 都能在开发机上真实取证；交易所交互本身
（真实限流节奏）由 T012 的单元套件与执行机 T020/T021 覆盖。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe.definition import (
    build_definition,
    freeze_definition,
    load_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import (
    BackfillIncompleteError,
    UniverseNotFrozenError,
    WindowError,
)
from alphamill.data_bridge.universe.rate_limit import RateLimiter, RateLimitPolicy
from tests.f008_fixtures import criteria_for as _criteria
from tests.f008_fixtures import market as _market
from tests.f008_fixtures import snapshot as _snapshot

pytestmark = pytest.mark.integration

WINDOW_START = datetime(2026, 9, 1, 0, 0, tzinfo=UTC)
WINDOW_END = datetime(2026, 9, 1, 2, 30, tzinfo=UTC)  # 150 分钟 → 2 批（FETCH_LIMIT=100）


class FakeExchange:
    """按 since 顺序产出 1m K 线；可注入在第 N 次调用上失败。"""

    rateLimit = 1

    def __init__(self, *, fail_on_call: int | None = None, stop_at: datetime | None = None):
        self.calls: list[int] = []
        self.fail_on_call = fail_on_call
        self.stop_at = stop_at or WINDOW_END

    def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=100):
        self.calls.append(since)
        if self.fail_on_call is not None and len(self.calls) == self.fail_on_call:
            raise RuntimeError("injected exchange failure")
        rows = []
        moment = since
        end_ms = int(self.stop_at.timestamp() * 1000)
        while len(rows) < limit and moment < end_ms:
            rows.append([moment, 100.0, 101.0, 99.0, 100.5, 1.0])
            moment += 60_000
        return rows

    def close(self):
        return None


def _frozen_universe(tmp_path: Path, *, pairs=("BTC", "ETH"), freeze: bool = True) -> str:
    criteria = _criteria(turnover_rank_top_n=10)
    snapshot = _snapshot(*[_market(base) for base in pairs])
    definition = build_definition(criteria, evaluate(snapshot, criteria))
    write_definition(definition, tmp_path)
    if freeze:
        freeze_definition(definition.universe_id, frozen_by="tester", lake_root=tmp_path)
    return definition.universe_id


def _limiter() -> RateLimiter:
    """共享限速器：注入假时钟与空 sleep，测试里不做真实等待。"""
    return RateLimiter(
        RateLimitPolicy(min_interval_seconds=0.0, max_retries=1),
        clock=lambda: 0.0,
        sleep=lambda _seconds: None,
    )


def _count_rows(conn, symbol: str) -> tuple[int, int]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*), count(DISTINCT time) FROM ohlcv_1m"
            " WHERE exchange = %s AND symbol = %s",
            ("binance", symbol),
        )
        total, distinct = cur.fetchone()
    return int(total), int(distinct)


def test_backfill_interrupt_then_resume_without_duplicates(f008_conn, tmp_path) -> None:
    """AC-003：跑到一半被打断 → 重跑从断点继续、不写重复行、最终行数与预期一致。"""
    universe_id = _frozen_universe(tmp_path)
    plans = runner.plan_batch(load_definition(universe_id, tmp_path))
    interrupted = FakeExchange(fail_on_call=2)
    first = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=interrupted,
        limiter=_limiter(),
        hostname="qiaozhi-gp",
    )
    assert "BTC/USDT" in first.failed_pairs() or "ETH/USDT" in first.failed_pairs()
    first_rows = _count_rows(f008_conn, "BTC/USDT")
    assert first_rows[0] == 100  # 第一批已落库

    second = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=FakeExchange(),
        limiter=_limiter(),
        hostname="qiaozhi-gp",
        resume_run_id=first.run_id,
    )
    total, distinct = _count_rows(f008_conn, "BTC/USDT")
    assert total == distinct == 150  # (WINDOW_END - WINDOW_START) / 1m
    assert second.pending() == ()
    assert second.failed_pairs() == ()


def test_failed_pair_does_not_block_the_other(f008_conn, tmp_path) -> None:
    """NFR-002：单 pair 失败隔离，其他 pair 照常完成并留各自进度。"""
    universe_id = _frozen_universe(tmp_path)
    definition = load_definition(universe_id, tmp_path)
    plans = runner.plan_batch(definition)
    exchange = FakeExchange()
    original = exchange.fetch_ohlcv

    def selective(symbol, **kwargs):
        if symbol == "BTC/USDT":
            raise RuntimeError("injected failure for BTC")
        return original(symbol, **kwargs)

    exchange.fetch_ohlcv = selective  # type: ignore[method-assign]
    run = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=exchange,
        limiter=_limiter(),
        hostname="qiaozhi-gp",
    )
    assert run.failed_pairs() == ("BTC/USDT",)
    assert _count_rows(f008_conn, "ETH/USDT")[0] == 150
    assert _count_rows(f008_conn, "BTC/USDT")[0] == 0


def test_run_record_and_events_carry_hostname_and_pair(f008_conn, tmp_path) -> None:
    """AC-010：运行记录与进度事件可按 run/pair 查询且标注 hostname。"""
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    events: list[tuple[str, dict]] = []
    run = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=runner.plan_batch(definition),
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=FakeExchange(),
        limiter=_limiter(),
        hostname="qiaozhi-gp",
        event_sink=lambda kind, payload: events.append((kind, payload)),
    )
    loaded = runner.load_run(run.run_id, tmp_path / "reports")
    assert loaded.hostname == "qiaozhi-gp"
    assert loaded.pairs[0]["status"] == "completed"
    assert loaded.pairs[0]["rows"] == 150
    assert loaded.window_start == "2026-09-01T00:00:00Z"
    assert (tmp_path / "reports" / run.run_id / "run.json").is_file()

    kinds = [kind for kind, _ in events]
    # 进度事件按 pair 粒度落盘（design §4）：一个 pair 完成即一条 progress
    assert kinds == ["backfill.progress"]
    assert all(payload["run_id"] == run.run_id for _, payload in events)
    assert all(payload["lake_pair"] == "BTC-USDT-PERP" for _, payload in events)
    assert all(payload["hostname"] == "qiaozhi-gp" for _, payload in events)
    assert events[-1][1]["rows"] == 150


def test_unfrozen_universe_is_refused(f008_conn, tmp_path) -> None:
    universe_id = _frozen_universe(tmp_path, freeze=False)
    with pytest.raises(UniverseNotFrozenError):
        runner.run_backfill_batch(
            universe_id=universe_id,
            plans=(),
            start=WINDOW_START,
            end=WINDOW_END,
            conn=f008_conn,
            lake_root=tmp_path,
            reports_dir=tmp_path / "reports",
            exchange=FakeExchange(),
            limiter=_limiter(),
        )


def test_invalid_window_is_refused_before_any_write(f008_conn, tmp_path) -> None:
    with pytest.raises(WindowError, match="必须早于"):
        runner.run_backfill_batch(
            universe_id="sha256:" + "0" * 64,
            plans=[],
            start=WINDOW_END,
            end=WINDOW_START,
            conn=f008_conn,
            lake_root=tmp_path,
            reports_dir=tmp_path / "reports",
        )


def test_empty_batch_is_refused(f008_conn, tmp_path) -> None:
    universe_id = _frozen_universe(tmp_path)
    with pytest.raises(BackfillIncompleteError):
        runner.run_backfill_batch(
            universe_id=universe_id,
            plans=(),
            start=WINDOW_START,
            end=WINDOW_END,
            conn=f008_conn,
            lake_root=tmp_path,
            reports_dir=tmp_path / "reports",
            exchange=FakeExchange(),
            limiter=_limiter(),
        )


def test_plan_batch_splits_by_rank_and_validates_pairs(tmp_path) -> None:
    universe_id = _frozen_universe(tmp_path, pairs=("BTC", "ETH", "SOL"))
    definition = load_definition(universe_id, tmp_path)
    assert [plan.db_symbol for plan in runner.plan_batch(definition, batch=1, batch_split=2)] == [
        "BTC/USDT",
        "ETH/USDT",
    ]
    assert [plan.db_symbol for plan in runner.plan_batch(definition, batch=2, batch_split=2)] == [
        "SOL/USDT",
    ]
    with pytest.raises(WindowError, match="不在宇宙定义内"):
        runner.plan_batch(definition, pairs=["DOGE/USDT"])
    assert len(runner.plan_batch(definition, pairs=["ETH/USDT"])) == 1


def test_artifact_publish_after_backfill_matches_membership(f008_conn, tmp_path) -> None:
    """回填完成后可发布台账 artifact，且发布是幂等的（同内容同 digest）。"""
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    runner.run_backfill_batch(
        universe_id=universe_id,
        plans=runner.plan_batch(definition),
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=FakeExchange(),
        limiter=_limiter(),
    )
    from alphamill.data_bridge.universe.membership import TradabilityInterval

    intervals = [
        TradabilityInterval(lake_pair="BTC-USDT-PERP", valid_from=WINDOW_START, valid_to=None)
    ]
    first, path = artifact_mod.publish_artifact(intervals, tmp_path)
    second, _ = artifact_mod.publish_artifact(intervals, tmp_path)
    assert first == second
    assert path.name == f"{first}.json"
    assert artifact_mod.load_artifact(first, tmp_path).universe_at(
        WINDOW_START + timedelta(minutes=1)
    ) == frozenset({"BTC-USDT-PERP"})
