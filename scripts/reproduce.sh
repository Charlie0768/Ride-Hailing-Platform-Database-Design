#!/usr/bin/env bash
# Isolated local verification. Usage: bash scripts/reproduce.sh /path/to/mysql
set -euo pipefail
RD_BASE="${1:?Provide the MySQL installation directory containing bin/mysqld}"
RD_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RD_TEMP="$(mktemp -d /tmp/ride-hailing-XXXXXX)"
export MYSQL_BIN="$RD_BASE/bin/mysql"
export MYSQL_SOCKET="$RD_TEMP/mysql.sock"
RD_CLIENT=("$MYSQL_BIN" --no-defaults --protocol=SOCKET "--socket=$MYSQL_SOCKET" -uroot)
cleanup() {
  "$RD_BASE/bin/mysqladmin" --no-defaults --protocol=SOCKET "--socket=$MYSQL_SOCKET" -uroot shutdown >/dev/null 2>&1 || true
}
trap cleanup EXIT
"$RD_BASE/bin/mysqld" --no-defaults --initialize-insecure "--basedir=$RD_BASE" "--datadir=$RD_TEMP/data" "--log-error=$RD_TEMP/init.log"
"$RD_BASE/bin/mysqld" --no-defaults "--basedir=$RD_BASE" "--datadir=$RD_TEMP/data" "--socket=$MYSQL_SOCKET" "--pid-file=$RD_TEMP/mysql.pid" --skip-networking --mysqlx=OFF "--log-error=$RD_TEMP/server.log" &
RD_PID=$!
RD_READY=0
for RD_ATTEMPT in $(seq 1 100); do
  if "${RD_CLIENT[@]}" -e 'SELECT 1' >/dev/null 2>&1; then RD_READY=1;break;fi
  if ! kill -0 "$RD_PID" 2>/dev/null; then cat "$RD_TEMP/server.log";exit 1;fi
  sleep 0.2
done
if [ "$RD_READY" -ne 1 ]; then cat "$RD_TEMP/server.log";exit 1;fi
python3 "$RD_ROOT/scripts/create_logic.py"
python3 "$RD_ROOT/scripts/generate_data.py"
for RD_FILE in 01_schema.sql 02_logic.sql 03_seed.sql 04_warehouse.sql 06_application_role.sql; do
  "${RD_CLIENT[@]}" < "$RD_ROOT/sql/$RD_FILE"
done
python3 "$RD_ROOT/scripts/run_validation.py"
python3 "$RD_ROOT/scripts/collect_report_evidence.py"
printf 'Verified using isolated data directory: %s\n' "$RD_TEMP"
