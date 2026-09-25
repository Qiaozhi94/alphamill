"""F001 file-limit exemption register regression test."""

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VENDOR_LINE_LIMIT_EXEMPT_DIRECTORY = Path("src/alphamill/factor_factory/generators/alphagen_vendor")


def _over_limit_files() -> set[str]:
    return {
        str(path.relative_to(ROOT))
        for root in (ROOT / "src", ROOT / "freqtrade", ROOT / "deployment")
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".py", ".ps1"}
        and not path.is_relative_to(ROOT / VENDOR_LINE_LIMIT_EXEMPT_DIRECTORY)
        and len(path.read_text(encoding="utf-8").splitlines()) > 350
    }


def test_all_f001_over_limit_files_are_registered_with_an_expiry() -> None:
    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
    section = sop.split("### F001 原样迁移文件豁免", 1)[1].split("\n### ", 1)[0]
    registered = set(re.findall(r"^\| `([^`]+)` \|", section, flags=re.MULTILINE))
    actual = _over_limit_files()

    assert actual == registered
    assert "解除期限" in section
    assert "F002" in section


def test_vendor_directory_exemption_does_not_weaken_other_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given: equally long files exist inside the vendor directory and ordinary source.
    sop = (ROOT / "docs/SOP.md").read_text(encoding="utf-8")
    directory_section = sop.split("### F003 AlphaGen vendor 目录级豁免", 1)[1].split("\n## ", 1)[0]
    registered_directories = set(
        re.findall(r"^\| `([^`]+)/` \|", directory_section, flags=re.MULTILINE)
    )
    vendor_file = (
        tmp_path / "src/alphamill/factor_factory/generators/alphagen_vendor/upstream_module.py"
    )
    ordinary_file = tmp_path / "src/alphamill/factor_factory/generators/ordinary_module.py"
    vendor_file.parent.mkdir(parents=True)
    ordinary_file.parent.mkdir(parents=True, exist_ok=True)
    long_source = "pass\n" * 351
    vendor_file.write_text(long_source, encoding="utf-8")
    ordinary_file.write_text(long_source, encoding="utf-8")
    monkeypatch.setattr(sys.modules[__name__], "ROOT", tmp_path)

    # When: the repository line-limit scan runs.
    actual = _over_limit_files()

    # Then: only the file outside the directory exemption remains a violation.
    assert registered_directories == {VENDOR_LINE_LIMIT_EXEMPT_DIRECTORY.as_posix()}
    assert actual == {str(ordinary_file.relative_to(tmp_path))}
