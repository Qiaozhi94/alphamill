"""F008 限速与指数退避（T012，`FR-003` / `NFR-001` / `AC-004`）。

速率预算是**整条回填流水线共享**的资源，不是每个 pair 一份——多个 pair 必须复用同一个
`RateLimiter` 实例（design §5：「pair 间可有限并发（受限速预算约束）」），因此同一个实例上
任意两次请求的间隔都不小于 `RateLimitPolicy.min_interval_seconds`。

AC-004 的核心不变量是「失败绝不提速」：

- 每次尝试（首次与重试）之前都先 `acquire()`，重试同样消耗速率预算；
- 退避等待（`base * 2**(attempt-1)`，封顶 `max_backoff_seconds`）**叠加**在速率预算之上
  而不是替换它——失败只会把请求推后，不会让后续请求提前；
- 尝试次数用尽即抛 `RateLimitExhaustedError`（`from exc` 保留因果链），由 T013 编排把该
  pair 标 failed 并保留 `last_cursor`，不静默提速、不跳过。

`clock` / `sleep` 可注入：生产用 `time.monotonic` / `time.sleep`，测试注入假时钟推进虚拟
时间，不真 sleep。

`call()` 的可重试判定由 `is_rate_limit_error()` 给出，**只重试限流/风控类异常**；其余异常
（参数错、解析错、数据错）原样抛出——重试它们只会浪费配额并掩盖真实故障。判定按异常**类名**
（含 MRO，子类同样命中）与消息特征（`429` / `rate limit` / `too many request` / `banned`）
进行，**不 import ccxt**：本模块不应被某个 ccxt 版本的导入顺序或依赖可用性绑死。

`max_retries` 的语义是**总尝试次数上限（含首次尝试）**：`1` 表示只试一次、不重试。AC-004 的
验收口径是「尝试次数恰好等于 `max_retries`」，故不采用「首次之外再额外重试 N 次」的读法；
默认 5 ⇒ 最多 4 次退避重试。

线程安全：本类按**单写者**假设使用（T013 的编排在单线程里调用 `acquire()` / `call()`）；
跨 pair 共享同一实例即可获得全局预算，无需额外加锁。
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

from alphamill.data_bridge.universe.errors import RateLimitExhaustedError, UniverseError

T = TypeVar("T")

#: 按类名匹配的 ccxt 限流/风控异常（子类经 MRO 同样命中）。不把
#: `ExchangeNotAvailable` / `OnMaintenance` 算进来：那是可用性问题而非配额问题。
RATE_LIMIT_ERROR_CLASS_NAMES = frozenset({"RateLimitExceeded", "DDoSProtection", "RequestTimeout"})

#: 消息特征（比较前统一小写）：交易所常把配额信息写在文本里，而异常类型是泛化的。
RATE_LIMIT_MESSAGE_MARKERS = ("429", "rate limit", "too many request", "banned")


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    """限速与退避参数；默认值取保守侧。"""

    #: 同一 limiter 上任意两次请求之间的最小间隔（秒）。Binance USDⓈ-M 权重上限
    #: 2400/min（≈40 请求/秒）；OHLCV 分页单请求权重 1–10，0.5s ⇒ ≤120 请求/分钟，
    #: 给 pair 内并发与权重抖动留出余量。
    min_interval_seconds: float = 0.5
    #: 总尝试次数上限（含首次尝试）：1 = 只试一次、不重试。
    max_retries: int = 5
    #: 首次失败后的退避时长，此后逐次翻倍。
    base_backoff_seconds: float = 1.0
    #: 单次退避上限：429/418 的惩罚窗口以分钟计，但封顶 60s 避免单个 pair 静默等过久。
    max_backoff_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.min_interval_seconds < 0:
            raise UniverseError("RateLimitPolicy: min_interval_seconds 不得为负")
        if self.max_retries < 1:
            raise UniverseError("RateLimitPolicy: max_retries 是总尝试次数上限，必须 ≥ 1")
        if self.base_backoff_seconds < 0:
            raise UniverseError("RateLimitPolicy: base_backoff_seconds 不得为负")
        if self.max_backoff_seconds < self.base_backoff_seconds:
            raise UniverseError(
                "RateLimitPolicy: max_backoff_seconds 不得小于 base_backoff_seconds"
            )

    def backoff_seconds(self, attempt: int) -> float:
        """第 `attempt` 次尝试失败后的退避时长：`base * 2**(attempt-1)`，封顶。"""
        if attempt < 1:
            raise UniverseError("RateLimitPolicy.backoff_seconds: attempt 从 1 起算")
        return min(self.base_backoff_seconds * 2 ** (attempt - 1), self.max_backoff_seconds)


class RateLimiter:
    """pair 间共享的速率预算，外加限流异常的指数退避重试（`AC-004`）。"""

    def __init__(
        self,
        policy: RateLimitPolicy,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._policy = policy
        self._clock = clock
        self._sleep = sleep
        # 下一次请求最早可发起的时刻；None = 尚未发出过请求。
        self._next_allowed_at: float | None = None
        #: 累计等待秒数（速率预算 + 退避），供长跑观测与「累计等待单调不减」断言。
        self.total_wait_seconds = 0.0

    @property
    def policy(self) -> RateLimitPolicy:
        """本实例使用的限速策略（退避参数由 `BackfillRun` 落盘）。"""
        return self._policy

    def acquire(self) -> float:
        """占用一个请求名额：必要时 sleep，返回本次等待秒数（无需等待时为 0.0）。"""
        now = self._clock()
        if self._next_allowed_at is None or now >= self._next_allowed_at:
            self._next_allowed_at = now + self._policy.min_interval_seconds
            return 0.0
        wait = self._next_allowed_at - now
        self._wait(wait)
        self._next_allowed_at += self._policy.min_interval_seconds
        return wait

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """acquire 后执行 `func`；限流异常按指数退避重试，超上限抛异常。

        非限流异常不重试，原样抛出；退避重试用尽后抛 `RateLimitExhaustedError`，
        最后一次限流异常挂在 `__cause__` 上（`from exc` 保留因果链）。
        """
        attempts = self._policy.max_retries
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            self.acquire()
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                if not is_rate_limit_error(exc):
                    raise
                last_exc = exc
                if attempt < attempts:
                    self._wait(self._policy.backoff_seconds(attempt))
        raise RateLimitExhaustedError(
            f"限流退避重试超上限（max_retries={attempts}，最后一次："
            f"{type(last_exc).__name__}: {last_exc}）"
        ) from last_exc

    def _wait(self, seconds: float) -> None:
        """唯一等待出口：sleep 由外部注入，等待时长计入累计观测值。"""
        self._sleep(seconds)
        self.total_wait_seconds += seconds


def is_rate_limit_error(exc: BaseException) -> bool:
    """异常是否属于限流/风控（即 `call()` 可重试的那一类）。

    先按类名（遍历 MRO，因此 ccxt 异常的子类同样命中），再按消息特征——两者都
    不 import ccxt，避免把判定绑死在 ccxt 的导入路径与版本上。
    """
    if any(cls.__name__ in RATE_LIMIT_ERROR_CLASS_NAMES for cls in type(exc).__mro__):
        return True
    message = str(exc).lower()
    return any(marker in message for marker in RATE_LIMIT_MESSAGE_MARKERS)
