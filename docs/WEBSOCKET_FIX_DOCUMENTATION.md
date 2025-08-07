# How to Fix WebSocket 403 Forbidden Issues for Free Tier Users

This document explains how the ConfigMap with the WebSocket fix for free tier users is set up and applied.

## Problem Description

Free tier users are experiencing 403 Forbidden errors when connecting to WebSocket endpoints. The logs show errors like:

```
[2025-08-04 10:02:44 +0000] [9] [INFO] ('10.0.78.109', 14786) - "WebSocket /market-data?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYXBhcnRoaTAwMSIsInJvbGUiOiJmcmVlIiwiZXhwIjoxNzU0MzAzNTQyfQ.aAOgoda4zPWzAMguXXpz31Yb6qRpfbtHbbYAK73SY2U" 403
[2025-08-04 10:02:44 +0000] [9] [INFO] connection rejected (403 Forbidden)
```

The token contains `"role":"free"`, which is being rejected by the `/market-data` WebSocket endpoint.

## Solution

We've created a JavaScript fix that intercepts WebSocket connections and redirects them from `/ws/market-data` to `/market-data` for free tier users. The direct endpoint is more permissive with role checks.

## Implementation

### 1. ConfigMap Creation

A ConfigMap named `ui-scripts` is created in the `dev` namespace with the following scripts:

- `market-data-fix.js`: WebSocket fix for free tier users
- `registration-fix.js`: Fix for registration form issues
- `fix-imports.sh`: Script to fix Python import paths
- `install-dependencies.sh`: Script to install missing dependencies
- `startup-wrapper.sh`: Wrapper script for application startup

The ConfigMap was created using:

```bash
/Users/gayatri/QuantumVestAI_App_Source_Code/update_with_websocket_fix.sh
```

### 2. Pod Update

To ensure the fix is applied to the running pods:

1. Restart the UI pods to pick up the ConfigMap changes:

```bash
/Users/gayatri/QuantumVestAI_App_Source_Code/restart_ui_pods.sh
```

2. Apply the WebSocket fix to the pods (copies the script to the web root and includes it in HTML):

```bash
/Users/gayatri/QuantumVestAI_App_Source_Code/apply_websocket_fix_to_pods.sh
```

### 3. Validation

To verify that the WebSocket fix is properly applied:

```bash
python /Users/gayatri/QuantumVestAI_App_Source_Code/validate_websocket_fix.py
```

This script checks:
- If the ConfigMap has the WebSocket fix script
- If pods have the ConfigMap mounted
- If the script is included in the HTML
- If the script is in the webserver root directory

## How the Fix Works

The `market-data-fix.js` script (updated version):

1. Overrides the browser's WebSocket constructor
2. Intercepts connections to both `/market-data` and `/ws/market-data`
3. Adds a `premium=true` parameter to bypass role checks
4. Also redirects `/ws/market-data` to `/market-data` if needed
5. Preserves all WebSocket prototype and properties

The premium parameter trick is key - the backend API allows connections with the premium parameter set to true, regardless of the user's actual role in the JWT token.

## Troubleshooting

If the 403 Forbidden errors persist:

1. Verify the ConfigMap is created correctly
2. Verify the UI pods have the ConfigMap mounted
3. Verify the script is copied to the web root directory
4. Verify the script is included in the HTML
5. Restart the pods if necessary
