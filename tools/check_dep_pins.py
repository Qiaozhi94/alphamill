#!/usr/bin/env python3
"""dev 依赖 pin 一致性检查（CURRENT-code.md C001 回归门）。

校验 [project.optional-dependencies].dev 中每个依赖的已安装版本是否落在
声明的版本范围内。手写最小版本比较器（仅支持 >=/<=/==/!=/>/< 与逗号组合的
简单 specifier，按点分段整数比较），不引入第三方依赖；语义化版本的
pre-release/dev 后缀等复杂场景超出本门禁目标，不做处理。

用法：python tools/check_dep_pins.py
退出码 0 = 全部在范围内；1 = 存在越界/未安装/无法解析。
"""

from __future__ import annotations

import importlib.metadata
import pathlib
import re
import sys
import tomllib
from collections.abc import Callable

ROOT = pathlib.Path(__file__).resolve().parent.parent

NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$")
CLAUSE_RE = re.compile(r"^(>=|<=|==|!=|>|<)\s*(.+)$")


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


def declared_dev_pins(root: pathlib.Path) -> dict[str, str]:
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    dev = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    pins: dict[str, str] = {}
    for entry in dev:
        name, spec = parse_pin(entry)
        pins[name] = spec
    return pins


def check(
    root: pathlib.Path = ROOT,
    installed_version: Callable[[str], str] | None = None,
) -> list[str]:
    version_of = importlib.metadata.version if installed_version is None else installed_version
    failures: list[str] = []
    for name, spec in declared_dev_pins(root).items():
        try:
            ver = version_of(name)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"{name}: 未安装（声明范围: {spec or '无'}）")
            continue
        if not satisfies(ver, spec):
            failures.append(f"{name}: 已装 {ver} 不在声明范围内（{spec or '无'}）")
    return failures


def main() -> int:
    failures = check()
    if not failures:
        print("check_dep_pins: 全部 dev 依赖版本在声明范围内")
        return 0
    print("check_dep_pins: 失败", file=sys.stderr)
    for e in failures:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
