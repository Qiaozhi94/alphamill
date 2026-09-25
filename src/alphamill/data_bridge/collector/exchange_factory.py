"""ccxt 交易所实例构造（回填与衍生品采集共用）。

只读公开行情时不需要 API key；有凭据就走凭据（更高配额），代理按 `<EXCHANGE>_HTTPS_PROXY`
可选开启（本机 DNS 污染时的内网出口）。
"""

from __future__ import annotations

import os
from typing import Any


def build_exchange(exchange_id: str, *, with_credentials: bool = True):
    import ccxt

    exchange_class = getattr(ccxt, exchange_id, None)
    if exchange_class is None:
        raise ValueError(f"ccxt 不认识交易所 {exchange_id!r}")
    config: dict[str, Any] = {"enableRateLimit": True, "timeout": 30_000}
    if with_credentials:
        api_key = os.getenv(f"{exchange_id.upper()}_API_KEY", "")
        secret = os.getenv(f"{exchange_id.upper()}_SECRET", "")
        password = os.getenv(f"{exchange_id.upper()}_PASSPHRASE", "")
        if api_key and secret:
            config["apiKey"] = api_key
            config["secret"] = secret
        if password:
            config["password"] = password
    proxy = os.getenv(f"{exchange_id.upper()}_HTTPS_PROXY", "")
    if proxy:
        config["httpsProxy"] = proxy
    return exchange_class(config)
