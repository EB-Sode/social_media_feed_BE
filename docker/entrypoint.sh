#!/bin/sh

echo "Waiting for database to start..."
sleep 5  # simple wait, or use wait-for-it for production

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files (optional)
# python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
