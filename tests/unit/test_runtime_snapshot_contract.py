"""Runtime snapshot SQL conversion regression tests."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_null_numeric_metrics_are_inserted_as_sql_null() -> None:
    script = (ROOT / "scripts/collect_runtime_snapshot.ps1").read_text(encoding="utf-8")
    function = script.split("function ConvertTo-SqlNumber", 1)[1].split("function Invoke-DbSql", 1)[0]

    assert 'return "NULL"' in function
    assert 'return "0"' not in function
