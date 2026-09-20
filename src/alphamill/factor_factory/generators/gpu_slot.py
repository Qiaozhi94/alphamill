"""GPU slot arbitration and Kronos offload coordination for F003."""

from __future__ import annotations

import fcntl
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TextIO
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from alphamill.factor_factory.errors import FactorFactoryError
from alphamill.factor_factory.generators.kronos_offload import (
    CLIENT_DEADLINE_MARGIN_S,
    RESTORE_TIMEOUT_S,
    STATUS_TIMEOUT_S,
    STOP_TIMEOUT_S,
    KronosOffloadOutcome,
    client_deadline,
    offload_kronos,
    restore_kronos,
)
from alphamill.factor_factory.generators.vram import VramReading, query_vram, vram_is_sufficient

DEFAULT_WINDOW_TZ = "Asia/Shanghai"


@dataclass(frozen=True, kw_only=True)
class GpuSlotConfig:
    vram_limit_gb: float
    window_start: str
    window_end: str
    # 架构 §7.1 的时段表按**执行机本地时间**表述（行标签「工作日夜」「周末白天」本身
    # 就需要本地日历才能读）。时区随执行机走并经配置承载，迁移 qiaozhi-lab 时只改配置。
    window_tz: str = DEFAULT_WINDOW_TZ
    queue_timeout_s: int = 1800


def in_training_window(
    now: datetime, *, window_start: str, window_end: str, window_tz: str = DEFAULT_WINDOW_TZ
) -> bool:
    """Test an instant against the execution host's LOCAL training window.

    Storage stays UTC everywhere; only this comparison is zone-aware, because the
    architecture §7.1 schedule is written in the execution host's local time.
    """
    start = datetime.strptime(window_start, "%H:%M").time()
    end = datetime.strptime(window_end, "%H:%M").time()
    try:
        zone = ZoneInfo(window_tz)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise FactorFactoryError(f"unknown training window timezone: {window_tz!r}") from exc
    if now.tzinfo is None:
        raise FactorFactoryError("training window needs a timezone-aware instant")
    current = now.astimezone(zone).time()
    return start <= current < end if start <= end else current >= start or current < end


@dataclass(frozen=True, kw_only=True)
class QueueRecord:
    queue_seq: int
    run_id: str
    event: Literal["queued", "acquired", "released", "timeout"]
    ts: datetime
    vram_free_gb: float | None


class GpuQueueTimeoutError(FactorFactoryError):
    termination: Literal["queue_timeout"] = "queue_timeout"

    def __init__(self, *, record: QueueRecord) -> None:
        self.record = record
        super().__init__(f"GPU queue timed out for run {record.run_id}")


class GpuSlot:
    def __init__(self, *, locks_dir: Path, config: GpuSlotConfig) -> None:
        locks_dir.mkdir(parents=True, exist_ok=True)
        self._slot_path = locks_dir / "gpu.slot"
        self._queue_path = locks_dir / "gpu.queue"
        self._config = config
        self._held: dict[str, int] = {}

    def acquire(
        self, run_id: str, *, now: datetime | None = None, ignore_window: bool = False
    ) -> QueueRecord:
        """Wait FIFO; insufficient **or unreadable** VRAM rejoins the tail.

        An unreadable probe is not evidence of a free card: on the execution host a
        failed ``nvidia-smi`` says nothing about who holds the 8GB. Architecture §7.1
        is explicit that the queue wins rather than gambling on OOM, so this path is
        fail-closed. CPU-only runs never reach here — the CLI takes no slot under
        ``--allow-cpu``.

        ``ignore_window`` is the explicit ``--allow-offhours`` escape hatch: it
        bypasses the schedule check only — never the VRAM probe, and never the
        clock that stamps queue records.
        """
        self._append(run_id, "queued", None, now)
        started = time.monotonic()
        while True:
            current = now if now is not None else datetime.now(UTC)
            window_open = ignore_window or in_training_window(
                current,
                window_start=self._config.window_start,
                window_end=self._config.window_end,
                window_tz=self._config.window_tz,
            )
            if window_open and self._waiting_head() == run_id:
                descriptor = os.open(self._slot_path, os.O_CREAT | os.O_RDWR, 0o644)
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    os.close(descriptor)
                else:
                    reading = query_vram()
                    free = None if reading is None else reading.free_gb
                    if vram_is_sufficient(reading, limit_gb=self._config.vram_limit_gb):
                        record = self._append(run_id, "acquired", free, now)
                        self._held[run_id] = descriptor
                        return record
                    try:
                        self._append(run_id, "released", free, now)
                    finally:
                        fcntl.flock(descriptor, fcntl.LOCK_UN)
                        os.close(descriptor)
                    self._append(run_id, "queued", free, now)
            elapsed = time.monotonic() - started
            if elapsed >= self._config.queue_timeout_s:
                record = self._append(run_id, "timeout", None, now)
                raise GpuQueueTimeoutError(record=record)
            time.sleep(min(0.01, self._config.queue_timeout_s - elapsed))

    def release(self, run_id: str, *, now: datetime | None = None) -> QueueRecord:
        try:
            descriptor = self._held.pop(run_id)
        except KeyError as exc:
            raise FactorFactoryError(f"run does not own GPU slot: {run_id}") from exc
        reading = query_vram()
        try:
            free = None if reading is None else reading.free_gb
            return self._append(run_id, "released", free, now)
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)

    def queue_records(self) -> list[QueueRecord]:
        with self._queue_path.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
            try:
                return self._read(stream)
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _append(
        self,
        run_id: str,
        event: Literal["queued", "acquired", "released", "timeout"],
        free: float | None,
        now: datetime | None,
    ) -> QueueRecord:
        with self._queue_path.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                records = self._read(stream)
                record = QueueRecord(
                    queue_seq=records[-1].queue_seq + 1 if records else 1,
                    run_id=run_id,
                    event=event,
                    ts=now if now is not None else datetime.now(UTC),
                    vram_free_gb=free,
                )
                payload = asdict(record)
                payload["ts"] = record.ts.isoformat()
                stream.seek(0, os.SEEK_END)
                stream.write(json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                return record
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _read(stream: TextIO) -> list[QueueRecord]:
        stream.seek(0)
        payloads = [json.loads(line) for line in stream if line.strip()]
        for payload in payloads:
            payload["ts"] = datetime.fromisoformat(payload["ts"])
        return [QueueRecord(**payload) for payload in payloads]

    def _waiting_head(self) -> str | None:
        latest = {record.run_id: record for record in self.queue_records()}
        waiting = [record for record in latest.values() if record.event == "queued"]
        return min(waiting, key=lambda record: record.queue_seq).run_id if waiting else None


__all__ = (
    "CLIENT_DEADLINE_MARGIN_S",
    "DEFAULT_WINDOW_TZ",
    "GpuQueueTimeoutError",
    "GpuSlot",
    "GpuSlotConfig",
    "RESTORE_TIMEOUT_S",
    "STATUS_TIMEOUT_S",
    "STOP_TIMEOUT_S",
    "KronosOffloadOutcome",
    "QueueRecord",
    "VramReading",
    "client_deadline",
    "in_training_window",
    "offload_kronos",
    "restore_kronos",
    "query_vram",
    "vram_is_sufficient",
)
