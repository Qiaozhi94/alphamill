"""运行状态机（`spec.md` §5 冻结状态集；`TR-001`/`NFR-001`）。

状态名是机器可读契约：`evaluation.run_state_changed` 事件与 manifest 都用这里的取值。
终态集合与 spec §5 一致——canonical 成员以 `REGISTERED` 收口（保证「承诺成员集合 == 终态登记
集合」可判定），preview 以 `PREVIEW_DONE` 收口且不可晋级。
"""

from __future__ import annotations

STATE_CREATED = "CREATED"
STATE_VALIDATING = "VALIDATING"
STATE_RUNNING = "RUNNING"
STATE_EVIDENCE_READY = "EVIDENCE_READY"
STATE_REJECTED = "REJECTED"
STATE_INCOMPLETE = "INCOMPLETE"
STATE_REGISTERED = "REGISTERED"
STATE_PREVIEW_DONE = "PREVIEW_DONE"
STATE_FINALIZED = "FINALIZED"

RUN_STATES = (
    STATE_CREATED,
    STATE_VALIDATING,
    STATE_RUNNING,
    STATE_EVIDENCE_READY,
    STATE_REJECTED,
    STATE_INCOMPLETE,
    STATE_REGISTERED,
    STATE_PREVIEW_DONE,
    STATE_FINALIZED,
)
MEMBER_TERMINAL_STATES = (STATE_REGISTERED,)
PREVIEW_TERMINAL_STATES = (STATE_PREVIEW_DONE,)
RETRYABLE_STATES = (STATE_INCOMPLETE,)

TRANSITIONS = {
    STATE_CREATED: (STATE_VALIDATING, STATE_INCOMPLETE),
    STATE_VALIDATING: (STATE_RUNNING, STATE_REJECTED, STATE_INCOMPLETE),
    STATE_RUNNING: (STATE_EVIDENCE_READY, STATE_REJECTED, STATE_INCOMPLETE),
    STATE_INCOMPLETE: (STATE_VALIDATING, STATE_REGISTERED),
    STATE_REJECTED: (STATE_REGISTERED,),
    STATE_EVIDENCE_READY: (STATE_REGISTERED, STATE_PREVIEW_DONE),
    STATE_REGISTERED: (),
    STATE_PREVIEW_DONE: (),
    STATE_FINALIZED: (),
}


class RunStateError(ValueError):
    """未登记状态或非法迁移。"""


def require_state(state: str) -> str:
    if state not in RUN_STATES:
        raise RunStateError(f"未登记的运行状态: {state!r}（合法: {list(RUN_STATES)}）")
    return state


def can_transition(source: str, target: str) -> bool:
    require_state(source)
    require_state(target)
    return target in TRANSITIONS[source]


def assert_transition(source: str, target: str) -> None:
    if not can_transition(source, target):
        raise RunStateError(f"非法状态迁移: {source} -> {target}")
