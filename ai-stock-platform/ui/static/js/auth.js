/**
 * Authentication utilities for QuantumVestAI UI
 * Created: 2025-06-16
 * Updated: 2025-06-17 17:03:55
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
                
                if (data.access_token) {
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
                
                return {
                    success: data.success === true,
                    userId: data.user_id,
                    redirectUrl: data.redirect_url,
                    error: data.detail || null
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

    // Auto-initialize any auth forms with data-auto-init attribute
    const initializeForms = () => {
        // Login form initialization
        const loginForm = document.getElementById('loginForm');
        if (loginForm && loginForm.getAttribute('data-auto-init') !== 'false') {
            // Login form is being handled directly in login.html
            console.log('Login form found - initialization handled in page script');
        }
        
        // Register form initialization
        const registerForm = document.getElementById('registerForm');
        if (registerForm && registerForm.getAttribute('data-auto-init') !== 'false') {
            // Register form is being handled directly in register.html
            console.log('Registration form found - initialization handled in page script');
        }
        
        // Auto logout links
        const logoutLinks = document.querySelectorAll('[data-auth="logout"]');
        logoutLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                window.authUtils.logout();
            });
        });
    };
    
    // Initialize forms
    initializeForms();
    
    // Check protected pages
    const bodyElement = document.body;
    if (bodyElement && bodyElement.getAttribute('data-auth-required') === 'true') {
        window.authUtils.requireAuth();
    }
});