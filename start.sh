#!/bin/bash
# Production startup script for Railway deployment
# Runs migrations, collects static files, then starts gunicorn with proper signal handling
set -e

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting Gunicorn..."
exec gunicorn jkr.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --timeout 120 \
  --workers 2 \
  --log-file - \
  --access-logfile - \
  --error-logfile -
