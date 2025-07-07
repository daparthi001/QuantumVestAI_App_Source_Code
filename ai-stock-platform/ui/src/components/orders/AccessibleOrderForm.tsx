/**
 * Accessible Order Form Component
 * Created: 2025-05-19 04:57:00
 * Author: daparthi001
 */
import React, { useRef, useEffect } from 'react';
import {
    TextField,
    Select,
    MenuItem,
    Button,
    FormControl,
    InputLabel,
    FormHelperText
} from '@mui/material';
import { useForm } from 'react-hook-form';
import { Order } from '../../types/order';

interface AccessibleOrderFormProps {
    onSubmit: (data: Partial<Order>) => Promise<void>;
    initialData?: Order | null;
}

export const AccessibleOrderForm: React.FC<AccessibleOrderFormProps> = ({
    onSubmit,
    initialData
}) => {
    const { register, handleSubmit, formState: { errors } } = useForm({
        defaultValues: initialData || {}
    });
    const firstInput = useRef<HTMLInputElement>(null);

    useEffect(() => {
        if (firstInput.current) {
            firstInput.current.focus();
        }
    }, []);

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && e.shiftKey) {
            handleSubmit(onSubmit)();
        }
    };

    return (
        <form 
            onSubmit={handleSubmit(onSubmit)}
            className="order-form"
            aria-label="Order Entry Form"
            onKeyPress={handleKeyPress}
        >
            <TextField
                {...register('symbol', { required: 'Symbol is required' })}
                inputRef={firstInput}
                label="Symbol"
                error={!!errors.symbol}
                helperText={errors.symbol?.message}
                fullWidth
                margin="normal"
                inputProps={{
                    'aria-label': 'Trading Symbol',
                    'aria-describedby': 'symbol-helper-text'
                }}
            />

            <FormControl fullWidth margin="normal">
                <InputLabel id="side-label">Side</InputLabel>
                <Select
                    {...register('side', { required: 'Side is required' })}
                    labelId="side-label"
                    aria-label="Trading Side"
                >
                    <MenuItem value="BUY">Buy</MenuItem>
                    <MenuItem value="SELL">Sell</MenuItem>
                </Select>
                {errors.side && (
                    <FormHelperText error>
                        {errors.side.message}
                    </FormHelperText>
                )}
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
                inputProps={{
                    'aria-label': 'Order Quantity',
                    'aria-describedby': 'quantity-helper-text',
                    min: 0,
                    step: 1
                }}
            />

            {/* Add more accessible form fields */}

            <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                className="order-form__submit"
                aria-label="Submit Order"
            >
                {initialData ? 'Modify Order' : 'Place Order'}
            </Button>

            <div className="sr-only" role="status" aria-live="polite">
                {errors.symbol && 'Symbol field has an error'}
                {errors.quantity && 'Quantity field has an error'}
            </div>
        </form>
    );
};