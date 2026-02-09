#!/usr/bin/env bash
set -e

echo "🔄 Applying migrations..."
python manage.py migrate --noinput

echo "🧹 Fixing notification types..."
python manage.py fix_notification_types || true

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn..."
exec gunicorn YOUR_PROJECT.wsgi:application --bind 0.0.0.0:${PORT:-10000}
