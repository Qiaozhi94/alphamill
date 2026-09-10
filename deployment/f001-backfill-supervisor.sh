#!/usr/bin/env bash
# F001 回填 supervisor：等当前回填进程退出后，断点续传重跑直到 6 个交易对全部
# complete（BACKFILL_END 钉死与首跑一致，保证跨进程 resume 命中），随后执行
# 衍生品回填（binanceusdm）。日志追加 /tmp/f001-backfill.log。
set -u
cd /home/georg/projects/alphamill

set -a; source deployment/.env; set +a
export DB_HOST=127.0.0.1
export BACKFILL_START=2024-09-10T00:00:00Z
export BACKFILL_END=2026-09-10T15:52:00Z
export BACKFILL_FETCH_LIMIT=1000
export LOG_LEVEL=INFO
export BINANCE_HTTPS_PROXY=http://10.31.0.254:7890

PSQL="docker exec quant-timescaledb psql -U quant -d quant -t -A -c"

# 等首跑进程退出（PID 由调用方传入 $1）
if [ -n "${1:-}" ]; then
  while kill -0 "$1" 2>/dev/null; do sleep 30; done
fi

for pass in 2 3 4 5 6 7 8; do
  DONE=$($PSQL "SELECT count(*) FROM (SELECT DISTINCT symbol FROM backfill_progress WHERE exchange='binance' AND timeframe='1m' AND status='complete' AND target_end='2026-09-10 15:52:00+00:00' AND target_start='2024-09-10 00:00:00+00:00') t;")
  echo "$(date -u +%FT%TZ) [supervisor] pass=$pass completed_symbols=$DONE/6"
  [ "$DONE" -ge 6 ] && break
  .venv/bin/python -m src.alphamill.data_bridge.collector.historical_backfill >> /tmp/f001-backfill.log 2>&1
done

echo "$(date -u +%FT%TZ) [supervisor] OHLCV 回填收口，开始衍生品回填"
DERIVATIVES_EXCHANGE=binanceusdm \
DERIVATIVES_SYMBOLS="BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT" \
DERIVATIVES_DATASETS="funding,open_interest" \
DERIVATIVES_START=2024-09-10T00:00:00Z \
DERIVATIVES_END=2026-09-10T15:52:00Z \
DERIVATIVES_FETCH_LIMIT=1000 \
BINANCEUSDM_HTTPS_PROXY=http://10.31.0.254:7890 \
LOG_LEVEL=INFO \
  .venv/bin/python -m src.alphamill.data_bridge.collector.derivatives_market_backfill >> /tmp/f001-backfill.log 2>&1

echo "$(date -u +%FT%TZ) [supervisor] 全部回填任务结束"
