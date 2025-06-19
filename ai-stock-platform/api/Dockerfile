FROM python:3.10-slim

# Set metadata
LABEL maintainer="daparthi001" \
      created="2025-06-19 07:11:20" \
      version="1.0.0" \
      environment="production" \
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
    API_ENV="production" \
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

# Start the application directly from main.py - this is critical for proper routing
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]