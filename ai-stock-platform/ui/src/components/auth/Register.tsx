/**
 * Register Component
 * Created: 2025-06-19 18:00:37
 * Author: daparthi001
 */
import React, { useState, FormEvent } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../services/auth.service';
import { ROUTES } from '../../config/constants';

// Form validation
interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

// Register component styles
const styles = {
  container: {
    maxWidth: '500px',
    margin: '40px auto',
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
    marginTop: '10px',
  },
  errorText: {
    color: 'red',
    fontSize: '14px',
    marginTop: '5px',
  },
  successMessage: {
    padding: '15px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    marginBottom: '20px',
    textAlign: 'center' as const,
  },
  loginLink: {
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
  formError: {
    color: 'red',
    marginTop: '10px',
    textAlign: 'center' as const,
  },
};

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
    <div style={styles.container}>
      <div style={styles.header}>
        <h1>QuantumVestAI</h1>
        <h2>Create Account</h2>
      </div>

      {success && (
        <div style={styles.successMessage}>
          Registration successful! Redirecting to login page...
        </div>
      )}

      <form onSubmit={handleSubmit} style={styles.form}>
        <div style={styles.inputGroup}>
          <label htmlFor="username">Username *</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter a username"
            style={styles.input}
            disabled={loading || success}
          />
          {errors.username && <div style={styles.errorText}>{errors.username}</div>}
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="email">Email *</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            style={styles.input}
            disabled={loading || success}
          />
          {errors.email && <div style={styles.errorText}>{errors.email}</div>}
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="fullName">Full Name (Optional)</label>
          <input
            id="fullName"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Enter your full name"
            style={styles.input}
            disabled={loading || success}
          />
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="password">Password *</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Create a password"
            style={styles.input}
            disabled={loading || success}
          />
          {errors.password && <div style={styles.errorText}>{errors.password}</div>}
          <div style={styles.passwordRequirements}>
            Password must be at least 8 characters long
          </div>
        </div>

        <div style={styles.inputGroup}>
          <label htmlFor="confirmPassword">Confirm Password *</label>
          <input
            id="confirmPassword"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Confirm your password"
            style={styles.input}
            disabled={loading || success}
          />
          {errors.confirmPassword && <div style={styles.errorText}>{errors.confirmPassword}</div>}
        </div>

        {formError && <div style={styles.formError}>{formError}</div>}

        <button
          type="submit"
          style={styles.button}
          disabled={loading || success}
        >
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>

        <div style={styles.loginLink}>
          Already have an account?{' '}
          <Link to={ROUTES.LOGIN} style={styles.link}>
            Log in
          </Link>
        </div>
      </form>
    </div>
  );
};

export default Register;