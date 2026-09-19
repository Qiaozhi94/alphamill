"""experiment_store 异常契约（F007 design §4/§7）。

`SnapshotInputError` 对应稳定错误码 `E_INPUT_INVALID`：输入不可解析、或不满足声明用途
（成员缺失/版本 invalid/覆盖不足/保真度不足/canonical 请求 latest）——一律 fail-closed，
不降级为警告（ADR-0003）。
"""


class SnapshotError(Exception):
    """ResearchSnapshot 领域异常基类。"""


class SnapshotInputError(SnapshotError):
    """输入不可解析或不满足声明用途；映射到稳定错误码 `E_INPUT_INVALID`。"""


class SnapshotNotFoundError(SnapshotError):
    """按 snapshot_id 找不到已发布快照。"""


class SnapshotIntegrityError(SnapshotError):
    """已发布快照内容与身份/摘要不符，或同 ID 不同内容（篡改、截断、覆盖尝试）。"""
