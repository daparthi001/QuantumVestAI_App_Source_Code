/**
 * Order Form Component
 * Created: 2025-05-19 04:52:08
 * Author: daparthi001
 */
import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { 
    TextField,
    Select,
    MenuItem,
    Button,
    FormControl,
    InputLabel
} from '@mui/material';
import { Order, OrderType, TimeInForce, OrderSide } from '../../types/order';


interface OrderFormProps {
    onSubmit: (data: Partial<Order>) => Promise<void>;
    initialData?: Order | null;
}

export const OrderForm: React.FC<OrderFormProps> = ({ 
    onSubmit,
    initialData
}) => {
    const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
        defaultValues: initialData || {
            symbol: '',
            side: OrderSide.BUY,
            quantity: 0,
            orderType: OrderType.MARKET,
            timeInForce: TimeInForce.DAY,
            price: undefined,
            stopPrice: undefined
        }
    });

    const orderType = watch('orderType');

    useEffect(() => {
        if (initialData) {
            reset(initialData);
        }
    }, [initialData, reset]);

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="order-form">
            <TextField
                {...register('symbol', { required: 'Symbol is required' })}
                label="Symbol"
                error={!!errors.symbol}
                helperText={errors.symbol?.message}
                fullWidth
                margin="normal"
            />

            <FormControl fullWidth margin="normal">
                <InputLabel>Side</InputLabel>
                <Select {...register('side', { required: 'Side is required' })}>
                    <MenuItem value="BUY">Buy</MenuItem>
                    <MenuItem value="SELL">Sell</MenuItem>
                </Select>
            </FormControl>

            <TextField
                {...register('quantity', {
                    required: 'Quantity is required',
                    min: { value: 0, message: 'Quantity must be positive' }
                })}
                label="Quantity"
                type="number"
                error={!!errors.quantity}
                helperText={errors.quantity?.message}
                fullWidth
                margin="normal"
            />

            <FormControl fullWidth margin="normal">
                <InputLabel>Order Type</InputLabel>
                <Select
                    {...register('orderType', { required: 'Order type is required' })}
                >
                    <MenuItem value={OrderType.MARKET}>Market</MenuItem>
                    <MenuItem value={OrderType.LIMIT}>Limit</MenuItem>
                    <MenuItem value={OrderType.STOP}>Stop</MenuItem>
                    <MenuItem value={OrderType.STOP_LIMIT}>Stop Limit</MenuItem>
                </Select>
            </FormControl>

            {(orderType === OrderType.LIMIT || orderType === OrderType.STOP_LIMIT) && (
                <TextField
                    {...register('price', { required: 'Price is required' })}
                    label="Price"
                    type="number"
                    error={!!errors.price}
                    helperText={errors.price?.message}
                    fullWidth
                    margin="normal"
                />
            )}

            {(orderType === OrderType.STOP || orderType === OrderType.STOP_LIMIT) && (
                <TextField
                    {...register('stopPrice', { required: 'Stop price is required' })}
                    label="Stop Price"
                    type="number"
                    error={!!errors.stopPrice}
                    helperText={errors.stopPrice?.message}
                    fullWidth
                    margin="normal"
                />
            )}

            <FormControl fullWidth margin="normal">
                <InputLabel>Time in Force</InputLabel>
                <Select
                    {...register('timeInForce', { required: 'Time in force is required' })}
                >
                    <MenuItem value={TimeInForce.DAY}>Day</MenuItem>
                    <MenuItem value={TimeInForce.GTC}>Good Till Cancelled</MenuItem>
                    <MenuItem value={TimeInForce.IOC}>Immediate or Cancel</MenuItem>
                    <MenuItem value={TimeInForce.FOK}>Fill or Kill</MenuItem>
                </Select>
            </FormControl>

            <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                className="order-form__submit"
            >
                {initialData ? 'Modify Order' : 'Place Order'}
            </Button>
        </form>
    );
};