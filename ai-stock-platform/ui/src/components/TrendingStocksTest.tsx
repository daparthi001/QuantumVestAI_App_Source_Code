import React from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import TrendingStocks from './TrendingStocks';

const TrendingStocksTest: React.FC = () => {
  return (
    <Container className="py-4">
      <Row>
        <Col lg={12}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Trending Stocks Component Test</h5>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">
                This is a test page to verify the TrendingStocks component works correctly.
              </p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row>
        <Col lg={6}>
          <h6>Default Configuration</h6>
          <TrendingStocks />
        </Col>
        <Col lg={6}>
          <h6>Compact Configuration</h6>
          <TrendingStocks 
            limit={5}
            refreshInterval={30000}
            showHeader={false}
            compact={true}
          />
        </Col>
      </Row>
    </Container>
  );
};

export default TrendingStocksTest;