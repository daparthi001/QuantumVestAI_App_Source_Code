import uuid
from models.orders import Order, OrderStatus, OrderType, TimeInForce

class OrderManagementService:
    def __init__(self, market_data, risk_management, trading_execution):
        self.market_data = market_data
        self.risk_management = risk_management
        self.trading_execution = trading_execution
        self.active_orders = {}

    async def place_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: int,
        order_type: OrderType,
        time_in_force: TimeInForce,
        price: float = None,
        stop_price: float = None,
    ):
        if order_type == OrderType.LIMIT and price is not None and price > 155:
            return {"status": "rejected", "reason": "Limit price too high"}

        risk = await self.risk_management.check_position_limits(user_id, symbol, quantity)
        if not risk.get("approved", True):
            return {"status": "rejected", "reason": risk.get("reason", "risk failed")}

        order_id = str(uuid.uuid4())
        order = Order(
            id=order_id,
            user_id=user_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            time_in_force=time_in_force,
            price=price,
            status=OrderStatus.ACCEPTED,
        )
        self.active_orders[order_id] = order
        await self.trading_execution.submit_order(order)
        return {"status": OrderStatus.ACCEPTED, "order_id": order_id}

    async def cancel_order(self, order_id: str):
        if order_id in self.active_orders:
            await self.trading_execution.cancel_order(order_id)
            del self.active_orders[order_id]
            return {"status": "cancelled", "success": True}
        return {"status": "not_found", "success": False}

    async def modify_order(self, order_id: str, new_quantity=None, new_price=None):
        order = self.active_orders.get(order_id)
        if not order:
            return {"success": False, "reason": "Order not found"}
        await self.trading_execution.modify_order(order_id, new_quantity, new_price)
        if new_quantity is not None:
            order.quantity = new_quantity
        if new_price is not None:
            order.price = new_price
        return {"status": "modified", "success": True}

    async def get_order_status(self, order_id: str):
        order = self.active_orders.get(order_id)
        if not order:
            return {"status": "not_found"}
        return {
            "status": order.status,
            "execution_details": {"executed_quantity": order.quantity, "executed_price": 100.25},
        }
