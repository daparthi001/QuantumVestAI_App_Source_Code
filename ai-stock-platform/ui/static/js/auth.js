/**
 * Authentication utilities for QuantumVestAI
 * Updated: 2025-01-09
 * Author: daparthi001
 */

document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const toggleButtons = document.querySelectorAll('.password-toggle');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const input = this.parentNode.querySelector('input');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            
            // Toggle icon
            const icon = this.querySelector('i');
            icon.classList.toggle('bi-eye');
            icon.classList.toggle('bi-eye-slash');
        });
    });

    // Login form handling
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous errors
            UIErrorHandler.clearFormErrors(loginForm);
            
            // Get form data
            const formData = new FormData(loginForm);
            const username = formData.get('username');
            const password = formData.get('password');
            const remember = formData.get('remember') === 'true';
            
            // Validate inputs
            let hasErrors = false;
            
            if (!username || username.trim().length < 3) {
                UIErrorHandler.showFormError('username', 'Username must be at least 3 characters long');
                hasErrors = true;
            }
            
            if (!password || password.length < 3) {
                UIErrorHandler.showFormError('password', 'Password must be at least 3 characters long');
                hasErrors = true;
            }
            
            if (hasErrors) {
                return;
            }
            
            // Show loading state on submit button
            const submitButton = loginForm.querySelector('button[type="submit"]');
            LoadingManager.showButtonLoading(submitButton, 'Signing In...');
            
            try {
                // Just submit the form normally - the server will handle it
                loginForm.submit();
            } catch (error) {
                console.error('Login submission error:', error);
                LoadingManager.hideButtonLoading(submitButton);
                UIErrorHandler.showError('Login failed. Please try again.');
            }
        });
        
        // Clear field errors on input
        const usernameInput = loginForm.querySelector('[name="username"]');
        const passwordInput = loginForm.querySelector('[name="password"]');
        
        if (usernameInput) {
            usernameInput.addEventListener('blur', function() {
                UIErrorHandler.clearFormError('username');
                if (this.value.length > 0 && this.value.length < 3) {
                    UIErrorHandler.showFormError('username', 'Username must be at least 3 characters long');
                }
            });
        }
        
        if (passwordInput) {
            passwordInput.addEventListener('blur', function() {
                UIErrorHandler.clearFormError('password');
                if (this.value.length > 0 && this.value.length < 3) {
                    UIErrorHandler.showFormError('password', 'Password must be at least 3 characters long');
                }
            });
        }
    }

    // Registration form handling
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Clear previous errors
            UIErrorHandler.clearFormErrors(registerForm);
            
            // Get form data
            const formData = new FormData(registerForm);
            const username = formData.get('username');
            const email = formData.get('email');
            const password = formData.get('password');
            const confirmPassword = formData.get('confirm_password');
            const terms = formData.get('terms') === 'on';
            
            // Validate inputs
            let hasErrors = false;
            
            if (!username || username.trim().length < 3) {
                UIErrorHandler.showFormError('username', 'Username must be at least 3 characters long');
                hasErrors = true;
            }
            
            if (!email || !email.includes('@')) {
                UIErrorHandler.showFormError('email', 'Please enter a valid email address');
                hasErrors = true;
            }
            
            if (!password || password.length < 8) {
                UIErrorHandler.showFormError('password', 'Password must be at least 8 characters long');
                hasErrors = true;
            }
            
            if (password !== confirmPassword) {
                UIErrorHandler.showFormError('confirm_password', 'Passwords do not match');
                hasErrors = true;
            }
            
            if (!terms) {
                UIErrorHandler.showFormError('terms', 'You must accept the Terms of Service');
                hasErrors = true;
            }
            
            if (hasErrors) {
                return;
            }
            
            // Show loading state on submit button
            const submitButton = registerForm.querySelector('button[type="submit"]');
            LoadingManager.showButtonLoading(submitButton, 'Creating Account...');
            
            try {
                // Just submit the form normally - the server will handle it
                registerForm.submit();
            } catch (error) {
                console.error('Registration submission error:', error);
                LoadingManager.hideButtonLoading(submitButton);
                UIErrorHandler.showError('Registration failed. Please try again.');
            }
        });
    }
});

// Global auth utilities object
window.authUtils = {
    // Get stored authentication token
    getToken: function() {
        const token = localStorage.getItem('access_token') || 
                     sessionStorage.getItem('access_token') ||
                     this.getTokenFromCookie();
        return token;
    },
    
    // Get token from cookie
    getTokenFromCookie: function() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='));
        
        if (cookieValue) {
            return cookieValue.split('=')[1].replace('Bearer%20', '').replace('Bearer ', '');
        }
        return null;
    },
    
    // Store authentication token
    setToken: function(token, remember = false) {
        if (remember) {
            localStorage.setItem('access_token', token);
        } else {
            sessionStorage.setItem('access_token', token);
        }
    },
    
    // Remove authentication token
    removeToken: function() {
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('access_token');
        // Also remove from cookie
        document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    },
    
    // Check if user is authenticated
    isAuthenticated: function() {
        return !!this.getToken();
    },
    
    // Logout user
    logout: function() {
        this.removeToken();
        window.location.href = '/logout';
    },
    
    // Check auth token and redirect if not authenticated
    requireAuth: function() {
        if (!this.isAuthenticated()) {
            const currentPath = window.location.pathname + window.location.search;
            window.location.href = `/login?next=${encodeURIComponent(currentPath)}`;
            return false;
        }
        return true;
    }
};