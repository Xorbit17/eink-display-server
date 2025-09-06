#!/usr/bin/env bash
set -euo pipefail

echo "▶ fresh-start: migrations + optional bootstrap"

# Wait for DB
if [ -n "${DATABASE_URL:-}" ]; then
  /usr/local/bin/wait-for-postgres.sh "${DATABASE_URL}"
fi

# Migrate
python manage.py migrate --noinput

# Create superuser if env provided (idempotent)
if [ -n "${ADMIN_USERNAME:-}" ] && [ -n "${ADMIN_PASSWORD:-}" ]; then
  echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
u = User.objects.filter(username='${ADMIN_USERNAME}').first(); \
u or User.objects.create_superuser('${ADMIN_USERNAME}', '${ADMIN_EMAIL:-}', '${ADMIN_PASSWORD}')" \
  | python manage.py shell
fi

# Optional: call your project seeding (guard if command missing)
if python manage.py help | grep -qE '^  seed$'; then
  python manage.py seed || true
fi

echo "✅ fresh-start completed"
