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
import apiService from '../services/api-service';

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
      setLoading(true);

      const overview = await apiService.getMarketOverview();

      const mapIndex = (name: string): MarketData => {
        const idx = overview.indices.find((i) => i.name === name);
        return {
          symbol: name,
          price: idx?.value || 0,
          change: 0,
          changePercent: idx?.change_percent || 0,
          volume: 0,
          marketCap: 0,
          high: 0,
          low: 0,
          timestamp: overview.date,
        };
      };

      const liveMarketData: MarketOverview = {
        spy: mapIndex('SPY'),
        qqq: mapIndex('QQQ'),
        dia: mapIndex('DIA'),
        vix: {
          symbol: 'VIX',
          price: overview.volatility_index,
          change: 0,
          changePercent: 0,
          volume: 0,
          marketCap: 0,
          high: 0,
          low: 0,
          timestamp: overview.date,
        },
      };
      setMarketData(liveMarketData);

      const portfolios = await apiService.getPortfolios();
      if (portfolios.length > 0) {
        const p = portfolios[0];
        const livePortfolio: PortfolioData = {
          totalValue: p.total_value,
          totalGain: p.total_profit_loss,
          totalGainPercent: p.total_profit_loss_percent,
          positions: p.positions.map((pos) => ({
            symbol: pos.symbol,
            quantity: pos.shares,
            currentPrice: pos.current_price,
            avgCost: pos.purchase_price,
            unrealizedPL: pos.profit_loss,
            unrealizedPLPercent: pos.change_percent,
          })),
        };
        setPortfolio(livePortfolio);
      }

      const movers = await apiService.getTopMovers();
      const liveTopMovers: MarketData[] = movers.map((m) => ({
        symbol: m.symbol,
        price: m.price,
        change: m.change || 0,
        changePercent: m.change_percent,
        volume: 0,
        marketCap: m.market_cap ? parseFloat(m.market_cap) : 0,
        high: m['52_week_high'] || 0,
        low: m['52_week_low'] || 0,
        timestamp: overview.date,
      }));
      setTopMovers(liveTopMovers);

      setLastUpdate(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    } finally {
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