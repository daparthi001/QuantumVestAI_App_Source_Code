/**
 * Login Component
 * Updated: 2025-06-19 18:00:37
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../services/auth.service';
import { ROUTES } from '../../config/constants';

// Login component styles
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
  registerLink: {
    textAlign: 'center' as const,
    marginTop: '20px',
    fontSize: '14px',
  },
  forgotPassword: {
    textAlign: 'right' as const,
    marginTop: '5px',
    fontSize: '14px',
  },
  link: {
    color: '#1e3a8a',
    textDecoration: 'none',
  },
  errorMessage: {
    color: 'red',
    marginTop: '10px',
    textAlign: 'center' as const,
  },
  orDivider: {
    display: 'flex',
    alignItems: 'center',
    margin: '20px 0',
  },
  line: {
    flex: '1',
    height: '1px',
    backgroundColor: '#ddd',
  },
  orText: {
    padding: '0 10px',
    color: '#888',
    fontSize: '14px',
  },
  demoAccount: {
    marginTop: '10px',
    padding: '14px',
    backgroundColor: '#4a5568',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    textAlign: 'center' as const,
    fontWeight: 'bold' as const,
  },
};

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
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>QuantumVestAI</h1>
        <h2>Login</h2>
      </div>

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputGroup}>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your username"
            style={styles.input}
            disabled={loading}
            autoComplete="username"
          />
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
            style={styles.input}
            disabled={loading}
            autoComplete="current-password"
          />
          <div style={styles.forgotPassword}>
            <Link to={ROUTES.FORGOT_PASSWORD} style={styles.link}>
              Forgot password?
            </Link>
          </div>
        </div>

        {error && <div style={styles.errorMessage}>{error}</div>}

        <button 
          type="submit" 
          style={styles.button}
          disabled={loading}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>
        
        <div style={styles.orDivider}>
          <div style={styles.line}></div>
          <div style={styles.orText}>or</div>
          <div style={styles.line}></div>
        </div>
        
        <div 
          style={styles.demoAccount}
          onClick={handleDemoLogin}
        >
          Continue with Demo Account
        </div>

        <div style={styles.registerLink}>
          Don't have an account?{' '}
          <Link to={ROUTES.REGISTER} style={styles.link}>
            Sign up
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Login;