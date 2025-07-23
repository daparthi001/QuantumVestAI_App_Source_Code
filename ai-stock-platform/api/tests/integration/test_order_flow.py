"""
Order Flow Integration Tests
Created: 2025-05-19 04:50:44
Author: daparthi001
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))
import asyncio
from datetime import datetime

import pytest
import pytest_asyncio
from models.orders import Order, OrderStatus, OrderType, TimeInForce
from services.market_data_service import MarketDataService
from services.order_management import OrderManagementService
from services.risk_management import RiskManagementService
from services.trading_execution import TradingExecutionService


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="module")
async def services():
    db = None
    market_data = MarketDataService()
    risk_management = RiskManagementService(market_data)
    trading_execution = TradingExecutionService(market_data)
    order_management = OrderManagementService(
        market_data,
        risk_management,
        trading_execution
    )
    
    return {
        'db': db,
        'market_data': market_data,
        'risk_management': risk_management,
        'trading_execution': trading_execution,
        'order_management': order_management
    }

@pytest.mark.asyncio
async def test_complete_order_flow(services):
    """Test complete order lifecycle from placement to execution"""
    # Place order
    order_result = await services['order_management'].place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        price=150.0
    )
    
    assert order_result['status'] == OrderStatus.ACCEPTED
    order_id = order_result['order_id']
    
    # Verify order status
    status = await services['order_management'].get_order_status(order_id)
    assert status['status'] == OrderStatus.ACCEPTED
    
    # Modify order
    modify_result = await services['order_management'].modify_order(
        order_id=order_id,
        new_quantity=150
    )
    assert modify_result['status'] == 'modified'
    
    # Verify modification
    status = await services['order_management'].get_order_status(order_id)
    assert status['execution_details']['executed_quantity'] == 150
    
    # Cancel order
    cancel_result = await services['order_management'].cancel_order(order_id)
    assert cancel_result['status'] == 'cancelled'
    
    # Verify cancellation
    status = await services['order_management'].get_order_status(order_id)
    assert status['status'] == OrderStatus.CANCELLED

@pytest.mark.asyncio
async def test_market_data_integration(services):
    """Test market data integration with order placement"""
    # Get current market price
    quote = await services['market_data'].get_quote('AAPL')
    assert quote is not None
    
    # Place market order
    order_result = await services['order_management'].place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY
    )
    
    assert order_result['status'] == OrderStatus.ACCEPTED
    
    # Verify execution price is near market price
    status = await services['order_management'].get_order_status(
        order_result['order_id']
    )
    if 'executed_price' in status['execution_details']:
        assert abs(
            status['execution_details']['executed_price'] - quote['last']
        ) < quote['last'] * 0.01  # Within 1% of last price

@pytest.mark.asyncio
async def test_risk_management_integration(services):
    """Test risk management integration"""
    # Set up risk limits
    await services['risk_management'].set_position_limit(
        'test_user',
        'AAPL',
        1000
    )
    
    # Place order within limits
    order_result = await services['order_management'].place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY
    )
    
    assert order_result['status'] == OrderStatus.ACCEPTED
    
    # Place order exceeding limits
    order_result = await services['order_management'].place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=2000,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY
    )
    
    assert order_result['status'] == 'rejected'
    assert 'position limit' in order_result['reason'].lower()
