class RiskManagementService:
    def __init__(self, market_data=None):
        self.limits = {}

    async def set_position_limit(self, user_id: str, symbol: str, limit: int):
        self.limits[(user_id, symbol)] = limit

    async def check_position_limits(self, user_id: str, symbol: str, quantity: int):
        limit = self.limits.get((user_id, symbol), float("inf"))
        if quantity > limit:
            return {"approved": False, "reason": "position limit exceeded"}
        return {"approved": True}

    async def check_market_risk(self, *args, **kwargs):
        return {"approved": True}

    async def check_volatility(self, *args, **kwargs):
        return {"approved": True}
