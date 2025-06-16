/**
 * Authentication utilities for QuantumVestAI UI
 * Created: 2025-06-16
 * Author: daparthi001ok
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
                
                // If this isn't already the login page, redirect
                if (!window.location.pathname.includes('/login')) {
                    window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                }
            }
            
            return response;
        }
    };
});