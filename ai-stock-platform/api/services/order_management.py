"""
Order Management Service
Created: 2025-05-19 04:47:02
Author: daparthi001
"""
from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4
from enum import Enum
from api.models.orders import Order, OrderStatus, OrderType, TimeInForce
from api.services.market_data_service import MarketDataService
from api.services.risk_management import RiskManagementService
from api.services.trading_execution import TradingExecutionService

class OrderValidationError(Exception):
    pass

class OrderManagementService:
    def __init__(
        self,
        market_data: MarketDataService,
        risk_management: RiskManagementService,
        trading_execution: TradingExecutionService
    ):
        self.market_data = market_data
        self.risk_management = risk_management
        self.trading_execution = trading_execution
        self.active_orders: Dict[str, Order] = {}
        self.order_history: List[Order] = []

    async def place_order(
        self,
        user_id: str,
        symbol: str,
        side: str,
        quantity: float,
        order_type: OrderType,
        time_in_force: TimeInForce,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict:
        """
        Place a new order with validation and risk checks
        """
        try:
            # Generate order ID
            order_id = str(uuid4())
            
            # Create order object
            order = Order(
                id=order_id,
                user_id=user_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                time_in_force=time_in_force,
                price=price,
                stop_price=stop_price,
                status=OrderStatus.PENDING,
                created_at=datetime.utcnow()
            )
            
            # Validate order
            await self._validate_order(order)
            
            # Perform risk checks
            await self._perform_risk_checks(order)
            
            # Submit order for execution
            execution_result = await self.trading_execution.submit_order(order)
            
            # Update order status
            order.status = execution_result['status']
            order.executed_price = execution_result.get('executed_price')
            order.executed_quantity = execution_result.get('executed_quantity')
            order.execution_time = execution_result.get('execution_time')
            
            # Store order
            if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL_FILLED]:
                self.active_orders[order_id] = order
            self.order_history.append(order)
            
            return {
                'order_id': order_id,
                'status': order.status,
                'execution_details': execution_result
            }
            
        except OrderValidationError as e:
            return {
                'status': 'rejected',
                'reason': str(e)
            }
        except Exception as e:
            return {
                'status': 'error',
                'reason': f"Order placement failed: {str(e)}"
            }

    async def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel an active order
        """
        try:
            if order_id not in self.active_orders:
                raise OrderValidationError("Order not found or already completed")
            
            order = self.active_orders[order_id]
            
            # Attempt to cancel the order
            cancellation_result = await self.trading_execution.cancel_order(order)
            
            if cancellation_result['success']:
                order.status = OrderStatus.CANCELLED
                del self.active_orders[order_id]
                
                return {
                    'status': 'cancelled',
                    'order_id': order_id
                }
            else:
                return {
                    'status': 'failed',
                    'reason': cancellation_result['reason']
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'reason': f"Order cancellation failed: {str(e)}"
            }

    async def modify_order(
        self,
        order_id: str,
        new_quantity: Optional[float] = None,
        new_price: Optional[float] = None
    ) -> Dict:
        """
        Modify an existing order
        """
        try:
            if order_id not in self.active_orders:
                raise OrderValidationError("Order not found or already completed")
            
            order = self.active_orders[order_id]
            
            # Create modification request
            modifications = {}
            if new_quantity is not None:
                modifications['quantity'] = new_quantity
            if new_price is not None:
                modifications['price'] = new_price
            
            # Validate modifications
            await self._validate_order_modification(order, modifications)
            
            # Submit modification
            modification_result = await self.trading_execution.modify_order(
                order,
                modifications
            )
            
            if modification_result['success']:
                # Update order details
                if new_quantity:
                    order.quantity = new_quantity
                if new_price:
                    order.price = new_price
                
                return {
                    'status': 'modified',
                    'order_id': order_id,
                    'new_details': modification_result['details']
                }
            else:
                return {
                    'status': 'failed',
                    'reason': modification_result['reason']
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'reason': f"Order modification failed: {str(e)}"
            }

    async def get_order_status(self, order_id: str) -> Dict:
        """
        Get current status of an order
        """
        try:
            # Check active orders first
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                status = await self.trading_execution.check_order_status(order)
                
                # Update order status if changed
                if status['status'] != order.status:
                    order.status = status['status']
                    if status['status'] in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                        del self.active_orders[order_id]
                
                return {
                    'order_id': order_id,
                    'status': order.status,
                    'execution_details': status.get('execution_details', {})
                }
            
            # Check order history
            for order in self.order_history:
                if order.id == order_id:
                    return {
                        'order_id': order_id,
                        'status': order.status,
                        'execution_details': {
                            'executed_price': order.executed_price,
                            'executed_quantity': order.executed_quantity,
                            'execution_time': order.execution_time
                        }
                    }
            
            raise OrderValidationError("Order not found")
            
        except Exception as e:
            return {
                'status': 'error',
                'reason': f"Failed to get order status: {str(e)}"
            }

    async def _validate_order(self, order: Order):
        """
        Validate order parameters
        """
        # Validate symbol
        quote = await self.market_data.get_quote(order.symbol)
        if not quote:
            raise OrderValidationError(f"Invalid symbol: {order.symbol}")
        
        # Validate price for limit orders
        if order.order_type == OrderType.LIMIT:
            if not order.price:
                raise OrderValidationError("Limit orders require a price")
            
            if order.side == "BUY" and order.price > quote['ask'] * 1.1:
                raise OrderValidationError("Limit price too high")
            elif order.side == "SELL" and order.price < quote['bid'] * 0.9:
                raise OrderValidationError("Limit price too low")
        
        # Validate quantity
        min_quantity = 0.01  # Example minimum quantity
        if order.quantity < min_quantity:
            raise OrderValidationError(f"Quantity below minimum: {min_quantity}")

    async def _perform_risk_checks(self, order: Order):
        """
        Perform pre-trade risk checks
        """
        # Position limits check
        position_limit = await self.risk_management.check_position_limits(
            order.user_id,
            order.symbol,
            order.quantity
        )
        if not position_limit['approved']:
            raise OrderValidationError(position_limit['reason'])
        
        # Market risk check
        market_risk = await self.risk_management.check_market_risk(
            order.symbol,
            order.side,
            order.quantity
        )
        if not market_risk['approved']:
            raise OrderValidationError(market_risk['reason'])
        
        # Volatility check
        volatility_check = await self.risk_management.check_volatility(
            order.symbol
        )
        if not volatility_check['approved']:
            raise OrderValidationError(volatility_check['reason'])

    async def _validate_order_modification(
        self,
        order: Order,
        modifications: Dict
    ):
        """
        Validate order modifications
        """
        # Create temporary order with modifications for validation
        modified_order = Order(
            id=order.id,
            user_id=order.user_id,
            symbol=order.symbol,
            side=order.side,
            quantity=modifications.get('quantity', order.quantity),
            order_type=order.order_type,
            time_in_force=order.time_in_force,
            price=modifications.get('price', order.price),
            stop_price=order.stop_price,
            status=order.status,
            created_at=order.created_at
        )
        
        # Validate modified order
        await self._validate_order(modified_order)
        await self._perform_risk_checks(modified_order)