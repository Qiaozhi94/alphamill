#!/usr/bin/env bash
# F008 分批回填的**时间片**执行器：把数天的长跑切成一片片（默认 30 分钟）循环跑。
#
# 为什么分片：单片被打断（网络抖动、代理封禁、机器重启、人工中止）只损失一片的工作量；
# 断点由 `backfill_progress.next_since` 与 `BackfillRun` 记录，下一片自动续上，
# 且所有分片共用同一份 `BackfillRun`（`--resume-run-id`），证据不碎。
#
# 用法：
#   bash scripts/f008-backfill-chunks.sh 1                 # 批 1，默认 30 分钟/片
#   CHUNK_MINUTES=15 MAX_CHUNKS=200 bash scripts/f008-backfill-chunks.sh 2
#   MAX_CHUNKS=1 bash scripts/f008-backfill-chunks.sh 1    # 只跑一片（人工逐片放行）
#   RUN_ID=<run_id> MAX_CHUNKS=1 bash scripts/f008-backfill-chunks.sh 1   # 续跑同一份记录
#
# 退出条件：本批全部 pair completed/unavailable，或达到 MAX_CHUNKS，或连续 3 片无进展。
set -uo pipefail

BATCH="${1:?用法: f008-backfill-chunks.sh <1|2>}"
REPO_F008="${REPO_F008:-/home/georg/projects/alphamill-universe}"
PROD="${PROD:-/home/georg/projects/alphamill}"
LAKE="${LAKE:-$PROD/lake}"
UNIVERSE="${UNIVERSE:-sha256:6d85a249e8fe509518443afb3407d0ed6ea736260c570c8f860676e0c466a709}"
START="${START:-2024-09-10T00:00:00Z}"
END="${END:-2026-09-10T15:52:00Z}"
CHUNK_MINUTES="${CHUNK_MINUTES:-30}"
MAX_CHUNKS="${MAX_CHUNKS:-96}"          # 96 × 30min = 48h 上限
FETCH="${FETCH_LIMIT:-1000}"
LOG_DIR="$REPO_F008/reports/backfill"
mkdir -p "$LOG_DIR"

set -a
# shellcheck disable=SC1091
. "$PROD/deployment/.env"
set +a
cd "$REPO_F008"

# RUN_ID 可由环境传入以续跑同一份 BackfillRun（人工逐片放行时用）
RUN_ID="${RUN_ID:-}"
stall=0
prev_done=-1

for chunk in $(seq 1 "$MAX_CHUNKS"); do
  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  log="$LOG_DIR/chunk-b${BATCH}-${stamp}.log"
  args=(--universe "$UNIVERSE" --batch "$BATCH" --start "$START" --end "$END"
        --lake-root "$LAKE" --reports-dir "$LOG_DIR"
        --fetch-limit "$FETCH" --max-runtime-minutes "$CHUNK_MINUTES")
  if [[ -n "$RUN_ID" ]]; then
    args+=(--resume-run-id "$RUN_ID")
  fi

  echo "[$(date -u +%H:%M:%SZ)] 片 $chunk/$MAX_CHUNKS 开始（${CHUNK_MINUTES} 分钟上限）→ $log"
  PYTHONPATH=src .venv/bin/python -m alphamill.data_bridge.universe backfill "${args[@]}" \
    > "$log.json" 2> "$log.err"
  code=$?

  RUN_ID="$(python3 -c "import json,sys;print(json.load(open('$log.json'))['run_id'])" 2>/dev/null || echo "$RUN_ID")"
  read -r done total <<<"$(python3 - "$LOG_DIR" "$RUN_ID" <<'PY' 2>/dev/null || echo "-1 -1"
import json, sys, pathlib
root, run_id = sys.argv[1], sys.argv[2]
d = json.loads((pathlib.Path(root) / run_id / "run.json").read_text())
pairs = d["pairs"]
done = sum(1 for p in pairs if p["status"] in {"completed", "unavailable"})
print(done, len(pairs))
PY
)"
  echo "[$(date -u +%H:%M:%SZ)] 片 $chunk 结束 exit=$code 完成 $done/$total"

  if [[ "$total" == "-1" ]]; then
    echo "  警告：读不到 run 记录，按无进展计"
    stall=$((stall + 1))
  elif [[ "$done" == "$total" ]]; then
    echo "本批全部完成（$done/$total）"
    exit 0
  elif [[ "$done" == "$prev_done" ]]; then
    stall=$((stall + 1))
    echo "  本片无进展（$stall/3）"
  else
    stall=0
  fi
  prev_done="$done"
  if (( stall >= 3 )); then
    echo "连续 3 片无进展，停止并保留现场供人工排查"
    exit 1
  fi
  sleep 5
done

echo "达到分片上限 $MAX_CHUNKS，仍未跑完：可原样重跑本脚本继续"
exit 1
