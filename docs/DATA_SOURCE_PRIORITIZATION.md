# Data Source Prioritization Guide

## Overview

This document explains the data source prioritization changes made to address Twitter API authorization limitations and prioritize premium data sources like Yahoo Finance and Alpha Vantage.

## Problem Addressed

The original issue was that Twitter API had only basic authorization while Yahoo Finance and Alpha Vantage provided premium access with better reliability. The system was showing latest data from Twitter despite these limitations.

## Changes Made

### 1. Configuration Options Added

Two new environment variables control data source behavior:

- `ENABLE_TWITTER_SENTIMENT=false` (default: disabled)
- `PRIORITIZE_PREMIUM_SOURCES=true` (default: enabled)

### 2. Data Source Weight Redistribution

**When Twitter is disabled (default):**
- News (Yahoo Finance): 55% weight
- Reddit: 30% weight  
- Fintech: 15% weight
- Twitter: 0% weight

**When Twitter is enabled with proper credentials:**
- News (Yahoo Finance): 40% weight (increased from 30%)
- Twitter: 25% weight (reduced from 40%)
- Reddit: 25% weight (increased from 20%)
- Fintech: 10% weight (same)

### 3. Enhanced Error Handling

- Graceful degradation when Twitter credentials are insufficient
- Clear logging when premium sources are prioritized
- Automatic fallback to Yahoo Finance for stock price data

### 4. Configuration Validation

- Twitter credentials are checked against the `ENABLE_TWITTER_SENTIMENT` setting
- System logs indicate when premium sources are being used instead of Twitter

## Benefits

1. **Reliable Data**: Yahoo Finance and Alpha Vantage provide consistent, high-quality financial data
2. **No API Limits**: Yahoo Finance doesn't require API keys for basic stock data
3. **Better Performance**: Reduces failed requests from Twitter API limitations
4. **Configurable**: Can enable Twitter when proper premium credentials are available

## Usage

### Default Configuration (Recommended)
```bash
# Use premium sources only
ENABLE_TWITTER_SENTIMENT=false
PRIORITIZE_PREMIUM_SOURCES=true
```

### With Twitter Premium Access
```bash
# Enable Twitter with proper credentials
ENABLE_TWITTER_SENTIMENT=true
TWITTER_BEARER_TOKEN=your_premium_twitter_token
# ... other Twitter credentials
```

## Files Modified

1. `ai-stock-platform/api/core/config/settings.py` - Added configuration options
2. `ai-stock-platform/api/social/multi_source_sentiment.py` - Updated weights and logic
3. `ai-stock-platform/api/twitter_config.py` - Enhanced credential validation
4. `ai-stock-platform/api/services/data_fetch_scheduler.py` - Improved logging
5. `ai-stock-platform/ui/core/config/settings.py` - UI configuration sync

## Testing

Run the validation test:
```bash
python test_data_source_priority.py
```

This confirms that:
- Twitter sentiment is disabled by default
- Premium sources are prioritized
- Configuration options work correctly
- System gracefully handles missing Twitter credentials

## Monitoring

The system logs will show:
- "Twitter sentiment disabled by configuration" when Twitter is disabled
- "Using premium data sources (Yahoo Finance, Alpha Vantage) - Twitter sentiment disabled"
- Source names in sentiment analysis results for transparency