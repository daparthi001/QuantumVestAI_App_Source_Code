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

# Copy requirements first for better caching
COPY --chown=app:app requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . /app/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Create non-root user
RUN useradd -m -u 1000 app && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Set runtime environment variables
ENV PORT=3000 \
    HOST=0.0.0.0

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Set startup command
CMD ["/app/scripts/start.sh"]