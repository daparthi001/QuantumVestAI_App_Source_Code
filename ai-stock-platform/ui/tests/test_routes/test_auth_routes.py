"""
Tests for authentication routes.
"""
from unittest.mock import MagicMock, patch
import os

import pytest
from fastapi import status
from core.config.settings import settings

settings.API_BASE_URL = "http://testserver/api"


def test_login_page_get(client):
    """Test that login page loads successfully."""
    response = client.get("/login")
    assert response.status_code == status.HTTP_200_OK
    assert "Sign In" in response.text
    assert "Username" in response.text
    assert "Password" in response.text

def test_login_post_success(client, test_user, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    # Mock the APIClient.post_form method
    with patch('services.api_client.APIClient.post_form') as mock_post_form:
        mock_post_form.return_value = {
            "data": {"access_token": "test_token"},
            "message": "Login successful"
        }
        # Simulate user info fetch
        with patch('services.api_client.APIClient.get') as mock_get:
            mock_get.return_value = {"data": test_user}
            response = client.post(
                "/login",
                data={"username": "testuser", "password": "password123"},
                follow_redirects=False
            )
            # Check redirect to dashboard
            assert response.status_code == status.HTTP_302_FOUND
            assert response.headers["location"] == "/dashboard"
            # Check authentication was called correctly
            mock_post_form.assert_called_once_with(
                "/auth/login", data={"username": "testuser", "password": "password123"}
            )

def test_login_post_failure(client, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    # Mock the APIClient.post_form method to return no token (invalid credentials)
    with patch('services.api_client.APIClient.post_form') as mock_post_form:
        mock_post_form.return_value = {"data": {}, "message": "Invalid username or password"}
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "wrongpassword"},
            follow_redirects=False
        )
        # Should return 400 and render login page again
        assert response.status_code == 400
        assert "Invalid username or password" in response.text

def test_login_with_next_parameter(client, test_user, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    # Mock the APIClient.post_form method
    with patch('services.api_client.APIClient.post_form') as mock_post_form:
        mock_post_form.return_value = {
            "data": {"access_token": "test_token"},
            "message": "Login successful"
        }
        with patch('services.api_client.APIClient.get') as mock_get:
            mock_get.return_value = {"data": test_user}
            response = client.post(
                "/login?next=/forecast",
                data={"username": "testuser", "password": "password123"},
                follow_redirects=False
            )
            # Check redirect to specified next page
            assert response.status_code == status.HTTP_302_FOUND
            assert response.headers["location"] == "/forecast"
            mock_post_form.assert_called_once_with(
                "/auth/login", data={"username": "testuser", "password": "password123"}
            )

def test_logout_route(client):
    """Test logout route clears cookies and redirects."""
    response = client.get("/logout")
    
    # Check redirect to login page
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "/login"
    
    # Check token cookie is cleared
    cookies = response.headers.get('set-cookie', '')
    assert 'qvai_token=;' in cookies
    assert 'Max-Age=0' in cookies

def test_register_page_get(client):
    """Test that registration page loads successfully."""
    response = client.get("/register")
    assert response.status_code == status.HTTP_200_OK
    assert "Create Account" in response.text
    assert "Username" in response.text
    assert "Email" in response.text
    assert "Password" in response.text
    assert "Subscription Type" in response.text

def test_register_post_success(client, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    # Mock the APIClient.post method
    with patch('services.api_client.APIClient.post') as mock_post:
        mock_post.return_value = {"data": {"user_id": 123}, "message": "Registration successful"}
        response = client.post(
            "/register",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Test User",
                "subscription_type": "free",
                "terms": "on"
            },
            follow_redirects=False
        )
        # Check redirect to login page
        assert response.status_code == status.HTTP_302_FOUND
        assert "/login" in response.headers["location"]
        mock_post.assert_called_once_with(
            "/auth/register",
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Test User",
                "subscription_type": "free",
                "terms_accepted": True,
            },
        )

def test_register_post_username_taken(client, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    # Mock the APIClient.post method to raise an exception
    with patch('services.api_client.APIClient.post') as mock_post:
        mock_post.side_effect = Exception("Username already taken")
        response = client.post(
            "/register",
            data={
                "username": "existinguser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Test User",
                "subscription_type": "free",
                "terms": "on"
            },
            follow_redirects=False
        )
        # Should return 400 and render register page again
        assert response.status_code == 400
        assert "Username already taken" in response.text
        mock_post.assert_called_once_with(
            "/auth/register",
            data={
                "username": "existinguser",
                "email": "new@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Test User",
                "subscription_type": "free",
                "terms_accepted": True,
            },
        )

def test_register_post_password_mismatch(client, monkeypatch):
    monkeypatch.setenv("API_BASE_URL", "http://testserver/api")
    response = client.post(
        "/register",
        data={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!",
            "full_name": "Test User",
            "subscription_type": "free",
            "terms": "on"
        },
        follow_redirects=False
    )
    # Should return 400 and render register page again
    assert response.status_code == 400
    assert "Passwords do not match" in response.text

def test_password_reset_request_page(client):
    """Test password reset request page loads."""
    response = client.get("/password-reset")
    assert response.status_code == status.HTTP_200_OK
    assert "Reset Password" in response.text
    assert "Email Address" in response.text

def test_password_reset_request_submit(client):
    """Test submitting password reset request."""
    response = client.post(
        "/password-reset",
        data={"email": "user@example.com"}
    )
    # Should return 200 and show success message
    assert response.status_code == 200
    assert "Password reset instructions have been sent" in response.text

def test_auth_middleware(client, test_user):
    """Test authentication middleware blocks protected routes."""
    # Test unauthenticated access to protected route
    response = client.get("/profile", allow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert "/login" in response.headers["location"]
    
    # Mock authenticated user in cookie/jwt
    with patch('ui.middleware.auth_middleware.verify_token') as mock_verify:
        mock_verify.return_value = test_user
        
        # Set a dummy token
        cookies = {"token": "fake_token"}
        response = client.get("/profile", cookies=cookies)
        
        # Should now allow access
        assert response.status_code == status.HTTP_200_OK
