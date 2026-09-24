"""T018 与 `AC-012`：五个子命令的契约与九类启动期拒绝（各自可区分的原因）。

用假交易所与 tmp 湖跑真实命令路径：拒绝路径断言「非零退出 + 稳定错误码」，成功路径断言
落盘产物与输出摘要；不需要数据库的路径（discover/freeze/show）全部在单元层覆盖，
需要库的（backfill/gate 的拒绝前置）只断言启动期拒绝。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from alphamill.data_bridge.universe import batching as runner
from alphamill.data_bridge.universe import cli
from alphamill.data_bridge.universe.admission import AdmissionOutcome
from alphamill.data_bridge.universe.definition import (
    build_definition,
    load_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import WindowError
from tests.f008_fixtures import criteria_for, market, snapshot

WINDOW = ("2026-09-01T00:00:00Z", "2026-09-04T00:00:00Z")


class _FakeExchange:
    rateLimit = 1

    def __init__(self, *, boom: bool = False):
        self.boom = boom

    def load_markets(self):
        if self.boom:
            raise RuntimeError("connection refused")
        created = int(datetime(2025, 1, 1, tzinfo=UTC).timestamp() * 1000)
        return {
            "BTC/USDT:USDT": {
                "symbol": "BTC/USDT:USDT",
                "id": "BTCUSDT",
                "base": "BTC",
                "quote": "USDT",
                "swap": True,
                "linear": True,
                "contract": True,
                "active": True,
                "created": created,
                "info": {"onboardDate": created},
            }
        }

    def fapiPublicGetKlines(self, params):
        return [
            [1_700_000_000_000 + i * 86_400_000, 1, 1, 1, 1, 10, 0, 1_000.0, 0, 0, 0, 0]
            for i in range(90)
        ]


@pytest.fixture()
def lake(tmp_path, monkeypatch) -> Path:
    root = tmp_path / "lake"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(root))
    return root


def _definition(lake: Path, *, bases=("BTC", "ETH")) -> str:
    criteria = criteria_for(turnover_rank_top_n=10)
    definition = build_definition(
        criteria, evaluate(snapshot(*[market(base) for base in bases]), criteria)
    )
    write_definition(definition, lake)
    return definition.universe_id


# ---------- discover ----------


def test_discover_writes_definition_and_prints_summary(lake, monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "fetch_snapshot", lambda criteria, now=None: snapshot(market("BTC")))
    assert cli.main(["discover", "--lake-root", str(lake)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected"] == 1
    assert payload["top"] == ["BTC/USDT"]
    assert load_definition(payload["universe_id"], lake).selected_pairs() == ("BTC/USDT",)


def test_discover_rejects_missing_criteria_fields(tmp_path, lake, capsys) -> None:
    broken = tmp_path / "criteria.json"
    broken.write_text('{"schema_version":1}', encoding="utf-8")
    assert cli.main(["discover", "--criteria", str(broken), "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_CRITERIA" in capsys.readouterr().err


def test_discover_rejects_unreachable_exchange(lake, monkeypatch, capsys) -> None:
    def boom(criteria, now=None):
        from alphamill.data_bridge.universe.exchange_snapshot import fetch_snapshot as real

        return real(criteria, exchange=_FakeExchange(boom=True))

    monkeypatch.setattr(cli, "fetch_snapshot", boom)
    assert cli.main(["discover", "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_EXCHANGE_UNREACHABLE" in capsys.readouterr().err


# ---------- freeze ----------


def test_freeze_requires_confirm_then_succeeds(lake, capsys) -> None:
    universe_id = _definition(lake)
    assert cli.main(["freeze", "--def", universe_id, "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_CONFIRM_REQUIRED" in capsys.readouterr().err

    assert (
        cli.main(
            [
                "freeze",
                "--def",
                universe_id,
                "--confirm",
                "--frozen-by",
                "georg",
                "--lake-root",
                str(lake),
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["frozen_by"] == "georg"


def test_freeze_rejects_empty_candidate_list(lake, capsys) -> None:
    criteria = criteria_for()
    definition = build_definition(
        criteria, evaluate(snapshot(market("BTC", listed_days=10)), criteria)
    )
    write_definition(definition, lake)
    assert definition.selected == ()
    assert (
        cli.main(["freeze", "--def", definition.universe_id, "--confirm", "--lake-root", str(lake)])
        == 2
    )
    assert "E_UNIVERSE_EMPTY_CANDIDATES" in capsys.readouterr().err


def test_freeze_rejects_unknown_definition(lake, capsys) -> None:
    assert (
        cli.main(["freeze", "--def", "sha256:" + "0" * 64, "--confirm", "--lake-root", str(lake)])
        == 2
    )
    assert "E_UNIVERSE_NOT_FOUND" in capsys.readouterr().err


# ---------- backfill / gate 的启动期拒绝 ----------


def test_backfill_rejects_unfrozen_universe(lake, capsys) -> None:
    universe_id = _definition(lake)
    code = cli.main(
        [
            "backfill",
            "--universe",
            universe_id,
            "--start",
            WINDOW[0],
            "--end",
            WINDOW[1],
            "--lake-root",
            str(lake),
        ]
    )
    assert code == 2
    assert "E_UNIVERSE_NOT_FROZEN" in capsys.readouterr().err


def test_backfill_rejects_invalid_and_missing_window(lake, monkeypatch, capsys) -> None:
    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()

    monkeypatch.delenv("BACKFILL_WINDOW_START", raising=False)
    monkeypatch.delenv("BACKFILL_WINDOW_END", raising=False)
    assert cli.main(["backfill", "--universe", universe_id, "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_WINDOW" in capsys.readouterr().err

    code = cli.main(
        [
            "backfill",
            "--universe",
            universe_id,
            "--start",
            WINDOW[1],
            "--end",
            WINDOW[0],
            "--lake-root",
            str(lake),
        ]
    )
    assert code == 2
    assert "E_UNIVERSE_WINDOW" in capsys.readouterr().err


def test_backfill_rejects_malformed_window_timestamp(lake, monkeypatch, capsys) -> None:
    """语法非法的时间戳是启动期拒绝（`E_UNIVERSE_WINDOW` / 退出 2），不得以 `ValueError` 逃逸。

    逃逸的后果不是「报错难看」：`cli.main` 只捕 `(UniverseError, OSError)`，裸 `ValueError`
    变成 traceback + 退出 1，而退出 1 的语义是「可重试的瞬时故障」——分片脚本会无限重试一个
    永远不可能合法的参数（检视定位的 error-code-escape）。
    """
    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()
    monkeypatch.delenv("BACKFILL_WINDOW_START", raising=False)
    monkeypatch.delenv("BACKFILL_WINDOW_END", raising=False)

    base = ["backfill", "--universe", universe_id, "--lake-root", str(lake)]
    malformed = (
        [*base, "--start", "yesterday", "--end", WINDOW[1]],
        [*base, "--start", WINDOW[0], "--end", "2024-13-01T00:00:00Z"],
    )
    for argv in malformed:
        assert cli.main(argv) == 2
        assert "E_UNIVERSE_WINDOW" in capsys.readouterr().err


def test_backfill_fetch_limit_overrides_module_default(lake, monkeypatch, capsys) -> None:
    """`--fetch-limit` 覆盖单次请求根数（Binance 现货上限 1000，默认 100 会让请求数多 10 倍）。"""
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod
    from alphamill.data_bridge.universe import backfill_runner as runner

    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()

    original = backfill_mod.FETCH_LIMIT
    monkeypatch.setattr(cli, "db_connect", lambda: _FakeConn())
    monkeypatch.setattr(runner, "run_backfill_batch", lambda **kwargs: _FakeRun())
    seen: list[int] = []
    try:
        code = cli.main(
            [
                "backfill",
                "--universe",
                universe_id,
                "--batch",
                "1",
                "--start",
                WINDOW[0],
                "--end",
                WINDOW[1],
                "--fetch-limit",
                "1000",
                "--lake-root",
                str(lake),
            ]
        )
        seen.append(backfill_mod.FETCH_LIMIT)
    finally:
        backfill_mod.FETCH_LIMIT = original
    assert code == 0
    assert seen == [1000]


class _FakeRun:
    def document(self):
        return {"run_id": "test", "pairs": []}

    def failed_pairs(self):
        return ()


def test_backfill_rejects_insufficient_disk(lake, monkeypatch, capsys) -> None:
    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()
    monkeypatch.setattr(cli, "require_headroom", _raise_disk)
    code = cli.main(
        [
            "backfill",
            "--universe",
            universe_id,
            "--start",
            WINDOW[0],
            "--end",
            WINDOW[1],
            "--lake-root",
            str(lake),
        ]
    )
    assert code == 2
    assert "E_UNIVERSE_DISK" in capsys.readouterr().err


def _raise_disk(*_args, **_kwargs):
    from alphamill.data_bridge.universe.errors import InsufficientDiskError

    raise InsufficientDiskError("磁盘余量不足：测试注入")


def test_backfill_rejects_insufficient_disk_from_real_estimate(lake, monkeypatch, capsys) -> None:
    """磁盘闸门要由真实 `capacity` 估算驱动：只注入探测到的余量，不替掉判定本身。

    上一条用例把 `cli.require_headroom` 整条替成「抛异常」，于是 `capacity` 三个函数
    一个都没跑到（把 `require_headroom` 改成恒不抛也照样绿）。这里只猴补 `free_bytes`，
    `estimate_rows → required_bytes → require_headroom` 全走产品代码。
    """
    from alphamill.data_bridge.universe import backfill_runner as runner
    from alphamill.data_bridge.universe import capacity

    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()
    monkeypatch.setattr(capacity, "free_bytes", lambda path: 0)
    monkeypatch.setattr(cli, "db_connect", lambda: _FakeConn())

    def must_not_run(**_kwargs):
        raise AssertionError("磁盘余量不足时必须停在启动期，不得进入回填")

    monkeypatch.setattr(runner, "run_backfill_batch", must_not_run)
    code = cli.main(
        [
            "backfill",
            "--universe",
            universe_id,
            "--start",
            WINDOW[0],
            "--end",
            WINDOW[1],
            "--lake-root",
            str(lake),
        ]
    )
    assert code == 2
    assert "E_UNIVERSE_DISK" in capsys.readouterr().err


# ---------- show ----------


def test_apply_listing_starts_only_lists_pairs_listed_after_window_start(lake) -> None:
    """晚上线的 pair 必须把真实上市时间交给回填层，否则交易所空批次会被判 stalled。"""
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod
    from alphamill.data_bridge.universe import backfill_runner as runner
    from alphamill.data_bridge.universe.definition import load_definition

    criteria = criteria_for(turnover_rank_top_n=10)
    definition = build_definition(
        criteria,
        evaluate(
            snapshot(market("OLD", listed_days=700), market("NEW", listed_days=200)), criteria
        ),
    )
    write_definition(definition, lake)
    loaded = load_definition(definition.universe_id, lake)
    cli.apply_listing_starts(loaded, runner.plan_batch(loaded), datetime(2026, 1, 1, tzinfo=UTC))
    entries = dict(item.split("=") for item in backfill_mod.LISTING_STARTS.split(",") if item)
    assert set(entries) == {"NEW/USDT"}  # OLD 早于窗口起点 → 不需要覆盖
    assert entries["NEW/USDT"].startswith("2026-03")  # 2026-09-19 往前 200 天


def test_gate_refreshes_aggregates_before_checking(lake, monkeypatch, capsys) -> None:
    """门禁前必须刷新连续聚合（否则新回填数据会以视图滞后被判 aggregate_mismatch）。"""
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod

    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()

    calls: list[tuple] = []
    monkeypatch.setattr(
        backfill_mod, "refresh_aggregates", lambda conn, start, end: calls.append((start, end))
    )
    monkeypatch.setattr(cli, "db_connect", lambda: _FakeConn())
    # 返回一条真实 ACTIVE 判定：空判定集现在是**判红**路径（检视 R1-015），
    # 本用例要验的是「先刷聚合再判定」，故给一条能过门的结论。
    monkeypatch.setattr(
        cli,
        "gate_and_admit",
        lambda *a, **k: [
            AdmissionOutcome(
                db_symbol="BTC/USDT",
                lake_pair="BTC-USDT-PERP",
                verdict="ACTIVE",
                reason_code=None,
                steps=("admission",),
                artifact_digest=None,
                listed_at=None,
            )
        ],
    )
    code = cli.main(
        [
            "gate",
            "--universe",
            universe_id,
            "--start",
            WINDOW[0],
            "--end",
            WINDOW[1],
            "--lake-root",
            str(lake),
        ]
    )
    assert code == 0
    assert calls == [
        (
            datetime.fromisoformat(WINDOW[0].replace("Z", "+00:00")),
            datetime.fromisoformat(WINDOW[1].replace("Z", "+00:00")),
        )
    ]
    assert "refreshing continuous aggregates" in capsys.readouterr().err


class _FakeConn:
    def close(self):
        return None


def _outcome(db_symbol: str, verdict: str, reason_code: str | None):
    from alphamill.data_bridge.universe.admission import AdmissionOutcome

    return AdmissionOutcome(
        db_symbol=db_symbol,
        lake_pair=db_symbol.replace("/", "-"),
        verdict=verdict,
        reason_code=reason_code,
        steps=("admission_recorded",),
        artifact_digest=None,
        listed_at=None,
    )


def test_gate_rejects_non_active_verdicts_with_nonzero_exit(lake, monkeypatch, capsys) -> None:
    """gate 的退出码必须跟着判定走：非 ACTIVE → 2，且 stderr 给出 `E_UNIVERSE_GATE_<判定>`。

    既有 gate 用例把 `gate_and_admit` 替成返回 `[]`——`all([])` 为真，退出码恒 0，
    于是「非 ACTIVE 判非零退出」这条契约没有任何断言（强制 `EXIT_OK` 也照样绿）。
    这里返回真实的 `AdmissionOutcome`：ACTIVE 与 QUARANTINED 混排，再单跑 INCOMPLETE。
    """
    from alphamill.data_bridge.collector import historical_backfill as backfill_mod

    universe_id = _definition(lake)
    cli.main(["freeze", "--def", universe_id, "--confirm", "--lake-root", str(lake)])
    capsys.readouterr()
    monkeypatch.setattr(backfill_mod, "refresh_aggregates", lambda conn, start, end: None)
    monkeypatch.setattr(cli, "db_connect", lambda: _FakeConn())
    argv = [
        "gate",
        "--universe",
        universe_id,
        "--start",
        WINDOW[0],
        "--end",
        WINDOW[1],
        "--lake-root",
        str(lake),
    ]

    monkeypatch.setattr(
        cli,
        "gate_and_admit",
        lambda *a, **k: [
            _outcome("BTC/USDT", "ACTIVE", None),
            _outcome("ETH/USDT", "QUARANTINED", "aggregate_mismatch"),
        ],
    )
    assert cli.main(argv) == 2
    captured = capsys.readouterr()
    assert [item["verdict"] for item in json.loads(captured.out)] == ["ACTIVE", "QUARANTINED"]
    assert "E_UNIVERSE_GATE_QUARANTINED" in captured.err
    assert "ETH/USDT → aggregate_mismatch" in captured.err
    assert "E_UNIVERSE_GATE_ACTIVE" not in captured.err  # 通过者不得产生拒绝行

    monkeypatch.setattr(
        cli,
        "gate_and_admit",
        lambda *a, **k: [_outcome("ETH/USDT", "INCOMPLETE", "backfill_incomplete")],
    )
    assert cli.main(argv) == 2
    captured = capsys.readouterr()
    assert "E_UNIVERSE_GATE_INCOMPLETE" in captured.err
    assert "ETH/USDT → backfill_incomplete" in captured.err


def test_show_prints_definition_and_exclusions(lake, capsys) -> None:
    criteria = criteria_for(turnover_rank_top_n=1)
    definition = build_definition(
        criteria,
        evaluate(snapshot(market("BTC", turnover=10.0), market("USDC", turnover=20.0)), criteria),
    )
    write_definition(definition, lake)
    assert cli.main(["show", "--universe", definition.universe_id, "--lake-root", str(lake)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["selected"][0]["db_symbol"] == "BTC/USDT"
    assert payload["excluded"][0]["reason"] == "stablecoin_pair"
    assert payload["frozen"] is False


def test_show_rejects_unknown_definition(lake, capsys) -> None:
    assert cli.main(["show", "--universe", "sha256:" + "1" * 64, "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_NOT_FOUND" in capsys.readouterr().err


def test_show_at_requires_digest_and_reads_artifact(lake, capsys) -> None:
    from alphamill.data_bridge.universe import artifact as artifact_mod
    from alphamill.data_bridge.universe.membership import TradabilityInterval

    assert cli.main(["show", "--at", WINDOW[0], "--lake-root", str(lake)]) == 2
    assert "E_UNIVERSE_WINDOW" in capsys.readouterr().err

    digest, _ = artifact_mod.publish_artifact(
        [
            TradabilityInterval(
                lake_pair="BTC-USDT", valid_from=datetime(2026, 1, 1, tzinfo=UTC), valid_to=None
            )
        ],
        lake,
    )
    assert cli.main(["show", "--at", WINDOW[0], "--digest", digest, "--lake-root", str(lake)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["members"] == ["BTC-USDT"]


def test_show_at_rejects_unknown_digest(lake, capsys) -> None:
    """未知 digest 属「不存在」→ `E_UNIVERSE_NOT_FOUND`（检视 R1-004）。

    原先它与「内容非法」共用 `E_UNIVERSE_ARTIFACT`，脚本无法区分「还没发布」与「已损坏」；
    内容非法路径仍报 `E_UNIVERSE_ARTIFACT`（见 `tests/unit/test_f008_artifact.py` 的键集合用例）。
    """
    assert (
        cli.main(
            ["show", "--at", WINDOW[0], "--digest", "sha256:" + "2" * 64, "--lake-root", str(lake)]
        )
        == 2
    )
    assert "E_UNIVERSE_NOT_FOUND" in capsys.readouterr().err


def test_plan_batch_rejects_candidate_excluded_from_selection(lake) -> None:
    """`--pairs` 必须对**入选集**校验：候选里被排除者此前静默变空批次（检视 R1-015）。

    被排除者通过校验时，过滤后得到空序列；`gate` 会因 `all([])` 为真**退出 0 报成功**——
    即 fail-open（`backfill` 侧只被下游「空批次」闸门拦下，报错文案与真实原因无关）。
    这里直接锁 `plan_batch` 的拒绝行为，并要求错误里带上排除原因。
    """
    criteria = criteria_for(turnover_rank_top_n=2)
    definition = build_definition(
        criteria, evaluate(snapshot(*[market(base) for base in ("BTC", "ETH", "SOL")]), criteria)
    )
    excluded = [item.db_symbol for item in definition.candidates if item.excluded_reason]
    assert excluded, "fixture 必须真的产生一个被排除的候选"
    assert excluded[0] not in definition.selected_pairs()

    with pytest.raises(WindowError, match="入选集") as excinfo:
        runner.plan_batch(definition, pairs=[excluded[0]])
    assert "排除原因" in str(excinfo.value)
