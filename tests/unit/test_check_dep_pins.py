"""check_dep_pins 回归测试：比较器边界 + 端到端 pin/版本一致性检查。"""

from __future__ import annotations

import pathlib

from tools import check_dep_pins
from tools import check_dep_pins as cdp

ROOT = pathlib.Path(__file__).resolve().parents[2]


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


def test_test_layer_imports_must_be_declared(tmp_path: pathlib.Path) -> None:
    """门禁必须抓「代码 import 了但 pyproject 没声明」——本仓这类事故已发生两次。

    httpx（F009 收口，266c9d6）与 pyyaml（F010 R2-002）都是本地由别的包传递安装而全绿、
    CI 干净环境收集期 ImportError。`check_dep_pins` 原先只校验"已声明的版本在范围内"，
    对"未声明"一无所知，所以两次都没拦住。按元规则「同一类问题出现 ≥2 次就修 harness」，
    这条检查落在门禁里，而不是靠下次记得。
    """
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = []\n'
        '[project.optional-dependencies]\ndev = ["pytest>=8,<10"]\n',
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_smoke.py").write_text("import yaml\nimport httpx\n", encoding="utf-8")

    failures = cdp.check_test_imports_declared(tmp_path)

    assert any("yaml" in f or "pyyaml" in f for f in failures), failures
    assert any("httpx" in f for f in failures), failures


def test_declared_test_imports_pass(tmp_path: pathlib.Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["requests>=2,<3"]\n'
        '[project.optional-dependencies]\ndev = ["pyyaml>=6,<7"]\n',
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_smoke.py").write_text(
        "import yaml\nimport requests\nimport json\nfrom pathlib import Path\n", encoding="utf-8"
    )

    assert cdp.check_test_imports_declared(tmp_path) == []


def test_repo_test_layer_imports_are_all_declared() -> None:
    """对本仓自己跑一遍：现在不得有未声明的测试层第三方 import。"""
    assert cdp.check_test_imports_declared(ROOT) == []


def test_indirect_requirement_is_caught(tmp_path: pathlib.Path) -> None:
    """间接依赖也要抓：`from fastapi.testclient import ...` 需要 httpx，而 AST 看不见它。

    这正是 httpx 那次漏掉的路径——只扫顶层 import 名的话，这条永远抓不到。
    """
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\ndependencies = ["fastapi>=0.115,<1"]\n'
        '[project.optional-dependencies]\ndev = ["pytest>=8,<10"]\n',
        encoding="utf-8",
    )
    tests_dir = tmp_path / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_api.py").write_text(
        "from fastapi.testclient import TestClient\n", encoding="utf-8"
    )

    failures = cdp.check_test_imports_declared(tmp_path)

    assert any("httpx" in f for f in failures), failures
