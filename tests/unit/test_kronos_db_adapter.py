"""Kronos DB fallback command regression tests."""

from pathlib import Path

from alphamill.kronos_service import db_adapter


def test_docker_fallback_uses_repository_compose_file_and_psql_variables() -> None:
    source = Path(db_adapter.__file__).read_text(encoding="utf-8")

    assert '"-f"' in source
    assert "str(COMPOSE_FILE)" in source
    assert "exchange = :'exchange'" in source
    assert "symbol = :'symbol'" in source
    assert "LIMIT :row_limit" in source
    assert "safe_exchange" not in source
    assert "safe_symbol" not in source
