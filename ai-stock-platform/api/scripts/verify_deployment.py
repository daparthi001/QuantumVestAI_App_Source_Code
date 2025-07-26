"""
Deployment Verification Script
Created: 2025-05-19 05:43:23
Author: daparthi001
"""
import os
import sys
import time
from typing import Any, Dict

import requests


def verify_deployment(base_url: str) -> None:
    """Verify the deployment by checking various endpoints"""
    
    # Health check
    health_response = requests.get(f"{base_url}/api/health")
    if health_response.status_code != 200:
        print(f"Health check failed: {health_response.text}")
        sys.exit(1)
    
    health_data = health_response.json()
    
    # Verify system metrics
    verify_system_metrics(health_data.get("system", {}))
    
    # Verify database connection
    if health_data.get("database") != "connected":
        print("Database connection verification failed")
        sys.exit(1)
    
    print("Deployment verification successful!")
    print(f"Pod: {health_data.get('pod', {}).get('name')}")
    print(f"Version: {health_data.get('version')}")

def verify_system_metrics(metrics: Dict[str, Any]) -> None:
    """Verify system metrics are within acceptable ranges"""
    
    memory_usage = float(metrics.get("memory_usage", "0%").rstrip("%"))
    disk_usage = float(metrics.get("disk_usage", "0%").rstrip("%"))
    
    if memory_usage > 90:
        print(f"Warning: High memory usage ({memory_usage}%)")
    
    if disk_usage > 90:
        print(f"Warning: High disk usage ({disk_usage}%)")

if __name__ == "__main__":
    base_url = os.getenv("API_URL", "http://quantumvestai-dev-api.dev.svc.cluster.local:8000")
    verify_deployment(base_url)
