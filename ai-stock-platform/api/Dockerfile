# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-05-20 17:12:19"
ARG VERSION="1.0.0"
ARG MAINTAINER="daparthi001"

LABEL maintainer="${MAINTAINER}" \
      created="${BUILD_DATE}" \
      version="${VERSION}" \
      environment="development" \
      description="QuantumVestAI API Service" \
      repository="ai-stock-platform/api"

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Copy metadata from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire current directory
COPY . /app/

# Set proper permissions
RUN chmod 644 \
        /app/__init__.py \
        /app/alembic.ini \
        /app/api.py \
        /app/api_safe_setup_Version2.py \
        /app/build-db-init.sh \
        /app/deploy-to-eks.sh \
        /app/docker-compose.yml \
        /app/docker-entrypoint.sh \
        /app/iam-policy.json \
        /app/main.py \
        /app/pyproject.toml \
        /app/rds_connect_policy.json \
        /app/requirements.txt \
        /app/setup.py \
        /app/test_db_connection.py \
        /app/update-script.py && \
    chmod -R 755 \
        /app/alembic \
        /app/config \
        /app/core \
        /app/db \
        /app/db_init \
        /app/ml \
        /app/models \
        /app/policies \
        /app/routers \
        /app/schemas \
        /app/scripts \
        /app/services \
        /app/tests \
        /app/utils \
        /app/websocket && \
    chmod +x \
        /app/build-db-init.sh \
        /app/deploy-to-eks.sh \
        /app/docker-entrypoint.sh

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    CREATED_BY="daparthi001" \
    CREATED_DATE="2025-05-20 17:12:19" \
    API_ENV="development" \
    API_V1_STR="/api/v1" \
    PROJECT_NAME="QuantumVestAI API" \
    VERSION="1.0.0"

# Set up a non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]