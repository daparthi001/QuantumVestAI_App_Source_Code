/**
 * Order Management Component
 * Created: 2025-05-19 04:52:08
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
    createOrder,
    cancelOrder,
    modifyOrder,
    fetchOrders
} from '../../store/actions/orderActions';
import { OrderForm } from './OrderForm';
import { OrderList } from './OrderList';
import { OrderAnalytics } from './OrderAnalytics';
import { OrderWebSocket } from '../../services/OrderWebSocket';
import { 
    Order,
    OrderType,
    OrderStatus,
    TimeInForce
} from '../../types/order';
import { RootState } from '../../store/types';

const OrderManagement: React.FC = () => {
    const dispatch = useDispatch();
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
    const { orders, loading, error } = useSelector(
        (state: RootState) => state.orders
    );

    useEffect(() => {
        dispatch(fetchOrders());
        
        // Initialize WebSocket connection
        const ws = new OrderWebSocket();
        ws.connect();
        
        return () => {
            ws.disconnect();
        };
    }, [dispatch]);

    const handleCreateOrder = async (orderData: Partial<Order>) => {
        try {
            await dispatch(createOrder(orderData));
            // Reset form and show success message
        } catch (error) {
            // Handle error
            console.error('Order creation failed:', error);
        }
    };

    const handleCancelOrder = async (orderId: string) => {
        try {
            await dispatch(cancelOrder(orderId));
            setSelectedOrder(null);
        } catch (error) {
            console.error('Order cancellation failed:', error);
        }
    };

    const handleModifyOrder = async (
        orderId: string,
        modifications: Partial<Order>
    ) => {
        try {
            await dispatch(modifyOrder(orderId, modifications));
            setSelectedOrder(null);
        } catch (error) {
            console.error('Order modification failed:', error);
        }
    };

    return (
        <div className="order-management">
            <div className="order-management__header">
                <h1>Order Management</h1>
            </div>
            
            <div className="order-management__content">
                <div className="order-management__form">
                    <OrderForm
                        onSubmit={handleCreateOrder}
                        initialData={selectedOrder}
                    />
                </div>
                
                <div className="order-management__list">
                    <OrderList
                        orders={orders}
                        onSelect={setSelectedOrder}
                        onCancel={handleCancelOrder}
                        onModify={handleModifyOrder}
                    />
                </div>
                
                <div className="order-management__analytics">
                    <OrderAnalytics orders={orders} />
                </div>
            </div>
            
            {error && (
                <div className="order-management__error">
                    Error: {error}
                </div>
            )}
            
            {loading && (
                <div className="order-management__loading">
                    Loading...
                </div>
            )}
        </div>
    );
};

export default OrderManagement;