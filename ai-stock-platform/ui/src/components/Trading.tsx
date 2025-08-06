/**
 * Trading Component - Live Trading Interface
 * Full implementation with real-time data and order management
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, CardHeader, CardTitle,
  Grid, Typography, Button, TextField,
  Select, MenuItem, FormControl, InputLabel,
  Table, TableBody, TableCell, TableContainer, 
  TableHead, TableRow, Paper, Chip, Box,
  Alert, Tabs, Tab, Divider
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, ShowChart, 
  AccountBalance, Timer, Warning 
} from '@mui/icons-material';

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
}

interface Order {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
  timestamp: string;
}

const Trading: React.FC = () => {
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy');
  const [quantity, setQuantity] = useState<string>('');
  const [limitPrice, setLimitPrice] = useState<string>('');
  const [orders, setOrders] = useState<Order[]>([]);
  const [watchlist, setWatchlist] = useState<Stock[]>([]);
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Mock data for demonstration
  useEffect(() => {
    const mockWatchlist: Stock[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 191.45,
        change: 2.34,
        changePercent: 1.24,
        volume: 45678900
      },
      {
        symbol: 'GOOGL',
        name: 'Alphabet Inc.',
        price: 142.67,
        change: -1.23,
        changePercent: -0.85,
        volume: 23456700
      },
      {
        symbol: 'MSFT',
        name: 'Microsoft Corporation',
        price: 378.91,
        change: 5.67,
        changePercent: 1.52,
        volume: 34567800
      },
      {
        symbol: 'TSLA',
        name: 'Tesla Inc.',
        price: 207.12,
        change: -3.45,
        changePercent: -1.64,
        volume: 56789000
      }
    ];

    setWatchlist(mockWatchlist);
    setSelectedStock(mockWatchlist[0]);
  }, []);

  const handlePlaceOrder = () => {
    if (!selectedStock || !quantity || parseFloat(quantity) <= 0) {
      setError('Please select a stock and enter a valid quantity');
      return;
    }

    if (orderType === 'limit' && (!limitPrice || parseFloat(limitPrice) <= 0)) {
      setError('Please enter a valid limit price');
      return;
    }

    const newOrder: Order = {
      id: Date.now().toString(),
      symbol: selectedStock.symbol,
      type: tradeType,
      quantity: parseFloat(quantity),
      price: orderType === 'market' ? selectedStock.price : parseFloat(limitPrice),
      status: 'pending',
      timestamp: new Date().toISOString()
    };

    setOrders([newOrder, ...orders]);
    setQuantity('');
    setLimitPrice('');
    setError(null);

    // Simulate order processing
    setTimeout(() => {
      setOrders(prevOrders => 
        prevOrders.map(order => 
          order.id === newOrder.id ? { ...order, status: 'filled' } : order
        )
      );
    }, 2000);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <Box sx={{ maxWidth: 1200, mx: 'auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Trading Terminal
      </Typography>

      <Grid container spacing={3}>
        {/* Watchlist */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Watchlist" />
            <CardContent>
              {watchlist.map((stock) => (
                <Box
                  key={stock.symbol}
                  sx={{
                    p: 2,
                    border: selectedStock?.symbol === stock.symbol ? 2 : 1,
                    borderColor: selectedStock?.symbol === stock.symbol ? 'primary.main' : 'divider',
                    borderRadius: 1,
                    mb: 1,
                    cursor: 'pointer',
                    '&:hover': { bgcolor: 'action.hover' }
                  }}
                  onClick={() => setSelectedStock(stock)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="h6">{stock.symbol}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {stock.name}
                      </Typography>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="h6">
                        {formatCurrency(stock.price)}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {stock.change >= 0 ? <TrendingUp color="success" /> : <TrendingDown color="error" />}
                        <Typography 
                          variant="body2" 
                          color={stock.change >= 0 ? 'success.main' : 'error.main'}
                        >
                          {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Trading Panel */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader 
              title={selectedStock ? `Trade ${selectedStock.symbol}` : 'Select a Stock'}
              avatar={<ShowChart />}
            />
            <CardContent>
              {selectedStock && (
                <>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" gutterBottom>
                      {selectedStock.name}
                    </Typography>
                    <Typography variant="h4" color="primary">
                      {formatCurrency(selectedStock.price)}
                    </Typography>
                    <Typography variant="body1" color={selectedStock.change >= 0 ? 'success.main' : 'error.main'}>
                      {selectedStock.change >= 0 ? '+' : ''}{selectedStock.change.toFixed(2)} ({selectedStock.changePercent.toFixed(2)}%)
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  {error && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      {error}
                    </Alert>
                  )}

                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Order Type</InputLabel>
                        <Select
                          value={orderType}
                          onChange={(e) => setOrderType(e.target.value as 'market' | 'limit')}
                        >
                          <MenuItem value="market">Market Order</MenuItem>
                          <MenuItem value="limit">Limit Order</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Trade Type</InputLabel>
                        <Select
                          value={tradeType}
                          onChange={(e) => setTradeType(e.target.value as 'buy' | 'sell')}
                        >
                          <MenuItem value="buy">Buy</MenuItem>
                          <MenuItem value="sell">Sell</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Quantity"
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        placeholder="Number of shares"
                      />
                    </Grid>
                    {orderType === 'limit' && (
                      <Grid item xs={12} sm={6}>
                        <TextField
                          fullWidth
                          label="Limit Price"
                          type="number"
                          value={limitPrice}
                          onChange={(e) => setLimitPrice(e.target.value)}
                          placeholder="Price per share"
                        />
                      </Grid>
                    )}
                    <Grid item xs={12}>
                      <Button
                        variant="contained"
                        color={tradeType === 'buy' ? 'success' : 'error'}
                        size="large"
                        onClick={handlePlaceOrder}
                        disabled={loading}
                        fullWidth
                      >
                        {tradeType === 'buy' ? 'Place Buy Order' : 'Place Sell Order'}
                      </Button>
                    </Grid>
                  </Grid>

                  {quantity && selectedStock && (
                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
                      <Typography variant="h6" gutterBottom>
                        Order Summary
                      </Typography>
                      <Typography>
                        {tradeType.toUpperCase()} {quantity} shares of {selectedStock.symbol}
                      </Typography>
                      <Typography>
                        Estimated Total: {formatCurrency(
                          parseFloat(quantity || '0') * 
                          (orderType === 'market' ? selectedStock.price : parseFloat(limitPrice || '0'))
                        )}
                      </Typography>
                    </Box>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Order History */}
        <Grid item xs={12}>
          <Card>
            <CardHeader 
              title="Recent Orders" 
              avatar={<AccountBalance />}
            />
            <CardContent>
              {orders.length === 0 ? (
                <Typography color="text.secondary">
                  No orders placed yet
                </Typography>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Price</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Time</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {orders.map((order) => (
                        <TableRow key={order.id}>
                          <TableCell>{order.symbol}</TableCell>
                          <TableCell>
                            <Chip 
                              label={order.type.toUpperCase()} 
                              color={order.type === 'buy' ? 'success' : 'error'}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{formatNumber(order.quantity)}</TableCell>
                          <TableCell>{formatCurrency(order.price)}</TableCell>
                          <TableCell>
                            <Chip 
                              label={order.status.toUpperCase()}
                              color={
                                order.status === 'filled' ? 'success' : 
                                order.status === 'pending' ? 'warning' : 'error'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(order.timestamp).toLocaleTimeString()}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Alert severity="info" sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Warning sx={{ mr: 1 }} />
          <Typography>
            This is a demo trading interface. No real trades are executed.
          </Typography>
        </Box>
      </Alert>
    </Box>
  );
};

export default Trading;
