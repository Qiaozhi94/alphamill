"""F003 GPU 单槽契约：NFR-002 / NFR-005 / AC-010。"""

from __future__ import annotations

import multiprocessing
import time
from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from alphamill.factor_factory.errors import FactorFactoryError
from alphamill.factor_factory.generators import gpu_slot
from alphamill.factor_factory.generators.gpu_slot import (
    DEFAULT_WINDOW_TZ,
    GpuQueueTimeoutError,
    GpuSlot,
    GpuSlotConfig,
    KronosOffloadOutcome,
    VramReading,
    in_training_window,
    offload_kronos,
    vram_is_sufficient,
)

Payload = dict[str, int | str | bool]
Response = tuple[int, Payload]
# 时段表按执行机本地时间（架构 §7.1）；夜槽夹具一律用本地挂钟构造。
NIGHT = datetime(2026, 9, 19, 23, 0, tzinfo=ZoneInfo(DEFAULT_WINDOW_TZ))


class _FakeClient:
    def __init__(
        self,
        *,
        statuses: tuple[Response, ...] = (),
        stop: Response | None = None,
        health: Response | None = None,
        service_present: bool = True,
        idle_threshold_gb: float | None = 0.5,
        connection_refused: bool = False,
    ) -> None:
        self.service_present = service_present
        self.idle_threshold_gb = idle_threshold_gb
        self._statuses = iter(statuses)
        self._stop = stop or (200, {"state": "stopped"})
        self._health = health or (503, {})
        self._connection_refused = connection_refused

    def request(self, method: str, url: str, contract_version: str, timeout_s: float) -> Response:
        del contract_version, timeout_s
        if self._connection_refused:
            raise ConnectionRefusedError
        if url.endswith("/lifecycle/status"):
            return next(self._statuses)
        return self._health if method == "GET" else self._stop


def _config(*, limit: float = 1.0, timeout: int = 1) -> GpuSlotConfig:
    return GpuSlotConfig(
        vram_limit_gb=limit,
        window_start="22:00",
        window_end="06:30",
        queue_timeout_s=timeout,
    )


def _status(
    *, device: str = "cuda", state: str = "running", vram_bytes: int = 3_000_000_000
) -> Response:
    return 200, {
        "state": state,
        "contract_version": "1",
        "model_loaded": state == "running",
        "vram_bytes": vram_bytes,
        "device": device,
    }


def _contend_and_release(locks_dir: str, config: GpuSlotConfig) -> None:
    slot = GpuSlot(locks_dir=Path(locks_dir), config=config)
    slot.acquire("run-b", now=NIGHT)
    slot.release("run-b", now=NIGHT)


@pytest.mark.parametrize(
    ("hour", "minute", "expected"),
    [(23, 0, True), (5, 0, True), (12, 0, False), (21, 59, False), (6, 29, True), (6, 30, False)],
)
def test_training_window_across_midnight(hour: int, minute: int, expected: bool) -> None:
    # Given: a LOCAL wall-clock time on the execution host (架构 §7.1 时段表按本地时间).
    now = datetime(2026, 9, 19, hour, minute, tzinfo=ZoneInfo(DEFAULT_WINDOW_TZ))
    # When: membership is evaluated.
    actual = in_training_window(now, window_start="22:00", window_end="06:30")
    # Then: start is inclusive and end is exclusive across midnight.
    assert actual is expected


def test_training_window_reads_local_clock_not_utc_clock() -> None:
    """R001 判红点：同一挂钟读数在本地为夜槽、在 UTC 下不是。

    2026-09-19T22:30+08:00 是执行机的夜槽；它的 UTC 表示是 14:30Z。若实现拿
    UTC 挂钟比时段表，这个瞬间会被判成窗口外，而 22:30Z（本地次日 06:30）
    会被误判成窗口内——真正的夜槽永不开启、放行的却是 Kronos 白天常驻时段。
    """
    night_local = datetime(2026, 9, 19, 22, 30, tzinfo=ZoneInfo(DEFAULT_WINDOW_TZ))
    assert night_local.astimezone(UTC).hour == 14

    assert in_training_window(night_local, window_start="22:00", window_end="06:30") is True, (
        "执行机本地 22:30 必须落在夜槽内"
    )
    assert (
        in_training_window(
            datetime(2026, 9, 19, 22, 30, tzinfo=UTC), window_start="22:00", window_end="06:30"
        )
        is False
    ), "22:30Z 对应本地次日 06:30，已在夜槽之外"


def test_training_window_rejects_unknown_timezone_and_naive_instant() -> None:
    with pytest.raises(FactorFactoryError, match="timezone"):
        in_training_window(
            datetime(2026, 9, 19, 23, 0, tzinfo=UTC),
            window_start="22:00",
            window_end="06:30",
            window_tz="Mars/Olympus",
        )
    with pytest.raises(FactorFactoryError, match="timezone-aware"):
        in_training_window(datetime(2026, 9, 19, 23, 0), window_start="22:00", window_end="06:30")


@pytest.mark.parametrize(
    ("reading", "expected"),
    [
        (None, False),
        (VramReading(total_gb=8, free_gb=3.9), False),
        (VramReading(total_gb=8, free_gb=4), True),
        (VramReading(total_gb=8, free_gb=7), True),
    ],
)
def test_vram_sufficiency_has_no_cpu_or_threshold_leak(
    reading: VramReading | None, expected: bool
) -> None:
    # Given: a configurable four-gigabyte limit and a probe result.
    # When: the predicate is evaluated.
    actual = vram_is_sufficient(reading, limit_gb=4)
    # Then: no GPU and below-limit readings fail; equality succeeds.
    assert actual is expected


def test_fifo_two_processes_acquire_in_queue_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: run-a holds the real flock before run-b starts in another process.
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=8))
    slot = GpuSlot(locks_dir=tmp_path, config=_config())
    slot.acquire("run-a", now=NIGHT)
    process = multiprocessing.get_context("fork").Process(
        target=_contend_and_release, args=(str(tmp_path), _config())
    )
    process.start()
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        records = slot.queue_records()
        if any(record.run_id == "run-b" and record.event == "queued" for record in records):
            break
        time.sleep(0.005)
    # When: the first owner releases the slot.
    assert not any(record.run_id == "run-b" and record.event == "acquired" for record in records)
    slot.release("run-a", now=NIGHT)
    process.join(timeout=0.5)
    # Then: the second process acquires next and all normal events are durable.
    if process.is_alive():
        process.terminate()
    assert process.exitcode == 0
    records = slot.queue_records()
    assert [record.queue_seq for record in records] == list(range(1, len(records) + 1))
    assert [record.run_id for record in records if record.event == "acquired"] == ["run-a", "run-b"]
    assert {record.event for record in records} >= {"queued", "acquired", "released"}


def test_waiting_beyond_timeout_records_typed_queue_timeout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: one owner holds the slot and the next run has a zero-second budget.
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=8))
    owner = GpuSlot(locks_dir=tmp_path, config=_config())
    owner.acquire("owner", now=NIGHT)
    waiter = GpuSlot(locks_dir=tmp_path, config=_config(timeout=0))
    # When: the waiter attempts to acquire.
    with pytest.raises(GpuQueueTimeoutError) as exc_info:
        waiter.acquire("waiter", now=NIGHT)
    owner.release("owner", now=NIGHT)
    # Then: callers can map the typed failure to termination=queue_timeout.
    assert exc_info.value.termination == "queue_timeout"
    assert exc_info.value.record.event == "timeout"
    assert waiter.queue_records()[-2].event == "timeout"


def test_low_vram_releases_and_requeues_without_acquired(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: free VRAM is below one configured limit but equal to another.
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=4))
    strict = GpuSlot(locks_dir=tmp_path, config=_config(limit=5, timeout=0))
    # When: the strict run probes after taking the OS lock.
    with pytest.raises(GpuQueueTimeoutError):
        strict.acquire("strict", now=NIGHT)
    strict_records = [record for record in strict.queue_records() if record.run_id == "strict"]
    # Then: it relinquishes and requeues without ever reporting acquired.
    assert "released" in [record.event for record in strict_records]
    assert "acquired" not in [record.event for record in strict_records]
    relaxed = GpuSlot(locks_dir=tmp_path, config=_config(limit=4, timeout=0))
    assert relaxed.acquire("relaxed", now=NIGHT).event == "acquired"
    relaxed.release("relaxed", now=NIGHT)


def test_unreadable_vram_never_acquires_the_slot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R002 判红点：nvidia-smi 读不出来不等于卡是空的，必须留在队列。

    架构 §7.1「队列赢，绝不并行赌 OOM」；读数缺失时取锁正是拿整张卡赌博。
    """
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: None)
    slot = GpuSlot(locks_dir=tmp_path, config=_config(timeout=0))

    with pytest.raises(GpuQueueTimeoutError):
        slot.acquire("blind", now=NIGHT)

    events = [record.event for record in slot.queue_records() if record.run_id == "blind"]
    assert "acquired" not in events, "读数不可得时不得取锁"
    assert events[-1] == "timeout"
    assert all(record.vram_free_gb is None for record in slot.queue_records())


def test_allow_offhours_bypasses_window_without_faking_the_clock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R006 判红点：越窗要走显式开关，队列时间戳必须是真实时钟。

    旧实现把 now 伪造成当天的 window_start 喂给 acquire 来骗过窗口判定，代价是整条
    队列审计的 ts 全是同一个编造值，AC-010「每类状态记录含时间戳」随之失真。
    """
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=8))
    slot = GpuSlot(locks_dir=tmp_path, config=_config(timeout=0))
    daytime = datetime(2026, 9, 19, 12, 0, tzinfo=ZoneInfo(DEFAULT_WINDOW_TZ))

    with pytest.raises(GpuQueueTimeoutError):
        slot.acquire("closed", now=daytime)

    before = datetime.now(UTC)
    record = slot.acquire("opened", ignore_window=True)
    after = datetime.now(UTC)
    slot.release("opened")

    assert record.event == "acquired"
    assert before <= record.ts <= after, "越窗取锁的时间戳必须是真实时钟，不是窗口起点"
    assert record.ts.date() != daytime.date() or record.ts.hour != daytime.hour


def test_configured_window_changes_slot_behavior(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: the same time is outside one configured window and inside another.
    monkeypatch.setattr(gpu_slot, "query_vram", lambda: VramReading(total_gb=8, free_gb=8))
    now = datetime(2026, 9, 19, 21, 30, tzinfo=ZoneInfo(DEFAULT_WINDOW_TZ))
    closed = GpuSlot(locks_dir=tmp_path, config=_config(timeout=0))
    # When: both configurations attempt acquisition.
    with pytest.raises(GpuQueueTimeoutError):
        closed.acquire("closed", now=now)
    opened = GpuSlot(
        locks_dir=tmp_path,
        config=GpuSlotConfig(
            vram_limit_gb=1, window_start="20:00", window_end="06:30", queue_timeout_s=0
        ),
    )
    # Then: only the configured open window acquires.
    assert opened.acquire("opened", now=now).event == "acquired"
    opened.release("opened", now=now)


@pytest.mark.parametrize(
    ("url", "client", "action"),
    [
        (None, None, "not_needed"),
        (
            "http://kronos",
            _FakeClient(service_present=False, connection_refused=True),
            "not_needed",
        ),
        (
            "http://kronos",
            _FakeClient(service_present=True, connection_refused=True),
            "fail_closed",
        ),
    ],
)
def test_control_plane_presence_decision(url: str | None, client, action: str) -> None:
    # Given: a configured control URL and deployment-presence observation.
    # When: status is requested or absence is established.
    outcome = offload_kronos(control_url=url, contract_version="1", client=client)
    # Then: only an absent manifest entry may continue after refusal.
    assert outcome.action == action


@pytest.mark.parametrize(
    ("status", "health", "threshold", "reading", "action", "before"),
    [
        ((404, {}), (200, {"device": "cpu"}), 0.5, None, "not_needed", None),
        (
            (200, {"error": "E_UNSUPPORTED_VERSION"}),
            (200, {"device": "cpu"}),
            0.5,
            None,
            "not_needed",
            None,
        ),
        ((404, {}), (503, {}), 0.5, None, "fail_closed", None),
        (
            (404, {}),
            (200, {"device": "cuda"}),
            1.0,
            VramReading(total_gb=8, free_gb=7.5),
            "not_needed",
            0.5,
        ),
    ],
)
def test_endpoint_absence_fallback_decision(
    status: Response,
    health: Response,
    threshold: float,
    reading: VramReading | None,
    action: str,
    before: float | None,
) -> None:
    # Given: an absent lifecycle endpoint and parameterized fallback observations.
    client = _FakeClient(statuses=(status,), health=health, idle_threshold_gb=threshold)
    # When: health and device memory are probed.
    outcome = offload_kronos(
        control_url="http://kronos",
        contract_version="1",
        client=client,
        vram_reader=lambda: reading,
    )
    # Then: the architecture decision-table outcome and reading are preserved.
    assert outcome.action == action
    assert outcome.reason == "endpoint_absent_no_gpu_tenant"
    assert outcome.vram_before_gb == before


def test_empty_process_list_never_overrides_memory_at_threshold() -> None:
    # Given: no process-list API exists, while memory.used equals the configured threshold.
    client = _FakeClient(
        statuses=((404, {}),), health=(200, {"device": "cuda"}), idle_threshold_gb=1
    )
    # When: fallback uses only device memory.
    outcome = offload_kronos(
        control_url="http://kronos",
        contract_version="1",
        client=client,
        vram_reader=lambda: VramReading(total_gb=8, free_gb=7),
    )
    # Then: equality fails closed with the mandated reason and reading.
    assert outcome.action == "fail_closed"
    assert outcome.reason == "endpoint_absent_no_gpu_tenant"
    assert outcome.vram_before_gb == 1


@pytest.mark.parametrize(
    ("client", "action", "before"),
    [
        (_FakeClient(statuses=(_status(device="cpu", vram_bytes=0),)), "not_needed", 0),
        (_FakeClient(statuses=(_status(),), stop=(409, {"error": "E_BUSY"})), "fail_closed", 3),
        (_FakeClient(statuses=(_status(),), stop=(504, {"error": "E_TIMEOUT"})), "fail_closed", 3),
    ],
)
def test_status_and_stop_decision(client: _FakeClient, action: str, before: float) -> None:
    # Given: status or stop yields one explicit lifecycle decision row.
    # When: offload is attempted.
    outcome = offload_kronos(control_url="http://kronos", contract_version="1", client=client)
    # Then: CPU is not needed and either stop error fails closed with its reading.
    assert outcome.action == action
    assert outcome.vram_before_gb == before


def test_success_confirms_vram_release_via_status() -> None:
    # Given: a running service stops and a second status reports lower VRAM.
    client = _FakeClient(
        statuses=(_status(), _status(state="stopped", vram_bytes=250_000_000)),
        stop=(200, {"state": "stopped", "vram_bytes": 250_000_000}),
    )
    # When: offload completes.
    outcome = offload_kronos(control_url="http://kronos", contract_version="1", client=client)
    # Then: success is reported only after the confirming status reading fell.
    assert outcome == KronosOffloadOutcome(
        action="stopped", reason="vram_released", vram_before_gb=3, vram_after_gb=0.25
    )
