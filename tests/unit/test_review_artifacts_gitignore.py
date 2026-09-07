"""检视过程稿 ignore 契约回归测试（D044 回归门）。

docs/reviews/ 下只有 RETROSPECTIVE.md 允许入库；CURRENT-* 过程稿与 FIX-log.md
必须被 .gitignore 忽略，防止 `git add -A` 把检视过程稿带进 git 历史
（review-convergence 协议要求过程稿永不入库）。变异验证已做过：重新放行任一
CURRENT-* 或删掉 RETROSPECTIVE 例外，本文件必须变红。
"""

from __future__ import annotations

import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _is_ignored(path: str) -> bool:
    proc = subprocess.run(
        ["git", "check-ignore", "-q", path],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
    )
    return proc.returncode == 0


def test_current_process_reports_are_ignored() -> None:
    assert _is_ignored("docs/reviews/CURRENT-doc.md")
    assert _is_ignored("docs/reviews/CURRENT-code.md")


def test_fix_log_is_ignored() -> None:
    assert _is_ignored("docs/reviews/FIX-log.md")


def test_retrospective_stays_trackable() -> None:
    assert not _is_ignored("docs/reviews/RETROSPECTIVE.md")
