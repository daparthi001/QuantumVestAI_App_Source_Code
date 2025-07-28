import React from 'react';
import { Container, Alert, Button } from 'react-bootstrap';

const Market: React.FC = () => {
  return (
    <Container>
      <Alert variant='info'>
        <Alert.Heading>Market Overview</Alert.Heading>
        <p>Detailed market data will appear here once implemented.</p>
        <Button variant='primary'>Coming Soon</Button>
      </Alert>
    </Container>
  );
};

export default Market;
