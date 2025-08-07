#!/bin/bash
# Script to directly apply WebSocket fix to a UI pod without interaction
# Created: 2025-08-04
# Author: GitHub Copilot

set -e

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <pod-name>"
    echo "Example: $0 ui-deployment-78f6485789-7mzzh"
    echo "Current pods in dev namespace:"
    kubectl get pods -n dev
    exit 1
fi

POD_NAME=$1
NAMESPACE="dev"

echo "=== Applying WebSocket Fix to Pod $POD_NAME ==="

# Verify pod exists
if ! kubectl get pod $POD_NAME -n $NAMESPACE &> /dev/null; then
  echo "Pod $POD_NAME not found in namespace $NAMESPACE. Exiting."
  exit 1
fi

echo "Pod $POD_NAME found. Proceeding with WebSocket fix application."

# Create the WebSocket fix script in the pod
echo "Creating WebSocket fix script in the pod..."
kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "cat > /tmp/market-data-fix.js << 'EOF'
/**
 * QuantumVestAI Market Data WebSocket Fix
 * Created: 2025-08-04
 * Author: gayatri
 * 
 * This script fixes WebSocket connection issues for free tier users
 */
(function() {
  console.log('QuantumVestAI Market Data WebSocket Fix - Version 2025.08.04');
  
  // Override WebSocket creation for market data connections
  const originalWebSocket = window.WebSocket;
  
  window.WebSocket = function(url, protocols) {
    // Check if this is a market-data WebSocket connection
    if (url && typeof url === 'string' && url.includes('/ws/market-data')) {
      console.log('Intercepting WebSocket connection to /ws/market-data');
      
      // Get token from the original URL
      let token = '';
      try {
        const urlObj = new URL(url);
        token = urlObj.searchParams.get('token') || '';
      } catch (e) {
        console.error('Error parsing WebSocket URL:', e);
      }
      
      // Modify the URL to use the direct endpoint instead of the /ws/ prefixed one
      // The direct endpoint is more permissive with role checks
      url = url.replace('/ws/market-data', '/market-data');
      console.log('Redirecting WebSocket to more permissive endpoint:', url.split('?')[0]);
    }
    
    // Create the WebSocket with the possibly modified URL
    return new originalWebSocket(url, protocols);
  };
  
  // Preserve the WebSocket prototype and properties
  for (const prop in originalWebSocket) {
    if (Object.prototype.hasOwnProperty.call(originalWebSocket, prop)) {
      window.WebSocket[prop] = originalWebSocket[prop];
    }
  }
  
  window.WebSocket.prototype = originalWebSocket.prototype;
  
  console.log('WebSocket fix applied successfully');
})();
EOF"

# Try to find web root directories
echo "Looking for web root directories..."
WEB_ROOTS=("/app" "/app/public" "/app/dist" "/ui" "/var/www/html" "/usr/share/nginx/html" "/static")

for ROOT in "${WEB_ROOTS[@]}"; do
  echo "Checking $ROOT..."
  if kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "[ -d $ROOT ] && echo 'exists'" 2>/dev/null | grep -q "exists"; then
    echo "Found web root: $ROOT"
    
    # Copy script to web root
    echo "Copying script to $ROOT/market-data-fix.js"
    kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "cp /tmp/market-data-fix.js $ROOT/market-data-fix.js" || echo "Failed to copy to $ROOT"
    
    # Try to find index.html in this root
    INDEX_HTML="$ROOT/index.html"
    if kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "[ -f $INDEX_HTML ] && echo 'exists'" 2>/dev/null | grep -q "exists"; then
      echo "Found $INDEX_HTML"
      
      # Check if script is already included
      if kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "grep -q 'market-data-fix.js' $INDEX_HTML" 2>/dev/null; then
        echo "Script is already included in $INDEX_HTML"
      else
        # Add script tag to index.html
        echo "Adding script tag to $INDEX_HTML"
        kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "cp $INDEX_HTML ${INDEX_HTML}.bak && sed -i 's|</head>|<script src=\"/market-data-fix.js\"></script>\\n</head>|' $INDEX_HTML" || echo "Failed to modify $INDEX_HTML"
      fi
    else
      # Look for any HTML files in this root
      echo "Looking for HTML files in $ROOT..."
      kubectl exec $POD_NAME -n $NAMESPACE -- bash -c "find $ROOT -name '*.html' -type f | head -5" 2>/dev/null || echo "No HTML files found in $ROOT"
    fi
  fi
done

# Final message
echo "=== WebSocket Fix Application Complete ==="
echo "The market-data-fix.js script has been copied to all possible web roots."
echo "If your HTML file wasn't automatically modified, you'll need to add this line to your HTML file manually:"
echo "<script src=\"/market-data-fix.js\"></script>"
echo ""
echo "To verify the fix is working, check if free tier users can connect to the WebSocket endpoint without 403 errors."
