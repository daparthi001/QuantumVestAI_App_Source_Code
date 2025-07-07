/**
 * Order List Component
 * Created: 2025-05-19 04:53:30
 * Author: daparthi001
 */
import React, { useState } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    IconButton,
    Chip,
    TablePagination,
    Menu,
    MenuItem
} from '@mui/material';
import {
    MoreVert as MoreVertIcon,
    Cancel as CancelIcon,
    Edit as EditIcon
} from '@mui/icons-material';
import { Order, OrderStatus } from '../../types/order';
import { formatDateTime, formatCurrency } from '../../utils/formatters';

interface OrderListProps {
    orders: Order[];
    onSelect: (order: Order) => void;
    onCancel: (orderId: string) => void;
}

export const OrderList: React.FC<OrderListProps> = ({
    orders,
    onSelect,
    onCancel,
    onModify: _onModify

}) => {
    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(10);
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
    const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);

    const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, order: Order) => {
        setAnchorEl(event.currentTarget);
        setSelectedOrder(order);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
        setSelectedOrder(null);
    };

    const getStatusColor = (status: OrderStatus) => {
        switch (status) {
            case OrderStatus.FILLED:
                return 'success';
            case OrderStatus.PARTIAL_FILLED:
                return 'warning';
            case OrderStatus.CANCELLED:
                return 'error';
            default:
                return 'default';
        }
    };

    return (
        <Paper className="order-list">
            <TableContainer>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Time</TableCell>
                            <TableCell>Symbol</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell>Side</TableCell>
                            <TableCell>Quantity</TableCell>
                            <TableCell>Price</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Actions</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {orders
                            .slice(page * rowsPerPage, (page + 1) * rowsPerPage)
                            .map((order) => (
                                <TableRow key={order.id}>
                                    <TableCell>
                                        {formatDateTime(order.createdAt)}
                                    </TableCell>
                                    <TableCell>{order.symbol}</TableCell>
                                    <TableCell>{order.orderType}</TableCell>
                                    <TableCell>
                                        <Chip
                                            label={order.side}
                                            color={order.side === 'BUY' ? 'primary' : 'secondary'}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>{order.quantity}</TableCell>
                                    <TableCell>
                                        {order.price ? formatCurrency(order.price) : 'Market'}
                                    </TableCell>
                                    <TableCell>
                                        <Chip
                                            label={order.status}
                                            color={getStatusColor(order.status)}
                                            size="small"
                                        />
                                    </TableCell>
                                    <TableCell>
                                        <IconButton
                                            onClick={(e) => handleMenuOpen(e, order)}
                                            disabled={!canModifyOrder(order)}
                                        >
                                            <MoreVertIcon />
                                        </IconButton>
                                    </TableCell>
                                </TableRow>
                            ))}
                    </TableBody>
                </Table>
            </TableContainer>
            
            <TablePagination
                component="div"
                count={orders.length}
                page={page}
                onPageChange={(_, newPage) => setPage(newPage)}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => {
                    setRowsPerPage(parseInt(e.target.value, 10));
                    setPage(0);
                }}
            />

            <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleMenuClose}
            >
                <MenuItem
                    onClick={() => {
                        if (selectedOrder) {
                            onSelect(selectedOrder);
                            handleMenuClose();
                        }
                    }}
                >
                    <EditIcon fontSize="small" /> Modify
                </MenuItem>
                <MenuItem
                    onClick={() => {
                        if (selectedOrder) {
                            onCancel(selectedOrder.id);
                            handleMenuClose();
                        }
                    }}
                >
                    <CancelIcon fontSize="small" /> Cancel
                </MenuItem>
            </Menu>
        </Paper>
    );
};

// Helper function to determine if an order can be modified
function canModifyOrder(order: Order): boolean {
    return order.status === OrderStatus.PENDING || order.status === OrderStatus.ACCEPTED;
}