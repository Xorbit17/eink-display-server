#!/usr/bin/env bash
set -euo pipefail

# Usage: wait-for-postgres.sh "postgres://user:pass@host:5432/dbname"
DB_URL="${1:-}"

if [ -z "$DB_URL" ]; then
  echo "wait-for-postgres: DATABASE_URL not provided"; exit 1
fi

echo "Waiting for Postgres…"
python - <<PY
import os, sys, time
import urllib.parse as up
import psycopg2

url = up.urlparse("${DB_URL}")
for i in range(60):
    try:
        conn = psycopg2.connect(
            dbname=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port or 5432,
        )
        conn.close()
        print("Postgres is ready.")
        sys.exit(0)
    except Exception as e:
        time.sleep(1)
print("Postgres wait timeout.", file=sys.stderr)
sys.exit(1)
PY
