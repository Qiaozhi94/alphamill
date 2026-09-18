"""F007 评测台 CLI 薄入口（`IR-001`/`IR-003`/`UX-001`；任务 T006，T013 追加其余子命令）。

CLI 只解析参数、序列化结果、映射稳定错误码与退出码，**不承载裁决逻辑**（design §2）。
成功输出首屏固定字段（tier/cohort/experiment、data/code digest、state、verdict、首个失败原因），
领域错误输出稳定 `error_code` 且非零退出——不存在 `PASS` 形态的退出码（`IR-003`）。

退出码：`0` 成功 · `1` 领域错误 · `2` 用法错误。本文件顶层异常处理器把**任何**未分类异常收敛成
`E_INTERNAL` 并返回非零：CLI 是进程边界，必须给出稳定可解析的失败输出，而不是把 traceback
当契约；这不是把门禁失败降级为警告——异常一律以非零退出并保留 message。
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from alphamill.evaluation.canonical import run_canonical
from alphamill.evaluation.canonical_ops import abandon_experiment, finalize_cohort
from alphamill.evaluation.capabilities import CapabilityError
from alphamill.evaluation.code_build import CodeBuildMismatchError
from alphamill.evaluation.contract_common import UpstreamContractError
from alphamill.evaluation.events import EventError
from alphamill.evaluation.preview import run_preview
from alphamill.evaluation.publisher import PublishError
from alphamill.evaluation.run_state import RunStateError
from alphamill.experiment_store.errors import SnapshotError, SnapshotIntegrityError
from alphamill.experiment_store.population import CohortError
from alphamill.factor_factory.bench.curves import CurvesError
from alphamill.factor_factory.bench.stage_model import StageModelError
from alphamill.validation.methodology_gate import GuardViolation

EXIT_OK = 0
EXIT_DOMAIN_ERROR = 1
EXIT_USAGE = 2

ERROR_INTERNAL = "E_INTERNAL"
ERROR_CODES = (
    "E_INPUT_INVALID",
    "E_DATA_DIGEST_MISMATCH",
    "E_METHODOLOGY_REJECTED",
    "E_REQUIRED_METRIC_FAILED",
    "E_CANONICAL_FORBIDDEN",
    "E_COHORT_FROZEN",
    "E_PUBLISH_INCOMPLETE",
    "E_PROMOTION_BLOCKED",
    ERROR_INTERNAL,
)


def classify_error(exc: BaseException) -> str:
    """领域异常 → 稳定错误码；未知异常一律 `E_INTERNAL`（不静默、不降级）。"""
    if isinstance(exc, CapabilityError):
        return "E_CANONICAL_FORBIDDEN"
    if isinstance(exc, SnapshotIntegrityError):
        return "E_DATA_DIGEST_MISMATCH"
    if isinstance(exc, (PublishError, CurvesError)):
        return "E_PUBLISH_INCOMPLETE"
    if isinstance(exc, CohortError):
        return "E_COHORT_FROZEN"
    if isinstance(exc, GuardViolation):
        return exc.code
    if isinstance(exc, (CodeBuildMismatchError, UpstreamContractError)):
        return exc.code
    if isinstance(exc, SnapshotError):
        return "E_INPUT_INVALID"
    if isinstance(exc, (StageModelError, RunStateError, EventError)):
        return "E_INPUT_INVALID"
    return ERROR_INTERNAL


def _dataset_list(value: str) -> list[str]:
    names = [item.strip() for item in value.split(",") if item.strip()]
    if not names:
        raise argparse.ArgumentTypeError("--latest 至少需要一个 dataset 名")
    return names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="alphamill-evaluation")
    subcommands = parser.add_subparsers(dest="command", required=True)

    preview = subcommands.add_parser("preview", help="隔离的探索性预览（不写正式总体）")
    preview.add_argument("--factor", required=True, help="上游 FactorDef 引用")
    preview.add_argument("--config", required=True, type=Path, help="预注册方法/阈值配置")
    preview.add_argument("--seed", required=True, type=int)
    preview.add_argument("--signals", required=True, type=Path, help="统一列集的信号夹具")
    target = preview.add_mutually_exclusive_group(required=True)
    target.add_argument("--snapshot", help="已发布 ResearchSnapshot ID")
    target.add_argument("--latest", type=_dataset_list, help="dataset 列表（先冻结成快照）")
    preview.add_argument("--cutoff", help="--latest 模式的信息截止时刻（UTC ISO-8601）")
    preview.add_argument("--symbol-map", dest="symbol_map", help="不可变 symbol-map digest")
    preview.add_argument("--universe", help="F008 universe 台账 digest（不解析 latest）")
    preview.add_argument("--calendar", type=Path, help="本 Feature calendar JSON")
    preview.add_argument("--cohort", help="显式 cohort 引用；缺省派生 preview 专属 cohort")
    preview.add_argument("--signal-source", dest="signal_source", default="real")
    preview.add_argument("--json", action="store_true", help="额外输出结构化 payload")

    canonical = subcommands.add_parser(
        "canonical", help="正式评测（写 reports/bench 与 official population）"
    )
    canonical.add_argument("--factor", required=True)
    canonical.add_argument("--candidate", required=True, help="cohort 承诺内的候选 ID")
    canonical.add_argument("--cohort", required=True, help="已冻结 cohort 引用")
    canonical.add_argument("--snapshot", required=True, help="已发布 ResearchSnapshot ID")
    canonical.add_argument("--config", required=True, type=Path)
    canonical.add_argument("--seed", required=True, type=int)
    canonical.add_argument("--signals", required=True, type=Path)
    canonical.add_argument("--expression", required=True, help="因子表达式（方法论门 L1 输入）")
    canonical.add_argument("--object", default=None, help="被测对象 ID（默认取 --factor）")
    canonical.add_argument("--code-build-digest", dest="code_build_digest", default=None)
    canonical.add_argument("--json", action="store_true")

    finalize = subcommands.add_parser("finalize-cohort", help="收齐后 finalize cohort")
    finalize.add_argument("--cohort", required=True)
    finalize.add_argument("--json", action="store_true")

    abandon = subcommands.add_parser("abandon", help="按终态不完整结论登记 INCOMPLETE 实验")
    abandon.add_argument("--experiment", required=True)
    abandon.add_argument("--reason", required=True)
    abandon.add_argument("--cohort", required=True)
    abandon.add_argument("--candidate", required=True)
    abandon.add_argument("--json", action="store_true")
    return parser


def _run_preview(args: argparse.Namespace) -> int:
    result = run_preview(
        config_path=args.config,
        factor_ref=args.factor,
        seed=args.seed,
        snapshot_id=args.snapshot,
        latest=args.latest,
        cutoff=args.cutoff,
        symbol_map_digest=args.symbol_map,
        universe_digest=args.universe,
        calendar_path=args.calendar,
        signals_path=args.signals,
        cohort_id=args.cohort,
        signal_source=args.signal_source,
    )
    for line in result.first_screen():
        print(line)
    if args.json:
        print(json.dumps(result.to_payload(), ensure_ascii=False, indent=2, sort_keys=True))
    return EXIT_OK


def _run_canonical(args: argparse.Namespace) -> int:
    result = run_canonical(
        config_path=args.config,
        factor_ref=args.factor,
        candidate_id=args.candidate,
        cohort_id=args.cohort,
        seed=args.seed,
        signals_path=args.signals,
        snapshot_id=args.snapshot,
        expression=args.expression,
        object_id=args.object,
        expected_code_build_digest=args.code_build_digest,
    )
    for line in result.first_screen():
        print(line)
    if args.json:
        print(json.dumps(result.to_payload(), ensure_ascii=False, indent=2, sort_keys=True))
    return EXIT_OK


def _run_finalize_cohort(args: argparse.Namespace) -> int:
    path = finalize_cohort(args.cohort)
    print(f"cohort={args.cohort}")
    print("status=FINALIZED")
    print(f"verdict={path}")
    return EXIT_OK


def _run_abandon(args: argparse.Namespace) -> int:
    path = abandon_experiment(
        experiment_id=args.experiment,
        reason=args.reason,
        cohort_id=args.cohort,
        candidate_id=args.candidate,
    )
    print(f"experiment_id={args.experiment}")
    print("state=REGISTERED")
    print(f"registration={path}")
    return EXIT_OK


HANDLERS = {
    "preview": _run_preview,
    "canonical": _run_canonical,
    "finalize-cohort": _run_finalize_cohort,
    "abandon": _run_abandon,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is None:
        print(f"error_code={ERROR_INTERNAL}")
        print(f"message=子命令未接线: {args.command}")
        return EXIT_DOMAIN_ERROR
    try:
        return handler(args)
    except Exception as exc:  # noqa: BLE001 - 见模块 docstring：CLI 边界收敛为稳定错误码
        print(f"error_code={classify_error(exc)}")
        print(f"message={type(exc).__name__}: {exc}")
        return EXIT_DOMAIN_ERROR


if __name__ == "__main__":
    sys.exit(main())
