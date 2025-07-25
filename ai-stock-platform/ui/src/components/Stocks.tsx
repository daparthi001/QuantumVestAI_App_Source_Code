/**
 * Stocks Component
 * Stock listing and search functionality with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Spinner, Alert, Badge, Placeholder } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { Stock } from '../services/api-service';
import useDebounce from '../hooks/useDebounce';

const Stocks: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [filteredStocks, setFilteredStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSector, setSelectedSector] = useState<string>('all');

  useEffect(() => {
    fetchStocks();
  }, []);

  useEffect(() => {
    filterStocks();
  }, [debouncedSearch, selectedSector, stocks]);

  const fetchStocks = async () => {
    try {
      setLoading(true);
      setError(null);
      const trendingStocks = await apiService.getTrendingStocks();
      setStocks(trendingStocks);
    } catch (err) {
      console.error('Error fetching stocks:', err);
      setError('Failed to load stocks. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const filterStocks = () => {
    let filtered = stocks;

    if (debouncedSearch) {
      filtered = filtered.filter(stock =>
        stock.symbol.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        stock.name.toLowerCase().includes(debouncedSearch.toLowerCase())
      );
    }

    setFilteredStocks(filtered);
  };

  const handleAddToWatchlist = async (symbol: string) => {
    try {
      // This would need to be implemented with proper watchlist selection
      console.log('Adding to watchlist:', symbol);
      // await apiService.addToWatchlist(watchlistId, symbol);
      alert(`${symbol} added to watchlist (feature coming soon)`);
    } catch (err) {
      console.error('Error adding to watchlist:', err);
      alert('Failed to add to watchlist');
    }
  };

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'text-success';
    if (change < 0) return 'text-danger';
    return 'text-muted';
  };

  const formatPrice = (price: number) => {
    return price.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    });
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Stocks</h1>
        <Button as={Link as any} to={ROUTES.WATCHLIST} variant="primary">
          Manage Watchlists
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchStocks}>
            Retry
          </Button>
        </Alert>
      )}

      <Row className="mb-4">
        <Col md={6}>
          <Form.Group>
            <Form.Control
              type="text"
              placeholder="\u{1F50D} Search stocks by symbol or name"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Form.Group>
        </Col>
        <Col md={3}>
          <Form.Select 
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
          >
            <option value="all">All Sectors</option>
            <option value="Technology">Technology</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Finance">Finance</option>
            <option value="Energy">Energy</option>
            <option value="Consumer">Consumer</option>
          </Form.Select>
        </Col>
        <Col md={3}>
          <Button variant="outline-primary" onClick={fetchStocks} disabled={loading}>
            {loading ? <Spinner animation="border" size="sm" /> : 'Refresh'}
          </Button>
        </Col>
      </Row>

      <Card>
        <Card.Header>
          <h5 className="mb-0">Stock List</h5>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <Table responsive hover>
              <tbody>
                {Array.from({ length: 5 }).map((_, idx) => (
                  <tr key={idx}>
                    {Array.from({ length: 8 }).map((__, i) => (
                      <td key={i}>
                        <Placeholder animation="wave" className="w-100" />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Name</th>
                  <th>Price</th>
                  <th>Change</th>
                  <th>Change %</th>
                  <th>Market Cap</th>
                  <th>P/E Ratio</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredStocks.map((stock) => (
                  <tr key={stock.symbol}>
                    <td>
                      <Link to={`/stocks/${stock.symbol}`} className="text-decoration-none fw-bold">
                        {stock.symbol}
                      </Link>
                    </td>
                    <td>{stock.name}</td>
                    <td>{formatPrice(stock.price)}</td>
                    <td className={getPriceChangeColor(stock.change || 0)}>
                      {stock.change ? (stock.change > 0 ? '+' : '') + stock.change.toFixed(2) : 'N/A'}
                    </td>
                    <td>
                      <Badge bg={stock.change_percent >= 0 ? 'success' : 'danger'}>
                        {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                      </Badge>
                    </td>
                    <td>{stock.market_cap || 'N/A'}</td>
                    <td>{stock.pe_ratio || 'N/A'}</td>
                    <td>
                      <Button 
                        variant="outline-primary" 
                        size="sm"
                        onClick={() => handleAddToWatchlist(stock.symbol)}
                      >
                        Add to Watchlist
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
          
          {!loading && filteredStocks.length === 0 && (
            <div className="text-center text-muted">
              <p>No stocks found matching your criteria.</p>
              <Button
                className="quantum-btn-secondary rounded-lg shadow hover:bg-opacity-80"
                onClick={() => {
                  setSearchTerm('');
                  setSelectedSector('all');
                }}
              >
                Clear Filters
              </Button>
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Stocks;