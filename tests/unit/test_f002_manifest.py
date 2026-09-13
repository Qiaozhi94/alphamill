"""T002 / AC-011·AC-015（单测部分）：manifest 契约读写、版本排序、完整性、
增量合成与 value_digest 的正反两面测试。"""

import json
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import paths
from alphamill.data_bridge.errors import (
    ManifestIntegrityError,
    VersionNotFoundError,
)
from alphamill.data_bridge.registry import DOUBLE, Column, require_dataset

SPEC = require_dataset("ohlcv_1m")


def _partition(pair: str, day: str, rows: int, digest_hex: str, **overrides) -> dict:
    entry = {
        "logical_partition_key": {"exchange": "binance", "pair": pair, "date": day},
        "path": f"ohlcv_1m/exchange=binance/pair={pair}/date={day}.r1.parquet",
        "rows": rows,
        "time_min": f"{day}T00:00:00Z",
        "time_max": f"{day}T23:59:00Z",
        "row_digest": f"sha256:{digest_hex}",
        "bytes": 100,
        "sha256": digest_hex,
    }
    entry.update(overrides)
    return entry


def _write_partition_file(root, partition: dict, content: bytes | None = None) -> None:
    path = root / partition["path"]
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = content if content is not None else b"x" * partition["bytes"]
    path.write_bytes(payload)
    import hashlib

    partition["sha256"] = hashlib.sha256(payload).hexdigest()


# ---------- data_version 语义 ----------

def test_version_parse_sort_and_next():
    assert mf.parse_data_version("v2026.09.12") == (date(2026, 9, 12), 1)
    assert mf.parse_data_version("v2026.09.12-r3") == (date(2026, 9, 12), 3)
    assert mf.format_data_version(date(2026, 9, 12)) == "v2026.09.12"
    assert mf.format_data_version(date(2026, 9, 12), 2) == "v2026.09.12-r2"
    assert mf.data_version_sort_key("v2026.09.12-r2") > mf.data_version_sort_key("v2026.09.12")
    with pytest.raises(VersionNotFoundError):
        mf.parse_data_version("2026.09.12")


def test_next_version_never_reuses_including_invalid(tmp_path):
    root = tmp_path
    for version in ("v2026.09.12", "v2026.09.12-r2"):
        mf.publish_manifest(root, {"dataset": "ohlcv_1m", "data_version": version,
                                   "status": "invalid" if version.endswith("r2") else "valid",
                                   "rows": 0, "value_digest": "", "partitions": []})
    day = date(2026, 9, 12)
    assert mf.next_data_version(root, "ohlcv_1m", day) == "v2026.09.12-r3"
    assert mf.next_data_version(root, "ohlcv_1m", date(2026, 9, 13)) == "v2026.09.13"


# ---------- load / publish / latest ----------

def _minimal_manifest(version: str, partitions: list | None = None, status: str = "valid") -> dict:
    return {
        "dataset": "ohlcv_1m", "source": mf.SOURCE_TAG,
        "data_version": version, "status": status, "rows": 2,
        "value_digest": "sha256:deadbeef", "partitions": json.loads(json.dumps(partitions or [])),
        "reconcile": {"rows": "ok", "time_bounds": "ok", "row_digest": "ok"},
    }


def test_load_missing_and_corrupt_manifest(tmp_path):
    with pytest.raises(VersionNotFoundError):
        mf.load_manifest(tmp_path, "ohlcv_1m", "v2026.09.12")
    path = paths.manifest_path(tmp_path, "ohlcv_1m", "v2026.09.12")
    path.parent.mkdir(parents=True)
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ManifestIntegrityError, match="损坏"):
        mf.load_manifest(tmp_path, "ohlcv_1m", "v2026.09.12")


def test_load_rejects_identity_mismatch_and_missing_fields(tmp_path):
    # 内容身份与所在路径不符：绕过 publish 手工错位写入
    wrong = _minimal_manifest("v2026.09.12")
    wrong["dataset"] = "signals_log"
    path = paths.manifest_path(tmp_path, "ohlcv_1m", "v2026.09.12")
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(wrong), encoding="utf-8")
    with pytest.raises(ManifestIntegrityError, match="身份不符"):
        mf.load_manifest(tmp_path, "ohlcv_1m", "v2026.09.12")

    incomplete = {"dataset": "ohlcv_1m", "data_version": "v2026.09.13"}
    mf.publish_manifest(tmp_path, incomplete)
    with pytest.raises(ManifestIntegrityError, match="必填字段"):
        mf.load_manifest(tmp_path, "ohlcv_1m", "v2026.09.13")


def test_latest_valid_skips_invalid_and_raises_when_none(tmp_path):
    mf.publish_manifest(tmp_path, _minimal_manifest("v2026.09.10", status="invalid"))
    mf.publish_manifest(tmp_path, _minimal_manifest("v2026.09.11"))
    assert mf.latest_valid_version(tmp_path, "ohlcv_1m") == "v2026.09.11"
    mf.publish_manifest(tmp_path, _minimal_manifest("v2026.09.12", status="invalid"))
    assert mf.latest_valid_version(tmp_path, "ohlcv_1m") == "v2026.09.11"
    with pytest.raises(VersionNotFoundError):
        mf.latest_valid_version(tmp_path, "signals_log")


# ---------- 完整性（AC-008 的单测面） ----------

def test_integrity_missing_file_and_byte_flip(tmp_path):
    partition = _partition("BTC-USDT", "2026-09-11", 2, "aa")
    _write_partition_file(tmp_path, partition)
    manifest = _minimal_manifest("v2026.09.12", [partition])
    mf.validate_manifest_integrity(tmp_path, manifest)

    (tmp_path / partition["path"]).unlink()
    with pytest.raises(ManifestIntegrityError, match="缺失"):
        mf.validate_manifest_integrity(tmp_path, manifest)

    _write_partition_file(tmp_path, partition, content=b"y" * partition["bytes"])
    # 字节数相同、内容不同 → sha256 不符（partition 内记录的仍是旧哈希）
    with pytest.raises(ManifestIntegrityError, match="sha256"):
        mf.validate_manifest_integrity(tmp_path, manifest)


def test_integrity_size_mismatch_but_not_unreferenced_files(tmp_path):
    partition = _partition("BTC-USDT", "2026-09-11", 2, "bb", bytes=10)
    _write_partition_file(tmp_path, partition)
    manifest = _minimal_manifest("v2026.09.12", [partition])

    other = tmp_path / partition["path"].replace("r1", "r2")
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_bytes(b"orphan-from-another-version")
    mf.validate_manifest_integrity(tmp_path, manifest)  # 未引用文件不判红

    (tmp_path / partition["path"]).write_bytes(b"short")
    with pytest.raises(ManifestIntegrityError, match="字节数"):
        mf.validate_manifest_integrity(tmp_path, manifest)


# ---------- value_digest（AC-015 单测面） ----------

def test_value_digest_stable_across_physical_metadata():
    base = [_partition("BTC-USDT", "2026-09-11", 2, "aa")]
    moved = [_partition("BTC-USDT", "2026-09-11", 2, "aa",
                        path="somewhere/else.r9.parquet", bytes=999, sha256="ff")]
    assert mf.compute_value_digest(SPEC, base) == mf.compute_value_digest(SPEC, moved)


def test_value_digest_changes_on_value_projection_or_coverage():
    base = [_partition("BTC-USDT", "2026-09-11", 2, "aa")]
    value_changed = [_partition("BTC-USDT", "2026-09-11", 2, "ab")]
    assert mf.compute_value_digest(SPEC, base) != mf.compute_value_digest(SPEC, value_changed)

    coverage = base + [_partition("ETH-USDT", "2026-09-11", 5, "cc")]
    assert mf.compute_value_digest(SPEC, base) != mf.compute_value_digest(SPEC, coverage)

    bounds = [_partition("BTC-USDT", "2026-09-11", 2, "aa", time_max="2026-09-11T23:58:00Z")]
    assert mf.compute_value_digest(SPEC, base) != mf.compute_value_digest(SPEC, bounds)

    tweaked_spec = replace(SPEC, projection=(Column("open", DOUBLE),))
    assert mf.compute_value_digest(SPEC, base) != mf.compute_value_digest(tweaked_spec, base)


def test_verify_value_digest_fail_closed(tmp_path):
    manifest = _minimal_manifest("v2026.09.12", [_partition("BTC-USDT", "2026-09-11", 2, "aa")])
    manifest.pop("value_digest")
    with pytest.raises(ManifestIntegrityError, match="缺失"):
        mf.verify_value_digest(SPEC, manifest)

    manifest["value_digest"] = "sha256:nope"
    with pytest.raises(ManifestIntegrityError, match="重算不符"):
        mf.verify_value_digest(SPEC, manifest)

    manifest["value_digest"] = mf.compute_value_digest(
        SPEC, manifest["partitions"])
    assert mf.verify_value_digest(SPEC, manifest) == manifest["value_digest"]


# ---------- 增量合成（AC-011 单测面） ----------

def test_synthesis_inherits_replaces_appends():
    baseline = [_partition("BTC-USDT", "2026-09-11", 2, "aa"),
                _partition("ETH-USDT", "2026-09-11", 3, "bb")]
    produced = [_partition("BTC-USDT", "2026-09-11", 4, "cc"),
                _partition("SOL-USDT", "2026-09-12", 5, "dd")]
    merged = mf.synthesize_partitions(baseline, produced)
    by_pair = {p["logical_partition_key"]["pair"]: p for p in merged}
    assert by_pair["BTC-USDT"]["row_digest"] == "sha256:cc"  # 整项替换
    assert by_pair["ETH-USDT"]["row_digest"] == "sha256:bb"  # 原样继承
    assert by_pair["SOL-USDT"]["row_digest"] == "sha256:dd"  # 追加
    assert sum(p["rows"] for p in merged) == 12  # 累计而非单日


def test_skipped_inheritance_and_replacement():
    baseline = [{"exchange": "binance", "pair": "DOGE-USDT", "date": "2026-09-10"}]
    produced_keys = [{"exchange": "binance", "pair": "BTC-USDT", "date": "2026-09-11"}]
    empty_keys = [{"exchange": "binance", "pair": "DOGE-USDT", "date": "2026-09-11"},
                  {"exchange": "binance", "pair": "ETH-USDT", "date": "2026-09-11"}]
    skipped = mf.synthesize_skipped(baseline, produced_keys, empty_keys)
    keys = [mf.canonical_key(s) for s in skipped]
    # 基线 DOGE-09-10 本轮未被触碰 → 原样继承；DOGE-09-11 判定为空 → 按本轮加入
    assert mf.canonical_key(baseline[0]) in keys
    assert any(s["pair"] == "DOGE-USDT" and s["date"] == "2026-09-11" for s in skipped)
    # 本轮产出分区的键不再留在 skipped 里
    assert not any(s["pair"] == "BTC-USDT" for s in skipped)
    # 覆盖过的空键若下一轮产出分区则被移除
    skipped3 = mf.synthesize_skipped(skipped, empty_keys[:1], [])
    assert not any(s["pair"] == "DOGE-USDT" and s["date"] == "2026-09-11" for s in skipped3)


def test_partition_diff_added_changed_removed():
    baseline = [_partition("BTC-USDT", "2026-09-11", 2, "aa"),
                _partition("ETH-USDT", "2026-09-11", 3, "bb")]
    current = [_partition("BTC-USDT", "2026-09-11", 2, "aa"),  # 未变
               _partition("ETH-USDT", "2026-09-11", 4, "bd"),   # 修订
               _partition("SOL-USDT", "2026-09-11", 1, "ee")]   # 新增
    diff = mf.partition_diff(baseline, current)
    reasons = {(d["pair"], d["reason"]) for d in diff}
    assert reasons == {("ETH-USDT", "changed"), ("SOL-USDT", "added")}

    shrunk = [_partition("BTC-USDT", "2026-09-11", 2, "aa")]
    diff_removed = mf.partition_diff(baseline, shrunk)
    assert {d["pair"] for d in diff_removed if d["reason"] == "removed"} == {"ETH-USDT"}


# ---------- 发布与导出 ----------

def test_publish_manifest_is_atomic_and_sorted_stable(tmp_path):
    manifest = _minimal_manifest("v2026.09.12")
    path = mf.publish_manifest(tmp_path, manifest)
    assert path.is_file()
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["data_version"] == "v2026.09.12"
    assert not list(path.parent.glob("*.tmp-*"))


def test_iso_utc_formatting():
    aware = datetime(2026, 9, 12, 2, 0, 3, tzinfo=timezone.utc)
    assert mf.iso_utc(aware) == "2026-09-12T02:00:03Z"
    assert mf.iso_utc(datetime(2026, 9, 12, 2, 0, 3)).endswith("Z")
