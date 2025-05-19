/**
 * Order Analytics Service
 * Created: 2025-05-19 05:01:47
 * Author: daparthi001
 */
import Analytics from 'analytics';
import googleAnalytics from '@analytics/google-analytics';
import { Order, OrderType } from '../../types/order';

export class OrderAnalytics {
    private static instance: OrderAnalytics;
    private analytics: Analytics;

    private constructor() {
        this.analytics = Analytics({
            app: 'order-management-ui',
            plugins: [
                googleAnalytics({
                    measurementId: process.env.REACT_APP_GA_MEASUREMENT_ID
                })
            ]
        });
    }

    static getInstance(): OrderAnalytics {
        if (!OrderAnalytics.instance) {
            OrderAnalytics.instance = new OrderAnalytics();
        }
        return OrderAnalytics.instance;
    }

    trackOrderCreation(order: Order) {
        this.analytics.track('order_created', {
            orderId: order.id,
            symbol: order.symbol,
            type: order.orderType,
            side: order.side,
            quantity: order.quantity,
            price: order.price
        });
    }

    trackOrderExecution(order: Order) {
        this.analytics.track('order_executed', {
            orderId: order.id,
            symbol: order.symbol,
            executedPrice: order.executedPrice,
            executedQuantity: order.executedQuantity,
            executionTime: order.executionTime
        });
    }

    trackOrderCancellation(orderId: string, reason?: string) {
        this.analytics.track('order_cancelled', {
            orderId,
            reason,
            timestamp: new Date().toISOString()
        });
    }

    trackUserBehavior(action: string, metadata: Record<string, any>) {
        this.analytics.track(`user_${action}`, {
            ...metadata,
            timestamp: new Date().toISOString()
        });
    }

    async getOrderMetrics(timeframe: 'day' | 'week' | 'month') {
        const response = await fetch(`/api/analytics/orders?timeframe=${timeframe}`);
        const data = await response.json();
        return data;
    }

    async generateOrderReport(startDate: Date, endDate: Date) {
        const response = await fetch('/api/analytics/report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ startDate, endDate })
        });
        return await response.json();
    }
}

// Custom hook for analytics
export const useOrderAnalytics = () => {
    const analytics = OrderAnalytics.getInstance();

    return {
        trackOrderEvent: (eventName: string, metadata: Record<string, any>) => {
            try {
                analytics.trackUserBehavior(eventName, metadata);
            } catch (error) {
                console.error('Analytics error:', error);
                // Don't let analytics errors affect the main application
            }
        },
        
        getOrderMetrics: async (timeframe: 'day' | 'week' | 'month') => {
            try {
                return await analytics.getOrderMetrics(timeframe);
            } catch (error) {
                console.error('Failed to fetch order metrics:', error);
                return null;
            }
        }
    };
};