#!/bin/bash
set -euo pipefail

# Apply DB migrations
echo "🔄 Applying migrations..."
python manage.py migrate --noinput

# ✅ Fix invalid notification_type values (idempotent + safe)
echo "🧹 Fixing notification types..."
python manage.py fix_notification_types || true

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Ensure Gunicorn socket permissions
touch /tmp/gunicorn.sock
chmod 777 /tmp/gunicorn.sock

# -------------------------
# 4️⃣ Start Nginx (serve static + media)
# -------------------------
# echo "🌐 Starting Nginx..."
# nginx -g "daemon off;" &

# -------------------------
# 3️⃣ Start Gunicorn (Django web server)
# -------------------------
echo "🚀 Starting Gunicorn..."
gunicorn social_media_feed.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --timeout 120


# # Start supervisord
# echo "🚀 Starting supervisord..."
# exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf


# -------------------------
# 5️⃣ Start Celery Worker + Beat
# -------------------------
# echo "☕ Starting Celery worker + beat..."
# mkdir -p /celerybeat

# # Start Celery Worker in background
# celery -A celery_app worker --loglevel=INFO &

# # Start Celery Beat in foreground (so container stays alive)
# celery -A celery_app beat \
#     --loglevel=INFO \
#     --scheduler django_celery_beat.schedulers:DatabaseScheduler \
#     --pidfile=/celerybeat/celerybeat.pid






# echo "Waiting for database to start..."
# sleep 5  # simple wait, or use wait-for-it for production

# # Apply migrations
# echo "Applying database migrations..."
# python manage.py migrate

# # Collect static files (optional)
# # python manage.py collectstatic --noinput

# # Start server
# echo "Starting server..."
# exec python manage.py runserver 0.0.0.0:8000


