"""AlphaGen 特征 token 到湖通道名的绑定（F012 `FR-001`，文档检视 D02/D35）。

vendor 渲染出的特征 token 是 `feature:<basename>`（如 `feature:close`），湖面板列名是
`<dataset>.<column>@<resample>`（如 `ohlcv_1m.close@1h`）。映射规则与
`alphagen_runner.build_stock_data` 的 FeatureType 槽位同源：取列名最后一段、去掉 `@` 后缀、小写。
绑定后的 token 进入 FactorDef 身份，因此 `definition_digest` 天然携带数据集与重采样身份。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from alphamill.factor_factory.errors import ChannelConflictError, MissingChannelError

_FEATURE_PREFIX = "feature:"


def basename(channel: str) -> str:
    """`ohlcv_1m.close@1h` → `close`（与 build_stock_data 的槽位判定逐字相同）。"""
    return channel.split(".")[-1].split("@")[0].lower()


def channel_index(feature_map: Mapping[str, int]) -> dict[str, str]:
    """basename → 湖通道名；同名 basename 出现多次即 `ChannelConflictError`。"""
    index: dict[str, str] = {}
    for channel in feature_map:
        name = basename(channel)
        if name in index:
            raise ChannelConflictError(
                f"feature basename {name!r} is ambiguous: {index[name]!r} vs {channel!r}"
            )
        index[name] = channel
    return index


def bind_feature_tokens(tokens: Sequence[str], channels: Mapping[str, str]) -> tuple[str, ...]:
    """把 `feature:<basename>` 改写为 `feature:<湖通道名>`；无对应通道即 `MissingChannelError`。"""
    bound: list[str] = []
    for token in tokens:
        if not token.startswith(_FEATURE_PREFIX):
            bound.append(token)
            continue
        name = token[len(_FEATURE_PREFIX) :].lower()
        if name not in channels:
            raise MissingChannelError(f"missing_channel:{name}")
        bound.append(f"{_FEATURE_PREFIX}{channels[name]}")
    return tuple(bound)
