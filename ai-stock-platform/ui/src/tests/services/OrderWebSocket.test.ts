/**
 * Order WebSocket Service Tests
 * Created: 2025-05-19 04:55:47
 * Author: daparthi001
 */
import { OrderWebSocket } from '../../services/OrderWebSocket';
import { store } from '../../store';
import { updateOrderStatus } from '../../store/slices/orderSlice';
import { OrderStatus } from '../../types/order';

describe('OrderWebSocket', () => {
    let ws: OrderWebSocket;
    let mockWebSocket: any;

    beforeEach(() => {
        // Mock WebSocket
        mockWebSocket = {
            send: jest.fn(),
            close: jest.fn(),
            addEventListener: jest.fn(),
            removeEventListener: jest.fn()
        };
        
        (global as any).WebSocket = jest.fn(() => mockWebSocket);
        
        ws = new OrderWebSocket();
    });

    it('establishes connection with correct URL', () => {
        localStorage.setItem('token', 'test-token');
        localStorage.setItem('userId', 'test-user');
        
        ws.connect();
        
        expect(WebSocket).toHaveBeenCalledWith(
            expect.stringContaining('/orders/test-user?token=test-token')
        );
    });

    it('handles order updates correctly', () => {
        const orderUpdate = {
            type: 'order_update',
            data: {
                order_id: 'test-order',
                status: OrderStatus.FILLED,
                executed_quantity: 100,
                executed_price: 150.5,
                timestamp: '2025-05-19T04:55:47Z'
            }
        };

        ws.connect();
        mockWebSocket.onmessage({ data: JSON.stringify(orderUpdate) });

        expect(store.getState().orders.orders).toContainEqual(
            expect.objectContaining({
                id: 'test-order',
                status: OrderStatus.FILLED
            })
        );
    });

    it('attempts reconnection on connection close', () => {
        jest.useFakeTimers();
        
        ws.connect();
        mockWebSocket.onclose({ code: 1006 });
        
        jest.advanceTimersByTime(1000);
        
        expect(WebSocket).toHaveBeenCalledTimes(2);
    });

    it('sends heartbeat messages', () => {
        jest.useFakeTimers();
        
        ws.connect();
        jest.advanceTimersByTime(30000);
        
        expect(mockWebSocket.send).toHaveBeenCalledWith(
            expect.stringContaining('heartbeat')
        );
    });
});