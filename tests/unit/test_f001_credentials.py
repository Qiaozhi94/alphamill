"""F001 credential injection regression tests."""

import json
import os
from pathlib import Path
import subprocess

from tools import check_secrets


ROOT = Path(__file__).resolve().parents[2]


def test_freqtrade_configs_use_environment_placeholders() -> None:
    for name in ("config.json", "config.dryrun.json"):
        config = json.loads((ROOT / "freqtrade/user_data" / name).read_text(encoding="utf-8"))
        api_server = config.get("api_server", {})
        for key in ("password", "jwt_secret_key", "ws_token"):
            if key in api_server:
                assert api_server[key].startswith("${FREQTRADE_")


def test_secret_scanner_rejects_plaintext_freqtrade_password(tmp_path: Path) -> None:
    config = {
        "api_server": {
            "password": "literal-password",
            "jwt_secret_key": "${JWT}",
            "ws_token": "${WS}",
        }
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    findings = check_secrets.check(tmp_path)

    assert any("freqtrade-plaintext-password" in finding for finding in findings)


def test_entrypoint_renders_credentials_without_mutating_template(tmp_path: Path) -> None:
    template = tmp_path / "config.json"
    rendered = tmp_path / "rendered.json"
    template.write_text(
        '{"api_server": {"password": "${FREQTRADE_API_PASSWORD}"}}\n', encoding="utf-8"
    )
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_freqtrade = fake_bin / "freqtrade"
    fake_freqtrade.write_text(
        "#!/usr/bin/env python3\nimport sys\nassert sys.argv[-2:] == ['--config', sys.argv[-1]]\n",
        encoding="utf-8",
    )
    fake_freqtrade.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "FREQTRADE_API_PASSWORD": "runtime-only-password",
        "FREQTRADE_CONFIG_TEMPLATE": str(template),
        "FREQTRADE_CONFIG_RENDERED": str(rendered),
    }

    subprocess.run(
        [str(ROOT / "deployment/freqtrade-entrypoint.sh"), "trade"],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(template.read_text(encoding="utf-8"))["api_server"]["password"] == (
        "${FREQTRADE_API_PASSWORD}"
    )
    assert json.loads(rendered.read_text(encoding="utf-8"))["api_server"]["password"] == (
        "runtime-only-password"
    )
