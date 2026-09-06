"""check_doc_links 回归测试：死链标记、合法链接放行、围栏内忽略（D011 回归门）。"""

from __future__ import annotations

import pathlib

from tools import check_doc_links


def build_root(tmp_path: pathlib.Path, readme: str, docs_files: dict[str, str]) -> None:
    (tmp_path / "README.md").write_text(readme, encoding="utf-8")
    for rel, content in docs_files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def test_flags_exactly_the_broken_link(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme="[ok](docs/alpha.md)\n[dead](docs/missing.md)\n",
        docs_files={"docs/alpha.md": "# A\n"},
    )
    errors = check_doc_links.check_links(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith("README.md:2:")
    assert "docs/missing.md" in errors[0]


def test_skips_http_mailto_anchor(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme=("[web](https://example.com)\n[mail](mailto:a@b.c)\n[anchor](#section)\n"),
        docs_files={},
    )
    assert check_doc_links.check_links(tmp_path) == []


def test_ignores_links_inside_code_fences(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme="```text\n[fenced-dead](docs/none.md)\n```\n[ok](docs/alpha.md)\n",
        docs_files={"docs/alpha.md": "# A\n"},
    )
    assert check_doc_links.check_links(tmp_path) == []


def test_resolves_relative_to_containing_file_and_directories(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme="unused\n",
        docs_files={
            "docs/README.md": "[self](alpha.md)\n[up](../README.md)\n[dir](decisions/)\n",
            "docs/alpha.md": "# A\n",
            "docs/decisions/x.md": "# X\n",
        },
    )
    assert check_doc_links.check_links(tmp_path) == []


def test_excludes_research_and_conversations(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme="unused\n",
        docs_files={
            "docs/research/note.md": "[dead](nowhere.md)\n",
        },
    )
    (tmp_path / "conversations").mkdir()
    (tmp_path / "conversations" / "c.md").write_text("[dead](nowhere.md)\n", encoding="utf-8")
    assert check_doc_links.check_links(tmp_path) == []


def test_anchor_fragment_stripped_before_resolution(tmp_path: pathlib.Path) -> None:
    build_root(
        tmp_path,
        readme="[sec](docs/alpha.md#sec)\n",
        docs_files={"docs/alpha.md": "# A\n"},
    )
    assert check_doc_links.check_links(tmp_path) == []
