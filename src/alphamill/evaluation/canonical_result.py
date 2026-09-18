"""canonical 运行结果对象（任务 T013/T016）。

单独成模块，使 `canonical`（正常路径）与 `rejection`（方法论门拒绝路径）都能构造同一个结果类型，
而不产生循环导入。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from alphamill.evaluation.contract_common import TIER_CANONICAL
from alphamill.evaluation.pipeline import failure_text, first_failure


@dataclass(frozen=True)
class CanonicalResult:
    experiment_id: str
    cohort_id: str
    candidate_id: str
    snapshot_id: str
    code_build_digest: str
    state: str
    cost_verdict: str
    sample_tier: str
    stage_results: Any
    approximation: Mapping[str, Any]
    promotion_verdict: str | None
    artifact_dir: str
    reused: bool

    def to_payload(self) -> dict[str, Any]:
        return {
            "execution_tier": TIER_CANONICAL,
            "experiment_id": self.experiment_id,
            "cohort_id": self.cohort_id,
            "candidate_id": self.candidate_id,
            "research_snapshot_id": self.snapshot_id,
            "code_build_digest": self.code_build_digest,
            "state": self.state,
            "cost_verdict": self.cost_verdict,
            "sample_tier": self.sample_tier,
            "promotion_verdict": self.promotion_verdict,
            "stages": self.stage_results.to_payload(),
            "approximation": dict(self.approximation),
            "first_failure": first_failure(self.stage_results),
            "artifact_dir": self.artifact_dir,
            "reused": self.reused,
        }

    def first_screen(self) -> tuple[str, ...]:
        return (
            f"tier={TIER_CANONICAL} cohort={self.cohort_id}",
            f"experiment_id={self.experiment_id}",
            f"candidate={self.candidate_id}",
            f"data={self.snapshot_id}",
            f"code={self.code_build_digest}",
            f"state={self.state}",
            f"cost_verdict={self.cost_verdict} sample_tier={self.sample_tier}",
            f"promotion_verdict={self.promotion_verdict}",
            f"artifact={self.artifact_dir}",
            f"reused={self.reused}",
            f"first_failure={failure_text(first_failure(self.stage_results))}",
        )
