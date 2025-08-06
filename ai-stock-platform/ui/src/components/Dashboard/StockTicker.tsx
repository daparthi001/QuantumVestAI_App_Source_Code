/**
 * Stock Ticker Component
 * Displays real-time scrolling stock prices and market data
 * Updated: 2025-08-06
 * Author: QuantumVestAI Team
 */
import React, { useState, useEffect, useRef } from 'react';
import { 
  Box, Typography, Chip, IconButton, 
  Card, CardContent, Tooltip 
} from '@mui/material';
import { 
  TrendingUp, TrendingDown, Pause, 
  PlayArrow, Speed, BarChart 
} from '@mui/icons-material';

interface TickerStock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
}

const StockTicker: React.FC = () => {
  const [stocks, setStocks] = useState<TickerStock[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [speed, setSpeed] = useState<number>(50); // pixels per second
  const tickerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    // Mock data - in a real app, this would come from a real-time API
    const mockStocks: TickerStock[] = [
      {
        symbol: 'AAPL',
        name: 'Apple Inc.',
        price: 191.45,
        change: 2.34,
        changePercent: 1.24,
        volume: 45678900,
        marketCap: 2.94e12
      },
      {
        symbol: 'GOOGL',
        name: 'Alphabet Inc.',
        price: 142.67,
        change: -1.23,
        changePercent: -0.85,
        volume: 23456700,
        marketCap: 1.78e12
      },
      {
        symbol: 'MSFT',
        name: 'Microsoft Corporation',
        price: 378.91,
        change: 5.67,
        changePercent: 1.52,
        volume: 34567800,
        marketCap: 2.81e12
      },
      {
        symbol: 'TSLA',
        name: 'Tesla Inc.',
        price: 207.12,
        change: -3.45,
        changePercent: -1.64,
        volume: 56789000,
        marketCap: 659e9
      },
      {
        symbol: 'AMZN',
        name: 'Amazon.com Inc.',
        price: 187.65,
        change: 4.23,
        changePercent: 2.31,
        volume: 41234500,
        marketCap: 1.96e12
      },
      {
        symbol: 'NVDA',
        name: 'NVIDIA Corporation',
        price: 765.43,
        change: 15.67,
        changePercent: 2.09,
        volume: 67890123,
        marketCap: 1.88e12
      },
      {
        symbol: 'META',
        name: 'Meta Platforms Inc.',
        price: 345.67,
        change: -8.91,
        changePercent: -2.51,
        volume: 28901234,
        marketCap: 876e9
      },
      {
        symbol: 'NFLX',
        name: 'Netflix Inc.',
        price: 456.78,
        change: 12.34,
        changePercent: 2.78,
        volume: 19876543,
        marketCap: 203e9
      }
    ];

    setStocks(mockStocks);
  }, []);

  useEffect(() => {
    if (!isPaused && tickerRef.current) {
      const ticker = tickerRef.current;
      let position = ticker.scrollWidth;

      const animate = () => {
        if (!isPaused) {
          position -= speed / 60; // 60 FPS
          
          if (position < -ticker.scrollWidth) {
            position = ticker.offsetWidth;
          }
          
          ticker.style.transform = `translateX(${position}px)`;
        }
        
        animationRef.current = requestAnimationFrame(animate);
      };

      animationRef.current = requestAnimationFrame(animate);
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPaused, speed]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatMarketCap = (marketCap: number) => {
    if (marketCap >= 1e12) {
      return `$${(marketCap / 1e12).toFixed(2)}T`;
    } else if (marketCap >= 1e9) {
      return `$${(marketCap / 1e9).toFixed(2)}B`;
    } else if (marketCap >= 1e6) {
      return `$${(marketCap / 1e6).toFixed(2)}M`;
    }
    return `$${marketCap}`;
  };

  const formatVolume = (volume: number) => {
    if (volume >= 1e6) {
      return `${(volume / 1e6).toFixed(1)}M`;
    } else if (volume >= 1e3) {
      return `${(volume / 1e3).toFixed(1)}K`;
    }
    return volume.toString();
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
          <BarChart sx={{ mr: 1 }} />
          Live Market Ticker
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Scroll Speed">
            <IconButton 
              size="small" 
              onClick={() => setSpeed(speed === 50 ? 100 : speed === 100 ? 25 : 50)}
            >
              <Speed />
            </IconButton>
          </Tooltip>
          <Tooltip title={isPaused ? 'Resume' : 'Pause'}>
            <IconButton 
              size="small" 
              onClick={() => setIsPaused(!isPaused)}
            >
              {isPaused ? <PlayArrow /> : <Pause />}
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Card sx={{ bgcolor: 'background.paper', border: 1, borderColor: 'divider' }}>
        <Box 
          sx={{ 
            height: 80, 
            overflow: 'hidden', 
            position: 'relative',
            bgcolor: 'grey.900',
            color: 'white'
          }}
        >
          <Box
            ref={tickerRef}
            sx={{
              display: 'flex',
              alignItems: 'center',
              height: '100%',
              position: 'absolute',
              whiteSpace: 'nowrap',
              paddingX: 2
            }}
          >
            {/* Duplicate stocks array to create seamless loop */}
            {[...stocks, ...stocks].map((stock, index) => (
              <Box
                key={`${stock.symbol}-${index}`}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  mr: 4,
                  minWidth: 'fit-content'
                }}
              >
                <Box sx={{ mr: 3 }}>
                  <Typography 
                    variant="body1" 
                    fontWeight="bold" 
                    sx={{ fontFamily: 'monospace' }}
                  >
                    {stock.symbol}
                  </Typography>
                  <Typography variant="caption" color="grey.400">
                    {formatVolume(stock.volume)}
                  </Typography>
                </Box>
                
                <Box sx={{ mr: 2 }}>
                  <Typography variant="h6" fontWeight="bold">
                    {formatCurrency(stock.price)}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {stock.change >= 0 ? (
                      <TrendingUp sx={{ fontSize: 16, color: '#4CAF50', mr: 0.5 }} />
                    ) : (
                      <TrendingDown sx={{ fontSize: 16, color: '#F44336', mr: 0.5 }} />
                    )}
                    <Typography 
                      variant="caption" 
                      color={stock.change >= 0 ? '#4CAF50' : '#F44336'}
                      fontWeight="bold"
                    >
                      {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.changePercent.toFixed(2)}%)
                    </Typography>
                  </Box>
                </Box>

                {stock.marketCap && (
                  <Box>
                    <Typography variant="caption" color="grey.400">
                      Market Cap
                    </Typography>
                    <Typography variant="body2" color="grey.300">
                      {formatMarketCap(stock.marketCap)}
                    </Typography>
                  </Box>
                )}
              </Box>
            ))}
          </Box>
        </Box>
      </Card>

      {/* Market Status */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip 
            label="Market Open" 
            color="success" 
            size="small" 
            variant="outlined"
          />
          <Chip 
            label={`${speed}px/s`} 
            size="small" 
            variant="outlined"
          />
        </Box>
        <Typography variant="caption" color="text.secondary">
          Real-time market data • Last updated: {new Date().toLocaleTimeString()}
        </Typography>
      </Box>
    </Box>
  );
};

export default StockTicker;
