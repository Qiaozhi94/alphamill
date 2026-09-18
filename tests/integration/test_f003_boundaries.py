"""F003 NFR-004 / AC-011：进程级 egress 与写路径护栏集成测试。"""

from __future__ import annotations

import builtins
import io
import os
import socket
from pathlib import Path

import pytest

import alphamill.factor_factory.generators.egress_guard as egress_guard_module
import alphamill.factor_factory.generators.write_guard as write_guard_module
from alphamill.factor_factory.errors import (
    BoundaryGuardError,
    EgressDeniedError,
    WriteDeniedError,
)
from alphamill.factor_factory.generators.egress_guard import install_egress_guard
from alphamill.factor_factory.generators.write_guard import install_write_path_guard

pytestmark = pytest.mark.integration


def _make_run_dir(tmp_path: Path) -> tuple[Path, Path]:
    reports_root = tmp_path / "reports"
    run_dir = reports_root / "generation" / "run-001"
    run_dir.mkdir(parents=True)
    return reports_root, run_dir


def test_egress_guard_denies_network_and_restores_socket_state() -> None:
    original_socket = socket.socket
    guard = install_egress_guard()

    try:
        assert guard.active
        guard.verify()
        with pytest.raises(EgressDeniedError):
            socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as unix_socket:
            assert unix_socket.family == socket.AF_UNIX
        with pytest.raises(EgressDeniedError):
            socket.create_connection(("127.0.0.1", 1))
    finally:
        guard.close()

    assert not guard.active
    assert socket.socket is original_socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as inet_socket:
        assert inet_socket.family == socket.AF_INET


def test_egress_guard_fromfd_only_allows_unix_family() -> None:
    guard = install_egress_guard()
    left, right = socket.socketpair()

    try:
        with pytest.raises(EgressDeniedError):
            socket.fromfd(-1, socket.AF_INET, socket.SOCK_STREAM)
        duplicate = socket.fromfd(left.fileno(), socket.AF_UNIX, socket.SOCK_STREAM)
        duplicate.close()
    finally:
        left.close()
        right.close()
        guard.close()


def test_egress_guard_rolls_back_when_a_patch_step_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    original_socket = socket.socket
    original_create_connection = socket.create_connection
    original_fromfd = socket.fromfd
    apply_patch = egress_guard_module._apply_socket_patch

    def fail_create_connection_patch(name, replacement) -> None:
        if name == "create_connection":
            raise RuntimeError("forced patch failure")
        apply_patch(name, replacement)

    monkeypatch.setattr(egress_guard_module, "_apply_socket_patch", fail_create_connection_patch)

    with pytest.raises(BoundaryGuardError):
        install_egress_guard()

    assert socket.socket is original_socket
    assert socket.create_connection is original_create_connection
    assert socket.fromfd is original_fromfd


def test_write_guard_rolls_back_when_a_patch_step_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reports_root, run_dir = _make_run_dir(tmp_path)
    originals = (builtins.open, io.open, os.open, os.mkdir, os.symlink, os.link)
    apply_patch = write_guard_module._apply_write_patch

    def fail_os_open_patch(owner, name, replacement) -> None:
        if owner is os and name == "open":
            raise RuntimeError("forced patch failure")
        apply_patch(owner, name, replacement)

    monkeypatch.setattr(write_guard_module, "_apply_write_patch", fail_os_open_patch)

    with pytest.raises(BoundaryGuardError):
        install_write_path_guard(run_dir, reports_root=reports_root)

    assert (builtins.open, io.open, os.open, os.mkdir, os.symlink, os.link) == originals


def test_write_guard_confines_writes_and_restores_open(tmp_path: Path) -> None:
    reports_root, run_dir = _make_run_dir(tmp_path)
    original_open = builtins.open
    guard = install_write_path_guard(run_dir, reports_root=reports_root)

    try:
        assert guard.active
        assert guard.root == run_dir.resolve()
        guard.verify()
        (run_dir / "inside.txt").write_text("allowed", encoding="utf-8")
        with pytest.raises(WriteDeniedError):
            (tmp_path / "elsewhere.txt").write_text("denied", encoding="utf-8")
        with pytest.raises(WriteDeniedError):
            (reports_root / "parent.txt").write_text("denied", encoding="utf-8")
        with pytest.raises(WriteDeniedError):
            (run_dir / ".." / ".." / "traversal.txt").write_text("denied", encoding="utf-8")

        source = run_dir / "source.txt"
        source.write_text("source", encoding="utf-8")
        with pytest.raises(WriteDeniedError):
            os.rename(source, tmp_path / "renamed-outside.txt")
    finally:
        guard.close()

    assert not guard.active
    assert builtins.open is original_open
    (tmp_path / "elsewhere.txt").write_text("restored", encoding="utf-8")


def test_write_guard_rejects_escaping_symlinks_and_new_links(tmp_path: Path) -> None:
    reports_root, run_dir = _make_run_dir(tmp_path)
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    escaping_parent = run_dir / "escaping-parent"
    escaping_parent.symlink_to(outside_dir, target_is_directory=True)
    source = run_dir / "source.txt"
    source.write_text("source", encoding="utf-8")

    with install_write_path_guard(run_dir, reports_root=reports_root):
        with pytest.raises(WriteDeniedError):
            (escaping_parent / "escaped.txt").write_text("denied", encoding="utf-8")
        with pytest.raises(WriteDeniedError):
            os.symlink(source, run_dir / "new-symlink")
        with pytest.raises(WriteDeniedError):
            os.link(source, run_dir / "new-hard-link")


def test_write_guard_rejects_run_dir_with_wrong_shape(tmp_path: Path) -> None:
    reports_root = tmp_path / "reports"
    wrong_run_dir = reports_root / "other" / "run-001"
    wrong_run_dir.mkdir(parents=True)

    with pytest.raises(BoundaryGuardError):
        install_write_path_guard(wrong_run_dir, reports_root=reports_root)


def test_write_guard_rejects_missing_run_dir(tmp_path: Path) -> None:
    reports_root = tmp_path / "reports"
    reports_root.mkdir()

    with pytest.raises(BoundaryGuardError):
        install_write_path_guard(reports_root / "generation" / "missing", reports_root=reports_root)


def test_egress_guard_context_restores_after_body_error() -> None:
    original_socket = socket.socket

    with pytest.raises(RuntimeError), install_egress_guard() as guard:
        assert guard.active
        raise RuntimeError("body failure")

    assert socket.socket is original_socket


def test_write_guard_context_restores_after_body_error(tmp_path: Path) -> None:
    reports_root, run_dir = _make_run_dir(tmp_path)
    original_open = builtins.open

    with (
        pytest.raises(RuntimeError),
        install_write_path_guard(run_dir, reports_root=reports_root) as guard,
    ):
        assert guard.active
        raise RuntimeError("body failure")

    assert builtins.open is original_open
