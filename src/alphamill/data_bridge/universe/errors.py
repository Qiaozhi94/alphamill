"""F008 宇宙扩容的异常契约（design §4/§7）。

每条拒绝路径都带稳定错误码 `code`：CLI 以非零退出并把 code 写到 stderr，
测试据此断言「各自可区分的原因」（AC-012），而不是匹配自然语言报错。
`code` 一经发布不得改动语义（只允许新增）。
"""

from __future__ import annotations

from alphamill.data_bridge.errors import DataBridgeError


class UniverseError(DataBridgeError):
    """宇宙扩容子系统异常基类。"""

    code = "E_UNIVERSE"


class CriteriaError(UniverseError):
    """筛选口径缺失、字段非法或出现未知键。"""

    code = "E_UNIVERSE_CRITERIA"


class ExchangeUnreachableError(UniverseError):
    """交易所行情不可达/不可解析（启动期拒绝，不做降级猜测）。"""

    code = "E_UNIVERSE_EXCHANGE_UNREACHABLE"


class ConfirmRequiredError(UniverseError):
    """`freeze` 缺少人工确认开关（`--confirm`）：冻结必须显式确认。"""

    code = "E_UNIVERSE_CONFIRM_REQUIRED"


class EmptyDefinitionError(UniverseError):
    """候选清单为空：空宇宙不得冻结，也不得驱动回填。"""

    code = "E_UNIVERSE_EMPTY_CANDIDATES"


class UniverseNotFoundError(UniverseError):
    """指定 universe_id 的定义或 digest artifact 不存在。"""

    code = "E_UNIVERSE_NOT_FOUND"


class UniverseNotFrozenError(UniverseError):
    """定义尚未人工确认冻结，不得驱动回填/门禁等长跑任务。"""

    code = "E_UNIVERSE_NOT_FROZEN"


class UniverseAlreadyFrozenError(UniverseError):
    """同一 universe_id 已冻结，冻结记录不可原地改写。"""

    code = "E_UNIVERSE_ALREADY_FROZEN"


class UniverseAmbiguousError(UniverseError):
    """默认解析遇到多种 `(exchange, market_type)` 口径：拒绝串线，要求显式指定（F011）。"""

    code = "E_UNIVERSE_AMBIGUOUS"


class UniverseLookaheadError(UniverseError):
    """显式指定的宇宙版本在窗口终点时尚未生效（`frozen_at`/`snapshot_at` 晚于 at，F011）。"""

    code = "E_UNIVERSE_LOOKAHEAD"


class UniverseArtifactError(UniverseError):
    """台账 artifact 非法：schema_version 不符、未知键、digest 不符或非 canonical。"""

    code = "E_UNIVERSE_ARTIFACT"


class MembershipError(UniverseError):
    """台账写入被拒：区间重叠、原地改写历史区间或必填字段缺失。"""

    code = "E_UNIVERSE_MEMBERSHIP"


class QualityGateError(UniverseError):
    """质量门判定失败或判定记录非法。"""

    code = "E_UNIVERSE_QUALITY_GATE"


class BackfillIncompleteError(UniverseError):
    """回填未完成就想跑门禁：判 INCOMPLETE，不判 PASS（design §7）。"""

    code = "E_UNIVERSE_BACKFILL_INCOMPLETE"


class WindowError(UniverseError):
    """回填/导出窗口非法（起点不早于终点、非整分钟等）。"""

    code = "E_UNIVERSE_WINDOW"


class InsufficientDiskError(UniverseError):
    """执行机磁盘余量不足以覆盖本批预估写入量（启动期拒绝）。"""

    code = "E_UNIVERSE_DISK"


class RateLimitExhaustedError(UniverseError):
    """限流退避重试超上限：该 pair 标 failed 并保留断点，never 提速。"""

    code = "E_UNIVERSE_RATE_LIMIT"

    def __init__(self, *args: object, attempts: int = 1) -> None:
        super().__init__(*args)
        #: 真实尝试次数（首次 + 退避重试）——`backfill.failed.retries` 的唯一来源。
        self.attempts = attempts
