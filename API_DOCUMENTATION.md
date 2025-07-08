# QuantumVestAI API Documentation

This directory contains comprehensive API documentation for the QuantumVestAI platform in OpenAPI 3.0 format.

## Files

- **swagger.yaml** - Complete OpenAPI 3.0 specification in YAML format
- **swagger.json** - Complete OpenAPI 3.0 specification in JSON format
- **API_DOCUMENTATION.md** - This documentation file

## API Overview

The QuantumVestAI API provides comprehensive access to AI-powered stock market analysis, forecasting, and portfolio management features.

### Base URLs

- **Development**: `https://dev.quantumvestai.com`
- **Production**: `https://api.quantumvestai.com`
- **Local Development**: `http://localhost:5000`

### Authentication

The API uses JWT Bearer token authentication. To authenticate:

1. Use the `/api/v1/auth/login` endpoint with your credentials
2. Include the returned token in the Authorization header: `Authorization: Bearer <token>`

### API Categories

#### 🔐 Authentication & User Management
- User registration, login, and password management
- JWT token validation and refresh
- User profile management
- API key generation

#### 📈 Stock Data & Market Information
- Real-time and historical stock data
- Market summaries and sector analysis
- Stock search and filtering
- Trending stocks identification

#### 🤖 AI-Powered Forecasting
- Machine learning stock price predictions
- Multiple forecast models (LSTM, Transformer, Ensemble, ARIMA)
- Model comparison and backtesting
- Stock predictability analysis

#### 📋 Watchlist Management
- Personal stock watchlists
- Performance tracking
- Price alerts and notifications

#### 💭 Sentiment Analysis
- Social media sentiment analysis
- Twitter integration for stock sentiment
- Market mood indicators
- Trending topics analysis

#### 🛠 Administrative Tools
- System statistics and monitoring
- User management (admin only)
- Cache management
- Data synchronization

#### 📊 Data Analytics
- Technical indicators
- Sector and industry performance
- Advanced data processing
- Custom analytics

#### 🐦 Social Media Integration
- Twitter API integration
- Real-time social sentiment
- Trending stocks on social media
- Social media health monitoring

## Key Features

### 🎯 AI-Powered Predictions
- Advanced machine learning models for stock forecasting
- Ensemble models combining multiple approaches
- Confidence intervals and predictability scores
- Historical backtesting capabilities

### 📊 Comprehensive Market Data
- Real-time stock prices and market data
- Historical data with flexible time periods
- Sector and industry analysis
- Market summaries and key indicators

### 🔍 Smart Analytics
- Technical indicator calculations
- Sentiment analysis from social media
- Trend detection and pattern recognition
- Risk assessment and recommendations

### 🚀 High Performance
- Rate limiting to ensure fair usage
- Caching for optimal performance
- Comprehensive error handling
- Standardized response formats

## Rate Limiting

API requests are rate-limited based on user type:

- **Standard users**: 100 requests per minute
- **Premium users**: 1000 requests per minute  
- **Admin users**: Unlimited

## Response Format

All API responses follow a standardized format:

```json
{
  "status": "success|error",
  "data": {...},
  "message": "Optional message",
  "timestamp": "2025-01-09T10:30:00Z",
  "request_id": "req_123456789"
}
```

## Error Handling

The API uses standard HTTP status codes and provides detailed error messages:

- **200**: Success
- **201**: Created
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **429**: Rate Limit Exceeded
- **500**: Internal Server Error

## Using the Documentation

### Swagger UI
You can use the swagger.yaml or swagger.json files with Swagger UI to get an interactive API explorer:

1. Go to [Swagger Editor](https://editor.swagger.io/)
2. Import the swagger.yaml file
3. Explore the API interactively

### Postman
Import the swagger.json file into Postman to create a complete collection of API endpoints.

### Code Generation
Use the OpenAPI specification to generate client libraries in your preferred programming language using tools like:
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger Codegen](https://swagger.io/tools/swagger-codegen/)

## Example Usage

### Authentication
```bash
# Login
curl -X POST "https://dev.quantumvestai.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=password"

# Use the returned token
curl -X GET "https://dev.quantumvestai.com/api/v1/stocks/AAPL" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Stock Forecast
```bash
curl -X GET "https://dev.quantumvestai.com/api/v1/forecast/AAPL?horizon=30&model=ensemble" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Twitter Sentiment Analysis
```bash
curl -X GET "https://dev.quantumvestai.com/api/social/twitter/sentiment/AAPL?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Support

For additional support:

1. Review the detailed API specification in swagger.yaml
2. Check the application logs for error details
3. Use the health check endpoints to diagnose issues
4. Contact support with specific error messages and timestamps

## Development

### Local Testing
To test the API locally:

1. Start the QuantumVestAI API server
2. Use the local base URL: `http://localhost:5000`
3. Access the interactive docs at: `http://localhost:5000/docs`

### Validation
The OpenAPI specification has been validated for:
- ✅ Valid YAML/JSON syntax
- ✅ OpenAPI 3.0 compliance
- ✅ Complete endpoint coverage
- ✅ Proper schema definitions
- ✅ Authentication flows
- ✅ Error response handling

---

**QuantumVestAI** - Powering intelligent investment decisions with AI