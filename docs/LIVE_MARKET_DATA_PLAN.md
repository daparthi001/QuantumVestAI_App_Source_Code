# Plan to Replace Mock Data with Live Market Data

This document describes the steps required to migrate from mock data to real-time market data in the application. Each step focuses on a specific aspect of the migration process.

## Step 1: Choose a Market Data API Provider

The first step is selecting a reliable data provider. Below is a comparison of common options:

| Provider | Free Tier | Data Offered | Notes |
|---------|-----------|-------------|------|
| **Alpha Vantage** | ✅ | Indices, stocks, forex | 5 API calls/min free |
| **IEX Cloud** | ✅ | US stock & index data | Better real-time data |
| **Finnhub** | ✅ | Stocks, indices, crypto | 60/min free |
| **Yahoo Finance** (via RapidAPI) | ✅ | Indices & company data | Slight delay |

When choosing a provider consider latency, data coverage, rate limits and pricing for higher tiers. The rest of this plan assumes at least one of these providers will be used to replace the current mock responses.
