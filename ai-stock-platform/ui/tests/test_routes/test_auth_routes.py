"""
Tests for authentication routes.
"""
from unittest.mock import MagicMock, patch

import pytest
from fastapi import status


def test_login_page_get(client):
    """Test that login page loads successfully."""
    response = client.get("/login")
    assert response.status_code == status.HTTP_200_OK
    assert "Sign In" in response.text
    assert "Username" in response.text
    assert "Password" in response.text

def test_login_post_success(client, test_user):
    """Test successful login with valid credentials."""
    # Mock the authentication service
    with patch('ui.routes.auth.authenticate_user') as mock_auth:
        mock_auth.return_value = {
            "access_token": "test_token",
            "user": test_user
        }
        
        # response = client.post(
        #     "/login",
        #     data={"username": "testuser", "password": "password123"}
        # )
        
        # Check redirect to home page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/"
        
        # Check authentication was called correctly
        mock_auth.assert_called_once_with("testuser", "password123")

def test_login_post_failure(client):
    """Test login failure with invalid credentials."""
    # Mock the authentication service to return None (invalid credentials)
    with patch('ui.routes.auth.authenticate_user') as mock_auth:
        mock_auth.return_value = None
        
        response = client.post(
            "/login",
            data={"username": "testuser", "password": "wrongpassword"},
            allow_redirects=False
        )
        
        # Check redirect back to login page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/login?error=1"
        
        # Check authentication was called correctly
        mock_auth.assert_called_once_with("testuser", "wrongpassword")

def test_login_with_next_parameter(client, test_user):
    """Test login with next parameter for redirect."""
    # Mock the authentication service
    with patch('ui.routes.auth.authenticate_user') as mock_auth:
        mock_auth.return_value = {
            "access_token": "test_token",
            "user": test_user
        }
        
        response = client.post(
            "/login?next=/forecast",
            data={"username": "testuser", "password": "password123"}
        )
        
        # Check redirect to specified next page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/forecast"

def test_logout_route(client):
    """Test logout route clears cookies and redirects."""
    response = client.get("/logout")
    
    # Check redirect to login page
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "/login"
    
    # Check token cookie is cleared
    cookies = response.headers.get('set-cookie', '')
    assert 'token=;' in cookies
    assert 'Max-Age=0' in cookies

def test_register_page_get(client):
    """Test that registration page loads successfully."""
    response = client.get("/register")
    assert response.status_code == status.HTTP_200_OK
    assert "Create Account" in response.text
    assert "Username" in response.text
    assert "Email" in response.text
    assert "Password" in response.text

def test_register_post_success(client):
    """Test successful user registration."""
    # Mock the user registration service
    with patch('ui.routes.auth.register_user') as mock_register:
        mock_register.return_value = {"success": True, "user_id": 123}
        
        # response = client.post(
        #     "/register",
        #     data={
        #         "username": "newuser",
        #         "email": "new@example.com",
        #         "password": "Password123!",
        #         "confirm_password": "Password123!",
        #         "terms": "on"
        #     }
        # )
        
        # Check redirect to login page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/login?registered=1"
        
        # Check registration was called correctly
        mock_register.assert_called_once()
        args = mock_register.call_args[0][0]
        assert args.username == "newuser"
        assert args.email == "new@example.com"
        assert args.password == "Password123!"

def test_register_post_username_taken(client):
    """Test registration with username already taken."""
    # Mock the user registration service to indicate error
    with patch('ui.routes.auth.register_user') as mock_register:
        mock_register.return_value = {"success": False, "error": "Username already taken"}
        
        # response = client.post(
        #     "/register",
        #     data={
        #         "username": "existinguser",
        #         "email": "new@example.com",
        #         "password": "Password123!",
        #         "confirm_password": "Password123!",
        #         "terms": "on"
        #     },
        #     allow_redirects=False
        # )
        
        # Check redirect back to registration page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/register?error=1"

def test_register_post_password_mismatch(client):
    """Test registration with mismatched passwords."""
    # response = client.post(
    #     "/register",
    #     data={
    #         "username": "newuser",
    #         "email": "new@example.com",
    #         "password": "Password123!",
    #         "confirm_password": "DifferentPassword123!",
    #         "terms": "on"
    #     },
    #     allow_redirects=False
    # )
    
    # Check redirect back to registration page
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "/register?error=1"

def test_password_reset_request_page(client):
    """Test password reset request page loads."""
    response = client.get("/password-reset")
    assert response.status_code == status.HTTP_200_OK
    assert "Reset Password" in response.text
    assert "Email Address" in response.text

def test_password_reset_request_submit(client):
    """Test submitting password reset request."""
    # Mock the password reset service
    with patch('ui.routes.auth.send_password_reset_email') as mock_reset:
        mock_reset.return_value = True
        
        response = client.post(
            "/password-reset",
            data={"email": "user@example.com"}
        )
        
        # Check redirect to confirmation page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/password-reset/sent"
        
        # Check service was called correctly
        mock_reset.assert_called_once_with("user@example.com")

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
