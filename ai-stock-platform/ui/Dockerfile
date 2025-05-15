# Build stage for React components (if needed)
FROM node:16-alpine AS react-build

WORKDIR /app

# Copy package files for React components - only if they exist
COPY package*.json ./ || true
RUN if [ -f "package.json" ]; then npm ci --silent || npm install --silent; fi

# Copy React source files if they exist
COPY src/ ./src/ || true
COPY public/ ./public/ || true
COPY tsconfig*.json ./ || true
COPY .env* ./ || true

# Build React application if package.json exists
RUN if [ -f "package.json" ]; then npm run build || echo "Build failed but continuing"; else mkdir -p build; fi

# Python runtime stage
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    nodejs \
    npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create the Python package structure that matches your project
RUN mkdir -p /app/ui/config /app/ui/routes /app/ui/services \
    /app/ui/utils /app/ui/middleware /app/ui/dependencies \
    /app/static/css /app/static/js /app/static/img /app/static/vendors \
    /app/templates /app/templates/admin /app/tests

# Copy the UI Python package
COPY ui/ /app/ui/

# Copy static files
COPY static/ /app/static/

# Copy templates
COPY templates/ /app/templates/

# Copy scripts and make them executable
COPY scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh

# Copy additional files
COPY requirements.txt setup.py README.md /app/
COPY .env.example /app/.env.example || true

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e .

# Copy the built React files to static directory if they exist
COPY --from=react-build /app/build /app/static/react || true

# Environment variables (non-sensitive defaults only)
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 3000

# Set the startup command to use your start.sh script or fall back to running directly
CMD if [ -f "/app/scripts/start.sh" ]; then \
        /app/scripts/start.sh; \
    else \
        python -m uvicorn ui.main:app --host 0.0.0.0 --port ${PORT}; \
    fi