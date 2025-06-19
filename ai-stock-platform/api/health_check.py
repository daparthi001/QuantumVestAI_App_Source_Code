"""
Dedicated Health Check Module
Created: 2025-06-19 04:08:15
Author: daparthi001
"""
import socket
import platform
import os
from datetime import datetime
import psutil

async def get_health_data():
    """
    Get comprehensive health check data
    This is a standalone function that doesn't rely on any router configuration
    """
    try:
        # Basic system information
        hostname = socket.gethostname()
        try:
            ip_address = socket.gethostbyname(hostname)
        except:
            ip_address = "unknown"
            
        # Process information
        process = psutil.Process(os.getpid())
        process_info = {
            "pid": process.pid,
            "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "threads": process.num_threads(),
            "uptime_seconds": round((datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds())
        }
        
        # System resources
        system_info = {
            "hostname": hostname,
            "ip_address": ip_address,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2)
        }
        
        # Environment information
        env_info = {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "app_version": os.environ.get("APP_VERSION", "1.0.0"),
            "pod_name": os.environ.get("POD_NAME", "unknown"),
            "node_name": os.environ.get("NODE_NAME", "unknown")
        }
        
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": system_info,
            "process": process_info,
            "environment": env_info
        }
        
        return health_data
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }