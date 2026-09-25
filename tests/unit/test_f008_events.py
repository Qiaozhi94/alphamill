"""T010 / `AC-010`：F008 事件流的 append-only、幂等去重与 fail-closed schema（design §4）。

覆盖 `TR-001`/`TR-002`：三类事件 append → read 往返；canonical JSONL 行（键排序、紧凑、无多余
空白、行尾换行）；幂等键（成员 `(lake_pair, effective_at, direction, line)`，回填
`(run_id, lake_pair, cursor)`，failed 用 `last_cursor`）去重且并发下成立；append-only 不覆盖
历史；按 `run_id`/`lake_pair`/`line` 查询；缺字段、未知字段、未知 `schema_version`、非
canonical 行、非法枚举与计数一律判红；`ALPHAMILL_EVENTS_DIR` 覆盖生效。非法 fixture 由 `_raw()`
落盘原始行构造，事件目录一律走 `tmp_path`（`store` fixture），不写仓库 `reports/`。
"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from alphamill.data_bridge.universe import event_store, events
from alphamill.data_bridge.universe.errors import UniverseError

ROOT = Path(__file__).resolve().parents[2]
MEMBER = events.EVENT_MEMBER_CHANGED
PROGRESS = events.EVENT_BACKFILL_PROGRESS
FAILED = events.EVENT_BACKFILL_FAILED
RECORDED = "2026-01-01T00:00:00Z"
EFFECTIVE = "2024-09-10T00:00:00Z"
CURSOR = "2024-09-11T00:00:00Z"


@pytest.fixture
def store(tmp_path: Path) -> Path:
    """事件根目录：每个测试独立 `tmp_path`，绝不落到仓库 `reports/` 下。"""
    return tmp_path / "events"


def _member(**override: Any) -> events.MemberChangedEvent:
    base: dict[str, Any] = {"lake_pair": "BTC-USDT-PERP", "direction": "in", "line": "tradability"}
    base |= {"effective_at": EFFECTIVE, "reason": "listed", "universe_id": "uni-1"}
    return events.member_changed_event(**{"recorded_at": RECORDED, **base, **override})


def _progress(**override: Any) -> events.BackfillProgressEvent:
    base: dict[str, Any] = {"run_id": "run-1", "lake_pair": "BTC-USDT-PERP", "rows": 1440}
    base |= {"cursor": CURSOR, "elapsed": 12.5}
    return events.backfill_progress_event(**{"recorded_at": RECORDED, **base, **override})


def _failed(**override: Any) -> events.BackfillFailedEvent:
    base: dict[str, Any] = {"run_id": "run-1", "lake_pair": "BTC-USDT-PERP", "retries": 5}
    base |= {"error_class": "RateLimitExceeded", "last_cursor": None}
    return events.backfill_failed_event(**{"recorded_at": RECORDED, **base, **override})


def _doc(event: events.Event, **override: Any) -> dict[str, Any]:
    """事件 → canonical 文档（可加/改键，用于构造非法行）。"""
    return {**events.event_document(event), **override}


def _text(document: dict[str, Any]) -> str:
    """键排序 + 紧凑分隔的 canonical 行文本（含换行）。"""
    return json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"


def _raw(store: Path, event_type: str, text: str) -> Path:
    """绕过写入 API 直接落盘原始行：非法 fixture、canonicity 变体、半行文件都靠它。"""
    path = store / f"{event_type}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _seed(store: Path, *items: events.Event) -> None:
    for item in items:
        assert events.append_event(item, events_dir=store) is True


def test_event_round_trip(store: Path) -> None:
    _seed(store, _member(), _progress(elapsed=3), _failed())
    [member] = events.read_events(MEMBER, events_dir=store)
    progress = events.read_events(PROGRESS, events_dir=store)
    failed = events.read_events(FAILED, events_dir=store)
    assert type(member) is events.MemberChangedEvent
    assert (member.lake_pair, member.direction, member.line, member.reason, member.universe_id) == (
        "BTC-USDT-PERP",
        "in",
        "tradability",
        "listed",
        "uni-1",
    )
    assert (member.effective_at, member.recorded_at, member.schema_version) == (
        datetime(2024, 9, 10, tzinfo=UTC),
        datetime(2026, 1, 1, tzinfo=UTC),
        1,
    )
    assert type(progress[0]) is events.BackfillProgressEvent
    assert (progress[0].rows, progress[0].cursor, progress[0].elapsed) == (1440, CURSOR, 3.0)
    assert type(failed[0]) is events.BackfillFailedEvent
    assert (failed[0].error_class, failed[0].retries, failed[0].last_cursor) == (
        "RateLimitExceeded",
        5,
        None,
    )


def test_canonical_lines_and_default_recorded_at(store: Path) -> None:
    event = _member()
    _seed(store, event)
    raw = (store / f"{MEMBER}.jsonl").read_text(encoding="utf-8")
    assert raw == events.canonical_line(event) == _text(events.event_document(event))
    assert raw.endswith("\n") and raw.count("\n") == 1
    assert ": " not in raw and ", " not in raw
    assert list(json.loads(raw)) == sorted(events.event_document(event))

    before = datetime.now(UTC)
    _seed(store, _progress(recorded_at=None))
    [item] = events.read_events(PROGRESS, events_dir=store)
    assert item.recorded_at.tzinfo is UTC and before <= item.recorded_at <= datetime.now(UTC)
    stored = json.loads((store / f"{PROGRESS}.jsonl").read_text(encoding="utf-8"))
    assert stored["recorded_at"].endswith("Z")


def test_member_dedup_uses_pair_effective_direction_line(store: Path) -> None:
    event = _member()
    assert events.idempotency_key(event) == ("BTC-USDT-PERP", EFFECTIVE, "in", "tradability")
    _seed(store, event)
    assert events.append_event(_member(), events_dir=store) is False  # 同键
    again = _member(recorded_at="2026-02-02T00:00:00Z")  # recorded_at 不参与幂等键
    assert events.append_event(again, events_dir=store) is False
    for variant in (
        _member(effective_at="2024-10-01T00:00:00Z"),
        _member(direction="out"),
        _member(line="admission", reason="universe_reselect"),
        _member(lake_pair="ETH-USDT-PERP"),
    ):
        assert events.append_event(variant, events_dir=store) is True
    stored = events.read_events(MEMBER, events_dir=store)
    assert len(stored) == 5
    assert (stored[3].line, stored[3].reason) == ("admission", "universe_reselect")


def test_backfill_dedup_and_append_only_history(store: Path) -> None:
    _seed(store, _progress(rows=1, elapsed=1.0))
    # 同 (run, pair, cursor)：rows/elapsed 变化不算新键
    assert events.append_event(_progress(rows=999), events_dir=store) is False
    for variant in (
        _progress(cursor="2024-09-12T00:00:00Z"),
        _progress(run_id="run-2"),
        _progress(lake_pair="ETH-USDT-PERP"),
    ):
        assert events.append_event(variant, events_dir=store) is True
    assert len(events.read_events(PROGRESS, events_dir=store)) == 4

    _seed(store, _failed())
    assert events.append_event(_failed(retries=9, error_class="Other"), events_dir=store) is False
    later = _failed(last_cursor="2024-09-13T00:00:00Z")
    assert events.append_event(later, events_dir=store) is True
    assert len(events.read_events(FAILED, events_dir=store)) == 2

    path = store / f"{PROGRESS}.jsonl"
    before = path.read_bytes()
    _seed(store, _progress(lake_pair="SOL-USDT-PERP"))
    assert events.append_event(_progress(), events_dir=store) is False  # 去重，不是覆盖
    after = path.read_bytes()
    assert after.startswith(before) and after.count(b"\n") == 5
    assert events.read_events(PROGRESS, events_dir=store)[0].cursor == CURSOR


def test_concurrent_appends_are_atomic_and_deduped(store: Path) -> None:
    failures: list[BaseException] = []
    appended: list[bool] = []

    def worker(index: int) -> None:
        try:
            for step in range(5):
                events.append_event(
                    _progress(lake_pair=f"PAIR-{index}", cursor=f"cursor-{step}"), events_dir=store
                )
            appended.append(events.append_event(_progress(), events_dir=store))
        except BaseException as exc:
            failures.append(exc)

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert failures == []
    assert (store / f"{PROGRESS}.jsonl").read_text(encoding="utf-8").count("\n") == 41
    assert len(events.read_events(PROGRESS, events_dir=store)) == 41
    assert appended.count(True) == 1 and appended.count(False) == 7  # 同键只落一行


def test_read_filters_and_stream_guardrails(store: Path) -> None:
    _seed(
        store,
        _progress(run_id="run-1"),
        _progress(run_id="run-2"),
        _progress(run_id="run-2", lake_pair="ETH-USDT-PERP"),
        _failed(run_id="run-2"),
        _member(),
        _member(line="admission", reason="universe_reselect"),
    )
    by_run = events.read_events(PROGRESS, run_id="run-2", events_dir=store)
    assert [item.run_id for item in by_run] == ["run-2", "run-2"]
    by_pair = events.read_events(PROGRESS, lake_pair="ETH-USDT-PERP", events_dir=store)
    assert [item.run_id for item in by_pair] == ["run-2"]
    both = events.read_events(FAILED, run_id="run-2", lake_pair="BTC-USDT-PERP", events_dir=store)
    assert len(both) == 1
    admission = events.read_events(MEMBER, line="admission", events_dir=store)
    assert [item.line for item in admission] == ["admission"]
    combo = events.read_events(
        MEMBER, lake_pair="BTC-USDT-PERP", line="tradability", events_dir=store
    )
    assert len(combo) == 1

    for event_type, filters in (
        (MEMBER, {"run_id": "run-1"}),  # 类型没有该字段：判红，不静默忽略
        (PROGRESS, {"line": "tradability"}),
        (FAILED, {"line": "admission"}),
    ):
        with pytest.raises(events.EventsError, match="不能按"):
            events.read_events(event_type, events_dir=store, **filters)
    for call in (
        lambda: events.read_events("universe.renamed", events_dir=store),
        lambda: events.event_path("universe.renamed", events_dir=store),
    ):
        with pytest.raises(events.EventsError, match="未知事件类型"):
            call()

    empty = store / "empty"  # 文件不存在或为空都读作空流，不是错误
    empty.mkdir(parents=True)
    (empty / f"{FAILED}.jsonl").write_text("", encoding="utf-8")
    assert events.read_events(FAILED, events_dir=empty) == ()
    assert events.read_events(FAILED, events_dir=store / "missing") == ()


@pytest.mark.parametrize(
    ("override", "match"),
    [
        ({"event_type": "universe.renamed"}, "未知事件类型"),
        ({"schema_version": 2}, "schema_version"),
        ({"schema_version": "1"}, "schema_version"),
        ({"schema_version": True}, "schema_version"),
        ({"hostname": "qiaozhi-lt"}, "unknown"),
    ],
)
def test_invalid_line_documents_are_rejected_and_stop_appends(
    store: Path, override: dict[str, Any], match: str
) -> None:
    _raw(store, MEMBER, _text(_doc(_member(), **override)))
    with pytest.raises(events.EventsError, match=match):
        events.read_events(MEMBER, events_dir=store)
    with pytest.raises(events.EventsError, match=match):
        events.append_event(_member(lake_pair="SOL-USDT-PERP"), events_dir=store)


def test_missing_field_and_file_level_violations(store: Path) -> None:
    missing = _doc(_member())
    del missing["reason"]
    shuffled = events.event_document(_member())
    body = ",".join(f'"{k}":{json.dumps(shuffled[k])}' for k in reversed(shuffled))
    unsorted = "{" + body + "}\n"
    cases = (
        (_text(missing), "missing="),  # 缺字段
        (_text(_doc(_member(), event_type=PROGRESS)), "键集合非法"),  # 键集合与申报类型不符
        (json.dumps(events.event_document(_member()), ensure_ascii=False) + "\n", "canonical"),
        (unsorted, "canonical"),
        (_text(_doc(_member(), effective_at="2024-09-10T08:00:00+08:00")), "canonical UTC"),
    )
    for text, match in cases:
        with pytest.raises(events.EventsError, match=match):
            events.parse_line(text)
    _raw(store, MEMBER, _text(missing))
    with pytest.raises(events.EventsError, match="missing="):
        events.append_event(_member(), events_dir=store)  # 非法历史行让追加一起判红

    for tail in ("", "\n\n"):  # 末行缺换行 / 多空行：读与追加都判红
        _raw(store, MEMBER, _text(events.event_document(_member())).rstrip("\n") + tail)
        with pytest.raises(events.EventsError):
            events.read_events(MEMBER, events_dir=store)
        with pytest.raises(events.EventsError):
            events.append_event(_member(), events_dir=store)


@pytest.mark.parametrize(
    ("builder", "payload", "match"),
    [
        (_member, {"lake_pair": ""}, "lake_pair"),
        (_member, {"lake_pair": " BTC-USDT-PERP"}, "lake_pair"),
        (_member, {"direction": "IN"}, "direction"),
        (_member, {"line": "seed"}, "line"),
        (_member, {"reason": "universe_reselect"}, "tradability"),
        (_member, {"reason": "listed", "line": "admission"}, "admission"),
        (_member, {"effective_at": None}, "effective_at"),
        (_member, {"effective_at": datetime(2024, 9, 10)}, "effective_at"),
        (_member, {"hostname": "qiaozhi-lt"}, "unknown"),
        (_progress, {"rows": -1}, "rows"),
        (_progress, {"cursor": ""}, "cursor"),
        (_progress, {"elapsed": float("nan")}, "elapsed"),
        (_failed, {"retries": -1}, "retries"),
        (_failed, {"last_cursor": 123}, "last_cursor"),
    ],
)
def test_write_side_rejects_bad_fields(builder: Any, payload: dict[str, Any], match: str) -> None:
    with pytest.raises(events.EventsError, match=match):
        builder(**payload)


def test_write_side_missing_field_foreign_object_and_version_guard() -> None:
    with pytest.raises(events.EventsError, match="missing="):
        events.build_event(MEMBER, lake_pair="BTC-USDT-PERP", effective_at=EFFECTIVE)
    payload = {key: value for key, value in _doc(_progress()).items() if key != "event_type"}
    forced = events.build_event(PROGRESS, **{**payload, "schema_version": 99})
    assert forced.schema_version == events.SCHEMA_VERSION == 1  # 调用方不可覆写

    class Alien:
        pass

    for call in (lambda: events.event_document(Alien()), lambda: events.idempotency_key(Alien())):
        with pytest.raises(events.EventsError, match="未知事件对象类型"):
            call()  # type: ignore[arg-type]


def test_events_dir_env_override_and_reexports(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv(events.ENV_EVENTS_DIR, str(tmp_path / "from-env"))
    assert events.default_events_dir() == (tmp_path / "from-env").resolve()
    assert events.append_event(_progress(), events_dir=None) is True
    assert (tmp_path / "from-env" / f"{PROGRESS}.jsonl").is_file()
    assert len(events.read_events(PROGRESS)) == 1  # 无 events_dir 时走环境变量

    explicit = tmp_path / "explicit"
    assert events.append_event(_progress(), events_dir=explicit) is True
    assert (explicit / f"{PROGRESS}.jsonl").is_file()
    assert events.default_events_dir() == (tmp_path / "from-env").resolve()

    monkeypatch.delenv(events.ENV_EVENTS_DIR)
    assert events.default_events_dir() == ROOT / "reports" / "universe" / "events"
    for name in ("read_events", "parse_line", "event_path", "EventsError", "MemberChangedEvent"):
        assert getattr(events, name) is getattr(event_store, name)
    assert events.SCHEMA_VERSION == event_store.SCHEMA_VERSION == 1
    assert issubclass(events.EventsError, UniverseError)
    assert events.EventsError.code == "E_UNIVERSE_EVENTS"
