"""`python -m alphamill.data_bridge.universe` 的模块入口。

仓库统一用 `python -m`（无 `[project.scripts]`，见 design §2 边界规则）。
"""

from __future__ import annotations

from alphamill.data_bridge.universe.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
