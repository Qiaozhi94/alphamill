"""F002 快照事务会话属性回归测试。"""

from datetime import UTC, datetime

import psycopg2

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


class _BrokenConn:
    """连接已断开：任何清理调用都抛 psycopg2 错误。"""

    def rollback(self):
        raise psycopg2.OperationalError("server closed the connection unexpectedly")

    def set_session(self, **kwargs):  # pragma: no cover - rollback 先抛
        raise AssertionError("rollback 失败后不应继续 set_session")


def test_session_reset_does_not_raise_when_connection_is_already_dead():
    """F002-R3-04：finally 里的清理不得用二次异常取代真正的失败原因。"""
    reconcile.reset_snapshot_session(_BrokenConn())
