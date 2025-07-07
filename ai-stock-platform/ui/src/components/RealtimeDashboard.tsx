/**
 * Real-time Market Data Dashboard
 * Premium quantum-inspired design with live data feeds
 */

import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import { formatPrice, formatChange, formatLargeNumber, formatPercentage } from '../utils/formatters';

// WebSocket service for real-time data
import wsService from '../services/websocket.service';

interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  high: number;
  low: number;
  timestamp: string;
}

interface PortfolioData {
  totalValue: number;
  totalGain: number;
  totalGainPercent: number;
  positions: Array<{
    symbol: string;
    quantity: number;
    currentPrice: number;
    avgCost: number;
    unrealizedPL: number;
    unrealizedPLPercent: number;
  }>;
}

interface MarketOverview {
  spy: MarketData;
  qqq: MarketData;
  dia: MarketData;
  vix: MarketData;
}

const RealtimeDashboard: React.FC = () => {
  const [marketData, setMarketData] = useState<MarketOverview | null>(null);
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [topMovers, setTopMovers] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Initialize WebSocket connection and subscribe to real-time data
  useEffect(() => {
    const initializeRealtimeData = () => {
      // Subscribe to market overview data
      wsService.subscribe('market_overview', (data: MarketOverview) => {
        setMarketData(data);
        setLastUpdate(new Date().toLocaleTimeString());
      });

      // Subscribe to portfolio updates
      wsService.subscribe('portfolio_update', (data: PortfolioData) => {
        setPortfolio(data);
      });

      // Subscribe to top movers
      wsService.subscribe('top_movers', (data: MarketData[]) => {
        setTopMovers(data);
      });

      // Initial data load
      fetchInitialData();
    };

    initializeRealtimeData();

    // Cleanup on unmount
    return () => {
      wsService.unsubscribe('market_overview');
      wsService.unsubscribe('portfolio_update');
      wsService.unsubscribe('top_movers');
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      // Simulate initial data fetch
      const mockMarketData: MarketOverview = {
        spy: {
          symbol: 'SPY',
          price: 459.32,
          change: 2.15,
          changePercent: 0.47,
          volume: 45234567,
          marketCap: 4.2e12,
          high: 460.12,
          low: 456.78,
          timestamp: new Date().toISOString()
        },
        qqq: {
          symbol: 'QQQ',
          price: 398.45,
          change: -1.23,
          changePercent: -0.31,
          volume: 32145678,
          marketCap: 2.8e12,
          high: 401.23,
          low: 397.45,
          timestamp: new Date().toISOString()
        },
        dia: {
          symbol: 'DIA',
          price: 342.67,
          change: 0.89,
          changePercent: 0.26,
          volume: 12345678,
          marketCap: 1.5e12,
          high: 343.12,
          low: 340.23,
          timestamp: new Date().toISOString()
        },
        vix: {
          symbol: 'VIX',
          price: 18.45,
          change: -0.67,
          changePercent: -3.51,
          volume: 8765432,
          marketCap: 0,
          high: 19.23,
          low: 17.89,
          timestamp: new Date().toISOString()
        }
      };

      const mockPortfolio: PortfolioData = {
        totalValue: 125420.67,
        totalGain: 8945.32,
        totalGainPercent: 7.68,
        positions: [
          {
            symbol: 'AAPL',
            quantity: 100,
            currentPrice: 189.45,
            avgCost: 175.23,
            unrealizedPL: 1422.00,
            unrealizedPLPercent: 8.11
          },
          {
            symbol: 'MSFT',
            quantity: 50,
            currentPrice: 378.92,
            avgCost: 365.14,
            unrealizedPLPercent: 3.78,
            unrealizedPL: 689.00
          },
          {
            symbol: 'GOOGL',
            quantity: 25,
            currentPrice: 142.31,
            avgCost: 138.67,
            unrealizedPL: 91.00,
            unrealizedPLPercent: 2.62
          }
        ]
      };

      const mockTopMovers: MarketData[] = [
        {
          symbol: 'NVDA',
          price: 789.23,
          change: 45.67,
          changePercent: 6.14,
          volume: 78234567,
          marketCap: 1.9e12,
          high: 792.45,
          low: 743.21,
          timestamp: new Date().toISOString()
        },
        {
          symbol: 'TSLA',
          price: 245.67,
          change: -12.34,
          changePercent: -4.78,
          volume: 89345678,
          marketCap: 780e9,
          high: 258.90,
          low: 242.15,
          timestamp: new Date().toISOString()
        }
      ];

      setMarketData(mockMarketData);
      setPortfolio(mockPortfolio);
      setTopMovers(mockTopMovers);
      setLoading(false);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
      setLoading(false);
    }
  };

  const MarketOverviewCard = ({ data, title }: { data: MarketData; title: string }) => (
    <Card className="quantum-card micro-interaction mb-3">
      <Card.Body>
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div>
            <h6 className="text-muted mb-1">{title}</h6>
            <h4 className="mb-0">{data.symbol}</h4>
          </div>
          <Badge bg={data.change >= 0 ? 'success' : 'danger'} className="quantum-badge">
            {data.change >= 0 ? '📈' : '📉'}
          </Badge>
        </div>
        <div className="mb-2">
          <div className="h3 mb-1">{formatPrice(data.price)}</div>
          <div className={`fw-bold ${data.change >= 0 ? 'text-success' : 'text-danger'}`}>
            {formatChange(data.change, data.changePercent)}
          </div>
        </div>
        <div className="row text-muted small">
          <div className="col-6">
            <div>High: {formatPrice(data.high)}</div>
            <div>Low: {formatPrice(data.low)}</div>
          </div>
          <div className="col-6">
            <div>Volume: {formatLargeNumber(data.volume)}</div>
            {data.marketCap > 0 && (
              <div>Cap: {formatLargeNumber(data.marketCap)}</div>
            )}
          </div>
        </div>
      </Card.Body>
    </Card>
  );

  if (loading) {
    return (
      <Container fluid className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
        <div className="text-center">
          <Spinner animation="border" variant="primary" className="mb-3" />
          <div className="text-muted">Loading real-time market data...</div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="realtime-dashboard">
      {/* Header with real-time indicator */}
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <h1 className="quantum-title">QuantumVest Dashboard</h1>
              <div className="text-muted">
                <span className="live-indicator">🔴 LIVE</span>
                Last updated: {lastUpdate}
              </div>
            </div>
            <div className="dashboard-actions">
              <Button as={Link as any} to={ROUTES.STOCKS} variant="primary" className="me-2">
                🚀 Explore Stocks
              </Button>
              <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="outline-primary">
                💼 Portfolio
              </Button>
            </div>
          </div>
        </Col>
      </Row>

      {/* Market Overview */}
      <Row className="mb-4">
        <Col md={3}>
          {marketData && <MarketOverviewCard data={marketData.spy} title="S&P 500" />}
        </Col>
        <Col md={3}>
          {marketData && <MarketOverviewCard data={marketData.qqq} title="NASDAQ 100" />}
        </Col>
        <Col md={3}>
          {marketData && <MarketOverviewCard data={marketData.dia} title="Dow Jones" />}
        </Col>
        <Col md={3}>
          {marketData && <MarketOverviewCard data={marketData.vix} title="Volatility Index" />}
        </Col>
      </Row>

      {/* Portfolio Performance */}
      <Row className="mb-4">
        <Col lg={8}>
          <Card className="quantum-card quantum-particles">
            <Card.Header>
              <div className="d-flex justify-content-between align-items-center">
                <h5 className="mb-0">💼 Portfolio Performance</h5>
                <Badge bg="info">Real-time</Badge>
              </div>
            </Card.Header>
            <Card.Body>
              {portfolio && (
                <Row>
                  <Col md={4}>
                    <div className="portfolio-metric">
                      <div className="metric-label">Total Value</div>
                      <div className="metric-value">{formatPrice(portfolio.totalValue)}</div>
                    </div>
                  </Col>
                  <Col md={4}>
                    <div className="portfolio-metric">
                      <div className="metric-label">Total Gain/Loss</div>
                      <div className={`metric-value ${portfolio.totalGain >= 0 ? 'text-success' : 'text-danger'}`}>
                        {formatChange(portfolio.totalGain, portfolio.totalGainPercent)}
                      </div>
                    </div>
                  </Col>
                  <Col md={4}>
                    <div className="portfolio-metric">
                      <div className="metric-label">Return Rate</div>
                      <div className={`metric-value ${portfolio.totalGainPercent >= 0 ? 'text-success' : 'text-danger'}`}>
                        {formatPercentage(portfolio.totalGainPercent)}
                      </div>
                    </div>
                  </Col>
                </Row>
              )}
              <div className="mt-3">
                <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="primary" className="w-100">
                  View Full Portfolio Analysis
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card className="quantum-card">
            <Card.Header>
              <h5 className="mb-0">📊 Top Movers</h5>
            </Card.Header>
            <Card.Body>
              <div className="top-movers-list">
                {topMovers.map((stock) => (
                  <div key={stock.symbol} className="top-mover-item d-flex justify-content-between align-items-center mb-2">
                    <div>
                      <div className="fw-bold">{stock.symbol}</div>
                      <div className="text-muted small">{formatPrice(stock.price)}</div>
                    </div>
                    <div className={`text-end ${stock.change >= 0 ? 'text-success' : 'text-danger'}`}>
                      <div className="fw-bold">{formatPercentage(stock.changePercent)}</div>
                      <div className="small">{formatPrice(stock.change)}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" className="w-100">
                  View All Stocks
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row>
        <Col>
          <Card className="quantum-card">
            <Card.Header>
              <h5 className="mb-0">🎯 Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-primary" className="w-100 quantum-action-btn">
                    👁️ Watchlist
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.BACKTEST} variant="outline-success" className="w-100 quantum-action-btn">
                    🔄 Backtest
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-info" className="w-100 quantum-action-btn">
                    📈 Analytics
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.ALERTS} variant="outline-warning" className="w-100 quantum-action-btn">
                    🔔 Alerts
                  </Button>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default RealtimeDashboard;