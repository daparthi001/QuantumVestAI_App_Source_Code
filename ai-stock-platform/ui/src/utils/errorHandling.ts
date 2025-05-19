/**
 * Error Handling Utilities
 * Created: 2025-05-19 04:55:47
 * Author: daparthi001
 */
import { toast } from 'react-toastify';

export class OrderError extends Error {
    constructor(
        message: string,
        public code: string,
        public details?: any
    ) {
        super(message);
        this.name = 'OrderError';
    }
}

export const handleOrderError = (error: any) => {
    if (error instanceof OrderError) {
        switch (error.code) {
            case 'VALIDATION_ERROR':
                toast.error(`Validation Error: ${error.message}`);
                break;
            case 'INSUFFICIENT_FUNDS':
                toast.error('Insufficient funds for this order');
                break;
            case 'MARKET_CLOSED':
                toast.warning('Market is currently closed');
                break;
            case 'CONNECTION_ERROR':
                toast.error('Connection error. Please try again');
                break;
            default:
                toast.error(`Error: ${error.message}`);
        }
    } else {
        toast.error('An unexpected error occurred');
        console.error('Unhandled error:', error);
    }
};