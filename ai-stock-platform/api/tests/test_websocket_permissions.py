"""
Tests for WebSocket permissions.
Created: 2025-08-05
Author: gayatri
"""
import pytest

from core.security.websocket_permissions import check_websocket_permissions


def test_free_tier_can_access_market_data():
    """Test that free tier users can access market data endpoints."""
    payload = {"sub": "user123", "role": "free"}
    
    # Should allow access to market data endpoints
    assert check_websocket_permissions(payload, "/market-data") is True
    assert check_websocket_permissions(payload, "/ws/market-data") is True


def test_premium_param_allows_access():
    """Test that premium parameter allows access regardless of role."""
    payload = {"sub": "user123", "role": "free"}
    
    # Should allow access when premium param is set
    assert check_websocket_permissions(payload, "/premium/data", premium_param="true") is True


def test_admin_role_has_full_access():
    """Test that admin role has access to all endpoints."""
    payload = {"sub": "admin123", "role": "admin"}
    
    # Should allow access to all endpoints
    assert check_websocket_permissions(payload, "/market-data") is True
    assert check_websocket_permissions(payload, "/ws/market-data") is True
    assert check_websocket_permissions(payload, "/premium/data") is True
    assert check_websocket_permissions(payload, "/admin/data") is True


def test_premium_role_has_premium_access():
    """Test that premium role has access to premium endpoints."""
    payload = {"sub": "user123", "role": "premium"}
    
    # Should allow access to market data and premium endpoints
    assert check_websocket_permissions(payload, "/market-data") is True
    assert check_websocket_permissions(payload, "/ws/market-data") is True
    assert check_websocket_permissions(payload, "/premium/data") is True
    
    # Should not allow access to admin endpoints
    assert check_websocket_permissions(payload, "/admin/data") is False
