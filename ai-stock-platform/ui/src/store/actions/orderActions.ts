/**
 * Order Actions
 * Created: 2025-05-19 04:54:48
 * Author: daparthi001
 */
import { AppThunk } from '../index';
import { orderApi } from '../../services/api';
import {
    fetchOrdersStart,
    fetchOrdersSuccess,
    fetchOrdersFailure,
    createOrderStart,
    createOrderSuccess,
    createOrderFailure,
    updateOrderStatus
} from '../slices/orderSlice';
import { Order, OrderStatus } from '../../types/order';

export const fetchOrders = (): AppThunk => async (dispatch) => {
    try {
        dispatch(fetchOrdersStart());
        const orders = await orderApi.getOrders();
        dispatch(fetchOrdersSuccess(orders));
    } catch (error: any) {
        dispatch(fetchOrdersFailure(error.message));
        throw error;
    }
};

export const createOrder = (orderData: Partial<Order>): AppThunk => async (dispatch) => {
    try {
        dispatch(createOrderStart());
        const order = await orderApi.createOrder(orderData);
        dispatch(createOrderSuccess(order));
        return order;
    } catch (error: any) {
        dispatch(createOrderFailure(error.message));
        throw error;
    }
};

export const cancelOrder = (orderId: string): AppThunk => async (dispatch) => {
    try {
        await orderApi.cancelOrder(orderId);
        dispatch(updateOrderStatus({
            orderId,
            status: OrderStatus.CANCELLED
        }));
    } catch (error: any) {
        // Handle error
        throw error;
    }
};

export const modifyOrder = (
    orderId: string,
    modifications: Partial<Order>
): AppThunk => async (dispatch) => {
    try {
        const updatedOrder = await orderApi.modifyOrder(orderId, modifications);
        dispatch(updateOrderStatus({
            orderId,
            status: updatedOrder.status,
            executionDetails: updatedOrder
        }));
        return updatedOrder;
    } catch (error: any) {
        // Handle error
        throw error;
    }
};