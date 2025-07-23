"""
Order Management Service Tests
Created: 2025-05-19 04:49:34
Author: daparthi001
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT)
sys.path.append(os.path.join(ROOT, "api"))
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from models.orders import Order, OrderStatus, OrderType, TimeInForce
from services.order_management import OrderManagementService


@pytest.fixture
def market_data_mock():
    mock = AsyncMock()
    mock.get_quote.return_value = {
        'symbol': 'AAPL',
        'bid': 150.0,
        'ask': 150.5,
        'last': 150.25
    }
    return mock

@pytest.fixture
def risk_management_mock():
    mock = AsyncMock()
    mock.check_position_limits.return_value = {'approved': True}
    mock.check_market_risk.return_value = {'approved': True}
    mock.check_volatility.return_value = {'approved': True}
    return mock

@pytest.fixture
def trading_execution_mock():
    mock = AsyncMock()
    mock.submit_order.return_value = {
        'status': OrderStatus.ACCEPTED,
        'order_id': 'test_order_id'
    }
    return mock

@pytest.fixture
def order_service(market_data_mock, risk_management_mock, trading_execution_mock):
    return OrderManagementService(
        market_data_mock,
        risk_management_mock,
        trading_execution_mock
    )

@pytest.mark.asyncio
async def test_place_market_order_success(order_service):
    result = await order_service.place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY
    )
    
    assert result['status'] == OrderStatus.ACCEPTED
    assert 'order_id' in result
    assert len(order_service.active_orders) == 1

@pytest.mark.asyncio
async def test_place_limit_order_validation(order_service):
    result = await order_service.place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        price=160.0  # Price too high
    )
    
    assert result['status'] == 'rejected'
    assert 'Limit price too high' in result['reason']
    assert len(order_service.active_orders) == 0

@pytest.mark.asyncio
async def test_cancel_order_success(order_service):
    # First place an order
    order_result = await order_service.place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.MARKET,
        time_in_force=TimeInForce.DAY
    )
    
    order_id = order_result['order_id']
    
    # Mock successful cancellation
    order_service.trading_execution.cancel_order.return_value = {
        'success': True
    }
    
    cancel_result = await order_service.cancel_order(order_id)
    
    assert cancel_result['status'] == 'cancelled'
    assert order_id not in order_service.active_orders

@pytest.mark.asyncio
async def test_modify_order_success(order_service):
    # Place initial order
    order_result = await order_service.place_order(
        user_id='test_user',
        symbol='AAPL',
        side='BUY',
        quantity=100,
        order_type=OrderType.LIMIT,
        time_in_force=TimeInForce.GTC,
        price=150.0
    )
    
    order_id = order_result['order_id']
    
    # Mock successful modification
    order_service.trading_execution.modify_order.return_value = {
        'success': True,
        'details': {'new_quantity': 150}
    }
    
    modify_result = await order_service.modify_order(
        order_id=order_id,
        new_quantity=150
    )
    
    assert modify_result['status'] == 'modified'
    assert order_service.active_orders[order_id].quantity == 150
