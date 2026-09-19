"""F003 可复现性契约（NFR-003）。

可复现的断言是**候选集合相等**——相同 `(seed, binding, code_digest, config_digest)`
重跑得到相同的 `factor_id` 集合与相同协同池成员；**不承诺逐位数值相同**（CPU/GPU
差异允许影响浮点末位）。本模块只提供身份与派生原语，不产任何评测结论。
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

from alphamill.factor_factory import canonical
from alphamill.factor_factory.errors import SchemaValidationError
from alphamill.factor_factory.factor import FactorDef

DEFAULT_TORCH_SEED = 0


def _load_torch() -> object | None:
    """可注入的 torch 载入缝：未安装 mining extra 时返回 None，而不是让导入失败。"""
    try:
        import torch
    except ImportError:
        return None
    return torch


def derive_seed(seed: int, *components: str) -> int:
    """由主 seed 与组件名稳定派生子种子，绝不读取全局 random 状态。"""
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise SchemaValidationError("seed 必须是整数")
    payload: canonical.JSONValue = [seed, *components]
    digest = hashlib.sha256(canonical.canonical_json_bytes(payload)).digest()
    return int.from_bytes(digest[:8], "big")


@dataclass(frozen=True, kw_only=True)
class RunIdentity:
    """一次运行的重现身份四元组。"""

    seed: int
    binding_digest: str
    config_digest: str
    code_digest: str

    @property
    def identity_digest(self) -> str:
        return canonical.sha256_prefixed_bytes(
            canonical.canonical_json_bytes(
                {
                    "seed": self.seed,
                    "binding_digest": self.binding_digest,
                    "config_digest": self.config_digest,
                    "code_digest": self.code_digest,
                }
            )
        )


def canonical_run_id(
    *,
    generator: str,
    seed: int,
    binding_digest: str,
    config_digest: str,
    code_digest: str,
    now: datetime | None = None,
) -> str:
    """由身份四元组推出确定性的 run_id，且必然是单一安全路径分量。"""
    if not generator or any(ch not in "abcdefghijklmnopqrstuvwxyz0123456789_-" for ch in generator):
        raise SchemaValidationError(f"generator 不能用于路径分量: {generator!r}")
    identity = RunIdentity(
        seed=seed,
        binding_digest=binding_digest,
        config_digest=config_digest,
        code_digest=code_digest,
    )
    stamp = (now or datetime.now(UTC)).astimezone(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{generator}-{stamp}-{identity.identity_digest.removeprefix('sha256:')[:12]}"


@contextmanager
def torch_determinism(*, enabled: bool = True) -> Iterator[None]:
    """训练期开启 torch 确定性开关，退出时恢复先前 RNG 与确定性设置。"""
    if not enabled:
        yield
        return
    torch = _load_torch()
    if torch is None:
        yield
        return

    cpu_state = torch.random.get_rng_state()
    cuda_states = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
    previous_determinism = torch.are_deterministic_algorithms_enabled()
    try:
        torch.manual_seed(DEFAULT_TORCH_SEED)
        torch.use_deterministic_algorithms(True, warn_only=True)
        yield
    finally:
        torch.random.set_rng_state(cpu_state)
        if cuda_states is not None:
            torch.cuda.set_rng_state_all(cuda_states)
        torch.use_deterministic_algorithms(previous_determinism)


def factor_id_set(factors: Iterable[FactorDef]) -> frozenset[str]:
    """候选集合的相等性原语：比较 factor_id 集合，而非数值逐位相等。"""
    return frozenset(factor.factor_id for factor in factors)


def pool_member_set(pool: FactorDef) -> frozenset[str]:
    """协同池成员集合的相等性原语。"""
    members = pool.params.get("members")
    if not isinstance(members, list):
        raise SchemaValidationError("pool.params['members'] 必须是列表")
    ids: list[str] = []
    for entry in members:
        if not isinstance(entry, dict) or not isinstance(entry.get("factor_id"), str):
            raise SchemaValidationError("pool 成员必须含 string 类型的 factor_id")
        ids.append(str(entry["factor_id"]))
    return frozenset(ids)
