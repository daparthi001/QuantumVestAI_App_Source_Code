/**
 * Registration form handler for QuantumVestAI
 * Created: 2025-06-17 01:50:11
 * Updated: 2025-06-20 14:27:52
 * Author: daparthi001
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get the registration form
    const registrationForm = document.getElementById('registration-form');
    
    // Get the error container
    const errorContainer = document.getElementById('error-container');
    
    if (registrationForm) {
        // Password strength meter
        const passwordInput = document.getElementById('password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        const passwordStrengthMeter = document.getElementById('password-strength-meter');
        const passwordStrengthText = document.getElementById('password-strength-text');
        
        // Update password strength when user types
        if (passwordInput && passwordStrengthMeter && passwordStrengthText) {
            passwordInput.addEventListener('input', function() {
                const strength = calculatePasswordStrength(this.value);
                updatePasswordStrengthUI(strength, passwordStrengthMeter, passwordStrengthText);
            });
        }
        
        // Event listener for form submission
        registrationForm.addEventListener('submit', function(event) {
            // Prevent default form submission
            event.preventDefault();
            
            // Clear any previous error messages
            if (errorContainer) {
                errorContainer.style.display = 'none';
                errorContainer.innerHTML = '';
            }
            
            // Get form values
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            const agreeTerms = document.getElementById('terms').checked;
            
            // Validate form inputs
            const validationErrors = validateRegistrationForm(username, email, password, confirmPassword, agreeTerms);
            
            if (validationErrors.length > 0) {
                // Show validation errors
                if (errorContainer) {
                    // Create error message HTML - FIX: Join array items with <br> for proper display
                    const errorHTML = validationErrors.map(error => `<div>${error}</div>`).join('');
                    errorContainer.innerHTML = errorHTML;
                    errorContainer.style.display = 'block';
                }
                return;
            }
            
            // Show loading indicator
            const submitButton = document.querySelector('button[type="submit"]');
            const originalText = submitButton.innerText;
            submitButton.disabled = true;
            submitButton.innerText = 'Creating Account...';
            
            // FIX: Use FormData instead of JSON to match server expectations
            const formData = new FormData();
            formData.append('username', username);
            formData.append('email', email);
            formData.append('password', password);
            formData.append('confirm_password', confirmPassword);
            
            // Send registration request
            fetch('/auth/register', {
                method: 'POST',
                // FIX: Do not set Content-Type header when using FormData
                // The browser will automatically set the correct multipart/form-data content type
                body: formData
            })
            .then(response => {
                // Check if the response is a redirect
                if (response.redirected) {
                    // Follow the redirect
                    window.location.href = response.url;
                    return null;
                }
                
                // If response is JSON
                if (response.headers.get('content-type')?.includes('application/json')) {
                    return response.json().then(data => {
                        if (!response.ok) {
                            throw data;
                        }
                        return data;
                    });
                }
                
                // If response is HTML
                return response.text().then(html => {
                    if (!response.ok) {
                        // Try to extract error message from HTML
                        const tempDiv = document.createElement('div');
                        tempDiv.innerHTML = html;
                        const msgElement = tempDiv.querySelector('[id*="msg"], .alert, [class*="error"]');
                        throw new Error(msgElement ? msgElement.textContent.trim() : 'Registration failed');
                    }
                    return html;
                });
            })
            .then(data => {
                // This block will only execute for successful responses that aren't redirects
                
                // Check if we received a token in the response
                if (data && data.token) {
                    // Store token for cross-tab authentication
                    localStorage.setItem('qvai_token', data.token);
                    
                    // Set cookies for server-side auth
                    document.cookie = `qvai_token=${data.token}; path=/; samesite=lax`;
                    document.cookie = `access_token=Bearer ${data.token}; path=/; samesite=lax`;
                    
                    // Dispatch auth event for cross-tab sync
                    if (typeof window !== 'undefined' && window.dispatchEvent) {
                        const authEvent = new CustomEvent('qvai_auth_event', {
                            detail: { action: 'login', token: data.token }
                        });
                        window.dispatchEvent(authEvent);
                    }
                    
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                } else {
                    // No token, redirect to login
                    window.location.href = '/login?msg=Registration+successful!+Please+log+in.';
                }
            })
            .catch(error => {
                // Reset submit button
                submitButton.disabled = false;
                submitButton.innerText = originalText;
                
                // Process and display error messages properly
                let errorMessages = [];
                
                // Handle different error formats
                if (error) {
                    if (typeof error === 'string') {
                        // Direct string error
                        errorMessages.push(error);
                    } else if (error.detail) {
                        // Handle FastAPI validation errors
                        if (Array.isArray(error.detail)) {
                            // Handle structured validation errors
                            error.detail.forEach(err => {
                                // Extract field name from path (usually the last element)
                                const field = err.loc ? (err.loc.slice(-1)[0] || 'Error') : 'Error';
                                errorMessages.push(`${field}: ${err.msg || 'Invalid value'}`);
                            });
                        } else if (typeof error.detail === 'string') {
                            // Handle string error message
                            errorMessages.push(error.detail);
                        } else {
                            // Convert object to string if it's an object
                            errorMessages.push(JSON.stringify(error.detail));
                        }
                    } else if (error.message) {
                        // Object with message property
                        errorMessages.push(error.message);
                    } else {
                        // Try to stringify the whole error object
                        try {
                            errorMessages.push(JSON.stringify(error));
                        } catch (e) {
                            errorMessages.push("An unknown error occurred");
                        }
                    }
                } else {
                    // Generic error message as fallback
                    errorMessages.push('An error occurred during registration. Please try again later.');
                }
                
                // Display error message
                if (errorContainer) {
                    // Create proper HTML for error messages
                    const errorHTML = errorMessages.map(msg => `<div>${msg}</div>`).join('');
                    errorContainer.innerHTML = errorHTML;
                    errorContainer.style.display = 'block';
                    
                    // Scroll to error container
                    errorContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        });
    }
});

/**
 * Calculates password strength on a scale of 0-4
 * 0: Very weak, 1: Weak, 2: Moderate, 3: Strong, 4: Very strong
 */
function calculatePasswordStrength(password) {
    if (!password) return 0;
    
    let strength = 0;
    
    // Award points based on password characteristics
    if (password.length >= 8) strength += 1;
    if (password.length >= 12) strength += 1;
    if (/[A-Z]/.test(password)) strength += 1;
    if (/[a-z]/.test(password)) strength += 1;
    if (/[0-9]/.test(password)) strength += 1;
    if (/[^A-Za-z0-9]/.test(password)) strength += 1;
    
    // Normalize to 0-4 scale
    return Math.min(4, Math.floor(strength * 4 / 6));
}

/**
 * Updates the password strength UI elements
 */
function updatePasswordStrengthUI(strength, meterElement, textElement) {
    // Update meter element
    if (meterElement) {
        meterElement.value = strength;
        
        // Update color based on strength
        switch (strength) {
            case 0:
                meterElement.className = 'strength-very-weak';
                break;
            case 1:
                meterElement.className = 'strength-weak';
                break;
            case 2:
                meterElement.className = 'strength-moderate';
                break;
            case 3:
                meterElement.className = 'strength-strong';
                break;
            case 4:
                meterElement.className = 'strength-very-strong';
                break;
        }
    }
    
    // Update text element
    if (textElement) {
        switch (strength) {
            case 0:
                textElement.innerText = 'Password is very weak';
                break;
            case 1:
                textElement.innerText = 'Password is weak';
                break;
            case 2:
                textElement.innerText = 'Password is moderate';
                break;
            case 3:
                textElement.innerText = 'Password is strong';
                break;
            case 4:
                textElement.innerText = 'Password is very strong';
                break;
        }
    }
}

/**
 * Validates the registration form inputs
 * Returns an array of validation error messages
 */
function validateRegistrationForm(username, email, password, confirmPassword, agreeTerms) {
    const errors = [];
    
    // Username validation
    if (!username) {
        errors.push('Username is required');
    } else if (username.length < 3 || username.length > 20) {
        errors.push('Username must be between 3-20 characters');
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        errors.push('Username must contain only letters, numbers, and underscores');
    }
    
    // Email validation
    if (!email) {
        errors.push('Email address is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        errors.push('Please enter a valid email address');
    }
    
    // Password validation
    if (!password) {
        errors.push('Password is required');
    } else if (password.length < 8) {
        errors.push('Password must be at least 8 characters long');
    } else if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
        errors.push('Password must include uppercase, lowercase, and numbers');
    }
    
    // Confirm password validation
    if (!confirmPassword) {
        errors.push('Please confirm your password');
    } else if (password !== confirmPassword) {
        errors.push('Passwords do not match');
    }
    
    // Terms agreement
    if (!agreeTerms) {
        errors.push('You must agree to the Terms of Service and Privacy Policy');
    }
    
    return errors;
}