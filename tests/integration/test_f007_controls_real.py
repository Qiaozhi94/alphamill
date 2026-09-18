"""T023 / `AC-001`·`AC-003`·`AC-004`·`AC-007`：执行机不可变快照上的四类控制真实环境取证。

**只在执行机运行**（SOP §3）：开发机默认 skip，开发机的 skip 不是证据。取证命令：

```text
ALPHAMILL_INTEGRATION=1 pytest -q \
  tests/integration/test_f007_controls_real.py --snapshot <snapshot-id>
```

与 `test_f007_controls.py` 的 fixture 控制**分属不同命令、不同数据来源**：本文件从快照绑定的真实
Parquet（经 F002 reader）派生 carry / 截面动量 / 白噪声 / 故意泄漏四类控制，绝不读
`tests/fixtures/f007/controls/`。证据落 `reports/f007/real_env/<run_id>/`，manifest 绑定
`snapshot_id` 与各成员 `value_digest`，并记录 hostname 与 `device=cpu`（开发机无 GPU）。

预注册方法配置（method-v1）是**注册事实**、不是控制夹具，因此复用它是正确的（否则门禁口径不可比）；
被禁止复用的是控制**数据**与取证**命令**。
"""

from __future__ import annotations

import json
import os
import platform
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pytest

from alphamill.data_bridge import reader
from alphamill.evaluation.pipeline import evaluate_fixture, first_failure
from alphamill.evaluation.run_config import load_run_config
from alphamill.experiment_store import research_snapshot as rs
from alphamill.validation.methodology_gate import GuardContext, evaluate_methodology

pytestmark = pytest.mark.integration

INTEGRATION_REQUIRED = os.getenv("ALPHAMILL_INTEGRATION", "").lower() in {"1", "true", "yes"}
REPO = Path(__file__).resolve().parents[2]
DEVICE = "cpu"
NOISE_SEED = 20260901
PRICE_DATASETS = ("ohlcv_1m", "ohlcv_5m", "ohlcv_15m", "ohlcv_1h", "ohlcv_4h", "ohlcv_1d")
FUNDING_DATASET = "derivatives_funding_rates"
LEAKAGE_EXPRESSION = "shift(close, -1) / close - 1"
MOMENTUM_EXPRESSION = "rank(close / delay(close, 24))"
CARRY_EXPRESSION = "-1 * signal"
NOISE_EXPRESSION = "signal"
EVIDENCE_SUBDIR = ("f007", "real_env")


@dataclass(frozen=True)
class Control:
    name: str
    signal: tuple[float, ...]
    label: tuple[float, ...]
    times: tuple[str, ...]
    expression: str
    expect_methodology_pass: bool


def _require_execution_environment(snapshot_id: str | None) -> str:
    if not INTEGRATION_REQUIRED:
        pytest.skip(
            "F007 T023 需在执行机取证：设 ALPHAMILL_INTEGRATION=1 并给 --snapshot <id>（SOP §3）"
        )
    if not snapshot_id:
        pytest.fail("ALPHAMILL_INTEGRATION=1 但未提供 --snapshot：真实环境证据不能以 skip 代替")
    return snapshot_id


def _emit(frame: pd.DataFrame, column: str, *, per_symbol: bool) -> tuple[tuple[Any, ...], ...]:
    ordered = frame.sort_values(["symbol", "time"] if per_symbol else ["time"], kind="stable")
    values: dict[str, list[float]] = {}
    for row in ordered.itertuples(index=False):
        values.setdefault(str(row.symbol), []).append(float(getattr(row, column)))
    return tuple(tuple(series) for series in values.values())


def _flatten(per_symbol: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    return tuple(value for series in per_symbol for value in series)


def _build_control_frames(snapshot, lake_root: Path) -> dict[str, pd.DataFrame]:
    """从快照绑定的真实数据派生四类控制；快照必须含价格与（carry 用）资金费数据集。"""
    members = snapshot.members
    price_dataset = next((name for name in PRICE_DATASETS if name in members), None)
    if price_dataset is None:
        pytest.fail(f"快照不含价格数据集（候选 {list(PRICE_DATASETS)}）: {sorted(members)}")
    cut = datetime.fromisoformat(snapshot.cutoff_time.replace("Z", "+00:00"))
    prices = reader.read(
        price_dataset,
        members[price_dataset].data_version,
        end=cut,
        lake_root=lake_root,
    ).frame
    if prices.empty:
        pytest.fail(f"{price_dataset} 在快照 cutoff 前无数据")
    prices = prices.sort_values(["symbol", "time"], kind="stable")
    prices["forward_return"] = prices.groupby("symbol", sort=False)["close"].pct_change().shift(-1)
    prices = prices.dropna(subset=["forward_return"])
    prices["momentum"] = prices.groupby("symbol", sort=False)["close"].pct_change(24)
    prices = prices.dropna(subset=["momentum"])
    frames = {"momentum": prices}
    if FUNDING_DATASET in members:
        funding = reader.read(
            FUNDING_DATASET,
            members[FUNDING_DATASET].data_version,
            end=cut,
            lake_root=lake_root,
        ).frame
        if not funding.empty:
            merged = pd.merge_asof(
                funding.sort_values("time")[["time", "symbol", "funding_rate"]],
                prices[["time", "symbol", "close", "forward_return"]].sort_values("time"),
                on="time",
                by="symbol",
                direction="backward",
            ).dropna(subset=["forward_return"])
            merged["signal"] = -merged["funding_rate"]
            frames["carry"] = merged
    return frames


def _noise_and_leakage(prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """白噪声与故意泄漏：固定 seed 的确定性伪随机 + 直接把未来收益当信号。"""
    ordered = prices.sort_values(["symbol", "time"], kind="stable").copy()
    generator = random.Random(NOISE_SEED)
    ordered["signal"] = [generator.uniform(-1.0, 1.0) for _ in range(len(ordered))]
    leakage = ordered.copy()
    leakage["signal"] = leakage["forward_return"]
    return {"noise": ordered, "leakage": leakage}


def _controls(snapshot, lake_root: Path) -> tuple[Control, ...]:
    frames = _build_control_frames(snapshot, lake_root)
    frames.update(_noise_and_leakage(frames["momentum"]))
    specifications = (
        ("carry", "signal", CARRY_EXPRESSION, True),
        ("momentum", "momentum", MOMENTUM_EXPRESSION, True),
        ("noise", "signal", NOISE_EXPRESSION, True),
        ("leakage", "signal", LEAKAGE_EXPRESSION, False),
    )
    controls = []
    for name, column, expression, expect_pass in specifications:
        frame = frames.get(name)
        if frame is None or frame.empty:
            continue
        signals = _flatten(_emit(frame, column, per_symbol=True))
        labels = _flatten(_emit(frame, "forward_return", per_symbol=True))
        times = _flatten(_emit(frame, "time", per_symbol=True))
        controls.append(
            Control(
                name=name,
                signal=tuple(float(value) for value in signals),
                label=tuple(float(value) for value in labels),
                times=tuple(str(value) for value in times),
                expression=expression,
                expect_methodology_pass=expect_pass,
            )
        )
    return tuple(controls)


def _evidence_root() -> Path:
    run_id = f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{os.getpid()}"
    root = rs.reports_root().joinpath(*EVIDENCE_SUBDIR, run_id)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_real_env_controls_are_archived_with_snapshot_binding(f007_snapshot_id):
    snapshot_id = _require_execution_environment(f007_snapshot_id)
    snapshot = rs.load_snapshot(rs.reports_root(), snapshot_id)
    lake_root = Path(os.getenv("ALPHAMILL_LAKE_DIR", REPO / "lake"))
    config = load_run_config(REPO / "tests" / "fixtures" / "f007" / "method-v1.json")
    observed_at = datetime.now(UTC).isoformat()
    controls = _controls(snapshot, lake_root)
    assert controls, "真实快照未派生任何控制序列"

    outcomes = []
    for control in controls:
        verdict = evaluate_methodology(
            expression=control.expression,
            declared_capabilities=("operator",),
            context=GuardContext(
                max_label_horizon=config.max_label_horizon, embargo=config.max_label_horizon
            ),
        )
        evaluation = evaluate_fixture(
            config=config,
            times=control.times,
            signals=control.signal,
            labels=control.label,
            execution_tier="canonical",
            observed_at=observed_at,
        )
        outcomes.append(
            {
                "control": control.name,
                "methodology_passed": verdict.passed,
                "stage_results": evaluation.stage_results.to_payload(),
                "cost_verdict": evaluation.cost_verdict,
                "sample_tier": evaluation.sample_tier,
                "first_failure": first_failure(evaluation.stage_results),
                "observations": len(control.signal),
            }
        )

    by_name = {entry["control"]: entry for entry in outcomes}
    assert by_name["leakage"]["methodology_passed"] is False, "故意泄漏必须被 L1 拦截"
    for name in ("carry", "momentum", "noise"):
        if name in by_name:
            assert by_name[name]["methodology_passed"] is True

    evidence_root = _evidence_root()
    manifest = {
        "schema_version": 1,
        "run_id": evidence_root.name,
        "recorded_at": observed_at,
        "snapshot_id": snapshot.snapshot_id,
        "cutoff_time": snapshot.cutoff_time,
        "value_digests": {
            name: member.value_digest for name, member in sorted(snapshot.members.items())
        },
        "hostname": platform.node(),
        "device": DEVICE,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "controls": outcomes,
    }
    (evidence_root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    assert (evidence_root / "manifest.json").is_file()
    assert manifest["hostname"] and manifest["device"] == DEVICE
    assert set(manifest["value_digests"]) == set(snapshot.members)
