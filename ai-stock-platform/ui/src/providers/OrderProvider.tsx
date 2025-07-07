/**
 * Order Context Provider
 * Created: 2025-05-19 05:00:36
 * Author: daparthi001
 */
import React, { createContext } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from '../store/orderStore';
import { useOrderWebSocket } from '../store/orderStore';

const OrderContext = createContext<null>(null);

export const OrderProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    // Initialize WebSocket connection
    useOrderWebSocket();

    return (
        <QueryClientProvider client={queryClient}>
            <OrderContext.Provider value={null}>
                {children}
            </OrderContext.Provider>
            {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
        </QueryClientProvider>
    );
};

// Custom hook for component error boundaries
export const useOrderErrorBoundary = () => {
    return {
        fallback: ({ error, resetErrorBoundary }: any) => (
            <div role="alert">
                <p>Something went wrong:</p>
                <pre>{error.message}</pre>
                <button onClick={resetErrorBoundary}>Try again</button>
            </div>
        ),
    };
};

// Export hooks and utilities
export { useOrders, useOrder, useCreateOrder, useUpdateOrder, useCancelOrder } from '../store/orderStore';