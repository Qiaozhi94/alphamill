"""AlphaGen 候选的边训练边自检流水线（F012 `FR-002`/`FR-003`/`FR-004`，design §5）。

每个被 AlphaGen 评估的表达式立即走：绑定湖通道 → 纯度归属分类（unknown → lookahead）→ 编译 →
按 `definition_digest` 查重 → 在同一面板上算信号 → 掩掉 close 缺失/非正的 bar → 判退化 →
截面中位数仓位预筛 → 入册或拒绝。入册数达到配额即停止接受新候选（之后的调用不计 proposed）。

异常归属（design §7）：候选级缺陷一律转成拒绝码并写事件；编译器未组装、面板结构错误等系统级
问题直接抛出，由调用方把整次运行判为 failed——不把数据缺陷伪装成候选拒绝（ADR-0003）。
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd

from alphamill.factor_factory.errors import (
    FactorCompilationError,
    FeatureMapIntegrityError,
    SchemaValidationError,
)
from alphamill.factor_factory.factor import FactorDef
from alphamill.factor_factory.generators.base import GenerationCounts, RejectionCounts
from alphamill.factor_factory.generators.channel_binding import bind_feature_tokens, channel_index
from alphamill.factor_factory.generators.lake_tensor import TensorPanel
from alphamill.factor_factory.generators.objective import ObjectiveParams, evaluate_objective
from alphamill.factor_factory.generators.purity import check_expression
from alphamill.factor_factory.hypotheses.catalog import DEFAULT_CATALOG, MECHANISM_UNKNOWN_ID
from alphamill.factor_factory.registry import factor_store
from alphamill.factor_factory.registry.compiler_registry import CompilerRegistry
from alphamill.factor_factory.registry.event_writer import RunEventWriter

GENERATOR = "alphagen"
POSITION_RULE = "cs_median"
_UNIVERSE = "__in_universe__"


@dataclass(frozen=True)
class Registered:
    factor: FactorDef


@dataclass(frozen=True)
class Rejected:
    reason_code: str
    detail: str


class CandidatePipeline:
    """单次运行内的候选处理器；只接受 token，不依赖 AlphaGen 本身（可用纯 Python 驱动）。"""

    def __init__(
        self,
        *,
        panel: TensorPanel,
        objective_params: ObjectiveParams,
        run_id: str,
        writer: RunEventWriter,
        compilers: CompilerRegistry,
        quota: int,
        generator_version: str,
        created_at: datetime,
        on_quota: Callable[[], None] | None = None,
    ) -> None:
        if quota < 1:
            raise SchemaValidationError("quota must be at least one")
        self._panel = panel
        self._channels = channel_index(panel.feature_map)
        self._close = _close_column(panel)
        self._params = objective_params
        self._run_id = run_id
        self._writer = writer
        self._compilers = compilers
        self._quota = quota
        self._version = generator_version
        self._created_at = created_at
        self._on_quota = on_quota
        self._hypothesis = DEFAULT_CATALOG.require(MECHANISM_UNKNOWN_ID)
        self._seen: set[str] = set()
        self._proposed = 0
        self._rejected = {code: 0 for code in RejectionCounts.__dataclass_fields__}
        self.registered: list[FactorDef] = []
        self.stopped = False

    def offer(self, tokens: Sequence[str]) -> Registered | Rejected | None:
        if self.stopped:
            return None
        self._proposed += 1
        raw = tuple(tokens)
        try:
            bound = bind_feature_tokens(raw, self._channels)
        except FactorCompilationError as exc:  # MissingChannelError
            return self._reject(raw, "unregistered_op", str(exc))
        try:
            verdict = check_expression(
                bound,
                scope="cross_sectional",
                seen_definition_digests=frozenset(),
                definition_digest="",
            )
        except SchemaValidationError as exc:  # 畸形 token
            return self._reject(bound, "unregistered_op", f"malformed:{exc}")
        if not verdict.accepted:
            return self._reject(bound, verdict.reason_code or "unregistered_op", verdict.detail)
        try:
            factor = factor_store.build_factor(
                hypothesis=self._hypothesis,
                name=GENERATOR,
                generator=GENERATOR,
                generator_version=self._version,
                scope="cross_sectional",
                expression=bound,
                params={},
                feature_map=self._panel.feature_map,
                run_id=self._run_id,
                created_at=self._created_at,
                compilers=self._compilers,
            )
        except (FactorCompilationError, FeatureMapIntegrityError) as exc:
            return self._reject(bound, "unregistered_op", str(exc))
        digest = factor_store.factor_to_dto(factor).definition_digest
        if digest in self._seen:
            return self._reject(bound, "duplicate_definition", digest, digest=digest)
        self._seen.add(digest)
        return self._prefilter(factor, bound, digest)

    def counts(self) -> GenerationCounts:
        return GenerationCounts(
            proposed=self._proposed,
            rejected=RejectionCounts(**self._rejected),
            registered=len(self.registered),
        )

    def _prefilter(self, factor: FactorDef, bound: tuple[str, ...], digest: str):
        started = time.perf_counter()
        frame = self._panel.panel
        close = frame[self._close].astype(float)
        tradable = close.notna() & (close > 0.0) & np.isfinite(close)
        signal = factor.compute(frame).astype(float)
        masked = int((frame[_UNIVERSE].astype(bool) & signal.notna() & ~tradable).sum())
        signal = signal.where(tradable)
        live = signal.loc[frame[_UNIVERSE].astype(bool)].dropna()
        record = {"definition_digest": digest, "masked_bars": masked}
        if live.empty or not np.isfinite(live.to_numpy()).all():
            detail = "degenerate_signal:" + ("no_observation" if live.empty else "non_finite")
            self._log(record, "rejected", started)
            return self._reject(bound, "reachability", detail, digest=digest)
        work = pd.DataFrame({self._close: close, _UNIVERSE: frame[_UNIVERSE], "signal": signal})
        result = evaluate_objective(
            work, params=self._params, resample=self._panel.resample, position_rule=POSITION_RULE
        )
        record |= {
            "turnover": _finite(result.turnover),
            "trades_90d": result.trades_90d,
            "after_cost_return": _finite(result.after_cost_return),
        }
        if not result.accepted:
            self._log(record, "rejected", started)
            return self._reject(bound, "reachability", result.detail, digest=digest)
        self._log(record, "registered", started)
        self.registered.append(factor)
        if len(self.registered) >= self._quota:
            self.stopped = True
            if self._on_quota is not None:
                self._on_quota()
        return Registered(factor)

    def _log(self, record: dict, outcome: str, started: float) -> None:
        elapsed = round((time.perf_counter() - started) * 1000.0, 3)
        self._writer.prefilter(record | {"outcome": outcome, "elapsed_ms": elapsed})

    def _reject(self, tokens, code: str, detail: str, *, digest: str | None = None) -> Rejected:
        self._rejected[code] += 1
        self._writer.rejected(tokens, code, detail, definition_digest=digest)
        return Rejected(code, detail)


def _close_column(panel: TensorPanel) -> str:
    columns = [name for name in panel.feature_map if name.split(".")[-1].startswith("close@")]
    if len(columns) != 1:
        raise SchemaValidationError(f"tensor panel needs exactly one close channel: {columns!r}")
    return columns[0]


def _finite(value: float) -> float | None:
    return value if math.isfinite(value) else None
