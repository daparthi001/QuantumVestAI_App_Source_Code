# ui/services/forecast_service.py
from typing import Any, Dict, List, Optional

# Import APIClient from the sibling ``services`` package. This keeps the
# module working when the code is deployed without the legacy ``ui``
# package at the repository root.
from .api_client import APIClient


def get_stock_info(ticker: str, token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = APIClient(token=token)
    return client.get(f"/stocks/{ticker}")

def get_forecast_data(ticker: str, days: int = 7, model: str = "ensemble", token: Optional[str] = None) -> Optional[Dict[str, Any]]:
    client = APIClient(token=token)
    return client.get(f"/forecast/{ticker}", params={
        "days": days,
        "model": model
    })

def search_stocks(query: str, token: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    client = APIClient(token=token)
    response = client.get("/stocks/search", params={"q": query})
    if response:
        return response.get("results", [])
    return None
