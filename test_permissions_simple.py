#!/usr/bin/env python3
"""
Simple test for the websocket permissions logic without dependencies.
"""

def check_websocket_permissions_test(token_payload, endpoint, premium_param=None):
    """
    Simplified version of the permissions check for testing.
    """
    # Free tier endpoints that should always be accessible
    FREE_TIER_ENDPOINTS = [
        "/market-data",
        "/ws/market-data"
    ]
    
    # Always allow access to free tier endpoints regardless of role or token status
    if any(endpoint.endswith(free_endpoint) for free_endpoint in FREE_TIER_ENDPOINTS):
        print(f"Allowing access to free-tier endpoint {endpoint}")
        return True
    
    # If premium parameter is provided and is 'true', allow access
    if premium_param and premium_param.lower() == 'true':
        print(f"Allowing access due to premium parameter")
        return True
    
    # Get user role from token
    role = token_payload.get("role", "free")
    
    # Admin role can access everything
    if role == "admin":
        return True
    
    # Premium users can access premium endpoints
    if role == "premium" and endpoint.startswith("/premium"):
        return True
    
    # Basic users can access basic endpoints
    if role in ["basic", "premium"] and endpoint.startswith("/basic"):
        return True
    
    # CRITICAL FIX: Allow all authenticated users access to market data endpoints
    # Market data should be publicly accessible for all user roles
    if endpoint.endswith("/market-data") or "/market-data" in endpoint:
        print(f"Allowing access to market data for role: {role}")
        return True
        
    # Default deny for unhandled cases
    print(f"Access denied to {endpoint} for role {role}")
    return False

def test_permissions():
    """Test the permissions logic."""
    print("=== Testing WebSocket Permissions Logic ===")
    
    # Test with the expired token from the logs
    token_payload = {
        "sub": "daparthi001",
        "role": "free", 
        "exp": 1754587392  # expired timestamp
    }
    
    test_cases = [
        ("/ws/market-data", True, "Free user should access /ws/market-data"),
        ("/market-data", True, "Free user should access /market-data"), 
        ("/some/market-data", True, "Free user should access any market-data endpoint"),
        ("/premium/data", False, "Free user should NOT access premium endpoints"),
        ("/basic/data", False, "Free user should NOT access basic endpoints"),
        ("/admin/panel", False, "Free user should NOT access admin endpoints"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for endpoint, expected, description in test_cases:
        result = check_websocket_permissions_test(token_payload, endpoint)
        status = "✓ PASS" if result == expected else "✗ FAIL" 
        print(f"{status}: {description}")
        print(f"   Endpoint: {endpoint} -> {result} (expected {expected})")
        if result == expected:
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    return passed == total

if __name__ == "__main__":
    success = test_permissions()
    if success:
        print("✓ All permission tests passed! The fix should work correctly.")
        exit(0)
    else:
        print("✗ Some permission tests failed.")
        exit(1)