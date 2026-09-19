"""F003 挖掘运行的依赖与 CUDA 能力自检。"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Final, Protocol, runtime_checkable

from alphamill.factor_factory.errors import MiningCapabilityError

MINING_REQUIRED_MODULES: Final[tuple[str, ...]] = (
    "torch",
    "numpy",
    "stable_baselines3",
    "gymnasium",
)


@runtime_checkable
class _CudaCapability(Protocol):
    def is_available(self) -> bool: ...


@runtime_checkable
class _TorchCapability(Protocol):
    cuda: _CudaCapability


def require_mining_capabilities(*, require_cuda: bool) -> None:
    """缺少 mining 模块或请求的 CUDA 能力时 fail-closed 拒绝运行。"""
    loaded_modules: dict[str, ModuleType] = {}
    missing_modules: list[str] = []
    for module_name in MINING_REQUIRED_MODULES:
        try:
            loaded_modules[module_name] = import_module(module_name)
        except (ImportError, OSError):
            missing_modules.append(module_name)

    if missing_modules:
        missing = ", ".join(missing_modules)
        raise MiningCapabilityError(f"缺少 mining 模块: {missing}")
    if not require_cuda:
        return

    torch_module = loaded_modules["torch"]
    if not isinstance(torch_module, _TorchCapability) or not isinstance(
        torch_module.cuda, _CudaCapability
    ):
        raise MiningCapabilityError("缺少 mining 能力: torch.cuda.is_available")
    try:
        cuda_available = torch_module.cuda.is_available()
    except (OSError, RuntimeError) as exc:
        raise MiningCapabilityError("mining 能力检查失败: torch.cuda.is_available") from exc
    if not cuda_available:
        raise MiningCapabilityError("缺少 mining 能力: torch.cuda.is_available")
