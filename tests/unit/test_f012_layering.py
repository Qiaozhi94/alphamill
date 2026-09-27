"""F012 检视 R-C6：generators 层不得反向导入 CLI 层（mine_dispatch / cli / manifest_builder）。"""

from __future__ import annotations

import ast
from pathlib import Path

GENERATORS = Path(__file__).resolve().parents[2] / "src/alphamill/factor_factory/generators"
UPPER = {"mine_dispatch", "cli", "manifest_builder", "mine_config"}


def _upward_imports(path: Path) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom) and node.module:
            names = {alias.name for alias in node.names}
            if node.module == "alphamill.factor_factory" and names & UPPER:
                found.append(f"{node.module}:{sorted(names & UPPER)}")
            if node.module.split(".")[-1] in UPPER and node.module.startswith("alphamill."):
                found.append(node.module)
        if isinstance(node, ast.Import):
            found += [a.name for a in node.names if a.name.split(".")[-1] in UPPER]
    return found


def test_generators_do_not_import_the_cli_layer() -> None:
    offenders = {
        str(path.relative_to(GENERATORS)): hits
        for path in GENERATORS.rglob("*.py")
        if "alphagen_vendor" not in path.parts and (hits := _upward_imports(path))
    }
    assert not offenders, offenders
