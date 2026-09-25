"""F002 数据桥异常契约（design §4）。

取数与导出对以下任一情形一律抛错，不降级为警告（D4 数据红线；本 feature
无 SOP 所述的「安全校验降级声明」出口）。
"""

import contextlib


class DataBridgeError(Exception):
    """数据桥异常基类。"""


class UnknownDatasetError(DataBridgeError):
    """dataset 不在 registry 白名单中。"""


class VersionNotFoundError(DataBridgeError):
    """请求的 data_version manifest 不存在，或不存在任何 valid 版本。"""


class InvalidVersionError(DataBridgeError):
    """请求的 data_version 已被标记 invalid，消费端拒绝读取。"""


class ManifestIntegrityError(DataBridgeError):
    """manifest 清单内文件缺失、字节数或 sha256 不符，或 value_digest 缺失/重算不符。

    不含「目录里存在本版本未引用的文件」——`.rN` 共享模型下那是其他版本的
    合法分区，reader 根本不扫描目录。
    """


class FlaggedPartitionError(DataBridgeError):
    """查询命中带未解决质量旗的分区且未显式 allow_flagged=True。"""


class InsufficientAsOfFidelityError(DataBridgeError):
    """对 as_of_fidelity=event_time_only 的 dataset 传了 as_of 且未显式豁免。"""


class SymbolCollisionError(DataBridgeError):
    """两行 symbol 映射推导出相同 lake_pair——意味着两个标的写进同一湖分区。"""


class SymbolNotFoundError(DataBridgeError):
    """symbol_map 中找不到请求方向的映射条目。"""


class ReconcileFailedError(DataBridgeError):
    """导出后与源库对账不一致；对应 data_version 已标记 invalid。"""


def mark_attempts(exc: BaseException, attempts: int) -> None:
    """把**真实尝试次数**（首次 + 退避重试）挂到异常上，供编排层落 `backfill.failed.retries`。

    重试发生在 `RateLimiter.call` 内部，异常抛出时已看不到次数；不标注就只能填 `None`
    或假 0（F008 TR-002 的 retries 因此失义）。两条规则：

    - **首个标注者为准**（已标注则不覆盖）：`RateLimiter.call` 数的是真实请求次数，
      比 F001 抓取层外层的重试循环更贴近事实，外层不得把它改小；
    - 异常实现带 `__slots__` 挂不上时放弃标注，编排层回落缺省 1——观测手段不得改变
      失败路径本身。
    """
    if getattr(exc, "attempts", None) is not None:
        return
    with contextlib.suppress(AttributeError):  # pragma: no cover - 带 __slots__ 的异常挂不上
        exc.attempts = attempts  # type: ignore[attr-defined]


def attempts_of(exc: BaseException) -> int:
    """读回 `mark_attempts` 标注的尝试次数；无标注或类型异常一律回落 1。"""
    value = getattr(exc, "attempts", 1)
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        return 1
    return value
