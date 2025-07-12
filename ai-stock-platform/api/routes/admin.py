"""
Admin Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

@router.get("/dashboard")
async def admin_dashboard():
    """Admin dashboard with system stats"""
    return {
        "status": "success",
        "data": {
            "system_stats": {
                "total_users": 1250,
                "active_users": 850,
                "total_stocks": 5000,
                "api_calls_today": 125000,
                "server_uptime": "5d 12h 30m"
            },
            "recent_activities": [
                {"type": "user_registration", "count": 25, "timestamp": datetime.now().isoformat()},
                {"type": "api_calls", "count": 5000, "timestamp": datetime.now().isoformat()},
                {"type": "predictions_generated", "count": 150, "timestamp": datetime.now().isoformat()}
            ]
        }
    }

@router.get("/users")
async def get_users():
    """Get all users for admin"""
    return {
        "status": "success",
        "data": {
            "users": [
                {"id": 1, "username": "demo", "email": "demo@example.com", "active": True},
                {"id": 2, "username": "testuser", "email": "test@example.com", "active": True}
            ],
            "total": 2
        }
    }
