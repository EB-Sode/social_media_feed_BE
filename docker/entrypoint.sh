#!/bin/bash
set -euo pipefail

# 1) Apply DB migrations
echo "🔄 Applying migrations..."
python manage.py migrate --noinput

# 2) Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# 3) Start supervisord (manages gunicorn + nginx)
echo "🚀 Starting supervisord..."
exec /usr/bin/supervisord -n -c /etc/supervisor/conf.d/supervisord.conf



# -------------------------
# 4️⃣ Start Nginx (serve static + media)
# -------------------------
# echo "🌐 Starting Nginx..."
# nginx -g "daemon off;" &

# # -------------------------
# # 3️⃣ Start Gunicorn (Django web server)
# # -------------------------
# echo "🚀 Starting Gunicorn..."
# gunicorn social_media_feed.wsgi:application \
#     --bind unix:/tmp/gunicorn.sock \
#     --workers 4 \
#     --timeout 120






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


