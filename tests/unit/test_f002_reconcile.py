"""F002 快照事务会话属性回归测试。"""

from datetime import UTC, datetime

from alphamill.data_bridge import reconcile


class _SnapshotCursor:
    def __init__(self):
        self.sql: list[str] = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, sql):
        self.sql.append(sql)

    def fetchone(self):
        return "123:456", datetime(2026, 9, 14, 1, tzinfo=UTC)


class _SnapshotConn:
    def __init__(self):
        self.cursor_obj = _SnapshotCursor()
        self.rollbacks = 0
        self.sessions: list[dict] = []

    def rollback(self):
        self.rollbacks += 1

    def set_session(self, **kwargs):
        self.sessions.append(kwargs)

    def cursor(self):
        return self.cursor_obj


def test_snapshot_transaction_sets_and_restores_session_defaults():
    conn = _SnapshotConn()
    assert reconcile.begin_snapshot_tx(conn) == ("123", "2026-09-14T01:00:00Z")
    assert conn.sessions[0] == {
        "isolation_level": "REPEATABLE READ",
        "readonly": True,
        "autocommit": False,
    }
    assert conn.cursor_obj.sql[0] == "BEGIN"

    reconcile.reset_snapshot_session(conn)
    assert conn.sessions[1] == {
        "isolation_level": "READ COMMITTED",
        "readonly": False,
        "autocommit": False,
    }
