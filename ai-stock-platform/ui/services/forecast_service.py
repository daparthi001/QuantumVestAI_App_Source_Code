# ui/services/forecast_service.py
from ui.services.api_client import APIClient
from typing import Dict, Any, Optional, List

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