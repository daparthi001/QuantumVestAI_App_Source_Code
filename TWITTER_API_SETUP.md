# Twitter API Integration Setup

This guide explains how to set up and configure the Twitter API integration for real-time social sentiment analysis in the QuantumVestAI application.

If you do not have a paid Twitter plan or prefer free alternatives, see
[Stock Sentiment Workarounds](docs/SENTIMENT_WORKAROUNDS.md) for ways to gather
sentiment data without official API access.

## Overview

The Twitter integration provides:
- Real-time sentiment analysis for stock symbols
- Trending stocks analysis based on Twitter activity
- Social media insights for investment decisions
- Automatic rate limiting and error handling

## Features

### 1. Sentiment Analysis
- Analyzes tweets mentioning specific stock symbols ($AAPL, $TSLA, etc.)
- Calculates sentiment scores using TextBlob NLP
- Provides daily sentiment trends
- Identifies top mentions with engagement metrics

### 2. Trending Stocks
- Tracks stocks with high Twitter activity
- Measures engagement and volume changes
- Provides sentiment-based recommendations

### 3. Error Handling
- Graceful fallback to demo data when API is not configured
- Rate limiting compliance
- Comprehensive error messages and logging

## Setup Instructions

### Prerequisites

1. **Twitter Developer Account**
   - Apply for a Twitter Developer account at https://developer.twitter.com
   - Create a new Twitter App
   - Generate API keys and tokens

2. **Required Permissions**
   - Read access to tweets
   - Access to Twitter API v2

### API Credentials

You need the following credentials from your Twitter Developer Dashboard:

```bash
# Twitter API Credentials
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### Environment Configuration

#### For Development (Local)

1. Create a `.env` file in the `ai-stock-platform/api/` directory:

```bash
# Twitter API Configuration
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAMLheAAAAAAA0%2BuSeid%2BULvsea4JtiGRiSDSJSI%3DEUifiRBkKG5E2XzMDjRfl76ZC9Ub0wnz4XsNiRVBChTYbJcE3F
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

2. Restart the API server to load the new configuration.

#### For Production (Kubernetes)

1. Add your Twitter credentials to `ci-cd/k8s/all-secrets.yaml` and apply the
   file. This consolidated manifest stores all application secrets in one place:

```bash
kubectl apply -f ci-cd/k8s/all-secrets.yaml
```

2. If you prefer to create a standalone secret you can still run:

```bash
kubectl create secret generic twitter-secrets \
  --from-literal=TWITTER_BEARER_TOKEN="your_bearer_token" \
  --from-literal=TWITTER_API_KEY="your_api_key" \
  --from-literal=TWITTER_API_SECRET="your_api_secret" \
  --from-literal=TWITTER_ACCESS_TOKEN="your_access_token" \
  --from-literal=TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
```

### Verification

To verify your Twitter API integration is working:

1. **Health Check Endpoint**
   ```bash
   curl http://quantumvestai-dev-api.dev.svc.cluster.local:8000/api/social/twitter/health
   ```

2. **Test Sentiment Analysis**
   ```bash
   curl http://quantumvestai-dev-api.dev.svc.cluster.local:8000/api/social/twitter/sentiment/AAPL
   ```

3. **Test Trending Stocks**
   ```bash
   curl http://quantumvestai-dev-api.dev.svc.cluster.local:8000/api/social/twitter/trending
   ```

## API Endpoints

### GET /api/social/twitter/sentiment/{symbol}

Analyze Twitter sentiment for a specific stock symbol.

**Parameters:**
- `symbol` (path): Stock symbol (e.g., AAPL, TSLA)
- `days` (query): Number of days to analyze (default: 7, max: 30)
- `max_tweets` (query): Maximum tweets to analyze (default: 500, max: 1000)

**Response:**
```json
{
  "status": "success",
  "data": {
    "symbol": "AAPL",
    "date": "2025-01-09",
    "sentiment_score": 0.15,
    "sentiment_label": "positive",
    "volume": 1250,
    "trending_score": 143.75,
    "sources": {
      "twitter": 1250,
      "reddit": 0,
      "news": 0,
      "other": 0
    },
    "top_mentions": [...],
    "daily_sentiment": [...]
  }
}
```

### GET /api/social/twitter/trending

Get trending stocks based on Twitter activity.

**Parameters:**
- `limit` (query): Number of trending stocks to return (default: 10, max: 50)

**Response:**
```json
{
  "status": "success",
  "data": {
    "trending_tickers": [
      {
        "ticker": "AAPL",
        "tweet_count": 1250,
        "engagement": 15000,
        "sentiment": 0.15,
        "volume_change": 0.08
      }
    ],
    "count": 10,
    "last_updated": "2025-01-09T10:30:00Z"
  }
}
```

### GET /api/social/twitter/health

Check Twitter API health and configuration status.

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "healthy",
    "configuration": {
      "bearer_token": true,
      "api_key": true,
      "api_secret": true,
      "access_token": true,
      "access_token_secret": true
    },
    "api_status": "available",
    "last_checked": "2025-01-09T10:30:00Z"
  }
}
```

## Rate Limiting

The Twitter API has rate limits that are automatically handled by the integration:

- **Search Tweets**: 300 requests per 15-minute window
- **Recent Search**: 450 requests per 15-minute window

The system includes:
- Automatic rate limit handling with wait times
- Request caching to minimize API calls
- Graceful degradation when limits are exceeded

## Error Handling

The integration handles various error scenarios:

### Configuration Errors
- Missing API credentials → Falls back to demo data
- Invalid credentials → Returns configuration error

### API Errors
- Rate limiting → Automatic retry with backoff
- Network issues → Cached data or graceful fallback
- Invalid queries → Validation error responses

### Client Errors
- 401 Unauthorized → Check API credentials
- 403 Forbidden → Check API permissions
- 429 Rate Limited → Automatic handling
- 503 Service Unavailable → Twitter API issues

## Demo Mode

When Twitter API credentials are not configured, the system automatically runs in demo mode:

- Returns realistic sample data
- Maintains all API response structures
- Includes clear indicators that demo data is being used
- Allows testing of UI components without API access

## Troubleshooting

### Common Issues

1. **"Twitter API credentials not configured"**
   - Verify environment variables are set correctly
   - Check that credentials are loaded at startup
   - Ensure secrets are properly mounted in Kubernetes

2. **"Twitter API credentials are invalid"**
   - Verify credentials in Twitter Developer Dashboard
   - Check for typos in environment variables
   - Ensure API keys haven't expired

3. **"Twitter API rate limit exceeded"**
   - Wait for rate limit reset (15 minutes)
   - Reduce query frequency
   - Check if multiple instances are using same credentials

4. **"No tweets found"**
   - Stock symbol might not be discussed on Twitter
   - Try different time ranges
   - Check if symbol format is correct ($SYMBOL)

### Debug Mode

Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

This provides detailed information about:
- API requests and responses
- Rate limiting status
- Error details and stack traces

## Best Practices

### Security
- Never commit API credentials to version control
- Use environment variables or secrets management
- Rotate credentials regularly
- Monitor API usage and costs

### Performance
- Use caching to minimize API calls
- Implement exponential backoff for retries
- Monitor rate limit usage
- Use pagination for large data sets

### Data Quality
- Filter out retweets for original content
- Use context annotations to improve relevance
- Implement spam and bot detection
- Validate stock symbols before querying

## Support

For additional support:

1. Check the [Twitter API Documentation](https://developer.twitter.com/en/docs)
2. Review application logs for error details
3. Use the health check endpoint to diagnose issues
4. Contact support with specific error messages and timestamps