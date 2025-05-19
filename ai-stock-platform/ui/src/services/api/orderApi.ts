/**
 * Order API Service
 * Created: 2025-05-19 04:54:48
 * Author: daparthi001
 */
import axios from 'axios';
import { Order } from '../../types/order';
import { API_BASE_URL } from '../../config';

const api = axios.create({
    baseURL: `${API_BASE_URL}/orders`,
    headers: {
        'Content-Type': 'application/json'
    }
});

export const orderApi = {
    async getOrders(): Promise<Order[]> {
        const response = await api.get('/');
        return response.data;
    },

    async getOrder(orderId: string): Promise<Order> {
        const response = await api.get(`/${orderId}`);
        return response.data;
    },

    async createOrder(orderData: Partial<Order>): Promise<Order> {
        const response = await api.post('/', orderData);
        return response.data;
    },

    async modifyOrder(
        orderId: string,
        modifications: Partial<Order>
    ): Promise<Order> {
        const response = await api.patch(`/${orderId}`, modifications);
        return response.data;
    },

    async cancelOrder(orderId: string): Promise<void> {
        await api.delete(`/${orderId}`);
    },

    async getOrderAnalytics(params?: {
        startDate?: string;
        endDate?: string;
    }) {
        const response = await api.get('/analytics', { params });
        return response.data;
    }
};