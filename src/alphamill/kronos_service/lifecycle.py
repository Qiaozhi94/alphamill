"""Kronos 生命周期控制面（F009）。

控制器是控制面的**唯一写入口**：持有期望态 `desired` 与进行中动作 `operation`，
保证同一时刻至多一个动作在执行。它**不存 `state`**——每次从
`(desired, signal.status().loaded)` 派生，避免第二份真相源（design §2/§5）。

三条硬语义（架构 §7.1）：
1. `desired=stopped` 期间推理端点不得隐式加载模型——`allow_load()` 是该准入的开关；
2. `E_TIMEOUT` 表示"动作仍在进行"，服务端不中断后台动作；最终落点由 `operation` 转
   `null` 表达，迟到完成补写 `result=late_complete` 日志行；
3. 返回任何错误信封之前，`operation` 已清空且 `(desired, model_loaded)` 已落在稳定态。
"""

from __future__ import annotations

import contextlib
import threading
import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass
from datetime import UTC, datetime

from . import vram
from .lifecycle_config import LifecycleConfig

CONTRACT_VERSION = "1"
CONTRACT_VERSION_HEADER = "X-Contract-Version"

E_UNSUPPORTED_VERSION = "E_UNSUPPORTED_VERSION"
E_BAD_REQUEST = "E_BAD_REQUEST"
E_BUSY = "E_BUSY"
E_TIMEOUT = "E_TIMEOUT"
E_UNLOAD_FAILED = "E_UNLOAD_FAILED"
E_UNAVAILABLE = "E_UNAVAILABLE"

#: 契约允许的全部错误码（IR-004）：实现不得发明新码
ERROR_CODES = (
    E_UNSUPPORTED_VERSION,
    E_BAD_REQUEST,
    E_BUSY,
    E_TIMEOUT,
    E_UNLOAD_FAILED,
    E_UNAVAILABLE,
)

#: 每个动作的失败码（架构 §7.1 错误码表）：未预期异常也必须映射到这里，
#: 否则异常会以 HTTP 500 漏出去，而客户端把无 `error` 字段的响应读成"端点不存在"。
ACTION_FAILURE_CODE = {"stop": E_UNLOAD_FAILED, "restore": E_UNAVAILABLE}

RUNNING = "running"
STOPPED = "stopped"
TRANSITIONAL = "transitional"


class LifecycleError(Exception):
    """控制面错误：`code` 即 wire 上的单键错误信封内容。"""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


class UnloadFailed(RuntimeError):
    """卸载失败。`discarded` 表示模型引用是否已丢弃——它决定失败落点（design §5 表）。"""

    def __init__(self, message: str, *, discarded: bool):
        super().__init__(message)
        self.discarded = discarded


@dataclass(frozen=True)
class Operation:
    id: str
    action: str
    started_at: str

    def as_dict(self) -> dict:
        return {"id": self.id, "action": self.action, "started_at": self.started_at}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class LifecycleController:
    def __init__(
        self,
        signal,
        config: LifecycleConfig,
        *,
        emit=print,
        clock=time.monotonic,
    ):
        self._signal = signal
        self._config = config
        self._emit = emit
        self._clock = clock
        self._desired = RUNNING
        self._operation: Operation | None = None
        self._meta_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="kronos-lifecycle")
        self._current: Future | None = None
        # 主线程放弃等待的动作 id：后台完成时据此补写 late_complete 收尾行（TR-002）
        self._timed_out: set[str] = set()

    # --- 派生态 -------------------------------------------------------------

    def _state(self, desired: str, loaded: bool) -> str:
        if desired == RUNNING and loaded:
            return RUNNING
        if desired == STOPPED and not loaded:
            return STOPPED
        return TRANSITIONAL

    def allow_load(self) -> bool:
        """推理准入：`desired=stopped` 期间禁止隐式加载（FR-003）。"""
        with self._meta_lock:
            return self._desired == RUNNING

    def status(self) -> dict:
        """只读查询：自带服务端 deadline，不进单飞执行器（动作进行中照样可达）。"""
        deadline = self._clock() + self._config.status_timeout_s
        with self._meta_lock:
            desired, operation = self._desired, self._operation
        model_status = self._signal.status()
        reading = self._probe(model_status.device, budget_s=deadline - self._clock())
        return {
            "state": self._state(desired, bool(model_status.loaded)),
            "desired": desired,
            "contract_version": CONTRACT_VERSION,
            "model_loaded": bool(model_status.loaded),
            "vram_bytes": reading.used_bytes,
            "vram_readable": reading.readable,
            "device": model_status.device,
            "operation": operation.as_dict() if operation else None,
        }

    def _probe(self, device: str, budget_s: float) -> vram.VramReading:
        """探测显存；**任何异常都按读数不可得处理**。

        控制面的可达性不依赖探测成功（AC-001 / §5 不变量）：探测抛错就把它记成
        `vram_readable=false`，而不是让 status 变成 500——后者会让编排分不清
        "读数缺失"与"控制面故障"，而这两件事的处置完全不同。
        """
        try:
            return vram.probe(
                device=device,
                mode=self._config.probe_mode,
                probe_timeout_s=self._config.probe_timeout_s,
                budget_s=budget_s,
            )
        except Exception:
            return vram.VramReading(used_bytes=None, readable=False, source="unavailable")

    def _vram_reading(self, device: str) -> vram.VramReading:
        return self._probe(device, budget_s=self._config.probe_timeout_s)

    # --- 动作 ---------------------------------------------------------------

    def stop(self) -> dict:
        return self._run_action("stop", STOPPED, self._config.stop_timeout_s)

    def restore(self) -> dict:
        return self._run_action("restore", RUNNING, self._config.restore_timeout_s)

    def _run_action(self, action: str, desired: str, timeout_s: float) -> dict:
        """受理 → 置 desired → 后台执行 → 按 deadline 等待（design §5）。

        受理判定（单飞）排在显存探测**之前**：FR-006 要求冲突动作"立即"返回
        `E_BUSY`，而探测可能卡到 `KRONOS_VRAM_PROBE_TIMEOUT_S`（FR-007 明说要防的
        情形）。被拒的动作不该触碰设备，否则编排的重试节奏被探测延迟带偏。
        """
        started = self._clock()
        model_status = self._signal.status()

        with self._meta_lock:
            if self._operation is not None:
                raise LifecycleError(E_BUSY)  # 不排队、不叠加
            operation = Operation(uuid.uuid4().hex[:8], action, _now_iso())
            state_before = self._state(self._desired, bool(model_status.loaded))
            self._desired = desired
            self._operation = operation

        # 已受理之后才读基线显存：这一步只服务日志行，不参与受理判定。
        vram_before = self._vram_reading(getattr(model_status, "device", "") or "")

        worker = self._stop_worker if action == "stop" else self._restore_worker
        future = self._executor.submit(
            self._execute, worker, operation, state_before, vram_before, started
        )
        self._current = future
        try:
            return future.result(timeout=timeout_s)
        except FutureTimeout:
            # 不中断后台动作：中断会留下半加载态（NFR-004）。operation 保持非空，
            # 后台完成时按同一 operation_id 补写 late_complete 收尾行。
            with self._meta_lock:
                if self._operation is not None:
                    # 仅在动作确实还在飞时登记迟到：动作恰在 deadline 边缘完成时
                    # 无条件登记会把 id 永久留在集合里（R1-003）。
                    self._timed_out.add(operation.id)
            raise LifecycleError(E_TIMEOUT) from None

    def _execute(
        self,
        worker,
        operation: Operation,
        state_before: str,
        vram_before: vram.VramReading,
        started: float,
    ) -> dict:
        result = ACTION_FAILURE_CODE[operation.action]  # 兜底：finally 的日志行必须有值
        try:
            payload, result = worker()
            return payload
        except LifecycleError as exc:
            result = exc.code
            raise
        except Exception as exc:
            # 兜底网：worker 自己的 try 之外仍可能抛。异常必须按动作映射成契约码，
            # 并把期望态收敛成**稳定**态——否则响应漏成 HTTP 500 或状态停在过渡态
            # （违反"返回错误前已落稳定态"，architecture §7.1 失败落点）。
            self._converge_after_failure(operation.action)
            result = ACTION_FAILURE_CODE[operation.action]
            raise LifecycleError(result) from exc
        finally:
            elapsed_ms = int((self._clock() - started) * 1000)
            with self._meta_lock:
                self._operation = None
                desired_now = self._desired
                late = operation.id in self._timed_out
                self._timed_out.discard(operation.id)
            # 观测不得掩盖动作结果：状态读取、探测与写日志任一抛错都只丢这行日志，
            # 不改变本次动作要抛出/返回的东西（否则原始异常被 finally 顶替，事后归因断线）。
            try:
                model_status = self._signal.status()
                state_after = self._state(desired_now, bool(model_status.loaded))
                vram_after = self._vram_reading(getattr(model_status, "device", "") or "")
                self._log(
                    operation=operation,
                    result="late_complete" if late else result,
                    state_before=state_before,
                    state_after=state_after,
                    desired=desired_now,
                    vram_before=vram_before,
                    vram_after=vram_after,
                    elapsed_ms=elapsed_ms,
                )
            except Exception as exc:  # pragma: no cover - 观测降级路径
                print(f"[kronos-lifecycle] log emit failed for {operation.id}: {exc}")

    def _converge_after_failure(self, action: str) -> None:
        """按**事实**把 desired 收敛到稳定态：以"模型是否还在内存里"为准。

        读不到就取 fail-closed 的一侧——**不得声称已卸载**：谎称 stopped 会让夜槽
        据此取锁训练，而模型可能还占着显存（OOM）；反向误报最多让编排白等一轮，
        随后的 `restore` 幂等无副作用。
        """
        try:
            loaded = bool(self._signal.status().loaded)
        except Exception:
            loaded = action == "stop"
        with self._meta_lock:
            self._desired = RUNNING if loaded else STOPPED

    # --- 动作实现 -----------------------------------------------------------

    def _stop_worker(self) -> tuple[dict, str]:
        try:
            self._signal.unload()
        except UnloadFailed as exc:
            if not exc.discarded:
                # 什么都没动 → 回到原状最诚实（design §5 表第一行）
                with self._meta_lock:
                    self._desired = RUNNING
            raise LifecycleError(E_UNLOAD_FAILED) from exc
        except Exception as exc:  # 卸载尚未开始就失败，等同"未丢引用"
            with self._meta_lock:
                self._desired = RUNNING
            raise LifecycleError(E_UNLOAD_FAILED) from exc
        # 卸载已成功（不可逆）。此后只是**报告**：读设备名或读显存失败不改变这个事实，
        # 更不得谎报 E_UNLOAD_FAILED——那会让编排以为显存还占着而白等一晚
        # （代码检视 R2-001：该路径此前会回落 desired=running 并停在 transitional）。
        try:
            device = self._signal.status().device
            vram_bytes = self._vram_reading(device).used_bytes
        except Exception:
            vram_bytes = None
        return {"state": STOPPED, "vram_bytes": vram_bytes}, "ok"

    def _restore_worker(self) -> tuple[dict, str]:
        try:
            self._signal.eager_load()
        except Exception as exc:
            # 加载失败：desired 回落 stopped，否则实例停在"期望 running 但加载不上"的
            # 过渡态里，state 落不回稳定态（design §5）。进程不退出。
            with self._meta_lock:
                self._desired = STOPPED
            raise LifecycleError(E_UNAVAILABLE) from exc
        return {"state": RUNNING}, "ok"

    # --- 观测 ---------------------------------------------------------------

    def _log(self, **fields) -> None:
        operation: Operation = fields.pop("operation")
        parts = [
            f"action={operation.action}",
            f"operation_id={operation.id}",
            f"result={fields['result']}",
            f"state_before={fields['state_before']}",
            f"state_after={fields['state_after']}",
            f"desired={fields['desired']}",
            f"vram_bytes_before={fields['vram_before'].used_bytes}",
            f"vram_bytes_after={fields['vram_after'].used_bytes}",
            f"vram_readable={fields['vram_after'].readable}",
            f"contract_version={CONTRACT_VERSION}",
            f"elapsed_ms={fields['elapsed_ms']}",
        ]
        self._emit(" ".join(parts))

    # --- 非契约辅助（不经 wire 层暴露） ------------------------------------

    def wait_idle(self, timeout: float | None = None) -> None:
        """等待在飞动作真正结束。**不是契约的一部分**，wire 层不暴露它。

        存在理由：`E_TIMEOUT` 之后动作仍在后台跑，测试与进程收尾需要一个确定的
        汇合点，否则只能轮询 `status().operation` 睡眠等待（既慢又易 flaky）。
        客户端侧的等价手段仍是轮询 `operation` 转 `null`（FR-006），不要把这个
        方法当成可依赖的外部接口。
        """
        future = self._current
        if future is not None:
            with contextlib.suppress(Exception):
                future.result(timeout=timeout)
