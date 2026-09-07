"""check_secrets 回归测试：模式命中/放行 + 端到端目录扫描 + 自身源码免误报。

fixture 一律写在 tmp_path 下；样例密钥在源码中用字符串拼接切开，保证本测试
文件自身不命中被测模式（否则门禁会拦下仓库里的自己）。
"""

from __future__ import annotations

import pathlib

from tools import check_secrets


def _bearer_line() -> str:
    # 拼接切开，避免源码自身命中 uuid-bearer 模式
    return "curl -H 'Authorization: B" + "earer 12345678-1234-1234-1234-123456789abc'"


def _apikey_line() -> str:
    return '"api' + 'Key": "23456789-2345-2345-2345-23456789abcd"'


def test_detect_uuid_bearer(tmp_path: pathlib.Path) -> None:
    (tmp_path / "log.md").write_text(_bearer_line(), encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "uuid-bearer" in findings[0]
    assert "log.md:1" in findings[0]


def test_detect_uuid_apikey(tmp_path: pathlib.Path) -> None:
    (tmp_path / "config.json").write_text(_apikey_line(), encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "uuid-apikey" in findings[0]


def test_detect_github_token(tmp_path: pathlib.Path) -> None:
    token = "ghp_" + "A" * 40
    (tmp_path / "note.txt").write_text(f"token: {token}", encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "github-token" in findings[0]


def test_detect_openai_style(tmp_path: pathlib.Path) -> None:
    key = "sk-" + "B" * 24
    (tmp_path / "note.txt").write_text(f"key {key}", encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "openai-style" in findings[0]


def test_detect_aws_key(tmp_path: pathlib.Path) -> None:
    aws = "AKIA" + "1234567890ABCDEF"
    (tmp_path / "env").write_text(f"AWS={aws}", encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "aws-access-key" in findings[0]


def test_detect_private_key_block(tmp_path: pathlib.Path) -> None:
    pem = "-----BEGIN RSA PRIV" + "ATE KEY-----"
    (tmp_path / "id_rsa").write_text(pem, encoding="utf-8")
    findings = check_secrets.check(tmp_path)
    assert len(findings) == 1
    assert "private-key-block" in findings[0]


def test_clean_file_passes(tmp_path: pathlib.Path) -> None:
    (tmp_path / "doc.md").write_text(
        "# 正常文档\n提到 apiKey 概念、Bearer 认证与 sk- 前缀，但无密钥值。\n"
        "run 34081647116 / commit 8df5f9f 均非密钥。\n",
        encoding="utf-8",
    )
    assert check_secrets.check(tmp_path) == []


def test_redacted_marker_passes(tmp_path: pathlib.Path) -> None:
    # 事件后的脱敏产物形态：Bearer ***REDACTED-ARK-API-KEY*** 不得误报
    (tmp_path / "timeline.md").write_text(
        "bash curl -H 'Authorization: Bearer ***REDACTED-ARK-API-KEY***'", encoding="utf-8"
    )
    assert check_secrets.check(tmp_path) == []


def test_skipped_dirs_not_scanned(tmp_path: pathlib.Path) -> None:
    hidden = tmp_path / ".omo"
    hidden.mkdir()
    (hidden / "session.md").write_text(_bearer_line(), encoding="utf-8")
    assert check_secrets.check(tmp_path) == []


def test_repo_tree_self_scan_clean() -> None:
    # 门禁对当前仓库树自身必须零命中（含本测试文件——拼接写法的意义所在）
    assert check_secrets.check(check_secrets.ROOT) == []
