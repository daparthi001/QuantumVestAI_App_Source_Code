/**
 * QuantumVestAI Registration Fix
 * Created: 2025-06-17 04:07:15
 * Author: daparthi001
 * 
 * This script fixes registration form submissions when working with AWS ALB Ingress
 */
(function() {
  console.log('QuantumVestAI Registration Fix - Version 2025.06.17.2');
  
  // Wait for DOM to be fully loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Find the registration form
    const form = document.querySelector('form');
    if (!form) {
      console.warn('Registration form not found');
      return;
    }
    
    console.log('Registration form found - applying fix');
    
    // Override the form submission
    form.addEventListener('submit', async function(event) {
      // Prevent default form submission
      event.preventDefault();
      
      // Get form elements
      const usernameField = document.querySelector('input[name="username"]');
      const emailField = document.querySelector('input[name="email"]');
      const passwordField = document.querySelector('input[name="password"]');
      const passwordConfirmField = document.querySelector('input[name="confirm_password"]') || 
                                document.querySelector('input[name="passwordConfirm"]');
      
      if (!usernameField || !emailField || !passwordField) {
        console.error('Required form fields not found');
        showError('Registration form is missing required fields. Please refresh and try again.');
        return;
      }
      
      const username = usernameField.value.trim();
      const email = emailField.value.trim();
      const password = passwordField.value;
      
      // Basic client-side validation
      if (!username) {
        showError('Username is required');
        usernameField.focus();
        return;
      }
      
      if (!email) {
        showError('Email is required');
        emailField.focus();
        return;
      }
      
      if (!password) {
        showError('Password is required');
        passwordField.focus();
        return;
      }
      
      if (passwordConfirmField && passwordConfirmField.value !== password) {
        showError('Passwords do not match');
        passwordConfirmField.focus();
        return;
      }
      
      // Prepare data for submission
      const formData = {
        username: username,
        email: email,
        password: password
      };
      
      try {
        // Show loading indicator
        showLoading();
        
        // Get the form action URL, fallback to API endpoint if not specified
        const url = form.action || '/api/auth/register';
        
        // Send registration request
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: JSON.stringify(formData),
          credentials: 'same-origin'
        });
        
        const data = await response.json();
        
        // Hide loading indicator
        hideLoading();
        
        if (!response.ok) {
          // Show error message from server
          showError(data.message || 'Registration failed. Please try again.');
          return;
        }
        
        // Registration successful
        showSuccess('Registration successful! Please log in.');
        
        // Redirect to login page after a delay
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
        
      } catch (error) {
        // Hide loading indicator
        hideLoading();
        
        // Show error message
        console.error('Registration error:', error);
        showError('An unexpected error occurred. Please try again later.');
      }
    });
  });
  
  // Helper functions
  function showError(message) {
    // Find error container or create one
    let errorContainer = document.querySelector('.error-message');
    if (!errorContainer) {
      errorContainer = document.createElement('div');
      errorContainer.className = 'error-message';
      const form = document.querySelector('form');
      form.insertBefore(errorContainer, form.firstChild);
    }
    
    // Set error message and show
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
  }
  
  function showSuccess(message) {
    // Find success container or create one
    let successContainer = document.querySelector('.success-message');
    if (!successContainer) {
      successContainer = document.createElement('div');
      successContainer.className = 'success-message';
      const form = document.querySelector('form');
      form.insertBefore(successContainer, form.firstChild);
    }
    
    // Set success message and show
    successContainer.textContent = message;
    successContainer.style.display = 'block';
  }
  
  function showLoading() {
    // Create or show loading indicator
    let loadingIndicator = document.querySelector('.loading-indicator');
    if (!loadingIndicator) {
      loadingIndicator = document.createElement('div');
      loadingIndicator.className = 'loading-indicator';
      loadingIndicator.innerHTML = 'Processing registration...';
      const form = document.querySelector('form');
      form.appendChild(loadingIndicator);
    }
    
    loadingIndicator.style.display = 'block';
  }
  
  function hideLoading() {
    // Hide loading indicator
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
  }
})();