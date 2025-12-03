# Dockerfile - production for Render
FROM python:3.11-slim

# Install system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      nginx \
      supervisor \
      curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files at build time (optional: you may prefer at container start)
RUN python manage.py collectstatic --noinput || true

# Remove default nginx config and copy ours
RUN rm -f /etc/nginx/sites-enabled/default
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

# Copy supervisord config
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Ensure entrypoint is executable
RUN chmod +x docker/entrypoint.sh

# Expose (Render sets PORT automatically)
EXPOSE 10000

# Use entrypoint (runs migrations/collectstatic then supervisord)
ENTRYPOINT ["sh", "docker/entrypoint.sh"]

