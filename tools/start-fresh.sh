#!/bin/bash
set -euo pipefail

# --- Configurable bits ---
APP_NAME="dashboard"
DB_FILE="db.sqlite3"

SUPERUSER_NAME="dv"
SUPERUSER_EMAIL="dennis.vaneecke@gmail.com"
SUPERUSER_PASSWORD="eicae6yu"
# --------------------------

echo "Resetting Django project for app: $APP_NAME"

# 1. Remove migration files (but keep __init__.py)
find "$APP_NAME/migrations" -type f -not -name "__init__.py" -delete

# 2. Remove SQLite DB (if it exists)
if [ -f "$DB_FILE" ]; then
  rm "$DB_FILE"
  echo "Deleted $DB_FILE"
fi

# 3. Recreate migrations and DB schema
python manage.py makemigrations "$APP_NAME"
python manage.py migrate

# 4. Create superuser non-interactively
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='$SUPERUSER_NAME').exists() or \
User.objects.create_superuser('$SUPERUSER_NAME', '$SUPERUSER_EMAIL', '$SUPERUSER_PASSWORD')" \
| python manage.py shell

python manage.py seed

echo "✅ Fresh start complete. Superuser: $SUPERUSER_NAME / $SUPERUSER_PASSWORD"
