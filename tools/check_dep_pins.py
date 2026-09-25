#!/usr/bin/env python3
"""依赖 pin 一致性检查（CURRENT-code.md C001 回归门；F002 起含运行时依赖）。

严格校验 [project].dependencies 与 dev extras：依赖必须安装且版本在声明范围内。
其他可选 extras 仅在已安装时校验范围，缺失由对应运行期能力自检 fail-closed。
手写最小版本比较器（仅支持 >=/<=/==/!=/>/< 与逗号组合的简单 specifier，
按点分段整数比较），不引入第三方依赖；语义化版本的 pre-release/dev 后缀等
复杂场景超出本门禁目标，不做处理。

用法：python tools/check_dep_pins.py
退出码 0 = 严格依赖齐全且所有已安装依赖在范围内；1 = 存在越界、严格依赖缺失或无法解析。
"""

from __future__ import annotations

import importlib.metadata
import pathlib
import re
import sys
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

ROOT = pathlib.Path(__file__).resolve().parent.parent
STRICT_EXTRAS: Final[frozenset[str]] = frozenset({"dev"})

NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$")
CLAUSE_RE = re.compile(r"^(>=|<=|==|!=|>|<)\s*(.+)$")


@dataclass(frozen=True, slots=True)
class DependencyPin:
    """一个依赖范围及其是否必须安装。"""

    spec: str
    required: bool


def parse_version(version: str) -> tuple[int, ...]:
    core = version.strip().split("+")[0].split("-")[0]
    parts: list[int] = []
    for chunk in core.split("."):
        m = re.match(r"\d+", chunk)
        if m is None:
            break
        parts.append(int(m.group()))
    return tuple(parts) if parts else (0,)


def _padded(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    n = max(len(a), len(b))
    return a + (0,) * (n - len(a)), b + (0,) * (n - len(b))


def satisfies(installed: str, spec: str) -> bool:
    installed_v = parse_version(installed)
    clauses = [c.strip() for c in spec.split(",") if c.strip()]
    for clause in clauses:
        m = CLAUSE_RE.match(clause)
        if m is None:
            raise ValueError(f"不支持的 specifier 子句: {clause}")
        op, ref = m.groups()
        a, b = _padded(installed_v, parse_version(ref))
        ok = {">=": a >= b, "<=": a <= b, "==": a == b, "!=": a != b, ">": a > b, "<": a < b}[op]
        if not ok:
            return False
    return True


def parse_pin(pin: str) -> tuple[str, str]:
    m = NAME_RE.match(pin.strip())
    if m is None:
        raise ValueError(f"无法解析依赖声明: {pin}")
    return m.group(1), m.group(2)


def declared_pins(root: pathlib.Path) -> dict[str, DependencyPin]:
    """读取运行时与全部 extras pin，并标记必须安装的依赖。

    F002 起运行时依赖（duckdb/pyarrow 等）同样声明版本范围（spec 决策表：
    「pin 范围入 pyproject，check_dep_pins 门禁覆盖」）。运行时和
    STRICT_EXTRAS 必须安装；其他 extras 仅在已安装时校验。同名声明以后写者
    的范围为准，但只要任一来源严格，该依赖仍严格。
    """
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    entries = [(entry, True) for entry in project.get("dependencies", [])]
    for extra, extra_entries in project.get("optional-dependencies", {}).items():
        entries.extend((entry, extra in STRICT_EXTRAS) for entry in extra_entries)

    pins: dict[str, DependencyPin] = {}
    for entry, required in entries:
        name, spec = parse_pin(entry)
        previous = pins.get(name)
        pins[name] = DependencyPin(
            spec=spec,
            required=required or (previous.required if previous is not None else False),
        )
    return pins


def check(
    root: pathlib.Path = ROOT,
    installed_version: Callable[[str], str] | None = None,
) -> list[str]:
    version_of = importlib.metadata.version if installed_version is None else installed_version
    failures: list[str] = []
    for name, pin in declared_pins(root).items():
        try:
            ver = version_of(name)
        except importlib.metadata.PackageNotFoundError:
            if pin.required:
                failures.append(f"{name}: 未安装（声明范围: {pin.spec or '无'}）")
            continue
        if not satisfies(ver, pin.spec):
            failures.append(f"{name}: 已装 {ver} 不在声明范围内（{pin.spec or '无'}）")
    return failures


def main() -> int:
    failures = check()
    if not failures:
        print("check_dep_pins: runtime/dev 齐全；已安装的其他 extras 版本均在声明范围内")
        return 0
    print("check_dep_pins: 失败", file=sys.stderr)
    for e in failures:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
