"""GPU slot arbitration and Kronos offload coordination for F003."""

from __future__ import annotations

import fcntl
import json
import os
import subprocess
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TextIO, TypeAlias
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from alphamill.factor_factory.errors import FactorFactoryError

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


@dataclass(frozen=True, kw_only=True)
class VramReading:
    total_gb: float
    free_gb: float


def query_vram() -> VramReading | None:
    """Read the first NVIDIA GPU without consulting process listings."""
    try:
        output = subprocess.run(
            (
                "nvidia-smi",
                "--query-gpu=memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ),
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        total, free = output.splitlines()[0].split(",", maxsplit=1)
        return VramReading(total_gb=float(total) / 1024, free_gb=float(free) / 1024)
    except (IndexError, OSError, subprocess.SubprocessError, ValueError):
        return None


def vram_is_sufficient(reading: VramReading | None, *, limit_gb: float) -> bool:
    return reading is not None and reading.free_gb >= limit_gb


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

    def acquire(self, run_id: str, *, now: datetime | None = None) -> QueueRecord:
        """Wait FIFO; insufficient **or unreadable** VRAM rejoins the tail.

        An unreadable probe is not evidence of a free card: on the execution host a
        failed ``nvidia-smi`` says nothing about who holds the 8GB. Architecture §7.1
        is explicit that the queue wins rather than gambling on OOM, so this path is
        fail-closed. CPU-only runs never reach here — the CLI takes no slot under
        ``--allow-cpu``.
        """
        self._append(run_id, "queued", None, now)
        started = time.monotonic()
        while True:
            current = now if now is not None else datetime.now(UTC)
            window_open = in_training_window(
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


@dataclass(frozen=True, kw_only=True)
class KronosOffloadOutcome:
    action: Literal["stopped", "not_needed", "fail_closed"]
    reason: str
    vram_before_gb: float | None
    vram_after_gb: float | None


_Payload: TypeAlias = dict[str, int | str | bool]
_Send: TypeAlias = Callable[[Literal["GET", "POST"], str], tuple[int, _Payload]]


def _http_request(
    method: Literal["GET", "POST"], url: str, contract_version: str, timeout_s: float
) -> tuple[int, _Payload]:
    request = Request(url, headers={"X-Contract-Version": contract_version}, method=method)
    try:
        response = urlopen(request, timeout=timeout_s)
    except HTTPError as exc:
        response = exc
    with response:
        status, content = response.status, response.read()
    try:
        decoded = json.loads(content) if content else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        decoded = {}
    if not isinstance(decoded, dict):
        return status, {}
    payload = {
        str(key): value for key, value in decoded.items() if isinstance(value, (bool, int, str))
    }
    return status, payload


def offload_kronos(
    *,
    control_url: str | None,
    contract_version: str,
    client=None,
    vram_reader: Callable[[], VramReading | None] = query_vram,
    timeout_s: float = 10.0,
) -> KronosOffloadOutcome:
    """Stop a GPU Kronos tenant or fail closed according to architecture §7.1."""
    if control_url is None:
        return _outcome("not_needed", "service_not_deployed")
    requester = _http_request if client is None else client.request
    service_present = True if client is None else client.service_present
    idle_threshold_gb = None if client is None else client.idle_threshold_gb
    base_url = control_url.rstrip("/")

    def send(method: Literal["GET", "POST"], path: str) -> tuple[int, _Payload]:
        return requester(method, f"{base_url}{path}", contract_version, timeout_s)

    try:
        status_code, status = send("GET", "/lifecycle/status")
    except OSError:
        action = "fail_closed" if service_present else "not_needed"
        return _outcome(action, "control_plane_unreachable")
    endpoint_absent = status_code == 404 or status.get("error") == "E_UNSUPPORTED_VERSION"
    if endpoint_absent or status.get("contract_version", contract_version) != contract_version:
        return _fallback_probe(send, idle_threshold_gb, vram_reader)
    before = _status_vram_gb(status)
    if status_code >= 400 or "error" in status:
        return _outcome("fail_closed", "status_failed", (before, None))
    if status.get("device") == "cpu":
        return _outcome("not_needed", "cpu_instance", (before, None))
    if status.get("state") == "stopped":
        return _outcome("not_needed", "already_stopped", (before, before))
    if status.get("state") != "running":
        return _outcome("fail_closed", "status_unknown", (before, None))
    try:
        stop_code, stopped = send("POST", "/lifecycle/stop")
        if stop_code >= 400 or "error" in stopped or stopped.get("state") != "stopped":
            return _outcome("fail_closed", "stop_failed", (before, None))
        confirm_code, confirmed = send("GET", "/lifecycle/status")
    except OSError:
        return _outcome("fail_closed", "control_plane_unreachable", (before, None))
    after = _status_vram_gb(confirmed)
    released = (
        confirm_code < 400
        and confirmed.get("state") == "stopped"
        and before is not None
        and after is not None
        and after < before
    )
    action = "stopped" if released else "fail_closed"
    return _outcome(action, "vram_released" if released else "vram_not_released", (before, after))


def _fallback_probe(
    send: _Send,
    idle_threshold_gb: float | None,
    vram_reader: Callable[[], VramReading | None],
) -> KronosOffloadOutcome:
    reason = "endpoint_absent_no_gpu_tenant"
    try:
        health_code, health = send("GET", "/health")
    except OSError:
        return _outcome("fail_closed", reason)
    if health_code >= 400 or health.get("device") not in {"cpu", "cuda"}:
        return _outcome("fail_closed", reason)
    if health.get("device") == "cpu":
        return _outcome("not_needed", reason)
    reading = vram_reader()
    if reading is None or idle_threshold_gb is None:
        return _outcome("fail_closed", reason)
    used_gb = max(0.0, reading.total_gb - reading.free_gb)
    action = "not_needed" if used_gb < idle_threshold_gb else "fail_closed"
    return _outcome(action, reason, (used_gb, None))


def _status_vram_gb(payload: _Payload) -> float | None:
    value = payload.get("vram_bytes")
    return value / 1_000_000_000 if type(value) is int else None


def _outcome(
    action: Literal["stopped", "not_needed", "fail_closed"],
    reason: str,
    readings: tuple[float | None, float | None] = (None, None),
) -> KronosOffloadOutcome:
    return KronosOffloadOutcome(
        action=action,
        reason=reason,
        vram_before_gb=readings[0],
        vram_after_gb=readings[1],
    )
