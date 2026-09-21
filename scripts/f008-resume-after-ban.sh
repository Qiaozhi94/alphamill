#!/usr/bin/env bash
# F008：Binance IP 封禁解除后的续跑（发现 → 冻结 → 批 1 回填）
#
# 背景：2026-09-21 发现流程按 ccxt rateLimit（50ms）突发 15 请求/秒，撞上 Binance
# `-1003`（418，出口 IP 封禁 1 小时）。封禁期内**不得再探测**（会升级为更长封禁），
# 因此本脚本先睡到封禁到期（+20s 余量），只探一次，再按保守节奏继续。
#
# 用法：bash scripts/f008-resume-after-ban.sh <ban_epoch_seconds> [universe_batch]
set -euo pipefail

BAN_UNTIL="${1:?用法: f008-resume-after-ban.sh <ban_epoch_seconds>}"
BATCH="${2:-1}"
REPO_F008="${REPO_F008:-/home/georg/projects/alphamill-universe}"
PROD="${PROD:-/home/georg/projects/alphamill}"
LAKE="${LAKE:-$PROD/lake}"
LOG_DIR="$REPO_F008/reports/backfill"
mkdir -p "$LOG_DIR"

now="$(date +%s)"
wait_s=$(( BAN_UNTIL - now + 20 ))
if (( wait_s > 0 )); then
  echo "[$(date -u +%H:%M:%SZ)] 封禁未到期，等待 ${wait_s}s（期间不探测，避免升级封禁）"
  sleep "$wait_s"
fi

set -a
# shellcheck disable=SC1091
. "$PROD/deployment/.env"
set +a

probe="$(curl -sS -m 15 -x "$BINANCE_HTTPS_PROXY" -o /dev/null -w '%{http_code}' \
  https://api.binance.com/api/v3/ping || true)"
echo "[$(date -u +%H:%M:%SZ)] 封禁后首次探测: HTTP $probe"
if [[ "$probe" != "200" ]]; then
  echo "仍不可用（$probe）：不继续打请求，请人工确认后重跑本脚本"
  exit 1
fi

# 封禁期内采集器已暂停（避免每秒重试把 1 小时封禁升级为更长封禁），解禁后恢复
if ! docker ps --filter name=quant-data-collector --format '{{.Names}}' | grep -q .; then
  docker start quant-data-collector >/dev/null && echo "[$(date -u +%H:%M:%SZ)] 采集器已恢复"
fi

cd "$REPO_F008"
echo "[$(date -u +%H:%M:%SZ)] 运行发现（保守节奏 1s/市场）"
PYTHONPATH=src .venv/bin/python -m alphamill.data_bridge.universe discover --lake-root "$LAKE" \
  > "$LOG_DIR/discover-postban.json" 2>"$LOG_DIR/discover-postban.err"

UNIVERSE="$(python3 -c "import json;print(json.load(open('$LOG_DIR/discover-postban.json'))['universe_id'])")"
echo "[$(date -u +%H:%M:%SZ)] 新 universe_id=$UNIVERSE"

PYTHONPATH=src .venv/bin/python -m alphamill.data_bridge.universe freeze \
  --def "$UNIVERSE" --confirm --lake-root "$LAKE"

echo "[$(date -u +%H:%M:%SZ)] 启动批 $BATCH 回填"
UNIVERSE="$UNIVERSE" bash "$REPO_F008/scripts/f008-backfill.sh" "$BATCH"
