# Build stage for React components
FROM node:16-alpine AS react-build

WORKDIR /app

# Copy package files for React components
COPY package*.json ./
RUN npm ci --silent || npm install --silent

# Copy React source files - only if they exist
COPY src/ src/ || true
COPY public/ public/ || true
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

# Set up Python package structure
RUN mkdir -p /app/config /app/routes /app/middleware /app/services /app/templates /app/static

# Copy Python files - with fallbacks in case directories don't exist
COPY config/ /app/config/ || true
COPY dependencies/ /app/dependencies/ || true
COPY middleware/ /app/middleware/ || true
COPY routes/ /app/routes/ || true
COPY scripts/ /app/scripts/ || true
COPY services/ /app/services/ || true
COPY templates/ /app/templates/ || true
COPY static/ /app/static/ || true

# Copy main.py if it exists
COPY main.py /app/ || true
COPY app.py /app/ || true  # Alternative main file name

# Make scripts executable if they exist
RUN if [ -d "/app/scripts" ]; then find /app/scripts -name "*.sh" -exec chmod +x {} \; || true; fi

# Copy requirements and install Python dependencies
COPY requirements*.txt ./ || true
RUN if [ -f "requirements.txt" ]; then pip install --no-cache-dir -r requirements.txt; elif [ -f "requirements-dev.txt" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

# Copy the built React files to static directory
COPY --from=react-build /app/build /app/static/react || true

# Environment variables (non-sensitive defaults only)
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 3000

# Determine appropriate startup command
RUN if [ -f "/app/main.py" ]; then \
        echo "python -m uvicorn main:app --host 0.0.0.0 --port \${PORT}" > /app/start.sh; \
    elif [ -f "/app/app.py" ]; then \
        echo "python -m uvicorn app:app --host 0.0.0.0 --port \${PORT}" > /app/start.sh; \
    elif [ -d "/app/scripts" ] && [ -f "/app/scripts/start.sh" ]; then \
        echo "/app/scripts/start.sh" > /app/start.sh; \
    else \
        echo "python -m uvicorn main:app --host 0.0.0.0 --port \${PORT}" > /app/start.sh; \
    fi && chmod +x /app/start.sh

# Set the startup command
CMD ["/bin/bash", "/app/start.sh"]