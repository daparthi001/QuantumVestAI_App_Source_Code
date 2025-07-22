# Use Python 3.10 as base
FROM python:3.10-slim

# Set metadata
LABEL maintainer="daparthi001"
LABEL org.opencontainers.image.created="2025-06-20T03:25:47Z"
LABEL org.opencontainers.image.version="1.5.2"
LABEL org.opencontainers.image.title="QuantumVestAI UI"
LABEL org.opencontainers.image.description="Frontend application for QuantumVestAI investment platform"

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user for security
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin -c "Docker image user" app

# Set working directory
WORKDIR /app

# Create config directory and scripts directory
RUN mkdir -p /config && mkdir -p /app/scripts

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting QuantumVestAI UI service..."\n\
echo "Current time: $(date -u)"\n\
echo "Running as user: $(whoami)"\n\
\n\
# Check if we should run in debug mode\n\
if [ "$DEBUG" = "true" ]; then\n\
    echo "Starting in debug mode..."\n\
    exec python -m uvicorn app.main:app --host $HOST --port $PORT --reload\n\
else\n\
    echo "Starting in production mode..."\n\
    exec gunicorn --bind $HOST:$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker app.main:app\n\
fi' > /app/scripts/start.sh && \
    chmod +x /app/scripts/start.sh

# Create a default package.json if it doesn't exist
RUN echo '{\n\
  "name": "quantumvestai-ui",\n\
  "version": "1.5.2",\n\
  "description": "Frontend for QuantumVestAI platform",\n\
  "scripts": {\n\
    "build": "echo No frontend build needed",\n\
    "test": "echo No tests specified"\n\
  },\n\
  "author": "daparthi001",\n\
  "license": "UNLICENSED"\n\
}' > /app/package.json

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full ui and api packages to ensure all modules are present for imports
COPY ai-stock-platform/ui /app/ui
COPY ai-stock-platform/api /app/api

# Copy application code (which may include an actual package.json that will overwrite our placeholder)
COPY . .

# Ensure the startup script is executable after copying
RUN chmod +x /app/scripts/start.sh

RUN if [ -f package.json ] && grep -q '"dependencies"' package.json; then \
      npm install && npm run build; \
    else \
      echo "No frontend dependencies found. Skipping npm install and build."; \
    fi

# Set ownership for all files
RUN chown -R app:app /app

# Run npm install only if we have a valid package.json with dependencies
RUN if grep -q '"dependencies"' package.json; then \
        npm install && \
        npm run build; \
    else \
        echo "No frontend dependencies found. Skipping npm install and build."; \
    fi

# Switch to non-root user
USER app

# Set runtime environment variables
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    APP_VERSION=1.5.2 \
    LAST_UPDATED="2025-06-20 03:25:47" \
    UPDATED_BY="daparthi001" \
    PYTHONPATH=/app/ai-stock-platform:/app/ai-stock-platform/ui:/app/ui:/app/api:/app

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Set startup command with optional debug mode
CMD ["/app/scripts/start.sh"]