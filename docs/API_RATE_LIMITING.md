# API Usage Restrictions and Rate Limiting

**Date**: August 4, 2025  
**Author**: GitHub Copilot  
**Project**: QuantumVestAI

## Overview

This document summarizes the restrictions and rate limiting measures implemented to ensure our API usage respects service limits and only uses live data. These changes ensure that Alpha Vantage, Yahoo Rapid API, and Twitter APIs are used efficiently without exceeding rate limits.

## Changes Made

### 1. Alpha Vantage API

- Removed demo fallback API key (`demo`) in `utils/market_data.py`
- Added validation to require a real API key, throwing an error if not present
- Implemented live API calls in `get_market_data()` function
- Set up proper error handling to expose errors rather than hiding them with fallback data

### 2. Yahoo Rapid API (Yahoo Finance)

- Increased cache TTL from 5 seconds to 60 seconds to reduce API calls
- Added rate limiting by implementing a minimum delay between requests (0.5 seconds)
- Added request time tracking to enforce proper spacing between API calls
- Changed behavior to throw an error when API key is missing instead of silently returning None

### 3. Twitter API

- Updated sentiment analysis to reduce data usage:
  - Reduced default time period from 7 days to 3 days
  - Reduced maximum tweets from 500 to 100
  - Implemented a hard limit of 100 tweets per request
  - Limited maximum API requests to 2 per analysis call
  - Reduced batch size from 100 to 50 tweets per request
  
- Added more restrictive search queries:
  - Added filter for verified accounts only (`is:verified`)
  - Added minimum engagement filter (`min_faves:10`)
  - Required hashtags (`has:hashtags`)
  - Excluded replies (`-is:reply`)

- Enhanced credential validation:
  - Updated `has_credentials()` method to require either a bearer token OR both API key and API secret
  - Made error messages more clear when credentials are missing

### 4. API Endpoints

- Updated API endpoints to reflect the new limits:
  - Changed Twitter sentiment endpoint to limit days to max 7 (default 3)
  - Set hard limit of 100 tweets for Twitter sentiment analysis
  - Exempted `/api/v1/auth/verify` from rate limiting to allow frequent token checks

## Best Practices

1. **Caching**: Implement caching for all API responses to minimize redundant calls
2. **Error Handling**: Expose errors to users rather than hiding them with fallback data
3. **Rate Limiting**: Respect API provider rate limits by implementing delays between calls
4. **Data Volume**: Minimize data volumes by limiting search periods and result counts
5. **API Keys**: Require valid API keys for all external services with proper validation

## Configuration Requirements

For the application to function properly, these environment variables must be set:

```
# Alpha Vantage API
ALPHA_VANTAGE_API_KEY=your_key_here

# Yahoo Finance API
RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=apidojo-yahoo-finance-v1.p.rapidapi.com

# Twitter API
TWITTER_API_KEY=your_key_here
TWITTER_API_SECRET=your_secret_here
TWITTER_BEARER_TOKEN=your_token_here  # Optional but recommended
```

## Monitoring Recommendations

1. Implement monitoring to track API rate limits and usage
2. Set up alerts for API failures or rate limit warnings
3. Monitor cache hit rates to ensure efficient API usage
