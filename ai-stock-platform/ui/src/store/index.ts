/**
 * Store Index
 * Created: 2025-01-08
 * Author: daparthi001
 */
import { configureStore } from '@reduxjs/toolkit';
import orderReducer from './slices/orderSlice';

// Configure the store
export const store = configureStore({
  reducer: {
    orders: orderReducer,
  },
});

// Export the main store components
export * from './orderStore';
export * from './types';

// Export actions
export * from './actions/orderActions';

// Export slices
export * from './slices/orderSlice';

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
