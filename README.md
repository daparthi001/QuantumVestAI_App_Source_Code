# QuantumVestAI Application Endpoints Documentation

This document provides a comprehensive list of API and UI endpoints for the QuantumVestAI application.
For screenshots and icons used in the interface, see [UI Visuals](docs/UI_IMAGES.md).

---

## **Authentication APIs**
- **POST** `/api/v1/auth/token` - Get access token with username/password
- **POST** `/api/v1/auth/login` - Login for UI clients
- **POST** `/api/v1/auth/register` - Register new user
- **POST** `/api/v1/auth/verify` - Verify JWT token validity
- **POST** `/api/v1/auth/logout` - Logout user
- **POST** `/api/v1/auth/password/change` - Change user password
- **POST** `/api/v1/auth/password/reset/request` - Request password reset
- **POST** `/api/v1/auth/password/reset/verify` - Verify password reset token
- **POST** `/api/v1/auth/password/reset/complete` - Complete password reset

---

## **User Management APIs**
- **GET** `/api/v1/users/me` - Get current user info
- **PUT** `/api/v1/users/me` - Update current user info
- **GET** `/api/v1/users/{user_id}` - Get user by ID
- **GET** `/api/v1/users/` - List all users (admin only)
- **PUT** `/api/v1/users/{user_id}/role` - Update user role (admin only)
- **PUT** `/api/v1/users/{user_id}/status` - Update user active status (admin only)
- **GET** `/api/v1/users/username/{username}` - Get user by username
- **POST** `/api/v1/users/regenerate-api-key` - Regenerate API key

---

## **Stock APIs**
- **GET** `/api/v1/stocks/search` - Search for stocks
- **GET** `/api/v1/stocks/{ticker}` - Get stock info
- **GET** `/api/v1/stocks/{ticker}/history` - Get stock price history
- **GET** `/api/v1/stocks/trending` - Get trending stocks
- **GET** `/api/v1/stocks/most-predictable` - Get most predictable stocks
- **GET** `/api/v1/stocks/sector/{sector}` - Get stocks by sector
- **GET** `/api/v1/stocks/industry/{industry}` - Get stocks by industry
- **GET** `/api/v1/stocks/markets/summary` - Get market summary

---

## **Forecast APIs**
- **GET** `/api/v1/forecast/{ticker}` - Get stock forecast
- **GET** `/api/v1/forecast/{ticker}/compare-models` - Compare forecast models
- **GET** `/api/v1/forecast/{ticker}/predictability` - Get stock predictability
- **GET** `/api/v1/forecast/{ticker}/backtest` - Backtest a forecast model
- **GET** `/api/v1/forecast/recommendations` - Get stock recommendations

---

## **Watchlist APIs**
- **GET** `/api/v1/watchlist/` - Get user's watchlist
- **POST** `/api/v1/watchlist/` - Add stock to watchlist
- **DELETE** `/api/v1/watchlist/{ticker}` - Remove stock from watchlist
- **PUT** `/api/v1/watchlist/{ticker}` - Update watchlist item
- **GET** `/api/v1/watchlist/performance` - Get watchlist performance

---

## **Admin APIs**
- **GET** `/api/v1/admin/stats` - Get system statistics
- **GET** `/api/v1/admin/users/stats` - Get user statistics
- **GET** `/api/v1/admin/forecasts/stats` - Get forecast statistics
- **GET** `/api/v1/admin/stocks/sync-status` - Get stock data sync status
- **POST** `/api/v1/admin/stocks/sync` - Trigger stock data sync
- **POST** `/api/v1/admin/model/retrain` - Retrain a forecast model
- **GET** `/api/v1/admin/logs` - Get system logs
- **GET** `/api/v1/admin/cache/stats` - Get cache statistics
- **POST** `/api/v1/admin/cache/clear` - Clear cache

---

## **Sentiment APIs**
- **GET** `/api/v1/sentiment/{ticker}` - Get sentiment for a stock
- **GET** `/api/v1/sentiment/compare` - Compare sentiment across stocks
- **GET** `/api/v1/sentiment/trending/topics` - Get trending sentiment topics
- **GET** `/api/v1/sentiment/market/mood` - Get overall market sentiment

---

## **Data APIs**
- **GET** `/api/v1/data/{ticker}` - Get processed stock data
- **GET** `/api/v1/data/{ticker}/predictability` - Get stock predictability analysis
- **GET** `/api/v1/data/{ticker}/technical-indicators` - Get technical indicators
- **GET** `/api/v1/data/sectors/performance` - Get sector performance
- **GET** `/api/v1/data/industries/performance` - Get industry performance

---
Feel free to reach out for further assistance or to report issues!
## Environment Setup
To create a virtual environment and install dependencies, run:
```bash
./setup_env.sh
```
Activate it with `source venv/bin/activate`.

## External API Key
To fetch real-time stock market data you must set the `ALPHA_VANTAGE_API_KEY`
environment variable. Sign up for a free key at
[Alpha Vantage](https://www.alphavantage.co/support/#api-key) and export it
before starting the API server:
```bash
export ALPHA_VANTAGE_API_KEY=your_key_here
```
Without this key the trending stock endpoints will not return current data.


