"""F001 supervisor portability and fail-closed contract tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_supervisor_has_portable_root_env_and_fail_closed_shell_options() -> None:
    script = (ROOT / "deployment/f001-backfill-supervisor.sh").read_text(encoding="utf-8")

    assert "set -euo pipefail" in script
    assert 'REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"' in script
    assert "cd /home/georg/projects/alphamill" not in script
    assert 'psql -U "$DB_USER" -d "$DB_NAME"' in script
    assert "10.31.0.254:7890" not in script
    assert 'PYTHONPATH="$REPO_ROOT/src"' in script
    assert (
        'BACKFILL_SYMBOLS="${SYMBOLS:-BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT}"'
        in script
    )
    assert "EXPECTED_SYMBOL_COUNT" in script
    assert "status IN ('complete', 'unavailable')" in script
    assert 'DERIVATIVES_SYMBOLS="${DERIVATIVES_SYMBOLS:-$BACKFILL_SYMBOLS}"' in script
    assert "${DERIVATIVES_SYMBOLS:-$SYMBOLS}" not in script
