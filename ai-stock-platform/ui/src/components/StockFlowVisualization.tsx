import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Card, CardContent, Typography, Box, FormControl, InputLabel, Select, MenuItem,
  ToggleButton, ToggleButtonGroup, Chip, CircularProgress, IconButton, Tooltip
} from '@mui/material';
import {
  TrendingUp, TrendingDown, PlayArrow, Pause, Refresh, Fullscreen,
  ShowChart, ScatterPlot, BarChart
} from '@mui/icons-material';
import { Line, Scatter, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
  ScatterController,
  BarElement,
  Filler
} from 'chart.js';
import { motion, AnimatePresence } from 'framer-motion';
import wsService from '../services/websocket.service';
import { mlService } from '../services/ml-service';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  ScatterController,
  BarElement,
  Filler
);

interface StockFlowData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  flow: number[];  // Historical flow values
  timestamp: string;
  sector: string;
  prediction?: number;
}

interface FlowVisualizationProps {
  stocks?: string[];
  height?: number;
  autoRefresh?: boolean;
  showPredictions?: boolean;
}

const StockFlowVisualization: React.FC<FlowVisualizationProps> = ({
  stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN'],
  height = 400,
  autoRefresh = true,
  showPredictions = true
}) => {
  const [flowData, setFlowData] = useState<StockFlowData[]>([]);
  const [isPlaying, setIsPlaying] = useState(autoRefresh);
  const [visualizationType, setVisualizationType] = useState<'flow' | 'scatter' | 'heatmap' | 'network'>('flow');
  const [selectedTimeframe, setSelectedTimeframe] = useState<'1m' | '5m' | '15m' | '1h' | '1d'>('5m');
  const [loading, setLoading] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [modelPredictions, setModelPredictions] = useState<Record<string, number>>({});
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Color palette for different stocks
  const colors = [
    'rgba(255, 99, 132, 0.8)',   // Red
    'rgba(54, 162, 235, 0.8)',   // Blue
    'rgba(255, 205, 86, 0.8)',   // Yellow
    'rgba(75, 192, 192, 0.8)',   // Teal
    'rgba(153, 102, 255, 0.8)',  // Purple
    'rgba(255, 159, 64, 0.8)',   // Orange
  ];

  const generateMockFlowData = useCallback((): StockFlowData[] => {
    return stocks.map((symbol) => {
      const basePrice = 100 + Math.random() * 300;
      const change = (Math.random() - 0.5) * 10;
      const changePercent = (change / basePrice) * 100;
      
      // Generate flow data (last 50 data points)
      const flow = Array.from({ length: 50 }, (_, i) => {
        const time = i / 49; // Normalize to 0-1
        const wave = Math.sin(time * Math.PI * 4) * 5;
        const trend = (Math.random() - 0.5) * 2;
        const noise = (Math.random() - 0.5) * 1;
        return basePrice + wave + trend + noise;
      });

      return {
        symbol,
        price: basePrice + change,
        change,
        changePercent,
        volume: Math.floor(Math.random() * 10000000) + 1000000,
        flow,
        timestamp: new Date().toISOString(),
        sector: ['Technology', 'Healthcare', 'Finance', 'Energy'][Math.floor(Math.random() * 4)],
        prediction: showPredictions ? modelPredictions[symbol] ?? basePrice + change : undefined
      };
    });
  }, [stocks, showPredictions, modelPredictions]);

  const fetchPredictions = useCallback(async () => {
    if (!showPredictions) {
      setModelPredictions({});
      return;
    }
    try {
      const results = await Promise.all(
        stocks.map(s => mlService.getPrediction(s, 'next_day').catch(() => null))
      );
      const map: Record<string, number> = {};
      results.forEach(res => {
        if (res) {
          map[res.symbol] = res.predicted_price;
        }
      });
      setModelPredictions(map);
    } catch (err) {
      console.error('Error fetching predictions', err);
    }
  }, [stocks, showPredictions]);

  const updateFlowData = useCallback(async () => {
    setLoading(true);
    await fetchPredictions();
    setTimeout(() => {
      setFlowData(generateMockFlowData());
      setLoading(false);
    }, 500);
  }, [generateMockFlowData, fetchPredictions]);

  const togglePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleVisualizationChange = (
    _event: React.MouseEvent<HTMLElement>,
    newType: string | null,
  ) => {
    if (newType !== null) {
      setVisualizationType(newType as any);
    }
  };

  const toggleFullscreen = () => {
    if (!isFullscreen && containerRef.current) {
      containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else if (document.fullscreenElement) {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  // Real-time data updates
  useEffect(() => {
    if (isPlaying && autoRefresh) {
      intervalRef.current = setInterval(() => {
        updateFlowData();
      }, 2000); // Update every 2 seconds
    } else if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, autoRefresh, updateFlowData]);

  // Initial data load
  useEffect(() => {
    updateFlowData();
  }, [updateFlowData]);

  // WebSocket integration for real-time updates
  useEffect(() => {
    const handleMarketData = (data: any) => {
      if (data && data.stocks) {
        setFlowData(prev => 
          prev.map(stock => {
            const update = data.stocks.find((s: any) => s.symbol === stock.symbol);
            if (update) {
              // Add new price to flow array and remove oldest
              const newFlow = [...stock.flow.slice(1), update.price];
              return {
                ...stock,
                price: update.price,
                change: update.change,
                changePercent: update.changePercent,
                volume: update.volume,
                flow: newFlow,
                timestamp: new Date().toISOString()
              };
            }
            return stock;
          })
        );
      }
    };

    if (autoRefresh) {
      wsService.subscribe('market_data', handleMarketData);
      return () => wsService.unsubscribe('market_data');
    }
  }, [autoRefresh]);

  // Chart configuration for flow visualization
  const getFlowChartData = () => {
    if (!flowData.length) return { labels: [], datasets: [] };

    const labels = Array.from({ length: 50 }, (_, i) => i);
    
    const datasets = flowData.map((stock, index) => ({
      label: stock.symbol,
      data: stock.flow,
      borderColor: colors[index % colors.length],
      backgroundColor: colors[index % colors.length].replace('0.8', '0.1'),
      borderWidth: 2,
      pointRadius: 0,
      pointHoverRadius: 4,
      tension: 0.4,
      fill: true,
    }));

    return { labels, datasets };
  };

  // Chart configuration for scatter plot (Price vs Volume)
  const getScatterChartData = () => {
    if (!flowData.length) return { datasets: [] };

    const datasets = [{
      label: 'Price vs Volume',
      data: flowData.map(stock => ({
        x: stock.volume / 1000000, // Volume in millions
        y: stock.price,
        symbol: stock.symbol,
        change: stock.changePercent
      })),
      backgroundColor: flowData.map((stock) => 
        stock.changePercent >= 0 ? 'rgba(76, 175, 80, 0.6)' : 'rgba(244, 67, 54, 0.6)'
      ),
      borderColor: flowData.map((stock) => 
        stock.changePercent >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)'
      ),
      pointRadius: 8,
      pointHoverRadius: 12,
    }];

    return { datasets };
  };

  // Chart configuration for sector heatmap
  const getSectorChartData = () => {
    if (!flowData.length) return { labels: [], datasets: [] };

    const sectorData = flowData.reduce((acc, stock) => {
      if (!acc[stock.sector]) {
        acc[stock.sector] = { count: 0, totalChange: 0 };
      }
      acc[stock.sector].count++;
      acc[stock.sector].totalChange += stock.changePercent;
      return acc;
    }, {} as Record<string, { count: number; totalChange: number }>);

    const labels = Object.keys(sectorData);
    const data = labels.map(sector => sectorData[sector].totalChange / sectorData[sector].count);

    return {
      labels,
      datasets: [{
        label: 'Sector Performance (%)',
        data,
        backgroundColor: data.map(value => 
          value >= 0 ? 'rgba(76, 175, 80, 0.8)' : 'rgba(244, 67, 54, 0.8)'
        ),
        borderColor: data.map(value => 
          value >= 0 ? 'rgba(76, 175, 80, 1)' : 'rgba(244, 67, 54, 1)'
        ),
        borderWidth: 1,
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20
        }
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: (context: any) => {
            if (visualizationType === 'scatter') {
              return `${context.raw.symbol}: $${context.raw.y.toFixed(2)} (${context.raw.change.toFixed(2)}%)`;
            }
            return `${context.dataset.label}: $${context.parsed.y.toFixed(2)}`;
          }
        }
      },
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: visualizationType === 'scatter' ? 'Volume (Millions)' : 'Time'
        }
      },
      y: {
        display: true,
        title: {
          display: true,
          text: 'Price ($)'
        }
      }
    },
    animation: {
      duration: 750,
      easing: 'easeInOutQuart' as const
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false
    }
  };

  const renderVisualization = () => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" height={height}>
          <CircularProgress />
        </Box>
      );
    }

    switch (visualizationType) {
      case 'flow':
        return <Line data={getFlowChartData()} options={chartOptions} />;
      case 'scatter':
        return <Scatter data={getScatterChartData()} options={chartOptions} />;
      case 'heatmap':
        return <Bar data={getSectorChartData()} options={chartOptions} />;
      default:
        return <Line data={getFlowChartData()} options={chartOptions} />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      ref={containerRef}
    >
      <Card className="stock-flow-visualization">
        <CardContent>
          {/* Header with controls */}
          <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
            <Typography variant="h5" component="h2" className="quantum-title">
              📈 Stock Flow Visualization
            </Typography>
            
            <Box display="flex" alignItems="center" gap={1}>
              {/* Visualization type selector */}
              <ToggleButtonGroup
                value={visualizationType}
                exclusive
                onChange={handleVisualizationChange}
                size="small"
              >
                <ToggleButton value="flow">
                  <Tooltip title="Flow Chart">
                    <ShowChart />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="scatter">
                  <Tooltip title="Price vs Volume">
                    <ScatterPlot />
                  </Tooltip>
                </ToggleButton>
                <ToggleButton value="heatmap">
                  <Tooltip title="Sector Performance">
                    <BarChart />
                  </Tooltip>
                </ToggleButton>
              </ToggleButtonGroup>

              {/* Timeframe selector */}
              <FormControl size="small" sx={{ minWidth: 80 }}>
                <InputLabel>Time</InputLabel>
                <Select
                  value={selectedTimeframe}
                  label="Time"
                  onChange={(e) => setSelectedTimeframe(e.target.value as any)}
                >
                  <MenuItem value="1m">1m</MenuItem>
                  <MenuItem value="5m">5m</MenuItem>
                  <MenuItem value="15m">15m</MenuItem>
                  <MenuItem value="1h">1h</MenuItem>
                  <MenuItem value="1d">1d</MenuItem>
                </Select>
              </FormControl>

              {/* Play/Pause button */}
              <IconButton onClick={togglePlayPause} color="primary">
                {isPlaying ? <Pause /> : <PlayArrow />}
              </IconButton>

              {/* Refresh button */}
              <IconButton onClick={updateFlowData} color="secondary">
                <Refresh />
              </IconButton>

              {/* Fullscreen button */}
              <IconButton onClick={toggleFullscreen}>
                <Fullscreen />
              </IconButton>
            </Box>
          </Box>

          {/* Stock status chips */}
          <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
            <AnimatePresence>
              {flowData.map((stock, index) => (
                <motion.div
                  key={stock.symbol}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Chip
                    label={`${stock.symbol}: $${stock.price.toFixed(2)} (${stock.changePercent.toFixed(2)}%)`}
                    color={stock.changePercent >= 0 ? 'success' : 'error'}
                    variant="outlined"
                    icon={stock.changePercent >= 0 ? <TrendingUp /> : <TrendingDown />}
                    style={{ 
                      borderColor: colors[index % colors.length],
                      color: colors[index % colors.length]
                    }}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </Box>

          {/* Chart container */}
          <Box height={height} position="relative">
            {renderVisualization()}
          </Box>

          {/* Data summary */}
          <Box display="flex" justifyContent="space-around" mt={2}>
            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                Total Stocks: {flowData.length}
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                Gainers: {flowData.filter(s => s.changePercent > 0).length}
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="body2" color="textSecondary">
                Last Update: {flowData.length > 0 ? new Date(flowData[0].timestamp).toLocaleTimeString() : 'Never'}
              </Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default StockFlowVisualization;