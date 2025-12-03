# Use slim image
FROM python:3.12-slim as base

# System deps
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl git nginx supervisord\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port
EXPOSE 8000

# Permissions
RUN chmod +x docker/entrypoint.sh

# Entrypoint runs migrations, collectstatic, then starts Gunicorn + Nginx
ENTRYPOINT ["sh", "docker/entrypoint.sh"]

# Use slim image
FROM python:3.12-slim

# System deps
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl git nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Permissions
RUN chmod +x docker/entrypoint.sh

# Expose Render port (not strictly necessary but good practice)
EXPOSE 8000

# Use supervisord as entrypoint
CMD ["/usr/bin/supervisord", "-c", "/app/docker/supervisord.conf"]
