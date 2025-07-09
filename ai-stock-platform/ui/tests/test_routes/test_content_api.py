"""Tests for content API demo endpoints."""
from fastapi import status


def test_get_news(client):
    response = client.get("/api/content/news")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert data


def test_get_trending(client):
    response = client.get("/api/content/trending")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_market_movers(client):
    response = client.get("/api/content/market-movers")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_ai_recommendations(client):
    response = client.get("/api/content/ai-recommendations")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
