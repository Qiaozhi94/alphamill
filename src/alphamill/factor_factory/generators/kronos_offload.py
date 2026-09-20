"""Kronos 生命周期控制面客户端：夜槽卸载与观测→处置决策表（架构 §7.1）。

与 GPU 单槽仲裁分开：这里只负责"能不能让 Kronos 交出显存"，取锁与排队归 gpu_slot。
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, TypeAlias
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from alphamill.factor_factory.generators.vram import VramReading, query_vram


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


# 架构 §7.1 的可配缺省：status 5s / stop 60s / restore 120s。三个动作共用单一超时会
# 把正常卸载误判成失败——卸载模型 + empty_cache 远超 status 的量级。
STATUS_TIMEOUT_S = 5.0
STOP_TIMEOUT_S = 60.0
RESTORE_TIMEOUT_S = 120.0


def offload_kronos(
    *,
    control_url: str | None,
    contract_version: str,
    service_deployed: bool = True,
    client=None,
    vram_reader: Callable[[], VramReading | None] = query_vram,
    status_timeout_s: float = STATUS_TIMEOUT_S,
    stop_timeout_s: float = STOP_TIMEOUT_S,
) -> KronosOffloadOutcome:
    """Stop a GPU Kronos tenant or fail closed according to architecture §7.1.

    A missing ``control_url`` is not evidence of absence. The decision table's
    "确未部署" row requires the deployment manifest to say so, which only the
    caller knows — hence ``service_deployed``. Defaulting it to True keeps a
    forgotten setting fail-closed instead of silently racing Kronos for the card.
    """
    if control_url is None:
        if service_deployed:
            return _outcome("fail_closed", "control_url_not_configured")
        return _outcome("not_needed", "service_not_deployed")
    requester = _http_request if client is None else client.request
    service_present = True if client is None else client.service_present
    idle_threshold_gb = None if client is None else client.idle_threshold_gb
    base_url = control_url.rstrip("/")

    def send(method: Literal["GET", "POST"], path: str) -> tuple[int, _Payload]:
        timeout = stop_timeout_s if path.endswith("/stop") else status_timeout_s
        return requester(method, f"{base_url}{path}", contract_version, timeout)

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


def restore_kronos(
    *,
    control_url: str | None,
    contract_version: str,
    client=None,
    timeout_s: float = RESTORE_TIMEOUT_S,
) -> bool:
    """训练窗口结束后恢复 Kronos 常驻推理；返回是否确认回到 running。

    停了不恢复等于白天 dry-run 一直拿不到实时信号（架构 §7.1 时段表只在夜槽卸载）。
    调用方在取锁失败、运行失败与正常结束三条路径上都必须走到这里。
    """
    if control_url is None:
        return False
    requester = _http_request if client is None else client.request
    try:
        status_code, payload = requester(
            "POST", f"{control_url.rstrip('/')}/lifecycle/restore", contract_version, timeout_s
        )
    except OSError:
        return False
    return status_code < 400 and "error" not in payload and payload.get("state") == "running"
