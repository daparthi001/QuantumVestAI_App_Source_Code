Models Directory (models/)
The models directory contains all the AI/ML model implementations used in your QuantumVestAI system. Here's a breakdown of each file and its purpose:
1. __init__.py

Purpose: Makes the directory a proper Python package
Content: Empty file (or with minimal imports)
Usage: Allows importing from the package using from models import ...

2. lstm_model.py

Purpose: Implements a Long Short-Term Memory (LSTM) neural network model
Key Function: run_lstm()
Features:

Uses TensorFlow/Keras to build a deep learning model
Scales input data using MinMaxScaler
Creates sequence data for time series prediction
Builds a stacked LSTM architecture with dropout layers for regularization
Forecasts future prices based on historical patterns
Handles different column name conventions (close/Close)



3. prophet_model.py

Purpose: Implements Facebook's Prophet time series forecasting model
Key Function: run_prophet()
Features:

Specialized for time series data with seasonality
Handles holidays and special events automatically
Produces confidence intervals for predictions
Returns forecast with upper and lower bounds
Adapts to different data formats



4. xgboost_model.py

Purpose: Implements XGBoost gradient boosting model for regression
Key Function: run_xgboost()
Features:

Uses percentage returns rather than raw prices
Handles feature engineering automatically
Predicts price changes using multiple features (open, high, low, close, volume)
Converts predicted returns back to price predictions
Standardizes column names for consistent processing



5. finbert_sentiment.py

Purpose: Provides sentiment analysis for financial texts
Key Function: get_finbert_sentiment()
Features:

Uses Hugging Face's transformers library
Employs the FinBERT model (financial domain-specific BERT)
Classifies sentiment as positive, neutral, or negative
Returns confidence scores for each sentiment class
Handles various response formats and error conditions



6. pipeline.py

Purpose: Implements an ensemble model combining multiple predictions
Key Function: run_ensemble()
Features:

Combines LSTM and Prophet predictions
Standardizes data formats between models
Uses simple averaging for ensemble prediction
Returns a comprehensive DataFrame with predictions from all models
Provides component model predictions for comparison



Key Technical Details:

Data Preprocessing:

All models handle data format standardization
Column name normalization (e.g., 'Close' vs 'close')
Date formatting and sequence preparation


Model Architectures:

LSTM: Two stacked LSTM layers with dropout
Prophet: Additive model with trend and seasonality components
XGBoost: Gradient boosting trees for regression


Prediction Format:

All models return predictions in a standardized format
Prophet and ensemble models return DataFrame with 'ds' (date) and 'yhat' (prediction) columns
LSTM returns a numpy array that gets converted to match the other formats


Error Handling:

All models have robust error handling
Clear error messages for missing data or columns
Graceful fallbacks for sentiment analysis



This modular design allows for easy extension with new models and enables the ensemble approach to combine predictions from different algorithms for improved accuracy.RetryGroutes directoryEditRoutes Directory (routes/)
The routes directory contains all the API endpoints and web routes for the QuantumVestAI system. Let me explain each file in detail:
1. __init__.py

Purpose: Makes the directory a proper Python package
Content: Empty file with optional imports
Usage: Allows importing routes using from routes import ...

2. admin.py

Purpose: Handles administration routes and dashboard
Key Endpoints:

GET /admin/ or GET /admin/dashboard: Renders the admin dashboard
GET /admin/health: Health check endpoint
GET /admin/list: Lists all admins (requires API key)
GET /admin/models: Lists model information (requires API key)
GET /admin/{username}: Gets specific admin information
POST /admin/add: Adds a new admin
DELETE /admin/remove/{username}: Removes an admin
POST /admin/retrain: Triggers model retraining


Key Features:

Authentication via API key
User management functionality
Model metadata management and display
Manual model retraining mechanism
Data persistence using JSON files



3. auth.py

Purpose: Handles user authentication and session management
Key Endpoints:

GET /login: Renders login form
POST /login: Processes login attempts
GET /register: Renders registration form
POST /register: Processes user registration
GET /logout: Handles user logout


Key Features:

Secure password hashing with bcrypt
JWT token-based authentication
Token expiration and validation
User session management via cookies
User lookup and verification functions



4. sentiment.py

Purpose: Provides sentiment analysis for stocks and financial text
Key Endpoints:

GET /sentiment/analyze: Analyzes sentiment of provided text
GET /sentiment/ticker: Analyzes social media sentiment for a ticker
GET /sentiment/analysis: Gets analyst recommendations and valuation metrics


Key Features:

Integration with Twitter API for social sentiment
FinBERT model for financial text analysis
Yahoo Finance data for analyst recommendations
Error handling for API failures
Lazy loading of models to save memory



5. webapi.py

Purpose: Core API for stock forecasting functionality
Key Endpoints:

POST /api/forecast: Generates price forecast (JSON response)
GET /forecast: Renders forecast page with visualization


Key Features:

Model selection (ensemble, prophet, xgboost, lstm)
Historical data download via yfinance
Forecast generation with various time horizons
Sentiment integration with forecast results
HTML rendering with chart visualization
User authentication integration



6. whitepaper_analysis.py

Purpose: Provides company summary and analysis functions
Key Endpoints:

GET /whitepaper/summarize: Summarizes company information from various sources


Key Features:

Retrieves company descriptions from Yahoo Finance
Scrapes SEC filings for additional information
Uses transformer-based summarization models
Text truncation for model compatibility
Source attribution in responses



Technical Implementation Details:
1. FastAPI Integration

All routes use FastAPI's dependency injection system
Type hints with Pydantic models for request validation
Path, query, and form parameters appropriately typed
Response models and status codes properly defined

2. Template Rendering

HTML responses use Jinja2 templates
Template context includes user data when available
Error handling with appropriate templates

3. Authentication Flow

Token-based authentication with JWT
Cookie storage for session persistence
Dependency-based current user retrieval
Authorization checks in protected routes

4. Data Sources

Financial data from Yahoo Finance
Social sentiment from Twitter API
Company information from SEC filings
User and model data from local JSON files

5. Error Handling

Structured exception handling with HTTP error codes
Graceful fallbacks for API failures
Informative error messages for debugging
User-friendly error presentations

The routes directory implements a complete RESTful API structure combined with server-side rendering for the web interface, providing both programmatic access and a user-friendly interface to the same underlying functionality.