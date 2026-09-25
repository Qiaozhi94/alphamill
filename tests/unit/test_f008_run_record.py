"""`DR-003` / T013 检视回归：运行记录的原子落盘、fail-closed 载入与续跑参数校验。

三条 finding（2026-09-24 代码检视第 1 轮）：
- R1-027：`run.json` 曾是截断式原地写，中断留下半截 JSON，而分片脚本固定带 `--resume-run-id`；
- R1-014：`load_run` 不校验 `schema_version`，版本漂移被静默按新契约解读；
- R1-009：`--resume-run-id` 不校验目标集合/窗口，换窗口续跑会静默空跑并报「本批全部完成」。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe import run_record
from alphamill.data_bridge.universe.batching import PairPlan, resume_mismatch
from alphamill.data_bridge.universe.errors import BackfillIncompleteError

START = datetime(2026, 9, 1, tzinfo=UTC)
END = datetime(2026, 9, 2, tzinfo=UTC)


def _run(run_id: str = "u-b1-20260901T000000Z") -> runner.BackfillRun:
    return runner.BackfillRun(
        run_id=run_id,
        universe_id="sha256:" + "a" * 64,
        batch=1,
        window_start="2026-09-01T00:00:00Z",
        window_end="2026-09-02T00:00:00Z",
        rate_limit={"min_interval_seconds": 0.2},
        hostname="qiaozhi-lt",
        started_at="2026-09-01T00:00:00Z",
        pairs=(
            {"db_symbol": "BTC/USDT", "lake_pair": "BTC-USDT-PERP", "rank": 1, "listed_at": None},
        ),
        finished_at=None,
    )


def test_write_run_document_keeps_previous_document_when_replace_fails(monkeypatch, tmp_path):
    """R1-027：更新走原子替换——替换失败时盘上仍是**上一份完整文档**，不是半截。

    变异验证：把 `os.replace` 换回 `target.write_bytes(payload)` 后本用例必红（旧内容被覆盖）。
    """
    reports = tmp_path / "reports"
    run_record.write_run_document("run-A", _run().document(), reports)
    target = run_record.run_dir("run-A", reports) / run_record.RUN_FILE
    first = json.loads(target.read_text(encoding="utf-8"))
    assert first["hostname"] == "qiaozhi-lt"

    def _boom(*_args):
        raise OSError("模拟替换瞬间断电")

    monkeypatch.setattr(run_record.os, "replace", _boom)
    with pytest.raises(OSError):
        run_record.write_run_document("run-A", {**first, "hostname": "别的机器"}, reports)

    survived = json.loads(target.read_text(encoding="utf-8"))
    assert survived == first, "替换失败时盘上必须是上一份完整文档"


def test_read_run_document_rejects_corrupt_and_missing(tmp_path):
    """R1-027/R1-014：损坏（半截 JSON）与缺失都判红，且是明确的领域错误而非裸异常。"""
    reports = tmp_path / "reports"
    target_dir = run_record.run_dir("run-B", reports)
    target_dir.mkdir(parents=True)
    (target_dir / run_record.RUN_FILE).write_text('{"schema_version": 1, "wind', encoding="utf-8")
    with pytest.raises(BackfillIncompleteError, match="损坏"):
        run_record.read_run_document("run-B", reports)

    with pytest.raises(BackfillIncompleteError, match="不存在"):
        run_record.read_run_document("run-missing", reports)


def test_read_run_document_rejects_non_object_and_missing_keys(tmp_path):
    """回归（检视 R2-B5）：合法 JSON 但非对象 / 缺必需键都必须转成领域错误。

    缺陷形态：`document.get(...)` 在 `isinstance(document, dict)` 之前 → `[1,2,3]` 抛
    `AttributeError`、缺 `run_id` 在 `load_run` 抛 `KeyError`——两者都逃出 `cli.main` 的
    `except (UniverseError, OSError)`，变成 traceback + 退出 1（分片脚本会当可重试瞬时故障）。
    """
    reports = tmp_path / "reports"
    target_dir = run_record.run_dir("run-F", reports)
    target_dir.mkdir(parents=True)

    (target_dir / run_record.RUN_FILE).write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(BackfillIncompleteError, match="顶层应为对象"):
        run_record.read_run_document("run-F", reports)

    (target_dir / run_record.RUN_FILE).write_text(
        '{"schema_version": 1, "window": {}}', encoding="utf-8"
    )
    with pytest.raises(BackfillIncompleteError, match="缺必需键"):
        run_record.read_run_document("run-F", reports)


def test_load_run_rejects_unknown_schema_version(tmp_path):
    """R1-014：`schema_version` 不符必须拒载，不得静默按新契约解读旧记录。"""
    reports = tmp_path / "reports"
    document = {**_run().document(), "schema_version": 2}
    run_record.write_run_document("run-C", document, reports)

    with pytest.raises(BackfillIncompleteError, match="schema_version 不符"):
        runner.load_run("run-C", reports)


def test_load_run_accepts_current_schema_version(tmp_path):
    """正向对照：同一份文档在版本正确时可载入（证明上面的拒绝来自版本而非其它原因）。"""
    reports = tmp_path / "reports"
    run_record.write_run_document("run-D", _run("run-D").document(), reports)
    loaded = runner.load_run("run-D", reports)
    assert loaded.run_id == "run-D"
    assert loaded.document()["schema_version"] == runner.SCHEMA_VERSION


def _plan(symbol: str) -> PairPlan:
    return PairPlan(
        db_symbol=symbol, lake_pair=f"{symbol.split('/')[0]}-USDT-PERP", rank=1, listed_at=None
    )


def test_resume_mismatch_covers_universe_window_and_pairs() -> None:
    """R1-009：续跑与请求的三处不一致都要被指出来（否则换窗口续跑会静默空跑报成功）。"""
    run = _run()
    assert resume_mismatch(run, run.universe_id, START, END, (_plan("BTC/USDT"),)) is None

    assert "universe_id" in resume_mismatch(run, "sha256:" + "b" * 64, START, END, ())
    assert "窗口" in resume_mismatch(
        run, run.universe_id, START, datetime(2026, 9, 3, tzinfo=UTC), ()
    )
    why = resume_mismatch(run, run.universe_id, START, END, (_plan("ETH/USDT"),))
    assert why is not None and "目标集合" in why


def test_write_run_document_creates_once_and_then_updates(tmp_path):
    """首次写入是「写一次」（同 id 不覆盖），之后才允许原子更新。"""
    reports = tmp_path / "reports"
    run = _run("run-E")
    run_record.write_run_document(run.run_id, run.document(), reports)
    target = run_record.run_dir(run.run_id, reports) / run_record.RUN_FILE
    original = target.read_bytes()
    run_record.write_run_document(run.run_id, {**run.document(), "finished_at": "x"}, reports)
    assert target.read_bytes() != original
    assert json.loads(target.read_text(encoding="utf-8"))["finished_at"] == "x"
    assert not list(Path(target.parent).glob("*.tmp")), "原子替换不得留下临时文件"
