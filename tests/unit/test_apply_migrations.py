"""Migration runner regression tests."""

from pathlib import Path

import pytest

from tools.apply_migrations import (
    apply_migrations,
    assert_transactional,
    migration_files,
)

ROOT = Path(__file__).resolve().parents[2]


class _Cursor:
    def __init__(self, connection):
        self.connection = connection
        self.result = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        self.connection.statements.append((sql, params))
        if sql.startswith("SELECT 1 FROM schema_migrations"):
            self.result = (params[0],) if params[0] in self.connection.applied else None
        elif sql.startswith("INSERT INTO schema_migrations"):
            self.connection.applied.add(params[0])

    def fetchone(self):
        return self.result


class _Connection:
    def __init__(self):
        self.applied = set()
        self.statements = []
        self.commits = 0

    def cursor(self):
        return _Cursor(self)

    def commit(self):
        self.commits += 1


def test_migrations_apply_in_filename_order_and_are_idempotent(tmp_path: Path) -> None:
    (tmp_path / "004_nullable.sql").write_text("ALTER TABLE example;", encoding="utf-8")
    (tmp_path / "003_derivatives.sql").write_text("CREATE TABLE example;", encoding="utf-8")
    conn = _Connection()

    assert [path.name for path in migration_files(tmp_path)] == [
        "003_derivatives.sql",
        "004_nullable.sql",
    ]
    assert apply_migrations(conn, tmp_path) == ["003_derivatives.sql", "004_nullable.sql"]
    assert apply_migrations(conn, tmp_path) == []
    assert conn.applied == {"003_derivatives.sql", "004_nullable.sql"}


def test_non_transactional_statements_are_rejected_before_execution() -> None:
    for sql in (
        "CREATE INDEX CONCURRENTLY idx_x ON t (c);",
        "VACUUM ANALYZE t;",
        "ALTER SYSTEM SET work_mem = '64MB';",
    ):
        with pytest.raises(RuntimeError, match="非事务语句"):
            assert_transactional("900_bad.sql", sql)


def test_shipped_migrations_pass_the_transactional_guard() -> None:
    for path in migration_files():
        assert_transactional(path.name, path.read_text(encoding="utf-8"))


def test_initdb_and_runner_share_one_migration_ledger() -> None:
    """C402：全新库的 initdb 路径也要登记 schema_migrations，否则 runner 首跑会重放全部迁移。"""
    compose = (ROOT / "deployment/docker-compose.yml").read_text(encoding="utf-8")
    script = (ROOT / "deployment/initdb-apply-migrations.sh").read_text(encoding="utf-8")

    assert "../db/migrations:/docker-entrypoint-initdb.d/migrations:ro" in compose
    assert "initdb-apply-migrations.sh:/docker-entrypoint-initdb.d/02_apply_migrations.sh:ro" in (
        compose
    )
    # 旧的逐文件挂载会绕开账本，必须已经移除
    assert "/docker-entrypoint-initdb.d/02_derivatives_market_data.sql" not in compose
    assert "/docker-entrypoint-initdb.d/03_nullable_dryrun_metrics.sql" not in compose
    assert "CREATE TABLE IF NOT EXISTS schema_migrations" in script
    assert "INSERT INTO schema_migrations (version)" in script
