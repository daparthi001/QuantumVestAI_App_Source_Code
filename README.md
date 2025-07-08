# QuantumVestAI Application Endpoints Documentation

This document provides a comprehensive list of API and UI endpoints for the QuantumVestAI application.

---

## **Authentication APIs**
- **POST** `/api/auth/token` - Get access token with username/password
- **POST** `/api/auth/login` - Login for UI clients
- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/verify` - Verify JWT token validity
- **POST** `/api/auth/logout` - Logout user
- **POST** `/api/auth/password/change` - Change user password
- **POST** `/api/auth/password/reset/request` - Request password reset
- **POST** `/api/auth/password/reset/verify` - Verify password reset token
- **POST** `/api/auth/password/reset/complete` - Complete password reset

---

## **User Management APIs**
- **GET** `/api/users/me` - Get current user info
- **PUT** `/api/users/me` - Update current user info
- **GET** `/api/users/{user_id}` - Get user by ID
- **GET** `/api/users/` - List all users (admin only)
- **PUT** `/api/users/{user_id}/role` - Update user role (admin only)
- **PUT** `/api/users/{user_id}/status` - Update user active status (admin only)
- **GET** `/api/users/username/{username}` - Get user by username
- **POST** `/api/users/regenerate-api-key` - Regenerate API key

---

## **Stock APIs**
- **GET** `/api/stocks/search` - Search for stocks
- **GET** `/api/stocks/{ticker}` - Get stock info
- **GET** `/api/stocks/{ticker}/history` - Get stock price history
- **GET** `/api/stocks/trending` - Get trending stocks
- **GET** `/api/stocks/most-predictable` - Get most predictable stocks
- **GET** `/api/stocks/sector/{sector}` - Get stocks by sector
- **GET** `/api/stocks/industry/{industry}` - Get stocks by industry
- **GET** `/api/stocks/markets/summary` - Get market summary

---

## **Forecast APIs**
- **GET** `/api/forecast/{ticker}` - Get stock forecast
- **GET** `/api/forecast/{ticker}/compare-models` - Compare forecast models
- **GET** `/api/forecast/{ticker}/predictability` - Get stock predictability
- **GET** `/api/forecast/{ticker}/backtest` - Backtest a forecast model
- **GET** `/api/forecast/recommendations` - Get stock recommendations

---

## **Watchlist APIs**
- **GET** `/api/watchlist/` - Get user's watchlist
- **POST** `/api/watchlist/` - Add stock to watchlist
- **DELETE** `/api/watchlist/{ticker}` - Remove stock from watchlist
- **PUT** `/api/watchlist/{ticker}` - Update watchlist item
- **GET** `/api/watchlist/performance` - Get watchlist performance

---

## **Admin APIs**
- **GET** `/api/admin/stats` - Get system statistics
- **GET** `/api/admin/users/stats` - Get user statistics
- **GET** `/api/admin/forecasts/stats` - Get forecast statistics
- **GET** `/api/admin/stocks/sync-status` - Get stock data sync status
- **POST** `/api/admin/stocks/sync` - Trigger stock data sync
- **POST** `/api/admin/model/retrain` - Retrain a forecast model
- **GET** `/api/admin/logs` - Get system logs
- **GET** `/api/admin/cache/stats` - Get cache statistics
- **POST** `/api/admin/cache/clear` - Clear cache

---

## **Sentiment APIs**
- **GET** `/api/sentiment/{ticker}` - Get sentiment for a stock
- **GET** `/api/sentiment/compare` - Compare sentiment across stocks
- **GET** `/api/sentiment/trending/topics` - Get trending sentiment topics
- **GET** `/api/sentiment/market/mood` - Get overall market sentiment

---

## **Data APIs**
- **GET** `/api/data/{ticker}` - Get processed stock data
- **GET** `/api/data/{ticker}/predictability` - Get stock predictability analysis
- **GET** `/api/data/{ticker}/technical-indicators` - Get technical indicators
- **GET** `/api/data/sectors/performance` - Get sector performance
- **GET** `/api/data/industries/performance` - Get industry performance

---

Feel free to reach out for further assistance or to report issues!