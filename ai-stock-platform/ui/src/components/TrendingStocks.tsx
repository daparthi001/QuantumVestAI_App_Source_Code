import React from 'react';
import {
  Card, CardContent, Typography, Skeleton,
  Box, List, ListItem, ListItemText, ListItemIcon,
  Divider, Avatar, IconButton
} from '@mui/material';
import { 
  ArrowUpward, ArrowDownward, TrendingUp, 
  Refresh 
} from '@mui/icons-material';
import { green, red, grey, blue } from '@mui/material/colors';
import { formatPrice, formatChange, formatPercentage } from '../utils/formatters';
import useTrendingStocks from '../hooks/useTrendingStocks';

interface TrendingStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  change_percent: number;
  volume: number;
  last_updated: string;
}


interface TrendingStocksProps {
  limit?: number;
  showHeader?: boolean;
  compact?: boolean;
}

const TrendingStocks: React.FC<TrendingStocksProps> = ({
  limit = 10,
  showHeader = true,
  compact = false
}) => {
  const { stocks, lastUpdate, loading, error } = useTrendingStocks(limit);
  const [refreshing, setRefreshing] = React.useState<boolean>(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => setRefreshing(false), 1000);
  };

  const getPriceChangeIcon = (changePercent: number) => {
    if (changePercent > 0) {
      return <ArrowUpward style={{ color: green[500], fontSize: '16px' }} />;
    } else if (changePercent < 0) {
      return <ArrowDownward style={{ color: red[500], fontSize: '16px' }} />;
    }
    return null;
  };

  const getPriceChangeColor = (changePercent: number) => {
    if (changePercent > 0) {
      return green[600];
    } else if (changePercent < 0) {
      return red[600];
    }
    return grey[600];
  };

  const getVolumeDisplay = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(1)}M`;
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(1)}K`;
    }
    return volume.toString();
  };

  const formatLastUpdated = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      
      if (diffMinutes < 1) {
        return 'Just now';
      } else if (diffMinutes < 60) {
        return `${diffMinutes}m ago`;
      } else {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
    } catch {
      return 'Unknown';
    }
  };

  if (loading) {
    return (
      <Card sx={{ minHeight: compact ? 300 : 400 }}>
        <CardContent>
          {showHeader && (
            <Box display="flex" alignItems="center" mb={2}>
              <TrendingUp sx={{ mr: 1, color: blue[500] }} />
              <Typography variant="h6" component="h2">
                Trending Stocks
              </Typography>
            </Box>
          )}
          <List>
            {Array.from({ length: limit }).map((_, idx) => (
              <ListItem key={idx}>
                <ListItemIcon>
                  <Skeleton variant="circular" width={32} height={32} />
                </ListItemIcon>
                <ListItemText
                  primary={<Skeleton width="60%" />}
                  secondary={<Skeleton width="40%" />}
                />
              </ListItem>
            ))}
          </List>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ minHeight: compact ? 300 : 400 }}>
        <CardContent>
          {showHeader && (
            <Box display="flex" alignItems="center" mb={2}>
              <TrendingUp sx={{ mr: 1, color: blue[500] }} />
              <Typography variant="h6" component="h2">
                Trending Stocks
              </Typography>
            </Box>
          )}
          <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height={200}>
            <Typography color="error" variant="body1" gutterBottom>
              {error}
            </Typography>
            <IconButton onClick={handleRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ minHeight: compact ? 300 : 400 }}>
      <CardContent>
        {showHeader && (
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Box display="flex" alignItems="center">
              <TrendingUp sx={{ mr: 1, color: blue[500] }} />
              <Typography variant="h6" component="h2">
                Trending Stocks
              </Typography>
            </Box>
            <Box display="flex" alignItems="center">
              <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>
                {formatLastUpdated(lastUpdate)}
              </Typography>
              <IconButton 
                onClick={handleRefresh} 
                size="small" 
                disabled={refreshing}
                color="primary"
              >
                <Refresh sx={{ fontSize: '18px' }} />
              </IconButton>
            </Box>
          </Box>
        )}

        <List sx={{ py: 0 }}>
          {stocks.map((stock, index) => (
            <React.Fragment key={stock.symbol}>
              <ListItem 
                sx={{ 
                  py: compact ? 0.5 : 1,
                  px: 0,
                  '&:hover': { backgroundColor: 'action.hover' }
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  <Avatar 
                    sx={{ 
                      width: 32, 
                      height: 32, 
                      fontSize: '12px',
                      bgcolor: blue[100],
                      color: blue[800]
                    }}
                  >
                    {stock.symbol.substring(0, 2)}
                  </Avatar>
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="subtitle2" component="span" fontWeight="bold">
                          {stock.symbol}
                        </Typography>
                        {!compact && (
                          <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                            {stock.name}
                          </Typography>
                        )}
                      </Box>
                      <Box display="flex" alignItems="center">
                        <Typography variant="subtitle2" fontWeight="bold" sx={{ mr: 1 }}>
                          ${formatPrice(stock.price)}
                        </Typography>
                        {getPriceChangeIcon(stock.change_percent)}
                      </Box>
                    </Box>
                  }
                  secondary={
                    <Box display="flex" justifyContent="space-between" alignItems="center" mt={0.5}>
                      <Box display="flex" alignItems="center">
                        <Typography 
                          variant="caption" 
                          sx={{ 
                            color: getPriceChangeColor(stock.change_percent),
                            fontWeight: 'bold'
                          }}
                        >
                          {formatChange(stock.change)} ({formatPercentage(stock.change_percent)})
                        </Typography>
                      </Box>
                      {!compact && (
                        <Typography variant="caption" color="text.secondary">
                          Vol: {getVolumeDisplay(stock.volume)}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < stocks.length - 1 && (
                <Divider variant="inset" component="li" />
              )}
            </React.Fragment>
          ))}
        </List>

        {stocks.length === 0 && (
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <Typography color="text.secondary">
              No trending stocks data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default TrendingStocks;