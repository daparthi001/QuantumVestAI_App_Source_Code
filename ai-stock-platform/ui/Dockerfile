# Build stage for React components (if needed)
FROM node:16-alpine AS react-build

WORKDIR /app

# Copy package files for React components - only if they exist
COPY package*.json ./ 2>/dev/null || true
RUN if [ -f "package.json" ]; then npm ci --silent || npm install --silent; fi

# Copy React source files if they exist
COPY src/ ./src/ 2>/dev/null || true
COPY public/ ./public/ 2>/dev/null || true
COPY tsconfig*.json ./ 2>/dev/null || true
COPY .env* ./ 2>/dev/null || true

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

# Copy scripts and make them executable (if they exist)
RUN mkdir -p /app/scripts
COPY scripts/ /app/scripts/ 2>/dev/null || true
# If scripts directory exists, make .sh files executable
RUN find /app/scripts -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true

# Copy additional files - fix for .env.example not found
COPY requirements.txt /app/
COPY setup.py /app/ 2>/dev/null || true
COPY README.md /app/ 2>/dev/null || true
# Do not copy .env.example since it doesn't exist

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
# Only run setup.py if it exists
RUN if [ -f "/app/setup.py" ]; then pip install -e .; fi

# Copy the built React files to static directory if they exist
COPY --from=react-build /app/build /app/static/react 2>/dev/null || true

# Environment variables (non-sensitive defaults only)
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 3000

# Fix for CMD JSON format as recommended in warning
CMD ["sh", "-c", "if [ -f \"/app/scripts/start.sh\" ]; then /app/scripts/start.sh; else python -m uvicorn ui.main:app --host 0.0.0.0 --port ${PORT}; fi"]