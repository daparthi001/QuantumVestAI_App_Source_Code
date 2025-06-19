# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-06-19 05:51:42"
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
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pydantic-settings>=2.0.0

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

# Create necessary directories
RUN mkdir -p /app/api /app/logs

# Copy entry point script first and make it executable
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Create api package structure
RUN echo '"""API Package\nCreated: 2025-05-21 13:57:49\nAuthor: daparthi001\n"""\nfrom api.main import app\n\n__all__ = ["app"]' > /app/api/__init__.py

# Create a placeholder main.py if it doesn't exist in the build context
RUN echo '"""QuantumVestAI API - Main Application\nCreated: 2025-06-19 05:51:42\nAuthor: daparthi001\n"""\nfrom fastapi import FastAPI\nimport logging\n\nlogger = logging.getLogger("quantumvestai_api")\napp = FastAPI(title="QuantumVestAI API", version="1.0.0")\n\n@app.get("/")\nasync def root():\n    return {"status": "Service starting up... Please check again soon."}\n\n@app.get("/health")\nasync def health():\n    return {"status": "healthy"}' > /app/api/main.py

# Try to copy the real main.py if it exists (but don't fail if it doesn't)
COPY api/main.py /app/api/main.py || true
COPY main.py /app/api/main.py || true

# Copy the rest of the application
COPY . .

# Set proper permissions
RUN find /app -type d -exec chmod 755 {} \; || echo "Some directories couldn't be chmod'd" && \
    find /app -name "*.sh" -exec chmod +x {} \; || echo "Some scripts couldn't be chmod'd"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    CREATED_BY="daparthi001" \
    CREATED_DATE="2025-06-19 05:51:42" \
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

# Start the application using the app from the api package
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]