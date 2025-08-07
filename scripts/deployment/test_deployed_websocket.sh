#!/bin/bash
# Script to test the WebSocket permissions fix deployment
# Created: 2025-08-04
# Author: gayatri

set -e

# Configuration
API_URL=$(kubectl get svc -n quantumvestai quantumvestai-api -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
if [ -z "$API_URL" ]; then
  echo "Could not determine API URL from Kubernetes service. Using default URL."
  API_URL="api.quantumvestai.com"
fi

echo "=== Testing WebSocket Permissions Fix on $API_URL ==="

# Generate test tokens
echo "Generating test tokens..."

# Free tier user token
FREE_TOKEN=$(curl -s -X POST "https://${API_URL}/api/v1/auth/test-token" \
  -H "Content-Type: application/json" \
  -d '{"role": "free", "username": "test-free-user"}' | jq -r '.token')

# Premium user token
PREMIUM_TOKEN=$(curl -s -X POST "https://${API_URL}/api/v1/auth/test-token" \
  -H "Content-Type: application/json" \
  -d '{"role": "premium", "username": "test-premium-user"}' | jq -r '.token')

echo "Testing /market-data endpoint with free tier user..."
python3 -c "
import asyncio
import websockets
import json

async def test():
    uri = f'wss://${API_URL}/api/v1/market-data?token=${FREE_TOKEN}'
    try:
        async with websockets.connect(uri) as websocket:
            print('Connected successfully with free tier token')
            await websocket.send(json.dumps({'type': 'ping'}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f'Received: {response}')
            return True
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

asyncio.run(test())
"

echo "Testing /ws/market-data endpoint with free tier user..."
python3 -c "
import asyncio
import websockets
import json

async def test():
    uri = f'wss://${API_URL}/api/v1/ws/market-data?token=${FREE_TOKEN}'
    try:
        async with websockets.connect(uri) as websocket:
            print('Connected successfully with free tier token')
            await websocket.send(json.dumps({'type': 'ping'}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f'Received: {response}')
            return True
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

asyncio.run(test())
"

echo "Testing premium endpoint with premium user..."
python3 -c "
import asyncio
import websockets
import json

async def test():
    uri = f'wss://${API_URL}/api/v1/premium/market-data?token=${PREMIUM_TOKEN}'
    try:
        async with websockets.connect(uri) as websocket:
            print('Connected successfully with premium token')
            await websocket.send(json.dumps({'type': 'ping'}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f'Received: {response}')
            return True
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

asyncio.run(test())
"

echo "Testing premium endpoint with free tier user (should fail)..."
python3 -c "
import asyncio
import websockets
import json

async def test():
    uri = f'wss://${API_URL}/api/v1/premium/market-data?token=${FREE_TOKEN}'
    try:
        async with websockets.connect(uri) as websocket:
            print('Connected successfully (unexpected!)')
            await websocket.send(json.dumps({'type': 'ping'}))
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f'Received: {response}')
            return False
    except websockets.exceptions.InvalidStatusCode as e:
        if e.status_code == 4003:  # Expected error code for permission denied
            print('Correctly received permission denied error')
            return True
        else:
            print(f'Unexpected status code: {e.status_code}')
            return False
    except Exception as e:
        print(f'Error: {str(e)}')
        return False

asyncio.run(test())
"

echo "=== Testing Complete ==="
