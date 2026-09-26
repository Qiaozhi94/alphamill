"""导出 CLI——`python -m alphamill.data_bridge.exporter`（design §5 退出码契约）。

退出码：0 = 成功（含 no-op）；1 = 可重试的瞬时故障（库连接失败、IO 错误、
staging 写入中断）；2 = 不可重试的数据裁决（对账失败→版本已标 invalid、
manifest 完整性失败、registry/symbol 校验失败）。systemd unit 以
`RestartPreventExitStatus=2` 锁定「对账失败不重试」。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import sys
from typing import Any

import psycopg2

from alphamill.data_bridge import registry
from alphamill.data_bridge.errors import DataBridgeError
from alphamill.data_bridge.universe.errors import UniverseError

EXIT_OK = 0
EXIT_TRANSIENT = 1
EXIT_FATAL = 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m alphamill.data_bridge.exporter",
        description="TimescaleDB → Parquet 湖导出器（F002）",
    )
    parser.add_argument(
        "--dataset",
        action="append",
        default=None,
        metavar="NAME",
        help="导出的 dataset（可重复）；缺省导出 registry 全部",
    )
    parser.add_argument(
        "--mode",
        choices=("incremental", "full"),
        default="incremental",
        help="incremental=每日增量（默认）；full=全量校验（修订时递增版本）",
    )
    parser.add_argument(
        "--window-end",
        default=None,
        metavar="ISO_DATETIME",
        help="窗口开区间上界（UTC ISO8601）；缺省为今日 00:00 UTC，即导到「昨天」",
    )
    parser.add_argument(
        "--allow-shrink",
        action="store_true",
        help="full 模式人工确认：源库收缩确属有意，放行空结果/大幅收缩的新版本"
        "（窗口传错导致的截断不在确认范围内，仍然拒绝）",
    )
    parser.add_argument(
        "--universe-filter",
        action="store_true",
        help="F008/F011：按「台账可交易 ∩ 质量门 ACTIVE ∩ 被绑定宇宙入选集」过滤 pair，"
        "落选/退市 pair 按截止日保留历史（窗口终点为 PIT 时点）；缺省关闭，行为与 F002 现状一致",
    )
    parser.add_argument(
        "--universe-id",
        default=None,
        metavar="DIGEST",
        help="F011：显式绑定的宇宙版本（须已冻结且在窗口终点前生效）；缺省取当时生效的最新版本",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="调试日志")
    args = parser.parse_args(argv)
    if args.universe_id and not args.universe_filter:
        parser.error("--universe-id 只能与 --universe-filter 同时给出（不隐式开启过滤）")
    return args


def _selected_datasets(names: list[str] | None) -> list[str]:
    if not names:
        return sorted(registry.DATASETS)
    for name in names:
        registry.require_dataset(name)  # UnknownDatasetError → 退出码 2
    return names


def _refresh_symbol_map() -> None:
    """导出前刷新 current 副本与不可变 artifact（「随湖维护」，FR-004）。"""
    from alphamill.data_bridge import symbol_map

    ref = symbol_map.export_symbol_map()
    logging.getLogger(__name__).info("symbol_map 已发布: digest=%s", ref.digest)


def _bind_universe(args: argparse.Namespace) -> tuple[str, Any]:
    """F011 启动期绑定：窗口终点一次定值，在刷新 symbol_map 与任何 dataset 之前解析（FR-003）。"""
    from alphamill.data_bridge import partitions
    from alphamill.data_bridge.universe import binding

    window_end = args.window_end or dt.datetime.now(dt.UTC).date().isoformat()
    at = dt.datetime.combine(partitions.as_date(window_end), dt.time.min, tzinfo=dt.UTC)
    bound = binding.resolve_binding(at, universe_id=args.universe_id)
    logging.getLogger(__name__).info(
        "宇宙绑定: universe_id=%s snapshot_at=%s frozen_at=%s resolution=%s",
        bound.universe_id,
        bound.definition.snapshot_at,
        bound.freeze.frozen_at,
        bound.resolution,
    )
    return window_end, bound


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    from alphamill.data_bridge.exporter import export_dataset

    window_end, bound = args.window_end, None
    if args.universe_filter:
        try:
            window_end, bound = _bind_universe(args)
        except UniverseError as exc:  # 拒绝启动：湖内零写入（不发布 symbol_map、不导出）
            print(f"FATAL: {exc.code}: {exc}", file=sys.stderr)
            return EXIT_FATAL
        except OSError as exc:
            print(f"FATAL: 瞬时故障（可重试）: {exc}", file=sys.stderr)
            return EXIT_TRANSIENT

    exit_code = EXIT_OK
    try:
        datasets = _selected_datasets(args.dataset)
        _refresh_symbol_map()
    except psycopg2.Error as exc:
        print(f"FATAL: 瞬时故障（可重试）: {exc}", file=sys.stderr)
        return EXIT_TRANSIENT
    except OSError as exc:
        print(f"FATAL: 瞬时故障（可重试）: {exc}", file=sys.stderr)
        return EXIT_TRANSIENT
    except ValueError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return EXIT_FATAL
    except DataBridgeError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return EXIT_FATAL

    for dataset in datasets:
        try:
            summary = export_dataset(
                dataset,
                mode=args.mode,
                window_end=window_end,
                allow_shrink=args.allow_shrink,
                universe_filter=args.universe_filter,
                bound_universe=bound,
            )
        except psycopg2.Error as exc:
            print(f"FATAL: {dataset}: 瞬时故障（可重试）: {exc}", file=sys.stderr)
            exit_code = max(exit_code, EXIT_TRANSIENT)
            continue
        except OSError as exc:
            print(f"FATAL: {dataset}: 瞬时故障（可重试）: {exc}", file=sys.stderr)
            exit_code = max(exit_code, EXIT_TRANSIENT)
            continue
        except ValueError as exc:
            print(f"FATAL: {dataset}: {exc}", file=sys.stderr)
            exit_code = max(exit_code, EXIT_FATAL)
            continue
        except DataBridgeError as exc:
            print(f"FATAL: {dataset}: {exc}", file=sys.stderr)
            exit_code = max(exit_code, EXIT_FATAL)
            continue
        print(json.dumps(summary, ensure_ascii=False))
        if summary["status"] == "invalid":
            exit_code = max(exit_code, EXIT_FATAL)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
