/**
 * Login Component - Quantum Design System
 * Enhanced with modern UI/UX and glass morphism effects
 * Updated: 2025-01-09
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';
import authService from '../../services/auth.service';
import { ROUTES } from '../../config/constants';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!username || !password) {
      setError('Username and password are required');
      setLoading(false);
      return;
    }

    try {
      const response = await authService.login(username, password);
      console.log('Login successful:', response);
      
      // Redirect to dashboard after successful login
      navigate(ROUTES.DASHBOARD);
    } catch (err: any) {
      console.error('Login error:', err);
      
      // Set appropriate error message based on error response
      if (err.response && err.response.status === 401) {
        setError('Invalid username or password');
      } else if (err.response && err.response.status === 403) {
        setError('Your account is inactive or blocked');
      } else if (err.message === 'Network Error') {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Login failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Login with demo account
  const handleDemoLogin = async () => {
    setError('');
    setLoading(true);
    try {
      await authService.login('demo', 'password');
      navigate(ROUTES.DASHBOARD);
    } catch (err: any) {
      console.error('Demo login error:', err);
      setError('Demo login failed. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="quantum-bg min-vh-100 d-flex align-items-center justify-content-center">
      <Container>
        <Row className="justify-content-center">
          <Col md={6} lg={4}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="quantum-card shadow-lg">
                <Card.Body className="p-5">
                  {/* Header */}
                  <div className="text-center mb-4">
                    <motion.div
                      initial={{ scale: 0.8 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.5, delay: 0.2 }}
                    >
                      <h1 className="quantum-text-gradient mb-2">
                        <motion.span
                          className="me-2"
                          animate={{ rotate: 360 }}
                          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        >
                          ⚛️
                        </motion.span>
                        QuantumVestAI
                      </h1>
                      <h2 className="text-muted">Welcome Back</h2>
                    </motion.div>
                  </div>

                  {/* Login Form */}
                  <Form onSubmit={handleSubmit}>
                    <AnimatePresence>
                      {error && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <Alert variant="danger" className="mb-3">
                            {error}
                          </Alert>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 0.3 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label>Username</Form.Label>
                        <Form.Control
                          type="text"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                          placeholder="Enter your username"
                          disabled={loading}
                          autoComplete="username"
                          className="quantum-input"
                        />
                      </Form.Group>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: 0.4 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label>Password</Form.Label>
                        <Form.Control
                          type="password"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          placeholder="Enter your password"
                          disabled={loading}
                          autoComplete="current-password"
                          className="quantum-input"
                        />
                        <div className="text-end mt-2">
                          <Link 
                            to={ROUTES.FORGOT_PASSWORD} 
                            className="text-decoration-none quantum-link"
                          >
                            Forgot password?
                          </Link>
                        </div>
                      </Form.Group>
                    </motion.div>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.5 }}
                    >
                      <Button
                        type="submit"
                        className="quantum-btn w-100 mb-3"
                        disabled={loading}
                      >
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Logging in...
                          </>
                        ) : (
                          'Login'
                        )}
                      </Button>
                    </motion.div>

                    {/* Divider */}
                    <div className="d-flex align-items-center my-4">
                      <div className="flex-grow-1 border-top"></div>
                      <span className="mx-3 text-muted">or</span>
                      <div className="flex-grow-1 border-top"></div>
                    </div>

                    {/* Demo Account Button */}
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.6 }}
                    >
                      <Button
                        variant="outline-primary"
                        className="quantum-btn-outline w-100 mb-3"
                        onClick={handleDemoLogin}
                        disabled={loading}
                      >
                        <motion.span
                          className="me-2"
                          animate={{ scale: [1, 1.2, 1] }}
                          transition={{ duration: 2, repeat: Infinity }}
                        >
                          🚀
                        </motion.span>
                        Continue with Demo Account
                      </Button>
                    </motion.div>

                    {/* Register Link */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.5, delay: 0.7 }}
                      className="text-center"
                    >
                      <span className="text-muted">Don't have an account? </span>
                      <Link 
                        to={ROUTES.REGISTER} 
                        className="text-decoration-none quantum-link"
                      >
                        Sign up
                      </Link>
                    </motion.div>
                  </Form>
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default Login;