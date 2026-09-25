#!/usr/bin/env bash
# F008 批 1/2 回填启动器（执行机 qiaozhi-lt 上运行；断点续跑，可反复执行）
#
# 用法：
#   bash scripts/f008-backfill.sh 1            # 批 1（成交额前 30）
#   bash scripts/f008-backfill.sh 2            # 批 2（第 31–40）
#   BACKFILL_FETCH_LIMIT=500 bash scripts/f008-backfill.sh 1   # 改每请求 K 线数（默认 1000）
#
# 续跑：中断后**原样重跑同一批**即可——逐 pair 断点由 backfill_progress.next_since 继续，
# 已完成的 pair 由进度账本识别为 complete 直接跳过（幂等 upsert，不会产生重复行）。
#
# 说明：
# - 宇宙定义与湖都在生产路径（F008 的代码在 feature worktree，数据在共享湖）；
# - 代理经环境变量注入：默认取 deployment/.env 的 BINANCE_HTTPS_PROXY；
# - 输出走 nohup 日志：reports/backfill/<batch>-<timestamp>.log；
# - 中断后原样重跑即可从断点续跑（进度账本 backfill_progress + BackfillRun）。
set -euo pipefail

BATCH="${1:?用法: f008-backfill.sh <1|2>}"
REPO_F008="${REPO_F008:-/home/georg/projects/alphamill-universe}"
PROD="${PROD:-/home/georg/projects/alphamill}"
LAKE="${LAKE:-$PROD/lake}"
UNIVERSE="${UNIVERSE:-sha256:b40651e2a101c6ba3253d01e2e811d1e0d6db1008505637c6dbabc2f53de9804}"
START="${START:-2024-09-10T00:00:00Z}"
END="${END:-2026-09-10T15:52:00Z}"

set -a
# shellcheck disable=SC1091
. "$PROD/deployment/.env"
set +a

cd "$REPO_F008"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$REPO_F008/reports/backfill/batch${BATCH}-${STAMP}.log"
mkdir -p "$(dirname "$LOG")"

# 必须在加载 deployment/.env **之后**取值，且用独立命名空间：该 .env 里的 `FETCH_LIMIT=5`
# 是给采集器的，同名会把回填打成 5 根/请求（2026-09-24 实测：3,402 批只推进 17,005 行）。
# 1000 = Binance 现货 klines 单请求上限（F001 默认 100 会让请求数多 10 倍）。
FETCH="${BACKFILL_FETCH_LIMIT:-1000}"
ARGS=(--universe "$UNIVERSE" --batch "$BATCH" --start "$START" --end "$END"
      --lake-root "$LAKE" --reports-dir "$REPO_F008/reports/backfill"
      --fetch-limit "$FETCH")
echo "start batch=$BATCH at $STAMP -> $LOG"
PYTHONPATH=src nohup .venv/bin/python -m alphamill.data_bridge.universe backfill "${ARGS[@]}" \
  >"$LOG" 2>&1 &
echo "pid=$! log=$LOG"
