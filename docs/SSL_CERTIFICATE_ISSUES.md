# SSL Certificate Troubleshooting

This document provides information on how to troubleshoot SSL certificate verification issues when connecting to external financial APIs.

## Common SSL Certificate Issues

When connecting to external financial APIs like Alpha Vantage or Yahoo Finance, you might encounter SSL certificate verification errors. These typically occur in development environments, testing scenarios, or when there are proxy configurations or certificate issues with your network setup.

## Solution Options

### 1. Disable SSL Verification (Development Only)

For development environments only, you can disable SSL verification by setting the `DISABLE_SSL_VERIFY` environment variable:

```bash
export DISABLE_SSL_VERIFY=true
```

Then restart the application or API server.

**IMPORTANT**: This option is not recommended for production environments as it introduces security vulnerabilities. Only use it for development or testing.

### 2. Update Certificates (Recommended for Production)

For production environments, ensure your system's CA certificates are up-to-date:

- On Ubuntu/Debian: `sudo apt update && sudo apt install ca-certificates -y`
- On macOS: Ensure you have the latest OS updates
- On Windows: Ensure Windows updates are installed

### 3. Configure Proxy Settings

If you're behind a corporate proxy, you may need to configure proxy settings:

```bash
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### Testing the Fix

You can test if the fix works by running the included test script:

```bash
python test_trending_stocks_fixed.py
```

This script will test both the direct service and the API endpoint with SSL verification disabled.

### API Endpoints Affected

The following API endpoints are affected by this fix:

- **GET** `/api/v1/stocks/trending` - Get trending stocks
- **GET** `/api/v1/stocks/trending/cache/status` - Get trending stocks cache status
- **POST** `/api/v1/stocks/trending/cache/invalidate` - Invalidate trending stocks cache

## Implementation Details

The fix modifies the `TrendingStocksService` to conditionally disable SSL verification based on the `DISABLE_SSL_VERIFY` environment variable. It creates a custom SSL context when verification is disabled.
