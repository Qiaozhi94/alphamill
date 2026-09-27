"""F012 代码检视第 1 轮回归：CLI 异常归属与收尾（R-A1~R-A5）。"""

from __future__ import annotations

import pytest
from _f012_cli_support import _mine, install_alphagen_runtime
from test_f003_cli_contract import _read_mine_run

from alphamill.factor_factory.cli import EXIT_FAILED
from alphamill.factor_factory.errors import SchemaValidationError


@pytest.fixture()
def alphagen_runtime(monkeypatch):
    return install_alphagen_runtime(monkeypatch)


@pytest.mark.parametrize(
    "error",
    [SchemaValidationError("panel lacks close column"), ValueError("cuda"), TypeError("x")],
    ids=["schema", "value", "type"],
)
def test_errors_raised_during_training_fail_the_run_not_the_config(
    tmp_path, alphagen_runtime, error
) -> None:
    """R-A1：design §7——训练期结构类/未列出异常记 failed，不伪装成 invalid_config。"""
    _, state = alphagen_runtime
    state["produce_error"] = error

    code, reports_root = _mine(tmp_path)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_FAILED
    assert (run["status"], run["termination"]) == ("failed", type(error).__name__)
