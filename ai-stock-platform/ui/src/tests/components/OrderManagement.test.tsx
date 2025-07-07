/**
 * Order Management Component Tests
 * Created: 2025-05-19 04:55:47
 * Author: daparthi001
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import configureStore from 'redux-mock-store';
import thunk from 'redux-thunk';
import OrderManagement from '../../components/orders/OrderManagement';

const mockStore = configureStore([thunk.default]);

describe('OrderManagement Component', () => {
    let store: any;

    beforeEach(() => {
        store = mockStore({
            orders: {
                orders: [],
                loading: false,
                error: null,
                selectedOrder: null
            }
        });
    });

    it('renders without crashing', () => {
        render(
            <Provider store={store}>
                <OrderManagement />
            </Provider>
        );
        expect(screen.getByText('Order Management')).toBeInTheDocument();
    });

    it('displays order form correctly', () => {
        render(
            <Provider store={store}>
                <OrderManagement />
            </Provider>
        );

        expect(screen.getByLabelText('Symbol')).toBeInTheDocument();
        expect(screen.getByLabelText('Quantity')).toBeInTheDocument();
        expect(screen.getByLabelText('Order Type')).toBeInTheDocument();
    });

    it('handles order submission', async () => {
        render(
            <Provider store={store}>
                <OrderManagement />
            </Provider>
        );

        fireEvent.change(screen.getByLabelText('Symbol'), {
            target: { value: 'AAPL' }
        });
        fireEvent.change(screen.getByLabelText('Quantity'), {
            target: { value: '100' }
        });
        fireEvent.click(screen.getByText('Place Order'));

        await waitFor(() => {
            const actions = store.getActions();
            expect(actions).toContainEqual(
                expect.objectContaining({
                    type: 'orders/createOrderStart'
                })
            );
        });
    });

    it('displays error message when order creation fails', async () => {
        store = mockStore({
            orders: {
                orders: [],
                loading: false,
                error: 'Failed to create order',
                selectedOrder: null
            }
        });

        render(
            <Provider store={store}>
                <OrderManagement />
            </Provider>
        );

        expect(screen.getByText('Failed to create order')).toBeInTheDocument();
    });
});