# API_PREFIX Fix Guide

## Issue Description
The application is failing to start due to a settings attribute error:
```
AttributeError: 'Settings' object has no attribute 'API_PREFIX'
```

This occurs because some files are using `settings.API_PREFIX`, but the settings object only has `API_V1_STR`.

## Solution

We've implemented multiple layers of fixes to ensure this issue is resolved permanently:

### 1. Source Code Fixes
- Fixed `security.py` to use `API_V1_STR` instead of `API_PREFIX`
- Ensured `authentication.py` uses `API_V1_STR` consistently
- Updated the Docker entrypoint script to check and fix any instances of `API_PREFIX`

### 2. Build-time Fixes
- Updated the Dockerfile to apply the API_PREFIX fix during the build process
- Added validation steps to ensure the security module is properly configured

### 3. Runtime Fixes
- Enhanced the docker-entrypoint.sh to check and fix API_PREFIX references
- Added logging to help diagnose any remaining issues

## How to Apply the Fix

### Option 1: Build New Docker Image
This is the recommended approach for a permanent fix:

1. Update the Dockerfile and other source files:
   ```bash
   # Run the direct fix script to update source files
   ./direct_fix_api_prefix.sh
   ```

2. Build and deploy a new Docker image:
   ```bash
   # Navigate to the API directory
   cd ai-stock-platform/api
   
   # Build the image
   docker build -t quantumvestai:websocket-fix .
   
   # Push to your registry
   docker tag quantumvestai:websocket-fix ${YOUR_REGISTRY}/quantumvestai:websocket-fix
   docker push ${YOUR_REGISTRY}/quantumvestai:websocket-fix
   
   # Update the deployment
   kubectl set image deployment/quantumvestai-api api=${YOUR_REGISTRY}/quantumvestai:websocket-fix -n quantumvestai
   ```

### Option 2: Apply Fix to Running Pods
For a quick fix without rebuilding:

1. Run the direct fix script:
   ```bash
   # Apply the fix to the local files
   ./direct_fix_api_prefix.sh
   ```

2. Apply the fix to the Kubernetes pods:
   ```bash
   kubectl apply -f fix_api_prefix_job.yaml
   ```

### Option 3: Manual Fix
If needed, you can manually fix the running containers:

1. Connect to each pod and apply the fix:
   ```bash
   # Find all API pods
   kubectl get pods -n quantumvestai -l app=quantumvestai-api
   
   # Connect to each pod and fix the issue
   kubectl exec -it POD_NAME -n quantumvestai -- bash
   
   # Inside the pod:
   sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security/authentication.py
   sed -i "s/settings.API_PREFIX/settings.API_V1_STR/g" /app/core/security.py
   ```

2. Restart the pods:
   ```bash
   kubectl rollout restart deployment/quantumvestai-api -n quantumvestai
   ```

## Verification

After applying the fix, verify that the API starts correctly:

```bash
# Check pod status
kubectl get pods -n quantumvestai

# Check pod logs
kubectl logs -n quantumvestai POD_NAME

# Test the API
curl https://api.quantumvestai.com/api/v1/health
```

If you see the API responding without errors, the fix has been successfully applied.

## Prevention

To prevent this issue in the future:

1. Use consistent variable names across the codebase
2. Add automated tests to check for configuration consistency
3. Include validation in the CI/CD pipeline to catch similar issues
4. Consider using a single settings file with clear naming conventions
