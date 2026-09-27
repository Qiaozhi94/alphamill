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


def test_incomplete_cost_model_is_rejected_before_kronos_offload(
    tmp_path, alphagen_runtime, monkeypatch
) -> None:
    """R-A2：一层深合并下只给部分 cost_model 会缺键；须在卸载 Kronos 前以 invalid_config 拒绝。"""
    from _f012_cli_support import _config

    from alphamill.factor_factory import cli as cli_module
    from alphamill.factor_factory.cli import EXIT_REJECTED

    calls, _ = alphagen_runtime
    monkeypatch.setattr(
        cli_module.gpu_slot, "query_vram", lambda: type("V", (), {"free_gb": 8.0})()
    )
    config = _config(tmp_path, {"objective": {"cost_model": {"taker_fee_bps": 10}}})

    code, reports_root = _mine(tmp_path, "--config", str(config), allow_cpu=False)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_REJECTED and run["termination"] == "invalid_config", run
    assert calls.offload == 0


def test_unlisted_exception_still_publishes_a_failed_run(tmp_path, alphagen_runtime) -> None:
    """R-A2：design §7「其他未列出的异常」→ failed 并写 run.json，不以 traceback 退出。"""
    _, state = alphagen_runtime
    state["produce_error"] = KeyError("maker_fee_bps")

    code, reports_root = _mine(tmp_path)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_FAILED and (run["status"], run["termination"]) == ("failed", "KeyError")


@pytest.mark.parametrize("rule", ["sign", "foo"])
def test_position_rule_other_than_cs_median_is_rejected(tmp_path, alphagen_runtime, rule) -> None:
    """R-A3：预筛固定按 cs_median（Q-005）；run.json 不能记一个没被使用的规则。"""
    from _f012_cli_support import _config

    from alphamill.factor_factory.cli import EXIT_REJECTED

    config = _config(tmp_path, {"objective": {"position_rule": rule}})

    code, reports_root = _mine(tmp_path, "--config", str(config))

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_REJECTED and run["termination"] == "invalid_config", run


def test_seed_leaves_signal_handling_alone(tmp_path, monkeypatch) -> None:
    """R-A4：seed 无检查点；接管 SIGTERM 只会把信号吞掉。"""
    import signal

    from test_f003_cli_contract import _build_cli_fixture

    from alphamill.factor_factory.cli import EXIT_OK, main
    from alphamill.factor_factory.generators.manual import seeds

    seen = []
    original = seeds.ManualGenerator.produce

    def spy(self, request):
        seen.append(signal.getsignal(signal.SIGTERM))
        return original(self, request)

    monkeypatch.setattr(seeds.ManualGenerator, "produce", spy)
    lake_root, reports_root, binding_path = _build_cli_fixture(tmp_path)
    before = signal.getsignal(signal.SIGTERM)

    code = main(
        ["seed", "--generator", "manual", "--binding", str(binding_path), "--seed", "3"],
        reports_root=reports_root,
        lake_root=lake_root,
    )

    assert code == EXIT_OK and seen == [before]


def test_manual_mine_interrupted_before_generation_is_partial(tmp_path, monkeypatch) -> None:
    """R-A4：manual mine 在生成前收到 SIGTERM → partial/interrupted，而不是照常 completed。"""
    import os
    import signal

    from test_f003_cli_contract import _prepare_mine_runtime

    from alphamill.factor_factory import cli as cli_module
    from alphamill.factor_factory.cli import EXIT_OK

    _prepare_mine_runtime(monkeypatch)

    def window_then_sigterm(*_args, **_kwargs) -> bool:
        os.kill(os.getpid(), signal.SIGTERM)
        return True

    monkeypatch.setattr(cli_module.gpu_slot, "in_training_window", window_then_sigterm)

    code, reports_root = _mine(tmp_path, generator="manual")

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_OK
    assert (run["status"], run["stop_reason"]) == ("partial", "interrupted")


def test_summary_failure_after_publish_does_not_flip_the_exit_code(
    tmp_path, alphagen_runtime, monkeypatch, capsys
) -> None:
    """R-A5：run.json 已发布为 completed 后，摘要打印失败不能再走异常收尾（二次 finalize、exit≠0）。"""
    from alphamill.factor_factory import manifest_builder
    from alphamill.factor_factory.cli import EXIT_OK

    def broken(_path):
        raise ValueError("prefilter.jsonl corrupt line")

    monkeypatch.setattr(manifest_builder, "_prefilter_elapsed", broken)

    code, reports_root = _mine(tmp_path)

    _, run, _ = _read_mine_run(reports_root)
    assert code == EXIT_OK and run["status"] == "completed"
    assert "summary" in capsys.readouterr().err
