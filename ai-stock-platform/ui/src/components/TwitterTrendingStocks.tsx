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
}

const TwitterTrendingStocks: React.FC = () => {
  const [trending, setTrending] = useState<TrendingStock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrending = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await axios.get('/api/social/twitter/trending');
        setTrending(response.data.trending_tickers);
      } catch (err) {
        setError('Failed to load trending stocks');
        console.error(err);
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

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6">Trending on Twitter</Typography>
          <Box display="flex" justifyContent="center" my={3}>
            <CircularProgress />
          </Box>
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
            <Typography color="error">{error || 'No trending stocks available'}</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>Trending Stocks on Twitter</Typography>
        
        <List disablePadding>
          {trending.map((stock, index) => (
            <React.Fragment key={stock.ticker}>
              {index > 0 && <Divider variant="inset" component="li" />}
              <ListItem 
                component={Link} 
                to={`/stocks/${stock.ticker}`}
                sx={{ alignItems: 'center', cursor: 'pointer' }}
              >
                <Avatar sx={{ bgcolor: grey[200], width: 36, height: 36, mr: 2 }}>${stock.ticker}</Avatar>
                <ListItemText 
                  primary={stock.ticker} 
                  secondary={`${stock.tweet_count} tweets • ${stock.engagement} engagement`} 
                />
                <ListItemIcon style={{ minWidth: 'auto' }}>
                  {getSentimentIcon(stock.sentiment)}
                </ListItemIcon>
                <Chip 
                  size="small" 
                  label={stock.sentiment > 0 ? 'Bullish' : stock.sentiment < 0 ? 'Bearish' : 'Neutral'} 
                  style={{ 
                    backgroundColor: stock.sentiment > 0 ? green[100] : stock.sentiment < 0 ? red[100] : grey[100],
                    color: stock.sentiment > 0 ? green[800] : stock.sentiment < 0 ? red[800] : grey[800],
                  }}
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      </CardContent>
    </Card>
  );
};

export default TwitterTrendingStocks;