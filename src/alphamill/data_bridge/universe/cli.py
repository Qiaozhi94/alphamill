"""`python -m alphamill.data_bridge.universe`：五个子命令与全部启动期拒绝（`IR-001` / T018）。

| 子命令 | 作用 |
|---|---|
| `discover` | 按口径筛候选并落 `UniverseDef` 草稿 |
| `freeze` | 人工确认后冻结定义 |
| `backfill` | 分批回填（批次按成交额排名切分） |
| `gate` | 跑质量门并准入 |
| `show` | 打印定义 / 按 digest 打印某时点成员 |

启动期拒绝（非零退出，各自可区分的 `code`）：

- `E_UNIVERSE_CRITERIA` / `E_UNIVERSE_EXCHANGE_UNREACHABLE`——口径缺字段 / 交易所不可达；
- `E_UNIVERSE_CONFIRM_REQUIRED` / `E_UNIVERSE_EMPTY_CANDIDATES` / `E_UNIVERSE_NOT_FOUND`
  ——`freeze` 缺 `--confirm` / 候选为空 / 定义不存在；
- `E_UNIVERSE_NOT_FROZEN` / `E_UNIVERSE_WINDOW` / `E_UNIVERSE_DISK`——`backfill` 未冻结 /
  窗口非法 / 磁盘余量不足；
- `E_UNIVERSE_GATE_INCOMPLETE`（及其余非 ACTIVE 判定）——回填未完成即跑门禁；
- `E_UNIVERSE_NOT_FOUND`——`show` 的定义或 digest 不存在。

退出码：`0` 成功；`1` 可重试的瞬时故障（库连接、IO）；`2` 数据裁决/启动期拒绝。
调用形态是模块入口（仓库无 `[project.scripts]`，见 `design.md` §2 边界规则）。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from alphamill.data_bridge.collector.db_writer import db_connect
from alphamill.data_bridge.universe import artifact as artifact_mod
from alphamill.data_bridge.universe import backfill_runner as runner
from alphamill.data_bridge.universe.admission import gate_and_admit
from alphamill.data_bridge.universe.capacity import estimate_rows, require_headroom, required_bytes
from alphamill.data_bridge.universe.cli_support import (
    apply_listing_starts,
    default_frozen_by,
    lake_root_for,
    parse_moment,
    refresh_aggregates,
    split_pairs,
    window_from_args,
)
from alphamill.data_bridge.universe.criteria import load_criteria
from alphamill.data_bridge.universe.definition import (
    build_definition,
    freeze_definition,
    is_frozen,
    load_definition,
    require_frozen,
    write_definition,
)
from alphamill.data_bridge.universe.discover import evaluate
from alphamill.data_bridge.universe.errors import (
    ConfirmRequiredError,
    EmptyDefinitionError,
    UniverseError,
    WindowError,
)
from alphamill.data_bridge.universe.exchange_snapshot import fetch_snapshot
from alphamill.data_bridge.universe.rate_limit import RateLimiter, RateLimitPolicy
from alphamill.data_bridge.universe.verdicts import VERDICT_ACTIVE

EXIT_OK = 0
EXIT_TRANSIENT = 1
EXIT_REJECTED = 2


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m alphamill.data_bridge.universe",
        description="F008 宇宙扩容与 point-in-time 宇宙台账",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    discover = sub.add_parser("discover", help="按口径筛候选并落 UniverseDef 草稿")
    discover.add_argument("--criteria", default=None, help="口径文件（缺省用入库默认口径）")
    discover.add_argument("--lake-root", default=None)
    discover.add_argument("--now", default=None, help="快照时间覆盖（ISO8601，测试/复算用）")

    freeze = sub.add_parser("freeze", help="人工确认后冻结定义")
    freeze.add_argument("--def", dest="definition", required=True)
    freeze.add_argument("--confirm", action="store_true", help="人工确认开关（必填）")
    freeze.add_argument("--frozen-by", default=None)
    freeze.add_argument("--lake-root", default=None)

    backfill = sub.add_parser("backfill", help="分批回填（批次按成交额排名切分）")
    backfill.add_argument("--universe", required=True)
    backfill.add_argument("--batch", type=int, choices=(1, 2), default=None)
    backfill.add_argument("--pairs", default=None, help="逗号分隔 db_symbol，缺省整批")
    backfill.add_argument("--start", default=None)
    backfill.add_argument("--end", default=None)
    backfill.add_argument("--lake-root", default=None)
    backfill.add_argument("--reports-dir", default=None)
    backfill.add_argument("--min-interval", type=float, default=0.5)
    backfill.add_argument(
        "--fetch-limit",
        type=int,
        default=None,
        help="单次 klines 请求的 K 线根数（Binance 现货上限 1000；缺省沿用 F001 的 100）",
    )
    backfill.add_argument("--max-retries", type=int, default=8)

    gate = sub.add_parser("gate", help="跑质量门并登记准入")
    gate.add_argument("--universe", required=True)
    gate.add_argument("--pairs", default=None)
    gate.add_argument("--start", default=None)
    gate.add_argument("--end", default=None)
    gate.add_argument("--lake-root", default=None)

    show = sub.add_parser("show", help="打印定义 / 某时点成员集合")
    show.add_argument("--universe", default=None)
    show.add_argument("--at", default=None, help="时点（ISO8601）；需与 --digest 同用")
    show.add_argument("--digest", default=None, help="台账 artifact digest")
    show.add_argument("--lake-root", default=None)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    handlers = {
        "discover": _discover,
        "freeze": _freeze,
        "backfill": _backfill,
        "gate": _gate,
        "show": _show,
    }
    try:
        return handlers[args.command](args)
    except UniverseError as exc:
        print(f"{exc.code}: {exc}", file=sys.stderr)
        return EXIT_REJECTED
    except OSError as exc:
        print(f"E_UNIVERSE_IO: {exc}", file=sys.stderr)
        return EXIT_TRANSIENT


# ---------------------------------------------------------------- 子命令


def _discover(args) -> int:
    criteria = load_criteria(args.criteria)
    now = parse_moment(args.now) if args.now else None
    snapshot = fetch_snapshot(criteria, now=now)
    definition = build_definition(criteria, evaluate(snapshot, criteria))
    path = write_definition(definition, lake_root_for(args))
    summary = {
        "universe_id": definition.universe_id,
        "snapshot_at": definition.snapshot_at,
        "criteria": criteria.describe(),
        "selected": len(definition.selected),
        "candidates": len(definition.candidates),
        "definition_path": str(path),
        "top": [item.db_symbol for item in definition.selected[:10]],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return EXIT_OK


def _freeze(args) -> int:
    if not args.confirm:
        raise ConfirmRequiredError("freeze 需要 --confirm：冻结是人工确认动作，不接受默认同意")
    lake_root = lake_root_for(args)
    definition = load_definition(args.definition, lake_root)
    if not definition.selected:
        raise EmptyDefinitionError(f"universe {args.definition} 的候选清单为空，拒绝冻结")
    record = freeze_definition(
        args.definition, frozen_by=args.frozen_by or default_frozen_by(), lake_root=lake_root
    )
    print(
        json.dumps(
            {
                "universe_id": record.universe_id,
                "frozen_at": record.frozen_at,
                "frozen_by": record.frozen_by,
                "selected": len(definition.selected),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return EXIT_OK


def _backfill(args) -> int:
    lake_root = lake_root_for(args)
    definition = require_frozen(args.universe, lake_root)
    start, end = window_from_args(args)
    runner.run_window_check(start, end)
    plans = runner.plan_batch(definition, batch=args.batch, pairs=split_pairs(args.pairs))
    rows = estimate_rows(pairs=len(plans), window_days=(end - start).total_seconds() / 86400)
    require_headroom(lake_root_for(args), required_bytes(rows))
    apply_listing_starts(definition, plans, start)
    if args.fetch_limit is not None:
        from alphamill.data_bridge.collector import historical_backfill as backfill_mod

        backfill_mod.FETCH_LIMIT = max(1, int(args.fetch_limit))
    limiter = RateLimiter(
        RateLimitPolicy(min_interval_seconds=args.min_interval, max_retries=args.max_retries)
    )
    conn = db_connect()
    try:
        run = runner.run_backfill_batch(
            universe_id=args.universe,
            plans=plans,
            start=start,
            end=end,
            conn=conn,
            lake_root=lake_root,
            reports_dir=Path(args.reports_dir) if args.reports_dir else None,
            limiter=limiter,
            batch=args.batch,
        )
    finally:
        conn.close()
    print(json.dumps(run.document(), ensure_ascii=False, indent=2))
    return EXIT_REJECTED if run.failed_pairs() else EXIT_OK


def _gate(args) -> int:
    lake_root = lake_root_for(args)
    definition = require_frozen(args.universe, lake_root)
    start, end = window_from_args(args)
    runner.run_window_check(start, end)
    conn = db_connect()
    try:
        refresh_aggregates(conn, start, end)
        outcomes = gate_and_admit(
            conn,
            definition=definition,
            window_start=start,
            window_end=end,
            pairs=split_pairs(args.pairs),
            lake_root=lake_root,
        )
    finally:
        conn.close()
    print(
        json.dumps(
            [
                {
                    "db_symbol": item.db_symbol,
                    "verdict": item.verdict,
                    "reason_code": item.reason_code,
                    "steps": list(item.steps),
                    "artifact_digest": item.artifact_digest,
                }
                for item in outcomes
            ],
            ensure_ascii=False,
            indent=2,
        )
    )
    for item in outcomes:
        if item.verdict != VERDICT_ACTIVE:
            print(
                f"E_UNIVERSE_GATE_{item.verdict}: {item.db_symbol} → {item.reason_code}",
                file=sys.stderr,
            )
    return EXIT_OK if all(item.verdict == VERDICT_ACTIVE for item in outcomes) else EXIT_REJECTED


def _show(args) -> int:
    lake_root = lake_root_for(args)
    if args.at:
        if not args.digest:
            raise WindowError("show --at 需要同时给出 --digest（台账按显式 digest 引用）")
        ledger = artifact_mod.load_artifact(args.digest, lake_root)
        members = sorted(ledger.universe_at(parse_moment(args.at)))
        print(
            json.dumps(
                {"digest": args.digest, "at": args.at, "members": members},
                ensure_ascii=False,
                indent=2,
            )
        )
        return EXIT_OK
    if not args.universe:
        raise WindowError("show 需要 --universe <id> 或 --at <T> --digest <digest>")
    definition = load_definition(args.universe, lake_root)
    print(
        json.dumps(
            {
                "universe_id": definition.universe_id,
                "snapshot_at": definition.snapshot_at,
                "criteria": definition.criteria.describe(),
                "frozen": is_frozen(definition.universe_id, lake_root),
                "selected": [item.payload() for item in definition.selected],
                "excluded": [
                    {"db_symbol": item.db_symbol, "reason": item.excluded_reason}
                    for item in definition.candidates
                    if item.excluded_reason
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return EXIT_OK


# ---------------------------------------------------------------- 工具


if __name__ == "__main__":  # pragma: no cover - 由 __main__.py 覆盖
    raise SystemExit(main())
