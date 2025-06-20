/**
 * Registration form handling for QuantumVestAI
 * Updated: 2025-06-20 06:04:23
 * Author: daparthi001auth_controller.py
 */

document.addEventListener('DOMContentLoaded', () => {
    // Get the registration form
    const registrationForm = document.getElementById('registration-form');
    
    if (registrationForm) {
        // Get the error container
        const errorContainer = document.getElementById('error-container');
        
        // Set up form submission handler
        registrationForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(registrationForm);
            
            try {
                // Submit the form using fetch
                const response = await fetch('/auth/register', {
                    method: 'POST',
                    body: formData
                });
                
                // Handle redirect (successful registration)
                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }
                
                // Handle error response
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    // JSON response - parse and display error
                    const data = await response.json();
                    displayError(data.detail || data.msg || 'Registration failed');
                } else {
                    // HTML response - extract error message from response
                    const html = await response.text();
                    
                    // Look for error message in the HTML
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    // Try to find error message in the HTML
                    const errorMsg = tempDiv.querySelector('#error-container')?.innerText 
                                    || tempDiv.querySelector('.alert-danger')?.innerText 
                                    || 'Registration failed';
                    
                    displayError(errorMsg);
                }
            } catch (error) {
                console.error('Error during registration:', error);
                displayError('An unexpected error occurred. Please try again later.');
            }
            
            function displayError(message) {
                if (!errorContainer) return;
                
                // Clear previous errors
                errorContainer.innerHTML = '';
                
                // Handle object error messages
                if (typeof message === 'object') {
                    // FIX: Handle object error messages properly
                    if (Array.isArray(message)) {
                        // Array of error messages
                        const errorList = message.map(err => {
                            if (typeof err === 'string') return err;
                            if (typeof err === 'object') {
                                return err.msg || err.message || JSON.stringify(err);
                            }
                            return String(err);
                        }).join('<br>');
                        
                        errorContainer.innerHTML = errorList;
                    } else {
                        // Single object error
                        const errorMessages = [];
                        
                        // Extract messages from object
                        for (const key in message) {
                            if (message.hasOwnProperty(key)) {
                                const value = message[key];
                                if (typeof value === 'string') {
                                    errorMessages.push(`${key}: ${value}`);
                                } else {
                                    errorMessages.push(`${key}: ${JSON.stringify(value)}`);
                                }
                            }
                        }
                        
                        if (errorMessages.length > 0) {
                            errorContainer.innerHTML = errorMessages.join('<br>');
                        } else {
                            errorContainer.innerText = 'Registration failed with validation errors';
                        }
                    }
                } else {
                    // String error message
                    errorContainer.innerText = message;
                }
                
                // Show the error container
                errorContainer.style.display = 'block';
                
                // Scroll to error container
                errorContainer.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});