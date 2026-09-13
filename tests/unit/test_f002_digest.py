"""T016 / AC-012：规范编码与 row_digest 的正反两面测试。

核心断言：同一函数喂「纯 Python 值（psycopg2 路径）」与「PyArrow to_pylist
路径」得到相同摘要；任何越过高位数字的改写（含 ±x 抵消式改写、double 最低
有效位改写）摘要必变——这正是 sum/numeric 口径抓不住的。
"""

import calendar
import math
from datetime import UTC, datetime

import pyarrow as pa
import pytest

from alphamill.data_bridge import digest
from alphamill.data_bridge.registry import (
    DOUBLE,
    JSONB,
    TEXT,
    TIMESTAMPTZ,
    Column,
)

PROJECTION = (
    Column("time", TIMESTAMPTZ),
    Column("exchange", TEXT),
    Column("symbol", TEXT),
    Column("open", DOUBLE),
    Column("close", DOUBLE),
    Column("metadata", JSONB),
)

T0 = datetime(2026, 9, 11, 0, 0, tzinfo=UTC)


def _row(close: float, open_: float = 100.0, metadata: dict | None = None) -> list:
    return [T0, "binance", "BTC/USDT", open_, close, metadata or {"k": "v"}]


def test_two_input_routes_same_digest():
    rows = [_row(101.5), _row(102.5)]
    plain = digest.row_digest(rows, PROJECTION)
    table = pa.table(
        {
            "time": pa.array([r[0] for r in rows], pa.timestamp("us", tz="UTC")),
            "exchange": pa.array([r[1] for r in rows], pa.string()),
            "symbol": pa.array([r[2] for r in rows], pa.string()),
            "open": pa.array([r[3] for r in rows], pa.float64()),
            "close": pa.array([r[4] for r in rows], pa.float64()),
            "metadata": pa.array([digest.canonical_json_text(r[5]) for r in rows], pa.string()),
        }
    )
    via_arrow = digest.row_digest(digest.iter_row_values(table), PROJECTION)
    assert plain == via_arrow
    assert plain.startswith("sha256:")


def test_order_independent_and_duplicate_stable():
    rows = [_row(101.5), _row(102.5)]
    assert digest.row_digest(rows, PROJECTION) == digest.row_digest(rows[::-1], PROJECTION)
    dup = rows + [rows[0]]
    assert digest.row_digest(dup, PROJECTION) == digest.row_digest(
        [rows[0], rows[0], rows[1]], PROJECTION
    )


def test_lowest_mantissa_bit_rewrite_changes_digest():
    # Decimal(10位) 定标口径对 <1e-10 的改写不可见；位模式编码必须可见
    original = digest.row_digest([_row(101.5)], PROJECTION)
    nudged = digest.row_digest([_row(math.nextafter(101.5, math.inf))], PROJECTION)
    assert original != nudged


def test_cancellation_rewrite_changes_digest():
    # 两行 +x/−x 抵消式改写：sum(round(col,10)) 不变，位模式摘要必变
    base = digest.row_digest(
        [
            [T0, "binance", "BTC/USDT", 100.0, -100.0, {}],
            [T0, "binance", "ETH/USDT", 200.0, -200.0, {}],
        ],
        PROJECTION,
    )
    rewritten = digest.row_digest(
        [
            [T0, "binance", "BTC/USDT", 100.5, -100.5, {}],
            [T0, "binance", "ETH/USDT", 200.5, -200.5, {}],
        ],
        PROJECTION,
    )
    assert base != rewritten


def test_negative_zero_and_nan_normalized():
    assert digest.encode_double(0.0) == digest.encode_double(-0.0)
    nan_a, nan_b = float("nan"), float("nan")
    assert digest.encode_double(nan_a) == digest.encode_double(nan_b)
    assert digest.encode_double(nan_a) == struct_packed_quiet_nan()
    assert digest.encode_double(0.0) != digest.encode_double(-1.0)


def struct_packed_quiet_nan() -> bytes:
    return digest.encode_double(float("nan"))


def test_text_and_jsonb_canonical_encoding():
    # jsonb 键序无关；与 text 同构造（长度前缀 + UTF-8），NULL 哨兵不碰撞
    a = digest.canonical_field({"b": 1, "a": 2}, JSONB)
    b = digest.canonical_field({"a": 2, "b": 1}, JSONB)
    assert a == b
    assert digest.canonical_field(None, JSONB) == b"\x00"
    assert digest.canonical_field(None, TEXT) == b"\x00"
    assert digest.canonical_field(None, DOUBLE) == b"\x00"
    assert digest.canonical_field(None, TIMESTAMPTZ) == b"\x00"
    non_null = digest.canonical_field("x", TEXT)
    assert non_null.startswith(b"\x01")
    assert non_null != digest.canonical_field(0.0, DOUBLE)  # 0x01+payload 互异


def test_naive_and_aware_timestamps_encode_equal():
    naive = datetime(2026, 9, 11, 12, 0)
    aware = naive.replace(tzinfo=UTC)
    assert digest.canonical_field(naive, TIMESTAMPTZ) == digest.canonical_field(aware, TIMESTAMPTZ)
    assert digest.utc_micros(aware) == calendar.timegm((2026, 9, 11, 12, 0, 0)) * 1_000_000


def test_row_length_mismatch_rejected():
    with pytest.raises(ValueError, match="列数"):
        digest.canonical_row_bytes([T0, "binance"], PROJECTION)


def test_null_sentinel_never_collides_with_value_bytes():
    for logical_type in (TIMESTAMPTZ, TEXT, DOUBLE, JSONB):
        assert digest.canonical_field(None, logical_type) != b""
        assert digest.canonical_field(None, logical_type)[0] == 0
