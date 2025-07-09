class TradingExecutionService:
    def __init__(self, market_data=None):
        self.market_data = market_data

    async def submit_order(self, order):
        return {"status": "ACCEPTED", "order_id": order.id}

    async def cancel_order(self, order_id: str):
        return {"success": True}

    async def modify_order(self, order_id: str, new_quantity=None, new_price=None):
        return {"success": True, "details": {"new_quantity": new_quantity, "new_price": new_price}}
