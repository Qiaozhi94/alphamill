#!/bin/bash
# 全新数据库的迁移入口（docker-entrypoint-initdb.d 阶段执行）。
#
# 与既有库的升级入口 tools/apply_migrations.py **共用同一个版本账本**
# schema_migrations：initdb 路径应用完每个文件后同样登记版本，否则 runner 首跑
# 会把全部迁移再重放一遍（C402）。迁移文件必须幂等，见 tools/apply_migrations.py。
set -euo pipefail

MIGRATION_DIR=/docker-entrypoint-initdb.d/migrations

run_sql() { psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" "$@"; }

run_sql -c 'CREATE TABLE IF NOT EXISTS schema_migrations (
    version    TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
)'

shopt -s nullglob
for migration in "$MIGRATION_DIR"/*.sql; do
  version="$(basename "$migration")"
  echo "initdb: applying $version"
  run_sql -f "$migration"
  run_sql -c "INSERT INTO schema_migrations (version) VALUES ('$version') ON CONFLICT DO NOTHING"
done
echo "initdb: migrations recorded in schema_migrations"
