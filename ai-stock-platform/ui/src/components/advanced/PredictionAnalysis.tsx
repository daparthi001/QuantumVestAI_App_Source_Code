/**
 * AI Prediction Analysis Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Row, Col, Spinner } from 'react-bootstrap';
import { mlService, PredictionResult, ModelInfo } from '../../services/ml-service';
import { stockService } from '../../services/api';
import { useError } from '../../contexts/ErrorContext';
import PredictionChart from './charts/PredictionChart';
import useDebounce from '../../hooks/useDebounce';

const PredictionAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('AAPL');
  const [predictionType, setPredictionType] = useState<'next_day' | 'week_ahead' | 'month_ahead'>('week_ahead');
  const [modelId, setModelId] = useState<string | undefined>(undefined);
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [stockOptions, setStockOptions] = useState<Array<{symbol: string, name: string}>>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const debouncedSearch = useDebounce(searchTerm, 300);
  const { showErrorMessage } = useError();
  
  // Fetch available models
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const modelData = await mlService.getModels();
        setModels(modelData);
      } catch (error) {
        console.error('Error fetching models:', error);
      }
    };
    
    fetchModels();
  }, []);
  
  // Fetch available stocks
  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const stocks = await stockService.getAvailableSymbols();
        setStockOptions(stocks.map(symbol => ({ symbol, name: symbol })));
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    };
    
    fetchStocks();
  }, []);
  
  // Filter stocks based on search term
  const filteredStocks = stockOptions.filter(stock =>
    stock.symbol.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
    stock.name.toLowerCase().includes(debouncedSearch.toLowerCase())
  ).slice(0, 10); // Limit to 10 results
  
  // Generate prediction
  const handleGeneratePrediction = async () => {
    if (!symbol) {
      showErrorMessage('Please select a stock symbol');
      return;
    }
    
    setLoading(true);
    setPrediction(null);
    
    try {
      const result = await mlService.getPrediction(symbol, predictionType);
      setPrediction(result);
    } catch (error: any) {
      showErrorMessage(error.response?.data?.message || 'Failed to generate prediction');
    } finally {
      setLoading(false);
    }
  };
  
  // Calculate prediction metrics
  const calculateMetrics = () => {
    if (!prediction) return null;
    
    const latestPrice = 150.25; // This would come from real data
    const predictedPrice = prediction.predicted_price;
    const changeAmount = predictedPrice - latestPrice;
    const changePercent = (changeAmount / latestPrice) * 100;
    
    return {
      latestPrice,
      predictedPrice,
      changeAmount,
      changePercent
    };
  };
  
  const metrics = calculateMetrics();
  
  return (
    <div className="prediction-analysis">
      <div className="mb-4">
        <h3>AI-Powered Price Predictions</h3>
        <p className="text-muted">
          Generate price predictions based on machine learning models trained on historical market data.
        </p>
      </div>
      
      <Row>
        <Col md={4}>
          <Card className="mb-4">
            <Card.Body>
              <h4 className="mb-3">Configure Prediction</h4>
              
              <Form.Group className="mb-3">
                <Form.Label>Stock Symbol</Form.Label>
                <div className="search-select">
                  <Form.Control
                    type="text"
                    placeholder="\u{1F50D} Search stocks..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    autoComplete="off"
                    className="mb-1"
                  />
                  
                  {searchTerm && (
                    <div className="search-results">
                      {filteredStocks.length > 0 ? (
                        filteredStocks.map(stock => (
                          <div 
                            key={stock.symbol}
                            className="search-item"
                            onClick={() => {
                              setSymbol(stock.symbol);
                              setSearchTerm('');
                            }}
                          >
                            <strong>{stock.symbol}</strong> - {stock.name}
                          </div>
                        ))
                      ) : (
                        <div className="search-item no-results">No matching stocks found</div>
                      )}
                    </div>
                  )}
                  
                  <div className="selected-value">
                    {symbol && `Selected: ${symbol}`}
                  </div>
                </div>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Prediction Timeframe</Form.Label>
                <Form.Select 
                  value={predictionType}
                  onChange={(e) => setPredictionType(e.target.value as any)}
                >
                  <option value="next_day">Next Trading Day</option>
                  <option value="week_ahead">Week Ahead</option>
                  <option value="month_ahead">Month Ahead</option>
                </Form.Select>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>ML Model (Optional)</Form.Label>
                <Form.Select 
                  value={modelId || ''}
                  onChange={(e) => setModelId(e.target.value || undefined)}
                >
                  <option value="">Default Model</option>
                  {models.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name} ({model.accuracy.toFixed(2)} accuracy)
                    </option>
                  ))}
                </Form.Select>
                <Form.Text className="text-muted">
                  Leave as default to use the best model for this stock.
                </Form.Text>
              </Form.Group>
              
              <Button 
                variant="primary" 
                className="w-100" 
                onClick={handleGeneratePrediction}
                disabled={loading || !symbol}
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Generating...
                  </>
                ) : 'Generate Prediction'}
              </Button>
            </Card.Body>
          </Card>
          
          {models.length > 0 && (
            <Card>
              <Card.Header>
                <h5 className="mb-0">Available ML Models</h5>
              </Card.Header>
              <Card.Body className="p-0">
                <div className="model-list">
                  {models.map(model => (
                    <div key={model.id} className="model-item">
                      <div className="model-header">
                        <h6>{model.name}</h6>
                        <span className={`model-status status-${model.status}`}>
                          {model.status}
                        </span>
                      </div>
                      <div className="model-details">
                        <div><strong>Algorithm:</strong> {model.algorithm}</div>
                        <div><strong>Accuracy:</strong> {model.accuracy.toFixed(2)}%</div>
                        <div><strong>Last Trained:</strong> {new Date(model.last_trained).toLocaleDateString()}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          )}
        </Col>
        
        <Col md={8}>
          {loading ? (
            <div className="prediction-loading">
              <Spinner animation="border" role="status" />
              <p>Generating AI prediction...</p>
            </div>
          ) : prediction ? (
            <div className="prediction-results">
              <Card className="mb-4">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h4 className="mb-0">{symbol} Prediction Results</h4>
                    <div className="prediction-meta">
                      <span className="badge bg-info">
                        {predictionType === 'next_day' ? 'Next Day' : 
                         predictionType === 'week_ahead' ? 'Week Ahead' : 'Month Ahead'}
                      </span>
                      <span className="model-badge">
                        {prediction.model_version}
                      </span>
                    </div>
                  </div>
                  
                  {metrics && (
                    <Row className="prediction-metrics">
                      <Col xs={6} md={3}>
                        <div className="metric-card">
                          <div className="metric-title">Current Price</div>
                          <div className="metric-value">${metrics.latestPrice.toFixed(2)}</div>
                        </div>
                      </Col>
                      <Col xs={6} md={3}>
                        <div className="metric-card">
                          <div className="metric-title">Predicted Price</div>
                          <div className="metric-value">${metrics.predictedPrice.toFixed(2)}</div>
                        </div>
                      </Col>
                      <Col xs={6} md={3}>
                        <div className="metric-card">
                          <div className="metric-title">Change ($)</div>
                          <div className={`metric-value ${metrics.changeAmount >= 0 ? 'text-success' : 'text-danger'}`}>
                            {metrics.changeAmount >= 0 ? '+' : ''}{metrics.changeAmount.toFixed(2)}
                          </div>
                        </div>
                      </Col>
                      <Col xs={6} md={3}>
                        <div className="metric-card">
                          <div className="metric-title">Change (%)</div>
                          <div className={`metric-value ${metrics.changePercent >= 0 ? 'text-success' : 'text-danger'}`}>
                            {metrics.changePercent >= 0 ? '+' : ''}{metrics.changePercent.toFixed(2)}%
                          </div>
                        </div>
                      </Col>
                    </Row>
                  )}
                </Card.Body>
              </Card>
              
              <Card>
                <Card.Body>
                  <h5>Price Prediction Chart</h5>
                  <div className="chart-container">
                    <PredictionChart 
                      symbol={symbol}
                      prediction={[prediction]}
                    />
                  </div>
                  
                  <div className="prediction-disclaimer mt-3">
                    <p className="text-muted small">
                      <i className="bi bi-info-circle me-1"></i>
                      Predictions are based on historical data and machine learning models. 
                      Actual market performance may vary. Do not make investment decisions based solely on these predictions.
                    </p>
                  </div>
                </Card.Body>
              </Card>
            </div>
          ) : (
            <div className="prediction-placeholder">
              <div className="text-center p-5">
                <i className="bi bi-graph-up prediction-icon"></i>
                <h4>AI Prediction Engine</h4>
                <p className="text-muted">
                  Select a stock and timeframe to generate price predictions powered by machine learning.
                </p>
              </div>
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default PredictionAnalysis;