"""TD Ameritrade paperMoney execution service for tests.

This lightweight service posts orders to the TD Ameritrade paperMoney
API so users can practice trading without risking capital.
"""
from __future__ import annotations

import logging
import os
import requests

from ai-stock-platform.api.models.orders import Order, OrderStatus


class PaperMoneyExecutionService:
    """Simple HTTP client for the paperMoney order endpoints."""

    def __init__(self, access_token: str, account_id: str):
        self.base_url = os.getenv("TD_API_BASE_URL", "https://api.tdameritrade.com/v1")
        self.access_token = access_token
        self.account_id = account_id
        self.logger = logging.getLogger(__name__)

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _order_url(self, order_id: str | None = None) -> str:
        url = f"{self.base_url}/accounts/{self.account_id}/orders"
        if order_id:
            return f"{url}/{order_id}"
        return url

    async def submit_order(self, order: Order) -> dict:
        payload = {
            "orderType": order.order_type.value,
            "session": "NORMAL",
            "duration": order.time_in_force.value,
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": "BUY" if order.side.upper() == "BUY" else "SELL",
                    "quantity": order.quantity,
                    "instrument": {"symbol": order.symbol, "assetType": "EQUITY"},
                }
            ],
        }
        if order.price is not None:
            payload["price"] = order.price
        try:
            resp = requests.post(self._order_url(), json=payload, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            self.logger.debug("Submitted paperMoney order %s", order.id)
            return {"status": OrderStatus.ACCEPTED, "order_id": order.id}
        except Exception as exc:  # pragma: no cover - network issues
            self.logger.error("paperMoney order failed: %s", exc)
            return {"status": "error", "reason": str(exc)}

    async def cancel_order(self, order_id: str) -> dict:
        try:
            resp = requests.delete(self._order_url(order_id), headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return {"success": True}
        except Exception as exc:  # pragma: no cover - network issues
            self.logger.error("paperMoney cancel failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def modify_order(self, order_id: str, new_quantity: int | None = None, new_price: float | None = None) -> dict:
        payload: dict[str, object] = {}
        if new_quantity is not None:
            payload["quantity"] = new_quantity
        if new_price is not None:
            payload["price"] = new_price
        try:
            resp = requests.put(self._order_url(order_id), json=payload, headers=self._headers(), timeout=10)
            resp.raise_for_status()
            return {"success": True, "details": payload}
        except Exception as exc:  # pragma: no cover - network issues
            self.logger.error("paperMoney modify failed: %s", exc)
            return {"success": False, "error": str(exc)}

__all__ = ["PaperMoneyExecutionService"]
