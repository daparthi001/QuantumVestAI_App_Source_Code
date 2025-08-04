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
                            
                            // Store token in localStorage for cross-tab sync
                            if (token) {
                                localStorage.setItem('qvai_token', token);
                                
                                // Dispatch event for cross-tab sync
                                const authEvent = new CustomEvent('qvai_auth_event', {
                                    detail: { action: 'login', token: token }
                                });
                                window.dispatchEvent(authEvent);
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
    // Get stored authentication token
    getToken: function() {
        // First check for qvai_token (new standard)
        const token = localStorage.getItem('qvai_token') || 
                     // Fallback to legacy tokens
                     localStorage.getItem('access_token') || 
                     sessionStorage.getItem('access_token') ||
                     this.getTokenFromCookie();
        return token;
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