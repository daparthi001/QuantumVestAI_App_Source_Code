#!/bin/bash
# Set up Alpha Vantage API key for QuantumVestAI application

# Default API key (free tier)
DEFAULT_API_KEY="ZS3BWXCFU22FINK5"

# Check if API key is provided as argument
if [ -n "$1" ]; then
    API_KEY="$1"
else
    # Use default key
    API_KEY=$DEFAULT_API_KEY
    echo "Using default Alpha Vantage API key (free tier with limited requests)."
    echo "For production use, get a key from https://www.alphavantage.co/ and run:"
    echo "  $0 YOUR_API_KEY"
fi

# Set the API key in the environment
export ALPHA_VANTAGE_API_KEY=$API_KEY
echo "ALPHA_VANTAGE_API_KEY has been set to: $API_KEY"

# Write to .env file if it exists
if [ -f "/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/.env" ]; then
    # Check if key already exists in .env file
    if grep -q "ALPHA_VANTAGE_API_KEY" "/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/.env"; then
        # Replace existing key
        sed -i '' "s/ALPHA_VANTAGE_API_KEY=.*/ALPHA_VANTAGE_API_KEY=$API_KEY/" "/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/.env"
    else
        # Add key to .env file
        echo "ALPHA_VANTAGE_API_KEY=$API_KEY" >> "/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/.env"
    fi
    echo "API key has been added to .env file."
else
    # Create .env file
    echo "ALPHA_VANTAGE_API_KEY=$API_KEY" > "/Users/gayatri/QuantumVestAI_App_Source_Code/ai-stock-platform/.env"
    echo "Created .env file with API key."
fi

echo ""
echo "To use the API key in the current shell session, run:"
echo "  source $0"

# Display current settings for trending stocks
echo ""
echo "Current settings for trending stocks service:"
echo "  - Cache TTL: ${CACHE_TTL_TRENDING_STOCKS:-300} seconds"
echo "  - Request Interval: ${ALPHA_VANTAGE_REQUEST_INTERVAL:-12} seconds"
echo ""
echo "You can adjust these settings by setting environment variables:"
echo "  export CACHE_TTL_TRENDING_STOCKS=600  # 10 minutes"
echo "  export ALPHA_VANTAGE_REQUEST_INTERVAL=15  # 15 seconds between requests"
