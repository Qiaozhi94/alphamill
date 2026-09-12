"""Runtime snapshot SQL conversion regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_null_numeric_metrics_are_inserted_as_sql_null() -> None:
    script = (ROOT / "scripts/collect_runtime_snapshot.ps1").read_text(encoding="utf-8")
    function = script.split("function ConvertTo-SqlNumber", 1)[1].split("function Invoke-DbSql", 1)[
        0
    ]

    assert 'return "NULL"' in function
    assert 'return "0"' not in function


def test_snapshot_schema_allows_unknown_numeric_metrics() -> None:
    init_sql = (ROOT / "db/init.sql").read_text(encoding="utf-8")
    migration = (ROOT / "db/migrations/004_nullable_dryrun_metrics.sql").read_text(
        encoding="utf-8"
    )

    for column in (
        "total_stake",
        "trade_count",
        "closed_trade_count",
        "profit_all_abs",
        "profit_all_pct",
        "winrate",
        "max_drawdown_abs",
        "max_drawdown_ratio",
    ):
        assert f"{column} DROP NOT NULL" in migration
        assert f"{column} DROP DEFAULT" in migration
    snapshot_ddl = init_sql.split("CREATE TABLE IF NOT EXISTS dryrun_runtime_snapshots", 1)[1]
    snapshot_ddl = snapshot_ddl.split("CREATE INDEX", 1)[0]
    assert "winrate             DOUBLE PRECISION NOT NULL" not in snapshot_ddl
