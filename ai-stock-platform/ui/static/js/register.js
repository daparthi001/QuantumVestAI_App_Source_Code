/**
 * Registration form handler for QuantumVestAI UI
 * Created: 2025-06-17 01:50:11
 * Updated: 2025-06-20 04:54:15
 * Author: daparthi001yes
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
                errorContainer.innerText = '';
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
                    errorContainer.innerText = validationErrors.join('\n');
                    errorContainer.style.display = 'block';
                }
                return;
            }
            
            // Create registration data
            const registrationData = {
                username: username,
                email: email,
                password: password
            };
            
            // Show loading indicator
            const submitButton = document.querySelector('button[type="submit"]');
            const originalText = submitButton.innerText;
            submitButton.disabled = true;
            submitButton.innerText = 'Creating Account...';
            
            // Send registration request
            fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(registrationData)
            })
            .then(response => {
                if (response.ok) {
                    // Registration successful, redirect to login page
                    window.location.href = '/login?msg=Registration+successful!+Please+log+in.';
                    return;
                }
                
                // Parse response to get error details
                return response.json().then(errorData => {
                    throw errorData;
                });
            })
            .then(data => {
                // This block will only execute for successful responses
                window.location.href = '/login?msg=Registration+successful!+Please+log+in.';
            })
            .catch(error => {
                // Reset submit button
                submitButton.disabled = false;
                submitButton.innerText = originalText;
                
                // Process and display error messages
                let errorMessage = '';
                
                if (error.detail) {
                    // Handle FastAPI validation errors
                    if (Array.isArray(error.detail)) {
                        // Handle structured validation errors
                        errorMessage = error.detail.map(item => {
                            // Extract field name from path (usually the last element)
                            const field = item.loc.slice(-1)[0];
                            return `${field}: ${item.msg}`;
                        }).join('\n');
                    } else if (typeof error.detail === 'string') {
                        // Handle string error message
                        errorMessage = error.detail;
                    } else {
                        // Convert object to string if it's an object
                        errorMessage = JSON.stringify(error.detail);
                    }
                } else if (typeof error === 'string') {
                    // Direct string error
                    errorMessage = error;
                } else {
                    // Generic error message as fallback
                    errorMessage = 'An error occurred during registration. Please try again later.';
                    console.error('Registration error:', error);
                }
                
                // Display error message
                if (errorContainer) {
                    errorContainer.innerText = errorMessage;
                    errorContainer.style.display = 'block';
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