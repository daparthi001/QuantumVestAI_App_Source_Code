/**
 * Backtest Results Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Button, Spinner, Table, Badge } from 'react-bootstrap';
import { backtestService, BacktestResult } from '../../services/backtest-service';
import { useError } from '../../contexts/ErrorContext';
import BacktestChart from './charts/BacktestChart';

interface BacktestResultsProps {
  backtestId: string;
}

const BacktestResults: React.FC<BacktestResultsProps> = ({ backtestId }) => {
  const [backtestResult, setBacktestResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const { showErrorMessage } = useError();
  
  useEffect(() => {
    const fetchBacktestResult = async () => {
      try {
        const result = await backtestService.getBacktestResult(backtestId);
        setBacktestResult(result);
      } catch (error: any) {
        showErrorMessage(error.response?.data?.message || 'Failed to fetch backtest results');
      } finally {
        setLoading(false);
      }
    };
    
    fetchBacktestResult();
  }, [backtestId, showErrorMessage]);
  
  if (loading) {
    return (
      <div className="backtest-loading text-center p-5">
        <Spinner animation="border" role="status" />
        <p className="mt-3">Loading backtest results...</p>
      </div>
    );
  }
  
  if (!backtestResult) {
    return (
      <div className="backtest-error text-center p-5">
        <i className="bi bi-exclamation-triangle-fill text-danger fs-1"></i>
        <h4 className="mt-3">Error Loading Results</h4>
        <p className="text-muted">Unable to load backtest results. Please try again later.</p>
      </div>
    );
  }
  
  return (
    <div className="backtest-results">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3>Backtest Results</h3>
          <p className="text-muted mb-0">
            Strategy: {backtestResult.parameters.strategy.replace('_', ' ').toUpperCase()} | 
            Period: {backtestResult.parameters.startDate} to {backtestResult.parameters.endDate}
          </p>
        </div>
        <div>
          <Button variant="outline-primary" className="me-2">
            <i className="bi bi-download me-1"></i> Export
          </Button>
          <Button variant="outline-secondary">
            <i className="bi bi-share me-1"></i> Share
          </Button>
        </div>
      </div>
      
      <Row className="performance-metrics mb-4">
        <Col xs={6} md={3}>
          <div className="metric-card">
            <div className="metric-title">Total Return</div>
            <div className={`metric-value ${backtestResult.results.totalReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {(backtestResult.results.totalReturn * 100).toFixed(2)}%
            </div>
          </div>
        </Col>
        <Col xs={6} md={3}>
          <div className="metric-card">
            <div className="metric-title">Annualized Return</div>
            <div className={`metric-value ${backtestResult.results.annualizedReturn >= 0 ? 'text-success' : 'text-danger'}`}>
              {(backtestResult.results.annualizedReturn * 100).toFixed(2)}%
            </div>
          </div>
        </Col>
        <Col xs={6} md={3}>
          <div className="metric-card">
            <div className="metric-title">Sharpe Ratio</div>
            <div className="metric-value">
              {backtestResult.results.sharpeRatio.toFixed(2)}
            </div>
          </div>
        </Col>
        <Col xs={6} md={3}>
          <div className="metric-card">
            <div className="metric-title">Max Drawdown</div>
            <div className="metric-value text-danger">
              {(backtestResult.results.maxDrawdown * 100).toFixed(2)}%
            </div>
          </div>
        </Col>
      </Row>
      
      <div className="chart-section">
        <Card>
          <Card.Body>
            <div className="chart-controls">
              <h5 className="mb-0">Portfolio Performance</h5>
              <div className="btn-group">
                <Button variant="outline-secondary" size="sm" active>1M</Button>
                <Button variant="outline-secondary" size="sm">3M</Button>
                <Button variant="outline-secondary" size="sm">6M</Button>
                <Button variant="outline-secondary" size="sm">1Y</Button>
                <Button variant="outline-secondary" size="sm">ALL</Button>
              </div>
            </div>
            
            <div className="chart-container">
              <BacktestChart
                equityCurve={backtestResult.results.equityCurve}
                benchmarkCurve={backtestResult.results.benchmarkCurve}
              />
            </div>
            
            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#4e73df'}}></div>
                <span>Portfolio</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{backgroundColor: '#858796'}}></div>
                <span>Benchmark (S&P 500)</span>
              </div>
            </div>
          </Card.Body>
        </Card>
      </div>
      
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Risk Metrics</h5>
            </Card.Header>
            <Card.Body>
              <div className="risk-metrics-grid">
                <div className="risk-metric">
                  <div className="risk-metric-name">Volatility (Annual)</div>
                  <div className="risk-metric-value">{(backtestResult.results.volatility * 100).toFixed(2)}%</div>
                </div>
                <div className="risk-metric">
                  <div className="risk-metric-name">Beta</div>
                  <div className="risk-metric-value">{backtestResult.results.beta.toFixed(2)}</div>
                </div>
                <div className="risk-metric">
                  <div className="risk-metric-name">Alpha</div>
                  <div className="risk-metric-value">{(backtestResult.results.alpha * 100).toFixed(2)}%</div>
                </div>
                <div className="risk-metric">
                  <div className="risk-metric-name">Sortino Ratio</div>
                  <div className="risk-metric-value">{backtestResult.results.sortino.toFixed(2)}</div>
                </div>
                <div className="risk-metric">
                  <div className="risk-metric-name">Max Drawdown</div>
                  <div className="risk-metric-value">{(backtestResult.results.maxDrawdown * 100).toFixed(2)}%</div>
                </div>
                <div className="risk-metric">
                  <div className="risk-metric-name">Benchmark Return</div>
                  <div className="risk-metric-value">{(backtestResult.results.benchmarkReturn * 100).toFixed(2)}%</div>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Drawdown Periods</h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table className="mb-0">
                <thead>
                  <tr>
                    <th>Start</th>
                    <th>End</th>
                    <th>Depth</th>
                    <th>Recovery</th>
                  </tr>
                </thead>
                <tbody>
                  {backtestResult.results.drawdowns.map((drawdown, index) => (
                    <tr key={index}>
                      <td>{drawdown.start}</td>
                      <td>{drawdown.end}</td>
                      <td className="text-danger">{(drawdown.depth * 100).toFixed(2)}%</td>
                      <td>{drawdown.recovery}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">Trade History</h5>
          <Badge bg="info">{backtestResult.results.trades.length} Trades</Badge>
        </Card.Header>
        <Card.Body className="p-0">
          <div className="trades-table-container">
            <Table className="trades-table mb-0">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Entry Date</th>
                  <th>Entry Price</th>
                  <th>Exit Date</th>
                  <th>Exit Price</th>
                  <th>Return</th>
                  <th>Holding Period</th>
                </tr>
              </thead>
              <tbody>
                {backtestResult.results.trades.map((trade, index) => (
                  <tr key={index}>
                    <td>{trade.symbol}</td>
                    <td>{trade.entryDate}</td>
                    <td>${trade.entryPrice.toFixed(2)}</td>
                    <td>{trade.exitDate}</td>
                    <td>${trade.exitPrice.toFixed(2)}</td>
                    <td className={trade.return >= 0 ? 'trade-profit' : 'trade-loss'}>
                      {(trade.return * 100).toFixed(2)}%
                    </td>
                    <td>{trade.holdingPeriod} days</td>
                  </tr>
                ))}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    </div>
  );
};

export default BacktestResults;