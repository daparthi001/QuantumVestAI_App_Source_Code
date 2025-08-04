/**
 * Authentication utilities for QuantumVestAI
 * Updated: 2025-01-09
 * Author: daparthi001
 */

// Set up automatic token validation and refresh
function setupTokenRefresh() {
    // Check token validity every 5 minutes
    setInterval(() => {
        if (window.authUtils && window.authUtils.isAuthenticated()) {
            // Verify token validity 
            if (!window.authUtils.validateToken()) {
                console.warn('Auth token validation failed, attempting to refresh session');
                // Here you could implement a silent refresh logic
                // For now, we'll just notify about potential issues
                
                // If on dashboard or protected page, might want to redirect to login
                if (window.location.pathname.includes('/dashboard') || 
                    window.location.pathname.includes('/portfolio')) {
                    // Instead of immediate redirect, show a warning first
                    if (!window._tokenWarningShown) {
                        window._tokenWarningShown = true;
                        console.warn('Session may be expired. Please refresh the page if you experience any issues.');
                    }
                }
            }
        }
    }, 5 * 60 * 1000); // Check every 5 minutes
}

document.addEventListener('DOMContentLoaded', function() {
    // Set up token refresh mechanism
    setupTokenRefresh();
    
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
                // Submit the form using fetch to handle the token sync
                const formDataObj = Object.fromEntries(formData.entries());
                fetch(loginForm.action, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams(formDataObj).toString(),
                    credentials: 'same-origin'
                })
                .then(response => {
                    if (response.ok) {
                        // Check if we were redirected to dashboard (successful login)
                        if (response.redirected && response.url.includes('/dashboard')) {
                            // Success! Parse cookies to extract token
                            const cookies = document.cookie.split(';');
                            let token = null;
                            
                            // First try to find qvai_token
                            for (let cookie of cookies) {
                                cookie = cookie.trim();
                                if (cookie.startsWith('qvai_token=')) {
                                    token = cookie.substring('qvai_token='.length);
                                    break;
                                }
                            }
                            
                            // If no qvai_token, try access_token
                            if (!token) {
                                for (let cookie of cookies) {
                                    cookie = cookie.trim();
                                    if (cookie.startsWith('access_token=')) {
                                        token = cookie.substring('access_token='.length).replace('Bearer ', '');
                                        break;
                                    }
                                }
                            }
                            
                            // Store token in localStorage AND sessionStorage for cross-tab sync and session persistence
                            if (token) {
                                localStorage.setItem('qvai_token', token);
                                sessionStorage.setItem('qvai_token', token);
                                
                                // Also store in a longer expiration cookie as backup
                                const expiryDate = new Date();
                                expiryDate.setDate(expiryDate.getDate() + 7); // 7 days expiry
                                document.cookie = `qvai_token=${token}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax`;
                                
                                // Dispatch event for cross-tab sync
                                const authEvent = new CustomEvent('qvai_auth_event', {
                                    detail: { action: 'login', token: token }
                                });
                                window.dispatchEvent(authEvent);
                                
                                console.log('Authentication token stored successfully');
                            }
                            
                            // Navigate to the redirected URL
                            window.location.href = response.url;
                        } else {
                            // Form submission worked but we got a different page (login with errors)
                            window.location.href = response.url;
                        }
                    } else {
                        // Handle error response
                        LoadingManager.hideButtonLoading(submitButton);
                        UIErrorHandler.showError('Login failed. Please check your credentials and try again.');
                    }
                })
                .catch(error => {
                    console.error('Login submission error:', error);
                    LoadingManager.hideButtonLoading(submitButton);
                    UIErrorHandler.showError('Login failed. Please try again.');
                });
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
    // Get stored authentication token with comprehensive fallback strategy
    getToken: function() {
        // First check for qvai_token (new standard)
        let token = localStorage.getItem('qvai_token') || 
                    sessionStorage.getItem('qvai_token') ||
                    // Fallback to legacy tokens
                    localStorage.getItem('access_token') || 
                    sessionStorage.getItem('access_token') ||
                    this.getTokenFromCookie();
                    
        // If no token found, try to get it from cookie directly
        if (!token) {
            // This is a more direct cookie parsing approach as a last resort
            const cookies = document.cookie.split(';');
            for (const cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'qvai_token') {
                    token = value;
                    break;
                } else if (name === 'access_token') {
                    token = value;
                    break;
                }
            }
        }
        
        // If token exists but has 'Bearer ' prefix, clean it up
        if (token && token.startsWith('Bearer ')) {
            token = token.replace('Bearer ', '');
            
            // Update all storage locations with clean token for consistency
            this.setToken(token, true);
        }
        
        return token;
    },
    
    // Check if user is authenticated
    isAuthenticated: function() {
        return !!this.getToken();
    },
    
    // Verify token is still valid (can be expanded with actual validation)
    validateToken: function() {
        const token = this.getToken();
        if (!token) return false;
        
        try {
            // Simple validation - check if token appears to be a JWT
            // A more robust solution would verify with the server
            const parts = token.split('.');
            return parts.length === 3;
        } catch (e) {
            console.error('Token validation error:', e);
            return false;
        }
    },
    
    // Get token from cookie
    getTokenFromCookie: function() {
        // First try qvai_token cookie
        let cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('qvai_token='));
        
        if (cookieValue) {
            return cookieValue.split('=')[1];
        }
        
        // Fallback to access_token cookie
        cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('access_token='));
        
        if (cookieValue) {
            return cookieValue.split('=')[1].replace('Bearer%20', '').replace('Bearer ', '');
        }
        return null;
    },
    
    // Store authentication token
    setToken: function(token, remember = false) {
        // Always store in localStorage for cross-tab sync
        localStorage.setItem('qvai_token', token);
        
        // For backward compatibility
        if (remember) {
            localStorage.setItem('access_token', token);
        } else {
            sessionStorage.setItem('access_token', token);
        }
        
        // Set cookies for server-side auth
        document.cookie = `qvai_token=${token}; path=/; samesite=lax`;
        document.cookie = `access_token=Bearer ${token}; path=/; samesite=lax`;
        
        // Dispatch event for cross-tab sync
        const authEvent = new CustomEvent('qvai_auth_event', {
            detail: { action: 'login', token: token }
        });
        window.dispatchEvent(authEvent);
    },
    
    // Remove authentication token
    removeToken: function() {
        // Remove all token storage
        localStorage.removeItem('qvai_token');
        localStorage.removeItem('access_token');
        sessionStorage.removeItem('access_token');
        
        // Remove cookies
        document.cookie = 'qvai_token=; Max-Age=0; path=/';
        document.cookie = 'access_token=; Max-Age=0; path=/';
        document.cookie = 'user_info=; Max-Age=0; path=/';
        
        // Dispatch event for cross-tab sync
        const authEvent = new CustomEvent('qvai_auth_event', {
            detail: { action: 'logout' }
        });
        window.dispatchEvent(authEvent);
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