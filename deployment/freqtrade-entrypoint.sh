#!/usr/bin/env bash
set -euo pipefail

template="${FREQTRADE_CONFIG_TEMPLATE:-/freqtrade/user_data/config.json}"
rendered="${FREQTRADE_CONFIG_RENDERED:-/tmp/alphamill-freqtrade-config.json}"

python - "$template" "$rendered" <<'PY'
import json
import os
import re
import sys
from pathlib import Path

template, rendered = map(Path, sys.argv[1:])
pattern = re.compile(r"\$\{([A-Z][A-Z0-9_]*)(:-[^}]*)?\}")


def replace(value: object) -> object:
    if isinstance(value, dict):
        return {key: replace(item) for key, item in value.items()}
    if isinstance(value, list):
        return [replace(item) for item in value]
    if not isinstance(value, str):
        return value
    missing = [
        name
        for name, default in pattern.findall(value)
        if not os.getenv(name) and not default
    ]
    if missing:
        raise SystemExit(
            "missing required Freqtrade environment variables: " + ", ".join(missing)
        )
    return pattern.sub(
        lambda match: os.getenv(match.group(1), match.group(2)[2:] if match.group(2) else ""),
        value,
    )


config = replace(json.loads(template.read_text(encoding="utf-8")))
rendered.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

exec freqtrade "$@" --config "$rendered"
