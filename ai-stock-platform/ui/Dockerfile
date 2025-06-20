# QuantumVestAI UI Dockerfile
# Created: Unknown
# Updated: 2025-06-18 01:56:23
# Author: daparthi001

# Use Python 3.10 for consistency with API
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app structure and set permissions
RUN mkdir -p /app/ui /app/static /app/templates /app/logs \
    && chmod 755 /app/ui /app/static /app/templates /app/logs

# Create non-root user first so we can use it for all operations
RUN useradd -m -u 1000 app

# Copy requirements first for better caching
COPY --chown=app:app requirements.txt .

# Install Python dependencies with explicit dependency additions
RUN pip install --no-cache-dir -r requirements.txt && \
    # Ensure critical dependencies are installed regardless of requirements.txt
    pip install --no-cache-dir fastapi uvicorn aiohttp requests jinja2

# Copy application code
COPY . .

# Copy the fixed startup script
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

# Set the entrypoint
CMD ["/app/scripts/start.sh"]