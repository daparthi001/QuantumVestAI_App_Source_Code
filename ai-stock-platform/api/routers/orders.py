"""
Order Management API Endpoints
Created: 2025-05-19 04:52:08
Author: daparthi001
"""
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from db.session import get_db
from api.services.order_management import OrderManagementService
from api.services.order_history import OrderHistoryService
from api.services.order_websocket import OrderWebSocketService
from api.schemas.order import (
    OrderCreate,
    OrderModify,
    OrderResponse,
    OrderFilter,
    OrderAnalytics
)
from core.auth import get_current_user

router = APIRouter()
ws_service = OrderWebSocketService()

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order: OrderCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    order_service = OrderManagementService(db)
    
    try:
        result = await order_service.place_order(
            user_id=current_user.id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            time_in_force=order.time_in_force,
            price=order.price,
            stop_price=order.stop_price
        )
        
        if result['status'] == 'rejected':
            raise HTTPException(
                status_code=400,
                detail=result['reason']
            )
            
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel an existing order"""
    order_service = OrderManagementService(db)
    
    try:
        result = await order_service.cancel_order(order_id)
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['reason']
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.patch("/orders/{order_id}", response_model=OrderResponse)
async def modify_order(
    order_id: str,
    modifications: OrderModify,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Modify an existing order"""
    order_service = OrderManagementService(db)
    
    try:
        result = await order_service.modify_order(
            order_id=order_id,
            new_quantity=modifications.quantity,
            new_price=modifications.price
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['reason']
            )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/orders", response_model=List[OrderResponse])
async def get_orders(
    filter: OrderFilter = Depends(),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order history with filters"""
    history_service = OrderHistoryService(db)
    
    try:
        result = await history_service.get_order_history(
            user_id=current_user.id,
            filters=filter
        )
        return result['orders']
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/orders/analytics", response_model=OrderAnalytics)
async def get_order_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order analytics"""
    history_service = OrderHistoryService(db)
    
    try:
        return await history_service.get_order_analytics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.websocket("/ws/orders/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str
):
    """WebSocket endpoint for real-time order updates"""
    try:
        # Verify token and user
        if not verify_token(token, user_id):
            await websocket.close(code=4001)
            return
            
        await ws_service.connect(websocket, user_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                # Handle incoming messages if needed
                
        except WebSocketDisconnect:
            await ws_service.disconnect(websocket, user_id)
            
    except Exception as e:
        await websocket.close(code=4000)