import React, { useState } from 'react';
import {
  Container, Card, CardContent, Typography, Box, Switch,
  FormControlLabel, Chip, Alert, Accordion, AccordionSummary, AccordionDetails
} from '@mui/material';
import {
  Timeline, TrendingUp, ShowChart, Analytics, ExpandMore, Info
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import StockFlowVisualization from '../components/StockFlowVisualization';
import { Link } from 'react-router-dom';
import '../styles/stock-flow.css';

const StockFlowPage: React.FC = () => {
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [showPredictions, setShowPredictions] = useState(true);
  const [selectedStocks, setSelectedStocks] = useState<string[]>([
    'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN'
  ]);

  const popularStocks = [
    'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'NFLX', 
    'AMD', 'INTC', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'UBER', 'SNAP'
  ];

  const handleStockToggle = (stock: string) => {
    setSelectedStocks(prev => 
      prev.includes(stock) 
        ? prev.filter(s => s !== stock)
        : [...prev, stock].slice(0, 8) // Limit to 8 stocks for performance
    );
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        duration: 0.6,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box display="flex" alignItems="center" mb={4}>
            <Timeline fontSize="large" color="primary" sx={{ mr: 2 }} />
            <Box>
              <Typography variant="h3" component="h1" className="quantum-title">
                Stock Flow Analytics
              </Typography>
              <Typography variant="subtitle1" color="textSecondary">
                Real-time visualization of stock price movements, trends, and market flows
              </Typography>
            </Box>
          </Box>
        </motion.div>

        {/* Quick Info Alert */}
        <motion.div variants={itemVariants}>
          <Alert 
            severity="info" 
            icon={<Info />}
            sx={{ mb: 3 }}
          >
            <Typography variant="body2">
              <strong>Interactive Features:</strong> Toggle between flow charts, scatter plots, and sector heatmaps. 
              Use play/pause for real-time updates, and click fullscreen for immersive analysis.
            </Typography>
          </Alert>
        </motion.div>

        {/* Controls Panel */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎛️ Visualization Controls
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={3}>
                <Box display="flex" gap={2}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={autoRefresh}
                        onChange={(e) => setAutoRefresh(e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Real-time Updates"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={showPredictions}
                        onChange={(e) => setShowPredictions(e.target.checked)}
                        color="secondary"
                      />
                    }
                    label="AI Predictions"
                  />
                </Box>
                
                <Box display="flex" gap={1} alignItems="center">
                  <Typography variant="body2" color="textSecondary">
                    Quick Add:
                  </Typography>
                  <Box
                    component="button"
                    onClick={() => setSelectedStocks(['AAPL', 'MSFT', 'GOOGL', 'AMZN'])}
                    sx={{
                      border: '1px solid',
                      borderColor: 'primary.main',
                      borderRadius: 1,
                      px: 2,
                      py: 0.5,
                      backgroundColor: 'transparent',
                      color: 'primary.main',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'white'
                      }
                    }}
                  >
                    Big Tech
                  </Box>
                  <Box
                    component="button"
                    onClick={() => setSelectedStocks(['TSLA', 'RIVN', 'LCID', 'NIO'])}
                    sx={{
                      border: '1px solid',
                      borderColor: 'primary.main',
                      borderRadius: 1,
                      px: 2,
                      py: 0.5,
                      backgroundColor: 'transparent',
                      color: 'primary.main',
                      cursor: 'pointer',
                      '&:hover': {
                        backgroundColor: 'primary.light',
                        color: 'white'
                      }
                    }}
                  >
                    EV Stocks
                  </Box>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </motion.div>

        {/* Stock Selection */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Select Stocks to Visualize ({selectedStocks.length}/8)
              </Typography>
              
              <Box display="flex" flexWrap="wrap" gap={1}>
                {popularStocks.map((stock) => (
                  <Chip
                    key={stock}
                    label={stock}
                    variant={selectedStocks.includes(stock) ? "filled" : "outlined"}
                    color={selectedStocks.includes(stock) ? "primary" : "default"}
                    clickable
                    onClick={() => handleStockToggle(stock)}
                    sx={{
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        transform: 'scale(1.05)'
                      }
                    }}
                  />
                ))}
              </Box>
              
              {selectedStocks.length === 0 && (
                <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                  Please select at least one stock to visualize.
                </Typography>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Main Visualization */}
        {selectedStocks.length > 0 && (
          <motion.div variants={itemVariants}>
            <StockFlowVisualization
              stocks={selectedStocks}
              height={500}
              autoRefresh={autoRefresh}
              showPredictions={showPredictions}
            />
          </motion.div>
        )}

        {/* Feature Explanations */}
        <motion.div variants={itemVariants}>
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📚 Understanding Stock Flow Visualizations
              </Typography>
              
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">
                    <ShowChart sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Flow Chart View
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    Shows real-time price movements as flowing streams. Each line represents a stock's price 
                    trajectory over time, with smooth animations highlighting trends and volatility. 
                    The flowing nature helps identify momentum patterns and correlation between stocks.
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">
                    <Analytics sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Price vs Volume Scatter
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    Displays the relationship between stock price and trading volume. Green dots indicate 
                    stocks with positive performance, while red dots show declining stocks. The position 
                    reveals whether high-volume trading correlates with price movements.
                  </Typography>
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="subtitle1">
                    <TrendingUp sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Sector Performance Heatmap
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Typography variant="body2">
                    Aggregates performance by sector, showing which industries are leading or lagging. 
                    This view helps identify sector rotation patterns and broad market trends that 
                    affect related stocks within the same industry.
                  </Typography>
                </AccordionDetails>
              </Accordion>
            </CardContent>
          </Card>
        </motion.div>

          {/* Navigation Links */}
        <motion.div variants={itemVariants}>
          <Box display="flex" justifyContent="center" gap={2} mt={4}>
            <Box
              component={Link}
              to="/dashboard"
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 1,
                border: '1px solid',
                borderColor: 'primary.main',
                borderRadius: 1,
                textDecoration: 'none',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'primary.light',
                  color: 'white'
                }
              }}
            >
              <Analytics />
              Return to Dashboard
            </Box>
            <Box
              component={Link}
              to="/stocks"
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                px: 2,
                py: 1,
                backgroundColor: 'primary.main',
                color: 'white',
                borderRadius: 1,
                textDecoration: 'none',
                '&:hover': {
                  backgroundColor: 'primary.dark'
                }
              }}
            >
              <ShowChart />
              Explore Individual Stocks
            </Box>
          </Box>
        </motion.div>
      </Container>
    </motion.div>
  );
};

export default StockFlowPage;