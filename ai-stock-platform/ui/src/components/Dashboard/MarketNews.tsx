/**
 * Market News Component
 * Displays latest financial news and market updates
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, CardHeader, 
  Typography, Box, List, ListItem, ListItemText,
  Chip, Avatar, Divider, Link, LinearProgress,
  Button, Grid
} from '@mui/material';
import { 
  Article, TrendingUp, Schedule, 
  OpenInNew, Refresh 
} from '@mui/icons-material';

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  url: string;
  category: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  relatedSymbols: string[];
}

const MarketNews: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const categories = ['all', 'market', 'earnings', 'crypto', 'economy'];

  useEffect(() => {
    loadNews();
  }, []);

  const loadNews = () => {
    setLoading(true);
    
    // Mock data - in a real app, this would come from a news API
    const mockNews: NewsItem[] = [
      {
        id: '1',
        title: 'Federal Reserve Signals Potential Rate Cuts Amid Economic Uncertainty',
        summary: 'The Federal Reserve hints at possible interest rate adjustments as inflation shows signs of cooling and economic growth moderates.',
        source: 'Reuters',
        publishedAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
        url: '#',
        category: 'economy',
        sentiment: 'neutral',
        relatedSymbols: ['SPY', 'TLT']
      },
      {
        id: '2',
        title: 'Tech Giants Rally on AI Investment Surge',
        summary: 'Major technology companies see significant gains as investors bet on artificial intelligence and machine learning capabilities.',
        source: 'CNBC',
        publishedAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        url: '#',
        category: 'market',
        sentiment: 'positive',
        relatedSymbols: ['NVDA', 'MSFT', 'GOOGL']
      },
      {
        id: '3',
        title: 'Apple Reports Strong iPhone Sales Despite Market Headwinds',
        summary: 'Apple exceeds expectations with robust iPhone sales figures, driven by strong demand in emerging markets.',
        source: 'Bloomberg',
        publishedAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
        url: '#',
        category: 'earnings',
        sentiment: 'positive',
        relatedSymbols: ['AAPL']
      },
      {
        id: '4',
        title: 'Bitcoin Reaches New Monthly High Amid Institutional Interest',
        summary: 'Cryptocurrency markets surge as major institutions announce increased Bitcoin allocations and regulatory clarity improves.',
        source: 'CoinDesk',
        publishedAt: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
        url: '#',
        category: 'crypto',
        sentiment: 'positive',
        relatedSymbols: ['BTC-USD', 'ETH-USD']
      },
      {
        id: '5',
        title: 'Energy Sector Faces Volatility on Supply Chain Concerns',
        summary: 'Oil and gas companies experience mixed trading as geopolitical tensions raise supply chain uncertainty.',
        source: 'MarketWatch',
        publishedAt: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
        url: '#',
        category: 'market',
        sentiment: 'negative',
        relatedSymbols: ['XOM', 'CVX', 'COP']
      }
    ];

    setTimeout(() => {
      setNews(mockNews);
      setLoading(false);
    }, 1000);
  };

  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const publishedDate = new Date(dateString);
    const diffInMinutes = Math.floor((now.getTime() - publishedDate.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h ago`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d ago`;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'success';
      case 'negative': return 'error';
      default: return 'default';
    }
  };

  const filteredNews = selectedCategory === 'all' 
    ? news 
    : news.filter(item => item.category === selectedCategory);

  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>Market News</Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center' }}>
          <Article sx={{ mr: 1 }} />
          Market News
        </Typography>
        <Button startIcon={<Refresh />} onClick={loadNews} disabled={loading}>
          Refresh
        </Button>
      </Box>

      {/* Category Filter */}
      <Box sx={{ mb: 3 }}>
        <Grid container spacing={1}>
          {categories.map((category) => (
            <Grid item key={category}>
              <Chip
                label={category.charAt(0).toUpperCase() + category.slice(1)}
                variant={selectedCategory === category ? 'filled' : 'outlined'}
                color={selectedCategory === category ? 'primary' : 'default'}
                onClick={() => setSelectedCategory(category)}
                clickable
              />
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* News List */}
      <Card>
        <CardContent sx={{ p: 0 }}>
          <List disablePadding>
            {filteredNews.map((newsItem, index) => (
              <React.Fragment key={newsItem.id}>
                <ListItem sx={{ p: 3 }}>
                  <ListItemText
                    primary={
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {newsItem.title}
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                          <Chip
                            label={newsItem.category}
                            size="small"
                            variant="outlined"
                          />
                          <Chip
                            label={newsItem.sentiment}
                            size="small"
                            color={getSentimentColor(newsItem.sentiment) as any}
                            variant="outlined"
                          />
                          {newsItem.relatedSymbols.map((symbol) => (
                            <Chip
                              key={symbol}
                              label={symbol}
                              size="small"
                              variant="outlined"
                              sx={{ fontFamily: 'monospace' }}
                            />
                          ))}
                        </Box>
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="text.secondary" paragraph>
                          {newsItem.summary}
                        </Typography>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Avatar sx={{ width: 24, height: 24, mr: 1, fontSize: '0.75rem' }}>
                              {newsItem.source.charAt(0)}
                            </Avatar>
                            <Typography variant="caption" color="text.secondary">
                              {newsItem.source}
                            </Typography>
                            <Schedule sx={{ mx: 1, fontSize: 16 }} color="disabled" />
                            <Typography variant="caption" color="text.secondary">
                              {getTimeAgo(newsItem.publishedAt)}
                            </Typography>
                          </Box>
                          <Button
                            size="small"
                            endIcon={<OpenInNew />}
                            onClick={() => window.open(newsItem.url, '_blank')}
                          >
                            Read More
                          </Button>
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
                {index < filteredNews.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        </CardContent>
      </Card>

      {filteredNews.length === 0 && (
        <Typography variant="body1" color="text.secondary" sx={{ textAlign: 'center', mt: 3 }}>
          No news available for the selected category.
        </Typography>
      )}
    </Box>
  );
};

export default MarketNews;
