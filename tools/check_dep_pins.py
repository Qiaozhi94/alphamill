#!/usr/bin/env python3
"""依赖 pin 一致性检查（CURRENT-code.md C001 回归门；F002 起含运行时依赖）。

校验 [project].dependencies 与 dev extras 中每个依赖的已安装版本是否落在
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


def declared_pins(root: pathlib.Path) -> dict[str, str]:
    """运行时 [project].dependencies 与 dev extras 的 pin 一并校验。

    F002 起运行时依赖（duckdb/pyarrow 等）同样声明版本范围（spec 决策表：
    「pin 范围入 pyproject，check_dep_pins 门禁覆盖」），故两者合并且同名
    声明以后写者为准。
    """
    with (root / "pyproject.toml").open("rb") as f:
        data = tomllib.load(f)
    project = data.get("project", {})
    entries = list(project.get("dependencies", []))
    entries += project.get("optional-dependencies", {}).get("dev", [])
    pins: dict[str, str] = {}
    for entry in entries:
        name, spec = parse_pin(entry)
        pins[name] = spec
    return pins


def check(
    root: pathlib.Path = ROOT,
    installed_version: Callable[[str], str] | None = None,
) -> list[str]:
    version_of = importlib.metadata.version if installed_version is None else installed_version
    failures: list[str] = []
    for name, spec in declared_pins(root).items():
        try:
            ver = version_of(name)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"{name}: 未安装（声明范围: {spec or '无'}）")
            continue
        if not satisfies(ver, spec):
            failures.append(f"{name}: 已装 {ver} 不在声明范围内（{spec or '无'}）")
    return failures


#: import 名 → 发行包名（两者不同的才列）。
IMPORT_TO_DISTRIBUTION = {
    "yaml": "pyyaml",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "psycopg2": "psycopg2-binary",
}

#: 「import 了 A，但 A 的这条用法还需要 B 而 B 不是 A 的必装依赖」——这类间接需求 AST 看
#: 不见，必须显式登记。httpx 就是这么漏的：测试 `from fastapi.testclient import TestClient`，
#: 而 httpx 只在 fastapi 的 standard/all extra 里，本地由别的包带上、CI 干净环境 ImportError。
INDIRECT_REQUIREMENTS = {
    ("fastapi.testclient", "httpx"),
    ("starlette.testclient", "httpx"),
}

#: 测试层允许直接 import 而无需声明的：标准库之外的本仓自有包与门禁工具。
#: 同目录模块（conftest、_f009_fakes、f001_backfill_config…）另行按文件存在性判定——
#: pytest 的 prepend 导入模式会把测试文件所在目录放进 sys.path，它们不是第三方包。
LOCAL_TOP_LEVEL = {"alphamill", "tools", "tests"}


def _sibling_modules(root: pathlib.Path) -> set[str]:
    """测试树内可被同目录导入的模块名（含 tools/ 下的门禁脚本，它们由 pythonpath 提供）。"""
    names: set[str] = set()
    for path in list((root / "tests").rglob("*.py")) + list((root / "tools").glob("*.py")):
        names.add(path.stem)
    return names


def check_test_imports_declared(root: pathlib.Path = ROOT) -> list[str]:
    """测试层的第三方顶层 import 必须在 pyproject 里声明（runtime 或 dev extras）。

    动机：本仓已两次被同一模式咬——httpx（F009 收口 266c9d6）与 pyyaml（F010 R2-002）
    都由别的包传递安装，本地全绿而 CI 干净环境在收集期 ImportError。只校验"已声明的
    版本在范围内"对"未声明"一无所知，所以按元规则把这条检查落进门禁。
    """
    import ast

    declared = set(declared_pins(root))
    siblings = _sibling_modules(root)
    failures: list[str] = []
    for path in sorted((root / "tests").rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        for module, needed in sorted(INDIRECT_REQUIREMENTS):
            if module in source and needed not in declared:
                failures.append(
                    f"{path.relative_to(root)}: 用到 {module} 需要 {needed!r}，"
                    "但它未在 pyproject 声明（该依赖是间接的，AST 看不见）"
                )
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:  # pragma: no cover - 语法错误由 ruff 负责
            failures.append(f"{path.relative_to(root)}: 无法解析（{exc}）")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module.split(".")[0]] if node.module and node.level == 0 else []
            else:
                continue
            for name in names:
                if name in LOCAL_TOP_LEVEL or name in sys.stdlib_module_names:
                    continue
                if name in siblings:  # 测试树/门禁脚本内的模块，不是第三方包
                    continue
                dist = IMPORT_TO_DISTRIBUTION.get(name, name)
                if dist not in declared:
                    failures.append(
                        f"{path.relative_to(root)}: import {name} 对应的发行包 {dist!r} "
                        "未在 pyproject 声明（CI 干净环境会在收集期 ImportError）"
                    )
    return sorted(set(failures))


def main() -> int:
    failures = check() + check_test_imports_declared()
    if not failures:
        print("check_dep_pins: 全部依赖版本在声明范围内（runtime + dev）")
        return 0
    print("check_dep_pins: 失败", file=sys.stderr)
    for e in failures:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
