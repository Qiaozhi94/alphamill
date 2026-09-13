"""NAS backup transfer regression tests."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_backup_uses_chunk_byte_bounds_and_archive_checksum() -> None:
    script = (ROOT / "deployment/backup-nas.sh").read_text(encoding="utf-8")

    assert "iflag=skip_bytes,count_bytes" in script
    assert 'nas_append_chunk "$src" "$pos" "$want"' in script
    assert "if ! nas_append_chunk" in script
    assert "have=0" in script
    assert "transfer_directory_to_nas reports reports" in script
    assert "transfer_directory_to_nas lake lake" in script
    assert 'md5sum "$archive"' in script
    assert "pg_restore --list" in script
    assert "StrictHostKeyChecking=yes" in script
    assert 'UserKnownHostsFile="$NAS_KNOWN_HOSTS"' in script
    assert 'ssh-keygen -F "$NAS_HOST"' in script
    assert "StrictHostKeyChecking=no" not in script
    assert 'if ! ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST"' in script
    assert 'log "FATAL: $remote_dir 远端解包失败"' in script


def test_backup_service_start_limit_directives_present():
    """T019 回归：注释声称「最多 3 次」必须由显式指令支撑，否则不生效。"""
    service = (ROOT / "deployment/alphamill-backup.service").read_text(encoding="utf-8")
    assert "StartLimitIntervalSec=" in service
    assert "StartLimitBurst=3" in service
    assert "Restart=on-failure" in service and "RestartSec=15min" in service
