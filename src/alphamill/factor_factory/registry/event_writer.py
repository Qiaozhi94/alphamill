"""运行内单写者：线性写出拒绝事件与预筛记录（F012 `FR-004` / `DR-002` / `NFR-005`）。

`run_store.append_candidate_rejected` 每写一条都在锁内回读整个 events.jsonl 取序号，事件数
上万时是 O(n²)（文档检视 D07）。一次挖掘运行的 run_dir 只属于一个 run_id，天然单写者：
打开时读一次现有行数得到序号，之后每条用无用户态缓冲的 `os.write` 追加、不回读，按批 fsync。

`close()` 必须先于 `run_store.finalize_run` / 失败收尾调用（D30）：run.json 发布时事件已落盘，
finalize 内唯一一次 `_append_event` 读到的行数也与本写者写出的一致，序号连续。
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import get_args

from alphamill.factor_factory import canonical
from alphamill.factor_factory.errors import RunStoreError, SchemaValidationError
from alphamill.factor_factory.generators.base import RejectionReason
from alphamill.factor_factory.registry import run_store
from alphamill.factor_factory.registry.run_schema import EVENT_SCHEMA_VERSION

_REASONS = frozenset(get_args(RejectionReason))


class _Appender:
    def __init__(self, path: Path, fsync_every: int) -> None:
        self._fd = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
        self._pending = 0
        self._fsync_every = fsync_every

    def write(self, line: bytes) -> None:
        if os.write(self._fd, line) != len(line):
            raise RunStoreError("short write while appending run record")
        self._pending += 1
        if self._pending >= self._fsync_every:
            self.flush()

    def flush(self) -> None:
        if self._pending:
            os.fsync(self._fd)
            self._pending = 0

    def close(self) -> None:
        self.flush()
        os.close(self._fd)


class RunEventWriter:
    """events.jsonl（拒绝事件）与 prefilter.jsonl（预筛指标）的单写者。"""

    def __init__(self, run_dir: Path, *, run_id: str, fsync_every: int = 256) -> None:
        run_dir.mkdir(parents=True, exist_ok=True)
        events = run_dir / "events.jsonl"
        self._run_id = run_id
        self._seq = _count_lines(events)
        self._events = _Appender(events, fsync_every)
        self._prefilter = _Appender(run_dir / "prefilter.jsonl", fsync_every)
        self._closed = False

    def rejected(
        self,
        expression: Sequence[str],
        reason_code: str,
        detail: str,
        *,
        definition_digest: str | None = None,
        ts: datetime | None = None,
    ) -> run_store.GenerationEvent:
        if reason_code not in _REASONS:
            raise SchemaValidationError(f"unknown rejection reason: {reason_code!r}")
        payload: dict = {
            "expression": list(expression),
            "reason_code": reason_code,
            "detail": detail,
        }
        if definition_digest is not None:
            payload["definition_digest"] = definition_digest
        self._seq += 1
        event = run_store.GenerationEvent(
            schema_version=EVENT_SCHEMA_VERSION,
            event_seq=self._seq,
            event_type="generation.candidate_rejected",
            ts=ts if ts is not None else datetime.now(UTC),
            run_id=self._run_id,
            payload=payload,
        )
        self._events.write(canonical.canonical_json_bytes(run_store._payload(event)) + b"\n")
        return event

    def prefilter(self, record: Mapping[str, object]) -> None:
        self._prefilter.write(canonical.canonical_json_bytes(dict(record)) + b"\n")

    def close(self) -> None:
        """幂等：finalize 之前调用一次，finally 里再调用只做兜底。"""
        if self._closed:
            return
        self._closed = True
        self._events.close()
        self._prefilter.close()


def _count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    content = path.read_bytes()
    if content and not content.endswith(b"\n"):
        raise RunStoreError(f"events.jsonl contains an incomplete line: {path}")
    return content.count(b"\n")
