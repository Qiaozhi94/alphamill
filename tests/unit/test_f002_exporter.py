"""F002 导出窗口边界测试。"""

import datetime as dt

import psycopg2
import pytest

from alphamill.data_bridge import export_policy, exporter, registry
from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge.errors import DataBridgeError


def _partition(pair: str) -> dict:
    return {
        "logical_partition_key": {"exchange": "binance", "pair": pair, "date": "2026-09-14"},
        "path": f"ohlcv_1m/exchange=binance/pair={pair}/date=2026-09-14.r1.parquet",
        "rows": 1,
        "time_min": "2026-09-14T00:00:00Z",
        "time_max": "2026-09-14T00:00:00Z",
        "row_digest": "sha256:" + pair.replace("-", "") * 64,
        "bytes": 1,
        "sha256": "0" * 64,
    }


def test_default_window_end_excludes_current_partial_day(monkeypatch):
    monkeypatch.setattr(exporter.reconcile, "table_span", lambda _conn, _spec: None)
    _, end = exporter._resolve_window(
        object(), registry.require_dataset("ohlcv_1m"), "incremental", None, []
    )
    assert end == dt.datetime.now(dt.UTC).date()


def test_full_merge_drops_source_partitions_that_disappeared():
    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT")]
    produced = [_partition("BTC-USDT")]
    merged = export_policy.merge_partitions("full", baseline, produced)
    assert [entry["logical_partition_key"]["pair"] for entry in merged] == ["BTC-USDT"]


def test_full_shrink_guard_rejects_empty_result_with_nonempty_baseline():
    with pytest.raises(DataBridgeError, match="空快照"):
        export_policy.guard_full_shrink([_partition("BTC-USDT")], [], dt.date(2026, 9, 15))


def test_full_shrink_guard_rejects_large_shrink_and_truncated_window():
    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT"), _partition("SOL-USDT")]
    with pytest.raises(DataBridgeError, match="大幅降至"):
        export_policy.guard_full_shrink(baseline, [_partition("BTC-USDT")], dt.date(2026, 9, 15))

    baseline = [_partition("BTC-USDT"), _partition("ETH-USDT")]
    current = [_partition("BTC-USDT")]
    with pytest.raises(DataBridgeError, match="截断"):
        export_policy.guard_full_shrink(baseline, current, dt.date(2026, 9, 14))


def test_quality_flag_count_change_is_not_a_noop():
    baseline = {
        "symbol_map_digest": "sha256:" + "a" * 64,
        "quality": {"flagged_partitions": ["binance/BTC-USDT/2026-09-14"], "unresolved_total": 1},
        "excluded_null_event_time": 0,
    }
    assert mf.metadata_changed(
        baseline,
        "sha256:" + "a" * 64,
        ["binance/BTC-USDT/2026-09-14"],
        2,
        0,
    )


def test_export_failure_is_not_masked_by_session_reset(monkeypatch, tmp_path):
    """F002-R3-04：导出失败时，finally 的会话恢复不得覆盖原始异常。"""

    class _BrokenConn:
        def rollback(self):
            raise psycopg2.OperationalError("server closed the connection unexpectedly")

        def set_session(self, **kwargs):  # pragma: no cover - rollback 先抛
            raise AssertionError("rollback 失败后不应继续 set_session")

    def boom(*_args, **_kwargs):
        raise RuntimeError("导出过程中的真正失败原因")

    monkeypatch.setattr(exporter, "_export_one", boom)
    with pytest.raises(RuntimeError, match="真正失败原因"):
        exporter.export_dataset("ohlcv_1m", conn=_BrokenConn(), lake_root=tmp_path)


def test_shrink_guard_can_be_confirmed_but_window_truncation_never_is():
    """F002-R3-02：--allow-shrink 是源库收缩的人工确认通道，窗口传错不在确认范围内。"""
    baseline = [_partition(pair) for pair in ("BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT")]
    survivor = [_partition("BTC-USDT")]
    end = dt.date(2026, 9, 15)

    # 未确认：空结果与腰斩（4 → 1）都拒绝
    with pytest.raises(DataBridgeError, match="空快照"):
        export_policy.guard_full_shrink(baseline, [], end)
    with pytest.raises(DataBridgeError, match="大幅降至"):
        export_policy.guard_full_shrink(baseline, survivor, end)

    # 已确认：同样的两种情形放行
    export_policy.guard_full_shrink(baseline, [], end, allow_shrink=True)
    export_policy.guard_full_shrink(baseline, survivor, end, allow_shrink=True)

    # 窗口截断（基线最新日期 >= window_end）即使确认也必须拒绝
    with pytest.raises(DataBridgeError, match="截断已有基线"):
        export_policy.guard_full_shrink(baseline, [_partition("BTC-USDT")], dt.date(2026, 9, 14))
    with pytest.raises(DataBridgeError, match="截断已有基线"):
        export_policy.guard_full_shrink(
            baseline, [_partition("BTC-USDT")], dt.date(2026, 9, 14), allow_shrink=True
        )


def test_usable_baseline_falls_back_when_newest_version_is_corrupt(monkeypatch, tmp_path, caplog):
    """回归（2026-09-24）：最新版本完整性损坏时，基线回退到更早的可用版本。

    实测现场：`ohlcv_1m` 的 `v2026.09.21` 引用了 12 个 `date=2026-09-18/19` 分区文件而
    磁盘上没有 → 全量导出在 `_baseline()` 处 `ManifestIntegrityError` 中断，缺失分区
    永远没有机会被重新写出来。回退后导出可继续（并把坏版本引用的分区重建）。
    """
    from alphamill.data_bridge.errors import ManifestIntegrityError

    good = {"status": "valid", "dataset": "ohlcv_1m", "partitions": []}
    bad = {"status": "valid", "dataset": "ohlcv_1m", "partitions": [_partition("BTC-USDT")]}

    monkeypatch.setattr(mf, "list_versions", lambda _root, _dataset: ["v2026.09.13", "v2026.09.21"])
    monkeypatch.setattr(
        mf,
        "load_manifest",
        lambda _root, _dataset, version: bad if version.endswith(".21") else good,
    )
    monkeypatch.setattr(mf, "verify_value_digest", lambda _spec, _manifest: None)

    def _validate(_root, manifest, partitions=None):
        if manifest is bad:
            raise ManifestIntegrityError("清单内文件缺失: ohlcv_1m/.../date=2026-09-18.r1.parquet")

    monkeypatch.setattr(mf, "validate_manifest_integrity", _validate)

    with caplog.at_level("WARNING"):
        version, manifest = mf.usable_baseline(tmp_path, "ohlcv_1m")

    assert version == "v2026.09.13"
    assert manifest is good
    assert "完整性校验未通过" in caplog.text


def test_usable_baseline_is_none_when_no_usable_version(monkeypatch, tmp_path):
    """所有版本都不可用（缺失/非 valid/损坏）时返回 (None, None)——与"从未导出过"同义。"""
    from alphamill.data_bridge.errors import ManifestIntegrityError

    monkeypatch.setattr(mf, "list_versions", lambda _root, _dataset: ["v2026.09.21"])
    monkeypatch.setattr(
        mf,
        "load_manifest",
        lambda _root, _dataset, _version: {"status": "valid", "partitions": []},
    )
    monkeypatch.setattr(mf, "verify_value_digest", lambda _spec, _manifest: None)
    monkeypatch.setattr(
        mf,
        "validate_manifest_integrity",
        lambda *_a, **_k: (_ for _ in ()).throw(ManifestIntegrityError("清单内文件缺失")),
    )
    assert mf.usable_baseline(tmp_path, "ohlcv_1m") == (None, None)
