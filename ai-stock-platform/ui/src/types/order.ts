/**
 * Order Types - Fixed Version
 * Created: 2025-05-19 04:59:21
 * Author: daparthi001
 */
import { z } from 'zod';

export const OrderSchema = z.object({
    id: z.string().uuid(),
    userId: z.string(),
    symbol: z.string().min(1),
    side: z.enum(['BUY', 'SELL']),
    quantity: z.number().positive(),
    orderType: z.enum(['MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT']),
    timeInForce: z.enum(['DAY', 'GTC', 'IOC', 'FOK']),
    price: z.number().optional(),
    stopPrice: z.number().optional(),
    status: z.enum([
        'PENDING',
        'ACCEPTED',
        'REJECTED',
        'PARTIAL_FILLED',
        'FILLED',
        'CANCELLED',
        'EXPIRED'
    ]),
    createdAt: z.string().datetime(),
    updatedAt: z.string().datetime(),
    executedPrice: z.number().optional(),
    executedQuantity: z.number().optional(),
    executionTime: z.string().datetime().optional()
});

export type Order = z.infer<typeof OrderSchema>;

export function validateOrder(order: unknown): Order {
    return OrderSchema.parse(order);
}