"""F008 回填入口必须刷新连续聚合（批次收尾 + 中断/异常也刷）。

背景：`run_backfill_batch` 直调 `backfill.run_backfill`，绕过了老入口
`collector/backfill_cli.py` 末尾的 `refresh_aggregates`；批 1 实跑后 ohlcv_5m 比 1m 基表
少 162 万个 5 分钟桶，`tests/integration/test_f001_row_reconciliation.py` 判红，只能人工
`CALL refresh_continuous_aggregate` 补。这里把"回填后必刷"钉成单元断言，不依赖数据库。
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest

from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe import cli_support

WINDOW_START = datetime(2024, 9, 10, tzinfo=UTC)
WINDOW_END = datetime(2024, 9, 11, tzinfo=UTC)


@dataclass(frozen=True)
class _Criteria:
    exchange: str = "binance"


@dataclass(frozen=True)
class _Definition:
    criteria: _Criteria = _Criteria()
    universe_id: str = "sha256:deadbeef"


def _plan() -> runner.PairPlan:
    return runner.PairPlan(db_symbol="BTC/USDT", lake_pair="BTC-USDT", rank=1, listed_at=None)


def _patch(monkeypatch: pytest.MonkeyPatch, calls: list[tuple], *, boom: bool = False) -> None:
    monkeypatch.setattr(runner, "require_frozen", lambda *_a, **_k: _Definition())
    monkeypatch.setattr(runner.backfill, "ensure_progress_table", lambda _conn: None)
    monkeypatch.setattr(
        runner, "split_already_complete", lambda _conn, _ex, plans, _s, _e: ([], list(plans))
    )
    # 真实刷新走 cli_support.refresh_aggregates；这里只替换它，保留 runner 侧的
    # contextmanager 接线，使"是否在 finally 里刷"仍被断言覆盖
    monkeypatch.setattr(
        cli_support, "refresh_aggregates", lambda conn, s, e: calls.append((conn, s, e))
    )

    def _run_backfill(**_kwargs):
        if boom:
            raise RuntimeError("网络出口抖动")

    monkeypatch.setattr(runner.backfill, "run_backfill", _run_backfill)


def test_batch_end_refreshes_aggregates(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[tuple] = []
    _patch(monkeypatch, calls)
    conn = object()

    runner.run_backfill_batch(
        universe_id="sha256:deadbeef",
        plans=[_plan()],
        start=WINDOW_START,
        end=WINDOW_END,
        conn=conn,
        lake_root=tmp_path,
        reports_dir=tmp_path / "reports",
        exchange=object(),
        hostname="qiaozhi-lt",
    )

    assert calls == [(conn, WINDOW_START, WINDOW_END)], "批次收尾必须刷新一次连续聚合"


def test_interrupted_batch_still_refreshes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """中断/异常退出也要刷：否则已补的区间在视图里留静默缺口（alphamill-eb 观测）。"""
    calls: list[tuple] = []
    _patch(monkeypatch, calls, boom=True)
    conn = object()

    with pytest.raises(RuntimeError):
        runner.run_backfill_batch(
            universe_id="sha256:deadbeef",
            plans=[_plan()],
            start=WINDOW_START,
            end=WINDOW_END,
            conn=conn,
            lake_root=tmp_path,
            reports_dir=tmp_path / "reports",
            exchange=object(),
            hostname="qiaozhi-lt",
        )

    assert calls == [(conn, WINDOW_START, WINDOW_END)], "异常退出也必须刷已补区间"


def test_refresh_failure_does_not_mask_batch_result(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """刷新本身失败不得吞掉批次结果——报告已落盘，聚合缺口可事后补刷，但必须留告警。"""

    def _boom(*_a, **_k):
        raise RuntimeError("锁超时")

    monkeypatch.setattr(cli_support, "refresh_aggregates", _boom)

    with (
        caplog.at_level("WARNING"),
        cli_support.refresh_aggregates_after(object(), WINDOW_START, WINDOW_END),
    ):
        pass

    assert "需人工补刷" in caplog.text
