# Build stage
FROM python:3.9-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install poetry
RUN pip install poetry==1.4.2

# Copy only requirements file first for better caching
COPY pyproject.toml poetry.lock* /app/

# Configure poetry for production use
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Runtime stage
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    # AWS CLI for RDS IAM authentication
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && apt-get update && apt-get install -y unzip \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip ./aws \
    && apt-get remove -y unzip \
    && apt-get clean

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app:${PATH}"

# Copy project dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Create uploads directory with appropriate permissions
RUN mkdir -p /app/uploads/whitepapers \
    && chmod -R 755 /app/uploads

# Copy application code
COPY . /app/

# Create non-root user for security
RUN groupadd -r quantumvest && useradd -r -g quantumvest quantumvest \
    && chown -R quantumvest:quantumvest /app

# Switch to non-root user
USER quantumvest

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Entry point
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]