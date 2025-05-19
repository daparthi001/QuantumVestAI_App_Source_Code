/**
 * Order List Performance Tests
 * Created: 2025-05-19 04:58:03
 * Author: daparthi001
 */
import React from 'react';
import { render } from '@testing-library/react';
import { OrderList } from '../../components/orders/OrderList';
import { generateTestOrders } from '../utils/testData';

describe('OrderList Performance', () => {
    it('renders large datasets efficiently', () => {
        const orders = generateTestOrders(1000);
        const start = performance.now();
        
        render(
            <OrderList
                orders={orders}
                onSelect={jest.fn()}
                onCancel={jest.fn()}
                onModify={jest.fn()}
            />
        );
        
        const end = performance.now();
        const renderTime = end - start;
        
        // Ensure rendering time is under 100ms for 1000 items
        expect(renderTime).toBeLessThan(100);
    });

    it('handles frequent updates efficiently', async () => {
        const orders = generateTestOrders(100);
        const { rerender } = render(
            <OrderList
                orders={orders}
                onSelect={jest.fn()}
                onCancel={jest.fn()}
                onModify={jest.fn()}
            />
        );

        const updateTimes: number[] = [];
        
        // Simulate 10 rapid updates
        for (let i = 0; i < 10; i++) {
            const start = performance.now();
            rerender(
                <OrderList
                    orders={[...orders, generateTestOrders(1)[0]]}
                    onSelect={jest.fn()}
                    onCancel={jest.fn()}
                    onModify={jest.fn()}
                />
            );
            updateTimes.push(performance.now() - start);
        }

        // Average update time should be under 16ms (60fps)
        const avgUpdateTime = updateTimes.reduce((a, b) => a + b) / updateTimes.length;
        expect(avgUpdateTime).toBeLessThan(16);
    });

    it('maintains smooth scrolling', async () => {
        const orders = generateTestOrders(10000);
        const { container } = render(
            <OrderList
                orders={orders}
                onSelect={jest.fn()}
                onCancel={jest.fn()}
                onModify={jest.fn()}
            />
        );

        const scrollTimes: number[] = [];
        const scrollContainer = container.querySelector('.virtual-scroll-container');

        // Simulate smooth scrolling
        for (let i = 0; i < 100; i += 10) {
            const start = performance.now();
            if (scrollContainer) {
                scrollContainer.scrollTop = i * 50;
            }
            scrollTimes.push(performance.now() - start);
        }

        // Average scroll operation should be under 8ms
        const avgScrollTime = scrollTimes.reduce((a, b) => a + b) / scrollTimes.length;
        expect(avgScrollTime).toBeLessThan(8);
    });
});