"""单写者 claim 与 lease 接管（`design.md` §5、`NFR-001`/`SC-002`；任务 T025）。

- runner 以 `<key>.claim` **原子创建**（`O_EXCL`）取得单写权；已有**完整** canonical 直接幂等
  返回（不是冲突），只有**在飞**的运行才构成冲突；
- claim 记录 owner token、启动时间、lease 秒数与 pid；
- **崩溃接管**只在三条件同时成立时允许：lease 已过期 ∧ 无活进程 ∧ temp artifact 未发布；
  正常路径**不能偷锁**（未过期或进程仍在即拒绝）；
- release 只有持有同一 owner token 才能执行，避免误释放他人锁。

错误码映射说明：F007 的冻结错误码表没有独立的 busy/conflict 码，而 `E_COHORT_FROZEN` 在 T012 的
语义已覆盖「单写者/登记冲突」，故在飞冲突映射到它（使用既有冻结码，不新增取值）；该映射记为
待检视确认的假设。
"""

from __future__ import annotations

import contextlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

CLAIM_SUFFIX = ".claim"
TAKEOVER_SUFFIX = ".takeover"
DEFAULT_LEASE_SECONDS = 900
CLAIM_SCHEMA_VERSION = 1


class ClaimBusyError(Exception):
    """已在飞的运行持有单写权（或在飞时被请求接管）。"""

    code = "E_COHORT_FROZEN"


def claim_path(root: Path, key: str) -> Path:
    if not key or "/" in key or "\\" in key:
        raise ValueError(f"非法 claim key: {key!r}")
    return root / f"{key}{CLAIM_SUFFIX}"


def _parse(stamp: str) -> datetime:
    parsed = datetime.fromisoformat(stamp)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


@dataclass(frozen=True)
class Claim:
    key: str
    owner_token: str
    started_at: str
    lease_seconds: int
    pid: int
    schema_version: int = CLAIM_SCHEMA_VERSION

    def expires_at(self) -> datetime:
        return _parse(self.started_at) + timedelta(seconds=self.lease_seconds)

    def is_expired(self, now: datetime | None = None) -> bool:
        moment = now or datetime.now(UTC)
        return moment >= self.expires_at()

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "key": self.key,
            "owner_token": self.owner_token,
            "started_at": self.started_at,
            "lease_seconds": self.lease_seconds,
            "pid": self.pid,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Claim:
        return cls(
            key=str(payload["key"]),
            owner_token=str(payload["owner_token"]),
            started_at=str(payload["started_at"]),
            lease_seconds=int(payload["lease_seconds"]),
            pid=int(payload["pid"]),
        )


def read_claim(root: Path, key: str) -> Claim | None:
    """读取 claim；文件不存在**或内容损坏/为空**都返回 `None`，不抛 `JSONDecodeError`。

    损坏的 claim（如崩溃时只创建了空文件）是「失效锁」，由 `recover` 接管，不能让它把
    `experiment_id` 永久堵死（`R1-105`）。
    """
    path = claim_path(root, key)
    if not path.is_file():
        return None
    try:
        return Claim.from_payload(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError):
        return None


def claim_file_exists(root: Path, key: str) -> bool:
    return claim_path(root, key).is_file()


def acquire(
    root: Path,
    key: str,
    *,
    owner_token: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    now: datetime | None = None,
) -> Claim:
    """原子创建 claim；已存在即在飞冲突（`E_COHORT_FROZEN`），不覆盖、不偷锁。"""
    if not owner_token:
        raise ValueError("owner_token 不能为空")
    if lease_seconds <= 0:
        raise ValueError(f"lease_seconds 必须为正: {lease_seconds}")
    path = claim_path(root, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    moment = (now or datetime.now(UTC)).astimezone(UTC)
    claim = Claim(
        key=key,
        owner_token=owner_token,
        started_at=moment.isoformat(),
        lease_seconds=lease_seconds,
        pid=os.getpid(),
    )
    try:
        handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    except FileExistsError as exc:
        existing = read_claim(root, key)
        holder = existing.owner_token if existing else "<corrupt>"
        raise ClaimBusyError(f"{key} 已被 {holder} 持有，拒绝并发写入") from exc
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        json.dump(claim.to_payload(), stream, ensure_ascii=False, sort_keys=True)
    return claim


def release(root: Path, key: str, *, owner_token: str) -> None:
    """只允许持有同一 token 的一方释放；他人/已释放即拒绝（不误删他人锁）。"""
    path = claim_path(root, key)
    if not path.is_file():
        return
    existing = read_claim(root, key)
    if existing is None:
        raise ClaimBusyError(f"{key} 的 claim 不可识别（损坏），拒绝释放")
    if existing.owner_token != owner_token:
        raise ClaimBusyError(
            f"{key} 由 {existing.owner_token} 持有，{owner_token} 不得释放他人 claim"
        )
    path.unlink(missing_ok=True)


def assert_takeover_allowed(
    claim: Claim,
    *,
    now: datetime | None = None,
    process_alive: bool | None = None,
    temp_published: bool = False,
) -> None:
    """接管三条件：lease 过期 ∧ 无活进程 ∧ temp 未发布；任一不成立即拒绝。"""
    alive = is_process_alive(claim.pid) if process_alive is None else process_alive
    if not claim.is_expired(now):
        raise ClaimBusyError(f"{claim.key} 的 lease 未过期，不得接管（正常路径不能偷锁）")
    if alive:
        raise ClaimBusyError(f"{claim.key} 的持有进程仍存活（pid={claim.pid}），不得接管")
    if temp_published:
        raise ClaimBusyError(f"{claim.key} 的 temp artifact 已发布，应走幂等读取而非接管")


def _takeover_path(path: Path) -> Path:
    return path.with_name(f"{path.name}{TAKEOVER_SUFFIX}")


def _read_takeover_pid(guard: Path) -> int | None:
    try:
        return int(json.loads(guard.read_text(encoding="utf-8"))["pid"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _acquire_takeover_guard(guard: Path) -> int:
    """接管临界区锁：``O_EXCL`` 创建 `<claim>.takeover`，只有持锁者能删除旧 claim。

    这是把「读→判定→删→建」变成串行临界区的关键：任何两个接管者都无法同时进入，因此不存在
    「接管者删掉对手刚建立的锁」的交错（`R2-202`）。残留的 guard（持有进程已死）按 pid 存活
    探测就地回收，避免崩溃后永久堵死。
    """
    for _ in range(2):
        try:
            return os.open(guard, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError as exc:
            holder = _read_takeover_pid(guard)
            if holder is None or not is_process_alive(holder):
                with contextlib.suppress(OSError):
                    guard.unlink()
                continue
            raise ClaimBusyError(f"{guard.name} 正在被其他进程接管，拒绝并发接管") from exc
    raise ClaimBusyError(f"{guard.name} 接管锁争用失败，拒绝并发接管")


def recover(
    root: Path,
    key: str,
    *,
    owner_token: str,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    now: datetime | None = None,
    process_alive: bool | None = None,
    temp_published: bool = False,
) -> Claim:
    """接管失效锁后原子替换 claim；不满足接管条件即拒绝，原锁保持不变。

    「读 claim → 判定失效 → 删除 → 创建」整体放在 `<claim>.takeover` 串行临界区内，
    保证任一时刻至多一个接管者；文件不存在直接 `acquire`，损坏/为空视为失效锁。
    """
    path = claim_path(root, key)
    if not path.is_file():
        return acquire(root, key, owner_token=owner_token, lease_seconds=lease_seconds, now=now)
    guard = _takeover_path(path)
    guard_fd = _acquire_takeover_guard(guard)
    try:
        if not path.is_file():
            return acquire(root, key, owner_token=owner_token, lease_seconds=lease_seconds, now=now)
        existing = read_claim(root, key)
        if existing is None:
            path.unlink(missing_ok=True)
            return acquire(root, key, owner_token=owner_token, lease_seconds=lease_seconds, now=now)
        assert_takeover_allowed(
            existing, now=now, process_alive=process_alive, temp_published=temp_published
        )
        path.unlink(missing_ok=True)
        return acquire(root, key, owner_token=owner_token, lease_seconds=lease_seconds, now=now)
    finally:
        os.close(guard_fd)
        with contextlib.suppress(OSError):
            guard.unlink()
