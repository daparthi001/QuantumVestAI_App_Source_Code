/**
 * Order Types - Fixed Version
 * Created: 2025-05-19 04:59:21
 * Author: daparthi001
 */
import { z } from 'zod';

// Export individual enum types
export enum OrderStatus {
    PENDING = 'PENDING',
    ACCEPTED = 'ACCEPTED',
    REJECTED = 'REJECTED',
    PARTIAL_FILLED = 'PARTIAL_FILLED',
    FILLED = 'FILLED',
    CANCELLED = 'CANCELLED',
    EXPIRED = 'EXPIRED'
}

export enum OrderType {
    MARKET = 'MARKET',
    LIMIT = 'LIMIT',
    STOP = 'STOP',
    STOP_LIMIT = 'STOP_LIMIT'
}

export enum TimeInForce {
    DAY = 'DAY',
    GTC = 'GTC',
    IOC = 'IOC',
    FOK = 'FOK'
}

export enum OrderSide {
    BUY = 'BUY',
    SELL = 'SELL'
}

export const OrderSchema = z.object({
    id: z.string().uuid(),
    userId: z.string(),
    symbol: z.string().min(1),
    side: z.nativeEnum(OrderSide),
    quantity: z.number().positive(),
    orderType: z.nativeEnum(OrderType),
    timeInForce: z.nativeEnum(TimeInForce),
    price: z.number().optional(),
    stopPrice: z.number().optional(),
    status: z.nativeEnum(OrderStatus),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
    executedPrice: z.number().optional(),
    executedQuantity: z.number().optional(),
    executionTime: z.string().datetime().optional(),
    canModify: z.boolean().optional().default(true)
});

export type Order = z.infer<typeof OrderSchema>;

export function validateOrder(order: unknown): Order {
    return OrderSchema.parse(order);
}