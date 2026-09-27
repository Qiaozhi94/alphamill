"""挖掘 CLI 的生成器分发（F012 `FR-006`/`IR-001`，design §1 第 13 行）。

manual 与 alphagen 在 CLI 上的差异全部收在这里：run_id 前缀、config 合成、层级规则、
引擎与 objective 字段、宇宙汇总、张量准备与生成器构造。`cli.py` 只编排护栏链，不再写死 manual。

config 合成（检视 D13/D27/D44）：manual = `DEFAULT_MINE_CONFIG` + 用户 `--config`（与改动前一致，
`config_digest` 不变）；alphagen = MINE 公共段 + `DEFAULT_ALPHAGEN_CONFIG` + 用户 `--config`，
其中 `objective` 一层深合并。
"""

from __future__ import annotations

import json
import platform
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from pandas.tseries.frequencies import to_offset

from alphamill.factor_factory import canonical, errors
from alphamill.factor_factory.canonical import JSONValue
from alphamill.factor_factory.generators import base, binding, gpu_slot
from alphamill.factor_factory.generators.alphagen_context import (
    ALPHAGEN_GENERATOR_VERSION,
    BuildContext,
    objective_params,
)
from alphamill.factor_factory.generators.candidate_pipeline import POSITION_RULE
from alphamill.factor_factory.generators.channel_binding import channel_index
from alphamill.factor_factory.generators.lake_tensor import (
    TensorPanel,
    build_tensor,
    pairs_during,
    require_universe_members,
    universe_pair_count,
)
from alphamill.factor_factory.generators.manual import seeds as manual_seeds
from alphamill.factor_factory.generators.objective import funding_feature_columns
from alphamill.factor_factory.mine_config import DEFAULT_ALPHAGEN_CONFIG, DEFAULT_MINE_CONFIG
from alphamill.factor_factory.registry import run_store

_VENDOR_BASELINE: Final = (
    Path(__file__).parent / "generators/alphagen_vendor/_upstream_baseline.json"
)
_LEGACY_MANUAL_OBJECTIVE: Final = run_store.ObjectiveInfo(  # manual 无预筛，沿用改动前取值
    turnover_penalty_lambda=0.0,
    reachability_min_trades_90d=30,
    cost_model={},
    min_after_cost_return=0.0,
)


@dataclass(frozen=True, kw_only=True)
class GeneratorSpec:
    name: str
    tier_level: str
    needs_panel: bool
    tier_required_in_config: bool


SPECS: Final = {
    "manual": GeneratorSpec(
        name="manual", tier_level="manual", needs_panel=False, tier_required_in_config=True
    ),
    "alphagen": GeneratorSpec(
        name="alphagen", tier_level="L0", needs_panel=True, tier_required_in_config=False
    ),
}


def resolve(name: str) -> GeneratorSpec:
    return SPECS[name]


def compose_config(
    spec: GeneratorSpec,
    supplied: Mapping[str, JSONValue],
    *,
    mining: bool,
    quota: int,
    window: JSONValue,
) -> dict[str, JSONValue]:
    if spec.name == "manual":
        return {
            **(DEFAULT_MINE_CONFIG if mining else {}),
            **supplied,
            "generator": "manual",
            "quota": quota,
            "window": window,
        }
    objective = {**_mapping(DEFAULT_ALPHAGEN_CONFIG["objective"])}
    objective.update(_mapping(supplied.get("objective", {})))
    composed: dict[str, JSONValue] = {
        **DEFAULT_MINE_CONFIG,
        **DEFAULT_ALPHAGEN_CONFIG,
        **supplied,
        "objective": objective,
        "generator": spec.name,
        "quota": quota,
        "window": window,
    }
    try:  # 启动期（卸载 Kronos 之前）就把 objective 缺键/错型判成 invalid_config（检视 R-A2）
        objective_params(composed)
    except (KeyError, TypeError, ValueError) as exc:
        raise errors.SchemaValidationError(f"alphagen objective config invalid: {exc!r}") from exc
    if objective.get("position_rule") != POSITION_RULE:  # 预筛只实现 cs_median（Q-005，R-A3）
        raise errors.SchemaValidationError(f"position_rule must be {POSITION_RULE!r}")
    return composed


def build_generator(spec: GeneratorSpec, ctx: BuildContext) -> base.Generator:
    if spec.name == "manual":
        return manual_seeds.ManualGenerator(run_id=ctx.run_id)
    return _build_alphagen(ctx)


def _build_alphagen(ctx: BuildContext) -> base.Generator:
    from alphamill.factor_factory.generators.alphagen_generator import AlphaGenGenerator

    return AlphaGenGenerator(ctx)


def warm_training_runtime() -> None:
    """护栏外预热训练依赖（见 `alphagen_training.warm_runtime`）；惰性导入以免拉起 torch。"""
    from alphamill.factor_factory.generators.alphagen_training import warm_runtime

    warm_runtime()


def prepare_panel(
    validated: binding.ValidatedBinding,
    window: base.Window,
    config: Mapping[str, JSONValue],
    lake_root: Path | None,
) -> TensorPanel:
    """张量先于 Kronos 卸载与取 GPU 槽构建（检视 D21）；只读窗口内宇宙成员并集（D24）。"""
    datasets = config.get("datasets")
    resample = config.get("resample")
    if (
        not isinstance(datasets, list)
        or not datasets
        or not all(isinstance(d, str) for d in datasets)
    ):
        raise errors.SchemaValidationError("alphagen config datasets must be a non-empty list")
    if not isinstance(resample, str):
        raise errors.SchemaValidationError("alphagen config resample must be a string")
    to_offset(resample)  # 非法重采样 → ValueError → invalid_config
    missing = [dataset for dataset in datasets if dataset not in validated.resolved.members]
    if missing:
        raise errors.SchemaValidationError(f"datasets absent from binding: {missing!r}")
    try:
        panel = build_tensor(
            validated,
            datasets=datasets,
            resample=resample,
            # reader 取 [start, end) 开盘的 K 线，左闭右标签重采样后标签 ∈ (start, end]，
            # 且最后一根在 end（= cutoff）时收盘，不越绑定截止（检视 R-B4/R2-1）
            start=window.start,
            end=window.end,
            pairs=pairs_during(validated.universe_ledger, window.start, window.end),
            lake_root=lake_root,
        )
    except errors.SchemaValidationError as exc:  # 零行等湖内容问题 → invalid_binding
        raise errors.BindingValidationError(f"tensor build failed: {exc}") from exc
    require_universe_members(panel.panel)
    channel_index(panel.feature_map)  # ChannelConflictError → invalid_config
    funding_bps = objective_params(config).cost_model.funding_8h_bps
    if funding_bps > 0 and not funding_feature_columns(panel.feature_map, resample=resample):
        # 否则资金费被静默按 0 扣（检视 R2-3）
        raise errors.SchemaValidationError(
            "funding_8h_bps > 0 but the panel has no funding channel"
        )
    return panel


def universe_summary(
    spec: GeneratorSpec, validated: binding.ValidatedBinding, panel: TensorPanel | None
) -> run_store.UniverseSummary:
    if spec.needs_panel and panel is not None:
        pair_count = universe_pair_count(panel.panel)  # 窗口内曾在宇宙（FR-008）
    else:
        cutoff = validated.resolved.cutoff_time
        pair_count = len(validated.universe_ledger.universe_at(cutoff))
    return run_store.UniverseSummary(
        pair_count=pair_count,
        symbol_map_digest=validated.resolved.symbol_map_digest,
        universe_digest=validated.resolved.universe.digest,
        source=validated.source.mode,
    )


def engine_info(spec: GeneratorSpec) -> run_store.EngineInfo:
    dependencies = {"alphamill": "0.1.0", "python": platform.python_version()}
    if spec.name == "manual":
        identity = {"generator": "manual", "version": manual_seeds.MANUAL_GENERATOR_VERSION}
        vendor_commit = None
    else:
        vendor_commit = json.loads(_VENDOR_BASELINE.read_text(encoding="utf-8"))["commit"]
        identity = {
            "generator": spec.name,
            "version": ALPHAGEN_GENERATOR_VERSION,
            "vendor_commit": vendor_commit,
        }
    return run_store.EngineInfo(
        vendor_commit=vendor_commit,
        code_digest=canonical.sha256_prefixed_bytes(canonical.canonical_json_bytes(identity)),
        dependencies=dependencies,
    )


def objective_info(spec: GeneratorSpec, config: Mapping[str, JSONValue]) -> run_store.ObjectiveInfo:
    if spec.name == "manual":
        return _LEGACY_MANUAL_OBJECTIVE
    objective = _mapping(config["objective"])
    return run_store.ObjectiveInfo(
        turnover_penalty_lambda=float(objective["turnover_penalty_lambda"]),
        reachability_min_trades_90d=int(objective["reachability_min_trades_90d"]),
        cost_model=dict(_mapping(objective["cost_model"])),
        min_after_cost_return=float(objective["min_after_cost_return"]),
        position_rule=str(objective["position_rule"]),
    )


def slot_config(config: Mapping[str, JSONValue]) -> gpu_slot.GpuSlotConfig:
    return gpu_slot.GpuSlotConfig(
        vram_limit_gb=float(config["vram_limit_gb"]),
        window_start=str(config["training_window_start"]),
        window_end=str(config["training_window_end"]),
        window_tz=str(config["training_window_tz"]),
        queue_timeout_s=int(config["queue_timeout_s"]),
    )


def _mapping(value: object) -> Mapping[str, JSONValue]:
    if not isinstance(value, Mapping):
        raise errors.SchemaValidationError("config section must be a JSON object")
    return value
