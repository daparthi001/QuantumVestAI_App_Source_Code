# Base image
FROM python:3.9-slim as base

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install the application
RUN pip install --no-cache-dir -e .

# Build stage for production
FROM base as production

ENV ENV=production \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=4

# Expose the application port
EXPOSE 8000

# Set the startup command
CMD ["./scripts/start.sh"]

# Development stage with additional tools
FROM base as development

# Install development dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

ENV ENV=development \
    DEBUG=true \
    PORT=8000 \
    HOST=0.0.0.0

# Set the startup command for development
CMD ["./scripts/start.sh"]