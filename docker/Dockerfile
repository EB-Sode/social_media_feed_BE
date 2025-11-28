# --------- BASE IMAGE ---------
FROM python:3.12-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --------- FINAL IMAGE ---------
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from base
COPY --from=base /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

# Make entrypoint executable
RUN chmod +x docker/entrypoint.sh

# Environment variables for production/development
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Entry point script
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
