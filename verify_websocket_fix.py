#!/usr/bin/env python3
"""
WebSocket Fix Verification Script

This script verifies that the improved WebSocket fix is working
by checking the logs for 403 Forbidden errors after the fix was applied.

Usage:
    python verify_websocket_fix.py

Author: GitHub Copilot
Date: August 4, 2025
"""

import subprocess
import re
import time
import sys
from datetime import datetime

def run_kubectl_command(command):
    """Run kubectl command and return output"""
    try:
        result = subprocess.run(command, shell=True, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {command}")
        print(f"Error: {e.stderr}")
        return None

def get_pod_logs(pod_name, namespace="dev", container=None, since="5m"):
    """Get logs from a pod"""
    container_arg = f"--container {container}" if container else ""
    command = f"kubectl logs {pod_name} -n {namespace} {container_arg} --since={since}"
    return run_kubectl_command(command)

def find_api_pod():
    """Find the API pod"""
    command = "kubectl get pods -n dev -o name | grep api"
    return run_kubectl_command(command).strip()

def check_for_websocket_errors(logs):
    """Check for WebSocket 403 Forbidden errors in logs"""
    # Find all WebSocket connection attempts
    websocket_pattern = r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*?)\] .*?WebSocket /market-data\?token=(.*?) (\d{3})"
    websocket_attempts = re.findall(websocket_pattern, logs)
    
    # Count successful and failed attempts
    total_attempts = len(websocket_attempts)
    failed_attempts = sum(1 for _, _, status in websocket_attempts if status == "403")
    successful_attempts = total_attempts - failed_attempts
    
    # Extract timestamps of the last few attempts
    recent_attempts = []
    for timestamp, token_part, status in websocket_attempts[-5:]:
        token_prefix = token_part[:20] + "..."
        recent_attempts.append({
            "timestamp": timestamp,
            "token": token_prefix,
            "status": status
        })
    
    return {
        "total_attempts": total_attempts,
        "failed_attempts": failed_attempts,
        "successful_attempts": successful_attempts,
        "recent_attempts": recent_attempts
    }

def verify_websocket_fix():
    """Main verification function"""
    print("=== Verifying WebSocket Fix ===")
    
    # Get the API pod
    api_pods = find_api_pod()
    if not api_pods:
        print("No API pod found. Exiting.")
        return False
    
    api_pod = api_pods.split('\n')[0]
    print(f"Using API pod: {api_pod}")
    
    # Get logs from the API pod
    print("Getting logs from API pod...")
    logs = get_pod_logs(api_pod)
    if not logs:
        print("Could not get logs from API pod. Exiting.")
        return False
    
    # Check for WebSocket errors
    print("Analyzing logs for WebSocket connection attempts...")
    results = check_for_websocket_errors(logs)
    
    # Print results
    print(f"\nTotal WebSocket connection attempts: {results['total_attempts']}")
    print(f"Failed attempts (403 Forbidden): {results['failed_attempts']}")
    print(f"Successful attempts: {results['successful_attempts']}")
    
    print("\nRecent connection attempts:")
    for attempt in results['recent_attempts']:
        print(f"  {attempt['timestamp']} - Status: {attempt['status']} - Token: {attempt['token']}")
    
    # Check if there are no recent 403 errors
    recent_errors = sum(1 for attempt in results['recent_attempts'] if attempt['status'] == "403")
    
    if recent_errors == 0:
        print("\nSUCCESS: No recent 403 Forbidden errors found!")
        print("The WebSocket fix appears to be working correctly.")
        return True
    else:
        print(f"\nWARNING: Found {recent_errors} recent 403 Forbidden errors.")
        print("The WebSocket fix might not be working correctly.")
        
        # Provide additional diagnostic information
        print("\nDiagnostic Information:")
        print("1. Checking if the script is in the UI pod...")
        
        ui_pod = run_kubectl_command("kubectl get pods -n dev | grep ui-deployment | awk '{print $1}'").strip()
        if ui_pod:
            script_check = run_kubectl_command(f"kubectl exec -n dev {ui_pod} -- ls -l /app/market-data-fix.js 2>/dev/null || echo 'Not found'")
            print(f"   Script in UI pod: {'Not found' if 'Not found' in script_check else 'Found'}")
            
            if 'Not found' not in script_check:
                script_content = run_kubectl_command(f"kubectl exec -n dev {ui_pod} -- grep -A 2 premium=true /app/market-data-fix.js 2>/dev/null || echo 'premium parameter not found'")
                print(f"   Script premium parameter: {'Not found' if 'premium parameter not found' in script_content else 'Found'}")
        
        print("\nRecommendations:")
        print("1. Verify that the market-data-fix.js script is included in the HTML")
        print("2. Check if the script is being loaded properly in the browser")
        print("3. Check for any JavaScript errors in the browser console")
        print("4. Verify that the premium=true parameter is being added to the WebSocket URL")
        
        return False

if __name__ == "__main__":
    success = verify_websocket_fix()
    sys.exit(0 if success else 1)
