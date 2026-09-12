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
# shellcheck disable=SC1091
set -a; source "$REPO_ROOT/deployment/.env"; set +a

NAS_HOST="${ALPHAMILL_NAS_HOST:-10.31.0.254}"
NAS_USER="${ALPHAMILL_NAS_USER:-root}"
NAS_BASE="/volume1/alphamill-backups"
LOCAL_BACKUP_DIR="$REPO_ROOT/deployment/backups"
DATE="$(date -u +%Y%m%d)"
LOG_TAG="[backup $DATE]"
NAS_KNOWN_HOSTS="${ALPHAMILL_NAS_KNOWN_HOSTS:-$HOME/.ssh/alphamill_known_hosts}"

SSH_OPTS=(
  -i "${ALPHAMILL_NAS_KEY:-$HOME/.ssh/id_ed25519_remote}"
  -o StrictHostKeyChecking=yes
  -o UserKnownHostsFile="$NAS_KNOWN_HOSTS"
  -o ConnectTimeout=15
)

log() { echo "$(date -u +%FT%TZ) $LOG_TAG $*"; }

[ -f "$NAS_KNOWN_HOSTS" ] || {
  log "FATAL: NAS known_hosts 不存在：$NAS_KNOWN_HOSTS"
  exit 1
}
ssh-keygen -F "$NAS_HOST" -f "$NAS_KNOWN_HOSTS" >/dev/null || {
  log "FATAL: NAS host key 未预注册：$NAS_HOST"
  exit 1
}

# UGREEN NAS 的 sshd 会在 ~10MB 处 reset 入站流式 cat，且登录 shell 回显破坏
# SFTP/rsync 协议——因此用 4MB 分块追加 + 逐块字节数校验 + 失败截断回退重试。
nas_append_chunk() { # $1=本地文件 $2=skip_bytes $3=count_bytes $4=远端路径
  dd if="$1" bs=4194304 iflag=skip_bytes,count_bytes skip="$2" count="$3" 2>/dev/null \
    | ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "cat >> $4" 2>/dev/null
}

transfer_to_nas() { # $1=本地文件 $2=远端路径
  local src="$1" dst="$2"
  local size pos=0 chunk=4194304 want have expected try
  size=$(stat -c %s "$src")
  ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "rm -f $dst && touch $dst" 2>/dev/null
  while [ "$pos" -lt "$size" ]; do
    want=$chunk
    [ $((pos + want)) -gt "$size" ] && want=$((size - pos))
    for try in 1 2 3 4 5; do
      if ! nas_append_chunk "$src" "$pos" "$want" "$dst"; then
        have=0
      else
        have=$(ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "stat -c %s $dst" 2>/dev/null | tail -n 1) || have=0
      fi
      expected=$((pos + want))
      [ "$have" = "$expected" ] && break
      log "chunk@$pos 第${try}次校验不符(have=$have want=$expected)，截断重试"
      if ! ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "truncate -s $pos $dst" 2>/dev/null; then
        log "FATAL: 无法截断远端文件 $dst"
        return 1
      fi
    done
    [ "$have" = "$expected" ] || { log "FATAL: chunk@$pos 重试耗尽"; return 1; }
    pos=$((pos + want))
  done
  return 0
}

transfer_directory_to_nas() { # $1=local directory name; $2=remote directory name
  local source_dir="$REPO_ROOT/$1" remote_dir="$2"
  local archive="$LOCAL_BACKUP_DIR/$remote_dir-$DATE.tar.gz"
  local remote_archive="$NAS_BASE/$remote_dir/$DATE.tar.gz"
  local local_md5 remote_md5

  mkdir -p "$source_dir"
  tar -C "$source_dir" -czf "$archive" .
  ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "mkdir -p $NAS_BASE/$remote_dir" 2>/dev/null
  transfer_to_nas "$archive" "$remote_archive"
  local_md5=$(md5sum "$archive" | awk '{print $1}')
  remote_md5=$(ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" \
    "md5sum $remote_archive" 2>/dev/null | tail -n 1 | awk '{print $1}')
  [ "$remote_md5" = "$local_md5" ] || {
    log "FATAL: $remote_dir md5 不一致 local=$local_md5 remote=$remote_md5"
    return 1
  }
  ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" \
    "tar -xzf $remote_archive -C $NAS_BASE/$remote_dir && rm -f $remote_archive" 2>/dev/null
  rm -f "$archive"
  log "$remote_dir 校验一致 md5=$local_md5"
}

mkdir -p "$LOCAL_BACKUP_DIR/db" "$LOCAL_BACKUP_DIR/logs"

# 1) TimescaleDB 逻辑 dump
DUMP="$LOCAL_BACKUP_DIR/db/alphamill-$DATE.dump"
log "pg_dump -> $DUMP"
docker exec quant-timescaledb pg_dump -U "$DB_USER" -d "$DB_NAME" -Fc > "$DUMP"
[ -s "$DUMP" ] || { log "FATAL: dump 为空"; exit 1; }
docker exec -i quant-timescaledb pg_restore --list < "$DUMP" >/dev/null
log "dump 大小 $(du -h "$DUMP" | cut -f1)"

# 2) 同步到 NAS（所有产物都走分块、字节数和 md5 校验通道）
log "db/reports/lake -> $NAS_USER@$NAS_HOST:$NAS_BASE/"
transfer_to_nas "$DUMP" "$NAS_BASE/db/alphamill-$DATE.dump" || { log "FATAL: dump 传输失败"; exit 1; }
# 传输完整性：双端字节数 + md5
local_size=$(stat -c %s "$DUMP")
remote_md5=$(ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "md5sum $NAS_BASE/db/alphamill-$DATE.dump" 2>/dev/null | tail -n 1 | awk '{print $1}')
local_md5=$(md5sum "$DUMP" | awk '{print $1}')
[ "$remote_md5" = "$local_md5" ] || { log "FATAL: md5 不一致 local=$local_md5 remote=$remote_md5"; exit 1; }
log "dump 校验一致 md5=$local_md5 size=$local_size"
transfer_directory_to_nas reports reports || { log "FATAL: reports 传输失败"; exit 1; }
if [ -d "$REPO_ROOT/lake" ]; then
  transfer_directory_to_nas lake lake || { log "FATAL: lake 传输失败"; exit 1; }
else
  log "lake/ 尚不存在，跳过（F002 生效）"
fi

# 3) 保留策略：本地 7 天，NAS 30 天
find "$LOCAL_BACKUP_DIR/db" -name 'alphamill-*.dump' -mtime +7 -delete
ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" \
  "find $NAS_BASE/db -name 'alphamill-*.dump' -mtime +30 -delete" 2>/dev/null

# 4) NAS 端产物校验（grep -c 输出纯净计数，天然免疫登录回显）
NAS_DUMPS=$(ssh "${SSH_OPTS[@]}" "$NAS_USER@$NAS_HOST" "ls -1 $NAS_BASE/db/alphamill-$DATE.dump" 2>/dev/null | grep -c "alphamill-$DATE.dump")
if [ "$NAS_DUMPS" -ge 1 ]; then log "完成：NAS 端副本已确认（$NAS_DUMPS）"; else log "FATAL: NAS 端未见今日 dump"; exit 1; fi
