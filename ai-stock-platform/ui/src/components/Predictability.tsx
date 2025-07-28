import React from 'react';
import { Container, Alert, Button } from 'react-bootstrap';

const Predictability: React.FC = () => {
  return (
    <Container>
      <Alert variant='info'>
        <Alert.Heading>Predictability</Alert.Heading>
        <p>This section will analyze how predictable a stock's price movements are.</p>
        <Button variant='primary'>Coming Soon</Button>
      </Alert>
    </Container>
  );
};

export default Predictability;
