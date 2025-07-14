FROM python:3.10-slim

# Set metadata
LABEL maintainer="daparthi001" \
      created="2025-06-19 15:34:18" \
      version="1.0.1" \
      description="QuantumVestAI API Service"

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    PYTHONPATH=/app \
    TZ=UTC \
    API_ENV="development" \
    PROJECT_NAME="QuantumVestAI API" \
    VERSION="1.0.1" \
    POSTGRES_SERVER=localhost \
    POSTGRES_USER=postgres \
    POSTGRES_PASSWORD=postgres \
    POSTGRES_DB=quantumvestai \
    POSTGRES_PORT=5432

# Provide default connection string so database_migrator.py can run
ENV DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}"

# Healthcheck - Test the /api/v1/health endpoint specifically
# Set up a non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/v1/health || exit 1

EXPOSE ${PORT}

# Copy entrypoint script
COPY --chown=appuser:appuser docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Use entrypoint to run migrations before starting
ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]