/**
 * Stocks Component
 * Stock listing and search functionality
 */
import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Table } from 'react-bootstrap';

const Stocks: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const mockStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.', price: 198.45, change: 4.12, changePercent: 2.1, volume: '45.2M' },
    { symbol: 'MSFT', name: 'Microsoft Corporation', price: 425.63, change: 7.56, changePercent: 1.8, volume: '23.1M' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation', price: 1024.78, change: 32.45, changePercent: 3.2, volume: '67.8M' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 176.89, change: 2.14, changePercent: 1.2, volume: '18.9M' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 187.12, change: 2.78, changePercent: 1.5, volume: '34.6M' },
  ];

  const filteredStocks = mockStocks.filter(stock =>
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container fluid>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Stocks</h1>
        <Button variant="primary">Add to Watchlist</Button>
      </div>

      <Row className="mb-4">
        <Col md={6}>
          <Form.Group>
            <Form.Control
              type="text"
              placeholder="Search stocks by symbol or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </Form.Group>
        </Col>
        <Col md={6}>
          <div className="d-flex gap-2">
            <Form.Select>
              <option>All Sectors</option>
              <option>Technology</option>
              <option>Healthcare</option>
              <option>Finance</option>
              <option>Energy</option>
            </Form.Select>
            <Form.Select>
              <option>Market Cap</option>
              <option>Large Cap</option>
              <option>Mid Cap</option>
              <option>Small Cap</option>
            </Form.Select>
          </div>
        </Col>
      </Row>

      <Card>
        <Card.Body>
          <Table responsive hover>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Name</th>
                <th>Price</th>
                <th>Change</th>
                <th>Change %</th>
                <th>Volume</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStocks.map((stock, index) => (
                <tr key={index}>
                  <td><strong>{stock.symbol}</strong></td>
                  <td>{stock.name}</td>
                  <td>${stock.price.toFixed(2)}</td>
                  <td className={stock.change >= 0 ? 'text-success' : 'text-danger'}>
                    {stock.change >= 0 ? '+' : ''}${stock.change.toFixed(2)}
                  </td>
                  <td className={stock.changePercent >= 0 ? 'text-success' : 'text-danger'}>
                    {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(1)}%
                  </td>
                  <td>{stock.volume}</td>
                  <td>
                    <Button size="sm" variant="outline-primary" className="me-1">
                      View
                    </Button>
                    <Button size="sm" variant="outline-success">
                      + Watch
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Stocks;