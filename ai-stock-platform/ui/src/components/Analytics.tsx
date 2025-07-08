/**
 * Analytics Component
 * Market analytics and insights with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Badge, Table } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { MarketOverview, Stock } from '../services/api-service';

const Analytics: React.FC = () => {
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [topMovers, setTopMovers] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch market overview
      const marketData = await apiService.getMarketOverview();
      setMarketOverview(marketData);

      // Fetch top movers
      const movers = await apiService.getTopMovers();
      setTopMovers(movers);

    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatChange = (change: number) => {
    const isPositive = change >= 0;
    return (
      <span className={isPositive ? 'text-success' : 'text-danger'}>
        {isPositive ? '+' : ''}{change.toFixed(2)}%
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    });
  };

  const renderOverviewTab = () => (
    <>
      {/* Market Indices */}
      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Market Indices</h5>
        </Card.Header>
        <Card.Body>
          {marketOverview ? (
            <Row>
              {marketOverview.indices.map((index, idx) => (
                <Col md={4} key={idx} className="text-center mb-3">
                  <Card className="border-0 bg-light">
                    <Card.Body>
                      <h6>{index.name}</h6>
                      <h4>{index.value.toLocaleString()}</h4>
                      <div>{formatChange(index.change_percent)}</div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Market Sectors */}
      <Card className="mb-4">
        <Card.Header>
          <h5 className="mb-0">Sector Performance</h5>
        </Card.Header>
        <Card.Body>
          {marketOverview ? (
            <Row>
              {marketOverview.sectors.map((sector, idx) => (
                <Col md={6} lg={4} key={idx} className="mb-3">
                  <Card className="border-0 bg-light">
                    <Card.Body>
                      <div className="d-flex justify-content-between align-items-center">
                        <h6 className="mb-0">{sector.name}</h6>
                        <Badge bg={sector.change_percent >= 0 ? 'success' : 'danger'}>
                          {formatChange(sector.change_percent)}
                        </Badge>
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Market Sentiment */}
      {marketOverview && (
        <Card className="mb-4">
          <Card.Header>
            <h5 className="mb-0">Market Sentiment</h5>
          </Card.Header>
          <Card.Body>
            <Row>
              <Col md={6}>
                <Card className="border-0 bg-light text-center">
                  <Card.Body>
                    <h6>Overall Sentiment</h6>
                    <h4>
                      <Badge bg={marketOverview.market_sentiment === 'positive' ? 'success' : 'danger'}>
                        {marketOverview.market_sentiment}
                      </Badge>
                    </h4>
                  </Card.Body>
                </Card>
              </Col>
              <Col md={6}>
                <Card className="border-0 bg-light text-center">
                  <Card.Body>
                    <h6>Volatility Index</h6>
                    <h4>{marketOverview.volatility_index}</h4>
                  </Card.Body>
                </Card>
              </Col>
            </Row>
          </Card.Body>
        </Card>
      )}
    </>
  );

  const renderMoversTab = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Top Movers</h5>
      </Card.Header>
      <Card.Body>
        {topMovers.length > 0 ? (
          <Table responsive hover>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Price</th>
                <th>Change</th>
                <th>Change %</th>
                <th>Market Cap</th>
              </tr>
            </thead>
            <tbody>
              {topMovers.map((stock) => (
                <tr key={stock.symbol}>
                  <td>
                    <Link to={`/stocks/${stock.symbol}`} className="text-decoration-none fw-bold">
                      {stock.symbol}
                    </Link>
                  </td>
                  <td>{stock.name}</td>
                  <td>{formatCurrency(stock.price)}</td>
                  <td className={stock.change && stock.change >= 0 ? 'text-success' : 'text-danger'}>
                    {stock.change ? (stock.change > 0 ? '+' : '') + stock.change.toFixed(2) : 'N/A'}
                  </td>
                  <td>
                    <Badge bg={stock.change_percent >= 0 ? 'success' : 'danger'}>
                      {formatChange(stock.change_percent)}
                    </Badge>
                  </td>
                  <td>{stock.market_cap || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        ) : (
          <div className="text-center">
            <Spinner animation="border" role="status">
              <span className="visually-hidden">Loading...</span>
            </Spinner>
          </div>
        )}
      </Card.Body>
    </Card>
  );

  const renderAnalysisTab = () => (
    <Card className="mb-4">
      <Card.Header>
        <h5 className="mb-0">Market Analysis</h5>
      </Card.Header>
      <Card.Body>
        <Alert variant="info">
          <Alert.Heading>AI-Powered Market Analysis</Alert.Heading>
          <p>Advanced market analysis features are coming soon. This will include:</p>
          <ul>
            <li>Risk analysis and portfolio optimization</li>
            <li>Correlation analysis between stocks and sectors</li>
            <li>Economic indicators and their market impact</li>
            <li>Predictive analytics and forecasting</li>
          </ul>
          <Button variant="primary" as={Link as any} to={ROUTES.AI_ASSISTANT}>
            Try AI Assistant
          </Button>
        </Alert>
      </Card.Body>
    </Card>
  );

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Analytics</h1>
        <Button variant="outline-primary" onClick={fetchAnalyticsData} disabled={loading}>
          {loading ? <Spinner animation="border" size="sm" /> : 'Refresh Data'}
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchAnalyticsData}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Tab Navigation */}
      <Card className="mb-4">
        <Card.Header>
          <div className="d-flex gap-2">
            <Button
              variant={activeTab === 'overview' ? 'primary' : 'outline-primary'}
              onClick={() => setActiveTab('overview')}
            >
              Market Overview
            </Button>
            <Button
              variant={activeTab === 'movers' ? 'primary' : 'outline-primary'}
              onClick={() => setActiveTab('movers')}
            >
              Top Movers
            </Button>
            <Button
              variant={activeTab === 'analysis' ? 'primary' : 'outline-primary'}
              onClick={() => setActiveTab('analysis')}
            >
              Analysis
            </Button>
          </div>
        </Card.Header>
      </Card>

      {/* Tab Content */}
      {activeTab === 'overview' && renderOverviewTab()}
      {activeTab === 'movers' && renderMoversTab()}
      {activeTab === 'analysis' && renderAnalysisTab()}

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" className="w-100">
                📈 Browse Stocks
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-success" className="w-100">
                📋 Manage Watchlist
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.BACKTEST} variant="outline-info" className="w-100">
                🔄 Run Backtest
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.AI_ASSISTANT} variant="outline-warning" className="w-100">
                🤖 AI Assistant
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Analytics;
