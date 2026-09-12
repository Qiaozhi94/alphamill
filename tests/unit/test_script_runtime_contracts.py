"""Runtime-level checks for the F001 PowerShell and shell script contracts."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_f001_shell_scripts_parse() -> None:
    for name in ("deployment/backup-nas.sh", "deployment/f001-backfill-supervisor.sh"):
        subprocess.run(["bash", "-n", str(ROOT / name)], check=True)


def test_nas_append_chunk_executes_with_stub_ssh(tmp_path: Path) -> None:
    script = (ROOT / "deployment/backup-nas.sh").read_text(encoding="utf-8")
    match = re.search(r"nas_append_chunk\(\) \{.*?\n\}", script, flags=re.DOTALL)
    assert match is not None
    source = tmp_path / "source.bin"
    received = tmp_path / "received.bin"
    source.write_bytes(b"abc")

    driver = f"""
set -euo pipefail
SSH_OPTS=()
NAS_USER=test
NAS_HOST=localhost
ssh() {{ cat > {received}; }}
{match.group(0)}
nas_append_chunk {source} 0 3 /remote
cmp {source} {received}
"""
    subprocess.run(["bash", "-c", driver], check=True)


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell 7 unavailable")
def test_invoke_db_check_rejects_scalar_zero() -> None:
    script_path = (ROOT / "deployment/verify.ps1").as_posix()
    command = f"""
$source = [IO.File]::ReadAllText('{script_path}')
$start = $source.IndexOf('function Invoke-DbCheck')
$end = $source.IndexOf('Write-Step \"Docker Compose services\"')
function Write-Step {{ param([string]$Message) }}
$ComposeFile = 'compose.yml'
$dbUser = 'quant'
$dbName = 'quant'
Invoke-Expression $source.Substring($start, $end - $start)
function docker {{ $global:LASTEXITCODE = 0; '0' }}
try {{
    Invoke-DbCheck 'mutation' 'SELECT 0' -ExpectPass
    exit 1
}} catch {{
    if ($_.Exception.Message -notmatch 'expected PASS') {{ exit 2 }}
    exit 0
}}
"""
    subprocess.run(["pwsh", "-NoProfile", "-Command", command], check=True)


@pytest.mark.skipif(shutil.which("pwsh") is None, reason="PowerShell 7 unavailable")
def test_snapshot_schema_check_rejects_missing_nullable_columns() -> None:
    script_path = (ROOT / "scripts/collect_runtime_snapshot.ps1").as_posix()
    command = f"""
$source = [IO.File]::ReadAllText('{script_path}')
$start = $source.IndexOf('$schemaCheck = @"')
$end = $source.IndexOf('$freqtradeUser =')
function Invoke-DbScalar {{ param([string]$Sql); '0' }}
try {{
    Invoke-Expression $source.Substring($start, $end - $start)
    exit 1
}} catch {{
    if ($_.Exception.Message -notmatch 'schema is missing or unknown metrics are not nullable') {{
        exit 2
    }}
    exit 0
}}
"""
    subprocess.run(["pwsh", "-NoProfile", "-Command", command], check=True)
