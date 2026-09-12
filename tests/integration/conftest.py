"""Load the local deployment environment for host-side integration tests."""

from __future__ import annotations

import os
from pathlib import Path


def pytest_configure() -> None:
    dotenv = Path(__file__).resolve().parents[2] / "deployment/.env"
    if dotenv.is_file():
        for raw_line in dotenv.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

    # Compose uses the service DNS name; these tests run on the host.
    if os.environ.get("DB_HOST") == "timescaledb":
        os.environ["DB_HOST"] = "127.0.0.1"
