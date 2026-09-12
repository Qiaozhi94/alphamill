"""Apply versioned SQL migrations to a fresh or existing AlphaMill database.

Run explicitly after deploying a new application version:
    .venv/bin/python tools/apply_migrations.py

全新库在 Compose 的 initdb 阶段由 deployment/initdb-apply-migrations.sh 应用同一批
SQL 并登记同一个 schema_migrations 账本；本入口是 initdb 阶段已过的既有库的升级路径。
两条路径共用账本，因此 runner 在全新库上首跑是空操作（C402）。

对迁移文件的两条硬约束：

1. **必须幂等**——同一文件可能在两条路径上各执行一次（例如账本建立之前就手工跑过），
   所以一律用 ``CREATE TABLE/INDEX IF NOT EXISTS``、``ALTER TABLE IF EXISTS`` 等写法；
2. **不得包含非事务语句**——本 runner 在单个事务内整文件执行，``CREATE INDEX
   CONCURRENTLY``、``VACUUM``、``ALTER SYSTEM``、``CREATE DATABASE`` 等无法在事务块中
   运行。写了会被 :func:`assert_transactional` 提前拦下并给出可读报错，而不是在半路
   炸出 psycopg2 的原始异常（C403）。
"""

from __future__ import annotations

import os
import re
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


# 这些语句无法在事务块中执行；runner 整文件走单事务，故提前拦截（C403）。
NON_TRANSACTIONAL = (
    re.compile(r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+CONCURRENTLY\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+INDEX\s+CONCURRENTLY\b", re.IGNORECASE),
    re.compile(r"\bVACUUM\b", re.IGNORECASE),
    re.compile(r"\bALTER\s+SYSTEM\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+DATABASE\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+TABLESPACE\b", re.IGNORECASE),
)


def assert_transactional(version: str, sql: str) -> None:
    """迁移文件含非事务语句时给出可读报错，而不是在执行到一半才炸。"""
    hits = sorted({m.group(0).upper() for p in NON_TRANSACTIONAL for m in p.finditer(sql)})
    if hits:
        raise RuntimeError(
            f"{version} 含非事务语句 {hits}：本 runner 在单个事务内整文件执行。"
            "请把该语句拆到独立的运维步骤，或改用可在事务内执行的等价写法。"
        )


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
            sql = path.read_text(encoding="utf-8")
            assert_transactional(version, sql)
            cur.execute(sql)
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
