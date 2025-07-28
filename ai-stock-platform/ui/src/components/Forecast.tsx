import React from 'react';
import { Container, Alert, Button } from 'react-bootstrap';

const Forecast: React.FC = () => {
  return (
    <Container>
      <Alert variant='info'>
        <Alert.Heading>Forecast</Alert.Heading>
        <p>This feature is under development. Forecast analytics will be available soon.</p>
        <Button variant='primary'>Coming Soon</Button>
      </Alert>
    </Container>
  );
};

export default Forecast;
