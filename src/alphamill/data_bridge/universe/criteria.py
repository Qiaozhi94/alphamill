"""筛选口径的载入与校验（T001 / `FR-001` / `DR-001`）。

口径是 `discover` 的输入、也是 `universe_id` 的组成部分，所以：

- 入库文件 `criteria.json` 是**默认口径的唯一来源**（可复核、进版本库、随代码评审）；
- 载入时严格校验键集合——多一个键即判非法，口径不允许悄悄多出未入档的筛选维度；
- `min_listed_days` 的语义是**严格大于**（`spec.md` §3：上线 >180 天）；
- 口径是排名法而非绝对金额阈值：绝对阈值随市场周期漂移，产出规模不可控（Q-001 裁决）。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from alphamill.data_bridge import symbol_map
from alphamill.data_bridge.universe.errors import CriteriaError

SCHEMA_VERSION = 1
DEFAULT_CRITERIA_PATH = Path(__file__).with_name("criteria.json")
EXCLUDE_RULE_IDS = (
    "stablecoin_pair",
    "leveraged_token",
    "index_basket",
    "tokenized_tradfi",
    "tokenized_commodity",
)

_REQUIRED_KEYS = frozenset(
    {
        "schema_version",
        "exchange",
        "market_type",
        "quote_currency",
        "turnover_lookback_days",
        "turnover_rank_top_n",
        "min_listed_days",
        "exclude_rules",
    }
)


@dataclass(frozen=True, kw_only=True)
class Criteria:
    """一次发现所使用的不可变口径；改任何一个字段都会产生新的 `universe_id`。"""

    exchange: str
    market_type: str
    quote_currency: str
    turnover_lookback_days: int
    turnover_rank_top_n: int
    min_listed_days: int
    exclude_rules: tuple[str, ...]
    schema_version: int = SCHEMA_VERSION

    def payload(self) -> dict[str, Any]:
        """进入 `universe_id` 的 canonical 形式（字段序由 canonical JSON 决定）。"""
        return {
            "schema_version": self.schema_version,
            "exchange": self.exchange,
            "market_type": self.market_type,
            "quote_currency": self.quote_currency,
            "turnover_lookback_days": self.turnover_lookback_days,
            "turnover_rank_top_n": self.turnover_rank_top_n,
            "min_listed_days": self.min_listed_days,
            "exclude_rules": list(self.exclude_rules),
        }

    def describe(self) -> str:
        return (
            f"{self.exchange}/{self.market_type} {self.quote_currency} "
            f"top{self.turnover_rank_top_n} of {self.turnover_lookback_days}d "
            f"listed>{self.min_listed_days}d exclude={','.join(self.exclude_rules) or '-'}"
        )


def load_criteria(path: str | Path | None = None) -> Criteria:
    """载入并严格校验口径文件；缺字段、未知键或非法值一律判红。"""
    source = Path(path) if path is not None else DEFAULT_CRITERIA_PATH
    try:
        raw = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise CriteriaError(f"口径文件不可读: {source}: {exc}") from exc
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CriteriaError(f"口径文件不是合法 JSON: {source}: {exc}") from exc
    if not isinstance(document, dict):
        raise CriteriaError(f"口径文件顶层必须是 JSON object: {source}")
    return criteria_from_payload(document, source=str(source))


def criteria_from_payload(document: dict[str, Any], *, source: str = "<memory>") -> Criteria:
    """从已解析的 payload 构造口径；键集合必须严格相等（多一个即判非法）。"""
    missing = sorted(_REQUIRED_KEYS - set(document))
    unknown = sorted(set(document) - _REQUIRED_KEYS)
    if missing or unknown:
        raise CriteriaError(f"口径键集合非法（{source}）: missing={missing}, unknown={unknown}")

    schema_version = document["schema_version"]
    if schema_version != SCHEMA_VERSION:
        raise CriteriaError(
            f"不支持的 criteria schema_version: {schema_version!r}（期望 {SCHEMA_VERSION}）"
        )
    exchange = _require_text(document, "exchange")
    market_type = _require_text(document, "market_type")
    if market_type not in symbol_map.MARKET_TYPES:
        raise CriteriaError(f"market_type 非法: {market_type!r}（合法: {symbol_map.MARKET_TYPES}）")
    quote_currency = _require_text(document, "quote_currency").upper()
    lookback = _require_positive_int(document, "turnover_lookback_days")
    top_n = _require_positive_int(document, "turnover_rank_top_n")
    min_listed_days = _require_non_negative_int(document, "min_listed_days")

    rules = document["exclude_rules"]
    if not isinstance(rules, list) or not all(isinstance(item, str) for item in rules):
        raise CriteriaError("exclude_rules 必须是字符串数组")
    unknown_rules = sorted(set(rules) - set(EXCLUDE_RULE_IDS))
    if unknown_rules:
        raise CriteriaError(f"未知排除规则: {unknown_rules}（合法: {list(EXCLUDE_RULE_IDS)}）")
    if len(set(rules)) != len(rules):
        raise CriteriaError(f"exclude_rules 出现重复项: {rules}")

    return Criteria(
        exchange=exchange,
        market_type=market_type,
        quote_currency=quote_currency,
        turnover_lookback_days=lookback,
        turnover_rank_top_n=top_n,
        min_listed_days=min_listed_days,
        exclude_rules=tuple(rules),
    )


def _require_text(document: dict[str, Any], key: str) -> str:
    value = document[key]
    if not isinstance(value, str) or not value.strip():
        raise CriteriaError(f"{key} 必须是非空字符串，得到 {value!r}")
    return value.strip()


def _require_positive_int(document: dict[str, Any], key: str) -> int:
    value = _require_non_negative_int(document, key)
    if value == 0:
        raise CriteriaError(f"{key} 必须为正整数，得到 {value!r}")
    return value


def _require_non_negative_int(document: dict[str, Any], key: str) -> int:
    value = document[key]
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CriteriaError(f"{key} 必须是非负整数，得到 {value!r}")
    return value
