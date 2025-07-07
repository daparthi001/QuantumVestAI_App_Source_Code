/**
 * Store Types
 * Created: 2025-01-08
 * Author: daparthi001
 */

// Import Order type first
import type { Order, OrderStatus, OrderType, TimeInForce, OrderSide } from '../types/order';

export interface RootState {
  orders: OrderState;
}

export interface OrderState {
  orders: Order[];
  loading: boolean;
  error: string | null;
  selectedOrder: Order | null;
}

// Re-export common types
export type { Order, OrderStatus, OrderType, TimeInForce, OrderSide };
