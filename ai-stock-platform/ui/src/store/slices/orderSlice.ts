/**
 * Order Redux Slice
 * Created: 2025-05-19 04:53:30
 * Author: daparthi001
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Order, OrderStatus } from '../../types/order';

interface OrderState {
    orders: Order[];
    loading: boolean;
    error: string | null;
    selectedOrder: Order | null;
}

const initialState: OrderState = {
    orders: [],
    loading: false,
    error: null,
    selectedOrder: null
};

const orderSlice = createSlice({
    name: 'orders',
    initialState,
    reducers: {
        fetchOrdersStart(state) {
            state.loading = true;
            state.error = null;
        },
        fetchOrdersSuccess(state, action: PayloadAction<Order[]>) {
            state.orders = action.payload;
            state.loading = false;
            state.error = null;
        },
        fetchOrdersFailure(state, action: PayloadAction<string>) {
            state.loading = false;
            state.error = action.payload;
        },
        createOrderStart(state) {
            state.loading = true;
            state.error = null;
        },
        createOrderSuccess(state, action: PayloadAction<Order>) {
            state.orders.unshift(action.payload);
            state.loading = false;
            state.error = null;
        },
        createOrderFailure(state, action: PayloadAction<string>) {
            state.loading = false;
            state.error = action.payload;
        },
        updateOrderStatus(state, action: PayloadAction<{ 
            orderId: string;
            status: OrderStatus;
            executionDetails?: any;
        }>) {
            const order = state.orders.find(o => o.id === action.payload.orderId);
            if (order) {
                order.status = action.payload.status;
                if (action.payload.executionDetails) {
                    Object.assign(order, action.payload.executionDetails);
                }
            }
        },
        setSelectedOrder(state, action: PayloadAction<Order | null>) {
            state.selectedOrder = action.payload;
        }
    }
});

export const {
    fetchOrdersStart,
    fetchOrdersSuccess,
    fetchOrdersFailure,
    createOrderStart,
    createOrderSuccess,
    createOrderFailure,
    updateOrderStatus,
    setSelectedOrder
} = orderSlice.actions;

export default orderSlice.reducer;