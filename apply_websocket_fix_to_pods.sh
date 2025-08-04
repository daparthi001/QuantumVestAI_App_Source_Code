#!/bin/bash
# Script to copy WebSocket fix to the correct location in the UI pods
# Created: 2025-08-04
# Author: GitHub Copilot

set -e

echo "=== Copying WebSocket fix to UI pods ==="

# First, list all pods to see what's available
echo "Available pods in dev namespace:"
kubectl get pods -n dev

# Get all UI pods - trying various label combinations
echo "Looking for UI pods..."
echo "Searching for pods with name containing 'ui'..."
UI_PODS=$(kubectl get pods -n dev -o name | grep -i -E 'ui')

if [ -z "$UI_PODS" ]; then
  echo "No pods with 'ui' in name. Looking for pods with 'frontend' in name..."
  UI_PODS=$(kubectl get pods -n dev -o name | grep -i -E 'frontend')
fi

if [ -z "$UI_PODS" ]; then
  echo "No UI-related pods found automatically. Please select a pod manually:"
  kubectl get pods -n dev
  read -p "Enter the name of the UI pod (without the 'pod/' prefix): " POD_NAME
  UI_PODS="pod/$POD_NAME"
fi

echo "Found UI pods: $UI_PODS"

# Verify the pods actually exist (in case they were restarted/replaced)
VERIFIED_PODS=""
for POD in $UI_PODS; do
  if kubectl get $POD -n dev &> /dev/null; then
    echo "$POD exists and will be processed"
    VERIFIED_PODS="$VERIFIED_PODS $POD"
  else
    echo "$POD not found, might have been restarted/replaced"
  fi
done

if [ -z "$VERIFIED_PODS" ]; then
  echo "No verified UI pods found. Getting latest pod list..."
  kubectl get pods -n dev
  read -p "Enter the name of the UI pod (without the 'pod/' prefix): " POD_NAME
  VERIFIED_PODS="pod/$POD_NAME"
fi

UI_PODS=$VERIFIED_PODS

# Generate a temporary script to run inside the pods
TMP_SCRIPT=$(mktemp)
cat << 'EOF' > $TMP_SCRIPT
#!/bin/bash
# Script to copy and include the WebSocket fix
set -e

# Find where the ConfigMap is mounted
SCRIPT_LOCATIONS=( 
  "/scripts/market-data-fix.js" 
  "/ui-scripts/market-data-fix.js" 
  "/config/market-data-fix.js"
  "/market-data-fix.js"
)

SCRIPT_FOUND=0
SCRIPT_PATH=""
for LOCATION in "${SCRIPT_LOCATIONS[@]}"; do
  if [ -f "$LOCATION" ]; then
    SCRIPT_FOUND=1
    SCRIPT_PATH="$LOCATION"
    echo "Found script at $SCRIPT_PATH"
    break
  fi
done

if [ $SCRIPT_FOUND -eq 0 ]; then
  echo "Could not find market-data-fix.js script. ConfigMap might not be mounted correctly."
  exit 1
fi

# Find the web root directories
WEB_ROOTS=(
  "/app/"
  "/app/public/"
  "/app/dist/"
  "/ui/"
  "/var/www/html/"
  "/usr/share/nginx/html/"
)

# Copy to web roots
COPIED=0
for ROOT in "${WEB_ROOTS[@]}"; do
  if [ -d "$ROOT" ]; then
    echo "Copying to $ROOT"
    cp "$SCRIPT_PATH" "${ROOT}market-data-fix.js"
    COPIED=1
  fi
done

if [ $COPIED -eq 0 ]; then
  echo "Could not find any web root directories"
  exit 1
fi

# Find index.html files
INDEX_FILES=(
  "/app/index.html"
  "/app/public/index.html"
  "/app/dist/index.html"
  "/ui/index.html"
  "/var/www/html/index.html"
  "/usr/share/nginx/html/index.html"
)

# Add script tag to index.html
MODIFIED=0
for INDEX_FILE in "${INDEX_FILES[@]}"; do
  if [ -f "$INDEX_FILE" ]; then
    echo "Found index.html at $INDEX_FILE"
    
    # Check if script is already included
    if grep -q "market-data-fix.js" "$INDEX_FILE"; then
      echo "market-data-fix.js is already included in $INDEX_FILE"
      continue
    fi
    
    # Make a backup
    cp "$INDEX_FILE" "${INDEX_FILE}.bak"
    
    # Find the script tag location
    if grep -q "</head>" "$INDEX_FILE"; then
      # Add the script right before </head>
      sed -i 's|</head>|<script src="/market-data-fix.js"></script>\n</head>|' "$INDEX_FILE"
      echo "Added market-data-fix.js to $INDEX_FILE before </head>"
      MODIFIED=1
    else
      # Try adding after the first script tag
      if grep -q "<script" "$INDEX_FILE"; then
        sed -i '/<script/a <script src="/market-data-fix.js"></script>' "$INDEX_FILE"
        echo "Added market-data-fix.js to $INDEX_FILE after first script tag"
        MODIFIED=1
      else
        # Last resort - add at the beginning of the file
        sed -i '1i <script src="/market-data-fix.js"></script>' "$INDEX_FILE"
        echo "Added market-data-fix.js to beginning of $INDEX_FILE"
        MODIFIED=1
      fi
    fi
  fi
done

if [ $MODIFIED -eq 0 ]; then
  echo "Could not find or modify any index.html file"
  
  # Try to find all HTML files and modify them
  echo "Searching for other HTML files..."
  HTML_FILES=$(find /app /ui /var/www/html /usr/share/nginx/html -name "*.html" 2>/dev/null || true)
  
  if [ -z "$HTML_FILES" ]; then
    echo "No HTML files found"
    exit 1
  fi
  
  for HTML_FILE in $HTML_FILES; do
    echo "Found HTML file: $HTML_FILE"
    
    # Check if script is already included
    if grep -q "market-data-fix.js" "$HTML_FILE"; then
      echo "market-data-fix.js is already included in $HTML_FILE"
      continue
    fi
    
    # Make a backup
    cp "$HTML_FILE" "${HTML_FILE}.bak"
    
    # Find the script tag location
    if grep -q "</head>" "$HTML_FILE"; then
      # Add the script right before </head>
      sed -i 's|</head>|<script src="/market-data-fix.js"></script>\n</head>|' "$HTML_FILE"
      echo "Added market-data-fix.js to $HTML_FILE before </head>"
      MODIFIED=1
    elif grep -q "<script" "$HTML_FILE"; then
      # Try adding after the first script tag
      sed -i '/<script/a <script src="/market-data-fix.js"></script>' "$HTML_FILE"
      echo "Added market-data-fix.js to $HTML_FILE after first script tag"
      MODIFIED=1
    fi
  done
fi

if [ $MODIFIED -eq 0 ]; then
  echo "Could not find or modify any HTML file"
  exit 1
fi

echo "WebSocket fix has been installed successfully"
EOF

chmod +x $TMP_SCRIPT

# Copy and execute the script in each pod
for POD in $UI_PODS; do
  echo "Processing $POD..."
  kubectl cp $TMP_SCRIPT $POD:/tmp/install_ws_fix.sh -n dev
  kubectl exec $POD -n dev -- bash /tmp/install_ws_fix.sh
  echo "Completed for $POD"
  echo "--------------------------------------"
done

# Clean up
rm $TMP_SCRIPT

echo "=== WebSocket fix applied to all UI pods ==="
echo "The WebSocket redirection should now work for free tier users"
