/**
 * Quantum Dashboard Component - World-Class Financial AI Platform
 * Features advanced data visualization, AI insights, and quantum animations
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import Skeleton from '@mui/material/Skeleton';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ROUTES } from '../config/constants';

interface MarketData {
  symbol: string;
  price: string;
  change: string;
  changePercent: string;
  changeClass: string;
}

interface NewsItem {
  title: string;
  time: string;
  source: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

interface PortfolioMetric {
  label: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: string;
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [marketData, setMarketData] = useState<MarketData[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [portfolioMetrics, setPortfolioMetrics] = useState<PortfolioMetric[]>([]);
  const [highlightMarket, setHighlightMarket] = useState(false);
  const [highlightNews, setHighlightNews] = useState(false);

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => {
      setMarketData([
        { symbol: 'AAPL', price: '$189.84', change: '+2.34', changePercent: '+1.25%', changeClass: 'text-success' },
        { symbol: 'MSFT', price: '$378.85', change: '+5.67', changePercent: '+1.52%', changeClass: 'text-success' },
        { symbol: 'GOOGL', price: '$2,832.14', change: '-12.45', changePercent: '-0.44%', changeClass: 'text-danger' },
        { symbol: 'TSLA', price: '$248.50', change: '+8.92', changePercent: '+3.72%', changeClass: 'text-success' },
        { symbol: 'NVDA', price: '$456.78', change: '+15.23', changePercent: '+3.45%', changeClass: 'text-success' },
      ]);

      setNews([
        { title: 'AI Stocks Rally on Quantum Computing Breakthrough', time: '2 hours ago', source: 'TechNews', sentiment: 'positive' },
        { title: 'Federal Reserve Signals Rate Stability', time: '4 hours ago', source: 'Financial Times', sentiment: 'neutral' },
        { title: 'Market Volatility Expected This Week', time: '6 hours ago', source: 'MarketWatch', sentiment: 'negative' },
        { title: 'Crypto Market Shows Resilience', time: '10 hours ago', source: 'CoinDesk', sentiment: 'positive' },
      ]);

      setPortfolioMetrics([
        { label: 'Total Value', value: '$124,567.89', change: '+$4,567.89', changeType: 'positive', icon: '💰' },
        { label: 'Day\'s Change', value: '+$523.12', change: '+0.42%', changeType: 'positive', icon: '📈' },
        { label: 'Total Return', value: '+18.7%', change: '+2.3%', changeType: 'positive', icon: '🎯' },
        { label: 'Win Rate', value: '76.5%', change: '+5.2%', changeType: 'positive', icon: '🏆' },
      ]);

      setIsLoading(false);
      setHighlightMarket(true);
      setHighlightNews(true);
      setTimeout(() => {
        setHighlightMarket(false);
        setHighlightNews(false);
      }, 1500);
    }, 1000);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5
      }
    }
  };

  if (isLoading) {
    return (
      <Container fluid className="py-4">
        <Row className="g-4">
          <Col lg={8}>
            <Card className="quantum-card rounded-2xl shadow-lg p-4">
              <Card.Body>
                <Skeleton variant="rectangular" height={300} animation="wave" />
              </Card.Body>
            </Card>
          </Col>
          <Col lg={4}>
            <Card className="quantum-card rounded-2xl shadow-lg p-4">
              <Card.Body>
                <Skeleton variant="rectangular" height={300} animation="wave" />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Container fluid>
        {/* Header Section */}
        <motion.div variants={itemVariants} className="d-flex justify-content-between align-items-center mb-4">
          <div>
            <motion.h1
              className="quantum-text-gradient"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              Quantum Dashboard
            </motion.h1>
            <motion.p
              className="text-muted"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Real-time AI-powered financial insights
            </motion.p>
          </div>
          <div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button onClick={() => navigate(ROUTES.STOCKS)} className="quantum-btn me-2 explore-btn">
                Explore Stocks <i className="bi bi-arrow-right ms-1"></i>
              </Button>
            </motion.div>
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
              <Button onClick={() => navigate(ROUTES.PORTFOLIO)} className="quantum-btn-secondary">
                💼 View Portfolio
              </Button>
            </motion.div>
          </div>
        </motion.div>

        {/* Portfolio Metrics */}
        <motion.div variants={itemVariants}>
          <Row className="mb-4">
            {portfolioMetrics.map((metric, index) => (
              <Col lg={3} md={6} className="mb-3" key={index}>
                <motion.div
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Card className="quantum-card h-100">
                    <Card.Body className="text-center">
                      <motion.div
                        className="h2 mb-2"
                        animate={{ rotate: [0, 10, -10, 0] }}
                        transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                      >
                        {metric.icon}
                      </motion.div>
                      <h6 className="text-muted mb-2">{metric.label}</h6>
                      <h4 className="quantum-text-primary mb-1">{metric.value}</h4>
                      {metric.change && (
                        <small className={`text-${metric.changeType === 'positive' ? 'success' : 'danger'}`}>
                          {metric.change}
                        </small>
                      )}
                    </Card.Body>
                  </Card>
                </motion.div>
              </Col>
            ))}
          </Row>
        </motion.div>

        <Row>
          {/* AI Market Insights */}
          <Col lg={8} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className="quantum-card h-100">
                <Card.Header className="quantum-card-header">
                  <div className="d-flex align-items-center">
                    <motion.span
                      className="me-2 h5"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                    >
                      🧠
                    </motion.span>
                    <h5 className="mb-0">AI Market Insights</h5>
                    <span className="ms-auto quantum-pulse">
                      <small className="text-success">● Live</small>
                    </span>
                  </div>
                </Card.Header>
                <Card.Body className="quantum-card-body">
                  <div className="chart-container mb-3">
                    <motion.div
                      className="d-flex align-items-center justify-content-center h-100"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 }}
                    >
                      <div className="text-center">
                        <motion.div
                          className="quantum-glow"
                          animate={{ scale: [1, 1.1, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          <h3 className="quantum-text-gradient">📊</h3>
                        </motion.div>
                        <p className="text-muted">Interactive charts coming soon...</p>
                        <small className="text-info">Powered by Quantum ML Models</small>
                      </div>
                    </motion.div>
                  </div>
                  <div className="d-flex justify-content-between">
                    <div className="text-center">
                      <div className="quantum-text-success h6">↗ Bullish Signals</div>
                      <small className="text-muted">85% confidence</small>
                    </div>
                    <div className="text-center">
                      <div className="quantum-text-warning h6">⚠ Market Volatility</div>
                      <small className="text-muted">Medium risk</small>
                    </div>
                    <div className="text-center">
                      <div className="quantum-text-info h6">🎯 Opportunities</div>
                      <small className="text-muted">7 identified</small>
                    </div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>

          {/* Portfolio Summary */}
          <Col lg={4} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className="quantum-card h-100">
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0">💼 Portfolio Summary</h5>
                </Card.Header>
                <Card.Body className="quantum-card-body">
                  <div className="d-flex justify-content-between mb-3">
                    <span>Total Value:</span>
                    <span className="fw-bold quantum-text-primary">$124,567.89</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3">
                    <span>Day's Change:</span>
                    <span className="text-success">+$523.12</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3">
                    <span>Total Invested:</span>
                    <span>$120,000.00</span>
                  </div>
                  <div className="d-flex justify-content-between mb-3">
                    <span>Total Gain:</span>
                    <span className="text-success">+$4,567.89</span>
                  </div>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button onClick={() => navigate(ROUTES.PORTFOLIO)} className="quantum-btn w-100">
                      View Full Portfolio
                    </Button>
                  </motion.div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        <Row>
          {/* Top Performing Stocks */}
          <Col lg={6} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className={`quantum-card ${highlightMarket ? 'quantum-animate-pulse' : ''}`}>
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0">🚀 Top Performers</h5>
                </Card.Header>
                <Card.Body className="quantum-card-body">
                  <div className="list-group list-group-flush">
                    {marketData.map((stock, index) => (
                      <motion.div
                        key={stock.symbol}
                        className="list-group-item bg-transparent border-0 px-0"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        whileHover={{ scale: 1.02, x: 5 }}
                      >
                        <div className="d-flex justify-content-between align-items-center">
                          <div>
                            <div className="fw-bold quantum-text-primary">{stock.symbol}</div>
                            <small className="text-muted">Live Price</small>
                          </div>
                          <div className="text-end">
                            <div className="fw-bold">{stock.price}</div>
                            <small className={stock.changeClass}>
                              {stock.change} ({stock.changePercent})
                            </small>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <div className="mt-3">
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      <Button onClick={() => navigate(ROUTES.STOCKS)} className="quantum-btn-outline w-100">
                        View All Stocks
                      </Button>
                    </motion.div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>

          {/* AI News & Sentiment */}
          <Col lg={6} className="mb-4">
            <motion.div variants={itemVariants}>
              <Card className={`quantum-card ${highlightNews ? 'quantum-animate-pulse' : ''}`}>
                <Card.Header className="quantum-card-header">
                  <div className="d-flex align-items-center">
                    <h5 className="mb-0">📰 AI News Sentiment</h5>
                    <motion.span
                      className="ms-auto"
                      animate={{ opacity: [0.5, 1, 0.5] }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <small className="text-info">● AI Analyzed</small>
                    </motion.span>
                  </div>
                </Card.Header>
                <Card.Body className="quantum-card-body">
                  <div className="list-group list-group-flush">
                    {news.map((newsItem, index) => (
                      <motion.div
                        key={index}
                        className="list-group-item bg-transparent border-0 px-0"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        whileHover={{ scale: 1.01, x: 3 }}
                      >
                        <div className="d-flex">
                          <motion.span
                            className="me-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
                          >
                            {newsItem.sentiment === 'positive' ? '🟢' : 
                             newsItem.sentiment === 'negative' ? '🔴' : '🟡'}
                          </motion.span>
                          <div className="flex-grow-1">
                            <div className="fw-bold">{newsItem.title}</div>
                            <small className="text-muted">{newsItem.source} • {newsItem.time}</small>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                  <div className="mt-3">
                    <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                      <Button onClick={() => navigate(ROUTES.NEWS)} className="quantum-btn-outline w-100">
                        View All News
                      </Button>
                    </motion.div>
                  </div>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>

        {/* Quick Actions */}
        <motion.div variants={itemVariants}>
          <Row>
            <Col>
              <Card className="quantum-card">
                <Card.Header className="quantum-card-header">
                  <h5 className="mb-0">⚡ Quick Actions</h5>
                </Card.Header>
                <Card.Body className="quantum-card-body">
                  <Row>
                    {[
                      { route: ROUTES.WATCHLIST, label: 'Manage Watchlist', icon: '📋', variant: 'quantum-btn-outline' },
                      { route: ROUTES.BACKTEST, label: 'Run Backtest', icon: '🔄', variant: 'quantum-btn-secondary' },
                      { route: ROUTES.ANALYTICS, label: 'View Analytics', icon: '📊', variant: 'quantum-btn-outline' },
                      { route: ROUTES.ALERTS, label: 'Set Alerts', icon: '🔔', variant: 'quantum-btn-outline' },
                    ].map((action, index) => (
                      <Col md={3} className="mb-3" key={index}>
                        <motion.div
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Button 
                            onClick={() => navigate(action.route)} 
                            className={`${action.variant} w-100`}
                          >
                            <motion.span
                              className="me-2"
                              animate={{ rotate: [0, 10, -10, 0] }}
                              transition={{ duration: 3, repeat: Infinity, delay: index * 0.5 }}
                            >
                              {action.icon}
                            </motion.span>
                            {action.label}
                          </Button>
                        </motion.div>
                      </Col>
                    ))}
                  </Row>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </motion.div>
      </Container>
    </motion.div>
  );
};

export default Dashboard;