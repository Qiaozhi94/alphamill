"""F003 挖掘能力自检测试：NFR-005 / T015 要求缺失能力 fail-closed。"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from types import ModuleType

import pytest

from alphamill.factor_factory import errors
from alphamill.factor_factory.generators import mining_capability

EXPECTED_REQUIRED_MODULES = ("torch", "numpy", "stable_baselines3", "gymnasium")


@dataclass(frozen=True, slots=True)
class _CudaAvailability:
    available: bool

    def is_available(self) -> bool:
        return self.available


class _TorchModule(ModuleType):
    cuda: _CudaAvailability

    def __init__(self, *, cuda_available: bool) -> None:
        super().__init__("torch")
        self.cuda = _CudaAvailability(cuda_available)


def _module_loader(
    *, missing: frozenset[str], cuda_available: bool = True
) -> Callable[[str], ModuleType]:
    modules = {name: ModuleType(name) for name in EXPECTED_REQUIRED_MODULES}
    modules["torch"] = _TorchModule(cuda_available=cuda_available)

    def _load(name: str) -> ModuleType:
        if name in missing:
            raise ModuleNotFoundError(name)
        return modules[name]

    return _load


def test_all_missing_modules_are_reported(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: none of the mining modules can be imported.
    monkeypatch.setattr(
        mining_capability,
        "import_module",
        _module_loader(missing=frozenset(EXPECTED_REQUIRED_MODULES)),
        raising=False,
    )

    # When: mining capabilities are required without a CUDA requirement.
    with pytest.raises(errors.FactorFactoryError) as exc_info:
        mining_capability.require_mining_capabilities(require_cuda=False)

    # Then: the typed failure names every required module.
    assert mining_capability.MINING_REQUIRED_MODULES == EXPECTED_REQUIRED_MODULES
    assert isinstance(exc_info.value, errors.MiningCapabilityError)
    assert all(name in str(exc_info.value) for name in EXPECTED_REQUIRED_MODULES)


def test_one_missing_module_is_named(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: only stable_baselines3 is unavailable.
    missing = "stable_baselines3"
    monkeypatch.setattr(
        mining_capability,
        "import_module",
        _module_loader(missing=frozenset({missing})),
        raising=False,
    )

    # When: mining capabilities are required.
    with pytest.raises(errors.FactorFactoryError) as exc_info:
        mining_capability.require_mining_capabilities(require_cuda=False)

    # Then: the typed failure identifies only the missing module.
    assert isinstance(exc_info.value, errors.MiningCapabilityError)
    assert missing in str(exc_info.value)
    assert all(
        name not in str(exc_info.value) for name in EXPECTED_REQUIRED_MODULES if name != missing
    )


def test_required_cuda_unavailable_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: all modules import, but torch reports that CUDA is unavailable.
    monkeypatch.setattr(
        mining_capability,
        "import_module",
        _module_loader(missing=frozenset(), cuda_available=False),
        raising=False,
    )

    # When: a CUDA mining run checks capabilities.
    with pytest.raises(errors.FactorFactoryError) as exc_info:
        mining_capability.require_mining_capabilities(require_cuda=True)

    # Then: the typed failure names the unavailable torch CUDA capability.
    assert isinstance(exc_info.value, errors.MiningCapabilityError)
    assert "torch.cuda.is_available" in str(exc_info.value)


def test_all_capabilities_available_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given: all modules import and fake torch reports CUDA available.
    monkeypatch.setattr(
        mining_capability,
        "import_module",
        _module_loader(missing=frozenset(), cuda_available=True),
        raising=False,
    )

    # When: a CUDA mining run checks capabilities.
    result = mining_capability.require_mining_capabilities(require_cuda=True)

    # Then: the check returns without degrading or raising.
    assert result is None
