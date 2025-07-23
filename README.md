# QuantumVestAI Application Endpoints Documentation

This document provides a comprehensive list of API and UI endpoints for the QuantumVestAI application.
For screenshots and icons used in the interface, see [UI Visuals](docs/UI_IMAGES.md).
For instructions on integrating ChatGPT into the UI, see [ChatGPT Guide](docs/CHATGPT_UI_INTEGRATION.md).

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
After activating, add the API package to your `PYTHONPATH` so tools like
Alembic can locate the `api` module when run from outside the repository root:
```bash
export PYTHONPATH="$(pwd)/ai-stock-platform:$PYTHONPATH"
```

> **Important**: Ensure that the top-level `ai-stock-platform` directory is
> listed **before** the `ai-stock-platform/api` directory in your
> `PYTHONPATH`. If the API folder appears first, imports such as
> `from core.config import get_settings` may resolve to the legacy
> `api/core/config` module which does not expose `get_settings` and results in
> the `ImportError: cannot import name 'get_settings'` error. A safe ordering is:
> ```bash
> export PYTHONPATH="$(pwd)/ai-stock-platform:$(pwd)/app/core:$PYTHONPATH"
> ```
> This guarantees that the shared `core` package is used for configuration.

## External API Key
To fetch real-time stock market data you must set the `ALPHA_VANTAGE_API_KEY`
environment variable. Sign up for a free key at
[Alpha Vantage](https://www.alphavantage.co/support/#api-key) and export it
before starting the API server. If the variable is not set the application will
fall back to the public **demo** key which has strict rate limits:
```bash
export ALPHA_VANTAGE_API_KEY=your_key_here
```
Without this key the trending stock endpoints will not return current data.

## Database Setup

The API uses asynchronous SQLAlchemy connections. Before running the server you must
configure two environment variables:

```bash
export ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
export RUN_DB_MIGRATIONS=true
```

`ASYNC_DATABASE_URL` provides the connection string for the async engine. If it is
not set, the API looks for `DATABASE_URL` instead and falls back to a local SQLite
file (`test.db`). `RUN_DB_MIGRATIONS` controls whether the application automatically
creates tables on startup. The migration script now also checks both variables, so
either can be used when deploying to environments such as Amazon RDS.

Alternatively you can supply individual connection parameters using the
environment variables `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` and
`DB_PASSWORD`. The API assembles the connection URL from these values when
`DATABASE_URL` or `ASYNC_DATABASE_URL` is not defined. A variable named
`DB_URL` is **not** used.

For local development you can initialize a PostgreSQL database by running:

```bash
./app/core/scripts/init_local_db.sh
```

If the tables are missing at startup, the API will attempt to create them
automatically.

### Docker Environment Files
Both the API and UI containers load environment variables from files matching
their runtime environment. When the container starts it looks for a file named
`.env.<environment>` inside the respective directory and applies those values.
Set `API_ENV` for the API image or `ENV` for the UI image to select which file
should be used (for example `API_ENV=production`).

Sensitive values like `SECRET_KEY` should not be stored in these files for
production deployments. Instead, create a Kubernetes `Secret` and mount it as an
environment variable or file. Both the API and UI startup scripts will read a
`SECRET_KEY_FILE` path if provided to load the key securely.


\n
