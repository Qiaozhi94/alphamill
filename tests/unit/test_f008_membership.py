"""T007/T008 与 `AC-007`/`AC-008`：只追加台账、`universe_at(T)` 与 initial_seed 补种。

单元层锁三件事：
1. 状态迁移行 → 可交易区间的派生规则（退市 = 追加一行，不改写历史行）；
2. `members_at(T)` 的时点语义与「区间并集判定」逐点一致（库侧与 artifact 侧同源）；
3. 写入面**只有 INSERT**：任何 UPDATE/DELETE 语句出现在模块里即判红（追加语义的回归锁）。
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from alphamill.data_bridge.universe import membership as membership_mod
from alphamill.data_bridge.universe.errors import MembershipError
from alphamill.data_bridge.universe.membership import (
    MembershipRow,
    append_membership,
    materialize_intervals,
    members_at,
    seed_initial_members,
    validate_row,
)

T1 = datetime(2026, 1, 1, tzinfo=UTC)
T2 = datetime(2026, 6, 1, tzinfo=UTC)
T3 = datetime(2026, 9, 1, tzinfo=UTC)
T0 = datetime(2025, 12, 1, tzinfo=UTC)
MID = datetime(2026, 3, 1, tzinfo=UTC)


def _row(pair: str, start: datetime, reason: str, *, end: datetime | None = None) -> MembershipRow:
    return MembershipRow(
        exchange="binance",
        market_type="perp",
        db_symbol=pair.replace("-PERP", ""),
        lake_pair=pair,
        valid_from=start,
        valid_to=end,
        reason=reason,
        universe_id="sha256:" + "a" * 64,
    )


# ---------- 应用层写入闸 ----------


def test_validate_row_rejects_bad_reason_and_windows() -> None:
    assert "reason 非法" in validate_row(_row("BTC-USDT-PERP", T1, "admitted"))
    assert "valid_to" in validate_row(_row("BTC-USDT-PERP", T1, "listed", end=T1))
    naive = MembershipRow(
        exchange="binance",
        market_type="perp",
        db_symbol="BTC/USDT",
        lake_pair="BTC-USDT-PERP",
        valid_from=datetime(2026, 1, 1),  # noqa: DTZ001 - 故意构造 naive 输入
        reason="listed",
        universe_id="sha256:" + "a" * 64,
    )
    assert "时区" in validate_row(naive)
    assert validate_row(_row("BTC-USDT-PERP", T1, "listed")) is None


def test_append_membership_rejects_invalid_before_touching_db() -> None:
    conn = _Conn()
    with pytest.raises(MembershipError):
        append_membership(conn, [_row("BTC-USDT-PERP", T1, "admitted")])
    assert conn.statements == []


def test_module_has_no_update_or_delete_path() -> None:
    """AC-008 的回归锁：写入面只有 INSERT，历史区间没有原地改写路径。"""
    import inspect

    source = inspect.getsource(membership_mod).upper()
    assert "UPDATE " not in source.replace("UNIVERSE_MEMBERSHIP_NO_MUTATION", "")
    assert "DELETE " not in source.replace("DELETE PATH", "")
    assert "INSERT INTO UNIVERSE_MEMBERSHIP" in source


def test_append_membership_inserts_every_row_and_commits() -> None:
    conn = _Conn()
    written = append_membership(conn, [_row("BTC-USDT-PERP", T1, "listed")])
    assert written == 1
    assert conn.commits == 1
    sql = conn.statements[0][0].upper()
    assert sql.strip().startswith("INSERT INTO UNIVERSE_MEMBERSHIP")


# ---------- 区间派生 ----------


def test_delisting_appends_a_transition_and_closes_the_interval() -> None:
    rows = [_row("BTC-USDT-PERP", T1, "listed"), _row("BTC-USDT-PERP", T2, "delisted")]
    intervals = materialize_intervals(rows)
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(T1, T2)]


def test_open_listed_state_stays_open() -> None:
    intervals = materialize_intervals([_row("BTC-USDT-PERP", T1, "listed")])
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(T1, None)]


def test_delisted_row_alone_contributes_no_interval() -> None:
    assert materialize_intervals([_row("BTC-USDT-PERP", T2, "delisted")]) == ()


def test_bounded_initial_seed_is_a_closed_interval() -> None:
    intervals = materialize_intervals([_row("OLD-USDT-PERP", T1, "initial_seed", end=T2)])
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(T1, T2)]


def test_relisting_yields_two_intervals() -> None:
    rows = [
        _row("BTC-USDT-PERP", T1, "listed"),
        _row("BTC-USDT-PERP", T2, "delisted"),
        _row("BTC-USDT-PERP", T3, "listed"),
    ]
    intervals = materialize_intervals(rows)
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(T1, T2), (T3, None)]


def test_adjacent_states_merge_into_one_interval() -> None:
    rows = [_row("BTC-USDT-PERP", T1, "initial_seed"), _row("BTC-USDT-PERP", T2, "listed")]
    intervals = materialize_intervals(rows)
    assert [(item.valid_from, item.valid_to) for item in intervals] == [(T1, None)]


# ---------- 时点语义（AC-007） ----------


def test_universe_at_point_in_time_membership() -> None:
    rows = [_row("BTC-USDT-PERP", T1, "listed"), _row("BTC-USDT-PERP", T2, "delisted")]
    assert members_at(rows, T0) == frozenset()
    assert members_at(rows, MID) == frozenset({"BTC-USDT-PERP"})
    assert members_at(rows, T3) == frozenset()


def test_members_at_matches_interval_union_semantics() -> None:
    """库侧状态判定与 artifact 侧并集判定必须逐点一致（同一批行派生）。"""
    rows = [
        _row("BTC-USDT-PERP", T1, "listed"),
        _row("BTC-USDT-PERP", T2, "delisted"),
        _row("BTC-USDT-PERP", T3, "listed"),
        _row("OLD-USDT-PERP", T1, "initial_seed", end=T2),
        _row("NEW-USDT-PERP", T3, "listed"),
    ]
    intervals = materialize_intervals(rows)
    for moment in (
        T0,
        T1,
        MID,
        T2,
        datetime(2026, 7, 1, tzinfo=UTC),
        T3,
        datetime(2027, 1, 1, tzinfo=UTC),
    ):
        union = {
            item.lake_pair
            for item in intervals
            if item.valid_from <= moment and (item.valid_to is None or moment < item.valid_to)
        }
        assert members_at(rows, moment) == frozenset(union), moment


def test_members_at_requires_utc() -> None:
    with pytest.raises(MembershipError, match="时区"):
        members_at([], datetime(2026, 1, 1))  # noqa: DTZ001 - 故意构造 naive 输入


def test_bound_row_disappears_after_valid_to() -> None:
    rows = [_row("OLD-USDT-PERP", T1, "initial_seed", end=T2)]
    assert members_at(rows, MID) == frozenset({"OLD-USDT-PERP"})
    assert members_at(rows, T2) == frozenset()


# ---------- initial_seed 补种（T008） ----------


def test_seed_initial_members_uses_each_pair_data_start() -> None:
    starts = [("BTC/USDT", datetime(2024, 9, 10, 0, 0, tzinfo=UTC))]
    conn = _Conn(data_starts=starts)
    rows = seed_initial_members(
        conn,
        universe_id="sha256:" + "b" * 64,
        pairs=["BTC/USDT"],
        exchange="binance",
        market_type="perp",
    )
    assert [row.reason for row in rows] == ["initial_seed"]
    assert rows[0].valid_from == datetime(2024, 9, 10, tzinfo=UTC)
    assert rows[0].lake_pair == "BTC-USDT-PERP"
    assert conn.commits == 1


def test_seed_initial_members_fails_closed_when_pair_has_no_data() -> None:
    conn = _Conn(data_starts=[("BTC/USDT", datetime(2024, 9, 10, tzinfo=UTC))])
    with pytest.raises(MembershipError, match="ETH/USDT"):
        seed_initial_members(
            conn,
            universe_id="sha256:" + "b" * 64,
            pairs=["BTC/USDT", "ETH/USDT"],
            exchange="binance",
            market_type="perp",
        )
    assert conn.commits == 0


class _Cursor:
    def __init__(self, conn: _Conn) -> None:
        self._conn = conn
        self._result: list[tuple] = []

    def __enter__(self) -> _Cursor:
        return self

    def __exit__(self, *_args) -> bool:
        return False

    def execute(self, sql: str, params=()) -> None:
        self._conn.statements.append((sql, params))
        if "min(time)" in sql:
            self._result = list(self._conn.data_starts)
        elif sql.strip().upper().startswith("SELECT"):
            self._result = list(self._conn.rows)
        else:
            self._result = []

    def fetchall(self) -> list[tuple]:
        return self._result


class _Conn:
    def __init__(self, *, data_starts=(), rows=()) -> None:
        self.data_starts = tuple(data_starts)
        self.rows = tuple(rows)
        self.statements: list[tuple[str, tuple]] = []
        self.commits = 0

    def cursor(self) -> _Cursor:
        return _Cursor(self)

    def commit(self) -> None:
        self.commits += 1
