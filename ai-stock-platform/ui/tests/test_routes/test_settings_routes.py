import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status, HTTPException


def test_settings_requires_auth(client):
    """Unauthorized requests to /settings should be rejected."""
    response = client.get("/settings/", headers={"Accept": "application/json"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_settings_with_valid_token(client, test_user):
    """Access to /settings succeeds when token is valid."""
    with patch(
        "ui.middleware.auth_middleware.verify_token",
        new=AsyncMock(return_value=test_user),
    ):
        response = client.get(
            "/settings/",
            headers={
                "Authorization": "Bearer good",
                "Accept": "text/html",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert "Settings - QuantumVestAI" in response.text


def test_settings_with_invalid_token(client):
    """Invalid tokens should be rejected."""
    with patch(
        "ui.middleware.auth_middleware.verify_token",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="bad")),
    ):
        response = client.get(
            "/settings/",
            headers={
                "Authorization": "Bearer bad",
                "Accept": "application/json",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
