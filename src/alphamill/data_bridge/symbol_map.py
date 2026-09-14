"""symbol_map：湖内 pair ↔ Freqtrade pair 的映射与内容寻址发布（design §4）。

映射键冻结为 **(exchange, market_type, db_symbol)**（F002-D010）——库内
`DISTINCT symbol` 不足以无损推导（spot 与 perp 的 `BTC/USDT` 是不同标的）。
输出格式冻结：spot `BTC/USDT → BTC-USDT`（Freqtrade `BTC/USDT`）、perp
`BTC/USDT[:USDT] → BTC-USDT-PERP`（Freqtrade `BTC/USDT:USDT`）。任意两行推导
出相同 lake_pair 即为碰撞，导出直接失败（`SymbolCollisionError`）。

current 副本位于湖元数据目录，不改写源码树；它不是可复现身份：canonical CSV
（五列排序、UTF-8、LF、固定表头）原子发布到
`lake/_metadata/symbol_maps/<digest>.csv`，digest 为 canonical bytes 的
SHA-256；已有同 digest 文件必须逐字节一致。ResearchSnapshot 只引用显式 digest。
"""

from __future__ import annotations

import csv
import errno
import hashlib
import io
import os
import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from alphamill.data_bridge import paths
from alphamill.data_bridge.errors import (
    DataBridgeError,
    SymbolCollisionError,
    SymbolNotFoundError,
)

COLUMNS = ("exchange", "market_type", "db_symbol", "lake_pair", "freqtrade_pair")
MARKET_TYPES = ("spot", "perp")
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

# 只有 registry 显式允许的源表参与映射；signals_log 可混合 spot/perp，不能套用单一
# DatasetSpec.market_type，因此由 pair 分区源表提供全局 universe。
_DISTINCT_SQL = """
SELECT DISTINCT exchange, symbol FROM {table}
"""


def current_csv_path(lake_root: Path | None = None) -> Path:
    """current 副本路径；默认位于 `lake/_metadata/symbol_map.csv`。

    环境变量 ALPHAMILL_SYMBOL_MAP_CURRENT 仅供测试/多环境覆盖。
    """
    override = os.getenv("ALPHAMILL_SYMBOL_MAP_CURRENT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    root = Path(lake_root) if lake_root is not None else paths.lake_root()
    return root / "_metadata" / "symbol_map.csv"


@dataclass(frozen=True)
class SymbolMapRef:
    digest: str
    path: Path  # digest 命名的不可变 artifact，不是 current 副本


@dataclass(frozen=True)
class SymbolRow:
    exchange: str
    market_type: str
    db_symbol: str


def derive_pairs(db_symbol: str, market_type: str) -> tuple[str, str]:
    """db symbol → (lake_pair, freqtrade_pair)，格式按 design §4 冻结。"""
    if market_type not in MARKET_TYPES:
        raise DataBridgeError(f"未知 market_type: {market_type!r}（合法: {MARKET_TYPES}）")
    base_part, _, settle = db_symbol.partition(":")
    if "/" not in base_part:
        raise DataBridgeError(f"非法 db_symbol {db_symbol!r}：期望 BASE/QUOTE[·:SETTLE]")
    lake_pair = base_part.replace("/", "-")
    if market_type == "perp":
        lake_pair = f"{lake_pair}-PERP"
        freqtrade_pair = f"{base_part}:{settle or base_part.split('/', 1)[1]}"
    else:
        freqtrade_pair = base_part
    return lake_pair, freqtrade_pair


def build_symbol_map(rows: list[SymbolRow]) -> pd.DataFrame:
    """纯函数：映射行 → 五列 DataFrame；lake_pair 碰撞直接失败。"""
    records = []
    seen: dict[str, SymbolRow] = {}
    for row in rows:
        lake_pair, freqtrade_pair = derive_pairs(row.db_symbol, row.market_type)
        if lake_pair in seen:
            raise SymbolCollisionError(
                f"lake_pair 碰撞: {lake_pair!r} 由 "
                f"({seen[lake_pair].exchange}, {seen[lake_pair].market_type}, "
                f"{seen[lake_pair].db_symbol}) 与 "
                f"({row.exchange}, {row.market_type}, {row.db_symbol}) 同时推导"
            )
        seen[lake_pair] = row
        records.append(
            {
                "exchange": row.exchange,
                "market_type": row.market_type,
                "db_symbol": row.db_symbol,
                "lake_pair": lake_pair,
                "freqtrade_pair": freqtrade_pair,
            }
        )
    frame = pd.DataFrame.from_records(records, columns=list(COLUMNS))
    return frame.sort_values(list(COLUMNS), kind="stable").reset_index(drop=True)


def canonical_csv_bytes(frame: pd.DataFrame) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(COLUMNS)
    ordered = frame.sort_values(list(COLUMNS), kind="stable")
    for record in ordered.itertuples(index=False):
        writer.writerow([getattr(record, col) for col in COLUMNS])
    return buffer.getvalue().encode("utf-8")


def content_digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    tmp.write_bytes(payload)
    os.replace(tmp, path)


def _atomic_create(path: Path, payload: bytes) -> None:
    """原子创建不可变 artifact；不支持 hard-link 时退回 O_EXCL，绝不覆盖。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}-{id(payload)}")
    tmp.write_bytes(payload)
    try:
        try:
            os.link(tmp, path)
        except FileExistsError:
            raise
        except OSError as exc:
            # 某些跨文件系统/网络文件系统不支持 link；O_EXCL 保留 no-overwrite 语义。
            if exc.errno not in {
                errno.EXDEV,
                errno.EPERM,
                errno.EOPNOTSUPP,
                errno.ENOTSUP,
            }:
                raise
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as target:
                target.write(payload)
                target.flush()
                os.fsync(target.fileno())
    except FileExistsError:
        raise
    finally:
        tmp.unlink(missing_ok=True)


def _rows_from_conn(conn) -> list[SymbolRow]:
    """从各 dataset 源表取 DISTINCT (exchange, symbol)，market_type 按 registry。"""
    from alphamill.data_bridge import registry

    rows: dict[tuple[str, str, str], SymbolRow] = {}
    for spec in registry.DATASETS.values():
        if not spec.symbol_map_enabled:
            continue
        with conn.cursor() as cur:
            cur.execute(_DISTINCT_SQL.format(table=spec.source_table))
            for exchange, symbol in cur.fetchall():
                rows[(exchange, spec.market_type, symbol)] = SymbolRow(
                    exchange, spec.market_type, symbol
                )
    return sorted(rows.values(), key=lambda r: (r.exchange, r.market_type, r.db_symbol))


def export_symbol_map(conn=None, lake_root: Path | None = None) -> SymbolMapRef:
    """刷新 current 副本并按 digest 原子发布不可变 artifact。"""
    from alphamill.data_bridge.collector.db_writer import db_connect

    own_conn = conn is None
    conn = conn if conn is not None else db_connect()
    try:
        root = lake_root or paths.lake_root()
        frame = build_symbol_map(_rows_from_conn(conn))
        payload = canonical_csv_bytes(frame)
        digest = content_digest(payload)

        artifact = paths.symbol_maps_dir(root) / f"{digest}.csv"
        if artifact.is_file() and artifact.read_bytes() != payload:
            raise DataBridgeError(f"同 digest artifact 内容不一致: {artifact}")
        if not artifact.is_file():
            try:
                _atomic_create(artifact, payload)
            except FileExistsError:
                if artifact.read_bytes() != payload:
                    raise DataBridgeError(f"同 digest artifact 内容不一致: {artifact}") from None
        _atomic_write(current_csv_path(root), payload)
        return SymbolMapRef(digest=digest, path=artifact)
    finally:
        if own_conn:
            conn.close()


def load_symbol_map(digest: str | None = None, lake_root: Path | None = None) -> pd.DataFrame:
    """显式 digest → 不可变 artifact（可重放）；None → current 副本（仅供探索）。"""
    if digest is None:
        source = current_csv_path(lake_root)
    else:
        if not _DIGEST_RE.fullmatch(digest):
            raise DataBridgeError(f"非法 symbol_map digest: {digest!r}")
        source = paths.symbol_maps_dir(lake_root or paths.lake_root()) / f"{digest}.csv"
    if not source.is_file():
        raise DataBridgeError(f"symbol_map 不存在: {source}")
    payload = source.read_bytes()
    if digest is not None and content_digest(payload) != digest:
        raise DataBridgeError(f"symbol_map digest 校验失败: {source}")
    frame = pd.read_csv(io.BytesIO(payload), dtype=str, keep_default_na=False)
    missing = [col for col in COLUMNS if col not in frame.columns]
    if missing:
        raise DataBridgeError(f"symbol_map 缺少列 {missing}: {source}")
    if tuple(frame.columns) != COLUMNS:
        raise DataBridgeError(f"symbol_map 列顺序或列集合非法: {source}")
    if digest is not None and canonical_csv_bytes(frame) != payload:
        raise DataBridgeError(f"symbol_map 不是 canonical CSV: {source}")
    return frame.sort_values(list(COLUMNS), kind="stable").reset_index(drop=True)


def resolve(
    value: str,
    direction: str,
    exchange: str,
    market_type: str = "spot",
    lake_root: Path | None = None,
) -> str:
    """按方向查询映射；无 exchange 无法消歧，故为必填（F002-D010）。"""
    column_by_direction = {
        "to_lake": ("db_symbol", "lake_pair"),
        "to_freqtrade": ("db_symbol", "freqtrade_pair"),
        "to_db": ("lake_pair", "db_symbol"),
    }
    if direction not in column_by_direction:
        raise DataBridgeError(f"未知映射方向: {direction!r}")
    src_col, dst_col = column_by_direction[direction]
    frame = load_symbol_map(lake_root=lake_root)
    matched = frame[
        (frame["exchange"] == exchange)
        & (frame["market_type"] == market_type)
        & (frame[src_col] == value)
    ]
    if matched.empty:
        raise SymbolNotFoundError(
            f"symbol_map 无映射: {direction} {value!r} (exchange={exchange}, "
            f"market_type={market_type})"
        )
    if len(matched) > 1:
        raise DataBridgeError(f"symbol_map 映射不唯一: {direction} {value!r}")
    return str(matched.iloc[0][dst_col])


def to_db_symbols(
    pairs: list[str],
    market_type: str,
    lake_root: Path | None = None,
    digest: str | None = None,
) -> list[str]:
    """湖内 pair 集合 → 去重后的 db symbol 集合（reader 行级过滤用）。"""
    frame = load_symbol_map(digest=digest, lake_root=lake_root)
    matched = frame[(frame["market_type"] == market_type) & (frame["lake_pair"].isin(pairs))]
    missing = sorted(set(pairs) - set(matched["lake_pair"]))
    if missing:
        raise SymbolNotFoundError(f"symbol_map 无 {market_type} 映射的 lake_pair: {missing}")
    return sorted(set(matched["db_symbol"]))
