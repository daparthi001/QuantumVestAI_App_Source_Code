"""
Tests for the API client service.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "ai-stock-platform"))
sys.path.append(os.path.join(ROOT, "ai-stock-platform", "api"))
pytest.importorskip("requests")
import requests
import json

from ui.services.api_client import APIClient
from core.config.settings import settings

def test_api_client_initialization():
    """Test API client initializes with correct values."""
    # Test with no token
    client = APIClient()
    assert client.base_url == settings.API_BASE_URL
    assert client.headers["Content-Type"] == "application/json"
    assert "Authorization" not in client.headers
    
    # Test with token
    client = APIClient(token="test_token")
    assert client.headers["Authorization"] == "Bearer test_token"

@patch("requests.get")
def test_api_client_get(mock_get):
    """Test API client GET method."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    
    client = APIClient()
    result = client.get("/test-endpoint")
    
    # Check request was made correctly
    mock_get.assert_called_once_with(
        f"{settings.API_BASE_URL}/test-endpoint",
        headers=client.headers,
        params=None,
        timeout=10
    )
    
    # Check response processing
    assert result == {"data": "test"}

@patch("requests.get")
def test_api_client_get_with_params(mock_get):
    """Test API client GET method with query parameters."""
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    
    client = APIClient()
    result = client.get("/test-endpoint", params={"key": "value"})
    
    # Check params were passed correctly
    mock_get.assert_called_once_with(
        f"{settings.API_BASE_URL}/test-endpoint",
        headers=client.headers,
        params={"key": "value"},
        timeout=10
    )

@patch("requests.get")
def test_api_client_get_error(mock_get):
    """Test API client handles errors correctly."""
    # Mock error response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Not found"}
    mock_get.return_value = mock_response
    
    client = APIClient()
    result = client.get("/not-found")
    
    # Should return None on error
    assert result is None

@patch("requests.get")
def test_api_client_get_connection_error(mock_get):
    """Test API client handles connection errors."""
    # Mock connection error
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")
    
    client = APIClient()
    result = client.get("/test-endpoint")
    
    # Should return None on connection error
    assert result is None

@patch("requests.post")
def test_api_client_post(mock_post):
    """Test API client POST method."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"id": 123}
    mock_post.return_value = mock_response
    
    client = APIClient()
    data = {"name": "Test"}
    result = client.post("/test-endpoint", data=data)
    
    # Check request was made correctly
    mock_post.assert_called_once_with(
        f"{settings.API_BASE_URL}/test-endpoint",
        headers=client.headers,
        data=json.dumps(data),
        timeout=10
    )
    
    # Check response processing
    assert result == {"id": 123}

@patch("requests.put")
def test_api_client_put(mock_put):
    """Test API client PUT method."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"updated": True}
    mock_put.return_value = mock_response
    
    client = APIClient()
    data = {"name": "Updated"}
    result = client.put("/test-endpoint/123", data=data)
    
    # Check request was made correctly
    mock_put.assert_called_once_with(
        f"{settings.API_BASE_URL}/test-endpoint/123",
        headers=client.headers,
        data=json.dumps(data),
        timeout=10
    )
    
    # Check response processing
    assert result == {"updated": True}

@patch("requests.delete")
def test_api_client_delete(mock_delete):
    """Test API client DELETE method."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_delete.return_value = mock_response
    
    client = APIClient()
    result = client.delete("/test-endpoint/123")
    
    # Check request was made correctly
    mock_delete.assert_called_once_with(
        f"{settings.API_BASE_URL}/test-endpoint/123",
        headers=client.headers,
        timeout=10
    )
    
    # Check response processing (None for 204 No Content)
    assert result is None

def test_api_client_build_url():
    """Test API client builds URLs correctly."""
    client = APIClient()
    
    # Test with leading slash
    url = client.build_url("/endpoint")
    assert url == f"{settings.API_BASE_URL}/endpoint"
    
    # Test without leading slash
    url = client.build_url("endpoint")
    assert url == f"{settings.API_BASE_URL}/endpoint"
    
    # Test with query parameters already in path
    url = client.build_url("/endpoint?param=value")
    assert url == f"{settings.API_BASE_URL}/endpoint?param=value"

@patch("requests.post")
def test_api_client_authenticate(mock_post):
    """Test API client authenticate method."""
    # Mock successful auth response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_token",
        "user": {"username": "testuser"}
    }
    mock_post.return_value = mock_response
    
    client = APIClient()
    result = client.authenticate("testuser", "password")
    
    # Check auth request was made correctly
    mock_post.assert_called_once_with(
        f"{settings.API_BASE_URL}/auth/login",
        headers=client.headers,
        data=json.dumps({
            "username": "testuser", 
            "password": "password"
        }),
        timeout=10
    )
    
    # Check response
    assert result["access_token"] == "test_token"
    assert result["user"]["username"] == "testuser"

@patch("requests.post")
def test_api_client_authenticate_failure(mock_post):
    """Test API client handles authentication failure."""
    # Mock auth failure
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {"detail": "Invalid credentials"}
    mock_post.return_value = mock_response
    
    client = APIClient()
    result = client.authenticate("testuser", "wrongpassword")
    
    # Should return None on auth failure
    assert result is None