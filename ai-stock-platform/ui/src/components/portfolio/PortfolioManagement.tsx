/**
 * Portfolio Management Component
 * Created: 2025-05-19 04:22:18
 * Author: daparthi001
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Modal, Form, Row, Col, Alert, Badge } from 'react-bootstrap';
import { portfolioService } from '../../services/portfolio.service';
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/formatters';
import { Position, Transaction, PortfolioSummary } from '../../types/portfolio';

const PortfolioManagement: React.FC = () => {
    const [positions, setPositions] = useState<Position[]>([]);
    const [summary, setSummary] = useState<PortfolioSummary | null>(null);
    const [showTransactionModal, setShowTransactionModal] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [newTransaction, setNewTransaction] = useState<Partial<Transaction>>({
        type: 'BUY',
        symbol: '',
        shares: 0,
        price: 0
    });

    useEffect(() => {
        loadPortfolioData();
        // Set up WebSocket connection for real-time updates
        const subscription = portfolioService.subscribeToUpdates((update) => {
            updatePositionPrice(update.symbol, update.price);
        });

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const loadPortfolioData = async () => {
        try {
            setLoading(true);
            const [positionsData, summaryData] = await Promise.all([
                portfolioService.getPositions(),
                portfolioService.getPortfolioSummary()
            ]);
            setPositions(positionsData.data);
            setSummary(summaryData.data);
        } catch (err) {
            setError('Failed to load portfolio data');
        } finally {
            setLoading(false);
        }
    };

    const updatePositionPrice = (symbol: string, newPrice: number) => {
        setPositions(current => 
            current.map(position => {
                if (position.symbol === symbol) {
                    const marketValue = position.shares * newPrice;
                    const gainLoss = marketValue - position.costBasis;
                    return {
                        ...position,
                        currentPrice: newPrice,
                        marketValue,
                        gainLoss,
                        gainLossPercent: (gainLoss / position.costBasis) * 100
                    };
                }
                return position;
            })
        );
    };

    const handleTransactionSubmit = async () => {
        try {
            if (!newTransaction.symbol || !newTransaction.shares || !newTransaction.price) {
                setError('Please fill in all required fields');
                return;
            }

            await portfolioService.addTransaction(newTransaction as Transaction);
            setShowTransactionModal(false);
            loadPortfolioData();
            setNewTransaction({
                type: 'BUY',
                symbol: '',
                shares: 0,
                price: 0
            });
        } catch (err) {
            setError('Failed to process transaction');
        }
    };

    return (
        <>
            <Card className="portfolio-management">
                <Card.Header className="d-flex justify-content-between align-items-center">
                    <h5 className="mb-0">Portfolio Management</h5>
                    <Button 
                        variant="primary" 
                        onClick={() => setShowTransactionModal(true)}
                    >
                        Add Transaction
                    </Button>
                </Card.Header>
                <Card.Body>
                    {error && (
                        <Alert variant="danger" onClose={() => setError(null)} dismissible>
                            {error}
                        </Alert>
                    )}

                    {summary && (
                        <Row className="mb-4">
                            <Col md={3}>
                                <div className="summary-card">
                                    <h6>Total Value</h6>
                                    <div className="value">
                                        {formatCurrency(summary.totalValue)}
                                    </div>
                                </div>
                            </Col>
                            <Col md={3}>
                                <div className="summary-card">
                                    <h6>Day's Gain/Loss</h6>
                                    <div className={`value ${summary.dayChange >= 0 ? 'positive' : 'negative'}`}>
                                        {formatCurrency(summary.dayChange)}
                                        <small>({formatPercentage(summary.dayChangePercent)})</small>
                                    </div>
                                </div>
                            </Col>
                            <Col md={3}>
                                <div className="summary-card">
                                    <h6>Total Gain/Loss</h6>
                                    <div className={`value ${summary.totalGainLoss >= 0 ? 'positive' : 'negative'}`}>
                                        {formatCurrency(summary.totalGainLoss)}
                                        <small>({formatPercentage(summary.totalGainLossPercent)})</small>
                                    </div>
                                </div>
                            </Col>
                            <Col md={3}>
                                <div className="summary-card">
                                    <h6>Cash Balance</h6>
                                    <div className="value">
                                        {formatCurrency(summary.cashBalance)}
                                    </div>
                                </div>
                            </Col>
                        </Row>
                    )}

                    <Table responsive>
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Shares</th>
                                <th>Avg Cost</th>
                                <th>Current Price</th>
                                <th>Market Value</th>
                                <th>Gain/Loss</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {positions.map((position) => (
                                <tr key={position.symbol}>
                                    <td>{position.symbol}</td>
                                    <td>{formatNumber(position.shares)}</td>
                                    <td>{formatCurrency(position.averageCost)}</td>
                                    <td>
                                        <div className="price-cell">
                                            {formatCurrency(position.currentPrice)}
                                            <Badge 
                                                bg={position.priceChange >= 0 ? 'success' : 'danger'}
                                                className="ms-2"
                                            >
                                                {formatPercentage(position.priceChangePercent)}
                                            </Badge>
                                        </div>
                                    </td>
                                    <td>{formatCurrency(position.marketValue)}</td>
                                    <td className={position.gainLoss >= 0 ? 'positive' : 'negative'}>
                                        {formatCurrency(position.gainLoss)}
                                        <small>({formatPercentage(position.gainLossPercent)})</small>
                                    </td>
                                    <td>
                                        <Button 
                                            variant="outline-primary" 
                                            size="sm"
                                            onClick={() => {
                                                setNewTransaction({
                                                    type: 'SELL',
                                                    symbol: position.symbol,
                                                    shares: 0,
                                                    price: position.currentPrice
                                                });
                                                setShowTransactionModal(true);
                                            }}
                                        >
                                            Sell
                                        </Button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            <Modal show={showTransactionModal} onHide={() => setShowTransactionModal(false)}>
                <Modal.Header closeButton>
                    <Modal.Title>Add Transaction</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-3">
                            <Form.Label>Transaction Type</Form.Label>
                            <Form.Select
                                value={newTransaction.type}
                                onChange={(e) => 
                                    setNewTransaction({ 
                                        ...newTransaction, 
                                        type: e.target.value as 'BUY' | 'SELL' 
                                    })
                                }
                            >
                                <option value="BUY">Buy</option>
                                <option value="SELL">Sell</option>
                            </Form.Select>
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Symbol</Form.Label>
                            <Form.Control
                                type="text"
                                value={newTransaction.symbol}
                                onChange={(e) => 
                                    setNewTransaction({ 
                                        ...newTransaction, 
                                        symbol: e.target.value.toUpperCase() 
                                    })
                                }
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Shares</Form.Label>
                            <Form.Control
                                type="number"
                                value={newTransaction.shares}
                                onChange={(e) => 
                                    setNewTransaction({ 
                                        ...newTransaction, 
                                        shares: parseFloat(e.target.value) 
                                    })
                                }
                            />
                        </Form.Group>

                        <Form.Group className="mb-3">
                            <Form.Label>Price</Form.Label>
                            <Form.Control
                                type="number"
                                value={newTransaction.price}
                                onChange={(e) => 
                                    setNewTransaction({ 
                                        ...newTransaction, 
                                        price: parseFloat(e.target.value) 
                                    })
                                }
                            />
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowTransactionModal(false)}>
                        Cancel
                    </Button>
                    <Button variant="primary" onClick={handleTransactionSubmit}>
                        Submit Transaction
                    </Button>
                </Modal.Footer>
            </Modal>
        </>
    );
};

export default PortfolioManagement;