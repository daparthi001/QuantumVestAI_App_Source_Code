# WebSocket Permissions Fix for QuantumVestAI

## Overview

This document outlines the steps to deploy and test the WebSocket permissions fix for the QuantumVestAI application. The fix resolves 403 Forbidden errors that free tier users encounter when connecting to WebSocket endpoints.

## Problem Description

Free tier users with `"role":"free"` in their JWT tokens were being rejected when connecting to the `/market-data` and `/ws/market-data` WebSocket endpoints, resulting in 403 Forbidden errors.

## Solution

Our solution implements:
- A WebSocket permissions module (`websocket_permissions.py`)
- Role-based access control for WebSocket endpoints
- Support for a `premium=true` parameter to override role checks
- Proper logging for permission decisions

## Deployment Steps

1. **Review the Code**
   - Check the WebSocket permissions module in `core/security/websocket_permissions.py`
   - Review the implementation in the WebSocket router (`routers/websocket.py`)

2. **Build and Deploy**
   ```bash
   # Make the deployment script executable
   chmod +x deploy_websocket_fix.sh
   
   # Run the deployment script
   ./deploy_websocket_fix.sh
   ```

3. **Verify the Fix**
   ```bash
   # Run the verification script
   python verify_websocket_fix.py
   
   # Test real connections
   python test_websocket_client.py
   ```

4. **Rollback (if needed)**
   ```bash
   # Rollback to previous deployment
   kubectl rollout undo deployment quantumvestai-dev-api
   ```

## Files Modified

- `/core/security/websocket_permissions.py`: Permission system implementation
- `/core/security/__init__.py`: Security package initialization
- `/core/security/authentication.py`: User authentication functions
- `/core/security/tokens.py`: JWT token handling
- `/routers/websocket.py`: WebSocket endpoints with permission checks
- `/Dockerfile`: Updated to properly copy security files
- `/docker-entrypoint.sh`: Added security module validation

## Testing

The fix has been tested with:
- Free tier users connecting to market data endpoints
- Premium users connecting to premium endpoints
- Admin users connecting to all endpoints
- Anonymous connections to public endpoints
- Various invalid token scenarios

## Troubleshooting

If you encounter issues after deployment:

1. **Check Pod Logs**
   ```bash
   kubectl logs -n quantumvestai deployment/quantumvestai-api
   ```

2. **Verify Module Structure**
   ```bash
   # Connect to a pod
   kubectl exec -it -n quantumvestai $(kubectl get pods -n quantumvestai -l app=quantumvestai-api -o name | head -1) -- bash
   
   # Check the module structure
   ls -la /app/core/security/
   
   # Verify imports work
   python -c "from core.security import get_current_active_user; print('Success')"
   ```

3. **Common Errors**
   - Import errors: Check file paths in the Dockerfile and module structure
   - 403 Errors: Check JWT token validation and role assignment
   - WebSocket connection issues: Check CORS settings and token extraction

## Contact

For issues with this fix, please contact:
- gayatri@quantumvestai.com
- daparthi001@quantumvestai.com
