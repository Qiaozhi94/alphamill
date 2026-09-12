"""deployment/verify.ps1 environment configuration regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_verify_reads_database_identity_from_dotenv() -> None:
    script = (ROOT / "deployment/verify.ps1").read_text(encoding="utf-8")

    assert "$dbUser" in script
    assert "$dbName" in script
    assert "psql -U quant -d quant" not in script
