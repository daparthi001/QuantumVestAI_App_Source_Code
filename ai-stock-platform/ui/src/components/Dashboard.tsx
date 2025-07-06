/**
 * Dashboard Component
 * Main dashboard with overview of portfolio, market data, and quick actions
 */
import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';

const Dashboard: React.FC = () => {
  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Dashboard</h1>
        <div>
          <Button as={Link} to={ROUTES.STOCKS} variant="primary" className="me-2">
            Explore Stocks
          </Button>
          <Button as={Link} to={ROUTES.PORTFOLIO} variant="outline-primary">
            View Portfolio
          </Button>
        </div>
      </div>

      <Row>
        {/* Market Overview */}
        <Col lg={8} className="mb-4">
          <Card className="h-100">
            <Card.Header>
              <h5 className="mb-0">Market Overview</h5>
            </Card.Header>
            <Card.Body>
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
              <div className="mt-3">
                <div className="bg-light p-3 rounded text-center">
                  <p className="mb-0">📈 Market Chart Placeholder</p>
                  <small className="text-muted">Interactive chart will be displayed here</small>
                </div>
              </div>
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
              <Button as={Link} to={ROUTES.PORTFOLIO} variant="primary" className="w-100">
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
              <div className="list-group list-group-flush">
                {[
                  { symbol: 'AAPL', name: 'Apple Inc.', price: '$198.45', change: '+2.1%', changeClass: 'text-success' },
                  { symbol: 'MSFT', name: 'Microsoft Corp.', price: '$425.63', change: '+1.8%', changeClass: 'text-success' },
                  { symbol: 'NVDA', name: 'NVIDIA Corp.', price: '$1024.78', change: '+3.2%', changeClass: 'text-success' },
                  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: '$176.89', change: '+1.2%', changeClass: 'text-success' },
                  { symbol: 'AMZN', name: 'Amazon.com Inc.', price: '$187.12', change: '+1.5%', changeClass: 'text-success' },
                ].map((stock, index) => (
                  <div key={index} className="list-group-item d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{stock.symbol}</strong>
                      <br />
                      <small className="text-muted">{stock.name}</small>
                    </div>
                    <div className="text-end">
                      <div>{stock.price}</div>
                      <small className={stock.changeClass}>{stock.change}</small>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <Button as={Link} to={ROUTES.STOCKS} variant="outline-primary" className="w-100">
                  View All Stocks
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>

        {/* Recent News */}
        <Col lg={6} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Recent News</h5>
            </Card.Header>
            <Card.Body>
              <div className="list-group list-group-flush">
                {[
                  { title: 'Fed Holds Interest Rates Steady', time: '2 hours ago', source: 'Reuters' },
                  { title: 'Tech Stocks Rally on AI Optimism', time: '4 hours ago', source: 'Bloomberg' },
                  { title: 'Q4 Earnings Season Kicks Off', time: '6 hours ago', source: 'CNBC' },
                  { title: 'Oil Prices Rise Amid Supply Concerns', time: '8 hours ago', source: 'WSJ' },
                  { title: 'Crypto Market Shows Resilience', time: '10 hours ago', source: 'CoinDesk' },
                ].map((news, index) => (
                  <div key={index} className="list-group-item">
                    <div className="fw-bold">{news.title}</div>
                    <small className="text-muted">{news.source} • {news.time}</small>
                  </div>
                ))}
              </div>
              <div className="mt-3">
                <Button as={Link} to={ROUTES.NEWS} variant="outline-primary" className="w-100">
                  View All News
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
                  <Button as={Link} to={ROUTES.WATCHLIST} variant="outline-primary" className="w-100">
                    📋 Manage Watchlist
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link} to={ROUTES.BACKTEST} variant="outline-success" className="w-100">
                    🔄 Run Backtest
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link} to={ROUTES.ANALYTICS} variant="outline-info" className="w-100">
                    📊 View Analytics
                  </Button>
                </Col>
                <Col md={3} className="mb-3">
                  <Button as={Link} to={ROUTES.ALERTS} variant="outline-warning" className="w-100">
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