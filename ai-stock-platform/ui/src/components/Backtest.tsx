/**
 * Backtest Component
 * Strategy backtesting with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Form, Spinner, Alert, Table, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { BacktestResult, BacktestRequest } from '../services/api-service';

const Backtest: React.FC = () => {
  const [backtestHistory, setBacktestHistory] = useState<BacktestResult[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState<boolean>(false);
  const [selectedResult, setSelectedResult] = useState<BacktestResult | null>(null);
  
  const [backtestConfig, setBacktestConfig] = useState<BacktestRequest>({
    symbol: '',
    strategy: 'moving_average',
    strategy_id: 'moving_average',
    start_date: '',
    end_date: '',
    initial_capital: 10000,
    parameters: {}
  });

  useEffect(() => {
    fetchBacktestHistory();
  }, []);

  const fetchBacktestHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getBacktestHistory();
      setBacktestHistory(data);
    } catch (err) {
      console.error('Error fetching backtest history:', err);
      setError('Failed to load backtest history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunBacktest = async () => {
    if (!backtestConfig.symbol.trim() || !backtestConfig.start_date || !backtestConfig.end_date) {
      setError('Please fill in all required fields.');
      return;
    }

    try {
      setRunning(true);
      setError(null);
      const result = await apiService.runBacktest({
        ...backtestConfig,
        symbol: backtestConfig.symbol.trim().toUpperCase()
      });
      setSelectedResult(result);
      await fetchBacktestHistory();
    } catch (err) {
      console.error('Error running backtest:', err);
      setError('Failed to run backtest. Please try again.');
    } finally {
      setRunning(false);
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

  const getStrategyLabel = (strategy: string) => {
    switch (strategy) {
      case 'moving_average': return 'Moving Average';
      case 'rsi': return 'RSI';
      case 'macd': return 'MACD';
      case 'bollinger_bands': return 'Bollinger Bands';
      case 'buy_and_hold': return 'Buy and Hold';
      default: return strategy;
    }
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Strategy Backtesting</h1>
        <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-primary">
          View Analytics
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={() => setError(null)}>
            Dismiss
          </Button>
        </Alert>
      )}

      <Row>
        {/* Backtest Configuration */}
        <Col lg={4} className="mb-4">
          <Card>
            <Card.Header>
              <h5 className="mb-0">Run New Backtest</h5>
            </Card.Header>
            <Card.Body>
              <Form>
                <Form.Group className="mb-3">
                  <Form.Label>Stock Symbol</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Enter stock symbol (e.g., AAPL)"
                    value={backtestConfig.symbol}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, symbol: e.target.value })}
                    style={{ textTransform: 'uppercase' }}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Strategy</Form.Label>
                  <Form.Select
                    value={backtestConfig.strategy}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, strategy: e.target.value, strategy_id: e.target.value })}
                  >
                    <option value="moving_average">Moving Average</option>
                    <option value="rsi">RSI</option>
                    <option value="macd">MACD</option>
                    <option value="bollinger_bands">Bollinger Bands</option>
                    <option value="buy_and_hold">Buy and Hold</option>
                  </Form.Select>
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Start Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={backtestConfig.start_date}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, start_date: e.target.value })}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>End Date</Form.Label>
                  <Form.Control
                    type="date"
                    value={backtestConfig.end_date}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, end_date: e.target.value })}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Initial Capital</Form.Label>
                  <Form.Control
                    type="number"
                    value={backtestConfig.initial_capital}
                    onChange={(e) => setBacktestConfig({ ...backtestConfig, initial_capital: parseFloat(e.target.value) || 10000 })}
                  />
                </Form.Group>

                <Button
                  variant="primary"
                  onClick={handleRunBacktest}
                  disabled={running || !backtestConfig.symbol.trim()}
                  className="w-100"
                >
                  {running ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      Running Backtest...
                    </>
                  ) : (
                    'Run Backtest'
                  )}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        {/* Results */}
        <Col lg={8} className="mb-4">
          {selectedResult ? (
            <Card>
              <Card.Header>
                <h5 className="mb-0">Latest Backtest Results</h5>
              </Card.Header>
              <Card.Body>
                <Row className="mb-4">
                  <Col md={6}>
                    <h6>Strategy: {getStrategyLabel(selectedResult.strategy)}</h6>
                    <h6>Symbol: {selectedResult.symbol}</h6>
                    <h6>Period: {selectedResult.start_date} to {selectedResult.end_date}</h6>
                  </Col>
                  <Col md={6}>
                    <h6>Total Return: 
                      <Badge bg={selectedResult.total_return >= 0 ? 'success' : 'danger'} className="ms-2">
                        {formatPercent(selectedResult.total_return)}
                      </Badge>
                    </h6>
                    <h6>Final Value: {formatCurrency(selectedResult.final_value)}</h6>
                    <h6>Max Drawdown: 
                      <Badge bg="warning" className="ms-2">
                        {formatPercent(selectedResult.max_drawdown)}
                      </Badge>
                    </h6>
                  </Col>
                </Row>

                <div className="bg-light p-3 rounded text-center mb-3">
                  <p className="mb-0">📊 Strategy Performance Chart</p>
                  <small className="text-muted">Interactive chart will be displayed here</small>
                </div>

                <Table responsive>
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Sharpe Ratio</td>
                      <td>{selectedResult.sharpe_ratio?.toFixed(2) || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Win Rate</td>
                      <td>{selectedResult.win_rate ? formatPercent(selectedResult.win_rate) : 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Total Trades</td>
                      <td>{selectedResult.total_trades || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td>Volatility</td>
                      <td>{selectedResult.volatility ? formatPercent(selectedResult.volatility) : 'N/A'}</td>
                    </tr>
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          ) : (
            <Card>
              <Card.Body className="text-center text-muted">
                <h5>No Backtest Results</h5>
                <p>Run a backtest to see the results here.</p>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* Backtest History */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Backtest History</h5>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
            </div>
          ) : backtestHistory.length === 0 ? (
            <div className="text-center text-muted">
              <p>No backtest history available.</p>
              <p>Run your first backtest to see results here.</p>
            </div>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Symbol</th>
                  <th>Strategy</th>
                  <th>Total Return</th>
                  <th>Final Value</th>
                  <th>Max Drawdown</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {backtestHistory.map((result, index) => (
                  <tr key={index}>
                    <td>{new Date(result.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link to={`/stocks/${result.symbol}`} className="text-decoration-none fw-bold">
                        {result.symbol}
                      </Link>
                    </td>
                    <td>{getStrategyLabel(result.strategy)}</td>
                    <td>
                      <Badge bg={result.total_return >= 0 ? 'success' : 'danger'}>
                        {formatPercent(result.total_return)}
                      </Badge>
                    </td>
                    <td>{formatCurrency(result.final_value)}</td>
                    <td>
                      <Badge bg="warning">
                        {formatPercent(result.max_drawdown)}
                      </Badge>
                    </td>
                    <td>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => setSelectedResult(result)}
                      >
                        View Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Backtest;
