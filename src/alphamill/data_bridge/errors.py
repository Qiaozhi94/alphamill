"""F002 数据桥异常契约（design §4）。

取数与导出对以下任一情形一律抛错，不降级为警告（D4 数据红线；本 feature
无 SOP 所述的「安全校验降级声明」出口）。
"""


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
