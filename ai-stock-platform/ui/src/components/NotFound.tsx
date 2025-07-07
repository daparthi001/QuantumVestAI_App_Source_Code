/**
 * Not Found Component
 * 404 error page
 */
import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../config/constants';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container>
      <Row className="justify-content-center text-center" style={{ minHeight: '70vh' }}>
        <Col md={6} className="d-flex flex-column justify-content-center">
          <h1 className="display-1 fw-bold text-primary">404</h1>
          <h2 className="mb-4">Page Not Found</h2>
          <p className="lead text-muted mb-4">
            Sorry, the page you are looking for doesn't exist or has been moved.
          </p>
          <div>
            <Button as={Link as any} to={ROUTES.DASHBOARD} variant="primary" size="lg" className="me-3">
              Go to Dashboard
            </Button>
            <Button as={Link as any} to={ROUTES.STOCKS} variant="outline-primary" size="lg">

              Browse Stocks
            </Button>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default NotFound;