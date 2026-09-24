"""T013/T014 与 `AC-003`/`AC-010`：分批回填编排、断点续跑与运行记录。

真实库（docker `quant-timescaledb` 的 scratch 库）+ 假交易所：断点续跑、幂等不重复、
失败隔离、`BackfillRun` 落盘与 hostname 都能在开发机上真实取证；交易所交互本身
（真实限流节奏）由 T012 的单元套件与执行机 T020/T021 覆盖。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import psycopg2
import pytest

from alphamill.data_bridge.collector import backfill_orchestrator
from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe import cli, events
from alphamill.data_bridge.universe.admission import (
    STEP_ADMISSION,
    STEP_ARTIFACT,
    STEP_LEDGER,
    admit_pair,
)
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
from alphamill.data_bridge.universe.event_sink import backfill_sink
from alphamill.data_bridge.universe.quality_gate import (
    VERDICT_ACTIVE,
    VERDICT_INCOMPLETE,
    VERDICT_QUARANTINED,
    PairGateResult,
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


def test_run_record_carries_hostname_and_events_are_contract_shaped(f008_conn, tmp_path) -> None:
    """AC-010：运行记录可按 run/pair 查询且标注 hostname；事件载荷严格等于冻结键集合。

    hostname 归 `BackfillRun` 运行记录（design §4 / T014），**不进**事件流——事件契约是
    精确键集合，多一个 `hostname`/`status` 就 `EventsError`（`events.py` docstring）。
    """
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    sink_calls: list[tuple[str, dict]] = []
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
        event_sink=lambda kind, payload: sink_calls.append((kind, payload)),
    )
    loaded = runner.load_run(run.run_id, tmp_path / "reports")
    assert loaded.hostname == "qiaozhi-gp"
    assert loaded.pairs[0]["status"] == "completed"
    assert loaded.pairs[0]["rows"] == 150
    assert loaded.window_start == "2026-09-01T00:00:00Z"
    assert (tmp_path / "reports" / run.run_id / "run.json").is_file()

    kinds = [kind for kind, _ in sink_calls]
    # 进度事件按 pair 粒度落盘（design §4）：一个 pair 完成即一条 progress
    assert kinds == ["backfill.progress"]
    assert all(payload["run_id"] == run.run_id for _, payload in sink_calls)
    assert all(payload["lake_pair"] == "BTC-USDT" for _, payload in sink_calls)
    assert all(set(payload) == set(events.PAYLOAD_FIELDS[kind]) for kind, payload in sink_calls), (
        "事件载荷必须逐个精确命中冻结键集合（多/少一个都判红）"
    )
    assert all("hostname" not in payload for _, payload in sink_calls)
    assert sink_calls[-1][1]["rows"] == 150
    assert sink_calls[-1][1]["elapsed"] >= 0.0


def test_already_complete_pair_is_skipped_without_fetching(f008_conn, tmp_path) -> None:
    """账本说 complete 的 pair 不再触网（数据已在库），但仍记为 completed 并留痕。"""
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    with f008_conn.cursor() as cur:
        for minute in range(5):
            cur.execute(
                "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
                " VALUES (%s, 'binance', 'BTC/USDT', 100, 101, 99, 100, 1)",
                (WINDOW_START + timedelta(minutes=minute),),
            )
        cur.execute(
            "INSERT INTO backfill_progress (exchange, symbol, timeframe, target_start,"
            " target_end, next_since, status, rows_upserted)"
            " VALUES ('binance', 'BTC/USDT', '1m', %s, %s, %s, 'complete', 900719)",
            (WINDOW_START, WINDOW_END, WINDOW_END),
        )
    f008_conn.commit()

    exchange = FakeExchange()
    exchange.fetch_ohlcv = lambda *a, **k: pytest.fail("已完成的 pair 不应再触网")  # type: ignore[method-assign]
    run = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=runner.plan_batch(definition),
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=exchange,
        limiter=_limiter(),
    )
    assert run.failed_pairs() == ()
    entry = run.pairs[0]
    assert entry["status"] == "completed"
    assert entry["note"] == "already_complete"
    # rows 取库内实测（5 行），ledger_rows 才是账本里的历史计数 —— 两者不一致时以实测为准
    assert entry["rows"] == 5
    assert entry["ledger_rows"] == 900719


def test_time_boxed_chunks_defer_and_resume(f008_conn, tmp_path) -> None:
    """时间片到点：当前 pair 记 deferred 并保留断点，下一片续完且不重复（长跑分片执行）。

    **必须带生产 sink**（检视 R2-B1）：时间片到点时尚未开跑的 pair 的 `last_cursor` 是 `None`，
    而事件契约的 `cursor` 不可空（`last_cursor` 才可空）——照发会让**每个分片到点即以
    `E_UNIVERSE_EVENTS` 中止**。`_emit` 现在对「无游标的非失败结果」不发 progress 事件；
    变异：把该跳过改掉，本用例红（事件目录由 `f008_conn` 改道到 tmp_path）。
    """
    universe_id = _frozen_universe(tmp_path, pairs=("BTC", "ETH"))
    definition = load_definition(universe_id, tmp_path)
    plans = runner.plan_batch(definition)

    first = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=FakeExchange(),
        limiter=_limiter(),
        event_sink=backfill_sink(),  # 生产接线（缺省 None 是库调用者的旁路）
        max_runtime_seconds=0.0,  # 立刻到点：第一个 pair 还没抓就 deferred
    )
    statuses = {item["db_symbol"]: item["status"] for item in first.pairs}
    assert "deferred" in statuses.values()
    assert first.failed_pairs() == ()  # 时间片到点不是失败
    assert set(first.pending()) == {"BTC/USDT", "ETH/USDT"}

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
        resume_run_id=first.run_id,
    )
    assert second.pending() == ()
    for symbol in ("BTC/USDT", "ETH/USDT"):
        total, distinct = _count_rows(f008_conn, symbol)
        assert total == distinct == 150, symbol


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
    with pytest.raises(WindowError, match="不在本宇宙的入选集内"):
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


# ---------------- 检视修复：事件平面的生产接线与契约形状（TR-001 / TR-002 / AC-010）


def test_production_backfill_path_appends_contract_events_on_disk(
    f008_conn, tmp_path, monkeypatch
) -> None:
    """TR-002/AC-010：生产 sink（`cli._backfill` 用的同一工厂）真接线后事件落盘并可读回。

    不注入测试 lambda：`tests/integration/test_f008_backfill.py` 里此前只有自注入 sink 的
    自证，生产路径一行事件都没落过——那正是这轮检视的 High 发现。事件目录用
    `ALPHAMILL_EVENTS_DIR` 改道到 `tmp_path`（不写仓库默认 `reports/universe/events/`）。
    """
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "events"))
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
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
        event_sink=backfill_sink(),
    )
    progress = events.read_events(events.EVENT_BACKFILL_PROGRESS, run_id=run.run_id)
    assert [item.lake_pair for item in progress] == ["BTC-USDT"]
    assert progress[0].rows == 150
    assert progress[0].cursor == "2026-09-01T02:30:00Z"  # 断点 = 窗口终点
    assert progress[0].elapsed >= 0.0
    assert (tmp_path / "events" / f"{events.EVENT_BACKFILL_PROGRESS}{events.SUFFIX}").is_file()


def test_cli_backfill_wiring_persists_events_without_injected_sink(
    f008_conn, f002_db, tmp_path, monkeypatch, capsys
) -> None:
    """`IR-001`/`TR-002`/`AC-010`：走 `cli.main(["backfill", ...])` 生产入口，事件必须真落盘。

    注入的只有「库连接」与「交易所客户端」两个外部边界；批次切分、限速器、事件 sink 全部走
    CLI 自己的接线（**不注入 lambda sink**，`cli._backfill` 里就是 `backfill_sink()`）。
    事件目录**只**通过 `ALPHAMILL_EVENTS_DIR` 改道到 `tmp_path`——接线代码不许为测试而改，
    这条用例才证明得了生产路径真的会写事件（也保证测试不落进仓库默认根）。

    变异对照：把 `cli._backfill` 的 `event_sink=backfill_sink()` 去掉，本用例必红。
    """
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "events"))
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    conn = psycopg2.connect(**f002_db)
    monkeypatch.setattr(cli, "db_connect", lambda: conn)
    monkeypatch.setattr(backfill_orchestrator, "build_exchange", lambda exchange_id: FakeExchange())
    code = cli.main(
        [
            "backfill",
            "--universe",
            universe_id,
            "--lake-root",
            str(tmp_path),
            "--reports-dir",
            str(tmp_path / "reports"),
            "--start",
            "2026-09-01T00:00:00Z",
            "--end",
            "2026-09-01T02:30:00Z",
            "--min-interval",
            "0",  # 生产 default 0.5s 会让用例真实等待；其余接线一字不改
        ]
    )
    assert code == 0, capsys.readouterr().err
    run_id = json.loads(capsys.readouterr().out)["run_id"]
    [progress] = events.read_events(events.EVENT_BACKFILL_PROGRESS, run_id=run_id)
    assert progress.lake_pair == "BTC-USDT"
    assert progress.rows == 150
    assert progress.cursor == "2026-09-01T02:30:00Z"
    assert progress.elapsed >= 0.0
    assert (tmp_path / "events" / f"{events.EVENT_BACKFILL_PROGRESS}{events.SUFFIX}").is_file()


def test_failed_pair_event_carries_real_retry_count(f008_conn, tmp_path, monkeypatch) -> None:
    """TR-002：`backfill.failed.retries` 是**真实尝试次数 − 首次**，不是 `None` 或假 0。

    交易所持续返回可重试错误（429）：`RateLimiter` 重试 `max_retries=3` 次后抛
    `RateLimitExhaustedError`，事件里的 `retries=2` 必须与这个真实次数一致。
    事件目录由 `ALPHAMILL_EVENTS_DIR` 改道到 `tmp_path`，不落仓库默认根。
    """
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "events"))
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))

    class RateLimited(FakeExchange):
        def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=100):
            raise RuntimeError("429 Too Many Requests: rate limit exceeded")

    limiter = RateLimiter(
        RateLimitPolicy(min_interval_seconds=0.0, max_retries=3),
        clock=lambda: 0.0,
        sleep=lambda _seconds: None,
    )
    run = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=runner.plan_batch(load_definition(universe_id, tmp_path)),
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=RateLimited(),
        limiter=limiter,
        event_sink=backfill_sink(),
    )
    assert run.failed_pairs() == ("BTC/USDT",)
    [failed] = events.read_events(events.EVENT_BACKFILL_FAILED, run_id=run.run_id)
    assert failed.lake_pair == "BTC-USDT"
    assert failed.error_class == "RateLimitExhaustedError"
    assert failed.retries == 2  # max_retries=3 次真实尝试 − 首次
    assert failed.last_cursor is not None  # 失败保留断点，可单独重跑


def test_admission_emits_member_changed_on_tradability_and_admission_lines(
    f008_conn, tmp_path, monkeypatch
) -> None:
    """TR-001/AC-010：准入生产路径在台账线与判定线各留痕，两条线可按 `line` 区分。

    事件目录由 `ALPHAMILL_EVENTS_DIR` 改道到 `tmp_path`（`f008_conn` fixture 也设了这一条），
    不落仓库默认根 `reports/universe/events/`。
    """
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "events"))
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    active = PairGateResult(
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT",
        exchange="binance",
        market_type="spot",
        verdict=VERDICT_ACTIVE,
        reason_code=None,
        metrics={"synthetic": True},
    )
    outcome = admit_pair(
        f008_conn,
        definition=definition,
        result=active,
        lake_root=tmp_path,
        hostname="qiaozhi-gp",
        listed_at=WINDOW_START,
        start=WINDOW_START,
    )
    assert outcome.steps == (STEP_LEDGER, STEP_ARTIFACT, STEP_ADMISSION)

    tradability = events.read_events(events.EVENT_MEMBER_CHANGED, line="tradability")
    admission = events.read_events(events.EVENT_MEMBER_CHANGED, line="admission")
    # 台账线：每条实际落库的湖内命名空间一行（spot + perp），原因取台账原因码
    assert sorted(item.lake_pair for item in tradability) == ["BTC-USDT", "BTC-USDT-PERP"]
    assert {item.direction for item in tradability} == {"in"}
    assert {item.reason for item in tradability} == {"listed"}
    assert {item.universe_id for item in tradability} == {universe_id}
    # 判定线：按贸易符号一行，ACTIVE 是准入原因
    assert [item.lake_pair for item in admission] == ["BTC-USDT"]
    assert (admission[0].direction, admission[0].reason) == ("in", VERDICT_ACTIVE)
    assert admission[0].universe_id == universe_id


@pytest.mark.parametrize(
    ("verdict", "reason_code"),
    [(VERDICT_QUARANTINED, "missing_ratio_exceeded"), (VERDICT_INCOMPLETE, "backfill_incomplete")],
)
def test_non_active_verdict_emits_out_direction_admission_event(
    f008_conn, tmp_path, monkeypatch, verdict: str, reason_code: str
) -> None:
    """QUARANTINED / INCOMPLETE 不是「没有事件」：判定线记 `out` + 质量门原因码。

    事件目录由 `ALPHAMILL_EVENTS_DIR` 改道到 `tmp_path`（不写仓库默认根）。
    """
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "events"))
    universe_id = _frozen_universe(tmp_path, pairs=("BTC",))
    definition = load_definition(universe_id, tmp_path)
    result = PairGateResult(
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT",
        exchange="binance",
        market_type="spot",
        verdict=verdict,
        reason_code=reason_code,
        metrics={},
    )
    outcome = admit_pair(
        f008_conn, definition=definition, result=result, lake_root=tmp_path, start=WINDOW_START
    )
    assert outcome.steps == (STEP_ADMISSION,)
    [event] = events.read_events(events.EVENT_MEMBER_CHANGED, line="admission")
    assert (event.direction, event.reason) == ("out", reason_code)
    assert event.universe_id == universe_id
    # 非 ACTIVE 不动台账，也就不该有台账线事件
    assert events.read_events(events.EVENT_MEMBER_CHANGED, line="tradability") == ()


def test_resume_rejects_mismatched_window_or_batch(f008_conn, tmp_path) -> None:
    """回归（检视 R2-B2）：换窗口/换批次续跑必须**拒绝启动**，不得静默空跑报「本批全部完成」。

    缺陷形态（删掉 `run_backfill_batch` 里的 `resume_mismatch` 调用）：已完成的 pair 不在
    `pending` → 新窗口一行不取 → `remaining` 为空直接 `finished()`，CLI 退出 0，分片脚本
    打印「本批全部完成」——把「参数打错」报成「跑完了」。变异后本用例必红。
    """
    universe_id = _frozen_universe(tmp_path, pairs=("BTC", "ETH"))
    definition = load_definition(universe_id, tmp_path)
    plans = runner.plan_batch(definition)
    first = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=FakeExchange(),
        limiter=_limiter(),
        max_runtime_seconds=0.0,
    )

    base = {
        "universe_id": universe_id,
        "conn": f008_conn,
        "lake_root": tmp_path,
        "reports_dir": tmp_path / "reports",
        "exchange": FakeExchange(),
        "limiter": _limiter(),
        "resume_run_id": first.run_id,
    }
    with pytest.raises(WindowError, match="续跑参数"):
        runner.run_backfill_batch(
            plans=plans, start=WINDOW_START, end=WINDOW_END + timedelta(days=1), **base
        )
    with pytest.raises(WindowError, match="续跑参数"):
        runner.run_backfill_batch(plans=plans[:1], start=WINDOW_START, end=WINDOW_END, **base)
    with pytest.raises(WindowError, match="续跑参数"):
        runner.run_backfill_batch(plans=(), start=WINDOW_START, end=WINDOW_END, **base)
