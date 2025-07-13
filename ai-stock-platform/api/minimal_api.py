"""
Minimal API for Testing Endpoints
Created: 2025-06-19 04:20:11
Author: daparthi001
"""
import os
import sys

import uvicorn
from fastapi import FastAPI, HTTPException

# Print debugging information
print(f"Starting minimal API...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Create a minimal FastAPI app
app = FastAPI(title="Minimal API", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Minimal API is running"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "api": "minimal"}

@app.get("/api/v1/health")
async def api_health():
    """API health check endpoint"""
    return {
        "status": "healthy", 
        "api": "minimal", 
        "path": "/api/v1/health"
    }

# Add other test endpoints
@app.get("/api/v1/forecast")
async def forecast():
    """Test forecast endpoint"""
    return {"message": "Forecast endpoint is working"}

@app.get("/api/v1/auth/login")
async def login_test():
    """Test login endpoint"""
    return {"message": "Login endpoint exists"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("minimal_api:app", host="0.0.0.0", port=port)
