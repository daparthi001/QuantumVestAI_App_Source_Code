/**
 * Enhanced UI Error Handling and Loading States
 * Created: 2025-01-09
 * Author: AI Assistant
 */

// Global error handling utilities
window.UIErrorHandler = {
    // Show error message to user
    showError: function(message, options = {}) {
        const defaultOptions = {
            title: 'Error',
            type: 'error',
            duration: 5000,
            closable: true,
            position: 'top-right'
        };
        
        const config = { ...defaultOptions, ...options };
        
        // Remove existing error notifications if replace is true
        if (config.replace) {
            this.clearErrors();
        }
        
        // Create error notification element
        const errorElement = document.createElement('div');
        errorElement.className = `alert alert-${config.type === 'error' ? 'danger' : config.type} alert-dismissible fade show error-notification`;
        errorElement.setAttribute('role', 'alert');
        errorElement.style.position = 'fixed';
        errorElement.style.zIndex = '9999';
        errorElement.style.minWidth = '300px';
        errorElement.style.maxWidth = '500px';
        
        // Position the notification
        switch (config.position) {
            case 'top-right':
                errorElement.style.top = '20px';
                errorElement.style.right = '20px';
                break;
            case 'top-left':
                errorElement.style.top = '20px';
                errorElement.style.left = '20px';
                break;
            case 'bottom-right':
                errorElement.style.bottom = '20px';
                errorElement.style.right = '20px';
                break;
            case 'bottom-left':
                errorElement.style.bottom = '20px';
                errorElement.style.left = '20px';
                break;
            default:
                errorElement.style.top = '20px';
                errorElement.style.right = '20px';
        }
        
        // Create error content
        let content = '';
        if (config.title && config.title !== 'Error') {
            content += `<strong>${config.title}:</strong> `;
        }
        content += message;
        
        errorElement.innerHTML = `
            ${content}
            ${config.closable ? '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>' : ''}
        `;
        
        // Add to DOM
        document.body.appendChild(errorElement);
        
        // Auto-remove after duration
        if (config.duration > 0) {
            setTimeout(() => {
                if (errorElement.parentNode) {
                    errorElement.remove();
                }
            }, config.duration);
        }
        
        return errorElement;
    },
    
    // Show success message
    showSuccess: function(message, options = {}) {
        return this.showError(message, { ...options, type: 'success', title: 'Success' });
    },
    
    // Show warning message
    showWarning: function(message, options = {}) {
        return this.showError(message, { ...options, type: 'warning', title: 'Warning' });
    },
    
    // Show info message
    showInfo: function(message, options = {}) {
        return this.showError(message, { ...options, type: 'info', title: 'Info' });
    },
    
    // Clear all error notifications
    clearErrors: function() {
        const notifications = document.querySelectorAll('.error-notification');
        notifications.forEach(notification => notification.remove());
    },
    
    // Show inline form error
    showFormError: function(fieldName, message) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (!field) return;
        
        // Remove existing error
        this.clearFormError(fieldName);
        
        // Add error class to field
        field.classList.add('is-invalid');
        
        // Create error message element
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.textContent = message;
        errorElement.setAttribute('data-field-error', fieldName);
        
        // Insert after field
        field.parentNode.insertBefore(errorElement, field.nextSibling);
    },
    
    // Clear specific form field error
    clearFormError: function(fieldName) {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.remove('is-invalid');
        }
        
        const errorElement = document.querySelector(`[data-field-error="${fieldName}"]`);
        if (errorElement) {
            errorElement.remove();
        }
    },
    
    // Clear all form errors
    clearFormErrors: function(form) {
        if (typeof form === 'string') {
            form = document.querySelector(form);
        }
        if (!form) return;
        
        // Remove invalid classes
        const invalidFields = form.querySelectorAll('.is-invalid');
        invalidFields.forEach(field => field.classList.remove('is-invalid'));
        
        // Remove error messages
        const errorMessages = form.querySelectorAll('.invalid-feedback');
        errorMessages.forEach(msg => msg.remove());
    },
    
    // Handle API error response
    handleAPIError: function(error, options = {}) {
        let message = 'An unexpected error occurred';
        let details = null;
        
        if (error.response) {
            // Server responded with error
            const data = error.response.data || {};
            message = data.message || data.detail || `Server error (${error.response.status})`;
            details = data.details;
            
            // Handle validation errors
            if (data.error_code === 'VALIDATION_ERROR' && details && details.validation_errors) {
                this.handleValidationErrors(details.validation_errors);
                return;
            }
        } else if (error.request) {
            // Network error
            message = 'Network error - please check your connection';
        } else if (error.message) {
            // Other error
            message = error.message;
        }
        
        this.showError(message, options);
    },
    
    // Handle validation errors from API
    handleValidationErrors: function(validationErrors) {
        if (!Array.isArray(validationErrors)) return;
        
        validationErrors.forEach(error => {
            if (error.field) {
                this.showFormError(error.field, error.message);
            }
        });
        
        // Also show general validation error
        this.showError('Please correct the highlighted fields', { type: 'warning' });
    }
};

// Loading state utilities
window.LoadingManager = {
    // Show loading spinner on element
    showLoading: function(element, options = {}) {
        const defaultOptions = {
            overlay: true,
            spinner: true,
            message: 'Loading...',
            size: 'medium' // small, medium, large
        };
        
        const config = { ...defaultOptions, ...options };
        
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (!element) return;
        
        // Store original position
        const originalPosition = element.style.position;
        if (!originalPosition || originalPosition === 'static') {
            element.style.position = 'relative';
            element.setAttribute('data-original-position', 'static');
        }
        
        // Create loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            backdrop-filter: blur(2px);
        `;
        
        // Create spinner content
        let spinnerSize = '3rem';
        switch (config.size) {
            case 'small': spinnerSize = '1.5rem'; break;
            case 'large': spinnerSize = '4rem'; break;
            default: spinnerSize = '3rem';
        }
        
        const spinnerContent = document.createElement('div');
        spinnerContent.className = 'loading-content text-center';
        spinnerContent.innerHTML = `
            ${config.spinner ? `
                <div class="spinner-border text-primary" role="status" style="width: ${spinnerSize}; height: ${spinnerSize};">
                    <span class="visually-hidden">Loading...</span>
                </div>
            ` : ''}
            ${config.message ? `<div class="loading-message mt-2">${config.message}</div>` : ''}
        `;
        
        loadingOverlay.appendChild(spinnerContent);
        element.appendChild(loadingOverlay);
        
        // Add loading class
        element.classList.add('loading');
        
        return loadingOverlay;
    },
    
    // Hide loading spinner
    hideLoading: function(element) {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        if (!element) return;
        
        // Remove loading overlay
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) {
            overlay.remove();
        }
        
        // Remove loading class
        element.classList.remove('loading');
        
        // Restore original position
        const originalPosition = element.getAttribute('data-original-position');
        if (originalPosition) {
            element.style.position = originalPosition;
            element.removeAttribute('data-original-position');
        }
    },
    
    // Show loading on button and disable it
    showButtonLoading: function(button, loadingText = 'Loading...') {
        if (typeof button === 'string') {
            button = document.querySelector(button);
        }
        if (!button) return;
        
        // Store original text and state
        button.setAttribute('data-original-text', button.innerHTML);
        button.setAttribute('data-original-disabled', button.disabled);
        
        // Set loading state
        button.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${loadingText}
        `;
        button.disabled = true;
        button.classList.add('loading');
    },
    
    // Hide loading on button and restore state
    hideButtonLoading: function(button) {
        if (typeof button === 'string') {
            button = document.querySelector(button);
        }
        if (!button) return;
        
        // Restore original text and state
        const originalText = button.getAttribute('data-original-text');
        const originalDisabled = button.getAttribute('data-original-disabled') === 'true';
        
        if (originalText) {
            button.innerHTML = originalText;
            button.removeAttribute('data-original-text');
        }
        
        button.disabled = originalDisabled;
        button.removeAttribute('data-original-disabled');
        button.classList.remove('loading');
    },
    
    // Show global loading overlay
    showGlobalLoading: function(message = 'Loading...') {
        // Remove existing global loading
        this.hideGlobalLoading();
        
        const globalOverlay = document.createElement('div');
        globalOverlay.id = 'global-loading-overlay';
        globalOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(3px);
        `;
        
        globalOverlay.innerHTML = `
            <div class="text-center text-white">
                <div class="spinner-border text-light mb-3" role="status" style="width: 4rem; height: 4rem;">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <div class="h5">${message}</div>
            </div>
        `;
        
        document.body.appendChild(globalOverlay);
        return globalOverlay;
    },
    
    // Hide global loading overlay
    hideGlobalLoading: function() {
        const overlay = document.getElementById('global-loading-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
};

// Enhanced API client with error handling and loading states
window.APIClient = {
    baseURL: window.API_BASE_URL || '/api/v1',
    
    // Make API request with error handling
    request: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        // Get auth token if available
        const token = window.authUtils && window.authUtils.getToken();
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        const config = { ...defaultOptions, ...options };
        
        // If body is an object, stringify it
        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }
        
        try {
            const response = await fetch(`${this.baseURL}${url}`, config);
            
            // Check if response is ok
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const error = new Error(errorData.message || `HTTP ${response.status}`);
                error.response = { 
                    status: response.status, 
                    data: errorData 
                };
                throw error;
            }
            
            return await response.json();
        } catch (error) {
            // Handle network errors
            if (!error.response) {
                error.request = true;
            }
            throw error;
        }
    },
    
    // GET request
    get: function(url, options = {}) {
        return this.request(url, { ...options, method: 'GET' });
    },
    
    // POST request
    post: function(url, data, options = {}) {
        return this.request(url, { 
            ...options, 
            method: 'POST', 
            body: data 
        });
    },
    
    // PUT request
    put: function(url, data, options = {}) {
        return this.request(url, { 
            ...options, 
            method: 'PUT', 
            body: data 
        });
    },
    
    // DELETE request
    delete: function(url, options = {}) {
        return this.request(url, { ...options, method: 'DELETE' });
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Handle global AJAX errors
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && event.reason.response) {
            console.error('Unhandled API error:', event.reason);
            // Don't show error for handled cases
            if (!event.reason.handled) {
                UIErrorHandler.handleAPIError(event.reason);
            }
        }
    });
    
    // Add CSS for loading states
    const style = document.createElement('style');
    style.textContent = `
        .loading-overlay {
            pointer-events: none;
        }
        
        .loading {
            pointer-events: none;
        }
        
        .error-notification {
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: none;
        }
        
        .spinner-border-sm {
            width: 1rem;
            height: 1rem;
        }
        
        .loading-content {
            color: #6c757d;
        }
        
        .loading-message {
            font-size: 0.9rem;
            color: #6c757d;
        }
    `;
    document.head.appendChild(style);
});