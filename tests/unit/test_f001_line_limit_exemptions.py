"""F001 file-limit exemption register regression test."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_all_f001_over_limit_files_are_registered_with_an_expiry() -> None:
    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
    section = sop.split("### F001 原样迁移文件豁免", 1)[1].split("\n## ", 1)[0]
    registered = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.MULTILINE))
    actual = {
        str(path.relative_to(ROOT))
        for root in (ROOT / "src", ROOT / "freqtrade", ROOT / "deployment")
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".ps1"}
        and len(path.read_text(encoding="utf-8").splitlines()) > 350
    }

    assert actual == registered
    assert "解除期限" in section
    assert "F002" in section
