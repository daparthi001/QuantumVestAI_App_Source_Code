/**
 * Alert System Component
 * Created: 2025-05-19 04:17:48
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Table, Badge, Modal, Alert } from 'react-bootstrap';
import { alertService } from '../../services/alert.service';
import { AlertType, AlertCondition, AlertSeverity } from '../../types/alerts';

interface AlertConfig {
    id?: string;
    symbol: string;
    type: AlertType;
    condition: AlertCondition;
    threshold: number;
    severity: AlertSeverity;
    active: boolean;
    createdAt?: string;
}

const AlertSystem: React.FC = () => {
    const [alerts, setAlerts] = useState<AlertConfig[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [newAlert, setNewAlert] = useState<Partial<AlertConfig>>({
        symbol: '',
        type: AlertType.PRICE,
        condition: AlertCondition.ABOVE,
        threshold: 0,
        severity: AlertSeverity.MEDIUM,
        active: true
    });
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadAlerts();
    }, []);

    const loadAlerts = async () => {
        try {
            const response = await alertService.getAlerts();
            setAlerts(response.data);
        } catch (err) {
            setError('Failed to load alerts');
        }
    };

    const handleCreateAlert = async () => {
        try {
            if (!newAlert.symbol || !newAlert.threshold) {
                setError('Please fill in all required fields');
                return;
            }

            await alertService.createAlert(newAlert as AlertConfig);
            setShowModal(false);
            loadAlerts();
            setNewAlert({
                symbol: '',
                type: AlertType.PRICE,
                condition: AlertCondition.ABOVE,
                threshold: 0,
                severity: AlertSeverity.MEDIUM,
                active: true
            });
        } catch (err) {
            setError('Failed to create alert');
        }
    };

    const handleToggleAlert = async (alertId: string, active: boolean) => {
        try {
            await alertService.updateAlert(alertId, { active });
            loadAlerts();
        } catch (err) {
            setError('Failed to update alert');
        }
    };

    const handleDeleteAlert = async (alertId: string) => {
        try {
            await alertService.deleteAlert(alertId);
            loadAlerts();
        } catch (err) {
            setError('Failed to delete alert');
        }
    };

    const getSeverityBadge = (severity: AlertSeverity) => {
        const variants = {
            [AlertSeverity.LOW]: 'info',
            [AlertSeverity.MEDIUM]: 'warning',
            [AlertSeverity.HIGH]: 'danger'
        };
        return <Badge bg={variants[severity]}>{severity}</Badge>;
    };

    return (
        <>
            <Card className="alert-system">
                <Card.Header className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Alert System</h5>
                    <Button variant="primary" onClick={() => setShowModal(true)}>
                        Create Alert
                    </Button>
                </Card.Header>
                <Card.Body>
                    {error && (
                        <Alert variant="danger" onClose={() => setError(null)} dismissible>
                            {error}
                        </Alert>
                    )}
                    
                    <Table responsive>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Type</th>
                                <th>Condition</th>
                                <th>Threshold</th>
                                <th>Severity</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {alerts.map((alert) => (
                                <tr key={alert.id}>
                                    <td>{alert.symbol}</td>
                                    <td>{alert.type}</td>
                                    <td>{alert.condition}</td>
                                    <td>{alert.threshold}</td>
                                    <td>{getSeverityBadge(alert.severity)}</td>
                                    <td>
                                        <Form.Check
                                            type="switch"
                                            checked={alert.active}
                                            onChange={(e) => 
                                                handleToggleAlert(alert.id!, e.target.checked)
                                            }
                                        />
                                    </td>
                                    <td>
                                        <Button
                                            variant="danger"
                                            size="sm"
                                            onClick={() => handleDeleteAlert(alert.id!)}
                                        >
                                            Delete
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            <Modal show={showModal} onHide={() => setShowModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Create New Alert</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Symbol</Form.Label>
                            <Form.Control
                                type="text"
                                value={newAlert.symbol}
                                onChange={(e) => 
                                    setNewAlert({ ...newAlert, symbol: e.target.value })
                                }
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Alert Type</Form.Label>
                            <Form.Select
                                value={newAlert.type}
                                onChange={(e) => 
                                    setNewAlert({ ...newAlert, type: e.target.value as AlertType })
                                }
                            >
                                {Object.values(AlertType).map((type) => (
                                    <option key={type} value={type}>
                                        {type}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Condition</Form.Label>
                            <Form.Select
                                value={newAlert.condition}
                                onChange={(e) => 
                                    setNewAlert({ 
                                        ...newAlert, 
                                        condition: e.target.value as AlertCondition 
                                    })
                                }
                            >
                                {Object.values(AlertCondition).map((condition) => (
                                    <option key={condition} value={condition}>
                                        {condition}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Threshold</Form.Label>
                            <Form.Control
                                type="number"
                                value={newAlert.threshold}
                                onChange={(e) => 
                                    setNewAlert({ 
                                        ...newAlert, 
                                        threshold: parseFloat(e.target.value) 
                                    })
                                }
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Severity</Form.Label>
                            <Form.Select
                                value={newAlert.severity}
                                onChange={(e) => 
                                    setNewAlert({ 
                                        ...newAlert, 
                                        severity: e.target.value as AlertSeverity 
                                    })
                                }
                            >
                                {Object.values(AlertSeverity).map((severity) => (
                                    <option key={severity} value={severity}>
                                        {severity}
                                    </option>
                                ))}
                            </Form.Select>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowModal(false)}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleCreateAlert}>
                        Create Alert
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

export default AlertSystem;