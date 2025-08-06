import pytest
from fastapi import status


def test_spa_fallback_serves_index(client):
    """Unknown paths should serve the index.html template for SPA routing."""
    response = client.get("/some/unknown/path", headers={"Accept": "text/html"})
    assert response.status_code == status.HTTP_200_OK
    assert "AI-Powered Investing for Everyone" in response.text
