# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-05-20 15:13:20"
ARG VERSION="1.0.0"
ARG MAINTAINER="daparthi001"

LABEL maintainer="${MAINTAINER}" \
      created="${BUILD_DATE}" \
      version="${VERSION}" \
      description="QuantumVestAI API Service"

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim

# Copy metadata from builder
COPY --from=builder /app/requirements.txt /app/
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories based on project structure
RUN mkdir -p /app/api/alembic \
    /app/api/config \
    /app/api/core \
    /app/api/db \
    /app/api/db_init \
    /app/api/ml \
    /app/api/models \
    /app/api/policies \
    /app/api/routers \
    /app/api/schemas \
    /app/api/services \
    /app/api/tests \
    /app/api/utils \
    /app/api/websocket \
    /app/logs \
    /app/data

# Copy application code with proper structure
COPY alembic/ /app/api/alembic/
COPY config/ /app/api/config/
COPY core/ /app/api/core/
COPY db/ /app/api/db/
COPY db_init/ /app/api/db_init/
COPY ml/ /app/api/ml/
COPY models/ /app/api/models/
COPY policies/ /app/api/policies/
COPY routers/ /app/api/routers/
COPY schemas/ /app/api/schemas/
COPY services/ /app/api/services/
COPY tests/ /app/api/tests/
COPY utils/ /app/api/utils/
COPY websocket/ /app/api/websocket/
COPY scripts/ /app/scripts/

# Copy configuration files
COPY alembic.ini /app/
COPY pyproject.toml /app/
COPY requirements.txt /app/
COPY .env.template /app/
COPY main.py /app/api/

# Create __init__.py files for Python packages
RUN find /app -type d -exec touch {}/__init__.py \;

# Set permissions
RUN chmod -R 755 /app/scripts && \
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
    CREATED_DATE="2025-05-20 15:13:20" \
    API_ENV=development \
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

# Command to run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]