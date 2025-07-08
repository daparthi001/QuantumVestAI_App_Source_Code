import React, { useState, useEffect } from 'react';
import {
  Card, CardContent, Typography, CircularProgress,
  Box, List, ListItem, ListItemText, ListItemIcon,
  Divider, Chip, Avatar
} from '@mui/material';
import { ArrowUpward, ArrowDownward, Remove } from '@mui/icons-material';
import { green, red, grey } from '@mui/material/colors';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface TrendingStock {
  ticker: string;
  tweet_count: number;
  engagement: number;
  sentiment: number;
  volume_change?: number;
}

interface TrendingResponse {
  status: string;
  data?: {
    trending_tickers: TrendingStock[];
    count: number;
    last_updated: string;
    note?: string;
  };
  error?: string;
  message?: string;
}

const TwitterTrendingStocks: React.FC = () => {
  const [trending, setTrending] = useState<TrendingStock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [note, setNote] = useState<string>('');

  useEffect(() => {
    const fetchTrending = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Use the new social API endpoint structure
        const response = await axios.get('/api/social/twitter/trending');
        const data: TrendingResponse = response.data;
        
        if (data.status === 'success' && data.data) {
          setTrending(data.data.trending_tickers);
          setLastUpdated(data.data.last_updated);
          setNote(data.data.note || '');
        } else {
          setError(data.error || 'Failed to load trending stocks');
        }
      } catch (err: any) {
        console.error('Error fetching trending stocks:', err);
        if (err.response && err.response.status === 503) {
          setError('Twitter integration not configured. Using demo data.');
        } else {
          setError('Failed to load trending stocks');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTrending();
    
    // Refresh every 30 minutes
    const intervalId = setInterval(fetchTrending, 30 * 60 * 1000);
    
    return () => clearInterval(intervalId);
  }, []);

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return <ArrowUpward style={{ color: green[500] }} />;
    if (score < -0.1) return <ArrowDownward style={{ color: red[500] }} />;
    return <Remove style={{ color: grey[500] }} />;
  };

  const getSentimentLabel = (score: number): string => {
    if (score > 0.1) return 'Bullish';
    if (score < -0.1) return 'Bearish';
    return 'Neutral';
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return { backgroundColor: green[100], color: green[800] };
    if (score < -0.1) return { backgroundColor: red[100], color: red[800] };
    return { backgroundColor: grey[100], color: grey[800] };
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6">Trending on Twitter</Typography>
          <Box display="flex" justifyContent="center" my={3}>
            <CircularProgress />
          </Box>
          <Typography variant="body2" color="textSecondary" align="center">
            Loading trending stocks...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error || trending.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6">Trending on Twitter</Typography>
          <Box my={2}>
            <Typography color="error" variant="body2">
              {error || 'No trending stocks available'}
            </Typography>
            {note && (
              <Typography variant="caption" color="textSecondary" display="block" mt={1}>
                {note}
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6">Trending Stocks on Twitter</Typography>
          {note && (
            <Typography variant="caption" color="textSecondary">
              {note}
            </Typography>
          )}
        </Box>
        
        <List disablePadding>
          {trending.map((stock, index) => (
            <React.Fragment key={stock.ticker}>
              {index > 0 && <Divider variant="inset" component="li" />}
              <ListItem 
                component={Link} 
                to={`/stocks/${stock.ticker}`}
                sx={{ 
                  alignItems: 'center', 
                  cursor: 'pointer',
                  '&:hover': {
                    backgroundColor: grey[50]
                  }
                }}
              >
                <Avatar 
                  sx={{ 
                    bgcolor: grey[200], 
                    width: 36, 
                    height: 36, 
                    mr: 2,
                    fontSize: '0.75rem',
                    fontWeight: 'bold'
                  }}
                >
                  {stock.ticker}
                </Avatar>
                <ListItemText 
                  primary={
                    <Typography variant="subtitle2" fontWeight="bold">
                      {stock.ticker}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        {stock.tweet_count.toLocaleString()} tweets • {stock.engagement.toLocaleString()} engagement
                      </Typography>
                      {stock.volume_change !== undefined && (
                        <Typography variant="caption" color="textSecondary" display="block">
                          Volume change: {(stock.volume_change * 100).toFixed(1)}%
                        </Typography>
                      )}
                    </Box>
                  }
                />
                <Box display="flex" alignItems="center" gap={1}>
                  <ListItemIcon style={{ minWidth: 'auto' }}>
                    {getSentimentIcon(stock.sentiment)}
                  </ListItemIcon>
                  <Chip 
                    size="small" 
                    label={getSentimentLabel(stock.sentiment)}
                    style={getSentimentColor(stock.sentiment)}
                  />
                </Box>
              </ListItem>
            </React.Fragment>
          ))}
        </List>

        {/* Footer with last updated info */}
        <Box mt={2} pt={1} borderTop={1} borderColor="divider">
          <Typography variant="caption" color="textSecondary" align="center" display="block">
            Last updated: {lastUpdated ? new Date(lastUpdated).toLocaleString() : 'Unknown'}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default TwitterTrendingStocks;