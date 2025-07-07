/**
 * Enhanced Authentication utilities for QuantumVestAI UI
 * Created: 2025-06-16
 * Updated: 2025-06-17 17:03:55
 * Enhanced: 2025-01-09 (AI Assistant)
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

    // Enhanced form validation
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        // Add client-side validation
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
                // Attempt API login first
                const response = await APIClient.post('/auth/login', {
                    username: username.trim(),
                    password: password,
                    remember: remember
                });
                
                if (response.status === 'success') {
                    // Store token if provided
                    if (response.data && response.data.access_token) {
                        authUtils.setToken(response.data.access_token);
                    }
                    
                    UIErrorHandler.showSuccess('Login successful! Redirecting...', { duration: 2000 });
                    
                    // Redirect after short delay
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    throw new Error(response.message || 'Login failed');
                }
            } catch (error) {
                console.error('API login failed:', error);
                
                // Mark error as handled
                error.handled = true;
                
                // Try fallback form submission
                try {
                    UIErrorHandler.showWarning('Attempting fallback login...', { duration: 2000 });
                    
                    // Submit form normally as fallback
                    const fallbackForm = document.createElement('form');
                    fallbackForm.method = 'POST';
                    fallbackForm.action = '/login'; // Use direct login endpoint
                    
                    const usernameInput = document.createElement('input');
                    usernameInput.type = 'hidden';
                    usernameInput.name = 'username';
                    usernameInput.value = username;
                    
                    const passwordInput = document.createElement('input');
                    passwordInput.type = 'hidden';
                    passwordInput.name = 'password';
                    passwordInput.value = password;
                    
                    const rememberInput = document.createElement('input');
                    rememberInput.type = 'hidden';
                    rememberInput.name = 'remember';
                    rememberInput.value = remember;
                    
                    fallbackForm.appendChild(usernameInput);
                    fallbackForm.appendChild(passwordInput);
                    fallbackForm.appendChild(rememberInput);
                    
                    document.body.appendChild(fallbackForm);
                    fallbackForm.submit();
                    
                } catch (fallbackError) {
                    UIErrorHandler.handleAPIError(error);
                }
            } finally {
                LoadingManager.hideButtonLoading(submitButton);
            }
        });
        
        // Real-time validation
        const usernameInput = loginForm.querySelector('[name="username"]');
        const passwordInput = loginForm.querySelector('[name="password"]');
        
        if (usernameInput) {
            usernameInput.addEventListener('blur', function() {
                UIErrorHandler.clearFormError('username');
                if (this.value.trim().length > 0 && this.value.trim().length < 3) {
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
            const token = this.getToken();
            if (!token) return false;
            
            // Check if token is expired (basic check)
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                return payload.exp > Date.now() / 1000;
            } catch (e) {
                return true; // If we can't parse, assume it's valid
            }
        },
        
        // Enhanced logout function
        logout: async function() {
            try {
                // Try to call API logout endpoint
                await APIClient.post('/auth/logout', {});
            } catch (error) {
                console.warn('API logout failed:', error);
            }
            
            // Clear local storage
            this.removeToken();
            
            // Clear any session storage
            sessionStorage.clear();
            
            // Show success message
            UIErrorHandler.showSuccess('Logged out successfully', { duration: 2000 });
            
            // Redirect to login
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
        },
        
        // Check authentication status with server
        checkAuthStatus: async function() {
            try {
                const response = await APIClient.get('/auth/me');
                return response.status === 'success';
            } catch (error) {
                return false;
            }
        },
        
        // Make authenticated request
        makeAuthenticatedRequest: async function(url, options = {}) {
            const token = this.getToken();
            if (!token) {
                throw new Error('No authentication token available');
            }
            
            const headers = {
                'Authorization': `Bearer ${token}`,
                ...options.headers
            };
            
            return APIClient.request(url, { ...options, headers });
        }
    };
    
    // Auto-logout on token expiration
    setInterval(() => {
        if (!authUtils.isAuthenticated() && authUtils.getToken()) {
            UIErrorHandler.showWarning('Your session has expired. Please log in again.');
            authUtils.logout();
        }
    }, 60000); // Check every minute
    
    // Handle logout buttons
    const logoutButtons = document.querySelectorAll('[data-action="logout"]');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            authUtils.logout();
        });
    });
});
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