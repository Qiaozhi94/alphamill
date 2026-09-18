"""Process-level write confinement for generator runs.

This guard targets accidental and vendor writes, not a hostile native extension or a
kernel-level adversary. It confines write-capable filesystem operations to one run root;
it is not a replacement for operating-system isolation.
"""

from __future__ import annotations

import builtins
import io
import os
from collections.abc import Callable
from pathlib import Path
from types import ModuleType, TracebackType
from typing import IO, Final, NoReturn, TypeAlias

from alphamill.factor_factory.errors import BoundaryGuardError, WriteDeniedError

_GuardFunction: TypeAlias = Callable[..., IO[str] | IO[bytes] | int | None]
_WRITE_FLAGS: Final[int] = (
    os.O_WRONLY
    | os.O_RDWR
    | os.O_CREAT
    | os.O_TRUNC
    | os.O_APPEND
    | os.O_EXCL
    | getattr(os, "O_TMPFILE", 0)
)


def assert_write_allowed(path: str | os.PathLike[str], *, root: Path) -> Path:
    """Return the resolved path when it is contained by ``root``."""
    try:
        resolved_path = Path(path).resolve()
        resolved_path.relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError) as exc:
        raise WriteDeniedError(f"write path is outside the permitted root: {path!s}") from exc
    return resolved_path


def _path_text(path: str | bytes | os.PathLike[str]) -> str:
    return os.fsdecode(os.fspath(path))


def _write_mode(mode: str) -> bool:
    return any(flag in mode for flag in "wax+")


def _write_flags(flags: int) -> bool:
    return bool(flags & _WRITE_FLAGS)


def _deny_descriptor() -> NoReturn:
    raise WriteDeniedError("descriptor-relative writes are not permitted")


def _assert_path_allowed(path: str | bytes | os.PathLike[str] | int, root: Path) -> Path:
    if isinstance(path, int):
        _deny_descriptor()
    return assert_write_allowed(_path_text(path), root=root)


def _apply_write_patch(owner: ModuleType, name: str, replacement: _GuardFunction) -> None:
    setattr(owner, name, replacement)


class WritePathGuard:
    """Own process-wide write replacements for one resolved generation run root."""

    __slots__ = ("_root", "_originals", "_patches", "_closed")

    def __init__(self, root: Path, originals, patches) -> None:
        self._root = root
        self._originals = originals
        self._patches = patches
        self._closed = False

    @property
    def active(self) -> bool:
        """Return whether every write replacement is still installed."""
        return not self._closed and all(
            getattr(owner, name) is replacement for owner, name, replacement in self._patches
        )

    @property
    def root(self) -> Path:
        """Return the resolved run directory accepted as the write root."""
        return self._root

    def verify(self) -> None:
        """Raise when the process no longer has this guard's write replacements."""
        if not self.active:
            raise BoundaryGuardError("write path guard is not active")

    def close(self) -> None:
        """Restore the saved filesystem functions once; repeated calls do nothing."""
        if self._closed:
            return
        self._closed = True
        for owner, name, original in self._originals:
            setattr(owner, name, original)

    def __enter__(self) -> WritePathGuard:
        """Return this active guard for a context-managed run."""
        self.verify()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Restore filesystem functions when leaving the context."""
        self.close()


def _validate_run_dir(run_dir: Path, reports_root: Path) -> Path:
    if ".." in run_dir.parts:
        raise BoundaryGuardError("run_dir may not contain traversal components")
    lexical_root = reports_root.absolute() / "generation"
    lexical_run = run_dir.absolute()
    try:
        lexical_relative = lexical_run.relative_to(lexical_root)
    except ValueError as exc:
        raise BoundaryGuardError(
            "run_dir must resolve to reports_root/generation/<run_id>"
        ) from exc
    if len(lexical_relative.parts) != 1:
        raise BoundaryGuardError("run_dir must contain one safe path component")

    try:
        resolved_root = reports_root.resolve()
        resolved_run = run_dir.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as exc:
        raise BoundaryGuardError("run_dir must already exist and resolve cleanly") from exc
    if not resolved_run.is_dir():
        raise BoundaryGuardError("run_dir must be an existing directory")

    try:
        resolved_relative = resolved_run.relative_to(resolved_root / "generation")
    except ValueError as exc:
        raise BoundaryGuardError(
            "run_dir must resolve to reports_root/generation/<run_id>"
        ) from exc
    if len(resolved_relative.parts) != 1:
        raise BoundaryGuardError("run_dir must contain one safe path component")
    if resolved_run != resolved_root / "generation" / resolved_relative.name:
        raise BoundaryGuardError("run_dir must not resolve through a symlink")
    return resolved_run


def _guard_open(original: _GuardFunction, root: Path) -> _GuardFunction:
    def guarded(file, mode="r", *args, **kwargs):
        if _write_mode(mode):
            _assert_path_allowed(file, root)
        return original(file, mode, *args, **kwargs)

    return guarded


def _guard_os_open(original: _GuardFunction, root: Path) -> _GuardFunction:
    def guarded(path, flags, mode=0o777, *, dir_fd=None):
        if _write_flags(flags):
            if dir_fd is not None:
                _deny_descriptor()
            _assert_path_allowed(path, root)
        if dir_fd is None:
            return original(path, flags, mode)
        return original(path, flags, mode, dir_fd=dir_fd)

    return guarded


def _guard_path_operation(original: _GuardFunction, root: Path) -> _GuardFunction:
    def guarded(path, *args, **kwargs):
        if kwargs.get("dir_fd") is not None:
            _deny_descriptor()
        _assert_path_allowed(path, root)
        return original(path, *args, **kwargs)

    return guarded


def _guard_move(original: _GuardFunction, root: Path) -> _GuardFunction:
    def guarded(source, destination, *args, **kwargs):
        if kwargs.get("src_dir_fd") is not None or kwargs.get("dst_dir_fd") is not None:
            _deny_descriptor()
        _assert_path_allowed(source, root)
        _assert_path_allowed(destination, root)
        return original(source, destination, *args, **kwargs)

    return guarded


def _deny_link(*_args, **_kwargs) -> NoReturn:
    raise WriteDeniedError("creating links is not permitted")


def _self_test(root: Path, original_unlink: _GuardFunction) -> None:
    token = f".alphamill-write-guard-{id(root)}"
    inside = root / token
    outside = root.parent / token
    try:
        with builtins.open(inside, "w", encoding="utf-8") as stream:
            stream.write("guard")
        try:
            with builtins.open(outside, "w", encoding="utf-8") as stream:
                stream.write("guard")
        except WriteDeniedError:
            return
        raise BoundaryGuardError("write path guard failed to deny an outside write")
    finally:
        if inside.exists():
            original_unlink(inside)
        if outside.exists():
            original_unlink(outside)


def _install_write_replacements(root: Path, targets) -> WritePathGuard:
    originals = tuple((owner, name, original) for owner, name, original, _ in targets)
    patches = tuple((owner, name, replacement) for owner, name, _, replacement in targets)
    guard = WritePathGuard(root, originals, patches)
    original_unlink = next(original for owner, name, original in originals if name == "unlink")
    try:
        for owner, name, _, replacement in targets:
            _apply_write_patch(owner, name, replacement)
        _self_test(root, original_unlink)
    except BaseException as exc:
        guard.close()
        raise BoundaryGuardError("write path guard installation failed") from exc
    return guard


def install_write_path_guard(
    run_dir: Path,
    *,
    reports_root: Path | None = None,
) -> WritePathGuard:
    """Install, self-test, and return a fail-closed run-directory write guard."""
    selected_root = (
        Path(__file__).resolve().parents[4] / "reports" if reports_root is None else reports_root
    )
    root = _validate_run_dir(Path(run_dir), Path(selected_root))
    target_names = (
        (builtins, "open"),
        (io, "open"),
        (os, "open"),
        (os, "mkdir"),
        (os, "makedirs"),
        (os, "rename"),
        (os, "replace"),
        (os, "remove"),
        (os, "unlink"),
        (os, "rmdir"),
        (os, "symlink"),
        (os, "link"),
    )
    originals = {(owner, name): getattr(owner, name) for owner, name in target_names}
    targets = (
        (
            builtins,
            "open",
            originals[builtins, "open"],
            _guard_open(originals[builtins, "open"], root),
        ),
        (io, "open", originals[io, "open"], _guard_open(originals[io, "open"], root)),
        (os, "open", originals[os, "open"], _guard_os_open(originals[os, "open"], root)),
        (os, "mkdir", originals[os, "mkdir"], _guard_path_operation(originals[os, "mkdir"], root)),
        (
            os,
            "makedirs",
            originals[os, "makedirs"],
            _guard_path_operation(originals[os, "makedirs"], root),
        ),
        (os, "rename", originals[os, "rename"], _guard_move(originals[os, "rename"], root)),
        (os, "replace", originals[os, "replace"], _guard_move(originals[os, "replace"], root)),
        (
            os,
            "remove",
            originals[os, "remove"],
            _guard_path_operation(originals[os, "remove"], root),
        ),
        (
            os,
            "unlink",
            originals[os, "unlink"],
            _guard_path_operation(originals[os, "unlink"], root),
        ),
        (os, "rmdir", originals[os, "rmdir"], _guard_path_operation(originals[os, "rmdir"], root)),
        (os, "symlink", originals[os, "symlink"], _deny_link),
        (os, "link", originals[os, "link"], _deny_link),
    )
    return _install_write_replacements(root, targets)
