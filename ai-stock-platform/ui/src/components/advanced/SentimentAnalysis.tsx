/**
 * Sentiment Analysis Component
 * Created: 2025-06-19 03:13:52
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Form, Button, Spinner, Badge } from 'react-bootstrap';
import { sentimentService, SentimentData, TrendingStock } from '../../services/sentiment-service';
import { useError } from '../../contexts/ErrorContext';
import SentimentChart from './charts/SentimentChart';

const SentimentAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('AAPL');
  const [sentimentData, setSentimentData] = useState<SentimentData | null>(null);
  const [trendingStocks, setTrendingStocks] = useState<TrendingStock[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [trendingLoading, setTrendingLoading] = useState<boolean>(true);
  const { showErrorMessage } = useError();
  
  // Fetch trending stocks on component mount
  useEffect(() => {
    const fetchTrendingStocks = async () => {
      try {
        const stocks = await sentimentService.getTrendingStocks(10);
        setTrendingStocks(stocks);
      } catch (error) {
        console.error('Error fetching trending stocks:', error);
      } finally {
        setTrendingLoading(false);
      }
    };
    
    fetchTrendingStocks();
  }, []);
  
  // Handle sentiment analysis request
  const handleAnalyzeSentiment = async () => {
    if (!symbol) {
      showErrorMessage('Please enter a stock symbol');
      return;
    }
    
    setLoading(true);
    setSentimentData(null);
    
    try {
      const data = await sentimentService.getStockSentiment(symbol);
      setSentimentData(data);
    } catch (error: any) {
      showErrorMessage(error.response?.data?.message || 'Failed to analyze sentiment');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle clicking on a trending stock
  const handleTrendingStockClick = (symbol: string) => {
    setSymbol(symbol);
    handleAnalyzeSentiment();
  };
  
  // Get sentiment label color
  const getSentimentColor = (label: string): string => {
    switch (label) {
      case 'positive': return 'success';
      case 'negative': return 'danger';
      case 'neutral': return 'secondary';
      default: return 'info';
    }
  };
  
  return (
    <div className="sentiment-analysis">
      <div className="mb-4">
        <h3>Social Media Sentiment Analysis</h3>
        <p className="text-muted">
          Analyze market sentiment for stocks based on social media and news sources.
        </p>
      </div>
      
      <Row>
        <Col md={4}>
          <Card className="mb-4">
            <Card.Body>
              <h4 className="mb-3">Analyze Stock Sentiment</h4>
              
              <Form.Group className="mb-3">
                <Form.Label>Stock Symbol</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter stock symbol (e.g., AAPL)"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                />
              </Form.Group>
              
              <Button 
                variant="primary" 
                className="w-100" 
                onClick={handleAnalyzeSentiment}
                disabled={loading || !symbol}
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Analyzing...
                  </>
                ) : 'Analyze Sentiment'}
              </Button>
            </Card.Body>
          </Card>
          
          <Card>
            <Card.Header>
              <h5 className="mb-0">Trending Stocks</h5>
            </Card.Header>
            <Card.Body className="p-0">
              {trendingLoading ? (
                <div className="text-center p-4">
                  <Spinner animation="border" size="sm" />
                  <p className="mb-0 mt-2">Loading trending stocks...</p>
                </div>
              ) : (
                <div className="trending-stocks-list">
                  {trendingStocks.map(stock => (
                    <div 
                      key={stock.symbol} 
                      className="trending-stock-item"
                      onClick={() => handleTrendingStockClick(stock.symbol)}
                    >
                      <div className="trending-stock-info">
                        <div className="trending-stock-symbol">{stock.symbol}</div>
                        <div className="trending-stock-name">{stock.company_name}</div>
                      </div>
                      <div className="trending-stock-metrics">
                        <Badge 
                          bg={stock.sentiment_score > 0.1 ? 'success' : stock.sentiment_score < -0.1 ? 'danger' : 'secondary'}
                          className="me-2"
                        >
                          {stock.sentiment_score > 0.1 ? 'Positive' : stock.sentiment_score < -0.1 ? 'Negative' : 'Neutral'}
                        </Badge>
                        <span className="trending-stock-mentions">
                          {stock.mention_count} mentions
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={8}>
          {loading ? (
            <div className="sentiment-loading">
              <Spinner animation="border" role="status" />
              <p>Analyzing social media sentiment...</p>
            </div>
          ) : sentimentData ? (
            <div className="sentiment-results">
              <Card className="mb-4">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center mb-4">
                    <div>
                      <h4 className="mb-0">{sentimentData.symbol} Sentiment Analysis</h4>
                      <p className="text-muted mb-0">Analysis Date: {sentimentData.date}</p>
                    </div>
                    <Badge 
                      bg={getSentimentColor(sentimentData.sentiment_label)} 
                      style={{ fontSize: '1rem', padding: '0.5rem 1rem' }}
                    >
                      {sentimentData.sentiment_label.toUpperCase()}
                    </Badge>
                  </div>
                  
                  <Row className="sentiment-metrics">
                    <Col xs={6} md={3}>
                      <div className="metric-card">
                        <div className="metric-title">Sentiment Score</div>
                        <div className="metric-value">{sentimentData.sentiment_score.toFixed(2)}</div>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="metric-card">
                        <div className="metric-title">Social Volume</div>
                        <div className="metric-value">{sentimentData.volume}</div>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="metric-card">
                        <div className="metric-title">Trending Score</div>
                        <div className="metric-value">{sentimentData.trending_score.toFixed(1)}</div>
                      </div>
                    </Col>
                    <Col xs={6} md={3}>
                      <div className="metric-card">
                        <div className="metric-title">Sources</div>
                        <div className="metric-value source-breakdown">
                          <div className="source-item">
                            <span className="source-label">Twitter:</span>
                            <span className="source-value">{sentimentData.sources.twitter}</span>
                          </div>
                          <div className="source-item">
                            <span className="source-label">News:</span>
                            <span className="source-value">{sentimentData.sources.news}</span>
                          </div>
                        </div>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
              
              <Row>
                <Col md={8}>
                  <Card>
                    <Card.Body>
                      <h5>Sentiment Over Time</h5>
                      <div className="chart-container">
                        <SentimentChart 
                          symbol={sentimentData.symbol}
                          data={sentimentData}
                        />
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={4}>
                  <Card>
                    <Card.Header>
                      <h5 className="mb-0">Top Mentions</h5>
                    </Card.Header>
                    <Card.Body className="p-0">
                      <div className="mentions-list">
                        {sentimentData.top_mentions.map((mention, index) => (
                          <div key={index} className="mention-item">
                            <div className="mention-text">{mention.text}</div>
                            <div className="mention-meta">
                              <Badge 
                                bg={mention.sentiment > 0.1 ? 'success' : mention.sentiment < -0.1 ? 'danger' : 'secondary'}
                                className="me-2"
                              >
                                {mention.sentiment > 0.1 ? 'Positive' : mention.sentiment < -0.1 ? 'Negative' : 'Neutral'}
                              </Badge>
                              <span className="mention-source">{mention.source}</span>
                              {mention.url && (
                                <a href={mention.url} target="_blank" rel="noopener noreferrer" className="mention-link">
                                  <i className="bi bi-box-arrow-up-right"></i>
                                </a>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>
          ) : (
            <div className="sentiment-placeholder">
              <div className="text-center p-5">
                <i className="bi bi-chat-square-text sentiment-icon"></i>
                <h4>Social Sentiment Analysis</h4>
                <p className="text-muted">
                  Enter a stock symbol to analyze market sentiment from social media and news sources.
                </p>
              </div>
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default SentimentAnalysis;