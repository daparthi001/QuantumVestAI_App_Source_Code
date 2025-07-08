/**
 * Alerts Component
 * Manage price alerts and notifications with API integration
 */
import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Spinner, Alert as BootstrapAlert, Modal, Form, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { ROUTES } from '../config/constants';
import apiService, { Alert, CreateAlertRequest } from '../services/api-service';

const Alerts: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newAlert, setNewAlert] = useState<CreateAlertRequest>({
    symbol: '',
    type: 'price_above',
    condition: 'greater_than',
    value: 0,
    message: ''
  });
  const [creating, setCreating] = useState<boolean>(false);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getAlerts();
      setAlerts(data);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to load alerts. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAlert = async () => {
    if (!newAlert.symbol.trim() || newAlert.value <= 0) return;

    try {
      setCreating(true);
      await apiService.createAlert({
        ...newAlert,
        symbol: newAlert.symbol.trim().toUpperCase()
      });
      setNewAlert({ symbol: '', type: 'price_above', condition: 'greater_than', value: 0, message: '' });
      setShowCreateModal(false);
      await fetchAlerts();
    } catch (err) {
      console.error('Error creating alert:', err);
      setError('Failed to create alert. Please try again.');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteAlert = async (alertId: number) => {
    if (!window.confirm('Are you sure you want to delete this alert?')) return;

    try {
      await apiService.deleteAlert(alertId);
      await fetchAlerts();
    } catch (err) {
      console.error('Error deleting alert:', err);
      setError('Failed to delete alert. Please try again.');
    }
  };

  const getAlertTypeLabel = (type: string) => {
    switch (type) {
      case 'price_above': return 'Price Above';
      case 'price_below': return 'Price Below';
      case 'percent_change': return 'Percent Change';
      case 'volume_spike': return 'Volume Spike';
      default: return type;
    }
  };

  const getAlertStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge bg="success">Active</Badge>;
      case 'triggered': return <Badge bg="warning">Triggered</Badge>;
      case 'disabled': return <Badge bg="secondary">Disabled</Badge>;
      default: return <Badge bg="secondary">{status}</Badge>;
    }
  };

  const formatCurrency = (amount: number) => {
    return amount.toLocaleString('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    });
  };

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Price Alerts</h1>
        <Button variant="primary" onClick={() => setShowCreateModal(true)}>
          Create New Alert
        </Button>
      </div>

      {error && (
        <BootstrapAlert variant="danger" className="mb-4">
          {error}
          <Button variant="link" onClick={fetchAlerts}>
            Retry
          </Button>
        </BootstrapAlert>
      )}

      {/* Alert Statistics */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6>Total Alerts</h6>
              <h4 className="text-primary">{alerts.length}</h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6>Active Alerts</h6>
              <h4 className="text-success">
                {alerts.filter(alert => alert.status === 'active').length}
              </h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6>Triggered Today</h6>
              <h4 className="text-warning">
                {alerts.filter(alert => alert.status === 'triggered').length}
              </h4>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="text-center">
            <Card.Body>
              <h6>Disabled</h6>
              <h4 className="text-secondary">
                {alerts.filter(alert => alert.status === 'disabled').length}
              </h4>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Alerts Table */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">My Alerts</h5>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <div className="text-center">
              <Spinner animation="border" role="status">
                <span className="visually-hidden">Loading...</span>
              </Spinner>
              <p className="mt-2">Loading alerts...</p>
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center text-muted">
              <h5>No Alerts Set</h5>
              <p>Create your first alert to get notified about price movements.</p>
              <Button variant="outline-primary" onClick={() => setShowCreateModal(true)}>
                Create Your First Alert
              </Button>
            </div>
          ) : (
            <Table responsive hover>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Target Value</th>
                  <th>Current Price</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>
                      <Link to={`/stocks/${alert.symbol}`} className="text-decoration-none fw-bold">
                        {alert.symbol}
                      </Link>
                    </td>
                    <td>{getAlertTypeLabel(alert.type)}</td>
                    <td>
                      {alert.type.includes('price') ? formatCurrency(alert.value) : `${alert.value}%`}
                    </td>
                    <td>{alert.current_price ? formatCurrency(alert.current_price) : 'N/A'}</td>
                    <td>{getAlertStatusBadge(alert.status)}</td>
                    <td>{new Date(alert.created_at).toLocaleDateString()}</td>
                    <td>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDeleteAlert(alert.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* Quick Actions */}
      <Card className="mt-4">
        <Card.Header>
          <h5 className="mb-0">Quick Actions</h5>
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" className="w-100">
                📈 Browse Stocks
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.WATCHLIST} variant="outline-success" className="w-100">
                📋 Manage Watchlist
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button as={Link as any} to={ROUTES.PORTFOLIO} variant="outline-info" className="w-100">
                💼 View Portfolio
              </Button>
            </Col>
            <Col md={3} className="mb-3">
              <Button variant="outline-warning" onClick={() => setShowCreateModal(true)} className="w-100">
                🔔 Create Alert
              </Button>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Create Alert Modal */}
      <Modal show={showCreateModal} onHide={() => setShowCreateModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Alert</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Stock Symbol</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter stock symbol (e.g., AAPL)"
                value={newAlert.symbol}
                onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
                style={{ textTransform: 'uppercase' }}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Alert Type</Form.Label>
              <Form.Select
                value={newAlert.type}
                onChange={(e) => {
                  const type = e.target.value;
                  const condition = type === 'price_above' ? 'greater_than' : 
                                   type === 'price_below' ? 'less_than' : 'equal_to';
                  setNewAlert({ ...newAlert, type: type as any, condition });
                }}
              >
                <option value="price_above">Price Above</option>
                <option value="price_below">Price Below</option>
                <option value="percent_change">Percent Change</option>
                <option value="volume_spike">Volume Spike</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>
                Target Value 
                {newAlert.type.includes('price') ? ' ($)' : ' (%)'}
              </Form.Label>
              <Form.Control
                type="number"
                step="0.01"
                placeholder={newAlert.type.includes('price') ? "Enter target price" : "Enter percentage"}
                value={newAlert.value || ''}
                onChange={(e) => setNewAlert({ ...newAlert, value: parseFloat(e.target.value) || 0 })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Message (Optional)</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Custom message for this alert"
                value={newAlert.message}
                onChange={(e) => setNewAlert({ ...newAlert, message: e.target.value })}
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
            onClick={handleCreateAlert}
            disabled={!newAlert.symbol.trim() || newAlert.value <= 0 || creating}
          >
            {creating ? <Spinner animation="border" size="sm" /> : 'Create Alert'}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default Alerts;
