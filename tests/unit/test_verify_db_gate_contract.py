"""Database gate fail-closed regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_scalar_database_assertions_require_pass_value() -> None:
    script = (ROOT / "deployment/verify.ps1").read_text(encoding="utf-8")

    assert "[switch]$ExpectPass" in script
    assert "expected PASS (1)" in script
    assert script.count('"@ -ExpectPass') >= 10
    assert "matching_rows" in script
    abnormal_check = script.split('Invoke-DbCheck "1m abnormal price move check"', 1)[1]
    assert (
        '"@ -ExpectPass'
        not in abnormal_check.split('Invoke-DbCheck "Latest candle freshness"', 1)[0]
    )
    assert '"@ -ExpectPass' in script.split('Invoke-DbCheck "Latest candle freshness"', 1)[1]
    assert (
        '"@ -ExpectPass' in script.split('Invoke-DbCheck "Continuous aggregate row counts"', 1)[1]
    )
