"""Process-level egress protection for generator runs.

This guard replaces selected socket constructors in the current process and allows only
Unix-domain sockets. It is a process-level guard, not kernel-level network isolation, and
it does not retroactively affect sockets that were already open before installation.
"""

from __future__ import annotations

import socket
from collections.abc import Callable
from types import TracebackType
from typing import NoReturn

from alphamill.factor_factory.errors import BoundaryGuardError, EgressDeniedError


def _apply_socket_patch(name: str, replacement: Callable[..., socket.socket]) -> None:
    setattr(socket, name, replacement)


class EgressGuard:
    """Own the process-wide socket replacements and their restoration lifecycle."""

    __slots__ = (
        "_originals",
        "_patches",
        "_closed",
    )

    def __init__(
        self,
        originals: tuple[tuple[str, Callable[..., socket.socket]], ...],
        patches: tuple[tuple[str, Callable[..., socket.socket]], ...],
    ) -> None:
        self._originals = originals
        self._patches = patches
        self._closed = False

    @property
    def active(self) -> bool:
        """Return whether every egress replacement is still installed."""
        return not self._closed and all(
            getattr(socket, name) is replacement for name, replacement in self._patches
        )

    def verify(self) -> None:
        """Raise when the process no longer has this guard's socket replacements."""
        if not self.active:
            raise BoundaryGuardError("egress guard is not active")

    def close(self) -> None:
        """Restore the saved socket functions once; repeated calls do nothing."""
        if self._closed:
            return
        self._closed = True
        for name, original in self._originals:
            setattr(socket, name, original)

    def __enter__(self) -> EgressGuard:
        """Return this active guard for a context-managed run."""
        self.verify()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Restore socket functions when leaving the context."""
        self.close()

    def _self_test(self) -> None:
        try:
            denied_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except EgressDeniedError:
            pass
        else:
            denied_socket.close()
            raise BoundaryGuardError("egress guard failed to deny AF_INET sockets")

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM):
            pass


def install_egress_guard() -> EgressGuard:
    """Install, self-test, and return a fail-closed process-level egress guard."""
    original_socket = socket.socket
    original_create_connection = socket.create_connection
    original_fromfd = socket.fromfd

    def guarded_socket(
        family: int = -1,
        type: int = -1,
        proto: int = -1,
        fileno: int | None = None,
    ) -> socket.socket:
        if family != socket.AF_UNIX:
            raise EgressDeniedError("only AF_UNIX sockets are permitted")
        return original_socket(family=family, type=type, proto=proto, fileno=fileno)

    def guarded_create_connection(*_args, **_kwargs) -> NoReturn:
        raise EgressDeniedError("socket.create_connection is disabled")

    def guarded_fromfd(fd: int, family: int, type: int, proto: int = 0) -> socket.socket:
        if family != socket.AF_UNIX:
            raise EgressDeniedError("only AF_UNIX descriptors are permitted")
        return original_fromfd(fd, family, type, proto)

    originals = (
        ("socket", original_socket),
        ("create_connection", original_create_connection),
        ("fromfd", original_fromfd),
    )
    patches = (
        ("socket", guarded_socket),
        ("create_connection", guarded_create_connection),
        ("fromfd", guarded_fromfd),
    )
    guard = EgressGuard(originals, patches)

    try:
        for name, replacement in patches:
            _apply_socket_patch(name, replacement)
        guard._self_test()
    except BaseException as exc:
        guard.close()
        raise BoundaryGuardError("egress guard installation failed") from exc

    return guard
