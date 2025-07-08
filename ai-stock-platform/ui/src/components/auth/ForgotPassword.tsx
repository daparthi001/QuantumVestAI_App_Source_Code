/**
 * Forgot Password Component - Quantum Design System
 * Enhanced with modern UI/UX and glass morphism effects
 * Updated: 2025-01-09
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';
import authService from '../../services/auth.service';
import { ROUTES } from '../../config/constants';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Email is required');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setLoading(true);

    try {
      await authService.requestPasswordReset(email);
      setSuccess(true);
    } catch (err: any) {
      console.error('Password reset request error:', err);
      if (err.message === 'Network Error') {
        setError('Network error. Please check your connection and try again.');
      } else {
        // Don't reveal if email exists or not for security
        setSuccess(true);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="quantum-bg min-vh-100 d-flex align-items-center justify-content-center">
      <Container>
        <Row className="justify-content-center">
          <Col md={6} lg={5}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="quantum-card shadow-lg">
                <Card.Body className="p-5">
                  {success ? (
                    <motion.div
                      initial={{ scale: 0.8 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.5 }}
                      className="text-center"
                    >
                      <motion.div
                        className="mb-4"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <div className="display-1">📧</div>
                      </motion.div>
                      <h2 className="quantum-text-gradient mb-3">Check Your Email</h2>
                      <Alert variant="success" className="text-start">
                        <p className="mb-2">If the email address you entered is associated with an account, you will receive password reset instructions shortly.</p>
                      </Alert>
                      <p className="text-muted mb-4">
                        Please check your email and follow the instructions to reset your password.
                        Don't forget to check your spam folder!
                      </p>
                      <Link to={ROUTES.LOGIN} className="btn quantum-btn w-100">
                        <span className="me-2">←</span>
                        Back to Login
                      </Link>
                    </motion.div>
                  ) : (
                    <>
                      {/* Header */}
                      <div className="text-center mb-4">
                        <motion.div
                          initial={{ scale: 0.8 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.5, delay: 0.2 }}
                        >
                          <motion.div
                            className="mb-3 display-3"
                            animate={{ rotate: [0, 10, -10, 0] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          >
                            🔑
                          </motion.div>
                          <h1 className="quantum-text-gradient mb-2">Reset Password</h1>
                          <p className="text-muted">Enter your email address and we'll send you instructions on how to reset your password.</p>
                        </motion.div>
                      </div>

                      {/* Reset Form */}
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
                          <Form.Group className="mb-4">
                            <Form.Label>Email Address</Form.Label>
                            <Form.Control
                              type="email"
                              value={email}
                              onChange={(e) => setEmail(e.target.value)}
                              placeholder="Enter your email address"
                              disabled={loading}
                              className="quantum-input"
                              size="lg"
                              required
                            />
                          </Form.Group>
                        </motion.div>

                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.5, delay: 0.4 }}
                        >
                          <Button
                            type="submit"
                            className="quantum-btn w-100 mb-3"
                            disabled={loading}
                            size="lg"
                          >
                            {loading ? (
                              <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Sending Instructions...
                              </>
                            ) : (
                              <>
                                <motion.span
                                  className="me-2"
                                  animate={{ scale: [1, 1.2, 1] }}
                                  transition={{ duration: 1.5, repeat: Infinity }}
                                >
                                  📧
                                </motion.span>
                                Send Reset Instructions
                              </>
                            )}
                          </Button>
                        </motion.div>

                        {/* Back to Login */}
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ duration: 0.5, delay: 0.5 }}
                          className="text-center"
                        >
                          <span className="text-muted">Remember your password? </span>
                          <Link 
                            to={ROUTES.LOGIN} 
                            className="text-decoration-none quantum-link"
                          >
                            <span className="me-1">←</span>
                            Back to Login
                          </Link>
                        </motion.div>
                      </Form>
                    </>
                  )}
                </Card.Body>
              </Card>
            </motion.div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default ForgotPassword;