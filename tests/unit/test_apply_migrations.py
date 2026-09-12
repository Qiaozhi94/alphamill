"""Migration runner regression tests."""

from pathlib import Path

from tools.apply_migrations import apply_migrations, migration_files


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
