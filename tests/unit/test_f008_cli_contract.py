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

from alphamill.data_bridge.universe import cli
from alphamill.data_bridge.universe.definition import (
    build_definition,
    load_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
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


# ---------- show ----------


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
    assert (
        cli.main(
            ["show", "--at", WINDOW[0], "--digest", "sha256:" + "2" * 64, "--lake-root", str(lake)]
        )
        == 2
    )
    assert "E_UNIVERSE_ARTIFACT" in capsys.readouterr().err
