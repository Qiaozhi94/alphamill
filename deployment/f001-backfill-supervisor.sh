#!/usr/bin/env bash
# F001 回填 supervisor：等当前回填进程退出后，断点续传重跑直到 6 个交易对全部
# complete（BACKFILL_END 钉死与首跑一致，保证跨进程 resume 命中），随后执行
# 衍生品回填（binanceusdm）。日志追加 /tmp/f001-backfill.log。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

set -a; source deployment/.env; set +a
set -a; source deployment/f001-backfill-window.env; set +a
export DB_HOST=127.0.0.1
export BACKFILL_START="$BACKFILL_WINDOW_START"
export BACKFILL_END="$BACKFILL_WINDOW_END"
export BACKFILL_FETCH_LIMIT=1000
export LOG_LEVEL=INFO
export BINANCE_HTTPS_PROXY="${BINANCE_HTTPS_PROXY:-}"
BACKFILL_SYMBOLS="${SYMBOLS:-BTC/USDT,ETH/USDT}"
IFS=',' read -r -a CONFIGURED_SYMBOLS <<< "$BACKFILL_SYMBOLS"
EXPECTED_SYMBOL_COUNT=0
for configured_symbol in "${CONFIGURED_SYMBOLS[@]}"; do
  [ -n "${configured_symbol// /}" ] && EXPECTED_SYMBOL_COUNT=$((EXPECTED_SYMBOL_COUNT + 1))
done

psql_query() {
  docker exec quant-timescaledb psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "$1"
}

# 等首跑进程退出（PID 由调用方传入 $1）
if [ -n "${1:-}" ]; then
  while kill -0 "$1" 2>/dev/null; do sleep 30; done
fi

for pass in 2 3 4 5 6 7 8 9 10; do
  # 只喂未完成的 symbol：权威窗口内最新状态为 complete 的不再重跑
  #（模块的 load_progress 不跳过 complete，整轮重喂会无谓重下已完成的百万行）。
  INCOMPLETE=$(psql_query "SELECT coalesce(string_agg(symbol, ',' ORDER BY symbol), '') FROM (SELECT symbol, status, row_number() OVER (PARTITION BY symbol ORDER BY updated_at DESC) AS rn FROM backfill_progress WHERE exchange='binance' AND timeframe='1m' AND target_start='$BACKFILL_START' AND target_end='$BACKFILL_END') t WHERE rn=1 AND status NOT IN ('complete', 'unavailable');")
  DONE=$(psql_query "SELECT count(*) FROM (SELECT DISTINCT symbol FROM backfill_progress WHERE exchange='binance' AND timeframe='1m' AND status IN ('complete', 'unavailable') AND target_start='$BACKFILL_START' AND target_end='$BACKFILL_END') t;")
  echo "$(date -u +%FT%TZ) [supervisor] pass=$pass completed=$DONE/$EXPECTED_SYMBOL_COUNT todo=[$INCOMPLETE]"
  [ "$DONE" -ge "$EXPECTED_SYMBOL_COUNT" ] && break
  [ -z "$INCOMPLETE" ] && break
  SYMBOLS="$INCOMPLETE" PYTHONPATH="$REPO_ROOT/src" .venv/bin/python -m alphamill.data_bridge.collector.historical_backfill >> /tmp/f001-backfill.log 2>&1
done

if [ "$DONE" -lt "$EXPECTED_SYMBOL_COUNT" ]; then
  echo "$(date -u +%FT%TZ) [supervisor] OHLCV 回填未完成：$DONE/$EXPECTED_SYMBOL_COUNT" >&2
  exit 1
fi

echo "$(date -u +%FT%TZ) [supervisor] OHLCV 回填收口，开始衍生品回填"
DERIVATIVES_EXCHANGE="${DERIVATIVES_EXCHANGE:-binanceusdm}" \
DERIVATIVES_SYMBOLS="${DERIVATIVES_SYMBOLS:-$BACKFILL_SYMBOLS}" \
DERIVATIVES_DATASETS="funding,open_interest" \
DERIVATIVES_START="$BACKFILL_WINDOW_START" \
DERIVATIVES_END="$BACKFILL_WINDOW_END" \
DERIVATIVES_FETCH_LIMIT=1000 \
BINANCEUSDM_HTTPS_PROXY="${BINANCEUSDM_HTTPS_PROXY:-${BINANCE_HTTPS_PROXY:-}}" \
LOG_LEVEL=INFO \
  PYTHONPATH="$REPO_ROOT/src" .venv/bin/python -m alphamill.data_bridge.collector.derivatives_market_backfill >> /tmp/f001-backfill.log 2>&1

echo "$(date -u +%FT%TZ) [supervisor] 全部回填任务结束"
