/**
 * Order Validation Hook
 * Created: 2025-05-19 05:00:36
 * Author: daparthi001
 */
import { useCallback } from 'react';
import { z } from 'zod';
import { OrderSchema } from '../types/order';

export const useOrderValidation = () => {
    const validateOrderData = useCallback((data: unknown) => {
        try {
            return OrderSchema.parse(data);
        } catch (error) {
            if (error instanceof z.ZodError) {
                const issues = error.issues.map((issue) => ({
                    path: issue.path.join('.'),
                    message: issue.message,
                }));
                throw new Error(
                    `Validation failed: ${JSON.stringify(issues, null, 2)}`
                );
            }
            throw error;
        }
    }, []);

    const validateQuantity = useCallback((quantity: number) => {
        if (quantity <= 0) {
            throw new Error('Quantity must be greater than 0');
        }
        if (!Number.isInteger(quantity)) {
            throw new Error('Quantity must be a whole number');
        }
        return true;
    }, []);

    const validatePrice = useCallback((price: number) => {
        if (price <= 0) {
            throw new Error('Price must be greater than 0');
        }
        if (isNaN(price)) {
            throw new Error('Price must be a valid number');
        }
        return true;
    }, []);

    return {
        validateOrderData,
        validateQuantity,
        validatePrice,
    };
};