"""
Trading Execution Service
Created: 2025-05-19 04:48:12
Author: daparthi001
"""
from typing import Dict, Optional
from datetime import datetime
import asyncio
import aiohttp
from api.models.orders import Order, OrderStatus, OrderType
from api.services.market_data_service import MarketDataService
from api.core.config import settings

class TradingExecutionService:
    def __init__(self, market_data: MarketDataService):
        self.market_data = market_data
        self.execution_endpoints = {
            'submit': f"{settings.TRADING_API_URL}/execute",
            'cancel': f"{settings.TRADING_API_URL}/cancel",
            'modify': f"{settings.TRADING_API_URL}/modify",
            'status': f"{settings.TRADING_API_URL}/status"
        }
        self.active_orders = {}

    async def submit_order(self, order: Order) -> Dict:
        """
        Submit an order for execution
        """
        try:
            # Pre-execution validation
            await self._validate_market_conditions(order)
            
            # Prepare order for execution
            execution_request = self._prepare_execution_request(order)
            
            # Submit to trading venue
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.execution_endpoints['submit'],
                    json=execution_request,
                    headers=self._get_auth_headers()
                ) as response:
                    execution_result = await response.json()
                    
                    if response.status == 200:
                        # Update order status
                        order.status = OrderStatus.ACCEPTED
                        self.active_orders[order.id] = order
                        
                        # Start monitoring order status
                        asyncio.create_task(self._monitor_order_status(order))
                        
                        return {
                            'status': OrderStatus.ACCEPTED,
                            'order_id': order.id,
                            'execution_details': execution_result
                        }
                    else:
                        return {
                            'status': OrderStatus.REJECTED,
                            'reason': execution_result.get('error', 'Unknown error')
                        }
                        
        except Exception as e:
            return {
                'status': OrderStatus.REJECTED,
                'reason': str(e)
            }

    async def cancel_order(self, order: Order) -> Dict:
        """
        Cancel an active order
        """
        try:
            if order.status not in [OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PARTIAL_FILLED]:
                return {
                    'success': False,
                    'reason': f"Cannot cancel order in status: {order.status}"
                }
                
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.execution_endpoints['cancel'],
                    json={'order_id': order.id},
                    headers=self._get_auth_headers()
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        order.status = OrderStatus.CANCELLED
                        order.cancelled_at = datetime.utcnow()
                        if order.id in self.active_orders:
                            del self.active_orders[order.id]
                            
                        return {
                            'success': True,
                            'details': result
                        }
                    else:
                        return {
                            'success': False,
                            'reason': result.get('error', 'Cancellation failed')
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'reason': str(e)
            }

    async def modify_order(self, order: Order, modifications: Dict) -> Dict:
        """
        Modify an existing order
        """
        try:
            if order.status not in [OrderStatus.PENDING, OrderStatus.ACCEPTED]:
                return {
                    'success': False,
                    'reason': f"Cannot modify order in status: {order.status}"
                }
                
            modification_request = {
                'order_id': order.id,
                'modifications': modifications
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.execution_endpoints['modify'],
                    json=modification_request,
                    headers=self._get_auth_headers()
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        # Update order with modifications
                        for key, value in modifications.items():
                            setattr(order, key, value)
                        order.updated_at = datetime.utcnow()
                        
                        return {
                            'success': True,
                            'details': result
                        }
                    else:
                        return {
                            'success': False,
                            'reason': result.get('error', 'Modification failed')
                        }
                        
        except Exception as e:
            return {
                'success': False,
                'reason': str(e)
            }

    async def check_order_status(self, order: Order) -> Dict:
        """
        Check the current status of an order
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.execution_endpoints['status']}/{order.id}",
                    headers=self._get_auth_headers()
                ) as response:
                    result = await response.json()
                    
                    if response.status == 200:
                        return {
                            'status': result['status'],
                            'execution_details': result.get('execution_details', {})
                        }
                    else:
                        return {
                            'status': order.status,
                            'error': result.get('error', 'Status check failed')
                        }
                        
        except Exception as e:
            return {
                'status': order.status,
                'error': str(e)
            }

    async def _validate_market_conditions(self, order: Order):
        """
        Validate current market conditions before execution
        """
        quote = await self.market_data.get_quote(order.symbol)
        
        if not quote:
            raise ValueError(f"Unable to get quote for {order.symbol}")
            
        if order.order_type == OrderType.MARKET:
            if order.side == "BUY" and quote['ask'] > quote['last'] * 1.05:
                raise ValueError("Market price has moved too far from last trade")
            elif order.side == "SELL" and quote['bid'] < quote['last'] * 0.95:
                raise ValueError("Market price has moved too far from last trade")

    def _prepare_execution_request(self, order: Order) -> Dict:
        """
        Prepare order for execution submission
        """
        return {
            'order_id': order.id,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': order.quantity,
            'order_type': order.order_type,
            'time_in_force': order.time_in_force,
            'price': order.price,
            'stop_price': order.stop_price,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _get_auth_headers(self) -> Dict:
        """
        Get authentication headers for API requests
        """
        return {
            'Authorization': f"Bearer {settings.TRADING_API_KEY}",
            'Content-Type': 'application/json'
        }

    async def _monitor_order_status(self, order: Order):
        """
        Continuously monitor order status until completion
        """
        while order.status in [OrderStatus.PENDING, OrderStatus.ACCEPTED, OrderStatus.PARTIAL_FILLED]:
            try:
                status = await self.check_order_status(order)
                
                if status['status'] != order.status:
                    order.status = status['status']
                    if 'execution_details' in status:
                        order.executed_price = status['execution_details'].get('price')
                        order.executed_quantity = status['execution_details'].get('quantity')
                        order.execution_time = datetime.fromisoformat(
                            status['execution_details'].get('time')
                        )
                
                if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
                    if order.id in self.active_orders:
                        del self.active_orders[order.id]
                    break
                
                await asyncio.sleep(1)  # Poll every second
                
            except Exception as e:
                print(f"Error monitoring order {order.id}: {e}")
                await asyncio.sleep(5)  # Back off on error