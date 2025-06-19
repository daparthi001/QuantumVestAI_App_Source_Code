/**
 * Login Component
 * Created: 2025-06-19 19:01:49
 * Author: daparthi001
 */
import authService from '../services/auth-service';

class Login {
  constructor() {
    this.loginForm = document.getElementById('login-form');
    this.usernameInput = document.getElementById('username');
    this.passwordInput = document.getElementById('password');
    this.errorMessage = document.getElementById('error-message');
    this.loginButton = document.getElementById('login-button');
    
    this.registerEvents();
  }
  
  /**
   * Register event listeners
   */
  registerEvents() {
    if (this.loginForm) {
      this.loginForm.addEventListener('submit', this.handleSubmit.bind(this));
    }
  }
  
  /**
   * Handle form submission
   * @param {Event} event - Form submit event
   */
  async handleSubmit(event) {
    event.preventDefault();
    
    // Clear previous error
    this.setErrorMessage('');
    
    // Get form values
    const username = this.usernameInput.value.trim();
    const password = this.passwordInput.value;
    
    // Validate form
    if (!username) {
      this.setErrorMessage('Username is required');
      return;
    }
    
    if (!password) {
      this.setErrorMessage('Password is required');
      return;
    }
    
    // Disable form during submission
    this.setLoading(true);
    
    try {
      // Attempt login
      await authService.login(username, password);
      
      // Redirect to dashboard on success
      window.location.href = '/dashboard';
    } catch (error) {
      console.error('Login failed', error);
      
      // Display error message
      if (error.status === 401) {
        this.setErrorMessage('Invalid username or password');
      } else {
        this.setErrorMessage(error.message || 'Login failed. Please try again.');
      }
    } finally {
      this.setLoading(false);
    }
  }
  
  /**
   * Set error message
   * @param {string} message - Error message
   */
  setErrorMessage(message) {
    if (this.errorMessage) {
      this.errorMessage.textContent = message;
      this.errorMessage.style.display = message ? 'block' : 'none';
    }
  }
  
  /**
   * Set loading state
   * @param {boolean} isLoading - Loading state
   */
  setLoading(isLoading) {
    if (this.loginButton) {
      this.loginButton.disabled = isLoading;
      this.loginButton.textContent = isLoading ? 'Logging in...' : 'Login';
    }
    
    if (this.usernameInput) {
      this.usernameInput.disabled = isLoading;
    }
    
    if (this.passwordInput) {
      this.passwordInput.disabled = isLoading;
    }
  }
}

// Initialize login component when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new Login();
});