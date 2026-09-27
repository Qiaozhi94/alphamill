"""F012 T019 产能取证：把一次执行机夜槽 `mine --generator alphagen` 运行固化为入库证据。

用法（执行机，运行结束后）：

    python3 tools/f012_capacity_evidence.py reports/generation/<run_id> \
        --stdout reports/f012/capacity-run.stdout --binding <绑定文件路径>

输出 `reports/f012/capacity-run.json`（run.json 原样副本，reports/generation 不入库）与
`reports/f012/capacity-evidence.json`（AC-009 字段 + run.json 摘要哈希）。取证校验由
`tests/integration/test_f012_capacity_evidence.py` 完成；本脚本不做任何判定之外的加工。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import socket
import statistics
from datetime import UTC, datetime
from pathlib import Path

CAPACITY_TARGET = 50
OUT_DIR = Path(__file__).resolve().parents[1] / "reports" / "f012"


def build(run_dir: Path, stdout_path: Path, binding: str) -> dict:
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    summary = _last_json_line(stdout_path)
    if summary.get("run_id") != run["run_id"]:
        raise SystemExit(f"stdout 摘要 run_id 与 run.json 不一致：{summary.get('run_id')!r}")
    elapsed = _prefilter_elapsed(run_dir / "prefilter.jsonl")
    started = datetime.fromisoformat(run["started_at"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(run["finished_at"].replace("Z", "+00:00"))
    registered = run["counts"]["registered"]
    return {
        "task": "F012/T019",
        "host": run["hostname"],
        "run_id": run["run_id"],
        "binding": binding,
        "status": run["status"],
        "stop_reason": run["stop_reason"],
        "termination": run["termination"],
        "device": run["device"],
        "quota": run["budget"]["quota"],
        "budget": run["budget"],
        "counts": run["counts"],
        "registered": registered,
        "evaluations": run["evaluations"],
        "duration_s": round((finished - started).total_seconds(), 1),
        "vram_limit_gb": run["vram_limit_gb"],
        "vram_peak_gb": summary.get("vram_peak_gb"),
        "prefilter_n": len(elapsed),
        "prefilter_ms_p50": round(statistics.median(elapsed), 1) if elapsed else None,
        "prefilter_ms_p95": (
            round(statistics.quantiles(elapsed, n=20)[18], 1) if len(elapsed) >= 2 else None
        ),
        "kronos_offload": run["kronos_offload"],
        "run_json_sha256": hashlib.sha256((run_dir / "run.json").read_bytes()).hexdigest(),
        "m2_capacity_finding": (
            None
            if registered >= CAPACITY_TARGET
            else f"夜槽入册 {registered}/{CAPACITY_TARGET}（{run['stop_reason']}），登记 M2 产能"
        ),
        "captured_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "captured_on": socket.gethostname(),
    }


def _last_json_line(path: Path) -> dict:
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        if line.startswith("{"):
            return json.loads(line)
    raise SystemExit(f"{path} 中没有 stdout JSON 摘要行")


def _prefilter_elapsed(path: Path) -> list[float]:
    if not path.exists():
        return []
    rows = path.read_text(encoding="utf-8").splitlines()
    return [float(json.loads(row)["elapsed_ms"]) for row in rows if row.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--stdout", type=Path, required=True)
    parser.add_argument("--binding", required=True)
    args = parser.parse_args()
    evidence = build(args.run_dir, args.stdout, args.binding)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.run_dir / "run.json", OUT_DIR / "capacity-run.json")
    (OUT_DIR / "capacity-evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: evidence[k] for k in ("run_id", "status", "registered")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
