# Use official Python image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/ui/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY scripts/ /app/scripts/
COPY setup.py README.md .env.example /app/

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Set environment variables
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose port
EXPOSE 3000

# Set startup command using the startup script
CMD ["/app/scripts/start.sh"]