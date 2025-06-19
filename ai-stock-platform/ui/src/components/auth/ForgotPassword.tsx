/**
 * Forgot Password Component
 * Created: 2025-06-19 18:00:37
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import authService from '../../services/auth.service';
import { ROUTES } from '../../config/constants';

// Styles
const styles = {
  container: {
    maxWidth: '400px',
    margin: '50px auto',
    padding: '30px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
    borderRadius: '8px',
    backgroundColor: '#fff',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '30px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '20px',
  },
  inputGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '5px',
  },
  input: {
    padding: '12px',
    borderRadius: '4px',
    border: '1px solid #ddd',
    fontSize: '16px',
  },
  button: {
    padding: '14px',
    backgroundColor: '#1e3a8a',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold' as const,
  },
  infoText: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '20px',
    textAlign: 'center' as const,
  },
  errorMessage: {
    color: 'red',
    marginTop: '10px',
    textAlign: 'center' as const,
  },
  successMessage: {
    padding: '15px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    marginBottom: '20px',
    textAlign: 'center' as const,
  },
  backToLogin: {
    textAlign: 'center' as const,
    marginTop: '20px',
    fontSize: '14px',
  },
  link: {
    color: '#1e3a8a',
    textDecoration: 'none',
  },
};

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
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>QuantumVestAI</h1>
        <h2>Reset Password</h2>
      </div>

      {success ? (
        <>
          <div style={styles.successMessage}>
            If the email address you entered is associated with an account, you will receive password reset instructions shortly.
          </div>
          <div style={styles.backToLogin}>
            <Link to={ROUTES.LOGIN} style={styles.link}>
              Back to login
            </Link>
          </div>
        </>
      ) : (
        <>
          <div style={styles.infoText}>
            Enter your email address and we'll send you instructions on how to reset your password.
          </div>

          <form onSubmit={handleSubmit} style={styles.form}>
            <div style={styles.inputGroup}>
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                style={styles.input}
                disabled={loading}
              />
            </div>

            {error && <div style={styles.errorMessage}>{error}</div>}

            <button 
              type="submit" 
              style={styles.button}
              disabled={loading}
            >
              {loading ? 'Sending...' : 'Send Reset Instructions'}
            </button>

            <div style={styles.backToLogin}>
              <Link to={ROUTES.LOGIN} style={styles.link}>
                Back to login
              </Link>
            </div>
          </form>
        </>
      )}
    </div>
  );
};

export default ForgotPassword;