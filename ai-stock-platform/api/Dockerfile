# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-05-20 15:58:56"
ARG VERSION="1.0.0"
ARG MAINTAINER="daparthi001"
ARG ENVIRONMENT="development"

LABEL maintainer="${MAINTAINER}" \
      created="${BUILD_DATE}" \
      version="${VERSION}" \
      environment="${ENVIRONMENT}" \
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
COPY api/requirements.txt .
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

# Create logs and data directories
RUN mkdir -p /app/logs /app/data

# Simply copy the entire api directory
COPY api/ /app/api/

# Set proper permissions
RUN chmod -R 755 /app/api/scripts && \
    chmod +x /app/api/docker-entrypoint.sh \
            /app/api/build-db-init.sh \
            /app/api/deploy-to-eks.sh && \
    chmod -R 644 /app/api && \
    chmod -R +X /app/api && \
    chmod 755 /app/logs /app/data

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    CREATED_BY="daparthi001" \
    CREATED_DATE="2025-05-20 15:58:56" \
    API_ENV=${ENVIRONMENT} \
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
ENTRYPOINT ["/app/api/docker-entrypoint.sh"]

# Start the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]