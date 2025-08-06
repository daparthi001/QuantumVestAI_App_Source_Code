/**
 * Portfolio Summary Component
 * Displays portfolio value, performance, and allocation
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, CardHeader, 
  Grid, Typography, Box, LinearProgress,
  Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, PieChart, 
  AccountBalance, Timeline 
} from '@mui/icons-material';

interface PortfolioData {
  totalValue: number;
  totalGain: number;
  totalGainPercent: number;
  dayChange: number;
  dayChangePercent: number;
  cashBalance: number;
}

interface Holding {
  symbol: string;
  name: string;
  shares: number;
  currentPrice: number;
  totalValue: number;
  gainLoss: number;
  gainLossPercent: number;
  allocation: number;
}

const PortfolioSummary: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock data - in a real app, this would come from an API
    const mockPortfolio: PortfolioData = {
      totalValue: 125750.45,
      totalGain: 8750.45,
      totalGainPercent: 7.48,
      dayChange: 1234.56,
      dayChangePercent: 0.99,
      cashBalance: 5432.10
    };

    const mockHoldings: Holding[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        shares: 50,
        currentPrice: 191.45,
        totalValue: 9572.50,
        gainLoss: 572.50,
        gainLossPercent: 6.35,
        allocation: 25.3
      },
      {
        symbol: 'GOOGL',
        name: 'Alphabet Inc.',
        shares: 25,
        currentPrice: 142.67,
        totalValue: 3566.75,
        gainLoss: -233.25,
        gainLossPercent: -6.14,
        allocation: 15.8
      },
      {
        symbol: 'MSFT',
        name: 'Microsoft Corporation',
        shares: 30,
        currentPrice: 378.91,
        totalValue: 11367.30,
        gainLoss: 867.30,
        gainLossPercent: 8.26,
        allocation: 28.4
      },
      {
        symbol: 'TSLA',
        name: 'Tesla Inc.',
        shares: 15,
        currentPrice: 207.12,
        totalValue: 3106.80,
        gainLoss: -193.20,
        gainLossPercent: -5.85,
        allocation: 12.7
      }
    ];

    setTimeout(() => {
      setPortfolio(mockPortfolio);
      setHoldings(mockHoldings);
      setLoading(false);
    }, 1000);
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>Portfolio Summary</Typography>
        <LinearProgress />
      </Box>
    );
  }

  if (!portfolio) {
    return (
      <Typography variant="body1" color="text.secondary">
        Portfolio data not available
      </Typography>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
        <AccountBalance sx={{ mr: 1 }} />
        Portfolio Summary
      </Typography>

      {/* Portfolio Overview */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Value
              </Typography>
              <Typography variant="h4" color="primary">
                {formatCurrency(portfolio.totalValue)}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                {portfolio.dayChange >= 0 ? (
                  <TrendingUp sx={{ color: 'success.main', mr: 1 }} />
                ) : (
                  <TrendingDown sx={{ color: 'error.main', mr: 1 }} />
                )}
                <Typography
                  color={portfolio.dayChange >= 0 ? 'success.main' : 'error.main'}
                  variant="body2"
                >
                  {portfolio.dayChange >= 0 ? '+' : ''}{formatCurrency(portfolio.dayChange)} ({portfolio.dayChangePercent.toFixed(2)}%)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Gain/Loss
              </Typography>
              <Typography 
                variant="h4" 
                color={portfolio.totalGain >= 0 ? 'success.main' : 'error.main'}
              >
                {portfolio.totalGain >= 0 ? '+' : ''}{formatCurrency(portfolio.totalGain)}
              </Typography>
              <Typography
                color={portfolio.totalGain >= 0 ? 'success.main' : 'error.main'}
                variant="body2"
              >
                {portfolio.totalGainPercent.toFixed(2)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cash Balance
              </Typography>
              <Typography variant="h4">
                {formatCurrency(portfolio.cashBalance)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Available for trading
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Holdings
              </Typography>
              <Typography variant="h4">
                {holdings.length}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Different positions
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Holdings Table */}
      <Card>
        <CardHeader 
          title="Holdings" 
          titleTypographyProps={{ variant: 'h6' }}
          avatar={<PieChart />}
        />
        <CardContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Shares</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell align="right">Value</TableCell>
                  <TableCell align="right">Gain/Loss</TableCell>
                  <TableCell align="right">Allocation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {holdings.map((holding) => (
                  <TableRow key={holding.symbol}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {holding.symbol}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {holding.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      {holding.shares}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(holding.currentPrice)}
                    </TableCell>
                    <TableCell align="right">
                      {formatCurrency(holding.totalValue)}
                    </TableCell>
                    <TableCell align="right">
                      <Box>
                        <Typography
                          color={holding.gainLoss >= 0 ? 'success.main' : 'error.main'}
                          variant="body2"
                        >
                          {holding.gainLoss >= 0 ? '+' : ''}{formatCurrency(holding.gainLoss)}
                        </Typography>
                        <Typography
                          color={holding.gainLoss >= 0 ? 'success.main' : 'error.main'}
                          variant="caption"
                        >
                          ({holding.gainLossPercent.toFixed(2)}%)
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end' }}>
                        <Box sx={{ width: 60, mr: 1 }}>
                          <LinearProgress 
                            variant="determinate" 
                            value={holding.allocation} 
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                        <Typography variant="body2">
                          {holding.allocation.toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default PortfolioSummary;
