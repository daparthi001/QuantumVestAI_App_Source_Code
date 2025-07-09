"""
Manual Health Endpoint Test
Created: 2025-06-19 04:08:15
Author: daparthi001

This file can be run directly on the server to check if the health function works
without going through the API routes.
"""
import pytest
pytest.skip("Manual script", allow_module_level=True)
import asyncio
import json
from health_check import get_health_data

async def test_health():
    """Test the health function directly"""
    print("Testing health check function...")
    health_data = await get_health_data()
    print(json.dumps(health_data, indent=2))
    print("Health check function test completed")

if __name__ == "__main__":    asyncio.run(test_health())