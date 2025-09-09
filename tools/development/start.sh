#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1

DJANGO_CMD="python manage.py runserver 0.0.0.0:8000"
DAEMON_CMD="python manage.py daemon"

# Trap children properly
_term() { echo "Stopping…"; kill -TERM "$DJANGO_PID" "$DAEMON_PID" 2>/dev/null || true; }
trap _term TERM INT

# Start processes
bash -lc "$DAEMON_CMD" &
DAEMON_PID=$!

bash -lc "$DJANGO_CMD" &
DJANGO_PID=$!

# Wait for both
wait -n "$DJANGO_PID" "$DAEMON_PID"
EXIT_CODE=$?

# If one dies, kill the other
kill -TERM "$DJANGO_PID" "$DAEMON_PID" 2>/dev/null || true
wait || true

exit $EXIT_CODE
