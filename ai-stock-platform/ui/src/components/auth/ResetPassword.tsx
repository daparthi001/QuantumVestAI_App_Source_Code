/**
 * Reset Password Component
 * Created: 2025-06-19 18:00:37
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
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
  passwordRequirements: {
    fontSize: '12px',
    color: '#666',
    marginTop: '5px',
  },
};

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token') || '';

  const [password, setPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');

    if (!password) {
      setError('Password is required');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!token) {
      setError('Invalid or missing reset token');
      return;
    }

    setLoading(true);

    try {
      await authService.resetPassword(token, password);
      setSuccess(true);
      
      // Redirect to login after brief delay
      setTimeout(() => {
        navigate(ROUTES.LOGIN);
      }, 3000);
    } catch (err: any) {
      console.error('Password reset error:', err);
      if (err.response && err.response.status === 400) {
        setError('Invalid or expired token');
      } else if (err.message === 'Network Error') {
        setError('Network error. Please check your connection and try again.');
      } else {
        setError('Password reset failed. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  // If no token is provided, show error
  if (!token) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1>QuantumVestAI</h1>
          <h2>Reset Password</h2>
        </div>
        <div style={styles.errorMessage}>
          Invalid or missing reset token. Please request a new password reset link.
        </div>
        <div style={styles.backToLogin}>
          <Link to={ROUTES.FORGOT_PASSWORD} style={styles.link}>
            Request new password reset
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>QuantumVestAI</h1>
        <h2>Set New Password</h2>
      </div>

      {success ? (
        <>
          <div style={styles.successMessage}>
            Your password has been reset successfully! Redirecting to login page...
          </div>
          <div style={styles.backToLogin}>
            <Link to={ROUTES.LOGIN} style={styles.link}>
              Back to login
            </Link>
          </div>
        </>
      ) : (
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputGroup}>
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter new password"
              style={styles.input}
              disabled={loading}
            />
            <div style={styles.passwordRequirements}>
              Password must be at least 8 characters long
            </div>
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
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
            {loading ? 'Resetting Password...' : 'Reset Password'}
          </button>

          <div style={styles.backToLogin}>
            <Link to={ROUTES.LOGIN} style={styles.link}>
              Back to login
            </Link>
          </div>
        </form>
      )}
    </div>
  );
};

export default ResetPassword;