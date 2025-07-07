/**
 * Test Data Generator Utilities
 * Created: 2025-01-08
 * Author: daparthi001
 */
import { Order, OrderStatus, OrderType, TimeInForce, OrderSide } from '../../types/order';

export function generateTestOrders(count: number): Order[] {
    const orders: Order[] = [];
    const symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX'];
    
    for (let i = 0; i < count; i++) {
        const order: Order = {
            id: `order-${i}`,
            userId: `user-${Math.floor(i / 10)}`,
            symbol: symbols[i % symbols.length],
            side: i % 2 === 0 ? OrderSide.BUY : OrderSide.SELL,
            quantity: Math.floor(Math.random() * 1000) + 1,
            orderType: Object.values(OrderType)[Math.floor(Math.random() * Object.values(OrderType).length)],
            timeInForce: Object.values(TimeInForce)[Math.floor(Math.random() * Object.values(TimeInForce).length)],
            price: Math.random() * 1000 + 10,
            stopPrice: Math.random() * 1000 + 10,
            status: Object.values(OrderStatus)[Math.floor(Math.random() * Object.values(OrderStatus).length)],
            createdAt: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            updatedAt: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            executedPrice: Math.random() * 1000 + 10,
            executedQuantity: Math.floor(Math.random() * 1000) + 1,
            executionTime: new Date(Date.now() - Math.random() * 86400000).toISOString(),
            canModify: Math.random() > 0.5
        };
        
        orders.push(order);
    }
    
    return orders;
}

export function generateTestOrder(): Order {
    return generateTestOrders(1)[0];
}

export const mockOrder: Order = {
    id: 'test-order-1',
    userId: 'test-user-1',
    symbol: 'AAPL',
    side: OrderSide.BUY,
    quantity: 100,
    orderType: OrderType.MARKET,
    timeInForce: TimeInForce.DAY,
    price: 150.00,
    status: OrderStatus.PENDING,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    canModify: true
};