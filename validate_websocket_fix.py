#!/usr/bin/env python3
"""
WebSocket Fix Validation Script

This script validates that the WebSocket redirection fix is properly applied
to redirect /ws/market-data endpoints to /market-data for free tier users.

Usage:
    python validate_websocket_fix.py

Author: GitHub Copilot
Date: August 4, 2025
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_kubectl_command(command):
    """Run kubectl command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error: {e.stderr}")
        return None

def check_configmap_content():
    """Check if the ConfigMap has the WebSocket fix script"""
    logger.info("Checking if ConfigMap has the WebSocket fix script...")
    
    cm_output = run_kubectl_command("kubectl get configmap ui-scripts -n dev -o yaml")
    if not cm_output:
        logger.error("Failed to get ConfigMap content")
        return False
    
    # Check if market-data-fix.js exists in the ConfigMap
    if "market-data-fix.js" not in cm_output:
        logger.error("market-data-fix.js not found in ConfigMap")
        return False
    
    # Check if the WebSocket redirection logic is present
    ws_fix_patterns = [
        "Override WebSocket creation",
        "url.replace('/ws/market-data', '/market-data')",
        "Redirecting WebSocket to more permissive endpoint"
    ]
    
    for pattern in ws_fix_patterns:
        if pattern not in cm_output:
            logger.error(f"WebSocket fix pattern not found: {pattern}")
            return False
    
    logger.info("✓ ConfigMap has the correct WebSocket fix script")
    return True

def check_pod_mounts():
    """Check if pods have the ConfigMap mounted correctly"""
    logger.info("Checking if UI pods have the ConfigMap mounted...")
    
    # First, list all pods to see what's available
    logger.info("Available pods in dev namespace:")
    run_kubectl_command("kubectl get pods -n dev")
    
    # Try various label combinations to find UI pods
    label_combinations = [
        "app=ui", 
        "app=frontend", 
        "tier=frontend", 
        "component=ui", 
        "app=quantumvestai"
    ]
    
    pods_output = None
    for labels in label_combinations:
        logger.info(f"Trying to find pods with label: {labels}")
        pods_output = run_kubectl_command(f"kubectl get pods -n dev -l {labels} -o name")
        if pods_output and pods_output.strip():
            logger.info(f"Found pods with label {labels}")
            break
    
    # If no pods found with labels, try grepping for UI/frontend in names
    if not pods_output or not pods_output.strip():
        logger.info("No UI pods found with standard labels. Trying to find pod names containing 'ui' or 'frontend'")
        pods_output = run_kubectl_command("kubectl get pods -n dev -o name | grep -E 'ui|frontend'")
    
    # If still no pods found, list all pods for manual selection
    if not pods_output or not pods_output.strip():
        logger.error("No UI pods found automatically. Please check your pod names manually.")
        logger.info("Pods available in dev namespace:")
        run_kubectl_command("kubectl get pods -n dev")
        return False
    
    pod_names = pods_output.strip().split('\n')
    all_pods_ok = True
    
    for pod_name in pod_names:
        pod = pod_name.strip()
        if not pod:
            continue
            
        # Check if pod has the ConfigMap mounted
        pod_desc = run_kubectl_command(f"kubectl describe {pod} -n dev")
        if not pod_desc:
            logger.error(f"Failed to describe pod {pod}")
            all_pods_ok = False
            continue
        
        if "ui-scripts" not in pod_desc:
            logger.error(f"Pod {pod} does not have ui-scripts ConfigMap mounted")
            all_pods_ok = False
            continue
            
        logger.info(f"✓ Pod {pod} has the ConfigMap mounted")
        
        # Check if the script is present in the container
        script_check = run_kubectl_command(f"kubectl exec {pod} -n dev -- ls /scripts/market-data-fix.js 2>/dev/null || echo 'not found'")
        if script_check and "not found" not in script_check:
            logger.info(f"✓ Pod {pod} has market-data-fix.js in /scripts")
        else:
            # Try alternate locations
            alternate_locations = ["/ui-scripts/", "/config/", "/"]
            found = False
            for loc in alternate_locations:
                script_check = run_kubectl_command(f"kubectl exec {pod} -n dev -- ls {loc}market-data-fix.js 2>/dev/null || echo 'not found'")
                if script_check and "not found" not in script_check:
                    logger.info(f"✓ Pod {pod} has market-data-fix.js in {loc}")
                    found = True
                    break
            
            if not found:
                logger.error(f"Pod {pod} does not have market-data-fix.js script")
                all_pods_ok = False
    
    return all_pods_ok

def check_script_inclusion_in_html():
    """Check if the script is included in the HTML files"""
    logger.info("Checking if WebSocket fix script is included in HTML files...")
    
    # Try various label combinations to find UI pods
    label_combinations = [
        "app=ui", 
        "app=frontend", 
        "tier=frontend", 
        "component=ui", 
        "app=quantumvestai"
    ]
    
    pod_output = None
    for labels in label_combinations:
        pod_output = run_kubectl_command(f"kubectl get pods -n dev -l {labels} -o name | head -1")
        if pod_output and pod_output.strip():
            break
    
    # If no pods found with labels, try grepping for UI/frontend in names
    if not pod_output or not pod_output.strip():
        pod_output = run_kubectl_command("kubectl get pods -n dev -o name | grep -E 'ui|frontend' | head -1")
    
    # If still no pods found, list all pods for manual selection
    if not pod_output or not pod_output.strip():
        logger.error("No UI pod found. Please check your pod names manually.")
        run_kubectl_command("kubectl get pods -n dev")
        return False
    
    pod_name = pod_output.strip()
    
    # Check if the script is included in index.html or other HTML files
    html_content = run_kubectl_command(f"kubectl exec {pod_name} -n dev -- cat /app/index.html 2>/dev/null || echo 'not found'")
    if not html_content or "not found" in html_content:
        # Try alternate paths
        alt_paths = ["/app/public/index.html", "/app/dist/index.html", "/ui/index.html"]
        for path in alt_paths:
            html_content = run_kubectl_command(f"kubectl exec {pod_name} -n dev -- cat {path} 2>/dev/null || echo 'not found'")
            if html_content and "not found" not in html_content:
                break
    
    if not html_content or "not found" in html_content:
        logger.error("Could not find index.html in the pod")
        return False
    
    # Check if market-data-fix.js is referenced
    if "market-data-fix.js" in html_content:
        logger.info("✓ market-data-fix.js is included in the HTML")
        return True
    else:
        logger.warning("⚠ market-data-fix.js is NOT included in the HTML")
        # Create a script to add the script tag to the HTML
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("""#!/bin/bash
# Add WebSocket fix script to index.html
# This should be run in the container

set -e

# Find the index.html file
INDEX_FILES=( 
  "/app/index.html"
  "/app/public/index.html" 
  "/app/dist/index.html"
  "/ui/index.html"
)

for INDEX_FILE in "${INDEX_FILES[@]}"; do
  if [ -f "$INDEX_FILE" ]; then
    echo "Found index.html at $INDEX_FILE"
    
    # Check if script is already included
    if grep -q "market-data-fix.js" "$INDEX_FILE"; then
      echo "market-data-fix.js is already included in $INDEX_FILE"
      exit 0
    fi
    
    # Find the script tag location
    if grep -q "</head>" "$INDEX_FILE"; then
      # Add the script right before </head>
      sed -i 's|</head>|<script src="/market-data-fix.js"></script>\\n</head>|' "$INDEX_FILE"
      echo "Added market-data-fix.js to $INDEX_FILE before </head>"
    else
      # Try adding after the first script tag
      sed -i '/<script/a <script src="/market-data-fix.js"></script>' "$INDEX_FILE"
      echo "Added market-data-fix.js to $INDEX_FILE after first script tag"
    fi
    
    exit 0
  fi
done

echo "Could not find index.html file"
exit 1
""")
            script_path = f.name
        
        logger.info(f"Created script to add market-data-fix.js to index.html at {script_path}")
        logger.info("You can copy this script to the pod and run it")
        return False

def check_script_in_webserver_root():
    """Check if the script is in the webserver root directory"""
    logger.info("Checking if WebSocket fix script is in webserver root directory...")
    
    # Try various label combinations to find UI pods
    label_combinations = [
        "app=ui", 
        "app=frontend", 
        "tier=frontend", 
        "component=ui", 
        "app=quantumvestai"
    ]
    
    pod_output = None
    for labels in label_combinations:
        pod_output = run_kubectl_command(f"kubectl get pods -n dev -l {labels} -o name | head -1")
        if pod_output and pod_output.strip():
            break
    
    # If no pods found with labels, try grepping for UI/frontend in names
    if not pod_output or not pod_output.strip():
        pod_output = run_kubectl_command("kubectl get pods -n dev -o name | grep -E 'ui|frontend' | head -1")
    
    # If still no pods found, list all pods for manual selection
    if not pod_output or not pod_output.strip():
        logger.error("No UI pod found. Please check your pod names manually.")
        run_kubectl_command("kubectl get pods -n dev")
        return False
    
    pod_name = pod_output.strip()
    
    # Check if the script is in the webserver root
    webserver_paths = ["/app/", "/app/public/", "/app/dist/", "/ui/", "/var/www/html/", "/usr/share/nginx/html/"]
    script_found = False
    
    for path in webserver_paths:
        script_check = run_kubectl_command(f"kubectl exec {pod_name} -n dev -- ls {path}market-data-fix.js 2>/dev/null || echo 'not found'")
        if script_check and "not found" not in script_check:
            logger.info(f"✓ market-data-fix.js found in {path}")
            script_found = True
            break
    
    if not script_found:
        logger.error("⚠ market-data-fix.js not found in webserver root directories")
        
        # Create a script to copy the script to webserver root
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("""#!/bin/bash
# Copy WebSocket fix script to webserver root
# This should be run in the container

set -e

# Find the script
SCRIPT_PATHS=(
  "/scripts/market-data-fix.js"
  "/ui-scripts/market-data-fix.js"
  "/config/market-data-fix.js"
)

# Find the webserver root
WEB_ROOTS=(
  "/app/"
  "/app/public/"
  "/app/dist/"
  "/ui/"
  "/var/www/html/"
  "/usr/share/nginx/html/"
)

# Find the script
SCRIPT_PATH=""
for PATH in "${SCRIPT_PATHS[@]}"; do
  if [ -f "$PATH" ]; then
    SCRIPT_PATH="$PATH"
    echo "Found script at $SCRIPT_PATH"
    break
  fi
done

if [ -z "$SCRIPT_PATH" ]; then
  echo "Could not find market-data-fix.js script"
  exit 1
fi

# Copy to webserver roots
SUCCESS=0
for ROOT in "${WEB_ROOTS[@]}"; do
  if [ -d "$ROOT" ]; then
    echo "Copying to $ROOT"
    cp "$SCRIPT_PATH" "${ROOT}market-data-fix.js"
    SUCCESS=1
  fi
done

if [ $SUCCESS -eq 1 ]; then
  echo "Successfully copied market-data-fix.js to webserver root"
else
  echo "Could not find a suitable webserver root directory"
  exit 1
fi
""")
            script_path = f.name
        
        logger.info(f"Created script to copy market-data-fix.js to webserver root at {script_path}")
        logger.info("You can copy this script to the pod and run it")
        return False
    
    return True

def create_pod_restart_script():
    """Create a script to restart the pods"""
    logger.info("Creating script to restart the pods...")
    
    script_path = "/Users/gayatri/QuantumVestAI_App_Source_Code/restart_ui_pods.sh"
    with open(script_path, 'w') as f:
        f.write("""#!/bin/bash
# Script to restart UI pods to pick up ConfigMap changes
# Created: 2025-08-04

set -e

echo "=== Restarting QuantumVestAI UI pods ==="

# Get all UI pods
UI_PODS=$(kubectl get pods -n dev -l app=quantumvestai,tier=frontend -o name)

if [ -z "$UI_PODS" ]; then
  echo "No UI pods found"
  exit 1
fi

# Restart pods one by one
for POD in $UI_PODS; do
  echo "Restarting $POD..."
  kubectl delete $POD -n dev
  echo "Waiting for new pod to be ready..."
  sleep 3
done

# Wait for all pods to be ready
echo "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pods -l app=quantumvestai,tier=frontend -n dev --timeout=120s

echo "=== UI pods restarted ==="

# Verify pods have the ConfigMap mounted
echo "=== Verifying ConfigMap mount ==="
for POD in $(kubectl get pods -n dev -l app=quantumvestai,tier=frontend -o name); do
  echo "Checking $POD..."
  kubectl describe $POD -n dev | grep -A 5 "ui-scripts"
done

echo "=== Pod restart complete ==="
""")
    
    os.chmod(script_path, 0o755)
    logger.info(f"Created pod restart script at {script_path}")
    return script_path

def validate_websocket_fix():
    """Main validation function"""
    success = True
    
    # Check if ConfigMap has the WebSocket fix
    if not check_configmap_content():
        success = False
        logger.error("⚠ ConfigMap does not have the correct WebSocket fix script")
    
    # Check if pods have the ConfigMap mounted
    pod_mounts_ok = check_pod_mounts()
    if not pod_mounts_ok:
        success = False
        logger.warning("⚠ Some pods might not have the ConfigMap mounted properly")
        
        # Create pod restart script
        restart_script = create_pod_restart_script()
        logger.info(f"You can run {restart_script} to restart the pods")
    
    # Check if script is included in HTML
    if not check_script_inclusion_in_html():
        success = False
        logger.warning("⚠ WebSocket fix script is not included in the HTML")
    
    # Check if script is in webserver root
    if not check_script_in_webserver_root():
        success = False
        logger.warning("⚠ WebSocket fix script is not in the webserver root directory")
    
    # Print summary
    if success:
        logger.info("✅ WebSocket fix is properly applied")
        print("\nValidation complete. The WebSocket fix is properly applied.")
        print("The pods should now redirect /ws/market-data WebSocket connections to /market-data for free tier users.")
    else:
        logger.error("❌ WebSocket fix is not properly applied")
        print("\nValidation found issues with the WebSocket fix application.")
        print("\nRecommendations:")
        print("1. Make sure the ConfigMap is properly mounted to the pods")
        print("2. Make sure the market-data-fix.js script is accessible by the web application")
        print("3. Make sure the market-data-fix.js script is included in the HTML")
        print("4. Restart the pods to pick up the ConfigMap changes")
        print("\nYou can run the restart_ui_pods.sh script to restart the pods.")
    
    return success

if __name__ == "__main__":
    success = validate_websocket_fix()
    sys.exit(0 if success else 1)
