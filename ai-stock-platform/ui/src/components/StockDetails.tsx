/**
 * StockDetails Component
 * Detailed stock information and analysis with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Spinner, Alert, Badge, Tab, Tabs } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { Stock } from '../services/api-service';

const StockDetails: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [stock, setStock] = useState<Stock | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');

  useEffect(() => {
    if (symbol) {
      fetchStockDetails(symbol);
    }
  }, [symbol]);

  const fetchStockDetails = async (symbol: string) => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getStockDetails(symbol);
      setStock(data);
    } catch (err) {
      console.error('Error fetching stock details:', err);
      setError('Failed to load stock details. Please try again.');
      // Set mock data for demonstration
      setStock({
        symbol: symbol.toUpperCase(),
        name: `${symbol.toUpperCase()} Corporation`,
        price: 198.45,
        change: 4.12,
        change_percent: 2.1,
        market_cap: '$2.1T',
        pe_ratio: 25.4,
        dividend_yield: 1.8,
        '52_week_high': 220.45,
        '52_week_low': 145.67
      });
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    });
  };

  const formatPercent = (value: number) => {
    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading stock details...</p>
      </Container>
    );
  }

  if (error || !stock) {
    return (
      <Container>
        <Alert variant="danger" className="mt-4">
          {error || 'Stock not found'}
          <Button variant="link" onClick={() => window.history.back()}>
            Go Back
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid>
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1>{stock.symbol}</h1>
          <h5 className="text-muted">{stock.name}</h5>
        </div>
        <div>
          <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" className="me-2">
            Back to Stocks
          </Button>
          <Button variant="primary">Add to Watchlist</Button>
        </div>
      </div>

      {/* Price Summary */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={3} className="text-center">
              <h6>Current Price</h6>
              <h2>{formatCurrency(stock.price)}</h2>
              <Badge bg={stock.change_percent >= 0 ? 'success' : 'danger'}>
                {formatPercent(stock.change_percent)}
              </Badge>
            </Col>
            <Col md={3} className="text-center">
              <h6>Day's Range</h6>
              <div>{formatCurrency(stock.price - 5)} - {formatCurrency(stock.price + 5)}</div>
            </Col>
            <Col md={3} className="text-center">
              <h6>52 Week Range</h6>
              <div>{formatCurrency(stock['52_week_low'] || 0)} - {formatCurrency(stock['52_week_high'] || 0)}</div>
            </Col>
            <Col md={3} className="text-center">
              <h6>Market Cap</h6>
              <div>{stock.market_cap}</div>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Detailed Information Tabs */}
      <Tabs
        activeKey={activeTab}
        onSelect={(tab) => setActiveTab(tab || 'overview')}
        className="mb-4"
      >
        <Tab eventKey="overview" title="Overview">
          <Row>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Key Metrics</h5>
                </Card.Header>
                <Card.Body>
                  <Row className="mb-2">
                    <Col>P/E Ratio:</Col>
                    <Col className="text-end">{stock.pe_ratio || 'N/A'}</Col>
                  </Row>
                  <Row className="mb-2">
                    <Col>Dividend Yield:</Col>
                    <Col className="text-end">{stock.dividend_yield ? stock.dividend_yield + '%' : 'N/A'}</Col>
                  </Row>
                  <Row className="mb-2">
                    <Col>Market Cap:</Col>
                    <Col className="text-end">{stock.market_cap}</Col>
                  </Row>
                  <Row className="mb-2">
                    <Col>Volume:</Col>
                    <Col className="text-end">45.2M</Col>
                  </Row>
                  <Row className="mb-2">
                    <Col>Avg Volume:</Col>
                    <Col className="text-end">52.1M</Col>
                  </Row>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Price Chart</h5>
                </Card.Header>
                <Card.Body>
                  <div className="bg-light p-4 rounded text-center">
                    <h5>📈 Interactive Price Chart</h5>
                    <p className="text-muted">Real-time price chart will be displayed here</p>
                    <small className="text-muted">Integration with TradingView or Chart.js</small>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="news" title="News">
          <Alert variant="info">
            <Alert.Heading>Stock-Specific News</Alert.Heading>
            <p>Latest news and analysis for {stock.symbol} will be displayed here.</p>
            <Button as={Link as any} to={ROUTES.NEWS} variant="primary">
              View All News
            </Button>
          </Alert>
        </Tab>

        <Tab eventKey="analysis" title="Analysis">
          <Alert variant="info">
            <Alert.Heading>AI Analysis</Alert.Heading>
            <p>AI-powered technical and fundamental analysis for {stock.symbol} will be displayed here.</p>
            <Button as={Link as any} to={ROUTES.AI_ASSISTANT} variant="primary">
              Get AI Analysis
            </Button>
          </Alert>
        </Tab>

        <Tab eventKey="alerts" title="Alerts">
          <Alert variant="info">
            <Alert.Heading>Price Alerts</Alert.Heading>
            <p>Set up custom price alerts for {stock.symbol}.</p>
            <Button as={Link as any} to={ROUTES.ALERTS} variant="primary">
              Create Alert
            </Button>
          </Alert>
        </Tab>
      </Tabs>

      {/* Quick Actions */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} className="mb-3">
              <Button variant="outline-primary" className="w-100">
                📋 Add to Watchlist
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button variant="outline-success" className="w-100">
                💼 Add to Portfolio
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.ALERTS} variant="outline-warning" className="w-100">
                🔔 Set Price Alert
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.AI_ASSISTANT} variant="outline-info" className="w-100">
                🤖 AI Analysis
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default StockDetails;
