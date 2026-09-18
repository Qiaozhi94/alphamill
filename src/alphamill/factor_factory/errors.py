"""F003 因子工厂的共享类型化错误。

CLI 依此区分「可拒绝」(BindingValidationError / SchemaValidationError)
与「运行失败」(其余)。
"""

from __future__ import annotations


class FactorFactoryError(Exception):
    """因子工厂所有错误的基类。"""


class SchemaValidationError(FactorFactoryError):
    """产物 schema 非法。"""


class UnknownSchemaVersionError(SchemaValidationError):
    """schema_version 不在已知集合内；禁止做兼容性猜测。"""


class ConclusionFieldError(SchemaValidationError):
    """生成结果携带了评测结论字段（AI 权限红线，AC-001）。"""


class UnknownHypothesisError(SchemaValidationError):
    """引用了 catalog 中不存在的 hypothesis_id。"""


class CompilerNotRegisteredError(FactorFactoryError):
    """该 generator 没有注册表达式编译器（fail-closed，不静默回退）。"""


class FactorCompilationError(FactorFactoryError):
    """表达式无法编译为 compute。"""


class FactorDependencyError(FactorCompilationError):
    """编译所需依赖不可得，如 pool 缺少成员解析器。"""


class FeatureMapIntegrityError(FactorFactoryError):
    """feature_map 缺失、digest 不符或通道编号非法。"""


class FactorStoreError(FactorFactoryError):
    """FactorDef 产物读写失败或同路径内容冲突。"""


class BindingValidationError(FactorFactoryError):
    """快照绑定缺失、字段非法或 value_digest 不符，启动期拒绝。"""


class SnapshotResolverUnavailableError(BindingValidationError):
    """snapshot 形态绑定需要解析器但未提供。"""


class RunStoreError(FactorFactoryError):
    """运行 manifest / 事件写入失败。"""


class BoundaryGuardError(FactorFactoryError):
    """护栏安装或自检失败；调用方必须拒绝启动。"""


class EgressDeniedError(BoundaryGuardError):
    """进程级 egress 护栏拦截了一次出网尝试。"""


class WriteDeniedError(BoundaryGuardError):
    """写路径白名单拒绝了 runs 目录之外的写入。"""
