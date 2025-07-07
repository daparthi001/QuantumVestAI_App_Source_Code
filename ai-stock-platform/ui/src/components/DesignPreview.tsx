/**
 * QuantumVestAI Design Preview - Showcase of the New UI
 * This component demonstrates the new quantum-inspired design system
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { motion } from 'framer-motion';
import '../styles/quantum-design-system.css';
import '../styles/global.css';

const DesignPreview: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const portfolioMetrics = [
    { label: 'Total Value', value: '$124,567.89', change: '+$4,567.89', changeType: 'positive', icon: '💰' },
    { label: 'Day\'s Change', value: '+$523.12', change: '+0.42%', changeType: 'positive', icon: '📈' },
    { label: 'Total Return', value: '+18.7%', change: '+2.3%', changeType: 'positive', icon: '🎯' },
    { label: 'Win Rate', value: '76.5%', change: '+5.2%', changeType: 'positive', icon: '🏆' },
  ];

  const marketData = [
    { symbol: 'AAPL', price: '$189.84', change: '+2.34', changePercent: '+1.25%', changeClass: 'text-success' },
    { symbol: 'MSFT', price: '$378.85', change: '+5.67', changePercent: '+1.52%', changeClass: 'text-success' },
    { symbol: 'GOOGL', price: '$2,832.14', change: '-12.45', changePercent: '-0.44%', changeClass: 'text-danger' },
    { symbol: 'TSLA', price: '$248.50', change: '+8.92', changePercent: '+3.72%', changeClass: 'text-success' },
  ];

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

  return (
    <div className="quantum-bg min-vh-100">
      {/* Quantum Particles Background Effect */}
      <div className="quantum-particles">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="quantum-particle"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: 0
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
              opacity: [0, 0.5, 0]
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              position: 'fixed',
              width: '2px',
              height: '2px',
              background: `rgba(74, 144, 226, ${Math.random() * 0.5})`,
              borderRadius: '50%',
              pointerEvents: 'none',
              zIndex: 1
            }}
          />
        ))}
      </div>

      {/* Enhanced Top Navigation */}
      <motion.div
        className="quantum-nav"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <nav className="navbar px-4 py-3">
          <Container fluid>
            <div className="navbar-brand fw-bold d-flex align-items-center">
              <motion.div
                className="me-2"
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              >
                ⚛️
              </motion.div>
              <span className="quantum-text-gradient">QuantumVestAI</span>
              <small className="ms-3 text-muted">Design Preview</small>
            </div>

            <div className="d-flex align-items-center">
              <motion.div whileHover={{ scale: 1.05 }} className="me-3">
                <Button className="quantum-btn-outline quantum-btn-small">
                  🌙 Dark Mode
                </Button>
              </motion.div>
              <motion.div whileHover={{ scale: 1.05 }}>
                <span className="text-white">{currentTime.toLocaleTimeString()}</span>
              </motion.div>
            </div>
          </Container>
        </nav>
      </motion.div>

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Container fluid className="p-4">
          {/* Header Section */}
          <motion.div variants={itemVariants} className="text-center mb-5">
            <motion.h1
              className="quantum-text-gradient display-4"
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              World-Class Financial AI Platform
            </motion.h1>
            <motion.p
              className="lead text-muted"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
            >
              Quantum-Inspired Design • Glass Morphism • AI-Powered Insights
            </motion.p>
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
                            <h1 className="quantum-text-gradient">📊</h1>
                          </motion.div>
                          <p className="text-muted">Advanced Analytics Dashboard</p>
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

            {/* Stock Performance */}
            <Col lg={4} className="mb-4">
              <motion.div variants={itemVariants}>
                <Card className="quantum-card h-100">
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
                  </Card.Body>
                </Card>
              </motion.div>
            </Col>
          </Row>

          {/* Design System Showcase */}
          <motion.div variants={itemVariants}>
            <Row>
              <Col>
                <Card className="quantum-card">
                  <Card.Header className="quantum-card-header">
                    <h5 className="mb-0">🎨 Quantum Design System Features</h5>
                  </Card.Header>
                  <Card.Body className="quantum-card-body">
                    <Row>
                      <Col md={3} className="mb-3">
                        <motion.div
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Button className="quantum-btn w-100">
                            <motion.span
                              className="me-2"
                              animate={{ rotate: [0, 10, -10, 0] }}
                              transition={{ duration: 3, repeat: Infinity }}
                            >
                              ✨
                            </motion.span>
                            Glass Morphism
                          </Button>
                        </motion.div>
                      </Col>
                      <Col md={3} className="mb-3">
                        <motion.div
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Button className="quantum-btn-secondary w-100">
                            <motion.span
                              className="me-2"
                              animate={{ scale: [1, 1.2, 1] }}
                              transition={{ duration: 2, repeat: Infinity }}
                            >
                              🌊
                            </motion.span>
                            Fluid Animations
                          </Button>
                        </motion.div>
                      </Col>
                      <Col md={3} className="mb-3">
                        <motion.div
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Button className="quantum-btn-outline w-100">
                            <motion.span
                              className="me-2"
                              animate={{ opacity: [0.5, 1, 0.5] }}
                              transition={{ duration: 2, repeat: Infinity }}
                            >
                              ⚡
                            </motion.span>
                            Micro-Interactions
                          </Button>
                        </motion.div>
                      </Col>
                      <Col md={3} className="mb-3">
                        <motion.div
                          whileHover={{ scale: 1.05, y: -5 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Button className="quantum-btn-outline w-100">
                            <motion.span
                              className="me-2 quantum-glow"
                            >
                              🎯
                            </motion.span>
                            Quantum Effects
                          </Button>
                        </motion.div>
                      </Col>
                    </Row>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </motion.div>
        </Container>
      </motion.div>
    </div>
  );
};

export default DesignPreview;