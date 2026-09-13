"""规范编码与 row_digest——对账口径的唯一权威实现（design §3，F002-D003/R2-04）。

源侧（psycopg2 游标产出的 Python 值序列）与湖侧（PyArrow `to_pylist()` 的
值序列）由**同一个函数** `canonical_row_bytes()` 编码——不让 PG 与 DuckDB 各算
一次（`hashtext` 无跨引擎等价物，`sum(numeric)` 不抗抵消）。SHA-256 与聚合
顺序无关且抗抵消；本模块不提供降级出口，性能不可接受走 spec 修订。

编码规则（逐列，顺序 = registry 投影列顺序，无损）：
- `timestamptz`：UTC 微秒 int64，8 字节大端；
- `double`：IEEE-754 binary64 原始位模式 8 字节大端（**不得 Decimal 定标**），
  `-0.0` 归一为 `+0.0`，NaN 归一为单一静默 NaN 位型；
- `text`：UTF-8 字节，前置 uint32 大端长度；
- `jsonb`：规范 JSON（键按 Unicode 码点排序、无空白）后按 `text` 编码；
- NULL：单字节哨兵 `0x00`；非 NULL 前置 `0x01`，哨兵不与任何值碰撞。

排序键 = 该行的规范编码字节串本身（字典序），不是逻辑主键——`signals_log`
无主键，而完全相同的两行编码相同且相邻，顺序唯一确定。
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from collections.abc import Iterable, Iterator, Sequence
from datetime import UTC, datetime, timedelta
from typing import Any

from alphamill.data_bridge.registry import DOUBLE, JSONB, TEXT, TIMESTAMPTZ, Column

DIGEST_PREFIX = "sha256:"

_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
_ONE_MICRO = timedelta(microseconds=1)
_NAN_BITS = 0x7FF8000000000000
_NULL = b"\x00"
_NOT_NULL = b"\x01"


def utc_micros(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return (value - _EPOCH) // _ONE_MICRO


def encode_double(value: float) -> bytes:
    if value == 0.0:
        value = abs(value)  # -0.0 → +0.0
    bits = _NAN_BITS if math.isnan(value) else struct.unpack(">Q", struct.pack(">d", value))[0]
    return struct.pack(">Q", bits)


def canonical_json_text(value: Any) -> str:
    """jsonb 规范化：键按 Unicode 码点排序、无空白、非 ASCII 原样。"""
    if isinstance(value, str):
        value = json.loads(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _encode_text(raw: str) -> bytes:
    payload = raw.encode("utf-8")
    return struct.pack(">I", len(payload)) + payload


def canonical_field(value: Any, logical_type: str) -> bytes:
    if value is None:
        return _NULL
    body: bytes
    if logical_type == TIMESTAMPTZ:
        body = struct.pack(">q", utc_micros(value))
    elif logical_type == DOUBLE:
        body = encode_double(float(value))
    elif logical_type == TEXT:
        body = _encode_text(value)
    elif logical_type == JSONB:
        body = _encode_text(canonical_json_text(value))
    else:
        raise ValueError(f"未知逻辑类型: {logical_type!r}")
    return _NOT_NULL + body


def canonical_row_bytes(values: Sequence[Any], projection: Sequence[Column]) -> bytes:
    if len(values) != len(projection):
        raise ValueError(f"行值列数 {len(values)} 与投影列数 {len(projection)} 不一致")
    return b"".join(
        canonical_field(value, col.logical_type)
        for value, col in zip(values, projection, strict=True)
    )


def iter_row_values(table: Any) -> Iterator[list[Any]]:
    """PyArrow Table → 逐行 Python 值（湖侧输入路径；与 psycopg2 同一编码函数）。"""
    columns = [table.column(i).to_pylist() for i in range(table.num_columns)]
    for row in zip(*columns, strict=True):
        yield list(row)


def row_digest(rows: Iterable[Sequence[Any]], projection: Sequence[Column]) -> str:
    """按规范编码字节串字典序排序后的流式 SHA-256，返回 `sha256:<hex>`。"""
    encoded = sorted(canonical_row_bytes(values, projection) for values in rows)
    hasher = hashlib.sha256()
    for chunk in encoded:
        hasher.update(chunk)
    return DIGEST_PREFIX + hasher.hexdigest()
