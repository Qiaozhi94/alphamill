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


def test_usable_baseline_refuses_fallback_in_incremental_mode(monkeypatch, tmp_path):
    """回归（2026-09-24 检视 R1-001，Critical）：增量模式**不得**整版回退基线。

    回退版当继承基线时 `start = 基线最大日期 + 1`，新 valid 清单会丢掉中间版本独有的分区
    （文件还在盘上却不再被引用），而 `guard_full_shrink` 只在全量模式生效——即静默的数据链
    损失。故增量遇到损坏的最新 valid 版本必须**拒绝启动**，并给出可执行的处置。
    """
    from alphamill.data_bridge.errors import ManifestIntegrityError

    bad = {"status": "valid", "dataset": "ohlcv_1m", "partitions": [_partition("BTC-USDT")]}
    monkeypatch.setattr(mf, "list_versions", lambda _root, _dataset: ["v2026.09.13", "v2026.09.21"])
    monkeypatch.setattr(mf, "load_manifest", lambda _root, _dataset, _version: bad)
    monkeypatch.setattr(mf, "verify_value_digest", lambda _spec, _manifest: None)

    def _validate(_root, manifest, partitions=None):
        raise ManifestIntegrityError("清单内文件缺失: ohlcv_1m/.../date=2026-09-18.r1.parquet")

    monkeypatch.setattr(mf, "validate_manifest_integrity", _validate)

    with pytest.raises(ManifestIntegrityError) as excinfo:
        mf.usable_baseline(tmp_path, "ohlcv_1m")

    assert "不允许回退基线" in str(excinfo.value)
    assert "v2026.09.21" in str(excinfo.value)


def test_usable_baseline_falls_back_when_newest_version_is_corrupt(monkeypatch, tmp_path, caplog):
    """全量模式（`allow_fallback=True`）：最新版本损坏 → 回退到更早的可用版本。

    实测现场：`ohlcv_1m` 的 `v2026.09.21` 引用了 12 个 `date=2026-09-18/19` 分区文件而
    磁盘上没有 → 导出在基线处 `ManifestIntegrityError` 中断，缺失分区永远没有机会被重新
    写出来。全量模式从库重算全窗口，回退只是换个 diff 参照，故允许回退。
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
        version, manifest = mf.usable_baseline(tmp_path, "ohlcv_1m", allow_fallback=True)

    assert version == "v2026.09.13"
    assert manifest is good
    assert "校验未通过" in caplog.text


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
    assert mf.usable_baseline(tmp_path, "ohlcv_1m", allow_fallback=True) == (None, None)


def test_export_wiring_passes_allow_fallback_only_for_full_mode(monkeypatch, tmp_path):
    """回归（检视第 2 轮 N2）：接线 `allow_fallback=(mode == "full")` 必须有锁。

    变异验证：把 `exporter._export_one` 的实参改成恒 `True`（或删掉实参回落到"总是回退"）
    后本用例必红——否则增量模式会恢复 R1-001（Critical）的「整版回退当继承基线 → 静默丢
    中间版本分区」。此前两条回归只调 `usable_baseline` 本体，锁不住这处传参。
    """
    from alphamill.data_bridge import exporter, registry

    recorded: list[dict] = []

    def _baseline(_root, _dataset, **kwargs):
        recorded.append(kwargs)
        return None, None

    class _Stop(Exception):
        pass

    monkeypatch.setattr(mf, "usable_baseline", _baseline)
    monkeypatch.setattr(exporter.reconcile, "begin_snapshot_tx", lambda _conn: (0, None))
    monkeypatch.setattr(exporter, "_resolve_window", lambda *a, **k: (_ for _ in ()).throw(_Stop()))
    spec = registry.require_dataset("ohlcv_1m")

    for mode, expected in (("incremental", False), ("full", True)):
        recorded.clear()
        with pytest.raises(_Stop):
            exporter._export_one(None, spec, mode, None, tmp_path, lambda _payload: None, 0.0)
        assert recorded == [{"allow_fallback": expected}], f"{mode} 的 allow_fallback 接线不对"
