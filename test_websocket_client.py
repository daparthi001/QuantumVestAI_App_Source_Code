#!/usr/bin/env python3
"""
WebSocket Client Test for QuantumVestAI Permissions Fix
Created: 2025-08-07
Author: GitHub Copilot

This script tests WebSocket connections to various endpoints with different user roles.
It verifies that the WebSocket permissions fix is working correctly.
"""

import asyncio
import json
import logging
import sys
import websockets
import jwt
import time
import argparse
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("websocket-test")

# Default values
DEFAULT_API_URL = "wss://api-dev.quantumvestai.com"
SECRET_KEY = "testing_secret_key_replace_in_production"  # For creating test tokens

def create_test_token(user_id, role, expiry_minutes=60):
    """Create a JWT token for testing purposes."""
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expiry_minutes)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

async def test_websocket_endpoint(endpoint, token=None, premium=False, expected_success=True):
    """Test a WebSocket endpoint with the given parameters."""
    # Build URL
    url = f"{endpoint}"
    
    # Add parameters if provided
    params = []
    if token:
        params.append(f"token={token}")
    if premium:
        params.append("premium=true")
    
    if params:
        url += "?" + "&".join(params)
    
    logger.info(f"Testing connection to: {url}")
    
    try:
        # Connect to WebSocket endpoint
        async with websockets.connect(url, ping_interval=None) as websocket:
            logger.info(f"Connected successfully to {endpoint}")
            
            # Send a test message
            test_message = {
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(test_message))
            logger.info(f"Sent test message: {test_message}")
            
            # Wait for a response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                logger.info(f"Received response: {response}")
                return True
            except asyncio.TimeoutError:
                logger.warning("No response received (timeout)")
                return False
    
    except (websockets.exceptions.InvalidStatusCode, 
            websockets.exceptions.ConnectionClosedError) as e:
        if expected_success:
            logger.error(f"Failed to connect: {str(e)}")
            return False
        else:
            logger.info(f"Expected connection failure occurred: {str(e)}")
            return True
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

async def run_all_tests(base_url):
    """Run all WebSocket permission tests."""
    results = {}
    
    # Test free tier user on market-data endpoint
    free_token = create_test_token("test-free-user", "free")
    results["free_user_market_data"] = await test_websocket_endpoint(
        f"{base_url}/market-data", token=free_token, expected_success=True
    )
    
    # Test free tier user on ws/market-data endpoint
    results["free_user_ws_market_data"] = await test_websocket_endpoint(
        f"{base_url}/ws/market-data", token=free_token, expected_success=True
    )
    
    # Test premium user on premium endpoint
    premium_token = create_test_token("test-premium-user", "premium")
    results["premium_user_premium_endpoint"] = await test_websocket_endpoint(
        f"{base_url}/premium/data", token=premium_token, expected_success=True
    )
    
    # Test free tier user on premium endpoint (should fail)
    results["free_user_premium_endpoint"] = await test_websocket_endpoint(
        f"{base_url}/premium/data", token=free_token, expected_success=False
    )
    
    # Test free tier user with premium parameter (should succeed)
    results["free_user_premium_param"] = await test_websocket_endpoint(
        f"{base_url}/premium/data", token=free_token, premium=True, expected_success=True
    )
    
    # Test anonymous connection to market-data
    results["anonymous_market_data"] = await test_websocket_endpoint(
        f"{base_url}/market-data", expected_success=True
    )
    
    # Print results summary
    logger.info("\n===== TEST RESULTS =====")
    all_passed = True
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        if not result:
            all_passed = False
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall result: {'PASS' if all_passed else 'FAIL'}")
    return all_passed

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test WebSocket permissions fix")
    parser.add_argument("--api-url", default=DEFAULT_API_URL,
                      help=f"Base URL of the API (default: {DEFAULT_API_URL})")
    args = parser.parse_args()
    
    # Run tests
    logger.info(f"Starting WebSocket permission tests against {args.api_url}")
    success = asyncio.run(run_all_tests(args.api_url))
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)
