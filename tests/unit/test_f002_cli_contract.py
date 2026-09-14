"""T009：导出 CLI 退出码契约（design §5：0 成功 / 1 可重试 / 2 数据裁决）。"""

import psycopg2
import pytest

from alphamill.data_bridge import cli
from alphamill.data_bridge.errors import (
    DataBridgeError,
    ManifestIntegrityError,
    SymbolCollisionError,
)


def _ok_summary():
    return {"dataset": "ohlcv_1m", "status": "valid", "no_op": False, "data_version": "v2026.09.13"}


def _patch_export(monkeypatch, func) -> None:
    import alphamill.data_bridge.cli as cli_mod
    import alphamill.data_bridge.exporter as exporter_mod

    # symbol map 刷新依赖真实库，属 CLI 流水线噪声，单测打桩
    monkeypatch.setattr(cli_mod, "_refresh_symbol_map", lambda: None)
    monkeypatch.setattr(exporter_mod, "export_dataset", func)


def test_exit_0_on_valid_and_noop(monkeypatch):
    summaries = iter(
        [
            _ok_summary(),
            {"dataset": "signals_log", "status": "no-op", "no_op": True, "data_version": None},
        ]
    )
    _patch_export(monkeypatch, lambda *a, **k: next(summaries))
    assert cli.main(["--dataset", "ohlcv_1m", "--dataset", "signals_log"]) == 0


def test_exit_2_on_unknown_dataset(monkeypatch):
    # registry 校验失败 → 2（无需触发导出）
    assert cli.main(["--dataset", "nope"]) == 2


def test_exit_2_on_invalid_reconcile(monkeypatch):
    summary = {
        "dataset": "ohlcv_1m",
        "status": "invalid",
        "no_op": False,
        "data_version": "v2026.09.13",
    }
    _patch_export(monkeypatch, lambda *a, **k: summary)
    assert cli.main([]) == 2


@pytest.mark.parametrize(
    "error",
    [
        psycopg2.OperationalError("connection refused"),
        psycopg2.InterfaceError("connection already closed"),
    ],
)
def test_exit_1_on_transient_db_errors(monkeypatch, error):
    def boom(*a, **k):
        raise error

    _patch_export(monkeypatch, boom)
    assert cli.main([]) == 1


def test_exit_1_on_transient_io_error(monkeypatch):
    def boom(*a, **k):
        raise OSError("disk full")

    _patch_export(monkeypatch, boom)
    assert cli.main([]) == 1


def test_exit_1_on_symbol_map_io_error(monkeypatch):
    import alphamill.data_bridge.cli as cli_mod

    def boom():
        raise OSError("disk full")

    monkeypatch.setattr(cli_mod, "_refresh_symbol_map", boom)
    assert cli.main([]) == 1


def test_exit_2_on_invalid_window_value(monkeypatch):
    def boom(*a, **k):
        raise ValueError("window-end 非法")

    _patch_export(monkeypatch, boom)
    assert cli.main([]) == 2


def test_exit_1_beats_0_but_2_beats_1(monkeypatch):
    import alphamill.data_bridge.cli as cli_mod
    import alphamill.data_bridge.exporter as exporter_mod

    monkeypatch.setattr(cli_mod, "_refresh_symbol_map", lambda: None)

    def runner(sequence):
        calls = iter(sequence)

        def fake(dataset, mode="incremental", window_end=None, **kwargs):
            action = next(calls)
            if isinstance(action, Exception):
                raise action
            return action

        return fake

    # 第一个 dataset 瞬时失败、第二个成功 → 1
    monkeypatch.setattr(
        exporter_mod, "export_dataset", runner([psycopg2.OperationalError("down"), _ok_summary()])
    )
    assert cli.main(["--dataset", "ohlcv_1m", "--dataset", "signals_log"]) == 1

    # 第一个瞬时失败、第二个数据裁决 → 2（不可重试裁决优先）
    monkeypatch.setattr(
        exporter_mod,
        "export_dataset",
        runner(
            [
                psycopg2.OperationalError("down"),
                {
                    "dataset": "signals_log",
                    "status": "invalid",
                    "no_op": False,
                    "data_version": "x",
                },
            ]
        ),
    )
    assert cli.main(["--dataset", "ohlcv_1m", "--dataset", "signals_log"]) == 2


@pytest.mark.parametrize(
    "error",
    [
        SymbolCollisionError("lake_pair 碰撞"),
        ManifestIntegrityError("sha256 不符"),
        DataBridgeError("symbol 无法映射"),
    ],
)
def test_exit_2_on_data_adjudication_errors(monkeypatch, error):
    def boom(*a, **k):
        raise error

    _patch_export(monkeypatch, boom)
    assert cli.main([]) == 2


def test_default_exports_all_datasets(monkeypatch):
    seen = {}

    def fake(dataset, mode="incremental", window_end=None, **kwargs):
        seen.setdefault("datasets", []).append(dataset)
        return {"dataset": dataset, "status": "valid", "no_op": False, "data_version": "v1"}

    _patch_export(monkeypatch, fake)
    assert cli.main([]) == 0
    assert sorted(seen["datasets"]) == sorted(
        [
            "ohlcv_1m",
            "derivatives_funding_rates",
            "derivatives_open_interest",
            "derivatives_mark_index_basis",
            "signals_log",
        ]
    )


def test_allow_shrink_flag_is_forwarded_to_exporter(monkeypatch):
    """F002-R3-02：CLI 的人工确认开关必须真的传到导出器，缺省为 False。"""
    seen: list[bool] = []

    def fake(dataset, mode="incremental", window_end=None, allow_shrink=False, **kwargs):
        seen.append(allow_shrink)
        return _ok_summary()

    _patch_export(monkeypatch, fake)
    assert cli.main(["--dataset", "ohlcv_1m"]) == 0
    assert cli.main(["--dataset", "ohlcv_1m", "--mode", "full", "--allow-shrink"]) == 0
    assert seen == [False, True]
