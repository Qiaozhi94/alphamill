"""生命周期控制面的 wire 层（F009 FR-005 / IR-001..IR-004）。

这里只做四件事：版本协商、请求体形态校验、调用控制器、序列化成契约信封。
状态判断一律在 `lifecycle.LifecycleController` 里（design §2 职责划分）。

错误一律 **HTTP 200 + 恰为单键** `{"error": "E_*"}`：契约测试只认信封，非 2xx 可能被
中间件或代理改写成错误页而丢掉 `error` 字段，届时客户端会把它误判成"端点不存在"。

控制器调用一律经 `run_in_threadpool`：控制器是同步阻塞实现（动作等待自己的 deadline、
status 可能跑 nvidia-smi 子进程），直接在事件循环里调用会把整个服务串行化——届时
单飞的 `E_BUSY` 永远观测不到（冲突请求根本没被处理），`status` 也不再是"动作进行中
可达"（F009 T022 执行机实测：1.2s 的 restore 期间并发 stop 被受理、status 报
operation=null）。
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from .lifecycle import (
    ACTION_FAILURE_CODE,
    CONTRACT_VERSION,
    CONTRACT_VERSION_HEADER,
    E_BAD_REQUEST,
    E_UNSUPPORTED_VERSION,
    LifecycleController,
    LifecycleError,
)


def _envelope(code: str) -> JSONResponse:
    return JSONResponse(status_code=200, content={"error": code})


def _version_ok(request: Request) -> bool:
    """头缺失**不**按默认版本放行（FR-005）。"""
    return request.headers.get(CONTRACT_VERSION_HEADER) == CONTRACT_VERSION


async def _body_ok(request: Request) -> bool:
    """`stop`/`restore` 只接受空体或 `{}`；其他形态一律 E_BAD_REQUEST。"""
    raw = (await request.body()).strip()
    if not raw:
        return True
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return parsed == {}


def build_lifecycle_router(controller: LifecycleController) -> APIRouter:
    router = APIRouter(prefix="/lifecycle", tags=["lifecycle"])

    @router.get("/status")
    async def status(request: Request):
        if not _version_ok(request):
            return _envelope(E_UNSUPPORTED_VERSION)
        return await run_in_threadpool(controller.status)

    async def _action(request: Request, run, action: str) -> JSONResponse | dict:
        # 顺序固定：版本协商 → 请求体形态 → 动作。E_UNSUPPORTED_VERSION 是客户端判定
        # "服务端未实现本契约"的入口，不得被请求体校验复用（架构 §7.1）。
        if not _version_ok(request):
            return _envelope(E_UNSUPPORTED_VERSION)
        if not await _body_ok(request):
            return _envelope(E_BAD_REQUEST)
        try:
            return await run_in_threadpool(run)
        except LifecycleError as exc:
            return _envelope(exc.code)
        except Exception:
            # 最后一道兜底（R2-002）：逐个路径堵漏堵不完，而无 `error` 字段的 500 会被
            # 客户端读成"端点不存在"并转入回落探测。任何未预期异常都按端点映射成该
            # 动作的失败码——控制器侧已负责把状态收敛到稳定态。
            return _envelope(ACTION_FAILURE_CODE[action])

    @router.post("/stop")
    async def stop(request: Request):
        return await _action(request, controller.stop, "stop")

    @router.post("/restore")
    async def restore(request: Request):
        return await _action(request, controller.restore, "restore")

    return router
