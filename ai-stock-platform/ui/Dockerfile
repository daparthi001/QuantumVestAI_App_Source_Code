# Use Python 3.10 as base
FROM python:3.10-slim

# Install Node.js and npm
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Create config directory
RUN mkdir -p /config

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy package.json and install Node.js dependencies
# COPY package.json .
RUN npm install

# # Copy application code
# COPY . .

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