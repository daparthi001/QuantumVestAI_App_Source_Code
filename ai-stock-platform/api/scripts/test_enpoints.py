"""
API Endpoint Test Script
Created: 2025-06-19 03:54:33
Author: daparthi001
"""
import requests
import sys
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "https://dev.quantumvestai.com"

def test_health_endpoint():
    """Test the health endpoint"""
    print(f"Testing health endpoint: {BASE_URL}/api/v1/health")
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_auth_endpoint():
    """Test the authentication endpoint"""
    print(f"Testing auth endpoint: {BASE_URL}/api/v1/auth/login")
    
    try:
        # Just test if the endpoint exists, don't attempt actual login
        response = requests.options(f"{BASE_URL}/api/v1/auth/login")
        print(f"Status code: {response.status_code}")
        
        # If OPTIONS returns 200-299, the endpoint likely exists
        return 200 <= response.status_code < 300
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main test function"""
    print(f"API Endpoint Test - {datetime.now().isoformat()}")
    print("=" * 50)
    
    health_result = test_health_endpoint()
    print("\n" + "=" * 50 + "\n")
    auth_result = test_auth_endpoint()
    
    print("\n" + "=" * 50)
    print(f"Health endpoint: {'✅ PASS' if health_result else '❌ FAIL'}")
    print(f"Auth endpoint: {'✅ PASS' if auth_result else '❌ FAIL'}")
    
    # Return exit code based on test results
    if health_result and auth_result:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())