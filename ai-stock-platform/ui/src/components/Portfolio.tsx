/**
 * Portfolio Component
 * Portfolio management with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Spinner, Alert, Badge, Modal, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import apiService, { Portfolio, Position } from '../services/api-service';

const PortfolioComponent: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showAddPositionModal, setShowAddPositionModal] = useState<boolean>(false);
  const [newPortfolioName, setNewPortfolioName] = useState<string>('');
  const [newPosition, setNewPosition] = useState({
    symbol: '',
    shares: '',
    purchase_price: ''
  });
  const [creating, setCreating] = useState<boolean>(false);
  const [adding, setAdding] = useState<boolean>(false);

  useEffect(() => {
    fetchPortfolios();
  }, []);

  const fetchPortfolios = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPortfolios();
      setPortfolios(data);
      if (data.length > 0 && !selectedPortfolio) {
        setSelectedPortfolio(data[0]);
      }
    } catch (err) {
      console.error('Error fetching portfolios:', err);
      setError('Failed to load portfolios. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePortfolio = async () => {
    if (!newPortfolioName.trim()) return;

    try {
      setCreating(true);
      await apiService.createPortfolio({ 
        name: newPortfolioName.trim(),
        description: `Portfolio: ${newPortfolioName.trim()}`
      });
      setNewPortfolioName('');
      setShowCreateModal(false);
      await fetchPortfolios();
    } catch (err) {
      console.error('Error creating portfolio:', err);
      setError('Failed to create portfolio. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleAddPosition = async () => {
    if (!newPosition.symbol.trim() || !newPosition.shares || !newPosition.purchase_price || !selectedPortfolio) return;

    try {
      setAdding(true);
      await apiService.addPosition(selectedPortfolio.id, {
        symbol: newPosition.symbol.trim().toUpperCase(),
        shares: parseFloat(newPosition.shares),
        purchase_price: parseFloat(newPosition.purchase_price)
      });
      setNewPosition({ symbol: '', shares: '', purchase_price: '' });
      setShowAddPositionModal(false);
      await fetchPortfolios();
    } catch (err) {
      console.error('Error adding position:', err);
      setError('Failed to add position. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  const handleRemovePosition = async (portfolioId: number, positionId: number) => {
    if (!window.confirm('Are you sure you want to remove this position?')) return;

    try {
      await apiService.removePosition(portfolioId, positionId);
      await fetchPortfolios();
    } catch (err) {
      console.error('Error removing position:', err);
      setError('Failed to remove position. Please try again.');
    }
  };

  const calculateTotalValue = (positions: Position[]) => {
    return positions.reduce((total, position) => total + (position.current_price * position.shares), 0);
  };

  const calculateTotalGainLoss = (positions: Position[]) => {
    return positions.reduce((total, position) => {
      const currentValue = position.current_price * position.shares;
      const purchaseValue = position.purchase_price * position.shares;
      return total + (currentValue - purchaseValue);
    }, 0);
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

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Portfolio</h1>
        <div>
          <Button variant="primary" onClick={() => setShowCreateModal(true)} className="me-2">
            Create Portfolio
          </Button>
          {selectedPortfolio && (
            <Button variant="outline-primary" onClick={() => setShowAddPositionModal(true)}>
              Add Position
            </Button>
          )}
        </div>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchPortfolios}>
            Retry
          </Button>
        </Alert>
      )}

      {loading ? (
        <div className="text-center">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading portfolios...</p>
        </div>
      ) : portfolios.length === 0 ? (
        <Card>
          <Card.Body className="text-center">
            <h5>No Portfolios Yet</h5>
            <p className="text-muted">Create your first portfolio to start tracking your investments.</p>
            <Button variant="primary" onClick={() => setShowCreateModal(true)}>
              Create Your First Portfolio
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <>
          {/* Portfolio Selection */}
          <Row className="mb-4">
            <Col>
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Select Portfolio</h5>
                </Card.Header>
                <Card.Body>
                  <div className="d-flex gap-2 flex-wrap">
                    {portfolios.map((portfolio) => (
                      <Button
                        key={portfolio.id}
                        variant={selectedPortfolio?.id === portfolio.id ? 'primary' : 'outline-primary'}
                        onClick={() => setSelectedPortfolio(portfolio)}
                      >
                        {portfolio.name}
                      </Button>
                    ))}
                  </div>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {selectedPortfolio && (
            <>
              {/* Portfolio Summary */}
              <Row className="mb-4">
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6>Total Value</h6>
                      <h4 className="text-primary">
                        {formatCurrency(calculateTotalValue(selectedPortfolio.positions))}
                      </h4>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6>Total Gain/Loss</h6>
                      <h4 className={calculateTotalGainLoss(selectedPortfolio.positions) >= 0 ? 'text-success' : 'text-danger'}>
                        {formatCurrency(calculateTotalGainLoss(selectedPortfolio.positions))}
                      </h4>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6>Positions</h6>
                      <h4>{selectedPortfolio.positions.length}</h4>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="text-center">
                    <Card.Body>
                      <h6>Daily Change</h6>
                      <h4 className="text-success">+2.3%</h4>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              {/* Portfolio Positions */}
              <Card>
                <Card.Header>
                  <h5 className="mb-0">Positions in {selectedPortfolio.name}</h5>
                </Card.Header>
                <Card.Body>
                  {selectedPortfolio.positions.length === 0 ? (
                    <div className="text-center text-muted">
                      <p>No positions in this portfolio yet.</p>
                      <Button variant="outline-primary" onClick={() => setShowAddPositionModal(true)}>
                        Add Your First Position
                      </Button>
                    </div>
                  ) : (
                    <Table responsive hover>
                      <thead>
                        <tr>
                          <th>Symbol</th>
                          <th>Shares</th>
                          <th>Purchase Price</th>
                          <th>Current Price</th>
                          <th>Market Value</th>
                          <th>Gain/Loss</th>
                          <th>Gain/Loss %</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedPortfolio.positions.map((position) => {
                          const marketValue = position.current_price * position.shares;
                          const purchaseValue = position.purchase_price * position.shares;
                          const gainLoss = marketValue - purchaseValue;
                          const gainLossPercent = (gainLoss / purchaseValue) * 100;

                          return (
                            <tr key={position.id}>
                              <td>
                                <Link to={`/stocks/${position.symbol}`} className="text-decoration-none fw-bold">
                                  {position.symbol}
                                </Link>
                              </td>
                              <td>{position.shares}</td>
                              <td>{formatCurrency(position.purchase_price)}</td>
                              <td>{formatCurrency(position.current_price)}</td>
                              <td>{formatCurrency(marketValue)}</td>
                              <td className={gainLoss >= 0 ? 'text-success' : 'text-danger'}>
                                {formatCurrency(gainLoss)}
                              </td>
                              <td>
                                <Badge bg={gainLoss >= 0 ? 'success' : 'danger'}>
                                  {formatPercent(gainLossPercent)}
                                </Badge>
                              </td>
                              <td>
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => handleRemovePosition(selectedPortfolio.id, position.id)}
                                >
                                  Remove
                                </Button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </Table>
                  )}
                </Card.Body>
              </Card>
            </>
          )}
        </>
      )}

      {/* Create Portfolio Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Portfolio</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Portfolio Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter portfolio name"
                value={newPortfolioName}
                onChange={(e) => setNewPortfolioName(e.target.value)}
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
            onClick={handleCreatePortfolio}
            disabled={!newPortfolioName.trim() || creating}
          >
            {creating ? <Spinner animation="border" size="sm" /> : 'Create'}
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Add Position Modal */}
      <Modal show={showAddPositionModal} onHide={() => setShowAddPositionModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Add Position to {selectedPortfolio?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Stock Symbol</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter stock symbol (e.g., AAPL)"
                value={newPosition.symbol}
                onChange={(e) => setNewPosition({ ...newPosition, symbol: e.target.value })}
                style={{ textTransform: 'uppercase' }}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Number of Shares</Form.Label>
              <Form.Control
                type="number"
                placeholder="Enter number of shares"
                value={newPosition.shares}
                onChange={(e) => setNewPosition({ ...newPosition, shares: e.target.value })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Purchase Price per Share</Form.Label>
              <Form.Control
                type="number"
                step="0.01"
                placeholder="Enter purchase price"
                value={newPosition.purchase_price}
                onChange={(e) => setNewPosition({ ...newPosition, purchase_price: e.target.value })}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowAddPositionModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleAddPosition}
            disabled={!newPosition.symbol.trim() || !newPosition.shares || !newPosition.purchase_price || adding}
          >
            {adding ? <Spinner animation="border" size="sm" /> : 'Add Position'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default PortfolioComponent;
