"""check_dep_pins 回归测试：比较器边界 + 端到端 pin/版本一致性检查。"""

from __future__ import annotations

import pathlib

from tools import check_dep_pins


def test_parse_version_dotted_numeric() -> None:
    assert check_dep_pins.parse_version("9.0.3") == (9, 0, 3)
    assert check_dep_pins.parse_version("0.16.2") == (0, 16, 2)
    assert check_dep_pins.parse_version("1.0.post1") == (1, 0)
    assert check_dep_pins.parse_version("") == (0,)


def test_satisfies_in_range() -> None:
    assert check_dep_pins.satisfies("9.0.3", ">=8,<10")
    assert check_dep_pins.satisfies("0.16.2", ">=0.16,<0.17")


def test_satisfies_below_range() -> None:
    assert not check_dep_pins.satisfies("7.4.1", ">=8,<10")
    assert not check_dep_pins.satisfies("0.15.0", ">=0.16,<0.17")


def test_satisfies_above_range() -> None:
    assert not check_dep_pins.satisfies("10.0.0", ">=8,<10")
    assert not check_dep_pins.satisfies("0.17.0", ">=0.16,<0.17")


def test_satisfies_boundaries() -> None:
    assert check_dep_pins.satisfies("8.0.0", ">=8,<10")
    assert not check_dep_pins.satisfies("10.0.0", ">10")
    assert check_dep_pins.satisfies("10.0.1", ">10")
    assert check_dep_pins.satisfies("9", ">=9,<10")


def test_satisfies_unsupported_clause_raises() -> None:
    try:
        check_dep_pins.satisfies("1.0", "~=1.0")
    except ValueError as e:
        assert "不支持的 specifier 子句" in str(e)
    else:
        raise AssertionError("~= 子句应被拒绝")


def test_check_end_to_end_in_range(tmp_path: pathlib.Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project.optional-dependencies]\ndev = ["fakepkg>=1,<2"]\n',
        encoding="utf-8",
    )
    failures = check_dep_pins.check(
        tmp_path, installed_version=lambda name: {"fakepkg": "1.5"}[name]
    )
    assert failures == []


def test_check_end_to_end_out_of_range(tmp_path: pathlib.Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project.optional-dependencies]\ndev = ["fakepkg>=1,<2"]\n',
        encoding="utf-8",
    )
    failures = check_dep_pins.check(
        tmp_path, installed_version=lambda name: {"fakepkg": "2.1"}[name]
    )
    assert len(failures) == 1
    assert "fakepkg" in failures[0]
    assert "2.1" in failures[0]
    assert ">=1,<2" in failures[0]


def test_check_end_to_end_not_installed(tmp_path: pathlib.Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project.optional-dependencies]\ndev = ["ghostpkg>=1,<2"]\n',
        encoding="utf-8",
    )

    def _missing(name: str) -> str:
        raise check_dep_pins.importlib.metadata.PackageNotFoundError(name)

    failures = check_dep_pins.check(tmp_path, installed_version=_missing)
    assert len(failures) == 1
    assert "未安装" in failures[0]


def test_uninstalled_mining_extra_does_not_fail(tmp_path: pathlib.Path) -> None:
    # Given: strict dependencies are installed, but the optional mining extra is absent.
    (tmp_path / "pyproject.toml").write_text(
        """[project]
dependencies = ["runtimepkg>=1,<2"]
[project.optional-dependencies]
dev = ["devpkg>=1,<2"]
mining = ["torch>=2.7,<3"]
""",
        encoding="utf-8",
    )

    def _installed_version(name: str) -> str:
        versions = {"runtimepkg": "1.5", "devpkg": "1.5"}
        try:
            return versions[name]
        except KeyError:
            raise check_dep_pins.importlib.metadata.PackageNotFoundError(name) from None

    # When: the dependency gate checks all declared dependency groups.
    failures = check_dep_pins.check(tmp_path, installed_version=_installed_version)

    # Then: an absent non-dev extra does not fail the repository gate.
    assert failures == []


def test_installed_mining_extra_out_of_range_fails(tmp_path: pathlib.Path) -> None:
    # Given: a mining dependency is installed outside its declared range.
    (tmp_path / "pyproject.toml").write_text(
        '[project.optional-dependencies]\nmining = ["torch>=2.7,<3"]\n',
        encoding="utf-8",
    )

    # When: the dependency gate checks the installed optional dependency.
    failures = check_dep_pins.check(tmp_path, installed_version=lambda _name: "3.0.0")

    # Then: an installed optional dependency must still satisfy its range.
    assert len(failures) == 1
    assert "torch" in failures[0]
    assert "3.0.0" in failures[0]
    assert ">=2.7,<3" in failures[0]


def test_missing_runtime_and_dev_dependencies_still_fail(tmp_path: pathlib.Path) -> None:
    # Given: one runtime dependency and one strict dev dependency are absent.
    (tmp_path / "pyproject.toml").write_text(
        """[project]
dependencies = ["runtimepkg>=1,<2"]
[project.optional-dependencies]
dev = ["devpkg>=1,<2"]
""",
        encoding="utf-8",
    )

    def _missing(name: str) -> str:
        raise check_dep_pins.importlib.metadata.PackageNotFoundError(name)

    # When: the dependency gate checks strict dependencies.
    failures = check_dep_pins.check(tmp_path, installed_version=_missing)

    # Then: both strict dependency groups remain mandatory.
    assert {failure.split(":", 1)[0] for failure in failures} == {"runtimepkg", "devpkg"}
