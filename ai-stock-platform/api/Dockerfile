# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-06-19 05:57:30"
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

# Create a placeholder main.py in case we don't find one later
RUN echo '"""QuantumVestAI API - Main Application\nCreated: 2025-06-19 05:57:30\nAuthor: daparthi001\n"""\nfrom fastapi import FastAPI\nimport logging\nfrom datetime import datetime\nimport os\nimport socket\n\n# Configure logging\nlogging.basicConfig(level=logging.INFO)\nlogger = logging.getLogger("quantumvestai_api")\n\napp = FastAPI(title="QuantumVestAI API", version="1.0.0")\n\n@app.get("/")\nasync def root():\n    """API root endpoint"""\n    logger.info("Root endpoint accessed")\n    return {\n        "name": "QuantumVestAI API",\n        "version": "1.0.0",\n        "status": "running",\n        "environment": os.environ.get("API_ENV", "development"),\n        "documentation": "/docs"\n    }\n\n@app.get("/health")\nasync def health_check():\n    """Basic health check endpoint"""\n    logger.info("Health check endpoint accessed")\n    return {"status": "healthy"}\n\n@app.get("/api/v1/health")\nasync def api_health_check():\n    """API v1 health check endpoint"""\n    logger.info("API v1 health check endpoint accessed")\n    system_info = {\n        "hostname": socket.gethostname(),\n        "timestamp": datetime.now().isoformat(),\n        "environment": os.environ.get("API_ENV", "development"),\n    }\n    return {\n        "status": "healthy",\n        "version": "1.0.0",\n        "system": system_info\n    }' > /app/api/main.py

# Copy the rest of the application
COPY . .

# If main.py exists in the root, try to copy it to the api directory
RUN if [ -f "/app/main.py" ]; then \
        echo "Found main.py in root directory, copying to api directory..."; \
        cp /app/main.py /app/api/main.py; \
    fi

# Set proper permissions
RUN find /app -type d -exec chmod 755 {} \; 2>/dev/null || echo "Some directories couldn't be chmod'd" && \
    find /app -name "*.sh" -exec chmod +x {} \; 2>/dev/null || echo "Some scripts couldn't be chmod'd"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    CREATED_BY="daparthi001" \
    CREATED_DATE="2025-06-19 05:57:30" \
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