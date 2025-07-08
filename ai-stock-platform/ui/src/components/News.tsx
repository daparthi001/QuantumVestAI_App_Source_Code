/**
 * News Component
 * Financial news and market updates with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Spinner, Alert, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { NewsItem } from '../services/api-service';

const News: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [filteredNews, setFilteredNews] = useState<NewsItem[]>([]);

  useEffect(() => {
    fetchNews();
  }, []);

  useEffect(() => {
    filterNews();
  }, [news, selectedCategory, searchTerm]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getLatestNews(50);
      setNews(data);
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Failed to load news. Please try again.');
      // Set mock data for demonstration
      setNews(getMockNews());
    } finally {
      setLoading(false);
    }
  };

  const filterNews = () => {
    let filtered = news;

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(item => item.category === selectedCategory);
    }

    if (searchTerm) {
      filtered = filtered.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.summary.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredNews(filtered);
  };

  const getMockNews = (): NewsItem[] => [
    {
      id: '1',
      title: 'Federal Reserve Holds Interest Rates Steady at 5.25-5.50%',
      summary: 'The Federal Reserve decided to maintain the federal funds rate in its current range, citing concerns about inflation and economic growth.',
      content: '',
      category: 'market',
      source: 'Reuters',
      author: 'Financial Reporter',
      published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      url: '#',
      sentiment: 'neutral'
    },
    {
      id: '2',
      title: 'Tech Stocks Rally on Strong AI Earnings Reports',
      summary: 'Major technology companies report better-than-expected earnings driven by artificial intelligence initiatives.',
      content: '',
      category: 'technology',
      source: 'Bloomberg',
      author: 'Tech Reporter',
      published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      url: '#',
      sentiment: 'positive'
    },
    {
      id: '3',
      title: 'Energy Sector Faces Headwinds Amid Oil Price Volatility',
      summary: 'Energy companies struggle with fluctuating oil prices and geopolitical tensions affecting global supply chains.',
      content: '',
      category: 'energy',
      source: 'WSJ',
      author: 'Energy Analyst',
      published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      url: '#',
      sentiment: 'negative'
    },
    {
      id: '4',
      title: 'Healthcare Innovation Drives Biotech Stock Surge',
      summary: 'Breakthrough developments in gene therapy and personalized medicine boost biotech sector performance.',
      content: '',
      category: 'healthcare',
      source: 'CNBC',
      author: 'Healthcare Reporter',
      published_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      url: '#',
      sentiment: 'positive'
    },
    {
      id: '5',
      title: 'Consumer Spending Patterns Shift in Q4 2024',
      summary: 'Retail data shows changing consumer preferences with increased focus on value and sustainability.',
      content: '',
      category: 'consumer',
      source: 'MarketWatch',
      author: 'Retail Analyst',
      published_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      url: '#',
      sentiment: 'neutral'
    }
  ];

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'technology': return 'primary';
      case 'healthcare': return 'success';
      case 'energy': return 'warning';
      case 'finance': return 'info';
      case 'market': return 'secondary';
      default: return 'light';
    }
  };

  const getSentimentBadge = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <Badge bg="success">Positive</Badge>;
      case 'negative': return <Badge bg="danger">Negative</Badge>;
      case 'neutral': return <Badge bg="secondary">Neutral</Badge>;
      default: return <Badge bg="light">Unknown</Badge>;
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays} days ago`;
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Financial News</h1>
        <Button variant="outline-primary" onClick={fetchNews} disabled={loading}>
          {loading ? <Spinner animation="border" size="sm" /> : 'Refresh'}
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchNews}>
            Retry
          </Button>
        </Alert>
      )}

      {/* Filters */}
      <Row className="mb-4">
        <Col md={6}>
          <Form.Group>
            <Form.Control
              type="text"
              placeholder="Search news..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            <option value="market">Market</option>
            <option value="technology">Technology</option>
            <option value="healthcare">Healthcare</option>
            <option value="energy">Energy</option>
            <option value="finance">Finance</option>
            <option value="consumer">Consumer</option>
          </Form.Select>
        </Col>
        <Col md={3}>
          <div className="text-muted">
            {filteredNews.length} articles found
          </div>
        </Col>
      </Row>

      {/* News Articles */}
      {loading ? (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading news...</p>
        </div>
      ) : (
        <Row>
          {filteredNews.map((article) => (
            <Col lg={6} xl={4} key={article.id} className="mb-4">
              <Card className="h-100">
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <Badge bg={getCategoryColor(article.category)}>
                    {article.category.charAt(0).toUpperCase() + article.category.slice(1)}
                  </Badge>
                  {getSentimentBadge(article.sentiment)}
                </Card.Header>
                <Card.Body>
                  <Card.Title className="h6">{article.title}</Card.Title>
                  <Card.Text className="text-muted small">
                    {article.summary}
                  </Card.Text>
                  <div className="mt-auto">
                    <small className="text-muted">
                      {article.source} • {formatTimeAgo(article.published_at)}
                    </small>
                  </div>
                </Card.Body>
                <Card.Footer>
                  <Button 
                    variant="outline-primary" 
                    size="sm"
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Read Full Article
                  </Button>
                </Card.Footer>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {!loading && filteredNews.length === 0 && (
        <div className="text-center text-muted">
          <h5>No Articles Found</h5>
          <p>Try adjusting your search criteria or category filter.</p>
          <Button variant="outline-primary" onClick={() => { setSearchTerm(''); setSelectedCategory('all'); }}>
            Clear Filters
          </Button>
        </div>
      )}

      {/* Quick Actions */}
      <Card className="mt-4">
        <Card.Header>
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.ANALYTICS} variant="outline-primary" className="w-100">
                📊 Market Analytics
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-success" className="w-100">
                📈 Browse Stocks
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.AI_ASSISTANT} variant="outline-info" className="w-100">
                🤖 AI Analysis
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
    </Container>
  );
};

export default News;
