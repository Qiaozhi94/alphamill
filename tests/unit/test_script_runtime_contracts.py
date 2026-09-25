"""Runtime-level checks for the F001 PowerShell and shell script contracts."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
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


def _run_f008_backfill_launcher(tmp_path: Path, **env_overrides: str) -> list[str]:
    """真跑 `scripts/f008-backfill.sh`（stub .env + stub interpreter），返回 CLI 收到的 argv。"""
    repo = tmp_path / "repo"
    prod = tmp_path / "prod"
    (repo / ".venv/bin").mkdir(parents=True)
    (prod / "deployment").mkdir(parents=True)
    # 生产 deployment/.env 的真相：`FETCH_LIMIT=5` 属于采集器，回填不得继承。
    (prod / "deployment/.env").write_text("FETCH_LIMIT=5\n", encoding="utf-8")
    captured = tmp_path / "argv.txt"
    stub_python = repo / ".venv/bin/python"
    stub_python.write_text(
        "#!/usr/bin/env bash\n"
        'printf \'%s\\n\' "$@" > "$F008_ARGV_CAPTURE.tmp"\n'
        'mv "$F008_ARGV_CAPTURE.tmp" "$F008_ARGV_CAPTURE"\n',
        encoding="utf-8",
    )
    stub_python.chmod(0o755)
    env = {
        **os.environ,
        "REPO_F008": str(repo),
        "PROD": str(prod),
        "F008_ARGV_CAPTURE": str(captured),
    }
    env.pop("FETCH_LIMIT", None)
    env.pop("BACKFILL_FETCH_LIMIT", None)
    env.update(env_overrides)

    result = subprocess.run(
        ["bash", str(ROOT / "scripts/f008-backfill.sh"), "1"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    # 启动器把回填 nohup 到后台，故轮询等待 stub 落盘。
    deadline = time.monotonic() + 10.0
    while not captured.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert captured.exists(), f"stub interpreter 未被调用：\n{result.stdout}\n{result.stderr}"
    return captured.read_text(encoding="utf-8").splitlines()


def _fetch_limit(argv: list[str]) -> str:
    assert argv[:3] == ["-m", "alphamill.data_bridge.universe", "backfill"], argv
    assert argv.count("--fetch-limit") == 1, argv
    return argv[argv.index("--fetch-limit") + 1]


def test_f008_backfill_launcher_ignores_collector_fetch_limit(tmp_path: Path) -> None:
    """回归（partial-symmetric-fix）：.env/父进程的 `FETCH_LIMIT=5` 不得再传到 CLI。

    事故：`f008-backfill.sh` 用 `FETCH_LIMIT` 这个与采集器同名的变量取值，被 `set -a;
    . deployment/.env` 打成 5 根/请求（吞吐 1/200）；分片执行器改了，启动器没同步。
    """
    argv = _run_f008_backfill_launcher(tmp_path, FETCH_LIMIT="5")

    assert _fetch_limit(argv) == "1000"


def test_f008_backfill_launcher_honours_backfill_fetch_limit_override(tmp_path: Path) -> None:
    """`BACKFILL_FETCH_LIMIT` 是启动器唯一的速度旋钮（与分片执行器同名、同默认值）。"""
    argv = _run_f008_backfill_launcher(tmp_path, BACKFILL_FETCH_LIMIT="500")

    assert _fetch_limit(argv) == "500"
