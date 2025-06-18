# QuantumVestAI UI Dockerfile
# Created: Unknown
# Updated: 2025-06-18 01:56:23
# Author: daparthi001

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

# Create non-root user first so we can use it for all operations
RUN useradd -m -u 1000 app

# Copy requirements first for better caching
COPY --chown=app:app requirements.txt .

# Install Python dependencies with explicit dependency additions
RUN pip install --no-cache-dir -r requirements.txt && \
    # Ensure critical dependencies are installed regardless of requirements.txt
    pip install --no-cache-dir fastapi uvicorn aiohttp requests jinja2

# Copy application code
COPY --chown=app:app . /app/

# Fix import issues in utils/__init__.py
RUN if [ -f /app/utils/__init__.py ]; then \
        sed -i 's/from ui\.utils/from utils/g' /app/utils/__init__.py; \
    fi

# Fix template_filters.py to properly use templates from app.state
RUN if [ -f /app/utils/template_filters.py ]; then \
        sed -i 's/app.jinja_env/templates.env/g' /app/utils/template_filters.py; \
    fi

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Update main.py to ensure templates are stored in app.state
RUN if grep -q "templates = Jinja2Templates" /app/main.py && ! grep -q "app.state.templates = templates" /app/main.py; then \
        sed -i '/templates = Jinja2Templates/a app.state.templates = templates  # Store templates in app.state' /app/main.py; \
    fi

# Set ownership for all files
RUN chown -R app:app /app

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

# Set startup command with optional debug mode
CMD ["/app/scripts/start.sh"]