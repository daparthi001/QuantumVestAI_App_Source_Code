/**
 * Registration form handler for QuantumVestAI UI
 * Created: 2025-06-17 01:50:11
 * Updated: 2025-06-20 04:32:00
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