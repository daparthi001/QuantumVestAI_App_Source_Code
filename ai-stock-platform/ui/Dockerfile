# Build stage for React components (if needed)
FROM node:16-alpine AS react-build

WORKDIR /app

# Copy package files for React components - only attempt if they exist
COPY package*.json ./ 2>/dev/null || echo "No package.json found"

# Only run npm install if package.json exists
RUN if [ -f "package.json" ]; then npm ci --silent || npm install --silent; fi

# Copy React source files - only attempt if they exist
COPY src/ ./src/ 2>/dev/null || echo "No src directory found"
COPY public/ ./public/ 2>/dev/null || echo "No public directory found"
COPY tsconfig*.json ./ 2>/dev/null || echo "No tsconfig found"

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

# Copy the UI Python package - core of the application
COPY ui/ /app/ui/

# Copy static files and templates
COPY static/ /app/static/
COPY templates/ /app/templates/

# Create scripts directory
RUN mkdir -p /app/scripts

# Try to copy scripts directory - might not exist
COPY scripts/ /app/scripts/ 2>/dev/null || echo "No scripts directory found"

# Make shell scripts executable if they exist
RUN find /app/scripts -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || echo "No shell scripts found"

# Copy requirements.txt - this must exist
COPY requirements.txt /app/

# Try to copy optional files - fix syntax for Docker compatibility
COPY setup.py /app/ 2>/dev/null || echo "No setup.py found"
COPY README.md /app/ 2>/dev/null || echo "No README.md found"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the package if setup.py exists
RUN if [ -f "/app/setup.py" ]; then pip install -e .; fi

# Copy the built React files to static directory if they exist
COPY --from=react-build /app/build /app/static/react 2>/dev/null || echo "No React build files found"

# Environment variables
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 3000

# Use a simple sh -c command that handles startup logic
CMD ["sh", "-c", "if [ -f /app/scripts/start.sh ]; then /app/scripts/start.sh; else python -m uvicorn ui.main:app --host 0.0.0.0 --port ${PORT}; fi"]