"""F003 FR-002/AC-002：AlphaGen vendor 卫生与冻结基线验收。"""

import hashlib
import json
import re
from pathlib import Path
from typing import Final

ROOT: Final = Path(__file__).resolve().parents[2]
VENDOR_ROOT: Final = ROOT / "src/alphamill/factor_factory/generators/alphagen_vendor"
BASELINE_PATH: Final = VENDOR_ROOT / "_upstream_baseline.json"
VENDORED_PATH: Final = VENDOR_ROOT / "VENDORED.md"
LOCAL_SHIM_FILES: Final = frozenset({"alphamill_qlib_shim.py"})
METADATA_FILES: Final = frozenset({"_upstream_baseline.json", "VENDORED.md"})
EXPECTED_BASELINE_FILE_SHA256: Final = (
    "28410c732ba4c7b7a7991f52b410748502762b20874cd1a088c0cca0e72dee46"
)
EXPECTED_BASELINE_DIGEST: Final = (
    "sha256:fd4b8619f98f1e7fca88764d239b17b49709a0743e111829f84f8adb99e0a43b"
)
UNMODIFIED_SPOT_CHECK: Final = "alphagen/config.py"


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_vendor_tree_contains_only_frozen_subset_and_local_shim() -> None:
    # Given: the frozen manifest defines the only permitted upstream source files.
    manifest = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    expected = set(manifest["subset"]) | LOCAL_SHIM_FILES | METADATA_FILES

    # When: every file below the vendor root is enumerated without following the network.
    actual = {
        path.relative_to(VENDOR_ROOT).as_posix()
        for path in VENDOR_ROOT.rglob("*")
        if path.is_file()
    }

    # Then: no excluded upstream tree or undeclared local file is present.
    assert VENDOR_ROOT.is_dir()
    assert actual == expected, (
        f"missing={sorted(expected - actual)}, unexpected={sorted(actual - expected)}"
    )


def test_every_baseline_difference_is_annotated() -> None:
    # Given: the manifest carries the pinned digest for every copied upstream source file.
    manifest = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    # When: current source digests are compared with the frozen upstream digests.
    differing = {
        relative_path
        for relative_path, expected_digest in manifest["files"].items()
        if _sha256(VENDOR_ROOT / relative_path) != expected_digest
    }
    annotated = {
        relative_path
        for relative_path in differing
        if "# [alphamill]" in (VENDOR_ROOT / relative_path).read_text(encoding="utf-8")
    }

    # Then: every changed blob is attributable, and every new shim declares local ownership.
    assert differing <= annotated, (
        f"differing files={sorted(differing)}, unannotated={sorted(differing - annotated)}"
    )
    assert all(
        "# [alphamill]" in (VENDOR_ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in LOCAL_SHIM_FILES
    )


def test_vendor_never_imports_alphamill_glue() -> None:
    # Given: dependency flow must remain glue to vendor only.
    alphamill_import = re.compile(
        r"^\s*(?:from|import)\s+alphamill(?:\.|\s|$)",
        flags=re.MULTILINE,
    )

    # When: every vendored Python source is scanned locally.
    violations = sorted(
        path.relative_to(VENDOR_ROOT).as_posix()
        for path in VENDOR_ROOT.rglob("*.py")
        if alphamill_import.search(path.read_text(encoding="utf-8"))
    )

    # Then: no vendor module knows the AlphaMill glue package.
    assert not violations, f"vendor imports alphamill glue: {violations}"


def test_vendored_metadata_records_required_provenance() -> None:
    # Given: ADR-0002 requires provenance, modifications, and the license limitation.
    vendored = VENDORED_PATH.read_text(encoding="utf-8")
    required_fragments = {
        "upstream repository": "https://github.com/ICT-FinD-Lab/alphagen",
        "pinned commit": "259687e8f316994426416c530a94842a2fe6405e",
        "pinned commit date": "2026-06-04T05:54:37Z",
        "vendor date": "2026-09-19",
        "modification list": "## 修改清单",
        "license statement": "## 许可说明",
        "no upstream license": "没有 LICENSE",
        "private-use decision": "ADR-0001",
        "private-use scope": "个人、私有使用",
    }
    required_modified_files = {
        "alphamill_qlib_shim.py",
        "alphagen/data/expression.py",
        "alphagen/data/tokens.py",
    }

    # When: required metadata fragments are checked without consulting upstream.
    missing = sorted(
        label for label, fragment in required_fragments.items() if fragment not in vendored
    )
    modification_section = vendored.split("## 修改清单", 1)[1].split("## 许可说明", 1)[0]
    missing_modifications = sorted(
        required_modified_files - set(re.findall(r"`([^`]+)`", modification_section))
    )

    # Then: all five provenance categories and the no-license decision remain explicit.
    assert not missing, f"VENDORED.md missing required items: {missing}"
    assert not missing_modifications, f"VENDORED.md missing modified files: {missing_modifications}"
    assert "none yet" not in modification_section
    assert "qlib" in modification_section.lower()


def test_frozen_baseline_is_unchanged_and_internally_consistent() -> None:
    # Given: T003 froze both the complete manifest bytes and its canonical content digest.
    baseline_bytes = BASELINE_PATH.read_bytes()
    manifest = json.loads(baseline_bytes)
    canonical = json.dumps(
        {
            "repo": manifest["repository"],
            "commit": manifest["commit"],
            "files": manifest["files"],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode()

    # When: the frozen bytes, canonical payload, and one unchanged source are hashed.
    baseline_file_digest = hashlib.sha256(baseline_bytes).hexdigest()
    canonical_digest = "sha256:" + hashlib.sha256(canonical).hexdigest()
    spot_check_digest = _sha256(VENDOR_ROOT / UNMODIFIED_SPOT_CHECK)

    # Then: the reference is unchanged and still identifies an unmodified vendored blob.
    assert baseline_file_digest == EXPECTED_BASELINE_FILE_SHA256
    assert manifest["baseline_digest"] == EXPECTED_BASELINE_DIGEST
    assert canonical_digest == EXPECTED_BASELINE_DIGEST
    assert spot_check_digest == manifest["files"][UNMODIFIED_SPOT_CHECK]
