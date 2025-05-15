# Build stage for React components
FROM node:16-alpine AS react-build

WORKDIR /app

# Copy package files for React components
COPY package.json package-lock.json* ./
RUN npm ci --silent

# Copy React source files
COPY src/ src/
COPY public/ public/
COPY tsconfig.json .
COPY .env* ./

# Build React application
RUN npm run build

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
RUN mkdir -p /app/ui/config /app/ui/routes /app/ui/middleware /app/ui/services /app/templates /app/static

# Copy Python package files
COPY ui/ /app/ui/
COPY templates/ /app/templates/
COPY static/ /app/static/
COPY main.py /app/

# Make scripts executable
RUN if [ -d "/app/ui/scripts" ]; then chmod +x /app/ui/scripts/*.sh; fi

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built React files to static directory
COPY --from=react-build /app/build /app/static/react

# Environment variables (non-sensitive defaults only)
ENV PORT=3000 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app

# Expose application port
EXPOSE 3000

# Set the startup command - use direct uvicorn command instead of script
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]