"""T001 / `AC-006`·`AC-008`：F002/F003/F008 上游契约摄入与信号源分层的契约测试。

这些测试固定的是 **F007 消费者侧**契约（字段名与枚举）。F003/F008 尚在开发中，
差异会在这里先变红。覆盖：universe artifact digest/canonical/schema 校验与
`universe_at(T)` 时点语义；**F008 发布器产出的字节按同一 digest 被 F007 消费面装载**
（两侧 canonical 序列化各自独立实现，跨实现漂移在此失败关闭）；生成侧只消费 completed
运行、拒绝者仍入分母、未知原因码失败关闭；算子能力登记表默认拒绝；协同池无豁免；
信号适配不改数值与 `source=placeholder` 分层。
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from alphamill.data_bridge import paths
from alphamill.data_bridge.symbol_map import derive_pairs
from alphamill.data_bridge.universe.artifact import publish_artifact
from alphamill.data_bridge.universe.membership import TradabilityInterval
from alphamill.evaluation import upstream_contracts as uc
from alphamill.evaluation.universe_ledger import UniverseMember, publish_universe

T0 = datetime(2026, 7, 1, tzinfo=UTC)
T_MID = datetime(2026, 7, 20, tzinfo=UTC)
T3 = datetime(2026, 9, 1, tzinfo=UTC)
BTC_FROM = datetime(2026, 7, 10, tzinfo=UTC)
BTC_TO = datetime(2026, 8, 15, tzinfo=UTC)
ETH_FROM = datetime(2026, 7, 1, tzinfo=UTC)

# `IR-002` 冻结的字面文档：顶层 {schema_version, members}、成员严格三键、按
# (lake_pair, valid_from) 排序、valid_to=null 表示当前有效。
UNIVERSE_DOCUMENT = {
    "schema_version": 1,
    "members": [
        {
            "lake_pair": "BTC-USDT-PERP",
            "valid_from": "2026-07-10T00:00:00Z",
            "valid_to": "2026-08-15T00:00:00Z",
        },
        {"lake_pair": "ETH-USDT-PERP", "valid_from": "2026-07-01T00:00:00Z", "valid_to": None},
    ],
}


def _members() -> list[UniverseMember]:
    return [
        UniverseMember("ETH-USDT-PERP", ETH_FROM, None),
        UniverseMember("BTC-USDT-PERP", BTC_FROM, BTC_TO),
    ]


def _artifact_path(root: Path, digest: str) -> Path:
    return root / "_metadata" / "universes" / f"{digest}.json"


def _independent_payload(document: dict) -> bytes:
    """独立于被测模块复算 canonical 字节：只用 stdlib json 固定 `IR-002` 的规则。"""
    return json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    ).encode("utf-8")


def _publish_document(tmp_path: Path, document: dict) -> str:
    """按「文件名的 digest = 自身字节摘要」写入 artifact 目录（模拟发布侧落盘）。"""
    payload = _independent_payload(document)
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    target = _artifact_path(tmp_path, digest)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return digest


# ---------- F008 universe ----------


def test_universe_key_sets_are_frozen():
    assert set(UNIVERSE_DOCUMENT) == set(uc.UNIVERSE_TOP_LEVEL_KEYS)
    assert set(UNIVERSE_DOCUMENT["members"][0]) == set(uc.UNIVERSE_MEMBER_KEYS)
    assert uc.UNIVERSE_SCHEMA_VERSION == 1


def test_universe_artifact_is_canonical_json_content_addressed(tmp_path):
    digest = publish_universe(_members(), tmp_path)
    expected = "sha256:" + hashlib.sha256(_independent_payload(UNIVERSE_DOCUMENT)).hexdigest()
    assert digest == expected
    target = _artifact_path(tmp_path, digest)
    assert target.read_bytes() == _independent_payload(UNIVERSE_DOCUMENT)
    # 同 digest 逐字节一致：成员顺序不同的输入归一到同一 canonical 字节
    assert publish_universe(list(reversed(_members())), tmp_path) == digest
    assert target.read_bytes() == _independent_payload(UNIVERSE_DOCUMENT)
    # 落盘只有 `<digest>.json`，不再有任何 `.csv` 路径
    assert [item.name for item in uc.universe_artifact_dir(tmp_path).iterdir()] == [
        f"{digest}.json"
    ]


def test_universe_at_returns_point_in_time_membership(tmp_path):
    digest = publish_universe(_members(), tmp_path)
    ledger = uc.load_universe(digest, tmp_path)
    assert ledger.digest == digest
    assert ledger.schema_version == uc.UNIVERSE_SCHEMA_VERSION
    assert ledger.universe_at(T0) == ("ETH-USDT-PERP",)
    assert ledger.universe_at(T_MID) == ("BTC-USDT-PERP", "ETH-USDT-PERP")
    assert ledger.universe_at(T3) == ("ETH-USDT-PERP",)


def test_universe_members_carry_only_the_minimal_pit_projection(tmp_path):
    ledger = uc.load_universe(publish_universe(_members(), tmp_path), tmp_path)
    btc = next(member for member in ledger.members if member.lake_pair == "BTC-USDT-PERP")
    eth = next(member for member in ledger.members if member.lake_pair == "ETH-USDT-PERP")
    assert (btc.valid_from, btc.valid_to) == (BTC_FROM, BTC_TO)
    assert eth.valid_to is None


def test_universe_at_half_open_boundaries(tmp_path):
    ledger = uc.load_universe(publish_universe(_members(), tmp_path), tmp_path)
    assert ledger.universe_at(BTC_FROM) == ("BTC-USDT-PERP", "ETH-USDT-PERP")  # 左闭
    assert ledger.universe_at(BTC_FROM - timedelta(seconds=1)) == ("ETH-USDT-PERP",)
    assert ledger.universe_at(BTC_TO) == ("ETH-USDT-PERP",)  # 右开
    assert ledger.universe_at(BTC_TO - timedelta(seconds=1)) == (
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
    )


def test_universe_digest_tamper_is_detected(tmp_path):
    digest = publish_universe(_members(), tmp_path)
    target = _artifact_path(tmp_path, digest)
    target.write_bytes(target.read_bytes().replace(b"BTC-USDT-PERP", b"XBT-USDT-PERP"))
    with pytest.raises(uc.UpstreamContractError, match="digest 校验失败"):
        uc.load_universe(digest, tmp_path)


def test_non_canonical_universe_bytes_fail_closed(tmp_path):
    payload = json.dumps(UNIVERSE_DOCUMENT, indent=2, sort_keys=True).encode("utf-8")
    digest = "sha256:" + hashlib.sha256(payload).hexdigest()
    target = _artifact_path(tmp_path, digest)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    with pytest.raises(uc.UpstreamContractError, match="canonical"):
        uc.load_universe(digest, tmp_path)


def test_unknown_universe_schema_version_fails_closed(tmp_path):
    digest = _publish_document(tmp_path, {**UNIVERSE_DOCUMENT, "schema_version": 2})
    with pytest.raises(uc.UpstreamContractError, match="schema_version"):
        uc.load_universe(digest, tmp_path)


def test_unknown_universe_keys_fail_closed(tmp_path):
    top_level = _publish_document(tmp_path, {**UNIVERSE_DOCUMENT, "reason": "listed"})
    with pytest.raises(uc.UpstreamContractError, match="顶层键非法"):
        uc.load_universe(top_level, tmp_path)
    member = {
        "lake_pair": "BTC-USDT-PERP",
        "valid_from": "2026-07-10T00:00:00Z",
        "valid_to": None,
        "universe_id": "uni-1",
    }
    member_key = _publish_document(tmp_path, {"schema_version": 1, "members": [member]})
    with pytest.raises(uc.UpstreamContractError, match="成员键非法"):
        uc.load_universe(member_key, tmp_path)


def test_overlapping_validity_windows_fail_closed(tmp_path):
    overlapping = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT-PERP",
                "valid_from": "2026-07-01T00:00:00Z",
                "valid_to": "2026-08-01T00:00:00Z",
            },
            {"lake_pair": "BTC-USDT-PERP", "valid_from": "2026-07-15T00:00:00Z", "valid_to": None},
        ],
    }
    digest = _publish_document(tmp_path, overlapping)
    with pytest.raises(uc.UpstreamContractError, match="overlapping validity windows"):
        uc.load_universe(digest, tmp_path)
    with pytest.raises(uc.UpstreamContractError, match="overlapping validity windows"):
        publish_universe(
            [
                UniverseMember("BTC-USDT-PERP", T0, datetime(2026, 8, 1, tzinfo=UTC)),
                UniverseMember("BTC-USDT-PERP", datetime(2026, 7, 15, tzinfo=UTC), None),
            ],
            tmp_path,
        )


def test_missing_universe_artifact_fails_closed(tmp_path):
    with pytest.raises(uc.UpstreamContractError, match="不存在"):
        uc.load_universe("sha256:" + "1" * 64, tmp_path)


def test_universe_artifact_dir_is_lake_metadata(tmp_path):
    assert uc.universe_artifact_dir(tmp_path) == tmp_path / "_metadata" / "universes"


def test_default_lake_root_matches_data_bridge(tmp_path, monkeypatch):
    monkeypatch.setenv("ALPHAMILL_LAKE_DIR", str(tmp_path))
    assert uc.universe_artifact_dir() == paths.lake_root() / "_metadata" / "universes"


# F008 生产侧命名空间：同一 `db_symbol` 在 spot 与 perp 两个湖内命名空间成对登记
# （design §3 定稿口径），`-PERP` 后缀由生产侧 `symbol_map.derive_pairs` 加一次。
BTC_SPOT = derive_pairs("BTC/USDT", "spot")[0]
BTC_PERP = derive_pairs("BTC/USDT:USDT", "perp")[0]
ETH_PERP = derive_pairs("ETH/USDT:USDT", "perp")[0]
SOL_PERP = derive_pairs("SOL/USDT:USDT", "perp")[0]
F008_MICRO_FROM = datetime(2026, 7, 10, 0, 0, 0, 500_000, tzinfo=UTC)

# F008 发布器应当落盘的 canonical 文档：按 (lake_pair, valid_from) 排序、时间戳为
# UTC ISO-8601（`Z`、微秒保留 6 位）、`valid_to=null` 表示当前有效。
F008_DOCUMENT = {
    "schema_version": 1,
    "members": [
        {"lake_pair": "BTC-USDT", "valid_from": "2026-07-10T00:00:00Z", "valid_to": None},
        {
            "lake_pair": "BTC-USDT-PERP",
            "valid_from": "2026-07-10T00:00:00Z",
            "valid_to": "2026-08-15T00:00:00Z",
        },
        {"lake_pair": "ETH-USDT-PERP", "valid_from": "2026-07-01T00:00:00Z", "valid_to": None},
        {
            "lake_pair": "SOL-USDT-PERP",
            "valid_from": "2026-07-10T00:00:00.500000Z",
            "valid_to": None,
        },
    ],
}


def _f008_intervals() -> list[TradabilityInterval]:
    """F008 生产侧发布器入参：刻意乱序，排序由发布器负责。"""
    return [
        TradabilityInterval(lake_pair=ETH_PERP, valid_from=ETH_FROM, valid_to=None),
        TradabilityInterval(lake_pair=BTC_PERP, valid_from=BTC_FROM, valid_to=BTC_TO),
        TradabilityInterval(lake_pair=BTC_SPOT, valid_from=BTC_FROM, valid_to=None),
        TradabilityInterval(lake_pair=SOL_PERP, valid_from=F008_MICRO_FROM, valid_to=None),
    ]


def test_f008_publisher_digest_is_loadable_by_f007(tmp_path):
    """F008 发布器产出的字节必须能按同一 digest 被 F007 消费面装载。

    两侧 canonical 序列化是刻意各自独立实现（发布侧 `data_bridge/universe/canonical.py`、
    消费侧 `evaluation/universe_ledger.py`，互不 import）：本用例是把 **F008 发布字节** 交给
    **F007 只读加载** 的唯一一处，任一侧键序/分隔符/时间格式/尾随字节漂移都在这里变红，
    而不是等到 `--universe` 路径拒载 artifact。
    """
    digest, target = publish_artifact(_f008_intervals(), tmp_path)

    # 1) stdlib 独立复算 digest 与 canonical 字节（不 import 任何一侧的规范化模块）
    payload = target.read_bytes()
    assert digest == "sha256:" + hashlib.sha256(payload).hexdigest()
    assert payload == _independent_payload(F008_DOCUMENT)
    assert target == _artifact_path(tmp_path, digest)

    # 2) F007 侧按同一 digest 加载：成员区间逐条一致
    ledger = uc.load_universe(digest, tmp_path)
    assert ledger.digest == digest
    assert ledger.schema_version == uc.UNIVERSE_SCHEMA_VERSION
    assert [(m.lake_pair, m.valid_from, m.valid_to) for m in ledger.members] == [
        (BTC_SPOT, BTC_FROM, None),
        (BTC_PERP, BTC_FROM, BTC_TO),
        (ETH_PERP, ETH_FROM, None),
        (SOL_PERP, F008_MICRO_FROM, None),
    ]
    # pair 归一化只发生在 F008 生产侧：F007 按 `lake_pair` 原样比对，不二次加 `-PERP`
    # （否则会读成 `BTC-USDT-PERP-PERP`，整个 perp 命名空间静默漏掉）
    assert (BTC_SPOT, BTC_PERP, ETH_PERP, SOL_PERP) == (
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
        "SOL-USDT-PERP",
    )

    # 3) universe_at(T) 与 F008 台账语义一致：半开区间 [valid_from, valid_to)
    assert ledger.universe_at(T0) == ("ETH-USDT-PERP",)
    assert ledger.universe_at(BTC_FROM - timedelta(seconds=1)) == ("ETH-USDT-PERP",)
    assert ledger.universe_at(BTC_FROM) == (  # 左闭（SOL 尚差 0.5 秒，见微秒用例）
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
    )
    assert ledger.universe_at(BTC_TO - timedelta(seconds=1)) == (
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
        "SOL-USDT-PERP",
    )
    assert ledger.universe_at(BTC_TO) == ("BTC-USDT", "ETH-USDT-PERP", "SOL-USDT-PERP")  # 右开
    assert ledger.universe_at(T_MID) == (
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
        "SOL-USDT-PERP",
    )
    assert ledger.universe_at(T3) == ("BTC-USDT", "ETH-USDT-PERP", "SOL-USDT-PERP")
    # 微秒精度逐位保留：截断会把 SOL 的生效边界整体前移
    assert ledger.universe_at(F008_MICRO_FROM - timedelta(microseconds=1)) == (
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
    )
    assert ledger.universe_at(F008_MICRO_FROM) == (
        "BTC-USDT",
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
        "SOL-USDT-PERP",
    )

    # 4) `IR-002` 冻结 `ensure_ascii=False`：非 ASCII 成员名逐字进字节（不写成 \uXXXX）。
    #    两侧任一方改转义设置，消费侧的 canonical 复算就会与发布字节不符而拒载。
    wide_digest, wide_target = publish_artifact(
        [TradabilityInterval(lake_pair="币安-BTC-USDT", valid_from=T0, valid_to=None)],
        tmp_path,
    )
    wide_payload = wide_target.read_bytes()
    assert "币安-BTC-USDT".encode() in wide_payload
    assert b"\\u" not in wide_payload
    assert wide_digest == "sha256:" + hashlib.sha256(wide_payload).hexdigest()
    assert uc.load_universe(wide_digest, tmp_path).universe_at(T0) == ("币安-BTC-USDT",)


# ---------- F003 生成侧 ----------


def test_only_completed_runs_are_consumed():
    funnel = uc.ingest_generation_events(
        [
            {
                "type": uc.EVENT_RUN_COMPLETED,
                "status": "completed",
                "run_id": "r1",
                "counts": {"registered": 50},
            },
            {
                "type": uc.EVENT_RUN_COMPLETED,
                "status": "partial",
                "run_id": "r2",
                "counts": {"registered": 5},
            },
            {"type": uc.EVENT_RUN_COMPLETED, "status": "failed", "run_id": "r3", "counts": {}},
        ]
    )
    assert [run.run_id for run in funnel.completed_runs] == ["r1"]
    assert funnel.registered_candidates == 50


def test_rejected_candidates_stay_in_denominator():
    funnel = uc.ingest_generation_events(
        [
            {
                "type": uc.EVENT_RUN_COMPLETED,
                "status": "completed",
                "run_id": "r1",
                "counts": {"registered": 50},
            },
            {
                "type": uc.EVENT_CANDIDATE_REJECTED,
                "run_id": "r1",
                "expression": "x",
                "reason_code": uc.REASON_LOOKAHEAD,
            },
            {
                "type": uc.EVENT_CANDIDATE_REJECTED,
                "run_id": "r1",
                "expression": "y",
                "reason_code": uc.REASON_LOOKAHEAD,
            },
            {
                "type": uc.EVENT_CANDIDATE_REJECTED,
                "run_id": "r1",
                "expression": "z",
                "reason_code": uc.REASON_UNREGISTERED_OPERATOR,
            },
        ]
    )
    assert funnel.rejected_total == 3
    assert funnel.rejected_by_reason[uc.REASON_LOOKAHEAD] == 2
    assert funnel.rejected_by_reason[uc.REASON_INSUFFICIENT_REACHABILITY] == 0
    assert funnel.denominator == 53


def test_unknown_rejection_reason_fails_closed():
    with pytest.raises(uc.UpstreamContractError, match="原因码未登记"):
        uc.ingest_generation_events(
            [{"type": uc.EVENT_CANDIDATE_REJECTED, "run_id": "r1", "reason_code": "surprise"}]
        )


def test_unknown_generation_event_fails_closed():
    with pytest.raises(uc.UpstreamContractError, match="类型未登记"):
        uc.ingest_generation_events([{"type": "generation.something_else"}])


def test_operator_registry_default_deny():
    registry = uc.load_operator_capabilities(
        {
            "schema_version": uc.OPERATOR_SCHEMA_VERSION,
            "operators": [
                {"name": "rank", "kind": "cross_sectional", "window_semantics": "same_ts"}
            ],
        }
    )
    assert registry.require("rank").kind == "cross_sectional"
    with pytest.raises(uc.UpstreamContractError, match="未登记"):
        registry.require("future_peek")


def test_operator_registry_rejects_unknown_kind():
    with pytest.raises(uc.UpstreamContractError, match="kind 未登记"):
        uc.load_operator_capabilities(
            {
                "schema_version": uc.OPERATOR_SCHEMA_VERSION,
                "operators": [{"name": "x", "kind": "magic"}],
            }
        )


def test_pool_factor_has_no_exemption_and_exposes_provenance():
    pool = uc.load_pool_factor(
        {
            "generator": "pool",
            "factor_id": "factor_sha256:pool",
            "members": [{"factor_id": "f-b", "weight": 0.4}, {"factor_id": "f-a", "weight": 0.6}],
        }
    )
    provenance = pool.provenance()
    assert provenance["generator"] == "pool"
    assert [m["factor_id"] for m in provenance["members"]] == ["f-a", "f-b"]
    assert sum(m["weight"] for m in provenance["members"]) == pytest.approx(1.0)
    with pytest.raises(uc.UpstreamContractError, match="generator"):
        uc.load_pool_factor({"generator": "alphagen", "factor_id": "x", "members": []})


# ---------- 信号型 FactorDef 适配 ----------


def _records() -> list[dict]:
    return [
        {
            "time": "2026-09-01T00:00:00Z",
            "symbol": "BTC/USDT",
            "source": "kronos",
            "signal": 0.123456789,
            "realized": 0.5,
        },
        {
            "time": "2026-09-01T01:00:00Z",
            "symbol": "BTC/USDT",
            "source": "placeholder",
            "signal": -0.987654321,
            "realized": None,
        },
    ]


def test_signal_adapter_preserves_values_exactly():
    observations, provenance = uc.adapt_signal_records(
        _records(),
        dataset="signals_log",
        adapter_version="f007-adapter-v1",
        signal_column="signal",
        label_column="realized",
        horizons={"kronos": 1, "placeholder": 4},
    )
    assert [o.value for o in observations] == [0.123456789, -0.987654321]
    assert observations[1].label is None
    assert observations[0].horizon == 1
    assert provenance.to_dict()["source_distribution"] == {"kronos": 1, "placeholder": 1}
    assert provenance.has_placeholder is True


def test_placeholder_signal_source_layering():
    _, provenance = uc.adapt_signal_records(
        _records(),
        dataset="signals_log",
        adapter_version="f007-adapter-v1",
        signal_column="signal",
        label_column="realized",
    )
    with pytest.raises(uc.UpstreamContractError) as excinfo:
        uc.assert_signal_source_allowed(provenance, uc.TIER_CANONICAL)
    assert excinfo.value.code == "E_INPUT_INVALID"
    preview = uc.assert_signal_source_allowed(provenance, uc.TIER_PREVIEW)
    assert preview == {"signal_source": "placeholder", "approximation": True}


def test_real_signal_source_is_not_marked_approximate():
    _, provenance = uc.adapt_signal_records(
        [{"time": "t", "symbol": "s", "source": "kronos", "signal": 1.0}],
        dataset="signals_log",
        adapter_version="f007-adapter-v1",
        signal_column="signal",
    )
    assert uc.assert_signal_source_allowed(provenance, uc.TIER_CANONICAL) == {
        "signal_source": "real",
        "approximation": False,
    }


def test_non_numeric_signal_is_rejected():
    with pytest.raises(uc.UpstreamContractError, match="不是数值"):
        uc.adapt_signal_records(
            [{"time": "t", "symbol": "s", "signal": "high"}],
            dataset="signals_log",
            adapter_version="v1",
            signal_column="signal",
        )


def test_load_universe_rejects_malformed_digest_before_io(tmp_path) -> None:
    """`sha256:` 前缀不够：路径成分必须在拼路径前被拒（检视 R1-004）。

    `sha256:../escape` 若只查前缀，`..` 会成为路径成分——先读 artifact 目录外的文件、再被
    digest 比对拒掉。消费侧的校验规则与发布侧 `artifact.is_digest()` 一致（各自独立实现）。
    """
    for bad in ("sha256:../escape", "sha256:" + "Z" * 64, "sha256:short", "not-a-digest"):
        with pytest.raises(uc.UpstreamContractError):
            uc.load_universe(bad, tmp_path)
