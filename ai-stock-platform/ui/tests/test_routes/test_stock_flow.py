"""Tests for the stock flow route."""

def test_stock_flow_page(client):
    response = client.get("/stocks/flow")
    assert response.status_code == 200
    assert "Stock Flow Visualization" in response.text
