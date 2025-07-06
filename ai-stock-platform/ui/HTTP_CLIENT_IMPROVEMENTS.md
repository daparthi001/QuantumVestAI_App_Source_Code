# HTTP Client Improvements for QuantumVestAI

This document describes the comprehensive improvements made to the HTTP client implementation in the QuantumVestAI application to address connection, timeout, error handling, and performance issues.

## Overview

The HTTP client has been completely revamped with a centralized, production-ready implementation that includes:

- Connection pooling and reuse
- Comprehensive retry mechanisms
- Proper timeout configurations
- SSL/TLS certificate handling
- Authentication and header management
- Performance optimizations
- Comprehensive error handling
- Async/sync compatibility

## Key Features

### 1. Connection Pooling and Performance
- **Connection Reuse**: HTTP connections are pooled and reused across requests
- **Configurable Limits**: Max connections (100) and keepalive connections (20) are configurable
- **Keep-Alive**: Connections are kept alive for 30 seconds by default
- **Resource Management**: Proper cleanup and lifecycle management

### 2. Timeout Configuration
- **Connect Timeout**: 5 seconds (configurable via `HTTPX_CONNECT_TIMEOUT`)
- **Read Timeout**: 30 seconds (configurable via `HTTPX_READ_TIMEOUT`)
- **Write Timeout**: 10 seconds (configurable via `HTTPX_WRITE_TIMEOUT`)
- **Pool Timeout**: 10 seconds (configurable via `HTTPX_POOL_TIMEOUT`)

### 3. Retry Mechanisms
- **Exponential Backoff**: Retry delays increase exponentially with jitter
- **Configurable Retries**: Up to 3 retries by default (configurable via `HTTPX_MAX_RETRIES`)
- **Smart Retry Logic**: Only retries on transient errors (network issues, 5xx, 429)
- **Rate Limit Handling**: Respects `Retry-After` headers for 429 responses

### 4. Error Handling
- **Comprehensive Exception Handling**: Covers all httpx exception types
- **Graceful Fallbacks**: Applications continue to work with fallback data
- **Detailed Logging**: All HTTP errors are logged with context
- **Non-Retryable Errors**: Client errors (4xx) are not retried

### 5. Authentication and Headers
- **Bearer Token Support**: Automatic `Authorization` header management
- **Default Headers**: User-Agent, Accept, Content-Type set automatically
- **Custom Headers**: Support for additional headers per request
- **API Key Management**: Secure token handling

### 6. SSL/TLS Configuration
- **Certificate Verification**: Enabled by default (configurable via `HTTPX_VERIFY_SSL`)
- **Secure Connections**: Proper SSL/TLS handling for HTTPS
- **Certificate Pinning**: Ready for certificate pinning if needed

## Usage

### Basic Usage

```python
from core.http_client import get_http_client, safe_get_json, safe_post_json

# Using the global client (recommended)
async with get_http_client() as client:
    response = await client.get(
        url="https://api.example.com/data",
        auth_token="your_token_here"
    )

# Using utility functions with fallback
data = await safe_get_json(
    url="https://api.example.com/data",
    auth_token="your_token_here",
    default={"error": "fallback_data"}
)
```

### Advanced Usage

```python
from core.http_client import HTTPClient, HTTPClientConfig

# Custom configuration
config = HTTPClientConfig()
config.max_retries = 5
config.timeout.read = 60.0

# Create custom client
async with HTTPClient(config) as client:
    response = await client.post(
        url="https://api.example.com/data",
        json={"key": "value"},
        auth_token="your_token_here"
    )
```

## Configuration

All HTTP client behavior can be configured via environment variables:

### Connection Settings
```bash
HTTPX_CONNECT_TIMEOUT=5.0      # Connection timeout in seconds
HTTPX_READ_TIMEOUT=30.0        # Read timeout in seconds
HTTPX_WRITE_TIMEOUT=10.0       # Write timeout in seconds
HTTPX_POOL_TIMEOUT=10.0        # Pool timeout in seconds
```

### Connection Pool Settings
```bash
HTTPX_MAX_KEEPALIVE=20         # Max keepalive connections
HTTPX_MAX_CONNECTIONS=100      # Max total connections
HTTPX_KEEPALIVE_EXPIRY=30.0    # Keepalive expiry in seconds
```

### Retry Settings
```bash
HTTPX_MAX_RETRIES=3            # Maximum retry attempts
HTTPX_RETRY_DELAY_BASE=1.0     # Base retry delay in seconds
HTTPX_RETRY_DELAY_MAX=60.0     # Maximum retry delay in seconds
```

### Security Settings
```bash
HTTPX_VERIFY_SSL=true          # Enable SSL certificate verification
```

## Migration Guide

### Before (Old Implementation)
```python
async with httpx.AsyncClient() as client:
    response = await client.get(
        url="https://api.example.com/data",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5.0
    )
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code)
    
    return response.json()
```

### After (New Implementation)
```python
# Option 1: Using utility function (recommended)
data = await safe_get_json(
    url="https://api.example.com/data",
    auth_token=token,
    default={}
)

# Option 2: Using client directly
async with get_http_client() as client:
    response = await client.get(
        url="https://api.example.com/data",
        auth_token=token
    )
    response.raise_for_status()
    return response.json()
```

## Files Updated

### New Files
- `core/http_client.py` - Centralized HTTP client implementation
- `tests/test_http_client.py` - Comprehensive test suite
- `test_integration.py` - Integration tests

### Updated Files
- `auth/dependencies.py` - Updated to use new HTTP client
- `controllers/market_controller.py` - Updated to use new HTTP client
- `controllers/dashboard_controller.py` - Updated to use new HTTP client
- `routes/auth.py` - Updated to use new HTTP client
- `templates/auth/dependencies.py` - Updated to use new HTTP client
- `requirements.txt` - Updated httpx version
- `.env.example` - Added HTTP client configuration

## Testing

### Run Integration Tests
```bash
cd ai-stock-platform/ui
python test_integration.py
```

### Run Unit Tests
```bash
cd ai-stock-platform/ui
python -m pytest tests/test_http_client.py -v
```

## Performance Improvements

### Before
- New HTTP client instance for each request
- No connection pooling
- Basic timeout handling
- Limited error handling
- No retry mechanisms

### After
- Shared HTTP client with connection pooling
- Configurable connection limits and timeouts
- Comprehensive error handling and logging
- Intelligent retry mechanisms with exponential backoff
- SSL/TLS optimization
- Resource cleanup and lifecycle management

## Monitoring and Debugging

### Logging
All HTTP requests and errors are logged with appropriate levels:
- `DEBUG`: Connection pool status, cache hits/misses
- `INFO`: Successful requests, fallback usage
- `WARNING`: Retry attempts, rate limiting
- `ERROR`: Request failures, authentication issues

### Metrics
The HTTP client provides timing information for performance monitoring:
- Request/response times
- Retry attempts
- Connection pool usage
- Error rates

## Best Practices

1. **Use the Global Client**: Use `get_http_client()` for most use cases
2. **Use Utility Functions**: Use `safe_get_json()` and `safe_post_json()` for simple requests
3. **Handle Fallbacks**: Always provide fallback data for non-critical requests
4. **Configure Timeouts**: Set appropriate timeouts for your use case
5. **Monitor Logs**: Watch HTTP client logs for performance issues
6. **Test Error Conditions**: Test your application with network failures

## Troubleshooting

### Common Issues

1. **Connection Timeouts**
   - Increase `HTTPX_CONNECT_TIMEOUT`
   - Check network connectivity
   - Verify target service availability

2. **Read Timeouts**
   - Increase `HTTPX_READ_TIMEOUT`
   - Check if API responses are slow
   - Consider implementing request pagination

3. **Too Many Retries**
   - Check API service health
   - Verify authentication tokens
   - Review retry configuration

4. **SSL/TLS Issues**
   - Set `HTTPX_VERIFY_SSL=false` for development (not recommended for production)
   - Check certificate validity
   - Update CA certificates

### Debug Mode
Enable debug logging to see detailed HTTP client activity:
```bash
LOG_LEVEL=debug
DEBUG=true
```

## Security Considerations

1. **SSL/TLS Verification**: Always enabled in production
2. **Token Management**: Secure storage and transmission of auth tokens
3. **Header Sanitization**: Automatic sanitization of sensitive headers in logs
4. **Certificate Pinning**: Ready for implementation if required

## Future Enhancements

1. **Request/Response Middleware**: Add hooks for request/response processing
2. **Circuit Breaker**: Implement circuit breaker pattern for failing services
3. **Metrics Collection**: Integrate with Prometheus or similar monitoring systems
4. **Request Tracing**: Add distributed tracing support
5. **Caching Layer**: Implement HTTP response caching