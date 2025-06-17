/**
 * Authentication utilities for QuantumVestAI UI
 * Created: 2025-06-16
 * Updated: 2025-06-17 16:20:02
 * Author: daparthi001yes
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

    // API authentication helper functions
    window.authUtils = {
        // Get the authentication token from cookies or localStorage
        getToken: function() {
            // Try to get from localStorage first (for SPA usage)
            const token = localStorage.getItem('auth_token');
            if (token) {
                return token;
            }
            
            // If not in localStorage, the cookie will be sent automatically by browser
            return null;
        },
        
        // Set authentication token
        setToken: function(token) {
            localStorage.setItem('auth_token', token);
        },
        
        // Remove token (logout)
        removeToken: function() {
            localStorage.removeItem('auth_token');
        },
        
        // Check if user is authenticated
        isAuthenticated: function() {
            return !!this.getToken();
        },
        
        // Add auth header to fetch options
        addAuthHeader: function(options = {}) {
            const token = this.getToken();
            if (!token) {
                return options;
            }
            
            if (!options.headers) {
                options.headers = {};
            }
            
            options.headers['Authorization'] = `Bearer ${token}`;
            return options;
        },
        
        // Authenticated fetch wrapper
        fetchAuth: async function(url, options = {}) {
            const authOptions = this.addAuthHeader(options);
            const response = await fetch(url, authOptions);
            
            // If unauthorized, redirect to login
            if (response.status === 401) {
                // Remove token as it's probably invalid
                this.removeToken();
                
                // Store the current URL to redirect back after login
                const currentPath = window.location.pathname + window.location.search;
                
                // Redirect to login
                window.location.href = `/login?next=${encodeURIComponent(currentPath)}`;
                
                // Return null to indicate auth failure
                return null;
            }
            
            return response;
        },
        
        // Login helper
        login: async function(username, password, remember = false) {
            try {
                const formData = new FormData();
                formData.append('username', username);
                formData.append('password', password);
                
                if (remember) {
                    formData.append('remember', 'true');
                }
                
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    body: formData
                });
                
                // If we got a redirect, follow it
                if (response.redirected) {
                    window.location.href = response.url;
                    return { success: true };
                }
                
                // Otherwise parse the JSON response
                const data = await response.json();
                
                if (response.ok && data.access_token) {
                    this.setToken(data.access_token);
                    return { 
                        success: true, 
                        token: data.access_token,
                        user: data.user 
                    };
                }
                
                return {
                    success: false,
                    error: data.detail || 'Login failed'
                };
            } catch (error) {
                console.error('Login error:', error);
                return {
                    success: false,
                    error: 'An unexpected error occurred'
                };
            }
        },
        
        // Register helper
        register: async function(userData) {
            try {
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    return {
                        success: true,
                        userId: data.user_id,
                        redirectUrl: data.redirect_url
                    };
                }
                
                return {
                    success: false,
                    error: data.detail || 'Registration failed'
                };
            } catch (error) {
                console.error('Registration error:', error);
                return {
                    success: false,
                    error: 'An unexpected error occurred'
                };
            }
        },
        
        // Logout helper
        logout: function() {
            this.removeToken();
            window.location.href = '/login';
        }
    };

    // Auto-initialize any login forms
    const loginForm = document.getElementById('loginForm');
    if (loginForm && loginForm.getAttribute('data-auto-init') !== 'false') {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const remember = document.getElementById('remember')?.checked || false;
            
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Signing in...';
            }
            
            const result = await window.authUtils.login(username, password, remember);
            
            if (result.success) {
                const urlParams = new URLSearchParams(window.location.search);
                const nextUrl = urlParams.get('next') || '/dashboard';
                window.location.href = nextUrl;
            } else {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger alert-dismissible fade show';
                alertDiv.role = 'alert';
                alertDiv.innerHTML = result.error;
                
                const closeButton = document.createElement('button');
                closeButton.type = 'button';
                closeButton.className = 'btn-close';
                closeButton.setAttribute('data-bs-dismiss', 'alert');
                closeButton.setAttribute('aria-label', 'Close');
                
                alertDiv.appendChild(closeButton);
                
                // Find where to insert the alert
                const firstElement = loginForm.firstElementChild;
                loginForm.insertBefore(alertDiv, firstElement);
                
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.innerHTML = 'Sign In';
                }
            }
        });
    }
});