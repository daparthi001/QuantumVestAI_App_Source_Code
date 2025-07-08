/**
 * Register Component - Quantum Design System
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

// Form validation
interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState<string>('');
  const [email, setEmail] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [success, setSuccess] = useState<boolean>(false);
  const [formError, setFormError] = useState<string>('');
  const [errors, setErrors] = useState<FormErrors>({});

  // Validate form fields
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;

    // Validate username
    if (!username) {
      newErrors.username = 'Username is required';
      isValid = false;
    } else if (username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters';
      isValid = false;
    }

    // Validate email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      newErrors.email = 'Email is required';
      isValid = false;
    } else if (!emailRegex.test(email)) {
      newErrors.email = 'Please enter a valid email address';
      isValid = false;
    }

    // Validate password
    if (!password) {
      newErrors.password = 'Password is required';
      isValid = false;
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
      isValid = false;
    }

    // Validate password confirmation
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Handle form submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setFormError('');

    // Validate form
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      // Register user
      await authService.register({
        username,
        email,
        password,
        full_name: fullName || undefined,
      });

      // Show success message
      setSuccess(true);
      
      // Clear form
      setUsername('');
      setEmail('');
      setFullName('');
      setPassword('');
      setConfirmPassword('');
      setErrors({});
      
      // Redirect to login after brief delay
      setTimeout(() => {
        navigate(ROUTES.LOGIN);
      }, 3000);
    } catch (err: any) {
      console.error('Registration error:', err);
      
      // Set appropriate error message based on error response
      if (err.response && err.response.status === 400) {
        if (err.response.data && err.response.data.detail) {
          setFormError(err.response.data.detail);
        } else {
          setFormError('Username or email already exists');
        }
      } else if (err.message === 'Network Error') {
        setFormError('Network error. Please check your connection and try again.');
      } else {
        setFormError('Registration failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="quantum-bg min-vh-100 d-flex align-items-center justify-content-center">
      <Container>
        <Row className="justify-content-center">
          <Col md={8} lg={6}>
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
                      <h2 className="text-muted">Join the Future</h2>
                    </motion.div>
                  </div>

                  {/* Success Message */}
                  <AnimatePresence>
                    {success && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <Alert variant="success" className="mb-3">
                          <motion.span
                            className="me-2"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 1, repeat: Infinity }}
                          >
                            🎉
                          </motion.span>
                          Registration successful! Redirecting to login page...
                        </Alert>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* Registration Form */}
                  <Form onSubmit={handleSubmit}>
                    <AnimatePresence>
                      {formError && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                        >
                          <Alert variant="danger" className="mb-3">
                            {formError}
                          </Alert>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Form Fields */}
                    <Row>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: 0.3 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label>Username <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                              type="text"
                              value={username}
                              onChange={(e) => setUsername(e.target.value)}
                              placeholder="Enter a username"
                              disabled={loading || success}
                              className="quantum-input"
                              isInvalid={!!errors.username}
                            />
                            <Form.Control.Feedback type="invalid">
                              {errors.username}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </motion.div>
                      </Col>

                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: 0.4 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label>Email <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                              type="email"
                              value={email}
                              onChange={(e) => setEmail(e.target.value)}
                              placeholder="Enter your email"
                              disabled={loading || success}
                              className="quantum-input"
                              isInvalid={!!errors.email}
                            />
                            <Form.Control.Feedback type="invalid">
                              {errors.email}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </motion.div>
                      </Col>
                    </Row>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.5 }}
                    >
                      <Form.Group className="mb-3">
                        <Form.Label>Full Name (Optional)</Form.Label>
                        <Form.Control
                          type="text"
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                          placeholder="Enter your full name"
                          disabled={loading || success}
                          className="quantum-input"
                        />
                      </Form.Group>
                    </motion.div>

                    <Row>
                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: 0.6 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label>Password <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                              type="password"
                              value={password}
                              onChange={(e) => setPassword(e.target.value)}
                              placeholder="Create a password"
                              disabled={loading || success}
                              className="quantum-input"
                              isInvalid={!!errors.password}
                            />
                            <Form.Control.Feedback type="invalid">
                              {errors.password}
                            </Form.Control.Feedback>
                            <Form.Text className="text-muted">
                              Password must be at least 8 characters long
                            </Form.Text>
                          </Form.Group>
                        </motion.div>
                      </Col>

                      <Col md={6}>
                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.5, delay: 0.7 }}
                        >
                          <Form.Group className="mb-3">
                            <Form.Label>Confirm Password <span className="text-danger">*</span></Form.Label>
                            <Form.Control
                              type="password"
                              value={confirmPassword}
                              onChange={(e) => setConfirmPassword(e.target.value)}
                              placeholder="Confirm your password"
                              disabled={loading || success}
                              className="quantum-input"
                              isInvalid={!!errors.confirmPassword}
                            />
                            <Form.Control.Feedback type="invalid">
                              {errors.confirmPassword}
                            </Form.Control.Feedback>
                          </Form.Group>
                        </motion.div>
                      </Col>
                    </Row>

                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.8 }}
                    >
                      <Button
                        type="submit"
                        className="quantum-btn w-100 mb-3"
                        disabled={loading || success}
                        size="lg"
                      >
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Creating Account...
                          </>
                        ) : (
                          <>
                            <motion.span
                              className="me-2"
                              animate={{ scale: [1, 1.1, 1] }}
                              transition={{ duration: 1.5, repeat: Infinity }}
                            >
                              🚀
                            </motion.span>
                            Create Account
                          </>
                        )}
                      </Button>
                    </motion.div>

                    {/* Login Link */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.5, delay: 0.9 }}
                      className="text-center"
                    >
                      <span className="text-muted">Already have an account? </span>
                      <Link 
                        to={ROUTES.LOGIN} 
                        className="text-decoration-none quantum-link"
                      >
                        Log in
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

export default Register;