"""F011 导出 CLI 契约：启动期绑定、原因码、单次解析、部署单元一致性（AC-003/004/008）。

`_refresh_symbol_map` 与 `export_dataset` 打桩并记账：拒绝路径上二者都不得被调用
（「湖内零写入」= 不发布 symbol_map、不发布任何新版本）。
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pytest

import alphamill.data_bridge.cli as cli_mod
import alphamill.data_bridge.exporter as exporter_mod
from alphamill.data_bridge import cli
from alphamill.data_bridge.universe import binding as binding_mod
from alphamill.data_bridge.universe.definition import freeze_path
from tests.f011_fixtures import define_universe

REPO = Path(__file__).resolve().parents[2]
WINDOW = ["--window-end", "2026-09-05T00:00:00Z"]


@pytest.fixture()
def harness(tmp_path, monkeypatch):
    lake = tmp_path / "lake"
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(lake))
    calls: dict = {"refresh": 0, "exports": [], "resolve": 0}

    def refresh() -> None:
        calls["refresh"] += 1

    def export(dataset, **kwargs):
        calls["exports"].append((dataset, kwargs))
        bound = kwargs.get("bound_universe")
        return {
            "dataset": dataset,
            "status": "valid",
            "no_op": False,
            "data_version": "v2026.09.05",
            "universe_id": getattr(bound, "universe_id", None),
            "dropped_by_universe": [],
        }

    real_resolve = binding_mod.resolve_binding

    def counting_resolve(*args, **kwargs):
        calls["resolve"] += 1
        return real_resolve(*args, **kwargs)

    monkeypatch.setattr(cli_mod, "_refresh_symbol_map", refresh)
    monkeypatch.setattr(exporter_mod, "export_dataset", export)
    monkeypatch.setattr(binding_mod, "resolve_binding", counting_resolve)
    return {"lake": lake, "calls": calls}


def _u1(lake):
    return define_universe(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at="2026-08-31"
    )


def _case_no_definition(lake) -> list[str]:
    return []


def _case_unknown_id(lake) -> list[str]:
    _u1(lake)
    return ["--universe-id", "sha256:" + "0" * 64]


def _case_draft(lake) -> list[str]:
    draft = define_universe(
        lake, selected=("BTC",), snapshot_at="2026-08-30T00:00:00Z", frozen_at=None
    )
    return ["--universe-id", draft.universe_id]


def _case_lookahead(lake) -> list[str]:
    later = define_universe(
        lake, selected=("BTC",), snapshot_at="2026-09-02T00:00:00Z", frozen_at="2026-09-06"
    )
    return ["--universe-id", later.universe_id]


def _case_ambiguous(lake) -> list[str]:
    _u1(lake)
    define_universe(
        lake,
        selected=("ETH",),
        snapshot_at="2026-08-30T00:00:00Z",
        frozen_at="2026-08-31",
        market_type="spot",
    )
    return []


def _case_corrupt(lake) -> list[str]:
    good = _u1(lake)
    freeze_path(good.universe_id, lake).write_text("{not json", encoding="utf-8")
    return []


@pytest.mark.parametrize(
    ("build", "code"),
    [
        (_case_no_definition, "E_UNIVERSE_NOT_FROZEN"),
        (_case_unknown_id, "E_UNIVERSE_NOT_FOUND"),
        (_case_draft, "E_UNIVERSE_NOT_FROZEN"),
        (_case_lookahead, "E_UNIVERSE_LOOKAHEAD"),
        (_case_ambiguous, "E_UNIVERSE_AMBIGUOUS"),
        (_case_corrupt, "E_UNIVERSE_ARTIFACT"),
    ],
)
def test_binding_failures_exit_2_with_reason_code_and_write_nothing(
    harness, capsys, build, code
) -> None:
    """AC-004：IR-003 六种情形——退出码 2、stderr 行首原因码、symbol_map 与新版本均未发布。"""
    extra = build(harness["lake"])

    rc = cli.main(["--universe-filter", *WINDOW, *extra])

    assert rc == 2
    assert f"FATAL: {code}: " in capsys.readouterr().err
    assert harness["calls"]["refresh"] == 0, "拒绝时不得刷新 symbol_map"
    assert harness["calls"]["exports"] == [], "拒绝时不得导出任何 dataset"
    assert not (harness["lake"] / "_manifests").exists()


def test_universe_id_without_filter_is_rejected_by_argument_parsing(harness, capsys) -> None:
    """AC-003 / IR-001：单给 `--universe-id` 是参数错误，不隐式开启过滤。"""
    with pytest.raises(SystemExit) as info:
        cli.main(["--universe-id", "sha256:" + "0" * 64])
    assert info.value.code == 2
    assert "--universe-id 只能与 --universe-filter 同时给出" in capsys.readouterr().err
    assert harness["calls"]["exports"] == []


def test_binding_is_resolved_once_and_shared_by_all_datasets(harness) -> None:
    """AC-008：一次运行只解析一次绑定；各 dataset 拿同一绑定、同一窗口终点。"""
    bound = _u1(harness["lake"])

    rc = cli.main(["--universe-filter", "--dataset", "ohlcv_1m", "--dataset", "signals_log"])

    assert rc == 0
    calls = harness["calls"]
    assert calls["resolve"] == 1
    assert calls["refresh"] == 1
    assert [name for name, _ in calls["exports"]] == ["ohlcv_1m", "signals_log"]
    kwargs = [k for _, k in calls["exports"]]
    assert {k["bound_universe"].universe_id for k in kwargs} == {bound.universe_id}
    assert all(k["universe_filter"] is True for k in kwargs)
    today = dt.datetime.now(dt.UTC).date().isoformat()
    assert {k["window_end"] for k in kwargs} == {today}, "窗口终点一次定值、全部 dataset 共用"


def test_explicit_universe_id_is_passed_through(harness) -> None:
    older = _u1(harness["lake"])
    define_universe(
        harness["lake"],
        selected=("BTC", "ETH"),
        snapshot_at="2026-09-02T00:00:00Z",
        frozen_at="2026-09-03",
    )

    rc = cli.main(["--universe-filter", *WINDOW, "--universe-id", older.universe_id])

    assert rc == 0
    bound = harness["calls"]["exports"][0][1]["bound_universe"]
    assert bound.universe_id == older.universe_id
    assert bound.resolution == "explicit"


def test_default_path_does_not_resolve_a_binding(harness) -> None:
    """NFR-002：不开过滤时不解析绑定、不改窗口参数。"""
    rc = cli.main(["--dataset", "ohlcv_1m"])

    assert rc == 0
    assert harness["calls"]["resolve"] == 0
    ((_, kwargs),) = harness["calls"]["exports"]
    assert kwargs["universe_filter"] is False
    assert kwargs["bound_universe"] is None
    assert kwargs["window_end"] is None


def test_both_production_export_units_switch_the_filter_together() -> None:
    """AC-008 / Q-002：日常增量与周日全量的 `--universe-filter` 必须同开同关。"""
    daily = (REPO / "deployment/alphamill-export.service").read_text(encoding="utf-8")
    weekly = (REPO / "deployment/alphamill-fullexport.service").read_text(encoding="utf-8")

    def exec_start(unit: str) -> str:
        return next(line for line in unit.splitlines() if line.startswith("ExecStart="))

    assert ("--universe-filter" in exec_start(daily)) == ("--universe-filter" in exec_start(weekly))


@pytest.mark.parametrize(
    "relative",
    [
        "src/alphamill/data_bridge/exporter.py",
        "src/alphamill/data_bridge/partitions.py",
        "src/alphamill/data_bridge/cli.py",
        "src/alphamill/data_bridge/universe/binding.py",
        "src/alphamill/data_bridge/universe/verdicts.py",
    ],
)
def test_touched_modules_stay_within_the_sop_line_limit(relative) -> None:
    """design §0：SOP 350 行硬上限（仓库无全局行数门禁，按本 feature 触及面锁定）。"""
    lines = (REPO / relative).read_text(encoding="utf-8").count("\n")
    assert lines <= 350, f"{relative}: {lines} 行"
