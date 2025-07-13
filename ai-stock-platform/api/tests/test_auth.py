"""
Authentication Tests
Created: 2025-05-19 04:07:03
Author: daparthi001
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))
import pytest

pytest.importorskip("httpx")
from api.main import app
from core.security import create_access_token
from fastapi.testclient import TestClient

client = TestClient(app)

def test_login_success():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "testpass"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_get_current_user():
    token = create_access_token({"sub": "testuser"})
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
