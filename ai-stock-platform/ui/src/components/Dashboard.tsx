/**
 * Dashboard Component
 * Main dashboard with overview of portfolio, market data, and quick actions
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { MarketOverview, Stock, Watchlist } from '../services/api-service';

const Dashboard: React.FC = () => {
  const [marketOverview, setMarketOverview] = useState<MarketOverview | null>(null);
  const [trendingStocks, setTrendingStocks] = useState<Stock[]>([]);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch market overview
        const marketData = await apiService.getMarketOverview();
        setMarketOverview(marketData);

        // Fetch trending stocks
        const trending = await apiService.getTrendingStocks();
        setTrendingStocks(trending);

        // Fetch watchlists
        try {
          const watchlistData = await apiService.getWatchlists();
          setWatchlists(watchlistData);
        } catch (err) {
          // User might not be logged in, ignore watchlist errors
          console.log('Watchlists not available:', err);
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

  const formatChange = (change: number) => {
    const isPositive = change >= 0;
    return (
      <span className={isPositive ? 'text-success' : 'text-danger'}>
        {isPositive ? '+' : ''}{change.toFixed(2)}%
      </span>
    );
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Dashboard</h1>
        <div>
          <Button as={Link as any} to={ROUTES.STOCKS} variant="primary" className="me-2">
            Explore Stocks
          </Button>
          <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="outline-primary">
            View Portfolio
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Alert>
      )}

      <Row>
        {/* Market Overview */}
        <Col lg={8} className="mb-4">
          <Card className="h-100">
            <Card.Header>
              <h5 className="mb-0">Market Overview</h5>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center">
                  <Spinner animation="border" role="status">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                </div>
              ) : marketOverview ? (
                <Row>
                  {marketOverview.indices.map((index, idx) => (
                    <Col md={4} key={idx} className="text-center mb-3">
                      <h6>{index.name}</h6>
                      <h4>{index.value.toLocaleString()}</h4>
                      <small>{formatChange(index.change_percent)}</small>
                    </Col>
                  ))}
                </Row>
              ) : (
                <Row>
                  <Col md={4} className="text-center mb-3">
                    <h6>S&P 500</h6>
                    <h4 className="text-success">5,421.53</h4>
                    <small className="text-success">+0.8%</small>
                  </Col>
                  <Col md={4} className="text-center mb-3">
                    <h6>NASDAQ</h6>
                    <h4 className="text-success">17,658.23</h4>
                    <small className="text-success">+1.2%</small>
                  </Col>
                  <Col md={4} className="text-center mb-3">
                    <h6>Dow Jones</h6>
                    <h4 className="text-success">39,875.12</h4>
                    <small className="text-success">+0.5%</small>
                  </Col>
                </Row>
              )}
              {marketOverview && (
                <div className="mt-3">
                  <div className="bg-light p-3 rounded">
                    <Row>
                      <Col md={6}>
                        <h6>Market Sentiment</h6>
                        <Badge bg={marketOverview.market_sentiment === 'positive' ? 'success' : 'danger'}>
                          {marketOverview.market_sentiment}
                        </Badge>
                      </Col>
                      <Col md={6}>
                        <h6>Volatility Index</h6>
                        <span className="h5">{marketOverview.volatility_index}</span>
                      </Col>
                    </Row>
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* Quick Stats */}
        <Col lg={4} className="mb-4">
          <Card className="h-100">
            <Card.Header>
              <h5 className="mb-0">Portfolio Summary</h5>
            </Card.Header>
            <Card.Body>
              <div className="text-center mb-3">
                <h4>$124,567.89</h4>
                <small className="text-success">+$2,456 (+2.0%)</small>
              </div>
              <hr />
              <div className="d-flex justify-content-between mb-2">
                <span>Day's Change:</span>
                <span className="text-success">+$523.12</span>
              </div>
              <div className="d-flex justify-content-between mb-2">
                <span>Total Invested:</span>
                <span>$120,000.00</span>
              </div>
              <div className="d-flex justify-content-between mb-3">
                <span>Total Gain:</span>
                <span className="text-success">+$4,567.89</span>
              </div>
              <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="primary" className="w-100">
                View Full Portfolio
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        {/* Top Stocks */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Trending Stocks</h5>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center">
                  <Spinner animation="border" role="status" size="sm">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {trendingStocks.slice(0, 5).map((stock, index) => (
                    <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{stock.symbol}</strong>
                        <br />
                        <small className="text-muted">{stock.name}</small>
                      </div>
                      <div className="text-end">
                        <div>${stock.price.toFixed(2)}</div>
                        <small className={stock.change_percent >= 0 ? 'text-success' : 'text-danger'}>
                          {formatChange(stock.change_percent)}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-3">
                <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" className="w-100">

                  View All Stocks
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Watchlists */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">My Watchlists</h5>
            </Card.Header>
            <Card.Body>
              {loading ? (
                <div className="text-center">
                  <Spinner animation="border" role="status" size="sm">
                    <span className="visually-hidden">Loading...</span>
                  </Spinner>
                </div>
              ) : watchlists.length > 0 ? (
                <div className="list-group list-group-flush">
                  {watchlists.slice(0, 3).map((watchlist, index) => (
                    <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                      <div>
                        <strong>{watchlist.name}</strong>
                        <br />
                        <small className="text-muted">{watchlist.stocks.length} stocks</small>
                      </div>
                      <div className="text-end">
                        <Badge bg="secondary">{watchlist.stocks.length}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center text-muted">
                  <p>No watchlists yet</p>
                  <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-primary" size="sm">
                    Create Your First Watchlist
                  </Button>
                </div>
              )}
              <div className="mt-3">
                <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-primary" className="w-100">
                  View All Watchlists
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Quick Actions */}
      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Quick Actions</h5>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-primary" className="w-100">

                    📋 Manage Watchlist
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.BACKTEST} variant="outline-success" className="w-100">

                    🔄 Run Backtest
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-info" className="w-100">

                    📊 View Analytics
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link as any} to={ROUTES.ALERTS} variant="outline-warning" className="w-100">

                    🔔 Set Alerts
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

export default Dashboard;