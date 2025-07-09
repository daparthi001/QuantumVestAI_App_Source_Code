"""
Pytest configuration and fixtures for QuantumVestAI UI tests.
"""
import os
import sys
import pytest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
# Ensure ai-stock-platform packages are discoverable
sys.path.append(os.path.join(ROOT, "ai-stock-platform"))
sys.path.append(os.path.join(ROOT, "ai-stock-platform", "api"))

pytest.importorskip("httpx")
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from ui.main import app as ui_app
from ui.services.api_client import APIClient
from core.config.settings import settings

@pytest.fixture
def app() -> FastAPI:
    """
    Fixture that returns the FastAPI app instance for testing.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    return ui_app

@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """
    Fixture that creates a test client for sending test requests.
    
    Args:
        app: FastAPI application
        
    Returns:
        TestClient: The configured test client
    """
    return TestClient(app)

@pytest.fixture
def mock_api_client():
    """
    Fixture that provides a mocked API client.
    
    Returns:
        MagicMock: Mocked API client
    """
    with patch('ui.services.api_client.APIClient') as mock:
        mock_client = MagicMock(spec=APIClient)
        yield mock_client

@pytest.fixture
def auth_token():
    """
    Fixture that provides a sample auth token for testing.
    
    Returns:
        str: A sample auth token
    """
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0dXNlciIsInJvbGUiOiJiYXNpYyIsImV4cCI6MTcxNjU5MjM0NX0.abc123"

@pytest.fixture
def auth_headers(auth_token):
    """
    Fixture that provides headers with authentication.
    
    Args:
        auth_token: JWT token for authentication
        
    Returns:
        dict: Headers with authentication
    """
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_user():
    """
    Fixture that provides test user data.
    
    Returns:
        dict: Test user information
    """
    return {
        "id": 123,
        "username": "testuser",
        "email": "test@example.com",
        "role": "basic",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-05-14T23:59:59Z",
    }

@pytest.fixture
def premium_user():
    """
    Fixture that provides premium user data.
    
    Returns:
        dict: Premium user information
    """
    return {
        "id": 456,
        "username": "premiumuser",
        "email": "premium@example.com",
        "role": "premium",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-05-14T23:59:59Z",
        "subscription": {
            "plan": "Premium",
            "status": "active",
            "renewal_date": "2025-06-01"
        }
    }

@pytest.fixture
def admin_user():
    """
    Fixture that provides admin user data.
    
    Returns:
        dict: Admin user information
    """
    return {
        "id": 789,
        "username": "adminuser",
        "email": "admin@example.com",
        "role": "admin",
        "status": "active",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-05-14T23:59:59Z",
    }

@pytest.fixture
def stock_data():
    """
    Fixture that provides sample stock data for tests.
    
    Returns:
        dict: Sample stock data
    """
    return {
        "ticker": "AAPL",
        "info": {
            "name": "Apple Inc.",
            "price": 187.42,
            "change": 2.15,
            "change_percent": 1.16,
            "volume": 36472891,
            "average_volume": 42691354,
            "market_cap": 2963485192000,
            "pe_ratio": 28.79,
            "exchange": "NASDAQ",
            "sector": "Technology"
        },
        "historical_data": [
            {"date": "2025-05-14", "open": 185.27, "high": 188.45, "low": 185.19, "close": 187.42, "volume": 36472891},
            {"date": "2025-05-13", "open": 184.76, "high": 186.23, "low": 183.98, "close": 185.27, "volume": 32819403},
            # More historical data...
        ]
    }

@pytest.fixture
def forecast_data():
    """
    Fixture that provides sample forecast data for tests.
    
    Returns:
        dict: Sample forecast data for a stock
    """
    return {
        "ticker": "AAPL",
        "current_price": 187.42,
        "end_price": 193.24,
        "peak_price": 195.68,
        "minimum_price": 186.93,
        "price_range": 8.75,
        "confidence_level": 87,
        "volatility": "Medium",
        "volatility_description": "Moderate price fluctuations expected",
        "trend": "Upward",
        "trend_strength": "Strong bullish momentum",
        "signal": "Buy",
        "signal_strength": "Strong buy signal",
        "accuracy": 92.5,
        "forecast_points": [
            {"date": "2025-05-15", "price": 188.75, "lower": 187.21, "upper": 190.29},
            {"date": "2025-05-16", "price": 189.94, "lower": 187.65, "upper": 192.23},
            # More forecast points...
        ],
        "summary": "Apple Inc. (AAPL) shows a strong positive trend over the next 7 days, with a predicted price increase of 3.10%."
    }

@pytest.fixture
def watchlist_data():
    """
    Fixture that provides sample watchlist data for tests.
    
    Returns:
        list: Sample watchlist items
    """
    return [
        {
            "ticker": "AAPL",
            "info": {
                "name": "Apple Inc.",
                "price": 187.42,
                "change": 2.15,
                "change_percent": 1.16,
                "volume": 36472891,
                "market_cap": 2963485192000
            },
            "notes": "Considering buying on next dip"
        },
        {
            "ticker": "MSFT",
            "info": {
                "name": "Microsoft Corp.",
                "price": 349.35,
                "change": 1.12,
                "change_percent": 0.32,
                "volume": 22541968,
                "market_cap": 2594823199000
            },
            "notes": None
        }
    ]