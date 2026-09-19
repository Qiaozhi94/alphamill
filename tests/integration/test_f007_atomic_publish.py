"""T011 / `AC-005`·`NFR-001`·`TR-001`·`TR-002`：原子发布、恢复与运行事件契约。

覆盖：preview/canonical 发布目录与消费者判据、曲线-标量互推不符即拒绝且**不留可见半成品**、
失败注入（缺 registration / 缺 curves_summary / 曲线损坏）一律 `E_PUBLISH_INCOMPLETE`、
quarantine 模式、同语义重发幂等与语义冲突拒绝、跨文件系统发布拒绝、
事件幂等追加与按 cohort/stage/type 查询。
"""

from __future__ import annotations

import json
import os
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.evaluation import publisher
from alphamill.evaluation.capabilities import CapabilityError, context_for
from alphamill.evaluation.contract_common import TIER_CANONICAL, TIER_PREVIEW
from alphamill.evaluation.events import (
    EVENT_GATE_REJECTED,
    EVENT_REGISTERED,
    EVENT_RUN_STATE_CHANGED,
    EventError,
    append_events,
    build_event,
    query_events,
    read_events,
)
from alphamill.evaluation.publisher import (
    CURVES_NAME,
    MANIFEST_NAME,
    REGISTRATION_NAME,
    PublishError,
    PublishRequest,
    is_published,
    list_published,
    publish,
)
from alphamill.factor_factory.bench.curves import (
    CurvesError,
    build_equity_curves,
    read_curves,
)

EXPERIMENT = "sha256:" + "e" * 64
SNAPSHOT = "sha256:" + "s" * 64
OBJECT = "factor_sha256:" + "o" * 64
COHORT = "cohort_sha256:" + "c" * 64
START = datetime(2026, 9, 1, tzinfo=UTC)


def _curves(size: int = 12) -> object:
    times = tuple(START + timedelta(hours=index) for index in range(size))
    periods = tuple(0.01 if index % 3 else -0.004 for index in range(size))
    return build_equity_curves(periods, times=times)


def _request(
    *, canonical: bool = False, curves=None, report=None, registration=None, events=()
) -> PublishRequest:
    sidecar = curves or _curves()
    return PublishRequest(
        experiment_id=EXPERIMENT,
        manifest={
            "schema_version": 1,
            "execution_tier": TIER_CANONICAL if canonical else TIER_PREVIEW,
            "experiment_id": EXPERIMENT,
            "state": "REGISTERED" if canonical else "PREVIEW_DONE",
            "events_digest": "sha256:" + "d" * 64,
            **({"research_snapshot_id": SNAPSHOT, "object_id": OBJECT} if canonical else {}),
        },
        report=report
        if report is not None
        else {"schema_version": 1, "curves_summary": sidecar.scalar_summary()},
        curves=sidecar,
        events=events,
        registration=registration
        if registration is not None
        else ({"schema_version": 1} if canonical else None),
        object_id=OBJECT,
        snapshot_id=SNAPSHOT,
    )


def _events(count: int = 1):
    return tuple(
        build_event(
            experiment_id=EXPERIMENT,
            execution_tier=TIER_CANONICAL,
            cohort_id=COHORT,
            from_state="RUNNING",
            to_state="EVIDENCE_READY",
            stage="signal_quality",
            sequence=index,
        )
        for index in range(count)
    )


# ---------- 原子发布 ----------


def test_preview_publish_is_visible_only_after_rename(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    request = _request()
    target = publisher.target_dir(context, request)
    assert not target.exists()
    published = publish(context, request)
    assert published == target
    assert is_published(target, canonical=False)
    assert {path.name for path in target.iterdir()} >= {MANIFEST_NAME, "report.json", CURVES_NAME}


def test_canonical_publish_requires_registration(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    request = replace(_request(canonical=True), registration=None)
    with pytest.raises(PublishError, match="registration"):
        publish(context, request)
    target = publisher.target_dir(context, _request(canonical=True))
    assert not target.exists()


def test_canonical_publish_writes_registration_last_and_is_consumable(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    target = publish(context, _request(canonical=True))
    assert (target / REGISTRATION_NAME).is_file()
    assert is_published(target, canonical=True)
    assert [path.name for path in list_published(tmp_path / "bench", canonical=True)] == [
        target.name
    ]


def test_missing_curves_summary_blocks_publication(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    request = _request(report={"schema_version": 1})
    with pytest.raises(PublishError, match="curves_summary"):
        publish(context, request)
    assert not publisher.target_dir(context, request).exists()


def test_scalar_mismatch_blocks_publication(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    sidecar = _curves()
    summary = dict(sidecar.scalar_summary())
    summary["max_drawdown"] = 999.0
    request = _request(report={"schema_version": 1, "curves_summary": summary})
    with pytest.raises(PublishError, match="互推不符"):
        publish(context, request)
    assert not publisher.target_dir(context, request).exists()


def test_manifest_without_required_fields_blocks_publication(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    request = replace(_request(), manifest={"schema_version": 1})
    with pytest.raises(PublishError, match="manifest 缺必填字段"):
        publish(context, request)
    assert not publisher.target_dir(context, request).exists()


def test_quarantine_keeps_failed_attempt_out_of_the_consumer_path(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    request = _request(report={"schema_version": 1})
    with pytest.raises(PublishError):
        publish(context, request, quarantine_on_failure=True)
    target = publisher.target_dir(context, request)
    assert not target.exists()
    quarantined = list((tmp_path / "preview" / "_quarantine").glob("*.tmp-*"))
    assert quarantined and quarantined[0].is_dir()


def test_registration_is_written_only_after_validation(tmp_path):
    """R1-009 回归：registration-last——校验失败时 registration.json 不得写进失败批次。

    修复前 `_write_payload` 在校验前就写 registration.json，故障注入后 quarantine 目录里
    会残留 registration.json；本断言在删除「校验后再写 registration」次序时变红。
    """
    context = context_for(TIER_CANONICAL, tmp_path)
    sidecar = _curves()
    summary = dict(sidecar.scalar_summary())
    summary["max_drawdown"] = 999.0
    request = _request(canonical=True, report={"schema_version": 1, "curves_summary": summary})
    with pytest.raises(PublishError, match="互推不符"):
        publish(context, request, quarantine_on_failure=True)
    assert not publisher.target_dir(context, request).exists()
    quarantined = list((tmp_path / "bench" / "_quarantine").glob("*.tmp-*"))
    assert quarantined and quarantined[0].is_dir()
    assert not (quarantined[0] / REGISTRATION_NAME).exists()


def test_republish_with_identical_semantics_is_idempotent(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    request = _request()
    first = publish(context, request)
    second = publish(context, request)
    assert first == second
    assert is_published(first, canonical=False)


def test_republish_with_conflicting_semantics_is_rejected(tmp_path):
    context = context_for(TIER_PREVIEW, tmp_path)
    publish(context, _request())
    alternate = _curves(20)
    conflicting = _request(
        curves=alternate, report={"schema_version": 1, "curves_summary": alternate.scalar_summary()}
    )
    with pytest.raises(PublishError, match="语义不一致"):
        publish(context, conflicting)


def test_cross_filesystem_publish_is_rejected(tmp_path):
    shared_memory = Path("/dev/shm")
    if not shared_memory.is_dir():
        pytest.skip("/dev/shm 不可用，无法构造跨盘场景")
    reports = tmp_path / "reports"
    reports.mkdir()
    probe = shared_memory / f"f007-probe-{os.getpid()}"
    probe.mkdir()
    try:
        if probe.stat().st_dev == reports.stat().st_dev:
            pytest.skip("临时目录与 /dev/shm 同设备，无法构造跨盘场景")
        with pytest.raises(PublishError, match="同一文件系统"):
            publisher.assert_same_filesystem(probe, reports)
    finally:
        probe.rmdir()


def test_incomplete_directory_is_not_consumable(tmp_path):
    directory = tmp_path / "bench" / OBJECT / SNAPSHOT / EXPERIMENT
    directory.mkdir(parents=True)
    (directory / MANIFEST_NAME).write_text(json.dumps({"schema_version": 1}), encoding="utf-8")
    assert is_published(directory, canonical=True) is False
    assert list_published(tmp_path / "bench", canonical=True) == ()


def test_canonical_without_object_or_snapshot_is_rejected(tmp_path):
    context = context_for(TIER_CANONICAL, tmp_path)
    request = replace(_request(canonical=True), object_id=None)
    with pytest.raises(PublishError, match="canonical 发布缺"):
        publisher.target_dir(context, request)


def test_preview_context_resolves_only_to_the_preview_namespace(tmp_path):
    preview = context_for(TIER_PREVIEW, tmp_path)
    resolved = publisher.target_dir(preview, _request(canonical=True))
    assert resolved.is_relative_to(tmp_path / "preview")
    assert not resolved.is_relative_to(tmp_path / "bench")
    with pytest.raises(CapabilityError):
        preview.bench_dir(OBJECT, SNAPSHOT, EXPERIMENT)


# ---------- 曲线侧车 ----------


def test_curve_roundtrip_recomputes_scalars(tmp_path):
    sidecar = _curves()
    path = tmp_path / "curves.parquet"
    from alphamill.factor_factory.bench.curves import write_curves

    write_curves(path, sidecar)
    restored = read_curves(path)
    assert restored.scalar_summary() == sidecar.scalar_summary()
    assert len(restored.equity_net) == len(sidecar.equity_net)


def test_curve_with_short_column_is_rejected():
    sidecar = _curves()
    broken = sidecar.quantiles | {"q5": (0.0,)}
    with pytest.raises(CurvesError, match="长度"):
        type(sidecar)(
            times=sidecar.times,
            equity_net=sidecar.equity_net,
            drawdown=sidecar.drawdown,
            quantiles=broken,
            long_short=sidecar.long_short,
            rolling_ic={},
        )


# ---------- 运行事件 ----------


def test_event_append_is_idempotent_and_conflicts_are_integrity_errors(tmp_path):
    path = tmp_path / "events.jsonl"
    events = _events(2)
    assert len(append_events(path, events)) == 2
    assert len(append_events(path, events)) == 2
    tampered = replace(
        build_event(
            experiment_id=EXPERIMENT,
            execution_tier=TIER_CANONICAL,
            cohort_id=COHORT,
            from_state="RUNNING",
            to_state="REJECTED",
            stage="signal_quality",
            sequence=0,
        ),
        event_id=events[0].event_id,
    )
    with pytest.raises(EventError, match="完整性错误"):
        append_events(path, (tampered,))


def test_event_query_filters_by_cohort_stage_and_type(tmp_path):
    path = tmp_path / "events.jsonl"
    events = _events(3) + (
        build_event(
            experiment_id=EXPERIMENT,
            execution_tier=TIER_CANONICAL,
            cohort_id=COHORT,
            from_state="VALIDATING",
            to_state="REJECTED",
            stage="signal_quality",
            event_type=EVENT_GATE_REJECTED,
            sequence=9,
        ),
    )
    append_events(path, events)
    stored = read_events(path)
    assert len(query_events(stored, stage="signal_quality")) == 4
    assert len(query_events(stored, event_type=EVENT_GATE_REJECTED)) == 1
    assert len(query_events(stored, cohort_id=COHORT, event_type=EVENT_RUN_STATE_CHANGED)) == 3
    assert query_events(stored, cohort_id="cohort_sha256:" + "z" * 64) == ()


def test_event_validation_rejects_unknown_type_and_state():
    with pytest.raises(EventError, match="事件类型"):
        build_event(
            experiment_id=EXPERIMENT,
            execution_tier=TIER_CANONICAL,
            cohort_id=COHORT,
            from_state="RUNNING",
            to_state="EVIDENCE_READY",
            event_type="evaluation.mystery",
        )
    with pytest.raises(EventError, match="运行状态"):
        build_event(
            experiment_id=EXPERIMENT,
            execution_tier=TIER_CANONICAL,
            cohort_id=COHORT,
            from_state="NOWHERE",
            to_state="EVIDENCE_READY",
        )


def test_registered_event_uses_actual_terminal_state_and_validates_transition():
    """R1-113 回归：登记事件 `from_state` 取实际终态；非法迁移被 `assert_transition` 拒绝。"""
    from alphamill.evaluation.canonical_registration import registered_events
    from alphamill.evaluation.run_state import RunStateError

    event = registered_events(EXPERIMENT, COHORT, "cand", from_state="INCOMPLETE")[0]
    assert event.from_state == "INCOMPLETE"
    assert event.to_state == "REGISTERED"
    with pytest.raises(RunStateError, match="非法状态迁移"):
        registered_events(EXPERIMENT, COHORT, "cand", from_state="REGISTERED")


def test_registered_event_is_idempotent_on_experiment_id(tmp_path):
    path = tmp_path / "events.jsonl"
    event = build_event(
        experiment_id=EXPERIMENT,
        execution_tier=TIER_CANONICAL,
        cohort_id=COHORT,
        from_state="EVIDENCE_READY",
        to_state="REGISTERED",
        event_type=EVENT_REGISTERED,
        sequence=0,
    )
    append_events(path, (event,))
    append_events(path, (event,))
    assert len(read_events(path)) == 1
