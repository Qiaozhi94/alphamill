"""experiment_store 路径与不可变 artifact 落盘原语（F007 design §3.2）。

`reports/` 根默认仓库根目录，可用 `ALPHAMILL_REPORTS_DIR` 覆盖（测试/多环境），与 F002
`ALPHAMILL_LAKE_DIR` 同一模式。产物路径一律用 POSIX 逻辑路径（`NFR-005`），物理路径只进
provenance，因此本模块返回的 `Path` 只用于**落盘**，不参与身份。
"""

from __future__ import annotations

import errno
import os
from pathlib import Path

from alphamill.data_bridge import paths
from alphamill.experiment_store.errors import SnapshotIntegrityError

SNAPSHOTS_SUBDIR = "research_snapshots"
CALENDAR_SUBDIR = "_inputs/universe_calendars"
MANIFEST_NAME = "manifest.json"


def reports_root() -> Path:
    """reports 根：默认仓库根 `reports/`，`ALPHAMILL_REPORTS_DIR` 可覆盖。"""
    override = os.getenv("ALPHAMILL_REPORTS_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (paths.REPO_ROOT / "reports").resolve()


def snapshot_dir(root: Path, snapshot_id: str) -> Path:
    return root / SNAPSHOTS_SUBDIR / snapshot_id


def calendar_artifact_path(root: Path, digest: str) -> Path:
    return root / SNAPSHOTS_SUBDIR / CALENDAR_SUBDIR / f"{digest}.json"


def atomic_create(path: Path, payload: bytes) -> None:
    """原子创建不可变 artifact（hard-link 优先，退回 O_EXCL），绝不覆盖已有文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}")
    tmp.write_bytes(payload)
    try:
        try:
            os.link(tmp, path)
        except FileExistsError as exc:
            raise SnapshotIntegrityError(f"artifact 已存在且不可覆盖: {path}") from exc
        except OSError as exc:
            if exc.errno not in {errno.EXDEV, errno.EPERM, errno.EOPNOTSUPP, errno.ENOTSUP}:
                raise
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
    finally:
        tmp.unlink(missing_ok=True)
