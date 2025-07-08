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
                const response = await fetch('/register', {
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
                
                // Use the global error handler if available
                if (window.UIErrorHandler) {
                    window.UIErrorHandler.showError(message, { 
                        position: 'inline', 
                        container: errorContainer,
                        replace: true
                    });
                    return;
                }
                
                // Fallback: Simple error display
                errorContainer.innerHTML = '';
                errorContainer.style.display = 'block';
                
                // Handle different message types
                let errorText = '';
                if (typeof message === 'string') {
                    errorText = message;
                } else if (Array.isArray(message)) {
                    errorText = message.join('<br>');
                } else if (typeof message === 'object' && message !== null) {
                    // Extract common error properties
                    errorText = message.detail || message.msg || message.message || 'Registration failed';
                } else {
                    errorText = 'Registration failed';
                }
                
                errorContainer.innerHTML = errorText;
                errorContainer.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
});