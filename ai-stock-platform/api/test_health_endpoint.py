"""
Direct Health Endpoint Test
Created: 2025-06-19 04:08:15
Author: daparthi001
"""
import pytest

pytest.skip("Manual external endpoint test", allow_module_level=True)
import json
import sys
from datetime import datetime

import requests

# Constants
API_URL = "http://quantumvestai-dev-api:8000"
HEALTH_PATH = "/api/v1/health"
TIMEOUT = 10  # seconds

def main():
    """Test the health endpoint directly"""
    print(f"Testing health endpoint: {API_URL}{HEALTH_PATH}")
    print(f"Date/Time: {datetime.now().isoformat()}")
    print("-" * 50)
    
    try:
        # Send GET request to health endpoint
        print("Sending GET request...")
        response = requests.get(f"{API_URL}{HEALTH_PATH}", timeout=TIMEOUT)
        
        # Print response details
        print(f"Status code: {response.status_code}")
        print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Print response body if available
        if response.content:
            try:
                print(f"Response body: {json.dumps(response.json(), indent=2)}")
            except ValueError:
                print(f"Response body (non-JSON): {response.text}")
        else:
            print("Response body: <empty>")
        
        # Return exit code based on status
        return 0 if 200 <= response.status_code < 300 else 1
        
    except requests.RequestException as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
