/**
 * Order WebSocket Service
 * Created: 2025-05-19 04:54:48
 * Author: daparthi001
 */
import { store } from '../store';
import { updateOrderStatus } from '../store/slices/orderSlice';
import { OrderStatus } from '../types/order';

export class OrderWebSocket {
    private ws: WebSocket | null = null;
    private reconnectAttempts = 0;
    private maxReconnectAttempts = 5;
    private reconnectTimeout = 1000;
    private heartbeatIntervalId: ReturnType<typeof setInterval> | null = null;

    constructor() {
        this.handleMessage = this.handleMessage.bind(this);
        this.handleClose = this.handleClose.bind(this);
        this.handleError = this.handleError.bind(this);
    }

    connect() {
        try {
            const token = localStorage.getItem('token');
            const userId = localStorage.getItem('userId');

            if (!token || !userId) {
                throw new Error('Authentication required');
            }

            const viteEnv: Record<string, string> = (typeof import.meta !== 'undefined' && import.meta.env) || {};
            const wsBase =
                viteEnv.VITE_WS_URL ||
                (typeof process !== 'undefined' ? process.env.REACT_APP_WS_URL : undefined) ||
                'ws://quantumvestai-dev-api:8000/ws';
            this.ws = new WebSocket(`${wsBase}/orders/${userId}?token=${token}`);

            this.ws.onopen = this.handleOpen.bind(this);
            this.ws.onmessage = this.handleMessage;
            this.ws.onclose = this.handleClose;
            this.ws.onerror = this.handleError;

        } catch (error) {
            console.error('WebSocket connection failed:', error);
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.heartbeatIntervalId) {
            clearInterval(this.heartbeatIntervalId);
            this.heartbeatIntervalId = null;
        }
    }

    private handleOpen() {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;

        // Send heartbeat every 30 seconds
        this.heartbeatIntervalId = setInterval(() => {
            this.sendHeartbeat();
        }, 30000);
    }

    private handleMessage(event: MessageEvent) {
        try {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'order_update':
                    this.handleOrderUpdate(data.data);
                    break;
                case 'execution_report':
                    this.handleExecutionReport(data.data);
                    break;
                case 'heartbeat':
                    // Handle heartbeat response
                    break;
                default:
                    console.warn('Unknown message type:', data.type);
            }
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    }

    private handleClose(event: CloseEvent) {
        console.log('WebSocket closed:', event.code, event.reason);

        if (this.heartbeatIntervalId) {
            clearInterval(this.heartbeatIntervalId);
            this.heartbeatIntervalId = null;
        }

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
                this.reconnectAttempts++;
                this.connect();
            }, this.reconnectTimeout * Math.pow(2, this.reconnectAttempts));
        }
    }

    private handleError(error: Event) {
        console.error('WebSocket error:', error);
    }

    private handleOrderUpdate(orderUpdate: any) {
        store.dispatch(updateOrderStatus({
            orderId: orderUpdate.order_id,
            status: orderUpdate.status as OrderStatus,
            executionDetails: {
                executedQuantity: orderUpdate.executed_quantity,
                executedPrice: orderUpdate.executed_price,
                lastUpdateTime: orderUpdate.timestamp
            }
        }));
    }

    private handleExecutionReport(execution: any) {
        store.dispatch(updateOrderStatus({
            orderId: execution.order_id,
            status: 'FILLED' as OrderStatus,
            executionDetails: {
                executedQuantity: execution.quantity,
                executedPrice: execution.price,
                executionTime: execution.timestamp
            }
        }));
    }

    private sendHeartbeat() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'heartbeat',
                timestamp: new Date().toISOString()
            }));
        }
    }
}