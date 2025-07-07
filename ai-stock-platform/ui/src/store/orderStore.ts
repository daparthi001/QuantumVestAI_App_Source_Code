/**
 * Order Store with React Query
 * Created: 2025-05-19 05:00:36
 * Author: daparthi001
 */
import { useEffect } from 'react';
import { QueryClient, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { orderApi } from '../services/api/orderApi';
import { Order, OrderStatus, validateOrder } from '../types/order';
import { toast } from 'react-toastify';
import { OrderWebSocket } from '../services/OrderWebSocket';

// Create a client
export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 30000, // 30 seconds
            cacheTime: 3600000, // 1 hour
            retry: 3,
            retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
        },
    },
});

// Query keys
export const orderKeys = {
    all: ['orders'] as const,
    lists: () => [...orderKeys.all, 'list'] as const,
    list: (filters: string) => [...orderKeys.lists(), { filters }] as const,
    details: () => [...orderKeys.all, 'detail'] as const,
    detail: (id: string) => [...orderKeys.details(), id] as const,
};

// Custom hooks for order management
export const useOrders = (filters?: any) => {
    return useQuery({
        queryKey: orderKeys.list(JSON.stringify(filters)),
        queryFn: async () => {
            const orders = await orderApi.getOrders();
            return orders.map(validateOrder);
        },
        onError: (error: Error) => {
            toast.error(`Failed to fetch orders: ${error.message}`);
        },
    });
};

export const useOrder = (orderId: string) => {
    return useQuery({
        queryKey: orderKeys.detail(orderId),
        queryFn: async () => {
            const order = await orderApi.getOrder(orderId);
            return validateOrder(order);
        },
        enabled: Boolean(orderId),
    });
};

export const useCreateOrder = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (newOrder: Partial<Order>) => {
            const order = await orderApi.createOrder(newOrder);
            return validateOrder(order);
        },
        onSuccess: (newOrder) => {
            // Optimistically update the cache
            queryClient.setQueryData<Order[]>(orderKeys.lists(), (old = []) => {
                return [newOrder, ...old];
            });
            toast.success('Order created successfully');
        },
        onError: (error: Error) => {
            toast.error(`Failed to create order: ${error.message}`);
        },
    });
};

export const useUpdateOrder = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({
            orderId,
            updates,
        }: {
            orderId: string;
            updates: Partial<Order>;
        }) => {
            const order = await orderApi.modifyOrder(orderId, updates);
            return validateOrder(order);
        },
        onMutate: async ({ orderId, updates }) => {
            // Cancel outgoing refetches
            await queryClient.cancelQueries(orderKeys.detail(orderId));

            // Snapshot the previous value
            const previousOrder = queryClient.getQueryData<Order>(
                orderKeys.detail(orderId)
            );

            // Optimistically update
            queryClient.setQueryData<Order>(orderKeys.detail(orderId), (old) => {
                return old ? { ...old, ...updates } : old;
            });

            return { previousOrder };
        },
        onError: (err, variables, context) => {
            // Rollback on error
            if (context?.previousOrder) {
                queryClient.setQueryData(
                    orderKeys.detail(variables.orderId),
                    context.previousOrder
                );
            }
            toast.error(`Failed to update order: ${err instanceof Error ? err.message : 'Unknown error'}`);
        },
        onSettled: (_data, _error, { orderId }) => {
            // Invalidate related queries
            queryClient.invalidateQueries(orderKeys.detail(orderId));
            queryClient.invalidateQueries(orderKeys.lists());
        },
    });
};

export const useCancelOrder = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (orderId: string) => {
            await orderApi.cancelOrder(orderId);
            return orderId;
        },
        onMutate: async (orderId) => {
            await queryClient.cancelQueries(orderKeys.detail(orderId));

            const previousOrder = queryClient.getQueryData<Order>(
                orderKeys.detail(orderId)
            );

            queryClient.setQueryData<Order>(orderKeys.detail(orderId), (old) => {
                return old ? { ...old, status: OrderStatus.CANCELLED } : old;
            });

            return { previousOrder };
        },
        onError: (err, orderId, context) => {
            if (context?.previousOrder) {
                queryClient.setQueryData(
                    orderKeys.detail(orderId),
                    context.previousOrder
                );
            }
            toast.error(`Failed to cancel order: ${err instanceof Error ? err.message : 'Unknown error'}`);
        },
        onSuccess: () => {
            toast.success('Order cancelled successfully');
        },
        onSettled: (_data, _error, orderId) => {
            queryClient.invalidateQueries(orderKeys.detail(orderId));
            queryClient.invalidateQueries(orderKeys.lists());
        },
    });
};

// WebSocket integration
export const useOrderWebSocket = () => {
    useEffect(() => {
        const ws = new OrderWebSocket();
        ws.connect();

        return () => {
            ws.disconnect();
        };
    }, []);  // Remove handleOrderUpdate dependency since OrderWebSocket uses Redux directly
};