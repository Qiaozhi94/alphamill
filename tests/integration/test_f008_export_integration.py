"""T017 与 `AC-009`：台账 artifact 内容寻址、准入三步顺序与导出清单过滤。

真实库 + scratch 湖：准入三步（库追加 → artifact 发布 → 写准入记录）的落点逐一断言，
导出侧 `admitted=` / `universe_filter=` 过滤后 manifest 的 `pairs` 收窄，而 `symbol_map`
保持全量（「库里有什么」与「研究能用什么」允许不等）。
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from conftest import D4, export_symbol_map_for, seed_f002_data

from alphamill.data_bridge import manifest as mf
from alphamill.data_bridge import symbol_map as symbol_map_mod
from alphamill.data_bridge.exporter import export_dataset
from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe.admission import (
    STEP_ADMISSION,
    STEP_ARTIFACT,
    STEP_LEDGER,
    admit_pair,
    gate_and_admit,
)
from alphamill.data_bridge.universe.definition import (
    build_definition,
    freeze_definition,
    load_definition,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import QualityGateError
from alphamill.data_bridge.universe.membership import load_membership, materialize_intervals
from alphamill.data_bridge.universe.quality_gate import (
    VERDICT_ACTIVE,
    VERDICT_QUARANTINED,
    current_verdicts,
)

pytestmark = pytest.mark.integration

WINDOW_START = datetime(2026, 9, 1, tzinfo=UTC)
WINDOW_END = datetime(2026, 9, 4, tzinfo=UTC)

from tests.f008_fixtures import criteria_for, market, snapshot  # noqa: E402


@pytest.fixture()
def seeded(f008_conn, f002_lake):
    """F002 种子数据 + 迁移 005 + scratch 湖（symbol map 指向 tmp，绝不碰真实 lake/）。"""
    seed_f002_data(f008_conn)
    export_symbol_map_for(f008_conn, f002_lake)
    return f002_lake


def _frozen_definition(tmp_path, *, bases=("BTC", "ETH")) -> str:
    criteria = criteria_for(turnover_rank_top_n=10)
    definition = build_definition(
        criteria, evaluate(snapshot(*[market(base) for base in bases]), criteria)
    )
    write_definition(definition, tmp_path / "lake")
    freeze_definition(definition.universe_id, frozen_by="tester", lake_root=tmp_path / "lake")
    return definition.universe_id


def _active_result(db_symbol: str, lake_pair: str):
    """合成 ACTIVE 判定：本文件验的是准入**联动与导出过滤**，门禁判定本身由
    `test_f008_quality_gate.py` 的四类 fixture 覆盖。"""
    from alphamill.data_bridge.universe.quality_gate import PairGateResult

    return PairGateResult(
        db_symbol=db_symbol,
        lake_pair=lake_pair,
        exchange="binance",
        market_type="spot",
        verdict=VERDICT_ACTIVE,
        reason_code=None,
        metrics={"synthetic": True},
    )


def test_admit_pair_runs_three_steps_in_order(seeded, f008_conn, tmp_path) -> None:
    universe_id = _frozen_definition(tmp_path)
    definition = load_definition(universe_id, tmp_path / "lake")
    result = _active_result("BTC/USDT", "BTC-USDT")

    outcome = admit_pair(
        f008_conn,
        definition=definition,
        result=result,
        lake_root=tmp_path / "lake",
        hostname="qiaozhi-gp",
        listed_at=WINDOW_START,
    )
    assert outcome.steps == (STEP_LEDGER, STEP_ARTIFACT, STEP_ADMISSION)
    assert outcome.artifact_digest is not None

    rows = load_membership(f008_conn)
    # 同一 db_symbol 写两条湖内命名空间：ohlcv_1m 用 spot，derivatives_* 用 perp
    assert sorted((row.market_type, row.lake_pair) for row in rows) == [
        ("perp", "BTC-USDT-PERP"),
        ("spot", "BTC-USDT"),
    ]
    assert {row.reason for row in rows} == {"listed"}
    ledger = artifact_mod.load_artifact(outcome.artifact_digest, tmp_path / "lake")
    assert ledger.universe_at(WINDOW_START + timedelta(days=1)) == frozenset(
        {"BTC-USDT", "BTC-USDT-PERP"}
    )
    verdicts = current_verdicts(f008_conn, universe_id=universe_id)
    assert verdicts["BTC-USDT"].verdict == VERDICT_ACTIVE


def test_admit_pair_is_idempotent_across_gate_reruns(seeded, f008_conn, tmp_path) -> None:
    """回归（2026-09-24）：门禁复跑不得因重复追加台账行而中断。

    第二次 `gate` 曾在 BTC 上报「`universe_membership` 追加序非法」整轮中断——库侧
    触发器按设计拒绝重复/回填 `valid_from`，所以幂等必须由调用方按
    `(lake_pair, market_type, valid_from)` 去重（`append_membership` 的契约）。
    """
    universe_id = _frozen_definition(tmp_path)
    definition = load_definition(universe_id, tmp_path / "lake")
    result = _active_result("BTC/USDT", "BTC-USDT")
    kwargs = {
        "definition": definition,
        "result": result,
        "lake_root": tmp_path / "lake",
        "hostname": "qiaozhi-lt",
        "listed_at": WINDOW_START,
    }

    first = admit_pair(f008_conn, **kwargs)
    second = admit_pair(f008_conn, **kwargs)

    assert second.steps == (STEP_LEDGER, STEP_ARTIFACT, STEP_ADMISSION)
    assert second.artifact_digest == first.artifact_digest
    rows = load_membership(f008_conn)
    assert sorted((row.market_type, row.lake_pair) for row in rows) == [
        ("perp", "BTC-USDT-PERP"),
        ("spot", "BTC-USDT"),
    ], "复跑不得产生重复台账行"


def test_quarantined_pair_records_verdict_without_touching_ledger(
    seeded, f008_conn, tmp_path
) -> None:
    universe_id = _frozen_definition(tmp_path)
    definition = load_definition(universe_id, tmp_path / "lake")
    from alphamill.data_bridge.universe.quality_gate import PairGateResult

    failed = PairGateResult(
        db_symbol="ETH/USDT",
        lake_pair="ETH-USDT-PERP",
        exchange="binance",
        market_type="perp",
        verdict=VERDICT_QUARANTINED,
        reason_code="missing_ratio_exceeded",
        metrics={"missing_ratio": 0.5},
    )
    outcome = admit_pair(
        f008_conn, definition=definition, result=failed, lake_root=tmp_path / "lake"
    )
    assert outcome.steps == (STEP_ADMISSION,)
    assert outcome.artifact_digest is None
    assert load_membership(f008_conn) == []
    assert not artifact_mod.artifact_dir(tmp_path / "lake").exists()
    assert current_verdicts(f008_conn)["ETH-USDT-PERP"].verdict == VERDICT_QUARANTINED


def test_gate_and_admit_quarantines_sparse_seed_data(seeded, f008_conn, tmp_path) -> None:
    """真实门禁跑在稀疏种子数据上必然判隔离（不写台账、只留判定）。"""
    universe_id = _frozen_definition(tmp_path)
    outcomes = gate_and_admit(
        f008_conn,
        definition=load_definition(universe_id, tmp_path / "lake"),
        window_start=WINDOW_START,
        window_end=WINDOW_END,
        pairs=["BTC/USDT"],
        lake_root=tmp_path / "lake",
        hostname="qiaozhi-gp",
        require_backfill_complete=False,
    )
    assert [item.verdict for item in outcomes] == [VERDICT_QUARANTINED]
    assert outcomes[0].steps == (STEP_ADMISSION,)
    assert load_membership(f008_conn) == []
    with pytest.raises(QualityGateError, match="不在宇宙定义内"):
        gate_and_admit(
            f008_conn,
            definition=load_definition(universe_id, tmp_path / "lake"),
            window_start=WINDOW_START,
            window_end=WINDOW_END,
            pairs=["DOGE/USDT"],
            lake_root=tmp_path / "lake",
        )


def test_export_pairs_are_filtered_while_symbol_map_stays_full(seeded, f008_conn, tmp_path) -> None:
    """导出清单 = 台账可交易 ∩ ACTIVE；`symbol_map` 保持全量（允许不等）。"""
    lake = seeded
    unfiltered = export_dataset(
        "ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f008_conn, lake_root=lake
    )
    baseline = mf.load_manifest(lake, "ohlcv_1m", unfiltered["data_version"])
    assert set(baseline["pairs"]) == {"BTC-USDT", "ETH-USDT"}

    filtered = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end=f"{D4}T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        admitted={"BTC-USDT"},
    )
    manifest = mf.load_manifest(lake, "ohlcv_1m", filtered["data_version"])
    assert set(manifest["pairs"]) == {"BTC-USDT"}
    assert all(
        partition["logical_partition_key"]["pair"] == "BTC-USDT"
        for partition in manifest["partitions"]
    )
    # symbol_map 不参与过滤：它回答「库里有什么」——被排除出导出清单的 ETH 仍在，
    # 派生品表的 perp 命名空间也仍在（导出清单回答的是「研究能用什么」）
    frame = symbol_map_mod.load_symbol_map(manifest["symbol_map_digest"], lake)
    pairs = set(frame["lake_pair"])
    assert {"BTC-USDT", "ETH-USDT", "BTC-USDT-PERP"} <= pairs
    assert set(manifest["pairs"]) < pairs  # 导出清单是真子集


def test_universe_filter_flag_matches_explicit_admitted(seeded, f008_conn, tmp_path) -> None:
    """`universe_filter=True` 与显式给出同一准入集合等价（F008 FR-006 的操作入口）。"""
    lake = seeded
    universe_id = _frozen_definition(tmp_path)
    admit_pair(
        f008_conn,
        definition=load_definition(universe_id, tmp_path / "lake"),
        result=_active_result("BTC/USDT", "BTC-USDT"),
        lake_root=tmp_path / "lake",
        hostname="qiaozhi-gp",
        listed_at=WINDOW_START,
    )
    summary = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end=f"{D4}T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        universe_filter=True,
    )
    manifest = mf.load_manifest(lake, "ohlcv_1m", summary["data_version"])
    assert set(manifest["pairs"]) == {"BTC-USDT"}


def _insert_ohlcv_row(conn, symbol: str, day: str) -> None:
    """补一行 1m 种子：让该 pair 在基线的活跃跨度里出现「跨日缺口」（供 skipped 继承路径入镜）。"""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO ohlcv_1m (time, exchange, symbol, open, high, low, close, volume)"
            " VALUES (%s,'binance',%s,100,101,99,100,1)",
            (datetime.fromisoformat(f"{day}T00:00:00+00:00"), symbol),
        )
    conn.commit()


def test_universe_filter_tolerates_flags_of_excluded_pairs(seeded, f008_conn, tmp_path) -> None:
    """回归（检视 C2 / R1-002）：被排除 pair 的未解决质量标记不得让整轮导出 FATAL。

    种子数据在 `ohlcv_quality_flags` 里给 **BTC/USDT** 留了一条未解决标记，而本次
    `--universe-filter` 算出的准入集合只有 ETH-USDT（`admit_pair` 真实落台账 + 准入判定）。
    若把按准入集合收窄后的映射交给 `quality_flags()`，被排除的 BTC 取不到 lake_pair →
    `DataBridgeError` → 整轮导出 FATAL、清单不发布。质量标记是**全湖记账**（回答「湖里哪些分区
    有问题」），按准入集合收窄的只有导出分区；被排除者的标记必须仍记在它自己名下，不冒充准入 pair。
    """
    lake = seeded
    universe_id = _frozen_definition(tmp_path)
    admit_pair(
        f008_conn,
        definition=load_definition(universe_id, tmp_path / "lake"),
        result=_active_result("ETH/USDT", "ETH-USDT"),
        lake_root=tmp_path / "lake",
        hostname="qiaozhi-gp",
        listed_at=WINDOW_START,
    )

    summary = export_dataset(
        "ohlcv_1m",
        mode="full",
        window_end=f"{D4}T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        universe_filter=True,
    )
    assert summary["status"] == "valid", summary
    manifest = mf.load_manifest(lake, "ohlcv_1m", summary["data_version"])
    assert set(manifest["pairs"]) == {"ETH-USDT"}, "准入集合确实只含被准入的那一对"
    assert manifest["quality"]["flagged_partitions"] == ["binance/BTC-USDT/2026-09-01"]
    assert manifest["quality"]["unresolved_total"] == 1
    assert all("ETH-USDT" not in item for item in manifest["quality"]["flagged_partitions"])


def test_incremental_universe_filter_does_not_mark_excluded_pairs_skipped(
    seeded, f008_conn, tmp_path
) -> None:
    """回归（检视 C5 / R1-005）：策略排除的 pair 日期不得被写成「空单元格」进 `skipped`。

    基线全量版本里 BTC-USDT 与 ETH-USDT 都有分区、且各有一条真实缺口（D2）→ 基线 `skipped`
    里两条 pair 都在，能把**继承**路径也照进来。随后只准入 BTC-USDT 跑一次增量（窗口 = 基线
    最大日期 +1 = D4，源库那天无数据）：若把未收窄的基线条目/基线 skipped 交给
    `empty_cell_keys` / `synthesize_skipped`，被排除的 ETH 维度会按窗口日期判缺 →
    `ETH-USDT/D4` 新进 skipped，基线里的 `ETH-USDT/D2` 也被原样继承——skipped 的语义是
    「本该有分区却缺」，把策略排除说成数据缺口会逐版本累积，并在数据未变时因 skipped 变化
    白白发布新版本。
    """
    lake = seeded
    _insert_ohlcv_row(f008_conn, "ETH/USDT", "2026-09-03")
    universe_id = _frozen_definition(tmp_path)
    baseline = export_dataset(
        "ohlcv_1m", mode="full", window_end=f"{D4}T00:00:00Z", conn=f008_conn, lake_root=lake
    )
    baseline_manifest = mf.load_manifest(lake, "ohlcv_1m", baseline["data_version"])
    assert set(baseline_manifest["pairs"]) == {"BTC-USDT", "ETH-USDT"}
    assert {"exchange": "binance", "pair": "ETH-USDT", "date": "2026-09-02"} in (
        baseline_manifest["skipped"]
    ), "前置条件：基线里被排除 pair 有可继承的 skipped 键"

    admit_pair(
        f008_conn,
        definition=load_definition(universe_id, tmp_path / "lake"),
        result=_active_result("BTC/USDT", "BTC-USDT"),
        lake_root=tmp_path / "lake",
        hostname="qiaozhi-lt",
        listed_at=WINDOW_START,
    )
    summary = export_dataset(
        "ohlcv_1m",
        mode="incremental",
        window_end="2026-09-05T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        universe_filter=True,
    )
    assert summary["status"] == "valid", summary
    manifest = mf.load_manifest(lake, "ohlcv_1m", summary["data_version"])
    skipped = manifest["skipped"]
    assert [item for item in skipped if item.get("pair") == "ETH-USDT"] == [], (
        f"被排除 pair 的日期被写成空单元格: {skipped}"
    )
    # 窗口确实判过缺：准入 pair 自己缺席的日期照旧入档（不是「过滤后整片不判」）
    assert {"exchange": "binance", "pair": "BTC-USDT", "date": "2026-09-04"} in skipped
    assert {"exchange": "binance", "pair": "BTC-USDT", "date": "2026-09-02"} in skipped
    # 排除 ≠ 删历史：被排除 pair 的湖分区按 F002 语义原样继承
    assert {"exchange": "binance", "pair": "ETH-USDT", "date": "2026-09-01"} in [
        partition["logical_partition_key"] for partition in manifest["partitions"]
    ]


def test_admitted_filter_is_noop_for_datasets_without_pair_partition(
    seeded, f008_conn, tmp_path
) -> None:
    """回归（2026-09-24）：非 pair 分区的 dataset 不得因准入过滤而崩。

    `signals_log` 的分区键只有 `date`（`symbol_map_enabled=False`），`discover_cells()` 给出的
    单元格形状是 `(date,)`；过滤代码若硬取 `cell[1]` 就越界——真实全量导出实测
    `IndexError: tuple index out of range`，整轮导出在 `ohlcv_1m` 之前中断。
    这类 dataset 没有 `lake_pair` 维度，准入过滤对它保持原行为（不静默改数据）。
    """
    lake = seeded
    summary = export_dataset(
        "signals_log",
        mode="full",
        window_end=f"{D4}T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        admitted={"BTC-USDT"},
    )
    assert summary["status"] in {"valid", "no_op"}, summary
    manifest = mf.load_manifest(lake, "signals_log", summary["data_version"])
    # 无 pair 维度：manifest 不带 pairs 收窄语义，分区不得因过滤被丢
    assert int(summary["partitions"]) == len(manifest["partitions"])


def test_artifact_publish_is_stable_and_old_digest_survives(seeded, f008_conn, tmp_path) -> None:
    """AC-009：同内容同 digest 且逐字节一致；内容变化得新 digest，旧 digest 仍可读。"""
    from alphamill.data_bridge.universe.membership import MembershipRow, append_membership

    lake = tmp_path / "lake"
    universe_id = _frozen_definition(tmp_path)
    append_membership(
        f008_conn,
        [
            MembershipRow(
                exchange="binance",
                market_type="spot",
                db_symbol="BTC/USDT",
                lake_pair="BTC-USDT",
                valid_from=WINDOW_START,
                reason="listed",
                universe_id=universe_id,
            )
        ],
    )
    first_digest, first_path = artifact_mod.publish_artifact(
        materialize_intervals(load_membership(f008_conn)), lake
    )
    again_digest, _ = artifact_mod.publish_artifact(
        materialize_intervals(load_membership(f008_conn)), lake
    )
    assert again_digest == first_digest
    assert first_path.read_bytes() == artifact_mod.canonical_artifact_bytes(
        artifact_mod.build_document(materialize_intervals(load_membership(f008_conn)))
    )

    append_membership(
        f008_conn,
        [
            MembershipRow(
                exchange="binance",
                market_type="spot",
                db_symbol="ETH/USDT",
                lake_pair="ETH-USDT",
                valid_from=WINDOW_START,
                reason="listed",
                universe_id=universe_id,
            )
        ],
    )
    second_digest, _ = artifact_mod.publish_artifact(
        materialize_intervals(load_membership(f008_conn)), lake
    )
    assert second_digest != first_digest
    assert artifact_mod.load_artifact(first_digest, lake).universe_at(WINDOW_START) == frozenset(
        {"BTC-USDT"}
    )


@pytest.mark.xfail(
    strict=True,
    reason="依赖 F003（feat/F003-alphagen-vendor 未并入 main）的 "
    "factor_factory.generators.universe.load_explicit_universe；F003 落地后 XPASS 转红，"
    "强制摘除本标记并真跑（tasks.md §4 已登记）",
)
def test_artifact_loads_with_f003_explicit_universe_consumer(tmp_path) -> None:
    """AC-009 的跨消费者断言：产物必须能被 F003 的显式宇宙加载器直接加载。"""
    from factor_factory.generators.universe import (
        load_explicit_universe,  # type: ignore[import-not-found]
    )

    from alphamill.data_bridge.universe.membership import TradabilityInterval

    intervals = [TradabilityInterval(lake_pair="BTC-USDT", valid_from=WINDOW_START, valid_to=None)]
    digest, path = artifact_mod.publish_artifact(intervals, tmp_path)
    ledger = load_explicit_universe(path, expected_digest=digest, expected_schema_version=1)
    assert ledger.universe_at(WINDOW_START + timedelta(minutes=1)) == frozenset({"BTC-USDT-PERP"})


def test_incremental_universe_filter_keeps_skipped_for_non_pair_dataset(
    seeded, f008_conn, tmp_path
) -> None:
    """回归（检视第 2 轮 N1）：非 pair 分区 dataset 的基线 `skipped` 不得被准入过滤清空。

    `signals_log` 的逻辑键只有 `date`、**没有 `pair`**：`_admitted_only` 若按「pair 不在准入
    集合内」一刀切，会把它的缺口账整片丢掉——`manifest.skipped` 静默缩水，`content_changed`
    还会因此白发布一个版本（缺口账是「本该有分区却缺」，不是策略排除）。修复前本用例必红。
    """
    lake = seeded
    with f008_conn.cursor() as cur:
        cur.execute(
            "INSERT INTO signals_log (time, exchange, symbol, source, signal_type, confidence,"
            " metadata, latest_candle, expected_return, volatility, direction_prob,"
            " realized_return_60m, evaluated_at)"
            " VALUES (%s,'binance','BTC/USDT','placeholder','buy',0.9,'{}'::jsonb,"
            " %s, 0.01, 0.2, 0.6, NULL, NULL)",  # D4 一行 → 全量 span D1..D4 里 D3 成缺口
            (datetime(2026, 9, 4, 12, tzinfo=UTC), datetime(2026, 9, 4, 9, tzinfo=UTC)),
        )
    f008_conn.commit()

    baseline = export_dataset(
        "signals_log",
        mode="full",
        window_end="2026-09-05T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
    )
    baseline_manifest = mf.load_manifest(lake, "signals_log", baseline["data_version"])
    assert {"date": "2026-09-03"} in baseline_manifest["skipped"], "前置条件：基线要有可继承的缺口"

    summary = export_dataset(
        "signals_log",
        mode="incremental",
        window_end="2026-09-06T00:00:00Z",
        conn=f008_conn,
        lake_root=lake,
        admitted={"BTC-USDT"},  # 非空准入集合即触发旧缺陷
    )
    manifest = mf.load_manifest(lake, "signals_log", summary["data_version"])
    assert {"date": "2026-09-03"} in manifest["skipped"], (
        f"非 pair 分区数据集的基线缺口被准入过滤清空: {manifest['skipped']}"
    )
    assert {"date": "2026-09-05"} in manifest["skipped"], "本轮窗口缺口照旧入档"
