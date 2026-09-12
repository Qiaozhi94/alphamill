"""Apply versioned SQL migrations to a fresh or existing AlphaMill database.

Run explicitly after deploying a new application version:
    .venv/bin/python tools/apply_migrations.py

Fresh databases still receive the same SQL through Compose initdb mounts. This
runner is the upgrade path for databases whose initdb phase has already passed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = PROJECT_ROOT / "db" / "migrations"
DOTENV_FILE = PROJECT_ROOT / "deployment" / ".env"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from alphamill.data_bridge.collector.db_writer import db_connect  # noqa: E402


def _dotenv_values(path: Path = DOTENV_FILE) -> dict[str, str]:
    if not path.is_file():
        return {}
    values = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def load_dotenv(path: Path = DOTENV_FILE) -> None:
    for key, value in _dotenv_values(path).items():
        os.environ.setdefault(key, value)


def migration_files(migration_dir: Path = MIGRATION_DIR) -> list[Path]:
    return sorted(migration_dir.glob("*.sql"), key=lambda path: path.name)


def apply_migrations(conn, migration_dir: Path = MIGRATION_DIR) -> list[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    conn.commit()

    applied = []
    for path in migration_files(migration_dir):
        version = path.name
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM schema_migrations WHERE version = %s", (version,))
            if cur.fetchone():
                continue
            cur.execute(path.read_text(encoding="utf-8"))
            cur.execute("INSERT INTO schema_migrations (version) VALUES (%s)", (version,))
        conn.commit()
        applied.append(version)
    return applied


def main() -> int:
    load_dotenv()
    conn = db_connect()
    try:
        applied = apply_migrations(conn)
    finally:
        conn.close()
    print(f"migrations applied: {', '.join(applied) if applied else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
