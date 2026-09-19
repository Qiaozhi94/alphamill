"""T012 / AC-004：pair 间共享速率预算、限流指数退避与「失败绝不提速」。

全部断言落在**虚拟时间**上：`RateLimiter` 的 `clock` / `sleep` 就是为此而设的注入点，
`FakeClock` 只推进虚拟时间并记录每次等待，本套件一次真实 sleep 都不会发生。

覆盖映射（`spec.md` AC-004 / `design.md` §5）：

1. 共享预算——两个 pair 交替用同一实例，相邻请求间隔 ≥ `min_interval_seconds`；
2. 限流退避——等待按 `base * 2**(attempt-1)` 递增并在 `max_backoff_seconds` 封顶，
   尝试次数恰好 `max_retries`，超限抛 `RateLimitExhaustedError` 且保留因果链；
3. 非限流异常不重试；
4. 失败不提速——退避重试后紧随的请求仍满足 `min_interval_seconds`，累计等待单调不减；
5. `is_rate_limit_error` 的正反例（类名路径、消息路径、普通异常）；
6. 成功时原样返回被调函数的返回值（args/kwargs 透传、对象同一性）。
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest

from alphamill.data_bridge.universe import rate_limit
from alphamill.data_bridge.universe.errors import RateLimitExhaustedError, UniverseError
from alphamill.data_bridge.universe.rate_limit import (
    RateLimiter,
    RateLimitPolicy,
    is_rate_limit_error,
)


class FakeClock:
    """虚拟时钟 + 睡眠记录器：`sleep` 只推进虚拟时间并记账。"""

    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        assert seconds >= 0, f"sleep 时长不得为负：{seconds}"
        self.sleeps.append(seconds)
        self.now += seconds

    @property
    def total_slept(self) -> float:
        return sum(self.sleeps)


class RateLimitExceeded(Exception):
    """模拟 `ccxt.RateLimitExceeded`：消息里没有任何特征词，只能靠类名识别。"""


class DDoSProtection(Exception):
    """模拟 `ccxt.DDoSProtection`。"""


class RequestTimeout(Exception):
    """模拟 `ccxt.RequestTimeout`。"""


def _limiter(**overrides: Any) -> tuple[RateLimiter, FakeClock]:
    """构造挂在假时钟上的 limiter；`overrides` 直接透传给 `RateLimitPolicy`。"""
    clock = FakeClock()
    policy = RateLimitPolicy(**overrides)
    return RateLimiter(policy, clock=clock.monotonic, sleep=clock.sleep), clock


# --------------------------------------------------------------------------- #
# 1. pair 间共享的速率预算
# --------------------------------------------------------------------------- #


def test_shared_budget_spaces_requests_across_pairs() -> None:
    """两个「pair」交替调用**同一个** limiter：相邻请求的虚拟时间差 ≥ min_interval。"""
    min_interval = 10.0
    limiter, clock = _limiter(min_interval_seconds=min_interval)
    pairs = ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BTC-USDT", "ETH-USDT", "SOL-USDT"]
    events: list[tuple[str, float]] = []

    def request(pair: str) -> str:
        events.append((pair, clock.now))
        return pair

    for pair in pairs:
        assert limiter.call(request, pair) == pair

    assert [pair for pair, _ in events] == pairs
    stamps = [stamp for _, stamp in events]
    deltas = [later - earlier for earlier, later in zip(stamps, stamps[1:], strict=True)]
    assert all(delta >= min_interval for delta in deltas), deltas
    # 共享预算 = 只有一个名额序列：5 次等待、每次恰好一个 min_interval。
    assert clock.sleeps == [min_interval] * (len(pairs) - 1)
    assert limiter.total_wait_seconds == pytest.approx(clock.total_slept)


def test_acquire_returns_wait_seconds_and_paces_slots() -> None:
    """`acquire()` 返回本次等待秒数：首次为 0，紧接着的第二次等满一个间隔。"""
    min_interval = 5.0
    limiter, clock = _limiter(min_interval_seconds=min_interval)

    assert limiter.acquire() == 0.0
    assert limiter.acquire() == min_interval
    assert clock.now == min_interval
    assert clock.sleeps == [min_interval]
    assert limiter.total_wait_seconds == min_interval


# --------------------------------------------------------------------------- #
# 2. 限流退避：指数递增、封顶、尝试次数上限
# --------------------------------------------------------------------------- #


def test_backoff_grows_exponentially_caps_and_then_exhausts() -> None:
    """连续限流：等待递增到封顶、尝试次数恰好 max_retries、最后抛错并保留因果链。"""
    # min_interval=0 把速率预算的等待隔离掉，clock.sleeps 里剩下的全是退避等待。
    policy = RateLimitPolicy(
        min_interval_seconds=0.0,
        max_retries=5,
        base_backoff_seconds=4.0,
        max_backoff_seconds=10.0,
    )
    clock = FakeClock()
    limiter = RateLimiter(policy, clock=clock.monotonic, sleep=clock.sleep)
    failures: list[RateLimitExceeded] = []

    def always_limited() -> None:
        exc = RateLimitExceeded(f"HTTP 429 boom #{len(failures) + 1}")
        failures.append(exc)
        raise exc

    with pytest.raises(RateLimitExhaustedError) as excinfo:
        limiter.call(always_limited)

    assert len(failures) == policy.max_retries  # 尝试次数恰好等于 max_retries
    expected = [policy.backoff_seconds(attempt) for attempt in range(1, policy.max_retries)]
    assert expected == [4.0, 8.0, 10.0, 10.0]  # base*2**(n-1)，到顶后保持封顶值
    assert expected[0] < expected[1] < expected[2]  # 封顶之前严格递增
    assert max(expected) == policy.max_backoff_seconds  # 封顶确实被触发
    assert clock.sleeps == expected  # 等待序列逐次只增不减
    assert clock.now == sum(expected)
    assert excinfo.value.__cause__ is failures[-1]  # `from exc` 保留因果链
    assert f"max_retries={policy.max_retries}" in str(excinfo.value)


def test_single_attempt_policy_does_not_retry() -> None:
    """`max_retries=1` 是「只试一次」的边界：不重试、不退避，直接判超限。"""
    limiter, clock = _limiter(min_interval_seconds=0.0, max_retries=1, base_backoff_seconds=2.0)
    calls = 0

    def always_limited() -> None:
        nonlocal calls
        calls += 1
        raise DDoSProtection("too many requests")

    with pytest.raises(RateLimitExhaustedError):
        limiter.call(always_limited)

    assert calls == 1
    assert clock.sleeps == []


# --------------------------------------------------------------------------- #
# 3. 非限流异常不重试
# --------------------------------------------------------------------------- #


def test_non_rate_limit_error_is_not_retried() -> None:
    """参数/数据类故障重试只会浪费配额：调用次数 = 1，原样抛出。"""
    limiter, clock = _limiter(min_interval_seconds=0.0, max_retries=5, base_backoff_seconds=1.0)
    calls = 0

    def boom() -> None:
        nonlocal calls
        calls += 1
        raise ValueError("unknown symbol BTC-XXX")

    with pytest.raises(ValueError, match="unknown symbol BTC-XXX"):
        limiter.call(boom)

    assert calls == 1
    assert clock.sleeps == []
    assert limiter.total_wait_seconds == 0.0


# --------------------------------------------------------------------------- #
# 4. 失败绝不提速
# --------------------------------------------------------------------------- #


def test_failure_does_not_speed_up_following_requests() -> None:
    """一次限流失败重试后，紧随的成功请求仍满足 min_interval，累计等待单调不减。"""
    min_interval = 2.0
    policy = RateLimitPolicy(
        min_interval_seconds=min_interval,
        max_retries=3,
        base_backoff_seconds=1.0,
        max_backoff_seconds=8.0,
    )
    clock = FakeClock()
    limiter = RateLimiter(policy, clock=clock.monotonic, sleep=clock.sleep)
    attempts = 0
    stamps: list[float] = []
    cumulative: list[float] = []

    def flaky(limit_failures: int) -> str:
        nonlocal attempts
        attempts += 1
        stamps.append(clock.now)
        if attempts <= limit_failures:
            raise RateLimitExceeded("binance: rate limit exceeded")
        return "ok"

    def record_ok() -> str:
        stamps.append(clock.now)
        return "ok"

    assert limiter.call(flaky, 1) == "ok"  # 首次失败 → 退避 → 重试成功
    cumulative.append(limiter.total_wait_seconds)
    assert limiter.call(record_ok) == "ok"  # 紧随其后的成功请求
    cumulative.append(limiter.total_wait_seconds)

    assert attempts == 2
    assert stamps == [0.0, min_interval, 2 * min_interval]
    # 退避叠加在速率预算之上，而不是替换它：1.0 退避 + 1.0 补足间隔 + 2.0 正常间隔。
    assert clock.sleeps == [1.0, 1.0, 2.0]
    deltas = [later - earlier for earlier, later in zip(stamps, stamps[1:], strict=True)]
    assert all(delta >= min_interval for delta in deltas), deltas
    assert cumulative == sorted(cumulative)  # 累计等待单调不减
    assert limiter.total_wait_seconds == pytest.approx(sum(clock.sleeps))


# --------------------------------------------------------------------------- #
# 5. is_rate_limit_error 正反例
# --------------------------------------------------------------------------- #


def test_is_rate_limit_error_matches_ccxt_class_names() -> None:
    """ccxt 限流/风控类：消息里没有特征词，只能按类名（含 MRO 子类）命中。"""
    assert is_rate_limit_error(RateLimitExceeded("boom")) is True
    assert is_rate_limit_error(DDoSProtection("boom")) is True
    assert is_rate_limit_error(RequestTimeout("boom")) is True

    class BinanceRateLimitExceeded(RateLimitExceeded):
        """交易所自定义子类：按 MRO 类名同样命中。"""

    assert is_rate_limit_error(BinanceRateLimitExceeded("boom")) is True


def test_is_rate_limit_error_matches_message_markers() -> None:
    """泛化异常类型 + 带配额信息的消息（含普通异常的 429）判为限流。"""
    assert is_rate_limit_error(ValueError("HTTP 429 Too Many Requests")) is True
    assert is_rate_limit_error(RuntimeError("binance: RATE LIMIT exceeded")) is True
    assert is_rate_limit_error(Exception("too many requests for endpoint")) is True
    assert is_rate_limit_error(Exception("IP banned until 1700000000000")) is True
    for marker in rate_limit.RATE_LIMIT_MESSAGE_MARKERS:
        assert is_rate_limit_error(Exception(f"prefix {marker.upper()} suffix")) is True


def test_is_rate_limit_error_rejects_other_failures() -> None:
    """非限流异常不得命中：否则 `call()` 会对数据/参数故障做无谓重试。"""
    assert is_rate_limit_error(ValueError("unknown symbol BTC-XXX")) is False
    assert is_rate_limit_error(KeyError("rows")) is False
    assert is_rate_limit_error(UniverseError("定义未冻结")) is False
    assert is_rate_limit_error(TimeoutError("connection reset by peer")) is False
    assert is_rate_limit_error(ConnectionError("dns failure")) is False


def test_is_rate_limit_error_covers_real_ccxt_classes() -> None:
    """装了 ccxt 时对**真实**异常类再验一遍：不想当然地认为自己认得出。"""
    ccxt = pytest.importorskip("ccxt")
    for name in sorted(rate_limit.RATE_LIMIT_ERROR_CLASS_NAMES):
        assert is_rate_limit_error(getattr(ccxt, name)("boom")) is True, name
    assert is_rate_limit_error(ccxt.BadSymbol("BTC-XXX")) is False


def test_module_detects_ccxt_errors_without_importing_ccxt() -> None:
    """判定不依赖 ccxt 导入顺序：模块自身不得 import ccxt（静态契约）。"""
    tree = ast.parse(Path(rate_limit.__file__).read_text(encoding="utf-8"))
    roots = {
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert "ccxt" not in roots


# --------------------------------------------------------------------------- #
# 6. 返回值与策略默认值
# --------------------------------------------------------------------------- #


def test_success_returns_original_return_value() -> None:
    """成功后原样返回被调函数的返回值，args/kwargs 透传。"""
    limiter, _ = _limiter(min_interval_seconds=1.0)

    def compute(a: int, b: int, *, scale: int = 1) -> dict[str, int]:
        return {"value": (a + b) * scale}

    assert limiter.call(compute, 1, 2, scale=3) == {"value": 9}
    sentinel = object()
    assert limiter.call(lambda: sentinel) is sentinel


def test_default_policy_is_conservative() -> None:
    """默认值在保守侧：非零间隔、有上限的重试、封顶不小于基数。"""
    policy = RateLimitPolicy()
    assert policy.min_interval_seconds > 0
    assert policy.max_retries >= 1
    assert 0 < policy.base_backoff_seconds <= policy.max_backoff_seconds


@pytest.mark.parametrize(
    "overrides",
    [
        {"min_interval_seconds": -1.0},
        {"max_retries": 0},
        {"base_backoff_seconds": -1.0},
        {"base_backoff_seconds": 10.0, "max_backoff_seconds": 1.0},
    ],
)
def test_invalid_policy_is_rejected(overrides: dict[str, Any]) -> None:
    """非法策略在构造期即拒绝（`max_retries=0` 在「总尝试次数」语义下无意义）。"""
    with pytest.raises(UniverseError):
        RateLimitPolicy(**overrides)
