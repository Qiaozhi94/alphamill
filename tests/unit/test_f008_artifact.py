"""T009 与 `AC-013`：台账 artifact 的 canonical JSON、内容寻址与 fail-closed 载入。

覆盖：同内容同 digest 且逐字节一致、内容变化得新 digest 且旧 digest 仍可读、
顶层/成员未知键拒绝、schema_version 不符拒绝、排序与 digest 篡改拒绝、
半开区间语义（左闭右开），以及写一次发布纪律。
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe.artifact import (
    ArtifactLedger,
    ArtifactMember,
    build_document,
    canonical_artifact_bytes,
    load_artifact,
    publish_artifact,
    validate_document,
)
from alphamill.data_bridge.universe.errors import UniverseArtifactError
from alphamill.data_bridge.universe.membership import TradabilityInterval

START = datetime(2024, 9, 10, tzinfo=UTC)
END = datetime(2026, 1, 1, tzinfo=UTC)


def _intervals() -> list[TradabilityInterval]:
    return [
        TradabilityInterval(lake_pair="ETH-USDT-PERP", valid_from=START, valid_to=END),
        TradabilityInterval(lake_pair="BTC-USDT-PERP", valid_from=START, valid_to=None),
    ]


# ---------- canonical 形式 ----------


def test_canonical_document_is_sorted_and_compact() -> None:
    payload = canonical_artifact_bytes(build_document(_intervals()))
    text = payload.decode("utf-8")
    assert text.startswith('{"members":[{"lake_pair":"BTC-USDT-PERP"')
    assert ": " not in text and ", " not in text
    assert not text.endswith("\n")
    assert '"schema_version":1' in text
    document = json.loads(text)
    assert [member["lake_pair"] for member in document["members"]] == [
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
    ]


def test_unknown_keys_are_rejected_at_every_level() -> None:
    document = build_document(_intervals())
    document["generated_by"] = "someone"
    with pytest.raises(UniverseArtifactError, match="顶层键集合非法"):
        validate_document(document)

    document = build_document(_intervals())
    document["members"][0]["reason"] = "listed"
    with pytest.raises(UniverseArtifactError, match="键集合非法"):
        validate_document(document)


def test_unsorted_members_are_rejected() -> None:
    document = {
        "schema_version": 1,
        "members": [
            {"lake_pair": "ETH-USDT-PERP", "valid_from": "2024-09-10T00:00:00Z", "valid_to": None},
            {"lake_pair": "BTC-USDT-PERP", "valid_from": "2024-09-10T00:00:00Z", "valid_to": None},
        ],
    }
    with pytest.raises(UniverseArtifactError, match="排序"):
        validate_document(document)


def test_window_must_be_positive() -> None:
    document = {
        "schema_version": 1,
        "members": [
            {
                "lake_pair": "BTC-USDT-PERP",
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_to": "2024-09-10T00:00:00Z",
            }
        ],
    }
    with pytest.raises(UniverseArtifactError, match="晚于"):
        validate_document(document)


def test_schema_version_must_be_integer() -> None:
    document = {"schema_version": "1", "members": []}
    with pytest.raises(UniverseArtifactError, match="整数"):
        validate_document(document)


# ---------- 发布与载入 ----------


def test_publish_is_content_addressed_and_byte_identical(tmp_path) -> None:
    first_digest, first_path = publish_artifact(_intervals(), tmp_path)
    reordered = list(reversed(_intervals()))
    second_digest, second_path = publish_artifact(reordered, tmp_path)
    assert first_digest == second_digest
    assert first_path == second_path
    assert first_path.name == f"{first_digest}.json"
    assert first_path.read_bytes() == canonical_artifact_bytes(build_document(_intervals()))


def test_changed_content_yields_new_digest_and_old_stays_readable(tmp_path) -> None:
    old_digest, old_path = publish_artifact(_intervals(), tmp_path)
    changed = [
        *_intervals(),
        TradabilityInterval(lake_pair="SOL-USDT-PERP", valid_from=START, valid_to=None),
    ]
    new_digest, new_path = publish_artifact(changed, tmp_path)
    assert new_digest != old_digest
    assert old_path.read_bytes() != new_path.read_bytes()

    old_ledger = load_artifact(old_digest, tmp_path)
    new_ledger = load_artifact(new_digest, tmp_path)
    assert {member.lake_pair for member in old_ledger.members} == {
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
    }
    assert {member.lake_pair for member in new_ledger.members} == {
        "BTC-USDT-PERP",
        "ETH-USDT-PERP",
        "SOL-USDT-PERP",
    }


def test_publish_is_write_once(tmp_path) -> None:
    digest, path = publish_artifact(_intervals(), tmp_path)
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(UniverseArtifactError, match="内容不一致"):
        publish_artifact(_intervals(), tmp_path)
    assert path.read_bytes().endswith(b" ")
    assert digest  # 旧 digest 已发布，内容被篡改由载入侧检出


def test_load_detects_tampered_bytes(tmp_path) -> None:
    digest, path = publish_artifact(_intervals(), tmp_path)
    path.write_bytes(path.read_bytes().replace(b"BTC-USDT-PERP", b"BCH-USDT-PERP"))
    with pytest.raises(UniverseArtifactError, match="键集合非法|digest 不符"):
        load_artifact(digest, tmp_path)


def test_load_rejects_schema_version_mismatch(tmp_path) -> None:
    document = build_document(_intervals())
    document["schema_version"] = 2
    payload = canonical_artifact_bytes(document)
    from alphamill.data_bridge.universe.canonical import sha256_prefixed

    digest = sha256_prefixed(payload)
    target = artifact_mod.artifact_path(digest, tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    with pytest.raises(UniverseArtifactError, match="schema_version 不支持"):
        load_artifact(digest, tmp_path)


def test_load_rejects_unknown_key_even_with_valid_digest(tmp_path) -> None:
    document = build_document(_intervals())
    document["members"][0]["universe_id"] = "sha256:" + "a" * 64
    # 故意用非严格编码器造一个「digest 自洽但 schema 非法」的 artifact
    payload = json.dumps(document, sort_keys=True, separators=(",", ":")).encode()
    from alphamill.data_bridge.universe.canonical import sha256_prefixed

    digest = sha256_prefixed(payload)
    target = artifact_mod.artifact_path(digest, tmp_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    with pytest.raises(UniverseArtifactError, match="键集合非法"):
        load_artifact(digest, tmp_path)


def test_load_missing_artifact_fails_closed(tmp_path) -> None:
    with pytest.raises(UniverseArtifactError, match="不可读"):
        load_artifact("sha256:" + "0" * 64, tmp_path)


def test_artifact_path_rejects_bad_digest(tmp_path) -> None:
    with pytest.raises(UniverseArtifactError, match="非法 universe digest"):
        artifact_mod.artifact_path("sha256:short", tmp_path)


def test_artifact_dir_is_lake_metadata(tmp_path) -> None:
    assert artifact_mod.artifact_dir(tmp_path) == tmp_path / "_metadata" / "universes"


# ---------- 时点语义 ----------


def test_universe_at_is_left_closed_right_open() -> None:
    ledger = ArtifactLedger(
        digest="sha256:" + "b" * 64,
        schema_version=1,
        members=(
            ArtifactMember(lake_pair="BTC-USDT-PERP", valid_from=START, valid_to=END),
            ArtifactMember(lake_pair="ETH-USDT-PERP", valid_from=START, valid_to=None),
        ),
    )
    assert ledger.universe_at(START) == frozenset({"BTC-USDT-PERP", "ETH-USDT-PERP"})
    assert ledger.universe_at(END) == frozenset({"ETH-USDT-PERP"})
    assert ledger.universe_at(datetime(2024, 1, 1, tzinfo=UTC)) == frozenset()


def test_universe_at_requires_timezone() -> None:
    ledger = ArtifactLedger(digest="sha256:" + "b" * 64, schema_version=1, members=())
    with pytest.raises(UniverseArtifactError, match="时区"):
        ledger.universe_at(datetime(2026, 1, 1))  # noqa: DTZ001 - 故意构造 naive 输入
