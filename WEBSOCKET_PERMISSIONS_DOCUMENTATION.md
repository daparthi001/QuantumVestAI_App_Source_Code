# WebSocket Permissions Fix

## Overview

This document describes the permanent server-side fix for WebSocket 403 Forbidden errors in the QuantumVestAI application. The fix allows free tier users to connect to market data WebSocket endpoints while maintaining security controls for premium endpoints.

## Problem

Free tier users with `"role":"free"` in their JWT tokens were being rejected when connecting to the `/market-data` and `/ws/market-data` WebSocket endpoints. This was causing 403 Forbidden errors, preventing these users from accessing real-time market data.

## Solution

We implemented a comprehensive server-side fix with the following components:

1. **WebSocket Permissions Module**: A dedicated module for managing WebSocket endpoint permissions
2. **Role-based Access Control**: Refined permission checks based on user roles
3. **Premium Parameter Support**: Added support for a `premium=true` parameter to override role checks when needed
4. **Free Tier Endpoints**: Explicitly defined endpoints that should be accessible to free tier users
5. **Tests**: Added unit tests to verify the permission system works correctly

## Implementation Details

### New Files

- `core/security/websocket_permissions.py`: Core WebSocket permissions logic
- `tests/test_websocket_permissions.py`: Tests for the permission system

### Modified Files

- `api/routers/websocket.py`: Updated to use the new permissions system and handle premium parameter

### Key Permission Rules

1. Free tier users can access:
   - `/market-data`
   - `/ws/market-data`

2. Premium users can additionally access:
   - `/premium/*` endpoints

3. Admin users can access all endpoints

4. The `premium=true` parameter can be used to override role checks (for testing or special cases)

## How It Works

1. When a WebSocket connection request arrives, we:
   - Validate the JWT token
   - Extract user ID and role from the token
   - Check if a premium parameter is provided
   - Apply permission rules based on the endpoint and user role

2. If permission is granted:
   - The connection is accepted
   - The user is added to the connection manager

3. If permission is denied:
   - The connection is closed with code 4003
   - A "Permission denied" reason is provided

## Testing

The fix has been tested with:
- Free tier users connecting to market data endpoints
- Premium users connecting to premium endpoints
- Admin users connecting to all endpoints
- Anonymous connections to public endpoints
- Various invalid token scenarios

## How to Apply This Fix

1. Create the WebSocket permissions module:
   ```
   mkdir -p api/core/security
   cp websocket_permissions.py api/core/security/
   ```

2. Run the WebSocket permissions fix script:
   ```
   python websocket-role-fix.py
   ```

3. Run the tests:
   ```
   cd api
   python -m pytest tests/test_websocket_permissions.py
   ```

4. Restart the API server:
   ```
   kubectl rollout restart deployment quantumvestai-dev-api
   ```

5. Verify the fix is working by having a free tier user connect to the market data WebSocket endpoints.

## Verification

You can verify that the fix is working by:

1. Creating a free tier user account
2. Generating a JWT token with `"role":"free"`
3. Connecting to the `/market-data` WebSocket endpoint
4. Checking that the connection succeeds instead of receiving a 403 error

## Future Improvements

- Add more fine-grained permissions for specific market data types
- Implement rate limiting based on user tiers
- Add usage tracking for analytics and quota enforcement
