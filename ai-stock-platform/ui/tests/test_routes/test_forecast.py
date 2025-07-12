"""
Tests for forecast routes.
"""
import pytest
from unittest.mock import patch, MagicMock

def test_ticker_search_page(client):
    """Test that ticker search page loads correctly."""
    response = client.get("/ticker-search")
    
    assert response.status_code == 200
    assert "Search for a Stock" in response.text
    assert "Enter a ticker symbol or company name" in response.text

def test_forecast_page_without_ticker(client):
    """Test forecast page redirects when no ticker is provided."""
    response = client.get("/forecast")
    
    assert response.status_code == 302  # Redirect
    assert response.headers["location"] == "/ticker-search"

@patch("ui.routes.forecast.get_stock_info")
@patch("ui.routes.forecast.get_forecast_data")
def test_forecast_page_with_ticker(mock_get_forecast, mock_get_stock, client, stock_data, forecast_data):
    """Test forecast page loads correctly with ticker."""
    # Mock API responses
    mock_get_stock.return_value = stock_data
    mock_get_forecast.return_value = forecast_data
    
    response = client.get("/forecast?ticker=AAPL")
    
    assert response.status_code == 200
    assert "AAPL Stock Forecast" in response.text
    assert "Apple Inc." in response.text
    assert "7-Day Price Forecast" in response.text
    
    # Check API was called correctly
    mock_get_stock.assert_called_once_with("AAPL")
    mock_get_forecast.assert_called_once()

@patch("ui.routes.forecast.get_stock_info")
def test_forecast_page_invalid_ticker(mock_get_stock, client):
    """Test forecast page handles invalid ticker."""
    # Mock API error response
    mock_get_stock.return_value = None
    
    response = client.get("/forecast?ticker=INVALID")
    
    assert response.status_code == 200
    assert "Error" in response.text
    assert "Please try another ticker symbol" in response.text

@patch("ui.routes.forecast.get_model_comparison")
def test_model_comparison_page(mock_get_comparison, client, stock_data):
    """Test model comparison page loads correctly."""
    # Mock API responses
    model_comparison = {
        "ensemble": {"rmse": 1.47, "mae": 1.21, "mape": 0.65},
        "lstm": {"rmse": 1.82, "mae": 1.45, "mape": 0.78},
        "prophet": {"rmse": 2.15, "mae": 1.72, "mape": 0.92},
        "xgboost": {"rmse": 1.93, "mae": 1.56, "mape": 0.84},
        "arima": {"rmse": 2.37, "mae": 1.98, "mape": 1.06}
    }
    
    mock_get_comparison.return_value = model_comparison
    
    with patch("ui.routes.forecast.get_stock_info") as mock_get_stock:
        mock_get_stock.return_value = stock_data
        
        response = client.get("/compare-models?ticker=AAPL")
        
        assert response.status_code == 200
        assert "AAPL Model Comparison" in response.text
        assert "Model Breakdown" in response.text
        assert "Ensemble Model" in response.text
        
        # Check API was called correctly
        mock_get_stock.assert_called_once_with("AAPL")
        mock_get_comparison.assert_called_once()

@patch("ui.routes.forecast.get_stock_info")
def test_predictability_page(mock_get_stock, client, stock_data):
    """Test predictability analysis page loads correctly."""
    # Mock API responses
    mock_get_stock.return_value = stock_data
    
    with patch("ui.routes.forecast.get_predictability_data") as mock_get_predict:
        predictability_data = {
            "score": 87,
            "rank": 12,
            "category": "High",
            "factors": {
                "volatility": {"score": 78, "description": "Moderate volatility makes price movements more predictable"},
                "volume": {"score": 92, "description": "High trading volume creates clear patterns"},
                "trend": {"score": 85, "description": "Strong directional trend detected"}
            }
        }
        mock_get_predict.return_value = predictability_data
        
        response = client.get("/predictability?ticker=AAPL")
        
        assert response.status_code == 200
        assert "Stock Predictability Analysis" in response.text
        assert "Predictability Score" in response.text
        assert "Factor Analysis" in response.text
        
        # Check API was called correctly
        mock_get_stock.assert_called_once_with("AAPL")
        mock_get_predict.assert_called_once()

@patch("ui.routes.forecast.search_stocks")
def test_stock_search_api(mock_search, client):
    """Test stock search API endpoint."""
    # Mock search results
    search_results = [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "AAPL.L", "name": "Apple Inc. (London)"}
    ]
    mock_search.return_value = search_results
    
    response = client.get("/api/search-stocks?query=apple")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["symbol"] == "AAPL"
    
    # Check API was called correctly
    mock_search.assert_called_once_with("apple")

@patch("ui.routes.forecast.get_stock_history")
def test_stock_history_api(mock_history, client, auth_headers):
    """Test stock history API endpoint (requires auth)."""
    # Mock history data
    history_data = [
        {"date": "2025-05-14", "close": 187.42},
        {"date": "2025-05-13", "close": 185.27}
    ]
    mock_history.return_value = history_data
    
    response = client.get("/api/stock-history/AAPL?period=1mo", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["date"] == "2025-05-14"
    
    # Without auth should fail
    response = client.get("/api/stock-history/AAPL?period=1mo")
    assert response.status_code == 401
