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
