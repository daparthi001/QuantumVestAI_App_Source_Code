"""
Order History Service
Created: 2025-05-19 04:50:44
Author: daparthi001
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session
from api.models.orders import Order, OrderStatus
from api.schemas.order import OrderFilter

class OrderHistoryService:
    def __init__(self, db: Session):
        self.db = db

    async def get_order_history(
        self,
        user_id: str,
        filters: Optional[OrderFilter] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict:
        """
        Retrieve order history with filtering and pagination
        """
        query = self.db.query(Order).filter(Order.user_id == user_id)
        
        if filters:
            query = self._apply_filters(query, filters)
            
        total = query.count()
        orders = query.order_by(desc(Order.created_at))\
                     .offset((page - 1) * page_size)\
                     .limit(page_size)\
                     .all()
                     
        return {
            'orders': orders,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }

    async def get_order_analytics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Calculate order analytics for a user
        """
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
            
        orders = self.db.query(Order).filter(
            and_(
                Order.user_id == user_id,
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).all()
        
        return {
            'total_orders': len(orders),
            'order_types': self._analyze_order_types(orders),
            'execution_analysis': self._analyze_execution_metrics(orders),
            'daily_statistics': self._calculate_daily_statistics(orders),
            'symbol_breakdown': self._analyze_symbol_breakdown(orders),
            'performance_metrics': self._calculate_performance_metrics(orders)
        }

    def _apply_filters(self, query, filters: OrderFilter):
        """
        Apply filters to the order query
        """
        if filters.symbol:
            query = query.filter(Order.symbol == filters.symbol)
        if filters.status:
            query = query.filter(Order.status == filters.status)
        if filters.order_type:
            query = query.filter(Order.order_type == filters.order_type)
        if filters.start_date:
            query = query.filter(Order.created_at >= filters.start_date)
        if filters.end_date:
            query = query.filter(Order.created_at <= filters.end_date)
        return query

    def _analyze_order_types(self, orders: List[Order]) -> Dict:
        """
        Analyze distribution of order types
        """
        type_counts = {}
        for order in orders:
            type_counts[order.order_type] = type_counts.get(
                order.order_type,
                0
            ) + 1
            
        return {
            'distribution': type_counts,
            'most_common': max(type_counts.items(), key=lambda x: x[1])[0]
        }

    def _analyze_execution_metrics(self, orders: List[Order]) -> Dict:
        """
        Analyze order execution metrics
        """
        filled_orders = [o for o in orders if o.status == OrderStatus.FILLED]
        execution_times = [
            (o.execution_time - o.created_at).total_seconds()
            for o in filled_orders
            if o.execution_time
        ]
        
        return {
            'fill_rate': len(filled_orders) / len(orders) if orders else 0,
            'average_execution_time': sum(execution_times) / len(execution_times)
            if execution_times else 0,
            'cancellation_rate': len(
                [o for o in orders if o.status == OrderStatus.CANCELLED]
            ) / len(orders) if orders else 0
        }

    def _calculate_daily_statistics(self, orders: List[Order]) -> Dict:
        """
        Calculate daily order statistics
        """
        daily_stats = {}
        for order in orders:
            date = order.created_at.date()
            if date not in daily_stats:
                daily_stats[date] = {
                    'total_orders': 0,
                    'filled_orders': 0,
                    'total_value': 0
                }
            
            daily_stats[date]['total_orders'] += 1
            if order.status == OrderStatus.FILLED:
                daily_stats[date]['filled_orders'] += 1
                daily_stats[date]['total_value'] += (
                    order.executed_price * order.executed_quantity
                    if order.executed_price and order.executed_quantity
                    else 0
                )
                
        return daily_stats

    def _analyze_symbol_breakdown(self, orders: List[Order]) -> Dict:
        """
        Analyze orders by symbol
        """
        symbol_stats = {}
        for order in orders:
            if order.symbol not in symbol_stats:
                symbol_stats[order.symbol] = {
                    'total_orders': 0,
                    'filled_orders': 0,
                    'total_value': 0
                }
            
            symbol_stats[order.symbol]['total_orders'] += 1
            if order.status == OrderStatus.FILLED:
                symbol_stats[order.symbol]['filled_orders'] += 1
                symbol_stats[order.symbol]['total_value'] += (
                    order.executed_price * order.executed_quantity
                    if order.executed_price and order.executed_quantity
                    else 0
                )
                
        return symbol_stats

    def _calculate_performance_metrics(self, orders: List[Order]) -> Dict:
        """
        Calculate order performance metrics
        """
        filled_orders = [o for o in orders if o.status == OrderStatus.FILLED]
        
        return {
            'total_value': sum(
                o.executed_price * o.executed_quantity
                for o in filled_orders
                if o.executed_price and o.executed_quantity
            ),
            'average_order_size': sum(
                o.quantity for o in orders
            ) / len(orders) if orders else 0,
            'success_rate': len(filled_orders) / len(orders) if orders else 0,
            'average_fill_price': sum(
                o.executed_price for o in filled_orders
                if o.executed_price
            ) / len(filled_orders) if filled_orders else 0
        }