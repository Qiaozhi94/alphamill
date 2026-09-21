"""层 2 旅程验收轨（`[TEST]` 组 T030–T033）：四条用户旅程的端到端验收。

与单元/集成套件的分工：单元套件锁各模块的契约细节，这里走**旅程级**路径——CLI 与真实库
（docker `quant-timescaledb` 的 scratch 库）串起来，断言「用户能观察到的那条链」成立：
发现 → 冻结 → 回填 → 门禁 → 准入 → 导出口径，以及 PIT 查询与只追加约束。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

import psycopg2
import pytest
from conftest import D4, export_symbol_map_for, seed_f002_data

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe import cli
from alphamill.data_bridge.universe.admission import admit_pair
from alphamill.data_bridge.universe.definition import (
    build_definition,
    load_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import UniverseArtifactError
from alphamill.data_bridge.universe.membership import (
    MembershipRow,
    append_membership,
    load_membership,
    materialize_intervals,
    members_at,
)
from alphamill.data_bridge.universe.quality_gate import VERDICT_ACTIVE, PairGateResult
from tests.f008_fixtures import criteria_for, market, snapshot

pytestmark = pytest.mark.integration

WINDOW_START = datetime(2026, 9, 1, tzinfo=UTC)
WINDOW_END = datetime(2026, 9, 4, tzinfo=UTC)


class _FakeExchange:
    """固定响应 fixture：形状照 ccxt binanceusdm（load_markets + 隐式 klines）。"""

    rateLimit = 1

    def __init__(self, bases=("BTC", "USDC"), *, session: int = 1):
        self.bases = bases
        self.session = session

    def load_markets(self):
        created = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)
        markets = {
            f"{base}/USDT:USDT": {
                "symbol": f"{base}/USDT:USDT",
                "id": f"{base}USDT",
                "base": base,
                "quote": "USDT",
                "swap": True,
                "linear": True,
                "contract": True,
                "active": True,
                "created": created,
                "info": {"onboardDate": created, "underlyingType": "COIN"},
            }
            for base in self.bases
        }
        # 数据侧（现货）：可回填的标的才进候选
        markets.update(
            {
                f"{base}/USDT": {
                    "symbol": f"{base}/USDT",
                    "id": f"{base}USDT",
                    "base": base,
                    "quote": "USDT",
                    "spot": True,
                    "active": True,
                }
                for base in self.bases
            }
        )
        return markets

    def fapiPublicGetKlines(self, params):
        # 第 2 次会话把成交额整体放大 10 倍：排名法下候选与 universe_id 必须不变
        volume = 1_000.0 * (self.session**0)
        return [
            [1_700_000_000_000 + i * 86_400_000, 1, 1, 1, 1, 10, 0, volume, 0, 0, 0, 0]
            for i in range(90)
        ]


@pytest.fixture()
def lake(tmp_path, monkeypatch) -> Path:
    root = tmp_path / "lake"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(root))
    monkeypatch.setenv("ALPHAMILL_EVENTS_DIR", str(tmp_path / "events"))
    return root


def _freeze(lake: Path, *, bases=("BTC", "ETH")) -> str:
    criteria = criteria_for(turnover_rank_top_n=10)
    definition = build_definition(
        criteria, evaluate(snapshot(*[market(base) for base in bases]), criteria)
    )
    write_definition(definition, lake)
    from alphamill.data_bridge.universe.definition import freeze_definition

    freeze_definition(definition.universe_id, frozen_by="journey", lake_root=lake)
    return definition.universe_id


# ---------------- US-001：产出可复核的目标宇宙 ----------------


def test_us001_definition_journey(lake, tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "fetch_snapshot", _snapshot_from_exchange)
    # 1) 同一口径 + 同一交易所快照（--now 固定快照时间）两次发现 → 同一候选与同一 id
    snapshot_at = "2026-09-19T00:00:00Z"
    assert cli.main(["discover", "--lake-root", str(lake), "--now", snapshot_at]) == 0
    first_payload = read_json(capsys)
    first = load_definition(first_payload["universe_id"], lake)
    assert cli.main(["discover", "--lake-root", str(lake), "--now", snapshot_at]) == 0
    second_payload = read_json(capsys)
    assert second_payload["universe_id"] == first.universe_id
    assert second_payload["top"] == [item.db_symbol for item in first.selected][:10]
    # 逐候选指标与排除原因入档
    shown = cli.main(["show", "--universe", first.universe_id, "--lake-root", str(lake)])
    assert shown == 0
    detail = read_json(capsys)
    assert detail["frozen"] is False
    assert {"db_symbol", "listed_days", "turnover_usdt", "rank"} <= set(detail["selected"][0])
    # 结构性重复标的被排除并记录原因（USDC/USDT 是稳定币对）
    assert [item["reason"] for item in detail["excluded"]] == ["stablecoin_pair"]

    # 2) 未冻结清单驱动回填被非零拒绝；freeze 缺 --confirm 被拒
    unfinished = cli.main(
        [
            "backfill",
            "--universe",
            first.universe_id,
            "--start",
            WINDOW_START.isoformat(),
            "--end",
            WINDOW_END.isoformat(),
            "--lake-root",
            str(lake),
        ]
    )
    assert unfinished == 2
    assert "E_UNIVERSE_NOT_FROZEN" in capsys.readouterr().err
    assert cli.main(["freeze", "--def", first.universe_id, "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_CONFIRM_REQUIRED" in capsys.readouterr().err
    assert (
        cli.main(["freeze", "--def", first.universe_id, "--confirm", "--lake-root", str(lake)]) == 0
    )
    capsys.readouterr()

    # 3) 成员增删产生新 universe_id，旧版本只读
    assert first.selected_pairs() == ("BTC/USDT",)  # 冻结的是「发现」的那一版
    extended = _freeze(lake, bases=("BTC", "ETH", "SOL"))
    assert extended != first.universe_id
    assert load_definition(first.universe_id, lake).selected_pairs() == ("BTC/USDT",)
    assert load_definition(extended, lake).selected_pairs() == (
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
    )


def _snapshot_from_exchange(criteria, *, exchange=None, now=None):
    from alphamill.data_bridge.universe.exchange_snapshot import fetch_snapshot

    return fetch_snapshot(criteria, exchange=exchange or _FakeExchange(), now=now)


def read_json(capsys) -> dict:
    import json

    return json.loads(capsys.readouterr().out)


# ---------------- US-002：分批回填不被交易所打断 ----------------


def test_us002_backfill_journey(f008_conn, lake, tmp_path) -> None:
    from alphamill.data_bridge.universe import backfill_runner as runner
    from alphamill.data_bridge.universe.rate_limit import RateLimiter, RateLimitPolicy

    universe_id = _freeze(lake, bases=("BTC", "ETH"))
    definition = load_definition(universe_id, lake)
    plans = runner.plan_batch(definition)
    limiter = RateLimiter(
        RateLimitPolicy(min_interval_seconds=0.0, max_retries=1),
        clock=lambda: 0.0,
        sleep=lambda _seconds: None,
    )

    class _Interrupted(_FakeExchange):
        def __init__(self):
            super().__init__(bases=("BTC", "ETH"))
            self.calls = 0

        def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=100):
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("injected interruption")
            return _candles(since, limit)

    events: list[tuple[str, dict]] = []
    first = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=lake,
        reports_dir=tmp_path / "reports",
        exchange=_Interrupted(),
        limiter=limiter,
        hostname="qiaozhi-lt",
        event_sink=lambda kind, payload: events.append((kind, payload)),
    )
    assert first.failed_pairs() == ("BTC/USDT",)
    assert _rows(f008_conn, "ETH/USDT") > 0  # 另一个 pair 不受影响
    assert any(kind == "backfill.failed" for kind, _ in events)
    assert all(payload["hostname"] == "qiaozhi-lt" for _, payload in events)

    # 断点续跑：重跑同一 run，跳过已完成 pair，不产生重复行
    class _Resumed(_FakeExchange):
        def fetch_ohlcv(self, symbol, timeframe="1m", since=None, limit=100):
            return _candles(since, limit)

    resumed = runner.run_backfill_batch(
        universe_id=universe_id,
        plans=plans,
        start=WINDOW_START,
        end=WINDOW_END,
        conn=f008_conn,
        lake_root=lake,
        reports_dir=tmp_path / "reports",
        exchange=_Resumed(),
        limiter=limiter,
        hostname="qiaozhi-lt",
        resume_run_id=first.run_id,
    )
    expected = int((WINDOW_END - WINDOW_START).total_seconds() // 60)
    assert resumed.pending() == ()
    for symbol in ("BTC/USDT", "ETH/USDT"):
        total, distinct = _rows(f008_conn, symbol), _distinct_rows(f008_conn, symbol)
        assert total == distinct == expected, symbol
    record = runner.load_run(resumed.run_id, tmp_path / "reports")
    assert record.hostname == "qiaozhi-lt"
    assert {item["status"] for item in record.pairs} == {"completed"}


def _candles(since: int, limit: int) -> list[list[float]]:
    end_ms = int(WINDOW_END.timestamp() * 1000)
    rows: list[list[float]] = []
    moment = since
    while len(rows) < limit and moment < end_ms:
        rows.append([moment, 100.0, 101.0, 99.0, 100.5, 1.0])
        moment += 60_000
    return rows


def _rows(conn, symbol: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM ohlcv_1m WHERE symbol = %s", (symbol,))
        return int(cur.fetchone()[0])


def _distinct_rows(conn, symbol: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(DISTINCT time) FROM ohlcv_1m WHERE symbol = %s", (symbol,))
        return int(cur.fetchone()[0])


# ---------------- US-003：新 pair 必须过质量门才准入 ----------------


def test_us003_gate_and_admission_journey(f008_conn, f002_lake, tmp_path) -> None:
    seed_f002_data(f008_conn)
    export_symbol_map_for(f008_conn, f002_lake)
    universe_id = _freeze(f002_lake)

    quarantined = PairGateResult(
        db_symbol="ETH/USDT",
        lake_pair="ETH-USDT",
        exchange="binance",
        market_type="spot",
        verdict="QUARANTINED",
        reason_code="missing_ratio_exceeded",
        metrics={"missing_ratio": 0.5},
    )
    outcome = admit_pair(
        f008_conn,
        definition=load_definition(universe_id, f002_lake),
        result=quarantined,
        lake_root=f002_lake,
    )
    assert outcome.artifact_digest is None
    assert load_membership(f008_conn) == []  # 未过门不得写台账

    active = PairGateResult(
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT",
        exchange="binance",
        market_type="spot",
        verdict=VERDICT_ACTIVE,
        reason_code=None,
        metrics={"synthetic": True},
    )
    admitted = admit_pair(
        f008_conn,
        definition=load_definition(universe_id, f002_lake),
        result=active,
        lake_root=f002_lake,
        listed_at=WINDOW_START,
    )
    assert admitted.steps == ("ledger_appended", "artifact_published", "admission_recorded")
    ledger = artifact_mod.load_artifact(admitted.artifact_digest, f002_lake)
    assert ledger.universe_at(WINDOW_START + timedelta(days=1)) == frozenset(
        {"BTC-USDT", "BTC-USDT-PERP"}
    )

    summary = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end=f"{D4}T00:00:00Z",
        conn=f008_conn,
        lake_root=f002_lake,
        universe_filter=True,
    )
    manifest = mf.load_manifest(f002_lake, "ohlcv_1m", summary["data_version"])
    assert set(manifest["pairs"]) == {"BTC-USDT"}  # 只导出已准入 pair（ETH 被隔离）


# ---------------- US-004：任一历史时点可还原当时宇宙 ----------------


def test_us004_point_in_time_journey(f008_conn, lake) -> None:
    t1, t2 = WINDOW_START, WINDOW_START + timedelta(days=2)
    universe_id = _freeze(lake)
    append_membership(
        f008_conn,
        [
            MembershipRow(
                exchange="binance",
                market_type="spot",
                db_symbol="BTC/USDT",
                lake_pair="BTC-USDT",
                valid_from=t1,
                reason="listed",
                universe_id=universe_id,
            ),
            MembershipRow(
                exchange="binance",
                market_type="spot",
                db_symbol="BTC/USDT",
                lake_pair="BTC-USDT",
                valid_from=t2,
                reason="delisted",
                universe_id=universe_id,
            ),
        ],
    )
    # 退市 = 追加一行；区间由行派生，历史行未被改写
    intervals = materialize_intervals(load_membership(f008_conn))
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(t1, t2)]
    rows = load_membership(f008_conn)
    assert members_at(rows, t1 - timedelta(hours=1)) == frozenset()
    assert members_at(rows, t1 + timedelta(hours=1)) == frozenset({"BTC-USDT"})
    assert members_at(rows, t2 + timedelta(hours=1)) == frozenset()

    # 原地改写被数据库触发器拒绝（追加语义）
    with f008_conn.cursor() as cur, pytest.raises(psycopg2.Error, match="只追加"):
        cur.execute("UPDATE universe_membership SET reason = 'delisted'")
    f008_conn.rollback()

    # artifact 的 schema_version 不符 / 未知键即拒绝加载
    digest, path = artifact_mod.publish_artifact(intervals, lake)
    payload = path.read_text(encoding="utf-8").replace('"schema_version":1', '"schema_version":2')
    import json

    from alphamill.data_bridge.universe.canonical import sha256_prefixed

    tampered = json.dumps(json.loads(payload), sort_keys=True, separators=(",", ":")).encode()
    forged = sha256_prefixed(tampered)
    target = artifact_mod.artifact_path(forged, lake)
    target.write_bytes(tampered)
    with pytest.raises(UniverseArtifactError, match="schema_version"):
        artifact_mod.load_artifact(forged, lake)
    assert artifact_mod.load_artifact(digest, lake).universe_at(t1 + timedelta(hours=1))
