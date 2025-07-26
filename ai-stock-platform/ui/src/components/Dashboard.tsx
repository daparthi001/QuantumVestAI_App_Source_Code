/**
 * Dashboard Component - Quantum Design System
 * Enhanced with modern UI/UX, animations, and glass morphism effects
 * Updated: 2025-01-09
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ROUTES } from '../config/constants';
import TrendingStocks from './TrendingStocks';
import apiService, { MarketOverview, Portfolio } from '../services/api-service';

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);

  const formatCurrency = (amount: number) =>
    amount.toLocaleString('en-US', { style: 'currency', currency: 'USD' });

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [overviewData, portfolios] = await Promise.all([
          apiService.getMarketOverview(),
          apiService.getPortfolios(),
        ]);
        setMarketOverview(overviewData);
        if (portfolios.length > 0) {
          setPortfolio(portfolios[0]);
        }
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);


  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        delayChildren: 0.3,
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1 }
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="quantum-bg min-vh-100"
    >
      <Container fluid className="p-4">
        {/* Enhanced Header */}
        <motion.div 
          variants={itemVariants}
          className="d-flex justify-content-between align-items-center mb-5"
        >
          <div>
            <h1 className="quantum-text-gradient display-6 mb-2">
              <motion.span
                className="me-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                📊
              </motion.span>
              Dashboard
            </h1>
            <p className="text-muted lead">Welcome to your financial command center</p>
          </div>
          <div className="d-flex gap-2">
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button
                as={Link as any}
                to={ROUTES.STOCKS}
                className="quantum-btn me-2 explore-btn"
                size="lg"
              >
                Explore Stocks <i className="bi bi-arrow-right ms-1"></i>
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button 
                as={Link as any} 
                to={ROUTES.PORTFOLIO} 
                className="quantum-btn-outline"
                size="lg"
              >
                <span className="me-2">💼</span>
                Portfolio
              </Button>
            </motion.div>
          </div>
        </motion.div>

        {/* Error Alert */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Alert variant="danger" className="mb-4 quantum-card">
                <Alert.Heading>
                  <span className="me-2">⚠️</span>
                  Connection Issue
                </Alert.Heading>
                <p>{error}</p>
                <Button 
                  variant="outline-danger" 
                  onClick={() => window.location.reload()}
                  className="quantum-btn-outline"
                >
                  🔄 Retry
                </Button>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <Row>
          {/* Market Overview */}
          <Col lg={8} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className="quantum-card h-100">
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0 d-flex align-items-center">
                    <motion.span
                      className="me-2"
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      📈
                    </motion.span>
                    Market Overview
                    <Badge bg="success" className="ms-2">Live</Badge>
                  </h5>
                </Card.Header>
                <Card.Body>
                  {loading ? (
                    <div className="text-center py-5">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="d-inline-block"
                      >
                        <Spinner animation="border" role="status" variant="primary">
                          <span className="visually-hidden">Loading...</span>
                        </Spinner>
                      </motion.div>
                      <p className="mt-3 text-muted">Loading market data...</p>
                  ) : marketOverview ? (
                    <Row>
                      {marketOverview.indices.map((idxData, idx) => {
                        const iconMap: Record<string, string> = {
                          'S&P 500': '📊',
                          NASDAQ: '💻',
                          'Dow Jones': '🏭',
                        };
                        const icon = iconMap[idxData.name] || '📈';
                        return (
                          <Col md={4} key={idx} className="mb-3">
                            <motion.div
                              className="quantum-stat-card text-center p-3"
                              whileHover={{ scale: 1.05, y: -5 }}
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              transition={{ duration: 0.2, delay: idx * 0.1 }}
                            >
                              <div className="mb-2 fs-2">{icon}</div>
                              <h6 className="text-muted">{idxData.name}</h6>
                              <h4 className="quantum-text-primary mb-2">{idxData.value.toLocaleString()}</h4>
                              <span className={idxData.change_percent >= 0 ? 'text-success' : 'text-danger'}>
                                {idxData.change_percent >= 0 ? '↗ ' : '↘ '}
                                {idxData.change_percent.toFixed(2)}%
                              </span>
                            </motion.div>
                          </Col>
                        );
                      })}
                    </Row>
                  ) : (
                    <div className="text-center text-muted">No market data available</div>
                  )
                  }
                  <motion.div
                    className="text-center mb-3 quantum-stat-card p-3"
                    whileHover={{ scale: 1.02 }}
                  >
                      <h4 className="quantum-text-primary">{portfolio ? formatCurrency(portfolio.total_value) : '--'}</h4>
                      {portfolio && (
                        <small className={portfolio.total_profit_loss >= 0 ? 'text-success' : 'text-danger'}>
                          {portfolio.total_profit_loss >= 0 ? '+' : ''}{formatCurrency(portfolio.total_profit_loss)} ({portfolio.total_profit_loss_percent.toFixed(2)}%)
                        </small>
                      )}
                    </motion.div>
                    <hr />
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                    >
                      <div className="d-flex justify-content-between mb-2">
                        <span className="text-muted">Day's Change:</span>
                        <span className={portfolio && portfolio.daily_change_percent >= 0 ? 'text-success fw-semibold' : 'text-danger fw-semibold'}>
                          {portfolio ? (portfolio.daily_change_percent >= 0 ? '+' : '') + portfolio.daily_change_percent.toFixed(2) + '%' : '--'}
                        </span>
                      </div>
                      <div className="d-flex justify-content-between mb-2">
                        <span className="text-muted">Total Invested:</span>
                        <span className="fw-semibold">{portfolio ? formatCurrency(portfolio.total_value - portfolio.total_profit_loss) : '--'}</span>
                      </div>
                      <div className="d-flex justify-content-between mb-3">
                        <span className="text-muted">Total Gain:</span>
                        <span className={portfolio && portfolio.total_profit_loss >= 0 ? 'text-success fw-semibold' : 'text-danger fw-semibold'}>
                          {portfolio ? (portfolio.total_profit_loss >= 0 ? '+' : '') + formatCurrency(portfolio.total_profit_loss) : '--'}
                        </span>
                      </div>
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button
                        as={Link as any}
                        to={ROUTES.PORTFOLIO}
                        className="quantum-btn w-100"
                      >
                        <span className="me-2">💼</span>
                        View Full Portfolio
                      </Button>
                    </motion.div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        <Row>
          {/* Trending Stocks */}
          <Col lg={6} className="mb-4">
            <motion.div variants={itemVariants}>
              <div className="h-100">
                <TrendingStocks 
                  limit={5} 
                  refreshInterval={60000} 
                  showHeader={false}
                  compact={true}
                />
              </div>
            </motion.div>
          </Col>

          {/* Stock Flow Preview */}
          <Col lg={6} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className="quantum-card h-100">
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0 d-flex align-items-center">
                    <motion.span
                      className="me-2"
                      animate={{ 
                        rotate: [0, 10, -10, 0],
                        scale: [1, 1.1, 1]
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      🌊
                    </motion.span>
                    Stock Flow Preview
                  </h5>
                </Card.Header>
                <Card.Body>
                  <motion.div
                    className="text-center p-3"
                    whileHover={{ scale: 1.02 }}
                  >
                    <p className="text-muted mb-3">
                      Experience real-time stock movements with our interactive flow visualization
                    </p>
                    <motion.div 
                      className="mb-3"
                      animate={{ 
                        background: [
                          'linear-gradient(45deg, #667eea, #764ba2)',
                          'linear-gradient(45deg, #f093fb, #f5576c)',
                          'linear-gradient(45deg, #4facfe, #00f2fe)',
                          'linear-gradient(45deg, #667eea, #764ba2)'
                        ]
                      }}
                      transition={{ duration: 4, repeat: Infinity }}
                      style={{
                        height: '80px',
                        borderRadius: '10px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: 'bold'
                      }}
                    >
                      📈 Live Data Flows 📊
                    </motion.div>
                    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                      <Button 
                        as={Link as any} 
                        to={ROUTES.STOCK_FLOW} 
                        className="quantum-btn w-100"
                        variant="primary"
                      >
                        <span className="me-2">🚀</span>
                        Explore Stock Flows
                      </Button>
                    </motion.div>
                  </motion.div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        <Row>
          <Col lg={6} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className="quantum-card h-100">
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0 d-flex align-items-center">
                    <motion.span
                      className="me-2"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    >
                      ⚡
                    </motion.span>
                    Quick Actions
                  </h5>
                </Card.Header>
                <Card.Body>
                  <Row>
                    {[
                      { route: ROUTES.STOCK_FLOW, icon: '🌊', label: 'Stock Flow', variant: 'outline-primary' },
                      { route: ROUTES.WATCHLIST, icon: '📋', label: 'Manage Watchlist', variant: 'outline-primary' },
                      { route: ROUTES.BACKTEST, icon: '🔄', label: 'Run Backtest', variant: 'outline-success' },
                      { route: ROUTES.ANALYTICS, icon: '📊', label: 'View Analytics', variant: 'outline-info' },
                      { route: ROUTES.ALERTS, icon: '🔔', label: 'Set Alerts', variant: 'outline-warning' }
                    ].map((action, index) => (
                      <Col md={6} className="mb-3" key={action.route}>
                        <motion.div
                          whileHover={{ scale: 1.05, y: -2 }}
                          whileTap={{ scale: 0.95 }}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 }}
                        >
                          <Button 
                            as={Link as any} 
                            to={action.route} 
                            variant={action.variant}
                            className="w-100 quantum-btn-outline"
                          >
                            <span className="me-2">{action.icon}</span>
                            {action.label}
                          </Button>
                        </motion.div>
                      </Col>
                    ))}
                  </Row>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>
      </Container>
    </motion.div>
  );
};

export default Dashboard;
