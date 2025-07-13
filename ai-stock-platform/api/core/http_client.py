"""HTTP client wrapper for API and UI compatibility."""
from typing import Any, Dict, Optional

from ui.core.http_client import HTTPClient, HTTPClientConfig
from ui.core.http_client import get_http_client as _get_http_client


async def get_http_client():
    async with _get_http_client() as client:
        yield client

async def safe_get_json(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
    default: Any = None,
    timeout: Optional[float] = None,
) -> Any:
    try:
        async with get_http_client() as client:
            response = await client.get(
                url=url,
                params=params,
                headers=headers,
                auth_token=auth_token
            )
            response.raise_for_status()
            return response.json()
    except Exception:
        return default

async def safe_post_json(
    url: str,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    auth_token: Optional[str] = None,
    default: Any = None,
) -> Any:
    try:
        async with get_http_client() as client:
            response = await client.post(
                url=url,
                json=json_data,
                headers=headers,
                auth_token=auth_token
            )
            response.raise_for_status()
            return response.json()
    except Exception:
        return default

from ui.core.http_client import cleanup_http_clients

__all__ = [
    "HTTPClient",
    "HTTPClientConfig",
    "get_http_client",
    "safe_get_json",
    "safe_post_json",
    "cleanup_http_clients",
]
