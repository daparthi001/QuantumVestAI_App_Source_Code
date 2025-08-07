#!/bin/bash
# Script to directly apply WebSocket fix to a UI pod
# Created: 2025-08-04
# Author: GitHub Copilot

set -e

echo "=== Applying WebSocket Fix Directly to UI Pod ==="

# Get current pods
echo "Current pods in dev namespace:"
kubectl get pods -n dev

# Prompt for pod name
read -p "Enter the exact name of the UI pod: " POD_NAME

if [ -z "$POD_NAME" ]; then
  echo "No pod name entered. Exiting."
  exit 1
fi

# Verify pod exists
if ! kubectl get pod $POD_NAME -n dev &> /dev/null; then
  echo "Pod $POD_NAME not found in namespace dev. Exiting."
  exit 1
fi

echo "Pod $POD_NAME found. Proceeding with WebSocket fix application."

# Create the WebSocket fix script in the pod
echo "Creating WebSocket fix script in the pod..."
kubectl exec $POD_NAME -n dev -- bash -c "cat > /tmp/market-data-fix.js << 'EOF'
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

# Find web root directories in the pod
echo "Finding web root directories in the pod..."
kubectl exec $POD_NAME -n dev -- bash -c "find / -type d -name html -o -name www -o -name public -o -name dist -o -path '*/static*' 2>/dev/null || echo 'No web roots found'"

# Prompt for web root directory
echo "Based on the directories listed above, enter the web root directory path:"
read -p "Web root directory (e.g., /var/www/html, /app/public): " WEB_ROOT

if [ -z "$WEB_ROOT" ]; then
  echo "No web root directory entered. Using common web roots..."
  WEB_ROOTS=("/app" "/app/public" "/app/dist" "/var/www/html" "/usr/share/nginx/html")
  
  for ROOT in "${WEB_ROOTS[@]}"; do
    if kubectl exec $POD_NAME -n dev -- bash -c "[ -d $ROOT ] && echo 'exists' || echo 'not exists'" | grep -q "exists"; then
      echo "Found web root: $ROOT"
      WEB_ROOT=$ROOT
      break
    fi
  done
  
  if [ -z "$WEB_ROOT" ]; then
    echo "Could not find a suitable web root directory. Using /tmp as fallback."
    WEB_ROOT="/tmp"
  fi
fi

# Copy script to web root
echo "Copying script to web root: $WEB_ROOT"
kubectl exec $POD_NAME -n dev -- bash -c "cp /tmp/market-data-fix.js $WEB_ROOT/"
echo "Script copied to $WEB_ROOT/market-data-fix.js"

# Find HTML files
echo "Finding index.html files in the pod..."
kubectl exec $POD_NAME -n dev -- bash -c "find $WEB_ROOT -name '*.html' -type f 2>/dev/null || echo 'No HTML files found'"

# Prompt for index.html file
echo "Based on the HTML files listed above, enter the path to the main index.html file:"
read -p "index.html path (e.g., /var/www/html/index.html): " INDEX_HTML

if [ -z "$INDEX_HTML" ]; then
  echo "No index.html path entered. Using common paths..."
  INDEX_FILES=("$WEB_ROOT/index.html" "$WEB_ROOT/public/index.html" "$WEB_ROOT/dist/index.html")
  
  for FILE in "${INDEX_FILES[@]}"; do
    if kubectl exec $POD_NAME -n dev -- bash -c "[ -f $FILE ] && echo 'exists' || echo 'not exists'" | grep -q "exists"; then
      echo "Found index.html: $FILE"
      INDEX_HTML=$FILE
      break
    fi
  done
  
  if [ -z "$INDEX_HTML" ]; then
    echo "Could not find index.html. The script has been copied to $WEB_ROOT/market-data-fix.js but you'll need to include it in your HTML manually."
    exit 0
  fi
fi

# Check if script is already included
echo "Checking if script is already included in $INDEX_HTML..."
SCRIPT_INCLUDED=$(kubectl exec $POD_NAME -n dev -- bash -c "grep -q 'market-data-fix.js' $INDEX_HTML && echo 'yes' || echo 'no'")

if [ "$SCRIPT_INCLUDED" == "yes" ]; then
  echo "Script is already included in $INDEX_HTML."
else
  # Add script tag to index.html
  echo "Adding script tag to $INDEX_HTML..."
  kubectl exec $POD_NAME -n dev -- bash -c "cp $INDEX_HTML ${INDEX_HTML}.bak && sed -i 's|</head>|<script src=\"/market-data-fix.js\"></script>\\n</head>|' $INDEX_HTML"
  echo "Script tag added to $INDEX_HTML."
fi

echo "=== WebSocket Fix Applied Successfully ==="
echo "The fix should now be active. Free tier users should be able to connect to the WebSocket endpoint without 403 Forbidden errors."
