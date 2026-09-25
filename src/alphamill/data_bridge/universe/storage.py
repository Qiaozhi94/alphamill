"""内容寻址 artifact 的落盘原语：原子创建、写一次、同 digest 逐字节一致。

发布纪律（design §3/§7）与 `symbol_map.export_symbol_map` 一致，但实现独立：

- **原子创建**：先写同目录临时文件，再 `os.link` 到目标（同目录 rename 语义，
  允许文件系统不支持硬链接时退化为 `O_CREAT|O_EXCL`）；
- **写一次**：目标已存在时不覆盖；内容不同即报错（同 digest 必须逐字节一致）；
- **只按显式 digest 读**：没有 latest/current 副本，读取必须给全名。
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from alphamill.data_bridge.universe.errors import UniverseArtifactError

_LINK_FALLBACK_ERRNOS = {errno.EXDEV, errno.EPERM, errno.EOPNOTSUPP, errno.ENOTSUP}


def atomic_create(path: Path, payload: bytes) -> bool:
    """原子创建 `path`；已存在且内容一致返回 False，内容不同抛错。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file():
        if path.read_bytes() != payload:
            raise UniverseArtifactError(f"同 digest artifact 内容不一致: {path}")
        return False
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    try:
        tmp.write_bytes(payload)
        try:
            os.link(tmp, path)
        except FileExistsError:
            if path.read_bytes() != payload:
                raise UniverseArtifactError(f"同 digest artifact 内容不一致: {path}") from None
            return False
        except OSError as exc:
            if exc.errno not in _LINK_FALLBACK_ERRNOS:
                raise
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
        return True
    finally:
        tmp.unlink(missing_ok=True)


def read_bytes(path: Path, *, what: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise UniverseArtifactError(f"{what} 不存在或不可读: {path}: {exc}") from exc
