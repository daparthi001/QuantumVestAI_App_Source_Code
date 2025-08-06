/**
 * Sentiment Chart Component
 * Displays market sentiment analysis with interactive charts
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect } from 'react';
import { 
  Card, CardContent, CardHeader, 
  Typography, Box, Select, MenuItem, FormControl, 
  InputLabel, Grid, Chip, LinearProgress
} from '@mui/material';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, ResponsiveContainer, AreaChart, Area,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Psychology, 
  Timeline, PieChart as PieChartIcon 
} from '@mui/icons-material';

interface SentimentData {
  timestamp: string;
  overallSentiment: number;
  bullishSentiment: number;
  bearishSentiment: number;
  neutralSentiment: number;
  volume: number;
}

interface SectorSentiment {
  sector: string;
  sentiment: number;
  color: string;
}

const SentimentChart: React.FC = () => {
  const [timeframe, setTimeframe] = useState<string>('1D');
  const [sentimentData, setSentimentData] = useState<SentimentData[]>([]);
  const [sectorData, setSectorData] = useState<SectorSentiment[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentSentiment, setCurrentSentiment] = useState<number>(0);

  const timeframes = ['1D', '5D', '1M', '3M', '1Y'];

  useEffect(() => {
    loadSentimentData();
  }, [timeframe]);

  const loadSentimentData = () => {
    setLoading(true);

    // Mock data generation - in a real app, this would come from sentiment analysis API
    const generateData = () => {
      const now = new Date();
      const dataPoints = timeframe === '1D' ? 24 : timeframe === '5D' ? 120 : 30;
      const interval = timeframe === '1D' ? 60 : timeframe === '5D' ? 60 : 1440; // minutes
      
      return Array.from({ length: dataPoints }, (_, i) => {
        const timestamp = new Date(now.getTime() - (dataPoints - 1 - i) * interval * 60 * 1000);
        const basesentiment = 0.6 + Math.sin(i * 0.1) * 0.2;
        const volatility = 0.1;
        
        return {
          timestamp: timestamp.toISOString(),
          overallSentiment: Math.max(0, Math.min(1, basesentiment + (Math.random() - 0.5) * volatility)),
          bullishSentiment: Math.max(0, Math.min(1, basesentiment + 0.1 + (Math.random() - 0.5) * volatility)),
          bearishSentiment: Math.max(0, Math.min(1, 1 - basesentiment + (Math.random() - 0.5) * volatility)),
          neutralSentiment: Math.max(0, Math.min(1, 0.5 + (Math.random() - 0.5) * 0.2)),
          volume: Math.floor(1000 + Math.random() * 5000)
        };
      });
    };

    const mockSectorData: SectorSentiment[] = [
      { sector: 'Technology', sentiment: 0.75, color: '#2196F3' },
      { sector: 'Healthcare', sentiment: 0.68, color: '#4CAF50' },
      { sector: 'Finance', sentiment: 0.45, color: '#FF9800' },
      { sector: 'Energy', sentiment: 0.32, color: '#F44336' },
      { sector: 'Consumer', sentiment: 0.58, color: '#9C27B0' },
      { sector: 'Industrial', sentiment: 0.51, color: '#607D8B' }
    ];

    setTimeout(() => {
      const data = generateData();
      setSentimentData(data);
      setSectorData(mockSectorData);
      setCurrentSentiment(data[data.length - 1]?.overallSentiment || 0);
      setLoading(false);
    }, 1000);
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    if (timeframe === '1D') {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (timeframe === '5D') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  const getSentimentLabel = (sentiment: number) => {
    if (sentiment > 0.7) return 'Very Bullish';
    if (sentiment > 0.6) return 'Bullish';
    if (sentiment > 0.4) return 'Neutral';
    if (sentiment > 0.3) return 'Bearish';
    return 'Very Bearish';
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.7) return 'success.main';
    if (sentiment > 0.6) return 'success.light';
    if (sentiment > 0.4) return 'warning.main';
    if (sentiment > 0.3) return 'error.light';
    return 'error.main';
  };

  if (loading) {
    return (
      <Box>
        <Typography variant="h6" gutterBottom>Market Sentiment</Typography>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center' }}>
          <Psychology sx={{ mr: 1 }} />
          Market Sentiment
        </Typography>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Timeframe</InputLabel>
          <Select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value)}
            label="Timeframe"
          >
            {timeframes.map((tf) => (
              <MenuItem key={tf} value={tf}>{tf}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Current Sentiment Overview */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Overall Sentiment
              </Typography>
              <Typography 
                variant="h3" 
                sx={{ color: getSentimentColor(currentSentiment) }}
              >
                {(currentSentiment * 100).toFixed(0)}%
              </Typography>
              <Chip 
                label={getSentimentLabel(currentSentiment)}
                color={currentSentiment > 0.5 ? 'success' : 'error'}
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={8}>
          <Card>
            <CardHeader title="Sentiment Trend" titleTypographyProps={{ variant: 'h6' }} />
            <CardContent>
              <ResponsiveContainer width="100%" height={200}>
                <AreaChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={formatTimestamp}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={[0, 1]} 
                    tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    labelFormatter={(label) => formatTimestamp(label)}
                    formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, 'Sentiment']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="overallSentiment" 
                    stroke="#2196F3" 
                    fill="#2196F3" 
                    fillOpacity={0.3}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Charts */}
      <Grid container spacing={3}>
        {/* Bull vs Bear Sentiment */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="Bull vs Bear Sentiment" titleTypographyProps={{ variant: 'h6' }} />
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sentimentData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={formatTimestamp}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis 
                    domain={[0, 1]} 
                    tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
                    tick={{ fontSize: 12 }}
                  />
                  <Tooltip 
                    labelFormatter={(label) => formatTimestamp(label)}
                    formatter={(value: number, name: string) => [
                      `${(value * 100).toFixed(1)}%`, 
                      name === 'bullishSentiment' ? 'Bullish' : 'Bearish'
                    ]}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="bullishSentiment" 
                    stroke="#4CAF50" 
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="bearishSentiment" 
                    stroke="#F44336" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Sector Sentiment */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader title="Sector Sentiment" titleTypographyProps={{ variant: 'h6' }} />
            <CardContent>
              {sectorData.map((sector) => (
                <Box key={sector.sector} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{sector.sector}</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {(sector.sentiment * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={sector.sentiment * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: sector.color
                      }
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default SentimentChart;
