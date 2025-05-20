# Build stage
FROM python:3.10-slim AS builder

# Set build arguments and metadata
ARG BUILD_DATE="2025-05-20 15:30:14"
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

# Create necessary directories with proper structure
RUN mkdir -p /app/api \
    /app/core \
    /app/db \
    /app/models \
    /app/logs \
    /app/data \
    /app/scripts

# Copy application code maintaining original structure
COPY api/ /app/api/
COPY core/ /app/core/
COPY db/ /app/db/
COPY models/ /app/models/
COPY scripts/ /app/scripts/
COPY alembic/ /app/alembic/
COPY alembic.ini /app/

# Create updated main.py with correct imports
RUN echo 'from fastapi import FastAPI' > /app/main.py && \
    echo 'from fastapi.middleware.cors import CORSMiddleware' >> /app/main.py && \
    echo 'from datetime import datetime' >> /app/main.py && \
    echo '' >> /app/main.py && \
    echo 'from core.config import settings' >> /app/main.py && \
    echo 'from routers import (' >> /app/main.py && \
    echo '    auth,' >> /app/main.py && \
    echo '    stocks,' >> /app/main.py && \
    echo '    users,' >> /app/main.py && \
    echo '    forecast,' >> /app/main.py && \
    echo '    watchlist,' >> /app/main.py && \
    echo '    admin,' >> /app/main.py && \
    echo '    sentiment,' >> /app/main.py && \
    echo '    data,' >> /app/main.py && \
    echo '    whitepaper' >> /app/main.py && \
    echo ')' >> /app/main.py && \
    echo '' >> /app/main.py && \
    echo '# Create FastAPI instance' >> /app/main.py && \
    echo 'app = FastAPI(' >> /app/main.py && \
    echo '    title=settings.PROJECT_NAME,' >> /app/main.py && \
    echo '    version=settings.VERSION,' >> /app/main.py && \
    echo '    openapi_url=f"{settings.API_V1_STR}/openapi.json"' >> /app/main.py && \
    echo ')' >> /app/main.py && \
    echo '' >> /app/main.py && \
    echo '# Set up CORS' >> /app/main.py && \
    echo 'if settings.BACKEND_CORS_ORIGINS:' >> /app/main.py && \
    echo '    app.add_middleware(' >> /app/main.py && \
    echo '        CORSMiddleware,' >> /app/main.py && \
    echo '        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],' >> /app/main.py && \
    echo '        allow_credentials=True,' >> /app/main.py && \
    echo '        allow_methods=["*"],' >> /app/main.py && \
    echo '        allow_headers=["*"],' >> /app/main.py && \
    echo '    )' >> /app/main.py && \
    echo '' >> /app/main.py && \
    echo '# Include routers with tags' >> /app/main.py && \
    echo 'app.include_router(auth.router, prefix=f"{settings.API_V1_STR}", tags=["auth"])' >> /app/main.py && \
    echo 'app.include_router(users.router, prefix=f"{settings.API_V1_STR}", tags=["users"])' >> /app/main.py && \
    echo 'app.include_router(stocks.router, prefix=f"{settings.API_V1_STR}", tags=["stocks"])' >> /app/main.py && \
    echo 'app.include_router(forecast.router, prefix=f"{settings.API_V1_STR}", tags=["forecast"])' >> /app/main.py && \
    echo 'app.include_router(watchlist.router, prefix=f"{settings.API_V1_STR}", tags=["watchlist"])' >> /app/main.py && \
    echo 'app.include_router(admin.router, prefix=f"{settings.API_V1_STR}", tags=["admin"])' >> /app/main.py && \
    echo 'app.include_router(sentiment.router, prefix=f"{settings.API_V1_STR}", tags=["sentiment"])' >> /app/main.py && \
    echo 'app.include_router(data.router, prefix=f"{settings.API_V1_STR}", tags=["data"])' >> /app/main.py && \
    echo 'app.include_router(whitepaper.router, prefix=f"{settings.API_V1_STR}", tags=["whitepaper"])' >> /app/main.py && \
    echo '' >> /app/main.py && \
    echo '@app.get("/health")' >> /app/main.py && \
    echo 'async def health_check():' >> /app/main.py && \
    echo '    """Health check endpoint"""' >> /app/main.py && \
    echo '    return {' >> /app/main.py && \
    echo '        "status": "healthy",' >> /app/main.py && \
    echo '        "version": settings.VERSION,' >> /app/main.py && \
    echo '        "timestamp": datetime.utcnow().isoformat(),' >> /app/main.py && \
    echo '        "user": "daparthi001",' >> /app/main.py && \
    echo '        "created": "2025-05-20 15:30:14"' >> /app/main.py && \
    echo '    }' >> /app/main.py

# Set permissions
RUN chmod -R 755 /app/scripts && \
    chmod -R 644 /app/core /app/db /app/models /app/api && \
    chmod -R +X /app/core /app/db /app/models /app/api && \
    chmod 755 /app/logs /app/data

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    CREATED_BY="daparthi001" \
    CREATED_DATE="2025-05-20 15:30:14" \
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

# Update command to use main.py in root directory
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]