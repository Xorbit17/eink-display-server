#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# eink-display-server local dev runner (server locally, Postgres in Docker)
# Usage:
#   ./tools/dev/dev.sh             # start normally
#   ./tools/dev/dev.sh --start-fresh  # wipe DB, clear migrations, rebuild
#
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "$SCRIPT_DIR/.env.dev"

source "$SCRIPT_DIR/.env.dev"

# --- Config (defaults; override via .env.dev) ---
PROJECT_NAME="${PROJECT_NAME:-eink-display-server}"
APP_NAME="${APP_NAME:-dashboard}"

DJANGO_ADDR="${DJANGO_ADDR:-0.0.0.0:8000}"
DISCOVERY_PORT="${DISCOVERY_PORT:-51234}"
ADMIN_USERNAME="${ADMIN_USERNAME:-dv}"
ADMIN_PASSWORD="${ADMIN_PASSWORD}"
ADMIN_EMAIL="${ADMIN_EMAIL}"
ENV="dvelopment"

# APIs (optional)
# OPENAI_API_KEY:(Secret in .env.dev)
# OPENWEATHERMAP_API_KEY:(Secret in .env.dev)

APP_DIR="${APP_DIR:-$REPO_ROOT/$APP_NAME}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-$APP_DIR/migrations}"

DJANGO_CMD="${DJANGO_CMD:-python manage.py runserver $DJANGO_ADDR}"
DAEMON_CMD="${DAEMON_CMD:-python manage.py daemon}"

log()  { echo -e "\033[1;34m[dev]\033[0m $*"; }
warn() { echo -e "\033[1;33m[warn]\033[0m $*" >&2; }
err()  { echo -e "\033[1;31m[err]\033[0m  $*" >&2; }

require() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing dependency: $1"; exit 1; }
}

remove_old_migrations() {
  if [[ -d "$MIGRATIONS_DIR" ]]; then
    log "Removing old migrations in ${MIGRATIONS_DIR} (keeping __init__.py)..."
    find "$MIGRATIONS_DIR" -type f -not -name "__init__.py" -delete
  else
    warn "Migrations directory not found at: $MIGRATIONS_DIR"
  fi
}

django_env_export() {
  export PYTHONUNBUFFERED=1
  export DJANGO_SETTINGS_MODULE="${PROJECT_NAME}.settings"

  export DISCOVERY_PORT="${DISCOVERY_PORT}"

  export ADMIN_USERNAME="${ADMIN_USERNAME}"
  export ADMIN_PASSWORD="${ADMIN_PASSWORD}"
  export ADMIN_EMAIL="${ADMIN_EMAIL}"

  export IMAGE_INPUT_DIR="${IMAGE_INPUT_DIR}"
  export GENERATED_OUTPUT_DIR="${GENERATED_OUTPUT_DIR}"

  export OPENAI_API_KEY="${OPENAI_API_KEY}"
  export OPENWEATHERMAP_API_KEY="${OPENWEATHERMAP_API_KEY}"
  export ENV="${ENV}"
  
}

django_manage() {
  log "manage.py $*"
  python manage.py "$@"
}

create_superuser_if_missing() {
  log "Ensuring Django superuser '${ADMIN_USERNAME}' exists..."
  python - <<'PY'
import os
import django

# Ensure settings are available even if the shell env is odd
os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.getenv("DJANGO_SETTINGS_MODULE", "eink-display-server.settings"))

django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ["ADMIN_USERNAME"]
email = os.environ.get("ADMIN_EMAIL") or ""
password = os.environ["ADMIN_PASSWORD"]

u = User.objects.filter(username=username).first()
if not u:
    User.objects.create_superuser(username, email, password)
    print(f"Created superuser {username}")
else:
    print(f"Superuser {username} already exists")
PY
}

do_start_fresh() {
  rm ./db.sqlite3 || true
  remove_old_migrations
  django_env_export
  django_manage makemigrations "${APP_NAME}"
  django_manage migrate
  create_superuser_if_missing
  django_manage seed

  log "Fresh start complete."
}

run_processes() {
  django_env_export
  log "Starting local dev:"
  echo "  - Django:  $DJANGO_ADDR"
  echo "  - Daemon:  ${DAEMON_CMD}"
  _term() { echo "Stopping…"; kill -TERM "${DJ_PID:-0}" "${DM_PID:-0}" 2>/dev/null || true; }
  trap _term TERM INT

  # Start daemon first (so it can subscribe / schedule)
  bash -lc "$DAEMON_CMD" &
  DM_PID=$!

  # Start server
  bash -lc "$DJANGO_CMD" &
  DJ_PID=$!

  # Wait for either to exit
  set +e
  wait -n "$DJ_PID" "$DM_PID"
  EXIT_CODE=$?
  set -e

  # If one dies, kill the other
  kill -TERM "$DJ_PID" "$DM_PID" 2>/dev/null || true
  wait || true

  exit $EXIT_CODE
}

# --- Entry point ---
require python

ACTION="${1:-}"
case "${ACTION}" in
  --start-fresh)
    do_start_fresh
    run_processes
    ;;
  "" )
    run_processes
    ;;
  *)
    err "Unknown option: ${ACTION}"
    echo "Usage: $0 [--start-fresh]"
    exit 2
    ;;
esac
