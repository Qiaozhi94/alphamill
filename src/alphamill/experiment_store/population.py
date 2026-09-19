"""canonical 登记与官方总体（`DR-003`/`DR-004`/`TR-003`/`AC-003`；任务 T012）。

- `cohort.json` 在首个 canonical 运行前**冻结**，内容寻址（`cohort_sha256:<digest>`，`frozen_at`/
  `frozen_by` 只进 provenance、不入身份），冻结后不可原地修改；
- 每个承诺成员无论证据完整（`EVIDENCE_READY`）、`REJECTED` 还是 `INCOMPLETE` 终态，都必须有终态
  registration event（`evaluation.registered`）——被拒者仍计入漏斗分母（`FR-004`）；
- 只有「承诺成员集合 == 终态登记集合」时才允许 `finalize-cohort`（否则 `E_COHORT_FROZEN`），
  并**原子**写出 `cohort_verdict.json`（失败不产生部分 verdict）；
- official population 是 `cohort.json + events/*.json + cohort_verdict.json` 的**确定性投影**，
  不另建可手改真相表；删除派生索引必须能完全重建。
"""

from __future__ import annotations

import json
import os
import shutil
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphamill.evaluation.contract_common import content_digest
from alphamill.evaluation.events import EVENT_REGISTERED, RunEvent
from alphamill.evaluation.run_state import STATE_REGISTERED, require_state
from alphamill.experiment_store.identity import canonical_json

SCHEMA_VERSION = 1
COHORTS_SUBDIR = "cohorts"
COHORT_FILENAME = "cohort.json"
VERDICT_FILENAME = "cohort_verdict.json"
EVENTS_SUBDIR = "events"
IDENTITY_FIELDS = (
    "schema_version",
    "hypothesis_family",
    "selection_stage",
    "method_config_ref",
    "cost_model_ref",
    "inclusion_rules",
    "commitments",
    "window",
    "universe_digest",
    "calendar_digest",
)


class CohortError(Exception):
    """cohort 未收齐、定义非法或登记冲突；映射到 `E_COHORT_FROZEN`。"""

    code = "E_COHORT_FROZEN"


class RegistryIntegrityError(CohortError):
    """已发布目录与请求不一致（篡改、同 ID 不同内容）。"""


@dataclass(frozen=True)
class MemberRegistration:
    candidate_id: str
    experiment_id: str
    run_state: str
    promotion_verdict: str
    sample_tier: str | None = None
    cost_model_version: str | None = None
    dedup: Mapping[str, Any] | None = None
    evidence_ref: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "experiment_id": self.experiment_id,
            "run_state": self.run_state,
            "promotion_verdict": self.promotion_verdict,
            "sample_tier": self.sample_tier,
            "cost_model_version": self.cost_model_version,
            "dedup": dict(self.dedup) if self.dedup else None,
            "evidence_ref": self.evidence_ref,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> MemberRegistration:
        return cls(
            candidate_id=str(payload["candidate_id"]),
            experiment_id=str(payload["experiment_id"]),
            run_state=str(payload["run_state"]),
            promotion_verdict=str(payload["promotion_verdict"]),
            sample_tier=payload.get("sample_tier"),
            cost_model_version=payload.get("cost_model_version"),
            dedup=payload.get("dedup"),
            evidence_ref=payload.get("evidence_ref"),
        )


def cohort_id_for(definition: Mapping[str, Any]) -> str:
    """cohort 身份：只哈希语义字段；冻结时间与冻结人不参与身份。"""
    missing = [field for field in IDENTITY_FIELDS if field not in definition]
    if missing:
        raise CohortError(f"cohort 定义缺字段: {missing}")
    material = {field: definition[field] for field in IDENTITY_FIELDS}
    return "cohort_sha256:" + content_digest(canonical_json(material).encode("utf-8")).removeprefix(
        "sha256:"
    )


def cohort_dir(root: Path, cohort_id: str) -> Path:
    return root / COHORTS_SUBDIR / cohort_id


def commitment_ids(definition: Mapping[str, Any]) -> tuple[str, ...]:
    commitments = definition.get("commitments")
    if not isinstance(commitments, Sequence) or isinstance(commitments, (str, bytes)):
        raise CohortError("cohort.commitments 必须是数组")
    ids = []
    for index, entry in enumerate(commitments):
        if not isinstance(entry, Mapping) or not entry.get("candidate_id"):
            raise CohortError(f"commitments[{index}] 缺 candidate_id")
        ids.append(str(entry["candidate_id"]))
    if len(set(ids)) != len(ids):
        raise CohortError(f"承诺成员重复: {ids}")
    return tuple(ids)


def freeze_cohort(root: Path, definition: Mapping[str, Any]) -> tuple[str, Path]:
    """冻结 cohort 并写入 `cohort.json`；同语义重发幂等，语义冲突拒绝。"""
    cohort_id = cohort_id_for(definition)
    directory = cohort_dir(root, cohort_id)
    final = directory / COHORT_FILENAME
    payload = (
        json.dumps(dict(definition), ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    ).encode("utf-8")
    if final.is_file():
        if final.read_bytes() != payload:
            raise RegistryIntegrityError(f"cohort 定义与已冻结内容不一致: {final}")
        return cohort_id, final
    final.parent.mkdir(parents=True, exist_ok=True)
    temp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    temp.write_bytes(payload)
    os.replace(temp, final)
    return cohort_id, final


def load_cohort(root: Path, cohort_id: str) -> dict[str, Any]:
    final = cohort_dir(root, cohort_id) / COHORT_FILENAME
    if not final.is_file():
        raise CohortError(f"未找到已冻结 cohort: {cohort_id}")
    definition = json.loads(final.read_text(encoding="utf-8"))
    if cohort_id_for(definition) != cohort_id:
        raise RegistryIntegrityError(f"cohort 身份重算不符: {cohort_id}")
    return definition


def register_member(
    root: Path, cohort_id: str, registration: MemberRegistration, event: RunEvent
) -> Path:
    """登记一个终态成员；`evaluation.registered` 是该幂等写入的唯一凭据。"""
    definition = load_cohort(root, cohort_id)
    if event.type != EVENT_REGISTERED:
        raise CohortError(f"成员登记必须用 {EVENT_REGISTERED}，收到 {event.type!r}")
    if event.to_state != STATE_REGISTERED:
        raise CohortError(f"成员登记必须落到 {STATE_REGISTERED}，收到 {event.to_state!r}")
    if event.experiment_id != registration.experiment_id:
        raise CohortError("事件 experiment_id 与登记载荷不一致")
    require_state(registration.run_state)
    if registration.run_state != STATE_REGISTERED:
        raise CohortError(f"成员终态必须是 {STATE_REGISTERED}，收到 {registration.run_state!r}")
    if registration.candidate_id not in commitment_ids(definition):
        raise CohortError(f"候选 {registration.candidate_id} 不在 cohort 承诺内")
    directory = cohort_dir(root, cohort_id) / EVENTS_SUBDIR
    directory.mkdir(parents=True, exist_ok=True)
    final = directory / f"{event.event_id}.json"
    payload = (
        json.dumps(
            {"event": event.to_payload(), "registration": registration.to_payload()},
            ensure_ascii=False,
            indent=1,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    if final.is_file():
        if final.read_bytes() != payload:
            raise RegistryIntegrityError(f"同 event_id 登记内容不一致: {final}")
        return final
    temp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    temp.write_bytes(payload)
    os.replace(temp, final)
    return final


def registrations(root: Path, cohort_id: str) -> tuple[MemberRegistration, ...]:
    definition = load_cohort(root, cohort_id)
    order = commitment_ids(definition)
    directory = cohort_dir(root, cohort_id) / EVENTS_SUBDIR
    if not directory.is_dir():
        return ()
    by_candidate: dict[str, MemberRegistration] = {}
    source: dict[str, Path] = {}
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        registration = MemberRegistration.from_payload(payload["registration"])
        existing = by_candidate.get(registration.candidate_id)
        if existing is not None and existing != registration:
            raise RegistryIntegrityError(
                f"候选 {registration.candidate_id} 存在不一致的多条终态登记: "
                f"{source[registration.candidate_id].name} 与 {path.name}（拒绝静默 last-wins）"
            )
        by_candidate[registration.candidate_id] = registration
        source[registration.candidate_id] = path
    return tuple(by_candidate[candidate] for candidate in order if candidate in by_candidate)


def missing_commitments(root: Path, cohort_id: str) -> tuple[str, ...]:
    registered = {entry.candidate_id for entry in registrations(root, cohort_id)}
    return tuple(
        candidate
        for candidate in commitment_ids(load_cohort(root, cohort_id))
        if candidate not in registered
    )


def assert_cohort_complete(root: Path, cohort_id: str) -> None:
    missing = missing_commitments(root, cohort_id)
    if missing:
        raise CohortError(f"cohort 仍有 {len(missing)} 个承诺成员未终态登记: {list(missing)}")


def _verdict_semantically_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    """幂等判据排除墙钟 `finalized_at`（`R1-008`）：其余字段逐项相等才算同一 verdict。"""

    def semantic(entry: Mapping[str, Any]) -> dict[str, Any]:
        value = dict(entry)
        value.pop("finalized_at", None)
        return value

    return semantic(left) == semantic(right)


def finalize_cohort(
    root: Path, cohort_id: str, *, verdict: Mapping[str, Any], finalized_at: str
) -> Path:
    """收齐校验通过后原子写 `cohort_verdict.json`；失败不产生部分 verdict。"""
    assert_cohort_complete(root, cohort_id)
    definition = load_cohort(root, cohort_id)
    entries = registrations(root, cohort_id)
    promotion_overrides = verdict.get("promotion_verdicts") or {}
    dedup_overrides = verdict.get("dedup") or {}
    members = []
    for entry in entries:
        payload = entry.to_payload()
        candidate = entry.candidate_id
        if candidate in promotion_overrides:
            payload["promotion_verdict"] = promotion_overrides[candidate]
        if candidate in dedup_overrides:
            payload["dedup"] = dedup_overrides[candidate]
        members.append(payload)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "cohort_id": cohort_id,
        "status": "FINALIZED",
        "finalized_at": finalized_at,
        "trial_count": len(definition["commitments"]),
        "member_count": len(members),
        "rejected_count": sum(1 for member in members if member["promotion_verdict"] == "rejected"),
        "members": members,
        "cohort_statistics": dict(verdict),
    }
    directory = cohort_dir(root, cohort_id)
    final = directory / VERDICT_FILENAME
    encoded = (json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    if final.is_file():
        existing = json.loads(final.read_text(encoding="utf-8"))
        if _verdict_semantically_equal(existing, payload):
            return final
        raise RegistryIntegrityError(f"cohort verdict 已存在且内容不一致: {final}")
    temp = final.with_name(f"{final.name}.tmp-{os.getpid()}")
    temp.write_bytes(encoded)
    os.replace(temp, final)
    return final


def load_verdict(root: Path, cohort_id: str) -> dict[str, Any] | None:
    final = cohort_dir(root, cohort_id) / VERDICT_FILENAME
    if not final.is_file():
        return None
    return json.loads(final.read_text(encoding="utf-8"))


def official_population(root: Path, cohort_id: str) -> dict[str, Any]:
    """official population = cohort + 终态登记 + verdict 的确定性投影（可重建）。"""
    definition = load_cohort(root, cohort_id)
    return {
        "cohort": definition,
        "cohort_id": cohort_id,
        "registrations": [entry.to_payload() for entry in registrations(root, cohort_id)],
        "verdict": load_verdict(root, cohort_id),
    }


def assert_projection_rebuilds(root: Path, cohort_id: str) -> None:
    """删除派生索引后必须能完全重建：先删索引，再要求投影与删除前逐字段相等且计数自洽。"""
    before = official_population(root, cohort_id)
    derived = cohort_dir(root, cohort_id) / "index"
    reset_derived_indexes(root, cohort_id)
    if derived.exists():
        raise RegistryIntegrityError("派生索引未被删除，重建前提不成立")
    after = official_population(root, cohort_id)
    if after != before:
        raise RegistryIntegrityError(f"official population 投影不确定: {cohort_id}")
    verdict = after["verdict"]
    if verdict is None:
        return
    if verdict["trial_count"] != len(after["cohort"]["commitments"]):
        raise RegistryIntegrityError("verdict trial_count 与承诺成员数不符")
    if (
        verdict["member_count"] + len(missing_commitments(root, cohort_id))
        != verdict["trial_count"]
    ):
        raise RegistryIntegrityError("verdict member_count 与登记集合不符")
    final_members = verdict.get("members") or after["registrations"]
    rejected = sum(1 for member in final_members if member["promotion_verdict"] == "rejected")
    if rejected != verdict["rejected_count"]:
        raise RegistryIntegrityError("verdict rejected_count 与登记集合不符")


def reset_derived_indexes(root: Path, cohort_id: str) -> None:
    """删除派生索引目录（不触碰 cohort/events/verdict 真相源），供重建测试使用。"""
    derived = cohort_dir(root, cohort_id) / "index"
    if derived.exists():
        shutil.rmtree(derived)
