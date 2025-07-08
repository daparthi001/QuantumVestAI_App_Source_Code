/**
 * Watchlist Component
 * Manage and view user watchlists with full API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Spinner, Alert, Modal, Form, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import apiService, { Watchlist } from '../services/api-service';

const WatchlistComponent: React.FC = () => {
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showAddStockModal, setShowAddStockModal] = useState<boolean>(false);
  const [selectedWatchlist, setSelectedWatchlist] = useState<Watchlist | null>(null);
  const [newWatchlistName, setNewWatchlistName] = useState<string>('');
  const [newStockSymbol, setNewStockSymbol] = useState<string>('');
  const [creating, setCreating] = useState<boolean>(false);
  const [adding, setAdding] = useState<boolean>(false);

  useEffect(() => {
    fetchWatchlists();
  }, []);

  const fetchWatchlists = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getWatchlists();
      setWatchlists(data);
    } catch (err) {
      console.error('Error fetching watchlists:', err);
      setError('Failed to load watchlists. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async () => {
    if (!newWatchlistName.trim()) return;

    try {
      setCreating(true);
      await apiService.createWatchlist({ name: newWatchlistName.trim() });
      setNewWatchlistName('');
      setShowCreateModal(false);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error creating watchlist:', err);
      setError('Failed to create watchlist. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleAddStock = async () => {
    if (!newStockSymbol.trim() || !selectedWatchlist) return;

    try {
      setAdding(true);
      await apiService.addToWatchlist(selectedWatchlist.id, newStockSymbol.trim().toUpperCase());
      setNewStockSymbol('');
      setShowAddStockModal(false);
      setSelectedWatchlist(null);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error adding stock:', err);
      setError('Failed to add stock to watchlist. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  const handleRemoveStock = async (watchlistId: number, symbol: string) => {
    if (!window.confirm(`Remove ${symbol} from watchlist?`)) return;

    try {
      await apiService.removeFromWatchlist(watchlistId, symbol);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error removing stock:', err);
      setError('Failed to remove stock from watchlist. Please try again.');
    }
  };

  const handleDeleteWatchlist = async (watchlistId: number) => {
    if (!window.confirm('Are you sure you want to delete this watchlist?')) return;

    try {
      await apiService.deleteWatchlist(watchlistId);
      await fetchWatchlists();
    } catch (err) {
      console.error('Error deleting watchlist:', err);
      setError('Failed to delete watchlist. Please try again.');
    }
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
        <h1>My Watchlists</h1>
        <div>
          <Button variant="primary" onClick={() => setShowCreateModal(true)}>
            Create New Watchlist
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchWatchlists}>
            Retry
          </Button>
        </Alert>
      )}

      {loading ? (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading watchlists...</p>
        </div>
      ) : watchlists.length === 0 ? (
        <Card>
          <Card.Body className="text-center">
            <h5>No Watchlists Yet</h5>
            <p className="text-muted">Create your first watchlist to start tracking your favorite stocks.</p>
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              Create Your First Watchlist
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {watchlists.map((watchlist) => (
            <Col lg={6} key={watchlist.id} className="mb-4">
              <Card>
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <div>
                    <h5 className="mb-0">{watchlist.name}</h5>
                    <small className="text-muted">
                      {watchlist.stocks.length} stock{watchlist.stocks.length !== 1 ? 's' : ''}
                    </small>
                  </div>
                  <div>
                    <Button
                      variant="outline-primary"
                      size="sm"
                      className="me-2"
                      onClick={() => {
                        setSelectedWatchlist(watchlist);
                        setShowAddStockModal(true);
                      }}
                    >
                      Add Stock
                    </Button>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => handleDeleteWatchlist(watchlist.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body>
                  {watchlist.stocks.length === 0 ? (
                    <div className="text-center text-muted">
                      <p>No stocks in this watchlist yet.</p>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => {
                          setSelectedWatchlist(watchlist);
                          setShowAddStockModal(true);
                        }}
                      >
                        Add Your First Stock
                      </Button>
                    </div>
                  ) : (
                    <Table responsive hover>
                      <thead>
                        <tr>
                          <th>Symbol</th>
                          <th>Name</th>
                          <th>Price</th>
                          <th>Change %</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {watchlist.stocks.map((stock) => (
                          <tr key={stock.symbol}>
                            <td>
                              <Link to={`/stocks/${stock.symbol}`} className="text-decoration-none fw-bold">
                                {stock.symbol}
                              </Link>
                            </td>
                            <td>{stock.name}</td>
                            <td>{formatPrice(stock.price)}</td>
                            <td>
                              <Badge bg={stock.change_percent >= 0 ? 'success' : 'danger'}>
                                {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                              </Badge>
                            </td>
                            <td>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => handleRemoveStock(watchlist.id, stock.symbol)}
                              >
                                Remove
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  )}
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      {/* Create Watchlist Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Watchlist</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Watchlist Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter watchlist name"
                value={newWatchlistName}
                onChange={(e) => setNewWatchlistName(e.target.value)}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleCreateWatchlist}
            disabled={!newWatchlistName.trim() || creating}
          >
            {creating ? <Spinner animation="border" size="sm" /> : 'Create'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Add Stock Modal */}
      <Modal show={showAddStockModal} onHide={() => setShowAddStockModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Stock to {selectedWatchlist?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Stock Symbol</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter stock symbol (e.g., AAPL)"
                value={newStockSymbol}
                onChange={(e) => setNewStockSymbol(e.target.value)}
                style={{ textTransform: 'uppercase' }}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddStockModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleAddStock}
            disabled={!newStockSymbol.trim() || adding}
          >
            {adding ? <Spinner animation="border" size="sm" /> : 'Add Stock'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default WatchlistComponent;
