#!/usr/bin/env bash
# AlphaMill 每日 NAS 备份同步（migration-plan §七 / tasks T015）
#
# 同步三类资产到 UGREEN NAS (root@10.31.0.254:/volume1/alphamill-backups/)：
#   db/      TimescaleDB 逻辑 dump（pg_dump -Fc，容器内 socket，免开 5432）
#   reports/ 对账与回填报告
#   lake/    Parquet 湖分区（F002 起生效，目录位预留）
#
# 保留策略：本地 7 天滚动，NAS 30 天。
# 调度：systemd user timer（deployment/alphamill-backup.{service,timer}），
#       或手工 `bash deployment/backup-nas.sh`。退出码非 0 = 失败。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAS_HOST="${ALPHAMILL_NAS_HOST:-10.31.0.254}"
NAS_USER="${ALPHAMILL_NAS_USER:-root}"
NAS_BASE="/volume1/alphamill-backups"
LOCAL_BACKUP_DIR="$REPO_ROOT/deployment/backups"
DATE="$(date -u +%Y%m%d)"
LOG_TAG="[backup $DATE]"

# shellcheck disable=SC1091
set -a; source "$REPO_ROOT/deployment/.env"; set +a

SSH_OPTS=(
  -i "${ALPHAMILL_NAS_KEY:-$HOME/.ssh/id_ed25519_remote}"
  -o StrictHostKeyChecking=no
  -o UserKnownHostsFile=/dev/null
  -o ConnectTimeout=15
)

log() { echo "$(date -u +%FT%TZ) $LOG_TAG $*"; }

mkdir -p "$LOCAL_BACKUP_DIR/db" "$LOCAL_BACKUP_DIR/logs"

# 1) TimescaleDB 逻辑 dump
DUMP="$LOCAL_BACKUP_DIR/db/alphamill-$DATE.dump"
log "pg_dump -> $DUMP"
docker exec quant-timescaledb pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$DUMP"
[ -s "$DUMP" ] || { log "FATAL: dump 为空"; exit 1; }
log "dump 大小 $(du -h "$DUMP" | cut -f1)"

# 2) 同步到 NAS（tar-over-ssh：UGREEN 登录 shell 会回显 "proxy: OFF"，污染 rsync 协议流，
#    故用字节流传输，天然免疫登录前导输出）
log "tar/ssh db/reports/lake -> $NAS_USER@$NAS_HOST:$NAS_BASE/"
ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "mkdir -p $NAS_BASE/db $NAS_BASE/reports $NAS_BASE/lake" 2>/dev/null
cat "$DUMP" | ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "cat > $NAS_BASE/db/alphamill-$DATE.dump" 2>/dev/null
tar -C "$REPO_ROOT/reports" -czf - . | ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "tar -xzf - -C $NAS_BASE/reports" 2>/dev/null
if [ -d "$REPO_ROOT/lake" ]; then
  tar -C "$REPO_ROOT/lake" -czf - . | ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "tar -xzf - -C $NAS_BASE/lake" 2>/dev/null
else
  log "lake/ 尚不存在，跳过（F002 生效）"
fi

# 3) 保留策略：本地 7 天，NAS 30 天
find "$LOCAL_BACKUP_DIR/db" -name 'alphamill-*.dump' -mtime +7 -delete
ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" \
  "find $NAS_BASE/db -name 'alphamill-*.dump' -mtime +30 -delete" 2>/dev/null

# 4) NAS 端产物校验
NAS_DUMPS=$(ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "ls -1 $NAS_BASE/db/alphamill-$DATE.dump" 2>/dev/null)
[ -n "$NAS_DUMPS" ] || { log "FATAL: NAS 端未见今日 dump"; exit 1; }
log "完成：NAS 端 $NAS_DUMPS"
